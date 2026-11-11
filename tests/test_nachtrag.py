"""Nachtrag (Rückblick 2026): Vorschlag mit Quellen → Story → Agent-Modus → Veröffentlichung mit Ereignisdatum.

Kein Netz: der Radar holt die Quellen über Kontext.text_von, im Test über einen Fake (fetch_text bzw.
sources.fetch_article_text). Kein Modellaufruf, keine Kosten auf diesem Weg.
"""

import json
from datetime import datetime, timezone

import pytest

from news_radar import nachtrag, publisher, schalter, sources
from news_radar.agent_v2 import import_daten, paket_v2
from news_radar.agents import Kontext
from news_radar.config import load_settings
from news_radar.store import Store
from news_radar.workflow import fake as fake_mod
from news_radar.workflow import repo, schema

URL1 = "https://www.tagesschau.de/inland/tamilischer-tempel-hamm-100.html"
URL2 = "https://www.wa.de/hamm/tempelfest-2026-91234.html"
ARTIKEL1 = ("Am 14. März 2026 hat der Sri-Kamadchi-Ampal-Tempel in Hamm sein neues Gemeindehaus eröffnet. "
            "Rund 2000 Gäste aus Deutschland, Österreich und der Schweiz kamen zur Einweihung. "
            "Der Tempelverein hatte drei Jahre lang Spenden für den Bau gesammelt. "
            "Das Haus bietet Räume für Tamil-Unterricht, Tanz und Beratung für Familien.")
ARTIKEL2 = ("Der Tempelverein in Hamm hat sein Gemeindehaus am 14. März 2026 eingeweiht. "
            "Nach Angaben des Vereins kamen rund 2000 Gäste. Die Stadt Hamm war mit dem Oberbürgermeister vertreten. "
            "Im Gemeindehaus soll ab April Tamil-Unterricht für Kinder stattfinden. "
            "Der Verein will das Haus auch für Hochzeiten und Trauerfeiern der Gemeinde öffnen.")
SEITEN = {URL1: ARTIKEL1, URL2: ARTIKEL2}


@pytest.fixture
def settings(tmp_path, monkeypatch):
    for var in ("WP_URL", "WP_USER", "WP_APP_PASSWORD", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "GEMINI_API_KEY",
                "BILD_POOL_DIR", "NOTIFY_WEBHOOK_URL"):
        monkeypatch.setenv(var, "")
    s = load_settings()
    s.data_dir = tmp_path
    return s


def vorschlag(**kw) -> dict:
    v = {"arbeitstitel": "Tempel in Hamm eröffnet Gemeindehaus", "datum": "2026-03-14", "rubrik": "community",
         "ort": "Hamm", "bezug": "Größter Hindu-Tempel Deutschlands, Treffpunkt der Community", "heikel": False,
         "quellen": [{"url": URL1, "titel": "Tempel eröffnet Gemeindehaus", "herausgeber": "tagesschau.de",
                      "datum": "2026-03-14", "sprache": "de", "art": "bericht"},
                     {"url": URL2, "titel": "Tempelfest in Hamm", "herausgeber": "Westfälischer Anzeiger",
                      "datum": "2026-03-15", "sprache": "de", "art": "bericht"}],
         "kernfakten": ["Eröffnung am 14. März 2026", "rund 2000 Gäste"], "bild_hinweis": "Foto der Einweihung"}
    v.update(kw)
    return v


def kontext(store, settings, seiten=None, abrufe=None):
    seiten = SEITEN if seiten is None else seiten

    def holen(url):
        if abrufe is not None:
            abrufe.append(url)
        return seiten.get(url, "")
    return Kontext(settings=settings, store=store, fetch_text=holen, suche=lambda q: [])


def annehmen(store, settings, vorschlaege, **kw):
    return nachtrag.annehmen(store, settings, {"vorschlaege": vorschlaege}, von="test",
                             ctx=kontext(store, settings, **kw))


