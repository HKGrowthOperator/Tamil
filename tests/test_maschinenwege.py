"""Maschinenwege ändern nur wartende Entwürfe: Wird ein Entwurf zwischen Lesen und Schreiben freigegeben, bleiben
Inhalt und Bild, und es wird keine Datei gelöscht (sonst überträgt der Timer etwas, das niemand gesehen hat)."""

import json

from news_radar import agent
from news_radar.images import FeaturedImage, branded_card
from news_radar.store import OPEN_STATES, Store

from test_agent import _fertig, _row, settings  # noqa: F401 – Fixture


def test_update_draft_nur_wartend(settings):  # noqa: F811
    with Store(settings.db_path) as store:
        did = store.insert_draft(_row("u1", "Tempelfest Hamm"))
        assert store.update_draft(did, titel="Neu", nur_status=OPEN_STATES) == 1
        store.set_status(did, "freigeben")
        assert store.update_draft(did, titel="Ungesehen", nur_status=OPEN_STATES) == 0
        assert store.get_draft(did)["titel"] == "Neu"


def test_kino_fakten_nicht_nach_der_freigabe(settings):  # noqa: F811
    with Store(settings.db_path) as store:
        did = store.insert_draft(_row("kino:1", "Jailer 2", typ="kino_termine", fingerprint="a"))
        echt = store.draft_by_uid

        def lesen_dann_freigeben(uid):  # zwischen Lesen und Schreiben gibt jemand frei
            row = echt(uid)
            store.set_status(did, "freigeben")
            return row

        store.draft_by_uid = lesen_dann_freigeben
        assert store.update_kino_facts("kino:1", {"kinos": ["neu"]}, "b", "Neue Spielorte") is False
        store.draft_by_uid = echt
        d = store.get_draft(did)
        assert d["fingerprint"] == "a" and d["status"] == "freigegeben"


def test_agent_import_freigabe_zwischen_lesen_und_schreiben(settings, tmp_path, monkeypatch):  # noqa: F811
    with Store(settings.db_path) as store:
        did = store.insert_draft(_row("u1", "Tempelfest Hamm", bild_datei="alt.jpg"))
        settings.bilder_dir.mkdir(parents=True, exist_ok=True)
        (settings.bilder_dir / "alt.jpg").write_bytes(b"x")

        def bild_und_freigabe(settings, **kw):  # der Bildabruf dauert; währenddessen gibt jemand frei
            store.set_status(did, "freigeben", von="luis")
            karte = branded_card("Neu", "Community", kw["slug"], "community")
            return FeaturedImage(karte.data, karte.filename, karte.mime, karte.credit, "karte")

        monkeypatch.setattr(agent, "beitragsbild", bild_und_freigabe)
        datei = tmp_path / "ergebnis.json"
        datei.write_text(json.dumps({"ergebnisse": [_fertig(did, "Ungesehener Titel")]}), encoding="utf-8")
        stats = agent.import_results(store, settings, datei)
        d = store.get_draft(did)
        assert stats["uebernommen"] == 0 and stats["fehler"], stats
        assert d["titel"] == "Tempelfest Hamm" and d["bild_datei"] == "alt.jpg" and d["status"] == "freigegeben"
        assert sorted(p.name for p in settings.bilder_dir.iterdir()) == ["alt.jpg"]
