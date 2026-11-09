<?php
/**
 * Customizer-Abschnitt „Tamil.de“: Kontakt, Social, Texte, Startseite, Production, TV.
 *
 * Kontaktdaten sind standardmäßig leer und erscheinen erst, wenn sie eingetragen sind – keine Beispielnummern live.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Felder: Schlüssel → [Bereich, Beschriftung, Typ, Standard].
 *
 * @return array<string,array{0:string,1:string,2:string,3:string}>
 */
function tamil_customizer_felder(): array {
	return array(
		'tagline'                 => array( 'allgemein', __( 'Unterzeile im Kopf', 'tamil' ), 'text', 'Nachrichten, Kino und Community für Tamilen in DE, AT und CH' ),
		'ueber_uns'               => array( 'allgemein', __( 'Über Tamil.de (Footer)', 'tamil' ), 'textarea', 'Tamil.de ist eine Plattform für deutschsprachige Tamilen in Deutschland, der Schweiz und Österreich: Nachrichten aus der tamilischen Welt, Kino, Veranstaltungen, Feste und praktische Hinweise.' ),
		'org'                     => array( 'allgemein', __( 'Betreiber (Footer, Impressum)', 'tamil' ), 'text', 'KBS Management GmbH' ),
		'autor_name'              => array( 'allgemein', __( 'Autorenbox: Name', 'tamil' ), 'text', 'Redaktion Tamil.de' ),
		'autor_text'              => array( 'allgemein', __( 'Autorenbox: Text', 'tamil' ), 'textarea', 'Die Redaktion schreibt über die tamilische Community im deutschsprachigen Raum – auf Deutsch, mit Blick auf Deutschland, Österreich und die Schweiz.' ),
		'telefon'                 => array( 'kontakt', __( 'Telefon', 'tamil' ), 'text', '' ),
		'email'                   => array( 'kontakt', __( 'E-Mail', 'tamil' ), 'email', '' ),
		'whatsapp'                => array( 'kontakt', __( 'WhatsApp-Nummer (international, z. B. +49 170 …)', 'tamil' ), 'text', '' ),
		'adresse'                 => array( 'kontakt', __( 'Anschrift (eine Zeile pro Zeile)', 'tamil' ), 'textarea', '' ),
		'antwortzeit'             => array( 'kontakt', __( 'Antwortzeit', 'tamil' ), 'text', 'Wir antworten in der Regel innerhalb von zwei Werktagen.' ),
		'kontakt_formular'        => array( 'kontakt', __( 'Kontaktformular (Shortcode eines Formular-Plugins)', 'tamil' ), 'text', '' ),
		'event_formular'          => array( 'kontakt', __( 'Formular „Event einreichen“ (Shortcode)', 'tamil' ), 'text', '' ),
		'social_whatsapp'         => array( 'social', __( 'WhatsApp-Kanal', 'tamil' ), 'url', 'https://whatsapp.com/channel/0029VaFIN43KWEKo3BGoE13t' ),
		'social_instagram'        => array( 'social', __( 'Instagram', 'tamil' ), 'url', 'https://www.instagram.com/tamil_de/' ),
		'social_facebook'         => array( 'social', __( 'Facebook', 'tamil' ), 'url', '' ),
		'social_youtube'          => array( 'social', __( 'YouTube', 'tamil' ), 'url', '' ),
		'aufmacher_id'            => array( 'start', __( 'Aufmacher (Beitrags-ID, leer = neuester markierter Beitrag mit Bild)', 'tamil' ), 'number', '' ),
		'rezept_id'               => array( 'start', __( 'Rezept der Woche (Beitrags-ID, leer = neuestes aus „Küche“)', 'tamil' ), 'number', '' ),
		'rezept_kicker'           => array( 'start', __( 'Rezept: Überschrift des Bands', 'tamil' ), 'text', 'Rezept der Woche' ),
		'production_tag'          => array( 'production', __( 'Schlagwort der Konzertbeiträge', 'tamil' ), 'text', 'production' ),
		'production_titel'        => array( 'production', __( 'Titel', 'tamil' ), 'text', 'Tamil.de Production' ),
		'production_claim'        => array( 'production', __( 'Claim', 'tamil' ), 'textarea', 'Die Konzertreihe „Live mit dir!“: Tamil.de holt die großen Namen der tamilischen Musik nach Deutschland.' ),
		'production_text'         => array( 'production', __( 'Text', 'tamil' ), 'textarea', 'A.R. Rahman, Ilaiyaraaja, Anirudh und Santhosh Narayanan standen oder stehen mit Tamil.de Production auf deutschen Bühnen. Hier stehen alle Konzerte, Tickets, Saalpläne und Antworten auf die häufigsten Fragen rund um den Konzertbesuch.' ),
		'production_ticket_label' => array( 'production', __( 'Ticket-Knopf: Beschriftung', 'tamil' ), 'text', 'Tickets' ),
		'production_ticket_url'   => array( 'production', __( 'Ticket-Knopf: Link', 'tamil' ), 'url', '' ),
		'tv_text'                 => array( 'tv', __( 'Einleitung', 'tamil' ), 'textarea', 'Tamilisches Fernsehen im Browser. Die Streams starten erst nach Klick.' ),
		'tv_sender'               => array( 'tv', __( 'Sender (eine Zeile pro Sender: Name | Stream-Adresse .m3u8)', 'tamil' ), 'textarea', '' ),
	);
}

/**
 * Wert aus dem Customizer, sonst Standard.
 */
function tamil_opt( string $key ): string {
	$felder   = tamil_customizer_felder();
	$standard = $felder[ $key ][3] ?? '';
	return (string) get_theme_mod( 'tamil_' . $key, $standard );
}

function tamil_customize_register( WP_Customize_Manager $wp_customize ): void {
	$wp_customize->add_panel(
		'tamil',
		array(
			'title'    => __( 'Tamil.de', 'tamil' ),
			'priority' => 30,
		)
	);
	$bereiche = array(
		'allgemein'  => __( 'Allgemein', 'tamil' ),
		'kontakt'    => __( 'Kontakt und Formulare', 'tamil' ),
		'social'     => __( 'Social Media', 'tamil' ),
		'start'      => __( 'Startseite', 'tamil' ),
		'production' => __( 'Production', 'tamil' ),
		'tv'         => __( 'Tamil TV', 'tamil' ),
	);
	foreach ( $bereiche as $id => $titel ) {
		$wp_customize->add_section(
			'tamil_' . $id,
			array(
				'title' => $titel,
				'panel' => 'tamil',
			)
		);
	}
	foreach ( tamil_customizer_felder() as $key => [ $bereich, $label, $typ, $standard ] ) {
		$sanitize = match ( $typ ) {
			'url'      => 'esc_url_raw',
			'email'    => 'sanitize_email',
			'number'   => 'absint',
			'textarea' => 'sanitize_textarea_field',
			default    => 'sanitize_text_field',
		};
		$wp_customize->add_setting(
			'tamil_' . $key,
			array(
				'default'           => $standard,
				'sanitize_callback' => $sanitize,
			)
		);
		$wp_customize->add_control(
			'tamil_' . $key,
			array(
				'label'   => $label,
				'section' => 'tamil_' . $bereich,
				'type'    => $typ,
			)
		);
	}
}
add_action( 'customize_register', 'tamil_customize_register' );
