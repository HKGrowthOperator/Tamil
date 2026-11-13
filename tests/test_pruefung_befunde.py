"""Befunde der unabhängigen Prüfung (13.11.2026) zur Nachrecherche und zweiten KI, plus ein Fehler aus dem Live-Betrieb.

P1  Der „pruefung“-Block ist an den Text gebunden: Satzmenge (Titel, Teaser, Haupttext ohne Quellenzeile) und
    sha256 des inhalt_html müssen passen; „kein_fakt“ gilt nur für Sätze ohne Zahl, Datum und Namen.
P2  Neustarts verworfener Storys höchstens zweimal, nie nach Endprüfung oder Faktencheck; Ergänzen nur ohne
    wartenden Prüf- oder Suchjob; Nachrecherche: primär nur Veranstalter oder vertrauenswürdige Registerquellen,
    passt() prüft das Jahr.
Live  Story 117 (MTS-Diwali, Kurzmeldung) wurde verworfen, weil Entwurf 68 (Story 108, Rückblick) dieselbe
    Primärquelle als uid trägt – eigene Beiträge brauchen eine eigene uid.
"""

import hashlib
import json

import pytest

from news_radar import sources
from news_radar.agent_v2 import import_daten
from news_radar.agents import Kontext, nachrecherche, pruefer
from news_radar.store import Store
from news_radar.workflow import fake as fake_mod
from news_radar.workflow import jobs, orchestrator, repo
from news_radar.workflow.fake import FakeAnthropic

from test_nachrecherche import (HAMM, KOELN, NOW, _hamm_offen, _ohne_modell, ereignisse, google, hamm,  # noqa: F401
                                lauf, settings)

ERFUNDEN = "Der Bürgermeister hat dem Tempel gestern eine Million Euro geschenkt."


def _mit_erfundenem_satz(beitrag: dict) -> dict:
    html = beitrag["inhalt_html"]
    i = html.index("</p>")
    return {**beitrag, "inhalt_html": html[:i] + " " + ERFUNDEN + html[i:]}


def _import(store, settings, ctx, sid, claims, beitrag, block):
    return import_daten(store, settings, {"ergebnisse": [{"story_id": sid, "claims": claims, "beitrag": beitrag,
                                                          "pruefung": block}]}, von="cloud-sitzung", ctx=ctx)


# ---- P1: Bindung an den Text ------------------------------------------------------------------------

def test_pruefung_fuer_einen_anderen_text_wird_abgewiesen(settings):
    with Store(settings.db_path) as store:
        ctx, sid, claims, beitrag = _hamm_offen(settings, store)
        beitrag = _mit_erfundenem_satz(beitrag)
        block = fake_mod.pruefung_block({"inhalt_html": "<p>x</p>"}, claims, pruefer="p2")
        block["saetze"] = [{"nr": 1, "satz": "Ein Satz, der nicht im Text steht.", "urteil": "gedeckt",
                            "claim_ids": [], "fundstelle": "", "kern": False}]
        stats = _import(store, settings, ctx, sid, claims, beitrag, block)
        assert stats["entwuerfe"] == 0 and store.list_drafts() == []
        assert any("sha256" in f or "Sätze" in f for f in stats["fehler"]), stats


def test_pruefung_muss_jeden_satz_abdecken(settings):
    with Store(settings.db_path) as store:
        ctx, sid, claims, beitrag = _hamm_offen(settings, store)
        beitrag = _mit_erfundenem_satz(beitrag)
        block = fake_mod.pruefung_block(beitrag, claims, pruefer="p2")
        block["saetze"] = [s for s in block["saetze"] if "Million" not in s["satz"]]  # Satz ausgelassen
        stats = _import(store, settings, ctx, sid, claims, beitrag, block)
        assert stats["entwuerfe"] == 0 and any("nicht geprüft" in f for f in stats["fehler"]), stats


