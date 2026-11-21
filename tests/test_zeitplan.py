"""Zeitplan (Vertrag B1.1 „zeitgesteuerte Ausführungen“, Festlegung F0 Punkt 10): der Plan aus dienst.py als Daten,
aufgezeichnete Läufe, nächste Fälligkeit, Anhalten durch den Schalter – und die Ansicht /zeitplan."""

import sys
import time
from datetime import datetime

import pytest

from news_radar import dienst, schalter
from news_radar.config import load_settings
from news_radar.dienst import TZ, Aufgabe, Dienst, Regel
from news_radar.store import Store


@pytest.fixture
def settings(tmp_path, monkeypatch):
    for var in ("WP_URL", "WP_USER", "WP_APP_PASSWORD", "GEMINI_API_KEY", "NOTIFY_WEBHOOK_URL", "ANTHROPIC_API_KEY"):
        monkeypatch.setenv(var, "")
    s = load_settings()
    s.data_dir = tmp_path
    return s


def t(tag, stunde, minute=0):
    return datetime(2026, 11, tag, stunde, minute, tzinfo=TZ)  # 9.11.2026 ist ein Montag


def test_plan_ist_die_eine_quelle_fuer_dienst_und_ansicht(settings):
    plan = dienst.plan(settings, env={})
    assert [e.name for e in plan] == ["scan", "digest", "sicherung"]
    assert [e.name for e in dienst.plan(settings, env={"GEMINI_API_KEY": "x"})][-1] == "bildpool"
    d = dienst.aufbauen(settings, 3000)
    assert [(a.name, a.befehl[3:], a.regel, a.kanaele) for a in d.aufgaben] == \
        [(e.name, list(e.args), e.regel, e.kanaele) for e in dienst.plan(settings)]
    scan = plan[0]
    assert scan.regel == Regel(alle=180) and set(scan.kanaele) == {"redaktion", "website"}
    assert plan[2].kanaele == ()  # die Sicherung bleibt lokal und läuft auch im Stopp


def test_takt_und_naechste_faelligkeit():
    assert dienst.takt_text(Regel(alle=180)) == "alle 3 Minuten"
    assert dienst.takt_text(Regel(um=(8, 0))) == "täglich 08:00"
    assert dienst.takt_text(Regel(um=(4, 30), wochentag=0)) == "montags 04:30"
    assert dienst.naechster_termin(t(9, 10), Regel(alle=180), t(9, 9, 59)) == t(9, 10, 2)
    assert dienst.naechster_termin(t(9, 10), Regel(alle=180), None) is None  # beim nächsten Start
    assert dienst.naechster_termin(t(9, 7), Regel(um=(8, 0)), None) == t(9, 8)
    assert dienst.naechster_termin(t(9, 9), Regel(um=(8, 0)), None) == t(10, 8)
    assert dienst.naechster_termin(t(10, 5), Regel(um=(4, 30), wochentag=0), None) == t(16, 4, 30)


def test_dienst_zeichnet_laeufe_auf_und_ruht_im_stopp(settings):
    with Store(settings.db_path) as store:
        gut = Aufgabe("gut", [sys.executable, "-c", "pass"], Regel(alle=3600))
        kaputt = Aufgabe("kaputt", [sys.executable, "-c", "import sys; sys.exit(3)"], Regel(alle=3600))
        gestoppt = Aufgabe("gestoppt", [sys.executable, "-c", "pass"], Regel(alle=3600), kanaele=("redaktion",))
        lokal = Aufgabe("lokal", [sys.executable, "-c", "pass"], Regel(alle=3600))
        schalter.setzen(store, "redaktion", True, wer="priya", grund="Test")
        d = Dienst([], [gut, kaputt, gestoppt, lokal], store=store)
        d.schritt()
        assert gestoppt.proc is None and gut.proc is not None
        ende = time.monotonic() + 10
        while any(a.proc is not None for a in (gut, kaputt, lokal)) and time.monotonic() < ende:
            time.sleep(0.05)
            d.schritt()
        laeufe = {r["aufgabe"]: dict(r) for r in store.db.execute("SELECT * FROM dienst_laeufe")}
    assert laeufe["gut"]["ergebnis"] == "ok" and laeufe["gut"]["ende"]
    assert laeufe["kaputt"]["ergebnis"] == "fehler (Code 3)"
    assert laeufe["gestoppt"]["ergebnis"] == "angehalten (redaktion)"


def test_alles_haelt_jede_aufgabe_mit_kanal_an_nicht_die_sicherung(settings):
    with Store(settings.db_path) as store:
        schalter.setzen(store, "alles", True, wer="anna", grund="Notfall")
        plan = dienst.plan(settings, env={})
        assert schalter.haelt_an(store, plan[0].kanaele)["kanal"] == "alles"  # scan
        assert schalter.haelt_an(store, plan[1].kanaele)["kanal"] == "alles"  # digest
        assert schalter.haelt_an(store, plan[2].kanaele) is None             # sicherung
        schalter.setzen(store, "alles", False, wer="anna")
        schalter.setzen(store, "redaktion", True, wer="anna", grund="nur Redaktion")
        assert schalter.haelt_an(store, plan[0].kanaele) is None  # scan läuft: er veröffentlicht weiter


def test_zeitplan_ansicht(settings):
    from news_radar.web import create_app

    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim", "s3cret"
    with Store(settings.db_path) as store:
        store._write("INSERT INTO dienst_laeufe (aufgabe, start, ende, ergebnis) VALUES "
                     "('scan', '2026-11-11T09:00:00+00:00', '2026-11-11T09:00:20+00:00', 'fehler (Code 1)')")
        schalter.setzen(store, "alles", True, wer="anna", grund="Notfall")
    app = create_app(settings, testing=True)
    client = app.test_client()
    client.get("/login")
    with client.session_transaction() as s:
        token = s["csrf"]
    client.post("/login", data={"user": "luis", "password": "geheim", "_csrf": token})
    html = client.get("/zeitplan").get_data(as_text=True)
    for teil in ("scan", "digest", "sicherung", "alle 3 Minuten", "täglich 08:00", "11.11.2026 10:00",
                 "fehler (Code 1)", "angehalten", "noch nicht aufgezeichnet", "Worker"):
        assert teil in html, teil
