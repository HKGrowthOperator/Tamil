<?php
/**
 * „Tamil in meiner Stadt“ als Streifen (Probe „Ausgabe“, Theme 3.17.0): direkt unter dem Cover, auf Titan, niedrig.
 * Stadtwahl und die nächsten kommenden Dinge in einer Reihe: zuerst Filme mit Vorstellung ab heute, dann Termine ab
 * heute. Nichts Vergangenes, keine Geschichten (die stehen im großen Abschnitt der anderen Proben, stadt.php).
 *
 * Daten und Verhalten wie stadt.php: tamil_stadt_daten(), dieselben data-Attribute, also filtern
 * assets/js/stadt-start.js (eingebettet, vor dem ersten Malen) und assets/js/stadt.js (Auswahlfeld) auch hier. Hat die
 * gewählte Stadt in einem Fach nichts, füllt das Skript es mit dem Bestand aus allen Städten und sagt es darüber;
 * gibt es nirgends etwas, steht ein leiser Satz mit Link. Ohne Skript steht „Alle Städte“ da, das Auswahlfeld bleibt
 * verborgen. Gespeichert wird nur im localStorage (Schlüssel tamil_stadt); keine Standortabfrage.
 *
 * Die Reihe ist seitlich wischbar, sobald sie breiter ist als ihr Platz; assets/js/streifen.js zeigt dann Balken und
 * Pfeile (Tastatur und Maus). Jede Karte ist ein Link, also auch ohne die Pfeile per Tab erreichbar.
 */

defined( 'ABSPATH' ) || exit;

$tamil_d = tamil_stadt_daten();

// wählbar sind hier nur Städte mit etwas Kommendem (Vorstellung ab heute oder Termin)
$tamil_mit = array();
foreach ( $tamil_d['filme'] as $tamil_f ) {
	$tamil_mit = array_merge( $tamil_mit, array_keys( $tamil_f['orte'] ) );
}
$tamil_mit     = array_merge( $tamil_mit, wp_list_pluck( $tamil_d['termine'], 'stadt' ) );
$tamil_staedte = array_intersect_key( $tamil_d['staedte'], array_flip( array_filter( array_map( 'strval', $tamil_mit ) ) ) );

// Attribute in das äußere Element einer fertigen Karte setzen (data-stadt, hidden) und HTML vor ihrem Ende anhängen
$tamil_karte = static function ( string $html, array $staedte, bool $sichtbar, string $anhang = '' ): string {
	$attr = ' data-stadt-karte data-stadt="' . esc_attr( implode( ' ', $staedte ) ) . '" data-alle' . ( $sichtbar ? '' : ' hidden' );
	$html = (string) preg_replace( '/^<li\b/', '<li' . $attr, $html, 1 );
	if ( '' !== $anhang ) {
		$ende = strrpos( $html, '</' );
		$html = false === $ende ? $html : substr( $html, 0, $ende ) . $anhang . substr( $html, $ende );
	}
	return $html;
};

// Leersatz eines Fachs (nur wenn es auch in allen Städten nichts gibt): kurzer Satz, der Link am Ende
$tamil_leer = static function ( string $fach, string $satz, string $link, string $satz_stadt, string $url, bool $zeigen ): void {
	printf(
		'<p class="stadt__leer" data-leer="%1$s"%2$s><span data-leer-satz data-text-alle="%3$s" data-text-stadt="%5$s">%3$s</span> <a href="%6$s" data-leer-link data-text-alle="%4$s" data-text-stadt="%4$s">%4$s</a></p>',
		esc_attr( $fach ),
		$zeigen ? '' : ' hidden',
		esc_attr( $satz ),
		esc_attr( $link ),
		esc_attr( $satz_stadt ),
		esc_url( $url )
	);
};

