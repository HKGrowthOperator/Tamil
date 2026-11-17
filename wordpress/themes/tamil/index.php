<?php
/**
 * Listen ohne eigene Vorlage (Schlagwort, Autor, Datum, Beitragsseite): Seitenkopf, Liste mit Bild und Vorspann,
 * Seitennavigation.
 */

defined( 'ABSPATH' ) || exit;

get_header();

$tamil_titel = is_home() ? __( 'Neueste Beiträge', 'tamil' ) : wp_strip_all_tags( get_the_archive_title() );
$tamil_ids   = array_map( 'intval', wp_list_pluck( $GLOBALS['wp_query']->posts, 'ID' ) );
tamil_cache_fuellen( $tamil_ids );
?>
<div class="innen">
	<header class="seitenkopf">
		<h1 class="seitenkopf__titel"><?php echo esc_html( $tamil_titel ); ?></h1>
		<?php
		if ( get_the_archive_description() ) :
			?>
			<div class="seitenkopf__zeile"><?php echo wp_kses_post( get_the_archive_description() ); ?></div><?php endif; ?>
	</header>
	<?php if ( $tamil_ids ) : ?>
		<section class="block" aria-label="<?php esc_attr_e( 'Beiträge', 'tamil' ); ?>">
			<?php echo tamil_zeilen( $tamil_ids, array( 'ebene' => 'h2' ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_zeilen() ?>
		</section>
		<?php get_template_part( 'template-parts/pagination' ); ?>
	<?php else : ?>
		<section class="block leer">
			<h2 class="block-titel"><?php esc_html_e( 'Keine Beiträge gefunden', 'tamil' ); ?></h2>
			<?php get_search_form(); ?>
		</section>
	<?php endif; ?>
</div>
<?php
get_footer();
