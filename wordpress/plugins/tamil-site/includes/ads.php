<?php
/**
 * Werbeplätze. Reihenfolge je Platz: gebuchte Anzeige (werbung.php) → Advanced-Ads-Platzierung → eigenes Banner-HTML → Eigenanzeige von Tamil.de
 * (Production, Event melden, Werben, WhatsApp-Kanal) → nichts. Ein Platz ohne Inhalt bleibt unsichtbar.
 *
 * Eigenanzeigen sind Bildbanner (Auftraggeber 17.11.: alles auf der Website hat ein Bild, auch jede Anzeige): ein
 * mitgeliefertes Foto (assets/img/anzeigen/, NACHWEIS.md) oder ein Bild aus der Mediathek. Ohne Bild keine Anzeige.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Die Werbeplätze mit Beschriftung für die Einstellungen: Name, Ort und Maße aus tamil_site_werbung_formate() (eine
 * Quelle für Tabelle, Einstellungen und Darstellung).
 *
 * @return array<string,string>
 */
function tamil_site_werbeplaetze(): array {
	$plaetze = array();
	foreach ( tamil_site_werbung_formate() as $platz => $f ) {
		$plaetze[ $platz ] = sprintf( '%1$s: %2$s (%3$s)', $f['name'], $f['wo'], tamil_site_werbung_masse_text( $platz ) );
	}
	return $plaetze;
}

/**
 * Eigenanzeigen (Vorlage → Beschriftung).
 *
 * @return array<string,string>
 */
function tamil_site_eigenanzeigen(): array {
	return array(
		''               => __( '– keine –', 'tamil-site' ),
		'production'     => __( 'Tamil.de Production: Live mit dir!', 'tamil-site' ),
		'event'          => __( 'Event melden: Dein Fest im Kalender', 'tamil-site' ),
		'werben'         => __( 'Werben auf Tamil.de', 'tamil-site' ),
		'whatsapp'       => __( 'WhatsApp-Kanal', 'tamil-site' ),
		'whatsapp-klein' => __( 'WhatsApp-Kanal, kurz (für 320×50)', 'tamil-site' ),
	);
}

/**
 * Einstellungen mit Standardwerten. Ohne Buchung zeigt jeder Platz eine Eigenanzeige; eigen_bild: je Bild einer
 * Eigenanzeige eine Mediathek-ID, die das mitgelieferte Standardbild ersetzt (0 = Standardbild).
 *
 * @return array{anzeigen:array<string,string>,advanced_ads:array<string,string>,eigen:array<string,string>,eigen_bild:array<string,int>,whatsapp_url:string}
 */
function tamil_site_settings(): array {
	$defaults = array(
		'anzeigen'     => array(),
		'advanced_ads' => array(),
		'eigen'        => array(
			'leaderboard' => 'production',
			'sidebar'     => 'event',
			'inarticle'   => 'whatsapp',
			'billboard'   => 'event',
			'footer'      => 'werben',
			'mobile'      => 'whatsapp-klein',
		),
		'eigen_bild'   => array(),
		'whatsapp_url' => 'https://whatsapp.com/channel/0029VaFIN43KWEKo3BGoE13t',
	);
	$stored   = get_option( 'tamil_site_settings', array() );
	$settings = array_merge( $defaults, is_array( $stored ) ? $stored : array() );
	// Eigenanzeigen, die es nicht mehr gibt (etwa nach einer Umbenennung), fallen auf den Standard zurück.
	foreach ( (array) $settings['eigen'] as $platz => $vorlage ) {
		if ( '' !== $vorlage && ! array_key_exists( (string) $vorlage, tamil_site_eigenanzeigen() ) ) {
			$settings['eigen'][ $platz ] = $defaults['eigen'][ $platz ] ?? '';
		}
	}
	$bilder = array();
	foreach ( array_keys( tamil_site_eigenanzeige_standardbilder() ) as $bild ) {
		$bilder[ $bild ] = absint( ( (array) $settings['eigen_bild'] )[ $bild ] ?? 0 );
	}
	$settings['eigen_bild'] = $bilder;
	return $settings;
}

function tamil_site_ico( string $name, string $cls = 'ico ico-sm' ): string {
	return sprintf( '<svg class="%1$s" aria-hidden="true"><use href="#i-%2$s"/></svg>', esc_attr( $cls ), esc_attr( $name ) );
}

/**
 * Mitgelieferte Standardbilder der Eigenanzeigen (assets/img/anzeigen/, Herkunft und Lizenz in NACHWEIS.md). Je Bild:
 * Datei in voller Breite (höchstens 1200 px) und in 600 px, Maße, Alternativtext, Nachweis für den Fuß der Seite
 * („zugeschnitten“: das Banner zeigt immer einen Ausschnitt), Dateiseite und Lizenz-URL (für verlinkte Nachweise),
 * Bildausschnitt (object-position) und die Seite, auf der die Schrift steht (links oder rechts im Bild).
 *
 * @return array<string,array{datei:string,klein:string,w:int,h:int,alt:string,nachweis:string,quelle:string,lizenz:string,fokus:string,seite:string}>
 */
