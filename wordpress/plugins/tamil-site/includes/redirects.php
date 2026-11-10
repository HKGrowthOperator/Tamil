<?php
/**
 * 301-Weiterleitungen für den Relaunch (alte Kategorien und Seiten) aus einer CSV-Tabelle in den Einstellungen.
 *
 * CSV-Format wie tools/export_site.py (redirects.csv): Spalten „alt“ und „neu“ (Pfade oder volle URLs),
 * weitere Spalten werden ignoriert. Gespeichert wird eine Tabelle Pfad → Ziel in der Option tamil_site_redirects.
 */

defined( 'ABSPATH' ) || exit;

const TAMIL_SITE_REDIRECT_MAX_BYTES  = 524288;
const TAMIL_SITE_REDIRECT_MAX_ZEILEN = 5000;

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
 * CSV zeilenweise bereinigen. sanitize_textarea_field entfernt %xx-Folgen und würde /%c3%bcber-uns/ zu /ber-uns/
 * machen; hier fallen nur Tags und Steuerzeichen weg.
 */
function tamil_site_clean_csv( string $csv ): string {
	$out = array();
	foreach ( (array) preg_split( '/\r\n|\r|\n/', $csv ) as $line ) {
		$line = trim( (string) preg_replace( '/[\x00-\x08\x0B\x0C\x0E-\x1F]/', '', wp_strip_all_tags( (string) wp_check_invalid_utf8( (string) $line ) ) ) );
		if ( '' !== $line ) {
			$out[] = $line;
		}
	}
	return implode( "\n", $out );
}

/**
 * CSV prüfen und in die Tabelle verwandeln: Obergrenze (Zeilen, Bytes), danach Ziele nur auf der eigenen Website,
 * keine Ketten und Schleifen.
 *
 * @return array{csv:string,table:array<string,string>,verworfen:array<int,array{alt:string,grund:string}>}|WP_Error
 */
function tamil_site_prepare_redirects( string $csv ) {
	if ( strlen( $csv ) > TAMIL_SITE_REDIRECT_MAX_BYTES || preg_match_all( '/\r\n|\r|\n/', $csv ) + 1 > TAMIL_SITE_REDIRECT_MAX_ZEILEN ) {
		return new WP_Error( 'tamil_site_zu_gross', __( 'Die Weiterleitungsliste ist zu groß.', 'tamil-site' ), array( 'status' => 413 ) );
	}
	$csv       = tamil_site_clean_csv( $csv );
	$verworfen = array();
	$table     = tamil_site_parse_redirect_csv( $csv, $verworfen );
	// Ketten A→B→C werden bis zum Ende aufgelöst (A zeigt direkt auf C); nur echte Schleifen fallen weg.
	$quellen = $table;
	foreach ( $quellen as $from => $to ) {
		$ziel    = $to;
		$gesehen = array( $from );
		while ( isset( $quellen[ $ziel ] ) ) {
			if ( in_array( $ziel, $gesehen, true ) ) {
				$verworfen[] = array(
					'alt'   => $from,
					'grund' => 'Schleife',
				);
				unset( $table[ $from ] );
				continue 2;
			}
			$gesehen[] = $ziel;
			$ziel      = $quellen[ $ziel ];
		}
		if ( $ziel === $from ) {
			$verworfen[] = array(
				'alt'   => $from,
				'grund' => 'Schleife (Ziel gleich Quelle)',
			);
			unset( $table[ $from ] );
			continue;
		}
		$table[ $from ] = $ziel;
	}
	return array(
		'csv'       => $csv,
		'table'     => $table,
		'verworfen' => $verworfen,
	);
}

/**
 * CSV-Text in die Weiterleitungstabelle verwandeln.
 *
 * @param string                                       $csv       CSV mit Spalten „alt“ und „neu“.
 * @param array<int,array{alt:string,grund:string}>    $verworfen Wird um verworfene Zeilen ergänzt (fremder Host).
 * @return array<string,string> Pfad → Zielpfad auf der eigenen Website.
 */
function tamil_site_parse_redirect_csv( string $csv, array &$verworfen = array() ): array {
	$table   = array();
	$lines   = (array) preg_split( '/\r\n|\r|\n/', trim( $csv ) );
	$alt     = 0;
	$neu     = 1;
	$eigener = strtolower( (string) wp_parse_url( home_url(), PHP_URL_HOST ) );
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
		if ( str_starts_with( $to, 'http' ) ) {
			if ( strtolower( (string) wp_parse_url( $to, PHP_URL_HOST ) ) !== $eigener ) {
				$verworfen[] = array(
					'alt'   => $from_path,
					'grund' => 'Ziel außerhalb der eigenen Website',
				);
				continue;
			}
			$to = tamil_site_normalize_path( $to );
		}
		// Nur der Pfad wird gespeichert; die Adresse der Website kommt erst beim Weiterleiten dazu (Domain-Umschaltung).
		$table[ $from_path ] = tamil_site_normalize_path( $to );
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

/**
 * Zieladresse zur Weiterleitungszeit bilden (home_url von jetzt). Alte Einträge mit voller Adresse werden auf den Pfad gekürzt.
 */
function tamil_site_redirect_url( string $target ): string {
	return home_url( tamil_site_normalize_path( $target ) );
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
		wp_safe_redirect( tamil_site_redirect_url( $table[ $path ] ), 301, 'Tamil.de Relaunch' );
		exit;
	}
}
add_action( 'template_redirect', 'tamil_site_maybe_redirect', 1 );

/**
 * REST: POST tamil-site/v1/weiterleitungen mit {"csv": "alt,neu\n…"} ersetzt die Weiterleitungstabelle (nur mit
 * manage_options). So kann die Migration (tools/migration.py) die 301-Tabelle ohne Zugang zur Oberfläche einspielen;
 * ein zweiter Aufruf mit gleichem Inhalt ändert nichts.
 */
function tamil_site_rest_redirects( WP_REST_Request $request ) {
	$prep = tamil_site_prepare_redirects( (string) $request->get_param( 'csv' ) );
	if ( is_wp_error( $prep ) ) {
		return $prep;
	}
	update_option( 'tamil_site_redirects_csv', $prep['csv'], false );
	update_option( 'tamil_site_redirects', $prep['table'], false );
	return new WP_REST_Response(
		array(
			'eintraege' => count( $prep['table'] ),
			'tabelle'   => $prep['table'],
			'verworfen' => $prep['verworfen'],
		)
	);
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
