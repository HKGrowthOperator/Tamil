<?php
/**
 * Werbebuchung (Festlegung F3, Datenmodell §14): Angebote, Tabellen, Reservierung, Stand, Aktiv-Funktion, Ausliefern.
 *
 * Grundsätze:
 * - „Aktiv“ entscheidet genau eine Funktion: tamil_site_werbung_aktiv(). Alle Auslieferungen fragen nur sie.
 * - Keine Doppelbuchung: je Platz und Tag höchstens eine Zeile in tamil_werbetage (Primärschlüssel platz+tag). Die Tage
 *   werden einzeln und aufsteigend belegt; scheitert ein Tag, gibt die Buchung alle ihre Tage wieder frei.
 * - Zustandswechsel sind bedingte UPDATEs (WHERE alter Stand): Wer zuerst kommt, gewinnt; Wiederholungen ändern nichts.
 * - Start, Wechsel und Ende folgen allein aus dem Datum; abgelaufene Reservierungen räumt der nächste Aufruf ab, der
 *   Verfügbarkeit braucht (kein Zeitdienst).
 * - Preise kommen von KBS und stehen nur in der Datenbank (Menü Werbung → Angebote); ohne Preis heißt es „Preis folgt“
 *   und der Platz ist nicht buchbar.
 * - Alles Öffentliche hängt am Funktionsschalter „werbung“ (Standard aus).
 */

defined( 'ABSPATH' ) || exit;

// phpcs:disable WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- eigene Tabellen; Zustände und Belegung dürfen nie aus einem Cache kommen

/**
 * Minuten, die gewählte Tage während der Zahlung reserviert bleiben (F3).
 */
define( 'TAMIL_SITE_WERBUNG_RESERVIERUNG_MINUTEN', 35 );

/**
 * Größte Datei für ein Werbemittel in Bytes.
 */
define( 'TAMIL_SITE_WERBUNG_MAX_BYTES', 500 * 1024 );

/**
 * So viele Tage im Voraus kann gebucht werden.
 */
define( 'TAMIL_SITE_WERBUNG_HORIZONT_TAGE', 365 );

/**
 * Höchstens so viele offene (reservierte, unbezahlte) Buchungen zugleich, über alle Besucher.
 */
define( 'TAMIL_SITE_WERBUNG_MAX_OFFEN', 20 );

/**
 * Höchstens so viele Reservierungen je Verbindung (IP-Hash) in einer Stunde.
 */
define( 'TAMIL_SITE_WERBUNG_DROSSEL', 5 );

/**
 * Nach so vielen Tagen werden die Personendaten nie bezahlter Buchungen geleert.
 */
define( 'TAMIL_SITE_WERBUNG_FRIST_UNBEZAHLT_TAGE', 30 );

/**
 * Tabellenname.
 *
 * @param string $name buchungen, tage, statistik, protokoll, ereignisse.
 */
function tamil_site_werbung_tabelle( string $name ): string {
	global $wpdb;
	$namen = array(
		'buchungen'  => 'tamil_werbebuchungen',
		'tage'       => 'tamil_werbetage',
		'statistik'  => 'tamil_werbestatistik',
		'protokoll'  => 'tamil_werbeprotokoll',
		'ereignisse' => 'tamil_stripe_ereignisse',
	);
	return $wpdb->prefix . $namen[ $name ];
}

/**
 * Tabellen anlegen oder angleichen (Upgrade-Schritt, idempotent) und die Seite „Werben“ als Entwurf anlegen.
 */
function tamil_site_werbung_tabellen(): void {
	global $wpdb;
	require_once ABSPATH . 'wp-admin/includes/upgrade.php';
	$c = $wpdb->get_charset_collate();
	$b = tamil_site_werbung_tabelle( 'buchungen' );
	$t = tamil_site_werbung_tabelle( 'tage' );
	$s = tamil_site_werbung_tabelle( 'statistik' );
	$p = tamil_site_werbung_tabelle( 'protokoll' );
	$e = tamil_site_werbung_tabelle( 'ereignisse' );
	dbDelta(
		"CREATE TABLE {$b} (
 id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
 nummer varchar(20) NOT NULL,
 platz varchar(20) NOT NULL,
 laufzeit smallint(5) unsigned NOT NULL,
 start date NOT NULL,
 ende date NOT NULL,
 reserviert_bis datetime NOT NULL,
 firma varchar(200) NOT NULL DEFAULT '',
 ansprechperson varchar(200) NOT NULL DEFAULT '',
 rechnungsadresse text NOT NULL,
 email varchar(200) NOT NULL DEFAULT '',
 telefon varchar(60) NOT NULL DEFAULT '',
 ust_id varchar(40) NOT NULL DEFAULT '',
 werbemittel_desktop varchar(255) NOT NULL DEFAULT '',
 werbemittel_mobil varchar(255) NOT NULL DEFAULT '',
 ziel_url varchar(500) NOT NULL DEFAULT '',
 betrag int(10) unsigned NOT NULL DEFAULT 0,
 waehrung char(3) NOT NULL DEFAULT 'eur',
 bedingungen_fassung varchar(60) NOT NULL DEFAULT '',
 bedingungen_at datetime DEFAULT NULL,
 stripe_session varchar(255) NOT NULL DEFAULT '',
 stripe_zahlung varchar(255) NOT NULL DEFAULT '',
 beleg_url varchar(500) NOT NULL DEFAULT '',
 zahlung varchar(20) NOT NULL DEFAULT 'offen',
 pruefung varchar(20) NOT NULL DEFAULT 'offen',
 ablehnungsgrund text NOT NULL,
 pausiert tinyint(1) NOT NULL DEFAULT 0,
 beendet_at datetime DEFAULT NULL,
 kunden_hash char(64) NOT NULL DEFAULT '',
 warnung text NOT NULL,
 erstellt_at datetime NOT NULL,
 PRIMARY KEY  (id),
 UNIQUE KEY nummer (nummer),
 KEY kunden_hash (kunden_hash),
 KEY zahlung (zahlung)
) {$c};
CREATE TABLE {$t} (
 platz varchar(20) NOT NULL,
 tag date NOT NULL,
 buchung_id bigint(20) unsigned NOT NULL,
 PRIMARY KEY  (platz,tag),
 KEY buchung_id (buchung_id)
) {$c};
CREATE TABLE {$s} (
 buchung_id bigint(20) unsigned NOT NULL,
 tag date NOT NULL,
 einblendungen int(10) unsigned NOT NULL DEFAULT 0,
 klicks int(10) unsigned NOT NULL DEFAULT 0,
 PRIMARY KEY  (buchung_id,tag)
) {$c};
CREATE TABLE {$p} (
 id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
 buchung_id bigint(20) unsigned NOT NULL,
 zeit datetime NOT NULL,
 wer varchar(60) NOT NULL DEFAULT '',
 was varchar(255) NOT NULL DEFAULT '',
 PRIMARY KEY  (id),
 KEY buchung_id (buchung_id)
) {$c};
CREATE TABLE {$e} (
 ereignis_id varchar(255) NOT NULL,
 typ varchar(80) NOT NULL DEFAULT '',
 empfangen_at datetime NOT NULL,
 PRIMARY KEY  (ereignis_id)
) {$c};"
	);
	foreach ( array( $b, $t, $s, $p, $e ) as $tabelle ) {
		if ( $wpdb->get_var( $wpdb->prepare( 'SHOW TABLES LIKE %s', $tabelle ) ) !== $tabelle ) {
			throw new RuntimeException( 'Tabelle ' . esc_html( $tabelle ) . ' fehlt nach dbDelta' );
		}
	}
	// Seite „Werben“: Entwurf mit dem Shortcode; veröffentlicht wird sie, wenn der Schalter im Echtbetrieb an ist.
	if ( ! get_page_by_path( 'werben', OBJECT, 'page' ) ) {
		$id = wp_insert_post(
			array(
				'post_type'    => 'page',
				'post_status'  => 'draft',
				'post_title'   => 'Werben',
				'post_name'    => 'werben',
				'post_content' => '[tamil_werbung]',
			),
			true
		);
		if ( is_wp_error( $id ) ) {
			throw new RuntimeException( 'Seite werben: ' . esc_html( $id->get_error_message() ) );
		}
	}
}