def test_sha256_muss_zum_text_passen(settings):
    with Store(settings.db_path) as store:
        ctx, sid, claims, beitrag = _hamm_offen(settings, store)
        block = {**fake_mod.pruefung_block(beitrag, claims, pruefer="p2"), "sha256": "0" * 64}
        stats = _import(store, settings, ctx, sid, claims, beitrag, block)
        assert stats["entwuerfe"] == 0 and any("sha256" in f for f in stats["fehler"]), stats


def test_kein_fakt_mit_zahl_datum_oder_name_gilt_als_ungedeckt(settings):
    with Store(settings.db_path) as store:
        ctx, sid, claims, beitrag = _hamm_offen(settings, store)
        beitrag = _mit_erfundenem_satz(beitrag)
        block = fake_mod.pruefung_block(beitrag, claims, pruefer="p2")
        for s in block["saetze"]:
            if "Million" in s["satz"]:
                s["urteil"] = "kein_fakt"
        stats = _import(store, settings, ctx, sid, claims, beitrag, block)
        for d in store.list_drafts():
            assert ERFUNDEN not in d["inhalt_html"]
        assert stats["entwuerfe"] in (0, 1)


def test_kein_fakt_regel():
    assert pruefer.darf_kein_fakt("Das freut viele in der Gemeinde.")
    for satz in ("Rund 3000 Gäste kamen.", "Am Samstag beginnt das Fest.", "Das sagte Kamala Sivakumar.",
                 "Am 14. November feiert die Gemeinde."):
        assert not pruefer.darf_kein_fakt(satz), satz


def test_saetze_des_entwurfs_ohne_quellenzeile_mit_titel_und_teaser():
    felder = {"titel": "Lichterfest in Hamm", "teaser": "Tausende feiern. Der Tempel lädt ein.",
              "inhalt_html": '<p>Am 14. November feiert die Gemeinde. Rund 3000 Gäste kommen.</p>\n'
                             '<h2>Programm</h2><p>Die Feier beginnt um 10 Uhr.</p>\n<p class="quelle">Quelle: WA</p>'}
    assert pruefer.saetze_des_entwurfs(felder) == [
        "Lichterfest in Hamm", "Tausende feiern.", "Der Tempel lädt ein.", "Am 14. November feiert die Gemeinde.",
        "Rund 3000 Gäste kommen.", "Programm", "Die Feier beginnt um 10 Uhr."]


def test_nur_ganze_saetze_werden_gestrichen():
    from news_radar.workflow.models import SatzUrteil

    felder = {"titel": "T", "teaser": "",
              "inhalt_html": "<p>Die Feier beginnt um 10 Uhr mit Musik. Die Feier beginnt um 10 Uhr.</p>"}
    u = SatzUrteil(nr=2, satz="Die Feier beginnt um 10 Uhr.", urteil="ungedeckt", claim_ids=[], fundstelle="",
                   kern=False)
    neu, gestrichen, _ = pruefer.pruefung_anwenden(felder, [u])
    assert "Die Feier beginnt um 10 Uhr mit Musik." in neu["inhalt_html"] and gestrichen


def test_endpruefung_ohne_alle_saetze_heisst_ueberarbeitung(settings):
    def luecke(user, system, req):
        out = fake_mod.pruefer(user, system, req)
        if fake_mod.block(user, "entwurf") is not None:
            out["saetze"] = out["saetze"][1:]
        return out

    client = lauf(settings, [hamm()], client=FakeAnthropic({"pruefer": luecke}), texte={hamm().url: HAMM})
    with Store(settings.db_path) as store:
        story = repo.stories(store)[0]
    assert client.rollen().count("text") == 2 and story["status"] == "verworfen"


# ---- P2 ------------------------------------------------------------------------------------------

def test_hoechstens_zwei_neustarts_einer_verworfenen_story(settings):
    with Store(settings.db_path) as store:
        sid = repo.story_anlegen(store, typ="news", titel="Story")
        for n in range(3):
            repo.story_setzen(store, sid, status="verworfen", notiz="Zweite KI: verworfen – kein Beleg")
            store.db.execute("UPDATE workflow_jobs SET status = 'fertig' WHERE story_id = ?", (sid,))
            store.db.commit()
            orchestrator.neu_starten(store, sid, f"Neue Quelle {n}")
        assert len(ereignisse(store, "neu_gestartet")) == 2


