#!/usr/bin/env bash
# Start des Tamil.de-WordPress-Containers. Läuft bei jedem Start, ist idempotent:
#   1. Code (Core, Theme, Plugins) frisch aus dem Image nach /var/www/html – nur uploads/ und database/ bleiben
#   2. wp-config.php aus den Variablen; Salts einmalig erzeugt und im Datenbank-Volume aufbewahrt
#   3. Erstinstallation (nur wenn noch nicht installiert) und Grundeinrichtung (bis sie einmal durchgelaufen ist)
#   4. Jeder Start: Benutzer ki-agent, Anwendungspasswörter „radar“ (ki-agent) und „migration“ (Admin), Cockpit
#   5. Apache über das Entrypoint-Skript des offiziellen Images
#
# Variablen:
#   WP_URL_PUBLIC           öffentliche Adresse ohne / am Ende, z. B. https://tamil-web.…sslip.io
#                           (fehlt sie, gilt die erste Adresse aus COOLIFY_URL)
#   WP_ADMIN_PASSWORD       Pflicht bei der Erstinstallation; danach ändert der Container das Passwort nicht mehr
#   WP_ADMIN_USER           Standard luis
#   WP_ADMIN_EMAIL          Standard info@hkgrowth-operator.de
#   WP_TITLE                Standard Tamil.de
#   RADAR_APP_PASSWORD      gesetzt: ki-agent hat genau dieses Anwendungspasswort „radar“ (leer: unverändert)
#   MIGRATION_APP_PASSWORD  gesetzt: der Admin hat genau dieses Anwendungspasswort „migration“ (leer: wird entfernt)
#   RADAR_COCKPIT_URL       Adresse des Radar-Cockpits (Einstellung des Plugins tamil-radar)
#   WP_ENVIRONMENT_TYPE     Standard staging (production, staging, development, local)
set -euo pipefail

SRC=/usr/src/wordpress
DOCROOT=/var/www/html
DB_DIR="$DOCROOT/wp-content/database"
UP_DIR="$DOCROOT/wp-content/uploads"
HELFER=/opt/tamil/wp-helfer.php
MERKER_EINRICHTUNG="$DB_DIR/.grundeinrichtung-fertig"

log() { echo "[tamil-start] $*"; }
fehler() { echo "[tamil-start] FEHLER: $*" >&2; exit 1; }

# wp-cli immer als www-data (die SQLite-Datei muss Apache gehören), Cache nach /tmp
export WP_CLI_CACHE_DIR=/tmp/wp-cli-cache WP_CLI_DISABLE_AUTO_CHECK_UPDATE=1
wp() { runuser -u www-data -- /usr/local/bin/wp --path="$DOCROOT" "$@"; }

# --- Variablen prüfen ------------------------------------------------------------------------------------------------
WP_URL_PUBLIC="${WP_URL_PUBLIC:-${COOLIFY_URL:-}}"
WP_URL_PUBLIC="${WP_URL_PUBLIC%%,*}"
WP_URL_PUBLIC="${WP_URL_PUBLIC%/}"
[[ "$WP_URL_PUBLIC" =~ ^https?://[A-Za-z0-9.-]+(:[0-9]+)?(/[A-Za-z0-9._~-]+)*$ ]] \
  || fehler "WP_URL_PUBLIC fehlt oder ist keine http(s)-Adresse (z. B. https://tamil-web.example.org)."
export WP_ADMIN_USER="${WP_ADMIN_USER:-luis}"
[[ "$WP_ADMIN_USER" =~ ^[A-Za-z0-9._@-]+$ ]] || fehler "WP_ADMIN_USER enthält unzulässige Zeichen."
WP_ADMIN_EMAIL="${WP_ADMIN_EMAIL:-info@hkgrowth-operator.de}"
WP_TITLE="${WP_TITLE:-Tamil.de}"
WP_ENVIRONMENT_TYPE="${WP_ENVIRONMENT_TYPE:-staging}"
case "$WP_ENVIRONMENT_TYPE" in production|staging|development|local) ;; *) fehler "WP_ENVIRONMENT_TYPE ungültig." ;; esac

# --- 1. Code aus dem Image -------------------------------------------------------------------------------------------
# /var/www/html ist im offiziellen Image ein (anonymes) Volume und könnte alten Code vom letzten Deploy enthalten.
# Darum bei jedem Start abgleichen; --delete entfernt Reste alter Versionen. Daten-Volumes und wp-config bleiben.
log "Code abgleichen ($(sed -n "s/^\$wp_version = '\(.*\)';/\1/p" "$SRC/wp-includes/version.php"))"
rsync -a --delete \
  --exclude=/wp-config.php --exclude=/wp-config-docker.php \
  --exclude=/wp-content/uploads/ --exclude=/wp-content/database/ \
  "$SRC/" "$DOCROOT/"
mkdir -p "$DB_DIR" "$UP_DIR"
for d in "$DB_DIR" "$UP_DIR"; do
  mountpoint -q "$d" || log "WARNUNG: $d ist kein eigenes Volume – die Daten gehen beim nächsten Deploy verloren."
  # nur anpassen, was nicht schon www-data gehört (Coolify legt neue Volumes als root an)
  find "$d" \( ! -user www-data -o ! -group www-data \) -exec chown -h www-data:www-data {} +
done
chmod 0750 "$DB_DIR"

