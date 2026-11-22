<?php
/**
 * Startseiten-Probe „Cover First“ (/?probe=cover, inc/proben.php): eine Titelgeschichte als Cover mit eigenem
 * Kontextfeld (Ort, Quelle, Datum, Vorspann), daneben drei Beistücke in drei Formaten, absteigend (4:3, 16:9, 8:3).
 * Die übrigen vier Beiträge des Vorrats stehen als Reihe „Weitere Meldungen“ darunter, dann die Rubrikkacheln.
 * Jeder Beitrag ist eine Bildkarte mit Titel im Bild und Punktbogen (tamil_anr_imbild()).
 *
 * @var array $args { @type array $kacheln Rubrikkacheln aus tamil_start_auswahl(). }
 */

defined( 'ABSPATH' ) || exit;

$tamil_wahl    = tamil_probe_cover_auswahl();
$tamil_formate = array(
	array( 'beistueck beistueck--gross', 'r43', '(min-width: 1024px) 388px, (min-width: 600px) 40vw, calc(100vw - 32px)' ),
	array( 'beistueck beistueck--mittel', 'r169', '(min-width: 1024px) 388px, (min-width: 600px) 30vw, calc(100vw - 32px)' ),
	array( 'beistueck beistueck--flach', 'r83', '(min-width: 1024px) 388px, (min-width: 600px) 30vw, calc(100vw - 32px)' ),
);
?>
<div class="innen oben oben--probe titelseite titelseite--<?php echo (int) count( $tamil_wahl['bei'] ); ?>">
	<?php
	echo tamil_anr_imbild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild()
		$tamil_wahl['cover'],
		array(
			'klasse'       => 'aufmacher aufmacher--cover',
			'rahmen'       => tamil_probe_coverformat( $tamil_wahl['cover'] ),
			'ebene'        => 'h2',
			'eager'        => true,
			'sizes'        => '(min-width: 1024px) 860px, (min-width: 600px) calc(100vw - 48px), 100vw',
			'titel_stufen' => true,
			'zusatz'       => tamil_kontext(
				$tamil_wahl['cover'],
				array(
					'form'  => 'cover',
					'satz'  => 'vorspann',
					'titel' => __( 'Titelgeschichte', 'tamil' ),
					'datum' => true,
				)
			),
		)
	);
	?>

	<?php if ( $tamil_wahl['bei'] ) : ?>
		<section class="beistuecke" aria-label="<?php esc_attr_e( 'Weitere Geschichten', 'tamil' ); ?>">
			<?php
			foreach ( $tamil_wahl['bei'] as $tamil_i => $tamil_id ) {
				echo tamil_anr_imbild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild()
					$tamil_id,
					array(
						'klasse' => $tamil_formate[ $tamil_i ][0],
						'rahmen' => $tamil_formate[ $tamil_i ][1],
						'sizes'  => $tamil_formate[ $tamil_i ][2],
						'eager'  => 0 === $tamil_i, // B1 steht am Handy im ersten Bildschirm
						// Ein Satz nur unter dem ersten Beistück (am Handy; ab 600 px stehen die drei bündig)
						'zusatz' => 0 === $tamil_i ? tamil_kontext(
							$tamil_id,
							array(
								'form'   => 'zeile',
								'satz'   => 'einer',
								'ort'    => false,
								'quelle' => false,
							)
						) : '',
					)
				);
			}
			?>
		</section>
	<?php endif; ?>

	<?php if ( $tamil_wahl['rest'] ) : ?>
		<section class="weitere" aria-labelledby="t-meldungen">
			<h2 class="block-titel" id="t-meldungen"><?php esc_html_e( 'Weitere Meldungen', 'tamil' ); ?></h2>
			<div class="neben karten karten--reihe">
				<?php
				foreach ( $tamil_wahl['rest'] as $tamil_id ) {
					echo tamil_anr_imbild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild()
						$tamil_id,
						array(
							'klasse'   => 'karte',
							'rahmen'   => 'r169',
							'vorspann' => true,
							'niedrig'  => true,
							'sizes'    => '(min-width: 1024px) 290px, (min-width: 600px) calc(50vw - 36px), 320px',
						)
					);
				}
				?>
			</div>
		</section>
	<?php endif; ?>

	<?php echo tamil_kacheln( (array) ( $args['kacheln'] ?? array() ), __( 'Rubriken mit Bild', 'tamil' ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_kacheln() ?>
</div>
