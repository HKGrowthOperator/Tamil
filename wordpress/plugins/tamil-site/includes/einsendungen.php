<?php
/**
 * Einsendungen (Festlegung F1): Speicherung, Status, Bilder, Löschfrist und Protokoll.
 *
 * Formulare: includes/einsendungen-formular.php · Notfall-Liste in wp-admin: includes/einsendungen-admin.php ·
 * Abholen durch den Radar: Plugin tamil-radar, includes/einsendungen.php (REST). WordPress ruft den Radar nie auf und
 * verschickt keine E-Mail.
 *
 * Daten (docs/spezifikation/datenmodell.md §12): eine eigene Tabelle, nicht öffentlich; Bilder in einem eigenen
 * Ordner unter uploads/ mit zufälligem Namen und Sperre für den Webserver. Löschung 90 Tage nach Abschluss
 * (übernommen, erledigt, abgelehnt), Spam nach 7 Tagen, nie abgeschlossene Einsendungen 90 Tage nach Eingang
 * (Höchstfrist), IP-Hash nach 24 Stunden. Das Protokoll enthält keine Namen
 * oder Kontaktdaten, nur Vorgangsnummer, Aktion und wer (Benutzername, „website“ oder „cron“); Frist 12 Monate (F0).
 */

defined( 'ABSPATH' ) || exit;

/** Löschfrist nach Abschluss (übernommen, erledigt, abgelehnt), in Tagen. */
define( 'TAMIL_SITE_EINSENDUNG_FRIST_TAGE', 90 );
/** Höchstfrist für nie abgeschlossene Einsendungen, in Tagen nach Eingang. */
define( 'TAMIL_SITE_EINSENDUNG_HOECHST_TAGE', 90 );
/** Löschfrist für Spam, in Tagen. */
define( 'TAMIL_SITE_EINSENDUNG_SPAM_TAGE', 7 );
/** So lange bleibt der IP-Hash (nur für die Drossel), in Stunden. */
define( 'TAMIL_SITE_EINSENDUNG_IP_STUNDEN', 24 );
/** Frist für das Protokoll, in Monaten (F0). */
define( 'TAMIL_SITE_EINSENDUNG_PROTOKOLL_MONATE', 12 );

/**
 * Formulararten → Beschriftung.
 *
 * @return array<string,string>
 */
function tamil_site_einsendung_arten(): array {
	return array(
		'event'       => __( 'Event einreichen', 'tamil-site' ),
		'beitrag'     => __( 'Beitrag oder Thema vorschlagen', 'tamil-site' ),
		'kooperation' => __( 'Kooperation', 'tamil-site' ),
		'werbung'     => __( 'Werbeanfrage', 'tamil-site' ),
		'kontakt'     => __( 'Kontakt', 'tamil-site' ),
	);
}

/**
 * Status → Beschriftung. „vorbereitet“ führt nur der Radar.
 *
 * @return array<string,string>
 */
function tamil_site_einsendung_status_liste(): array {
	return array(
		'eingegangen' => __( 'eingegangen', 'tamil-site' ),
		'abgeholt'    => __( 'abgeholt', 'tamil-site' ),
		'uebernommen' => __( 'übernommen', 'tamil-site' ),
		'erledigt'    => __( 'erledigt', 'tamil-site' ),
		'abgelehnt'   => __( 'abgelehnt', 'tamil-site' ),
		'spam'        => __( 'Spam', 'tamil-site' ),
	);
}

/**
 * Abschließende Status (setzen abgeschlossen_at, Beginn der Löschfrist).
 *
 * @return array<int,string>
 */
function tamil_site_einsendung_status_abschluss(): array {
	return array( 'uebernommen', 'erledigt', 'abgelehnt', 'spam' );
}

function tamil_site_einsendung_tabelle(): string {
	global $wpdb;
	return $wpdb->prefix . 'tamil_einsendungen';
}

function tamil_site_einsendung_protokoll_tabelle(): string {
	global $wpdb;
	return $wpdb->prefix . 'tamil_einsendungen_protokoll';
}

