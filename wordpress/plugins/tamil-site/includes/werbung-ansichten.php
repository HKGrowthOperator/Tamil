<?php
/**
 * Ausgaben der Seite „Werben“ (Teil von werbung-seiten.php): Angebote, Buchungsschritte, Zusammenfassung, Meldungen,
 * Kundenübersicht. Alles escaped; Klassen wb-…
 */

defined( 'ABSPATH' ) || exit;

/**
 * Versteckte Felder für GET-Formulare: die Abfrageparameter der Seitenadresse (z. B. page_id ohne schöne Links).
 *
 * @param array<string,string|int> $weitere Zusätzliche Felder.
 */
function tamil_site_werbung_html_versteckt( array $weitere ): string {
	$felder = array();
	wp_parse_str( (string) wp_parse_url( tamil_site_werbung_seite_url(), PHP_URL_QUERY ), $felder );
	$out = '';
	foreach ( array_merge( $felder, $weitere ) as $name => $wert ) {
		$out .= '<input type="hidden" name="' . esc_attr( (string) $name ) . '" value="' . esc_attr( (string) $wert ) . '">';
	}
	return $out;
}

/**
 * Formatbeschreibung, z. B. „728 × 90 (Desktop) / 320 × 50 (Handy)“.
 */
function tamil_site_werbung_html_masse( string $platz ): string {
	$f = tamil_site_werbung_formate()[ $platz ];
	if ( ! tamil_site_werbung_zwei_bilder( $platz ) ) {
		return sprintf( '%d × %d', $f['desktop'][0], $f['desktop'][1] );
	}
	/* translators: 1–4: Pixelmaße */
	return sprintf( __( '%1$d × %2$d (Desktop) / %3$d × %4$d (Handy)', 'tamil-site' ), $f['desktop'][0], $f['desktop'][1], $f['mobil'][0], $f['mobil'][1] );
}

function tamil_site_werbung_datum_text( string $tag ): string {
	return mysql2date( 'd.m.Y', $tag );
}

/**
 * Preisseite: Plätze, Maße, Position, Preise je Laufzeit, nächster freier Termin.
 */
