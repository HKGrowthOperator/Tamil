"""Cockpit-Seiten der Redaktion v2: Belege im Entwurf, „Recherche nötig“, Kosten, Quellen, Warteschlange, Benutzer."""

from __future__ import annotations

import csv
import difflib
import io
import re
from functools import wraps

from flask import Blueprint, Response, abort, current_app, flash, redirect, render_template, request, session, url_for

from .. import net
from ..workflow import jobs, orchestrator, repo
from ..workflow.providers import budget_fuer
from . import get_store

red = Blueprint("red", __name__)

SUPPORT_LABEL = {"bestaetigt": "bestätigt", "einzelquelle": "eine Quelle", "unbestaetigt": "nur Hinweis",
                 "widerspruch": "Widerspruch", "offen": "offen"}
URTEIL_LABEL = {"gedeckt": "gedeckt", "ungedeckt": "nicht belegt", "widerspruch": "Widerspruch", "kein_fakt": "Einordnung"}
ART_LABEL = {"volltext": "Volltext", "zusammenfassung": "Zusammenfassung", "hinweis": "nur Titel (Hinweis)",
             "daten": "strukturierte Daten", "redaktion": "Redaktion"}


def _settings():
    return current_app.extensions["settings"]


def _user() -> str:
    return session.get("user", "")


