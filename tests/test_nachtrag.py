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
        return abruf_aus(SEITEN)(ohne, frist)
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
        assert [d.url for d in repo.dokumente(store, beide["story_id"])] == [PDF_URL, PDF_URL + "#page=2"]  # 1 = ohne
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
        return net.Fetched(url=url, status=200, content=b"<p>x</p>", content_type="text/html")
    monkeypatch.setattr(net, "safe_get", fake_get)
    nachtrag.standard_abruf("https://example.org/a", frist=5.0)
    kw = aufrufe[0]  # die Grenze gilt schon beim Lesen, je gemeldetem Content-Type
    assert kw["max_bytes"] == 3_000_000 and kw["max_bytes_je_typ"] == {"application/pdf": 8_000_000}
    assert "application/pdf" in kw["accept"] and kw["frist"] == 5.0
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
        # Befund P3: kein sichtbarer Seitentext → art „daten“: Aussagen belegbar, aber kein langer Beitrag daraus
        from news_radar.agents import factcheck
        from news_radar.workflow.models import Claim

        assert doc.art == "daten" and doc.primaer
        claim = Claim(id="C1", aussage="Regie: Nelson Dilipkumar", art="wer", kern=True, quellen=[doc.doc_key],
                      fundstelle="director: Nelson Dilipkumar", sicherheit=0.9)
        assert factcheck.support(claim, {doc.doc_key: doc}, set()) == "bestaetigt"
        verlage, primaer, volltext = factcheck.stoff([doc])
        assert not primaer and not volltext
        assert factcheck.laenge_fuer("kino", 10, verlage, primaer, volltext) == "kino"  # nicht kino_lang/kino_mittel
        assert factcheck.laenge_fuer("news", 10, verlage, primaer, volltext) == "kurz"


def test_json_ld_nur_als_notanker_und_nur_passende_typen():
    # Seite mit Text: Film-Angaben (Movie) bleiben draußen; Termine (…Event mit startDate) hängt seite_lesen seit
    # 13.11.2026 an (eigener Test unten)
    text = nachtrag.seite_lesen(html_seite(kino_html(KINO_LD, f"<article><p>{ARTIKEL1}</p></article>")))[0]
    angehaengt = text[len(ARTIKEL1):]
    assert text.startswith(ARTIKEL1) and "startDate: 2026-06-12T20:00" in angehaengt
    assert "Nelson Dilipkumar" not in angehaengt  # Film-Angaben (Movie) nur als Notanker
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


def test_anker_nur_bei_pdf_und_page_1_wie_ohne_anker(settings):
    """Befund P2: der Anker darf die Dublettenprüfung nicht aushebeln (HTML-Anker, #page=1)."""
    anders = {"arbeitstitel": "Völlig anderes Thema aus Zürich", "ort": "Zürich"}
    datei = pdf_bytes([SEITE1, SEITE2])
    with Store(settings.db_path) as store:
        html_sid = annehmen(store, settings, [vorschlag(quellen=[vorschlag()["quellen"][0]])])["ergebnisse"][0]["story_id"]
        pdf_sid = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL), {PDF_URL: datei})["story_id"]
        for url, sid in ((URL1 + "#page=1", html_sid), (PDF_URL + "#page=1", pdf_sid)):
            e = pdf_annehmen(store, settings, pdf_vorschlag(url, **anders), {PDF_URL: datei})
            assert e["ergebnis"] == "vorhanden" and e["story_id"] == sid, (url, e)
        for url, sid in ((URL1 + "#page=2", html_sid), (PDF_URL + "#page=2", pdf_sid)):
            e = pdf_annehmen(store, settings, pdf_vorschlag(url, **anders), {PDF_URL: datei})
            assert e["ergebnis"] == "vielleicht_vorhanden" and e["story_id"] == sid, (url, e)
        neu = pdf_annehmen(store, settings, pdf_vorschlag(URL1 + "#page=2", erzwingen=True, **anders), {PDF_URL: datei})
        doc = repo.dokumente(store, neu["story_id"])[0]
        assert neu["ergebnis"] == "angelegt" and "#page" not in store.db.execute(
            "SELECT url_norm || uid FROM source_documents WHERE story_id = ?", (neu["story_id"],)).fetchone()[0]
        assert doc.text == ARTIKEL1  # HTML: der Anker ändert nichts am Text


def test_dieselbe_pdf_einmal_abgerufen_hoechstens_zwei_anker(settings):
    """Befund P2: mehrere Anker auf dieselbe Datei → ein Abruf, höchstens zwei Seiten je Datei."""
    abrufe = []
    v = pdf_vorschlag(PDF_URL + "#page=2", PDF_URL + "#page=3", PDF_URL + "#page=1", URL1)
    with Store(settings.db_path) as store:
        e = nachtrag.annehmen(store, settings, {"vorschlaege": [v]}, von="test", ctx=kontext(store, settings),
                              abruf=pdf_abruf({PDF_URL: pdf_bytes([SEITE1, SEITE2, SEITE1])}, abrufe))["ergebnisse"][0]
        assert e["ergebnis"] == "angelegt" and e["quellen_geholt"] == 3
        assert [a.split("#")[0] for a in abrufe] == [PDF_URL, URL1]  # die Datei nur einmal geholt
        assert e["quellen_uebersprungen"] == [{"url": PDF_URL + "#page=1", "grund": "höchstens zwei Seiten je Datei"}]
        assert [d.url for d in repo.dokumente(store, e["story_id"])] == [PDF_URL + "#page=2", PDF_URL + "#page=3", URL1]


