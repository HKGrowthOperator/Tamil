<?php
/**
 * Menü (Seitenpaneel): Rubriken, Seiten, Werben, Kontakt und Social. Öffnet über den Menüknopf im Kopf.
 */

defined( 'ABSPATH' ) || exit;

$items  = tamil_nav_items();
$seiten = array_filter(
	array(
		'events'     => __( 'Veranstaltungskalender', 'tamil' ),
		'production' => tamil_opt( 'production_titel' ),
		'tv'         => __( 'Tamil TV', 'tamil' ),
		'ueber-uns'  => __( 'Über Tamil.de', 'tamil' ),
		'kontakt'    => __( 'Kontakt', 'tamil' ),
	),
	static fn( $slug ) => null !== tamil_seite( (string) $slug ),
	ARRAY_FILTER_USE_KEY
);
$wa     = tamil_whatsapp_link();
?>
<div class="menue" id="menue" hidden>
	<div class="menue-paneel" role="dialog" aria-modal="true" aria-label="<?php esc_attr_e( 'Menü', 'tamil' ); ?>">
		<div class="menue-kopf">
			<?php get_template_part( 'template-parts/header/logo' ); ?>
			<button type="button" class="rund" data-close aria-label="<?php esc_attr_e( 'Menü schließen', 'tamil' ); ?>"><?php tamil_icon( 'close', 'ico ico-sm' ); ?></button>
		</div>
		<p class="menue-titel"><?php esc_html_e( 'Rubriken', 'tamil' ); ?></p>
		<ul class="menue-rubriken">
			<li><a href="<?php echo esc_url( home_url( '/' ) ); ?>"<?php echo is_front_page() ? ' aria-current="page"' : ''; ?>><?php esc_html_e( 'Startseite', 'tamil' ); ?></a></li>
			<?php foreach ( $items as $item ) : ?>
				<li><a class="<?php echo $item['slug'] ? 'rubrik r-' . esc_attr( $item['slug'] ) : ''; ?>" href="<?php echo esc_url( $item['url'] ); ?>"<?php echo $item['aktiv'] ? ' aria-current="page"' : ''; ?>><?php echo esc_html( $item['label'] ); ?></a></li>
			<?php endforeach; ?>
		</ul>
		<?php if ( $seiten ) : ?>
			<p class="menue-titel"><?php esc_html_e( 'Service', 'tamil' ); ?></p>
			<ul class="menue-seiten">
				<?php foreach ( $seiten as $slug => $label ) : ?>
					<li><a href="<?php echo esc_url( tamil_seiten_url( $slug ) ); ?>"<?php echo is_page( $slug ) ? ' aria-current="page"' : ''; ?>><?php echo esc_html( $label ); ?></a></li>
				<?php endforeach; ?>
				<li><a href="<?php echo esc_url( tamil_seiten_url( 'kontakt', 'werben' ) ); ?>"><?php esc_html_e( 'Werben auf Tamil.de', 'tamil' ); ?></a></li>
			</ul>
		<?php endif; ?>
		<div class="menue-fuss">
			<?php
			if ( $wa ) :
				?>
				<a class="knopf knopf-wa" href="<?php echo esc_url( $wa ); ?>" target="_blank" rel="noopener"><?php tamil_icon( 'whatsapp', 'ico ico-sm' ); ?> <?php esc_html_e( 'WhatsApp an die Redaktion', 'tamil' ); ?></a><?php endif; ?>
			<div class="social">
				<?php foreach ( tamil_social() as $s ) : ?>
					<a class="rund" href="<?php echo esc_url( $s['url'] ); ?>" aria-label="<?php echo esc_attr( $s['name'] ); ?>" target="_blank" rel="noopener"><?php tamil_icon( $s['icon'], 'ico ico-sm' ); ?></a>
				<?php endforeach; ?>
			</div>
		</div>
	</div>
</div>
