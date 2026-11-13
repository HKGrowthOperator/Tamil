"""Routen der Freigabe-App."""

from __future__ import annotations

import json
import logging
import hashlib
import re
from datetime import datetime, timezone
from urllib.parse import urlsplit

from flask import (Blueprint, Response, abort, current_app, flash, g, jsonify, redirect, render_template, request,
                   send_from_directory, session, url_for)

from .. import bilder, images, lizenz, prompts, schalter
from ..workflow import costs, repo
from ..publisher import inhalt_fuer_wp  # Vorschau wie veröffentlicht (Nachtrag: mit Vermerk)
from ..render import sanitize_html
from ..store import OPEN_STATES, PUBLISHABLE, STATUSES, TRANSITIONS, ConflictError
from ..wordpress import slugify
from . import anmelden, client_ip, get_store, gleich
from .rechte import pruefe, recht_noetig

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


def sicheres_ziel(target: str | None, default: str = "/") -> str:
    """Nur Pfade auf diesem Host: „/…“, aber nicht „//host“, „/\\host“ oder „https://…“ (Open Redirect)."""
    if not target or not target.startswith("/") or target.startswith("//") or "\\" in target:
        return default
    teile = urlsplit(target)
    if teile.scheme or teile.netloc or any(ord(c) < 32 for c in target):
        return default
    return target


# ---- Login -------------------------------------------------------------------------

@ui.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not gleich(request.form.get("_csrf", ""), session.get("csrf", "")) or not session.get("csrf"):
            abort(400, "Formular abgelaufen – bitte Seite neu laden.")
        user = request.form.get("user", "").strip()[:100]
        password = request.form.get("password", "")[:1000]
        drossel = current_app.extensions["drossel"]
        schluessel = {"ip": client_ip(), "nutzer": user.casefold()}
        if drossel.gesperrt(schluessel):
            flash("Zu viele Fehlversuche – bitte in 15 Minuten erneut versuchen.", "fehler")
            return render_template("login.html"), 429
        ergebnis = anmelden(_settings(), user, password, get_store())
        if ergebnis:
            rolle, konto = ergebnis
            drossel.erfolg(schluessel)
            session.permanent = True
            session["user"] = user
            session["rolle"] = rolle
            session["sid"] = repo.sitzung_anlegen(get_store(), user, konto)
            return redirect(sicheres_ziel(request.args.get("next")))
        drossel.fehler(schluessel)
        flash("Benutzername oder Passwort falsch.", "fehler")
    return render_template("login.html")


@ui.post("/logout")
@recht_noetig("abmelden")
def logout():
    repo.sitzung_beenden(get_store(), session.get("sid", ""))
    session.clear()
    return redirect(url_for("ui.login"))


# ---- Feed ----------------------------------------------------------------------------

@ui.get("/")
def feed():
    status = request.args.get("status", "neu")
    if status not in STATUSES:
        abort(404)
    herkunft = "nachtrag" if request.args.get("herkunft") == "nachtrag" else None  # Filter „Rückblick“
    page = max(1, int(request.args.get("seite", 1)))
    per_page = 30
    store = get_store()
    counts = store.counts_by_status()
    counts["veroeffentlicht"] += counts.get("in_wordpress", 0)
    statuses = ["veroeffentlicht", "in_wordpress", "wird_veroeffentlicht"] if status == "veroeffentlicht" else [status]
    drafts = []
    for s in statuses:
        drafts += store.list_drafts(s, limit=per_page, offset=(page - 1) * per_page, herkunft=herkunft)
    drafts.sort(key=lambda d: d["updated_at"], reverse=True) if status != "neu" else None
    return render_template("feed.html", drafts=drafts, status=status, tabs=TABS, counts=counts, page=page,
                           has_more=len(drafts) >= per_page, labels=STATUS_LABELS, herkunft=herkunft)


