<?php
/**
 * Bildkette: Jeder Anreißer zeigt ein echtes Bild (Luis, 17.11.2026: nichts nur als Text). Eine Stelle für alle
 * Bausteine, in dieser Reihenfolge:
 *
 *   a) das eigene Beitragsbild, wenn es ein Foto ist (keine Titelkarte „Grafik: Tamil.de“). Bänder breiter als 2,5:1
 *      werden im Rahmen beschnitten; ihr Nachweis bekommt „zugeschnitten“.
 *   b) sonst das erste Bild aus dem Text des Beitrags, das in der Mediathek liegt und mindestens 600 px breit ist
 *      (mit seinen Größen, srcset und Nachweis).
 *   c) sonst, bei Kino- und Terminbeiträgen, das Foto des neuesten anderen Beitrags zum selben Film bzw. zur selben
 *      Veranstaltung (inc/filmbilder.php), mit dessen Nachweis und ohne Schild, weil es den Film zeigt;
 *   d) sonst ein Symbolbild aus dem Rubrik-Pool (inc/bildpool.php): echte Fotos je Rubrik, bevorzugt nach Beitrags-ID
 *      gewählt; auf einer Seite reihum vergeben, damit kein Ersatzbild doppelt erscheint (tamil_pool_seite()); sichtbar
 *      als „Symbolbild“ gekennzeichnet, mit Nachweis.
 *
 * Nachweise entstehen an einer Stelle (tamil_nachweis_bauen()): Urheber mit Link auf die Dateiseite, Lizenz mit Link
 * auf den Lizenztext, „zugeschnitten“ bei Fotos unter freier Lizenz (die Rahmen schneiden per object-fit) und bei
 * Bändern; redaktionelle Symbolbilder beginnen mit „Symbolbild“. Der Fuß sammelt sie („Bildnachweise dieser Seite“).
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
 * @return array{art:string,id:int,pool:array<string,mixed>,breit:bool,symbol:bool,alt:string,nachweis:string,quelle:int}
 *         art „eigen“, „inhalt“, „film“ oder „pool“; nachweis ist escaptes HTML (beim Pool leer, siehe
 *         tamil_bild_nachweis_html()); symbol = Symbolbild (Pool oder redaktionell gekennzeichnet); quelle = Beitrag
 *         des Filmbilds.
 */
function tamil_bildwahl( int $post_id ): array {
	static $wahl = array();
	if ( isset( $wahl[ $post_id ] ) ) {
		return $wahl[ $post_id ];
	}
	$thumb = (int) get_post_thumbnail_id( $post_id );
	if ( $thumb && wp_attachment_is_image( $thumb ) && ! tamil_ist_titelkarte( $post_id ) ) {
		$breit            = tamil_bild_ist_breit( $thumb );
		$symbol           = tamil_ist_symbolbild( $post_id, $thumb );
		$wahl[ $post_id ] = array(
			'art'      => 'eigen',
			'id'       => $thumb,
			'pool'     => array(),
			'breit'    => $breit,
			'symbol'   => $symbol,
			'alt'      => tamil_bild_alt( $post_id ),
			'nachweis' => tamil_nachweis_bauen( tamil_bildnachweis( $post_id ), tamil_nachweis_angaben( $post_id, $breit, $symbol ) ),
			'quelle'   => 0,
		);
		return $wahl[ $post_id ];
	}
	$inhalt = tamil_inhaltsbild( $post_id );
	if ( $inhalt ) {
		$breit            = tamil_bild_ist_breit( $inhalt['id'] );
		$alt              = trim( (string) get_post_meta( $inhalt['id'], '_wp_attachment_image_alt', true ) );
		$symbol           = tamil_ist_symbolbild( 0, $inhalt['id'], $inhalt['nachweis'] );
		$wahl[ $post_id ] = array(
			'art'      => 'inhalt',
			'id'       => $inhalt['id'],
			'pool'     => array(),
			'breit'    => $breit,
			'symbol'   => $symbol,
			'alt'      => wp_strip_all_tags( get_the_title( $post_id ) ) === $alt ? '' : $alt,
			'nachweis' => tamil_nachweis_bauen(
				$inhalt['nachweis'],
				array(
					'zuschnitt' => $breit,
					'symbol'    => $symbol,
				)
			),
			'quelle'   => 0,
		);
		return $wahl[ $post_id ];
	}
	$quelle = tamil_film_quelle( $post_id );
	if ( $quelle ) {
		$foto             = tamil_eigenes_foto( $quelle );
		$alt              = trim( (string) get_post_meta( $foto, '_wp_attachment_image_alt', true ) );
		$symbol           = tamil_ist_symbolbild( $quelle, $foto );
		$wahl[ $post_id ] = array(
			'art'      => 'film',
			'id'       => $foto,
			'pool'     => array(),
			'breit'    => false,
			'symbol'   => $symbol,
			'alt'      => wp_strip_all_tags( get_the_title( $post_id ) ) === $alt ? '' : $alt,
			'nachweis' => tamil_nachweis_bauen( tamil_bildnachweis( $quelle ), tamil_nachweis_angaben( $quelle, false, $symbol ) ),
			'quelle'   => $quelle,
		);
		return $wahl[ $post_id ];
	}
	// Symbolbild aus dem Pool: welches Bild, entscheidet erst die Ausgabe (tamil_pool_fuer()), damit nur gezeigte
	// Bilder auf der Seite als vergeben gelten
	$wahl[ $post_id ] = array(
		'art'      => 'pool',
		'id'       => 0,
		'pool'     => array(),
		'breit'    => false,
		'symbol'   => true,
		'alt'      => '',
		'nachweis' => '',
		'quelle'   => 0,
	);
	return $wahl[ $post_id ];
}