$tamil_kino   = tamil_rubrik( 'kino' );
$tamil_max    = array(
	'kino'    => 3,
	'termine' => 6,
);
$tamil_pfeil  = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2"/></svg>';
$tamil_sofort = 0; // die ersten zwei Karten stehen am Handy nah am ersten Bildschirm: ohne „lazy“
?>
<section class="streifen" id="meine-stadt" aria-labelledby="t-stadt" data-stadt-bereich data-streifen>
	<?php tamil_signatur( 'flaeche' ); // ab 1024 px unten rechts auf der Fläche, unter den Karten (wie in „Diese Woche“) ?>
	<div class="innen streifen__innen">
		<div class="streifen__kopf">
			<h2 class="streifen__titel" id="t-stadt"><?php echo esc_html_x( 'Tamil in', 'Titel „Tamil in meiner Stadt“, erster Teil', 'tamil' ); ?> <span data-stadt-name data-ohne="<?php esc_attr_e( 'meiner Stadt', 'tamil' ); ?>"><?php esc_html_e( 'meiner Stadt', 'tamil' ); ?></span></h2>
			<?php if ( $tamil_staedte ) : ?>
				<div class="streifen__wahl" data-stadt-wahl hidden>
					<label for="stadt-wahl"><?php esc_html_e( 'Stadt', 'tamil' ); ?></label>
					<select id="stadt-wahl" aria-describedby="stadt-hinweis">
						<option value=""><?php esc_html_e( 'Alle Städte', 'tamil' ); ?></option>
						<?php foreach ( $tamil_staedte as $tamil_slug => $tamil_name ) : ?>
							<option value="<?php echo esc_attr( $tamil_slug ); ?>"><?php echo esc_html( $tamil_name ); ?></option>
						<?php endforeach; ?>
					</select>
					<p class="streifen__hinweis" id="stadt-hinweis"><?php esc_html_e( 'Die Auswahl bleibt nur in diesem Browser gespeichert.', 'tamil' ); ?></p>
				</div>
			<?php endif; ?>
		</div>

		<div class="streifen__inhalt stadt__inhalt" data-stadt-inhalt>
			<p class="nur-vorlesen" aria-live="polite" data-stadt-status></p>
			<?php /* translators: {stadt} bleibt stehen und wird im Browser durch den Namen der Stadt ersetzt */ ?>
			<p class="streifen__fort" data-stadt-fort data-text="<?php esc_attr_e( 'Für {stadt} steht gerade nichts an. Hier steht, was in allen Städten kommt.', 'tamil' ); ?>" hidden></p>
			<?php // Handy: Die Ersatzzeile eines Fachs stünde in einer Spalte, die erst beim Wischen ganz ins Bild kommt. Dort sagt es diese Zeile über der Reihe (assets/js/streifen.js füllt sie), in voller Breite und mit Umbruch. ?>
			<p class="streifen__ersatz" data-ersatz-oben hidden></p>
			<div class="streifen__bahn" data-bahn data-karten="<?php echo (int) ( min( $tamil_max['kino'], count( $tamil_d['filme'] ) ) + min( $tamil_max['termine'], count( $tamil_d['termine'] ) ) ); ?>">
				<div class="streifen__fach" data-fach="kino" data-max="<?php echo (int) $tamil_max['kino']; ?>"<?php echo $tamil_d['filme'] ? '' : ' hidden'; ?>>
					<div class="streifen__art">
						<h3 id="t-stadt-kino"><?php esc_html_e( 'Im Kino, ab heute', 'tamil' ); ?></h3>
						<?php /* translators: {stadt} bleibt stehen und wird im Browser durch den Namen der Stadt ersetzt */ ?>
						<p data-ersatz data-text="<?php esc_attr_e( 'In {stadt} gerade kein Film. Anderswo:', 'tamil' ); ?>" data-text-oben="<?php esc_attr_e( 'In {stadt} gerade kein Film. In der Reihe stehen Filme aus anderen Städten.', 'tamil' ); ?>" hidden></p>
					</div>
					<ul class="streifen__karten" aria-labelledby="t-stadt-kino">
						<?php
						foreach ( $tamil_d['filme'] as $tamil_i => $tamil_f ) {
							// je Kino eine Zeile „Kino, Termin“ mit dem Link zu Tickets und Zeiten (außerhalb des Kartenlinks); zu sehen
							// ist nur die Zeile der gewählten Stadt
							$tamil_orte = '';
							foreach ( $tamil_f['orte'] as $tamil_slug => $tamil_kinos ) {
								foreach ( $tamil_kinos as $tamil_k ) {
									$tamil_orte .= '<li data-stadt="' . esc_attr( $tamil_slug ) . '" hidden><span>' . esc_html( trim( $tamil_k['kino'] . ( '' !== $tamil_k['termin'] ? ', ' . $tamil_k['termin'] : '' ), ', ' ) ) . '</span>';
									if ( '' !== $tamil_k['url'] ) {
										$tamil_orte .= ' <a class="textlink" href="' . esc_url( $tamil_k['url'] ) . '" target="_blank" rel="noopener nofollow">' . esc_html__( 'Tickets und Zeiten', 'tamil' ) . '</a>';
									}
									$tamil_orte .= '</li>';
								}
							}
							// phpcs:disable WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_grafik_kino() und oben
							echo $tamil_karte(
								tamil_grafik_kino( $tamil_f['film'], 'h4', $tamil_sofort++ < 2 ),
								array_keys( $tamil_f['orte'] ),
								$tamil_i < $tamil_max['kino'],
								'' !== $tamil_orte ? '<ul class="stadt__spielorte" hidden>' . $tamil_orte . '</ul>' : ''
							);
							// phpcs:enable WordPress.Security.EscapeOutput.OutputNotEscaped
						}
						?>
					</ul>
				</div>
				<div class="streifen__fach" data-fach="termine" data-max="<?php echo (int) $tamil_max['termine']; ?>"<?php echo $tamil_d['termine'] ? '' : ' hidden'; ?>>
					<div class="streifen__art">
						<h3 id="t-stadt-termine"><?php esc_html_e( 'Termine, ab heute', 'tamil' ); ?></h3>
						<?php /* translators: {stadt} bleibt stehen und wird im Browser durch den Namen der Stadt ersetzt */ ?>
						<p data-ersatz data-text="<?php esc_attr_e( 'Für {stadt} kein Termin. Anderswo:', 'tamil' ); ?>" data-text-oben="<?php esc_attr_e( 'Für {stadt} kein Termin. In der Reihe stehen Termine aus anderen Städten.', 'tamil' ); ?>" hidden></p>
					</div>
					<ul class="streifen__karten" aria-labelledby="t-stadt-termine">
						<?php
						foreach ( $tamil_d['termine'] as $tamil_i => $tamil_t ) {
							// phpcs:disable WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_grafik_termin()
							echo $tamil_karte(
								tamil_grafik_termin( $tamil_t['id'], 'h4', false, $tamil_sofort++ < 2 ),
								array_filter( array( $tamil_t['stadt'] ) ),
								$tamil_i < $tamil_max['termine']
							);
							// phpcs:enable WordPress.Security.EscapeOutput.OutputNotEscaped
						}
						?>
					</ul>
				</div>
			</div>
			<div class="streifen__leerzeilen">
				<?php
				/* translators: {stadt} bleibt stehen und wird im Browser durch den Namen der Stadt ersetzt */
				$tamil_leer( 'kino', __( 'Ab heute kennen wir keine tamilische Vorstellung.', 'tamil' ), __( 'Zur Rubrik Kino', 'tamil' ), __( 'In {stadt} läuft gerade kein tamilischer Film.', 'tamil' ), $tamil_kino['url'], ! $tamil_d['filme'] );
				/* translators: {stadt} bleibt stehen und wird im Browser durch den Namen der Stadt ersetzt */
				$tamil_leer( 'termine', __( 'Gerade steht kein Termin im Kalender.', 'tamil' ), __( 'Termin einreichen', 'tamil' ), __( 'Für {stadt} steht kein Termin im Kalender.', 'tamil' ), tamil_einreichen_url(), ! $tamil_d['termine'] );
				?>
			</div>
			<div class="streifen__lage" data-lage hidden>
				<button type="button" class="streifen__pfeil streifen__pfeil--zurueck" data-zurueck aria-label="<?php esc_attr_e( 'Zurück in der Reihe', 'tamil' ); ?>"><?php echo $tamil_pfeil; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- festes SVG ?></button>
				<span class="streifen__spur" aria-hidden="true"><span class="streifen__balken" data-balken></span></span>
				<button type="button" class="streifen__pfeil" data-weiter aria-label="<?php esc_attr_e( 'Weiter in der Reihe', 'tamil' ); ?>"><?php echo $tamil_pfeil; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- festes SVG ?></button>
			</div>
		</div>

		<p class="streifen__weiter">
			<a class="textlink" href="<?php echo esc_url( $tamil_kino['url'] ); ?>"><?php esc_html_e( 'Kino nach Stadt', 'tamil' ); ?></a>
			<a class="textlink" href="<?php echo esc_url( tamil_rubrik( 'events' )['url'] ); ?>"><?php esc_html_e( 'Alle Termine', 'tamil' ); ?></a>
		</p>
	</div>
</section>
<?php
// Gespeicherte Stadt vor dem ersten Malen anwenden (kein Springen beim Laden); dieselbe Datei wie in stadt.php
$tamil_start = TAMIL_THEME_DIR . '/assets/js/stadt-start.js';
if ( $tamil_staedte && is_readable( $tamil_start ) ) {
	echo '<script>' . file_get_contents( $tamil_start ) . "</script>\n"; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped, WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents -- eigene Datei
}
