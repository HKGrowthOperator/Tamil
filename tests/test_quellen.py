"""Quellen-Register (enabled, Felder) und Bewertung von `quellen pruefen` – ohne Netz."""

from datetime import datetime, timezone

from news_radar import quellencheck, sources
from news_radar.config import Source, load_settings
from news_radar.quellencheck import Pruefung, bewerten
from news_radar.store import Store


def test_register_has_20_active_of_28_and_disabled_sources_have_a_reason():
    s = load_settings()
    assert len(s.alle_quellen) == 28 and len(s.sources) == 20
    assert all(q.notiz for q in s.alle_quellen if not q.enabled)
    assert {q.prioritaet for q in s.alle_quellen} <= {"A", "B", "C"}
    assert not any(q.bild_nutzen for q in s.alle_quellen)  # ohne dokumentierte Erlaubnis keine Pressebilder


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
