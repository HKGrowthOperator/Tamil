"""Verzeichnis, Radar-Seite (Festlegung F2, Vertrag B1.4, Abnahmetest T4): Einsendungen bei WordPress abholen
(Cursor), nach festen Regeln prüfen (Pflichtfelder, Form, Dubletten gegen die Einträge), Kategorie nur mit Modell
vorschlagen, Prüfung ablegen, im Cockpit freigeben (neu, alt neben neu Feld für Feld, entfernen) oder ablehnen.

Kein Netz: `FakeWordPressVerzeichnis` steht für tamil-radar/v1/verzeichnis/*, FakeAnthropic für das Modell. Alle
Angaben sind erfunden (example.test)."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from news_radar import schalter, verzeichnis
from news_radar.abnahme.wp_eingang import Antwort
from news_radar.abnahme.wp_verzeichnis import FakeWordPressVerzeichnis
from news_radar.config import load_settings
from news_radar.store import Store
from news_radar.wordpress import TamilRadarClient
from news_radar.workflow import costs, repo, schema
from news_radar.workflow.fake import FakeAnthropic
from news_radar.workflow.providers import Claude

FIX = Path(__file__).parent / "fixtures"
EINSENDER = ("Erika Beispiel", "erika@example.test")
VEREIN = {"name": "Tamilischer Kulturverein Essen", "art": "verein", "beschreibung": "Tanz, Musik und Sprachkurse.",
          "plz": "45127", "stadt": "Essen", "land": "DE", "bundesland_kanton": "Nordrhein-Westfalen",
          "telefon": "+49 201 1234567", "website": "https://verein.example.test"}


@pytest.fixture
def settings(tmp_path, monkeypatch):
    for var in ("WP_URL", "WP_USER", "WP_APP_PASSWORD", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "GEMINI_API_KEY",
                "BILD_POOL_DIR", "NOTIFY_WEBHOOK_URL", "ANTHROPIC_API_KEY"):
        monkeypatch.setenv(var, "")
    s = load_settings()
    s.data_dir = tmp_path
    return s


@pytest.fixture
def store(settings):
    with Store(settings.db_path) as st:
        yield st


@pytest.fixture
def wp():
    return FakeWordPressVerzeichnis()


def client(wp):
    return TamilRadarClient("https://www.tamil.test", "ki-agent", "app-pw", session=wp)


def claude(settings, store, fake=None):
    return Claude(settings, store, client=fake or FakeAnthropic(), budget=costs.Budget(store, 5.0, 150.0))


def lauf(store, wp, ki=None):
    return verzeichnis.lauf(store, client(wp), ki)


def posts(wp, praefix="eintrag"):
    return [(r, k) for m, r, k in wp.koerper if r.startswith(praefix)]


def ohne_personendaten(store) -> bool:
    zeilen = [str(dict(r)) for r in store.db.execute("SELECT * FROM editorial_actions")]
    zeilen += [str(r) for r in store.iter_log()]
    return not any(p in z for z in zeilen for p in EINSENDER)


# ---- Migration und Client -------------------------------------------------------------------------------------------

def test_migration_legt_verzeichnis_einsendungen_an(store):
    assert 13 in schema.MIGRATIONS and schema.LATEST >= 13
    spalten = {r[1] for r in store.db.execute("PRAGMA table_info(verzeichnis_einsendungen)")}
    assert {"wp_id", "vorgangsnummer", "typ", "eintrag_id", "status", "wp_status", "einsender_name", "einsender_email",
            "berechtigung", "felder", "regeln", "pruefung", "alt", "alt_stand", "entscheidung", "eingang_at"} <= spalten


def test_client_liest_den_rest_vertrag_aus_der_fixture():
    roh = json.loads((FIX / "wp_verzeichnis_einsendungen.json").read_text(encoding="utf-8"))

    class Session:
        auth, headers, aufrufe = None, {}, []

        def request(self, method, url, **kw):
            self.aufrufe.append((method, url, kw.get("params")))
            return Antwort(200, roh)

    s = Session()
    daten = TamilRadarClient("https://www.tamil.test", "u", "p", session=s).vz_einsendungen(nach=4, anzahl=50)
    assert [e["vorgangsnummer"] for e in daten["einsendungen"]] == ["V261114-K7M3Q"] and daten["naechster"] == 5
    assert s.aufrufe == [("GET", "https://www.tamil.test/wp-json/tamil-radar/v1/verzeichnis/einsendungen",
                          {"nach": 4, "anzahl": 50})]


def test_client_503_heisst_nichts_abzuholen_und_nur_gueltige_vorgaenge(wp):
    c = client(wp)
    wp.funktion_an = False
    assert c.vz_einsendungen(nach=0) is None and c.vz_eintraege(nach=0) is None
    with pytest.raises(ValueError):
        c.vz_einsendung("../status")
    with pytest.raises(ValueError):
        c.vz_einsendung("T261113-K7M3Q")  # Vorgangsnummer des Eingangs (F1), nicht des Verzeichnisses


# ---- Abholen --------------------------------------------------------------------------------------------------------

def test_schalter_verzeichnis_haelt_alles_an_ohne_aufruf(store, wp):
    wp.einreichen("neu", VEREIN)
    schalter.setzen(store, "verzeichnis", True, wer="anna", grund="Rechtstexte fehlen")
    out = lauf(store, wp)
    assert out["angehalten"] >= 1 and wp.aufrufe == []
    assert wp.einsendungen[0]["status"] == "neu"  # bleibt auf der Website liegen
    schalter.setzen(store, "verzeichnis", False, wer="anna")
    out = lauf(store, wp)
    assert out["neu"] == 1 and out["geprueft"] == 1 and wp.einsendungen[0]["status"] == "geprueft"


def test_abholen_mit_cursor_idempotent_ohne_abgeschlossene(store, wp):
    for i in range(5):
        wp.einreichen("neu", {**VEREIN, "name": f"Verein Nummer {i}", "plz": f"4512{i}"})
    wp.einsendungen[4]["status"] = "abgelehnt"  # auf der Website schon entschieden: nicht einlesen
    out = verzeichnis.abholen(store, client(wp), anzahl=2)
    assert out["neu"] == 4 and out["seiten"] >= 3
    assert verzeichnis.abholen(store, client(wp))["neu"] == 0  # Cursor: nichts doppelt
    assert len(verzeichnis.liste(store, "alle")) == 4
    zeilen = repo.aktionen_liste(store, kanal="verzeichnis")
    assert zeilen and all(z["regel_fassung"] for z in zeilen) and ohne_personendaten(store)


# ---- Prüfen ohne Modell ---------------------------------------------------------------------------------------------

def test_pruefung_ohne_modell_legt_ergebnis_bei_wordpress_ab(store, wp):
    v = wp.einreichen("neu", VEREIN)
    out = lauf(store, wp)
    assert out["geprueft"] == 1 and out.get("modell", 0) == 0
    e = verzeichnis.holen(store, v)
    assert e["status"] == "geprueft" and e["wp_status"] == "geprueft"
    p = wp.einsendung(v)["pruefung"]
    assert p["fehlt"] == [] and p["formfehler"] == [] and p["dubletten"] == [] and p["kategorie_vorschlag"] == ""
    assert "ohne Modell" in " ".join(p["hinweise"])  # Kategorie-Vorschlag entfällt
    assert not any(x in json.dumps(p, ensure_ascii=False) for x in EINSENDER)
    aktionen = repo.aktionen_liste(store, aktion="verzeichnis_geprueft")
    assert len(aktionen) == 1 and aktionen[0]["ausloeser"] == "agent" and aktionen[0]["kanal"] == "verzeichnis"
    assert ohne_personendaten(store)


def test_vorschlag_ohne_stadt_wird_nicht_ergaenzt_sondern_unvollstaendig(store, wp):
    v = wp.einreichen("neu", {k: w for k, w in VEREIN.items() if k != "stadt"})
    lauf(store, wp)
    e = verzeichnis.holen(store, v)
    assert "stadt" in e["pruefung"]["fehlt"]
    assert any("unvollständig" in h and "Stadt" in h for h in e["pruefung"]["hinweise"])
    werte = verzeichnis.vorschlag(e)
    assert werte["stadt"] == verzeichnis.FEHLT  # „fehlt“, nie geraten
    assert werte["oeffnungszeiten"] == ""  # optional und nicht angegeben: leer, nichts erfunden


def test_formfehler_plz_telefon_website_und_kontaktweg(store, wp):
    v = wp.einreichen("neu", {"name": "Tempel Wien", "art": "tempel", "plz": "10115", "stadt": "Wien", "land": "AT",
                              "telefon": "bitte anrufen", "website": "tempel.example.test"})
    lauf(store, wp)
    p = verzeichnis.holen(store, v)["pruefung"]
    assert {"plz", "telefon", "website"} <= set(p["formfehler"])
    v2 = wp.einreichen("neu", {"name": "Ohne Kontakt", "art": "verein", "plz": "45127", "stadt": "Essen", "land": "DE"})
    lauf(store, wp)
    assert "kontakt" in verzeichnis.holen(store, v2)["pruefung"]["fehlt"]


def test_dublette_gegen_vorhandenen_eintrag_mit_verweis(store, wp):
    eid = wp.eintrag_anlegen({**VEREIN, "name": "Tamilischer Kulturverein Essen e. V."})
    wp.eintrag_anlegen({**VEREIN, "name": "Ganz anderer Laden", "telefon": "+49 30 999999"})
    v = wp.einreichen("neu", VEREIN)
    lauf(store, wp)
    p = verzeichnis.holen(store, v)["pruefung"]
    assert [d["eintrag_id"] for d in p["dubletten"]] == [eid]
    assert "plz" in p["dubletten"][0]["grund"] and "name" in p["dubletten"][0]["grund"]
    assert any(h.startswith("mögliche Dublette") and str(eid) in h for h in p["hinweise"])
    # gleiche Telefonnummer, aber unähnlicher Name: keine Dublette
    v2 = wp.einreichen("neu", {**VEREIN, "name": "Sportgruppe Nord", "plz": "45139"})
    lauf(store, wp)
    assert verzeichnis.holen(store, v2)["pruefung"]["dubletten"] == []


def test_dublette_derselbe_vorschlag_zweimal_vor_der_freigabe(store, wp):
    v1 = wp.einreichen("neu", VEREIN)
    v2 = wp.einreichen("neu", {**VEREIN, "name": "Tamilischer Kulturverein Essen e.V."})
    lauf(store, wp)
    assert verzeichnis.holen(store, v1)["pruefung"]["dubletten"] == []
    dub = verzeichnis.holen(store, v2)["pruefung"]["dubletten"]
    assert dub and dub[0].get("einsendung") == v1


def test_regeln_der_website_werden_mitverwendet(store, wp):
    v = wp.einreichen("neu", VEREIN)
    wp.regeln_extra[v] = {"dubletten": [{"eintrag_id": 4711, "grund": "name+website"}]}
    lauf(store, wp)
    assert 4711 in [d["eintrag_id"] for d in verzeichnis.holen(store, v)["pruefung"]["dubletten"]]


# ---- Kategorie nur mit Modell ---------------------------------------------------------------------------------------

def test_kategorie_vorschlag_mit_modell_gemessen_und_ohne_einsenderdaten(settings, store, wp):
    fake = FakeAnthropic()
    v = wp.einreichen("neu", VEREIN, anmerkung="Bitte Erika Beispiel unter 0170 1234567 anrufen")
    lauf(store, wp, claude(settings, store, fake))
    assert fake.rollen() == ["verzeichnis"]
    anfrage = fake.requests[0]["user"] + fake.requests[0]["system"]
    assert not any(x in anfrage for x in (*EINSENDER, "0170 1234567", "+49 201 1234567"))
    assert verzeichnis.holen(store, v)["pruefung"]["kategorie_vorschlag"] == "verein-kultur"
    usage = store.db.execute("SELECT rolle, status FROM agent_usage").fetchall()
    assert [tuple(u) for u in usage] == [("verzeichnis", "ok")]


def test_kategorie_ausserhalb_der_liste_wird_verworfen(settings, store, wp):
    fake = FakeAnthropic({"verzeichnis": {"kategorie": "business-reise"}})  # passt nicht zur Art „verein“
    v = wp.einreichen("neu", VEREIN)
    lauf(store, wp, claude(settings, store, fake))
    p = verzeichnis.holen(store, v)["pruefung"]
    assert p["kategorie_vorschlag"] == "" and any("verworfen" in h for h in p["hinweise"])


def test_modellaufruf_prueft_schalter_verzeichnis(settings, store, wp):
    fake = FakeAnthropic()
    wp.einreichen("neu", VEREIN)
    verzeichnis.abholen(store, client(wp))
    schalter.setzen(store, "verzeichnis", True, wer="anna", grund="Pause")
    out = verzeichnis.pruefen(store, client(wp), claude(settings, store, fake))
    assert out["angehalten"] == 1 and fake.requests == []


# ---- Freigeben, ablehnen ---------------------------------------------------------------------------------------------

def test_t4_neu_freigeben_schreibt_nur_eingesandte_werte(settings, store, wp):
    v = wp.einreichen("neu", {**VEREIN, "email": "info@verein.example.test"}, nicht_oeffentlich=("email",))
    lauf(store, wp, claude(settings, store))
    e = verzeichnis.holen(store, v)
    ergebnis = verzeichnis.freigeben(store, client(wp), v, von="priya", kategorie=e["pruefung"]["kategorie_vorschlag"])
    (route, koerper), = posts(wp)
    assert route == "eintrag" and koerper["einsendung"] == v
    assert koerper["felder"]["kategorie"] == "verein-kultur" and koerper["felder"]["stadt"] == "Essen"
    assert "email" not in koerper["felder"] and "premium" not in koerper["felder"]  # nicht öffentlich: nicht senden
    eid = ergebnis["eintrag"]["id"]
    assert wp.eintraege[eid]["status"] == "veroeffentlicht" and wp.eintraege[eid]["premium"] is False
    e = verzeichnis.holen(store, v)
    assert (e["status"], e["wp_status"], e["eintrag_id"]) == ("freigegeben", "freigegeben", eid)
    a = repo.aktionen_liste(store, aktion="verzeichnis_freigegeben")
    assert a[0]["wer"] == "priya" and a[0]["ausloeser"] == "person" and ohne_personendaten(store)
    with pytest.raises(verzeichnis.Konflikt):  # nur einmal
        verzeichnis.freigeben(store, client(wp), v, von="priya")


def test_redaktion_aendert_einen_wert_vor_der_freigabe(store, wp):
    v = wp.einreichen("neu", VEREIN)
    lauf(store, wp)
    verzeichnis.freigeben(store, client(wp), v, von="priya", werte={"name": "Tamilischer Kulturverein Essen e. V."})
    assert posts(wp)[0][1]["felder"]["name"] == "Tamilischer Kulturverein Essen e. V."
    v2 = wp.einreichen("neu", {**VEREIN, "name": "Zweiter Verein", "plz": "45139"})
    lauf(store, wp)
    with pytest.raises(ValueError, match="Nicht in der Einsendung"):  # nichts ergänzen, keine Öffnungszeiten raten
        verzeichnis.freigeben(store, client(wp), v2, von="priya", werte={"oeffnungszeiten": "Mo–Fr 9–17 Uhr"})
    assert len(posts(wp)) == 1


def test_premium_laesst_sich_nie_setzen(store, wp):
    v = wp.einreichen("neu", VEREIN)
    lauf(store, wp)
    for werte in ({"premium": "1"}, {"Premium": "ja"}):
        with pytest.raises(ValueError, match="Premium"):
            verzeichnis.freigeben(store, client(wp), v, von="priya", werte=werte)
    with pytest.raises(ValueError, match="Premium"):
        verzeichnis.freigeben(store, client(wp), v, von="priya", annehmen=["premium"])
    assert posts(wp) == [] and verzeichnis.holen(store, v)["status"] == "geprueft"


def test_t4_telefon_aendern_alt_neben_neu_feldweise(store, wp):
    eid = wp.eintrag_anlegen({**VEREIN, "email": "alt@verein.example.test"})
    v = wp.einreichen("aenderung", {"telefon": "+49 201 7654321", "email": "neu@verein.example.test"}, eintrag_id=eid)
    lauf(store, wp)
    e = verzeichnis.holen(store, v)
    assert e["alt"]["telefon"] == "+49 201 1234567" and e["alt_stand"] == wp.stand(eid)
    zeilen = {z["feld"]: z for z in verzeichnis.vergleich(e)}
    assert (zeilen["telefon"]["alt"], zeilen["telefon"]["neu"]) == ("+49 201 1234567", "+49 201 7654321")
    assert zeilen["telefon"]["geaendert"] and zeilen["email"]["geaendert"]
    assert {u["feld"] for u in e["pruefung"]["unterschied"]} == {"telefon", "email"}
    verzeichnis.freigeben(store, client(wp), v, von="priya", annehmen=["telefon"])  # E-Mail nicht angenommen
    (route, koerper), = posts(wp)
    assert route == f"eintrag/{eid}" and koerper["felder"] == {"telefon": "+49 201 7654321"}
    assert koerper["stand"] == e["alt_stand"]
    assert wp.eintraege[eid]["felder"]["telefon"] == "+49 201 7654321"
    assert wp.eintraege[eid]["felder"]["email"] == "alt@verein.example.test"


def test_t4_ablehnen_aendert_nichts_am_eintrag(store, wp):
    eid = wp.eintrag_anlegen(VEREIN)
    vorher = dict(wp.eintraege[eid]["felder"])
    v = wp.einreichen("aenderung", {"telefon": "+49 201 7654321"}, eintrag_id=eid)
    lauf(store, wp)
    verzeichnis.ablehnen(store, client(wp), v, von="priya")
    assert wp.eintraege[eid]["felder"] == vorher and posts(wp) == []
    assert wp.einsendung(v)["status"] == "abgelehnt" and verzeichnis.holen(store, v)["status"] == "abgelehnt"
    with pytest.raises(verzeichnis.Konflikt):
        verzeichnis.freigeben(store, client(wp), v, von="priya", annehmen=["telefon"])


def test_veralteter_stand_409_wird_sauber_gemeldet_und_neu_geladen(store, wp):
    eid = wp.eintrag_anlegen(VEREIN)
    v = wp.einreichen("aenderung", {"telefon": "+49 201 7654321"}, eintrag_id=eid)
    lauf(store, wp)
    wp.eintraege[eid]["felder"]["website"] = "https://neu.example.test"  # jemand ändert in wp-admin
    with pytest.raises(verzeichnis.StandVeraltet):
        verzeichnis.freigeben(store, client(wp), v, von="priya", annehmen=["telefon"])
    e = verzeichnis.holen(store, v)
    assert e["status"] == "geprueft" and e["alt"]["website"] == "https://neu.example.test"
    assert e["alt_stand"] == wp.stand(eid)  # neu gelesen: der nächste Versuch gilt dem aktuellen Stand
    verzeichnis.freigeben(store, client(wp), v, von="priya", annehmen=["telefon"])
    assert wp.eintraege[eid]["felder"]["telefon"] == "+49 201 7654321"


def test_nicht_oeffentlich_bei_aenderung_heisst_leer(store, wp):
    eid = wp.eintrag_anlegen(VEREIN)
    v = wp.einreichen("aenderung", {"website": "https://verein.example.test"}, eintrag_id=eid,
                      nicht_oeffentlich=("website",))
    lauf(store, wp)
    assert {z["feld"]: z["neu"] for z in verzeichnis.vergleich(verzeichnis.holen(store, v))}["website"] == ""
    verzeichnis.freigeben(store, client(wp), v, von="priya", annehmen=["website"])
    assert posts(wp)[0][1]["felder"] == {"website": ""} and wp.eintraege[eid]["felder"]["website"] == ""


def test_entfernen_mit_bestaetigung_macht_den_eintrag_zum_entwurf(store, wp):
    eid = wp.eintrag_anlegen(VEREIN)
    v = wp.einreichen("entfernen", {}, eintrag_id=eid)
    lauf(store, wp)
    verzeichnis.freigeben(store, client(wp), v, von="priya")
    (route, koerper), = posts(wp)
    assert route == f"eintrag/{eid}/entfernen" and set(koerper) == {"einsendung", "stand"}
    assert wp.eintraege[eid]["status"] == "entfernt"


def test_freigabe_im_stopp_ruft_nicht_auf(store, wp):
    v = wp.einreichen("neu", VEREIN)
    lauf(store, wp)
    schalter.setzen(store, "verzeichnis", True, wer="anna", grund="Pause")
    with pytest.raises(schalter.Gestoppt):
        verzeichnis.freigeben(store, client(wp), v, von="priya")
    assert posts(wp) == [] and verzeichnis.holen(store, v)["status"] == "geprueft"


def test_unklarer_ausgang_wird_abgeglichen_nicht_wiederholt(store, wp):
    v = wp.einreichen("neu", VEREIN)
    lauf(store, wp)
    wp.abbruch_nach_senden.add(v)
    verzeichnis.freigeben(store, client(wp), v, von="priya")
    assert len(posts(wp)) == 1  # ein POST, danach nur Lesen
    assert verzeichnis.holen(store, v)["status"] == "freigegeben" and len(wp.eintraege) == 1


def test_abweisung_der_website_wird_verstaendlich_gemeldet(store, wp):
    v = wp.einreichen("neu", VEREIN)
    lauf(store, wp)
    with pytest.raises(verzeichnis.Abgewiesen) as info:
        verzeichnis.freigeben(store, client(wp), v, von="priya", werte={"plz": "123"})
    assert "plz" in str(info.value) and verzeichnis.holen(store, v)["status"] == "geprueft"


# ---- Löschfrist und Dienst -------------------------------------------------------------------------------------------

def test_loeschfrist_90_tage_nach_eingang(store, wp):
    alt, neu = wp.einreichen("neu", VEREIN), wp.einreichen("neu", {**VEREIN, "name": "Zweiter Verein"})
    lauf(store, wp)
    jetzt = datetime.now(timezone.utc)
    store._write("UPDATE verzeichnis_einsendungen SET eingang_at = ? WHERE vorgangsnummer = ?",
                 ((jetzt - timedelta(days=91)).isoformat(timespec="seconds"), alt))
    out = verzeichnis.loeschen(store, jetzt=jetzt)
    assert out["geloescht"] == 1 and verzeichnis.holen(store, alt) is None and verzeichnis.holen(store, neu)
    assert repo.aktionen_liste(store, aktion="verzeichnis_geloescht") and ohne_personendaten(store)


def test_dienst_plan_nur_mit_funktionsschalter(settings):
    from news_radar import dienst

    settings.wp_url, settings.wp_user, settings.wp_app_password = "https://www.tamil.test", "ki-agent", "pw"
    assert "verzeichnis" not in [e.name for e in dienst.plan(settings, env={})]  # Standard aus
    plan = {e.name: e for e in dienst.plan(settings, env={"RADAR_VERZEICHNIS": "an"})}
    assert plan["verzeichnis"].args == ("verzeichnis", "lauf") and plan["verzeichnis"].kanaele == ("verzeichnis",)
    assert plan["verzeichnis-frist"].args == ("verzeichnis", "loeschen") and plan["verzeichnis-frist"].kanaele == ()
