"""Plugin tamil-site: Upgrade-Routine (Datenversion, Seiten, Rechte, Sperre) und Funktionsschalter."""

import json


def _php_json(wp_cli, code: str):
    return json.loads(wp_cli(code))


def test_datenversion_nach_aufruf_aktuell(wp, wp_cli):
    wp_cli("delete_option( 'tamil_site_datenversion' );")
    assert wp.get("/").status_code == 200
    stand = _php_json(wp_cli, "echo wp_json_encode( array( (int) get_option( 'tamil_site_datenversion' ), TAMIL_SITE_DATENVERSION ) );")
    assert stand[0] == stand[1] >= 1


def test_vorhandene_seiten_bleiben_unberuehrt_und_lauf_ist_idempotent(wp_cli):
    code = r"""
    $ergebnis = array();
    $alt      = get_page_by_path( 'impressum', OBJECT, 'page' );
    $sicher   = $alt ? array( 'post_status' => $alt->post_status, 'post_content' => $alt->post_content, 'post_title' => $alt->post_title ) : null;
    if ( $alt ) {
        wp_update_post( array( 'ID' => $alt->ID, 'post_status' => 'publish', 'post_content' => 'Text von KBS', 'post_title' => 'Impressum KBS' ) );
        $id = $alt->ID;
    } else {
        $id = wp_insert_post( array( 'post_type' => 'page', 'post_name' => 'impressum', 'post_status' => 'publish', 'post_content' => 'Text von KBS', 'post_title' => 'Impressum KBS' ) );
    }
    delete_option( 'tamil_site_datenversion' );
    $ergebnis['lauf1'] = tamil_site_upgrade_ausfuehren();
    delete_option( 'tamil_site_datenversion' );
    $ergebnis['lauf2'] = tamil_site_upgrade_ausfuehren();
    $p = get_post( $id );
    $ergebnis['impressum'] = array( $p->post_status, $p->post_content, $p->post_title, $p->post_name );
    $ergebnis['anzahl']    = count( get_posts( array( 'post_type' => 'page', 'post_name__in' => array( 'impressum' ), 'post_status' => 'any', 'numberposts' => -1 ) ) );
    if ( $sicher ) {
        wp_update_post( array_merge( array( 'ID' => $id ), $sicher ) );
    } else {
        wp_delete_post( $id, true ); // vorher gab es keine: nichts zurücklassen
    }
    echo wp_json_encode( $ergebnis );
    """
    r = _php_json(wp_cli, code)
    assert r["lauf1"] is True and r["lauf2"] is True
    assert r["impressum"] == ["publish", "Text von KBS", "Impressum KBS", "impressum"]
    assert r["anzahl"] == 1


def test_fehlende_seite_wird_leerer_entwurf(wp_cli):
    code = r"""
    // Eine vorhandene Seite wird nur kurz umbenannt (ID und Inhalt bleiben), nicht gelöscht.
    $alt = get_page_by_path( 'datenschutz', OBJECT, 'page' );
    if ( $alt ) { wp_update_post( array( 'ID' => $alt->ID, 'post_name' => 'datenschutz-testpause' ) ); }
    delete_option( 'tamil_site_datenversion' );
    tamil_site_upgrade_ausfuehren();
    tamil_site_upgrade_ausfuehren();
    $neu   = get_page_by_path( 'datenschutz', OBJECT, 'page' );
    $daten = array( $neu->post_status, $neu->post_content, $neu->post_title,
        count( get_posts( array( 'post_type' => 'page', 'post_name__in' => array( 'datenschutz' ), 'post_status' => 'any', 'numberposts' => -1 ) ) ) );
    wp_delete_post( $neu->ID, true );
    if ( $alt ) { wp_update_post( array( 'ID' => $alt->ID, 'post_name' => 'datenschutz' ) ); }
    echo wp_json_encode( $daten );
    """
    assert _php_json(wp_cli, code) == ["draft", "", "Datenschutz", 1]


def test_sperre_verhindert_gleichzeitigen_lauf_und_rechte_werden_nachgeruestet(wp_cli):
    code = r"""
    $r = array();
    $r['erste']  = tamil_site_upgrade_sperren();
    $r['zweite'] = tamil_site_upgrade_sperren();
    $r['lauf_gesperrt'] = tamil_site_upgrade_ausfuehren();
    tamil_site_upgrade_entsperren();
    // liegengebliebene Sperre verfällt
    global $wpdb;
    $wpdb->query( $wpdb->prepare( "INSERT INTO {$wpdb->options} (option_name, option_value, autoload) VALUES ('tamil_site_upgrade_sperre', %s, 'off')", (string) ( time() - 3600 ) ) );
    $r['alte_sperre'] = tamil_site_upgrade_sperren();
    tamil_site_upgrade_entsperren();
    // Rechte: fehlendes Recht der Rolle radar wird ergänzt, nichts entzogen
    $role = get_role( 'radar' );
    $role->remove_cap( 'upload_files' );
    tamil_site_rechte_anmelden( 'radar', array( 'tamil_test_recht' ) );
    delete_option( 'tamil_site_datenversion' );
    $r['lauf'] = tamil_site_upgrade_ausfuehren();
    $role = get_role( 'radar' );
    $r['rechte'] = array( $role->has_cap( 'upload_files' ), $role->has_cap( 'tamil_test_recht' ), $role->has_cap( 'edit_posts' ) );
    $role->remove_cap( 'tamil_test_recht' );
    echo wp_json_encode( $r );
    """
    r = _php_json(wp_cli, code)
    assert r["erste"] is True and r["zweite"] is False and r["lauf_gesperrt"] is False
    assert r["alte_sperre"] is True
    assert r["lauf"] is True and r["rechte"] == [True, True, True]


