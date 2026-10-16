from datetime import datetime, timedelta, timezone

import pytest

from news_radar import filtering
from news_radar.config import Source, load_settings
from news_radar.sources import NewsItem

NOW = datetime(2026, 10, 16, 12, tzinfo=timezone.utc)


@pytest.fixture
def settings(monkeypatch):
    monkeypatch.setenv("WP_USER", "")
    return load_settings()


def item(title, summary="", source="Test", hours_old=1, **kw):
    return NewsItem(title=title, url=f"https://e.com/{abs(hash(title))}", summary=summary, source=source,
                    published=NOW - timedelta(hours=hours_old), **kw)


def test_dach_score_title_city_wins(settings):
    assert filtering.dach_score(item("Tamilen in Paderborn feiern", "auch in Köln"), settings.regions) == (4, "Paderborn")
    assert filtering.dach_score(item("Pongal-Fest", "Tempel in Hamm, Deutschland"), settings.regions) == (2, "Hamm")
    assert filtering.dach_score(item("Tamil film", "shown in Zurich"), settings.regions)[1] == "Zürich"
    assert filtering.dach_score(item("Neues aus Chennai", "Indien"), settings.regions) == (0, "")


def test_exact_terms_case_sensitive(settings):
    assert filtering.dach_score(item("Wir essen tamilisch", "bern ist kein ort"), settings.regions) == (0, "")
    assert filtering.dach_score(item("Tempelfest in Essen", ""), settings.regions) == (3, "Essen")


def test_tamil_terms_substring(settings):
    assert filtering.score_item(item("தமிழர்கள் சுவிஸ்"), {"தமிழ்": 3, "சுவிஸ்": 3}) == 12
    assert filtering.dach_score(item("சுவிஸ் தமிழர் தகவல்"), settings.regions) == (1, "Schweiz")


def test_select_two_tier_threshold(settings):
    with_dach = item("Tamilischer Abend in Luzern", "Kultur")  # tamilisch 8 + Luzern
    without = item("Tamilischer Abend", "Kultur irgendwo")  # tamilisch 8 → reicht auch ohne DACH (min_score 4)
    weak_dach = item("Konzert in Luzern", "tamil Musik")  # konzert 2 + tamil 3 = 5? -> tamil im Text 3, konzert Titel 2 = 5
    weak_nodach = item("Konzert", "tamil Musik")  # 2+3 = 5 ≥ 4 → passt
    very_weak_dach = item("Fest in Luzern", "mit Musik")  # 0 Punkte, DACH → reicht nicht (min_score_dach 2)
    picked = filtering.select([with_dach, without, weak_dach, weak_nodach, very_weak_dach], settings, set(), [], now=NOW)
    titles = [p.title for p in picked]
    assert very_weak_dach.title not in titles and with_dach.title in titles
    assert titles[0] == with_dach.title  # DACH zuerst
    assert picked[0].dach_score == 3 and picked[0].ort == "Luzern"


def test_select_bypasses_keywords_for_kino_and_event_kind(settings):
    kino = item("„Jailer 2“ läuft in 3 Kinos", "CineStar Mainz", source="CineStar", kind="kino", hours_old=0)
    event = item("Vaango Pazhagalam", "Basel", source="tamilswiss.ch Events", kind="event", hours_old=100)
    picked = filtering.select([kino, event], settings, set(), [], now=NOW)
    assert {p.title for p in picked} == {kino.title, event.title}
    assert next(p for p in picked if p.kind == "kino").category_hint == "kino"
    assert next(p for p in picked if p.kind == "event").ort == "Basel"  # Stadt aus dem Text schlägt die Länder-Vorgabe
    only_country = item("Tamil Dream Night", "irgendwo", source="tamilswiss.ch Events", kind="event")
    assert filtering.select([only_country], settings, set(), [], now=NOW)[0].ort == "Schweiz"


def test_select_keeps_related_sources_and_respects_max_items(settings):
    a = item("Anirudh live in Köln: Tickets ab Freitag", "tamil", source="Google News DACH · WAZ")
    b = item("Anirudh live in Köln - Tickets ab Freitag!", "tamil", source="Google News DACH · Express")
    picked = filtering.select([a, b], settings, set(), [], now=NOW)
    assert len(picked) == 1 and picked[0].related[0].source.endswith("Express")

    settings.sources = [Source(name="Tamil-Portal", type="rss", url="https://x", min_score=0, max_items=2, kind="news")]
    items = [item(t, "ohne Stichwort", source="Tamil-Portal") for t in ("Pongal", "Deepavali", "Thaipusam", "Navaratri", "Theruvizha")]
    assert len(filtering.select(items, settings, set(), [], now=NOW)) == 2


def test_select_filters_old_blocked_seen_and_blocklist(settings):
    old = item("Tamilen in Berlin", hours_old=200)
    blocked = item("Tamil casino bonus Berlin", "tamil")
    seen = item("Tamilen in Hamburg")
    picked = filtering.select([old, blocked, seen], settings, {seen.uid}, [], now=NOW)
    assert picked == []
