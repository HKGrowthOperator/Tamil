<?php
/**
 * Testfälle für die Bilderpflicht im lokalen WordPress anlegen (nur lokal, nie gegen die echte Seite).
 *
 *   php "$WP_DIR/wp-cli.phar" --path="$WP_DIR" --allow-root eval-file wordpress/dev/bilder_testfaelle.php
 *
 * Legt Beiträge an, die die Ränder der Bildkette treffen (idempotent über das Meta „bilder_testfall“):
 * ohne Beitragsbild, nur mit Bild im Text (≥ 600 px, mit figcaption), Titelkarte („Grafik: Tamil.de“,
 * bild_origin=karte), Band 3:1 als Beitragsbild, Termine ab heute in DE/AT/CH (mit Ende, Eintritt, Veranstalter),
 * ein Film mit Spieltagen ab heute, ein vergangener Kino-Beitrag, ein neuer Kino-Beitrag ohne Kinoliste und zwei
 * Beiträge, die das Bild eines anderen Beitrags zum selben Film übernehmen (Titelkarte, Kritik ohne Bild).
 * Die Testbilder sind einfarbige Flächen aus GD (keine fremden Fotos). Danach: node wordpress/dev/bilder_pflicht.mjs.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit( 1 );
}

require_once ABSPATH . 'wp-admin/includes/image.php';
require_once ABSPATH . 'wp-admin/includes/file.php';
require_once ABSPATH . 'wp-admin/includes/media.php';

/**
 * Einfarbiges Testbild in die Mediathek legen.
 */
function bt_bild( string $name, int $w, int $h, array $farbe, string $caption ): int {
	$vorhanden = get_posts(
		array(
			'post_type'   => 'attachment',
			'name'        => sanitize_title( $name ),
			'numberposts' => 1,
			'fields'      => 'ids',
		)
	);
	if ( $vorhanden ) {
		return (int) $vorhanden[0];
	}
	$im = imagecreatetruecolor( $w, $h );
	imagefill( $im, 0, 0, imagecolorallocate( $im, $farbe[0], $farbe[1], $farbe[2] ) );
	imagefilledrectangle( $im, (int) ( $w * 0.1 ), (int) ( $h * 0.3 ), (int) ( $w * 0.4 ), (int) ( $h * 0.8 ), imagecolorallocate( $im, 240, 240, 230 ) );
	$tmp = wp_tempnam( $name . '.jpg' );
	imagejpeg( $im, $tmp, 85 );
	$id = media_handle_sideload(
		array(
			'name'     => $name . '.jpg',
			'tmp_name' => $tmp,
		),
		0,
		null,
		array(
			'post_title'   => $name,
			'post_name'    => sanitize_title( $name ),
			'post_excerpt' => $caption,
		)
	);
	if ( is_wp_error( $id ) ) {
		WP_CLI::error( $id->get_error_message() );
	}
	update_post_meta( $id, '_wp_attachment_image_alt', 'Testbild ' . $name );
	return (int) $id;
}

/**
 * Beitrag anlegen oder aktualisieren (Schlüssel: Meta bilder_testfall).
 */
function bt_beitrag( string $fall, array $daten, array $meta = array(), int $bild = 0 ): int {
	$alt = get_posts(
		array(
			'post_type'   => 'post',
			'meta_key'    => 'bilder_testfall', // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_key
			'meta_value'  => $fall, // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_value
			'numberposts' => 1,
			'fields'      => 'ids',
		)
	);
	$daten = array_merge(
		array(
			'post_status' => 'publish',
			'post_type'   => 'post',
		),
		$daten
	);
	if ( $alt ) {
		$daten['ID'] = (int) $alt[0];
	}
	$id = wp_insert_post( $daten, true );
	if ( is_wp_error( $id ) ) {
		WP_CLI::error( $id->get_error_message() );
	}
	update_post_meta( $id, 'bilder_testfall', $fall );
	foreach ( $meta as $k => $v ) {
		update_post_meta( $id, $k, is_array( $v ) ? wp_slash( wp_json_encode( $v ) ) : $v );
	}
	if ( $bild ) {
		set_post_thumbnail( $id, $bild );
	} else {
		delete_post_thumbnail( $id );
	}
	WP_CLI::log( sprintf( '%-22s %d %s', $fall, $id, get_permalink( $id ) ) );
	return (int) $id;
}

