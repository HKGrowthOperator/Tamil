<?php
/**
 * Karte für einen Beitrag: Bild, Meta-Zeile (Rubrik · Datum), Titel, optional Vorspann.
 *
 * @var array $args {
 *     @type int    $post    Beitrags-ID (Standard: aktueller Beitrag).
 *     @type string $variant '' (Bild oben), 'gross' (große Geschichte), 'zeile' (Vorschaubild rechts).
 *     @type string $heading h2 | h3.
 *     @type bool   $excerpt Vorspann zeigen.
 *     @type bool   $rubrik  Rubrik in der Meta-Zeile zeigen.
 *     @type bool   $lazy    Bild verzögert laden.
 * }
 */

defined( 'ABSPATH' ) || exit;

$post_id = (int) ( $args['post'] ?? get_the_ID() );
$variant = (string) ( $args['variant'] ?? '' );
$heading = in_array( $args['heading'] ?? '', array( 'h2', 'h3' ), true ) ? $args['heading'] : 'h3';
$excerpt = (bool) ( $args['excerpt'] ?? ( 'zeile' !== $variant ) );
$rubrik  = (bool) ( $args['rubrik'] ?? true );
$lazy    = (bool) ( $args['lazy'] ?? true );
$link    = get_permalink( $post_id );
$size    = 'zeile' === $variant ? 'tamil-zeile' : ( 'gross' === $variant ? 'tamil-lead' : 'tamil-card' );
$attr    = $lazy ? array( 'loading' => 'lazy' ) : array( 'loading' => 'eager' );
$chips   = wp_list_pluck( tamil_tags( $post_id ), 'slug' );
?>
<article class="karte<?php echo '' !== $variant ? ' karte-' . esc_attr( $variant ) : ''; ?>" data-chips="<?php echo esc_attr( implode( ' ', $chips ) ); ?>">
	<a class="bild" href="<?php echo esc_url( $link ); ?>" tabindex="-1" aria-hidden="true"><?php echo tamil_bild( $post_id, $size, $attr ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- tamil_bild() escapt selbst ?></a>
	<div class="text">
		<?php tamil_meta( $post_id, $rubrik, 'zeile' !== $variant ); ?>
		<<?php echo $heading; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- h2/h3 ?>><a href="<?php echo esc_url( $link ); ?>"><?php echo esc_html( get_the_title( $post_id ) ); ?></a></<?php echo $heading; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?>>
		<?php
		if ( $excerpt ) :
			?>
			<p class="auszug"><?php echo esc_html( wp_trim_words( tamil_standfirst( $post_id ), 'gross' === $variant ? 40 : 22, ' …' ) ); ?></p><?php endif; ?>
	</div>
</article>
