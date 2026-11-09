---
description: Die nach Tor G2 gewählte Richtung zur vollständigen Probeseite ausbauen (Start, Artikel, Rubrik, Events, Kinoliste, Kontakt), mit Kritik und QA, als Artifact für Tor G3.
argument-hint: "<slug>"
allowed-tools: Agent, Read, Write, Glob, Grep, Bash(node tools/shots.mjs*), Bash(git *), AskUserQuestion
---

# /design-ausbau <slug>

## Ausführungsvertrag

- Nur mit Tor G2 (`docs/abnahme/*-G2.md` nennt `<slug>`). Sonst stoppen.
- Die Hauptsitzung gestaltet nicht selbst; Kritik und QA kommen aus frischen Agents.
- Höchstens zwei Runden Kritik/QA; danach gilt, was die Schwelle besteht, oder Luis entscheidet.

## Schritte

1. Änderungswünsche aus G2 und `design/kritik/<slug>-r*.md` sammeln.
2. `art-director` mit Umfang „Probeseite“: Seiten nach `design/richtungen/<slug>/seiten/` (start, artikel, rubrik,
   events, kinoliste, kontakt), Änderungswünsche als Pflichtliste.
3. Parallel `design-kritiker` (Ausgabe `design/kritik/<slug>-ausbau-r1.md`) und `qa-pruefer`.
4. P0/P1 → `art-director` behebt (Runde 2) → erneut Kritik und QA.
5. Artifact veröffentlichen (Seiten als Dateien, Navigation zwischen ihnen), Link an Luis.
6. Commit `feat(design): Probeseite <slug>`, Push. Auf **Tor G3** warten; Urteil nach `docs/abnahme/<datum>-G3.md`.