# ---- Migration ----------------------------------------------------------------------------------------

def test_migration_alter_bestand_bleibt_gueltig(settings, monkeypatch):
    alt = {k: v for k, v in schema.MIGRATIONS.items() if k < 5}
    monkeypatch.setattr(schema, "MIGRATIONS", alt)
    with Store(settings.db_path) as store:
        assert store.db.execute("PRAGMA user_version").fetchone()[0] == 4
        sid = repo.story_anlegen(store, typ="news", titel="Alte Story")
        store.insert_draft({"uid": "alt-1", "titel": "Alter Entwurf", "story_id": sid})
    monkeypatch.undo()
    with Store(settings.db_path) as store:
        assert store.db.execute("PRAGMA user_version").fetchone()[0] == schema.LATEST >= 5
        s = repo.story(store, sid)
        assert s["herkunft"] == "radar" and s["ereignis_datum"] is None
        d = store.draft_by_uid("alt-1")
        assert d["herkunft"] == "radar" and not d["ereignis_datum"]


# ---- Vorschlag annehmen -------------------------------------------------------------------------------

def test_vorschlag_wird_story_mit_selbst_geholten_quellen_ohne_job_und_kosten(settings):
    with Store(settings.db_path) as store:
        out = annehmen(store, settings, [vorschlag(heikel=True)])
        e = out["ergebnisse"][0]
        assert e["ergebnis"] == "angelegt" and e["quellen_geholt"] == 2 and out["angelegt"] == 1
        s = repo.story(store, e["story_id"])
        assert s["herkunft"] == "nachtrag" and s["ereignis_datum"] == "2026-03-14" and s["kategorie"] == "community"
        assert s["sensibel"] == 1 and s["status"] == "neu" and "Treffpunkt der Community" in s["notiz"]
        docs = repo.dokumente(store, e["story_id"])
        assert [d.text for d in docs] == [ARTIKEL1, ARTIKEL2]  # Text vom Radar geholt, nie aus dem Vorschlag
        assert docs[0].publisher == "tagesschau.de" and docs[0].art == "volltext" and docs[0].primaer
        assert store.db.execute("SELECT COUNT(*) FROM workflow_jobs").fetchone()[0] == 0
        assert store.db.execute("SELECT COUNT(*) FROM agent_usage").fetchone()[0] == 0
        zeile = store.db.execute("SELECT * FROM editorial_actions WHERE aktion = 'nachtrag_angelegt'").fetchone()
        assert zeile["story_id"] == e["story_id"] and zeile["ausloeser"] == "agent" and "Tempel" not in (zeile["notiz"] or "")
        # Der Scan-Tageslimit zählt Nachträge nicht mit
        assert repo.bezahlte_storys_heute(store, "2000-01-01") == 0


def test_export_liefert_nachtrag_mit_hinweisen_und_verwirft_vergangenes_nicht(settings):
    with Store(settings.db_path) as store:
        sid = annehmen(store, settings, [vorschlag(rubrik="events")])["ergebnisse"][0]["story_id"]
        mappe = paket_v2(store, settings, ctx=kontext(store, settings))
        p = next(p for p in mappe["storys"] if p["story_id"] == sid)
        assert p["herkunft"] == "nachtrag" and p["ereignis_datum"] == "2026-03-14" and p["kategorie"] == "events"
        h = p["vorschlag_hinweise"]
        assert h["bezug"].startswith("Größter") and h["kernfakten"] == ["Eröffnung am 14. März 2026", "rund 2000 Gäste"]
        assert h["bild_hinweis"] == "Foto der Einweihung" and "keine Belege" in h["achtung"]
        assert [d["doc_key"] for d in p["dokumente"]] == ["Q1", "Q2"]
        assert repo.story(store, sid)["status"] == "neu"


