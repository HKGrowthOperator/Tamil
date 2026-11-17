<?php
/**
 * Startseite klar2: Aufmacher mit Titel im Bild, daneben (Desktop) „Weitere Meldungen“, darunter vier Nebenstücke
 * und die Rubrikkacheln; Werbeplatz 01; dunkler Bereich „Diese Woche“ (Kino und Termine); „Küche“; Werbeplatz
 * Billboard; weitere Rubrikblöcke. Auswahl aus tamil_start_auswahl() (inc/queries.php).
 */

defined( 'ABSPATH' ) || exit;

get_header();

$tamil_a = tamil_start_auswahl();

if ( ! $tamil_a['lead'] ) :
	?>
	<div class="innen seitenkopf">
		<h1 class="seitenkopf__titel"><?php esc_html_e( 'Noch keine Beiträge', 'tamil' ); ?></h1>
		<p class="seitenkopf__zeile"><?php esc_html_e( 'Sobald der erste Beitrag veröffentlicht ist, erscheint hier die Startseite.', 'tamil' ); ?></p>
	</div>
	<?php
	get_footer();
	return;
endif;

$tamil_aufmacher = tamil_anr_imbild(
	$tamil_a['lead'],
	array(
		'klasse'   => 'aufmacher',
		'rahmen'   => 'r43',
		'ebene'    => 'h2',
		'vorspann' => true,
		'eager'    => true,
		'sizes'    => '(min-width: 1024px) 780px, (min-width: 600px) calc(100vw - 48px), 100vw',
	)
);
?>
<h1 class="nur-vorlesen"><?php echo esc_html( get_bloginfo( 'name' ) . ', ' . __( 'Startseite', 'tamil' ) ); ?></h1>

<div class="innen oben">
	<?php echo $tamil_aufmacher; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild() ?>

	<?php if ( $tamil_a['neben'] ) : ?>
		<section class="neben" aria-label="<?php esc_attr_e( 'Weitere Geschichten', 'tamil' ); ?>">
			<?php
			foreach ( $tamil_a['neben'] as $tamil_id ) {
				echo tamil_anr_stueck( $tamil_id ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_stueck()
			}
			?>
		</section>
	<?php endif; ?>

	<?php if ( $tamil_a['meldungen'] ) : ?>
		<section class="meldungen" aria-labelledby="t-meldungen">
			<h2 class="block-titel" id="t-meldungen"><?php esc_html_e( 'Weitere Meldungen', 'tamil' ); ?></h2>
			<ul>
				<?php
				foreach ( $tamil_a['meldungen'] as $tamil_id ) {
					echo tamil_anr_zeile( $tamil_id, array( 'sizes' => '(min-width: 600px) 120px, 96px' ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_zeile()
				}
				?>
			</ul>
		</section>
	<?php endif; ?>

	<?php echo tamil_kacheln( $tamil_a['kacheln'], __( 'Rubriken mit Bild', 'tamil' ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_kacheln() ?>
</div>

<?php
// Werbeplatz 01 unter dem ersten Abschnitt (nicht über dem Aufmacher).
tamil_leaderboard( 'innen anzeige-zwischen' );

get_template_part( 'template-parts/home/woche', null, array( 'woche' => $tamil_a['woche'] ) );

if ( $tamil_a['kueche'] ) {
	get_template_part( 'template-parts/home/kueche', null, array( 'ids' => $tamil_a['kueche'] ) );
}

$tamil_billboard = function_exists( 'tamil_site_anzeige' ) ? tamil_site_anzeige( 'billboard', false ) : '';
if ( '' !== $tamil_billboard ) :
	?>
	<div class="innen anzeige-zwischen"><?php echo $tamil_billboard; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Werbeplatz aus dem Plugin, dort escapt ?></div>
	<?php
endif;

foreach ( $tamil_a['rubriken'] as $tamil_slug => $tamil_ids ) {
	get_template_part(
		'template-parts/home/rubrik',
		null,
		array(
			'slug' => $tamil_slug,
			'ids'  => $tamil_ids,
		)
	);
}

get_footer();
