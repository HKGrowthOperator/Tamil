<?php
/**
 * Startseite „Tagesblatt“: Datum, Aufmacher mit Foto, die nächsten Feste und das Kino als Tafeln, Werbeplatz,
 * danach „Zuletzt bei tamil.de“ als Strom nach Monaten. Tafeln ohne Inhalt fallen weg oder sagen, dass nichts ansteht.
 */

defined( 'ABSPATH' ) || exit;

get_header();

$auswahl = tamil_home_auswahl();

if ( ! $auswahl['lead'] ) :
	?>
	<section class="abschnitt"><div class="wrap"><h1 class="strom-kopf"><?php esc_html_e( 'Noch keine Beiträge', 'tamil' ); ?></h1><p class="satz"><?php esc_html_e( 'Sobald der erste Beitrag veröffentlicht ist, erscheint hier die Startseite.', 'tamil' ); ?></p></div></section>
	<?php
	get_footer();
	return;
endif;

get_template_part( 'template-parts/home/blatt', null, array( 'auswahl' => $auswahl ) );

$billboard = function_exists( 'tamil_site_anzeige' ) ? tamil_site_anzeige( 'billboard', false ) : '';
if ( '' !== $billboard ) :
	?>
	<div class="wrap anzeige-mitte"><?php echo $billboard; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Werbeplatz aus dem Plugin, dort escapt ?></div>
	<?php
endif;

$zuletzt = tamil_ids( array( 'posts_per_page' => 12 ), array( (int) $auswahl['lead'] ) );
if ( $zuletzt ) :
	?>
	<section class="abschnitt zuletzt" id="zuletzt" aria-labelledby="zuletzt-titel">
		<div class="wrap">
			<h2 id="zuletzt-titel" class="strom-kopf"><?php esc_html_e( 'Zuletzt bei tamil.de', 'tamil' ); ?></h2>
			<?php tamil_strom( $zuletzt ); ?>
			<p class="weiter-links">
				<?php foreach ( array_keys( tamil_rubriken_standard() ) as $slug ) : ?>
					<?php $rubrik = tamil_rubrik( $slug ); ?>
					<?php if ( $rubrik['term'] && 'events' !== $slug && $rubrik['term']->count > 0 ) : ?>
						<?php /* translators: %s: Rubrik */ ?>
						<a class="textlink" href="<?php echo esc_url( $rubrik['url'] ); ?>"><?php echo esc_html( sprintf( __( 'Mehr aus %s', 'tamil' ), $rubrik['label'] ) ); ?></a>
					<?php endif; ?>
				<?php endforeach; ?>
			</p>
		</div>
	</section>
	<?php
endif;

get_footer();