// Verkaufsbedingungen liefert KBS; bis dahin ein leerer Entwurf. Recht zum Verwalten für Administratoren.
tamil_site_seite_anmelden( 'werbebedingungen', 'Verkaufsbedingungen Werbung' );
tamil_site_rechte_anmelden( 'administrator', array( 'tamil_werbung_verwalten' ) );

/**
 * Formate je Platz: Desktop und Handy (Breite, Höhe). Gleiche Maße heißen: ein Bild für beide.
 *
 * @return array<string,array{desktop:array{0:int,1:int},mobil:array{0:int,1:int},wo:string,name:string}>
 */
function tamil_site_werbung_formate(): array {
	return array(
		'leaderboard' => array(
			'name'    => __( 'Leaderboard', 'tamil-site' ),
			'wo'      => __( 'unter der Navigation, alle Seiten', 'tamil-site' ),
			'desktop' => array( 728, 90 ),
			'mobil'   => array( 320, 50 ),
		),
		'sidebar'     => array(
			'name'    => __( 'Half Page', 'tamil-site' ),
			'wo'      => __( 'Seitenspalte', 'tamil-site' ),
			'desktop' => array( 300, 600 ),
			'mobil'   => array( 300, 600 ),
		),
		'inarticle'   => array(
			'name'    => __( 'Im Artikel', 'tamil-site' ),
			'wo'      => __( 'nach dem zweiten Absatz', 'tamil-site' ),
			'desktop' => array( 728, 90 ),
			'mobil'   => array( 300, 250 ),
		),
		'billboard'   => array(
			'name'    => __( 'Billboard', 'tamil-site' ),
			'wo'      => __( 'Startseite, zwischen den Rubriken', 'tamil-site' ),
			'desktop' => array( 970, 250 ),
			'mobil'   => array( 300, 250 ),
		),
		'footer'      => array(
			'name'    => __( 'Fuß', 'tamil-site' ),
			'wo'      => __( 'über dem Fuß der Seite', 'tamil-site' ),
			'desktop' => array( 728, 90 ),
			'mobil'   => array( 320, 100 ),
		),
		'mobile'      => array(
			'name'    => __( 'Mobil', 'tamil-site' ),
			'wo'      => __( 'am Handy fest am unteren Rand', 'tamil-site' ),
			'desktop' => array( 320, 50 ),
			'mobil'   => array( 320, 50 ),
		),
	);
}

/**
 * Braucht der Platz ein eigenes Bild fürs Handy?
 */
function tamil_site_werbung_zwei_bilder( string $platz ): bool {
	$f = tamil_site_werbung_formate()[ $platz ] ?? null;
	return $f && $f['desktop'] !== $f['mobil'];
}

/**
 * Angebote mit Standardwerten (Vorschläge der Festlegung; Preise leer = „Preis folgt“).
 *
 * @return array{laufzeiten:array<int,int>,vorlauf:int,bedingungen_fassung:string,plaetze:array<string,array{aktiv:bool,preise:array<int,int>}>}
 */
function tamil_site_werbung_angebote(): array {
	$gespeichert = get_option( 'tamil_site_werbung_angebote', array() );
	$gespeichert = is_array( $gespeichert ) ? $gespeichert : array();
	$laufzeiten  = array_values( array_filter( array_map( 'intval', (array) ( $gespeichert['laufzeiten'] ?? array( 7, 14, 30 ) ) ) ) );
	$out         = array(
		'laufzeiten'          => $laufzeiten ? $laufzeiten : array( 7, 14, 30 ),
		'vorlauf'             => max( 0, (int) ( $gespeichert['vorlauf'] ?? 2 ) ),
		'bedingungen_fassung' => (string) ( $gespeichert['bedingungen_fassung'] ?? '' ),
		'plaetze'             => array(),
	);
	foreach ( array_keys( tamil_site_werbung_formate() ) as $platz ) {
		$p      = (array) ( $gespeichert['plaetze'][ $platz ] ?? array() );
		$preise = array();
		$roh    = (array) ( $p['preise'] ?? array() );
		foreach ( $out['laufzeiten'] as $tage ) {
			$preise[ $tage ] = max( 0, (int) ( $roh[ $tage ] ?? 0 ) );
		}
		$out['plaetze'][ $platz ] = array(
			'aktiv'  => array_key_exists( 'aktiv', $p ) ? (bool) $p['aktiv'] : true,
			'preise' => $preise,
		);
	}
	return $out;
}

/**
 * Preis in Cent für Platz und Laufzeit; 0 = noch kein Preis („Preis folgt“).
 */
function tamil_site_werbung_preis( string $platz, int $laufzeit ): int {
	$a = tamil_site_werbung_angebote();
	return (int) ( $a['plaetze'][ $platz ]['preise'][ $laufzeit ] ?? 0 );
}

