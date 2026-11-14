<?php
/**
 * Listen ohne eigene Vorlage (Schlagwort, Autor, Datum, Beitragsseite): Seitenkopf, Strom nach Monaten, Seiten.
 */

defined( 'ABSPATH' ) || exit;

get_header();

$titel = is_home() ? __( 'Neueste Beiträge', 'tamil' ) : wp_strip_all_tags( get_the_archive_title() );
$ids   = array_map( 'intval', wp_list_pluck( $GLOBALS['wp_query']->posts, 'ID' ) );
?>
<header class="seitenkopf">
	<div class="wrap">
		<h1><?php echo esc_html( $titel ); ?></h1>
		<?php
		if ( get_the_archive_description() ) :
			?>
			<div class="satz"><?php echo wp_kses_post( get_the_archive_description() ); ?></div><?php endif; ?>
	</div>
</header>
<section class="abschnitt" aria-label="<?php esc_attr_e( 'Beiträge', 'tamil' ); ?>">
	<div class="wrap">
		<?php if ( $ids ) : ?>
			<?php
			tamil_strom(
				$ids,
				array(
					'monat'  => 'h2',
					'titel'  => 'h3',
					'teaser' => 'immer',
				)
			);
			?>
			<?php get_template_part( 'template-parts/pagination' ); ?>
		<?php else : ?>
			<h2 class="strom-kopf"><?php esc_html_e( 'Keine Beiträge gefunden', 'tamil' ); ?></h2>
			<?php get_search_form(); ?>
		<?php endif; ?>
	</div>
</section>
<?php
get_footer();
