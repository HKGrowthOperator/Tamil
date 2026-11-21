<?php
/**
 * Wow-Aufmacher „Punkt für Punkt zum Bild“ (Theme 3.10.0, Vorlage design/richtungen/klar2/wow/punkt-zum-bild/,
 * Entscheidung 21.11.2026 im Auftrag von Luis): Über dem Foto des Aufmachers der Startseite liegt eine Decke in
 * Titan mit den 238 Punkten des Masters „Tamil Dots 04A“ als Fenster aufs echte Foto. Beim Scrollen wachsen die
 * Punkte, bis das volle Farbfoto steht. Dachzeile und Titel stehen von Anfang an unten auf der Decke.
 *
 * Nur mit eigenem Foto (kein Symbolbild, kein Pool- oder Filmbild, keine Titelkarte) ab 960 px Breite. Abschaltbar
 * im Customizer (Tamil.de → Startseite → „Wow-Aufmacher“) und über den Filter `tamil_wow_aufmacher` (false = aus).
 * Ohne Skript, ohne Canvas und mit „Bewegung reduzieren“ steht sofort das fertige Foto mit Titel (die Decke gibt es
 * nur, wenn das Skript im Kopf die Klasse wow-an setzt). Zeichnen: assets/js/wow.js, nur auf der Startseite.
 */

defined( 'ABSPATH' ) || exit;

/** Kleinste Breite des Originalfotos für die Decke. */
const TAMIL_WOW_MIN_BREITE = 960;

/**
 * Bekommt dieser Beitrag als Aufmacher die Decke?
 */
function tamil_wow_aufmacher_an( int $post_id ): bool {
	$an = '1' === tamil_opt( 'wow_aufmacher' ) && $post_id > 0;
	if ( $an ) {
		$w    = tamil_bildwahl( $post_id );
		$meta = 'eigen' === $w['art'] ? wp_get_attachment_metadata( (int) $w['id'] ) : array();
		$an   = 'eigen' === $w['art'] && ! $w['symbol'] && ! $w['breit'] && (int) ( $meta['width'] ?? 0 ) >= TAMIL_WOW_MIN_BREITE;
	}
	/**
	 * Wow-Aufmacher für diesen Beitrag an oder aus.
	 *
	 * @param bool $an      Nach Einstellung und Foto.
	 * @param int  $post_id Aufmacher der Startseite.
	 */
	return (bool) apply_filters( 'tamil_wow_aufmacher', $an, $post_id );
}

/**
 * Wow-Aufmacher auf dieser Seite (nur Startseite, einmal gerechnet)?
 */
function tamil_wow_auf_seite(): bool {
	static $an = null;
	if ( null === $an ) {
		$an = is_front_page() && ! is_paged() && function_exists( 'tamil_start_auswahl' ) && tamil_wow_aufmacher_an( (int) ( tamil_start_auswahl()['lead'] ?? 0 ) );
	}
	return $an;
}

/**
 * Vor dem ersten Bild: die Decke nur einschalten, wenn Canvas da ist und keine reduzierte Bewegung gewünscht ist.
 */
function tamil_wow_kopf(): void {
	if ( ! tamil_wow_auf_seite() ) {
		return;
	}
	echo "<script>(function(){var h=document.documentElement;if(window.CanvasRenderingContext2D&&!(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches))h.classList.add('wow-an');})();</script>\n";
}
add_action( 'wp_head', 'tamil_wow_kopf', 1 );

/**
 * Skript der Decke (mit den Punktdaten), nur wenn die Startseite den Wow-Aufmacher zeigt.
 */
function tamil_wow_skript(): void {
	if ( ! tamil_wow_auf_seite() ) {
		return;
	}
	wp_enqueue_script(
		'tamil-wow',
		TAMIL_THEME_URI . '/assets/js/wow.js',
		array(),
		tamil_asset_version( 'assets/js/wow.js' ),
		array(
			'strategy'  => 'defer',
			'in_footer' => true,
		)
	);
}
add_action( 'wp_enqueue_scripts', 'tamil_wow_skript', 20 );
