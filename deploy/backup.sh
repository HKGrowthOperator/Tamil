#!/usr/bin/env bash
# Tägliches Backup der Warteschlange (WAL-sicher per sqlite3 .backup) und der Bilder; 14 Tage aufbewahren.
set -euo pipefail
APP=${APP:-/opt/tamil-news-radar}
DEST=${DEST:-$APP/backup}
mkdir -p "$DEST"
STAMP=$(date +%F)
sqlite3 "$APP/data/radar.sqlite" ".backup '$DEST/radar-$STAMP.sqlite'"
tar -czf "$DEST/bilder-$STAMP.tgz" -C "$APP/data" bilder 2>/dev/null || true
find "$DEST" -type f -mtime +14 -delete
