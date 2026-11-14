<?php
/**
 * Verzeichnis öffentlich (Festlegung F2): Shortcode [tamil_verzeichnis] mit Suche und Filtern in der Adresse,
 * Profil je Eintrag unter /verzeichnis/<name>/ mit Schema-Auszeichnung, Formulare über ?vz_formular=neu|aenderung.
 *
 * Markup schlicht mit Klassen vz-*; die Gestaltung macht das Theme nach Tor G3. Schalter „verzeichnis“ aus: neutraler
 * Hinweis statt Liste, Profile 404, keine Einträge in der Sitemap.
 */

defined( 'ABSPATH' ) || exit;

/** Einträge je Seite. */
define( 'TAMIL_SITE_VZ_JE_SEITE', 20 );

function tamil_site_vz_shortcode_anmelden(): void {
	add_shortcode( 'tamil_verzeichnis', 'tamil_site_vz_shortcode' );
}
add_action( 'init', 'tamil_site_vz_shortcode_anmelden' );

function tamil_site_vz_css(): void {
	$css = 'assets/verzeichnis.css';
	wp_enqueue_style( 'tamil-site-verzeichnis', TAMIL_SITE_URL . $css, array(), TAMIL_SITE_VERSION . '.' . filemtime( TAMIL_SITE_DIR . $css ) );
}

/**
 * Filter aus der Adresse (bereinigt).
 *
 * @return array{suche:string,art:string,kategorie:string,land:string,region:string,stadt:string,seite:int}
 */
function tamil_site_vz_filter(): array {
	// phpcs:disable WordPress.Security.NonceVerification.Recommended -- öffentliche Suche, nur lesend
	$get = static function ( string $k ): string {
		return isset( $_GET[ $k ] ) ? sanitize_text_field( wp_unslash( $_GET[ $k ] ) ) : '';
	};
	$f   = array(
		'suche'     => mb_substr( $get( 'vz_suche' ), 0, 100 ),
		'art'       => sanitize_key( $get( 'vz_art' ) ),
		'kategorie' => sanitize_title( $get( 'vz_kategorie' ) ),
		'land'      => strtoupper( sanitize_key( $get( 'vz_land' ) ) ),
		'region'    => mb_substr( $get( 'vz_region' ), 0, 60 ),
		'stadt'     => mb_substr( $get( 'vz_stadt' ), 0, 100 ),
		'seite'     => max( 1, absint( $get( 'vz_seite' ) ) ),
	);
	// phpcs:enable WordPress.Security.NonceVerification.Recommended
	if ( ! array_key_exists( $f['art'], tamil_site_vz_arten() ) ) {
		$f['art'] = '';
	}
	if ( ! array_key_exists( $f['land'], tamil_site_vz_laender() ) ) {
		$f['land'] = '';
	}
	return $f;
}

/**
 * Abfrage der veröffentlichten Einträge: Premium zuerst, dann nach Name.
 *
 * @param array{suche:string,art:string,kategorie:string,land:string,region:string,stadt:string,seite:int} $f Filter.
 */
function tamil_site_vz_abfrage( array $f ): WP_Query {
	$meta = array(
		'relation' => 'AND',
		'premium'  => array(
			'key'  => '_tamil_vz_premium',
			'type' => 'NUMERIC',
		),
	);
	$zu   = array(
		'art'    => '_tamil_vz_art',
		'land'   => '_tamil_vz_land',
		'region' => '_tamil_vz_bundesland_kanton',
		'stadt'  => '_tamil_vz_stadt',
	);
	foreach ( $zu as $k => $key ) {
		if ( '' !== $f[ $k ] ) {
			$meta[] = array(
				'key'   => $key,
				'value' => $f[ $k ],
			);
		}
	}
	$args = array(
		'post_type'      => TAMIL_SITE_VZ_TYP,
		'post_status'    => 'publish',
		'posts_per_page' => TAMIL_SITE_VZ_JE_SEITE,
		'paged'          => $f['seite'],
		'meta_query'     => $meta, // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query -- Filter des Verzeichnisses
		'orderby'        => array(
			'premium' => 'DESC',
			'title'   => 'ASC',
		),
	);
	if ( '' !== $f['suche'] ) {
		$args['s'] = $f['suche'];
	}
	if ( '' !== $f['kategorie'] ) {
		$args['tax_query'] = array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_tax_query -- Filter des Verzeichnisses
			array(
				'taxonomy' => TAMIL_SITE_VZ_KATEGORIE,
				'field'    => 'slug',
				'terms'    => $f['kategorie'],
			),
		);
	}
	return new WP_Query( $args );
}

