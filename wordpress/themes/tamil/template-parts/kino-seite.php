<?php
/**
 * Rubrik Kino, Seite 1: Seitenkopf (Foto nur, wenn es eins gibt), links „Im Programm“ (Filme mit laufender Spielzeit:
 * Film, Städte, Kinos, Weitersagen) direkt unter der Einleitung; darunter „Nach Stadt“ (Land, Stadt, Film, Kino,
 * Termin) und „Aus dem Kinojahr“ mit den übrigen Beiträgen der Rubrik. Ohne laufende Filme: Leerzustand wie bei
 * der Festtafel.
 *
 * @var array $args { @type array $rubrik, @type array $filme Ergebnis von tamil_kino_filme(), @type int[] $ids }
 */

defined( 'ABSPATH' ) || exit;

$rubrik  = $args['rubrik'];
$filme   = $args['filme'];
$ids     = array_values( array_diff( $args['ids'], wp_list_pluck( $filme, 'post' ) ) );
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
?>
<header class="seitenkopf<?php echo '' !== $figur ? ' mit-bild' : ''; ?>">
	<div class="wrap">
		<div class="sk-text">
			<h1><?php echo esc_html( $rubrik['label'] ); ?></h1>
			<p class="satz"><?php echo esc_html( $rubrik['beschreibung'] ); ?></p>
			<p class="aktionen">
				<?php
				if ( $filme ) :
					?>
					<a class="textlink" href="#nach-stadt"><?php esc_html_e( 'Meine Stadt finden', 'tamil' ); ?></a><?php endif; ?>
				<a class="textlink" href="<?php echo esc_url( tamil_wa_teilen( __( 'Tamilisches Kino diese Woche', 'tamil' ), $rubrik['url'] ) ); ?>"><?php esc_html_e( 'Per WhatsApp schicken', 'tamil' ); ?></a>
			</p>
			<section class="bogen" aria-labelledby="im-programm">
				<div class="bogen-kopf">
					<h2 id="im-programm"><?php esc_html_e( 'Im Programm', 'tamil' ); ?></h2>
					<?php
					if ( $filme && '' !== $filme[0]['stand'] ) :
						?>
						<p class="bogen-stand"><?php echo esc_html( $filme[0]['stand'] ); ?></p><?php endif; ?>
				</div>
				<?php
				if ( $filme ) {
					tamil_kino_tafel( $filme, true );
				} else {
					echo '<p class="bogen-leer">' . esc_html__( 'Für diese Woche kennen wir keine tamilische Vorstellung. Kennt ihr eine? Schickt sie der Redaktion.', 'tamil' ) . '</p>';
				}
				?>
			</section>
		</div>
		<?php echo $figur; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_figur() ?>
	</div>
</header>

<?php if ( $filme ) : ?>
	<section class="abschnitt" aria-labelledby="nach-stadt">
		<div class="wrap schmal">
			<section class="bogen">
				<div class="bogen-kopf"><h2 id="nach-stadt"><?php esc_html_e( 'Nach Stadt', 'tamil' ); ?></h2></div>
				<?php tamil_kino_orte_tafel( $filme ); ?>
				<p class="bogen-fuss notiz"><?php esc_html_e( 'Aus den Programmen der Kinos, Angaben ohne Gewähr. Fehlt ein Kino? Schreibt der Redaktion.', 'tamil' ); ?></p>
			</section>
		</div>
	</section>
<?php endif; ?>
<?php tamil_leaderboard(); ?>

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
