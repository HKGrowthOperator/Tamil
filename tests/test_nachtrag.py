"""Nachtrag (Rückblick 2026): Vorschlag mit Quellen → Story → Agent-Modus → Veröffentlichung mit Ereignisdatum.

Kein Netz: der Radar holt die Quellen über Kontext.text_von, im Test über einen Fake (fetch_text bzw.
sources.fetch_article_text). Kein Modellaufruf, keine Kosten auf diesem Weg.
"""

import json
from datetime import datetime, timezone

import pytest

from news_radar import nachtrag, net, publisher, schalter, sources
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


def html(text: str, titel: str = "Tempel eröffnet Gemeindehaus – Lokales") -> str:
    kopf = f"<title>{titel}</title>" if titel else ""
    return f"<html><head>{kopf}</head><body><article><p>{text}</p></article></body></html>"


SEITEN = {URL1: html(ARTIKEL1), URL2: html(ARTIKEL2, "Tempelfest in Hamm | WA")}


def abruf_aus(seiten, abrufe=None, umleitung=None):
    """Fake-Transport: wie net.safe_get, aber ohne Netz (unbekannte Adresse → 404)."""
    def abruf(url, frist=None):
        if abrufe is not None:
            abrufe.append(url)
        if url not in seiten:
            raise net.HTTPError(404, url)
        return net.Fetched(url=(umleitung or {}).get(url, url), status=200, content=seiten[url].encode("utf-8"),
                           content_type="text/html; charset=utf-8")
    return abruf


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


def kontext(store, settings):
    return Kontext(settings=settings, store=store, fetch_text=lambda url: "", suche=lambda q: [])


def annehmen(store, settings, vorschlaege, seiten=None, abrufe=None, umleitung=None, **kw):
    return nachtrag.annehmen(store, settings, {"vorschlaege": vorschlaege}, von="test", ctx=kontext(store, settings),
                             abruf=abruf_aus(SEITEN if seiten is None else seiten, abrufe, umleitung), **kw)


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
    ({"arbeitstitel": "x" * 201}, "arbeitstitel"),
    ({"ort": "x" * 121}, "ort"),
    ({"bezug": "x" * 1001}, "bezug"),
    ({"kernfakten": ["x" * 301]}, "kernfakten"),
    ({"kernfakten": ["x"] * 13}, "kernfakten"),
    ({"bild_hinweis": "x" * 301}, "bild_hinweis"),
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
        teil = annehmen(store, settings, [vorschlag()], seiten={URL1: SEITEN[URL1]})["ergebnisse"][0]
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
        assert aehnlich["ergebnis"] == "vielleicht_vorhanden" and aehnlich["story_id"] == erst["story_id"]
        assert aehnlich["grund"] == f"vielleicht schon vorhanden: Story {erst['story_id']}"
        assert len(repo.stories(store)) == 1


def test_stopp_redaktion_haelt_annahme_an(settings):
    with Store(settings.db_path) as store:
        schalter.setzen(store, "redaktion", True, wer="anna", grund="Prüfen")
        abrufe = []
        with pytest.raises(schalter.Gestoppt):
            annehmen(store, settings, [vorschlag()], abrufe=abrufe)
        assert abrufe == [] and repo.stories(store) == []


def test_titel_der_quelle_kommt_von_der_seite_nie_aus_dem_vorschlag(settings):
    """P1: Ein erfundener Satz als Quellen-Titel darf keine Fundstelle werden."""
    from news_radar.agents import factcheck
    from news_radar.workflow.models import Claim

    erfunden = "Der Tempel hat 5000 neue Mitglieder aufgenommen und einen Neubau angekündigt"
    quellen = [{**vorschlag()["quellen"][0], "titel": erfunden}, {**vorschlag()["quellen"][1], "titel": erfunden}]
    seiten = {URL1: html(ARTIKEL1, "Tempel eröffnet Gemeindehaus – Lokales"), URL2: html(ARTIKEL2, titel="")}
    with Store(settings.db_path) as store:
        sid = annehmen(store, settings, [vorschlag(quellen=quellen)], seiten=seiten)["ergebnisse"][0]["story_id"]
        docs = repo.dokumente(store, sid)
        assert [d.titel for d in docs] == ["Tempel eröffnet Gemeindehaus – Lokales", ""]
        claim = Claim(id="C1", aussage=erfunden, art="was", kern=True, quellen=["Q1", "Q2"], fundstelle=erfunden,
                      sicherheit=0.9)
        assert not any(factcheck.fundstelle_belegt(claim, d) for d in docs)
        assert erfunden not in json.dumps(paket_v2(store, settings, ctx=kontext(store, settings)), ensure_ascii=False)


