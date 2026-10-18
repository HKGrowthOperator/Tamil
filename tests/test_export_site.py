import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import export_site  # noqa: E402


class FakeResp:
    def __init__(self, data, headers=None, content=b""):
        self._data, self.headers, self.content = data, headers or {}, content

    def json(self):
        return self._data

    def raise_for_status(self):
        pass


class FakeSession:
    """Zwei Seiten Beiträge, je eine Seite Rest; Medien-Downloads liefern Bytes."""

    def __init__(self):
        self.calls = []
        self.headers = {}

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, params))
        if url.endswith("/posts"):
            page = (params or {}).get("page", 1)
            if (params or {}).get("per_page") == 1:
                return FakeResp([{"id": 1}], {"X-WP-Total": "3"})
            data = {1: [post(1, "<p>Lang " + "wort " * 100 + '</p><img src="http://bild.de/a.jpg">', [2]), post(2, "<p>kurz</p>", [1, 9])],
                    2: [post(3, '<iframe src="https://www.youtube.com/embed/x"></iframe><p>' + "x " * 90 + "</p>", [5])]}[page]
            return FakeResp(data, {"X-WP-TotalPages": "2"})
        if url.endswith("/pages"):
            return FakeResp([{"id": 10, "slug": "backup", "link": "https://www.tamil.de/backup/"}, {"id": 11, "slug": "impressum", "link": "https://www.tamil.de/impressum/"}], {"X-WP-TotalPages": "1"})
        if url.endswith("/categories"):
            return FakeResp([{"id": 2, "slug": "news", "name": "News", "count": 312}, {"id": 1, "slug": "test", "name": "Test", "count": 3},
                             {"id": 9, "slug": "media", "name": "Media", "count": 84}, {"id": 5, "slug": "anirudh", "name": "Anirudh", "count": 6}], {"X-WP-TotalPages": "1"})
        if url.endswith("/tags"):
            return FakeResp([{"id": 7, "name": "Kino", "slug": "kino", "count": 1}], {"X-WP-TotalPages": "1"})
        if url.endswith("/media"):
            return FakeResp([{"id": 100, "source_url": "https://www.tamil.de/wp-content/uploads/2024/11/kanguva.jpg"},
                             {"id": 101, "source_url": "https://www.tamil.de/wp-content/uploads/2016/03/a.png"}], {"X-WP-TotalPages": "1"})
        return FakeResp(None, content=b"bytes")


def post(pid, content, cats):
    return {"id": pid, "date": "2024-11-06T13:36:33", "slug": f"p{pid}", "link": f"https://www.tamil.de/p{pid}/", "title": {"rendered": f"Titel {pid}"},
            "content": {"rendered": content}, "featured_media": 100 if pid == 1 else 0, "categories": cats, "tags": [7]}


def test_paging_stops_at_total_pages():
    s = FakeSession()
    items = list(export_site.paged(s, "https://x/wp-json/wp/v2/posts", pause=0))
    assert [i["id"] for i in items] == [1, 2, 3]
    assert [c[1]["page"] for c in s.calls] == [1, 2]


def test_export_writes_inventory_redirects_and_media(tmp_path):
    report = export_site.export("https://www.tamil.de", tmp_path, with_media=True, workers=2, session=FakeSession())
    assert report["posts"] == 3 and report["posts_total_laut_api"] == 3 and report["media_geladen"] == 2
    assert (tmp_path / "media" / "2024" / "11" / "kanguva.jpg").read_bytes() == b"bytes"
    rows = list(csv.DictReader((tmp_path / "inventory.csv").open(encoding="utf-8")))
    by_id = {r["id"]: r for r in rows}
    assert by_id["1"]["http_bilder"] == "1" and by_id["1"]["empfehlung"] == "prüfen" and by_id["1"]["beitragsbild"] == "ja"
    assert by_id["2"]["kategorien"] == "test|media" and by_id["2"]["empfehlung"] == "löschen" and by_id["2"]["neue_kategorie"] == "kino"
    assert by_id["3"]["youtube"] == "1" and by_id["3"]["neue_kategorie"] == "events" and by_id["3"]["empfehlung"] == "übernehmen"
    redirects = list(csv.DictReader((tmp_path / "redirects.csv").open(encoding="utf-8")))
    alt_neu = {r["alt"]: r["neu"] for r in redirects}
    assert alt_neu["https://www.tamil.de/category/test/"] == "https://www.tamil.de/"
    assert alt_neu["https://www.tamil.de/category/anirudh/"] == "https://www.tamil.de/events/"
    assert alt_neu["https://www.tamil.de/backup/"] == "https://www.tamil.de/"
    assert "https://www.tamil.de/impressum/" not in alt_neu
    assert json.loads((tmp_path / "report.json").read_text())["inventar"]["http_bilder_posts"] == 1


