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
 * Die Werbeplätze des Designs (Nummern wie im Angebot; Billboard ist die In-Article-Fläche der Startseite).
 *
 * @return array<string,string>
 */
function tamil_site_werbeplaetze(): array {
	return array(
		'leaderboard' => __( '01 Leaderboard unter der Navigation (728×90 / 320×50)', 'tamil-site' ),
		'sidebar'     => __( '02 Half Page in der Seitenspalte (300×600)', 'tamil-site' ),
		'inarticle'   => __( '03 Im Artikel nach dem zweiten Absatz (728×90 / 300×250)', 'tamil-site' ),
		'billboard'   => __( '03 Startseite zwischen den Rubriken (970×250 / 300×250)', 'tamil-site' ),
		'footer'      => __( '04 Über dem Footer (728×90 / 320×100)', 'tamil-site' ),
		'mobile'      => __( '05 Mobil, fixiert am unteren Rand (320×50)', 'tamil-site' ),
	);
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
 * Datei in voller Breite (höchstens 1200 px) und in 600 px, Maße, Alternativtext, Nachweis für den Fuß der Seite,
 * Bildausschnitt (object-position) und die Seite, auf der die Schrift steht (links oder rechts im Bild).
 *
 * @return array<string,array{datei:string,klein:string,w:int,h:int,alt:string,nachweis:string,fokus:string,seite:string}>
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
			'fokus'    => '45% 30%',
			'seite'    => 'rechts',
		),
		'event'      => array(
			'datei'    => 'event.webp',
			'klein'    => 'event-600.webp',
			'w'        => 1200,
			'h'        => 930,
			'alt'      => __( 'Tempelfest am Sri-Kamadchi-Ampal-Tempel in Hamm: Besucher mit bunten Schirmen vor Tempelturm und Festwagen (Archivbild)', 'tamil-site' ),
			'nachweis' => __( 'Foto: Rainer Halama / Wikimedia Commons, CC BY-SA 2.5', 'tamil-site' ),
			'fokus'    => '30% 62%',
			'seite'    => 'links',
		),
		'werben'     => array(
			'datei'    => 'werben.webp',
			'klein'    => 'werben-600.webp',
			'w'        => 1200,
			'h'        => 900,
			'alt'      => __( 'Fußgängerzone mit Geschäften und Passanten, die Gorkistraße in Berlin-Tegel (Symbolbild)', 'tamil-site' ),
			'nachweis' => __( 'Foto: Fridolin freudenfett / Wikimedia Commons, CC BY-SA 4.0', 'tamil-site' ),
			'fokus'    => '50% 62%',
			'seite'    => 'links',
		),
		'whatsapp'   => array(
			'datei'    => 'whatsapp.webp',
			'klein'    => 'whatsapp-600.webp',
			'w'        => 1200,
			'h'        => 800,
			'alt'      => __( 'Hände mit einem Smartphone und einem Kaffeebecher (Symbolbild)', 'tamil-site' ),
			'nachweis' => __( 'Foto: Pixel.la / Wikimedia Commons, CC0', 'tamil-site' ),
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
 * @return array<string,array{url:string,label:string,titel:string,satz:string,link:string,neu:bool,bild:string}>
 */
function tamil_site_eigenanzeige_vorlagen(): array {
	$wa      = tamil_site_settings()['whatsapp_url'];
	$einr    = function_exists( 'tamil_site_funktion_an' ) && tamil_site_funktion_an( 'einreichungen' ) ? tamil_site_seite_oder( 'einreichen', '' ) : '';
	$werben  = function_exists( 'tamil_site_funktion_an' ) && tamil_site_funktion_an( 'werbung' ) ? tamil_site_seite_oder( 'werben', '' ) : '';
	$kontakt = tamil_site_seite_oder( 'kontakt', home_url( '/kontakt/' ) );
	return array(
		'production'     => array(
			'url'   => tamil_site_seite_oder( 'production', '' ),
			'label' => __( 'Tamil.de Production: Konzertreihe „Live mit dir!“', 'tamil-site' ),
			'titel' => __( 'Live mit dir!', 'tamil-site' ),
			'satz'  => __( 'A.R. Rahman, Ilaiyaraaja, Anirudh und Santhosh Narayanan standen oder stehen mit Tamil.de Production auf deutschen Bühnen.', 'tamil-site' ),
			'link'  => __( 'Zur Konzertreihe', 'tamil-site' ),
			'neu'   => false,
			'bild'  => 'production',
		),
		'event'          => array(
			'url'   => '' !== $einr ? $einr : $kontakt . '#event-einreichen',
			'label' => __( 'Termin bei Tamil.de melden', 'tamil-site' ),
			'titel' => __( 'Dein Fest im Kalender.', 'tamil-site' ),
			'satz'  => __( 'Tempelfest, Konzert, Turnier: kostenlos melden, die Redaktion trägt es ein.', 'tamil-site' ),
			'link'  => __( 'Termin melden', 'tamil-site' ),
			'neu'   => false,
			'bild'  => 'event',
		),
		'werben'         => array(
			'url'   => '' !== $werben ? $werben : $kontakt . '#werben',
			'label' => __( 'Werben auf Tamil.de: Werbeplätze und Mediadaten', 'tamil-site' ),
			'titel' => __( 'Werben auf Tamil.de', 'tamil-site' ),
			'satz'  => __( 'Eine Community in drei Ländern, sechs feste Werbeplätze. Mediadaten gibt es auf Anfrage.', 'tamil-site' ),
			'link'  => __( 'Werbeplätze ansehen', 'tamil-site' ),
			'neu'   => false,
			'bild'  => 'werben',
		),
		'whatsapp-klein' => array(
			'url'   => $wa,
			'label' => __( 'Tamil.de WhatsApp-Kanal öffnen', 'tamil-site' ),
			'titel' => __( 'Tamil.de auf WhatsApp', 'tamil-site' ),
			'satz'  => '',
			'link'  => __( 'Abonnieren', 'tamil-site' ),
			'neu'   => true,
			'bild'  => 'whatsapp',
		),
		'whatsapp'       => array(
			'url'   => $wa,
			'label' => __( 'Tamil.de WhatsApp-Kanal öffnen', 'tamil-site' ),
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
 * @return array{src:string,srcset:string,w:int,h:int,alt:string,nachweis:string,fokus:string,seite:string}|null
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
		'fokus'    => (string) $standard['fokus'],
		'seite'    => (string) $standard['seite'],
	);
}

/**
 * Bildgrößen je Werbeplatz für sizes (Breite der Fläche bei den Formaten aus anzeigen.css).
 */
function tamil_site_eigenanzeige_sizes( string $platz ): string {
	$sizes = array(
		'leaderboard' => '(min-width: 768px) 728px, 100vw',
		'footer'      => '(min-width: 768px) 728px, 100vw',
		'billboard'   => '(min-width: 1024px) 970px, (min-width: 600px) 100vw, 336px',
		'inarticle'   => '(min-width: 1024px) 728px, 336px',
		'sidebar'     => '300px',
		'mobile'      => '320px',
	);
	return $sizes[ $platz ] ?? '(min-width: 768px) 728px, 100vw';
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
	return sprintf(
		'<a class="flaeche anzeige-wrap" href="%1$s"%2$s aria-label="%3$s"><div class="anzeige a-%4$s anzeige--bild anzeige--%5$s">'
		. '<img class="anzeige__bild" src="%6$s" srcset="%7$s" sizes="%8$s" width="%9$d" height="%10$d" alt="%11$s" loading="lazy" decoding="async" style="object-position: %12$s">'
		. '<span class="text"><span class="claim">%13$s</span>%14$s<span class="cta">%15$s</span></span>%16$s</div></a>',
		esc_url( $v['url'] ),
		$v['neu'] ? ' target="_blank" rel="noopener"' : '',
		esc_attr( $v['label'] ),
		esc_attr( $vorlage ),
		'rechts' === $bild['seite'] ? 'rechts' : 'links',
		esc_url( $bild['src'] ),
		esc_attr( $bild['srcset'] ),
		esc_attr( tamil_site_eigenanzeige_sizes( $platz ) ),
		(int) $bild['w'],
		(int) $bild['h'],
		esc_attr( $bild['alt'] ),
		esc_attr( (string) preg_replace( '/[^0-9% .a-z]/', '', $bild['fokus'] ) ),
		esc_html( $v['titel'] ),
		'' !== $v['satz'] ? '<span class="sub">' . esc_html( $v['satz'] ) . '</span>' : '',
		esc_html( $v['link'] ),
		$nachweis
	);
}

/**
 * Bildnachweis einer Eigenanzeige für den Fuß der Seite merken (Theme: tamil_nachweise()). Gemerkt wird nur, was
 * auch gezeigt wird.
 */
function tamil_site_eigenanzeige_nachweis_merken( string $vorlage ): void {
	$v = tamil_site_eigenanzeige_vorlagen()[ $vorlage ] ?? null;
	if ( ! function_exists( 'tamil_nachweise' ) || ! $v || '' === $v['url'] ) {
		return;
	}
	$bild = tamil_site_eigenanzeige_bild( $v['bild'] );
	if ( $bild && '' !== $bild['nachweis'] ) {
		tamil_nachweise( $bild['nachweis'] );
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
	$eigen   = tamil_site_eigenanzeige_html( $vorlage, $platz );
	return array( $eigen, '' !== $eigen, '' !== $eigen ? $vorlage : '' );
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
 * Fertiger Werbeplatz mit Label „Anzeige“; leer, wenn der Platz nichts zeigt. Eigenanzeigen tragen zusätzlich die
 * Klassen ad-anzeige und ad-bild; ihr Bildnachweis landet im Fuß der Seite.
 */
function tamil_site_anzeige( string $platz, bool $ausgeben = true ): string {
	$platz = sanitize_key( $platz );
	if ( ! array_key_exists( $platz, tamil_site_werbeplaetze() ) ) {
		return '';
	}
	[ $inhalt, $eigen, $vorlage ] = tamil_site_anzeige_inhalt( $platz );
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
	if ( $eigen ) {
		tamil_site_eigenanzeige_nachweis_merken( $vorlage );
	}
	$mobil = 'mobile' === $platz;
	$out   = sprintf(
		'<div class="ad ad-%1$s%2$s"%3$s data-platz="%1$s"><span class="ad-label">%4$s</span>%5$s%6$s</div>',
		esc_attr( $platz ),
		$eigen ? ' ad-anzeige ad-bild' : '',
		$mobil ? ' id="ad-mobile"' : '',
		esc_html__( 'Anzeige', 'tamil-site' ),
		$inhalt, // Banner-Code aus den Einstellungen (nur Administratoren), Advanced Ads oder die Vorlagen oben.
		$mobil ? '<button type="button" class="schliessen" aria-label="' . esc_attr__( 'Werbung schließen', 'tamil-site' ) . '">×</button>' : ''
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
}
add_action( 'wp_enqueue_scripts', 'tamil_site_anzeigen_css', 20 );

/**
 * [tamil_anzeige platz="leaderboard"]
 */
function tamil_site_shortcode_anzeige( $atts ): string {
	$atts = shortcode_atts( array( 'platz' => 'inarticle' ), $atts, 'tamil_anzeige' );
	return tamil_site_anzeige( (string) $atts['platz'], false );
}
