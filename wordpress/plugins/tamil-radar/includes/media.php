<?php
/**
 * Beitragsbild aus Base64-Daten in die Mediathek: Datei, Anhang, Metadaten, Alt-Text, Bildnachweis.
 */

defined( 'ABSPATH' ) || exit;

/**
 * @param string $b64      Base64-kodierte JPEG/PNG/WebP-Daten.
 * @param string $filename Gewünschter Dateiname (wird gesäubert).
 * @param string $alt      Alt-Text.
 * @param string $credit   Bildnachweis (wird Caption und Meta bild_credit).
 * @param int    $post_id  Beitrag, dem das Bild gehört.
 * @return int|WP_Error Attachment-ID.
 */
function tamil_radar_sideload_base64( string $b64, string $filename, string $alt, string $credit, int $post_id ) {
	$bytes = base64_decode( $b64, true ); // phpcs:ignore WordPress.PHP.DiscouragedPHPFunctions.obfuscation_base64_decode
	if ( false === $bytes || strlen( $bytes ) < 200 ) {
		return new WP_Error( 'tamil_radar_bild', __( 'Bilddaten unlesbar (Base64 erwartet).', 'tamil-radar' ), array( 'status' => 400 ) );
	}
	if ( strlen( $bytes ) > 15 * MB_IN_BYTES ) {
		return new WP_Error( 'tamil_radar_bild', __( 'Bild größer als 15 MB.', 'tamil-radar' ), array( 'status' => 413 ) );
	}
	$filename = sanitize_file_name( '' !== $filename ? $filename : 'radar-' . $post_id . '.jpg' );
	$upload   = wp_upload_bits( $filename, null, $bytes );
	if ( ! empty( $upload['error'] ) ) {
		return new WP_Error( 'tamil_radar_bild', (string) $upload['error'], array( 'status' => 500 ) );
	}
	$check = wp_check_filetype_and_ext( $upload['file'], $filename );
	if ( ! in_array( $check['type'], array( 'image/jpeg', 'image/png', 'image/webp' ), true ) ) {
		wp_delete_file( $upload['file'] );
		return new WP_Error( 'tamil_radar_bild', __( 'Nur JPEG, PNG oder WebP.', 'tamil-radar' ), array( 'status' => 415 ) );
	}
	require_once ABSPATH . 'wp-admin/includes/image.php';
	$attachment_id = wp_insert_attachment(
		array(
			'post_mime_type' => $check['type'],
			'post_title'     => sanitize_text_field( pathinfo( $filename, PATHINFO_FILENAME ) ),
			'post_excerpt'   => sanitize_text_field( $credit ), // Caption = Bildnachweis
			'post_content'   => '',
			'post_status'    => 'inherit',
		),
		$upload['file'],
		$post_id,
		true
	);
	if ( is_wp_error( $attachment_id ) ) {
		wp_delete_file( $upload['file'] );
		return $attachment_id;
	}
	wp_update_attachment_metadata( $attachment_id, wp_generate_attachment_metadata( $attachment_id, $upload['file'] ) );
	update_post_meta( $attachment_id, '_wp_attachment_image_alt', sanitize_text_field( $alt ) );
	update_post_meta( $attachment_id, 'bild_credit', sanitize_text_field( $credit ) );
	return (int) $attachment_id;
}

/**
 * Bildnachweis eines Beitrags: Meta am Beitrag, sonst Caption/Meta des Beitragsbilds.
 */
function tamil_radar_bildnachweis( int $post_id ): string {
	$credit = (string) get_post_meta( $post_id, 'bild_credit', true );
	if ( '' !== $credit ) {
		return $credit;
	}
	$thumb = get_post_thumbnail_id( $post_id );
	if ( ! $thumb ) {
		return '';
	}
	$credit = (string) get_post_meta( $thumb, 'bild_credit', true );
	if ( '' !== $credit ) {
		return $credit;
	}
	$attachment = get_post( $thumb );
	return $attachment ? (string) $attachment->post_excerpt : '';
}