/**
 * Upgrade-Schritt (Datenversion 2): beide Tabellen über dbDelta, Bildordner mit Sperre. Idempotent.
 */
function tamil_site_einsendungen_tabellen(): void {
	global $wpdb;
	require_once ABSPATH . 'wp-admin/includes/upgrade.php';
	$charset = $wpdb->get_charset_collate();
	$t       = tamil_site_einsendung_tabelle();
	$p       = tamil_site_einsendung_protokoll_tabelle();
	dbDelta(
		"CREATE TABLE {$t} (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  vorgangsnummer varchar(20) NOT NULL,
  art varchar(20) NOT NULL,
  status varchar(20) NOT NULL DEFAULT 'eingegangen',
  eingang_at datetime NOT NULL,
  abgeholt_at datetime DEFAULT NULL,
  abgeschlossen_at datetime DEFAULT NULL,
  name varchar(200) NOT NULL,
  email varchar(200) NOT NULL,
  telefon varchar(40) NOT NULL DEFAULT '',
  felder longtext NOT NULL,
  einwilligung tinyint(1) NOT NULL DEFAULT 0,
  einwilligung_fassung varchar(40) NOT NULL DEFAULT '',
  bild_datei varchar(80) NOT NULL DEFAULT '',
  bild_typ varchar(20) NOT NULL DEFAULT '',
  bild_groesse int(10) unsigned NOT NULL DEFAULT 0,
  bild_sha256 varchar(64) NOT NULL DEFAULT '',
  bild_recht_bestaetigt tinyint(1) NOT NULL DEFAULT 0,
  ip_hash varchar(64) DEFAULT NULL,
  PRIMARY KEY  (id),
  UNIQUE KEY vorgangsnummer (vorgangsnummer),
  KEY status_abschluss (status,abgeschlossen_at),
  KEY ip_eingang (ip_hash,eingang_at)
) {$charset};"
	);
	dbDelta(
		"CREATE TABLE {$p} (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  ts datetime NOT NULL,
  wer varchar(60) NOT NULL,
  aktion varchar(30) NOT NULL,
  vorgangsnummer varchar(20) NOT NULL DEFAULT '',
  notiz varchar(300) NOT NULL DEFAULT '',
  PRIMARY KEY  (id),
  KEY ts (ts)
) {$charset};"
	);
	foreach ( array( $t, $p ) as $tabelle ) {
		// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- Prüfung nach dbDelta
		if ( $wpdb->get_var( $wpdb->prepare( 'SHOW TABLES LIKE %s', $tabelle ) ) !== $tabelle ) {
			throw new RuntimeException( 'Tabelle ' . esc_html( $tabelle ) . ' fehlt nach dbDelta.' );
		}
	}
	tamil_site_einsendung_bildordner();
}

// Anmeldung bei der Upgrade-Routine (includes/upgrade.php): Tabellen ab Datenversion 2, Recht für die Rolle „radar“.
tamil_site_upgrade_schritt( 2, 'einsendungen', 'tamil_site_einsendungen_tabellen' );
tamil_site_rechte_anmelden( 'radar', array( 'tamil_einsendungen_abholen' ) );

/**
 * Ordner für eingesandte Bilder (angelegt, mit Sperre für Apache und leerer index.php).
 *
 * @return string Pfad mit abschließendem Schrägstrich.
 */
function tamil_site_einsendung_bildordner(): string {
	$basis  = defined( 'TAMIL_SITE_EINSENDUNG_ORDNER' ) ? (string) TAMIL_SITE_EINSENDUNG_ORDNER : wp_upload_dir( null, false )['basedir'] . '/tamil-einsendungen';
	$ordner = trailingslashit( $basis );
	if ( ! is_dir( $ordner ) && ! wp_mkdir_p( $ordner ) ) {
		throw new RuntimeException( 'Bildordner für Einsendungen nicht anlegbar.' );
	}
	$dateien = array(
		'.htaccess' => "Require all denied\n",
		'index.php' => "<?php\n// Stille.\n",
	);
	foreach ( $dateien as $name => $inhalt ) {
		if ( ! file_exists( $ordner . $name ) ) {
			// phpcs:ignore WordPress.WP.AlternativeFunctions.file_system_operations_file_put_contents -- kleine Schutzdatei
			file_put_contents( $ordner . $name, $inhalt );
		}
	}
	return $ordner;
}

