"""Plugin tamil-site: Deinstallation und steuerliche Aufbewahrung der Werbebuchungen (F3).

Führt uninstall.php im lokalen WordPress wirklich aus. Vorher werden alle Optionen `tamil_site_*` gesichert, danach
zurückgeschrieben und die Tabellen über die Upgrade-Routine neu angelegt, damit die übrigen Tests weiterlaufen.
"""

import json

import pytest

_RAHMEN = r"""
global $wpdb;
$sicher = $wpdb->get_results( $wpdb->prepare( 'SELECT option_name, option_value, autoload FROM %i WHERE option_name LIKE %s', $wpdb->options, 'tamil\_site\_%' ), ARRAY_A );
$b = tamil_site_werbung_tabelle( 'buchungen' );
$p = tamil_site_werbung_tabelle( 'protokoll' );
$wpdb->query( $wpdb->prepare( 'DELETE FROM %i WHERE nummer LIKE %s', $b, 'WTEST-%' ) );
$neu = function ( string $nummer, string $zahlung ) use ( $wpdb, $b, $p ) {
    $wpdb->insert( $b, array( 'nummer' => $nummer, 'platz' => 'footer', 'laufzeit' => 7, 'start' => '2099-01-01',
        'ende' => '2099-01-07', 'reserviert_bis' => gmdate( 'Y-m-d H:i:s' ), 'firma' => 'Testfirma',
        'rechnungsadresse' => 'Teststr. 1', 'email' => 'test@example.org', 'zahlung' => $zahlung,
        'ablehnungsgrund' => '', 'warnung' => '', 'erstellt_at' => gmdate( 'Y-m-d H:i:s' ) ) );
    $id = (int) $wpdb->insert_id;
    $wpdb->insert( $p, array( 'buchung_id' => $id, 'zeit' => gmdate( 'Y-m-d H:i:s' ), 'wer' => 'test', 'was' => 'angelegt' ) );
    return $id;
};
{{VORBEREITEN}}
define( 'WP_UNINSTALL_PLUGIN', 'tamil-site/tamil-site.php' );
include WP_PLUGIN_DIR . '/tamil-site/uninstall.php';
$da = function ( string $name ) use ( $wpdb ) {
    $t = $wpdb->prefix . $name;
    return $wpdb->get_var( $wpdb->prepare( 'SHOW TABLES LIKE %s', $t ) ) === $t;
};
$r = array( 'tabellen' => array(), 'nummern' => array(), 'protokoll' => 0 );
foreach ( array( 'tamil_werbebuchungen', 'tamil_werbeprotokoll', 'tamil_werbetage', 'tamil_werbestatistik', 'tamil_stripe_ereignisse' ) as $n ) {
    $r['tabellen'][ $n ] = $da( $n );
}
if ( $r['tabellen']['tamil_werbebuchungen'] ) {
    $r['nummern'] = $wpdb->get_col( $wpdb->prepare( 'SELECT nummer FROM %i WHERE nummer LIKE %s ORDER BY nummer', $b, 'WTEST-%' ) );
}
if ( $r['tabellen']['tamil_werbeprotokoll'] && $r['tabellen']['tamil_werbebuchungen'] ) {
    $r['protokoll'] = (int) $wpdb->get_var( $wpdb->prepare( 'SELECT COUNT(*) FROM %i x JOIN %i y ON y.id = x.buchung_id WHERE y.nummer LIKE %s', $p, $b, 'WTEST-%' ) );
}
$r['option_weg'] = false === get_option( 'tamil_site_werbung_deinstallation_loeschen', false );
// Zurück auf den alten Stand: Optionen, dann Tabellen über die Upgrade-Routine, Testzeilen weg.
foreach ( $sicher as $zeile ) {
    $wpdb->replace( $wpdb->options, $zeile );
}
wp_cache_flush();
delete_option( 'tamil_site_werbung_deinstallation_loeschen' );
delete_option( 'tamil_site_datenversion' );
$r['upgrade'] = tamil_site_upgrade_ausfuehren();
$wpdb->query( $wpdb->prepare( 'DELETE FROM %i WHERE buchung_id IN ( SELECT id FROM %i WHERE nummer LIKE %s )', $p, $b, 'WTEST-%' ) );
$wpdb->query( $wpdb->prepare( 'DELETE FROM %i WHERE nummer LIKE %s', $b, 'WTEST-%' ) );
echo wp_json_encode( $r );
"""


def _deinstallieren(wp_cli, vorbereiten: str):
    r = json.loads(wp_cli(_RAHMEN.replace("{{VORBEREITEN}}", vorbereiten)))
    assert r["upgrade"] is True, "Wiederherstellen nach der Deinstallation gescheitert"
    return r


@pytest.fixture
def ohne_fremde_buchungen(wp_cli):
    """Die Szenarien brauchen eine bekannte Lage: bezahlte Buchungen aus anderen Tests würden das Ergebnis ändern."""
    n = int(wp_cli("global $wpdb; echo (int) $wpdb->get_var( $wpdb->prepare( \"SELECT COUNT(*) FROM %i WHERE zahlung IN ('bezahlt', 'erstattet') AND nummer NOT LIKE %s\", tamil_site_werbung_tabelle( 'buchungen' ), 'WTEST-%' ) );"))
    if n:
        pytest.skip(f"{n} bezahlte Buchungen aus anderen Tests vorhanden")


def test_bezahlte_buchungen_bleiben_bei_deinstallation(wp_cli):
    r = _deinstallieren(wp_cli, "$neu( 'WTEST-1-BEZ', 'bezahlt' ); $neu( 'WTEST-2-ERS', 'erstattet' ); $neu( 'WTEST-3-OFF', 'offen' ); $neu( 'WTEST-4-FEH', 'fehlgeschlagen' );")
    t = r["tabellen"]
    assert t["tamil_werbebuchungen"] and t["tamil_werbeprotokoll"], "Buchungen und Protokoll müssen bleiben"
    assert not (t["tamil_werbetage"] or t["tamil_werbestatistik"] or t["tamil_stripe_ereignisse"])
    assert r["nummern"] == ["WTEST-1-BEZ", "WTEST-2-ERS"], "nie bezahlte Buchungen (Personendaten) werden entfernt"
    assert r["protokoll"] == 2


def test_alles_loeschen_nur_mit_ausdruecklicher_option(wp_cli):
    r = _deinstallieren(wp_cli, "$neu( 'WTEST-1-BEZ', 'bezahlt' ); update_option( 'tamil_site_werbung_deinstallation_loeschen', 1 );")
    assert not any(r["tabellen"].values()), r["tabellen"]
    assert r["option_weg"] is True


def test_ohne_bezahlte_buchungen_wird_alles_entfernt(wp_cli, ohne_fremde_buchungen):
    r = _deinstallieren(wp_cli, "$neu( 'WTEST-3-OFF', 'offen' );")
    assert not any(r["tabellen"].values()), r["tabellen"]


def test_hinweis_in_wp_admin(wp_cli):
    r = json.loads(wp_cli("""$a = tamil_site_werbung_deinstallation_hinweis();
        update_option( 'tamil_site_werbung_deinstallation_loeschen', 1 );
        $b = tamil_site_werbung_deinstallation_hinweis();
        delete_option( 'tamil_site_werbung_deinstallation_loeschen' );
        echo wp_json_encode( array( $a, $b ) );"""))
    assert "steuerlich" in r[0] and "bleiben" in r[0]
    assert "Achtung" in r[1] and "auch die bezahlten" in r[1]
