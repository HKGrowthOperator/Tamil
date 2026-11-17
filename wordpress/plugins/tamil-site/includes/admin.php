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

/**
 * Auf der Einstellungsseite: Auswahl aus der Mediathek für die Bilder der Eigenanzeigen (ohne Skript bleibt das
 * Zahlenfeld für die Mediathek-ID).
 *
 * @param string $seite Hook der Admin-Seite.
 */
function tamil_site_admin_skripte( string $seite ): void {
	if ( 'settings_page_tamil-site' !== $seite ) {
		return;
	}
	wp_enqueue_media();
	$js = 'assets/admin-anzeigen.js';
	wp_enqueue_script( 'tamil-site-admin-anzeigen', TAMIL_SITE_URL . $js, array( 'media-editor' ), TAMIL_SITE_VERSION . '.' . filemtime( TAMIL_SITE_DIR . $js ), true );
	wp_localize_script(
		'tamil-site-admin-anzeigen',
		'tamilSiteBild',
		array(
			'titel' => __( 'Bild für die Eigenanzeige wählen', 'tamil-site' ),
			'knopf' => __( 'Dieses Bild verwenden', 'tamil-site' ),
		)
	);
}
add_action( 'admin_enqueue_scripts', 'tamil_site_admin_skripte' );

function tamil_site_sanitize_settings( $input ): array {
	$input = is_array( $input ) ? $input : array();
	$out   = array(
		'anzeigen'     => array(),
		'advanced_ads' => array(),
		'eigen'        => array(),
		'eigen_bild'   => array(),
		'whatsapp_url' => esc_url_raw( (string) ( $input['whatsapp_url'] ?? '' ) ),
	);
	foreach ( array_keys( tamil_site_eigenanzeige_standardbilder() ) as $bild ) {
		// Nur Bilder aus der Mediathek; leer oder 0 = mitgeliefertes Standardbild.
		$id = absint( $input['eigen_bild'][ $bild ] ?? 0 );
		if ( $id && ! wp_attachment_is_image( $id ) ) {
			/* translators: %d: Mediathek-ID */
			add_settings_error( 'tamil_site_settings', 'kein_bild', sprintf( __( 'Mediathek-ID %d ist kein Bild; das Standardbild bleibt.', 'tamil-site' ), $id ), 'warning' );
			$id = 0;
		}
		$out['eigen_bild'][ $bild ] = $id;
	}
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
 * CSV speichern und daraus die Tabelle für template_redirect ableiten. Fehlt das Feld in der Anfrage ganz (null),
 * bleiben CSV und Tabelle, wie sie sind (B5 Nebenbefund 1: sonst leert jedes Speichern die Weiterleitungen).
 */
function tamil_site_sanitize_redirects_csv( $input ): string {
	if ( null === $input ) {
		return (string) get_option( 'tamil_site_redirects_csv', '' );
	}
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
	if ( '' === trim( $csv ) && $table ) {
		$csv = tamil_site_redirects_als_csv( $table ); // nur die Tabelle gespeichert: so zeigen, dass Speichern sie behält
	}
	?>
	<div class="wrap">
		<h1><?php esc_html_e( 'Tamil.de Website', 'tamil-site' ); ?></h1>
		<form method="post" action="options.php">
			<?php settings_fields( 'tamil_site' ); ?>
			<h2><?php esc_html_e( 'Funktionen', 'tamil-site' ); ?></h2>
			<p class="description"><?php esc_html_e( 'Jeder Baustein lässt sich einzeln einschalten. Im Echtbetrieb bleibt er aus, bis Auftragsverarbeitung und Rechtstexte vorliegen.', 'tamil-site' ); ?></p>
			<fieldset>
				<?php
				foreach ( tamil_site_funktionen_stand() as $name => $an ) :
					$bereit = tamil_site_funktion_bereit( $name );
					?>
				<p><label><input type="checkbox" name="tamil_site_funktionen[<?php echo esc_attr( $name ); ?>]" value="1" <?php checked( $an && $bereit ); ?> <?php disabled( ! $bereit ); ?>> <?php echo esc_html( tamil_site_funktionen()[ $name ] ); ?></label>
					<?php if ( ! $bereit ) : ?>
					<span class="description">
						<?php
						/* translators: 1: nötige Datenversion, 2: Datenversion der Installation */
						echo esc_html( sprintf( __( 'Erst ab Datenversion %1$d einschaltbar, die Installation steht auf %2$d. Die Upgrade-Routine holt das nach.', 'tamil-site' ), (int) tamil_site_funktionen_datenversion()[ $name ], tamil_site_datenversion() ) );
						?>
					</span>
					<?php endif; ?>
				</p>
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
			</table>
			<h3><?php esc_html_e( 'Bilder der Eigenanzeigen', 'tamil-site' ); ?></h3>
			<p class="description"><?php esc_html_e( 'Jede Eigenanzeige ist ein Bildbanner. Ohne eigene Wahl gilt das mitgelieferte Standardbild; eine Anzeige ohne Bild wird nicht gezeigt. Alternativtext und Bildunterschrift (als Bildnachweis) kommen aus der Mediathek.', 'tamil-site' ); ?></p>
			<table class="form-table" role="presentation">
				<?php
				$tamil_bild_namen = array(
					'production' => __( 'Live mit dir! (Production)', 'tamil-site' ),
					'event'      => __( 'Event melden', 'tamil-site' ),
					'werben'     => __( 'Werben auf Tamil.de', 'tamil-site' ),
					'whatsapp'   => __( 'WhatsApp-Kanal (beide Größen)', 'tamil-site' ),
				);
				foreach ( tamil_site_eigenanzeige_standardbilder() as $tamil_bild => $tamil_std ) :
					$tamil_feld  = 'tamil-site-eigen-bild-' . $tamil_bild;
					$tamil_id    = (int) ( $settings['eigen_bild'][ $tamil_bild ] ?? 0 );
					$tamil_jetzt = tamil_site_eigenanzeige_bild( $tamil_bild );
					?>
				<tr>
					<th scope="row"><label for="<?php echo esc_attr( $tamil_feld ); ?>"><?php echo esc_html( $tamil_bild_namen[ $tamil_bild ] ?? $tamil_bild ); ?></label></th>
					<td>
						<?php if ( $tamil_jetzt ) : ?>
						<img src="<?php echo esc_url( $tamil_jetzt['src'] ); ?>" alt="" width="240" style="display:block;max-width:240px;height:auto;margin-bottom:8px">
						<?php endif; ?>
						<input type="number" min="0" step="1" class="small-text" id="<?php echo esc_attr( $tamil_feld ); ?>" name="tamil_site_settings[eigen_bild][<?php echo esc_attr( $tamil_bild ); ?>]" value="<?php echo esc_attr( $tamil_id ? (string) $tamil_id : '' ); ?>" placeholder="<?php esc_attr_e( 'Standard', 'tamil-site' ); ?>">
						<button type="button" class="button tamil-bild-waehlen" data-feld="<?php echo esc_attr( $tamil_feld ); ?>" hidden><?php esc_html_e( 'Aus der Mediathek wählen', 'tamil-site' ); ?></button>
						<button type="button" class="button-link tamil-bild-standard" data-feld="<?php echo esc_attr( $tamil_feld ); ?>" hidden><?php esc_html_e( 'Standardbild', 'tamil-site' ); ?></button>
						<p class="description">
							<?php
							if ( ! $tamil_jetzt ) {
								esc_html_e( 'Kein Bild vorhanden: Diese Eigenanzeige wird nicht gezeigt.', 'tamil-site' );
							} elseif ( $tamil_id ) {
								esc_html_e( 'Bild aus der Mediathek. Feld leeren für das Standardbild.', 'tamil-site' );
							} else {
								/* translators: %s: Bildnachweis */
								echo esc_html( sprintf( __( 'Standardbild (%s). Mediathek-ID eintragen, um es zu ersetzen.', 'tamil-site' ), '' !== $tamil_std['nachweis'] ? $tamil_std['nachweis'] : __( 'ohne Nachweis', 'tamil-site' ) ) );
							}
							?>
						</p>
					</td>
				</tr>
				<?php endforeach; ?>
			</table>
			<table class="form-table" role="presentation">
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
