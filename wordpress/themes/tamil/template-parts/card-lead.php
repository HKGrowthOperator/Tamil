<?php
/**
 * Große Karte (Aufmacher außerhalb der Bühne, z. B. Suche oder Rubrik).
 *
 * @var array $args { @type int $post Beitrags-ID. }
 */

defined( 'ABSPATH' ) || exit;

$post_id = (int) ( $args['post'] ?? get_the_ID() );
$link    = get_permalink( $post_id );
$kat     = tamil_hauptkategorie( $post_id );
?>
<article class="card lead">
	<a class="media" href="<?php echo esc_url( $link ); ?>" tabindex="-1" aria-hidden="true">
		<?php echo tamil_bild( $post_id, 'tamil-lead', array( 'fetchpriority' => 'high' ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?>
		<?php
		if ( $kat ) :
			?>
			<span class="badge gold"><?php echo esc_html( $kat->name ); ?></span><?php endif; ?>
	</a>
	<div class="text">
		<h2><a href="<?php echo esc_url( $link ); ?>"><?php echo esc_html( get_the_title( $post_id ) ); ?></a></h2>
		<p class="standfirst"><?php echo esc_html( tamil_standfirst( $post_id ) ); ?></p>
		<?php tamil_meta( $post_id, false ); ?>
	</div>
</article>
