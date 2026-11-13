<?php
/**
 * Deinstallation: Einstellungen und Weiterleitungen entfernen – Beiträge und ihre Meta-Felder bleiben erhalten.
 * Einsendungen (Personendaten) werden mit ihren Bildern und dem Protokoll gelöscht.
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

// Werbebuchung (F3): Angebote und Tabellen. Buchungsdaten unterliegen der steuerlichen Aufbewahrung – vor dem
// Löschen des Plugins exportieren.
delete_option( 'tamil_site_werbung_angebote' );
foreach ( array( 'tamil_werbebuchungen', 'tamil_werbetage', 'tamil_werbestatistik', 'tamil_werbeprotokoll', 'tamil_stripe_ereignisse' ) as $tamil_site_tabelle ) {
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.DirectDatabaseQuery.SchemaChange -- Deinstallation entfernt die eigenen Tabellen
	$wpdb->query( $wpdb->prepare( 'DROP TABLE IF EXISTS %i', $wpdb->prefix . $tamil_site_tabelle ) );
}

// Verzeichnis (F2): Einsendungen mit Personendaten und Protokoll entfernen; Einträge (Beitragstyp) bleiben.
$tamil_site_vz_tabellen = array( $wpdb->prefix . 'tamil_vz_einsendungen', $wpdb->prefix . 'tamil_vz_protokoll' );
foreach ( $tamil_site_vz_tabellen as $tamil_site_vz_tabelle ) {
	$wpdb->query( "DROP TABLE IF EXISTS {$tamil_site_vz_tabelle}" ); // phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.DirectDatabaseQuery.SchemaChange, WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- eigene Tabellen bei der Deinstallation
}
wp_clear_scheduled_hook( 'tamil_site_vz_aufraeumen' );
