<?php
/**
 * Rolle „Radar“: darf eigene Beiträge anlegen, veröffentlichen, aktualisieren und Bilder hochladen – mehr nicht.
 */

defined( 'ABSPATH' ) || exit;

function tamil_radar_role_caps(): array {
	return array(
		'read'                   => true,
		'edit_posts'             => true,
		'publish_posts'          => true,
		'edit_published_posts'   => true,
		'delete_posts'           => true,
		'upload_files'           => true,
	);
}

function tamil_radar_register_role(): void {
	$role = get_role( 'radar' );
	if ( $role ) {
		foreach ( tamil_radar_role_caps() as $cap => $grant ) {
			if ( $grant && ! $role->has_cap( $cap ) ) {
				$role->add_cap( $cap );
			}
		}
		return;
	}
	add_role( 'radar', __( 'Radar', 'tamil-radar' ), tamil_radar_role_caps() );
}
