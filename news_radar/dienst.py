"""Ein Container für den ganzen Radar (Coolify, Dockerfile): Cockpit, Scan alle 3 Minuten, Worker, Digest, Sicherung.

  python -m news_radar dienst          (CMD im Dockerfile; ersetzt die systemd-Units aus deploy/)

Langläufer (bei Absturz mit Backoff neu gestartet):
  web     gunicorn „news_radar.web:create_app()“ auf 0.0.0.0:$PORT (Standard 3000)
  worker  Redaktion v2 (nur mit RADAR_WORKFLOW=v2 und Schlüssel)
Zeitplan (Europe/Berlin; jeweils als eigener Prozess mit Timeout, nie doppelt):
  scan      `run` alle 3 Minuten           (news-radar.timer)
  digest    `digest` täglich 08:00          (news-radar-digest.timer)
  sicherung `sicherung erstellen` 03:00     (Backup-Cron) – nach $RADAR_DATA_DIR/backup
  bildpool  montags 04:30, nur mit GEMINI_API_KEY (news-radar-bildpool.timer)

Startet der Container als root, gehört der Datenordner danach dem Nutzer `radar` und der Dienst gibt die Rechte ab
(Coolify-Volumes gehören anfangs root). SIGTERM (Redeploy) beendet alle Kinder geordnet.
"""

from __future__ import annotations

import logging
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

from .config import Settings

TZ = ZoneInfo("Europe/Berlin")
log = logging.getLogger("news_radar.dienst")


@dataclass(frozen=True)
class Regel:
    """Entweder `alle` Sekunden oder täglich `um` (Stunde, Minute), optional nur am `wochentag` (0 = Montag)."""
    alle: int = 0
    um: tuple[int, int] | None = None
    wochentag: int | None = None


def letzter_termin(jetzt: datetime, regel: Regel) -> datetime:
    """Der jüngste geplante Zeitpunkt <= jetzt (nur für Regeln mit `um`)."""
    assert regel.um is not None
    termin = jetzt.replace(hour=regel.um[0], minute=regel.um[1], second=0, microsecond=0)
    if termin > jetzt:
        termin -= timedelta(days=1)
    if regel.wochentag is not None:
        while termin.weekday() != regel.wochentag:
            termin -= timedelta(days=1)
    return termin


def faellig(jetzt: datetime, letzte: datetime | None, regel: Regel) -> bool:
    """Intervall: beim ersten Mal sofort, dann alle `alle` Sekunden. Uhrzeit: wenn seit `letzte` ein Termin lag."""
    if regel.alle:
        return letzte is None or (jetzt - letzte).total_seconds() >= regel.alle
    return letzte is not None and letzter_termin(jetzt, regel) > letzte


@dataclass
class Aufgabe:
    name: str
    befehl: list[str]
    regel: Regel
    timeout: int = 300
    letzte: datetime | None = None
    proc: subprocess.Popen | None = None
    gestartet: float = 0.0


@dataclass
class Langlaeufer:
    name: str
    befehl: list[str]
    proc: subprocess.Popen | None = None
    gestartet: float = 0.0
    fehlstarts: int = 0
    naechster_start: float = 0.0


@dataclass
class Dienst:
    langlaeufer: list[Langlaeufer]
    aufgaben: list[Aufgabe]
    uhr: Callable[[], datetime] = field(default=lambda: datetime.now(TZ))
    env: dict[str, str] | None = None
    stop: bool = False

    def _starten(self, befehl: list[str]) -> subprocess.Popen:
        return subprocess.Popen(befehl, env=self.env)

    def schritt(self) -> None:
        mono = time.monotonic()
        for l in self.langlaeufer:
            if l.proc is not None and l.proc.poll() is not None:
                lief = mono - l.gestartet
                l.fehlstarts = 0 if lief > 600 else l.fehlstarts + 1
                warten = min(60, 2 ** l.fehlstarts) if l.fehlstarts else 1
                log.warning("%s beendet (Code %s nach %.0f s) – Neustart in %s s", l.name, l.proc.returncode, lief, warten)
                l.proc, l.naechster_start = None, mono + warten
            if l.proc is None and mono >= l.naechster_start:
                log.info("starte %s", l.name)
                l.proc, l.gestartet = self._starten(l.befehl), mono
        jetzt = self.uhr()
        for a in self.aufgaben:
            if a.proc is not None:
                if a.proc.poll() is None:
                    if mono - a.gestartet > a.timeout:
                        log.error("%s nach %s s abgebrochen (Timeout)", a.name, a.timeout)
                        a.proc.kill()
                        a.proc.wait()
                        a.proc = None
                    continue  # läuft noch: nicht doppelt starten
                if a.proc.returncode:
                    log.warning("%s endete mit Code %s", a.name, a.proc.returncode)
                a.proc = None
            if faellig(jetzt, a.letzte, a.regel):
                a.letzte = jetzt
                a.proc, a.gestartet = self._starten(a.befehl), mono

    def beenden(self, frist: float = 20.0) -> None:
        procs = [p for p in [l.proc for l in self.langlaeufer] + [a.proc for a in self.aufgaben] if p is not None]
        for p in procs:
            if p.poll() is None:
                p.terminate()
        ende = time.monotonic() + frist
        for p in procs:
            try:
                p.wait(timeout=max(0.1, ende - time.monotonic()))
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait()

    def laufen(self, takt: float = 1.0) -> None:
        jetzt = self.uhr()
        for a in self.aufgaben:  # Uhrzeit-Aufgaben beim Start nicht nachholen (z. B. Digest nach Redeploy um 09:00)
            if a.regel.um is not None and a.letzte is None:
                a.letzte = jetzt
        while not self.stop:
            self.schritt()
            time.sleep(takt)
        self.beenden()


