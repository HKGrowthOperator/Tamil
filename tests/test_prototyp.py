"""Prototyp-Build: Bereinigung alter WordPress-Beiträge, Auswahl ohne Dubletten, Rezept-Zerlegung, Kalender."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "prototyp"))

import build  # noqa: E402

SHARE = "<div class='share-to-whatsapp-wrapper'><div class='share-on-whsp'>Share on: </div><a class='whatsapp-share'>WhatsApp</a><div class='clear '></div></div>"
YT = ('<figure class="wp-block-embed is-type-video"><div class="wp-block-embed__wrapper">'
      '<iframe loading="lazy" title="Trailer" width="630" height="354" src="https://www.youtube.com/embed/FW_PPcr1sPE?feature=oembed" allowfullscreen></iframe>'
      '</div></figure>')


def test_clean_body_removes_widget_dead_images_and_attributes():
    raw = ('<p style="color:red" data-mce-style="x">Hallo <strong>Welt</strong></p>'
           '<p><a href="http://static.example/a.jpg" rel="fancybox"><br /><img src="http://static.example/a.jpg" srcset="x 1w" /></a></p>'
           '<h1 class="wp-block-heading">Kopf</h1><h4>Klein</h4><p>&nbsp;</p>'
           '<p><a href="https://www.tamil.de/wp-content/uploads/2024/10/b.jpeg"><img decoding="async" src="https://www.tamil.de/wp-content/uploads/2024/10/b.jpeg" alt="" width="864" height="774" class="wp-image-1" srcset="a 1w"></a></p>'
           '<script>alert(1)</script>' + YT + SHARE)
    out = build.clean_body(raw)
    assert "share-to-whatsapp" not in out and "WhatsApp" not in out
    assert "http://" not in out and "srcset" not in out and "style=" not in out and "data-mce" not in out
    assert "<script" not in out and "<iframe" not in out
    assert '<div class="video-embed" data-video="FW_PPcr1sPE">' in out and "Video laden" in out
    assert "<h2>Kopf</h2>" in out and "<h3>Klein</h3>" in out and "<h1" not in out
    assert '<figure><img src="https://www.tamil.de/wp-content/uploads/2024/10/b.jpeg" alt="" width="864" height="774"></figure>' in out
    assert "<p></p>" not in out and "&nbsp;</p>" not in out
    assert build.inline_images(out) == ["https://www.tamil.de/wp-content/uploads/2024/10/b.jpeg"]


def test_localize_images_rewrites_or_drops():
    body = '<p>a</p><figure><img src="https://x/1.jpg" alt=""></figure><figure><img src="https://x/2.jpg" alt=""></figure>'
    out = build.localize_images(body, {"https://x/1.jpg": "img/p1-1.jpg", "https://x/2.jpg": None})
    assert 'src="img/p1-1.jpg"' in out and "2.jpg" not in out and out.count("<figure>") == 1


def test_split_recipe_two_sections():
    body = ("<p><b>Kottu Roti</b> ist ein Gericht.</p><p><strong>Zutaten:</strong></p><ul><li>500gr Mehl</li><li>Salz</li></ul>"
            "<h3>Zubereitung:</h3><p>Kneten.</p><p>Backen.</p><h3>Essensvorschlag:</h3><p>Mit Curry.</p>"
            "<h3>Kothu Rotti (gehackt)</h3><p>Für 4 Personen:</p><h3>Zutaten:</h3><ul><li>6 Rotti</li></ul><h3>Zubereitung:</h3><p>Schneiden.</p>")
    r = build.split_recipe(body)
    assert "Gericht" in r["intro"]
    assert [s["titel"] for s in r["abschnitte"]] == ["Grundrezept", "Kothu Rotti (gehackt)"]
    assert r["abschnitte"][0]["zutaten"] == ["500gr Mehl", "Salz"] and r["abschnitte"][0]["schritte"] == ["Kneten.", "Backen."]
    assert r["abschnitte"][0]["tipp"] == ["Mit Curry."]
    assert r["abschnitte"][1]["zutaten"] == ["6 Rotti"] and r["abschnitte"][1]["schritte"] == ["Schneiden."]


def _post(i, kat, datum, woerter=200, w=1200, titel=None):
    return {"id": i, "slug": f"p{i}", "titel": titel or f"Titel {i}", "datum": datum, "kategorien": [kat], "alt_kategorien": [], "excerpt": "",
            "woerter": woerter, "bild": {"orig_w": w, "src": f"img/p{i}.jpg"}, "tags": [], "chips": []}


def test_select_without_duplicates_and_kultur_fallback():
    site = build.load_site()
    posts = [_post(i, "news", f"2026-09-{i:02d}") for i in range(1, 15)] + [_post(20, "kino", "2026-09-20"), _post(21, "kino", "2026-09-21", woerter=40)]
    posts.append(_post(30, "news", "2026-09-25", titel="Pongal-Fest in Hamburg"))
    site = dict(site, hero=[14, 13, 12], top_themen=[1, 2], rezept={"id": 999})
    sel = build.select(posts, site)
    assert [p["id"] for p in sel["hero"]] == [14, 13, 12]
    assert sel["neueste"][0]["id"] == 30 and 14 not in {p["id"] for p in sel["neueste"]}
    home_ids = [p["id"] for p in sel["hero"] + sel["neueste"]] + [p["id"] for lst in sel["rubriken"].values() for p in lst]
    assert len(home_ids) == len(set(home_ids))
    assert 21 not in {p["id"] for p in sel["kategorie_seiten"]["kino"]}  # zu kurz
    assert sel["kategorie_seiten"]["kultur"][0]["id"] == 30 and sel["kategorie_seiten"]["kultur"][0]["kultur_fallback"]
    assert sel["rubriken"]["kultur"] == [] and sel["rubriken"]["sport"] == []  # 30 ist schon unter Neueste verbraucht
    assert 30 not in {p["id"] for p in sel["rubriken"]["news"]}
    assert 1 in build.used_ids(sel) and 21 not in build.used_ids(sel)


def test_pick_image_priority_and_helpers():
    media = {"source_url": "https://x/full.png", "media_details": {"width": 1648, "height": 700, "sizes": {
        "medium_large": {"source_url": "https://x/768.png", "width": 768, "height": 326}, "slider-img": {"source_url": "https://x/692.png", "width": 692, "height": 360}}}}
    assert build.pick_image(media) == ("https://x/768.png", 1648, 700)
    assert build.pick_image({"source_url": "https://x/only.png"}) == ("https://x/only.png", 0, 0)
    assert build.reading_time(488) == 3 and build.reading_time(10) == 1
    assert build.excerpt("<p>" + "wort " * 60 + "[&hellip;]</p>", 40).endswith(" …") and len(build.excerpt("kurz", 40)) == 4
    assert build.kino_chips({"titel": "Kanguva – Kino-Highlight ab 14. November", "alt_kategorien": ["kritik"]}) == ["kritik", "kinostart"]
    assert build.fmt_date("2026-10-16", weekday=True) == "Freitag, 16. Oktober 2026"
    assert build.fix_caps("KOLAMAAVU KOKILA – KRITIK") == "Kolamaavu Kokila – Kritik" and build.fix_caps("Konzert in NRW: ANIRUDH live") == "Konzert in NRW: Anirudh live"
    assert build.fmt_range("2026-10-15", "2026-10-22") == "15.–22. Oktober 2026"


def test_month_grid_and_event_months():
    events = [{"von": "2026-10-16", "bis": "2026-10-19", "titel": "A"}, {"von": "2026-10-31", "titel": "B"}, {"von": "2026-11-05", "titel": "C"}]
    grid = build.month_grid(2026, 10, events)
    assert grid["weeks"][0][:3] == [None, None, None] and grid["weeks"][0][3]["day"] == 1  # Oktober 2026 beginnt am Donnerstag
    day17 = next(c for w in grid["weeks"] for c in w if c and c["day"] == 17)
    assert [e["titel"] for e in day17["events"]] == ["A"] and day17["weekend"]
    assert [m["label"] for m in build.event_months(events)] == ["Oktober 2026", "November 2026"]


def test_build_renders_all_pages(tmp_path):
    written = build.build(tmp_path)
    assert "index.html" in written and "kategorie-sport.html" in written and "kontakt.html" in written and "design-system.html" in written
    index = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "Jailer 2" in index and "Rezept der Woche" in index and 'href="kategorie-kino.html"' in index
    assert build.check_links(tmp_path) == []
    for page in ("production.html", "tv.html", "impressum.html", "datenschutz.html", "ueber-uns.html", "service-fsk.html"):
        assert page in written, page
    assert 'src="img/logo.png"' in index and 'href="https://www.gravity-club.de' in index and "Tamil.de Production" in index
    kueche = (tmp_path / "kategorie-kueche.html").read_text(encoding="utf-8")
    assert kueche.count('<article class="card') >= 5 and "Bundesgericht" not in kueche
    tv = (tmp_path / "tv.html").read_text(encoding="utf-8")
    assert "Santhora TV" in tv and "Stream wird angefragt" in tv
    assert "Leser-Reporter" in (tmp_path / "kontakt.html").read_text(encoding="utf-8")
    bare = build.render_all(tmp_path / "bare", bare_index=True)
    text = (tmp_path / "bare" / "index.html").read_text(encoding="utf-8")
    assert not text.lstrip().startswith("<!doctype") and "<title>" in text and 'claude:viewport-fit-sides' in text
    assert (tmp_path / "bare" / "kontakt.html").read_text(encoding="utf-8").lstrip().startswith("<!doctype html>")
