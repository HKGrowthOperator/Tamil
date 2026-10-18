<?php
/**
 * Seite (Impressum, Datenschutz, Über uns …) mit Seitenspalte.
 */

defined( 'ABSPATH' ) || exit;

get_header();

while ( have_posts() ) :
	the_post();
	?>
	<div class="container">
		<?php tamil_breadcrumb( array( array( get_the_title(), '' ) ) ); ?>
		<div class="with-sidebar">
			<article <?php post_class( 'artikel' ); ?>>
				<header class="artikel-kopf"><h1><?php the_title(); ?></h1></header>
				<?php if ( has_post_thumbnail() ) : ?>
					<figure class="hero-bild"><?php the_post_thumbnail( 'tamil-lead' ); ?></figure>
				<?php endif; ?>
				<div class="artikel-body"><?php the_content(); ?></div>
			</article>
			<?php get_sidebar(); ?>
		</div>
	</div>
	<?php
endwhile;

get_footer();