def rechte_abgeben(data_dir: Path, nutzer: str = "radar") -> None:
    """Als root gestartet: Datenordner an `nutzer` übergeben und die Rechte abgeben."""
    if os.name != "posix" or os.getuid() != 0:
        return
    import pwd

    try:
        pw = pwd.getpwnam(nutzer)
    except KeyError:
        log.warning("Nutzer %s fehlt – der Dienst läuft als root weiter", nutzer)
        return
    data_dir.mkdir(parents=True, exist_ok=True)
    for wurzel, ordner, dateien in os.walk(data_dir):
        for name in [wurzel, *(os.path.join(wurzel, n) for n in ordner + dateien)]:
            st = os.lstat(name)
            if st.st_uid != pw.pw_uid or st.st_gid != pw.pw_gid:
                os.lchown(name, pw.pw_uid, pw.pw_gid)
    os.setgroups([])
    os.setgid(pw.pw_gid)
    os.setuid(pw.pw_uid)
    os.environ["HOME"] = pw.pw_dir


def aufbauen(settings: Settings, port: int) -> Dienst:
    py = [sys.executable, "-m", "news_radar"]
    langlaeufer = [Langlaeufer("web", [sys.executable, "-m", "gunicorn", "-w", "2", "--threads", "4",
                                       "-b", f"0.0.0.0:{port}", "--timeout", "120", "--access-logfile", "-",
                                       "news_radar.web:create_app()"])]
    if settings.workflow == "v2" and os.environ.get("ANTHROPIC_API_KEY"):
        langlaeufer.append(Langlaeufer("worker", py + ["worker"]))
    elif settings.workflow == "v2":
        log.warning("RADAR_WORKFLOW=v2 ohne ANTHROPIC_API_KEY: Scan legt Storys an, der Worker startet nicht "
                    "(Agent-Modus: agent export --v2)")
    aufgaben = [
        Aufgabe("scan", py + ["run"], Regel(alle=180), timeout=300),
        Aufgabe("digest", py + ["digest"], Regel(um=(8, 0)), timeout=300),
        Aufgabe("sicherung", py + ["sicherung", "erstellen", "--ziel", str(settings.data_dir / "backup")],
                Regel(um=(3, 0)), timeout=1800),
    ]
    if os.environ.get("GEMINI_API_KEY"):
        aufgaben.append(Aufgabe("bildpool", py + ["bildpool", "fuellen", "--anzahl", "3", "--mit-budget"],
                                Regel(um=(4, 30), wochentag=0), timeout=1800))
    return Dienst(langlaeufer, aufgaben)


def main(settings: Settings) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(name)s %(message)s")
    rechte_abgeben(settings.data_dir)
    port = int(os.environ.get("PORT", "3000"))
    dienst = aufbauen(settings, port)

    def anhalten(signum, _frame):
        log.info("Signal %s – beende alle Prozesse", signum)
        dienst.stop = True

    signal.signal(signal.SIGTERM, anhalten)
    signal.signal(signal.SIGINT, anhalten)
    log.info("Radar-Dienst: Port %s, Daten %s, Workflow %s, Langläufer %s", port, settings.data_dir, settings.workflow,
             ", ".join(l.name for l in dienst.langlaeufer))
    dienst.laufen()
    return 0
