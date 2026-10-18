<?php
/**
 * Backend: Menü „News-Radar“ (Cockpit), Einstellungen (Cockpit-URL, Werbeplätze, Weiterleitungen), Spalte „Radar“.
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
	register_setting(
		'tamil_radar',
		'tamil_radar_redirects_csv',
		array(
			'type'              => 'string',
			'sanitize_callback' => 'tamil_radar_sanitize_redirects_csv',
			'default'           => '',
		)
	);
}
add_action( 'admin_init', 'tamil_radar_register_settings' );

function tamil_radar_sanitize_settings( $input ): array {
	$input = is_array( $input ) ? $input : array();
	$out   = array(
		'cockpit_url'  => esc_url_raw( (string) ( $input['cockpit_url'] ?? '' ) ),
		'anzeigen'     => array(),
		'advanced_ads' => array(),
	);
	foreach ( array_keys( tamil_radar_werbeplaetze() ) as $platz ) {
		// Banner-HTML nur für Administratoren (unfiltered_html), sonst nur Standard-HTML.
		$html = (string) ( $input['anzeigen'][ $platz ] ?? '' );
		$out['anzeigen'][ $platz ]     = current_user_can( 'unfiltered_html' ) ? trim( $html ) : wp_kses_post( $html );
		$out['advanced_ads'][ $platz ] = sanitize_text_field( (string) ( $input['advanced_ads'][ $platz ] ?? '' ) );
	}
	return $out;
}

/**
 * CSV speichern und daraus die Tabelle für template_redirect ableiten.
 */
function tamil_radar_sanitize_redirects_csv( $input ): string {
	$csv = sanitize_textarea_field( (string) $input );
	update_option( 'tamil_radar_redirects', tamil_radar_parse_redirect_csv( $csv ), false );
	return $csv;
}

function tamil_radar_page_settings(): void {
	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}
	$settings = tamil_radar_settings();
	$csv      = (string) get_option( 'tamil_radar_redirects_csv', '' );
	$table    = tamil_radar_redirects();
	?>
	<div class="wrap tamil-radar-wrap">
		<h1><?php esc_html_e( 'News-Radar · Einstellungen', 'tamil-radar' ); ?></h1>
		<form method="post" action="options.php">
			<?php settings_fields( 'tamil_radar' ); ?>
			<h2><?php esc_html_e( 'Cockpit', 'tamil-radar' ); ?></h2>
			<table class="form-table" role="presentation">
				<tr>
					<th scope="row"><label for="tamil_radar_cockpit_url"><?php esc_html_e( 'Adresse des Cockpits', 'tamil-radar' ); ?></label></th>
					<td><input type="url" class="regular-text" id="tamil_radar_cockpit_url" name="tamil_radar_settings[cockpit_url]" value="<?php echo esc_attr( $settings['cockpit_url'] ); ?>" placeholder="https://radar.tamil.de">
					<p class="description"><?php esc_html_e( 'Die Freigabe-App des Radars (RADAR_WEB_URL). Wird im Menü „News-Radar“ eingebettet und im Dashboard-Widget abgefragt.', 'tamil-radar' ); ?></p></td>
				</tr>
			</table>
			<h2><?php esc_html_e( 'Werbeplätze', 'tamil-radar' ); ?></h2>
			<p class="description"><?php esc_html_e( 'Je Platz entweder eine Advanced-Ads-Platzierung (Slug) oder eigenes Banner-HTML. Advanced Ads hat Vorrang. Leer = Platz bleibt unsichtbar.', 'tamil-radar' ); ?></p>
			<table class="form-table" role="presentation">
				<?php foreach ( tamil_radar_werbeplaetze() as $platz => $label ) : ?>
				<tr>
					<th scope="row"><?php echo esc_html( $label ); ?></th>
					<td>
						<input type="text" class="regular-text" name="tamil_radar_settings[advanced_ads][<?php echo esc_attr( $platz ); ?>]" value="<?php echo esc_attr( $settings['advanced_ads'][ $platz ] ?? '' ); ?>" placeholder="<?php esc_attr_e( 'Advanced-Ads-Platzierung (optional)', 'tamil-radar' ); ?>">
						<textarea class="large-text code" rows="3" name="tamil_radar_settings[anzeigen][<?php echo esc_attr( $platz ); ?>]" placeholder="<?php esc_attr_e( 'Banner-HTML', 'tamil-radar' ); ?>"><?php echo esc_textarea( $settings['anzeigen'][ $platz ] ?? '' ); ?></textarea>
					</td>
				</tr>
				<?php endforeach; ?>
			</table>
			<h2><?php esc_html_e( 'Weiterleitungen (301)', 'tamil-radar' ); ?></h2>
			<p class="description"><?php esc_html_e( 'CSV mit den Spalten „alt“ und „neu“ (z. B. redirects.csv aus dem Export der alten Seite). Pfade oder volle URLs.', 'tamil-radar' ); ?></p>
			<textarea class="large-text code" rows="10" name="tamil_radar_redirects_csv"><?php echo esc_textarea( $csv ); ?></textarea>
			<p class="description">
				<?php
				/* translators: %d: Anzahl Weiterleitungen */
				echo esc_html( sprintf( _n( '%d Weiterleitung aktiv.', '%d Weiterleitungen aktiv.', count( $table ), 'tamil-radar' ), count( $table ) ) );
				?>
			</p>
			<?php submit_button(); ?>
		</form>
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
