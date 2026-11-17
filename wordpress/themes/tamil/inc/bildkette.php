<?php
/**
 * Bildkette: Jeder Anreißer zeigt ein echtes Bild (Luis, 17.11.2026: nichts nur als Text). Eine Stelle für alle
 * Bausteine, in dieser Reihenfolge:
 *
 *   a) das eigene Beitragsbild, wenn es ein Foto ist (keine Titelkarte „Grafik: Tamil.de“). Bänder breiter als 2,5:1
 *      werden im Rahmen beschnitten; ihr Nachweis bekommt „zugeschnitten“.
 *   b) sonst das erste Bild aus dem Text des Beitrags, das in der Mediathek liegt und mindestens 600 px breit ist
 *      (mit seinen Größen, srcset und Nachweis).
 *   c) sonst ein Symbolbild aus dem Rubrik-Pool (inc/bildpool.php): vier echte Fotos je Rubrik, fest nach Beitrags-ID
 *      gewählt, damit Nachbarn verschieden sind; sichtbar als „Symbolbild“ gekennzeichnet, mit vollem Nachweis.
 *
 * Die Nachweise sammelt der Fuß („Bildnachweise dieser Seite“) als HTML mit Links auf Dateiseite und Lizenz.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Ist das Beitragsbild eine Titelkarte (Schlagzeile als Bild)? Erkennbar am Nachweis „Grafik: Tamil.de“, sonst an der
 * Herkunft „karte“ oder der Lizenz „tamil-grafik“ – außer der Nachweis nennt ein Foto („Foto: …“, dann wurde das Bild
 * nachträglich getauscht). Titelkarten zeigt das Theme nie; der Beitrag bekommt sein Bild aus der Kette.
 */
function tamil_ist_titelkarte( int $post_id ): bool {
	$nachweis = strtolower( tamil_bildnachweis( $post_id ) );
	if ( str_starts_with( $nachweis, 'grafik: tamil.de' ) ) {
		return true;
	}
	if ( str_starts_with( $nachweis, 'foto:' ) ) {
		return false;
	}
	return 'karte' === get_post_meta( $post_id, 'bild_origin', true ) || 'tamil-grafik' === get_post_meta( $post_id, 'bild_lizenz', true );
}

/**
 * Bildwahl eines Beitrags über die Kette (je Aufruf der Seite einmal gerechnet).
 *
 * @return array{art:string,id:int,pool:array<string,mixed>,breit:bool,alt:string,nachweis:string}
 *         art „eigen“, „inhalt“ oder „pool“; nachweis ist escaptes HTML.
 */
function tamil_bildwahl( int $post_id ): array {
	static $wahl = array();
	if ( isset( $wahl[ $post_id ] ) ) {
		return $wahl[ $post_id ];
	}
	$thumb = (int) get_post_thumbnail_id( $post_id );
	if ( $thumb && wp_attachment_is_image( $thumb ) && ! tamil_ist_titelkarte( $post_id ) ) {
		$breit            = tamil_bild_ist_breit( $thumb );
		$text             = str_replace( ' · ', ', ', tamil_bildnachweis( $post_id ) );
		$wahl[ $post_id ] = array(
			'art'      => 'eigen',
			'id'       => $thumb,
			'pool'     => array(),
			'breit'    => $breit,
			'alt'      => tamil_bild_alt( $post_id ),
			'nachweis' => '' !== $text ? esc_html( $text . ( $breit ? ', ' . __( 'zugeschnitten', 'tamil' ) : '' ) ) : '',
		);
		return $wahl[ $post_id ];
	}
	$inhalt = tamil_inhaltsbild( $post_id );
	if ( $inhalt ) {
		$breit            = tamil_bild_ist_breit( $inhalt['id'] );
		$alt              = trim( (string) get_post_meta( $inhalt['id'], '_wp_attachment_image_alt', true ) );
		$wahl[ $post_id ] = array(
			'art'      => 'inhalt',
			'id'       => $inhalt['id'],
			'pool'     => array(),
			'breit'    => $breit,
			'alt'      => wp_strip_all_tags( get_the_title( $post_id ) ) === $alt ? '' : $alt,
			'nachweis' => '' !== $inhalt['nachweis'] ? esc_html( $inhalt['nachweis'] . ( $breit ? ', ' . __( 'zugeschnitten', 'tamil' ) : '' ) ) : '',
		);
		return $wahl[ $post_id ];
	}
	$pool             = tamil_pool_bild( tamil_rubrik_slug( $post_id ), $post_id );
	$wahl[ $post_id ] = array(
		'art'      => 'pool',
		'id'       => 0,
		'pool'     => $pool,
		'breit'    => false,
		/* translators: %s: Bildbeschreibung */
		'alt'      => sprintf( __( 'Symbolbild: %s', 'tamil' ), $pool['alt'] ),
		'nachweis' => tamil_pool_nachweis( $pool ),
	);
	return $wahl[ $post_id ];
}

