<?php
/**
 * Logo: Custom Logo aus dem Customizer, sonst das Logo des Themes – das neue Logo von Luis (20.11.2026), aus
 * design/inhalte/logo-2026-11.webp unverändert freigestellt (design/inhalte/logo_freistellen.py): WebP 1x und 2x mit
 * durchsichtigem Grund. Alternativtext „tamil.de“.
 *
 * @var array $args { @type string $class CSS-Klasse des Links. }
 */

defined( 'ABSPATH' ) || exit;

$tamil_klasse = $args['class'] ?? 'kopf__logo';
$tamil_logo   = (int) get_theme_mod( 'custom_logo' );
?>
<a class="<?php echo esc_attr( $tamil_klasse ); ?>" href="<?php echo esc_url( home_url( '/' ) ); ?>" rel="home">
	<?php
	if ( $tamil_logo ) {
		echo wp_get_attachment_image( $tamil_logo, 'medium', false, array( 'alt' => 'tamil.de' ) );
	} else {
		$tamil_mass = wp_getimagesize( TAMIL_THEME_DIR . '/assets/img/logo.webp' );
		printf(
			'<img src="%1$s" srcset="%1$s 1x, %2$s 2x" width="%3$d" height="%4$d" alt="tamil.de">',
			esc_url( TAMIL_THEME_URI . '/assets/img/logo.webp' ),
			esc_url( TAMIL_THEME_URI . '/assets/img/logo-2x.webp' ),
			(int) ( $tamil_mass[0] ?? 199 ),
			(int) ( $tamil_mass[1] ?? 72 )
		);
	}
	?>
</a>