/**
 * Symbolbild aus dem Pool für einen Beitrag ohne eigenes Bild: einmal je Seite gewählt (tamil_pool_seite()), danach
 * für denselben Beitrag immer dasselbe.
 *
 * @return array{datei:string,w:int,h:int,alt:string,urheber:string,lizenz:string,lizenz_url:string,seite:string,fokus:string}
 */
function tamil_pool_fuer( int $post_id ): array {
	static $gewaehlt = array();
	if ( ! isset( $gewaehlt[ $post_id ] ) ) {
		$gewaehlt[ $post_id ] = tamil_pool_seite( tamil_rubrik_slug( $post_id ), $post_id );
	}
	return $gewaehlt[ $post_id ];
}

/**
 * Pool-Bild für einen Rahmen dieser Seite: bevorzugt das zur Nummer gehörende (Beitrags-ID, damit ein Beitrag auf
 * allen Seiten möglichst dasselbe Bild zeigt); ist es auf der Seite schon vergeben, das nächste freie desselben Pools.
 * Erst wenn alle vergeben sind, kommt das am seltensten gezeigte wieder.
 *
 * @return array{datei:string,w:int,h:int,alt:string,urheber:string,lizenz:string,lizenz_url:string,seite:string,fokus:string}
 */
function tamil_pool_seite( string $slug, int $n ): array {
	static $gezeigt = array();
	$liste          = tamil_pool_liste( $slug );
	$anzahl         = count( $liste );
	$start          = abs( $n ) % $anzahl;
	$wahl           = $liste[ $start ];
	for ( $i = 0; $i < $anzahl; $i++ ) {
		$p = $liste[ ( $start + $i ) % $anzahl ];
		if ( ( $gezeigt[ $p['datei'] ] ?? 0 ) < ( $gezeigt[ $wahl['datei'] ] ?? 0 ) ) {
			$wahl = $p;
		}
		if ( empty( $gezeigt[ $p['datei'] ] ) ) {
			$wahl = $p;
			break;
		}
	}
	// Pool der Rubrik erschöpft: erst ein freies Bild des allgemeinen Pools, bevor sich eines wiederholt (CODE-06)
	if ( ! empty( $gezeigt[ $wahl['datei'] ] ) ) {
		$allgemein = tamil_pool_liste( 'allgemein' );
		$anzahl    = count( $allgemein );
		for ( $i = 0; $i < $anzahl; $i++ ) {
			$p = $allgemein[ ( abs( $n ) + $i ) % $anzahl ];
			if ( empty( $gezeigt[ $p['datei'] ] ) ) {
				$wahl = $p;
				break;
			}
		}
	}
	$gezeigt[ $wahl['datei'] ] = ( $gezeigt[ $wahl['datei'] ] ?? 0 ) + 1;
	return $wahl;
}

/**
 * Ist ein redaktionelles Beitragsbild ein Symbolbild? Erkennbar an „Symbolbild“ im Alternativtext oder in der
 * Bildunterschrift des Anhangs, im Nachweis oder am Meta „bild_symbolbild“ des Beitrags.
 */
