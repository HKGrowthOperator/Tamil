<?php
/**
 * Topbar: Telefon, E-Mail, WhatsApp (nur wenn eingetragen), Social, „Werben“.
 */

defined( 'ABSPATH' ) || exit;

$telefon = tamil_opt( 'telefon' );
$email   = tamil_opt( 'email' );
$wa      = tamil_whatsapp_link();
?>
<div class="topbar">
	<div class="container">
		<div class="kontakt">
			<?php if ( $telefon ) : ?>
				<a href="tel:<?php echo esc_attr( preg_replace( '/[^\d+]/', '', $telefon ) ); ?>"><?php tamil_icon( 'phone', 'ico ico-sm' ); ?><span class="label"><?php echo esc_html( $telefon ); ?></span></a>
			<?php endif; ?>
			<?php if ( $email ) : ?>
				<a href="mailto:<?php echo esc_attr( antispambot( $email ) ); ?>"><?php tamil_icon( 'mail', 'ico ico-sm' ); ?><span class="label"><?php echo esc_html( antispambot( $email ) ); ?></span></a>
			<?php endif; ?>
			<?php if ( $wa ) : ?>
				<a class="wa" href="<?php echo esc_url( $wa ); ?>" target="_blank" rel="noopener"><?php tamil_icon( 'whatsapp', 'ico ico-sm' ); ?><span class="label">WhatsApp</span></a>
			<?php endif; ?>
		</div>
		<div class="social">
			<?php foreach ( tamil_social() as $s ) : ?>
				<a href="<?php echo esc_url( $s['url'] ); ?>" aria-label="<?php echo esc_attr( $s['name'] ); ?>" target="_blank" rel="noopener"><?php tamil_icon( $s['icon'], 'ico ico-sm' ); ?></a>
			<?php endforeach; ?>
			<a class="werben" href="<?php echo esc_url( tamil_seiten_url( 'kontakt', 'werben' ) ); ?>"><?php esc_html_e( 'Werben', 'tamil' ); ?></a>
		</div>
	</div>
</div>
