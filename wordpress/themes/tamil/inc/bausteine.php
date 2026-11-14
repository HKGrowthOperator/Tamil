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
	if ( ! tamil_hat_bild( $post_id ) ) {
		return '';
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
	$nachweis = tamil_bildnachweis( $post_id );
	tamil_nachweise( $nachweis );
	return sprintf(
		'<figure class="%1$s">%2$s%3$s</figure>',
		esc_attr( $opt['klasse'] ),
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
 * }
 */
function tamil_strom( array $ids, array $opt = array() ): void {
	$opt   = array_merge(
		array(
			'monat'  => 'h3',
			'titel'  => 'h4',
			'teaser' => 'breit',
			'rubrik' => true,
		),
		$opt
	);
	$titel = in_array( $opt['titel'], array( 'h2', 'h3', 'h4' ), true ) ? $opt['titel'] : 'h3';
	$monat = in_array( $opt['monat'], array( 'h2', 'h3' ), true ) ? $opt['monat'] : '';
	$jahr  = wp_date( 'Y' );
	$offen = '';
	foreach ( $ids as $id ) {
		$ts = (int) get_post_timestamp( $id );
		$m  = wp_date( 'Y-m', $ts );
		if ( ( '' !== $monat && $m !== $offen ) || '' === $offen ) {
			if ( '' !== $offen ) {
				echo '</ul>';
			}
			if ( '' !== $monat ) {
				$name = wp_date( 'Y', $ts ) === $jahr ? wp_date( 'F', $ts ) : wp_date( 'F Y', $ts );
				printf( '<%1$s class="monat-kopf">%2$s</%1$s>', $monat, esc_html( $name ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- $monat ist geprüft
			}
			echo '<ul class="tage strom' . ( '' !== $opt['teaser'] ? ' mit-teaser' : '' ) . '">';
			$offen = '' !== $monat ? $m : 'alle';
		}
		$link  = get_permalink( $id );
		$figur = tamil_figur(
			$id,
			array(
				'klasse' => 'daumen',
				'size'   => 'tamil-card',
			)
		);
		echo '<li' . ( '' === $figur ? ' class="ohne-bild"' : '' ) . '>';
		echo tamil_zeilen_tag( $ts ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_zeilen_tag()
		echo '<div class="s-text">';
		printf( '<%1$s class="b-titel"><a href="%2$s">%3$s</a></%1$s>', $titel, esc_url( $link ), esc_html( get_the_title( $id ) ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- $titel ist geprüft
		$wo = tamil_rubrik_ort( $id, (bool) $opt['rubrik'] );
		if ( '' !== $wo ) {
			echo '<p class="wo">' . esc_html( $wo ) . '</p>';
		}
		if ( '' !== $opt['teaser'] ) {
			echo '<p class="teaser' . ( 'breit' === $opt['teaser'] ? ' nur-breit' : '' ) . '">' . tamil_text( wp_trim_words( tamil_standfirst( $id ), 32, ' …' ) ) . '</p>'; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_text()
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
		echo '<td class="was">' . ( $verlinkt ? '<a href="' . esc_url( get_permalink( (int) $id ) ) . '">' . esc_html( $titel ) . '</a>' : esc_html( $titel ) );
		if ( $ist ) {
			echo '<span class="als">' . esc_html__( 'als Nächstes', 'tamil' ) . '</span>';
		}
		echo '</td>';
		echo '<td class="wer">' . ( '' !== $e['veranstalter'] ? esc_html( $e['veranstalter'] ) : '<span class="leer">' . esc_html__( 'nicht angegeben', 'tamil' ) . '</span>' ) . '</td>';
		echo '<td class="wo">' . ( '' !== $e['ort'] ? esc_html( $e['ort'] ) : '<span class="leer">' . esc_html__( 'nicht angegeben', 'tamil' ) . '</span>' ) . '</td>';
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
 * Kino in Kurzform: je Beitrag mit Kinoliste Film, Städte, Zahl der Kinos, Link und Stand.
 *
 * @return array<int,array{film:string,staedte:string[],kinos:int,link:string,stand:int,post:int,fakten:array}>
 */
function tamil_kino_filme( int $anzahl = 3 ): array {
	if ( ! function_exists( 'tamil_site_kino_posts' ) ) {
		return array();
	}
	$filme = array();
	foreach ( array_map( 'intval', tamil_site_kino_posts( $anzahl, array( 'fields' => 'ids' ) )->posts ) as $id ) {
		$fakten = tamil_site_kino_fakten( $id );
		$kinos  = is_array( $fakten['kinos'] ?? null ) ? $fakten['kinos'] : array();
		if ( ! $kinos ) {
			continue;
		}
		$staedte = array_values( array_unique( array_filter( array_map( static fn( $k ) => trim( (string) ( $k['stadt'] ?? '' ) ), $kinos ) ) ) );
		$film    = trim( (string) ( $fakten['film'] ?? '' ) );
		$filme[] = array(
			'film'    => '' !== $film ? $film : get_the_title( $id ),
			'staedte' => $staedte,
			'kinos'   => count( $kinos ),
			'link'    => (string) get_permalink( $id ),
			'stand'   => (int) get_post_modified_time( 'U', true, $id ),
			'post'    => $id,
			'fakten'  => $fakten,
		);
	}
	return $filme;
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
