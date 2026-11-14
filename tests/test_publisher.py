import pytest

from news_radar import publisher
from news_radar.config import load_settings
from news_radar.images import branded_card, save_pair
from news_radar.store import Store
from lizenz_hilfe import lizenz_setzen


class FakeWP:
    def __init__(self, fail_on=None):
        self.posts, self.media = [], []
        self.fail_on = fail_on

    def upload_media(self, image, alt):
        self.media.append((image.filename, alt, len(image.data)))
        return 40 + len(self.media)

    def create_post(self, **kw):
        if self.fail_on and self.fail_on in kw["title"]:
            raise RuntimeError("WordPress POST posts -> 500: kaputt")
        self.posts.append(kw)
        return {"id": 100 + len(self.posts), "link": f"https://www.tamil.de/{kw['slug']}/"}

    def edit_link(self, post):
        return f"https://www.tamil.de/wp-admin/post.php?post={post['id']}&action=edit"


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("WP_URL", "https://www.tamil.de")
    monkeypatch.setenv("WP_USER", "ki-agent")
    monkeypatch.setenv("WP_APP_PASSWORD", "xxxx")
    monkeypatch.setenv("WP_SEO_META", "rankmath")
    settings = load_settings()
    settings.data_dir = tmp_path
    store = Store(settings.db_path)
    yield settings, store
    store.close()


def seed(settings, store, uid, titel, status="neu"):
    name, _ = save_pair(branded_card(titel, "Kino", uid), settings.bilder_dir, uid)
    draft_id = store.insert_draft(dict(
        uid=uid, typ="artikel", titel=titel, teaser="T", inhalt_html="<p>x</p>", kategorie="kino",
        schlagworte=["Kino"], seo_titel="SEO", meta_beschreibung="Meta", bild_datei=name, bild_alt="Alt",
        bild_credit="Grafik: Tamil.de", quelle_url="https://q.de", quelle_name="Q", original_json={},
    ))
    lizenz_setzen(store, draft_id, settings)  # Bildkarte mit vollständigem Lizenz-Datensatz
    if status == "freigegeben":
        store.set_status(draft_id, "freigeben")
    return draft_id


def test_publish_only_freigegeben(env):
    settings, store = env
    seed(settings, store, "a", "Neu bleibt neu")
    seed(settings, store, "b", "Freigegeben eins", "freigegeben")
    seed(settings, store, "c", "Freigegeben zwei", "freigegeben")
    wp = FakeWP()
    results = publisher.publish_approved(settings, store, wp)
    assert [r.status for r in results] == ["veroeffentlicht", "veroeffentlicht"]
    assert store.get_draft(1)["status"] == "neu"
    assert store.get_draft(2)["status"] == "veroeffentlicht" and store.get_draft(2)["wp_link"].endswith("/freigegeben-eins/")
    post = wp.posts[0]
    assert post["status"] == "publish" and post["media_id"] == 41 and post["category_slug"] == "kino"
    assert post["meta"] == {"rank_math_title": "SEO", "rank_math_description": "Meta"}
    assert "<p>x</p>" in post["content"] and 'class="quelle"' in post["content"]
    assert publisher.publish_approved(settings, store, wp) == []  # nichts mehr offen


def test_publish_failure_marks_fehler_and_can_retry(env):
    settings, store = env
    seed(settings, store, "b", "Kaputt", "freigegeben")
    wp = FakeWP(fail_on="Kaputt")
    results = publisher.publish_approved(settings, store, wp)
    assert results[0].status == "fehler" and "500" in results[0].note
    assert store.get_draft(1)["status"] == "fehler" and "500" in store.get_draft(1)["fehler"]
    store.set_status(1, "erneut")
    assert publisher.publish_approved(settings, store, FakeWP())[0].status == "veroeffentlicht"


def test_publish_draft_as_wordpress_draft(env):
    settings, store = env
    draft_id = seed(settings, store, "d", "WP-Entwurf")
    row = store.claim_draft(draft_id, von="luis")
    info = publisher.publish_draft(row, settings, FakeWP(), store, status="draft")
    assert info["status"] == "draft" and "action=edit" in info["link"]
    assert store.get_draft(draft_id)["status"] == "in_wordpress"


class FakePlugin(publisher.TamilRadarClient):
    """Plugin-Client ohne HTTP: merkt sich Aufrufe, meldet auf Wunsch eine Dublette."""

    def __init__(self, duplikat=False):
        super().__init__("https://www.tamil.de", "ki-agent", "xxxx")
        self.created, self.updated, self.duplikat = [], [], duplikat

    def status(self):
        return {"plugin": "1.0.0"}

    def create(self, payload):
        self.created.append(payload)
        if self.duplikat:
            return {"duplikat": True, "id": 7, "link": "https://www.tamil.de/alt/", "edit_link": "https://www.tamil.de/wp-admin/post.php?post=7&action=edit"}
        return {"id": 200 + len(self.created), "status": payload["status"], "link": f"https://www.tamil.de/{payload['slug']}/",
                "edit_link": f"https://www.tamil.de/wp-admin/post.php?post={200 + len(self.created)}&action=edit"}

    def update(self, uid, payload):
        self.updated.append((uid, payload))
        return {"id": 7, "status": "publish", "link": "https://www.tamil.de/alt/", "edit_link": "https://www.tamil.de/wp-admin/post.php?post=7&action=edit"}