@ui.post("/entwurf/<int:draft_id>/status")
@recht_noetig("bearbeiten")
def set_status(draft_id: int):
    aktion = request.form.get("aktion", "")
    if aktion not in TRANSITIONS:
        abort(400)
    store = get_store()
    stand = None
    if aktion in ("freigeben", "erneut"):
        pruefe("freigeben")
        stand = _stand(request.form.get("stand"))
        if stand is None or (store.get_draft(draft_id) or {}).get("stand", stand) != stand:
            flash(VERALTET if stand is None else GEAENDERT, "fehler")  # nichts ändern, noch einmal ansehen
            return redirect(url_for("ui.entwurf", draft_id=draft_id))
        gesperrt = lizenz.sperre(store, _draft_or_404(draft_id), _settings())
        if gesperrt:  # Gate (Spezifikation Bilder 3.3): ohne vollständigen Lizenz-Datensatz keine Freigabe
            flash(f"{gesperrt}. Bitte „Lizenz eintragen“ – Freigabe gesperrt.", "fehler")
            return redirect(url_for("ui.entwurf", draft_id=draft_id))
    try:
        neu = store.set_status(draft_id, aktion, von=_user(), stand=stand)
    except ConflictError as exc:
        if stand is not None and (store.get_draft(draft_id) or {}).get("stand") != stand:
            flash(GEAENDERT, "fehler")
            return redirect(url_for("ui.entwurf", draft_id=draft_id))
        return render_template("fehler.html", titel="Zustand hat sich geändert", text=str(exc), draft_id=draft_id), 409
    store.event("aktion", id=draft_id, aktion=aktion, status=neu, von=_user())
    row = store.get_draft(draft_id)
    repo.aktion(store, wer=_user(), aktion=aktion, draft_id=draft_id, story_id=row.get("story_id"),
                fassung=repo.fassung_hash(row))
    sperre = schalter.sperre(store, "website") if neu == "freigegeben" else None
    if sperre is not None:  # wie Entwurfsseite und Sammelfreigabe: freigegeben, wartet
        _wartet(row, sperre)
        flash(_angehalten_meldung(sperre, "Nichts wurde an WordPress übertragen. Der Entwurf ist freigegeben und "
                                          "wartet; er geht beim nächsten Lauf hinaus, sobald der Schalter wieder aus "
                                          "ist."), "fehler")
    else:
        flash(f"{STATUS_LABELS.get(neu, neu)}.", "ok")
    return redirect(sicheres_ziel(request.form.get("next") or request.args.get("next"), url_for("ui.feed")))


SAMMEL_MAX = 100  # mehr Karten zeigt der Feed nicht auf einmal


@ui.post("/entwurf/sammelfreigabe")
@recht_noetig("freigeben")
def sammelfreigabe():
    """Mehrere Entwürfe freigeben: je Entwurf derselbe Übergang und dieselbe Protokollzeile wie einzeln. Was nicht
    freigegeben werden kann, wird mit Grund gemeldet. Bei angehaltener Website: freigegeben, wartet (wie einzeln)."""
    ziel = sicheres_ziel(request.form.get("next"), url_for("ui.feed"))
    ids: list[int] = []
    for roh in request.form.getlist("ids"):
        # nur ASCII-Ziffern: isdigit() ließe „²“ durch (int() scheitert), isdecimal() allein andere Schriften
        if roh.isascii() and roh.isdecimal() and int(roh) not in ids:
            ids.append(int(roh))
    if not ids:
        flash("Keine Entwürfe ausgewählt.", "fehler")
        return redirect(ziel)
    if len(ids) > SAMMEL_MAX:
        flash(f"Höchstens {SAMMEL_MAX} Entwürfe auf einmal – bitte kleiner auswählen.", "fehler")
        return redirect(ziel)
    store = get_store()
    sperre = schalter.sperre(store, "website")
    frei, nicht = [], []
    for draft_id in ids:
        row = store.get_draft(draft_id)
        if row is None:
            nicht.append(f"#{draft_id}: nicht gefunden")
            continue
        if row["status"] not in OPEN_STATES and row["status"] != "fehler":
            nicht.append(f"#{draft_id} „{row['titel'][:60]}“: Status „{STATUS_LABELS.get(row['status'], row['status'])}“")
            continue
        stand = _stand(request.form.get(f"stand_{draft_id}"))
        if stand is None or row.get("stand") != stand:
            nicht.append(f"#{draft_id} „{row['titel'][:60]}“: {VERALTET if stand is None else GEAENDERT}")
            continue
        gesperrt = lizenz.sperre(store, row, _settings())
        if gesperrt:
            nicht.append(f"#{draft_id} „{row['titel'][:60]}“: {gesperrt}")
            continue
        aktion = _freigeben(store, row, stand=stand)
        if not aktion:
            geaendert = (store.get_draft(draft_id) or {}).get("stand") != stand
            nicht.append(f"#{draft_id} „{row['titel'][:60]}“: "
                         + (GEAENDERT if geaendert else "Zustand hat sich gerade geändert"))
            continue
        store.event("aktion", id=draft_id, aktion=aktion, status="freigegeben", von=_user(), sammel=True)
        if sperre is not None:
            _wartet(row, sperre)
        frei.append(draft_id)
    if frei:
        flash(f"{len(frei)} {'Entwurf' if len(frei) == 1 else 'Entwürfe'} freigegeben.", "ok")
    if frei and sperre is not None:
        flash(_angehalten_meldung(sperre, "Nichts wurde an WordPress übertragen. Die freigegebenen Entwürfe warten "
                                          "und gehen beim nächsten Lauf hinaus, sobald der Schalter wieder aus ist."),
              "fehler")
    if nicht:
        flash(f"Nicht freigegeben ({len(nicht)}): " + "; ".join(nicht), "fehler")
    return redirect(ziel)


# ---- Bearbeiten -------------------------------------------------------------------------

