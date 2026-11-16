<?php
/**
 * Anreißer in klar2: Bild im Rahmen, Dachzeile „Rubrik | Datum“, Titel, Vorspann. Jeder Anreißer ist ein einziger
 * Link (a.anr) um Bild und Text; Bilder füllen ihren Rahmen (object-fit: cover), Nachweise sammelt der Fuß.
 *
 * Bausteine: tamil_bild(), tamil_meta(), tamil_anr_imbild() (Titel im Bild), tamil_anr_stueck() (Nebenstück),
 * tamil_anr_zeile() (Meldung, Listenzeile), tamil_kacheln() (Rubrikkacheln), tamil_grafik_kino(),
 * tamil_grafik_termin() (gestaltete Kacheln ohne Foto auf Dunkel).
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
 * Beitragsbild als <img> für einen Rahmen; merkt den Nachweis für den Fuß. Leer ohne zeigbares Bild.
 *
 * @param array<string,mixed> $opt {
 *     @type string $size  Bildgröße (Standard „large“, ungeschnitten; der Rahmen schneidet).
 *     @type string $sizes sizes-Angabe für srcset.
 *     @type bool   $eager Sofort laden (erster Bildschirm).
 *     @type string $klasse Klasse des Bilds.
 * }
 */
function tamil_bild( int $post_id, array $opt = array() ): string {
	if ( ! tamil_bild_zeigbar( $post_id ) ) {
		return '';
	}
	$attr = array(
		'alt'      => tamil_bild_alt( $post_id ),
		'decoding' => 'async',
	);
	if ( ! empty( $opt['eager'] ) ) {
		$attr['loading']       = 'eager';
		$attr['fetchpriority'] = 'high';
	} else {
		$attr['loading'] = 'lazy';
	}
	if ( ! empty( $opt['sizes'] ) ) {
		$attr['sizes'] = (string) $opt['sizes'];
	}
	if ( ! empty( $opt['klasse'] ) ) {
		$attr['class'] = (string) $opt['klasse'];
	}
	$img = (string) get_the_post_thumbnail( $post_id, (string) ( $opt['size'] ?? 'large' ), $attr );
	if ( '' !== $img ) {
		tamil_nachweise( str_replace( ' · ', ', ', tamil_bildnachweis( $post_id ) ) );
	}
	return $img;
}

/**
 * Rubrikfoto als <img> (Rubrikkacheln und Seitenköpfe ohne eigenes Foto); merkt den Nachweis.
 *
 * @param array<string,mixed> $opt { @type bool $alt Alternativtext setzen, @type bool $eager. }
 */
