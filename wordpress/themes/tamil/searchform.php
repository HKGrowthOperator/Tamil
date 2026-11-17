<?php
/**
 * Suchformular (Suche, 404): ein Feld und ein Knopf in einer Zeile.
 */

defined( 'ABSPATH' ) || exit;

$tamil_feld = wp_unique_id( 'suche-' );
?>
<form class="suchfeld" role="search" method="get" action="<?php echo esc_url( home_url( '/' ) ); ?>">
	<label class="nur-vorlesen" for="<?php echo esc_attr( $tamil_feld ); ?>"><?php esc_html_e( 'Suchbegriff', 'tamil' ); ?></label>
	<input id="<?php echo esc_attr( $tamil_feld ); ?>" type="search" name="s" value="<?php echo esc_attr( get_search_query() ); ?>" placeholder="<?php esc_attr_e( 'Film, Stadt, Fest', 'tamil' ); ?>">
	<button type="submit" class="knopf"><?php esc_html_e( 'Suchen', 'tamil' ); ?></button>
</form>
