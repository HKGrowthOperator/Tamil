<?php
/**
 * Bühne der Startseite: Aufmacher links, rechts „Aktuell“ (zwei Karten) und „Außerdem“ (vier Zeilen).
 *
 * @var array $args { @type array $auswahl Ergebnis von tamil_home_auswahl(). }
 */

defined( 'ABSPATH' ) || exit;

$auswahl = $args['auswahl'];
$lead    = (int) $auswahl['lead'];
if ( ! $lead ) {
	return;
}
$kat   = tamil_hauptkategorie( $lead );
$titel = get_the_title( $lead );
$bild  = (string) get_the_post_thumbnail_url( $lead, 'tamil-card' );
?>
<section class="buehne" id="buehne" aria-label="<?php esc_attr_e( 'Aufmacher', 'tamil' ); ?>"<?php echo $bild ? ' style="--lead:url(\'' . esc_url( $bild ) . '\')"' : ''; ?>>
	<div class="buehne-hintergrund" aria-hidden="true"></div>
	<div class="container">
		<p class="datum-zeile"><span><?php echo esc_html( tamil_heute() ); ?></span><span><?php echo esc_html( tamil_opt( 'tagline' ) ); ?></span></p>
		<article class="buehne-lead">
			<a class="media" href="<?php echo esc_url( get_permalink( $lead ) ); ?>" tabindex="-1" aria-hidden="true">
				<?php
				echo tamil_bild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- tamil_bild() escapt selbst
					$lead,
					'tamil-lead',
					array(
						'fetchpriority' => 'high',
						'loading'       => 'eager',
					)
				); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped 
				?>
				<?php
				if ( $kat ) :
					?>
					<span class="badge gold"><?php echo esc_html( $kat->name ); ?></span><?php endif; ?>
			</a>
			<div class="text">
				<h1<?php echo mb_strlen( $titel ) > 58 ? ' class="lang"' : ''; ?>><a href="<?php echo esc_url( get_permalink( $lead ) ); ?>"><?php echo esc_html( $titel ); ?></a></h1>
				<p class="standfirst"><?php echo esc_html( tamil_standfirst( $lead ) ); ?></p>
				<?php tamil_meta( $lead ); ?>
			</div>
		</article>
		<aside class="buehne-seite" aria-label="<?php esc_attr_e( 'Aktuell', 'tamil' ); ?>">
			<h2 class="kicker"><span class="ta" lang="ta">புதியவை</span><span class="de"><?php esc_html_e( 'Aktuell', 'tamil' ); ?></span></h2>
			<?php foreach ( $auswahl['aktuell'] as $id ) : ?>
				<?php
				get_template_part(
					'template-parts/card',
					null,
					array(
						'post'    => $id,
						'variant' => 'zeile',
						'excerpt' => false,
						'lazy'    => false,
					)
				);
				?>
			<?php endforeach; ?>
			<?php if ( $auswahl['ausserdem'] ) : ?>
				<ul class="ausserdem" aria-label="<?php esc_attr_e( 'Außerdem', 'tamil' ); ?>">
					<?php foreach ( $auswahl['ausserdem'] as $id ) : ?>
						<?php $k = tamil_hauptkategorie( $id ); ?>
						<li><span class="kat"><?php echo esc_html( $k ? $k->name : '' ); ?></span><a href="<?php echo esc_url( get_permalink( $id ) ); ?>"><?php echo esc_html( get_the_title( $id ) ); ?></a><span class="wann"><?php echo esc_html( get_the_date( 'j. M', $id ) ); ?></span></li>
					<?php endforeach; ?>
				</ul>
			<?php endif; ?>
		</aside>
	</div>
</section>
