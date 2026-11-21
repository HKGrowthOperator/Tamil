<?php
/**
 * Eingriffe in Inhalt und Ausgabe: Werbeplatz im Artikel, Textauszug, Body-Klassen, Suche nur in Beiträgen.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Werbeplatz 03 nach dem zweiten Absatz – nur im Hauptinhalt eines langen Beitrags und nur, wenn die Redaktion den
 * Platz nicht selbst per [tamil_anzeige] gesetzt hat. Ob der Beitrag lang genug ist (ab fünf Absätzen), entscheidet
 * das Plugin (tamil_site_artikel_plaetze(), N-06); dann liefert tamil_site_anzeige() hier nichts.
 */
function tamil_inarticle_anzeige( string $content ): string {
	if ( ! is_singular( 'post' ) || ! in_the_loop() || ! is_main_query() || ! function_exists( 'tamil_site_anzeige' ) ) {
		return $content;
	}
	if ( str_contains( $content, 'class="ad ' ) || substr_count( $content, '</p>' ) < 3 ) {
		return $content;
	}
	$anzeige = tamil_site_anzeige( 'inarticle', false );
	if ( '' === $anzeige ) {
		return $content;
	}
	$pos = 0;
	for ( $i = 0; $i < 2; $i++ ) {
		$pos = strpos( $content, '</p>', $pos );
		if ( false === $pos ) {
			return $content;
		}
		$pos += 4;
	}
	return substr( $content, 0, $pos ) . "\n" . $anzeige . "\n" . substr( $content, $pos );
}
add_filter( 'the_content', 'tamil_inarticle_anzeige', 20 );

function tamil_excerpt_length(): int {
	return 28;
}
add_filter( 'excerpt_length', 'tamil_excerpt_length' );

function tamil_excerpt_more(): string {
	return ' …';
}
add_filter( 'excerpt_more', 'tamil_excerpt_more' );

/**
 * Body-Klassen: Seitentyp für das CSS (page-start, page-artikel …).
 */
function tamil_body_class( array $classes ): array {
	if ( is_front_page() ) {
		$classes[] = 'page-start';
	} elseif ( is_singular( 'post' ) ) {
		$classes[] = 'page-artikel';
	} elseif ( is_category() ) {
		$classes[] = 'page-kategorie';
	}
	return $classes;
}
add_filter( 'body_class', 'tamil_body_class' );

/**
 * Die Suche zeigt Beiträge, keine Seiten oder Anhänge.
 */
function tamil_search_nur_beitraege( WP_Query $query ): void {
	if ( ! is_admin() && $query->is_main_query() && $query->is_search() ) {
		$query->set( 'post_type', 'post' );
	}
	if ( ! is_admin() && $query->is_main_query() && $query->is_category() ) {
		$query->set( 'posts_per_page', 12 );
	}
}
add_action( 'pre_get_posts', 'tamil_search_nur_beitraege' );

/**
 * Links mit target="_blank" im Inhalt bekommen rel="noopener", sofern sie kein rel haben.
 */
function tamil_links_noopener( string $content ): string {
	if ( ! str_contains( $content, 'target="_blank"' ) ) {
		return $content;
	}
	return (string) preg_replace( '/<a ((?:(?!rel=)[^>])*?)target="_blank"((?:(?!rel=)[^>])*)>/i', '<a $1target="_blank" rel="noopener"$2>', $content );
}
add_filter( 'the_content', 'tamil_links_noopener', 30 );

/**
 * YouTube-Kennung aus einer Video-Adresse (watch, embed, shorts, youtu.be); leer, wenn es keine ist.
 */
function tamil_youtube_id( string $url ): string {
	if ( preg_match( '~^https?://(?:www\.|m\.)?(?:youtube(?:-nocookie)?\.com/(?:watch\?(?:[^#\s]*&)?v=|embed/|shorts/)|youtu\.be/)([\w-]{6,20})~i', $url, $treffer ) ) {
		return $treffer[1];
	}
	return '';
}

/**
 * Die Box „Video laden“ für eine YouTube-Kennung. Sie enthält nur Zeilenelemente, damit wpautop sie nicht zerlegt.
 */
