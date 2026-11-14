<?php
/**
 * Deinstallation: Einstellungen und Weiterleitungen entfernen – Beiträge und ihre Meta-Felder bleiben erhalten.
 * Einsendungen (Personendaten) werden mit ihren Bildern und dem Protokoll gelöscht. Bezahlte Werbebuchungen bleiben
 * für die steuerliche Aufbewahrung erhalten (siehe unten).
 */

defined( 'WP_UNINSTALL_PLUGIN' ) || exit;

delete_option( 'tamil_site_settings' );
delete_option( 'tamil_site_redirects' );
delete_option( 'tamil_site_redirects_csv' );
delete_option( 'tamil_site_funktionen' );
delete_option( 'tamil_site_datenversion' );
delete_option( 'tamil_site_seo' );
delete_option( 'tamil_site_zustimmung' );
delete_option( 'tamil_site_einsendungen' );
delete_option( 'tamil_site_einsendungen_fassungen' );
wp_clear_scheduled_hook( 'tamil_site_einsendungen_aufraeumen' );

global $wpdb;
// phpcs:disable WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.DirectDatabaseQuery.SchemaChange -- eigene Tabellen entfernen
$wpdb->query( "DROP TABLE IF EXISTS {$wpdb->prefix}tamil_einsendungen" );
$wpdb->query( "DROP TABLE IF EXISTS {$wpdb->prefix}tamil_einsendungen_protokoll" );
// phpcs:enable
$tamil_site_einsendungen_ordner = trailingslashit( defined( 'TAMIL_SITE_EINSENDUNG_ORDNER' ) ? (string) TAMIL_SITE_EINSENDUNG_ORDNER : wp_upload_dir( null, false )['basedir'] . '/tamil-einsendungen' );
if ( is_dir( $tamil_site_einsendungen_ordner ) ) {
	foreach ( (array) scandir( $tamil_site_einsendungen_ordner ) as $tamil_site_datei ) {
		if ( is_file( $tamil_site_einsendungen_ordner . $tamil_site_datei ) ) {
			wp_delete_file( $tamil_site_einsendungen_ordner . $tamil_site_datei );
		}
	}
	rmdir( $tamil_site_einsendungen_ordner ); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_system_operations_rmdir -- leerer eigener Ordner
}

// Werbebuchung (F3). Bezahlte (auch erstattete) Buchungen sind steuerlich aufzubewahren: Gibt es sie, bleiben die
// Tabellen der Buchungen und ihres Protokolls stehen; nur nie bezahlte Buchungen (mit ihren Personendaten) und die
// Betriebstabellen werden entfernt. Alles löschen nur mit der ausdrücklichen Option
// `tamil_site_werbung_deinstallation_loeschen` (z. B. `wp option update tamil_site_werbung_deinstallation_loeschen 1`
// nach dem Export). Der Hinweis steht in wp-admin unter Werbung.
delete_option( 'tamil_site_werbung_angebote' );
$tamil_site_werbung_alles  = (bool) get_option( 'tamil_site_werbung_deinstallation_loeschen', false );
$tamil_site_werbebuchungen = $wpdb->prefix . 'tamil_werbebuchungen';
$tamil_site_werbeprotokoll = $wpdb->prefix . 'tamil_werbeprotokoll';
// phpcs:disable WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.DirectDatabaseQuery.SchemaChange -- Deinstallation, eigene Tabellen
$tamil_site_werbung_bezahlt  = $wpdb->get_var( $wpdb->prepare( 'SHOW TABLES LIKE %s', $tamil_site_werbebuchungen ) ) === $tamil_site_werbebuchungen
	? (int) $wpdb->get_var( $wpdb->prepare( "SELECT COUNT(*) FROM %i WHERE zahlung IN ('bezahlt', 'erstattet')", $tamil_site_werbebuchungen ) )
	: 0;
$tamil_site_werbung_behalten = $tamil_site_werbung_bezahlt > 0 && ! $tamil_site_werbung_alles;
$tamil_site_werbetabellen    = array( 'tamil_werbetage', 'tamil_werbestatistik', 'tamil_stripe_ereignisse' );
if ( $tamil_site_werbung_behalten ) {
	$wpdb->query( $wpdb->prepare( "DELETE FROM %i WHERE buchung_id IN ( SELECT id FROM %i WHERE zahlung NOT IN ('bezahlt', 'erstattet') )", $tamil_site_werbeprotokoll, $tamil_site_werbebuchungen ) );
	$wpdb->query( $wpdb->prepare( "DELETE FROM %i WHERE zahlung NOT IN ('bezahlt', 'erstattet')", $tamil_site_werbebuchungen ) );
} else {
	$tamil_site_werbetabellen[] = 'tamil_werbebuchungen';
	$tamil_site_werbetabellen[] = 'tamil_werbeprotokoll';
}
foreach ( $tamil_site_werbetabellen as $tamil_site_tabelle ) {
	$wpdb->query( $wpdb->prepare( 'DROP TABLE IF EXISTS %i', $wpdb->prefix . $tamil_site_tabelle ) );
}
// phpcs:enable
delete_option( 'tamil_site_werbung_deinstallation_loeschen' );

// Verzeichnis (F2): Einsendungen mit Personendaten und Protokoll entfernen; Einträge (Beitragstyp) bleiben.
$tamil_site_vz_tabellen = array( $wpdb->prefix . 'tamil_vz_einsendungen', $wpdb->prefix . 'tamil_vz_protokoll' );
foreach ( $tamil_site_vz_tabellen as $tamil_site_vz_tabelle ) {
	$wpdb->query( "DROP TABLE IF EXISTS {$tamil_site_vz_tabelle}" ); // phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.DirectDatabaseQuery.SchemaChange, WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- eigene Tabellen bei der Deinstallation
}
wp_clear_scheduled_hook( 'tamil_site_vz_aufraeumen' );