def _protokoll(aktion: str, row: dict, **kw) -> None:
    """Eine Zeile im Protokoll der Aktionen für eine Person aus dem Cockpit (nur Kennungen, keine Inhalte)."""
    repo.aktion(get_store(), wer=_user(), aktion=aktion, draft_id=row["id"], story_id=row.get("story_id"), **kw)


@ui.post("/entwurf/<int:draft_id>")
@recht_noetig("bearbeiten")
def entwurf_speichern(draft_id: int):
    store = get_store()
    row = _draft_or_404(draft_id)
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
    _protokoll("gespeichert", row, fassung=repo.fassung_hash(store.get_draft(draft_id)))
    flash("Gespeichert.", "ok")
    return redirect(url_for("ui.entwurf", draft_id=draft_id))


@ui.get("/entwurf/<int:draft_id>")
def entwurf(draft_id: int):
    store = get_store()
    row = _draft_or_404(draft_id)
    settings = _settings()
    pool = bilder.BildPool(settings.bildpool_dir).status()
    themen = [{"slug": t["thema"], "rubrik": t.get("rubrik", ""), "anzahl": pool.get(t["thema"], {}).get("anzahl", 0)}
              for t in prompts.bildpool_themen()]
    from .redaktion import belege_fuer

    asset = lizenz.asset_fuer(store, row) if row.get("bild_datei") else None
    luecken = lizenz.luecken(store, row, settings)
    return render_template("entwurf.html", d=row, labels=STATUS_LABELS, categories=settings.categories,
                           belege=belege_fuer(store, row),
                           can_publish=row["status"] in PUBLISHABLE, open_states=OPEN_STATES,
                           lizenz_luecken=luecken, lizenz_meldung=lizenz.meldung(luecken) if luecken else "",
                           lizenz_asset=asset, lizenz_formular=_lizenz_vorbelegung(row, asset),
                           lizenz_herkuenfte=lizenz.FORMULAR_HERKUNFT, lizenz_kuerzel=lizenz.FORMULAR_KUERZEL,
                           lizenz_namen=lizenz.NAMEN, lizenz_name=lizenz.lizenz_name, cc_versionen=lizenz.CC_VERSIONEN,
                           ki_freigegeben=settings.bild_ki_freigabe,
                           preview=inhalt_fuer_wp(row), bildthemen=themen,
                           ki_bereit=bool(settings.gemini_key) and settings.bild_ki_freigabe,
                           bild_thema=row.get("bild_thema") or prompts.thema_fuer(row["kategorie"], row["titel"]))


def _angehalten_meldung(sperre: dict, was: str) -> str:
    from . import fmt_dt

    return (f"{schalter.LABEL[sperre['kanal']]} angehalten (seit {fmt_dt(sperre['seit'])}, {sperre['wer']}: "
            f"{sperre['grund']}). {was}")


@ui.post("/entwurf/<int:draft_id>/neu-schreiben")
@recht_noetig("bearbeiten")
def neu_schreiben(draft_id: int):
    store = get_store()
    row = _draft_or_404(draft_id)
    anweisung = request.form.get("anweisung", "").strip() or "Schreibe den Text flüssiger und kürzer."
    sperre = schalter.sperre(store, "redaktion")
    if sperre is not None:
        flash(_angehalten_meldung(sperre, "Neu schreiben ruft ein Modell auf und geht erst wieder, wenn der Schalter "
                                          "aus ist. Bearbeiten von Hand geht weiter."), "fehler")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    try:
        draft = _writer().rewrite(row, anweisung)
    except schalter.Gestoppt as exc:
        flash(_angehalten_meldung(exc.sperre, "Der Text bleibt unverändert."), "fehler")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    except Exception as exc:  # noqa: BLE001 - dem Nutzer den Fehler zeigen statt 500
        log.exception("Umschreiben fehlgeschlagen")
        flash(f"Umschreiben fehlgeschlagen: {str(exc)[:200]}", "fehler")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    if draft is None:
        flash("Das Modell hat den Text nicht umgeschrieben (abgelehnt).", "fehler")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    fields = draft.model_dump()
    fields.pop("typ", None)
    fields["hinweise"] = [h for h in row["hinweise"] if not h.startswith("Rohfassung")]  # neu geschrieben = keine Rohfassung mehr
    store.update_draft(draft_id, von=_user(), rewrite_count=row["rewrite_count"] + 1, **fields)
    if row["status"] in ("neu", "zurueckgestellt"):
        try:
            store.set_status(draft_id, "bearbeiten", von=_user())
        except ConflictError:
            pass
    store.event("neu_geschrieben", id=draft_id, anweisung=anweisung, von=_user())
    _protokoll("neu_geschrieben", row, fassung=repo.fassung_hash(store.get_draft(draft_id)))
    flash("Neu geschrieben – bitte prüfen.", "ok")
    return redirect(url_for("ui.entwurf", draft_id=draft_id))