/**
 * Jetzt in UTC im Datenbankformat.
 */
function tamil_site_einsendung_jetzt(): string {
	return gmdate( 'Y-m-d H:i:s' );
}

/**
 * Datenbankzeit (UTC) → ISO 8601, leer bei NULL.
 *
 * @param string|null $wert Datenbankwert.
 */
function tamil_site_einsendung_iso( ?string $wert ): ?string {
	if ( null === $wert || '' === $wert ) {
		return null;
	}
	return gmdate( 'c', (int) strtotime( $wert . ' UTC' ) );
}

/**
 * Protokollzeile ohne Personendaten.
 *
 * @param string $aktion  z. B. eingang, status, bild_abgerufen, geloescht, loeschfrist.
 * @param string $vorgang Vorgangsnummer oder leer.
 * @param string $notiz   Kurzer Grund oder Zähler, keine Inhalte.
 * @param string $wer     Benutzername, „website“ oder „cron“; leer = aktueller Benutzer.
 */
function tamil_site_einsendung_protokoll( string $aktion, string $vorgang = '', string $notiz = '', string $wer = '' ): void {
	global $wpdb;
	if ( '' === $wer ) {
		$wer = is_user_logged_in() ? wp_get_current_user()->user_login : 'website';
	}
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery -- eigene Tabelle
	$wpdb->insert(
		tamil_site_einsendung_protokoll_tabelle(),
		array(
			'ts'             => tamil_site_einsendung_jetzt(),
			'wer'            => substr( $wer, 0, 60 ),
			'aktion'         => substr( $aktion, 0, 30 ),
			'vorgangsnummer' => substr( $vorgang, 0, 20 ),
			'notiz'          => substr( $notiz, 0, 300 ),
		)
	);
}

/**
 * Neue Vorgangsnummer, z. B. T261113-K7M3Q (Datum + fünf Zeichen ohne Verwechsler).
 */
function tamil_site_einsendung_vorgangsnummer_neu(): string {
	$zeichen = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
	$teil    = '';
	for ( $i = 0; $i < 5; $i++ ) {
		$teil .= $zeichen[ random_int( 0, strlen( $zeichen ) - 1 ) ];
	}
	return 'T' . gmdate( 'ymd' ) . '-' . $teil;
}

/**
 * Hat die Zeichenkette die Form einer Vorgangsnummer?
 */
function tamil_site_einsendung_vorgangsnummer_gueltig( string $wert ): bool {
	return (bool) preg_match( '/^T\d{6}-[A-HJ-NP-Z2-9]{5}$/', $wert );
}

/**
 * Speichert eine geprüfte Einsendung. Die Vorgangsnummer wird bei Kollision neu gezogen.
 *
 * Drossel ohne Rennen: erst einfügen, dann zählen. Liegen mit dieser Zeile mehr als $drossel Einsendungen desselben
 * IP-Hashes in der letzten Stunde vor (gezählt bis zur eigenen id, damit bei gleichzeitigen Aufrufen die früheren
 * gewinnen), wird die Zeile wieder gelöscht und die Einsendung abgelehnt.
 *
 * @param array<string,mixed> $daten   art, name, email, telefon, felder (array), einwilligung_fassung, bild (array|null),
 *                                     bild_recht_bestaetigt, ip_hash.
 * @param int                 $drossel Höchstzahl je Stunde und IP-Hash (0 = keine Drossel).
 * @return string|WP_Error Vorgangsnummer.
 */
