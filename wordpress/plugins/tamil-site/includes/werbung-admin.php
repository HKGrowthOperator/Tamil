<?php
/**
 * Verwaltung der Werbebuchung in wp-admin (Menü „Werbung“, Recht tamil_werbung_verwalten): Buchungsliste mit Stand
 * und Warnungen, Einzelansicht mit Prüfen, Ablehnen (volle Erstattung), Pausieren, Fortsetzen, Beenden, Erstatten,
 * Protokoll und Statistik je Tag mit CSV-Export; Angebote (Laufzeiten, Preise, Vorlauf, Fassung der Bedingungen).
 * Jede Handlung: Nonce und Rechteprüfung, Zustandswechsel nur über die Funktionen in werbung.php.
 */

defined( 'ABSPATH' ) || exit;

// phpcs:disable WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- eigene Tabellen

const TAMIL_SITE_WERBUNG_RECHT = 'tamil_werbung_verwalten';

function tamil_site_werbung_admin_menu(): void {
	add_menu_page( __( 'Werbung', 'tamil-site' ), __( 'Werbung', 'tamil-site' ), TAMIL_SITE_WERBUNG_RECHT, 'tamil-werbung', 'tamil_site_werbung_admin_seite', 'dashicons-megaphone', 26 );
	add_submenu_page( 'tamil-werbung', __( 'Buchungen', 'tamil-site' ), __( 'Buchungen', 'tamil-site' ), TAMIL_SITE_WERBUNG_RECHT, 'tamil-werbung', 'tamil_site_werbung_admin_seite' );
	add_submenu_page( 'tamil-werbung', __( 'Angebote', 'tamil-site' ), __( 'Angebote', 'tamil-site' ), TAMIL_SITE_WERBUNG_RECHT, 'tamil-werbung-angebote', 'tamil_site_werbung_admin_angebote' );
}
add_action( 'admin_menu', 'tamil_site_werbung_admin_menu' );

function tamil_site_werbung_admin_url( array $args = array() ): string {
	return add_query_arg( array_merge( array( 'page' => 'tamil-werbung' ), $args ), admin_url( 'admin.php' ) );
}

/**
 * Hinweise oben auf jeder Werbungsseite: Schalter, Stripe, Testmodus.
 */
function tamil_site_werbung_admin_hinweise(): string {
	$out = '';
	if ( ! tamil_site_funktion_an( 'werbung' ) ) {
		$out .= '<div class="notice notice-warning inline"><p>' . esc_html__( 'Der Funktionsschalter „Werbebuchung“ ist aus (Einstellungen → Tamil.de Website). Die Seite „Werben“, die Auslieferung gebuchter Anzeigen und die Zahlungsmeldungen sind abgeschaltet.', 'tamil-site' ) . '</p></div>';
	}
	if ( ! tamil_site_stripe_bereit() ) {
		$out .= '<div class="notice notice-warning inline"><p>' . esc_html__( 'Stripe ist nicht eingerichtet: STRIPE_SECRET_KEY und STRIPE_WEBHOOK_SECRET fehlen in der Umgebung.', 'tamil-site' ) . '</p></div>';
	} elseif ( tamil_site_stripe_testmodus() ) {
		$out .= '<div class="notice notice-info inline"><p>' . esc_html__( 'Stripe im Testmodus: Zahlungen sind nicht echt.', 'tamil-site' ) . '</p></div>';
	}
	return $out;
}

/**
 * Buchungsliste oder Einzelansicht.
 */