/**
 * Vorhandene Werte eines Feldes bei veröffentlichten Einträgen (für die Auswahl von Bundesland und Stadt).
 *
 * @return array<int,string>
 */
function tamil_site_vz_vorhandene_werte( string $feld ): array {
	global $wpdb;
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- kleine Liste für die Filter
	$werte = $wpdb->get_col( $wpdb->prepare( "SELECT DISTINCT m.meta_value FROM {$wpdb->postmeta} m JOIN {$wpdb->posts} p ON p.ID = m.post_id WHERE p.post_type = %s AND p.post_status = 'publish' AND m.meta_key = %s AND m.meta_value != '' ORDER BY m.meta_value", TAMIL_SITE_VZ_TYP, '_tamil_vz_' . $feld ) );
	return array_map( 'strval', (array) $werte );
}

/**
 * [tamil_verzeichnis]: Liste mit Suche oder – mit ?vz_formular=neu|aenderung – das Formular.
 */
function tamil_site_vz_shortcode(): string {
	if ( ! tamil_site_funktion_an( 'verzeichnis' ) ) {
		return '<div class="vz vz-aus"><p>' . esc_html__( 'Das Verzeichnis steht derzeit nicht zur Verfügung.', 'tamil-site' ) . '</p></div>';
	}
	tamil_site_vz_css();
	// phpcs:disable WordPress.Security.NonceVerification.Recommended -- nur Auswahl der Anzeige
	$formular = isset( $_GET['vz_formular'] ) ? sanitize_key( wp_unslash( $_GET['vz_formular'] ) ) : '';
	$eintrag  = isset( $_GET['vz_eintrag'] ) ? absint( $_GET['vz_eintrag'] ) : 0;
	// phpcs:enable WordPress.Security.NonceVerification.Recommended
	$hier = is_singular() ? (string) get_permalink( get_queried_object_id() ) : home_url( '/' );
	if ( in_array( $formular, array( 'neu', 'aenderung' ), true ) ) {
		return '<div class="vz"><p class="vz-zurueck"><a href="' . esc_url( $hier ) . '">' . esc_html__( 'Zum Verzeichnis', 'tamil-site' ) . '</a></p>' . tamil_site_vz_formular( $formular, $eintrag ) . '</div>';
	}
	$f     = tamil_site_vz_filter();
	$query = tamil_site_vz_abfrage( $f );
	ob_start();
	?>
	<div class="vz">
		<form class="vz-suche" method="get" action="<?php echo esc_url( $hier ); ?>" role="search">
			<p class="vz-feld">
				<label for="vz-suche"><?php esc_html_e( 'Suche', 'tamil-site' ); ?></label>
				<input type="search" id="vz-suche" name="vz_suche" value="<?php echo esc_attr( $f['suche'] ); ?>">
			</p>
			<?php
			$auswahl = array(
				'art'       => array( __( 'Art', 'tamil-site' ), tamil_site_vz_arten() ),
				'kategorie' => array( __( 'Kategorie', 'tamil-site' ), tamil_site_vz_kategorie_optionen() ),
				'land'      => array( __( 'Land', 'tamil-site' ), tamil_site_vz_laender() ),
				'region'    => array( __( 'Bundesland oder Kanton', 'tamil-site' ), array_combine( tamil_site_vz_vorhandene_werte( 'bundesland_kanton' ), tamil_site_vz_vorhandene_werte( 'bundesland_kanton' ) ) ),
				'stadt'     => array( __( 'Stadt', 'tamil-site' ), array_combine( tamil_site_vz_vorhandene_werte( 'stadt' ), tamil_site_vz_vorhandene_werte( 'stadt' ) ) ),
			);
			foreach ( $auswahl as $k => $def ) :
				?>
			<p class="vz-feld">
				<label for="vz-filter-<?php echo esc_attr( $k ); ?>"><?php echo esc_html( $def[0] ); ?></label>
				<select id="vz-filter-<?php echo esc_attr( $k ); ?>" name="vz_<?php echo esc_attr( $k ); ?>">
					<option value=""><?php esc_html_e( 'alle', 'tamil-site' ); ?></option>
					<?php foreach ( (array) $def[1] as $wert => $label ) : ?>
					<option value="<?php echo esc_attr( (string) $wert ); ?>"<?php selected( $f[ $k ], (string) $wert ); ?>><?php echo esc_html( (string) $label ); ?></option>
					<?php endforeach; ?>
				</select>
			</p>
			<?php endforeach; ?>
			<p class="vz-aktion"><button type="submit"><?php esc_html_e( 'Suchen', 'tamil-site' ); ?></button></p>
		</form>
		<p class="vz-vorschlagen"><a href="<?php echo esc_url( add_query_arg( 'vz_formular', 'neu', $hier ) . '#vz-formular' ); ?>"><?php esc_html_e( 'Eintrag vorschlagen', 'tamil-site' ); ?></a></p>
		<?php if ( ! $query->have_posts() ) : ?>
		<p class="vz-leer"><?php esc_html_e( 'Keine Einträge gefunden.', 'tamil-site' ); ?></p>
		<?php else : ?>
		<ul class="vz-liste">
			<?php
			foreach ( $query->posts as $post ) :
				$id      = (int) $post->ID;
				$premium = tamil_site_vz_premium( $id );
				?>
			<li class="vz-eintrag<?php echo $premium ? ' vz-premium' : ''; ?>">
				<a class="vz-name" href="<?php echo esc_url( (string) get_permalink( $id ) ); ?>"><?php echo esc_html( get_the_title( $id ) ); ?></a>
				<?php if ( $premium ) : ?>
				<span class="vz-premium-marke"><?php esc_html_e( 'Premium', 'tamil-site' ); ?></span>
				<?php endif; ?>
				<span class="vz-meta"><?php echo esc_html( tamil_site_vz_kurzinfo( $id ) ); ?></span>
			</li>
			<?php endforeach; ?>
		</ul>
			<?php if ( $query->max_num_pages > 1 ) : ?>
		<nav class="vz-seiten" aria-label="<?php esc_attr_e( 'Seiten', 'tamil-site' ); ?>">
				<?php if ( $f['seite'] > 1 ) : ?>
			<a rel="prev" href="<?php echo esc_url( add_query_arg( 'vz_seite', $f['seite'] - 1 ) ); ?>"><?php esc_html_e( 'Zurück', 'tamil-site' ); ?></a>
				<?php endif; ?>
				<?php if ( $f['seite'] < $query->max_num_pages ) : ?>
			<a rel="next" href="<?php echo esc_url( add_query_arg( 'vz_seite', $f['seite'] + 1 ) ); ?>"><?php esc_html_e( 'Weiter', 'tamil-site' ); ?></a>
				<?php endif; ?>
		</nav>
			<?php endif; ?>
		<?php endif; ?>
	</div>
	<?php
	return (string) ob_get_clean();
}

