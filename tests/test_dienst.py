"""Container-Betrieb (Coolify): Zeitplan, Neustart der Langläufer, geordnetes Ende."""

import sys
import time
from datetime import datetime

from news_radar import dienst
from news_radar.dienst import TZ, Aufgabe, Dienst, Langlaeufer, Regel, faellig


def t(tag, stunde, minute=0):
    return datetime(2026, 11, tag, stunde, minute, tzinfo=TZ)  # 9.11.2026 ist ein Montag


def test_faellig_interval_and_daily_and_weekly():
    alle3 = Regel(alle=180)
    assert faellig(t(9, 10), None, alle3)
    assert not faellig(t(9, 10, 2), t(9, 10), alle3) and faellig(t(9, 10, 3), t(9, 10), alle3)
    acht = Regel(um=(8, 0))
    assert not faellig(t(9, 7, 59), t(9, 7), acht)
    assert faellig(t(9, 8, 0), t(9, 7, 59), acht)
    assert not faellig(t(9, 8, 1), t(9, 8, 0), acht)  # nur einmal je Tag
    assert faellig(t(10, 8, 5), t(9, 8, 0), acht)
    assert not faellig(t(9, 9), None, acht)  # ohne Startzeit kein Nachholen
    montag = Regel(um=(4, 30), wochentag=0)
    assert faellig(t(9, 4, 31), t(9, 4), montag)
    assert not faellig(t(10, 4, 31), t(9, 4, 31), montag)  # Dienstag
    assert faellig(t(16, 4, 30), t(10, 4, 31), montag)


def test_service_restarts_crashed_process_runs_tasks_and_stops_children(tmp_path):
    marke = tmp_path / "lauf.txt"
    absturz = Langlaeufer("absturz", [sys.executable, "-c", "import sys; sys.exit(3)"])
    dauer = Langlaeufer("dauer", [sys.executable, "-c", "import time; time.sleep(60)"])
    scan = Aufgabe("scan", [sys.executable, "-c", f"open({str(marke)!r}, 'a').write('x')"], Regel(alle=1))
    d = Dienst([absturz, dauer], [scan])
    ende = time.monotonic() + 3.5
    starts = set()
    while time.monotonic() < ende:
        d.schritt()
        if absturz.proc is not None:
            starts.add(absturz.proc.pid)
        time.sleep(0.1)
    assert len(starts) >= 2  # abgestürzter Langläufer wird neu gestartet (Backoff 1–2 s)
    assert len(marke.read_text()) >= 2  # Intervall-Aufgabe lief mehrfach, nie parallel
    lauf = dauer.proc
    t0 = time.monotonic()
    d.beenden(frist=5)
    assert lauf.poll() is not None and time.monotonic() - t0 < 5


def test_task_timeout_kills_and_no_overlap(tmp_path):
    haengt = Aufgabe("haengt", [sys.executable, "-c", "import time; time.sleep(30)"], Regel(alle=1), timeout=1)
    d = Dienst([], [haengt])
    d.schritt()
    erster = haengt.proc
    time.sleep(0.5)
    d.schritt()
    assert haengt.proc is erster  # läuft noch: kein zweiter Start
    time.sleep(0.8)
    d.schritt()
    assert erster.poll() is not None  # nach dem Timeout beendet
    d.beenden(frist=2)


def test_build_service_from_settings(monkeypatch, tmp_path):
    from news_radar.config import load_settings

    monkeypatch.setenv("RADAR_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("RADAR_WORKFLOW", "v2")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("RADAR_ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    ohne = dienst.aufbauen(load_settings(), 3000)
    assert [l.name for l in ohne.langlaeufer] == ["web"]
    assert "0.0.0.0:3000" in ohne.langlaeufer[0].befehl
    assert [a.name for a in ohne.aufgaben] == ["scan", "digest", "sicherung"]
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("GEMINI_API_KEY", "g-test")
    mit = dienst.aufbauen(load_settings(), 3000)
    assert [l.name for l in mit.langlaeufer] == ["web", "worker"] and mit.aufgaben[-1].name == "bildpool"
    assert str(tmp_path / "backup") in mit.aufgaben[2].befehl