def test_herausgeber_aus_dem_host_und_datum_streng(settings):
    """P2: Herausgeber und Datum werden zur Quellenangabe – nicht ungeprüft aus dem Vorschlag."""
    quellen = [{**vorschlag()["quellen"][0], "herausgeber": "Tagesschau", "datum": "14.03.2026"},
               {**vorschlag()["quellen"][1], "herausgeber": "Westfälischer Anzeiger", "datum": "2026-03-15T10:00"}]
    with Store(settings.db_path) as store:
        sid = annehmen(store, settings, [vorschlag(quellen=quellen)],
                       umleitung={URL2: "https://www.fremd-verlag.example/artikel"})["ergebnisse"][0]["story_id"]
        docs = repo.dokumente(store, sid)
        assert [d.publisher for d in docs] == ["Tagesschau", "fremd-verlag.example"]
        assert [d.published_at for d in docs] == ["", ""]
        assert docs[1].url == "https://www.fremd-verlag.example/artikel"  # verlinkt wird, was gelesen wurde
        # dieselbe Ursprungsadresse wird trotzdem als Dublette erkannt
        nochmal = annehmen(store, settings, [vorschlag(quellen=quellen)],
                           umleitung={URL2: "https://www.fremd-verlag.example/artikel"})["ergebnisse"][0]
        assert nochmal["ergebnis"] == "vorhanden" and nochmal["story_id"] == sid
    assert nachtrag.herausgeber("SRF", "https://www.srf.ch/x") == "SRF"
    assert nachtrag.herausgeber("WDR", "https://www1.wdr.de/x") == "WDR"
    assert nachtrag.herausgeber("Bild", "https://www.wa.de/x") == "wa.de"


def _nachtrag_story(store, settings, status="recherche_erforderlich"):
    sid = annehmen(store, settings, [vorschlag()])["ergebnisse"][0]["story_id"]
    repo.story_setzen(store, sid, status=status)
    return sid


def _jobs(store, sid):
    return store.db.execute("SELECT COUNT(*) FROM workflow_jobs WHERE story_id = ?", (sid,)).fetchone()[0]


def test_nachtrag_bekommt_nie_einen_modell_job(settings):
    """P2: Neu starten, Quelle ergänzen, Job erneut, Worker – für Nachträge kein Job, kein Modellaufruf."""
    from news_radar.workflow import jobs, orchestrator
    from news_radar.workflow.fake import FakeAnthropic

    with Store(settings.db_path) as store:
        sid = _nachtrag_story(store, settings)
        assert jobs.einreihen(store, sid, "recherche") is None and _jobs(store, sid) == 0
        assert orchestrator.neu_starten(store, sid, "Neue Quelle: Test")
        assert _jobs(store, sid) == 0 and repo.story(store, sid)["status"] == "neu"  # zurück im Agent-Export
        repo.story_setzen(store, sid, status="recherche_erforderlich")
        key = orchestrator.quelle_ergaenzen(store, sid, "https://www.wdr.de/tempel-hamm", von="anna")
        assert key == "Q3" and _jobs(store, sid) == 0 and repo.story(store, sid)["status"] == "neu"
        # der Export holt den Volltext der ergänzten Quelle (ohne Suche nach zweiter Quelle)
        ctx = Kontext(settings=settings, store=store, fetch_text=lambda url: ARTIKEL2 if "wdr" in url else "",
                      suche=lambda q: (_ for _ in ()).throw(AssertionError("keine Suche")))
        p = next(p for p in paket_v2(store, settings, ctx=ctx)["storys"] if p["story_id"] == sid)
        assert p["dokumente"][2]["text"] == ARTIKEL2 and p["dokumente"][2]["art"] == "volltext"
        # ein Altbestand-Job (etwa vor diesem Fix angelegt): „erneut“ geht nicht, der Worker ruft kein Modell
        store.db.execute("INSERT INTO workflow_jobs (story_id, schritt, status, prio, versuche, naechster_versuch, "
                         "idempotenz_key, payload, erstellt, aktualisiert) VALUES (?, 'recherche', 'tot', 0, 0, "
                         "'2000-01-01', 'alt', '{}', '2000-01-01', '2000-01-01')", (sid,))
        store.db.commit()
        jid = store.db.execute("SELECT id FROM workflow_jobs WHERE story_id = ?", (sid,)).fetchone()[0]
        assert not jobs.erneut(store, jid)
        store.db.execute("UPDATE workflow_jobs SET status = 'offen' WHERE id = ?", (jid,))
        store.db.commit()
        client = FakeAnthropic()
        orchestrator.abarbeiten(orchestrator.kontext(settings, store, client=client, fetch_text=lambda u: ARTIKEL1,
                                                     suche=lambda q: []))
        assert client.requests == [] and store.db.execute("SELECT COUNT(*) FROM agent_usage").fetchone()[0] == 0
        assert store.db.execute("SELECT status FROM workflow_jobs WHERE id = ?", (jid,)).fetchone()[0] == "fertig"


