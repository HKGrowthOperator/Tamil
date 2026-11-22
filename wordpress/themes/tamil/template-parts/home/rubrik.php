<?php
/**
 * Rubrikblock der Startseite: Blocktitel als Link zur Rubrik, darunter bis zu vier Bildkarten mit Titel im Bild (am
 * Handy eine wischbare Reihe, am Tablet zwei mal zwei, am Desktop vier nebeneinander, dort mit Vorspann darunter).
 *
 * Jeder zweite Block ist eine Bühne (K-06, 21.11.2026): die erste Karte groß, die übrigen klein gestapelt daneben, gebaut
 * wie die Küche; Titel im Bild und Punktbogen wie überall.
 *
 * @var array $args { @type string $slug Rubrik, @type int[] $ids Beiträge mit Bild, @type bool $buehne Bauart Bühne. }
 */

defined( 'ABSPATH' ) || exit;

$tamil_rubrik = tamil_rubrik( (string) $args['slug'] );
$tamil_id_t   = 't-rubrik-' . sanitize_html_class( (string) $args['slug'] );
?>
<section class="rubrikblock innen" aria-labelledby="<?php echo esc_attr( $tamil_id_t ); ?>">
	<div class="block-kopf">
		<h2 class="block-titel" id="<?php echo esc_attr( $tamil_id_t ); ?>"><a href="<?php echo esc_url( $tamil_rubrik['url'] ); ?>"><?php echo esc_html( $tamil_rubrik['label'] ); ?></a></h2>
	</div>
	<?php if ( ! empty( $args['buehne'] ) ) : ?>
		<?php $tamil_ids = array_slice( array_map( 'intval', (array) $args['ids'] ), 0, 4 ); ?>
		<div class="kueche__raster rubrikblock__buehne kueche__raster--<?php echo (int) count( $tamil_ids ); ?>">
			<?php
			foreach ( $tamil_ids as $tamil_i => $tamil_id ) {
				echo tamil_anr_imbild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild()
					$tamil_id,
					0 === $tamil_i ? array(
						'klasse' => 'kachel kachel--gross',
						'rahmen' => 'r169',
						'rubrik' => false,
						'sizes'  => '(min-width: 1024px) 800px, (min-width: 600px) calc(66vw - 32px), calc(100vw - 32px)',
					) : array(
						'klasse' => 'kachel kachel--klein',
						'rahmen' => 'r83',
						'rubrik' => false,
						'sizes'  => '(min-width: 1024px) 380px, (min-width: 600px) 33vw, calc(100vw - 32px)',
					)
				);
			}
			?>
		</div>
	<?php else : ?>
	<div class="neben karten karten--reihe">
		<?php
		foreach ( (array) $args['ids'] as $tamil_id ) {
			echo tamil_anr_imbild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild()
				(int) $tamil_id,
				array(
					'klasse'   => 'karte',
					'rahmen'   => 'r169',
					'rubrik'   => false,
					'vorspann' => true,
					'sizes'    => '(min-width: 1024px) 290px, (min-width: 600px) calc(50vw - 36px), 320px',
				)
			);
		}
		?>
	</div>
	<?php endif; ?>
</section>
