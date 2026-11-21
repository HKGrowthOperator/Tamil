<?php
/**
 * Tamil.de Theme – Einstieg. Die Funktionen liegen nach Aufgabe getrennt in inc/.
 *
 * Werbeplätze, Termin-Felder und Weiterleitungen kommen aus dem Plugin „Tamil.de Website“ (tamil-site); ohne das
 * Plugin bleiben die Werbeplätze leer und die Terminlisten verschwinden, alles andere läuft weiter.
 */

defined( 'ABSPATH' ) || exit;

define( 'TAMIL_THEME_VERSION', '3.11.0' );
define( 'TAMIL_THEME_DIR', get_template_directory() );
define( 'TAMIL_THEME_URI', get_template_directory_uri() );

require_once TAMIL_THEME_DIR . '/inc/setup.php';
require_once TAMIL_THEME_DIR . '/inc/customizer.php';
require_once TAMIL_THEME_DIR . '/inc/rubriken.php';
require_once TAMIL_THEME_DIR . '/inc/template-tags.php';
require_once TAMIL_THEME_DIR . '/inc/bildpool.php';
require_once TAMIL_THEME_DIR . '/inc/bausteine.php';
require_once TAMIL_THEME_DIR . '/inc/signatur.php';
require_once TAMIL_THEME_DIR . '/inc/bildkette.php';
require_once TAMIL_THEME_DIR . '/inc/filmbilder.php';
require_once TAMIL_THEME_DIR . '/inc/anreisser.php';
require_once TAMIL_THEME_DIR . '/inc/wow.php';
require_once TAMIL_THEME_DIR . '/inc/navigation.php';
require_once TAMIL_THEME_DIR . '/inc/queries.php';
require_once TAMIL_THEME_DIR . '/inc/content-filters.php';
require_once TAMIL_THEME_DIR . '/inc/enqueue.php';
require_once TAMIL_THEME_DIR . '/inc/patterns.php';
require_once TAMIL_THEME_DIR . '/inc/schema.php';
require_once TAMIL_THEME_DIR . '/inc/seo.php';
