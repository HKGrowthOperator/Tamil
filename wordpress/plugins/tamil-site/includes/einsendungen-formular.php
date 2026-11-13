<?php
/**
 * Einsendungen (F1): die fünf Formulare auf der Website, Shortcode [tamil_einsendung art="event|beitrag|kooperation|werbung|kontakt"].
 *
 * Eingebunden über den Seiteninhalt oder die Customizer-Felder des Themes („Kontaktformular“, „Formular Event
 * einreichen“). Schlichtes eigenes Markup mit Klassen tf-…; gestaltet wird im Theme (nach Tor G3).
 *
 * Annahme nur mit gültigem Nonce, leerem verstecktem Feld, Absendedauer ≥ 3 Sekunden, höchstens fünf Einsendungen
 * je Stunde und IP-Hash, Pflichtfeldern, höchstens drei Links im Text und Einwilligung in der angezeigten Fassung.
 * Bilder (nur Event und Beitrag): JPEG oder PNG bis 5 MB, neu gespeichert ohne Metadaten, nicht öffentlich.
 * Rückmeldung nur auf der Seite (Vorgangsnummer), nie per E-Mail. Funktionsschalter „einreichungen“, Standard aus.
 */

defined( 'ABSPATH' ) || exit;

/** Mindestdauer zwischen Anzeige und Absenden, in Sekunden. */
define( 'TAMIL_SITE_EINSENDUNG_MIN_SEKUNDEN', 3 );
/** Höchstens so viele Einsendungen je Stunde und IP-Hash. */
define( 'TAMIL_SITE_EINSENDUNG_JE_STUNDE', 5 );
/** Höchstens so viele Links in den Textfeldern. */
define( 'TAMIL_SITE_EINSENDUNG_MAX_LINKS', 3 );
/** Größte Bilddatei in Byte (5 MB). */
define( 'TAMIL_SITE_EINSENDUNG_BILD_BYTES', 5 * 1024 * 1024 );
/** Größtes Bild in Pixeln (Schutz des Arbeitsspeichers beim Neuspeichern). */
define( 'TAMIL_SITE_EINSENDUNG_BILD_PIXEL', 25000000 );

/**
 * Felder je Art. Typen: text, textarea, email, tel, url, datetime, land.
 *
 * @return array<string,array{label:string,typ:string,pflicht:bool,max:int,hilfe?:string}>
 */
function tamil_site_einsendung_felder( string $art ): array {
	$f     = static function ( string $label, string $typ = 'text', bool $pflicht = false, int $max = 200, string $hilfe = '' ): array {
		$feld = array(
			'label'   => $label,
			'typ'     => $typ,
			'pflicht' => $pflicht,
			'max'     => $max,
		);
		if ( '' !== $hilfe ) {
			$feld['hilfe'] = $hilfe;
		}
		return $feld;
	};
	$arten = array(
		'event'       => array(
			'titel'        => $f( __( 'Titel', 'tamil-site' ), 'text', true ),
			'beginn'       => $f( __( 'Datum und Uhrzeit', 'tamil-site' ), 'datetime', true, 20 ),
			'ende'         => $f( __( 'Ende', 'tamil-site' ), 'datetime', false, 20 ),
			'ort'          => $f( __( 'Ort mit Adresse', 'tamil-site' ), 'text', true, 300, __( 'Saal oder Gebäude, Straße und Hausnummer', 'tamil-site' ) ),
			'stadt'        => $f( __( 'Stadt', 'tamil-site' ), 'text', true, 100 ),
			'land'         => $f( __( 'Land', 'tamil-site' ), 'land', true, 2 ),
			'veranstalter' => $f( __( 'Veranstalter', 'tamil-site' ), 'text', true ),
			'beschreibung' => $f( __( 'Beschreibung', 'tamil-site' ), 'textarea', true, 5000 ),
			'eintritt'     => $f( __( 'Eintritt', 'tamil-site' ), 'text', false, 100, __( 'z. B. 15 Euro, Kinder frei', 'tamil-site' ) ),
			'ticket_link'  => $f( __( 'Ticket-Link', 'tamil-site' ), 'url', false, 500 ),
		),
		'beitrag'     => array(
			'thema' => $f( __( 'Thema', 'tamil-site' ), 'text', true ),
			'text'  => $f( __( 'Hinweis oder Text', 'tamil-site' ), 'textarea', true, 10000 ),
			'link'  => $f( __( 'Link', 'tamil-site' ), 'url', false, 500 ),
		),
		'kooperation' => array(
			'organisation' => $f( __( 'Organisation', 'tamil-site' ) ),
			'anliegen'     => $f( __( 'Anliegen', 'tamil-site' ), 'textarea', true, 5000 ),
		),
		'werbung'     => array(
			'firma'          => $f( __( 'Firma', 'tamil-site' ) ),
			'platz_zeitraum' => $f( __( 'Gewünschter Platz und Zeitraum', 'tamil-site' ), 'text', false, 300 ),
			'nachricht'      => $f( __( 'Nachricht', 'tamil-site' ), 'textarea', true, 5000 ),
		),
		'kontakt'     => array(
			'nachricht' => $f( __( 'Nachricht', 'tamil-site' ), 'textarea', true, 5000 ),
		),
	);
	return $arten[ $art ] ?? array();
}

/**
 * Gemeinsame Felder aller Formulare.
 *
 * @return array<string,array{label:string,typ:string,pflicht:bool,max:int}>
 */
