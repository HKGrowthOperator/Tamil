<?php
/**
 * Upgrade-Routine: bringt eine laufende Installation auf den Datenstand dieses Plugins.
 *
 * Hintergrund: Der Container richtet nur beim allerersten Start ein (wordpress/docker/start.sh), und die Rolle „radar“
 * bekommt ihre Rechte nur, wenn sie noch fehlt. Neue Bausteine kämen auf der laufenden Website sonst nie an.
 *
 * So meldet ein Baustein an, was er braucht (beim Laden seiner Datei, vor `init`):
 *   tamil_site_seite_anmelden( 'impressum', 'Impressum' );          // Seite anlegen, falls sie fehlt (als Entwurf)
 *   tamil_site_rechte_anmelden( 'radar', array( 'edit_posts' ) );  // fehlende Rechte einer Rolle nachrüsten
 *   tamil_site_upgrade_schritt( 2, 'tabelle_x', 'tamil_site_tabelle_x' ); // einmaliger Schritt ab Datenversion 2 (z. B. dbDelta)
 * und erhöht danach TAMIL_SITE_DATENVERSION. Seiten und Rechte werden bei jedem Lauf abgeglichen, nummerierte Schritte
 * laufen genau dann, wenn die gespeicherte Version kleiner ist als ihre Nummer. Alles muss idempotent sein.
 *
 * Bei jedem Seitenaufruf kostet die Routine einen Optionsvergleich (die Option wird mit autoload geladen).
 */

defined( 'ABSPATH' ) || exit;

/**
 * Datenversion dieses Plugins. Erhöhen, sobald ein Baustein Seiten, Rechte, Tabellen oder Schritte neu anmeldet.
 */
define( 'TAMIL_SITE_DATENVERSION', 1 );

/**
 * Sperre gegen gleichzeitige Läufe: so viele Sekunden gilt eine liegengebliebene Sperre noch.
 */
define( 'TAMIL_SITE_UPGRADE_SPERRE_SEKUNDEN', 300 );

/**
 * Gemeinsames Register der Upgrade-Routine.
 *
 * @return array{seiten:array<string,string>,rechte:array<string,array<int,string>>,schritte:array<int,array{version:int,name:string,fn:callable}>}
 */
function &tamil_site_upgrade_register(): array {
	static $register = array(
		'seiten'   => array(),
		'rechte'   => array(),
		'schritte' => array(),
	);
	return $register;
}

/**
 * Meldet eine Seite an, die es geben muss. Fehlt sie, wird sie als leerer Entwurf angelegt; vorhandene Seiten
 * (gleich welcher Status) werden nie verändert.
 *
 * @param string $slug  Pfad der Seite.
 * @param string $titel Titel des Entwurfs.
 */
function tamil_site_seite_anmelden( string $slug, string $titel ): void {
	$register = &tamil_site_upgrade_register();
	$slug     = sanitize_title( $slug );

	$register['seiten'][ $slug ] = $titel;
}

/**
 * Meldet Rechte an, die eine Rolle haben muss. Fehlende werden ergänzt, vorhandene nie entzogen.
 *
 * @param string        $rolle  Rollenname.
 * @param array<string> $rechte Rechte (capabilities).
 */
function tamil_site_rechte_anmelden( string $rolle, array $rechte ): void {
	$register                     = &tamil_site_upgrade_register();
	$bisher                       = $register['rechte'][ $rolle ] ?? array();
	$register['rechte'][ $rolle ] = array_values( array_unique( array_merge( $bisher, array_map( 'strval', $rechte ) ) ) );
}

/**
 * Meldet einen einmaligen Schritt an (z. B. eine Tabelle über dbDelta). Er läuft, wenn die gespeicherte Datenversion
 * kleiner als $version ist, und muss trotzdem idempotent sein (ein abgebrochener Lauf wird wiederholt).
 *
 * @param int      $version    Datenversion, ab der der Schritt gilt.
 * @param string   $name       Kurzer Name (für das Protokoll im Fehlerfall).
 * @param callable $ausfuehren Ausführung.
 */
function tamil_site_upgrade_schritt( int $version, string $name, callable $ausfuehren ): void {
	$register               = &tamil_site_upgrade_register();
	$register['schritte'][] = array(
		'version' => $version,
		'name'    => $name,
		'fn'      => $ausfuehren,
	);
}

/**
 * Gespeicherte Datenversion (0, wenn die Routine noch nie gelaufen ist).
 */
function tamil_site_datenversion(): int {
	return (int) get_option( 'tamil_site_datenversion', 0 );
}

/**
 * Früh bei jedem Aufruf: nur wenn die Version nicht stimmt, wird nachgeholt.
 */
function tamil_site_upgrade_pruefen(): void {
	if ( tamil_site_datenversion() >= TAMIL_SITE_DATENVERSION ) {
		return;
	}
	tamil_site_upgrade_ausfuehren();
}
// Priorität 20: nach tamil_radar_init (10), damit die Rolle „radar“ schon existiert.
add_action( 'init', 'tamil_site_upgrade_pruefen', 20 );

/**
 * Sperre setzen. INSERT IGNORE ist atomar (eindeutiger Optionsname); add_option() wäre es nicht.
 */
