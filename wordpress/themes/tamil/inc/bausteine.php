<?php
/**
 * Bausteine der Gestaltung „Tageskalender“: Bild mit Nachweis, Datumsblock, Strom nach Monaten, Tafeln für Feste
 * und Kino, Bildnachweise der Seite für den Fuß.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Bildnachweise der aktuellen Seite sammeln (der Fuß zeigt sie gesammelt) oder abrufen.
 *
 * @param string $nachweis Nachweis zum Merken; leer = nur abrufen.
 * @return string[]
 */
function tamil_nachweise( string $nachweis = '' ): array {
	static $liste = array();
	$nachweis     = trim( $nachweis );
	if ( '' !== $nachweis && ! in_array( $nachweis, $liste, true ) ) {
		$liste[] = $nachweis;
	}
	return $liste;
}

/**
 * Hat der Beitrag ein Bild (Beitragsbild)?
 */
function tamil_hat_bild( int $post_id ): bool {
	return has_post_thumbnail( $post_id );
}

/**
 * Ist das Beitragsbild eine Titelkarte (Schlagzeile als Bild, Nachweis „Grafik: Tamil.de“)? Solche Karten zeigt das
 * Theme nicht; der Beitrag erscheint dann ohne Bild (Kritik theme-tageskalender-r2 P1-D).
 */
function tamil_ist_titelkarte( int $post_id ): bool {
	return str_starts_with( strtolower( tamil_bildnachweis( $post_id ) ), 'grafik: tamil.de' );
}

/**
 * Darf das Beitragsbild gezeigt werden (vorhanden und keine Titelkarte)?
 */
function tamil_bild_zeigbar( int $post_id ): bool {
	if ( ! tamil_hat_bild( $post_id ) || tamil_ist_titelkarte( $post_id ) ) {
		return false;
	}
	// Bänder breiter als 2,5:1 sind Logos oder Banner (etwa ein Ticketanbieter), kein Beitragsbild.
	$meta = wp_get_attachment_metadata( (int) get_post_thumbnail_id( $post_id ) );
	$w    = (int) ( $meta['width'] ?? 0 );
	$h    = (int) ( $meta['height'] ?? 0 );
	return ! ( $w && $h && $w / $h > 2.5 );
}

/**
 * Rubrikfoto als <figure> (Archiv- bzw. Symbolbild mit Nachweis), für Beiträge und Seitenköpfe ohne eigenes Foto.
 *
 * @param array<string,mixed> $opt { @type string $klasse, @type bool $eager, @type string $link Ziel (optional). }
 */
function tamil_rubrikfoto_figur( string $slug, array $opt = array() ): string {
	$f        = tamil_rubrikfoto( $slug );
	$nachweis = __( 'Archivbild der Rubrik.', 'tamil' ) . ' ' . $f['nachweis'];
	tamil_nachweise( $nachweis );
	$img = sprintf(
		'<img src="%1$s" width="%2$d" height="%3$d" alt="%4$s" %5$s>',
		esc_url( TAMIL_THEME_URI . '/assets/img/rubrik/' . $f['datei'] ),
		(int) $f['w'],
		(int) $f['h'],
		esc_attr( ! empty( $opt['alt'] ) ? $f['alt'] : '' ),
		! empty( $opt['eager'] ) ? 'loading="eager" fetchpriority="high"' : 'loading="lazy"'
	);
	if ( ! empty( $opt['link'] ) ) {
		$img = '<a class="bild-link" href="' . esc_url( (string) $opt['link'] ) . '" tabindex="-1" aria-hidden="true">' . $img . '</a>';
	}
	return sprintf(
		'<figure class="%1$s rubrikfoto">%2$s<figcaption>%3$s <a class="quelle" href="%4$s">%5$s</a></figcaption></figure>',
		esc_attr( (string) ( $opt['klasse'] ?? 'bild' ) ),
		$img,
		esc_html( $nachweis ),
		esc_url( $f['quelle'] ),
		esc_html__( 'Quelle', 'tamil' )
	);
}

/**
 * Rubrik-Slug eines Beitrags für das Rubrikfoto.
 */
function tamil_rubrik_slug( int $post_id ): string {
	$kat = tamil_hauptkategorie( $post_id );
	return $kat ? $kat->slug : 'allgemein';
}

/**
 * Titel für eine Tafelzelle: höchstens etwa zwei Zeilen (60 Zeichen), an einer Wortgrenze gekürzt. Der volle Titel
 * steht auf der Seite des Beitrags. Serverseitig statt line-clamp, damit kein verdeckter Text im Bild liegt.
 */
