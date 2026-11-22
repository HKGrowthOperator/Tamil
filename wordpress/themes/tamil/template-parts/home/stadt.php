<?php
/**
 * „Tamil in meiner Stadt“ (Startseiten-Proben, inc/proben.php): Stadt wählen, darunter Kino, Termine und Geschichten
 * von dort. Auf Weiß mit der Linie in Titan; alle Beiträge als Bildkarten mit Titel im Bild und Punktbogen.
 *
 * Alle Karten aller Städte stehen im HTML und tragen data-stadt (Schlüssel ihrer Städte). Ohne Skript ist der
 * vollständige Zustand „Alle Städte“ zu sehen (nächste Vorstellungen, nächste Termine, die drei neuesten Geschichten
 * mit Ort), das Auswahlfeld bleibt verborgen, und am Ende stehen die Links „Kino nach Stadt“ und „Alle Termine“. Mit
 * Skript filtert assets/js/stadt-start.js (direkt hinter dem Abschnitt eingebettet, vor dem ersten Malen) nach der in
 * diesem Browser gespeicherten Stadt; assets/js/stadt.js bedient das Auswahlfeld. Gespeichert wird nur im
 * localStorage (Schlüssel tamil_stadt); kein Cookie, keine Anfrage an den Server, keine Standortabfrage.
 *
 * Ein Fach ohne Inhalt belegt keine Kartenfläche; an seiner Stelle steht ein Satz (.stadt__leer), nie eine leere
 * Bildkachel. Gibt es gar nichts (kein Film, kein Termin, keine Geschichte mit Ort), entfällt der Abschnitt.
 *
 * @var array $args { @type bool $oben Abschnitt steht ganz oben (Community First): erste Bilder sofort laden. }
 */

defined( 'ABSPATH' ) || exit;

$tamil_d    = tamil_stadt_daten();
$tamil_oben = ! empty( $args['oben'] );
if ( ! $tamil_d['filme'] && ! $tamil_d['termine'] && ! $tamil_d['geschichten'] ) {
	return;
}

// Attribute in das äußere Element einer fertigen Karte setzen (data-stadt, hidden) und HTML vor ihrem Ende anhängen
$tamil_karte = static function ( string $html, array $staedte, bool $sichtbar, string $anhang = '' ): string {
	$attr = ' data-stadt-karte data-stadt="' . esc_attr( implode( ' ', $staedte ) ) . '"' . ( $sichtbar ? '' : ' hidden' );
	$html = (string) preg_replace( '/^<(li|article)\b/', '<$1' . $attr, $html, 1 );
	if ( '' !== $anhang ) {
		$ende = strrpos( $html, '</' );
		$html = false === $ende ? $html : substr( $html, 0, $ende ) . $anhang . substr( $html, $ende );
	}
	return $html;
};

// Leerzustand eines Fachs als Satz mit Link: Wortlaut für „Alle Städte“ und für eine gewählte Stadt ({stadt})
$tamil_leer = static function ( string $fach, array $alle, array $stadt, string $url, bool $zeigen ): void {
	printf(
		// phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- alle Werte unten escapt
		'<p class="stadt__leer" data-leer="%1$s"%2$s><span data-leer-satz data-text-alle="%3$s" data-text-stadt="%5$s">%3$s</span> <a href="%7$s" data-leer-link data-text-alle="%4$s" data-text-stadt="%6$s">%4$s</a></p>',
		esc_attr( $fach ),
		$zeigen ? '' : ' hidden',
		esc_attr( $alle[0] ?? '' ),
		esc_attr( $alle[1] ?? '' ),
		esc_attr( $stadt[0] ),
		esc_attr( $stadt[1] ),
		esc_url( $url )
	);
};