function tamil_site_eigenanzeige_standardbilder(): array {
	$bilder = array(
		'production' => array(
			'datei'    => 'production.webp',
			'klein'    => 'production-600.webp',
			'w'        => 692,
			'h'        => 359,
			'alt'      => __( 'A.R. Rahman singt mit Mikrofon auf der Bühne eines Konzerts der Reihe „Live mit dir!“', 'tamil-site' ),
			'nachweis' => __( 'Foto: Archiv Tamil.de', 'tamil-site' ),
			'quelle'   => '',
			'lizenz'   => '',
			'fokus'    => '45% 30%',
			'seite'    => 'rechts',
		),
		'event'      => array(
			'datei'    => 'event.webp',
			'klein'    => 'event-600.webp',
			'w'        => 1200,
			'h'        => 930,
			'alt'      => __( 'Tempelfest am Sri-Kamadchi-Ampal-Tempel in Hamm: Besucher mit bunten Schirmen vor Tempelturm und Festwagen (Archivbild)', 'tamil-site' ),
			'nachweis' => __( 'Foto: Rainer Halama / Wikimedia Commons, CC BY-SA 2.5, zugeschnitten', 'tamil-site' ),
			'quelle'   => 'https://commons.wikimedia.org/wiki/File:Hamm_Tempelfest_2118.jpg',
			'lizenz'   => 'https://creativecommons.org/licenses/by-sa/2.5/',
			'fokus'    => '30% 62%',
			'seite'    => 'links',
		),
		'werben'     => array(
			'datei'    => 'werben.webp',
			'klein'    => 'werben-600.webp',
			'w'        => 1200,
			'h'        => 900,
			'alt'      => __( 'Fußgängerzone mit Geschäften und Passanten, die Gorkistraße in Berlin-Tegel (Symbolbild)', 'tamil-site' ),
			'nachweis' => __( 'Foto: Fridolin freudenfett / Wikimedia Commons, CC BY-SA 4.0, zugeschnitten', 'tamil-site' ),
			'quelle'   => 'https://commons.wikimedia.org/wiki/File:Tegel_Gorkistra%C3%9Fe_Fu%C3%9Fg%C3%A4ngerzone-001.JPG',
			'lizenz'   => 'https://creativecommons.org/licenses/by-sa/4.0/',
			'fokus'    => '50% 62%',
			'seite'    => 'links',
		),
		'whatsapp'   => array(
			'datei'    => 'whatsapp.webp',
			'klein'    => 'whatsapp-600.webp',
			'w'        => 1200,
			'h'        => 800,
			'alt'      => __( 'Hände mit einem Smartphone und einem Kaffeebecher (Symbolbild)', 'tamil-site' ),
			'nachweis' => __( 'Foto: Pixel.la / Wikimedia Commons, CC0, zugeschnitten', 'tamil-site' ),
			'quelle'   => 'https://commons.wikimedia.org/wiki/File:Hands-coffee-smartphone-technology_(23698591814).jpg',
			'lizenz'   => 'https://creativecommons.org/publicdomain/zero/1.0/',
			'fokus'    => '40% 45%',
			'seite'    => 'rechts',
		),
	);
	/**
	 * Standardbilder der Eigenanzeigen ändern (z. B. in Tests ein Bild entfernen).
	 *
	 * @param array $bilder Bild → Angaben.
	 */
	return (array) apply_filters( 'tamil_site_eigenanzeige_standardbilder', $bilder );
}

/**
 * Adresse einer veröffentlichten Seite (nach Slug) oder $ersatz.
 */
function tamil_site_seite_oder( string $slug, string $ersatz ): string {
	$seite = get_page_by_path( $slug, OBJECT, 'page' );
	return $seite instanceof WP_Post && 'publish' === $seite->post_status ? (string) get_permalink( $seite ) : $ersatz;
}

/**
 * Vorlagen der Eigenanzeigen: Ziel, Texte (Titel, ein Satz, Linktext; ohne Icon, Dachzeile, Gedankenstrich oder
 * Trennpunkte) und welches Bild. Eine Vorlage ohne Ziel (url leer) wird nicht gezeigt: „Live mit dir!“ braucht die
 * Seite „production“, sonst führte die Anzeige ins Leere.
 *
 * @return array<string,array{url:string,titel:string,satz:string,link:string,neu:bool,bild:string}>
 */
