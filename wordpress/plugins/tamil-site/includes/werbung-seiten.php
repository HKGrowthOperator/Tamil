<?php
/**
 * Öffentliche Seite „Werben“ (Shortcode [tamil_werbung]): Preise, Buchung in fünf Schritten, Rückkehr von Stripe,
 * Kundenübersicht über einen geheimen Link und Wiederfinden mit Buchungsnummer und E-Mail-Adresse.
 *
 * Schlichtes, semantisches Markup mit Klassen wb-…; gestaltet wird im Theme nach Tor G3. Formulare werden vor der
 * Ausgabe in template_redirect verarbeitet (Weiterleitung nach dem Absenden). Wer eine reservierte Buchung bezahlen
 * oder abbrechen darf, zeigt ein kurzlebiges Cookie mit dem Geheimnis des Kundenlinks (nur dieser Browser).
 */

defined( 'ABSPATH' ) || exit;

/**
 * Zustand der laufenden Anfrage (Fehler, alte Eingaben, Meldung) zwischen Verarbeitung und Ausgabe.
 *
 * @param array<string,mixed>|null $neu Werte zum Ergänzen.
 * @return array{fehler:array<int,string>,alt:array<string,string>,meldung:string,nummer:string}
 */
function tamil_site_werbung_zustand( ?array $neu = null ): array {
	static $zustand = array(
		'fehler'  => array(),
		'alt'     => array(),
		'meldung' => '',
		'nummer'  => '',
	);
	if ( null !== $neu ) {
		$zustand = array_merge( $zustand, $neu );
	}
	return $zustand;
}

/**
 * Adresse der Seite mit dem Shortcode (aktuelle Seite, sonst /werben/).
 */
function tamil_site_werbung_seite_url(): string {
	$id = get_queried_object_id();
	if ( $id && is_page( $id ) ) {
		return (string) get_permalink( $id );
	}
	$seite = get_page_by_path( 'werben', OBJECT, 'page' );
	return $seite ? (string) get_permalink( $seite ) : home_url( '/werben/' );
}

/**
 * Wert aus $_GET (bereinigt).
 */
function tamil_site_werbung_get( string $name ): string {
	// phpcs:ignore WordPress.Security.NonceVerification.Recommended -- nur lesende Navigation zwischen den Schritten
	return isset( $_GET[ $name ] ) ? sanitize_text_field( wp_unslash( $_GET[ $name ] ) ) : '';
}

/**
 * Wert aus $_POST (bereinigt; Nonce prüft der Aufrufer).
 */
function tamil_site_werbung_post( string $name, bool $mehrzeilig = false ): string {
	// phpcs:ignore WordPress.Security.NonceVerification.Missing -- Nonce wird in tamil_site_werbung_anfrage() geprüft
	if ( ! isset( $_POST[ $name ] ) || ! is_string( $_POST[ $name ] ) ) {
		return '';
	}
	// phpcs:ignore WordPress.Security.NonceVerification.Missing
	$wert = wp_unslash( $_POST[ $name ] );
	return $mehrzeilig ? sanitize_textarea_field( $wert ) : sanitize_text_field( $wert );
}

function tamil_site_werbung_cookie_name( string $nummer ): string {
	return 'tamil_wb_' . strtolower( preg_replace( '/[^A-Za-z0-9]/', '', $nummer ) );
}

function tamil_site_werbung_cookie_setzen( string $nummer, string $token, int $dauer ): void {
	setcookie(
		tamil_site_werbung_cookie_name( $nummer ),
		$token,
		array(
			'expires'  => time() + $dauer,
			'path'     => COOKIEPATH ? COOKIEPATH : '/',
			'secure'   => is_ssl(),
			'httponly' => true,
			'samesite' => 'Lax',
		)
	);
}

/**
 * Buchung, deren Geheimnis dieser Browser im Cookie hat.
 *
 * @return array{0:array<string,mixed>,1:string}|null Buchung und Klartext des Geheimnisses.
 */
