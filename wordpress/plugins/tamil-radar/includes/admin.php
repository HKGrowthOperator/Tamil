<?php
/**
 * Backend: Menü „News-Radar“ (Cockpit), Einstellungen (Cockpit-Adresse), Spalte „Radar“ in der Beitragsliste.
 */

defined( 'ABSPATH' ) || exit;

function tamil_radar_admin_menu(): void {
	add_menu_page(
		__( 'News-Radar', 'tamil-radar' ),
		__( 'News-Radar', 'tamil-radar' ),
		'edit_posts',
		'tamil-radar',
		'tamil_radar_page_cockpit',
		'dashicons-rss',
		26
	);
	add_submenu_page( 'tamil-radar', __( 'Cockpit', 'tamil-radar' ), __( 'Cockpit', 'tamil-radar' ), 'edit_posts', 'tamil-radar', 'tamil_radar_page_cockpit' );
	add_submenu_page( 'tamil-radar', __( 'Einstellungen', 'tamil-radar' ), __( 'Einstellungen', 'tamil-radar' ), 'manage_options', 'tamil-radar-einstellungen', 'tamil_radar_page_settings' );
}
add_action( 'admin_menu', 'tamil_radar_admin_menu' );

function tamil_radar_admin_assets( string $hook ): void {
	if ( str_contains( $hook, 'tamil-radar' ) || 'index.php' === $hook ) {
		wp_enqueue_style( 'tamil-radar-admin', TAMIL_RADAR_URL . 'assets/admin.css', array(), TAMIL_RADAR_VERSION );
	}
}
add_action( 'admin_enqueue_scripts', 'tamil_radar_admin_assets' );

/**
 * Cockpit-Seite: das externe Werkzeug im Backend (iframe) – unter HTTPS mit frame-ancestors auf beiden Seiten.
 */
function tamil_radar_page_cockpit(): void {
	$url = (string) tamil_radar_settings()['cockpit_url'];
	echo '<div class="wrap tamil-radar-wrap"><h1>' . esc_html__( 'News-Radar', 'tamil-radar' ) . '</h1>';
	if ( '' === $url ) {
		echo '<p>' . esc_html__( 'Noch keine Cockpit-Adresse hinterlegt.', 'tamil-radar' ) . ' ';
		if ( current_user_can( 'manage_options' ) ) {
			echo '<a href="' . esc_url( admin_url( 'admin.php?page=tamil-radar-einstellungen' ) ) . '">' . esc_html__( 'Einstellungen öffnen', 'tamil-radar' ) . '</a>';
		}
		echo '</p></div>';
		return;
	}
	echo '<p class="tamil-radar-toolbar"><a class="button button-primary" target="_blank" rel="noopener" href="' . esc_url( $url ) . '">' . esc_html__( 'In neuem Tab öffnen', 'tamil-radar' ) . '</a> ';
	echo '<span class="description">' . esc_html__( 'Der Radar läuft als eigenes Werkzeug. Freigaben landen als Beiträge in WordPress.', 'tamil-radar' ) . '</span></p>';
	echo '<iframe class="tamil-radar-frame" src="' . esc_url( $url ) . '" title="' . esc_attr__( 'News-Radar Cockpit', 'tamil-radar' ) . '" loading="lazy" referrerpolicy="no-referrer"></iframe>';
	echo '<p class="description">' . esc_html__( 'Bleibt der Rahmen leer, lässt das Cockpit keine Einbettung zu (nur unter HTTPS möglich) – dann den Tab-Link nutzen.', 'tamil-radar' ) . '</p></div>';
}

/* ---- Einstellungen ---------------------------------------------------------------------- */

function tamil_radar_register_settings(): void {
	register_setting(
		'tamil_radar',
		'tamil_radar_settings',
		array(
			'type'              => 'array',
			'sanitize_callback' => 'tamil_radar_sanitize_settings',
			'default'           => array(),
		)
	);
}
add_action( 'admin_init', 'tamil_radar_register_settings' );

function tamil_radar_sanitize_settings( $input ): array {
	$input = is_array( $input ) ? $input : array();
	delete_transient( 'tamil_radar_cockpit_status' );
	return array( 'cockpit_url' => esc_url_raw( (string) ( $input['cockpit_url'] ?? '' ) ) );
}

function tamil_radar_page_settings(): void {
	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}
	$settings = tamil_radar_settings();
	?>
	<div class="wrap tamil-radar-wrap">
		<h1><?php esc_html_e( 'News-Radar · Einstellungen', 'tamil-radar' ); ?></h1>
		<form method="post" action="options.php">
			<?php settings_fields( 'tamil_radar' ); ?>
			<table class="form-table" role="presentation">
				<tr>
					<th scope="row"><label for="tamil_radar_cockpit_url"><?php esc_html_e( 'Adresse des Cockpits', 'tamil-radar' ); ?></label></th>
					<td><input type="url" class="regular-text" id="tamil_radar_cockpit_url" name="tamil_radar_settings[cockpit_url]" value="<?php echo esc_attr( $settings['cockpit_url'] ); ?>" placeholder="https://radar.tamil.de">
					<p class="description"><?php esc_html_e( 'Die Freigabe-App des Radars (RADAR_WEB_URL). Wird im Menü „News-Radar“ eingebettet und im Dashboard-Widget abgefragt.', 'tamil-radar' ); ?></p></td>
				</tr>
			</table>
			<?php submit_button(); ?>
		</form>
		<h2><?php esc_html_e( 'Zugang für den Radar', 'tamil-radar' ); ?></h2>
		<p><?php esc_html_e( 'Der Radar meldet sich mit einem Benutzer der Rolle „Radar“ und einem Anwendungspasswort an (Benutzer → Profil → Anwendungspasswörter). Diese Daten gehören in die .env des Radars: WP_URL, WP_USER, WP_APP_PASSWORD.', 'tamil-radar' ); ?></p>
	</div>
	<?php
}

/* ---- Spalte „Radar“ in der Beitragsliste ------------------------------------------------- */

function tamil_radar_posts_columns( array $columns ): array {
	$columns['tamil_radar'] = __( 'Radar', 'tamil-radar' );
	return $columns;
}
add_filter( 'manage_posts_columns', 'tamil_radar_posts_columns' );

function tamil_radar_posts_column( string $column, int $post_id ): void {
	if ( 'tamil_radar' !== $column ) {
		return;
	}
	$uid = (string) get_post_meta( $post_id, 'radar_uid', true );
	if ( '' === $uid ) {
		echo '<span class="tamil-radar-dash">–</span>';
		return;
	}
	$quelle = (string) get_post_meta( $post_id, 'quelle_name', true );
	$origin = (string) get_post_meta( $post_id, 'bild_origin', true );
	echo '<span class="tamil-radar-tag">' . esc_html__( 'Radar', 'tamil-radar' ) . '</span>';
	if ( $quelle ) {
		echo '<br><small>' . esc_html( $quelle ) . '</small>';
	}
	if ( 'ki' === $origin ) {
		echo '<br><small>' . esc_html__( 'KI-Symbolbild', 'tamil-radar' ) . '</small>';
	}
}
add_action( 'manage_posts_custom_column', 'tamil_radar_posts_column', 10, 2 );
