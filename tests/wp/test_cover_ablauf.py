"""Theme tamil 3.15.0: Das Cover der Startseite verfällt (inc/queries.php, TML-W02).

Ein im Customizer gesetzter Aufmacher gilt bis „Aufmacher gilt bis“ (einschließlich), ohne Datum höchstens sieben Tage
ab dem Eintragen; Altbestand ohne Zeitpunkt: Veröffentlichung plus sieben Tage. Ein markierter Beitrag verfällt
sieben Tage nach Veröffentlichung. Danach greift die Kette (neuestes Foto), nie bleibt ein abgelaufenes Cover stehen.
"""

import json

import pytest

TAG = 86400


def _bild(wp_cli) -> int:
    return int(wp_cli(
        "$id = wp_insert_attachment( array( 'post_mime_type' => 'image/jpeg', 'post_title' => 'cover-test', 'post_status' => 'inherit' ),"
        " 'cover-test.jpg' );"
        " wp_update_attachment_metadata( $id, array( 'width' => 1600, 'height' => 1200, 'file' => 'cover-test.jpg', 'sizes' => array() ) );"
        " echo $id;"))


@pytest.fixture
def start(wp_cli):
    """Merkt sich Aufmacher, Datum, Zeitpunkt und markierte Beiträge, leert sie für den Test und stellt danach alles
    wieder her. `start.beitrag(tage)` legt einen Beitrag mit eigenem Foto an, veröffentlicht vor `tage` Tagen."""
    alt = json.loads(wp_cli(
        "echo wp_json_encode( array( 'id' => get_theme_mod( 'tamil_aufmacher_id', null ), 'bis' => get_theme_mod( 'tamil_aufmacher_bis', null ),"
        " 'seit' => get_option( 'tamil_aufmacher_seit', null ), 'sticky' => get_option( 'sticky_posts', array() ) ) );"))
    wp_cli("remove_theme_mod( 'tamil_aufmacher_id' ); remove_theme_mod( 'tamil_aufmacher_bis' ); delete_option( 'tamil_aufmacher_seit' );"
           " update_option( 'sticky_posts', array() ); tamil_flush_auswahl();")
    beitraege: list[int] = []
    bilder: list[int] = []

    class Start:
        @staticmethod
        def beitrag(tage: float, titel: str = "Cover-Test") -> int:
            bild = _bild(wp_cli)
            bilder.append(bild)
            pid = int(wp_cli(
                f"$p = wp_insert_post( array( 'post_title' => '{titel}', 'post_status' => 'publish', 'post_content' => '<p>x</p>',"
                f" 'post_date' => wp_date( 'Y-m-d H:i:s', time() - {int(tage * TAG)} ) ) ); set_post_thumbnail( $p, {bild} ); echo $p;"))
            beitraege.append(pid)
            return pid

        @staticmethod
        def lead(vorher: str = "") -> int:
            """Aufmacher der Startseite nach `vorher` (PHP); der Zwischenspeicher wird davor verworfen."""
            return int(wp_cli(f"{vorher} tamil_flush_auswahl(); echo (int) tamil_start_auswahl()['lead'];"))

    yield Start
    for pid in beitraege:
        wp_cli(f"wp_delete_post( {pid}, true );")
    for aid in bilder:
        wp_cli(f"wp_delete_attachment( {aid}, true );")
    # erst die Theme-Einstellungen (der Haken schreibt dabei einen neuen Zeitpunkt), dann den alten Zeitpunkt
    wp_cli(
        f"$a = json_decode( '{json.dumps(alt)}', true );"
        " foreach ( array( 'id' => 'tamil_aufmacher_id', 'bis' => 'tamil_aufmacher_bis' ) as $k => $mod ) {"
        "   if ( null === $a[ $k ] ) { remove_theme_mod( $mod ); } else { set_theme_mod( $mod, $a[ $k ] ); } }"
        " if ( null === $a['seit'] ) { delete_option( 'tamil_aufmacher_seit' ); } else { update_option( 'tamil_aufmacher_seit', $a['seit'], false ); }"
        " update_option( 'sticky_posts', $a['sticky'] ); tamil_flush_auswahl();")


def test_gesetztes_cover_gilt_sieben_tage_ab_dem_eintragen(wp_cli, start):
    alt = start.beitrag(30)  # ein altes Stück: Es zählt der Zeitpunkt des Eintragens, nicht das Alter des Beitrags
    start.beitrag(0.1)  # die Kette hätte etwas Neueres
    assert start.lead(f"set_theme_mod( 'tamil_aufmacher_id', {alt} );") == alt, "frisch gesetzt: bleibt"
    seit = int(wp_cli("echo (int) get_option( 'tamil_aufmacher_seit' );"))
    jetzt = int(wp_cli("echo time();"))
    assert abs(jetzt - seit) < 120, "der Zeitpunkt des Eintragens wird beim Speichern festgehalten"
    assert start.lead(f"update_option( 'tamil_aufmacher_seit', time() - {6 * TAG} );") == alt, "nach sechs Tagen: bleibt"

    kette = start.lead("remove_theme_mod( 'tamil_aufmacher_id' );")
    assert kette != alt and int(wp_cli("echo (int) get_option( 'tamil_aufmacher_seit', 0 );")) == 0, "geleert: Zeitpunkt weg"
    nach = start.lead(f"set_theme_mod( 'tamil_aufmacher_id', {alt} ); update_option( 'tamil_aufmacher_seit', time() - {8 * TAG} );")
    assert nach == kette, "nach acht Tagen: abgelaufen, die Kette (neuestes Foto) greift"


