"""Plugin tamil-site: Angaben für Suchmaschinen und soziale Netze (Beschreibung, OpenGraph, Twitter, JSON-LD, noindex)
und die SEO-Felder, die der Radar über tamil-radar schreibt."""

import base64
import html
import io
import json
import re
import uuid

import pytest
import requests
from PIL import Image
from wp_umgebung import PW, URL, USER

from news_radar.wordpress import TamilRadarClient


def _meta(seite: str, attr: str, name: str) -> list[str]:
    werte = []
    for tag in re.findall(r"<meta\s[^>]*>", seite):
        if re.search(rf'{attr}=["\']{re.escape(name)}["\']', tag):
            m = re.search(r'content=(["\'])(.*?)\1', tag)
            werte.append(html.unescape(m.group(2)) if m else "")
    return werte


def _jsonld(seite: str) -> list[dict]:
    bloecke = re.findall(r'<script type="application/ld\+json">(.*?)</script>', seite, re.DOTALL)
    daten = [json.loads(b) for b in bloecke]  # ungültiges JSON lässt den Test scheitern
    flach = []
    for d in daten:
        flach.extend(d.get("@graph", [d]) if isinstance(d, dict) else d)
    return flach


def _typen(seite: str) -> list[str]:
    return [d.get("@type") for d in _jsonld(seite)]


def _png() -> str:
    buf = io.BytesIO()
    Image.new("RGB", (1600, 1000), (30, 60, 90)).save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


@pytest.fixture
def radar_beitrag(wp, wp_admin):
    """Ein veröffentlichter Beitrag über den Radar-Weg, mit SEO-Feldern und Beitragsbild."""
    c = TamilRadarClient(URL, USER, PW)
    uid = f"seo-{uuid.uuid4().hex[:10]}"
    post = c.create({
        "titel": "Radar-Beitrag für SEO", "inhalt": "<p>Langer Text des Beitrags. " + "Wort " * 80 + "</p>",
        "teaser": "Teaser des Beitrags", "status": "publish", "slug": f"seo-test-{uid}", "kategorie": "kino",
        "schlagworte": ["Kino"], "meta": {"radar_uid": uid},
        "seo": {"title": "SEO-Titel vom Radar", "description": "Beschreibung vom Radar für die Suche.", "focus": "Kino Hamm"},
        "bild": {"daten": _png(), "dateiname": f"{uid}.png", "alt": "Bild-Alt", "credit": "Grafik: Test"},
    })
    yield post
    requests.delete(f"{URL}/wp-json/wp/v2/posts/{post['id']}", params={"force": "true"}, auth=wp_admin, timeout=30)


@pytest.fixture
def event_beitrag(wp_cli):
    pid = int(wp_cli(
        "echo wp_insert_post( array( 'post_title' => 'Konzert in Essen', 'post_status' => 'publish', 'post_name' => 'seo-test-konzert', "
        "'post_content' => '<p>Inhalt</p>', 'meta_input' => array( 'standfirst' => 'Vorspann zum Konzert.', 'event_datum' => '2031-05-01', "
        "'event_ort' => 'Grugahalle' ) ) );"))
    yield pid
    wp_cli(f"wp_delete_post( {pid}, true );")


def test_radar_beitrag_beschreibung_og_twitter_und_artikel_schema(wp, wp_cli, radar_beitrag):
    seite = wp.get(f"/seo-test-{radar_beitrag['radar_uid']}/").text
    assert _meta(seite, "name", "description") == ["Beschreibung vom Radar für die Suche."]
    assert "<title>SEO-Titel vom Radar" in seite
    assert _meta(seite, "property", "og:title") == ["SEO-Titel vom Radar"]
    assert _meta(seite, "property", "og:type") == ["article"]
    assert _meta(seite, "property", "og:description") == ["Beschreibung vom Radar für die Suche."]
    bild = _meta(seite, "property", "og:image")
    assert len(bild) == 1 and bild[0].startswith(URL + "/wp-content/uploads/") and "1200x630" in bild[0]
    assert _meta(seite, "property", "og:image:width") == ["1200"] and _meta(seite, "property", "og:image:height") == ["630"]
    assert _meta(seite, "name", "twitter:card") == ["summary_large_image"]
    artikel = [d for d in _jsonld(seite) if d.get("@type") == "NewsArticle"]
    assert len(artikel) == 1
    a = artikel[0]
    assert a["headline"] == "Radar-Beitrag für SEO" and a["description"] == "Beschreibung vom Radar für die Suche."
    assert a["mainEntityOfPage"].endswith(f"/seo-test-{radar_beitrag['radar_uid']}/") and a["image"]
    assert a["datePublished"] and a["publisher"]["@type"] == "Organization"
    krumen = [d for d in _jsonld(seite) if d.get("@type") == "BreadcrumbList"]
    assert len(krumen) == 1 and [e["position"] for e in krumen[0]["itemListElement"]] == [1, 2, 3]
    assert krumen[0]["itemListElement"][1]["name"] == "Kino"
    felder = json.loads(wp_cli(
        f"echo wp_json_encode( array_map( function ( $k ) {{ return get_post_meta( {radar_beitrag['id']}, $k, true ); }}, "
        "array( '_tamil_seo_title', '_tamil_seo_description', '_tamil_seo_focus' ) ) );"))
    assert felder == ["SEO-Titel vom Radar", "Beschreibung vom Radar für die Suche.", "Kino Hamm"]


