<?php
/**
 * Theme-Unterstützung, Bildgrößen, Menüs, Aufräumen im <head>.
 */

defined( 'ABSPATH' ) || exit;

function tamil_setup(): void {
	load_theme_textdomain( 'tamil', TAMIL_THEME_DIR . '/languages' );

	add_theme_support( 'title-tag' );
	add_theme_support( 'post-thumbnails' );
	add_theme_support( 'automatic-feed-links' );
	add_theme_support( 'responsive-embeds' );
	add_theme_support( 'align-wide' );
	add_theme_support( 'editor-styles' );
	add_theme_support( 'html5', array( 'search-form', 'gallery', 'caption', 'style', 'script', 'navigation-widgets' ) );
	add_theme_support(
		'custom-logo',
		array(
			'height'      => 121,
			'width'       => 300,
			'flex-height' => true,
			'flex-width'  => true,
		)
	);
	add_editor_style( 'assets/css/editor.css' );

	// 16:9 für Aufmacher und Karten, 4:3 für Zeilen-Karten (wie im Design).
	add_image_size( 'tamil-lead', 1200, 675, true );
	add_image_size( 'tamil-card', 800, 450, true );
	add_image_size( 'tamil-zeile', 480, 360, true );
	set_post_thumbnail_size( 800, 450, true );

	register_nav_menus(
		array(
			'haupt'          => __( 'Hauptnavigation', 'tamil' ),
			'footer_service' => __( 'Footer: Service', 'tamil' ),
			'footer_legal'   => __( 'Footer: Rechtliches', 'tamil' ),
		)
	);
}
add_action( 'after_setup_theme', 'tamil_setup' );

/**
 * Breite des Textes im Artikel (für eingebettete Medien).
 */
function tamil_content_width(): void {
	$GLOBALS['content_width'] = 720;
}
add_action( 'after_setup_theme', 'tamil_content_width', 0 );

/**
 * Bildgrößen in der Mediathek wählbar machen.
 */
function tamil_image_size_names( array $sizes ): array {
	return array_merge(
		$sizes,
		array(
			'tamil-lead' => __( 'Aufmacher (16:9)', 'tamil' ),
			'tamil-card' => __( 'Karte (16:9)', 'tamil' ),
		)
	);
}
add_filter( 'image_size_names_choose', 'tamil_image_size_names' );

/**
 * Emoji-Skripte, Generator-Tag und den RSD-/WLW-Ballast weglassen.
 */
function tamil_cleanup_head(): void {
	remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
	remove_action( 'wp_print_styles', 'print_emoji_styles' );
	remove_action( 'admin_print_scripts', 'print_emoji_detection_script' );
	remove_action( 'admin_print_styles', 'print_emoji_styles' );
	remove_action( 'wp_head', 'wp_generator' );
	remove_action( 'wp_head', 'rsd_link' );
	remove_action( 'wp_head', 'wlwmanifest_link' );
}
add_action( 'init', 'tamil_cleanup_head' );

/**
 * Trenner im Seitentitel.
 */
function tamil_title_separator(): string {
	return '–';
}
add_filter( 'document_title_separator', 'tamil_title_separator' );

/**
 * Favicon aus dem Theme, solange kein Website-Icon im Customizer gesetzt ist.
 */
function tamil_favicon(): void {
	if ( ! has_site_icon() ) {
		echo '<link rel="icon" href="' . esc_url( TAMIL_THEME_URI . '/assets/img/favicon.svg' ) . '" type="image/svg+xml">' . "\n";
	}
}
add_action( 'wp_head', 'tamil_favicon', 2 );

/**
 * Widget-Bereich unter den festen Bausteinen der Seitenspalte.
 */
function tamil_widgets(): void {
	register_sidebar(
		array(
			'id'            => 'seitenspalte',
			'name'          => __( 'Seitenspalte (unten)', 'tamil' ),
			'before_widget' => '<div id="%1$s" class="widget %2$s">',
			'after_widget'  => '</div>',
			'before_title'  => '<h2 class="kicker"><span class="ta" lang="ta"></span><span class="de">',
			'after_title'   => '</span></h2>',
		)
	);
}
add_action( 'widgets_init', 'tamil_widgets' );
