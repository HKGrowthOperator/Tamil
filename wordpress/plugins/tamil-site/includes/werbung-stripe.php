<?php
/**
 * Stripe für die Werbebuchung (Integrationen §11): Checkout-Session, Abgleich, Erstattung und Webhook.
 *
 * - Transport: wp_remote_request() an https://api.stripe.com/v1/ – austauschbar über den WordPress-Filter
 *   pre_http_request (in Tests immer ein Fake, nie das Netz).
 * - Schlüssel nur aus wp-config.php oder der Umgebung: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET.
 * - Kartendaten sieht die Website nie; gespeichert werden nur Kennungen (Session, Zahlung) und der Beleg-Link.
 * - Webhook: nur mit gültiger Signatur (HMAC-SHA256 über „Zeitstempel.Rohtext“, nur v1, 5 Minuten Toleranz), jede
 *   Ereignis-ID genau einmal. Ohne Schalter „werbung“ antwortet die Route 503, Stripe wiederholt später.
 */

defined( 'ABSPATH' ) || exit;

// phpcs:disable WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- eigene Tabelle, Dubletten-Prüfung muss atomar sein

/**
 * Zeittoleranz der Webhook-Signatur in Sekunden (nie 0).
 */
define( 'TAMIL_SITE_STRIPE_TOLERANZ', 300 );

/**
 * Wert aus wp-config.php (Konstante) oder Umgebung.
 */
function tamil_site_stripe_wert( string $name ): string {
	if ( defined( $name ) ) {
		return (string) constant( $name );
	}
	$wert = getenv( $name );
	return false === $wert ? '' : (string) $wert;
}

/**
 * Ist Stripe eingerichtet (beide Schlüssel vorhanden)?
 */
function tamil_site_stripe_bereit(): bool {
	return '' !== tamil_site_stripe_wert( 'STRIPE_SECRET_KEY' ) && '' !== tamil_site_stripe_wert( 'STRIPE_WEBHOOK_SECRET' );
}

/**
 * Testmodus? Folgt aus dem Schlüssel.
 */
function tamil_site_stripe_testmodus(): bool {
	return str_starts_with( tamil_site_stripe_wert( 'STRIPE_SECRET_KEY' ), 'sk_test_' );
}

/**
 * Aufruf der Stripe-API. Prüft unmittelbar davor den Schalter „werbung“ (Stopp-Schalter dieses Bausteins).
 *
 * @param string              $methode     GET oder POST.
 * @param string              $pfad        z. B. checkout/sessions.
 * @param array<string,mixed> $daten       Formularfelder (verschachtelt wie bei Stripe).
 * @param string              $idempotenz  Idempotenzschlüssel für POST (Wiederholung legt nichts doppelt an).
 * @return array<string,mixed>|WP_Error
 */
function tamil_site_stripe_aufruf( string $methode, string $pfad, array $daten = array(), string $idempotenz = '' ) {
	if ( ! tamil_site_funktion_an( 'werbung' ) ) {
		return new WP_Error( 'werbung_aus', __( 'Werbebuchung ist ausgeschaltet.', 'tamil-site' ) );
	}
	$schluessel = tamil_site_stripe_wert( 'STRIPE_SECRET_KEY' );
	if ( '' === $schluessel ) {
		return new WP_Error( 'stripe_fehlt', __( 'Stripe ist nicht eingerichtet.', 'tamil-site' ) );
	}
	$url  = 'https://api.stripe.com/v1/' . ltrim( $pfad, '/' );
	$args = array(
		'method'  => $methode,
		'timeout' => 20,
		'headers' => array( 'Authorization' => 'Bearer ' . $schluessel ),
	);
	if ( 'GET' === $methode ) {
		$url .= $daten ? '?' . http_build_query( $daten ) : '';
	} else {
		$args['headers']['Content-Type'] = 'application/x-www-form-urlencoded';
		$args['body']                    = http_build_query( $daten );
		if ( '' !== $idempotenz ) {
			$args['headers']['Idempotency-Key'] = $idempotenz;
		}
	}
	$antwort = wp_remote_request( $url, $args );
	if ( is_wp_error( $antwort ) ) {
		return $antwort;
	}
	$code  = (int) wp_remote_retrieve_response_code( $antwort );
	$daten = json_decode( (string) wp_remote_retrieve_body( $antwort ), true );
	if ( $code >= 400 || ! is_array( $daten ) ) {
		$text = is_array( $daten ) ? (string) ( $daten['error']['message'] ?? '' ) : '';
		return new WP_Error( 'stripe', sprintf( 'Stripe %d %s', $code, sanitize_text_field( $text ) ) );
	}
	return $daten;
}

