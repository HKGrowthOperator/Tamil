<?php
/**
 * Template Name: Kontakt
 *
 * Kontakt in klar2: die Formulare des Plugins tamil-site („Nachricht an die Redaktion“, „Termin einreichen“,
 * „Kooperation“, jeweils mit Danke-Anzeige nach dem Absenden), daneben die Redaktionsdaten (nur, wenn sie im
 * Customizer stehen) und andere Wege; darunter die Werbeplätze aus dem Plugin mit Preis „auf Anfrage“. Der alte
 * Seiteninhalt (Leser-Reporter, Bildschirmfotos von 2017) wird nicht mehr gezeigt. Ohne Plugin oder mit
 * ausgeschaltetem Baustein „Einreichungen“ bleiben E-Mail und WhatsApp (falls gesetzt) bzw. Formulare aus dem
 * Customizer. Greift automatisch für die Seite mit dem Slug „kontakt“.
 */

defined( 'ABSPATH' ) || exit;

get_header();

$tamil_telefon   = tamil_opt( 'telefon' );
$tamil_email     = tamil_opt( 'email' );
$tamil_adresse   = array_filter( array_map( 'trim', explode( "\n", tamil_opt( 'adresse' ) ) ) );
$tamil_wa        = tamil_whatsapp_link();
$tamil_formulare = shortcode_exists( 'tamil_einsendung' ) && function_exists( 'tamil_site_funktion_an' ) && tamil_site_funktion_an( 'einreichungen' );
$tamil_angaben   = array_filter(
	array(
		__( 'Telefon', 'tamil' )   => $tamil_telefon ? '<a href="tel:' . esc_attr( preg_replace( '/[^\d+]/', '', $tamil_telefon ) ) . '">' . esc_html( $tamil_telefon ) . '</a>' : '',
		__( 'E-Mail', 'tamil' )    => $tamil_email ? '<a href="mailto:' . esc_attr( antispambot( $tamil_email ) ) . '">' . esc_html( antispambot( $tamil_email ) ) . '</a>' : '',
		__( 'WhatsApp', 'tamil' )  => $tamil_wa ? '<a href="' . esc_url( $tamil_wa ) . '" target="_blank" rel="noopener">' . esc_html( tamil_opt( 'whatsapp' ) ) . '</a>' : '',
		__( 'Anschrift', 'tamil' ) => $tamil_adresse ? implode( '<br>', array_map( 'esc_html', $tamil_adresse ) ) : '',
	)
);
$tamil_erlaubt   = array(
	'a'  => array(
		'href'   => array(),
		'target' => array(),
		'rel'    => array(),
	),
	'br' => array(),
);
$tamil_bloecke   = array(
	'kontakt'     => array( 'kontaktformular', __( 'Nachricht an die Redaktion', 'tamil' ), __( 'Fragen, Hinweise, Korrekturen oder ein Thema für die Redaktion. Wir antworten so schnell wie möglich.', 'tamil' ), tamil_opt( 'kontakt_formular' ) ),
	'event'       => array( 'event-einreichen', __( 'Termin einreichen', 'tamil' ), __( 'Kostenlos für Vereine, Tempel, Schulen und Veranstalter. Die Redaktion prüft jede Einreichung; freigegebene Termine erscheinen im Kalender.', 'tamil' ), tamil_opt( 'event_formular' ) ),
	'kooperation' => array( 'kooperation', __( 'Kooperation', 'tamil' ), __( 'Für Vereine, Veranstalter und Unternehmen, die mit Tamil.de zusammenarbeiten möchten.', 'tamil' ), '' ),
);
$tamil_formate   = function_exists( 'tamil_site_werbung_formate' ) ? tamil_site_werbung_formate() : array();
$tamil_masse     = static function ( array $f ): string {
	$desktop = $f['desktop'][0] . ' × ' . $f['desktop'][1];
	/* translators: 1: Maße Desktop, 2: Maße Handy */
	return $f['desktop'] === $f['mobil'] ? $desktop : sprintf( __( '%1$s, mobil %2$s', 'tamil' ), $desktop, $f['mobil'][0] . ' × ' . $f['mobil'][1] );
};
?>
<div class="innen">
	<header class="seitenkopf">
		<h1 class="seitenkopf__titel"><?php the_title(); ?></h1>
		<p class="seitenkopf__zeile"><?php esc_html_e( 'Redaktion, Werbung oder ein Termin für den Kalender: hier erreicht ihr uns. Auf Deutsch, Tamil oder Englisch.', 'tamil' ); ?></p>
	</header>

	<div class="kontakt">
		<div class="kontakt__formulare">
			<?php foreach ( $tamil_bloecke as $tamil_art => [ $tamil_anker, $tamil_titel, $tamil_satz, $tamil_eigen ] ) : ?>
				<?php
				if ( ! $tamil_formulare && '' === $tamil_eigen && 'kooperation' === $tamil_art ) {
					continue; // ohne Formular reicht der Weg über Nachricht und Termin
				}
				?>
				<section class="kontakt__formular" id="<?php echo esc_attr( $tamil_anker ); ?>" aria-labelledby="<?php echo esc_attr( 't-' . $tamil_anker ); ?>">
					<h2 class="block-titel" id="<?php echo esc_attr( 't-' . $tamil_anker ); ?>"><?php echo esc_html( $tamil_titel ); ?></h2>
					<p class="block__zeile"><?php echo esc_html( $tamil_satz ); ?></p>
					<?php if ( $tamil_formulare ) : ?>
						<div class="formular-wrap"><?php echo do_shortcode( '[tamil_einsendung art="' . esc_attr( $tamil_art ) . '"]' ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Formular des Plugins, dort escapt ?></div>
					<?php elseif ( '' !== $tamil_eigen ) : ?>
						<div class="formular-wrap"><?php echo do_shortcode( $tamil_eigen ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Formular-Plugin ?></div>
					<?php elseif ( $tamil_email || $tamil_wa ) : ?>
						<p class="knoepfe">
							<?php if ( $tamil_email ) : ?>
								<a class="knopf" href="mailto:<?php echo esc_attr( antispambot( $tamil_email ) ); ?>?subject=<?php echo rawurlencode( $tamil_titel ); ?>"><?php esc_html_e( 'E-Mail schreiben', 'tamil' ); ?></a>
							<?php endif; ?>
							<?php if ( $tamil_wa ) : ?>
								<a class="knopf knopf-leise" href="<?php echo esc_url( $tamil_wa ); ?>" target="_blank" rel="noopener"><?php esc_html_e( 'Per WhatsApp schreiben', 'tamil' ); ?></a>
							<?php endif; ?>
						</p>
					<?php elseif ( current_user_can( 'edit_theme_options' ) ) : ?>
						<p class="hinweis-box"><?php esc_html_e( 'Hinweis für die Redaktion: Den Baustein „Einreichungen“ einschalten (Tamil.de Website) oder im Customizer E-Mail bzw. ein Formular eintragen.', 'tamil' ); ?></p>
					<?php endif; ?>
				</section>
			<?php endforeach; ?>
			<?php if ( '' !== tamil_opt( 'antwortzeit' ) ) : ?>
				<p class="block__notiz"><?php echo esc_html( tamil_opt( 'antwortzeit' ) ); ?></p>
			<?php endif; ?>
		</div>
		<aside class="kontakt__daten" aria-label="<?php esc_attr_e( 'Redaktion und andere Wege', 'tamil' ); ?>">
			<?php if ( $tamil_angaben ) : ?>
				<h2 class="block-titel"><?php esc_html_e( 'Redaktion und Verlag', 'tamil' ); ?></h2>
				<dl class="angaben">
					<?php foreach ( $tamil_angaben as $tamil_label => $tamil_wert ) : ?>
						<div><dt><?php echo esc_html( $tamil_label ); ?></dt><dd><?php echo wp_kses( $tamil_wert, $tamil_erlaubt ); ?></dd></div>
					<?php endforeach; ?>
				</dl>
			<?php endif; ?>
			<h2 class="block-titel<?php echo $tamil_angaben ? ' kontakt__wege-titel' : ''; ?>"><?php esc_html_e( 'Andere Wege', 'tamil' ); ?></h2>
			<ul class="wege">
				<?php foreach ( tamil_dienste() as $tamil_d ) : ?>
					<?php if ( ! $tamil_d['aktiv'] ) : ?>
						<li><a href="<?php echo esc_url( $tamil_d['url'] ); ?>"><?php echo esc_html( $tamil_d['label'] ); ?></a></li>
					<?php endif; ?>
				<?php endforeach; ?>
			</ul>
		</aside>
	</div>
	<?php tamil_leaderboard( 'anzeige-zwischen' ); ?>

	<?php if ( $tamil_formate ) : ?>
		<section class="block" id="werben" aria-labelledby="werben-titel">
			<div class="block-kopf">
				<h2 class="block-titel" id="werben-titel"><?php esc_html_e( 'Werben auf Tamil.de', 'tamil' ); ?></h2>
				<?php if ( tamil_seite( 'werben' ) ) : ?>
					<a class="textlink" href="<?php echo esc_url( tamil_seiten_url( 'werben' ) ); ?>"><?php esc_html_e( 'Werbeplatz buchen', 'tamil' ); ?></a>
				<?php endif; ?>
			</div>
			<?php /* translators: %d: Anzahl der Werbeplätze */ ?>
			<p class="block__zeile"><?php echo esc_html( sprintf( __( '%d feste Werbeplätze, die auf jeder Seite an derselben Stelle stehen: Leserinnen und Leser wissen, wo Werbung steht, und Kunden wissen, was sie buchen.', 'tamil' ), count( $tamil_formate ) ) ); ?></p>
			<div class="tafel-wrap">
				<table class="tafel plaetze">
					<thead><tr><th scope="col"><?php esc_html_e( 'Platz', 'tamil' ); ?></th><th scope="col"><?php esc_html_e( 'Format', 'tamil' ); ?></th><th scope="col"><?php esc_html_e( 'Wo', 'tamil' ); ?></th><th scope="col"><?php esc_html_e( 'Preis', 'tamil' ); ?></th></tr></thead>
					<tbody>
						<?php foreach ( $tamil_formate as $tamil_f ) : ?>
							<tr>
								<th scope="row"><?php echo esc_html( $tamil_f['name'] ); ?></th>
								<td class="masse"><?php echo esc_html( $tamil_masse( $tamil_f ) ); ?></td>
								<td><?php echo esc_html( ucfirst( $tamil_f['wo'] ) ); ?></td>
								<td class="preis"><?php esc_html_e( 'auf Anfrage', 'tamil' ); ?></td>
							</tr>
						<?php endforeach; ?>
					</tbody>
				</table>
			</div>
			<p class="aktionen">
				<?php if ( tamil_seite( 'werben' ) ) : ?>
					<a class="textlink" href="<?php echo esc_url( tamil_seiten_url( 'werben' ) ); ?>"><?php esc_html_e( 'Alles zu Werbeplätzen und Buchung', 'tamil' ); ?></a>
				<?php endif; ?>
				<?php if ( $tamil_email ) : ?>
					<a class="textlink" href="mailto:<?php echo esc_attr( antispambot( $tamil_email ) ); ?>?subject=<?php echo rawurlencode( __( 'Werbeanfrage', 'tamil' ) ); ?>"><?php esc_html_e( 'Werbeanfrage per E-Mail', 'tamil' ); ?></a>
				<?php endif; ?>
			</p>
		</section>
	<?php endif; ?>
</div>
<?php
get_footer();