/**
 * Kategorien als slug → „Art: Name“.
 *
 * @return array<string,string>
 */
function tamil_site_vz_kategorie_optionen(): array {
	$terms = get_terms(
		array(
			'taxonomy'   => TAMIL_SITE_VZ_KATEGORIE,
			'hide_empty' => false,
		)
	);
	$out   = array();
	foreach ( is_array( $terms ) ? $terms : array() as $term ) {
		$art                = (string) get_term_meta( $term->term_id, 'tamil_vz_art', true );
		$out[ $term->slug ] = ( tamil_site_vz_arten()[ $art ] ?? '' ) . ( '' !== $art ? ': ' : '' ) . $term->name;
	}
	return $out;
}

/**
 * „Art · Kategorie · Stadt“.
 */
function tamil_site_vz_kurzinfo( int $id ): string {
	$w     = (array) tamil_site_vz_eintrag_werte( $id );
	$teile = array( tamil_site_vz_arten()[ $w['art'] ?? '' ] ?? '' );
	if ( '' !== ( $w['kategorie'] ?? '' ) ) {
		$term    = get_term_by( 'slug', $w['kategorie'], TAMIL_SITE_VZ_KATEGORIE );
		$teile[] = $term ? $term->name : '';
	}
	$teile[] = (string) ( $w['stadt'] ?? '' );
	return implode( ' · ', array_filter( $teile ) );
}

/**
 * Seite mit dem Verzeichnis (für Links aus dem Profil).
 */
function tamil_site_vz_seite_url(): string {
	$seite = get_page_by_path( 'verzeichnis', OBJECT, 'page' );
	return $seite instanceof WP_Post && 'publish' === $seite->post_status ? (string) get_permalink( $seite ) : home_url( '/verzeichnis/' );
}

