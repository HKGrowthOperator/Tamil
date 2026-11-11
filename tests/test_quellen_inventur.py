"""Quellen aus der Inventur 11.11.2026 gegen die an dem Tag gespeicherten Seiten (gekürzt) – ohne Netz.

Die Kino-Seiten (Anbieter "html") sind zurückgestellt (Prüfung 11.11.2026) und aus; ihre Fixture-Tests prüfen den
Anbieter mit fester Uhr, damit er bei einer späteren Wiederaufnahme belegt bleibt."""

from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from news_radar import filtering, quellencheck, sources
from news_radar import kino_providers as kp
from news_radar.config import Source, load_settings
from news_radar.kino_providers import Show

FIX = Path(__file__).parent / "fixtures"
TZ = kp.TZ
STAND = datetime(2026, 11, 11, 12, tzinfo=TZ)  # Abruf der Fixtures
KINO_HTML = ("Filmkunstkinos Düsseldorf · Kino aus Indien", "Mathäser Filmpalast München",
             "Babylon Berlin · IndoGerman Film", "dein-dein · Tamil Films in Germany")


class Antwort:
    def __init__(self, datei: str):
        self.status_code = 200
        self.content = (FIX / datei).read_bytes()
        self.headers = {"Content-Type": "text/html; charset=utf-8"}

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


def _seite(monkeypatch, datei):
    monkeypatch.setattr(sources.requests, "get", lambda url, **kw: Antwort(datei))


def test_kino_html_quellen_sind_zurueckgestellt(settings):
    for name in KINO_HTML:
        q = _quelle(settings, name)
        assert not q.enabled and "Kino-HTML-Weg zurückgestellt" in q.notiz, name
        assert q.type == "kino" and q.provider == "html" and q.selectors, name
    assert not any(q.provider == "html" for q in settings.sources)


def test_filmkunstkinos_nur_tamilische_vorstellungen(monkeypatch, settings):
    _seite(monkeypatch, "filmkunstkinos_indien.html")
    shows = kp.fetch_html_kino(_quelle(settings, "Filmkunstkinos Düsseldorf · Kino aus Indien"), settings, now=STAND)
    assert sorted(s.film for s in shows) == ["OM", "Sirai"]  # die Hindi-Vorstellung fällt heraus
    om = next(s for s in shows if s.film == "OM")
    assert om.start.strftime("%Y-%m-%d %H:%M") == "2026-11-21 12:00" and om.stadt == "Düsseldorf"
    assert om.url == "https://filmkunstkinos.de/filme/om-2026/"
    # ein Eintrag je Film und Kinowoche; „Sirai“ (10.01.2026) ist vorbei und fällt heraus
    items = kp.aggregate_shows(shows, now=datetime(2026, 11, 19, 9, tzinfo=TZ))
    assert [i.facts["film"] for i in items] == ["OM"] and items[0].kind == "kino"


def test_mathaeser_nur_der_tamilische_film(monkeypatch, settings):
    _seite(monkeypatch, "mathaeser_programm.html")
    shows = kp.fetch_html_kino(_quelle(settings, "Mathäser Filmpalast München"), settings, now=STAND)
    assert [s.film for s in shows] == ["Scene"] and shows[0].stadt == "München"
    assert shows[0].start.date() == date(2026, 11, 16)


def test_babylon_telugu_fassung_kommt_nicht_durch(monkeypatch, settings):
    _seite(monkeypatch, "babylon_indogerman.html")
    assert kp.fetch_html_kino(_quelle(settings, "Babylon Berlin · IndoGerman Film"), settings, now=STAND) == []


def test_dein_dein_aus_bis_luis_entscheidet(monkeypatch, settings):
    q = _quelle(settings, "dein-dein · Tamil Films in Germany")
    assert not q.enabled and "KI-Crawler" in q.notiz
    _seite(monkeypatch, "deindein_tamil_films.html")
    shows = kp.fetch_html_kino(q, settings, now=STAND)
    assert [s.film for s in shows] == ["Scene", "Ramayana: Rise of a Legend", "OM: Chapter 1"]
    assert shows[0].stadt == "Nuremberg"


@pytest.mark.xfail(strict=True, reason="film_key bleibt unverändert (Prüfung 11.11.2026): Abschneiden nach „:“/„ - “ "
                   "legte verschiedene Filme zusammen (Ponniyin Selvan: Part 1/2, KGF: Chapter 1/2)")