/**
 * Betrag für die Anzeige, z. B. „1.250,00 €“.
 */
function tamil_site_werbung_betrag_text( int $cent ): string {
	return number_format_i18n( $cent / 100, 2 ) . ' €';
}

/**
 * Heute im Kalender der Website (Zeitzone der Einstellungen).
 */
function tamil_site_werbung_heute(): string {
	return wp_date( 'Y-m-d' );
}

/**
 * Datum plus Tage (Y-m-d).
 */
function tamil_site_werbung_plus_tage( string $tag, int $tage ): string {
	return gmdate( 'Y-m-d', (int) strtotime( $tag . ' 00:00:00 UTC' ) + $tage * DAY_IN_SECONDS );
}

/**
 * Frühester Starttag: heute plus Vorlauf in Werktagen (Montag bis Freitag; Feiertage kennt die Website nicht).
 */
function tamil_site_werbung_fruehester_start( ?string $heute = null ): string {
	$tag   = $heute ?? tamil_site_werbung_heute();
	$offen = tamil_site_werbung_angebote()['vorlauf'];
	while ( $offen > 0 ) {
		$tag = tamil_site_werbung_plus_tage( $tag, 1 );
		if ( (int) gmdate( 'N', (int) strtotime( $tag . ' UTC' ) ) <= 5 ) {
			--$offen;
		}
	}
	return $tag;
}

/**
 * Ist das ein gültiges Datum Y-m-d?
 */
function tamil_site_werbung_datum_ok( string $tag ): bool {
	$d = DateTimeImmutable::createFromFormat( '!Y-m-d', $tag, new DateTimeZone( 'UTC' ) );
	return $d && $d->format( 'Y-m-d' ) === $tag;
}

/**
 * Ist der Platz buchbar (Schalter an, Angebot aktiv, Preis gesetzt)?
 */
function tamil_site_werbung_buchbar( string $platz, int $laufzeit ): bool {
	$a = tamil_site_werbung_angebote();
	return tamil_site_funktion_an( 'werbung' )
		&& ! empty( $a['plaetze'][ $platz ]['aktiv'] )
		&& in_array( $laufzeit, $a['laufzeiten'], true )
		&& tamil_site_werbung_preis( $platz, $laufzeit ) > 0;
}

/**
 * Die eine Aktiv-Funktion: bezahlt und geprüft und nicht pausiert und nicht vorzeitig beendet und heute im Zeitraum.
 *
 * @param array<string,mixed> $b     Buchung (Zeile).
 * @param string|null         $heute Datum Y-m-d (Standard: heute).
 */
function tamil_site_werbung_aktiv( array $b, ?string $heute = null ): bool {
	$heute = $heute ?? tamil_site_werbung_heute();
	return 'bezahlt' === ( $b['zahlung'] ?? '' )
		&& 'freigegeben' === ( $b['pruefung'] ?? '' )
		&& empty( $b['pausiert'] )
		&& empty( $b['beendet_at'] )
		&& (string) $b['start'] <= $heute
		&& $heute <= (string) $b['ende'];
}

/**
 * Angezeigter Stand (aus Zahlung, Prüfung, Pause, Ende und Datum; „läuft“ nur über die Aktiv-Funktion).
 *
 * @param array<string,mixed> $b Buchung.
 * @return string reserviert, verfallen, in_pruefung, geplant, laeuft, pausiert, beendet, abgelehnt, erstattet
 */
function tamil_site_werbung_stand( array $b, ?string $heute = null ): string {
	$heute = $heute ?? tamil_site_werbung_heute();
	if ( 'erstattet' === $b['zahlung'] ) {
		return 'erstattet';
	}
	if ( 'abgelehnt' === $b['pruefung'] ) {
		return 'abgelehnt';
	}
	if ( 'offen' === $b['zahlung'] ) {
		return (string) $b['reserviert_bis'] > gmdate( 'Y-m-d H:i:s' ) ? 'reserviert' : 'verfallen';
	}
	if ( 'bezahlt' !== $b['zahlung'] ) {
		return 'verfallen';
	}
	if ( tamil_site_werbung_aktiv( $b, $heute ) ) {
		return 'laeuft';
	}
	if ( ! empty( $b['beendet_at'] ) || $heute > (string) $b['ende'] ) {
		return 'beendet';
	}
	if ( 'freigegeben' !== $b['pruefung'] ) {
		return 'in_pruefung';
	}
	return ! empty( $b['pausiert'] ) ? 'pausiert' : 'geplant';
}

/**
 * Beschriftung der Stände.
 *
 * @return array<string,string>
 */
function tamil_site_werbung_staende(): array {
	return array(
		'reserviert'  => __( 'reserviert, Zahlung offen', 'tamil-site' ),
		'verfallen'   => __( 'nicht bezahlt, Tage frei', 'tamil-site' ),
		'in_pruefung' => __( 'bezahlt, in Prüfung', 'tamil-site' ),
		'geplant'     => __( 'geplant', 'tamil-site' ),
		'laeuft'      => __( 'läuft', 'tamil-site' ),
		'pausiert'    => __( 'pausiert', 'tamil-site' ),
		'beendet'     => __( 'beendet', 'tamil-site' ),
		'abgelehnt'   => __( 'abgelehnt', 'tamil-site' ),
		'erstattet'   => __( 'abgelehnt, erstattet', 'tamil-site' ),
	);
}

/**
 * Buchung lesen.
 *
 * @return array<string,mixed>|null
 */
function tamil_site_werbung_buchung( int $id ): ?array {
	global $wpdb;
	$b = $wpdb->get_row( $wpdb->prepare( 'SELECT * FROM %i WHERE id = %d', tamil_site_werbung_tabelle( 'buchungen' ), $id ), ARRAY_A );
	return $b ? $b : null;
}

/**
 * Buchung nach Buchungsnummer.
 *
 * @return array<string,mixed>|null
 */
function tamil_site_werbung_buchung_nach_nummer( string $nummer ): ?array {
	global $wpdb;
	$b = $wpdb->get_row( $wpdb->prepare( 'SELECT * FROM %i WHERE nummer = %s', tamil_site_werbung_tabelle( 'buchungen' ), strtoupper( $nummer ) ), ARRAY_A );
	return $b ? $b : null;
}

/**
 * Buchung nach geheimem Kundenlink (gespeichert ist nur der Hash).
 *
 * @return array<string,mixed>|null
 */
