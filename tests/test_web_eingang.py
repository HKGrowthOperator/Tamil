"""Cockpit „Eingang“ (Festlegung F1): Liste, Prüfung, übernehmen als Entwurf, erledigt/abgelehnt/Spam, Notiz.
`leser` sieht, `redaktion` entscheidet; Kontaktdaten nur für die Redaktion, Antwort nur über einen mailto-Link."""

import pytest

from news_radar import eingang
from news_radar.abnahme.wp_eingang import FakeWordPressEingang
from news_radar.config import load_settings
from news_radar.store import Store
from news_radar.web import create_app
from news_radar.wordpress import TamilRadarClient
from news_radar.workflow import repo

from test_eingang import EVENT, JETZT

NUTZER = {"priya": ("priya-passwort-1", "redaktion"), "lena": ("lena-passwort-1", "leser")}


@pytest.fixture
def umgebung(tmp_path, monkeypatch):
    for var in ("WP_URL", "WP_USER", "WP_APP_PASSWORD", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "GEMINI_API_KEY",
                "BILD_POOL_DIR", "NOTIFY_WEBHOOK_URL", "ANTHROPIC_API_KEY"):
        monkeypatch.setenv(var, "")
    settings = load_settings()
    settings.data_dir = tmp_path
    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim", "s3cret"
    wp = FakeWordPressEingang()
    vorgaenge = {"event": wp.einreichen("event", EVENT, telefon="+49 30 1234567"),
                 "kooperation": wp.einreichen("kooperation", {"organisation": "Kulturhaus Beispiel",
                                                              "anliegen": "Gemeinsame Lesereihe"},
                                              name="Max Muster", email="max@example.test")}
    client = TamilRadarClient("https://www.tamil.test", "ki-agent", "pw", session=wp)
    with Store(settings.db_path) as store:
        for name, (pw, rolle) in NUTZER.items():
            repo.nutzer_anlegen(store, name, pw, rolle)
        eingang.abholen(store, client)
        eingang.vorbereiten(store, None, jetzt=JETZT)
    app = create_app(settings, testing=True)
    app.extensions["eingang_client"] = client
    return app, wp, vorgaenge, settings


def login(app, user):
    client = app.test_client()
    client.get("/login")
    with client.session_transaction() as s:
        token = s["csrf"]
    assert client.post("/login", data={"user": user, "password": NUTZER[user][0], "_csrf": token}).status_code == 302
    return client, token


def test_liste_und_pruefung_im_heutigen_stil(umgebung):
    app, _, vorgaenge, _ = umgebung
    c, _ = login(app, "priya")
    seite = c.get("/eingang").get_data(as_text=True)
    assert "Eingang" in seite and "Pongal-Fest Testverein" in seite and "Kooperation" in seite
    assert 'href="/eingang"' in c.get("/").get_data(as_text=True)  # in der Navigation
    detail = c.get(f"/eingang/{vorgaenge['event']}").get_data(as_text=True)
    assert eingang.VERMERK in detail and "Als Entwurf übernehmen" in detail
    assert "erika@example.test" in detail and "mailto:erika@example.test" in detail
    assert "<script>" not in detail.split("</head>")[1].replace('<script src="/static/app.js"></script>', "")
    assert c.get("/eingang/T000000-AAAAA").status_code == 404


def test_leser_sieht_aber_entscheidet_nicht_und_sieht_keine_kontaktdaten(umgebung):
    app, wp, vorgaenge, _ = umgebung
    c, token = login(app, "lena")
    detail = c.get(f"/eingang/{vorgaenge['event']}")
    assert detail.status_code == 200
    text = detail.get_data(as_text=True)
    assert "Pongal-Fest Testverein" in text and "erika@example.test" not in text and "1234567" not in text
    assert "Als Entwurf übernehmen" not in text
    for pfad, daten in (("uebernehmen", {"titel": "X"}), ("status", {"status": "spam"}), ("notiz", {"notiz": "x"})):
        r = c.post(f"/eingang/{vorgaenge['event']}/{pfad}", data={"_csrf": token, **daten})
        assert r.status_code == 403, pfad
    assert wp.zeile(vorgaenge["event"])["status"] == "abgeholt"


def test_redaktion_uebernimmt_und_landet_im_entwurf(umgebung):
    app, wp, vorgaenge, settings = umgebung
    c, token = login(app, "priya")
    r = c.post(f"/eingang/{vorgaenge['event']}/uebernehmen",
               data={"_csrf": token, "titel": "Pongal-Fest in Essen", "teaser": "Tanz und Musik.",
                     "text": "Tanz, Musik und Essen.", "event_datum": "2027-01-16T18:30", "event_ort": "Gemeindesaal, Essen",
                     "ticket_url": EVENT["ticket_link"]})
    assert r.status_code == 302 and "/entwurf/" in r.headers["Location"]
    with Store(settings.db_path) as store:
        d = store.list_drafts("neu")[0]
        assert d["titel"] == "Pongal-Fest in Essen" and eingang.VERMERK in d["hinweise"]
    assert wp.zeile(vorgaenge["event"])["status"] == "uebernommen"
    entwurf = c.get(r.headers["Location"]).get_data(as_text=True)
    assert eingang.VERMERK in entwurf
    nochmal = c.post(f"/eingang/{vorgaenge['event']}/uebernehmen", data={"_csrf": token, "titel": "X"})
    assert nochmal.status_code == 302  # zurück zur Einsendung mit Meldung, kein zweiter Entwurf
    with Store(settings.db_path) as store:
        assert len(store.list_drafts()) == 1


def test_kooperation_status_und_notiz_ohne_entwurf(umgebung):
    app, wp, vorgaenge, settings = umgebung
    c, token = login(app, "priya")
    v = vorgaenge["kooperation"]
    detail = c.get(f"/eingang/{v}").get_data(as_text=True)
    assert "Als Entwurf übernehmen" not in detail and "mailto:max@example.test" in detail
    assert c.post(f"/eingang/{v}/notiz", data={"_csrf": token, "notiz": "Rückruf Montag"}).status_code == 302
    assert c.post(f"/eingang/{v}/status", data={"_csrf": token, "status": "erledigt"}).status_code == 302
    assert c.post(f"/eingang/{v}/status", data={"_csrf": token, "status": "vorbereitet"}).status_code == 400
    with Store(settings.db_path) as store:
        e = eingang.holen(store, v)
        assert (e["status"], e["notiz"]) == ("erledigt", "Rückruf Montag")
        assert store.list_drafts() == []
    assert wp.zeile(v)["status"] == "erledigt"
    assert "Kulturhaus Beispiel" in c.get("/eingang?ansicht=abgeschlossen").get_data(as_text=True)
