<?php
/**
 * Bausteine für die Vorlagen: Icons, Kicker, Meta-Zeile, Bilder (nie ohne), Vorspann, Teilen, Brotkrumen.
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
 * Abschnittstitel: tamilisches Wort als Überschrift, deutsches Label, optional „Alle …“.
 */
function tamil_kicker( string $slug, string $text = '', string $mehr = '', string $mehr_text = '', string $tamil = '' ): void {
	$rubrik = tamil_rubrik( $slug );
	$tamil  = '' !== $tamil ? $tamil : $rubrik['tamil'];
	echo '<div class="section-head"><h2 class="kicker"><span class="ta" lang="ta">' . esc_html( $tamil ) . '</span><span class="de">' . esc_html( '' !== $text ? $text : $rubrik['label'] ) . '</span></h2>';
	if ( '' !== $mehr ) {
		/* translators: %s: Rubrik */
		$label = '' !== $mehr_text ? $mehr_text : sprintf( __( 'Alle %s', 'tamil' ), $rubrik['label'] );
		echo '<a class="mehr" href="' . esc_url( $mehr ) . '">' . esc_html( $label ) . '</a>';
	}
	echo '</div>';
}

/**
 * Lesezeit in Minuten (200 Wörter pro Minute, mindestens 1).
 */
function tamil_lesezeit( int $post_id ): int {
	$words = count( (array) preg_split( '/\s+/u', trim( wp_strip_all_tags( (string) get_post_field( 'post_content', $post_id ) ) ), -1, PREG_SPLIT_NO_EMPTY ) );
	return max( 1, (int) ceil( $words / 200 ) );
}

/**
 * Meta-Zeile: Rubrik · Datum · Lesezeit.
 */
function tamil_meta( int $post_id, bool $kat_zeigen = true ): void {
	echo '<p class="meta">';
	if ( $kat_zeigen ) {
		$kat = tamil_hauptkategorie( $post_id );
		if ( $kat ) {
			echo '<span class="kat">' . esc_html( $kat->name ) . '</span>';
		}
	}
	echo '<span><time datetime="' . esc_attr( get_the_date( 'c', $post_id ) ) . '">' . esc_html( get_the_date( 'j. F Y', $post_id ) ) . '</time></span>';
	/* translators: %d: Minuten */
	echo '<span>' . esc_html( sprintf( __( '%d Min.', 'tamil' ), tamil_lesezeit( $post_id ) ) ) . '</span>';
	echo '</p>';
}

/**
 * Vorspann: Meta „standfirst“, sonst der Textauszug.
 */
function tamil_standfirst( int $post_id ): string {
	$text = trim( (string) get_post_meta( $post_id, 'standfirst', true ) );
	if ( '' === $text ) {
		$text = has_excerpt( $post_id ) ? (string) get_the_excerpt( $post_id ) : wp_trim_words( wp_strip_all_tags( (string) get_post_field( 'post_content', $post_id ) ), 34, ' …' );
	}
	return $text;
}

/**
 * Beitragsbild – oder, wenn keins da ist, die Bildkarte der Rubrik. Kein Beitrag erscheint ohne Bild.
 *
 * @param array<string,string> $attr Zusätzliche Attribute (loading, fetchpriority, alt …).
 */
function tamil_bild( int $post_id, string $size = 'tamil-card', array $attr = array() ): string {
	$attr = array_merge( array( 'alt' => '' ), $attr );
	if ( has_post_thumbnail( $post_id ) ) {
		return (string) get_the_post_thumbnail( $post_id, $size, $attr );
	}
	$kat   = tamil_hauptkategorie( $post_id );
	$label = $kat ? $kat->name : get_bloginfo( 'name' );
	$src   = TAMIL_THEME_URI . '/assets/img/bildkarte.svg';
	$extra = '';
	foreach ( $attr as $name => $value ) {
		if ( 'alt' !== $name && 'class' !== $name ) {
			$extra .= sprintf( ' %s="%s"', esc_attr( $name ), esc_attr( $value ) );
		}
	}
	return sprintf(
		'<span class="bildkarte" data-rubrik="%1$s"><img src="%2$s" width="1200" height="675" alt="%3$s"%4$s><span class="bildkarte-label">%5$s</span></span>',
		esc_attr( $kat ? $kat->slug : '' ),
		esc_url( $src ),
		esc_attr( $attr['alt'] ),
		$extra,
		esc_html( $label )
	);
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
		$credit = trim( __( 'Symbolbild: KI-generiert', 'tamil' ) . ( $credit ? ' · ' . $credit : '' ) );
	}
	if ( '' === $credit && ! $thumb ) {
		$credit = __( 'Grafik: Tamil.de', 'tamil' );
	}
	return $credit;
}

/**
 * Teilen-Leiste (WhatsApp zuerst – so teilt die Community).
 */
