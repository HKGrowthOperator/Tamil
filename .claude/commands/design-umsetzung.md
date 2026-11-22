---
description: Nach Tor G3 das Design festschreiben (DESIGN.md, design/tokens.css) und Theme und Cockpit parallel umbauen, prüfen, zusammenführen und ausliefern.
allowed-tools: Agent, Read, Write, Edit, Glob, Grep, Bash(git *), Bash(node tools/shots.mjs*), Bash(python -m pytest*), Bash(bash wordpress/dev/lint.sh*), Skill
---

# /design-umsetzung

## Ausführungsvertrag

- Nur mit Tor G3 (`docs/abnahme/*-G3.md`). Sonst stoppen.
- Theme und Cockpit bauen Agents in eigenen Worktrees; die Hauptsitzung führt zusammen und liefert aus.
- Abweichungen von der Probeseite sind P1, außer sie sind begründet und von Luis akzeptiert.

## Schritte

1. **Festschreiben:** mit dem Skill `impeccable` (`document`, dann `extract`) aus der Probeseite
   `design/richtungen/<slug>/seiten/` eine neue `DESIGN.md` und `design/tokens.css` erzeugen; `PRODUCT.md` (Anti-Referenzen)
   ergänzen. Commit `docs(design): …`.
2. **Parallel** `theme-bauer` und `cockpit-bauer` (eine Nachricht, zwei Agent-Aufrufe), je mit Pfad der Probeseite und
   der Abnahme.
3. Ergebnisse (Worktree-Branches) in `claude/radar-multiagent` übernehmen (Merge, keine Force-Pushes); Konflikte lösen.
4. **Prüfen:** `qa-pruefer` auf lokalem WordPress und Cockpit; `design-kritiker` vergleicht Theme-Screens mit der
   Probeseite (`design/kritik/<slug>-umsetzung.md`).
5. Befunde an die Bau-Agents zurück (eine Runde), dann `/release`.
