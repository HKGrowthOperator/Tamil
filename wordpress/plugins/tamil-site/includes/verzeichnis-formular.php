<?php
/**
 * Verzeichnis-Formulare (Festlegung F2): „Eintrag vorschlagen“ und „Änderung melden“ (auch „Eintrag entfernen“).
 *
 * Spam-Schutz wie bei den Einsendungen (F1): Nonce, verstecktes Feld, Absendedauer ≥ 3 Sekunden (Zeitstempel mit
 * Prüfsumme), höchstens fünf Einsendungen je Stunde und IP-Hash. Einwilligung in der angezeigten Fassung. Fehlende
 * Angaben zum Eintrag werden nicht ergänzt; die Einsendung wird angenommen und in der Prüfung als „fehlt“ markiert.
 * Pflicht sind nur Name und Art des Eintrags sowie Name, E-Mail und Berechtigung des Einsenders.
 */

defined( 'ABSPATH' ) || exit;

/** Mindestdauer zwischen Anzeige und Absenden, in Sekunden. */
define( 'TAMIL_SITE_VZ_MIN_SEKUNDEN', 3 );
/** Höchstzahl Einsendungen je Stunde und IP-Hash. */
define( 'TAMIL_SITE_VZ_JE_STUNDE', 5 );

/**
 * Einwilligungstext und Fassung (vorläufig, bis KBS die Rechtstexte liefert; änderbar über den Filter).
 *
 * @return array{text:string,fassung:string}
 */
function tamil_site_vz_einwilligung(): array {
	$standard = array(
		'text'    => __( 'Vorläufige Fassung. Ich willige ein, dass Tamil.de meine Angaben speichert, um den Vorschlag zu prüfen und mich bei Rückfragen zu kontaktieren. Mein Name und meine E-Mail-Adresse werden nicht veröffentlicht und 90 Tage nach Eingang gelöscht.', 'tamil-site' ),
		'fassung' => '2026-11-vorlaeufig',
	);
	$wert     = apply_filters( 'tamil_site_vz_einwilligung', $standard );
	return is_array( $wert ) && isset( $wert['text'], $wert['fassung'] ) ? $wert : $standard;
}

/**
 * Zeitstempel mit Prüfsumme.
 *
 * @param int|null $zeit Unixzeit (Standard: jetzt).
 */
function tamil_site_vz_zeitstempel( ?int $zeit = null ): string {
	$zeit = $zeit ?? time();
	return $zeit . '.' . substr( wp_hash( 'tamil-vz-zeit|' . $zeit ), 0, 20 );
}

/**
 * Zeitstempel prüfen: ok, schnell oder ungueltig.
 *
 * @param int|null $jetzt Unixzeit (Standard: jetzt).
 */
function tamil_site_vz_zeit_pruefen( string $wert, ?int $jetzt = null ): string {
	$jetzt = $jetzt ?? time();
	if ( ! preg_match( '/^(\d{9,11})\.([a-f0-9]{20})$/', $wert, $m ) || ! hash_equals( tamil_site_vz_zeitstempel( (int) $m[1] ), $wert ) ) {
		return 'ungueltig';
	}
	$dauer = $jetzt - (int) $m[1];
	if ( $dauer > DAY_IN_SECONDS ) {
		return 'ungueltig';
	}
	return $dauer < TAMIL_SITE_VZ_MIN_SEKUNDEN ? 'schnell' : 'ok';
}

/**
 * Adresse des Besuchers (hinter Proxys: TAMIL_PROXY_ANZAHL in wp-config.php, wie bei F1).
 */
