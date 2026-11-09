#!/usr/bin/env bash
# Wiederherstellung eines Backup-Stands (als root): Dienste stoppen, Sicherung prüfen, zurückspielen, Dienste starten.
#   sudo deploy/restore.sh 2026-11-08
# Der vorherige Stand bleibt als data/radar.sqlite.vor-restore-<Zeit> und data/bilder.vor-restore-<Zeit> liegen.
set -euo pipefail
STAND=${1:?Stand angeben, z. B. 2026-11-08 (ls /opt/tamil-news-radar/backup)}
APP=${APP:-/opt/tamil-news-radar}
DEST=${DEST:-$APP/backup}
PY=${PY:-$APP/.venv/bin/python}
UNITS=(news-radar.timer news-radar-worker.service news-radar-web.service)
cd "$APP"
"$PY" -m news_radar sicherung pruefen --ziel "$DEST" --datum "$STAND"
if [ -z "${OHNE_SYSTEMCTL:-}" ]; then systemctl stop "${UNITS[@]}" || true; fi
"$PY" -m news_radar sicherung wiederherstellen --ziel "$DEST" --datum "$STAND"
if [ -z "${OHNE_SYSTEMCTL:-}" ]; then
  chown -R newsradar: "$APP/data"
  systemctl start news-radar-web.service news-radar.timer
  systemctl start news-radar-worker.service 2>/dev/null || true
  sleep 2
  curl -fsS http://127.0.0.1:8787/gesund && echo
fi
echo "Wiederhergestellt: Stand $STAND"