function tamil_site_eigenanzeige_vorlagen(): array {
	$wa      = tamil_site_settings()['whatsapp_url'];
	$einr    = function_exists( 'tamil_site_funktion_an' ) && tamil_site_funktion_an( 'einreichungen' ) ? tamil_site_seite_oder( 'einreichen', '' ) : '';
	$werben  = function_exists( 'tamil_site_funktion_an' ) && tamil_site_funktion_an( 'werbung' ) ? tamil_site_seite_oder( 'werben', '' ) : '';
	$kontakt = tamil_site_seite_oder( 'kontakt', home_url( '/kontakt/' ) );
	return array(
		'production'     => array(
			'url'   => tamil_site_seite_oder( 'production', '' ),
			'titel' => __( 'Live mit dir!', 'tamil-site' ),
			'satz'  => __( 'A.R. Rahman, Ilaiyaraaja, Anirudh und Santhosh Narayanan standen oder stehen mit Tamil.de Production auf deutschen Bühnen.', 'tamil-site' ),
			'link'  => __( 'Zur Konzertreihe', 'tamil-site' ),
			'neu'   => false,
			'bild'  => 'production',
		),
		'event'          => array(
			'url'   => '' !== $einr ? $einr : $kontakt . '#event-einreichen',
			'titel' => __( 'Dein Fest im Kalender.', 'tamil-site' ),
			'satz'  => __( 'Tempelfest, Konzert, Turnier: kostenlos melden, die Redaktion trägt es ein.', 'tamil-site' ),
			'link'  => __( 'Termin melden', 'tamil-site' ),
			'neu'   => false,
			'bild'  => 'event',
		),
		'werben'         => array(
			'url'   => '' !== $werben ? $werben : $kontakt . '#werben',
			'titel' => __( 'Werben auf Tamil.de', 'tamil-site' ),
			'satz'  => __( 'Eine Community in drei Ländern, sechs feste Werbeplätze. Mediadaten gibt es auf Anfrage.', 'tamil-site' ),
			'link'  => __( 'Werbeplätze ansehen', 'tamil-site' ),
			'neu'   => false,
			'bild'  => 'werben',
		),
		'whatsapp-klein' => array(
			'url'   => $wa,
			'titel' => __( 'Tamil.de auf WhatsApp', 'tamil-site' ),
			'satz'  => '',
			'link'  => __( 'Abonnieren', 'tamil-site' ),
			'neu'   => true,
			'bild'  => 'whatsapp',
		),
		'whatsapp'       => array(
			'url'   => $wa,
			'titel' => __( 'Kinostarts und Termine direkt aufs Handy.', 'tamil-site' ),
			'satz'  => __( 'Der Kanal von Tamil.de auf WhatsApp. Keine Gruppe, eure Nummern bleiben unsichtbar.', 'tamil-site' ),
			'link'  => __( 'Kanal öffnen', 'tamil-site' ),
			'neu'   => true,
			'bild'  => 'whatsapp',
		),
	);
}

/**
 * Bild einer Eigenanzeige: das in den Einstellungen gewählte Bild aus der Mediathek, sonst das mitgelieferte
 * Standardbild. Null, wenn keins von beiden da ist – dann wird die Anzeige nicht gezeigt (jede Anzeige hat ein Bild).
 *
 * @return array{src:string,srcset:string,w:int,h:int,alt:string,nachweis:string,quelle:string,lizenz:string,fokus:string,seite:string}|null
 */
function tamil_site_eigenanzeige_bild( string $bild ): ?array {
	$standard = tamil_site_eigenanzeige_standardbilder()[ $bild ] ?? null;
	$id       = (int) ( tamil_site_settings()['eigen_bild'][ $bild ] ?? 0 );
	if ( $id && wp_attachment_is_image( $id ) ) {
		$src = wp_get_attachment_image_src( $id, 'large' );
		if ( $src ) {
			$alt = trim( (string) get_post_meta( $id, '_wp_attachment_image_alt', true ) );
			$alt = '' !== $alt ? $alt : trim( (string) get_the_title( $id ) );
			return array(
				'src'      => (string) $src[0],
				'srcset'   => (string) wp_get_attachment_image_srcset( $id, 'large' ),
				'w'        => (int) $src[1],
				'h'        => (int) $src[2],
				'alt'      => $alt,
				'nachweis' => trim( (string) wp_get_attachment_caption( $id ) ),
				'quelle'   => '',
				'lizenz'   => '',
				'fokus'    => '50% 50%',
				'seite'    => $standard['seite'] ?? 'links',
			);
		}
	}
	if ( ! $standard || ! is_readable( TAMIL_SITE_DIR . 'assets/img/anzeigen/' . $standard['datei'] ) ) {
		return null;
	}
	$url    = TAMIL_SITE_URL . 'assets/img/anzeigen/';
	$srcset = $url . $standard['datei'] . ' ' . (int) $standard['w'] . 'w';
	if ( '' !== $standard['klein'] && is_readable( TAMIL_SITE_DIR . 'assets/img/anzeigen/' . $standard['klein'] ) ) {
		$srcset = $url . $standard['klein'] . ' 600w, ' . $srcset;
	}
	return array(
		'src'      => $url . $standard['datei'],
		'srcset'   => $srcset,
		'w'        => (int) $standard['w'],
		'h'        => (int) $standard['h'],
		'alt'      => (string) $standard['alt'],
		'nachweis' => (string) $standard['nachweis'],
		'quelle'   => (string) ( $standard['quelle'] ?? '' ),
		'lizenz'   => (string) ( $standard['lizenz'] ?? '' ),
		'fokus'    => (string) $standard['fokus'],
		'seite'    => (string) $standard['seite'],
	);
}

