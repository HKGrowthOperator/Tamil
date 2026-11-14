---
description: Ausliefern – prüfen, unabhängiger Code-Review, Commits, Push, PR aktualisieren, Coolify-Deploy mit Warten, Gesundheit prüfen.
argument-hint: "[radar|website|beide]"
allowed-tools: Agent, Read, Edit, Glob, Grep, Bash(git *), Bash(python -m pytest*), Bash(python -m news_radar abnahme*), Bash(bash wordpress/dev/lint.sh*), Bash(python tools/coolify.py*), Bash(curl -fsS*), Bash(curl -fsSI*), Skill
---

# /release [radar|website|beide]

## Ausführungsvertrag

- Kein Push ohne grüne Prüfungen (`pruefen`) und ohne Durchsicht der Befunde des `code-pruefer`.
- Nie auf `main` pushen, nie force. Merge von PR #2 nur nach Tor G4 und auf Luis' Wort.
- Deploy nur, wenn der Push durch ist; ein fehlgeschlagener Deploy wird behoben oder zurückgerollt, nie stehen gelassen.

## Schritte

1. Skill `pruefen` für die geänderten Bereiche; rot → beheben (oder `radar-entwickler`/Bau-Agent beauftragen).
2. `code-pruefer` mit Basis `origin/main...HEAD`; P0/P1 beheben, P2/P3 abwägen und im PR nennen.
3. Commits je Bereich (`type(scope): …`, Attributionszeilen aus `CLAUDE.md`), Push auf `claude/radar-multiagent`.
4. PR #2 aktualisieren (Statusliste, Getestet, Offen für Luis).
5. Deploy der betroffenen App(s) mit `python tools/coolify.py deploy <uuid>` (Skill `coolify-betrieb`), dann
   Gesundheit: Radar `/gesund`, Website `/` und `/wp-login.php`.
6. Kurzbericht: was ausgeliefert, Prüfergebnis, Deploy-Status, offene Punkte.
