<?php
/**
 * Rubrik Kino, Seite 1: Seitenkopf mit Foto, links „Im Programm“ (Film, Städte, Kinos, Weitersagen) direkt unter der
 * Einleitung; darunter „Nach Stadt“ (nach Land, Stadt, Film, Kino und Termin aus den Kinolisten) und „Aus dem
 * Kinojahr“ mit den übrigen Beiträgen der Rubrik.
 *
 * @var array $args { @type array $rubrik, @type array $filme Ergebnis von tamil_kino_filme(), @type int[] $ids }
 */

defined( 'ABSPATH' ) || exit;

$rubrik  = $args['rubrik'];
$filme   = $args['filme'];
$ids     = array_values( array_diff( $args['ids'], wp_list_pluck( $filme, 'post' ) ) );
$laender = array(
	'DE' => __( 'Deutschland', 'tamil' ),
	'AT' => __( 'Österreich', 'tamil' ),
	'CH' => __( 'Schweiz', 'tamil' ),
);
$termin  = static function ( array $k ): string {
	$fmt = static fn( string $d ): string => wp_date( 'j.n.', (int) strtotime( $d ) );
	if ( ! empty( $k['termine'] ) ) {
		/* translators: 1: Anzahl, 2: Datum */
		return sprintf( _n( '%1$d Vorstellung ab %2$s', '%1$d Vorstellungen ab %2$s', count( $k['termine'] ), 'tamil' ), count( $k['termine'] ), $fmt( (string) $k['termine'][0] ) );
	}
	if ( ! empty( $k['von'] ) && ! empty( $k['bis'] ) ) {
		/* translators: 1: Beginn, 2: Ende */
		return sprintf( __( '%1$s bis %2$s', 'tamil' ), $fmt( (string) $k['von'] ), $fmt( (string) $k['bis'] ) );
	}
	/* translators: %s: Datum */
	return ! empty( $k['von'] ) ? sprintf( __( 'ab %s', 'tamil' ), $fmt( (string) $k['von'] ) ) : '';
};
// Nach Stadt: Land → Stadt → Einträge (Film, Kino, Termin, Link).
$orte = array();
foreach ( $filme as $f ) {
	foreach ( (array) ( $f['fakten']['kinos'] ?? array() ) as $k ) {
		$stadt = trim( (string) ( $k['stadt'] ?? '' ) );
		if ( '' === $stadt ) {
			continue;
		}
		$land                      = (string) ( $k['land'] ?? '' );
		$orte[ $land ][ $stadt ][] = array(
			'film'   => $f['film'],
			'kino'   => trim( (string) ( $k['kino'] ?? '' ) ),
			'termin' => $termin( $k ),
			'url'    => (string) ( $k['url'] ?? '' ),
		);
	}
}
uksort( $orte, static fn( $a, $b ) => array_search( $a, array_keys( $laender ), true ) <=> array_search( $b, array_keys( $laender ), true ) );
// Foto im Kopf: der erste Film oder Beitrag der Rubrik mit Foto; eine Grafik nur, wenn es kein Foto gibt (ungeschnitten).
$bild_id = tamil_leitbild( array_merge( wp_list_pluck( $filme, 'post' ), $ids ) );
$figur   = $bild_id ? tamil_figur(
	$bild_id,
	array(
		'klasse' => 'bild kopf-bild',
		'size'   => 'tamil-card',
		'eager'  => true,
		'alt'    => true,
	)
) : '';
$stand   = max( wp_list_pluck( $filme, 'stand' ) );
?>
<header class="seitenkopf<?php echo '' !== $figur ? ' mit-bild' : ''; ?>">
	<div class="wrap">
		<div class="sk-text">
			<h1><?php echo esc_html( $rubrik['label'] ); ?></h1>
			<p class="satz"><?php echo esc_html( $rubrik['beschreibung'] ); ?></p>
			<p class="aktionen">
				<?php
				if ( $orte ) :
					?>
					<a class="textlink" href="#nach-stadt"><?php esc_html_e( 'Meine Stadt finden', 'tamil' ); ?></a><?php endif; ?>
				<a class="textlink" href="<?php echo esc_url( tamil_wa_teilen( __( 'Tamilisches Kino diese Woche', 'tamil' ), $rubrik['url'] ) ); ?>"><?php esc_html_e( 'Per WhatsApp schicken', 'tamil' ); ?></a>
			</p>
			<section class="bogen" aria-labelledby="im-programm">
				<div class="bogen-kopf">
					<h2 id="im-programm"><?php esc_html_e( 'Im Programm', 'tamil' ); ?></h2>
					<p class="bogen-stand"><?php echo esc_html( tamil_stand( $stand ) ); ?></p>
				</div>
				<?php tamil_kino_tafel( $filme, true ); ?>
			</section>
		</div>
		<?php echo $figur; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_figur() ?>
	</div>