function tamil_ist_symbolbild( int $post_id, int $attachment_id, string $nachweis = '' ): bool {
	$texte = array(
		$nachweis,
		$attachment_id ? (string) get_post_meta( $attachment_id, '_wp_attachment_image_alt', true ) : '',
		$attachment_id ? (string) wp_get_attachment_caption( $attachment_id ) : '',
		$post_id ? (string) get_post_meta( $post_id, 'bild_credit', true ) : '',
	);
	if ( $post_id && '' !== (string) get_post_meta( $post_id, 'bild_symbolbild', true ) && '0' !== (string) get_post_meta( $post_id, 'bild_symbolbild', true ) ) {
		return true;
	}
	return (bool) preg_grep( '/symbolbild/iu', $texte );
}

/**
 * Angaben eines Beitrags für den Nachweis seines Bilds: Dateiseite und Lizenz-Adresse aus den Radar-Feldern
 * (bild_quelle_url, bild_lizenz_url, bild_lizenz), dazu Zuschnitt und Symbolbild.
 *
 * @return array{seite:string,lizenz_url:string,zuschnitt:bool,symbol:bool}
 */
function tamil_nachweis_angaben( int $post_id, bool $breit, bool $symbol ): array {
	$lizenz_url = (string) get_post_meta( $post_id, 'bild_lizenz_url', true );
	if ( '' === $lizenz_url ) {
		$lizenz_url = tamil_lizenz_url( (string) get_post_meta( $post_id, 'bild_lizenz', true ) );
	}
	return array(
		'seite'      => (string) get_post_meta( $post_id, 'bild_quelle_url', true ),
		'lizenz_url' => $lizenz_url,
		'zuschnitt'  => $breit,
		'symbol'     => $symbol,
	);
}

/**
 * Lizenz-Adresse zu einem Lizenznamen aus dem Nachweis („CC BY-SA 4.0“, „CC BY 2.0 at“, „CC0 1.0“, „Public Domain“)
 * oder einem Kürzel des Radars („cc-by-sa-4.0“, „cc0-1.0“, „pdm-1.0“). Unbekannt: leer.
 */
function tamil_lizenz_url( string $name ): string {
	$name = strtolower( trim( str_replace( array( '_', '-' ), array( ' ', ' ' ), $name ) ) );
	if ( preg_match( '/^cc ?by( sa| nd| nc| nc sa| nc nd)? ?([1-4]\.[05])(?: ([a-z]{2}))?$/', $name, $m ) ) {
		$art = 'by' . str_replace( ' ', '-', (string) $m[1] );
		return 'https://creativecommons.org/licenses/' . $art . '/' . $m[2] . '/' . ( ! empty( $m[3] ) ? $m[3] . '/' : '' );
	}
	if ( preg_match( '/^cc ?0(?: 1\.0)?$/', $name ) ) {
		return 'https://creativecommons.org/publicdomain/zero/1.0/';
	}
	if ( preg_match( '/^(?:pd|pdm(?: 1\.0)?|public domain(?: mark)?(?: 1\.0)?|gemeinfrei)$/', $name ) ) {
		return 'https://creativecommons.org/publicdomain/mark/1.0/';
	}
	return '';
}

/**
 * Nachweis als HTML aus dem Text („Foto: Urheber / Wikimedia Commons, CC BY-SA 4.0“): Urheber verlinkt auf die
 * Dateiseite, Lizenz auf den Lizenztext, dazu „zugeschnitten“ und bei Symbolbildern „Symbolbild,“ davor.
 *
 * Ohne bekannte Dateiseite, aber mit Wikimedia Commons als Herkunft verlinkt „Wikimedia Commons“ die Suche nach dem
 * Urheber auf Commons (keine erfundene Dateiseite). „zugeschnitten“ steht bei Bändern und bei jedem Foto unter freier
 * Lizenz, denn die Rahmen schneiden Bilder per object-fit auf ihr Format zu.
 *
 * @param array<string,mixed> $angaben { @type string $seite, @type string $lizenz_url, @type bool $zuschnitt, @type bool $symbol }
 */
