<?php
/**
 * Suche in klar2: Seitenkopf mit Suchfeld und Zahl der Treffer, Treffer als Liste mit Bild (Suchwort hervorgehoben),
 * Seitennavigation. Ohne Suchbegriff (Link „Suche“ in der Kopfzeile) nur das Suchfeld und die Rubriken.
 */

defined( 'ABSPATH' ) || exit;

get_header();
global $wp_query;
$tamil_q   = trim( get_search_query( false ) );
$tamil_ids = '' !== $tamil_q ? array_map( 'intval', wp_list_pluck( $wp_query->posts, 'ID' ) ) : array();
$tamil_n   = '' !== $tamil_q ? (int) $wp_query->found_posts : 0;
tamil_cache_fuellen( $tamil_ids );
?>
<div class="innen">
	<header class="seitenkopf">
		<h1 class="seitenkopf__titel"><?php esc_html_e( 'Suche', 'tamil' ); ?></h1>
		<?php get_search_form(); ?>
		<p class="seitenkopf__zeile">
			<?php
			if ( '' === $tamil_q ) {
				esc_html_e( 'Sucht nach einem Film, einer Stadt, einem Fest oder einem Namen.', 'tamil' );
			} else {
				/* translators: 1: Anzahl, 2: Suchbegriff */
				echo tamil_text( sprintf( _n( '%1$d Beitrag zu „%2$s“, die neuesten zuerst', '%1$d Beiträge zu „%2$s“, die neuesten zuerst', $tamil_n, 'tamil' ), $tamil_n, $tamil_q ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_text(), tamilische Wörter mit lang="ta"
			}
			?>
		</p>
	</header>

	<?php if ( $tamil_ids ) : ?>
		<section class="block block--treffer" aria-label="<?php esc_attr_e( 'Treffer', 'tamil' ); ?>">
			<?php
			echo tamil_zeilen( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_zeilen()
				$tamil_ids,
				array(
					'ebene'    => 'h2',
					'markiere' => $tamil_q,
				)
			);
			?>
		</section>
		<?php get_template_part( 'template-parts/pagination' ); ?>
	<?php elseif ( '' !== $tamil_q ) : ?>
		<section class="block leer">
			<h2 class="block-titel"><?php esc_html_e( 'Nichts gefunden', 'tamil' ); ?></h2>
			<p class="leer__satz"><?php esc_html_e( 'Versucht es mit einem anderen Wort, zum Beispiel einem Filmtitel, einer Stadt oder einem Fest. Oder stöbert in den Rubriken.', 'tamil' ); ?></p>
		</section>
	<?php endif; ?>

	<?php if ( ! $tamil_ids ) : ?>
		<?php echo tamil_kacheln( tamil_kacheln_ohne(), __( 'Rubriken', 'tamil' ) ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_kacheln() ?>
	<?php endif; ?>
</div>
<?php
get_footer();
