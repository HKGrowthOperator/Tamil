<?php
/**
 * Angaben für Suchmaschinen und soziale Netze: Beschreibung, OpenGraph, Twitter-Karte, JSON-LD (NewsArticle,
 * BreadcrumbList, WebSite mit Suche) und noindex für Suchergebnisse.
 *
 * Läuft nur, wenn kein SEO-Plugin (Yoast, Rank Math) aktiv ist – sonst gäbe es alles doppelt. Das Event-Schema der
 * Termine kommt weiter aus dem Theme (themes/tamil/inc/schema.php) und wird hier nicht wiederholt. Die Sitemap kommt
 * aus WordPress.
 *
 * Beschreibung eines Beitrags: Feld _tamil_seo_description (schreibt der Radar), sonst Vorspann (standfirst), sonst
 * der gekürzte Auszug. Titel: Feld _tamil_seo_title, sonst der Titel von WordPress.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Höchstlänge der Beschreibung in Zeichen.
 */
define( 'TAMIL_SITE_SEO_LAENGE', 160 );

/**
 * Ist die eigene SEO-Ausgabe aktiv? Nein, sobald Yoast oder Rank Math läuft.
 */
function tamil_site_seo_aktiv(): bool {
	$aktiv = ! defined( 'WPSEO_VERSION' ) && ! defined( 'RANK_MATH_VERSION' );
	/**
	 * Eigene SEO-Ausgabe ein- oder ausschalten.
	 *
	 * @param bool $aktiv Stand.
	 */
	return (bool) apply_filters( 'tamil_site_seo_aktiv', $aktiv );
}

/**
 * Vorschaubild für soziale Netze: 1200 × 630, beschnitten.
 */
function tamil_site_seo_bildgroesse(): void {
	add_image_size( 'tamil-og', 1200, 630, true );
}
add_action( 'after_setup_theme', 'tamil_site_seo_bildgroesse', 20 );

/**
 * Einstellungen (Standardbild für Seiten ohne Beitragsbild).
 *
 * @return array{bild:string}
 */
function tamil_site_seo_einstellungen(): array {
	$gespeichert = get_option( 'tamil_site_seo', array() );
	$gespeichert = is_array( $gespeichert ) ? $gespeichert : array();
	return array( 'bild' => (string) ( $gespeichert['bild'] ?? '' ) );
}

/**
 * @param mixed $input Formularwerte.
 * @return array{bild:string}
 */
function tamil_site_sanitize_seo( $input ): array {
	$input = is_array( $input ) ? $input : array();
	return array( 'bild' => esc_url_raw( trim( (string) ( $input['bild'] ?? '' ) ) ) );
}

/**
 * Text auf höchstens $laenge Zeichen kürzen, an einer Wortgrenze, mit Auslassungszeichen.
 */
function tamil_site_seo_kuerzen( string $text, int $laenge = TAMIL_SITE_SEO_LAENGE ): string {
	$text = trim( (string) preg_replace( '/\s+/u', ' ', wp_strip_all_tags( html_entity_decode( $text, ENT_QUOTES, 'UTF-8' ) ) ) );
	if ( mb_strlen( $text ) <= $laenge ) {
		return $text;
	}
	$schnitt = mb_substr( $text, 0, $laenge - 1 );
	$leer    = mb_strrpos( $schnitt, ' ' );
	if ( false !== $leer && $leer > $laenge / 2 ) {
		$schnitt = mb_substr( $schnitt, 0, $leer );
	}
	return rtrim( $schnitt, ' ,.;:–-' ) . '…';
}

/**
 * Darf ein Beitrag Angaben für Suchmaschinen bekommen? Nur veröffentlicht und ohne Passwort. Geschützte, private und
 * nicht veröffentlichte Beiträge bekommen keine Beschreibung, kein Bild und kein Artikel-Schema – auch nicht nach
 * Eingabe des Passworts.
 */
function tamil_site_seo_oeffentlich( $post ): bool {
	return $post instanceof WP_Post && 'publish' === $post->post_status && '' === (string) $post->post_password;
}

/**
 * Beschreibung eines Beitrags oder einer Seite (leer, wenn er nicht öffentlich ist).
 */
