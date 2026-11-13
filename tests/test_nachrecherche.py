"""„Recherche nötig“ ist kein Endzustand mehr (Auftrag Luis, 13.11.2026): scheitert das Gate, sucht der Radar selbst
nach Belegen (Nachrecherche, höchstens zwei Runden), danach entscheidet eine zweite KI („pruefer“) aus frischem Kontext:
schreiben (notfalls als Kurzmeldung nur aus belegten Aussagen) oder verwerfen mit Grund. Jeder fertige Entwurf geht
vorher Satz für Satz durch dieselbe zweite KI. Ohne Modellschlüssel liefert der Agent-Export die Storys in
Nachrecherche mit Fehlstellen und Suchanfragen als eigene Liste."""

import json
from datetime import datetime, timedelta, timezone

import pytest

from news_radar import sources
from news_radar.agent_v2 import import_daten, paket_v2
from news_radar.agents import Kontext, nachrecherche
from news_radar.config import Bildquelle, load_settings
from news_radar.store import Store
from news_radar.workflow import costs, fake as fake_mod, jobs, orchestrator, repo
from news_radar.workflow.fake import FakeAnthropic

NOW = datetime.now(timezone.utc)
KOELN = ("Der tamilische Kulturverein Köln hat am Freitag den Integrationspreis der Stadt Köln erhalten. "
         "Die Auszeichnung ist mit 5000 Euro dotiert und wurde im Rathaus übergeben. "
         "Der Verein betreibt seit 1998 eine Samstagsschule mit rund 200 Kindern. "
         "Die Vorsitzende kündigte an, das Preisgeld in neue Lernmaterialien zu stecken.")
HAMM = ("Die tamilische Gemeinde in Hamm feiert am Samstag, 14. November, ihr Lichterfest im Sri-Kamadchi-Ampal-Tempel. "
        "Erwartet werden rund 3000 Besucherinnen und Besucher aus ganz Deutschland. "
        "Der Tempel in Hamm-Uentrop ist der größte hinduistische Tempel Deutschlands. "
        "Die Feier beginnt um 10 Uhr mit einer Prozession, der Eintritt ist frei. "
        "Veranstalter ist der Tempelverein, der seit 2002 in Hamm aktiv ist.")
VEREIN_URL = "https://www.tamilverein-koeln.de/integrationspreis"
VEREIN = Bildquelle(host="tamilverein-koeln.de", betreiber="Tamilischer Kulturverein Köln", art="verein",
                    nachweis="Foto: Tamilischer Kulturverein Köln")


@pytest.fixture
def settings(tmp_path, monkeypatch):
    for var in ("WP_URL", "WP_USER", "WP_APP_PASSWORD", "NOTIFY_WEBHOOK_URL", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY",
                "GEMINI_API_KEY", "BILD_POOL_DIR", "ANTHROPIC_API_KEY"):
        monkeypatch.setenv(var, "")
    s = load_settings()
    s.data_dir = tmp_path / "data"
    s.web_url = "https://radar.test"
    return s


def google(summary="Preis für Verein", url="https://news.google.com/rss/articles/k1"):
    return sources.NewsItem(title="Tamilischer Verein in Köln gewinnt Integrationspreis - WDR", url=url, summary=summary,
                            source="Google News DACH · WDR", published=NOW - timedelta(hours=1))


def hamm(url="https://www.ruhrnachrichten.de/hamm/lichterfest"):
    return sources.NewsItem(title="Tamilisches Lichterfest im Tempel Hamm", url=url, summary="Tamilen feiern in Hamm",
                            source="Ruhr Nachrichten", published=NOW - timedelta(hours=1))


def lauf(settings, items, client=None, texte=None, suche=None):
    client = client or FakeAnthropic()
    with Store(settings.db_path) as store:
        ctx = orchestrator.kontext(settings, store, client=client, fetch_text=lambda url: (texte or {}).get(url, ""),
                                   suche=suche or (lambda q: []))
        orchestrator.scan(ctx, items)
        for _ in range(6):  # Zeitraffer: wie die Abnahme
            orchestrator.abarbeiten(ctx)
            store.db.execute("UPDATE workflow_jobs SET naechster_versuch = '2000-01-01' WHERE status = 'offen'")
            store.db.commit()
    return client


