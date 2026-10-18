<?php
/**
 * Deinstallation: Optionen, Transients und Rolle entfernen – Beiträge, Bilder und Meta bleiben erhalten.
 */

defined( 'WP_UNINSTALL_PLUGIN' ) || exit;

delete_option( 'tamil_radar_settings' );
delete_option( 'tamil_radar_version' );
delete_transient( 'tamil_radar_cockpit_status' );

// Benutzer der Rolle „Radar“ werden Autoren, damit niemand ohne Rolle zurückbleibt.
foreach ( get_users( array( 'role' => 'radar', 'fields' => 'ID' ) ) as $user_id ) {
	$user = new WP_User( (int) $user_id );
	$user->set_role( 'author' );
}
remove_role( 'radar' );
