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
    assert a["datePublished"] and a["publisher"]["@type"] == "NewsMediaOrganization"
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


# --- Geschützte und nicht öffentliche Beiträge, Titel aus dem Radar ------------------------------------------------


def test_geschuetzter_beitrag_ohne_beschreibung_bild_und_schema(wp, wp_cli):
    pid = int(wp_cli(
        "$a = wp_insert_attachment( array( 'post_title' => 'geheim-bild', 'post_mime_type' => 'image/png', 'post_status' => 'inherit' ), false );"
        "$p = wp_insert_post( array( 'post_title' => 'Geschützt SEO', 'post_status' => 'publish', 'post_name' => 'seo-test-geschuetzt',"
        " 'post_password' => 'geheim', 'post_content' => '<p>Geheimer Inhalt.</p>', 'meta_input' => array( 'standfirst' => 'Geheimer Vorspann',"
        " '_tamil_seo_description' => 'Geheime Beschreibung' ) ) ); set_post_thumbnail( $p, $a ); echo $p;"))
    try:
        seite = wp.get("/seo-test-geschuetzt/").text
        kopf = seite.split("</head>")[0]
        assert "Geheime Beschreibung" not in kopf and "Geheimer Vorspann" not in kopf
        assert _meta(seite, "name", "description") == [] and _meta(seite, "property", "og:description") == []
        assert "geheim-bild" not in " ".join(_meta(seite, "property", "og:image"))
        assert "NewsArticle" not in _typen(seite)
        # Entwürfe und private Beiträge: keine Beschreibung, kein Artikel
        code = (f"wp_update_post( array( 'ID' => {pid}, 'post_password' => '', 'post_status' => 'draft' ) );"
                f"$a = tamil_site_seo_beschreibung_beitrag( {pid} );"
                f"wp_update_post( array( 'ID' => {pid}, 'post_status' => 'private' ) );"
                f"echo wp_json_encode( array( $a, tamil_site_seo_beschreibung_beitrag( {pid} ), tamil_site_seo_oeffentlich( get_post( {pid} ) ) ) );")
        assert json.loads(wp_cli(code)) == ["", "", False]
    finally:
        wp_cli(f"$t = get_post_thumbnail_id( {pid} ); wp_delete_post( {pid}, true ); if ( $t ) {{ wp_delete_attachment( $t, true ); }}")


def test_seo_titel_wird_escaped(wp, wp_cli):
    pid = int(wp_cli(
        "echo wp_insert_post( array( 'post_title' => 'Titeltest', 'post_status' => 'publish', 'post_name' => 'seo-test-titel',"
        " 'post_content' => '<p>x</p>' ) );"))
    try:
        wp_cli(f"update_post_meta( {pid}, '_tamil_seo_title', '</title><script>alert(1)</script>' );")
        seite = wp.get("/seo-test-titel/").text
        assert "<script>alert(1)</script>" not in seite
        titel = re.search(r"<title>(.*?)</title>", seite, re.DOTALL).group(1)
        assert "<" not in titel and "alert(1)" in html.unescape(titel)
    finally:
        wp_cli(f"wp_delete_post( {pid}, true );")


# --- Prüfung 12.11.2026 (claude-seo, Abgleich mit Merzenich Aktuell): Autor, Herausgeber, Canonical, dünne Seiten ----


@pytest.fixture
def admin_beitraege(wp_cli):
    """Zwei Beiträge des Admins (wie der übernommene Altbestand, der unter einem Benutzer läuft) mit einem Schlagwort,
    das nur einmal vorkommt, und eines, das dreimal vorkommt."""
    ids = json.loads(wp_cli(
        "$ids = array(); foreach ( array( 1, 2, 3 ) as $n ) { $ids[] = wp_insert_post( array( 'post_title' => \"SEO Altbestand $n\","
        " 'post_status' => 'publish', 'post_author' => 1, 'post_name' => \"seo-test-alt-$n\", 'post_content' => '<p>Text</p>',"
        " 'tags_input' => 1 === $n ? array( 'seo-einzeln', 'seo-dreimal' ) : array( 'seo-dreimal' ) ) ); }"
        " echo wp_json_encode( $ids );"))
    yield ids
    wp_cli("foreach ( " + json.dumps(ids).replace("[", "array(").replace("]", ")") + " as $i ) { wp_delete_post( $i, true ); }"
           " foreach ( array( 'seo-einzeln', 'seo-dreimal' ) as $s ) { $t = get_term_by( 'slug', $s, 'post_tag' );"
           " if ( $t ) { wp_delete_term( $t->term_id, 'post_tag' ); } }")


def test_autor_im_schema_wie_die_autorenzeile(wp, admin_beitraege):
    seite = wp.get("/seo-test-alt-1/").text
    autor = [d for d in _jsonld(seite) if d.get("@type") == "NewsArticle"][0]["author"]
    # sichtbar steht „Redaktion Tamil.de“ (Customizer autor_name); nie ein Anmeldename
    assert autor["name"] == "Redaktion Tamil.de" and autor["@type"] == "Organization"
    assert "<strong>Redaktion Tamil.de</strong>" in seite
    assert '"name":"admin"' not in seite