@pytest.mark.parametrize("aenderung, grund", [
    ({"arbeitstitel": ""}, "arbeitstitel"),
    ({"datum": "14.03.2026"}, "datum"),
    ({"datum": "2099-01-01"}, "Zukunft"),
    ({"rubrik": "politik"}, "rubrik"),
    ({"quellen": []}, "quellen"),
    ({"quellen": [{"url": f"https://example.org/{i}", "titel": "t", "herausgeber": "h", "datum": "2026-01-01",
                   "sprache": "de", "art": "bericht"} for i in range(7)]}, "höchstens 6"),
    ({"quellen": [{"url": "ftp://example.org/x", "titel": "t", "herausgeber": "h", "datum": "2026-01-01",
                   "sprache": "de", "art": "bericht"}]}, "http"),
])
def test_ungueltige_vorschlaege_werden_mit_grund_abgelehnt(settings, aenderung, grund):
    with Store(settings.db_path) as store:
        abrufe = []
        e = annehmen(store, settings, [vorschlag(**aenderung)], abrufe=abrufe)["ergebnisse"][0]
        assert e["ergebnis"] == "abgelehnt" and grund in e["grund"], e
        assert repo.stories(store) == [] and abrufe == []


@pytest.mark.parametrize("url", ["http://127.0.0.1/admin", "http://169.254.169.254/latest/meta-data",
                                 "http://10.0.0.5/intern"])
def test_interne_adresse_wird_abgelehnt_ohne_abruf(settings, url):
    with Store(settings.db_path) as store:
        abrufe = []
        quellen = vorschlag()["quellen"] + [{"url": url, "titel": "x", "herausgeber": "x", "datum": "2026-03-14",
                                             "sprache": "de", "art": "bericht"}]
        e = annehmen(store, settings, [vorschlag(quellen=quellen)], abrufe=abrufe)["ergebnisse"][0]
        assert e["ergebnis"] == "abgelehnt" and "interne Adresse" in e["grund"]
        assert abrufe == [] and repo.stories(store) == []


def test_nicht_abrufbare_quellen_werden_uebersprungen_bleibt_keine_abgelehnt(settings):
    with Store(settings.db_path) as store:
        teil = annehmen(store, settings, [vorschlag()], seiten={URL1: ARTIKEL1})["ergebnisse"][0]
        assert teil["ergebnis"] == "angelegt" and teil["quellen_geholt"] == 1
        assert teil["quellen_uebersprungen"][0]["url"] == URL2
        leer = annehmen(store, settings, [vorschlag(arbeitstitel="Ganz anderes Thema in Wien",
                                                    quellen=[{"url": "https://example.org/weg", "titel": "t",
                                                              "herausgeber": "h", "datum": "2026-02-01",
                                                              "sprache": "de", "art": "bericht"}])],
                        seiten={})["ergebnisse"][0]
        assert leer["ergebnis"] == "abgelehnt" and "keine Quelle abrufbar" in leer["grund"]
        assert len(repo.stories(store)) == 1


def test_derselbe_vorschlag_zweimal_ergibt_keine_zweite_story(settings):
    with Store(settings.db_path) as store:
        erst = annehmen(store, settings, [vorschlag()])["ergebnisse"][0]
        abrufe = []
        nochmal = annehmen(store, settings, [vorschlag()], abrufe=abrufe)["ergebnisse"][0]
        assert nochmal["ergebnis"] == "vorhanden" and nochmal["story_id"] == erst["story_id"]
        assert nochmal["grund"] == f"schon vorhanden: Story {erst['story_id']}" and abrufe == []
        aehnlich = annehmen(store, settings, [vorschlag(arbeitstitel="Tempel in Hamm eröffnet das Gemeindehaus",
                                                        datum="2026-03-16", quellen=[{
                                                            "url": "https://www.wdr.de/tempel-hamm", "titel": "t",
                                                            "herausgeber": "WDR", "datum": "2026-03-16",
                                                            "sprache": "de", "art": "bericht"}])])["ergebnisse"][0]
        assert aehnlich["ergebnis"] == "vorhanden" and aehnlich["story_id"] == erst["story_id"]
        assert len(repo.stories(store)) == 1