function tamil_site_einsendung_felder_person(): array {
	return array(
		'name'    => array(
			'label'   => __( 'Name', 'tamil-site' ),
			'typ'     => 'text',
			'pflicht' => true,
			'max'     => 200,
		),
		'email'   => array(
			'label'   => __( 'E-Mail-Adresse', 'tamil-site' ),
			'typ'     => 'email',
			'pflicht' => true,
			'max'     => 200,
		),
		'telefon' => array(
			'label'   => __( 'Telefon', 'tamil-site' ),
			'typ'     => 'tel',
			'pflicht' => false,
			'max'     => 40,
		),
	);
}

/**
 * Darf diese Art ein Bild mitschicken?
 */
function tamil_site_einsendung_mit_bild( string $art ): bool {
	return in_array( $art, array( 'event', 'beitrag' ), true );
}

/**
 * Länder für Termine.
 *
 * @return array<string,string>
 */
function tamil_site_einsendung_laender(): array {
	return array(
		'DE' => __( 'Deutschland', 'tamil-site' ),
		'AT' => __( 'Österreich', 'tamil-site' ),
		'CH' => __( 'Schweiz', 'tamil-site' ),
	);
}

/**
 * Einwilligungstext und Fassung (gepflegt unter Werkzeuge → Einsendungen; bis KBS liefert: vorläufige Fassung).
 *
 * @return array{text:string,fassung:string}
 */
function tamil_site_einsendung_einwilligung(): array {
	$standard    = array(
		'text'    => __( 'Vorläufige Fassung. Ich willige ein, dass Tamil.de meine Angaben speichert, um meine Einsendung zu bearbeiten und mich bei Rückfragen zu kontaktieren. Die Angaben werden 90 Tage nach Abschluss gelöscht.', 'tamil-site' ),
		'fassung' => '2026-11-vorlaeufig',
	);
	$gespeichert = get_option( 'tamil_site_einsendungen', array() );
	$gespeichert = is_array( $gespeichert ) ? array_filter( array_map( 'strval', $gespeichert ), 'strlen' ) : array();
	return array_merge( $standard, array_intersect_key( $gespeichert, $standard ) );
}

/**
 * Bereinigung für die Einstellungen (Einwilligungstext und Fassung).
 *
 * @param mixed $input Formularwerte.
 * @return array{text:string,fassung:string}
 */
function tamil_site_sanitize_einsendungen( $input ): array {
	$input = is_array( $input ) ? $input : array();
	return array(
		'text'    => sanitize_textarea_field( (string) ( $input['text'] ?? '' ) ),
		'fassung' => substr( sanitize_key( str_replace( '.', '-', (string) ( $input['fassung'] ?? '' ) ) ), 0, 40 ),
	);
}

/**
 * Zeitstempel für das Formular (Unixzeit plus Prüfsumme, damit niemand ihn vordatiert).
 *
 * @param int|null $zeit Unixzeit (Standard: jetzt).
 */
function tamil_site_einsendung_zeitstempel( ?int $zeit = null ): string {
	$zeit = $zeit ?? time();
	return $zeit . '.' . substr( wp_hash( 'tamil-einsendung-zeit|' . $zeit ), 0, 20 );
}

/**
 * Prüft den Zeitstempel: ok, schnell (unter 3 Sekunden) oder ungueltig (gefälscht oder älter als einen Tag).
 *
 * @param int|null $jetzt Unixzeit (Standard: jetzt).
 */
function tamil_site_einsendung_zeit_pruefen( string $wert, ?int $jetzt = null ): string {
	$jetzt = $jetzt ?? time();
	if ( ! preg_match( '/^(\d{9,11})\.([a-f0-9]{20})$/', $wert, $m ) ) {
		return 'ungueltig';
	}
	if ( ! hash_equals( tamil_site_einsendung_zeitstempel( (int) $m[1] ), $wert ) ) {
		return 'ungueltig';
	}
	$dauer = $jetzt - (int) $m[1];
	if ( $dauer > DAY_IN_SECONDS ) {
		return 'ungueltig';
	}
	return $dauer < TAMIL_SITE_EINSENDUNG_MIN_SEKUNDEN ? 'schnell' : 'ok';
}

/**
 * Adresse des Besuchers. Hinter einem Proxy (Traefik in Coolify) zählt der Eintrag aus X-Forwarded-For, den der
 * vertrauenswürdige Proxy angehängt hat: TAMIL_PROXY_ANZAHL in wp-config.php = Zahl der Proxys vor WordPress.
 */
function tamil_site_einsendung_client_ip(): string {
	$ip     = isset( $_SERVER['REMOTE_ADDR'] ) ? sanitize_text_field( wp_unslash( $_SERVER['REMOTE_ADDR'] ) ) : '';
	$proxys = defined( 'TAMIL_PROXY_ANZAHL' ) ? (int) TAMIL_PROXY_ANZAHL : 0;
	if ( $proxys > 0 && isset( $_SERVER['HTTP_X_FORWARDED_FOR'] ) ) {
		$kette = array_values( array_filter( array_map( 'trim', explode( ',', sanitize_text_field( wp_unslash( $_SERVER['HTTP_X_FORWARDED_FOR'] ) ) ) ) ) );
		$wahl  = $kette[ count( $kette ) - $proxys ] ?? '';
		if ( filter_var( $wahl, FILTER_VALIDATE_IP ) ) {
			$ip = $wahl;
		}
	}
	return $ip;
}

/**
 * Nicht rückrechenbarer Wert der Adresse (HMAC mit dem geheimen Salz der Installation).
 */
function tamil_site_einsendung_ip_hash( string $ip ): string {
	return hash_hmac( 'sha256', $ip, wp_salt( 'nonce' ) );
}

