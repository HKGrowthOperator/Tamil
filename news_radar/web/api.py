"""Lesezugang für Auswertungen (Pilot): GET /api/bericht mit `Authorization: Bearer <RADAR_LESE_TOKEN>`.
Agent-Modus übers Netz: GET /api/agent/export und POST /api/agent/import mit `Bearer <RADAR_AGENT_TOKEN>` – dieselbe
Aufgabenmappe und derselbe Import wie `agent export/import --v2`, mit allen Gates. POST /api/agent/vorschlag nimmt
Nachtrag-Vorschläge mit Quellen an (`nachtrag.annehmen`, kein Modell); POST /api/agent/bild setzt ein Bild mit
Nachweis an einem wartenden Entwurf (`bildvorschlag.annehmen`, kein Modell).

Nur lesen, kein Login, keine Änderungen. Ohne RADAR_LESE_TOKEN gibt es den Endpunkt nicht (404). Er liefert Storys,
Quellen-Dokumente, Claims, Entwürfe, Fassungen mit Belegen, Kosten je Aufruf, Warteschlange und Budget – nie Benutzer,
Sitzungen oder Einstellungen.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from flask import Blueprint, abort, g, jsonify, request

from .. import schalter
from ..workflow import jobs, repo
from . import get_store, gleich

api = Blueprint("api", __name__)

TEXT_MAX = 8000  # Zeichen je Quellen-Dokument


def _berechtigt(token: str | None = None) -> bool:
    token = g.settings.lese_token if token is None else token
    if not token:
        abort(404)
    kopf = request.headers.get("Authorization", "")
    return kopf.startswith("Bearer ") and gleich(kopf[7:].strip(), token)


def _angehalten(exc: schalter.Gestoppt):
    """409: Der Schalter hält die Redaktion an – nichts abgerufen, nichts angelegt."""
    resp = jsonify({"fehler": str(exc), "kanal": exc.sperre["kanal"], "seit": exc.sperre["seit"]})
    resp.status_code = 409
    return resp


def _abgewiesen():
    resp = jsonify({"fehler": "nicht berechtigt"})
    resp.status_code = 401
    resp.headers["WWW-Authenticate"] = 'Bearer realm="radar"'
    return resp


@api.get("/api/agent/export")
def agent_export():
    if not _berechtigt(g.settings.agent_token):
        return _abgewiesen()
    from ..agent_v2 import paket_v2

    try:
        limit = min(20, max(1, int(request.args.get("limit", 5))))
    except ValueError:
        limit = 5
    try:
        return jsonify(paket_v2(get_store(), g.settings, limit=limit))
    except schalter.Gestoppt as exc:
        return _angehalten(exc)


@api.post("/api/agent/import")
def agent_import():
    if not _berechtigt(g.settings.agent_token):
        return _abgewiesen()
    from ..agent_v2 import import_daten

    raw = request.get_json(silent=True)
    if raw is None:
        return jsonify({"fehler": "JSON erwartet"}), 400
    von = str(request.args.get("von") or "claude-code")[:60]
    try:
        stats = import_daten(get_store(), g.settings, raw, von=von)
    except schalter.Gestoppt as exc:
        return _angehalten(exc)
    except ValueError as exc:
        return jsonify({"fehler": str(exc)}), 400
    get_store().event("agent_api", von=von, **{k: v for k, v in stats.items() if k != "fehler"},
                      fehler=len(stats["fehler"]))
    return jsonify(stats)


@api.post("/api/agent/vorschlag")
def agent_vorschlag():
    """Nachtrag: Vorschläge mit Quellen annehmen – der Radar holt die Quellen selbst, legt Storys an, kein Modell."""
    if not _berechtigt(g.settings.agent_token):
        return _abgewiesen()
    from ..nachtrag import annehmen

    raw = request.get_json(silent=True)
    if raw is None:
        return jsonify({"fehler": "JSON erwartet"}), 400
    von = str(request.args.get("von") or "claude-code")[:60]
    from ..nachtrag import WEB_FRIST_GESAMT, WEB_MAX_VORSCHLAEGE

    try:
        out = annehmen(get_store(), g.settings, raw, von=von, max_vorschlaege=WEB_MAX_VORSCHLAEGE,
                       frist_gesamt=WEB_FRIST_GESAMT)
    except schalter.Gestoppt as exc:
        return _angehalten(exc)
    except ValueError as exc:
        return jsonify({"fehler": str(exc)}), 400
    get_store().event("agent_api_vorschlag", von=von, **{k: v for k, v in out.items() if isinstance(v, int)})
    if out.get("angehalten"):  # mitten im Stapel angehalten: 409, mit den bis dahin erzielten Ergebnissen
        return jsonify({"fehler": "Redaktion angehalten", **out["angehalten"], **out}), 409
    return jsonify(out)


@api.post("/api/agent/bild")
def agent_bild():
    """Bild mit Nachweis: der Radar prüft Herkunft und Rechte selbst, holt das Bild und setzt es am wartenden Entwurf."""
    if not _berechtigt(g.settings.agent_token):
        return _abgewiesen()
    from ..bildvorschlag import WEB_FRIST_GESAMT, WEB_MAX_BILDER, annehmen

    raw = request.get_json(silent=True)
    if raw is None:
        return jsonify({"fehler": "JSON erwartet"}), 400
    von = str(request.args.get("von") or "claude-code")
    try:
        out = annehmen(get_store(), g.settings, raw, von=von, max_bilder=WEB_MAX_BILDER, frist_gesamt=WEB_FRIST_GESAMT)
    except schalter.Gestoppt as exc:
        return _angehalten(exc)
    except ValueError as exc:
        return jsonify({"fehler": str(exc)}), 400
    get_store().event("agent_api_bild", von=von, **{k: v for k, v in out.items() if isinstance(v, int)})
    if out.get("angehalten"):  # mitten im Stapel angehalten: 409, mit den bis dahin erzielten Ergebnissen
        return jsonify({"fehler": "Redaktion angehalten", **out["angehalten"], **out}), 409
    return jsonify(out)


@api.get("/api/bericht")
def bericht():
    if not _berechtigt():
        return _abgewiesen()
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
        "gestoppt": [{"kanal": z["kanal"], "seit": z["seit"]} for z in schalter.aktive(store)],
    })
