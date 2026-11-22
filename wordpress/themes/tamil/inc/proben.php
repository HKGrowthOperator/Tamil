<?php
/**
 * Startseiten-Proben (Theme 3.16.0, Masterplan von Luis vom 21.11.2026, TML-W06): drei Entwürfe für den ersten
 * Bildschirm der Startseite zum Vergleichen, dazu der Abschnitt „Tamil in meiner Stadt“. Bauvorgabe:
 * design/richtungen/klar2/proben-start/entwurf.md.
 *
 * Seit 3.17.0 gibt es eine vierte Probe „Ausgabe“ (/?probe=ausgabe) nach der Empfehlung der unabhängigen Kritik vom
 * 22.11.2026: großes Cover, direkt darunter „Tamil in meiner Stadt“ als Streifen (ersetzt dort „Diese Woche“),
 * gewichtete Beistücke, tamilische Rubriknamen. Aufbau: design/richtungen/klar2/proben-start/ausgabe.md.
 *
 * Aufruf: /?probe=cover, /?probe=news, /?probe=community, /?probe=ausgabe. Es gibt sie nur, wenn im Customizer „Tamil.de → Startseite →
 * Startseiten-Proben“ an ist (Standard aus). Ist der Schalter aus oder der Wert unbekannt, liefert tamil_probe() leer
 * und front-page.php gibt die normale Startseite aus. Probenseiten tragen noindex, sind nirgends verlinkt und werden
 * nicht zwischengespeichert.
 *
 * Die Proben nutzen dieselben acht Beiträge wie die Startseite (tamil_start_auswahl(): lead, neben, meldungen) und
 * haben keinen eigenen Zwischenspeicher; es kann also nichts zwischen Probe und normaler Seite verwechselt werden.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Die Proben: Schlüssel im Parameter „probe“ und Name im Umschalter.
 *
 * @return array<string,string>
 */
function tamil_proben(): array {
	return array(
		'cover'     => __( 'Cover First', 'tamil' ),
		'news'      => __( 'News First', 'tamil' ),
		'community' => __( 'Community First', 'tamil' ),
		'ausgabe'   => __( 'Ausgabe', 'tamil' ),
	);
}

/**
 * Welche Probe zeigt dieser Aufruf? Leer = normale Startseite (Schalter aus, andere Seite, unbekannter Wert).
 */
function tamil_probe(): string {
	if ( '1' !== tamil_opt( 'startseiten_proben' ) || ! is_front_page() || is_paged() ) {
		return '';
	}
	// Der Wert wird nur mit den festen Schlüsseln verglichen (genau, ohne Bereinigen: „cover'“ ist unbekannt) und
	// nie ausgegeben; der Rückgabewert ist der Schlüssel aus der eigenen Liste.
	// phpcs:ignore WordPress.Security.NonceVerification.Recommended, WordPress.Security.ValidatedSanitizedInput.InputNotSanitized -- nur Vergleich mit festen Werten
	$wert = isset( $_GET['probe'] ) && is_string( $_GET['probe'] ) ? wp_unslash( $_GET['probe'] ) : '';
	foreach ( array_keys( tamil_proben() ) as $schluessel ) {
		if ( $schluessel === $wert ) {
			return $schluessel;
		}
	}
	return '';
}

/**
 * Probenseiten bleiben aus dem Index (auch im Echtbetrieb).
 *
 * @param array<string,bool|string> $robots Robots-Angaben.
 * @return array<string,bool|string>
 */
function tamil_probe_robots( array $robots ): array {
	if ( '' === tamil_probe() ) {
		return $robots;
	}
	unset( $robots['index'], $robots['max-image-preview'] );
	$robots['noindex'] = true;
	return $robots;
}
add_filter( 'wp_robots', 'tamil_probe_robots', 30 );

/**
 * Probenseiten nicht zwischenspeichern (Plugin tamil-site, includes/leistung.php): Wer den Schalter umlegt oder die
 * Proben vergleicht, sieht sofort den aktuellen Stand.
 *
 * @param mixed $nie Bisheriger Stand.
 */
function tamil_probe_nie_zwischenspeichern( $nie ): bool {
	return (bool) $nie || '' !== tamil_probe();
}
add_filter( 'tamil_site_nie_zwischenspeichern', 'tamil_probe_nie_zwischenspeichern' );

/**
 * Body-Klasse der Probe (probe, probe-cover …).
 *
 * @param string[] $klassen Klassen.
 * @return string[]
 */
function tamil_probe_body_class( array $klassen ): array {
	$probe = tamil_probe();
	if ( '' !== $probe ) {
		$klassen[] = 'probe';
		$klassen[] = 'probe-' . $probe;
	}
	return $klassen;
}
add_filter( 'body_class', 'tamil_probe_body_class' );

/**
 * Der Wow-Aufmacher bleibt in Cover First, News First und Ausgabe aus (der erste Bildschirm bewegt sich dort nie von selbst).
 *
 * @param mixed $an Nach Einstellung und Foto.
 */
function tamil_probe_ohne_wow( $an ): bool {
	return (bool) $an && ! in_array( tamil_probe(), array( 'cover', 'news', 'ausgabe' ), true );
}
add_filter( 'tamil_wow_aufmacher', 'tamil_probe_ohne_wow' );

