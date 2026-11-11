"""Cockpit-Seiten für den Betrieb (Vertrag B1.1): Stopp-Schalter und Zeitplan."""

from __future__ import annotations

from datetime import datetime

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for

from .. import dienst, schalter
from . import get_store
from .rechte import pruefe, recht_noetig

betrieb = Blueprint("betrieb", __name__)


def _kanal_or_404(kanal: str) -> str:
    if kanal not in schalter.KANAELE:
        abort(404)
    return kanal


# ---- Schalter -----------------------------------------------------------------------------------

@betrieb.get("/schalter")
def schalter_seite():
    return render_template("schalter.html", kanaele=schalter.stand(get_store()))


@betrieb.post("/schalter/<kanal>/an")
@recht_noetig("anhalten")
def anhalten(kanal: str):
    _kanal_or_404(kanal)
    try:
        schalter.setzen(get_store(), kanal, True, wer=session.get("user", ""), grund=request.form.get("grund", ""))
    except ValueError as exc:
        flash(f"{exc} – nichts angehalten.", "fehler")
        return redirect(url_for("betrieb.schalter_seite"))
    flash(f"{schalter.LABEL[kanal]} angehalten. Bearbeiten und Freigeben von Hand gehen weiter.", "ok")
    return redirect(url_for("betrieb.schalter_seite"))


@betrieb.post("/schalter/<kanal>/aus")
@recht_noetig("kanal_einschalten")
def einschalten(kanal: str):
    _kanal_or_404(kanal)
    if kanal == "alles":
        pruefe("alles_einschalten")
    schalter.setzen(get_store(), kanal, False, wer=session.get("user", ""), grund=request.form.get("grund", ""))
    rest = schalter.sperre(get_store(), kanal) if kanal != "alles" else None
    if rest is not None:
        flash(f"{schalter.LABEL[kanal]} eingeschaltet – hält aber weiter an, solange „Alles“ angehalten ist.", "fehler")
    else:
        flash(f"{schalter.LABEL[kanal]} läuft wieder. Freigegebenes geht beim nächsten Lauf hinaus.", "ok")
    return redirect(url_for("betrieb.schalter_seite"))


# ---- Zeitplan -----------------------------------------------------------------------------------

def _zeit(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).astimezone(dienst.TZ)
    except ValueError:
        return None


@betrieb.get("/zeitplan")
def zeitplan():
    store = get_store()
    jetzt = datetime.now(dienst.TZ)
    zeilen = []
    for e in dienst.plan(current_app.extensions["settings"]):
        letzter = store.db.execute("SELECT * FROM dienst_laeufe WHERE aufgabe = ? ORDER BY id DESC LIMIT 1",
                                   (e.name,)).fetchone()
        gestartet = store.db.execute("SELECT start FROM dienst_laeufe WHERE aufgabe = ? AND ergebnis IS NOT "
                                     "'abgebrochen' ORDER BY id DESC LIMIT 1", (e.name,)).fetchone()
        naechste = dienst.naechster_termin(jetzt, e.regel, _zeit(gestartet["start"]) if gestartet else None)
        zeilen.append({"plan": e, "takt": dienst.takt_text(e.regel), "letzter": dict(letzter) if letzter else None,
                       "naechste": naechste.isoformat() if naechste else "", "sperre": schalter.haelt_an(store, e.kanaele),
                       "kanaele": [schalter.LABEL[k] for k in e.kanaele]})
    worker = schalter.sperre(store, "redaktion")
    return render_template("zeitplan.html", zeilen=zeilen, worker_sperre=worker,
                           workflow=current_app.extensions["settings"].workflow)
