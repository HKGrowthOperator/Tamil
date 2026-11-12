"""Quellen-Registry, Feeds, HTML-Selektoren, WordPress-REST, Google-News-Rotation, Zeitbudget – alles ohne Netz."""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from news_radar import dates, sources
from news_radar.config import Source, load_settings

FIX = Path(__file__).parent / "fixtures"


class FakeResponse:
    def __init__(self, path: Path | None = None, status: int = 200, data=None):
        self.status_code = status
        self.content = path.read_bytes() if path else b""
        self.text = self.content.decode("utf-8", "replace")
        self._data = data

    def json(self):
        return self._data if self._data is not None else json.loads(self.text)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    headers: dict = {}

    def iter_content(self, size):
        yield self.content

    def close(self):
        pass


@pytest.fixture
def settings(monkeypatch):
    for var in ("WP_USER", "WP_APP_PASSWORD", "NEWSAPI_KEY", "GNEWS_TOKEN"):
        monkeypatch.setenv(var, "")
    return load_settings()


def test_extract_paragraphs_drops_theme_code_and_navigation():
    html = """
    <html><head><style>.tdi_9{vertical-align:baseline}</style><script>var x = {a: 1};</script></head>
    <body><nav><p>Menu Startseite Nachrichten Schweiz Events Suche Suche nach: Suche Swiss Tamil Events Weiter</p></nav>
    <p>.tdb_header_logo{margin-bottom:0;clear:none}.tdb_header_logo .tdb-logo-a{display:flex;pointer-events:auto}</p>
    <p>{"@context":"http://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1}]}</p>
    <article><p>Die tamilische Gemeinschaft in Basel lädt am 24. Oktober 2026 zu Workshops, Kulturständen und Bühnenbeiträgen ein.</p>
    <p>kurz</p>
    <p>Das Event richtet sich an Menschen aller Nationalitäten und Altersgruppen, der Eintritt ist frei und Essen gibt es auch.</p></article>
    <footer><p>Als Nonprofit-Organisation sind wir weiterhin auf Spenden angewiesen und danken allen Helferinnen und Helfern.</p></footer>
    </body></html>"""
    text = sources.extract_paragraphs(html)
    assert text.startswith("Die tamilische Gemeinschaft in Basel")
    assert "Eintritt ist frei" in text and "tdb_header_logo" not in text and "@context" not in text
    assert "Spenden" not in text and "Menu" not in text and "kurz" not in text


def test_registry_contains_all_types():
    assert set(sources.FETCHERS) == {"rss", "newsapi", "gnews", "gnews_region", "wp_json", "html", "kino", "tribe_events"}


def test_rss_uses_entry_source_as_publisher(monkeypatch):
    monkeypatch.setattr(sources.requests, "get", lambda url, **kw: FakeResponse(FIX / "gnews_de.xml"))
    items = sources.fetch_rss(Source(name="Google News DE", type="rss", url="https://x"), None)
    assert len(items) == 1 and items[0].source == "Google News DE · Hamburger Abendblatt"
    assert items[0].published.tzinfo is not None and items[0].title.endswith("Hamburger Abendblatt")


def test_tamil_feed_keeps_tamil_title_and_event_kind(monkeypatch):
    monkeypatch.setattr(sources.requests, "get", lambda url, **kw: FakeResponse(FIX / "swisstamilmedia_events.xml"))
    src = Source(name="SwissTamilMedia", type="rss", url="https://x", language="ta", kind="event")
    items = sources.fetch_rss(src, None)
    assert len(items) == 2 and items[0].kind == "event" and items[0].language == "ta"
    assert "சுவிட்சர்லாந்தில்" in items[0].title