def test_tief_verschachteltes_json_ld_wird_uebersprungen():
    """Befund P2: RecursionError beim Parsen bzw. in _ld_werte darf nicht nach außen dringen."""
    tief = '<script type="application/ld+json">' + "[" * 100_000 + "]" * 100_000 + "</script>"
    assert nachtrag.strukturierte_angaben(tief) == ""
    verschachtelt = {"name": "innen"}
    for _ in range(400):
        verschachtelt = {"name": verschachtelt}
    film = {"@type": "Movie", "name": "Jailer 2", "director": verschachtelt, "actor": [[[[[[["Tief"]]]]]]]}
    text = nachtrag.strukturierte_angaben(f'<script type="application/ld+json">{json.dumps(film)}</script>')
    assert "name: Jailer 2" in text and "innen" not in text and "Tief" not in text  # höchstens 5 Ebenen


def test_seite_lesen_linear_bei_nicht_geschlossenen_tags():
    import time

    for roh in ("<title>offen " * 40000, '<script type="application/ld+json">{"a":1}' * 10000,
                '<meta property="og:title" ' * 20000, '<meta content="x" property="og:title" ' * 20000):
        t = time.monotonic()
        nachtrag.seite_lesen(net.Fetched(url=URL1, status=200, content=roh.encode(), content_type="text/html"))
        assert time.monotonic() - t < 1, roh[:20]
    assert nachtrag.seite_lesen(net.Fetched(url=URL1, status=200, content=html(ARTIKEL1, "Titel &amp; mehr").encode(),
                                            content_type="text/html"))[1] == "Titel & mehr"
    og = ('<meta name="a" content="b"><meta content="Zweites Muster" property="og:title">'
          '<meta property="og:title" content="Erstes Muster"><title>Titel</title>')
    assert nachtrag.seite_lesen(net.Fetched(url=URL1, status=200, content=og.encode(),
                                            content_type="text/html"))[1] == "Erstes Muster"  # Reihenfolge wie bisher


def test_tuerkisches_i_verschiebt_keine_fundstellen():
    """Befund P1 (zweite Prüfung): „İ“.lower() hat zwei Zeichen; JSON-LD und og:title nach einem İ müssen bleiben."""
    vorn = "<nav>" + "İstanbul İzmir " * 40 + "</nav>"
    og = vorn + '<meta property="og:title" content="Kulturabend in İstanbul"><title>Andere</title>'
    assert nachtrag.seite_lesen(net.Fetched(url=URL1, status=200, content=og.encode(),
                                            content_type="text/html"))[1] == "Kulturabend in İstanbul"
    ld = vorn + kino_html(KINO_LD)
    assert "name: Jailer 2" in nachtrag.strukturierte_angaben(ld)
    assert nachtrag.strukturierte_angaben(ld) == nachtrag.strukturierte_angaben(kino_html(KINO_LD))


def test_hoechstens_zwei_pdf_kinder_gleichzeitig(monkeypatch):
    """Befund P2 (zweite Prüfung): je Kind bis 300 MB, also höchstens zwei zugleich; wer in der Frist nicht
    drankommt, bekommt „PDF zu aufwendig“."""
    import subprocess
    import threading
    import time

    from news_radar import pdf_kind

    assert pdf_kind.SPEICHER_MAX == 300 * 1024 * 1024
    stand = {"jetzt": 0, "max": 0}
    sperre = threading.Lock()

    def fake_run(befehl, **kw):
        with sperre:
            stand["jetzt"] += 1
            stand["max"] = max(stand["max"], stand["jetzt"])
        time.sleep(0.2)
        with sperre:
            stand["jetzt"] -= 1
        return subprocess.CompletedProcess(befehl, 0, stdout=b'{"text": "x", "titel": ""}', stderr=None)
    monkeypatch.setattr(nachtrag.subprocess, "run", fake_run)
    faeden = [threading.Thread(target=nachtrag.pdf_lesen, args=(b"%PDF-1.4",)) for _ in range(6)]
    for f in faeden:
        f.start()
    for f in faeden:
        f.join()
    assert stand["max"] == 2
    belegt = [nachtrag._PDF_PLAETZE.acquire() for _ in range(nachtrag.PDF_PARALLEL)]
    try:
        t = time.monotonic()
        with pytest.raises(nachtrag.Unlesbar, match="PDF zu aufwendig"):
            nachtrag.pdf_lesen(b"%PDF-1.4", frist=time.monotonic() + 0.3)
        assert time.monotonic() - t < 1.5
    finally:
        for _ in belegt:
            nachtrag._PDF_PLAETZE.release()


def _aufruf_merken(monkeypatch) -> dict:
    import subprocess

    aufruf = {}

    def fake_run(befehl, **kw):
        aufruf.update(kw)
        return subprocess.CompletedProcess(befehl, 0, stdout=b'{"text": "x", "titel": ""}', stderr=None)
    monkeypatch.setattr(nachtrag.subprocess, "run", fake_run)
    return aufruf


