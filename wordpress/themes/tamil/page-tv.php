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
<div class="innen">
	<header class="seitenkopf">
		<h1 class="seitenkopf__titel"><?php the_title(); ?></h1>
		<p class="seitenkopf__zeile"><?php echo esc_html( tamil_opt( 'tv_text' ) ); ?></p>
	</header>
	<section class="block">
		<?php if ( $sender ) : ?>
			<ul class="sender">
				<?php foreach ( $sender as [ $name, $stream ] ) : ?>
					<li>
						<div class="player" data-stream="<?php echo esc_url( $stream ); ?>">
							<?php /* translators: %s: Sender */ ?>
							<button type="button" class="play knopf" aria-label="<?php echo esc_attr( sprintf( __( '%s abspielen', 'tamil' ), $name ) ); ?>"><?php esc_html_e( 'Abspielen', 'tamil' ); ?></button>
						</div>
						<h2 class="sender__name"><?php echo esc_html( $name ); ?></h2>
						<p class="sender__zeile"><?php esc_html_e( 'Live-Stream im Browser, startet erst nach Klick.', 'tamil' ); ?></p>
					</li>
				<?php endforeach; ?>
			</ul>
		<?php else : ?>
			<h2 class="block-titel"><?php esc_html_e( 'Die Sender werden gerade eingerichtet.', 'tamil' ); ?></h2>
			<p class="leer__satz"><?php esc_html_e( 'Sobald neue Stream-Adressen vorliegen, laufen die Player hier wieder.', 'tamil' ); ?></p>
		<?php endif; ?>
	</section>
	<?php
	while ( have_posts() ) :
		the_post();
		if ( '' !== trim( (string) get_the_content() ) ) :
			?>
			<section class="block seite__text"><div class="inhalt"><?php the_content(); ?></div></section>
			<?php
		endif;
	endwhile;
	?>
</div>
<?php
get_footer();
