<?php
/**
 * Hauptnavigation (ab Tablet) und mobiles Menü (Drawer).
 */

defined( 'ABSPATH' ) || exit;

$items  = tamil_nav_items();
$werben = tamil_seiten_url( 'kontakt', 'werben' );
$wa     = tamil_whatsapp_link();
$extra  = array_filter(
	array(
		array( 'production', tamil_opt( 'production_titel' ), 'நிகழ்ச்சிகள்' ),
		array( 'tv', __( 'Tamil TV', 'tamil' ), 'தொலைக்காட்சி' ),
	),
	static fn( $e ) => null !== tamil_seite( $e[0] )
);
?>
<nav class="mainnav" aria-label="<?php esc_attr_e( 'Hauptnavigation', 'tamil' ); ?>">
	<div class="container">
		<ul>
			<?php foreach ( $items as $item ) : ?>
				<li><a href="<?php echo esc_url( $item['url'] ); ?>"<?php echo $item['aktiv'] ? ' aria-current="page"' : ''; ?>><?php echo esc_html( $item['label'] ); ?></a></li>
			<?php endforeach; ?>
		</ul>
		<a class="btn btn-gold btn-sm" href="<?php echo esc_url( $werben ); ?>"><?php esc_html_e( 'Werben', 'tamil' ); ?></a>
	</div>
</nav>
<div class="drawer" id="drawer" hidden>
	<div class="panel" role="dialog" aria-modal="true" aria-label="<?php esc_attr_e( 'Menü', 'tamil' ); ?>">
		<div class="kopf">
			<?php get_template_part( 'template-parts/header/logo' ); ?>
			<button type="button" class="icon-btn" data-close aria-label="<?php esc_attr_e( 'Menü schließen', 'tamil' ); ?>"><?php tamil_icon( 'close' ); ?></button>
		</div>
		<ul>
			<li><a href="<?php echo esc_url( home_url( '/' ) ); ?>"<?php echo is_front_page() ? ' aria-current="page"' : ''; ?>><?php esc_html_e( 'Startseite', 'tamil' ); ?></a></li>
			<?php foreach ( $items as $item ) : ?>
				<li><a href="<?php echo esc_url( $item['url'] ); ?>"<?php echo $item['aktiv'] ? ' aria-current="page"' : ''; ?>><?php echo esc_html( $item['label'] ); ?>
				<?php
				if ( $item['tamil'] ) :
					?>
					<span class="ta" lang="ta"><?php echo esc_html( $item['tamil'] ); ?></span><?php endif; ?></a></li>
			<?php endforeach; ?>
			<?php foreach ( $extra as [ $slug, $label, $tamil ] ) : ?>
				<li><a href="<?php echo esc_url( tamil_seiten_url( $slug ) ); ?>"<?php echo is_page( $slug ) ? ' aria-current="page"' : ''; ?>><?php echo esc_html( $label ); ?><span class="ta" lang="ta"><?php echo esc_html( $tamil ); ?></span></a></li>
			<?php endforeach; ?>
			<li><a href="<?php echo esc_url( $werben ); ?>"><?php esc_html_e( 'Werben auf Tamil.de', 'tamil' ); ?><span class="ta" lang="ta">விளம்பரம்</span></a></li>
		</ul>
		<div class="kontakt-zeile">
			<?php
			if ( tamil_opt( 'telefon' ) ) :
				?>
				<span><?php echo esc_html( tamil_opt( 'telefon' ) ); ?></span><?php endif; ?>
			<?php
			if ( tamil_opt( 'email' ) ) :
				?>
				<span><?php echo esc_html( antispambot( tamil_opt( 'email' ) ) ); ?></span><?php endif; ?>
			<?php
			if ( $wa ) :
				?>
				<a class="btn btn-wa btn-sm" href="<?php echo esc_url( $wa ); ?>" target="_blank" rel="noopener"><?php tamil_icon( 'whatsapp', 'ico ico-sm' ); ?> WhatsApp</a><?php endif; ?>
		</div>
	</div>
</div>