function tamil_nachweis_bauen( string $text, array $angaben = array() ): string {
	$text = trim( (string) preg_replace( '/\s+/u', ' ', str_replace( ' · ', ', ', $text ) ) );
	if ( '' === $text ) {
		return '';
	}
	$seite      = (string) ( $angaben['seite'] ?? '' );
	$lizenz_url = (string) ( $angaben['lizenz_url'] ?? '' );
	$zuschnitt  = ! empty( $angaben['zuschnitt'] );
	$symbol     = ! empty( $angaben['symbol'] );

	// Lizenz am Ende: „…, CC BY-SA 4.0“ (danach höchstens Zusätze wie „zugeschnitten“)
	$lizenz = '';
	$rest   = '';
	if ( preg_match( '/^(.*?),\s*(CC0(?: 1\.0)?|CC BY(?:-(?:SA|ND|NC|NC-SA|NC-ND))? [1-4]\.[05](?: [a-z]{2})?|Public Domain(?: Mark)?(?: 1\.0)?|PD)\b\s*(?:,\s*(.*))?$/iu', $text, $m ) ) {
		$text   = $m[1];
		$lizenz = $m[2];
		$rest   = trim( (string) ( $m[3] ?? '' ) );
		if ( '' === $lizenz_url ) {
			$lizenz_url = tamil_lizenz_url( $lizenz );
		}
	}
	$frei = '' !== $lizenz && '' !== tamil_lizenz_url( $lizenz );

	// Kopf: „Foto: Urheber / Wikimedia Commons“
	$praefix = '';
	if ( preg_match( '/^((?:Symbolbild,?\s*)?(?:Foto|Bild|Filmbild|Grafik|Illustration)\s*:\s*)(.*)$/iu', $text, $k ) ) {
		$praefix = $k[1];
		$text    = $k[2];
	}
	$commons = '';
	if ( preg_match( '#^(.*?)\s*[/,]\s*(Wikimedia Commons)$#iu', $text, $c ) ) {
		$text    = $c[1];
		$commons = $c[2];
	}
	$urheber = esc_html( $text );
	if ( '' !== $seite && preg_match( '#^https?://#i', $seite ) ) {
		$urheber = '<a href="' . esc_url( $seite ) . '">' . $urheber . '</a>';
	}
	$html = esc_html( $praefix ) . $urheber;
	if ( '' !== $commons ) {
		$html .= ' / ' . ( '' === $seite && '' !== $text
			? '<a href="' . esc_url( 'https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=' . rawurlencode( trim( (string) preg_replace( '/\s*\(https?:[^)]*\)/i', '', $text ) ) ) ) . '">' . esc_html( $commons ) . '</a>'
			: esc_html( $commons ) );
	}
	if ( '' !== $lizenz ) {
		$html .= ', ' . ( '' !== $lizenz_url ? '<a href="' . esc_url( $lizenz_url ) . '" rel="license">' . esc_html( $lizenz ) . '</a>' : esc_html( $lizenz ) );
	}
	if ( '' !== $rest ) {
		$html .= ', ' . esc_html( $rest );
	}
	if ( ( $zuschnitt || $frei || '' !== $commons ) && ! preg_match( '/zugeschnitten|ausschnitt/iu', $rest . ' ' . $text ) ) {
		$html .= ', ' . esc_html__( 'zugeschnitten', 'tamil' );
	}
	if ( $symbol && ! preg_match( '/^\s*symbolbild/iu', $praefix . $text ) ) {
		$html = esc_html__( 'Symbolbild', 'tamil' ) . ', ' . $html;
	}
	return $html;
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
	return tamil_nachweis_bauen(
		'Foto: ' . $pool['urheber'] . ' / Wikimedia Commons, ' . $pool['lizenz'],
		array(
			'seite'      => (string) $pool['seite'],
			'lizenz_url' => (string) $pool['lizenz_url'],
			'zuschnitt'  => true,
			'symbol'     => true,
		)
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
	$w = tamil_bildwahl( $post_id );
	return 'pool' === $w['art'] ? tamil_pool_nachweis( tamil_pool_fuer( $post_id ) ) : $w['nachweis'];
}

/**
 * Schild „Symbolbild“ im Rahmen; in Rahmen unter 150 px nur „S“ (CSS, Container-Abfrage), der volle Hinweis steht im
 * Alternativtext, in der Bildunterschrift und im Fuß.
 */
function tamil_symbolbild_schild(): string {
	return '<span class="symbolbild" aria-hidden="true"><span class="symbolbild__lang">' . esc_html__( 'Symbolbild', 'tamil' ) . '</span><span class="symbolbild__kurz" title="' . esc_attr__( 'Symbolbild', 'tamil' ) . '">S</span></span>';
}

/**
 * <img> eines Pool-Bilds mit kleinen Fassungen (320 und 480 px) im srcset. Die 480er braucht die 160 px breite
 * Rubrikkachel am Handy mit doppelter bis dreifacher Pixeldichte; sonst lädt es das ganze Bild (QA-19).
 *
 * @param array<string,mixed> $p    Eintrag aus tamil_bildpool().
 * @param array<string,string> $attr alt, loading, sizes, class, fetchpriority.
 */
function tamil_pool_tag( array $p, array $attr ): string {
	$basis  = TAMIL_THEME_URI . '/assets/img/rubrik/';
	$klein  = str_replace( '.webp', '-320.webp', (string) $p['datei'] );
	$mittel = str_replace( '.webp', '-480.webp', (string) $p['datei'] );
	return sprintf(
		'<img src="%1$s" srcset="%2$s 320w, %11$s 480w, %1$s %3$dw" sizes="%4$s" width="%3$d" height="%5$d" alt="%6$s" decoding="async" loading="%7$s"%8$s%9$s style="object-position: %10$s">',
		esc_url( $basis . $p['datei'] ),
		esc_url( $basis . $klein ),
		(int) $p['w'],
		esc_attr( '' !== ( $attr['sizes'] ?? '' ) ? $attr['sizes'] : '100vw' ),
		(int) $p['h'],
		esc_attr( (string) ( $attr['alt'] ?? '' ) ),
		esc_attr( (string) ( $attr['loading'] ?? 'lazy' ) ),
		! empty( $attr['fetchpriority'] ) ? ' fetchpriority="' . ( 'low' === $attr['fetchpriority'] ? 'low' : 'high' ) . '"' : '',
		! empty( $attr['class'] ) ? ' class="' . esc_attr( $attr['class'] ) . '"' : '',
		esc_attr( (string) $p['fokus'] ),
		esc_url( $basis . $mittel )
	);
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
 *     @type bool   $niedrig   Mit geringem Vorrang laden (Bildkarten unter dem Aufmacher, damit dessen Bild zuerst kommt).
 *     @type string $klasse    Klasse des Bilds.
 *     @type bool   $schild    Schild „Symbolbild“ im Rahmen (Standard ja).
 *     @type bool   $signet    Signet unten rechts im Bild (Standard ja: jeder Beitrag trägt es; nein bei Rubrikkacheln,
 *                             Seiten und Verzeichniseinträgen, siehe inc/signatur.php).
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
		if ( ! empty( $opt['niedrig'] ) ) {
			$attr['fetchpriority'] = 'low'; // Bildkarten nahe dem Aufmacher: nicht vor dessen Bild laden
		}
	}
	$klassen = array_filter( array( (string) ( $opt['klasse'] ?? '' ), $w['breit'] ? 'bild--breit' : '' ) );
	if ( $klassen ) {
		$attr['class'] = implode( ' ', $klassen );
	}
	$signet = (bool) ( $opt['signet'] ?? true );
	$ton    = 'dunkel';
	// Ein geliehenes Filmbild, das ein anderer Beitrag auf dieser Seite schon als Kartenbild zeigt, weicht einem
	// Symbolbild aus dem Pool (CODE-06). Eigene Bilder werden nie ersetzt; Rubrikkacheln (ohne Signet) zählen nicht.
	// Steht der Beitrag, dem das Bild gehört, in der Liste der Seite, weicht das geliehene Bild auch dann aus, wenn der
	// Besitzer erst weiter unten kommt.
	$besitzer = (int) ( $w['quelle'] ?? 0 );
	if ( $signet && 'film' === $w['art'] && ( ! tamil_anhang_frei( (int) $w['id'], $post_id ) || ( $besitzer && $besitzer !== $post_id && tamil_auf_seite( $besitzer ) ) ) ) {
		$w = array_merge(
			$w,
			array(
				'art'      => 'pool',
				'id'       => 0,
				'breit'    => false,
				'symbol'   => true,
				'nachweis' => '',
			)
		);
	}
	if ( 'pool' === $w['art'] ) {
		$p             = tamil_pool_fuer( $post_id );
		$ton           = $signet ? tamil_signatur_ecke_ton_pool( (string) $p['datei'] ) : $ton;
		$w['nachweis'] = tamil_pool_nachweis( $p );
		/* translators: %s: Bildbeschreibung */
		$attr['alt']   = sprintf( __( 'Symbolbild: %s', 'tamil' ), $p['alt'] );
		$attr['sizes'] = (string) ( $opt['sizes'] ?? '' );
		$img           = tamil_pool_tag( $p, $attr );
	} else {
		if ( ! empty( $opt['sizes'] ) ) {
			$attr['sizes'] = (string) $opt['sizes'];
		}
		if ( $signet ) {
			tamil_anhang_frei( (int) $w['id'], $post_id ); // merken, damit spätere Filmbilder ausweichen
		}
		$img = (string) wp_get_attachment_image( $w['id'], (string) ( $opt['size'] ?? 'large' ), false, $attr );
		if ( '' !== $img && $signet ) {
			$ton = tamil_signatur_ecke_ton( (int) $w['id'] );
		}
	}
	if ( '' !== $img && $w['symbol'] && ( $opt['schild'] ?? true ) ) {
		$img .= tamil_symbolbild_schild();
	}
	if ( '' !== $img && $signet ) {
		$img .= tamil_signatur_ecke_html( $ton );
	}
	if ( '' !== $img ) {
		tamil_nachweise( $w['nachweis'] );
	}
	return $img;
}

