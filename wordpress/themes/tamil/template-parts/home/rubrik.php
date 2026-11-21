<?php
/**
 * Rubrikblock der Startseite: Blocktitel als Link zur Rubrik, darunter bis zu vier Bildkarten mit Titel im Bild (am
 * Handy eine wischbare Reihe, am Tablet zwei mal zwei, am Desktop vier nebeneinander, dort mit Vorspann darunter).
 *
 * @var array $args { @type string $slug Rubrik, @type int[] $ids Beiträge mit Bild. }
 */

defined( 'ABSPATH' ) || exit;

$tamil_rubrik = tamil_rubrik( (string) $args['slug'] );
$tamil_id_t   = 't-rubrik-' . sanitize_html_class( (string) $args['slug'] );
?>
<section class="rubrikblock innen" aria-labelledby="<?php echo esc_attr( $tamil_id_t ); ?>">
	<div class="block-kopf">
		<h2 class="block-titel" id="<?php echo esc_attr( $tamil_id_t ); ?>"><a href="<?php echo esc_url( $tamil_rubrik['url'] ); ?>"><?php echo esc_html( $tamil_rubrik['label'] ); ?></a></h2>
	</div>
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
</section>
