"""Cockpit-Seite Social (F4): Warteschlange mit Karenz, „von Hand entscheiden“, WhatsApp-Entwürfe, Historie, Regelwerk.

Lesen dürfen alle Angemeldeten; stoppen, Text ändern, freigeben, verwerfen und „als gepostet markieren“ die Redaktion
(Recht `social`); das Regelwerk ändert nur admin (`social_regelwerk`). Gestaltung im heutigen Stil des Cockpits.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, send_file, session, url_for

from ..social import aktionen, konfig, regelwerk
from ..social.ablauf import startmarke
from . import get_store
from .rechte import recht_noetig

social = Blueprint("social", __name__)
BILD_NAME = re.compile(r"social-[0-9a-f]{32}\.jpg")


def _zurueck():
    return redirect(url_for("social.seite"))


def _ausfuehren(fn, ok: str):
    try:
        fn()
    except LookupError:
        abort(404)
    except ValueError as exc:
        flash(f"Nicht ausgeführt: {exc}.", "fehler")
        return _zurueck()
    flash(ok, "ok")
    return _zurueck()


@social.get("/social")
def seite():
    store = get_store()
    jetzt = datetime.now(timezone.utc)
    return render_template("social.html", a=aktionen.ansicht(store), rw=regelwerk.aktuell(store),
                           konf=konfig.laden(), marke=startmarke(store), jetzt=jetzt.isoformat(timespec="seconds"),
                           regeln=regelwerk.REGELN)


@social.get("/social/<int:zeile_id>/bild")
def bild(zeile_id: int):
    z = aktionen.zeile(get_store(), zeile_id)
    if z is None or not BILD_NAME.fullmatch(z.get("bild_datei") or ""):
        abort(404)
    pfad = current_app.extensions["settings"].data_dir / "social" / z["bild_datei"]
    if not pfad.is_file():
        abort(404)
    name = f"tamil-de-{z['wp_post_id']}-{z['kanal']}.jpg"
    return send_file(pfad, mimetype="image/jpeg", as_attachment=bool(request.args.get("download")),
                     download_name=name, max_age=0)


@social.post("/social/<int:zeile_id>/stoppen")
@recht_noetig("social")
def stoppen(zeile_id: int):
    return _ausfuehren(lambda: aktionen.stoppen(get_store(), zeile_id, wer=session.get("user", ""),
                                                grund=request.form.get("grund", "")), "Gestoppt – geht nicht hinaus.")


@social.post("/social/<int:zeile_id>/text")
@recht_noetig("social")
def text(zeile_id: int):
    return _ausfuehren(lambda: aktionen.text_aendern(get_store(), zeile_id, request.form.get("text", ""),
                                                     wer=session.get("user", "")), "Text gespeichert.")


@social.post("/social/<int:zeile_id>/freigeben")
@recht_noetig("social")
def freigeben(zeile_id: int):
    return _ausfuehren(lambda: aktionen.freigeben(get_store(), zeile_id, wer=session.get("user", ""),
                                                  grund=request.form.get("grund", "")),
                       "Freigegeben – geht nach der Karenz hinaus.")


@social.post("/social/<int:zeile_id>/verwerfen")
@recht_noetig("social")
def verwerfen(zeile_id: int):
    return _ausfuehren(lambda: aktionen.verwerfen(get_store(), zeile_id, wer=session.get("user", ""),
                                                  grund=request.form.get("grund", "")), "Verworfen.")


@social.post("/social/<int:zeile_id>/gepostet")
@recht_noetig("social")
def gepostet(zeile_id: int):
    return _ausfuehren(lambda: aktionen.gepostet(get_store(), zeile_id, wer=session.get("user", "")),
                       "Als gepostet markiert.")


@social.post("/social/regelwerk")
@recht_noetig("social_regelwerk")
def regelwerk_aendern():
    store = get_store()
    rw = regelwerk.aktuell(store)
    form = request.form
    aenderung: dict = {k: form.get(k) for k in regelwerk.ZAHLEN if form.get(k) not in (None, "")}
    if form.get("heikel") is not None:
        aenderung["heikel"] = [w for w in re.split(r"[,\n]", form.get("heikel", "")) if w.strip()]
    tags = {r: form.get(f"hashtags_{r}", "").split() for r in rw.rubriken if form.get(f"hashtags_{r}") is not None}
    if tags:
        aenderung["hashtags"] = tags
        aenderung["hashtags_von_kbs"] = bool(form.get("hashtags_von_kbs"))
    try:
        neu = regelwerk.speichern(store, aenderung, wer=session.get("user", ""))
    except ValueError as exc:
        flash(f"Regelwerk nicht geändert: {exc}.", "fehler")
        return _zurueck()
    flash(f"Regelwerk Fassung {neu.fassung} gespeichert. Die Freigabe durch KBS gilt für diese Fassung noch nicht.",
          "ok")
    return _zurueck()
