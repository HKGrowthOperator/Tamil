<?php
/**
 * Kopf: Topbar, Masthead mit Logo und Suche, Hauptnavigation, mobiles Menü, Laufband, Werbeplatz 01.
 */

defined( 'ABSPATH' ) || exit;
?><!doctype html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<a class="skip-link" href="#inhalt"><?php esc_html_e( 'Zum Inhalt springen', 'tamil' ); ?></a>
<div class="site<?php echo tamil_hat_mobile_anzeige() ? ' has-sticky-ad' : ''; ?>">
<header class="kopf">
	<?php get_template_part( 'template-parts/header/topbar' ); ?>
	<?php get_template_part( 'template-parts/header/masthead' ); ?>
	<?php get_template_part( 'template-parts/header/nav' ); ?>
</header>
<?php get_template_part( 'template-parts/header/ticker' ); ?>
<div class="container"><?php tamil_anzeige( 'leaderboard' ); ?></div>
<main id="inhalt" tabindex="-1">
