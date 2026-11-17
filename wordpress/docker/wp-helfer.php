<?php
/**
 * Helfer für start.sh, aufgerufen als www-data mit `wp eval-file /opt/tamil/wp-helfer.php <aufgabe>`.
 *
 *   admin-passwort  Passwort des Admins (WP_ADMIN_USER) aus WP_ADMIN_PASSWORD setzen – nur nach der Installation
 *   einrichtung     WordPress-Beispielinhalte entfernen, Rubriken anlegen, leere Seiten events + kontakt
 *   zugaenge        bei jedem Start: Benutzer ki-agent, Anwendungspasswörter „radar“ und „migration“, Cockpit-Adresse
 *   testsystem      bei jedem Start, nur außerhalb des Echtbetriebs: Seiten production, einreichen, werben, verzeichnis;
 *                   einmalig die Bausteine Einreichungen, Verzeichnis und Werbebuchung an und Beispiel-Einträge im
 *                   Verzeichnis (Entscheidung Luis 17.11.: auf dem Testsystem mit Testdaten an)
 *   beispiele-entfernen  alle Beispiel-Einträge des Verzeichnisses löschen (vor dem Start der echten Website)
 *
 * Geheimnisse kommen nur aus Umgebungsvariablen und werden nie ausgegeben.
 *
 * @package tamil-docker
 */

defined( 'ABSPATH' ) || exit;

// Rubriken wie in sources.toml ([categories.*]) und wordpress/README.md – Slug => Name.
const TAMIL_C_RUBRIKEN = array(
	'news'          => 'Nachrichten',
	'entertainment' => 'Entertainment',
	'events'        => 'Events',
	'community'     => 'Community',
	'kueche'        => 'Küche',
	'kino'          => 'Kino',
	'sport'         => 'Sport',
	'kultur'        => 'Kultur',
);

// Seiten, die das Theme für seine Vorlagen braucht (page-events.php, page-kontakt.php) – Inhalte kommen später.
const TAMIL_C_SEITEN = array(
	'events'  => 'Events',
	'kontakt' => 'Kontakt',
);

function tamil_c_admin(): ?WP_User {
	$login = (string) getenv( 'WP_ADMIN_USER' );
	$user  = '' !== $login ? get_user_by( 'login', $login ) : false;
	return $user instanceof WP_User ? $user : null;
}

/**
 * Admin-Passwort aus WP_ADMIN_PASSWORD (bei der Installation wird erst ein Wegwerf-Passwort gesetzt).
 */
function tamil_c_admin_passwort(): void {
	$user = tamil_c_admin();
	$pw   = (string) getenv( 'WP_ADMIN_PASSWORD' );
	if ( ! $user || '' === $pw ) {
		WP_CLI::error( 'Admin oder WP_ADMIN_PASSWORD fehlt.' );
	}
	wp_set_password( $pw, $user->ID );
	WP_CLI::log( 'Admin-Passwort gesetzt.' );
}

/**
 * Grundeinrichtung nach der Installation. Idempotent; löscht nur unveränderte WordPress-Beispielinhalte.
 */
