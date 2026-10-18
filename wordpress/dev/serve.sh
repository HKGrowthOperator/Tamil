#!/usr/bin/env bash
# Lokales WordPress starten (nach wordpress/dev/setup.sh). Vordergrund; für den Hintergrund: `serve.sh &`.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WP_DIR="${WP_DIR:-${SCRATCH:-/tmp}/tamil-wp}"
PORT="${WP_PORT:-8085}"
[ -f "$WP_DIR/wp-config.php" ] || { echo "Kein WordPress in $WP_DIR – erst wordpress/dev/setup.sh ausführen."; exit 1; }
echo "WordPress: http://127.0.0.1:$PORT  (Admin: /wp-admin, Zugangsdaten in $WP_DIR/.env.local)"
exec env PHP_CLI_SERVER_WORKERS="${PHP_CLI_SERVER_WORKERS:-4}" \
  php -S "127.0.0.1:$PORT" -t "$WP_DIR" \
  -d post_max_size=64M -d upload_max_filesize=64M -d memory_limit=256M -d display_errors=0 \
  "$HERE/router.php"
