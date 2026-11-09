# Betrieb

Alles läuft in **Coolify v4** auf dem Server 167.233.76.202. Hier stehen nur Namen, Pfade und Abläufe, **keine Werte**:
Passwörter, Tokens und Schlüssel liegen ausschließlich in den Coolify-Variablen der jeweiligen App.

## Coolify

| | |
|---|---|
| Oberfläche / API | `https://coolify.167.233.76.202.sslip.io` · API `…/api/v1` |
| Quelle | GitHub-App-Source `52`, Repo `HKGrowthOperator/Tamil`, Branch `claude/radar-multiagent` (nach dem Merge von PR #2: `main`) |
| API-Token | nur als Umgebungsvariable `COOLIFY_TOKEN` in der Shell, nie in Dateien oder Ausgaben. Der eingefügte Root-Token ist zu widerrufen (Tor B2) und durch ein eng gefasstes Token zu ersetzen |
| Werkzeug | `tools/coolify.py` (Status, Deploy und Warten, Logs, Variablen setzen ohne Ausgabe, Volumes) |

### App „tamil.de“ – News-Radar und Cockpit

| | |
|---|---|
| UUID | `igq37g4vbxzhw5u19efuk9ip` |
| Domain | `https://tamil.hk-growthoperator.de` (DNS A → 167.233.76.202, Let's Encrypt) |
| Build | `Dockerfile` im Repo-Root, Port 3000, Healthcheck `GET /gesund` (curl im Image) |
| Prozess | `python -m news_radar dienst` (gunicorn, Worker, Scan alle 3 Min., Digest 08:00, Sicherung 03:00) |
| Volume | `/app/data` (SQLite, Bilder, `backup/`) |
| Variablen (gesetzt) | `RADAR_WORKFLOW`, `RADAR_BUDGET_TAG_USD`, `RADAR_BUDGET_MONAT_USD`, `RADAR_ENTWUERFE_TAG`, `RADAR_KI_BILDER_JE_ARTIKEL`, `RADAR_PROXY_HOPS`, `RADAR_WEB_URL`, `WEB_USER`, `WEB_PASSWORD`, `WEB_SECRET`, `RADAR_LESE_TOKEN`, `RADAR_AGENT_TOKEN` |
| Variablen (offen) | `ANTHROPIC_API_KEY` (Tor B1, trägt Luis ein) · `WP_URL`, `WP_USER`, `WP_APP_PASSWORD`, `WP_POST_STATUS=publish` (nach `/website-live`) |
| Lesezugriff | `GET /api/bericht` mit `Authorization: Bearer $RADAR_LESE_TOKEN` |
| Agent-Modus | `GET /api/agent/export`, `POST /api/agent/import` mit `Bearer $RADAR_AGENT_TOKEN` |

### App „tamil-web“ – Website (WordPress)

| | |
|---|---|
| UUID | wird bei `/website-live` angelegt und hier eingetragen |
| Domain | `https://tamil-web.167.233.76.202.sslip.io` (vorerst; eigene Subdomain später) |
| Build | `wordpress/Dockerfile`, Build-Kontext Repo-Root, Port 80, Healthcheck `/wp-login.php` |
| Volumes | `/var/www/html/wp-content/uploads`, `/var/www/html/wp-content/database` |
| Variablen | `WP_URL_PUBLIC`, `WP_ADMIN_USER` (luis), `WP_ADMIN_PASSWORD`, `RADAR_APP_PASSWORD` (= `WP_APP_PASSWORD` im Radar), `MIGRATION_APP_PASSWORD`, `RADAR_COCKPIT_URL`, optional `WP_ENVIRONMENT_TYPE` |
| Start | `wordpress/docker/start.sh`: Code frisch aus dem Image, wp-config aus Variablen, Erstinstallation, Nutzer `ki-agent` mit Anwendungspasswort |

## Deploy

1. Lokal fertig nach `CLAUDE.md` („Fertig heißt“), Push auf den Branch.
2. `python tools/coolify.py deploy <uuid>` startet den Deploy und wartet bis `finished` oder `failed`, zeigt die
   letzten Log-Zeilen.
3. Prüfen: Radar `curl -fsS https://tamil.hk-growthoperator.de/gesund`; Website `curl -fsSI <domain>/`.
4. Bei Fehler: Logs lesen, beheben, erneut. **Rollback:** in Coolify den letzten grünen Deploy erneut ausrollen
   (Deployments → Redeploy) oder den fehlerhaften Commit per PR zurücknehmen.

## Variablen setzen (Stolperfallen)

- `PATCH /applications/{uuid}/envs/bulk` mit `is_buildtime: false`, `is_runtime: true`, `is_literal: false`.
  Buildtime-Variablen landen sonst im Image.
- Werte nie aus `real_value` zurückschreiben: Der ist schon gequotet, das führte zu doppelten Anführungszeichen und
  einem `.env`-Parse-Fehler.
- Zufallswerte (Passwörter, Tokens) erzeugt das Werkzeug selbst und gibt sie nie aus. Luis liest sie in Coolify nach.
- Ohne `curl` im Image rollt Coolify jeden Deploy über den Healthcheck zurück.

## Sicherung und Wiederherstellung

- Radar: täglich 03:00 `python -m news_radar sicherung erstellen --ziel /app/data/backup`; wiederherstellen per
  „Execute command“ mit `python -m news_radar sicherung wiederherstellen <stand>` (prüft Integrität vorher).
- Website: beide Volumes in Coolify sichern (Backups der Persistent Storages).
- systemd-Variante (HK-Server, nur Alternative): `deploy/install.sh`, `deploy/restore.sh`.

## Kosten

Radar-Budget im Pilot: 2 $ pro Tag und 2 $ pro Monat, harter Stopp für neue bezahlte Jobs, Freigabe läuft weiter.
Stand: `/gesund` oder `/api/bericht` → `budget`.