function tamil_site_werbung_admin_seite(): void {
	if ( ! current_user_can( TAMIL_SITE_WERBUNG_RECHT ) ) {
		wp_die( esc_html__( 'Keine Berechtigung.', 'tamil-site' ), 403 );
	}
	// phpcs:ignore WordPress.Security.NonceVerification.Recommended -- nur Anzeige
	$id = isset( $_GET['buchung'] ) ? absint( $_GET['buchung'] ) : 0;
	echo '<div class="wrap">';
	if ( $id ) {
		tamil_site_werbung_admin_einzeln( $id );
		echo '</div>';
		return;
	}
	global $wpdb;
	tamil_site_werbung_aufraeumen();
	// phpcs:ignore WordPress.Security.NonceVerification.Recommended -- Filter der Anzeige
	$filter  = isset( $_GET['stand'] ) ? sanitize_key( wp_unslash( $_GET['stand'] ) ) : '';
	$zeilen  = (array) $wpdb->get_results( $wpdb->prepare( 'SELECT * FROM %i ORDER BY id DESC LIMIT 500', tamil_site_werbung_tabelle( 'buchungen' ) ), ARRAY_A );
	$staende = tamil_site_werbung_staende();
	echo '<h1>' . esc_html__( 'Werbebuchungen', 'tamil-site' ) . '</h1>' . wp_kses_post( tamil_site_werbung_admin_hinweise() );
	echo '<ul class="subsubsub"><li><a href="' . esc_url( tamil_site_werbung_admin_url() ) . '">' . esc_html__( 'Alle', 'tamil-site' ) . '</a></li>';
	foreach ( $staende as $schluessel => $name ) {
		echo ' | <li><a href="' . esc_url( tamil_site_werbung_admin_url( array( 'stand' => $schluessel ) ) ) . '"' . ( $filter === $schluessel ? ' class="current"' : '' ) . '>' . esc_html( $name ) . '</a></li>';
	}
	/* translators: %d: Tage */
	echo '</ul><p class="description" style="clear:both">' . esc_html( sprintf( __( 'Nie bezahlte Buchungen: Die Werbemittel werden gelöscht, sobald die Reservierung verfällt; die Personendaten nach %d Tagen. Bezahlte Buchungen bleiben für die steuerliche Aufbewahrung.', 'tamil-site' ), TAMIL_SITE_WERBUNG_FRIST_UNBEZAHLT_TAGE ) ) . '</p>';
	echo '<table class="widefat striped"><thead><tr><th>' . esc_html__( 'Nummer', 'tamil-site' ) . '</th><th>' . esc_html__( 'Platz', 'tamil-site' ) . '</th><th>' . esc_html__( 'Zeitraum', 'tamil-site' ) . '</th><th>' . esc_html__( 'Firma', 'tamil-site' ) . '</th><th>' . esc_html__( 'Betrag', 'tamil-site' ) . '</th><th>' . esc_html__( 'Stand', 'tamil-site' ) . '</th><th>' . esc_html__( 'Warnung', 'tamil-site' ) . '</th></tr></thead><tbody>';
	$anzahl = 0;
	foreach ( $zeilen as $b ) {
		$stand = tamil_site_werbung_stand( $b );
		if ( '' !== $filter && $filter !== $stand ) {
			continue;
		}
		++$anzahl;
		printf(
			'<tr><td><a href="%1$s"><strong>%2$s</strong></a></td><td>%3$s</td><td>%4$s – %5$s</td><td>%6$s</td><td>%7$s</td><td>%8$s</td><td>%9$s</td></tr>',
			esc_url( tamil_site_werbung_admin_url( array( 'buchung' => (int) $b['id'] ) ) ),
			esc_html( $b['nummer'] ),
			esc_html( tamil_site_werbung_formate()[ $b['platz'] ]['name'] ?? $b['platz'] ),
			esc_html( tamil_site_werbung_datum_text( $b['start'] ) ),
			esc_html( tamil_site_werbung_datum_text( $b['ende'] ) ),
			esc_html( $b['firma'] ),
			esc_html( tamil_site_werbung_betrag_text( (int) $b['betrag'] ) ),
			esc_html( $staende[ $stand ] ),
			'' !== $b['warnung'] ? '<span class="dashicons dashicons-warning" aria-hidden="true"></span> ' . esc_html( $b['warnung'] ) : ''
		);
	}
	if ( ! $anzahl ) {
		echo '<tr><td colspan="7">' . esc_html__( 'Keine Buchungen.', 'tamil-site' ) . '</td></tr>';
	}
	echo '</tbody></table></div>';
}

