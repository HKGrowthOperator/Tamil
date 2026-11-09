<?php
/**
 * REST-Schnittstelle tamil-radar/v1: status, beitrag (POST), beitrag/{uid} (GET, PUT), stil.
 *
 * Ein Aufruf legt den fertigen Beitrag an: Text, Teaser, Kategorie, Schlagworte, Meta, SEO und das Beitragsbild
 * (Base64). Dubletten erkennt der Radar an radar_uid (409). Veröffentlichen darf nur, wer publish_posts hat.
 */

defined( 'ABSPATH' ) || exit;

function tamil_radar_can_read(): bool {
	return current_user_can( 'edit_posts' );
}

function tamil_radar_can_write(): bool {
	return current_user_can( 'edit_posts' ) && current_user_can( 'upload_files' );
}

function tamil_radar_register_routes(): void {
	register_rest_route(
		TAMIL_RADAR_NS,
		'/status',
		array(
			'methods'             => WP_REST_Server::READABLE,
			'callback'            => 'tamil_radar_rest_status',
			'permission_callback' => 'tamil_radar_can_read',
		)
	);
	register_rest_route(
		TAMIL_RADAR_NS,
		'/beitrag',
		array(
			'methods'             => WP_REST_Server::CREATABLE,
			'callback'            => 'tamil_radar_rest_create',
			'permission_callback' => 'tamil_radar_can_write',
			'args'                => tamil_radar_beitrag_args( true ),
		)
	);
	register_rest_route(
		TAMIL_RADAR_NS,
		'/beitrag/(?P<uid>[A-Za-z0-9._:-]+)',
		array(
			array(
				'methods'             => WP_REST_Server::READABLE,
				'callback'            => 'tamil_radar_rest_get',
				'permission_callback' => 'tamil_radar_can_read',
			),
			array(
				'methods'             => WP_REST_Server::EDITABLE,
				'callback'            => 'tamil_radar_rest_update',
				'permission_callback' => 'tamil_radar_can_write',
				'args'                => tamil_radar_beitrag_args( false ),
			),
		)
	);
	register_rest_route(
		TAMIL_RADAR_NS,
		'/stil',
		array(
			'methods'             => WP_REST_Server::READABLE,
			'callback'            => 'tamil_radar_rest_stil',
			'permission_callback' => 'tamil_radar_can_read',
			'args'                => array(
				'n' => array(
					'type'    => 'integer',
					'default' => 8,
					'minimum' => 1,
					'maximum' => 20,
				),
			),
		)
	);
}

/**
 * Parameter-Schema für POST beitrag und PUT beitrag/{uid}.
 */
function tamil_radar_beitrag_args( bool $create ): array {
	$args = array(
		'titel'       => array(
			'type'              => 'string',
			'required'          => $create,
			'sanitize_callback' => 'sanitize_text_field',
		),
		'inhalt'      => array(
			'type'     => 'string',
			'required' => $create,
		),
		'teaser'      => array(
			'type'              => 'string',
			'default'           => '',
			'sanitize_callback' => 'sanitize_textarea_field',
		),
		'status'      => array(
			'type'    => 'string',
			'enum'    => array( 'publish', 'pending', 'draft', 'future' ),
			'default' => 'pending',
		),
		'slug'        => array(
			'type'              => 'string',
			'default'           => '',
			'sanitize_callback' => 'tamil_radar_sanitize_slug',
		),
		'datum'       => array(
			'type'    => 'string',
			'default' => '',
		),
		'kategorie'   => array(
			'type'              => 'string',
			'default'           => '',
			'sanitize_callback' => 'tamil_radar_sanitize_slug',
		),
		'kategorien'  => array(
			'type'    => 'array',
			'items'   => array( 'type' => 'string' ),
			'default' => array(),
		),
		'schlagworte' => array(
			'type'    => 'array',
			'items'   => array( 'type' => 'string' ),
			'default' => array(),
		),
		'meta'        => array(
			'type'    => 'object',
			'default' => array(),
		),
		'seo'         => array(
			'type'    => 'object',
			'default' => array(),
		),
		'bild'        => array(
			'type'    => 'object',
			'default' => array(),
		),
	);
	if ( ! $create ) {
		// PUT ändert nur, was mitgeschickt wird – keine Vorgaben, die Felder leeren oder das Enum verletzen.
		foreach ( $args as $name => $schema ) {
			unset( $args[ $name ]['default'] );
		}
	}
	return $args;
}

/**
 * sanitize_title als REST-Sanitizer: WordPress übergibt das Request-Objekt als zweites Argument, das sanitize_title
 * sonst als Rückfallwert zurückgäbe.
 */
