<?php
/**
 * Seite (Impressum, Datenschutz, Über uns …) mit Seitenspalte.
 */

defined( 'ABSPATH' ) || exit;

get_header();

while ( have_posts() ) :
	the_post();
	?>
	<div class="wrap">
		<?php tamil_breadcrumb( array( array( get_the_title(), '' ) ) ); ?>
		<div class="mit-spalte">
			<article <?php post_class( 'artikel' ); ?>>
				<header class="artikel-kopf"><h1><?php the_title(); ?></h1></header>
				<?php if ( has_post_thumbnail() ) : ?>
					<figure class="artikel-bild"><?php the_post_thumbnail( 'tamil-lead' ); ?></figure>
				<?php endif; ?>
				<div class="artikel-text"><?php the_content(); ?></div>
			</article>
			<?php get_sidebar(); ?>
		</div>
	</div>
	<?php
endwhile;

get_footer();
