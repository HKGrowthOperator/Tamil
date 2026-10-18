<?php
/**
 * Karte für einen Beitrag.
 *
 * @var array $args {
 *     @type int    $post    Beitrags-ID (Standard: aktueller Beitrag).
 *     @type string $variant '', 'breit', 'zeile', 'mittel'.
 *     @type string $heading h2 | h3.
 *     @type bool   $excerpt Textauszug zeigen.
 *     @type bool   $badge   Rubrik als Badge auf dem Bild statt in der Meta-Zeile.
 *     @type bool   $lazy    Bild verzögert laden.
 * }
 */

defined( 'ABSPATH' ) || exit;

$post_id = (int) ( $args['post'] ?? get_the_ID() );
$variant = (string) ( $args['variant'] ?? '' );
$heading = in_array( $args['heading'] ?? '', array( 'h2', 'h3' ), true ) ? $args['heading'] : 'h3';
$excerpt = (bool) ( $args['excerpt'] ?? true );
$badge   = (bool) ( $args['badge'] ?? false );
$lazy    = (bool) ( $args['lazy'] ?? true );
$link    = get_permalink( $post_id );
$kat     = tamil_hauptkategorie( $post_id );
$size    = 'zeile' === $variant ? 'tamil-zeile' : ( 'breit' === $variant ? 'tamil-lead' : 'tamil-card' );
$attr    = $lazy ? array( 'loading' => 'lazy' ) : array( 'loading' => 'eager' );
$chips   = wp_list_pluck( tamil_tags( $post_id ), 'slug' );
?>
<article class="card <?php echo esc_attr( $variant ); ?>" data-chips="<?php echo esc_attr( implode( ' ', $chips ) ); ?>">
	<a class="media" href="<?php echo esc_url( $link ); ?>" tabindex="-1" aria-hidden="true">
		<?php echo tamil_bild( $post_id, $size, $attr ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?>
		<?php
		if ( $badge && $kat ) :
			?>
			<span class="badge"><?php echo esc_html( $kat->name ); ?></span><?php endif; ?>
	</a>
	<div class="text">
		<<?php echo $heading; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- h2/h3 ?>><a href="<?php echo esc_url( $link ); ?>"><?php echo esc_html( get_the_title( $post_id ) ); ?></a></<?php echo $heading; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?>>
		<?php
		if ( $excerpt ) :
			?>
			<p class="excerpt"><?php echo esc_html( wp_trim_words( tamil_standfirst( $post_id ), 'breit' === $variant ? 40 : 24, ' …' ) ); ?></p><?php endif; ?>
		<?php tamil_meta( $post_id, ! $badge ); ?>
	</div>
</article>
