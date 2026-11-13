"""Gegenprüfung (13.11.2026): drei neue Umgehungen des Prüfblocks und Nacharbeiten.

A  „gedeckt“ ist keine Selbstauskunft: nur mit claim_ids bestätigter Claims, und Zahlen, Daten und Namen des Satzes
   stehen in Aussage oder Fundstelle dieser Claims – sonst ungedeckt.
B  „kein_fakt“ gilt im Agent-Import nie; im Worker nur ohne großgeschriebenes Wort außer am Satzanfang.
C  Die Quellenzeile baut der Radar aus den Dokumenten der Story neu; Text darin wird nie übernommen.
Dazu: uid-Suffix „:story-<id>“ und URL-sichere uid im Client, Abkürzungen beim Satzteilen, Neustart-Zähler auch für
„fehler“, Kostendeckel je Story, Hinweis auf die gleiche Primärquelle.
"""

import hashlib

import pytest

from news_radar.agent_v2 import import_daten
from news_radar.agents import pruefer
from news_radar.store import Store
from news_radar.workflow import fake as fake_mod
from news_radar.workflow import jobs, orchestrator, repo
from news_radar.workflow.fake import FakeAnthropic
from news_radar.workflow.models import Claim, SatzUrteil
from news_radar.workflow.providers import usage_protokollieren

from test_nachrecherche import HAMM, _hamm_offen, ereignisse, hamm, lauf, settings  # noqa: F401


def _lauf(settings, zusatz, urteil_fuer=None, quelle_zeile=""):
    """Wie die Nachstellung der Prüferin: Satzurteile von Hand, alle „gedeckt“ ohne claim_ids."""
    with Store(settings.db_path) as store:
        ctx, sid, claims, beitrag = _hamm_offen(settings, store)
        beitrag = dict(beitrag)
        html = beitrag["inhalt_html"]
        i = html.index("</p>")
        html = html[:i] + (" " + zusatz if zusatz else "") + html[i:] + quelle_zeile
        beitrag["inhalt_html"] = html
        block = fake_mod.pruefung_block(beitrag, claims, pruefer="p2")
        block["sha256"] = hashlib.sha256(html.encode()).hexdigest()
        echte = {s["satz"]: s for s in block["saetze"]}
        block["saetze"] = [
            {**echte.get(s, {}), "nr": n, "satz": s, "urteil": urteil_fuer, "claim_ids": [], "fundstelle": "",
             "kern": False} if zusatz and s == zusatz else {**echte[s], "nr": n}
            for n, s in enumerate(pruefer.saetze_des_entwurfs(beitrag), 1)]
        stats = import_daten(store, settings, {"ergebnisse": [{"story_id": sid, "claims": claims, "beitrag": beitrag,
                                                               "pruefung": block}]}, von="cloud-sitzung", ctx=ctx)
        d = store.list_drafts()
        return stats, (d[0]["inhalt_html"] if d else "")


def test_a_gedeckt_ohne_claim_ids_gilt_nicht(settings):
    _, html = _lauf(settings, "Der Tempelverein hat 9000 Euro Spenden gesammelt.", "gedeckt")
    assert "9000 Euro" not in html


def test_b_kein_fakt_im_agent_import_nie(settings):
    _, html = _lauf(settings, "Die Feier wurde wegen Sturm nach Dortmund verlegt.", "kein_fakt")
    assert "Dortmund" not in html


def test_c_quellenzeile_baut_der_radar(settings):
    _, html = _lauf(settings, "", None,
                    '<p class="quelle">Quelle: Ruhr Nachrichten. Der Bürgermeister sagte die Feier ab.</p>')
    assert "sagte die Feier ab" not in html and '<p class="quelle">Quelle: Ruhr Nachrichten</p>' in html


def test_gedeckt_braucht_zahlen_und_namen_im_beleg():
    c = Claim(id="C1", aussage="Rund 3000 Gäste kamen zum Lichterfest in Hamm.", art="zahl", kern=True,
              quellen=["Q1"], fundstelle="Rund 3000 Gäste", sicherheit=0.9, support="bestaetigt")
    gut = SatzUrteil(nr=1, satz="Rund 3000 Gäste kamen zum Lichterfest in Hamm.", urteil="gedeckt",
                     claim_ids=["C1"], fundstelle="", kern=True)
    falsch = SatzUrteil(nr=2, satz="Rund 4000 Gäste kamen zum Lichterfest in Hamm.", urteil="gedeckt",
                        claim_ids=["C1"], fundstelle="", kern=True)
    fremd = SatzUrteil(nr=3, satz="Rund 3000 Gäste kamen zum Lichterfest in Bern.", urteil="gedeckt",
                       claim_ids=["C1"], fundstelle="", kern=True)
    unbekannt = SatzUrteil(nr=4, satz="Rund 3000 Gäste kamen zum Lichterfest in Hamm.", urteil="gedeckt",
                           claim_ids=["C9"], fundstelle="", kern=True)
    urteile = pruefer.belegt([gut, falsch, fremd, unbekannt], [c])
    assert [u.urteil for u in urteile] == ["gedeckt", "ungedeckt", "ungedeckt", "ungedeckt"]