function tamil_youtube_box( string $id ): string {
	return sprintf(
		'<div class="video-embed" data-video="%1$s"><button type="button" class="video-load">%2$s</button><span class="video-hint">%3$s <a href="%4$s" rel="noopener">%5$s</a></span></div>',
		esc_attr( $id ),
		esc_html__( 'Video laden', 'tamil' ),
		esc_html__( 'Beim Laden werden Daten an YouTube übertragen.', 'tamil' ),
		esc_url( 'https://www.youtube.com/watch?v=' . $id ),
		esc_html__( 'Bei YouTube ansehen', 'tamil' )
	);
}

/**
 * YouTube erst nach Klick laden (DSGVO). Statt des eingebetteten Players erscheint die Box .video-embed mit Knopf;
 * assets/js/app.js lädt das Video dann von youtube-nocookie.com. Der Filter greift vor dem oEmbed-Abruf, beim Aufbau
 * der Seite geht also keine Anfrage an YouTube hinaus, und der feste iframe (läuft am Handy seitlich über) entfällt.
 *
 * @param string|null $result Vorab-Ergebnis anderer Filter.
 * @param string      $url    Adresse, die eingebettet werden soll.
 */
function tamil_youtube_nach_klick( $result, $url ) {
	$id = tamil_youtube_id( (string) $url );
	return '' === $id ? $result : tamil_youtube_box( $id );
}
add_filter( 'pre_oembed_result', 'tamil_youtube_nach_klick', 10, 2 );

/**
 * Dasselbe für schon zwischengespeicherte Einbettungen (Metadaten _oembed_*), die noch den festen Player enthalten.
 *
 * @param string|false $html Gespeichertes oder frisch geholtes Einbettungs-HTML.
 * @param string       $url  Adresse der Einbettung.
 */
function tamil_youtube_nach_klick_gespeichert( $html, $url ) {
	$id = tamil_youtube_id( (string) $url );
	return '' === $id ? $html : tamil_youtube_box( $id );
}
add_filter( 'embed_oembed_html', 'tamil_youtube_nach_klick_gespeichert', 10, 2 );

/**
 * Kino-Artikel: Die Spielortliste aus dem Radar (ul.kino-liste mit Überschrift davor) ersetzt das Theme durch die
 * Tabelle „Spielorte und Termine“ aus kino_fakten, wie in der Rubrik Kino. Der gespeicherte Inhalt bleibt unverändert.
 */
function tamil_kino_liste_ersetzen( string $content ): string {
	if ( ! is_singular( 'post' ) || ! in_the_loop() || ! str_contains( $content, 'class="kino-liste"' ) ) {
		return $content;
	}
	$film = tamil_kino_film( (int) get_the_ID() );
	if ( ! $film ) {
		return $content;
	}
	ob_start();
	echo '<section class="kino-orte" aria-labelledby="spielorte-titel"><h2 id="spielorte-titel">' . esc_html__( 'Spielorte und Termine', 'tamil' ) . '</h2>';
	if ( '' !== $film['stand'] ) {
		echo '<p class="kino-orte__stand">' . esc_html( $film['stand'] ) . '</p>';
	}
	tamil_kino_orte_tafel( array( $film ) );
	echo '<p class="kino-orte__notiz">' . esc_html__( 'Aus den Programmen der Kinos, Angaben ohne Gewähr.', 'tamil' ) . '</p></section>';
	$tafel = (string) ob_get_clean();
	$neu   = preg_replace( '#(?:<h[23][^>]*>[^<]*</h[23]>\s*)?<ul class="kino-liste">.*?</ul>#s', $tafel, $content, 1 );
	return is_string( $neu ) ? $neu : $content;
}
add_filter( 'the_content', 'tamil_kino_liste_ersetzen', 15 );

/**
 * Reste der alten Seite im Text nicht anzeigen: das Teilen-Feld des alten WhatsApp-Plugins („Share on: WhatsApp“, steht
 * über der neuen Teilen-Leiste und verlinkt auf www.tamil.de) und Bilder unter www.tamil.de/wp-content/uploads/ (auf
 * die eigenen Uploads umgeschrieben oder, ohne lokale Datei, weggelassen). Der gespeicherte Inhalt bleibt unverändert.
 */
function tamil_inhalt_altreste( string $content ): string {
	return tamil_alte_uploads( tamil_altreste_entfernen( $content ) );
}
add_filter( 'the_content', 'tamil_inhalt_altreste', 1 );