def test_feed_keeps_real_date_for_event_sources():
    """Fund 09.11.: Termin-Quellen bekamen als Datum den Abrufzeitpunkt – alte Berichte aus dem Archiv der Rubrik
    sahen frisch aus. `published` bleibt der Abrufzeitpunkt (Sortierung), das echte Datum steht daneben."""
    now = datetime(2026, 11, 9, 20, tzinfo=timezone.utc)
    events = Source(name="Swiss Tamil Info · Events", type="rss", url="https://x", language="ta", kind="event")
    items = sources._feed_items((FIX / "swisstamilinfo_events.xml").read_bytes(), events, now=now)
    assert [i.url.rsplit("/", 2)[-2] for i in items] == ["22670", "27129", "22741", "22541", "22051"]
    assert all(i.published == now for i in items)
    assert items[0].source_published == datetime(2026, 7, 12, tzinfo=timezone.utc)
    assert items[1].source_published == datetime(2026, 10, 11, tzinfo=timezone.utc)
    assert items[2].source_published is None  # Feed ohne Datum: unbekannt, nicht der Abrufzeitpunkt

    news = Source(name="Swiss Tamil Info · Schweiz", type="rss", url="https://x", language="ta")
    meldung = sources._feed_items((FIX / "swisstamilinfo_schweiz.xml").read_bytes(), news, now=now)[0]
    assert meldung.published == meldung.source_published == datetime(2026, 11, 9, 15, tzinfo=timezone.utc)


def test_fetch_html_with_selectors(monkeypatch, settings):
    monkeypatch.setattr(sources.requests, "get", lambda url, **kw: FakeResponse(FIX / "eventfrog_search.html"))
    src = next(s for s in settings.sources if s.name == "Eventfrog CH")
    items = sources.fetch_html(src, settings)
    assert len(items) == 2
    first = items[0]
    assert first.url.startswith("https://eventfrog.ch/de/p/") and first.kind == "event"
    assert first.facts["event_datum"].startswith("20") and first.facts["event_datum"].endswith("-10-17")
    assert "Uzwil" in first.ort and "Jeiler 2" in first.title


def test_fetch_html_json_attribute(monkeypatch, settings):
    monkeypatch.setattr(sources.requests, "get", lambda url, **kw: FakeResponse(FIX / "tamilswiss_events.html"))
    src = next(s for s in settings.alle_quellen if s.name == "tamilswiss.ch Events")
    items = sources.fetch_html(src, settings)
    assert [i.title for i in items] == ["Vaango Pazhagalam 2.0", "Beat Your Heart 2026"]
    assert items[0].url == "https://tamilswiss.ch/event/vaango-pazhagalam-2-0-bs-f9c6"
    assert items[0].facts["event_datum"] == "2026-10-24" and items[0].ort == "Basel" and items[1].ort == ""


def test_fetch_wp_json_maps_fields(monkeypatch, settings):
    calls = []

    def fake_get(url, **kw):
        calls.append((url, kw.get("params")))
        return FakeResponse(FIX / "hdr_bern_mec_events.json")

    monkeypatch.setattr(sources.requests, "get", fake_get)
    src = next(s for s in settings.sources if s.name == "Haus der Religionen Bern")
    items = sources.fetch_wp_json(src, settings)
    assert calls[0][0].endswith("/wp-json/wp/v2/mec-events") and calls[0][1]["search"] == "Saivanerikoodam"
    assert len(items) == 2 and items[0].kind == "event" and items[0].title.startswith("Verein Saivanerikoodam")
    assert "Murugan" in items[0].summary and items[0].url.startswith("https://haus-der-religionen.ch/events/")
    # Kalendereintrag (eigener Beitragstyp): date_gmt ist das Anlagedatum, kein Veröffentlichungsdatum eines Berichts
    assert items[0].source_published is None
    artikel = Source(name="Portal", type="wp_json", url="https://x", endpoint="posts", kind="event")
    assert sources.fetch_wp_json(artikel, settings)[0].source_published == datetime(2026, 2, 12, 7, 24, 21,
                                                                                   tzinfo=timezone.utc)


