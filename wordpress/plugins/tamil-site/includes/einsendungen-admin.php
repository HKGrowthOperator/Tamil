<?php
/**
 * Einsendungen (F1) in wp-admin: Werkzeuge → Einsendungen. Nur lesend und nur für den Notfall (der Eingang läuft im
 * Cockpit des Radars). Dazu der Einwilligungstext mit Fassung (Text von KBS; bis dahin die vorläufige Fassung).
 * Nur für Benutzer mit manage_options.
 */

defined( 'ABSPATH' ) || exit;

function tamil_site_einsendungen_admin_menu(): void {
	add_management_page( __( 'Einsendungen', 'tamil-site' ), __( 'Einsendungen', 'tamil-site' ), 'manage_options', 'tamil-einsendungen', 'tamil_site_einsendungen_seite' );
}
add_action( 'admin_menu', 'tamil_site_einsendungen_admin_menu' );

/**
 * Seite: Liste (neueste zuerst, 50 je Seite) oder eine Einsendung im Einzelnen.
 */
function tamil_site_einsendungen_seite(): void {
	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}
	// phpcs:disable WordPress.Security.NonceVerification.Recommended -- nur lesende Ansicht
	$vorgang = isset( $_GET['vorgang'] ) ? sanitize_text_field( wp_unslash( $_GET['vorgang'] ) ) : '';
	$seite   = isset( $_GET['seite'] ) ? max( 1, absint( $_GET['seite'] ) ) : 1;
	// phpcs:enable WordPress.Security.NonceVerification.Recommended
	$basis = admin_url( 'tools.php?page=tamil-einsendungen' );
	?>
	<div class="wrap">
		<h1><?php esc_html_e( 'Einsendungen', 'tamil-site' ); ?></h1>
		<p class="description"><?php esc_html_e( 'Nur lesend, für den Notfall. Bearbeitet werden Einsendungen im Cockpit des Radars. Geantwortet wird von Hand aus dem eigenen Mailprogramm.', 'tamil-site' ); ?>
		<?php
		/* translators: 1: Tage nach Abschluss, 2: Tage für Spam */
		echo esc_html( sprintf( __( 'Löschung %1$d Tage nach Abschluss, Spam nach %2$d Tagen.', 'tamil-site' ), TAMIL_SITE_EINSENDUNG_FRIST_TAGE, TAMIL_SITE_EINSENDUNG_SPAM_TAGE ) );
		?>
		</p>
		<?php if ( ! tamil_site_funktion_an( 'einreichungen' ) ) : ?>
		<div class="notice notice-info inline"><p><?php esc_html_e( 'Die Funktion „Einreichungen“ ist ausgeschaltet; die Formulare nehmen nichts an.', 'tamil-site' ); ?></p></div>
		<?php endif; ?>
		<?php
		if ( tamil_site_datenversion() < 2 ) {
			echo '<p>' . esc_html__( 'Die Tabelle ist noch nicht angelegt.', 'tamil-site' ) . '</p></div>';
			return;
		}
		if ( '' !== $vorgang ) {
			tamil_site_einsendungen_einzeln( $vorgang, $basis );
		} else {
			tamil_site_einsendungen_tabelle( $seite, $basis );
		}
		$einwilligung = tamil_site_einsendung_einwilligung();
		$gepflegt     = (array) get_option( 'tamil_site_einsendungen', array() );
		?>
		<h2><?php esc_html_e( 'Einwilligung in den Formularen', 'tamil-site' ); ?></h2>
		<p class="description"><?php esc_html_e( 'Text und Fassung liefert KBS. Leer lassen = vorläufige Fassung. Gespeichert wird bei jeder Einsendung die Fassung, der zugestimmt wurde. Ein geänderter Text braucht eine neue Fassung; jede Fassung wird mit ihrem Text unten archiviert.', 'tamil-site' ); ?></p>
		<?php settings_errors( 'tamil_site_einsendungen' ); ?>
		<form method="post" action="options.php">
			<?php settings_fields( 'tamil_site_einsendungen' ); ?>
			<table class="form-table" role="presentation">
				<tr>
					<th scope="row"><label for="tamil-einsendungen-text"><?php esc_html_e( 'Einwilligungstext', 'tamil-site' ); ?></label></th>
					<td><textarea class="large-text" rows="4" id="tamil-einsendungen-text" name="tamil_site_einsendungen[text]" placeholder="<?php echo esc_attr( $einwilligung['text'] ); ?>"><?php echo esc_textarea( (string) ( $gepflegt['text'] ?? '' ) ); ?></textarea></td>
				</tr>
				<tr>
					<th scope="row"><label for="tamil-einsendungen-fassung"><?php esc_html_e( 'Fassung', 'tamil-site' ); ?></label></th>
					<td><input type="text" class="regular-text" id="tamil-einsendungen-fassung" name="tamil_site_einsendungen[fassung]" value="<?php echo esc_attr( (string) ( $gepflegt['fassung'] ?? '' ) ); ?>" placeholder="<?php echo esc_attr( $einwilligung['fassung'] ); ?>"></td>
				</tr>
			</table>
			<?php submit_button(); ?>
		</form>
		<h3><?php esc_html_e( 'Archiv der Fassungen', 'tamil-site' ); ?></h3>
		<table class="widefat striped">
			<thead><tr>
				<th scope="col"><?php esc_html_e( 'Fassung', 'tamil-site' ); ?></th>
				<th scope="col"><?php esc_html_e( 'Abgelegt', 'tamil-site' ); ?></th>
				<th scope="col"><?php esc_html_e( 'Text', 'tamil-site' ); ?></th>
			</tr></thead>
			<tbody>
			<?php foreach ( tamil_site_einsendung_fassungen() as $tamil_fassung => $tamil_eintrag ) : ?>
				<tr>
					<td><?php echo esc_html( (string) $tamil_fassung ); ?></td>
					<td><?php echo esc_html( '' !== $tamil_eintrag['seit'] ? wp_date( 'j.n.Y H:i', (int) strtotime( $tamil_eintrag['seit'] ) ) : '–' ); ?></td>
					<td><?php echo esc_html( $tamil_eintrag['text'] ); ?></td>
				</tr>
			<?php endforeach; ?>
			</tbody>
		</table>
	</div>
	<?php
}

