<?php
/**
 * Newsletter-Anmeldung: Shortcode eines Newsletter-Plugins, sonst Formular an die Adresse des Anbieters, sonst der
 * WhatsApp-Kanal als ehrlicher Ersatz (keine Attrappe, die nichts verschickt).
 *
 * @var array $args { id, button (CSS-Klasse), text }
 */

defined( 'ABSPATH' ) || exit;

$id        = $args['id'] ?? 'nl';
$button    = $args['button'] ?? 'btn-primary';
$text      = $args['text'] ?? '';
$shortcode = tamil_opt( 'newsletter_shortcode' );
$action    = tamil_opt( 'newsletter_action' );
$feld      = ( '' !== tamil_opt( 'newsletter_feld' ) ? tamil_opt( 'newsletter_feld' ) : 'email' );
$kanal     = tamil_opt( 'social_whatsapp' );

if ( $text ) {
	echo '<p class="klein">' . esc_html( $text ) . '</p>';
}
if ( '' !== $shortcode ) {
	echo do_shortcode( $shortcode ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Ausgabe des Newsletter-Plugins
	return;
}
if ( '' !== $action ) :
	?>
	<form class="nl-form" method="post" action="<?php echo esc_url( $action ); ?>" target="_blank">
		<label class="sr-only" for="<?php echo esc_attr( $id ); ?>"><?php esc_html_e( 'E-Mail-Adresse', 'tamil' ); ?></label>
		<input id="<?php echo esc_attr( $id ); ?>" type="email" name="<?php echo esc_attr( $feld ); ?>" placeholder="<?php esc_attr_e( 'deine@mail.de', 'tamil' ); ?>" required autocomplete="email">
		<button class="btn <?php echo esc_attr( $button ); ?>"><?php esc_html_e( 'Anmelden', 'tamil' ); ?></button>
		<p class="doi"><?php esc_html_e( 'Double-Opt-in: Du bestätigst die Anmeldung per E-Mail. Abmeldung jederzeit.', 'tamil' ); ?></p>
	</form>
	<?php
	return;
endif;
if ( '' !== $kanal ) :
	?>
	<p><a class="btn btn-wa" href="<?php echo esc_url( $kanal ); ?>" target="_blank" rel="noopener"><?php tamil_icon( 'whatsapp', 'ico ico-sm' ); ?> <?php esc_html_e( 'WhatsApp-Kanal folgen', 'tamil' ); ?></a></p>
	<?php
endif;
