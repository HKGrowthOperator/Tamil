---
name: coolify-betrieb
description: Coolify-Betrieb für tamil.de – Apps anlegen, Variablen setzen ohne Werte zu zeigen, Volumes, Deploy mit Warten und Gesundheitsprüfung, Rollback. Nur aufrufen, wenn ausdrücklich deployt oder eingerichtet werden soll (/release, /website-live).
disable-model-invocation: true
---

# Coolify-Betrieb

Werkzeug: `python tools/coolify.py` (Hilfe mit `--help`). Fakten (Apps, UUIDs, Domains, Volumes, Variablennamen):
[docs/betrieb.md](../../../docs/betrieb.md). Regeln: `.claude/rules/betrieb.md`.

## Voraussetzungen

- `COOLIFY_TOKEN` in der Umgebung (oder vom Sitzungs-Proxy eingesetzt). Fehlt er: Luis bitten, ein eng gefasstes
  Token anzulegen (Tor B2) – **nie** einen Token aus anderen Apps suchen oder übernehmen.
- Lokal fertig nach `CLAUDE.md` („Fertig heißt“), Branch gepusht.

## Abläufe

**Deploy:** `python tools/coolify.py deploy <uuid>` → wartet, zeigt Log-Ende, Rückgabe 0 nur bei `finished`. Danach
`curl -fsS https://tamil.hk-growthoperator.de/gesund` bzw. `curl -fsSI <website>/`.

**Variablen:** `python tools/coolify.py env-setzen <uuid> NAME=wert NAME=@zufall NAME=@datei:<pfad>` → nur Namen in der
Ausgabe; danach Redeploy. Gemeinsame Geheimnisse zweier Apps (z. B. `RADAR_APP_PASSWORD` der Website =
`WP_APP_PASSWORD` des Radars): einmal mit `@zufall` in eine Scratch-Datei (Rechte 600) erzeugen, dann in beide Apps
mit `@datei:`.

**Neue App (Website):** `python tools/coolify.py api POST /applications/private-github-app --json <spec.json>` mit
`project_uuid`, `server_uuid`, `environment_name`, `github_app_uuid` (Source 52), `git_repository`
`HKGrowthOperator/Tamil`, `git_branch`, `build_pack: dockerfile`, `dockerfile_location: /wordpress/Dockerfile`,
`ports_exposes: "80"`, `domains`. Fehlende UUIDs vorher per `api GET /projects`, `/servers`, `/github-apps` lesen.
Danach Volumes (`api POST /applications/<uuid>/storages`), Variablen, Deploy. Neue UUID sofort in `docs/betrieb.md`
und `tools/coolify.py` (`APPS`) eintragen.

**Rollback:** in Coolify den letzten grünen Deploy erneut ausrollen oder den fehlerhaften Commit per PR zurücknehmen;
nie Volumes löschen.

## Stolperfallen

- Variablen mit `is_buildtime: true` landen im Image; das Werkzeug setzt immer runtime.
- `real_value` ist schon gequotet – nie zurückschreiben.
- Healthcheck braucht `curl` im Image; sonst rollt Coolify zurück.
- Der Radar braucht `RADAR_PROXY_HOPS=1` hinter Traefik (echte Client-IP für die Login-Drossel).
