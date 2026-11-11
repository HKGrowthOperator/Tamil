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


# ---- Orchestrator: entwurf_anlegen -------------------------------------------------------------------

def _orchestrator_story(store, settings):
    from news_radar.agents import Kontext
    from news_radar.workflow import repo

    sid = repo.story_anlegen(store, typ="news", titel="Thaipusam in Zürich")
    repo.dokument_hinzufuegen(store, sid, url="https://www.example.org/a", publisher="ex", text="Prozession")
    ctx = Kontext(settings, store, fetch_text=lambda u: "")
    felder = {"titel": "Thaipusam in Zürich", "teaser": "T", "inhalt_html": "<p>Erste</p>", "kategorie": "community"}
    return ctx, sid, felder


def _bildstand(store, settings, did):
    import hashlib

    from news_radar.workflow import repo

    d = store.get_draft(did)
    return (d["bild_datei"], d["inhalt_html"], d["status"],
            hashlib.sha256((settings.bilder_dir / d["bild_datei"]).read_bytes()).hexdigest(),
            repo.asset_fuer_datei(store, d["bild_datei"])["id"])


def test_orchestrator_wiederlauf_bei_freigegebenem_entwurf(settings):  # noqa: F811
    from news_radar.workflow import orchestrator, repo

    with Store(settings.db_path) as store:
        ctx, sid, felder = _orchestrator_story(store, settings)
        did = orchestrator.entwurf_anlegen(ctx, repo.story(store, sid), felder, {}, typ="artikel", hinweise=[])
        store.set_status(did, "freigeben", von="luis")
        vorher = _bildstand(store, settings, did)
        dateien = sorted(p.name for p in settings.bilder_dir.iterdir())
        assets = store.db.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
        felder2 = {**felder, "inhalt_html": "<p>Zweite</p>", "kategorie": "kultur", "bild_thema": "konzert"}
        assert orchestrator.entwurf_anlegen(ctx, repo.story(store, sid), felder2, {}, typ="artikel", hinweise=[]) is None
        assert _bildstand(store, settings, did) == vorher
        assert sorted(p.name for p in settings.bilder_dir.iterdir()) == dateien
        assert store.db.execute("SELECT COUNT(*) FROM assets").fetchone()[0] == assets
        assert repo.story(store, sid)["status"] == "verworfen"


def test_orchestrator_freigabe_zwischen_lesen_und_schreiben(settings, monkeypatch):  # noqa: F811
    from news_radar.workflow import orchestrator, repo

    with Store(settings.db_path) as store:
        ctx, sid, felder = _orchestrator_story(store, settings)
        did = orchestrator.entwurf_anlegen(ctx, repo.story(store, sid), felder, {}, typ="artikel", hinweise=[])
        datei, inhalt, _, inhalt_sha, asset = _bildstand(store, settings, did)
        dateien = sorted(p.name for p in settings.bilder_dir.iterdir())

        def freigeben_waehrenddessen(existing):  # gelesen als „wartet“, dann gibt jemand frei
            store.set_status(did, "freigeben", von="luis")
            return False

        monkeypatch.setattr(orchestrator, "von_mensch_bearbeitet", freigeben_waehrenddessen)
        felder2 = {**felder, "inhalt_html": "<p>Zweite</p>", "kategorie": "kultur"}
        assert orchestrator.entwurf_anlegen(ctx, repo.story(store, sid), felder2, {}, typ="artikel", hinweise=[]) is None
        assert _bildstand(store, settings, did) == (datei, inhalt, "freigegeben", inhalt_sha, asset)
        assert sorted(p.name for p in settings.bilder_dir.iterdir()) == dateien
        assert store.db.execute("SELECT COUNT(*) FROM assets WHERE draft_id IS NULL").fetchone()[0] == 0
        assert repo.story(store, sid)["status"] == "verworfen"


def test_orchestrator_menschlich_bearbeitet_laesst_kein_neues_bild_zurueck(settings):  # noqa: F811
    from news_radar.workflow import orchestrator, repo

    with Store(settings.db_path) as store:
        ctx, sid, felder = _orchestrator_story(store, settings)
        did = orchestrator.entwurf_anlegen(ctx, repo.story(store, sid), felder, {}, typ="artikel", hinweise=[])
        store.update_draft(did, von="luis", titel="Von Hand verbessert")
        vorher = _bildstand(store, settings, did)
        dateien = sorted(p.name for p in settings.bilder_dir.iterdir())
        felder2 = {**felder, "inhalt_html": "<p>Zweite</p>", "kategorie": "kultur"}
        assert orchestrator.entwurf_anlegen(ctx, repo.story(store, sid), felder2, {}, typ="artikel", hinweise=[]) == did
        assert _bildstand(store, settings, did) == vorher
        assert sorted(p.name for p in settings.bilder_dir.iterdir()) == dateien
        assert store.db.execute("SELECT COUNT(*) FROM assets WHERE draft_id IS NULL").fetchone()[0] == 0



