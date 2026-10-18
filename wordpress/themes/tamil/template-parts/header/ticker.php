<?php
/**
 * Laufband mit Schlagzeilen (Kinoliste, Termine, neueste Beiträge). Ohne Beiträge kein Laufband.
 */

defined( 'ABSPATH' ) || exit;

$items = tamil_ticker();
if ( ! $items ) {
	return;
}
?>
<div class="ticker" aria-label="<?php esc_attr_e( 'Aktuelle Schlagzeilen', 'tamil' ); ?>">
	<div class="track">
		<?php foreach ( $items as $t ) : ?>
			<a class="item" href="<?php echo esc_url( $t['href'] ); ?>"><span class="k" lang="ta"><?php echo esc_html( $t['k'] ); ?></span><?php echo esc_html( $t['text'] ); ?></a>
		<?php endforeach; ?>
	</div>
</div>
