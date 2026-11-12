"""Termin-Kalender aus der Inventur 11.11.2026, ohne Netz: Kalender-JSON des WordPress-Plugins „The Events Calendar“
(/wp-json/tribe/events/v1/events, Sri Navadurga Devi Tempel Wuppertal). Vergangene Termine fallen heraus;
Gedenktermine mit LTTE-Bezug (Maaveerar) werden nie automatisch zur Story ([blocklist] termine)."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from news_radar import filtering, sources
from news_radar.config import Source, load_settings

FIX = Path(__file__).parent / "fixtures"
VOR_DEM_FEST = datetime(2026, 5, 20, 9, tzinfo=timezone.utc)


class Antwort:
    def __init__(self, datei: str):
        self.status_code = 200
        self.content = (FIX / datei).read_bytes()
        self.headers = {"Content-Type": "application/json; charset=UTF-8"}

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


@pytest.fixture
def wuppertal(monkeypatch):
    aufrufe = []

    def get(url, **kw):
        aufrufe.append((url, kw.get("params")))
        return Antwort("tribe_events_wuppertal.json")

    monkeypatch.setattr(sources.requests, "get", get)
    quelle = Source(name="Sri Navadurga Devi Tempel Wuppertal · Termine", type="tribe_events",
                    url="https://hindutempel-wuppertal.de", country="DE", kind="event")
    return quelle, aufrufe


def test_events_calendar_liefert_nur_kommende_termine(settings, wuppertal):
    quelle, aufrufe = wuppertal
    items = sources.FETCHERS["tribe_events"](quelle, settings, now=VOR_DEM_FEST)
    assert aufrufe[0][0] == "https://hindutempel-wuppertal.de/wp-json/tribe/events/v1/events"
    assert aufrufe[0][1]["start_date"] == "2026-05-20"  # nur ab heute anfragen
    # Neujahr (1.1.) und Mesha Sankranti (14.4.) sind vorbei und fallen heraus
    assert [(i.title, i.facts["event_datum"]) for i in items] == [
        ("Santhi (vorläufige Aktivitäten des jährlichen Tempelfests)", "2026-05-21"),
        ("Prozessionsumzug Theer Thiruvila", "2026-05-30"),
        ("12. Tag des Tempelfestes", "2026-06-02"),
    ]  # „Maaveerar Poojai“ (27.11.) fehlt: Gedenktermin
    prozession = items[1]
    assert prozession.kind == "event" and prozession.facts["event_ort"] == "Sri Navathurgadevi Tempel, Hünefeldstraße 63B, Wuppertal"
    assert prozession.url == "https://hindutempel-wuppertal.de/event/prozessionsumzug-theer-thiruvila-2026/"
    assert "10:00" in prozession.summary and prozession.source_published is None


def test_nach_dem_fest_kommt_nichts_mehr(settings, wuppertal):
    quelle, _ = wuppertal
    items = sources.FETCHERS["tribe_events"](quelle, settings, now=datetime(2026, 11, 28, tzinfo=timezone.utc))
    assert items == []


def test_maaveerar_gedenken_wird_nie_automatisch_zur_story(settings, wuppertal):
    quelle, _ = wuppertal
    assert "maaveerar" in settings.blocklist_termine
    items = sources.FETCHERS["tribe_events"](quelle, settings, now=datetime(2026, 11, 20, tzinfo=timezone.utc))
    assert items == []  # einziger kommender Termin ist das Gedenken
    assert filtering.gedenktermin(sources.NewsItem("மாவீரர் நாள் 2026", "https://x.example/1", "", "q",
                                                   VOR_DEM_FEST, kind="event"), settings)
    assert not filtering.gedenktermin(sources.NewsItem("Tempelfest Tag 1", "https://x.example/3", "", "q",
                                                       VOR_DEM_FEST, kind="event"), settings)


def test_gedenk_sperre_gilt_nur_fuer_termine(settings):
    """Nachrichten über das Gedenken (Bericht, Polizei, Gericht) bleiben dem normalen Weg überlassen."""
    meldung = sources.NewsItem("Polizei prüft Maaveerar-Veranstaltung", "https://x.example/2", "", "q", VOR_DEM_FEST)
    assert not filtering.gedenktermin(meldung, settings)


@pytest.mark.parametrize("titel", ["Heroes' Day 2026", "Heroes’ Day in Hamm", "Mahaaveerar Thinam", "Māvīrar Nāḷ",
                                   "Heldengedenktag der Tamilen", "Maaveerar Naal", "மாவீரர் நாள் நினைவு",
                                   "National Heroes Day", "Tamilischer Heldentag"])
def test_gedenk_sperre_trifft_schreibweisen(settings, titel):
    """Prüfung von 28122c7: Apostrophe und Diakritika dürfen die Sperre nicht umgehen."""
    item = sources.NewsItem(titel, "https://x.example/g", "", "q", VOR_DEM_FEST, kind="event")
    assert filtering.gedenktermin(item, settings), titel


def _kalender(monkeypatch, events):
    import json

    class Roh(Antwort):
        def __init__(self):
            self.status_code, self.headers = 200, {"Content-Type": "application/json"}
            self.content = json.dumps({"events": events}).encode()

    monkeypatch.setattr(sources.requests, "get", lambda url, **kw: Roh())
    return Source(name="Kalender", type="tribe_events", url="https://tempel.example", country="DE", kind="event")


def test_laufender_mehrtaegiger_termin_bleibt(settings, monkeypatch):
    quelle = _kalender(monkeypatch, [{"title": "Tempelfest", "url": "https://tempel.example/fest/",
                                      "start_date": "2026-05-22 00:00:00", "end_date": "2026-06-02 23:59:59",
                                      "all_day": True}])
    items = sources.FETCHERS["tribe_events"](quelle, settings, now=datetime(2026, 5, 25, 9, tzinfo=timezone.utc))
    assert [i.title for i in items] == ["Tempelfest"]


def test_iso_datum_mit_t_wird_gelesen(settings, monkeypatch):
    quelle = _kalender(monkeypatch, [{"title": "Prozession", "url": "https://tempel.example/p/",
                                      "start_date": "2026-05-31T10:00:00", "all_day": False}])
    [item] = sources.FETCHERS["tribe_events"](quelle, settings, now=VOR_DEM_FEST)
    assert item.facts["event_datum"] == "2026-05-31" and "10:00" in item.summary


@pytest.mark.parametrize("titel", ["Maaveerar's Day", "Mahaveerar’s Naal", "Heroes’ Day"])
def test_gedenk_sperre_mit_besitz_s(settings, titel):
    item = sources.NewsItem(titel, "https://x.example/g", "", "q", VOR_DEM_FEST, kind="event")
    assert filtering.gedenktermin(item, settings), titel


def test_national_heroes_museum_ist_kein_gedenktermin(settings):
    item = sources.NewsItem("Ausflug ins National Heroes Museum", "https://x.example/m", "", "q", VOR_DEM_FEST,
                            kind="event")
    assert not filtering.gedenktermin(item, settings)


def test_kalender_nennt_ende_mehrtaegiger_termine(settings, monkeypatch):
    quelle = _kalender(monkeypatch, [{"title": "Tempelfest", "url": "https://tempel.example/fest/",
                                      "start_date": "2026-05-22 00:00:00", "end_date": "2026-06-02 23:59:59",
                                      "all_day": True}])
    [item] = sources.FETCHERS["tribe_events"](quelle, settings, now=datetime(2026, 5, 25, 9, tzinfo=timezone.utc))
    assert item.facts["event_ende"] == "2026-06-02" and "bis 02.06.2026" in item.summary


@pytest.mark.parametrize("titel", ["Tamil National Heroes Commemoration", "National Heroes Remembrance",
                                   "Heroes Remembrance Day", "மா\u200dவீரர் நாள்", "Maa\u00adveerar",
                                   "Maaveerars Day", "Maaveerarnaal", "Maavirar Naal", "Helden-Gedenktag 2026",
                                   "Ma\u200bveerar"])
def test_gedenk_sperre_runde_4_gesperrt(settings, titel):
    item = sources.NewsItem(titel, "https://x.example/g", "", "q", VOR_DEM_FEST, kind="event")
    assert filtering.gedenktermin(item, settings), titel


@pytest.mark.parametrize("titel", ["National Heroes Museum", "Helden der Kindheit", "Superheroes Day"])
def test_gedenk_sperre_runde_4_frei(settings, titel):
    item = sources.NewsItem(titel, "https://x.example/f", "", "q", VOR_DEM_FEST, kind="event")
    assert not filtering.gedenktermin(item, settings), titel


def test_kalender_ende_um_mitternacht_gehoert_zum_vortag(settings, monkeypatch):
    quelle = _kalender(monkeypatch, [{"title": "Abendpuja", "url": "https://tempel.example/abend/",
                                      "start_date": "2026-05-22 18:00:00", "end_date": "2026-05-23 00:00:00",
                                      "all_day": False},
                                     {"title": "Fest", "url": "https://tempel.example/fest2/",
                                      "start_date": "2026-05-22 00:00:00", "end_date": "2026-05-25 00:00:00",
                                      "all_day": True}])
    abend, fest = sources.FETCHERS["tribe_events"](quelle, settings, now=VOR_DEM_FEST)
    assert abend.facts["event_ende"] == "2026-05-22" and "bis" not in abend.summary
    assert fest.facts["event_ende"] == "2026-05-24" and "bis 24.05.2026" in fest.summary
