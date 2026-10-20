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
