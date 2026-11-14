<?php
/**
 * Navigation: Einträge aus dem Menü „Hauptnavigation“, sonst aus den Rubriken. Kopfleiste, Rubrik-Leiste (mobil)
 * und Menü nutzen dieselbe Liste.
 */

defined( 'ABSPATH' ) || exit;

/**
 * @return array<int,array{label:string,url:string,aktiv:bool,slug:string}>
 */
function tamil_nav_items(): array {
	$items     = array();
	$locations = get_nav_menu_locations();
	if ( ! empty( $locations['haupt'] ) ) {
		foreach ( (array) wp_get_nav_menu_items( $locations['haupt'] ) as $item ) {
			if ( (int) $item->menu_item_parent ) {
				continue;
			}
			$slug = '';
			if ( 'taxonomy' === $item->type && 'category' === $item->object ) {
				$term = get_term( (int) $item->object_id, 'category' );
				$slug = $term instanceof WP_Term ? $term->slug : '';
			}
			$items[] = array(
				'label' => $item->title,
				'url'   => $item->url,
				'aktiv' => tamil_nav_aktiv( $item->url ),
				'slug'  => $slug,
			);
		}
		return $items;
	}
	foreach ( array( 'news', 'kino', 'events', 'community', 'entertainment', 'kueche', 'kultur', 'sport' ) as $slug ) {
		$rubrik = tamil_rubrik( $slug );
		if ( ! $rubrik['term'] && 'events' !== $slug ) {
			continue;
		}
		$items[] = array(
			'label' => $rubrik['label'],
			'url'   => $rubrik['url'],
			'aktiv' => tamil_nav_aktiv( $rubrik['url'] ) || ( is_category( $slug ) ),
			'slug'  => $slug,
		);
	}
	return $items;
}

/**
 * Ist die URL die aktuelle Seite (oder die Rubrik des aktuellen Beitrags)?
 */
function tamil_nav_aktiv( string $url ): bool {
	$jetzt = trailingslashit( strtok( (string) home_url( add_query_arg( array() ) ), '?' ) );
	if ( trailingslashit( $url ) === $jetzt ) {
		return true;
	}
	if ( is_singular( 'post' ) ) {
		$kat = tamil_hauptkategorie( (int) get_queried_object_id() );
		return $kat && trailingslashit( (string) get_category_link( $kat ) ) === trailingslashit( $url );
	}
	return false;
}

/**
 * Die vier Ziele im Kopf (Termine, Kino, Community, Verzeichnis). Ist das Menü „Hauptnavigation“ gesetzt, kommen
 * seine ersten vier Einträge; sonst die Rubriken und Seiten, die es gibt. „breit“ heißt: am Handy nur im Menü.
 *
 * @return array<int,array{label:string,url:string,aktiv:bool,breit:bool,dienst:bool}>
 */
function tamil_kopf_ziele(): array {
	$ziele     = array();
	$locations = get_nav_menu_locations();
	if ( ! empty( $locations['haupt'] ) ) {
		foreach ( array_slice( tamil_nav_items(), 0, 4 ) as $i => $item ) {
			$ziele[] = array(
				'label'  => $item['label'],
				'url'    => $item['url'],
				'aktiv'  => $item['aktiv'],
				'breit'  => $i >= 2,
				'dienst' => false,
			);
		}
		return $ziele;
	}
	$events = tamil_seite( 'events' );
	if ( $events ) {
		$ziele[] = array(
			'label'  => __( 'Termine', 'tamil' ),
			'url'    => (string) get_permalink( $events ),
			'aktiv'  => is_page( 'events' ),
			'breit'  => false,
			'dienst' => true,
		);
	}
	foreach ( array( 'kino', 'community' ) as $slug ) {
		$rubrik = tamil_rubrik( $slug );
		if ( $rubrik['term'] ) {
			$ziele[] = array(
				'label'  => $rubrik['label'],
				'url'    => $rubrik['url'],
				'aktiv'  => is_category( $slug ) || ( is_singular( 'post' ) && tamil_nav_aktiv( $rubrik['url'] ) ),
				'breit'  => 'community' === $slug,
				'dienst' => 'kino' === $slug,
			);
		}
	}
	$verzeichnis = tamil_seite( 'verzeichnis' );
	if ( $verzeichnis ) {
		$ziele[] = array(
			'label'  => __( 'Verzeichnis', 'tamil' ),
			'url'    => (string) get_permalink( $verzeichnis ),
			'aktiv'  => is_page( 'verzeichnis' ),
			'breit'  => true,
			'dienst' => true,
		);
	}
	return $ziele;
}

/**
 * Dienste für das Menü „Mehr“ und den Fuß: Termin einreichen, Werben und die Seiten, die es gibt.
 *
 * @return array<int,array{label:string,url:string,aktiv:bool}>
 */
function tamil_dienste(): array {
	$dienste = array(
		array(
			'label' => __( 'Termin einreichen', 'tamil' ),
			'url'   => tamil_seiten_url( 'kontakt', 'event-einreichen' ),
			'aktiv' => false,
		),
		array(
			'label' => __( 'Werben', 'tamil' ),
			'url'   => tamil_seite( 'werben' ) ? tamil_seiten_url( 'werben' ) : tamil_seiten_url( 'kontakt', 'werben' ),
			'aktiv' => is_page( 'werben' ),
		),
	);
	foreach ( array(
		'production' => tamil_opt( 'production_titel' ),
		'tv'         => __( 'Tamil TV', 'tamil' ),
		'ueber-uns'  => __( 'Über Tamil.de', 'tamil' ),
		'kontakt'    => __( 'Kontakt', 'tamil' ),
	) as $slug => $label ) {
		if ( tamil_seite( $slug ) ) {
			$dienste[] = array(
				'label' => $label,
				'url'   => tamil_seiten_url( $slug ),
				'aktiv' => is_page( $slug ),
			);
		}
	}
	return $dienste;
}