function tamil_site_einsendung_speichern( array $daten, int $drossel = 0 ) {
	global $wpdb;
	$bild  = is_array( $daten['bild'] ?? null ) ? $daten['bild'] : null;
	$zeile = array(
		'art'                   => (string) $daten['art'],
		'status'                => 'eingegangen',
		'eingang_at'            => tamil_site_einsendung_jetzt(),
		'name'                  => (string) $daten['name'],
		'email'                 => (string) $daten['email'],
		'telefon'               => (string) ( $daten['telefon'] ?? '' ),
		'felder'                => (string) wp_json_encode( (array) ( $daten['felder'] ?? array() ) ),
		'einwilligung'          => 1,
		'einwilligung_fassung'  => (string) $daten['einwilligung_fassung'],
		'bild_datei'            => $bild ? (string) $bild['datei'] : '',
		'bild_typ'              => $bild ? (string) $bild['typ'] : '',
		'bild_groesse'          => $bild ? (int) $bild['groesse'] : 0,
		'bild_sha256'           => $bild ? (string) $bild['sha256'] : '',
		'bild_recht_bestaetigt' => $bild && ! empty( $daten['bild_recht_bestaetigt'] ) ? 1 : 0,
		'ip_hash'               => (string) ( $daten['ip_hash'] ?? '' ),
	);
	for ( $versuch = 0; $versuch < 5; $versuch++ ) {
		$zeile['vorgangsnummer'] = tamil_site_einsendung_vorgangsnummer_neu();
		$wpdb->suppress_errors( true );
		// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery -- eigene Tabelle
		$ok = $wpdb->insert( tamil_site_einsendung_tabelle(), $zeile );
		$wpdb->suppress_errors( false );
		if ( $ok ) {
			$id = (int) $wpdb->insert_id;
			if ( $drossel > 0 && tamil_site_einsendung_drossel_bis( $zeile['ip_hash'], $id ) > $drossel ) {
				// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- eigene Tabelle
				$wpdb->delete( tamil_site_einsendung_tabelle(), array( 'id' => $id ) );
				return new WP_Error( 'tamil_einsendung_drossel', __( 'Zu viele Einsendungen in der letzten Stunde.', 'tamil-site' ) );
			}
			tamil_site_einsendung_protokoll( 'eingang', $zeile['vorgangsnummer'], $zeile['art'], 'website' );
			return $zeile['vorgangsnummer'];
		}
	}
	return new WP_Error( 'tamil_einsendung_speichern', __( 'Die Einsendung konnte nicht gespeichert werden.', 'tamil-site' ) );
}

/**
 * Einsendungen desselben IP-Hashes in der letzten Stunde bis einschließlich id $bis.
 */
function tamil_site_einsendung_drossel_bis( string $ip_hash, int $bis ): int {
	global $wpdb;
	$t = tamil_site_einsendung_tabelle();
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- eigene Tabelle
	return (int) $wpdb->get_var( $wpdb->prepare( "SELECT COUNT(*) FROM {$t} WHERE ip_hash = %s AND eingang_at >= %s AND id <= %d", $ip_hash, gmdate( 'Y-m-d H:i:s', time() - HOUR_IN_SECONDS ), $bis ) );
}

/**
 * Rohzeile zu einer Vorgangsnummer.
 *
 * @return array<string,mixed>|null
 */
function tamil_site_einsendung_zeile( string $vorgang ): ?array {
	global $wpdb;
	$t = tamil_site_einsendung_tabelle();
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- eigene Tabelle, Name aus dem Präfix
	$zeile = $wpdb->get_row( $wpdb->prepare( "SELECT * FROM {$t} WHERE vorgangsnummer = %s", $vorgang ), ARRAY_A );
	return is_array( $zeile ) ? $zeile : null;
}

/**
 * Darstellung für REST und Admin-Liste (ohne IP-Hash und Dateinamen).
 *
 * @param array<string,mixed> $z Rohzeile.
 * @return array<string,mixed>
 */
