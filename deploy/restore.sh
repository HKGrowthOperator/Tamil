#!/usr/bin/env bash
# Wiederherstellung eines Backup-Stands (als root): alle Radar-Dienste stoppen, Sicherung prüfen, zurückspielen,
# Dienste wieder starten.
#   sudo /opt/tamil-news-radar/restore.sh 2026-11-08
# Der vorherige Stand bleibt als data/radar.sqlite.vor-restore-<Zeit> und data/bilder.vor-restore-<Zeit> liegen.
# Python läuft dabei als Dienstkonto newsradar, root führt nur systemctl aus (Code, venv und dieses Skript gehören root).
set -euo pipefail
STAND=${1:?Stand angeben, z. B. 2026-11-08 (ls /opt/tamil-news-radar/backup)}
[[ "$STAND" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || { echo "Stand muss YYYY-MM-DD sein" >&2; exit 2; }
APP=${APP:-/opt/tamil-news-radar}
DEST=${DEST:-$APP/backup}
PY=${PY:-$APP/.venv/bin/python}
# Timer zuerst (damit nichts neu startet), dann die Dienste – auch ein gerade laufender Scan oder Digest
UNITS=(news-radar.timer news-radar-digest.timer news-radar-bildpool.timer
       news-radar.service news-radar-digest.service news-radar-bildpool.service
       news-radar-worker.service news-radar-web.service)
als_dienst() { if [ -z "${OHNE_SYSTEMCTL:-}" ]; then runuser -u newsradar -- "$@"; else "$@"; fi; }
cd "$APP"
als_dienst "$PY" -m news_radar sicherung pruefen --ziel "$DEST" --datum "$STAND"
if [ -z "${OHNE_SYSTEMCTL:-}" ]; then
  VORHER=()
  for u in "${UNITS[@]}"; do
    if systemctl is-active --quiet "$u"; then VORHER+=("$u"); fi
    if systemctl cat "$u" >/dev/null 2>&1; then systemctl stop "$u"; fi
  done
  for u in "${UNITS[@]}"; do
    if systemctl is-active --quiet "$u"; then echo "Abbruch: $u läuft noch – nichts geändert" >&2; exit 1; fi
  done
fi
als_dienst "$PY" -m news_radar sicherung wiederherstellen --ziel "$DEST" --datum "$STAND"
if [ -z "${OHNE_SYSTEMCTL:-}" ]; then
  # Was vorher lief, läuft wieder (mindestens Cockpit und Scan-Timer); einmalige Dienste startet ihr Timer
  START=(news-radar-web.service news-radar.timer)
  for u in "${VORHER[@]}"; do
    case "$u" in *.timer|news-radar-worker.service|news-radar-web.service) START+=("$u");; esac
  done
  systemctl start $(printf '%s\n' "${START[@]}" | sort -u)
  sleep 2
  curl -fsS http://127.0.0.1:8787/gesund && echo
fi
echo "Wiederhergestellt: Stand $STAND"
