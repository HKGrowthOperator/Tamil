<?php
/**
 * Seitennavigation für Listen (Rubrik, Schlagwort, Suche, Archiv): „Seite 1 von 3“ und die Seitenlinks.
 */

defined( 'ABSPATH' ) || exit;

global $wp_query;
$gesamt = (int) $wp_query->max_num_pages;
if ( $gesamt < 2 ) {
	return;
}
$links = paginate_links(
	array(
		'type'      => 'array',
		'mid_size'  => 1,
		'prev_text' => __( 'Neuere Beiträge', 'tamil' ),
		'next_text' => __( 'Ältere Beiträge', 'tamil' ),
	)
);
if ( ! $links ) {
	return;
}
?>
<nav class="seiten" aria-label="<?php esc_attr_e( 'Seiten', 'tamil' ); ?>">
	<div class="seiten-zeile">
		<?php /* translators: 1: aktuelle Seite, 2: Seiten insgesamt */ ?>
		<p><?php echo esc_html( sprintf( __( 'Seite %1$d von %2$d', 'tamil' ), max( 1, (int) get_query_var( 'paged' ) ), $gesamt ) ); ?></p>
		<div class="seiten-links"><?php echo implode( '', $links ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- von paginate_links escapt ?></div>
	</div>
</nav>