@ui.post("/entwurf/<int:draft_id>/zuruecksetzen")
@recht_noetig("bearbeiten")
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
    _protokoll("zurueckgesetzt", row, fassung=repo.fassung_hash(store.get_draft(draft_id)))
    flash("Auf das Original zurückgesetzt.", "ok")
    return redirect(url_for("ui.entwurf", draft_id=draft_id))


@ui.post("/entwurf/<int:draft_id>/bild")
@recht_noetig("bearbeiten")
def bild(draft_id: int):
    store = get_store()
    row = _draft_or_404(draft_id)
    if row["status"] not in OPEN_STATES:  # sonst ginge ein ungesehenes Bild ohne neue Freigabe hinaus
        flash("Freigegebene Entwürfe zuerst zurückstellen, dann das Bild ersetzen.", "fehler")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    settings = _settings()
    aktion = request.form.get("aktion", "karte")
    stem_base = (row.get("bild_datei") or f"{row['uid'][:12]}-{slugify(row['titel'], 50)}.jpg").removesuffix(".jpg")
    stem_base = re.sub(r"-\d+$", "", stem_base)
    version = sum(1 for e in store.iter_log(event="bild") if e.get("id") == draft_id) + 2
    stem = f"{stem_base}-{version}"
    label = next((c.label for c in settings.categories if c.slug == row["kategorie"]), row["kategorie"])
    felder: dict = {}  # Bildfelder (Prompt, Thema, Suchbegriff) gehen mit dem bedingten Bild-UPDATE zusammen
    try:
        if aktion == "upload":
            file = request.files.get("datei")
            if not file or not file.filename:
                flash("Keine Datei ausgewählt.", "fehler")
                return redirect(url_for("ui.entwurf", draft_id=draft_id))
            # kein Standardnachweis: Rechte trägt die Redaktion unter „Lizenz eintragen“ ein (bis dahin gesperrt)
            image = images.from_upload(file.read(), stem, request.form.get("credit", "").strip())
            if lizenz.ist_karten_alt(row.get("bild_alt")):  # beschreibt die Bildkarte, nicht das neue Foto
                felder = {"bild_alt": ""}
        elif aktion in ("ki", "pool") and not settings.bild_ki_freigabe:
            flash(KI_AUS, "fehler")
            return redirect(url_for("ui.entwurf", draft_id=draft_id))
        elif aktion == "ki":
            thema = request.form.get("bild_thema", "").strip() or row.get("bild_thema") or ""
            motiv = request.form.get("bild_prompt", "").strip()
            if not settings.gemini_key:
                flash("Für KI-Bilder fehlt GEMINI_API_KEY in der .env – Bild unverändert.", "fehler")
                return redirect(url_for("ui.entwurf", draft_id=draft_id))
            sperre = schalter.sperre(store, "redaktion")
            if sperre is not None:  # die Bild-KI ist ein Aufruf nach außen der Agenten-Redaktion
                flash(_angehalten_meldung(sperre, "KI-Bilder gehen erst wieder, wenn der Schalter aus ist – Bild "
                                                  "unverändert."), "fehler")
                return redirect(url_for("ui.entwurf", draft_id=draft_id))
            prompt = prompts.bild_prompt_bauen(motiv, thema)
            image = _ki_bild(store, settings, row, prompt, stem)
            if image is False:
                return redirect(url_for("ui.entwurf", draft_id=draft_id))
            felder = {"bild_prompt": motiv, "bild_thema": thema}
            if image is None:
                flash("Die Bild-KI hat kein Bild geliefert (Protokoll prüfen) – Bild unverändert.", "fehler")
                return redirect(url_for("ui.entwurf", draft_id=draft_id))
            if thema:
                bilder.BildPool(settings.bildpool_dir).add(thema, image, prompt)
        elif aktion == "pool":
            thema = request.form.get("bild_thema", "").strip()
            image = bilder.BildPool(settings.bildpool_dir).pick(thema, stem) if thema else None
            if image is None:
                flash(f"Im Bildpool „{thema or '–'}“ liegt noch kein Bild – Bild unverändert.", "fehler")
                return redirect(url_for("ui.entwurf", draft_id=draft_id))
            felder = {"bild_thema": thema}
        elif aktion == "stock":
            query = request.form.get("suchbegriff", "").strip() or row.get("bild_suchbegriff") or row["titel"]
            image = images.featured_image(settings, query, row["titel"], label, stem)
            if image.origin == "karte":
                flash("Kein Stockfoto gefunden (oder kein Unsplash/Pexels-Schlüssel) – Bildkarte erzeugt.", "fehler")
            felder = {"bild_suchbegriff": query}
            if image.origin == "karte":  # Rückfall auf die Bildkarte: sie beschreibt sich selbst
                felder["bild_alt"] = lizenz.alt_fuer_karte(row["titel"])
        else:
            image = images.branded_card(row["titel"], label, stem, row.get("kategorie") or "")
            felder = {"bild_alt": lizenz.alt_fuer_karte(row["titel"])}  # die Karte beschreibt sich selbst
    except Exception as exc:  # noqa: BLE001
        log.exception("Bild fehlgeschlagen")
        flash(f"Bild fehlgeschlagen: {str(exc)[:200]}", "fehler")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    # Eindeutiger Name je Entwurf und Inhalt: nie die Datei eines anderen Entwurfs überschreiben
    basis = re.sub(r"(?:-e\d+)?-(?:\d+|[0-9a-f]{8})$", "", stem_base)
    name, _thumb = images.save_pair(image, settings.bilder_dir,
                                    f"{basis}-e{draft_id}-{hashlib.sha256(image.data).hexdigest()[:8]}")
    # erst schreiben, dann aufräumen (und nie eine Datei löschen, auf die ein anderer Entwurf zeigt)
    if not store.update_draft(draft_id, von=_user(), nur_status=OPEN_STATES, bild_vorher=row.get("bild_datei"),
                              bild_datei=name, bild_credit=image.credit, bild_origin=image.origin, **felder):
        # inzwischen freigegeben oder anderes Bild: nichts ändern, neue Datei nur weg, wenn niemand darauf zeigt
        if not store.db.execute("SELECT 1 FROM drafts WHERE bild_datei = ? LIMIT 1", (name,)).fetchone():
            for neu in (name, _thumb):
                (settings.bilder_dir / neu).unlink(missing_ok=True)
        flash(GEAENDERT, "fehler")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    images.datei_sicherstellen(image, settings.bilder_dir, name)
    # gemeinsamer Speicherweg: jedes Bild bekommt seinen Lizenz-Datensatz (beim Upload offen bis zur Eingabe)
    asset_id = lizenz.anlegen(store, datei=name, daten=image.data, story_id=row.get("story_id"), draft_id=draft_id,
                              felder=lizenz.datensatz(image, titel=row["titel"] if image.origin == "karte" else "",
                                                      alt=felder.get("bild_alt") or row.get("bild_alt") or ""))
    andere = row.get("bild_datei") and store.db.execute(
        "SELECT 1 FROM drafts WHERE bild_datei = ? AND id != ? LIMIT 1", (row["bild_datei"], draft_id)).fetchone()
    for old in (() if andere else (row.get("bild_datei"), (row.get("bild_datei") or "").replace(".jpg", "-thumb.jpg"))):
        if old and old not in (name, _thumb):
            (settings.bilder_dir / old).unlink(missing_ok=True)
    store.event("bild", id=draft_id, aktion=aktion, origin=image.origin, von=_user(), asset=asset_id)
    _protokoll("bild", row, notiz=f"{aktion}: Asset {asset_id}")
    fehlt = lizenz.sperre(store, store.get_draft(draft_id) or row, _settings())
    flash("Bild ersetzt." + (f" {fehlt} – bitte „Lizenz eintragen“." if fehlt else ""), "fehler" if fehlt else "ok")
    return redirect(url_for("ui.entwurf", draft_id=draft_id))


