"""Kostendeckel je Story nach der Code-Prüfung von Sitzung B (P2).

Die Kosten der zweiten KI (Rolle „pruefer“) zählen nur gegen den vollen Deckel, nicht zusätzlich gegen den Anteil der
übrigen Schritte; jeder Schritt startet nur, wenn bisherige Summe plus Schätzung des Schritts in den Deckel passt.

- Realistische Kosten (Recherche, Text, Faktencheck je ~0,10 $, zweite KI 0,18 $ je Lauf), Endprüfung beanstandet
  einmal: die Story wird überarbeitet und fertig, nicht verworfen.
- Eine Endprüfung, die den Deckel wirklich überschreiten würde (0,90 $ verbraucht, Prüfung kostet ~0,30 $), startet
  nicht.
"""

from news_radar.store import Store
from news_radar.workflow import fake as fake_mod
from news_radar.workflow import jobs, orchestrator, repo
from news_radar.workflow.fake import FakeAnthropic
from news_radar.workflow.providers import usage_protokollieren

from test_nachrecherche import HAMM, hamm, settings  # noqa: F401

KOSTEN = {"recherche": 0.10, "text": 0.10, "faktencheck": 0.09, "lektorat": 0.01, "seo": 0.01, "pruefer": 0.18}


def _mit_kosten(store, rolle, usd, antwort):
    def responder(user, system, req):
        sid = repo.stories(store)[0]["id"]
        usage_protokollieren(store, rolle=rolle, provider="anthropic", modell="realistisch", usd=usd, story_id=sid)
        return antwort(user, system, req)
    return responder


def test_ueberarbeitung_nach_endpruefung_bei_realistischen_kosten(settings):
    settings.kosten_story_usd, settings.kosten_story_pruefung_usd = 1.0, 0.3
    laeufe = []

    def pruefer(user, system, req):
        daten = fake_mod.pruefer(user, system, req)
        laeufe.append(1)
        if len(laeufe) == 1 and daten.get("saetze"):  # erste Endprüfung: eine Kernaussage beanstandet
            daten["saetze"][0].update(urteil="ungedeckt", claim_ids=[], kern=True)
        return daten

    with Store(settings.db_path) as store:
        antworten = {r: _mit_kosten(store, r, usd, pruefer if r == "pruefer" else fake_mod.STANDARD[r])
                     for r, usd in KOSTEN.items()}
        client = FakeAnthropic(antworten)
        ctx = orchestrator.kontext(settings, store, client=client, fetch_text=lambda u: HAMM, suche=lambda q: [])
        orchestrator.scan(ctx, [hamm()])
        for _ in range(8):
            orchestrator.abarbeiten(ctx)
        story = repo.stories(store)[0]
        kosten = repo.kosten_story(store, story["id"])["usd"]
    assert len(laeufe) == 2 and client.rollen().count("text") == 2, (client.rollen(), story["notiz"])
    assert story["status"] == "fertig", (story["status"], story["notiz"], kosten)
    assert kosten <= 1.0


def test_endpruefung_startet_nicht_wenn_sie_den_deckel_ueberschreiten_wuerde(settings):
    settings.kosten_story_usd, settings.kosten_story_pruefung_usd = 1.0, 0.3
    with Store(settings.db_path) as store:
        client = FakeAnthropic()
        ctx = orchestrator.kontext(settings, store, client=client, fetch_text=lambda u: HAMM, suche=lambda q: [])
        orchestrator.scan(ctx, [hamm()])
        sid = repo.stories(store)[0]["id"]
        for rolle, usd in (("recherche", 0.2), ("text", 0.2), ("faktencheck", 0.2), ("pruefer", 0.3)):
            usage_protokollieren(store, rolle=rolle, provider="anthropic", modell="x", usd=usd, story_id=sid)
        store.db.execute("UPDATE workflow_jobs SET status = 'fertig' WHERE story_id = ?", (sid,))
        store.db.commit()
        repo.fassung_speichern(store, sid, "seo", {"titel": "Lichterfest", "teaser": "t", "inhalt_html": "<p>x</p>",
                                                   "kategorie": "news"}, von="test")
        jobs.einreihen(store, sid, "endpruefung", payload={})
        orchestrator.abarbeiten(ctx)
        story = repo.story(store, sid)
    assert client.requests == [] and story["status"] == "verworfen" and "Kostendeckel" in story["notiz"]
