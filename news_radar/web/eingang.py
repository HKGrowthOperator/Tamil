"""Cockpit „Eingang“ (Festlegung F1): Einsendungen der Website ansehen, prüfen und entscheiden.

Alle Angemeldeten sehen Liste und Prüfung; Kontaktdaten und Entscheidungen nur mit dem Recht `eingang_entscheiden`
(redaktion, admin). Übernehmen legt einen Entwurf mit dem Vermerk „Angaben des Einsenders, ungeprüft“ an; danach gilt
der normale Freigabeweg. Geantwortet wird von Hand: das Cockpit bietet nur einen mailto-Link, es verschickt nichts.
"""

from __future__ import annotations

import re
from urllib.parse import quote

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for

from .. import eingang
from . import get_store
from .rechte import darf, recht_noetig

eingang_bp = Blueprint("eingang", __name__)

ANSICHTEN = (("offen", "Offen"), ("abgeschlossen", "Abgeschlossen"), ("alle", "Alle"))
_EMAIL_RE = re.compile(r"[^@\s<>\"'()]+@[^@\s<>\"'()]+\.[^@\s<>\"'()]+")


def _client():
    """Transport zu WordPress: in Tests gesetzt, sonst aus den Einstellungen (ohne WordPress: None, der Dienst meldet)."""
    client = current_app.extensions.get("eingang_client")
    settings = current_app.extensions["settings"]
    if client is None and settings.wordpress_enabled:
        client = current_app.extensions["eingang_client"] = eingang.client_fuer(settings)
    return client


def _oder_404(vorgang: str) -> dict:
    e = eingang.holen(get_store(), vorgang)
    if e is None:
        abort(404)
    return e


def mailto(e: dict) -> str:
    """Link, der das eigene Mailprogramm öffnet (Antwort von Hand). Leer, wenn die Adresse nicht wie eine aussieht."""
    email = (e.get("email") or "").strip()
    if not _EMAIL_RE.fullmatch(email):
        return ""
    return f"mailto:{quote(email, safe='@')}?subject={quote('Ihre Einsendung ' + e['vorgangsnummer'] + ' bei Tamil.de')}"


@eingang_bp.get("/eingang")
def liste():
    ansicht = request.args.get("ansicht", "offen")
    if ansicht not in dict(ANSICHTEN):
        ansicht = "offen"
    art = request.args.get("art") or None
    if art not in eingang.ARTEN:
        art = None
    store = get_store()
    zahlen = eingang.zaehlen(store)
    summen = {"offen": sum(zahlen[s] for s in eingang.OFFEN), "abgeschlossen": sum(zahlen[s] for s in eingang.ABSCHLUESSE)}
    summen["alle"] = summen["offen"] + summen["abgeschlossen"]
    return render_template("eingang.html", eintraege=eingang.liste(store, ansicht, art), ansicht=ansicht, art=art,
                           ansichten=ANSICHTEN, summen=summen, arten=eingang.ARTEN, status_label=eingang.STATUS_LABEL)


@eingang_bp.get("/eingang/<vorgang>")
def einsendung(vorgang: str):
    e = _oder_404(vorgang)
    vorschlag = e["entwurf"] or eingang.regel_vorbereitung(e)[1]
    return render_template("einsendung.html", e=e, vorschlag=vorschlag, felder=eingang.FELDER[e["art"]],
                           arten=eingang.ARTEN, status_label=eingang.STATUS_LABEL, vermerk=eingang.VERMERK,
                           mailto=mailto(e) if darf("eingang_entscheiden") else "",
                           datum_text=eingang.datum_text, lokal=eingang._lokal,
                           entscheidungen=eingang.ENTSCHEIDUNGEN)


@eingang_bp.post("/eingang/<vorgang>/uebernehmen")
@recht_noetig("eingang_entscheiden")
def uebernehmen(vorgang: str):
    _oder_404(vorgang)
    felder = {k: request.form.get(k, "") for k in ("titel", "teaser", "text", "event_datum", "event_ort", "ticket_url")}
    try:
        did = eingang.uebernehmen(get_store(), current_app.extensions["settings"], vorgang, von=session.get("user", ""),
                                  felder=felder, client=_client())
    except eingang.Konflikt as exc:
        flash(f"Nicht übernommen: {exc}.", "fehler")
        return redirect(url_for("eingang.einsendung", vorgang=vorgang))
    except ValueError as exc:
        flash(f"Nicht übernommen: {exc}.", "fehler")
        return redirect(url_for("eingang.einsendung", vorgang=vorgang))
    flash(f"Übernommen als Entwurf ({eingang.VERMERK}). Jetzt prüfen, bearbeiten und freigeben.", "ok")
    return redirect(url_for("ui.entwurf", draft_id=did))


@eingang_bp.post("/eingang/<vorgang>/status")
@recht_noetig("eingang_entscheiden")
def status(vorgang: str):
    _oder_404(vorgang)
    neu = request.form.get("status", "")
    if neu not in eingang.ENTSCHEIDUNGEN:
        abort(400, "Unbekannter Status.")
    try:
        eingang.abschliessen(get_store(), vorgang, neu, von=session.get("user", ""), client=_client())
    except eingang.Konflikt as exc:
        flash(f"Nicht geändert: {exc}.", "fehler")
        return redirect(url_for("eingang.einsendung", vorgang=vorgang))
    flash(f"Einsendung {vorgang}: {eingang.STATUS_LABEL[neu]}. Eine Antwort an den Einsender geht nur von Hand.", "ok")
    return redirect(url_for("eingang.liste"))


@eingang_bp.post("/eingang/<vorgang>/notiz")
@recht_noetig("eingang_entscheiden")
def notiz(vorgang: str):
    _oder_404(vorgang)
    eingang.notiz_setzen(get_store(), vorgang, request.form.get("notiz", ""), von=session.get("user", ""))
    flash("Notiz gespeichert.", "ok")
    return redirect(url_for("eingang.einsendung", vorgang=vorgang))
