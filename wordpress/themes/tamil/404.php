<?php
/**
 * Seite nicht gefunden: Suche und die neuesten Beiträge als Strom.
 */

defined( 'ABSPATH' ) || exit;

get_header();
$neu = tamil_ids( array( 'posts_per_page' => 5 ) );
?>
<header class="seitenkopf">
	<div class="wrap">
		<h1><?php esc_html_e( 'Diese Seite gibt es nicht (mehr).', 'tamil' ); ?></h1>
		<p class="satz"><?php esc_html_e( 'Vielleicht ist der Beitrag umgezogen. Die Suche hilft weiter, oder ihr startet bei den neuesten Beiträgen.', 'tamil' ); ?></p>
		<?php get_search_form(); ?>
	</div>
</header>
<?php if ( $neu ) : ?>
	<section class="abschnitt" aria-labelledby="neu-titel">
		<div class="wrap">
			<div class="kopfzeile">
				<h2 id="neu-titel"><?php esc_html_e( 'Zuletzt bei tamil.de', 'tamil' ); ?></h2>
				<a class="mehr" href="<?php echo esc_url( home_url( '/' ) ); ?>"><?php esc_html_e( 'Zur Startseite', 'tamil' ); ?></a>
			</div>
			<?php
			tamil_strom(
				$neu,
				array(
					'monat' => '',
					'titel' => 'h3',
				)
			);
			?>
		</div>
	</section>
<?php endif; ?>
<?php
get_footer();