/**
 * Knopf für eine Handlung an einer Buchung.
 */
function tamil_site_werbung_admin_knopf( int $id, string $aktion, string $text, string $zusatz = '' ): string {
	return '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '" class="tamil-wb-aktion" style="display:inline-block;margin:0 .5em .5em 0">'
		. wp_nonce_field( 'tamil_wb_verwalten_' . $id, '_wpnonce', false, false )
		. '<input type="hidden" name="action" value="tamil_wb_verwalten"><input type="hidden" name="buchung" value="' . esc_attr( (string) $id ) . '"><input type="hidden" name="aktion" value="' . esc_attr( $aktion ) . '">'
		. $zusatz . '<button type="submit" class="button">' . esc_html( $text ) . '</button></form>';
}

/**
 * Einzelansicht einer Buchung.
 */
function tamil_site_werbung_admin_einzeln( int $id ): void {
	$b = tamil_site_werbung_buchung( $id );
	if ( ! $b ) {
		echo '<h1>' . esc_html__( 'Buchung nicht gefunden', 'tamil-site' ) . '</h1>';
		return;
	}
	$stand = tamil_site_werbung_stand( $b );
	/* translators: %s: Buchungsnummer */
	echo '<h1>' . esc_html( sprintf( __( 'Buchung %s', 'tamil-site' ), $b['nummer'] ) ) . '</h1>' . wp_kses_post( tamil_site_werbung_admin_hinweise() );
	// phpcs:ignore WordPress.Security.NonceVerification.Recommended -- nur Anzeige der Rückmeldung
	$ergebnis = isset( $_GET['ergebnis'] ) ? sanitize_key( wp_unslash( $_GET['ergebnis'] ) ) : '';
	if ( 'ok' === $ergebnis ) {
		echo '<div class="notice notice-success"><p>' . esc_html__( 'Erledigt.', 'tamil-site' ) . '</p></div>';
	} elseif ( 'nein' === $ergebnis ) {
		echo '<div class="notice notice-error"><p>' . esc_html__( 'Nicht möglich im jetzigen Stand.', 'tamil-site' ) . '</p></div>';
	}
	if ( '' !== $b['warnung'] ) {
		echo '<div class="notice notice-error"><p><strong>' . esc_html__( 'Warnung:', 'tamil-site' ) . '</strong> ' . esc_html( $b['warnung'] ) . '</p></div>';
	}
	$felder = array(
		__( 'Stand', 'tamil-site' )            => tamil_site_werbung_staende()[ $stand ],
		__( 'Platz', 'tamil-site' )            => ( tamil_site_werbung_formate()[ $b['platz'] ]['name'] ?? $b['platz'] ) . ' (' . tamil_site_werbung_html_masse( $b['platz'] ) . ')',
		__( 'Zeitraum', 'tamil-site' )         => tamil_site_werbung_datum_text( $b['start'] ) . ' – ' . tamil_site_werbung_datum_text( $b['ende'] ) . ' (' . (int) $b['laufzeit'] . ' ' . __( 'Tage', 'tamil-site' ) . ')',
		__( 'Betrag', 'tamil-site' )           => tamil_site_werbung_betrag_text( (int) $b['betrag'] ),
		__( 'Zahlung', 'tamil-site' )          => $b['zahlung'] . ( '' !== $b['stripe_zahlung'] ? ' (' . $b['stripe_zahlung'] . ')' : '' ),
		__( 'Prüfung', 'tamil-site' )          => $b['pruefung'] . ( '' !== $b['ablehnungsgrund'] ? ': ' . $b['ablehnungsgrund'] : '' ),
		__( 'Pausiert', 'tamil-site' )         => $b['pausiert'] ? __( 'ja', 'tamil-site' ) : __( 'nein', 'tamil-site' ),
		__( 'Firma', 'tamil-site' )            => $b['firma'],
		__( 'Ansprechperson', 'tamil-site' )   => $b['ansprechperson'],
		__( 'Rechnungsadresse', 'tamil-site' ) => $b['rechnungsadresse'],
		__( 'E-Mail', 'tamil-site' )           => $b['email'],
		__( 'Telefon', 'tamil-site' )          => $b['telefon'],
		__( 'USt-ID', 'tamil-site' )           => $b['ust_id'],
		__( 'Zieladresse', 'tamil-site' )      => $b['ziel_url'],
		__( 'Bedingungen', 'tamil-site' )      => $b['bedingungen_fassung'] . ( $b['bedingungen_at'] ? ' (' . $b['bedingungen_at'] . ' UTC)' : '' ),
	);
	echo '<table class="form-table" role="presentation"><tbody>';
	foreach ( $felder as $name => $wert ) {
		echo '<tr><th scope="row">' . esc_html( $name ) . '</th><td>' . nl2br( esc_html( (string) $wert ) ) . '</td></tr>';
	}
	echo '</tbody></table><h2>' . esc_html__( 'Werbemittel', 'tamil-site' ) . '</h2>';
	foreach ( array( 'werbemittel_desktop', 'werbemittel_mobil' ) as $feld ) {
		if ( '' !== $b[ $feld ] ) {
			echo '<p><img src="' . esc_url( tamil_site_werbung_bild_url( (string) $b[ $feld ] ) ) . '" alt="" style="max-width:100%;height:auto;border:1px solid #ccc"></p>';
		}
	}
	echo '<h2>' . esc_html__( 'Handlungen', 'tamil-site' ) . '</h2><p>';
	// phpcs:disable WordPress.Security.EscapeOutput.OutputNotEscaped -- Knöpfe sind escaped
	if ( 'bezahlt' === $b['zahlung'] && 'offen' === $b['pruefung'] ) {
		echo tamil_site_werbung_admin_knopf( $id, 'freigeben', __( 'Geprüft: freigeben', 'tamil-site' ) );
		echo tamil_site_werbung_admin_knopf( $id, 'ablehnen', __( 'Ablehnen und erstatten', 'tamil-site' ), '<label for="tamil-wb-grund">' . esc_html__( 'Grund (sieht der Kunde)', 'tamil-site' ) . '</label> <input type="text" id="tamil-wb-grund" name="grund" required class="regular-text"> ' );
	}
	if ( 'bezahlt' === $b['zahlung'] && empty( $b['beendet_at'] ) && 'abgelehnt' !== $b['pruefung'] ) {
		echo $b['pausiert'] ? tamil_site_werbung_admin_knopf( $id, 'fortsetzen', __( 'Fortsetzen', 'tamil-site' ) ) : tamil_site_werbung_admin_knopf( $id, 'pausieren', __( 'Pausieren', 'tamil-site' ) );
		echo tamil_site_werbung_admin_knopf( $id, 'beenden', __( 'Vorzeitig beenden', 'tamil-site' ) );
	}
	if ( 'bezahlt' === $b['zahlung'] && ( 'abgelehnt' === $b['pruefung'] || ! empty( $b['beendet_at'] ) ) ) {
		echo tamil_site_werbung_admin_knopf( $id, 'erstatten', __( 'Voll erstatten', 'tamil-site' ) );
	}
	// phpcs:enable WordPress.Security.EscapeOutput.OutputNotEscaped
	echo '</p><h2>' . esc_html__( 'Statistik', 'tamil-site' ) . '</h2>';
	$stat = tamil_site_werbung_statistik( $id );
	echo '<table class="widefat striped" style="max-width:40em"><thead><tr><th>' . esc_html__( 'Tag', 'tamil-site' ) . '</th><th>' . esc_html__( 'Einblendungen', 'tamil-site' ) . '</th><th>' . esc_html__( 'Klicks', 'tamil-site' ) . '</th></tr></thead><tbody>';
	foreach ( $stat as $z ) {
		echo '<tr><td>' . esc_html( tamil_site_werbung_datum_text( $z['tag'] ) ) . '</td><td>' . esc_html( (string) $z['einblendungen'] ) . '</td><td>' . esc_html( (string) $z['klicks'] ) . '</td></tr>';
	}
	if ( ! $stat ) {
		echo '<tr><td colspan="3">' . esc_html__( 'Noch keine Zahlen.', 'tamil-site' ) . '</td></tr>';
	}
	echo '</tbody></table><p><a class="button" href="' . esc_url( add_query_arg( array( 'action' => 'tamil_wb_export', 'buchung' => $id, '_wpnonce' => wp_create_nonce( 'tamil_wb_export_' . $id ) ), admin_url( 'admin-post.php' ) ) ) . '">' . esc_html__( 'Als CSV exportieren', 'tamil-site' ) . '</a></p>'; // phpcs:ignore WordPress.Arrays.ArrayDeclarationSpacing.AssociativeArrayFound
	echo '<h2>' . esc_html__( 'Protokoll', 'tamil-site' ) . '</h2><table class="widefat striped"><thead><tr><th>' . esc_html__( 'Zeit (UTC)', 'tamil-site' ) . '</th><th>' . esc_html__( 'Wer', 'tamil-site' ) . '</th><th>' . esc_html__( 'Was', 'tamil-site' ) . '</th></tr></thead><tbody>';
	foreach ( tamil_site_werbung_protokoll_lesen( $id ) as $z ) {
		echo '<tr><td>' . esc_html( $z['zeit'] ) . '</td><td>' . esc_html( $z['wer'] ) . '</td><td>' . esc_html( $z['was'] ) . '</td></tr>';
	}
	echo '</tbody></table><p><a href="' . esc_url( tamil_site_werbung_admin_url() ) . '">' . esc_html__( '← Alle Buchungen', 'tamil-site' ) . '</a></p>';
}