/**
 * Bildgrößen je Werbeplatz für sizes, aus den Formaten: ab der Grenze die Desktop-Breite, am Handy die Spaltenbreite,
 * dazwischen die Handy-Breite.
 */
function tamil_site_eigenanzeige_sizes( string $platz ): string {
	$f = tamil_site_werbung_formate()[ '' !== $platz ? $platz : 'leaderboard' ] ?? null;
	if ( ! $f ) {
		return '100vw';
	}
	if ( 'mobile' === $platz ) {
		return (int) $f['mobil'][0] . 'px';
	}
	$sizes = array();
	if ( (int) $f['ab'] && tamil_site_werbung_zwei_bilder( $platz ) ) {
		$sizes[] = sprintf( '(min-width: %1$dpx) %2$dpx', (int) $f['ab'], (int) $f['desktop'][0] );
	}
	$sizes[] = '(max-width: 599px) 100vw';
	$sizes[] = (int) $f['mobil'][0] . 'px';
	return implode( ', ', $sizes );
}

/**
 * Größen der Werbeflächen als CSS, erzeugt aus tamil_site_werbung_formate() (Prüfung 17.11., P1-8: Angabe und
 * Darstellung aus derselben Konfiguration). Gilt für Eigenanzeigen (.anzeige-wrap) und gebuchte Anzeigen
 * (.wb-anzeige); fremdes Banner-HTML behält die festen Flächen des Themes. Breite höchstens das Format, am Handy
 * (unter 600 px) die Spaltenbreite bis 20 % darüber; die Höhe folgt dem Seitenverhältnis.
 */
function tamil_site_anzeigen_formate_css(): string {
	$css   = '';
	$handy = '';
	foreach ( tamil_site_werbung_formate() as $platz => $f ) {
		$p           = '.ad.ad-' . sanitize_key( $platz );
		$flaeche     = $p . ' .flaeche.anzeige-wrap,' . $p . ' .flaeche.wb-anzeige';
		[ $mw, $mh ] = array_map( 'intval', $f['mobil'] );
		[ $dw, $dh ] = array_map( 'intval', $f['desktop'] );
		if ( 'mobile' === $platz ) {
			// Handy-Leiste: nur die Eigenanzeige (Raster aus anzeigen.css); gebuchte behalten die Leiste des Themes.
			$css .= sprintf( '%1$s .flaeche.anzeige-wrap{width:100%%;max-width:%2$dpx;height:auto;aspect-ratio:%2$d/%3$d}', $p, $mw, $mh );
			continue;
		}
		$css   .= sprintf( '%1$s{grid-template-columns:minmax(0,%2$dpx)}', $p, $mw );
		$css   .= sprintf( '%1$s{width:100%%;max-width:100%%;height:auto;aspect-ratio:%2$d/%3$d}', $flaeche, $mw, $mh );
		$handy .= sprintf( '%1$s{grid-template-columns:minmax(0,%2$dpx)}', $p, (int) round( $mw * 1.2 ) );
		if ( (int) $f['ab'] && tamil_site_werbung_zwei_bilder( $platz ) ) {
			$css .= sprintf( '@media (min-width:%1$dpx){%2$s{grid-template-columns:minmax(0,%3$dpx)}%4$s{aspect-ratio:%3$d/%5$d}}', (int) $f['ab'], $p, $dw, $flaeche, $dh );
		}
	}
	$css .= '.ad .flaeche.wb-anzeige a,.ad .flaeche.wb-anzeige picture{display:block}.ad .flaeche.wb-anzeige img{width:100%;height:auto}';
	return $css . '@media (max-width:599px){' . $handy . '}';
}

/**
 * HTML einer Eigenanzeige als Bildbanner (klar2): echtes Foto mit dunklem Verlauf, darin Titel, ein Satz und der
 * Linktext; Radius 0, kein Schatten, Gestaltung in assets/anzeigen.css. Leer, wenn die Vorlage unbekannt ist, kein
 * Ziel hat oder kein Bild – eine Eigenanzeige ohne Bild wird nicht gezeigt.
 *
 * @param string $vorlage Vorlage (tamil_site_eigenanzeigen()).
 * @param string $platz   Werbeplatz (für die Bildgrößen); leer = Leaderboard.
 */