function tamil_site_seo_beschreibung_beitrag( int $post_id ): string {
	$post = get_post( $post_id );
	if ( ! tamil_site_seo_oeffentlich( $post ) ) {
		return '';
	}
	foreach ( array( '_tamil_seo_description', 'standfirst' ) as $feld ) {
		$wert = trim( (string) get_post_meta( $post_id, $feld, true ) );
		if ( '' !== $wert ) {
			return tamil_site_seo_kuerzen( $wert );
		}
	}
	$text = has_excerpt( $post ) ? $post->post_excerpt : strip_shortcodes( $post->post_content );
	return tamil_site_seo_kuerzen( excerpt_remove_blocks( $text ) );
}

/**
 * Beschreibung der aktuellen Seite (leer, wenn es keine sinnvolle gibt).
 */
function tamil_site_seo_beschreibung(): string {
	if ( is_singular() ) {
		return tamil_site_seo_beschreibung_beitrag( (int) get_queried_object_id() );
	}
	if ( is_front_page() || is_home() ) {
		return tamil_site_seo_kuerzen( (string) get_bloginfo( 'description' ) );
	}
	if ( is_category() || is_tag() || is_tax() ) {
		return tamil_site_seo_kuerzen( (string) term_description() );
	}
	return '';
}

/**
 * Eigener SEO-Titel eines Beitrags (leer, wenn keiner gesetzt ist).
 */
function tamil_site_seo_titel_feld( int $post_id ): string {
	return trim( (string) get_post_meta( $post_id, '_tamil_seo_title', true ) );
}

/**
 * <title> aus dem Feld _tamil_seo_title, wenn gesetzt.
 *
 * @param string $titel Bisheriger Titel (leer = WordPress bildet ihn).
 */
function tamil_site_seo_document_title( $titel ) {
	if ( tamil_site_seo_aktiv() && is_singular() ) {
		$eigen = tamil_site_seo_titel_feld( (int) get_queried_object_id() );
		if ( '' !== $eigen ) {
			// WordPress gibt den Rückgabewert ungefiltert in <title> aus.
			return esc_html( $eigen );
		}
	}
	return $titel;
}
add_filter( 'pre_get_document_title', 'tamil_site_seo_document_title', 20 );

/**
 * Vorschaubild: Beitragsbild in 1200 × 630 (fehlt die Größe bei alten Bildern, das Original), sonst das Standardbild
 * aus den Einstellungen, sonst das Website-Icon.
 *
 * @return array{url:string,width:int,height:int,alt:string}|null
 */
function tamil_site_seo_bild(): ?array {
	if ( is_singular() && tamil_site_seo_oeffentlich( get_queried_object() ) && has_post_thumbnail( (int) get_queried_object_id() ) ) {
		$id  = (int) get_post_thumbnail_id( (int) get_queried_object_id() );
		$src = wp_get_attachment_image_src( $id, 'tamil-og' );
		if ( $src ) {
			return array(
				'url'    => (string) $src[0],
				'width'  => (int) $src[1],
				'height' => (int) $src[2],
				'alt'    => (string) get_post_meta( $id, '_wp_attachment_image_alt', true ),
			);
		}
	}
	$standard = tamil_site_seo_einstellungen()['bild'];
	if ( '' !== $standard ) {
		return array(
			'url'    => $standard,
			'width'  => 0,
			'height' => 0,
			'alt'    => '',
		);
	}
	$icon = get_site_icon_url( 512 );
	return $icon ? array(
		'url'    => $icon,
		'width'  => 512,
		'height' => 512,
		'alt'    => '',
	) : null;
}

/**
 * Adresse der aktuellen Seite für og:url (leer, wenn es keine feste gibt).
 */
function tamil_site_seo_url(): string {
	if ( is_singular() ) {
		return (string) wp_get_canonical_url( (int) get_queried_object_id() );
	}
	if ( is_front_page() ) {
		return home_url( '/' );
	}
	if ( is_category() || is_tag() || is_tax() ) {
		$link = get_term_link( get_queried_object() );
		return is_wp_error( $link ) ? '' : (string) $link;
	}
	return '';
}

/**
 * Logo des Herausgebers: eigenes Logo aus dem Customizer, sonst das, was das Theme meldet (Filter
 * tamil_site_seo_logo), sonst das Website-Icon.
 *
 * @return array{url:string,width:int,height:int}|null
 */