def test_derselbe_film_aus_drei_quellen_ist_ein_kino_eintrag():
    """Live 11.11.: „OM“ (Filmkunstkinos), „OM: Chapter 1“ (dein-dein), „IndoGerman Film: OM - Chapter 1: Udhiram …“
    (Babylon) – derselbe Film in derselben Kinowoche → ein Eintrag mit drei Kinos, nicht drei Storys."""
    titel = ["OM", "OM: Chapter 1", "IndoGerman Film: OM - Chapter 1: Udhiram - The Blood Wood"]
    assert len({kp.film_key(t) for t in titel}) == 1
    shows = [
        Show("OM", "Atelier", "Düsseldorf", "DE", start=datetime(2026, 11, 21, 12, tzinfo=TZ), provider="html"),
        Show("OM: Chapter 1", "Filmpalast Hofheim", "Hofheim", "DE", start=datetime(2026, 11, 20, 19, tzinfo=TZ)),
        Show(titel[2], "Babylon", "Berlin", "DE", start=datetime(2026, 11, 21, 13, tzinfo=TZ)),
    ]
    now = datetime(2026, 11, 19, 9, tzinfo=TZ)
    getrennt = [it for s in shows for it in kp.aggregate_shows([s], now=now)]  # wie aus drei Quellen
    items = kp.merge_kino_items(getrennt)
    assert len(items) == 1 and len(items[0].facts["kinos"]) == 3
    assert kp.film_key("Jailer 2") != kp.film_key("Jailer")  # Fortsetzungen bleiben getrennt


def test_tamilsco_termine(monkeypatch, settings):
    _seite(monkeypatch, "tamilsco_germany.html")
    items = sources.fetch_html(_quelle(settings, "Tamils.co · Termine Deutschland"), settings)
    assert [i.facts["event_datum"] for i in items] == ["2026-11-21", "2026-12-09", "2027-06-20"]
    picked = filtering.select(items, settings, set(), [], now=datetime(2026, 11, 11, tzinfo=timezone.utc))
    assert len(picked) == 2  # max_items 2


def _meldung(titel, text):
    return sources.NewsItem(title=titel, url=f"https://www.admin.ch/de/newnsb/{len(titel)}", summary=text,
                            source="SEM · Medienmitteilungen", published=datetime(2026, 11, 11, 8, tzinfo=timezone.utc))


def test_sem_braucht_mehr_als_einmal_sri_lanka(settings):
    assert _quelle(settings, "SEM · Medienmitteilungen").min_score == 4
    beilaeufig = _meldung("Asylstatistik Oktober 2026",
                          "Die meisten Gesuche kamen aus Afghanistan, der Türkei, Eritrea und Sri Lanka.")
    klar = _meldung("Rückkehr nach Sri Lanka: Bund und Kantone werten Wegweisungen aus",
                    "Das SEM hat die Rückkehrpraxis für Asylsuchende aus Sri Lanka überprüft.")
    picked = filtering.select([beilaeufig, klar], settings, set(), [],
                              now=datetime(2026, 11, 11, 12, tzinfo=timezone.utc))
    assert [i.title for i in picked] == [klar.title]


def test_quellen_pruefen_warnt_vor_veralteter_jahreszahl(monkeypatch, settings):
    url = "https://filmkunstkinos.de/specials/filmreihe-kino-aus-indien-2026/"
    assert "2026" in quellencheck.jahr_warnung(url, 2027)
    assert quellencheck.jahr_warnung(url, 2026) == ""
    assert quellencheck.jahr_warnung("https://www.newsd.admin.ch/newsd/feeds/rss?lang=de&org-nr=405", 2027) == ""
    monkeypatch.setattr(sources, "fetch_source", lambda s, st: [])
    monkeypatch.setattr(quellencheck, "robots_status", lambda url: "erlaubt")
    src = Source(name="Reihe", type="html", url="https://example.com/reihe-2026/")
    p = quellencheck.pruefe_quelle(src, settings, None, datetime(2027, 1, 5, tzinfo=timezone.utc))
    assert "2026" in p.warnung


def test_film_key_legt_verschiedene_filme_nicht_zusammen():
    """Prüfung 11.11.2026: Teile einer Reihe und Vorpremieren sind eigene Filme (eigene Kino-Storys)."""
    assert kp.film_key("Ponniyin Selvan: Part 1") != kp.film_key("Ponniyin Selvan: Part 2")
    assert kp.film_key("KGF: Chapter 1") != kp.film_key("KGF: Chapter 2")
    assert kp.film_key("Sneak Preview: Coolie") != kp.film_key("Sneak Preview: Jailer 2")
