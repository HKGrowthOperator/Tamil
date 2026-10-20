<?php
/**
 * Logo: Custom Logo aus dem Customizer, sonst das Logo des Themes, sonst die Wortmarke.
 *
 * @var array $args { @type string $class CSS-Klasse des Links. }
 */

defined( 'ABSPATH' ) || exit;

$class = $args['class'] ?? 'logo-wrap';
$logo  = (int) get_theme_mod( 'custom_logo' );
?>
<a class="<?php echo esc_attr( $class ); ?>" href="<?php echo esc_url( home_url( '/' ) ); ?>" aria-label="<?php echo esc_attr( get_bloginfo( 'name' ) . ' – ' . __( 'Startseite', 'tamil' ) ); ?>" rel="home">
	<?php
	if ( $logo ) {
		echo wp_get_attachment_image( $logo, 'medium', false, array( 'alt' => get_bloginfo( 'name' ) ) );
	} else {
		printf( '<img src="%s" alt="%s" width="300" height="121">', esc_url( TAMIL_THEME_URI . '/assets/img/logo.png' ), esc_attr( get_bloginfo( 'name' ) ) );
	}
	?>
</a>
