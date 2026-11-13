<?php
/**
 * Deinstallation: Einstellungen und Weiterleitungen entfernen – Beiträge und ihre Meta-Felder bleiben erhalten.
 */

defined( 'WP_UNINSTALL_PLUGIN' ) || exit;

delete_option( 'tamil_site_settings' );
delete_option( 'tamil_site_redirects' );
delete_option( 'tamil_site_redirects_csv' );
delete_option( 'tamil_site_funktionen' );
delete_option( 'tamil_site_datenversion' );
delete_option( 'tamil_site_seo' );
delete_option( 'tamil_site_zustimmung' );

// Verzeichnis (F2): Einsendungen mit Personendaten und Protokoll entfernen; Einträge (Beitragstyp) bleiben.
global $wpdb;
$tamil_site_vz_tabellen = array( $wpdb->prefix . 'tamil_vz_einsendungen', $wpdb->prefix . 'tamil_vz_protokoll' );
foreach ( $tamil_site_vz_tabellen as $tamil_site_vz_tabelle ) {
	$wpdb->query( "DROP TABLE IF EXISTS {$tamil_site_vz_tabelle}" ); // phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.DirectDatabaseQuery.SchemaChange, WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- eigene Tabellen bei der Deinstallation
}
wp_clear_scheduled_hook( 'tamil_site_vz_aufraeumen' );
