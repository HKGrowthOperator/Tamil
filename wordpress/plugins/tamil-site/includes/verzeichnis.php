<?php
/**
 * Verzeichnis (Festlegung F2): Einträge, Einsendungen („Eintrag vorschlagen“, „Änderung melden“), Prüfung nach
 * festen Regeln, Freigabe mit genau den freigegebenen Werten, Löschfrist und Protokoll.
 *
 * Formulare: includes/verzeichnis-formular.php · öffentliche Ansicht: includes/verzeichnis-ansicht.php · Eingabemaske
 * und Premium in wp-admin: includes/verzeichnis-admin.php · REST für den Radar: Plugin tamil-radar,
 * includes/verzeichnis.php. WordPress ruft den Radar nie auf und verschickt keine E-Mail.
 *
 * Daten (docs/spezifikation/datenmodell.md §13): Einträge als Beitragstyp tamil_vz_eintrag (Name = Titel,
 * Beschreibung = Inhalt, übrige Felder als geschützte Meta, Kategorie als Taxonomie mit der Art als Term-Meta).
 * Einsendungen in einer eigenen Tabelle, nicht öffentlich, Löschung 90 Tage nach Eingang. Protokoll ohne Namen oder
 * Kontaktdaten, Frist 12 Monate.
 */

defined( 'ABSPATH' ) || exit;

/** Beitragstyp der Einträge. */
define( 'TAMIL_SITE_VZ_TYP', 'tamil_vz_eintrag' );
/** Taxonomie der Kategorien. */
define( 'TAMIL_SITE_VZ_KATEGORIE', 'tamil_vz_kategorie' );
/** Löschfrist der Einsendungen (mit Name und E-Mail des Einsenders), in Tagen ab Eingang. */
define( 'TAMIL_SITE_VZ_FRIST_TAGE', 90 );
/** Frist für das Protokoll, in Monaten. */
define( 'TAMIL_SITE_VZ_PROTOKOLL_MONATE', 12 );
/** Höchstlänge der Beschreibung. */
define( 'TAMIL_SITE_VZ_BESCHREIBUNG_MAX', 600 );

/**
 * Arten → Beschriftung.
 *
 * @return array<string,string>
 */
function tamil_site_vz_arten(): array {
	return array(
		'business'      => __( 'Business', 'tamil-site' ),
		'dienstleister' => __( 'Dienstleister', 'tamil-site' ),
		'verein'        => __( 'Verein', 'tamil-site' ),
		'tempel'        => __( 'Tempel', 'tamil-site' ),
	);
}

/**
 * Kategorien je Art (Vorschlag der Festlegung, bestätigt am 13.11.2026; KBS pflegt sie danach in WordPress).
 *
 * @return array<string,array<int,string>>
 */
function tamil_site_vz_kategorien_vorschlag(): array {
	return array(
		'business'      => array( 'Restaurant und Imbiss', 'Lebensmittel', 'Textil und Schmuck', 'Reise', 'Sonstiges' ),
		'dienstleister' => array( 'Recht und Steuern', 'Gesundheit', 'Übersetzung', 'Foto und Video', 'Catering und Feiern', 'Handwerk', 'Fahrschule', 'Sonstiges' ),
		'verein'        => array( 'Kultur', 'Sport', 'Tamilschule', 'Hilfe und Soziales' ),
		'tempel'        => array( 'Hindu-Tempel', 'Kirche', 'weitere Gebetsstätte' ),
	);
}

/**
 * Länder → Name.
 *
 * @return array<string,string>
 */
function tamil_site_vz_laender(): array {
	return array(
		'DE' => __( 'Deutschland', 'tamil-site' ),
		'AT' => __( 'Österreich', 'tamil-site' ),
		'CH' => __( 'Schweiz', 'tamil-site' ),
	);
}

/**
 * Bundesländer und Kantone je Land.
 *
 * @return array<string,array<int,string>>
 */
function tamil_site_vz_regionen(): array {
	return array(
		'DE' => array( 'Baden-Württemberg', 'Bayern', 'Berlin', 'Brandenburg', 'Bremen', 'Hamburg', 'Hessen', 'Mecklenburg-Vorpommern', 'Niedersachsen', 'Nordrhein-Westfalen', 'Rheinland-Pfalz', 'Saarland', 'Sachsen', 'Sachsen-Anhalt', 'Schleswig-Holstein', 'Thüringen' ),
		'AT' => array( 'Burgenland', 'Kärnten', 'Niederösterreich', 'Oberösterreich', 'Salzburg', 'Steiermark', 'Tirol', 'Vorarlberg', 'Wien' ),
		'CH' => array( 'Aargau', 'Appenzell Ausserrhoden', 'Appenzell Innerrhoden', 'Basel-Landschaft', 'Basel-Stadt', 'Bern', 'Freiburg', 'Genf', 'Glarus', 'Graubünden', 'Jura', 'Luzern', 'Neuenburg', 'Nidwalden', 'Obwalden', 'Schaffhausen', 'Schwyz', 'Solothurn', 'St. Gallen', 'Tessin', 'Thurgau', 'Uri', 'Waadt', 'Wallis', 'Zug', 'Zürich' ),
	);
}

/**
 * Felder eines Eintrags. „wahl“: der Einsender entscheidet, ob der Wert öffentlich gezeigt werden darf.
 *
 * @return array<string,array{label:string,typ:string,max:int,pflicht:bool,wahl:bool}>
 */
function tamil_site_vz_felder(): array {
	$f = static function ( string $label, string $typ, int $max, bool $pflicht = false, bool $wahl = false ): array {
		return array(
			'label'   => $label,
			'typ'     => $typ,
			'max'     => $max,
			'pflicht' => $pflicht,
			'wahl'    => $wahl,
		);
	};
	return array(
		'name'              => $f( __( 'Name', 'tamil-site' ), 'text', 200, true ),
		'art'               => $f( __( 'Art', 'tamil-site' ), 'art', 20, true ),
		'kategorie'         => $f( __( 'Kategorie', 'tamil-site' ), 'kategorie', 200 ),
		'beschreibung'      => $f( __( 'Kurze Beschreibung', 'tamil-site' ), 'textarea', TAMIL_SITE_VZ_BESCHREIBUNG_MAX ),
		'adresse'           => $f( __( 'Straße und Hausnummer', 'tamil-site' ), 'text', 200, false, true ),
		'plz'               => $f( __( 'PLZ', 'tamil-site' ), 'plz', 10, true ),
		'stadt'             => $f( __( 'Stadt', 'tamil-site' ), 'text', 100, true ),
		'land'              => $f( __( 'Land', 'tamil-site' ), 'land', 2, true ),
		'bundesland_kanton' => $f( __( 'Bundesland oder Kanton', 'tamil-site' ), 'region', 60 ),
		'telefon'           => $f( __( 'Telefon', 'tamil-site' ), 'telefon', 40, false, true ),
		'email'             => $f( __( 'E-Mail', 'tamil-site' ), 'email', 200, false, true ),
		'website'           => $f( __( 'Website', 'tamil-site' ), 'url', 300, false, true ),
		'oeffnungszeiten'   => $f( __( 'Öffnungszeiten', 'tamil-site' ), 'textarea', 300, false, true ),
	);
}

