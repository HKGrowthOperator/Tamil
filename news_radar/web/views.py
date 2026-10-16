"""Routen der Freigabe-App."""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone

from flask import (Blueprint, Response, abort, current_app, flash, g, jsonify, redirect, render_template, request,
                   send_from_directory, session, url_for)

from .. import images
from ..render import render_content, sanitize_html
from ..store import OPEN_STATES, PUBLISHABLE, STATUSES, TRANSITIONS, ConflictError
from ..wordpress import slugify
from . import check_login, get_store

log = logging.getLogger(__name__)
ui = Blueprint("ui", __name__)

TABS = [("neu", "Neu"), ("bearbeitet", "Bearbeitet"), ("zurueckgestellt", "Zurückgestellt"), ("freigegeben", "Freigegeben"),
        ("veroeffentlicht", "Veröffentlicht"), ("abgelehnt", "Abgelehnt"), ("fehler", "Fehler")]
STATUS_LABELS = {"neu": "Neu", "bearbeitet": "Bearbeitet", "zurueckgestellt": "Zurückgestellt", "freigegeben": "Freigegeben",
                 "wird_veroeffentlicht": "Wird veröffentlicht …", "veroeffentlicht": "Veröffentlicht",
                 "in_wordpress": "WordPress-Entwurf", "abgelehnt": "Abgelehnt", "fehler": "Fehler"}
EDITABLE = ("titel", "teaser", "kategorie", "inhalt_html", "seo_titel", "meta_beschreibung", "bild_alt", "event_datum",
            "event_ort", "ticket_url")
_FILENAME_RE = re.compile(r"^[A-Za-z0-9._-]+\.jpg$")


def _settings():
    return current_app.extensions["settings"]


def _writer():
    writer = current_app.extensions.get("writer")
    if writer is None:
        from ..writer import Writer

        writer = current_app.extensions["writer"] = Writer(_settings())
    return writer


def _wordpress():
    wp = current_app.extensions.get("wordpress")
    if wp is None and _settings().wordpress_enabled:
        from ..publisher import make_wordpress

        wp = current_app.extensions["wordpress"] = make_wordpress(_settings())
    return wp


def _draft_or_404(draft_id: int) -> dict:
    row = get_store().get_draft(draft_id)
    if row is None:
        abort(404)
    return row


def _user() -> str:
    return session.get("user", "")


# ---- Login -------------------------------------------------------------------------

@ui.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if check_login(_settings(), request.form.get("user", ""), request.form.get("password", "")):
            session.permanent = True
            session["user"] = request.form["user"]
            target = request.args.get("next") or "/"
            return redirect(target if target.startswith("/") else "/")
        flash("Benutzername oder Passwort falsch.", "fehler")
    return render_template("login.html")


@ui.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("ui.login"))


# ---- Feed ----------------------------------------------------------------------------

@ui.get("/")
def feed():
    status = request.args.get("status", "neu")
    if status not in STATUSES:
        abort(404)
    page = max(1, int(request.args.get("seite", 1)))
    per_page = 30
    store = get_store()
    counts = store.counts_by_status()
    counts["veroeffentlicht"] += counts.get("in_wordpress", 0)
    statuses = ["veroeffentlicht", "in_wordpress", "wird_veroeffentlicht"] if status == "veroeffentlicht" else [status]
    drafts = []
    for s in statuses:
        drafts += store.list_drafts(s, limit=per_page, offset=(page - 1) * per_page)
    drafts.sort(key=lambda d: d["updated_at"], reverse=True) if status != "neu" else None
    return render_template("feed.html", drafts=drafts, status=status, tabs=TABS, counts=counts, page=page,
                           has_more=len(drafts) >= per_page, labels=STATUS_LABELS)


@ui.post("/entwurf/<int:draft_id>/status")
def set_status(draft_id: int):
    aktion = request.form.get("aktion", "")
    if aktion not in TRANSITIONS:
        abort(400)
    store = get_store()
    try:
        neu = store.set_status(draft_id, aktion, von=_user())
    except ConflictError as exc:
        return render_template("fehler.html", titel="Zustand hat sich geändert", text=str(exc), draft_id=draft_id), 409
    store.event("aktion", id=draft_id, aktion=aktion, status=neu, von=_user())
    flash(f"{STATUS_LABELS.get(neu, neu)}.", "ok")
    target = request.form.get("next") or request.args.get("next") or url_for("ui.feed")
    return redirect(target if target.startswith("/") else url_for("ui.feed"))


# ---- Bearbeiten -------------------------------------------------------------------------