@pytest.mark.parametrize("notiz", ["Zweite KI (Endprüfung): verworfen – nicht gedeckt",
                                   "Faktencheck: Kernaussage auch nach Überarbeitung nicht gedeckt"])
def test_nach_endpruefung_oder_faktencheck_kein_neustart(settings, notiz):
    with Store(settings.db_path) as store:
        sid = repo.story_anlegen(store, typ="news", titel="Story")
        repo.story_setzen(store, sid, status="verworfen", notiz=notiz)
        assert not orchestrator.neu_starten(store, sid, "Neue Quelle")


def test_endpruefung_verwirft_mit_eigener_kennung(settings):
    def immer(user, system, req):
        out = fake_mod.pruefer(user, system, req)
        if fake_mod.block(user, "entwurf") is not None and out["saetze"]:
            out["saetze"][0].update(urteil="widerspruch", kern=True)
        return out

    lauf(settings, [hamm()], client=FakeAnthropic({"pruefer": immer}), texte={hamm().url: HAMM})
    with Store(settings.db_path) as store:
        story = repo.stories(store)[0]
    assert story["notiz"].startswith("Zweite KI (Endprüfung): verworfen")
    assert not nachrecherche.neu_startbar(story)


def test_ergaenzen_nicht_bei_wartender_nachrecherche_oder_pruefung(settings):
    from news_radar import nachtrag

    with Store(settings.db_path) as store:
        sid = repo.story_anlegen(store, typ="news", titel="Story")
        repo.story_setzen(store, sid, status="recherche_erforderlich")
        for schritt in ("pruefung", "nachrecherche", "endpruefung"):
            jid = jobs.einreihen(store, sid, schritt, key=f"{sid}:{schritt}")
            _, grund = nachtrag._ziel_grund(store, sid)
            assert grund, schritt
            store.db.execute("UPDATE workflow_jobs SET status = 'fertig' WHERE id = ?", (jid,))
            store.db.commit()
        jobs.einreihen(store, sid, "recherche", key=f"{sid}:recherche")  # wartet nur auf Export/Worker
        assert nachtrag._ziel_grund(store, sid)[1] == ""


def test_recherche_laeuft_nicht_weiter_wenn_story_inzwischen_verworfen(settings):
    with Store(settings.db_path) as store:
        ctx = orchestrator.kontext(settings, store, client=FakeAnthropic(), fetch_text=lambda u: HAMM,
                                   suche=lambda q: [])
        orchestrator.scan(ctx, [hamm()])
        sid = repo.stories(store)[0]["id"]
        repo.story_setzen(store, sid, status="verworfen", notiz="verworfen von luis")
        orchestrator.abarbeiten(ctx)
        assert repo.story(store, sid)["status"] == "verworfen" and ctx.claude.client.requests == []


def test_nachrecherche_primaer_nur_fuer_veranstalter_oder_vertrauenswuerdige_quellen(settings):
    url = "https://www.lokal.example/preis-2026"
    with Store(settings.db_path) as store:
        ctx = Kontext(settings=settings, store=store, fetch_text=lambda u: KOELN + " 2026",
                      suche=lambda q: [{"titel": "Integrationspreis Köln", "url": url, "publisher": "Lokal"}])
        orchestrator.scan(ctx, [google()])
        story = repo.stories(store)[0]
        erg = nachrecherche.nachrecherchieren(ctx, story, ["Bericht mit Volltext"], [], 1)
        doc = next(d for d in repo.dokumente(store, story["id"]) if d.url == url)
    assert erg.neu and doc.art == "volltext" and not doc.primaer


def test_passt_prueft_das_jahr():
    worte = ["verein", "köln", "integr"]
    assert nachrecherche.passt("Der Verein in Köln bekam den Integrationspreis 2026.", worte, "Köln", jahr=2026)
    assert not nachrecherche.passt("Der Verein in Köln bekam den Integrationspreis 2019.", worte, "Köln", jahr=2026)


