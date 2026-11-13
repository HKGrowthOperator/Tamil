"""Eingang (Festlegung F1, integrationen.md §3 „Einsendungen“): Abholen bei WordPress über den austauschbaren
Transport, Vorbereitung (Regeln, ohne Schlüssel nur Regeln; mit Modell über `Claude.call`, Rolle `eingang`), Entscheidung
der Redaktion, Status zurück an WordPress, Protokoll, Löschfrist. Kein Netz: `FakeWordPressEingang` und FakeAnthropic.
Alle Personendaten sind erfunden (example.test)."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from news_radar import eingang, schalter
from news_radar.abnahme.wp_eingang import Antwort, FakeWordPressEingang
from news_radar.config import load_settings
from news_radar.store import Store
from news_radar.wordpress import TamilRadarClient
from news_radar.workflow import costs, repo, schema
from news_radar.workflow.fake import FakeAnthropic
from news_radar.workflow.providers import Claude

FIX = Path(__file__).parent / "fixtures"
JETZT = datetime(2026, 11, 13, 20, 0, tzinfo=timezone.utc)
PERSON = ("Erika Beispiel", "erika@example.test", "+49 30 1234567")
EVENT = {"titel": "Pongal-Fest Testverein", "beginn": "2027-01-16T18:30:00+01:00", "ende": "2027-01-16T22:00:00+01:00",
         "ort": "Gemeindesaal, Beispielstraße 1", "stadt": "Essen", "land": "DE", "veranstalter": "Testverein e. V.",
         "beschreibung": "Tanz, Musik und Essen. Alle Familien sind willkommen.", "eintritt": "10 Euro, Kinder frei",
         "ticket_link": "https://tickets.example.test/pongal"}


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
    return FakeWordPressEingang()


def client(wp):
    return TamilRadarClient("https://www.tamil.test", "ki-agent", "app-pw", session=wp)


def claude(settings, store, fake=None):
    return Claude(settings, store, client=fake or FakeAnthropic(), budget=costs.Budget(store, 5.0, 150.0))


def abholen_und_vorbereiten(store, wp, ki=None):
    eingang.abholen(store, client(wp))
    return eingang.vorbereiten(store, ki, jetzt=JETZT)


# ---- Migration und Client ----------------------------------------------------------------------------------------

def test_migration_11_legt_einsendungen_an(store):
    assert schema.LATEST >= 11 and 11 in schema.MIGRATIONS
    assert store.db.execute("PRAGMA user_version").fetchone()[0] == schema.LATEST
    spalten = {r[1] for r in store.db.execute("PRAGMA table_info(einsendungen)")}
    assert {"wp_id", "vorgangsnummer", "art", "status", "wp_status", "name", "email", "telefon", "einwilligung",
            "einwilligung_fassung", "felder", "bild", "zusammenfassung", "hinweise", "dublette_von", "entwurf",
            "entwurf_id", "notiz", "eingang_at", "abgeschlossen_at"} <= spalten


def test_client_liest_den_rest_vertrag_aus_der_fixture():
    roh = json.loads((FIX / "wp_einsendungen_liste.json").read_text(encoding="utf-8"))

    class Session:
        auth, headers, aufrufe = None, {}, []

        def request(self, method, url, **kw):
            self.aufrufe.append((method, url, kw.get("params")))
            return Antwort(200, roh)

    s = Session()
    daten = TamilRadarClient("https://www.tamil.test", "u", "p", session=s).einsendungen(nach=40, anzahl=50)
    assert [e["vorgangsnummer"] for e in daten["einsendungen"]] == ["T261113-K7M3Q", "T261113-P2W9D"]
    assert s.aufrufe == [("GET", "https://www.tamil.test/wp-json/tamil-radar/v1/einsendungen", {"nach": 40, "anzahl": 50})]


def test_client_503_heisst_nichts_abzuholen_und_409_ist_ein_konflikt(wp):
    c = client(wp)
    vorgang = wp.einreichen("kontakt", {"nachricht": "Hallo Redaktion"})
    assert c.einsendung_status(vorgang, "spam")["status"] == "spam"
    assert c.einsendung_status(vorgang, "erledigt") == {"konflikt": True, "aktuell": "spam"}
    wp.funktion_an = False
    assert c.einsendungen(nach=0) is None
    with pytest.raises(ValueError):
        c.einsendung("../status")  # nur gültige Vorgangsnummern in den Pfad


# ---- Abholen -----------------------------------------------------------------------------------------------------

def test_schalter_eingang_haelt_abholen_an_ohne_aufruf_und_ohne_verlust(store, wp):
    wp.einreichen("event", EVENT)
    schalter.setzen(store, "eingang", True, wer="anna", grund="Rechtstexte fehlen")
    out = eingang.abholen(store, client(wp))
    assert out["angehalten"] == 1 and wp.aufrufe == []
    assert wp.zeilen[0]["status"] == "eingegangen"  # bleibt auf der Website liegen
    schalter.setzen(store, "eingang", False, wer="anna")
    assert eingang.abholen(store, client(wp))["neu"] == 1
    assert wp.zeilen[0]["status"] == "abgeholt"


def test_abholen_mit_cursor_seitenweise_und_ohne_namen_im_protokoll(store, wp):
    for i in range(5):
        wp.einreichen("kontakt", {"nachricht": f"Nachricht Nummer {i}"})
    out = eingang.abholen(store, client(wp), anzahl=2)
    assert out["neu"] == 5 and out["seiten"] == 3
    assert {z["status"] for z in wp.zeilen} == {"abgeholt"}
    assert eingang.abholen(store, client(wp))["neu"] == 0  # Cursor gemerkt, nichts doppelt
    assert store.db.execute("SELECT COUNT(*) FROM einsendungen").fetchone()[0] == 5
    zeilen = repo.aktionen_liste(store, kanal="eingang")
    assert zeilen and {z["ausloeser"] for z in zeilen} == {"dienst"}
    text = json.dumps(zeilen, ensure_ascii=False) + json.dumps(list(store.iter_log()), ensure_ascii=False)
    assert not any(p in text for p in PERSON)


def test_abgeschlossene_auf_der_website_werden_nicht_eingelesen(store, wp):
    v = wp.einreichen("kontakt", {"nachricht": "Schon erledigt"})
    wp.zeile(v)["status"] = "erledigt"
    assert eingang.abholen(store, client(wp))["neu"] == 0


# ---- Vorbereiten ohne Modell (Regeln) ----------------------------------------------------------------------------

def test_regeln_ohne_schluessel_markieren_und_entwerfen_nur_aus_angaben(store, wp):
    wp.einreichen("event", EVENT)
    out = abholen_und_vorbereiten(store, wp)
    assert out["vorbereitet"] == 1 and out["modell"] == 0
    e = eingang.liste(store)[0]
    assert e["status"] == "vorbereitet" and e["hinweise"] == []
    assert "Pongal-Fest Testverein" in e["zusammenfassung"] and "Essen" in e["zusammenfassung"]
    assert e["entwurf"]["titel"] == "Pongal-Fest Testverein" and e["entwurf"]["quelle"] == "regeln"
    assert e["entwurf"]["absaetze"] == [EVENT["beschreibung"]]
    zeile = repo.aktionen_liste(store, aktion="eingang_vorbereitet")[0]
    assert (zeile["ausloeser"], zeile["kanal"], zeile["gegenstand_typ"]) == ("agent", "eingang", "einsendung")
    assert zeile["gegenstand_id"] == e["vorgangsnummer"] and zeile["regel_fassung"]


def test_regeln_vergangenheit_ausserhalb_dach_und_unvollstaendig(store, wp):
    wp.einreichen("event", {**EVENT, "beginn": "2026-10-01T18:00:00+02:00", "land": "LK", "veranstalter": ""})
    wp.einreichen("beitrag", {"thema": "", "text": "Ein Hinweis", "link": ""})
    abholen_und_vorbereiten(store, wp)
    event, beitrag = sorted(eingang.liste(store), key=lambda e: e["wp_id"])
    assert "Datum in der Vergangenheit" in event["hinweise"]
    assert any(h.startswith("Ort außerhalb DACH") for h in event["hinweise"])
    assert any(h.startswith("unvollständig") and "Veranstalter" in h for h in event["hinweise"])
    assert any(h.startswith("unvollständig") and "Thema" in h for h in beitrag["hinweise"])


def test_derselbe_termin_zweimal_gibt_moegliche_dublette(store, wp):
    wp.einreichen("event", EVENT)
    wp.einreichen("event", {**EVENT, "titel": "Pongal Fest – Testverein"}, email="max@example.test")
    abholen_und_vorbereiten(store, wp)
    erste, zweite = sorted(eingang.liste(store), key=lambda e: e["wp_id"])
    assert not any("Dublette" in h for h in erste["hinweise"])
    assert any(h.startswith("mögliche Dublette") for h in zweite["hinweise"])
    assert zweite["dublette_von"] == f"einsendung:{erste['vorgangsnummer']}"


def test_dublette_gegen_story_und_termin_entwurf(store, wp):
    sid = repo.story_anlegen(store, typ="event", titel="Pongal-Fest Testverein", ort="Essen",
                             schluessel="event:2027-01-16:essen:pongal")
    wp.einreichen("event", EVENT)
    abholen_und_vorbereiten(store, wp)
    assert eingang.liste(store)[0]["dublette_von"] == f"story:{sid}"
    store.insert_draft(dict(uid="t1", typ="event", titel="Thaipusam in Hamm", event_datum="2027-02-01",
                            ort="Hamm", event_ort="Tempel Hamm", inhalt_html="<p>x</p>"))
    wp.einreichen("event", {**EVENT, "titel": "Thaipusam Hamm", "beginn": "2027-02-01T10:00:00+01:00",
                            "stadt": "Hamm", "ort": "Tempel Hamm"})
    abholen_und_vorbereiten(store, wp)
    neu = max(eingang.liste(store), key=lambda e: e["wp_id"])
    assert neu["dublette_von"].startswith("entwurf:")


# ---- Vorbereiten mit Modell --------------------------------------------------------------------------------------

def test_modell_rolle_eingang_ohne_kontaktdaten_und_gemessen(settings, store, wp):
    fake = FakeAnthropic()
    wp.einreichen("event", EVENT)
    out = abholen_und_vorbereiten(store, wp, claude(settings, store, fake))
    assert out["modell"] == 1 and fake.rollen() == ["eingang"]
    anfrage = fake.requests[0]["user"] + fake.requests[0]["system"]
    assert not any(p in anfrage for p in PERSON)
    assert "Pongal-Fest Testverein" in anfrage
    usage = store.db.execute("SELECT rolle, status FROM agent_usage").fetchall()
    assert [tuple(u) for u in usage] == [("eingang", "ok")]
    e = eingang.liste(store)[0]
    assert e["entwurf"]["quelle"] == "modell" and e["entwurf"]["titel"]


def test_modell_mit_erfundener_angabe_wird_verworfen(settings, store, wp):
    def erfindet(user, system, req):
        return {"zusammenfassung": "Pongal-Fest in Essen", "titel": "Pongal-Fest Testverein",
                "teaser": "Rund 500 Gäste werden erwartet.", "absaetze": ["Mehr unter https://erfunden.example/x"]}

    wp.einreichen("event", EVENT)
    abholen_und_vorbereiten(store, wp, claude(settings, store, FakeAnthropic({"eingang": erfindet})))
    e = eingang.liste(store)[0]
    assert e["entwurf"]["quelle"] == "regeln"
    assert any("Modell-Entwurf verworfen" in h for h in e["hinweise"])
    assert "500" not in json.dumps(e["entwurf"]) and "erfunden" not in json.dumps(e["entwurf"])


def test_modell_aufruf_prueft_schalter_eingang(settings, store, wp):
    fake = FakeAnthropic()
    wp.einreichen("event", EVENT)
    eingang.abholen(store, client(wp))
    schalter.setzen(store, "eingang", True, wer="anna", grund="Pause")
    out = eingang.vorbereiten(store, claude(settings, store, fake), jetzt=JETZT)
    assert out["angehalten"] == 1 and fake.requests == []
    assert eingang.liste(store)[0]["status"] == "abgeholt"


# ---- Entscheiden -------------------------------------------------------------------------------------------------

def test_uebernehmen_legt_entwurf_mit_vermerk_an_und_meldet_wordpress(settings, store, wp):
    from news_radar.publisher import plugin_payload

    v = wp.einreichen("event", EVENT)
    abholen_und_vorbereiten(store, wp)
    did = eingang.uebernehmen(store, settings, v, von="priya", client=client(wp),
                              felder={"titel": "Pongal-Fest in Essen", "teaser": "Tanz, Musik und Essen."})
    d = store.get_draft(did)
    assert d["status"] == "neu" and d["typ"] == "event" and d["herkunft"] == "einsendung"
    assert eingang.VERMERK in d["hinweise"] and d["titel"] == "Pongal-Fest in Essen"
    assert d["event_datum"].startswith("2027-01-16") and "Essen" in d["event_ort"]
    assert d["ticket_url"] == EVENT["ticket_link"]
    assert not any(p in json.dumps(d, ensure_ascii=False) for p in PERSON)
    assert wp.zeile(v)["status"] == "uebernommen"
    e = eingang.holen(store, v)
    assert e["status"] == "uebernommen" and e["entwurf_id"] == did and e["abgeschlossen_at"]
    meta = plugin_payload(d, settings, "publish")["meta"]
    assert meta["event_veranstalter"] == "Testverein e. V." and meta["event_preis"] == "10 Euro, Kinder frei"
    assert meta["event_ende"].startswith("2027-01-16T22:00") and meta["event_land"] == "DE"
    zeile = repo.aktionen_liste(store, aktion="eingang_uebernommen")[0]
    assert (zeile["wer"], zeile["ausloeser"], zeile["draft_id"]) == ("priya", "person", did)
    with pytest.raises(eingang.Konflikt):  # zweimal übernehmen geht nicht
        eingang.uebernehmen(store, settings, v, von="priya", client=client(wp), felder={})


def test_kooperation_nur_status_und_notiz(settings, store, wp):
    v = wp.einreichen("kooperation", {"organisation": "Kulturhaus Beispiel", "anliegen": "Gemeinsame Lesereihe"})
    abholen_und_vorbereiten(store, wp)
    assert eingang.holen(store, v)["entwurf"] is None
    with pytest.raises(ValueError):
        eingang.uebernehmen(store, settings, v, von="priya", client=client(wp), felder={})
    eingang.notiz_setzen(store, v, "Rückruf am Montag", von="priya")
    eingang.abschliessen(store, v, "erledigt", von="priya", client=client(wp))
    e = eingang.holen(store, v)
    assert (e["status"], e["notiz"]) == ("erledigt", "Rückruf am Montag")
    assert wp.zeile(v)["status"] == "erledigt"
    assert store.db.execute("SELECT COUNT(*) FROM drafts").fetchone()[0] == 0


def test_status_bei_angehaltenem_eingang_wartet_und_geht_spaeter_hinaus(settings, store, wp):
    v = wp.einreichen("kontakt", {"nachricht": "Bitte um Rückruf"})
    abholen_und_vorbereiten(store, wp)
    schalter.setzen(store, "eingang", True, wer="anna", grund="Pause")
    eingang.abschliessen(store, v, "abgelehnt", von="priya", client=client(wp))
    assert wp.zeile(v)["status"] == "abgeholt" and eingang.holen(store, v)["status"] == "abgelehnt"
    schalter.setzen(store, "eingang", False, wer="anna")
    assert eingang.melden(store, client(wp))["gemeldet"] == 1
    assert wp.zeile(v)["status"] == "abgelehnt"


def test_unklarer_ausgang_wird_per_abfrage_abgeglichen(settings, store, wp):
    v = wp.einreichen("kontakt", {"nachricht": "Hallo"})
    abholen_und_vorbereiten(store, wp)
    wp.abbruch_nach_senden.add(v)
    eingang.abschliessen(store, v, "erledigt", von="priya", client=client(wp))
    assert wp.zeile(v)["status"] == "erledigt"
    assert eingang.holen(store, v)["wp_status"] == "erledigt"  # GET /einsendung/{vorgang} bestätigt
    assert eingang.melden(store, client(wp))["gemeldet"] == 0  # nichts mehr offen


def test_konflikt_auf_der_website_wird_vermerkt(settings, store, wp):
    v = wp.einreichen("kontakt", {"nachricht": "Hallo"})
    abholen_und_vorbereiten(store, wp)
    wp.zeile(v)["status"] = "spam"  # dort schon anders abgeschlossen
    eingang.abschliessen(store, v, "erledigt", von="priya", client=client(wp))
    e = eingang.holen(store, v)
    assert e["wp_status"] == "spam" and any("Website" in h for h in e["hinweise"])


def test_entscheidungen_sind_bedingt(settings, store, wp):
    v = wp.einreichen("kontakt", {"nachricht": "Hallo"})
    eingang.abholen(store, client(wp))
    with pytest.raises(eingang.Konflikt):  # noch nicht vorbereitet
        eingang.abschliessen(store, v, "erledigt", von="priya", client=client(wp))
    eingang.vorbereiten(store, None, jetzt=JETZT)
    eingang.abschliessen(store, v, "spam", von="priya", client=client(wp))
    with pytest.raises(eingang.Konflikt):
        eingang.abschliessen(store, v, "erledigt", von="priya", client=client(wp))
    with pytest.raises(ValueError):
        eingang.abschliessen(store, v, "vorbereitet", von="priya", client=client(wp))


# ---- Löschfrist --------------------------------------------------------------------------------------------------

def test_loeschfrist_90_tage_nach_abschluss_spam_7_tage(settings, store, wp):
    v_alt = wp.einreichen("kontakt", {"nachricht": "Alt"})
    v_spam = wp.einreichen("kontakt", {"nachricht": "Werbung für Pillen"})
    v_neu = wp.einreichen("kontakt", {"nachricht": "Neu"})
    v_offen = wp.einreichen("kontakt", {"nachricht": "Offen"})
    abholen_und_vorbereiten(store, wp)
    for v, st in ((v_alt, "erledigt"), (v_spam, "spam"), (v_neu, "erledigt")):
        eingang.abschliessen(store, v, st, von="priya", client=client(wp))
    vor = lambda tage: (datetime.now(timezone.utc) - timedelta(days=tage)).isoformat(timespec="seconds")
    store._write("UPDATE einsendungen SET abgeschlossen_at = ? WHERE vorgangsnummer = ?", (vor(91), v_alt))
    store._write("UPDATE einsendungen SET abgeschlossen_at = ? WHERE vorgangsnummer = ?", (vor(8), v_spam))
    store._write("UPDATE einsendungen SET abgeschlossen_at = ? WHERE vorgangsnummer = ?", (vor(30), v_neu))
    out = eingang.loeschen(store)
    assert (out["geloescht"], out["spam"]) == (1, 1)
    rest = {e["vorgangsnummer"] for e in eingang.liste(store, ansicht="alle")}
    assert rest == {v_neu, v_offen}
    zeile = repo.aktionen_liste(store, aktion="eingang_geloescht")[0]
    assert zeile["ausloeser"] == "dienst" and v_alt not in json.dumps(zeile)


# ---- Dienst ------------------------------------------------------------------------------------------------------

def test_dienst_plan_holt_mit_wordpress_ab_und_loescht_taeglich(settings):
    from news_radar import dienst

    assert "eingang" not in [e.name for e in dienst.plan(settings, env={})]
    settings.wp_url, settings.wp_user, settings.wp_app_password = "https://www.tamil.test", "ki-agent", "pw"
    plan = {e.name: e for e in dienst.plan(settings, env={})}
    assert plan["eingang"].args == ("eingang", "lauf") and plan["eingang"].kanaele == ("eingang",)
    assert plan["eingang"].regel.alle == 180
    assert plan["eingang-frist"].args == ("eingang", "loeschen") and plan["eingang-frist"].kanaele == ()