/**
 * Liste.
 */
function tamil_site_einsendungen_tabelle( int $seite, string $basis ): void {
	global $wpdb;
	$t        = tamil_site_einsendung_tabelle();
	$proseite = 50;
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- eigene Tabelle
	$gesamt = (int) $wpdb->get_var( "SELECT COUNT(*) FROM {$t}" );
	// phpcs:ignore WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching, WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- eigene Tabelle
	$zeilen = (array) $wpdb->get_results( $wpdb->prepare( "SELECT * FROM {$t} ORDER BY id DESC LIMIT %d OFFSET %d", $proseite, ( $seite - 1 ) * $proseite ), ARRAY_A );
	$arten  = tamil_site_einsendung_arten();
	$status = tamil_site_einsendung_status_liste();
	?>
	<table class="widefat striped">
		<thead><tr>
			<th scope="col"><?php esc_html_e( 'Vorgang', 'tamil-site' ); ?></th>
			<th scope="col"><?php esc_html_e( 'Art', 'tamil-site' ); ?></th>
			<th scope="col"><?php esc_html_e( 'Status', 'tamil-site' ); ?></th>
			<th scope="col"><?php esc_html_e( 'Eingang', 'tamil-site' ); ?></th>
			<th scope="col"><?php esc_html_e( 'Abschluss', 'tamil-site' ); ?></th>
			<th scope="col"><?php esc_html_e( 'Bild', 'tamil-site' ); ?></th>
		</tr></thead>
		<tbody>
		<?php if ( ! $zeilen ) : ?>
			<tr><td colspan="6"><?php esc_html_e( 'Keine Einsendungen.', 'tamil-site' ); ?></td></tr>
		<?php endif; ?>
		<?php foreach ( $zeilen as $z ) : ?>
			<tr>
				<td><a href="<?php echo esc_url( add_query_arg( 'vorgang', $z['vorgangsnummer'], $basis ) ); ?>"><?php echo esc_html( $z['vorgangsnummer'] ); ?></a></td>
				<td><?php echo esc_html( $arten[ $z['art'] ] ?? $z['art'] ); ?></td>
				<td><?php echo esc_html( $status[ $z['status'] ] ?? $z['status'] ); ?></td>
				<td><?php echo esc_html( tamil_site_einsendung_ortszeit( $z['eingang_at'] ) ); ?></td>
				<td><?php echo esc_html( tamil_site_einsendung_ortszeit( $z['abgeschlossen_at'] ) ); ?></td>
				<td><?php echo '' !== (string) $z['bild_datei'] ? esc_html__( 'ja', 'tamil-site' ) : '–'; ?></td>
			</tr>
		<?php endforeach; ?>
		</tbody>
	</table>
	<?php
	$seiten = (int) ceil( $gesamt / $proseite );
	if ( $seiten > 1 ) {
		echo '<p>';
		for ( $i = 1; $i <= $seiten; $i++ ) {
			echo $i === $seite ? '<strong>' . esc_html( (string) $i ) . '</strong> ' : '<a href="' . esc_url( add_query_arg( 'seite', $i, $basis ) ) . '">' . esc_html( (string) $i ) . '</a> ';
		}
		echo '</p>';
	}
}

