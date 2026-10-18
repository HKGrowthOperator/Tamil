<?php
/**
 * Template Name: Production
 *
 * Konzertreihe von Tamil.de: Claim, Tickets, Plakate (Beiträge mit dem Production-Schlagwort), Seiteninhalt
 * (Service für Konzertbesucher) und die nächsten Termine. Greift automatisch für die Seite „production“.
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
$events = function_exists( 'tamil_site_upcoming_events' ) ? tamil_site_upcoming_events( 3, array( 'fields' => 'ids' ) )->posts : array();
?>
<section class="buehne buehne-seite-kopf" aria-label="<?php echo esc_attr( tamil_opt( 'production_titel' ) ); ?>">
	<div class="container">
		<h2 class="kicker"><span class="ta" lang="ta">நிகழ்ச்சிகள்</span><span class="de"><?php echo esc_html( tamil_opt( 'production_titel' ) ); ?></span></h2>
		<h1><?php echo esc_html( tamil_opt( 'production_claim' ) ); ?></h1>
		<p class="standfirst"><?php echo esc_html( tamil_opt( 'production_text' ) ); ?></p>
		<p class="aktionen">
			<?php
			if ( $ticket ) :
				?>
				<a class="btn btn-gold" href="<?php echo esc_url( $ticket ); ?>" target="_blank" rel="noopener nofollow"><?php tamil_icon( 'ticket', 'ico ico-sm' ); ?> <?php echo esc_html( tamil_opt( 'production_ticket_label' ) ); ?></a><?php endif; ?>
			<a class="btn btn-ghost hell" href="<?php echo esc_url( tamil_seiten_url( 'kontakt' ) ); ?>"><?php esc_html_e( 'Als Veranstalter anfragen', 'tamil' ); ?></a>
		</p>
	</div>
</section>
<div class="container">
	<?php if ( $ids ) : ?>
		<section class="section">
			<?php tamil_kicker( 'events', __( 'Die Konzerte', 'tamil' ) ); ?>
			<div class="plakate">
				<?php foreach ( $ids as $id ) : ?>
					<article class="plakat">
						<a class="media" href="<?php echo esc_url( get_permalink( $id ) ); ?>" tabindex="-1" aria-hidden="true"><?php echo tamil_bild( $id, 'tamil-card', array( 'loading' => 'lazy' ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?></a>
						<h3><a href="<?php echo esc_url( get_permalink( $id ) ); ?>"><?php echo esc_html( get_the_title( $id ) ); ?></a></h3>
						<?php tamil_meta( $id, false ); ?>
					</article>
				<?php endforeach; ?>
			</div>
		</section>
	<?php endif; ?>
	<?php
	while ( have_posts() ) :
		the_post();
		?>
		<?php if ( '' !== trim( (string) get_the_content() ) ) : ?>
			<section class="section"><div class="artikel-body lesebreite"><?php the_content(); ?></div></section>
		<?php endif; ?>
	<?php endwhile; ?>
	<?php if ( $events ) : ?>
		<section class="section">
			<?php tamil_kicker( 'events', __( 'Nächste Termine', 'tamil' ), tamil_rubrik( 'events' )['url'], __( 'Alle Events', 'tamil' ) ); ?>
			<div class="events-teaser">
				<?php foreach ( $events as $id ) : ?>
					<?php
					get_template_part(
						'template-parts/event-card',
						null,
						array(
							'post'    => (int) $id,
							'kompakt' => true,
						)
					);
					?>
				<?php endforeach; ?>
			</div>
		</section>
	<?php endif; ?>
</div>
<?php
get_footer();