function tamil_site_upgrade_sperren(): bool {
	global $wpdb;
	$jetzt = time();
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- atomare Sperre, darf nicht aus dem Cache kommen
	$alt = $wpdb->get_var( $wpdb->prepare( "SELECT option_value FROM {$wpdb->options} WHERE option_name = %s", 'tamil_site_upgrade_sperre' ) );
	if ( null !== $alt && $jetzt - (int) $alt > TAMIL_SITE_UPGRADE_SPERRE_SEKUNDEN ) {
		tamil_site_upgrade_entsperren(); // liegengeblieben (abgebrochener Lauf)
	}
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- atomare Sperre
	$neu = $wpdb->query( $wpdb->prepare( "INSERT IGNORE INTO {$wpdb->options} (option_name, option_value, autoload) VALUES (%s, %s, 'off')", 'tamil_site_upgrade_sperre', (string) $jetzt ) );
	return 1 === (int) $neu;
}

function tamil_site_upgrade_entsperren(): void {
	global $wpdb;
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- Gegenstück zur atomaren Sperre
	$wpdb->delete( $wpdb->options, array( 'option_name' => 'tamil_site_upgrade_sperre' ) );
	wp_cache_delete( 'tamil_site_upgrade_sperre', 'options' );
	wp_cache_delete( 'notoptions', 'options' );
}

/**
 * Holt nach, was fehlt: Seiten, Rechte, dann die nummerierten Schritte in aufsteigender Reihenfolge.
 * Gibt false zurück, wenn ein anderer Lauf die Sperre hält oder ein Schritt scheitert (dann bleibt die Version stehen
 * und der nächste Aufruf versucht es erneut).
 */
function tamil_site_upgrade_ausfuehren(): bool {
	if ( ! tamil_site_upgrade_sperren() ) {
		return false;
	}
	$von = tamil_site_datenversion();
	$ok  = true;
	try {
		$register = tamil_site_upgrade_register();
		foreach ( $register['seiten'] as $slug => $titel ) {
			tamil_site_seite_sicherstellen( $slug, $titel );
		}
		foreach ( tamil_site_upgrade_rechte() as $rolle => $rechte ) {
			tamil_site_rechte_nachruesten( $rolle, $rechte );
		}
		$schritte = $register['schritte'];
		usort(
			$schritte,
			static function ( $a, $b ) {
				return $a['version'] <=> $b['version'];
			}
		);
		foreach ( $schritte as $schritt ) {
			if ( $schritt['version'] > $von && $schritt['version'] <= TAMIL_SITE_DATENVERSION ) {
				call_user_func( $schritt['fn'] );
			}
		}
	} catch ( Throwable $e ) {
		$ok = false;
		// phpcs:ignore WordPress.PHP.DevelopmentFunctions.error_log_error_log -- Fehler im Upgrade gehört ins Server-Log
		error_log( 'tamil-site: Upgrade auf Datenversion ' . TAMIL_SITE_DATENVERSION . ' gescheitert: ' . $e->getMessage() );
	} finally {
		if ( $ok ) {
			update_option( 'tamil_site_datenversion', TAMIL_SITE_DATENVERSION, true );
		}
		tamil_site_upgrade_entsperren();
	}
	return $ok;
}

/**
 * Angemeldete Rechte plus die Grundrechte der Rolle „radar“ aus dem Plugin tamil-radar (das sie selbst nur beim
 * Anlegen der Rolle vergibt).
 *
 * @return array<string,array<int,string>>
 */
function tamil_site_upgrade_rechte(): array {
	$rechte = tamil_site_upgrade_register()['rechte'];
	if ( function_exists( 'tamil_radar_role_caps' ) ) {
		$radar           = array_keys( array_filter( tamil_radar_role_caps() ) );
		$rechte['radar'] = array_values( array_unique( array_merge( $radar, $rechte['radar'] ?? array() ) ) );
	}
	return $rechte;
}

/**
 * Seite anlegen, falls es unter diesem Pfad keine gibt (auch keinen Entwurf und nichts im Papierkorb unter
 * demselben Pfad). Neue Seiten sind leere Entwürfe: veröffentlicht wird erst der gelieferte Text.
 *
 * @return int ID der vorhandenen oder neuen Seite, 0 bei Fehler.
 */
function tamil_site_seite_sicherstellen( string $slug, string $titel ): int {
	$vorhanden = get_page_by_path( $slug, OBJECT, 'page' );
	if ( $vorhanden instanceof WP_Post ) {
		return (int) $vorhanden->ID;
	}
	$id = wp_insert_post(
		array(
			'post_type'    => 'page',
			'post_status'  => 'draft',
			'post_title'   => $titel,
			'post_name'    => $slug,
			'post_content' => '',
		),
		true
	);
	if ( is_wp_error( $id ) ) {
		throw new RuntimeException( 'Seite ' . esc_html( $slug ) . ': ' . esc_html( $id->get_error_message() ) );
	}
	return (int) $id;
}

/**
 * Fehlende Rechte einer Rolle ergänzen. Fehlt die Rolle (Plugin aus), wird sie übersprungen.
 *
 * @param array<int,string> $rechte Rechte.
 * @return array<int,string> Neu vergebene Rechte.
 */
function tamil_site_rechte_nachruesten( string $rolle, array $rechte ): array {
	$role = get_role( $rolle );
	if ( ! $role ) {
		return array();
	}
	$neu = array();
	foreach ( $rechte as $cap ) {
		if ( ! $role->has_cap( $cap ) ) {
			$role->add_cap( $cap );
			$neu[] = $cap;
		}
	}
	return $neu;
}

// Erste Anmeldungen (Datenversion 1): Rechtsseiten. Den Text liefert KBS; bis dahin bleiben sie Entwürfe.
tamil_site_seite_anmelden( 'impressum', 'Impressum' );
tamil_site_seite_anmelden( 'datenschutz', 'Datenschutz' );
