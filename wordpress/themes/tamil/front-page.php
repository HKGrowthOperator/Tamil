<?php
/**
 * Startseite: Bühne, Nachrichten, Kino mit Kinoliste, Termine, Entertainment, Community mit Mitmach-Band, Rezept,
 * Production, Kultur, Sport. Abschnitte ohne Inhalt fallen weg.
 */

defined( 'ABSPATH' ) || exit;

get_header();

$auswahl = tamil_home_auswahl();

if ( ! $auswahl['lead'] ) :
	?>
	<div class="wrap"><section class="abschnitt leer"><h2><?php esc_html_e( 'Noch keine Beiträge', 'tamil' ); ?></h2><p><?php esc_html_e( 'Sobald der erste Beitrag veröffentlicht ist, erscheint hier die Startseite.', 'tamil' ); ?></p></section></div>
	<?php
	get_footer();
	return;
endif;

$rubrik = static function ( string $slug, array $extra = array() ) use ( $auswahl ): void {
	get_template_part(
		'template-parts/home/rubrik',
		null,
		array_merge(
			array(
				'slug' => $slug,
				'ids'  => $auswahl['rubriken'][ $slug ] ?? array(),
			),
			$extra
		)
	);
};

get_template_part( 'template-parts/home/buehne', null, array( 'auswahl' => $auswahl ) );
?>
<div class="wrap"><?php tamil_anzeige( 'billboard' ); ?></div>
<?php
$rubrik( 'news' );
$rubrik( 'kino', array( 'kino' => $auswahl['kino'] ) );
get_template_part( 'template-parts/home/events-teaser' );
$rubrik( 'entertainment' );
get_template_part( 'template-parts/home/community', null, array( 'ids' => $auswahl['rubriken']['community'] ) );
get_template_part( 'template-parts/home/rezept', null, array( 'post' => $auswahl['rezept'] ) );
get_template_part( 'template-parts/home/production', null, array( 'ids' => $auswahl['production'] ) );
$rubrik( 'kultur' );
$rubrik( 'sport' );
get_footer();
