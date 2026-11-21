"""Theme tamil 3.10.0: Wow-Aufmacher „Punkt für Punkt zum Bild“ (inc/wow.php).

Nur der Aufmacher der Startseite mit eigenem Foto ab 960 px Breite bekommt die Decke; abschaltbar im Customizer
(theme_mod tamil_wow_aufmacher) und über den Filter tamil_wow_aufmacher.
"""

import json

import pytest


def _bild(wp_cli, breite: int, hoehe: int) -> int:
    """Anhang mit der gewünschten Größe in den Metadaten (die Datei selbst braucht die Prüfung nicht)."""
    return int(wp_cli(
        "$id = wp_insert_attachment( array( 'post_mime_type' => 'image/jpeg', 'post_title' => 'wow-test', 'post_status' => 'inherit' ),"
        " 'wow-test.jpg' );"
        f" wp_update_attachment_metadata( $id, array( 'width' => {breite}, 'height' => {hoehe}, 'file' => 'wow-test.jpg', 'sizes' => array() ) );"
        " echo $id;"))


@pytest.fixture
def beitraege(wp_cli):
    """Drei Beiträge: eigenes großes Foto, eigenes kleines Foto, kein Foto."""
    gross = _bild(wp_cli, 1600, 900)
    klein = _bild(wp_cli, 640, 360)
    ids = {}
    for name, bild in (("gross", gross), ("klein", klein), ("ohne", 0)):
        ids[name] = int(wp_cli(
            f"$p = wp_insert_post( array( 'post_title' => 'Wow-Test {name}', 'post_status' => 'publish', 'post_content' => '<p>x</p>' ) );"
            + (f" set_post_thumbnail( $p, {bild} );" if bild else "") + " echo $p;"))
    yield ids
    for pid in ids.values():
        wp_cli(f"wp_delete_post( {pid}, true );")
    for aid in (gross, klein):
        wp_cli(f"wp_delete_attachment( {aid}, true );")


def _an(wp_cli, pid: int, vorher: str = "") -> bool:
    return json.loads(wp_cli(f"{vorher} echo wp_json_encode( tamil_wow_aufmacher_an( {pid} ) );"))


def test_nur_mit_eigenem_foto_ab_960_px(wp_cli, beitraege):
    an = "set_theme_mod( 'tamil_wow_aufmacher', '1' );"
    assert _an(wp_cli, beitraege["gross"], an) is True
    assert _an(wp_cli, beitraege["klein"], an) is False, "kleines Foto: normaler Aufmacher"
    assert _an(wp_cli, beitraege["ohne"], an) is False, "ohne eigenes Foto (Symbolbild aus dem Pool): normaler Aufmacher"


def test_abschalten_ueber_customizer_und_filter(wp_cli, beitraege):
    alt = wp_cli("echo wp_json_encode( get_theme_mod( 'tamil_wow_aufmacher', null ) );").strip()
    try:
        assert _an(wp_cli, beitraege["gross"], "set_theme_mod( 'tamil_wow_aufmacher', '' );") is False, "Customizer aus"
        assert _an(wp_cli, beitraege["gross"], "set_theme_mod( 'tamil_wow_aufmacher', '1' );"
                   " add_filter( 'tamil_wow_aufmacher', '__return_false' );") is False, "Filter aus"
        assert _an(wp_cli, beitraege["gross"], "remove_theme_mod( 'tamil_wow_aufmacher' );") is True, "Standard: an"
    finally:
        wp_cli(f"$a = json_decode( '{alt}' ); if ( null === $a ) {{ remove_theme_mod( 'tamil_wow_aufmacher' ); }}"
               " else { set_theme_mod( 'tamil_wow_aufmacher', $a ); }")


def test_startseite_laedt_skript_nur_mit_wow(wp, wp_cli):
    """Ist die Decke an, trägt der Aufmacher die Klasse wow und wow.js wird geladen; aus: beides fehlt."""
    alt = wp_cli("echo wp_json_encode( get_theme_mod( 'tamil_wow_aufmacher', null ) );").strip()
    lead = int(wp_cli("echo (int) tamil_start_auswahl()['lead'];"))
    soll = json.loads(wp_cli(f"remove_theme_mod( 'tamil_wow_aufmacher' ); echo wp_json_encode( tamil_wow_aufmacher_an( {lead} ) );"))
    try:
        seite = wp.get("/").text
        assert ('class="aufmacher wow"' in seite) is soll and ("assets/js/wow.js" in seite) is soll
        wp_cli("set_theme_mod( 'tamil_wow_aufmacher', '' );")
        aus = wp.get("/").text
        assert 'class="aufmacher wow"' not in aus and "assets/js/wow.js" not in aus and "wow-an" not in aus
        assert 'class="aufmacher"' in aus, "der normale Aufmacher bleibt"
    finally:
        wp_cli(f"$a = json_decode( '{alt}' ); if ( null === $a ) {{ remove_theme_mod( 'tamil_wow_aufmacher' ); }}"
               " else { set_theme_mod( 'tamil_wow_aufmacher', $a ); }")