KI_AUS = ("KI-Bilder und der Bildpool sind aus (BILD_KI_FREIGABE, Entscheidung „keine KI-Bilder“) – Bild unverändert. "
          "Commons, Register, Stock, eigenes Bild und die Bildkarte gehen weiter.")


def _ki_bild(store, settings, row: dict, prompt: str, stem: str):
    """„Neu generieren“ wie in der Agent-Kette: Kosten vorher reservieren, jeden Aufruf nach agent_usage schreiben.
    False = abgebrochen (Meldung ist gesetzt), None = die Bild-KI hat nichts geliefert."""
    from ..workflow.providers import budget_fuer, usage_protokollieren

    betrag = costs.bild_kosten(settings.bild_modell, settings.bild_groesse)
    budget = budget_fuer(settings, store)
    try:
        reservierung = budget.reservieren(betrag, "bild", row.get("story_id"))
    except costs.BudgetErschoepft as exc:
        flash(f"Budget erreicht ({exc}) – kein KI-Bild, Bild unverändert.", "fehler")
        return False
    try:
        image = bilder.from_gemini(prompt, settings, stem, current_app.extensions.get("bild_transport"))
        usage_protokollieren(store, rolle="bild", provider="gemini", modell_angefragt=settings.bild_modell,
                             modell=settings.bild_modell, usd=betrag if image else 0.0, bilder=1 if image else 0,
                             status="ok" if image else "fehler", story_id=row.get("story_id"))
    finally:
        budget.freigeben(reservierung)
    return image