function tamil_radar_sanitize_slug( $value ): string {
	return sanitize_title( (string) $value );
}

/**
 * Datum des Beitrags: ohne Zeitzonenangabe gilt die Zeitzone der Website (Europe/Berlin), mit Angabe die angegebene.
 */
function tamil_radar_parse_datum( string $raw ): ?DateTimeImmutable {
	$raw = trim( $raw );
	if ( '' === $raw ) {
		return null;
	}
	try {
		$dt = new DateTimeImmutable( $raw, wp_timezone() );
	} catch ( Exception $e ) {
		return null;
	}
	return $dt->setTimezone( wp_timezone() );
}

function tamil_radar_rest_status(): WP_REST_Response {
	$kategorien = array();
	foreach ( get_categories( array( 'hide_empty' => false ) ) as $cat ) {
		$kategorien[ $cat->slug ] = (int) $cat->term_id;
	}
	$letzter = get_posts(
		array(
			'post_type'      => 'post',
			'post_status'    => 'any',
			'posts_per_page' => 1,
			'orderby'        => 'date',
			'meta_query'     => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
				array(
					'key'     => 'radar_uid',
					'value'   => '',
					'compare' => '!=',
				),
			),
		)
	);
	$last    = $letzter ? array(
		'id'     => $letzter[0]->ID,
		'titel'  => $letzter[0]->post_title,
		'status' => $letzter[0]->post_status,
		'datum'  => $letzter[0]->post_date,
		'link'   => get_permalink( $letzter[0] ),
	) : null;
	return new WP_REST_Response(
		array(
			'plugin'          => TAMIL_RADAR_VERSION,
			'wordpress'       => get_bloginfo( 'version' ),
			'seo'             => tamil_radar_seo_plugin(),
			'advanced_ads'    => function_exists( 'get_the_ad_placement' ),
			'rolle_radar'     => (bool) get_role( 'radar' ),
			'benutzer'        => wp_get_current_user()->user_login,
			'kann_publish'    => current_user_can( 'publish_posts' ),
			'kategorien'      => $kategorien,
			'radar_beitraege' => array(
				'gesamt'          => tamil_radar_count_posts( 'any' ),
				'veroeffentlicht' => tamil_radar_count_posts( 'publish' ),
			),
			'letzter'         => $last,
			'zeit'            => current_time( 'c' ),
		)
	);
}

/**
 * Antwortkörper für einen Beitrag.
 */
function tamil_radar_beitrag_response( int $post_id ): array {
	$post = get_post( $post_id );
	$tags = wp_get_post_terms( $post_id, 'post_tag', array( 'fields' => 'names' ) );
	$cats = wp_get_post_terms( $post_id, 'category', array( 'fields' => 'slugs' ) );
	$meta = array();
	foreach ( tamil_radar_meta_keys() as $key => $type ) {
		$value = get_post_meta( $post_id, $key, true );
		if ( 'json' === $type ) {
			$value = tamil_radar_get_json( $post_id, $key );
		} elseif ( 'int' === $type ) {
			$value = '' === $value ? null : (int) $value;
		}
		$meta[ $key ] = $value;
	}
	return array(
		'id'             => $post_id,
		'status'         => $post ? $post->post_status : '',
		'titel'          => $post ? $post->post_title : '',
		'slug'           => $post ? $post->post_name : '',
		'datum'          => $post ? $post->post_date : '',
		'link'           => get_permalink( $post_id ),
		'edit_link'      => admin_url( 'post.php?post=' . $post_id . '&action=edit' ),
		'radar_uid'      => (string) get_post_meta( $post_id, 'radar_uid', true ),
		'featured_media' => (int) get_post_thumbnail_id( $post_id ),
		'bild_url'       => (string) get_the_post_thumbnail_url( $post_id, 'full' ),
		'categories'     => is_wp_error( $cats ) ? array() : $cats,
		'tags'           => is_wp_error( $tags ) ? array() : $tags,
		'meta'           => $meta,
		'seo'            => tamil_radar_seo_plugin(),
	);
}

/**
 * Kategorien per Slug auflösen; unbekannte Slugs fallen auf „news“ (sonst Standardkategorie) zurück.
 *
 * @return int[]
 */
function tamil_radar_resolve_categories( array $slugs ): array {
	$ids = array();
	foreach ( $slugs as $slug ) {
		$term = get_category_by_slug( sanitize_title( (string) $slug ) );
		if ( $term ) {
			$ids[] = (int) $term->term_id;
		}
	}
	if ( ! $ids ) {
		$news  = get_category_by_slug( 'news' );
		$ids[] = $news ? (int) $news->term_id : (int) get_option( 'default_category' );
	}
	return array_values( array_unique( $ids ) );
}