function tamil_site_eigenanzeige_html( string $vorlage, string $platz = '' ): string {
	$v = tamil_site_eigenanzeige_vorlagen()[ $vorlage ] ?? null;
	if ( ! $v || '' === $v['url'] ) {
		return '';
	}
	$bild = tamil_site_eigenanzeige_bild( $v['bild'] );
	if ( ! $bild ) {
		return '';
	}
	$nachweis = '';
	if ( ! function_exists( 'tamil_nachweise' ) && '' !== $bild['nachweis'] ) {
		// Ohne das Theme Tamil.de sammelt kein Fuß die Bildnachweise: dann steht der Nachweis klein im Banner.
		$nachweis = '<span class="anzeige__nachweis">' . esc_html( $bild['nachweis'] ) . '</span>';
	}
	// Kein aria-label: Der Name des Links kommt aus dem sichtbaren Text (Titel, Satz, Linktext), danach der
	// Alternativtext des Bilds (axe label-content-name-mismatch, WCAG 2.5.3). Das Bild steht darum hinter dem Text.
	return sprintf(
		'<a class="flaeche anzeige-wrap" href="%1$s"%2$s><div class="anzeige a-%3$s anzeige--bild anzeige--%4$s">'
		. '<span class="text"><span class="claim">%5$s</span>%6$s<span class="cta">%7$s</span></span>'
		. '<img class="anzeige__bild" src="%8$s" srcset="%9$s" sizes="%10$s" width="%11$d" height="%12$d" alt="%13$s" loading="lazy" decoding="async" style="object-position: %14$s">'
		. '%15$s</div></a>',
		esc_url( $v['url'] ),
		$v['neu'] ? ' target="_blank" rel="noopener"' : '',
		esc_attr( $vorlage ),
		'rechts' === $bild['seite'] ? 'rechts' : 'links',
		esc_html( $v['titel'] ),
		'' !== $v['satz'] ? '<span class="sub">' . esc_html( $v['satz'] ) . '</span>' : '',
		esc_html( $v['link'] ),
		esc_url( $bild['src'] ),
		esc_attr( $bild['srcset'] ),
		esc_attr( tamil_site_eigenanzeige_sizes( $platz ) ),
		(int) $bild['w'],
		(int) $bild['h'],
		esc_attr( $bild['alt'] ),
		esc_attr( (string) preg_replace( '/[^0-9% .a-z]/', '', $bild['fokus'] ) ),
		$nachweis
	);
}

/**
 * Einen Bildnachweis an das Theme melden: als Text an tamil_nachweise() (Liste im Fuß) und mit Dateiseite und
 * Lizenz-URL an die Aktion tamil_site_bildnachweis (für verlinkte Nachweise, Prüfung 17.11. P0-1 im Theme).
 *
 * @param string $text   Nachweis, z. B. „Foto: … / Wikimedia Commons, CC BY-SA 4.0, zugeschnitten“.
 * @param string $quelle Dateiseite (leer, wenn unbekannt).
 * @param string $lizenz Lizenz-URL (leer, wenn unbekannt).
 */
function tamil_site_nachweis_melden( string $text, string $quelle = '', string $lizenz = '' ): void {
	if ( '' === trim( $text ) ) {
		return;
	}
	if ( function_exists( 'tamil_nachweise' ) ) {
		tamil_nachweise( $text );
	}
	/**
	 * Bildnachweis einer vom Plugin gezeigten Abbildung (Eigenanzeige, Symbolbild im Verzeichnis).
	 *
	 * @param string $text   Nachweis als Text.
	 * @param string $quelle Dateiseite (leer, wenn unbekannt).
	 * @param string $lizenz Lizenz-URL (leer, wenn unbekannt).
	 */
	do_action( 'tamil_site_bildnachweis', $text, $quelle, $lizenz );
}

/**
 * Bildnachweis einer Eigenanzeige für den Fuß der Seite merken (Theme: tamil_nachweise()). Gemerkt wird nur, was
 * auch gezeigt wird.
 */
function tamil_site_eigenanzeige_nachweis_merken( string $vorlage ): void {
	$v = tamil_site_eigenanzeige_vorlagen()[ $vorlage ] ?? null;
	if ( ! $v || '' === $v['url'] ) {
		return;
	}
	$bild = tamil_site_eigenanzeige_bild( $v['bild'] );
	if ( $bild ) {
		tamil_site_nachweis_melden( $bild['nachweis'], $bild['quelle'], $bild['lizenz'] );
	}
}

/**
 * Lädt dieses HTML etwas von fremden Hosts? Gezählt wird, was der Browser beim Aufbau lädt: src, srcset, data,
 * poster, href von <link>, url(…) in Stilen – und jedes <script> und <iframe> (Skripte können beliebig nachladen).
 * Ein gewöhnlicher Link (<a href>) lädt nichts und zählt nicht.
 */
