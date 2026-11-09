<?php
/**
 * Eingabemaske „Vorspann und Termin“ im Beitragseditor: Vorspann, Ort und die Angaben einer Veranstaltung.
 * Die Kinoliste (kino_fakten) pflegt der News-Radar; hier wird sie nur angezeigt.
 */

defined( 'ABSPATH' ) || exit;

function tamil_site_add_metabox(): void {
	add_meta_box( 'tamil-site-termin', __( 'Vorspann und Termin', 'tamil-site' ), 'tamil_site_render_metabox', 'post', 'normal', 'high' );
}
add_action( 'add_meta_boxes', 'tamil_site_add_metabox' );

/**
 * Wert für <input type="datetime-local"> (Y-m-d\TH:i) bzw. leer.
 */
function tamil_site_datetime_input( string $value ): string {
	if ( '' === $value ) {
		return '';
	}
	return strlen( $value ) === 10 ? $value . 'T00:00' : str_replace( ' ', 'T', $value );
}

function tamil_site_render_metabox( WP_Post $post ): void {
	wp_nonce_field( 'tamil_site_metabox', 'tamil_site_nonce' );
	$get   = static fn( string $key ): string => (string) get_post_meta( $post->ID, $key, true );
	$kino  = tamil_site_get_json( $post->ID, 'kino_fakten' );
	$field = static function ( string $key, string $label, string $html, string $hilfe = '' ): void {
		echo '<p class="tamil-site-feld"><label for="tamil-site-' . esc_attr( $key ) . '"><strong>' . esc_html( $label ) . '</strong></label><br>';
		echo $html; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- unten gebaut und escaped
		if ( $hilfe ) {
			echo '<br><span class="description">' . esc_html( $hilfe ) . '</span>';
		}
		echo '</p>';
	};
	$input = static fn( string $key, string $type = 'text', string $value = '', string $extra = '' ): string => sprintf(
		'<input type="%1$s" id="tamil-site-%2$s" name="tamil_site[%2$s]" value="%3$s" class="widefat" %4$s>',
		esc_attr( $type ),
		esc_attr( $key ),
		esc_attr( $value ),
		$extra
	);

	$field(
		'standfirst',
		__( 'Vorspann', 'tamil-site' ),
		'<textarea id="tamil-site-standfirst" name="tamil_site[standfirst]" rows="3" class="widefat">' . esc_textarea( $get( 'standfirst' ) ) . '</textarea>',
		__( 'Zwei, drei Sätze unter der Überschrift. Leer = Textauszug.', 'tamil-site' )
	);
	$field( 'ort', __( 'Ort der Meldung', 'tamil-site' ), $input( 'ort', 'text', $get( 'ort' ), 'placeholder="Hamm, Zürich, Wien …"' ) );

	echo '<hr><h4 style="margin:12px 0 4px">' . esc_html__( 'Veranstaltung (nur ausfüllen, wenn der Beitrag ein Termin ist)', 'tamil-site' ) . '</h4>';
	echo '<div class="tamil-site-raster" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:0 16px">';
	$field( 'event_datum', __( 'Beginn', 'tamil-site' ), $input( 'event_datum', 'datetime-local', tamil_site_datetime_input( $get( 'event_datum' ) ) ) );
	$field( 'event_ende', __( 'Ende (optional)', 'tamil-site' ), $input( 'event_ende', 'datetime-local', tamil_site_datetime_input( $get( 'event_ende' ) ) ) );
	$field( 'event_ort', __( 'Veranstaltungsort', 'tamil-site' ), $input( 'event_ort', 'text', $get( 'event_ort' ), 'placeholder="Halle, Stadt"' ) );
	$land    = $get( 'event_land' );
	$options = '<option value="">' . esc_html__( '– Land –', 'tamil-site' ) . '</option>';
	foreach ( tamil_site_laender() as $code => $label ) {
		$options .= sprintf( '<option value="%1$s"%2$s>%3$s</option>', esc_attr( $code ), selected( $land, $code, false ), esc_html( $label ) );
	}
	$field( 'event_land', __( 'Land', 'tamil-site' ), '<select id="tamil-site-event_land" name="tamil_site[event_land]" class="widefat">' . $options . '</select>' );
	$field( 'event_veranstalter', __( 'Veranstalter', 'tamil-site' ), $input( 'event_veranstalter', 'text', $get( 'event_veranstalter' ) ) );
	$field( 'event_preis', __( 'Preis', 'tamil-site' ), $input( 'event_preis', 'text', $get( 'event_preis' ), 'placeholder="ab 25 €, Eintritt frei …"' ) );
	$field( 'ticket_url', __( 'Ticket- oder Info-Link', 'tamil-site' ), $input( 'ticket_url', 'url', $get( 'ticket_url' ), 'placeholder="https://"' ) );
	$field( 'ticket_label', __( 'Beschriftung des Knopfs', 'tamil-site' ), $input( 'ticket_label', 'text', $get( 'ticket_label' ), 'placeholder="Tickets"' ) );
	echo '</div>';

	if ( $kino ) {
		$anzahl = is_array( $kino['kinos'] ?? null ) ? count( $kino['kinos'] ) : 0;
		echo '<hr><p><strong>' . esc_html__( 'Kinoliste', 'tamil-site' ) . '</strong><br>';
		/* translators: 1: Filmtitel, 2: Anzahl Kinos, 3: Kinowoche */
		echo esc_html( sprintf( __( '„%1$s“ – %2$d Spielorte, Kinowoche %3$s. Wird vom News-Radar aktualisiert.', 'tamil-site' ), (string) ( $kino['film'] ?? '' ), $anzahl, (string) ( $kino['woche'] ?? '' ) ) );
		echo '</p>';
	}
}

function tamil_site_save_metabox( int $post_id ): void {
	if ( ! isset( $_POST['tamil_site_nonce'] ) || ! wp_verify_nonce( sanitize_key( wp_unslash( $_POST['tamil_site_nonce'] ) ), 'tamil_site_metabox' ) ) {
		return;
	}
	if ( ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) || ! current_user_can( 'edit_post', $post_id ) ) {
		return;
	}
	$input = isset( $_POST['tamil_site'] ) && is_array( $_POST['tamil_site'] ) ? wp_unslash( $_POST['tamil_site'] ) : array(); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput.InputNotSanitized -- je Feld unten
	foreach ( tamil_site_meta_keys() as $key => $type ) {
		if ( 'json' === $type || ! array_key_exists( $key, $input ) ) {
			continue;
		}
		$value = tamil_site_sanitize_meta( $input[ $key ], $type );
		if ( '' === $value ) {
			delete_post_meta( $post_id, $key );
		} else {
			update_post_meta( $post_id, $key, $value );
		}
	}
}
add_action( 'save_post_post', 'tamil_site_save_metabox' );