function tamil_site_werbung_cookie_buchung( string $nummer ): ?array {
	$name  = tamil_site_werbung_cookie_name( $nummer );
	$token = isset( $_COOKIE[ $name ] ) ? sanitize_key( wp_unslash( $_COOKIE[ $name ] ) ) : '';
	$b     = '' !== $token ? tamil_site_werbung_buchung_nach_nummer( $nummer ) : null;
	if ( ! $b || ! hash_equals( (string) $b['kunden_hash'], hash( 'sha256', $token ) ) ) {
		return null;
	}
	return array( $b, $token );
}

/**
 * Formulare und Rückkehr von Stripe verarbeiten, bevor die Seite ausgegeben wird.
 */
function tamil_site_werbung_anfrage(): void {
	$post = get_queried_object();
	if ( ! $post instanceof WP_Post || ! has_shortcode( (string) $post->post_content, 'tamil_werbung' ) ) {
		return;
	}
	// Seiten mit Buchungsdaten: nicht zwischenspeichern, nicht indexieren, Geheimnis nicht als Referrer weitergeben.
	nocache_headers();
	header( 'Referrer-Policy: no-referrer' );
	add_filter( 'wp_robots', 'wp_robots_no_robots' );
	if ( ! tamil_site_funktion_an( 'werbung' ) ) {
		return;
	}
	$aktion = tamil_site_werbung_post( 'tamil_wb_aktion' );
	if ( '' !== $aktion ) {
		$nonce = tamil_site_werbung_post( '_wpnonce' );
		if ( ! wp_verify_nonce( $nonce, 'tamil_wb_' . $aktion ) ) {
			tamil_site_werbung_zustand( array( 'fehler' => array( __( 'Das Formular ist abgelaufen. Bitte die Seite neu laden.', 'tamil-site' ) ) ) );
			return;
		}
		if ( 'buchen' === $aktion ) {
			tamil_site_werbung_post_buchen();
		} elseif ( 'bezahlen' === $aktion ) {
			tamil_site_werbung_post_bezahlen();
		} elseif ( 'wiederfinden' === $aktion ) {
			tamil_site_werbung_post_wiederfinden();
		}
		return;
	}
	$wb = tamil_site_werbung_get( 'wb' );
	if ( 'rueckkehr' === $wb ) {
		tamil_site_werbung_rueckkehr();
	} elseif ( 'abbruch' === $wb ) {
		tamil_site_werbung_abbruch();
	}
}
add_action( 'template_redirect', 'tamil_site_werbung_anfrage' );

/**
 * Weiterleiten und beenden.
 */
function tamil_site_werbung_weiter( string $url ): void {
	wp_safe_redirect( $url, 303 );
	exit;
}

/**
 * Hochgeladenes Werbemittel prüfen: JPEG oder PNG (nach Inhalt), Größe, genaue Maße.
 *
 * @param string            $feld Formularfeld.
 * @param array{0:int,1:int} $mass Breite, Höhe.
 * @return array{tmp:string,ext:string}|string Datei oder Fehlertext.
 */
function tamil_site_werbung_datei_pruefen( string $feld, array $mass ) {
	// phpcs:ignore WordPress.Security.NonceVerification.Missing -- Nonce in tamil_site_werbung_anfrage()
	$datei = isset( $_FILES[ $feld ] ) && is_array( $_FILES[ $feld ] ) ? $_FILES[ $feld ] : null;
	if ( ! $datei || UPLOAD_ERR_NO_FILE === (int) ( $datei['error'] ?? UPLOAD_ERR_NO_FILE ) ) {
		return __( 'Bitte ein Bild hochladen.', 'tamil-site' );
	}
	$tmp = (string) ( $datei['tmp_name'] ?? '' );
	if ( UPLOAD_ERR_OK !== (int) $datei['error'] || ! is_uploaded_file( $tmp ) ) {
		return __( 'Das Bild ist nicht vollständig angekommen.', 'tamil-site' );
	}
	if ( (int) filesize( $tmp ) > TAMIL_SITE_WERBUNG_MAX_BYTES ) {
		/* translators: %d: Kilobyte */
		return sprintf( __( 'Das Bild ist größer als %d KB.', 'tamil-site' ), (int) ( TAMIL_SITE_WERBUNG_MAX_BYTES / 1024 ) );
	}
	$info  = function_exists( 'finfo_open' ) ? (string) finfo_file( finfo_open( FILEINFO_MIME_TYPE ), $tmp ) : '';
	$bild  = getimagesize( $tmp );
	$typ   = is_array( $bild ) ? (int) $bild[2] : 0;
	$arten = array(
		IMAGETYPE_JPEG => array( 'image/jpeg', 'jpg' ),
		IMAGETYPE_PNG  => array( 'image/png', 'png' ),
	);
	if ( ! isset( $arten[ $typ ] ) || ( '' !== $info && $info !== $arten[ $typ ][0] ) ) {
		return __( 'Nur JPEG oder PNG.', 'tamil-site' );
	}
	if ( (int) $bild[0] !== $mass[0] || (int) $bild[1] !== $mass[1] ) {
		/* translators: 1: Breite, 2: Höhe, 3: Breite der Datei, 4: Höhe der Datei */
		return sprintf( __( 'Das Bild muss genau %1$d × %2$d Pixel groß sein (hochgeladen: %3$d × %4$d).', 'tamil-site' ), $mass[0], $mass[1], (int) $bild[0], (int) $bild[1] );
	}
	return array(
		'tmp' => $tmp,
		'ext' => $arten[ $typ ][1],
	);
}