def test_stopp_redaktion_haelt_annahme_an(settings):
    with Store(settings.db_path) as store:
        schalter.setzen(store, "redaktion", True, wer="anna", grund="Prüfen")
        abrufe = []
        with pytest.raises(schalter.Gestoppt):
            annehmen(store, settings, [vorschlag()], abrufe=abrufe)
        assert abrufe == [] and repo.stories(store) == []


# ---- Import und Veröffentlichung ------------------------------------------------------------------------

def _ergebnis(paket: dict) -> dict:
    dokus = fake_mod.recherche("<dokumente>\n" + json.dumps(paket["dokumente"]) + "\n</dokumente>", "", {})
    beitrag = fake_mod.text("<story>\n" + json.dumps({"titel": paket["titel"], "ort": paket["ort"],
                                                       "kategorie": paket["kategorie"]})
                            + "\n</story>\n<claims>\n" + json.dumps(dokus["claims"]) + "\n</claims>", "", {})
    return {"story_id": paket["story_id"], "claims": dokus["claims"], "widersprueche": [], "beitrag": beitrag}


def _schreiben(store, settings):
    ctx = kontext(store, settings)
    mappe = paket_v2(store, settings, ctx=ctx)
    return import_daten(store, settings, {"ergebnisse": [_ergebnis(p) for p in mappe["storys"]]}, von="test", ctx=ctx)


def test_nachtrag_entwurf_traegt_ereignisdatum_und_wird_mit_datum_und_vermerk_veroeffentlicht(settings):
    with Store(settings.db_path) as store:
        sid = annehmen(store, settings, [vorschlag()])["ergebnisse"][0]["story_id"]
        stats = _schreiben(store, settings)
        assert stats["entwuerfe"] == 1, stats
        d = store.list_drafts("neu")[0]
        assert d["story_id"] == sid and d["herkunft"] == "nachtrag" and d["ereignis_datum"] == "2026-03-14"
        jetzt = datetime(2026, 11, 20, 10, 0, tzinfo=timezone.utc)
        p = publisher.plugin_payload(d, settings, "publish", jetzt=jetzt)
        assert p["datum"] == "2026-03-14 12:00:00"
        assert p["inhalt"].rstrip().endswith(
            "<p><em>Nachtrag der Redaktion: Dieser Beitrag wurde im November 2026 für den Rückblick auf das Jahr "
            "2026 geschrieben.</em></p>")
        normal = publisher.plugin_payload({**d, "herkunft": "radar", "ereignis_datum": None}, settings, "publish",
                                          jetzt=jetzt)
        assert "datum" not in normal and "Nachtrag der Redaktion" not in normal["inhalt"]


def test_nachtrag_entwuerfe_haben_eigene_tagesgrenze(settings):
    settings.entwuerfe_tag = 0  # das Pilot-Limit des Scans blockiert den Rückblick nicht
    settings.nachtrag_entwuerfe_tag = 1
    with Store(settings.db_path) as store:
        annehmen(store, settings, [vorschlag(),
                                   vorschlag(arbeitstitel="Tamilisches Filmfest in Zürich", datum="2026-05-02",
                                             rubrik="kino", ort="Zürich",
                                             quellen=[{"url": "https://www.srf.ch/filmfest", "titel": "t",
                                                       "herausgeber": "SRF", "datum": "2026-05-02", "sprache": "de",
                                                       "art": "bericht"}])],
                 seiten={**SEITEN, "https://www.srf.ch/filmfest": ARTIKEL1.replace("Hamm", "Zürich")})
        stats = _schreiben(store, settings)
        assert stats["entwuerfe"] == 1 and any("Tagesgrenze" in f for f in stats["fehler"]), stats
        offen = [s for s in repo.stories(store) if s["status"] == "neu"]
        assert len(offen) == 1  # die zweite Story bleibt unverändert im Export


