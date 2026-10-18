<?php
/**
 * Abfragen für das Theme: kommende Events, Kinotermine-Beiträge, Event-Daten eines Beitrags.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Kommende Veranstaltungen (Beiträge mit event_datum ≥ heute), früheste zuerst.
 *
 * @param int   $limit Anzahl.
 * @param array $extra Zusätzliche WP_Query-Argumente (z. B. post__not_in).
 */
function tamil_radar_upcoming_events( int $limit = 6, array $extra = array() ): WP_Query {
	$args = array(
		'post_type'      => 'post',
		'post_status'    => 'publish',
		'posts_per_page' => $limit,
		'no_found_rows'  => true,
		'meta_key'       => 'event_datum', // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_key
		'orderby'        => 'meta_value',
		'order'          => 'ASC',
		'meta_query'     => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
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
 * Beiträge mit Kinoliste (kino_fakten), neueste zuerst.
 */
function tamil_radar_kino_posts( int $limit = 1, array $extra = array() ): WP_Query {
	$args = array(
		'post_type'      => 'post',
		'post_status'    => 'publish',
		'posts_per_page' => $limit,
		'no_found_rows'  => true,
		'meta_query'     => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
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
 * Kinoliste eines Beitrags: {film, woche, kinos:[{kino, stadt, land, termine|von|bis, url, quelle}]}.
 */
function tamil_radar_kino_fakten( int $post_id ): array {
	return tamil_radar_get_json( $post_id, 'kino_fakten' );
}

/**
 * Event-Daten eines Beitrags (leer, wenn kein event_datum gesetzt ist).
 *
 * @return array{datum:string,ende:string,ort:string,land:string,ticket_url:string}|array{}
 */
function tamil_radar_event( int $post_id ): array {
	$datum = (string) get_post_meta( $post_id, 'event_datum', true );
	if ( '' === $datum ) {
		return array();
	}
	return array(
		'datum'      => $datum,
		'ende'       => (string) get_post_meta( $post_id, 'event_ende', true ),
		'ort'        => (string) get_post_meta( $post_id, 'event_ort', true ),
		'land'       => (string) get_post_meta( $post_id, 'event_land', true ),
		'ticket_url' => (string) get_post_meta( $post_id, 'ticket_url', true ),
	);
}

/**
 * Anzahl der Beiträge, die der Radar angelegt hat (radar_uid gesetzt).
 */
function tamil_radar_count_posts( string $status = 'any' ): int {
	$query = new WP_Query(
		array(
			'post_type'      => 'post',
			'post_status'    => $status,
			'posts_per_page' => 1,
			'fields'         => 'ids',
			'meta_query'     => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
				array(
					'key'     => 'radar_uid',
					'value'   => '',
					'compare' => '!=',
				),
			),
		)
	);
	return (int) $query->found_posts;
}