/**
 * Wie viele Einsendungen kamen in der letzten Stunde von diesem IP-Hash?
 */
function tamil_site_einsendung_drossel_zaehler( string $ip_hash ): int {
	global $wpdb;
	$t = tamil_site_einsendung_tabelle();
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- eigene Tabelle
	return (int) $wpdb->get_var( $wpdb->prepare( "SELECT COUNT(*) FROM {$t} WHERE ip_hash = %s AND eingang_at >= %s", $ip_hash, gmdate( 'Y-m-d H:i:s', time() - HOUR_IN_SECONDS ) ) );
}

/**
 * Zählt Links in Freitext.
 */
function tamil_site_einsendung_links_zaehlen( string $text ): int {
	return (int) preg_match_all( '~(?:https?://|www\.)~i', $text );
}

/**
 * Prüfsumme für die Danke-Anzeige (nur echte Vorgangsnummern werden angezeigt).
 */
function tamil_site_einsendung_danke_pruef( string $vorgang, string $art ): string {
	return substr( wp_hash( 'tamil-einsendung-danke|' . $vorgang . '|' . $art ), 0, 16 );
}

/**
 * Prüft und bereinigt die Feldwerte (ohne Spam-Schutz und Bild).
 *
 * @param string              $art  Formularart.
 * @param array<string,mixed> $roh  Werte aus dem Formular (ungeschlüpft, unbereinigt).
 * @return array{werte:array<string,string>,fehler:array<string,string>}
 */
function tamil_site_einsendung_werte_pruefen( string $art, array $roh ): array {
	$werte  = array();
	$fehler = array();
	$felder = tamil_site_einsendung_felder_person() + tamil_site_einsendung_felder( $art );
	foreach ( $felder as $key => $feld ) {
		$wert = is_scalar( $roh[ $key ] ?? null ) ? (string) $roh[ $key ] : '';
		$wert = 'textarea' === $feld['typ'] ? sanitize_textarea_field( $wert ) : sanitize_text_field( $wert );
		$wert = trim( mb_substr( $wert, 0, $feld['max'] ) );
		if ( '' === $wert ) {
			$werte[ $key ] = '';
			if ( $feld['pflicht'] ) {
				/* translators: %s: Feldname */
				$fehler[ $key ] = sprintf( __( '%s fehlt.', 'tamil-site' ), $feld['label'] );
			}
			continue;
		}
		switch ( $feld['typ'] ) {
			case 'email':
				$wert = sanitize_email( $wert );
				if ( ! is_email( $wert ) ) {
					$fehler[ $key ] = __( 'Bitte eine gültige E-Mail-Adresse angeben.', 'tamil-site' );
				}
				break;
			case 'tel':
				if ( ! preg_match( '~^\+?[0-9 ()/.\-]{5,40}$~', $wert ) ) {
					$fehler[ $key ] = __( 'Bitte nur Ziffern, Leerzeichen und + ( ) / - verwenden.', 'tamil-site' );
				}
				break;
			case 'url':
				$sauber = esc_url_raw( $wert, array( 'http', 'https' ) );
				if ( '' === $sauber || ! filter_var( $sauber, FILTER_VALIDATE_URL ) ) {
					$fehler[ $key ] = __( 'Bitte einen vollständigen Link mit https:// angeben.', 'tamil-site' );
				}
				$wert = $sauber;
				break;
			case 'datetime':
				$zeit = DateTimeImmutable::createFromFormat( '!Y-m-d\TH:i', $wert, wp_timezone() );
				if ( ! $zeit ) {
					$zeit = DateTimeImmutable::createFromFormat( '!Y-m-d H:i', $wert, wp_timezone() );
				}
				if ( ! $zeit ) {
					$fehler[ $key ] = __( 'Bitte Datum und Uhrzeit vollständig angeben.', 'tamil-site' );
				} else {
					$wert = $zeit->format( 'c' );
				}
				break;
			case 'land':
				if ( ! array_key_exists( $wert, tamil_site_einsendung_laender() ) ) {
					$fehler[ $key ] = __( 'Bitte Deutschland, Österreich oder die Schweiz wählen.', 'tamil-site' );
				}
				break;
		}
		$werte[ $key ] = $wert;
	}
	$freitext = '';
	$erstes   = '';
	foreach ( tamil_site_einsendung_felder( $art ) as $key => $feld ) {
		if ( in_array( $feld['typ'], array( 'text', 'textarea' ), true ) ) {
			$freitext .= ' ' . $werte[ $key ];
			if ( '' === $erstes && 'textarea' === $feld['typ'] ) {
				$erstes = $key;
			}
		}
	}
	if ( tamil_site_einsendung_links_zaehlen( $freitext ) > TAMIL_SITE_EINSENDUNG_MAX_LINKS && ! isset( $fehler[ $erstes ] ) ) {
		/* translators: %d: Anzahl */
		$fehler[ $erstes ] = sprintf( __( 'Bitte höchstens %d Links im Text.', 'tamil-site' ), TAMIL_SITE_EINSENDUNG_MAX_LINKS );
	}
	return array(
		'werte'  => $werte,
		'fehler' => $fehler,
	);
}

/**
 * Nimmt ein hochgeladenes Bild an: Größe, echter Typ (JPEG/PNG), Pixelzahl; speichert es neu ohne Metadaten unter
 * zufälligem Namen im geschützten Ordner.
 *
 * @param array<string,mixed> $datei Eintrag aus $_FILES.
 * @param bool                $hochgeladen Prüfen, dass die Datei aus einem Upload stammt (Tests: false).
 * @return array{datei:string,typ:string,groesse:int,sha256:string}|null|WP_Error null = kein Bild.
 */
