<?php
/**
 * Navigation: Einträge aus dem Menü „Hauptnavigation“, sonst aus den Rubriken. Hauptleiste und mobiles Menü
 * nutzen dieselbe Liste; Rubriken bekommen im mobilen Menü ihr tamilisches Wort.
 */

defined( 'ABSPATH' ) || exit;

/**
 * @return array<int,array{label:string,url:string,aktiv:bool,tamil:string}>
 */
function tamil_nav_items(): array {
	$items     = array();
	$locations = get_nav_menu_locations();
	if ( ! empty( $locations['haupt'] ) ) {
		foreach ( (array) wp_get_nav_menu_items( $locations['haupt'] ) as $item ) {
			if ( (int) $item->menu_item_parent ) {
				continue;
			}
			$tamil = '';
			if ( 'taxonomy' === $item->type && 'category' === $item->object ) {
				$term  = get_term( (int) $item->object_id, 'category' );
				$tamil = $term instanceof WP_Term ? tamil_rubrik( $term->slug )['tamil'] : '';
			}
			$items[] = array(
				'label' => $item->title,
				'url'   => $item->url,
				'aktiv' => tamil_nav_aktiv( $item->url ),
				'tamil' => $tamil,
			);
		}
		return $items;
	}
	foreach ( array( 'news', 'entertainment', 'events', 'community', 'kueche', 'kino', 'sport', 'kultur' ) as $slug ) {
		$rubrik = tamil_rubrik( $slug );
		if ( ! $rubrik['term'] && 'events' !== $slug ) {
			continue;
		}
		$items[] = array(
			'label' => $rubrik['label'],
			'url'   => $rubrik['url'],
			'aktiv' => tamil_nav_aktiv( $rubrik['url'] ) || ( is_category( $slug ) ),
			'tamil' => $rubrik['tamil'],
		);
	}
	$kontakt = tamil_seite( 'kontakt' );
	if ( $kontakt ) {
		$items[] = array(
			'label' => get_the_title( $kontakt ),
			'url'   => (string) get_permalink( $kontakt ),
			'aktiv' => is_page( $kontakt->ID ),
			'tamil' => 'தொடர்பு',
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