function tamil_site_seo_logo(): ?array {
	$id  = (int) get_theme_mod( 'custom_logo' );
	$src = $id ? wp_get_attachment_image_src( $id, 'full' ) : false;
	if ( $src ) {
		return array(
			'url'    => (string) $src[0],
			'width'  => (int) $src[1],
			'height' => (int) $src[2],
		);
	}
	$icon = (string) get_site_icon_url( 512 );
	$logo = '' !== $icon ? array(
		'url'    => $icon,
		'width'  => 512,
		'height' => 512,
	) : null;
	/**
	 * Logo für das Schema, wenn kein eigenes Logo gesetzt ist (das Theme meldet seine Wortmarke).
	 *
	 * @param array{url:string,width:int,height:int}|null $logo Website-Icon oder null.
	 */
	$logo = apply_filters( 'tamil_site_seo_logo', $logo );
	return is_array( $logo ) && ! empty( $logo['url'] ) ? $logo : null;
}

/**
 * Herausgeber (die Website) für das Artikel-Schema: ein Nachrichtenmedium mit fester Kennung und Logo.
 *
 * @return array<string,mixed>
 */
function tamil_site_seo_herausgeber(): array {
	$org  = array(
		'@type' => 'NewsMediaOrganization',
		'@id'   => home_url( '/#organization' ),
		'name'  => wp_strip_all_tags( (string) get_bloginfo( 'name' ) ),
		'url'   => home_url( '/' ),
	);
	$logo = tamil_site_seo_logo();
	if ( $logo ) {
		$org['logo'] = array(
			'@type'  => 'ImageObject',
			'url'    => $logo['url'],
			'width'  => (int) $logo['width'],
			'height' => (int) $logo['height'],
		);
	}
	return $org;
}

/**
 * Name in der Autorenzeile. Steht so sichtbar im Artikel, im Schema und im Feed – nie ein Anmeldename.
 */
function tamil_site_seo_autor_name(): string {
	/**
	 * Name in der Autorenzeile (das Theme meldet seinen Customizer-Wert).
	 *
	 * @param string $name Standard: „Redaktion <Name der Website>“.
	 */
	$name = (string) apply_filters( 'tamil_site_seo_autor_name', 'Redaktion ' . wp_strip_all_tags( (string) get_bloginfo( 'name' ) ) );
	return '' !== trim( $name ) ? $name : wp_strip_all_tags( (string) get_bloginfo( 'name' ) );
}

/**
 * NewsArticle für einen Beitrag. Kein Event: das liefert das Theme.
 *
 * @return array<string,mixed>
 */
function tamil_site_seo_artikel( WP_Post $post ): array {
	// Autor wie in der sichtbaren Autorenzeile (die Redaktion), nie der Benutzer, unter dem der Beitrag angelegt ist:
	// der Altbestand läuft auf einem Benutzer, Radar-Beiträge auf dem Benutzer des Radars.
	$daten      = array(
		'@context'         => 'https://schema.org',
		'@type'            => 'NewsArticle',
		'headline'         => wp_strip_all_tags( get_the_title( $post ) ),
		'description'      => tamil_site_seo_beschreibung_beitrag( (int) $post->ID ),
		'datePublished'    => (string) get_post_time( 'c', true, $post ),
		'dateModified'     => (string) get_post_modified_time( 'c', true, $post ),
		'mainEntityOfPage' => (string) get_permalink( $post ),
		'inLanguage'       => str_replace( '_', '-', get_locale() ),
		'author'           => array(
			'@type' => 'Organization',
			'name'  => tamil_site_seo_autor_name(),
			'url'   => home_url( '/' ),
		),
		'publisher'        => tamil_site_seo_herausgeber(),
	);
	$kategorien = get_the_category( $post->ID );
	if ( $kategorien ) {
		$daten['articleSection'] = $kategorien[0]->name;
	}
	if ( has_post_thumbnail( $post ) ) {
		$bilder = array();
		foreach ( array( 'tamil-og', 'tamil-lead', 'full' ) as $groesse ) {
			$src = wp_get_attachment_image_src( (int) get_post_thumbnail_id( $post ), $groesse );
			if ( $src && ! in_array( $src[0], $bilder, true ) ) {
				$bilder[] = (string) $src[0];
			}
		}
		$daten['image'] = $bilder;
	}
	return $daten;
}

