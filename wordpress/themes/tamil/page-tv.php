<?php
/**
 * Template Name: Tamil TV
 *
 * Tamil TV ist pausiert: ohne Sender im Customizer ein ruhiger Zustand „Tamil TV kommt“ mit Symbolbild aus dem
 * Rubrik-Pool und Wegen zu Kino und Entertainment. Der alte Seiteninhalt (Player-Reste, Bildschirmfotos, „Share on“)
 * wird nicht gezeigt. Stehen Sender im Customizer (Name | HLS-Adresse), erscheinen die Player; der Stream startet erst
 * nach Klick (Datenschutz). Die Seite steht nicht im Rubrikband und nicht unter „Mehr“.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Titel der Seite in normaler Schreibung: Der Altbestand heißt „TAMIL TV CHANNEL“; <title>, Vorschau und Überschrift
 * sagen „Tamil TV“.
 *
 * @param string $titel Titel.
 * @param int    $id    Beitrag (bei the_title).
 */
function tamil_tv_titel( $titel, $id = 0 ) {
	$seite = (int) get_queried_object_id();
	if ( ( 0 === (int) $id || (int) $id === $seite ) && preg_match( '/^[^a-z]*$/u', wp_strip_all_tags( (string) $titel ) ) ) {
		return __( 'Tamil TV', 'tamil' );
	}
	return $titel;
}
add_filter( 'single_post_title', 'tamil_tv_titel' );
add_filter( 'the_title', 'tamil_tv_titel', 10, 2 );

get_header();

$tamil_sender = array();
foreach ( (array) preg_split( '/\r\n|\r|\n/', tamil_opt( 'tv_sender' ) ) as $tamil_zeile ) {
	$tamil_teile = array_map( 'trim', explode( '|', (string) $tamil_zeile ) );
	if ( 2 === count( $tamil_teile ) && '' !== $tamil_teile[0] && '' !== $tamil_teile[1] ) {
		$tamil_sender[] = $tamil_teile;
	}
}
?>
<div class="innen">
	<?php if ( $tamil_sender ) : ?>
		<header class="seitenkopf">
			<h1 class="seitenkopf__titel"><?php the_title(); ?></h1>
			<p class="seitenkopf__zeile"><?php echo esc_html( tamil_opt( 'tv_text' ) ); ?></p>
		</header>
		<section class="block">
			<ul class="sender">
				<?php foreach ( $tamil_sender as [ $tamil_name, $tamil_stream ] ) : ?>
					<li>
						<div class="player" data-stream="<?php echo esc_url( $tamil_stream ); ?>">
							<?php /* translators: %s: Sender */ ?>
							<button type="button" class="play knopf" aria-label="<?php echo esc_attr( sprintf( __( '%s abspielen', 'tamil' ), $tamil_name ) ); ?>"><?php esc_html_e( 'Abspielen', 'tamil' ); ?></button>
						</div>
						<h2 class="sender__name"><?php echo esc_html( $tamil_name ); ?></h2>
						<p class="sender__zeile"><?php esc_html_e( 'Live-Stream im Browser, startet erst nach Klick.', 'tamil' ); ?></p>
					</li>
				<?php endforeach; ?>
			</ul>
		</section>
	<?php else : ?>
		<section class="tv-pause" aria-labelledby="tv-titel">
			<div class="tv-pause__text">
				<h1 class="seitenkopf__titel" id="tv-titel"><?php esc_html_e( 'Tamil TV kommt', 'tamil' ); ?></h1>
				<p class="seitenkopf__zeile"><?php esc_html_e( 'Wir richten die Sender gerade neu ein. Sobald sie laufen, könnt ihr hier tamilisches Fernsehen im Browser schauen; der Stream startet erst nach eurem Klick.', 'tamil' ); ?></p>
				<p class="aktionen">
					<a class="textlink" href="<?php echo esc_url( tamil_rubrik( 'kino' )['url'] ); ?>"><?php esc_html_e( 'Bis dahin: tamilisches Kino', 'tamil' ); ?></a>
					<a class="textlink" href="<?php echo esc_url( tamil_rubrik( 'entertainment' )['url'] ); ?>"><?php esc_html_e( 'Entertainment', 'tamil' ); ?></a>
				</p>
			</div>
			<div class="rahmen r169 tv-pause__bild">
				<?php echo tamil_pool_img( 'entertainment', array( 'sofort' => true ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_pool_img() ?>
			</div>
		</section>
	<?php endif; ?>
</div>
<?php
get_footer();