def ereignisse(store, name):
    return [json.loads(r[0]) for r in store.db.execute("SELECT data FROM log WHERE event = ? ORDER BY id", (name,))]


# ---- Modell-Weg -----------------------------------------------------------------------------------

def test_gate_scheitert_nachrecherche_findet_offizielle_seite_und_es_wird_ein_entwurf(settings):
    """Nur ein Google-News-Hinweis: das Gate scheitert; die Nachrecherche findet die Seite des Vereins, die im Hinweis
    genannt ist, Recherche und Gate laufen erneut, die zweite KI prüft den Entwurf."""
    item = google(summary=f"Preis für Verein – mehr unter {VEREIN_URL}")
    settings.bildquellen = settings.bildquellen + [VEREIN]  # Veranstalter: seine Seite ist allein ein Beleg
    client = lauf(settings, [item], texte={VEREIN_URL: KOELN})
    with Store(settings.db_path) as store:
        story = repo.stories(store)[0]
        drafts = store.list_drafts()
        docs = repo.dokumente(store, story["id"])
        nr = ereignisse(store, "nachrecherche")
        schritte = [j["schritt"] for j in jobs.liste(store)]
    assert story["status"] == "fertig" and len(drafts) == 1
    neu = [d for d in docs if d.url == VEREIN_URL]
    assert neu and neu[0].art == "volltext" and neu[0].primaer and neu[0].quelle.startswith("Nachrecherche")
    assert client.rollen().count("recherche") == 2 and "pruefer" in client.rollen()
    assert schritte.count("nachrecherche") == 1 and "endpruefung" in schritte
    assert nr and nr[0]["runde"] == 1 and nr[0]["neu"] == 1 and nr[0]["fehlend"] and nr[0]["anfragen"]
    assert any(h.startswith("Geprüft von zweiter KI") for h in drafts[0]["hinweise"])


def test_nachrecherche_findet_nichts_zweite_ki_verwirft_mit_grund(settings):
    client = lauf(settings, [google()])
    with Store(settings.db_path) as store:
        story = repo.stories(store)[0]
        assert store.list_drafts() == []
        nr = ereignisse(store, "nachrecherche")
    assert story["status"] == "verworfen" and "Zweite KI" in story["notiz"]
    assert client.rollen().count("pruefer") == 1 and "text" not in client.rollen()
    assert nr[0]["neu"] == 0


def test_hoechstens_zwei_runden_nachrecherche(settings):
    """Findet die Nachrecherche immer etwas, das die Kernaussage trotzdem nicht trägt: nach zwei Runden entscheidet die
    zweite KI – kein Kreisel, keine endlosen Kosten."""
    zaehler = iter(range(100))

    def suche(q):
        n = next(zaehler)
        return [{"titel": f"Integrationspreis Köln Verein {n}", "url": f"https://www.lokal.example/preis-{n}",
                 "publisher": f"Lokal {n}"}]

    leer = lambda u, s, r: {"claims": [], "widersprueche": [], "fehlende_angaben": ["Datum der Verleihung"]}
    client = lauf(settings, [google()], client=FakeAnthropic({"recherche": leer}), suche=suche,
                  texte={f"https://www.lokal.example/preis-{n}": KOELN for n in range(100)})
    with Store(settings.db_path) as store:
        story = repo.stories(store)[0]
        n_nach = sum(1 for j in jobs.liste(store) if j["schritt"] == "nachrecherche")
    assert n_nach == 2 and client.rollen().count("recherche") == 3
    assert story["status"] == "verworfen" and client.rollen().count("pruefer") == 1