/**
 * Eine Einsendung im Einzelnen (ohne Bild, ohne IP-Hash).
 */
function tamil_site_einsendungen_einzeln( string $vorgang, string $basis ): void {
	$zeile = tamil_site_einsendung_zeile( $vorgang );
	echo '<p><a href="' . esc_url( $basis ) . '">' . esc_html__( '← Zur Liste', 'tamil-site' ) . '</a></p>';
	if ( ! $zeile ) {
		echo '<p>' . esc_html__( 'Einsendung nicht gefunden (vielleicht schon gelöscht).', 'tamil-site' ) . '</p>';
		return;
	}
	$e      = tamil_site_einsendung_ausgabe( $zeile );
	$felder = tamil_site_einsendung_felder( $e['art'] );
	$zeilen = array(
		__( 'Vorgang', 'tamil-site' )      => $e['vorgangsnummer'],
		__( 'Art', 'tamil-site' )          => tamil_site_einsendung_arten()[ $e['art'] ] ?? $e['art'],
		__( 'Status', 'tamil-site' )       => tamil_site_einsendung_status_liste()[ $e['status'] ] ?? $e['status'],
		__( 'Eingang', 'tamil-site' )      => tamil_site_einsendung_ortszeit( $zeile['eingang_at'] ),
		__( 'Name', 'tamil-site' )         => $e['name'],
		__( 'E-Mail', 'tamil-site' )       => $e['email'],
		__( 'Telefon', 'tamil-site' )      => $e['telefon'],
		__( 'Einwilligung', 'tamil-site' ) => $e['einwilligung'] ? __( 'ja', 'tamil-site' ) . ', ' . $e['einwilligung_fassung'] : __( 'nein', 'tamil-site' ),
	);
	foreach ( $e['felder'] as $key => $wert ) {
		$zeilen[ $felder[ $key ]['label'] ?? (string) $key ] = (string) $wert;
	}
	if ( $e['bild'] ) {
		$zeilen[ __( 'Bild', 'tamil-site' ) ] = $e['bild']['typ'] . ', ' . size_format( $e['bild']['groesse'] ) . ( $e['bild']['recht_bestaetigt'] ? ', ' . __( 'Recht bestätigt', 'tamil-site' ) : '' );
	}
	?>
	<table class="widefat striped">
		<tbody>
		<?php foreach ( $zeilen as $label => $wert ) : ?>
			<tr><th scope="row"><?php echo esc_html( $label ); ?></th><td><?php echo nl2br( esc_html( $wert ) ); ?></td></tr>
		<?php endforeach; ?>
		</tbody>
	</table>
	<?php
}

/**
 * Datenbankzeit (UTC) in Ortszeit der Website, „–“ bei leer.
 *
 * @param string|null $wert Datenbankwert.
 */
function tamil_site_einsendung_ortszeit( ?string $wert ): string {
	if ( null === $wert || '' === $wert ) {
		return '–';
	}
	return wp_date( 'j.n.Y H:i', (int) strtotime( $wert . ' UTC' ) );
}
