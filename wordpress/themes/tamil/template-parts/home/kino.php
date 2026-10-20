<?php
/**
 * Kinoliste der Woche: der neueste Beitrag mit Kinoliste – Film, Zahl der Spielorte, Städte zum Wischen, Link zur
 * vollständigen Liste. Steht im Kino-Abschnitt der Startseite unter den Kino-Beiträgen.
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
$film    = (string) ( $fakten['film'] ?? '' );
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
<div class="kinoliste" id="kinoliste">
	<div class="kinoliste-kopf">
		<p class="kinoliste-zahl"><b><?php echo esc_html( (string) count( $kinos ) ); ?></b> <?php echo esc_html( _n( 'Kino', 'Kinos', count( $kinos ), 'tamil' ) ); ?></p>
		<div>
			<p class="meta"><span class="rubrik r-kino"><?php esc_html_e( 'Diese Woche im Kino', 'tamil' ); ?></span><span><?php echo esc_html( tamil_kinowoche( (string) ( $fakten['woche'] ?? '' ) ) ); ?></span></p>
			<h3><a href="<?php echo esc_url( $link ); ?>"><?php echo esc_html( '' !== $film ? $film : get_the_title( $post_id ) ); ?></a></h3>
		</div>
		<a class="knopf" href="<?php echo esc_url( $link ); ?>"><?php esc_html_e( 'Alle Spielorte', 'tamil' ); ?></a>
	</div>
	<ul class="kinoliste-orte" aria-label="<?php esc_attr_e( 'Spielorte', 'tamil' ); ?>">
		<?php foreach ( $kinos as $k ) : ?>
			<li><a href="<?php echo esc_url( $link ); ?>"><b><?php echo esc_html( (string) ( $k['stadt'] ?? '' ) ); ?></b><span><?php echo esc_html( (string) ( $k['kino'] ?? '' ) ); ?></span><span class="klein"><?php echo esc_html( trim( ( $laender[ $k['land'] ?? '' ] ?? (string) ( $k['land'] ?? '' ) ) . ' · ' . $termin( $k ), ' ·' ) ); ?></span></a></li>
		<?php endforeach; ?>
	</ul>
	<?php if ( $quellen ) : ?>
		<?php /* translators: 1: Datum, 2: Quellen */ ?>
		<p class="kinoliste-stand"><?php echo esc_html( sprintf( __( 'Stand %1$s · Quellen: %2$s · Angaben ohne Gewähr', 'tamil' ), get_the_modified_date( 'j. F', $post_id ), implode( ', ', $quellen ) ) ); ?></p>
	<?php endif; ?>
</div>
