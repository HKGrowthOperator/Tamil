<?php
/**
 * Rubrik in klar2: Seitenkopf mit Name und Beschreibung; auf Seite 1 der neueste Beitrag mit eigenem Bild (sonst der
 * neueste) als Aufmacher (4:3, Titel im Bild) und daneben die nächsten vier als Meldungen; dann alle weiteren als Liste
 * mit Bild und Vorspann, Seitennavigation und die übrigen Rubriken als Kacheln. Die Rubrik „Kino“ zeigt auf Seite 1
 * vorn das Kinoprogramm (template-parts/kino-seite.php).
 */

defined( 'ABSPATH' ) || exit;

get_header();

$tamil_term   = get_queried_object();
$tamil_slug   = $tamil_term instanceof WP_Term ? $tamil_term->slug : '';
$tamil_rubrik = tamil_rubrik( $tamil_slug );
$tamil_paged  = max( 1, (int) get_query_var( 'paged' ) );
$tamil_ids    = array_map( 'intval', wp_list_pluck( $GLOBALS['wp_query']->posts, 'ID' ) );
tamil_cache_fuellen( $tamil_ids );

if ( 'kino' === $tamil_slug && 1 === $tamil_paged && function_exists( 'tamil_site_kino_posts' ) ) {
	get_template_part(
		'template-parts/kino-seite',
		null,
		array(
			'rubrik' => $tamil_rubrik,
			'filme'  => tamil_kino_filme( 6 ),
			'ids'    => $tamil_ids,
		)
	);
	get_footer();
	return;
}

$tamil_lead  = 0;
$tamil_seite = array();
if ( 1 === $tamil_paged && $tamil_ids ) {
	$tamil_mit_bild = array_values( array_filter( $tamil_ids, 'tamil_bild_zeigbar' ) );
	$tamil_lead     = (int) ( $tamil_mit_bild[0] ?? $tamil_ids[0] );
	$tamil_rest     = array_values( array_diff( $tamil_ids, array( $tamil_lead ) ) );
	$tamil_seite    = array_slice( $tamil_rest, 0, 4 );
	$tamil_ids      = array_values( array_diff( $tamil_rest, $tamil_seite ) );
}
?>
<div class="innen">
	<header class="seitenkopf">
		<h1 class="seitenkopf__titel"><?php echo esc_html( $tamil_rubrik['label'] ); ?></h1>
		<?php
		if ( '' !== $tamil_rubrik['beschreibung'] ) :
			?>
			<p class="seitenkopf__zeile"><?php echo esc_html( $tamil_rubrik['beschreibung'] ); ?></p><?php endif; ?>
	</header>

	<?php if ( $tamil_lead ) : ?>
		<div class="buehne">
			<?php
			echo tamil_anr_imbild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_imbild()
				$tamil_lead,
				array(
					'klasse'   => 'aufmacher aufmacher--rubrik',
					'rahmen'   => 'r43',
					'ebene'    => 'h2',
					'vorspann' => true,
					'eager'    => true,
					'sizes'    => '(min-width: 1024px) 780px, (min-width: 600px) calc(100vw - 48px), 100vw',
				)
			);
			?>
			<?php if ( $tamil_seite ) : ?>
				<section class="meldungen buehne__seite" aria-labelledby="t-neu">
					<h2 class="block-titel" id="t-neu"><?php esc_html_e( 'Neu in der Rubrik', 'tamil' ); ?></h2>
					<ul>
						<?php
						foreach ( $tamil_seite as $tamil_id ) {
							echo tamil_anr_zeile( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_anr_zeile()
								$tamil_id,
								array(
									'rubrik' => false,
									'sizes'  => '(min-width: 600px) 120px, 96px',
								)
							);
						}
						?>
					</ul>
				</section>
			<?php endif; ?>
		</div>
		<?php tamil_leaderboard( 'anzeige-zwischen' ); ?>
	<?php endif; ?>

	<?php if ( $tamil_ids ) : ?>
		<section class="block" aria-labelledby="t-alle">
			<?php /* translators: %s: Rubrik */ ?>
			<h2 class="block-titel" id="t-alle"><?php echo esc_html( 1 === $tamil_paged ? sprintf( __( 'Weitere Beiträge aus %s', 'tamil' ), $tamil_rubrik['label'] ) : sprintf( __( 'Beiträge aus %s', 'tamil' ), $tamil_rubrik['label'] ) ); ?></h2>
			<?php echo tamil_zeilen( $tamil_ids, array( 'rubrik' => false ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_zeilen() ?>
		</section>
	<?php endif; ?>
	<?php get_template_part( 'template-parts/pagination' ); ?>

	<?php if ( ! $tamil_lead && ! $tamil_ids ) : ?>
		<section class="block leer">
			<?php /* translators: %s: Rubrik */ ?>
			<h2 class="block-titel"><?php echo esc_html( sprintf( __( 'Hier entsteht die Rubrik %s', 'tamil' ), $tamil_rubrik['label'] ) ); ?></h2>
			<p class="leer__satz"><?php esc_html_e( 'Noch keine Beiträge. Ihr habt ein Thema, ein Turnier oder ein Fest? Meldet es der Redaktion.', 'tamil' ); ?></p>
			<p class="aktionen"><a class="textlink" href="<?php echo esc_url( tamil_seiten_url( 'kontakt' ) ); ?>"><?php esc_html_e( 'Thema vorschlagen', 'tamil' ); ?></a></p>
		</section>
	<?php endif; ?>

	<?php echo tamil_kacheln( tamil_kacheln_ohne( $tamil_slug ), __( 'Weitere Rubriken', 'tamil' ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_kacheln() ?>
</div>
<?php
get_footer();
