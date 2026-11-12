"""Quellen-Register (enabled, Felder) und Bewertung von `quellen pruefen` – ohne Netz."""

from datetime import datetime, timezone
from pathlib import Path

from news_radar import quellencheck, sources
from news_radar.config import Source, load_settings
from news_radar.quellencheck import Pruefung, bewerten
from news_radar.store import Store


INVENTUR_2026_11 = {
    # Name: (Typ, Land) – aufgenommen aus der Quellen-Inventur vom 11.11.2026
    "Sivan Kovil Glattbrugg": ("rss", "CH"),
    "Sri Kathirvelayutha Swamy Tempel St. Margrethen": ("rss", "CH"),
    "Düsseldorf Tamil Sangam": ("rss", "DE"),
    "Tamils.co · Termine Deutschland": ("html", "DE"),
    "Filmkunstkinos Düsseldorf · Kino aus Indien": ("kino", "DE"),
    "dein-dein · Tamil Films in Germany": ("kino", "DE"),
    "Mathäser Filmpalast München": ("kino", "DE"),
    "Babylon Berlin · IndoGerman Film": ("kino", "DE"),
    "Kevelaerer Blatt · Tamilen": ("rss", "DE"),
    "theinder.net": ("rss", "DE"),
    "SEM · Medienmitteilungen": ("rss", "CH"),
}


def test_register_has_33_active_of_42_and_disabled_sources_have_a_reason():
    s = load_settings()
    assert len(s.alle_quellen) == 42 and len(s.sources) == 33
    assert all(q.notiz for q in s.alle_quellen if not q.enabled)
    assert {q.prioritaet for q in s.alle_quellen} <= {"A", "B", "C"}
    assert not any(q.bild_nutzen for q in s.alle_quellen)  # ohne dokumentierte Erlaubnis keine Pressebilder


def test_inventur_quellen_haben_die_pflichtfelder():
    """Neue Quellen aus der Inventur: aktiv, Register-Felder gesetzt, bekannter Typ, keine Google-News-Abfragen."""
    by_name = {q.name: q for q in load_settings().alle_quellen}
    for name, (typ, land) in INVENTUR_2026_11.items():
        q = by_name[name]
        # Kino-Seiten (provider html) laufen nach den Korrekturen zur Prüfung 11.11.2026 wieder; dein-dein bleibt aus
        assert q.enabled == (not name.startswith("dein-dein")), name
        assert q.type == typ and q.type in sources.FETCHERS and q.country == land, name
        assert q.betreiber and q.notiz and q.robots == "erlaubt" and q.prioritaet in {"A", "B", "C"}, name
        assert not q.paywall and not q.bild_nutzen and q.url.startswith("https://"), name
        assert "news.google.com" not in q.url, name
        if q.type == "html" or q.provider == "html":
            assert {"item", "title", "link", "date"} <= set(q.selectors), name
        # Termine aus Tempeln, Vereinen und Kinos: als Termin, Kinoreihen nur mit tamilischem Bezug
        if q.kind == "event" and q.min_score:
            assert q.bezug_noetig, name


def test_inventur_quellen_stehen_vor_den_regionen():
    """Die Quellen stehen im Block der [[source]]-Einträge (ein anderer Zweig hängt am Dateiende an)."""
    text = (Path(__file__).parent.parent / "sources.toml").read_text(encoding="utf-8")
    ende = text.index("[regions.staedte]")
    for name in INVENTUR_2026_11:
        assert text.index(f'name = "{name}"') < ende, name


def _p(**kw):
    base = dict(name="Q", typ="rss", kind="news", land="", aktiv_bisher=True, erreichbar=True, fehler="", sekunden=1.0,
                treffer_jetzt=10, treffer_14_tage=10, gesehen_14_tage_db=0, entwuerfe_db=0, robots="erlaubt",
                paywall_hinweis=False)
    base.update(kw)
    return Pruefung(**base)


def test_bewerten_prefers_dach_sources_with_drafts_and_punishes_robots_and_paywall():
    dach = bewerten(_p(entwuerfe_db=5), Source(name="CH", type="rss", country="CH"))
    welt = bewerten(_p(), Source(name="Welt", type="rss"))
    assert dach > welt
    assert bewerten(_p(robots="verboten"), Source(name="x", type="rss")) < welt - 5
    assert bewerten(_p(paywall_hinweis=True), Source(name="x", type="rss")) < welt
    assert bewerten(_p(erreichbar=False), Source(name="x", type="rss")) == -10


def test_pruefe_quelle_counts_items_and_drafts(tmp_path, monkeypatch):
    settings = load_settings()
    now = datetime(2026, 11, 8, tzinfo=timezone.utc)
    src = Source(name="Testquelle", type="rss", url="https://example.com/feed", country="CH")
    items = [sources.NewsItem(title=f"T{i}", url=f"https://example.com/{i}", summary="", source="Testquelle",
                              published=now) for i in range(3)]
    monkeypatch.setattr(sources, "fetch_source", lambda s, st: items)
    monkeypatch.setattr(quellencheck, "robots_status", lambda url: "erlaubt")
    monkeypatch.setattr(quellencheck, "paywall_hint", lambda url: False)
    with Store(tmp_path / "r.sqlite") as store:
        store.mark("u1", "T", "https://example.com/1", "Testquelle", "entwurf")
        store.insert_draft(dict(uid="u1", titel="T"))
        p = quellencheck.pruefe_quelle(src, settings, store, now)
    assert p.erreichbar and p.treffer_jetzt == 3 and p.entwuerfe_db == 1 and p.robots == "erlaubt"
