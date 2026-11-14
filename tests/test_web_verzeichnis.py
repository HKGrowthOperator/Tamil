"""Cockpit „Verzeichnis“ (Festlegung F2, Abnahmetest T4): Liste, Prüfung, neu freigeben, Änderung alt neben neu
Feld für Feld, Entfernen mit Bestätigung, Ablehnen; 409 bei veraltetem Stand sichtbar; Premium nie. `leser` sieht,
`redaktion` entscheidet; Name und E-Mail des Einsenders nur für die Redaktion. Alle Angaben erfunden (example.test)."""

import re

import pytest

from news_radar import verzeichnis
from news_radar.abnahme.wp_verzeichnis import FakeWordPressVerzeichnis
from news_radar.config import load_settings
from news_radar.store import Store
from news_radar.web import create_app
from news_radar.wordpress import TamilRadarClient
from news_radar.workflow import repo

from test_verzeichnis_agent import VEREIN

NUTZER = {"priya": ("priya-passwort-1", "redaktion"), "lena": ("lena-passwort-1", "leser")}


@pytest.fixture
def umgebung(tmp_path, monkeypatch):
    for var in ("WP_URL", "WP_USER", "WP_APP_PASSWORD", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "GEMINI_API_KEY",
                "BILD_POOL_DIR", "NOTIFY_WEBHOOK_URL", "ANTHROPIC_API_KEY"):
        monkeypatch.setenv(var, "")
    settings = load_settings()
    settings.data_dir = tmp_path
    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim", "s3cret"
    wp = FakeWordPressVerzeichnis()
    eid = wp.eintrag_anlegen({**VEREIN, "email": "alt@verein.example.test"})
    vorgaenge = {
        "neu": wp.einreichen("neu", {**VEREIN, "name": "Murugan-Tempel Hamm", "art": "tempel", "plz": "59069",
                                     "stadt": "Hamm", "telefon": "+49 2381 123456", "website": ""},
                             name="Max Muster", email="max@example.test"),
        "aenderung": wp.einreichen("aenderung", {"telefon": "+49 201 7654321", "email": "neu@verein.example.test"},
                                   eintrag_id=eid),
        "entfernen": wp.einreichen("entfernen", {}, eintrag_id=eid),
    }
    client = TamilRadarClient("https://www.tamil.test", "ki-agent", "pw", session=wp)
    with Store(settings.db_path) as store:
        for name, (pw, rolle) in NUTZER.items():
            repo.nutzer_anlegen(store, name, pw, rolle)
        verzeichnis.lauf(store, client)
    app = create_app(settings, testing=True)
    app.extensions["verzeichnis_client"] = client
    return app, wp, vorgaenge, settings, eid


def login(app, user):
    client = app.test_client()
    client.get("/login")
    with client.session_transaction() as s:
        token = s["csrf"]
    assert client.post("/login", data={"user": user, "password": NUTZER[user][0], "_csrf": token}).status_code == 302
    return client, token


def schreibende(wp):
    return [(r, k) for _, r, k in wp.koerper if r.startswith("eintrag")]


def test_liste_und_neu_mit_hinweisen(umgebung):
    app, _, vorgaenge, _, _ = umgebung
    c, _ = login(app, "priya")
    seite = c.get("/verzeichnis")
    assert seite.status_code == 200
    text = seite.get_data(as_text=True)
    assert "Murugan-Tempel Hamm" in text and "Änderung" in text and "Entfernen" in text
    assert 'href="/verzeichnis"' in c.get("/").get_data(as_text=True)  # in der Navigation
    detail = c.get(f"/verzeichnis/{vorgaenge['neu']}")
    html = detail.get_data(as_text=True)
    assert "Prüfung des Agenten" in html and "ohne Modell geprüft" in html and "Freigeben und veröffentlichen" in html
    assert "max@example.test" in html  # die Redaktion sieht den Einsender
    assert 'name="premium"' not in html and "Premium setzt nur ein Administrator" in html
    assert "<script>" not in html.split("</head>")[1].replace('<script src="/static/app.js"></script>', "")
    assert "script-src 'self'" in detail.headers["Content-Security-Policy"]
    assert c.get("/verzeichnis/V000000-AAAAA").status_code == 404


def test_leser_sieht_aber_entscheidet_nicht_und_sieht_keinen_einsender(umgebung):
    app, wp, vorgaenge, _, _ = umgebung
    c, token = login(app, "lena")
    html = c.get(f"/verzeichnis/{vorgaenge['neu']}").get_data(as_text=True)
    assert "Murugan-Tempel Hamm" in html and "max@example.test" not in html and "Max Muster" not in html
    assert "Freigeben und veröffentlichen" not in html and "Ablehnen" not in html
    for pfad in ("freigeben", "ablehnen"):
        assert c.post(f"/verzeichnis/{vorgaenge['neu']}/{pfad}", data={"_csrf": token}).status_code == 403
    assert schreibende(wp) == [] and wp.einsendung(vorgaenge["neu"])["status"] == "geprueft"


def test_t4_neu_freigeben_ueber_das_cockpit(umgebung):
    app, wp, vorgaenge, settings, _ = umgebung
    c, token = login(app, "priya")
    v = vorgaenge["neu"]
    r = c.post(f"/verzeichnis/{v}/freigeben", data={"_csrf": token, "wert_name": "Sri Murugan-Tempel Hamm",
                                                    "kategorie": "tempel-hindu-tempel", "wert_oeffnungszeiten": "immer"})
    assert r.status_code == 302 and r.headers["Location"].endswith("/verzeichnis")
    (route, koerper), = schreibende(wp)
    assert route == "eintrag" and koerper["felder"]["name"] == "Sri Murugan-Tempel Hamm"
    assert koerper["felder"]["kategorie"] == "tempel-hindu-tempel"
    assert "oeffnungszeiten" not in koerper["felder"]  # nicht eingesandt: das Formular ergänzt nichts
    with Store(settings.db_path) as store:
        assert verzeichnis.holen(store, v)["status"] == "freigegeben"
    assert "Freigegeben" in c.get("/verzeichnis").get_data(as_text=True)


