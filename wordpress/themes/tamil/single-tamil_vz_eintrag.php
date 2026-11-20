<?php
/**
 * Profil eines Verzeichniseintrags (Plugin tamil-site, Baustein Verzeichnis) in klar2: Dachzeile „Art, Kategorie,
 * Stadt“, Name, Bild mit Nachweis, darunter das Profil des Plugins (Beschreibung, Angaben, „Änderung melden“) und die
 * Adresse mit Link zur Karte (OpenStreetMap, kein eingebetteter Dienst). Ohne Lesezeit, Teilen-Leiste und Vorspann:
 * ein Profil ist kein Artikel. Hat der Eintrag kein eigenes Bild, zeigt das Profil des Plugins sein Ersatzbild.
 */

defined( 'ABSPATH' ) || exit;

get_header();

while ( have_posts() ) :
	the_post();
	$tamil_id    = (int) get_the_ID();
	$tamil_werte = function_exists( 'tamil_site_vz_eintrag_werte' ) ? (array) tamil_site_vz_eintrag_werte( $tamil_id ) : array();
	$tamil_info  = function_exists( 'tamil_site_vz_kurzinfo' ) ? tamil_site_vz_kurzinfo( $tamil_id ) : '';
	$tamil_eigen = 'eigen' === tamil_bildwahl( $tamil_id )['art'];
	$tamil_ort   = trim( ( $tamil_werte['plz'] ?? '' ) . ' ' . ( $tamil_werte['stadt'] ?? '' ) );
	$tamil_karte = implode( ', ', array_filter( array( (string) ( $tamil_werte['adresse'] ?? '' ), $tamil_ort, (string) ( function_exists( 'tamil_site_vz_laender' ) ? ( tamil_site_vz_laender()[ $tamil_werte['land'] ?? '' ] ?? '' ) : '' ) ) ) );
	$tamil_liste = function_exists( 'tamil_site_vz_seite_url' ) ? tamil_site_vz_seite_url() : home_url( '/verzeichnis/' );
	$tamil_beisp = '' !== (string) get_post_meta( $tamil_id, '_tamil_vz_beispiel', true );
	?>
	<article <?php post_class( 'artikel vz-artikel' ); ?>>
		<header class="artikel__kopf">
			<p class="meta">
				<span class="meta__rubrik"><a href="<?php echo esc_url( $tamil_liste ); ?>"><?php esc_html_e( 'Verzeichnis', 'tamil' ); ?></a></span>
				<?php if ( '' !== $tamil_info ) : ?>
					<span><?php echo esc_html( $tamil_info ); ?></span>
				<?php endif; ?>
			</p>
			<h1 class="artikel__titel"><?php echo tamil_text( get_the_title() ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_text() ?></h1>
			<?php if ( $tamil_beisp ) : ?>
				<p class="hinweis-box seite__entwurf" role="note"><?php esc_html_e( 'Beispiel-Eintrag des Testsystems, keine echten Angaben.', 'tamil' ); ?></p>
			<?php endif; ?>
		</header>

		<?php if ( $tamil_eigen ) : ?>
			<figure class="artikel__figur">
				<?php
				echo tamil_bild( // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escapt in tamil_bild()
					$tamil_id,
					array(
						'eager'  => true,
						'signet' => false, // Eintrag eines Betriebs, kein Beitrag der Redaktion
						'klasse' => 'artikel__bild',
						'sizes'  => '(min-width: 1024px) 1040px, (min-width: 600px) 600px, 100vw',
					)
				);
				?>
				<?php if ( '' !== tamil_bild_nachweis_html( $tamil_id ) ) : ?>
					<figcaption class="artikel__nachweis"><?php echo wp_kses( tamil_bild_nachweis_html( $tamil_id ), tamil_nachweis_kses() ); ?></figcaption>
				<?php endif; ?>
			</figure>
		<?php endif; ?>

		<div class="artikel__haupt">
			<div class="artikel__text">
				<div class="inhalt vz-inhalt"><?php the_content(); ?></div>
				<?php if ( '' !== $tamil_karte ) : ?>
					<p class="aktionen vz-karte">
						<a class="textlink" href="<?php echo esc_url( 'https://www.openstreetmap.org/search?query=' . rawurlencode( $tamil_karte ) ); ?>" target="_blank" rel="noopener nofollow"><?php esc_html_e( 'Adresse auf der Karte ansehen', 'tamil' ); ?></a>
					</p>
				<?php endif; ?>
				<p class="aktionen">
					<a class="textlink" href="<?php echo esc_url( $tamil_liste ); ?>"><?php esc_html_e( 'Zurück zum Verzeichnis', 'tamil' ); ?></a>
				</p>
			</div>
		</div>
	</article>
	<?php
endwhile;

get_footer();