function tamil_site_werbung_html_angebote(): string {
	$a      = tamil_site_werbung_angebote();
	$zeilen = '';
	$fehlt  = false;
	foreach ( tamil_site_werbung_formate() as $platz => $f ) {
		if ( empty( $a['plaetze'][ $platz ]['aktiv'] ) ) {
			continue;
		}
		$preise = '';
		foreach ( $a['laufzeiten'] as $tage ) {
			$cent  = tamil_site_werbung_preis( $platz, $tage );
			$fehlt = $fehlt || ! $cent;
			/* translators: %d: Tage */
			$preise .= '<li>' . esc_html( sprintf( _n( '%d Tag', '%d Tage', $tage, 'tamil-site' ), $tage ) ) . ': '
				. ( $cent ? esc_html( tamil_site_werbung_betrag_text( $cent ) ) : '<span class="wb-platzhalter">' . esc_html__( 'Preis folgt', 'tamil-site' ) . '</span>' ) . '</li>';
		}
		$buchbar = array_filter(
			$a['laufzeiten'],
			static function ( $tage ) use ( $platz ) {
				return tamil_site_werbung_buchbar( $platz, $tage );
			}
		);
		$frei    = $buchbar ? tamil_site_werbung_freie_starts( $platz, min( $buchbar ), 1 ) : array();
		$termin  = $frei ? tamil_site_werbung_datum_text( $frei[0] ) : '–';
		$link    = $buchbar ? '<a class="wb-knopf" href="' . esc_url(
			add_query_arg(
				array(
					'wb'    => 'buchen',
					'platz' => $platz,
				),
				tamil_site_werbung_seite_url()
			)
		) . '">' . esc_html__( 'Buchen', 'tamil-site' ) . '</a>' : '';
		$zeilen .= sprintf(
			'<tr><th scope="row">%1$s</th><td data-label="%7$s">%2$s</td><td data-label="%8$s">%3$s</td><td data-label="%9$s"><ul class="wb-preise">%4$s</ul></td><td data-label="%10$s">%5$s</td><td>%6$s</td></tr>',
			esc_html( $f['name'] ),
			esc_html( $f['wo'] ),
			esc_html( tamil_site_werbung_html_masse( $platz ) ),
			$preise,
			esc_html( $termin ),
			$link,
			esc_attr__( 'Wo', 'tamil-site' ),
			esc_attr__( 'Maße in Pixel', 'tamil-site' ),
			esc_attr__( 'Preis je Laufzeit', 'tamil-site' ),
			esc_attr__( 'Nächster freier Termin', 'tamil-site' )
		);
	}
	$out  = '<section class="wb-angebote"><h2>' . esc_html__( 'Werbeplätze und Preise', 'tamil-site' ) . '</h2>';
	$out .= '<div class="wb-tabelle-wrap"><table class="wb-tabelle"><thead><tr><th scope="col">' . esc_html__( 'Platz', 'tamil-site' ) . '</th><th scope="col">'
		. esc_html__( 'Wo', 'tamil-site' ) . '</th><th scope="col">' . esc_html__( 'Maße in Pixel', 'tamil-site' ) . '</th><th scope="col">'
		. esc_html__( 'Preis je Laufzeit', 'tamil-site' ) . '</th><th scope="col">' . esc_html__( 'Nächster freier Termin', 'tamil-site' )
		. '</th><th scope="col"><span class="screen-reader-text">' . esc_html__( 'Buchen', 'tamil-site' ) . '</span></th></tr></thead><tbody>' . $zeilen . '</tbody></table></div>';
	$out .= '<p class="wb-hinweis">' . esc_html__( 'Preise inklusive Umsatzsteuer. Je Platz läuft zur selben Zeit genau eine Anzeige. Jedes Werbemittel wird vor dem Start geprüft; Vorlauf zwei Werktage. Bilder als JPEG oder PNG in den genannten Maßen.', 'tamil-site' ) . '</p>';
	if ( $fehlt ) {
		$out .= '<p class="wb-hinweis wb-platzhalter">' . esc_html__( 'Platzhalter: Die Preise liefert der Herausgeber. Plätze ohne Preis sind noch nicht buchbar.', 'tamil-site' ) . '</p>';
	}
	$out .= '</section>';
	return $out . tamil_site_werbung_html_wiederfinden();
}

/**
 * Formular „Buchung wiederfinden“.
 */
function tamil_site_werbung_html_wiederfinden(): string {
	$alt = tamil_site_werbung_zustand()['alt'];
	return '<section class="wb-wiederfinden"><h2>' . esc_html__( 'Buchung wiederfinden', 'tamil-site' ) . '</h2>'
		. '<p>' . esc_html__( 'Link zur Buchung verloren? Mit Buchungsnummer und E-Mail-Adresse erhalten Sie hier einen neuen Link; der alte gilt dann nicht mehr.', 'tamil-site' ) . '</p>'
		. '<form class="wb-formular" method="post" action="' . esc_url( tamil_site_werbung_seite_url() ) . '">'
		. wp_nonce_field( 'tamil_wb_wiederfinden', '_wpnonce', false, false )
		. '<input type="hidden" name="tamil_wb_aktion" value="wiederfinden">'
		. '<label for="wb-such-nummer">' . esc_html__( 'Buchungsnummer', 'tamil-site' ) . '</label><input type="text" id="wb-such-nummer" name="nummer" required autocomplete="off" value="' . esc_attr( (string) ( $alt['nummer'] ?? '' ) ) . '">'
		. '<label for="wb-such-email">' . esc_html__( 'E-Mail-Adresse der Buchung', 'tamil-site' ) . '</label><input type="email" id="wb-such-email" name="email" required autocomplete="email">'
		. '<p><button type="submit">' . esc_html__( 'Buchung anzeigen', 'tamil-site' ) . '</button></p></form></section>';
}

/**
 * Schritte 1 bis 4.
 */