def test_datum_gilt_bis_einschliesslich_und_schlaegt_die_sieben_tage(wp_cli, start):
    alt = start.beitrag(30)
    start.beitrag(0.1)
    setzen = f"set_theme_mod( 'tamil_aufmacher_id', {alt} ); update_option( 'tamil_aufmacher_seit', time() - {20 * TAG} );"
    heute = start.lead(setzen + " set_theme_mod( 'tamil_aufmacher_bis', current_time( 'Y-m-d' ) );")
    assert heute == alt, "Datum heute: gilt noch den ganzen Tag, auch wenn das Eintragen 20 Tage her ist"
    gestern = start.lead("set_theme_mod( 'tamil_aufmacher_bis', wp_date( 'Y-m-d', time() - DAY_IN_SECONDS ) );"
                         " update_option( 'tamil_aufmacher_seit', time() );")
    assert gestern != alt, "Datum gestern: abgelaufen, auch wenn gerade erst eingetragen"
    assert wp_cli("echo tamil_sanitize_datum( '2026-02-30' ) . '|' . tamil_sanitize_datum( 'morgen' ) . '|' . tamil_sanitize_datum( '2026-12-24' );") \
        == "||2026-12-24"


def test_altbestand_ohne_zeitpunkt_zaehlt_ab_veroeffentlichung(wp_cli, start):
    alt = start.beitrag(30)
    jung = start.beitrag(2)
    start.beitrag(0.1)
    ohne = " delete_option( 'tamil_aufmacher_seit' );"
    assert start.lead(f"set_theme_mod( 'tamil_aufmacher_id', {alt} );" + ohne) != alt, "30 Tage alter Beitrag ohne Zeitpunkt: abgelaufen"
    assert start.lead(f"set_theme_mod( 'tamil_aufmacher_id', {jung} );" + ohne) == jung, "zwei Tage alter Beitrag: gilt noch"


def test_markierter_beitrag_verfaellt_nach_sieben_tagen(wp_cli, start):
    alt = start.beitrag(8)
    jung = start.beitrag(2)
    neu = start.beitrag(0.1)
    assert start.lead(f"update_option( 'sticky_posts', array( {alt} ) );") != alt, "markiert, aber älter als sieben Tage"
    assert start.lead(f"update_option( 'sticky_posts', array( {alt}, {jung} ) );") == jung, "markiert und jung: Cover, vor dem neuesten Foto"
    assert neu != jung


def test_zwischenspeicher_kennt_tag_und_frist(wp_cli, start):
    alt = start.beitrag(30)
    start.beitrag(0.1)
    assert json.loads(wp_cli("echo wp_json_encode( str_ends_with( tamil_start_schluessel(), '_' . current_time( 'Ymd' ) ) );")) is True
    frist, ende = json.loads(wp_cli(
        f"set_theme_mod( 'tamil_aufmacher_id', {alt} ); tamil_flush_auswahl(); $a = tamil_start_auswahl();"
        " echo wp_json_encode( array( $a['frist'], tamil_cover_manuell()['ende'] ) );"))
    assert frist == ende > 0
    # ein Eintrag im Zwischenspeicher, dessen Cover inzwischen abgelaufen ist, wird nicht mehr ausgeliefert
    lead = int(wp_cli(
        f"update_option( 'tamil_aufmacher_seit', time() - {8 * TAG} );"
        " $a = get_transient( tamil_start_schluessel() ); $a['frist'] = time() - 1; set_transient( tamil_start_schluessel(), $a, 600 );"
        " echo (int) tamil_start_auswahl()['lead'];"))
    assert lead != alt


def test_hinweis_im_customizer_bei_abgelaufenem_cover(wp_cli, start):
    alt = start.beitrag(30)
    gueltig = wp_cli(f"set_theme_mod( 'tamil_aufmacher_id', {alt} ); echo tamil_customizer_hinweis( 'aufmacher_id' );")
    assert gueltig.startswith("Gilt bis") and "abgelaufen" not in gueltig
    weg = wp_cli(f"update_option( 'tamil_aufmacher_seit', time() - {8 * TAG} ); echo tamil_customizer_hinweis( 'aufmacher_id' );")
    assert "abgelaufen" in weg and "Aufmacher gilt bis" in weg
    assert wp_cli("remove_theme_mod( 'tamil_aufmacher_id' ); echo tamil_customizer_hinweis( 'aufmacher_id' );") == ""
    assert "7 Tage" in wp_cli("echo tamil_customizer_hinweis( 'aufmacher_bis' );")


def _aufmacher(wp) -> str:
    """Nur die Bildkarte des Aufmachers (der Beitrag darf weiter unten als gewöhnliche Karte stehen)."""
    seite = wp.get("/").text
    karte = seite[seite.index('<article class="aufmacher'):]
    return karte[:karte.index("</article>")]


def test_startseite_zeigt_abgelaufenes_cover_nicht_als_aufmacher(wp, wp_cli, start):
    alt = start.beitrag(30, "Cover-Test Abgelaufen 4711")
    start.beitrag(0.1, "Cover-Test Neu 4712")
    start.lead(f"set_theme_mod( 'tamil_aufmacher_id', {alt} );")
    assert "Cover-Test Abgelaufen 4711" in _aufmacher(wp), "gültig: steht im Aufmacher"
    start.lead(f"update_option( 'tamil_aufmacher_seit', time() - {8 * TAG} );")
    aufmacher = _aufmacher(wp)
    assert "Cover-Test Abgelaufen 4711" not in aufmacher and "Cover-Test Neu 4712" in aufmacher