def test_scan_ordnet_nachtraegen_keine_meldung_mit_job_zu(settings):
    from datetime import timedelta

    from news_radar.agents import cluster
    from news_radar.workflow import orchestrator
    from news_radar.workflow.fake import FakeAnthropic

    with Store(settings.db_path) as store:
        sid = _nachtrag_story(store, settings)
        now = datetime.now(timezone.utc)
        aehnlich = sources.NewsItem(title="Tempel in Hamm eröffnet Gemeindehaus", url="https://www.ruhr.de/tempel",
                                    summary="Gemeindehaus eröffnet", source="Ruhr Nachrichten",
                                    published=now - timedelta(hours=1))
        ctx = orchestrator.kontext(settings, store, client=FakeAnthropic(), fetch_text=lambda u: ARTIKEL1,
                                   suche=lambda q: [])
        assert cluster.zuordnen(ctx, [aehnlich])[0].story_id is None
        gleich = sources.NewsItem(title="Gemeindehaus in Hamm", url=URL1, summary="x", source="Tagesschau",
                                  published=now - timedelta(hours=1))
        orchestrator.scan(ctx, [gleich])
        orchestrator.abarbeiten(ctx)
        assert _jobs(store, sid) == 0
        assert store.db.execute("SELECT COUNT(*) FROM agent_usage WHERE story_id = ?", (sid,)).fetchone()[0] == 0


QUELLE3 = {"url": "https://www.wdr.de/kultur/abend", "titel": "t", "herausgeber": "WDR", "datum": "2026-03-14",
           "sprache": "de", "art": "bericht"}


def test_titel_dublette_nur_vielleicht_ort_trennt_erzwingen_legt_an(settings):
    """P2/P3: verschiedener Ort ist keine Dublette; reine Titelähnlichkeit meldet nur; eine gemeinsame Adresse reicht
    nicht, nur wenn alle Adressen schon Beleg derselben Story sind."""
    zh = vorschlag(arbeitstitel="Tamilischer Kulturabend in Zürich", ort="Zürich", quellen=[vorschlag()["quellen"][0]])
    be = vorschlag(arbeitstitel="Tamilischer Kulturabend in Bern", ort="Bern", quellen=[QUELLE3])
    with Store(settings.db_path) as store:
        seiten = {**SEITEN, QUELLE3["url"]: html(ARTIKEL2)}
        out = annehmen(store, settings, [zh, be], seiten=seiten)
        assert [e["ergebnis"] for e in out["ergebnisse"]] == ["angelegt", "angelegt"]
        bern2 = {**be, "quellen": [{**QUELLE3, "url": "https://www.derbund.ch/kulturabend"}]}
        seiten["https://www.derbund.ch/kulturabend"] = html(ARTIKEL2)
        e = annehmen(store, settings, [bern2], seiten=seiten)["ergebnisse"][0]
        assert e["ergebnis"] == "vielleicht_vorhanden" and e["story_id"] == out["ergebnisse"][1]["story_id"]
        e = annehmen(store, settings, [{**bern2, "erzwingen": True}], seiten=seiten)["ergebnisse"][0]
        assert e["ergebnis"] == "angelegt"
        # Jahresbericht: eine gemeinsame Adresse plus eine neue → kein Abweisen
        neu = vorschlag(arbeitstitel="Tamil-Schule Essen feiert Jubiläum", ort="Essen",
                        quellen=[vorschlag()["quellen"][0], {**QUELLE3, "url": "https://www.waz.de/essen/schule"}])
        seiten["https://www.waz.de/essen/schule"] = html(ARTIKEL2)
        assert annehmen(store, settings, [neu], seiten=seiten)["ergebnisse"][0]["ergebnis"] == "angelegt"
        assert annehmen(store, settings, [neu], seiten=seiten)["ergebnisse"][0]["ergebnis"] == "vorhanden"


def test_verschraenkte_aufrufe_legen_keine_doppelte_story_an(settings):
    """P2: Zwischen Dublettenprüfung und Anlegen liegen die Abrufe – ein zweiter Aufruf darf dazwischenkommen."""
    with Store(settings.db_path) as store:
        innen = {}
        basis = abruf_aus(SEITEN)

        def abruf(url, frist=None):
            if not innen:  # während Aufruf A seine Quellen holt, läuft Aufruf B vollständig durch
                innen["b"] = nachtrag.annehmen(store, settings, {"vorschlaege": [vorschlag()]}, von="b",
                                               ctx=kontext(store, settings), abruf=basis)
            return basis(url, frist)
        a = nachtrag.annehmen(store, settings, {"vorschlaege": [vorschlag()]}, von="a", ctx=kontext(store, settings),
                              abruf=abruf)["ergebnisse"][0]
        b = innen["b"]["ergebnisse"][0]
        assert b["ergebnis"] == "angelegt" and a["ergebnis"] == "vorhanden" and a["story_id"] == b["story_id"]
        assert len(repo.stories(store)) == 1 and len(repo.dokumente(store, b["story_id"])) == 2


