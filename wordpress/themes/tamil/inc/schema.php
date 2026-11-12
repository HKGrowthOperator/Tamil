<?php
/**
 * Strukturierte Daten (JSON-LD) für Termine: schema.org/Event aus den Feldern „Vorspann und Termin“.
 *
 * SEO-Plugins (Rank Math, Yoast) liefern Artikel-Schema, aber kein Event; das ergänzt das Theme. Ausgegeben wird nur,
 * wenn der Beitrag ein Datum hat (tamil_site_event aus dem Plugin tamil-site).
 *
 * @package Tamil
 */

defined( 'ABSPATH' ) || exit;

/**
 * Event-Schema eines Beitrags oder ein leeres Array.
 *
 * @param int $post_id Beitrag.
 * @return array<string,mixed>
 */
function tamil_event_schema( int $post_id ): array {
	if ( ! function_exists( 'tamil_site_event' ) ) {
		return array();
	}
	$e = tamil_site_event( $post_id );
	if ( ! $e || '' === $e['datum'] ) {
		return array();
	}
	$start = date_create_immutable( $e['datum'], wp_timezone() );
	if ( ! $start ) {
		return array();
	}
	$mit_zeit = strlen( $e['datum'] ) > 10 && '00:00' !== $start->format( 'H:i' );
	$data     = array(
		'@context'            => 'https://schema.org',
		'@type'               => 'Event',
		'name'                => wp_strip_all_tags( get_the_title( $post_id ) ),
		'startDate'           => $mit_zeit ? $start->format( 'c' ) : $start->format( 'Y-m-d' ),
		'eventStatus'         => 'https://schema.org/EventScheduled',
		'eventAttendanceMode' => 'https://schema.org/OfflineEventAttendanceMode',
		'url'                 => get_permalink( $post_id ),
		'description'         => wp_strip_all_tags( get_the_excerpt( $post_id ) ),
	);
	if ( '' !== $e['ende'] ) {
		$ende = date_create_immutable( $e['ende'], wp_timezone() );
		if ( $ende ) {
			$data['endDate'] = strlen( $e['ende'] ) > 10 ? $ende->format( 'c' ) : $ende->format( 'Y-m-d' );
		}
	}
	if ( '' !== $e['ort'] ) {
		$data['location'] = array(
			'@type'   => 'Place',
			'name'    => $e['ort'],
			'address' => array_filter(
				array(
					'@type'          => 'PostalAddress',
					'streetAddress'  => $e['ort'],
					'addressCountry' => in_array( $e['land'], array( 'DE', 'AT', 'CH' ), true ) ? $e['land'] : '',
				)
			),
		);
	}
	if ( '' !== $e['veranstalter'] ) {
		$data['organizer'] = array(
			'@type' => 'Organization',
			'name'  => $e['veranstalter'],
		);
	}
	if ( '' !== $e['ticket_url'] ) {
		$data['offers'] = array(
			'@type'        => 'Offer',
			'url'          => $e['ticket_url'],
			'availability' => 'https://schema.org/InStock',
		);
		if ( preg_match( '/(\d+(?:[.,]\d{1,2})?)\s*(€|EUR|CHF|Fr\.)/u', $e['preis'], $m ) ) {
			$data['offers']['price']         = str_replace( ',', '.', $m[1] );
			$data['offers']['priceCurrency'] = in_array( $m[2], array( 'CHF', 'Fr.' ), true ) ? 'CHF' : 'EUR';
		}
	}
	$bild = get_the_post_thumbnail_url( $post_id, 'tamil-lead' );
	if ( $bild ) {
		$data['image'] = array( $bild );
	}
	return $data;
}

/**
 * Gibt das Event-Schema im Kopf eines einzelnen Beitrags aus.
 */
function tamil_event_schema_ausgeben(): void {
	if ( ! is_singular( 'post' ) ) {
		return;
	}
	$data = tamil_event_schema( (int) get_queried_object_id() );
	if ( ! $data ) {
		return;
	}
	// JSON_HEX_TAG verhindert, dass ein „</script>“ in Titel oder Ort den Block beendet.
	echo '<script type="application/ld+json">' . wp_json_encode( $data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_HEX_TAG | JSON_HEX_AMP ) . "</script>\n"; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
}
add_action( 'wp_head', 'tamil_event_schema_ausgeben', 20 );

/**
 * Wortmarke des Themes als Logo des Herausgebers im Artikel-Schema (Plugin tamil-site), solange im Customizer kein
 * eigenes Logo gesetzt ist. Ändert nichts am Aussehen.
 *
 * @param array{url:string,width:int,height:int}|null $logo Website-Icon oder null.
 * @return array{url:string,width:int,height:int}|null
 */
function tamil_schema_logo( $logo ) {
	$datei = TAMIL_THEME_DIR . '/assets/img/logo.png';
	$masse = is_readable( $datei ) ? wp_getimagesize( $datei ) : false;
	if ( ! $masse ) {
		return $logo;
	}
	return array(
		'url'    => get_theme_file_uri( 'assets/img/logo.png' ),
		'width'  => (int) $masse[0],
		'height' => (int) $masse[1],
	);
}
add_filter( 'tamil_site_seo_logo', 'tamil_schema_logo' );

/**
 * Autorenzeile des Themes (Customizer „Autorenbox: Name“) auch im Schema und im Feed.
 *
 * @param string $name Standard des Plugins.
 */
function tamil_schema_autor_name( $name ): string {
	$eigen = function_exists( 'tamil_opt' ) ? trim( tamil_opt( 'autor_name' ) ) : '';
	return '' !== $eigen ? $eigen : (string) $name;
}
add_filter( 'tamil_site_seo_autor_name', 'tamil_schema_autor_name' );