/**
 * Geprüftes Werbemittel unter einem zufälligen Namen ablegen.
 *
 * @param array{tmp:string,ext:string} $datei Datei.
 * @return string Pfad relativ zu uploads/ oder '' bei Fehler.
 */
function tamil_site_werbung_datei_speichern( array $datei ): string {
	$uploads = wp_get_upload_dir();
	$relativ = 'tamil-werbung/' . gmdate( 'Y/m' ) . '/' . bin2hex( random_bytes( 16 ) ) . '.' . $datei['ext'];
	$ziel    = trailingslashit( $uploads['basedir'] ) . $relativ;
	if ( ! wp_mkdir_p( dirname( $ziel ) ) || ! move_uploaded_file( $datei['tmp'], $ziel ) ) {
		return '';
	}
	return $relativ;
}

function tamil_site_werbung_datei_loeschen( string $relativ ): void {
	if ( '' !== $relativ ) {
		wp_delete_file( trailingslashit( wp_get_upload_dir()['basedir'] ) . $relativ );
	}
}

/**
 * Schritte 3 und 4: Kundendaten und Werbemittel; reserviert die Tage.
 */
function tamil_site_werbung_post_buchen(): void {
	$d      = array(
		'platz'            => sanitize_key( tamil_site_werbung_post( 'platz' ) ),
		'laufzeit'         => absint( tamil_site_werbung_post( 'laufzeit' ) ),
		'start'            => tamil_site_werbung_post( 'start' ),
		'firma'            => tamil_site_werbung_post( 'firma' ),
		'ansprechperson'   => tamil_site_werbung_post( 'ansprechperson' ),
		'rechnungsadresse' => tamil_site_werbung_post( 'rechnungsadresse', true ),
		'email'            => sanitize_email( tamil_site_werbung_post( 'email' ) ),
		'telefon'          => tamil_site_werbung_post( 'telefon' ),
		'ust_id'           => tamil_site_werbung_post( 'ust_id' ),
		'ziel_url'         => esc_url_raw( tamil_site_werbung_post( 'ziel_url' ), array( 'http', 'https' ) ),
	);
	$fehler = array();
	foreach ( array(
		'firma'            => __( 'Firma', 'tamil-site' ),
		'ansprechperson'   => __( 'Ansprechperson', 'tamil-site' ),
		'rechnungsadresse' => __( 'Rechnungsadresse', 'tamil-site' ),
	) as $feld => $name ) {
		if ( '' === $d[ $feld ] || mb_strlen( $d[ $feld ] ) > 200 + ( 'rechnungsadresse' === $feld ? 300 : 0 ) ) {
			/* translators: %s: Feld */
			$fehler[] = sprintf( __( 'Bitte „%s“ angeben.', 'tamil-site' ), $name );
		}
	}
	if ( ! is_email( $d['email'] ) ) {
		$fehler[] = __( 'Bitte eine gültige E-Mail-Adresse angeben.', 'tamil-site' );
	}
	if ( '' === $d['ziel_url'] || ! wp_http_validate_url( $d['ziel_url'] ) || strlen( $d['ziel_url'] ) > 500 ) {
		$fehler[] = __( 'Bitte eine gültige Zieladresse mit http:// oder https:// angeben.', 'tamil-site' );
	}
	$d['telefon'] = substr( $d['telefon'], 0, 60 );
	$d['ust_id']  = substr( $d['ust_id'], 0, 40 );
	$format       = tamil_site_werbung_formate()[ $d['platz'] ] ?? null;
	if ( ! $format || ! tamil_site_werbung_buchbar( $d['platz'], $d['laufzeit'] ) ) {
		$fehler[] = __( 'Dieser Platz ist mit dieser Laufzeit gerade nicht buchbar.', 'tamil-site' );
	}
	$dateien = array();
	if ( $format ) {
		$felder = array( 'werbemittel_desktop' => $format['desktop'] );
		if ( tamil_site_werbung_zwei_bilder( $d['platz'] ) ) {
			$felder['werbemittel_mobil'] = $format['mobil'];
		}
		foreach ( $felder as $feld => $mass ) {
			$ergebnis = tamil_site_werbung_datei_pruefen( $feld, $mass );
			if ( is_string( $ergebnis ) ) {
				$fehler[] = ( 'werbemittel_mobil' === $feld ? __( 'Bild fürs Handy: ', 'tamil-site' ) : __( 'Bild: ', 'tamil-site' ) ) . $ergebnis;
			} else {
				$dateien[ $feld ] = $ergebnis;
			}
		}
	}
	if ( $fehler ) {
		tamil_site_werbung_zustand(
			array(
				'fehler' => $fehler,
				'alt'    => $d,
			)
		);
		return;
	}
	$d['werbemittel_desktop'] = tamil_site_werbung_datei_speichern( $dateien['werbemittel_desktop'] );
	$d['werbemittel_mobil']   = isset( $dateien['werbemittel_mobil'] ) ? tamil_site_werbung_datei_speichern( $dateien['werbemittel_mobil'] ) : '';
	$ergebnis                 = '' === $d['werbemittel_desktop'] || ( isset( $dateien['werbemittel_mobil'] ) && '' === $d['werbemittel_mobil'] )
		? new WP_Error( 'datei', __( 'Das Bild konnte nicht gespeichert werden.', 'tamil-site' ) )
		: tamil_site_werbung_reservieren( $d );
	if ( is_wp_error( $ergebnis ) ) {
		tamil_site_werbung_datei_loeschen( $d['werbemittel_desktop'] );
		tamil_site_werbung_datei_loeschen( $d['werbemittel_mobil'] );
		tamil_site_werbung_zustand(
			array(
				'fehler' => array( $ergebnis->get_error_message() ),
				'alt'    => $d,
			)
		);
		return;
	}
	[ $b, $token ] = $ergebnis;
	tamil_site_werbung_cookie_setzen( $b['nummer'], $token, 2 * HOUR_IN_SECONDS );
	tamil_site_werbung_weiter(
		add_query_arg(
			array(
				'wb'     => 'zusammenfassung',
				'nummer' => $b['nummer'],
			),
			tamil_site_werbung_seite_url()
		)
	);
}

