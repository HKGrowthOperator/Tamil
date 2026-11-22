"""Cockpit „Verzeichnis“ (Festlegung F2, Vertrag B1.4): Einsendungen für das Verzeichnis prüfen und entscheiden.

Alle Angemeldeten sehen Liste und Prüfung; Name und E-Mail des Einsenders und die Entscheidung nur mit dem Recht
`verzeichnis_entscheiden` (redaktion, admin). Neu: Vorschlag mit Hinweisen, Werte änderbar; Änderung: alt neben neu,
Feld für Feld annehmbar; Entfernen: der Eintrag mit Bestätigung. Erst die Freigabe schreibt auf die Website, immer
gegen den gelesenen Stand. Premium lässt sich hier nicht setzen (nur ein Administrator in WordPress).
"""

from __future__ import annotations

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for

from .. import schalter, verzeichnis
from . import get_store
from .rechte import recht_noetig

verzeichnis_bp = Blueprint("verzeichnis", __name__)

ANSICHTEN = (("offen", "Offen"), ("abgeschlossen", "Abgeschlossen"), ("alle", "Alle"))


def _client():
    """Transport zu WordPress: in Tests gesetzt, sonst aus den Einstellungen (ohne WordPress: None)."""
    client = current_app.extensions.get("verzeichnis_client")
    settings = current_app.extensions["settings"]
    if client is None and settings.wordpress_enabled:
        client = current_app.extensions["verzeichnis_client"] = verzeichnis.client_fuer(settings)
    return client


def _oder_404(vorgang: str) -> dict:
    e = verzeichnis.holen(get_store(), vorgang)
    if e is None:
        abort(404)
    return e


def _zurueck(vorgang: str):
    return redirect(url_for("verzeichnis.einsendung", vorgang=vorgang))


@verzeichnis_bp.get("/verzeichnis")
def liste():
    ansicht = request.args.get("ansicht", "offen")
    if ansicht not in dict(ANSICHTEN):
        ansicht = "offen"
    store = get_store()
    zahlen = verzeichnis.zaehlen(store)
    summen = {"offen": sum(zahlen[s] for s in verzeichnis.OFFEN),
              "abgeschlossen": sum(zahlen[s] for s in verzeichnis.ABSCHLUESSE)}
    summen["alle"] = summen["offen"] + summen["abgeschlossen"]
    return render_template("verzeichnis.html", eintraege=verzeichnis.liste(store, ansicht), ansicht=ansicht,
                           ansichten=ANSICHTEN, summen=summen, typen=verzeichnis.TYPEN, arten=verzeichnis.ARTEN,
                           status_label=verzeichnis.STATUS_LABEL)


@verzeichnis_bp.get("/verzeichnis/<vorgang>")
def einsendung(vorgang: str):
    e = _oder_404(vorgang)
    art = verzeichnis._art(e)
    return render_template("verzeichnis_einsendung.html", e=e, typen=verzeichnis.TYPEN, arten=verzeichnis.ARTEN,
                           status_label=verzeichnis.STATUS_LABEL, felder=verzeichnis.FELDER, wahl=verzeichnis.WAHL,
                           vorschlag=verzeichnis.vorschlag(e), vergleich=verzeichnis.vergleich(e),
                           kategorien=verzeichnis.KATEGORIEN.get(art, ()), kategorie_text=verzeichnis.kategorie_text,
                           fehlt_wert=verzeichnis.FEHLT, label=verzeichnis.LABEL,
                           gestoppt=schalter.gestoppt(get_store(), verzeichnis.KANAL))


def _kategorie_aus_formular() -> str | None:
    """„“ (Auswahl leer) = unverändert, „-“ = keine Kategorie (leeren), sonst der Slug."""
    wert = request.form.get("kategorie", "").strip()
    return None if not wert else "" if wert == "-" else wert


@verzeichnis_bp.post("/verzeichnis/<vorgang>/freigeben")
@recht_noetig("verzeichnis_entscheiden")
def freigeben(vorgang: str):
    e = _oder_404(vorgang)
    if any("premium" in k.casefold() for k in request.form):
        abort(400, "Premium setzt nur ein Administrator in WordPress – nicht über das Cockpit.")
    werte = {}
    if e["typ"] == "neu":  # nur Felder aus der Einsendung; was das Formular sonst schickt, zählt nicht
        werte = {k: request.form[f"wert_{k}"] for k in e["felder"] if f"wert_{k}" in request.form}
    annehmen = request.form.getlist("annehmen") if e["typ"] == "aenderung" else None
    client = _client()
    if client is None:
        flash("Nicht freigegeben: WordPress ist nicht verbunden.", "fehler")
        return _zurueck(vorgang)
    try:
        ergebnis = verzeichnis.freigeben(get_store(), client, vorgang, von=session.get("user", ""), werte=werte,
                                         annehmen=annehmen, kategorie=_kategorie_aus_formular())
    except (verzeichnis.Konflikt, verzeichnis.Abgewiesen, ValueError) as exc:  # auch StandVeraltet (409)
        flash(f"Nicht freigegeben: {exc}", "fehler")
        return _zurueck(vorgang)
    except schalter.Gestoppt as exc:
        flash(f"Nicht freigegeben: {exc}. Nach dem Einschalten noch einmal freigeben.", "fehler")
        return _zurueck(vorgang)
    eintrag = ergebnis.get("eintrag") if isinstance(ergebnis.get("eintrag"), dict) else {}
    if ergebnis.get("bereits"):
        fehlt = ", ".join(verzeichnis.LABEL.get(k, k) for k in ergebnis.get("nicht_uebernommen") or [])
        flash(f"Die Website hatte schon freigegeben (Eintrag {eintrag.get('id') or ''})"
              + (f"; Ihre Änderungen wurden nicht übernommen: {fehlt}." if fehlt else "; nichts doppelt."), "fehler")
        return redirect(url_for("verzeichnis.liste"))
    was = {"neu": "angelegt", "aenderung": "geändert", "entfernen": "entfernt (jetzt Entwurf)"}[e["typ"]]
    flash(f"Freigegeben: Eintrag {eintrag.get('id') or ''} {was}.", "ok")
    return redirect(url_for("verzeichnis.liste"))


@verzeichnis_bp.post("/verzeichnis/<vorgang>/ablehnen")
@recht_noetig("verzeichnis_entscheiden")
def ablehnen(vorgang: str):
    _oder_404(vorgang)
    try:
        verzeichnis.ablehnen(get_store(), _client(), vorgang, von=session.get("user", ""))
    except verzeichnis.Konflikt as exc:
        flash(f"Nicht geändert: {exc}.", "fehler")
        return _zurueck(vorgang)
    flash(f"Einsendung {vorgang} abgelehnt. Am Eintrag ändert sich nichts; eine Antwort an den Einsender geht nur "
          "von Hand.", "ok")
    return redirect(url_for("verzeichnis.liste"))
