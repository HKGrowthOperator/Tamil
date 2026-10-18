<?php
/**
 * Auswahl für Startseite, Ticker und „Mehr aus …“. Ergebnisse sind ID-Listen im Transient (10 Minuten) und werden
 * bei jeder Statusänderung eines Beitrags verworfen – die Startseite kostet so wenige Abfragen.
 */

defined( 'ABSPATH' ) || exit;

const TAMIL_HOME_RUBRIKEN = array( 'news', 'kino', 'entertainment', 'community', 'kultur', 'sport' );

/**
 * Beitrags-IDs (veröffentlicht, ohne bereits verwendete).
 *
 * @param array<string,mixed> $args WP_Query-Argumente.
 * @param int[]               $ohne Ausschließen.
 * @return int[]
 */
function tamil_ids( array $args, array $ohne = array() ): array {
	$defaults = array(
		'post_type'           => 'post',
		'post_status'         => 'publish',
		'fields'              => 'ids',
		'no_found_rows'       => true,
		'ignore_sticky_posts' => true,
		'post__not_in'        => array_values( array_unique( array_map( 'intval', $ohne ) ) ),
	);
	$query    = new WP_Query( array_merge( $defaults, $args ) );
	return array_map( 'intval', $query->posts );
}

/**
 * Startseite: Aufmacher, Aktuell (2), Außerdem (4), Top-Themen (5), Rubriken (je 4), Rezept, Production, Kino.
 *
 * @return array{lead:int,aktuell:int[],ausserdem:int[],top:int[],rubriken:array<string,int[]>,rezept:int,production:int[],kino:int}
 */
function tamil_home_auswahl(): array {
	$cached = get_transient( 'tamil_home_auswahl' );
	if ( is_array( $cached ) && isset( $cached['lead'] ) ) {
		return $cached;
	}
	$used     = array();
	$sticky   = array_map( 'intval', (array) get_option( 'sticky_posts', array() ) );
	$mit_bild = array(
		'meta_key' => '_thumbnail_id', // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_key
	);

	// Aufmacher: im Customizer gesetzt, sonst neuester markierter Beitrag mit Bild, sonst neuester mit Bild.
	$lead = absint( tamil_opt( 'aufmacher_id' ) );
	if ( ! $lead || 'publish' !== get_post_status( $lead ) ) {
		$lead = $sticky ? ( tamil_ids(
			array_merge(
				$mit_bild,
				array(
					'post__in'       => $sticky,
					'posts_per_page' => 1,
				)
			)
		)[0] ?? 0 ) : 0;
	}
	if ( ! $lead ) {
		$lead = tamil_ids( array_merge( $mit_bild, array( 'posts_per_page' => 1 ) ) )[0] ?? 0;
	}
	if ( ! $lead ) {
		$lead = tamil_ids( array( 'posts_per_page' => 1 ) )[0] ?? 0;
	}
	$used[] = $lead;

	// Top-Themen: die übrigen markierten Beiträge, aufgefüllt mit den neuesten.
	// post__in schlägt post__not_in in WP_Query – darum die Ausschlüsse hier selbst abziehen.
	$rest = array_values( array_diff( $sticky, $used ) );
	$top  = $rest ? tamil_ids(
		array(
			'post__in'       => $rest,
			'posts_per_page' => 5,
		)
	) : array();
	if ( count( $top ) < 5 ) {
		$top = array_merge( $top, tamil_ids( array( 'posts_per_page' => 5 - count( $top ) ), array_merge( $used, $top ) ) );
	}

	// Aktuell: zwei der neuesten aus verschiedenen Rubriken, dann vier weitere als Liste.
	$aktuell    = array();
	$lead_kat   = $lead ? tamil_hauptkategorie( $lead ) : null;
	$gesehen    = $lead_kat ? array( $lead_kat->term_id ) : array();
	$kandidaten = tamil_ids( array( 'posts_per_page' => 12 ), array_merge( $used, $top ) );
	foreach ( $kandidaten as $id ) {
		$kat = tamil_hauptkategorie( $id );
		if ( $kat && in_array( $kat->term_id, $gesehen, true ) ) {
			continue;
		}
		$aktuell[] = $id;
		$gesehen[] = $kat ? $kat->term_id : 0;
		if ( count( $aktuell ) === 2 ) {
			break;
		}
	}
	foreach ( $kandidaten as $id ) {
		if ( count( $aktuell ) >= 2 ) {
			break;
		}
		if ( ! in_array( $id, $aktuell, true ) ) {
			$aktuell[] = $id;
		}
	}
	$used      = array_merge( $used, $aktuell );
	$ausserdem = tamil_ids( array( 'posts_per_page' => 4 ), array_merge( $used, $top ) );
	$used      = array_merge( $used, $ausserdem, $top );

	// Kino-Schaufenster: neuester Beitrag mit Kinoliste (steht dann nicht noch einmal in der Rubrik).
	$kino = function_exists( 'tamil_site_kino_posts' ) ? ( array_map( 'intval', tamil_site_kino_posts( 1, array( 'fields' => 'ids' ) )->posts )[0] ?? 0 ) : 0;
	if ( $kino ) {
		$used[] = $kino;
	}

	// Rubriken der Startseite, ohne Dubletten.
	$rubriken = array();
	foreach ( TAMIL_HOME_RUBRIKEN as $slug ) {
		$rubriken[ $slug ] = get_category_by_slug( $slug ) ? tamil_ids(
			array(
				'posts_per_page' => 4,
				'category_name'  => $slug,
			),
			$used
		) : array();
		$used              = array_merge( $used, $rubriken[ $slug ] );
	}

	// Rezept der Woche.
	$rezept = absint( tamil_opt( 'rezept_id' ) );
	if ( ! $rezept || 'publish' !== get_post_status( $rezept ) ) {
		$rezept = get_category_by_slug( 'kueche' ) ? ( tamil_ids(
			array(
				'posts_per_page' => 1,
				'category_name'  => 'kueche',
			)
		)[0] ?? 0 ) : 0;
	}

	// Production: Beiträge mit dem Schlagwort aus dem Customizer.
	$tag        = sanitize_title( tamil_opt( 'production_tag' ) );
	$production = '' !== $tag ? tamil_ids(
		array(
			'posts_per_page' => 4,
			'tag'            => $tag,
		)
	) : array();

	$auswahl = array(
		'lead'       => (int) $lead,
		'aktuell'    => $aktuell,
		'ausserdem'  => $ausserdem,
		'top'        => $top,
		'rubriken'   => $rubriken,
		'rezept'     => (int) $rezept,
		'production' => $production,
		'kino'       => (int) $kino,
	);
	set_transient( 'tamil_home_auswahl', $auswahl, 10 * MINUTE_IN_SECONDS );
	return $auswahl;
}

