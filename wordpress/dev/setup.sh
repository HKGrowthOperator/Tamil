#!/usr/bin/env bash
# Lokales WordPress (PHP + SQLite, kein MySQL, kein Docker) zum Testen von Plugin und Theme.
# Alles landet außerhalb des Repos in $WP_DIR (Standard: $SCRATCH/tamil-wp bzw. /tmp/tamil-wp).
# Idempotent: erneut ausführen aktualisiert Symlinks, Kategorien und Aktivierung, lässt Daten stehen.
#
#   WP_DIR=… WP_PORT=8085 bash wordpress/dev/setup.sh
#   bash wordpress/dev/serve.sh &            # http://127.0.0.1:8085
#   Zugangsdaten (Admin, Anwendungspasswörter) in $WP_DIR/.env.local – nie ins Repo.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
WP_DIR="${WP_DIR:-${SCRATCH:-/tmp}/tamil-wp}"
DL_DIR="${WP_DL_DIR:-$WP_DIR-dl}"
PORT="${WP_PORT:-8085}"
URL="http://127.0.0.1:$PORT"
PHP_OPTS=()
[ -n "${CURL_CA_BUNDLE:-}" ] && PHP_OPTS+=(-d "curl.cainfo=$CURL_CA_BUNDLE" -d "openssl.cafile=$CURL_CA_BUNDLE")
WP=(php "${PHP_OPTS[@]}" "$WP_DIR/wp-cli.phar" "--path=$WP_DIR" --allow-root)
pw() { python3 -c "import secrets; print(secrets.token_urlsafe(14))"; }

mkdir -p "$WP_DIR" "$DL_DIR"
echo "== Downloads nach $DL_DIR"
[ -s "$DL_DIR/wp-cli.phar" ] || curl -fsSL -o "$DL_DIR/wp-cli.phar" https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
[ -s "$DL_DIR/wordpress.zip" ] || curl -fsSL -o "$DL_DIR/wordpress.zip" https://wordpress.org/latest.zip
[ -s "$DL_DIR/sqlite.zip" ] || curl -fsSL -o "$DL_DIR/sqlite.zip" https://downloads.wordpress.org/plugin/sqlite-database-integration.latest-stable.zip
cp "$DL_DIR/wp-cli.phar" "$WP_DIR/wp-cli.phar"

echo "== WordPress-Core"
if [ ! -f "$WP_DIR/wp-settings.php" ]; then
  tmp="$(mktemp -d)"
  unzip -q "$DL_DIR/wordpress.zip" -d "$tmp"
  cp -R "$tmp/wordpress/." "$WP_DIR/"
  rm -rf "$tmp"
fi
mkdir -p "$WP_DIR/wp-content/database" "$WP_DIR/wp-content/uploads" "$WP_DIR/wp-content/plugins" "$WP_DIR/wp-content/themes"

echo "== SQLite-Plugin + Drop-in"
PLUGIN_DIR="$WP_DIR/wp-content/plugins/sqlite-database-integration"
[ -d "$PLUGIN_DIR" ] || unzip -q "$DL_DIR/sqlite.zip" -d "$WP_DIR/wp-content/plugins/"
if ! grep -q '{SQLITE_IMPLEMENTATION_FOLDER_PATH}' "$PLUGIN_DIR/db.copy"; then
  echo "db.copy ohne die erwarteten Platzhalter – Plugin-Version prüfen (wp-content/db.php von Hand anlegen)."; exit 1
fi
sed -e "s#{SQLITE_IMPLEMENTATION_FOLDER_PATH}#$PLUGIN_DIR#" \
    -e "s#{SQLITE_PLUGIN}#sqlite-database-integration/load.php#" \
    "$PLUGIN_DIR/db.copy" > "$WP_DIR/wp-content/db.php"

echo "== wp-config.php"
if [ ! -f "$WP_DIR/wp-config.php" ]; then
  "${WP[@]}" config create --dbname=tamil --dbuser=tamil --dbpass=tamil --dbhost=localhost --skip-check --extra-php <<PHP
define( 'DB_DIR', __DIR__ . '/wp-content/database/' );
define( 'DB_FILE', 'tamil.sqlite' );
define( 'WP_ENVIRONMENT_TYPE', 'local' );
define( 'WP_DEBUG', true );
define( 'WP_DEBUG_LOG', true );
define( 'WP_DEBUG_DISPLAY', false );
define( 'WP_HOME', '$URL' );
define( 'WP_SITEURL', '$URL' );
define( 'DISABLE_WP_CRON', true );
define( 'FS_METHOD', 'direct' );
define( 'AUTOMATIC_UPDATER_DISABLED', true );
define( 'WP_AUTO_UPDATE_CORE', false );
PHP
fi

ENV_LOCAL="$WP_DIR/.env.local"
touch "$ENV_LOCAL"
setenv() { grep -q "^$1=" "$ENV_LOCAL" && sed -i "s|^$1=.*|$1=$2|" "$ENV_LOCAL" || echo "$1=$2" >> "$ENV_LOCAL"; }
getenv() { grep "^$1=" "$ENV_LOCAL" | head -1 | cut -d= -f2-; }

