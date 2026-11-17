<?php
/**
 * Template Name: Production
 *
 * Konzertreihe von Tamil.de: Claim, Tickets, die nächsten Termine und die Konzertbeiträge (Schlagwort aus dem
 * Customizer) als Listen mit Bild, danach der Seiteninhalt (Service für Konzertbesucher). Listen im Seiteninhalt, die
 * nur auf Beiträge dieser Website verlinken („Die Konzerte im Archiv“), erscheinen als Liste mit Bild wie alle Listen.
 * Greift automatisch für die Seite „production“.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Titel der Seite wie die Überschrift (Customizer „production_titel“): <title> und Vorschau sagen dasselbe wie das h1.
 *
 * @param string $titel Titel.
 * @param int    $id    Beitrag (bei the_title).
 */
function tamil_production_titel( $titel, $id = 0 ) {
	$eigen = tamil_opt( 'production_titel' );
	return '' !== $eigen && ( 0 === (int) $id || (int) $id === (int) get_queried_object_id() ) ? $eigen : $titel;
}
add_filter( 'single_post_title', 'tamil_production_titel' );
add_filter( 'the_title', 'tamil_production_titel', 10, 2 );

get_header();

$tag    = sanitize_title( tamil_opt( 'production_tag' ) );
$ids    = '' !== $tag ? tamil_ids(
	array(
		'posts_per_page' => 12,
		'tag'            => $tag,
	)
) : array();
$ticket = tamil_opt( 'production_ticket_url' );
$events = function_exists( 'tamil_site_upcoming_events' ) ? array_map( 'intval', tamil_site_upcoming_events( 4, array( 'fields' => 'ids' ) )->posts ) : array();
?>
<div class="innen">
	<header class="seitenkopf">
		<h1 class="seitenkopf__titel"><?php echo esc_html( tamil_opt( 'production_titel' ) ); ?></h1>
		<p class="seitenkopf__zeile"><?php echo esc_html( tamil_opt( 'production_claim' ) ); ?></p>
		<p class="seitenkopf__zeile"><?php echo esc_html( tamil_opt( 'production_text' ) ); ?></p>
		<p class="knoepfe">
			<?php
			if ( $ticket ) :
				?>
				<a class="knopf" href="<?php echo esc_url( $ticket ); ?>" target="_blank" rel="noopener nofollow"><?php echo esc_html( tamil_opt( 'production_ticket_label' ) ); ?></a><?php endif; ?>
			<a class="textlink" href="<?php echo esc_url( tamil_seiten_url( 'kontakt' ) ); ?>"><?php esc_html_e( 'Als Veranstalter anfragen', 'tamil' ); ?></a>
		</p>
	</header>
	<?php if ( $events ) : ?>
		<section class="block" aria-labelledby="naechste-titel">
			<div class="block-kopf">
				<h2 class="block-titel" id="naechste-titel"><?php esc_html_e( 'Die nächsten Termine', 'tamil' ); ?></h2>
				<a class="textlink" href="<?php echo esc_url( tamil_rubrik( 'events' )['url'] ); ?>"><?php esc_html_e( 'Alle Termine', 'tamil' ); ?></a>
			</div>
			<ul class="liste">
				<?php
				foreach ( $events as $tamil_id ) {
					echo tamil_anr_zeile( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_zeile()
						$tamil_id,
						array(
							'klasse' => 'zeile',
							'rubrik' => false,
							'ts'     => (int) strtotime( (string) get_post_meta( $tamil_id, 'event_datum', true ) ),
						)
					);
				}
				?>
			</ul>
		</section>
	<?php endif; ?>
	<?php if ( $ids ) : ?>
		<section class="block" aria-labelledby="konzerte-titel">
			<h2 class="block-titel" id="konzerte-titel"><?php esc_html_e( 'Die Konzerte', 'tamil' ); ?></h2>
			<?php echo tamil_zeilen( $ids ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_zeilen() ?>
		</section>
	<?php endif; ?>
	<?php
	while ( have_posts() ) :
		the_post();
		if ( '' !== trim( (string) get_the_content() ) ) :
			ob_start();
			the_content();
			$tamil_inhalt = (string) ob_get_clean();
			?>
			<section class="block seite__text"><div class="inhalt"><?php echo tamil_beitragslisten_mit_bild( $tamil_inhalt, $ids ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Inhalt aus the_content(), Listen escapt in tamil_zeilen() ?></div></section>
			<?php
		endif;
	endwhile;
	?>
</div>
<?php
get_footer();
