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
