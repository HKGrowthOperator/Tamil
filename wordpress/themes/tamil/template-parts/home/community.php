<?php
/**
 * Community: Beiträge der Rubrik und das rote Mitmach-Band („Melde uns dein Fest“).
 *
 * @var array $args { @type int[] $ids }
 */

defined( 'ABSPATH' ) || exit;

$ids    = $args['ids'] ?? array();
$rubrik = tamil_rubrik( 'community' );
if ( ! $rubrik['term'] ) {
	return;
}
$wa = tamil_whatsapp_link( __( 'Hallo Tamil.de, ich möchte ein Event melden: ', 'tamil' ) );
?>
<section class="abschnitt" id="community">
	<div class="wrap">
		<?php tamil_kicker( 'community', __( 'Aus der Community', 'tamil' ), $rubrik['url'] ); ?>
		<?php if ( $ids ) : ?>
			<div class="reihe">
				<?php foreach ( array_slice( $ids, 0, 3 ) as $id ) : ?>
					<?php
					get_template_part(
						'template-parts/card',
						null,
						array(
							'post'    => $id,
							'rubrik'  => false,
							'excerpt' => false,
						)
					);
					?>
				<?php endforeach; ?>
			</div>
		<?php endif; ?>
		<div class="mitmachen">
			<div class="mitmachen-text">
				<p class="rubrik r-safran"><?php esc_html_e( 'Mitmachen', 'tamil' ); ?></p>
				<h2><?php esc_html_e( 'Melde uns dein Fest.', 'tamil' ); ?></h2>
				<p><?php esc_html_e( 'Tempelfest, Kulturabend, Turnier oder Konzert: Schick uns Datum, Ort und ein Foto. Die Redaktion trägt es kostenlos in den Kalender ein.', 'tamil' ); ?></p>
				<div class="aktionen">
					<?php
					if ( $wa ) :
						?>
						<a class="knopf knopf-hell" href="<?php echo esc_url( $wa ); ?>" target="_blank" rel="noopener"><?php tamil_icon( 'whatsapp', 'ico ico-sm' ); ?> <?php esc_html_e( 'Per WhatsApp melden', 'tamil' ); ?></a><?php endif; ?>
					<a class="knopf knopf-umriss" href="<?php echo esc_url( tamil_seiten_url( 'kontakt', 'event-einreichen' ) ); ?>"><?php esc_html_e( 'Zum Formular', 'tamil' ); ?></a>
				</div>
			</div>
			<svg class="mitmachen-kolam" aria-hidden="true"><use href="#i-kolam"/></svg>
		</div>
	</div>
</section>
