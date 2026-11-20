<?php
/**
 * Template Name: Veranstaltungskalender
 *
 * Termine in klar2: Seitenkopf mit „Termin einreichen“; „Ab heute“ auf Titan Red mit den nächsten Terminen als
 * Bildkarten (Datum des Termins in der Dachzeile, Titel im Bild, Ort und Eintritt darunter); „Kommende Termine“ nach
 * Monaten als Bildkarten (Datum mit Uhrzeit in der Dachzeile, Ort, Veranstalter und Eintritt unter dem Bild), mit
 * Filtern nach Land und Stadt (nur mit Skript sichtbar); „Das Jahr“ mit den vergangenen Terminen dieses Jahres nach
 * Monaten zum Aufklappen, ebenfalls als Karten. Greift automatisch für die Seite mit dem Slug „events“.
 */

defined( 'ABSPATH' ) || exit;

get_header();

$tamil_rubrik  = tamil_rubrik( 'events' );
$tamil_kommend = function_exists( 'tamil_site_upcoming_events' ) ? array_map( 'intval', tamil_site_upcoming_events( 60, array( 'fields' => 'ids' ) )->posts ) : array();
$tamil_jahr    = wp_date( 'Y' );
$tamil_heute   = current_time( 'Y-m-d' );
$tamil_grenze  = wp_date( 'Y-m-d', (int) strtotime( $tamil_heute . ' +14 days' ) );
tamil_cache_fuellen( $tamil_kommend );

// Ab heute: die Termine der nächsten 14 Tage (höchstens sechs); sind es weniger als drei, die nächsten drei. Ein
// einzelner Termin steht quer (Bild links, Text rechts) über die volle Breite, zwei teilen sie sich.
$tamil_bald = array_values( array_filter( $tamil_kommend, static fn( $id ) => substr( (string) get_post_meta( $id, 'event_datum', true ), 0, 10 ) <= $tamil_grenze ) );
$tamil_bald = count( $tamil_bald ) >= 3 ? array_slice( $tamil_bald, 0, 6 ) : array_slice( $tamil_kommend, 0, 3 );

// Kommende Termine nach Monaten, dazu die Filterwerte (Land, Stadt) der Zeilen. Termine, die schon unter „Ab heute“
// stehen, tragen data-ab-heute: ohne Filter blendet das CSS sie hier aus (keine doppelten Karten), mit Filter zeigt die
// Liste wieder alle passenden Termine (app.js setzt dann .gefiltert).
$tamil_laender = array(
	'DE' => __( 'Deutschland', 'tamil' ),
	'AT' => __( 'Österreich', 'tamil' ),
	'CH' => __( 'Schweiz', 'tamil' ),
);
$tamil_zeilen  = array();
$tamil_staedte = array();
$tamil_land_da = array();
foreach ( $tamil_kommend as $tamil_id ) {
	$tamil_e = tamil_site_event( $tamil_id );
	if ( ! $tamil_e ) {
		continue;
	}
	$tamil_a     = tamil_termin_angaben( $tamil_id, $tamil_e );
	$tamil_stadt = __( 'Ort folgt', 'tamil' ) === $tamil_a['stadt'] ? '' : $tamil_a['stadt'];
	$tamil_land  = isset( $tamil_laender[ $tamil_a['land'] ] ) ? $tamil_a['land'] : '';
	if ( '' !== $tamil_stadt ) {
		$tamil_staedte[ sanitize_title( $tamil_stadt ) ] = $tamil_stadt;
	}
	if ( '' !== $tamil_land ) {
		$tamil_land_da[ $tamil_land ] = true;
	}
	$tamil_zusatz                                      = array_filter( array( $tamil_a['orte'], $tamil_a['eintritt'] ) );
	$tamil_zeilen[ substr( $tamil_a['iso'], 0, 7 ) ][] = tamil_anr_zeile(
		$tamil_id,
		array(
			'vorspann' => false,
			'ebene'    => 'h4',
			'dach'     => '<p class="meta"><time datetime="' . esc_attr( $tamil_a['iso'] ) . '">' . esc_html( $tamil_a['datum'] ) . '</time></p>',
			'zusatz'   => $tamil_zusatz ? '<p class="zeile__angaben">' . esc_html( implode( '. ', $tamil_zusatz ) ) . '</p>' : '',
			'attr'     => ' data-land="' . esc_attr( $tamil_land ) . '" data-stadt="' . esc_attr( '' !== $tamil_stadt ? sanitize_title( $tamil_stadt ) : '' ) . '"' . ( in_array( $tamil_id, $tamil_bald, true ) ? ' data-ab-heute' : '' ),
		)
	);
}
asort( $tamil_staedte, SORT_LOCALE_STRING );

