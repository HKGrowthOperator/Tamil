"""Sammelfreigabe im Feed: mehrere Entwürfe auf einmal, jeder durch denselben Übergang wie einzeln.

Recht `freigeben` (leser 403), CSRF, eine Protokollzeile je Entwurf mit der Person, nicht freigebbare Entwürfe werden
mit Grund gemeldet, bei angehaltenem Kanal `website` sind sie freigegeben und warten.
"""

import pytest

from news_radar import schalter
from news_radar.config import load_settings
from news_radar.store import Store
from news_radar.web import create_app
from news_radar.workflow import repo

NUTZER = {"priya": ("priya-passwort-1", "redaktion"), "lena": ("lena-passwort-1", "leser")}


@pytest.fixture
def app(tmp_path, monkeypatch):
    for var in ("WP_URL", "WP_USER", "WP_APP_PASSWORD", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "GEMINI_API_KEY",
                "BILD_POOL_DIR", "NOTIFY_WEBHOOK_URL", "ANTHROPIC_API_KEY"):
        monkeypatch.setenv(var, "")
    settings = load_settings()
    settings.data_dir = tmp_path
    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim", "s3cret"
    with Store(settings.db_path) as store:
        for name, (pw, rolle) in NUTZER.items():
            repo.nutzer_anlegen(store, name, pw, rolle)
        for i in (1, 2, 3, 4):
            store.insert_draft(dict(uid=f"u{i}", typ="artikel", titel=f"Beitrag {i}", teaser="T", inhalt_html="<p>x</p>",
                                    kategorie="news", relevanz=8, dach_bezug=True, ort="Hamm", schlagworte=["x"],
                                    original_json={"titel": f"Beitrag {i}", "inhalt_html": "<p>x</p>"}))
        store.set_status(3, "ablehnen", von="test")
    app = create_app(settings, testing=True)
    app.config["DB"] = settings.db_path
    return app


def login(app, user):
    client = app.test_client()
    client.get("/login")
    with client.session_transaction() as s:
        token = s["csrf"]
    assert client.post("/login", data={"user": user, "password": NUTZER[user][0], "_csrf": token}).status_code == 302
    return client, token


def _status(app):
    with Store(app.config["DB"]) as store:
        return {i: store.get_draft(i)["status"] for i in (1, 2, 3, 4)}


def _protokoll(app, draft_id):
    with Store(app.config["DB"]) as store:
        return [(a["wer"], a["aktion"], a.get("kanal")) for a in repo.aktionen(store, draft_id)]


def test_feed_zeigt_auswahl_nur_fuer_freigebbare_und_nur_mit_recht(app):
    client, _ = login(app, "priya")
    html = client.get("/").get_data(as_text=True)
    assert 'action="/entwurf/sammelfreigabe"' in html and "data-sammel" in html
    assert html.count('name="ids"') == 3                       # 1, 2, 4 offen; 3 ist abgelehnt (anderer Reiter)
    assert "Alle sichtbaren auswählen" in html and "Ausgewählte freigeben" in html
    leser, _ = login(app, "lena")
    assert 'name="ids"' not in leser.get("/").get_data(as_text=True)


def test_leser_bekommt_403_und_nichts_aendert_sich(app):
    client, token = login(app, "lena")
    resp = client.post("/entwurf/sammelfreigabe", data={"_csrf": token, "ids": ["1", "2"]})
    assert resp.status_code == 403
    assert _status(app)[1] == "neu" and _protokoll(app, 1) == []


def test_ohne_csrf_abgelehnt(app):
    client, _ = login(app, "priya")
    assert client.post("/entwurf/sammelfreigabe", data={"ids": ["1"]}).status_code in (400, 403)
    assert _status(app)[1] == "neu"


def test_gemischte_auswahl_meldet_grund_und_protokolliert_je_entwurf(app):
    client, token = login(app, "priya")
    resp = client.post("/entwurf/sammelfreigabe", data={"_csrf": token, "ids": ["1", "2", "3", "99"]},
                       follow_redirects=True)
    html = resp.get_data(as_text=True)
    assert _status(app) == {1: "freigegeben", 2: "freigegeben", 3: "abgelehnt", 4: "neu"}
    assert "2 Entwürfe freigegeben" in html
    assert "Nicht freigegeben (2)" in html
    assert "#3" in html and "Abgelehnt" in html and "#99" in html and "nicht gefunden" in html
    assert _protokoll(app, 1) == [("priya", "freigeben", None)]
    assert _protokoll(app, 2) == [("priya", "freigeben", None)]
    assert _protokoll(app, 3) == []


def test_zweimal_derselbe_entwurf_und_leere_auswahl(app):
    client, token = login(app, "priya")
    client.post("/entwurf/sammelfreigabe", data={"_csrf": token, "ids": ["1", "1"]})
    assert _protokoll(app, 1) == [("priya", "freigeben", None)]
    html = client.post("/entwurf/sammelfreigabe", data={"_csrf": token}, follow_redirects=True).get_data(as_text=True)
    assert "Keine Entwürfe ausgewählt" in html


def test_website_angehalten_freigegeben_und_wartet(app):
    with Store(app.config["DB"]) as store:
        schalter.setzen(store, "website", True, wer="anna", grund="Prüfung")
    client, token = login(app, "priya")
    html = client.post("/entwurf/sammelfreigabe", data={"_csrf": token, "ids": ["1", "4"]},
                       follow_redirects=True).get_data(as_text=True)
    assert _status(app)[1] == _status(app)[4] == "freigegeben"
    assert "angehalten" in html and "warten" in html
    assert _protokoll(app, 4) == [("priya", "freigeben", None), ("priya", "zurueckgehalten", "website")]