/**
 * Skript der Stadtwahl, nur auf Probenseiten (klein, ohne Abhängigkeiten, defer).
 */
function tamil_probe_skript(): void {
	if ( '' === tamil_probe() ) {
		return;
	}
	wp_enqueue_script(
		'tamil-stadt',
		TAMIL_THEME_URI . '/assets/js/stadt.js',
		array(),
		tamil_asset_version( 'assets/js/stadt.js' ),
		array(
			'strategy'  => 'defer',
			'in_footer' => true,
		)
	);
	if ( 'ausgabe' === tamil_probe() ) {
		// Pfeile und Balken der wischbaren Reihe im Stadtstreifen
		wp_enqueue_script(
			'tamil-streifen',
			TAMIL_THEME_URI . '/assets/js/streifen.js',
			array(),
			tamil_asset_version( 'assets/js/streifen.js' ),
			array(
				'strategy'  => 'defer',
				'in_footer' => true,
			)
		);
	}
}
add_action( 'wp_enqueue_scripts', 'tamil_probe_skript', 20 );

/**
 * Umschalter über dem Inhalt, nur auf Probenseiten: die Proben und die normale Startseite als Links.
 */
function tamil_probe_umschalter(): void {
	$probe = tamil_probe();
	if ( '' === $probe ) {
		return;
	}
	echo '<nav class="probe-wahl innen" aria-label="' . esc_attr__( 'Startseiten-Proben', 'tamil' ) . '"><span class="probe-wahl__titel">' . esc_html__( 'Probe:', 'tamil' ) . '</span><ul>';
	foreach ( tamil_proben() as $schluessel => $name ) {
		printf(
			'<li><a href="%1$s" rel="nofollow"%3$s>%2$s</a></li>',
			esc_url( add_query_arg( 'probe', $schluessel, home_url( '/' ) ) ),
			// am Handy kurz („Cover“), ab 600 px der volle Name („Cover First“)
			str_contains( $name, ' ' ) ? esc_html( strtok( $name, ' ' ) ) . '<span class="probe-wahl__lang"> ' . esc_html( substr( $name, strlen( strtok( $name, ' ' ) ) + 1 ) ) . '</span>' : esc_html( $name ),
			$schluessel === $probe ? ' aria-current="page"' : ''
		);
	}
	echo '<li><a href="' . esc_url( home_url( '/' ) ) . '">' . esc_html_x( 'normal', 'Umschalter der Proben: normale Startseite, kurz', 'tamil' ) . '<span class="probe-wahl__lang">' . esc_html_x( 'e Startseite', 'Umschalter der Proben: Rest von „normale Startseite“', 'tamil' ) . '</span></a></li></ul></nav>';
}

/**
 * Sortierung „neueste zuerst“ (bei gleicher Zeit die höhere ID zuerst, damit die Reihenfolge fest ist).
 */
function tamil_probe_neuer_zuerst( int $x, int $y ): int {
	$nach_zeit = (int) get_post_timestamp( $y ) <=> (int) get_post_timestamp( $x );
	return 0 !== $nach_zeit ? $nach_zeit : $y <=> $x;
}

/**
 * Vorrat für den ersten Abschnitt der Proben: der Aufmacher und die sieben Beiträge, die tamil_start_auswahl() dafür
 * schon reserviert hat (neben + meldungen), neueste zuerst. So bleibt alles darunter frei von Dubletten.
 *
 * @return array{lead:int,p:int[]}
 */
function tamil_probe_vorrat(): array {
	$a = tamil_start_auswahl();
	$p = array_values( array_unique( array_map( 'intval', array_merge( (array) $a['neben'], (array) $a['meldungen'] ) ) ) );
	$p = array_values( array_diff( $p, array( (int) $a['lead'] ) ) );
	usort( $p, 'tamil_probe_neuer_zuerst' );
	return array(
		'lead' => (int) $a['lead'],
		'p'    => $p,
	);
}

/**
 * Gleichen sich zwei Beiträge so, dass sie nicht nebeneinander stehen sollen? Gleiche Rubrik und gleiches erstes Wort
 * im Titel („Deepavali 2026 …“ neben „Deepavali in …“).
 */
function tamil_probe_aehnlich( int $a, int $b ): bool {
	$wort = static function ( int $id ): string {
		$titel = mb_strtolower( html_entity_decode( wp_strip_all_tags( get_the_title( $id ) ), ENT_QUOTES, 'UTF-8' ) );
		return (string) ( preg_split( '/\s+/u', trim( (string) preg_replace( '/[^\p{L}\p{N}\s]+/u', ' ', $titel ) ) )[0] ?? '' );
	};
	$ka   = tamil_hauptkategorie( $a );
	$kb   = tamil_hauptkategorie( $b );
	return $ka && $kb && $ka->term_id === $kb->term_id && '' !== $wort( $a ) && $wort( $a ) === $wort( $b );
}

/**
 * Hat der Beitrag einen Termin (event_datum), der vorbei ist? Ohne Termin: nein.
 */
