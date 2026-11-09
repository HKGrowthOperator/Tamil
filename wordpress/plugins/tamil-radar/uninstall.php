<?php
/**
 * Deinstallation: Optionen, Transients und Rolle entfernen – Beiträge, Bilder und Meta bleiben erhalten.
 */

defined( 'WP_UNINSTALL_PLUGIN' ) || exit;

delete_option( 'tamil_radar_settings' );
delete_option( 'tamil_radar_version' );
delete_transient( 'tamil_radar_cockpit_status' );

// Benutzer der Rolle „Radar“ werden Autoren, damit niemand ohne Rolle zurückbleibt.
$tamil_radar_users = get_users(
	array(
		'role'   => 'radar',
		'fields' => 'ID',
	)
);
foreach ( $tamil_radar_users as $tamil_radar_user_id ) {
	( new WP_User( (int) $tamil_radar_user_id ) )->set_role( 'author' );
}
remove_role( 'radar' );