function tamil_site_werbung_buchung_nach_token( string $token ): ?array {
	global $wpdb;
	if ( ! preg_match( '/^[a-f0-9]{48}$/', $token ) ) {
		return null;
	}
	$b = $wpdb->get_row( $wpdb->prepare( 'SELECT * FROM %i WHERE kunden_hash = %s', tamil_site_werbung_tabelle( 'buchungen' ), hash( 'sha256', $token ) ), ARRAY_A );
	return $b ? $b : null;
}

/**
 * Neues Geheimnis für den Kundenlink: gibt den Klartext zurück (nur für diesen Aufruf), speichert den Hash.
 */
function tamil_site_werbung_neues_token( int $id ): string {
	global $wpdb;
	$token = bin2hex( random_bytes( 24 ) );
	$wpdb->update( tamil_site_werbung_tabelle( 'buchungen' ), array( 'kunden_hash' => hash( 'sha256', $token ) ), array( 'id' => $id ) );
	return $token;
}

/**
 * Eine Zeile ins Protokoll der Buchung (ohne Personendaten).
 *
 * @param string $wer website, kunde, stripe oder Anmeldename.
 */
function tamil_site_werbung_protokoll( int $id, string $wer, string $was ): void {
	global $wpdb;
	$wpdb->insert(
		tamil_site_werbung_tabelle( 'protokoll' ),
		array(
			'buchung_id' => $id,
			'zeit'       => gmdate( 'Y-m-d H:i:s' ),
			'wer'        => substr( $wer, 0, 60 ),
			'was'        => substr( $was, 0, 255 ),
		)
	);
}

/**
 * Protokoll einer Buchung, älteste zuerst.
 *
 * @return array<int,array<string,string>>
 */
function tamil_site_werbung_protokoll_lesen( int $id ): array {
	global $wpdb;
	return (array) $wpdb->get_results( $wpdb->prepare( 'SELECT zeit, wer, was FROM %i WHERE buchung_id = %d ORDER BY id', tamil_site_werbung_tabelle( 'protokoll' ), $id ), ARRAY_A );
}

/**
 * Warnung für einen Menschen in der Buchungsliste setzen (leer = keine).
 */
function tamil_site_werbung_warnung( int $id, string $text ): void {
	global $wpdb;
	$wpdb->update( tamil_site_werbung_tabelle( 'buchungen' ), array( 'warnung' => $text ), array( 'id' => $id ) );
	if ( '' !== $text ) {
		tamil_site_werbung_protokoll( $id, 'website', 'Warnung: ' . $text );
	}
}

/**
 * Wer handelt gerade (für das Protokoll)?
 */
function tamil_site_werbung_wer(): string {
	$u = wp_get_current_user();
	return $u && $u->exists() ? (string) $u->user_login : 'website';
}

/**
 * Belegt alle Tage der Buchung (aufsteigend). Tage, die schon dieser Buchung gehören, zählen als belegt. Scheitert ein
 * Tag, werden die eigenen Tage wieder frei.
 *
 * @param array<string,mixed> $b Buchung.
 */
function tamil_site_werbung_tage_belegen( array $b ): bool {
	global $wpdb;
	$tabelle = tamil_site_werbung_tabelle( 'tage' );
	for ( $tag = (string) $b['start']; $tag <= (string) $b['ende']; $tag = tamil_site_werbung_plus_tage( $tag, 1 ) ) {
		$ok = $wpdb->query( $wpdb->prepare( 'INSERT IGNORE INTO %i (platz, tag, buchung_id) VALUES (%s, %s, %d)', $tabelle, $b['platz'], $tag, (int) $b['id'] ) );
		if ( 0 === $ok ) {
			$ok = (int) $wpdb->get_var( $wpdb->prepare( 'SELECT buchung_id FROM %i WHERE platz = %s AND tag = %s', $tabelle, $b['platz'], $tag ) ) === (int) $b['id'] ? 1 : 0;
		}
		if ( 1 !== $ok ) {
			tamil_site_werbung_tage_freigeben( (int) $b['id'] );
			return false;
		}
	}
	return true;
}

/**
 * Tage einer Buchung freigeben, wahlweise nur die nach einem Datum.
 */
function tamil_site_werbung_tage_freigeben( int $id, string $nach = '' ): void {
	global $wpdb;
	if ( '' === $nach ) {
		$wpdb->query( $wpdb->prepare( 'DELETE FROM %i WHERE buchung_id = %d', tamil_site_werbung_tabelle( 'tage' ), $id ) );
		return;
	}
	$wpdb->query( $wpdb->prepare( 'DELETE FROM %i WHERE buchung_id = %d AND tag > %s', tamil_site_werbung_tabelle( 'tage' ), $id, $nach ) );
}

/**
 * Abgelaufene Reservierungen ohne Zahlung: Zahlung „fehlgeschlagen“, Tage frei.
 *
 * @return int Anzahl freigegebener Buchungen.
 */
function tamil_site_werbung_aufraeumen(): int {
	global $wpdb;
	$tabelle = tamil_site_werbung_tabelle( 'buchungen' );
	$jetzt   = gmdate( 'Y-m-d H:i:s' );
	$ids     = $wpdb->get_col( $wpdb->prepare( "SELECT id FROM %i WHERE zahlung = 'offen' AND reserviert_bis < %s", $tabelle, $jetzt ) );
	$frei    = 0;
	foreach ( $ids as $id ) {
		$geaendert = (int) $wpdb->query( $wpdb->prepare( "UPDATE %i SET zahlung = 'fehlgeschlagen' WHERE id = %d AND zahlung = 'offen' AND reserviert_bis < %s", $tabelle, (int) $id, $jetzt ) );
		if ( 1 === $geaendert ) {
			tamil_site_werbung_tage_freigeben( (int) $id );
			tamil_site_werbung_bilder_loeschen( (int) $id );
			tamil_site_werbung_protokoll( (int) $id, 'website', 'Reservierung ohne Zahlung abgelaufen, Tage frei, Werbemittel gelöscht' );
			++$frei;
		}
	}
	// Nie bezahlte Buchungen: Personendaten nach der Frist leeren (bezahlte bleiben für das Steuerrecht).
	$frist = gmdate( 'Y-m-d H:i:s', time() - TAMIL_SITE_WERBUNG_FRIST_UNBEZAHLT_TAGE * DAY_IN_SECONDS );
	$alt   = $wpdb->get_col( $wpdb->prepare( "SELECT id FROM %i WHERE zahlung = 'fehlgeschlagen' AND erstellt_at < %s AND ( firma <> '' OR email <> '' OR ansprechperson <> '' )", $tabelle, $frist ) );
	foreach ( $alt as $id ) {
		tamil_site_werbung_bilder_loeschen( (int) $id );
		$geleert = $wpdb->query(
			$wpdb->prepare(
				"UPDATE %i SET firma = '', ansprechperson = '', rechnungsadresse = '', email = '', telefon = '', ust_id = '', kunden_hash = '' WHERE id = %d AND zahlung = 'fehlgeschlagen'",
				$tabelle,
				(int) $id
			)
		);
		if ( 1 === $geleert ) {
			tamil_site_werbung_protokoll( (int) $id, 'website', 'Personendaten gelöscht (nie bezahlt, Frist ' . TAMIL_SITE_WERBUNG_FRIST_UNBEZAHLT_TAGE . ' Tage)' );
		}
	}
	return $frei;
}