def admin_noetig(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get("rolle") != "admin":
            abort(403)
        return fn(*args, **kwargs)

    return wrapper


def _plain(html_text: str) -> list[str]:
    text = re.sub(r"</p>|<br\s*/?>|</h2>", "\n", html_text or "")
    text = re.sub(r"<[^>]+>", "", text)
    return [z.strip() for z in text.splitlines() if z.strip()]


def belege_fuer(store, row: dict) -> dict | None:
    """Alles, was die Entwurfsansicht zur Story zeigt (None für Entwürfe aus v1)."""
    sid = row.get("story_id")
    if not sid:
        return None
    story = repo.story(store, sid)
    if story is None:
        return None
    versionen = repo.fassungen(store, story_id=sid, draft_id=row["id"])
    faktencheck = next((v["inhalt"].get("faktencheck") for v in reversed(versionen) if v["rolle"] == "faktencheck"), None)
    texte = [v for v in versionen if v["rolle"] in ("vorlage", "text", "ueberarbeitung", "seo", "entwurf")]
    diffs = []
    vorher = None
    for v in texte:
        jetzt = _plain(v["inhalt"].get("inhalt_html", ""))
        if vorher is not None:
            diff = list(difflib.unified_diff(vorher, jetzt, lineterm="", n=0))[2:]
            diffs.append({"id": v["id"], "rolle": v["rolle"], "diff": diff})
        vorher = jetzt
    aktuell = _plain(row.get("inhalt_html", ""))
    if vorher is not None and aktuell != vorher:
        diffs.append({"id": 0, "rolle": "Redaktion", "diff": list(difflib.unified_diff(vorher, aktuell, lineterm="", n=0))[2:]})
    return {
        "story": story,
        "dokumente": repo.dokumente(store, sid),
        "claims": repo.claims(store, sid),
        "faktencheck": faktencheck or [],
        "versionen": versionen,
        "diffs": diffs,
        "asset": repo.asset_fuer_datei(store, row.get("bild_datei") or ""),
        "kosten": repo.kosten_story(store, sid),
        "aktionen": repo.aktionen(store, row["id"]),
        "fassung": repo.fassung_hash(row),
        "labels": {"support": SUPPORT_LABEL, "urteil": URTEIL_LABEL, "art": ART_LABEL},
    }


def budget_stand(store) -> dict:
    return budget_fuer(_settings(), store).stand()


# ---- Recherche nötig --------------------------------------------------------------------------

@red.get("/recherche")
def recherche():
    store = get_store()
    storys = repo.stories(store, "recherche_erforderlich", limit=100)
    for s in storys:
        s["dokumente"] = repo.dokumente(store, s["id"])
        s["claims"] = repo.claims(store, s["id"])
    laufend = repo.stories(store, ("neu", "recherche", "geprueft", "geschrieben", "geprueft_text"), limit=50)
    return render_template("recherche.html", storys=storys, laufend=laufend, labels=SUPPORT_LABEL, arten=ART_LABEL)


@red.post("/story/<int:story_id>/quelle")
def quelle(story_id: int):
    store = get_store()
    if repo.story(store, story_id) is None:
        abort(404)
    url = request.form.get("url", "").strip()
    try:
        orchestrator.quelle_ergaenzen(store, story_id, url, von=_user())
    except orchestrator.StoryNichtOffen as exc:
        return render_template("fehler.html", titel="Story nicht offen", text=str(exc)), 409
    except ValueError as exc:  # net.UnsafeURL ist ein ValueError
        flash(f"Diese Adresse geht nicht: {exc}", "fehler")
        return redirect(url_for("red.recherche"))
    flash("Quelle ergänzt – die Story läuft erneut durch Recherche und Prüfung.", "ok")
    return redirect(url_for("red.recherche"))


@red.post("/story/<int:story_id>/verwerfen")
def story_verwerfen(story_id: int):
    store = get_store()
    if repo.story(store, story_id) is None:
        abort(404)
    repo.story_setzen(store, story_id, status="verworfen", notiz=f"verworfen von {_user()}")
    store.event("story_verworfen", story=story_id, von=_user())
    flash("Story verworfen.", "ok")
    return redirect(url_for("red.recherche"))


@red.post("/entwurf/<int:draft_id>/dossier")
def dossier(draft_id: int):
    store = get_store()
    try:
        sid = orchestrator.dossier_anlegen(store, draft_id, von=_user())
    except ValueError:
        abort(404)
    flash(f"Dossier angestoßen (Story {sid}). Es erscheint als neuer Entwurf, sobald Recherche und Text fertig sind.", "ok")
    return redirect(url_for("ui.entwurf", draft_id=draft_id))


# ---- Kosten -------------------------------------------------------------------------------------

@red.get("/kosten")
def kosten():
    tage = request.args.get("tage", "30")
    tage_n = int(tage) if tage.isdigit() and 1 <= int(tage) <= 366 else 30
    store = get_store()
    from ..workflow.costs import PRICE_VERSION

    return render_template("kosten.html", bericht=repo.kosten_bericht(store, tage_n), stand=budget_stand(store), tage=tage_n,
                           preis_version=PRICE_VERSION)


@red.get("/kosten.csv")
def kosten_csv():
    tage = request.args.get("tage", "31")
    zeilen = repo.usage_zeilen(get_store(), int(tage) if tage.isdigit() else 31)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(zeilen[0]) if zeilen else ["id"], delimiter=";")
    w.writeheader()
    w.writerows(zeilen)
    return Response("﻿" + buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename=radar-kosten-{tage}-tage.csv"})


# ---- Quellen ------------------------------------------------------------------------------------

@red.get("/quellen")
def quellen():
    status = {s["name"]: s for s in get_store().source_status_all()}
    return render_template("quellen.html", quellen=_settings().alle_quellen, status=status)


# ---- Warteschlange ------------------------------------------------------------------------------

@red.get("/warteschlange")
def warteschlange():
    store = get_store()
    filt = request.args.get("status") or None
    if filt and filt not in ("offen", "laeuft", "fertig", "tot", "wartet_budget"):
        abort(404)
    return render_template("warteschlange.html", jobs=jobs.liste(store, filt, limit=150), zaehler=jobs.zaehlen(store),
                           filt=filt, stand=budget_stand(store))


@red.post("/job/<int:job_id>/erneut")
@admin_noetig
def job_erneut(job_id: int):
    store = get_store()
    if jobs.erneut(store, job_id):
        store.event("job_erneut", job=job_id, von=_user())
        flash("Job steht wieder in der Warteschlange.", "ok")
    else:
        flash("Dieser Job kann nicht neu gestartet werden.", "fehler")
    return redirect(url_for("red.warteschlange", status="tot"))


# ---- Benutzer -----------------------------------------------------------------------------------

@red.route("/nutzer", methods=["GET", "POST"])
@admin_noetig
def nutzer():
    store = get_store()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        aktion = request.form.get("aktion", "anlegen")
        try:
            if aktion == "sperren":
                repo.nutzer_sperren(store, name)
                flash(f"{name} gesperrt.", "ok")
            else:
                if not re.fullmatch(r"[A-Za-z0-9._@-]{2,40}", name):
                    raise ValueError("Name: 2–40 Zeichen, Buchstaben, Ziffern, . _ @ -")
                repo.nutzer_anlegen(store, name, request.form.get("passwort", ""), request.form.get("rolle", "redaktion"))
                flash(f"{name} angelegt.", "ok")
            store.event("nutzer", aktion=aktion, name=name, von=_user())
        except ValueError as exc:
            flash(str(exc), "fehler")
        return redirect(url_for("red.nutzer"))
    return render_template("nutzer.html", nutzer=repo.nutzer_liste(store))


def pruefe_url(url: str) -> bool:
    try:
        net.check_url(url)
        return True
    except ValueError:
        return False
