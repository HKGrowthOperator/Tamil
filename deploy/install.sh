#!/usr/bin/env bash
# Installation/Update auf einem Linux-Server (Debian/Ubuntu, systemd), als root aus dem Repo-Verzeichnis ausführen.
set -euo pipefail
APP=/opt/tamil-news-radar
command -v sqlite3 >/dev/null || apt-get install -y sqlite3
id newsradar >/dev/null 2>&1 || useradd --system --home "$APP" --shell /usr/sbin/nologin newsradar
mkdir -p "$APP/data/bilder" "$APP/backup"
rsync -a --delete --exclude '__pycache__' news_radar "$APP/"
cp sources.toml requirements.txt "$APP/"
[ -f "$APP/.env" ] || { cp .env.example "$APP/.env"; echo "Neue .env angelegt – bitte Schlüssel eintragen: $APP/.env"; }
[ -d "$APP/.venv" ] || python3 -m venv "$APP/.venv"
"$APP/.venv/bin/pip" install -q --upgrade pip
"$APP/.venv/bin/pip" install -q -r "$APP/requirements.txt"
cp deploy/backup.sh "$APP/backup.sh"
chown -R newsradar: "$APP"
chmod 600 "$APP/.env"
cp deploy/news-radar.service deploy/news-radar.timer deploy/news-radar-web.service \
   deploy/news-radar-digest.service deploy/news-radar-digest.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now news-radar.timer news-radar-digest.timer news-radar-web.service
systemctl restart news-radar-web.service
echo "0 3 * * * newsradar $APP/backup.sh" > /etc/cron.d/tamil-news-radar
echo
echo "Fertig."
echo "  Status:    systemctl list-timers 'news-radar*' ; systemctl status news-radar-web"
echo "  Logs:      journalctl -u news-radar -u news-radar-web -f"
echo "  App lokal: curl http://127.0.0.1:8787/gesund   (nach außen: deploy/cloudflared-ingress.yml)"
echo "  Erstbefüllung: sudo -u newsradar $APP/.venv/bin/python -m news_radar run --max-age-hours 336  (in $APP)"