def test_agent_import_eindeutiger_name_und_conflict_nur_fuer_den_eintrag(settings, tmp_path, monkeypatch):  # noqa: F811
    from news_radar.store import ConflictError

    with Store(settings.db_path) as store:
        a = store.insert_draft(_row("u1", "Tempelfest Hamm"))
        b = store.insert_draft(_row("u2", "Tempelfest Hamm"))
        echt = store.set_status

        def set_status(draft_id, aktion, **kw):
            if draft_id == a and aktion == "bearbeiten":
                raise ConflictError("Zustand hat sich geändert")
            return echt(draft_id, aktion, **kw)

        monkeypatch.setattr(store, "set_status", set_status)
        datei = tmp_path / "ergebnis.json"
        datei.write_text(json.dumps({"ergebnisse": [_fertig(a, "Gleicher Titel"), _fertig(b, "Gleicher Titel")]}),
                         encoding="utf-8")
        stats = agent.import_results(store, settings, datei)
        assert stats["uebernommen"] == 1 and len(stats["fehler"]) == 1 and str(a) in stats["fehler"][0]
        da, db_ = store.get_draft(a)["bild_datei"], store.get_draft(b)["bild_datei"]
        assert da != db_ and f"-e{a}-" in da and f"-e{b}-" in db_
        assert store.get_draft(b)["status"] == "bearbeitet"


def test_kino_update_ignoriert_wird_protokolliert(settings, monkeypatch):  # noqa: F811
    from news_radar import pipeline

    with Store(settings.db_path) as store:
        did = store.insert_draft(_row("kino:1", "Jailer 2", typ="kino_termine", fingerprint="a",
                                      fakten={"kinos": [{"kino": "A"}]}))
        echt = store.update_kino_facts

        def freigeben_dann_update(*args, **kw):  # Freigabe zwischen Lesen und bedingtem Update
            store.set_status(did, "freigeben")
            return echt(*args, **kw)

        monkeypatch.setattr(store, "update_kino_facts", freigeben_dann_update)

        class Item:
            uid, fingerprint, facts, kind = "kino:1", "b", {"kinos": [{"kino": "B"}]}, "kino"

        pipeline.refresh_kino([Item()], store, {"kino:1"})
        assert any(e.get("id") == did for e in store.iter_log(event="kino_update_ignoriert"))
        assert store.get_draft(did)["fingerprint"] == "a"



def test_orchestrator_ausnahme_zwischen_speichern_und_binden(settings, monkeypatch):  # noqa: F811
    import pytest

    from news_radar.workflow import orchestrator, repo

    with Store(settings.db_path) as store:
        ctx, sid, felder = _orchestrator_story(store, settings)
        did = orchestrator.entwurf_anlegen(ctx, repo.story(store, sid), felder, {}, typ="artikel", hinweise=[])
        store.set_status(did, "freigeben", von="luis")
        vorher = _bildstand(store, settings, did)
        dateien = sorted(p.name for p in settings.bilder_dir.iterdir())

        def kaputt(*a, **k):
            raise RuntimeError("DB belegt")

        monkeypatch.setattr(store, "insert_draft", kaputt)
        with pytest.raises(RuntimeError):
            orchestrator.entwurf_anlegen(ctx, repo.story(store, sid), {**felder, "inhalt_html": "<p>3</p>"}, {},
                                         typ="artikel", hinweise=[])
        assert _bildstand(store, settings, did) == vorher
        assert sorted(p.name for p in settings.bilder_dir.iterdir()) == dateien
        assert store.db.execute("SELECT COUNT(*) FROM assets WHERE draft_id IS NULL").fetchone()[0] == 0


def test_asset_fuer_datei_bevorzugt_gebundene(settings):  # noqa: F811
    from news_radar.workflow import repo

    with Store(settings.db_path) as store:
        gebunden = repo.asset_anlegen(store, datei="x.jpg", herkunft="karte", draft_id=7)
        repo.asset_anlegen(store, datei="x.jpg", herkunft="ki")  # verwaist, aber neuer
        assert repo.asset_fuer_datei(store, "x.jpg")["id"] == gebunden