// Das Jahr: vergangene Termine dieses Jahres nach Monaten
$tamil_vorbei = function_exists( 'tamil_site_upcoming_events' ) ? tamil_ids(
	array(
		'posts_per_page' => 100,
		'meta_key'       => 'event_datum', // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_key
		'orderby'        => 'meta_value',
		'order'          => 'DESC',
		'meta_query'     => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
			array(
				'key'     => 'event_datum',
				'value'   => array( $tamil_jahr . '-01-01', $tamil_heute ),
				'compare' => 'BETWEEN',
				'type'    => 'CHAR',
			),
		),
	)
) : array();
$tamil_vorbei = array_values( array_filter( $tamil_vorbei, static fn( $id ) => substr( (string) get_post_meta( $id, 'event_datum', true ), 0, 10 ) < $tamil_heute ) );
$tamil_monate = array();
foreach ( $tamil_vorbei as $tamil_id ) {
	$tamil_monate[ substr( (string) get_post_meta( $tamil_id, 'event_datum', true ), 0, 7 ) ][] = $tamil_id;
}
?>
<div class="innen">
	<header class="seitenkopf seitenkopf--signet">
		<?php tamil_signatur( 'kopf' ); ?>
		<h1 class="seitenkopf__titel"><?php the_title(); ?></h1>
		<p class="seitenkopf__zeile"><?php echo esc_html( $tamil_rubrik['beschreibung'] ); ?></p>
		<p class="aktionen"><a class="textlink" href="<?php echo esc_url( tamil_einreichen_url() ); ?>"><?php esc_html_e( 'Termin einreichen', 'tamil' ); ?></a></p>
	</header>
</div>

