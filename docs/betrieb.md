# Betrieb

Alles läuft in **Coolify v4** auf dem Server 167.233.76.202. Hier stehen nur Namen, Pfade und Abläufe, **keine Werte**:
Passwörter, Tokens und Schlüssel liegen ausschließlich in den Coolify-Variablen der jeweiligen App.

## Coolify

| | |
|---|---|
| Oberfläche / API | `https://coolify.167.233.76.202.sslip.io` · API `…/api/v1` |
| Quelle | GitHub-App-Source `52`, Repo `HKGrowthOperator/Tamil`, Branch `claude/radar-multiagent` (nach dem Merge von PR #2: `main`) |
| API-Token | nie in Dateien im Repo, Ausgaben oder Docs; `tools/coolify.py` liest ihn nur aus `COOLIFY_TOKEN`. **Stand 11.11.2026:** Die Einrichtung der Website lief auf Anweisung von Luis mit zwei Tokens, die er im Chat gezeigt hat („TAMIL“ nur lesen, „Forever“ mit Root-Rechten). Beide gelten als offengelegt und sind nach der Einrichtung zu widerrufen (Tor B2). **Zielzustand:** A-Eintrag `coolify.hk-growthoperator.de` auf den Coolify-Server, die Adresse in Coolify als Instanz-Adresse, ein Token mit den Rechten lesen, schreiben und deployen (kein Root), hinterlegt über das sichere Formular der Sitzung (es nimmt nur echte Hostnamen an, nicht die sslip-Adresse); dann `COOLIFY_URL=https://coolify.hk-growthoperator.de` und ein Platzhalter als `COOLIFY_TOKEN` |
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
| Variablen (seit 11.11.2026) | `WP_URL` (die Vorschau-Adresse der Website), `WP_USER` (`ki-agent`), `WP_APP_PASSWORD`, `WP_POST_STATUS` (`publish`): Freigegebenes erscheint beim nächsten Lauf auf der Website |
| Variablen (offen) | `ANTHROPIC_API_KEY` (Tor B1, trägt Luis ein) |
| Variablen (optional, Standard im Code) | `RADAR_EVENT_MAX_ALTER_TAGE` (30: Termin-Berichte, die laut Quelle älter sind und kein Datum in der Zukunft nennen, fallen im Vorfilter heraus; Laufnotiz `termin_veraltet`), `RADAR_NACHTRAG_TAG` (60: so viele Nachtrag-Entwürfe für den Rückblick nimmt der Radar am Tag an) |
| Lesezugriff | `GET /api/bericht` mit `Authorization: Bearer $RADAR_LESE_TOKEN` |
| Agent-Modus | `GET /api/agent/export`, `POST /api/agent/import` mit `Bearer $RADAR_AGENT_TOKEN`. Export: `?limit=N` (die ersten N offenen, höchstens 20) · `?ids=3,4,5` (genau diese Storys, soweit offen, in dieser Reihenfolge; höchstens 20, nur Ziffern, sonst 400) · `?nur=uebersicht` (nur Liste der offenen Storys ohne Dokumente und ohne Abruf, höchstens 200; Stopp-Schalter gilt). CLI: `agent export --v2 --ids 3,4,5` |
| Nachtrag (Rückblick) | `POST /api/agent/vorschlag?von=<name>` mit `Bearer $RADAR_AGENT_TOKEN`: höchstens fünf Vorschläge je Aufruf (Thema, Datum, ein bis sechs Quellen); der Radar ruft die Quellen selbst ab (HTML bis 3 MB; PDF bis 8 MB, Text mit pypdf, Titel aus den PDF-Metadaten; Anker `#page=N` = Text ab Seite N, höchstens 40 Seiten, der Anker bleibt im Link; verschlüsselte oder kaputte PDF werden mit Grund übersprungen; Seiten ohne lesbaren Text, aber mit JSON-LD vom Typ Movie/Event/ScreeningEvent/NewsArticle/Article: „Angaben der Seite (strukturierte Daten)“ aus den wörtlichen Werten). Größere Mengen: `python -m news_radar agent vorschlag --datei <json>` im Container |

### App „tamil-web“ – Website (WordPress)

| | |
|---|---|
| UUID | `exmew1h1b2tzc0csay3dzr2g` (angelegt am 11.11.2026; Projekt und Server wie der Radar) |
| Domain | `https://tamil-web.167.233.76.202.sslip.io` (Vorschau-Adresse und Testsystem nach §9 des Vertrags, bis die Domain tamil.de umgeschaltet wird, Tor B3) |
| Build | `wordpress/Dockerfile`, Build-Kontext Repo-Root, Port 80, Healthcheck `/wp-login.php` (Start 90 s, alle 10 s, 15 Versuche: der erste Start richtet WordPress ein) |
| Volumes | `…-tamil-web-uploads` → `/var/www/html/wp-content/uploads`, `…-tamil-web-database` → `/var/www/html/wp-content/database` |
| Variablen | `WP_URL_PUBLIC`, `WP_ADMIN_USER` (luis), `WP_ADMIN_PASSWORD`, `RADAR_APP_PASSWORD` (= `WP_APP_PASSWORD` im Radar), `RADAR_COCKPIT_URL`, optional `WP_ENVIRONMENT_TYPE`. `MIGRATION_APP_PASSWORD` nur für die Dauer einer Übernahme setzen; ohne die Variable entfernt der nächste Start das Anwendungspasswort „migration“ |
| Start | `wordpress/docker/start.sh`: Code frisch aus dem Image, wp-config aus Variablen, Erstinstallation, Nutzer `ki-agent` mit Anwendungspasswort |
| Inhalt | Altbestand übernommen am 11.11.2026 mit `tools/migration.py` (532 Beiträge, 7 Seiten, 1445 Medien, 25 Weiterleitungen); Prüfliste in `docs/abnahme/2026-11-11-uebernahme.md` |
| Anmeldung | `/wp-login.php`, Benutzer aus `WP_ADMIN_USER`; das Passwort liest Luis in Coolify bei den Variablen der App nach |
| Suchmaschinen | Solange `WP_ENVIRONMENT_TYPE` nicht `production` ist (Standard im Container: `staging`), sperrt das Plugin `tamil-site` die Website für Suchmaschinen (noindex, `robots.txt` mit `Disallow: /`, keine Sitemap). **Beim Livegang (Tor B3) `WP_ENVIRONMENT_TYPE=production` setzen**, sonst bleibt tamil.de unsichtbar |

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
