<?php
/**
 * Autoren nach außen: Die Website nennt als Autor die Redaktion (Autorenzeile, Schema, Feed), nie den Benutzer, unter
 * dem ein Beitrag angelegt ist. Anmeldenamen bleiben intern: keine Autorenarchive und keine öffentliche Benutzerliste
 * über die REST-Schnittstelle.
 *
 * Hintergrund (Prüfung 12.11.2026): Der übernommene Altbestand läuft auf einem Benutzer, Radar-Beiträge auf dem
 * Benutzer des Radars. Ohne diese Datei standen deren Anmeldenamen im Schema, im Feed (dc:creator), unter
 * /author/<name>/ und in /wp-json/wp/v2/users.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Feeds: Autor wie in der Autorenzeile.
 *
 * @param string|null $name Anzeigename des Benutzers.
 */
function tamil_site_autor_im_feed( $name ): string {
	return is_feed() && function_exists( 'tamil_site_seo_autor_name' ) ? tamil_site_seo_autor_name() : (string) $name;
}
add_filter( 'the_author', 'tamil_site_autor_im_feed' );

/**
 * Gibt es öffentliche Autorenarchive? Standard nein (die Website hat eine Autorenzeile ohne Profilseiten).
 */
function tamil_site_autorenarchive(): bool {
	/**
	 * Autorenarchive erlauben (z. B. sobald es Profile der Redaktion gibt).
	 *
	 * @param bool $an Standard false.
	 */
	return (bool) apply_filters( 'tamil_site_autorenarchive', false );
}

/**
 * /author/<name>/ und ?author=<id> leiten dauerhaft auf die Startseite (vor redirect_canonical, das ?author=1 sonst
 * auf den Anmeldenamen umleiten würde).
 */
function tamil_site_autorenarchiv_umleiten(): void {
	if ( is_author() && ! tamil_site_autorenarchive() ) {
		wp_safe_redirect( home_url( '/' ), 301, 'Tamil.de' );
		exit;
	}
}
add_action( 'template_redirect', 'tamil_site_autorenarchiv_umleiten', 1 );

/**
 * REST: Benutzerliste und einzelne Benutzer nur für Angemeldete (Anwendungspasswort oder Cookie mit Nonce). Der
 * Block-Editor (Autorenauswahl) und der Radar (users/me) sind angemeldet und merken davon nichts.
 *
 * @param mixed           $ergebnis Bisheriges Ergebnis (null = normal weiter).
 * @param WP_REST_Server  $server   Server.
 * @param WP_REST_Request $request  Anfrage.
 * @return mixed
 */
function tamil_site_benutzer_rest( $ergebnis, $server, $request ) {
	unset( $server );
	if ( null !== $ergebnis || ! $request instanceof WP_REST_Request ) {
		return $ergebnis;
	}
	$route = untrailingslashit( (string) $request->get_route() );
	if ( preg_match( '#^/wp/v2/users(/|$)#', $route ) && ! is_user_logged_in() ) {
		return new WP_Error( 'rest_not_logged_in', __( 'Nur für angemeldete Benutzer.', 'tamil-site' ), array( 'status' => 401 ) );
	}
	return $ergebnis;
}
add_filter( 'rest_pre_dispatch', 'tamil_site_benutzer_rest', 10, 3 );

/**
 * oEmbed (Vorschau beim Einbetten eines Beitrags): Autor wie in der Autorenzeile, Verweis auf die Startseite.
 *
 * @param array<string,mixed> $daten Antwort.
 * @return array<string,mixed>
 */
function tamil_site_autor_im_oembed( $daten ): array {
	$daten = (array) $daten;
	if ( isset( $daten['author_name'] ) || isset( $daten['author_url'] ) ) {
		$daten['author_name'] = function_exists( 'tamil_site_seo_autor_name' ) ? tamil_site_seo_autor_name() : '';
		$daten['author_url']  = home_url( '/' );
	}
	return $daten;
}
add_filter( 'oembed_response_data', 'tamil_site_autor_im_oembed', 20 );
