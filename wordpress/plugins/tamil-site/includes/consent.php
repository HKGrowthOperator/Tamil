<?php
/**
 * Cookie-Zustimmung: eigene Lösung ohne fremden Dienst, hängt am Funktionsschalter „zustimmung“ (aus = heutiges
 * Verhalten: Videos und Streams laden erst nach Klick).
 *
 * Kategorien: notwendig (immer), externe_medien (YouTube, TV-Streams), statistik (vorbereitet, derzeit leer).
 * Die Wahl liegt sechs Monate im Browser des Besuchers (localStorage, sonst ein eigenes Cookie); nichts geht an den
 * Server oder an Dritte, die HTML-Seite ist für alle Besucher gleich und bleibt zwischenspeicherbar.
 * Schnittstelle für Skripte: window.tamilZustimmung.hat( 'externe_medien' ) und das Ereignis „tamil:zustimmung“ am
 * document (assets/consent.js).
 */

defined( 'ABSPATH' ) || exit;

/**
 * Kategorien → Beschriftung.
 *
 * @return array<string,string>
 */
function tamil_site_zustimmung_kategorien(): array {
	return array(
		'notwendig'      => __( 'Notwendig', 'tamil-site' ),
		'externe_medien' => __( 'Externe Medien', 'tamil-site' ),
		'statistik'      => __( 'Statistik', 'tamil-site' ),
	);
}

/**
 * Standardtexte – vorläufige Fassung, bis der Auftraggeber den Text liefert.
 *
 * @return array<string,string>
 */
function tamil_site_zustimmung_standard(): array {
	return array(
		'titel'          => __( 'Cookies und externe Inhalte', 'tamil-site' ),
		'text'           => __( 'Vorläufige Fassung, der endgültige Text folgt. Wir speichern nur, was die Website zum Funktionieren braucht. Videos von YouTube und die Live-Streams der TV-Sender laden erst, wenn Sie zustimmen; dabei werden Daten an den jeweiligen Anbieter übertragen. Ihre Wahl bleibt sechs Monate in Ihrem Browser gespeichert und lässt sich jederzeit über „Cookie-Einstellungen“ im Fuß der Seite ändern.', 'tamil-site' ),
		'notwendig'      => __( 'Für den Betrieb der Website nötig, zum Beispiel diese Einstellung selbst. Immer aktiv.', 'tamil-site' ),
		'externe_medien' => __( 'Videos von YouTube und Live-Streams der TV-Sender laden sofort. Dabei werden Daten an die Anbieter übertragen.', 'tamil-site' ),
		'statistik'      => __( 'Derzeit nicht im Einsatz.', 'tamil-site' ),
		'fassung'        => '2026-11-vorlaeufig',
	);
}

/**
 * Gepflegte Texte, ergänzt um die Standardtexte.
 *
 * @return array<string,string>
 */
function tamil_site_zustimmung_texte(): array {
	$gespeichert = get_option( 'tamil_site_zustimmung', array() );
	$gespeichert = is_array( $gespeichert ) ? array_filter( array_map( 'strval', $gespeichert ), 'strlen' ) : array();
	return array_merge( tamil_site_zustimmung_standard(), array_intersect_key( $gespeichert, tamil_site_zustimmung_standard() ) );
}

/**
 * Bereinigung für das Einstellungsformular (nur Text, keine Auszeichnung).
 *
 * @param mixed $input Formularwerte.
 * @return array<string,string>
 */
function tamil_site_sanitize_zustimmung( $input ): array {
	$input = is_array( $input ) ? $input : array();
	$out   = array();
	foreach ( array_keys( tamil_site_zustimmung_standard() ) as $key ) {
		$wert = (string) ( $input[ $key ] ?? '' );
		if ( 'fassung' === $key ) {
			$out[ $key ] = substr( sanitize_key( str_replace( '.', '-', $wert ) ), 0, 40 );
		} elseif ( 'titel' === $key ) {
			$out[ $key ] = sanitize_text_field( $wert );
		} else {
			$out[ $key ] = sanitize_textarea_field( $wert );
		}
	}
	return $out;
}

/**
 * Skript und Stil, nur wenn der Schalter an ist.
 */
function tamil_site_zustimmung_assets(): void {
	if ( ! tamil_site_funktion_an( 'zustimmung' ) ) {
		return;
	}
	$css = 'assets/consent.css';
	$js  = 'assets/consent.js';
	wp_enqueue_style( 'tamil-site-consent', TAMIL_SITE_URL . $css, array(), TAMIL_SITE_VERSION . '.' . filemtime( TAMIL_SITE_DIR . $css ) );
	wp_enqueue_script(
		'tamil-site-consent',
		TAMIL_SITE_URL . $js,
		array(),
		TAMIL_SITE_VERSION . '.' . filemtime( TAMIL_SITE_DIR . $js ),
		array(
			'strategy'  => 'defer',
			'in_footer' => true,
		)
	);
}
add_action( 'wp_enqueue_scripts', 'tamil_site_zustimmung_assets' );