def test_zeitlimit_je_aufruf_und_hoechstzahl(settings):
    """P2: Gesamtfrist je Aufruf; was nicht mehr geschafft wird, kommt als „nicht bearbeitet“ zurück, ohne Story."""
    uhr = {"t": 0.0}
    fristen = []
    basis = abruf_aus({**SEITEN, QUELLE3["url"]: html(ARTIKEL2)})

    def langsam(url, frist=None):
        fristen.append(frist)
        uhr["t"] += 50
        return basis(url, frist)
    eins = vorschlag(quellen=[vorschlag()["quellen"][0]])
    zwei = vorschlag(arbeitstitel="Kulturabend in Bern", ort="Bern", quellen=[QUELLE3])
    with Store(settings.db_path) as store:
        out = nachtrag.annehmen(store, settings, {"vorschlaege": [eins, zwei, {**zwei, "arbeitstitel": "Drittes"}]},
                                ctx=kontext(store, settings), abruf=langsam, frist_gesamt=90, frist_abruf=20,
                                uhr=lambda: uhr["t"])
        assert [e["ergebnis"] for e in out["ergebnisse"]] == ["angelegt", "angelegt", "nicht_bearbeitet"]
        assert out["ergebnisse"][2]["grund"] == "nicht bearbeitet: Zeitlimit" and out["nicht_bearbeitet"] == 1
        assert fristen == [20, 70]  # je Abruf höchstens 20 s, nie über die Gesamtfrist hinaus
        assert len(repo.stories(store)) == 2
        with pytest.raises(ValueError, match="höchstens 5"):
            nachtrag.annehmen(store, settings, {"vorschlaege": [eins] * 6}, max_vorschlaege=5,
                              ctx=kontext(store, settings), abruf=basis)


def test_safe_get_haelt_die_gesamtfrist_ein():
    import time

    with pytest.raises(net.Zeitlimit):
        net.safe_get("https://www.example.org/", frist=time.monotonic() - 1)


def test_stopp_mitten_im_stapel_liefert_bisherige_ergebnisse(settings):
    with Store(settings.db_path) as store:
        basis = abruf_aus({**SEITEN, QUELLE3["url"]: html(ARTIKEL2)})

        def abruf(url, frist=None):
            schalter.setzen(store, "redaktion", True, wer="anna", grund="Pause")
            return basis(url, frist)
        out = nachtrag.annehmen(store, settings, {"vorschlaege": [
            vorschlag(quellen=[vorschlag()["quellen"][0]]),
            vorschlag(arbeitstitel="Kulturabend in Bern", ort="Bern", quellen=[QUELLE3])]},
            ctx=kontext(store, settings), abruf=abruf)
        assert [e["ergebnis"] for e in out["ergebnisse"]] == ["angelegt", "nicht_bearbeitet"]
        assert out["angehalten"]["kanal"] == "redaktion" and "angehalten" in out["ergebnisse"][1]["grund"]
        assert len(repo.stories(store)) == 1


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


def test_ohne_plugin_wird_ein_nachtrag_nicht_veroeffentlicht(settings):
    """P3: Der alte REST-Weg kennt kein Ereignisdatum – lieber klar ablehnen als mit heutigem Datum senden."""
    class CoreWP:
        def __init__(self):
            self.posts = []

        def create_post(self, **kw):
            self.posts.append(kw)
            return {"id": 1, "link": "https://www.tamil.de/p/"}

        def edit_link(self, post):
            return ""

    wp = CoreWP()
    with Store(settings.db_path) as store:
        row = {"id": 1, "uid": "x", "titel": "Rückblick", "inhalt_html": "<p>Text</p>", "kategorie": "news",
               "herkunft": "nachtrag", "ereignis_datum": "2026-03-14"}
        with pytest.raises(RuntimeError, match="Plugin"):
            publisher.publish_draft(row, settings, wp, store, status="publish")
        assert wp.posts == []
        publisher.publish_draft({**row, "herkunft": "radar", "ereignis_datum": ""}, settings, wp, store, status="draft")
        assert len(wp.posts) == 1 and "Nachtrag der Redaktion" not in wp.posts[0]["content"]


def test_cockpit_vorschau_zeigt_den_vermerk(settings):
    from news_radar.web import create_app

    from test_web_redaktion import login

    with Store(settings.db_path) as store:
        annehmen(store, settings, [vorschlag()])
        _schreiben(store, settings)
        did = store.list_drafts("neu")[0]["id"]
    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim", "s3cret"
    client = create_app(settings, testing=True).test_client()
    login(client)
    assert "Nachtrag der Redaktion: Dieser Beitrag wurde im" in client.get(f"/entwurf/{did}").get_data(as_text=True)
    assert "Nachtrag der Redaktion: Dieser Beitrag wurde im" in client.get(f"/vorschau/{did}").get_data(as_text=True)


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
                 seiten={**SEITEN, "https://www.srf.ch/filmfest": html(ARTIKEL1.replace("Hamm", "Zürich"))})
        stats = _schreiben(store, settings)
        assert stats["entwuerfe"] == 1 and any("Tagesgrenze" in f for f in stats["fehler"]), stats
        offen = [s for s in repo.stories(store) if s["status"] == "neu"]
        assert len(offen) == 1  # die zweite Story bleibt unverändert im Export


