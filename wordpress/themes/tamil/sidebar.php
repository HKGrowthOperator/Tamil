<?php
/**
 * Seitenspalte: Werbeplatz 02, Top-Themen, nächste Termine, Newsletter.
 *
 * @var array $args { @type bool $events Termine zeigen (Standard: ja). }
 */

defined( 'ABSPATH' ) || exit;

$auswahl      = tamil_home_auswahl();
$zeige_events = (bool) ( $args['events'] ?? true ) && function_exists( 'tamil_site_upcoming_events' );
$events       = $zeige_events ? tamil_site_upcoming_events( 4, array( 'fields' => 'ids' ) )->posts : array();
?>
<aside class="sidebar">
	<?php tamil_anzeige( 'sidebar' ); ?>
	<?php if ( $auswahl['top'] ) : ?>
		<div class="widget">
			<h2 class="kicker"><span class="ta" lang="ta">முக்கியம்</span><span class="de"><?php esc_html_e( 'Top-Themen', 'tamil' ); ?></span></h2>
			<ol class="liste">
				<?php foreach ( $auswahl['top'] as $i => $id ) : ?>
					<li><span class="nr"><?php echo esc_html( sprintf( '%02d', $i + 1 ) ); ?></span><a href="<?php echo esc_url( get_permalink( $id ) ); ?>"><?php echo esc_html( get_the_title( $id ) ); ?></a></li>
				<?php endforeach; ?>
			</ol>
		</div>
	<?php endif; ?>
	<?php if ( $events ) : ?>
		<div class="widget dunkel">
			<h2 class="kicker"><span class="ta" lang="ta">நிகழ்வுகள்</span><span class="de"><?php esc_html_e( 'Nächste Events', 'tamil' ); ?></span></h2>
			<ul class="liste">
				<?php foreach ( $events as $id ) : ?>
					<li><span class="nr"><?php echo esc_html( wp_date( 'j.', (int) strtotime( (string) get_post_meta( (int) $id, 'event_datum', true ) ) ) ); ?></span><a href="<?php echo esc_url( get_permalink( (int) $id ) ); ?>"><?php echo esc_html( get_the_title( (int) $id ) ); ?></a></li>
				<?php endforeach; ?>
			</ul>
			<a class="btn btn-ghost hell btn-sm" href="<?php echo esc_url( tamil_rubrik( 'events' )['url'] ); ?>"><?php esc_html_e( 'Alle Events', 'tamil' ); ?></a>
		</div>
	<?php endif; ?>
	<div class="widget papier newsletter">
		<h2 class="kicker"><span class="ta" lang="ta"></span><span class="de"><?php esc_html_e( 'Newsletter', 'tamil' ); ?></span></h2>
		<?php
		get_template_part(
			'template-parts/newsletter-form',
			null,
			array(
				'id'   => 'nl-side',
				'text' => __( 'Einmal pro Woche das Wichtigste aus Nachrichten, Kino und Events.', 'tamil' ),
			)
		);
		?>
	</div>
	<?php if ( is_active_sidebar( 'seitenspalte' ) ) : ?>
		<?php dynamic_sidebar( 'seitenspalte' ); ?>
	<?php endif; ?>
</aside>
