<?php
/**
 * Testsysteme bleiben aus dem Index: Ist die Umgebung nicht `production` (der Container setzt standardmäßig
 * `staging`, lokal gilt `local`), dann gilt überall noindex, nofollow – im Kopf jeder Seite, als Kopfzeile
 * X-Robots-Tag, in robots.txt (Disallow: /, ohne Sitemap) und ohne die Sitemap von WordPress. Sonst trüge die
 * Vorschau-Website die Beiträge der echten tamil.de als doppelte Inhalte in die Suchmaschinen.
 * OpenGraph und JSON-LD bleiben (Vorschauen beim Teilen, Prüfung der Angaben).
 * In `production` ändert diese Datei nichts.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Darf die Website indexiert werden? Nur in `production`.
 *
 * @param string|null $umgebung Umgebung (Standard: wp_get_environment_type()).
 */
function tamil_site_indexierbar( ?string $umgebung = null ): bool {
	$an = 'production' === ( $umgebung ?? wp_get_environment_type() );
	/**
	 * Indexierbarkeit überschreiben (Tests, Sonderfälle).
	 *
	 * @param bool $an Stand.
	 */
	return (bool) apply_filters( 'tamil_site_indexierbar', $an );
}

/**
 * Robots-Angaben im Kopf.
 *
 * @param array<string,bool|string> $robots Robots-Angaben.
 * @return array<string,bool|string>
 */
function tamil_site_indexierung_robots( array $robots ): array {
	if ( tamil_site_indexierbar() ) {
		return $robots;
	}
	unset( $robots['follow'], $robots['index'], $robots['max-image-preview'] );
	$robots['noindex']  = true;
	$robots['nofollow'] = true;
	return $robots;
}
add_filter( 'wp_robots', 'tamil_site_indexierung_robots', 99 );

/**
 * Wert der Kopfzeile X-Robots-Tag (leer = keine).
 */
function tamil_site_robots_kopfzeile(): string {
	return tamil_site_indexierbar() ? '' : 'noindex, nofollow';
}

/**
 * Kopfzeile für alle Antworten des Frontends (Seiten, Feeds, robots.txt).
 */
function tamil_site_indexierung_kopfzeile(): void {
	$wert = tamil_site_robots_kopfzeile();
	if ( '' !== $wert && ! headers_sent() ) {
		header( 'X-Robots-Tag: ' . $wert );
	}
}
add_action( 'send_headers', 'tamil_site_indexierung_kopfzeile' );

/**
 * robots.txt: auf Testsystemen alles sperren, ohne Sitemap-Zeile.
 *
 * @param string $ausgabe Bisheriger Inhalt.
 * @param mixed  $oeffentlich Einstellung „Suchmaschinen erlauben“.
 */
function tamil_site_robots_txt( $ausgabe, $oeffentlich ): string {
	unset( $oeffentlich );
	if ( tamil_site_indexierbar() ) {
		return (string) $ausgabe;
	}
	return "User-agent: *\nDisallow: /\n";
}
add_filter( 'robots_txt', 'tamil_site_robots_txt', 99, 2 );

/**
 * Sitemap von WordPress nur in `production`.
 *
 * @param bool $an Stand.
 */
function tamil_site_indexierung_sitemaps( $an ): bool {
	return tamil_site_indexierbar() ? (bool) $an : false;
}
add_filter( 'wp_sitemaps_enabled', 'tamil_site_indexierung_sitemaps', 99 );
