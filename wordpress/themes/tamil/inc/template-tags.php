<?php
/**
 * Bausteine für die Vorlagen: Icon-Sprite (für die Eigenanzeigen des Plugins), Lesezeit, Vorspann, Bildnachweis,
 * Werbeplätze, Social, Seiten, Datumsangaben.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Icon aus dem Sprite (assets/icons.svg, nach <body> eingebunden).
 */
function tamil_icon( string $name, string $cls = 'ico', bool $ausgeben = true ): string {
	$svg = sprintf( '<svg class="%1$s" aria-hidden="true"><use href="#i-%2$s"/></svg>', esc_attr( $cls ), esc_attr( $name ) );
	if ( $ausgeben ) {
		echo $svg; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- oben escaped
	}
	return $svg;
}

/**
 * Lesezeit in Minuten (200 Wörter pro Minute, mindestens 1).
 */
function tamil_lesezeit( int $post_id ): int {
	$words = count( (array) preg_split( '/\s+/u', trim( wp_strip_all_tags( (string) get_post_field( 'post_content', $post_id ) ) ), -1, PREG_SPLIT_NO_EMPTY ) );
	return max( 1, (int) ceil( $words / 200 ) );
}

/**
 * Text ohne Reste der alten tamil.de: Teilen-Knopf des alten WhatsApp-Plugins („Share on: WhatsApp“), Hinweis des
 * alten Video-Players. Nutzt die Bereinigung des Plugins tamil-site, sonst eine eigene, kleinere. Gibt reinen Text.
 */
function tamil_text_bereinigen( string $text ): string {
	if ( function_exists( 'tamil_site_seo_text_bereinigen' ) ) {
		return tamil_site_seo_text_bereinigen( $text );
	}
	$text = html_entity_decode( wp_strip_all_tags( tamil_altreste_entfernen( $text ) ), ENT_QUOTES, 'UTF-8' );
	$text = (string) preg_replace( array( '/\bShare on:\s*(?:WhatsApp|Facebook|Twitter)?/iu', '/To view this video please enable JavaScript[^.]*\./iu' ), ' ', $text );
	return trim( (string) preg_replace( '/\s+/u', ' ', $text ) );
}

/**
 * Teilen-Feld des alten WhatsApp-Plugins aus HTML entfernen (steht im Altbestand am Ende fast jedes Beitrags und
 * mancher Seiten: <div class="share-to-whatsapp-wrapper">…<div class="clear"></div></div>).
 */
function tamil_altreste_entfernen( string $html ): string {
	if ( ! str_contains( $html, 'share-to-whatsapp' ) && ! str_contains( $html, 'share-on-whsp' ) && ! str_contains( $html, 'whatsapp-button' ) ) {
		return $html;
	}
	return (string) preg_replace(
		array(
			'#<div[^>]*class="[^"]*share-to-whatsapp-wrapper[^"]*"[^>]*>.*?<div[^>]*class="clear\s*"[^>]*>\s*</div>\s*</div>#is',
			'#<div[^>]*class="[^"]*share-on-whsp[^"]*"[^>]*>.*?</div>#is',
			'#(?:<p>\s*)?<a[^>]*class="[^"]*whatsapp-button[^"]*"[^>]*>.*?</a>(?:\s*</p>)?#is',
		),
		'',
		$html
	);
}

/**
 * Vorspann: Meta „standfirst“, sonst der Textauszug, sonst der Anfang des Texts – ohne Reste der alten Seite.
 */
function tamil_standfirst( int $post_id ): string {
	$text = trim( (string) get_post_meta( $post_id, 'standfirst', true ) );
	if ( '' === $text && has_excerpt( $post_id ) ) {
		$text = tamil_text_bereinigen( (string) get_the_excerpt( $post_id ) );
	}
	if ( '' === $text ) {
		$text = wp_trim_words( tamil_text_bereinigen( strip_shortcodes( (string) get_post_field( 'post_content', $post_id ) ) ), 34, ' …' );
	}
	return $text;
}

/**
 * Vorspann im Artikel: Meta „standfirst“, sonst der eigene Textauszug, sonst die ersten ganzen Sätze des Texts
 * (höchstens zwei und etwa 260 Zeichen), damit kein Satz mitten im Wort endet.
 */