/**
 * Beiträge, die diese Seite zeigt: die Hauptabfrage (Rubrik, Suche, Archiv, der Artikel selbst) und die Auswahl der
 * Startseite. Mit $ids werden weitere vermerkt.
 *
 * @param int[] $ids Beiträge.
 */
function tamil_seite_beitraege( array $ids = array() ): array {
	static $liste = null;
	if ( null === $liste ) {
		$liste = array();
		if ( isset( $GLOBALS['wp_query'] ) && is_array( $GLOBALS['wp_query']->posts ) ) {
			foreach ( $GLOBALS['wp_query']->posts as $p ) {
				$liste[ (int) ( is_object( $p ) ? $p->ID : $p ) ] = true;
			}
		}
	}
	foreach ( $ids as $id ) {
		$liste[ (int) $id ] = true;
	}
	return $liste;
}

/**
 * Zeigt diese Seite den Beitrag?
 */
function tamil_auf_seite( int $post_id ): bool {
	return isset( tamil_seite_beitraege()[ $post_id ] );
}

/**
 * Darf ein Beitrag diesen Anhang als Kartenbild zeigen? Ja, wenn ihn auf dieser Seite noch kein anderer Beitrag gezeigt
 * hat; der erste Beitrag wird gemerkt. Die Seite wird immer in derselben Reihenfolge gebaut, die Wahl ist also bei
 * gleichem Inhalt gleich (kein Flackern zwischen Aufrufen oder im Seiten-Cache).
 */