def _lizenz_vorbelegung(row: dict, asset: dict | None) -> dict:
    """Werte für das Formular „Lizenz eintragen“: aus dem vorhandenen Datensatz, sonst leer; Nachweis aus dem Entwurf."""
    a = asset or {}
    kuerzel = a.get("lizenz_kuerzel") or ""
    basis, version = kuerzel, ""
    m = re.fullmatch(r"(cc-by(?:-sa)?)-(\d\.\d)", kuerzel)
    if m:
        basis, version = m.group(1), m.group(2)
    return {"urheber": a.get("urheber") or "", "rechteinhaber": a.get("rechteinhaber") or "", "lizenz": basis,
            "version": version or "4.0", "umfang": lizenz.umfang_menge(a.get("umfang")) or {"website"},
            "quelle_url": a.get("quelle_url") or "", "ablauf": a.get("ablauf") or "",
            "alt": next((t for t in (row.get("bild_alt"), a.get("alt")) if t and not lizenz.ist_karten_alt(t)), ""),
            "nachweis": row.get("bild_credit") or "",
            "herkunft": lizenz.formular_herkunft_aus(a.get("herkunft") or "", kuerzel)}


@ui.post("/entwurf/<int:draft_id>/lizenz")
@recht_noetig("bearbeiten")
def lizenz_eintragen(draft_id: int):
    """Formular „Lizenz eintragen“ (Spezifikation Bilder 3.4): Prüfung, neuer Datensatz, Nachweis und Alt-Text am
    Entwurf, Protokollzeile ohne Personendaten. Bildkarte und KI-Bilder bekommen ihren Datensatz nur automatisch."""
    store = get_store()
    row = _draft_or_404(draft_id)
    zurueck = redirect(url_for("ui.entwurf", draft_id=draft_id) + "#lizenz")
    if row["status"] not in OPEN_STATES:
        flash("Freigegebene Entwürfe zuerst zurückstellen, dann die Lizenz eintragen.", "fehler")
        return zurueck
    pfad = _settings().bilder_dir / (row.get("bild_datei") or "-")
    if not row.get("bild_datei") or not pfad.is_file():
        flash("Dieser Entwurf hat kein Bild.", "fehler")
        return zurueck
    if row.get("bild_origin") in ("karte", "ki", "pool"):
        flash("Bildkarte und KI-Bilder bekommen ihren Lizenz-Datensatz automatisch – bitte das Bild ersetzen.", "fehler")
        return zurueck
    datei = request.files.get("beleg_datei")
    beleg = (datei.filename or "", datei.read(lizenz.BELEG_MAX + 1)) if datei and datei.filename else None
    felder, fehler = lizenz.formular_pruefen(request.form, beleg, titel=row["titel"])
    if fehler:
        flash("Lizenz nicht eingetragen: " + "; ".join(fehler), "fehler")
        return zurueck
    endung = felder.pop("_beleg_endung", "")
    if endung:
        felder["beleg"] = lizenz.beleg_ablegen(_settings().data_dir, beleg[1], endung, felder.get("beleg", ""))
    vorher = lizenz.asset_fuer(store, row) or {}
    if vorher.get("bild_url"):
        felder.setdefault("bild_url", vorher["bild_url"])
    if not store.update_draft(draft_id, von=_user(), nur_status=OPEN_STATES, bild_vorher=row["bild_datei"],
                              bild_credit=felder["attribution"], bild_alt=felder["alt"]):
        flash(GEAENDERT, "fehler")
        return zurueck
    asset_id = lizenz.anlegen(store, datei=row["bild_datei"], daten=pfad.read_bytes(), story_id=row.get("story_id"),
                              draft_id=draft_id, felder={
                                  **felder, "geprueft_von": _user(),
                                  "geprueft_am": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    store.event("lizenz", id=draft_id, asset=asset_id, kuerzel=felder["lizenz_kuerzel"], von=_user())
    _protokoll("lizenz", row, fassung=repo.fassung_hash(store.get_draft(draft_id)),
               notiz=f"Lizenz eingetragen: {felder['lizenz_kuerzel']}, Umfang {felder['umfang']}, Asset {asset_id}")
    fehlt = lizenz.sperre(store, store.get_draft(draft_id) or row, _settings())
    flash("Lizenz eingetragen." + (f" Noch offen: {fehlt}" if fehlt else ""), "fehler" if fehlt else "ok")
    return zurueck


# ---- Veröffentlichen ------------------------------------------------------------------------

def _publish(draft_id: int, status: str):
    from ..publisher import publish_draft

    store = get_store()
    row = _draft_or_404(draft_id)
    stand = _stand(request.form.get("stand"))
    if stand is None or row.get("stand") != stand:  # nur den Stand veröffentlichen, den die Seite gezeigt hat
        flash(VERALTET if stand is None else GEAENDERT, "fehler")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    gesperrt = lizenz.sperre(store, row, _settings())
    if gesperrt:
        flash(f"{gesperrt}. Bitte „Lizenz eintragen“ – nichts übertragen, nichts freigegeben.", "fehler")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    sperre = schalter.sperre(store, "website")
    if sperre is not None and status != "publish":
        # „In WordPress bearbeiten“ ist kein Freigeben: im Stopp bleibt der Status, sonst ginge der Text später live
        flash(_angehalten_meldung(sperre, "Es wurde kein WordPress-Entwurf angelegt, der Status bleibt "
                                          f"„{STATUS_LABELS.get(row['status'], row['status'])}“. Bitte nach dem "
                                          "Einschalten erneut wählen."), "fehler")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    if sperre is not None:  # Freigeben von Hand geht, übertragen nicht: der Entwurf wartet auf den nächsten Lauf
        _freigeben_wartend(store, row, sperre, stand=stand)
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    wp = _wordpress()
    if wp is None:
        flash("WordPress ist noch nicht angebunden (WP_URL, WP_USER, WP_APP_PASSWORD in .env). Der Entwurf bleibt freigegeben.", "fehler")
        if not _freigeben(store, row, stand=stand) and (store.get_draft(draft_id) or {}).get("stand") != stand:
            flash(GEAENDERT, "fehler")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    claimed = store.claim_draft(draft_id, von=_user(), stand=stand)
    if claimed is None and (store.get_draft(draft_id) or {}).get("stand") != stand:
        flash(GEAENDERT, "fehler")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    if claimed is None:
        return render_template("fehler.html", titel="Schon unterwegs", text="Dieser Entwurf wird gerade veröffentlicht oder ist schon veröffentlicht.", draft_id=draft_id), 409
    try:
        info = publish_draft(claimed, _settings(), wp, store, status=status)
    except schalter.Gestoppt as exc:  # zwischen Prüfung und Aufruf angehalten: nichts übertragen
        store.release_claim(draft_id)
        _freigeben_wartend(store, row, exc.sperre, schon_frei=True)
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    except lizenz.LizenzFehlt as exc:  # zwischen Prüfung und Senden geändert: nichts gesendet
        store.mark_publish_failed(draft_id, str(exc))
        _protokoll("lizenz_fehlt", row, kanal="website", notiz=str(exc)[:200])
        flash(f"{exc} – nicht an WordPress gesendet.", "fehler")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    except Exception as exc:  # noqa: BLE001
        log.exception("Veröffentlichen fehlgeschlagen")
        store.mark_publish_failed(draft_id, str(exc))
        store.event("fehler", id=draft_id, titel=row["titel"], fehler=str(exc)[:300], schritt="veroeffentlichen", von=_user())
        flash(f"WordPress-Fehler: {str(exc)[:200]} – Status „Fehler“, später erneut versuchen.", "fehler")
        return redirect(url_for("ui.entwurf", draft_id=draft_id))
    repo.aktion(store, wer=_user(), aktion="veroeffentlicht" if status == "publish" else "wp_entwurf", draft_id=draft_id,
                story_id=row.get("story_id"), fassung=repo.fassung_hash(row), wp_post_id=info.get("post_id"),
                kanal="website")
    if status == "publish":
        flash(f"Live auf tamil.de: {info['link']}", "ok")
    else:
        flash(f"Als WordPress-Entwurf angelegt: {info['edit_link']}", "ok")
    return redirect(url_for("ui.entwurf", draft_id=draft_id))


GEAENDERT = "Der Entwurf wurde inzwischen geändert, bitte noch einmal ansehen."
VERALTET = "Diese Seite ist veraltet, bitte neu laden und noch einmal ansehen."  # Anfrage ganz ohne Stand


def _stand(roh: str | None) -> int | None:
    """Stand des Entwurfs, den die Seite gezeigt hat (Formularfeld); None, wenn er fehlt oder ungültig ist."""
    roh = (roh or "").strip()
    return int(roh) if roh.isascii() and roh.isdecimal() and len(roh) < 12 else None


def _freigeben(store, row: dict, stand: int | None = None) -> str:
    """Offenen Entwurf freigeben, einen mit Fehler erneut freigeben (mit Protokollzeile). Gibt die tatsächliche
    Aktion zurück („freigeben“ oder „erneut“); leer, wenn er es schon war oder nicht freigebbar ist."""
    aktion = "erneut" if row["status"] == "fehler" else "freigeben"
    if row["status"] not in OPEN_STATES and row["status"] != "fehler":
        return ""
    if lizenz.sperre(store, store.get_draft(row["id"]) or row, _settings()):  # Gate auf jedem Freigabeweg
        return ""
    try:
        store.set_status(row["id"], aktion, von=_user(), stand=stand)
    except ConflictError:
        return ""
    _protokoll(aktion, row, fassung=repo.fassung_hash(row))
    return aktion


def _wartet(row: dict, sperre: dict) -> None:
    """Protokollzeile „zurueckgehalten“ für einen freigegebenen Entwurf bei angehaltener Website (alle Wege gleich)."""
    _protokoll("zurueckgehalten", row, fassung=repo.fassung_hash(row), kanal="website",
               notiz=f"Schalter „{sperre['kanal']}“ angehalten seit {sperre['seit']}")


def _freigeben_wartend(store, row: dict, sperre: dict, schon_frei: bool = False, stand: int | None = None) -> None:
    """Website angehalten: freigeben, nicht übertragen, und dem Menschen sagen, warum und wie es weitergeht."""
    if not schon_frei:
        _freigeben(store, row, stand=stand)
    jetzt = store.get_draft(row["id"])["status"]
    if jetzt != "freigegeben":  # ehrlich bleiben: was nicht freigegeben ist, wartet auch nicht
        flash(_angehalten_meldung(sperre, f"Nichts wurde übertragen; der Entwurf steht auf "
                                          f"„{STATUS_LABELS.get(jetzt, jetzt)}“ und wartet nicht."), "fehler")
        return
    _wartet(row, sperre)
    flash(_angehalten_meldung(sperre, "Nichts wurde an WordPress übertragen. Der Entwurf ist freigegeben und wartet; "
                                      "er geht beim nächsten Lauf hinaus, sobald der Schalter wieder aus ist."), "fehler")


@ui.post("/entwurf/<int:draft_id>/veroeffentlichen")
@recht_noetig("veroeffentlichen")
def veroeffentlichen(draft_id: int):
    return _publish(draft_id, "publish")


@ui.post("/entwurf/<int:draft_id>/wp-entwurf")
@recht_noetig("veroeffentlichen")
def wp_entwurf(draft_id: int):
    return _publish(draft_id, "draft")


# ---- Vorschau, Dashboard, Protokoll, Bilder, Health ------------------------------------------------

@ui.get("/vorschau/<int:draft_id>")
def vorschau(draft_id: int):
    row = _draft_or_404(draft_id)
    return render_template("vorschau.html", d=row, content=inhalt_fuer_wp(row))


@ui.get("/dashboard")
def dashboard():
    days = 30 if request.args.get("tage") == "30" else 7
    return render_template("dashboard.html", dash=get_store().dashboard(days), days=days, labels=STATUS_LABELS)


_DATUM_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _aktionen_filter() -> dict:
    """Filter aus der Adresse: Person, Aktion, Kanal, Zeitraum (YYYY-MM-DD); Unsinniges wird ignoriert."""
    f = {k: (request.args.get(k) or "").strip()[:60] or None for k in ("wer", "aktion", "kanal")}
    for k in ("von", "bis"):
        wert = (request.args.get(k) or "").strip()
        f[k] = wert if _DATUM_RE.match(wert) else None
    return f


@ui.get("/protokoll")
def protokoll():
    store = get_store()
    event = request.args.get("ereignis") or None
    rows = list(store.iter_log(event=event, limit=200))
    filt = _aktionen_filter()
    return render_template("protokoll.html", rows=rows, event=event, aktionen=repo.aktionen_liste(store, **filt),
                           filt=filt, werte=repo.aktionen_werte(store))


@ui.get("/protokoll/aktionen.jsonl")
@recht_noetig("export")
def aktionen_jsonl():
    filt = _aktionen_filter()
    rows = repo.aktionen_liste(get_store(), limit=None, **filt)
    rows.reverse()  # wie /protokoll.jsonl: älteste zuerst
    return Response("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), mimetype="application/x-ndjson",
                    headers={"Content-Disposition": "attachment; filename=radar-aktionen.jsonl"})


@ui.get("/protokoll.jsonl")
@recht_noetig("export")
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
    from ..workflow import jobs
    from .redaktion import budget_stand

    store = get_store()
    runs = store.recent_runs(1)
    warteschlange = jobs.zaehlen(store)
    stand = budget_stand(store)
    gestoppte = schalter.aktive(store)
    return jsonify({"ok": True, "letzter_lauf": runs[0]["started_at"] if runs else None,
                    "offen": sum(store.counts_by_status()[s] for s in OPEN_STATES),
                    "warteschlange": {k: warteschlange[k] for k in ("offen", "laeuft", "tot", "wartet_budget")},
                    "budget": {k: stand[k] for k in ("tag_usd", "monat_usd", "tag_limit", "monat_limit", "warnung", "stopp")},
                    # öffentlich: nur ob und wie viele; Kanäle und Zeiten stehen im geschützten /api/bericht
                    "gestoppt": bool(gestoppte), "gestoppt_kanaele": len(gestoppte),
                    "zeit": datetime.now(timezone.utc).isoformat()})


@ui.get("/manifest.webmanifest")
def manifest():
    data = {
        "name": "Tamil.de Radar", "short_name": "Radar", "start_url": "/", "display": "standalone",
        "background_color": "#FDF9F5", "theme_color": "#B5282A", "lang": "de",
        "icons": [{"src": "/static/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/static/icon-512.png", "sizes": "512x512", "type": "image/png"}],
    }
    return Response(json.dumps(data), mimetype="application/manifest+json")


@ui.get("/sw.js")
def service_worker():
    return Response("self.addEventListener('fetch', () => {});\n", mimetype="application/javascript")
