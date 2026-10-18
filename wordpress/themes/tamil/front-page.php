<?php
/**
 * Startseite: Bühne, Abschnittsnavigation, Top-Themen, Rubriken, Kino, Production, Termine, Rezept, Community,
 * Newsletter. Abschnitte ohne Inhalt fallen weg (auch ihr Eintrag in der Abschnittsnavigation).
 */

defined( 'ABSPATH' ) || exit;

get_header();

$auswahl = tamil_home_auswahl();
$hat     = array(
	'top-themen'        => (bool) $auswahl['top'],
	'rubrik-news'       => (bool) tamil_rubrik( 'news' )['term'],
	'kino-schaufenster' => (bool) $auswahl['kino'],
	'production'        => (bool) $auswahl['production'],
	'events-teaser'     => function_exists( 'tamil_site_upcoming_events' ) && tamil_site_upcoming_events( 1, array( 'fields' => 'ids' ) )->posts,
	'rezept'            => (bool) $auswahl['rezept'],
	'community'         => (bool) tamil_rubrik( 'community' )['term'],
);
$labels  = array(
	'top-themen'        => __( 'Top-Themen', 'tamil' ),
	'rubrik-news'       => __( 'Nachrichten', 'tamil' ),
	'kino-schaufenster' => __( 'Kino', 'tamil' ),
	'production'        => __( 'Production', 'tamil' ),
	'events-teaser'     => __( 'Events', 'tamil' ),
	'rezept'            => __( 'Küche', 'tamil' ),
	'community'         => __( 'Community', 'tamil' ),
);

if ( ! $auswahl['lead'] ) :
	?>
	<div class="container"><section class="section leer"><h2><?php esc_html_e( 'Noch keine Beiträge', 'tamil' ); ?></h2><p><?php esc_html_e( 'Sobald der erste Beitrag veröffentlicht ist, erscheint hier die Startseite.', 'tamil' ); ?></p></section></div>
	<?php
	get_footer();
	return;
endif;

get_template_part( 'template-parts/home/buehne', null, array( 'auswahl' => $auswahl ) );
?>
<nav class="mininav" aria-label="<?php esc_attr_e( 'Abschnitte der Startseite', 'tamil' ); ?>"><div class="container">
	<?php foreach ( array_filter( $hat ) as $anker => $ja ) : ?>
		<a href="#<?php echo esc_attr( $anker ); ?>"><?php echo esc_html( $labels[ $anker ] ); ?></a>
	<?php endforeach; ?>
</div></nav>
<?php
get_template_part( 'template-parts/home/top-strip', null, array( 'ids' => $auswahl['top'] ) );
?>
<div class="container">
	<?php tamil_anzeige( 'billboard' ); ?>
	<?php
	get_template_part(
		'template-parts/home/rubrik',
		null,
		array(
			'slug' => 'news',
			'ids'  => $auswahl['rubriken']['news'],
		)
	);
	?>
</div>
<?php
get_template_part( 'template-parts/home/kino', null, array( 'post' => $auswahl['kino'] ) );
get_template_part( 'template-parts/home/production', null, array( 'ids' => $auswahl['production'] ) );
?>
<div class="container">
	<?php
	get_template_part(
		'template-parts/home/rubrik',
		null,
		array(
			'slug' => 'kino',
			'ids'  => $auswahl['rubriken']['kino'],
		)
	);
	?>
	<?php get_template_part( 'template-parts/home/events-teaser' ); ?>
	<?php
	get_template_part(
		'template-parts/home/rubrik',
		null,
		array(
			'slug' => 'entertainment',
			'ids'  => $auswahl['rubriken']['entertainment'],
		)
	);
	?>
</div>
<?php
get_template_part( 'template-parts/home/rezept', null, array( 'post' => $auswahl['rezept'] ) );
get_template_part( 'template-parts/home/community', null, array( 'ids' => $auswahl['rubriken']['community'] ) );
?>
<div class="container">
	<?php
	get_template_part(
		'template-parts/home/rubrik',
		null,
		array(
			'slug' => 'kultur',
			'ids'  => $auswahl['rubriken']['kultur'],
		)
	);
	?>
	<?php
	get_template_part(
		'template-parts/home/rubrik',
		null,
		array(
			'slug' => 'sport',
			'ids'  => $auswahl['rubriken']['sport'],
		)
	);
	?>
</div>
<?php
get_template_part( 'template-parts/home/newsletter' );
get_footer();
