#!/usr/bin/env bash
# PHP-Prüfung für Theme und Plugins: Syntax (php -l) immer, WordPress-Coding-Standards (PHPCS), wenn installierbar.
#   bash wordpress/dev/lint.sh            # Syntax + PHPCS (falls Composer/Packagist erreichbar)
#   PHPCS=0 bash wordpress/dev/lint.sh    # nur Syntax
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
fehler=0
while IFS= read -r -d '' f; do
  out="$(php -l "$f" 2>&1)" || { echo "$out"; fehler=1; }
done < <(find "$ROOT/themes" "$ROOT/plugins" -name '*.php' -print0)
for f in "$ROOT"/themes/*/theme.json; do
  python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$f" || { echo "theme.json kaputt: $f"; fehler=1; }
done
[ "$fehler" = 0 ] && echo "php -l: alle Dateien ok"

if [ "${PHPCS:-1}" = 1 ]; then
  TOOLS="${PHPCS_DIR:-${TMPDIR:-/tmp}/tamil-phpcs}"
  if [ ! -x "$TOOLS/vendor/bin/phpcs" ] && command -v composer >/dev/null; then
    mkdir -p "$TOOLS"
    ( cd "$TOOLS" && composer -q init --name=tamil/phpcs --no-interaction >/dev/null 2>&1; \
      composer -q config allow-plugins.dealerdirect/phpcodesniffer-composer-installer true; \
      composer -q require --dev wp-coding-standards/wpcs:^3 phpcompatibility/phpcompatibility-wp:"*" >/dev/null 2>&1 ) \
      || echo "PHPCS nicht installierbar (Packagist nicht erreichbar) – übersprungen."
  fi
  if [ -x "$TOOLS/vendor/bin/phpcs" ]; then
    pfade="$(find "$TOOLS/vendor" -maxdepth 2 -mindepth 2 -type d \( -path '*wp-coding-standards/*' -o -path '*phpcsstandards/*' -o -path '*phpcompatibility/*' \) | paste -sd, -)"
    "$TOOLS/vendor/bin/phpcs" --runtime-set installed_paths "$pfade" --standard="$ROOT/.phpcs.xml.dist" -q \
      --report="${PHPCS_REPORT:-summary}" "$ROOT/themes" "$ROOT/plugins" || fehler=1
  fi
fi
exit "$fehler"