function tamil_vorspann_artikel( int $post_id ): string {
	$text = trim( (string) get_post_meta( $post_id, 'standfirst', true ) );
	if ( '' === $text && has_excerpt( $post_id ) ) {
		$text = tamil_text_bereinigen( (string) get_the_excerpt( $post_id ) );
	}
	if ( '' !== $text ) {
		return tamil_ganze_saetze( $text );
	}
	$roh   = tamil_text_bereinigen( strip_shortcodes( (string) get_post_field( 'post_content', $post_id ) ) );
	$saetz = tamil_saetze( $roh, 2 );
	if ( mb_strlen( $saetz ) > 260 ) {
		$saetz = tamil_saetze( $roh, 1 );
	}
	return mb_strlen( $saetz ) > 320 ? wp_trim_words( $saetz, 40, ' …' ) : $saetz;
}

/**
 * Endet ein Text mitten im Satz (gekürzt, „…“), bis zum letzten ganzen Satz kürzen; gibt es keinen, bleibt er.
 */
function tamil_ganze_saetze( string $text ): string {
	$text = trim( $text );
	if ( '' === $text || preg_match( '/[.!?“"»)]$/u', $text ) ) {
		return $text;
	}
	// Satzende: Punkt, Frage- oder Ausrufezeichen nicht nach einer Ziffer („4. Juli“ ist kein Satzende)
	if ( preg_match( '/^(.*[^\d\s][.!?][“"»)]?)\s/us', $text, $m ) && mb_strlen( $m[1] ) >= 40 ) {
		return $m[1];
	}
	return $text;
}

/**
 * Bildnachweis des Beitragsbilds: Bildunterschrift des Anhangs, sonst Meta „bild_credit“.
 * KI-Symbolbilder tragen immer den Hinweis (EU-KI-Verordnung Art. 50).
 */
function tamil_bildnachweis( int $post_id ): string {
	$thumb  = (int) get_post_thumbnail_id( $post_id );
	$credit = $thumb ? trim( (string) wp_get_attachment_caption( $thumb ) ) : '';
	if ( '' === $credit ) {
		$credit = trim( (string) get_post_meta( $post_id, 'bild_credit', true ) );
	}
	if ( 'ki' === get_post_meta( $post_id, 'bild_origin', true ) && ! str_contains( strtolower( $credit ), 'ki' ) ) {
		$credit = trim( __( 'Symbolbild: KI-generiert', 'tamil' ) . ( $credit ? ', ' . $credit : '' ) );
	}
	if ( '' === $credit && ! $thumb ) {
		$credit = __( 'Grafik: Tamil.de', 'tamil' );
	}
	return $credit;
}

/**
 * Werbeplatz aus dem Plugin „Tamil.de Website“ (ohne Plugin: nichts).
 */
function tamil_anzeige( string $platz ): void {
	if ( function_exists( 'tamil_site_anzeige' ) ) {
		tamil_site_anzeige( $platz );
	}
}

/**
 * Werbeplatz 01 (Leaderboard, am Handy Banner) einmal je Seite, unter dem ersten Abschnitt statt über dem Aufmacher.
 * Die Vorlagen rufen ihn an ihrer Stelle auf; footer.php ruft ihn zuletzt noch einmal auf, falls eine Vorlage ihn
 * nicht gesetzt hat (dann steht er über dem Fuß). Ein ungebuchter Platz zeigt die Eigenanzeige (Festlegung F3).
 *
 * @param string $klasse Klasse des umgebenden Elements („innen anzeige-zwischen“ oder ein Rasterbereich).
 */
function tamil_leaderboard( string $klasse = 'innen anzeige-zwischen' ): void {
	static $gezeigt = false;
	if ( $gezeigt || ! function_exists( 'tamil_site_anzeige' ) ) {
		return;
	}
	$gezeigt = true;
	$html    = tamil_site_anzeige( 'leaderboard', false );
	if ( '' !== $html ) {
		echo '<div class="' . esc_attr( $klasse ) . '">' . $html . '</div>'; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Werbeplatz aus dem Plugin, dort escapt
	}
}

/**
 * Wird der mobile Sticky-Werbeplatz gezeigt? (Dann bekommt die Seite unten Platz.)
 */
function tamil_hat_mobile_anzeige(): bool {
	static $hat = null;
	if ( null === $hat ) {
		$hat = function_exists( 'tamil_site_anzeige' ) && '' !== tamil_site_anzeige( 'mobile', false );
	}
	return $hat;
}

/**
 * Social-Profile mit Adresse.
 *
 * @return array<int,array{icon:string,name:string,url:string}>
 */
