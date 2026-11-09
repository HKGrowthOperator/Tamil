---
description: Redesign-Runde für tamil.de – Brief prüfen, Referenzen, vier Richtungen parallel skizzieren, unabhängig kritisieren, nur bestandene Richtungen als Vergleichsseite zeigen (Tor G2).
argument-hint: "[slugs, Standard: plakatwand,zine,raster,feed]"
allowed-tools: Agent, Read, Write, Glob, Grep, Bash(node tools/shots.mjs*), Bash(git *), AskUserQuestion, Skill
---

# /design-runde

## Ausführungsvertrag

- Die Hauptsitzung **gestaltet nicht selbst**: kein HTML/CSS für Richtungen, keine Bewertungen. Sie startet Agents,
  liest deren Ergebnisse, baut nur die Vergleichsseite.
- Jede Kritik kommt aus einem **frischen** `design-kritiker`, dem die Begründung des Gestalters nicht mitgegeben wird.
- Gezeigt wird nur, was die Schwelle besteht (≥ 28/40, Slop-Test bestanden, kein offenes P0/P1).
- Liefert ein Agent nichts Brauchbares (keine Dateien, Prüffehler): einmal mit konkretem Fehler neu beauftragen, dann
  die Richtung als „nicht geliefert“ melden. Nicht selbst einspringen.

## Schritte

1. **Tor G1 prüfen.** Gibt es `design/brief.md` und `docs/abnahme/*-G1.md`? Wenn nein: Brief mit dem Skill
   `impeccable` (`shape`) gemeinsam mit Luis erarbeiten (Fragen per AskUserQuestion), Referenzen aus
   `design/referenzen/README.md` und die Links des Auftraggebers einbeziehen, Brief nach `design/brief.md`, Luis
   bestätigen lassen, Abnahme nach `docs/abnahme/<datum>-G1.md`. **Ohne G1 stoppen.**
2. **Referenzen** aktuell? Sonst `referenz-scout` (Agent) mit den Richtungen beauftragen.
3. **Vier `art-director` parallel** (ein Nachricht, vier Agent-Aufrufe), je mit: `slug`, Richtung (aus dem Brief),
   Umfang „Skizze“, Runde 1, Pfad `design/richtungen/<slug>/`, die 1–2 Vorbilder aus den Referenzen. Standard-Slugs:
   `plakatwand` (Kollywood-Plakatwand), `zine` (Diaspora-Zine), `raster` (Raster + Tamil-Schrift), `feed` (Vertikaler
   Feed); G1 kann Richtungen streichen oder schärfen.
4. **Vier `design-kritiker` parallel**, je mit: Seiten der Richtung, `design/brief.md`, Ausgabe
   `design/kritik/<slug>-r1.md`. Keine Begründung, kein Bericht des Gestalters mitgeben.
5. **Überarbeiten:** Urteil „überarbeiten“ → derselbe Slug an einen `art-director` mit Verweis auf die Kritikdatei
   (Runde 2), danach erneut ein frischer `design-kritiker` (`-r2.md`). Höchstens eine Überarbeitung.
6. **Filtern:** „zeigen“ kommt auf die Vergleichsseite; „verwerfen“ oder nach Runde 2 unter der Schwelle → Liste für
   Luis mit Grund.
7. **Vergleichsseite** `design/vergleich/index.html`: je bestandener Richtung erster Bildschirm Handy und Desktop
   (Kacheln aus `shots/`), Link zur klickbaren Skizze, Vorbild, Idee in einem Satz, Punktzahl. Als Artifact
   veröffentlichen (Skizzen als Dateien mit), Luis den Link geben – privat, er teilt mit dem Auftraggeber.
8. **Commit** `feat(design): Richtungsskizzen Runde <n>` (nur `design/`), Push.
9. Auf **Tor G2** warten; Urteil in `docs/abnahme/<datum>-G2.md`.
