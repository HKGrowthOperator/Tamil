"""End-to-End ohne Netz: Pipeline schreibt in die Warteschlange, Publisher veröffentlicht nur Freigegebenes."""

import io
from datetime import datetime, timedelta, timezone

import pytest
from PIL import Image

from news_radar import filtering, pipeline, sources
from news_radar.config import load_settings
from news_radar.images import branded_card, from_upload, save_pair
from news_radar.store import Store
from news_radar.wordpress import slugify
from news_radar.writer import Draft

NOW = datetime(2026, 10, 16, 12, tzinfo=timezone.utc)


@pytest.fixture
def settings(tmp_path, monkeypatch):
    for var in ("WP_USER", "WP_APP_PASSWORD", "NOTIFY_WEBHOOK_URL", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY"):
        monkeypatch.setenv(var, "")
    s = load_settings()
    s.data_dir = tmp_path / "data"
    s.web_url = "https://radar.test"
    return s


def item(title, summary="", hours_old=1, url=None, **kw):
    return sources.NewsItem(
        title=title,
        url=url or f"https://example.com/{slugify(title)}?utm_source=x",
        summary=summary,
        source="Test",
        published=NOW - timedelta(hours=hours_old),
        **kw,
    )


def make_draft(**kw):
    base = dict(
        relevanz=8, begruendung="DACH-Kinotermin", kategorie="kino", typ="artikel", dach_bezug=True, ort="Paderborn",
        titel="Ramayana läuft in Paderborn", teaser="Der Film kommt nach Paderborn.",
        inhalt_html="<p>Text.</p>\n<p class=\"quelle\">Quelle: X</p>",
        schlagworte=["Kino", "Paderborn"], seo_titel="Ramayana in Paderborn", meta_beschreibung="Termine",
        bild_suchbegriff="cinema hall", bild_alt="Kinosaal", event_datum="", event_ort="", ticket_url="",
    )
    base.update(kw)
    return Draft(**base)


class FakeWriter:
    def __init__(self, drafts):
        self.drafts = drafts
        self.calls = []

    def write(self, item, article_text):
        self.calls.append(item.title)
        return self.drafts[item.title]


def test_normalize_url_strips_tracking_and_www():
    assert sources.normalize_url("https://www.Example.com/a/?utm_source=x&id=2") == "https://example.com/a?id=2"


def test_uid_override_wins():
    assert item("x", uid_override="kino:jailer-2:2026W42").uid == "kino:jailer-2:2026W42"


def test_branded_card_and_upload_and_save_pair(tmp_path):
    img = branded_card("Ramayana startet in Paderborn – alle Termine für tamilische Kinofans", "Kino", "x")
    parsed = Image.open(io.BytesIO(img.data))
    assert parsed.format == "JPEG" and parsed.size == (1200, 675) and img.origin == "karte"

    buf = io.BytesIO()
    Image.new("RGB", (300, 900), (200, 10, 10)).save(buf, "PNG")
    up = from_upload(buf.getvalue(), "mein-bild")
    assert Image.open(io.BytesIO(up.data)).size == (1200, 675) and up.origin == "upload"

    name, thumb = save_pair(up, tmp_path / "bilder", "abc-mein-bild")
    assert (tmp_path / "bilder" / name).exists()
    assert Image.open(tmp_path / "bilder" / thumb).size[0] == 400


def test_slugify_german():
    assert slugify("Küche: Dosa & Sambar für Groß und Klein!") == "kueche-dosa-sambar-fuer-gross-und-klein"


def test_run_stores_draft_in_queue(settings, monkeypatch):
    relevant = item("Ramayana (Tamil) in Paderborn", "cineplex zeigt tamilischen Film", hours_old=2, dach_score=3, ort="Paderborn")
    weak = item("Tamil Nadu Milchpreis steigt", "tamil nadu", hours_old=1)
    monkeypatch.setattr(sources, "fetch_all", lambda s, store=None: [relevant, weak])
    monkeypatch.setattr(sources, "fetch_article_text", lambda url: "")
    monkeypatch.setattr(filtering, "select", lambda items, s, seen, titles: [i for i in items if i.uid not in seen])
    writer = FakeWriter({relevant.title: make_draft(), weak.title: make_draft(relevanz=2, titel="Milch")})

    results = pipeline.run(settings, writer=writer)
    by_status = {r.status: r for r in results}
    assert set(by_status) == {"entwurf", "verworfen"}
    assert by_status["entwurf"].link == "https://radar.test/entwurf/1"

    with Store(settings.db_path) as store:
        row = store.get_draft(1)
        assert row["status"] == "neu" and row["titel"] == "Ramayana läuft in Paderborn" and row["dach_bezug"] is True
        assert row["schlagworte"] == ["Kino", "Paderborn"] and row["original_json"].startswith("{")
        assert (settings.bilder_dir / row["bild_datei"]).exists()
        assert (settings.bilder_dir / row["bild_datei"].replace(".jpg", "-thumb.jpg")).exists()
        assert store.recent_runs()[0]["entwuerfe"] == 1 and store.recent_runs()[0]["verworfen"] == 1
        assert store.seen_uids() == {relevant.uid, weak.uid}

    # zweiter Lauf: nichts doppelt, Modell wird nicht erneut gefragt
    assert pipeline.run(settings, writer=writer) == []
    assert writer.calls == [relevant.title, weak.title]


def test_run_refreshes_open_kino_draft(settings, monkeypatch):
    facts1 = {"film": "Jailer 2", "woche": "2026-W42", "kinos": [{"kino": "CineStar Bremen", "stadt": "Bremen", "termine": []}]}
    kino = item("„Jailer 2“ (Tamil) läuft in 1 Kino", "Bremen", kind="kino", facts=facts1, fingerprint="f1",
                uid_override="kino:jailer-2:2026W42")
    monkeypatch.setattr(sources, "fetch_all", lambda s, store=None: [kino])
    monkeypatch.setattr(filtering, "select", lambda items, s, seen, titles: [i for i in items if i.uid not in seen])
    writer = FakeWriter({kino.title: make_draft(typ="artikel", titel="Jailer 2 kommt nach Bremen")})
    assert pipeline.run(settings, writer=writer)[0].status == "entwurf"

    kino.facts = {**facts1, "kinos": facts1["kinos"] + [{"kino": "CineStar Mainz", "stadt": "Mainz", "termine": []}]}
    kino.fingerprint = "f2"
    results = pipeline.run(settings, writer=writer)
    assert [r.status for r in results] == ["aktualisiert"] and "+CineStar Mainz" in results[0].note
    with Store(settings.db_path) as store:
        row = store.get_draft(1)
        assert row["typ"] == "kino_termine" and len(row["fakten"]["kinos"]) == 2 and row["hinweise"][0].startswith("Aktualisiert")
        assert store.counts_by_status()["neu"] == 1


def test_run_stops_at_daily_cap(settings, monkeypatch):
    settings.max_drafts_per_day = 1
    a, b = item("Pongal in Hamburg", dach_score=3), item("Deepavali in Köln", dach_score=3)
    monkeypatch.setattr(sources, "fetch_all", lambda s, store=None: [a, b])
    monkeypatch.setattr(sources, "fetch_article_text", lambda url: "")
    monkeypatch.setattr(filtering, "select", lambda items, s, seen, titles: [i for i in items if i.uid not in seen])
    writer = FakeWriter({a.title: make_draft(titel="Pongal"), b.title: make_draft(titel="Deepavali")})
    assert len(pipeline.run(settings, writer=writer)) == 1
    assert pipeline.run(settings, writer=writer) == []  # Budget für heute aufgebraucht
    with Store(settings.db_path) as store:
        assert store.counts_by_status()["neu"] == 1
        assert any(e["event"] == "tagesbudget" for e in store.iter_log())


def test_stale_event_date_uses_event_date_not_fetch_time(settings):
    now = datetime(2026, 10, 18, 10, tzinfo=timezone.utc)
    settings.max_age_hours = 72
    alt = item("Vaikasi Visakam im Tempel Bern", "Fest zu Ehren Murugans", kind="event")
    assert pipeline.stale_event_date(alt, "Wann: Freitag, 29.05.2026 ab 18.00 Uhr im Hindutempel", settings, now) == "2026-05-29"
    bericht = item("Vaahaikuyil 2026", "கடந்த 19.09.2026 சனிக்கிழமை", kind="event")
    assert pipeline.stale_event_date(bericht, "", settings, now) == "2026-09-19"
    kommend = item("Vaango Pazhagalam", "Samstag, 24. Oktober 2026 · Basel", kind="event", facts={"event_datum": "2026-10-24"})
    assert pipeline.stale_event_date(kommend, "", settings, now) == ""
    gestern = item("Jailer 2 Weinfelden", "", kind="event", facts={"event_datum": "2026-10-17"})
    assert pipeline.stale_event_date(gestern, "", settings, now) == ""  # innerhalb max_age_hours
    ohne = item("Beat Your Heart", "Broadcast poojas across all 26 cantons", kind="event")
    assert pipeline.stale_event_date(ohne, "", settings, now) == ""


def test_run_drops_past_events_before_writing(settings, monkeypatch):
    from news_radar.writer import RawWriter

    heute = datetime.now(timezone.utc).date()
    alt = item("Chithrapowrnami im Haus der Religionen", "Vollmondfest", hours_old=1, dach_score=3, ort="Bern",
               category_hint="community", score=9, kind="event",
               facts={"event_datum": (heute - timedelta(days=120)).isoformat(), "event_ort": "Bern"})
    neu = item("Pongal-Fest Hamm", "Fest im Tempel", hours_old=1, dach_score=3, ort="Hamm", category_hint="community",
               score=9, kind="event", facts={"event_datum": (heute + timedelta(days=30)).isoformat(), "event_ort": "Hamm"})
    monkeypatch.setattr(sources, "fetch_all", lambda s, store=None: [alt, neu])
    monkeypatch.setattr(sources, "fetch_article_text", lambda url: "")
    monkeypatch.setattr(filtering, "select", lambda items, s, seen, titles: [i for i in items if i.uid not in seen])
    results = {r.title: r for r in pipeline.run(settings, writer=RawWriter(settings))}
    assert results["Chithrapowrnami im Haus der Religionen"].status == "verworfen"
    assert results["Chithrapowrnami im Haus der Religionen"].note.startswith("veraltet")
    assert results["Pongal-Fest Hamm"].status == "entwurf"
    with Store(settings.db_path) as store:
        assert store.list_drafts(status="neu")[0]["titel"] == "Pongal-Fest Hamm"
        assert [e["grund"] for e in store.iter_log(event="verworfen")][0].startswith("Veranstaltung vom")


def test_run_ohne_ki_writes_marked_raw_drafts(settings, monkeypatch):
    from news_radar.writer import ROH_HINWEIS, RawWriter

    relevant = item("Pongal-Fest in Hamm lockt Hunderte Besucher - WA Hamm", "Der Hindu-Tempel Hamm feiert.", hours_old=2,
                    dach_score=3, ort="Hamm", category_hint="community", score=9, image_url="https://img.example/p.jpg")
    relevant.source = "Google News DACH"
    weak = item("Tamil Nadu Milchpreis steigt", "tamil nadu", hours_old=1, score=2)
    monkeypatch.setattr(sources, "fetch_all", lambda s, store=None: [relevant, weak])
    monkeypatch.setattr(sources, "fetch_article_text", lambda url: "Hunderte Besucher kamen am Samstag zum Tempelfest in Hamm-Uentrop. " * 3)
    monkeypatch.setattr(filtering, "select", lambda items, s, seen, titles: [i for i in items if i.uid not in seen])

    results = pipeline.run(settings, writer=RawWriter(settings))
    by_status = {r.status: r for r in results}
    assert set(by_status) == {"entwurf", "verworfen"} and by_status["entwurf"].note.startswith("Rohfassung")
    with Store(settings.db_path) as store:
        row = store.get_draft(1)
        assert row["hinweise"] == [ROH_HINWEIS] and row["kategorie"] == "community" and row["dach_bezug"] is True
        assert row["titel"] == "Pongal-Fest in Hamm lockt Hunderte Besucher" and row["quelle_name"] == "WA Hamm (via Google News)"
        assert "<blockquote>" in row["inhalt_html"] and row["quelle_bild"] == "https://img.example/p.jpg"
        assert store.recent_runs()[0]["modus"].endswith("ohne KI")
        assert [e["modus"] for e in store.iter_log(event="entwurf")] == ["roh"]
