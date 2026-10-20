<?php
/**
 * Dashboard-Widget: Zustand des Cockpits (gecacht), die letzten Radar-Beiträge, Links.
 */

defined( 'ABSPATH' ) || exit;

function tamil_radar_dashboard_setup(): void {
	if ( current_user_can( 'edit_posts' ) ) {
		wp_add_dashboard_widget( 'tamil_radar_widget', __( 'News-Radar', 'tamil-radar' ), 'tamil_radar_dashboard_widget', null, null, 'normal', 'high' );
	}
}
add_action( 'wp_dashboard_setup', 'tamil_radar_dashboard_setup' );

/**
 * /gesund des Cockpits abfragen (5 Minuten Cache). Leer, wenn keine Adresse oder nicht erreichbar.
 *
 * @return array<string,mixed>
 */
function tamil_radar_cockpit_status(): array {
	$url = (string) tamil_radar_settings()['cockpit_url'];
	if ( '' === $url ) {
		return array();
	}
	$cached = get_transient( 'tamil_radar_cockpit_status' );
	if ( is_array( $cached ) ) {
		return $cached;
	}
	$response = wp_remote_get( trailingslashit( $url ) . 'gesund', array( 'timeout' => 4 ) );
	$status   = array( 'ok' => false );
	if ( ! is_wp_error( $response ) && 200 === wp_remote_retrieve_response_code( $response ) ) {
		$body   = json_decode( wp_remote_retrieve_body( $response ), true );
		$status = is_array( $body ) ? array_merge( array( 'ok' => true ), $body ) : array( 'ok' => true );
	}
	set_transient( 'tamil_radar_cockpit_status', $status, 5 * MINUTE_IN_SECONDS );
	return $status;
}

function tamil_radar_dashboard_widget(): void {
	$settings = tamil_radar_settings();
	$status   = tamil_radar_cockpit_status();
	echo '<div class="tamil-radar-widget">';
	if ( '' === $settings['cockpit_url'] ) {
		echo '<p>' . esc_html__( 'Keine Cockpit-Adresse hinterlegt.', 'tamil-radar' ) . '</p>';
	} elseif ( ! empty( $status['ok'] ) ) {
		echo '<p><span class="tamil-radar-dot ok"></span> ' . esc_html__( 'Cockpit erreichbar', 'tamil-radar' );
		if ( ! empty( $status['letzter_lauf'] ) ) {
			echo ' · ' . esc_html( sprintf( /* translators: %s: Zeitpunkt */ __( 'letzter Lauf %s', 'tamil-radar' ), (string) $status['letzter_lauf'] ) );
		}
		if ( isset( $status['offen'] ) ) {
			echo ' · ' . esc_html( sprintf( /* translators: %d: Anzahl */ _n( '%d offener Entwurf', '%d offene Entwürfe', (int) $status['offen'], 'tamil-radar' ), (int) $status['offen'] ) );
		}
		echo '</p>';
	} else {
		echo '<p><span class="tamil-radar-dot fehler"></span> ' . esc_html__( 'Cockpit nicht erreichbar', 'tamil-radar' ) . '</p>';
	}
	$posts = get_posts(
		array(
			'post_type'      => 'post',
			'post_status'    => array( 'publish', 'pending', 'draft', 'future' ),
			'posts_per_page' => 5,
			'orderby'        => 'date',
			'meta_query'     => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
				array(
					'key'     => 'radar_uid',
					'value'   => '',
					'compare' => '!=',
				),
			),
		)
	);
	if ( $posts ) {
		echo '<ul class="tamil-radar-list">';
		foreach ( $posts as $post ) {
			$label = 'publish' === $post->post_status ? '' : ' <span class="tamil-radar-status">' . esc_html( get_post_status_object( $post->post_status )->label ?? $post->post_status ) . '</span>';
			echo '<li><a href="' . esc_url( get_edit_post_link( $post ) ) . '">' . esc_html( get_the_title( $post ) ) . '</a>' . $label . '<br><small>' . esc_html( get_the_date( '', $post ) . ' · ' . (string) get_post_meta( $post->ID, 'quelle_name', true ) ) . '</small></li>'; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
		}
		echo '</ul>';
	} else {
		echo '<p>' . esc_html__( 'Noch keine Beiträge vom Radar.', 'tamil-radar' ) . '</p>';
	}
	echo '<p class="tamil-radar-links"><a href="' . esc_url( admin_url( 'admin.php?page=tamil-radar' ) ) . '">' . esc_html__( 'Cockpit', 'tamil-radar' ) . '</a>';
	echo ' · <a href="' . esc_url( admin_url( 'edit.php?post_status=pending&post_type=post' ) ) . '">' . esc_html__( 'Ausstehende Beiträge', 'tamil-radar' ) . '</a></p>';
	echo '</div>';
}
