<?php
/**
 * Plugin Name:       Tamil.de News-Radar
 * Plugin URI:        https://github.com/HKGrowthOperator/Tamil
 * Description:       Anbindung des News-Radars an WordPress: Beiträge mit Bild und Meta per REST, Cockpit im Backend, Rolle „Radar“, 301-Weiterleitungen, Werbeplätze und Abfragen für Events und Kinotermine.
 * Version:           1.0.0
 * Requires at least: 6.6
 * Requires PHP:      8.1
 * Author:            HK Growth Operator
 * License:           MIT
 * Text Domain:       tamil-radar
 */

defined( 'ABSPATH' ) || exit;

define( 'TAMIL_RADAR_VERSION', '1.0.0' );
define( 'TAMIL_RADAR_FILE', __FILE__ );
define( 'TAMIL_RADAR_DIR', plugin_dir_path( __FILE__ ) );
define( 'TAMIL_RADAR_URL', plugin_dir_url( __FILE__ ) );
define( 'TAMIL_RADAR_NS', 'tamil-radar/v1' );

require_once TAMIL_RADAR_DIR . 'includes/meta.php';
require_once TAMIL_RADAR_DIR . 'includes/role.php';
require_once TAMIL_RADAR_DIR . 'includes/media.php';
require_once TAMIL_RADAR_DIR . 'includes/seo.php';
require_once TAMIL_RADAR_DIR . 'includes/queries.php';
require_once TAMIL_RADAR_DIR . 'includes/ads.php';
require_once TAMIL_RADAR_DIR . 'includes/redirects.php';
require_once TAMIL_RADAR_DIR . 'includes/rest.php';
require_once TAMIL_RADAR_DIR . 'includes/admin.php';
require_once TAMIL_RADAR_DIR . 'includes/dashboard.php';

/**
 * Aktivierung: Rolle anlegen, Version merken, Permalinks auffrischen.
 */
function tamil_radar_activate(): void {
	tamil_radar_register_role();
	update_option( 'tamil_radar_version', TAMIL_RADAR_VERSION );
	flush_rewrite_rules();
}
register_activation_hook( __FILE__, 'tamil_radar_activate' );
register_deactivation_hook( __FILE__, 'flush_rewrite_rules' );

/**
 * init: Meta registrieren, Rolle nachprüfen (verlinkte Installationen überspringen die Aktivierung).
 */
function tamil_radar_init(): void {
	load_plugin_textdomain( 'tamil-radar', false, dirname( plugin_basename( __FILE__ ) ) . '/languages' );
	tamil_radar_register_meta();
	if ( ! get_role( 'radar' ) ) {
		tamil_radar_register_role();
	}
	add_shortcode( 'tamil_anzeige', 'tamil_radar_shortcode_anzeige' );
}
add_action( 'init', 'tamil_radar_init' );
add_action( 'rest_api_init', 'tamil_radar_register_routes' );

/**
 * Einstellungen mit Standardwerten.
 *
 * @return array{cockpit_url:string,anzeigen:array<string,string>,advanced_ads:array<string,string>}
 */
function tamil_radar_settings(): array {
	$defaults = array(
		'cockpit_url'  => '',
		'anzeigen'     => array(),
		'advanced_ads' => array(),
	);
	$stored = get_option( 'tamil_radar_settings', array() );
	return array_merge( $defaults, is_array( $stored ) ? $stored : array() );
}

/**
 * Die sechs Werbeplätze des Designs (Schlüssel → Beschriftung).
 *
 * @return array<string,string>
 */
function tamil_radar_werbeplaetze(): array {
	return array(
		'leaderboard' => __( '01 Leaderboard (728×90 / 320×50)', 'tamil-radar' ),
		'billboard'   => __( '02 Billboard Startseite (970×250)', 'tamil-radar' ),
		'inarticle'   => __( '03 Im Artikel (728×90 / 300×250)', 'tamil-radar' ),
		'sidebar'     => __( '04 Sidebar (300×600 / 336×280)', 'tamil-radar' ),
		'footer'      => __( '05 Footer (728×90 / 320×100)', 'tamil-radar' ),
		'mobile'      => __( '06 Mobil sticky (320×50)', 'tamil-radar' ),
	);
}