def test_parse_de_date():
    now = datetime(2026, 10, 16, tzinfo=dates.TZ)
    assert dates.parse_de_date("7. November 2026", now).isoformat() == "2026-11-07"
    assert dates.parse_de_date("07.11.26", now).isoformat() == "2026-11-07"
    assert dates.parse_de_datetime("Sa, 7.11.2026 19:30", now).strftime("%Y-%m-%d %H:%M") == "2026-11-07 19:30"
    assert dates.parse_de_datetime("Samstag, 17. Oktober, 23:15", now).strftime("%Y-%m-%d %H:%M") == "2026-10-17 23:15"
    assert dates.parse_de_date("Okt 17", now).isoformat() == "2026-10-17"
    assert dates.parse_de_date("Jan 5", now).isoformat() == "2027-01-05"  # ohne Jahr: nächstes Datum
    assert dates.parse_de_date("2026-12-01T10:00", now).isoformat() == "2026-12-01"
    assert dates.parse_de_date("morgen 20 Uhr", now).isoformat() == "2026-10-17"
    assert dates.parse_de_date("Saturday, October 24, 2026", now).isoformat() == "2026-10-24"
    assert dates.parse_de_date("keine Angabe", now) is None


def test_region_queries_and_rotation(settings):
    src = next(s for s in settings.sources if s.type == "gnews_region")
    urls = sources.region_queries(src, settings)
    assert len(urls) == 32 and all("when%3A2d" in u for u in urls)
    assert "gl=DE&ceid=DE:de" in urls[0] and "hl=en&gl=CH" in urls[4] and "Berlin" in urls[6]
    covered = set()
    for minute in range(0, 18, 3):
        picks = sources.rotation(32, 6, minute)
        assert len(picks) <= 6
        covered |= set(picks)
    assert covered == set(range(32))
    assert sources.rotation(4, 6, 99) == [0, 1, 2, 3]


def test_gnews_region_fetches_only_a_slice(monkeypatch, settings):
    urls = []

    def fake_get(url, **kw):
        urls.append(url)
        return FakeResponse(FIX / "gnews_de.xml")

    monkeypatch.setattr(sources.requests, "get", fake_get)
    monkeypatch.setattr(sources.time, "sleep", lambda s: None)
    src = next(s for s in settings.sources if s.type == "gnews_region")
    items = sources.fetch_gnews_region(src, settings)
    assert 1 <= len(urls) <= 6 and len(items) == 1  # gleiche Meldung aus allen Abfragen nur einmal


def test_get_raises_rate_limited(monkeypatch):
    monkeypatch.setattr(sources.requests, "get", lambda url, **kw: FakeResponse(status=429))
    with pytest.raises(sources.RateLimited):
        sources._get("https://news.google.com/rss/x")


def test_fetch_all_skips_interval_and_paused_sources(monkeypatch, settings, tmp_path):
    from news_radar.store import Store

    store = Store(tmp_path / "r.sqlite")
    settings.sources = [
        Source(name="A", type="rss", url="https://a"),
        Source(name="B", type="rss", url="https://b", interval_minutes=60),
        Source(name="C", type="rss", url="https://c"),
    ]
    store.source_ok("B", 5)
    store.source_failed("C", "429", pause_minutes=30)
    called = []

    def fake_fetch(source, s):
        called.append(source.name)
        return []

    monkeypatch.setitem(sources.FETCHERS, "rss", fake_fetch)
    sources.fetch_all(settings, store)
    assert called == ["A"]
    store.close()


def test_fetch_all_respects_budget_and_records_status(monkeypatch, settings, tmp_path):
    from news_radar.store import Store

    store = Store(tmp_path / "r.sqlite")
    settings.fetch_seconds = 1
    settings.sources = [Source(name="schnell", type="rss", url="https://a"), Source(name="lahm", type="rss", url="https://b"),
                        Source(name="kaputt", type="rss", url="https://c")]
    now = datetime.now(timezone.utc)

    def fake_fetch(source, s):
        if source.name == "lahm":
            time.sleep(3)
        if source.name == "kaputt":
            raise RuntimeError("HTTP 500")
        return [sources.NewsItem("t", "https://a/1", "", source.name, now)]

    monkeypatch.setitem(sources.FETCHERS, "rss", fake_fetch)
    t0 = time.monotonic()
    items = sources.fetch_all(settings, store)
    assert time.monotonic() - t0 < 2.5 and [i.source for i in items] == ["schnell"]
    status = {s["name"]: s for s in store.source_status_all()}
    assert status["schnell"]["last_count"] == 1 and "500" in status["kaputt"]["error_msg"]
    store.close()


