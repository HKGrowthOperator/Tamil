<?php
/**
 * Startseiten-Probe „News First“ (/?probe=news, inc/proben.php): oben eine Zeitfolge der fünf neuesten Beiträge des
 * Vorrats (links die Zeit, in der Mitte die Bildkarte, rechts Ort, ein Satz und die Quelle), daneben das Cover
 * kleiner und die zwei ältesten Beiträge. Jeder Beitrag ist eine Bildkarte mit Titel im Bild und Punktbogen.
 *
 * Keine erfundene Aktualität: „Heute wichtig“ steht nur, wenn mindestens ein Beitrag der Zeitfolge von heute ist,
 * sonst „Zuletzt erschienen“. Uhrzeit nur bei Beiträgen von heute oder gestern (tamil_zeit_text()).
 *
 * Die Zeitfolge lässt die Titelgeschichte aus (sie steht als Cover daneben, am Handy darunter). Wäre sie nach ihrem
 * Datum Teil der Liste (neuer als der letzte Eintrag, meist der neueste Beitrag überhaupt), sagt eine Zeile unter der
 * Überschrift das und führt zu ihr (3.16.1): „Zuletzt erschienen“ lässt nie stillschweigend den neuesten Beitrag aus.
 *
 * @var array $args { @type array $kacheln Rubrikkacheln aus tamil_start_auswahl(). }
 */

defined( 'ABSPATH' ) || exit;

$tamil_vorrat = tamil_probe_vorrat();
$tamil_folge  = array_slice( $tamil_vorrat['p'], 0, 5 );
$tamil_alt    = array_slice( $tamil_vorrat['p'], 5, 2 );
$tamil_heute  = current_time( 'Y-m-d' );
// Gehört die Titelgeschichte nach ihrem Datum in die Liste? Dann fehlt sie dort sichtbar und wird genannt.
$tamil_lead_ts = (int) get_post_timestamp( $tamil_vorrat['lead'] );
$tamil_fehlt   = $tamil_folge && $tamil_vorrat['lead'] && $tamil_lead_ts > (int) get_post_timestamp( (int) end( $tamil_folge ) );
$tamil_neu     = (bool) array_filter( $tamil_folge, static fn( int $id ): bool => wp_date( 'Y-m-d', (int) get_post_timestamp( $id ) ) === $tamil_heute );
?>
<div class="innen oben oben--probe nachrichten">
	<?php if ( $tamil_folge ) : ?>
		<section class="nachrichten__folge" aria-labelledby="t-zeitfolge">
			<h2 class="block-titel" id="t-zeitfolge"><?php echo esc_html( $tamil_neu ? __( 'Heute wichtig', 'tamil' ) : __( 'Zuletzt erschienen', 'tamil' ) ); ?></h2>
			<?php if ( $tamil_fehlt ) : ?>
				<p class="zeitfolge__hinweis">
					<?php
					/* translators: %s: Datum der Titelgeschichte */
					echo esc_html( sprintf( __( 'Nicht in dieser Liste: die Titelgeschichte (%s).', 'tamil' ), tamil_zeit_text( $tamil_lead_ts ) ) );
					?>
					<a class="textlink" href="#titelgeschichte"><?php esc_html_e( 'Zur Titelgeschichte', 'tamil' ); ?></a>
				</p>
			<?php endif; ?>
			<ol class="zeitfolge">
				<?php
				foreach ( $tamil_folge as $tamil_i => $tamil_id ) :
					$tamil_ts  = (int) get_post_timestamp( $tamil_id );
					$tamil_kat = tamil_hauptkategorie( $tamil_id );
					?>
					<li class="zeitfolge__eintrag<?php echo 0 === $tamil_i ? ' zeitfolge__eintrag--erste' : ''; ?>">
						<p class="zeitfolge__zeit">
							<time datetime="<?php echo esc_attr( wp_date( 'c', $tamil_ts ) ); ?>"><?php echo esc_html( tamil_zeit_text( $tamil_ts ) ); ?></time>
							<?php if ( $tamil_kat ) : ?>
								<span class="zeitfolge__rubrik"><?php echo esc_html( $tamil_kat->name ); ?></span>
							<?php endif; ?>
						</p>
						<?php
						echo tamil_anr_imbild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild()
							$tamil_id,
							array(
								'klasse' => 'zeitkarte',
								'rahmen' => 0 === $tamil_i ? 'r169' : 'r83',
								'dach'   => '', // Zeit und Rubrik stehen neben dem Bild; im Bild nur der Titel
								'eager'  => 0 === $tamil_i,
								'sizes'  => 0 === $tamil_i ? '(min-width: 1024px) 380px, (min-width: 600px) 300px, calc(100vw - 32px)' : '(min-width: 1024px) 280px, (min-width: 600px) 300px, calc(100vw - 32px)',
								'zusatz' => tamil_kontext(
									$tamil_id,
									array(
										'form' => 'zeile',
										'satz' => 'einer',
									)
								),
							)
						);
						?>
					</li>
				<?php endforeach; ?>
			</ol>
		</section>
	<?php endif; ?>

	<div class="nachrichten__seite" id="titelgeschichte">
		<?php
		echo tamil_anr_imbild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild()
			$tamil_vorrat['lead'],
			array(
				'klasse'       => 'aufmacher aufmacher--klein',
				'rahmen'       => 'r169',
				'ebene'        => 'h2',
				'titel_stufen' => true,
				'sizes'        => '(min-width: 1024px) 520px, (min-width: 600px) calc(100vw - 48px), 100vw',
				'zusatz'       => tamil_kontext(
					$tamil_vorrat['lead'],
					array(
						'form' => 'cover',
						'satz' => 'vorspann',
					)
				),
			)
		);
		foreach ( $tamil_alt as $tamil_i => $tamil_id ) {
			echo tamil_anr_imbild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild()
				$tamil_id,
				array(
					'klasse'  => 0 === $tamil_i ? 'beistueck beistueck--mittel' : 'beistueck beistueck--flach',
					'rahmen'  => 0 === $tamil_i ? 'r169' : 'r83',
					'niedrig' => true,
					'sizes'   => '(min-width: 1024px) 520px, (min-width: 600px) 50vw, calc(100vw - 32px)',
				)
			);
		}
		?>
	</div>

	<?php echo tamil_kacheln( (array) ( $args['kacheln'] ?? array() ), __( 'Rubriken mit Bild', 'tamil' ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_kacheln() ?>
</div>