/**
 * Brotkrumen: Start → (Rubrik bzw. übergeordnete Seiten) → aktuelle Seite.
 *
 * @return array<int,array{name:string,url:string}>
 */
function tamil_site_seo_krumen(): array {
	$krumen = array(
		array(
			'name' => __( 'Start', 'tamil-site' ),
			'url'  => home_url( '/' ),
		),
	);
	if ( is_singular( 'post' ) ) {
		$post       = get_queried_object();
		$kategorien = get_the_category( $post->ID );
		if ( $kategorien ) {
			$krumen[] = array(
				'name' => $kategorien[0]->name,
				'url'  => (string) get_category_link( $kategorien[0] ),
			);
		}
		$krumen[] = array(
			'name' => wp_strip_all_tags( get_the_title( $post ) ),
			'url'  => (string) get_permalink( $post ),
		);
	} elseif ( is_page() && ! is_front_page() ) {
		$post = get_queried_object();
		foreach ( array_reverse( get_post_ancestors( $post ) ) as $vorfahr ) {
			$krumen[] = array(
				'name' => wp_strip_all_tags( get_the_title( $vorfahr ) ),
				'url'  => (string) get_permalink( $vorfahr ),
			);
		}
		$krumen[] = array(
			'name' => wp_strip_all_tags( get_the_title( $post ) ),
			'url'  => (string) get_permalink( $post ),
		);
	} elseif ( is_category() || is_tag() ) {
		$term = get_queried_object();
		$link = get_term_link( $term );
		if ( ! is_wp_error( $link ) ) {
			$krumen[] = array(
				'name' => $term->name,
				'url'  => (string) $link,
			);
		}
	}
	return count( $krumen ) > 1 ? $krumen : array();
}

/**
 * Alle JSON-LD-Blöcke der aktuellen Seite.
 *
 * @return array<int,array<string,mixed>>
 */
function tamil_site_seo_schema(): array {
	$bloecke = array();
	if ( is_front_page() ) {
		$bloecke[] = array(
			'@context'        => 'https://schema.org',
			'@type'           => 'WebSite',
			'name'            => wp_strip_all_tags( (string) get_bloginfo( 'name' ) ),
			'url'             => home_url( '/' ),
			'inLanguage'      => str_replace( '_', '-', get_locale() ),
			'potentialAction' => array(
				'@type'       => 'SearchAction',
				'target'      => array(
					'@type'       => 'EntryPoint',
					'urlTemplate' => home_url( '/?s={search_term_string}' ),
				),
				'query-input' => 'required name=search_term_string',
			),
		);
	}
	if ( is_singular( 'post' ) && tamil_site_seo_oeffentlich( get_queried_object() ) ) {
		$bloecke[] = tamil_site_seo_artikel( get_queried_object() );
	}
	$krumen = tamil_site_seo_krumen();
	if ( $krumen ) {
		$liste = array();
		foreach ( $krumen as $i => $krume ) {
			$liste[] = array(
				'@type'    => 'ListItem',
				'position' => $i + 1,
				'name'     => $krume['name'],
				'item'     => $krume['url'],
			);
		}
		$bloecke[] = array(
			'@context'        => 'https://schema.org',
			'@type'           => 'BreadcrumbList',
			'itemListElement' => $liste,
		);
	}
	return $bloecke;
}

/**
 * Meta-Angaben als Liste [Attribut, Name, Inhalt] (Attribut name oder property).
 *
 * @return array<int,array{0:string,1:string,2:string}>
 */