def test_pdf_kind_stderr_verworfen_und_warnungen_aus(monkeypatch):
    """Befund P2 (zweite Prüfung): stderr des Kindes (pypdf-Warnungen, 15 MB) nicht im Web-Worker sammeln."""
    import subprocess

    aufruf = _aufruf_merken(monkeypatch)
    nachtrag.pdf_lesen(b"%PDF-1.4")
    assert aufruf["stderr"] is subprocess.DEVNULL and aufruf["stdout"] is subprocess.PIPE
    assert "capture_output" not in aufruf
    quelle = (nachtrag.Path(nachtrag.__file__).with_name("pdf_kind.py")).read_text(encoding="utf-8")
    assert "logging.disable(logging.WARNING)" in quelle


def test_pdf_kind_bekommt_nur_eine_kleine_umgebung(monkeypatch):
    """Befund P3 (zweite Prüfung): keine Geheimnisse aus der Umgebung des Web-Prozesses im Kind."""
    monkeypatch.setenv("RADAR_AGENT_TOKEN", "geheim-nicht-ins-kind")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "geheim-auch-nicht")
    aufruf = _aufruf_merken(monkeypatch)
    nachtrag.pdf_lesen(b"%PDF-1.4")
    assert aufruf["env"] is not None and set(aufruf["env"]) <= {"PATH", "LANG", "LC_ALL"}
    assert "geheim" not in str(aufruf["env"])


def test_pdf_lesen_hat_eigene_frist_nach_dem_abruf(settings):
    """Befund P3 (zweite Prüfung): die Abruf-Frist ist verbraucht, das Lesen bekommt trotzdem seine eigene Zeit."""
    with Store(settings.db_path) as store:
        e = nachtrag.annehmen(store, settings, {"vorschlaege": [pdf_vorschlag(PDF_URL)]}, von="test",
                              ctx=kontext(store, settings), abruf=pdf_abruf({PDF_URL: pdf_bytes([SEITE1, SEITE2])}),
                              frist_abruf=0.000001)["ergebnisse"][0]
        assert e["ergebnis"] == "angelegt", e


def test_doppelte_adresse_wird_vor_dem_lesen_erkannt(settings, monkeypatch):
    gelesen = []
    echt = nachtrag.pdf_lesen
    monkeypatch.setattr(nachtrag, "pdf_lesen", lambda daten, ab_seite=1, frist=None: (gelesen.append(ab_seite)
                                                                                      or echt(daten, ab_seite, frist)))
    with Store(settings.db_path) as store:
        e = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL + "#page=2", PDF_URL + "#page=2"),
                         {PDF_URL: pdf_bytes([SEITE1, SEITE2])})
    assert e["ergebnis"] == "angelegt" and gelesen == [2]
    assert e["quellen_uebersprungen"] == [{"url": PDF_URL + "#page=2", "grund": "doppelt im Vorschlag"}]


def _pdf_text_und_schwer(seiten: list) -> bytes:
    """Seiten aus Textzeilen (Liste) oder einem schweren Strom (Zahl = MB Leerraum-Operatoren)."""
    import zlib

    objekte = [b"<< /Type /Catalog /Pages 2 0 R >>", b"", b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    for s in seiten:
        if isinstance(s, list):
            ops = b"BT /F1 10 Tf 12 TL 40 800 Td " + b" ".join(b"(" + z.encode("latin-1") + b") Tj T*" for z in s) + b" ET"
            objekte.append(b"<< /Length %d >>\nstream\n" % len(ops) + ops + b"\nendstream")
        else:
            roh = zlib.compress(b"1 0 0 1 0 0 cm\n" * (s * 1_000_000 // 15), 9)
            objekte.append(b"<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(roh) + roh + b"\nendstream")
    erste = len(objekte) + 1
    for n in range(len(seiten)):
        objekte.append(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >>"
                       b" /Contents %d 0 R >>" % (4 + n))
    kids = " ".join(f"{erste + n} 0 R" for n in range(len(seiten))).encode()
    objekte[1] = b"<< /Type /Pages /Kids [%s] /Count %d >>" % (kids, len(seiten))
    return pdf_roh(objekte)


def test_pdf_zu_aufwendige_seite_kuerzt_lueckenlos_mit_hinweis(settings):
    """Befund P3 (zweite Prüfung): nie still Seiten überspringen. Gelesen wird ein lückenloser Anfang bis vor die
    erste zu aufwendige Seite, mit Hinweis „gekürzt“; ist schon die Startseite zu aufwendig: abgelehnt."""
    zeilen = [z.replace("ä", "ae").replace("ü", "ue") for z in SEITE1]
    datei = _pdf_text_und_schwer([zeilen, 3, ["Diese Seite nach der schweren darf nicht im Text stehen."]])
    with Store(settings.db_path) as store:
        e = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL), {PDF_URL: datei})
        assert e["ergebnis"] == "angelegt", e
        text = repo.dokumente(store, e["story_id"])[0].text
        assert "Kleine Anfrage" in text and "nach der schweren" not in text
        assert e["quellen_hinweise"] == [{"url": PDF_URL, "hinweis": "gekürzt: gelesen bis Seite 1, Seite 2 zu aufwendig"}]
        schwer = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL + "#page=2", erzwingen=True,
                                                             arbeitstitel="Nur die schwere Seite"), {PDF_URL: datei})
        assert schwer["ergebnis"] == "abgelehnt" and "PDF zu aufwendig" in schwer["quellen_uebersprungen"][0]["grund"]


# ---- Nachtrag ergänzen (story_id) -------------------------------------------------------------------------