function tamil_site_werbung_html_buchen(): string {
	$a        = tamil_site_werbung_angebote();
	$z        = tamil_site_werbung_zustand();
	$alt      = $z['alt'];
	$platz    = sanitize_key( (string) ( $alt['platz'] ?? tamil_site_werbung_get( 'platz' ) ) );
	$laufzeit = absint( $alt['laufzeit'] ?? tamil_site_werbung_get( 'laufzeit' ) );
	$start    = (string) ( $alt['start'] ?? tamil_site_werbung_get( 'start' ) );
	$url      = tamil_site_werbung_seite_url();
	$out      = '<section class="wb-buchen"><h2>' . esc_html__( 'Werbeplatz buchen', 'tamil-site' ) . '</h2>';

	// Schritt 1: Platz und Laufzeit
	$plaetze = '';
	foreach ( tamil_site_werbung_formate() as $p => $f ) {
		if ( ! empty( $a['plaetze'][ $p ]['aktiv'] ) ) {
			$plaetze .= '<option value="' . esc_attr( $p ) . '"' . selected( $p, $platz, false ) . '>' . esc_html( $f['name'] . ' – ' . tamil_site_werbung_html_masse( $p ) ) . '</option>';
		}
	}
	$laufzeiten = '';
	foreach ( $a['laufzeiten'] as $tage ) {
		$cent        = '' !== $platz ? tamil_site_werbung_preis( $platz, $tage ) : 0;
		$laufzeiten .= '<label><input type="radio" name="laufzeit" value="' . esc_attr( (string) $tage ) . '"' . checked( $tage, $laufzeit, false ) . ' required> '
			/* translators: %d: Tage */
			. esc_html( sprintf( _n( '%d Tag', '%d Tage', $tage, 'tamil-site' ), $tage ) )
			. ( $cent ? ' – ' . esc_html( tamil_site_werbung_betrag_text( $cent ) ) : '' ) . '</label>';
	}
	$out .= '<form class="wb-formular wb-schritt" method="get" action="' . esc_url( strtok( $url, '?' ) ) . '"><h3>' . esc_html__( '1. Platz und Laufzeit', 'tamil-site' ) . '</h3>'
		. tamil_site_werbung_html_versteckt( array( 'wb' => 'buchen' ) )
		. '<label for="wb-platz">' . esc_html__( 'Platz', 'tamil-site' ) . '</label><select id="wb-platz" name="platz" required>' . $plaetze . '</select>'
		. '<fieldset><legend>' . esc_html__( 'Laufzeit', 'tamil-site' ) . '</legend>' . $laufzeiten . '</fieldset>'
		. '<p><button type="submit">' . esc_html__( 'Freie Termine zeigen', 'tamil-site' ) . '</button></p></form>';
	if ( '' === $platz || ! $laufzeit ) {
		return $out . '</section>';
	}
	if ( ! tamil_site_werbung_buchbar( $platz, $laufzeit ) ) {
		return $out . '<p class="wb-hinweis">' . esc_html__( 'Dieser Platz ist mit dieser Laufzeit noch nicht buchbar (Preis folgt).', 'tamil-site' ) . '</p></section>';
	}

	// Schritt 2: Startdatum (nur freie Starttage wählbar)
	$starts = tamil_site_werbung_freie_starts( $platz, $laufzeit );
	$opt    = '';
	foreach ( $starts as $s ) {
		$opt .= '<option value="' . esc_attr( $s ) . '"' . selected( $s, $start, false ) . '>' . esc_html( tamil_site_werbung_datum_text( $s ) . ' – ' . tamil_site_werbung_datum_text( tamil_site_werbung_plus_tage( $s, $laufzeit - 1 ) ) ) . '</option>';
	}
	$out .= '<form class="wb-formular wb-schritt" method="get" action="' . esc_url( strtok( $url, '?' ) ) . '"><h3>' . esc_html__( '2. Startdatum', 'tamil-site' ) . '</h3>'
		. tamil_site_werbung_html_versteckt(
			array(
				'wb'       => 'buchen',
				'platz'    => $platz,
				'laufzeit' => $laufzeit,
			)
		)
		. ( $starts ? '<label for="wb-start">' . esc_html__( 'Zeitraum (belegte Tage sind nicht wählbar)', 'tamil-site' ) . '</label><select id="wb-start" name="start" required>' . $opt . '</select><p><button type="submit">' . esc_html__( 'Weiter', 'tamil-site' ) . '</button></p>'
			: '<p>' . esc_html__( 'In den nächsten zwölf Monaten ist kein passender Zeitraum frei.', 'tamil-site' ) . '</p>' )
		. '</form>';
	if ( ! in_array( $start, $starts, true ) ) {
		return $out . '</section>';
	}

	// Schritte 3 und 4: Kundendaten und Werbemittel
	$f    = tamil_site_werbung_formate()[ $platz ];
	$feld = static function ( string $name, string $label, string $typ = 'text', bool $pflicht = true, string $auto = '' ) use ( $alt ): string {
		$id = 'wb-' . $name;
		return '<label for="' . esc_attr( $id ) . '">' . esc_html( $label ) . ( $pflicht ? '' : ' ' . esc_html__( '(freiwillig)', 'tamil-site' ) ) . '</label>'
			. '<input type="' . esc_attr( $typ ) . '" id="' . esc_attr( $id ) . '" name="' . esc_attr( $name ) . '" value="' . esc_attr( (string) ( $alt[ $name ] ?? '' ) ) . '"'
			. ( $pflicht ? ' required' : '' ) . ( '' !== $auto ? ' autocomplete="' . esc_attr( $auto ) . '"' : '' ) . '>';
	};
	$bild = static function ( string $name, string $label, array $mass ): string {
		/* translators: 1: Breite, 2: Höhe, 3: KB */
		$hinweis = sprintf( __( 'JPEG oder PNG, genau %1$d × %2$d Pixel, höchstens %3$d KB', 'tamil-site' ), $mass[0], $mass[1], (int) ( TAMIL_SITE_WERBUNG_MAX_BYTES / 1024 ) );
		return '<label for="wb-' . esc_attr( $name ) . '">' . esc_html( $label ) . '</label><input type="file" id="wb-' . esc_attr( $name ) . '" name="' . esc_attr( $name ) . '" accept="image/jpeg,image/png" required aria-describedby="wb-' . esc_attr( $name ) . '-hinweis">'
			. '<span class="wb-feldhinweis" id="wb-' . esc_attr( $name ) . '-hinweis">' . esc_html( $hinweis ) . '</span>';
	};
	$out .= '<form class="wb-formular wb-schritt" method="post" enctype="multipart/form-data" action="' . esc_url( add_query_arg( array( 'wb' => 'buchen', 'platz' => $platz, 'laufzeit' => $laufzeit, 'start' => $start ), $url ) ) . '">' // phpcs:ignore WordPress.Arrays.ArrayDeclarationSpacing.AssociativeArrayFound
		. wp_nonce_field( 'tamil_wb_buchen', '_wpnonce', false, false )
		. '<input type="hidden" name="tamil_wb_aktion" value="buchen"><input type="hidden" name="platz" value="' . esc_attr( $platz ) . '"><input type="hidden" name="laufzeit" value="' . esc_attr( (string) $laufzeit ) . '"><input type="hidden" name="start" value="' . esc_attr( $start ) . '">'
		. '<h3>' . esc_html__( '3. Ihre Angaben', 'tamil-site' ) . '</h3>'
		. $feld( 'firma', __( 'Firma', 'tamil-site' ), 'text', true, 'organization' )
		. $feld( 'ansprechperson', __( 'Ansprechperson', 'tamil-site' ), 'text', true, 'name' )
		. '<label for="wb-rechnungsadresse">' . esc_html__( 'Rechnungsadresse', 'tamil-site' ) . '</label><textarea id="wb-rechnungsadresse" name="rechnungsadresse" rows="3" required autocomplete="street-address">' . esc_textarea( (string) ( $alt['rechnungsadresse'] ?? '' ) ) . '</textarea>'
		. $feld( 'email', __( 'E-Mail-Adresse', 'tamil-site' ), 'email', true, 'email' )
		. $feld( 'telefon', __( 'Telefon', 'tamil-site' ), 'tel', false, 'tel' )
		. $feld( 'ust_id', __( 'USt-ID', 'tamil-site' ), 'text', false )
		. '<h3>' . esc_html__( '4. Werbemittel', 'tamil-site' ) . '</h3>'
		. $bild( 'werbemittel_desktop', tamil_site_werbung_zwei_bilder( $platz ) ? __( 'Bild für große Bildschirme', 'tamil-site' ) : __( 'Bild', 'tamil-site' ), $f['desktop'] )
		. ( tamil_site_werbung_zwei_bilder( $platz ) ? $bild( 'werbemittel_mobil', __( 'Bild fürs Handy', 'tamil-site' ), $f['mobil'] ) : '' )
		. $feld( 'ziel_url', __( 'Zieladresse beim Klick (https://…)', 'tamil-site' ), 'url', true, 'url' )
		/* translators: %d: Minuten */
		. '<p class="wb-hinweis">' . esc_html( sprintf( __( 'Mit „Weiter“ werden die gewählten Tage %d Minuten für Sie reserviert. Ohne Zahlung werden sie danach wieder frei.', 'tamil-site' ), TAMIL_SITE_WERBUNG_RESERVIERUNG_MINUTEN ) ) . '</p>'
		. '<p><button type="submit">' . esc_html__( 'Weiter zur Zusammenfassung', 'tamil-site' ) . '</button></p></form>';
	return $out . '</section>';
}

