<?php
/**
 * Rubrik: Kopf mit tamilischem Wort, Beschreibung, Zähler und Filter-Chips; erste Karte breit, dann 3er-Raster.
 * In „Kino“ steht die aktuelle Kinoliste vorn.
 */

defined( 'ABSPATH' ) || exit;

get_header();

$term   = get_queried_object();
$slug   = $term instanceof WP_Term ? $term->slug : '';
$rubrik = tamil_rubrik( $slug );
$paged  = max( 1, (int) get_query_var( 'paged' ) );
$kino   = 'kino' === $slug && 1 === $paged && function_exists( 'tamil_site_kino_posts' ) ? ( array_map( 'intval', tamil_site_kino_posts( 1, array( 'fields' => 'ids' ) )->posts )[0] ?? 0 ) : 0;
?>
<div class="container">
	<?php tamil_breadcrumb( array( array( $rubrik['label'], '' ) ) ); ?>
	<header class="seitenkopf">
		<h1><?php echo esc_html( $rubrik['label'] ); ?>
		<?php
		if ( $rubrik['tamil'] ) :
			?>
			<span class="ta" lang="ta"><?php echo esc_html( $rubrik['tamil'] ); ?></span><?php endif; ?></h1>
		<?php
		if ( $rubrik['beschreibung'] ) :
			?>
			<p class="beschreibung"><?php echo esc_html( $rubrik['beschreibung'] ); ?></p><?php endif; ?>
		<?php /* translators: %d: Anzahl */ ?>
		<p class="zaehler"><?php echo esc_html( sprintf( _n( '%d Beitrag', '%d Beiträge', (int) $term->count, 'tamil' ), (int) $term->count ) ); ?></p>
		<?php if ( $rubrik['chips'] ) : ?>
			<div class="chips" data-filter-group="chips" role="group" aria-label="<?php esc_attr_e( 'Filter', 'tamil' ); ?>">
				<button type="button" class="chip" data-filter="alle" aria-pressed="true"><?php esc_html_e( 'Alle', 'tamil' ); ?></button>
				<?php foreach ( $rubrik['chips'] as $key => $label ) : ?>
					<button type="button" class="chip" data-filter="<?php echo esc_attr( $key ); ?>" aria-pressed="false"><?php echo esc_html( $label ); ?></button>
				<?php endforeach; ?>
			</div>
		<?php endif; ?>
	</header>
	<div class="with-sidebar">
		<div>
			<?php if ( have_posts() || $kino ) : ?>
				<div class="cards drei">
					<?php
					$erste = 1 === $paged;
					if ( $kino ) {
						get_template_part(
							'template-parts/card',
							null,
							array(
								'post'    => $kino,
								'variant' => 'breit',
								'heading' => 'h2',
								'lazy'    => false,
							)
						);
						$erste = false;
					}
					while ( have_posts() ) {
						the_post();
						if ( get_the_ID() === $kino ) {
							continue;
						}
						get_template_part(
							'template-parts/card',
							null,
							$erste ? array(
								'variant' => 'breit',
								'heading' => 'h2',
								'lazy'    => false,
							) : array()
						);
						$erste = false;
					}
					?>
				</div>
				<p class="leer" data-filter-leer="chips" hidden><?php esc_html_e( 'Für diesen Filter gibt es auf dieser Seite keine Beiträge.', 'tamil' ); ?></p>
				<?php get_template_part( 'template-parts/pagination' ); ?>
			<?php else : ?>
				<div class="leer">
					<?php /* translators: %s: Rubrik */ ?>
					<h2><?php echo esc_html( sprintf( __( 'Hier entsteht die Rubrik %s', 'tamil' ), $rubrik['label'] ) ); ?></h2>
					<p><?php esc_html_e( 'Noch keine Beiträge. Ihr habt ein Thema, ein Turnier oder ein Fest? Meldet es der Redaktion.', 'tamil' ); ?></p>
					<div class="aktionen"><a class="btn btn-primary" href="<?php echo esc_url( tamil_seiten_url( 'kontakt' ) ); ?>"><?php esc_html_e( 'Thema vorschlagen', 'tamil' ); ?></a></div>
				</div>
			<?php endif; ?>
		</div>
		<?php get_sidebar(); ?>
	</div>
</div>
<?php
get_footer();