def test_publish_via_plugin_sends_everything_in_one_call(env):
    settings, store = env
    draft_id = seed(settings, store, "p1", "Plugin-Pfad", "freigegeben")
    store.update_draft(draft_id, typ="event", event_datum="2026-11-05", event_ort="Kinopark Aalen", ticket_url="https://t.de", relevanz=8, ort="Aalen")
    wp = FakePlugin()
    results = publisher.publish_approved(settings, store, wp)
    assert results[0].status == "veroeffentlicht" and store.get_draft(draft_id)["wp_link"] == "https://www.tamil.de/plugin-pfad/"
    payload = wp.created[0]
    assert payload["status"] == "publish" and payload["kategorie"] == "kino" and payload["schlagworte"] == ["Kino"]
    assert payload["seo"] == {"title": "SEO", "description": "Meta", "focus": "Kino"}
    assert payload["bild"]["dateiname"] == "p1.jpg" and payload["bild"]["credit"] == "Grafik: Tamil.de" and len(payload["bild"]["daten"]) > 1000
    meta = payload["meta"]
    assert meta["radar_uid"] == "p1" and meta["radar_relevanz"] == 8 and meta["event_datum"] == "2026-11-05"
    assert meta["event_ort"] == "Kinopark Aalen" and meta["ticket_url"] == "https://t.de" and meta["quelle_name"] == "Q"
    assert "kino_fakten" not in meta and 'class="quelle"' in payload["inhalt"]


def test_publish_via_plugin_duplicate_updates_kino_list(env):
    settings, store = env
    a = seed(settings, store, "k1", "Jailer 2 läuft in 23 Kinos", "freigegeben")
    store.update_draft(a, typ="kino_termine", fakten={"film": "Jailer 2", "woche": "2026-W43", "kinos": []})
    b = seed(settings, store, "a1", "Normaler Artikel", "freigegeben")
    wp = FakePlugin(duplikat=True)
    results = {r.title: r for r in publisher.publish_approved(settings, store, wp)}
    assert results["Jailer 2 läuft in 23 Kinos"].status == "veroeffentlicht" and results["Normaler Artikel"].status == "veroeffentlicht"
    assert len(wp.updated) == 1 and wp.updated[0][0] == "k1" and wp.updated[0][1]["meta"]["kino_fakten"]["woche"] == "2026-W43"
    assert store.get_draft(a)["wp_post_id"] == 7 and store.get_draft(b)["wp_post_id"] == 7
    assert [e["grund"] for e in store.iter_log(event="aktualisiert")] == ["Kinoliste"]


def test_seo_meta_variants(env):
    settings, _ = env
    row = {"seo_titel": "", "titel": "T", "meta_beschreibung": "", "teaser": "Tz"}
    settings.wp_seo_meta = "yoast"
    assert publisher.seo_meta(settings, row) == {"_yoast_wpseo_title": "T", "_yoast_wpseo_metadesc": "Tz"}
    settings.wp_seo_meta = "none"
    assert publisher.seo_meta(settings, row) is None


def test_timeout_after_successful_post_does_not_create_a_second_post(env):
    """WordPress legt den Beitrag an, die Antwort geht unterwegs verloren (Timeout). Der nächste Versuch bekommt 409
    (radar_uid existiert) und markiert den Entwurf als veröffentlicht – ohne zweiten Beitrag."""
    import requests

    from news_radar.wordpress import TamilRadarClient

    settings, store = env

    class Resp:
        def __init__(self, code, data):
            self.status_code, self._data, self.text = code, data, ""

        def json(self):
            return self._data

    class Session:
        def __init__(self):
            self.posts, self.headers, self.auth = {}, {}, None
            self.verloren = True

        def request(self, method, url, timeout=None, json=None, **kw):
            if method == "POST" and url.endswith("/beitrag"):
                uid = json["meta"]["radar_uid"]
                if uid in self.posts:
                    pid = self.posts[uid]
                    return Resp(409, {"code": "tamil_radar_duplicate", "data": {"status": 409, "id": pid,
                                                                                "link": f"https://www.tamil.de/p{pid}/"}})
                self.posts[uid] = 700 + len(self.posts)
                assert json["meta"]["radar_story_id"] == 42
                if self.verloren:
                    self.verloren = False
                    raise requests.Timeout("Antwort verloren")
                return Resp(201, {"id": self.posts[uid], "link": "x", "status": "publish"})
            raise AssertionError(url)

    session = Session()
    wp = TamilRadarClient("https://www.tamil.de", "u", "p", session=session)
    name, _ = save_pair(branded_card("Lichterfest", "Community", "s42"), settings.bilder_dir, "s42")
    draft_id = store.insert_draft(dict(uid="https://example.com/lichterfest", titel="Lichterfest in Hamm", teaser="T",
                                       inhalt_html="<p>Text</p>", kategorie="community", bild_datei=name, story_id=42))
    lizenz_setzen(store, draft_id, settings)
    store.set_status(draft_id, "freigeben")
    erste = publisher.publish_approved(settings, store, wp=wp)
    assert erste[0].status == "fehler" and store.get_draft(draft_id)["status"] == "fehler"
    store.set_status(draft_id, "erneut")
    zweite = publisher.publish_approved(settings, store, wp=wp)
    row = store.get_draft(draft_id)
    assert zweite[0].status == "veroeffentlicht" and row["status"] == "veroeffentlicht" and row["wp_post_id"] == 700
    assert len(session.posts) == 1
