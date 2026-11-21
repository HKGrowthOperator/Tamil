<?php
/**
 * Startseite klar2, „Text auf Bild“ (Luis, 20.11.2026): Jeder Beitrag steht als Bildkarte mit Dachzeile und Titel im
 * Foto. Aufmacher, daneben (Desktop) „Weitere Meldungen“ als Stapel von drei Karten 16:9 (Handy und Tablet: wischbare
 * Reihe), darunter vier Nebenstücke als Karten und die Rubrikkacheln; Werbeplatz 01; „Diese Woche“ auf Titan Red
 * (Kino und Termine); „Küche“; Werbeplatz Billboard; weitere Rubrikblöcke mit Karten. Auswahl aus
 * tamil_start_auswahl() (inc/queries.php).
 */

defined( 'ABSPATH' ) || exit;

get_header();

$tamil_a = tamil_start_auswahl();
// Beiträge der Startseite vermerken (ohne Rubrikkacheln), damit geliehene Filmbilder ihrem Besitzer ausweichen (CODE-06)
$tamil_ohne = $tamil_a;
unset( $tamil_ohne['kacheln'] );
$tamil_alle = array();
array_walk_recursive(
	$tamil_ohne,
	static function ( $wert, $schluessel ) use ( &$tamil_alle ) {
		// Beitrags-IDs stehen in Listen (Zahl als Schlüssel) oder unter „lead“ bzw. „post“, nicht unter Zählern wie „kinos“
		if ( is_int( $wert ) && $wert > 0 && ( is_int( $schluessel ) || in_array( $schluessel, array( 'lead', 'post' ), true ) ) ) {
			$tamil_alle[] = $wert;
		}
	}
);
tamil_seite_beitraege( $tamil_alle );

if ( ! $tamil_a['lead'] ) :
	?>
	<div class="innen seitenkopf">
		<h1 class="seitenkopf__titel"><?php esc_html_e( 'Noch keine Beiträge', 'tamil' ); ?></h1>
		<p class="seitenkopf__zeile"><?php esc_html_e( 'Sobald der erste Beitrag veröffentlicht ist, erscheint hier die Startseite.', 'tamil' ); ?></p>
	</div>
	<?php
	get_footer();
	return;
endif;

$tamil_aufmacher = tamil_anr_imbild(
	$tamil_a['lead'],
	array(
		'klasse'    => 'aufmacher',
		'rahmen'    => 'r43',
		'ebene'     => 'h2',
		'vorspann'  => true,
		'eager'     => true,
		'sizes'     => '(min-width: 1024px) 780px, (min-width: 600px) calc(100vw - 48px), 100vw',
		'wow'       => tamil_wow_auf_seite(),
		'titel_max' => 84, // K-02: am Handy höchstens vier, am Desktop höchstens drei Zeilen
	)
);
?>
<h1 class="nur-vorlesen"><?php echo esc_html( get_bloginfo( 'name' ) . ', ' . __( 'Startseite', 'tamil' ) ); ?></h1>

<div class="innen oben">
	<?php echo $tamil_aufmacher; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild() ?>

	<?php if ( $tamil_a['neben'] ) : ?>
		<section class="neben karten" aria-label="<?php esc_attr_e( 'Weitere Geschichten', 'tamil' ); ?>">
			<?php
			foreach ( $tamil_a['neben'] as $tamil_id ) {
				echo tamil_anr_imbild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild()
					$tamil_id,
					array(
						'klasse'   => 'karte',
						'rahmen'   => 'r169',
						'vorspann' => true,
						'niedrig'  => true,
						'sizes'    => '(min-width: 1024px) 290px, (min-width: 600px) calc(50vw - 36px), calc(100vw - 32px)',
					)
				);
			}
			?>
		</section>
	<?php endif; ?>

	<?php if ( $tamil_a['meldungen'] ) : ?>
		<section class="meldungen" aria-labelledby="t-meldungen">
			<div class="meldungen__halter">
			<h2 class="block-titel" id="t-meldungen"><?php esc_html_e( 'Weitere Meldungen', 'tamil' ); ?></h2>
			<ul class="karten karten--reihe">
				<?php
				foreach ( $tamil_a['meldungen'] as $tamil_id ) {
					echo '<li>' . tamil_anr_imbild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild()
						$tamil_id,
						array(
							'klasse'  => 'karte karte--meldung',
							'rahmen'  => 'r169',
							'niedrig' => true,
							'sizes'   => '(min-width: 1024px) 388px, 320px',
						)
					) . '</li>';
				}
				?>
			</ul>
			</div>
		</section>
	<?php endif; ?>

	<?php echo tamil_kacheln( $tamil_a['kacheln'], __( 'Rubriken mit Bild', 'tamil' ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_kacheln() ?>
</div>

<?php
// Werbeplatz 01 unter dem ersten Abschnitt (nicht über dem Aufmacher).
tamil_leaderboard( 'innen anzeige-zwischen' );

get_template_part( 'template-parts/home/woche', null, array( 'woche' => $tamil_a['woche'] ) );

if ( $tamil_a['kueche'] ) {
	get_template_part( 'template-parts/home/kueche', null, array( 'ids' => $tamil_a['kueche'] ) );
}

$tamil_billboard = function_exists( 'tamil_site_anzeige' ) ? tamil_site_anzeige( 'billboard', false ) : '';
if ( '' !== $tamil_billboard ) :
	?>
	<div class="innen anzeige-zwischen"><?php echo $tamil_billboard; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Werbeplatz aus dem Plugin, dort escapt ?></div>
	<?php
endif;

// Rhythmus (K-06): die Rubrikblöcke wechseln zwischen der Reihe aus vier Karten und der Bühne (eine große Kachel, die
// übrigen klein gestapelt daneben), damit nicht fünf gleich gebaute Reihen aufeinander folgen
$tamil_nr = 0;
foreach ( $tamil_a['rubriken'] as $tamil_slug => $tamil_ids ) {
	get_template_part(
		'template-parts/home/rubrik',
		null,
		array(
			'slug'   => $tamil_slug,
			'ids'    => $tamil_ids,
			'buehne' => 1 === $tamil_nr % 2 && count( $tamil_ids ) >= 3,
		)
	);
	++$tamil_nr;
}

get_footer();