$kat   = static fn( string $slug ): array => array( (int) get_category_by_slug( $slug )->term_id );
$tag   = static fn( int $tage, string $zeit = '19:00' ): string => wp_date( 'Y-m-d', strtotime( "+$tage days" ) ) . ' ' . $zeit;
$heute = current_time( 'Y-m-d' );

$inhalt_bild = bt_bild( 'testfall-inhaltsbild', 1200, 800, array( 70, 110, 90 ), 'Foto: Testbild im Text (lokal)' );
$karte       = bt_bild( 'testfall-titelkarte', 1200, 630, array( 181, 40, 42 ), 'Grafik: Tamil.de' );
$band        = bt_bild( 'testfall-band-3zu1', 1500, 500, array( 40, 70, 130 ), 'Foto: Testband 3:1 (lokal)' );
$kino_bild   = bt_bild( 'testfall-kino', 1200, 900, array( 90, 60, 120 ), 'Foto: Testbild Kino (lokal)' );
$url         = wp_get_attachment_image_url( $inhalt_bild, 'large' );

bt_beitrag(
	'ohne-bild',
	array(
		'post_title'    => 'Testfall: Beitrag ohne Bild',
		'post_content'  => '<p>Dieser Beitrag hat kein Beitragsbild und kein Bild im Text. Er bekommt ein Symbolbild aus dem Rubrik-Pool.</p>',
		'post_category' => $kat( 'news' ),
	)
);
bt_beitrag(
	'nur-inhaltsbild',
	array(
		'post_title'    => 'Testfall: Bild nur im Text',
		'post_content'  => '<p>Einleitung ohne Bild.</p><figure class="wp-block-image"><img src="' . esc_url( $url ) . '" alt="Testbild im Text" class="wp-image-999999"><figcaption>Foto: Testbild im Text (figcaption)</figcaption></figure><p>Weiter im Text.</p>',
		'post_category' => $kat( 'community' ),
	)
);
bt_beitrag(
	'titelkarte',
	array(
		'post_title'    => 'Testfall: Titelkarte als Beitragsbild',
		'post_content'  => '<p>Das Beitragsbild ist eine Titelkarte (Grafik: Tamil.de); das Theme zeigt stattdessen ein Symbolbild.</p>',
		'post_category' => $kat( 'news' ),
	),
	array(
		'bild_origin' => 'karte',
		'bild_credit' => 'Grafik: Tamil.de',
	),
	$karte
);
bt_beitrag(
	'band-3zu1',
	array(
		'post_title'    => 'Testfall: Band im Format 3:1',
		'post_content'  => '<p>Das Beitragsbild ist dreimal so breit wie hoch und wird im Rahmen beschnitten.</p>',
		'post_category' => $kat( 'entertainment' ),
	),
	array(),
	$band
);
bt_beitrag(
	'termin-de',
	array(
		'post_title'    => 'Testfall: Tempelfest in Berlin',
		'post_content'  => '<p>Ein kommender Termin in Deutschland mit Ende am selben Tag, Eintritt und Veranstalter.</p>',
		'post_category' => $kat( 'events' ),
	),
	array(
		'event_datum'        => $tag( 3, '18:00' ),
		'event_ende'         => $tag( 3, '23:00' ),
		'event_ort'          => 'Gemeindesaal, 10967 Berlin',
		'event_land'         => 'DE',
		'event_veranstalter' => 'Testverein Berlin',
		'event_preis'        => '10 €, Kinder frei',
	)
);
bt_beitrag(
	'termin-at',
	array(
		'post_title'    => 'Testfall: Konzertabend in Wien',
		'post_content'  => '<p>Ein kommender Termin in Österreich.</p>',
		'post_category' => $kat( 'events' ),
	),
	array(
		'event_datum'        => $tag( 9, '19:30' ),
		'event_ort'          => 'Festsaal, 1150 Wien',
		'event_land'         => 'AT',
		'event_veranstalter' => 'Testverein Wien',
	)
);
bt_beitrag(
	'termin-ch',
	array(
		'post_title'    => 'Testfall: Tanzabend in Zürich',
		'post_content'  => '<p>Ein kommender Termin in der Schweiz, mehr als 14 Tage entfernt.</p>',
		'post_category' => $kat( 'events' ),
	),
	array(
		'event_datum' => $tag( 30, '17:00' ),
		'event_ort'   => 'Stadthalle, 8004 Zürich',
		'event_land'  => 'CH',
		'event_preis' => '25 CHF',
	)
);
bt_beitrag(
	'kino-aktuell',
	array(
		'post_title'    => 'Testfall: Film mit Spieltagen ab heute',
		'post_content'  => '<p>Kinoliste mit Vorstellungen in den nächsten Tagen.</p>',
		'post_category' => $kat( 'kino' ),
	),
	array(
		'kino_fakten' => array(
			'film'  => 'Testfilm',
			'kinos' => array(
				array(
					'kino'    => 'Testkino Mitte',
					'stadt'   => 'Berlin',
					'land'    => 'DE',
					'termine' => array( $tag( 2, '20:00' ), $tag( 4, '18:00' ) ),
					'url'     => 'https://example.test/tickets',
				),
				array(
					'kino'    => 'Testkino Süd',
					'stadt'   => 'Zürich',
					'land'    => 'CH',
					'termine' => array( $tag( 3, '20:15' ) ),
				),
			),
		),
	),
	$kino_bild
);
bt_beitrag(
	'kino-vorbei',
	array(
		'post_title'    => 'Testfall: Film, dessen Spielzeit vorbei ist',
		'post_content'  => '<p>Alte Kinoliste, darf nicht unter „Diese Woche“ stehen.</p>',
		'post_category' => $kat( 'kino' ),
		'post_date'     => wp_date( 'Y-m-d H:i:s', strtotime( '-60 days' ) ),
	),
	array(
		'kino_fakten' => array(
			'film'  => 'Alter Testfilm',
			'kinos' => array(
				array(
					'kino'    => 'Testkino Alt',
					'stadt'   => 'Köln',
					'land'    => 'DE',
					'termine' => array( wp_date( 'Y-m-d', strtotime( '-55 days' ) ) . ' 20:00' ),
				),
			),
		),
	)
);
bt_beitrag(
	'kino-neu',
	array(
		'post_title'    => 'Testfall: Neuer Kino-Beitrag ohne Kinoliste',
		'post_content'  => '<p>Kritik aus den letzten 30 Tagen, ohne Beitragsbild.</p>',
		'post_category' => $kat( 'kino' ),
		'post_date'     => wp_date( 'Y-m-d H:i:s', strtotime( '-5 days' ) ),
	)
);
bt_beitrag(
	'film-ramayana',
	array(
		'post_title'    => 'Testfall: Ramayana: Rise of a Legend im Kino',
		'post_content'  => '<p>Kinoliste mit Titelkarte; das Bild kommt aus dem älteren Beitrag zum selben Film.</p>',
		'post_category' => $kat( 'kino' ),
	),
	array(
		'bild_origin' => 'karte',
		'kino_fakten' => array(
			'film'  => 'Ramayana: Rise of a Legend',
			'kinos' => array(
				array(
					'kino'    => 'Testkino Nord',
					'stadt'   => 'Hamburg',
					'land'    => 'DE',
					'termine' => array( $tag( 5, '19:00' ) ),
				),
			),
		),
	),
	$karte
);
bt_beitrag(
	'film-kritik',
	array(
		'post_title'    => 'Testfall: „Testfilm“ – Kritik',
		'post_content'  => '<p>Kritik ohne eigenes Bild; das Bild kommt aus dem Beitrag mit der Kinoliste.</p>',
		'post_category' => $kat( 'kino' ),
		'post_date'     => wp_date( 'Y-m-d H:i:s', strtotime( '-2 days' ) ),
	)
);
delete_transient( 'tamil_start_' . current_time( 'Ymd' ) );
delete_transient( 'tamil_filmbilder' );
WP_CLI::success( 'Testfälle angelegt (' . $heute . ').' );
