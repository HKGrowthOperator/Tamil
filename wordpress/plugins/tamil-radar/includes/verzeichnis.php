<?php
/**
 * REST tamil-radar/v1 für das Verzeichnis (Festlegung F2): Der Radar holt Einsendungen ab, liest Einträge für den
 * Vergleich alt/neu und schreibt nach der Freigabe im Cockpit genau die freigegebenen Werte. WordPress ruft den Radar
 * nie auf.
 *
 *   GET  /verzeichnis/einsendungen?nach=<id>&anzahl=<1..100>    Einsendungen ab dem Cursor (aufsteigend nach id)
 *   GET  /verzeichnis/einsendung/{vorgang}                      eine Einsendung mit Prüfung nach festen Regeln
 *   POST /verzeichnis/einsendung/{vorgang}/status               {"status":"geprueft|abgelehnt","pruefung":{…}}
 *   GET  /verzeichnis/eintraege?nach=<id>&anzahl=<1..100>       alle Einträge (für die Dublettenprüfung)
 *   GET  /verzeichnis/eintrag/{id}                              ein Eintrag mit „stand“
 *   POST /verzeichnis/eintrag                                   {"einsendung":"V…","felder":{…}} → 201
 *   POST /verzeichnis/eintrag/{id}                              {"einsendung":"V…","stand":"…","felder":{…}}
 *   POST /verzeichnis/eintrag/{id}/entfernen                    {"einsendung":"V…","stand":"…"}
 *
 * Recht: tamil_verzeichnis_pflegen (nur Rolle „radar“, vergeben über die Upgrade-Routine von tamil-site).
 * Premium ist über diese Routen nicht setzbar. Logik und Prüfungen: tamil-site, includes/verzeichnis.php.
 * Funktionsschalter „verzeichnis“ aus: 503 tamil_funktion_aus. Beschreibung: docs/spezifikation/integrationen.md §3.
 */

defined( 'ABSPATH' ) || exit;

function tamil_radar_verzeichnis_recht(): bool {
	return current_user_can( 'tamil_verzeichnis_pflegen' );
}

/**
 * Routen anmelden.
 */
function tamil_radar_verzeichnis_routen(): void {
	$vorgang = '/verzeichnis/einsendung/(?P<vorgang>V\d{6}-[A-HJ-NP-Z2-9]{5})';
	$eintrag = '/verzeichnis/eintrag/(?P<id>\d+)';
	$cursor  = array(
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
	);
	$schreib = array(
		'einsendung' => array(
			'type'     => 'string',
			'required' => true,
			'pattern'  => '^V\d{6}-[A-HJ-NP-Z2-9]{5}$',
		),
		'felder'     => array(
			'type'     => 'object',
			'required' => true,
		),
	);
	$stand   = array(
		'stand' => array(
			'type'     => 'string',
			'required' => true,
		),
	);
	$routen  = array(
		array( '/verzeichnis/einsendungen', WP_REST_Server::READABLE, 'tamil_radar_vz_einsendungen', $cursor ),
		array( $vorgang, WP_REST_Server::READABLE, 'tamil_radar_vz_einsendung', array() ),
		array(
			$vorgang . '/status',
			WP_REST_Server::CREATABLE,
			'tamil_radar_vz_einsendung_status',
			array(
				'status'   => array(
					'type'     => 'string',
					'required' => true,
					'enum'     => array( 'geprueft', 'abgelehnt' ),
				),
				'pruefung' => array( 'type' => 'object' ),
			),
		),
		array( '/verzeichnis/eintraege', WP_REST_Server::READABLE, 'tamil_radar_vz_eintraege', $cursor ),
		array( $eintrag, WP_REST_Server::READABLE, 'tamil_radar_vz_eintrag', array() ),
		array( '/verzeichnis/eintrag', WP_REST_Server::CREATABLE, 'tamil_radar_vz_anlegen', $schreib ),
		array( $eintrag, WP_REST_Server::CREATABLE, 'tamil_radar_vz_aendern', $schreib + $stand ),
		array(
			$eintrag . '/entfernen',
			WP_REST_Server::CREATABLE,
			'tamil_radar_vz_entfernen',
			array( 'einsendung' => $schreib['einsendung'] ) + $stand,
		),
	);
	foreach ( $routen as $r ) {
		register_rest_route(
			TAMIL_RADAR_NS,
			$r[0],
			array(
				array(
					'methods'             => $r[1],
					'callback'            => $r[2],
					'permission_callback' => 'tamil_radar_verzeichnis_recht',
					'args'                => $r[3],
				),
			)
		);
	}
}
add_action( 'rest_api_init', 'tamil_radar_verzeichnis_routen' );

/**
 * Ist alles da (tamil-site mit Tabelle, Schalter an)? Sonst ein Fehler mit 503.
 */
function tamil_radar_vz_bereit(): ?WP_Error {
	if ( ! function_exists( 'tamil_site_vz_freigabe' ) || ! function_exists( 'tamil_site_funktion_an' ) || tamil_site_datenversion() < 4 ) {
		return new WP_Error( 'tamil_site_fehlt', __( 'Das Verzeichnis ist auf dieser Website nicht eingerichtet (Plugin tamil-site).', 'tamil-radar' ), array( 'status' => 503 ) );
	}
	if ( ! tamil_site_funktion_an( 'verzeichnis' ) ) {
		return new WP_Error( 'tamil_funktion_aus', __( 'Die Funktion „Verzeichnis“ ist ausgeschaltet.', 'tamil-radar' ), array( 'status' => 503 ) );
	}
	return null;
}