function tamil_c_einrichtung(): void {
	// „Hallo Welt!“, Beispiel-Seite, Entwurf der Datenschutzerklärung – nur an ihren Standard-IDs und -Slugs.
	$beispiele = array(
		1 => array( 'post', array( 'hello-world', 'hallo-welt' ) ),
		2 => array( 'page', array( 'sample-page', 'beispiel-seite' ) ),
		3 => array( 'page', array( 'privacy-policy', 'datenschutzerklaerung' ) ),
	);
	foreach ( $beispiele as $id => [ $typ, $slugs ] ) {
		$post = get_post( $id );
		if ( $post && $typ === $post->post_type && in_array( $post->post_name, $slugs, true ) ) {
			wp_delete_post( $id, true );
			WP_CLI::log( "Beispielinhalt entfernt: {$post->post_name}" );
		}
	}
	if ( ! get_post( (int) get_option( 'wp_page_for_privacy_policy' ) ) ) {
		update_option( 'wp_page_for_privacy_policy', 0 );
	}

	// Rubriken
	foreach ( TAMIL_C_RUBRIKEN as $slug => $name ) {
		if ( get_term_by( 'slug', $slug, 'category' ) ) {
			continue;
		}
		$neu = wp_insert_term( $name, 'category', array( 'slug' => $slug ) );
		if ( is_wp_error( $neu ) ) {
			WP_CLI::warning( "Rubrik {$slug}: " . $neu->get_error_message() );
		} else {
			WP_CLI::log( "Rubrik angelegt: {$slug}" );
		}
	}
	$news = get_term_by( 'slug', 'news', 'category' );
	if ( $news ) {
		update_option( 'default_category', (int) $news->term_id );
		// „Uncategorized“/„Allgemein“ entfernen, solange sie leer ist
		foreach ( array( 'uncategorized', 'allgemein' ) as $slug ) {
			$alt = get_term_by( 'slug', $slug, 'category' );
			if ( $alt && 0 === (int) $alt->count && (int) $alt->term_id !== (int) $news->term_id ) {
				wp_delete_term( (int) $alt->term_id, 'category' );
			}
		}
	}

	// Leere Seiten für die Vorlagen (nur wenn der Slug noch frei ist)
	$admin = tamil_c_admin();
	foreach ( TAMIL_C_SEITEN as $slug => $titel ) {
		if ( get_page_by_path( $slug, OBJECT, 'page' ) ) {
			continue;
		}
		$id = wp_insert_post(
			array(
				'post_type'    => 'page',
				'post_status'  => 'publish',
				'post_name'    => $slug,
				'post_title'   => $titel,
				'post_content' => '',
				'post_author'  => $admin ? $admin->ID : 0,
			),
			true
		);
		if ( is_wp_error( $id ) ) {
			WP_CLI::warning( "Seite {$slug}: " . $id->get_error_message() );
		} else {
			WP_CLI::log( "Seite angelegt: {$slug}" );
		}
	}
}

/**
 * Anwendungspasswort mit festem Namen auf das Geheimnis aus einer Umgebungsvariablen bringen.
 *
 * WordPress entfernt beim Anmelden alles außer a–z/0–9 aus dem Passwort (wp_authenticate_application_password) –
 * gehasht wird deshalb genau diese Form, mit WP_Application_Passwords::hash_password() (ab 6.8 wp_fast_hash).
 * Passt ein vorhandener Eintrag schon, bleibt er unverändert (UUID und „zuletzt benutzt“ bleiben erhalten).
 *
 * @param bool $leer_entfernen Ist die Variable leer, den Eintrag löschen (sonst unverändert lassen).
 */