/**
 * admin-post.php?action=tamil_wb_verwalten
 */
function tamil_site_werbung_admin_handlung(): void {
	$id = isset( $_POST['buchung'] ) ? absint( $_POST['buchung'] ) : 0; // phpcs:ignore WordPress.Security.NonceVerification.Missing -- Nonce folgt mit der ID
	if ( ! current_user_can( TAMIL_SITE_WERBUNG_RECHT ) || ! check_admin_referer( 'tamil_wb_verwalten_' . $id ) ) {
		wp_die( esc_html__( 'Keine Berechtigung.', 'tamil-site' ), 403 );
	}
	$aktion = isset( $_POST['aktion'] ) ? sanitize_key( wp_unslash( $_POST['aktion'] ) ) : '';
	$grund  = isset( $_POST['grund'] ) ? sanitize_text_field( wp_unslash( $_POST['grund'] ) ) : '';
	switch ( $aktion ) {
		case 'freigeben':
			$ok = tamil_site_werbung_freigeben( $id );
			break;
		case 'ablehnen':
			$ok = '' !== $grund && tamil_site_werbung_ablehnen( $id, substr( $grund, 0, 500 ) );
			break;
		case 'pausieren':
			$ok = tamil_site_werbung_pausieren( $id, true );
			break;
		case 'fortsetzen':
			$ok = tamil_site_werbung_pausieren( $id, false );
			break;
		case 'beenden':
			$ok = tamil_site_werbung_beenden( $id );
			break;
		case 'erstatten':
			$ok = tamil_site_werbung_erstatten( $id );
			break;
		default:
			$ok = false;
	}
	wp_safe_redirect(
		tamil_site_werbung_admin_url(
			array(
				'buchung'  => $id,
				'ergebnis' => $ok ? 'ok' : 'nein',
			)
		)
	);
	exit;
}
add_action( 'admin_post_tamil_wb_verwalten', 'tamil_site_werbung_admin_handlung' );