/**
 * Kontaktwege (mindestens einer ist für einen Eintrag nötig).
 *
 * @return array<int,string>
 */
function tamil_site_vz_kontaktwege(): array {
	return array( 'telefon', 'email', 'website' );
}

/**
 * Status der Einsendungen → Beschriftung.
 *
 * @return array<string,string>
 */
function tamil_site_vz_einsendung_status_liste(): array {
	return array(
		'neu'         => __( 'neu', 'tamil-site' ),
		'geprueft'    => __( 'geprüft', 'tamil-site' ),
		'freigegeben' => __( 'freigegeben', 'tamil-site' ),
		'abgelehnt'   => __( 'abgelehnt', 'tamil-site' ),
	);
}

function tamil_site_vz_tabelle(): string {
	global $wpdb;
	return $wpdb->prefix . 'tamil_vz_einsendungen';
}

function tamil_site_vz_protokoll_tabelle(): string {
	global $wpdb;
	return $wpdb->prefix . 'tamil_vz_protokoll';
}

/**
 * Beitragstyp und Taxonomie (immer registriert, damit die Verwaltung arbeiten kann; öffentlich sichtbar nur mit
 * eingeschaltetem Schalter, siehe verzeichnis-ansicht.php).
 */
function tamil_site_vz_registrieren(): void {
	register_post_type(
		TAMIL_SITE_VZ_TYP,
		array(
			'labels'              => array(
				'name'          => __( 'Verzeichnis', 'tamil-site' ),
				'singular_name' => __( 'Verzeichnis-Eintrag', 'tamil-site' ),
				'add_new_item'  => __( 'Eintrag anlegen', 'tamil-site' ),
				'edit_item'     => __( 'Eintrag bearbeiten', 'tamil-site' ),
			),
			'public'              => true,
			'exclude_from_search' => true,
			'show_in_rest'        => false,
			'has_archive'         => false,
			'menu_icon'           => 'dashicons-store',
			'supports'            => array( 'title', 'editor', 'thumbnail' ),
			'capability_type'     => array( 'tamil_vz_eintrag', 'tamil_vz_eintraege' ),
			'map_meta_cap'        => true,
			'rewrite'             => array(
				'slug'       => 'verzeichnis',
				'with_front' => false,
			),
		)
	);
	register_taxonomy(
		TAMIL_SITE_VZ_KATEGORIE,
		TAMIL_SITE_VZ_TYP,
		array(
			'labels'            => array(
				'name'          => __( 'Verzeichnis-Kategorien', 'tamil-site' ),
				'singular_name' => __( 'Verzeichnis-Kategorie', 'tamil-site' ),
			),
			'public'            => false,
			'show_ui'           => true,
			'show_in_rest'      => false,
			'show_admin_column' => true,
			'hierarchical'      => false,
			'meta_box_cb'       => false,
			'capabilities'      => array(
				'manage_terms' => 'manage_categories',
				'edit_terms'   => 'manage_categories',
				'delete_terms' => 'manage_categories',
				'assign_terms' => 'edit_tamil_vz_eintraege',
			),
		)
	);
}
add_action( 'init', 'tamil_site_vz_registrieren', 6 );

/**
 * Rechte am Beitragstyp für Administrator und Redaktion. Die Rolle „radar“ bekommt sie nicht: sie schreibt nur über
 * die eigenen REST-Routen (Recht tamil_verzeichnis_pflegen).
 *
 * @return array<int,string>
 */
function tamil_site_vz_rechte_redaktion(): array {
	$rechte = array();
	foreach ( array( 'edit', 'edit_others', 'publish', 'read_private', 'delete', 'delete_others', 'delete_published', 'delete_private', 'edit_published', 'edit_private' ) as $teil ) {
		$rechte[] = $teil . '_tamil_vz_eintraege';
	}
	return $rechte;
}

/**
 * Upgrade-Schritt (Datenversion 4): Tabellen über dbDelta, Kategorien aus dem Vorschlag (nur fehlende), Seite
 * „Verzeichnis“ als Entwurf mit dem Shortcode (nur wenn es sie nicht gibt). Idempotent.
 */
