<?php
/**
 * Rubrik Kino, Seite 1: Seitenkopf; „Im Programm“ als dunkler Bereich wie „Diese Woche“ – nur Filme mit Spieltagen
 * ab heute: der erste (mit eigenem Bild, sonst der erste überhaupt) groß, daneben die übrigen als Bildkacheln; läuft
 * nur einer, stehen neben ihm seine Angaben (Zahl der Kinos, Städte, Link zur Tabelle). „Nach Stadt“ als Tabelle mit
 * dem Bild des Films in jeder Zeile; „Aus dem Kinojahr“ mit den übrigen Beiträgen als Liste mit Bild; die übrigen
 * Rubriken als Kacheln.
 *
 * @var array $args { @type array $rubrik, @type array $filme Ergebnis von tamil_kino_filme(), @type int[] $ids }
 */

defined( 'ABSPATH' ) || exit;

$tamil_rubrik = $args['rubrik'];
$tamil_filme  = $args['filme'];
$tamil_posts  = array_map( 'intval', wp_list_pluck( $tamil_filme, 'post' ) );
$tamil_ids    = array_values( array_diff( array_map( 'intval', $args['ids'] ), $tamil_posts ) );
$tamil_lead   = (int) ( array_values( array_filter( $tamil_posts, 'tamil_bild_zeigbar' ) )[0] ?? ( $tamil_posts[0] ?? 0 ) );
$tamil_lfilm  = array_values( array_filter( $tamil_filme, static fn( $f ) => (int) $f['post'] === $tamil_lead ) )[0] ?? array();
$tamil_rest   = array_values( array_filter( $tamil_filme, static fn( $f ) => (int) $f['post'] !== $tamil_lead ) );
$tamil_gross  = $tamil_lead ? tamil_anr_imbild(
	$tamil_lead,
	array(
		'klasse' => 'kachel kachel--gross',
		'ebene'  => 'h3',
		'eager'  => true,
		'sizes'  => '(min-width: 1024px) 780px, (min-width: 600px) calc(100vw - 48px), calc(100vw - 32px)',
	)
) : '';
?>
<div class="innen">
	<header class="seitenkopf">
		<h1 class="seitenkopf__titel"><?php echo esc_html( $tamil_rubrik['label'] ); ?></h1>
		<p class="seitenkopf__zeile"><?php echo esc_html( $tamil_rubrik['beschreibung'] ); ?></p>
		<p class="aktionen">
			<?php
			if ( $tamil_filme ) :
				?>
				<a class="textlink" href="#nach-stadt"><?php esc_html_e( 'Meine Stadt finden', 'tamil' ); ?></a><?php endif; ?>
			<a class="textlink" href="<?php echo esc_url( tamil_wa_teilen( __( 'Tamilisches Kino diese Woche', 'tamil' ), $tamil_rubrik['url'] ) ); ?>"><?php esc_html_e( 'Per WhatsApp schicken', 'tamil' ); ?></a>
		</p>
	</header>
</div>

<section class="woche woche--seite" aria-labelledby="t-programm">
	<div class="innen">
		<h2 class="woche__titel" id="t-programm"><?php esc_html_e( 'Im Programm', 'tamil' ); ?></h2>
		<div class="programm<?php echo '' === $tamil_gross ? ' ohne-gross' : ''; ?>">
			<?php echo $tamil_gross; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild() ?>
			<div class="woche__gruppe">
				<p class="woche__art" id="t-filme"><?php echo esc_html( $tamil_filme && '' !== $tamil_filme[0]['stand'] ? $tamil_filme[0]['stand'] : __( 'Filme mit laufender Spielzeit', 'tamil' ) ); ?></p>
				<?php if ( $tamil_lfilm && ! $tamil_rest ) : ?>
					<div class="programm__fakten">
						<?php /* translators: %d: Anzahl der Kinos */ ?>
						<p class="grafik__zahl"><?php echo esc_html( sprintf( _n( '%d Kino', '%d Kinos', (int) $tamil_lfilm['kinos'], 'tamil' ), (int) $tamil_lfilm['kinos'] ) ); ?></p>
						<?php if ( $tamil_lfilm['staedte'] ) : ?>
							<p class="grafik__orte"><?php echo esc_html( tamil_staedte_kurz( $tamil_lfilm['staedte'], 8 ) ); ?></p>
						<?php endif; ?>
						<p><a class="textlink" href="#nach-stadt"><?php esc_html_e( 'Kinos und Termine nach Stadt', 'tamil' ); ?></a></p>
					</div>
				<?php endif; ?>
				<ul aria-labelledby="t-filme">
					<?php
					foreach ( $tamil_rest as $tamil_f ) {
						echo tamil_grafik_kino( $tamil_f ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_grafik_kino()
					}
					if ( ! $tamil_filme ) {
						echo tamil_grafik_leer( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_grafik_leer()
							__( 'Kino melden', 'tamil' ),
							__( 'Für diese Woche kennen wir keine tamilische Vorstellung. Kennt ihr eine? Schickt sie der Redaktion.', 'tamil' ),
							tamil_seiten_url( 'kontakt' ),
							'kino'
						);
					}
					?>
				</ul>
			</div>
		</div>
	</div>
</section>

<div class="innen">
	<?php if ( $tamil_filme ) : ?>
		<section class="block" id="nach-stadt" aria-labelledby="t-nach-stadt">
			<h2 class="block-titel" id="t-nach-stadt"><?php esc_html_e( 'Nach Stadt', 'tamil' ); ?></h2>
			<?php tamil_kino_orte_tafel( $tamil_filme, true ); ?>
			<p class="block__notiz"><?php esc_html_e( 'Aus den Programmen der Kinos, Angaben ohne Gewähr. Fehlt ein Kino? Schreibt der Redaktion.', 'tamil' ); ?></p>
		</section>
	<?php endif; ?>
	<?php tamil_leaderboard( 'anzeige-zwischen' ); ?>

	<?php if ( $tamil_ids ) : ?>
		<section class="block" aria-labelledby="t-kinojahr">
			<h2 class="block-titel" id="t-kinojahr"><?php esc_html_e( 'Aus dem Kinojahr', 'tamil' ); ?></h2>
			<?php echo tamil_zeilen( $tamil_ids, array( 'rubrik' => false ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_zeilen() ?>
		</section>
	<?php endif; ?>
	<?php get_template_part( 'template-parts/pagination' ); ?>

	<?php echo tamil_kacheln( tamil_kacheln_ohne( 'kino' ), __( 'Weitere Rubriken', 'tamil' ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_kacheln() ?>
</div>
