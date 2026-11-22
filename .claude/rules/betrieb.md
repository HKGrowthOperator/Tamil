---
paths:
  - "Dockerfile"
  - "wordpress/Dockerfile"
  - "wordpress/docker/**"
  - "deploy/**"
  - "tools/coolify.py"
  - "docs/betrieb.md"
  - ".env.example"
---

# Regeln: Betrieb

- **Geheimnisse:** Werte nie ausgeben, nie in Dateien im Repo, nie in Docs. In Docs und `.env.example` stehen nur
  Namen. Zufallswerte erzeugt `tools/coolify.py` selbst und schreibt sie direkt in Coolify.
- **Coolify-Token** nur aus der Umgebungsvariable `COOLIFY_TOKEN`. Kein Token aus anderen Coolify-Apps lesen oder
  übernehmen.
- **Variablen** per `envs/bulk` mit `is_buildtime: false`, `is_runtime: true`, `is_literal: false`; nie `real_value`
  zurückschreiben (doppelte Anführungszeichen).
- **Images brauchen `curl`** für den Coolify-Healthcheck; der Radar-Container gibt nach dem Start die root-Rechte ab
  (`dienst.rechte_abgeben`).
- **Deploy nur nach „Fertig heißt“** (`CLAUDE.md`), dann `python tools/coolify.py deploy <uuid>` und Gesundheit prüfen
  (`/gesund`, Logs). Fehlgeschlagene Deploys nicht stehen lassen.
- **Volumes nie löschen** (Radar `/app/data`; Website `wp-content/uploads`, `wp-content/database`).
- **`deploy/`** ist die systemd-Alternative für einen eigenen Server; Coolify ist der Standard.
- Neue App-UUIDs, Domains und Variablennamen sofort in `docs/betrieb.md` eintragen.
