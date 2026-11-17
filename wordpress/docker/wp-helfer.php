<?php
/**
 * Helfer für start.sh, aufgerufen als www-data mit `wp eval-file /opt/tamil/wp-helfer.php <aufgabe>`.
 *
 *   admin-passwort  Passwort des Admins (WP_ADMIN_USER) aus WP_ADMIN_PASSWORD setzen – nur nach der Installation
 *   einrichtung     WordPress-Beispielinhalte entfernen, Rubriken anlegen, leere Seiten events + kontakt
 *   zugaenge        bei jedem Start: Benutzer ki-agent, Anwendungspasswörter „radar“ und „migration“, Cockpit-Adresse
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
	default:
		WP_CLI::error( "Unbekannte Aufgabe: {$tamil_c_aufgabe}" );
}