/**
 * Profil eines Eintrags anstelle des Inhalts (nur Hauptabfrage, Einzelansicht).
 *
 * @param string $inhalt Inhalt.
 */
function tamil_site_vz_profil_inhalt( $inhalt ) {
	if ( ! is_singular( TAMIL_SITE_VZ_TYP ) || ! in_the_loop() || ! is_main_query() || get_the_ID() !== get_queried_object_id() ) {
		return $inhalt;
	}
	return tamil_site_vz_profil( (int) get_the_ID() );
}
add_filter( 'the_content', 'tamil_site_vz_profil_inhalt', 20 );

/**
 * Profil-Markup.
 */
function tamil_site_vz_profil( int $id ): string {
	tamil_site_vz_css();
	$w       = (array) tamil_site_vz_eintrag_werte( $id );
	$premium = tamil_site_vz_premium( $id );
	$zeilen  = array(
		'art'             => __( 'Art', 'tamil-site' ),
		'adresse'         => __( 'Adresse', 'tamil-site' ),
		'telefon'         => __( 'Telefon', 'tamil-site' ),
		'email'           => __( 'E-Mail', 'tamil-site' ),
		'website'         => __( 'Website', 'tamil-site' ),
		'oeffnungszeiten' => __( 'Öffnungszeiten', 'tamil-site' ),
	);
	ob_start();
	?>
	<div class="vz-profil<?php echo $premium ? ' vz-premium' : ''; ?>">
		<?php if ( $premium ) : ?>
		<p class="vz-premium-marke"><?php esc_html_e( 'Premium', 'tamil-site' ); ?></p>
		<?php endif; ?>
		<?php if ( '' !== ( $w['beschreibung'] ?? '' ) ) : ?>
		<p class="vz-beschreibung"><?php echo nl2br( esc_html( $w['beschreibung'] ) ); ?></p>
		<?php endif; ?>
		<dl class="vz-angaben">
			<?php
			foreach ( $zeilen as $key => $label ) :
				if ( 'adresse' === $key ) {
					$ort  = trim( ( $w['plz'] ?? '' ) . ' ' . ( $w['stadt'] ?? '' ) );
					$wert = implode( ', ', array_filter( array( $w['adresse'] ?? '', $ort, tamil_site_vz_laender()[ $w['land'] ?? '' ] ?? '' ) ) );
				} elseif ( 'art' === $key ) {
					$wert = tamil_site_vz_kurzinfo( $id );
				} else {
					$wert = (string) ( $w[ $key ] ?? '' );
				}
				if ( '' === $wert ) {
					continue;
				}
				?>
			<dt><?php echo esc_html( $label ); ?></dt>
			<dd class="vz-<?php echo esc_attr( $key ); ?>">
				<?php if ( 'telefon' === $key ) : ?>
				<a href="<?php echo esc_url( 'tel:' . preg_replace( '/[^0-9+]/', '', $wert ) ); ?>"><?php echo esc_html( $wert ); ?></a>
				<?php elseif ( 'email' === $key ) : ?>
				<a href="<?php echo esc_url( 'mailto:' . antispambot( $wert ) ); ?>"><?php echo esc_html( antispambot( $wert ) ); ?></a>
				<?php elseif ( 'website' === $key ) : ?>
				<a href="<?php echo esc_url( $wert ); ?>" rel="nofollow noopener"><?php echo esc_html( preg_replace( '~^https?://~', '', $wert ) ); ?></a>
				<?php else : ?>
					<?php echo nl2br( esc_html( $wert ) ); ?>
				<?php endif; ?>
			</dd>
			<?php endforeach; ?>
		</dl>
		<p class="vz-aenderung"><a href="<?php echo esc_url( add_query_arg( array( 'vz_formular' => 'aenderung', 'vz_eintrag' => $id ), tamil_site_vz_seite_url() ) . '#vz-formular' ); // phpcs:ignore WordPress.Arrays.ArrayDeclarationSpacing.AssociativeArrayFound -- kurz ?>"><?php esc_html_e( 'Änderung melden', 'tamil-site' ); ?></a></p>
	</div>
	<?php
	return (string) ob_get_clean();
}

/**
 * Schalter aus: Profile antworten 404.
 */
