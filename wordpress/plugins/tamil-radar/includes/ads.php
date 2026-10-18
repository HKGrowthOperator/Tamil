<?php
/**
 * Werbeplätze: Advanced Ads (Platzierung), sonst HTML aus den Einstellungen, sonst nichts.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Roh-HTML für einen Werbeplatz (ohne Rahmen/Label – das setzt das Theme).
 */
function tamil_radar_anzeige_html( string $platz ): string {
	$platz = sanitize_key( $platz );
	if ( ! array_key_exists( $platz, tamil_radar_werbeplaetze() ) ) {
		return '';
	}
	$settings  = tamil_radar_settings();
	$placement = (string) ( $settings['advanced_ads'][ $platz ] ?? '' );
	if ( $placement && function_exists( 'get_the_ad_placement' ) ) {
		$html = (string) get_the_ad_placement( $placement );
		if ( '' !== trim( $html ) ) {
			return $html;
		}
	}
	$html = (string) ( $settings['anzeigen'][ $platz ] ?? '' );
	/**
	 * Letzte Chance für Themes/Plugins, ein Banner zu liefern.
	 *
	 * @param string $html  Bisheriges HTML.
	 * @param string $platz Werbeplatz.
	 */
	return (string) apply_filters( 'tamil_radar_anzeige', $html, $platz );
}

/**
 * Fertiger Block mit Label „Anzeige“, wie im Design; leer, wenn kein Banner gebucht ist.
 */
function tamil_radar_anzeige( string $platz, bool $echo = true ): string {
	$html = tamil_radar_anzeige_html( $platz );
	if ( '' === trim( $html ) ) {
		return '';
	}
	$out = sprintf(
		'<div class="ad ad-%1$s" data-platz="%1$s"><span class="ad-label">%2$s</span><div class="flaeche">%3$s</div></div>',
		esc_attr( $platz ),
		esc_html__( 'Anzeige', 'tamil-radar' ),
		$html // bewusst ungefiltert: Banner-Code aus den Einstellungen (nur Administratoren) bzw. Advanced Ads
	);
	if ( $echo ) {
		echo $out; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
	}
	return $out;
}

/**
 * [tamil_anzeige platz="leaderboard"]
 */
function tamil_radar_shortcode_anzeige( $atts ): string {
	$atts = shortcode_atts( array( 'platz' => 'inarticle' ), $atts, 'tamil_anzeige' );
	return tamil_radar_anzeige( (string) $atts['platz'], false );
}
