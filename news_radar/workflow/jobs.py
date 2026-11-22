"""Warteschlange der Arbeitsschritte (workflow_jobs) in der Radar-Datenbank.

- einreihen: idempotent über idempotenz_key (derselbe Schritt derselben Story landet nur einmal in der Schlange)
- naechster: atomarer Claim (UPDATE … WHERE status = 'offen'), höchste Priorität zuerst
- fehlgeschlagen: Wiederholung nach 1, 5, 30 Minuten; nach 3 Versuchen „tot“ (Dead Letter, im Cockpit „Erneut“)
- budget: Jobs, die am Budget scheitern, warten („wartet_budget“) und gehen am nächsten Budget-Tag wieder los
- aufraeumen: Jobs, deren Deadline abgelaufen ist (Worker abgestürzt), kommen zurück in die Schlange
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any

from .. import schalter

BACKOFF_SEKUNDEN = (60, 300, 1800)
MAX_VERSUCHE = 3
# Deadline je Schritt: länger als Client-Timeout × Versuche (600 s × 2) plus Abrufzeit, damit aufraeumen() keinen
# noch laufenden Job ein zweites Mal startet
DEADLINE_SEKUNDEN = {"recherche": 1500, "schreiben": 1500, "faktencheck": 1500, "lektorat": 900, "seo": 900,
                     "bild": 600, "gate": 120, "kino": 300, "nachrecherche": 900, "pruefung": 1500,
                     "endpruefung": 1500}
# Schritte, die auch an einem Nachtrag laufen dürfen: ohne Modell und ohne Kosten (Suche nach Belegen)
NACHTRAG_ERLAUBT = ("nachrecherche",)
DEADLINE_STANDARD = 900

# Priorität: Termin in den nächsten Tagen > Nachricht > Rest > Dossier
PRIO_EVENT_BALD, PRIO_NEWS, PRIO_NORMAL, PRIO_DOSSIER = 30, 20, 10, 0


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def einreihen(store, story_id: int | None, schritt: str, *, prio: int = PRIO_NORMAL, key: str | None = None,
              payload: dict | None = None, verzoegerung: float = 0) -> int | None:
    """Neuer Job; None, wenn es den Schlüssel schon gibt (idempotent) – oder wenn die Story ein Nachtrag ist: Nachträge
    schreibt nur der Agent-Modus, nie ein Worker mit Modell (keine Kosten auf diesem Weg). Ausnahme: die
    Nachrecherche (sucht Belege ohne Modell)."""
    now = _now()
    key = key or f"{story_id}:{schritt}"
    if story_id is not None and schritt not in NACHTRAG_ERLAUBT and ist_nachtrag(store, story_id):
        return None
    with store.lock:
        cur = store.db.execute(
            "INSERT OR IGNORE INTO workflow_jobs (story_id, schritt, status, prio, versuche, naechster_versuch, "
            "idempotenz_key, payload, erstellt, aktualisiert) VALUES (?,?, 'offen', ?, 0, ?, ?, ?, ?, ?)",
            (story_id, schritt, prio, _iso(now + timedelta(seconds=verzoegerung)), key,
             json.dumps(payload or {}, ensure_ascii=False), _iso(now), _iso(now)),
        )
        store.db.commit()
        return cur.lastrowid if cur.rowcount == 1 else None


def ist_nachtrag(store, story_id: int | None) -> bool:
    if story_id is None:
        return False
    row = store.db.execute("SELECT herkunft FROM stories WHERE id = ?", (story_id,)).fetchone()
    return bool(row) and row[0] == "nachtrag"


def _job(row) -> dict:
    d = dict(row)
    try:
        d["payload"] = json.loads(d.get("payload") or "{}")
    except ValueError:
        d["payload"] = {}
    return d


def naechster(store, worker: str = "worker", schritte: tuple[str, ...] | None = None) -> dict | None:
    """Reserviert den dringendsten fälligen Job für diesen Worker (oder None). Hält der Schalter „redaktion“ (oder
    „alles“) an, wird kein Job übernommen."""
    if schalter.gestoppt(store, "redaktion"):
        return None
    now = _now()
    filt, params = "", []
    if schritte:
        filt = f" AND schritt IN ({','.join('?' for _ in schritte)})"
        params = list(schritte)
    with store.lock:
        for _ in range(5):  # bei Gleichzeitigkeit nächsten Kandidaten versuchen
            row = store.db.execute(
                "SELECT id, schritt FROM workflow_jobs WHERE status = 'offen' AND naechster_versuch <= ?" + filt +
                " ORDER BY prio DESC, id LIMIT 1", (_iso(now), *params),
            ).fetchone()
            if row is None:
                return None
            deadline = _iso(now + timedelta(seconds=DEADLINE_SEKUNDEN.get(row["schritt"], DEADLINE_STANDARD)))
            cur = store.db.execute(
                "UPDATE workflow_jobs SET status = 'laeuft', worker = ?, deadline = ?, versuche = versuche + 1, "
                "aktualisiert = ? WHERE id = ? AND status = 'offen'",
                (worker, deadline, _iso(now), row["id"]),
            )
            store.db.commit()
            if cur.rowcount == 1:
                return _job(store.db.execute("SELECT * FROM workflow_jobs WHERE id = ?", (row["id"],)).fetchone())
    return None


def _besitz(worker: str | None) -> tuple[str, tuple]:
    """Bedingung „dieser Worker hält den Job noch“ – ein von aufraeumen() neu vergebener Job wird nicht überschrieben."""
    return (" AND status = 'laeuft' AND worker = ?", (worker,)) if worker else ("", ())


def erledigt(store, job_id: int, worker: str | None = None) -> bool:
    filt, extra = _besitz(worker)
    cur = store._write(f"UPDATE workflow_jobs SET status = 'fertig', fehler = NULL, aktualisiert = ? WHERE id = ?{filt}",
                       (_iso(_now()), job_id, *extra))
    return cur.rowcount == 1


def fehlgeschlagen(store, job_id: int, fehler: str, worker: str | None = None) -> str:
    """Wiederholung mit Backoff; nach MAX_VERSUCHE „tot“. Gibt den neuen Status zurück („verloren“, wenn ein anderer
    Worker den Job inzwischen hält)."""
    row = store.db.execute("SELECT versuche FROM workflow_jobs WHERE id = ?", (job_id,)).fetchone()
    versuche = row["versuche"] if row else MAX_VERSUCHE
    now = _now()
    filt, extra = _besitz(worker)
    if versuche >= MAX_VERSUCHE:
        cur = store._write(f"UPDATE workflow_jobs SET status = 'tot', fehler = ?, aktualisiert = ? WHERE id = ?{filt}",
                           (fehler[:500], _iso(now), job_id, *extra))
        return "tot" if cur.rowcount == 1 else "verloren"
    pause = BACKOFF_SEKUNDEN[min(versuche, len(BACKOFF_SEKUNDEN)) - 1]
    cur = store._write(
        f"UPDATE workflow_jobs SET status = 'offen', fehler = ?, naechster_versuch = ?, aktualisiert = ? WHERE id = ?{filt}",
        (fehler[:500], _iso(now + timedelta(seconds=pause)), _iso(now), job_id, *extra),
    )
    return "offen" if cur.rowcount == 1 else "verloren"


def angehalten(store, job_id: int, grund: str, worker: str | None = None) -> bool:
    """Stopp-Schalter mitten im Schritt: Job zurück in die Schlange, der Versuch zählt nicht. Er beginnt wieder, sobald
    der Schalter aus ist."""
    filt, extra = _besitz(worker)
    now = _iso(_now())
    cur = store._write(
        f"UPDATE workflow_jobs SET status = 'offen', versuche = MAX(0, versuche - 1), fehler = ?, naechster_versuch = ?, "
        f"aktualisiert = ? WHERE id = ?{filt}", (grund[:300], now, now, job_id, *extra))
    return cur.rowcount == 1


BUDGET_PAUSE_SEKUNDEN = 900  # wartende Jobs frühestens nach 15 Minuten erneut versuchen (kein Leerlauf-Kreisel)


def wartet_budget(store, job_id: int, grund: str) -> None:
    """Budget erreicht: Job zurückstellen, der Versuch zählt nicht; frühestens in 15 Minuten wieder."""
    now = _now()
    store._write(
        "UPDATE workflow_jobs SET status = 'wartet_budget', versuche = MAX(0, versuche - 1), fehler = ?, "
        "naechster_versuch = ?, aktualisiert = ? WHERE id = ?",
        (grund[:300], _iso(now + timedelta(seconds=BUDGET_PAUSE_SEKUNDEN)), _iso(now), job_id),
    )


def budget_wieder_frei(store) -> int:
    """Wartende Jobs, deren Pause vorbei ist, zurück in die Schlange."""
    now = _iso(_now())
    cur = store._write("UPDATE workflow_jobs SET status = 'offen', aktualisiert = ? "
                       "WHERE status = 'wartet_budget' AND naechster_versuch <= ?", (now, now))
    return cur.rowcount


def aufraeumen(store) -> int:
    """Hängende Jobs (Deadline vorbei) zurück in die Schlange bzw. auf „tot“, wenn die Versuche aufgebraucht sind."""
    now = _iso(_now())
    with store.lock:
        cur = store.db.execute(
            "UPDATE workflow_jobs SET status = CASE WHEN versuche >= ? THEN 'tot' ELSE 'offen' END, "
            "fehler = 'Deadline überschritten', aktualisiert = ? WHERE status = 'laeuft' AND deadline < ?",
            (MAX_VERSUCHE, now, now),
        )
        store.db.commit()
        return cur.rowcount


def erneut(store, job_id: int) -> bool:
    cur = store._write(
        "UPDATE workflow_jobs SET status = 'offen', versuche = 0, fehler = NULL, naechster_versuch = ?, aktualisiert = ? "
        "WHERE id = ? AND status IN ('tot', 'wartet_budget') AND NOT EXISTS (SELECT 1 FROM stories s WHERE "
        "s.id = workflow_jobs.story_id AND s.herkunft = 'nachtrag')", (_iso(_now()), _iso(_now()), job_id),
    )
    return cur.rowcount == 1


def liste(store, status: str | None = None, limit: int = 100) -> list[dict]:
    if status:
        rows = store.db.execute(
            "SELECT j.*, s.titel AS story_titel FROM workflow_jobs j LEFT JOIN stories s ON s.id = j.story_id "
            "WHERE j.status = ? ORDER BY j.prio DESC, j.id DESC LIMIT ?", (status, limit))
    else:
        rows = store.db.execute(
            "SELECT j.*, s.titel AS story_titel FROM workflow_jobs j LEFT JOIN stories s ON s.id = j.story_id "
            "ORDER BY j.id DESC LIMIT ?", (limit,))
    return [_job(r) for r in rows]


def zaehlen(store) -> dict[str, int]:
    out = {s: 0 for s in ("offen", "laeuft", "fertig", "tot", "wartet_budget")}
    for row in store.db.execute("SELECT status, COUNT(*) FROM workflow_jobs GROUP BY status"):
        out[row[0]] = row[1]
    return out


def offen_fuer_story(store, story_id: int) -> list[dict[str, Any]]:
    return [_job(r) for r in store.db.execute(
        "SELECT * FROM workflow_jobs WHERE story_id = ? AND status IN ('offen', 'laeuft', 'wartet_budget')", (story_id,))]
