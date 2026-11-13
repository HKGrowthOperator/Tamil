"""Was die Redaktion im Cockpit mit Social-Beiträgen tut. Jede Aktion braucht eine Person, ändert nur aus dem
erwarteten Zustand (bedingtes UPDATE, kein Rennen mit dem Senden) und schreibt eine Zeile ins Protokoll.

Instagram und Facebook tragen denselben Inhalt: Stoppen, Text ändern, Freigeben und Verwerfen wirken auf beide Zeilen
eines Beitrags. WhatsApp ist ein Entwurf, den ein Mensch postet und danach als gepostet markiert.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .. import schalter
from ..store import now_iso
from . import ERLEDIGT, META_KANAELE, OFFEN, regelwerk
from .ablauf import TEXT_MAX, _iso, _protokoll

GRUND_MAX = 300
STOPPBAR = ("karenz", "geplant", "pausiert")
AENDERBAR = ("karenz", "geplant", "von_hand")
STATUS_TEXT = {
    "von_hand": "von Hand entscheiden", "karenz": "Karenz", "gestoppt": "gestoppt", "geplant": "geplant",
    "wird_gesendet": "wird gesendet", "unklar": "Ausgang unklar", "veroeffentlicht": "veröffentlicht",
    "trocken": "Trockenlauf", "pausiert": "pausiert", "verworfen": "verworfen", "entwurf": "Entwurf",
    "gepostet": "gepostet",
}


def zeile(store, zeile_id: int) -> dict | None:
    row = store.db.execute("SELECT * FROM social_beitraege WHERE id = ?", (zeile_id,)).fetchone()
    return dict(row) if row else None


def _pflicht(zeile_id: int, store) -> dict:
    z = zeile(store, zeile_id)
    if z is None:
        raise LookupError(f"Social-Beitrag {zeile_id} gibt es nicht")
    return z


def _person(wer: str) -> str:
    wer = (wer or "").strip()
    if not wer:
        raise ValueError("Person fehlt")
    return wer


def _grund(grund: str) -> str:
    grund = " ".join((grund or "").split())[:GRUND_MAX]
    if not grund:
        raise ValueError("Grund fehlt")
    return grund


def _meta_setzen(store, z: dict, aus: tuple[str, ...], **felder) -> list[dict]:
    """Beide Meta-Zeilen des Beitrags bedingt umstellen; gibt die geänderten Zeilen (vorher) zurück."""
    felder["aktualisiert"] = now_iso()
    zeilen = [dict(r) for r in store.db.execute(
        f"SELECT * FROM social_beitraege WHERE wp_post_id = ? AND kanal IN ({','.join('?' * len(META_KANAELE))}) "
        f"AND status IN ({','.join('?' * len(aus))})", (z["wp_post_id"], *META_KANAELE, *aus))]
    geaendert = []
    for r in zeilen:
        spalten = ", ".join(f"{k} = ?" for k in felder)
        cur = store._write(f"UPDATE social_beitraege SET {spalten} WHERE id = ? AND status = ?",
                           (*felder.values(), r["id"], r["status"]))
        if cur.rowcount == 1:
            geaendert.append(r)
    return geaendert


def stoppen(store, zeile_id: int, *, wer: str, grund: str) -> int:
    """Während der Karenz (oder solange geplant/pausiert) anhalten: der Beitrag geht nicht hinaus."""
    wer, grund = _person(wer), _grund(grund)
    z = _pflicht(zeile_id, store)
    geaendert = _meta_setzen(store, z, STOPPBAR, status="gestoppt", entschieden_von=wer,
                             entscheidung=f"gestoppt: {grund}")
    if not geaendert:
        raise ValueError("Nicht mehr stoppbar: der Beitrag ist schon gesendet, entschieden oder gestoppt")
    for r in geaendert:
        _protokoll(store, r, "social_gestoppt", grund, wer=wer, ausloeser="person")
    return len(geaendert)


def text_aendern(store, zeile_id: int, text: str, *, wer: str) -> int:
    wer = _person(wer)
    text = (text or "").replace("\r\n", "\n").strip()
    if not text:
        raise ValueError("Text fehlt")
    if len(text) > TEXT_MAX:
        raise ValueError(f"Text länger als {TEXT_MAX} Zeichen (Grenze von Instagram)")
    z = _pflicht(zeile_id, store)
    geaendert = _meta_setzen(store, z, AENDERBAR, text=text)
    if not geaendert:
        raise ValueError("Text nur vor dem Senden änderbar (Karenz, geplant, von Hand)")
    for r in geaendert:
        _protokoll(store, r, "social_text", "Text geändert", wer=wer, ausloeser="person")
    return len(geaendert)


def freigeben(store, zeile_id: int, *, wer: str, grund: str, jetzt: datetime | None = None) -> int:
    """„Von Hand entscheiden“ → freigeben: neue Karenz von zehn Minuten, dann wie jeder regelkonforme Beitrag."""
    wer, grund = _person(wer), _grund(grund)
    jetzt = jetzt or datetime.now(timezone.utc)
    rw = regelwerk.aktuell(store)
    z = _pflicht(zeile_id, store)
    geaendert = _meta_setzen(store, z, ("von_hand",), status="karenz",
                             karenz_bis=_iso(jetzt + timedelta(minutes=rw.karenz_min)), geplant_fuer=None,
                             entschieden_von=wer, entscheidung=f"freigegeben: {grund}", wartet_grund=None)
    if not geaendert:
        raise ValueError("Nur Beiträge unter „von Hand entscheiden“ lassen sich freigeben")
    for r in geaendert:
        _protokoll(store, r, "social_freigegeben", grund, wer=wer, ausloeser="person")
    return len(geaendert)


def verwerfen(store, zeile_id: int, *, wer: str, grund: str) -> int:
    wer, grund = _person(wer), _grund(grund)
    z = _pflicht(zeile_id, store)
    geaendert = _meta_setzen(store, z, ("von_hand",), status="verworfen", entschieden_von=wer,
                             entscheidung=f"verworfen: {grund}")
    if not geaendert:
        raise ValueError("Nur Beiträge unter „von Hand entscheiden“ lassen sich verwerfen")
    for r in geaendert:
        _protokoll(store, r, "social_verworfen", grund, wer=wer, ausloeser="person")
    return len(geaendert)


def gepostet(store, zeile_id: int, *, wer: str) -> None:
    """WhatsApp: von Hand im Kanal gepostet – Person und Zeit stehen am Beitrag und im Protokoll."""
    wer = _person(wer)
    z = _pflicht(zeile_id, store)
    if z["kanal"] != "whatsapp":
        raise ValueError("Nur WhatsApp-Entwürfe werden als gepostet markiert")
    jetzt = now_iso()
    cur = store._write("UPDATE social_beitraege SET status = 'gepostet', gepostet_von = ?, gepostet_at = ?, "
                       "aktualisiert = ? WHERE id = ? AND status = 'entwurf'", (wer, jetzt, jetzt, zeile_id))
    if cur.rowcount != 1:
        raise ValueError("Schon als gepostet markiert")
    _protokoll(store, z, "whatsapp_gepostet", f"von Hand gepostet am {jetzt}", wer=wer, ausloeser="person")


def ansicht(store, *, historie: int = 100) -> dict:
    """Daten für /social: Warteschlange, von Hand entscheiden, WhatsApp-Entwürfe, Historie."""
    import json

    def liste(sql: str, params: tuple = ()) -> list[dict]:
        out = []
        for r in store.db.execute(sql, params):
            d = dict(r)
            d["pruefung"] = json.loads(d.get("regelpruefung") or "{}")
            d["gruende"] = regelwerk.gruende(d["pruefung"])
            d["hashtags_liste"] = json.loads(d.get("hashtags") or "[]")
            d["status_text"] = STATUS_TEXT.get(d["status"], d["status"])
            out.append(d)
        return out

    marks = ",".join("?" * len(OFFEN))
    whatsapp_aus = schalter.gestoppt(store, "whatsapp")
    return {
        "warteschlange": liste(f"SELECT * FROM social_beitraege WHERE kanal != 'whatsapp' AND status IN ({marks}) "
                               "ORDER BY COALESCE(geplant_fuer, karenz_bis), id", OFFEN),
        "von_hand": liste("SELECT * FROM social_beitraege WHERE kanal != 'whatsapp' AND status = 'von_hand' "
                          "ORDER BY id DESC"),
        "whatsapp": [] if whatsapp_aus else liste(
            "SELECT * FROM social_beitraege WHERE kanal = 'whatsapp' AND status = 'entwurf' ORDER BY id DESC LIMIT 50"),
        "whatsapp_aus": whatsapp_aus,
        "historie": liste("SELECT * FROM social_beitraege WHERE status NOT IN ('entwurf', 'von_hand') AND "
                          f"status NOT IN ({marks}) ORDER BY aktualisiert DESC, id DESC LIMIT ?", (*OFFEN, historie)),
        "erledigt": ERLEDIGT,
    }
