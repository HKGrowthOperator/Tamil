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
// Werbeplatz 01 unter dem Tagesblatt (nicht über dem Aufmacher, Kritik theme-tageskalender-r1 P1-1).
tamil_leaderboard();

// Werbeplatz Billboard steht mitten im Strom „Zuletzt“, nicht direkt unter dem Tagesblatt (dort steht schon Platz 01).
$billboard = function_exists( 'tamil_site_anzeige' ) ? tamil_site_anzeige( 'billboard', false ) : '';
$zuletzt   = tamil_ids( array( 'posts_per_page' => 12 ), array( (int) $auswahl['lead'] ) );
if ( $zuletzt ) :
	$teil_1 = array_slice( $zuletzt, 0, 6 );
	$teil_2 = array_slice( $zuletzt, 6 );
	?>
	<section class="abschnitt zuletzt" id="zuletzt" aria-labelledby="zuletzt-titel">
		<div class="wrap">
			<h2 id="zuletzt-titel" class="strom-kopf"><?php esc_html_e( 'Zuletzt bei tamil.de', 'tamil' ); ?></h2>
			<?php tamil_strom( $teil_1, array( 'teaser' => '' ) ); // ohne Anreißer: Dichte je Bildschirm (sloplint 58) ?>
			<?php
			if ( '' !== $billboard ) :
				?>
				<div class="anzeige-zwischen"><?php echo $billboard; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Werbeplatz aus dem Plugin, dort escapt ?></div>
				<?php
			endif;
			if ( $teil_2 ) {
				tamil_strom(
					$teil_2,
					array(
						'teaser' => '',
						'weiter' => wp_date( 'Y-m', (int) get_post_timestamp( (int) end( $teil_1 ) ) ),
					)
				);
			}
			?>
			<?php
			$news = tamil_rubrik( 'news' );
			if ( $news['term'] ) :
				?>
				<p class="weiter-links"><a class="textlink" href="<?php echo esc_url( $news['url'] ); ?>"><?php esc_html_e( 'Ältere Beiträge', 'tamil' ); ?></a></p>
			<?php endif; ?>
		</div>
	</section>
	<?php
endif;

get_footer();