def test_zweite_ki_schreibt_kurzmeldung_nur_aus_belegten_aussagen(settings):
    """Eine Kernaussage steht nur in einem Google-Hinweis: Nachrecherche ohne Ergebnis, die zweite KI hält die Story
    mit den bestätigten Aussagen für schreibbar → Kurzmeldung; die unbelegte Aussage kommt nicht in den Text."""
    def recherche(user, system, req):
        out = fake_mod.recherche(user, system, req)
        hinweis = next(d for d in fake_mod.block(user, "dokumente") if d["art"] == "hinweis")
        out["claims"].append({"id": "C99", "aussage": "Der Oberbürgermeister eröffnet das Lichterfest persönlich.",
                              "art": "wer", "kern": True, "quellen": [hinweis["doc_key"]],
                              "fundstelle": hinweis["titel"][:160], "sicherheit": 0.5, "support": "offen"})
        return out

    treffer = [{"titel": "Oberbürgermeister besucht Lichterfest in Hamm", "url": "https://news.google.com/rss/articles/ob",
                "publisher": "WA"}]
    item = hamm()
    client = lauf(settings, [item], client=FakeAnthropic({"recherche": recherche}), texte={item.url: HAMM},
                  suche=lambda q: treffer)
    with Store(settings.db_path) as store:
        story = repo.stories(store)[0]
        draft = store.list_drafts()[0]
        claims = {c.id: c for c in repo.claims(store, story["id"])}
    assert story["status"] == "fertig" and story["laenge"] == "kurz"
    assert not claims["C99"].kern and claims["C99"].support != "bestaetigt"
    assert all(c.support == "bestaetigt" for c in claims.values() if c.kern)
    assert "Oberbürgermeister" not in draft["inhalt_html"]
    assert any("Kurzmeldung" in h for h in draft["hinweise"])
    assert client.rollen().count("pruefer") == 2  # Story-Prüfung und Prüfung des Entwurfs


def test_zweite_ki_streicht_ungedeckten_satz_im_entwurf(settings):
    gestrichen = {}

    def pruefer(user, system, req):
        out = fake_mod.pruefer(user, system, req)
        if fake_mod.block(user, "entwurf") is not None:
            satz = next(s for s in reversed(out["saetze"]) if s["urteil"] == "gedeckt")
            satz.update(urteil="ungedeckt", kern=False, claim_ids=[], fundstelle="")
            gestrichen["satz"] = satz["satz"]
        return out

    item = hamm()
    lauf(settings, [item], client=FakeAnthropic({"pruefer": pruefer}), texte={item.url: HAMM})
    with Store(settings.db_path) as store:
        draft = store.list_drafts()[0]
        rollen = [v["rolle"] for v in repo.fassungen(store, story_id=draft["story_id"])]
    assert gestrichen["satz"] not in draft["inhalt_html"]
    assert any(h.startswith("Zweite KI hat gestrichen") for h in draft["hinweise"])
    assert any(h.startswith("Geprüft von zweiter KI") for h in draft["hinweise"])
    assert "pruefung" in rollen


def test_zweite_ki_findet_ungedeckte_kernaussage_einmal_ueberarbeitet_dann_verworfen(settings):
    def pruefer(user, system, req):
        out = fake_mod.pruefer(user, system, req)
        if fake_mod.block(user, "entwurf") is not None and out["saetze"]:
            out["saetze"][0].update(urteil="widerspruch", kern=True)
        return out

    item = hamm()
    client = lauf(settings, [item], client=FakeAnthropic({"pruefer": pruefer}), texte={item.url: HAMM})
    with Store(settings.db_path) as store:
        story = repo.stories(store)[0]
        assert store.list_drafts() == []
    assert client.rollen().count("text") == 2 and story["status"] == "verworfen" and "Zweite KI" in story["notiz"]


def test_pruefer_hat_eigenes_modell_aus_der_env(settings, monkeypatch):
    monkeypatch.setenv("RADAR_MODELL_PRUEFER", "claude-test-pruefer")
    s = load_settings()
    assert s.modell_fuer("pruefer") == "claude-test-pruefer"
    monkeypatch.delenv("RADAR_MODELL_PRUEFER")
    assert load_settings().modell_fuer("pruefer") == "claude-opus-5-5"


