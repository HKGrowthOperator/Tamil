<?php
/**
 * Seite (Impressum, Datenschutz, Über uns, Verzeichnis, Werben …): Kopf und Text wie im Artikel; Fließtext auf
 * Lesebreite, Formulare, Tabellen und Listen aus den Plugins dürfen die breitere Spalte nutzen.
 */

defined( 'ABSPATH' ) || exit;

get_header();

while ( have_posts() ) :
	the_post();
	$tamil_bild = tamil_bild(
		(int) get_the_ID(),
		array(
			'eager'  => true,
			'klasse' => 'artikel__bild',
			'sizes'  => '(min-width: 1024px) 1040px, (min-width: 600px) 720px, 100vw',
		)
	);
	?>
	<article <?php post_class( 'artikel seite' ); ?>>
		<header class="artikel__kopf">
			<h1 class="artikel__titel"><?php the_title(); ?></h1>
		</header>
		<?php if ( '' !== $tamil_bild ) : ?>
			<figure class="artikel__figur">
				<?php echo $tamil_bild; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_bild() ?>
				<figcaption class="artikel__nachweis"><?php echo esc_html( str_replace( ' · ', ', ', tamil_bildnachweis( (int) get_the_ID() ) ) ); ?></figcaption>
			</figure>
		<?php endif; ?>
		<div class="artikel__haupt">
			<div class="artikel__text">
				<div class="inhalt"><?php the_content(); ?></div>
			</div>
		</div>
	</article>
	<?php
endwhile;

get_footer();
