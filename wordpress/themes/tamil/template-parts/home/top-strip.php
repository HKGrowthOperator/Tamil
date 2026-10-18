<?php
/**
 * Top-Themen: die von der Redaktion markierten Beiträge („Oben halten“), aufgefüllt mit den neuesten.
 *
 * @var array $args { @type int[] $ids }
 */

defined( 'ABSPATH' ) || exit;

$ids = $args['ids'] ?? array();
if ( ! $ids ) {
	return;
}
?>
<section class="band top-band" id="top-themen" aria-label="<?php esc_attr_e( 'Top-Themen', 'tamil' ); ?>">
	<div class="container">
		<div class="top-strip-wrap">
			<h2 class="kicker"><span class="ta" lang="ta">முக்கியம்</span><span class="de"><?php esc_html_e( 'Top-Themen', 'tamil' ); ?></span></h2>
			<ol class="top-strip">
				<?php foreach ( $ids as $i => $id ) : ?>
					<li><span class="nr" aria-hidden="true"><?php echo esc_html( sprintf( '%02d', $i + 1 ) ); ?></span><div><h3><a href="<?php echo esc_url( get_permalink( $id ) ); ?>"><?php echo esc_html( get_the_title( $id ) ); ?></a></h3><?php tamil_meta( $id ); ?></div></li>
				<?php endforeach; ?>
			</ol>
		</div>
	</div>
</section>
