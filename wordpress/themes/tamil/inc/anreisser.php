<?php
/**
 * Anreißer in klar2: Bild im Rahmen, Dachzeile „Rubrik | Datum“, Titel, Vorspann. Jeder Anreißer ist ein einziger
 * Link (a.anr) um Bild und Text; Bilder füllen ihren Rahmen (object-fit: cover), Nachweise sammelt der Fuß.
 *
 * Jeder Anreißer hat ein Bild: tamil_bild() (inc/bildkette.php) liefert das eigene Foto, ein Bild aus dem Text oder ein
 * Symbolbild aus dem Rubrik-Pool. Bausteine: tamil_meta(), tamil_anr_imbild() (Bildkarte, Titel im Bild),
 * tamil_anr_stueck() (Nebenstück als Karte), tamil_anr_zeile() und tamil_zeilen() (Listen als Kartenraster),
 * tamil_kacheln() (Rubrikkacheln), tamil_grafik_kino(), tamil_grafik_termin(), tamil_grafik_leer() (Bildkacheln auf
 * Dunkel für Kino und Termine; als Karte mit Titel im Bild).
 *
 * Seit 3.7.0 ist jeder Beitrags-Anreißer der Website eine Bildkarte (Luis, 20.11.2026). Ausgenommen sind nur
 * Rubrikkacheln (Navigation), Leerzustände, die Kinotabelle (Spielorte) und Verzeichniseinträge.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Alternativtext eines Beitragsbilds: der Text aus der Mediathek, leer, wenn er nur den Titel wiederholt (der Titel
 * steht im selben Link).
 */
function tamil_bild_alt( int $post_id ): string {
	$alt = trim( (string) get_post_meta( (int) get_post_thumbnail_id( $post_id ), '_wp_attachment_image_alt', true ) );
	return wp_strip_all_tags( get_the_title( $post_id ) ) === $alt ? '' : $alt;
}

/**
 * Dachzeile „Rubrik | Datum“ (ein Format für alle Anreißer).
 *
 * @param array<string,mixed> $opt { @type bool $rubrik Rubrik nennen (Standard ja), @type int $ts anderer Zeitpunkt. }
 */
function tamil_meta( int $post_id, array $opt = array() ): string {
	$kat = ( $opt['rubrik'] ?? true ) ? tamil_hauptkategorie( $post_id ) : null;
	$ts  = (int) ( $opt['ts'] ?? get_post_timestamp( $post_id ) );
	return sprintf(
		'<p class="meta">%1$s<time datetime="%2$s">%3$s</time></p>',
		$kat ? '<span class="meta__rubrik">' . esc_html( $kat->name ) . '</span>' : '',
		esc_attr( wp_date( 'Y-m-d', $ts ) ),
		esc_html( wp_date( 'j. F Y', $ts ) )
	);
}

/**
 * Titel eines Beitrags für Anreißer (escapt, tamilische Wörter mit lang="ta").
 */
function tamil_titel( int $post_id ): string {
	return tamil_text( get_the_title( $post_id ) );
}

/**
 * Überschriftenebene prüfen.
 */
function tamil_ebene( string $ebene, string $sonst = 'h3' ): string {
	return in_array( $ebene, array( 'h2', 'h3', 'h4' ), true ) ? $ebene : $sonst;
}

