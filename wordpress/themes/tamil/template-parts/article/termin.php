<?php
/**
 * Termin-Angaben eines Beitrags (aus den Feldern „Vorspann und Termin“).
 *
 * @var array $args { @type int $post, @type array $event }
 */

defined( 'ABSPATH' ) || exit;

$post_id = (int) $args['post'];
$e       = $args['event'];
$start   = date_create_immutable( $e['datum'], wp_timezone() );
$zeit    = $start && strlen( $e['datum'] ) > 10 && '00:00' !== $start->format( 'H:i' ) ? $start->format( 'H:i' ) . ' Uhr' : '';
$laender = array(
	'DE'   => __( 'Deutschland', 'tamil' ),
	'AT'   => __( 'Österreich', 'tamil' ),
	'CH'   => __( 'Schweiz', 'tamil' ),
	'DACH' => 'DE · AT · CH',
);
$fakten  = array_filter(
	array(
		__( 'Wann', 'tamil' )         => tamil_termin_text( $e['datum'], $e['ende'] ),
		__( 'Uhrzeit', 'tamil' )      => $zeit,
		__( 'Wo', 'tamil' )           => $e['ort'],
		__( 'Land', 'tamil' )         => $laender[ $e['land'] ] ?? '',
		__( 'Veranstalter', 'tamil' ) => $e['veranstalter'],
		__( 'Preis', 'tamil' )        => $e['preis'],
	)
);
?>
<section class="termin-box" aria-label="<?php esc_attr_e( 'Termin', 'tamil' ); ?>">
	<dl class="fakten">
		<?php foreach ( $fakten as $label => $wert ) : ?>
			<div><dt><?php echo esc_html( $label ); ?></dt><dd><?php echo esc_html( $wert ); ?></dd></div>
		<?php endforeach; ?>
	</dl>
	<p class="aktionen">
		<?php if ( $e['ticket_url'] ) : ?>
			<a class="knopf" href="<?php echo esc_url( $e['ticket_url'] ); ?>" target="_blank" rel="noopener nofollow"><?php tamil_icon( 'ticket', 'ico ico-sm' ); ?> <?php echo esc_html( ( '' !== $e['ticket_label'] ? $e['ticket_label'] : __( 'Tickets', 'tamil' ) ) ); ?></a>
		<?php endif; ?>
		<a class="knopf knopf-wa" href="<?php echo esc_url( 'https://wa.me/?text=' . rawurlencode( get_the_title( $post_id ) . ' – ' . tamil_termin_text( $e['datum'], $e['ende'] ) . ' ' . get_permalink( $post_id ) ) ); ?>" target="_blank" rel="noopener"><?php tamil_icon( 'whatsapp', 'ico ico-sm' ); ?> <?php esc_html_e( 'Per WhatsApp teilen', 'tamil' ); ?></a>
	</p>
	<p class="klein leise"><?php esc_html_e( 'Angaben ohne Gewähr, bitte beim Veranstalter prüfen.', 'tamil' ); ?></p>
</section>
