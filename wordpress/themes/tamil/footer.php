<?php
/**
 * Fuß: Werbeplatz 04, Feld mit Logo und Selbstbeschreibung, Rubriken, Dienste, Rechtliches und den Bildnachweisen
 * der Seite; mobil Werbeplatz 05.
 */

defined( 'ABSPATH' ) || exit;

$tamil_social    = tamil_social();
$tamil_nachweise = tamil_nachweise();
?>
<?php tamil_leaderboard(); ?>
</main>
<?php
$tamil_footer_ad = function_exists( 'tamil_site_anzeige' ) ? tamil_site_anzeige( 'footer', false ) : '';
if ( '' !== $tamil_footer_ad ) :
	?>
	<div class="wrap anzeige-unten"><?php echo $tamil_footer_ad; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Werbeplatz aus dem Plugin, dort escapt ?></div>
<?php endif; ?>
<footer class="fuss">
	<div class="wrap">
		<div class="fuss-marke">
			<?php get_template_part( 'template-parts/header/logo', null, array( 'class' => 'fuss-logo' ) ); ?>
			<p><?php echo esc_html( '' !== tamil_opt( 'tagline' ) ? tamil_opt( 'tagline' ) : tamil_opt( 'ueber_uns' ) ); // kurz wie in der Probe; der lange Text steht auf „Über uns“ ?></p>
			<p class="fuss-recht">
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
					$datenschutz = (int) get_option( 'wp_page_for_privacy_policy' );
					if ( $datenschutz && 'publish' === get_post_status( $datenschutz ) ) {
						echo '<a href="' . esc_url( get_permalink( $datenschutz ) ) . '">' . esc_html__( 'Datenschutzerklärung', 'tamil' ) . '</a>';
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
		<div>
			<h2><?php esc_html_e( 'Rubriken', 'tamil' ); ?></h2>
			<ul>
				<?php foreach ( array_keys( tamil_rubriken_standard() ) as $slug ) : ?>
					<?php $rubrik = tamil_rubrik( $slug ); ?>
					<?php if ( $rubrik['term'] && 'events' !== $slug ) : ?>
						<li><a href="<?php echo esc_url( $rubrik['url'] ); ?>"><?php echo esc_html( $rubrik['label'] ); ?></a></li>
					<?php endif; ?>
				<?php endforeach; ?>
			</ul>
		</div>
		<div>
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
				foreach ( array_filter( tamil_kopf_ziele(), static fn( $z ) => $z['dienst'] ) as $z ) {
					echo '<li><a href="' . esc_url( $z['url'] ) . '">' . esc_html( $z['label'] ) . '</a></li>';
				}
				foreach ( tamil_dienste() as $d ) {
					echo '<li><a href="' . esc_url( $d['url'] ) . '">' . esc_html( $d['label'] ) . '</a></li>';
				}
				echo '</ul>';
			}
			?>
			<?php if ( $tamil_social ) : ?>
				<h2 class="fuss-folgen"><?php esc_html_e( 'Folgen', 'tamil' ); ?></h2>
				<ul>
					<?php foreach ( $tamil_social as $s ) : ?>
						<li><a href="<?php echo esc_url( $s['url'] ); ?>" target="_blank" rel="noopener"><?php echo esc_html( $s['name'] ); ?></a></li>
					<?php endforeach; ?>
				</ul>
			<?php endif; ?>
		</div>
		<?php if ( $tamil_nachweise ) : ?>
			<div>
				<h2><?php esc_html_e( 'Bildnachweise', 'tamil' ); ?></h2>
				<ul class="nachweise">
					<?php foreach ( $tamil_nachweise as $n ) : ?>
						<li><?php echo esc_html( $n ); ?></li>
					<?php endforeach; ?>
				</ul>
			</div>
		<?php endif; ?>
	</div>
</footer>
<?php tamil_anzeige( 'mobile' ); ?>
</div>
<?php wp_footer(); ?>
</body>
</html>