/**
 * admin-post.php?action=tamil_wb_export – Statistik einer Buchung als CSV.
 */
function tamil_site_werbung_admin_export(): void {
	$id = isset( $_GET['buchung'] ) ? absint( $_GET['buchung'] ) : 0; // phpcs:ignore WordPress.Security.NonceVerification.Recommended -- Nonce folgt mit der ID
	if ( ! current_user_can( TAMIL_SITE_WERBUNG_RECHT ) || ! check_admin_referer( 'tamil_wb_export_' . $id ) ) {
		wp_die( esc_html__( 'Keine Berechtigung.', 'tamil-site' ), 403 );
	}
	$b = tamil_site_werbung_buchung( $id );
	if ( ! $b ) {
		wp_die( esc_html__( 'Buchung nicht gefunden.', 'tamil-site' ), 404 );
	}
	header( 'Content-Type: text/csv; charset=utf-8' );
	header( 'Content-Disposition: attachment; filename="werbung-' . sanitize_file_name( strtolower( $b['nummer'] ) ) . '.csv"' );
	$zeilen = array( 'buchung;tag;einblendungen;klicks' );
	foreach ( tamil_site_werbung_statistik( $id ) as $z ) {
		$zeilen[] = implode( ';', array( $b['nummer'], $z['tag'], $z['einblendungen'], $z['klicks'] ) );
	}
	echo esc_html( implode( "\n", $zeilen ) ) . "\n";
	exit;
}
add_action( 'admin_post_tamil_wb_export', 'tamil_site_werbung_admin_export' );

