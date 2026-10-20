<?php
/**
 * Deinstallation: Einstellungen und Weiterleitungen entfernen – Beiträge und ihre Meta-Felder bleiben erhalten.
 */

defined( 'WP_UNINSTALL_PLUGIN' ) || exit;

delete_option( 'tamil_site_settings' );
delete_option( 'tamil_site_redirects' );
delete_option( 'tamil_site_redirects_csv' );