/**
 * Checkout-Session für eine reservierte Buchung anlegen.
 *
 * @param array<string,mixed> $b     Buchung.
 * @param string              $seite Adresse der Seite „Werben“.
 * @return array<string,mixed>|WP_Error Session (id, url).
 */
function tamil_site_stripe_checkout( array $b, string $seite ) {
	$f    = tamil_site_werbung_formate()[ $b['platz'] ];
	$name = sprintf(
		/* translators: 1: Platz, 2: Tage, 3: Startdatum */
		__( 'Werbeplatz %1$s, %2$d Tage ab %3$s', 'tamil-site' ),
		$f['name'],
		(int) $b['laufzeit'],
		wp_date( 'd.m.Y', (int) strtotime( $b['start'] . ' 12:00:00' ) )
	);
	return tamil_site_stripe_aufruf(
		'POST',
		'checkout/sessions',
		array(
			'mode'                 => 'payment',
			'client_reference_id'  => $b['nummer'],
			'payment_method_types' => array( 'card' ),
			'line_items'           => array(
				array(
					'quantity'   => 1,
					'price_data' => array(
						'currency'     => $b['waehrung'],
						'unit_amount'  => (int) $b['betrag'],
						'product_data' => array( 'name' => $name ),
					),
				),
			),
			'metadata'             => array( 'buchung' => $b['nummer'] ),
			'success_url'          => add_query_arg(
				array(
					'wb'     => 'rueckkehr',
					'nummer' => $b['nummer'],
				),
				$seite
			) . '&session_id={CHECKOUT_SESSION_ID}',
			'cancel_url'           => add_query_arg(
				array(
					'wb'     => 'abbruch',
					'nummer' => $b['nummer'],
				),
				$seite
			),
			// kleinster erlaubter Wert ist 30 Minuten; die Tage bleiben 35 Minuten reserviert
			'expires_at'           => time() + 31 * MINUTE_IN_SECONDS,
		),
		'checkout-' . $b['nummer']
	);
}

/**
 * Zweiter Abgleich: Session bei Stripe abrufen und eine bestätigte Zahlung übernehmen.
 *
 * @param array<string,mixed> $b Buchung.
 */
function tamil_site_stripe_abgleich( array $b ): bool {
	if ( '' === $b['stripe_session'] || ( 'offen' !== $b['zahlung'] && 'fehlgeschlagen' !== $b['zahlung'] ) ) {
		return false;
	}
	$session = tamil_site_stripe_aufruf( 'GET', 'checkout/sessions/' . rawurlencode( $b['stripe_session'] ), array( 'expand' => array( 'payment_intent.latest_charge' ) ) );
	if ( is_wp_error( $session ) ) {
		tamil_site_werbung_protokoll( (int) $b['id'], 'website', 'Abgleich mit Stripe gescheitert: ' . $session->get_error_message() );
		return false;
	}
	if ( 'expired' === ( $session['status'] ?? '' ) ) {
		tamil_site_werbung_zahlung_abbrechen( $b, 'stripe', 'Zahlung abgelaufen (Abgleich)' );
		return false;
	}
	return tamil_site_werbung_zahlung_bestaetigen( $b, $session, 'Abgleich' );
}

/**
 * Beleg (Quittung von Stripe) nachholen, falls noch keiner gespeichert ist.
 *
 * @param array<string,mixed> $b Buchung.
 */
function tamil_site_stripe_beleg( array $b ): string {
	global $wpdb;
	if ( '' !== $b['beleg_url'] || '' === $b['stripe_zahlung'] ) {
		return (string) $b['beleg_url'];
	}
	$pi = tamil_site_stripe_aufruf( 'GET', 'payment_intents/' . rawurlencode( $b['stripe_zahlung'] ), array( 'expand' => array( 'latest_charge' ) ) );
	if ( is_wp_error( $pi ) ) {
		return '';
	}
	$url = esc_url_raw( (string) ( $pi['latest_charge']['receipt_url'] ?? '' ) );
	if ( '' !== $url ) {
		$wpdb->update( tamil_site_werbung_tabelle( 'buchungen' ), array( 'beleg_url' => $url ), array( 'id' => (int) $b['id'] ) );
	}
	return $url;
}

