#!/usr/bin/env bash
# Installation auf einem Linux-Server (Debian/Ubuntu), als root ausführen.
set -euo pipefail
APP=/opt/tamil-news-radar
id newsradar >/dev/null 2>&1 || useradd --system --home "$APP" --shell /usr/sbin/nologin newsradar
mkdir -p "$APP"
cp -r news_radar sources.toml requirements.txt "$APP"/
[ -f "$APP/.env" ] || cp .env.example "$APP/.env"
python3 -m venv "$APP/.venv"
"$APP/.venv/bin/pip" install -q -r "$APP/requirements.txt"
chown -R newsradar: "$APP"
chmod 600 "$APP/.env"
cp deploy/news-radar.service deploy/news-radar.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now news-radar.timer
echo "Fertig. Zugangsdaten in $APP/.env eintragen, Status: systemctl list-timers news-radar.timer"