<section class="woche woche--seite" aria-labelledby="ab-heute">
	<?php tamil_signatur( 'flaeche' ); ?>
	<div class="innen">
		<h2 class="woche__titel" id="ab-heute"><?php esc_html_e( 'Ab heute', 'tamil' ); ?></h2>
		<p class="woche__art"><time datetime="<?php echo esc_attr( $tamil_heute ); ?>"><?php echo esc_html( tamil_stand( time() ) ); ?></time></p>
		<ul class="termine-raster<?php echo 1 === count( $tamil_bald ) ? ' termine-raster--eins' : ( 2 === count( $tamil_bald ) ? ' termine-raster--zwei' : '' ); ?>">
			<?php
			foreach ( $tamil_bald as $tamil_i => $tamil_id ) {
				// die erste Karte ist das größte Bild im ersten Bildschirm: sofort und vorrangig laden
				echo tamil_grafik_termin( $tamil_id, 'h3', true, true, 0 === $tamil_i ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_grafik_termin()
			}
			if ( ! $tamil_bald ) {
				echo tamil_grafik_leer( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_grafik_leer()
					__( 'Termin einreichen', 'tamil' ),
					__( 'Gerade steht kein kommender Termin im Kalender. Kennt ihr einen? Schickt ihn der Redaktion, kostenlos für Vereine, Tempel und Schulen.', 'tamil' ),
					tamil_einreichen_url(),
					'events'
				);
			}
			?>
		</ul>
	</div>
</section>

<div class="innen">
	<?php if ( $tamil_zeilen ) : ?>
		<section class="block kalender" aria-labelledby="kommend" data-filter>
			<h2 class="block-titel" id="kommend"><?php esc_html_e( 'Kommende Termine', 'tamil' ); ?></h2>
			<?php /* translators: %d: Anzahl */ ?>
			<p class="block__zeile" aria-live="polite"><span data-filter-zahl><?php echo esc_html( sprintf( _n( '%d Termin', '%d Termine', count( $tamil_kommend ), 'tamil' ), count( $tamil_kommend ) ) ); ?></span><?php esc_html_e( ', nach Monaten.', 'tamil' ); ?></p>
			<?php if ( count( $tamil_land_da ) > 1 || count( $tamil_staedte ) > 1 ) : ?>
				<div class="filter" hidden>
					<?php if ( count( $tamil_land_da ) > 1 ) : ?>
						<div class="chips" role="group" aria-label="<?php esc_attr_e( 'Land', 'tamil' ); ?>" data-filter-art="land">
							<button type="button" class="chip" data-wert="" aria-pressed="true"><?php esc_html_e( 'Alle Länder', 'tamil' ); ?></button>
							<?php foreach ( $tamil_laender as $tamil_k => $tamil_name ) : ?>
								<?php if ( isset( $tamil_land_da[ $tamil_k ] ) ) : ?>
									<button type="button" class="chip" data-wert="<?php echo esc_attr( $tamil_k ); ?>" aria-pressed="false"><?php echo esc_html( $tamil_name ); ?></button>
								<?php endif; ?>
							<?php endforeach; ?>
						</div>
					<?php endif; ?>
					<?php if ( count( $tamil_staedte ) > 1 ) : ?>
						<div class="chips" role="group" aria-label="<?php esc_attr_e( 'Stadt', 'tamil' ); ?>" data-filter-art="stadt">
							<button type="button" class="chip" data-wert="" aria-pressed="true"><?php esc_html_e( 'Alle Städte', 'tamil' ); ?></button>
							<?php foreach ( $tamil_staedte as $tamil_k => $tamil_name ) : ?>
								<button type="button" class="chip" data-wert="<?php echo esc_attr( (string) $tamil_k ); ?>" aria-pressed="false"><?php echo esc_html( $tamil_name ); ?></button>
							<?php endforeach; ?>
						</div>
					<?php endif; ?>
				</div>
			<?php endif; ?>
			<?php foreach ( $tamil_zeilen as $tamil_monat => $tamil_liste ) : ?>
				<section class="kalender__monat" aria-labelledby="<?php echo esc_attr( 'monat-' . $tamil_monat ); ?>">
					<h3 class="kalender__titel" id="<?php echo esc_attr( 'monat-' . $tamil_monat ); ?>"><?php echo esc_html( wp_date( 'F Y', (int) strtotime( $tamil_monat . '-01' ) ) ); ?></h3>
					<ul class="karten karten--raster">
						<?php echo implode( '', $tamil_liste ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_zeile() ?>
					</ul>
				</section>
			<?php endforeach; ?>
			<p class="leer__satz kalender__alle-oben"><?php esc_html_e( 'Alle kommenden Termine stehen oben unter „Ab heute“.', 'tamil' ); ?></p>
			<p class="leer__satz" data-filter-leer hidden><?php esc_html_e( 'Für diese Auswahl steht gerade kein Termin im Kalender.', 'tamil' ); ?> <a class="textlink" href="<?php echo esc_url( tamil_einreichen_url() ); ?>"><?php esc_html_e( 'Termin einreichen', 'tamil' ); ?></a></p>
		</section>
	<?php endif; ?>

	<?php tamil_leaderboard( 'anzeige-zwischen' ); ?>
	<?php if ( $tamil_monate ) : ?>
		<section class="block" aria-labelledby="das-jahr">
			<?php /* translators: %s: Jahr */ ?>
			<h2 class="block-titel" id="das-jahr"><?php echo esc_html( sprintf( __( 'Das Jahr %s', 'tamil' ), $tamil_jahr ) ); ?></h2>
			<p class="block__zeile"><?php esc_html_e( 'Feste und Aufführungen, die schon waren, nach Monaten.', 'tamil' ); ?></p>
			<?php $tamil_erster = true; ?>
			<?php foreach ( $tamil_monate as $tamil_monat => $tamil_liste ) : ?>
				<?php $tamil_ts = (int) strtotime( $tamil_monat . '-01' ); ?>
				<details class="monat"<?php echo $tamil_erster ? ' open' : ''; ?>>
					<summary>
						<span class="monat__name"><?php echo esc_html( wp_date( 'F', $tamil_ts ) ); ?></span>
						<?php /* translators: %d: Anzahl */ ?>
						<span class="monat__zahl"><?php echo esc_html( sprintf( _n( '%d Termin', '%d Termine', count( $tamil_liste ), 'tamil' ), count( $tamil_liste ) ) ); ?></span>
					</summary>
					<ul class="karten karten--raster">
						<?php
						foreach ( $tamil_liste as $tamil_id ) {
							// Bilder laden „lazy“: in zugeklappten Monaten holt der Browser sie erst beim Aufklappen
							echo tamil_anr_zeile( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_zeile()
								$tamil_id,
								array(
									'rubrik'   => false,
									'vorspann' => false,
									'ts'       => (int) strtotime( (string) get_post_meta( $tamil_id, 'event_datum', true ) ),
								)
							);
						}
						?>
					</ul>
				</details>
				<?php $tamil_erster = false; ?>
			<?php endforeach; ?>
		</section>
	<?php endif; ?>

	<?php
	while ( have_posts() ) :
		the_post();
		if ( '' !== trim( (string) get_the_content() ) ) :
			?>
			<section class="block seite__text"><div class="inhalt"><?php the_content(); ?></div></section>
			<?php
		endif;
	endwhile;
	?>
</div>
<?php
get_footer();
