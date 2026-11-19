<?php
/**
 * Seite nicht gefunden: Seitenkopf mit Suche, die neuesten Beiträge als Liste und die Rubriken als Kacheln.
 */

defined( 'ABSPATH' ) || exit;

get_header();
$tamil_neu = tamil_ids( array( 'posts_per_page' => 5 ) );
?>
<div class="innen">
	<header class="seitenkopf seitenkopf--raum">
		<h1 class="seitenkopf__titel"><?php esc_html_e( 'Diese Seite gibt es nicht (mehr).', 'tamil' ); ?></h1>
		<p class="seitenkopf__zeile"><?php esc_html_e( 'Vielleicht ist der Beitrag umgezogen. Die Suche hilft weiter, oder ihr startet bei den neuesten Beiträgen.', 'tamil' ); ?></p>
		<?php get_search_form(); ?>
		<?php tamil_signatur( 'raum' ); ?>
	</header>
	<?php if ( $tamil_neu ) : ?>
		<section class="block" aria-labelledby="neu-titel">
			<div class="block-kopf">
				<h2 class="block-titel" id="neu-titel"><?php esc_html_e( 'Zuletzt bei tamil.de', 'tamil' ); ?></h2>
				<a class="textlink" href="<?php echo esc_url( home_url( '/' ) ); ?>"><?php esc_html_e( 'Zur Startseite', 'tamil' ); ?></a>
			</div>
			<?php echo tamil_zeilen( $tamil_neu ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_zeilen() ?>
		</section>
	<?php endif; ?>
	<?php echo tamil_kacheln( tamil_kacheln_ohne(), __( 'Rubriken mit Bild', 'tamil' ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_kacheln() ?>
</div>
<?php
get_footer();
