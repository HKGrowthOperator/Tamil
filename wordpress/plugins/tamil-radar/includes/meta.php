<?php
/**
 * Beitrags-Meta des Radars: Quelle, Bildnachweis, Ort, Event- und Kinodaten – alles per REST sichtbar und schreibbar.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Meta-Schlüssel → Typ (text | url | int | datetime | land | json).
 *
 * @return array<string,string>
 */
function tamil_radar_meta_keys(): array {
	return array(
		'radar_uid'      => 'text',
		'radar_relevanz' => 'int',
		'quelle_name'    => 'text',
		'quelle_url'     => 'url',
		'quelle_datum'   => 'datetime',
		'quelle_sprache' => 'text',
		'bild_credit'    => 'text',
		'bild_origin'    => 'text',
		'ort'            => 'text',
		'standfirst'     => 'text',
		'event_datum'    => 'datetime',
		'event_ende'     => 'datetime',
		'event_ort'      => 'text',
		'event_land'     => 'land',
		'ticket_url'     => 'url',
		'kino_fakten'    => 'json',
		'rezept'         => 'json',
	);
}

/**
 * Einen Meta-Wert nach Typ säubern. Unbrauchbares wird leer (bzw. 0).
 *
 * @param mixed  $value Rohwert.
 * @param string $type  Typ aus tamil_radar_meta_keys().
 * @return string|int
 */
function tamil_radar_sanitize_meta( $value, string $type ) {
	switch ( $type ) {
		case 'int':
			return max( 0, min( 10, (int) $value ) );
		case 'url':
			return esc_url_raw( (string) $value );
		case 'datetime':
			$raw = trim( (string) $value );
			if ( '' === $raw ) {
				return '';
			}
			foreach ( array( 'Y-m-d H:i', 'Y-m-d\TH:i', 'Y-m-d\TH:iP', 'Y-m-d\TH:i:sP', 'Y-m-d' ) as $format ) {
				$dt = DateTimeImmutable::createFromFormat( $format, $raw );
				if ( $dt instanceof DateTimeImmutable ) {
					return 'Y-m-d' === $format ? $dt->format( 'Y-m-d' ) : $dt->format( 'Y-m-d H:i' );
				}
			}
			return '';
		case 'land':
			$land = strtoupper( sanitize_text_field( (string) $value ) );
			return in_array( $land, array( 'DE', 'AT', 'CH', 'DACH' ), true ) ? $land : '';
		case 'json':
			if ( is_array( $value ) ) {
				return wp_json_encode( $value, JSON_UNESCAPED_UNICODE );
			}
			$raw = trim( (string) $value );
			if ( '' === $raw ) {
				return '';
			}
			$decoded = json_decode( $raw, true );
			return null === $decoded ? '' : wp_json_encode( $decoded, JSON_UNESCAPED_UNICODE );
		default:
			return sanitize_text_field( (string) $value );
	}
}

/**
 * register_post_meta für alle Radar-Felder (single, REST-sichtbar, nur für Redakteure schreibbar).
 */
function tamil_radar_register_meta(): void {
	foreach ( tamil_radar_meta_keys() as $key => $type ) {
		register_post_meta(
			'post',
			$key,
			array(
				'type'              => 'int' === $type ? 'integer' : 'string',
				'single'            => true,
				'default'           => 'int' === $type ? 0 : '',
				'show_in_rest'      => true,
				'sanitize_callback' => static function ( $value ) use ( $type ) {
					return tamil_radar_sanitize_meta( $value, $type );
				},
				'auth_callback'     => static function () {
					return current_user_can( 'edit_posts' );
				},
			)
		);
	}
}

/**
 * JSON-Meta als Array lesen (leer, wenn nichts oder kaputt).
 *
 * @param int    $post_id Beitrag.
 * @param string $key     Meta-Schlüssel (kino_fakten, rezept).
 * @return array<string,mixed>
 */
function tamil_radar_get_json( int $post_id, string $key ): array {
	$raw = get_post_meta( $post_id, $key, true );
	if ( ! is_string( $raw ) || '' === $raw ) {
		return array();
	}
	$decoded = json_decode( $raw, true );
	return is_array( $decoded ) ? $decoded : array();
}

/**
 * Beitrag zu einer Radar-UID (auch Entwürfe und Papierkorb), sonst 0.
 */
function tamil_radar_post_id_by_uid( string $uid ): int {
	if ( '' === $uid ) {
		return 0;
	}
	$ids = get_posts(
		array(
			'post_type'      => 'post',
			'post_status'    => 'any',
			'posts_per_page' => 1,
			'fields'         => 'ids',
			'meta_key'       => 'radar_uid', // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_key
			'meta_value'     => $uid, // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_value
			'no_found_rows'  => true,
		)
	);
	return $ids ? (int) $ids[0] : 0;
}
