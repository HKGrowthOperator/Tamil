<?php
/**
 * Footer: Werbeplatz 04, Über Tamil.de, Rubriken, Service, Folgen, Rechtliches; mobil Werbeplatz 05.
 */

defined( 'ABSPATH' ) || exit;

$social = tamil_social();
?>
</main>
<div class="wrap"><?php tamil_anzeige( 'footer' ); ?></div>
<footer class="fuss">
	<div class="wrap fuss-raster">
		<div class="fuss-ueber">
			<a class="fuss-marke" href="<?php echo esc_url( home_url( '/' ) ); ?>">tamil<span>.de</span></a>
			<p><?php echo esc_html( tamil_opt( 'ueber_uns' ) ); ?></p>
		</div>
		<div>
			<h2 class="fuss-titel"><?php esc_html_e( 'Rubriken', 'tamil' ); ?></h2>
			<ul>
				<?php foreach ( array_keys( tamil_rubriken_standard() ) as $slug ) : ?>
					<?php $rubrik = tamil_rubrik( $slug ); ?>
					<?php if ( $rubrik['term'] || 'events' === $slug ) : ?>
						<li><a href="<?php echo esc_url( $rubrik['url'] ); ?>"><?php echo esc_html( $rubrik['label'] ); ?></a></li>
					<?php endif; ?>
				<?php endforeach; ?>
			</ul>
		</div>
		<div>
			<h2 class="fuss-titel"><?php esc_html_e( 'Service', 'tamil' ); ?></h2>
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
				echo '<li><a href="' . esc_url( tamil_seiten_url( 'kontakt', 'event-einreichen' ) ) . '">' . esc_html__( 'Event einreichen', 'tamil' ) . '</a></li>';
				echo '<li><a href="' . esc_url( tamil_seiten_url( 'kontakt', 'werben' ) ) . '">' . esc_html__( 'Werben auf Tamil.de', 'tamil' ) . '</a></li>';
				foreach ( array(
					'production' => tamil_opt( 'production_titel' ),
					'tv'         => __( 'Tamil TV', 'tamil' ),
					'ueber-uns'  => __( 'Über Tamil.de', 'tamil' ),
				) as $slug => $label ) {
					if ( tamil_seite( $slug ) ) {
						echo '<li><a href="' . esc_url( tamil_seiten_url( $slug ) ) . '">' . esc_html( $label ) . '</a></li>';
					}
				}
				echo '<li><a href="' . esc_url( tamil_seiten_url( 'kontakt' ) ) . '">' . esc_html__( 'Kontakt', 'tamil' ) . '</a></li>';
				echo '</ul>';
			}
			?>
		</div>
		<?php if ( $social ) : ?>
			<div>
				<h2 class="fuss-titel"><?php esc_html_e( 'Folgen', 'tamil' ); ?></h2>
				<ul>
					<?php foreach ( $social as $s ) : ?>
						<li><a href="<?php echo esc_url( $s['url'] ); ?>" target="_blank" rel="noopener"><?php tamil_icon( $s['icon'], 'ico ico-sm' ); ?> <?php echo esc_html( $s['name'] ); ?></a></li>
					<?php endforeach; ?>
				</ul>
			</div>
		<?php endif; ?>
		<div class="fuss-unten">
			<span>© <?php echo esc_html( wp_date( 'Y' ) ); ?> <?php bloginfo( 'name' ); ?><?php echo tamil_opt( 'org' ) ? ' · ' . esc_html( tamil_opt( 'org' ) ) : ''; ?></span>
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
				foreach ( array( 'impressum' => __( 'Impressum', 'tamil' ) ) as $slug => $label ) {
					if ( tamil_seite( $slug ) ) {
						echo '<a href="' . esc_url( tamil_seiten_url( $slug ) ) . '">' . esc_html( $label ) . '</a>';
					}
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
		</div>
	</div>
</footer>
<?php tamil_anzeige( 'mobile' ); ?>
</div>
<?php wp_footer(); ?>
</body>
</html>