def test_premium_im_formular_wird_abgewiesen(umgebung):
    app, wp, vorgaenge, settings, _ = umgebung
    c, token = login(app, "priya")
    for feld in ("premium", "wert_premium"):
        r = c.post(f"/verzeichnis/{vorgaenge['neu']}/freigeben", data={"_csrf": token, feld: "1"})
        assert r.status_code == 400
    assert schreibende(wp) == []


def test_t4_aenderung_alt_neben_neu_feldweise_und_409(umgebung):
    app, wp, vorgaenge, settings, eid = umgebung
    c, token = login(app, "priya")
    v = vorgaenge["aenderung"]
    html = c.get(f"/verzeichnis/{v}").get_data(as_text=True)
    zeile = re.search(r"<tr class=\"warn\"><th scope=\"row\"><label[^>]*>[^<]*<input[^>]*> Telefon</label></th>(.*?)</tr>",
                      html, re.S).group(1)
    assert "+49 201 1234567" in zeile and "+49 201 7654321" in zeile  # alt neben neu
    assert 'name="annehmen" value="telefon"' in html and 'name="annehmen" value="email"' in html
    wp.eintraege[eid]["felder"]["website"] = "https://neu.example.test"  # jemand ändert in wp-admin
    r = c.post(f"/verzeichnis/{v}/freigeben", data={"_csrf": token, "annehmen": ["telefon"]})
    assert r.status_code == 302 and r.headers["Location"].endswith(f"/verzeichnis/{v}")
    seite = c.get(f"/verzeichnis/{v}").get_data(as_text=True)
    assert "seit dem Lesen" in seite and "neu geladen" in seite  # 409 sauber angezeigt
    assert wp.eintraege[eid]["felder"]["telefon"] == "+49 201 1234567"
    r = c.post(f"/verzeichnis/{v}/freigeben", data={"_csrf": token, "annehmen": ["telefon"]})
    assert r.status_code == 302 and r.headers["Location"].endswith("/verzeichnis")
    assert wp.eintraege[eid]["felder"]["telefon"] == "+49 201 7654321"
    assert wp.eintraege[eid]["felder"]["email"] == "alt@verein.example.test"  # nicht angenommen: unverändert


def test_t4_ablehnen_aendert_nichts(umgebung):
    app, wp, vorgaenge, settings, eid = umgebung
    c, token = login(app, "priya")
    vorher = dict(wp.eintraege[eid]["felder"])
    r = c.post(f"/verzeichnis/{vorgaenge['aenderung']}/ablehnen", data={"_csrf": token})
    assert r.status_code == 302
    assert wp.eintraege[eid]["felder"] == vorher and schreibende(wp) == []
    assert wp.einsendung(vorgaenge["aenderung"])["status"] == "abgelehnt"


def test_entfernen_mit_bestaetigung(umgebung):
    app, wp, vorgaenge, settings, eid = umgebung
    c, token = login(app, "priya")
    v = vorgaenge["entfernen"]
    html = c.get(f"/verzeichnis/{v}").get_data(as_text=True)
    assert "wirklich aus dem Verzeichnis nehmen" in html and "Tamilischer Kulturverein Essen" in html
    assert c.post(f"/verzeichnis/{v}/freigeben", data={"_csrf": token}).status_code == 302
    assert wp.eintraege[eid]["status"] == "entfernt"


def test_annehmen_haekchen_vorne_in_der_feldspalte(umgebung):
    """P3-a: das Häkchen steht mit der Feldbezeichnung als Label in der ersten Spalte (am Handy sichtbar, groß)."""
    app, _, vorgaenge, _, _ = umgebung
    c, _ = login(app, "priya")
    html = c.get(f"/verzeichnis/{vorgaenge['aenderung']}").get_data(as_text=True)
    assert re.search(r'<th scope="row"><label class="auswahl"><input type="checkbox" name="annehmen" value="telefon"'
                     r'[^>]*> Telefon</label></th>', html)
    assert '<th scope="col">Annehmen</th>' not in html


def test_kategorie_leeren_im_formular(umgebung):
    app, wp, vorgaenge, _, eid = umgebung
    c, token = login(app, "priya")
    wp.eintraege[eid]["felder"]["kategorie"] = "verein-kultur"
    v = vorgaenge["aenderung"]
    html = c.get(f"/verzeichnis/{v}").get_data(as_text=True)
    assert 'value="-"' in html and "keine Kategorie" in html


def test_bereits_freigegeben_zeigt_hinweis_statt_angelegt(umgebung):
    app, wp, vorgaenge, _, _ = umgebung
    c, token = login(app, "priya")
    v = vorgaenge["neu"]
    felder = {k: f["wert"] for k, f in wp.einsendung(v)["felder"].items() if f["wert"]}
    assert TamilRadarClient("https://www.tamil.test", "u", "p", session=wp).vz_anlegen(v, felder)[0] == 201
    c.post(f"/verzeichnis/{v}/freigeben", data={"_csrf": token, "wert_name": "Anderer Name"})
    seite = c.get("/verzeichnis").get_data(as_text=True)
    assert "hatte schon freigegeben" in seite and "nicht übernommen" in seite and "angelegt" not in seite