def test_nachrecherche_kosten_und_budget(settings):
    """Die Nachrecherche selbst kostet nichts (Zeile in agent_usage ohne Modell); jeder weitere Modellaufruf läuft über
    die Budget-Reservierung – ist das Budget erschöpft, wartet der Job."""
    lauf(settings, [google()])
    with Store(settings.db_path) as store:
        zeilen = [dict(r) for r in store.db.execute("SELECT rolle, provider, kosten_usd FROM agent_usage")]
    assert {"rolle": "nachrecherche", "provider": "suche", "kosten_usd": 0} in zeilen
    assert any(z["rolle"] == "pruefer" and z["provider"] == "anthropic" for z in zeilen)


# ---- Suchwege ---------------------------------------------------------------------------------------

def test_suchanfragen_aus_titel_ort_personen_und_fehlstellen():
    story = {"titel": "Tamilischer Verein in Köln gewinnt Integrationspreis - WDR", "ort": "Köln", "typ": "news"}
    fehl = nachrecherche.fehlstellen(["Termin ohne bestätigten Ort", "Kernaussage C2 nur aus einer Quelle belegt: X"],
                                     ["Name der Vorsitzenden"])
    assert "Ort" in fehl and "Name der Vorsitzenden" in fehl
    anfragen = nachrecherche.suchanfragen(story, ["Vorsitzende Kamala Sivakumar sprach im Rathaus"], fehl)
    assert 1 <= len(anfragen) <= nachrecherche.MAX_ANFRAGEN
    assert any("Köln" in a for a in anfragen) and any("Kamala Sivakumar" in a for a in anfragen)
    assert all("WDR" not in a for a in anfragen)


def test_soziale_netzwerke_und_paywall_werden_nie_belege(settings):
    abrufe = []

    def text(url):
        abrufe.append(url)
        return "Abo abschließen: jetzt weiterlesen mit Plus. " + KOELN if "zeitung" in url else KOELN

    item = google(summary="Preis – https://www.facebook.com/tamilverein/posts/1 und https://www.instagram.com/p/x "
                          "und https://www.zeitung.example/preis")
    with Store(settings.db_path) as store:
        ctx = Kontext(settings=settings, store=store, fetch_text=text, suche=lambda q: [])
        orchestrator.scan(ctx, [item])
        story = repo.stories(store)[0]
        erg = nachrecherche.nachrecherchieren(ctx, story, ["Bericht mit Volltext"], [], 1)
        docs = repo.dokumente(store, story["id"])
    assert not any("facebook" in u or "instagram" in u for u in abrufe)
    assert erg.neu == [] and not any("zeitung" in d.url for d in docs)


def test_register_quellen_aus_bereits_gesehenen_meldungen(settings):
    """Weg „register“: eine Meldung einer registrierten Quelle, die der Radar schon gesehen (aber nicht genommen)
    hat, wird gelesen und angehängt."""
    with Store(settings.db_path) as store:
        store.mark("uid-wa", "Integrationspreis für tamilischen Verein in Köln", "https://www.wa.de/koeln/preis",
                   "WA Hamm", "irrelevant")
        ctx = Kontext(settings=settings, store=store, fetch_text=lambda u: KOELN if "wa.de" in u else "",
                      suche=lambda q: [])
        orchestrator.scan(ctx, [google()])
        story = repo.stories(store)[0]
        erg = nachrecherche.nachrecherchieren(ctx, story, ["Bericht mit Volltext"], [], 1)
        docs = repo.dokumente(store, story["id"])
    # WA ist keine vertrauenswürdige Registerquelle: Beleg ja, allein aber nicht primär (zweiter Verlag nötig)
    assert erg.wege.get("register") == 1 and any(d.url == "https://www.wa.de/koeln/preis" and d.art == "volltext"
                                                  and not d.primaer for d in docs)


