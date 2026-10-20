<?php
/**
 * Seite nicht gefunden: Suche und die neuesten Beiträge.
 */

defined( 'ABSPATH' ) || exit;

get_header();
?>
<div class="wrap">
	<section class="abschnitt fehlerseite">
		<p class="rubrik r-news"><?php esc_html_e( 'Seite nicht gefunden', 'tamil' ); ?></p>
		<h1><?php esc_html_e( 'Diese Seite gibt es (nicht mehr).', 'tamil' ); ?></h1>
		<p><?php esc_html_e( 'Vielleicht ist der Beitrag umgezogen. Die Suche hilft weiter – oder ihr startet bei den neuesten Beiträgen.', 'tamil' ); ?></p>
		<?php get_search_form(); ?>
	</section>
	<section class="abschnitt">
		<?php tamil_kicker( 'news', __( 'Neu auf Tamil.de', 'tamil' ), home_url( '/' ), __( 'Zur Startseite', 'tamil' ) ); ?>
		<div class="reihe">
			<?php foreach ( tamil_ids( array( 'posts_per_page' => 3 ) ) as $id ) : ?>
				<?php
				get_template_part(
					'template-parts/card',
					null,
					array(
						'post'  => $id,
						'badge' => true,
					)
				);
				?>
			<?php endforeach; ?>
		</div>
	</section>
</div>
<?php
get_footer();
