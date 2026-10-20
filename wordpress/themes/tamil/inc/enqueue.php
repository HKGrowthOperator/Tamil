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
	// Gutenberg-Grundstile braucht das Theme nur für Blöcke im Inhalt; die globalen Stile aus theme.json bleiben.
	wp_dequeue_style( 'classic-theme-styles' );
}
add_action( 'wp_enqueue_scripts', 'tamil_enqueue' );

/**
 * Schriften vorladen (Titelschrift und Textschrift, jeweils der lateinische Teil).
 */
function tamil_preload_fonts(): void {
	foreach ( array( 'catamaran-latin.woff2', 'literata-latin.woff2' ) as $font ) {
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
