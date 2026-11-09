<?php
/**
 * Seitenzahlen für Listen (Rubrik, Schlagwort, Suche, Archiv).
 */

defined( 'ABSPATH' ) || exit;

$links = paginate_links(
	array(
		'type'      => 'array',
		'mid_size'  => 1,
		'prev_text' => __( 'Zurück', 'tamil' ),
		'next_text' => __( 'Weiter', 'tamil' ),
	)
);
if ( ! $links ) {
	return;
}
?>
<nav class="pagination" aria-label="<?php esc_attr_e( 'Seiten', 'tamil' ); ?>">
	<?php echo implode( '', $links ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- von paginate_links escaped ?>
</nav>
