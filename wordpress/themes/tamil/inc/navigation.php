<?php
/**
 * Navigation: das dunkle Rubrikband (Einträge aus dem Menü „Hauptnavigation“, sonst die Rubriken in der Reihenfolge
 * von klar2 und „Kontakt“), die Dienste für „Mehr“ und den Fuß und die zwei Hinweise „Diese Woche“ in der Kopfzeile.
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

/**
 * Die Hinweise „Diese Woche“ in der Kopfzeile (ab 800 px): der nächste Termin und der Film mit den meisten Kinos.
 * Beide nur, wenn es sie gibt; Titel gekürzt, damit die Kopfzeile einzeilig bleibt.
 *
 * @return array<int,array{text:string,url:string}>
 */
function tamil_kopf_hinweise(): array {
	static $hinweise = null;
	if ( null !== $hinweise ) {
		return $hinweise;
	}
	$hinweise = array();
	if ( function_exists( 'tamil_site_upcoming_events' ) && function_exists( 'tamil_site_event' ) ) {
		$id = (int) ( tamil_site_upcoming_events( 1, array( 'fields' => 'ids' ) )->posts[0] ?? 0 );
		$e  = $id ? tamil_site_event( $id ) : array();
		$ts = $e ? strtotime( (string) $e['datum'] ) : false;
		if ( $ts ) {
			$hinweise[] = array(
				/* translators: 1: Termin, 2: Datum */
				'text' => sprintf( __( '%1$s am %2$s', 'tamil' ), tamil_titel_kurz( get_the_title( $id ), 30 ), wp_date( 'j. F', $ts ) ),
				'url'  => (string) get_permalink( $id ),
			);
		}
	}
	$filme = tamil_kino_filme( 3 );
	usort( $filme, static fn( $a, $b ) => $b['kinos'] <=> $a['kinos'] );
	if ( $filme ) {
		$f          = $filme[0];
		$hinweise[] = array(
			/* translators: 1: Film, 2: Anzahl Kinos */
			'text' => sprintf( _n( '„%1$s“ läuft in %2$d Kino', '„%1$s“ läuft in %2$d Kinos', $f['kinos'], 'tamil' ), tamil_titel_kurz( $f['film'], 24 ), $f['kinos'] ),
			'url'  => $f['link'],
		);
	}
	return $hinweise;
}