/**
 * Datei eines Werbemittels löschen (Pfad relativ zu uploads/).
 */
function tamil_site_werbung_datei_loeschen( string $relativ ): void {
	if ( '' !== $relativ && ! str_contains( $relativ, '..' ) ) {
		wp_delete_file( trailingslashit( wp_get_upload_dir()['basedir'] ) . $relativ );
	}
}

/**
 * Werbemittel einer nie bezahlten Buchung löschen und die Felder leeren.
 */
function tamil_site_werbung_bilder_loeschen( int $id ): void {
	global $wpdb;
	$b = tamil_site_werbung_buchung( $id );
	if ( ! $b || in_array( $b['zahlung'], array( 'bezahlt', 'erstattet' ), true ) ) {
		return;
	}
	tamil_site_werbung_datei_loeschen( (string) $b['werbemittel_desktop'] );
	tamil_site_werbung_datei_loeschen( (string) $b['werbemittel_mobil'] );
	$wpdb->update(
		tamil_site_werbung_tabelle( 'buchungen' ),
		array(
			'werbemittel_desktop' => '',
			'werbemittel_mobil'   => '',
		),
		array( 'id' => $id )
	);
}

/**
 * Reservierung bis zum Ablauf der Stripe-Session (plus Puffer) verlängern – nur anheben und nur, solange die Buchung
 * offen und noch reserviert ist.
 *
 * @param int $id  Buchung.
 * @param int $bis Unix-Zeit.
 */
function tamil_site_werbung_reservierung_verlaengern( int $id, int $bis ): bool {
	global $wpdb;
	$neu = $wpdb->query(
		$wpdb->prepare(
			"UPDATE %i SET reserviert_bis = %s WHERE id = %d AND zahlung = 'offen' AND reserviert_bis >= %s AND reserviert_bis < %s",
			tamil_site_werbung_tabelle( 'buchungen' ),
			gmdate( 'Y-m-d H:i:s', $bis ),
			$id,
			gmdate( 'Y-m-d H:i:s' ),
			gmdate( 'Y-m-d H:i:s', $bis )
		)
	);
	return 1 === $neu;
}

/**
 * Zahl der offenen, noch reservierten Buchungen.
 */
function tamil_site_werbung_offene(): int {
	global $wpdb;
	return (int) $wpdb->get_var( $wpdb->prepare( "SELECT COUNT(*) FROM %i WHERE zahlung = 'offen' AND reserviert_bis >= %s", tamil_site_werbung_tabelle( 'buchungen' ), gmdate( 'Y-m-d H:i:s' ) ) );
}

/**
 * Wie oft steht ein Eintrag schon im Protokoll der Buchung (Versuchszähler für Idempotenzschlüssel)?
 */
function tamil_site_werbung_protokoll_anzahl( int $id, string $was ): int {
	global $wpdb;
	return (int) $wpdb->get_var( $wpdb->prepare( 'SELECT COUNT(*) FROM %i WHERE buchung_id = %d AND was = %s', tamil_site_werbung_tabelle( 'protokoll' ), $id, $was ) );
}

/**
 * Belegte Tage eines Platzes in einem Zeitraum.
 *
 * @return array<string,bool> Tag → true
 */
function tamil_site_werbung_belegt( string $platz, string $von, string $bis ): array {
	global $wpdb;
	$tage = $wpdb->get_col( $wpdb->prepare( 'SELECT tag FROM %i WHERE platz = %s AND tag >= %s AND tag <= %s', tamil_site_werbung_tabelle( 'tage' ), $platz, $von, $bis ) );
	return array_fill_keys( array_map( 'strval', $tage ), true );
}

/**
 * Mögliche Starttage, an denen die ganze Laufzeit frei ist.
 *
 * @return array<int,string>
 */
function tamil_site_werbung_freie_starts( string $platz, int $laufzeit, int $anzahl = 60, ?string $heute = null ): array {
	tamil_site_werbung_aufraeumen();
	$von      = tamil_site_werbung_fruehester_start( $heute );
	$bis      = tamil_site_werbung_plus_tage( $heute ?? tamil_site_werbung_heute(), TAMIL_SITE_WERBUNG_HORIZONT_TAGE );
	$belegt   = tamil_site_werbung_belegt( $platz, $von, tamil_site_werbung_plus_tage( $bis, $laufzeit ) );
	$starts   = array();
	$gefunden = 0;
	for ( $start = $von; $start <= $bis && $gefunden < $anzahl; $start = tamil_site_werbung_plus_tage( $start, 1 ) ) {
		$frei = true;
		for ( $i = 0; $i < $laufzeit; $i++ ) {
			if ( isset( $belegt[ tamil_site_werbung_plus_tage( $start, $i ) ] ) ) {
				$frei = false;
				break;
			}
		}
		if ( $frei ) {
			$starts[] = $start;
			++$gefunden;
		}
	}
	return $starts;
}

/**
 * Neue Buchungsnummer (W + 8 Zeichen ohne verwechselbare Zeichen).
 */
function tamil_site_werbung_nummer(): string {
	$zeichen = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';
	$n       = 'W';
	for ( $i = 0; $i < 8; $i++ ) {
		$n .= $zeichen[ random_int( 0, strlen( $zeichen ) - 1 ) ];
	}
	return $n;
}

/**
 * Buchung anlegen und ihre Tage atomar reservieren (35 Minuten). Erwartet geprüfte Daten.
 *
 * @param array<string,mixed> $d platz, laufzeit, start, firma, ansprechperson, rechnungsadresse, email, telefon,
 *                               ust_id, werbemittel_desktop, werbemittel_mobil, ziel_url.
 * @return array{0:array<string,mixed>,1:string}|WP_Error Buchung und Klartext des Kundenlinks.
 */