/**
 * Status, den der Aufrufer setzen darf: publish nur mit publish_posts, sonst pending.
 */
function tamil_radar_allowed_status( string $wanted ): string {
	if ( in_array( $wanted, array( 'publish', 'future' ), true ) && ! current_user_can( 'publish_posts' ) ) {
		return 'pending';
	}
	return '' !== $wanted ? $wanted : 'pending';
}

/**
 * Meta aus dem Request übernehmen (nur bekannte Schlüssel, gesäubert).
 */
function tamil_radar_apply_meta( int $post_id, array $meta ): void {
	$keys = tamil_radar_meta_keys();
	foreach ( $meta as $key => $value ) {
		if ( ! isset( $keys[ $key ] ) ) {
			continue;
		}
		$clean = tamil_radar_sanitize_meta( $value, $keys[ $key ] );
		if ( '' === $clean || 0 === $clean ) {
			delete_post_meta( $post_id, $key );
		} else {
			update_post_meta( $post_id, $key, $clean );
		}
	}
}

/**
 * Beitragsbild aus dem Request setzen (ersetzt ein vorhandenes).
 *
 * @return true|WP_Error
 */
function tamil_radar_apply_bild( int $post_id, array $bild ) {
	if ( empty( $bild['daten'] ) ) {
		return true;
	}
	$attachment = tamil_radar_sideload_base64(
		(string) $bild['daten'],
		(string) ( $bild['dateiname'] ?? '' ),
		(string) ( $bild['alt'] ?? get_the_title( $post_id ) ),
		(string) ( $bild['credit'] ?? '' ),
		$post_id
	);
	if ( is_wp_error( $attachment ) ) {
		return $attachment;
	}
	set_post_thumbnail( $post_id, $attachment );
	if ( ! empty( $bild['credit'] ) ) {
		update_post_meta( $post_id, 'bild_credit', sanitize_text_field( (string) $bild['credit'] ) );
	}
	return true;
}

function tamil_radar_rest_create( WP_REST_Request $request ) {
	$meta = (array) $request->get_param( 'meta' );
	$uid  = sanitize_text_field( (string) ( $meta['radar_uid'] ?? '' ) );
	if ( $uid ) {
		$existing = tamil_radar_post_id_by_uid( $uid );
		if ( $existing ) {
			return new WP_Error(
				'tamil_radar_duplicate',
				__( 'Zu dieser radar_uid gibt es schon einen Beitrag.', 'tamil-radar' ),
				array(
					'status'    => 409,
					'id'        => $existing,
					'link'      => get_permalink( $existing ),
					'edit_link' => admin_url( 'post.php?post=' . $existing . '&action=edit' ),
				)
			);
		}
	}
	$status = tamil_radar_allowed_status( (string) $request->get_param( 'status' ) );
	$data   = array(
		'post_type'     => 'post',
		'post_status'   => 'draft',
		'post_title'    => (string) $request->get_param( 'titel' ),
		'post_content'  => wp_kses_post( (string) $request->get_param( 'inhalt' ) ),
		'post_excerpt'  => (string) $request->get_param( 'teaser' ),
		'post_author'   => get_current_user_id(),
		'post_category' => tamil_radar_resolve_categories( array_merge( array( (string) $request->get_param( 'kategorie' ) ), (array) $request->get_param( 'kategorien' ) ) ),
	);
	$slug   = (string) $request->get_param( 'slug' );
	if ( $slug ) {
		$data['post_name'] = $slug;
	}
	$datum = tamil_radar_parse_datum( (string) $request->get_param( 'datum' ) );
	if ( $datum ) {
		$data['post_date']     = $datum->format( 'Y-m-d H:i:s' );
		$data['post_date_gmt'] = $datum->setTimezone( new DateTimeZone( 'UTC' ) )->format( 'Y-m-d H:i:s' );
	}
	$post_id = wp_insert_post( wp_slash( $data ), true );
	if ( is_wp_error( $post_id ) ) {
		$post_id->add_data( array( 'status' => 500 ) );
		return $post_id;
	}
	$bild = tamil_radar_apply_bild( (int) $post_id, (array) $request->get_param( 'bild' ) );
	if ( is_wp_error( $bild ) ) {
		wp_delete_post( (int) $post_id, true );
		return $bild;
	}
	$tags = array_filter( array_map( 'sanitize_text_field', (array) $request->get_param( 'schlagworte' ) ) );
	if ( $tags ) {
		wp_set_post_terms( (int) $post_id, $tags, 'post_tag', false );
	}
	tamil_radar_apply_meta( (int) $post_id, $meta );
	tamil_radar_write_seo( (int) $post_id, (array) $request->get_param( 'seo' ) );
	wp_update_post(
		array(
			'ID'          => (int) $post_id,
			'post_status' => $status,
		)
	);
	$response = new WP_REST_Response( tamil_radar_beitrag_response( (int) $post_id ), 201 );
	$response->header( 'Location', rest_url( TAMIL_RADAR_NS . '/beitrag/' . rawurlencode( '' !== $uid ? $uid : (string) $post_id ) ) );
	return $response;
}

