<?php
/**
 * Router für `php -S`: vorhandene Dateien und Verzeichnisse (wp-admin/, wp-content/) liefert der eingebaute
 * Server selbst aus, alles andere geht an WordPress – so funktionieren Permalinks und /wp-json/ ohne Apache.
 */
$path = parse_url( $_SERVER['REQUEST_URI'], PHP_URL_PATH );
$root = rtrim( $_SERVER['DOCUMENT_ROOT'], '/' );
$file = $root . $path;

if ( '/' !== $path && ( is_file( $file ) || is_file( rtrim( $file, '/' ) . '/index.php' ) ) ) {
	return false; // php -S bedient die Datei bzw. das Verzeichnis-Index selbst
}

$_SERVER['SCRIPT_NAME']     = '/index.php';
$_SERVER['SCRIPT_FILENAME'] = $root . '/index.php';
$_SERVER['PHP_SELF']        = '/index.php';
require $root . '/index.php';
