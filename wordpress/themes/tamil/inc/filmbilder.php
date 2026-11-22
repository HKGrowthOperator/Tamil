<?php
/**
 * Bild eines anderen Beitrags zum selben Film oder zur selben Veranstaltung (Bildkette, Stufe vor dem Rubrik-Pool).
 *
 * Ein Kino-Beitrag ohne eigenes Foto (etwa eine Kinoliste mit Titelkarte) zeigt das echte Beitragsbild des neuesten
 * anderen Beitrags über denselben Film, zum Beispiel das Plakat aus dem Bericht über die Sondervorstellung. Ebenso
 * für Termin-Reihen. Abgleich über einen Schlüssel: der Filmtitel aus kino_fakten, ein Titel in Anführungszeichen
 * („…“, “…”, "…", »…«) oder bei Terminen der Titelkopf vor „ – “ bzw. „: “; normalisiert (ohne Akzente, Satzzeichen,
 * Zusätze wie „(Tamil)“ oder „3D“). Findet sich kein gleicher Schlüssel, genügt ein Schlüssel aus mindestens zwei
 * Wörtern oder fünf Zeichen, der als ganze Wörter im Titel steht („Jailer 2 im Kino Claudia“ → „Jailer 2“).
 * Verzeichnis der Schlüssel: die 100 neuesten Beiträge aus Kino, Entertainment und Events mit eigenem Foto (keine
 * Titelkarte, kein Band), neueste zuerst, zehn Minuten im Transient (verworfen mit der Startseite,
 * tamil_flush_auswahl()).
 */

defined( 'ABSPATH' ) || exit;

const TAMIL_FILM_RUBRIKEN = array( 'kino', 'entertainment', 'events' );

/**
 * Schlüssel normalisieren: Kleinbuchstaben ohne Akzente, ohne Zusätze zur Fassung, nur Buchstaben, Ziffern und Leerzeichen.
 */
function tamil_film_norm( string $text ): string {
	$text = strtolower( remove_accents( html_entity_decode( wp_strip_all_tags( $text ), ENT_QUOTES, 'UTF-8' ) ) );
	$text = (string) preg_replace( '/\((?:tamil|omu|omeu|ov|ome?u?|3d|imax|telugu|hindi)[^)]*\)/', ' ', $text );
	$text = (string) preg_replace( '/\b(?:in )?3d\b/', ' ', $text );
	$text = (string) preg_replace( '/[^a-z0-9]+/', ' ', $text );
	return trim( (string) preg_replace( '/\s+/', ' ', $text ) );
}

/**
 * Schlüssel eines Beitrags: Film aus kino_fakten, Titel in Anführungszeichen, bei Terminen der Titelkopf.
 *
 * @return string[]
 */
function tamil_film_schluessel( int $post_id ): array {
	$titel  = html_entity_decode( get_the_title( $post_id ), ENT_QUOTES, 'UTF-8' );
	$liste  = array();
	$fakten = function_exists( 'tamil_site_kino_fakten' ) ? tamil_site_kino_fakten( $post_id ) : array();
	if ( ! empty( $fakten['film'] ) ) {
		$liste[] = (string) $fakten['film'];
	}
	if ( preg_match_all( '/[„“"»«‚‘]([^„“”"»«‚‘’]{2,80})[“”"«»‘’]/u', $titel, $treffer ) ) {
		$liste = array_merge( $liste, $treffer[1] );
	}
	if ( '' !== (string) get_post_meta( $post_id, 'event_datum', true ) ) {
		$kopf = preg_split( '/\s+[–-]\s+|:\s+/u', $titel );
		if ( is_array( $kopf ) && count( $kopf ) > 1 && str_word_count( tamil_film_norm( $kopf[0] ) ) >= 2 ) {
			$liste[] = $kopf[0];
		}
	}
	return array_values( array_unique( array_filter( array_map( 'tamil_film_norm', $liste ), static fn( $s ) => strlen( $s ) >= 2 ) ) );
}