# --- 2. Salts und wp-config.php --------------------------------------------------------------------------------------
SALTS="$DB_DIR/.salts.php"
if [ ! -s "$SALTS" ]; then
  log "Salts erzeugen (einmalig, bleiben im Datenbank-Volume)"
  ( umask 077
    # shellcheck disable=SC2016  # PHP-Code, $k soll die Shell nicht ersetzen
    php -r 'echo "<?php\n// Einmalig von start.sh erzeugt – nicht weitergeben.\n";
      foreach (["AUTH_KEY","SECURE_AUTH_KEY","LOGGED_IN_KEY","NONCE_KEY","AUTH_SALT","SECURE_AUTH_SALT","LOGGED_IN_SALT","NONCE_SALT"] as $k) {
        echo "define( \x27$k\x27, \x27" . bin2hex(random_bytes(32)) . "\x27 );\n";
      }' > "$SALTS.neu"
    mv "$SALTS.neu" "$SALTS" )
fi
chown www-data:www-data "$SALTS"
chmod 0600 "$SALTS"

FORCE_SSL=false
[[ "$WP_URL_PUBLIC" == https://* ]] && FORCE_SSL=true
cat > "$DOCROOT/wp-config.php" <<PHP
<?php
// Von /opt/tamil/start.sh bei jedem Containerstart erzeugt – Änderungen hier gehen verloren.
define( 'DB_NAME', 'tamil' );
define( 'DB_USER', '' );
define( 'DB_PASSWORD', '' );
define( 'DB_HOST', 'localhost' );
define( 'DB_CHARSET', 'utf8mb4' );
define( 'DB_COLLATE', '' );
// SQLite (Plugin sqlite-database-integration, Drop-in wp-content/db.php) im Volume wp-content/database
define( 'DB_DIR', __DIR__ . '/wp-content/database/' );
define( 'DB_FILE', 'tamil.sqlite' );
require __DIR__ . '/wp-content/database/.salts.php';
\$table_prefix = 'wp_';

// Hinter Traefik endet TLS am Proxy: X-Forwarded-Proto zeigt, ob der Besucher HTTPS benutzt.
if ( isset( \$_SERVER['HTTP_X_FORWARDED_PROTO'] ) && str_contains( strtolower( (string) \$_SERVER['HTTP_X_FORWARDED_PROTO'] ), 'https' ) ) {
	\$_SERVER['HTTPS'] = 'on';
}
define( 'WP_HOME', '$WP_URL_PUBLIC' );
define( 'WP_SITEURL', '$WP_URL_PUBLIC' );
define( 'FORCE_SSL_ADMIN', $FORCE_SSL );
define( 'WP_ENVIRONMENT_TYPE', '$WP_ENVIRONMENT_TYPE' );

// Code kommt nur aus dem Image: keine Updates, kein Datei-Editor, keine Installationen im Backend
define( 'AUTOMATIC_UPDATER_DISABLED', true );
define( 'WP_AUTO_UPDATE_CORE', false );
define( 'DISALLOW_FILE_EDIT', true );
define( 'DISALLOW_FILE_MODS', true );
define( 'DISABLE_WP_CRON', false );
define( 'WP_DEBUG', false );
define( 'WP_DEBUG_DISPLAY', false );

if ( ! defined( 'ABSPATH' ) ) {
	define( 'ABSPATH', __DIR__ . '/' );
}
require_once ABSPATH . 'wp-settings.php';
PHP
chown root:www-data "$DOCROOT/wp-config.php"
chmod 0640 "$DOCROOT/wp-config.php"

# --- 3. Erstinstallation und Grundeinrichtung ------------------------------------------------------------------------
if ! wp core is-installed >/dev/null 2>&1; then
  [ -n "${WP_ADMIN_PASSWORD:-}" ] || fehler "WordPress ist noch nicht installiert und WP_ADMIN_PASSWORD fehlt."
  log "Erstinstallation: $WP_TITLE, Admin $WP_ADMIN_USER"
  # Wegwerf-Passwort für den Aufruf, das echte setzt der Helfer aus der Umgebung (steht so in keiner Befehlszeile)
  wp core install --url="$WP_URL_PUBLIC" --title="$WP_TITLE" --admin_user="$WP_ADMIN_USER" \
    --admin_email="$WP_ADMIN_EMAIL" --admin_password="$(head -c 32 /dev/urandom | base64 | tr -dc 'A-Za-z0-9')" \
    --skip-email
  wp eval-file "$HELFER" admin-passwort
  rm -f "$MERKER_EINRICHTUNG"
fi

if [ ! -f "$MERKER_EINRICHTUNG" ]; then
  log "Grundeinrichtung: Plugins, Theme, Einstellungen, Rubriken"
  wp plugin activate sqlite-database-integration tamil-site tamil-radar
  wp theme activate tamil
  wp option update timezone_string Europe/Berlin >/dev/null
  wp option update date_format "j. F Y" >/dev/null
  wp option update time_format "H:i" >/dev/null
  wp option update permalink_structure "/%postname%/" >/dev/null
  wp widget reset --all >/dev/null 2>&1 || true
  if [ -f "$DOCROOT/wp-content/languages/de_DE.mo" ]; then
    wp site switch-language de_DE >/dev/null || log "Sprache de_DE nicht aktiviert – Backend bleibt Englisch."
  else
    log "Keine deutschen Sprachdateien im Image – Backend bleibt Englisch."
  fi
  wp eval-file "$HELFER" einrichtung
  wp rewrite flush >/dev/null
  runuser -u www-data -- touch "$MERKER_EINRICHTUNG"
fi

# --- 4. Zugänge (jeder Start) ----------------------------------------------------------------------------------------
wp eval-file "$HELFER" zugaenge

# --- 5. Apache -------------------------------------------------------------------------------------------------------
# Geheimnisse nicht an Apache/PHP weiterreichen
unset WP_ADMIN_PASSWORD RADAR_APP_PASSWORD MIGRATION_APP_PASSWORD
log "WordPress bereit unter $WP_URL_PUBLIC – starte Apache"
exec docker-entrypoint.sh "$@"
