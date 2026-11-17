<?php
/**
 * Ergänzungen zur SEO-Ausgabe des Plugins tamil-site (Meta, Open Graph, Artikel-Schema kommen von dort; hier nichts
 * doppelt): Ersatz für leere Beschreibungen (Startseite, Rubriken), ein Standard-Teilenbild für Seiten ohne eigenes
 * Bild und das Organization-Schema der Startseite. Läuft Yoast oder Rank Math, gibt das Plugin nichts aus und das
 * Theme ebenso wenig.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Ist die eigene SEO-Ausgabe (Plugin tamil-site) aktiv? Ohne Plugin: nur, wenn kein SEO-Plugin läuft.
 */
function tamil_seo_aktiv(): bool {
	if ( function_exists( 'tamil_site_seo_aktiv' ) ) {
		return tamil_site_seo_aktiv();
	}
	return ! defined( 'WPSEO_VERSION' ) && ! defined( 'RANK_MATH_VERSION' );
}

/**
 * Ersatz für die Beschreibung der Website, solange unter „Einstellungen → Allgemein“ kein Untertitel steht. Das Plugin
 * nimmt den Untertitel als Meta-Beschreibung der Startseite.
 *
 * @param mixed $wert Gespeicherter Untertitel.
 */
function tamil_seo_untertitel( $wert ) {
	if ( is_admin() ) {
		return $wert; // im Formular „Einstellungen → Allgemein“ bleibt das Feld leer
	}
	return '' === trim( (string) $wert ) ? __( 'Nachrichten, Kino und Community für Tamilen in Deutschland, Österreich und der Schweiz', 'tamil' ) : $wert;
}
add_filter( 'option_blogdescription', 'tamil_seo_untertitel' );

/**
 * Ersatz für leere Beschreibungen der Rubriken: die kurzen Texte aus tamil_rubriken_standard() (die auch im
 * Seitenkopf der Rubrik stehen). Das Plugin nimmt term_description() als Meta-Beschreibung der Rubrikseite.
 *
 * @param mixed $wert    Gespeicherte Beschreibung.
 * @param int   $term_id Rubrik.
 */
function tamil_seo_rubrik_beschreibung( $wert, $term_id = 0 ) {
	if ( '' !== trim( (string) $wert ) || ! $term_id ) {
		return $wert;
	}
	$term = get_term( (int) $term_id, 'category' );
	$text = $term instanceof WP_Term ? ( tamil_rubriken_standard()[ $term->slug ]['beschreibung'] ?? '' ) : '';
	return '' !== $text ? $text : $wert;
}
add_filter( 'category_description', 'tamil_seo_rubrik_beschreibung', 10, 2 );

/**
 * Standard-Teilenbild (1200 × 630, Logo neben einem Foto aus dem Rubrik-Pool mit Nachweis im Bild), solange in den
 * Einstellungen des Plugins keins gesetzt ist. Das Plugin nimmt es für Startseite, Rubriken und Seiten ohne Bild.
 * Das Foto wird nur beschnitten, das Logo steht daneben und nicht darauf (CC BY-SA, Spezifikation Bilder 2.3).
 *
 * @param mixed $wert Gespeicherte Einstellungen des Plugins.
 */
function tamil_seo_teilenbild( $wert ) {
	$wert = is_array( $wert ) ? $wert : array();
	if ( empty( $wert['bild'] ) ) {
		$wert['bild'] = TAMIL_THEME_URI . '/assets/img/teilen.jpg';
	}
	return $wert;
}
add_filter( 'option_tamil_site_seo', 'tamil_seo_teilenbild' );
add_filter( 'default_option_tamil_site_seo', 'tamil_seo_teilenbild' );

/**
 * Organization-Schema der Startseite (das Plugin gibt dort nur WebSite aus): dieselbe Kennung wie der Herausgeber im
 * Artikel-Schema (#organization), Logo und die Social-Profile, die im Customizer stehen.
 *
 * @return array<string,mixed>
 */
function tamil_seo_organisation(): array {
	$logo = TAMIL_THEME_DIR . '/assets/img/logo.png';
	$mass = is_readable( $logo ) ? wp_getimagesize( $logo ) : false;
	$org  = array(
		'@context' => 'https://schema.org',
		'@type'    => 'NewsMediaOrganization',
		'@id'      => home_url( '/#organization' ),
		'name'     => wp_strip_all_tags( (string) get_bloginfo( 'name' ) ),
		'url'      => home_url( '/' ),
	);
	if ( $mass ) {
		$org['logo'] = array(
			'@type'  => 'ImageObject',
			'url'    => get_theme_file_uri( 'assets/img/logo.png' ),
			'width'  => (int) $mass[0],
			'height' => (int) $mass[1],
		);
	}
	$profile = array_values( array_filter( wp_list_pluck( tamil_social(), 'url' ), static fn( $u ) => str_starts_with( (string) $u, 'https://' ) ) );
	if ( $profile ) {
		$org['sameAs'] = $profile;
	}
	return $org;
}

/**
 * Gibt das Organization-Schema auf der Startseite aus.
 */
function tamil_seo_organisation_ausgeben(): void {
	if ( ! is_front_page() || ! tamil_seo_aktiv() ) {
		return;
	}
	echo '<script type="application/ld+json">' . wp_json_encode( tamil_seo_organisation(), JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_HEX_TAG | JSON_HEX_AMP ) . "</script>\n"; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
}
add_action( 'wp_head', 'tamil_seo_organisation_ausgeben', 21 );
