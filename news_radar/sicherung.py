"""Sicherung und Wiederherstellung: Datenbank (WAL-sicher über die SQLite-Backup-API) und Bilder.

  python -m news_radar sicherung erstellen [--ziel backup/]          (täglich per cron, 14 Tage aufbewahren)
  python -m news_radar sicherung pruefen --datum 2026-11-08          (Integritätsprüfung, ohne etwas zu ändern)
  python -m news_radar sicherung wiederherstellen --datum 2026-11-08 (Dienste vorher stoppen: deploy/restore.sh)

Vor der Wiederherstellung wird der aktuelle Stand als radar.sqlite.vor-restore-<Zeit> beiseitegelegt.
"""

from __future__ import annotations

import re
import shutil
import sqlite3
import tarfile
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

AUFBEWAHREN_TAGE = 14
_STAND_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_EIGENE_RE = re.compile(r"^(radar-\d{4}-\d{2}-\d{2}\.sqlite|bilder-\d{4}-\d{2}-\d{2}\.tgz)$")


def stand(stamp: str) -> str:
    """Ein Stand ist genau YYYY-MM-DD – kein Pfad, kein Platzhalter."""
    if not _STAND_RE.fullmatch(stamp or ""):
        raise ValueError(f"Stand muss YYYY-MM-DD sein, nicht {stamp!r}")
    date.fromisoformat(stamp)
    return stamp


def _sqlite_kopie(von: Path, nach: Path) -> None:
    """Konsistente Kopie über die SQLite-Backup-API: berücksichtigt Daten, die noch im WAL stehen, und Sperren."""
    quelle = sqlite3.connect(von)
    ziel = sqlite3.connect(nach)
    try:
        quelle.backup(ziel)
    finally:
        ziel.close()
        quelle.close()


def erstellen(data_dir: Path, ziel: Path, stamp: str | None = None) -> dict:
    ziel.mkdir(parents=True, exist_ok=True)
    stamp = stand(stamp or date.today().isoformat())
    db_ziel = ziel / f"radar-{stamp}.sqlite"
    _sqlite_kopie(data_dir / "radar.sqlite", db_ziel)  # konsistent auch während Worker und Cockpit schreiben (WAL)
    bilder = data_dir / "bilder"
    tgz = ziel / f"bilder-{stamp}.tgz"
    with tarfile.open(tgz, "w:gz") as tar:
        if bilder.is_dir():
            tar.add(bilder, arcname="bilder")
    grenze = datetime.now(timezone.utc) - timedelta(days=AUFBEWAHREN_TAGE)
    for alt in ziel.glob("*"):  # nur eigene Sicherungen löschen, nie andere Dateien im Ordner
        if alt.is_file() and _EIGENE_RE.fullmatch(alt.name) and datetime.fromtimestamp(alt.stat().st_mtime, timezone.utc) < grenze:
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


def _nur_bilder(tar: tarfile.TarFile) -> list[tarfile.TarInfo]:
    """Nur Einträge unter bilder/ – ein manipuliertes Archiv kann so nicht radar.sqlite oder .env überschreiben."""
    return [m for m in tar.getmembers() if m.name == "bilder" or m.name.startswith("bilder/")]


def wiederherstellen(data_dir: Path, quelle: Path, stamp: str) -> dict:
    """Erst die Bilder in einen Nebenordner entpacken (schlägt das fehl, bleibt alles wie es war), dann die Datenbank
    über die Backup-API zurückschreiben und den Bilderordner tauschen. Die Dienste müssen gestoppt sein
    (deploy/restore.sh stoppt alle news-radar-Units und bricht ab, wenn einer noch läuft)."""
    stamp = stand(stamp)
    db = quelle / f"radar-{stamp}.sqlite"
    info = pruefen(db)
    data_dir.mkdir(parents=True, exist_ok=True)
    jetzt = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    tgz = quelle / f"bilder-{stamp}.tgz"
    neu_bilder = None
    if tgz.is_file():
        tmp = Path(tempfile.mkdtemp(prefix=f"bilder.restore-{jetzt}-", dir=data_dir))
        try:
            with tarfile.open(tgz, "r:gz") as tar:
                tar.extractall(tmp, members=_nur_bilder(tar), filter="data")  # „data“: keine absoluten Pfade, kein ../
        except Exception:
            shutil.rmtree(tmp, ignore_errors=True)
            raise
        neu_bilder = tmp / "bilder"
        neu_bilder.mkdir(exist_ok=True)
    aktuell = data_dir / "radar.sqlite"
    if aktuell.exists():
        _sqlite_kopie(aktuell, data_dir / f"radar.sqlite.vor-restore-{jetzt}")  # inkl. WAL-Inhalt
    _sqlite_kopie(db, aktuell)  # schreibt Seite für Seite in die echte Datei, WAL und -shm bleiben stimmig
    if neu_bilder is not None:
        bilder = data_dir / "bilder"
        if bilder.exists():
            bilder.rename(data_dir / f"bilder.vor-restore-{jetzt}")
        neu_bilder.rename(bilder)
        shutil.rmtree(neu_bilder.parent, ignore_errors=True)
    return info
