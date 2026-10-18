"""Freigabe-App mit dem Flask-Test-Client: Login, CSRF, Feed, Aktionen, Bearbeiten, Bild, Direkt posten."""

import io
import json

import pytest
from PIL import Image

from news_radar.config import load_settings
from news_radar.images import branded_card, save_pair
from news_radar.store import Store
from news_radar.web import create_app
from news_radar.writer import Draft


class FakeWriter:
    def __init__(self):
        self.calls = []

    def rewrite(self, row, anweisung, timeout=80.0):
        self.calls.append(anweisung)
        return Draft(relevanz=8, begruendung="ok", kategorie="kino", typ="artikel", dach_bezug=True, ort="Mainz",
                     titel="Neu geschrieben", teaser="Neuer Teaser", inhalt_html="<p>neu</p>", schlagworte=["x"],
                     seo_titel="s", meta_beschreibung="m", bild_suchbegriff="q", bild_alt="a", event_datum="", event_ort="", ticket_url="")


class FakeWP:
    def __init__(self):
        self.posts = []

    def upload_media(self, image, alt):
        return 9

    def create_post(self, **kw):
        self.posts.append(kw)
        return {"id": 500 + len(self.posts), "link": f"https://www.tamil.de/{kw['slug']}/"}

    def edit_link(self, post):
        return f"https://www.tamil.de/wp-admin/post.php?post={post['id']}&action=edit"