/**
 * Schritt 5: Bedingungen angenommen → Checkout bei Stripe.
 */
function tamil_site_werbung_post_bezahlen(): void {
	$nummer = strtoupper( sanitize_key( tamil_site_werbung_post( 'nummer' ) ) );
	$paar   = tamil_site_werbung_cookie_buchung( $nummer );
	if ( ! $paar ) {
		tamil_site_werbung_zustand( array( 'fehler' => array( __( 'Diese Buchung gehört nicht zu diesem Browser oder ist abgelaufen.', 'tamil-site' ) ) ) );
		return;
	}
	$b = $paar[0];
	if ( 'reserviert' !== tamil_site_werbung_stand( $b ) ) {
		tamil_site_werbung_zustand( array( 'fehler' => array( __( 'Die Reservierung ist abgelaufen; die Tage sind wieder frei. Bitte neu buchen.', 'tamil-site' ) ) ) );
		return;
	}
	if ( '1' !== tamil_site_werbung_post( 'bedingungen' ) ) {
		tamil_site_werbung_zustand( array( 'fehler' => array( __( 'Bitte die Verkaufsbedingungen annehmen.', 'tamil-site' ) ) ) );
		return;
	}
	global $wpdb;
	$fassung = tamil_site_werbung_angebote()['bedingungen_fassung'];
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- eigene Tabelle
	$wpdb->update(
		tamil_site_werbung_tabelle( 'buchungen' ),
		array(
			'bedingungen_fassung' => '' !== $fassung ? $fassung : 'Entwurf',
			'bedingungen_at'      => gmdate( 'Y-m-d H:i:s' ),
		),
		array( 'id' => (int) $b['id'] )
	);
	tamil_site_werbung_protokoll( (int) $b['id'], 'kunde', 'Bedingungen angenommen (Fassung ' . ( '' !== $fassung ? $fassung : 'Entwurf' ) . ')' );
	$session = null;
	if ( '' !== $b['stripe_session'] ) {
		$session = tamil_site_stripe_aufruf( 'GET', 'checkout/sessions/' . rawurlencode( $b['stripe_session'] ) );
		$session = ! is_wp_error( $session ) && 'open' === ( $session['status'] ?? '' ) ? $session : null;
	}
	if ( null === $session ) {
		$session = tamil_site_stripe_checkout( $b, tamil_site_werbung_seite_url() );
		if ( is_wp_error( $session ) || empty( $session['id'] ) || empty( $session['url'] ) ) {
			tamil_site_werbung_protokoll( (int) $b['id'], 'website', 'Zahlung konnte nicht gestartet werden' . ( is_wp_error( $session ) ? ': ' . $session->get_error_message() : '' ) );
			tamil_site_werbung_zustand( array( 'fehler' => array( __( 'Die Zahlung kann gerade nicht gestartet werden. Bitte in einigen Minuten erneut versuchen.', 'tamil-site' ) ) ) );
			return;
		}
		// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- eigene Tabelle
		$wpdb->update( tamil_site_werbung_tabelle( 'buchungen' ), array( 'stripe_session' => (string) $session['id'] ), array( 'id' => (int) $b['id'] ) );
		tamil_site_werbung_protokoll( (int) $b['id'], 'kunde', 'Zahlung bei Stripe gestartet' );
	}
	add_filter( 'allowed_redirect_hosts', 'tamil_site_werbung_stripe_host' );
	tamil_site_werbung_weiter( (string) $session['url'] );
}

