<?php
/**
 * Masthead: Menüknopf (mobil), Unterzeile und Datum, Logo, Suche.
 */

defined( 'ABSPATH' ) || exit;
?>
<div class="masthead">
	<div class="container">
		<button type="button" class="icon-btn burger" id="burger" aria-controls="drawer" aria-expanded="false" aria-label="<?php esc_attr_e( 'Menü öffnen', 'tamil' ); ?>"><?php tamil_icon( 'menu' ); ?></button>
		<div class="links">
			<span class="tagline"><?php echo esc_html( tamil_opt( 'tagline' ) ); ?></span>
			<span class="datum"><?php echo esc_html( tamil_heute() ); ?></span>
		</div>
		<?php get_template_part( 'template-parts/header/logo' ); ?>
		<button type="button" class="icon-btn suche-btn" id="suche-btn" aria-controls="suche" aria-label="<?php esc_attr_e( 'Suche öffnen', 'tamil' ); ?>"><?php tamil_icon( 'search' ); ?></button>
		<form class="suche" id="suche" role="search" method="get" action="<?php echo esc_url( home_url( '/' ) ); ?>">
			<label class="sr-only" for="q"><?php esc_html_e( 'Suche', 'tamil' ); ?></label>
			<input id="q" type="search" name="s" value="<?php echo esc_attr( get_search_query() ); ?>" placeholder="<?php esc_attr_e( 'Suchen …', 'tamil' ); ?>">
			<button type="submit" class="icon-btn" aria-label="<?php esc_attr_e( 'Suchen', 'tamil' ); ?>"><?php tamil_icon( 'search' ); ?></button>
		</form>
	</div>
</div>
