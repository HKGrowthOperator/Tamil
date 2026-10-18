<?php
/**
 * Rubrik-Block: ein breiter Beitrag links, drei Zeilen rechts. Leere Rubrik: Einladung zum Melden.
 *
 * @var array $args { @type string $slug, @type int[] $ids }
 */

defined( 'ABSPATH' ) || exit;

$slug   = (string) $args['slug'];
$ids    = $args['ids'] ?? array();
$rubrik = tamil_rubrik( $slug );
if ( ! $rubrik['term'] ) {
	return;
}
?>
<section class="section" id="rubrik-<?php echo esc_attr( $slug ); ?>">
	<?php tamil_kicker( $slug, '', $rubrik['url'] ); ?>
	<?php if ( $ids ) : ?>
		<div class="rubrik">
			<div>
			<?php
			get_template_part(
				'template-parts/card',
				null,
				array(
					'post'    => $ids[0],
					'variant' => 'breit',
					'heading' => 'h2',
				)
			);
			?>
					</div>
			<div class="zeilen">
				<?php foreach ( array_slice( $ids, 1, 3 ) as $id ) : ?>
					<?php
					get_template_part(
						'template-parts/card',
						null,
						array(
							'post'    => $id,
							'variant' => 'zeile',
							'excerpt' => false,
						)
					);
					?>
				<?php endforeach; ?>
			</div>
		</div>
	<?php else : ?>
		<div class="leer">
			<?php /* translators: %s: Rubrik */ ?>
			<h3><?php echo esc_html( sprintf( __( 'Noch keine Beiträge in %s', 'tamil' ), $rubrik['label'] ) ); ?></h3>
			<p><?php echo esc_html( $rubrik['beschreibung'] ); ?></p>
			<div class="aktionen"><a class="btn btn-primary btn-sm" href="<?php echo esc_url( tamil_seiten_url( 'kontakt', 'event-einreichen' ) ); ?>"><?php esc_html_e( 'Thema melden', 'tamil' ); ?></a></div>
		</div>
	<?php endif; ?>
</section>