/**
 * Weiterleitung zur Bezahlseite von Stripe erlauben.
 *
 * @param array<int,string> $hosts Erlaubte Hosts.
 * @return array<int,string>
 */
function tamil_site_werbung_stripe_host( array $hosts ): array {
	$hosts[] = 'checkout.stripe.com';
	return $hosts;
}

/**
 * Buchung wiederfinden: Buchungsnummer und E-Mail-Adresse → neuer geheimer Link (der alte gilt nicht mehr).
 */
function tamil_site_werbung_post_wiederfinden(): void {
	$nummer = strtoupper( preg_replace( '/[^A-Za-z0-9]/', '', tamil_site_werbung_post( 'nummer' ) ) );
	$email  = sanitize_email( tamil_site_werbung_post( 'email' ) );
	$sperre = 'tamil_wb_suche_' . md5( $nummer );
	$zahl   = (int) get_transient( $sperre );
	$fehler = __( 'Zu diesen Angaben gibt es keine Buchung.', 'tamil-site' );
	if ( $zahl >= 5 ) {
		$fehler = __( 'Zu viele Versuche. Bitte in 15 Minuten erneut versuchen.', 'tamil-site' );
	} else {
		set_transient( $sperre, $zahl + 1, 15 * MINUTE_IN_SECONDS );
		$b = '' !== $nummer ? tamil_site_werbung_buchung_nach_nummer( $nummer ) : null;
		if ( $b && '' !== $email && hash_equals( strtolower( (string) $b['email'] ), strtolower( $email ) ) ) {
			$token = tamil_site_werbung_neues_token( (int) $b['id'] );
			tamil_site_werbung_protokoll( (int) $b['id'], 'kunde', 'Kundenlink neu ausgegeben (Buchungsnummer und E-Mail)' );
			tamil_site_werbung_weiter( add_query_arg( 'buchung', $token, tamil_site_werbung_seite_url() ) );
		}
	}
	tamil_site_werbung_zustand(
		array(
			'fehler' => array( $fehler ),
			'alt'    => array( 'nummer' => $nummer ),
		)
	);
}

