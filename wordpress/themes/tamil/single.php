<?php
/**
 * Beitrag: Kopf mit Datumsblock (Tag, Monat, Wochentag, Rubrik und Ort), Titel, Vorspann und „Per WhatsApp
 * schicken“; Foto 16:9 mit Nachweis; Text in der Mitte mit Termin-Tafel, Werbeplatz 03, Quelle, Schlagworten und
 * Teilen; rechts Werbeplatz 02; danach „Weiterlesen“ als Strom.
 */

defined( 'ABSPATH' ) || exit;

get_header();

while ( have_posts() ) :
	the_post();
	$post_id = get_the_ID();
	$kat     = tamil_hauptkategorie( $post_id );
	$url     = (string) get_permalink();
	$titel   = get_the_title();
	$kino    = function_exists( 'tamil_site_kino_fakten' ) ? tamil_site_kino_fakten( $post_id ) : array();
	$event   = function_exists( 'tamil_site_event' ) ? tamil_site_event( $post_id ) : array();
	$inhalt  = (string) get_post_field( 'post_content', $post_id );
	$ort     = trim( (string) get_post_meta( $post_id, 'ort', true ) );
	$zeilen  = array();
	$zeile   = $kat ? '<a href="' . esc_url( get_category_link( $kat ) ) . '">' . esc_html( $kat->name ) . '</a>' : '';
	if ( '' !== $ort ) {
		$zeile .= ( '' !== $zeile ? ', ' : '' ) . esc_html( $ort );
	}
	if ( '' !== $zeile ) {
		$zeilen[] = $zeile;
	}
	if ( $kino ) {
		/* translators: %s: Datum */
		$zeilen[] = esc_html( sprintf( __( 'Kinoliste, Stand: %s', 'tamil' ), get_the_modified_date( 'j. F' ) ) );
	}
	$minuten = tamil_lesezeit( $post_id );
	$sidebar = function_exists( 'tamil_site_anzeige' ) ? tamil_site_anzeige( 'sidebar', false ) : '';
	$teilen  = array(
		array( 'Facebook', 'https://www.facebook.com/sharer/sharer.php?u=' . rawurlencode( $url ) ),
		array( 'X', 'https://twitter.com/intent/tweet?url=' . rawurlencode( $url ) . '&text=' . rawurlencode( $titel ) ),
		array( 'Telegram', 'https://t.me/share/url?url=' . rawurlencode( $url ) . '&text=' . rawurlencode( $titel ) ),
	);
	?>
	<article <?php post_class( 'artikel' ); ?>>
		<header class="artikel-kopf">
			<div class="wrap">
				<?php tamil_tag_block( (int) get_post_timestamp( $post_id ), $zeilen ); ?>
				<div class="artikel-kopf-text">
					<h1><?php echo esc_html( $titel ); ?></h1>
					<p class="vorspann"><?php echo tamil_text( tamil_standfirst( $post_id ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_text() ?></p>
					<p class="autor">
						<?php
						/* translators: 1: Autor, 2: Minuten */
						echo esc_html( sprintf( _n( '%1$s, %2$d Minute Lesezeit', '%1$s, %2$d Minuten Lesezeit', $minuten, 'tamil' ), tamil_opt( 'autor_name' ), $minuten ) );
						?>
					</p>
					<p class="aktionen"><a class="textlink" href="<?php echo esc_url( tamil_wa_teilen( $titel, $url ) ); ?>"><?php esc_html_e( 'Per WhatsApp schicken', 'tamil' ); ?></a></p>
				</div>
			</div>
		</header>

		<?php
		$figur = tamil_figur(
			$post_id,
			array(
				'klasse' => 'bild',
				'size'   => 'tamil-lead',
				'link'   => false,
				'eager'  => true,
				'alt'    => true,
			)
		);
		if ( '' !== $figur ) :
			?>
			<div class="artikel-bild"><div class="wrap"><?php echo $figur; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_figur() ?></div></div>
		<?php endif; ?>

		<div class="artikel-text">
			<div class="wrap">
				<div class="text">
					<?php
					if ( $event && ! str_contains( $inhalt, 'event-box' ) ) {
						get_template_part(
							'template-parts/article/termin',
							null,
							array(
								'post'  => $post_id,
								'event' => $event,
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
							'post'   => $post_id,
							'inhalt' => $inhalt,
						)
					);
					?>
					<?php if ( tamil_tags( $post_id ) ) : ?>
						<p class="schlagworte">
							<span class="klein"><?php esc_html_e( 'Schlagworte:', 'tamil' ); ?></span>
							<?php foreach ( tamil_tags( $post_id ) as $tag ) : ?>
								<a href="<?php echo esc_url( get_tag_link( $tag ) ); ?>"><?php echo esc_html( $tag->name ); ?></a>
							<?php endforeach; ?>
						</p>
					<?php endif; ?>
					<div class="teilen-block" aria-label="<?php esc_attr_e( 'Teilen', 'tamil' ); ?>">
						<a class="knopf" href="<?php echo esc_url( tamil_wa_teilen( $titel, $url ) ); ?>"><?php esc_html_e( 'Per WhatsApp schicken', 'tamil' ); ?></a>
						<?php foreach ( $teilen as [ $name, $href ] ) : ?>
							<a class="textlink" href="<?php echo esc_url( $href ); ?>" target="_blank" rel="noopener"><?php echo esc_html( $name ); ?></a>
						<?php endforeach; ?>
						<a class="textlink" href="<?php echo esc_url( 'mailto:?subject=' . rawurlencode( $titel ) . '&body=' . rawurlencode( $url ), array( 'mailto' ) ); ?>"><?php esc_html_e( 'E-Mail', 'tamil' ); ?></a>
						<button type="button" class="textlink knopf-text" data-copy="<?php echo esc_attr( $url ); ?>"><?php esc_html_e( 'Link kopieren', 'tamil' ); ?></button>
					</div>
					<p class="autor-text"><strong><?php echo esc_html( tamil_opt( 'autor_name' ) ); ?></strong> <?php echo esc_html( tamil_opt( 'autor_text' ) ); ?></p>
				</div>
				<?php
				if ( '' !== $sidebar ) :
					?>
					<aside class="artikel-rand" aria-label="<?php esc_attr_e( 'Anzeige', 'tamil' ); ?>"><?php echo $sidebar; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Werbeplatz aus dem Plugin, dort escapt ?></aside>
				<?php endif; ?>
			</div>
		</div>
	</article>
	<?php tamil_leaderboard(); ?>

	<?php $related = tamil_related( $post_id ); ?>
	<?php if ( $related ) : ?>
		<section class="abschnitt weiterlesen" aria-labelledby="weiterlesen-titel">
			<div class="wrap">
				<div class="kopfzeile">
					<h2 id="weiterlesen-titel"><?php esc_html_e( 'Weiterlesen', 'tamil' ); ?></h2>
					<?php if ( $kat ) : ?>
						<?php /* translators: %s: Rubrik */ ?>
						<a class="mehr" href="<?php echo esc_url( get_category_link( $kat ) ); ?>"><?php echo esc_html( sprintf( __( 'Mehr aus %s', 'tamil' ), $kat->name ) ); ?></a>
					<?php endif; ?>
				</div>
				<?php
				tamil_strom(
					$related,
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
endwhile;

get_footer();