/**
 * Euro-Eingabe in Cent; leer = 0 (Preis folgt), unlesbar = null.
 * Deutsche Schreibweise: Punkt mit genau drei Ziffern danach trennt Tausender („1.250“ = 1250 €), Komma trennt Cent
 * („1.250,50“). Ein Punkt mit einer oder zwei Ziffern danach gilt als Dezimalpunkt („12.50“).
 */
function tamil_site_werbung_cent( string $eingabe ): ?int {
	$eingabe = trim( str_replace( array( '€', ' ', "\u{00A0}" ), '', $eingabe ) );
	if ( '' === $eingabe ) {
		return 0;
	}
	if ( preg_match( '/^(\d{1,3}(?:\.\d{3})+)(?:,(\d{1,2}))?$/', $eingabe, $m ) || preg_match( '/^(\d+)(?:,(\d{1,2}))?$/', $eingabe, $m ) ) {
		$euro = (int) str_replace( '.', '', $m[1] );
		$cent = isset( $m[2] ) ? (int) str_pad( $m[2], 2, '0' ) : 0;
		return $euro * 100 + $cent;
	}
	if ( preg_match( '/^(\d+)\.(\d{1,2})$/', $eingabe, $m ) ) {
		return (int) $m[1] * 100 + (int) str_pad( $m[2], 2, '0' );
	}
	return null;
}

/**
 * Angebote bearbeiten.
 */