def test_schritte_laufen_einmal_in_reihenfolge(wp_cli):
    code = r"""
    $GLOBALS['tamil_test_log'] = array();
    tamil_site_upgrade_schritt( 1, 'b', function () { $GLOBALS['tamil_test_log'][] = 'v1'; } );
    tamil_site_upgrade_schritt( 99, 'zukunft', function () { $GLOBALS['tamil_test_log'][] = 'v99'; } );
    update_option( 'tamil_site_datenversion', 0 );
    tamil_site_upgrade_ausfuehren();
    tamil_site_upgrade_pruefen();
    echo wp_json_encode( $GLOBALS['tamil_test_log'] );
    """
    assert json.loads(wp_cli(code)) == ["v1"]


def test_funktionsschalter_standard_aus(wp_cli):
    code = r"""
    $alt = get_option( 'tamil_site_funktionen', null );
    delete_option( 'tamil_site_funktionen' );
    $r = array();
    foreach ( array( 'einreichungen', 'verzeichnis', 'werbung', 'zustimmung', 'gibtsnicht' ) as $n ) { $r[ $n ] = tamil_site_funktion_an( $n ); }
    update_option( 'tamil_site_funktionen', tamil_site_sanitize_funktionen( array( 'zustimmung' => '1', 'boese' => '1' ) ) );
    $r['nach_speichern'] = array( tamil_site_funktion_an( 'zustimmung' ), tamil_site_funktion_an( 'werbung' ), array_keys( get_option( 'tamil_site_funktionen' ) ) );
    if ( null === $alt ) { delete_option( 'tamil_site_funktionen' ); } else { update_option( 'tamil_site_funktionen', $alt ); }
    echo wp_json_encode( $r );
    """
    r = json.loads(wp_cli(code))
    assert not any(r[n] for n in ("einreichungen", "verzeichnis", "werbung", "zustimmung", "gibtsnicht"))
    assert r["nach_speichern"] == [True, False, ["einreichungen", "verzeichnis", "werbung", "zustimmung"]]


def test_einstellungsseite_zeigt_schalter(wp, wp_sitzung):
    html = wp_sitzung.get(f"{wp.url}/wp-admin/options-general.php?page=tamil-site", timeout=30).text
    for name in ("einreichungen", "verzeichnis", "werbung", "zustimmung"):
        assert f'name="tamil_site_funktionen[{name}]"' in html


def test_nach_fehlschlag_wartezeit_statt_neuversuch_bei_jedem_aufruf(wp_cli):
    code = r"""
    $r = array();
    $GLOBALS['tamil_test_zaehler'] = 0;
    tamil_site_upgrade_schritt( TAMIL_SITE_DATENVERSION, 'kaputt', function () { $GLOBALS['tamil_test_zaehler']++; throw new RuntimeException( 'kaputt' ); } );
    update_option( 'tamil_site_datenversion', 0 );
    delete_option( 'tamil_site_upgrade_fehler' );
    $r['lauf'] = tamil_site_upgrade_ausfuehren();
    $r['fehler_gemerkt'] = (int) get_option( 'tamil_site_upgrade_fehler' ) > 0;
    tamil_site_upgrade_pruefen();
    tamil_site_upgrade_pruefen();
    $r['versuche_in_wartezeit'] = $GLOBALS['tamil_test_zaehler'];
    update_option( 'tamil_site_upgrade_fehler', time() - TAMIL_SITE_UPGRADE_WARTEN_SEKUNDEN - 1 );
    tamil_site_upgrade_pruefen();
    $r['versuche_nach_wartezeit'] = $GLOBALS['tamil_test_zaehler'];
    $r['version'] = (int) get_option( 'tamil_site_datenversion' );
    // aufräumen: ohne den kaputten Schritt (gibt es nur in diesem Prozess) wieder auf Stand
    delete_option( 'tamil_site_upgrade_fehler' );
    update_option( 'tamil_site_datenversion', TAMIL_SITE_DATENVERSION );
    echo wp_json_encode( $r );
    """
    r = json.loads(wp_cli(code))
    assert r == {"lauf": False, "fehler_gemerkt": True, "versuche_in_wartezeit": 1, "versuche_nach_wartezeit": 2, "version": 0}


def test_liegengebliebene_sperre_nur_mit_gelesenem_wert_loeschen(wp_cli):
    code = r"""
    global $wpdb;
    tamil_site_upgrade_entsperren();
    $wpdb->query( "INSERT INTO {$wpdb->options} (option_name, option_value, autoload) VALUES ('tamil_site_upgrade_sperre', 'B', 'off')" );
    $r = array( tamil_site_upgrade_sperre_aufraeumen( 'A' ) );
    $r[] = $wpdb->get_var( "SELECT option_value FROM {$wpdb->options} WHERE option_name = 'tamil_site_upgrade_sperre'" );
    $r[] = tamil_site_upgrade_sperre_aufraeumen( 'B' );
    $r[] = $wpdb->get_var( "SELECT option_value FROM {$wpdb->options} WHERE option_name = 'tamil_site_upgrade_sperre'" );
    tamil_site_upgrade_entsperren();
    echo wp_json_encode( $r );
    """
    assert json.loads(wp_cli(code)) == [False, "B", True, None]
