<?php
/**
 * Seitenspalte: Werbeplatz 02, Top-Themen, nächste Termine, WhatsApp-Kanal, Widgets.
 *
 * @var array $args { @type bool $events Termine zeigen (Standard: ja). }
 */

defined( 'ABSPATH' ) || exit;

$auswahl      = tamil_home_auswahl();
$zeige_events = (bool) ( $args['events'] ?? true ) && function_exists( 'tamil_site_upcoming_events' );
$events       = $zeige_events ? tamil_site_upcoming_events( 4, array( 'fields' => 'ids' ) )->posts : array();
$kanal        = tamil_opt( 'social_whatsapp' );
?>
<aside class="seitenspalte">
	<?php tamil_anzeige( 'sidebar' ); ?>
	<?php if ( $auswahl['top'] ) : ?>
		<section class="kasten">
			<h2 class="kasten-titel"><?php esc_html_e( 'Top-Themen', 'tamil' ); ?></h2>
			<ol class="nummern">
				<?php foreach ( $auswahl['top'] as $id ) : ?>
					<li><a href="<?php echo esc_url( get_permalink( $id ) ); ?>"><?php echo esc_html( get_the_title( $id ) ); ?></a></li>
				<?php endforeach; ?>
			</ol>
		</section>
	<?php endif; ?>
	<?php if ( $events ) : ?>
		<section class="kasten">
			<h2 class="kasten-titel"><?php esc_html_e( 'Nächste Termine', 'tamil' ); ?></h2>
			<ul class="termin-liste">
				<?php foreach ( $events as $id ) : ?>
					<?php $ts = (int) strtotime( (string) get_post_meta( (int) $id, 'event_datum', true ) ); ?>
					<li><span class="mini-datum"><b><?php echo esc_html( wp_date( 'j', $ts ) ); ?></b><?php echo esc_html( wp_date( 'M', $ts ) ); ?></span><a href="<?php echo esc_url( get_permalink( (int) $id ) ); ?>"><?php echo esc_html( get_the_title( (int) $id ) ); ?></a></li>
				<?php endforeach; ?>
			</ul>
			<a class="mehr" href="<?php echo esc_url( tamil_rubrik( 'events' )['url'] ); ?>"><?php esc_html_e( 'Zum Kalender', 'tamil' ); ?><?php tamil_icon( 'arrow', 'ico ico-sm' ); ?></a>
		</section>
	<?php endif; ?>
	<?php if ( $kanal ) : ?>
		<section class="kasten kanal">
			<?php tamil_icon( 'whatsapp', 'ico kanal-ico' ); ?>
			<h2 class="kasten-titel"><?php esc_html_e( 'Tamil.de auf WhatsApp', 'tamil' ); ?></h2>
			<p><?php esc_html_e( 'Kinostarts, Feste und wichtige Nachrichten direkt aufs Handy. Ein Kanal, keine Gruppe: Deine Nummer bleibt privat.', 'tamil' ); ?></p>
			<a class="knopf knopf-wa" href="<?php echo esc_url( $kanal ); ?>" target="_blank" rel="noopener"><?php esc_html_e( 'Kanal abonnieren', 'tamil' ); ?></a>
		</section>
	<?php endif; ?>
	<?php if ( is_active_sidebar( 'seitenspalte' ) ) : ?>
		<?php dynamic_sidebar( 'seitenspalte' ); ?>
	<?php endif; ?>
</aside>
