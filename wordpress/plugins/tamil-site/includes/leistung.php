<?php
/**
 * Tempo: Cache-Kopfzeilen für die HTML-Seiten.
 *
 * Nicht angemeldete Besucher bekommen Seiten bei GET 60 Sekunden aus dem Browser-Speicher (kurz genug, dass neue
 * Beiträge schnell erscheinen). Suchergebnisse und Seiten, die sich über den Filter tamil_site_nie_zwischenspeichern
 * anmelden (spätere Formular- und Buchungsseiten), werden nie zwischengespeichert. Angemeldete Benutzer, Verwaltung
 * und REST bleiben, wie WordPress sie ausliefert. Statische Dateien regelt Apache (wordpress/Dockerfile).
 */

defined( 'ABSPATH' ) || exit;

/**
 * Sekunden, die eine HTML-Seite für Gäste im Browser-Speicher bleiben darf.
 */
define( 'TAMIL_SITE_HTML_MAX_AGE', 60 );

/**
 * Regel für Cache-Control.
 *
 * @param bool $angemeldet Benutzer ist angemeldet.
 * @param bool $suche      Suchergebnisse.
 * @param bool $nie        Seite hat sich als „nie zwischenspeichern“ angemeldet.
 * @return string Wert der Kopfzeile; leer = nichts ändern.
 */
function tamil_site_cache_regel( bool $angemeldet, bool $suche, bool $nie ): string {
	if ( $angemeldet ) {
		return '';
	}
	if ( $suche || $nie ) {
		return 'no-store';
	}
	return 'public, max-age=' . TAMIL_SITE_HTML_MAX_AGE;
}

/**
 * Setzt die Kopfzeile für die aktuelle Seite (spät in template_redirect, nach den Weiterleitungen).
 */
function tamil_site_cache_kopfzeilen(): void {
	$methode = isset( $_SERVER['REQUEST_METHOD'] ) ? strtoupper( sanitize_key( wp_unslash( $_SERVER['REQUEST_METHOD'] ) ) ) : '';
	if ( ! in_array( $methode, array( 'GET', 'HEAD' ), true ) || is_admin() || headers_sent() ) {
		return;
	}
	if ( wp_doing_ajax() || ( defined( 'REST_REQUEST' ) && REST_REQUEST ) || is_preview() || is_customize_preview() ) {
		return;
	}
	// Persönliche Inhalte für Gäste: geschützte Beiträge und eigene, noch nicht freigegebene Kommentare.
	$persoenlich = ( is_singular() && post_password_required() ) || ! empty( wp_get_current_commenter()['comment_author_email'] );
	/**
	 * Aktuelle Seite nie zwischenspeichern (Formulare, Buchung, persönliche Antworten).
	 *
	 * @param bool $nie Standard false.
	 */
	$nie   = (bool) apply_filters( 'tamil_site_nie_zwischenspeichern', $persoenlich );
	$regel = tamil_site_cache_regel( is_user_logged_in(), is_search(), $nie );
	if ( '' === $regel ) {
		return;
	}
	header( 'Cache-Control: ' . $regel );
	if ( 'no-store' !== $regel ) {
		header_remove( 'Pragma' );
		header_remove( 'Expires' );
	}
}
add_action( 'template_redirect', 'tamil_site_cache_kopfzeilen', 99 );
