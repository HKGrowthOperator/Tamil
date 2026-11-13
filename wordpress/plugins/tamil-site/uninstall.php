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