/**
 * Prüft die Kopfzeile Stripe-Signature gegen den unveränderten Rohtext.
 *
 * @param string $rohtext   Body, wie er ankam.
 * @param string $kopf      t=…,v1=…[,v1=…].
 * @param string $geheimnis whsec_….
 * @param int    $jetzt     Unix-Zeit.
 */
function tamil_site_stripe_signatur_gueltig( string $rohtext, string $kopf, string $geheimnis, int $jetzt ): bool {
	if ( '' === $geheimnis || '' === $kopf ) {
		return false;
	}
	$zeit   = null;
	$proben = array();
	foreach ( explode( ',', $kopf ) as $teil ) {
		$paar = explode( '=', trim( $teil ), 2 );
		if ( 2 !== count( $paar ) ) {
			continue;
		}
		if ( 't' === $paar[0] && ctype_digit( $paar[1] ) ) {
			$zeit = (int) $paar[1];
		} elseif ( 'v1' === $paar[0] ) {
			$proben[] = $paar[1];
		}
	}
	if ( null === $zeit || ! $proben || abs( $jetzt - $zeit ) > TAMIL_SITE_STRIPE_TOLERANZ ) {
		return false;
	}
	$erwartet = hash_hmac( 'sha256', $zeit . '.' . $rohtext, $geheimnis );
	foreach ( $proben as $probe ) {
		if ( hash_equals( $erwartet, $probe ) ) {
			return true;
		}
	}
	return false;
}

/**
 * Ereignis-ID merken. false = schon bekannt (Dublette).
 */
function tamil_site_stripe_ereignis_merken( string $id, string $typ ): bool {
	global $wpdb;
	return 1 === (int) $wpdb->query( $wpdb->prepare( 'INSERT IGNORE INTO %i (ereignis_id, typ, empfangen_at) VALUES (%s, %s, %s)', tamil_site_werbung_tabelle( 'ereignisse' ), $id, $typ, gmdate( 'Y-m-d H:i:s' ) ) );
}

/**
 * Ereignis-ID wieder vergessen (die Verarbeitung ist gescheitert, Stripe soll erneut senden).
 */
function tamil_site_stripe_ereignis_vergessen( string $id ): void {
	global $wpdb;
	$wpdb->delete( tamil_site_werbung_tabelle( 'ereignisse' ), array( 'ereignis_id' => $id ) );
}

/**
 * Ein geprüftes Ereignis verarbeiten.
 *
 * @param array<string,mixed> $ereignis Ereignis von Stripe.
 * @return string Kurzbeschreibung (für die Antwort).
 */