# ---- extract_paragraphs: linear statt Regex über die ganze Seite (Fund aus der Code-Prüfung) --------------

def _alt_extract(html_text: str, limit: int = 6000) -> str:
    """Die bisherige Fassung (Regex über die Rohseite) – nur als Vergleich für normale Seiten."""
    import re

    rausch = re.compile(r"<(script|style|noscript|template|svg|nav|header|footer|aside|form)\b[^>]*>.*?</\1\s*>",
                        re.S | re.I)
    body = rausch.sub(" ", html_text)
    m = re.search(r"<article\b[^>]*>(.*?)</article\s*>", body, flags=re.S | re.I)
    if m and len(m.group(1)) > 400:
        body = m.group(1)
    out = []
    for raw in re.findall(r"<p[^>]*>(.*?)</p>", body, flags=re.S | re.I):
        p = sources.clean_text(raw)
        if len(p) <= 60 or len(p) > 3000:
            continue
        if len(sources._CODE_HINT_RE.findall(p)) >= 2 or p.count("{") + p.count("}") >= 4:
            continue
        out.append(p)
    return "\n".join(out)[:limit]


def _echte_seiten() -> list[str]:
    import json

    ordner = Path(__file__).parent / "fixtures"
    seiten = [(ordner / f).read_text(encoding="utf-8")
              for f in ("tamil_home.html", "tamilswiss_events.html", "eventfrog_search.html")]
    posts = json.loads((ordner / "alt_export" / "posts.json").read_text(encoding="utf-8"))
    for post in posts:  # Beiträge der alten tamil.de, eingebettet in eine Seite mit typischem Rauschen
        inhalt = post["content"]["rendered"]
        seiten.append(inhalt)
        seiten.append(
            "<html><head><style>p{color:red}</style><script>var a='<p>kein Absatz</p>';</script>"
            "<script type='application/ld+json'>{\"@context\":\"https://schema.org\"}</script></head><body>"
            "<HEADER class=k><nav><ul><li><p>Menü mit einem ausreichend langen Text, der nicht zählen darf.</p></li>"
            "</ul></nav></HEADER ><svg><path d='M0'/></svg >"
            f"<article class='post'>{inhalt}<form><p>Kommentar schreiben und dabei einen langen Text eingeben, "
            "der nicht in die Absätze gehört.</p></form ></article><aside><p>Weitere Beiträge aus der Rubrik mit "
            "einem langen Teaser, der ebenfalls verschwinden muss.</p></aside><footer>© tamil.de</footer></body>"
            "</html>")
    return seiten


def test_extract_paragraphs_gleich_wie_bisher_auf_echten_seiten():
    seiten = _echte_seiten()
    assert len(seiten) >= 6 and any(_alt_extract(s) for s in seiten)
    for seite in seiten:
        assert sources.extract_paragraphs(seite) == _alt_extract(seite)
        assert sources.extract_paragraphs(seite, 300) == _alt_extract(seite, 300)


