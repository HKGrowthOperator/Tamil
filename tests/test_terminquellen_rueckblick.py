"""Terminquellen aus der Rückblick-Recherche 12.11.2026, ohne Netz, gegen die an dem Tag gespeicherten Antworten:

- München Tamil Sangam e.V.: Kalender „The Events Calendar“ (/wp-json/tribe/events/v1/events). Die Fixture ist die
  Antwort für das ganze Jahr 2026 (start_date 1.1.): Kodai Vizha (16.5.) ist vorbei und fällt heraus.
- Sri Meenadchi Ambal Tempel Backnang: Terminliste „Zukünftige Veranstaltungen“ (Elementor-Widget, je Termin ein
  <article class="mel-card">, Datum englisch „November 13, 2026 6:00 p.m.“). Ort ist immer der Tempel."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from news_radar import pipeline, sources
from news_radar.config import load_settings

FIX = Path(__file__).parent / "fixtures"
STAND = datetime(2026, 11, 12, 12, tzinfo=timezone.utc)  # Abruf der Fixtures
MTS = "München Tamil Sangam · Termine"
BACKNANG = "Sri Meenadchi Ambal Tempel Backnang · Termine"


class Antwort:
    def __init__(self, datei: str, typ: str):
        self.status_code = 200
        self.content = (FIX / datei).read_bytes()
        self.headers = {"Content-Type": typ}

    def iter_content(self, size):
        yield self.content

    def raise_for_status(self):
        pass

    def close(self):
        pass


@pytest.fixture
def settings(monkeypatch):
    for var in ("WP_USER", "WP_APP_PASSWORD", "NEWSAPI_KEY", "GNEWS_TOKEN"):
        monkeypatch.setenv(var, "")
    return load_settings()


def _quelle(settings, name):
    return next(q for q in settings.alle_quellen if q.name == name)


def _seite(monkeypatch, datei, typ):
    aufrufe = []

    def get(url, **kw):
        aufrufe.append((url, kw.get("params")))
        return Antwort(datei, typ)

    monkeypatch.setattr(sources.requests, "get", get)
    return aufrufe


def test_muenchen_tamil_sangam_ist_registriert(settings):
    q = _quelle(settings, MTS)
    assert (q.type, q.url, q.country, q.kind) == ("tribe_events", "https://muenchentamilsangam.org", "DE", "event")
    assert q.robots == "erlaubt" and q.betreiber and q.prioritaet in {"A", "B", "C"}


def test_muenchen_tamil_sangam_nur_kommende_termine_mit_ort(monkeypatch, settings):
    aufrufe = _seite(monkeypatch, "tribe_events_muenchen_tamil_sangam.json", "application/json; charset=UTF-8")
    items = sources.FETCHERS["tribe_events"](_quelle(settings, MTS), settings, now=STAND)
    assert aufrufe[0][0] == "https://muenchentamilsangam.org/wp-json/tribe/events/v1/events"
    assert aufrufe[0][1]["start_date"] == "2026-11-12"
    # „MTS Kodai Vizha 2026“ (16.5.2026) ist vorbei und fehlt
    assert [(i.title, i.facts["event_datum"]) for i in items] == [("Diwali-2026", "2026-11-21")]
    diwali = items[0]
    assert diwali.facts["event_ort"] == "Bürgerhaus Neukeferloh, Bürgerhaus, Leonhard-Stadler-Straße 12, Neukeferloh"
    assert diwali.ort == "Neukeferloh" and diwali.kind == "event"
    assert diwali.url == "https://muenchentamilsangam.org/event/diwali-2026/"
    assert diwali.summary.startswith("21.11.2026, 10:30 Uhr")


def _ohne_auswahl(settings):
    q = _quelle(settings, BACKNANG)
    q.params = {k: v for k, v in q.params.items() if k != "nur_titel"}
    return q


def test_backnang_ist_registriert(settings):
    q = _quelle(settings, BACKNANG)
    assert (q.type, q.country, q.kind) == ("html", "DE", "event")
    assert q.url == "https://srimeenadchiambal.com/de/zukuenftige-veranstaltungen/"
    assert q.robots == "erlaubt" and q.betreiber and q.prioritaet in {"A", "B", "C"}


def test_backnang_an_mit_festauswahl(settings):
    """Seit 13.11. an (Gedenk-Sperre gilt für alle Terminquellen); nur große Feste werden Story, keine Pooja- und
    Fastentage (params.nur_titel)."""
    q = _quelle(settings, BACKNANG)
    assert q.enabled is True and BACKNANG in {x.name for x in settings.sources}
    nur = [t.lower() for t in q.params["nur_titel"]]
    assert "deepavali" in nur and "pongal" in nur and "தீபாவளி" in nur
    assert MTS in {x.name for x in settings.sources}


def test_festauswahl_laesst_pooja_tage_weg(monkeypatch, settings):
    _seite(monkeypatch, "srimeenadchiambal_zukunft.html", "text/html; charset=UTF-8")
    q = _quelle(settings, BACKNANG)
    assert sources.FETCHERS["html"](q, settings) == []  # nur Skandashashti, Fasten, Thiruvempavai: kein Fest
    q.params = {**q.params, "nur_titel": ["Sarvalaya Deepam"]}
    assert [i.title for i in sources.FETCHERS["html"](q, settings)] == ["சர்வாலய தீபம்/Sarvalaya Deepam"]


def test_backnang_termine_mit_datum_und_ort(monkeypatch, settings):
    _seite(monkeypatch, "srimeenadchiambal_zukunft.html", "text/html; charset=UTF-8")
    items = sources.FETCHERS["html"](_ohne_auswahl(settings), settings)
    assert len(items) == 9
    assert [(i.title, i.facts["event_datum"]) for i in items[:4]] == [
        ("கந்தசஷ்டி 5ம் நாள்/Skandashashti is the 5th day", "2026-11-13"),
        ("கந்தசஷ்டி 6ம் நாள்/Skandashashti is the 6th day", "2026-11-14"),
        ("கந்தசஷ்டி விரத உபவாசம்/Skandashashti Fasting", "2026-11-15"),
        ("கந்தசஷ்டி விரதபூர்த்தி/Skandashashti Vratapoorthi", "2026-11-16"),
    ]
    assert items[-1].facts["event_datum"] == "2026-12-24"  # „Dezember 24, 2026“ (deutscher Monat, englische Form)
    for i in items:
        assert i.kind == "event" and i.source_published is None
        assert i.facts["event_ort"] == "Sri Meenadchi Ambal Tempel, Sulzbacher Str. 56, 71522 Backnang"
        assert i.ort == "Sri Meenadchi Ambal Tempel, Sulzbacher Str. 56, 71522 Backnang"
        assert i.url.startswith("https://srimeenadchiambal.com/events/")
    assert "November 16, 2026 9:30 a.m." in items[3].summary


def test_backnang_vergangener_termin_gilt_als_veraltet(monkeypatch, settings):
    """Die Seite zeigt nur Kommendes; bleibt ein Termin stehen, sortiert die Pipeline ihn nach dem Tag aus."""
    _seite(monkeypatch, "srimeenadchiambal_zukunft.html", "text/html; charset=UTF-8")
    items = sources.FETCHERS["html"](_ohne_auswahl(settings), settings)
    assert pipeline.stale_event_date(items[0], "", settings, now=STAND) == ""
    assert pipeline.stale_event_date(items[0], "", settings, now=datetime(2026, 12, 1, tzinfo=timezone.utc)) == "2026-11-13"