function tamil_c_app_passwort( WP_User $user, string $name, string $env, bool $leer_entfernen ): void {
	$roh     = (string) getenv( $env );
	$geheim  = (string) preg_replace( '/[^a-z\d]/i', '', $roh );
	$liste   = WP_Application_Passwords::get_user_application_passwords( $user->ID );
	$andere  = array_values( array_filter( $liste, static fn( $p ) => ( $p['name'] ?? '' ) !== $name ) );
	$treffer = array_values( array_filter( $liste, static fn( $p ) => ( $p['name'] ?? '' ) === $name ) );

	if ( '' === $geheim ) {
		if ( '' !== $roh ) {
			WP_CLI::warning( "{$env} enthält keine Buchstaben/Ziffern – Anwendungspasswort „{$name}“ nicht gesetzt." );
		}
		if ( $leer_entfernen && $treffer ) {
			update_user_meta( $user->ID, WP_Application_Passwords::USERMETA_KEY_APPLICATION_PASSWORDS, $andere );
			WP_CLI::log( "Anwendungspasswort „{$name}“ von {$user->user_login} entfernt ({$env} leer)." );
		}
		return;
	}
	if ( $roh !== $geheim ) {
		WP_CLI::warning( "{$env}: WordPress ignoriert Leer- und Sonderzeichen – gültig sind nur Buchstaben und Ziffern." );
	}
	if ( strlen( $geheim ) < 16 ) {
		WP_CLI::warning( "{$env} ist kürzer als 16 Zeichen – bitte ein längeres Geheimnis verwenden." );
	}

	$pruefen = static function ( string $pw, string $hash ): bool {
		return method_exists( 'WP_Application_Passwords', 'check_password' )
			? WP_Application_Passwords::check_password( $pw, $hash )
			: wp_check_password( $pw, $hash );
	};
	if ( 1 === count( $treffer ) && $pruefen( $geheim, (string) $treffer[0]['password'] ) ) {
		$status = 'unverändert';
	} else {
		$andere[] = array(
			'uuid'      => wp_generate_uuid4(),
			'app_id'    => '',
			'name'      => $name,
			'password'  => method_exists( 'WP_Application_Passwords', 'hash_password' )
				? WP_Application_Passwords::hash_password( $geheim )
				: wp_hash_password( $geheim ),
			'created'   => time(),
			'last_used' => null,
			'last_ip'   => null,
		);
		update_user_meta( $user->ID, WP_Application_Passwords::USERMETA_KEY_APPLICATION_PASSWORDS, $andere );
		$status = 'gesetzt';
	}
	// Ohne diesen Merker prüft WordPress Anwendungspasswörter gar nicht erst (WP_Application_Passwords::is_in_use()).
	update_network_option( get_main_network_id(), WP_Application_Passwords::OPTION_KEY_IN_USE, true );
	WP_CLI::log( "Anwendungspasswort „{$name}“ für {$user->user_login}: {$status}." );
}

/**
 * Bei jedem Start: ki-agent, Anwendungspasswörter, Cockpit-Adresse.
 */
function tamil_c_zugaenge(): void {
	// Benutzer ki-agent mit der Rolle des Radar-Plugins (Slug „radar“, includes/role.php); ohne Plugin: author.
	$agent = get_user_by( 'login', 'ki-agent' );
	if ( ! $agent ) {
		$id = wp_insert_user(
			array(
				'user_login'   => 'ki-agent',
				'user_email'   => 'ki-agent@radar.invalid', // kein Postfach – der Radar meldet sich nur per Anwendungspasswort an
				'user_pass'    => wp_generate_password( 40, true, true ),
				'display_name' => 'News-Radar',
				'role'         => get_role( 'radar' ) ? 'radar' : 'author',
			)
		);
		if ( is_wp_error( $id ) ) {
			WP_CLI::error( 'ki-agent: ' . $id->get_error_message() );
		}
		$agent = get_user_by( 'id', $id );
		WP_CLI::log( 'Benutzer ki-agent angelegt (Rolle ' . implode( ',', $agent->roles ) . ').' );
	}
	tamil_c_app_passwort( $agent, 'radar', 'RADAR_APP_PASSWORD', false );

	$admin = tamil_c_admin();
	if ( $admin ) {
		tamil_c_app_passwort( $admin, 'migration', 'MIGRATION_APP_PASSWORD', true );
	} elseif ( '' !== (string) getenv( 'MIGRATION_APP_PASSWORD' ) ) {
		WP_CLI::warning( 'Benutzer ' . getenv( 'WP_ADMIN_USER' ) . ' fehlt – Anwendungspasswort „migration“ nicht gesetzt.' );
	}

	// Adresse des Cockpits (Option des Radar-Plugins, Feld cockpit_url)
	$cockpit = trim( (string) getenv( 'RADAR_COCKPIT_URL' ) );
	if ( '' !== $cockpit ) {
		$url = esc_url_raw( $cockpit, array( 'http', 'https' ) );
		if ( '' === $url ) {
			WP_CLI::warning( 'RADAR_COCKPIT_URL ist keine http(s)-Adresse – nicht übernommen.' );
		} else {
			$alt = get_option( 'tamil_radar_settings', array() );
			$alt = is_array( $alt ) ? $alt : array();
			if ( ( $alt['cockpit_url'] ?? '' ) !== $url ) {
				update_option( 'tamil_radar_settings', array_merge( $alt, array( 'cockpit_url' => $url ) ) );
				delete_transient( 'tamil_radar_cockpit_status' );
				WP_CLI::log( "Cockpit-Adresse: {$url}" );
			}
		}
	}
}