/**
 * Bild mit Titel im Bild: Aufmacher, Kacheln und jede Bildkarte (seit 3.7.0 jeder Beitrags-Anreißer der Website, Luis
 * 20.11.2026: „auf jeder Meldung Tamil Dots und Schrift auf der Karte“). Dachzeile „Rubrik | Datum“ und Titel auf dem
 * Verlauf im Foto, Punktbogen unten rechts, Schild „Symbolbild“ oben rechts (beides aus tamil_bild()).
 *
 * @param array<string,mixed> $opt {
 *     @type string $klasse   Klassen des <article> (z. B. „aufmacher“, „karte“, „kachel kachel--gross“).
 *     @type string $rahmen   Formatklasse des Rahmens (r43, r169, r83 oder leer, dann setzt das CSS das Format).
 *     @type string $ebene    h2, h3 oder h4.
 *     @type bool|string $vorspann Vorspann unter dem Bild: true (ganze Sätze bis 260 Zeichen) oder „kurz“ (30 Wörter).
 *     @type bool   $rubrik   Rubrik in der Dachzeile (Standard ja; nein in Blöcken, deren Titel die Rubrik nennt).
 *     @type int    $ts       anderer Zeitpunkt für die Dachzeile.
 *     @type string $dach     eigene Dachzeile statt „Rubrik | Datum“ (escaptes HTML, etwa das Datum eines Termins).
 *     @type string $zusatz   Angaben unter dem Bild (escaptes HTML, etwa Ort und Eintritt eines Termins).
 *     @type string $markiere Suchwort, das in Titel und Vorspann hervorgehoben wird.
 *     @type string $sizes, @type bool $eager, @type bool $niedrig (Bild mit geringem Vorrang, siehe tamil_bild()).
 * }
 */
function tamil_anr_imbild( int $post_id, array $opt = array() ): string {
	$img  = tamil_bild(
		$post_id,
		array(
			'sizes'   => $opt['sizes'] ?? '',
			'eager'   => ! empty( $opt['eager'] ),
			'niedrig' => ! empty( $opt['niedrig'] ),
		)
	);
	$meta = array( 'rubrik' => $opt['rubrik'] ?? true );
	if ( ! empty( $opt['ts'] ) ) {
		$meta['ts'] = (int) $opt['ts'];
	}
	$wort  = (string) ( $opt['markiere'] ?? '' );
	$ebene = tamil_ebene( (string) ( $opt['ebene'] ?? 'h3' ) );
	$dach  = isset( $opt['dach'] ) ? (string) $opt['dach'] : tamil_meta( $post_id, $meta );
	$text  = $dach . sprintf( '<%1$s class="titel">%2$s</%1$s>', $ebene, tamil_markiere( tamil_titel( $post_id ), $wort ) );
	$wow   = ! empty( $opt['wow'] ); // Wow-Aufmacher (inc/wow.php): Bahn und Halter um Bild und Vorspann, Decke über dem Foto
	$html  = '<article class="' . esc_attr( (string) ( $opt['klasse'] ?? 'kachel' ) . ( $wow ? ' wow' : '' ) ) . '">';
	$html .= '<a class="anr imbild-anr" href="' . esc_url( get_permalink( $post_id ) ) . '">';
	$html .= $wow ? '<div class="wow-bahn"><div class="wow-halter">' : '';
	$html .= '<div class="rahmen' . ( ! empty( $opt['rahmen'] ) ? ' ' . esc_attr( (string) $opt['rahmen'] ) : '' ) . ( $wow ? ' wow-rahmen' : '' ) . '">' . $img;
	$html .= $wow ? '<canvas class="wow-decke" aria-hidden="true"></canvas>' : '';
	$html .= '<div class="imbild">' . $text . '</div></div>';
	$html .= (string) ( $opt['zusatz'] ?? '' );
	if ( 'kurz' === ( $opt['vorspann'] ?? false ) ) {
		// ganze Sätze bis etwa 130 Zeichen (drei Zeilen), damit die Begrenzung auf drei Zeilen kein Datum („19.…“) und
		// keinen Satz mitten im Wort schneidet; nur ein überlanger erster Satz wird an einer Wortgrenze gekürzt
		$kurz  = tamil_saetze_bis( tamil_standfirst( $post_id ), 130 );
		$kurz  = mb_strlen( $kurz ) > 150 ? wp_trim_words( $kurz, 20, ' …' ) : $kurz;
		$html .= '<p class="vorspann">' . tamil_markiere( tamil_text( $kurz ), $wort ) . '</p>';
	} elseif ( ! empty( $opt['vorspann'] ) ) {
		$html .= '<p class="vorspann">' . tamil_markiere( tamil_text( tamil_ganze_saetze( tamil_saetze_bis( tamil_standfirst( $post_id ), 260 ) ) ), $wort ) . '</p>';
	}
	return $html . ( $wow ? '</div></div>' : '' ) . '</a></article>';
}

