<?php
/**
 * Fuß jeder Seite (weißer Grund mit Linie in Titan Red oben): Werbeplatz „Footer“, Logo mit Unterzeile, Rubriken,
 * Dienste, Social (nur mit Adresse), die Bildnachweise der Seite und die Zeile mit Rechtlichem (als Band in Titan Red,
 * nur per CSS). Am Handy danach der feste Werbeplatz. Jeder Werbeplatz ist schon ein benannter Bereich des
 * Plugins (<aside aria-label="Anzeige: …">); das Theme legt keinen zweiten darum.
 */

defined( 'ABSPATH' ) || exit;

$tamil_social    = tamil_social();
$tamil_unterzeil = '' !== tamil_opt( 'tagline' ) ? tamil_opt( 'tagline' ) : tamil_opt( 'ueber_uns' );
?>
<?php tamil_leaderboard(); ?>
</main>
<?php
$tamil_footer_ad = function_exists( 'tamil_site_anzeige' ) ? tamil_site_anzeige( 'footer', false ) : '';
if ( '' !== $tamil_footer_ad ) :
	?>
	<div class="innen anzeige-unten"><?php echo $tamil_footer_ad; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Werbeplatz aus dem Plugin (benannter Bereich „Anzeige: Fuß“), dort escapt ?></div>
<?php endif; ?>
<footer class="fuss">
	<div class="innen fuss__innen">
		<div class="fuss__marke">
			<?php get_template_part( 'template-parts/header/logo', null, array( 'class' => 'fuss__logo' ) ); ?>
			<?php
			if ( '' !== $tamil_unterzeil ) :
				?>
				<p class="fuss__satz"><?php echo esc_html( $tamil_unterzeil ); ?></p><?php endif; ?>
		</div>
		<nav class="fuss__spalte" aria-label="<?php esc_attr_e( 'Rubriken im Fuß', 'tamil' ); ?>">
			<h2><?php esc_html_e( 'Rubriken', 'tamil' ); ?></h2>
			<ul>
				<?php foreach ( tamil_nav_items() as $tamil_item ) : ?>
					<?php
					if ( '' === $tamil_item['slug'] ) {
						continue; // Kontakt steht unter Dienste
					}
					?>
					<li><a href="<?php echo esc_url( $tamil_item['url'] ); ?>"><?php echo esc_html( $tamil_item['label'] ); ?></a></li>
				<?php endforeach; ?>
			</ul>
		</nav>
		<nav class="fuss__spalte" aria-label="<?php esc_attr_e( 'Dienste im Fuß', 'tamil' ); ?>">
			<h2><?php esc_html_e( 'Dienste', 'tamil' ); ?></h2>
			<?php
			if ( has_nav_menu( 'footer_service' ) ) {
				wp_nav_menu(
					array(
						'theme_location' => 'footer_service',
						'container'      => false,
						'depth'          => 1,
					)
				);
			} else {
				echo '<ul>';
				foreach ( tamil_dienste() as $tamil_d ) {
					echo '<li><a href="' . esc_url( $tamil_d['url'] ) . '">' . esc_html( $tamil_d['label'] ) . '</a></li>';
				}
				echo '</ul>';
			}
			?>
		</nav>
		<?php if ( $tamil_social ) : ?>
			<div class="fuss__spalte">
				<h2><?php esc_html_e( 'Folgen', 'tamil' ); ?></h2>
				<ul>
					<?php foreach ( $tamil_social as $tamil_s ) : ?>
						<li><a href="<?php echo esc_url( $tamil_s['url'] ); ?>" target="_blank" rel="noopener"><?php echo esc_html( $tamil_s['name'] ); ?></a></li>
					<?php endforeach; ?>
				</ul>
			</div>
		<?php endif; ?>
	</div>
	<?php
	// Erst hier auslesen: Werbeplätze und Bilder darüber haben ihre Nachweise dann gemerkt (die Handy-Leiste unter dem
	// Fuß meldet ihren vorab über get_footer im Plugin).
	$tamil_nachweise = tamil_nachweise();
	?>
	<?php if ( $tamil_nachweise ) : ?>
		<details class="innen fuss__nachweise">
			<?php /* translators: %d: Anzahl der Nachweise */ ?>
			<summary><?php echo esc_html( sprintf( __( 'Bildnachweise dieser Seite (%d)', 'tamil' ), count( $tamil_nachweise ) ) ); ?></summary>
			<ul class="nachweise">
				<?php foreach ( $tamil_nachweise as $tamil_n ) : ?>
					<li><?php echo wp_kses( $tamil_n, tamil_nachweis_kses() ); ?></li>
				<?php endforeach; ?>
			</ul>
		</details>
	<?php endif; ?>
	<div class="innen">
		<p class="fuss__recht">
			<span>© <?php echo esc_html( wp_date( 'Y' ) ); ?> <?php bloginfo( 'name' ); ?><?php echo tamil_opt( 'org' ) ? ', ' . esc_html( tamil_opt( 'org' ) ) : ''; ?></span>
			<?php
			if ( has_nav_menu( 'footer_legal' ) ) {
				wp_nav_menu(
					array(
						'theme_location' => 'footer_legal',
						'container'      => false,
						'depth'          => 1,
						'items_wrap'     => '%3$s',
						'fallback_cb'    => false,
					)
				);
			} else {
				if ( tamil_seite( 'impressum' ) ) {
					echo '<a href="' . esc_url( tamil_seiten_url( 'impressum' ) ) . '">' . esc_html__( 'Impressum', 'tamil' ) . '</a>';
				}
				$tamil_datenschutz = (int) get_option( 'wp_page_for_privacy_policy' );
				if ( $tamil_datenschutz && 'publish' === get_post_status( $tamil_datenschutz ) ) {
					echo '<a href="' . esc_url( get_permalink( $tamil_datenschutz ) ) . '">' . esc_html__( 'Datenschutzerklärung', 'tamil' ) . '</a>';
				} elseif ( tamil_seite( 'datenschutz' ) ) {
					echo '<a href="' . esc_url( tamil_seiten_url( 'datenschutz' ) ) . '">' . esc_html__( 'Datenschutzerklärung', 'tamil' ) . '</a>';
				}
			}
			/**
			 * Platz für den Link „Cookie-Einstellungen“ eines Consent-Plugins.
			 */
			do_action( 'tamil_footer_legal' );
			?>
		</p>
	</div>
</footer>
<?php tamil_anzeige( 'mobile' ); // Handy-Leiste: ein benannter Bereich des Plugins („Anzeige: Mobil“, id ad-mobile), ohne Rahmen ?>
</div>
<?php wp_footer(); ?>
</body>
</html>
