from datetime import datetime, timedelta, timezone

import pytest
from PIL import Image
import io

from news_radar import filtering, pipeline, sources
from news_radar.config import load_settings
from news_radar.images import branded_card
from news_radar.wordpress import slugify
from news_radar.writer import Draft, _schema, build_system

NOW = datetime(2026, 10, 16, 12, tzinfo=timezone.utc)


@pytest.fixture
def settings(tmp_path, monkeypatch):
    for var in ("WP_USER", "WP_APP_PASSWORD", "NOTIFY_WEBHOOK_URL"):
        monkeypatch.setenv(var, "")
    s = load_settings()
    s.data_dir = tmp_path / "data"
    s.out_dir = tmp_path / "out"
    return s


def item(title, summary="", hours_old=1, url=None):
    return sources.NewsItem(
        title=title,
        url=url or f"https://example.com/{slugify(title)}?utm_source=x",
        summary=summary,
        source="Test",
        published=NOW - timedelta(hours=hours_old),
    )


def test_normalize_url_strips_tracking_and_www():
    assert sources.normalize_url("https://www.Example.com/a/?utm_source=x&id=2") == "https://example.com/a?id=2"


def test_select_filters_old_blocked_irrelevant_and_duplicates(settings):
    items = [
        item("Anirudh live in Germany: Tickets für Köln", "Konzert der tamilischen Musiklegende"),
        item("Anirudh live in Germany - Tickets für Köln!", "Doppelte Meldung"),
        item("Neuer Kollywood-Film startet in deutschen Kinos", hours_old=200),
        item("Börse schließt im Plus", "DAX steigt"),
        item("Tamil casino bonus", "tamil tamil tamil"),
    ]
    picked = filtering.select(items, settings, set(), [], now=NOW)
    assert [i.title for i in picked] == ["Anirudh live in Germany: Tickets für Köln"]
    assert picked[0].category_hint == "entertainment"


def test_select_skips_already_seen(settings):
    news = item("Pongal-Fest in Hamburg", "tamilische Community feiert")
    assert filtering.select([news], settings, {news.uid}, [], now=NOW) == []


def test_keywords_match_whole_words_only(settings):
    assert filtering.score_item(item("Ein Bernhardiner"), {"bern": 5}) == 0
    assert filtering.score_item(item("Tamilen in Bern"), {"bern": 5}) == 10


def test_branded_card_is_valid_jpeg():
    img = branded_card("Ramayana startet in Paderborn – alle Termine für tamilische Kinofans", "Kino", "x")
    parsed = Image.open(io.BytesIO(img.data))
    assert parsed.format == "JPEG" and parsed.size == (1200, 675)
    assert img.origin == "karte" and img.credit == "Grafik: Tamil.de"


def test_slugify_german():
    assert slugify("Küche: Dosa & Sambar für Groß und Klein!") == "kueche-dosa-sambar-fuer-gross-und-klein"


def test_schema_is_strict_and_limits_categories(settings):
    schema = _schema(settings.category_slugs())
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(Draft.model_fields)
    assert schema["properties"]["kategorie"]["enum"] == settings.category_slugs()


def test_system_prompt_is_cached_and_contains_style(settings):
    system = build_system(settings)
    assert system[0]["cache_control"] == {"type": "ephemeral"}
    assert "ihr" in system[0]["text"] and "kino: Kino" in system[0]["text"]


def make_draft(**kw):
    base = dict(
        relevanz=8, begruendung="DACH-Kinotermin", kategorie="kino", titel="Ramayana läuft in Paderborn",
        teaser="Der Film kommt nach Paderborn.", inhalt_html="<p>Text.</p>\n<p class=\"quelle\">Quelle: X</p>",
        schlagworte=["Kino", "Paderborn"], seo_titel="Ramayana in Paderborn", meta_beschreibung="Termine",
        bild_suchbegriff="cinema hall", bild_alt="Kinosaal",
    )
    base.update(kw)
    return Draft(**base)


def test_render_content_replaces_model_source_with_link():
    news = item("x", url="https://cineplex.de/film?a=<b>")
    html = pipeline.render_content(make_draft(), news)
    assert html.count('class="quelle"') == 1
    assert 'href="https://cineplex.de/film?a=&lt;b&gt;"' in html


class FakeWriter:
    def __init__(self, drafts):
        self.drafts = drafts

    def write(self, item, article_text):
        return self.drafts[item.title]


def test_run_dry_run_end_to_end(settings, monkeypatch):
    relevant = item("Ramayana (Tamil) in Paderborn", "cineplex zeigt tamilischen Film", hours_old=2)
    weak = item("Tamil Nadu Milchpreis steigt", "tamil nadu", hours_old=1)
    monkeypatch.setattr(sources, "fetch_all", lambda s: [relevant, weak])
    monkeypatch.setattr(sources, "fetch_article_text", lambda url: "")
    monkeypatch.setattr(filtering, "select", lambda items, s, seen, titles: [i for i in items if i.uid not in seen])
    writer = FakeWriter({relevant.title: make_draft(), weak.title: make_draft(relevanz=2, titel="Milch")})

    results = pipeline.run(settings, writer=writer)
    by_status = {r.status: r for r in results}
    assert set(by_status) == {"dry-run", "verworfen"}
    preview = by_status["dry-run"].link
    assert preview.endswith("vorschau.html")
    assert (settings.out_dir / "ramayana-laeuft-in-paderborn" / "ramayana-laeuft-in-paderborn.jpg").exists()

    # zweiter Lauf: nichts doppelt
    assert pipeline.run(settings, writer=writer) == []


class FakeWP:
    def __init__(self):
        self.posts = []

    def upload_media(self, image, alt):
        return 42

    def create_post(self, **kw):
        self.posts.append(kw)
        return {"id": 7}

    def edit_link(self, post):
        return "https://www.tamil.de/wp-admin/post.php?post=7&action=edit"


def test_run_creates_pending_wordpress_post(settings, monkeypatch):
    relevant = item("Anirudh Tour Europa", "tamil")
    monkeypatch.setattr(sources, "fetch_all", lambda s: [relevant])
    monkeypatch.setattr(sources, "fetch_article_text", lambda url: "")
    monkeypatch.setattr(filtering, "select", lambda items, s, seen, titles: items)
    wp = FakeWP()
    results = pipeline.run(settings, writer=FakeWriter({relevant.title: make_draft()}), wp=wp)
    assert results[0].status == "entwurf"
    post = wp.posts[0]
    assert post["status"] == "pending"  # Human-in-the-Loop: nie direkt live
    assert post["media_id"] == 42 and post["category_slug"] == "kino"
