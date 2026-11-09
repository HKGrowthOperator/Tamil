<?php
/**
 * Beitrags-Meta der Website: Vorspann, Ort, Veranstaltung, Kinoliste. Redaktion (Eingabemaske) und News-Radar
 * (REST) schreiben dieselben Felder; das Theme liest sie.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Meta-Schlüssel → Typ (text | textarea | url | datetime | land | json).
 *
 * @return array<string,string>
 */
function tamil_site_meta_keys(): array {
	return array(
		'standfirst'         => 'textarea',
		'ort'                => 'text',
		'event_datum'        => 'datetime',
		'event_ende'         => 'datetime',
		'event_ort'          => 'text',
		'event_land'         => 'land',
		'event_veranstalter' => 'text',
		'event_preis'        => 'text',
		'ticket_url'         => 'url',
		'ticket_label'       => 'text',
		'kino_fakten'        => 'json',
	);
}

/**
 * Länder des Veranstaltungskalenders.
 *
 * @return array<string,string>
 */
function tamil_site_laender(): array {
	return array(
		'DE'   => __( 'Deutschland', 'tamil-site' ),
		'AT'   => __( 'Österreich', 'tamil-site' ),
		'CH'   => __( 'Schweiz', 'tamil-site' ),
		'DACH' => __( 'DE · AT · CH', 'tamil-site' ),
	);
}

/**
 * Einen Wert nach Typ säubern; Unbrauchbares wird leer.
 *
 * @param mixed  $value Rohwert.
 * @param string $type  Typ aus tamil_site_meta_keys().
 */
function tamil_site_sanitize_meta( $value, string $type ): string {
	switch ( $type ) {
		case 'url':
			return esc_url_raw( (string) $value );
		case 'textarea':
			return sanitize_textarea_field( (string) $value );
		case 'datetime':
			$raw = trim( (string) $value );
			foreach ( array( 'Y-m-d H:i', 'Y-m-d\TH:i', 'Y-m-d\TH:iP', 'Y-m-d\TH:i:sP', 'Y-m-d' ) as $format ) {
				$dt = '' === $raw ? false : DateTimeImmutable::createFromFormat( $format, $raw );
				if ( $dt instanceof DateTimeImmutable ) {
					return 'Y-m-d' === $format ? $dt->format( 'Y-m-d' ) : $dt->format( 'Y-m-d H:i' );
				}
			}
			return '';
		case 'land':
			$land = strtoupper( sanitize_text_field( (string) $value ) );
			return array_key_exists( $land, tamil_site_laender() ) ? $land : '';
		case 'json':
			if ( is_array( $value ) ) {
				return (string) wp_json_encode( $value, JSON_UNESCAPED_UNICODE );
			}
			$decoded = json_decode( trim( (string) $value ), true );
			return is_array( $decoded ) ? (string) wp_json_encode( $decoded, JSON_UNESCAPED_UNICODE ) : '';
		default:
			return sanitize_text_field( (string) $value );
	}
}

function tamil_site_register_meta(): void {
	foreach ( tamil_site_meta_keys() as $key => $type ) {
		register_post_meta(
			'post',
			$key,
			array(
				'type'              => 'string',
				'single'            => true,
				'default'           => '',
				'show_in_rest'      => true,
				'sanitize_callback' => static function ( $value ) use ( $type ) {
					return tamil_site_sanitize_meta( $value, $type );
				},
				'auth_callback'     => static function ( $allowed, $meta_key, $post_id ) {
					return current_user_can( 'edit_post', (int) $post_id );
				},
			)
		);
	}
}

/**
 * JSON-Meta als Array (leer, wenn nichts oder kaputt).
 *
 * @return array<string|int,mixed>
 */
function tamil_site_get_json( int $post_id, string $key ): array {
	$raw = get_post_meta( $post_id, $key, true );
	if ( is_array( $raw ) ) {
		return $raw;
	}
	$decoded = is_string( $raw ) && '' !== $raw ? json_decode( $raw, true ) : null;
	return is_array( $decoded ) ? $decoded : array();
}