</header>
<?php tamil_leaderboard(); ?>

<?php if ( $orte ) : ?>
	<section class="abschnitt" aria-labelledby="nach-stadt">
		<div class="wrap schmal">
			<section class="bogen">
				<div class="bogen-kopf"><h2 id="nach-stadt"><?php esc_html_e( 'Nach Stadt', 'tamil' ); ?></h2></div>
				<table class="tafel orte">
					<thead><tr><th scope="col"><?php esc_html_e( 'Stadt', 'tamil' ); ?></th><th scope="col"><?php esc_html_e( 'Film, Kino und Termin', 'tamil' ); ?></th></tr></thead>
					<?php foreach ( $orte as $land => $staedte ) : ?>
						<?php ksort( $staedte, SORT_LOCALE_STRING ); ?>
						<tbody>
							<tr class="land"><th scope="rowgroup" colspan="2"><?php echo esc_html( $laender[ $land ] ?? $land ); ?></th></tr>
							<?php foreach ( $staedte as $stadt => $eintraege ) : ?>
								<?php foreach ( $eintraege as $e ) : ?>
									<tr>
										<th scope="row" class="stadt"><?php echo esc_html( $stadt ); ?></th>
										<td class="was">
											<?php echo esc_html( '„' . $e['film'] . '“' ); ?>
											<span class="unter">
												<?php echo esc_html( trim( $e['kino'] . ( '' !== $e['termin'] ? ', ' . $e['termin'] : '' ), ', ' ) ); ?>
												<?php
												if ( '' !== $e['url'] ) :
													?>
													<a class="ticket" href="<?php echo esc_url( $e['url'] ); ?>" target="_blank" rel="noopener nofollow"><?php esc_html_e( 'Tickets und Zeiten', 'tamil' ); ?></a><?php endif; ?>
											</span>
										</td>
									</tr>
								<?php endforeach; ?>
							<?php endforeach; ?>
						</tbody>
					<?php endforeach; ?>
				</table>
				<p class="bogen-fuss notiz"><?php esc_html_e( 'Aus den Programmen der Kinos, Angaben ohne Gewähr. Fehlt ein Kino? Schreibt der Redaktion.', 'tamil' ); ?></p>
			</section>
		</div>
	</section>
<?php endif; ?>

<?php if ( $ids ) : ?>
	<section class="abschnitt" aria-labelledby="kinojahr">
		<div class="wrap schmal">
			<div class="kopfzeile"><h2 id="kinojahr"><?php esc_html_e( 'Aus dem Kinojahr', 'tamil' ); ?></h2></div>
			<table class="tafel jahr">
				<thead><tr><th scope="col"><?php esc_html_e( 'Tag', 'tamil' ); ?></th><th scope="col"><?php esc_html_e( 'Was und wo', 'tamil' ); ?></th></tr></thead>
				<tbody>
					<?php foreach ( $ids as $id ) : ?>
						<?php $ort = trim( (string) get_post_meta( $id, 'ort', true ) ); ?>
						<tr>
							<td class="t-tag"><?php echo tamil_zeilen_tag( (int) get_post_timestamp( $id ), 't' ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_zeilen_tag() ?></td>
							<td class="was"><a href="<?php echo esc_url( get_permalink( $id ) ); ?>"><?php echo esc_html( get_the_title( $id ) ); ?></a>
							<?php
							if ( '' !== $ort ) :
								?>
								<span class="unter"><?php echo esc_html( $ort ); ?></span><?php endif; ?></td>
						</tr>
					<?php endforeach; ?>
				</tbody>
			</table>
			<?php get_template_part( 'template-parts/pagination' ); ?>
		</div>
	</section>
<?php endif; ?>
