<?php
/**
 * Template Name: Veranstaltungskalender
 *
 * Termine in klar2: Seitenkopf mit „Termin einreichen“; „Ab heute“ als dunkler Bereich mit den kommenden Terminen als
 * gestaltete Kacheln (Datum als größte Angabe nach dem Titel); „Das Jahr“ mit den vergangenen Terminen dieses Jahres
 * nach Monaten als Liste mit Bild. Greift automatisch für die Seite mit dem Slug „events“.
 */

defined( 'ABSPATH' ) || exit;

get_header();

$tamil_rubrik  = tamil_rubrik( 'events' );
$tamil_kommend = function_exists( 'tamil_site_upcoming_events' ) ? array_map( 'intval', tamil_site_upcoming_events( 60, array( 'fields' => 'ids' ) )->posts ) : array();
$tamil_jahr    = wp_date( 'Y' );
$tamil_heute   = current_time( 'Y-m-d' );
$tamil_vorbei  = function_exists( 'tamil_site_upcoming_events' ) ? tamil_ids(
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
$tamil_vorbei  = array_values( array_filter( $tamil_vorbei, static fn( $id ) => substr( (string) get_post_meta( $id, 'event_datum', true ), 0, 10 ) < $tamil_heute ) );
$tamil_monate  = array();
foreach ( $tamil_vorbei as $tamil_id ) {
	$tamil_monate[ substr( (string) get_post_meta( $tamil_id, 'event_datum', true ), 0, 7 ) ][] = $tamil_id;
}
tamil_cache_fuellen( $tamil_kommend );
?>
<div class="innen">
	<header class="seitenkopf">
		<h1 class="seitenkopf__titel"><?php the_title(); ?></h1>
		<p class="seitenkopf__zeile"><?php echo esc_html( $tamil_rubrik['beschreibung'] ); ?></p>
		<p class="aktionen"><a class="textlink" href="<?php echo esc_url( tamil_seiten_url( 'kontakt', 'event-einreichen' ) ); ?>"><?php esc_html_e( 'Termin einreichen', 'tamil' ); ?></a></p>
	</header>
</div>

<section class="woche woche--seite" aria-labelledby="ab-heute">
	<div class="innen">
		<h2 class="woche__titel" id="ab-heute"><?php esc_html_e( 'Ab heute', 'tamil' ); ?></h2>
		<p class="woche__art"><time datetime="<?php echo esc_attr( $tamil_heute ); ?>"><?php echo esc_html( tamil_stand( time() ) ); ?></time></p>
		<ul class="termine-raster">
			<?php
			foreach ( $tamil_kommend as $tamil_id ) {
				echo tamil_grafik_termin( $tamil_id, 'h3', true ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_grafik_termin()
			}
			if ( ! $tamil_kommend ) {
				echo tamil_grafik_leer( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_grafik_leer()
					__( 'Termin einreichen', 'tamil' ),
					__( 'Gerade steht kein kommender Termin im Kalender. Kennt ihr einen? Schickt ihn der Redaktion, kostenlos für Vereine, Tempel und Schulen.', 'tamil' ),
					tamil_seiten_url( 'kontakt', 'event-einreichen' )
				);
			}
			?>
		</ul>
	</div>
</section>

<div class="innen">
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
					<ul class="liste">
						<?php
						foreach ( $tamil_liste as $tamil_id ) {
							echo tamil_anr_zeile( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_zeile()
								$tamil_id,
								array(
									'klasse'   => 'zeile',
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
