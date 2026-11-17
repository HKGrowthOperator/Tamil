<?php
/**
 * Beitrag in klar2: Dachzeile, Titel, Vorspann, Leiste mit Lesezeit und „Per WhatsApp teilen“; großes Bild (am Handy
 * randlos) mit Nachweis; Text in einer Spalte von höchstens 560 px (am Tablet eine gemeinsame Kante für Kopf, Bild und
 * Text); Termin, Quelle, Schlagworte, Teilen und Redaktion; am Desktop rechts Werbeplatz 02; danach „Weiterlesen“.
 */

defined( 'ABSPATH' ) || exit;

get_header();

while ( have_posts() ) :
	the_post();
	$tamil_id      = (int) get_the_ID();
	$tamil_kat     = tamil_hauptkategorie( $tamil_id );
	$tamil_url     = (string) get_permalink();
	$tamil_titel   = get_the_title();
	$tamil_event   = function_exists( 'tamil_site_event' ) ? tamil_site_event( $tamil_id ) : array();
	$tamil_inhalt  = (string) get_post_field( 'post_content', $tamil_id );
	$tamil_ort     = trim( (string) get_post_meta( $tamil_id, 'ort', true ) );
	$tamil_film    = tamil_kino_film( $tamil_id );
	$tamil_minuten = tamil_lesezeit( $tamil_id );
	$tamil_rand    = function_exists( 'tamil_site_anzeige' ) ? tamil_site_anzeige( 'sidebar', false ) : '';
	// Bild aus der Kette; ein Bild aus dem Text steht schon im Text und wird oben nicht wiederholt
	$tamil_bild   = 'inhalt' === tamil_bildwahl( $tamil_id )['art'] ? '' : tamil_bild(
		$tamil_id,
		array(
			'eager'  => true,
			'klasse' => 'artikel__bild',
			'sizes'  => '(min-width: 1024px) 1040px, (min-width: 600px) 600px, 100vw',
		)
	);
	$tamil_teilen = array(
		array( 'Facebook', 'https://www.facebook.com/sharer/sharer.php?u=' . rawurlencode( $tamil_url ) ),
		array( 'X', 'https://twitter.com/intent/tweet?url=' . rawurlencode( $tamil_url ) . '&text=' . rawurlencode( $tamil_titel ) ),
		array( 'Telegram', 'https://t.me/share/url?url=' . rawurlencode( $tamil_url ) . '&text=' . rawurlencode( $tamil_titel ) ),
	);
	$tamil_leiste = array(
		/* translators: %d: Minuten */
		sprintf( _n( '%d Min. Lesezeit', '%d Min. Lesezeit', $tamil_minuten, 'tamil' ), $tamil_minuten ),
	);
	if ( '' !== $tamil_ort ) {
		$tamil_leiste[] = $tamil_ort;
	}
	if ( $tamil_film && '' !== $tamil_film['stand'] ) {
		// Stand aus den Kinodaten (Kinowoche), nicht aus dem Änderungsdatum; vorbei ist vorbei.
		$tamil_leiste[] = $tamil_film['stand'] . ( $tamil_film['bis'] < current_time( 'Y-m-d' ) ? ', ' . __( 'Spielzeit vorbei', 'tamil' ) : '' );
	}
	?>
	<article <?php post_class( 'artikel' . ( '' !== $tamil_rand ? ' artikel--mit-rand' : '' ) ); ?>>
		<header class="artikel__kopf">
			<p class="meta">
				<?php if ( $tamil_kat ) : ?>
					<span class="meta__rubrik"><a href="<?php echo esc_url( get_category_link( $tamil_kat ) ); ?>"><?php echo esc_html( $tamil_kat->name ); ?></a></span>
				<?php endif; ?>
				<time datetime="<?php echo esc_attr( get_the_date( 'Y-m-d' ) ); ?>"><?php echo esc_html( get_the_date( 'j. F Y' ) ); ?></time>
			</p>
			<h1 class="artikel__titel"><?php echo tamil_text( $tamil_titel ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_text() ?></h1>
			<?php $tamil_vorspann = tamil_vorspann_artikel( $tamil_id ); ?>
			<?php if ( '' !== $tamil_vorspann ) : ?>
				<p class="artikel__vorspann"><?php echo tamil_text( $tamil_vorspann ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_text() ?></p>
			<?php endif; ?>
			<div class="artikel__leiste">
				<span><?php echo esc_html( implode( ', ', $tamil_leiste ) ); ?></span>
				<a class="artikel__teilen" href="<?php echo esc_url( tamil_wa_teilen( $tamil_titel, $tamil_url ) ); ?>"><?php esc_html_e( 'Per WhatsApp teilen', 'tamil' ); ?></a>
			</div>
		</header>

		<?php if ( '' !== $tamil_bild ) : ?>
			<figure class="artikel__figur">
				<?php echo $tamil_bild; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_bild() ?>
				<?php if ( '' !== tamil_bild_nachweis_html( $tamil_id ) ) : ?>
					<figcaption class="artikel__nachweis"><?php echo wp_kses( tamil_bild_nachweis_html( $tamil_id ), tamil_nachweis_kses() ); ?></figcaption>
				<?php endif; ?>
			</figure>
		<?php endif; ?>

		<div class="artikel__haupt">
			<div class="artikel__text">
				<?php
				if ( $tamil_event && ! str_contains( $tamil_inhalt, 'event-box' ) ) {
					get_template_part(
						'template-parts/article/termin',
						null,
						array(
							'post'  => $tamil_id,
							'event' => $tamil_event,
						)
					);
				}
				?>
				<div class="inhalt">
					<?php the_content(); ?>
				</div>
				<?php
				wp_link_pages(
					array(
						'before' => '<nav class="seiten-links" aria-label="' . esc_attr__( 'Seiten des Beitrags', 'tamil' ) . '">',
						'after'  => '</nav>',
					)
				);
				get_template_part(
					'template-parts/article/quelle',
					null,
					array(
						'post'   => $tamil_id,
						'inhalt' => $tamil_inhalt,
					)
				);
				?>
				<?php if ( tamil_tags( $tamil_id ) ) : ?>
					<p class="schlagworte">
						<span class="schlagworte__titel"><?php esc_html_e( 'Schlagworte', 'tamil' ); ?></span>
						<?php foreach ( tamil_tags( $tamil_id ) as $tamil_tag ) : ?>
							<a href="<?php echo esc_url( get_tag_link( $tamil_tag ) ); ?>"><?php echo esc_html( $tamil_tag->name ); ?></a>
						<?php endforeach; ?>
					</p>
				<?php endif; ?>
				<div class="teilen" role="group" aria-label="<?php esc_attr_e( 'Teilen', 'tamil' ); ?>">
					<a class="knopf" href="<?php echo esc_url( tamil_wa_teilen( $tamil_titel, $tamil_url ) ); ?>"><?php esc_html_e( 'Per WhatsApp schicken', 'tamil' ); ?></a>
					<?php foreach ( $tamil_teilen as [ $tamil_name, $tamil_href ] ) : ?>
						<a class="textlink" href="<?php echo esc_url( $tamil_href ); ?>" target="_blank" rel="noopener"><?php echo esc_html( $tamil_name ); ?></a>
					<?php endforeach; ?>
					<a class="textlink" href="<?php echo esc_url( 'mailto:?subject=' . rawurlencode( $tamil_titel ) . '&body=' . rawurlencode( $tamil_url ), array( 'mailto' ) ); ?>"><?php esc_html_e( 'E-Mail', 'tamil' ); ?></a>
					<button type="button" class="textlink knopf-text" data-copy="<?php echo esc_attr( $tamil_url ); ?>"><?php esc_html_e( 'Link kopieren', 'tamil' ); ?></button>
				</div>
				<p class="autor"><strong><?php echo esc_html( tamil_opt( 'autor_name' ) ); ?></strong> <?php echo esc_html( tamil_opt( 'autor_text' ) ); ?></p>
			</div>
			<?php
			if ( '' !== $tamil_rand ) :
				?>
				<aside class="artikel__rand" aria-label="<?php esc_attr_e( 'Anzeige', 'tamil' ); ?>"><?php echo $tamil_rand; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Werbeplatz aus dem Plugin, dort escapt ?></aside>
			<?php endif; ?>
		</div>
	</article>
	<?php tamil_leaderboard( 'innen anzeige-zwischen' ); ?>

	<?php $tamil_related = tamil_related( $tamil_id, 4 ); ?>
	<?php if ( $tamil_related ) : ?>
		<section class="weiterlesen innen" aria-labelledby="weiterlesen-titel">
			<div class="block-kopf">
				<h2 class="block-titel" id="weiterlesen-titel"><?php esc_html_e( 'Weiterlesen', 'tamil' ); ?></h2>
				<?php if ( $tamil_kat ) : ?>
					<?php /* translators: %s: Rubrik */ ?>
					<a class="textlink" href="<?php echo esc_url( get_category_link( $tamil_kat ) ); ?>"><?php echo esc_html( sprintf( __( 'Mehr aus %s', 'tamil' ), $tamil_kat->name ) ); ?></a>
				<?php endif; ?>
			</div>
			<div class="neben">
				<?php
				foreach ( $tamil_related as $tamil_r ) {
					echo tamil_anr_stueck( $tamil_r ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_stueck()
				}
				?>
			</div>
		</section>
	<?php endif; ?>
	<?php
endwhile;

get_footer();
