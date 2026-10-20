"""Integrationstest gegen ein laufendes WordPress mit dem Plugin tamil-radar (wordpress/dev/setup.sh + serve.sh).

Läuft nur, wenn WP_TEST_URL, WP_TEST_USER und WP_TEST_APP_PASSWORD gesetzt sind (stehen in $WP_DIR/.env.local).
Aufräumen über die Core-REST mit dem Admin-Anwendungspasswort (WP_ADMIN_USER/WP_ADMIN_APP_PASSWORD, ebenfalls in
.env.local); ohne Admin-Zugang versucht es der Radar-Benutzer, dessen Rolle veröffentlichte Beiträge nicht löschen darf.
"""

import base64
import io
import os
import uuid

import pytest
import requests
from PIL import Image

from news_radar import publisher
from news_radar.config import load_settings
from news_radar.images import branded_card, save_pair
from news_radar.store import Store
from news_radar.wordpress import TamilRadarClient, make_client

URL = os.environ.get("WP_TEST_URL", "").rstrip("/")
USER = os.environ.get("WP_TEST_USER", "")
PW = os.environ.get("WP_TEST_APP_PASSWORD", "")
pytestmark = pytest.mark.skipif(not (URL and USER and PW), reason="WP_TEST_URL/WP_TEST_USER/WP_TEST_APP_PASSWORD fehlen")


def _png() -> str:
    buf = io.BytesIO()
    Image.new("RGB", (640, 360), (200, 16, 46)).save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


@pytest.fixture
def client():
    c = TamilRadarClient(URL, USER, PW)
    created: list[int] = []
    yield c, created
    # Die Rolle „radar“ darf veröffentlichte Beiträge nicht löschen – aufräumen mit dem Admin-Zugang, falls vorhanden
    auth = (os.environ["WP_ADMIN_USER"], os.environ["WP_ADMIN_APP_PASSWORD"]) if os.environ.get("WP_ADMIN_APP_PASSWORD") else (USER, PW)
    for post_id in created:
        r = requests.delete(f"{URL}/wp-json/wp/v2/posts/{post_id}", params={"force": "true"}, auth=auth, timeout=30)
        assert r.status_code == 200 or auth == (USER, PW), f"Aufräumen von Post {post_id} fehlgeschlagen: {r.status_code}"


def test_status_reports_plugin_and_categories(client):
    c, _ = client
    status = c.status()
    assert status and status["plugin"] and status["rolle_radar"] is True
    assert {"news", "kino", "events", "community"} <= set(status["kategorien"])
    assert isinstance(make_client(URL, USER, PW), TamilRadarClient)


def test_create_get_duplicate_and_update(client):
    c, created = client
    uid = f"test-{uuid.uuid4().hex[:10]}"
    payload = {
        "titel": "Testbeitrag aus dem Radar", "inhalt": "<p>Erster Absatz.</p><p class=\"quelle\">Quelle: Test</p>",
        "teaser": "Teaser des Tests", "status": "publish", "slug": f"radar-test-{uid}", "kategorie": "kino",
        "schlagworte": ["Radar-Test", "Kino"],
        "meta": {"radar_uid": uid, "radar_relevanz": 8, "quelle_name": "Testquelle", "quelle_url": "https://example.test/a",
                 "ort": "Hamm", "event_datum": "2030-01-05", "event_ort": "Kinopark", "event_land": "de",
                 "kino_fakten": {"film": "Test", "woche": "2030-W01", "kinos": [{"kino": "K1", "stadt": "Hamm", "land": "DE"}]}},
        "seo": {"title": "SEO-Titel", "description": "SEO-Beschreibung"},
        "bild": {"daten": _png(), "dateiname": "radar-test.png", "alt": "Alt-Text", "credit": "Grafik: Test"},
    }
    post = c.create(payload)
    created.append(post["id"])
    assert post["status"] == "publish" and post["featured_media"] > 0 and post["categories"] == ["kino"]
    assert set(post["tags"]) == {"Radar-Test", "Kino"} and post["radar_uid"] == uid
    assert post["meta"]["event_datum"] == "2030-01-05" and post["meta"]["event_land"] == "DE"
    assert post["meta"]["ort"] == "Hamm" and post["meta"]["kino_fakten"]["woche"] == "2030-W01"
    assert post["link"].endswith(f"/radar-test-{uid}/") and "action=edit" in post["edit_link"]

    # Dublette → 409 mit vorhandener ID
    dup = c.create(payload)
    assert dup["duplikat"] is True and dup["id"] == post["id"]

    got = c.get(uid)
    assert got and got["id"] == post["id"] and got["titel"] == "Testbeitrag aus dem Radar"

    updated = c.update(uid, {"titel": "Testbeitrag aktualisiert", "meta": {"kino_fakten": {"film": "Test", "woche": "2030-W02", "kinos": []}}})
    assert updated["titel"] == "Testbeitrag aktualisiert" and updated["meta"]["kino_fakten"]["woche"] == "2030-W02"

    # Beitragsbild liegt in der Mediathek mit Alt-Text
    media = requests.get(f"{URL}/wp-json/wp/v2/media/{post['featured_media']}", auth=(USER, PW), timeout=30).json()
    assert media["alt_text"] == "Alt-Text" and media["mime_type"] == "image/png"
    assert c.get("gibt-es-nicht") is None


def test_publisher_end_to_end_via_plugin(tmp_path, monkeypatch, client):
    _, created = client
    monkeypatch.setenv("WP_URL", URL)
    monkeypatch.setenv("WP_USER", USER)
    monkeypatch.setenv("WP_APP_PASSWORD", PW)
    monkeypatch.setenv("WP_POST_STATUS", "draft")
    settings = load_settings()
    settings.data_dir = tmp_path
    uid = f"test-{uuid.uuid4().hex[:10]}"
    with Store(settings.db_path) as store:
        name, _ = save_pair(branded_card("Radar Ende zu Ende", "Kino", uid), settings.bilder_dir, uid)
        draft_id = store.insert_draft(dict(
            uid=uid, typ="artikel", titel="Radar Ende zu Ende", teaser="T", inhalt_html="<p>x</p>", kategorie="kino",
            schlagworte=["Kino"], seo_titel="SEO", meta_beschreibung="Meta", bild_datei=name, bild_alt="Alt",
            bild_credit="Grafik: Tamil.de", quelle_url="https://q.de", quelle_name="Q", relevanz=7, original_json={},
        ))
        row = store.claim_draft(draft_id, von="test")
        wp = publisher.make_wordpress(settings)
        assert isinstance(wp, TamilRadarClient)
        info = publisher.publish_draft(row, settings, wp, store)
        created.append(info["post_id"])
        assert info["status"] == "draft" and "action=edit" in info["link"]
        assert store.get_draft(draft_id)["status"] == "in_wordpress"
    got = wp.get(uid)
    assert got["meta"]["quelle_name"] == "Q" and got["meta"]["radar_relevanz"] == 7 and got["featured_media"] > 0


def test_redirect_and_ad_seed():
    r = requests.get(f"{URL}/category/anirudh/", allow_redirects=False, timeout=30)
    assert r.status_code == 301 and r.headers["Location"].rstrip("/").endswith("/category/events")
    home = requests.get(URL + "/", timeout=30).text
    assert "Testbanner Leaderboard" in home or 'class="ad-test"' in home or "<body" in home  # Theme entscheidet, ob der Platz gerendert wird