_ABSATZ = "<p>Dies ist ein langer Absatz mit genug Text, damit er die Mindestlänge sicher überschreitet.</p>"
_TUERKISCH = {  # „İ“.lower() hat zwei Zeichen: Positionen aus einer kleingeschriebenen Kopie verrutschen
    "i-im-absatz": "<p>Präsident Erdoğan besuchte heute İstanbul und traf dort Vertreter der Gemeinde.</p>"
                   "<p>Zweiter Absatz mit genügend Text, damit er sicher über der Mindestlänge liegt, heute.</p>",
    "i-in-navigation": "<nav>" + "İzmir İstanbul " * 50 + "</nav>" + _ABSATZ * 3,
    "i-vor-artikel": "İ" * 600 + "<article>" + _ABSATZ * 8 + "</article>",
    "i-vor-skript": "İ" * 300 + "<script>var a='<p>kein Absatz, aber lang genug um zu zählen, falls er durchrutscht</p>';"
                    "</script>" + _ABSATZ * 2,
}


_OHNE_SCHLUSS = {  # Rauschblöcke ohne passenden Schluss: wie bisher überspringen, der Rest der Seite bleibt
    "custom-nav-element": "<nav-menu><a>x</a></nav-menu>" + _ABSATZ * 3,
    "header-component": "<header-component>m</header-component><main>" + _ABSATZ * 3 + "</main>",
    "form-field": "<form-field name=a></form-field>" + _ABSATZ * 3,
    "aside-panel": "<aside-panel>x</aside-panel>" + _ABSATZ * 3,
    "svg-icon": "<svg-icon name=x></svg-icon>" + _ABSATZ * 3,
    "kommentar-nav": "<!-- <nav> alt --> " + _ABSATZ * 3,
    "form-im-attribut": "<div data-t='<form'>x</div>" + _ABSATZ * 3,
    "svg-selbstschliessend": "<svg/>" + _ABSATZ * 3,
    "offenes-skript-dann-style": "<script>offen " + _ABSATZ + "<style>a{}</style>" + _ABSATZ * 2,
    "nav-menu-dann-nav": "<nav-menu>" + _ABSATZ + "</nav>" + _ABSATZ * 2,
    "verschachtelt": "<header><nav>a</nav>b</header>" + _ABSATZ * 2,
    "leerraum-im-schluss": "<script >x</script >" + _ABSATZ,
    "scriptx": "<scriptx>a</scriptx>" + _ABSATZ,
    "gross": "<NAV>n</NAV><P>" + "Langer Text " * 10 + "</P>",
    "offener-absatz": "<p>offen ohne Schluss " + _ABSATZ * 2,
}


@pytest.mark.parametrize("name", sorted(_OHNE_SCHLUSS))
def test_extract_paragraphs_ohne_schluss_wie_bisher(name):
    seite = _OHNE_SCHLUSS[name]
    assert sources.extract_paragraphs(seite) == _alt_extract(seite)


@pytest.mark.parametrize("name", sorted(_TUERKISCH))
def test_extract_paragraphs_mit_tuerkischem_i_wie_bisher(name):
    seite = _TUERKISCH[name]
    assert _alt_extract(seite) and sources.extract_paragraphs(seite) == _alt_extract(seite)


def test_extract_paragraphs_linear_bei_nicht_geschlossenen_tags():
    import time

    for roh in ('<script type="application/ld+json">{"a":1}' * 10000,  # ~420 KB, nie geschlossen
                "<p>offen " * 50000, "<article>offen " * 30000, "<script " * 60000):
        t = time.monotonic()
        sources.extract_paragraphs(roh, 20000)
        assert time.monotonic() - t < 1, roh[:30]
    # ein nicht geschlossener Rauschblock wird wie bisher übersprungen, der Rest der Seite bleibt
    seite = ("<p>" + "Echter Absatz mit genug Text für die Mindestlänge. " * 2 + "</p><script>var x = '<p>"
             + "Absatz nach offenem Skript. " * 4 + "</p>'")
    assert sources.extract_paragraphs(seite) == _alt_extract(seite) and "nach offenem Skript" in _alt_extract(seite)
    for roh in ("<script x" * 60000 + ">", "<nav>" * 60000):  # „>“ erst am Ende bzw. nie ein Schluss
        t = time.monotonic()
        sources.extract_paragraphs(roh)
        assert time.monotonic() - t < 1, roh[:20]
