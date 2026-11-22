---
description: Einen Baustein aus dem Vertrag bauen (grundlage, einreichungen, verzeichnis, werbung, social) – nur mit bestätigter Festlegung; Bau-Agents in Worktrees, danach unabhängige Code-Prüfung, Prüfungen, Zusammenführen.
argument-hint: "<baustein>"
allowed-tools: Agent, Read, Edit, Write, Glob, Grep, Bash(git *), Bash(python -m pytest*), Bash(python -m news_radar abnahme*), Bash(bash wordpress/dev/lint.sh*), Bash(node tools/shots.mjs*), Skill, AskUserQuestion
---

# /vertrag-bau <baustein>

## Ausführungsvertrag

- Gebaut wird nur, was in `docs/vertrag/festlegung-<baustein>.md` steht, und nur, wenn `docs/abnahme/*-F*-<baustein>.md`
  das Ja von Luis festhält. Ausnahme: der technische Teil von `grundlage` (Upgrade-Routine, Register, Tests), der
  keine Geschäftsregel enthält.
- Die Hauptsitzung baut nicht selbst. Website-Teile baut `plugin-bauer`, Radar- und Cockpit-Teile `radar-entwickler`,
  beide in eigenen Worktrees und parallel, wenn sie keine gemeinsamen Dateien ändern.
- Regeln aus `.claude/rules/vertrag.md` gelten immer: kein Mailversand, nur offizielle Schnittstellen, jede
  automatische Ausführung prüft den Stopp-Schalter und schreibt Protokoll, neue Funktionen im Echtbetrieb aus.
- Kein Zusammenführen ohne grüne Prüfungen und ohne Durchsicht der Befunde des `code-pruefer` (frischer Kontext).
- Liefert ein Agent nichts Brauchbares, wird er einmal neu beauftragt; danach steht der Teil als „nicht geliefert“
  im Bericht.

## Schritte

1. Festlegung und Leistungsverzeichnis lesen; die Abnahmetests des Bausteins aus `docs/vertrag/leistungen.md` sind
   die Pflichtliste.
2. Aufträge schreiben: je Agent Ziel, Dateien, Schnittstelle zum anderen Teil (Route, Felder, Rechte), Tests, Grenzen.
3. Agents parallel starten. Abgaben lesen; Worktrees zusammenführen (Merge in `claude/radar-multiagent`).
4. Skill `pruefen` für alle geänderten Bereiche; bei Oberflächen `qa-pruefer`.
5. `code-pruefer` mit dem Diff des Bausteins; P0 und P1 beheben lassen, P2 und P3 abwägen und im PR nennen.
6. `docs/vertrag/leistungen.md` (Stand) und `docs/entscheidungen.md` nachtragen; `/release`.
7. Auf dem Testsystem zeigen: Adresse und die Handtests des Bausteins an Luis.
