<?php
/**
 * Zählung der gebuchten Anzeigen je Buchung und Tag: Einblendungen (mindestens die halbe Fläche eine Sekunde sichtbar,
 * gemessen von assets/werbung.js) und Klicks (über eine Weiterleitung). Ohne Cookies, ohne Personendaten: gespeichert
 * wird nur die Summe je Tag. Gezählt wird nur, solange die Buchung aktiv ist.
 */

defined( 'ABSPATH' ) || exit;

// phpcs:disable WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- Zähler in eigener Tabelle, atomar erhöht

/**
 * Zähler erhöhen.
 *
 * @param string $feld einblendungen oder klicks.
 */
function tamil_site_werbung_zaehlen( int $buchung, string $feld, ?string $tag = null ): void {
	global $wpdb;
	if ( ! in_array( $feld, array( 'einblendungen', 'klicks' ), true ) ) {
		return;
	}
	$tabelle = tamil_site_werbung_tabelle( 'statistik' );
	$tag     = $tag ?? tamil_site_werbung_heute();
	$wpdb->query( $wpdb->prepare( 'INSERT IGNORE INTO %i (buchung_id, tag, einblendungen, klicks) VALUES (%d, %s, 0, 0)', $tabelle, $buchung, $tag ) );
	$wpdb->query( $wpdb->prepare( 'UPDATE %i SET %i = %i + 1 WHERE buchung_id = %d AND tag = %s', $tabelle, $feld, $feld, $buchung, $tag ) );
}

/**
 * Statistik einer Buchung, Tag aufsteigend.
 *
 * @return array<int,array{tag:string,einblendungen:int,klicks:int}>
 */
function tamil_site_werbung_statistik( int $buchung ): array {
	global $wpdb;
	$zeilen = (array) $wpdb->get_results( $wpdb->prepare( 'SELECT tag, einblendungen, klicks FROM %i WHERE buchung_id = %d ORDER BY tag', tamil_site_werbung_tabelle( 'statistik' ), $buchung ), ARRAY_A );
	return array_map(
		static function ( $z ) {
			return array(
				'tag'           => (string) $z['tag'],
				'einblendungen' => (int) $z['einblendungen'],
				'klicks'        => (int) $z['klicks'],
			);
		},
		$zeilen
	);
}

/**
 * Ist der Aufrufer erkennbar ein Bot (Suchmaschine, Vorschau, Abruf-Werkzeug)?
 */
function tamil_site_werbung_bot(): bool {
	$ua = isset( $_SERVER['HTTP_USER_AGENT'] ) ? sanitize_text_field( wp_unslash( $_SERVER['HTTP_USER_AGENT'] ) ) : '';
	return '' === $ua || (bool) preg_match( '/bot\b|bot\/|crawl|spider|slurp|facebookexternalhit|preview|headless|lighthouse|monitor|curl\/|wget\//i', $ua );
}

/**
 * Zählt höchstens einmal je Besucher, Buchung, Art und Tag. Erkennung über einen Hash aus Adresse und Tagessalz in
 * einem Transient (läuft nach einem Tag ab); gespeichert wird weder die Adresse noch der Hash in der Statistik.
 *
 * @param string $feld einblendungen oder klicks.
 */
function tamil_site_werbung_zaehlen_einmal( int $buchung, string $feld ): bool {
	if ( tamil_site_werbung_bot() ) {
		return false;
	}
	$tag   = tamil_site_werbung_heute();
	$ip    = isset( $_SERVER['REMOTE_ADDR'] ) ? sanitize_text_field( wp_unslash( $_SERVER['REMOTE_ADDR'] ) ) : '';
	$salz  = hash_hmac( 'sha256', $tag, wp_salt( 'nonce' ) );
	$marke = 'tamil_wb_z_' . substr( hash_hmac( 'sha256', $ip . '|' . $buchung . '|' . $feld, $salz ), 0, 32 );
	if ( get_transient( $marke ) ) {
		return false;
	}
	set_transient( $marke, 1, DAY_IN_SECONDS );
	tamil_site_werbung_zaehlen( $buchung, $feld, $tag );
	return true;
}

/**
 * POST /wp-json/tamil-site/v1/werbung/einblendung (buchung=ID)
 */
function tamil_site_werbung_rest_einblendung( WP_REST_Request $request ): WP_REST_Response {
	$b = tamil_site_werbung_buchung( absint( $request->get_param( 'buchung' ) ) );
	if ( ! tamil_site_funktion_an( 'werbung' ) || ! $b || ! tamil_site_werbung_aktiv( $b ) ) {
		return new WP_REST_Response( null, 204 );
	}
	tamil_site_werbung_zaehlen_einmal( (int) $b['id'], 'einblendungen' );
	return new WP_REST_Response( null, 204 );
}

/**
 * GET /wp-json/tamil-site/v1/werbung/klick/<id> – zählt und leitet zur Zieladresse weiter.
 */
function tamil_site_werbung_rest_klick( WP_REST_Request $request ): WP_REST_Response {
	$b    = tamil_site_werbung_buchung( absint( $request['id'] ) );
	$ziel = home_url( '/' );
	// Nur eine aktive Buchung führt zum Kunden; sonst (pausiert, beendet, erstattet …) zur Startseite.
	if ( tamil_site_funktion_an( 'werbung' ) && $b && tamil_site_werbung_aktiv( $b ) && '' !== $b['ziel_url'] ) {
		$ziel = (string) $b['ziel_url'];
		tamil_site_werbung_zaehlen_einmal( (int) $b['id'], 'klicks' );
	}
	$antwort = new WP_REST_Response( null, 302 );
	$antwort->header( 'Location', esc_url_raw( $ziel ) );
	$antwort->header( 'Cache-Control', 'no-store' );
	$antwort->header( 'X-Robots-Tag', 'noindex, nofollow' );
	return $antwort;
}

function tamil_site_werbung_zaehlung_routen(): void {
	register_rest_route(
		'tamil-site/v1',
		'/werbung/einblendung',
		array(
			'methods'             => 'POST',
			'callback'            => 'tamil_site_werbung_rest_einblendung',
			// öffentlich: zählt nur eine Summe je Tag für aktive Buchungen, ändert sonst nichts
			'permission_callback' => '__return_true',
			'args'                => array(
				'buchung' => array(
					'type'     => 'integer',
					'required' => true,
				),
			),
		)
	);
	register_rest_route(
		'tamil-site/v1',
		'/werbung/klick/(?P<id>\d+)',
		array(
			'methods'             => 'GET',
			'callback'            => 'tamil_site_werbung_rest_klick',
			'permission_callback' => '__return_true',
		)
	);
}
add_action( 'rest_api_init', 'tamil_site_werbung_zaehlung_routen' );

function tamil_site_werbung_skript_registrieren(): void {
	wp_register_script( 'tamil-site-werbung', TAMIL_SITE_URL . 'assets/werbung.js', array(), TAMIL_SITE_VERSION, array( 'in_footer' => true ) );
	wp_register_style( 'tamil-site-werbung', TAMIL_SITE_URL . 'assets/werbung.css', array(), TAMIL_SITE_VERSION );
}
add_action( 'wp_enqueue_scripts', 'tamil_site_werbung_skript_registrieren', 5 );