function tamil_site_einsendung_ausgabe( array $z ): array {
	$felder = json_decode( (string) $z['felder'], true );
	return array(
		'id'                   => (int) $z['id'],
		'vorgangsnummer'       => (string) $z['vorgangsnummer'],
		'art'                  => (string) $z['art'],
		'status'               => (string) $z['status'],
		'eingang_at'           => tamil_site_einsendung_iso( $z['eingang_at'] ),
		'abgeholt_at'          => tamil_site_einsendung_iso( $z['abgeholt_at'] ),
		'abgeschlossen_at'     => tamil_site_einsendung_iso( $z['abgeschlossen_at'] ),
		'name'                 => (string) $z['name'],
		'email'                => (string) $z['email'],
		'telefon'              => (string) $z['telefon'],
		'einwilligung'         => (bool) $z['einwilligung'],
		'einwilligung_fassung' => (string) $z['einwilligung_fassung'],
		'felder'               => is_array( $felder ) ? $felder : array(),
		'bild'                 => '' === (string) $z['bild_datei'] ? null : array(
			'typ'              => (string) $z['bild_typ'],
			'groesse'          => (int) $z['bild_groesse'],
			'sha256'           => (string) $z['bild_sha256'],
			'recht_bestaetigt' => (bool) $z['bild_recht_bestaetigt'],
		),
	);
}

/**
 * Einsendungen nach einem Cursor (id), aufsteigend.
 *
 * @param int $nach   Nur Einsendungen mit größerer id.
 * @param int $anzahl Höchstens so viele (1–100).
 * @return array{einsendungen:array<int,array<string,mixed>>,weiter:int,mehr:bool}
 */
function tamil_site_einsendung_liste( int $nach, int $anzahl ): array {
	global $wpdb;
	$t      = tamil_site_einsendung_tabelle();
	$anzahl = max( 1, min( 100, $anzahl ) );
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- eigene Tabelle
	$zeilen = (array) $wpdb->get_results( $wpdb->prepare( "SELECT * FROM {$t} WHERE id > %d ORDER BY id ASC LIMIT %d", max( 0, $nach ), $anzahl + 1 ), ARRAY_A );
	$mehr   = count( $zeilen ) > $anzahl;
	$zeilen = array_slice( $zeilen, 0, $anzahl );
	$aus    = array_map( 'tamil_site_einsendung_ausgabe', $zeilen );
	return array(
		'einsendungen' => $aus,
		'weiter'       => $aus ? (int) end( $aus )['id'] : max( 0, $nach ),
		'mehr'         => $mehr,
	);
}

/**
 * Erlaubte Übergänge auf der Website: eingegangen → abgeholt; eingegangen/abgeholt → ein Abschluss.
 * Ein Abschluss ist endgültig (die Löschfrist läuft); derselbe Status noch einmal ist ohne Wirkung.
 *
 * @return array<string,array<int,string>> Zielstatus → erlaubte Ausgangsstatus.
 */
function tamil_site_einsendung_uebergaenge(): array {
	$offen = array( 'eingegangen', 'abgeholt' );
	return array(
		'abgeholt'    => array( 'eingegangen' ),
		'uebernommen' => $offen,
		'erledigt'    => $offen,
		'abgelehnt'   => $offen,
		'spam'        => $offen,
	);
}

/**
 * Status setzen. Prüfung und Schreiben sind eine bedingte Anweisung (kein Rennen zwischen Lesen und Schreiben).
 *
 * @return array<string,mixed>|WP_Error Neue Darstellung.
 */
