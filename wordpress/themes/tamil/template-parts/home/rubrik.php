<?php
/**
 * Rubrik-Block der Startseite: eine große Geschichte links, drei Zeilen rechts. Leere Rubrik: Einladung zum Melden.
 * Im Kino-Block folgt die Kinoliste der Woche.
 *
 * @var array $args { @type string $slug, @type int[] $ids, @type int $kino Beitrag mit Kinoliste (optional). }
 */

defined( 'ABSPATH' ) || exit;

$slug   = (string) $args['slug'];
$ids    = $args['ids'] ?? array();
$rubrik = tamil_rubrik( $slug );
$kino   = (int) ( $args['kino'] ?? 0 );
if ( ! $rubrik['term'] ) {
	return;
}
?>
<section class="abschnitt" id="rubrik-<?php echo esc_attr( $slug ); ?>">
	<div class="wrap">
		<?php tamil_kicker( $slug, '', $rubrik['url'] ); ?>
		<?php if ( $ids ) : ?>
			<div class="mosaik">
				<?php
				get_template_part(
					'template-parts/card',
					null,
					array(
						'post'    => $ids[0],
						'variant' => 'gross',
						'heading' => 'h3',
						'rubrik'  => false,
					)
				);
				?>
				<div class="stapel">
					<?php foreach ( array_slice( $ids, 1, 3 ) as $id ) : ?>
						<?php
						get_template_part(
							'template-parts/card',
							null,
							array(
								'post'    => $id,
								'variant' => 'neben',
								'excerpt' => false,
								'rubrik'  => false,
							)
						);
						?>
					<?php endforeach; ?>
				</div>
			</div>
		<?php elseif ( ! $kino ) : ?>
			<div class="leer">
				<?php /* translators: %s: Rubrik */ ?>
				<h3><?php echo esc_html( sprintf( __( 'Noch keine Beiträge in %s', 'tamil' ), $rubrik['label'] ) ); ?></h3>
				<p><?php echo esc_html( $rubrik['beschreibung'] ); ?></p>
				<a class="knopf" href="<?php echo esc_url( tamil_seiten_url( 'kontakt', 'event-einreichen' ) ); ?>"><?php esc_html_e( 'Thema melden', 'tamil' ); ?></a>
			</div>
		<?php endif; ?>
		<?php
		if ( $kino ) {
			get_template_part( 'template-parts/home/kino', null, array( 'post' => $kino ) );
		}
		?>
	</div>
</section>
