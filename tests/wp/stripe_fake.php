<?php
/**
 * Nur für tests/wp/test_werbung.py: ersetzt die Stripe-API über den Filter pre_http_request (nie das Netz).
 * Die Tests legen diese Datei mit einem Zufalls-Geheimnis als mu-plugin ins lokale WordPress und entfernen sie danach.
 * Aufrufe stehen in der Option tamil_test_stripe_aufrufe, Sessions in tamil_test_stripe_sessions.
 */

defined( 'ABSPATH' ) || exit;

define( 'STRIPE_SECRET_KEY', 'sk_test_fake' );
define( 'STRIPE_WEBHOOK_SECRET', '__GEHEIMNIS__' );

add_filter(
	'pre_http_request',
	static function ( $pre, $args, $url ) {
		if ( ! str_starts_with( (string) $url, 'https://api.stripe.com/' ) ) {
			return $pre;
		}
		$pfad    = substr( (string) wp_parse_url( $url, PHP_URL_PATH ), 4 );
		$methode = (string) ( $args['method'] ?? 'GET' );
		$body    = array();
		if ( ! empty( $args['body'] ) ) {
			parse_str( (string) $args['body'], $body );
		}
		$aufrufe   = (array) get_option( 'tamil_test_stripe_aufrufe', array() );
		$aufrufe[] = array(
			'methode'    => $methode,
			'pfad'       => $pfad,
			'body'       => $body,
			'idempotenz' => (string) ( $args['headers']['Idempotency-Key'] ?? '' ),
			'auth'       => (string) ( $args['headers']['Authorization'] ?? '' ),
		);
		update_option( 'tamil_test_stripe_aufrufe', $aufrufe, false );
		$sessions = (array) get_option( 'tamil_test_stripe_sessions', array() );
		$code     = 404;
		$antwort  = array( 'error' => array( 'message' => 'Fake: unbekannt ' . $methode . ' ' . $pfad ) );
		if ( 'POST' === $methode && 'checkout/sessions' === $pfad ) {
			$id              = 'cs_test_' . substr( md5( (string) ( $args['headers']['Idempotency-Key'] ?? wp_generate_password( 12, false ) ) ), 0, 16 );
			$sessions[ $id ] = array(
				'id'                  => $id,
				'object'              => 'checkout.session',
				'url'                 => 'https://checkout.stripe.com/c/pay/' . $id,
				'status'              => 'open',
				'payment_status'      => 'unpaid',
				'amount_total'        => (int) ( $body['line_items'][0]['price_data']['unit_amount'] ?? 0 ),
				'currency'            => (string) ( $body['line_items'][0]['price_data']['currency'] ?? '' ),
				'client_reference_id' => (string) ( $body['client_reference_id'] ?? '' ),
				'payment_intent'      => null,
			);
			update_option( 'tamil_test_stripe_sessions', $sessions, false );
			$code    = 200;
			$antwort = $sessions[ $id ];
		} elseif ( preg_match( '#^checkout/sessions/([^/]+)/expire$#', $pfad, $m ) && 'POST' === $methode ) {
			if ( isset( $sessions[ $m[1] ] ) && 'open' === $sessions[ $m[1] ]['status'] ) {
				$sessions[ $m[1] ]['status'] = 'expired';
				update_option( 'tamil_test_stripe_sessions', $sessions, false );
				$code    = 200;
				$antwort = $sessions[ $m[1] ];
			} else {
				$code    = 400;
				$antwort = array( 'error' => array( 'message' => 'Fake: Session nicht offen' ) );
			}
		} elseif ( preg_match( '#^checkout/sessions/([^/]+)$#', $pfad, $m ) && isset( $sessions[ $m[1] ] ) ) {
			$code    = 200;
			$antwort = $sessions[ $m[1] ];
			if ( 'paid' === $antwort['payment_status'] ) {
				$antwort['payment_intent'] = array(
					'id'            => 'pi_' . $m[1],
					'latest_charge' => array( 'receipt_url' => 'https://pay.stripe.com/receipts/test_' . $m[1] ),
				);
			}
		} elseif ( 'POST' === $methode && 'refunds' === $pfad ) {
			$stand = (string) get_option( 'tamil_test_stripe_erstattung', 'succeeded' );
			if ( 'fehler' === $stand ) {
				$code    = 402;
				$antwort = array( 'error' => array( 'message' => 'Fake: Erstattung abgelehnt' ) );
			} else {
				$code    = 200;
				$antwort = array(
					'id'             => 're_test',
					'status'         => $stand,
					'payment_intent' => (string) ( $body['payment_intent'] ?? '' ),
				);
			}
		} elseif ( preg_match( '#^payment_intents/([^/]+)$#', $pfad, $m ) ) {
			$code    = 200;
			$antwort = array(
				'id'            => $m[1],
				'latest_charge' => array( 'receipt_url' => 'https://pay.stripe.com/receipts/' . $m[1] ),
			);
		}
		return array(
			'headers'  => array(),
			'body'     => wp_json_encode( $antwort ),
			'response' => array(
				'code'    => $code,
				'message' => '',
			),
			'cookies'  => array(),
			'filename' => null,
		);
	},
	10,
	3
);