function tamil_probe_termin_vorbei( int $post_id ): bool {
	$e = function_exists( 'tamil_site_event' ) ? (array) tamil_site_event( $post_id ) : array();
	return ! empty( $e['datum'] ) && tamil_termin_vorbei( (string) $e['datum'], (string) ( $e['ende'] ?? '' ) );
}

/**
 * Cover First: wer aufs Cover kommt, wer die drei Beistücke bekommt und was in die Reihe darunter rückt.
 *
 * - Cover = Aufmacher der Startseite. Hat er nur ein Symbolbild aus dem Pool und gibt es im Vorrat einen Beitrag mit
 *   eigenem Foto, rückt dieser aufs Cover (große Flächen gehen an eigene Fotos).
 * - B1 und B2: zuerst Beiträge mit Foto, dann mit eigenem Bild, dann der Reihe nach. B3 (8:3): bevorzugt ein breites
 *   Bild oder ein Symbolbild, weil das flache Format das am besten verträgt.
 * - Zwei Beiträge mit gleicher Rubrik und gleichem ersten Titelwort stehen nicht nebeneinander: der zweite rückt in
 *   die Reihe darunter.
 *
 * Nur für die Probe „Ausgabe“ ($ohne_vergangen, Theme 3.17.1): Ein Beitrag, dessen Termin vorbei ist, wird nicht das
 * Cover. An seine Stelle rückt aus dem Vorrat der erste Beitrag mit eigenem Foto und ohne vergangenen Termin, sonst
 * der neueste ohne vergangenen Termin; der verdrängte Beitrag wird ein Beistück. Gibt es keinen solchen Beitrag,
 * bleibt das Cover. Cover First und die normale Startseite kennen diese Regel nicht.
 *
 * @return array{cover:int,bei:int[],rest:int[]}
 */
function tamil_probe_cover_auswahl( bool $ohne_vergangen = false ): array {
	$v       = tamil_probe_vorrat();
	$cover   = $v['lead'];
	$p       = $v['p'];
	$vorbei  = 0;
	$kommend = $ohne_vergangen ? array_values( array_filter( $p, static fn( int $id ): bool => ! tamil_probe_termin_vorbei( $id ) ) ) : array();
	if ( $cover && $kommend && tamil_probe_termin_vorbei( $cover ) ) {
		$neu = $kommend[0];
		foreach ( $kommend as $id ) {
			if ( tamil_ist_foto( $id ) ) {
				$neu = $id;
				break;
			}
		}
		$vorbei = $cover;
		$p      = array_values( array_diff( $p, array( $neu ) ) );
		$p[]    = $cover;
		$cover  = $neu;
		usort( $p, 'tamil_probe_neuer_zuerst' );
	}
	if ( $cover && 'pool' === tamil_bildwahl( $cover )['art'] ) {
		$foto = tamil_leitbild( $ohne_vergangen ? array_values( array_diff( array_intersect( $p, $kommend ), array( $cover ) ) ) : $p );
		if ( $foto ) {
			$p     = array_values( array_diff( $p, array( $foto ) ) );
			$p[]   = $cover;
			$cover = $foto;
			usort( $p, 'tamil_probe_neuer_zuerst' );
		}
	}
	$rang_foto  = static function ( int $id ): int {
		if ( tamil_ist_foto( $id ) ) {
			return 0;
		}
		$w = tamil_bildwahl( $id );
		return in_array( $w['art'], array( 'eigen', 'inhalt' ), true ) && ! $w['breit'] && ! $w['symbol'] ? 1 : 2;
	};
	$rang_flach = static function ( int $id ): int {
		$w = tamil_bildwahl( $id );
		return $w['breit'] || $w['symbol'] ? 0 : 1;
	};
	$bei        = array();
	foreach ( array( $rang_foto, $rang_foto, $rang_flach ) as $rang ) {
		$offen = array_values( array_diff( $p, $bei ) );
		if ( ! $offen ) {
			break;
		}
		// ähnliche Beiträge (zu Cover oder schon gewählten Beistücken) nur, wenn sonst nichts bleibt
		$frei = array_values(
			array_filter(
				$offen,
				static function ( int $id ) use ( $cover, $bei ): bool {
					foreach ( array_merge( array( $cover ), $bei ) as $da ) {
						if ( tamil_probe_aehnlich( $id, $da ) ) {
							return false;
						}
					}
					return true;
				}
			)
		);
		$wahl = $frei ? $frei : $offen;
		$best = $wahl[0];
		foreach ( $wahl as $id ) {
			if ( $rang( $id ) < $rang( $best ) ) {
				$best = $id;
			}
		}
		$bei[] = $best;
	}
	// der vom Cover verdrängte Beitrag bleibt oben: Er nimmt den letzten Platz der Beistücke, wenn er keinen bekam
	if ( $vorbei && $bei && ! in_array( $vorbei, $bei, true ) ) {
		$bei[ count( $bei ) - 1 ] = $vorbei;
	}
	return array(
		'cover' => (int) $cover,
		'bei'   => $bei,
		'rest'  => array_slice( array_values( array_diff( $p, $bei ) ), 0, 4 ),
	);
}