function tamil_site_vz_client_ip(): string {
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

function tamil_site_vz_ip_hash( string $ip ): string {
	return hash_hmac( 'sha256', $ip, wp_salt( 'nonce' ) );
}

/**
 * Einsendungen der letzten Stunde von diesem IP-Hash.
 */
function tamil_site_vz_drossel_zaehler( string $ip_hash ): int {
	global $wpdb;
	$t = tamil_site_vz_tabelle();
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- eigene Tabelle
	return (int) $wpdb->get_var( $wpdb->prepare( "SELECT COUNT(*) FROM {$t} WHERE ip_hash = %s AND eingang_at >= %s", $ip_hash, gmdate( 'Y-m-d H:i:s', time() - HOUR_IN_SECONDS ) ) );
}

function tamil_site_vz_danke_pruef( string $vorgang ): string {
	return substr( wp_hash( 'tamil-vz-danke|' . $vorgang ), 0, 16 );
}

/**
 * Öffentlicher Eintrag (für „Änderung melden“), sonst 0.
 */
function tamil_site_vz_oeffentlicher_eintrag( int $id ): int {
	return $id && TAMIL_SITE_VZ_TYP === get_post_type( $id ) && 'publish' === get_post_status( $id ) ? $id : 0;
}

/**
 * Formularzustand für die Anzeige nach einem Fehler.
 *
 * @param array<string,mixed>|null $neu Neuer Zustand.
 * @return array<string,mixed>
 */
function tamil_site_vz_zustand( ?array $neu = null ): array {
	static $zustand = array();
	if ( null !== $neu ) {
		$zustand = $neu;
	}
	return $zustand;
}

/**
 * Verarbeitet ein abgesendetes Verzeichnis-Formular (template_redirect). Erfolg: 303 mit Vorgangsnummer.
 */
function tamil_site_vz_formular_verarbeiten(): void {
	$methode = isset( $_SERVER['REQUEST_METHOD'] ) ? strtoupper( sanitize_key( wp_unslash( $_SERVER['REQUEST_METHOD'] ) ) ) : '';
	if ( 'POST' !== $methode || ! isset( $_POST['vz_typ'] ) ) { // phpcs:ignore WordPress.Security.NonceVerification.Missing -- Nonce wird unten geprüft
		return;
	}
	$typ = sanitize_key( wp_unslash( $_POST['vz_typ'] ) ); // phpcs:ignore WordPress.Security.NonceVerification.Missing -- Nonce wird unten geprüft
	if ( ! in_array( $typ, array( 'neu', 'aenderung' ), true ) || ! tamil_site_funktion_an( 'verzeichnis' ) ) {
		return;
	}
	$ergebnis = tamil_site_vz_formular_annehmen( $typ );
	if ( is_string( $ergebnis ) ) {
		$ziel = is_singular() ? (string) get_permalink( get_queried_object_id() ) : home_url( '/' );
		$ziel = add_query_arg(
			array(
				'vz_eingang' => rawurlencode( $ergebnis ),
				'vz_pruef'   => tamil_site_vz_danke_pruef( $ergebnis ),
			),
			$ziel
		) . '#vz-formular';
		wp_safe_redirect( $ziel, 303 );
		exit;
	}
	tamil_site_vz_zustand( array_merge( $ergebnis, array( 'typ' => $typ ) ) );
}
add_action( 'template_redirect', 'tamil_site_vz_formular_verarbeiten', 1 );

/**
 * Prüft und speichert die Einsendung aus $_POST.
 *
 * @return string|array{werte:array<string,string>,oeffentlich:array<string,bool>,fehler:array<string,string>,meldung:string}
 */
function tamil_site_vz_formular_annehmen( string $typ ) {
	// phpcs:disable WordPress.Security.NonceVerification.Missing -- Nonce wird unten geprüft, bevor etwas gespeichert wird
	$roh         = isset( $_POST['vz'] ) && is_array( $_POST['vz'] ) ? wp_unslash( $_POST['vz'] ) : array(); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput.InputNotSanitized -- bereinigt je Feld in tamil_site_vz_werte_pruefen()
	$roh_oeff    = isset( $_POST['vz_oeffentlich'] ) && is_array( $_POST['vz_oeffentlich'] ) ? array_map( 'sanitize_key', array_keys( wp_unslash( $_POST['vz_oeffentlich'] ) ) ) : array(); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput.InputNotSanitized -- nur Schlüssel, bereinigt
	$nonce       = isset( $_POST['vz_nonce'] ) ? sanitize_text_field( wp_unslash( $_POST['vz_nonce'] ) ) : '';
	$zeit        = isset( $_POST['vz_zeit'] ) ? sanitize_text_field( wp_unslash( $_POST['vz_zeit'] ) ) : '';
	$falle       = isset( $_POST['vz_webseite'] ) ? sanitize_text_field( wp_unslash( $_POST['vz_webseite'] ) ) : '';
	$fassung     = isset( $_POST['vz_fassung'] ) ? sanitize_key( wp_unslash( $_POST['vz_fassung'] ) ) : '';
	$einwilligt  = ! empty( $_POST['vz_einwilligung'] );
	$eintrag_id  = isset( $_POST['vz_eintrag'] ) ? absint( $_POST['vz_eintrag'] ) : 0;
	$wunsch      = isset( $_POST['vz_wunsch'] ) ? sanitize_key( wp_unslash( $_POST['vz_wunsch'] ) ) : '';
	$person_name = isset( $_POST['vz_einsender_name'] ) ? sanitize_text_field( wp_unslash( $_POST['vz_einsender_name'] ) ) : '';
	$person_mail = isset( $_POST['vz_einsender_email'] ) ? sanitize_email( wp_unslash( $_POST['vz_einsender_email'] ) ) : '';
	$berechtigt  = isset( $_POST['vz_berechtigung'] ) ? sanitize_key( wp_unslash( $_POST['vz_berechtigung'] ) ) : '';
	$anmerkung   = isset( $_POST['vz_anmerkung'] ) ? sanitize_textarea_field( wp_unslash( $_POST['vz_anmerkung'] ) ) : '';
	// phpcs:enable WordPress.Security.NonceVerification.Missing

	$oeffentlich = array();
	foreach ( tamil_site_vz_felder() as $key => $feld ) {
		$oeffentlich[ $key ] = ! $feld['wahl'] || in_array( $key, $roh_oeff, true );
	}
	unset( $roh['kategorie'] ); // Kategorie schlägt der Agent vor, nicht das Formular.
	$gepr   = tamil_site_vz_werte_pruefen( (array) $roh );
	$basis  = array(
		'werte'       => $gepr['werte'],
		'oeffentlich' => $oeffentlich,
		'fehler'      => array(),
		'person'      => array(
			'name'         => $person_name,
			'email'        => $person_mail,
			'berechtigung' => $berechtigt,
			'anmerkung'    => $anmerkung,
			'wunsch'       => $wunsch,
		),
	);
	$nicht  = __( 'Die Einsendung wurde nicht angenommen.', 'tamil-site' );
	$zstand = tamil_site_vz_zeit_pruefen( $zeit );
	if ( ! wp_verify_nonce( $nonce, 'tamil_vz_' . $typ ) || 'ungueltig' === $zstand ) {
		return array_merge( $basis, array( 'meldung' => __( 'Das Formular ist abgelaufen. Bitte prüft eure Angaben und sendet es noch einmal ab.', 'tamil-site' ) ) );
	}
	if ( '' !== $falle ) {
		return array(
			'werte'       => array(),
			'oeffentlich' => array(),
			'fehler'      => array(),
			'meldung'     => $nicht,
		);
	}
	if ( 'schnell' === $zstand ) {
		return array_merge( $basis, array( 'meldung' => $nicht . ' ' . __( 'Sie kam schneller, als ein Mensch tippen kann. Bitte sendet sie noch einmal ab.', 'tamil-site' ) ) );
	}
	$ip_hash = tamil_site_vz_ip_hash( tamil_site_vz_client_ip() );
	if ( tamil_site_vz_drossel_zaehler( $ip_hash ) >= TAMIL_SITE_VZ_JE_STUNDE ) {
		return array_merge( $basis, array( 'meldung' => $nicht . ' ' . __( 'Von eurem Anschluss kamen in der letzten Stunde zu viele Einsendungen. Bitte versucht es später noch einmal.', 'tamil-site' ) ) );
	}

	$fehler = $gepr['fehler'];
	if ( '' === $person_name ) {
		$fehler['einsender_name'] = __( 'Bitte euren Namen angeben.', 'tamil-site' );
	}
	if ( '' === $person_mail || ! is_email( $person_mail ) ) {
		$fehler['einsender_email'] = __( 'Bitte eine gültige E-Mail-Adresse für Rückfragen angeben.', 'tamil-site' );
	}
	if ( ! in_array( $berechtigt, array( 'inhaber', 'hinweis' ), true ) ) {
		$fehler['berechtigung'] = __( 'Bitte angeben, ob ihr Inhaber oder berechtigt seid oder nur darauf hinweist.', 'tamil-site' );
	}
	if ( ! $einwilligt ) {
		$fehler['einwilligung'] = __( 'Ohne Einwilligung können wir die Einsendung nicht annehmen.', 'tamil-site' );
	} elseif ( tamil_site_vz_einwilligung()['fassung'] !== $fassung ) {
		$fehler['einwilligung'] = __( 'Der Text der Einwilligung hat sich geändert. Bitte lest ihn und bestätigt ihn noch einmal.', 'tamil-site' );
	}

	$speichern_typ = 'neu';
	$felder        = $gepr['werte'];
	if ( 'neu' === $typ ) {
		$eintrag_id = 0;
		if ( '' === ( $felder['name'] ?? '' ) ) {
			$fehler['name'] = __( 'Bitte den Namen des Eintrags angeben.', 'tamil-site' );
		}
		if ( '' === ( $felder['art'] ?? '' ) && ! isset( $fehler['art'] ) ) {
			$fehler['art'] = __( 'Bitte eine der vier Arten wählen.', 'tamil-site' );
		}
		$felder = array_filter(
			$felder,
			static function ( $wert ) {
				return '' !== $wert;
			}
		);
	} else {
		$eintrag_id = tamil_site_vz_oeffentlicher_eintrag( $eintrag_id );
		if ( ! $eintrag_id ) {
			return array_merge( $basis, array( 'meldung' => __( 'Diesen Eintrag gibt es nicht (mehr).', 'tamil-site' ) ) );
		}
		if ( 'entfernen' === $wunsch ) {
			$speichern_typ = 'entfernen';
			$felder        = array();
		} else {
			$speichern_typ = 'aenderung';
			$alt           = (array) tamil_site_vz_eintrag_werte( $eintrag_id );
			$felder        = array_filter(
				$felder,
				static function ( $wert, $key ) use ( $alt ) {
					return (string) ( $alt[ $key ] ?? '' ) !== $wert;
				},
				ARRAY_FILTER_USE_BOTH
			);
			if ( ! $felder && '' === $anmerkung && ! $fehler ) {
				$fehler['anmerkung'] = __( 'Wir sehen keine Änderung. Bitte ändert ein Feld oder beschreibt die Änderung.', 'tamil-site' );
			}
		}
	}
	if ( $fehler ) {
		return array_merge(
			$basis,
			array(
				'fehler'  => $fehler,
				'meldung' => __( 'Bitte prüft die markierten Angaben.', 'tamil-site' ),
			)
		);
	}
	$mit_wahl = array();
	foreach ( $felder as $key => $wert ) {
		$mit_wahl[ $key ] = array(
			'wert'        => $wert,
			'oeffentlich' => $oeffentlich[ $key ],
		);
	}
	$vorgang = tamil_site_vz_einsendung_speichern(
		array(
			'typ'                  => $speichern_typ,
			'eintrag_id'           => $eintrag_id,
			'einsender_name'       => $person_name,
			'einsender_email'      => $person_mail,
			'berechtigung'         => $berechtigt,
			'felder'               => $mit_wahl,
			'anmerkung'            => $anmerkung,
			'einwilligung_fassung' => $fassung,
			'ip_hash'              => $ip_hash,
		)
	);
	if ( is_wp_error( $vorgang ) ) {
		return array_merge( $basis, array( 'meldung' => $vorgang->get_error_message() ) );
	}
	return $vorgang;
}

/**
 * Vorgangsnummer aus der Adresse, wenn die Prüfsumme stimmt.
 */
function tamil_site_vz_danke(): string {
	// phpcs:disable WordPress.Security.NonceVerification.Recommended -- nur Anzeige, durch Prüfsumme gesichert
	$vorgang = isset( $_GET['vz_eingang'] ) ? sanitize_text_field( wp_unslash( $_GET['vz_eingang'] ) ) : '';
	$pruef   = isset( $_GET['vz_pruef'] ) ? sanitize_key( wp_unslash( $_GET['vz_pruef'] ) ) : '';
	// phpcs:enable WordPress.Security.NonceVerification.Recommended
	if ( ! tamil_site_vz_vorgangsnummer_gueltig( $vorgang ) || ! hash_equals( tamil_site_vz_danke_pruef( $vorgang ), $pruef ) ) {
		return '';
	}
	return $vorgang;
}

/**
 * Formular ausgeben.
 *
 * @param string $typ        neu oder aenderung.
 * @param int    $eintrag_id Bei „aenderung“ der öffentliche Eintrag.
 */
function tamil_site_vz_formular( string $typ, int $eintrag_id = 0 ): string {
	$vorgang = tamil_site_vz_danke();
	ob_start();
	if ( '' !== $vorgang ) {
		?>
		<div class="vz-formular" id="vz-formular">
			<div class="vz-danke" role="status">
				<p><?php esc_html_e( 'Danke. Die Redaktion prüft eure Einsendung, bevor etwas im Verzeichnis erscheint.', 'tamil-site' ); ?></p>
				<p><?php esc_html_e( 'Eure Vorgangsnummer:', 'tamil-site' ); ?> <strong class="vz-vorgang"><?php echo esc_html( $vorgang ); ?></strong></p>
			</div>
		</div>
		<?php
		return (string) ob_get_clean();
	}
	$alt = array();
	if ( 'aenderung' === $typ ) {
		$eintrag_id = tamil_site_vz_oeffentlicher_eintrag( $eintrag_id );
		if ( ! $eintrag_id ) {
			ob_end_clean();
			return '<div class="vz-formular" id="vz-formular"><p>' . esc_html__( 'Diesen Eintrag gibt es nicht (mehr).', 'tamil-site' ) . '</p></div>';
		}
		$alt = (array) tamil_site_vz_eintrag_werte( $eintrag_id );
	}
	$zustand      = tamil_site_vz_zustand();
	$aktiv        = ( $zustand['typ'] ?? '' ) === $typ;
	$werte        = $aktiv ? array_merge( $alt, (array) ( $zustand['werte'] ?? array() ) ) : $alt;
	$oeffentlich  = $aktiv ? (array) ( $zustand['oeffentlich'] ?? array() ) : array();
	$person       = $aktiv ? (array) ( $zustand['person'] ?? array() ) : array();
	$fehler       = $aktiv ? (array) ( $zustand['fehler'] ?? array() ) : array();
	$meldung      = $aktiv ? (string) ( $zustand['meldung'] ?? '' ) : '';
	$einwilligung = tamil_site_vz_einwilligung();
	$ziel         = is_singular() ? (string) get_permalink( get_queried_object_id() ) : home_url( '/' );
	$ziel         = add_query_arg( 'aenderung' === $typ ? array( 'vz_formular' => 'aenderung', 'vz_eintrag' => $eintrag_id ) : array( 'vz_formular' => 'neu' ), $ziel ); // phpcs:ignore WordPress.Arrays.ArrayDeclarationSpacing.AssociativeArrayFound -- kurz
	$titel        = 'neu' === $typ ? __( 'Eintrag vorschlagen', 'tamil-site' ) : __( 'Änderung melden', 'tamil-site' );
	?>
	<div class="vz-formular" id="vz-formular">
		<form class="vz-form" method="post" action="<?php echo esc_url( $ziel . '#vz-formular' ); ?>" aria-label="<?php echo esc_attr( $titel ); ?>">
			<?php if ( '' !== $meldung ) : ?>
			<div class="vz-meldung" role="alert">
				<p><?php echo esc_html( $meldung ); ?></p>
				<?php if ( $fehler ) : ?>
				<ul>
					<?php foreach ( $fehler as $key => $text ) : ?>
					<li><a href="#vz-<?php echo esc_attr( str_replace( '_', '-', (string) $key ) ); ?>"><?php echo esc_html( $text ); ?></a></li>
					<?php endforeach; ?>
				</ul>
				<?php endif; ?>
			</div>
			<?php endif; ?>
			<?php if ( 'aenderung' === $typ ) : ?>
			<p class="vz-hinweis">
				<?php
				/* translators: %s: Name des Eintrags */
				echo esc_html( sprintf( __( 'Änderung zum Eintrag „%s“. Ändert nur, was nicht mehr stimmt.', 'tamil-site' ), (string) ( $alt['name'] ?? '' ) ) );
				?>
			</p>
			<fieldset class="vz-feld vz-auswahl">
				<legend><?php esc_html_e( 'Was möchtet ihr?', 'tamil-site' ); ?></legend>
				<?php $wunsch = (string) ( $person['wunsch'] ?? 'aendern' ); ?>
				<label><input type="radio" name="vz_wunsch" value="aendern"<?php checked( 'entfernen' !== $wunsch ); ?>> <?php esc_html_e( 'Angaben ändern', 'tamil-site' ); ?></label>
				<label><input type="radio" name="vz_wunsch" value="entfernen"<?php checked( 'entfernen' === $wunsch ); ?>> <?php esc_html_e( 'Eintrag entfernen', 'tamil-site' ); ?></label>
			</fieldset>
			<?php else : ?>
			<p class="vz-hinweis"><?php esc_html_e( 'Name und Art sind Pflicht. Fehlt etwas, fragt die Redaktion nach; nichts wird von uns ergänzt.', 'tamil-site' ); ?></p>
			<?php endif; ?>
			<?php
			foreach ( tamil_site_vz_felder() as $key => $feld ) {
				if ( 'kategorie' === $key ) {
					continue;
				}
				$haken = $aktiv ? ! empty( $oeffentlich[ $key ] ) : ( 'aenderung' === $typ && '' !== (string) ( $alt[ $key ] ?? '' ) );
				tamil_site_vz_formular_feld( $key, $feld, (string) ( $werte[ $key ] ?? '' ), (string) ( $fehler[ $key ] ?? '' ), $haken, 'neu' === $typ && in_array( $key, array( 'name', 'art' ), true ) );
			}
			$personfelder = array(
				'einsender_name'  => array( __( 'Euer Name (wird nicht veröffentlicht)', 'tamil-site' ), 'text', 'name' ),
				'einsender_email' => array( __( 'Eure E-Mail für Rückfragen (wird nicht veröffentlicht)', 'tamil-site' ), 'email', 'email' ),
			);
			foreach ( $personfelder as $key => $def ) :
				$fid = 'vz-' . str_replace( '_', '-', $key );
				?>
			<p class="vz-feld">
				<label for="<?php echo esc_attr( $fid ); ?>"><?php echo esc_html( $def[0] ); ?> <span class="vz-pflicht"><?php esc_html_e( '(Pflicht)', 'tamil-site' ); ?></span></label>
				<input type="<?php echo esc_attr( $def[1] ); ?>" id="<?php echo esc_attr( $fid ); ?>" name="vz_<?php echo esc_attr( $key ); ?>" value="<?php echo esc_attr( (string) ( $person[ substr( $key, 10 ) ] ?? '' ) ); ?>" autocomplete="<?php echo esc_attr( $def[2] ); ?>" required<?php echo isset( $fehler[ $key ] ) ? ' aria-invalid="true"' : ''; ?>>
				<?php if ( isset( $fehler[ $key ] ) ) : ?>
				<span class="vz-fehler"><?php echo esc_html( $fehler[ $key ] ); ?></span>
				<?php endif; ?>
			</p>
			<?php endforeach; ?>
			<fieldset class="vz-feld vz-auswahl" id="vz-berechtigung">
				<legend><?php esc_html_e( 'Wer sendet? (Pflicht)', 'tamil-site' ); ?></legend>
				<?php $b = (string) ( $person['berechtigung'] ?? '' ); ?>
				<label><input type="radio" name="vz_berechtigung" value="inhaber" required<?php checked( 'inhaber' === $b ); ?>> <?php esc_html_e( 'Ich bin Inhaber oder berechtigt', 'tamil-site' ); ?></label>
				<label><input type="radio" name="vz_berechtigung" value="hinweis"<?php checked( 'hinweis' === $b ); ?>> <?php esc_html_e( 'Ich weise nur darauf hin', 'tamil-site' ); ?></label>
				<?php if ( isset( $fehler['berechtigung'] ) ) : ?>
				<span class="vz-fehler"><?php echo esc_html( $fehler['berechtigung'] ); ?></span>
				<?php endif; ?>
			</fieldset>
			<p class="vz-feld">
				<label for="vz-anmerkung"><?php esc_html_e( 'Anmerkung an die Redaktion (freiwillig, wird nicht veröffentlicht)', 'tamil-site' ); ?></label>
				<textarea id="vz-anmerkung" name="vz_anmerkung" rows="3" maxlength="600"><?php echo esc_textarea( (string) ( $person['anmerkung'] ?? '' ) ); ?></textarea>
				<?php if ( isset( $fehler['anmerkung'] ) ) : ?>
				<span class="vz-fehler"><?php echo esc_html( $fehler['anmerkung'] ); ?></span>
				<?php endif; ?>
			</p>
			<p class="vz-feld vz-einwilligung" id="vz-einwilligung">
				<input type="checkbox" id="vz-einwilligung-feld" name="vz_einwilligung" value="1" required>
				<label for="vz-einwilligung-feld"><?php echo esc_html( $einwilligung['text'] ); ?> <span class="vz-pflicht"><?php esc_html_e( '(Pflicht)', 'tamil-site' ); ?></span></label>
				<?php if ( isset( $fehler['einwilligung'] ) ) : ?>
				<span class="vz-fehler"><?php echo esc_html( $fehler['einwilligung'] ); ?></span>
				<?php endif; ?>
			</p>
			<p class="vz-falle" aria-hidden="true">
				<label for="vz-webseite"><?php esc_html_e( 'Dieses Feld bitte leer lassen', 'tamil-site' ); ?></label>
				<input type="text" id="vz-webseite" name="vz_webseite" value="" tabindex="-1" autocomplete="off">
			</p>
			<input type="hidden" name="vz_typ" value="<?php echo esc_attr( $typ ); ?>">
			<input type="hidden" name="vz_eintrag" value="<?php echo esc_attr( (string) $eintrag_id ); ?>">
			<input type="hidden" name="vz_zeit" value="<?php echo esc_attr( tamil_site_vz_zeitstempel() ); ?>">
			<input type="hidden" name="vz_fassung" value="<?php echo esc_attr( $einwilligung['fassung'] ); ?>">
			<input type="hidden" name="vz_nonce" value="<?php echo esc_attr( wp_create_nonce( 'tamil_vz_' . $typ ) ); ?>">
			<p class="vz-aktion"><button type="submit"><?php esc_html_e( 'Absenden', 'tamil-site' ); ?></button></p>
		</form>
	</div>
	<?php
	return (string) ob_get_clean();
}

/**
 * Ein Feld des Eintrags mit Beschriftung, Fehler und – bei Kontaktdaten – der Wahl „öffentlich zeigen“.
 *
 * @param array{label:string,typ:string,max:int,pflicht:bool,wahl:bool} $feld Felddefinition.
 */
function tamil_site_vz_formular_feld( string $key, array $feld, string $wert, string $fehler, bool $haken, bool $pflicht ): void {
	$fid   = 'vz-' . str_replace( '_', '-', $key );
	$name  = 'vz[' . $key . ']';
	$extra = ( $pflicht ? ' required' : '' ) . ( '' !== $fehler ? ' aria-invalid="true" aria-describedby="' . esc_attr( $fid . '-fehler' ) . '"' : '' );
	?>
	<p class="vz-feld vz-feld-<?php echo esc_attr( $key ); ?>">
		<label for="<?php echo esc_attr( $fid ); ?>"><?php echo esc_html( $feld['label'] ); ?><?php echo $pflicht ? ' <span class="vz-pflicht">' . esc_html__( '(Pflicht)', 'tamil-site' ) . '</span>' : ''; ?></label>
		<?php if ( in_array( $feld['typ'], array( 'art', 'land', 'region' ), true ) ) : ?>
		<select id="<?php echo esc_attr( $fid ); ?>" name="<?php echo esc_attr( $name ); ?>"<?php echo $extra; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- oben escaped ?>>
			<option value=""><?php esc_html_e( 'bitte wählen', 'tamil-site' ); ?></option>
			<?php if ( 'region' === $feld['typ'] ) : ?>
				<?php foreach ( tamil_site_vz_regionen() as $land => $regionen ) : ?>
				<optgroup label="<?php echo esc_attr( tamil_site_vz_laender()[ $land ] ); ?>">
					<?php foreach ( $regionen as $region ) : ?>
					<option value="<?php echo esc_attr( $region ); ?>"<?php selected( $wert, $region ); ?>><?php echo esc_html( $region ); ?></option>
					<?php endforeach; ?>
				</optgroup>
				<?php endforeach; ?>
			<?php else : ?>
				<?php foreach ( 'art' === $feld['typ'] ? tamil_site_vz_arten() : tamil_site_vz_laender() as $code => $label ) : ?>
				<option value="<?php echo esc_attr( $code ); ?>"<?php selected( $wert, $code ); ?>><?php echo esc_html( $label ); ?></option>
				<?php endforeach; ?>
			<?php endif; ?>
		</select>
		<?php elseif ( 'textarea' === $feld['typ'] ) : ?>
		<textarea id="<?php echo esc_attr( $fid ); ?>" name="<?php echo esc_attr( $name ); ?>" rows="3" maxlength="<?php echo esc_attr( (string) $feld['max'] ); ?>"<?php echo $extra; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- oben escaped ?>><?php echo esc_textarea( $wert ); ?></textarea>
		<?php else : ?>
			<?php $typ = array( 'email' => 'email', 'url' => 'url', 'telefon' => 'tel' )[ $feld['typ'] ] ?? 'text'; // phpcs:ignore WordPress.Arrays.ArrayDeclarationSpacing.AssociativeArrayFound -- kurz ?>
		<input type="<?php echo esc_attr( $typ ); ?>" id="<?php echo esc_attr( $fid ); ?>" name="<?php echo esc_attr( $name ); ?>" value="<?php echo esc_attr( $wert ); ?>" maxlength="<?php echo esc_attr( (string) $feld['max'] ); ?>"<?php echo $extra; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- oben escaped ?>>
		<?php endif; ?>
		<?php if ( $feld['wahl'] ) : ?>
		<label class="vz-oeffentlich"><input type="checkbox" name="vz_oeffentlich[<?php echo esc_attr( $key ); ?>]" value="1"<?php checked( $haken ); ?>> <?php esc_html_e( 'im Verzeichnis zeigen', 'tamil-site' ); ?></label>
		<?php endif; ?>
		<?php if ( '' !== $fehler ) : ?>
		<span class="vz-fehler" id="<?php echo esc_attr( $fid . '-fehler' ); ?>"><?php echo esc_html( $fehler ); ?></span>
		<?php endif; ?>
	</p>
	<?php
}
