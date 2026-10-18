<?php
/**
 * Seite nicht gefunden: Suche und die neuesten Beiträge.
 */

defined( 'ABSPATH' ) || exit;

get_header();
?>
<div class="container">
	<section class="section fehlerseite">
		<p class="kicker"><span class="ta" lang="ta">மன்னிக்கவும்</span><span class="de"><?php esc_html_e( 'Seite nicht gefunden', 'tamil' ); ?></span></p>
		<h1><?php esc_html_e( 'Diese Seite gibt es (nicht mehr).', 'tamil' ); ?></h1>
		<p><?php esc_html_e( 'Vielleicht ist der Beitrag umgezogen. Die Suche hilft weiter – oder ihr startet bei den neuesten Beiträgen.', 'tamil' ); ?></p>
		<?php get_search_form(); ?>
	</section>
	<section class="section">
		<?php tamil_kicker( 'news', __( 'Neu auf Tamil.de', 'tamil' ), home_url( '/' ), __( 'Zur Startseite', 'tamil' ) ); ?>
		<div class="cards">
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
