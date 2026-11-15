<?php
/**
 * Werbeplätze. Reihenfolge je Platz: gebuchte Anzeige (werbung.php) → Advanced-Ads-Platzierung → eigenes Banner-HTML → Eigenanzeige von Tamil.de
 * (Production, Event melden, Werben, WhatsApp-Kanal) → nichts. Ein Platz ohne Inhalt bleibt unsichtbar.
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
 * Einstellungen mit Standardwerten. Ohne Buchung zeigt jeder Platz eine Eigenanzeige.
 *
 * @return array{anzeigen:array<string,string>,advanced_ads:array<string,string>,eigen:array<string,string>,whatsapp_url:string}
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
	return $settings;
}

function tamil_site_ico( string $name, string $cls = 'ico ico-sm' ): string {
	return sprintf( '<svg class="%1$s" aria-hidden="true"><use href="#i-%2$s"/></svg>', esc_attr( $cls ), esc_attr( $name ) );
}

/**
 * HTML einer Eigenanzeige (Gestaltung kommt aus dem Theme, Klassen .anzeige-wrap / .anzeige): Titel, ein Satz und ein
 * Linktext, ohne Icon, Dachzeile, Gedankenstrich oder Trennpunkte, damit sie sich wie ein Anreißer der Seite liest.
 */
function tamil_site_eigenanzeige_html( string $vorlage ): string {
	$vorlagen = array(
		'production'     => array(
			'url'   => home_url( '/production/' ),
			'label' => __( 'Tamil.de Production: Konzertreihe „Live mit dir!“', 'tamil-site' ),
			'titel' => __( 'Live mit dir!', 'tamil-site' ),
			'satz'  => __( 'A.R. Rahman, Ilaiyaraaja, Anirudh und Santhosh Narayanan standen oder stehen mit Tamil.de Production auf deutschen Bühnen.', 'tamil-site' ),
			'link'  => __( 'Zur Konzertreihe', 'tamil-site' ),
			'neu'   => false,
		),
		'event'          => array(
			'url'   => home_url( '/kontakt/#event-einreichen' ),
			'label' => __( 'Termin bei Tamil.de melden', 'tamil-site' ),
			'titel' => __( 'Dein Fest im Kalender.', 'tamil-site' ),
			'satz'  => __( 'Tempelfest, Konzert, Turnier: kostenlos melden, die Redaktion trägt es ein.', 'tamil-site' ),
			'link'  => __( 'Termin melden', 'tamil-site' ),
			'neu'   => false,
		),
		'werben'         => array(
			'url'   => home_url( '/kontakt/#werben' ),
			'label' => __( 'Werben auf Tamil.de: Mediadaten', 'tamil-site' ),
			'titel' => __( 'Werben auf Tamil.de', 'tamil-site' ),
			'satz'  => __( 'Eine Community in drei Ländern, fünf feste Werbeplätze. Mediadaten gibt es auf Anfrage.', 'tamil-site' ),
			'link'  => __( 'Mediadaten', 'tamil-site' ),
			'neu'   => false,
		),
		'whatsapp-klein' => array(
			'url'   => tamil_site_settings()['whatsapp_url'],
			'label' => __( 'Tamil.de WhatsApp-Kanal öffnen', 'tamil-site' ),
			'titel' => __( 'Tamil.de auf WhatsApp', 'tamil-site' ),
			'satz'  => '',
			'link'  => __( 'Abonnieren', 'tamil-site' ),
			'neu'   => true,
		),
		'whatsapp'       => array(
			'url'   => tamil_site_settings()['whatsapp_url'],
			'label' => __( 'Tamil.de WhatsApp-Kanal öffnen', 'tamil-site' ),
			'titel' => __( 'Kinostarts und Termine direkt aufs Handy.', 'tamil-site' ),
			'satz'  => __( 'Der Kanal von Tamil.de auf WhatsApp. Keine Gruppe, eure Nummern bleiben unsichtbar.', 'tamil-site' ),
			'link'  => __( 'Kanal öffnen', 'tamil-site' ),
			'neu'   => true,
		),
	);
	if ( ! isset( $vorlagen[ $vorlage ] ) ) {
		return '';
	}
	$v = $vorlagen[ $vorlage ];
	return sprintf(
		'<a class="flaeche anzeige-wrap" href="%1$s"%2$s aria-label="%3$s"><div class="anzeige a-%4$s"><span class="text"><span class="claim">%5$s</span>%6$s</span><span class="cta">%7$s</span></div></a>',
		esc_url( $v['url'] ),
		$v['neu'] ? ' target="_blank" rel="noopener"' : '',
		esc_attr( $v['label'] ),
		esc_attr( $vorlage ),
		esc_html( $v['titel'] ),
		'' !== $v['satz'] ? '<span class="sub">' . esc_html( $v['satz'] ) . '</span>' : '',
		esc_html( $v['link'] )
	);
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
	$ersatz   = tamil_site_eigenanzeige_html( (string) ( $settings['eigen'][ $platz ] ?? '' ) );
	return '<div class="tz-anzeige" data-tz-platz>' . $ersatz . '<template data-zustimmung="externe_medien"><div class="flaeche">' . $html . '</div></template></div>';
}

