"""SQLite-Speicher: Warteschlange der Entwürfe, gesehene Meldungen, Läufe, Quellen-Status, Protokoll.

Der Timer-Lauf und die Freigabe-App greifen gleichzeitig zu: WAL-Modus + busy_timeout machen das
sicher, jede Komponente öffnet ihre eigene Verbindung (die App eine pro Request).
"""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

# Lebenszyklus eines Entwurfs (Vertrag B.2.2: Freigeben, Ablehnen, Bearbeiten, Zurückstellen)
OPEN_STATES = frozenset({"neu", "bearbeitet", "zurueckgestellt"})
STATUSES = ("neu", "bearbeitet", "zurueckgestellt", "freigegeben", "wird_veroeffentlicht",
            "veroeffentlicht", "in_wordpress", "abgelehnt", "fehler")
TRANSITIONS: dict[str, tuple[frozenset[str], str]] = {
    "bearbeiten": (frozenset({"neu", "bearbeitet", "zurueckgestellt"}), "bearbeitet"),
    "freigeben": (frozenset({"neu", "bearbeitet", "zurueckgestellt", "fehler"}), "freigegeben"),
    "zurueckstellen": (frozenset({"neu", "bearbeitet", "freigegeben"}), "zurueckgestellt"),
    "ablehnen": (frozenset({"neu", "bearbeitet", "zurueckgestellt", "freigegeben", "fehler"}), "abgelehnt"),
    "wiederherstellen": (frozenset({"abgelehnt"}), "neu"),
    "erneut": (frozenset({"fehler"}), "freigegeben"),
}
# Zustände, aus denen „Direkt posten“ erlaubt ist (die Freigabe passiert implizit)
PUBLISHABLE = frozenset({"neu", "bearbeitet", "zurueckgestellt", "freigegeben", "fehler"})

JSON_COLUMNS = ("schlagworte", "weitere_quellen", "fakten_json", "hinweise")
DRAFT_COLUMNS = (
    "uid", "typ", "status", "quelle_name", "quelle_url", "quelle_datum", "quelle_sprache", "weitere_quellen",
    "quelle_bild", "relevanz", "begruendung", "dach_bezug", "ort", "kategorie", "titel", "teaser", "inhalt_html",
    "schlagworte", "seo_titel", "meta_beschreibung", "bild_datei", "bild_credit", "bild_alt",
    "bild_suchbegriff", "bild_origin", "event_datum", "event_ort", "ticket_url", "fakten_json",
    "fingerprint", "hinweise", "original_json", "rewrite_count", "wp_post_id", "wp_link", "fehler",
    "bearbeitet_von", "freigegeben_at", "veroeffentlicht_at",
)
# Spalten, die nach der ersten Version dazukamen (ALTER TABLE für bestehende Datenbanken)
ADDED_COLUMNS = (("quelle_bild", "TEXT"),)
# Nicht in den Prototyp-Export (intern bzw. WordPress-spezifisch)
EXPORT_SKIP = ("original_json", "fingerprint", "fakten_json", "wp_post_id", "wp_link", "bearbeitet_von", "fehler")

SCHEMA = """
CREATE TABLE IF NOT EXISTS seen (
    uid TEXT PRIMARY KEY, title TEXT, url TEXT, source TEXT, status TEXT, created_at TEXT
);
CREATE TABLE IF NOT EXISTS log (
    id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, event TEXT, data TEXT
);
CREATE TABLE IF NOT EXISTS drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid TEXT NOT NULL UNIQUE,
    typ TEXT NOT NULL DEFAULT 'artikel',
    status TEXT NOT NULL DEFAULT 'neu',
    quelle_name TEXT, quelle_url TEXT, quelle_datum TEXT, quelle_sprache TEXT, weitere_quellen TEXT,
    quelle_bild TEXT,
    relevanz INTEGER, begruendung TEXT, dach_bezug INTEGER NOT NULL DEFAULT 0, ort TEXT,
    kategorie TEXT, titel TEXT, teaser TEXT, inhalt_html TEXT, schlagworte TEXT,
    seo_titel TEXT, meta_beschreibung TEXT,
    bild_datei TEXT, bild_credit TEXT, bild_alt TEXT, bild_suchbegriff TEXT, bild_origin TEXT,
    event_datum TEXT, event_ort TEXT, ticket_url TEXT,
    fakten_json TEXT, fingerprint TEXT, hinweise TEXT,
    original_json TEXT NOT NULL DEFAULT '{}',
    rewrite_count INTEGER NOT NULL DEFAULT 0,
    wp_post_id INTEGER, wp_link TEXT, fehler TEXT,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
    bearbeitet_von TEXT, freigegeben_at TEXT, veroeffentlicht_at TEXT
);
CREATE INDEX IF NOT EXISTS drafts_status ON drafts(status, created_at DESC);
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, started_at TEXT NOT NULL, finished_at TEXT,
    modus TEXT, gesammelt INTEGER, relevant INTEGER, entwuerfe INTEGER, verworfen INTEGER,
    veroeffentlicht INTEGER, fehler INTEGER, notiz TEXT
);
CREATE TABLE IF NOT EXISTS source_status (
    name TEXT PRIMARY KEY, last_ok TEXT, last_error TEXT, last_count INTEGER, error_msg TEXT, paused_until TEXT
);
"""