echo "== Installation"
if ! "${WP[@]}" core is-installed >/dev/null 2>&1; then
  ADMIN_PW="$(pw)"
  "${WP[@]}" core install --url="$URL" --title="Tamil.de (lokal)" --admin_user=admin \
    --admin_password="$ADMIN_PW" --admin_email=admin@example.test --skip-email
  setenv WP_ADMIN_USER admin
  setenv WP_ADMIN_PASSWORD "$ADMIN_PW"
fi
"${WP[@]}" option update timezone_string Europe/Berlin >/dev/null
"${WP[@]}" option update blogdescription "Nachrichten, Kino und Community" >/dev/null
"${WP[@]}" option update date_format "j. F Y" >/dev/null
"${WP[@]}" option update time_format "H:i" >/dev/null
"${WP[@]}" option update permalink_structure "/%postname%/" >/dev/null
"${WP[@]}" plugin activate sqlite-database-integration >/dev/null 2>&1 || true
( "${WP[@]}" language core install de_DE >/dev/null 2>&1 && "${WP[@]}" site switch-language de_DE >/dev/null 2>&1 ) \
  || echo "   (deutsche Sprachdateien nicht geladen – Backend bleibt Englisch)"

echo "== Plugin und Theme aus dem Repo"
if [ -d "$REPO/wordpress/plugins/tamil-radar" ]; then
  ln -sfn "$REPO/wordpress/plugins/tamil-radar" "$WP_DIR/wp-content/plugins/tamil-radar"
  "${WP[@]}" plugin activate tamil-radar
fi
if [ -d "$REPO/wordpress/themes/tamil" ]; then
  ln -sfn "$REPO/wordpress/themes/tamil" "$WP_DIR/wp-content/themes/tamil"
  "${WP[@]}" theme activate tamil
fi
"${WP[@]}" rewrite flush --hard >/dev/null 2>&1 || "${WP[@]}" rewrite flush >/dev/null

echo "== Kategorien aus sources.toml"
python3 - "$REPO/sources.toml" <<'EOF' | while IFS='|' read -r slug label; do
import sys, tomllib
raw = tomllib.loads(open(sys.argv[1], encoding="utf-8").read())
for slug, c in raw.get("categories", {}).items():
    print(f"{slug}|{c['label']}")
EOF
  "${WP[@]}" term get category "$slug" --by=slug --field=term_id >/dev/null 2>&1 \
    || "${WP[@]}" term create category "$label" --slug="$slug" >/dev/null
done
"${WP[@]}" option update default_category "$("${WP[@]}" term get category news --by=slug --field=term_id)" >/dev/null

echo "== Testdaten fürs Plugin (nur lokal: Weiterleitung, Werbeplatz)"
if "${WP[@]}" plugin is-active tamil-radar >/dev/null 2>&1; then
  "${WP[@]}" option update tamil_radar_redirects "{\"/category/anirudh/\":\"$URL/category/events/\",\"/category/blog/\":\"$URL/category/community/\"}" --format=json >/dev/null
  "${WP[@]}" option get tamil_radar_settings >/dev/null 2>&1 || "${WP[@]}" option update tamil_radar_settings \
    '{"cockpit_url":"http://127.0.0.1:8787","anzeigen":{"leaderboard":"<div class=\"ad-test\" style=\"background:#0e1226;color:#fff;padding:24px;text-align:center\">Testbanner Leaderboard</div>"},"advanced_ads":{}}' --format=json >/dev/null
fi

echo "== Benutzer und Anwendungspasswörter"
if ! "${WP[@]}" user get ki-agent >/dev/null 2>&1; then
  ROLE=radar
  "${WP[@]}" role list --field=role | grep -qx radar || ROLE=author
  "${WP[@]}" user create ki-agent ki-agent@example.test --role="$ROLE" --user_pass="$(pw)" --display_name="News-Radar" >/dev/null
fi
if [ -z "$(getenv WP_APP_PASSWORD)" ]; then
  setenv WP_APP_PASSWORD "$("${WP[@]}" user application-password create ki-agent radar --porcelain)"
fi
if [ -z "$(getenv WP_ADMIN_APP_PASSWORD)" ]; then
  setenv WP_ADMIN_APP_PASSWORD "$("${WP[@]}" user application-password create admin importer --porcelain)"
fi
setenv WP_URL "$URL"
setenv WP_USER ki-agent
setenv WP_POST_STATUS publish
setenv WP_TEST_URL "$URL"
setenv WP_TEST_USER ki-agent
setenv WP_TEST_APP_PASSWORD "$(getenv WP_APP_PASSWORD)"
chmod 600 "$ENV_LOCAL"

echo
echo "Fertig: $URL   (Version $("${WP[@]}" core version), PHP $(php -r 'echo PHP_VERSION;'))"
echo "  Starten:   bash wordpress/dev/serve.sh &"
echo "  Zugänge:   $ENV_LOCAL  (admin + Anwendungspasswörter)"
echo "  Radar:     set -a; . $ENV_LOCAL; set +a; python -m news_radar publish"
echo "  Reset:     rm $WP_DIR/wp-content/database/tamil.sqlite && bash wordpress/dev/setup.sh"
