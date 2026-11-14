<?php
/**
 * Verzeichnis in wp-admin: Eingabemaske der Felder eines Eintrags (Redaktion) und die Markierung „Premium“, die nur
 * ein Administrator (manage_options) setzen kann. Weder das Formular noch die Schnittstelle des Radars schreiben
 * Premium.
 */

defined( 'ABSPATH' ) || exit;

function tamil_site_vz_metabox_anmelden(): void {
	add_meta_box( 'tamil-vz-felder', __( 'Angaben im Verzeichnis', 'tamil-site' ), 'tamil_site_vz_metabox', TAMIL_SITE_VZ_TYP, 'normal', 'high' );
}
add_action( 'add_meta_boxes', 'tamil_site_vz_metabox_anmelden' );

/**
 * Eingabemaske.
 *
 * @param WP_Post $post Eintrag.
 */
function tamil_site_vz_metabox( $post ): void {
	$w = (array) tamil_site_vz_eintrag_werte( (int) $post->ID );
	wp_nonce_field( 'tamil_vz_admin_' . $post->ID, 'tamil_vz_admin_nonce' );
	echo '<p>' . esc_html__( 'Name und Beschreibung stehen in Titel und Inhalt. Pflicht: Art, PLZ, Stadt, Land und mindestens Telefon, E-Mail oder Website.', 'tamil-site' ) . '</p><table class="form-table">';
	foreach ( tamil_site_vz_felder() as $key => $feld ) {
		if ( in_array( $key, array( 'name', 'beschreibung' ), true ) ) {
			continue;
		}
		$wert = (string) ( $w[ $key ] ?? '' );
		echo '<tr><th><label for="tamil-vz-' . esc_attr( $key ) . '">' . esc_html( $feld['label'] ) . '</label></th><td>';
		if ( 'textarea' === $feld['typ'] ) {
			echo '<textarea class="large-text" rows="3" id="tamil-vz-' . esc_attr( $key ) . '" name="tamil_vz[' . esc_attr( $key ) . ']">' . esc_textarea( $wert ) . '</textarea>';
		} elseif ( in_array( $feld['typ'], array( 'art', 'land', 'kategorie' ), true ) ) {
			$optionen = array(
				'art'       => tamil_site_vz_arten(),
				'land'      => tamil_site_vz_laender(),
				'kategorie' => tamil_site_vz_kategorie_optionen(),
			)[ $feld['typ'] ];
			echo '<select id="tamil-vz-' . esc_attr( $key ) . '" name="tamil_vz[' . esc_attr( $key ) . ']"><option value="">–</option>';
			foreach ( $optionen as $code => $label ) {
				echo '<option value="' . esc_attr( (string) $code ) . '"' . selected( $wert, (string) $code, false ) . '>' . esc_html( $label ) . '</option>';
			}
			echo '</select>';
		} else {
			echo '<input class="regular-text" type="text" id="tamil-vz-' . esc_attr( $key ) . '" name="tamil_vz[' . esc_attr( $key ) . ']" value="' . esc_attr( $wert ) . '">';
		}
		echo '</td></tr>';
	}
	echo '<tr><th>' . esc_html__( 'Premium', 'tamil-site' ) . '</th><td>';
	if ( current_user_can( 'manage_options' ) ) {
		echo '<label><input type="checkbox" name="tamil_vz_premium" value="1"' . checked( tamil_site_vz_premium( (int) $post->ID ), true, false ) . '> ' . esc_html__( 'Premium (oben in den Listen, sichtbar gekennzeichnet)', 'tamil-site' ) . '</label>';
	} else {
		echo esc_html( tamil_site_vz_premium( (int) $post->ID ) ? __( 'ja (setzt nur ein Administrator)', 'tamil-site' ) : __( 'nein (setzt nur ein Administrator)', 'tamil-site' ) );
	}
	echo '</td></tr></table>';
}

/**
 * Speichern aus der Eingabemaske (Nonce, Recht am Eintrag; Premium nur mit manage_options).
 *
 * @param int $post_id Eintrag.
 */