function tamil_site_einsendung_bild_annehmen( array $datei, bool $hochgeladen = true ) {
	$fehler = (int) ( $datei['error'] ?? UPLOAD_ERR_NO_FILE );
	if ( UPLOAD_ERR_NO_FILE === $fehler ) {
		return null;
	}
	$zu_gross = new WP_Error( 'bild', __( 'Das Bild ist größer als 5 MB.', 'tamil-site' ) );
	if ( in_array( $fehler, array( UPLOAD_ERR_INI_SIZE, UPLOAD_ERR_FORM_SIZE ), true ) ) {
		return $zu_gross;
	}
	$tmp = (string) ( $datei['tmp_name'] ?? '' );
	if ( UPLOAD_ERR_OK !== $fehler || '' === $tmp || ! is_file( $tmp ) || ( $hochgeladen && ! is_uploaded_file( $tmp ) ) ) {
		return new WP_Error( 'bild', __( 'Das Bild konnte nicht hochgeladen werden.', 'tamil-site' ) );
	}
	if ( filesize( $tmp ) > TAMIL_SITE_EINSENDUNG_BILD_BYTES ) {
		return $zu_gross;
	}
	$falsch = new WP_Error( 'bild', __( 'Bitte nur Bilder im Format JPEG oder PNG.', 'tamil-site' ) );
	$info   = @getimagesize( $tmp ); // phpcs:ignore WordPress.PHP.NoSilencedErrors.Discouraged -- kaputte Dateien sind ein erwarteter Fall
	if ( ! $info || ! in_array( $info[2], array( IMAGETYPE_JPEG, IMAGETYPE_PNG ), true ) ) {
		return $falsch;
	}
	if ( $info[0] < 1 || $info[1] < 1 || $info[0] * $info[1] > TAMIL_SITE_EINSENDUNG_BILD_PIXEL ) {
		return new WP_Error( 'bild', __( 'Das Bild hat zu viele Pixel (höchstens 25 Megapixel).', 'tamil-site' ) );
	}
	if ( ! function_exists( 'imagecreatefromjpeg' ) ) {
		return new WP_Error( 'bild', __( 'Bilder können derzeit nicht angenommen werden.', 'tamil-site' ) );
	}
	$jpeg = IMAGETYPE_JPEG === $info[2];
	// phpcs:ignore WordPress.PHP.NoSilencedErrors.Discouraged -- kaputte Dateien sind ein erwarteter Fall
	$bild = $jpeg ? @imagecreatefromjpeg( $tmp ) : @imagecreatefrompng( $tmp );
	if ( ! $bild ) {
		return $falsch;
	}
	if ( $jpeg && function_exists( 'exif_read_data' ) ) {
		$exif    = @exif_read_data( $tmp ); // phpcs:ignore WordPress.PHP.NoSilencedErrors.Discouraged -- fehlende EXIF-Daten sind normal
		$drehung = array(
			3 => 180,
			6 => -90,
			8 => 90,
		)[ (int) ( $exif['Orientation'] ?? 1 ) ] ?? 0;
		if ( $drehung ) {
			$gedreht = imagerotate( $bild, $drehung, 0 );
			if ( $gedreht ) {
				imagedestroy( $bild );
				$bild = $gedreht;
			}
		}
	}
	$name = bin2hex( random_bytes( 16 ) ) . ( $jpeg ? '.jpg' : '.png' );
	$pfad = tamil_site_einsendung_bildordner() . $name;
	if ( $jpeg ) {
		$ok = imagejpeg( $bild, $pfad, 90 );
	} else {
		imagesavealpha( $bild, true );
		$ok = imagepng( $bild, $pfad, 6 );
	}
	imagedestroy( $bild );
	if ( ! $ok || ! is_file( $pfad ) ) {
		return new WP_Error( 'bild', __( 'Das Bild konnte nicht gespeichert werden.', 'tamil-site' ) );
	}
	return array(
		'datei'   => $name,
		'typ'     => $jpeg ? 'image/jpeg' : 'image/png',
		'groesse' => (int) filesize( $pfad ),
		'sha256'  => (string) hash_file( 'sha256', $pfad ),
	);
}

/**
 * Zustand des zuletzt abgesendeten Formulars in diesem Aufruf (Fehler und Werte für die erneute Anzeige).
 *
 * @param array<string,mixed>|null $neu Neuer Zustand.
 * @return array<string,mixed>
 */
function tamil_site_einsendung_zustand( ?array $neu = null ): array {
	static $zustand = array();
	if ( null !== $neu ) {
		$zustand = $neu;
	}
	return $zustand;
}

/**
 * Verarbeitet ein abgesendetes Formular (template_redirect, vor allen anderen). Erfolg: 303 auf dieselbe Seite mit
 * Vorgangsnummer. Sonst bleibt der Zustand für die Anzeige stehen.
 */