function tamil_site_werbung_admin_angebote(): void {
	if ( ! current_user_can( TAMIL_SITE_WERBUNG_RECHT ) ) {
		wp_die( esc_html__( 'Keine Berechtigung.', 'tamil-site' ), 403 );
	}
	$a = tamil_site_werbung_angebote();
	echo '<div class="wrap"><h1>' . esc_html__( 'Werbung: Angebote', 'tamil-site' ) . '</h1>';
	echo wp_kses_post( tamil_site_werbung_admin_hinweise() );
	// phpcs:ignore WordPress.Security.NonceVerification.Recommended -- nur Anzeige der Rückmeldung
	if ( isset( $_GET['gespeichert'] ) ) {
		echo '<div class="notice notice-success"><p>' . esc_html__( 'Gespeichert.', 'tamil-site' ) . '</p></div>';
	}
	// phpcs:ignore WordPress.Security.NonceVerification.Recommended -- nur Anzeige der Rückmeldung
	$ungueltig = isset( $_GET['ungueltig'] ) ? absint( $_GET['ungueltig'] ) : 0;
	if ( $ungueltig ) {
		/* translators: %d: Anzahl */
		echo '<div class="notice notice-error"><p>' . esc_html( sprintf( _n( '%d Preis war nicht lesbar und wurde nicht übernommen (bisheriger Wert bleibt). Beispiele: 1.250 oder 1.250,50 oder 99,90.', '%d Preise waren nicht lesbar und wurden nicht übernommen (bisherige Werte bleiben). Beispiele: 1.250 oder 1.250,50 oder 99,90.', $ungueltig, 'tamil-site' ), $ungueltig ) ) . '</p></div>';
	}
	echo '<p>' . esc_html__( 'Preise in Euro inklusive Umsatzsteuer. Ein leeres Feld heißt „Preis folgt“: Dann ist die Laufzeit an diesem Platz nicht buchbar. Je Platz läuft zur selben Zeit eine Anzeige (exklusiv); Wechsel mehrerer Anzeigen ist nicht Teil dieses Bausteins.', 'tamil-site' ) . '</p>';
	echo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '">';
	wp_nonce_field( 'tamil_wb_angebote' );
	echo '<input type="hidden" name="action" value="tamil_wb_angebote"><table class="form-table" role="presentation"><tbody>';
	echo '<tr><th scope="row"><label for="tamil-wb-laufzeiten">' . esc_html__( 'Laufzeiten in Tagen', 'tamil-site' ) . '</label></th><td><input type="text" id="tamil-wb-laufzeiten" name="laufzeiten" value="' . esc_attr( implode( ', ', $a['laufzeiten'] ) ) . '" class="regular-text"><p class="description">' . esc_html__( 'Mit Komma getrennt, z. B. 7, 14, 30.', 'tamil-site' ) . '</p></td></tr>';
	echo '<tr><th scope="row"><label for="tamil-wb-vorlauf">' . esc_html__( 'Vorlauf in Werktagen', 'tamil-site' ) . '</label></th><td><input type="number" min="0" max="30" id="tamil-wb-vorlauf" name="vorlauf" value="' . esc_attr( (string) $a['vorlauf'] ) . '" class="small-text"></td></tr>';
	echo '<tr><th scope="row"><label for="tamil-wb-fassung">' . esc_html__( 'Fassung der Verkaufsbedingungen', 'tamil-site' ) . '</label></th><td><input type="text" id="tamil-wb-fassung" name="bedingungen_fassung" value="' . esc_attr( $a['bedingungen_fassung'] ) . '" class="regular-text"><p class="description">' . esc_html__( 'Wird mit jeder Buchung gespeichert. Leer: „Entwurf“.', 'tamil-site' ) . '</p></td></tr>';
	echo '</tbody></table><table class="widefat striped"><thead><tr><th>' . esc_html__( 'Platz', 'tamil-site' ) . '</th><th>' . esc_html__( 'Buchbar', 'tamil-site' ) . '</th>';
	foreach ( $a['laufzeiten'] as $tage ) {
		/* translators: %d: Tage */
		echo '<th>' . esc_html( sprintf( __( 'Preis %d Tage (€)', 'tamil-site' ), $tage ) ) . '</th>';
	}
	echo '<th>' . esc_html__( 'Gleichzeitig', 'tamil-site' ) . '</th></tr></thead><tbody>';
	foreach ( tamil_site_werbung_formate() as $platz => $f ) {
		echo '<tr><th scope="row">' . esc_html( $f['name'] . ' (' . tamil_site_werbung_html_masse( $platz ) . ')' ) . '</th>';
		echo '<td><input type="checkbox" name="plaetze[' . esc_attr( $platz ) . '][aktiv]" value="1"' . checked( ! empty( $a['plaetze'][ $platz ]['aktiv'] ), true, false ) . ' aria-label="' . esc_attr( $f['name'] ) . '"></td>';
		foreach ( $a['laufzeiten'] as $tage ) {
			$cent = (int) $a['plaetze'][ $platz ]['preise'][ $tage ];
			echo '<td><input type="text" inputmode="decimal" size="9" name="plaetze[' . esc_attr( $platz ) . '][preise][' . esc_attr( (string) $tage ) . ']" value="' . esc_attr( $cent ? number_format( $cent / 100, 2, ',', '' ) : '' ) . '" placeholder="' . esc_attr__( 'Preis folgt', 'tamil-site' ) . '"></td>';
		}
		echo '<td>1</td></tr>';
	}
	echo '</tbody></table>';
	submit_button( __( 'Angebote speichern', 'tamil-site' ) );
	echo '</form></div>';
}

