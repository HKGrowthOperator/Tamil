<?php
/**
 * Termin-Kachel: Datumsblock (Safran, wenn der Termin in den nächsten sieben Tagen liegt), Art, Titel, Ort, Knöpfe.
 *
 * @var array $args { @type int $post Beitrags-ID, @type bool $kompakt Startseite: ohne Knöpfe. }
 */

defined( 'ABSPATH' ) || exit;

$post_id = (int) ( $args['post'] ?? get_the_ID() );
$kompakt = (bool) ( $args['kompakt'] ?? false );
$e       = function_exists( 'tamil_site_event' ) ? tamil_site_event( $post_id ) : array();
if ( ! $e ) {
	return;
}
$start   = date_create_immutable( $e['datum'], wp_timezone() );
$ts      = $start ? $start->getTimestamp() : time();
$ende    = '' !== $e['ende'] ? date_create_immutable( $e['ende'], wp_timezone() ) : false;
$bald    = $ts - time() < 7 * DAY_IN_SECONDS;
$land    = $e['land'];
$laender = 'DACH' === $land ? array( 'DE', 'AT', 'CH' ) : array_filter( array( $land ) );
$kat     = tamil_hauptkategorie( $post_id );
$art     = tamil_tags( $post_id )[0] ?? null; // Art des Termins (Kino, Kultur, Tanz …)
$link    = get_permalink( $post_id );
$ticket  = $e['ticket_url'];
$titel   = get_the_title( $post_id );
$zeit    = $start && strlen( $e['datum'] ) > 10 && '00:00' !== $start->format( 'H:i' ) ? $start->format( 'H:i' ) . ' Uhr' : '';
$tags    = wp_list_pluck( tamil_tags( $post_id ), 'slug' );
$bis     = $ende && $start && $ende->format( 'Y-m-d' ) !== $start->format( 'Y-m-d' ) ? $ende : null;
?>
<article class="termin<?php echo $bald ? ' bald' : ''; ?><?php echo $kompakt ? ' kompakt' : ''; ?>" data-ev="<?php echo esc_attr( implode( ' ', array_merge( $laender, $kat ? array( $kat->slug ) : array(), $tags ) ) ); ?>">
	<div class="datum" aria-hidden="true">
		<b><?php echo esc_html( wp_date( 'j', $ts ) ); ?></b>
		<span><?php echo esc_html( wp_date( 'M', $ts ) ); ?></span>
		<span class="wtag"><?php echo esc_html( $bis ? '– ' . wp_date( 'j. M', $bis->getTimestamp() ) : wp_date( 'D', $ts ) ); ?></span>
	</div>
	<div class="termin-text">
		<p class="meta">
			<?php echo tamil_rubrik_punkt( $kat, false, $art ? $art->name : '' ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_rubrik_punkt() ?>
			<?php
			if ( $zeit ) :
				?>
				<span><?php echo esc_html( $zeit ); ?></span><?php endif; ?>
			<?php
			if ( $land ) :
				?>
				<span><?php echo esc_html( 'DACH' === $land ? 'DE · AT · CH' : $land ); ?></span><?php endif; ?>
		</p>
		<h3><a href="<?php echo esc_url( $link ); ?>"><?php echo esc_html( $titel ); ?></a></h3>
		<?php
		if ( $e['ort'] ) :
			?>
			<p class="ort"><?php tamil_icon( 'pin', 'ico ico-sm' ); ?> <?php echo esc_html( $e['ort'] ); ?></p><?php endif; ?>
		<?php if ( ! $kompakt ) : ?>
			<div class="aktionen">
				<?php if ( $ticket ) : ?>
					<a class="knopf knopf-klein" href="<?php echo esc_url( $ticket ); ?>" target="_blank" rel="noopener nofollow"><?php tamil_icon( 'ticket', 'ico ico-sm' ); ?> <?php echo esc_html( ( '' !== $e['ticket_label'] ? $e['ticket_label'] : __( 'Tickets', 'tamil' ) ) ); ?></a>
				<?php endif; ?>
				<a class="knopf knopf-klein knopf-wa" href="<?php echo esc_url( 'https://wa.me/?text=' . rawurlencode( $titel . ' – ' . tamil_termin_text( $e['datum'], $e['ende'] ) . ' ' . $link ) ); ?>" target="_blank" rel="noopener"><?php tamil_icon( 'whatsapp', 'ico ico-sm' ); ?> <?php esc_html_e( 'Teilen', 'tamil' ); ?></a>
			</div>
		<?php endif; ?>
	</div>
</article>
