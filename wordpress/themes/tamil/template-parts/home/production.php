<?php
/**
 * Production-Band: Claim, Text, Knöpfe und die Plakate der Konzertbeiträge.
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
<section class="band" id="production">
	<div class="container">
		<section class="section">
			<?php tamil_kicker( 'events', tamil_opt( 'production_titel' ), $seite ? (string) get_permalink( $seite ) : '', __( 'Alle Konzerte und Service', 'tamil' ), 'நிகழ்ச்சிகள்' ); ?>
			<div class="production-grid">
				<div class="production-text">
					<h2 class="gross"><?php echo esc_html( tamil_opt( 'production_claim' ) ); ?></h2>
					<p><?php echo esc_html( tamil_opt( 'production_text' ) ); ?></p>
					<p class="aktionen">
						<?php
						if ( $seite ) :
							?>
							<a class="btn btn-primary" href="<?php echo esc_url( get_permalink( $seite ) ); ?>"><?php esc_html_e( 'Zur Konzertreihe', 'tamil' ); ?></a><?php endif; ?>
						<?php
						if ( $ticket ) :
							?>
							<a class="btn btn-ghost" href="<?php echo esc_url( $ticket ); ?>" target="_blank" rel="noopener nofollow"><?php tamil_icon( 'ticket', 'ico ico-sm' ); ?> <?php echo esc_html( tamil_opt( 'production_ticket_label' ) ); ?></a><?php endif; ?>
					</p>
				</div>
				<div class="plakate klein">
					<?php foreach ( $ids as $id ) : ?>
						<article class="plakat">
							<a class="media" href="<?php echo esc_url( get_permalink( $id ) ); ?>" tabindex="-1" aria-hidden="true"><?php echo tamil_bild( $id, 'tamil-card', array( 'loading' => 'lazy' ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?></a>
							<h3><a href="<?php echo esc_url( get_permalink( $id ) ); ?>"><?php echo esc_html( get_the_title( $id ) ); ?></a></h3>
						</article>
					<?php endforeach; ?>
				</div>
			</div>
		</section>
	</div>
</section>
