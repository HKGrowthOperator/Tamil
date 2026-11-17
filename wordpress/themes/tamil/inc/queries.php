<?php
/**
 * Auswahl für Startseite, „Diese Woche“ und „Weiterlesen“. Ergebnisse der Startseite sind ID-Listen im Transient
 * (10 Minuten, Schlüssel mit dem heutigen Datum, damit um Mitternacht nichts Vergangenes stehen bleibt) und werden bei
 * jeder Statusänderung eines Beitrags verworfen – die Startseite kostet so wenige Abfragen.
 */

defined( 'ABSPATH' ) || exit;

const TAMIL_START_RUBRIKEN = array( 'community', 'kultur', 'entertainment', 'sport', 'news' );

/**
 * Beitrags-IDs (veröffentlicht, ohne bereits verwendete). Beiträge, Meta und Rubriken landen gleich im Cache, damit
 * die Anreißer danach ohne weitere Abfragen auskommen.
 *
 * @param array<string,mixed> $args WP_Query-Argumente.
 * @param int[]               $ohne Ausschließen.
 * @return int[]
 */
function tamil_ids( array $args, array $ohne = array() ): array {
	$defaults = array(
		'post_type'           => 'post',
		'post_status'         => 'publish',
		'fields'              => 'ids',
		'no_found_rows'       => true,
		'ignore_sticky_posts' => true,
		'post__not_in'        => array_values( array_unique( array_map( 'intval', $ohne ) ) ),
	);
	$query    = new WP_Query( array_merge( $defaults, $args ) );
	$ids      = array_map( 'intval', $query->posts );
	tamil_cache_fuellen( $ids );
	return $ids;
}

/**
 * Beiträge, ihre Meta, Rubriken und Beitragsbilder in einem Zug laden.
 *
 * @param int[] $ids Beiträge.
 */
function tamil_cache_fuellen( array $ids ): void {
	if ( ! $ids ) {
		return;
	}
	_prime_post_caches( $ids, true, true );
	$bilder = array_filter( array_map( static fn( $id ) => (int) get_post_meta( $id, '_thumbnail_id', true ), $ids ) );
	if ( $bilder ) {
		_prime_post_caches( array_values( $bilder ), false, true );
	}
}

/**
 * Beiträge mit eigenem Bild (Foto als Beitragsbild oder Bild im Text, keine Titelkarte). Die übrigen bekommen ein
 * Symbolbild aus dem Pool; für die vorderen Plätze werden eigene Bilder bevorzugt.
 *
 * @param array<string,mixed> $args WP_Query-Argumente.
 * @param int[]               $ohne Ausschließen.
 * @return int[]
 */
function tamil_ids_mit_bild( array $args, array $ohne = array(), int $anzahl = 0 ): array {
	$ids = array_values( array_filter( tamil_ids( $args, $ohne ), 'tamil_bild_zeigbar' ) );
	return $anzahl ? array_slice( $ids, 0, $anzahl ) : $ids;
}

/**
 * Schlüssel des Transients der Startseite (mit dem heutigen Datum).
 */
function tamil_start_schluessel(): string {
	return 'tamil_start_' . current_time( 'Ymd' );
}

/**
 * Startseite klar2: Aufmacher, vier Nebenstücke, sechs Meldungen, Rubrikkacheln, „Diese Woche“ (zwei Kino-Beiträge
 * mit Bild), „Küche“ (vier mit Bild) und weitere Rubrikblöcke. Ohne Dubletten; Ergebnis zehn Minuten im Transient.
 *
 * @return array{lead:int,neben:int[],meldungen:int[],kacheln:array,woche:array,kueche:int[],rubriken:array<string,int[]>}
 */
