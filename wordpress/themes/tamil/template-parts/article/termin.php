<?php
/**
 * Termin eines Beitrags (Felder „Vorspann und Termin“) als Kasten ohne Kasten: Linie in Titan Red oben, Titel, Angaben
 * Zeile für Zeile, darunter Tickets, Weitersagen und der Weg zu allen Terminen.
 *
 * @var array $args { @type int $post, @type array $event }
 */

defined( 'ABSPATH' ) || exit;

$tamil_id      = (int) $args['post'];
$tamil_e       = $args['event'];
$tamil_laender = array(
	'DE'   => __( 'Deutschland', 'tamil' ),
	'AT'   => __( 'Österreich', 'tamil' ),
	'CH'   => __( 'Schweiz', 'tamil' ),
	'DACH' => __( 'Deutschland, Österreich und Schweiz', 'tamil' ),
);
$tamil_angaben = array_filter(
	array(
		__( 'Wann', 'tamil' )         => tamil_termin_text( (string) $tamil_e['datum'], (string) $tamil_e['ende'] ),
		__( 'Wo', 'tamil' )           => trim( (string) $tamil_e['ort'] ),
		__( 'Veranstalter', 'tamil' ) => trim( (string) $tamil_e['veranstalter'] ),
		__( 'Land', 'tamil' )         => $tamil_laender[ $tamil_e['land'] ] ?? '',
		__( 'Preis', 'tamil' )        => trim( (string) $tamil_e['preis'] ),
	)
);
$tamil_titel   = get_the_title( $tamil_id );
$tamil_vorbei  = substr( (string) $tamil_e['datum'], 0, 10 ) < current_time( 'Y-m-d' ) && ( '' === (string) $tamil_e['ende'] || substr( (string) $tamil_e['ende'], 0, 10 ) < current_time( 'Y-m-d' ) );
?>
<section class="termin-box" aria-labelledby="termin-titel">
	<h2 class="termin-box__titel" id="termin-titel"><?php echo esc_html( $tamil_vorbei ? __( 'Termin (vorbei)', 'tamil' ) : __( 'Termin', 'tamil' ) ); ?></h2>
	<dl class="angaben">
		<?php foreach ( $tamil_angaben as $tamil_label => $tamil_wert ) : ?>
			<div><dt><?php echo esc_html( $tamil_label ); ?></dt><dd><?php echo esc_html( $tamil_wert ); ?></dd></div>
		<?php endforeach; ?>
	</dl>
	<p class="aktionen">
		<?php if ( ! empty( $tamil_e['ticket_url'] ) && ! $tamil_vorbei ) : ?>
			<a class="textlink" href="<?php echo esc_url( $tamil_e['ticket_url'] ); ?>" target="_blank" rel="noopener nofollow"><?php echo esc_html( '' !== (string) $tamil_e['ticket_label'] ? $tamil_e['ticket_label'] : __( 'Tickets', 'tamil' ) ); ?></a>
		<?php endif; ?>
		<a class="textlink" href="<?php echo esc_url( tamil_wa_teilen( $tamil_titel . ', ' . tamil_termin_text( (string) $tamil_e['datum'], (string) $tamil_e['ende'] ), (string) get_permalink( $tamil_id ) ) ); ?>"><?php esc_html_e( 'Per WhatsApp schicken', 'tamil' ); ?></a>
		<a class="textlink" href="<?php echo esc_url( tamil_rubrik( 'events' )['url'] ); ?>"><?php esc_html_e( 'Alle Termine', 'tamil' ); ?></a>
	</p>
	<p class="termin-box__hinweis"><?php esc_html_e( 'Angaben ohne Gewähr, bitte beim Veranstalter prüfen.', 'tamil' ); ?></p>
</section>