/** Archivbeiträge der Konzertreihe „Live mit dir!“ (IDs der Übernahme auf dem Testsystem). */
const TAMIL_C_PRODUCTION_BEITRAEGE = array( 2420, 2423, 2417, 2494 );

/** Meta-Schlüssel, der Beispiel-Einträge im Verzeichnis kennzeichnet (vor dem Start der echten Website löschen). */
const TAMIL_C_BEISPIEL_META = '_tamil_vz_beispiel';

/**
 * Inhalt der Seite „production“: die Archivbeiträge der Konzertreihe, soweit es sie auf dieser Installation gibt
 * (Links ohne Domain, überleben die Umschaltung auf tamil.de). Den Text über der Liste setzt das Theme
 * (page-production.php, Customizer); nur ohne Archivbeiträge steht hier der Satz aus dem Altbestand.
 */
function tamil_c_production_inhalt(): string {
	$links = array();
	foreach ( TAMIL_C_PRODUCTION_BEITRAEGE as $id ) {
		$post = get_post( $id );
		if ( $post instanceof WP_Post && 'post' === $post->post_type && 'publish' === $post->post_status ) {
			$links[] = '<li><a href="' . esc_url( wp_make_link_relative( (string) get_permalink( $post ) ) ) . '">' . esc_html( get_the_title( $post ) ) . '</a></li>';
		}
	}
	if ( ! $links ) {
		return '<!-- wp:paragraph --><p>A.R. Rahman, Ilaiyaraaja, Anirudh und Santhosh Narayanan standen oder stehen mit Tamil.de Production auf deutschen Bühnen.</p><!-- /wp:paragraph -->';
	}
	return '<!-- wp:heading --><h2 class="wp-block-heading">Die Konzerte im Archiv</h2><!-- /wp:heading -->'
		. '<!-- wp:list --><ul class="wp-block-list">' . implode( '', $links ) . '</ul><!-- /wp:list -->';
}

/**
 * Inhalt der Seite „einreichen“: Wege zu allen Formularen, zuerst „Event einreichen“.
 */
function tamil_c_einreichen_inhalt(): string {
	$formulare = array(
		'event'       => 'Event einreichen',
		'beitrag'     => 'Beitrag oder Thema vorschlagen',
		'kooperation' => 'Kooperation',
		'werbung'     => 'Werbeanfrage',
	);
	$links     = '';
	$abschnitt = '';
	foreach ( $formulare as $art => $titel ) {
		$links     .= '<li><a href="#tf-' . $art . '">' . $titel . '</a></li>';
		$abschnitt .= '<!-- wp:heading --><h2 class="wp-block-heading">' . $titel . '</h2><!-- /wp:heading -->'
			. '<!-- wp:shortcode -->[tamil_einsendung art="' . $art . '"]<!-- /wp:shortcode -->';
	}
	return '<!-- wp:paragraph --><p>Termine, Themen, Kooperationen und Werbeanfragen an die Redaktion. Jede Einsendung wird geprüft; die Vorgangsnummer steht nach dem Absenden auf dieser Seite.</p><!-- /wp:paragraph -->'
		. '<!-- wp:list --><ul class="wp-block-list">' . $links . '</ul><!-- /wp:list -->' . $abschnitt;
}

/**
 * Seite mit Slug sicherstellen: fehlt sie, wird sie veröffentlicht angelegt; ein Entwurf mit genau dem erwarteten
 * Shortcode (von der Upgrade-Routine angelegt) wird veröffentlicht; alles andere bleibt, wie es ist.
 *
 * @param string $vorlage Seitenvorlage des Themes (leer = keine).
 * @param string $kennung Shortcode, an dem ein Entwurf der Upgrade-Routine erkannt wird (leer = keiner).
 */
