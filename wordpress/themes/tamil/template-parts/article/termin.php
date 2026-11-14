<?php
/**
 * Termin eines Beitrags (Felder „Vorspann und Termin“) als Bogen: eine Zeile der Feste-Tafel, darunter Uhrzeit,
 * Land, Preis und Tickets.
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
	'DACH' => __( 'Deutschland, Österreich und Schweiz', 'tamil' ),
);
$fakten  = array_filter(
	array(
		__( 'Wann', 'tamil' )    => tamil_termin_text( $e['datum'], $e['ende'] ),
		__( 'Uhrzeit', 'tamil' ) => $zeit,
		__( 'Land', 'tamil' )    => $laender[ $e['land'] ] ?? '',
		__( 'Preis', 'tamil' )   => $e['preis'],
	)
);
$titel   = get_the_title( $post_id );
?>
<section class="bogen termin-bogen" aria-labelledby="termin-titel">
	<div class="bogen-kopf">
		<h2 id="termin-titel"><?php esc_html_e( 'Termin', 'tamil' ); ?></h2>
		<p class="bogen-stand"><?php esc_html_e( 'Angaben ohne Gewähr, bitte beim Veranstalter prüfen.', 'tamil' ); ?></p>
	</div>
	<?php
	tamil_feste_tafel(
		array( $post_id ),
		array( 'verlinken' => false )
	);
	?>
	<?php if ( $fakten ) : ?>
		<dl class="angaben">
			<?php foreach ( $fakten as $label => $wert ) : ?>
				<div><dt><?php echo esc_html( $label ); ?></dt><dd><?php echo esc_html( $wert ); ?></dd></div>
			<?php endforeach; ?>
		</dl>
	<?php endif; ?>
	<p class="bogen-fuss aktionen">
		<?php if ( $e['ticket_url'] ) : ?>
			<a class="textlink" href="<?php echo esc_url( $e['ticket_url'] ); ?>" target="_blank" rel="noopener nofollow"><?php echo esc_html( '' !== $e['ticket_label'] ? $e['ticket_label'] : __( 'Tickets', 'tamil' ) ); ?></a>
		<?php endif; ?>
		<a class="textlink" href="<?php echo esc_url( tamil_wa_teilen( $titel . ', ' . tamil_termin_text( $e['datum'], $e['ende'] ), (string) get_permalink( $post_id ) ) ); ?>"><?php esc_html_e( 'Per WhatsApp schicken', 'tamil' ); ?></a>
		<a class="textlink" href="<?php echo esc_url( tamil_rubrik( 'events' )['url'] ); ?>"><?php esc_html_e( 'Zum Festkalender', 'tamil' ); ?></a>
	</p>
</section>
