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

	// Geschnittene Größen für die Mediathek und ältere Inhalte. Die Vorlagen (klar2) laden die ungeschnittene Größe
	// „large“ mit srcset und schneiden per CSS auf 4:3, 16:9 und 8:3; neu erzeugte Vorschaubilder braucht es nicht.
	add_image_size( 'tamil-lead', 1600, 1000, true );
	add_image_size( 'tamil-card', 960, 720, true );
	add_image_size( 'tamil-zeile', 480, 480, true );
	set_post_thumbnail_size( 960, 720, true );
	// Ungeschnittene kleine Breiten für srcset: Rubrikkacheln (160 px), Listenbilder (96 bis 240 px) und Nebenstücke
	// (112 bis 290 px) laden so 320 bzw. 640 px statt 768. Gilt für neue Uploads; der Bestand bekommt sie erst mit
	// „wp media regenerate --only-missing“.
	add_image_size( 'tamil-320', 320, 0, false );
	add_image_size( 'tamil-640', 640, 0, false );

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
 * Neue Uploads: verkleinerte Fassungen als WebP (das Original bleibt JPEG). Nur, wenn der Server WebP schreiben kann;
 * PNG (Logos, Grafiken) bleibt PNG. Der Bestand wird nicht neu gerechnet.
 *
 * @param array<string,string> $formate Zuordnung Quelltyp → Zieltyp.
 * @return array<string,string>
 */
function tamil_webp_ausgabe( $formate ): array {
	$formate = is_array( $formate ) ? $formate : array();
	if ( wp_image_editor_supports( array( 'mime_type' => 'image/webp' ) ) ) {
		$formate['image/jpeg'] = 'image/webp';
	}
	return $formate;
}
add_filter( 'image_editor_output_format', 'tamil_webp_ausgabe' );

/**
 * Bildgrößen in der Mediathek wählbar machen.
 */
function tamil_image_size_names( array $sizes ): array {
	return array_merge(
		$sizes,
		array(
			'tamil-lead' => __( 'Aufmacher (16:10)', 'tamil' ),
			'tamil-card' => __( 'Karte (4:3)', 'tamil' ),
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
	return '|';
}
add_filter( 'document_title_separator', 'tamil_title_separator' );

/**
 * Icons aus dem Theme („t.“ auf dem Rot des Rubrikbands), solange kein Website-Icon im Customizer gesetzt ist: SVG,
 * PNG 32 als Rückfall, 180 für iOS, Manifest mit 192 und 512. Die Farbe der Browserleiste (theme-color) ist immer das
 * Rot des Bands.
 */
function tamil_favicon(): void {
	echo '<meta name="theme-color" content="#B5282A">' . "\n";
	if ( has_site_icon() ) {
		return; // WordPress gibt das Website-Icon selbst aus
	}
	$img = TAMIL_THEME_URI . '/assets/img/';
	printf( '<link rel="icon" href="%s" type="image/svg+xml">' . "\n", esc_url( $img . 'favicon.svg' ) );
	printf( '<link rel="icon" href="%s" type="image/png" sizes="32x32">' . "\n", esc_url( $img . 'icon-32.png' ) );
	printf( '<link rel="apple-touch-icon" href="%s" sizes="180x180">' . "\n", esc_url( $img . 'apple-touch-icon.png' ) );
	printf( '<link rel="manifest" href="%s">' . "\n", esc_url( TAMIL_THEME_URI . '/assets/manifest.webmanifest' ) );
}
add_action( 'wp_head', 'tamil_favicon', 2 );