URL3 = "https://www.wdr.de/nachrichten/tempel-hamm-gemeindehaus-gaeste-100.html"
ARTIKEL3 = ("Zur Eröffnung des Gemeindehauses am Sri-Kamadchi-Ampal-Tempel in Hamm kamen nach Zählung der Polizei "
            "rund 2500 Menschen. Der Bau hat nach Angaben des Tempelvereins 1,2 Millionen Euro gekostet, finanziert "
            "fast vollständig aus Spenden der Gemeinde. Im Erdgeschoss liegen ein Saal für 400 Personen und eine "
            "Küche, im Obergeschoss sechs Unterrichtsräume für Tamil, Musik und Tanz.")
SEITEN3 = {**SEITEN, URL3: html(ARTIKEL3, "Tempel Hamm: Gemeindehaus eröffnet - WDR")}


def nachtrag_mit_luecke(store, settings, quellen=None, status="recherche_erforderlich"):
    """Nachtrag-Story, deren Import an fehlenden Kernfakten gescheitert ist."""
    quellen = quellen or [vorschlag()["quellen"][0]]
    sid = annehmen(store, settings, [vorschlag(quellen=quellen)])["ergebnisse"][0]["story_id"]
    repo.story_setzen(store, sid, status=status, notiz="Fehlt: Zahl der Gäste laut Polizei")
    return sid


def quelle(url, **kw):
    return {"url": url, "titel": "t", "herausgeber": "WDR", "datum": "2026-03-15", "sprache": "de", "art": "bericht",
            **kw}


def test_ergaenzen_haengt_neue_quellen_an_und_gibt_die_story_wieder_frei(settings):
    with Store(settings.db_path) as store:
        sid = nachtrag_mit_luecke(store, settings)
        abrufe = []
        out = annehmen(store, settings, [vorschlag(
            story_id=sid, arbeitstitel="Ganz anderer Arbeitstitel ohne Ähnlichkeit", datum="2026-03-15",
            quellen=[quelle(URL1), quelle(URL2), quelle(URL3)], kernfakten=["rund 2500 Menschen laut Polizei"],
            bezug="Neuer Bezug", bild_hinweis="Saal", erzwingen=True)], seiten=SEITEN3, abrufe=abrufe)
        e = out["ergebnisse"][0]
        assert e["ergebnis"] == "ergaenzt" and e["story_id"] == sid and e["quellen_geholt"] == 2, e
        assert e["quellen_uebersprungen"] == [{"url": URL1, "grund": "schon Beleg dieser Story"}]
        assert out["ergaenzt"] == 1 and out["angelegt"] == 0 and len(repo.stories(store)) == 1
        assert URL1 not in abrufe  # schon Beleg: nicht noch einmal geholt
        s = repo.story(store, sid)
        heute = kontext(store, settings).uhr().date().isoformat()
        assert s["status"] == "neu" and s["ereignis_datum"] == "2026-03-14"  # Datum der Story bleibt
        assert e["hinweis"] == "Datum der Story bleibt 2026-03-14"
        assert s["titel"] == "Tempel in Hamm eröffnet Gemeindehaus"  # der Arbeitstitel ändert die Story nicht
        assert s["notiz"].startswith("Fehlt: Zahl der Gäste laut Polizei")
        assert f"Ergänzt am {heute}: 2 Quellen" in s["notiz"]
        docs = repo.dokumente(store, sid)
        assert [d.doc_key for d in docs] == ["Q1", "Q2", "Q3"]
        assert [d.text for d in docs] == [ARTIKEL1, ARTIKEL2, ARTIKEL3]
        assert docs[2].titel == "Tempel Hamm: Gemeindehaus eröffnet - WDR" and docs[2].publisher == "WDR"
        zeile = store.db.execute("SELECT * FROM editorial_actions WHERE aktion = 'nachtrag_ergaenzt'").fetchone()
        assert zeile["story_id"] == sid and zeile["wer"] == "test" and zeile["kanal"] == "redaktion"
        mappe = paket_v2(store, settings, ctx=kontext(store, settings))
        p = next(p for p in mappe["storys"] if p["story_id"] == sid)
        assert [d["doc_key"] for d in p["dokumente"]] == ["Q1", "Q2", "Q3"]
        h = p["vorschlag_hinweise"]
        assert h["kernfakten"] == ["rund 2500 Menschen laut Polizei", "Eröffnung am 14. März 2026", "rund 2000 Gäste"]
        assert h["bezug"] == "Neuer Bezug"
        assert h["bild_hinweis"] == "Saal"


def test_ergaenzen_ohne_neue_quelle_ist_vorhanden_und_holt_nichts(settings):
    with Store(settings.db_path) as store:
        sid = nachtrag_mit_luecke(store, settings, quellen=vorschlag()["quellen"])
        abrufe = []
        e = annehmen(store, settings, [vorschlag(story_id=sid, datum="2026-03-20")], abrufe=abrufe)["ergebnisse"][0]
        assert e["ergebnis"] == "vorhanden" and e["story_id"] == sid and abrufe == []
        assert [u["grund"] for u in e["quellen_uebersprungen"]] == ["schon Beleg dieser Story"] * 2
        s = repo.story(store, sid)
        assert s["status"] == "recherche_erforderlich" and s["ereignis_datum"] == "2026-03-14"