/**
 * Daten einer Buchung als Liste.
 *
 * @param array<string,mixed> $b Buchung.
 */
function tamil_site_werbung_html_daten( array $b ): string {
	$f      = tamil_site_werbung_formate()[ $b['platz'] ] ?? array( 'name' => $b['platz'] );
	$zeilen = array(
		__( 'Buchungsnummer', 'tamil-site' ) => $b['nummer'],
		__( 'Platz', 'tamil-site' )          => $f['name'],
		__( 'Zeitraum', 'tamil-site' )       => tamil_site_werbung_datum_text( $b['start'] ) . ' – ' . tamil_site_werbung_datum_text( $b['ende'] ),
		__( 'Betrag', 'tamil-site' )         => tamil_site_werbung_betrag_text( (int) $b['betrag'] ) . ' ' . __( '(inkl. USt.)', 'tamil-site' ),
		__( 'Zieladresse', 'tamil-site' )    => $b['ziel_url'],
	);
	$out    = '<dl class="wb-daten">';
	foreach ( $zeilen as $name => $wert ) {
		$out .= '<dt>' . esc_html( $name ) . '</dt><dd>' . esc_html( (string) $wert ) . '</dd>';
	}
	return $out . '</dl>';
}

/**
 * Schritt 5: Zusammenfassung, Bedingungen, Bezahlen.
 */
