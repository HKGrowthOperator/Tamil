<?php
/**
 * Seite (Impressum, Datenschutz, Über uns, Verzeichnis, Werben …): Kopf und Text wie im Artikel; Fließtext auf
 * Lesebreite, Formulare, Tabellen und Listen aus den Plugins dürfen die breitere Spalte nutzen.
 *
 * Impressum und Datenschutz außerhalb des Echtbetriebs: nur der Hinweis „Entwurf: Der Text von KBS folgt.“ Der alte
 * Inhalt (nennt Dienste, die nicht genutzt werden, und tote Links) wird nicht gezeigt; den Text liefert KBS.
 */

defined( 'ABSPATH' ) || exit;

get_header();

while ( have_posts() ) :
	the_post();
	$tamil_entwurf = tamil_ist_rechtstext_entwurf( (int) get_the_ID() );
	$tamil_bild    = $tamil_entwurf ? '' : tamil_bild(
		(int) get_the_ID(),
		array(
			'eager'     => true,
			'nur_eigen' => true, // Seiten (Impressum, Datenschutz …) bekommen kein Symbolbild
			'klasse'    => 'artikel__bild',
			'sizes'     => '(min-width: 1024px) 1040px, (min-width: 600px) 720px, 100vw',
		)
	);
	?>
	<article <?php post_class( 'artikel seite' ); ?>>
		<header class="artikel__kopf">
			<h1 class="artikel__titel"><?php the_title(); ?></h1>
			<?php if ( $tamil_entwurf ) : ?>
				<p class="hinweis-box seite__entwurf" role="note"><strong><?php esc_html_e( 'Entwurf:', 'tamil' ); ?></strong> <?php esc_html_e( 'Der Text von KBS folgt.', 'tamil' ); ?></p>
			<?php endif; ?>
		</header>
		<?php if ( '' !== $tamil_bild ) : ?>
			<figure class="artikel__figur">
				<?php echo $tamil_bild; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_bild() ?>
				<figcaption class="artikel__nachweis"><?php echo wp_kses( tamil_bild_nachweis_html( (int) get_the_ID() ), tamil_nachweis_kses() ); ?></figcaption>
			</figure>
		<?php endif; ?>
		<?php if ( ! $tamil_entwurf ) : ?>
			<div class="artikel__haupt">
				<div class="artikel__text">
					<div class="inhalt"><?php the_content(); ?></div>
				</div>
			</div>
		<?php endif; ?>
	</article>
	<?php
endwhile;

get_footer();