/**
 * Nebenstück („Weiterlesen“): seit 3.7.0 eine Bildkarte mit Titel im Bild und Vorspann darunter.
 *
 * @param array<string,mixed> $opt { @type string $ebene, @type string $sizes, @type string $klasse, @type bool $rubrik. }
 */
function tamil_anr_stueck( int $post_id, array $opt = array() ): string {
	return tamil_anr_imbild(
		$post_id,
		array(
			'klasse'   => (string) ( $opt['klasse'] ?? 'karte' ),
			'rahmen'   => 'r169',
			'ebene'    => (string) ( $opt['ebene'] ?? 'h3' ),
			'rubrik'   => $opt['rubrik'] ?? true,
			'vorspann' => 'kurz',
			'niedrig'  => true,
			'sizes'    => (string) ( $opt['sizes'] ?? '(min-width: 1024px) 290px, (min-width: 600px) calc(50vw - 36px), 320px' ),
		)
	);
}

/**
 * Eintrag einer Liste (Rubrik, Suche, Archive, Termine, Production, 404, Weiterlesen): seit 3.7.0 eine Bildkarte mit
 * Titel im Bild in einem <li>; Vorspann und Angaben unter dem Bild.
 *
 * @param array<string,mixed> $opt {
 *     @type string $klasse   zusätzliche Klasse der Karte (Standard „karte--zeile“).
 *     @type string $ebene    h2, h3 oder h4.
 *     @type bool   $vorspann Vorspann unter dem Bild (kurz, 30 Wörter).
 *     @type bool   $rubrik   Rubrik in der Dachzeile.
 *     @type int    $ts       anderer Zeitpunkt für die Dachzeile (Termine).
 *     @type string $sizes.
 *     @type string $markiere Suchwort, das in Titel und Vorspann hervorgehoben wird.
 *     @type string $zusatz   weitere Angaben unter dem Bild (escaptes HTML, etwa Ort und Eintritt eines Termins).
 *     @type string $dach     eigene Dachzeile statt „Rubrik | Datum“ (escaptes HTML, etwa Datum mit Uhrzeit).
 *     @type string $attr     weitere Attribute des <li> (escapt, etwa data-land für Filter).
 *     @type bool   $eager    Bild sofort und vorrangig (erste Karte im ersten Bildschirm), sonst mit geringem Vorrang.
 * }
 */
function tamil_anr_zeile( int $post_id, array $opt = array() ): string {
	$zusatz = (string) ( $opt['zusatz'] ?? '' );
	$karte  = array(
		'klasse'   => trim( 'karte ' . (string) ( $opt['klasse'] ?? 'karte--zeile' ) ),
		'rahmen'   => 'r169',
		'ebene'    => (string) ( $opt['ebene'] ?? 'h3' ),
		'rubrik'   => $opt['rubrik'] ?? true,
		'vorspann' => ! empty( $opt['vorspann'] ) ? 'kurz' : false,
		'markiere' => (string) ( $opt['markiere'] ?? '' ),
		'zusatz'   => '' !== $zusatz ? '<div class="karte__zusatz">' . $zusatz . '</div>' : '',
		'eager'    => ! empty( $opt['eager'] ),
		'niedrig'  => empty( $opt['eager'] ),
		'sizes'    => (string) ( $opt['sizes'] ?? '(min-width: 1024px) 384px, (min-width: 600px) calc(50vw - 36px), calc(100vw - 32px)' ),
	);
	if ( ! empty( $opt['ts'] ) ) {
		$karte['ts'] = (int) $opt['ts'];
	}
	if ( isset( $opt['dach'] ) ) {
		$karte['dach'] = (string) $opt['dach'];
	}
	return '<li class="karten__eintrag"' . (string) ( $opt['attr'] ?? '' ) . '>' . tamil_anr_imbild( $post_id, $karte ) . '</li>';
}

/**
 * Suchwort in schon escaptem HTML mit <mark> hervorheben (nur im Text, nie in Tags oder Attributen).
 */
