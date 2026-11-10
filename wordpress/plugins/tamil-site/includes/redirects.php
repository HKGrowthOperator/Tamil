<?php
/**
 * 301-Weiterleitungen für den Relaunch (alte Kategorien und Seiten) aus einer CSV-Tabelle in den Einstellungen.
 *
 * CSV-Format wie tools/export_site.py (redirects.csv): Spalten „alt“ und „neu“ (Pfade oder volle URLs),
 * weitere Spalten werden ignoriert. Gespeichert wird eine Tabelle Pfad → Ziel in der Option tamil_site_redirects.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Pfad normalisieren: nur der Pfadteil, Kleinbuchstaben, mit abschließendem Schrägstrich.
 */
function tamil_site_normalize_path( string $value ): string {
	$path = (string) wp_parse_url( trim( $value ), PHP_URL_PATH );
	if ( '' === $path ) {
		$path = '/';
	}
	$path = '/' . trim( strtolower( $path ), '/' );
	return '/' === $path ? '/' : $path . '/';
}

/**
 * CSV-Text in die Weiterleitungstabelle verwandeln.
 *
 * @return array<string,string> Pfad → Ziel (Pfad oder URL).
 */
function tamil_site_parse_redirect_csv( string $csv ): array {
	$table = array();
	$lines = (array) preg_split( '/\r\n|\r|\n/', trim( $csv ) );
	$alt   = 0;
	$neu   = 1;
	foreach ( $lines as $i => $line ) {
		if ( '' === trim( $line ) ) {
			continue;
		}
		$cells = str_getcsv( $line, ',', '"', '\\' );
		if ( 0 === $i && in_array( 'alt', array_map( 'strtolower', $cells ), true ) ) {
			$lower = array_map( 'strtolower', $cells );
			$alt   = (int) array_search( 'alt', $lower, true );
			$neu   = (int) array_search( 'neu', $lower, true );
			continue;
		}
		$from = isset( $cells[ $alt ] ) ? trim( (string) $cells[ $alt ] ) : '';
		$to   = isset( $cells[ $neu ] ) ? trim( (string) $cells[ $neu ] ) : '';
		if ( '' === $from || '' === $to ) {
			continue;
		}
		$from_path = tamil_site_normalize_path( $from );
		if ( '/' === $from_path ) {
			continue;
		}
		$table[ $from_path ] = esc_url_raw( str_starts_with( $to, 'http' ) ? $to : home_url( tamil_site_normalize_path( $to ) ) );
	}
	return $table;
}

/**
 * @return array<string,string>
 */
function tamil_site_redirects(): array {
	$table = get_option( 'tamil_site_redirects', array() );
	return is_array( $table ) ? $table : array();
}

function tamil_site_maybe_redirect(): void {
	if ( is_admin() || wp_doing_ajax() || ( defined( 'REST_REQUEST' ) && REST_REQUEST ) ) {
		return;
	}
	$table = tamil_site_redirects();
	if ( ! $table ) {
		return;
	}
	$path = tamil_site_normalize_path( (string) ( $_SERVER['REQUEST_URI'] ?? '/' ) ); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput
	if ( isset( $table[ $path ] ) && tamil_site_normalize_path( $table[ $path ] ) !== $path ) {
		wp_safe_redirect( $table[ $path ], 301, 'Tamil.de Relaunch' );
		exit;
	}
}
add_action( 'template_redirect', 'tamil_site_maybe_redirect', 1 );

/**
 * REST: POST tamil-site/v1/weiterleitungen mit {"csv": "alt,neu\n…"} ersetzt die Weiterleitungstabelle (nur mit
 * manage_options). So kann die Migration (tools/migration.py) die 301-Tabelle ohne Zugang zur Oberfläche einspielen;
 * ein zweiter Aufruf mit gleichem Inhalt ändert nichts.
 */
function tamil_site_rest_redirects( WP_REST_Request $request ): WP_REST_Response {
	$csv = sanitize_textarea_field( (string) $request->get_param( 'csv' ) );
	update_option( 'tamil_site_redirects_csv', $csv, false );
	$table = tamil_site_parse_redirect_csv( $csv );
	update_option( 'tamil_site_redirects', $table, false );
	return new WP_REST_Response( array( 'eintraege' => count( $table ) ) );
}

function tamil_site_register_redirect_route(): void {
	register_rest_route(
		'tamil-site/v1',
		'/weiterleitungen',
		array(
			'methods'             => 'POST',
			'callback'            => 'tamil_site_rest_redirects',
			'permission_callback' => static function (): bool {
				return current_user_can( 'manage_options' );
			},
			'args'                => array(
				'csv' => array(
					'type'     => 'string',
					'required' => true,
				),
			),
		)
	);
}
add_action( 'rest_api_init', 'tamil_site_register_redirect_route' );
