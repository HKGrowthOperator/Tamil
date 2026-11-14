<?php
/**
 * Tagesblatt der Startseite: links Tagesziffer, Aufmacher (Schlagzeile, Vorspann, WhatsApp) und „Die nächsten
 * Feste“; rechts das Foto des Aufmachers mit Nachweis und „Im Kino“. Am Handy: Datum, Feste, Schlagzeile, Foto,
 * Vorspann, Kino.
 *
 * @var array $args { @type array $auswahl Ergebnis von tamil_home_auswahl(). }
 */

defined( 'ABSPATH' ) || exit;

$lead  = (int) $args['auswahl']['lead'];
$link  = (string) get_permalink( $lead );
$titel = get_the_title( $lead );
$feste = function_exists( 'tamil_site_upcoming_events' ) ? array_map( 'intval', tamil_site_upcoming_events( 4, array( 'fields' => 'ids' ) )->posts ) : array();
$filme = tamil_kino_filme( 3 );
$jetzt = time();
?>
<section class="blatt" aria-label="<?php esc_attr_e( 'Heute', 'tamil' ); ?>">
	<div class="wrap">
		<div class="blatt-text">
			<div class="blatt-tag"><?php tamil_tag_block( $jetzt ); ?></div>
			<article class="aufmacher">
				<h1><a class="titel-link" href="<?php echo esc_url( $link ); ?>"><?php echo esc_html( $titel ); ?></a></h1>
				<p class="vorspann"><?php echo tamil_text( tamil_saetze( tamil_standfirst( $lead ), 2 ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_text() ?></p>
				<p class="aktionen"><a class="textlink" href="<?php echo esc_url( tamil_wa_teilen( $titel, $link ) ); ?>"><?php esc_html_e( 'Per WhatsApp schicken', 'tamil' ); ?></a></p>
			</article>
			<?php if ( function_exists( 'tamil_site_upcoming_events' ) ) : ?>
				<div class="blatt-feste<?php echo $feste ? '' : ' ist-leer'; ?>">
					<section class="bogen" aria-labelledby="feste-titel">
						<div class="bogen-kopf">
							<h2 id="feste-titel"><?php esc_html_e( 'Die nächsten Feste', 'tamil' ); ?></h2>
							<p class="bogen-stand"><time datetime="<?php echo esc_attr( wp_date( 'Y-m-d', $jetzt ) ); ?>"><?php echo esc_html( tamil_stand( $jetzt ) ); ?></time></p>
						</div>
						<?php
						if ( $feste ) {
							tamil_feste_tafel( $feste );
						} else {
							echo '<p class="bogen-leer">' . esc_html__( 'Gerade steht kein kommendes Fest im Kalender. Kennt ihr eins? Schickt es der Redaktion.', 'tamil' ) . '</p>';
						}
						?>
						<p class="bogen-fuss aktionen">
							<a class="textlink" href="<?php echo esc_url( tamil_rubrik( 'events' )['url'] ); ?>"><?php esc_html_e( 'Ganzer Festkalender', 'tamil' ); ?></a>
							<a class="textlink" href="<?php echo esc_url( tamil_seiten_url( 'kontakt', 'event-einreichen' ) ); ?>"><?php esc_html_e( 'Termin einreichen', 'tamil' ); ?></a>
						</p>
					</section>
				</div>
			<?php endif; ?>
		</div>
		<div class="blatt-rechts">
			<?php
			echo tamil_figur( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_figur()
				$lead,
				array(
					'klasse' => 'bild aufmacher-bild',
					'size'   => 'tamil-card',
					'eager'  => true,
					'alt'    => true,
				)
			);
			?>
			<?php if ( function_exists( 'tamil_site_kino_posts' ) ) : ?>
				<div class="blatt-kino">
					<section class="bogen" aria-labelledby="kino-titel">
						<div class="bogen-kopf">
							<h2 id="kino-titel"><?php esc_html_e( 'Im Kino', 'tamil' ); ?></h2>
							<?php
							if ( $filme && '' !== $filme[0]['stand'] ) :
								?>
								<p class="bogen-stand"><?php echo esc_html( $filme[0]['stand'] ); ?></p><?php endif; ?>
						</div>
						<?php
						if ( $filme ) {
							tamil_kino_tafel( $filme );
						} else {
							echo tamil_kino_leer(); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_kino_leer()
						}
						?>
						<p class="bogen-fuss"><a class="textlink" href="<?php echo esc_url( tamil_rubrik( 'kino' )['url'] ); ?>"><?php esc_html_e( 'Kino nach Stadt', 'tamil' ); ?></a></p>
					</section>
				</div>
			<?php endif; ?>
		</div>
	</div>
</section>
