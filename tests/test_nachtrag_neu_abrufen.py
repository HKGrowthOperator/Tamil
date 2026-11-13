"""Befunde der Prüfung von a6b13cf (Story ergänzen mit neu_abrufen, JSON-LD, TEXT_MAX) und Kurzfelder auf Kinoseiten.

- Ein erneuter Abruf ersetzt nur das Dokument genau dieser Adresse; leitet sie um (Startseite, andere Quelle der
  Story), wird nichts ersetzt („umgeleitet, nicht ersetzt“). Der alte Text bleibt als Fassung, die Claims der Story
  werden gelöscht (sie bezogen sich auf den alten Text), der Titel wird immer mit ersetzt.
- JSON-LD: nur der Termin, der zur Seite gehört; Events ohne Namen nie; @type mit Nicht-Strings wirft nicht.
- TEXT_MAX: der Termin-Block bleibt ganz, nie mitten in einem Wert abgeschnitten.
"""

import json

from news_radar import nachtrag, net
from news_radar.store import Store
from news_radar.workflow import repo
from news_radar.workflow.models import Claim

from test_nachtrag import (ARTIKEL1, ARTIKEL2, PDF_URL, SEITE1, SEITE2, TERMIN_TEXT, TERMIN_URL, URL1, URL2, abruf_aus,
                           annehmen, html, kontext, pdf_bytes, quelle, settings, termin_html, vorschlag)  # noqa: F401

NEU = ("Am 14. März 2026 hat der Sri-Kamadchi-Ampal-Tempel in Hamm sein neues Gemeindehaus eröffnet. Nach neuen "
       "Angaben kamen rund 2600 Gäste aus Deutschland, Österreich und der Schweiz zur Einweihung in Hamm-Uentrop. "
       "Der Tempelverein hatte drei Jahre lang Spenden für den Bau gesammelt und dankte allen Familien.")


def story_mit(store, settings, quellen, seiten):
    sid = annehmen(store, settings, [vorschlag(quellen=quellen)], seiten=seiten)["ergebnisse"][0]["story_id"]
    repo.story_setzen(store, sid, status="recherche_erforderlich")
    return sid


def neu_abrufen(store, settings, sid, urls, seiten, umleitung=None, abrufe=None):
    return annehmen(store, settings, [vorschlag(story_id=sid, quellen=[quelle(u) for u in urls], neu_abrufen=True)],
                    seiten=seiten, umleitung=umleitung, abrufe=abrufe)["ergebnisse"][0]


def test_umleitung_auf_startseite_ersetzt_nichts(settings):
    with Store(settings.db_path) as store:
        sid = story_mit(store, settings, [quelle(URL1)], {URL1: html(ARTIKEL1)})
        start = "https://www.tagesschau.de/"
        e = neu_abrufen(store, settings, sid, [URL1], {URL1: html(NEU + " " + NEU, "Startseite")},
                        umleitung={URL1: start})
        doc = repo.dokumente(store, sid)[0]
        assert doc.text == ARTIKEL1 and doc.url == URL1, e
        assert {"url": URL1, "grund": "umgeleitet, nicht ersetzt"} in e["quellen_uebersprungen"]
        assert e["ergebnis"] != "ergaenzt"


def test_umleitung_auf_andere_quelle_der_story_ersetzt_keine_von_beiden(settings):
    with Store(settings.db_path) as store:
        sid = story_mit(store, settings, [quelle(URL1), quelle(URL2)], {URL1: html(ARTIKEL1), URL2: html(ARTIKEL2)})
        e = neu_abrufen(store, settings, sid, [URL1], {URL1: html(NEU)}, umleitung={URL1: URL2})
        texte = [d.text for d in repo.dokumente(store, sid)]
        assert texte == [ARTIKEL1, ARTIKEL2], e


def test_neu_abrufen_ersetzt_text_und_titel_hebt_alten_text_auf_und_loescht_claims(settings):
    with Store(settings.db_path) as store:
        sid = story_mit(store, settings, [quelle(URL1)], {URL1: html(ARTIKEL1, "Alter Titel")})
        repo.claims_setzen(store, sid, [Claim(id="C1", aussage="Rund 2000 Gäste kamen.", art="zahl", kern=True,
                                              quellen=["Q1"], fundstelle="Rund 2000 Gäste", sicherheit=0.9,
                                              support="bestaetigt")])
        e = neu_abrufen(store, settings, sid, [URL1], {URL1: html(NEU, "")})
        assert e["ergebnis"] == "ergaenzt" and e["aktualisiert"] == 1, e
        doc = repo.dokumente(store, sid)[0]
        assert doc.text == NEU and doc.titel == ""  # Titel immer mit dem Text, auch durch einen leeren
        assert repo.claims(store, sid) == []
        alt = [v for v in repo.fassungen(store, story_id=sid) if v["rolle"] == "quelle_vorher"]
        assert alt and alt[0]["inhalt"]["text"] == ARTIKEL1 and alt[0]["inhalt"]["titel"] == "Alter Titel"
        assert alt[0]["inhalt"]["doc_key"] == "Q1"