function tamil_site_einsendung_verarbeiten(): void {
	$methode = isset( $_SERVER['REQUEST_METHOD'] ) ? strtoupper( sanitize_key( wp_unslash( $_SERVER['REQUEST_METHOD'] ) ) ) : '';
	if ( 'POST' !== $methode || ! isset( $_POST['tf_art'] ) ) { // phpcs:ignore WordPress.Security.NonceVerification.Missing -- Nonce wird unten geprüft
		return;
	}
	$art = sanitize_key( wp_unslash( $_POST['tf_art'] ) ); // phpcs:ignore WordPress.Security.NonceVerification.Missing -- Nonce wird unten geprüft
	if ( ! array_key_exists( $art, tamil_site_einsendung_arten() ) || ! tamil_site_funktion_an( 'einreichungen' ) ) {
		return;
	}
	$ergebnis = tamil_site_einsendung_annehmen( $art );
	if ( is_string( $ergebnis ) ) {
		$ziel = is_singular() ? (string) get_permalink( get_queried_object_id() ) : home_url( '/' );
		$ziel = add_query_arg(
			array(
				'eingang' => rawurlencode( $ergebnis ),
				'art'     => $art,
				'pruef'   => tamil_site_einsendung_danke_pruef( $ergebnis, $art ),
			),
			$ziel
		) . '#tf-' . $art;
		wp_safe_redirect( $ziel, 303 );
		exit;
	}
	tamil_site_einsendung_zustand( array_merge( $ergebnis, array( 'art' => $art ) ) );
}
add_action( 'template_redirect', 'tamil_site_einsendung_verarbeiten', 1 );

/**
 * Prüft und speichert die Einsendung aus $_POST/$_FILES.
 *
 * @return string|array{werte:array<string,string>,fehler:array<string,string>,meldung:string} Vorgangsnummer oder Zustand.
 */
function tamil_site_einsendung_annehmen( string $art ) {
	$roh   = isset( $_POST['tf'] ) && is_array( $_POST['tf'] ) ? wp_unslash( $_POST['tf'] ) : array(); // phpcs:ignore WordPress.Security.NonceVerification.Missing, WordPress.Security.ValidatedSanitizedInput.InputNotSanitized -- Nonce unten; bereinigt wird je Feld in tamil_site_einsendung_werte_pruefen()
	$leer  = array(
		'werte'  => array(),
		'fehler' => array(),
	);
	$nicht = __( 'Die Einsendung wurde nicht angenommen.', 'tamil-site' );

	$nonce = isset( $_POST['tf_nonce'] ) ? sanitize_text_field( wp_unslash( $_POST['tf_nonce'] ) ) : '';
	$zeit  = isset( $_POST['tf_zeit'] ) ? sanitize_text_field( wp_unslash( $_POST['tf_zeit'] ) ) : '';
	$falle = isset( $_POST['tf_webseite'] ) ? sanitize_text_field( wp_unslash( $_POST['tf_webseite'] ) ) : '';
	$gepr  = tamil_site_einsendung_werte_pruefen( $art, (array) $roh );

	if ( ! wp_verify_nonce( $nonce, 'tamil_einsendung_' . $art ) || 'ungueltig' === tamil_site_einsendung_zeit_pruefen( $zeit ) ) {
		return array_merge( $gepr, array( 'meldung' => __( 'Das Formular ist abgelaufen. Bitte prüft eure Angaben und sendet es noch einmal ab.', 'tamil-site' ) ) );
	}
	if ( '' !== $falle ) {
		return array_merge( $leer, array( 'meldung' => $nicht ) );
	}
	if ( 'schnell' === tamil_site_einsendung_zeit_pruefen( $zeit ) ) {
		return array_merge( $gepr, array( 'meldung' => $nicht . ' ' . __( 'Sie kam schneller, als ein Mensch tippen kann. Bitte sendet sie noch einmal ab.', 'tamil-site' ) ) );
	}
	$ip_hash = tamil_site_einsendung_ip_hash( tamil_site_einsendung_client_ip() );
	if ( tamil_site_einsendung_drossel_zaehler( $ip_hash ) >= TAMIL_SITE_EINSENDUNG_JE_STUNDE ) {
		return array_merge( $gepr, array( 'meldung' => $nicht . ' ' . __( 'Von eurem Anschluss kamen in der letzten Stunde zu viele Einsendungen. Bitte versucht es später noch einmal.', 'tamil-site' ) ) );
	}

	$fehler       = $gepr['fehler'];
	$einwilligung = tamil_site_einsendung_einwilligung();
	$fassung      = isset( $_POST['tf_fassung'] ) ? sanitize_key( wp_unslash( $_POST['tf_fassung'] ) ) : '';
	if ( empty( $_POST['tf_einwilligung'] ) ) {
		$fehler['einwilligung'] = __( 'Ohne Einwilligung können wir die Einsendung nicht annehmen.', 'tamil-site' );
	} elseif ( $fassung !== $einwilligung['fassung'] ) {
		$fehler['einwilligung'] = __( 'Der Text der Einwilligung hat sich geändert. Bitte lest ihn und bestätigt ihn noch einmal.', 'tamil-site' );
	}

	$bild  = null;
	$recht = ! empty( $_POST['tf_bild_recht'] );
	if ( tamil_site_einsendung_mit_bild( $art ) && isset( $_FILES['tf_bild'] ) && is_array( $_FILES['tf_bild'] ) && UPLOAD_ERR_NO_FILE !== (int) ( $_FILES['tf_bild']['error'] ?? UPLOAD_ERR_NO_FILE ) ) {
		if ( ! $recht ) {
			$fehler['bild_recht'] = __( 'Bitte bestätigt, dass das Bild verwendet werden darf, oder schickt die Einsendung ohne Bild.', 'tamil-site' );
		} elseif ( ! $fehler ) {
			$bild = tamil_site_einsendung_bild_annehmen( $_FILES['tf_bild'] ); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput.InputNotSanitized -- Datei wird geprüft und neu gespeichert
			if ( is_wp_error( $bild ) ) {
				$fehler['bild'] = $bild->get_error_message();
				$bild           = null;
			}
		}
	}
	if ( $fehler ) {
		return array(
			'werte'   => $gepr['werte'],
			'fehler'  => $fehler,
			'meldung' => __( 'Bitte prüft die markierten Angaben.', 'tamil-site' ),
		);
	}

	$person  = array_intersect_key( $gepr['werte'], tamil_site_einsendung_felder_person() );
	$vorgang = tamil_site_einsendung_speichern(
		array(
			'art'                   => $art,
			'name'                  => $person['name'],
			'email'                 => $person['email'],
			'telefon'               => $person['telefon'],
			'felder'                => array_intersect_key( $gepr['werte'], tamil_site_einsendung_felder( $art ) ),
			'einwilligung_fassung'  => $einwilligung['fassung'],
			'bild'                  => $bild,
			'bild_recht_bestaetigt' => $recht,
			'ip_hash'               => $ip_hash,
		)
	);
	if ( is_wp_error( $vorgang ) ) {
		if ( $bild ) {
			wp_delete_file( tamil_site_einsendung_bildordner() . $bild['datei'] );
		}
		return array_merge( $gepr, array( 'meldung' => $vorgang->get_error_message() ) );
	}
	return $vorgang;
}