function tamil_site_einsendung_status_setzen( string $vorgang, string $neu ) {
	global $wpdb;
	$uebergaenge = tamil_site_einsendung_uebergaenge();
	if ( ! isset( $uebergaenge[ $neu ] ) ) {
		return new WP_Error( 'tamil_einsendung_status', __( 'Unbekannter Status.', 'tamil-site' ), array( 'status' => 400 ) );
	}
	$t     = tamil_site_einsendung_tabelle();
	$von   = $uebergaenge[ $neu ];
	$jetzt = tamil_site_einsendung_jetzt();
	$platz = implode( ',', array_fill( 0, count( $von ), '%s' ) );
	if ( 'abgeholt' === $neu ) {
		$set = 'status = %s, abgeholt_at = %s';
	} else {
		$set = 'status = %s, abgeschlossen_at = %s';
	}
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.PreparedSQL.InterpolatedNotPrepared, WordPress.DB.PreparedSQLPlaceholders.UnfinishedPrepare -- eigene Tabelle, Platzhalter für die Ausgangsstatus
	$geaendert = $wpdb->query( $wpdb->prepare( "UPDATE {$t} SET {$set} WHERE vorgangsnummer = %s AND status IN ({$platz})", array_merge( array( $neu, $jetzt, $vorgang ), $von ) ) );
	if ( false === $geaendert ) {
		return new WP_Error( 'tamil_einsendung_db', __( 'Der Status konnte nicht gespeichert werden.', 'tamil-site' ), array( 'status' => 500 ) );
	}
	$zeile = tamil_site_einsendung_zeile( $vorgang );
	if ( ! $zeile ) {
		return new WP_Error( 'tamil_einsendung_fehlt', __( 'Einsendung nicht gefunden.', 'tamil-site' ), array( 'status' => 404 ) );
	}
	if ( (int) $geaendert > 0 ) {
		tamil_site_einsendung_protokoll( 'status', $vorgang, 'nach=' . $neu );
		return tamil_site_einsendung_ausgabe( $zeile );
	}
	if ( $zeile['status'] === $neu || ( 'abgeholt' === $neu && 'eingegangen' !== $zeile['status'] ) ) {
		return tamil_site_einsendung_ausgabe( $zeile ); // schon so (oder schon weiter): ohne Wirkung
	}
	return new WP_Error(
		'tamil_einsendung_abgeschlossen',
		__( 'Die Einsendung ist bereits abgeschlossen.', 'tamil-site' ),
		array(
			'status'      => 409,
			'aktuell'     => (string) $zeile['status'],
			'angefordert' => $neu,
		)
	);
}

/**
 * Bild einer Einsendung (Inhalt und Angaben) oder null.
 *
 * @return array{typ:string,groesse:int,sha256:string,daten:string}|null
 */
function tamil_site_einsendung_bild( string $vorgang ): ?array {
	$zeile = tamil_site_einsendung_zeile( $vorgang );
	if ( ! $zeile || '' === (string) $zeile['bild_datei'] ) {
		return null;
	}
	$pfad = tamil_site_einsendung_bildordner() . basename( (string) $zeile['bild_datei'] );
	if ( ! is_file( $pfad ) ) {
		return null;
	}
	// phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents -- lokale Datei
	$daten = (string) file_get_contents( $pfad );
	return array(
		'typ'     => (string) $zeile['bild_typ'],
		'groesse' => strlen( $daten ),
		'sha256'  => hash( 'sha256', $daten ),
		'daten'   => $daten,
	);
}

/**
 * Löschfrist: abgeschlossene Einsendungen nach 90 Tagen, Spam nach 7 Tagen, nie abgeschlossene 90 Tage nach Eingang
 * (jeweils mit Bild), IP-Hash nach 24 Stunden, Protokoll nach 12 Monaten. Schreibt je gelöschter Einsendung und für
 * den Lauf eine Protokollzeile.
 *
 * @param int|null $jetzt Zeitpunkt (Unix, für Tests).
 * @return array{geloescht:int,spam:int,offen:int,ip_hash:int,protokoll:int}
 */
