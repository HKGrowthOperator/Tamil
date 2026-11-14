---
description: Website tamil-web in Coolify einrichten oder aktualisieren, echten Altbestand migrieren, Radar verbinden (Freigabe veröffentlicht sofort), prüfen – Vorbereitung für Tor G4.
allowed-tools: Agent, Read, Write, Edit, Glob, Grep, Bash(python tools/coolify.py*), Bash(curl -fsS*), Bash(curl -fsSI*), Bash(node tools/shots.mjs*), Bash(git *), Skill, AskUserQuestion
---

# /website-live

## Ausführungsvertrag

- Braucht `COOLIFY_TOKEN` (eng gefasstes Token, Tor B2). Fehlt er: Luis bitten und stoppen; nie Tokens aus anderen
  Apps suchen.
- Geheimnisse entstehen mit `@zufall` direkt in Coolify oder in Scratch-Dateien (600) und werden nie ausgegeben.
- Die alte tamil.de wird nur gelesen.
- Jeder Schritt wird geprüft, bevor der nächste beginnt; bei Fehler stoppen und melden.

## Schritte

1. **App** (Skill `coolify-betrieb`): Gibt es „tamil-web“ schon (`docs/betrieb.md`)? Sonst anlegen
   (`wordpress/Dockerfile`, Port 80, Domain `https://tamil-web.167.233.76.202.sslip.io`, zwei Volumes,
   Healthcheck `/wp-login.php`). UUID in `docs/betrieb.md` und `tools/coolify.py` eintragen.
2. **Variablen:** `WP_URL_PUBLIC`, `WP_ADMIN_USER=luis`, `WP_ADMIN_PASSWORD=@zufall`, `RADAR_APP_PASSWORD` und
   `MIGRATION_APP_PASSWORD` aus Scratch-Dateien (`@datei:`), `RADAR_COCKPIT_URL=https://tamil.hk-growthoperator.de`.
3. **Deploy** und prüfen: `/` 200, `/wp-login.php` 200, REST `wp-json/tamil-radar/v1/status` mit dem
   Radar-Anwendungspasswort 200.
4. **Migration:** `migrator` mit Website-Adresse und Pfad der Migrations-Passwortdatei; Prüfliste zurück.
5. **Radar verbinden:** in der Radar-App `WP_URL`, `WP_USER=ki-agent`, `WP_APP_PASSWORD=@datei:<radar-passwort>`,
   `WP_POST_STATUS=publish` setzen, Radar-Deploy, `/gesund` prüfen. Bereits freigegebene Entwürfe: mit Luis klären, ob
   sie jetzt veröffentlicht werden sollen.
6. **Probe:** eine Freigabe im Cockpit erzeugt einen Beitrag auf der Website (Luis klickt oder bestätigt).
7. `node tools/shots.mjs` gegen Start, Rubrik, drei Artikel, Events, Kontakt der Live-Adresse.
8. Bericht an Luis mit Adressen, Login-Hinweis (Passwort in Coolify nachlesen), Prüfliste; `docs/betrieb.md` und
   `docs/entscheidungen.md` aktualisieren; Commit, Push. Tor G4 folgt mit dem neuen Theme.