function tamil_start_auswahl(): array {
	$cached = get_transient( tamil_start_schluessel() );
	if ( is_array( $cached ) && isset( $cached['lead'] ) ) {
		return $cached;
	}
	$used     = array();
	$sticky   = array_map( 'intval', (array) get_option( 'sticky_posts', array() ) );
	$mit_bild = tamil_ids_mit_bild( array( 'posts_per_page' => 60 ) );

	// Aufmacher: im Customizer gesetzt, sonst neuester markierter Beitrag mit Bild, sonst neuester mit Foto (kein
	// beschnittenes Band), sonst neuester mit Bild.
	$lead = absint( tamil_opt( 'aufmacher_id' ) );
	if ( ! $lead || 'publish' !== get_post_status( $lead ) || ! tamil_bild_zeigbar( $lead ) ) {
		$lead = $sticky ? ( tamil_ids_mit_bild(
			array(
				'post__in'       => $sticky,
				'posts_per_page' => count( $sticky ),
			),
			array(),
			1
		)[0] ?? 0 ) : 0;
	}
	if ( ! $lead ) {
		$fotos = array_values( array_filter( $mit_bild, static fn( $id ) => ! tamil_bildwahl( $id )['breit'] ) );
		$lead  = $fotos[0] ?? ( $mit_bild[0] ?? ( tamil_ids( array( 'posts_per_page' => 1 ) )[0] ?? 0 ) );
	}
	$used[] = $lead;

	// Diese Woche zuerst (nur Aktuelles, tamil_woche_auswahl()): Filme und Termine stehen dort und nicht noch einmal
	// unter den Nebenstücken oder Meldungen.
	$woche = tamil_woche_auswahl( $used );
	$used  = array_merge( $used, $woche['bilder'], array_map( 'intval', wp_list_pluck( $woche['filme'], 'post' ) ), $woche['termine'] );

	// Nebenstücke: vier mit Bild; Meldungen: sechs, mit Bild bevorzugt, sonst die neuesten.
	$neben     = array_slice( array_values( array_diff( $mit_bild, $used ) ), 0, 4 );
	$used      = array_merge( $used, $neben );
	$meldungen = array_slice( array_values( array_diff( $mit_bild, $used ) ), 0, 6 );
	if ( count( $meldungen ) < 6 ) {
		$meldungen = array_merge( $meldungen, tamil_ids( array( 'posts_per_page' => 6 - count( $meldungen ) ), array_merge( $used, $meldungen ) ) );
	}
	$used = array_merge( $used, $meldungen );

	// Küche: Rezept der Woche aus dem Customizer zuerst, dann die neuesten mit Bild.
	$kueche = array();
	$rezept = absint( tamil_opt( 'rezept_id' ) );
	if ( $rezept && 'publish' === get_post_status( $rezept ) && tamil_bild_zeigbar( $rezept ) ) {
		$kueche[] = $rezept;
	}
	if ( get_category_by_slug( 'kueche' ) ) {
		$kueche = array_merge(
			$kueche,
			tamil_ids_mit_bild(
				array(
					'posts_per_page' => 12,
					'category_name'  => 'kueche',
				),
				array_merge( $used, $kueche ),
				4 - count( $kueche )
			)
		);
	}
	$used = array_merge( $used, $kueche );

	// Weitere Rubriken: je vier mit Bild, ein Block erst ab zwei Beiträgen.
	$rubriken = array();
	foreach ( TAMIL_START_RUBRIKEN as $slug ) {
		if ( ! get_category_by_slug( $slug ) ) {
			continue;
		}
		$ids = tamil_ids_mit_bild(
			array(
				'posts_per_page' => 12,
				'category_name'  => $slug,
			),
			$used,
			4
		);
		if ( count( $ids ) >= 2 ) {
			$rubriken[ $slug ] = $ids;
			$used              = array_merge( $used, $ids );
		}
	}

	$auswahl = array(
		'lead'      => (int) $lead,
		'neben'     => $neben,
		'meldungen' => $meldungen,
		'kacheln'   => tamil_kacheln_auswahl(),
		'woche'     => $woche,
		'kueche'    => $kueche,
		'rubriken'  => $rubriken,
	);
	set_transient( tamil_start_schluessel(), $auswahl, 10 * MINUTE_IN_SECONDS );
	return $auswahl;
}

/**
 * „Diese Woche“: nur, was diese Woche zählt.
 * - Im Kino: Filme mit Spieltagen ab heute (aus kino_fakten), höchstens zwei.
 * - Bildkacheln groß und klein: Kino-Beiträge der letzten 30 Tage, sonst weitere Filme mit Spieltagen ab heute; nie
 *   ältere Beiträge ohne kommenden Termin.
 * - Termine: die kommenden der nächsten 14 Tage (höchstens drei), sonst die nächsten drei.
 *
 * @param int[] $ohne Schon auf der Seite verwendete Beiträge.
 * @return array{bilder:int[],filme:array<int,array<string,mixed>>,termine:int[]}
 */