function tamil_site_stripe_verarbeiten( array $ereignis ): string {
	global $wpdb;
	$typ    = (string) ( $ereignis['type'] ?? '' );
	$objekt = (array) ( $ereignis['data']['object'] ?? array() );
	if ( str_starts_with( $typ, 'checkout.session.' ) ) {
		$b = tamil_site_werbung_buchung_nach_nummer( (string) ( $objekt['client_reference_id'] ?? '' ) );
		if ( ! $b || (string) ( $objekt['id'] ?? '' ) !== $b['stripe_session'] ) {
			return 'unbekannt';
		}
		switch ( $typ ) {
			case 'checkout.session.completed':
			case 'checkout.session.async_payment_succeeded':
				return tamil_site_werbung_zahlung_bestaetigen( $b, $objekt, 'Meldung ' . $typ ) ? 'bezahlt' : 'unveraendert';
			case 'checkout.session.async_payment_failed':
				return tamil_site_werbung_zahlung_abbrechen( $b, 'stripe', 'Zahlung fehlgeschlagen' ) ? 'frei' : 'unveraendert';
			case 'checkout.session.expired':
				return tamil_site_werbung_zahlung_abbrechen( $b, 'stripe', 'Zahlung abgelaufen' ) ? 'frei' : 'unveraendert';
		}
		return 'ignoriert';
	}
	if ( 'charge.refunded' === $typ || 'refund.updated' === $typ || 'refund.failed' === $typ ) {
		$pi = (string) ( $objekt['payment_intent'] ?? '' );
		$id = (int) $wpdb->get_var( $wpdb->prepare( 'SELECT id FROM %i WHERE stripe_zahlung = %s AND stripe_zahlung <> %s', tamil_site_werbung_tabelle( 'buchungen' ), $pi, '' ) );
		if ( ! $id ) {
			return 'unbekannt';
		}
		$voll   = 'charge.refunded' === $typ && (int) ( $objekt['amount_refunded'] ?? 0 ) >= (int) ( $objekt['amount'] ?? PHP_INT_MAX );
		$fertig = 'refund.updated' === $typ && 'succeeded' === ( $objekt['status'] ?? '' );
		if ( $voll || $fertig ) {
			$neu = (int) $wpdb->query( $wpdb->prepare( "UPDATE %i SET zahlung = 'erstattet', warnung = '' WHERE id = %d AND zahlung = 'bezahlt'", tamil_site_werbung_tabelle( 'buchungen' ), $id ) );
			if ( 1 === $neu ) {
				tamil_site_werbung_protokoll( $id, 'stripe', 'erstattet (Meldung ' . $typ . ')' );
			}
			return 'erstattet';
		}
		if ( 'refund.failed' === $typ || 'failed' === ( $objekt['status'] ?? '' ) ) {
			tamil_site_werbung_warnung( $id, 'Erstattung bei Stripe gescheitert – bitte in Stripe prüfen' );
			return 'warnung';
		}
	}
	return 'ignoriert';
}

/**
 * POST /wp-json/tamil-site/v1/werbung/stripe
 */
function tamil_site_stripe_webhook( WP_REST_Request $request ): WP_REST_Response {
	if ( ! tamil_site_funktion_an( 'werbung' ) || ! tamil_site_stripe_bereit() ) {
		return new WP_REST_Response( array( 'fehler' => 'aus' ), 503 );
	}
	$rohtext = (string) $request->get_body();
	if ( ! tamil_site_stripe_signatur_gueltig( $rohtext, (string) $request->get_header( 'stripe_signature' ), tamil_site_stripe_wert( 'STRIPE_WEBHOOK_SECRET' ), time() ) ) {
		// phpcs:ignore WordPress.PHP.DevelopmentFunctions.error_log_error_log -- abgewiesene Meldung gehört ins Server-Log (ohne Inhalt)
		error_log( 'tamil-site: Stripe-Meldung mit ungültiger Signatur abgewiesen' );
		return new WP_REST_Response( array( 'fehler' => 'signatur' ), 400 );
	}
	$ereignis = json_decode( $rohtext, true );
	$id       = is_array( $ereignis ) ? (string) ( $ereignis['id'] ?? '' ) : '';
	if ( '' === $id ) {
		return new WP_REST_Response( array( 'fehler' => 'inhalt' ), 400 );
	}
	if ( ! tamil_site_stripe_ereignis_merken( $id, substr( (string) ( $ereignis['type'] ?? '' ), 0, 80 ) ) ) {
		return new WP_REST_Response( array( 'ergebnis' => 'doppelt' ), 200 );
	}
	try {
		$ergebnis = tamil_site_stripe_verarbeiten( $ereignis );
	} catch ( Throwable $e ) {
		tamil_site_stripe_ereignis_vergessen( $id );
		// phpcs:ignore WordPress.PHP.DevelopmentFunctions.error_log_error_log -- Fehler gehört ins Server-Log
		error_log( 'tamil-site: Stripe-Meldung nicht verarbeitet: ' . $e->getMessage() );
		return new WP_REST_Response( array( 'fehler' => 'verarbeitung' ), 500 );
	}
	return new WP_REST_Response( array( 'ergebnis' => $ergebnis ), 200 );
}

function tamil_site_stripe_routen(): void {
	register_rest_route(
		'tamil-site/v1',
		'/werbung/stripe',
		array(
			'methods'             => 'POST',
			'callback'            => 'tamil_site_stripe_webhook',
			// Öffentlich für Stripe; gültig ist eine Meldung nur mit Signatur (Prüfung im Callback gegen den Rohtext).
			'permission_callback' => '__return_true',
		)
	);
}
add_action( 'rest_api_init', 'tamil_site_stripe_routen' );