# ---- Route und CLI --------------------------------------------------------------------------------------

def test_route_vorschlag_mit_token_stopp_und_fehlern(settings, monkeypatch):
    from news_radar.web import create_app

    monkeypatch.setattr(nachtrag, "standard_abruf", abruf_aus(SEITEN))
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
    zu_viele = client.post("/api/agent/vorschlag", json={"vorschlaege": [vorschlag()] * 6}, headers=kopf)
    assert zu_viele.status_code == 400 and "höchstens 5" in zu_viele.get_json()["fehler"]
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

    monkeypatch.setattr(nachtrag, "standard_abruf", abruf_aus(SEITEN))
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


# ---- PDF-Quellen (Rückblick 2026: Drucksachen, Urteile, Berichte, Statistiken) ----------------------------

PDF_URL = "https://dserver.bundestag.de/btd/20/123/2012345.pdf"
SEITE1 = ["Deutscher Bundestag Drucksache 20/12345, 20. Wahlperiode.",
          "Antwort der Bundesregierung auf die Kleine Anfrage zur Lage der tamilischen Gemeinden.",
          "Vorbemerkung der Fragesteller: Die Fragen betreffen Abschiebungen nach Sri Lanka.",
          "Die Bundesregierung beantwortet die Fragen im Einvernehmen mit dem Auswärtigen Amt.",
          "Die Zahlen stammen aus dem Ausländerzentralregister zum Stichtag 30. Juni 2026."]
SEITE2 = ["Im ersten Halbjahr 2026 stellten 412 Personen aus Sri Lanka einen Erstantrag beim Bundes-",
          "amt für Migration und Flüchtlinge. Die Schutzquote lag bei 18,4 Prozent.",
          "Die Zahl der Abschiebungen nach Sri-",
          "Lanka betrug im selben Zeitraum 37, davon 21 im Rahmen von Sammelabschiebungen.",
          "Weitere Angaben zu Dublin-Verfahren enthält die Anlage zu dieser Antwort der Bundesregierung."]


def pdf_bytes(seiten: list[list[str]], titel: str = "", passwort: str = "") -> bytes:
    """Kleines Text-PDF ohne Netz: eine Inhaltsdatei je Seite (Helvetica, WinAnsi), Zeilen mit T*."""
    from io import BytesIO

    from pypdf import PdfWriter
    from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

    w = PdfWriter()
    font = w._add_object(DictionaryObject({
        NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"), NameObject("/Encoding"): NameObject("/WinAnsiEncoding")}))
    for zeilen in seiten:
        seite = w.add_blank_page(595, 842)
        ops = ["BT /F1 10 Tf 12 TL 40 800 Td"]
        ops += ["(" + z.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") + ") Tj T*" for z in zeilen]
        stream = DecodedStreamObject()
        stream.set_data("\n".join(ops + ["ET"]).encode("cp1252"))
        seite[NameObject("/Contents")] = w._add_object(stream)
        seite[NameObject("/Resources")] = DictionaryObject(
            {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})})
    if titel:
        w.add_metadata({"/Title": titel})
    if passwort:
        w.encrypt(passwort, algorithm="RC4-128")
    buf = BytesIO()
    w.write(buf)
    return buf.getvalue()


def pdf_abruf(dateien: dict, abrufe=None):
    """Fake-Transport: PDF-Bytes je Adresse ohne Anker (wie requests: das Fragment geht nie an den Server)."""
    def abruf(url, frist=None):
        if abrufe is not None:
            abrufe.append(url)
        ohne = url.split("#", 1)[0]
        if ohne in dateien:
            return net.Fetched(url=ohne, status=200, content=dateien[ohne], content_type="application/pdf")
        return abruf_aus(SEITEN)(url, frist)
    return abruf


def pdf_vorschlag(*urls, **kw) -> dict:
    v = {"arbeitstitel": "Bundesregierung zu Abschiebungen nach Sri Lanka", "rubrik": "news", "ort": "Berlin",
         "quellen": [{"url": u, "titel": "erfundener Titel", "herausgeber": "Deutscher Bundestag",
                      "datum": "2026-08-01", "sprache": "de", "art": "drucksache"} for u in urls]}
    return vorschlag(**{**v, **kw})


def pdf_annehmen(store, settings, v, dateien):
    return nachtrag.annehmen(store, settings, {"vorschlaege": [v]}, von="test", ctx=kontext(store, settings),
                             abruf=pdf_abruf(dateien))["ergebnisse"][0]


def test_pdf_quelle_wird_gelesen_titel_aus_metadaten(settings):
    datei = pdf_bytes([SEITE1, SEITE2], titel="Drucksache 20/12345")
    with Store(settings.db_path) as store:
        e = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL), {PDF_URL: datei})
        assert e["ergebnis"] == "angelegt", e
        doc = repo.dokumente(store, e["story_id"])[0]
        assert doc.titel == "Drucksache 20/12345" and doc.url == PDF_URL and doc.art == "volltext"
        assert "Antwort der Bundesregierung auf die Kleine Anfrage" in doc.text
        assert "412 Personen aus Sri Lanka" in doc.text and "\n\n" in doc.text  # Seitenwechsel als Leerzeile
        # Silbentrennung zusammengezogen, echter Bindestrich vor Großbuchstaben bleibt
        assert "beim Bundesamt für Migration" in doc.text and "nach Sri-Lanka betrug" in doc.text
        assert "Bundes-" not in doc.text and "  " not in doc.text
    assert nachtrag.pdf_lesen(pdf_bytes([SEITE1, SEITE2]))[1] == ""  # ohne Metadaten leer, nie aus dem Vorschlag