$tamil_kino    = tamil_rubrik( 'kino' );
$tamil_n_kino  = min( 2, count( $tamil_d['filme'] ) );
$tamil_n_term  = min( 2, count( $tamil_d['termine'] ) );
$tamil_n_gesch = min( 3, count( $tamil_d['geschichten'] ) );
?>
<section class="stadt innen<?php echo $tamil_oben ? ' stadt--oben' : ''; ?>" id="meine-stadt" aria-labelledby="t-stadt" data-stadt-bereich>
	<div class="stadt__kopf">
		<h2 class="stadt__titel" id="t-stadt"><?php echo esc_html_x( 'Tamil in', 'Titel „Tamil in meiner Stadt“, erster Teil', 'tamil' ); ?> <span data-stadt-name data-ohne="<?php esc_attr_e( 'meiner Stadt', 'tamil' ); ?>"><?php esc_html_e( 'meiner Stadt', 'tamil' ); ?></span></h2>
		<?php if ( $tamil_d['staedte'] ) : ?>
			<div class="stadt__wahl" data-stadt-wahl hidden>
				<label for="stadt-wahl"><?php esc_html_e( 'Stadt', 'tamil' ); ?></label>
				<select id="stadt-wahl" aria-describedby="stadt-hinweis">
					<option value=""><?php esc_html_e( 'Alle Städte', 'tamil' ); ?></option>
					<?php foreach ( $tamil_d['staedte'] as $tamil_slug => $tamil_name ) : ?>
						<option value="<?php echo esc_attr( $tamil_slug ); ?>"><?php echo esc_html( $tamil_name ); ?></option>
					<?php endforeach; ?>
				</select>
				<p class="stadt__hinweis" id="stadt-hinweis"><?php esc_html_e( 'Die Auswahl bleibt nur in diesem Browser gespeichert.', 'tamil' ); ?></p>
			</div>
		<?php endif; ?>
	</div>
	<p class="nur-vorlesen" aria-live="polite" data-stadt-status></p>
	<?php /* translators: {stadt} bleibt stehen und wird im Browser durch den Namen der Stadt ersetzt */ ?>
	<p class="stadt__leer stadt__fort" data-stadt-fort data-text="<?php esc_attr_e( 'Für {stadt} haben wir gerade nichts Neues. Hier steht, was in allen Städten läuft.', 'tamil' ); ?>" hidden></p>

	<div class="stadt__inhalt" data-stadt-inhalt>
		<div class="stadt__reihe" data-karten="<?php echo (int) ( $tamil_n_kino + $tamil_n_term ); ?>">
			<div class="stadt__fach stadt__fach--kino" data-fach="kino" data-max="2" style="--n: <?php echo (int) max( 1, $tamil_n_kino ); ?>"<?php echo $tamil_d['filme'] ? '' : ' hidden'; ?>>
				<h3 class="stadt__art" id="t-stadt-kino"><?php esc_html_e( 'Im Kino', 'tamil' ); ?></h3>
				<ul class="stadt__karten" aria-labelledby="t-stadt-kino">
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
							tamil_grafik_kino( $tamil_f['film'], 'h4', $tamil_oben && 0 === $tamil_i ),
							array_keys( $tamil_f['orte'] ),
							$tamil_i < 2,
							'' !== $tamil_orte ? '<ul class="stadt__spielorte" hidden>' . $tamil_orte . '</ul>' : ''
						);
						// phpcs:enable WordPress.Security.EscapeOutput.OutputNotEscaped
					}
					?>
				</ul>
			</div>
			<div class="stadt__fach stadt__fach--termine" data-fach="termine" data-max="2" style="--n: <?php echo (int) max( 1, $tamil_n_term ); ?>"<?php echo $tamil_d['termine'] ? '' : ' hidden'; ?>>
				<h3 class="stadt__art" id="t-stadt-termine"><?php esc_html_e( 'Termine', 'tamil' ); ?></h3>
				<ul class="stadt__karten" aria-labelledby="t-stadt-termine">
					<?php
					foreach ( $tamil_d['termine'] as $tamil_i => $tamil_t ) {
						// phpcs:disable WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_grafik_termin()
						echo $tamil_karte(
							tamil_grafik_termin( $tamil_t['id'], 'h4', false, $tamil_oben && 0 === $tamil_i ),
							array_filter( array( $tamil_t['stadt'] ) ),
							$tamil_i < 2
						);
						// phpcs:enable WordPress.Security.EscapeOutput.OutputNotEscaped
					}
					?>
				</ul>
			</div>
			<div class="stadt__leerzeilen">
				<?php
				$tamil_leer(
					'kino',
					array(
						__( 'Für diese Woche kennen wir keine tamilische Vorstellung.', 'tamil' ),
						__( 'Kinostarts, Kritiken und frühere Spielorte stehen in der Rubrik Kino.', 'tamil' ),
					),
					array(
						__( 'In {stadt} läuft gerade kein tamilischer Film, von dem wir wissen.', 'tamil' ),
						__( 'Alle Spielorte stehen unter Kino nach Stadt.', 'tamil' ),
					),
					$tamil_kino['url'],
					! $tamil_d['filme']
				);
				$tamil_leer(
					'termine',
					array(
						__( 'Gerade steht kein kommender Termin im Kalender.', 'tamil' ),
						__( 'Kennt ihr einen? Schickt ihn der Redaktion, kostenlos für Vereine, Tempel und Schulen.', 'tamil' ),
					),
					array(
						__( 'Für {stadt} steht kein Termin im Kalender.', 'tamil' ),
						__( 'Kennt ihr einen? Schickt ihn der Redaktion, kostenlos für Vereine, Tempel und Schulen.', 'tamil' ),
					),
					tamil_einreichen_url(),
					! $tamil_d['termine']
				);
				$tamil_leer(
					'geschichten',
					array(),
					array(
						__( 'Aus {stadt} haben wir noch keine Geschichte.', 'tamil' ),
						__( 'Die neuesten stehen in der Rubrik Community.', 'tamil' ),
					),
					tamil_rubrik( 'community' )['url'],
					false
				);
				?>
			</div>
		</div>

		<div class="stadt__fach stadt__fach--geschichten" data-fach="geschichten" data-max="3"<?php echo $tamil_d['geschichten'] ? '' : ' hidden'; ?>>
			<h3 class="stadt__art" id="t-stadt-geschichten"><?php esc_html_e( 'Aus der Stadt', 'tamil' ); ?></h3>
			<div class="kueche__raster rubrikblock__buehne kueche__raster--<?php echo (int) max( 1, $tamil_n_gesch ); ?>" data-buehne>
				<?php
				foreach ( $tamil_d['geschichten'] as $tamil_i => $tamil_g ) {
					// phpcs:disable WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild()
					echo $tamil_karte(
						tamil_anr_imbild(
							$tamil_g['id'],
							array(
								'klasse' => 0 === $tamil_i ? 'kachel kachel--gross' : 'kachel kachel--klein',
								'rahmen' => 0 === $tamil_i ? 'r169' : 'r83',
								'ebene'  => 'h4',
								'sizes'  => 0 === $tamil_i ? '(min-width: 1024px) 800px, (min-width: 600px) calc(66vw - 32px), calc(100vw - 32px)' : '(min-width: 1024px) 380px, (min-width: 600px) 33vw, calc(100vw - 32px)',
								'zusatz' => tamil_kontext(
									$tamil_g['id'],
									array(
										'form'   => 'zeile',
										'satz'   => 'einer',
										'quelle' => false,
									)
								),
							)
						),
						$tamil_g['staedte'],
						$tamil_i < 3
					);
					// phpcs:enable WordPress.Security.EscapeOutput.OutputNotEscaped
				}
				?>
			</div>
		</div>
	</div>

	<p class="stadt__weiter">
		<a class="textlink" href="<?php echo esc_url( $tamil_kino['url'] ); ?>"><?php esc_html_e( 'Kino nach Stadt', 'tamil' ); ?></a>
		<a class="textlink" href="<?php echo esc_url( tamil_rubrik( 'events' )['url'] ); ?>"><?php esc_html_e( 'Alle Termine', 'tamil' ); ?></a>
	</p>
</section>
<?php
// Gespeicherte Stadt vor dem ersten Malen anwenden (kein Springen beim Laden); die Datei ist klein und eigen
$tamil_start = TAMIL_THEME_DIR . '/assets/js/stadt-start.js';
if ( $tamil_d['staedte'] && is_readable( $tamil_start ) ) {
	echo '<script>' . file_get_contents( $tamil_start ) . "</script>\n"; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped, WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents -- eigene Datei
}
