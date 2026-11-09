<?php
/**
 * Nächste Termine (drei Kacheln) mit „Event einreichen“.
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
<section class="abschnitt" id="termine">
	<div class="wrap">
		<?php tamil_kicker( 'events', __( 'Nächste Termine', 'tamil' ), $rubrik['url'], __( 'Zum Kalender', 'tamil' ) ); ?>
		<div class="termine">
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
	</div>
</section>
