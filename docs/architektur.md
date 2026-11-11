# Architektur

Drei Systeme, ein Repo. Website und Radar sind getrennte Produkte; WordPress ist nur das Ziel der Veröffentlichung.

```
Quellen (RSS, WP-JSON, HTML, Kino-Anbieter, Google News)
   │  alle 3 Min. `python -m news_radar run` (im Dienst-Container)
   ▼
News-Radar ── Signal/Relevanz ─ Cluster ─ Story + Jobs (workflow_jobs, SQLite /app/data)
   │  Worker: research → gate → write → factcheck → copydesk → seo → media
   │  oder Agent-Modus: GET /api/agent/export → Claude-Sitzung schreibt → POST /api/agent/import
   ▼
Entwurf (Status „neu“) mit Claims, Belegen je Absatz, Kosten, Fassungen
   │  Mensch im Cockpit: prüfen, bearbeiten, „Freigeben“
   ▼
publisher.py ── REST (Anwendungspasswort ki-agent) ──► Plugin tamil-radar ──► WordPress-Beitrag
                                                        (WP_POST_STATUS=publish)
```

## News-Radar (`news_radar/`)

| Bereich | Dateien | Aufgabe |
|---|---|---|
| Einstieg | `__main__.py`, `dienst.py` | CLI; `dienst` startet im Container gunicorn, Worker und Zeitplan (Scan, Digest, Sicherung, Bildpool) |
| Quellen | `sources.py`, `kino_providers.py`, `net.py`, `quellencheck.py`, `sources.toml` | Abruf mit SSRF-Schutz (`net.safe_get`), ETag, Quellenregister |
| Auswahl | `filtering.py`, `dates.py` | Relevanz, DACH-Bezug, Ausland-Filter, Datumserkennung (auch tamilische Monate) |
| Redaktion v2 | `workflow/` (Jobs, Kosten, Budget, Provider, Orchestrator, Schema, Repo), `agents/` (relevance, cluster, research, factcheck, schreiben, copydesk, seo, media) | Rollen mit Belegen und Budget-Reservierung |
| Agent-Modus | `agent_v2.py`, `web/api.py` | Mappe exportieren, Texte mit denselben Gates importieren |
| Prompts | `prompts/*.md` | Prompt je Rolle als Markdown, Version = Hash des Inhalts |
| Bilder | `bilder.py`, `images.py`, `agents/media.py` | Reihenfolge Archiv → Quelle → Stock → Pool → KI → Karte, Lizenz je Bild |
| Veröffentlichen | `publisher.py`, `wordpress.py` | idempotent, `story_id` als Meta |
| Betrieb | `sicherung.py`, `notify.py`, `bewertung.py`, `abnahme/` | Backup/Restore, Digest, Blindbewertung, Abnahme-Szenarien |

## Cockpit (`news_radar/web/`)

Flask mit serverseitigen Sitzungen, Login-Drossel, CSRF, CSP ohne Inline-Script, nh3-Bereinigung. Seiten: Dashboard,
Feed, Entwurf (Claims, Belege, Fassungen, Kosten), Warteschlange, Recherche nötig, Quellen, Kosten, Protokoll, Nutzer.
API: `/api/bericht` (Lese-Token), `/api/agent/export|import` (Agent-Token), `/gesund`.

## Website (`wordpress/`)

- Theme `themes/tamil`: `theme.json` (Palette, Schriften, Größen), `assets/css/theme.css`, `template-parts/`,
  `inc/` (Setup, Enqueue, Customizer, Schema/JSON-LD, Queries).
- Plugin `plugins/tamil-radar`: REST-Endpunkte für den Radar, Meta, Medien, Rolle „Radar“, Weiterleitungen.
- Plugin `plugins/tamil-site`: Werbeplätze mit Eigenanzeigen, 301-Weiterleitungen, Termin-Felder.
- Container `Dockerfile` + `docker/start.sh`: WordPress 6 mit SQLite, Theme und Plugins frisch aus dem Image,
  persistent nur `uploads/` und `database/`.
- Lokal: `dev/` (setup, serve, import, lint, shots, package).

## Daten

- Radar: SQLite unter `$RADAR_DATA_DIR` (Container `/app/data`), Sicherungen in `/app/data/backup`.
- Website: SQLite im Volume `wp-content/database`, Medien im Volume `wp-content/uploads`.
- Altbestand von tamil.de: `tools/export_site.py` (nur lesen) → `prototyp/content/*.json` → Importer.