function tamil_site_fremde_inhalte( string $html ): bool {
	if ( preg_match( '/<(script|iframe|object|embed)\b/i', $html ) ) {
		return true;
	}
	$eigen    = strtolower( (string) wp_parse_url( home_url(), PHP_URL_HOST ) );
	$adressen = array();
	if ( preg_match_all( '/\s(?:src|data|poster)\s*=\s*["\']?\s*([^"\'\s>]+)/i', $html, $m ) ) {
		$adressen = array_merge( $adressen, $m[1] );
	}
	if ( preg_match_all( '/\ssrcset\s*=\s*["\']([^"\']+)/i', $html, $m ) ) {
		foreach ( $m[1] as $srcset ) {
			foreach ( explode( ',', $srcset ) as $teil ) {
				$adressen[] = strtok( trim( $teil ), ' ' );
			}
		}
	}
	if ( preg_match_all( '/<link\b[^>]*\shref\s*=\s*["\']?\s*([^"\'\s>]+)/i', $html, $m ) ) {
		$adressen = array_merge( $adressen, $m[1] );
	}
	if ( preg_match_all( '/url\(\s*["\']?([^"\')]+)/i', $html, $m ) ) {
		$adressen = array_merge( $adressen, $m[1] );
	}
	foreach ( $adressen as $adresse ) {
		$adresse = html_entity_decode( trim( (string) $adresse ), ENT_QUOTES, 'UTF-8' );
		if ( ! preg_match( '~^(?:[a-z][a-z0-9+.-]*:)?//~i', $adresse ) ) {
			continue; // relativ oder data: – bleibt auf der eigenen Website
		}
		$host = strtolower( (string) wp_parse_url( ( str_starts_with( $adresse, '//' ) ? 'https:' : '' ) . $adresse, PHP_URL_HOST ) );
		if ( '' === $host || $host !== $eigen ) {
			return true;
		}
	}
	return false;
}

/**
 * Fremdes Werbe-HTML erst nach Zustimmung: Ist der Schalter „zustimmung“ an und lädt der Inhalt etwas von fremden
 * Hosts, steht er inaktiv in einem <template>; consent.js setzt ihn nach Zustimmung zu „externe_medien“ ein. Bis
 * dahin zeigt der Platz die Eigenanzeige (oder nichts).
 *
 * @param string $html  Werbe-HTML.
 * @param string $platz Werbeplatz.
 */
function tamil_site_anzeige_fremd( string $html, string $platz ): string {
	if ( ! tamil_site_funktion_an( 'zustimmung' ) || ! tamil_site_fremde_inhalte( $html ) ) {
		return '<div class="flaeche">' . $html . '</div>';
	}
	$settings = tamil_site_settings();
	$vorlage  = (string) ( $settings['eigen'][ $platz ] ?? '' );
	$ersatz   = tamil_site_eigenanzeige_html( $vorlage, $platz );
	if ( '' !== $ersatz ) {
		tamil_site_eigenanzeige_nachweis_merken( $vorlage );
	}
	return '<div class="tz-anzeige" data-tz-platz>' . $ersatz . '<template data-zustimmung="externe_medien"><div class="flaeche">' . $html . '</div></template></div>';
}

/**
 * Inhalt eines Werbeplatzes ohne Rahmen. Zweiter Rückgabewert: true, wenn es eine Eigenanzeige ist; dritter: ihre
 * Vorlage (sonst leer).
 *
 * @return array{0:string,1:bool,2:string}
 */
function tamil_site_anzeige_inhalt( string $platz ): array {
	// Eine gebuchte, heute aktive Anzeige (Werbebuchung F3) geht allem anderen vor; „aktiv“ entscheidet werbung.php.
	$gebucht = function_exists( 'tamil_site_werbung_ausliefern' ) ? tamil_site_werbung_ausliefern( $platz ) : '';
	if ( '' !== $gebucht ) {
		return array( $gebucht, false, '' );
	}
	$settings  = tamil_site_settings();
	$placement = (string) ( $settings['advanced_ads'][ $platz ] ?? '' );
	if ( $placement && function_exists( 'get_the_ad_placement' ) ) {
		$html = (string) get_the_ad_placement( $placement );
		if ( '' !== trim( $html ) ) {
			return array( tamil_site_anzeige_fremd( $html, $platz ), false, '' );
		}
	}
	$html = trim( (string) ( $settings['anzeigen'][ $platz ] ?? '' ) );
	if ( '' !== $html ) {
		return array( tamil_site_anzeige_fremd( $html, $platz ), false, '' );
	}
	$vorlage = (string) ( $settings['eigen'][ $platz ] ?? '' );
	// Nie Werbung für die Seite, auf der man gerade ist („Werben auf Tamil.de“ auf /werben/)
	$ziel = (string) ( tamil_site_eigenanzeige_vorlagen()[ $vorlage ]['url'] ?? '' );
	if ( '' !== $ziel && tamil_site_ist_aktuelle_seite( $ziel ) ) {
		return array( '', false, '' );
	}
	$eigen = tamil_site_eigenanzeige_html( $vorlage, $platz );
	return array( $eigen, '' !== $eigen, '' !== $eigen ? $vorlage : '' );
}

/**
 * Führt eine Adresse auf die gerade angezeigte Seite (ohne Anker und Abfrage)?
 */
function tamil_site_ist_aktuelle_seite( string $url ): bool {
	if ( is_admin() || ! did_action( 'wp' ) ) {
		return false;
	}
	$pfad  = static fn( string $u ): string => untrailingslashit( (string) wp_parse_url( $u, PHP_URL_PATH ) );
	$jetzt = $pfad( home_url( add_query_arg( array(), $GLOBALS['wp']->request ?? '' ) ) );
	return '' !== $pfad( $url ) && $pfad( $url ) === $jetzt && false === strpos( $url, '#' );
}