/**
 * Formularseiten nie zwischenspeichern (Nonce, Zeitstempel, Danke-Anzeige).
 *
 * @param bool $nie Bisheriger Wert.
 */
function tamil_site_einsendung_nie_zwischenspeichern( bool $nie ): bool {
	if ( $nie || ! tamil_site_funktion_an( 'einreichungen' ) || ! is_singular() ) {
		return $nie;
	}
	$post = get_queried_object();
	return $post instanceof WP_Post && ( has_shortcode( $post->post_content, 'tamil_einsendung' ) || ( 'page' === $post->post_type && 'kontakt' === $post->post_name ) );
}
add_filter( 'tamil_site_nie_zwischenspeichern', 'tamil_site_einsendung_nie_zwischenspeichern' );

/**
 * Shortcode registrieren.
 */
function tamil_site_einsendung_shortcode_anmelden(): void {
	add_shortcode( 'tamil_einsendung', 'tamil_site_einsendung_shortcode' );
}
add_action( 'init', 'tamil_site_einsendung_shortcode_anmelden' );

/**
 * [tamil_einsendung art="…"]
 *
 * @param array<string,string>|string $atts Attribute.
 */
function tamil_site_einsendung_shortcode( $atts ): string {
	$atts = shortcode_atts( array( 'art' => 'kontakt' ), is_array( $atts ) ? $atts : array(), 'tamil_einsendung' );
	$art  = sanitize_key( $atts['art'] );
	if ( ! array_key_exists( $art, tamil_site_einsendung_arten() ) ) {
		return '';
	}
	if ( ! tamil_site_funktion_an( 'einreichungen' ) ) {
		return '<div class="tf tf-aus" id="tf-' . esc_attr( $art ) . '"><p>' . esc_html__( 'Dieses Formular steht derzeit nicht zur Verfügung.', 'tamil-site' ) . '</p></div>';
	}
	$css = 'assets/einsendungen.css';
	wp_enqueue_style( 'tamil-site-einsendungen', TAMIL_SITE_URL . $css, array(), TAMIL_SITE_VERSION . '.' . filemtime( TAMIL_SITE_DIR . $css ) );
	ob_start();
	tamil_site_einsendung_formular( $art );
	return (string) ob_get_clean();
}

/**
 * Danke-Anzeige, falls die Adresse eine echte Vorgangsnummer dieser Art trägt.
 */
function tamil_site_einsendung_danke( string $art ): string {
	// phpcs:disable WordPress.Security.NonceVerification.Recommended -- nur Anzeige, durch Prüfsumme gesichert
	$vorgang = isset( $_GET['eingang'] ) ? sanitize_text_field( wp_unslash( $_GET['eingang'] ) ) : '';
	$von_art = isset( $_GET['art'] ) ? sanitize_key( wp_unslash( $_GET['art'] ) ) : '';
	$pruef   = isset( $_GET['pruef'] ) ? sanitize_key( wp_unslash( $_GET['pruef'] ) ) : '';
	// phpcs:enable WordPress.Security.NonceVerification.Recommended
	if ( $von_art !== $art || ! tamil_site_einsendung_vorgangsnummer_gueltig( $vorgang ) || ! hash_equals( tamil_site_einsendung_danke_pruef( $vorgang, $art ), $pruef ) ) {
		return '';
	}
	return $vorgang;
}

/**
 * Gibt das Formular einer Art aus.
 */
