<?php
/**
 * Startseiten-Probe „Community First“ (/?probe=community, inc/proben.php): Die Seite beginnt mit „Tamil in meiner
 * Stadt“ (Stadt wählen, darunter Kino, Termine und Geschichten von dort). Danach folgt der erste Abschnitt der
 * Startseite unverändert aus front-page.php (Aufmacher, Meldungen, Nebenstücke, Rubrikkacheln).
 */

defined( 'ABSPATH' ) || exit;

get_template_part( 'template-parts/home/stadt', null, array( 'oben' => true ) );