@pytest.mark.parametrize("status", ["fertig", "verworfen", "geschrieben", "neu"])
def test_ergaenzen_nur_bei_recherche_noetig_oder_neu(settings, status):
    with Store(settings.db_path) as store:
        sid = nachtrag_mit_luecke(store, settings, status=status)
        abrufe = []
        e = annehmen(store, settings, [vorschlag(story_id=sid, quellen=[quelle(URL3)])], seiten=SEITEN3,
                     abrufe=abrufe)["ergebnisse"][0]
        assert e["ergebnis"] == "abgelehnt" and e["grund"] == "Story nicht ergänzbar" and abrufe == []
        log = [json.loads(z["data"]) for z in store.db.execute(
            "SELECT data FROM log WHERE event = 'nachtrag_ergaenzen_abgelehnt'")]
        assert log == [{"story": sid, "grund": f"Story ist {status}", "von": "test"}]
        assert len(repo.dokumente(store, sid)) == 1


def test_ergaenzen_nicht_bei_vorhandenem_entwurf(settings):
    """Nur „Recherche nötig“ ohne Entwurf: sonst könnte ein gleichzeitiger Import die neue Quelle am Gate vorbei
    unter „weitere Quellen“ führen."""
    with Store(settings.db_path) as store:
        sid = nachtrag_mit_luecke(store, settings)
        store.insert_draft({"uid": "entwurf-1", "titel": "Entwurf", "story_id": sid})
        abrufe = []
        e = annehmen(store, settings, [vorschlag(story_id=sid, quellen=[quelle(URL3)])], seiten=SEITEN3,
                     abrufe=abrufe)["ergebnisse"][0]
        assert e["ergebnis"] == "abgelehnt" and abrufe == [] and len(repo.dokumente(store, sid)) == 1, e


def test_ergaenzen_unbekannte_fremde_oder_beschaeftigte_story_wird_abgelehnt(settings):
    with Store(settings.db_path) as store:
        radar = repo.story_anlegen(store, typ="news", titel="Story vom Scan")
        repo.story_setzen(store, radar, status="recherche_erforderlich")
        sid = nachtrag_mit_luecke(store, settings)
        ts = "2026-03-20T10:00:00+00:00"
        store.db.execute("INSERT INTO workflow_jobs (story_id, schritt, status, naechster_versuch, erstellt, "
                         "aktualisiert) VALUES (?, 'recherche', 'laeuft', ?, ?, ?)", (sid, ts, ts, ts))
        store.db.commit()
        abrufe = []
        gruende = {}
        for ziel in (99999, radar, sid, 0, "7", True):
            e = annehmen(store, settings, [vorschlag(story_id=ziel, quellen=[quelle(URL3)])], seiten=SEITEN3,
                         abrufe=abrufe)["ergebnisse"][0]
            assert e["ergebnis"] == "abgelehnt", (ziel, e)
            gruende[repr(ziel)] = e["grund"]
        assert gruende["99999"] == gruende[repr(radar)] == "Story nicht ergänzbar"  # einheitlich nach außen
        details = {json.loads(z["data"])["grund"] for z in store.db.execute(
            "SELECT data FROM log WHERE event = 'nachtrag_ergaenzen_abgelehnt'")}
        assert {"Story nicht gefunden", "keine Nachtrag-Story"} <= details
        assert "läuft gerade ein Job" in gruende[repr(sid)]
        assert all(g.startswith("story_id") for k, g in gruende.items() if k in ("0", "'7'", "True")), gruende
        assert abrufe == [] and len(repo.dokumente(store, sid)) == 1


def test_ergaenzen_status_aendert_sich_waehrend_der_abrufe_nichts_geschrieben(settings):
    with Store(settings.db_path) as store:
        sid = nachtrag_mit_luecke(store, settings)
        basis = abruf_aus(SEITEN3)

        def abruf(url, frist=None):  # während der Abrufe erzeugt ein Import einen Entwurf
            repo.story_setzen(store, sid, status="geschrieben")
            return basis(url, frist)
        e = nachtrag.annehmen(store, settings, {"vorschlaege": [vorschlag(story_id=sid, quellen=[quelle(URL3)])]},
                              von="test", ctx=kontext(store, settings), abruf=abruf)["ergebnisse"][0]
        assert e["ergebnis"] == "abgelehnt" and e["grund"] == "Story inzwischen geschrieben"
        s = repo.story(store, sid)
        assert s["status"] == "geschrieben" and "Ergänzt" not in s["notiz"] and len(repo.dokumente(store, sid)) == 1
        assert store.db.execute(
            "SELECT COUNT(*) FROM editorial_actions WHERE aktion = 'nachtrag_ergaenzt'").fetchone()[0] == 0


def test_ergaenzen_pdf_mit_anker_wird_angehaengt_gleiche_seite_uebersprungen(settings):
    datei = pdf_bytes([SEITE1, SEITE2, SEITE1])
    with Store(settings.db_path) as store:
        sid = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL + "#page=2"), {PDF_URL: datei})["story_id"]
        repo.story_setzen(store, sid, status="recherche_erforderlich", notiz="Fehlt: Zahl")
        e = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL + "#page=2", PDF_URL + "#page=3", story_id=sid),
                         {PDF_URL: datei})
        assert e["ergebnis"] == "ergaenzt" and e["quellen_geholt"] == 1 and "hinweis" not in e, e
        assert e["quellen_uebersprungen"] == [{"url": PDF_URL + "#page=2", "grund": "schon Beleg dieser Story"}]
        docs = repo.dokumente(store, sid)
        assert [(d.doc_key, d.url) for d in docs] == [("Q1", PDF_URL + "#page=2"), ("Q2", PDF_URL + "#page=3")]
        assert docs[1].text.startswith("Deutscher Bundestag")


