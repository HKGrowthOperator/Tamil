from datetime import datetime, timezone

import pytest

from news_radar import render
from news_radar.config import load_settings
from news_radar.sources import NewsItem
from news_radar.writer import Draft, _schema, build_rewrite_message, build_system, build_user_message


@pytest.fixture
def settings(monkeypatch):
    for var in ("WP_USER", "WP_APP_PASSWORD"):
        monkeypatch.setenv(var, "")
    return load_settings()


def test_schema_v2_enums_and_required(settings):
    schema = _schema(settings.category_slugs())
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(Draft.model_fields)
    assert schema["properties"]["kategorie"]["enum"] == settings.category_slugs()
    assert schema["properties"]["typ"]["enum"] == ["artikel", "event", "kino_termine"]
    assert schema["properties"]["dach_bezug"]["type"] == "boolean"


def test_system_prompt_is_cached_and_mentions_rules(settings):
    system = build_system(settings)
    text = system[0]["text"]
    assert system[0]["cache_control"] == {"type": "ephemeral"}
    assert "IMMER auf Deutsch" in text and "KEINE Kinos im Text" in text and "kino: Kino" in text


def test_user_message_contains_language_region_and_facts():
    item = NewsItem(
        title="ஜெர்மனியில் தீபாவளி", url="https://x.ta/1", summary="Kurz", source="SwissNews7",
        published=datetime(2026, 10, 16, 8, tzinfo=timezone.utc), language="ta", kind="event", ort="Zürich",
        facts={"kinos": []}, related=[NewsItem("a", "https://b.de/2", "", "WAZ", datetime(2026, 10, 16, tzinfo=timezone.utc))],
    )
    msg = build_user_message(item, "")
    assert "Sprache der Quelle: Tamil" in msg and "DACH-Ort laut Vorfilter: Zürich" in msg
    assert "Art der Meldung laut Vorfilter: event" in msg and "WAZ (https://b.de/2)" in msg
    assert '"kinos": []' in msg and "(nicht verfügbar)" in msg


def test_rewrite_message_contains_previous_draft_and_instruction():
    row = {"titel": "Alt", "inhalt_html": "<p>x</p>", "schlagworte": ["a"], "relevanz": 7, "quelle_name": "WAZ",
           "quelle_url": "https://waz.de/1", "fakten": {"woche": "2026-W42"}}
    msg = build_rewrite_message(row, "kürzer und sachlicher")
    assert "Anweisung der Redaktion: kürzer und sachlicher" in msg and '"titel": "Alt"' in msg
    assert '"woche": "2026-W42"' in msg and "Behalte alle Fakten" in msg


def test_render_content_replaces_model_source_with_links():
    row = {
        "typ": "artikel", "inhalt_html": '<p>Text.</p>\n<p class="quelle">Quelle: X</p>',
        "quelle_url": "https://cineplex.de/film?a=<b>", "quelle_name": "cineplex",
        "weitere_quellen": [{"name": "WAZ", "url": "https://waz.de/x"}],
    }
    out = render.render_content(row)
    assert out.count('class="quelle"') == 1 and 'href="https://cineplex.de/film?a=&lt;b&gt;"' in out and ">WAZ<" in out
    assert out.startswith("<p>Text.</p>")


def test_render_kino_list_and_event_box():
    row = {
        "typ": "kino_termine", "inhalt_html": "<p>Jailer 2 startet.</p>", "quelle_url": "https://cinestar.de/x", "quelle_name": "CineStar",
        "fakten": {"woche": "2026-W42", "kinos": [
            {"kino": "CineStar Mainz", "stadt": "Mainz", "land": "DE", "termine": ["2026-10-17T19:30:00+02:00"], "url": "https://cinestar.de/mainz"},
            {"kino": "Annenhof Kino", "stadt": "Graz", "land": "AT", "termine": [], "von": "2026-10-16"},
        ]},
    }
    out = render.render_content(row)
    assert "<h2>Spielorte und Termine</h2>" in out
    assert out.index("Graz (AT)") < out.index("Mainz") and "17.10.2026 19:30" in out and "ab 16.10.2026" in out
    assert "Tickets &amp; Infos" in out and "Kinowoche 2026-W42" in out

    event = {"typ": "event", "inhalt_html": "<p>Fest.</p>", "event_datum": "2026-11-14", "event_ort": "Zürich", "ticket_url": "https://t.ch/1",
             "quelle_url": "https://q.ch", "quelle_name": "Q"}
    out = render.render_content(event)
    assert "<strong>Wann:</strong> 14.11.2026" in out and "<strong>Wo:</strong> Zürich" in out and ">Tickets<" in out


def test_sanitize_strips_scripts_and_handlers():
    dirty = '<p onclick="x()">Hi</p><script>alert(1)</script><a href="javascript:bad()">l</a><iframe src="x"></iframe><marquee>no</marquee>'
    assert render.sanitize_html(dirty) == '<p>Hi</p><a href="#">l</a>no'


def test_raw_writer_draft_matches_schema(settings):
    from news_radar.writer import RawWriter, split_source_suffix

    writer = RawWriter(settings)
    it = NewsItem(title="Jailer 2 startet in Bremen - Weser-Kurier", url="https://example.com/a", summary="",
                  source="Google News DACH", published=datetime(2026, 10, 17, tzinfo=timezone.utc), kind="news",
                  score=8, dach_score=2, ort="Bremen", category_hint="kino")
    d = writer.write(it, "Der Film läuft ab Donnerstag im CineStar. Tickets gibt es online.")
    assert d.relevanz == 8 and d.kategorie == "kino" and d.typ == "artikel" and d.titel == "Jailer 2 startet in Bremen"
    assert d.kategorie in _schema(settings.category_slugs())["properties"]["kategorie"]["enum"]
    assert d.teaser.startswith("Der Film läuft") and "Auszug aus der Quelle" in d.inhalt_html and d.dach_bezug
    assert "Bremen" in d.schlagworte and d.inhalt_html.endswith('<p class="quelle">Quelle: Google News DACH</p>')
    unknown = NewsItem(title="Kurz - X", url="https://example.com/b", summary="s", source="S",
                       published=datetime(2026, 10, 17, tzinfo=timezone.utc), kind="event", category_hint="quatsch", score=1)
    weak = writer.write(unknown, "")
    assert weak.relevanz == 4 and weak.kategorie == "news" and weak.typ == "event"
    assert split_source_suffix("Kurz - X") == ("Kurz - X", "")
    assert split_source_suffix("Eine lange Überschrift über Tamilen in Hamm | WA Hamm") == ("Eine lange Überschrift über Tamilen in Hamm", "WA Hamm")