/**
 * Hat der Beitrag ein eigenes Bild (Beitragsbild als Foto oder Bild im Text), also kein Symbolbild?
 */
function tamil_bild_zeigbar( int $post_id ): bool {
	return 'pool' !== tamil_bildwahl( $post_id )['art'];
}

/**
 * Ist ein Bild breiter als 2,5:1 (Band, Banner)? Solche Bilder schneidet der Rahmen, der Nachweis sagt es.
 */
function tamil_bild_ist_breit( int $attachment_id ): bool {
	$meta = wp_get_attachment_metadata( $attachment_id );
	$w    = (int) ( $meta['width'] ?? 0 );
	$h    = (int) ( $meta['height'] ?? 0 );
	return $w && $h && $w / $h > 2.5;
}

/**
 * Erstes Bild aus dem Text eines Beitrags, das in der Mediathek liegt (lokal, also auflösbar über die Adresse) und
 * mindestens 600 px breit ist; Nachweis aus der Bildunterschrift des Anhangs oder der figcaption im Text.
 *
 * Die Klasse wp-image-<ID> wird nicht geglaubt: Nach der Übernahme der alten Seite können IDs auf andere Anhänge
 * zeigen. Maßgeblich ist die Adresse im src.
 *
 * @return array{id:int,nachweis:string}|array{}
 */
function tamil_inhaltsbild( int $post_id ): array {
	$html = (string) get_post_field( 'post_content', $post_id );
	if ( ! str_contains( $html, '<img' ) || ! preg_match_all( '/<img\b[^>]*>/i', $html, $treffer, PREG_OFFSET_CAPTURE ) ) {
		return array();
	}
	foreach ( $treffer[0] as $i => list( $tag, $pos ) ) {
		if ( $i >= 6 || ! preg_match( '/\ssrc\s*=\s*(["\'])([^"\']+)\1/i', $tag, $src ) ) {
			continue;
		}
		$id = tamil_anhang_aus_url( html_entity_decode( $src[2], ENT_QUOTES ) );
		if ( ! $id ) {
			continue;
		}
		$meta = wp_get_attachment_metadata( $id );
		if ( (int) ( $meta['width'] ?? 0 ) < 600 ) {
			continue;
		}
		$nachweis = trim( (string) wp_get_attachment_caption( $id ) );
		if ( '' === $nachweis && preg_match( '#^.{0,400}?<figcaption[^>]*>(.*?)</figcaption>#is', substr( $html, $pos + strlen( $tag ) ), $fc ) ) {
			$nachweis = trim( wp_strip_all_tags( $fc[1] ) );
		}
		if ( str_starts_with( strtolower( $nachweis ), 'grafik: tamil.de' ) ) {
			continue; // eine Titelkarte im Text ist auch kein Foto
		}
		return array(
			'id'       => $id,
			'nachweis' => str_replace( ' · ', ', ', $nachweis ),
		);
	}
	return array();
}