/**
 * Ausgabe: das Cover, ein großes Beistück mit zwei kleineren und „Weitere Meldungen“ mit einer großen Karte und drei
 * flachen. Vorrat und Regeln wie Cover First (tamil_probe_cover_auswahl()), dazu: kein vergangener Termin als Cover.
 * Aus den vier übrigen Beiträgen wird der erste mit eigenem Foto die große Karte, sonst der neueste.
 *
 * @return array{cover:int,gross:int,klein:int[],haupt:int,flach:int[]}
 */
function tamil_probe_ausgabe_auswahl(): array {
	$w     = tamil_probe_cover_auswahl( true );
	$rest  = array_values( $w['rest'] );
	$haupt = (int) ( $rest[0] ?? 0 );
	foreach ( $rest as $id ) {
		if ( tamil_ist_foto( $id ) ) {
			$haupt = (int) $id;
			break;
		}
	}
	return array(
		'cover' => (int) $w['cover'],
		'gross' => (int) ( $w['bei'][0] ?? 0 ),
		'klein' => array_values( array_slice( $w['bei'], 1 ) ),
		'haupt' => $haupt,
		'flach' => array_values( array_diff( $rest, array( $haupt ) ) ),
	);
}

/**
 * „sizes“ für das Titelbild der Ausgabe. Am Handy ist die Bildfläche höher als breit (bis 125 % der Fensterbreite,
 * siehe .aufmacher--ausgabe .rahmen); das Bild füllt sie in der Höhe und ist dann breiter als das Fenster. Die
 * Angabe nennt diese wirkliche Breite (Höhe mal Seitenverhältnis), damit der Browser bei doppelter Pixeldichte die
 * größte passende Fassung lädt und nicht eine für 100vw. Ohne bekannte Maße (Symbolbild aus dem Pool) gilt 16:9.
 */
function tamil_probe_cover_sizes( int $post_id ): string {
	$w    = tamil_bildwahl( $post_id );
	$meta = ! empty( $w['id'] ) ? wp_get_attachment_metadata( (int) $w['id'] ) : array();
	$form = is_array( $meta ) && ! empty( $meta['width'] ) && ! empty( $meta['height'] ) ? (int) $meta['width'] / (int) $meta['height'] : 16 / 9;
	$vw   = (int) min( 300, max( 100, ceil( 125 * $form ) ) );
	return sprintf( '(min-width: 1280px) 1200px, (min-width: 600px) calc(100vw - 48px), %dvw', $vw );
}

/**
 * Tamilischer Name der Rubrik eines Beitrags neben dem deutschen (Ausgabe, am Kontextfeld der Titelgeschichte). Nur
 * der gepflegte Name aus tamil_rubrik() (inc/rubriken.php oder Feld „tamil“ der Kategorie); ohne ihn leer. Es wird
 * nichts übersetzt.
 *
 * @return string Escaptes HTML, leer ohne tamilischen Namen.
 */
function tamil_rubrik_zweisprachig( int $post_id ): string {
	$kat = tamil_hauptkategorie( $post_id );
	if ( ! $kat ) {
		return '';
	}
	$ta = trim( (string) tamil_rubrik( $kat->slug )['tamil'] );
	if ( '' === $ta || ! preg_match( '/[\x{0B80}-\x{0BFF}]/u', $ta ) ) {
		return '';
	}
	return '<p class="rubrik-ta"><span class="rubrik-ta__ta" lang="ta">' . esc_html( $ta ) . '</span> <span class="rubrik-ta__de">' . esc_html( $kat->name ) . '</span></p>';
}

/**
 * Hat der Titel ein Wort ab 16 Zeichen? Das Cover der Ausgabe setzt ihn dann am Handy eine Stufe kleiner, damit kein
 * Wort bricht.
 */
function tamil_titel_langes_wort( int $post_id ): bool {
	$titel = html_entity_decode( wp_strip_all_tags( get_the_title( $post_id ) ), ENT_QUOTES, 'UTF-8' );
	foreach ( (array) preg_split( '/[\s\-–]+/u', $titel ) as $wort ) {
		if ( mb_strlen( (string) $wort ) >= 16 ) {
			return true;
		}
	}
	return false;
}

/**
 * Format des Covers ab 1024 px: Original mindestens 1,6 : 1 → 16:10, sonst 3:2; Titel über 90 Zeichen → immer 3:2
 * (mehr Höhe für den Titel). Am Handy ist das Cover immer 4:3, am Tablet 16:10 (CSS).
 */
function tamil_probe_coverformat( int $post_id ): string {
	$w      = tamil_bildwahl( $post_id );
	$meta   = $w['id'] ? wp_get_attachment_metadata( (int) $w['id'] ) : array();
	$breite = (int) ( $meta['width'] ?? 0 );
	$hoehe  = (int) ( $meta['height'] ?? 0 );
	$lang   = mb_strlen( html_entity_decode( get_the_title( $post_id ), ENT_QUOTES, 'UTF-8' ) ) > 90;
	return ! $lang && $hoehe > 0 && $breite / $hoehe >= 1.6 ? 'r1610' : 'r32';
}

/**
 * Zeit eines Beitrags für die Zeitfolge, ohne erfundene Genauigkeit: heute und gestern mit Uhrzeit, älter nur das
 * Datum (importierte und von Hand datierte Beiträge tragen oft 12:00 Uhr).
 */