function tamil_site_seo_meta(): array {
	if ( is_search() || is_404() ) {
		return array();
	}
	$beschreibung = tamil_site_seo_beschreibung();
	$titel        = is_singular() ? tamil_site_seo_titel_feld( (int) get_queried_object_id() ) : '';
	if ( '' === $titel ) {
		$titel = is_singular() ? wp_strip_all_tags( get_the_title( (int) get_queried_object_id() ) ) : wp_get_document_title();
	}
	$artikel = is_singular( 'post' );
	$meta    = array();
	if ( '' !== $beschreibung ) {
		$meta[] = array( 'name', 'description', $beschreibung );
	}
	$meta[] = array( 'property', 'og:locale', get_locale() );
	$meta[] = array( 'property', 'og:site_name', wp_strip_all_tags( (string) get_bloginfo( 'name' ) ) );
	$meta[] = array( 'property', 'og:type', $artikel ? 'article' : 'website' );
	$meta[] = array( 'property', 'og:title', html_entity_decode( $titel, ENT_QUOTES, 'UTF-8' ) );
	if ( '' !== $beschreibung ) {
		$meta[] = array( 'property', 'og:description', $beschreibung );
	}
	$url = tamil_site_seo_url();
	if ( '' !== $url ) {
		$meta[] = array( 'property', 'og:url', $url );
	}
	if ( $artikel ) {
		$post   = get_queried_object();
		$meta[] = array( 'property', 'article:published_time', (string) get_post_time( 'c', true, $post ) );
		$meta[] = array( 'property', 'article:modified_time', (string) get_post_modified_time( 'c', true, $post ) );
	}
	$bild = tamil_site_seo_bild();
	if ( $bild ) {
		$meta[] = array( 'property', 'og:image', $bild['url'] );
		if ( $bild['width'] && $bild['height'] ) {
			$meta[] = array( 'property', 'og:image:width', (string) $bild['width'] );
			$meta[] = array( 'property', 'og:image:height', (string) $bild['height'] );
		}
		if ( '' !== $bild['alt'] ) {
			$meta[] = array( 'property', 'og:image:alt', $bild['alt'] );
		}
	}
	$meta[] = array( 'name', 'twitter:card', $bild ? 'summary_large_image' : 'summary' );
	$meta[] = array( 'name', 'twitter:title', html_entity_decode( $titel, ENT_QUOTES, 'UTF-8' ) );
	if ( '' !== $beschreibung ) {
		$meta[] = array( 'name', 'twitter:description', $beschreibung );
	}
	if ( $bild ) {
		$meta[] = array( 'name', 'twitter:image', $bild['url'] );
	}
	return $meta;
}

/**
 * Ausgabe im Kopf (nach <title>, vor dem Event-Schema des Themes).
 */
function tamil_site_seo_ausgeben(): void {
	if ( ! tamil_site_seo_aktiv() || is_admin() || is_feed() ) {
		return;
	}
	foreach ( tamil_site_seo_meta() as $m ) {
		$url = in_array( $m[1], array( 'og:url', 'og:image', 'twitter:image' ), true );
		printf( '<meta %s="%s" content="%s">' . "\n", esc_attr( $m[0] ), esc_attr( $m[1] ), $url ? esc_url( $m[2] ) : esc_attr( $m[2] ) );
	}
	foreach ( tamil_site_seo_schema() as $block ) {
		// JSON_HEX_TAG verhindert, dass ein „</script>“ in einem Titel den Block beendet.
		echo '<script type="application/ld+json">' . wp_json_encode( $block, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_HEX_TAG | JSON_HEX_AMP ) . "</script>\n"; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
	}
}
add_action( 'wp_head', 'tamil_site_seo_ausgeben', 5 );

/**
 * Suchergebnisse und Seiten, die sich anmelden, bleiben aus dem Index (z. B. spätere Buchungsseiten über den Filter
 * tamil_site_nicht_indexieren).
 *
 * @param array<string,bool|string> $robots Robots-Angaben.
 * @return array<string,bool|string>
 */
function tamil_site_seo_robots( array $robots ): array {
	/**
	 * Aktuelle Seite aus dem Index nehmen.
	 *
	 * @param bool $nicht Standard: Suchergebnisse und Schlagwörter mit zu wenigen Beiträgen.
	 */
	if ( apply_filters( 'tamil_site_nicht_indexieren', is_search() || tamil_site_seo_duennes_archiv() ) ) {
		$robots['noindex'] = true;
		$robots['follow']  = true;
		unset( $robots['max-image-preview'] );
	}
	return $robots;
}
add_filter( 'wp_robots', 'tamil_site_seo_robots', 20 );

/**
 * Mindestzahl an Beiträgen, ab der ein Schlagwort in den Index und in die Sitemap kommt.
 */
function tamil_site_seo_schlagwort_minimum(): int {
	/**
	 * Mindestzahl Beiträge je Schlagwort.
	 *
	 * @param int $minimum Standard 3.
	 */
	return max( 1, (int) apply_filters( 'tamil_site_seo_schlagwort_minimum', 3 ) );
}