def test_ergaenzen_haelt_beim_stopp_an(settings):
    with Store(settings.db_path) as store:
        sid = nachtrag_mit_luecke(store, settings)
        schalter.setzen(store, "redaktion", True, wer="anna", grund="Prüfen")
        abrufe = []
        with pytest.raises(schalter.Gestoppt):
            annehmen(store, settings, [vorschlag(story_id=sid, quellen=[quelle(URL3)])], seiten=SEITEN3, abrufe=abrufe)
        assert abrufe == [] and len(repo.dokumente(store, sid)) == 1


def test_ergaenzen_ueber_route_und_cli(settings, monkeypatch, tmp_path, capsys):
    from news_radar.__main__ import main
    from news_radar.web import create_app

    monkeypatch.setattr(nachtrag, "standard_abruf", abruf_aus(SEITEN3))
    monkeypatch.setenv("RADAR_DATA_DIR", str(settings.data_dir))
    with Store(settings.db_path) as store:
        sid = nachtrag_mit_luecke(store, settings)
    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim", "s3cret"
    settings.agent_token = "agent-token-mit-genug-zeichen"
    client = create_app(settings, testing=True).test_client()
    resp = client.post("/api/agent/vorschlag", json={"vorschlaege": [vorschlag(story_id=sid, quellen=[quelle(URL3)])]},
                       headers={"Authorization": "Bearer agent-token-mit-genug-zeichen"})
    data = resp.get_json()
    assert resp.status_code == 200 and data["ergaenzt"] == 1 and data["ergebnisse"][0]["ergebnis"] == "ergaenzt"
    with Store(settings.db_path) as store:
        repo.story_setzen(store, sid, status="recherche_erforderlich")
    datei = tmp_path / "v.json"
    datei.write_text(json.dumps([vorschlag(story_id=sid, quellen=[quelle(URL2)])]), encoding="utf-8")
    assert main(["agent", "vorschlag", "--datei", str(datei)]) == 0
    assert "1 ergänzt" in capsys.readouterr().out
    with Store(settings.db_path) as store:
        assert [d.doc_key for d in repo.dokumente(store, sid)] == ["Q1", "Q2", "Q3"]


def test_ergaenzen_riesige_story_id_wird_abgelehnt_und_der_stapel_laeuft_weiter(settings):
    with Store(settings.db_path) as store:
        sid = nachtrag_mit_luecke(store, settings)
        out = annehmen(store, settings, [vorschlag(story_id=2**63, quellen=[quelle(URL3)]),
                                         vorschlag(story_id=2**31, quellen=[quelle(URL3)]),
                                         vorschlag(story_id=sid, quellen=[quelle(URL3)])], seiten=SEITEN3)
        e = out["ergebnisse"]
        assert [x["ergebnis"] for x in e] == ["abgelehnt", "abgelehnt", "ergaenzt"], e
        assert e[0]["grund"].startswith("story_id") and e[1]["grund"].startswith("story_id")


def test_ergaenzen_zaehlt_vorhandene_seiten_derselben_datei_mit(settings):
    datei = pdf_bytes([SEITE1, SEITE2, SEITE1, SEITE2])
    with Store(settings.db_path) as store:
        sid = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL + "#page=2"), {PDF_URL: datei})["story_id"]
        repo.story_setzen(store, sid, status="recherche_erforderlich")
        e = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL + "#page=3", story_id=sid), {PDF_URL: datei})
        assert e["ergebnis"] == "ergaenzt", e
        repo.story_setzen(store, sid, status="recherche_erforderlich")
        abrufe = []
        e = nachtrag.annehmen(store, settings, {"vorschlaege": [pdf_vorschlag(PDF_URL + "#page=4", story_id=sid)]},
                              von="test", ctx=kontext(store, settings), abruf=pdf_abruf({PDF_URL: datei}, abrufe))
        e = e["ergebnisse"][0]
        assert e["ergebnis"] == "abgelehnt" and abrufe == [], e
        assert e["quellen_uebersprungen"] == [{"url": PDF_URL + "#page=4", "grund": "höchstens zwei Seiten je Datei"}]
        assert len(repo.dokumente(store, sid)) == 2


def test_ergaenzen_hoechstens_zehn_dokumente_je_story(settings):
    with Store(settings.db_path) as store:
        sid = nachtrag_mit_luecke(store, settings)
        for n in range(8):
            repo.dokument_hinzufuegen(store, sid, url=f"https://www.example.org/bericht-{n}", text=ARTIKEL1)
        e = annehmen(store, settings, [vorschlag(story_id=sid, quellen=[quelle(URL3), quelle(URL2)])],
                     seiten=SEITEN3)["ergebnisse"][0]
        assert e["ergebnis"] == "ergaenzt" and e["quellen_geholt"] == 1, e
        assert e["quellen_uebersprungen"] == [{"url": URL2, "grund": "höchstens 10 Dokumente je Story"}]
        repo.story_setzen(store, sid, status="recherche_erforderlich")
        abrufe = []
        e = annehmen(store, settings, [vorschlag(story_id=sid, quellen=[quelle(URL2)])], seiten=SEITEN3,
                     abrufe=abrufe)["ergebnisse"][0]
        assert e["ergebnis"] == "abgelehnt" and abrufe == [] and len(repo.dokumente(store, sid)) == 10