function tamil_site_einsendung_formular( string $art ): void {
	$id      = 'tf-' . $art;
	$vorgang = tamil_site_einsendung_danke( $art );
	if ( '' !== $vorgang ) {
		$neu = remove_query_arg( array( 'eingang', 'art', 'pruef' ) );
		?>
		<div class="tf tf-<?php echo esc_attr( $art ); ?>" id="<?php echo esc_attr( $id ); ?>">
			<div class="tf-danke" role="status">
				<p><?php esc_html_e( 'Danke, die Redaktion meldet sich.', 'tamil-site' ); ?></p>
				<p><?php esc_html_e( 'Eure Vorgangsnummer:', 'tamil-site' ); ?> <strong class="tf-vorgang"><?php echo esc_html( $vorgang ); ?></strong></p>
				<p><a href="<?php echo esc_url( $neu . '#' . $id ); ?>"><?php esc_html_e( 'Noch etwas einsenden', 'tamil-site' ); ?></a></p>
			</div>
		</div>
		<?php
		return;
	}
	$zustand      = tamil_site_einsendung_zustand();
	$aktiv        = ( $zustand['art'] ?? '' ) === $art;
	$werte        = $aktiv ? (array) ( $zustand['werte'] ?? array() ) : array();
	$fehler       = $aktiv ? (array) ( $zustand['fehler'] ?? array() ) : array();
	$meldung      = $aktiv ? (string) ( $zustand['meldung'] ?? '' ) : '';
	$einwilligung = tamil_site_einsendung_einwilligung();
	$datenschutz  = tamil_site_zustimmung_datenschutz_url();
	$ziel         = is_singular() ? (string) get_permalink( get_queried_object_id() ) : home_url( '/' );
	$mit_bild     = tamil_site_einsendung_mit_bild( $art );
	$felder       = tamil_site_einsendung_felder( $art ) + tamil_site_einsendung_felder_person();
	?>
	<div class="tf tf-<?php echo esc_attr( $art ); ?>" id="<?php echo esc_attr( $id ); ?>">
		<form class="tf-formular" method="post" action="<?php echo esc_url( $ziel . '#' . $id ); ?>" aria-label="<?php echo esc_attr( tamil_site_einsendung_arten()[ $art ] ); ?>"<?php echo $mit_bild ? ' enctype="multipart/form-data"' : ''; ?>>
			<?php if ( '' !== $meldung ) : ?>
			<div class="tf-meldung" role="alert">
				<p><?php echo esc_html( $meldung ); ?></p>
				<?php if ( $fehler ) : ?>
				<ul>
					<?php foreach ( $fehler as $key => $text ) : ?>
					<li><a href="#<?php echo esc_attr( $id . '-' . str_replace( '_', '-', (string) $key ) ); ?>"><?php echo esc_html( $text ); ?></a></li>
					<?php endforeach; ?>
				</ul>
				<?php endif; ?>
			</div>
			<?php endif; ?>
			<p class="tf-hinweis"><?php esc_html_e( 'Pflichtfelder sind mit „Pflicht“ gekennzeichnet.', 'tamil-site' ); ?></p>
			<?php
			foreach ( $felder as $key => $feld ) {
				tamil_site_einsendung_feld( $id, (string) $key, $feld, (string) ( $werte[ $key ] ?? '' ), (string) ( $fehler[ $key ] ?? '' ) );
			}
			if ( $mit_bild ) :
				$bild_id = $id . '-bild';
				?>
			<p class="tf-feld">
				<label for="<?php echo esc_attr( $bild_id ); ?>"><?php esc_html_e( 'Bild', 'tamil-site' ); ?></label>
				<input type="file" id="<?php echo esc_attr( $bild_id ); ?>" name="tf_bild" accept="image/jpeg,image/png" aria-describedby="<?php echo esc_attr( $bild_id . '-hilfe' ); ?><?php echo isset( $fehler['bild'] ) ? ' ' . esc_attr( $bild_id . '-fehler' ) : ''; ?>"<?php echo isset( $fehler['bild'] ) ? ' aria-invalid="true"' : ''; ?>>
				<span class="tf-hilfe" id="<?php echo esc_attr( $bild_id . '-hilfe' ); ?>"><?php esc_html_e( 'Freiwillig. JPEG oder PNG, höchstens 5 MB. Bei einem Fehler bitte das Bild noch einmal auswählen.', 'tamil-site' ); ?></span>
				<?php if ( isset( $fehler['bild'] ) ) : ?>
				<span class="tf-fehler" id="<?php echo esc_attr( $bild_id . '-fehler' ); ?>"><?php echo esc_html( $fehler['bild'] ); ?></span>
				<?php endif; ?>
			</p>
			<p class="tf-feld tf-auswahl">
				<input type="checkbox" id="<?php echo esc_attr( $id . '-bild-recht' ); ?>" name="tf_bild_recht" value="1"<?php echo isset( $fehler['bild_recht'] ) ? ' aria-invalid="true" aria-describedby="' . esc_attr( $id . '-bild-recht-fehler' ) . '"' : ''; ?>>
				<label for="<?php echo esc_attr( $id . '-bild-recht' ); ?>"><?php esc_html_e( 'Ich bestätige, dass das Bild von Tamil.de verwendet werden darf (nur nötig, wenn ich ein Bild mitschicke).', 'tamil-site' ); ?></label>
				<?php if ( isset( $fehler['bild_recht'] ) ) : ?>
				<span class="tf-fehler" id="<?php echo esc_attr( $id . '-bild-recht-fehler' ); ?>"><?php echo esc_html( $fehler['bild_recht'] ); ?></span>
				<?php endif; ?>
			</p>
			<?php endif; ?>
			<p class="tf-feld tf-auswahl tf-einwilligung">
				<input type="checkbox" id="<?php echo esc_attr( $id . '-einwilligung' ); ?>" name="tf_einwilligung" value="1" required<?php echo isset( $fehler['einwilligung'] ) ? ' aria-invalid="true" aria-describedby="' . esc_attr( $id . '-einwilligung-fehler' ) . '"' : ''; ?>>
				<label for="<?php echo esc_attr( $id . '-einwilligung' ); ?>"><?php echo esc_html( $einwilligung['text'] ); ?> <span class="tf-pflicht"><?php esc_html_e( '(Pflicht)', 'tamil-site' ); ?></span></label>
				<?php if ( $datenschutz ) : ?>
				<a class="tf-datenschutz" href="<?php echo esc_url( $datenschutz ); ?>"><?php esc_html_e( 'Datenschutzerklärung', 'tamil-site' ); ?></a>
				<?php endif; ?>
				<?php if ( isset( $fehler['einwilligung'] ) ) : ?>
				<span class="tf-fehler" id="<?php echo esc_attr( $id . '-einwilligung-fehler' ); ?>"><?php echo esc_html( $fehler['einwilligung'] ); ?></span>
				<?php endif; ?>
			</p>
			<p class="tf-falle" aria-hidden="true">
				<label for="<?php echo esc_attr( $id . '-webseite' ); ?>"><?php esc_html_e( 'Dieses Feld bitte leer lassen', 'tamil-site' ); ?></label>
				<input type="text" id="<?php echo esc_attr( $id . '-webseite' ); ?>" name="tf_webseite" value="" tabindex="-1" autocomplete="off">
			</p>
			<input type="hidden" name="tf_art" value="<?php echo esc_attr( $art ); ?>">
			<input type="hidden" name="tf_zeit" value="<?php echo esc_attr( tamil_site_einsendung_zeitstempel() ); ?>">
			<input type="hidden" name="tf_fassung" value="<?php echo esc_attr( $einwilligung['fassung'] ); ?>">
			<input type="hidden" name="tf_nonce" value="<?php echo esc_attr( wp_create_nonce( 'tamil_einsendung_' . $art ) ); ?>">
			<p class="tf-aktion"><button type="submit" class="tf-senden"><?php esc_html_e( 'Absenden', 'tamil-site' ); ?></button></p>
		</form>
	</div>
	<?php
}

