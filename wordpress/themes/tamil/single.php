<?php
/**
 * Beitrag: Kopf mit Vorspann und Teilen, Beitragsbild mit Bildnachweis, Termin-Angaben, Text mit Werbeplatz 03,
 * Schlagworte, Autorenbox, „Mehr aus …“, Seitenspalte.
 */

defined( 'ABSPATH' ) || exit;

get_header();

while ( have_posts() ) :
	the_post();
	$post_id = get_the_ID();
	$kat     = tamil_hauptkategorie( $post_id );
	$rubrik  = $kat ? tamil_rubrik( $kat->slug ) : null;
	$url     = (string) get_permalink();
	$titel   = get_the_title();
	$kino    = function_exists( 'tamil_site_kino_fakten' ) ? tamil_site_kino_fakten( $post_id ) : array();
	$event   = function_exists( 'tamil_site_event' ) ? tamil_site_event( $post_id ) : array();
	$inhalt  = (string) get_post_field( 'post_content', $post_id );
	$kette   = $kat ? array( array( $kat->name, (string) get_category_link( $kat ) ), array( $titel, '' ) ) : array( array( $titel, '' ) );
	?>
	<div class="lesebalken" aria-hidden="true"></div>
	<div class="container">
		<?php tamil_breadcrumb( $kette ); ?>
		<div class="with-sidebar">
			<article <?php post_class( 'artikel' ); ?>>
				<header class="artikel-kopf">
					<p class="badges">
						<?php if ( $kino ) : ?>
							<span class="badge gruen"><?php esc_html_e( 'Kinotermine', 'tamil' ); ?></span>
							<?php /* translators: %s: Datum */ ?>
							<span class="stand-badge"><?php echo esc_html( sprintf( __( 'aktualisiert %s', 'tamil' ), get_the_modified_date( 'j. F' ) ) ); ?></span>
						<?php elseif ( $kat ) : ?>
							<a class="badge" href="<?php echo esc_url( get_category_link( $kat ) ); ?>"><?php echo esc_html( $kat->name ); ?></a>
						<?php endif; ?>
						<?php
						if ( $event ) :
							?>
							<span class="badge soft"><?php tamil_icon( 'calendar', 'ico ico-xs' ); ?> <?php echo esc_html( tamil_termin_text( $event['datum'], $event['ende'] ) ); ?></span><?php endif; ?>
					</p>
					<h1><?php echo esc_html( $titel ); ?></h1>
					<p class="standfirst"><?php echo esc_html( tamil_standfirst( $post_id ) ); ?></p>
					<div class="byline">
						<span class="avatar" aria-hidden="true">T</span>
						<span><strong><?php echo esc_html( tamil_opt( 'autor_name' ) ); ?></strong>
						<?php
						/* translators: 1: Datum, 2: Minuten */
						echo esc_html( sprintf( _n( '%1$s, %2$d Minute Lesezeit', '%1$s, %2$d Minuten Lesezeit', tamil_lesezeit( $post_id ), 'tamil' ), get_the_date( 'j. F Y' ), tamil_lesezeit( $post_id ) ) );
						?>
						</span>
					</div>
					<?php tamil_share( $titel, $url ); ?>
				</header>

				<figure class="hero-bild">
					<?php
					echo tamil_bild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- tamil_bild() escapt selbst
						$post_id,
						'tamil-lead',
						array(
							'fetchpriority' => 'high',
							'loading'       => 'eager',
							'alt'           => (string) get_post_meta( (int) get_post_thumbnail_id(), '_wp_attachment_image_alt', true ),
						)
					); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped 
					?>
					<figcaption><span class="leise"><?php echo esc_html( tamil_bildnachweis( $post_id ) ); ?></span></figcaption>
				</figure>

				<?php if ( $event && ! str_contains( $inhalt, 'event-box' ) ) : ?>
					<?php
					get_template_part(
						'template-parts/article/termin',
						null,
						array(
							'post'  => $post_id,
							'event' => $event,
						)
					);
					?>
				<?php endif; ?>

				<div class="artikel-body<?php echo has_category( 'kueche' ) ? '' : ' initial'; ?>">
					<?php the_content(); ?>
					<?php
					wp_link_pages(
						array(
							'before' => '<nav class="pagination" aria-label="' . esc_attr__( 'Seiten des Beitrags', 'tamil' ) . '">',
							'after'  => '</nav>',
						)
					);
					?>
				</div>

				<?php
				get_template_part(
					'template-parts/article/quelle',
					null,
					array(
						'post'   => $post_id,
						'inhalt' => $inhalt,
					)
				);
				?>

				<div class="tags">
					<?php foreach ( tamil_tags( $post_id ) as $tag ) : ?>
						<a class="tag" href="<?php echo esc_url( get_tag_link( $tag ) ); ?>"><?php echo esc_html( $tag->name ); ?></a>
					<?php endforeach; ?>
					<?php
					if ( $kat ) :
						?>
						<a class="tag" href="<?php echo esc_url( get_category_link( $kat ) ); ?>"><?php echo esc_html( $kat->name ); ?></a><?php endif; ?>
				</div>
				<?php tamil_share( $titel, $url ); ?>
				<div class="autorenbox"><span class="avatar" aria-hidden="true">T</span><div><strong><?php echo esc_html( tamil_opt( 'autor_name' ) ); ?></strong><p><?php echo esc_html( tamil_opt( 'autor_text' ) ); ?></p></div></div>

				<?php $related = tamil_related( $post_id ); ?>
				<?php if ( $related ) : ?>
					<section class="section related">
						<?php /* translators: %s: Rubrik */ ?>
						<?php tamil_kicker( $kat ? $kat->slug : 'news', $kat ? sprintf( __( 'Mehr aus %s', 'tamil' ), $kat->name ) : __( 'Auch interessant', 'tamil' ), $rubrik ? $rubrik['url'] : '' ); ?>
						<div class="cards">
							<?php foreach ( $related as $id ) : ?>
								<?php get_template_part( 'template-parts/card', null, array( 'post' => $id ) ); ?>
							<?php endforeach; ?>
						</div>
					</section>
				<?php endif; ?>
			</article>
			<?php get_sidebar(); ?>
		</div>
	</div>
	<a class="fab-wa" href="<?php echo esc_url( 'https://wa.me/?text=' . rawurlencode( $titel . ' ' . $url ) ); ?>" target="_blank" rel="noopener" aria-label="<?php esc_attr_e( 'Per WhatsApp teilen', 'tamil' ); ?>"><?php tamil_icon( 'whatsapp' ); ?></a>
	<?php
endwhile;

get_footer();