class ConflictError(Exception):
    """Der Entwurf wurde zwischenzeitlich von jemand anderem verändert."""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def _loads(value: Any, default: Any) -> Any:
    if value in (None, ""):
        return default
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return default


def row_to_draft(row: sqlite3.Row | None) -> dict | None:
    """DB-Zeile → dict mit geparsten JSON-Spalten."""
    if row is None:
        return None
    d = dict(row)
    d["schlagworte"] = _loads(d.get("schlagworte"), [])
    d["weitere_quellen"] = _loads(d.get("weitere_quellen"), [])
    d["fakten"] = _loads(d.get("fakten_json"), {})
    d["hinweise"] = _loads(d.get("hinweise"), [])
    d["dach_bezug"] = bool(d.get("dach_bezug"))
    return d


class Store:
    def __init__(self, path: Path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.db = sqlite3.connect(path, check_same_thread=False, timeout=5)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.execute("PRAGMA synchronous=NORMAL")
        self.lock = threading.Lock()  # Schreibzugriffe aus mehreren Threads eines Prozesses
        self.migrate()

    def migrate(self) -> None:
        self.db.executescript(SCHEMA)
        present = {row[1] for row in self.db.execute("PRAGMA table_info(drafts)")}
        for column, ddl in ADDED_COLUMNS:
            if column not in present:
                self.db.execute(f"ALTER TABLE drafts ADD COLUMN {column} {ddl}")
        self.db.commit()

    def close(self) -> None:
        self.db.close()

    def __enter__(self) -> "Store":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # ---- Schreib-Helfer -------------------------------------------------
    def _write(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        with self.lock:
            cur = self.db.execute(sql, params)
            self.db.commit()
            return cur

    # ---- gesehene Meldungen ----------------------------------------------
    def seen_uids(self) -> set[str]:
        return {row[0] for row in self.db.execute("SELECT uid FROM seen")}

    def recent_titles(self, days: int = 3) -> list[str]:
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        return [r[0] for r in self.db.execute("SELECT title FROM seen WHERE created_at >= ?", (since,))]

    def mark(self, uid: str, title: str, url: str, source: str, status: str) -> None:
        self._write(
            "INSERT OR REPLACE INTO seen VALUES (?,?,?,?,?,?)",
            (uid, title, url, source, status, now_iso()),
        )

    # ---- Protokoll (Vertrag B.3.4) ---------------------------------------
    def event(self, event: str, **data) -> None:
        self._write("INSERT INTO log (ts, event, data) VALUES (?,?,?)", (now_iso(), event, _dumps(data)))

    def iter_log(self, event: str | None = None, limit: int | None = None, since: str | None = None) -> Iterator[dict]:
        sql, params = "SELECT id, ts, event, data FROM log", []
        where = []
        if event:
            where.append("event = ?")
            params.append(event)
        if since:
            where.append("ts >= ?")
            params.append(since)
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY id DESC"
        if limit:
            sql += f" LIMIT {int(limit)}"
        for row in self.db.execute(sql, params):
            yield {"id": row["id"], "ts": row["ts"], "event": row["event"], **_loads(row["data"], {})}

    def export_log(self, path: Path) -> int:
        rows = list(self.iter_log())
        rows.reverse()
        path.write_text("\n".join(_dumps(r) for r in rows), encoding="utf-8")
        return len(rows)

    EXPORT_STATES = ("neu", "bearbeitet", "zurueckgestellt", "freigegeben", "veroeffentlicht", "in_wordpress")

    def export_drafts(self, statuses: tuple[str, ...] = EXPORT_STATES, limit: int = 60) -> dict:
        """Entwürfe samt letztem Lauf und Quellen-Status als JSON-taugliches dict (für den Prototyp)."""
        marks = ",".join("?" for _ in statuses)
        rows = self.db.execute(
            f"SELECT * FROM drafts WHERE status IN ({marks}) ORDER BY quelle_datum DESC, id DESC LIMIT ?",
            (*statuses, limit),
        )
        entwuerfe = []
        for row in rows:
            d = row_to_draft(row)
            for key in EXPORT_SKIP:
                d.pop(key, None)
            entwuerfe.append(d)
        runs = self.recent_runs(1)
        return {
            "stand": now_iso(),
            "lauf": runs[0] if runs else None,
            "quellen": [{"name": s["name"], "last_ok": s["last_ok"], "last_count": s["last_count"]} for s in self.source_status_all()],
            "entwuerfe": entwuerfe,
        }

    # ---- Entwürfe ----------------------------------------------------------
    def insert_draft(self, row: dict) -> int | None:
        """Legt einen Entwurf an. Gibt None zurück, wenn es zu dieser uid schon einen gibt."""
        data = {k: row.get(k) for k in DRAFT_COLUMNS if k in row}
        for col in JSON_COLUMNS:
            if col in data and not isinstance(data[col], (str, type(None))):
                data[col] = _dumps(data[col])
        if "fakten" in row and "fakten_json" not in row:
            data["fakten_json"] = _dumps(row["fakten"])
        if isinstance(data.get("original_json"), dict):
            data["original_json"] = _dumps(data["original_json"])
        data.setdefault("status", "neu")
        data.setdefault("typ", "artikel")
        data["dach_bezug"] = 1 if row.get("dach_bezug") else 0
        ts = now_iso()
        data["created_at"] = ts
        data["updated_at"] = ts
        cols = ", ".join(data)
        marks = ", ".join("?" for _ in data)
        cur = self._write(f"INSERT OR IGNORE INTO drafts ({cols}) VALUES ({marks})", tuple(data.values()))
        return cur.lastrowid if cur.rowcount == 1 else None

    def get_draft(self, draft_id: int) -> dict | None:
        return row_to_draft(self.db.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,)).fetchone())

    def draft_by_uid(self, uid: str) -> dict | None:
        return row_to_draft(self.db.execute("SELECT * FROM drafts WHERE uid = ?", (uid,)).fetchone())

    def list_drafts(self, status: str | None = None, limit: int = 100, offset: int = 0) -> list[dict]:
        order = "dach_bezug DESC, relevanz DESC, created_at DESC" if status == "neu" else "updated_at DESC"
        if status:
            rows = self.db.execute(
                f"SELECT * FROM drafts WHERE status = ? ORDER BY {order} LIMIT ? OFFSET ?", (status, limit, offset)
            )
        else:
            rows = self.db.execute(f"SELECT * FROM drafts ORDER BY {order} LIMIT ? OFFSET ?", (limit, offset))
        return [row_to_draft(r) for r in rows]

    def counts_by_status(self) -> dict[str, int]:
        counts = {s: 0 for s in STATUSES}
        for row in self.db.execute("SELECT status, COUNT(*) AS n FROM drafts GROUP BY status"):
            counts[row["status"]] = row["n"]
        return counts

    def update_draft(self, draft_id: int, von: str = "", **fields) -> None:
        data = {k: v for k, v in fields.items() if k in DRAFT_COLUMNS and k not in ("uid", "status")}
        for col in JSON_COLUMNS:
            if col in data and not isinstance(data[col], (str, type(None))):
                data[col] = _dumps(data[col])
        if "fakten" in fields:
            data["fakten_json"] = _dumps(fields["fakten"])
        if "dach_bezug" in data:
            data["dach_bezug"] = 1 if data["dach_bezug"] else 0
        data["updated_at"] = now_iso()
        if von:
            data["bearbeitet_von"] = von
        sets = ", ".join(f"{k} = ?" for k in data)
        self._write(f"UPDATE drafts SET {sets} WHERE id = ?", (*data.values(), draft_id))

    def set_status(self, draft_id: int, aktion: str, von: str = "") -> str:
        """Wendet eine Aktion der Status-Maschine an; ConflictError, wenn der Zustand nicht passt."""
        if aktion not in TRANSITIONS:
            raise ValueError(f"Unbekannte Aktion: {aktion}")
        allowed, target = TRANSITIONS[aktion]
        extra = ""
        if target == "freigegeben":
            extra = ", freigegeben_at = ?"
        marks = ",".join("?" for _ in allowed)
        params: list = [target, now_iso(), von]
        if extra:
            params.append(now_iso())
        params += [draft_id, *allowed]
        cur = self._write(
            f"UPDATE drafts SET status = ?, updated_at = ?, bearbeitet_von = ?{extra} "
            f"WHERE id = ? AND status IN ({marks})",
            tuple(params),
        )
        if cur.rowcount != 1:
            raise ConflictError(f"Entwurf {draft_id}: Aktion „{aktion}“ im aktuellen Zustand nicht möglich")
        return target

    def claim_draft(self, draft_id: int, von: str = "") -> dict | None:
        """Reserviert einen Entwurf fürs Veröffentlichen („Direkt posten“). None = schon vergeben."""
        marks = ",".join("?" for _ in PUBLISHABLE)
        ts = now_iso()
        cur = self._write(
            f"UPDATE drafts SET status = 'wird_veroeffentlicht', updated_at = ?, bearbeitet_von = ?, "
            f"freigegeben_at = COALESCE(freigegeben_at, ?), fehler = NULL WHERE id = ? AND status IN ({marks})",
            (ts, von, ts, draft_id, *PUBLISHABLE),
        )
        return self.get_draft(draft_id) if cur.rowcount == 1 else None

    def claim_for_publish(self, limit: int = 10) -> list[dict]:
        """Reserviert freigegebene Entwürfe für den Timer-Publisher (atomar je Zeile)."""
        ids = [r["id"] for r in self.db.execute(
            "SELECT id FROM drafts WHERE status = 'freigegeben' ORDER BY freigegeben_at LIMIT ?", (limit,)
        )]
        claimed = []
        for draft_id in ids:
            cur = self._write(
                "UPDATE drafts SET status = 'wird_veroeffentlicht', updated_at = ? WHERE id = ? AND status = 'freigegeben'",
                (now_iso(), draft_id),
            )
            if cur.rowcount == 1:
                claimed.append(self.get_draft(draft_id))
        return claimed

    def mark_published(self, draft_id: int, post_id: int | None, link: str) -> None:
        ts = now_iso()
        self._write(
            "UPDATE drafts SET status = 'veroeffentlicht', wp_post_id = ?, wp_link = ?, fehler = NULL, "
            "veroeffentlicht_at = ?, updated_at = ? WHERE id = ?",
            (post_id, link, ts, ts, draft_id),
        )

    def mark_in_wordpress(self, draft_id: int, post_id: int | None, edit_link: str) -> None:
        """„In WordPress bearbeiten“: Beitrag liegt als WP-Entwurf, Feinschliff passiert dort."""
        ts = now_iso()
        self._write(
            "UPDATE drafts SET status = 'in_wordpress', wp_post_id = ?, wp_link = ?, fehler = NULL, updated_at = ? WHERE id = ?",
            (post_id, edit_link, ts, draft_id),
        )

    def mark_publish_failed(self, draft_id: int, message: str) -> None:
        self._write(
            "UPDATE drafts SET status = 'fehler', fehler = ?, updated_at = ? WHERE id = ?",
            (message[:500], now_iso(), draft_id),
        )

    def release_claim(self, draft_id: int) -> None:
        self._write(
            "UPDATE drafts SET status = 'freigegeben', updated_at = ? WHERE id = ? AND status = 'wird_veroeffentlicht'",
            (now_iso(), draft_id),
        )

    def update_kino_facts(self, uid: str, facts: dict, fingerprint: str, note: str) -> bool:
        """Aktualisiert die Spielorte eines offenen Kino-Entwurfs, wenn sich etwas geändert hat."""
        row = self.draft_by_uid(uid)
        if row is None or row["status"] not in OPEN_STATES or row.get("fingerprint") == fingerprint:
            return False
        hinweise = row["hinweise"] + [note]
        self._write(
            "UPDATE drafts SET fakten_json = ?, fingerprint = ?, hinweise = ?, updated_at = ? WHERE id = ?",
            (_dumps(facts), fingerprint, _dumps(hinweise), now_iso(), row["id"]),
        )
        return True

    def drafts_created_since(self, since_iso: str) -> int:
        return self.db.execute("SELECT COUNT(*) FROM drafts WHERE created_at >= ?", (since_iso,)).fetchone()[0]

    # ---- Läufe und Quellen -------------------------------------------------
    def start_run(self, modus: str) -> int:
        cur = self._write("INSERT INTO runs (started_at, modus) VALUES (?, ?)", (now_iso(), modus))
        return cur.lastrowid

    def finish_run(self, run_id: int, **counts) -> None:
        allowed = ("gesammelt", "relevant", "entwuerfe", "verworfen", "veroeffentlicht", "fehler", "notiz")
        data = {k: v for k, v in counts.items() if k in allowed}
        data["finished_at"] = now_iso()
        sets = ", ".join(f"{k} = ?" for k in data)
        self._write(f"UPDATE runs SET {sets} WHERE id = ?", (*data.values(), run_id))

    def recent_runs(self, limit: int = 20) -> list[dict]:
        return [dict(r) for r in self.db.execute("SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,))]

    def source_ok(self, name: str, count: int) -> None:
        self._write(
            "INSERT INTO source_status (name, last_ok, last_count, error_msg, paused_until) VALUES (?,?,?,NULL,NULL) "
            "ON CONFLICT(name) DO UPDATE SET last_ok = excluded.last_ok, last_count = excluded.last_count, "
            "error_msg = NULL, paused_until = NULL",
            (name, now_iso(), count),
        )

    def source_failed(self, name: str, message: str, pause_minutes: int = 0) -> None:
        paused = (datetime.now(timezone.utc) + timedelta(minutes=pause_minutes)).isoformat(timespec="seconds") if pause_minutes else None
        self._write(
            "INSERT INTO source_status (name, last_error, error_msg, paused_until) VALUES (?,?,?,?) "
            "ON CONFLICT(name) DO UPDATE SET last_error = excluded.last_error, error_msg = excluded.error_msg, "
            "paused_until = excluded.paused_until",
            (name, now_iso(), message[:300], paused),
        )

    def source_last_ok(self, name: str) -> datetime | None:
        row = self.db.execute("SELECT last_ok FROM source_status WHERE name = ?", (name,)).fetchone()
        if not row or not row["last_ok"]:
            return None
        return datetime.fromisoformat(row["last_ok"])

    def sources_paused(self) -> set[str]:
        now = now_iso()
        return {r["name"] for r in self.db.execute("SELECT name FROM source_status WHERE paused_until > ?", (now,))}

    def source_status_all(self) -> list[dict]:
        return [dict(r) for r in self.db.execute("SELECT * FROM source_status ORDER BY name")]

    # ---- Dashboard (Vertrag B.3.3) ------------------------------------------
    def dashboard(self, days: int = 7) -> dict:
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")

        def grouped(column: str) -> list[dict]:
            return [
                {"name": r[0] or "–", "n": r[1]}
                for r in self.db.execute(
                    f"SELECT {column}, COUNT(*) FROM drafts WHERE created_at >= ? GROUP BY {column} ORDER BY 2 DESC",
                    (since,),
                )
            ]

        return {
            "tage": days,
            "status": self.counts_by_status(),
            "offen": sum(self.counts_by_status()[s] for s in OPEN_STATES),
            "neu_seit": self.drafts_created_since(since),
            "veroeffentlicht_seit": self.db.execute(
                "SELECT COUNT(*) FROM drafts WHERE veroeffentlicht_at >= ?", (since,)
            ).fetchone()[0],
            "je_kategorie": grouped("kategorie"),
            "je_quelle": grouped("quelle_name"),
            "je_typ": grouped("typ"),
            "laeufe": self.recent_runs(20),
            "fehler": list(self.iter_log(event="fehler", limit=20, since=since)),
            "quellen": self.source_status_all(),
        }