function tamil_site_werbung_reservieren( array $d ) {
	global $wpdb;
	$platz    = (string) $d['platz'];
	$laufzeit = (int) $d['laufzeit'];
	$start    = (string) $d['start'];
	if ( ! tamil_site_werbung_buchbar( $platz, $laufzeit ) ) {
		return new WP_Error( 'nicht_buchbar', __( 'Dieser Platz ist mit dieser Laufzeit gerade nicht buchbar.', 'tamil-site' ) );
	}
	$heute = tamil_site_werbung_heute();
	if ( ! tamil_site_werbung_datum_ok( $start ) || $start < tamil_site_werbung_fruehester_start( $heute )
		|| $start > tamil_site_werbung_plus_tage( $heute, TAMIL_SITE_WERBUNG_HORIZONT_TAGE ) ) {
		return new WP_Error( 'start', __( 'Dieser Starttag ist nicht wählbar.', 'tamil-site' ) );
	}
	tamil_site_werbung_aufraeumen();
	if ( tamil_site_werbung_offene() >= TAMIL_SITE_WERBUNG_MAX_OFFEN ) {
		return new WP_Error( 'voll', __( 'Gerade sind zu viele offene Buchungen in Bearbeitung. Bitte in einer halben Stunde erneut versuchen.', 'tamil-site' ) );
	}
	$token = bin2hex( random_bytes( 24 ) );
	$zeile = array(
		'platz'               => $platz,
		'laufzeit'            => $laufzeit,
		'start'               => $start,
		'ende'                => tamil_site_werbung_plus_tage( $start, $laufzeit - 1 ),
		'reserviert_bis'      => gmdate( 'Y-m-d H:i:s', time() + TAMIL_SITE_WERBUNG_RESERVIERUNG_MINUTEN * MINUTE_IN_SECONDS ),
		'firma'               => (string) $d['firma'],
		'ansprechperson'      => (string) $d['ansprechperson'],
		'rechnungsadresse'    => (string) $d['rechnungsadresse'],
		'email'               => (string) $d['email'],
		'telefon'             => (string) ( $d['telefon'] ?? '' ),
		'ust_id'              => (string) ( $d['ust_id'] ?? '' ),
		'werbemittel_desktop' => (string) $d['werbemittel_desktop'],
		'werbemittel_mobil'   => (string) $d['werbemittel_mobil'],
		'ziel_url'            => (string) $d['ziel_url'],
		'betrag'              => tamil_site_werbung_preis( $platz, $laufzeit ),
		'waehrung'            => 'eur',
		'ablehnungsgrund'     => '',
		'warnung'             => '',
		'kunden_hash'         => hash( 'sha256', $token ),
		'erstellt_at'         => gmdate( 'Y-m-d H:i:s' ),
	);
	$id    = 0;
	for ( $versuch = 0; $versuch < 5 && ! $id; $versuch++ ) {
		$zeile['nummer'] = tamil_site_werbung_nummer();
		$wpdb->suppress_errors( true );
		$ok = $wpdb->insert( tamil_site_werbung_tabelle( 'buchungen' ), $zeile );
		$wpdb->suppress_errors( false );
		$id = $ok ? (int) $wpdb->insert_id : 0;
	}
	if ( ! $id ) {
		return new WP_Error( 'speichern', __( 'Die Buchung konnte nicht gespeichert werden.', 'tamil-site' ) );
	}
	$b = tamil_site_werbung_buchung( $id );
	if ( ! tamil_site_werbung_tage_belegen( $b ) ) {
		// Nie zustande gekommen: Zeile wieder weg, Kundendaten bleiben nicht liegen.
		$wpdb->delete( tamil_site_werbung_tabelle( 'buchungen' ), array( 'id' => $id ) );
		return new WP_Error( 'belegt', __( 'Mindestens ein Tag ist gerade vergeben worden. Bitte einen anderen Starttag wählen.', 'tamil-site' ) );
	}
	tamil_site_werbung_protokoll( $id, 'kunde', sprintf( 'reserviert: %s, %d Tage ab %s, bis %s UTC', $platz, $laufzeit, $start, $zeile['reserviert_bis'] ) );
	return array( $b, $token );
}

/**
 * Zahlung bestätigen (nur aus einer signierten Stripe-Meldung oder dem Abgleich mit Stripe). Idempotent.
 *
 * @param array<string,mixed> $b       Buchung.
 * @param array<string,mixed> $session Checkout-Session von Stripe.
 * @param string              $quelle  Meldung oder Abgleich.
 * @return string bezahlt (neu übernommen), schon (nichts zu tun), offen (nicht bezahlt) oder fehler (bezahlt, aber
 *                nicht übernehmbar – die Warnung ist gesetzt, ein Mensch muss handeln).
 */
