<?php
/**
 * Community-Band: vier Beiträge und der Aufruf, Feste und Termine zu melden.
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
<section class="section band-dunkel community-band" id="community">
	<div class="container">
		<?php tamil_kicker( 'community', __( 'Aus der Community', 'tamil' ), $rubrik['url'] ); ?>
		<div class="community-grid">
			<div class="community-liste">
				<?php foreach ( $ids as $id ) : ?>
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
			<div class="community-cta">
				<h3><?php esc_html_e( 'Melde uns dein Fest.', 'tamil' ); ?></h3>
				<p><?php esc_html_e( 'Tempelfest, Kulturabend, Turnier, Konzert: Schick uns Datum, Ort und ein Foto – die Redaktion trägt es in den Kalender ein.', 'tamil' ); ?></p>
				<div class="aktionen">
					<?php
					if ( $wa ) :
						?>
						<a class="btn btn-wa" href="<?php echo esc_url( $wa ); ?>" target="_blank" rel="noopener"><?php tamil_icon( 'whatsapp', 'ico ico-sm' ); ?> <?php esc_html_e( 'Per WhatsApp melden', 'tamil' ); ?></a><?php endif; ?>
					<a class="btn btn-ghost hell" href="<?php echo esc_url( tamil_seiten_url( 'kontakt', 'event-einreichen' ) ); ?>"><?php esc_html_e( 'Formular', 'tamil' ); ?></a>
				</div>
			</div>
		</div>
	</div>
</section>
