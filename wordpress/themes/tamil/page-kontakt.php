<?php
/**
 * Template Name: Kontakt
 *
 * Kontakt: Nachricht an die Redaktion (Formular-Shortcode aus dem Customizer oder E-Mail/WhatsApp), rechts die
 * Redaktionsdaten (nur, wenn sie im Customizer stehen) und andere Wege; darunter Werben, Event einreichen und der
 * Seiteninhalt. Greift automatisch für die Seite mit dem Slug „kontakt“.
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
	array( __( 'Leaderboard', 'tamil' ), '728 × 90, mobil 320 × 50', __( 'Unter der Navigation, auf allen Seiten', 'tamil' ) ),
	array( __( 'Half Page', 'tamil' ), '300 × 600', __( 'Rechts neben dem Artikeltext', 'tamil' ) ),
	array( __( 'In-Article', 'tamil' ), '728 × 90, schmal 300 × 250', __( 'Im Artikel nach dem zweiten Absatz; Startseite 970 × 250', 'tamil' ) ),
	array( __( 'Footer', 'tamil' ), '728 × 90, mobil 320 × 100', __( 'Über dem Fuß, auf allen Seiten', 'tamil' ) ),
	array( __( 'Mobile Sticky', 'tamil' ), 'mobil 320 × 50', __( 'Nur am Handy, unten fest, schließbar', 'tamil' ) ),
);
$angaben  = array_filter(
	array(
		__( 'Telefon', 'tamil' )     => $telefon ? '<a href="tel:' . esc_attr( preg_replace( '/[^\d+]/', '', $telefon ) ) . '">' . esc_html( $telefon ) . '</a>' : '',
		__( 'E-Mail', 'tamil' )      => $email ? '<a href="mailto:' . esc_attr( antispambot( $email ) ) . '">' . esc_html( antispambot( $email ) ) . '</a>' : '',
		__( 'WhatsApp', 'tamil' )    => $wa ? '<a href="' . esc_url( $wa ) . '" target="_blank" rel="noopener">' . esc_html( tamil_opt( 'whatsapp' ) ) . '</a>' : '',
		__( 'Anschrift', 'tamil' )   => $adresse ? implode( '<br>', array_map( 'esc_html', $adresse ) ) : '',
		__( 'Antwortzeit', 'tamil' ) => esc_html( tamil_opt( 'antwortzeit' ) ),
	)
);
$erlaubt  = array(
	'a'  => array(
		'href'   => array(),
		'target' => array(),
		'rel'    => array(),
	),
	'br' => array(),
);
?>
<header class="seitenkopf">
	<div class="wrap">
		<h1><?php the_title(); ?></h1>
		<p class="satz"><?php esc_html_e( 'Redaktion, Werbung oder ein Termin für den Kalender: hier erreicht ihr uns. Auf Deutsch, Tamil oder Englisch.', 'tamil' ); ?></p>
	</div>
</header>

<section class="abschnitt">
	<div class="wrap form-raster">
		<div class="kontaktformular" id="kontaktformular">
			<h2 class="strom-kopf"><?php esc_html_e( 'Nachricht an die Redaktion', 'tamil' ); ?></h2>
			<?php if ( '' !== $formular ) : ?>
				<?php echo do_shortcode( $formular ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Formular-Plugin ?>
			<?php else : ?>
				<p class="satz"><?php esc_html_e( 'Schreibt uns direkt, wir antworten so schnell wie möglich.', 'tamil' ); ?></p>
				<p class="aktionen">
					<?php
					if ( $email ) :
						?>
						<a class="knopf" href="mailto:<?php echo esc_attr( antispambot( $email ) ); ?>"><?php esc_html_e( 'E-Mail schreiben', 'tamil' ); ?></a><?php endif; ?>
					<?php
					if ( $wa ) :
						?>
						<a class="knopf knopf-leise" href="<?php echo esc_url( $wa ); ?>" target="_blank" rel="noopener"><?php esc_html_e( 'Per WhatsApp schreiben', 'tamil' ); ?></a><?php endif; ?>
				</p>
				<?php
				if ( current_user_can( 'edit_theme_options' ) ) :
					?>
					<p class="hinweis-box"><?php esc_html_e( 'Hinweis für die Redaktion: Im Customizer (Tamil.de, Kontakt und Formulare) den Shortcode eines Formulars eintragen, dann steht hier das Formular.', 'tamil' ); ?></p><?php endif; ?>
			<?php endif; ?>
		</div>
		<aside class="ablauf" aria-labelledby="redaktion-titel">
			<h2 id="redaktion-titel"><?php esc_html_e( 'Redaktion und Verlag', 'tamil' ); ?></h2>
			<dl class="angaben">
				<?php foreach ( $angaben as $label => $wert ) : ?>
					<div><dt><?php echo esc_html( $label ); ?></dt><dd><?php echo wp_kses( $wert, $erlaubt ); ?></dd></div>
				<?php endforeach; ?>
			</dl>
			<h2><?php esc_html_e( 'Andere Wege', 'tamil' ); ?></h2>
			<ul class="wege">
				<?php foreach ( tamil_dienste() as $d ) : ?>
					<?php if ( ! is_page( 'kontakt' ) || ! $d['aktiv'] ) : ?>
						<li><a href="<?php echo esc_url( $d['url'] ); ?>"><?php echo esc_html( $d['label'] ); ?></a></li>
					<?php endif; ?>
				<?php endforeach; ?>
			</ul>
		</aside>
	</div>
</section>
<?php tamil_leaderboard(); ?>

<section class="abschnitt" id="werben" aria-labelledby="werben-titel">
	<div class="wrap schmal">
		<div class="kopfzeile">
			<h2 id="werben-titel"><?php esc_html_e( 'Werben auf Tamil.de', 'tamil' ); ?></h2>
			<?php
			if ( tamil_seite( 'werben' ) ) :
				?>
				<a class="mehr" href="<?php echo esc_url( tamil_seiten_url( 'werben' ) ); ?>"><?php esc_html_e( 'Werbeplatz buchen', 'tamil' ); ?></a><?php endif; ?>
		</div>
		<p class="satz"><?php esc_html_e( 'Fünf feste Werbeplätze, die auf jeder Seite an derselben Stelle stehen: Leserinnen und Leser wissen, wo Werbung steht, und Kunden wissen, was sie buchen.', 'tamil' ); ?></p>
		<section class="bogen" aria-label="<?php esc_attr_e( 'Werbeplätze', 'tamil' ); ?>">
			<table class="tafel plaetze">
				<thead><tr><th scope="col"><?php esc_html_e( 'Platz', 'tamil' ); ?></th><th scope="col"><?php esc_html_e( 'Format', 'tamil' ); ?></th><th scope="col"><?php esc_html_e( 'Wo', 'tamil' ); ?></th></tr></thead>
				<tbody>
					<?php foreach ( $formate as [ $name, $masse, $wo ] ) : ?>
						<tr><th scope="row" class="was"><?php echo esc_html( $name ); ?></th><td class="masse"><?php echo esc_html( $masse ); ?></td><td class="wo"><?php echo esc_html( $wo ); ?></td></tr>
					<?php endforeach; ?>
				</tbody>
			</table>
			<?php
			if ( $email ) :
				?>
				<p class="bogen-fuss"><a class="textlink" href="mailto:<?php echo esc_attr( antispambot( $email ) ); ?>?subject=<?php echo rawurlencode( __( 'Werbeanfrage', 'tamil' ) ); ?>"><?php esc_html_e( 'Werbeanfrage stellen', 'tamil' ); ?></a></p><?php endif; ?>
		</section>
	</div>
</section>

<section class="abschnitt" id="event-einreichen" aria-labelledby="einreichen-titel">
	<div class="wrap schmal">
		<div class="kopfzeile"><h2 id="einreichen-titel"><?php esc_html_e( 'Termin einreichen', 'tamil' ); ?></h2></div>
		<p class="satz"><?php esc_html_e( 'Kostenlos für Vereine, Tempel, Schulen und Veranstalter. Die Redaktion prüft jede Einreichung; freigegebene Termine erscheinen im Festkalender.', 'tamil' ); ?></p>
		<?php if ( '' !== $event_f ) : ?>
			<div class="formular-wrap"><?php echo do_shortcode( $event_f ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Formular-Plugin ?></div>
		<?php else : ?>
			<p class="aktionen">
				<?php
				if ( $wa ) :
					?>
					<a class="knopf" href="<?php echo esc_url( tamil_whatsapp_link( __( 'Hallo Tamil.de, ich möchte einen Termin melden: ', 'tamil' ) ) ); ?>" target="_blank" rel="noopener"><?php esc_html_e( 'Per WhatsApp melden', 'tamil' ); ?></a><?php endif; ?>
				<?php
				if ( $email ) :
					?>
					<a class="knopf knopf-leise" href="mailto:<?php echo esc_attr( antispambot( $email ) ); ?>?subject=<?php echo rawurlencode( __( 'Termin einreichen', 'tamil' ) ); ?>"><?php esc_html_e( 'Per E-Mail schicken', 'tamil' ); ?></a><?php endif; ?>
			</p>
		<?php endif; ?>
	</div>
</section>

<?php
while ( have_posts() ) :
	the_post();
	if ( '' !== trim( (string) get_the_content() ) ) :
		?>
		<section class="abschnitt"><div class="wrap schmal"><div class="inhalt"><?php the_content(); ?></div></div></section>
		<?php
	endif;
endwhile;

get_footer();
