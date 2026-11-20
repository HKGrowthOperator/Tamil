<?php
/**
 * Signet „Tamil Dots 04A“ als Hintergrund (Freigabe der Form durch Luis am 19.11.2026, docs/abnahme/2026-11-19-signature.md).
 *
 * Das Signet ist nicht das Logo: Es steht nie am, im oder hinter dem Logo und nie hinter Überschriften, Text oder
 * Gesichtern. Es ist immer dekorativ (aria-hidden, ohne Text, nicht fokussierbar) und sitzt in freier Fläche,
 * angeschnitten von der Kante seines Bereichs. Die Dateien liegen in assets/img/signatur/ (gebaut mit bauen.py aus der
 * freigegebenen Form, nur Titan, Impact und Weiß mit Deckkraft); die Regeln stehen in DESIGN.md, Abschnitt „Signet“.
 *
 * Varianten:
 * - flaeche  Titan-Flächen („Diese Woche“, Kino „Im Programm“, Termine „Ab heute“): ganze Kuppel in Impact auf Titan,
 *            inline, damit „Punkte bauen die Form auf“ beim Hineinscrollen laufen kann (assets/js/app.js).
 * - band     Rubrikband und Zeile mit Rechtlichem: Streifen der Kuppel als CSS-Hintergrund (ab 1024 px, nur bei freiem Platz).
 * - kopf     Seitenköpfe: kleine, leise Kuppel auf Weiß als CSS-Hintergrund.
 * - raum     Sonderstellen (404, Production „Live mit dir!“): 03 Spatial als CSS-Hintergrund.
 *
 * Dazu seit Theme 3.6.0 das Signet „an jedem Post“ (Luis, 19.11.2026: „klein und dezent, aber auf jeden einzelnen
 * Post“): ein kleiner Bogen unten rechts im Bild jedes Beitrags, von der Bildkante angeschnitten. tamil_bild()
 * (inc/bildkette.php) hängt ihn an jedes Beitragsbild, das in einem Rahmen steht; dazu das Bild des Artikels und, wenn
 * der Artikel sein Bild nur im Text hat, dieses Bild (tamil_signatur_ecke_im_text()). Nicht an Rubrikkacheln
 * (Navigation), Leerzuständen, Seiten, Verzeichniseinträgen, Anzeigen und nie am Logo. Weiß auf dunklen und mittleren
 * Bildecken, Titan und Impact auf hellen (tamil_signatur_ecke_ton()).
 */

defined( 'ABSPATH' ) || exit;

/**
 * Varianten: Datei (nur inline) und ob die Variante inline steht.
 *
 * @return array<string, array{inline: bool, datei?: string}>
 */
function tamil_signatur_varianten(): array {
	return array(
		'flaeche' => array(
			'inline' => true,
			'datei'  => 'flaeche.svg',
		),
		'band'    => array( 'inline' => false ),
		'kopf'    => array( 'inline' => false ),
		'raum'    => array( 'inline' => false ),
	);
}

/**
 * Inline-SVG einer Variante (einmal je Anfrage gelesen). Nur eigene Dateien des Themes.
 *
 * @param string $datei Dateiname in assets/img/signatur/.
 */
function tamil_signatur_svg( string $datei ): string {
	static $cache = array();
	if ( ! isset( $cache[ $datei ] ) ) {
		$pfad            = TAMIL_THEME_DIR . '/assets/img/signatur/' . basename( $datei );
		$cache[ $datei ] = is_readable( $pfad ) ? (string) file_get_contents( $pfad ) : ''; // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents -- eigene Datei des Themes
	}
	return $cache[ $datei ];
}

/**
 * Markup des Signets. Dekorativ: aria-hidden, ohne Text; inline zusätzlich focusable="false" (steht in der Datei).
 *
 * @param string $variante flaeche | band | kopf | raum.
 * @param array  $args     { @type string $klasse zusätzliche Klassen. }
 */
function tamil_signatur_html( string $variante, array $args = array() ): string {
	$varianten = tamil_signatur_varianten();
	if ( ! isset( $varianten[ $variante ] ) ) {
		return '';
	}
	$klassen = trim( 'signatur signatur--' . $variante . ' ' . (string) ( $args['klasse'] ?? '' ) );
	$innen   = '';
	if ( $varianten[ $variante ]['inline'] ) {
		$innen = tamil_signatur_svg( $varianten[ $variante ]['datei'] ?? '' );
		if ( '' === $innen ) {
			return '';
		}
	}
	return '<span class="' . esc_attr( $klassen ) . '" aria-hidden="true">' . $innen . '</span>';
}

