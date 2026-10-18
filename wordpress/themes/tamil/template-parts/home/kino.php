<?php
/**
 * Kino-Schaufenster: der neueste Beitrag mit Kinoliste – Zahl der Spielorte, Filmstreifen, Link zur Liste.
 *
 * @var array $args { @type int $post }
 */

defined( 'ABSPATH' ) || exit;

$post_id = (int) ( $args['post'] ?? 0 );
$fakten  = $post_id && function_exists( 'tamil_site_kino_fakten' ) ? tamil_site_kino_fakten( $post_id ) : array();
$kinos   = is_array( $fakten['kinos'] ?? null ) ? $fakten['kinos'] : array();
if ( ! $kinos ) {
	return;
}
$laender = array(
	'DE' => __( 'Deutschland', 'tamil' ),
	'AT' => __( 'Österreich', 'tamil' ),
	'CH' => __( 'Schweiz', 'tamil' ),
);
$link    = get_permalink( $post_id );
$quellen = array_unique( array_filter( array_map( static fn( $k ) => (string) ( $k['quelle'] ?? '' ), $kinos ) ) );
$termin  = static function ( array $k ): string {
	$fmt = static fn( string $d ): string => wp_date( 'j.n.', (int) strtotime( $d ) );
	if ( ! empty( $k['termine'] ) ) {
		/* translators: 1: Anzahl, 2: Datum */
		return sprintf( _n( '%1$d Vorstellung, ab %2$s', '%1$d Vorstellungen, ab %2$s', count( $k['termine'] ), 'tamil' ), count( $k['termine'] ), $fmt( (string) $k['termine'][0] ) );
	}
	if ( ! empty( $k['von'] ) && ! empty( $k['bis'] ) ) {
		return $fmt( (string) $k['von'] ) . ' – ' . $fmt( (string) $k['bis'] );
	}
	/* translators: %s: Datum */
	return ! empty( $k['von'] ) ? sprintf( __( 'ab %s', 'tamil' ), $fmt( (string) $k['von'] ) ) : '';
};
?>
<section class="section" id="kino-schaufenster" style="padding-top:0">
	<div class="container">
		<div class="kino-widget">
			<div class="kopf">
				<div><span class="zahl" data-count="<?php echo esc_attr( (string) count( $kinos ) ); ?>"><?php echo esc_html( (string) count( $kinos ) ); ?></span></div>
				<div>
					<h2 class="kicker"><span class="ta" lang="ta">சினிமா</span><span class="de"><?php esc_html_e( 'Jetzt im Kino', 'tamil' ); ?></span></h2>
					<h2 class="kino-titel"><a href="<?php echo esc_url( $link ); ?>"><?php echo esc_html( get_the_title( $post_id ) ); ?></a></h2>
					<?php /* translators: 1: Kinowoche, 2: Datum */ ?>
					<p class="zahl-text"><?php echo wp_kses( sprintf( __( '%1$s, <strong>aktualisiert %2$s</strong>.', 'tamil' ), esc_html( tamil_kinowoche( (string) ( $fakten['woche'] ?? '' ) ) ), esc_html( get_the_modified_date( 'j. F', $post_id ) ) ), array( 'strong' => array() ) ); ?></p>
				</div>
			</div>
			<div class="strip" aria-label="<?php esc_attr_e( 'Spielorte', 'tamil' ); ?>">
				<div class="track">
					<?php foreach ( $kinos as $k ) : ?>
						<a class="kino-karte" href="<?php echo esc_url( $link ); ?>"><span class="land"><?php echo esc_html( $laender[ $k['land'] ?? '' ] ?? (string) ( $k['land'] ?? '' ) ); ?></span><b><?php echo esc_html( (string) ( $k['stadt'] ?? '' ) ); ?></b><span><?php echo esc_html( (string) ( $k['kino'] ?? '' ) ); ?></span><span class="termin"><?php echo esc_html( $termin( $k ) ); ?></span></a>
					<?php endforeach; ?>
				</div>
			</div>
			<div class="aktion"><a class="btn btn-gold" href="<?php echo esc_url( $link ); ?>"><?php esc_html_e( 'Alle Spielorte und Tickets', 'tamil' ); ?></a><a class="btn btn-ghost hell" href="<?php echo esc_url( tamil_rubrik( 'kino' )['url'] ); ?>"><?php esc_html_e( 'Mehr Kino', 'tamil' ); ?></a></div>
			<?php if ( $quellen ) : ?>
				<?php /* translators: %s: Quellen */ ?>
				<p class="stand"><?php echo esc_html( sprintf( __( 'Quellen: %s. Angaben ohne Gewähr.', 'tamil' ), implode( ', ', $quellen ) ) ); ?></p>
			<?php endif; ?>
		</div>
	</div>
</section>
