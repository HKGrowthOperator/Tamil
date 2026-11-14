<?php
/**
 * Seite (Impressum, Datenschutz, Über uns …): Seitenkopf, optional Foto, Text in Lesebreite.
 */

defined( 'ABSPATH' ) || exit;

get_header();

while ( have_posts() ) :
	the_post();
	$figur = tamil_figur(
		get_the_ID(),
		array(
			'klasse' => 'bild',
			'size'   => 'tamil-lead',
			'link'   => false,
			'eager'  => true,
			'alt'    => true,
		)
	);
	?>
	<article <?php post_class( 'seite' ); ?>>
		<header class="seitenkopf">
			<div class="wrap"><h1><?php the_title(); ?></h1></div>
		</header>
		<?php
		if ( '' !== $figur ) :
			?>
			<div class="artikel-bild seite-bild"><div class="wrap"><?php echo $figur; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_figur() ?></div></div><?php endif; ?>
		<section class="abschnitt">
			<div class="wrap schmal"><div class="inhalt"><?php the_content(); ?></div></div>
		</section>
	</article>
	<?php
endwhile;

get_footer();
