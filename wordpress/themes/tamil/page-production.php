<?php
/**
 * Template Name: Production
 *
 * Konzertreihe von Tamil.de: Claim, Tickets, die Konzertbeiträge (Schlagwort aus dem Customizer) als Strom,
 * Seiteninhalt (Service für Konzertbesucher) und die nächsten Termine als Tafel. Greift automatisch für die Seite
 * „production“.
 */

defined( 'ABSPATH' ) || exit;

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
<header class="seitenkopf">
	<div class="wrap">
		<h1><?php echo esc_html( tamil_opt( 'production_titel' ) ); ?></h1>
		<p class="satz"><?php echo esc_html( tamil_opt( 'production_claim' ) ); ?></p>
		<p class="satz"><?php echo esc_html( tamil_opt( 'production_text' ) ); ?></p>
		<p class="aktionen">
			<?php
			if ( $ticket ) :
				?>
				<a class="knopf" href="<?php echo esc_url( $ticket ); ?>" target="_blank" rel="noopener nofollow"><?php echo esc_html( tamil_opt( 'production_ticket_label' ) ); ?></a><?php endif; ?>
			<a class="textlink" href="<?php echo esc_url( tamil_seiten_url( 'kontakt' ) ); ?>"><?php esc_html_e( 'Als Veranstalter anfragen', 'tamil' ); ?></a>
		</p>
	</div>
</header>
<?php if ( $events ) : ?>
	<section class="abschnitt" aria-labelledby="naechste-titel">
		<div class="wrap schmal">
			<section class="bogen">
				<div class="bogen-kopf"><h2 id="naechste-titel"><?php esc_html_e( 'Die nächsten Termine', 'tamil' ); ?></h2></div>
				<?php tamil_feste_tafel( $events, array( 'teilen' => true ) ); ?>
				<p class="bogen-fuss"><a class="textlink" href="<?php echo esc_url( tamil_rubrik( 'events' )['url'] ); ?>"><?php esc_html_e( 'Ganzer Festkalender', 'tamil' ); ?></a></p>
			</section>
		</div>
	</section>
<?php endif; ?>
<?php if ( $ids ) : ?>
	<section class="abschnitt" aria-labelledby="konzerte-titel">
		<div class="wrap">
			<h2 id="konzerte-titel" class="strom-kopf"><?php esc_html_e( 'Die Konzerte', 'tamil' ); ?></h2>
			<?php
			tamil_strom(
				$ids,
				array(
					'monat' => '',
					'titel' => 'h3',
				)
			);
			?>
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
