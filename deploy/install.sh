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
cp deploy/restore.sh "$APP/restore.sh"
# Code, venv und Skripte gehören root (restore.sh läuft als root – das Dienstkonto darf es nicht ändern können);
# newsradar schreibt nur in data/ und backup/ und liest die .env
chown -R root:root "$APP"
chmod -R go-w "$APP"
chmod 755 "$APP/backup.sh" "$APP/restore.sh"
chown -R newsradar: "$APP/data" "$APP/backup"
chown root:newsradar "$APP/.env"
chmod 640 "$APP/.env"
cp deploy/news-radar.service deploy/news-radar.timer deploy/news-radar-web.service \
   deploy/news-radar-digest.service deploy/news-radar-digest.timer \
   deploy/news-radar-worker.service deploy/news-radar-bildpool.service deploy/news-radar-bildpool.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now news-radar.timer news-radar-digest.timer news-radar-web.service
systemctl restart news-radar-web.service
# Redaktion v2: Worker und Bildpool nur, wenn RADAR_WORKFLOW=v2 in der .env steht
if grep -q '^RADAR_WORKFLOW=v2' "$APP/.env"; then
  systemctl enable --now news-radar-worker.service news-radar-bildpool.timer
  systemctl restart news-radar-worker.service
fi
echo "0 3 * * * newsradar $APP/backup.sh" > /etc/cron.d/tamil-news-radar
echo
echo "Fertig."
echo "  Status:    systemctl list-timers 'news-radar*' ; systemctl status news-radar-web"
echo "  Logs:      journalctl -u news-radar -u news-radar-web -u news-radar-worker -f"
echo "  Kosten:    sudo -u newsradar $APP/.venv/bin/python -m news_radar kosten   (in $APP)"
echo "  Restore:   sudo $APP/restore.sh YYYY-MM-DD   (Stände: ls $APP/backup)"
echo "  App lokal: curl http://127.0.0.1:8787/gesund   (nach außen: deploy/cloudflared-ingress.yml)"
echo "  Erstbefüllung: sudo -u newsradar $APP/.venv/bin/python -m news_radar run --max-age-hours 336  (in $APP)"