# ---- Ohne Modellschlüssel (Agent-Modus) ------------------------------------------------------------

def _ohne_modell(settings, store, texte=None):
    return Kontext(settings=settings, store=store, budget=costs.Budget(store, 1.0, 10.0),
                   fetch_text=lambda u: (texte or {}).get(u, ""), suche=lambda q: [])


def test_ohne_modell_import_scheitert_am_gate_nachrecherche_und_eigene_liste_im_export(settings):
    item = google(summary=f"Preis für Verein – {VEREIN_URL}")
    with Store(settings.db_path) as store:
        ctx = _ohne_modell(settings, store, texte={VEREIN_URL: KOELN})
        orchestrator.scan(ctx, [item])
        sid = repo.stories(store)[0]["id"]
        mappe = paket_v2(store, settings, ctx=ctx)
        assert [p["story_id"] for p in mappe["storys"]] == [sid] and mappe["nachrecherche"] == []
        p = mappe["storys"][0]
        beitrag = fake_mod.text("<story>\n" + json.dumps({"titel": p["titel"]}) + "\n</story>\n<claims>\n[]\n</claims>",
                                "", {})
        stats = import_daten(store, settings, {"ergebnisse": [{"story_id": sid, "claims": [], "beitrag": beitrag,
                                                               "fehlend": ["Bericht des Vereins"],
                                                               "pruefung": fake_mod.pruefung_block(beitrag, [])}]},
                             ctx=ctx)
        assert stats["nachrecherche"] == 1 and repo.story(store, sid)["status"] == "recherche_erforderlich"
        orchestrator.abarbeiten(ctx)  # ohne Modell: nur die Nachrecherche (sucht, kein Aufruf)
        mappe = paket_v2(store, settings, ctx=ctx)
        assert mappe["storys"] == []
        n = mappe["nachrecherche"][0]
        assert n["story_id"] == sid and n["runde"] == 1 and "Bericht des Vereins" in n["fehlend"]
        assert n["suchanfragen"] and any(d["url"] == VEREIN_URL for d in n["dokumente"])
        assert store.db.execute("SELECT COUNT(*) FROM agent_usage WHERE provider = 'anthropic'").fetchone()[0] == 0


def test_ohne_modell_import_nur_mit_beitrag_verwerfen_oder_neuen_quellen(settings):
    with Store(settings.db_path) as store:
        ctx = _ohne_modell(settings, store, texte={VEREIN_URL: KOELN})
        orchestrator.scan(ctx, [google()])
        sid = repo.stories(store)[0]["id"]
        stats = import_daten(store, settings, {"ergebnisse": [{"story_id": sid, "claims": [], "fehlend": ["Ort"]}]},
                             ctx=ctx)
        assert stats["fehler"] and "Beitrag, Verwerfen oder neue Quellen" in stats["fehler"][0]
        assert repo.story(store, sid)["status"] == "neu"
        stats = import_daten(store, settings, {"ergebnisse": [{"story_id": sid, "neue_quellen": [
            VEREIN_URL, "https://www.facebook.com/verein"]}]}, ctx=ctx)
        assert stats["quellen"] == 1 and any("soziales Netzwerk" in f for f in stats["fehler"])
        docs = repo.dokumente(store, sid)
        assert any(d.url == VEREIN_URL and d.art == "volltext" and d.primaer for d in docs)
        assert [p["story_id"] for p in paket_v2(store, settings, ctx=ctx)["storys"]] == [sid]  # bleibt offen


