<?php
/**
 * Stylesheet, Skript (defer) und das Icon-Sprite.
 */

defined( 'ABSPATH' ) || exit;

function tamil_asset_version( string $rel ): string {
	$path = TAMIL_THEME_DIR . '/' . $rel;
	return file_exists( $path ) ? TAMIL_THEME_VERSION . '.' . filemtime( $path ) : TAMIL_THEME_VERSION;
}

function tamil_enqueue(): void {
	wp_enqueue_style( 'tamil-theme', TAMIL_THEME_URI . '/assets/css/theme.css', array(), tamil_asset_version( 'assets/css/theme.css' ) );
	wp_enqueue_script(
		'tamil-app',
		TAMIL_THEME_URI . '/assets/js/app.js',
		array(),
		tamil_asset_version( 'assets/js/app.js' ),
		array(
			'strategy'  => 'defer',
			'in_footer' => true,
		)
	);
	wp_add_inline_style( 'tamil-theme', tamil_anzeigen_flaechen_css() );
	// Gutenberg-Grundstile braucht das Theme nur für Blöcke im Inhalt; die globalen Stile aus theme.json bleiben.
	wp_dequeue_style( 'classic-theme-styles' );
}
add_action( 'wp_enqueue_scripts', 'tamil_enqueue' );

/**
 * Seitenverhältnis der Werbeflächen für Banner-Code (Einstellungen, Advanced Ads) aus derselben Konfiguration wie
 * Eigenanzeigen und gebuchte Anzeigen (Plugin: tamil_site_werbung_formate(), dort auch die Breite je Platz als Raster):
 * Banner-Code steht so in derselben Fläche, und das Handy-Format wechselt an derselben Grenze. Ohne Plugin: nichts.
 * Die Handy-Leiste (320 × 50) steht in theme.css.
 */
function tamil_anzeigen_flaechen_css(): string {
	if ( ! function_exists( 'tamil_site_werbung_formate' ) ) {
		return '';
	}
	$css = '';
	foreach ( tamil_site_werbung_formate() as $platz => $f ) {
		if ( 'mobile' === $platz ) {
			continue;
		}
		$flaeche = '.ad.ad-' . sanitize_key( $platz ) . ' .flaeche';
		$css    .= sprintf( '%1$s{aspect-ratio:%2$d/%3$d}', $flaeche, (int) $f['mobil'][0], (int) $f['mobil'][1] );
		if ( (int) $f['ab'] && $f['desktop'] !== $f['mobil'] ) {
			$css .= sprintf( '@media (min-width:%1$dpx){%2$s{aspect-ratio:%3$d/%4$d}}', (int) $f['ab'], $flaeche, (int) $f['desktop'][0], (int) $f['desktop'][1] );
		}
	}
	return $css;
}

/**
 * Schrift vorladen: Libre Franklin, nur der lateinische Teil (eine Datei für alle Stärken).
 */
function tamil_preload_fonts(): void {
	printf( '<link rel="preload" href="%s" as="font" type="font/woff2" crossorigin>' . "\n", esc_url( TAMIL_THEME_URI . '/assets/fonts/libre-franklin-latin-wght-normal.woff2' ) );
}
add_action( 'wp_head', 'tamil_preload_fonts', 1 );

/**
 * Icon-Sprite direkt nach <body>, damit <use href="#i-…"> überall greift.
 */
function tamil_icon_sprite(): void {
	$file = TAMIL_THEME_DIR . '/assets/icons.svg';
	if ( is_readable( $file ) ) {
		echo file_get_contents( $file ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped, WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents -- eigene Datei
	}
}
add_action( 'wp_body_open', 'tamil_icon_sprite', 1 );
