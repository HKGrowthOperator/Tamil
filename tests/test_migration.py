"""Migration des Altbestands (tools/migration.py): Logik ohne Netz."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import migration  # noqa: E402

SITE = json.loads((Path(__file__).resolve().parent.parent / "prototyp" / "content" / "site.json").read_text(encoding="utf-8"))


def test_kategorien_abbildung():
    assert migration.map_kategorien(["news"]) == ("news", [], [])
    assert migration.map_kategorien(["blog"]) == ("community", [], [])
    assert migration.map_kategorien(["kritik"]) == ("kino", [], ["Kritik"])
    assert migration.map_kategorien(["anirudh"]) == ("events", [], ["Anirudh"])
    assert migration.map_kategorien(["turniere"]) == ("sport", [], [])
    # spezifische Rubrik vor news, news bleibt als weitere
    assert migration.map_kategorien(["news", "media"]) == ("kino", ["news"], [])
    # nur „test“: nicht übernehmen; Unbekanntes landet in news
    assert migration.map_kategorien(["test"]) == (None, [], [])
    assert migration.map_kategorien(["irgendwas"]) == ("news", [], [])


def test_alle_ziele_sind_neue_rubriken():
    from export_site import CATEGORY_MAP
    for neu, _ in CATEGORY_MAP.values():
        assert neu is None or neu in migration.NEUE_RUBRIKEN


def test_idempotenz_schluessel():
    assert migration.post_uid(9711) == "alt-9711"
    assert migration.post_uid(5, aus_seite=True) == "altseite-5"
    assert migration.idempotenz_pruefen([{"slug": "a"}, {"slug": "b"}, {"slug": "a"}]) == ["a"]


def test_beispielwerte_werden_entfernt_und_gemeldet():
    werte = migration.beispielwerte(SITE)
    assert "info@tamil.de" in werte and len(werte) == 3
    html = "<p>Tel. +49 69 123 456, Mail info@tamil.de, Hallo</p><p>WhatsApp +491701234567</p>"
    sauber, gefunden = migration.strip_beispielwerte(html, werte)
    assert "123 456" not in sauber and "info@tamil.de" not in sauber and "1701234567" not in sauber
    assert "Hallo" in sauber and len(gefunden) == 3
    assert migration.strip_beispielwerte("<p>nichts</p>", werte) == ("<p>nichts</p>", [])


def test_bildadressen_umschreiben():
    alt = "https://www.tamil.de/wp-content/uploads/2024/11/kanguva-300x200.jpg"
    html = (f'<p><a href="{alt}"><img src="{alt}" srcset="{alt} 300w, x 600w" sizes="(max-width:300px) 100vw" alt="Plakat"></a>'
            '<a href="https://www.tamil.de/anderer-beitrag/">mehr</a> <a href="http://tamil.de">Start</a></p>')
    assert migration.upload_urls(html) == [alt]
    neu = migration.rewrite_html(html, {alt: "https://neu.example/wp-content/uploads/2026/11/kanguva-300x200.jpg"})
    assert "tamil.de/wp-content" not in neu and neu.count("neu.example") == 2
    assert "srcset" not in neu and "sizes" not in neu and 'alt="Plakat"' in neu
    assert 'href="/anderer-beitrag/"' in neu and 'href="/"' in neu


def test_http_variante_und_youtube():
    alt = "https://www.tamil.de/wp-content/uploads/2020/01/a.jpg"
    neu = migration.rewrite_html('<img src="http://www.tamil.de/wp-content/uploads/2020/01/a.jpg">', {alt: "https://n/a.jpg"})
    assert 'src="https://n/a.jpg"' in neu
    yt = '<iframe loading="lazy" width="630" src="https://www.youtube.com/embed/YP4PBOfhaN8?feature=oembed" allowfullscreen></iframe>'
    out = migration.rewrite_html(yt, {})
    assert "<iframe" not in out and "https://www.youtube.com/watch?v=YP4PBOfhaN8" in out


def test_fremde_bilder():
    html = '<img src="http://www.tamil.de/wp-content/uploads/a.jpg"><img src="https://static.giga.de/x.jpg"><img src="/rel.jpg">'
    assert migration.fremde_bilder(html) == ["https://static.giga.de/x.jpg"]


def test_redirect_csv_und_seitenplan():
    cats = [{"slug": "blog", "count": 21}, {"slug": "news", "count": 3}]
    pages = [{"slug": "ueberuns", "link": "https://www.tamil.de/ueberuns/"}, {"slug": "login", "link": "https://www.tamil.de/login/"}]
    csv_text = migration.redirect_csv("https://www.tamil.de", cats, pages, [("https://www.tamil.de/a/", "https://www.tamil.de/b/")])
    zeilen = csv_text.splitlines()
    assert zeilen[0] == "alt,neu"
    assert "/category/blog/,/category/community/" in zeilen
    assert "/ueberuns/,/ueber-uns/" in zeilen
    assert "/a/,/b/" in zeilen
    plan = migration.seiten_plan(pages + [{"slug": "maya"}, {"slug": "kino"}])
    assert [p["slug"] for p in plan["seite"]] == ["ueberuns"] and [p["slug"] for p in plan["loeschen"]] == ["login"]
    assert [p["slug"] for p in plan["beitrag"]] == ["maya"] and [p["slug"] for p in plan["redirect"]] == ["kino"]


def test_text_entities():
    assert migration.text("Kanguva &#8211; <b>Highlight</b>\n  jetzt") == "Kanguva – Highlight jetzt"


def test_medien_slug_stabil_und_eindeutig():
    a = migration.media_slug("https://www.tamil.de/wp-content/uploads/2019/11/image.gif")
    assert a == migration.media_slug("http://tamil.de/wp-content/uploads/2019/11/image.gif")  # Schema/Host egal
    assert a != migration.media_slug("https://www.tamil.de/wp-content/uploads/2020/01/image.gif")  # gleicher Name, anderer Monat
    assert a.startswith("alt-image-")