function tamil_site_werbung_html_zusammenfassung( string $nummer ): string {
	$paar = tamil_site_werbung_cookie_buchung( $nummer );
	if ( ! $paar ) {
		return '<p>' . esc_html__( 'Diese Buchung gehört nicht zu diesem Browser oder ist abgelaufen.', 'tamil-site' ) . '</p>';
	}
	$b = $paar[0];
	if ( 'reserviert' !== tamil_site_werbung_stand( $b ) ) {
		return '<p>' . esc_html__( 'Die Reservierung ist abgelaufen; die Tage sind wieder frei.', 'tamil-site' ) . ' <a href="' . esc_url( add_query_arg( 'wb', 'buchen', tamil_site_werbung_seite_url() ) ) . '">' . esc_html__( 'Neu buchen', 'tamil-site' ) . '</a></p>';
	}
	$bed    = get_page_by_path( 'werbebedingungen', OBJECT, 'page' );
	$bed    = $bed && 'publish' === $bed->post_status ? '<a href="' . esc_url( (string) get_permalink( $bed ) ) . '" target="_blank" rel="noopener">' . esc_html__( 'Verkaufsbedingungen', 'tamil-site' ) . '</a>' : esc_html__( 'Verkaufsbedingungen (Text folgt)', 'tamil-site' );
	$bis    = wp_date( 'd.m.Y, H:i', (int) strtotime( $b['reserviert_bis'] . ' UTC' ) );
	$bilder = '<figure class="wb-vorschau"><img src="' . esc_url( tamil_site_werbung_bild_url( (string) $b['werbemittel_desktop'] ) ) . '" alt="' . esc_attr__( 'Ihr Werbemittel', 'tamil-site' ) . '"></figure>';
	if ( '' !== $b['werbemittel_mobil'] ) {
		$bilder .= '<figure class="wb-vorschau"><img src="' . esc_url( tamil_site_werbung_bild_url( (string) $b['werbemittel_mobil'] ) ) . '" alt="' . esc_attr__( 'Ihr Werbemittel fürs Handy', 'tamil-site' ) . '"></figure>';
	}
	return '<section class="wb-zusammenfassung"><h2>' . esc_html__( '5. Zusammenfassung', 'tamil-site' ) . '</h2>'
		/* translators: %s: Uhrzeit */
		. '<p>' . esc_html( sprintf( __( 'Die Tage sind bis %s Uhr für Sie reserviert.', 'tamil-site' ), $bis ) ) . '</p>'
		. tamil_site_werbung_html_daten( $b ) . $bilder
		. '<form class="wb-formular" method="post" action="' . esc_url( tamil_site_werbung_seite_url() ) . '">'
		. wp_nonce_field( 'tamil_wb_bezahlen', '_wpnonce', false, false )
		. '<input type="hidden" name="tamil_wb_aktion" value="bezahlen"><input type="hidden" name="nummer" value="' . esc_attr( $b['nummer'] ) . '">'
		/* translators: %s: Link zu den Bedingungen */
		. '<label><input type="checkbox" name="bedingungen" value="1" required> ' . sprintf( esc_html__( 'Ich nehme die %s an.', 'tamil-site' ), $bed ) . '</label>'
		. '<p class="wb-hinweis">' . esc_html__( 'Bezahlt wird auf der Seite von Stripe; Kartendaten sieht Tamil.de nicht. Das Werbemittel wird vor dem Start geprüft; bei Ablehnung wird der volle Betrag erstattet.', 'tamil-site' ) . '</p>'
		. '<p><button type="submit">' . esc_html__( 'Zahlungspflichtig buchen', 'tamil-site' ) . '</button></p></form></section>';
}