def test_pdf_anker_page_beginnt_auf_seite_und_bleibt_in_der_adresse(settings):
    datei = pdf_bytes([SEITE1, SEITE2, SEITE1])
    with Store(settings.db_path) as store:
        e = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL + "#page=2"), {PDF_URL: datei})
        doc = repo.dokumente(store, e["story_id"])[0]
        assert doc.url == PDF_URL + "#page=2" and doc.text.startswith("Im ersten Halbjahr 2026")
        # dieselbe Datei, andere Seite: keine Dublette derselben Adresse
        zwei = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL + "#page=3", erzwingen=True), {PDF_URL: datei})
        assert zwei["ergebnis"] == "angelegt" and zwei["story_id"] != e["story_id"]
        gleich = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL + "#page=2"), {PDF_URL: datei})
        assert gleich["ergebnis"] == "vorhanden" and gleich["story_id"] == e["story_id"]
        # zwei Seiten derselben Datei als Belege einer Story
        beide = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL + "#page=1", PDF_URL + "#page=2", erzwingen=True,
                                                            arbeitstitel="Asylzahlen im ersten Halbjahr"),
                             {PDF_URL: datei})
        assert beide["ergebnis"] == "angelegt" and beide["quellen_geholt"] == 2
        assert [d.url for d in repo.dokumente(store, beide["story_id"])] == [PDF_URL + "#page=1", PDF_URL + "#page=2"]
        weg = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL + "#page=9", erzwingen=True,
                                                          arbeitstitel="Seite gibt es nicht"), {PDF_URL: datei})
        assert weg["ergebnis"] == "abgelehnt" and "keine Seite 9" in weg["quellen_uebersprungen"][0]["grund"]


@pytest.mark.parametrize("daten", [b"%PDF-1.7\n kaputt \x00\x01 ohne xref", b"<<< gar kein PDF >>>"])
def test_kaputtes_pdf_wird_mit_grund_abgelehnt(settings, daten):
    with Store(settings.db_path) as store:
        e = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL), {PDF_URL: daten})
        assert e["ergebnis"] == "abgelehnt" and "keine Quelle abrufbar" in e["grund"]
        assert "PDF nicht lesbar" in e["quellen_uebersprungen"][0]["grund"] and repo.stories(store) == []


def test_verschluesseltes_pdf_wird_abgelehnt(settings):
    with Store(settings.db_path) as store:
        e = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL), {PDF_URL: pdf_bytes([SEITE1], passwort="geheim")})
        assert e["ergebnis"] == "abgelehnt" and "PDF nicht lesbar" in e["quellen_uebersprungen"][0]["grund"]


def test_pdf_ohne_text_uebersprungen_und_ueber_8_mb_abgelehnt(settings):
    gross = pdf_bytes([SEITE1, SEITE2]) + b"%" + b"x" * 8_000_001
    with Store(settings.db_path) as store:
        e = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL), {PDF_URL: pdf_bytes([[], []])})
        assert e["ergebnis"] == "abgelehnt" and e["quellen_uebersprungen"][0]["grund"] == "ohne lesbaren Text"
        g = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL), {PDF_URL: gross})
        assert g["ergebnis"] == "abgelehnt" and "zu groß" in g["quellen_uebersprungen"][0]["grund"]


def test_standard_abruf_nimmt_pdf_bis_8_mb_an_html_bleibt_bei_3_mb(monkeypatch):
    aufrufe = []

    def fake_get(url, **kw):
        aufrufe.append(kw)
        return net.Fetched(url=url, status=200, content=b"<p>x</p>" * 400_000, content_type="text/html")
    monkeypatch.setattr(net, "safe_get", fake_get)
    with pytest.raises(net.ResponseTooLarge):
        nachtrag.standard_abruf("https://example.org/a", frist=5.0)
    kw = aufrufe[0]
    assert "application/pdf" in kw["accept"] and kw["max_bytes"] == 8_000_000 and kw["frist"] == 5.0
    assert all(t in kw["accept"] for t in net.TEXT_TYPES)


