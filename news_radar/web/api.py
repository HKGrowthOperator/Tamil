"""Lesezugang für Auswertungen (Pilot): GET /api/bericht mit `Authorization: Bearer <RADAR_LESE_TOKEN>`.

Nur lesen, kein Login, keine Änderungen. Ohne RADAR_LESE_TOKEN gibt es den Endpunkt nicht (404). Er liefert Storys,
Quellen-Dokumente, Claims, Entwürfe, Fassungen mit Belegen, Kosten je Aufruf, Warteschlange und Budget – nie Benutzer,
Sitzungen oder Einstellungen.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from flask import Blueprint, abort, g, jsonify, request

from ..workflow import jobs, repo
from . import get_store, gleich

api = Blueprint("api", __name__)

TEXT_MAX = 8000  # Zeichen je Quellen-Dokument


def _berechtigt() -> bool:
    token = g.settings.lese_token
    if not token:
        abort(404)
    kopf = request.headers.get("Authorization", "")
    return kopf.startswith("Bearer ") and gleich(kopf[7:].strip(), token)


@api.get("/api/bericht")
def bericht():
    if not _berechtigt():
        resp = jsonify({"fehler": "nicht berechtigt"})
        resp.status_code = 401
        resp.headers["WWW-Authenticate"] = 'Bearer realm="radar"'
        return resp
    try:
        tage = min(60, max(1, int(request.args.get("tage", 7))))
    except ValueError:
        tage = 7
    from .redaktion import budget_stand

    store = get_store()
    seit = (datetime.now(timezone.utc) - timedelta(days=tage)).isoformat(timespec="seconds")
    storys = [dict(r) for r in store.db.execute(
        "SELECT * FROM stories WHERE aktualisiert >= ? OR erstellt >= ? ORDER BY id", (seit, seit))]
    for s in storys:
        sid = s["id"]
        s["dokumente"] = [{**d.model_dump(), "text": (d.text or "")[:TEXT_MAX]} for d in repo.dokumente(store, sid)]
        s["claims"] = [c.model_dump() for c in repo.claims(store, sid)]
        s["fassungen"] = [{k: f.get(k) for k in ("rolle", "von", "erstellt", "hash", "draft_id", "inhalt")}
                          for f in repo.fassungen(store, story_id=sid)]
        s["kosten"] = repo.kosten_story(store, sid)
        s["jobs"] = [dict(r) for r in store.db.execute(
            "SELECT id, schritt, status, versuche, fehler, aktualisiert FROM workflow_jobs WHERE story_id = ? ORDER BY id",
            (sid,))]
    entwuerfe = [{k: d.get(k) for k in ("id", "story_id", "status", "typ", "kategorie", "titel", "teaser", "inhalt_html",
                                         "hinweise", "quelle_name", "quelle_url", "weitere_quellen", "event_datum",
                                         "event_ort", "ticket_url", "bild_origin", "bild_credit", "relevanz", "ort",
                                         "created_at", "updated_at")}
                 for d in store.list_drafts(limit=500) if (d.get("created_at") or "") >= seit]
    return jsonify({
        "stand": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tage": tage,
        "budget": budget_stand(store),
        "warteschlange": jobs.zaehlen(store),
        "kosten": repo.kosten_bericht(store, tage=tage),
        "aufrufe": repo.usage_zeilen(store, tage=tage),
        "storys": storys,
        "entwuerfe": entwuerfe,
        "laeufe": store.recent_runs(20),
    })
