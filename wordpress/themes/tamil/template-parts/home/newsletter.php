<?php
/**
 * Newsletter-Band am Ende der Startseite.
 */

defined( 'ABSPATH' ) || exit;
?>
<section class="section nl-band" id="newsletter">
	<div class="container newsletter nl-schmal">
		<h2 class="kicker"><span class="ta" lang="ta">செய்திமடல்</span><span class="de"><?php esc_html_e( 'Newsletter', 'tamil' ); ?></span></h2>
		<h2 class="gross"><?php esc_html_e( 'Das Wichtigste der Woche. Einmal, nicht zehnmal.', 'tamil' ); ?></h2>
		<p><?php esc_html_e( 'Nachrichten, Kinostarts und Events für DE, AT und CH. Jeden Freitag, kostenlos, jederzeit abbestellbar.', 'tamil' ); ?></p>
		<?php
		get_template_part(
			'template-parts/newsletter-form',
			null,
			array(
				'id'     => 'nl-home',
				'button' => 'btn-gold',
			)
		);
		?>
	</div>
</section>
