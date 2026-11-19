<?php
/**
 * Navigation: das Rubrikband in Titan Red (Einträge aus dem Menü „Hauptnavigation“, sonst die Rubriken in der Reihenfolge
 * von klar2 und „Kontakt“), die Dienste für „Mehr“ und den Fuß und die Top-News „Neu“ in der Kopfzeile.
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
			if ( (int) $item->menu_item_parent || tamil_ist_tv_link( (string) $item->url ) ) {
				continue; // Tamil TV ist pausiert (Seite „Tamil TV kommt“) und steht nicht im Band
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
			'aktiv' => tamil_nav_aktiv( $rubrik['url'] ) || is_category( $slug ) || ( 'events' === $slug && is_page( 'events' ) ) || tamil_beitrag_in_rubrik( $slug ),
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
 * Gehört der angezeigte Beitrag zur Rubrik? (Ein Events-Artikel markiert „Events“, auch wenn das Band auf die Seite
 * /events/ statt auf /category/events/ führt.)
 */
function tamil_beitrag_in_rubrik( string $slug ): bool {
	if ( ! is_singular( 'post' ) ) {
		return false;
	}
	$kat = tamil_hauptkategorie( (int) get_queried_object_id() );
	return $kat && $kat->slug === $slug;
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
			'url'   => tamil_einreichen_url(),
			'aktiv' => is_page( 'einreichen' ),
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
 * Top-News „Neu“ in der Kopfzeile: die neuesten veröffentlichten Beiträge aller Rubriken, ohne den Aufmacher der
 * Startseite und ohne den Beitrag, der gerade offen ist. Navigation, daher ohne Bild (Ausnahme der Bilderpflicht).
 * Die Kandidaten liegen zehn Minuten im Transient und werden mit der Startseite verworfen (tamil_flush_auswahl()).
 *
 * @return int[] Höchstens zwei Beiträge.
 */
function tamil_kopf_neu(): array {
	static $neu = null;
	if ( null !== $neu ) {
		return $neu;
	}
	$kandidaten = get_transient( 'tamil_kopf_neu' );
	if ( ! is_array( $kandidaten ) ) {
		$kandidaten = tamil_ids(
			array( 'posts_per_page' => 4 ),
			array( (int) tamil_start_auswahl()['lead'] )
		);
		set_transient( 'tamil_kopf_neu', $kandidaten, 10 * MINUTE_IN_SECONDS );
	}
	$offen = is_singular( 'post' ) ? (int) get_queried_object_id() : 0;
	$neu   = array_slice( array_values( array_diff( array_map( 'intval', $kandidaten ), array( $offen ) ) ), 0, 2 );
	return $neu;
}

/**
 * Adresse für „Termin einreichen“: die Seite „einreichen“ (Formulare des Plugins), sonst der Abschnitt auf „Kontakt“.
 */
function tamil_einreichen_url(): string {
	return tamil_seite( 'einreichen' ) ? tamil_seiten_url( 'einreichen' ) : tamil_seiten_url( 'kontakt', 'event-einreichen' );
}

/**
 * Zeigt ein Menüeintrag auf die Seite „Tamil TV“?
 */
function tamil_ist_tv_link( string $url ): bool {
	$tv = tamil_seite( 'tv' );
	return $tv && untrailingslashit( (string) get_permalink( $tv ) ) === untrailingslashit( $url );
}
