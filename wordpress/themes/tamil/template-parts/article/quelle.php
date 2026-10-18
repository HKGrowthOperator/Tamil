<?php
/**
 * Quellenzeile für Beiträge mit Quelle (Meta „quelle_url“), sofern der Text sie nicht schon enthält.
 *
 * @var array $args { @type int $post, @type string $inhalt }
 */

defined( 'ABSPATH' ) || exit;

$post_id = (int) $args['post'];
$url     = (string) get_post_meta( $post_id, 'quelle_url', true );
if ( '' === $url || str_contains( (string) ( $args['inhalt'] ?? '' ), 'class="quelle"' ) ) {
	return;
}
$name = (string) get_post_meta( $post_id, 'quelle_name', true );
?>
<p class="quelle"><?php esc_html_e( 'Quelle:', 'tamil' ); ?> <a href="<?php echo esc_url( $url ); ?>" target="_blank" rel="noopener nofollow"><?php echo esc_html( ( '' !== $name ? $name : (string) wp_parse_url( $url, PHP_URL_HOST ) ) ); ?></a></p>
