<?php
/**
 * Kopf: schmale Leiste (ab 761 px), Kopfzeile mit Logo, vier Zielen und dem Menü „Mehr“; darunter Werbeplatz 01.
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
<a class="skip" href="#inhalt"><?php esc_html_e( 'Zum Inhalt', 'tamil' ); ?></a>
<div class="site<?php echo tamil_hat_mobile_anzeige() ? ' has-sticky-ad' : ''; ?>">
<?php get_template_part( 'template-parts/header/kopf' ); ?>
<?php
$tamil_leaderboard = function_exists( 'tamil_site_anzeige' ) ? tamil_site_anzeige( 'leaderboard', false ) : '';
if ( '' !== $tamil_leaderboard ) :
	?>
	<div class="wrap anzeige-oben"><?php echo $tamil_leaderboard; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Werbeplatz aus dem Plugin, dort escapt ?></div>
<?php endif; ?>
<main id="inhalt" tabindex="-1">