function tamil_zeit_text( int $ts ): string {
	$tag     = wp_date( 'Y-m-d', $ts );
	$heute   = current_time( 'Y-m-d' );
	$gestern = ( new DateTimeImmutable( $heute . ' 12:00:00', wp_timezone() ) )->modify( '-1 day' )->format( 'Y-m-d' );
	if ( $tag === $heute ) {
		/* translators: %s: Uhrzeit */
		return sprintf( __( 'Heute, %s Uhr', 'tamil' ), wp_date( 'H:i', $ts ) );
	}
	if ( $tag === $gestern ) {
		/* translators: %s: Uhrzeit */
		return sprintf( __( 'Gestern, %s Uhr', 'tamil' ), wp_date( 'H:i', $ts ) );
	}
	return (string) wp_date( 'j. F Y', $ts );
}

/**
 * Ein Satz zu einem Beitrag (erster Satz des Vorspanns; über 150 Zeichen an der Wortgrenze gekürzt wie bei den Karten).
 */
function tamil_probe_satz( int $post_id ): string {
	$satz = tamil_saetze( tamil_standfirst( $post_id ), 1 );
	return mb_strlen( $satz ) > 150 ? wp_trim_words( $satz, 20, ' …' ) : $satz;
}

/**
 * Ist ein Termin vorbei? Maßgeblich ist sein letzter Tag (das Ende, wenn es nach dem Beginn liegt, sonst der Beginn):
 * vor heute = vorbei; ein Termin von heute gilt den ganzen Tag als kommend (wie tamil_site_upcoming_events()).
 */
function tamil_termin_vorbei( string $datum, string $ende = '' ): bool {
	$tag = max( substr( $datum, 0, 10 ), substr( $ende, 0, 10 ) );
	return (bool) preg_match( '/^\d{4}-\d{2}-\d{2}$/', $tag ) && $tag < current_time( 'Y-m-d' );
}

/**
 * Text neben oder unter einer Bildkarte (im selben Link, Option „zusatz“ von tamil_anr_imbild()): Ort, Termin, Quelle
 * und ein Satz oder der Vorspann. Nur gepflegte Felder; ein leeres Feld entfällt samt Bezeichnung. Ein eigenes Feld
 * „Warum das wichtig ist“ gibt es nicht, also auch kein solches Etikett. Ein Termin vor heute steht als „war am …“
 * da (tamil_termin_vorbei()); je Beitrag gibt es genau einen Termin (event_datum), also keinen „nächsten“ zur Wahl.
 *
 * @param array<string,mixed> $opt {
 *     @type string $form  „cover“ (Angaben als Liste mit Bezeichnung, daneben der Vorspann) oder „zeile“ (Ort, Satz, Quelle).
 *     @type string $satz  „vorspann“ (ganze Sätze bis 260 Zeichen), „einer“ (ein Satz) oder leer (kein Satz).
 *     @type string $titel Zeile über den Angaben (nur „cover“, etwa „Titelgeschichte“).
 *     @type bool   $datum Erscheinungsdatum unter den Angaben (nur „cover“).
 *     @type bool   $ort   Ort nennen (Standard ja).
 *     @type bool   $quelle Quelle nennen (Standard ja).
 * }
 * @return string Escaptes HTML, leer ohne Inhalt.
 */
