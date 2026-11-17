<?php
/**
 * Bausteine hinter den Anreißern: Bildnachweise der Seite für den Fuß, welche Bilder gezeigt werden, Kürzungen für
 * Titel und Orte, Kinolisten (Spielzeit, Filme, Tabelle „Nach Stadt“), tamilische Wörter mit lang="ta".
 */

defined( 'ABSPATH' ) || exit;

/**
 * Bildnachweise der aktuellen Seite sammeln (der Fuß zeigt sie gesammelt) oder abrufen.
 *
 * @param string $nachweis Nachweis zum Merken als escaptes HTML (Links auf Dateiseite und Lizenz); leer = nur abrufen.
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
 * Rubrik-Slug eines Beitrags für den Rubrik-Pool.
 */
function tamil_rubrik_slug( int $post_id ): string {
	$kat = tamil_hauptkategorie( $post_id );
	return $kat ? $kat->slug : 'allgemein';
}

/**
 * Titel gekürzt (Kopfzeile, Tabellen): höchstens etwa zwei Zeilen (60 Zeichen), an einer Wortgrenze. Der volle Titel
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
 * KI-Bilds, nicht breiter als 2,5:1 und mit einem eigenen Alternativtext (steht dort nur der Titel, ist es meist ein
 * Plakat oder Flyer). Nur Fotos taugen als Leitbild (Rubrikkacheln, Aufmacher).
 */
function tamil_ist_foto( int $post_id ): bool {
	$w = tamil_bildwahl( $post_id );
	if ( 'eigen' !== $w['art'] || $w['breit'] || ! str_starts_with( strtolower( tamil_bildnachweis( $post_id ) ), 'foto:' ) ) {
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
 * WhatsApp-Link zum Weiterschicken (wa.me ohne Nummer: Leser wählen selbst, an wen).
 */
function tamil_wa_teilen( string $text, string $url = '' ): string {
	return 'https://wa.me/?text=' . rawurlencode( trim( $text . ( '' !== $url ? ' ' . $url : '' ) ) );
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
 * Tafel „Nach Stadt“: Land, Stadt, Film, Kino, Termin und Link zu Tickets und Zeiten aus den Kinolisten. Auf der
 * Kinoseite trägt jede Zeile das Bild des Films (im Artikel steht es schon darüber).
 *
 * @param array<int,array> $filme  Ergebnis von tamil_kino_filme() bzw. tamil_kino_film().
 * @param bool             $bilder Bild des Films in jeder Zeile.
 */
function tamil_kino_orte_tafel( array $filme, bool $bilder = false ): void {
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
				'post'   => (int) $f['post'],
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
	$ein_film = 1 === count( $filme ); // bei einem Film steht er schon im Titel; der Name je Zeile entfällt
	echo '<div class="tafel-wrap"><table class="tafel orte' . ( $bilder ? ' tafel--bilder' : '' ) . '"><thead><tr><th scope="col">' . esc_html__( 'Stadt', 'tamil' ) . '</th><th scope="col">' . esc_html( $ein_film ? __( 'Kino und Termin', 'tamil' ) : __( 'Film, Kino und Termin', 'tamil' ) ) . '</th></tr></thead>';
	foreach ( $orte as $land => $staedte ) {
		ksort( $staedte, SORT_LOCALE_STRING );
		echo '<tbody><tr class="land"><th scope="rowgroup" colspan="2">' . esc_html( $laender[ $land ] ?? $land ) . '</th></tr>';
		foreach ( $staedte as $stadt => $eintraege ) {
			foreach ( $eintraege as $e ) {
				echo '<tr><th scope="row" class="stadt">' . esc_html( $stadt ) . '</th><td class="was">';
				if ( $bilder ) {
					echo '<span class="tafel__bild rahmen r169">' . tamil_bild( $e['post'], array( 'sizes' => '96px' ) ) . '</span><span class="tafel__text">'; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_bild()
				}
				echo $ein_film ? '' : '<span class="film">' . esc_html( '„' . $e['film'] . '“' ) . '</span>';
				echo '<span class="unter">' . esc_html( trim( $e['kino'] . ( '' !== $e['termin'] ? ', ' . $e['termin'] : '' ), ', ' ) );
				if ( '' !== $e['url'] ) {
					echo '<a class="ticket" href="' . esc_url( $e['url'] ) . '" target="_blank" rel="noopener nofollow">' . esc_html__( 'Tickets und Zeiten', 'tamil' ) . '</a>';
				}
				echo '</span>' . ( $bilder ? '</span>' : '' ) . '</td></tr>';
			}
		}
		echo '</tbody>';
	}
	echo '</table></div>';
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