function tamil_c_seite( string $slug, string $titel, string $inhalt, string $vorlage = '', string $kennung = '' ): void {
	$seite = get_page_by_path( $slug, OBJECT, 'page' );
	if ( $seite instanceof WP_Post ) {
		if ( 'draft' === $seite->post_status && '' !== $kennung && str_contains( (string) $seite->post_content, $kennung ) ) {
			wp_update_post(
				array(
					'ID'          => $seite->ID,
					'post_status' => 'publish',
				)
			);
			WP_CLI::log( "Seite veröffentlicht: {$slug}" );
		} elseif ( 'publish' !== $seite->post_status ) {
			WP_CLI::log( "Seite {$slug} steht als {$seite->post_status} – unverändert." );
		}
		return;
	}
	$admin = tamil_c_admin();
	$id    = wp_insert_post(
		array(
			'post_type'    => 'page',
			'post_status'  => 'publish',
			'post_name'    => $slug,
			'post_title'   => $titel,
			'post_content' => $inhalt,
			'post_author'  => $admin ? $admin->ID : 0,
		),
		true
	);
	if ( is_wp_error( $id ) ) {
		WP_CLI::warning( "Seite {$slug}: " . $id->get_error_message() );
		return;
	}
	if ( '' !== $vorlage && array_key_exists( $vorlage, wp_get_theme()->get_page_templates( null, 'page' ) ) ) {
		update_post_meta( (int) $id, '_wp_page_template', $vorlage );
	}
	WP_CLI::log( "Seite angelegt: {$slug}" );
}

/**
 * Beispiel-Einträge im Verzeichnis: erkennbar erfunden („Beispiel:“ im Namen und in der Beschreibung, Musterstadt,
 * Adressen unter example.org), mit TAMIL_C_BEISPIEL_META gekennzeichnet.
 *
 * @return array<int,array<string,string>>
 */
function tamil_c_beispiele(): array {
	$text = 'Beispiel-Eintrag für das Testsystem, kein echter Betrieb. Wird vor dem Start der Website entfernt.';
	$mit  = static function ( array $werte ) use ( $text ): array {
		return array_merge(
			array(
				'beschreibung' => $text,
				'plz'          => '12345',
				'stadt'        => 'Musterstadt',
				'land'         => 'DE',
				'website'      => 'https://example.org/',
			),
			$werte
		);
	};
	return array(
		$mit(
			array(
				'name'      => 'Beispiel: Tempelverein Musterstadt',
				'art'       => 'tempel',
				'kategorie' => sanitize_title( 'tempel-Hindu-Tempel' ),
			)
		),
		$mit(
			array(
				'name'      => 'Beispiel: Tamilischer Kulturverein Musterstadt',
				'art'       => 'verein',
				'kategorie' => sanitize_title( 'verein-Kultur' ),
			)
		),
		$mit(
			array(
				'name'      => 'Beispiel: Restaurant Musterstadt',
				'art'       => 'business',
				'kategorie' => sanitize_title( 'business-Restaurant und Imbiss' ),
			)
		),
		$mit(
			array(
				'name'      => 'Beispiel: Übersetzungsbüro Musterstadt',
				'art'       => 'dienstleister',
				'kategorie' => sanitize_title( 'dienstleister-Übersetzung' ),
			)
		),
	);
}

/**
 * Testsystem einrichten (nie im Echtbetrieb). Idempotent: Seiten nach Slug, Schalter und Beispiele nur beim ersten
 * Lauf (Merker in der Option tamil_c_testsystem), damit späteres Ausschalten im Backend bestehen bleibt.
 */
