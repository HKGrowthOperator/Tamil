"""Sicherung und Wiederherstellung: Datenbank (WAL-sicher über die SQLite-Backup-API) und Bilder.

  python -m news_radar sicherung erstellen [--ziel backup/]          (täglich per cron, 14 Tage aufbewahren)
  python -m news_radar sicherung pruefen --datum 2026-11-08          (Integritätsprüfung, ohne etwas zu ändern)
  python -m news_radar sicherung wiederherstellen --datum 2026-11-08 (Dienste vorher stoppen: deploy/restore.sh)

Vor der Wiederherstellung wird der aktuelle Stand als radar.sqlite.vor-restore-<Zeit> beiseitegelegt.
"""

from __future__ import annotations

import shutil
import sqlite3
import tarfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

AUFBEWAHREN_TAGE = 14


def erstellen(data_dir: Path, ziel: Path, stamp: str | None = None) -> dict:
    ziel.mkdir(parents=True, exist_ok=True)
    stamp = stamp or date.today().isoformat()
    db_ziel = ziel / f"radar-{stamp}.sqlite"
    quelle = sqlite3.connect(data_dir / "radar.sqlite")
    kopie = sqlite3.connect(db_ziel)
    try:
        quelle.backup(kopie)  # konsistent auch während Worker und Cockpit schreiben (WAL)
    finally:
        kopie.close()
        quelle.close()
    bilder = data_dir / "bilder"
    tgz = ziel / f"bilder-{stamp}.tgz"
    with tarfile.open(tgz, "w:gz") as tar:
        if bilder.is_dir():
            tar.add(bilder, arcname="bilder")
    grenze = datetime.now(timezone.utc) - timedelta(days=AUFBEWAHREN_TAGE)
    for alt in ziel.glob("*"):
        if alt.is_file() and datetime.fromtimestamp(alt.stat().st_mtime, timezone.utc) < grenze:
            alt.unlink()
    return {"datenbank": db_ziel, "bilder": tgz}


def pruefen(datei: Path) -> dict:
    """Integritätsprüfung einer gesicherten Datenbank; gibt Zählwerte zurück, ValueError bei Defekt."""
    if not datei.is_file():
        raise ValueError(f"Sicherung fehlt: {datei}")
    con = sqlite3.connect(f"file:{datei}?mode=ro", uri=True)
    try:
        ergebnis = con.execute("PRAGMA integrity_check").fetchone()[0]
        if ergebnis != "ok":
            raise ValueError(f"Sicherung beschädigt: {ergebnis}")
        tabellen = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        zaehlen = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]  # noqa: S608 – Tabellennamen aus sqlite_master
                   for t in ("drafts", "stories", "agent_usage", "workflow_jobs") if t in tabellen}
        version = con.execute("PRAGMA user_version").fetchone()[0]
    finally:
        con.close()
    return {"integritaet": "ok", "version": version, **zaehlen}


def wiederherstellen(data_dir: Path, quelle: Path, stamp: str) -> dict:
    db = quelle / f"radar-{stamp}.sqlite"
    info = pruefen(db)
    data_dir.mkdir(parents=True, exist_ok=True)
    aktuell = data_dir / "radar.sqlite"
    jetzt = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    if aktuell.exists():
        shutil.copy2(aktuell, data_dir / f"radar.sqlite.vor-restore-{jetzt}")
    for rest in (data_dir / "radar.sqlite-wal", data_dir / "radar.sqlite-shm"):
        rest.unlink(missing_ok=True)
    shutil.copy2(db, aktuell)
    tgz = quelle / f"bilder-{stamp}.tgz"
    if tgz.is_file():
        bilder = data_dir / "bilder"
        if bilder.exists():
            bilder.rename(data_dir / f"bilder.vor-restore-{jetzt}")
        with tarfile.open(tgz, "r:gz") as tar:
            tar.extractall(data_dir, filter="data")  # „data“-Filter: keine absoluten Pfade, kein ../
    return info