/**
 * Link „Cookie-Einstellungen“ im Fuß (Hook des Themes).
 */
function tamil_site_zustimmung_link(): void {
	if ( ! tamil_site_funktion_an( 'zustimmung' ) ) {
		return;
	}
	echo '<a href="#cookie-einstellungen" class="tz-link" data-tz-oeffnen>' . esc_html__( 'Cookie-Einstellungen', 'tamil-site' ) . '</a>';
}
add_action( 'tamil_footer_legal', 'tamil_site_zustimmung_link' );

/**
 * Link auf die Datenschutzerklärung, falls veröffentlicht.
 */
function tamil_site_zustimmung_datenschutz_url(): string {
	$id = (int) get_option( 'wp_page_for_privacy_policy' );
	if ( $id && 'publish' === get_post_status( $id ) ) {
		return (string) get_permalink( $id );
	}
	$seite = get_page_by_path( 'datenschutz', OBJECT, 'page' );
	return $seite instanceof WP_Post && 'publish' === $seite->post_status ? (string) get_permalink( $seite ) : '';
}

/**
 * Hinweis und Einstellungsdialog am Ende der Seite. Beide sind zunächst verborgen; consent.js zeigt den Hinweis,
 * solange keine gültige Wahl im Browser liegt.
 */
function tamil_site_zustimmung_ausgeben(): void {
	if ( ! tamil_site_funktion_an( 'zustimmung' ) || is_admin() ) {
		return;
	}
	$t           = tamil_site_zustimmung_texte();
	$datenschutz = tamil_site_zustimmung_datenschutz_url();
	?>
	<div class="tz-hinweis" data-tz-hinweis data-fassung="<?php echo esc_attr( $t['fassung'] ); ?>" role="region" aria-labelledby="tz-titel" hidden>
		<h2 class="tz-titel" id="tz-titel"><?php echo esc_html( $t['titel'] ); ?></h2>
		<p class="tz-text"><?php echo esc_html( $t['text'] ); ?>
			<?php if ( $datenschutz ) : ?>
			<a href="<?php echo esc_url( $datenschutz ); ?>"><?php esc_html_e( 'Datenschutzerklärung', 'tamil-site' ); ?></a>
			<?php endif; ?>
		</p>
		<div class="tz-knoepfe">
			<button type="button" class="tz-knopf tz-knopf-haupt" data-tz-alle><?php esc_html_e( 'Alle akzeptieren', 'tamil-site' ); ?></button>
			<button type="button" class="tz-knopf" data-tz-notwendig><?php esc_html_e( 'Nur notwendige', 'tamil-site' ); ?></button>
			<button type="button" class="tz-knopf tz-knopf-leise" data-tz-oeffnen><?php esc_html_e( 'Einstellungen', 'tamil-site' ); ?></button>
		</div>
	</div>
	<dialog class="tz-dialog" id="cookie-einstellungen" aria-labelledby="tz-dialog-titel">
		<form method="dialog" class="tz-form">
			<h2 class="tz-titel" id="tz-dialog-titel"><?php esc_html_e( 'Cookie-Einstellungen', 'tamil-site' ); ?></h2>
			<p class="tz-text"><?php echo esc_html( $t['text'] ); ?></p>
			<fieldset class="tz-kategorien">
				<legend class="tz-unsichtbar"><?php esc_html_e( 'Kategorien', 'tamil-site' ); ?></legend>
				<?php foreach ( tamil_site_zustimmung_kategorien() as $key => $label ) : ?>
				<label class="tz-kategorie">
					<input type="checkbox" name="tz-<?php echo esc_attr( $key ); ?>" value="1" <?php echo 'notwendig' === $key ? 'checked disabled' : ''; ?>>
					<span><strong><?php echo esc_html( $label ); ?></strong> <?php echo esc_html( $t[ $key ] ); ?></span>
				</label>
				<?php endforeach; ?>
			</fieldset>
			<div class="tz-knoepfe">
				<button type="button" class="tz-knopf tz-knopf-haupt" data-tz-speichern><?php esc_html_e( 'Auswahl speichern', 'tamil-site' ); ?></button>
				<button type="button" class="tz-knopf" data-tz-alle><?php esc_html_e( 'Alle akzeptieren', 'tamil-site' ); ?></button>
				<button type="button" class="tz-knopf" data-tz-notwendig><?php esc_html_e( 'Nur notwendige', 'tamil-site' ); ?></button>
			</div>
		</form>
	</dialog>
	<?php
}
add_action( 'wp_footer', 'tamil_site_zustimmung_ausgeben', 5 );