function tamil_rubrikfoto_img( string $slug, array $opt = array() ): string {
	$f = tamil_rubrikfoto( $slug );
	tamil_nachweise( __( 'Archivbild der Rubrik.', 'tamil' ) . ' ' . $f['nachweis'] );
	return sprintf(
		'<img src="%1$s" width="%2$d" height="%3$d" alt="%4$s" decoding="async" %5$s>',
		esc_url( TAMIL_THEME_URI . '/assets/img/rubrik/' . $f['datei'] ),
		(int) $f['w'],
		(int) $f['h'],
		esc_attr( ! empty( $opt['alt'] ) ? $f['alt'] : '' ),
		! empty( $opt['eager'] ) ? 'loading="eager" fetchpriority="high"' : 'loading="lazy"'
	);
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
 * Bild mit Titel im Bild (Aufmacher, große Kacheln in „Diese Woche“ und „Küche“). Ohne zeigbares Bild leer.
 *
 * @param array<string,mixed> $opt {
 *     @type string $klasse   Klassen des <article> (z. B. „aufmacher“, „kachel kachel--gross“).
 *     @type string $rahmen   Formatklasse des Rahmens (r43, r169, r83 oder leer, dann setzt das CSS das Format).
 *     @type string $ebene    h2 oder h3.
 *     @type bool   $vorspann Vorspann unter dem Bild.
 *     @type bool   $unter    Titel unter statt im Bild (Gesichter frei lassen).
 *     @type string $sizes, @type bool $eager.
 * }
 */
function tamil_anr_imbild( int $post_id, array $opt = array() ): string {
	$img = tamil_bild(
		$post_id,
		array(
			'sizes' => $opt['sizes'] ?? '',
			'eager' => ! empty( $opt['eager'] ),
		)
	);
	if ( '' === $img ) {
		return '';
	}
	$ebene = tamil_ebene( (string) ( $opt['ebene'] ?? 'h3' ) );
	$text  = tamil_meta( $post_id ) . sprintf( '<%1$s class="titel">%2$s</%1$s>', $ebene, tamil_titel( $post_id ) );
	$unter = ! empty( $opt['unter'] );
	$html  = '<article class="' . esc_attr( (string) ( $opt['klasse'] ?? 'kachel' ) ) . '">';
	$html .= '<a class="anr' . ( $unter ? '' : ' imbild-anr' ) . '" href="' . esc_url( get_permalink( $post_id ) ) . '">';
	$html .= '<div class="rahmen' . ( ! empty( $opt['rahmen'] ) ? ' ' . esc_attr( (string) $opt['rahmen'] ) : '' ) . '">' . $img;
	$html .= $unter ? '</div><div class="kachel__unter">' . $text . '</div>' : '<div class="imbild">' . $text . '</div></div>';
	if ( ! empty( $opt['vorspann'] ) ) {
		$html .= '<p class="vorspann">' . tamil_text( tamil_saetze( tamil_standfirst( $post_id ), 2 ) ) . '</p>';
	}
	return $html . '</a></article>';
}

/**
 * Nebenstück: Bild 16:9, Dachzeile, Titel, Vorspann (am Handy Bild links, am Desktop Bild über dem Text).
 *
 * @param array<string,mixed> $opt { @type string $ebene, @type string $sizes, @type string $klasse, @type bool $rubrik. }
 */
function tamil_anr_stueck( int $post_id, array $opt = array() ): string {
	$img   = tamil_bild( $post_id, array( 'sizes' => $opt['sizes'] ?? '(min-width: 1024px) 290px, (min-width: 600px) 200px, 112px' ) );
	$ebene = tamil_ebene( (string) ( $opt['ebene'] ?? 'h3' ) );
	return sprintf(
		'<article class="%1$s"><a class="anr" href="%2$s">%3$s<div class="stueck__text">%4$s<%5$s class="titel">%6$s</%5$s><p class="vorspann">%7$s</p></div></a></article>',
		esc_attr( (string) ( $opt['klasse'] ?? 'stueck' ) . ( '' === $img ? ' ohne-bild' : '' ) ),
		esc_url( get_permalink( $post_id ) ),
		'' !== $img ? '<div class="rahmen r169">' . $img . '</div>' : '',
		tamil_meta( $post_id, array( 'rubrik' => $opt['rubrik'] ?? true ) ),
		$ebene,
		tamil_titel( $post_id ),
		tamil_text( wp_trim_words( tamil_standfirst( $post_id ), 26, ' …' ) )
	);
}

/**
 * Zeile einer Liste: Text links, kleines Bild 16:9 rechts (Meldungen) oder links (große Listen). Ohne Bild nur Text.
 *
 * @param array<string,mixed> $opt {
 *     @type string $klasse   „meldung“ (Standard) oder „zeile“.
 *     @type string $ebene    h2 oder h3.
 *     @type bool   $vorspann Vorspann zeigen.
 *     @type bool   $rubrik   Rubrik in der Dachzeile.
 *     @type int    $ts       anderer Zeitpunkt für die Dachzeile (Termine).
 *     @type string $sizes.
 * }
 */
function tamil_anr_zeile( int $post_id, array $opt = array() ): string {
	$klasse = (string) ( $opt['klasse'] ?? 'meldung' );
	$img    = tamil_bild( $post_id, array( 'sizes' => $opt['sizes'] ?? '(min-width: 600px) 240px, 96px' ) );
	$ebene  = tamil_ebene( (string) ( $opt['ebene'] ?? 'h3' ) );
	$meta   = array( 'rubrik' => $opt['rubrik'] ?? true );
	if ( ! empty( $opt['ts'] ) ) {
		$meta['ts'] = (int) $opt['ts'];
	}
	return sprintf(
		'<li class="%1$s"><a class="anr" href="%2$s"><div class="%3$s__text">%4$s<%5$s class="titel">%6$s</%5$s>%7$s</div>%8$s</a></li>',
		esc_attr( $klasse . ( '' === $img ? ' ohne-bild' : '' ) ),
		esc_url( get_permalink( $post_id ) ),
		esc_attr( $klasse ),
		tamil_meta( $post_id, $meta ),
		$ebene,
		tamil_titel( $post_id ),
		! empty( $opt['vorspann'] ) ? '<p class="vorspann">' . tamil_text( wp_trim_words( tamil_standfirst( $post_id ), 30, ' …' ) ) . '</p>' : '',
		'' !== $img ? '<div class="rahmen r169">' . $img . '</div>' : ''
	);
}

/**
 * Liste von Zeilen (Rubrik, Suche, Archive, Weiterlesen).
 *
 * @param int[]               $ids Beiträge.
 * @param array<string,mixed> $opt wie tamil_anr_zeile(), dazu @type string $liste Klasse der Liste.
 */
function tamil_zeilen( array $ids, array $opt = array() ): string {
	$opt  = array_merge(
		array(
			'klasse'   => 'zeile',
			'vorspann' => true,
			'liste'    => 'liste',
		),
		$opt
	);
	$html = '<ul class="' . esc_attr( (string) $opt['liste'] ) . '">';
	foreach ( $ids as $id ) {
		$html .= tamil_anr_zeile( (int) $id, $opt );
	}
	return $html . '</ul>';
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
		$img = $k['bild'] ? tamil_bild( (int) $k['bild'], array( 'sizes' => '(min-width: 1024px) 160px, 160px' ) ) : '';
		if ( '' === $img ) {
			$img = tamil_rubrikfoto_img( $k['slug'] );
		} else {
			$img = (string) preg_replace( '/ alt="[^"]*"/', ' alt=""', $img, 1 ); // der Name steht im Bild
		}
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
 * Gestaltete Kachel „Im Kino“ (Fläche auf Dunkel): Film, Zahl der Kinos, Städte.
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
	return sprintf(
		'<li class="grafik" data-grafik="kino"><a class="anr" href="%1$s"><%2$s class="titel">%3$s</%2$s><p class="grafik__zahl">%4$s</p>%5$s</a></li>',
		esc_url( $f['link'] ),
		$ebene,
		esc_html( $f['film'] ),
		esc_html( $zahl ),
		$f['staedte'] ? '<p class="grafik__orte">' . esc_html( tamil_staedte_kurz( $f['staedte'] ) ) . '</p>' : ''
	);
}

/**
 * Gestaltete Kachel „Termin“ (Fläche auf Dunkel): Titel, Datum als größte Angabe, Ort und Veranstalter, Vorspann.
 */
function tamil_grafik_termin( int $post_id, string $ebene = 'h3', bool $text = true ): string {
	$e = function_exists( 'tamil_site_event' ) ? tamil_site_event( $post_id ) : array();
	if ( ! $e ) {
		return '';
	}
	$start = date_create_immutable( (string) $e['datum'], wp_timezone() );
	$titel = get_the_title( $post_id );
	$orte  = array_filter(
		array(
			tamil_ort_kurz( (string) $e['ort'] ),
			tamil_wer_kurz( (string) $e['veranstalter'], $titel, (string) $e['ort'] ),
		)
	);
	$ebene = tamil_ebene( $ebene );
	return sprintf(
		'<li class="grafik" data-grafik="termin"><a class="anr" href="%1$s"><%2$s class="titel">%3$s</%2$s><p class="grafik__zahl">%4$s</p>%5$s%6$s</a></li>',
		esc_url( get_permalink( $post_id ) ),
		$ebene,
		tamil_titel( $post_id ),
		$start ? '<time datetime="' . esc_attr( $start->format( 'Y-m-d' ) ) . '">' . esc_html( tamil_termin_text( (string) $e['datum'], (string) $e['ende'] ) ) . '</time>' : '',
		$orte ? '<p class="grafik__orte">' . esc_html( implode( ', ', $orte ) ) . '</p>' : '',
		$text ? '<p class="grafik__text">' . tamil_text( wp_trim_words( tamil_standfirst( $post_id ), 28, ' …' ) ) . '</p>' : ''
	);
}

/**
 * Gestaltete Kachel ohne Eintrag (Leerzustand in „Diese Woche“): Titel, Satz, Ziel.
 */
function tamil_grafik_leer( string $titel, string $satz, string $url, string $ebene = 'h3' ): string {
	$ebene = tamil_ebene( $ebene );
	return sprintf(
		'<li class="grafik grafik--leer"><a class="anr" href="%1$s"><%2$s class="titel">%3$s</%2$s><p class="grafik__orte">%4$s</p></a></li>',
		esc_url( $url ),
		$ebene,
		esc_html( $titel ),
		esc_html( $satz )
	);
}