def test_neu_abrufen_pdf_mit_seitenanker(settings):
    url = PDF_URL + "#page=2"
    alt = pdf_bytes([SEITE1, SEITE2])
    neu = pdf_bytes([SEITE1, [z.replace("412", "415") for z in SEITE2]])

    def abruf(dateien):
        def f(adresse, frist=None):
            ohne = adresse.split("#", 1)[0]
            return net.Fetched(url=ohne, status=200, content=dateien[ohne], content_type="application/pdf")
        return f

    with Store(settings.db_path) as store:
        sid = nachtrag.annehmen(store, settings, {"vorschlaege": [vorschlag(quellen=[quelle(url)])]}, von="test",
                                ctx=kontext(store, settings), abruf=abruf({PDF_URL: alt}))["ergebnisse"][0]["story_id"]
        repo.story_setzen(store, sid, status="recherche_erforderlich")
        e = nachtrag.annehmen(store, settings, {"vorschlaege": [vorschlag(story_id=sid, quellen=[quelle(url)],
                                                                         neu_abrufen=True)]},
                              von="test", ctx=kontext(store, settings), abruf=abruf({PDF_URL: neu}))["ergebnisse"][0]
        docs = repo.dokumente(store, sid)
        assert e["ergebnis"] == "ergaenzt" and e["aktualisiert"] == 1, e
        assert len(docs) == 1 and docs[0].url == url and "415" in docs[0].text


def test_neu_abrufen_bei_voller_story_geht_neue_quelle_nicht(settings):
    with Store(settings.db_path) as store:
        sid = story_mit(store, settings, [quelle(URL1)], {URL1: html(ARTIKEL1)})
        for n in range(nachtrag.MAX_DOKUMENTE - 1):
            repo.dokument_hinzufuegen(store, sid, url=f"https://www.example.org/b-{n}", text=ARTIKEL2)
        weitere = "https://www.wdr.de/neu-100.html"
        e = neu_abrufen(store, settings, sid, [URL1, weitere], {URL1: html(NEU), weitere: html(ARTIKEL2)})
        assert e["ergebnis"] == "ergaenzt" and e["aktualisiert"] == 1 and e["quellen_geholt"] == 0, e
        assert {"url": weitere, "grund": nachtrag.GRUND_MAX} in e["quellen_uebersprungen"]
        assert len(repo.dokumente(store, sid)) == nachtrag.MAX_DOKUMENTE


# ---- JSON-LD ------------------------------------------------------------------------------------

def _ld(*objekte) -> str:
    return "".join(f'<script type="application/ld+json">{json.dumps(o)}</script>' for o in objekte)


EV_A = {"@type": "Event", "name": "SCENE - KINO CLAUDIA - ZH (SURIYA) 2nd WEEK", "startDate": "2026-11-14T13:00:00+01:00",
        "location": {"@type": "Place", "name": "Kino Claudia"}}
EV_B = {"@type": "Event", "name": "Ganz anderes Konzert in Bern", "startDate": "2026-12-01T19:00:00+01:00",
        "location": {"@type": "Place", "name": "Festhalle Bern"}}
EV_OHNE = {"@type": "Event", "startDate": "2026-12-24T18:00:00+01:00", "location": {"name": "Irgendwo"}}


def _lesen(roh: str, titel: str = "SCENE - KINO CLAUDIA - ZH (SURIYA) 2nd WEEK") -> str:
    seite = f"<html><head><title>{titel}</title>{roh}</head><body><article><p>{TERMIN_TEXT}</p></article></body></html>"
    f = net.Fetched(url=TERMIN_URL, status=200, content=seite.encode(), content_type="text/html; charset=utf-8")
    return nachtrag.seite_lesen(f, TERMIN_URL)[0]


def test_von_mehreren_events_nur_das_zur_seite_passende():
    text = _lesen(_ld(EV_B, EV_A, EV_OHNE))
    assert "startDate: 2026-11-14" in text and "Festhalle Bern" not in text and "Irgendwo" not in text


def test_mehrere_events_ohne_passenden_namen_keines():
    text = _lesen(_ld(EV_A, EV_B), titel="Programm der Woche")
    assert nachtrag.LD_KOPF not in text


def test_genau_ein_event_auch_ohne_passenden_titel_namenlos_nie():
    assert "startDate: 2026-11-14" in _lesen(_ld(EV_A), titel="Programm der Woche")
    assert nachtrag.LD_KOPF not in _lesen(_ld(EV_OHNE))


def test_typ_mit_nicht_strings_wirft_nicht():
    kaputt = {**EV_A, "@type": [{"x": 1}, ["Event"], 3, "Event"]}
    assert "startDate: 2026-11-14" in _lesen(_ld(kaputt))
    assert nachtrag.LD_KOPF not in _lesen(_ld({**EV_A, "@type": {"a": "Event"}}))


def test_text_nahe_text_max_behaelt_den_ganzen_termin_block():
    lang = ("Wort " * (nachtrag.TEXT_MAX // 5 + 50)).strip()
    seite = f"<html><head><title>{EV_A['name']}</title>{_ld(EV_A)}</head><body><article><p>{lang}</p></article></body></html>"
    f = net.Fetched(url=TERMIN_URL, status=200, content=seite.encode(), content_type="text/html; charset=utf-8")
    text = nachtrag.seite_lesen(f, TERMIN_URL)[0]
    assert len(text) <= nachtrag.TEXT_MAX
    assert text.endswith("location.name: Kino Claudia") and "startDate: 2026-11-14T13:00:00+01:00" in text