function tamil_site_werbung_zahlung_bestaetigen( array $b, array $session, string $quelle ): string {
	global $wpdb;
	$id = (int) $b['id'];
	if ( 'paid' !== ( $session['payment_status'] ?? '' ) ) {
		return 'offen';
	}
	if ( (string) ( $session['id'] ?? '' ) !== (string) $b['stripe_session'] ) {
		tamil_site_werbung_warnung( $id, 'Zahlung zu einer anderen Checkout-Session (' . sanitize_text_field( (string) ( $session['id'] ?? '' ) ) . ') eingegangen – bitte in Stripe prüfen' );
		return 'fehler';
	}
	if ( (int) ( $session['amount_total'] ?? -1 ) !== (int) $b['betrag'] || strtolower( (string) ( $session['currency'] ?? '' ) ) !== $b['waehrung'] ) {
		tamil_site_werbung_warnung( $id, 'Betrag oder Währung der Zahlung passt nicht zur Buchung – bitte in Stripe prüfen' );
		return 'fehler';
	}
	$pi      = $session['payment_intent'] ?? '';
	$pi      = is_array( $pi ) ? (string) ( $pi['id'] ?? '' ) : (string) $pi;
	$beleg   = is_array( $session['payment_intent'] ?? null ) ? (string) ( $session['payment_intent']['latest_charge']['receipt_url'] ?? '' ) : '';
	$tabelle = tamil_site_werbung_tabelle( 'buchungen' );
	$neu     = $wpdb->query( $wpdb->prepare( "UPDATE %i SET zahlung = 'bezahlt', stripe_zahlung = %s, beleg_url = %s WHERE id = %d AND zahlung = 'offen'", $tabelle, $pi, esc_url_raw( $beleg ), $id ) );
	if ( 1 === $neu ) {
		tamil_site_werbung_protokoll( $id, 'stripe', 'bezahlt (' . $quelle . ')' );
		return 'bezahlt';
	}
	$jetzt = false === $neu ? null : tamil_site_werbung_buchung( $id );
	if ( $jetzt && in_array( $jetzt['zahlung'], array( 'bezahlt', 'erstattet' ), true ) ) {
		return 'schon';
	}
	if ( $jetzt && 'fehlgeschlagen' === $jetzt['zahlung'] ) {
		// Zahlung kam nach Ablauf der Reservierung: Tage erneut belegen, sonst muss ein Mensch erstatten.
		$frei = tamil_site_werbung_tage_belegen( $jetzt );
		$neu  = $wpdb->query( $wpdb->prepare( "UPDATE %i SET zahlung = 'bezahlt', stripe_zahlung = %s, beleg_url = %s WHERE id = %d AND zahlung = 'fehlgeschlagen'", $tabelle, $pi, esc_url_raw( $beleg ), $id ) );
		if ( 1 === $neu ) {
			tamil_site_werbung_protokoll( $id, 'stripe', 'bezahlt nach Ablauf der Reservierung (' . $quelle . ')' );
			if ( ! $frei ) {
				tamil_site_werbung_warnung( $id, 'Zahlung nach Ablauf der Reservierung, Tage inzwischen vergeben – bitte erstatten' );
			} elseif ( '' === $jetzt['werbemittel_desktop'] ) {
				tamil_site_werbung_warnung( $id, 'Zahlung nach Ablauf der Reservierung, Werbemittel schon gelöscht – neu einreichen lassen oder erstatten' );
			}
			return 'bezahlt';
		}
		if ( $frei ) {
			tamil_site_werbung_tage_freigeben( $id );
		}
	}
	tamil_site_werbung_warnung( $id, 'Bezahlte Zahlung konnte nicht übernommen werden – bitte in Stripe prüfen' );
	return 'fehler';
}

/**
 * Zahlung abgebrochen, abgelehnt oder Session abgelaufen: nur aus „offen“, Tage frei.
 *
 * @param array<string,mixed> $b Buchung.
 */
function tamil_site_werbung_zahlung_abbrechen( array $b, string $wer, string $grund ): bool {
	global $wpdb;
	$neu = $wpdb->query( $wpdb->prepare( "UPDATE %i SET zahlung = 'fehlgeschlagen' WHERE id = %d AND zahlung = 'offen'", tamil_site_werbung_tabelle( 'buchungen' ), (int) $b['id'] ) );
	if ( false === $neu ) {
		throw new RuntimeException( 'Buchung ' . (int) $b['id'] . ': Abbruch nicht gespeichert' );
	}
	if ( 1 !== $neu ) {
		return false;
	}
	tamil_site_werbung_tage_freigeben( (int) $b['id'] );
	tamil_site_werbung_bilder_loeschen( (int) $b['id'] );
	tamil_site_werbung_protokoll( (int) $b['id'], $wer, $grund . ', Tage frei, Werbemittel gelöscht' );
	return true;
}

/**
 * Volle Erstattung übernehmen: Zahlung „erstattet“, Tage ab morgen frei (die Anzeige endet sofort, weil die
 * Aktiv-Funktion „bezahlt“ verlangt).
 */
function tamil_site_werbung_als_erstattet( int $id, string $quelle ): bool {
	global $wpdb;
	$neu = $wpdb->query( $wpdb->prepare( "UPDATE %i SET zahlung = 'erstattet', warnung = '' WHERE id = %d AND zahlung = 'bezahlt'", tamil_site_werbung_tabelle( 'buchungen' ), $id ) );
	if ( false === $neu ) {
		throw new RuntimeException( 'Buchung ' . (int) $id . ': Erstattung nicht gespeichert' );
	}
	if ( 1 !== $neu ) {
		return false;
	}
	tamil_site_werbung_tage_freigeben( $id, tamil_site_werbung_heute() );
	tamil_site_werbung_protokoll( $id, 'stripe', 'erstattet (' . $quelle . '), Tage ab morgen frei' );
	return true;
}

/**
 * Werbemittel freigeben (Mensch). Nur bezahlte Buchungen in Prüfung.
 */
function tamil_site_werbung_freigeben( int $id ): bool {
	global $wpdb;
	$neu = (int) $wpdb->query( $wpdb->prepare( "UPDATE %i SET pruefung = 'freigegeben' WHERE id = %d AND pruefung = 'offen' AND zahlung = 'bezahlt'", tamil_site_werbung_tabelle( 'buchungen' ), $id ) );
	if ( 1 === $neu ) {
		tamil_site_werbung_protokoll( $id, tamil_site_werbung_wer(), 'Werbemittel geprüft und freigegeben' );
	}
	return 1 === $neu;
}

/**
 * Werbemittel ablehnen (Mensch): Tage frei, volle Erstattung über Stripe.
 */
function tamil_site_werbung_ablehnen( int $id, string $grund ): bool {
	global $wpdb;
	$neu = (int) $wpdb->query( $wpdb->prepare( "UPDATE %i SET pruefung = 'abgelehnt', ablehnungsgrund = %s WHERE id = %d AND pruefung = 'offen' AND zahlung = 'bezahlt'", tamil_site_werbung_tabelle( 'buchungen' ), $grund, $id ) );
	if ( 1 !== $neu ) {
		return false;
	}
	tamil_site_werbung_tage_freigeben( $id );
	tamil_site_werbung_protokoll( $id, tamil_site_werbung_wer(), 'abgelehnt, Tage frei' );
	tamil_site_werbung_erstatten( $id );
	return true;
}

/**
 * Pausieren (true) oder fortsetzen (false).
 */
function tamil_site_werbung_pausieren( int $id, bool $pause ): bool {
	global $wpdb;
	$neu = (int) $wpdb->query( $wpdb->prepare( "UPDATE %i SET pausiert = %d WHERE id = %d AND pausiert = %d AND zahlung = 'bezahlt' AND beendet_at IS NULL", tamil_site_werbung_tabelle( 'buchungen' ), $pause ? 1 : 0, $id, $pause ? 0 : 1 ) );
	if ( 1 === $neu ) {
		tamil_site_werbung_protokoll( $id, tamil_site_werbung_wer(), $pause ? 'pausiert' : 'fortgesetzt' );
	}
	return 1 === $neu;
}