function tamil_kontext( int $post_id, array $opt = array() ): string {
	$form   = 'zeile' === ( $opt['form'] ?? 'cover' ) ? 'zeile' : 'cover';
	$e      = function_exists( 'tamil_site_event' ) ? (array) tamil_site_event( $post_id ) : array();
	$ort    = '';
	$termin = '';
	if ( ! empty( $e['datum'] ) ) {
		$termin = tamil_termin_text( (string) $e['datum'], (string) ( $e['ende'] ?? '' ) );
		if ( tamil_termin_vorbei( (string) $e['datum'], (string) ( $e['ende'] ?? '' ) ) ) {
			// Ein Termin vor heute steht nie da wie eine Ankündigung (Kritik vom 22.11.2026). Ein Zeitraum beginnt mit dem
			// Tag („20. November bis …“), ein einzelner Tag mit dem Wochentag („Sa, 21. November 2026“).
			/* translators: %s: Datum oder Zeitraum eines vergangenen Termins */
			$termin = sprintf( preg_match( '/^\d/', $termin ) ? __( 'war vom %s', 'tamil' ) : __( 'war am %s', 'tamil' ), $termin );
		}
		$ort = tamil_ort_kurz( (string) ( $e['ort'] ?? '' ) );
		$ort = __( 'Ort folgt', 'tamil' ) === $ort ? '' : $ort;
	}
	if ( '' === $ort ) {
		$ort = trim( (string) get_post_meta( $post_id, 'ort', true ) );
	}
	$ort    = ( $opt['ort'] ?? true ) ? $ort : '';
	$quelle = ( $opt['quelle'] ?? true ) ? trim( (string) get_post_meta( $post_id, 'quelle_name', true ) ) : '';
	$art    = (string) ( $opt['satz'] ?? '' );
	$satz   = '';
	if ( 'vorspann' === $art ) {
		$satz = tamil_ganze_saetze( tamil_saetze_bis( tamil_standfirst( $post_id ), 260 ) );
	} elseif ( 'einer' === $art ) {
		$satz = tamil_probe_satz( $post_id );
	}
	$satz_html = '' !== trim( $satz ) ? '<p class="kontext__satz">' . tamil_text( $satz ) . '</p>' : '';

	if ( 'zeile' === $form ) {
		$html  = '' !== $ort ? '<p class="kontext__ort">' . tamil_text( $ort ) . '</p>' : '';
		$html .= $satz_html;
		/* translators: %s: Name der Quelle */
		$html .= '' !== $quelle ? '<p class="kontext__quelle">' . tamil_text( sprintf( __( 'Quelle: %s', 'tamil' ), $quelle ) ) . '</p>' : '';
		return '' !== $html ? '<div class="kontext kontext--zeile">' . $html . '</div>' : '';
	}

	$angaben = array_filter(
		array(
			'ort'    => array( __( 'Ort', 'tamil' ), $ort ),
			'termin' => array( __( 'Termin', 'tamil' ), $termin ),
			'quelle' => array( __( 'Quelle', 'tamil' ), $quelle ),
			'datum'  => array( __( 'Erschienen', 'tamil' ), ! empty( $opt['datum'] ) ? (string) wp_date( 'j. F Y', (int) get_post_timestamp( $post_id ) ) : '' ),
		),
		static fn( array $x ): bool => '' !== $x[1]
	);
	$liste   = '';
	foreach ( $angaben as $schluessel => $x ) {
		$liste .= '<div class="kontext__angabe kontext__angabe--' . esc_attr( $schluessel ) . '"><dt>' . esc_html( $x[0] ) . '</dt><dd>' . tamil_text( $x[1] ) . '</dd></div>';
	}
	$titel = trim( (string) ( $opt['titel'] ?? '' ) );
	$kopf  = ( '' !== $titel ? '<p class="kontext__titel">' . esc_html( $titel ) . '</p>' : '' ) . ( '' !== $liste ? '<dl class="kontext__angaben">' . $liste . '</dl>' : '' );
	if ( '' === $kopf && '' === $satz_html ) {
		return '';
	}
	return '<div class="kontext kontext--cover">' . ( '' !== $kopf ? '<div class="kontext__kopf">' . $kopf . '</div>' : '' ) . $satz_html . '</div>';
}

/**
 * Städte aus dem Freitext „Ort der Meldung“ (Meta ort): trennt an Komma, Semikolon, Schrägstrich und „ und “, verwirft
 * Länder, Kantone, Klammern, Postleitzahlen und Einrichtungen. Es gibt kein eigenes Stadt-Feld; das Ergebnis ist eine
 * Zerlegung von Freitext und kennt keine Länder.
 *
 * @return array<string,string> Schlüssel (sanitize_title) → Schreibweise.
 */
function tamil_stadt_namen( string $ort ): array {
	$ort   = (string) preg_replace( '/\([^)]*\)/u', ' ', $ort );
	$teile = preg_split( '/\s*[,;\/]\s*|\s+und\s+/u', $ort );
	$kein  = array( 'deutschland', 'schweiz', 'österreich', 'oesterreich', 'sri lanka', 'indien', 'frankreich', 'italien', 'kanada', 'grossbritannien', 'großbritannien', 'england', 'europa', 'tamil nadu', 'tamil eelam', 'weltweit', 'online', 'ort folgt' );
	$namen = array();
	foreach ( is_array( $teile ) ? $teile : array() as $teil ) {
		$teil  = trim( (string) preg_replace( '/^(?:[A-Z]{1,2}-)?\d{4,5}\s+/u', '', trim( (string) preg_replace( '/\s+/u', ' ', $teil ) ) ) );
		$klein = mb_strtolower( $teil );
		if ( '' === $teil || in_array( $klein, $kein, true ) || mb_strlen( $teil ) > 30 || count( explode( ' ', $teil ) ) > 3 ) {
			continue;
		}
		if ( preg_match( '/\d|kanton|tamilalayam|schule|verein|tempel|zentrum|halle|stra(?:ß|ss)e|platz\b/iu', $teil ) || ! preg_match( '/^\p{Lu}/u', $teil ) ) {
			continue;
		}
		$schluessel = sanitize_title( $teil );
		if ( '' !== $schluessel && ! isset( $namen[ $schluessel ] ) ) {
			$namen[ $schluessel ] = $teil;
		}
	}
	return $namen;
}

/**
 * „Tamil in meiner Stadt“: so viele der neuesten Beiträge mit Ort zählen für die Auswahl der Städte.
 */
const TAMIL_STADT_VORRAT = 200;

/**
 * „Tamil in meiner Stadt“ unter „Alle Städte“: Geschichten sind höchstens so viele Tage alt.
 */
const TAMIL_STADT_TAGE = 60;