/**
 * Cache verwerfen, sobald sich an Beiträgen oder Einstellungen etwas ändert.
 */
function tamil_flush_auswahl(): void {
	delete_transient( 'tamil_home_auswahl' );
	delete_transient( 'tamil_ticker' );
}
add_action( 'transition_post_status', 'tamil_flush_auswahl' );
add_action( 'deleted_post', 'tamil_flush_auswahl' );
add_action( 'customize_save_after', 'tamil_flush_auswahl' );
add_action( 'update_option_sticky_posts', 'tamil_flush_auswahl' );
add_action( 'updated_post_meta', 'tamil_flush_auswahl_meta', 10, 3 );

function tamil_flush_auswahl_meta( $meta_id, $post_id, $meta_key ): void {
	if ( in_array( $meta_key, array( '_thumbnail_id', 'kino_fakten', 'event_datum' ), true ) ) {
		tamil_flush_auswahl();
	}
}

/**
 * „Mehr aus …“: drei Beiträge der Hauptkategorie, aufgefüllt mit den neuesten.
 *
 * @return int[]
 */
function tamil_related( int $post_id, int $anzahl = 3 ): array {
	$kat = tamil_hauptkategorie( $post_id );
	$ids = $kat ? tamil_ids(
		array(
			'posts_per_page' => $anzahl,
			'cat'            => $kat->term_id,
		),
		array( $post_id )
	) : array();
	if ( count( $ids ) < $anzahl ) {
		$ids = array_merge( $ids, tamil_ids( array( 'posts_per_page' => $anzahl - count( $ids ) ), array_merge( $ids, array( $post_id ) ) ) );
	}
	return $ids;
}

/**
 * Laufband: neueste Kinoliste, drei kommende Termine, sechs neueste Beiträge.
 *
 * @return array<int,array{k:string,text:string,href:string}>
 */
function tamil_ticker(): array {
	$cached = get_transient( 'tamil_ticker' );
	if ( is_array( $cached ) ) {
		return $cached;
	}
	$ids = array();
	if ( function_exists( 'tamil_site_kino_posts' ) ) {
		$ids = array_merge( $ids, array_map( 'intval', tamil_site_kino_posts( 1, array( 'fields' => 'ids' ) )->posts ) );
	}
	if ( function_exists( 'tamil_site_upcoming_events' ) ) {
		$ids = array_merge( $ids, array_map( 'intval', tamil_site_upcoming_events( 3, array( 'fields' => 'ids' ) )->posts ) );
	}
	$ids   = array_merge( $ids, tamil_ids( array( 'posts_per_page' => 6 ), $ids ) );
	$items = array();
	foreach ( array_unique( $ids ) as $id ) {
		$kat     = tamil_hauptkategorie( $id );
		$items[] = array(
			'k'    => $kat ? tamil_rubrik( $kat->slug )['tamil'] : '',
			'text' => html_entity_decode( get_the_title( $id ), ENT_QUOTES, 'UTF-8' ),
			'href' => (string) get_permalink( $id ),
		);
	}
	set_transient( 'tamil_ticker', $items, 10 * MINUTE_IN_SECONDS );
	return $items;
}