/**
 * Signet ausgeben (siehe tamil_signatur_html()).
 *
 * @param string $variante flaeche | band | kopf | raum.
 * @param array  $args     { @type string $klasse zusätzliche Klassen. }
 */
function tamil_signatur( string $variante, array $args = array() ): void {
	echo tamil_signatur_html( $variante, $args ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Klassen escapt, SVG aus eigener Datei des Themes
}

/**
 * Seiten (page.php) mit Signet im Kopf: die Dienstseiten Werben, Verzeichnis und Einreichen. Rechtstexte und reine
 * Textseiten bleiben ohne. Erweiterbar über den Filter „tamil_signatur_seiten“ (Liste von Seiten-Slugs).
 *
 * @param int $id Seite.
 */
function tamil_signatur_im_seitenkopf( int $id ): bool {
	$seiten = (array) apply_filters( 'tamil_signatur_seiten', array( 'werben', 'verzeichnis', 'einreichen' ) );
	return in_array( (string) get_post_field( 'post_name', $id ), $seiten, true );
}

/**
 * Signet in der Bildecke: dekorative, leere Spanne; Bild und Größe kommen aus dem CSS (Abschnitt „Signet an jedem
 * Post“), damit die Datei einmal geladen und zwischengespeichert wird.
 *
 * @param string $ton „hell“ für eine helle Bildecke (Punkte in Titan und Impact), sonst weiße Punkte.
 */
function tamil_signatur_ecke_html( string $ton = 'dunkel' ): string {
	return '<span class="signatur-ecke' . ( 'hell' === $ton ? ' signatur-ecke--rot' : '' ) . '" aria-hidden="true"></span>';
}

/**
 * Ist die Ecke unten rechts einer Bilddatei hell? Mittlere relative Helligkeit (WCAG, linear) in einem Raster von
 * 8 × 6 Punkten im Bereich rechts 18 % und unten 26 %, dort, wo das Signet sitzt. Über 0,3 steht Rot besser als Weiß
 * (gleicher Kontrast beider Fassungen bei etwa 0,34).
 *
 * @return bool|null null, wenn die Datei nicht gelesen werden kann.
 */
function tamil_signatur_ecke_datei_hell( string $pfad ): ?bool {
	if ( ! function_exists( 'imagecreatefromstring' ) || ! is_readable( $pfad ) ) {
		return null;
	}
	$roh = file_get_contents( $pfad ); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents -- lokale Datei (Mediathek oder Theme)
	$im  = false === $roh ? false : @imagecreatefromstring( $roh ); // phpcs:ignore WordPress.PHP.NoSilencedErrors.Discouraged -- defekte Dateien melden sich mit einer Warnung; hier gilt dann „unbekannt“
	if ( ! $im ) {
		return null;
	}
	if ( ! imageistruecolor( $im ) ) {
		imagepalettetotruecolor( $im );
	}
	$w     = imagesx( $im );
	$h     = imagesy( $im );
	$summe = 0.0;
	$n     = 0;
	$lin   = static fn( int $c ): float => ( $c / 255 ) <= 0.04045 ? ( $c / 255 ) / 12.92 : ( ( ( $c / 255 ) + 0.055 ) / 1.055 ) ** 2.4;
	for ( $i = 0; $i < 8; $i++ ) {
		for ( $j = 0; $j < 6; $j++ ) {
			$x      = (int) min( $w - 1, round( $w * ( 0.82 + 0.17 * $i / 7 ) ) );
			$y      = (int) min( $h - 1, round( $h * ( 0.72 + 0.26 * $j / 5 ) ) );
			$rgb    = imagecolorat( $im, $x, $y );
			$summe += 0.2126 * $lin( ( $rgb >> 16 ) & 0xFF ) + 0.7152 * $lin( ( $rgb >> 8 ) & 0xFF ) + 0.0722 * $lin( $rgb & 0xFF );
			++$n;
		}
	}
	return $summe / $n > 0.3;
}

/**
 * Ton der Bildecke eines Anhangs (einmal gerechnet, gemerkt im Meta „_tamil_signet_ecke“). Gemessen wird die kleinste
 * ungeschnittene Fassung („medium“), sonst das Original.
 *
 * @return string „hell“ oder „dunkel“.
 */
function tamil_signatur_ecke_ton( int $attachment_id ): string {
	$gemerkt = (string) get_post_meta( $attachment_id, '_tamil_signet_ecke', true );
	if ( 'hell' === $gemerkt || 'dunkel' === $gemerkt ) {
		return $gemerkt;
	}
	$pfad  = (string) get_attached_file( $attachment_id );
	$klein = image_get_intermediate_size( $attachment_id, 'medium' );
	if ( is_array( $klein ) && ! empty( $klein['path'] ) ) {
		$pfad = trailingslashit( wp_get_upload_dir()['basedir'] ) . $klein['path'];
	}
	$hell = tamil_signatur_ecke_datei_hell( $pfad );
	if ( null === $hell ) {
		return 'dunkel';
	}
	$ton = $hell ? 'hell' : 'dunkel';
	update_post_meta( $attachment_id, '_tamil_signet_ecke', $ton );
	return $ton;
}

/**
 * Neue Bildgrößen (Bild ersetzt oder neu berechnet): den gemerkten Ton der Ecke verwerfen.
 *
 * @param array $daten         Metadaten des Anhangs.
 * @param int   $attachment_id Anhang.
 * @return array
 */
function tamil_signatur_ecke_vergessen( $daten, $attachment_id ) {
	delete_post_meta( (int) $attachment_id, '_tamil_signet_ecke' );
	return $daten;
}
add_filter( 'wp_update_attachment_metadata', 'tamil_signatur_ecke_vergessen', 10, 2 );

/**
 * Ton der Bildecke eines Pool-Bilds (Theme-Datei, kleine Fassung); gemerkt in einer Transiente je Datei und Stand.
 *
 * @param string $datei Dateiname in assets/img/rubrik/.
 * @return string „hell“ oder „dunkel“.
 */
function tamil_signatur_ecke_ton_pool( string $datei ): string {
	$pfad = TAMIL_THEME_DIR . '/assets/img/rubrik/' . str_replace( '.webp', '-320.webp', basename( $datei ) );
	if ( ! is_readable( $pfad ) ) {
		$pfad = TAMIL_THEME_DIR . '/assets/img/rubrik/' . basename( $datei );
	}
	$alle     = get_transient( 'tamil_signet_ecke_pool' );
	$alle     = is_array( $alle ) ? $alle : array();
	$schluess = basename( $pfad ) . ':' . ( is_readable( $pfad ) ? (int) filemtime( $pfad ) : 0 );
	if ( isset( $alle[ $schluess ] ) ) {
		return (string) $alle[ $schluess ];
	}
	$hell = tamil_signatur_ecke_datei_hell( $pfad );
	if ( null === $hell ) {
		return 'dunkel';
	}
	$alle[ $schluess ] = $hell ? 'hell' : 'dunkel';
	set_transient( 'tamil_signet_ecke_pool', $alle );
	return $alle[ $schluess ];
}

/**
 * Artikel, deren Bild nur im Text steht (Bildkette Stufe b, im Kopf kein Bild): das Signet an dieses Bild im Text.
 * Das Bild bekommt eine Hülle (span.bild-ecke), an deren Ecke das Signet sitzt; sonst bleibt der Text unverändert.
 *
 * @param string $content Inhalt des Beitrags.
 */
function tamil_signatur_ecke_im_text( string $content ): string {
	if ( ! is_singular( 'post' ) || ! in_the_loop() || ! is_main_query() || ! str_contains( $content, '<img' ) ) {
		return $content;
	}
	$wahl = tamil_bildwahl( (int) get_the_ID() );
	if ( 'inhalt' !== $wahl['art'] ) {
		return $content;
	}
	$fertig = false;
	$neu    = preg_replace_callback(
		'/<img\b[^>]*>/i',
		static function ( array $m ) use ( $wahl, &$fertig ): string {
			if ( $fertig || ! preg_match( '/\ssrc\s*=\s*(["\'])([^"\']+)\1/i', $m[0], $src ) || tamil_anhang_aus_url( html_entity_decode( $src[2], ENT_QUOTES ) ) !== (int) $wahl['id'] ) {
				return $m[0];
			}
			$fertig = true;
			return '<span class="bild-ecke">' . $m[0] . tamil_signatur_ecke_html( tamil_signatur_ecke_ton( (int) $wahl['id'] ) ) . '</span>';
		},
		$content
	);
	return is_string( $neu ) ? $neu : $content;
}
add_filter( 'the_content', 'tamil_signatur_ecke_im_text', 12 );