/**
 * Hat dieses Kino einer Kinoliste noch eine Vorstellung ab heute? Mit einzelnen Spieltagen zählen nur die kommenden,
 * mit Zeitraum das Ende; ein Kino ohne beides läuft, solange die Liste selbst gilt (tamil_kino_filme()).
 *
 * @param array<string,mixed> $k     Eintrag aus kino_fakten['kinos'].
 * @param string              $heute JJJJ-MM-TT.
 * @return array<string,mixed> Der Eintrag mit den kommenden Spieltagen, leer, wenn nichts mehr läuft.
 */
function tamil_stadt_kino_laeuft( array $k, string $heute ): array {
	if ( ! empty( $k['termine'] ) ) {
		$k['termine'] = array_values( array_filter( (array) $k['termine'], static fn( $d ) => substr( (string) $d, 0, 10 ) >= $heute ) );
		return $k['termine'] ? $k : array();
	}
	if ( ! empty( $k['bis'] ) && substr( (string) $k['bis'], 0, 10 ) < $heute ) {
		return array();
	}
	return $k;
}

/**
 * Daten für „Tamil in meiner Stadt“: Städte der Auswahl und alles, was der Abschnitt zeigen kann (je Beitrag mit den
 * Schlüsseln seiner Städte). Einmal je Seitenaufruf gerechnet, ohne eigenen Zwischenspeicher.
 *
 * - Kino: tamil_kino_filme( 6 ), je Kino nur mit Vorstellung ab heute. Zählt die Kinoliste mehr Kinos, als ab heute
 *   noch spielen, trägt der Film „zahl_text“ („ab heute noch 1 von 13 Kinos“), damit die Karte hier nicht ohne
 *   Erklärung eine andere Zahl nennt als „Diese Woche“ (dort stehen alle Kinos der Liste).
 * - Termine: die nächsten zwölf (Plugin tamil-site), Stadt aus tamil_termin_angaben(); „Ort folgt“ hat keine Stadt.
 * - Geschichten: Beiträge mit „Ort der Meldung“, aus dem eine Stadt lesbar ist, neueste zuerst; ohne die Beiträge des
 *   ersten Abschnitts, von „Diese Woche“ und ohne die Filme und Termine dieses Abschnitts. Gezählt werden die
 *   TAMIL_STADT_VORRAT neuesten (bis 3.16.0 nur 24: Städte mit zwei älteren Beiträgen fehlten in der Auswahl). Unter
 *   „Alle Städte“ stehen nur die drei neuesten der letzten TAMIL_STADT_TAGE Tage („alle“); gibt es keine, entfällt das
 *   Fach dort. Für eine gewählte Stadt stehen ihre drei neuesten da, ohne Altersgrenze.
 * - In die Auswahl kommt jede Stadt mit mindestens einer Vorstellung ab heute, einem kommenden Termin oder zwei
 *   Geschichten; alphabetisch. Einträge des Verzeichnisses werden nicht verwendet.
 *
 * @return array{staedte:array<string,string>,filme:array<int,array<string,mixed>>,termine:array<int,array{id:int,stadt:string}>,geschichten:array<int,array{id:int,staedte:string[],alle:bool}>,ids:int[]}
 */