def test_import_nur_mit_neuen_quellen_zaehlt_als_runde(settings):
    url = "https://www.tamilverein-koeln.de/a"
    with Store(settings.db_path) as store:
        ctx = _ohne_modell(settings, store, texte={f"{url}{n}": KOELN for n in range(5)})
        orchestrator.scan(ctx, [google()])
        sid = repo.stories(store)[0]["id"]
        for n in range(3):
            stats = import_daten(store, settings, {"ergebnisse": [{"story_id": sid, "neue_quellen": [f"{url}{n}"]}]},
                                 ctx=ctx)
        story = repo.story(store, sid)
    assert story["status"] == "verworfen" and "Nach zwei Runden" in story["notiz"], (story, stats)


# ---- Live: Story 117 (MTS-Diwali) und Entwurf 68 (Story 108) ---------------------------------------------

MTS_URL = "https://muenchentamilsangam.org/event/diwali-2026/"
MTS_TEXT = ("Der München Tamil Sangam lädt am 21. November 2026 zur Diwali-Feier in den Kulturtreff München ein. "
            "Das Programm beginnt um 16 Uhr mit Tänzen der Kinder der Tamilschule. "
            "Karten gibt es beim Sangam, der Eintritt für Kinder ist frei. "
            "Der Sangam feiert Diwali seit 2004 jedes Jahr mit der tamilischen Gemeinde in München.")


def test_eigener_beitrag_mit_derselben_primaerquelle_bekommt_eigene_uid(settings):
    """Live 13.11.: Entwurf 68 (Story 108, Rückblick, veröffentlicht) trägt als uid die Seite des Sangam; die neue
    Kurzmeldung (Story 117, Agent-Modus) mit derselben Primärquelle wurde als Dublette verworfen."""
    from news_radar.agent_v2 import paket_v2

    with Store(settings.db_path) as store:
        alt = store.insert_draft({"uid": MTS_URL, "titel": "Rückblick: Diwali bei den Sangams", "story_id": 108,
                                  "typ": "artikel", "inhalt_html": "<p>x</p>", "kategorie": "community"})
        store.claim_draft(alt, von="luis")
        store.mark_published(alt, 4711, "https://www.tamil.de/rueckblick-diwali/")
        item = sources.NewsItem(title="Tamilische Diwali-Feier des München Tamil Sangam am 21. November",
                                url=MTS_URL, summary="Diwali in München", source="Ruhr Nachrichten",
                                published=NOW, ort="München")
        ctx = _ohne_modell(settings, store, texte={MTS_URL: MTS_TEXT})
        orchestrator.scan(ctx, [item])
        p = paket_v2(store, settings, ctx=ctx)["storys"][0]
        claims = fake_mod.recherche("<dokumente>\n" + json.dumps(p["dokumente"]) + "\n</dokumente>", "", {})["claims"]
        beitrag = fake_mod.text("<story>\n" + json.dumps({"titel": p["titel"]}) + "\n</story>\n<claims>\n"
                                + json.dumps(claims) + "\n</claims>", "", {})
        stats = _import(store, settings, ctx, p["story_id"], claims, beitrag,
                        fake_mod.pruefung_block(beitrag, claims, pruefer="p2"))
        neu = [d for d in store.list_drafts(limit=10) if d["id"] != alt]
        story = repo.story(store, p["story_id"])
        assert story["status"] == "fertig" and len(neu) == 1, (story, stats)
        assert neu[0]["uid"] == f"{MTS_URL}#story-{story['id']}" and neu[0]["quelle_url"] == MTS_URL
        assert store.get_draft(alt)["uid"] == MTS_URL  # bestehende uid unverändert


def test_als_dublette_verworfene_story_ist_neu_startbar(settings):
    with Store(settings.db_path) as store:
        sid = repo.story_anlegen(store, typ="news", titel="MTS Diwali")
        repo.story_setzen(store, sid, status="verworfen", notiz="Entwurf zu dieser Meldung existiert schon")
        assert orchestrator.neu_starten(store, sid, "Regression Story 117")
        assert [j["schritt"] for j in jobs.offen_fuer_story(store, sid)] == ["recherche"]