def test_kein_fakt_im_worker_nur_ohne_grossgeschriebenes_wort():
    assert pruefer.darf_kein_fakt("Das freut viele in der Gemeinde.") is False  # „Gemeinde“ mitten im Satz
    assert pruefer.darf_kein_fakt("Das freut viele, die dabei waren.")
    assert pruefer.darf_kein_fakt("Wer mag, kann Sie dort treffen.")  # Anrede steht in der Stoppliste
    assert not pruefer.darf_kein_fakt("Die Feier wurde nach Dortmund verlegt.")


def test_abkuerzungen_trennen_keinen_satz():
    felder = {"titel": "", "teaser": "",
              "inhalt_html": "<p>Es kommen u. a. Gäste aus Bern. Dr. Kumar spricht. Treffpunkt ist St. Gallen, "
                             "z. B. am Bahnhof. Es gibt ca. 200 Plätze bzw. Stehplätze, Nr. 5 ist frei.</p>"}
    assert pruefer.saetze_des_entwurfs(felder) == [
        "Es kommen u. a. Gäste aus Bern.", "Dr. Kumar spricht.", "Treffpunkt ist St. Gallen, z. B. am Bahnhof.",
        "Es gibt ca. 200 Plätze bzw. Stehplätze, Nr. 5 ist frei."]


# ---- uid-Suffix und Client ---------------------------------------------------------------------------

def test_uid_suffix_ohne_raute_und_urlsicher_im_client_bei_409_und_kino(settings):
    from news_radar import publisher
    from news_radar.wordpress import TamilRadarClient

    class Resp:
        def __init__(self, code, data):
            self.status_code, self._data, self.text = code, data, ""

        def json(self):
            return self._data

    class Session:
        def __init__(self):
            self.aufrufe, self.headers, self.auth = [], {}, None

        def request(self, method, url, timeout=None, json=None, **kw):
            self.aufrufe.append((method, url))
            if method == "POST":
                return Resp(409, {"data": {"status": 409, "id": 77, "link": "https://www.tamil.de/k/"}})
            return Resp(200, {"id": 77, "link": "https://www.tamil.de/k/", "status": "publish"})

    uid = "https://cinestar.de/film/jailer-2/:story-12"
    with Store(settings.db_path) as store:
        did = store.insert_draft({"uid": uid, "typ": "kino_termine", "titel": "Jailer 2", "teaser": "t",
                                  "inhalt_html": "<p>x</p>", "kategorie": "kino", "story_id": 12,
                                  "fakten": {"film": "Jailer 2", "kinos": []}})
        session = Session()
        publisher.publish_via_plugin(store.get_draft(did), settings,
                                     TamilRadarClient("https://www.tamil.de", "u", "p", session=session), store,
                                     "publish")
    put = [u for m, u in session.aufrufe if m == "PUT"]
    assert put and put[0].endswith("/beitrag/https%3A%2F%2Fcinestar.de%2Ffilm%2Fjailer-2%2F%3Astory-12")


# ---- Neustarts, Kostendeckel, Hinweis ------------------------------------------------------------------

def test_neustart_zaehler_gilt_auch_fuer_fehler(settings):
    with Store(settings.db_path) as store:
        sid = repo.story_anlegen(store, typ="news", titel="Story")
        ergebnis = []
        for n in range(3):
            repo.story_setzen(store, sid, status="fehler", notiz="recherche: Timeout")
            store.db.execute("UPDATE workflow_jobs SET status = 'fertig' WHERE story_id = ?", (sid,))
            store.db.commit()
            ergebnis.append(orchestrator.neu_starten(store, sid, f"Neue Quelle {n}"))
    assert ergebnis == [True, True, False]


def test_kostendeckel_je_story_verwirft_vor_dem_naechsten_bezahlten_schritt(settings):
    settings.kosten_story_usd = 1.0
    with Store(settings.db_path) as store:
        client = FakeAnthropic()
        ctx = orchestrator.kontext(settings, store, client=client, fetch_text=lambda u: HAMM, suche=lambda q: [])
        orchestrator.scan(ctx, [hamm()])
        sid = repo.stories(store)[0]["id"]
        usage_protokollieren(store, rolle="vorher", provider="anthropic", modell="x", usd=1.2, story_id=sid)
        orchestrator.abarbeiten(ctx)
        story = repo.story(store, sid)
    assert client.requests == [] and story["status"] == "verworfen" and "Kostendeckel" in story["notiz"]


def test_zweiter_entwurf_mit_gleicher_primaerquelle_traegt_hinweis(settings):
    from test_pruefung_befunde import test_eigener_beitrag_mit_derselben_primaerquelle_bekommt_eigene_uid as fall

    fall(settings)
    with Store(settings.db_path) as store:
        neu = [d for d in store.list_drafts(limit=10) if d["story_id"] != 108][0]
        alt = [d for d in store.list_drafts(limit=10) if d["story_id"] == 108][0]
    assert neu["uid"].endswith(f":story-{neu['story_id']}") and "#" not in neu["uid"]
    assert any(f"Gleiche Primärquelle wie Entwurf {alt['id']}" in h for h in neu["hinweise"])