function tamil_stadt_daten(): array {
	static $daten = null;
	if ( null !== $daten ) {
		return $daten;
	}
	$a     = tamil_start_auswahl();
	$heute = current_time( 'Y-m-d' );
	$namen = array();
	$zahl  = array();
	$merke = static function ( string $name, string $fach ) use ( &$namen, &$zahl ): string {
		$schluessel = sanitize_title( $name );
		if ( '' === $schluessel ) {
			return '';
		}
		if ( ! isset( $namen[ $schluessel ] ) ) {
			$namen[ $schluessel ] = $name;
			$zahl[ $schluessel ]  = array(
				'kino'        => 0,
				'termine'     => 0,
				'geschichten' => 0,
			);
		}
		++$zahl[ $schluessel ][ $fach ];
		return $schluessel;
	};

	$filme = array();
	foreach ( tamil_kino_filme( 6 ) as $f ) {
		$gesamt = count( (array) ( $f['fakten']['kinos'] ?? array() ) );
		$kinos  = array_values( array_filter( array_map( static fn( $k ) => tamil_stadt_kino_laeuft( (array) $k, $heute ), (array) ( $f['fakten']['kinos'] ?? array() ) ) ) );
		$orte   = array();
		foreach ( $kinos as $k ) {
			$stadt = trim( (string) preg_replace( '/\s+/u', ' ', (string) ( $k['stadt'] ?? '' ) ) );
			if ( '' === $stadt ) {
				continue;
			}
			$schluessel = isset( $orte[ sanitize_title( $stadt ) ] ) ? sanitize_title( $stadt ) : $merke( $stadt, 'kino' );
			if ( '' === $schluessel ) {
				continue;
			}
			$orte[ $schluessel ][] = array(
				'kino'   => trim( (string) ( $k['kino'] ?? '' ) ),
				'termin' => tamil_kino_termin_text( $k ),
				'url'    => (string) ( $k['url'] ?? '' ),
			);
		}
		if ( ! $kinos ) {
			continue;
		}
		$f['fakten']['kinos'] = $kinos;
		$f['kinos']           = count( $kinos );
		if ( count( $kinos ) < $gesamt ) {
			// Dieser Abschnitt zählt nur Kinos mit Vorstellung ab heute, „Diese Woche“ alle Kinos der Liste. Stehen beide
			// Zahlen auf derselben Seite, sagt die Karte hier, was sie zählt (Kritik vom 22.11.2026: „1 Kino“ neben „13 Kinos“).
			/* translators: 1: Kinos mit Vorstellung ab heute, 2: alle Kinos der Kinoliste */
			$f['zahl_text'] = sprintf( __( 'ab heute noch %1$d von %2$d Kinos', 'tamil' ), count( $kinos ), $gesamt );
		}
		$f['staedte'] = array_values( array_map( static fn( $s ) => $namen[ $s ], array_keys( $orte ) ) );
		$filme[]      = array(
			'film' => $f,
			'orte' => $orte,
		);
	}

	$termine = array();
	if ( function_exists( 'tamil_site_upcoming_events' ) && function_exists( 'tamil_site_event' ) ) {
		$ids = array_map( 'intval', tamil_site_upcoming_events( 12, array( 'fields' => 'ids' ) )->posts );
		tamil_cache_fuellen( $ids );
		foreach ( $ids as $id ) {
			$e = tamil_site_event( $id );
			if ( ! $e ) {
				continue;
			}
			$stadt     = tamil_termin_angaben( $id, $e )['stadt'];
			$termine[] = array(
				'id'    => $id,
				'stadt' => __( 'Ort folgt', 'tamil' ) === $stadt ? '' : $merke( $stadt, 'termine' ),
			);
		}
	}

	$belegt  = array_merge(
		array( (int) $a['lead'] ),
		array_map( 'intval', (array) $a['neben'] ),
		array_map( 'intval', (array) $a['meldungen'] ),
		array_map( 'intval', (array) ( $a['woche']['bilder'] ?? array() ) ),
		array_map( 'intval', wp_list_pluck( (array) ( $a['woche']['filme'] ?? array() ), 'post' ) ),
		array_map( 'intval', (array) ( $a['woche']['termine'] ?? array() ) ),
		array_map( static fn( $f ) => (int) $f['film']['post'], $filme ),
		wp_list_pluck( $termine, 'id' )
	);
	$mit_ort = tamil_ids(
		array(
			'posts_per_page' => TAMIL_STADT_VORRAT,
			'meta_query'     => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query -- nur auf Probenseiten
				array(
					'key'     => 'ort',
					'value'   => '',
					'compare' => '!=',
				),
			),
		),
		$belegt
	);
	usort( $mit_ort, 'tamil_probe_neuer_zuerst' );
	$grenze = (int) strtotime( $heute . ' 00:00:00 ' . wp_timezone_string() ) - TAMIL_STADT_TAGE * DAY_IN_SECONDS;
	$vorrat = array();
	foreach ( $mit_ort as $id ) {
		$orte = array();
		foreach ( tamil_stadt_namen( (string) get_post_meta( $id, 'ort', true ) ) as $name ) {
			$orte[] = $merke( $name, 'geschichten' );
		}
		$orte = array_values( array_filter( $orte ) );
		if ( $orte ) {
			$vorrat[ $id ] = $orte;
		}
	}

	// Auswahl: mindestens eine Vorstellung ab heute, ein kommender Termin oder zwei Geschichten
	$staedte = array();
	foreach ( $namen as $schluessel => $name ) {
		if ( $zahl[ $schluessel ]['kino'] || $zahl[ $schluessel ]['termine'] || $zahl[ $schluessel ]['geschichten'] >= 2 ) {
			$staedte[ $schluessel ] = $name;
		}
	}
	asort( $staedte, SORT_LOCALE_STRING | SORT_FLAG_CASE );

	// Ins HTML kommen nur Geschichten, die jemand sehen kann: die drei neuesten je wählbarer Stadt und, für „Alle
	// Städte“, die drei neuesten der letzten TAMIL_STADT_TAGE Tage (Schlüssel „alle“).
	$geschichten = array();
	$je_stadt    = array();
	$alle        = 0;
	foreach ( $vorrat as $id => $orte ) {
		$orte   = array_values( array_filter( $orte, static fn( string $s ): bool => isset( $staedte[ $s ] ) ) );
		$frisch = $alle < 3 && (int) get_post_timestamp( $id ) >= $grenze;
		$zeigen = array_filter( $orte, static fn( string $s ): bool => ( $je_stadt[ $s ] ?? 0 ) < 3 );
		if ( ! $frisch && ! $zeigen ) {
			continue;
		}
		foreach ( $orte as $s ) {
			$je_stadt[ $s ] = ( $je_stadt[ $s ] ?? 0 ) + 1;
		}
		$alle         += $frisch ? 1 : 0;
		$geschichten[] = array(
			'id'      => (int) $id,
			'staedte' => $orte,
			'alle'    => $frisch,
		);
	}

	$daten = array(
		'staedte'     => $staedte,
		'filme'       => $filme,
		'termine'     => $termine,
		'geschichten' => $geschichten,
		'ids'         => array_values( array_unique( array_merge( array_map( static fn( $f ) => (int) $f['film']['post'], $filme ), wp_list_pluck( $termine, 'id' ), wp_list_pluck( $geschichten, 'id' ) ) ) ),
	);
	return $daten;
}