def test_html_quelle_unveraendert_neben_pdf(settings):
    with Store(settings.db_path) as store:
        e = pdf_annehmen(store, settings, pdf_vorschlag(URL1, PDF_URL), {PDF_URL: pdf_bytes([SEITE1, SEITE2])})
        docs = repo.dokumente(store, e["story_id"])
        assert [d.url for d in docs] == [URL1, PDF_URL] and docs[0].text == ARTIKEL1
        assert docs[0].titel == "Tempel eröffnet Gemeindehaus – Lokales"


# ---- Notanker: strukturierte Angaben (JSON-LD), wenn eine Seite ohne JavaScript keinen Text hat --------------

KINO_URL = "https://www.kino-beispiel.de/film/jailer-2"
KINO_LD = {"@context": "https://schema.org", "@graph": [
    {"@type": "Organization", "name": "Kino Beispiel GmbH"},
    {"@type": ["Movie"], "name": "Jailer 2", "inLanguage": "ta", "duration": "PT2H48M",
     "description": "Rajinikanth kehrt als pensionierter Gefängnisdirektor Muthuvel Pandian zurück und muss seine "
                    "Familie vor einem alten Gegner schützen. Der Film läuft in tamilischer Originalfassung mit "
                    "deutschen Untertiteln in ausgewählten Kinos in Deutschland, Österreich und der Schweiz.",
     "director": {"@type": "Person", "name": "Nelson Dilipkumar"},
     "actor": [{"@type": "Person", "name": "Rajinikanth"}, {"@type": "Person", "name": "Ramya Krishnan"}]},
    {"@type": "ScreeningEvent", "name": "Jailer 2 (OmU)", "startDate": "2026-06-12T20:00",
     "location": {"@type": "MovieTheater", "name": "Kino Beispiel Saal 3",
                  "address": {"@type": "PostalAddress", "streetAddress": "Hauptstraße 1", "postalCode": "50667",
                              "addressLocality": "Köln"}},
     "offers": [{"@type": "Offer", "price": "14.50", "priceCurrency": "EUR"}]}]}


def kino_html(ld, text: str = "") -> str:
    skript = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    return f"<html><head><title>Jailer 2 – Kino</title>{skript}</head><body><div id='app'></div>{text}</body></html>"


def html_seite(roh: str) -> net.Fetched:
    return net.Fetched(url=KINO_URL, status=200, content=roh.encode("utf-8"), content_type="text/html; charset=utf-8")


def test_seite_ohne_text_mit_json_ld_wird_zu_strukturierten_angaben(settings):
    v = vorschlag(arbeitstitel="Jailer 2 im Kino", rubrik="kino", ort="Köln", quellen=[
        {"url": KINO_URL, "titel": "t", "herausgeber": "Kino", "datum": "2026-06-01", "sprache": "de", "art": "kino"}])
    with Store(settings.db_path) as store:
        e = annehmen(store, settings, [v], seiten={KINO_URL: kino_html(KINO_LD)})["ergebnisse"][0]
        assert e["ergebnis"] == "angelegt", e
        doc = repo.dokumente(store, e["story_id"])[0]
        t = doc.text
        assert t.startswith("Angaben der Seite (strukturierte Daten)") and doc.titel == "Jailer 2 – Kino"
        for wert in ("Jailer 2", "Rajinikanth kehrt als pensionierter Gefängnisdirektor", "Nelson Dilipkumar",
                     "Ramya Krishnan", "PT2H48M", "2026-06-12T20:00", "Kino Beispiel Saal 3", "Hauptstraße 1",
                     "Köln", "14.50", "inLanguage: ta"):
            assert wert in t, wert
        assert "Kino Beispiel GmbH" not in t  # nur Movie, Event, ScreeningEvent, NewsArticle, Article


def test_json_ld_nur_als_notanker_und_nur_passende_typen():
    assert nachtrag.seite_lesen(html_seite(kino_html(KINO_LD, f"<article><p>{ARTIKEL1}</p></article>")))[0] == ARTIKEL1
    nur_firma = {"@type": "Organization", "name": "Kino Beispiel GmbH", "description": "x" * 400}
    kaputt = '<html><script type="application/ld+json">{kein json</script><body></body></html>'
    for roh in (kino_html(nur_firma), kaputt):
        assert nachtrag.seite_lesen(html_seite(roh))[0] == ""


# ---- PDF: Zeit- und Speichergrenze (Befund P1 der Code-Prüfung) --------------------------------------------

