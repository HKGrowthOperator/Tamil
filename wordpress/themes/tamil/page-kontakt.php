<?php
/**
 * Template Name: Kontakt
 *
 * Kontaktkarte, Kontaktformular (Shortcode aus dem Customizer), Werben auf Tamil.de, Event einreichen, Seiteninhalt.
 * Greift automatisch für die Seite mit dem Slug „kontakt“.
 */

defined( 'ABSPATH' ) || exit;

get_header();

$telefon  = tamil_opt( 'telefon' );
$email    = tamil_opt( 'email' );
$adresse  = array_filter( array_map( 'trim', explode( "\n", tamil_opt( 'adresse' ) ) ) );
$wa       = tamil_whatsapp_link();
$formular = tamil_opt( 'kontakt_formular' );
$event_f  = tamil_opt( 'event_formular' );
$formate  = array(
	array( '01', __( 'Leaderboard', 'tamil' ), '728 × 90 · mobil 320 × 50', __( 'Unter der Navigation, auf allen Seiten', 'tamil' ) ),
	array( '02', __( 'Half Page (Seitenspalte)', 'tamil' ), '300 × 600', __( 'Rechte Spalte, bleibt beim Scrollen stehen', 'tamil' ) ),
	array( '03', __( 'In-Article', 'tamil' ), '728 × 90 · mobil 300 × 250', __( 'Im Artikel nach dem zweiten Absatz; Startseite 970 × 250', 'tamil' ) ),
	array( '04', __( 'Footer', 'tamil' ), '728 × 90 · mobil 320 × 100', __( 'Über dem Footer, auf allen Seiten', 'tamil' ) ),
	array( '05', __( 'Mobile Sticky', 'tamil' ), 'mobil 320 × 50', __( 'Nur mobil, fixiert am unteren Rand, schließbar', 'tamil' ) ),
);
?>
<div class="container">
	<?php tamil_breadcrumb( array( array( get_the_title(), '' ) ) ); ?>
	<header class="seitenkopf">
		<h1><?php the_title(); ?> <span class="ta" lang="ta">தொடர்பு</span></h1>
		<p class="beschreibung"><?php esc_html_e( 'Redaktion, Werbung oder ein Event für den Kalender – hier erreicht ihr uns. Auf Deutsch, Tamil oder Englisch.', 'tamil' ); ?></p>
	</header>
	<div class="kontakt-grid">
		<div class="kontakt-karte">
			<h2 class="kicker"><span class="ta" lang="ta">ஆசிரியர் குழு</span><span class="de"><?php esc_html_e( 'Redaktion und Verlag', 'tamil' ); ?></span></h2>
			<?php
			if ( $telefon ) :
				?>
				<div class="zeile"><?php tamil_icon( 'phone' ); ?><div><strong><?php esc_html_e( 'Telefon', 'tamil' ); ?></strong><a href="tel:<?php echo esc_attr( preg_replace( '/[^\d+]/', '', $telefon ) ); ?>"><?php echo esc_html( $telefon ); ?></a></div></div><?php endif; ?>
			<?php
			if ( $email ) :
				?>
				<div class="zeile"><?php tamil_icon( 'mail' ); ?><div><strong><?php esc_html_e( 'E-Mail', 'tamil' ); ?></strong><a href="mailto:<?php echo esc_attr( antispambot( $email ) ); ?>"><?php echo esc_html( antispambot( $email ) ); ?></a></div></div><?php endif; ?>
			<?php
			if ( $wa ) :
				?>
				<div class="zeile"><?php tamil_icon( 'whatsapp' ); ?><div><strong>WhatsApp</strong><?php echo esc_html( tamil_opt( 'whatsapp' ) ); ?><br><a class="btn btn-wa btn-sm" href="<?php echo esc_url( $wa ); ?>" target="_blank" rel="noopener"><?php tamil_icon( 'whatsapp', 'ico ico-sm' ); ?> <?php esc_html_e( 'Nachricht schreiben', 'tamil' ); ?></a></div></div><?php endif; ?>
			<?php
			if ( $adresse ) :
				?>
				<div class="zeile"><?php tamil_icon( 'pin' ); ?><div><strong><?php esc_html_e( 'Anschrift', 'tamil' ); ?></strong><?php echo wp_kses( implode( '<br>', array_map( 'esc_html', $adresse ) ), array( 'br' => array() ) ); ?></div></div><?php endif; ?>
			<div class="zeile"><?php tamil_icon( 'clock' ); ?><div><strong><?php esc_html_e( 'Antwortzeit', 'tamil' ); ?></strong><?php echo esc_html( tamil_opt( 'antwortzeit' ) ); ?></div></div>
		</div>
		<div class="kontaktformular" id="kontaktformular">
			<h2 class="kicker"><span class="ta" lang="ta"></span><span class="de"><?php esc_html_e( 'Nachricht an die Redaktion', 'tamil' ); ?></span></h2>
			<?php if ( '' !== $formular ) : ?>
				<?php echo do_shortcode( $formular ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Formular-Plugin ?>
			<?php else : ?>
				<p><?php esc_html_e( 'Schreibt uns direkt – wir antworten so schnell wie möglich.', 'tamil' ); ?></p>
				<p class="aktionen">
					<?php
					if ( $email ) :
						?>
						<a class="btn btn-primary" href="mailto:<?php echo esc_attr( antispambot( $email ) ); ?>"><?php tamil_icon( 'mail', 'ico ico-sm' ); ?> <?php esc_html_e( 'E-Mail schreiben', 'tamil' ); ?></a><?php endif; ?>
					<?php
					if ( $wa ) :
						?>
						<a class="btn btn-wa" href="<?php echo esc_url( $wa ); ?>" target="_blank" rel="noopener"><?php tamil_icon( 'whatsapp', 'ico ico-sm' ); ?> WhatsApp</a><?php endif; ?>
				</p>
				<?php
				if ( current_user_can( 'edit_theme_options' ) ) :
					?>
					<p class="hinweis-box"><?php esc_html_e( 'Hinweis für die Redaktion: Im Customizer (Tamil.de → Kontakt und Formulare) den Shortcode eines Formular-Plugins eintragen, dann steht hier das Formular.', 'tamil' ); ?></p><?php endif; ?>
			<?php endif; ?>
		</div>
	</div>

	<section class="section" id="werben">
		<?php tamil_kicker( 'news', __( 'Werben auf Tamil.de', 'tamil' ), '', '', 'விளம்பரம்' ); ?>
		<p class="lesebreite"><?php esc_html_e( 'Fünf feste Werbeplätze, die auf jeder Seite an derselben Stelle stehen – Leserinnen und Leser wissen, wo Werbung steht, und Kunden wissen, was sie buchen. Formate nach IAB-Standard, monatlicher Bericht mit Einblendungen und Klicks.', 'tamil' ); ?></p>
		<div class="formate">
			<?php foreach ( $formate as [ $nr, $name, $masse, $position ] ) : ?>
				<div class="format"><span class="nr"><?php echo esc_html( $nr ); ?></span><div><h3><?php echo esc_html( $name ); ?></h3><p class="masse"><?php echo esc_html( $masse ); ?></p><p><?php echo esc_html( $position ); ?></p></div></div>
			<?php endforeach; ?>
			<div class="format sonder"><span class="nr">+</span><div><h3><?php esc_html_e( 'Sonderformate', 'tamil' ); ?></h3><p><?php esc_html_e( 'Advertorial, Newsletter-Platz, Event-Partnerschaft – auf Anfrage.', 'tamil' ); ?></p></div></div>
		</div>
		<?php
		if ( $email ) :
			?>
			<p class="aktionen"><a class="btn btn-gold" href="mailto:<?php echo esc_attr( antispambot( $email ) ); ?>?subject=<?php echo rawurlencode( __( 'Werbeanfrage', 'tamil' ) ); ?>"><?php esc_html_e( 'Werbeanfrage stellen', 'tamil' ); ?></a></p><?php endif; ?>
	</section>

	<section class="section" id="event-einreichen">
		<?php tamil_kicker( 'events', __( 'Event einreichen', 'tamil' ) ); ?>
		<p class="lesebreite"><?php esc_html_e( 'Kostenlos für Vereine, Tempel, Schulen und Veranstalter. Die Redaktion prüft jede Einreichung; freigegebene Events erscheinen im Kalender, im Newsletter und – wenn es passt – als Beitrag.', 'tamil' ); ?></p>
		<?php if ( '' !== $event_f ) : ?>
			<div class="formular-wrap"><?php echo do_shortcode( $event_f ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Formular-Plugin ?></div>
		<?php else : ?>
			<p class="aktionen">
				<?php
				if ( $wa ) :
					?>
					<a class="btn btn-wa" href="<?php echo esc_url( tamil_whatsapp_link( __( 'Hallo Tamil.de, ich möchte ein Event melden: ', 'tamil' ) ) ); ?>" target="_blank" rel="noopener"><?php tamil_icon( 'whatsapp', 'ico ico-sm' ); ?> <?php esc_html_e( 'Per WhatsApp melden', 'tamil' ); ?></a><?php endif; ?>
				<?php
				if ( $email ) :
					?>
					<a class="btn btn-ghost" href="mailto:<?php echo esc_attr( antispambot( $email ) ); ?>?subject=<?php echo rawurlencode( __( 'Event einreichen', 'tamil' ) ); ?>"><?php esc_html_e( 'Per E-Mail schicken', 'tamil' ); ?></a><?php endif; ?>
			</p>
		<?php endif; ?>
	</section>

	<?php
	while ( have_posts() ) :
		the_post();
		?>
		<?php if ( '' !== trim( (string) get_the_content() ) ) : ?>
			<section class="section lesebreite"><div class="artikel-body"><?php the_content(); ?></div></section>
		<?php endif; ?>
	<?php endwhile; ?>
</div>
<?php
get_footer();