/**
 * Ist die aktuelle Seite ein Schlagwort mit zu wenigen Beiträgen? (Altbestand: 219 von 269 Schlagwörtern haben genau
 * einen Beitrag – solche Seiten sind für Suchmaschinen dünn.)
 */
function tamil_site_seo_duennes_archiv(): bool {
	if ( ! is_tag() ) {
		return false;
	}
	$term = get_queried_object();
	return $term instanceof WP_Term && (int) $term->count < tamil_site_seo_schlagwort_minimum();
}

/**
 * Sitemap von WordPress: keine Benutzer (Autorenarchive gibt es nicht, siehe autoren.php).
 *
 * @param WP_Sitemaps_Provider|mixed $provider Anbieter.
 * @param string                     $name     Name des Anbieters.
 * @return WP_Sitemaps_Provider|mixed|false
 */
function tamil_site_seo_sitemap_anbieter( $provider, $name ) {
	return 'users' === $name ? false : $provider;
}
add_filter( 'wp_sitemaps_add_provider', 'tamil_site_seo_sitemap_anbieter', 10, 2 );

/**
 * Sitemap von WordPress: Schlagwörter nur ab der Mindestzahl an Beiträgen; Rubriken bleiben vollständig.
 *
 * @param array<string,mixed> $args     Abfrage für get_terms().
 * @param string              $taxonomy Taxonomie.
 * @return array<string,mixed>
 */
function tamil_site_seo_sitemap_schlagwoerter( $args, $taxonomy ): array {
	$args = (array) $args;
	if ( 'post_tag' !== $taxonomy ) {
		return $args;
	}
	$minimum = tamil_site_seo_schlagwort_minimum();
	$duenn   = array();
	foreach ( get_terms(
		array(
			'taxonomy'               => 'post_tag',
			'hide_empty'             => false,
			'number'                 => 0,
			'update_term_meta_cache' => false,
		)
	) as $term ) {
		if ( $term instanceof WP_Term && (int) $term->count < $minimum ) {
			$duenn[] = (int) $term->term_id;
		}
	}
	if ( $duenn ) {
		$args['exclude'] = array_values( array_unique( array_merge( array_map( 'intval', (array) ( $args['exclude'] ?? array() ) ), $duenn ) ) );
	}
	return $args;
}
add_filter( 'wp_sitemaps_taxonomies_query_args', 'tamil_site_seo_sitemap_schlagwoerter', 10, 2 );

/**
 * Kanonische Adresse für Startseite, Beitragsseite, Rubriken und Schlagwörter (Folgeseiten verweisen auf sich selbst).
 * Die Startseite blättert nicht (front-page.php zeigt immer dasselbe): /page/2/ verweist auf die Startseite.
 * Einzelseiten bekommen sie weiter von WordPress (rel_canonical), Suchergebnisse keine.
 */
function tamil_site_seo_canonical_url(): string {
	if ( is_singular() || is_search() || is_404() ) {
		return '';
	}
	if ( is_front_page() ) {
		return home_url( '/' );
	}
	if ( is_home() ) {
		$blog  = (int) get_option( 'page_for_posts' );
		$basis = $blog ? (string) get_permalink( $blog ) : home_url( '/' );
	} elseif ( is_category() || is_tag() || is_tax() ) {
		$link  = get_term_link( get_queried_object() );
		$basis = is_wp_error( $link ) ? '' : (string) $link;
	} else {
		return '';
	}
	$seite = max( 1, (int) get_query_var( 'paged' ) );
	if ( '' === $basis || 1 === $seite ) {
		return $basis;
	}
	global $wp_rewrite;
	if ( $wp_rewrite instanceof WP_Rewrite && $wp_rewrite->using_permalinks() ) {
		return trailingslashit( $basis ) . user_trailingslashit( $wp_rewrite->pagination_base . '/' . $seite, 'paged' );
	}
	return add_query_arg( 'paged', $seite, $basis );
}

/**
 * <link rel="canonical"> im Kopf für die Übersichtsseiten.
 */
function tamil_site_seo_canonical(): void {
	if ( ! tamil_site_seo_aktiv() || is_admin() || is_feed() ) {
		return;
	}
	$url = tamil_site_seo_canonical_url();
	if ( '' !== $url ) {
		printf( '<link rel="canonical" href="%s">' . "\n", esc_url( $url ) );
	}
}
add_action( 'wp_head', 'tamil_site_seo_canonical', 6 );
