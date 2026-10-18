<?php
/**
 * Rezept der Woche (gelbes Band).
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
<section class="section band-gold" id="rezept">
	<div class="container">
		<?php tamil_kicker( 'kueche', tamil_opt( 'rezept_kicker' ), tamil_rubrik( 'kueche' )['url'], __( 'Alle Rezepte', 'tamil' ) ); ?>
		<div class="rezept-band">
			<a class="media" href="<?php echo esc_url( $link ); ?>" tabindex="-1" aria-hidden="true"><?php echo tamil_bild( $post_id, 'tamil-card', array( 'loading' => 'lazy' ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?></a>
			<div>
				<h2 class="gross"><a href="<?php echo esc_url( $link ); ?>"><?php echo esc_html( get_the_title( $post_id ) ); ?></a></h2>
				<p class="rezept-vorspann"><?php echo esc_html( tamil_standfirst( $post_id ) ); ?></p>
				<a class="btn btn-dark" href="<?php echo esc_url( $link ); ?>"><?php esc_html_e( 'Zum Rezept', 'tamil' ); ?></a>
			</div>
		</div>
	</div>
</section>
