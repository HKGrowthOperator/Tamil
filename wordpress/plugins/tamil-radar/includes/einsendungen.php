<?php
/**
 * REST tamil-radar/v1 für Einsendungen (Festlegung F1): Der Radar holt ab, WordPress ruft den Radar nie auf.
 *
 *   GET  /einsendungen?nach=<id>&anzahl=<1..100>   neue Einsendungen ab dem Cursor (aufsteigend nach id)
 *   GET  /einsendung/{vorgang}                     eine Einsendung
 *   POST /einsendung/{vorgang}/status              {"status": "abgeholt|uebernommen|erledigt|abgelehnt|spam"}
 *   GET  /einsendung/{vorgang}/bild                Bild als Base64 mit Typ, Größe und SHA-256
 *
 * Recht: tamil_einsendungen_abholen (nur Rolle „radar“, vergeben über die Upgrade-Routine von tamil-site).
 * Daten und Prüfungen liegen im Plugin tamil-site (includes/einsendungen.php); fehlt es, antworten die Routen 503.
 * Der Funktionsschalter „einreichungen“ steuert nur das Annehmen auf der Website: Abholen, Status und Bild bleiben
 * erreichbar, damit vorhandene Einsendungen auch nach dem Ausschalten abgeschlossen werden können.
 * Beschreibung: docs/spezifikation/integrationen.md §3.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Darf der aktuelle Benutzer Einsendungen abholen und ihren Status setzen?
 */
function tamil_radar_einsendungen_recht(): bool {
	return current_user_can( 'tamil_einsendungen_abholen' );
}

/**
 * Routen anmelden.
 */
function tamil_radar_einsendungen_routen(): void {
	$vorgang = '/einsendung/(?P<vorgang>T\d{6}-[A-HJ-NP-Z2-9]{5})';
	register_rest_route(
		TAMIL_RADAR_NS,
		'/einsendungen',
		array(
			'methods'             => WP_REST_Server::READABLE,
			'callback'            => 'tamil_radar_einsendungen_liste',
			'permission_callback' => 'tamil_radar_einsendungen_recht',
			'args'                => array(
				'nach'   => array(
					'type'    => 'integer',
					'default' => 0,
					'minimum' => 0,
				),
				'anzahl' => array(
					'type'    => 'integer',
					'default' => 50,
					'minimum' => 1,
					'maximum' => 100,
				),
			),
		)
	);
	register_rest_route(
		TAMIL_RADAR_NS,
		$vorgang,
		array(
			'methods'             => WP_REST_Server::READABLE,
			'callback'            => 'tamil_radar_einsendung_holen',
			'permission_callback' => 'tamil_radar_einsendungen_recht',
		)
	);
	register_rest_route(
		TAMIL_RADAR_NS,
		$vorgang . '/status',
		array(
			'methods'             => WP_REST_Server::CREATABLE,
			'callback'            => 'tamil_radar_einsendung_status',
			'permission_callback' => 'tamil_radar_einsendungen_recht',
			'args'                => array(
				'status' => array(
					'type'     => 'string',
					'required' => true,
					'enum'     => array( 'abgeholt', 'uebernommen', 'erledigt', 'abgelehnt', 'spam' ),
				),
			),
		)
	);
	register_rest_route(
		TAMIL_RADAR_NS,
		$vorgang . '/bild',
		array(
			'methods'             => WP_REST_Server::READABLE,
			'callback'            => 'tamil_radar_einsendung_bild',
			'permission_callback' => 'tamil_radar_einsendungen_recht',
		)
	);
}
add_action( 'rest_api_init', 'tamil_radar_einsendungen_routen' );

/**
 * Ist tamil-site mit Tabelle da? Sonst ein Fehler mit 503.
 */
function tamil_radar_einsendungen_bereit(): ?WP_Error {
	if ( ! function_exists( 'tamil_site_einsendung_liste' ) || ! function_exists( 'tamil_site_datenversion' ) || tamil_site_datenversion() < 2 ) {
		return new WP_Error( 'tamil_site_fehlt', __( 'Einsendungen sind auf dieser Website nicht eingerichtet (Plugin tamil-site).', 'tamil-radar' ), array( 'status' => 503 ) );
	}
	return null;
}

/**
 * GET /einsendungen
 *
 * @return WP_REST_Response|WP_Error
 */
function tamil_radar_einsendungen_liste( WP_REST_Request $request ) {
	$fehler = tamil_radar_einsendungen_bereit();
	if ( $fehler ) {
		return $fehler;
	}
	$liste = tamil_site_einsendung_liste( (int) $request['nach'], (int) $request['anzahl'] );
	if ( is_wp_error( $liste ) ) {
		return $liste;
	}
	$antwort = rest_ensure_response( $liste );
	$antwort->header( 'Cache-Control', 'no-store' );
	return $antwort;
}

/**
 * GET /einsendung/{vorgang}
 *
 * @return WP_REST_Response|WP_Error
 */
function tamil_radar_einsendung_holen( WP_REST_Request $request ) {
	$fehler = tamil_radar_einsendungen_bereit();
	if ( $fehler ) {
		return $fehler;
	}
	$zeile = tamil_site_einsendung_zeile( (string) $request['vorgang'] );
	if ( ! $zeile ) {
		$db = tamil_site_einsendung_db_fehler();
		return $db ? $db : new WP_Error( 'tamil_einsendung_fehlt', __( 'Einsendung nicht gefunden.', 'tamil-radar' ), array( 'status' => 404 ) );
	}
	$antwort = rest_ensure_response( tamil_site_einsendung_ausgabe( $zeile ) );
	$antwort->header( 'Cache-Control', 'no-store' );
	return $antwort;
}

/**
 * POST /einsendung/{vorgang}/status
 *
 * @return WP_REST_Response|WP_Error
 */
function tamil_radar_einsendung_status( WP_REST_Request $request ) {
	$fehler = tamil_radar_einsendungen_bereit();
	if ( $fehler ) {
		return $fehler;
	}
	$ergebnis = tamil_site_einsendung_status_setzen( (string) $request['vorgang'], (string) $request['status'] );
	return is_wp_error( $ergebnis ) ? $ergebnis : rest_ensure_response( $ergebnis );
}

/**
 * GET /einsendung/{vorgang}/bild
 *
 * @return WP_REST_Response|WP_Error
 */
function tamil_radar_einsendung_bild( WP_REST_Request $request ) {
	$fehler = tamil_radar_einsendungen_bereit();
	if ( $fehler ) {
		return $fehler;
	}
	$vorgang = (string) $request['vorgang'];
	$bild    = tamil_site_einsendung_bild( $vorgang );
	if ( is_wp_error( $bild ) ) {
		return $bild;
	}
	if ( ! $bild ) {
		return new WP_Error( 'tamil_einsendung_ohne_bild', __( 'Zu dieser Einsendung gibt es kein Bild.', 'tamil-radar' ), array( 'status' => 404 ) );
	}
	tamil_site_einsendung_protokoll( 'bild_abgerufen', $vorgang );
	$antwort = rest_ensure_response(
		array(
			'vorgangsnummer' => $vorgang,
			'typ'            => $bild['typ'],
			'groesse'        => $bild['groesse'],
			'sha256'         => $bild['sha256'],
			'daten_base64'   => base64_encode( $bild['daten'] ), // phpcs:ignore WordPress.PHP.DiscouragedPHPFunctions.obfuscation_base64_encode -- Bild als Base64 wie bei POST /beitrag
		)
	);
	$antwort->header( 'Cache-Control', 'no-store' );
	return $antwort;
}
