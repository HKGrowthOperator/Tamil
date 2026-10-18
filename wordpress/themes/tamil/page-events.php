<?php
/**
 * Template Name: Veranstaltungskalender
 *
 * Kommende Termine als Liste (nach Monat) und als Monatsraster, Filter nach Land und Art (Schlagwort des Termins).
 * Greift automatisch für die Seite mit dem Slug „events“.
 */

defined( 'ABSPATH' ) || exit;

get_header();

$rubrik = tamil_rubrik( 'events' );
$ids    = function_exists( 'tamil_site_upcoming_events' ) ? array_map( 'intval', tamil_site_upcoming_events( 60, array( 'fields' => 'ids' ) )->posts ) : array();
$monate = array();
foreach ( $ids as $id ) {
	$ts                                = (int) strtotime( (string) get_post_meta( $id, 'event_datum', true ) );
	$monate[ wp_date( 'Y-m', $ts ) ][] = $id;
}
$heute    = current_datetime();
$erster   = $heute->modify( 'first day of this month' )->setTime( 0, 0 );
$tage     = (int) $erster->format( 't' );
$offset   = (int) $erster->format( 'N' ) - 1;
$im_monat = array();
foreach ( $monate[ $erster->format( 'Y-m' ) ] ?? array() as $id ) {
	$im_monat[ (int) wp_date( 'j', (int) strtotime( (string) get_post_meta( $id, 'event_datum', true ) ) ) ][] = $id;
}
$filter = array(
	'DE'      => __( 'Deutschland', 'tamil' ),
	'AT'      => __( 'Österreich', 'tamil' ),
	'CH'      => __( 'Schweiz', 'tamil' ),
	'kino'    => __( 'Kino', 'tamil' ),
	'konzert' => __( 'Konzerte', 'tamil' ),
	'kultur'  => __( 'Kultur', 'tamil' ),
	'tanz'    => __( 'Tanz', 'tamil' ),
);
?>
<div class="container">
	<?php tamil_breadcrumb( array( array( get_the_title(), '' ) ) ); ?>
	<header class="seitenkopf">
		<h1><?php the_title(); ?> <span class="ta" lang="ta"><?php echo esc_html( $rubrik['tamil'] ); ?></span></h1>
		<p class="beschreibung"><?php echo esc_html( $rubrik['beschreibung'] ); ?></p>
		<div class="events-werkzeuge">
			<div class="toggle" role="group" aria-label="<?php esc_attr_e( 'Ansicht', 'tamil' ); ?>"><button type="button" data-view="liste" aria-pressed="true"><?php esc_html_e( 'Liste', 'tamil' ); ?></button><button type="button" data-view="monat" aria-pressed="false"><?php esc_html_e( 'Monat', 'tamil' ); ?></button></div>
			<div class="chips" data-filter-group="ev" role="group" aria-label="<?php esc_attr_e( 'Filter', 'tamil' ); ?>">
				<button type="button" class="chip" data-filter="alle" aria-pressed="true"><?php esc_html_e( 'Alle', 'tamil' ); ?></button>
				<?php foreach ( $filter as $key => $label ) : ?>
					<button type="button" class="chip" data-filter="<?php echo esc_attr( $key ); ?>" aria-pressed="false"><?php echo esc_html( $label ); ?></button>
				<?php endforeach; ?>
			</div>
		</div>
	</header>
	<div class="with-sidebar">
		<div>
			<?php
			while ( have_posts() ) :
				the_post();
				?>
				<?php
				if ( '' !== trim( (string) get_the_content() ) ) :
					?>
					<div class="artikel-body"><?php the_content(); ?></div><?php endif; ?>
			<?php endwhile; ?>
			<div data-view-panel="liste">
				<?php foreach ( $monate as $monat => $liste ) : ?>
					<?php /* translators: %d: Anzahl */ ?>
					<h2 class="monat-kopf"><?php echo esc_html( wp_date( 'F Y', (int) strtotime( $monat . '-01' ) ) ); ?> <span class="n"><?php echo esc_html( sprintf( _n( '%d Event', '%d Events', count( $liste ), 'tamil' ), count( $liste ) ) ); ?></span></h2>
					<div class="event-liste">
						<?php foreach ( $liste as $id ) : ?>
							<?php get_template_part( 'template-parts/event-card', null, array( 'post' => $id ) ); ?>
						<?php endforeach; ?>
					</div>
				<?php endforeach; ?>
				<p class="leer" data-filter-leer="ev"<?php echo $ids ? ' hidden' : ''; ?>><?php esc_html_e( 'Für diese Auswahl sind gerade keine Termine eingetragen.', 'tamil' ); ?> <a href="<?php echo esc_url( tamil_seiten_url( 'kontakt', 'event-einreichen' ) ); ?>"><?php esc_html_e( 'Event einreichen', 'tamil' ); ?></a></p>
			</div>
			<div data-view-panel="monat" hidden>
				<h2 class="monat-kopf"><?php echo esc_html( wp_date( 'F Y', $erster->getTimestamp() ) ); ?> <span class="n"><?php esc_html_e( 'Monatsansicht', 'tamil' ); ?></span></h2>
				<table class="raster">
					<thead><tr>
					<?php
					foreach ( array( 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So' ) as $d ) :
						?>
						<th scope="col"><?php echo esc_html( $d ); ?></th><?php endforeach; ?></tr></thead>
					<tbody><tr>
						<?php
						for ( $i = 0; $i < $offset; $i++ ) {
							echo '<td class="leer"></td>';
						}
						for ( $tag = 1; $tag <= $tage; $tag++ ) {
							$wochentag = ( $offset + $tag - 1 ) % 7;
							echo '<td class="' . ( $wochentag >= 5 ? 'wochenende' : '' ) . '"><span class="tag-nr">' . (int) $tag . '</span>';
							$liste = $im_monat[ $tag ] ?? array();
							foreach ( array_slice( $liste, 0, 2 ) as $id ) {
								$tags = get_the_tags( $id );
								$k    = $tags ? $tags[0]->slug : '';
								echo '<a class="pill ' . esc_attr( $k ) . '" href="' . esc_url( get_permalink( $id ) ) . '" title="' . esc_attr( get_the_title( $id ) ) . '">' . esc_html( get_the_title( $id ) ) . '</a>';
							}
							if ( count( $liste ) > 2 ) {
								/* translators: %d: Anzahl */
								echo '<span class="mehr">' . esc_html( sprintf( __( '+%d weitere', 'tamil' ), count( $liste ) - 2 ) ) . '</span>';
							}
							echo '</td>';
							if ( 6 === $wochentag && $tag < $tage ) {
								echo '</tr><tr>';
							}
						}
						$rest = ( 7 - ( $offset + $tage ) % 7 ) % 7;
						for ( $i = 0; $i < $rest; $i++ ) {
							echo '<td class="leer"></td>';
						}
						?>
					</tr></tbody>
				</table>
			</div>
			<div class="cta-band">
				<h2 class="kicker"><span class="ta" lang="ta">பதிவு</span><span class="de"><?php esc_html_e( 'Event einreichen', 'tamil' ); ?></span></h2>
				<h2><?php esc_html_e( 'Du veranstaltest etwas? Trag dein Event kostenlos ein.', 'tamil' ); ?></h2>
				<p><?php esc_html_e( 'Konzert, Tempelfest, Turnier oder Kinoabend – die Redaktion prüft die Angaben und nimmt das Event in den Kalender und in den Newsletter auf.', 'tamil' ); ?></p>
				<div><a class="btn btn-dark" href="<?php echo esc_url( tamil_seiten_url( 'kontakt', 'event-einreichen' ) ); ?>"><?php tamil_icon( 'plus', 'ico ico-sm' ); ?> <?php esc_html_e( 'Event einreichen', 'tamil' ); ?></a></div>
			</div>
		</div>
		<?php get_sidebar( null, array( 'events' => false ) ); ?>
	</div>
</div>
<?php
get_footer();