function tamil_anhang_frei( int $anhang, int $post_id ): bool {
	static $gezeigt = array();
	if ( $anhang <= 0 ) {
		return true;
	}
	if ( ! isset( $gezeigt[ $anhang ] ) ) {
		$gezeigt[ $anhang ] = $post_id;
	}
	return $gezeigt[ $anhang ] === $post_id;
}

/**
 * Ein Bild aus dem Rubrik-Pool als <img> (Rubrikkacheln ohne Beitrag mit Foto, Leerzustände), reihum auf der Seite;
 * merkt den Nachweis. Das Signet nur, wenn das Bild für einen Beitrag steht (Zeilen der Kinotabelle).
 *
 * @param array<string,mixed> $opt { @type int $n bevorzugte Nummer im Pool, @type bool $schild, @type bool $sofort, @type bool $alt, @type string $sizes, @type bool $signet (Standard nein). }
 */
function tamil_pool_img( string $slug, array $opt = array() ): string {
	$p = tamil_pool_seite( $slug, (int) ( $opt['n'] ?? 0 ) );
	tamil_nachweise( tamil_pool_nachweis( $p ) );
	$img = tamil_pool_tag(
		$p,
		array(
			/* translators: %s: Bildbeschreibung */
			'alt'     => ( $opt['alt'] ?? true ) ? sprintf( __( 'Symbolbild: %s', 'tamil' ), $p['alt'] ) : '',
			'loading' => ! empty( $opt['sofort'] ) ? 'eager' : 'lazy',
			'sizes'   => (string) ( $opt['sizes'] ?? '' ),
		)
	);
	if ( $opt['schild'] ?? true ) {
		$img .= tamil_symbolbild_schild();
	}
	if ( ! empty( $opt['signet'] ) ) {
		$img .= tamil_signatur_ecke_html( tamil_signatur_ecke_ton_pool( (string) $p['datei'] ) );
	}
	return $img;
}
