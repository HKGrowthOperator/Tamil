"""SQLite-Speicher: gesehene Meldungen und Protokoll (Vertrag Pos. B.3.4)."""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path


class Store:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.lock = threading.Lock()  # Beiträge werden parallel verarbeitet
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS seen (
                uid TEXT PRIMARY KEY, title TEXT, url TEXT, source TEXT,
                status TEXT, created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS log (
                id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, event TEXT, data TEXT
            );
            """
        )

    def seen_uids(self) -> set[str]:
        return {row[0] for row in self.db.execute("SELECT uid FROM seen")}

    def recent_titles(self, days: int = 3) -> list[str]:
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        return [r[0] for r in self.db.execute("SELECT title FROM seen WHERE created_at >= ?", (since,))]

    def mark(self, uid: str, title: str, url: str, source: str, status: str) -> None:
        with self.lock:
            self._write(
                "INSERT OR REPLACE INTO seen VALUES (?,?,?,?,?,?)",
                (uid, title, url, source, status, datetime.now(timezone.utc).isoformat()),
            )

    def event(self, event: str, **data) -> None:
        with self.lock:
            self._write(
                "INSERT INTO log (ts, event, data) VALUES (?,?,?)",
                (datetime.now(timezone.utc).isoformat(), event, json.dumps(data, ensure_ascii=False, default=str)),
            )

    def _write(self, sql: str, params: tuple) -> None:
        self.db.execute(sql, params)
        self.db.commit()

    def export_log(self, path: Path) -> int:
        rows = self.db.execute("SELECT ts, event, data FROM log ORDER BY id").fetchall()
        path.write_text(
            "\n".join(json.dumps({"ts": t, "event": e, **json.loads(d)}, ensure_ascii=False) for t, e, d in rows),
            encoding="utf-8",
        )
        return len(rows)