@ui.route("/entwurf/<int:draft_id>", methods=["GET", "POST"])
def entwurf(draft_id: int):
    store = get_store()
    row = _draft_or_404(draft_id)
    if request.method == "POST":
        fields = {k: request.form.get(k, "").strip() for k in EDITABLE}
        fields["inhalt_html"] = sanitize_html(fields["inhalt_html"])
        fields["schlagworte"] = [t.strip() for t in request.form.get("schlagworte", "").split(",") if t.strip()]
        if fields["kategorie"] not in _settings().category_slugs():
            fields["kategorie"] = row["kategorie"]
        store.update_draft(draft_id, von=_user(), **fields)
        if row["status"] in ("neu", "zurueckgestellt"):
            try:
                store.set_status(draft_id, "bearbeiten", von=_user())
            except ConflictError:
                pass
        store.event("bearbeitet", id=draft_id, von=_user())
        flash("Gespeichert.", "ok")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    return render_template("entwurf.html", d=row, labels=STATUS_LABELS, categories=_settings().categories,
                           can_publish=row["status"] in PUBLISHABLE, open_states=OPEN_STATES,
                           preview=render_content(row))


@ui.post("/entwurf/<int:draft_id>/neu-schreiben")
def neu_schreiben(draft_id: int):
    store = get_store()
    row = _draft_or_404(draft_id)
    anweisung = request.form.get("anweisung", "").strip() or "Schreibe den Text flüssiger und kürzer."
    try:
        draft = _writer().rewrite(row, anweisung)
    except Exception as exc:  # noqa: BLE001 - dem Nutzer den Fehler zeigen statt 500
        log.exception("Umschreiben fehlgeschlagen")
        flash(f"Umschreiben fehlgeschlagen: {str(exc)[:200]}", "fehler")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    if draft is None:
        flash("Das Modell hat den Text nicht umgeschrieben (abgelehnt).", "fehler")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    fields = draft.model_dump()
    fields.pop("typ", None)
    store.update_draft(draft_id, von=_user(), rewrite_count=row["rewrite_count"] + 1, **fields)
    if row["status"] in ("neu", "zurueckgestellt"):
        try:
            store.set_status(draft_id, "bearbeiten", von=_user())
        except ConflictError:
            pass
    store.event("neu_geschrieben", id=draft_id, anweisung=anweisung, von=_user())
    flash("Neu geschrieben – bitte prüfen.", "ok")
    return redirect(url_for("ui.entwurf", draft_id=draft_id))


@ui.post("/entwurf/<int:draft_id>/zuruecksetzen")
def zuruecksetzen(draft_id: int):
    store = get_store()
    row = _draft_or_404(draft_id)
    try:
        original = json.loads(row["original_json"] or "{}")
    except ValueError:
        original = {}
    if not original:
        flash("Kein Original gespeichert.", "fehler")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    original.pop("typ", None)
    store.update_draft(draft_id, von=_user(), **original)
    store.event("zurueckgesetzt", id=draft_id, von=_user())
    flash("Auf das Original zurückgesetzt.", "ok")
    return redirect(url_for("ui.entwurf", draft_id=draft_id))


@ui.post("/entwurf/<int:draft_id>/bild")
def bild(draft_id: int):
    store = get_store()
    row = _draft_or_404(draft_id)
    settings = _settings()
    aktion = request.form.get("aktion", "karte")
    stem_base = (row.get("bild_datei") or f"{row['uid'][:12]}-{slugify(row['titel'], 50)}.jpg").removesuffix(".jpg")
    stem_base = re.sub(r"-\d+$", "", stem_base)
    version = sum(1 for e in store.iter_log(event="bild") if e.get("id") == draft_id) + 2
    stem = f"{stem_base}-{version}"
    label = next((c.label for c in settings.categories if c.slug == row["kategorie"]), row["kategorie"])
    try:
        if aktion == "upload":
            file = request.files.get("datei")
            if not file or not file.filename:
                flash("Keine Datei ausgewählt.", "fehler")
                return redirect(url_for("ui.entwurf", draft_id=draft_id))
            image = images.from_upload(file.read(), stem, request.form.get("credit", "").strip() or "Foto: Tamil.de")
        elif aktion == "stock":
            query = request.form.get("suchbegriff", "").strip() or row.get("bild_suchbegriff") or row["titel"]
            image = images.featured_image(settings, query, row["titel"], label, stem)
            if image.origin == "karte":
                flash("Kein Stockfoto gefunden (oder kein Unsplash/Pexels-Schlüssel) – Bildkarte erzeugt.", "fehler")
            store.update_draft(draft_id, bild_suchbegriff=query)
        else:
            image = images.branded_card(row["titel"], label, stem)
    except Exception as exc:  # noqa: BLE001
        log.exception("Bild fehlgeschlagen")
        flash(f"Bild fehlgeschlagen: {str(exc)[:200]}", "fehler")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    name, _thumb = images.save_pair(image, settings.bilder_dir, stem)
    for old in (row.get("bild_datei"), (row.get("bild_datei") or "").replace(".jpg", "-thumb.jpg")):
        if old and old != name:
            (settings.bilder_dir / old).unlink(missing_ok=True)
    store.update_draft(draft_id, von=_user(), bild_datei=name, bild_credit=image.credit, bild_origin=image.origin)
    store.event("bild", id=draft_id, aktion=aktion, origin=image.origin, von=_user())
    flash("Bild ersetzt.", "ok")
    return redirect(url_for("ui.entwurf", draft_id=draft_id))


