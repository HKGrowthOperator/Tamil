<?php
/**
 * Template Name: Tamil TV
 *
 * Sender aus dem Customizer (Name | HLS-Adresse). Der Stream startet erst nach Klick (Datenschutz); Browser ohne
 * eingebautes HLS (Chrome, Firefox) bekommen den Link zum Öffnen im Player ihrer Wahl.
 */

defined( 'ABSPATH' ) || exit;

get_header();

$sender = array();
foreach ( (array) preg_split( '/\r\n|\r|\n/', tamil_opt( 'tv_sender' ) ) as $zeile ) {
	$teile = array_map( 'trim', explode( '|', $zeile ) );
	if ( 2 === count( $teile ) && '' !== $teile[0] && '' !== $teile[1] ) {
		$sender[] = $teile;
	}
}
?>
<div class="wrap">
	<?php tamil_breadcrumb( array( array( get_the_title(), '' ) ) ); ?>
	<header class="seitenkopf">
		<h1><?php the_title(); ?></h1>
		<p class="beschreibung"><?php echo esc_html( tamil_opt( 'tv_text' ) ); ?></p>
	</header>
	<div class="mit-spalte">
		<div>
			<?php if ( $sender ) : ?>
				<div class="kartenraster zwei">
					<?php foreach ( $sender as [ $name, $stream ] ) : ?>
						<article class="card">
							<div class="media player" data-stream="<?php echo esc_url( $stream ); ?>">
								<button type="button" class="play" aria-label="<?php /* translators: %s: Sender */ echo esc_attr( sprintf( __( '%s abspielen', 'tamil' ), $name ) ); ?>"><?php tamil_icon( 'play' ); ?></button>
							</div>
							<div class="text"><h3><?php echo esc_html( $name ); ?></h3><p class="excerpt"><?php esc_html_e( 'Live-Stream im Browser, startet erst nach Klick.', 'tamil' ); ?></p></div>
						</article>
					<?php endforeach; ?>
				</div>
			<?php else : ?>
				<div class="leer"><h2><?php esc_html_e( 'Die Sender werden gerade eingerichtet.', 'tamil' ); ?></h2><p><?php esc_html_e( 'Sobald neue Stream-Adressen vorliegen, laufen die Player hier wieder.', 'tamil' ); ?></p></div>
			<?php endif; ?>
			<?php
			while ( have_posts() ) :
				the_post();
				?>
				<?php
				if ( '' !== trim( (string) get_the_content() ) ) :
					?>
					<div class="artikel-text section"><?php the_content(); ?></div><?php endif; ?>
			<?php endwhile; ?>
		</div>
		<?php get_sidebar(); ?>
	</div>
</div>
<?php
get_footer();
