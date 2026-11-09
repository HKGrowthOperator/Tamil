<?php
/**
 * Abfragen fürs Theme: kommende Veranstaltungen, Beiträge mit Kinoliste, Termin-Angaben eines Beitrags.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Kommende Veranstaltungen (event_datum ab heute), früheste zuerst.
 *
 * @param int   $limit Anzahl (-1 = alle).
 * @param array $extra Weitere WP_Query-Argumente.
 */
function tamil_site_upcoming_events( int $limit = 6, array $extra = array() ): WP_Query {
	$args = array(
		'post_type'           => 'post',
		'post_status'         => 'publish',
		'posts_per_page'      => $limit,
		'no_found_rows'       => true,
		'ignore_sticky_posts' => true,
		'meta_key'            => 'event_datum', // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_key
		'orderby'             => 'meta_value',
		'order'               => 'ASC',
		'meta_query'          => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
			array(
				'key'     => 'event_datum',
				'value'   => current_time( 'Y-m-d' ),
				'compare' => '>=',
				'type'    => 'CHAR',
			),
		),
	);
	return new WP_Query( array_merge( $args, $extra ) );
}

/**
 * Beiträge mit Kinoliste, neueste zuerst.
 */
function tamil_site_kino_posts( int $limit = 1, array $extra = array() ): WP_Query {
	$args = array(
		'post_type'           => 'post',
		'post_status'         => 'publish',
		'posts_per_page'      => $limit,
		'no_found_rows'       => true,
		'ignore_sticky_posts' => true,
		'meta_query'          => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
			array(
				'key'     => 'kino_fakten',
				'value'   => '',
				'compare' => '!=',
			),
		),
	);
	return new WP_Query( array_merge( $args, $extra ) );
}

/**
 * Kinoliste: {film, woche, kinos:[{kino, stadt, land, termine[]|von|bis, url, quelle}]}.
 */
function tamil_site_kino_fakten( int $post_id ): array {
	return tamil_site_get_json( $post_id, 'kino_fakten' );
}

/**
 * Termin-Angaben eines Beitrags; leer, wenn kein event_datum gesetzt ist.
 *
 * @return array<string,string>
 */
function tamil_site_event( int $post_id ): array {
	$datum = (string) get_post_meta( $post_id, 'event_datum', true );
	if ( '' === $datum ) {
		return array();
	}
	$out = array( 'datum' => $datum );
	foreach ( array(
		'event_ende'         => 'ende',
		'event_ort'          => 'ort',
		'event_land'         => 'land',
		'event_veranstalter' => 'veranstalter',
		'event_preis'        => 'preis',
		'ticket_url'         => 'ticket_url',
		'ticket_label'       => 'ticket_label',
	) as $key => $name ) {
		$out[ $name ] = (string) get_post_meta( $post_id, $key, true );
	}
	return $out;
}
