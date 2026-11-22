---
description: Die nach Tor G2 gewählte Richtung zur vollständigen Probeseite ausbauen (Start, Artikel, Rubrik, Events, Kinoliste, Kontakt), mit Kritik und QA, als Artifact für Tor G3.
argument-hint: "<slug>"
allowed-tools: Agent, Read, Write, Glob, Grep, Bash(node tools/shots.mjs*), Bash(git *), AskUserQuestion
---

# /design-ausbau <slug>

## Ausführungsvertrag

- Nur mit Tor G2: Die jüngste Abnahme `docs/abnahme/*-G2*.md` nennt `<slug>` als vom Auftraggeber gewählt. Eine
  abgelehnte oder nur vorgelegte Runde zählt nicht. Sonst stoppen.
- Die Hauptsitzung gestaltet nicht selbst; Kritik und QA kommen aus frischen Agents.
- Höchstens zwei Runden Kritik/QA; danach gilt, was die harten Kriterien des Briefs erfüllt und kein offenes P0
  oder P1 hat, oder Luis entscheidet.

## Schritte

1. Änderungswünsche aus G2 und `design/kritik/<slug>-r*.md` sammeln.
2. `art-director` mit Umfang „Probeseite“: Seiten nach `design/richtungen/<slug>/seiten/` (start, artikel, rubrik,
   events, kinoliste, kontakt), Änderungswünsche als Pflichtliste. Dazu die Seitentypen aus dem Vertrag
   (`docs/vertrag/leistungen.md`), damit der Auftraggeber alles in einem Durchgang abnimmt: verzeichnis (Liste mit
   Filtern und Profil), einreichen (Formular und Danke-Seite), werben (Preisseite, Buchung, Kundenübersicht),
   Cookie-Hinweis, Textseite (Impressum). Felder und Abläufe stehen in den Festlegungen; Klassen der Bauteile aus den
   Plugins (`tf-`, `vz-`, `wb-`) verwenden.
3. Parallel `design-kritiker` (Ausgabe `design/kritik/<slug>-ausbau-r1.md`) und `qa-pruefer`.
4. P0/P1 → `art-director` behebt (Runde 2) → erneut Kritik und QA.
5. Artifact veröffentlichen (Seiten als Dateien, Navigation zwischen ihnen), Link an Luis.
6. Commit `feat(design): Probeseite <slug>`, Push. Auf **Tor G3** warten; Urteil nach `docs/abnahme/<datum>-G3.md`.
