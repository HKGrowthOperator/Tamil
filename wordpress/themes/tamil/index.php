<?php
/**
 * Listen ohne eigene Vorlage: Schlagwort, Autor, Datum, Beitragsseite.
 */

defined( 'ABSPATH' ) || exit;

get_header();

$titel = is_home() ? __( 'Neueste Beiträge', 'tamil' ) : wp_strip_all_tags( get_the_archive_title() );
?>
<div class="wrap">
	<?php tamil_breadcrumb( array( array( $titel, '' ) ) ); ?>
	<header class="seitenkopf">
		<h1><?php echo esc_html( $titel ); ?></h1>
		<?php
		if ( get_the_archive_description() ) :
			?>
			<div class="beschreibung"><?php echo wp_kses_post( get_the_archive_description() ); ?></div><?php endif; ?>
	</header>
	<div class="mit-spalte">
		<div>
			<?php if ( have_posts() ) : ?>
				<div class="kartenraster">
					<?php
					while ( have_posts() ) {
						the_post();
						get_template_part( 'template-parts/card' );
					}
					?>
				</div>
				<?php get_template_part( 'template-parts/pagination' ); ?>
			<?php else : ?>
				<div class="leer"><h2><?php esc_html_e( 'Keine Beiträge gefunden', 'tamil' ); ?></h2><?php get_search_form(); ?></div>
			<?php endif; ?>
		</div>
		<?php get_sidebar(); ?>
	</div>
</div>
<?php
get_footer();