/**
 * Meldungen nach Rückkehr oder Abbruch (ohne Cookie dieses Browsers).
 */
function tamil_site_werbung_html_meldung( string $art, string $nummer ): string {
	if ( 'abbruch' === $art ) {
		return '<p>' . esc_html__( 'Die Zahlung wurde abgebrochen. Es ist keine Buchung entstanden; die Tage sind wieder frei.', 'tamil-site' ) . ' <a href="' . esc_url( tamil_site_werbung_seite_url() ) . '">' . esc_html__( 'Zurück zu den Werbeplätzen', 'tamil-site' ) . '</a></p>';
	}
	/* translators: %s: Buchungsnummer */
	return '<p>' . esc_html( sprintf( __( 'Danke. Die Zahlung zur Buchung %s wird bestätigt, sobald Stripe sie meldet.', 'tamil-site' ), $nummer ) ) . '</p>' . tamil_site_werbung_html_wiederfinden();
}

/**
 * Kundenübersicht über den geheimen Link.
 */
function tamil_site_werbung_html_kunde( string $token ): string {
	$b = tamil_site_werbung_buchung_nach_token( $token );
	if ( ! $b ) {
		return '<p>' . esc_html__( 'Dieser Link ist nicht (mehr) gültig.', 'tamil-site' ) . '</p>' . tamil_site_werbung_html_wiederfinden();
	}
	$stand    = tamil_site_werbung_stand( $b );
	$zahlung  = array(
		'offen'          => __( 'offen', 'tamil-site' ),
		'bezahlt'        => __( 'bezahlt', 'tamil-site' ),
		'fehlgeschlagen' => __( 'nicht bezahlt', 'tamil-site' ),
		'erstattet'      => __( 'erstattet', 'tamil-site' ),
	);
	$pruefung = array(
		'offen'       => __( 'in Prüfung', 'tamil-site' ),
		'freigegeben' => __( 'freigegeben', 'tamil-site' ),
		'abgelehnt'   => __( 'abgelehnt', 'tamil-site' ),
	);
	$beleg    = in_array( $b['zahlung'], array( 'bezahlt', 'erstattet' ), true ) ? tamil_site_stripe_beleg( $b ) : '';
	$link     = add_query_arg( 'buchung', $token, tamil_site_werbung_seite_url() );
	$out      = '<section class="wb-kunde"><h2>' . esc_html__( 'Ihre Buchung', 'tamil-site' ) . '</h2>'
		. '<p class="wb-hinweis">' . esc_html__( 'Diese Seite ist nur über diesen Link erreichbar. Bitte den Link aufheben; wir schicken keine E-Mail.', 'tamil-site' ) . '</p>'
		. '<p><label for="wb-link">' . esc_html__( 'Ihr Link', 'tamil-site' ) . '</label><input type="text" id="wb-link" readonly value="' . esc_attr( $link ) . '"></p>'
		. '<p class="wb-stand">' . esc_html__( 'Stand:', 'tamil-site' ) . ' <strong>' . esc_html( tamil_site_werbung_staende()[ $stand ] ) . '</strong></p>'
		. tamil_site_werbung_html_daten( $b )
		. '<dl class="wb-daten"><dt>' . esc_html__( 'Zahlung', 'tamil-site' ) . '</dt><dd>' . esc_html( $zahlung[ $b['zahlung'] ] ?? $b['zahlung'] ) . '</dd>'
		. '<dt>' . esc_html__( 'Prüfung', 'tamil-site' ) . '</dt><dd>' . esc_html( $pruefung[ $b['pruefung'] ] ?? $b['pruefung'] ) . '</dd>';
	if ( 'abgelehnt' === $b['pruefung'] && '' !== $b['ablehnungsgrund'] ) {
		$out .= '<dt>' . esc_html__( 'Grund der Ablehnung', 'tamil-site' ) . '</dt><dd>' . esc_html( (string) $b['ablehnungsgrund'] ) . '</dd>';
	}
	if ( '' !== $beleg ) {
		$out .= '<dt>' . esc_html__( 'Beleg', 'tamil-site' ) . '</dt><dd><a href="' . esc_url( $beleg ) . '" rel="noopener noreferrer" target="_blank">' . esc_html__( 'Zahlungsbeleg von Stripe', 'tamil-site' ) . '</a></dd>';
	}
	$out .= '</dl>';
	$stat = tamil_site_werbung_statistik( (int) $b['id'] );
	if ( $stat ) {
		$out .= '<h3>' . esc_html__( 'Einblendungen und Klicks', 'tamil-site' ) . '</h3><div class="wb-tabelle-wrap"><table class="wb-tabelle"><thead><tr><th scope="col">' . esc_html__( 'Tag', 'tamil-site' ) . '</th><th scope="col">' . esc_html__( 'Einblendungen', 'tamil-site' ) . '</th><th scope="col">' . esc_html__( 'Klicks', 'tamil-site' ) . '</th></tr></thead><tbody>';
		foreach ( $stat as $z ) {
			$out .= '<tr><th scope="row">' . esc_html( tamil_site_werbung_datum_text( $z['tag'] ) ) . '</th><td data-label="' . esc_attr__( 'Einblendungen', 'tamil-site' ) . '">' . esc_html( number_format_i18n( $z['einblendungen'] ) ) . '</td><td data-label="' . esc_attr__( 'Klicks', 'tamil-site' ) . '">' . esc_html( number_format_i18n( $z['klicks'] ) ) . '</td></tr>';
		}
		$out .= '</tbody></table></div>';
	}
	return $out . '</section>';
}