def test_ohne_modell_letzte_runde_kurzmeldung_oder_verworfen(settings):
    """Nach zwei Runden entscheidet der Import endgültig: ohne bestätigte Kernaussage verworfen mit Grund."""
    with Store(settings.db_path) as store:
        ctx = _ohne_modell(settings, store)
        orchestrator.scan(ctx, [google()])
        sid = repo.stories(store)[0]["id"]
        beitrag = fake_mod.text("<story>\n{}\n</story>\n<claims>\n[]\n</claims>", "", {})
        for _ in range(3):
            import_daten(store, settings, {"ergebnisse": [{"story_id": sid, "claims": [], "beitrag": beitrag,
                                                           "pruefung": fake_mod.pruefung_block(beitrag, [])}]},
                         ctx=ctx)
            orchestrator.abarbeiten(ctx)
        story = repo.story(store, sid)
        n_nach = sum(1 for j in jobs.liste(store) if j["schritt"] == "nachrecherche")
    assert n_nach == 2 and story["status"] == "verworfen" and "Nach zwei Runden" in story["notiz"]


def test_alte_storys_recherche_noetig_werden_angestossen(settings):
    """Bestand aus der Zeit vor der Nachrecherche (Status ohne Job): der Worker nimmt sie auf."""
    with Store(settings.db_path) as store:
        sid = repo.story_anlegen(store, typ="news", titel="Tamilischer Verein in Köln gewinnt Integrationspreis")
        repo.dokument_hinzufuegen(store, sid, url="https://news.google.com/rss/articles/alt", art="hinweis",
                                  titel="Integrationspreis", text=f"mehr: {VEREIN_URL}")
        repo.story_setzen(store, sid, status="recherche_erforderlich", notiz="Keine Kernaussage (was/wer/wann/wo) belegt")
        ctx = _ohne_modell(settings, store, texte={VEREIN_URL: KOELN})
        orchestrator.abarbeiten(ctx)
        schritte = [(j["schritt"], j["status"]) for j in jobs.liste(store)]
    assert ("nachrecherche", "fertig") in schritte and ("recherche", "offen") in schritte


# ---- Cockpit ---------------------------------------------------------------------------------------

def test_cockpit_reiter_in_nachrecherche_ohne_aufforderung_zur_quelle(settings):
    from news_radar.web import create_app

    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim", "s3cret"
    with Store(settings.db_path) as store:
        repo.nutzer_anlegen(store, "priya", "priya-passwort-1", "redaktion")
        ctx = _ohne_modell(settings, store)
        orchestrator.scan(ctx, [google()])
        sid = repo.stories(store)[0]["id"]
        repo.story_setzen(store, sid, status="recherche_erforderlich", notiz="Keine Kernaussage (was/wer/wann/wo) belegt")
        orchestrator.abarbeiten(ctx)
    app = create_app(settings, testing=True)

    def login(user, pw):
        c = app.test_client()
        c.get("/login")
        with c.session_transaction() as s:
            token = s["csrf"]
        assert c.post("/login", data={"user": user, "password": pw, "_csrf": token}).status_code == 302
        return c, token

    red, token = login("priya", "priya-passwort-1")
    html = red.get("/recherche").get_data(as_text=True)
    assert "In Nachrecherche" in html and "Gebt eine Quelle dazu" not in html
    assert "Runde 1" in html and "Gesucht" in html and f"/story/{sid}/quelle" not in html
    assert red.post(f"/story/{sid}/quelle", data={"url": VEREIN_URL, "_csrf": token}).status_code == 403
    admin, _ = login("luis", "geheim")
    html = admin.get("/recherche").get_data(as_text=True)
    assert f"/story/{sid}/quelle" in html and "<details" in html
    assert "In Nachrecherche" in admin.get("/").get_data(as_text=True)


# ---- Agent-Modus: Prüfung durch eine andere Instanz ist Pflicht (Entscheidung Luis, 13.11.2026) ---------------

def _hamm_offen(settings, store):
    ctx = _ohne_modell(settings, store, texte={"https://www.ruhrnachrichten.de/hamm/lichterfest": HAMM})
    orchestrator.scan(ctx, [hamm()])
    p = paket_v2(store, settings, ctx=ctx)["storys"][0]
    claims = fake_mod.recherche("<dokumente>\n" + json.dumps(p["dokumente"]) + "\n</dokumente>", "", {})["claims"]
    beitrag = fake_mod.text("<story>\n" + json.dumps({"titel": p["titel"]}) + "\n</story>\n<claims>\n"
                            + json.dumps(claims) + "\n</claims>", "", {})
    return ctx, p["story_id"], claims, beitrag


