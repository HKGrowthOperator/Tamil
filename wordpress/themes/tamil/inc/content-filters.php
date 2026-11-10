<?php
/**
 * Eingriffe in Inhalt und Ausgabe: Werbeplatz im Artikel, Textauszug, Body-Klassen, Suche nur in Beiträgen.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Werbeplatz 03 nach dem zweiten Absatz – nur im Hauptinhalt eines Beitrags mit mindestens vier Absätzen und nur,
 * wenn die Redaktion den Platz nicht selbst per [tamil_anzeige] gesetzt hat.
 */
function tamil_inarticle_anzeige( string $content ): string {
	if ( ! is_singular( 'post' ) || ! in_the_loop() || ! is_main_query() || ! function_exists( 'tamil_site_anzeige' ) ) {
		return $content;
	}
	if ( str_contains( $content, 'class="ad ' ) || substr_count( $content, '</p>' ) < 4 ) {
		return $content;
	}
	$anzeige = tamil_site_anzeige( 'inarticle', false );
	if ( '' === $anzeige ) {
		return $content;
	}
	$pos = 0;
	for ( $i = 0; $i < 2; $i++ ) {
		$pos = strpos( $content, '</p>', $pos );
		if ( false === $pos ) {
			return $content;
		}
		$pos += 4;
	}
	return substr( $content, 0, $pos ) . "\n" . $anzeige . "\n" . substr( $content, $pos );
}
add_filter( 'the_content', 'tamil_inarticle_anzeige', 20 );

function tamil_excerpt_length(): int {
	return 28;
}
add_filter( 'excerpt_length', 'tamil_excerpt_length' );

function tamil_excerpt_more(): string {
	return ' …';
}
add_filter( 'excerpt_more', 'tamil_excerpt_more' );

/**
 * Body-Klassen: Seitentyp für das CSS (page-start, page-artikel …).
 */
function tamil_body_class( array $classes ): array {
	if ( is_front_page() ) {
		$classes[] = 'page-start';
	} elseif ( is_singular( 'post' ) ) {
		$classes[] = 'page-artikel';
	} elseif ( is_category() ) {
		$classes[] = 'page-kategorie';
	}
	return $classes;
}
add_filter( 'body_class', 'tamil_body_class' );

/**
 * Die Suche zeigt Beiträge, keine Seiten oder Anhänge.
 */
function tamil_search_nur_beitraege( WP_Query $query ): void {
	if ( ! is_admin() && $query->is_main_query() && $query->is_search() ) {
		$query->set( 'post_type', 'post' );
	}
	if ( ! is_admin() && $query->is_main_query() && $query->is_category() ) {
		$query->set( 'posts_per_page', 12 );
	}
}
add_action( 'pre_get_posts', 'tamil_search_nur_beitraege' );

/**
 * Links mit target="_blank" im Inhalt bekommen rel="noopener", sofern sie kein rel haben.
 */
function tamil_links_noopener( string $content ): string {
	if ( ! str_contains( $content, 'target="_blank"' ) ) {
		return $content;
	}
	return (string) preg_replace( '/<a ((?:(?!rel=)[^>])*?)target="_blank"((?:(?!rel=)[^>])*)>/i', '<a $1target="_blank" rel="noopener"$2>', $content );
}
add_filter( 'the_content', 'tamil_links_noopener', 30 );

/**
 * YouTube-Kennung aus einer Video-Adresse (watch, embed, shorts, youtu.be); leer, wenn es keine ist.
 */
function tamil_youtube_id( string $url ): string {
	if ( preg_match( '~^https?://(?:www\.|m\.)?(?:youtube(?:-nocookie)?\.com/(?:watch\?(?:[^#\s]*&)?v=|embed/|shorts/)|youtu\.be/)([\w-]{6,20})~i', $url, $treffer ) ) {
		return $treffer[1];
	}
	return '';
}

/**
 * YouTube erst nach Klick laden (DSGVO). Statt des eingebetteten Players erscheint die Box .video-embed mit Knopf;
 * assets/js/app.js lädt das Video dann von youtube-nocookie.com. Der Filter greift vor dem oEmbed-Abruf, beim Aufbau
 * der Seite geht also keine Anfrage an YouTube hinaus, und der feste iframe (läuft am Handy seitlich über) entfällt.
 * Die Box enthält nur Zeilenelemente, damit wpautop sie nicht zerlegt.
 *
 * @param string|null $result Vorab-Ergebnis anderer Filter.
 * @param string      $url    Adresse, die eingebettet werden soll.
 */
function tamil_youtube_nach_klick( $result, $url ) {
	$id = tamil_youtube_id( (string) $url );
	if ( '' === $id ) {
		return $result;
	}
	return sprintf(
		'<div class="video-embed" data-video="%1$s"><button type="button" class="video-load">%2$s</button><span class="video-hint">%3$s <a href="%4$s" rel="noopener">%5$s</a></span></div>',
		esc_attr( $id ),
		esc_html__( 'Video laden', 'tamil' ),
		esc_html__( 'Beim Laden werden Daten an YouTube übertragen.', 'tamil' ),
		esc_url( 'https://www.youtube.com/watch?v=' . $id ),
		esc_html__( 'Bei YouTube ansehen', 'tamil' )
	);
}
add_filter( 'pre_oembed_result', 'tamil_youtube_nach_klick', 10, 2 );