@pytest.fixture
def app(tmp_path, monkeypatch):
    for var in ("WP_URL", "WP_USER", "WP_APP_PASSWORD", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY"):
        monkeypatch.setenv(var, "")
    settings = load_settings()
    settings.data_dir = tmp_path
    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim", "s3cret"
    settings.web_url = "https://radar.test"
    app = create_app(settings, testing=True)
    app.extensions["writer"] = FakeWriter()
    with Store(settings.db_path) as store:
        for i, (titel, status) in enumerate([("Jailer 2 in Mainz", "neu"), ("Pongal in Hamburg", "neu"), ("Alt", "abgelehnt")], 1):
            name, _ = save_pair(branded_card(titel, "Kino", f"u{i}"), settings.bilder_dir, f"u{i}-x")
            store.insert_draft(dict(uid=f"u{i}", typ="artikel", titel=titel, teaser="T", inhalt_html="<p>Text</p>", kategorie="kino",
                                    relevanz=8, dach_bezug=True, ort="Mainz", schlagworte=["Kino"], bild_datei=name, bild_alt="alt",
                                    quelle_url="https://q.de/1", quelle_name="Q", original_json={"titel": titel, "inhalt_html": "<p>Text</p>",
                                    "teaser": "T", "schlagworte": ["Kino"]}))
            if status == "abgelehnt":
                store.set_status(i, "ablehnen")
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def login(client):
    client.get("/login")  # CSRF-Token in die Session
    with client.session_transaction() as s:
        token = s["csrf"]
    resp = client.post("/login", data={"user": "luis", "password": "geheim", "_csrf": token})
    assert resp.status_code == 302
    return token


def test_requires_login(client):
    resp = client.get("/")
    assert resp.status_code == 302 and "/login" in resp.headers["Location"]
    assert client.get("/manifest.webmanifest").status_code == 200
    assert client.get("/gesund").json["ok"] is True
    assert client.get("/sw.js").status_code == 200


def test_login_wrong_password_then_ok(client, monkeypatch):
    monkeypatch.setattr("news_radar.web.time.sleep", lambda s: None)
    client.get("/login")
    with client.session_transaction() as s:
        token = s["csrf"]
    resp = client.post("/login", data={"user": "luis", "password": "falsch", "_csrf": token}, follow_redirects=True)
    assert "falsch" in resp.get_data(as_text=True)
    login(client)
    resp = client.get("/")
    assert resp.status_code == 200 and "Jailer 2 in Mainz" in resp.get_data(as_text=True)
    assert resp.headers["Cache-Control"] == "private, no-store"


def test_feed_tabs_and_counts(client):
    login(client)
    html = client.get("/?status=neu").get_data(as_text=True)
    assert "Neu <b>2</b>" in html and "Abgelehnt <b>1</b>" in html and "Direkt posten" not in html  # kein WP konfiguriert
    assert "Alt" in client.get("/?status=abgelehnt").get_data(as_text=True)
    assert client.get("/?status=quatsch").status_code == 404


def test_status_action_requires_csrf_and_follows_transitions(client):
    token = login(client)
    assert client.post("/entwurf/1/status", data={"aktion": "freigeben"}).status_code == 400
    resp = client.post("/entwurf/1/status", data={"aktion": "freigeben", "_csrf": token, "next": "/?status=neu"})
    assert resp.status_code == 302 and resp.headers["Location"].endswith("/?status=neu")
    assert client.post("/entwurf/3/status", data={"aktion": "freigeben", "_csrf": token}).status_code == 409
    assert client.post("/entwurf/1/status", data={"aktion": "explodieren", "_csrf": token}).status_code == 400
    html = client.get("/?status=freigegeben").get_data(as_text=True)
    assert "Jailer 2 in Mainz" in html and "Zurückziehen" in html


def test_edit_saves_and_sets_bearbeitet(client, app):
    token = login(client)
    resp = client.post("/entwurf/1", data={
        "_csrf": token, "titel": "Jailer 2 startet in Mainz", "teaser": "Neu", "kategorie": "events", "schlagworte": "Kino, Mainz ,",
        "inhalt_html": "<p>Hallo</p><script>x</script>", "seo_titel": "", "meta_beschreibung": "", "bild_alt": "Bild",
        "event_datum": "", "event_ort": "", "ticket_url": "",
    })
    assert resp.status_code == 302
    with Store(app.extensions["settings"].db_path) as store:
        d = store.get_draft(1)
    assert d["status"] == "bearbeitet" and d["titel"] == "Jailer 2 startet in Mainz" and d["kategorie"] == "events"
    assert d["schlagworte"] == ["Kino", "Mainz"] and d["inhalt_html"] == "<p>Hallo</p>" and d["bearbeitet_von"] == "luis"
    html = client.get("/entwurf/1").get_data(as_text=True)
    assert "Jailer 2 startet in Mainz" in html and "Bearbeitet" in html
    assert 'value="None"' not in html and ">None<" not in html  # leere Felder nie als „None“ anzeigen


def test_rewrite_uses_writer_and_reset_restores_original(client, app):
    token = login(client)
    client.post("/entwurf/1/neu-schreiben", data={"_csrf": token, "anweisung": "kürzer"})
    with Store(app.extensions["settings"].db_path) as store:
        d = store.get_draft(1)
        assert d["titel"] == "Neu geschrieben" and d["rewrite_count"] == 1 and d["status"] == "bearbeitet"
        assert json.loads(d["original_json"])["titel"] == "Jailer 2 in Mainz"
    assert app.extensions["writer"].calls == ["kürzer"]
    client.post("/entwurf/1/zuruecksetzen", data={"_csrf": token})
    with Store(app.extensions["settings"].db_path) as store:
        assert store.get_draft(1)["titel"] == "Jailer 2 in Mainz"


def test_image_actions_card_and_upload(client, app):
    token = login(client)
    settings = app.extensions["settings"]
    with Store(settings.db_path) as store:
        before = store.get_draft(1)["bild_datei"]
    client.post("/entwurf/1/bild", data={"_csrf": token, "aktion": "karte"})
    buf = io.BytesIO()
    Image.new("RGB", (800, 300), (10, 10, 200)).save(buf, "PNG")
    buf.seek(0)
    resp = client.post("/entwurf/1/bild", data={"_csrf": token, "aktion": "upload", "datei": (buf, "foto.png"), "credit": "Foto: Luis"},
                       content_type="multipart/form-data")
    assert resp.status_code == 302
    with Store(settings.db_path) as store:
        d = store.get_draft(1)
    assert d["bild_origin"] == "upload" and d["bild_credit"] == "Foto: Luis" and d["bild_datei"] != before
    assert not (settings.bilder_dir / before).exists()
    img = client.get(f"/bild/{d['bild_datei']}")
    assert img.status_code == 200 and Image.open(io.BytesIO(img.data)).size == (1200, 675)
    assert client.get("/bild/../etc/passwd").status_code == 404


def test_publish_without_wordpress_marks_freigegeben(client, app):
    token = login(client)
    resp = client.post("/entwurf/1/veroeffentlichen", data={"_csrf": token}, follow_redirects=True)
    assert "noch nicht angebunden" in resp.get_data(as_text=True)
    with Store(app.extensions["settings"].db_path) as store:
        assert store.get_draft(1)["status"] == "freigegeben"


def test_direct_post_and_wordpress_draft(client, app):
    token = login(client)
    wp = app.extensions["wordpress"] = FakeWP()
    assert "Direkt posten" in client.get("/").get_data(as_text=True)
    resp = client.post("/entwurf/1/veroeffentlichen", data={"_csrf": token}, follow_redirects=True)
    assert "Live auf tamil.de" in resp.get_data(as_text=True)
    assert wp.posts[0]["status"] == "publish" and wp.posts[0]["media_id"] == 9
    resp = client.post("/entwurf/2/wp-entwurf", data={"_csrf": token}, follow_redirects=True)
    assert "WordPress-Entwurf" in resp.get_data(as_text=True) and wp.posts[1]["status"] == "draft"
    with Store(app.extensions["settings"].db_path) as store:
        assert store.get_draft(1)["status"] == "veroeffentlicht" and store.get_draft(2)["status"] == "in_wordpress"
    assert client.post("/entwurf/1/veroeffentlichen", data={"_csrf": token}).status_code == 409
    html = client.get("/?status=veroeffentlicht").get_data(as_text=True)
    assert "Jailer 2 in Mainz" in html and "Pongal in Hamburg" in html


def test_preview_dashboard_and_protokoll(client, app):
    login(client)
    html = client.get("/vorschau/1").get_data(as_text=True)
    assert "<h1>Jailer 2 in Mainz</h1>" in html and 'class="quelle"' in html
    assert client.get("/dashboard").status_code == 200 and client.get("/dashboard?tage=30").status_code == 200
    with Store(app.extensions["settings"].db_path) as store:
        store.event("lauf", gesammelt=3)
    assert "lauf" in client.get("/protokoll").get_data(as_text=True)
    lines = client.get("/protokoll.jsonl").get_data(as_text=True).strip().splitlines()
    assert json.loads(lines[0])["event"] == "lauf"
    assert client.get("/entwurf/999").status_code == 404


def test_create_app_requires_secret(app):
    settings = app.extensions["settings"]
    settings.web_secret = ""
    with pytest.raises(RuntimeError):
        create_app(settings)


def test_feed_marks_rohfassung_and_rewrite_clears_it(app, client):
    from news_radar.writer import ROH_HINWEIS

    settings = app.extensions["settings"]
    with Store(settings.db_path) as store:
        name, _ = save_pair(branded_card("Roh", "Kino", "u9"), settings.bilder_dir, "u9-x")
        store.insert_draft(dict(uid="u9", typ="artikel", titel="Rohe Meldung aus Hamm", teaser="T", inhalt_html="<p>Text</p>", kategorie="community",
                                relevanz=7, dach_bezug=True, ort="Hamm", schlagworte=[], bild_datei=name, bild_alt="alt", quelle_url="https://q.de/9",
                                quelle_name="WA Hamm", hinweise=[ROH_HINWEIS], original_json={"titel": "Rohe Meldung aus Hamm"}))
    token = login(client)
    html = client.get("/?status=neu").get_data(as_text=True)
    assert 'class="badge hinweis roh"' in html and ">Rohfassung<" in html
    assert "Rohfassung ohne KI" in client.get("/entwurf/4").get_data(as_text=True)
    resp = client.post("/entwurf/4/neu-schreiben", data={"anweisung": "kürzer", "_csrf": token})
    assert resp.status_code == 302
    with Store(settings.db_path) as store:
        assert store.get_draft(4)["hinweise"] == [] and store.get_draft(4)["titel"] == "Neu geschrieben"