@pytest.mark.parametrize("aenderung, fehler", [
    (None, "ohne „pruefung“"),
    ({"pruefer": "cloud-sitzung"}, "andere Instanz"),
    ({"pruefer": ""}, "andere Instanz"),
    ({"urteil": "nicht_importieren"}, "nicht importieren"),
    ({"befunde": [{"schwere": "P2", "beschreibung": "Datum fehlt im Beleg", "satz": "x"}]}, "offene Befunde"),
    ({"zeitpunkt": "gestern"}, "zeitpunkt"),
    ({"zeitpunkt": "2099-01-01T00:00:00+00:00"}, "zeitpunkt"),
    ({"saetze": []}, "saetze"),
])
def test_import_ohne_gueltige_pruefung_wird_abgewiesen(settings, aenderung, fehler):
    with Store(settings.db_path) as store:
        ctx, sid, claims, beitrag = _hamm_offen(settings, store)
        eintrag = {"story_id": sid, "claims": claims, "beitrag": beitrag}
        if aenderung is not None:
            eintrag["pruefung"] = {**fake_mod.pruefung_block(beitrag, claims), **aenderung}
        stats = import_daten(store, settings, {"ergebnisse": [eintrag]}, von="cloud-sitzung", ctx=ctx)
        assert stats["entwuerfe"] == 0 and store.list_drafts() == []
        assert stats["fehler"] and fehler in stats["fehler"][0], stats["fehler"]
        assert repo.story(store, sid)["status"] == "neu" and jobs.offen_fuer_story(store, sid)  # nichts geändert


def test_import_mit_pruefung_einer_anderen_instanz_legt_entwurf_an(settings):
    with Store(settings.db_path) as store:
        ctx, sid, claims, beitrag = _hamm_offen(settings, store)
        block = {**fake_mod.pruefung_block(beitrag, claims, pruefer="pruefer-agent-2"),
                 "befunde": [{"schwere": "P3", "beschreibung": "Komma im Teaser", "satz": ""},
                             {"schwere": "P1", "beschreibung": "Zahl war falsch", "satz": "", "behoben": True}]}
        stats = import_daten(store, settings, {"ergebnisse": [{"story_id": sid, "claims": claims, "beitrag": beitrag,
                                                               "pruefung": block}]}, von="cloud-sitzung", ctx=ctx)
        draft = store.list_drafts()[0]
        fassung = [v for v in repo.fassungen(store, story_id=sid) if v["rolle"] == "pruefung"]
    assert stats["entwuerfe"] == 1, stats
    assert any(h.startswith("Geprüft von zweiter KI (pruefer-agent-2") for h in draft["hinweise"])
    assert any("Komma im Teaser" in h for h in draft["hinweise"])
    assert fassung and fassung[0]["inhalt"]["pruefung"]["pruefer"] == "pruefer-agent-2"


def test_verwerfen_braucht_keine_pruefung(settings):
    with Store(settings.db_path) as store:
        ctx, sid, _, _ = _hamm_offen(settings, store)
        stats = import_daten(store, settings, {"ergebnisse": [{"story_id": sid, "verwerfen": "Dublette"}]}, ctx=ctx)
        assert stats["verworfen"] == 1 and repo.story(store, sid)["status"] == "verworfen"


def test_neustart_einer_verworfenen_story_wird_protokolliert(settings):
    with Store(settings.db_path) as store:
        sid = repo.story_anlegen(store, typ="news", titel="Story")
        repo.story_setzen(store, sid, status="verworfen", notiz="Zweite KI: verworfen – kein Beleg")
        assert orchestrator.neu_starten(store, sid, "Neue Quelle: WDR")
        neu = ereignisse(store, "neu_gestartet")
    assert neu and neu[0]["story"] == sid and neu[0]["vorher"] == "verworfen" and "WDR" in neu[0]["grund"]
