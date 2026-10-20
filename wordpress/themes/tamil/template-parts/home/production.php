<?php
/**
 * Tamil.de Production: Claim, Text, Knöpfe und die Plakate der Konzertbeiträge.
 *
 * @var array $args { @type int[] $ids }
 */

defined( 'ABSPATH' ) || exit;

$ids = $args['ids'] ?? array();
if ( ! $ids ) {
	return;
}
$seite  = tamil_seite( 'production' );
$ticket = tamil_opt( 'production_ticket_url' );
?>
<section class="abschnitt" id="production">
	<div class="wrap">
		<div class="production">
			<div class="production-text">
				<p class="rubrik r-entertainment"><?php echo esc_html( tamil_opt( 'production_titel' ) ); ?></p>
				<h2><?php echo esc_html( tamil_opt( 'production_claim' ) ); ?></h2>
				<p><?php echo esc_html( tamil_opt( 'production_text' ) ); ?></p>
				<div class="aktionen">
					<?php
					if ( $ticket ) :
						?>
						<a class="knopf knopf-rot" href="<?php echo esc_url( $ticket ); ?>" target="_blank" rel="noopener nofollow"><?php tamil_icon( 'ticket', 'ico ico-sm' ); ?> <?php echo esc_html( tamil_opt( 'production_ticket_label' ) ); ?></a><?php endif; ?>
					<?php
					if ( $seite ) :
						?>
						<a class="knopf" href="<?php echo esc_url( get_permalink( $seite ) ); ?>"><?php esc_html_e( 'Zur Konzertreihe', 'tamil' ); ?></a><?php endif; ?>
				</div>
			</div>
			<div class="plakate">
				<?php foreach ( array_slice( $ids, 0, 3 ) as $id ) : ?>
					<a class="plakat" href="<?php echo esc_url( get_permalink( $id ) ); ?>">
						<span class="bild"><?php echo tamil_bild( $id, 'tamil-zeile', array( 'loading' => 'lazy' ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?></span>
						<span class="plakat-titel"><?php echo esc_html( get_the_title( $id ) ); ?></span>
					</a>
				<?php endforeach; ?>
			</div>
		</div>
	</div>
</section>
