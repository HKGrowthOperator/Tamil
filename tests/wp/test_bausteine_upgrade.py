"""Plugin tamil-site: Zusammenspiel der Bausteine in der Upgrade-Routine (F1 = 2, F3 = 3, F2 = 4).

Prüft gegen das lokale WordPress, dass jede Schrittnummer genau einmal vergeben ist und eine ältere Installation
beim Nachholen alle fehlenden Tabellen bekommt, ohne die schon vorhandenen anzufassen.
"""

import json

TABELLEN_F1 = ["tamil_einsendungen", "tamil_einsendungen_protokoll"]
TABELLEN_F3 = ["tamil_werbebuchungen", "tamil_werbetage", "tamil_werbestatistik", "tamil_werbeprotokoll",
               "tamil_stripe_ereignisse"]
TABELLEN_F2 = ["tamil_vz_einsendungen", "tamil_vz_protokoll"]


def _json(wp_cli, code: str):
    return json.loads(wp_cli(code))


def _php_liste(namen: list[str]) -> str:
    return "array( " + ", ".join(f"'{n}'" for n in namen) + " )"


# PHP: welche der Tabellen gibt es (Name → bool)?
_VORHANDEN = r"""
function tamil_test_vorhanden( array $namen ): array {
    global $wpdb;
    $r = array();
    foreach ( $namen as $n ) {
        $t       = $wpdb->prefix . $n;
        $r[ $n ] = $wpdb->get_var( $wpdb->prepare( 'SHOW TABLES LIKE %s', $t ) ) === $t;
    }
    return $r;
}
function tamil_test_entfernen( array $namen ): void {
    global $wpdb;
    foreach ( $namen as $n ) {
        $wpdb->query( $wpdb->prepare( 'DROP TABLE IF EXISTS %i', $wpdb->prefix . $n ) );
    }
}
"""


def test_schrittnummern_eindeutig_und_hoechstens_datenversion(wp_cli):
    r = _json(wp_cli, """$s = array();
        foreach ( tamil_site_upgrade_register()['schritte'] as $x ) { $s[] = array( $x['version'], $x['name'] ); }
        echo wp_json_encode( array( 'version' => TAMIL_SITE_DATENVERSION, 'schritte' => $s ) );""")
    nummern = [n for n, _ in r["schritte"]]
    assert r["version"] == 4
    assert len(nummern) == len(set(nummern)), f"Schrittnummer doppelt: {r['schritte']}"
    assert all(1 <= n <= r["version"] for n in nummern), r["schritte"]
    assert dict((name, n) for n, name in r["schritte"]) == {"einsendungen": 2, "werbung": 3, "verzeichnis": 4}


def test_upgrade_von_1_legt_alle_tabellen_an(wp_cli):
    alle = TABELLEN_F1 + TABELLEN_F3 + TABELLEN_F2
    r = _json(wp_cli, _VORHANDEN + f"""
        tamil_test_entfernen( {_php_liste(alle)} );
        $vorher = tamil_test_vorhanden( {_php_liste(alle)} );
        update_option( 'tamil_site_datenversion', 1 );
        $ok = tamil_site_upgrade_ausfuehren();
        echo wp_json_encode( array( 'ok' => $ok, 'vorher' => $vorher, 'nachher' => tamil_test_vorhanden( {_php_liste(alle)} ),
            'version' => (int) get_option( 'tamil_site_datenversion' ) ) );""")
    assert r["ok"] is True
    assert not any(r["vorher"].values())
    assert all(r["nachher"].values()), r["nachher"]
    assert r["version"] == 4


def test_upgrade_von_2_ergaenzt_werbung_und_verzeichnis(wp_cli):
    """Installation mit nur F1 (Datenversion 2): Werbe- und Verzeichnistabellen kommen dazu, F1 bleibt unberührt."""
    neu = TABELLEN_F3 + TABELLEN_F2
    r = _json(wp_cli, _VORHANDEN + f"""
        global $wpdb;
        tamil_site_upgrade_ausfuehren();
        $t = tamil_site_einsendung_tabelle();
        $wpdb->query( $wpdb->prepare( 'DELETE FROM %i WHERE vorgangsnummer = %s', $t, 'T000000-UPGR2' ) );
        $wpdb->insert( $t, array( 'vorgangsnummer' => 'T000000-UPGR2', 'art' => 'kontakt', 'status' => 'eingegangen',
            'eingang_at' => gmdate( 'Y-m-d H:i:s' ), 'name' => 'Test', 'email' => 'test@example.org', 'felder' => '{{}}',
            'einwilligung_fassung' => 'test' ) );
        $merker = (int) $wpdb->get_var( $wpdb->prepare( 'SELECT COUNT(*) FROM %i WHERE vorgangsnummer = %s', $t, 'T000000-UPGR2' ) );
        tamil_test_entfernen( {_php_liste(neu)} );
        update_option( 'tamil_site_datenversion', 2 );
        $vorher = tamil_test_vorhanden( {_php_liste(neu)} );
        $ok     = tamil_site_upgrade_ausfuehren();
        $danach = (int) $wpdb->get_var( $wpdb->prepare( 'SELECT COUNT(*) FROM %i WHERE vorgangsnummer = %s', $t, 'T000000-UPGR2' ) );
        $wpdb->query( $wpdb->prepare( 'DELETE FROM %i WHERE vorgangsnummer = %s', $t, 'T000000-UPGR2' ) );
        echo wp_json_encode( array( 'ok' => $ok, 'merker' => array( $merker, $danach ), 'vorher' => $vorher,
            'nachher' => tamil_test_vorhanden( {_php_liste(neu + TABELLEN_F1)} ),
            'version' => (int) get_option( 'tamil_site_datenversion' ),
            'rechte' => array( get_role( 'administrator' )->has_cap( 'tamil_werbung_verwalten' ),
                get_role( 'radar' ) && get_role( 'radar' )->has_cap( 'tamil_verzeichnis_pflegen' ),
                get_role( 'radar' ) && get_role( 'radar' )->has_cap( 'tamil_einsendungen_abholen' ) ) ) );""")
    assert r["ok"] is True
    assert r["merker"] == [1, 1], "Einsendung aus F1 darf beim Nachholen nicht verloren gehen"
    assert not any(r["vorher"].values())
    assert all(r["nachher"].values()), r["nachher"]
    assert r["version"] == 4
    assert r["rechte"] == [True, True, True]