/**
 * Eigenes, zeigbares Foto eines Beitrags (Anhang-ID) oder 0: kein Titelkarte, kein Band über 2,5:1.
 */
function tamil_eigenes_foto( int $post_id ): int {
	$thumb = (int) get_post_thumbnail_id( $post_id );
	if ( ! $thumb || ! wp_attachment_is_image( $thumb ) || tamil_ist_titelkarte( $post_id ) || tamil_bild_ist_breit( $thumb ) ) {
		return 0;
	}
	return $thumb;
}

/**
 * Verzeichnis Schlüssel → neuester Beitrag mit eigenem Foto (Kino, Entertainment, Events, Kinolisten, Termine).
 *
 * @return array<string,int>
 */
function tamil_film_verzeichnis(): array {
	static $verzeichnis = null;
	if ( null !== $verzeichnis ) {
		return $verzeichnis;
	}
	$gespeichert = get_transient( 'tamil_filmbilder' );
	if ( is_array( $gespeichert ) ) {
		$verzeichnis = $gespeichert;
		return $verzeichnis;
	}
	$verzeichnis = array();
	$ids         = tamil_ids(
		array(
			'posts_per_page' => 100,
			'meta_key'       => '_thumbnail_id', // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_key
			'category_name'  => implode( ',', TAMIL_FILM_RUBRIKEN ),
			'orderby'        => 'date',
			'order'          => 'DESC',
		)
	);
	foreach ( $ids as $id ) {
		if ( ! tamil_eigenes_foto( $id ) ) {
			continue;
		}
		foreach ( tamil_film_schluessel( $id ) as $s ) {
			if ( ! isset( $verzeichnis[ $s ] ) ) {
				$verzeichnis[ $s ] = $id; // neueste zuerst, der erste Treffer bleibt
			}
		}
	}
	set_transient( 'tamil_filmbilder', $verzeichnis, 10 * MINUTE_IN_SECONDS );
	return $verzeichnis;
}

/**
 * Gehört der Beitrag zu Kino, Entertainment oder Events (Rubrik, Kinoliste oder Termin)?
 */
function tamil_ist_film_oder_termin( int $post_id ): bool {
	if ( '' !== (string) get_post_meta( $post_id, 'event_datum', true ) || '' !== (string) get_post_meta( $post_id, 'kino_fakten', true ) ) {
		return true;
	}
	$kat = tamil_hauptkategorie( $post_id );
	return $kat && in_array( $kat->slug, TAMIL_FILM_RUBRIKEN, true );
}

/**
 * Beitrag, dessen Foto ein Kino- oder Terminbeitrag ohne eigenes Bild übernimmt, oder 0.
 */
function tamil_film_quelle( int $post_id ): int {
	if ( ! tamil_ist_film_oder_termin( $post_id ) ) {
		return 0;
	}
	$verzeichnis = tamil_film_verzeichnis();
	foreach ( tamil_film_schluessel( $post_id ) as $s ) {
		if ( isset( $verzeichnis[ $s ] ) && $verzeichnis[ $s ] !== $post_id ) {
			return $verzeichnis[ $s ];
		}
	}
	// Kein gleicher Schlüssel: ein bekannter Film- oder Reihentitel, der als ganze Wörter im Titel steht
	$titel  = ' ' . tamil_film_norm( get_the_title( $post_id ) ) . ' ';
	$beste  = 0;
	$laenge = 0;
	foreach ( $verzeichnis as $s => $id ) {
		$tragfaehig = str_contains( $s, ' ' ) || strlen( $s ) >= 5;
		if ( $id !== $post_id && $tragfaehig && strlen( $s ) > $laenge && str_contains( $titel, ' ' . $s . ' ' ) ) {
			$beste  = $id;
			$laenge = strlen( $s );
		}
	}
	return $beste;
}