function tamil_woche_auswahl( array $ohne = array() ): array {
	$heute  = current_time( 'Y-m-d' );
	$alle   = tamil_kino_filme( 6 );
	$filme  = array_slice( $alle, 0, 2 );
	$bilder = array();
	if ( get_category_by_slug( 'kino' ) ) {
		$bilder = tamil_ids(
			array(
				'posts_per_page' => 2,
				'category_name'  => 'kino',
				'date_query'     => array( array( 'after' => wp_date( 'Y-m-d', (int) strtotime( $heute . ' -30 days' ) ) ) ),
			),
			array_merge( $ohne, wp_list_pluck( $filme, 'post' ) )
		);
	}
	foreach ( array_slice( $alle, 2 ) as $f ) {
		if ( count( $bilder ) < 2 && ! in_array( (int) $f['post'], $bilder, true ) && ! in_array( (int) $f['post'], $ohne, true ) ) {
			$bilder[] = (int) $f['post'];
		}
	}
	$termine = array();
	if ( function_exists( 'tamil_site_upcoming_events' ) ) {
		$kommend = array_values( array_diff( array_map( 'intval', tamil_site_upcoming_events( 12, array( 'fields' => 'ids' ) )->posts ), $ohne ) );
		$grenze  = wp_date( 'Y-m-d', (int) strtotime( $heute . ' +14 days' ) );
		$bald    = array_values( array_filter( $kommend, static fn( $id ) => substr( (string) get_post_meta( $id, 'event_datum', true ), 0, 10 ) <= $grenze ) );
		$termine = array_slice( $bald ? $bald : $kommend, 0, 3 );
		tamil_cache_fuellen( $termine );
	}
	return array(
		'bilder'  => $bilder,
		'filme'   => $filme,
		'termine' => $termine,
	);
}

/**
 * Rubrikkacheln: jede Rubrik des Bands mit dem Foto ihres neuesten Beitrags (sonst das Rubrikfoto).
 *
 * @return array<int,array{label:string,url:string,slug:string,bild:int}>
 */
function tamil_kacheln_auswahl(): array {
	$kacheln = array();
	foreach ( tamil_nav_items() as $item ) {
		if ( '' === $item['slug'] ) {
			continue;
		}
		$bild = 0;
		if ( get_category_by_slug( $item['slug'] ) ) {
			$ids  = tamil_ids_mit_bild(
				array(
					'posts_per_page' => 8,
					'category_name'  => $item['slug'],
				)
			);
			$bild = tamil_leitbild( $ids ) ? tamil_leitbild( $ids ) : (int) ( $ids[0] ?? 0 );
		}
		$kacheln[] = array(
			'label' => $item['label'],
			'url'   => $item['url'],
			'slug'  => $item['slug'],
			'bild'  => $bild,
		);
	}
	return $kacheln;
}

/**
 * Rubrikkacheln ohne die aktuelle Rubrik (Rubrik- und Fehlerseiten), aus dem Transient der Startseite.
 *
 * @return array<int,array{label:string,url:string,slug:string,bild:int}>
 */
function tamil_kacheln_ohne( string $slug = '' ): array {
	$kacheln = tamil_start_auswahl()['kacheln'];
	return array_values( array_filter( $kacheln, static fn( $k ) => $k['slug'] !== $slug ) );
}

/**
 * Cache verwerfen, sobald sich an Beiträgen oder Einstellungen etwas ändert.
 */
function tamil_flush_auswahl(): void {
	delete_transient( tamil_start_schluessel() );
	delete_transient( 'tamil_filmbilder' ); // Verzeichnis der Filmbilder (inc/filmbilder.php)
	delete_transient( 'tamil_kopf_neu' ); // Top-News in der Kopfzeile (inc/navigation.php)
}
add_action( 'transition_post_status', 'tamil_flush_auswahl' );
add_action( 'deleted_post', 'tamil_flush_auswahl' );
add_action( 'customize_save_after', 'tamil_flush_auswahl' );
add_action( 'update_option_sticky_posts', 'tamil_flush_auswahl' );
add_action( 'updated_post_meta', 'tamil_flush_auswahl_meta', 10, 3 );
add_action( 'added_post_meta', 'tamil_flush_auswahl_meta', 10, 3 );

function tamil_flush_auswahl_meta( $meta_id, $post_id, $meta_key ): void {
	if ( in_array( $meta_key, array( '_thumbnail_id', 'kino_fakten', 'event_datum', 'bild_origin', 'bild_credit' ), true ) ) {
		tamil_flush_auswahl();
	}
}

/**
 * „Mehr aus …“: drei Beiträge der Hauptkategorie, aufgefüllt mit den neuesten.
 *
 * @return int[]
 */
function tamil_related( int $post_id, int $anzahl = 3 ): array {
	$kat = tamil_hauptkategorie( $post_id );
	$ids = $kat ? tamil_ids(
		array(
			'posts_per_page' => $anzahl,
			'cat'            => $kat->term_id,
		),
		array( $post_id )
	) : array();
	if ( count( $ids ) < $anzahl ) {
		$ids = array_merge( $ids, tamil_ids( array( 'posts_per_page' => $anzahl - count( $ids ) ), array_merge( $ids, array( $post_id ) ) ) );
	}
	return $ids;
}