# ---- Veröffentlichen ------------------------------------------------------------------------

def _publish(draft_id: int, status: str):
    from ..publisher import publish_draft

    store = get_store()
    row = _draft_or_404(draft_id)
    wp = _wordpress()
    if wp is None:
        flash("WordPress ist noch nicht angebunden (WP_URL, WP_USER, WP_APP_PASSWORD in .env). Der Entwurf bleibt freigegeben.", "fehler")
        if row["status"] in OPEN_STATES:
            try:
                store.set_status(draft_id, "freigeben", von=_user())
            except ConflictError:
                pass
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    claimed = store.claim_draft(draft_id, von=_user())
    if claimed is None:
        return render_template("fehler.html", titel="Schon unterwegs", text="Dieser Entwurf wird gerade veröffentlicht oder ist schon veröffentlicht.", draft_id=draft_id), 409
    try:
        info = publish_draft(claimed, _settings(), wp, store, status=status)
    except Exception as exc:  # noqa: BLE001
        log.exception("Veröffentlichen fehlgeschlagen")
        store.mark_publish_failed(draft_id, str(exc))
        store.event("fehler", id=draft_id, titel=row["titel"], fehler=str(exc)[:300], schritt="veroeffentlichen", von=_user())
        flash(f"WordPress-Fehler: {str(exc)[:200]} – Status „Fehler“, später erneut versuchen.", "fehler")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    if status == "publish":
        flash(f"Live auf tamil.de: {info['link']}", "ok")
    else:
        flash(f"Als WordPress-Entwurf angelegt: {info['edit_link']}", "ok")
    return redirect(url_for("ui.entwurf", draft_id=draft_id))


@ui.post("/entwurf/<int:draft_id>/veroeffentlichen")
def veroeffentlichen(draft_id: int):
    return _publish(draft_id, "publish")


@ui.post("/entwurf/<int:draft_id>/wp-entwurf")
def wp_entwurf(draft_id: int):
    return _publish(draft_id, "draft")


# ---- Vorschau, Dashboard, Protokoll, Bilder, Health ------------------------------------------------

@ui.get("/vorschau/<int:draft_id>")
def vorschau(draft_id: int):
    row = _draft_or_404(draft_id)
    return render_template("vorschau.html", d=row, content=render_content(row))


@ui.get("/dashboard")
def dashboard():
    days = 30 if request.args.get("tage") == "30" else 7
    return render_template("dashboard.html", dash=get_store().dashboard(days), days=days, labels=STATUS_LABELS)


@ui.get("/protokoll")
def protokoll():
    event = request.args.get("ereignis") or None
    rows = list(get_store().iter_log(event=event, limit=200))
    return render_template("protokoll.html", rows=rows, event=event)


@ui.get("/protokoll.jsonl")
def protokoll_jsonl():
    db_path = _settings().db_path

    def generate():
        # eigene Verbindung: der Request-Store ist beim Streamen schon geschlossen
        from ..store import Store

        with Store(db_path) as store:
            for row in store.iter_log():
                yield json.dumps(row, ensure_ascii=False) + "\n"

    return Response(generate(), mimetype="application/x-ndjson",
                    headers={"Content-Disposition": "attachment; filename=radar-protokoll.jsonl"})


@ui.get("/bild/<name>")
def bild_datei(name: str):
    if not _FILENAME_RE.match(name):
        abort(404)
    return send_from_directory(_settings().bilder_dir, name, conditional=True, max_age=86400)


@ui.get("/gesund")
def gesund():
    store = get_store()
    runs = store.recent_runs(1)
    return jsonify({"ok": True, "letzter_lauf": runs[0]["started_at"] if runs else None,
                    "offen": sum(store.counts_by_status()[s] for s in OPEN_STATES), "zeit": datetime.now(timezone.utc).isoformat()})


@ui.get("/manifest.webmanifest")
def manifest():
    data = {
        "name": "Tamil.de Radar", "short_name": "Radar", "start_url": "/", "display": "standalone",
        "background_color": "#1A1A1C", "theme_color": "#B01E2C", "lang": "de",
        "icons": [{"src": "/static/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/static/icon-512.png", "sizes": "512x512", "type": "image/png"}],
    }
    return Response(json.dumps(data), mimetype="application/manifest+json")


@ui.get("/sw.js")
def service_worker():
    return Response("self.addEventListener('fetch', () => {});\n", mimetype="application/javascript")
