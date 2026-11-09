<?php
/**
 * Kopfleiste (klebt oben): Logo, Rubriken (ab Desktop), „Werben“, Suche, Menü; mobil darunter die Rubrik-Leiste.
 */

defined( 'ABSPATH' ) || exit;

$items = tamil_nav_items();
?>
<header class="kopf">
	<div class="wrap kopf-zeile">
		<?php get_template_part( 'template-parts/header/logo' ); ?>
		<nav class="nav" aria-label="<?php esc_attr_e( 'Rubriken', 'tamil' ); ?>">
			<?php foreach ( $items as $item ) : ?>
				<a href="<?php echo esc_url( $item['url'] ); ?>"<?php echo $item['aktiv'] ? ' aria-current="page"' : ''; ?>><?php echo esc_html( $item['label'] ); ?></a>
			<?php endforeach; ?>
		</nav>
		<div class="kopf-aktionen">
			<a class="werben" href="<?php echo esc_url( tamil_seiten_url( 'kontakt', 'werben' ) ); ?>"><?php esc_html_e( 'Werben', 'tamil' ); ?></a>
			<button type="button" class="rund" id="suche-btn" aria-controls="suche" aria-expanded="false" aria-label="<?php esc_attr_e( 'Suche öffnen', 'tamil' ); ?>"><?php tamil_icon( 'search', 'ico ico-sm' ); ?></button>
			<button type="button" class="rund" id="burger" aria-controls="menue" aria-expanded="false" aria-label="<?php esc_attr_e( 'Menü öffnen', 'tamil' ); ?>"><?php tamil_icon( 'menu', 'ico ico-sm' ); ?></button>
		</div>
	</div>
	<form class="suche" id="suche" role="search" method="get" action="<?php echo esc_url( home_url( '/' ) ); ?>" hidden>
		<div class="wrap">
			<label class="screen-reader-text" for="q"><?php esc_html_e( 'Suche', 'tamil' ); ?></label>
			<input id="q" type="search" name="s" value="<?php echo esc_attr( get_search_query() ); ?>" placeholder="<?php esc_attr_e( 'Film, Stadt, Fest …', 'tamil' ); ?>">
			<button type="submit" class="knopf"><?php esc_html_e( 'Suchen', 'tamil' ); ?></button>
		</div>
	</form>
	<nav class="rubriken-leiste" aria-label="<?php esc_attr_e( 'Rubriken', 'tamil' ); ?>">
		<?php foreach ( $items as $item ) : ?>
			<a href="<?php echo esc_url( $item['url'] ); ?>"<?php echo $item['aktiv'] ? ' aria-current="page"' : ''; ?>><?php echo esc_html( $item['label'] ); ?></a>
		<?php endforeach; ?>
	</nav>
</header>
