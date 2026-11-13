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

// Werbebuchung (F3): Angebote und Tabellen. Buchungsdaten unterliegen der steuerlichen Aufbewahrung – vor dem
// Löschen des Plugins exportieren.
delete_option( 'tamil_site_werbung_angebote' );
global $wpdb;
foreach ( array( 'tamil_werbebuchungen', 'tamil_werbetage', 'tamil_werbestatistik', 'tamil_werbeprotokoll', 'tamil_stripe_ereignisse' ) as $tamil_site_tabelle ) {
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.DirectDatabaseQuery.SchemaChange -- Deinstallation entfernt die eigenen Tabellen
	$wpdb->query( $wpdb->prepare( 'DROP TABLE IF EXISTS %i', $wpdb->prefix . $tamil_site_tabelle ) );
}