function tamil_c_testsystem(): void {
	if ( 'production' === wp_get_environment_type() ) {
		WP_CLI::log( 'Echtbetrieb: Testsystem-Einrichtung übersprungen.' );
		return;
	}
	if ( ! function_exists( 'tamil_site_funktionen' ) ) {
		WP_CLI::warning( 'Plugin tamil-site nicht aktiv – Testsystem-Einrichtung übersprungen.' );
		return;
	}
	if ( defined( 'TAMIL_SITE_DATENVERSION' ) && tamil_site_datenversion() < TAMIL_SITE_DATENVERSION && ! tamil_site_upgrade_ausfuehren() ) {
		WP_CLI::warning( 'Upgrade-Routine nicht durchgelaufen – Bausteine bleiben aus.' );
		return;
	}

	tamil_c_seite( 'production', 'Live mit dir!', tamil_c_production_inhalt(), 'page-production.php' );
	tamil_c_seite( 'einreichen', 'Einreichen', tamil_c_einreichen_inhalt(), '', '[tamil_einsendung' );
	tamil_c_seite( 'werben', 'Werben', '[tamil_werbung]', '', '[tamil_werbung]' );
	tamil_c_seite( 'verzeichnis', 'Verzeichnis', '[tamil_verzeichnis]', '', '[tamil_verzeichnis]' );

	$merker = get_option( 'tamil_c_testsystem', array() );
	$merker = is_array( $merker ) ? $merker : array();
	if ( empty( $merker['schalter'] ) ) {
		$an = (array) get_option( 'tamil_site_funktionen', array() );
		foreach ( array( 'einreichungen', 'verzeichnis', 'werbung' ) as $name ) {
			$an[ $name ] = tamil_site_funktion_bereit( $name );
		}
		update_option( 'tamil_site_funktionen', $an );
		$merker['schalter'] = gmdate( 'c' );
		WP_CLI::log( 'Bausteine eingeschaltet: Einreichungen, Verzeichnis, Werbebuchung (nur Testsystem).' );
	}
	if ( empty( $merker['beispiele'] ) && function_exists( 'tamil_site_vz_eintrag_schreiben' ) ) {
		$vorhanden = get_posts(
			array(
				'post_type'   => TAMIL_SITE_VZ_TYP,
				'post_status' => 'any',
				'numberposts' => 1,
				'fields'      => 'ids',
				'meta_key'    => TAMIL_C_BEISPIEL_META, // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_key -- einmalig beim Start
			)
		);
		foreach ( $vorhanden ? array() : tamil_c_beispiele() as $werte ) {
			if ( ! term_exists( $werte['kategorie'], TAMIL_SITE_VZ_KATEGORIE ) ) {
				$werte['kategorie'] = '';
			}
			$id = tamil_site_vz_eintrag_schreiben( 0, $werte, 'publish' );
			if ( is_wp_error( $id ) ) {
				WP_CLI::warning( 'Beispiel-Eintrag: ' . $id->get_error_message() );
				continue;
			}
			update_post_meta( (int) $id, TAMIL_C_BEISPIEL_META, '1' );
			WP_CLI::log( 'Beispiel-Eintrag angelegt: ' . $werte['name'] );
		}
		$merker['beispiele'] = gmdate( 'c' );
	}
	update_option( 'tamil_c_testsystem', $merker, false );
}

/**
 * Alle Beispiel-Einträge des Verzeichnisses löschen (vor dem Start der echten Website).
 */
function tamil_c_beispiele_entfernen(): void {
	$ids = get_posts(
		array(
			'post_type'   => defined( 'TAMIL_SITE_VZ_TYP' ) ? TAMIL_SITE_VZ_TYP : 'tamil_vz_eintrag',
			'post_status' => 'any',
			'numberposts' => -1,
			'fields'      => 'ids',
			'meta_key'    => TAMIL_C_BEISPIEL_META, // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_key -- einmalige Aufräumaktion
		)
	);
	foreach ( $ids as $id ) {
		wp_delete_post( (int) $id, true );
	}
	WP_CLI::log( count( $ids ) . ' Beispiel-Einträge entfernt.' );
}

$tamil_c_aufgabe = $args[0] ?? '';
switch ( $tamil_c_aufgabe ) {
	case 'admin-passwort':
		tamil_c_admin_passwort();
		break;
	case 'einrichtung':
		tamil_c_einrichtung();
		break;
	case 'zugaenge':
		tamil_c_zugaenge();
		break;
	case 'testsystem':
		tamil_c_testsystem();
		break;
	case 'beispiele-entfernen':
		tamil_c_beispiele_entfernen();
		break;
	default:
		WP_CLI::error( "Unbekannte Aufgabe: {$tamil_c_aufgabe}" );
}
