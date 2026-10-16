import pytest

from news_radar import publisher
from news_radar.config import load_settings
from news_radar.images import branded_card, save_pair
from news_radar.store import Store


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


def test_seo_meta_variants(env):
    settings, _ = env
    row = {"seo_titel": "", "titel": "T", "meta_beschreibung": "", "teaser": "Tz"}
    settings.wp_seo_meta = "yoast"
    assert publisher.seo_meta(settings, row) == {"_yoast_wpseo_title": "T", "_yoast_wpseo_metadesc": "Tz"}
    settings.wp_seo_meta = "none"
    assert publisher.seo_meta(settings, row) is None
