"""Kinoprogramme: Tamil-Vorstellungen erkennen, je Film und Kinowoche bündeln, Anbieter zusammenführen."""

import json
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from news_radar import kino_providers as kp
from news_radar.config import Source, load_settings

FIX = Path(__file__).parent / "fixtures"
NOW = datetime(2026, 10, 16, 12, tzinfo=timezone.utc)  # Freitag, Kinowoche 2026-W42 (Do 15.10.–Mi 21.10.)


class FakeHttp:
    def __init__(self, routes):
        self.routes = routes

    def _resp(self, data):
        class R:
            status_code = 200

            def json(self_inner):
                return data

            def raise_for_status(self_inner):
                pass

        return R()

    def get(self, url, **kw):
        for key, path in self.routes.items():
            if key in url:
                return self._resp(json.loads((FIX / path).read_text(encoding="utf-8")))
        raise AssertionError(f"unerwartete URL {url}")

    def post(self, url, **kw):
        return self._resp(json.loads((FIX / self.routes["graphql"]).read_text(encoding="utf-8")))


@pytest.fixture
def settings(monkeypatch):
    monkeypatch.setenv("WP_USER", "")
    return load_settings()


def test_clean_title_and_film_key():
    assert kp.clean_film_title("Jailer 2 (Tamil OmeU)") == "Jailer 2"
    assert kp.clean_film_title("(tamil) Ramayana: Rise Of A Legend") == "Ramayana: Rise Of A Legend"
    assert kp.clean_film_title("*Jailer 2") == "Jailer 2"
    assert kp.clean_film_title("Jailer 2 | indisches Kino | with english subtitles , ab 18") == "Jailer 2"
    assert kp.film_key("Jailer 2 (Tamil OmeU)") == kp.film_key("(tamil) Jailer 2") == "jailer-2"


def test_kino_week_thursday_to_wednesday():
    assert kp.kino_week(date(2026, 10, 15)) == kp.kino_week(date(2026, 10, 21)) == (2026, 42)
    assert kp.kino_week(date(2026, 10, 22)) == (2026, 43)
    assert kp.kino_week(date(2026, 10, 14)) == (2026, 41)


def test_cinestar_filters_tamil_and_aggregates(settings):
    http = FakeHttp({"/api/cinema/12/show/": "cinestar_shows_12.json", "/api/cinema/15/show/": "cinestar_shows_15.json",
                     "/api/cinema/30/show/": "cinestar_shows_30.json", "/api/cinema/1/show/": "cinestar_shows_12.json",
                     "/api/cinema/": "cinestar_cinemas.json"})
    src = Source(name="CineStar", type="kino", provider="cinestar", params={"cinemas": [12, 15, 30]})
    shows = kp.fetch_cinestar(src, settings, http=http)
    assert {s.kino for s in shows} == {"CineStar Bremen - Kristall-Palast", "CineStar Dortmund", "CineStar Karlsruhe"} or len(shows) == 3
    assert all(s.land == "DE" and "Jailer 2" in s.film for s in shows)
    items = kp.aggregate_shows(shows, NOW)
    assert len(items) >= 1
    week42 = next(i for i in items if i.facts["woche"] == "2026-W42")
    assert week42.kind == "kino" and week42.uid.startswith("kino:") and "Kinos" in week42.title
    assert len(week42.facts["kinos"]) == 3 and week42.facts["kinos"][0]["stadt"] <= week42.facts["kinos"][1]["stadt"]


def test_kinoheld_parses_shows(settings):
    http = FakeHttp({"graphql": "kinoheld_search.json"})
    shows = kp.fetch_kinoheld(Source(name="kinoheld", type="kino", provider="kinoheld"), settings, http=http)
    assert len(shows) == 6 and shows[0].stadt == "Pforzheim" and shows[0].start.year == 2026
    assert {s.film for s in shows} == {"Jailer 2", "Ramayana: Rise Of A Legend"}
    items = kp.aggregate_shows(shows, NOW)
    jailer = next(i for i in items if i.facts["film"] == "Jailer 2")
    assert jailer.facts["kinos"][0]["kino"] == "Cinemoon Pforzheim" and len(jailer.facts["kinos"][0]["termine"]) >= 2


def test_cineplexx_austria(settings):
    http = FakeHttp({"/api/v2/movies": "cineplexx_movies.json", "/api/v1/cinemas": "cineplexx_cinemas.json"})
    shows = kp.fetch_cineplexx(Source(name="Cineplexx", type="kino", provider="cineplexx"), settings, http=http)
    assert [(s.kino, s.stadt, s.land) for s in shows] == [("Annenhof Kino", "Graz", "AT"), ("Cineplexx Millennium City", "Wien", "AT")]
    assert shows[0].von == date(2026, 10, 16) and shows[0].url == "https://www.cineplexx.at/film/jailer-2"
    items = kp.aggregate_shows(shows, NOW)
    assert any(i.facts["woche"] == "2026-W42" for i in items) and items[0].facts["kinos"][0]["von"] == "2026-10-16"


def test_merge_across_providers_same_uid_and_fingerprint_changes(settings):
    a = kp.aggregate_shows([kp.Show("Jailer 2", "CineStar Mainz", "Mainz", "DE", start=datetime(2026, 10, 17, 19, 30, tzinfo=kp.TZ))], NOW)
    b = kp.aggregate_shows([kp.Show("(tamil) Jailer 2", "Savoy", "Hamburg", "DE", start=datetime(2026, 10, 18, 20, 0, tzinfo=kp.TZ))], NOW)
    assert a[0].uid == b[0].uid and a[0].fingerprint != b[0].fingerprint
    merged = kp.merge_kino_items(a + b)
    assert len(merged) == 1 and [k["stadt"] for k in merged[0].facts["kinos"]] == ["Hamburg", "Mainz"]
    assert "2 Kinos: Hamburg, Mainz" in merged[0].title
    again = kp.merge_kino_items(merged + kp.aggregate_shows([kp.Show("Jailer 2", "Savoy", "Hamburg", "DE", start=datetime(2026, 10, 18, 20, 0, tzinfo=kp.TZ))], NOW))
    assert len(again[0].facts["kinos"]) == 2


def test_next_week_item_and_old_shows_ignored():
    shows = [kp.Show("Ramayana", "Colosseum", "Berlin", "DE", start=datetime(2026, 10, 23, 19, 0, tzinfo=kp.TZ)),
             kp.Show("Alt", "Kino", "Köln", "DE", start=datetime(2026, 9, 1, 19, 0, tzinfo=kp.TZ))]
    items = kp.aggregate_shows(shows, NOW)
    assert [i.facts["woche"] for i in items] == ["2026-W43"]