def test_ergaenzen_seitengrenze_auch_in_der_schreibtransaktion(settings):
    datei = pdf_bytes([SEITE1, SEITE2, SEITE1, SEITE2, SEITE1])
    with Store(settings.db_path) as store:
        sid = pdf_annehmen(store, settings, pdf_vorschlag(PDF_URL + "#page=2"), {PDF_URL: datei})["story_id"]
        repo.story_setzen(store, sid, status="recherche_erforderlich")
        basis = pdf_abruf({PDF_URL: datei})

        def abruf(url, frist=None):  # ein gleichzeitiger Aufruf hängt Seite 5 an
            repo.dokument_hinzufuegen(store, sid, url=PDF_URL + "#page=5", text="x" * 400)
            return basis(url, frist)
        e = nachtrag.annehmen(store, settings, {"vorschlaege": [pdf_vorschlag(PDF_URL + "#page=3", story_id=sid)]},
                              von="test", ctx=kontext(store, settings), abruf=abruf)["ergebnisse"][0]
        assert e["ergebnis"] == "abgelehnt" and "höchstens zwei Seiten je Datei" in e["grund"], e
        assert [d.url for d in repo.dokumente(store, sid)] == [PDF_URL + "#page=2", PDF_URL + "#page=5"]


def test_ergaenzen_fuehrt_hinweise_zusammen(settings):
    with Store(settings.db_path) as store:
        sid = nachtrag_mit_luecke(store, settings)
        e = annehmen(store, settings, [vorschlag(story_id=sid, quellen=[quelle(URL3)], bezug="", bild_hinweis="",
                                                 kernfakten=["rund 2500 Menschen", "rund 2000 Gäste"])],
                     seiten=SEITEN3)["ergebnisse"][0]
        assert e["ergebnis"] == "ergaenzt", e
        h = json.loads(repo.story(store, sid)["vorschlag"])
        assert h["bezug"] == "Größter Hindu-Tempel Deutschlands, Treffpunkt der Community"
        assert h["bild_hinweis"] == "Foto der Einweihung"
        assert h["kernfakten"] == ["rund 2500 Menschen", "rund 2000 Gäste", "Eröffnung am 14. März 2026"]
        repo.story_setzen(store, sid, status="recherche_erforderlich")
        viele = [f"Fakt {n}" for n in range(12)]
        annehmen(store, settings, [vorschlag(story_id=sid, quellen=[quelle(URL2)], kernfakten=viele)])
        assert json.loads(repo.story(store, sid)["vorschlag"])["kernfakten"] == viele  # höchstens 12, neue zuerst


def test_ergaenzen_heikel_stuft_nur_hoch(settings):
    with Store(settings.db_path) as store:
        sid = nachtrag_mit_luecke(store, settings)
        assert repo.story(store, sid)["sensibel"] == 0
        annehmen(store, settings, [vorschlag(story_id=sid, heikel=True, quellen=[quelle(URL3)])], seiten=SEITEN3)
        assert repo.story(store, sid)["sensibel"] == 1
        repo.story_setzen(store, sid, status="recherche_erforderlich")
        e = annehmen(store, settings, [vorschlag(story_id=sid, heikel=False, quellen=[quelle(URL2)])])["ergebnisse"][0]
        assert e["ergebnis"] == "ergaenzt" and repo.story(store, sid)["sensibel"] == 1


def test_ergaenzen_job_beginnt_waehrend_der_abrufe_nichts_geschrieben(settings):
    with Store(settings.db_path) as store:
        sid = nachtrag_mit_luecke(store, settings)
        basis = abruf_aus(SEITEN3)

        def abruf(url, frist=None):  # ein Worker greift die Story zwischen erster Prüfung und Transaktion
            ts = "2026-03-20T10:00:00+00:00"
            store.db.execute("INSERT INTO workflow_jobs (story_id, schritt, status, naechster_versuch, erstellt, "
                             "aktualisiert) VALUES (?, 'recherche', 'laeuft', ?, ?, ?)", (sid, ts, ts, ts))
            store.db.commit()
            return basis(url, frist)
        e = nachtrag.annehmen(store, settings, {"vorschlaege": [vorschlag(story_id=sid, quellen=[quelle(URL3)])]},
                              von="test", ctx=kontext(store, settings), abruf=abruf)["ergebnisse"][0]
        assert e["ergebnis"] == "abgelehnt" and e["grund"] == "an der Story läuft gerade ein Job", e
        s = repo.story(store, sid)
        assert s["status"] == "recherche_erforderlich" and len(repo.dokumente(store, sid)) == 1


def test_ergaenzen_setzt_doc_key_nach_dem_hoechsten_fort(settings):
    with Store(settings.db_path) as store:
        sid = nachtrag_mit_luecke(store, settings)
        for n in (2, 3):
            repo.dokument_hinzufuegen(store, sid, url=f"https://www.example.org/bericht-{n}", text=ARTIKEL1)
        store.db.execute("DELETE FROM source_documents WHERE story_id = ? AND doc_key = 'Q2'", (sid,))
        store.db.commit()
        e = annehmen(store, settings, [vorschlag(story_id=sid, quellen=[quelle(URL3)])], seiten=SEITEN3)["ergebnisse"][0]
        assert e["ergebnis"] == "ergaenzt", e
        assert [d.doc_key for d in repo.dokumente(store, sid)] == ["Q1", "Q3", "Q4"]


