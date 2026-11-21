"""Plugin tamil-site: Eigenanzeigen (ungebuchte Werbeplätze, Festlegung F3) als Bildbanner.

Regel des Auftraggebers (Luis, 17.11.): Alles auf der Website hat ein Bild, auch jede Anzeige; eine Eigenanzeige ohne
Bild wird nicht gezeigt. Dazu weiter: kein Icon, keine Dachzeile, kein Gedankenstrich, keine „·“-Ketten (Hallmark Gate
19 und Floor 10, Kritik theme-tageskalender-r1 P1-3 und P1-5); Platz, Kennzeichnung „Anzeige“ und Ziel bleiben.
"""

import html
import json
import re

import pytest
import requests
from wp_umgebung import URL

VORLAGEN = ["production", "event", "werben", "whatsapp", "whatsapp-klein"]


def _html(wp_cli, vorlage: str, platz: str = "") -> str:
    return wp_cli(f"echo tamil_site_eigenanzeige_html( '{vorlage}', '{platz}' );")


def _img(html: str) -> str:
    m = re.search(r'<img class="anzeige__bild"[^>]*>', html)
    assert m, "Bild im Banner fehlt"
    return m.group(0)


def _ohne_tags(html_text: str) -> str:
    """Sichtbarer Text ohne Tags und Entitäten, Leerraum zusammengefasst: Das Theme verlinkt Urheber und Lizenz im
    Nachweis (Theme 3.3.0, tamil_nachweis_bauen()), die Aussage bleibt dieselbe."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", html_text))).strip()


def _attr(tag: str, name: str) -> str:
    m = re.search(rf'\s{name}="([^"]*)"', tag)
    return m.group(1) if m else ""


@pytest.mark.parametrize("vorlage", VORLAGEN)
def test_eigenanzeige_ist_bildbanner_ohne_icon_dachzeile_und_striche(wp_cli, seite_production, vorlage):
    html = _html(wp_cli, vorlage)
    assert html.startswith('<a class="flaeche anzeige-wrap"') and f'class="anzeige a-{vorlage} anzeige--bild' in html
    assert "<svg" not in html and "eyebrow" not in html and 'class="marke"' not in html
    assert "–" not in html and "—" not in html and "·" not in html  # –, —, ·
    assert '<span class="claim">' in html and '<span class="cta">' in html
    img = _img(html)
    assert _attr(img, "alt").strip(), "Bild ohne Alternativtext"
    assert _attr(img, "width") and _attr(img, "height") and 'loading="lazy"' in img


@pytest.mark.parametrize("vorlage", VORLAGEN)
def test_linkname_beginnt_mit_dem_sichtbaren_text(wp_cli, seite_production, vorlage):
    """axe label-content-name-mismatch (Prüfung 17.11., P1-11): kein aria-label, das vom sichtbaren Text abweicht. Der
    Name kommt aus dem Inhalt; Titel und Linktext stehen vor dem Bild, damit der Name mit dem sichtbaren Text beginnt."""
    html = _html(wp_cli, vorlage)
    link = re.match(r"<a [^>]*>", html).group(0)
    assert "aria-label" not in link and "aria-labelledby" not in link
    assert html.index('<span class="claim">') < html.index('<img class="anzeige__bild"')
    assert html.index('<span class="cta">') < html.index('<img class="anzeige__bild"')


@pytest.mark.parametrize("vorlage", ["production", "event", "werben", "whatsapp"])
def test_bild_der_eigenanzeige_wird_geladen(wp, wp_cli, seite_production, vorlage):
    img = _img(_html(wp_cli, vorlage))
    adressen = [_attr(img, "src")] + [teil.strip().split(" ")[0] for teil in _attr(img, "srcset").split(",") if teil.strip()]
    for adresse in adressen:
        r = requests.get(adresse.replace("&#038;", "&"), timeout=30)
        assert r.status_code == 200 and r.headers.get("content-type", "").startswith("image/"), adresse
        assert len(r.content) > 5000, f"{adresse}: kein echtes Foto"


def test_production_behauptet_nichts_ueber_die_quelle_hinaus(wp_cli, seite_production):
    """Nichts Erfundenes (unabhängige Prüfung Runde 4, P1-5): die Quelle (site.json) sagt „standen oder stehen … auf
    deutschen Bühnen“, nicht „Konzertreihe in Deutschland, Österreich und der Schweiz“, und belegt keine Tickets."""
    html = _html(wp_cli, "production")
    assert "standen oder stehen mit Tamil.de Production auf deutschen Bühnen" in html
    assert "Österreich" not in html and "Schweiz" not in html and ">Tickets<" not in html
    assert '/production/"' in html


def test_production_ohne_seite_fuehrt_nicht_ins_leere(wp_cli):
    """Ohne veröffentlichte Seite „production“ (live bisher 404) zeigt „Live mit dir!“ nichts statt eines toten Links."""
    if wp_cli("$s = get_page_by_path( 'production', OBJECT, 'page' ); echo $s && 'publish' === $s->post_status ? 1 : 0;").strip() == "1":
        pytest.skip("Seite production ist lokal angelegt")
    assert _html(wp_cli, "production") == ""


def test_unbekannte_vorlage_bleibt_leer(wp_cli):
    assert _html(wp_cli, "gibt-es-nicht") == ""


def test_whatsapp_oeffnet_neues_fenster_andere_nicht(wp_cli):
    assert 'target="_blank" rel="noopener"' in _html(wp_cli, "whatsapp")
    assert "target=" not in _html(wp_cli, "werben")


def test_eigenanzeige_ohne_bild_wird_nicht_gezeigt(wp_cli):
    """Weder Standardbild noch gewähltes Bild: Die Eigenanzeige und damit der ungebuchte Platz bleiben leer."""
    code = ("add_filter( 'tamil_site_eigenanzeige_standardbilder', static function ( $b ) { unset( $b['werben'] ); return $b; } );"
            " $s = tamil_site_settings(); $s['eigen']['footer'] = 'werben'; $s['anzeigen']['footer'] = ''; $s['advanced_ads']['footer'] = '';"
            " add_filter( 'pre_option_tamil_site_settings', static function () use ( $s ) { return $s; } );"
            " echo wp_json_encode( array( tamil_site_eigenanzeige_html( 'werben' ), tamil_site_anzeige( 'footer', false ), tamil_site_eigenanzeige_html( 'event' ) !== '' ) );")
    html, platz, anderes = json.loads(wp_cli(code))
    assert html == "" and platz == "", "Anzeige ohne Bild darf nicht erscheinen"
    assert anderes is True, "die übrigen Eigenanzeigen bleiben"


@pytest.fixture
def mediathek_bild(wp_cli, tmp_path):
    """Ein echtes Bild in der Mediathek (mit Alternativtext und Bildunterschrift), danach gelöscht."""
    datei = tmp_path / "eigenanzeige-test.png"
    datei.write_bytes(_png(640, 420))
    aid = int(wp_cli(
        "require_once ABSPATH . 'wp-admin/includes/image.php';"
        f" $u = wp_upload_bits( 'eigenanzeige-test.png', null, file_get_contents( '{datei}' ) );"
        " $id = wp_insert_attachment( array( 'post_mime_type' => 'image/png', 'post_title' => 'Eigenanzeige Test', 'post_status' => 'inherit',"
        " 'post_excerpt' => 'Foto: Testbild' ), $u['file'] );"
        " wp_update_attachment_metadata( $id, wp_generate_attachment_metadata( $id, $u['file'] ) );"
        " update_post_meta( $id, '_wp_attachment_image_alt', 'Testbild für die Eigenanzeige' ); echo (int) $id;").strip())
    alt = wp_cli("echo wp_json_encode( get_option( 'tamil_site_settings', null ) );").strip()
    yield aid
    wp_cli(f"wp_delete_attachment( {aid}, true );")
    if alt == "null":
        wp_cli("delete_option( 'tamil_site_settings' );")
    else:
        wp_cli(f"update_option( 'tamil_site_settings', json_decode( {alt!r}, true ) );")


def _png(w: int, h: int) -> bytes:
    """Farbverlauf als PNG (ohne Bildbibliothek)."""
    import struct
    import zlib
    roh = b"".join(b"\x00" + bytes(v for x in range(w) for v in ((x + y) % 256, (x * 2) % 256, (y * 3) % 256)) for y in range(h))

    def chunk(art: bytes, daten: bytes) -> bytes:
        return struct.pack(">I", len(daten)) + art + daten + struct.pack(">I", zlib.crc32(art + daten) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(roh, 6)) + chunk(b"IEND", b""))


def test_gewaehltes_bild_ersetzt_standardbild(wp_cli, mediathek_bild):
    wp_cli(f"$s = (array) get_option( 'tamil_site_settings', array() ); $s['eigen_bild'] = array( 'event' => {mediathek_bild} );"
           " update_option( 'tamil_site_settings', $s );")
    img = _img(_html(wp_cli, "event"))
    assert "eigenanzeige-test" in _attr(img, "src") and _attr(img, "alt") == "Testbild für die Eigenanzeige"
    assert "assets/img/anzeigen/" not in img
    assert requests.get(_attr(img, "src"), timeout=30).status_code == 200
    # gelöschtes Bild: zurück zum Standardbild
    wp_cli(f"wp_delete_attachment( {mediathek_bild}, true );")
    img = _img(_html(wp_cli, "event"))
    assert "assets/img/anzeigen/event" in _attr(img, "src")


def test_formular_nimmt_nur_bilder_aus_der_mediathek(wp_cli, mediathek_bild):
    seite = int(wp_cli("echo (int) wp_insert_post( array( 'post_type' => 'page', 'post_status' => 'draft', 'post_title' => 'kein Bild' ) );").strip())
    try:
        aus = json.loads(wp_cli(
            f"echo wp_json_encode( tamil_site_sanitize_settings( array( 'eigen_bild' => array( 'event' => '{mediathek_bild}', 'werben' => '{seite}',"
            " 'whatsapp' => 'abc', 'boese' => '5' ) ) )['eigen_bild'] );"))
    finally:
        wp_cli(f"wp_delete_post( {seite}, true );")
    assert aus == {"production": 0, "event": mediathek_bild, "werben": 0, "whatsapp": 0}


def test_frontend_texte_ohne_trennpunkt_und_gedankenstrich(wp_cli):
    """Kritik theme-tageskalender-r2 P1-B: Länder, Buchungsdaten, Platz- und Zeitraumtexte im Frontend mit Komma
    bzw. „bis“ statt „·“ und „–“."""
    laender = json.loads(wp_cli("echo wp_json_encode( tamil_site_laender() );"))
    assert laender["DACH"] == "Deutschland, Österreich und Schweiz"
    daten = wp_cli("echo tamil_site_werbung_html_daten( array( 'nummer' => 'T-1', 'platz' => 'leaderboard', 'start' => '2026-11-20',"
                   " 'ende' => '2026-11-26', 'betrag' => 1000, 'ziel_url' => 'https://example.test/' ) );")
    assert " bis " in daten and "–" not in daten and "·" not in daten


def test_frontend_quellen_ohne_trennpunkt_und_gedankenstrich():
    """Quelltext-Prüfung für Stellen, die lokal ohne eingerichtetes Verzeichnis bzw. Buchung nicht erreichbar sind."""
    from pathlib import Path
    plugin = Path(__file__).resolve().parents[2] / "wordpress" / "plugins" / "tamil-site" / "includes"
    vz = (plugin / "verzeichnis-ansicht.php").read_text(encoding="utf-8")
    assert "implode( ' · '" not in vz and "implode( ', ', array_filter( $teile ) )" in vz
    wb = (plugin / "werbung-ansichten.php").read_text(encoding="utf-8")
    assert "' – '" not in wb and "'–'" not in wb  # auch kein Strich als Platzhalter (r3 P2-1)
    assert "__( 'auf Anfrage', 'tamil-site' )" in wb


def test_ungebuchter_platz_zeigt_eigenanzeige_mit_label_und_bild(wp_cli):
    """F3: ein ungebuchter Platz bleibt nicht leer; das Label „Anzeige“ steht dabei, das Banner hat ein Bild."""
    raus = json.loads(wp_cli("echo wp_json_encode( array( tamil_site_anzeige( 'footer', false ), tamil_site_settings()['eigen']['footer'] ) );"))
    html, vorlage = raus
    if not vorlage:
        pytest.skip("Footer-Platz hat lokal keine Eigenanzeige eingestellt")
    if "data-wb-buchung" in html or 'class="flaeche anzeige-wrap"' not in html:
        pytest.skip("Footer-Platz ist lokal gebucht oder mit fremdem Code belegt")
    assert 'class="ad ad-footer ad-anzeige ad-bild"' in html and '<span class="ad-label">Anzeige</span>' in html
    assert _attr(_img(html), "alt").strip()
    # Bildgrößen aus den Formaten (728 × 90 ab 768 px, am Handy Spaltenbreite, dazwischen 320 × 100)
    assert 'sizes="(min-width: 768px) 728px, (max-width: 599px) 100vw, 320px"' in html


def test_seite_mit_eigenanzeigen_nennt_ihre_bildnachweise_im_fuss(wp, wp_cli, seite_production):
    """Die Bildnachweise der gezeigten Eigenanzeigen stehen im Fuß, auch die der Plätze, die erst im Fuß ausgegeben
    werden (Fuß-Anzeige, Handy-Leiste); das CSS der Banner steht im Kopf."""
    if wp_cli("echo function_exists( 'tamil_nachweise' ) ? 1 : 0;").strip() != "1":
        pytest.skip("Theme ohne tamil_nachweise()")
    seite = wp.get("/").text
    assert re.search(r"<link[^>]+tamil-site-anzeigen-css[^>]+anzeigen\.css", seite.split("</head>")[0])
    nachweise = _ohne_tags(seite.split("Bildnachweise dieser Seite", 1)[1] if "Bildnachweise dieser Seite" in seite else "")
    for platz in ("footer", "mobile"):
        vorlage = json.loads(wp_cli(f"echo wp_json_encode( tamil_site_anzeige_inhalt( '{platz}' ) );"))[2]
        if not vorlage:
            continue
        bild = json.loads(wp_cli(f"echo wp_json_encode( tamil_site_eigenanzeige_bild( tamil_site_eigenanzeige_vorlagen()['{vorlage}']['bild'] ) );"))
        assert bild["nachweis"] and bild["nachweis"] in nachweise, f"{platz}: Nachweis fehlt im Fuß"


def test_werbeplatz_ist_ein_benannter_bereich(wp_cli, seite_production):
    """axe „region“ (Prüfung 17.11.): Werbeplätze außerhalb von main und footer (Fuß-Anzeige, Handy-Leiste) liegen in
    einem eigenen Bereich; je Platz ein anderer Name (sonst landmark-unique)."""
    namen = set()
    for platz in ("leaderboard", "footer", "mobile"):
        html = wp_cli(f"echo tamil_site_anzeige( '{platz}', false );")
        if not html:
            continue
        kopf = re.match(r"<aside class=\"ad ad-[a-z]+[^\"]*\"[^>]*>", html)
        assert kopf, html[:120]
        name = re.search(r'aria-label="([^"]+)"', kopf.group(0)).group(1)
        assert name.startswith("Anzeige"), name
        namen.add(name)
    assert len(namen) >= 2


# --- Regeln für Hausanzeigen (Q2-10, Prüfdurchgang 2 vom 20.11.2026) ---------------------------------------------


def test_keine_zweite_eigenanzeige_direkt_danach(wp_cli):
    """Nennt das Theme den Platz unmittelbar davor und war dort eine Eigenanzeige, bleibt der folgende Platz leer;
    ohne Nachbarn oder nach einer gebuchten Anzeige erscheint die Eigenanzeige."""
    code = (" $s = tamil_site_settings(); foreach ( array( 'leaderboard', 'footer' ) as $p ) { $s['eigen'][ $p ] = 'event';"
            " $s['anzeigen'][ $p ] = ''; $s['advanced_ads'][ $p ] = ''; }"
            " add_filter( 'pre_option_tamil_site_settings', static function () use ( $s ) { return $s; } );"
            " $lb = tamil_site_anzeige( 'leaderboard', false ); $direkt = tamil_site_anzeige( 'footer', false, 'leaderboard' );"
            " $frei = tamil_site_anzeige( 'footer', false );"
            " echo wp_json_encode( array( '' !== $lb, $direkt, '' !== $frei ) );")
    lb, direkt, frei = json.loads(wp_cli(code))
    assert lb is True, "die erste Eigenanzeige erscheint"
    assert direkt == "", "keine zweite Eigenanzeige direkt dahinter"
    assert frei is True, "ohne Nachbarn erscheint sie"


def test_impressum_und_datenschutz_ohne_eigenanzeigen(wp, wp_cli):
    pid = int(wp_cli("echo (int) wp_insert_post( array( 'post_type' => 'page', 'post_status' => 'publish',"
                     " 'post_name' => 'datenschutzerklaerung', 'post_title' => 'Datenschutz (Test)', 'post_content' => '<p>Text.</p>' ) );"))
    try:
        seite = wp.get("/datenschutzerklaerung/").text
        assert '<aside class="ad ' not in seite, "auf Datenschutz keine Eigenanzeigen (ungebuchte Plätze bleiben leer)"
        assert '<aside class="ad ' in wp.get("/kontakt/").text, "Gegenprobe: andere Seiten behalten ihre Plätze"
    finally:
        wp_cli(f"wp_delete_post( {pid}, true );")


def test_keine_werbung_fuer_die_eigene_seite(wp, wp_cli, seite_production):
    """Eine Eigenanzeige führt nie auf die Seite, auf der sie steht: „Live mit dir!“ fehlt auf /production/, auf
    /kontakt/ erscheint sie (gleiche Regel für „Werben auf Tamil.de“ auf /werben/)."""
    alt = wp_cli("echo base64_encode( wp_json_encode( get_option( 'tamil_site_settings' ) ) );").strip()
    wp_cli("$s = (array) get_option( 'tamil_site_settings', array() ); $s['eigen']['leaderboard'] = 'production';"
           " $s['anzeigen']['leaderboard'] = ''; $s['advanced_ads']['leaderboard'] = '';"
           " remove_all_filters( 'sanitize_option_tamil_site_settings' ); update_option( 'tamil_site_settings', $s );")
    try:
        assert "Zur Konzertreihe" not in wp.get("/production/").text
        assert "Zur Konzertreihe" in wp.get("/kontakt/").text
    finally:
        wp_cli("remove_all_filters( 'sanitize_option_tamil_site_settings' );"
               f" update_option( 'tamil_site_settings', json_decode( base64_decode( '{alt}' ), true ) );")
