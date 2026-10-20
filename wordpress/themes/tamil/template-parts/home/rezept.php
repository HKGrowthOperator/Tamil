<?php
/**
 * Rezept der Woche: großes Bild, Titel, Vorspann.
 *
 * @var array $args { @type int $post }
 */

defined( 'ABSPATH' ) || exit;

$post_id = (int) ( $args['post'] ?? 0 );
if ( ! $post_id ) {
	return;
}
$link = get_permalink( $post_id );
?>
<section class="abschnitt" id="rezept">
	<div class="wrap">
		<div class="rezept-band">
			<a class="bild" href="<?php echo esc_url( $link ); ?>" tabindex="-1" aria-hidden="true"><?php echo tamil_bild( $post_id, 'tamil-card', array( 'loading' => 'lazy' ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?></a>
			<div class="rezept-text">
				<p class="rubrik r-kueche"><?php echo esc_html( tamil_opt( 'rezept_kicker' ) ); ?></p>
				<h2><a href="<?php echo esc_url( $link ); ?>"><?php echo esc_html( get_the_title( $post_id ) ); ?></a></h2>
				<p><?php echo esc_html( tamil_standfirst( $post_id ) ); ?></p>
				<div class="aktionen">
					<a class="knopf" href="<?php echo esc_url( $link ); ?>"><?php esc_html_e( 'Zum Rezept', 'tamil' ); ?></a>
					<a class="mehr" href="<?php echo esc_url( tamil_rubrik( 'kueche' )['url'] ); ?>"><?php esc_html_e( 'Alle Rezepte', 'tamil' ); ?><?php tamil_icon( 'arrow', 'ico ico-sm' ); ?></a>
				</div>
			</div>
		</div>
	</div>
</section>