/**
 * Inhalt eines Werbeplatzes ohne Rahmen. Zweiter Rückgabewert: true, wenn es eine Eigenanzeige ist.
 *
 * @return array{0:string,1:bool}
 */
function tamil_site_anzeige_inhalt( string $platz ): array {
	// Eine gebuchte, heute aktive Anzeige (Werbebuchung F3) geht allem anderen vor; „aktiv“ entscheidet werbung.php.
	$gebucht = function_exists( 'tamil_site_werbung_ausliefern' ) ? tamil_site_werbung_ausliefern( $platz ) : '';
	if ( '' !== $gebucht ) {
		return array( $gebucht, false );
	}
	$settings  = tamil_site_settings();
	$placement = (string) ( $settings['advanced_ads'][ $platz ] ?? '' );
	if ( $placement && function_exists( 'get_the_ad_placement' ) ) {
		$html = (string) get_the_ad_placement( $placement );
		if ( '' !== trim( $html ) ) {
			return array( tamil_site_anzeige_fremd( $html, $platz ), false );
		}
	}
	$html = trim( (string) ( $settings['anzeigen'][ $platz ] ?? '' ) );
	if ( '' !== $html ) {
		return array( tamil_site_anzeige_fremd( $html, $platz ), false );
	}
	$eigen = tamil_site_eigenanzeige_html( (string) ( $settings['eigen'][ $platz ] ?? '' ) );
	return array( $eigen, '' !== $eigen );
}

/**
 * Fertiger Werbeplatz mit Label „Anzeige“; leer, wenn der Platz nichts zeigt.
 */
function tamil_site_anzeige( string $platz, bool $ausgeben = true ): string {
	$platz = sanitize_key( $platz );
	if ( ! array_key_exists( $platz, tamil_site_werbeplaetze() ) ) {
		return '';
	}
	[ $inhalt, $eigen ] = tamil_site_anzeige_inhalt( $platz );
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
	$mobil = 'mobile' === $platz;
	$out   = sprintf(
		'<div class="ad ad-%1$s%2$s"%3$s data-platz="%1$s"><span class="ad-label">%4$s</span>%5$s%6$s</div>',
		esc_attr( $platz ),
		$eigen ? ' ad-anzeige' : '',
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
 * [tamil_anzeige platz="leaderboard"]
 */
function tamil_site_shortcode_anzeige( $atts ): string {
	$atts = shortcode_atts( array( 'platz' => 'inarticle' ), $atts, 'tamil_anzeige' );
	return tamil_site_anzeige( (string) $atts['platz'], false );
}
