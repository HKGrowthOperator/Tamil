<?php
/**
 * Rubriken: deutsches Label, tamilisches Wort (für Meta-Angaben, nicht als Schmuck), Beschreibung, Filter-Chips.
 * Label und Beschreibung lassen sich in WordPress (Kategorie bearbeiten) überschreiben.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Standardwerte der Rubriken (Reihenfolge = Navigation).
 *
 * @return array<string,array{label:string,tamil:string,beschreibung:string,chips:array<string,string>}>
 */
function tamil_rubriken_standard(): array {
	return array(
		'news'          => array(
			'label'        => 'Nachrichten',
			'tamil'        => 'செய்திகள்',
			'beschreibung' => 'Was die tamilische Community in Deutschland, Österreich und der Schweiz bewegt: Politik, Diaspora, Sri Lanka und Tamil Nadu – eingeordnet auf Deutsch.',
			'chips'        => array(),
		),
		'entertainment' => array(
			'label'        => 'Entertainment',
			'tamil'        => 'பொழுதுபோக்கு',
			'beschreibung' => 'Musik, Stars, Serien und Konzerte – von Kollywood bis zur Diaspora-Szene in Europa.',
			'chips'        => array(
				'konzert' => 'Konzerte',
				'musik'   => 'Musik',
			),
		),
		'events'        => array(
			'label'        => 'Events',
			'tamil'        => 'நிகழ்வுகள்',
			'beschreibung' => 'Konzerte, Feste, Wettbewerbe und Kinoabende – der Veranstaltungskalender für DE, AT und CH.',
			'chips'        => array(),
		),
		'community'     => array(
			'label'        => 'Community',
			'tamil'        => 'சமூகம்',
			'beschreibung' => 'Vereine, Tempel, Schulen und Menschen: Geschichten aus der tamilischen Gemeinschaft im deutschsprachigen Raum.',
			'chips'        => array(),
		),
		'kueche'        => array(
			'label'        => 'Küche',
			'tamil'        => 'சமையல்',
			'beschreibung' => 'Rezepte aus Jaffna, Chennai und der Diaspora – mit Zutatenliste und Schritt-für-Schritt-Anleitung.',
			'chips'        => array(),
		),
		'kino'          => array(
			'label'        => 'Kino',
			'tamil'        => 'சினிமா',
			'beschreibung' => 'Tamilische Filme im deutschsprachigen Raum: Kinostarts, Spielorte, Kritiken und Hintergründe – aktualisiert mit jedem neuen Kinoprogramm.',
			'chips'        => array(
				'kritik'      => 'Kritik',
				'kinostart'   => 'Kinostart',
				'kinotermine' => 'Kinotermine',
			),
		),
		'sport'         => array(
			'label'        => 'Sport',
			'tamil'        => 'விளையாட்டு',
			'beschreibung' => 'Cricket, Fußball, Kabaddi und Turniere der tamilischen Vereine – Ergebnisse, Termine und Porträts.',
			'chips'        => array(),
		),
		'kultur'        => array(
			'label'        => 'Kultur',
			'tamil'        => 'பண்பாடு',
			'beschreibung' => 'Pongal, Parai, Tempelfeste, Tanz und Literatur: tamilische Kultur erklärt und gelebt – hier und in der Heimat.',
			'chips'        => array(),
		),
	);
}

/**
 * Eine Rubrik mit den Werten aus WordPress (Name, Beschreibung, Term-Meta „tamil“) über den Standards.
 *
 * @return array{slug:string,label:string,tamil:string,beschreibung:string,chips:array<string,string>,url:string,term:?WP_Term}
 */
function tamil_rubrik( string $slug ): array {
	static $cache = array();
	if ( isset( $cache[ $slug ] ) ) {
		return $cache[ $slug ];
	}
	$standard = tamil_rubriken_standard()[ $slug ] ?? array(
		'label'        => ucfirst( $slug ),
		'tamil'        => '',
		'beschreibung' => '',
		'chips'        => array(),
	);
	$term     = get_category_by_slug( $slug );
	$term     = $term instanceof WP_Term ? $term : null;
	$out      = array_merge(
		$standard,
		array(
			'slug' => $slug,
			'term' => $term,
			'url'  => $term ? (string) get_category_link( $term ) : home_url( '/' ),
		)
	);
	if ( $term ) {
		$out['label'] = $term->name;
		if ( '' !== trim( $term->description ) ) {
			$out['beschreibung'] = wp_strip_all_tags( $term->description );
		}
		$tamil = (string) get_term_meta( $term->term_id, 'tamil', true );
		if ( '' !== $tamil ) {
			$out['tamil'] = $tamil;
		}
	}
	if ( 'events' === $slug ) {
		$page = get_page_by_path( 'events' );
		if ( $page instanceof WP_Post && 'publish' === $page->post_status ) {
			$out['url'] = (string) get_permalink( $page );
		}
	}
	$cache[ $slug ] = $out;
	return $out;
}

/**
 * Hauptkategorie eines Beitrags (Rank Math/Yoast-Hauptkategorie, sonst die erste außer „Allgemein“).
 */
function tamil_hauptkategorie( int $post_id ): ?WP_Term {
	foreach ( array( 'rank_math_primary_category', '_yoast_wpseo_primary_category' ) as $key ) {
		$primary = (int) get_post_meta( $post_id, $key, true );
		if ( $primary ) {
			$term = get_term( $primary, 'category' );
			if ( $term instanceof WP_Term ) {
				return $term;
			}
		}
	}
	$terms = get_the_category( $post_id );
	foreach ( $terms as $term ) {
		if ( 'uncategorized' !== $term->slug && 'allgemein' !== $term->slug ) {
			return $term;
		}
	}
	return $terms[0] ?? null;
}