/**
 * admin-post.php?action=tamil_wb_angebote
 */
function tamil_site_werbung_admin_angebote_speichern(): void {
	if ( ! current_user_can( TAMIL_SITE_WERBUNG_RECHT ) || ! check_admin_referer( 'tamil_wb_angebote' ) ) {
		wp_die( esc_html__( 'Keine Berechtigung.', 'tamil-site' ), 403 );
	}
	$laufzeiten = isset( $_POST['laufzeiten'] ) ? sanitize_text_field( wp_unslash( $_POST['laufzeiten'] ) ) : '';
	$laufzeiten = array_values( array_unique( array_filter( array_map( 'absint', explode( ',', $laufzeiten ) ), static fn( $t ) => $t >= 1 && $t <= 365 ) ) );
	sort( $laufzeiten );
	$plaetze   = array();
	$ungueltig = 0;
	$bisher    = tamil_site_werbung_angebote();
	// phpcs:ignore WordPress.Security.ValidatedSanitizedInput.InputNotSanitized -- jedes Feld wird unten einzeln bereinigt
	$roh = isset( $_POST['plaetze'] ) && is_array( $_POST['plaetze'] ) ? wp_unslash( $_POST['plaetze'] ) : array();
	foreach ( array_keys( tamil_site_werbung_formate() ) as $platz ) {
		$preise = array();
		foreach ( $laufzeiten as $tage ) {
			$cent = tamil_site_werbung_cent( sanitize_text_field( (string) ( $roh[ $platz ]['preise'][ $tage ] ?? '' ) ) );
			if ( null === $cent ) {
				++$ungueltig; // unlesbar: bisherigen Preis behalten
				$cent = (int) ( $bisher['plaetze'][ $platz ]['preise'][ $tage ] ?? 0 );
			}
			$preise[ $tage ] = $cent;
		}
		$plaetze[ $platz ] = array(
			'aktiv'  => ! empty( $roh[ $platz ]['aktiv'] ),
			'preise' => $preise,
		);
	}
	update_option(
		'tamil_site_werbung_angebote',
		array(
			'laufzeiten'          => $laufzeiten ? $laufzeiten : array( 7, 14, 30 ),
			'vorlauf'             => isset( $_POST['vorlauf'] ) ? min( 30, absint( $_POST['vorlauf'] ) ) : 2,
			'bedingungen_fassung' => isset( $_POST['bedingungen_fassung'] ) ? substr( sanitize_text_field( wp_unslash( $_POST['bedingungen_fassung'] ) ), 0, 60 ) : '',
			'plaetze'             => $plaetze,
		),
		false
	);
	wp_safe_redirect( add_query_arg( array( 'page' => 'tamil-werbung-angebote', 'gespeichert' => 1, 'ungueltig' => $ungueltig ), admin_url( 'admin.php' ) ) ); // phpcs:ignore WordPress.Arrays.ArrayDeclarationSpacing.AssociativeArrayFound
	exit;
}
add_action( 'admin_post_tamil_wb_angebote', 'tamil_site_werbung_admin_angebote_speichern' );