function tamil_titel_kurz( string $titel, int $zeichen = 60 ): string {
	$titel = trim( wp_strip_all_tags( $titel ) );
	if ( mb_strlen( $titel ) <= $zeichen ) {
		return $titel;
	}
	$kurz = mb_substr( $titel, 0, $zeichen );
	$pos  = mb_strrpos( $kurz, ' ' );
	return rtrim( false !== $pos ? mb_substr( $kurz, 0, $pos ) : $kurz, ' ,;:(' ) . ' …';
}

/**
 * Höchstens $anzahl Sätze eines Texts (für den Vorspann des Aufmachers).
 */
function tamil_saetze( string $text, int $anzahl = 2 ): string {
	$teile = preg_split( '/(?<=[.!?])\s+(?=[A-ZÄÖÜ„"0-9])/u', trim( $text ) );
	return is_array( $teile ) ? implode( ' ', array_slice( $teile, 0, $anzahl ) ) : $text;
}

/**
 * Ist das Beitragsbild ein Foto? Nur Bilder mit Nachweis „Foto: …“, ohne die Kennung einer Bildkarte oder eines
 * KI-Bilds und mit einem eigenen Alternativtext (steht dort nur der Titel, ist es meist ein Plakat oder Flyer).
 * Nur Fotos taugen als Leitbild im Seitenkopf; Grafiken werden nie beschnitten.
 */
function tamil_ist_foto( int $post_id ): bool {
	if ( ! tamil_bild_zeigbar( $post_id ) || ! str_starts_with( strtolower( tamil_bildnachweis( $post_id ) ), 'foto:' ) ) {
		return false;
	}
	if ( in_array( (string) get_post_meta( $post_id, 'bild_origin', true ), array( 'karte', 'ki' ), true ) ) {
		return false;
	}
	$alt = trim( (string) get_post_meta( (int) get_post_thumbnail_id( $post_id ), '_wp_attachment_image_alt', true ) );
	return '' !== $alt && wp_strip_all_tags( get_the_title( $post_id ) ) !== $alt;
}

/**
 * Leitbild für einen Seitenkopf: der erste Beitrag mit Foto; ohne Foto kein Bild (keine Plakate, Flyer, Logos).
 *
 * @param int[] $ids Kandidaten in der gewünschten Reihenfolge.
 */
function tamil_leitbild( array $ids ): int {
	foreach ( $ids as $id ) {
		if ( tamil_ist_foto( (int) $id ) ) {
			return (int) $id;
		}
	}
	return 0;
}

/**
 * „Wer“ in der Festtafel: nur der Name des Veranstalters, ohne Telefonnummer und Zusätze; leer, wenn er schon im
 * Titel oder im Ort steht.
 */
function tamil_wer_kurz( string $wer, string $titel, string $ort ): string {
	$wer = (string) preg_replace( '/\b(?:Tel\.?|Telefon|Tel)\s*:?\s*[\d+()\/\s-]{5,}/iu', '', $wer );
	$wer = trim( (string) preg_split( '/\s*[·,;|]\s*/u', $wer )[0] );
	if ( '' === $wer || false !== mb_stripos( $titel, $wer ) || false !== mb_stripos( $ort, $wer ) ) {
		return '';
	}
	return $wer;
}

/**
 * „Wo“ in der Festtafel: nur die Stadt (letzter Teil der Ortsangabe ohne Postleitzahl); „Ort folgt“, wenn der Ort
 * noch nicht feststeht.
 */
function tamil_ort_kurz( string $ort ): string {
	$ort = trim( $ort );
	if ( '' === $ort || preg_match( '/bekannt gegeben|wird noch|folgt|tba|tbd/iu', $ort ) ) {
		return __( 'Ort folgt', 'tamil' );
	}
	$teile = array_values( array_filter( array_map( 'trim', explode( ',', $ort ) ) ) );
	$stadt = (string) preg_replace( '/^(?:[A-Z]{1,2}-)?\d{4,5}\s+/u', '', (string) end( $teile ) );
	return '' !== $stadt ? $stadt : $ort;
}

/**
 * Beitragsbild als <figure> mit Nachweis darunter; leer, wenn der Beitrag kein Bild hat.
 *
 * @param array<string,mixed> $opt {
 *     @type string $klasse  Klassen der figure (Standard „bild“).
 *     @type string $size    Bildgröße.
 *     @type bool   $link    Bild verlinkt auf den Beitrag (für Mausnutzer; aus der Tab-Reihenfolge genommen).
 *     @type bool   $eager   Sofort laden (erster Bildschirm).
 *     @type bool   $alt     Alternativtext des Anhangs setzen (sonst leer, weil der Titel daneben steht).
 * }
 */