function tamil_markiere( string $html, string $wort ): string {
	$wort = trim( $wort );
	if ( mb_strlen( $wort ) < 2 ) {
		return $html;
	}
	$muster = '/' . preg_quote( esc_html( $wort ), '/' ) . '/iu';
	$teile  = preg_split( '/(<[^>]*>)/u', $html, -1, PREG_SPLIT_DELIM_CAPTURE );
	if ( ! is_array( $teile ) ) {
		return $html;
	}
	foreach ( $teile as $i => $teil ) {
		if ( '' !== $teil && '<' !== $teil[0] ) {
			$teile[ $i ] = (string) preg_replace( $muster, '<mark>$0</mark>', $teil );
		}
	}
	return implode( '', $teile );
}

/**
 * Liste von Beiträgen (Rubrik, Suche, Archive, Production, 404, Kinojahr) als Kartenraster: Handy eine Spalte, Tablet
 * zwei, Desktop drei; Vorspann unter dem Bild.
 *
 * @param int[]               $ids Beiträge.
 * @param array<string,mixed> $opt wie tamil_anr_zeile(), dazu @type bool $erste_eager die erste Karte sofort laden
 *                                 (Liste im ersten Bildschirm).
 */
function tamil_zeilen( array $ids, array $opt = array() ): string {
	$opt  = array_merge( array( 'vorspann' => true ), $opt );
	$html = '<ul class="karten karten--raster">';
	foreach ( array_values( $ids ) as $i => $id ) {
		$html .= tamil_anr_zeile( (int) $id, array_merge( $opt, array( 'eager' => 0 === $i && ! empty( $opt['erste_eager'] ) ) ) );
	}
	return $html . '</ul>';
}

/**
 * Listen im Seiteninhalt, deren Punkte nur je einen Link auf einen Beitrag dieser Website enthalten (etwa „Die
 * Konzerte im Archiv“ auf /production/), als Liste mit Bild ausgeben (Bilderpflicht, Tippflächen). Andere Listen
 * bleiben, wie sie sind; Beiträge aus $ohne (stehen auf der Seite schon) fallen aus der Liste.
 *
 * @param int[] $ohne Beiträge, die schon gezeigt werden.
 */
function tamil_beitragslisten_mit_bild( string $html, array $ohne = array() ): string {
	if ( ! str_contains( $html, '<ul' ) ) {
		return $html;
	}
	$neu = preg_replace_callback(
		'#<ul\b[^>]*>(.*?)</ul>#is',
		static function ( array $m ) use ( $ohne ): string {
			if ( ! preg_match_all( '#<li\b[^>]*>(.*?)</li>#is', $m[1], $punkte ) ) {
				return $m[0];
			}
			$ids = array();
			foreach ( $punkte[1] as $punkt ) {
				if ( 1 !== preg_match_all( '#<a\b[^>]*\shref\s*=\s*(["\'])([^"\']+)\1#i', $punkt, $links ) || '' !== trim( wp_strip_all_tags( (string) preg_replace( '#<a\b.*?</a>#is', '', $punkt ) ) ) ) {
					return $m[0]; // mehr als ein Link oder Text neben dem Link: eine normale Liste
				}
				$url = html_entity_decode( $links[2][0], ENT_QUOTES );
				$id  = url_to_postid( str_starts_with( $url, '/' ) ? home_url( $url ) : $url );
				if ( ! $id || 'post' !== get_post_type( $id ) || 'publish' !== get_post_status( $id ) ) {
					return $m[0];
				}
				$ids[] = $id;
			}
			$ids = array_values( array_diff( array_unique( $ids ), array_map( 'intval', $ohne ) ) );
			return $ids ? tamil_zeilen( $ids, array( 'rubrik' => false ) ) : '';
		},
		$html
	);
	return is_string( $neu ) ? $neu : $html;
}

/**
 * Rubrikkacheln: kleine Bildkacheln mit dem Rubriknamen im Bild. Navigation, keine Schlagzeilen.
 *
 * @param array<int,array{label:string,url:string,slug:string,bild:int}> $kacheln Bild = Beitrag mit Foto oder 0.
 */
