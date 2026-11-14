<?php
/**
 * Rubrik: Seitenkopf mit Beschreibung, der neueste Beitrag als Aufmacher (Foto, Datumsblock, Titel, Vorspann), dann
 * die übrigen Beiträge als Strom nach Monaten und die Seitennavigation. Die Rubrik „Kino“ zeigt auf Seite 1 vorn
 * das Kinoprogramm (template-parts/kino-seite.php).
 */

defined( 'ABSPATH' ) || exit;

get_header();

$term   = get_queried_object();
$slug   = $term instanceof WP_Term ? $term->slug : '';
$rubrik = tamil_rubrik( $slug );
$paged  = max( 1, (int) get_query_var( 'paged' ) );
$ids    = array_map( 'intval', wp_list_pluck( $GLOBALS['wp_query']->posts, 'ID' ) );
$kino   = 'kino' === $slug && 1 === $paged && function_exists( 'tamil_site_kino_posts' );

if ( $kino ) {
	get_template_part(
		'template-parts/kino-seite',
		null,
		array(
			'rubrik' => $rubrik,
			'filme'  => tamil_kino_filme( 6 ),
			'ids'    => $ids,
		)
	);
	get_footer();
	return;
}
?>
<header class="seitenkopf">
	<div class="wrap">
		<h1><?php echo esc_html( $rubrik['label'] ); ?></h1>
		<?php
		if ( $rubrik['beschreibung'] ) :
			?>
			<p class="satz"><?php echo esc_html( $rubrik['beschreibung'] ); ?></p><?php endif; ?>
	</div>
</header>
<?php if ( $ids ) : ?>
	<?php
	$lead = 1 === $paged ? array_shift( $ids ) : 0;
	if ( $lead ) :
		$link  = (string) get_permalink( $lead );
		$titel = get_the_title( $lead );
		$ort   = trim( (string) get_post_meta( $lead, 'ort', true ) );
		$figur = tamil_figur(
			$lead,
			array(
				'klasse' => 'bild',
				'size'   => 'tamil-lead',
				'eager'  => true,
				'alt'    => true,
			)
		);
		?>
		<section class="abschnitt rubrik-lead" aria-label="<?php esc_attr_e( 'Neuester Beitrag', 'tamil' ); ?>">
			<div class="wrap lead<?php echo '' === $figur ? ' ohne-bild' : ''; ?>">
				<?php echo $figur; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_figur() ?>
				<div class="lead-text">
					<?php tamil_tag_block( (int) get_post_timestamp( $lead ), '' !== $ort ? array( esc_html( $ort ) ) : array() ); ?>
					<h2 class="lead-titel"><a href="<?php echo esc_url( $link ); ?>"><?php echo esc_html( $titel ); ?></a></h2>
					<p class="teaser"><?php echo tamil_text( tamil_standfirst( $lead ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_text() ?></p>
					<p class="aktionen"><a class="textlink" href="<?php echo esc_url( tamil_wa_teilen( $titel, $link ) ); ?>"><?php esc_html_e( 'Per WhatsApp schicken', 'tamil' ); ?></a></p>
				</div>
			</div>
		</section>
		<?php tamil_leaderboard(); ?>
	<?php endif; ?>
	<?php if ( $ids ) : ?>
		<section class="abschnitt" aria-label="<?php esc_attr_e( 'Beiträge', 'tamil' ); ?>">
			<div class="wrap">
				<?php
				tamil_strom(
					$ids,
					array(
						'monat'  => 'h2',
						'titel'  => 'h3',
						'teaser' => 'immer',
						'rubrik' => false,
					)
				);
				?>
			</div>
		</section>
	<?php endif; ?>
	<div class="wrap"><?php get_template_part( 'template-parts/pagination' ); ?></div>
<?php else : ?>
	<section class="abschnitt">
		<div class="wrap">
			<?php /* translators: %s: Rubrik */ ?>
			<h2 class="strom-kopf"><?php echo esc_html( sprintf( __( 'Hier entsteht die Rubrik %s', 'tamil' ), $rubrik['label'] ) ); ?></h2>
			<p class="satz"><?php esc_html_e( 'Noch keine Beiträge. Ihr habt ein Thema, ein Turnier oder ein Fest? Meldet es der Redaktion.', 'tamil' ); ?></p>
			<p class="aktionen"><a class="textlink" href="<?php echo esc_url( tamil_seiten_url( 'kontakt' ) ); ?>"><?php esc_html_e( 'Thema vorschlagen', 'tamil' ); ?></a></p>
		</div>
	</section>
<?php endif; ?>
<?php
get_footer();
