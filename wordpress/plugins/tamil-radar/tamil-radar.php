<?php
/**
 * Plugin Name:       Tamil.de News-Radar
 * Plugin URI:        https://github.com/HKGrowthOperator/Tamil
 * Description:       Anbindung des News-Radars (externes Werkzeug) an WordPress: Beiträge mit Bild, Meta und SEO per REST, Cockpit im Backend, Dashboard-Widget und Rolle „Radar“. Unabhängig vom Theme.
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
}
add_action( 'init', 'tamil_radar_init' );
add_action( 'rest_api_init', 'tamil_radar_register_routes' );

/**
 * Einstellungen mit Standardwerten.
 *
 * @return array{cockpit_url:string}
 */
function tamil_radar_settings(): array {
	$defaults = array( 'cockpit_url' => '' );
	$stored   = get_option( 'tamil_radar_settings', array() );
	return array_merge( $defaults, is_array( $stored ) ? $stored : array() );
}