/**
 * Seiten ohne jede Anzeige: Impressum und Datenschutz (Q2-10).
 */
function tamil_site_seite_ohne_anzeigen(): bool {
	if ( ! is_page() ) {
		return false;
	}
	$id = (int) get_queried_object_id();
	if ( $id && (int) get_option( 'wp_page_for_privacy_policy' ) === $id ) {
		return true;
	}
	$seite = get_post( $id );
	return $seite instanceof WP_Post && in_array( $seite->post_name, array( 'impressum', 'datenschutz', 'datenschutzerklaerung' ), true );
}

/**
 * Eigenanzeigen dieser Seite, je Platz (für die Regel „nie zwei Hausanzeigen direkt hintereinander“).
 *
 * @return array<string,bool>
 */
function tamil_site_eigenanzeige_gezeigt( string $platz = '', bool $eigen = false ): array {
	static $gezeigt = array();
	if ( '' !== $platz ) {
		$gezeigt[ $platz ] = $eigen;
	}
	return $gezeigt;
}

/**
 * Plätze, die auf dieser Seite schon ausgegeben wurden (oder mit $platz: merken).
 *
 * @return array<int,string>
 */
function tamil_site_anzeige_gezeigt( string $platz = '' ): array {
	static $gezeigt = array();
	if ( '' !== $platz && ! in_array( $platz, $gezeigt, true ) ) {
		$gezeigt[] = $platz;
	}
	return $gezeigt;
}

/**
 * Ab so vielen Absätzen gilt ein Beitrag als lang: Erst dann steht eine Anzeige im Text (Prüfung 21.11., N-06).
 */
define( 'TAMIL_SITE_ARTIKEL_LANG_AB', 5 );

/**
 * Absätze mit Text in einem Beitragsinhalt (leere Absätze und die Quellenzeile zählen nicht).
 */
function tamil_site_artikel_absaetze( string $inhalt ): int {
	if ( ! str_contains( $inhalt, '</p>' ) ) {
		$inhalt = wpautop( $inhalt );
	}
	preg_match_all( '#<p\b([^>]*)>(.*?)</p>#is', $inhalt, $treffer, PREG_SET_ORDER );
	$zahl = 0;
	foreach ( $treffer as $p ) {
		if ( ! str_contains( $p[1], 'quelle' ) && '' !== trim( html_entity_decode( wp_strip_all_tags( $p[2] ) ), " \t\n\r\0\x0B\u{a0}" ) ) {
			++$zahl;
		}
	}
	return $zahl;
}

/**
 * Welche automatisch gesetzten Werbeplätze ein Beitrag mit so vielen Absätzen zeigt (N-06). Lange Beiträge: alle,
 * die Anzeige im Text nach dem zweiten Absatz eingeschlossen. Kurze Beiträge: keine Anzeige im Text und kein Fuß-Platz,
 * also in jeder Breite höchstens zwei Flächen (am Handy Leaderboard und Handy-Leiste, ab 768 px nur das Leaderboard,
 * ab 1024 px Half Page und Leaderboard).
 *
 * @return string[]
 */
function tamil_site_artikel_plaetze( int $absaetze ): array {
	$alle = array_keys( tamil_site_werbung_formate() );
	if ( $absaetze >= TAMIL_SITE_ARTIKEL_LANG_AB ) {
		return $alle;
	}
	return array_values( array_diff( $alle, array( 'inarticle', 'footer' ) ) );
}

/**
 * Darf der Platz auf dieser Seite automatisch stehen? Nur Beiträge sind eingeschränkt.
 */
function tamil_site_artikel_platz_erlaubt( string $platz ): bool {
	if ( ! is_singular( 'post' ) ) {
		return true;
	}
	$post = get_queried_object();
	if ( ! $post instanceof WP_Post ) {
		return true;
	}
	static $absaetze = array();
	if ( ! isset( $absaetze[ $post->ID ] ) ) {
		$absaetze[ $post->ID ] = tamil_site_artikel_absaetze( (string) $post->post_content );
	}
	return in_array( $platz, tamil_site_artikel_plaetze( $absaetze[ $post->ID ] ), true );
}

/**
 * Fertiger Werbeplatz mit Label „Anzeige“; leer, wenn der Platz nichts zeigt. Eigenanzeigen tragen zusätzlich die
 * Klassen ad-anzeige und ad-bild; ihr Bildnachweis landet im Fuß der Seite. Auf Impressum und Datenschutz gibt es
 * keine Anzeigen. Mit $direkt_nach nennt das Theme den Platz, der unmittelbar davor steht: war dort schon eine
 * Eigenanzeige, folgt keine zweite direkt darauf. Auf Beiträgen gilt die Regel aus tamil_site_artikel_plaetze(); ein
 * von der Redaktion per [tamil_anzeige] gesetzter Platz ($redaktion) ist davon ausgenommen.
 */