# ---- Route und CLI --------------------------------------------------------------------------------------

def test_route_vorschlag_mit_token_stopp_und_fehlern(settings, monkeypatch):
    from news_radar.web import create_app

    monkeypatch.setattr(sources, "fetch_article_text", lambda url: SEITEN.get(url, ""))
    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim", "s3cret"
    app = create_app(settings, testing=True)
    client = app.test_client()
    assert client.post("/api/agent/vorschlag", json={"vorschlaege": []}).status_code == 404
    settings.agent_token = "agent-token-mit-genug-zeichen"
    kopf = {"Authorization": "Bearer agent-token-mit-genug-zeichen"}
    assert client.post("/api/agent/vorschlag", json={"vorschlaege": []},
                       headers={"Authorization": "Bearer falsch"}).status_code == 401
    assert client.post("/api/agent/vorschlag", data="x", headers=kopf, content_type="text/plain").status_code == 400
    assert client.post("/api/agent/vorschlag", json={"vorschlaege": "x"}, headers=kopf).status_code == 400
    resp = client.post("/api/agent/vorschlag?von=rueckblick", json={"vorschlaege": [vorschlag(), vorschlag()]},
                       headers=kopf)
    data = resp.get_json()
    assert resp.status_code == 200 and [e["ergebnis"] for e in data["ergebnisse"]] == ["angelegt", "vorhanden"]
    assert data["angelegt"] == 1 and data["vorhanden"] == 1 and data["abgelehnt"] == 0
    with Store(settings.db_path) as store:
        schalter.setzen(store, "redaktion", True, wer="anna", grund="Kosten prüfen")
    resp = client.post("/api/agent/vorschlag", json={"vorschlaege": [vorschlag(datum="2026-04-01")]}, headers=kopf)
    assert resp.status_code == 409 and resp.get_json()["kanal"] == "redaktion"


def test_cli_agent_vorschlag(settings, monkeypatch, tmp_path, capsys):
    from news_radar.__main__ import main

    monkeypatch.setattr(sources, "fetch_article_text", lambda url: SEITEN.get(url, ""))
    monkeypatch.setenv("RADAR_DATA_DIR", str(settings.data_dir))
    datei = tmp_path / "vorschlaege.json"
    datei.write_text(json.dumps([vorschlag()]), encoding="utf-8")
    assert main(["agent", "vorschlag", "--datei", str(datei)]) == 0
    assert "1 angelegt" in capsys.readouterr().out
    with Store(settings.db_path) as store:
        assert repo.stories(store)[0]["herkunft"] == "nachtrag"


# ---- Cockpit ----------------------------------------------------------------------------------------------

def test_cockpit_zeigt_nachtrag_und_filter_rueckblick(settings):
    from news_radar.web import create_app

    from test_web_redaktion import login

    with Store(settings.db_path) as store:
        annehmen(store, settings, [vorschlag()])
        _schreiben(store, settings)
        did = store.list_drafts("neu")[0]["id"]
        store.insert_draft({"uid": "radar-1", "titel": "Normale Meldung aus dem Radar", "kategorie": "news"})
    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim", "s3cret"
    client = create_app(settings, testing=True).test_client()
    login(client)
    feed = client.get("/").get_data(as_text=True)
    assert "Nachtrag · 14.03.2026" in feed and "Normale Meldung aus dem Radar" in feed
    rueckblick = client.get("/?status=neu&herkunft=nachtrag").get_data(as_text=True)
    assert "Nachtrag · 14.03.2026" in rueckblick and "Normale Meldung aus dem Radar" not in rueckblick
    assert "Rückblick" in feed
    assert "Nachtrag · 14.03.2026" in client.get(f"/entwurf/{did}").get_data(as_text=True)
