<?php
/**
 * Kopf in drei Teilen wie klar2: Kopfzeile (Datum, ab 800 px die Hinweise „Diese Woche“, Suche), Logo auf hellem
 * Grund und das dunkle Rubrikband als eigenes <nav>. Im Band rechts „Mehr“ mit Suche, Diensten und Social.
 */

defined( 'ABSPATH' ) || exit;

$tamil_items    = tamil_nav_items();
$tamil_dienste  = tamil_dienste();
$tamil_social   = tamil_social();
$tamil_hinweise = tamil_kopf_hinweise();
$tamil_lupe     = '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false"><circle cx="6.8" cy="6.8" r="5" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M10.6 10.6 14.5 14.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>';
?>
<header class="kopf">
	<div class="kopfzeile">
		<div class="innen kopfzeile__innen">
			<time class="kopfzeile__datum" datetime="<?php echo esc_attr( wp_date( 'Y-m-d' ) ); ?>"><?php echo esc_html( tamil_heute() ); ?></time>
			<?php if ( $tamil_hinweise ) : ?>
				<p class="kopfzeile__hinweise"><strong><?php esc_html_e( 'Diese Woche', 'tamil' ); ?></strong>
					<?php foreach ( $tamil_hinweise as $tamil_h ) : ?>
						<a href="<?php echo esc_url( $tamil_h['url'] ); ?>"><?php echo esc_html( $tamil_h['text'] ); ?></a>
					<?php endforeach; ?>
				</p>
			<?php endif; ?>
			<a class="kopfzeile__suche" href="<?php echo esc_url( add_query_arg( 's', '', home_url( '/' ) ) ); ?>"><?php echo $tamil_lupe; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- festes SVG ?><?php esc_html_e( 'Suche', 'tamil' ); ?></a>
		</div>
	</div>
	<div class="innen">
		<?php get_template_part( 'template-parts/header/logo', null, array( 'class' => 'kopf__logo' ) ); ?>
	</div>
</header>
<nav class="band" aria-label="<?php esc_attr_e( 'Rubriken', 'tamil' ); ?>">
	<div class="band__innen">
		<ul class="band__liste">
			<?php foreach ( $tamil_items as $tamil_item ) : ?>
				<li><a href="<?php echo esc_url( $tamil_item['url'] ); ?>"<?php echo $tamil_item['aktiv'] ? ' aria-current="page"' : ''; ?>><?php echo esc_html( $tamil_item['label'] ); ?></a></li>
			<?php endforeach; ?>
		</ul>
		<details class="mehr">
			<summary><?php esc_html_e( 'Mehr', 'tamil' ); ?></summary>
			<div class="mehr__paneel">
				<form class="suchfeld" role="search" method="get" action="<?php echo esc_url( home_url( '/' ) ); ?>">
					<label class="nur-vorlesen" for="mehr-suche"><?php esc_html_e( 'Suchbegriff', 'tamil' ); ?></label>
					<input id="mehr-suche" type="search" name="s" value="<?php echo esc_attr( get_search_query() ); ?>" placeholder="<?php esc_attr_e( 'Film, Stadt, Fest', 'tamil' ); ?>">
					<button type="submit" class="knopf"><?php esc_html_e( 'Suchen', 'tamil' ); ?></button>
				</form>
				<div class="mehr__spalten">
					<div>
						<h2 class="mehr__titel"><?php esc_html_e( 'Dienste', 'tamil' ); ?></h2>
						<ul>
							<?php foreach ( $tamil_dienste as $tamil_d ) : ?>
								<li><a href="<?php echo esc_url( $tamil_d['url'] ); ?>"<?php echo $tamil_d['aktiv'] ? ' aria-current="page"' : ''; ?>><?php echo esc_html( $tamil_d['label'] ); ?></a></li>
							<?php endforeach; ?>
						</ul>
					</div>
					<?php if ( $tamil_social ) : ?>
						<div>
							<h2 class="mehr__titel"><?php esc_html_e( 'Folgen', 'tamil' ); ?></h2>
							<ul>
								<?php foreach ( $tamil_social as $tamil_s ) : ?>
									<li><a href="<?php echo esc_url( $tamil_s['url'] ); ?>" target="_blank" rel="noopener"><?php echo esc_html( $tamil_s['name'] ); ?></a></li>
								<?php endforeach; ?>
							</ul>
						</div>
					<?php endif; ?>
				</div>
			</div>
		</details>
	</div>
</nav>