function tamil_figur( int $post_id, array $opt = array() ): string {
	if ( ! tamil_bild_zeigbar( $post_id ) ) {
		if ( array_key_exists( 'ersatz', $opt ) && ! $opt['ersatz'] ) {
			return '';
		}
		return tamil_rubrikfoto_figur(
			tamil_rubrik_slug( $post_id ),
			array(
				'klasse' => $opt['klasse'] ?? 'bild',
				'eager'  => ! empty( $opt['eager'] ),
				'alt'    => ! empty( $opt['alt'] ),
				'link'   => ( $opt['link'] ?? true ) ? (string) get_permalink( $post_id ) : '',
			)
		);
	}
	$opt  = array_merge(
		array(
			'klasse' => 'bild',
			'size'   => 'tamil-card',
			'link'   => true,
			'eager'  => false,
			'alt'    => false,
		),
		$opt
	);
	$attr = $opt['eager'] ? array(
		'loading'       => 'eager',
		'fetchpriority' => 'high',
	) : array( 'loading' => 'lazy' );
	$alt  = $opt['alt'] ? trim( (string) get_post_meta( (int) get_post_thumbnail_id( $post_id ), '_wp_attachment_image_alt', true ) ) : '';
	$img  = (string) get_the_post_thumbnail( $post_id, $opt['size'], array_merge( $attr, array( 'alt' => $alt ) ) );
	if ( $opt['link'] ) {
		$img = sprintf( '<a class="bild-link" href="%1$s" tabindex="-1" aria-hidden="true">%2$s</a>', esc_url( get_permalink( $post_id ) ), $img );
	}
	$nachweis = str_replace( ' · ', ', ', tamil_bildnachweis( $post_id ) ); // Quellen aus dem Altbestand ohne Trennpunkte
	tamil_nachweise( $nachweis );
	return sprintf(
		'<figure class="%1$s">%2$s%3$s</figure>',
		esc_attr( $opt['klasse'] . ( str_starts_with( strtolower( $nachweis ), 'grafik' ) ? ' grafik' : '' ) ),
		$img,
		'' !== $nachweis ? '<figcaption>' . esc_html( $nachweis ) . '</figcaption>' : ''
	);
}

/**
 * WhatsApp-Link zum Weiterschicken (wa.me ohne Nummer: Leser wählen selbst, an wen).
 */
function tamil_wa_teilen( string $text, string $url = '' ): string {
	return 'https://wa.me/?text=' . rawurlencode( trim( $text . ( '' !== $url ? ' ' . $url : '' ) ) );
}

/**
 * „Rubrik, Ort“ unter einem Titel (ohne Trennpunkte).
 */
function tamil_rubrik_ort( int $post_id, bool $rubrik = true ): string {
	$teile = array();
	$kat   = $rubrik ? tamil_hauptkategorie( $post_id ) : null;
	if ( $kat ) {
		$teile[] = $kat->name;
	}
	$ort = trim( (string) get_post_meta( $post_id, 'ort', true ) );
	if ( '' !== $ort ) {
		$teile[] = $ort;
	}
	return implode( ', ', $teile );
}

/**
 * Datumsblock: große Tagesziffer, daneben Monat und Jahr, Wochentag und optional weitere Zeilen.
 *
 * @param int      $ts     Zeitpunkt.
 * @param string[] $zeilen Weitere Zeilen unter dem Wochentag (z. B. Rubrik und Ort); schon escapt.
 * @param string   $marke  Ersetzt den Wochentag (z. B. „Sonntag, Deepavali“).
 */
function tamil_tag_block( int $ts, array $zeilen = array(), string $marke = '' ): void {
	echo '<p class="tag"><time class="ziffer" datetime="' . esc_attr( wp_date( 'Y-m-d', $ts ) ) . '">' . esc_html( wp_date( 'j', $ts ) ) . '</time>';
	echo '<span class="tag-rest"><span class="monat">' . esc_html( wp_date( 'F Y', $ts ) ) . '</span>';
	echo '' !== $marke ? '<span class="marke">' . esc_html( $marke ) . '</span>' : '<span class="wochentag">' . esc_html( wp_date( 'l', $ts ) ) . '</span>';
	foreach ( $zeilen as $zeile ) {
		echo '<span class="tag-ort">' . $zeile . '</span>'; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Aufrufer escapt
	}
	echo '</span></p>';
}

/**
 * Tagesziffer einer Zeile: „15“ und darunter „So., Nov.“; $art „z“ für den Strom, „t“ für Tafeln.
 */
function tamil_zeilen_tag( int $ts, string $art = 'z' ): string {
	if ( 'z' === $art ) {
		return sprintf(
			'<span class="z"><time datetime="%1$s">%2$s</time><small>%3$s</small></span>',
			esc_attr( wp_date( 'Y-m-d', $ts ) ),
			esc_html( wp_date( 'j', $ts ) ),
			esc_html( wp_date( 'D, M', $ts ) )
		);
	}
	return sprintf(
		'<time datetime="%1$s"><span class="t-z">%2$s</span><span class="t-wt">%3$s</span></time>',
		esc_attr( wp_date( 'Y-m-d', $ts ) ),
		esc_html( wp_date( 'j', $ts ) ),
		esc_html( wp_date( 'D, M', $ts ) )
	);
}

