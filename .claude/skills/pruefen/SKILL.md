---
name: pruefen
description: Die passenden Prüfungen für geänderte Bereiche ausführen und als Tabelle melden (pytest, Abnahme-Szenarien, WordPress-Lint, Screenshots ohne seitliches Scrollen). Auslösen vor jedem Commit oder Push, wenn „fertig“ gemeldet werden soll, oder aus /release.
allowed-tools: Bash(python -m pytest*), Bash(python -m news_radar abnahme*), Bash(bash wordpress/dev/lint.sh*), Bash(node tools/shots.mjs*), Bash(git diff*), Bash(git status*)
---

# Prüfen („Fertig heißt“)

1. Geänderte Bereiche bestimmen: `git status --short` und `git diff --name-only <basis>`.
2. Je Bereich prüfen:

| Geändert | Prüfung | Muss |
|---|---|---|
| `news_radar/**`, `sources.toml`, `tests/**`, `tools/*.py` | `python -m pytest -q` | alle grün (WordPress-Integrationstests dürfen ohne `WP_TEST_*` übersprungen sein) |
| `news_radar/workflow/**`, `news_radar/agents/**`, `news_radar/prompts/**` | zusätzlich `python -m news_radar abnahme` | 51/51 |
| `wordpress/**` | `bash wordpress/dev/lint.sh` (`PHPCS=0` nur, wenn Composer fehlt – dann sagen) | ohne Befund |
| Oberflächen (`design/**`, Theme, `news_radar/web/**`) | `node tools/shots.mjs <seiten> --out <scratch>/shots` | 0 Fehler (kein seitliches Scrollen, keine Konsolenfehler, keine leeren Bilder) |
| `Dockerfile`, `wordpress/Dockerfile` | Build lokal, falls Docker verfügbar; sonst sagen, dass nicht gebaut wurde | Image startet, Healthcheck grün |

3. Melden als Tabelle: Bereich · Prüfung · Ergebnis · Anmerkung. Nichts „grün“ nennen, was nicht gelaufen ist.

## Stolperfallen

- pytest aus dem Repo-Root starten.
- Screenshots: lokale Dateien vom Repo-Root aus angeben, damit relative Bildpfade stimmen.
- Hinweise aus `shots.mjs` (kleine Tippflächen, fehlende Schriften, Tamil ohne `lang`) sind keine Fehler, gehören aber
  in den Bericht.
