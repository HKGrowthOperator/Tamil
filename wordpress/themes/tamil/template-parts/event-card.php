<?php
/**
 * Termin-Karte mit Datumsblock (Liste und Startseite).
 *
 * @var array $args { @type int $post Beitrags-ID, @type bool $kompakt }
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
$land    = $e['land'];
$laender = 'DACH' === $land ? array( 'DE', 'AT', 'CH' ) : array_filter( array( $land ) );
$kat     = tamil_hauptkategorie( $post_id );
$art     = tamil_tags( $post_id )[0] ?? null; // Art des Termins (Kino, Kultur, Tanz …)
$link    = get_permalink( $post_id );
$ticket  = $e['ticket_url'];
$titel   = get_the_title( $post_id );
$zeit    = $start && strlen( $e['datum'] ) > 10 && '00:00' !== $start->format( 'H:i' ) ? $start->format( 'H:i' ) . ' Uhr' : '';
$tags    = wp_list_pluck( tamil_tags( $post_id ), 'slug' );
?>
<article class="event-card<?php echo $kompakt ? ' kompakt' : ''; ?>" data-ev="<?php echo esc_attr( implode( ' ', array_merge( $laender, $kat ? array( $kat->slug ) : array(), $tags ) ) ); ?>">
	<div class="date-badge" aria-hidden="true">
		<span class="tag-nr"><?php echo esc_html( wp_date( 'j', $ts ) ); ?></span>
		<span class="monat"><?php echo esc_html( wp_date( 'M', $ts ) ); ?></span>
		<span class="wtag"><?php echo esc_html( wp_date( 'D', $ts ) ); ?><?php echo $ende && $ende->format( 'Y-m-d' ) !== $start->format( 'Y-m-d' ) ? ' – ' . esc_html( $ende->format( 'j' ) ) . '.' : ''; ?></span>
	</div>
	<div>
		<p class="meta">
			<?php
			if ( $art || $kat ) :
				?>
				<span class="kat"><?php echo esc_html( $art ? $art->name : $kat->name ); ?></span><?php endif; ?>
			<?php
			if ( $land ) :
				?>
				<span><?php echo esc_html( 'DACH' === $land ? 'DE · AT · CH' : $land ); ?></span><?php endif; ?>
			<?php
			if ( $zeit ) :
				?>
				<span><?php echo esc_html( $zeit ); ?></span><?php endif; ?>
		</p>
		<h3><a href="<?php echo esc_url( $link ); ?>"><?php echo esc_html( $titel ); ?></a></h3>
		<?php
		if ( $e['ort'] ) :
			?>
			<p class="ort"><?php tamil_icon( 'pin', 'ico ico-sm' ); ?> <?php echo esc_html( $e['ort'] ); ?></p><?php endif; ?>
		<div class="aktionen">
			<?php if ( $ticket ) : ?>
				<a class="btn btn-primary btn-sm" href="<?php echo esc_url( $ticket ); ?>" target="_blank" rel="noopener nofollow"><?php tamil_icon( 'ticket', 'ico ico-sm' ); ?> <?php echo esc_html( ( '' !== $e['ticket_label'] ? $e['ticket_label'] : __( 'Tickets', 'tamil' ) ) ); ?></a>
			<?php endif; ?>
			<a class="btn btn-wa btn-sm" href="<?php echo esc_url( 'https://wa.me/?text=' . rawurlencode( $titel . ' – ' . tamil_termin_text( $e['datum'], $e['ende'] ) . ' ' . $link ) ); ?>" target="_blank" rel="noopener"><?php tamil_icon( 'whatsapp', 'ico ico-sm' ); ?> <?php esc_html_e( 'Teilen', 'tamil' ); ?></a>
			<?php
			if ( ! $kompakt ) :
				?>
				<a class="btn btn-ghost btn-sm" href="<?php echo esc_url( $link ); ?>"><?php esc_html_e( 'Details', 'tamil' ); ?></a><?php endif; ?>
		</div>
	</div>
</article>
