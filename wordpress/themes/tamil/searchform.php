<?php
/**
 * Suchformular (Suche, 404, leere Listen).
 */

defined( 'ABSPATH' ) || exit;

$id = wp_unique_id( 'suche-' );
?>
<form class="suchformular" role="search" method="get" action="<?php echo esc_url( home_url( '/' ) ); ?>">
	<label class="sr-only" for="<?php echo esc_attr( $id ); ?>"><?php esc_html_e( 'Suche', 'tamil' ); ?></label>
	<input id="<?php echo esc_attr( $id ); ?>" type="search" name="s" value="<?php echo esc_attr( get_search_query() ); ?>" placeholder="<?php esc_attr_e( 'Film, Stadt, Fest …', 'tamil' ); ?>">
	<button type="submit" class="btn btn-primary"><?php tamil_icon( 'search', 'ico ico-sm' ); ?> <?php esc_html_e( 'Suchen', 'tamil' ); ?></button>
</form>
