<?php
/**
 * Suchergebnisse.
 */

defined( 'ABSPATH' ) || exit;

get_header();
global $wp_query;
?>
<div class="container">
	<?php tamil_breadcrumb( array( array( __( 'Suche', 'tamil' ), '' ) ) ); ?>
	<header class="seitenkopf">
		<?php /* translators: %s: Suchbegriff */ ?>
		<h1><?php echo esc_html( sprintf( __( 'Suche: „%s“', 'tamil' ), get_search_query() ) ); ?></h1>
		<?php /* translators: %d: Anzahl */ ?>
		<p class="zaehler"><?php echo esc_html( sprintf( _n( '%d Treffer', '%d Treffer', (int) $wp_query->found_posts, 'tamil' ), (int) $wp_query->found_posts ) ); ?></p>
		<?php get_search_form(); ?>
	</header>
	<div class="with-sidebar">
		<div>
			<?php if ( have_posts() ) : ?>
				<div class="cards drei">
					<?php
					while ( have_posts() ) {
						the_post();
						get_template_part( 'template-parts/card', null, array( 'badge' => true ) );
					}
					?>
				</div>
				<?php get_template_part( 'template-parts/pagination' ); ?>
			<?php else : ?>
				<div class="leer"><h2><?php esc_html_e( 'Nichts gefunden', 'tamil' ); ?></h2><p><?php esc_html_e( 'Versuch es mit einem anderen Wort – zum Beispiel einem Filmtitel, einer Stadt oder einem Fest.', 'tamil' ); ?></p></div>
			<?php endif; ?>
		</div>
		<?php get_sidebar(); ?>
	</div>
</div>
<?php
get_footer();
