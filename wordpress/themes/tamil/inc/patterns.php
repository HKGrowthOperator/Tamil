<?php
/**
 * Block-Muster für die Redaktion (Dateien in patterns/ werden von WordPress selbst registriert).
 */

defined( 'ABSPATH' ) || exit;

function tamil_pattern_category(): void {
	register_block_pattern_category( 'tamil', array( 'label' => __( 'Tamil.de', 'tamil' ) ) );
}
add_action( 'init', 'tamil_pattern_category' );