def test_vorspann_als_beschreibung_und_kein_doppeltes_event(wp, event_beitrag):
    seite = wp.get("/seo-test-konzert/").text
    assert _meta(seite, "name", "description") == ["Vorspann zum Konzert."]
    typen = _typen(seite)
    assert typen.count("Event") == 1 and typen.count("NewsArticle") == 1


def test_auszug_gekuerzt(wp, wp_cli):
    pid = int(wp_cli(
        "echo wp_insert_post( array( 'post_title' => 'Ohne Vorspann', 'post_status' => 'publish', 'post_name' => 'seo-test-auszug', "
        "'post_content' => '<p>' . str_repeat( 'Satz mit mehreren Wörtern. ', 40 ) . '</p>' ) );"))
    try:
        beschreibung = _meta(wp.get("/seo-test-auszug/").text, "name", "description")
        assert len(beschreibung) == 1 and 50 < len(beschreibung[0]) <= 160 and beschreibung[0].startswith("Satz mit")
    finally:
        wp_cli(f"wp_delete_post( {pid}, true );")


def test_startseite_website_mit_suche(wp):
    seite = wp.get("/").text
    website = [d for d in _jsonld(seite) if d.get("@type") == "WebSite"]
    assert len(website) == 1 and website[0]["potentialAction"]["@type"] == "SearchAction"
    assert "{search_term_string}" in website[0]["potentialAction"]["target"]["urlTemplate"]
    assert _meta(seite, "property", "og:type") == ["website"]
    assert len(_meta(seite, "name", "description")) == 1
    assert "NewsArticle" not in _typen(seite)


def test_suche_noindex(wp):
    seite = wp.get("/?s=kino").text
    robots = _meta(seite, "name", "robots")
    assert robots and "noindex" in robots[0]


def test_suche_noindex_auch_in_production(wp_cli):
    code = ("add_filter( 'tamil_site_indexierbar', '__return_true' ); add_filter( 'tamil_site_nicht_indexieren', '__return_true' );"
            "echo wp_json_encode( apply_filters( 'wp_robots', array() ) );")
    assert json.loads(wp_cli(code)).get("noindex") is True


def test_kein_doppel_mit_seo_plugin(wp_cli):
    out = wp_cli("echo tamil_site_seo_aktiv() ? 'an' : 'aus'; define( 'WPSEO_VERSION', '99' ); echo ' ', tamil_site_seo_aktiv() ? 'an' : 'aus';")
    assert out.strip() == "an aus"


def test_bildgroesse_registriert(wp_cli):
    assert json.loads(wp_cli("echo wp_json_encode( wp_get_registered_image_subsizes()['tamil-og'] ?? null );")) == {
        "width": 1200, "height": 630, "crop": True}


# --- Testsystem nicht indexieren: jede Umgebung außer production -------------------------------------------------


def test_testsystem_noindex_ueberall(wp):
    for pfad in ("/", "/category/kino/", "/?s=kino"):
        r = wp.get(pfad)
        robots = _meta(r.text, "name", "robots")
        assert robots and "noindex" in robots[0] and "nofollow" in robots[0], (pfad, robots)
        assert r.headers.get("X-Robots-Tag", "").replace(" ", "") == "noindex,nofollow", pfad
    # OpenGraph und JSON-LD bleiben
    assert _meta(wp.get("/").text, "property", "og:title") and "WebSite" in _typen(wp.get("/").text)


def test_testsystem_robots_txt_und_keine_sitemap(wp):
    r = wp.get("/robots.txt")
    assert r.status_code == 200
    zeilen = [z.strip() for z in r.text.splitlines() if z.strip()]
    assert "Disallow: /" in zeilen and not any(z.lower().startswith("sitemap:") for z in zeilen)
    assert r.headers.get("X-Robots-Tag", "").replace(" ", "") == "noindex,nofollow"
    assert wp.get("/wp-sitemap.xml").status_code == 404


def test_production_bleibt_indexierbar(wp_cli):
    code = ("echo wp_json_encode( array( tamil_site_indexierbar( 'production' ), tamil_site_indexierbar( 'staging' ),"
            " tamil_site_indexierbar( 'local' ), tamil_site_indexierbar( 'development' ) ) );")
    assert wp_cli(code).strip() == "[true,false,false,false]"
    # mit production (Filter): Robots ohne noindex, robots.txt und Sitemap wie von WordPress
    code = ("add_filter( 'tamil_site_indexierbar', '__return_true' );"
            "echo wp_json_encode( array( apply_filters( 'wp_robots', array() ), apply_filters( 'robots_txt', 'X', true ),"
            " apply_filters( 'wp_sitemaps_enabled', true ), tamil_site_robots_kopfzeile() ) );")
    robots, txt, sitemap, kopf = json.loads(wp_cli(code))
    assert "noindex" not in (robots or {}) and "Disallow: /\n" not in txt and txt.startswith("X") and sitemap is True and kopf == ""