function tamil_site_vz_upgrade(): void {
	global $wpdb;
	require_once ABSPATH . 'wp-admin/includes/upgrade.php';
	$charset = $wpdb->get_charset_collate();
	$t       = tamil_site_vz_tabelle();
	$p       = tamil_site_vz_protokoll_tabelle();
	dbDelta(
		"CREATE TABLE {$t} (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  vorgangsnummer varchar(20) NOT NULL,
  typ varchar(20) NOT NULL,
  eintrag_id bigint(20) unsigned NOT NULL DEFAULT 0,
  status varchar(20) NOT NULL DEFAULT 'neu',
  eingang_at datetime NOT NULL,
  abgeschlossen_at datetime DEFAULT NULL,
  einsender_name varchar(200) NOT NULL,
  einsender_email varchar(200) NOT NULL,
  berechtigung varchar(20) NOT NULL,
  felder longtext NOT NULL,
  anmerkung text NOT NULL,
  einwilligung tinyint(1) NOT NULL DEFAULT 0,
  einwilligung_fassung varchar(40) NOT NULL DEFAULT '',
  pruefung longtext NOT NULL,
  entscheidung longtext NOT NULL,
  ip_hash varchar(64) DEFAULT NULL,
  PRIMARY KEY  (id),
  UNIQUE KEY vorgangsnummer (vorgangsnummer),
  KEY status (status),
  KEY eingang (eingang_at),
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
  eintrag_id bigint(20) unsigned NOT NULL DEFAULT 0,
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
	tamil_site_vz_registrieren();
	foreach ( tamil_site_vz_kategorien_vorschlag() as $art => $namen ) {
		foreach ( $namen as $name ) {
			$slug = sanitize_title( $art . '-' . $name );
			if ( term_exists( $slug, TAMIL_SITE_VZ_KATEGORIE ) ) {
				continue;
			}
			$term = wp_insert_term(
				$name,
				TAMIL_SITE_VZ_KATEGORIE,
				array( 'slug' => $slug )
			);
			if ( is_wp_error( $term ) ) {
				throw new RuntimeException( 'Kategorie ' . esc_html( $slug ) . ': ' . esc_html( $term->get_error_message() ) );
			}
			update_term_meta( (int) $term['term_id'], 'tamil_vz_art', $art );
		}
	}
	if ( ! get_page_by_path( 'verzeichnis', OBJECT, 'page' ) ) {
		$id = wp_insert_post(
			array(
				'post_type'    => 'page',
				'post_status'  => 'draft',
				'post_title'   => __( 'Verzeichnis', 'tamil-site' ),
				'post_name'    => 'verzeichnis',
				'post_content' => '[tamil_verzeichnis]',
			),
			true
		);
		if ( is_wp_error( $id ) ) {
			throw new RuntimeException( 'Seite verzeichnis: ' . esc_html( $id->get_error_message() ) );
		}
	}
	flush_rewrite_rules( false );
}

// Anmeldung bei der Upgrade-Routine (includes/upgrade.php).
tamil_site_upgrade_schritt( 4, 'verzeichnis', 'tamil_site_vz_upgrade' );
tamil_site_rechte_anmelden( 'radar', array( 'tamil_verzeichnis_pflegen' ) );
tamil_site_rechte_anmelden( 'administrator', tamil_site_vz_rechte_redaktion() );
tamil_site_rechte_anmelden( 'editor', tamil_site_vz_rechte_redaktion() );

/**
 * Jetzt in UTC im Datenbankformat.
 */
function tamil_site_vz_jetzt(): string {
	return gmdate( 'Y-m-d H:i:s' );
}

/**
 * Datenbankzeit (UTC) → ISO 8601, null bei leer.
 *
 * @param string|null $wert Datenbankwert.
 */
function tamil_site_vz_iso( ?string $wert ): ?string {
	if ( null === $wert || '' === $wert ) {
		return null;
	}
	return gmdate( 'c', (int) strtotime( $wert . ' UTC' ) );
}

/**
 * Protokollzeile ohne Personendaten.
 *
 * @param string $aktion  z. B. eingang, status, angelegt, geaendert, entfernt, loeschfrist.
 * @param string $vorgang Vorgangsnummer oder leer.
 * @param int    $eintrag Eintrag oder 0.
 * @param string $notiz   Kurzer Grund oder Feldnamen, keine Inhalte.
 */
function tamil_site_vz_protokoll( string $aktion, string $vorgang = '', int $eintrag = 0, string $notiz = '', string $wer = '' ): void {
	global $wpdb;
	if ( '' === $wer ) {
		$wer = is_user_logged_in() ? wp_get_current_user()->user_login : 'website';
	}
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery -- eigene Tabelle
	$wpdb->insert(
		tamil_site_vz_protokoll_tabelle(),
		array(
			'ts'             => tamil_site_vz_jetzt(),
			'wer'            => substr( $wer, 0, 60 ),
			'aktion'         => substr( $aktion, 0, 30 ),
			'vorgangsnummer' => substr( $vorgang, 0, 20 ),
			'eintrag_id'     => $eintrag,
			'notiz'          => substr( $notiz, 0, 300 ),
		)
	);
}

/**
 * Bereinigt und prüft Feldwerte eines Eintrags.
 *
 * @param array<string,mixed> $roh          Werte (ungeschlüpft, unbereinigt). Unbekannte Schlüssel werden ignoriert.
 * @param string              $land_vorgabe Land, falls $roh keines enthält (für PLZ und Bundesland bei Teiländerungen).
 * @return array{werte:array<string,string>,fehler:array<string,string>}
 */
function tamil_site_vz_werte_pruefen( array $roh, string $land_vorgabe = '' ): array {
	$werte  = array();
	$fehler = array();
	foreach ( tamil_site_vz_felder() as $key => $feld ) {
		if ( ! array_key_exists( $key, $roh ) ) {
			continue;
		}
		if ( ! is_scalar( $roh[ $key ] ) && null !== $roh[ $key ] ) {
			$fehler[ $key ] = __( 'Ungültiger Wert.', 'tamil-site' );
			continue;
		}
		$wert = 'textarea' === $feld['typ'] ? sanitize_textarea_field( (string) $roh[ $key ] ) : sanitize_text_field( (string) $roh[ $key ] );
		$wert = trim( $wert );
		if ( mb_strlen( $wert ) > $feld['max'] ) {
			/* translators: %d: Höchstzahl der Zeichen */
			$fehler[ $key ] = sprintf( __( 'Höchstens %d Zeichen.', 'tamil-site' ), $feld['max'] );
		}
		$werte[ $key ] = $wert;
	}
	$land = $werte['land'] ?? $land_vorgabe;
	foreach ( $werte as $key => $wert ) {
		if ( '' === $wert || isset( $fehler[ $key ] ) ) {
			continue;
		}
		switch ( tamil_site_vz_felder()[ $key ]['typ'] ) {
			case 'art':
				if ( ! array_key_exists( $wert, tamil_site_vz_arten() ) ) {
					$fehler[ $key ] = __( 'Bitte eine der vier Arten wählen.', 'tamil-site' );
				}
				break;
			case 'land':
				$wert          = strtoupper( $wert );
				$werte[ $key ] = $wert;
				if ( ! array_key_exists( $wert, tamil_site_vz_laender() ) ) {
					$fehler[ $key ] = __( 'Bitte Deutschland, Österreich oder die Schweiz wählen.', 'tamil-site' );
				}
				break;
			case 'plz':
				$muster = 'DE' === $land ? '/^\d{5}$/' : '/^\d{4}$/';
				if ( '' !== $land && ! preg_match( $muster, $wert ) ) {
					$fehler[ $key ] = 'DE' === $land ? __( 'Die PLZ hat in Deutschland fünf Ziffern.', 'tamil-site' ) : __( 'Die PLZ hat in Österreich und der Schweiz vier Ziffern.', 'tamil-site' );
				}
				break;
			case 'region':
				if ( '' !== $land && ! in_array( $wert, tamil_site_vz_regionen()[ $land ] ?? array(), true ) ) {
					$fehler[ $key ] = __( 'Bitte ein Bundesland oder einen Kanton aus der Liste wählen.', 'tamil-site' );
				}
				break;
			case 'telefon':
				if ( ! preg_match( '/^\+?[0-9][0-9 ()\/\-]{4,24}$/', $wert ) ) {
					$fehler[ $key ] = __( 'Bitte eine Telefonnummer aus Ziffern angeben, gern mit +49 oder Vorwahl.', 'tamil-site' );
				}
				break;
			case 'email':
				if ( ! is_email( $wert ) ) {
					$fehler[ $key ] = __( 'Bitte eine gültige E-Mail-Adresse angeben.', 'tamil-site' );
				}
				break;
			case 'url':
				$url = esc_url_raw( $wert, array( 'http', 'https' ) );
				if ( '' === $url || ! filter_var( $url, FILTER_VALIDATE_URL ) || ! str_contains( (string) wp_parse_url( $url, PHP_URL_HOST ), '.' ) ) { // ohne DNS-Abfrage
					$fehler[ $key ] = __( 'Bitte die Adresse der Website mit https:// angeben.', 'tamil-site' );
				} else {
					$werte[ $key ] = $url;
				}
				break;
			case 'kategorie':
				$term = get_term_by( 'slug', $wert, TAMIL_SITE_VZ_KATEGORIE );
				$art  = $werte['art'] ?? '';
				if ( ! $term || ( '' !== $art && get_term_meta( $term->term_id, 'tamil_vz_art', true ) !== $art ) ) {
					$fehler[ $key ] = __( 'Diese Kategorie gibt es für diese Art nicht.', 'tamil-site' );
				}
				break;
		}
	}
	return array(
		'werte'  => $werte,
		'fehler' => $fehler,
	);
}

/**
 * Pflichtfelder, die in vollständigen Werten fehlen (Name, Art, PLZ, Stadt, Land, mindestens ein Kontaktweg).
 *
 * @param array<string,string> $werte Werte.
 * @return array<int,string> Feldnamen; „kontakt“ für den fehlenden Kontaktweg.
 */
function tamil_site_vz_fehlt( array $werte ): array {
	$fehlt = array();
	foreach ( tamil_site_vz_felder() as $key => $feld ) {
		if ( $feld['pflicht'] && '' === (string) ( $werte[ $key ] ?? '' ) ) {
			$fehlt[] = $key;
		}
	}
	$kontakt = array_filter(
		tamil_site_vz_kontaktwege(),
		static function ( $k ) use ( $werte ) {
			return '' !== (string) ( $werte[ $k ] ?? '' );
		}
	);
	if ( ! $kontakt ) {
		$fehlt[] = 'kontakt';
	}
	return $fehlt;
}

/**
 * Name für den Vergleich (klein, ohne Rechtsform und Zeichen).
 */
function tamil_site_vz_name_norm( string $name ): string {
	$name = remove_accents( mb_strtolower( $name ) );
	$name = preg_replace( '/\b(e\.?\s?v\.?|gmbh|ug|ag|ohg|kg)\b/u', ' ', $name );
	return (string) preg_replace( '/[^a-z0-9]+/', '', (string) $name );
}

/**
 * Telefonnummer für den Vergleich (nur Ziffern, führende 0 → Landesvorwahl 49/43/41 bleibt unbekannt, daher
 * nur die letzten neun Ziffern).
 */
function tamil_site_vz_telefon_norm( string $telefon ): string {
	$ziffern = (string) preg_replace( '/\D+/', '', $telefon );
	return strlen( $ziffern ) > 9 ? substr( $ziffern, -9 ) : $ziffern;
}

/**
 * Host einer Website für den Vergleich (ohne www).
 */
function tamil_site_vz_website_host( string $url ): string {
	$host = (string) wp_parse_url( $url, PHP_URL_HOST );
	return (string) preg_replace( '/^www\./', '', strtolower( $host ) );
}

/**
 * Mögliche Dubletten nach festen Regeln: ähnlicher Name und dazu gleiche PLZ, Telefonnummer oder Website.
 *
 * @param array<string,string> $werte  Werte der Einsendung.
 * @param int                  $ausser Eintrag, der nicht mitzählt (bei Änderungen der eigene).
 * @return array<int,array{eintrag_id:int,grund:string}>
 */
function tamil_site_vz_dubletten( array $werte, int $ausser = 0 ): array {
	$name = tamil_site_vz_name_norm( (string) ( $werte['name'] ?? '' ) );
	if ( '' === $name ) {
		return array();
	}
	$oder = array( 'relation' => 'OR' );
	if ( '' !== (string) ( $werte['plz'] ?? '' ) ) {
		$oder[] = array(
			'key'   => '_tamil_vz_plz',
			'value' => $werte['plz'],
		);
	}
	$tel = tamil_site_vz_telefon_norm( (string) ( $werte['telefon'] ?? '' ) );
	if ( '' !== $tel ) {
		$oder[] = array(
			'key'   => '_tamil_vz_telefon_norm',
			'value' => $tel,
		);
	}
	$host = tamil_site_vz_website_host( (string) ( $werte['website'] ?? '' ) );
	if ( '' !== $host ) {
		$oder[] = array(
			'key'   => '_tamil_vz_website_host',
			'value' => $host,
		);
	}
	if ( count( $oder ) < 2 ) {
		return array();
	}
	$ids     = get_posts(
		array(
			'post_type'        => TAMIL_SITE_VZ_TYP,
			'post_status'      => array( 'publish', 'draft', 'pending', 'private' ),
			'posts_per_page'   => 50,
			'fields'           => 'ids',
			'meta_query'       => $oder, // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query -- kleine Menge, nur bei Einsendungen
			'suppress_filters' => true,
		)
	);
	$treffer = array();
	foreach ( $ids as $id ) {
		$id = (int) $id;
		if ( $id === $ausser ) {
			continue;
		}
		$anderer = tamil_site_vz_name_norm( get_the_title( $id ) );
		similar_text( $name, $anderer, $prozent );
		$aehnlich = $prozent >= 80 || ( strlen( $anderer ) >= 4 && ( str_contains( $name, $anderer ) || str_contains( $anderer, $name ) ) );
		if ( ! $aehnlich ) {
			continue;
		}
		$gruende = array();
		if ( '' !== (string) ( $werte['plz'] ?? '' ) && get_post_meta( $id, '_tamil_vz_plz', true ) === $werte['plz'] ) {
			$gruende[] = 'plz';
		}
		if ( '' !== $tel && get_post_meta( $id, '_tamil_vz_telefon_norm', true ) === $tel ) {
			$gruende[] = 'telefon';
		}
		if ( '' !== $host && get_post_meta( $id, '_tamil_vz_website_host', true ) === $host ) {
			$gruende[] = 'website';
		}
		$treffer[] = array(
			'eintrag_id' => $id,
			'grund'      => 'name+' . implode( '+', $gruende ),
		);
	}
	return $treffer;
}

/**
 * Felder eines Eintrags lesen (alle Status).
 *
 * @return array<string,string>|null
 */
function tamil_site_vz_eintrag_werte( int $id ): ?array {
	$post = get_post( $id );
	if ( ! $post instanceof WP_Post || TAMIL_SITE_VZ_TYP !== $post->post_type || 'trash' === $post->post_status ) {
		return null;
	}
	$werte = array();
	foreach ( array_keys( tamil_site_vz_felder() ) as $key ) {
		$werte[ $key ] = (string) get_post_meta( $id, '_tamil_vz_' . $key, true );
	}
	$werte['name']         = $post->post_title;
	$werte['beschreibung'] = $post->post_content;
	$terms                 = wp_get_object_terms( $id, TAMIL_SITE_VZ_KATEGORIE, array( 'fields' => 'slugs' ) );
	$werte['kategorie']    = is_array( $terms ) && $terms ? (string) $terms[0] : '';
	return $werte;
}

/**
 * Status eines Eintrags nach außen: veroeffentlicht oder entfernt.
 */
function tamil_site_vz_eintrag_status( int $id ): string {
	return 'publish' === get_post_status( $id ) ? 'veroeffentlicht' : 'entfernt';
}

/**
 * Prüfsumme über Felder und Status (für die Änderung nur gegen den gelesenen Stand). Premium zählt nicht mit.
 */
function tamil_site_vz_stand( int $id ): string {
	$werte = tamil_site_vz_eintrag_werte( $id );
	return null === $werte ? '' : substr( hash( 'sha256', (string) wp_json_encode( array( $werte, tamil_site_vz_eintrag_status( $id ) ) ) ), 0, 16 );
}

function tamil_site_vz_premium( int $id ): bool {
	return '1' === (string) get_post_meta( $id, '_tamil_vz_premium', true );
}

/**
 * Eintrag für die Schnittstelle.
 *
 * @return array<string,mixed>|null
 */
function tamil_site_vz_eintrag_ausgabe( int $id ): ?array {
	$werte = tamil_site_vz_eintrag_werte( $id );
	if ( null === $werte ) {
		return null;
	}
	return array(
		'id'        => $id,
		'felder'    => $werte,
		'premium'   => tamil_site_vz_premium( $id ),
		'status'    => tamil_site_vz_eintrag_status( $id ),
		'stand'     => tamil_site_vz_stand( $id ),
		'link'      => 'publish' === get_post_status( $id ) ? (string) get_permalink( $id ) : '',
		'geaendert' => tamil_site_vz_iso( (string) get_post_field( 'post_modified_gmt', $id ) ),
	);
}

/**
 * Einträge ab Cursor (aufsteigend nach id, alle Status außer Papierkorb) – für die Dublettenprüfung im Radar.
 *
 * @return array{eintraege:array<int,array<string,mixed>>,naechster:int}
 */
function tamil_site_vz_eintraege_liste( int $nach, int $anzahl ): array {
	global $wpdb;
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- Cursor über ID
	$ids  = $wpdb->get_col( $wpdb->prepare( "SELECT ID FROM {$wpdb->posts} WHERE post_type = %s AND post_status IN ('publish','draft','pending','private') AND ID > %d ORDER BY ID ASC LIMIT %d", TAMIL_SITE_VZ_TYP, $nach, $anzahl ) );
	$out  = array();
	$last = $nach;
	foreach ( $ids as $id ) {
		$eintrag = tamil_site_vz_eintrag_ausgabe( (int) $id );
		if ( $eintrag ) {
			$out[] = $eintrag;
		}
		$last = (int) $id;
	}
	return array(
		'eintraege' => $out,
		'naechster' => $last,
	);
}

/**
 * Neue Vorgangsnummer (V + Datum + fünf Zeichen ohne Verwechsler).
 */
function tamil_site_vz_vorgangsnummer(): string {
	$zeichen = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
	$teil    = '';
	for ( $i = 0; $i < 5; $i++ ) {
		$teil .= $zeichen[ random_int( 0, strlen( $zeichen ) - 1 ) ];
	}
	return 'V' . gmdate( 'ymd' ) . '-' . $teil;
}

function tamil_site_vz_vorgangsnummer_gueltig( string $wert ): bool {
	return (bool) preg_match( '/^V\d{6}-[A-HJ-NP-Z2-9]{5}$/', $wert );
}

/**
 * Speichert eine Einsendung.
 *
 * @param array{typ:string,eintrag_id:int,einsender_name:string,einsender_email:string,berechtigung:string,felder:array<string,array{wert:string,oeffentlich:bool}>,anmerkung:string,einwilligung_fassung:string,ip_hash:string} $daten Daten.
 * @return string|WP_Error Vorgangsnummer.
 */
function tamil_site_vz_einsendung_speichern( array $daten ) {
	global $wpdb;
	for ( $versuch = 0; $versuch < 5; $versuch++ ) {
		$vorgang = tamil_site_vz_vorgangsnummer();
		// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery -- eigene Tabelle
		$ok = $wpdb->insert(
			tamil_site_vz_tabelle(),
			array(
				'vorgangsnummer'       => $vorgang,
				'typ'                  => $daten['typ'],
				'eintrag_id'           => $daten['eintrag_id'],
				'status'               => 'neu',
				'eingang_at'           => tamil_site_vz_jetzt(),
				'einsender_name'       => $daten['einsender_name'],
				'einsender_email'      => $daten['einsender_email'],
				'berechtigung'         => $daten['berechtigung'],
				'felder'               => (string) wp_json_encode( $daten['felder'] ),
				'anmerkung'            => $daten['anmerkung'],
				'einwilligung'         => 1,
				'einwilligung_fassung' => $daten['einwilligung_fassung'],
				'pruefung'             => '{}',
				'entscheidung'         => '{}',
				'ip_hash'              => $daten['ip_hash'],
			)
		);
		if ( $ok ) {
			tamil_site_vz_protokoll( 'eingang', $vorgang, $daten['eintrag_id'], $daten['typ'], 'website' );
			return $vorgang;
		}
	}
	return new WP_Error( 'tamil_vz_speichern', __( 'Die Einsendung konnte nicht gespeichert werden. Bitte versucht es später noch einmal.', 'tamil-site' ) );
}

/**
 * Zeile einer Einsendung.
 *
 * @return array<string,mixed>|null
 */
function tamil_site_vz_einsendung_zeile( string $vorgang ): ?array {
	global $wpdb;
	$t = tamil_site_vz_tabelle();
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- eigene Tabelle
	$zeile = $wpdb->get_row( $wpdb->prepare( "SELECT * FROM {$t} WHERE vorgangsnummer = %s", $vorgang ), ARRAY_A );
	return is_array( $zeile ) ? $zeile : null;
}

/**
 * Werte einer Einsendung (nur die Werte, ohne „öffentlich“).
 *
 * @param array<string,mixed> $zeile Zeile.
 * @return array<string,string>
 */
function tamil_site_vz_einsendung_werte( array $zeile ): array {
	$felder = json_decode( (string) $zeile['felder'], true );
	$werte  = array();
	foreach ( is_array( $felder ) ? $felder : array() as $key => $feld ) {
		$werte[ (string) $key ] = (string) ( $feld['wert'] ?? '' );
	}
	return $werte;
}

/**
 * Prüfung nach festen Regeln (ohne Modell): fehlende Pflichtfelder, Formfehler, mögliche Dubletten.
 *
 * @param array<string,mixed> $zeile Zeile.
 * @return array{fehlt:array<int,string>,formfehler:array<int,string>,dubletten:array<int,array{eintrag_id:int,grund:string}>}
 */
function tamil_site_vz_regeln( array $zeile ): array {
	$werte = tamil_site_vz_einsendung_werte( $zeile );
	if ( 'neu' !== $zeile['typ'] ) {
		$alt = tamil_site_vz_eintrag_werte( (int) $zeile['eintrag_id'] ) ?? array();
		$neu = array_merge( $alt, $werte );
		return array(
			'fehlt'      => 'entfernen' === $zeile['typ'] ? array() : tamil_site_vz_fehlt( $neu ),
			'formfehler' => array_keys( tamil_site_vz_werte_pruefen( $werte, (string) ( $neu['land'] ?? '' ) )['fehler'] ),
			'dubletten'  => array(),
		);
	}
	return array(
		'fehlt'      => tamil_site_vz_fehlt( $werte ),
		'formfehler' => array_keys( tamil_site_vz_werte_pruefen( $werte )['fehler'] ),
		'dubletten'  => tamil_site_vz_dubletten( $werte ),
	);
}

/**
 * Einsendung für die Schnittstelle.
 *
 * @param array<string,mixed> $zeile Zeile.
 * @return array<string,mixed>
 */
function tamil_site_vz_einsendung_ausgabe( array $zeile ): array {
	$felder = json_decode( (string) $zeile['felder'], true );
	return array(
		'id'             => (int) $zeile['id'],
		'vorgangsnummer' => (string) $zeile['vorgangsnummer'],
		'typ'            => (string) $zeile['typ'],
		'eintrag_id'     => (int) $zeile['eintrag_id'],
		'status'         => (string) $zeile['status'],
		'eingang'        => tamil_site_vz_iso( (string) $zeile['eingang_at'] ),
		'abgeschlossen'  => tamil_site_vz_iso( $zeile['abgeschlossen_at'] ?? null ),
		'einsender'      => array(
			'name'  => (string) $zeile['einsender_name'],
			'email' => (string) $zeile['einsender_email'],
		),
		'berechtigung'   => (string) $zeile['berechtigung'],
		'felder'         => is_array( $felder ) ? (object) $felder : new stdClass(),
		'anmerkung'      => (string) $zeile['anmerkung'],
		'einwilligung'   => array(
			'erteilt' => (bool) $zeile['einwilligung'],
			'fassung' => (string) $zeile['einwilligung_fassung'],
		),
		'regeln'         => tamil_site_vz_regeln( $zeile ),
		'pruefung'       => (object) (array) json_decode( (string) $zeile['pruefung'], true ),
		'entscheidung'   => (object) (array) json_decode( (string) $zeile['entscheidung'], true ),
	);
}

/**
 * Einsendungen ab Cursor (aufsteigend nach id).
 *
 * @return array{einsendungen:array<int,array<string,mixed>>,naechster:int}
 */
function tamil_site_vz_einsendung_liste( int $nach, int $anzahl ): array {
	global $wpdb;
	$t = tamil_site_vz_tabelle();
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- eigene Tabelle
	$zeilen = (array) $wpdb->get_results( $wpdb->prepare( "SELECT * FROM {$t} WHERE id > %d ORDER BY id ASC LIMIT %d", $nach, $anzahl ), ARRAY_A );
	$out    = array();
	$last   = $nach;
	foreach ( $zeilen as $zeile ) {
		$out[] = tamil_site_vz_einsendung_ausgabe( $zeile );
		$last  = (int) $zeile['id'];
	}
	return array(
		'einsendungen' => $out,
		'naechster'    => $last,
	);
}

/**
 * Status einer Einsendung setzen (geprueft, abgelehnt); optional das Prüfergebnis des Agenten ablegen.
 * „freigegeben“ setzt nur die Freigabe selbst (tamil_site_vz_freigabe). Atomar über die Bedingung im UPDATE.
 *
 * @param array<string,mixed>|null $pruefung Prüfergebnis (fehlt, formfehler, dubletten, kategorie_vorschlag, unterschied).
 * @return array<string,mixed>|WP_Error
 */
function tamil_site_vz_einsendung_status_setzen( string $vorgang, string $status, ?array $pruefung = null ) {
	global $wpdb;
	$erlaubt = array(
		'geprueft'  => array( 'neu', 'geprueft' ),
		'abgelehnt' => array( 'neu', 'geprueft' ),
	);
	if ( ! isset( $erlaubt[ $status ] ) ) {
		return new WP_Error( 'tamil_vz_status', __( 'Dieser Status lässt sich hier nicht setzen.', 'tamil-site' ), array( 'status' => 400 ) );
	}
	$zeile = tamil_site_vz_einsendung_zeile( $vorgang );
	if ( ! $zeile ) {
		return new WP_Error( 'tamil_vz_einsendung_fehlt', __( 'Einsendung nicht gefunden.', 'tamil-site' ), array( 'status' => 404 ) );
	}
	$t      = tamil_site_vz_tabelle();
	$setzen = $wpdb->prepare( 'status = %s', $status );
	if ( 'abgelehnt' === $status ) {
		$setzen .= $wpdb->prepare( ', abgeschlossen_at = %s', tamil_site_vz_jetzt() );
	}
	if ( null !== $pruefung ) {
		$setzen .= $wpdb->prepare( ', pruefung = %s', (string) wp_json_encode( $pruefung ) );
	}
	$alt = $erlaubt[ $status ];
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.PreparedSQL.InterpolatedNotPrepared, WordPress.DB.PreparedSQL.NotPrepared -- eigene Tabelle, $setzen ist vorbereitet
	$geaendert = (int) $wpdb->query( $wpdb->prepare( "UPDATE {$t} SET {$setzen} WHERE id = %d AND status IN (%s, %s)", (int) $zeile['id'], $alt[0], $alt[1] ) );
	if ( 1 !== $geaendert ) {
		$jetzt = tamil_site_vz_einsendung_zeile( $vorgang );
		return new WP_Error(
			'tamil_vz_status_konflikt',
			/* translators: %s: aktueller Status */
			sprintf( __( 'Die Einsendung steht auf „%s“ und lässt sich nicht mehr ändern.', 'tamil-site' ), (string) ( $jetzt['status'] ?? '' ) ),
			array( 'status' => 409 )
		);
	}
	tamil_site_vz_protokoll( 'status', $vorgang, (int) $zeile['eintrag_id'], $status );
	return tamil_site_vz_einsendung_ausgabe( (array) tamil_site_vz_einsendung_zeile( $vorgang ) );
}

/**
 * Sperre je Eintrag gegen gleichzeitige Änderungen (atomar über den eindeutigen Optionsnamen).
 */
function tamil_site_vz_sperren( int $id ): bool {
	global $wpdb;
	$name = 'tamil_vz_sperre_' . $id;
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- atomare Sperre
	$alt = $wpdb->get_var( $wpdb->prepare( "SELECT option_value FROM {$wpdb->options} WHERE option_name = %s", $name ) );
	if ( null !== $alt && time() - (int) $alt > 60 ) {
		// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- liegengebliebene Sperre
		$wpdb->delete(
			$wpdb->options,
			array(
				'option_name'  => $name,
				'option_value' => $alt,
			)
		);
	}
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- atomare Sperre
	return 1 === (int) $wpdb->query( $wpdb->prepare( "INSERT IGNORE INTO {$wpdb->options} (option_name, option_value, autoload) VALUES (%s, %s, 'off')", $name, (string) time() ) );
}

function tamil_site_vz_entsperren( int $id ): void {
	global $wpdb;
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- Gegenstück zur Sperre
	$wpdb->delete( $wpdb->options, array( 'option_name' => 'tamil_vz_sperre_' . $id ) );
	wp_cache_delete( 'tamil_vz_sperre_' . $id, 'options' );
	wp_cache_delete( 'notoptions', 'options' );
}

/**
 * Schreibt Werte in einen Eintrag (Titel, Inhalt, Meta, Kategorie, abgeleitete Vergleichswerte).
 *
 * @param array<string,string> $werte Nur die zu schreibenden Felder.
 * @return int|WP_Error ID.
 */
function tamil_site_vz_eintrag_schreiben( int $id, array $werte, string $post_status = '' ) {
	$post = array( 'post_type' => TAMIL_SITE_VZ_TYP );
	if ( $id ) {
		$post['ID'] = $id;
	}
	if ( array_key_exists( 'name', $werte ) ) {
		$post['post_title'] = $werte['name'];
	}
	if ( array_key_exists( 'beschreibung', $werte ) ) {
		$post['post_content'] = $werte['beschreibung'];
	}
	if ( '' !== $post_status ) {
		$post['post_status'] = $post_status;
	}
	$neu = $id ? wp_update_post( wp_slash( $post ), true ) : wp_insert_post( wp_slash( $post ), true );
	if ( is_wp_error( $neu ) ) {
		return $neu;
	}
	$neu = (int) $neu;
	foreach ( $werte as $key => $wert ) {
		if ( in_array( $key, array( 'name', 'beschreibung', 'kategorie' ), true ) ) {
			continue;
		}
		update_post_meta( $neu, '_tamil_vz_' . $key, wp_slash( $wert ) );
	}
	if ( array_key_exists( 'kategorie', $werte ) ) {
		wp_set_object_terms( $neu, '' === $werte['kategorie'] ? array() : array( $werte['kategorie'] ), TAMIL_SITE_VZ_KATEGORIE );
	}
	if ( ! $id ) {
		update_post_meta( $neu, '_tamil_vz_premium', '0' );
	}
	update_post_meta( $neu, '_tamil_vz_telefon_norm', tamil_site_vz_telefon_norm( (string) get_post_meta( $neu, '_tamil_vz_telefon', true ) ) );
	update_post_meta( $neu, '_tamil_vz_website_host', tamil_site_vz_website_host( (string) get_post_meta( $neu, '_tamil_vz_website', true ) ) );
	return $neu;
}

/**
 * Freigabe aus dem Radar: legt einen Eintrag an, ändert ihn oder entfernt ihn – mit genau den übergebenen Werten.
 *
 * Regeln: Jede Freigabe gehört zu genau einer Einsendung (Typ passend, nicht abgelehnt) und wirkt genau einmal;
 * eine wiederholte Freigabe derselben Einsendung liefert das frühere Ergebnis. Unbekannte Felder und „premium“
 * werden abgewiesen. Änderungen nur gegen den gelesenen Stand. Werte, die der Einsender als nicht öffentlich
 * markiert hat, werden nicht veröffentlicht. Der Eintrag muss danach vollständig sein.
 *
 * @param string              $aktion  anlegen, aendern, entfernen.
 * @param string              $vorgang Vorgangsnummer der Einsendung.
 * @param int                 $id      Eintrag (bei aendern, entfernen).
 * @param array<string,mixed> $felder  Freigegebene Werte.
 * @param string              $stand   Gelesener Stand (bei aendern, entfernen).
 * @return array<string,mixed>|WP_Error
 */
function tamil_site_vz_freigabe( string $aktion, string $vorgang, int $id, array $felder, string $stand ) {
	global $wpdb;
	$typ   = array(
		'anlegen'   => 'neu',
		'aendern'   => 'aenderung',
		'entfernen' => 'entfernen',
	)[ $aktion ] ?? '';
	$zeile = tamil_site_vz_einsendung_zeile( $vorgang );
	if ( ! $zeile ) {
		return new WP_Error( 'tamil_vz_einsendung_fehlt', __( 'Einsendung nicht gefunden.', 'tamil-site' ), array( 'status' => 404 ) );
	}
	if ( $zeile['typ'] !== $typ || ( 'anlegen' !== $aktion && (int) $zeile['eintrag_id'] !== $id ) ) {
		return new WP_Error( 'tamil_vz_falsche_einsendung', __( 'Die Einsendung passt nicht zu dieser Freigabe (Typ oder Eintrag).', 'tamil-site' ), array( 'status' => 409 ) );
	}
	if ( 'freigegeben' === $zeile['status'] ) {
		$fertig = (int) $zeile['eintrag_id'];
		if ( 'anlegen' === $aktion && ! $fertig ) {
			return new WP_Error( 'tamil_vz_in_arbeit', __( 'Diese Freigabe läuft gerade.', 'tamil-site' ), array( 'status' => 409 ) );
		}
		return array(
			'bereits'    => true,
			'eintrag'    => tamil_site_vz_eintrag_ausgabe( $fertig ),
			'einsendung' => tamil_site_vz_einsendung_ausgabe( $zeile ),
		);
	}
	if ( 'abgelehnt' === $zeile['status'] ) {
		return new WP_Error( 'tamil_vz_abgelehnt', __( 'Die Einsendung ist abgelehnt.', 'tamil-site' ), array( 'status' => 409 ) );
	}

	$unbekannt = array_diff( array_keys( $felder ), array_keys( tamil_site_vz_felder() ) );
	if ( in_array( 'premium', $unbekannt, true ) ) {
		return new WP_Error( 'tamil_vz_premium_verboten', __( 'Premium setzt nur ein Administrator in WordPress.', 'tamil-site' ), array( 'status' => 403 ) );
	}
	if ( $unbekannt ) {
		return new WP_Error(
			'tamil_vz_unbekannte_felder',
			__( 'Unbekannte Felder.', 'tamil-site' ),
			array(
				'status' => 400,
				'felder' => array_values( $unbekannt ),
			)
		);
	}
	if ( 'entfernen' === $aktion && $felder ) {
		return new WP_Error( 'tamil_vz_unbekannte_felder', __( 'Beim Entfernen werden keine Felder geschrieben.', 'tamil-site' ), array( 'status' => 400 ) );
	}
	$alt = array();
	if ( 'anlegen' !== $aktion ) {
		$alt = tamil_site_vz_eintrag_werte( $id );
		if ( null === $alt ) {
			return new WP_Error( 'tamil_vz_eintrag_fehlt', __( 'Eintrag nicht gefunden.', 'tamil-site' ), array( 'status' => 404 ) );
		}
	}
	$gepr = tamil_site_vz_werte_pruefen( $felder, (string) ( $alt['land'] ?? '' ) );
	if ( $gepr['fehler'] ) {
		return new WP_Error(
			'tamil_vz_ungueltig',
			__( 'Ungültige Werte.', 'tamil-site' ),
			array(
				'status' => 400,
				'fehler' => $gepr['fehler'],
			)
		);
	}
	$werte  = $gepr['werte'];
	$gesamt = array_merge( $alt, $werte );
	if ( 'entfernen' !== $aktion ) {
		$fehlt = tamil_site_vz_fehlt( $gesamt );
		if ( $fehlt ) {
			return new WP_Error(
				'tamil_vz_unvollstaendig',
				__( 'Der Eintrag wäre unvollständig.', 'tamil-site' ),
				array(
					'status' => 400,
					'fehlt'  => $fehlt,
				)
			);
		}
		if ( isset( $werte['plz'] ) || isset( $werte['land'] ) || isset( $werte['bundesland_kanton'] ) ) {
			$ganz = tamil_site_vz_werte_pruefen( array_intersect_key( $gesamt, array_flip( array( 'plz', 'land', 'bundesland_kanton' ) ) ) );
			if ( $ganz['fehler'] ) {
				return new WP_Error(
					'tamil_vz_ungueltig',
					__( 'Ungültige Werte.', 'tamil-site' ),
					array(
						'status' => 400,
						'fehler' => $ganz['fehler'],
					)
				);
			}
		}
		$eingesandt = json_decode( (string) $zeile['felder'], true );
		foreach ( is_array( $eingesandt ) ? $eingesandt : array() as $key => $feld ) {
			if ( isset( $werte[ $key ] ) && '' !== $werte[ $key ] && empty( $feld['oeffentlich'] ) && ( tamil_site_vz_felder()[ $key ]['wahl'] ?? false ) && trim( (string) ( $feld['wert'] ?? '' ) ) === $werte[ $key ] ) {
				return new WP_Error(
					'tamil_vz_nicht_oeffentlich',
					__( 'Der Einsender hat diesen Wert nicht zur Veröffentlichung freigegeben.', 'tamil-site' ),
					array(
						'status' => 409,
						'feld'   => $key,
					)
				);
			}
		}
	}

	if ( 'anlegen' !== $aktion && ! tamil_site_vz_sperren( $id ) ) {
		return new WP_Error( 'tamil_vz_gesperrt', __( 'Der Eintrag wird gerade geändert.', 'tamil-site' ), array( 'status' => 409 ) );
	}
	try {
		if ( 'anlegen' !== $aktion && ! hash_equals( tamil_site_vz_stand( $id ), $stand ) ) {
			return new WP_Error(
				'tamil_vz_stand',
				__( 'Der Eintrag hat sich seit dem Lesen geändert.', 'tamil-site' ),
				array(
					'status' => 409,
					'stand'  => tamil_site_vz_stand( $id ),
				)
			);
		}
		$t = tamil_site_vz_tabelle();
		// Einsendung beanspruchen: nur eine Freigabe gewinnt.
		// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- eigene Tabelle
		$beansprucht = (int) $wpdb->query( $wpdb->prepare( "UPDATE {$t} SET status = 'freigegeben', abgeschlossen_at = %s WHERE id = %d AND status IN ('neu','geprueft')", tamil_site_vz_jetzt(), (int) $zeile['id'] ) );
		if ( 1 !== $beansprucht ) {
			return new WP_Error( 'tamil_vz_in_arbeit', __( 'Diese Einsendung wurde gerade anders entschieden.', 'tamil-site' ), array( 'status' => 409 ) );
		}
		if ( 'entfernen' === $aktion ) {
			$ergebnis = tamil_site_vz_eintrag_schreiben( $id, array(), 'draft' );
		} else {
			$ergebnis = tamil_site_vz_eintrag_schreiben( $id, $werte, 'anlegen' === $aktion ? 'publish' : '' );
		}
		if ( is_wp_error( $ergebnis ) ) {
			// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- Beanspruchung zurücknehmen
			$wpdb->update(
				$t,
				array(
					'status'           => (string) $zeile['status'],
					'abgeschlossen_at' => null,
				),
				array( 'id' => (int) $zeile['id'] )
			);
			$ergebnis->add_data( array( 'status' => 500 ) );
			return $ergebnis;
		}
		$entscheidung = array(
			'aktion' => $aktion,
			'felder' => array_keys( $werte ),
			'wer'    => wp_get_current_user()->user_login,
			'zeit'   => gmdate( 'c' ),
		);
		// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- eigene Tabelle
		$wpdb->update(
			$t,
			array(
				'eintrag_id'   => (int) $ergebnis,
				'entscheidung' => (string) wp_json_encode( $entscheidung ),
			),
			array( 'id' => (int) $zeile['id'] )
		);
	} finally {
		if ( 'anlegen' !== $aktion ) {
			tamil_site_vz_entsperren( $id );
		}
	}
	$protokoll = array(
		'anlegen'   => 'angelegt',
		'aendern'   => 'geaendert',
		'entfernen' => 'entfernt',
	);
	tamil_site_vz_protokoll( $protokoll[ $aktion ], $vorgang, (int) $ergebnis, implode( ',', array_keys( $werte ) ) );
	return array(
		'bereits'    => false,
		'eintrag'    => tamil_site_vz_eintrag_ausgabe( (int) $ergebnis ),
		'einsendung' => tamil_site_vz_einsendung_ausgabe( (array) tamil_site_vz_einsendung_zeile( $vorgang ) ),
	);
}

/**
 * Täglich: Einsendungen 90 Tage nach Eingang löschen (mit Name und E-Mail), IP-Hash nach 24 Stunden leeren,
 * Protokoll nach 12 Monaten.
 */
function tamil_site_vz_aufraeumen(): void {
	global $wpdb;
	$t = tamil_site_vz_tabelle();
	$p = tamil_site_vz_protokoll_tabelle();
	// phpcs:disable WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- eigene Tabellen
	$geloescht = (int) $wpdb->query( $wpdb->prepare( "DELETE FROM {$t} WHERE eingang_at < %s", gmdate( 'Y-m-d H:i:s', time() - TAMIL_SITE_VZ_FRIST_TAGE * DAY_IN_SECONDS ) ) );
	$wpdb->query( $wpdb->prepare( "UPDATE {$t} SET ip_hash = NULL WHERE ip_hash IS NOT NULL AND eingang_at < %s", gmdate( 'Y-m-d H:i:s', time() - DAY_IN_SECONDS ) ) );
	$wpdb->query( $wpdb->prepare( "DELETE FROM {$p} WHERE ts < %s", gmdate( 'Y-m-d H:i:s', strtotime( '-' . TAMIL_SITE_VZ_PROTOKOLL_MONATE . ' months' ) ) ) );
	// phpcs:enable WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.PreparedSQL.InterpolatedNotPrepared
	if ( $geloescht ) {
		tamil_site_vz_protokoll( 'loeschfrist', '', 0, (string) $geloescht, 'cron' );
	}
}
add_action( 'tamil_site_vz_aufraeumen', 'tamil_site_vz_aufraeumen' );

/**
 * Täglichen Lauf einplanen (sobald die Tabelle da ist).
 */
function tamil_site_vz_cron_planen(): void {
	if ( tamil_site_datenversion() >= 4 && ! wp_next_scheduled( 'tamil_site_vz_aufraeumen' ) ) {
		wp_schedule_event( time() + HOUR_IN_SECONDS, 'daily', 'tamil_site_vz_aufraeumen' );
	}
}
add_action( 'init', 'tamil_site_vz_cron_planen', 30 );