/**
 * Anhang zu einer Bildadresse aus dem Text: nur Dateien unter uploads/ dieser Website. Größenzusätze („-300x200“)
 * werden abgeschnitten, damit auch verkleinerte Fassungen auf das Original führen.
 */
function tamil_anhang_aus_url( string $url ): int {
	static $cache = array();
	if ( isset( $cache[ $url ] ) ) {
		return $cache[ $url ];
	}
	$basis = wp_get_upload_dir()['baseurl'];
	$pfad  = (string) wp_parse_url( $url, PHP_URL_PATH );
	$hier  = (string) wp_parse_url( $basis, PHP_URL_PATH );
	$host  = wp_parse_url( $url, PHP_URL_HOST );
	if ( '' === $pfad || ( $host && wp_parse_url( $basis, PHP_URL_HOST ) !== $host ) || ! str_starts_with( $pfad, trailingslashit( $hier ) ) ) {
		$cache[ $url ] = 0;
		return 0;
	}
	$voll = $basis . substr( $pfad, strlen( $hier ) );
	$id   = attachment_url_to_postid( $voll );
	if ( ! $id ) {
		$id = attachment_url_to_postid( (string) preg_replace( '/-\d+x\d+(?=\.[a-z0-9]+$)/i', '', $voll ) );
	}
	$cache[ $url ] = $id && wp_attachment_is_image( $id ) ? (int) $id : 0;
	return $cache[ $url ];
}

/**
 * Nachweis eines Pool-Bilds als HTML: „Symbolbild, Foto: Urheber / Wikimedia Commons, CC BY-SA 4.0, zugeschnitten“,
 * Urheber verlinkt auf die Dateiseite, Lizenz auf den Lizenztext.
 *
 * @param array<string,mixed> $pool Eintrag aus tamil_bildpool().
 */
function tamil_pool_nachweis( array $pool ): string {
	return sprintf(
		/* translators: 1: Urheber mit Link, 2: Lizenz mit Link */
		__( 'Symbolbild, Foto: %1$s / Wikimedia Commons, %2$s, zugeschnitten', 'tamil' ),
		'<a href="' . esc_url( (string) $pool['seite'] ) . '">' . esc_html( (string) $pool['urheber'] ) . '</a>',
		'<a href="' . esc_url( (string) $pool['lizenz_url'] ) . '" rel="license">' . esc_html( (string) $pool['lizenz'] ) . '</a>'
	);
}

/**
 * Erlaubtes HTML in Nachweisen (Links auf Dateiseite und Lizenz).
 *
 * @return array<string,array<string,bool>>
 */
function tamil_nachweis_kses(): array {
	return array(
		'a' => array(
			'href' => true,
			'rel'  => true,
		),
	);
}

/**
 * Nachweis eines Beitragsbilds aus der Kette als HTML (für Bildunterschrift und Fuß).
 */
function tamil_bild_nachweis_html( int $post_id ): string {
	return tamil_bildwahl( $post_id )['nachweis'];
}

/**
 * Bild eines Beitrags aus der Kette als <img> für einen Rahmen; merkt den Nachweis für den Fuß. Ein Symbolbild aus
 * dem Pool trägt das Schild „Symbolbild“ (für Vorleser steht es im Alternativtext).
 *
 * @param array<string,mixed> $opt {
 *     @type string $size      Bildgröße (Standard „large“, ungeschnitten; der Rahmen schneidet).
 *     @type string $sizes     sizes-Angabe für srcset.
 *     @type bool   $eager     Sofort und vorrangig laden (erster Bildschirm).
 *     @type bool   $sofort    Sofort laden, ohne Vorrang (kleine Bilder im seitlichen Streifen).
 *     @type string $klasse    Klasse des Bilds.
 *     @type bool   $schild    Schild „Symbolbild“ im Rahmen (Standard ja).
 *     @type bool   $nur_eigen Nur das eigene Beitragsbild (Seiten wie Impressum), sonst nichts.
 * }
 */
