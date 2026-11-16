<?php
/**
 * Logo: Custom Logo aus dem Customizer, sonst das Logo des Themes (300 × 121 px, unverändert).
 *
 * @var array $args { @type string $class CSS-Klasse des Links. }
 */

defined( 'ABSPATH' ) || exit;

$tamil_klasse = $args['class'] ?? 'kopf__logo';
$tamil_logo   = (int) get_theme_mod( 'custom_logo' );
$tamil_name   = get_bloginfo( 'name' );
?>
<a class="<?php echo esc_attr( $tamil_klasse ); ?>" href="<?php echo esc_url( home_url( '/' ) ); ?>" rel="home">
	<?php
	if ( $tamil_logo ) {
		echo wp_get_attachment_image( $tamil_logo, 'medium', false, array( 'alt' => sprintf( /* translators: %s: Name der Website */ __( '%s, zur Startseite', 'tamil' ), $tamil_name ) ) );
	} else {
		/* translators: %s: Name der Website */
		printf( '<img src="%s" width="300" height="121" alt="%s">', esc_url( TAMIL_THEME_URI . '/assets/img/logo.png' ), esc_attr( sprintf( __( '%s, zur Startseite', 'tamil' ), $tamil_name ) ) );
	}
	?>
</a>
