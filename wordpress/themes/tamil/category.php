<?php
/**
 * Rubrik: Kopf mit Rubrikpunkt, Beschreibung, Zähler und Filter-Chips; erste Geschichte groß, dann ein Raster.
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
<div class="wrap">
	<?php tamil_breadcrumb( array( array( $rubrik['label'], '' ) ) ); ?>
	<header class="seitenkopf r-<?php echo esc_attr( $slug ); ?>">
		<h1><?php echo esc_html( $rubrik['label'] ); ?></h1>
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
	<?php
	if ( $kino ) {
		get_template_part( 'template-parts/home/kino', null, array( 'post' => $kino ) );
	}
	?>
	<div class="mit-spalte">
		<div>
			<?php if ( have_posts() ) : ?>
				<div class="kartenraster">
					<?php
					$erste = 1 === $paged;
					while ( have_posts() ) {
						the_post();
						if ( get_the_ID() === $kino ) {
							continue;
						}
						get_template_part(
							'template-parts/card',
							null,
							$erste ? array(
								'variant' => 'gross',
								'heading' => 'h2',
								'rubrik'  => false,
								'lazy'    => false,
							) : array( 'rubrik' => false )
						);
						$erste = false;
					}
					?>
				</div>
				<p class="leer" data-filter-leer="chips" hidden><?php esc_html_e( 'Für diesen Filter gibt es auf dieser Seite keine Beiträge.', 'tamil' ); ?></p>
				<?php get_template_part( 'template-parts/pagination' ); ?>
			<?php elseif ( ! $kino ) : ?>
				<div class="leer">
					<?php /* translators: %s: Rubrik */ ?>
					<h2><?php echo esc_html( sprintf( __( 'Hier entsteht die Rubrik %s', 'tamil' ), $rubrik['label'] ) ); ?></h2>
					<p><?php esc_html_e( 'Noch keine Beiträge. Ihr habt ein Thema, ein Turnier oder ein Fest? Meldet es der Redaktion.', 'tamil' ); ?></p>
					<a class="knopf" href="<?php echo esc_url( tamil_seiten_url( 'kontakt' ) ); ?>"><?php esc_html_e( 'Thema vorschlagen', 'tamil' ); ?></a>
				</div>
			<?php endif; ?>
		</div>
		<?php get_sidebar(); ?>
	</div>
</div>
<?php
get_footer();
