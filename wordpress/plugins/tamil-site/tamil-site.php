<?php
/**
 * Plugin Name:       Tamil.de Website
 * Plugin URI:        https://github.com/HKGrowthOperator/Tamil
 * Description:       Website-Funktionen für Tamil.de, unabhängig vom Theme und vom News-Radar: Event- und Kinofelder mit Eingabemaske, Werbeplätze (Advanced Ads, Banner-HTML, Eigenanzeigen) und 301-Weiterleitungen für den Relaunch.
 * Version:           1.1.0
 * Requires at least: 6.6
 * Requires PHP:      8.1
 * Author:            HK Growth Operator
 * License:           MIT
 * Text Domain:       tamil-site
 */

defined( 'ABSPATH' ) || exit;

define( 'TAMIL_SITE_VERSION', '1.1.0' );
define( 'TAMIL_SITE_DIR', plugin_dir_path( __FILE__ ) );
define( 'TAMIL_SITE_URL', plugin_dir_url( __FILE__ ) );

require_once TAMIL_SITE_DIR . 'includes/upgrade.php';
require_once TAMIL_SITE_DIR . 'includes/funktionen.php';
require_once TAMIL_SITE_DIR . 'includes/meta.php';
require_once TAMIL_SITE_DIR . 'includes/metabox.php';
require_once TAMIL_SITE_DIR . 'includes/queries.php';
require_once TAMIL_SITE_DIR . 'includes/ads.php';
require_once TAMIL_SITE_DIR . 'includes/redirects.php';
require_once TAMIL_SITE_DIR . 'includes/seo.php';
require_once TAMIL_SITE_DIR . 'includes/indexierung.php';
require_once TAMIL_SITE_DIR . 'includes/leistung.php';
require_once TAMIL_SITE_DIR . 'includes/consent.php';
require_once TAMIL_SITE_DIR . 'includes/admin.php';
require_once TAMIL_SITE_DIR . 'includes/werbung.php';
require_once TAMIL_SITE_DIR . 'includes/werbung-stripe.php';
require_once TAMIL_SITE_DIR . 'includes/werbung-zaehlung.php';
require_once TAMIL_SITE_DIR . 'includes/werbung-seiten.php';
require_once TAMIL_SITE_DIR . 'includes/werbung-admin.php';

register_activation_hook( __FILE__, 'flush_rewrite_rules' );
register_deactivation_hook( __FILE__, 'flush_rewrite_rules' );

/**
 * init (früh, Priorität 5): Meta registrieren, bevor andere Plugins dieselben Schlüssel anfassen.
 */
function tamil_site_init(): void {
	load_plugin_textdomain( 'tamil-site', false, dirname( plugin_basename( __FILE__ ) ) . '/languages' );
	tamil_site_register_meta();
	add_shortcode( 'tamil_anzeige', 'tamil_site_shortcode_anzeige' );
}
add_action( 'init', 'tamil_site_init', 5 );
