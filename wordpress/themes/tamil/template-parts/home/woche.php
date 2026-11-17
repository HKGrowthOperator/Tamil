<?php
/**
 * „Diese Woche“ (dunkel, volle Breite): Kino-Beiträge der letzten 30 Tage als Bildkacheln (die erste groß 4:3 mit
 * Titel im Bild, die zweite 8:3 mit Titel darunter), „Im Kino“ mit den Filmen, die ab heute laufen, und „Termine“ mit
 * den nächsten Terminen, alle als Bildkacheln. Fehlt etwas, sagt eine Bildkachel, wo es weitergeht.
 *
 * @var array $args { @type array $woche Ergebnis von tamil_woche_auswahl(). }
 */

defined( 'ABSPATH' ) || exit;

$tamil_woche   = (array) ( $args['woche'] ?? array() );
$tamil_ids     = array_map( 'intval', (array) ( $tamil_woche['bilder'] ?? array() ) );
$tamil_filme   = (array) ( $tamil_woche['filme'] ?? array() );
$tamil_termine = array_map( 'intval', (array) ( $tamil_woche['termine'] ?? array() ) );
$tamil_gross   = isset( $tamil_ids[0] ) ? tamil_anr_imbild(
	$tamil_ids[0],
	array(
		'klasse' => 'kachel kachel--gross',
		'ebene'  => 'h3',
		'sizes'  => '(min-width: 1024px) 780px, (min-width: 600px) calc(100vw - 48px), calc(100vw - 32px)',
	)
) : '';
$tamil_klein   = isset( $tamil_ids[1] ) ? tamil_anr_imbild(
	$tamil_ids[1],
	array(
		'klasse' => 'kachel kachel--klein',
		'rahmen' => 'r83',
		'ebene'  => 'h3',
		'unter'  => true,
		'sizes'  => '(min-width: 1024px) 380px, (min-width: 600px) 50vw, 100vw',
	)
) : '';
$tamil_kino    = tamil_rubrik( 'kino' );
$tamil_klassen = array( 'woche__raster' );
if ( '' === $tamil_gross ) {
	$tamil_klassen[] = 'ohne-gross';
}
if ( '' === $tamil_klein ) {
	$tamil_klassen[] = 'ohne-klein';
}
$tamil_klassen[] = 'termine-' . max( 1, count( $tamil_termine ) );
?>
<section class="woche" id="diese-woche" aria-labelledby="t-woche">
	<div class="innen">
		<h2 class="woche__titel" id="t-woche"><?php esc_html_e( 'Diese Woche', 'tamil' ); ?></h2>
		<div class="<?php echo esc_attr( implode( ' ', $tamil_klassen ) ); ?>">
			<?php
			echo $tamil_gross . $tamil_klein; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild()
			?>
			<div class="woche__gruppe woche__gruppe--kino">
				<p class="woche__art" id="t-kino"><?php esc_html_e( 'Im Kino', 'tamil' ); ?></p>
				<ul aria-labelledby="t-kino">
					<?php
					foreach ( $tamil_filme as $tamil_f ) {
						echo tamil_grafik_kino( $tamil_f ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_grafik_kino()
					}
					if ( ! $tamil_filme ) {
						echo tamil_grafik_leer( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_grafik_leer()
							__( 'Kinoprogramm', 'tamil' ),
							__( 'Für diese Woche kennen wir keine tamilische Vorstellung. Kinostarts, Kritiken und frühere Spielorte stehen in der Rubrik Kino.', 'tamil' ),
							$tamil_kino['url'],
							'kino'
						);
					}
					?>
				</ul>
			</div>
			<div class="woche__gruppe woche__gruppe--termine">
				<p class="woche__art" id="t-termine"><?php esc_html_e( 'Termine', 'tamil' ); ?></p>
				<ul aria-labelledby="t-termine">
					<?php
					foreach ( $tamil_termine as $tamil_id ) {
						echo tamil_grafik_termin( $tamil_id, 'h3', count( $tamil_termine ) < 3 ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_grafik_termin()
					}
					if ( ! $tamil_termine ) {
						echo tamil_grafik_leer( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_grafik_leer()
							__( 'Termin einreichen', 'tamil' ),
							__( 'Gerade steht kein kommender Termin im Kalender. Kennt ihr einen? Schickt ihn der Redaktion, kostenlos für Vereine, Tempel und Schulen.', 'tamil' ),
							tamil_seiten_url( 'kontakt', 'event-einreichen' ),
							'events'
						);
					}
					?>
				</ul>
			</div>
		</div>
		<p class="woche__weiter">
			<a class="textlink" href="<?php echo esc_url( tamil_rubrik( 'events' )['url'] ); ?>"><?php esc_html_e( 'Alle Termine', 'tamil' ); ?></a>
			<a class="textlink" href="<?php echo esc_url( $tamil_kino['url'] ); ?>"><?php esc_html_e( 'Kino nach Stadt', 'tamil' ); ?></a>
		</p>
	</div>
</section>