function tamil_kacheln( array $kacheln, string $label ): string {
	if ( ! $kacheln ) {
		return '';
	}
	$html = '<nav class="kacheln" aria-label="' . esc_attr( $label ) . '"><ul>';
	foreach ( $kacheln as $k ) {
		// Der Name steht im Bild: kein Alternativtext, kein Schild und kein Signet (Navigation, kein Beitrag); ohne
		// Beitrag mit Foto ein Bild des Pools. Die Bilder laden „lazy“, app.js lädt sie gesammelt, sobald der Streifen
		// in die Nähe kommt.
		$img   = $k['bild'] ? (string) preg_replace(
			'/ alt="[^"]*"/',
			' alt=""',
			tamil_bild(
				(int) $k['bild'],
				array(
					'sizes'  => '160px',
					'schild' => false,
					'signet' => false,
				)
			),
			1
		) : tamil_pool_img(
			$k['slug'],
			array(
				'schild' => false,
				'alt'    => false,
				'sizes'  => '160px',
			)
		);
		$html .= sprintf(
			'<li><a href="%1$s"><span class="rahmen">%2$s</span><span class="kachel__name">%3$s</span></a></li>',
			esc_url( $k['url'] ),
			$img,
			esc_html( $k['label'] )
		);
	}
	return $html . '</ul></nav>';
}

/**
 * Karte „Im Kino“ (auf Titan): Film und Zahl der Kinos im Bild, die Städte darunter (Startseite „Diese Woche“, Kino
 * „Im Programm“).
 *
 * @param array<string,mixed> $f Ergebnis von tamil_kino_film().
 */
function tamil_grafik_kino( array $f, string $ebene = 'h3' ): string {
	$laender = array_unique( array_filter( array_map( static fn( $k ) => (string) ( $k['land'] ?? '' ), (array) ( $f['fakten']['kinos'] ?? array() ) ) ) );
	$namen   = array(
		'DE' => __( 'in Deutschland', 'tamil' ),
		'AT' => __( 'in Österreich', 'tamil' ),
		'CH' => __( 'in der Schweiz', 'tamil' ),
	);
	$wo      = 1 === count( $laender ) && isset( $namen[ reset( $laender ) ] ) ? ' ' . $namen[ reset( $laender ) ] : '';
	/* translators: %d: Anzahl der Kinos */
	$zahl  = sprintf( _n( '%d Kino', '%d Kinos', (int) $f['kinos'], 'tamil' ), (int) $f['kinos'] ) . $wo;
	$ebene = tamil_ebene( $ebene );
	$kat   = tamil_hauptkategorie( (int) $f['post'] );
	return sprintf(
		'<li class="grafik grafik--karte" data-grafik="kino"><a class="anr imbild-anr" href="%1$s"><div class="rahmen r169">%6$s<div class="imbild"><p class="meta">%5$s<span>%4$s</span></p><%2$s class="titel">%3$s</%2$s></div></div>%7$s</a></li>',
		esc_url( $f['link'] ),
		$ebene,
		esc_html( $f['film'] ),
		esc_html( $zahl ),
		$kat ? '<span class="meta__rubrik">' . esc_html( $kat->name ) . '</span>' : '',
		tamil_bild( (int) $f['post'], array( 'sizes' => '(min-width: 1024px) 380px, (min-width: 600px) 50vw, 100vw' ) ),
		$f['staedte'] ? '<div class="grafik__inhalt"><p class="grafik__orte">' . esc_html( tamil_staedte_kurz( $f['staedte'] ) ) . '</p></div>' : ''
	);
}

/**
 * Angaben eines Termins für Kacheln und Zeilen: Datum mit Uhrzeit und Ende, Ort, Veranstalter, Eintritt.
 *
 * @param array<string,string> $e Ergebnis von tamil_site_event().
 * @return array{datum:string,iso:string,orte:string,eintritt:string,stadt:string,land:string}
 */
