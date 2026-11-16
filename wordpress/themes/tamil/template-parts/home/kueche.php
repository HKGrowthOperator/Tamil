<?php
/**
 * „Küche“ (hell): die erste Kachel groß (16:9), bis zu drei kleine (8:3) gestapelt daneben; jede Kachel behält ihr
 * Format auf allen Breiten, Titel im Bild.
 *
 * @var array $args { @type int[] $ids Beiträge mit Bild (höchstens vier). }
 */

defined( 'ABSPATH' ) || exit;

$tamil_ids    = array_map( 'intval', (array) ( $args['ids'] ?? array() ) );
$tamil_rubrik = tamil_rubrik( 'kueche' );
?>
<section class="kueche innen" id="kueche" aria-labelledby="t-kueche">
	<div class="block-kopf">
		<h2 class="block-titel" id="t-kueche"><a href="<?php echo esc_url( $tamil_rubrik['url'] ); ?>"><?php echo esc_html( $tamil_rubrik['label'] ); ?></a></h2>
	</div>
	<div class="kueche__raster kueche__raster--<?php echo (int) count( $tamil_ids ); ?>">
		<?php
		foreach ( $tamil_ids as $tamil_i => $tamil_id ) {
			echo tamil_anr_imbild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild()
				$tamil_id,
				0 === $tamil_i ? array(
					'klasse' => 'kachel kachel--gross',
					'rahmen' => 'r169',
					'sizes'  => '(min-width: 1024px) 800px, (min-width: 600px) calc(66vw - 32px), calc(100vw - 32px)',
				) : array(
					'klasse' => 'kachel kachel--klein',
					'rahmen' => 'r83',
					'sizes'  => '(min-width: 1024px) 380px, (min-width: 600px) 33vw, calc(100vw - 32px)',
				)
			);
		}
		?>
	</div>
</section>
