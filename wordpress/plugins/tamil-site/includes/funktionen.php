<?php
/**
 * Funktionsschalter: je Baustein ein Schalter, Standard aus. Im Echtbetrieb bleibt ein Baustein aus, bis
 * Auftragsverarbeitung und Rechtstexte vorliegen; eingeschaltet wird unter Einstellungen → Tamil.de Website.
 *
 * Nur in lokaler Umgebung (WP_ENVIRONMENT_TYPE local oder development) dürfen Tests einen Schalter für einen
 * einzelnen Aufruf einschalten: Kopfzeile `X-Tamil-Funktionen: zustimmung,werbung`.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Bekannte Schalter → Beschriftung.
 *
 * @return array<string,string>
 */
function tamil_site_funktionen(): array {
	return array(
		'einreichungen' => __( 'Einreichungen', 'tamil-site' ),
		'verzeichnis'   => __( 'Verzeichnis', 'tamil-site' ),
		'werbung'       => __( 'Werbebuchung', 'tamil-site' ),
		'zustimmung'    => __( 'Cookie-Zustimmung', 'tamil-site' ),
	);
}

/**
 * Gespeicherte Schalter (nur bekannte Namen, alle Werte bool).
 *
 * @return array<string,bool>
 */
function tamil_site_funktionen_stand(): array {
	$gespeichert = get_option( 'tamil_site_funktionen', array() );
	$gespeichert = is_array( $gespeichert ) ? $gespeichert : array();
	$stand       = array();
	foreach ( array_keys( tamil_site_funktionen() ) as $name ) {
		$stand[ $name ] = ! empty( $gespeichert[ $name ] );
	}
	return $stand;
}

/**
 * Ist der Baustein $name eingeschaltet?
 */
function tamil_site_funktion_an( string $name ): bool {
	if ( ! array_key_exists( $name, tamil_site_funktionen() ) ) {
		return false;
	}
	if ( in_array( $name, tamil_site_funktionen_test(), true ) ) {
		return true;
	}
	$an = tamil_site_funktionen_stand()[ $name ];
	/**
	 * Schalter von außen überschreiben (z. B. in einem Test-Plugin).
	 *
	 * @param bool   $an   Stand.
	 * @param string $name Baustein.
	 */
	return (bool) apply_filters( 'tamil_site_funktion_an', $an, $name );
}

/**
 * Für diesen Aufruf eingeschaltete Schalter aus der Test-Kopfzeile – nur lokal, sonst immer leer.
 *
 * @param string|null $umgebung Umgebung (Standard: wp_get_environment_type()).
 * @return array<int,string>
 */
function tamil_site_funktionen_test( ?string $umgebung = null ): array {
	if ( ! in_array( $umgebung ?? wp_get_environment_type(), array( 'local', 'development' ), true ) ) {
		return array();
	}
	$kopf = isset( $_SERVER['HTTP_X_TAMIL_FUNKTIONEN'] ) ? sanitize_text_field( wp_unslash( $_SERVER['HTTP_X_TAMIL_FUNKTIONEN'] ) ) : '';
	if ( '' === $kopf ) {
		return array();
	}
	return array_values( array_intersect( array_map( 'sanitize_key', explode( ',', $kopf ) ), array_keys( tamil_site_funktionen() ) ) );
}

/**
 * Bereinigung für das Einstellungsformular: nicht angehakt = aus.
 *
 * @param mixed $input Formularwerte.
 * @return array<string,bool>
 */
function tamil_site_sanitize_funktionen( $input ): array {
	$input = is_array( $input ) ? $input : array();
	$out   = array();
	foreach ( array_keys( tamil_site_funktionen() ) as $name ) {
		$out[ $name ] = ! empty( $input[ $name ] );
	}
	return $out;
}