def pdf_roh(objekte: list[bytes]) -> bytes:
    """PDF von Hand: Objekte 1…n, xref, trailer (Root = 1)."""
    out, offs = bytearray(b"%PDF-1.4\n"), []
    for n, o in enumerate(objekte, 1):
        offs.append(len(out))
        out += b"%d 0 obj\n" % n + o + b"\nendobj\n"
    x = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objekte) + 1)
    out += b"".join(b"%010d 00000 n \n" % o for o in offs)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objekte) + 1, x)
    return bytes(out)


def pdf_aufwendig(mb: int, seiten: int, geteilt: bool = True) -> bytes:
    """Wie die Proben der Prüfung: ein großer Inhaltsstrom aus Leerraum-Operatoren, von allen Seiten referenziert
    (geteilt) oder je Seite ein eigener."""
    import zlib

    strom = zlib.compress(b"1 0 0 1 0 0 cm\n" * (mb * 1_000_000 // 15), 9)
    s_obj = b"<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(strom) + strom + b"\nendstream"
    n_stroeme = 1 if geteilt else seiten
    kids = " ".join(f"{3 + n_stroeme + i} 0 R" for i in range(seiten)).encode()
    objekte = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [%s] /Count %d >>" % (kids, seiten)]
    objekte += [s_obj] * n_stroeme
    objekte += [b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents %d 0 R >>" % (3 + (0 if geteilt else i))
                for i in range(seiten)]
    return pdf_roh(objekte)


@pytest.mark.parametrize("daten", [pdf_aufwendig(2, 40), pdf_aufwendig(10, 1), pdf_aufwendig(3, 5, geteilt=False)],
                         ids=["2MB-40-Seiten-geteilt", "10MB-eine-Seite", "3MB-je-Seite"])
def test_praeparierte_pdf_enden_schnell_mit_grund(settings, daten):
    import time

    t = time.monotonic()
    with Store(settings.db_path) as store:
        e = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL), {PDF_URL: daten})
    grund = e["quellen_uebersprungen"][0]["grund"]
    assert e["ergebnis"] == "abgelehnt" and (grund == "ohne lesbaren Text" or "PDF zu aufwendig" in grund), grund
    assert time.monotonic() - t < 6


def test_pdf_zeitlimit_beendet_den_kindprozess(monkeypatch):
    import sys
    import time

    monkeypatch.setattr(nachtrag, "PDF_BEFEHL", [sys.executable, "-c", "import time; time.sleep(30)"])
    monkeypatch.setattr(nachtrag, "PDF_ZEIT_MAX", 0.5)
    t = time.monotonic()
    with pytest.raises(nachtrag.Unlesbar, match="PDF zu aufwendig"):
        nachtrag.pdf_lesen(pdf_bytes([SEITE1]))
    assert time.monotonic() - t < 3
    with pytest.raises(nachtrag.Unlesbar, match="PDF zu aufwendig"):  # Frist schon vorbei: gar nicht erst starten
        nachtrag.pdf_lesen(pdf_bytes([SEITE1]), frist=time.monotonic() - 1)
    monkeypatch.setattr(nachtrag, "PDF_BEFEHL", [sys.executable, "-c", "import sys; sys.exit(9)"])
    with pytest.raises(nachtrag.Unlesbar, match="PDF zu aufwendig"):  # z. B. vom Speicherlimit beendet
        nachtrag.pdf_lesen(pdf_bytes([SEITE1]))


def test_pdf_mit_schleife_im_seitenbaum_endet_sauber():
    import time

    schleife = pdf_roh([b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [2 0 R 3 0 R] /Count 2 >>",
                        b"<< /Type /Pages /Parent 2 0 R /Kids [2 0 R] /Count 1 >>"])
    t = time.monotonic()
    with pytest.raises(nachtrag.Unlesbar, match="PDF"):
        nachtrag.pdf_lesen(schleife)
    assert time.monotonic() - t < 6


def test_json_ld_ohne_schliessende_tags_ist_linear_und_begrenzt():
    import time

    offen = '<script type="application/ld+json">{"@type": "Movie", "name": "x"' * 10000  # ~440 KB, nie geschlossen
    t = time.monotonic()
    assert nachtrag.strukturierte_angaben(offen) == ""
    assert time.monotonic() - t < 1
    film = {"@type": "Movie", "description": "Rajinikanth kehrt als Gefängnisdirektor zurück."}
    viele = "".join(f'<script type="application/ld+json">{json.dumps({**film, "name": f"Film {i}"})}</script>'
                    for i in range(40))
    text = nachtrag.strukturierte_angaben(viele)
    assert "Film 19" in text and "Film 20" not in text  # höchstens 20 Blöcke
    gross = '<script type="application/ld+json">' + json.dumps({**film, "name": "y" * 250_000}) + "</script>"
    assert nachtrag.strukturierte_angaben(gross) == ""  # zusammen höchstens 200 KB