def test_save_pair_schreibt_gleiche_datei_nicht_neu(tmp_path):
    from news_radar import images

    bild = branded_card("Titel", "Community", "x", "community")
    name, thumb = images.save_pair(bild, tmp_path, "datei")
    vorher = {n: ((tmp_path / n).stat().st_ino, (tmp_path / n).stat().st_mtime_ns) for n in (name, thumb)}
    assert images.save_pair(bild, tmp_path, "datei") == (name, thumb)
    assert {n: ((tmp_path / n).stat().st_ino, (tmp_path / n).stat().st_mtime_ns) for n in (name, thumb)} == vorher
    anders = branded_card("Anderer Titel", "Kultur", "x", "kultur")
    images.save_pair(anders, tmp_path, "datei")
    assert (tmp_path / name).read_bytes() == anders.data
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted([name, thumb])  # keine Temp-Dateien übrig



def test_orchestrator_zwei_entwuerfe_einer_story_teilen_keine_datei(settings):  # noqa: F811
    from news_radar.workflow import orchestrator, repo

    with Store(settings.db_path) as store:
        ctx, sid, felder = _orchestrator_story(store, settings)
        a = orchestrator.entwurf_anlegen(ctx, repo.story(store, sid), felder, {"uid": "u-a"}, typ="artikel", hinweise=[])
        b = orchestrator.entwurf_anlegen(ctx, repo.story(store, sid), felder, {"uid": "u-b"}, typ="artikel", hinweise=[])
        assert a != b and store.get_draft(a)["bild_datei"] != store.get_draft(b)["bild_datei"]



def test_fassung_entwurf_neu_zeigt_auf_keine_geloeschte_datei(settings):  # noqa: F811
    from news_radar.workflow import orchestrator, repo

    with Store(settings.db_path) as store:
        ctx, sid, felder = _orchestrator_story(store, settings)
        did = orchestrator.entwurf_anlegen(ctx, repo.story(store, sid), felder, {}, typ="artikel", hinweise=[])
        store.update_draft(did, von="luis", titel="Von Hand")
        orchestrator.entwurf_anlegen(ctx, repo.story(store, sid), {**felder, "kategorie": "kultur"}, {}, typ="artikel",
                                     hinweise=[])
        neu = [f for f in repo.fassungen(store, story_id=sid) if f["rolle"] == "entwurf_neu"]
        inhalt = neu[-1]["inhalt"]
        inhalt = json.loads(inhalt) if isinstance(inhalt, str) else inhalt
        assert neu and inhalt.get("bild_datei", "") == ""



def test_agent_import_name_mit_inhalts_hash(settings, tmp_path):  # noqa: F811
    import hashlib

    with Store(settings.db_path) as store:
        did = store.insert_draft(_row("u1", "Tempelfest Hamm"))
        datei = tmp_path / "ergebnis.json"
        datei.write_text(json.dumps({"ergebnisse": [_fertig(did, "Tempelfest")]}), encoding="utf-8")
        assert agent.import_results(store, settings, datei)["uebernommen"] == 1
        name = store.get_draft(did)["bild_datei"]
        kurz = hashlib.sha256((settings.bilder_dir / name).read_bytes()).hexdigest()[:8]
        assert f"-e{did}-" in name and name.endswith(f"-{kurz}.jpg")



def test_orchestrator_ausnahme_nach_festschreiben_laesst_lizenz_beim_entwurf(settings, monkeypatch):  # noqa: F811
    import pytest

    from news_radar.workflow import orchestrator, repo

    with Store(settings.db_path) as store:
        ctx, sid, felder = _orchestrator_story(store, settings)

        def gesperrt(*a, **k):  # Entwurf ist schon festgeschrieben, nur das Binden scheitert
            raise RuntimeError("database is locked")

        monkeypatch.setattr(repo, "asset_draft_setzen", gesperrt)
        with pytest.raises(RuntimeError):
            orchestrator.entwurf_anlegen(ctx, repo.story(store, sid), felder, {}, typ="artikel", hinweise=[])
        d = store.list_drafts("neu")[0]
        asset = repo.asset_fuer_datei(store, d["bild_datei"])
        assert asset is not None and asset["herkunft"] == "karte"
        assert (settings.bilder_dir / d["bild_datei"]).is_file()