def test_dokument_hinzufuegen_vergibt_doc_key_nach_dem_hoechsten(settings):
    """Cockpit „Quelle ergänzen“: nach einer Lücke (Q1, Q3) nicht COUNT+1 = Q3 doppelt, sondern Q4."""
    with Store(settings.db_path) as store:
        sid = repo.story_anlegen(store, typ="news", titel="Story mit Lücke")
        for n in (1, 2, 3):
            repo.dokument_hinzufuegen(store, sid, url=f"https://www.example.org/bericht-{n}", text=ARTIKEL1)
        store.db.execute("DELETE FROM source_documents WHERE story_id = ? AND doc_key = 'Q2'", (sid,))
        store.db.commit()
        assert repo.dokument_hinzufuegen(store, sid, url="https://www.example.org/neu", text=ARTIKEL2) == "Q4"


# ---- Termindaten aus strukturierten Angaben (13.11.2026: Eventfrog-Seiten mit Text, Termine nur im JSON-LD) -----

TERMIN_URL = "https://eventfrog.ch/de/p/kino/kino/scene-kino-claudia-zh-suriya-2nd-week-kloten-75.html"
TERMIN_LD = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"Event",'
             '"name":"SCENE - KINO CLAUDIA - ZH (SURIYA) 2nd WEEK","startDate":"2026-11-14T13:00:00+01:00",'
             '"location":{"@type":"Place","name":"Kino Claudia","address":{"@type":"PostalAddress",'
             '"streetAddress":"Schaffhauserstrasse 76","postalCode":"8302","addressLocality":"Kloten"}}}</script>')
TERMIN_TEXT = ("Suriyas Film Scene läuft in der zweiten Woche im Kino Claudia. Tamilische Fassung mit englischen "
               "Untertiteln. Tickets gibt es online und an der Abendkasse, solange Plätze frei sind. ") * 2


def termin_html(text=TERMIN_TEXT, ld=TERMIN_LD):
    return f"<html><head><title>SCENE - Kino Claudia</title>{ld}</head><body><article><p>{text}</p></article></body></html>"


def test_terminseite_mit_text_behaelt_die_strukturierten_termindaten():
    seite = net.Fetched(url=TERMIN_URL, status=200, content=termin_html().encode("utf-8"),
                        content_type="text/html; charset=utf-8")
    text, titel, art, _ = nachtrag.seite_lesen(seite, TERMIN_URL)
    assert art == "volltext" and "zweiten Woche im Kino Claudia" in text
    assert "startDate: 2026-11-14T13:00:00+01:00" in text
    assert "location.address: Schaffhauserstrasse 76 8302 Kloten" in text


def test_artikelseite_ohne_termin_bekommt_keinen_datenblock():
    ld = ('<script type="application/ld+json">{"@type":"NewsArticle","headline":"x",'
          '"datePublished":"2026-03-14"}</script>')
    seite = net.Fetched(url=URL1, status=200, content=termin_html(ARTIKEL1 * 2, ld).encode("utf-8"),
                        content_type="text/html; charset=utf-8")
    text, _, art, _ = nachtrag.seite_lesen(seite, URL1)
    assert art == "volltext" and nachtrag.LD_KOPF not in text


def test_ergaenzen_neu_abrufen_aktualisiert_vorhandene_quellen(settings):
    with Store(settings.db_path) as store:
        alt = termin_html(ld="")
        sid = annehmen(store, settings, [vorschlag(quellen=[quelle(TERMIN_URL)])],
                       seiten={TERMIN_URL: alt})["ergebnisse"][0]["story_id"]
        repo.story_setzen(store, sid, status="recherche_erforderlich")
        assert "startDate" not in repo.dokumente(store, sid)[0].text
        abrufe = []
        e = annehmen(store, settings, [vorschlag(story_id=sid, quellen=[quelle(TERMIN_URL)], neu_abrufen=True)],
                     seiten={TERMIN_URL: termin_html()}, abrufe=abrufe)["ergebnisse"][0]
        assert e["ergebnis"] == "ergaenzt" and e.get("aktualisiert") == 1 and e["quellen_geholt"] == 0, e
        assert abrufe == [TERMIN_URL]
        docs = repo.dokumente(store, sid)
        assert [d.doc_key for d in docs] == ["Q1"] and "startDate: 2026-11-14T13:00:00+01:00" in docs[0].text
        assert repo.story(store, sid)["status"] == "neu"


def test_ergaenzen_neu_abrufen_ohne_aenderung_ist_vorhanden(settings):
    with Store(settings.db_path) as store:
        sid = annehmen(store, settings, [vorschlag(quellen=[quelle(TERMIN_URL)])],
                       seiten={TERMIN_URL: termin_html()})["ergebnisse"][0]["story_id"]
        repo.story_setzen(store, sid, status="recherche_erforderlich")
        e = annehmen(store, settings, [vorschlag(story_id=sid, quellen=[quelle(TERMIN_URL)], neu_abrufen=True)],
                     seiten={TERMIN_URL: termin_html()})["ergebnisse"][0]
        assert e["ergebnis"] == "vorhanden" and repo.story(store, sid)["status"] == "recherche_erforderlich"
