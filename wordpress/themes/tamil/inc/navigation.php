<?php
/**
 * Navigation: das rote Rubrikband (Einträge aus dem Menü „Hauptnavigation“, sonst die Rubriken in der Reihenfolge
 * von klar2 und „Kontakt“) und die Dienste für „Mehr“ und den Fuß.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Einträge des Rubrikbands.
 *
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
				'aktiv' => tamil_nav_aktiv( $item->url ) || ( '' !== $slug && is_category( $slug ) ),
				'slug'  => $slug,
			);
		}
		return $items;
	}
	foreach ( array( 'news', 'entertainment', 'events', 'community', 'kueche', 'kino', 'sport', 'kultur' ) as $slug ) {
		$rubrik = tamil_rubrik( $slug );
		if ( ! $rubrik['term'] && ! ( 'events' === $slug && tamil_seite( 'events' ) ) ) {
			continue;
		}
		$items[] = array(
			'label' => $rubrik['label'],
			'url'   => $rubrik['url'],
			'aktiv' => tamil_nav_aktiv( $rubrik['url'] ) || is_category( $slug ) || ( 'events' === $slug && is_page( 'events' ) ),
			'slug'  => $slug,
		);
	}
	if ( tamil_seite( 'kontakt' ) ) {
		$items[] = array(
			'label' => __( 'Kontakt', 'tamil' ),
			'url'   => tamil_seiten_url( 'kontakt' ),
			'aktiv' => is_page( 'kontakt' ),
			'slug'  => '',
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
 * Dienste für „Mehr“ und den Fuß: Termin einreichen, Werben und die Seiten, die es gibt.
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
		'verzeichnis' => __( 'Verzeichnis', 'tamil' ),
		'production'  => tamil_opt( 'production_titel' ),
		'tv'          => __( 'Tamil TV', 'tamil' ),
		'ueber-uns'   => __( 'Über Tamil.de', 'tamil' ),
		'kontakt'     => __( 'Kontakt', 'tamil' ),
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