function tamil_site_vz_metabox_speichern( $post_id ): void {
	$post_id = (int) $post_id;
	if ( ! isset( $_POST['tamil_vz_admin_nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['tamil_vz_admin_nonce'] ) ), 'tamil_vz_admin_' . $post_id ) ) {
		return;
	}
	if ( ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) || wp_is_post_revision( $post_id ) || ! current_user_can( 'edit_post', $post_id ) ) {
		return;
	}
	if ( ! tamil_site_vz_sperren( $post_id ) ) {
		set_transient( 'tamil_vz_admin_fehler_' . get_current_user_id(), array( 'sperre' => __( 'Der Eintrag wird gerade über die Freigabe geändert. Bitte gleich noch einmal speichern.', 'tamil-site' ) ), 60 );
		return;
	}
	try {
		tamil_site_vz_metabox_felder_speichern( $post_id );
	} finally {
		tamil_site_vz_entsperren( $post_id );
	}
}

/**
 * Felder aus der Eingabemaske schreiben (unter der Sperre, Nonce und Recht sind geprüft).
 */
function tamil_site_vz_metabox_felder_speichern( int $post_id ): void {
	$roh = isset( $_POST['tamil_vz'] ) && is_array( $_POST['tamil_vz'] ) ? wp_unslash( $_POST['tamil_vz'] ) : array(); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput.InputNotSanitized, WordPress.Security.NonceVerification.Missing -- Nonce in tamil_site_vz_metabox_speichern(), bereinigt in tamil_site_vz_werte_pruefen()
	unset( $roh['name'], $roh['beschreibung'] );
	$gepr  = tamil_site_vz_werte_pruefen( (array) $roh );
	$werte = array_diff_key( $gepr['werte'], $gepr['fehler'] );
	remove_action( 'save_post_' . TAMIL_SITE_VZ_TYP, 'tamil_site_vz_metabox_speichern' );
	foreach ( $werte as $key => $wert ) {
		if ( 'kategorie' === $key ) {
			wp_set_object_terms( $post_id, '' === $wert ? array() : array( $wert ), TAMIL_SITE_VZ_KATEGORIE );
			continue;
		}
		update_post_meta( $post_id, '_tamil_vz_' . $key, wp_slash( $wert ) );
	}
	update_post_meta( $post_id, '_tamil_vz_telefon_norm', tamil_site_vz_telefon_norm( (string) get_post_meta( $post_id, '_tamil_vz_telefon', true ) ) );
	update_post_meta( $post_id, '_tamil_vz_website_host', tamil_site_vz_website_host( (string) get_post_meta( $post_id, '_tamil_vz_website', true ) ) );
	if ( current_user_can( 'manage_options' ) ) {
		update_post_meta( $post_id, '_tamil_vz_premium', empty( $_POST['tamil_vz_premium'] ) ? '0' : '1' ); // phpcs:ignore WordPress.Security.NonceVerification.Missing -- Nonce in tamil_site_vz_metabox_speichern()
	} elseif ( '' === (string) get_post_meta( $post_id, '_tamil_vz_premium', true ) ) {
		update_post_meta( $post_id, '_tamil_vz_premium', '0' );
	}
	tamil_site_vz_protokoll( 'admin', '', $post_id, implode( ',', array_keys( $werte ) ) );
	if ( $gepr['fehler'] ) {
		set_transient( 'tamil_vz_admin_fehler_' . get_current_user_id(), $gepr['fehler'], 60 );
	}
}
add_action( 'save_post_' . TAMIL_SITE_VZ_TYP, 'tamil_site_vz_metabox_speichern' );

/**
 * Hinweis auf nicht gespeicherte Felder nach dem Speichern.
 */
function tamil_site_vz_admin_hinweis(): void {
	$fehler = get_transient( 'tamil_vz_admin_fehler_' . get_current_user_id() );
	if ( ! is_array( $fehler ) || ! $fehler ) {
		return;
	}
	delete_transient( 'tamil_vz_admin_fehler_' . get_current_user_id() );
	echo '<div class="notice notice-error"><p>' . esc_html__( 'Nicht gespeichert:', 'tamil-site' ) . '</p><ul>';
	foreach ( $fehler as $key => $text ) {
		echo '<li>' . esc_html( ( tamil_site_vz_felder()[ $key ]['label'] ?? $key ) . ': ' . $text ) . '</li>';
	}
	echo '</ul></div>';
}
add_action( 'admin_notices', 'tamil_site_vz_admin_hinweis' );
