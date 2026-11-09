<?php
/**
 * Bühne der Startseite: Aufmacher mit großem Bild, rechts „Neu auf Tamil.de“ (die nächsten Beiträge als Zeilen).
 *
 * @var array $args { @type array $auswahl Ergebnis von tamil_home_auswahl(). }
 */

defined( 'ABSPATH' ) || exit;

$auswahl = $args['auswahl'];
$lead    = (int) $auswahl['lead'];
if ( ! $lead ) {
	return;
}
$link = get_permalink( $lead );
$neu  = array_slice( array_merge( $auswahl['aktuell'], $auswahl['ausserdem'] ), 0, 5 );
?>
<section class="buehne" aria-label="<?php esc_attr_e( 'Aufmacher', 'tamil' ); ?>">
	<div class="wrap buehne-raster">
		<article class="aufmacher">
			<a class="bild" href="<?php echo esc_url( $link ); ?>" tabindex="-1" aria-hidden="true">
				<?php
				echo tamil_bild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- tamil_bild() escapt selbst
					$lead,
					'tamil-lead',
					array(
						'fetchpriority' => 'high',
						'loading'       => 'eager',
					)
				);
				?>
			</a>
			<?php tamil_meta( $lead ); ?>
			<h1><a href="<?php echo esc_url( $link ); ?>"><?php echo esc_html( get_the_title( $lead ) ); ?></a></h1>
			<p class="vorspann"><?php echo esc_html( tamil_standfirst( $lead ) ); ?></p>
		</article>
		<?php if ( $neu ) : ?>
			<aside class="neu" aria-labelledby="neu-titel">
				<h2 class="neu-titel" id="neu-titel"><span class="puls" aria-hidden="true"></span><?php esc_html_e( 'Neu auf Tamil.de', 'tamil' ); ?></h2>
				<?php foreach ( $neu as $id ) : ?>
					<?php
					get_template_part(
						'template-parts/card',
						null,
						array(
							'post'    => $id,
							'variant' => 'zeile',
							'lazy'    => false,
						)
					);
					?>
				<?php endforeach; ?>
			</aside>
		<?php endif; ?>
	</div>
</section>