/**
 * Strom: Beiträge nach Monaten, je Zeile Tagesziffer, Titel, „Rubrik, Ort“, Vorspann und Bild mit Nachweis.
 *
 * @param int[]               $ids Beiträge (neueste zuerst).
 * @param array<string,mixed> $opt {
 *     @type string $monat   Ebene der Monatsköpfe (h2|h3); leer = keine Monatsköpfe.
 *     @type string $titel   Ebene der Titel (h3|h4).
 *     @type string $teaser  'breit' (nur ab 761 px), 'immer' oder ''.
 *     @type bool   $rubrik  Rubrik unter dem Titel nennen.
 *     @type string $weiter  Monat (Y-m), mit dem ein vorheriger Strom endete: kein zweiter Monatskopf dafür.
 * }
 */
function tamil_strom( array $ids, array $opt = array() ): void {
	$opt    = array_merge(
		array(
			'monat'  => 'h3',
			'titel'  => 'h4',
			'teaser' => 'breit',
			'rubrik' => true,
			'weiter' => '',
		),
		$opt
	);
	$titel  = in_array( $opt['titel'], array( 'h2', 'h3', 'h4' ), true ) ? $opt['titel'] : 'h3';
	$monat  = in_array( $opt['monat'], array( 'h2', 'h3' ), true ) ? $opt['monat'] : '';
	$jahr   = wp_date( 'Y' );
	$offen  = '';
	$weiter = (string) $opt['weiter'];
	$vortag = '';
	foreach ( $ids as $id ) {
		$ts = isset( $opt['zeiten'][ $id ] ) ? (int) $opt['zeiten'][ $id ] : (int) get_post_timestamp( $id );
		$m  = wp_date( 'Y-m', $ts );
		if ( ( '' !== $monat && $m !== $offen ) || '' === $offen ) {
			if ( '' !== $offen ) {
				echo '</ul>';
			}
			if ( '' !== $monat && $m !== $weiter ) {
				$name = wp_date( 'Y', $ts ) === $jahr ? wp_date( 'F', $ts ) : wp_date( 'F Y', $ts );
				printf( '<%1$s class="monat-kopf">%2$s</%1$s>', $monat, esc_html( $name ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- $monat ist geprüft
			}
			echo '<ul class="tage strom' . ( '' !== $opt['teaser'] ? ' mit-teaser' : '' ) . '">';
			$offen  = '' !== $monat ? $m : 'alle';
			$weiter = '';
			$vortag = '';
		}
		$link    = get_permalink( $id );
		$figur   = tamil_figur(
			$id,
			array(
				'klasse' => 'daumen',
				'size'   => 'tamil-card',
			)
		);
		$klassen = array_filter( array( '' === $figur ? 'ohne-bild' : '', wp_date( 'Y-m-d', $ts ) === $vortag ? 'gleicher-tag' : '' ) );
		$vortag  = wp_date( 'Y-m-d', $ts );
		echo '<li' . ( $klassen ? ' class="' . esc_attr( implode( ' ', $klassen ) ) . '"' : '' ) . '>';
		echo tamil_zeilen_tag( $ts ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_zeilen_tag()
		echo '<div class="s-text">';
		printf( '<%1$s class="b-titel"><a href="%2$s">%3$s</a></%1$s>', $titel, esc_url( $link ), esc_html( get_the_title( $id ) ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- $titel ist geprüft
		$wo = tamil_rubrik_ort( $id, (bool) $opt['rubrik'] );
		if ( '' !== $wo ) {
			echo '<p class="wo">' . esc_html( $wo ) . '</p>';
		}
		if ( '' !== $opt['teaser'] ) {
			echo '<p class="teaser' . ( 'breit' === $opt['teaser'] ? ' nur-breit' : '' ) . '">' . tamil_text( wp_trim_words( tamil_standfirst( $id ), 18, ' …' ) ) . '</p>'; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_text()
		}
		echo '</div>';
		echo $figur; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_figur()
		echo '</li>';
	}
	if ( '' !== $offen ) {
		echo '</ul>';
	}
}

/**
 * Feste-Tafel: Tag, Was, Wer, Wo (und optional Weitersagen). Der erste kommende Termin ist „als Nächstes“.
 *
 * @param int[]               $ids Beiträge mit Termin (früheste zuerst).
 * @param array<string,mixed> $opt { @type bool $teilen Spalte „Weitersagen“, @type bool $verlinken Titel verlinken (Standard ja), @type string $klasse Zusatzklasse. }
 */
function tamil_feste_tafel( array $ids, array $opt = array() ): void {
	if ( ! function_exists( 'tamil_site_event' ) ) {
		return;
	}
	$teilen  = ! empty( $opt['teilen'] );
	$heute   = current_time( 'Y-m-d' );
	$naechst = false;
	echo '<table class="tafel feste' . ( ! empty( $opt['klasse'] ) ? ' ' . esc_attr( (string) $opt['klasse'] ) : '' ) . '"><thead><tr>';
	echo '<th scope="col">' . esc_html__( 'Tag', 'tamil' ) . '</th><th scope="col">' . esc_html__( 'Was', 'tamil' ) . '</th><th scope="col">' . esc_html__( 'Wer', 'tamil' ) . '</th><th scope="col">' . esc_html__( 'Wo', 'tamil' ) . '</th>';
	if ( $teilen ) {
		echo '<th scope="col">' . esc_html__( 'Weitersagen', 'tamil' ) . '</th>';
	}
	echo '</tr></thead><tbody>';
	foreach ( $ids as $id ) {
		$e = tamil_site_event( (int) $id );
		if ( ! $e ) {
			continue;
		}
		$start   = date_create_immutable( $e['datum'], wp_timezone() );
		$ts      = $start ? $start->getTimestamp() : 0;
		$tag     = $start ? $start->format( 'Y-m-d' ) : '';
		$vorbei  = '' !== $tag && $tag < $heute;
		$ist     = ! $vorbei && ! $naechst;
		$naechst = $naechst || $ist;
		$titel   = get_the_title( (int) $id );
		$klasse  = $vorbei ? 'vorbei' : ( $ist ? 'ist-naechst' : '' );
		echo '<tr' . ( '' !== $klasse ? ' class="' . esc_attr( $klasse ) . '"' : '' ) . '>';
		echo '<td class="t-tag">' . ( $ts ? tamil_zeilen_tag( $ts, 't' ) : '' ) . '</td>'; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_zeilen_tag()
		$verlinkt = ! isset( $opt['verlinken'] ) || $opt['verlinken'];
		echo '<td class="was">' . ( $verlinkt ? '<a href="' . esc_url( get_permalink( (int) $id ) ) . '" title="' . esc_attr( $titel ) . '">' . esc_html( tamil_titel_kurz( $titel ) ) . '</a>' : esc_html( tamil_titel_kurz( $titel ) ) );
		if ( $ist ) {
			echo '<span class="als">' . esc_html__( 'als Nächstes', 'tamil' ) . '</span>';
		}
		echo '</td>';
		$wo  = tamil_ort_kurz( $e['ort'] );
		$wo  = __( 'Ort folgt', 'tamil' ) !== $wo && false !== mb_stripos( $titel, $wo ) ? '' : $wo;
		$wer = tamil_wer_kurz( $e['veranstalter'], $titel, $e['ort'] );
		echo '<td class="wer">' . esc_html( $wer ) . '</td>';
		echo '<td class="wo">' . esc_html( $wo ) . '</td>';
		if ( $teilen ) {
			/* translators: %s: Titel des Termins */
			$label = sprintf( __( '%s per WhatsApp schicken', 'tamil' ), $titel );
			echo '<td class="t-teilen"><a class="teilen" href="' . esc_url( tamil_wa_teilen( $titel . ', ' . tamil_termin_text( $e['datum'], $e['ende'] ), (string) get_permalink( (int) $id ) ) ) . '" aria-label="' . esc_attr( $label ) . '">' . esc_html__( 'Per WhatsApp', 'tamil' ) . '</a></td>';
		}
		echo '</tr>';
	}
	echo '</tbody></table>';
}

/**
 * Spielzeit einer Kinoliste: bis wann sie gilt (letzter Spieltag, Ende der Kinowoche) und der Stand als Text aus den
 * Kinodaten selbst (Kinowoche oder erster Spieltag), nicht aus dem Änderungsdatum des Beitrags.
 *
 * @param array<string,mixed> $fakten Ergebnis von tamil_site_kino_fakten().
 * @return array{bis:string,stand:string}
 */
function tamil_kino_spielzeit( array $fakten ): array {
	$tage  = array();
	$woche = (string) ( $fakten['woche'] ?? '' );
	if ( preg_match( '/^(\d{4})-W(\d{2})$/', $woche, $m ) ) {
		$tage[] = ( new DateTimeImmutable( 'now', wp_timezone() ) )->setISODate( (int) $m[1], (int) $m[2], 4 )->modify( '+6 days' )->format( 'Y-m-d' );
	}
	$erster = '';
	foreach ( (array) ( $fakten['kinos'] ?? array() ) as $k ) {
		foreach ( array_merge( (array) ( $k['termine'] ?? array() ), array( (string) ( $k['bis'] ?? '' ) ) ) as $d ) {
			if ( '' !== (string) $d ) {
				$tage[] = substr( (string) $d, 0, 10 );
			}
		}
		$von = substr( (string) ( $k['von'] ?? ( $k['termine'][0] ?? '' ) ), 0, 10 );
		if ( '' !== $von && ( '' === $erster || $von < $erster ) ) {
			$erster = $von;
		}
	}
	if ( ! $tage && '' !== $erster ) {
		$tage[] = gmdate( 'Y-m-d', (int) strtotime( $erster . ' +6 days' ) );
	}
	$bis = $tage ? max( $tage ) : '';
	if ( '' !== $woche ) {
		/* translators: %s: Kinowoche */
		$stand = sprintf( __( 'Stand: %s', 'tamil' ), tamil_kinowoche( $woche ) );
	} elseif ( '' !== $erster ) {
		/* translators: %s: Datum */
		$stand = sprintf( __( 'Spielzeit ab %s', 'tamil' ), wp_date( 'j. F', (int) strtotime( $erster ) ) );
	} else {
		$stand = '';
	}
	$beginn = '' !== $erster ? $erster : '';
	if ( preg_match( '/^(\\d{4})-W(\\d{2})$/', $woche, $m ) ) {
		$beginn = ( new DateTimeImmutable( 'now', wp_timezone() ) )->setISODate( (int) $m[1], (int) $m[2], 4 )->format( 'Y-m-d' );
	}
	return array(
		'bis'    => $bis,
		'beginn' => $beginn,
		'stand'  => $stand,
	);
}

/**
 * Kino in Kurzform: je Beitrag mit Kinoliste Film, Städte, Zahl der Kinos, Link, Stand und Spielzeit. Listen, deren
 * Spielzeit vorbei ist, fallen weg (wie vergangene Feste).
 *
 * @return array<int,array{film:string,staedte:string[],kinos:int,link:string,stand:string,bis:string,post:int,fakten:array}>
 */
function tamil_kino_filme( int $anzahl = 3 ): array {
	if ( ! function_exists( 'tamil_site_kino_posts' ) ) {
		return array();
	}
	$heute = current_time( 'Y-m-d' );
	$filme = array();
	foreach ( array_map( 'intval', tamil_site_kino_posts( $anzahl, array( 'fields' => 'ids' ) )->posts ) as $id ) {
		$f = tamil_kino_film( $id );
		if ( $f && '' !== $f['bis'] && $f['bis'] >= $heute ) {
			$filme[] = $f;
		}
	}
	return $filme;
}

/**
 * Ein Film aus einem Beitrag mit Kinoliste (auch, wenn die Spielzeit vorbei ist); leer ohne Kinoliste.
 *
 * @return array<string,mixed>
 */
function tamil_kino_film( int $id ): array {
	$fakten = function_exists( 'tamil_site_kino_fakten' ) ? tamil_site_kino_fakten( $id ) : array();
	$kinos  = is_array( $fakten['kinos'] ?? null ) ? $fakten['kinos'] : array();
	if ( ! $kinos ) {
		return array();
	}
	$film = trim( (string) ( $fakten['film'] ?? '' ) );
	$zeit = tamil_kino_spielzeit( $fakten );
	return array(
		'film'    => '' !== $film ? $film : get_the_title( $id ),
		'staedte' => array_values( array_unique( array_filter( array_map( static fn( $k ) => trim( (string) ( $k['stadt'] ?? '' ) ), $kinos ) ) ) ),
		'kinos'   => count( $kinos ),
		'link'    => (string) get_permalink( $id ),
		'stand'   => $zeit['stand'],
		'bis'     => $zeit['bis'],
		'beginn'  => $zeit['beginn'],
		'post'    => $id,
		'fakten'  => $fakten,
	);
}

/**
 * Tafel „Nach Stadt“: Land, Stadt, Film, Kino, Termin und Link zu Tickets und Zeiten aus den Kinolisten.
 *
 * @param array<int,array> $filme Ergebnis von tamil_kino_filme() bzw. tamil_kino_film().
 */
function tamil_kino_orte_tafel( array $filme ): void {
	$laender = array(
		'DE' => __( 'Deutschland', 'tamil' ),
		'AT' => __( 'Österreich', 'tamil' ),
		'CH' => __( 'Schweiz', 'tamil' ),
	);
	$fmt     = static fn( string $d ): string => wp_date( 'j.n.', (int) strtotime( $d ) );
	$orte    = array();
	foreach ( $filme as $f ) {
		foreach ( (array) ( $f['fakten']['kinos'] ?? array() ) as $k ) {
			$stadt = trim( (string) ( $k['stadt'] ?? '' ) );
			if ( '' === $stadt ) {
				continue;
			}
			if ( ! empty( $k['termine'] ) ) {
				/* translators: 1: Anzahl, 2: Datum */
				$termin = sprintf( _n( '%1$d Vorstellung ab %2$s', '%1$d Vorstellungen ab %2$s', count( $k['termine'] ), 'tamil' ), count( $k['termine'] ), $fmt( (string) $k['termine'][0] ) );
			} elseif ( ! empty( $k['von'] ) && ! empty( $k['bis'] ) && (string) $k['bis'] >= (string) $k['von'] ) {
				/* translators: 1: Beginn, 2: Ende */
				$termin = sprintf( __( '%1$s bis %2$s', 'tamil' ), $fmt( (string) $k['von'] ), $fmt( (string) $k['bis'] ) );
			} else {
				/* translators: %s: Datum */
				$termin = ! empty( $k['von'] ) ? sprintf( __( 'ab %s', 'tamil' ), $fmt( (string) $k['von'] ) ) : '';
			}
			$orte[ (string) ( $k['land'] ?? '' ) ][ $stadt ][] = array(
				'film'   => $f['film'],
				'kino'   => trim( (string) ( $k['kino'] ?? '' ) ),
				'termin' => $termin,
				'url'    => (string) ( $k['url'] ?? '' ),
			);
		}
	}
	if ( ! $orte ) {
		return;
	}
	$reihe = array_keys( $laender );
	$rang  = static function ( $land ) use ( $reihe ): int {
		$i = array_search( (string) $land, $reihe, true );
		return false === $i ? 9 : (int) $i;
	};
	uksort( $orte, static fn( $a, $b ) => $rang( $a ) <=> $rang( $b ) );
	echo '<table class="tafel orte"><thead><tr><th scope="col">' . esc_html__( 'Stadt', 'tamil' ) . '</th><th scope="col">' . esc_html__( 'Film, Kino und Termin', 'tamil' ) . '</th></tr></thead>';
	foreach ( $orte as $land => $staedte ) {
		ksort( $staedte, SORT_LOCALE_STRING );
		echo '<tbody><tr class="land"><th scope="rowgroup" colspan="2">' . esc_html( $laender[ $land ] ?? $land ) . '</th></tr>';
		foreach ( $staedte as $stadt => $eintraege ) {
			foreach ( $eintraege as $e ) {
				echo '<tr><th scope="row" class="stadt">' . esc_html( $stadt ) . '</th><td class="was">' . esc_html( '„' . $e['film'] . '“' );
				echo '<span class="unter">' . esc_html( trim( $e['kino'] . ( '' !== $e['termin'] ? ', ' . $e['termin'] : '' ), ', ' ) );
				if ( '' !== $e['url'] ) {
					echo '<a class="ticket" href="' . esc_url( $e['url'] ) . '" target="_blank" rel="noopener nofollow">' . esc_html__( 'Tickets und Zeiten', 'tamil' ) . '</a>';
				}
				echo '</span></td></tr>';
			}
		}
		echo '</tbody>';
	}
	echo '</table>';
}

/**
 * Städte kurz: „Berlin, Bremen, Dortmund und 6 weitere Städte“.
 *
 * @param string[] $staedte Städte.
 */
function tamil_staedte_kurz( array $staedte, int $zeigen = 5 ): string {
	if ( count( $staedte ) <= $zeigen + 1 ) {
		return implode( ', ', $staedte );
	}
	$rest = count( $staedte ) - $zeigen;
	/* translators: 1: Städte, 2: Anzahl weiterer Städte */
	return sprintf( _n( '%1$s und %2$d weitere Stadt', '%1$s und %2$d weitere Städte', $rest, 'tamil' ), implode( ', ', array_slice( $staedte, 0, $zeigen ) ), $rest );
}

/**
 * Kino-Tafel (Film und Städte | Kinos | optional Weitersagen).
 *
 * @param array<int,array> $filme Ergebnis von tamil_kino_filme().
 */
function tamil_kino_tafel( array $filme, bool $teilen = false ): void {
	echo '<table class="tafel kino kompakt"><thead><tr><th scope="col">' . esc_html__( 'Film und Städte', 'tamil' ) . '</th><th scope="col" class="zahl">' . esc_html__( 'Kinos', 'tamil' ) . '</th>';
	if ( $teilen ) {
		echo '<th scope="col">' . esc_html__( 'Weitersagen', 'tamil' ) . '</th>';
	}
	echo '</tr></thead><tbody>';
	foreach ( $filme as $f ) {
		$staedte = tamil_staedte_kurz( $f['staedte'] );
		echo '<tr><td class="was"><a href="' . esc_url( $f['link'] ) . '">' . esc_html( '„' . $f['film'] . '“' ) . '</a><span class="unter">' . esc_html( $staedte ) . '</span></td>';
		echo '<td class="zahl">' . esc_html( (string) $f['kinos'] ) . '<span class="m"> ' . esc_html( _n( 'Kino', 'Kinos', $f['kinos'], 'tamil' ) ) . '</span></td>';
		if ( $teilen ) {
			/* translators: %s: Film */
			$label = sprintf( __( '„%s“ per WhatsApp schicken', 'tamil' ), $f['film'] );
			echo '<td class="t-teilen"><a class="teilen" href="' . esc_url( tamil_wa_teilen( '„' . $f['film'] . '“ im Kino: ' . $staedte, $f['link'] ) ) . '" aria-label="' . esc_attr( $label ) . '">' . esc_html__( 'Per WhatsApp', 'tamil' ) . '</a></td>';
		}
		echo '</tr>';
	}
	echo '</tbody></table>';
}

/**
 * „Stand: 9. November“ aus einem Zeitstempel.
 */
function tamil_stand( int $ts ): string {
	/* translators: %s: Datum */
	return sprintf( __( 'Stand: %s', 'tamil' ), wp_date( 'j. F', $ts ) );
}

/**
 * Tamilische Wörter in HTML mit lang="ta" auszeichnen (nur im Text, nie in Tags oder Attributen), damit Vorleser
 * und Schrift (Catamaran-Untermenge) sie richtig behandeln.
 */
function tamil_lang_ta( string $html ): string {
	if ( ! preg_match( '/[\x{0B80}-\x{0BFF}]/u', $html ) ) {
		return $html;
	}
	$teile = preg_split( '/(<[^>]*>)/u', $html, -1, PREG_SPLIT_DELIM_CAPTURE );
	if ( ! is_array( $teile ) ) {
		return $html;
	}
	$ueberspringen = false; // in <script>, <style> und <textarea> nichts ändern
	foreach ( $teile as $i => $teil ) {
		if ( '' === $teil ) {
			continue;
		}
		if ( '<' === $teil[0] ) {
			if ( preg_match( '/^<(script|style|textarea)\b/i', $teil ) ) {
				$ueberspringen = true;
			} elseif ( preg_match( '/^<\/(script|style|textarea)>/i', $teil ) ) {
				$ueberspringen = false;
			}
			continue;
		}
		if ( ! $ueberspringen ) {
			$teile[ $i ] = (string) preg_replace( '/[\x{0B80}-\x{0BFF}](?:[\x{0B80}-\x{0BFF}\x{200C}\x{200D} ]*[\x{0B80}-\x{0BFF}])?/u', '<span lang="ta">$0</span>', $teil );
		}
	}
	return implode( '', $teile );
}

/**
 * Text escapen und tamilische Wörter auszeichnen (für Vorspann und Anrisse).
 */
function tamil_text( string $text ): string {
	return tamil_lang_ta( esc_html( $text ) );
}

/**
 * Nächster kommender Termin mit Kinovorstellung (Rubrik Kino, Schlagwort Kino oder „Kino“ in Titel oder Ort), damit
 * die leere Kino-Tafel nicht der Feste-Tafel widerspricht.
 *
 * @return array{titel:string,link:string,ts:int}|array{}
 */
function tamil_naechste_kino_vorstellung(): array {
	if ( ! function_exists( 'tamil_site_upcoming_events' ) ) {
		return array();
	}
	foreach ( array_map( 'intval', tamil_site_upcoming_events( 10, array( 'fields' => 'ids' ) )->posts ) as $id ) {
		$e     = tamil_site_event( $id );
		$titel = get_the_title( $id );
		$kino  = 'kino' === tamil_rubrik_slug( $id ) || in_array( 'kino', wp_list_pluck( tamil_tags( $id ), 'slug' ), true )
			|| false !== mb_stripos( $titel . ' ' . ( $e['ort'] ?? '' ), 'kino' );
		if ( $kino && $e ) {
			return array(
				'titel' => $titel,
				'link'  => (string) get_permalink( $id ),
				'ts'    => (int) strtotime( $e['datum'] ),
			);
		}
	}
	return array();
}

/**
 * Leerzustand der Kino-Tafel: Verweis auf die nächste Kinovorstellung unter Termine, sonst der ruhige Satz.
 */
function tamil_kino_leer(): string {
	$v = tamil_naechste_kino_vorstellung();
	if ( $v ) {
		/* translators: 1: Datum, 2: Link zum Termin, 3: Link zu Termine */
		return '<p class="bogen-leer">' . sprintf( esc_html__( 'Nächste Vorstellung am %1$s: %2$s, unter %3$s.', 'tamil' ), esc_html( wp_date( 'j. F', $v['ts'] ) ), '<a href="' . esc_url( $v['link'] ) . '">' . esc_html( $v['titel'] ) . '</a>', '<a href="' . esc_url( tamil_rubrik( 'events' )['url'] ) . '">' . esc_html__( 'Termine', 'tamil' ) . '</a>' ) . '</p>';
	}
	return '<p class="bogen-leer">' . esc_html__( 'Für diese Woche kennen wir keine tamilische Vorstellung. Kennt ihr eine? Schickt sie der Redaktion.', 'tamil' ) . '</p>';
}