/**
 * Vorzeitig beenden (Mensch): ab morgen frei.
 */
function tamil_site_werbung_beenden( int $id ): bool {
	global $wpdb;
	$neu = (int) $wpdb->query( $wpdb->prepare( "UPDATE %i SET beendet_at = %s WHERE id = %d AND beendet_at IS NULL AND zahlung = 'bezahlt' AND pruefung <> 'abgelehnt'", tamil_site_werbung_tabelle( 'buchungen' ), gmdate( 'Y-m-d H:i:s' ), $id ) );
	if ( 1 === $neu ) {
		tamil_site_werbung_tage_freigeben( $id, tamil_site_werbung_heute() );
		tamil_site_werbung_protokoll( $id, tamil_site_werbung_wer(), 'vorzeitig beendet, folgende Tage frei' );
	}
	return 1 === $neu;
}

/**
 * Volle Erstattung über Stripe (nach Ablehnung automatisch; nach vorzeitigem Ende oder einer gescheiterten
 * Erstattung von Hand). Fehler werden zur Warnung für einen Menschen.
 */
function tamil_site_werbung_erstatten( int $id ): bool {
	global $wpdb;
	$b = tamil_site_werbung_buchung( $id );
	if ( ! $b || 'bezahlt' !== $b['zahlung'] || ( 'abgelehnt' !== $b['pruefung'] && empty( $b['beendet_at'] ) ) ) {
		return false;
	}
	if ( '' === $b['stripe_zahlung'] ) {
		tamil_site_werbung_warnung( $id, 'Erstattung nicht möglich: Zahlung bei Stripe unbekannt – bitte in Stripe erstatten' );
		return false;
	}
	$versuch = tamil_site_werbung_protokoll_anzahl( $id, 'Erstattung über Stripe angefordert' ) + 1;
	tamil_site_werbung_protokoll( $id, tamil_site_werbung_wer(), 'Erstattung über Stripe angefordert' );
	$antwort = tamil_site_stripe_aufruf(
		'POST',
		'refunds',
		array(
			'payment_intent' => $b['stripe_zahlung'],
			'metadata'       => array( 'buchung' => $b['nummer'] ),
		),
		'erstattung-' . $b['nummer'] . '-' . $versuch
	);
	if ( is_wp_error( $antwort ) ) {
		tamil_site_werbung_warnung( $id, 'Erstattung gescheitert: ' . $antwort->get_error_message() );
		return false;
	}
	$status = (string) ( $antwort['status'] ?? '' );
	if ( 'succeeded' === $status ) {
		try {
			tamil_site_werbung_als_erstattet( $id, 'Antwort auf die Erstattung' );
		} catch ( Throwable $e ) {
			tamil_site_werbung_warnung( $id, 'Erstattung bei Stripe erfolgt, aber nicht gespeichert – bitte prüfen' );
			return false;
		}
		return true;
	}
	if ( 'pending' === $status || 'requires_action' === $status ) {
		tamil_site_werbung_protokoll( $id, 'stripe', 'Erstattung in Bearbeitung' );
		return true;
	}
	tamil_site_werbung_warnung( $id, 'Erstattung gescheitert (Stand ' . sanitize_key( $status ) . ') – bitte in Stripe prüfen' );
	return false;
}

/**
 * Adresse eines gespeicherten Werbemittels (relativ zu uploads/).
 */
function tamil_site_werbung_bild_url( string $relativ ): string {
	return '' === $relativ ? '' : trailingslashit( wp_get_upload_dir()['baseurl'] ) . ltrim( $relativ, '/' );
}

/**
 * Die heute laufende Buchung eines Platzes (über die Aktiv-Funktion) oder null.
 *
 * @return array<string,mixed>|null
 */
function tamil_site_werbung_laufend( string $platz, ?string $heute = null ): ?array {
	global $wpdb;
	$heute = $heute ?? tamil_site_werbung_heute();
	$b     = $wpdb->get_row(
		$wpdb->prepare(
			'SELECT b.* FROM %i t JOIN %i b ON b.id = t.buchung_id WHERE t.platz = %s AND t.tag = %s',
			tamil_site_werbung_tabelle( 'tage' ),
			tamil_site_werbung_tabelle( 'buchungen' ),
			$platz,
			$heute
		),
		ARRAY_A
	);
	return $b && tamil_site_werbung_aktiv( $b, $heute ) ? $b : null;
}

/**
 * HTML der gebuchten Anzeige eines Platzes, leer ohne aktive Buchung oder bei ausgeschaltetem Schalter.
 */
function tamil_site_werbung_ausliefern( string $platz ): string {
	if ( ! tamil_site_funktion_an( 'werbung' ) ) {
		return '';
	}
	$b = tamil_site_werbung_laufend( $platz );
	if ( ! $b ) {
		return '';
	}
	$f       = tamil_site_werbung_formate()[ $platz ];
	$desktop = tamil_site_werbung_bild_url( (string) $b['werbemittel_desktop'] );
	$mobil   = tamil_site_werbung_bild_url( '' !== $b['werbemittel_mobil'] ? (string) $b['werbemittel_mobil'] : (string) $b['werbemittel_desktop'] );
	$quelle  = tamil_site_werbung_zwei_bilder( $platz ) ? sprintf(
		'<source media="(max-width: %1$dpx)" srcset="%2$s" width="%3$d" height="%4$d">',
		(int) $f['desktop'][0],
		esc_url( $mobil ),
		(int) $f['mobil'][0],
		(int) $f['mobil'][1]
	) : '';
	wp_enqueue_script( 'tamil-site-werbung' );
	return sprintf(
		'<div class="flaeche wb-anzeige" data-wb-buchung="%1$d" data-wb-zaehlen="%2$s"><a href="%3$s" rel="sponsored noopener" target="_blank"><picture>%4$s<img src="%5$s" width="%6$d" height="%7$d" alt="%8$s" decoding="async"></picture></a></div>',
		(int) $b['id'],
		esc_url( rest_url( 'tamil-site/v1/werbung/einblendung' ) ),
		esc_url( rest_url( 'tamil-site/v1/werbung/klick/' . (int) $b['id'] ) ),
		$quelle,
		esc_url( $desktop ),
		(int) $f['desktop'][0],
		(int) $f['desktop'][1],
		/* translators: %s: Firma */
		esc_attr( sprintf( __( 'Anzeige von %s', 'tamil-site' ), $b['firma'] ) )
	);
}
