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
<header class="seitenkopf">
	<div class="wrap">
		<h1><?php the_title(); ?></h1>
		<p class="satz"><?php echo esc_html( tamil_opt( 'tv_text' ) ); ?></p>
	</div>
</header>
<section class="abschnitt">
	<div class="wrap">
		<?php if ( $sender ) : ?>
			<ul class="sender">
				<?php foreach ( $sender as [ $name, $stream ] ) : ?>
					<li>
						<div class="player" data-stream="<?php echo esc_url( $stream ); ?>">
							<?php /* translators: %s: Sender */ ?>
							<button type="button" class="play knopf" aria-label="<?php echo esc_attr( sprintf( __( '%s abspielen', 'tamil' ), $name ) ); ?>"><?php esc_html_e( 'Abspielen', 'tamil' ); ?></button>
						</div>
						<h2 class="b-titel"><?php echo esc_html( $name ); ?></h2>
						<p class="klein"><?php esc_html_e( 'Live-Stream im Browser, startet erst nach Klick.', 'tamil' ); ?></p>
					</li>
				<?php endforeach; ?>
			</ul>
		<?php else : ?>
			<h2 class="strom-kopf"><?php esc_html_e( 'Die Sender werden gerade eingerichtet.', 'tamil' ); ?></h2>
			<p class="satz"><?php esc_html_e( 'Sobald neue Stream-Adressen vorliegen, laufen die Player hier wieder.', 'tamil' ); ?></p>
		<?php endif; ?>
		<?php
		while ( have_posts() ) :
			the_post();
			if ( '' !== trim( (string) get_the_content() ) ) :
				?>
				<div class="inhalt seite-text"><?php the_content(); ?></div>
				<?php
			endif;
		endwhile;
		?>
	</div>
</section>
<?php
get_footer();