/**
 * Rückkehr von Stripe: Abgleich, dann zum geheimen Link (wenn dieser Browser gebucht hat).
 */
function tamil_site_werbung_rueckkehr(): void {
	$nummer = strtoupper( sanitize_key( tamil_site_werbung_get( 'nummer' ) ) );
	$b      = tamil_site_werbung_buchung_nach_nummer( $nummer );
	if ( ! $b ) {
		return;
	}
	tamil_site_stripe_abgleich( $b );
	$paar = tamil_site_werbung_cookie_buchung( $nummer );
	if ( $paar ) {
		tamil_site_werbung_cookie_setzen( $nummer, '', -HOUR_IN_SECONDS );
		tamil_site_werbung_weiter( add_query_arg( 'buchung', $paar[1], tamil_site_werbung_seite_url() ) );
	}
	tamil_site_werbung_zustand(
		array(
			'meldung' => 'rueckkehr',
			'nummer'  => $nummer,
		)
	);
}

/**
 * Abbruch auf der Bezahlseite: Session bei Stripe beenden, Tage frei.
 */
function tamil_site_werbung_abbruch(): void {
	$nummer = strtoupper( sanitize_key( tamil_site_werbung_get( 'nummer' ) ) );
	$paar   = tamil_site_werbung_cookie_buchung( $nummer );
	tamil_site_werbung_zustand(
		array(
			'meldung' => 'abbruch',
			'nummer'  => $nummer,
		)
	);
	if ( ! $paar || 'offen' !== $paar[0]['zahlung'] ) {
		return;
	}
	$b = $paar[0];
	if ( '' === $b['stripe_session'] ) {
		tamil_site_werbung_zahlung_abbrechen( $b, 'kunde', 'Zahlung abgebrochen' );
		return;
	}
	$antwort = tamil_site_stripe_aufruf( 'POST', 'checkout/sessions/' . rawurlencode( $b['stripe_session'] ) . '/expire', array(), 'ablauf-' . $b['nummer'] );
	if ( ! is_wp_error( $antwort ) && 'expired' === ( $antwort['status'] ?? '' ) ) {
		tamil_site_werbung_zahlung_abbrechen( $b, 'kunde', 'Zahlung abgebrochen' );
	} else {
		tamil_site_stripe_abgleich( $b ); // vielleicht doch bezahlt
	}
}

/**
 * [tamil_werbung]
 */
function tamil_site_werbung_shortcode(): string {
	if ( ! tamil_site_funktion_an( 'werbung' ) ) {
		return '';
	}
	wp_enqueue_style( 'tamil-site-werbung' );
	$z     = tamil_site_werbung_zustand();
	$out   = '';
	$token = tamil_site_werbung_get( 'buchung' );
	$wb    = tamil_site_werbung_get( 'wb' );
	if ( $z['fehler'] ) {
		$out .= '<div class="wb-fehler" role="alert"><ul><li>' . implode( '</li><li>', array_map( 'esc_html', $z['fehler'] ) ) . '</li></ul></div>';
	}
	if ( '' !== $token ) {
		$out .= tamil_site_werbung_html_kunde( $token );
	} elseif ( 'buchen' === $wb ) {
		$out .= tamil_site_werbung_html_buchen();
	} elseif ( 'zusammenfassung' === $wb ) {
		$out .= tamil_site_werbung_html_zusammenfassung( strtoupper( sanitize_key( tamil_site_werbung_get( 'nummer' ) ) ) );
	} elseif ( '' !== $z['meldung'] ) {
		$out .= tamil_site_werbung_html_meldung( $z['meldung'], $z['nummer'] );
	} else {
		$out .= tamil_site_werbung_html_angebote();
	}
	return '<div class="wb-werbung">' . $out . '</div>';
}
add_shortcode( 'tamil_werbung', 'tamil_site_werbung_shortcode' );

require_once __DIR__ . '/werbung-ansichten.php';