/**
 * Ein Feld mit Beschriftung, Hilfe und Fehler.
 *
 * @param string                                                         $id     Formular-ID.
 * @param string                                                         $key    Feldname.
 * @param array{label:string,typ:string,pflicht:bool,max:int,hilfe?:string} $feld Felddefinition.
 * @param string                                                         $wert   Wert.
 * @param string                                                         $fehler Fehlermeldung.
 */
function tamil_site_einsendung_feld( string $id, string $key, array $feld, string $wert, string $fehler ): void {
	$fid   = $id . '-' . str_replace( '_', '-', $key );
	$name  = 'tf[' . $key . ']';
	$descr = array();
	if ( ! empty( $feld['hilfe'] ) ) {
		$descr[] = $fid . '-hilfe';
	}
	if ( '' !== $fehler ) {
		$descr[] = $fid . '-fehler';
	}
	$attr = ' id="' . esc_attr( $fid ) . '" name="' . esc_attr( $name ) . '"';
	if ( $feld['pflicht'] ) {
		$attr .= ' required';
	}
	if ( $descr ) {
		$attr .= ' aria-describedby="' . esc_attr( implode( ' ', $descr ) ) . '"';
	}
	if ( '' !== $fehler ) {
		$attr .= ' aria-invalid="true"';
	}
	$auto = array(
		'name'    => 'name',
		'email'   => 'email',
		'telefon' => 'tel',
	);
	if ( isset( $auto[ $key ] ) ) {
		$attr .= ' autocomplete="' . esc_attr( $auto[ $key ] ) . '"';
	}
	if ( 'datetime' === $feld['typ'] && '' !== $wert ) {
		$zeit = date_create_immutable( $wert );
		$wert = $zeit ? $zeit->setTimezone( wp_timezone() )->format( 'Y-m-d\TH:i' ) : '';
	}
	?>
	<p class="tf-feld">
		<label for="<?php echo esc_attr( $fid ); ?>"><?php echo esc_html( $feld['label'] ) . ( $feld['pflicht'] ? ' <span class="tf-pflicht">' . esc_html__( '(Pflicht)', 'tamil-site' ) . '</span>' : '' ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- beide Teile escapt ?></label>
		<?php
		switch ( $feld['typ'] ) {
			case 'textarea':
				echo '<textarea' . $attr . ' rows="6" maxlength="' . esc_attr( (string) $feld['max'] ) . '">' . esc_textarea( $wert ) . '</textarea>'; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- $attr ist aus escapten Teilen gebaut
				break;
			case 'land':
				echo '<select' . $attr . '><option value="">' . esc_html__( 'Bitte wählen', 'tamil-site' ) . '</option>'; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- $attr ist aus escapten Teilen gebaut
				foreach ( tamil_site_einsendung_laender() as $code => $land ) {
					echo '<option value="' . esc_attr( $code ) . '"' . selected( $wert, $code, false ) . '>' . esc_html( $land ) . '</option>';
				}
				echo '</select>';
				break;
			default:
				$typ    = array(
					'datetime' => 'datetime-local',
					'email'    => 'email',
					'tel'      => 'tel',
					'url'      => 'url',
				)[ $feld['typ'] ] ?? 'text';
				$laenge = 'datetime-local' === $typ ? '' : ' maxlength="' . esc_attr( (string) $feld['max'] ) . '"';
				echo '<input type="' . esc_attr( $typ ) . '"' . $attr . $laenge . ' value="' . esc_attr( $wert ) . '">'; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- $attr ist aus escapten Teilen gebaut
		}
		?>
		<?php if ( ! empty( $feld['hilfe'] ) ) : ?>
		<span class="tf-hilfe" id="<?php echo esc_attr( $fid . '-hilfe' ); ?>"><?php echo esc_html( $feld['hilfe'] ); ?></span>
		<?php endif; ?>
		<?php if ( '' !== $fehler ) : ?>
		<span class="tf-fehler" id="<?php echo esc_attr( $fid . '-fehler' ); ?>"><?php echo esc_html( $fehler ); ?></span>
		<?php endif; ?>
	</p>
	<?php
}