function tamil_termin_angaben( int $post_id, array $e ): array {
	$start = date_create_immutable( (string) $e['datum'], wp_timezone() );
	$orte  = array_filter(
		array(
			tamil_ort_kurz( (string) $e['ort'] ),
			tamil_wer_kurz( (string) $e['veranstalter'], get_the_title( $post_id ), (string) $e['ort'] ),
		)
	);
	$preis = trim( (string) ( $e['preis'] ?? '' ) );
	return array(
		'datum'    => tamil_termin_text( (string) $e['datum'], (string) $e['ende'] ),
		'iso'      => $start ? $start->format( 'Y-m-d' ) : '',
		'orte'     => implode( ', ', $orte ),
		/* translators: %s: Eintrittspreis */
		'eintritt' => '' !== $preis ? sprintf( __( 'Eintritt: %s', 'tamil' ), $preis ) : '',
		'stadt'    => tamil_ort_kurz( (string) $e['ort'] ),
		'land'     => strtoupper( trim( (string) ( $e['land'] ?? '' ) ) ),
	);
}

/**
 * Karte „Termin“ (auf Titan): Dachzeile „Rubrik | Datum des Termins“ und Titel im Bild, Ort und Eintritt darunter,
 * auf Wunsch der Vorspann.
 *
 * @param bool $text   Vorspann unter dem Bild.
 * @param bool $sofort Bild sofort und vorrangig laden (erste Karte im ersten Bildschirm, etwa „Ab heute“ auf /events/).
 */
function tamil_grafik_termin( int $post_id, string $ebene = 'h3', bool $text = true, bool $sofort = false ): string {
	$e = function_exists( 'tamil_site_event' ) ? tamil_site_event( $post_id ) : array();
	if ( ! $e ) {
		return '';
	}
	$a     = tamil_termin_angaben( $post_id, $e );
	$ebene = tamil_ebene( $ebene );
	$kat   = tamil_hauptkategorie( $post_id );
	$datum = '' !== $a['iso'] ? '<time datetime="' . esc_attr( $a['iso'] ) . '">' . esc_html( $a['datum'] ) . '</time>' : esc_html( $a['datum'] );
	$unter = implode( '. ', array_filter( array( $a['orte'], $a['eintritt'] ) ) );
	return sprintf(
		'<li class="grafik grafik--karte" data-grafik="termin"><a class="anr imbild-anr" href="%1$s"><div class="rahmen r169">%6$s<div class="imbild"><p class="meta">%5$s%4$s</p><%2$s class="titel">%3$s</%2$s></div></div>%7$s</a></li>',
		esc_url( get_permalink( $post_id ) ),
		$ebene,
		tamil_titel( $post_id ),
		$datum,
		$kat ? '<span class="meta__rubrik">' . esc_html( $kat->name ) . '</span>' : '',
		tamil_bild(
			$post_id,
			array(
				'sizes' => '(min-width: 1024px) 380px, (min-width: 600px) 50vw, 100vw',
				'eager' => $sofort,
			)
		),
		'' !== $unter || $text ? '<div class="grafik__inhalt">' . ( '' !== $unter ? '<p class="grafik__orte">' . esc_html( $unter ) . '</p>' : '' ) . ( $text ? '<p class="grafik__text">' . tamil_text( wp_trim_words( tamil_standfirst( $post_id ), 28, ' …' ) ) . '</p>' : '' ) . '</div>' : ''
	);
}

/**
 * Bildkachel ohne Eintrag (Leerzustand in „Diese Woche“, Kino und Termine): Symbolbild der Rubrik, Titel, Satz, Ziel.
 */
function tamil_grafik_leer( string $titel, string $satz, string $url, string $rubrik = 'events', string $ebene = 'h3' ): string {
	$ebene = tamil_ebene( $ebene );
	return sprintf(
		'<li class="grafik grafik--leer"><a class="anr" href="%1$s"><div class="rahmen r169">%5$s</div><div class="grafik__inhalt"><%2$s class="titel">%3$s</%2$s><p class="grafik__orte">%4$s</p></div></a></li>',
		esc_url( $url ),
		$ebene,
		esc_html( $titel ),
		esc_html( $satz ),
		tamil_pool_img(
			$rubrik,
			array(
				'n'     => 1,
				'sizes' => '(min-width: 1024px) 380px, (min-width: 600px) 50vw, 100vw',
			)
		)
	);
}
