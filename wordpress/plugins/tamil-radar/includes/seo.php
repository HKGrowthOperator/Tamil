<?php
/**
 * SEO-Felder für Rank Math oder Yoast setzen – nur, wenn das Plugin aktiv ist.
 */

defined( 'ABSPATH' ) || exit;

function tamil_radar_seo_plugin(): string {
	if ( defined( 'RANK_MATH_VERSION' ) ) {
		return 'rankmath';
	}
	if ( defined( 'WPSEO_VERSION' ) ) {
		return 'yoast';
	}
	return 'none';
}

/**
 * @param int   $post_id Beitrag.
 * @param array $seo     {title?, description?, focus?}.
 * @return string Welches Plugin bedient wurde (rankmath|yoast|none).
 */
function tamil_radar_write_seo( int $post_id, array $seo ): string {
	$title       = sanitize_text_field( (string) ( $seo['title'] ?? '' ) );
	$description = sanitize_text_field( (string) ( $seo['description'] ?? '' ) );
	$focus       = sanitize_text_field( (string) ( $seo['focus'] ?? '' ) );
	$plugin      = tamil_radar_seo_plugin();
	if ( 'rankmath' === $plugin ) {
		if ( $title ) {
			update_post_meta( $post_id, 'rank_math_title', $title );
		}
		if ( $description ) {
			update_post_meta( $post_id, 'rank_math_description', $description );
		}
		if ( $focus ) {
			update_post_meta( $post_id, 'rank_math_focus_keyword', $focus );
		}
	} elseif ( 'yoast' === $plugin ) {
		if ( $title ) {
			update_post_meta( $post_id, '_yoast_wpseo_title', $title );
		}
		if ( $description ) {
			update_post_meta( $post_id, '_yoast_wpseo_metadesc', $description );
		}
		if ( $focus ) {
			update_post_meta( $post_id, '_yoast_wpseo_focuskw', $focus );
		}
	}
	return $plugin;
}
