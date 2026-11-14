<?php
/**
 * Template Name: Veranstaltungskalender
 *
 * Festkalender: Seitenkopf mit Foto, darunter in der linken Spalte „Ab heute“ als Tafel (der nächste Termin rot,
 * Weitersagen je Zeile), danach „Das Jahr“ mit den vergangenen Terminen dieses Jahres nach Monaten. Greift
 * automatisch für die Seite mit dem Slug „events“.
 */

defined( 'ABSPATH' ) || exit;

get_header();

$rubrik  = tamil_rubrik( 'events' );
$kommend = function_exists( 'tamil_site_upcoming_events' ) ? array_map( 'intval', tamil_site_upcoming_events( 60, array( 'fields' => 'ids' ) )->posts ) : array();
$jahr    = wp_date( 'Y' );
$heute   = current_time( 'Y-m-d' );
$vorbei  = function_exists( 'tamil_site_upcoming_events' ) ? tamil_ids(
	array(
		'posts_per_page' => 100,
		'meta_key'       => 'event_datum', // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_key
		'orderby'        => 'meta_value',
		'order'          => 'DESC',
		'meta_query'     => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
			array(
				'key'     => 'event_datum',
				'value'   => array( $jahr . '-01-01', $heute ),
				'compare' => 'BETWEEN',
				'type'    => 'CHAR',
			),
		),
	)
) : array();
$vorbei  = array_values( array_filter( $vorbei, static fn( $id ) => substr( (string) get_post_meta( $id, 'event_datum', true ), 0, 10 ) < $heute ) );
$monate  = array();
foreach ( $vorbei as $id ) {
	$monate[ substr( (string) get_post_meta( $id, 'event_datum', true ), 0, 7 ) ][] = $id;
}
// Foto im Kopf: der erste Termin oder Beitrag der Rubrik mit Foto; eine Grafik nur, wenn es kein Foto gibt (ungeschnitten).
$bild_id = tamil_leitbild(
	array_merge(
		$kommend,
		$vorbei,
		get_category_by_slug( 'events' ) ? tamil_ids(
			array(
				'posts_per_page' => 12,
				'category_name'  => 'events',
			)
		) : array()
	)
);
$figur   = $bild_id ? tamil_figur(
	$bild_id,
	array(
		'klasse' => 'bild kopf-bild',
		'size'   => 'tamil-card',
		'eager'  => true,
		'alt'    => true,
	)
) : '';
?>
<header class="seitenkopf<?php echo '' !== $figur ? ' mit-bild' : ''; ?>">
	<div class="wrap">
		<div class="sk-text">
			<h1><?php the_title(); ?></h1>
			<p class="satz"><?php echo esc_html( $rubrik['beschreibung'] ); ?></p>
			<p class="aktionen"><a class="textlink" href="<?php echo esc_url( tamil_seiten_url( 'kontakt', 'event-einreichen' ) ); ?>"><?php esc_html_e( 'Termin einreichen', 'tamil' ); ?></a></p>
			<section class="bogen" aria-labelledby="ab-heute">
				<div class="bogen-kopf">
					<h2 id="ab-heute"><?php esc_html_e( 'Ab heute', 'tamil' ); ?></h2>
					<p class="bogen-stand"><time datetime="<?php echo esc_attr( $heute ); ?>"><?php echo esc_html( tamil_stand( time() ) ); ?></time></p>
				</div>
				<?php
				if ( $kommend ) {
					tamil_feste_tafel( $kommend, array( 'teilen' => true ) );
				} else {
					echo '<p class="bogen-leer">' . esc_html__( 'Gerade steht kein kommender Termin im Kalender. Kennt ihr einen? Schickt ihn der Redaktion.', 'tamil' ) . '</p>';
				}
				?>
			</section>
			<?php
			if ( $kommend ) :
				?>
				<p class="legende"><?php esc_html_e( 'Rot steht auf tamil.de für den nächsten Termin.', 'tamil' ); ?></p><?php endif; ?>
		</div>
		<?php echo $figur; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_figur() ?>
	</div>
</header>
<?php tamil_leaderboard(); ?>

<?php if ( $monate ) : ?>
	<section class="abschnitt" aria-labelledby="das-jahr">
		<div class="wrap schmal">
			<div class="kopfzeile">
				<?php /* translators: %s: Jahr */ ?>
				<h2 id="das-jahr"><?php echo esc_html( sprintf( __( 'Das Jahr %s', 'tamil' ), $jahr ) ); ?></h2>
			</div>
			<p class="satz"><?php esc_html_e( 'Feste und Aufführungen, die schon waren, nach Monaten.', 'tamil' ); ?></p>
			<?php $erster = true; ?>
			<?php foreach ( $monate as $monat => $liste ) : ?>
				<?php $ts = (int) strtotime( $monat . '-01' ); ?>
				<details class="monat-block"<?php echo $erster ? ' open' : ''; ?>>
					<summary>
						<span class="monat-name"><?php echo esc_html( wp_date( 'F', $ts ) ); ?></span>
						<?php /* translators: %d: Anzahl */ ?>
						<span class="anzahl"><?php echo esc_html( sprintf( _n( '%d Termin', '%d Termine', count( $liste ), 'tamil' ), count( $liste ) ) ); ?></span>
					</summary>
					<table class="tafel jahr">
						<thead><tr><th scope="col"><?php esc_html_e( 'Tag', 'tamil' ); ?></th><th scope="col"><?php esc_html_e( 'Was und wo', 'tamil' ); ?></th></tr></thead>
						<tbody>
							<?php foreach ( $liste as $id ) : ?>
								<?php
								$start = date_create_immutable( (string) get_post_meta( $id, 'event_datum', true ), wp_timezone() );
								$ort   = trim( (string) get_post_meta( $id, 'event_ort', true ) );
								?>
								<tr>
									<td class="t-tag"><?php echo $start ? tamil_zeilen_tag( $start->getTimestamp(), 't' ) : ''; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_zeilen_tag() ?></td>
									<td class="was"><a href="<?php echo esc_url( get_permalink( $id ) ); ?>"><?php echo esc_html( get_the_title( $id ) ); ?></a>
									<?php
									if ( '' !== $ort ) :
										?>
										<span class="unter"><?php echo esc_html( $ort ); ?></span><?php endif; ?></td>
								</tr>
							<?php endforeach; ?>
						</tbody>
					</table>
				</details>
				<?php $erster = false; ?>
			<?php endforeach; ?>
		</div>
	</section>
<?php endif; ?>

<?php
while ( have_posts() ) :
	the_post();
	if ( '' !== trim( (string) get_the_content() ) ) :
		?>
		<section class="abschnitt"><div class="wrap schmal"><div class="inhalt"><?php the_content(); ?></div></div></section>
		<?php
	endif;
endwhile;

get_footer();