/**
 * Infokasten aus dem Import (<div class="event-box"> mit „Wann:“, „Wo:“ und Ticket-Link) wie der Terminkasten des
 * Themes ausgeben (N-11): Überschrift „Termin“, Angaben als Liste, Datum im Hausformat („Do, 5. November 2026“), Links
 * als Textlinks. Was nicht dem Muster folgt, bleibt unverändert. Der gespeicherte Inhalt bleibt unverändert.
 */
function tamil_event_box_wie_termin( string $content ): string {
	if ( ! str_contains( $content, 'event-box' ) ) {
		return $content;
	}
	return (string) preg_replace_callback(
		'#<div class="(?:[^"]* )?event-box(?: [^"]*)?">(.*?)</div>#s', // Import und Muster „Termin-Kasten (im Text)“
		static function ( array $m ): string {
			preg_match_all( '#<p\b[^>]*>(.*?)</p>#s', $m[1], $absaetze );
			$angaben = '';
			$links   = '';
			foreach ( $absaetze[1] as $p ) {
				if ( preg_match( '#^\s*<strong>([^<:]+):</strong>\s*(.+)$#s', $p, $a ) ) {
					$wert = trim( $a[2] );
					if ( preg_match( '#^(\d{1,2})\.(\d{1,2})\.(\d{4})$#', wp_strip_all_tags( $wert ), $d ) ) {
						$wert = esc_html( tamil_termin_text( sprintf( '%04d-%02d-%02d', $d[3], $d[2], $d[1] ) ) );
					}
					$angaben .= '<div><dt>' . esc_html( trim( $a[1] ) ) . '</dt><dd>' . $wert . '</dd></div>';
				} elseif ( preg_match( '#^\s*(<a\s[^>]*>[^<]*</a>\s*)+$#', $p ) ) {
					$links .= str_replace( '<a ', '<a class="textlink" ', trim( $p ) ) . ' ';
				} else {
					return $m[0];
				}
			}
			if ( '' === $angaben ) {
				return $m[0];
			}
			return '<section class="termin-box termin-box--im-text" aria-labelledby="termin-titel"><h2 class="termin-box__titel" id="termin-titel">'
				. esc_html__( 'Termin', 'tamil' ) . '</h2><dl class="angaben">' . $angaben . '</dl>'
				. ( '' !== $links ? '<p class="aktionen">' . trim( $links ) . '</p>' : '' )
				. '<p class="termin-box__hinweis">' . esc_html__( 'Angaben ohne Gewähr, bitte beim Veranstalter prüfen.', 'tamil' ) . '</p></section>';
		},
		$content
	);
}
add_filter( 'the_content', 'tamil_event_box_wie_termin', 16 );

/**
 * Tamilische Wörter im Beitragstext mit lang="ta" auszeichnen (Altbestand hat Namen und Zitate auf Tamil).
 */
function tamil_inhalt_lang_ta( string $content ): string {
	return tamil_lang_ta( $content );
}
add_filter( 'the_content', 'tamil_inhalt_lang_ta', 40 );

/**
 * Quellenzeile im Text mit gleich benannten Links („Quelle: Eventfrog CH, Eventfrog CH“, zwei Seiten derselben Quelle):
 * ab dem zweiten gleichen Namen eine Zahl anhängen („Eventfrog CH (2)“), damit Lesende und Vorleser die Links
 * unterscheiden können (QA-08). Andere Inhalte bleiben unverändert.
 *
 * @param string $content Inhalt des Beitrags.
 */
function tamil_quelle_gleiche_namen( string $content ): string {
	if ( ! str_contains( $content, 'class="quelle"' ) ) {
		return $content;
	}
	$neu = preg_replace_callback(
		'#(<p class="quelle">)(.*?)(</p>)#s',
		static function ( array $m ): string {
			$zahl  = array();
			$innen = preg_replace_callback(
				'#(<a\b[^>]*>)([^<]+)(</a>)#',
				static function ( array $a ) use ( &$zahl ): string {
					$name          = trim( $a[2] );
					$zahl[ $name ] = ( $zahl[ $name ] ?? 0 ) + 1;
					return $zahl[ $name ] > 1 ? $a[1] . $a[2] . ' (' . $zahl[ $name ] . ')' . $a[3] : $a[0];
				},
				$m[2]
			);
			return $m[1] . ( is_string( $innen ) ? $innen : $m[2] ) . $m[3];
		},
		$content
	);
	return is_string( $neu ) ? $neu : $content;
}
add_filter( 'the_content', 'tamil_quelle_gleiche_namen', 35 );
