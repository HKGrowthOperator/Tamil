#!/usr/bin/env bash
# Tägliches Backup der Datenbank (WAL-sicher über die SQLite-Backup-API) und der Bilder; 14 Tage aufbewahren.
set -euo pipefail
APP=${APP:-/opt/tamil-news-radar}
DEST=${DEST:-$APP/backup}
cd "$APP"
"$APP/.venv/bin/python" -m news_radar sicherung erstellen --ziel "$DEST"