def test_orchestrator_aufraeumen_ersetzt_die_ausnahme_nicht(settings, monkeypatch):  # noqa: F811
    import pytest

    from news_radar.workflow import orchestrator, repo

    with Store(settings.db_path) as store:
        ctx, sid, felder = _orchestrator_story(store, settings)

        def abbruch(*a, **k):
            raise SystemExit(3)

        def kaputt(*a, **k):
            raise OSError("Aufräumen geht nicht")

        monkeypatch.setattr(store, "insert_draft", abbruch)
        monkeypatch.setattr(orchestrator, "_alte_datei_aufraeumen", kaputt)
        with pytest.raises(SystemExit):
            orchestrator.entwurf_anlegen(ctx, repo.story(store, sid), felder, {}, typ="artikel", hinweise=[])



def test_schreiben_zwei_threads_gleichzeitig(tmp_path):
    import threading

    from news_radar import images

    daten, fehler = b"x" * 2_000_000, []

    def lauf(pfad, schranke):
        schranke.wait()
        try:
            images._schreiben(pfad, daten)
        except Exception as exc:  # noqa: BLE001
            fehler.append(type(exc).__name__)

    for i in range(60):
        pfad, schranke = tmp_path / f"b{i}.jpg", threading.Barrier(2)
        laeufe = [threading.Thread(target=lauf, args=(pfad, schranke)) for _ in range(2)]
        [t.start() for t in laeufe]
        [t.join() for t in laeufe]
        assert pfad.read_bytes() == daten
    assert fehler == []
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted(f"b{i}.jpg" for i in range(60))


def test_save_pair_anderer_inhalt_neue_inode(tmp_path):
    from news_radar import images

    name, _ = images.save_pair(branded_card("Titel", "Community", "x", "community"), tmp_path, "datei")
    inode = (tmp_path / name).stat().st_ino
    images.save_pair(branded_card("Anderer Titel", "Kultur", "x", "kultur"), tmp_path, "datei")
    assert (tmp_path / name).stat().st_ino != inode  # ersetzt, nicht in place überschrieben



def test_agent_import_ueberschreibt_kein_bild_aus_dem_cockpit(settings, tmp_path, monkeypatch):  # noqa: F811
    with Store(settings.db_path) as store:
        did = store.insert_draft(_row("u1", "Tempelfest Hamm", bild_datei="alt.jpg"))
        settings.bilder_dir.mkdir(parents=True, exist_ok=True)
        for n in ("alt.jpg", "cockpit.jpg"):
            (settings.bilder_dir / n).write_bytes(b"x")

        def bild_waehrend_cockpit(settings, **kw):  # während des Bildabrufs ersetzt ein Mensch das Bild
            store.update_draft(did, bild_datei="cockpit.jpg", bild_origin="upload")
            karte = branded_card("Neu", "Community", kw["slug"], "community")
            return FeaturedImage(karte.data, karte.filename, karte.mime, karte.credit, "karte")

        monkeypatch.setattr(agent, "beitragsbild", bild_waehrend_cockpit)
        datei = tmp_path / "ergebnis.json"
        datei.write_text(json.dumps({"ergebnisse": [_fertig(did, "Ungesehener Titel")]}), encoding="utf-8")
        stats = agent.import_results(store, settings, datei)
        d = store.get_draft(did)
        assert stats["uebernommen"] == 0 and d["bild_datei"] == "cockpit.jpg" and d["titel"] == "Tempelfest Hamm"
        assert sorted(p.name for p in settings.bilder_dir.iterdir()) == ["alt.jpg", "cockpit.jpg"]


def test_orchestrator_ueberschreibt_kein_bild_aus_dem_cockpit(settings, monkeypatch):  # noqa: F811
    from news_radar.workflow import orchestrator, repo

    with Store(settings.db_path) as store:
        ctx, sid, felder = _orchestrator_story(store, settings)
        did = orchestrator.entwurf_anlegen(ctx, repo.story(store, sid), felder, {}, typ="artikel", hinweise=[])
        (settings.bilder_dir / "cockpit.jpg").write_bytes(b"x")

        def cockpit_bild_dazwischen(existing):
            store.update_draft(did, bild_datei="cockpit.jpg", bild_origin="upload")
            return False

        monkeypatch.setattr(orchestrator, "von_mensch_bearbeitet", cockpit_bild_dazwischen)
        felder2 = {**felder, "inhalt_html": "<p>Zweite</p>", "kategorie": "kultur"}
        assert orchestrator.entwurf_anlegen(ctx, repo.story(store, sid), felder2, {}, typ="artikel", hinweise=[]) is None
        d = store.get_draft(did)
        assert d["bild_datei"] == "cockpit.jpg" and d["inhalt_html"] == "<p>Erste</p>"