function tamil_site_vz_aus_404(): void {
	if ( is_singular( TAMIL_SITE_VZ_TYP ) && ! tamil_site_funktion_an( 'verzeichnis' ) ) {
		global $wp_query;
		$wp_query->set_404();
		status_header( 404 );
		nocache_headers();
	}
}
add_action( 'template_redirect', 'tamil_site_vz_aus_404', 2 );

/**
 * Schalter aus: jede öffentliche Abfrage des Beitragstyps (Profil, Archiv, Feed) wird zu 404.
 *
 * @param array<string,mixed> $abfrage Abfragevariablen.
 * @return array<string,mixed>
 */
function tamil_site_vz_aus_anfrage( $abfrage ) {
	if ( is_admin() || ! is_array( $abfrage ) || tamil_site_funktion_an( 'verzeichnis' ) ) {
		return $abfrage;
	}
	$typ = $abfrage['post_type'] ?? '';
	if ( isset( $abfrage[ TAMIL_SITE_VZ_TYP ] ) || TAMIL_SITE_VZ_TYP === $typ || ( is_array( $typ ) && in_array( TAMIL_SITE_VZ_TYP, $typ, true ) ) ) {
		return array( 'error' => '404' );
	}
	return $abfrage;
}
add_filter( 'request', 'tamil_site_vz_aus_anfrage' );

/**
 * Sitemap nur mit eingeschaltetem Schalter.
 *
 * @param array<string,WP_Post_Type> $typen Beitragstypen.
 * @return array<string,WP_Post_Type>
 */
function tamil_site_vz_sitemap( $typen ) {
	if ( ! tamil_site_funktion_an( 'verzeichnis' ) ) {
		unset( $typen[ TAMIL_SITE_VZ_TYP ] );
	}
	return $typen;
}
add_filter( 'wp_sitemaps_post_types', 'tamil_site_vz_sitemap' );

/**
 * Schema.org für ein Profil: Geschäft, Organisation oder Gebetsstätte; nur öffentliche Felder.
 *
 * @return array<string,mixed>
 */
function tamil_site_vz_schema( int $id ): array {
	$w       = (array) tamil_site_vz_eintrag_werte( $id );
	$typen   = array(
		'business'      => 'LocalBusiness',
		'dienstleister' => 'LocalBusiness',
		'verein'        => 'Organization',
		'tempel'        => 'PlaceOfWorship',
	);
	$schema  = array(
		'@context' => 'https://schema.org',
		'@type'    => $typen[ $w['art'] ?? '' ] ?? 'Organization',
		'name'     => $w['name'] ?? '',
		'url'      => (string) get_permalink( $id ),
		'address'  => array_filter(
			array(
				'@type'           => 'PostalAddress',
				'streetAddress'   => $w['adresse'] ?? '',
				'postalCode'      => $w['plz'] ?? '',
				'addressLocality' => $w['stadt'] ?? '',
				'addressRegion'   => $w['bundesland_kanton'] ?? '',
				'addressCountry'  => $w['land'] ?? '',
			)
		),
	);
	$weitere = array(
		'description'  => $w['beschreibung'] ?? '',
		'telephone'    => $w['telefon'] ?? '',
		'email'        => $w['email'] ?? '',
		'sameAs'       => $w['website'] ?? '',
		'openingHours' => 'LocalBusiness' === $schema['@type'] ? ( $w['oeffnungszeiten'] ?? '' ) : '',
	);
	return array_merge( $schema, array_filter( $weitere ) );
}

function tamil_site_vz_schema_ausgeben(): void {
	if ( ! is_singular( TAMIL_SITE_VZ_TYP ) || ! tamil_site_funktion_an( 'verzeichnis' ) ) {
		return;
	}
	echo '<script type="application/ld+json">' . wp_json_encode( tamil_site_vz_schema( (int) get_queried_object_id() ), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_HEX_TAG ) . "</script>\n";
}
add_action( 'wp_head', 'tamil_site_vz_schema_ausgeben', 20 );

/**
 * Seiten mit dem Verzeichnis nie zwischenspeichern (Formular mit Nonce und Zeitstempel).
 *
 * @param bool $nie Bisheriger Wert.
 */
function tamil_site_vz_nie_zwischenspeichern( bool $nie ): bool {
	if ( $nie || ! is_singular() ) {
		return $nie;
	}
	$post = get_queried_object();
	return $post instanceof WP_Post && has_shortcode( $post->post_content, 'tamil_verzeichnis' );
}
add_filter( 'tamil_site_nie_zwischenspeichern', 'tamil_site_vz_nie_zwischenspeichern' );