def test_feed_ohne_anmeldenamen(wp, admin_beitraege):
    feed = wp.get("/feed/").text
    autoren = set(re.findall(r"<dc:creator><!\[CDATA\[(.*?)\]\]></dc:creator>", feed))
    assert autoren == {"Redaktion Tamil.de"}


def test_benutzerliste_nur_fuer_angemeldete(wp, wp_admin, admin_beitraege):
    for pfad in ("/wp-json/wp/v2/users", "/wp-json/wp/v2/users/1"):
        r = wp.get(pfad)
        assert r.status_code == 401 and "admin" not in r.text, pfad
    assert wp.get("/wp-json/wp/v2/users", auth=wp_admin).status_code == 200
    assert wp.get("/wp-json/wp/v2/users/me", auth=wp.auth).json()["slug"] == "ki-agent"  # Radar prüft so seine Rechte


def test_oembed_ohne_anmeldenamen(wp, admin_beitraege):
    r = wp.get("/wp-json/oembed/1.0/embed", params={"url": URL + "/seo-test-alt-1/"})
    assert r.status_code == 200
    daten = r.json()
    assert daten["author_name"] == "Redaktion Tamil.de" and daten["author_url"].rstrip("/") == URL


def test_autorenarchiv_leitet_auf_die_startseite(wp, admin_beitraege):
    for pfad in ("/author/admin/", "/?author=1"):
        r = wp.get(pfad, allow_redirects=False)
        assert r.status_code == 301 and r.headers["Location"].rstrip("/") == URL, pfad


def test_herausgeber_mit_logo_und_kennung(wp, admin_beitraege):
    a = [d for d in _jsonld(wp.get("/seo-test-alt-1/").text) if d.get("@type") == "NewsArticle"][0]
    p = a["publisher"]
    assert p["@type"] == "NewsMediaOrganization" and p["@id"] == URL + "/#organization" and p["name"]
    logo = p["logo"]
    assert logo["width"] >= 112 and logo["height"] >= 112  # Theme-Logo 300 × 121
    r = requests.get(logo["url"], timeout=30)
    assert r.status_code == 200 and r.headers["Content-Type"].startswith("image/")


def _canonical(seite: str) -> list[str]:
    return [html.unescape(m) for m in re.findall(r'<link rel=["\']canonical["\'] href=["\']([^"\']+)', seite)]


def test_canonical_fuer_startseite_rubrik_und_folgeseite(wp, wp_cli, admin_beitraege):
    assert _canonical(wp.get("/").text) == [URL + "/"]
    assert _canonical(wp.get("/tag/seo-dreimal/").text) == [URL + "/tag/seo-dreimal/"]
    alt = wp_cli("echo get_option( 'posts_per_page' );").strip()
    wp_cli("update_option( 'posts_per_page', 1 );")
    try:
        assert _canonical(wp.get("/tag/seo-dreimal/page/2/").text) == [URL + "/tag/seo-dreimal/page/2/"]
    finally:
        wp_cli(f"update_option( 'posts_per_page', {int(alt)} );")
    assert len(_canonical(wp.get("/seo-test-alt-1/").text)) == 1  # Einzelseiten: weiter das eine von WordPress
    assert _canonical(wp.get("/?s=seo").text) == []


def test_duenne_schlagwoerter_noindex_und_nicht_in_der_sitemap(wp_cli, admin_beitraege):
    code = ("add_filter( 'tamil_site_indexierbar', '__return_true' ); $r = array();"
            " foreach ( array( 'seo-einzeln', 'seo-dreimal' ) as $s ) { query_posts( array( 'tag' => $s ) );"
            " $r[ $s ] = apply_filters( 'wp_robots', array() ); wp_reset_query(); }"
            " $r['users'] = apply_filters( 'wp_sitemaps_add_provider', new stdClass(), 'users' );"
            " $r['posts'] = (bool) apply_filters( 'wp_sitemaps_add_provider', new stdClass(), 'posts' );"
            " $args = apply_filters( 'wp_sitemaps_taxonomies_query_args', array(), 'post_tag' );"
            " $r['exclude'] = array_map( function ( $id ) { return get_term( $id )->slug; }, $args['exclude'] ?? array() );"
            " $r['kategorien'] = apply_filters( 'wp_sitemaps_taxonomies_query_args', array(), 'category' );"
            " echo wp_json_encode( $r );")
    r = json.loads(wp_cli(code))
    assert r["seo-einzeln"].get("noindex") is True and r["seo-einzeln"].get("follow") is True
    assert "noindex" not in r["seo-dreimal"]
    assert r["users"] is False and r["posts"] is True
    assert "seo-einzeln" in r["exclude"] and "seo-dreimal" not in r["exclude"]
    assert r["kategorien"] == []  # Rubriken bleiben vollständig
