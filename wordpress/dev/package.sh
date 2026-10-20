#!/usr/bin/env bash
# Installierbare Pakete bauen: wordpress/dist/{tamil,tamil-site,tamil-radar}.zip (Ordnername = Slug, wie WordPress es
# beim Hochladen erwartet). Versionsnummer aus dem Datei-Kopf, Prüfsumme daneben.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
DIST="$ROOT/dist"
mkdir -p "$DIST"
rm -f "$DIST"/*.zip "$DIST"/SHA256SUMS
pack() {  # $1 = Ordner (themes/tamil), $2 = Kopf-Datei für die Version
  local src="$ROOT/$1" name; name="$(basename "$1")"
  local version; version="$(grep -m1 -E '^\s*\*?\s*Version:' "$src/$2" | sed -E 's/.*Version:\s*//')"
  ( cd "$(dirname "$src")" && zip -qr "$DIST/$name.zip" "$name" -x "*/.DS_Store" "*/node_modules/*" "*/.git*" )
  echo "$name $version → dist/$name.zip ($(du -h "$DIST/$name.zip" | cut -f1))"
}
pack themes/tamil style.css
pack plugins/tamil-site tamil-site.php
pack plugins/tamil-radar tamil-radar.php
( cd "$DIST" && sha256sum ./*.zip > SHA256SUMS )