function tamil_site_anzeige( string $platz, bool $ausgeben = true, string $direkt_nach = '', bool $redaktion = false ): string {
	$platz = sanitize_key( $platz );
	if ( ! array_key_exists( $platz, tamil_site_werbeplaetze() ) || tamil_site_seite_ohne_anzeigen() ) {
		return '';
	}
	if ( ! $redaktion && ! tamil_site_artikel_platz_erlaubt( $platz ) ) {
		return '';
	}
	[ $inhalt, $eigen, $vorlage ] = tamil_site_anzeige_inhalt( $platz );
	if ( $eigen && '' !== $direkt_nach && ! empty( tamil_site_eigenanzeige_gezeigt()[ sanitize_key( $direkt_nach ) ] ) ) {
		return '';
	}
	/**
	 * Inhalt eines Werbeplatzes ändern oder ersetzen.
	 *
	 * @param string $inhalt HTML (Fläche).
	 * @param string $platz  Werbeplatz.
	 */
	$inhalt = (string) apply_filters( 'tamil_site_anzeige', $inhalt, $platz );
	if ( '' === trim( $inhalt ) ) {
		return '';
	}
	tamil_site_anzeige_gezeigt( $platz );
	tamil_site_eigenanzeige_gezeigt( $platz, (bool) $eigen );
	if ( $eigen ) {
		tamil_site_eigenanzeige_nachweis_merken( $vorlage );
	}
	$mobil = 'mobile' === $platz;
	// Ein eigener, je Platz anders benannter Bereich (aside): Werbung steht auch außerhalb von main und footer (Fuß,
	// Handy-Leiste) in einem Landmark (axe region) und lässt sich mit dem Screenreader überspringen.
	$out = sprintf(
		'<aside class="ad ad-%1$s%2$s"%3$s data-platz="%1$s" aria-label="%7$s"><span class="ad-label">%4$s</span>%5$s%6$s</aside>',
		esc_attr( $platz ),
		$eigen ? ' ad-anzeige ad-bild' : '',
		$mobil ? ' id="ad-mobile"' : '',
		esc_html__( 'Anzeige', 'tamil-site' ),
		$inhalt, // Banner-Code aus den Einstellungen (nur Administratoren), Advanced Ads oder die Vorlagen oben.
		$mobil ? '<button type="button" class="schliessen" aria-label="' . esc_attr__( 'Werbung schließen', 'tamil-site' ) . '">×</button>' : '',
		/* translators: %s: Name des Werbeplatzes */
		esc_attr( sprintf( __( 'Anzeige: %s', 'tamil-site' ), tamil_site_werbung_formate()[ $platz ]['name'] ?? $platz ) )
	);
	if ( $ausgeben ) {
		echo $out; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
	}
	return $out;
}

/**
 * Bildnachweise der Werbeplätze, die erst im Fuß der Seite stehen (Fuß, Handy-Leiste, Leaderboard als Rückfall),
 * vorab merken: Das Theme liest die gesammelten Nachweise am Anfang von footer.php, bevor diese Plätze ausgegeben
 * werden. Läuft beim Laden des Fußes (get_footer).
 */
function tamil_site_anzeige_nachweise_vormerken(): void {
	if ( ! function_exists( 'tamil_nachweise' ) || is_admin() ) {
		return;
	}
	foreach ( array( 'leaderboard', 'footer', 'mobile' ) as $platz ) {
		if ( in_array( $platz, tamil_site_anzeige_gezeigt(), true ) ) {
			continue;
		}
		[ , $eigen, $vorlage ] = tamil_site_anzeige_inhalt( $platz );
		if ( $eigen ) {
			tamil_site_eigenanzeige_nachweis_merken( $vorlage );
		}
	}
}
add_action( 'get_footer', 'tamil_site_anzeige_nachweise_vormerken' );

/**
 * Gestaltung der Bildbanner (klar2, mit den Farben des Themes und eigenem Rückfall) auf jeder öffentlichen Seite: Die
 * Werbeplätze stehen im Kopf, im Text und im Fuß, und spät geladenes CSS ließe das Banner springen.
 */
function tamil_site_anzeigen_css(): void {
	$css = 'assets/anzeigen.css';
	wp_enqueue_style( 'tamil-site-anzeigen', TAMIL_SITE_URL . $css, array(), TAMIL_SITE_VERSION . '.' . filemtime( TAMIL_SITE_DIR . $css ) );
	wp_add_inline_style( 'tamil-site-anzeigen', tamil_site_anzeigen_formate_css() );
}
add_action( 'wp_enqueue_scripts', 'tamil_site_anzeigen_css', 20 );

/**
 * [tamil_anzeige platz="leaderboard"]
 */
function tamil_site_shortcode_anzeige( $atts ): string {
	$atts = shortcode_atts( array( 'platz' => 'inarticle' ), $atts, 'tamil_anzeige' );
	return tamil_site_anzeige( (string) $atts['platz'], false, '', true );
}