function tamil_share( string $titel, string $url ): void {
	$wa = 'https://wa.me/?text=' . rawurlencode( $titel . ' ' . $url );
	echo '<div class="share" aria-label="' . esc_attr__( 'Teilen', 'tamil' ) . '"><span class="lbl">' . esc_html__( 'Teilen', 'tamil' ) . '</span>';
	echo '<a class="btn btn-wa" href="' . esc_url( $wa ) . '" target="_blank" rel="noopener">' . tamil_icon( 'whatsapp', 'ico ico-sm', false ) . ' <span class="txt">WhatsApp</span></a>'; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
	$ziele = array(
		array( 'facebook', 'Facebook', 'https://www.facebook.com/sharer/sharer.php?u=' . rawurlencode( $url ) ),
		array( 'x', 'X', 'https://twitter.com/intent/tweet?url=' . rawurlencode( $url ) . '&text=' . rawurlencode( $titel ) ),
		array( 'telegram', 'Telegram', 'https://t.me/share/url?url=' . rawurlencode( $url ) . '&text=' . rawurlencode( $titel ) ),
		array( 'mail', __( 'E-Mail', 'tamil' ), 'mailto:?subject=' . rawurlencode( $titel ) . '&body=' . rawurlencode( $url ) ),
	);
	foreach ( $ziele as [ $icon, $name, $href ] ) {
		$target = str_starts_with( $href, 'mailto:' ) ? '' : ' target="_blank" rel="noopener"';
		/* translators: %s: Netzwerk */
		echo '<a class="btn btn-ghost" href="' . esc_url( $href, array( 'https', 'mailto' ) ) . '"' . $target . ' aria-label="' . esc_attr( sprintf( __( 'Teilen über %s', 'tamil' ), $name ) ) . '">' . tamil_icon( $icon, 'ico ico-sm', false ) . ' <span class="txt">' . esc_html( $name ) . '</span></a>'; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
	}
	echo '<button type="button" class="btn btn-ghost" data-copy="' . esc_attr( $url ) . '" aria-label="' . esc_attr__( 'Link kopieren', 'tamil' ) . '">' . tamil_icon( 'link', 'ico ico-sm', false ) . ' <span class="txt">' . esc_html__( 'Link', 'tamil' ) . '</span></button>'; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
	echo '</div>';
}

/**
 * Brotkrumen: Start › [Rubrik ›] Titel.
 *
 * @param array<int,array{0:string,1:string}> $kette Paare aus Label und URL (letztes Element ohne URL).
 */
function tamil_breadcrumb( array $kette ): void {
	echo '<nav class="breadcrumb" aria-label="' . esc_attr__( 'Brotkrumen', 'tamil' ) . '"><a href="' . esc_url( home_url( '/' ) ) . '">' . esc_html__( 'Start', 'tamil' ) . '</a>';
	foreach ( $kette as [ $label, $url ] ) {
		echo '<span aria-hidden="true">›</span>';
		echo '' !== $url ? '<a href="' . esc_url( $url ) . '">' . esc_html( $label ) . '</a>' : '<span>' . esc_html( wp_html_excerpt( $label, 60, '…' ) ) . '</span>';
	}
	echo '</nav>';
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
 * Datumsangabe eines Termins: „Sa, 25. Oktober 2026, 18:00 Uhr“ bzw. Zeitraum.
 */
function tamil_termin_text( string $datum, string $ende = '' ): string {
	$start = date_create_immutable( $datum, wp_timezone() );
	if ( ! $start ) {
		return $datum;
	}
	$mit_zeit = strlen( $datum ) > 10 && '00:00' !== $start->format( 'H:i' );
	$text     = wp_date( 'D, j. F Y', $start->getTimestamp() ) . ( $mit_zeit ? ', ' . $start->format( 'H:i' ) . ' Uhr' : '' );
	$bis      = '' !== $ende ? date_create_immutable( $ende, wp_timezone() ) : false;
	if ( $bis && $bis->format( 'Y-m-d' ) !== $start->format( 'Y-m-d' ) ) {
		$text = wp_date( 'j. F', $start->getTimestamp() ) . ' – ' . wp_date( 'j. F Y', $bis->getTimestamp() );
	}
	return str_replace( '.,', ',', $text );
}

/**
 * Kinowoche lesbar: „2026-W42“ → „Kinowoche 15.–21. Oktober“, sonst der Text wie geliefert.
 */
function tamil_kinowoche( string $woche ): string {
	if ( ! preg_match( '/^(\d{4})-W(\d{2})$/', $woche, $m ) ) {
		return '' !== $woche ? sprintf( /* translators: %s: Zeitraum */ __( 'Kinowoche %s', 'tamil' ), $woche ) : __( 'Diese Kinowoche', 'tamil' );
	}
	$start = ( new DateTimeImmutable( 'now', wp_timezone() ) )->setISODate( (int) $m[1], (int) $m[2], 4 ); // Kinowoche beginnt donnerstags
	$ende  = $start->modify( '+6 days' );
	return sprintf(
		/* translators: 1: Beginn, 2: Ende */
		__( 'Kinowoche %1$s–%2$s', 'tamil' ),
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
