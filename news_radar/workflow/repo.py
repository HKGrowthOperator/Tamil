"""Datenbank-Zugriffe der Redaktion v2: Storys, Dokumente, Claims, Fassungen, Bildrechte, Aktionen, Kosten, Benutzer.

Alle Funktionen nehmen den Store (eine SQLite-Verbindung je Komponente) und schreiben über store._write bzw.
unter store.lock, damit Worker-Threads sich nicht in die Quere kommen.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

from ..sources import normalize_url
from ..store import now_iso
from .models import Claim, SourceDocument

STORY_STATUS = ("neu", "recherche", "geprueft", "geschrieben", "geprueft_text", "fertig", "recherche_erforderlich",
                "verworfen", "fehler", "zurueckgestellt")
FASSUNG_FELDER = ("titel", "teaser", "inhalt_html", "seo_titel", "meta_beschreibung", "schlagworte", "bild_datei",
                  "bild_alt", "event_datum", "event_ort", "ticket_url", "kategorie")


def _rows(cursor) -> list[dict]:
    return [dict(r) for r in cursor]


# ---- Storys -------------------------------------------------------------------------------------

def story_anlegen(store, *, typ: str, titel: str, kategorie: str = "", ort: str = "", region: str = "",
                  schluessel: str = "", prioritaet: int = 0, relevanz: int | None = None, begruendung: str = "",
                  status: str = "neu", laenge: str = "normal", sensibel: bool = False) -> int:
    ts = now_iso()
    cur = store._write(
        "INSERT INTO stories (typ, status, titel, kategorie, ort, region, sensibel, schluessel, prioritaet, laenge, "
        "relevanz, begruendung, erstellt, aktualisiert) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (typ, status, titel, kategorie, ort, region, 1 if sensibel else 0, schluessel, prioritaet, laenge, relevanz,
         begruendung, ts, ts),
    )
    return cur.lastrowid


def story(store, story_id: int) -> dict | None:
    row = store.db.execute("SELECT * FROM stories WHERE id = ?", (story_id,)).fetchone()
    return dict(row) if row else None


def story_setzen(store, story_id: int, **felder) -> None:
    erlaubt = {"status", "titel", "kategorie", "ort", "region", "sensibel", "schluessel", "prioritaet", "laenge",
               "relevanz", "begruendung", "notiz", "typ"}
    data = {k: v for k, v in felder.items() if k in erlaubt}
    if "sensibel" in data:
        data["sensibel"] = 1 if data["sensibel"] else 0
    data["aktualisiert"] = now_iso()
    sets = ", ".join(f"{k} = ?" for k in data)
    store._write(f"UPDATE stories SET {sets} WHERE id = ?", (*data.values(), story_id))


def stories(store, status: str | Iterable[str] | None = None, limit: int = 100) -> list[dict]:
    if status is None:
        return _rows(store.db.execute("SELECT * FROM stories ORDER BY aktualisiert DESC LIMIT ?", (limit,)))
    statuses = [status] if isinstance(status, str) else list(status)
    marks = ",".join("?" for _ in statuses)
    return _rows(store.db.execute(
        f"SELECT * FROM stories WHERE status IN ({marks}) ORDER BY aktualisiert DESC LIMIT ?", (*statuses, limit)))


def stories_seit(store, tage: int = 7, typen: Iterable[str] | None = None) -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(days=tage)).isoformat(timespec="seconds")
    sql, params = "SELECT * FROM stories WHERE erstellt >= ?", [since]
    if typen:
        typen = list(typen)
        sql += f" AND typ IN ({','.join('?' for _ in typen)})"
        params += typen
    return _rows(store.db.execute(sql + " ORDER BY id DESC", params))


def bezahlte_storys_heute(store, seit_iso: str) -> int:
    """Storys, die heute den bezahlten Weg gegangen sind (alles außer Kino, das ohne Modell läuft)."""
    return store.db.execute(
        "SELECT COUNT(*) FROM stories WHERE erstellt >= ? AND typ != 'kino' AND status != 'verworfen'", (seit_iso,)
    ).fetchone()[0]


def story_zu(store, *, url: str = "", uid: str = "", schluessel: str = "") -> int | None:
    """Story, zu der diese URL, UID oder dieser Schlüssel schon gehört."""
    if uid:
        row = store.db.execute("SELECT story_id FROM source_documents WHERE uid = ? LIMIT 1", (uid,)).fetchone()
        if row:
            return row[0]
    if url:
        row = store.db.execute("SELECT story_id FROM source_documents WHERE url_norm = ? LIMIT 1",
                               (normalize_url(url),)).fetchone()
        if row:
            return row[0]
    if schluessel:
        row = store.db.execute("SELECT id FROM stories WHERE schluessel = ? ORDER BY id DESC LIMIT 1",
                               (schluessel,)).fetchone()
        if row:
            return row[0]
    return None


# ---- Dokumente ----------------------------------------------------------------------------------

def dokument_hinzufuegen(store, story_id: int, *, url: str = "", uid: str = "", publisher: str = "", quelle: str = "",
                         published_at: str = "", language: str = "de", rights: str = "unbekannt", primaer: bool = False,
                         art: str = "zusammenfassung", titel: str = "", text: str = "") -> str | None:
    """Neues Dokument zur Story; None, wenn die URL schon dabei ist. Gibt den doc_key (Q1, Q2 …) zurück."""
    if url:
        # normalize_url wirft das Fragment weg; „…#daten“ (strukturierte Angaben derselben Seite) ist ein eigenes Dokument
        fragment = url.split("#", 1)[1] if "#" in url else ""
        url_norm = normalize_url(url) + (f"#{fragment}" if fragment else "")
    else:
        url_norm = f"text:{hashlib.sha256((titel + text).encode()).hexdigest()[:16]}"
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest() if text else ""
    with store.lock:
        if store.db.execute("SELECT 1 FROM source_documents WHERE story_id = ? AND url_norm = ?",
                            (story_id, url_norm)).fetchone():
            return None
        n = store.db.execute("SELECT COUNT(*) FROM source_documents WHERE story_id = ?", (story_id,)).fetchone()[0]
        key = f"Q{n + 1}"
        store.db.execute(
            "INSERT INTO source_documents (story_id, doc_key, url, url_norm, uid, publisher, quelle, published_at, "
            "retrieved_at, language, rights, primaer, art, titel, text, text_sha256, auszug) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (story_id, key, url, url_norm, uid, publisher, quelle, published_at, now_iso(), language, rights,
             1 if primaer else 0, art, titel, text, sha, text[:500]),
        )
        store.db.commit()
    return key


def dokument_setzen(store, story_id: int, doc_key: str, **felder) -> None:
    erlaubt = {"text", "art", "rights", "primaer", "publisher", "titel"}
    data = {k: v for k, v in felder.items() if k in erlaubt}
    if "text" in data:
        data["text_sha256"] = hashlib.sha256(data["text"].encode("utf-8")).hexdigest() if data["text"] else ""
        data["auszug"] = data["text"][:500]
    if "primaer" in data:
        data["primaer"] = 1 if data["primaer"] else 0
    sets = ", ".join(f"{k} = ?" for k in data)
    store._write(f"UPDATE source_documents SET {sets} WHERE story_id = ? AND doc_key = ?", (*data.values(), story_id, doc_key))


def dokumente(store, story_id: int) -> list[SourceDocument]:
    out = []
    for r in store.db.execute("SELECT * FROM source_documents WHERE story_id = ? ORDER BY id", (story_id,)):
        out.append(SourceDocument(
            doc_key=r["doc_key"], url=r["url"] or "", publisher=r["publisher"] or "", quelle=r["quelle"] or "",
            published_at=r["published_at"] or "", retrieved_at=r["retrieved_at"] or "", language=r["language"] or "de",
            rights=r["rights"] or "unbekannt", primaer=bool(r["primaer"]), art=r["art"] or "zusammenfassung",
            titel=r["titel"] or "", text=r["text"] or "",
        ))
    return out


# ---- Claims -------------------------------------------------------------------------------------

def claims_setzen(store, story_id: int, claims: list[Claim]) -> None:
    ts = now_iso()
    with store.lock:
        store.db.execute("DELETE FROM claims WHERE story_id = ?", (story_id,))
        store.db.executemany(
            "INSERT INTO claims (story_id, claim_key, aussage, art, kern, quellen, support, confidence, fundstelle, erstellt) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            [(story_id, c.id, c.aussage, c.art, 1 if c.kern else 0, json.dumps(c.quellen), c.support, c.sicherheit,
              c.fundstelle, ts) for c in claims],
        )
        store.db.commit()


def claims(store, story_id: int) -> list[Claim]:
    out = []
    for r in store.db.execute("SELECT * FROM claims WHERE story_id = ? ORDER BY id", (story_id,)):
        out.append(Claim(id=r["claim_key"], aussage=r["aussage"], art=r["art"] or "sonstiges", kern=bool(r["kern"]),
                         quellen=json.loads(r["quellen"] or "[]"), fundstelle=r["fundstelle"] or "",
                         sicherheit=r["confidence"] if r["confidence"] is not None else 0.5,
                         support=r["support"] or "offen"))
    return out


# ---- Fassungen ----------------------------------------------------------------------------------

def fassung_hash(felder: dict) -> str:
    kern = {k: felder.get(k) for k in FASSUNG_FELDER}
    return hashlib.sha256(json.dumps(kern, ensure_ascii=False, sort_keys=True, default=str).encode()).hexdigest()[:16]


def fassung_speichern(store, story_id: int | None, rolle: str, felder: dict, *, von: str = "",
                      draft_id: int | None = None) -> str:
    h = fassung_hash(felder)
    store._write(
        "INSERT INTO article_versions (story_id, draft_id, rolle, von, hash, inhalt, erstellt) VALUES (?,?,?,?,?,?,?)",
        (story_id, draft_id, rolle, von, h, json.dumps(felder, ensure_ascii=False, default=str), now_iso()),
    )
    return h


def fassungen(store, *, story_id: int | None = None, draft_id: int | None = None) -> list[dict]:
    if story_id is not None and draft_id is not None:
        rows = store.db.execute("SELECT * FROM article_versions WHERE story_id = ? OR draft_id = ? ORDER BY id",
                                (story_id, draft_id))
    elif story_id is not None:
        rows = store.db.execute("SELECT * FROM article_versions WHERE story_id = ? ORDER BY id", (story_id,))
    else:
        rows = store.db.execute("SELECT * FROM article_versions WHERE draft_id = ? ORDER BY id", (draft_id,))
    out = []
    for r in rows:
        d = dict(r)
        d["inhalt"] = json.loads(d["inhalt"] or "{}")
        out.append(d)
    return out


# ---- Bildrechte ---------------------------------------------------------------------------------

def asset_anlegen(store, *, datei: str, herkunft: str, rechteinhaber: str = "", lizenz: str = "", umfang: str = "",
                  attribution: str = "", ablauf: str = "", quelle_url: str = "", ki: bool = False,
                  story_id: int | None = None, draft_id: int | None = None, daten: bytes | None = None) -> int:
    sha = hashlib.sha256(daten).hexdigest() if daten else ""
    cur = store._write(
        "INSERT INTO assets (datei, sha256, herkunft, rechteinhaber, lizenz, umfang, attribution, ablauf, quelle_url, ki, "
        "story_id, draft_id, erstellt) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (datei, sha, herkunft, rechteinhaber, lizenz, umfang, attribution, ablauf, quelle_url, 1 if ki else 0,
         story_id, draft_id, now_iso()),
    )
    return cur.lastrowid


def asset_draft_setzen(store, asset_id: int, draft_id: int) -> None:
    store._write("UPDATE assets SET draft_id = ? WHERE id = ?", (draft_id, asset_id))


def asset_fuer_datei(store, datei: str) -> dict | None:
    row = store.db.execute("SELECT * FROM assets WHERE datei = ? ORDER BY id DESC LIMIT 1", (datei,)).fetchone()
    return dict(row) if row else None


# ---- Redaktionelle Aktionen (wer hat welche Fassung freigegeben) ---------------------------------

def aktion(store, *, wer: str, aktion: str, draft_id: int | None = None, story_id: int | None = None,
           fassung: str = "", wp_post_id: int | None = None, notiz: str = "") -> None:
    store._write(
        "INSERT INTO editorial_actions (ts, wer, aktion, draft_id, story_id, fassung_hash, wp_post_id, notiz) "
        "VALUES (?,?,?,?,?,?,?,?)", (now_iso(), wer, aktion, draft_id, story_id, fassung, wp_post_id, notiz[:300]),
    )


def aktionen(store, draft_id: int) -> list[dict]:
    return _rows(store.db.execute("SELECT * FROM editorial_actions WHERE draft_id = ? ORDER BY id", (draft_id,)))


# ---- Kosten -------------------------------------------------------------------------------------

def kosten_story(store, story_id: int) -> dict:
    row = store.db.execute(
        "SELECT COALESCE(SUM(kosten_usd), 0) AS usd, COUNT(*) AS aufrufe, "
        "SUM(CASE WHEN status != 'ok' THEN 1 ELSE 0 END) AS fehlversuche FROM agent_usage WHERE story_id = ?",
        (story_id,)).fetchone()
    je_rolle = _rows(store.db.execute(
        "SELECT rolle, modell, COUNT(*) AS aufrufe, SUM(kosten_usd) AS usd, SUM(input_tokens) AS input, "
        "SUM(output_tokens) AS output FROM agent_usage WHERE story_id = ? GROUP BY rolle, modell ORDER BY usd DESC",
        (story_id,)))
    return {"usd": round(row["usd"], 4), "aufrufe": row["aufrufe"], "fehlversuche": row["fehlversuche"] or 0,
            "je_rolle": je_rolle}


def kosten_bericht(store, tage: int = 30) -> dict:
    since = (datetime.now(timezone.utc) - timedelta(days=tage)).isoformat(timespec="seconds")

    def gruppe(spalten: str) -> list[dict]:
        return _rows(store.db.execute(
            f"SELECT {spalten}, COUNT(*) AS aufrufe, ROUND(SUM(kosten_usd), 4) AS usd, SUM(input_tokens) AS input, "
            f"SUM(output_tokens) AS output, SUM(cache_read) AS cache_read, SUM(bilder) AS bilder, "
            f"SUM(CASE WHEN status != 'ok' THEN 1 ELSE 0 END) AS fehlversuche "
            f"FROM agent_usage WHERE ts >= ? GROUP BY {spalten} ORDER BY usd DESC", (since,)))

    je_tag = _rows(store.db.execute(
        "SELECT substr(ts, 1, 10) AS tag, COUNT(*) AS aufrufe, ROUND(SUM(kosten_usd), 4) AS usd FROM agent_usage "
        "WHERE ts >= ? GROUP BY tag ORDER BY tag DESC", (since,)))
    gesamt = store.db.execute("SELECT COALESCE(SUM(kosten_usd), 0) FROM agent_usage WHERE ts >= ?", (since,)).fetchone()[0]
    entwuerfe = store.db.execute(
        "SELECT COUNT(*) FROM drafts WHERE story_id IS NOT NULL AND created_at >= ?", (since,)).fetchone()[0]
    return {"tage": tage, "gesamt_usd": round(gesamt, 4), "entwuerfe": entwuerfe,
            "je_entwurf_usd": round(gesamt / entwuerfe, 4) if entwuerfe else None,
            "je_rolle": gruppe("rolle"), "je_modell": gruppe("modell"), "je_tag": je_tag,
            "fehler": _rows(store.db.execute(
                "SELECT ts, rolle, modell_angefragt, status, fehler, story_id FROM agent_usage "
                "WHERE ts >= ? AND status != 'ok' ORDER BY id DESC LIMIT 50", (since,)))}


def usage_zeilen(store, tage: int = 31) -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(days=tage)).isoformat(timespec="seconds")
    return _rows(store.db.execute("SELECT * FROM agent_usage WHERE ts >= ? ORDER BY id", (since,)))


# ---- Benutzer -----------------------------------------------------------------------------------

ROLLEN = ("redaktion", "admin")


def nutzer_anlegen(store, name: str, passwort: str, rolle: str = "redaktion") -> None:
    from werkzeug.security import generate_password_hash

    if rolle not in ROLLEN:
        raise ValueError(f"Rolle muss {' oder '.join(ROLLEN)} sein")
    if len(passwort) < 10:
        raise ValueError("Passwort: mindestens 10 Zeichen")
    store._write(
        "INSERT INTO users (name, passwort_hash, rolle, aktiv, erstellt) VALUES (?,?,?,1,?) "
        "ON CONFLICT(name) DO UPDATE SET passwort_hash = excluded.passwort_hash, rolle = excluded.rolle, aktiv = 1",
        (name, generate_password_hash(passwort), rolle, now_iso()),
    )


def nutzer_sperren(store, name: str) -> bool:
    return store._write("UPDATE users SET aktiv = 0 WHERE name = ?", (name,)).rowcount == 1


def nutzer_pruefen(store, name: str, passwort: str) -> dict | None:
    from werkzeug.security import check_password_hash

    row = store.db.execute("SELECT * FROM users WHERE name = ? AND aktiv = 1", (name,)).fetchone()
    if row is None or not check_password_hash(row["passwort_hash"], passwort):
        return None
    store._write("UPDATE users SET letzter_login = ? WHERE name = ?", (now_iso(), name))
    return {"name": row["name"], "rolle": row["rolle"]}


def nutzer_liste(store) -> list[dict]:
    return _rows(store.db.execute("SELECT name, rolle, aktiv, erstellt, letzter_login FROM users ORDER BY name"))


def nutzer_anzahl(store) -> int:
    return store.db.execute("SELECT COUNT(*) FROM users WHERE aktiv = 1").fetchone()[0]


def json_feld(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def wochenbericht(store, tage: int = 7) -> dict:
    """Annahmequote, Fehler und Kosten je Artikel: die Kennzahlen des Pilotbetriebs."""
    since = (datetime.now(timezone.utc) - timedelta(days=tage)).isoformat(timespec="seconds")
    q = store.db.execute
    entwuerfe = q("SELECT COUNT(*) FROM drafts WHERE created_at >= ?", (since,)).fetchone()[0]
    angenommen = q("SELECT COUNT(*) FROM drafts WHERE created_at >= ? AND status IN "
                   "('freigegeben', 'wird_veroeffentlicht', 'veroeffentlicht', 'in_wordpress')", (since,)).fetchone()[0]
    abgelehnt = q("SELECT COUNT(*) FROM drafts WHERE created_at >= ? AND status = 'abgelehnt'", (since,)).fetchone()[0]
    storys = {r[0]: r[1] for r in q("SELECT status, COUNT(*) FROM stories WHERE erstellt >= ? GROUP BY status", (since,))}
    kosten = kosten_bericht(store, tage)
    tote = q("SELECT COUNT(*) FROM workflow_jobs WHERE status = 'tot' AND aktualisiert >= ?", (since,)).fetchone()[0]
    fehlversuche = q("SELECT COUNT(*) FROM agent_usage WHERE ts >= ? AND status != 'ok'", (since,)).fetchone()[0]
    entschieden = angenommen + abgelehnt
    return {
        "tage": tage, "entwuerfe": entwuerfe, "angenommen": angenommen, "abgelehnt": abgelehnt,
        "annahmequote": round(angenommen / entschieden, 2) if entschieden else None,
        "storys": storys, "recherche_noetig": storys.get("recherche_erforderlich", 0),
        "kosten_usd": kosten["gesamt_usd"], "kosten_je_entwurf": kosten["je_entwurf_usd"],
        "jobs_abgebrochen": tote, "fehlversuche": fehlversuche,
    }


def wochenbericht_text(store, tage: int = 7) -> str:
    b = wochenbericht(store, tage)
    quote = f"{b['annahmequote']:.0%}" if b["annahmequote"] is not None else "–"
    je = f"${b['kosten_je_entwurf']:.3f}" if b["kosten_je_entwurf"] else "–"
    return (f"Radar – letzte {tage} Tage: {b['entwuerfe']} Entwürfe, {b['angenommen']} angenommen, {b['abgelehnt']} "
            f"abgelehnt (Annahmequote {quote}); {b['recherche_noetig']} Storys „Recherche nötig“; Kosten "
            f"${b['kosten_usd']:.2f} ({je} je Entwurf); {b['jobs_abgebrochen']} abgebrochene Jobs, "
            f"{b['fehlversuche']} Fehlversuche bei Modellaufrufen.")