function tamil_bild( int $post_id, array $opt = array() ): string {
	$w = tamil_bildwahl( $post_id );
	if ( ! empty( $opt['nur_eigen'] ) && 'eigen' !== $w['art'] ) {
		return '';
	}
	$attr = array(
		'alt'      => $w['alt'],
		'decoding' => 'async',
	);
	if ( ! empty( $opt['eager'] ) ) {
		$attr['loading']       = 'eager';
		$attr['fetchpriority'] = 'high';
	} else {
		// Bilder in seitlich laufenden Streifen lädt der Browser bei „lazy“ erst, wenn sie hineingewischt werden.
		$attr['loading'] = ! empty( $opt['sofort'] ) ? 'eager' : 'lazy';
	}
	$klassen = array_filter( array( (string) ( $opt['klasse'] ?? '' ), $w['breit'] ? 'bild--breit' : '' ) );
	if ( $klassen ) {
		$attr['class'] = implode( ' ', $klassen );
	}
	if ( 'pool' === $w['art'] ) {
		$p   = $w['pool'];
		$img = sprintf(
			'<img src="%1$s" width="%2$d" height="%3$d" alt="%4$s" decoding="async" loading="%5$s"%6$s%7$s style="object-position: %8$s">',
			esc_url( TAMIL_THEME_URI . '/assets/img/rubrik/' . $p['datei'] ),
			(int) $p['w'],
			(int) $p['h'],
			esc_attr( $attr['alt'] ),
			esc_attr( $attr['loading'] ),
			isset( $attr['fetchpriority'] ) ? ' fetchpriority="high"' : '',
			isset( $attr['class'] ) ? ' class="' . esc_attr( $attr['class'] ) . '"' : '',
			esc_attr( (string) $p['fokus'] )
		);
		if ( $opt['schild'] ?? true ) {
			$img .= '<span class="symbolbild" aria-hidden="true">' . esc_html__( 'Symbolbild', 'tamil' ) . '</span>';
		}
	} else {
		if ( ! empty( $opt['sizes'] ) ) {
			$attr['sizes'] = (string) $opt['sizes'];
		}
		$img = (string) wp_get_attachment_image( $w['id'], (string) ( $opt['size'] ?? 'large' ), false, $attr );
	}
	if ( '' !== $img ) {
		tamil_nachweise( $w['nachweis'] );
	}
	return $img;
}

/**
 * Ein Bild aus dem Rubrik-Pool als <img> (Rubrikkacheln ohne Beitrag mit Foto, Leerzustände); merkt den Nachweis.
 *
 * @param array<string,mixed> $opt { @type int $n Nummer im Pool, @type bool $schild, @type bool $sofort, @type bool $alt. }
 */
function tamil_pool_img( string $slug, array $opt = array() ): string {
	$p = tamil_pool_bild( $slug, (int) ( $opt['n'] ?? 0 ) );
	tamil_nachweise( tamil_pool_nachweis( $p ) );
	$img = sprintf(
		'<img src="%1$s" width="%2$d" height="%3$d" alt="%4$s" decoding="async" loading="%5$s" style="object-position: %6$s">',
		esc_url( TAMIL_THEME_URI . '/assets/img/rubrik/' . $p['datei'] ),
		(int) $p['w'],
		(int) $p['h'],
		/* translators: %s: Bildbeschreibung */
		esc_attr( ( $opt['alt'] ?? true ) ? sprintf( __( 'Symbolbild: %s', 'tamil' ), $p['alt'] ) : '' ),
		! empty( $opt['sofort'] ) ? 'eager' : 'lazy',
		esc_attr( (string) $p['fokus'] )
	);
	if ( $opt['schild'] ?? true ) {
		$img .= '<span class="symbolbild" aria-hidden="true">' . esc_html__( 'Symbolbild', 'tamil' ) . '</span>';
	}
	return $img;
}