function tamil_site_einsendungen_aufraeumen( ?int $jetzt = null ): array {
	global $wpdb;
	$jetzt   = $jetzt ?? time();
	$t       = tamil_site_einsendung_tabelle();
	$p       = tamil_site_einsendung_protokoll_tabelle();
	$grenze  = gmdate( 'Y-m-d H:i:s', $jetzt - TAMIL_SITE_EINSENDUNG_FRIST_TAGE * DAY_IN_SECONDS );
	$spam    = gmdate( 'Y-m-d H:i:s', $jetzt - TAMIL_SITE_EINSENDUNG_SPAM_TAGE * DAY_IN_SECONDS );
	$hoechst = gmdate( 'Y-m-d H:i:s', $jetzt - TAMIL_SITE_EINSENDUNG_HOECHST_TAGE * DAY_IN_SECONDS );
	$ip      = gmdate( 'Y-m-d H:i:s', $jetzt - TAMIL_SITE_EINSENDUNG_IP_STUNDEN * HOUR_IN_SECONDS );
	$prot    = gmdate( 'Y-m-d H:i:s', strtotime( '-' . TAMIL_SITE_EINSENDUNG_PROTOKOLL_MONATE . ' months', $jetzt ) );
	$zaehler = array(
		'geloescht' => 0,
		'spam'      => 0,
		'offen'     => 0,
		'ip_hash'   => 0,
		'protokoll' => 0,
	);
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- eigene Tabelle
	$faellig = (array) $wpdb->get_results( $wpdb->prepare( "SELECT id, vorgangsnummer, status, bild_datei FROM {$t} WHERE ( status IN ('uebernommen','erledigt','abgelehnt') AND abgeschlossen_at < %s ) OR ( status = 'spam' AND abgeschlossen_at < %s ) OR ( status IN ('eingegangen','abgeholt') AND eingang_at < %s )", $grenze, $spam, $hoechst ), ARRAY_A );
	foreach ( $faellig as $z ) {
		if ( '' !== (string) $z['bild_datei'] ) {
			$pfad = tamil_site_einsendung_bildordner() . basename( (string) $z['bild_datei'] );
			if ( is_file( $pfad ) ) {
				wp_delete_file( $pfad );
			}
		}
		// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- eigene Tabelle
		if ( $wpdb->delete( $t, array( 'id' => (int) $z['id'] ) ) ) {
			$offen = in_array( $z['status'], array( 'eingegangen', 'abgeholt' ), true );
			++$zaehler[ $offen ? 'offen' : ( 'spam' === $z['status'] ? 'spam' : 'geloescht' ) ];
			tamil_site_einsendung_protokoll( 'geloescht', (string) $z['vorgangsnummer'], ( $offen ? 'Hoechstfrist ' : 'Frist ' ) . $z['status'], 'cron' );
		}
	}
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- eigene Tabelle
	$zaehler['ip_hash'] = (int) $wpdb->query( $wpdb->prepare( "UPDATE {$t} SET ip_hash = NULL WHERE ip_hash IS NOT NULL AND eingang_at < %s", $ip ) );
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- eigene Tabelle
	$zaehler['protokoll'] = (int) $wpdb->query( $wpdb->prepare( "DELETE FROM {$p} WHERE ts < %s", $prot ) );
	tamil_site_einsendung_protokoll(
		'loeschfrist',
		'',
		sprintf( 'geloescht=%d spam=%d offen=%d ip_hash=%d protokoll=%d', $zaehler['geloescht'], $zaehler['spam'], $zaehler['offen'], $zaehler['ip_hash'], $zaehler['protokoll'] ),
		'cron'
	);
	return $zaehler;
}

/**
 * WP-Cron: stündlich (der IP-Hash hat eine Frist von 24 Stunden). Läuft unabhängig vom Funktionsschalter, damit
 * Fristen auch nach dem Ausschalten eingehalten werden. Nur wenn die Tabellen schon angelegt sind.
 */
function tamil_site_einsendungen_cron_planen(): void {
	if ( tamil_site_datenversion() < 2 ) {
		return;
	}
	if ( ! wp_next_scheduled( 'tamil_site_einsendungen_aufraeumen' ) ) {
		wp_schedule_event( time() + 300, 'hourly', 'tamil_site_einsendungen_aufraeumen' );
	}
}
add_action( 'init', 'tamil_site_einsendungen_cron_planen', 30 );
add_action(
	'tamil_site_einsendungen_aufraeumen',
	static function (): void {
		tamil_site_einsendungen_aufraeumen();
	}
);