function tamil_radar_rest_get( WP_REST_Request $request ) {
	$post_id = tamil_radar_post_id_by_uid( (string) $request['uid'] );
	if ( ! $post_id ) {
		return new WP_Error( 'tamil_radar_not_found', __( 'Kein Beitrag zu dieser radar_uid.', 'tamil-radar' ), array( 'status' => 404 ) );
	}
	return new WP_REST_Response( tamil_radar_beitrag_response( $post_id ) );
}

function tamil_radar_rest_update( WP_REST_Request $request ) {
	$post_id = tamil_radar_post_id_by_uid( (string) $request['uid'] );
	if ( ! $post_id ) {
		return new WP_Error( 'tamil_radar_not_found', __( 'Kein Beitrag zu dieser radar_uid.', 'tamil-radar' ), array( 'status' => 404 ) );
	}
	if ( ! current_user_can( 'edit_post', $post_id ) ) {
		return new WP_Error( 'tamil_radar_forbidden', __( 'Dieser Beitrag darf nicht bearbeitet werden.', 'tamil-radar' ), array( 'status' => 403 ) );
	}
	$data = array( 'ID' => $post_id );
	foreach ( array(
		'titel'  => 'post_title',
		'inhalt' => 'post_content',
		'teaser' => 'post_excerpt',
	) as $param => $field ) {
		$value = $request->get_param( $param );
		if ( null !== $value && '' !== $value ) {
			$data[ $field ] = 'post_content' === $field ? wp_kses_post( (string) $value ) : (string) $value;
		}
	}
	$status = (string) $request->get_param( 'status' );
	if ( $status ) {
		$data['post_status'] = tamil_radar_allowed_status( $status );
	}
	if ( count( $data ) > 1 ) {
		$result = wp_update_post( wp_slash( $data ), true );
		if ( is_wp_error( $result ) ) {
			$result->add_data( array( 'status' => 500 ) );
			return $result;
		}
	}
	$kats = array_filter( array_merge( array( (string) $request->get_param( 'kategorie' ) ), (array) $request->get_param( 'kategorien' ) ) );
	if ( $kats ) {
		wp_set_post_categories( $post_id, tamil_radar_resolve_categories( $kats ) );
	}
	$tags = array_filter( array_map( 'sanitize_text_field', (array) $request->get_param( 'schlagworte' ) ) );
	if ( $tags ) {
		wp_set_post_terms( $post_id, $tags, 'post_tag', false );
	}
	$bild = tamil_radar_apply_bild( $post_id, (array) $request->get_param( 'bild' ) );
	if ( is_wp_error( $bild ) ) {
		return $bild;
	}
	tamil_radar_apply_meta( $post_id, (array) $request->get_param( 'meta' ) );
	$seo = (array) $request->get_param( 'seo' );
	if ( $seo ) {
		tamil_radar_write_seo( $post_id, $seo );
	}
	return new WP_REST_Response( tamil_radar_beitrag_response( $post_id ) );
}

/**
 * Letzte veröffentlichte Beiträge der Redaktion (ohne Radar-Beiträge) als Stilbeispiele.
 */
function tamil_radar_rest_stil( WP_REST_Request $request ): WP_REST_Response {
	$posts = get_posts(
		array(
			'post_type'      => 'post',
			'post_status'    => 'publish',
			'posts_per_page' => (int) $request->get_param( 'n' ),
			'orderby'        => 'date',
			'meta_query'     => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
				'relation' => 'OR',
				array(
					'key'     => 'radar_uid',
					'compare' => 'NOT EXISTS',
				),
				array(
					'key'   => 'radar_uid',
					'value' => '',
				),
			),
		)
	);
	$out   = array();
	foreach ( $posts as $post ) {
		$text  = wp_strip_all_tags( strip_shortcodes( $post->post_content ), true );
		$out[] = array(
			'id'    => $post->ID,
			'title' => $post->post_title,
			'datum' => $post->post_date,
			'text'  => mb_substr( $text, 0, 2200 ),
		);
	}
	return new WP_REST_Response( $out );
}
