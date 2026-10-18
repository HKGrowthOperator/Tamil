<?php
/**
 * Nächste Termine (drei Karten) mit „Event einreichen“.
 */

defined( 'ABSPATH' ) || exit;

if ( ! function_exists( 'tamil_site_upcoming_events' ) ) {
	return;
}
$events = tamil_site_upcoming_events( 3, array( 'fields' => 'ids' ) )->posts;
if ( ! $events ) {
	return;
}
$rubrik = tamil_rubrik( 'events' );
?>
<section class="section" id="events-teaser">
	<?php tamil_kicker( 'events', '', $rubrik['url'], __( 'Alle Events', 'tamil' ) ); ?>
	<div class="events-teaser">
		<?php foreach ( $events as $id ) : ?>
			<?php
			get_template_part(
				'template-parts/event-card',
				null,
				array(
					'post'    => (int) $id,
					'kompakt' => true,
				)
			);
			?>
		<?php endforeach; ?>
	</div>
	<p class="aktionen-zeile"><a class="btn btn-ghost btn-sm" href="<?php echo esc_url( tamil_seiten_url( 'kontakt', 'event-einreichen' ) ); ?>"><?php tamil_icon( 'plus', 'ico ico-sm' ); ?> <?php esc_html_e( 'Event einreichen', 'tamil' ); ?></a></p>
</section>
