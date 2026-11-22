<?php
/**
 * Startseiten-Probe „Ausgabe“ (/?probe=ausgabe, inc/proben.php, Theme 3.17.0) nach der Empfehlung der unabhängigen
 * Kritik vom 22.11.2026. Aufbau: design/richtungen/klar2/proben-start/ausgabe.md.
 *
 * 1. Cover: die Titelgeschichte groß (Titel im Bild in Stufen nach Länge, nie gekürzt), darunter die Rubrik auf Tamil
 *    und Deutsch, das Kontextfeld (Ort, Termin, Quelle) und der Vorspann in ganzen Sätzen.
 * 2. „Tamil in meiner Stadt“ als Streifen auf Titan (template-parts/home/stadt-streifen.php); er ersetzt in dieser
 *    Probe „Diese Woche“ (front-page.php).
 * 3. Beistücke mit Gewicht: ein großes, zwei kleinere daneben.
 * 4. „Weitere Meldungen“ gespiegelt: eine große Karte, drei flache daneben (am Handy eine wischbare Reihe).
 * 5. Rubrikkacheln mit dem tamilischen Namen der Rubrik.
 * Jeder Beitrag ist eine Bildkarte mit Titel im Bild und Punktbogen (tamil_anr_imbild()); kein Beitrag steht doppelt.
 *
 * @var array $args { @type array $kacheln Rubrikkacheln aus tamil_start_auswahl(). }
 */

defined( 'ABSPATH' ) || exit;

$tamil_w = tamil_probe_ausgabe_auswahl();
?>
<div class="innen oben--probe ausgabe ausgabe__kopf">
	<?php
	echo tamil_anr_imbild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild()
		$tamil_w['cover'],
		array(
			'klasse'       => 'aufmacher aufmacher--ausgabe' . ( tamil_titel_langes_wort( $tamil_w['cover'] ) ? ' aufmacher--langwort' : '' ),
			'ebene'        => 'h2',
			'eager'        => true,
			'sizes'        => tamil_probe_cover_sizes( $tamil_w['cover'] ),
			'titel_stufen' => true,
			'zusatz'       => '<div class="ausgabe__unter">' . tamil_rubrik_zweisprachig( $tamil_w['cover'] ) . tamil_kontext(
				$tamil_w['cover'],
				array(
					'form'  => 'cover',
					'satz'  => 'vorspann',
					'titel' => __( 'Titelgeschichte', 'tamil' ),
					'datum' => true,
				)
			) . '</div>',
		)
	);
	?>
</div>

<?php get_template_part( 'template-parts/home/stadt-streifen' ); ?>

<div class="innen oben--probe ausgabe ausgabe__rest">
	<?php if ( $tamil_w['gross'] ) : ?>
		<section class="ausgabe__stuecke ausgabe__stuecke--<?php echo (int) count( $tamil_w['klein'] ); ?>" aria-label="<?php esc_attr_e( 'Weitere Geschichten', 'tamil' ); ?>">
			<?php
			echo tamil_anr_imbild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild()
				$tamil_w['gross'],
				array(
					'klasse' => 'beistueck beistueck--gross',
					'sizes'  => '(min-width: 1024px) 800px, (min-width: 600px) calc(100vw - 48px), calc(100vw - 32px)',
					'zusatz' => tamil_kontext(
						$tamil_w['gross'],
						array(
							'form'   => 'zeile',
							'satz'   => 'vorspann',
							'quelle' => false,
						)
					),
				)
			);
			if ( $tamil_w['klein'] ) {
				echo '<div class="ausgabe__stapel">';
				foreach ( $tamil_w['klein'] as $tamil_id ) {
					echo tamil_anr_imbild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild()
						$tamil_id,
						array(
							'klasse'  => 'beistueck beistueck--mittel',
							'niedrig' => true,
							'sizes'   => '(min-width: 1024px) 388px, (min-width: 600px) calc(50vw - 32px), calc(100vw - 32px)',
						)
					);
				}
				echo '</div>';
			}
			?>
		</section>
	<?php endif; ?>

	<?php if ( $tamil_w['haupt'] ) : ?>
		<section class="ausgabe__weitere" aria-labelledby="t-meldungen">
			<h2 class="block-titel" id="t-meldungen"><?php esc_html_e( 'Weitere Meldungen', 'tamil' ); ?></h2>
			<div class="ausgabe__stuecke ausgabe__stuecke--gespiegelt ausgabe__stuecke--<?php echo (int) count( $tamil_w['flach'] ); ?>">
				<?php
				echo tamil_anr_imbild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild()
					$tamil_w['haupt'],
					array(
						'klasse'  => 'beistueck beistueck--gross',
						'niedrig' => true,
						'sizes'   => '(min-width: 1024px) 800px, (min-width: 600px) calc(100vw - 48px), calc(100vw - 32px)',
					)
				);
				if ( $tamil_w['flach'] ) {
					echo '<div class="ausgabe__stapel ausgabe__stapel--reihe">';
					foreach ( $tamil_w['flach'] as $tamil_id ) {
						echo tamil_anr_imbild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild()
							$tamil_id,
							array(
								'klasse'  => 'beistueck beistueck--flach',
								'niedrig' => true,
								'sizes'   => '(min-width: 1024px) 388px, (min-width: 600px) 33vw, 310px',
							)
						);
					}
					echo '</div>';
				}
				?>
			</div>
		</section>
	<?php endif; ?>

	<?php echo tamil_kacheln( (array) ( $args['kacheln'] ?? array() ), __( 'Rubriken mit Bild', 'tamil' ), true ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_kacheln() ?>
</div>
