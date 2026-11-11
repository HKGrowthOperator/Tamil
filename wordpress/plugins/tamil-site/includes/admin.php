<?php
/**
 * Einstellungen → Tamil.de Website: Funktionsschalter, Werbeplätze und 301-Weiterleitungen.
 *
 * Alle Optionen dieser Seite stehen in einer Gruppe; options.php speichert jede registrierte Option der Gruppe, darum
 * muss jede hier registrierte Option auch im Formular stehen.
 */

defined( 'ABSPATH' ) || exit;

function tamil_site_admin_menu(): void {
	add_options_page( __( 'Tamil.de Website', 'tamil-site' ), __( 'Tamil.de Website', 'tamil-site' ), 'manage_options', 'tamil-site', 'tamil_site_page_settings' );
}
add_action( 'admin_menu', 'tamil_site_admin_menu' );

function tamil_site_register_settings(): void {
	register_setting(
		'tamil_site',
		'tamil_site_settings',
		array(
			'type'              => 'array',
			'sanitize_callback' => 'tamil_site_sanitize_settings',
			'default'           => array(),
		)
	);
	register_setting(
		'tamil_site',
		'tamil_site_funktionen',
		array(
			'type'              => 'array',
			'sanitize_callback' => 'tamil_site_sanitize_funktionen',
			'default'           => array(),
		)
	);
	register_setting(
		'tamil_site',
		'tamil_site_seo',
		array(
			'type'              => 'array',
			'sanitize_callback' => 'tamil_site_sanitize_seo',
			'default'           => array(),
		)
	);
	register_setting(
		'tamil_site',
		'tamil_site_zustimmung',
		array(
			'type'              => 'array',
			'sanitize_callback' => 'tamil_site_sanitize_zustimmung',
			'default'           => array(),
		)
	);
	register_setting(
		'tamil_site',
		'tamil_site_redirects_csv',
		array(
			'type'              => 'string',
			'sanitize_callback' => 'tamil_site_sanitize_redirects_csv',
			'default'           => '',
		)
	);
}
add_action( 'admin_init', 'tamil_site_register_settings' );

function tamil_site_sanitize_settings( $input ): array {
	$input = is_array( $input ) ? $input : array();
	$out   = array(
		'anzeigen'     => array(),
		'advanced_ads' => array(),
		'eigen'        => array(),
		'whatsapp_url' => esc_url_raw( (string) ( $input['whatsapp_url'] ?? '' ) ),
	);
	foreach ( array_keys( tamil_site_werbeplaetze() ) as $platz ) {
		// Banner-HTML ungefiltert nur mit unfiltered_html (Administratoren einer Einzelinstallation).
		$html                          = (string) ( $input['anzeigen'][ $platz ] ?? '' );
		$out['anzeigen'][ $platz ]     = current_user_can( 'unfiltered_html' ) ? trim( $html ) : wp_kses_post( $html );
		$out['advanced_ads'][ $platz ] = sanitize_text_field( (string) ( $input['advanced_ads'][ $platz ] ?? '' ) );
		$vorlage                       = sanitize_key( (string) ( $input['eigen'][ $platz ] ?? '' ) );
		$out['eigen'][ $platz ]        = array_key_exists( $vorlage, tamil_site_eigenanzeigen() ) ? $vorlage : '';
	}
	return $out;
}

/**
 * CSV speichern und daraus die Tabelle für template_redirect ableiten.
 */
function tamil_site_sanitize_redirects_csv( $input ): string {
	$prep = tamil_site_prepare_redirects( (string) $input );
	if ( is_wp_error( $prep ) ) {
		add_settings_error( 'tamil_site_redirects_csv', 'zu_gross', $prep->get_error_message() );
		return (string) get_option( 'tamil_site_redirects_csv', '' );
	}
	foreach ( $prep['verworfen'] as $v ) {
		add_settings_error( 'tamil_site_redirects_csv', 'verworfen', esc_html( $v['alt'] . ': ' . $v['grund'] ), 'warning' );
	}
	update_option( 'tamil_site_redirects', $prep['table'], false );
	return $prep['csv'];
}

