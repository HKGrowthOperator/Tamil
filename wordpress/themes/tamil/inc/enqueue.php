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
	$abh = array();
	if ( file_exists( TAMIL_THEME_DIR . '/assets/css/alt.css' ) ) {
		// Übergang: Abschnitte des alten Themes für noch nicht umgestellte Seiten (vor theme.css, damit Neues gewinnt).
		wp_enqueue_style( 'tamil-alt', TAMIL_THEME_URI . '/assets/css/alt.css', array(), tamil_asset_version( 'assets/css/alt.css' ) );
		$abh[] = 'tamil-alt';
	}
	wp_enqueue_style( 'tamil-theme', TAMIL_THEME_URI . '/assets/css/theme.css', $abh, tamil_asset_version( 'assets/css/theme.css' ) );
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
	// Gutenberg-Grundstile braucht das Theme nur für Blöcke im Inhalt; die globalen Stile aus theme.json bleiben.
	wp_dequeue_style( 'classic-theme-styles' );
}
add_action( 'wp_enqueue_scripts', 'tamil_enqueue' );

/**
 * Schriften vorladen (Titelschrift und Textschrift, jeweils der lateinische Teil).
 */
function tamil_preload_fonts(): void {
	foreach ( array( 'rethink-sans-latin-wght-normal.woff2', 'golos-text-latin-wght-normal.woff2' ) as $font ) {
		printf( '<link rel="preload" href="%s" as="font" type="font/woff2" crossorigin>' . "\n", esc_url( TAMIL_THEME_URI . '/assets/fonts/' . $font ) );
	}
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