function tamil_social(): array {
	$out = array();
	foreach ( array(
		'whatsapp'  => __( 'WhatsApp-Kanal', 'tamil' ),
		'instagram' => 'Instagram',
		'facebook'  => 'Facebook',
		'youtube'   => 'YouTube',
	) as $icon => $name ) {
		$url = tamil_opt( 'social_' . $icon );
		if ( '' !== $url ) {
			$out[] = array(
				'icon' => $icon,
				'name' => $name,
				'url'  => $url,
			);
		}
	}
	return $out;
}

/**
 * wa.me-Link zur Redaktionsnummer (leer, wenn keine Nummer hinterlegt ist).
 */
function tamil_whatsapp_link( string $text = '' ): string {
	$nummer = preg_replace( '/\D+/', '', tamil_opt( 'whatsapp' ) );
	if ( ! $nummer ) {
		return '';
	}
	return 'https://wa.me/' . $nummer . ( '' !== $text ? '?text=' . rawurlencode( $text ) : '' );
}

/**
 * Seite per Slug (nur veröffentlicht), sonst null.
 */
function tamil_seite( string $slug ): ?WP_Post {
	$page = get_page_by_path( $slug );
	return $page instanceof WP_Post && 'publish' === $page->post_status ? $page : null;
}

/**
 * URL einer Seite per Slug; Rückfall auf die Startseite mit Anker.
 */
function tamil_seiten_url( string $slug, string $anker = '' ): string {
	$page = tamil_seite( $slug );
	$url  = $page ? (string) get_permalink( $page ) : home_url( '/' );
	return $url . ( '' !== $anker ? '#' . $anker : '' );
}

/**
 * Datum im Kopf: „Samstag, 18. Oktober 2026“.
 */
function tamil_heute(): string {
	return wp_date( 'l, j. F Y' );
}

/**
 * Datumsangabe eines Termins: „Sa, 25. Oktober 2026, 18:00 Uhr“, mit Ende am selben Tag „18:00 bis 23:00 Uhr“,
 * über mehrere Tage als Zeitraum.
 */
function tamil_termin_text( string $datum, string $ende = '' ): string {
	$start = date_create_immutable( $datum, wp_timezone() );
	if ( ! $start ) {
		return $datum;
	}
	$mit_zeit = strlen( $datum ) > 10 && '00:00' !== $start->format( 'H:i' );
	$text     = wp_date( 'D, j. F Y', $start->getTimestamp() ) . ( $mit_zeit ? ', ' . $start->format( 'H:i' ) . ' Uhr' : '' );
	$bis      = '' !== $ende ? date_create_immutable( $ende, wp_timezone() ) : false;
	if ( $bis && $bis->format( 'Y-m-d' ) > $start->format( 'Y-m-d' ) ) { // ein Ende vor dem Beginn ist ein Datenfehler und wird nicht ausgegeben
		$text = wp_date( 'j. F', $start->getTimestamp() ) . ' bis ' . wp_date( 'j. F Y', $bis->getTimestamp() );
	} elseif ( $bis && $mit_zeit && strlen( $ende ) > 10 && $bis > $start && $bis->format( 'Y-m-d' ) === $start->format( 'Y-m-d' ) ) {
		$text = wp_date( 'D, j. F Y', $start->getTimestamp() ) . ', ' . $start->format( 'H:i' ) . ' bis ' . $bis->format( 'H:i' ) . ' Uhr';
	}
	return str_replace( '.,', ',', $text );
}

/**
 * Kinowoche lesbar: „2026-W42“ wird zu „Kinowoche 15. bis 21. Oktober“, sonst der Text wie geliefert.
 */
function tamil_kinowoche( string $woche ): string {
	if ( ! preg_match( '/^(\d{4})-W(\d{2})$/', $woche, $m ) ) {
		return '' !== $woche ? sprintf( /* translators: %s: Zeitraum */ __( 'Kinowoche %s', 'tamil' ), $woche ) : __( 'Diese Kinowoche', 'tamil' );
	}
	$start = ( new DateTimeImmutable( 'now', wp_timezone() ) )->setISODate( (int) $m[1], (int) $m[2], 4 ); // Kinowoche beginnt donnerstags
	$ende  = $start->modify( '+6 days' );
	return sprintf(
		/* translators: 1: Beginn, 2: Ende */
		__( 'Kinowoche %1$s bis %2$s', 'tamil' ),
		wp_date( 'j.', $start->getTimestamp() ),
		wp_date( 'j. F', $ende->getTimestamp() )
	);
}

/**
 * Schlagworte eines Beitrags (immer ein Array, auch ohne Schlagworte).
 *
 * @return WP_Term[]
 */
function tamil_tags( int $post_id ): array {
	$tags = get_the_tags( $post_id );
	return is_array( $tags ) ? $tags : array();
}