HOME = (Path(__file__).parent / "fixtures" / "tamil_home.html").read_text(encoding="utf-8")


def test_parse_homepage_structure_and_brand():
    menus = export_site.parse_menus(HOME)
    assert [m["label"] for m in menus["haupt"]] == ["Home", "News", "EVENTS", "KINO"] and menus["haupt"][2]["url"].endswith("/category/anirudh/")
    assert [m["label"] for m in menus["top"]] == ["Über Tamil.de", "Impressum"]
    assert [t["label"] for t in export_site.parse_ticker(HOME)] == ["BAW erhebt Anklage gegen Tamilen", "Sie übersetzt auch im Gebärsaal"]
    ads = export_site.parse_ads(HOME)
    assert ads == [{"platz": "header", "url": "https://www.gravity-club.de", "bild": "https://www.tamil.de/wp-content/uploads/2024/10/topbanner.jpg", "masse": "728 × 90"},
                   {"platz": "sidebar", "url": "https://www.olyyn.com", "bild": "https://www.tamil.de/wp-content/uploads/2026/07/33633363663.jpg", "masse": "336 × 280"}]
    assert export_site.parse_blocks(HOME) == ["KÜCHE", "POWERED BY TAMIL.DE Production"]
    assert export_site.parse_social(HOME) == ["https://whatsapp.com/channel/0029VaFIN43KWEKo3BGoE13t", "https://www.instagram.com/tamil_de/"]
    brand = export_site.parse_brand(HOME)
    assert brand["logo"].endswith("kkbslogo.png") and brand["theme"] == ["Observer"] and "add-to-any" in brand["plugins"]
    assert brand["farben"][0] == "#B52224" and brand["generator"] == "WordPress 6.2.14" and "Ubuntu" in brand["fonts"]


def test_page_map_redirects():
    site = "https://www.tamil.de"
    pages = [{"slug": s, "link": f"{site}/{s}/"} for s in ("ueberuns", "maya", "kino", "members", "privacy-policy", "tv", "reporter")]
    rows = {r["alt"]: r["neu"] for r in export_site.redirect_rows(site, [], pages)}
    assert rows[f"{site}/ueberuns/"] == f"{site}/ueber-uns/" and rows[f"{site}/reporter/"] == f"{site}/kontakt/"
    assert f"{site}/maya/" not in rows  # bleibt unter demselben Pfad, wird Beitrag
    assert rows[f"{site}/members/"] == f"{site}/" and rows[f"{site}/privacy-policy/"] == f"{site}/"
    assert f"{site}/tv/" not in rows and f"{site}/kino/" not in rows


def test_category_redirects_target_wordpress_category_base():
    site = "https://www.tamil.de"
    cats = [{"slug": "blog", "count": 3}, {"slug": "news", "count": 9}, {"slug": "test", "count": 1}]
    rows = {r["alt"]: r["neu"] for r in export_site.redirect_rows(site, cats, [])}
    assert rows[f"{site}/category/blog/"] == f"{site}/category/community/"
    assert f"{site}/category/news/" not in rows  # gleicher Slug, keine Weiterleitung
    assert rows[f"{site}/category/test/"] == f"{site}/"