/**
 * Antwort ohne Zwischenspeicher.
 *
 * @param mixed $daten Daten oder Fehler.
 * @return WP_REST_Response|WP_Error
 */
function tamil_radar_vz_antwort( $daten, int $code = 200 ) {
	if ( is_wp_error( $daten ) ) {
		return $daten;
	}
	$antwort = rest_ensure_response( $daten );
	$antwort->set_status( $code );
	$antwort->header( 'Cache-Control', 'no-store' );
	return $antwort;
}

/**
 * GET /verzeichnis/einsendungen
 *
 * @return WP_REST_Response|WP_Error
 */
function tamil_radar_vz_einsendungen( WP_REST_Request $request ) {
	return tamil_radar_vz_bereit() ?? tamil_radar_vz_antwort( tamil_site_vz_einsendung_liste( (int) $request['nach'], (int) $request['anzahl'] ) );
}

/**
 * GET /verzeichnis/einsendung/{vorgang}
 *
 * @return WP_REST_Response|WP_Error
 */
function tamil_radar_vz_einsendung( WP_REST_Request $request ) {
	$fehler = tamil_radar_vz_bereit();
	if ( $fehler ) {
		return $fehler;
	}
	$zeile = tamil_site_vz_einsendung_zeile( (string) $request['vorgang'] );
	if ( ! $zeile ) {
		return new WP_Error( 'tamil_vz_einsendung_fehlt', __( 'Einsendung nicht gefunden.', 'tamil-radar' ), array( 'status' => 404 ) );
	}
	return tamil_radar_vz_antwort( tamil_site_vz_einsendung_ausgabe( $zeile ) );
}

/**
 * POST /verzeichnis/einsendung/{vorgang}/status
 *
 * @return WP_REST_Response|WP_Error
 */
function tamil_radar_vz_einsendung_status( WP_REST_Request $request ) {
	$fehler = tamil_radar_vz_bereit();
	if ( $fehler ) {
		return $fehler;
	}
	$pruefung = $request->get_param( 'pruefung' );
	return tamil_radar_vz_antwort( tamil_site_vz_einsendung_status_setzen( (string) $request['vorgang'], (string) $request['status'], is_array( $pruefung ) ? $pruefung : null ) );
}

/**
 * GET /verzeichnis/eintraege
 *
 * @return WP_REST_Response|WP_Error
 */
function tamil_radar_vz_eintraege( WP_REST_Request $request ) {
	return tamil_radar_vz_bereit() ?? tamil_radar_vz_antwort( tamil_site_vz_eintraege_liste( (int) $request['nach'], (int) $request['anzahl'] ) );
}

/**
 * GET /verzeichnis/eintrag/{id}
 *
 * @return WP_REST_Response|WP_Error
 */
function tamil_radar_vz_eintrag( WP_REST_Request $request ) {
	$fehler = tamil_radar_vz_bereit();
	if ( $fehler ) {
		return $fehler;
	}
	$eintrag = tamil_site_vz_eintrag_ausgabe( (int) $request['id'] );
	if ( null === $eintrag ) {
		return new WP_Error( 'tamil_vz_eintrag_fehlt', __( 'Eintrag nicht gefunden.', 'tamil-radar' ), array( 'status' => 404 ) );
	}
	return tamil_radar_vz_antwort( $eintrag );
}

/**
 * Felder aus dem Körper (nur ein Objekt, sonst leer).
 *
 * @return array<string,mixed>
 */
function tamil_radar_vz_felder( WP_REST_Request $request ): array {
	$felder = $request->get_param( 'felder' );
	return is_array( $felder ) ? $felder : array();
}

/**
 * POST /verzeichnis/eintrag
 *
 * @return WP_REST_Response|WP_Error
 */
function tamil_radar_vz_anlegen( WP_REST_Request $request ) {
	$fehler = tamil_radar_vz_bereit();
	if ( $fehler ) {
		return $fehler;
	}
	$ergebnis = tamil_site_vz_freigabe( 'anlegen', (string) $request['einsendung'], 0, tamil_radar_vz_felder( $request ), '' );
	return tamil_radar_vz_antwort( $ergebnis, ! is_wp_error( $ergebnis ) && empty( $ergebnis['bereits'] ) ? 201 : 200 );
}

/**
 * POST /verzeichnis/eintrag/{id}
 *
 * @return WP_REST_Response|WP_Error
 */
function tamil_radar_vz_aendern( WP_REST_Request $request ) {
	$fehler = tamil_radar_vz_bereit();
	if ( $fehler ) {
		return $fehler;
	}
	return tamil_radar_vz_antwort( tamil_site_vz_freigabe( 'aendern', (string) $request['einsendung'], (int) $request['id'], tamil_radar_vz_felder( $request ), (string) $request['stand'] ) );
}

/**
 * POST /verzeichnis/eintrag/{id}/entfernen
 *
 * @return WP_REST_Response|WP_Error
 */
function tamil_radar_vz_entfernen( WP_REST_Request $request ) {
	$fehler = tamil_radar_vz_bereit();
	if ( $fehler ) {
		return $fehler;
	}
	return tamil_radar_vz_antwort( tamil_site_vz_freigabe( 'entfernen', (string) $request['einsendung'], (int) $request['id'], array(), (string) $request['stand'] ) );
}
