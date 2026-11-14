<?php
/**
 * Suchergebnisse: Seitenkopf mit Suchbegriff, Zahl der Treffer und Suchfeld, dann die Treffer als Strom.
 */

defined( 'ABSPATH' ) || exit;

get_header();
global $wp_query;
$ids = array_map( 'intval', wp_list_pluck( $wp_query->posts, 'ID' ) );
?>
<header class="seitenkopf">
	<div class="wrap">
		<?php /* translators: %s: Suchbegriff */ ?>
		<h1><?php echo esc_html( sprintf( __( 'Suche: „%s“', 'tamil' ), get_search_query() ) ); ?></h1>
		<?php /* translators: %d: Anzahl */ ?>
		<p class="satz"><?php echo esc_html( sprintf( _n( '%d Treffer', '%d Treffer', (int) $wp_query->found_posts, 'tamil' ), (int) $wp_query->found_posts ) ); ?></p>
		<?php get_search_form(); ?>
	</div>
</header>
<section class="abschnitt" aria-label="<?php esc_attr_e( 'Treffer', 'tamil' ); ?>">
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
			<h2 class="strom-kopf"><?php esc_html_e( 'Nichts gefunden', 'tamil' ); ?></h2>
			<p class="satz"><?php esc_html_e( 'Versucht es mit einem anderen Wort, zum Beispiel einem Filmtitel, einer Stadt oder einem Fest.', 'tamil' ); ?></p>
		<?php endif; ?>
	</div>
</section>
<?php
get_footer();
