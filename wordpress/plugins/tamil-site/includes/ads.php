<?php
/**
 * Werbeplätze. Reihenfolge je Platz: Advanced-Ads-Platzierung → eigenes Banner-HTML → Eigenanzeige von Tamil.de
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
 * HTML einer Eigenanzeige (Gestaltung kommt aus dem Theme, Klassen .anzeige-wrap / .anzeige).
 */
function tamil_site_eigenanzeige_html( string $vorlage ): string {
	$wm = '<span class="wm">tamil<span class="de">.de</span></span>';
	switch ( $vorlage ) {
		case 'production':
			return sprintf(
				'<a class="flaeche anzeige-wrap" href="%1$s" aria-label="%2$s"><div class="anzeige a-production"><span class="marke">%3$s<span class="eyebrow">Production</span></span><span class="rule"></span><span class="text"><span class="claim">%4$s</span><span class="sub">%5$s</span></span><span class="cta">%6$s %7$s</span></div></a>',
				esc_url( home_url( '/production/' ) ),
				esc_attr__( 'Tamil.de Production: Live mit dir! – Tickets', 'tamil-site' ),
				$wm,
				esc_html__( 'Live mit dir!', 'tamil-site' ),
				esc_html__( 'A.R. Rahman · Ilaiyaraaja · Anirudh · Santhosh Narayanan – die Konzertreihe für DE, AT und CH', 'tamil-site' ),
				tamil_site_ico( 'ticket' ),
				esc_html__( 'Tickets', 'tamil-site' )
			);
		case 'event':
			return sprintf(
				'<a class="flaeche anzeige-wrap" href="%1$s" aria-label="%2$s"><div class="anzeige a-event"><svg class="kolam kolam-gross" aria-hidden="true"><use href="#i-kolam"/></svg><span class="text"><span class="eyebrow">%3$s</span><span class="claim">%4$s</span><span class="sub">%5$s</span></span><span class="cta">%6$s</span></div></a>',
				esc_url( home_url( '/kontakt/#event-einreichen' ) ),
				esc_attr__( 'Event bei Tamil.de melden', 'tamil-site' ),
				esc_html__( 'Veranstaltungskalender', 'tamil-site' ),
				esc_html__( 'Dein Fest im Kalender.', 'tamil-site' ),
				esc_html__( 'Tempelfest, Konzert, Turnier: kostenlos melden, die Redaktion trägt es ein.', 'tamil-site' ),
				esc_html__( 'Event melden', 'tamil-site' )
			);
		case 'werben':
			return sprintf(
				'<a class="flaeche anzeige-wrap" href="%1$s" aria-label="%2$s"><div class="anzeige a-werben hell"><span class="text"><span class="eyebrow">%3$s</span><span class="claim">%4$s</span><span class="sub">%5$s</span></span><span class="cta">%6$s</span></div></a>',
				esc_url( home_url( '/kontakt/#werben' ) ),
				esc_attr__( 'Werben auf Tamil.de – Mediadaten', 'tamil-site' ),
				esc_html__( 'Werben auf Tamil.de', 'tamil-site' ),
				esc_html__( 'Eine Community. Drei Länder. Fünf Formate.', 'tamil-site' ),
				esc_html__( 'Leaderboard, Half Page, In-Article, Footer, Mobile Sticky – Mediadaten auf Anfrage', 'tamil-site' ),
				esc_html__( 'Mediadaten', 'tamil-site' )
			);
		case 'whatsapp-klein':
			return sprintf(
				'<a class="flaeche anzeige-wrap" href="%1$s" target="_blank" rel="noopener" aria-label="%2$s"><div class="anzeige a-whatsapp-klein">%3$s<span class="text"><span class="claim">%4$s</span></span><span class="cta">%5$s</span></div></a>',
				esc_url( tamil_site_settings()['whatsapp_url'] ),
				esc_attr__( 'Tamil.de WhatsApp-Kanal öffnen', 'tamil-site' ),
				tamil_site_ico( 'whatsapp', 'ico' ),
				esc_html__( 'Tamil.de auf WhatsApp', 'tamil-site' ),
				esc_html__( 'Abonnieren', 'tamil-site' )
			);
		case 'whatsapp':
			return sprintf(
				'<a class="flaeche anzeige-wrap" href="%1$s" target="_blank" rel="noopener" aria-label="%2$s"><div class="anzeige a-whatsapp">%3$s<span class="text"><span class="claim">%4$s</span><span class="sub">%5$s</span></span><span class="cta">%6$s</span></div></a>',
				esc_url( tamil_site_settings()['whatsapp_url'] ),
				esc_attr__( 'Tamil.de WhatsApp-Kanal öffnen', 'tamil-site' ),
				tamil_site_ico( 'whatsapp', 'ico ico-lg' ),
				esc_html__( 'Kinostarts und Events direkt aufs Handy.', 'tamil-site' ),
				esc_html__( 'Der Tamil.de-Kanal auf WhatsApp – keine Gruppe, keine Nummern sichtbar', 'tamil-site' ),
				esc_html__( 'Kanal öffnen', 'tamil-site' )
			);
	}
	return '';
}

/**
 * Inhalt eines Werbeplatzes ohne Rahmen. Zweiter Rückgabewert: true, wenn es eine Eigenanzeige ist.
 *
 * @return array{0:string,1:bool}
 */
function tamil_site_anzeige_inhalt( string $platz ): array {
	$settings  = tamil_site_settings();
	$placement = (string) ( $settings['advanced_ads'][ $platz ] ?? '' );
	if ( $placement && function_exists( 'get_the_ad_placement' ) ) {
		$html = (string) get_the_ad_placement( $placement );
		if ( '' !== trim( $html ) ) {
			return array( '<div class="flaeche">' . $html . '</div>', false );
		}
	}
	$html = trim( (string) ( $settings['anzeigen'][ $platz ] ?? '' ) );
	if ( '' !== $html ) {
		return array( '<div class="flaeche">' . $html . '</div>', false );
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
