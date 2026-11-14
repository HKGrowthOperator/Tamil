<?php
/**
 * Leiste über dem Kopf (Unterzeile, Termin einreichen, Werben) und Kopfzeile: Logo, Datum (nur Unterseiten, ab
 * 1100 px), vier Ziele, Menü „Mehr“ mit Suche, übrigen Rubriken, Diensten und Social.
 */

defined( 'ABSPATH' ) || exit;

$ziele   = tamil_kopf_ziele();
$dienste = tamil_dienste();
$urls    = wp_list_pluck( $ziele, 'url' );
$weitere = array_filter( tamil_nav_items(), static fn( $item ) => ! in_array( $item['url'], $urls, true ) );
$social  = tamil_social();
$tagline = tamil_opt( 'tagline' );
?>
<div class="leiste">
	<div class="wrap">
		<?php
		if ( '' !== $tagline ) :
			?>
			<p class="leiste-text"><?php echo esc_html( $tagline ); ?></p><?php endif; ?>
		<nav class="leiste-links" aria-label="<?php esc_attr_e( 'Mitmachen', 'tamil' ); ?>">
			<?php foreach ( array_slice( $dienste, 0, 2 ) as $d ) : ?>
				<a href="<?php echo esc_url( $d['url'] ); ?>"<?php echo $d['aktiv'] ? ' aria-current="page"' : ''; ?>><?php echo esc_html( $d['label'] ); ?></a>
			<?php endforeach; ?>
		</nav>
	</div>
</div>
<header class="kopf">
	<div class="wrap">
		<?php get_template_part( 'template-parts/header/logo', null, array( 'class' => 'logo' ) ); ?>
		<?php
		if ( ! is_front_page() ) :
			?>
			<p class="kopf-datum"><time datetime="<?php echo esc_attr( wp_date( 'Y-m-d' ) ); ?>"><?php echo esc_html( tamil_heute() ); ?></time></p><?php endif; ?>
		<nav class="haupt" aria-label="<?php esc_attr_e( 'Hauptnavigation', 'tamil' ); ?>">
			<?php foreach ( $ziele as $z ) : ?>
				<a href="<?php echo esc_url( $z['url'] ); ?>"<?php echo $z['breit'] ? ' class="breit"' : ''; ?><?php echo $z['aktiv'] ? ' aria-current="page"' : ''; ?>><?php echo esc_html( $z['label'] ); ?></a>
			<?php endforeach; ?>
		</nav>
		<details class="menue">
			<summary><?php esc_html_e( 'Mehr', 'tamil' ); ?></summary>
			<div class="menue-paneel">
				<form class="menue-suche" role="search" method="get" action="<?php echo esc_url( home_url( '/' ) ); ?>">
					<label for="kopf-suche"><?php esc_html_e( 'Suche', 'tamil' ); ?></label>
					<span class="zeile-feld">
						<input id="kopf-suche" type="search" name="s" value="<?php echo esc_attr( get_search_query() ); ?>" placeholder="<?php esc_attr_e( 'Film, Stadt, Fest', 'tamil' ); ?>">
						<button type="submit" class="knopf"><?php esc_html_e( 'Suchen', 'tamil' ); ?></button>
					</span>
				</form>
				<div class="menue-spalten">
					<div>
						<h2 class="menue-titel"><?php esc_html_e( 'Rubriken', 'tamil' ); ?></h2>
						<ul>
							<?php foreach ( array_filter( $ziele, static fn( $z ) => $z['breit'] ) as $z ) : ?>
								<li><a href="<?php echo esc_url( $z['url'] ); ?>"<?php echo $z['aktiv'] ? ' aria-current="page"' : ''; ?>><?php echo esc_html( $z['label'] ); ?></a></li>
							<?php endforeach; ?>
							<?php foreach ( $weitere as $item ) : ?>
								<li><a href="<?php echo esc_url( $item['url'] ); ?>"<?php echo $item['aktiv'] ? ' aria-current="page"' : ''; ?>><?php echo esc_html( $item['label'] ); ?></a></li>
							<?php endforeach; ?>
						</ul>
					</div>
					<div>
						<h2 class="menue-titel"><?php esc_html_e( 'Dienste', 'tamil' ); ?></h2>
						<ul>
							<?php foreach ( $dienste as $d ) : ?>
								<li><a href="<?php echo esc_url( $d['url'] ); ?>"<?php echo $d['aktiv'] ? ' aria-current="page"' : ''; ?>><?php echo esc_html( $d['label'] ); ?></a></li>
							<?php endforeach; ?>
							<?php foreach ( $social as $s ) : ?>
								<li><a href="<?php echo esc_url( $s['url'] ); ?>" target="_blank" rel="noopener"><?php echo esc_html( $s['name'] ); ?></a></li>
							<?php endforeach; ?>
						</ul>
					</div>
				</div>
			</div>
		</details>
	</div>
</header>