function tamil_site_page_settings(): void {
	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}
	$settings = tamil_site_settings();
	$csv      = (string) get_option( 'tamil_site_redirects_csv', '' );
	$table    = tamil_site_redirects();
	?>
	<div class="wrap">
		<h1><?php esc_html_e( 'Tamil.de Website', 'tamil-site' ); ?></h1>
		<form method="post" action="options.php">
			<?php settings_fields( 'tamil_site' ); ?>
			<h2><?php esc_html_e( 'Funktionen', 'tamil-site' ); ?></h2>
			<p class="description"><?php esc_html_e( 'Jeder Baustein lässt sich einzeln einschalten. Im Echtbetrieb bleibt er aus, bis Auftragsverarbeitung und Rechtstexte vorliegen.', 'tamil-site' ); ?></p>
			<fieldset>
				<?php foreach ( tamil_site_funktionen_stand() as $name => $an ) : ?>
				<p><label><input type="checkbox" name="tamil_site_funktionen[<?php echo esc_attr( $name ); ?>]" value="1" <?php checked( $an ); ?>> <?php echo esc_html( tamil_site_funktionen()[ $name ] ); ?></label></p>
				<?php endforeach; ?>
			</fieldset>
			<h2><?php esc_html_e( 'Suchmaschinen und soziale Netze', 'tamil-site' ); ?></h2>
			<table class="form-table" role="presentation">
				<tr>
					<th scope="row"><label for="tamil-site-seo-bild"><?php esc_html_e( 'Standard-Vorschaubild', 'tamil-site' ); ?></label></th>
					<td><input type="url" class="regular-text" id="tamil-site-seo-bild" name="tamil_site_seo[bild]" value="<?php echo esc_attr( tamil_site_seo_einstellungen()['bild'] ); ?>">
					<p class="description"><?php esc_html_e( 'Adresse eines Bildes (am besten 1200 × 630) für Seiten ohne Beitragsbild. Leer: Website-Icon.', 'tamil-site' ); ?></p></td>
				</tr>
			</table>
			<h2><?php esc_html_e( 'Cookie-Zustimmung', 'tamil-site' ); ?></h2>
			<p class="description"><?php esc_html_e( 'Texte für Hinweis und Einstellungen. Leer lassen = Standardtext (vorläufige Fassung). Eine neue Fassung fragt alle Besucher erneut.', 'tamil-site' ); ?></p>
			<table class="form-table" role="presentation">
				<?php
				$tz_texte    = tamil_site_zustimmung_texte();
				$tz_gepflegt = (array) get_option( 'tamil_site_zustimmung', array() );
				$tz_felder   = array(
					'titel'          => __( 'Überschrift', 'tamil-site' ),
					'text'           => __( 'Hinweistext', 'tamil-site' ),
					'notwendig'      => __( 'Kategorie „Notwendig“', 'tamil-site' ),
					'externe_medien' => __( 'Kategorie „Externe Medien“', 'tamil-site' ),
					'statistik'      => __( 'Kategorie „Statistik“', 'tamil-site' ),
					'fassung'        => __( 'Fassung', 'tamil-site' ),
				);
				foreach ( $tz_felder as $tz_key => $tz_label ) :
					$tz_id = 'tamil-site-tz-' . $tz_key;
					?>
				<tr>
					<th scope="row"><label for="<?php echo esc_attr( $tz_id ); ?>"><?php echo esc_html( $tz_label ); ?></label></th>
					<td>
					<?php if ( in_array( $tz_key, array( 'titel', 'fassung' ), true ) ) : ?>
						<input type="text" class="regular-text" id="<?php echo esc_attr( $tz_id ); ?>" name="tamil_site_zustimmung[<?php echo esc_attr( $tz_key ); ?>]" value="<?php echo esc_attr( (string) ( $tz_gepflegt[ $tz_key ] ?? '' ) ); ?>" placeholder="<?php echo esc_attr( $tz_texte[ $tz_key ] ); ?>">
					<?php else : ?>
						<textarea class="large-text" rows="3" id="<?php echo esc_attr( $tz_id ); ?>" name="tamil_site_zustimmung[<?php echo esc_attr( $tz_key ); ?>]" placeholder="<?php echo esc_attr( $tz_texte[ $tz_key ] ); ?>"><?php echo esc_textarea( (string) ( $tz_gepflegt[ $tz_key ] ?? '' ) ); ?></textarea>
					<?php endif; ?>
					</td>
				</tr>
				<?php endforeach; ?>
			</table>
			<h2><?php esc_html_e( 'Werbeplätze', 'tamil-site' ); ?></h2>
			<p class="description"><?php esc_html_e( 'Je Platz gilt: Advanced-Ads-Platzierung vor Banner-HTML vor Eigenanzeige. Ist nichts gesetzt, bleibt der Platz unsichtbar.', 'tamil-site' ); ?></p>
			<table class="form-table" role="presentation">
				<?php foreach ( tamil_site_werbeplaetze() as $platz => $label ) : ?>
				<tr>
					<th scope="row"><?php echo esc_html( $label ); ?></th>
					<td>
						<p><input type="text" class="regular-text" name="tamil_site_settings[advanced_ads][<?php echo esc_attr( $platz ); ?>]" value="<?php echo esc_attr( $settings['advanced_ads'][ $platz ] ?? '' ); ?>" placeholder="<?php esc_attr_e( 'Advanced-Ads-Platzierung (Slug)', 'tamil-site' ); ?>"></p>
						<p><textarea class="large-text code" rows="2" name="tamil_site_settings[anzeigen][<?php echo esc_attr( $platz ); ?>]" placeholder="<?php esc_attr_e( 'Banner-HTML (optional)', 'tamil-site' ); ?>"><?php echo esc_textarea( $settings['anzeigen'][ $platz ] ?? '' ); ?></textarea></p>
						<p><label><?php esc_html_e( 'Eigenanzeige, wenn nichts gebucht ist:', 'tamil-site' ); ?>
						<select name="tamil_site_settings[eigen][<?php echo esc_attr( $platz ); ?>]">
							<?php foreach ( tamil_site_eigenanzeigen() as $key => $name ) : ?>
							<option value="<?php echo esc_attr( $key ); ?>" <?php selected( $settings['eigen'][ $platz ] ?? '', $key ); ?>><?php echo esc_html( $name ); ?></option>
							<?php endforeach; ?>
						</select></label></p>
					</td>
				</tr>
				<?php endforeach; ?>
				<tr>
					<th scope="row"><label for="tamil-site-wa"><?php esc_html_e( 'WhatsApp-Kanal', 'tamil-site' ); ?></label></th>
					<td><input type="url" class="regular-text" id="tamil-site-wa" name="tamil_site_settings[whatsapp_url]" value="<?php echo esc_attr( $settings['whatsapp_url'] ); ?>"></td>
				</tr>
			</table>
			<h2><?php esc_html_e( 'Weiterleitungen (301)', 'tamil-site' ); ?></h2>
			<p class="description"><?php esc_html_e( 'CSV mit den Spalten „alt“ und „neu“ (z. B. redirects.csv aus dem Export der alten Seite). Pfade oder volle URLs.', 'tamil-site' ); ?></p>
			<textarea class="large-text code" rows="10" name="tamil_site_redirects_csv"><?php echo esc_textarea( $csv ); ?></textarea>
			<p class="description">
				<?php
				/* translators: %d: Anzahl Weiterleitungen */
				echo esc_html( sprintf( _n( '%d Weiterleitung aktiv.', '%d Weiterleitungen aktiv.', count( $table ), 'tamil-site' ), count( $table ) ) );
				?>
			</p>
			<?php submit_button(); ?>
		</form>
	</div>
	<?php
}
