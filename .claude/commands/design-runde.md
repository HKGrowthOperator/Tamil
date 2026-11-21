---
description: Redesign-Runde für tamil.de – Brief und Vorbilder prüfen, drei Schnellproben parallel, Kennzahlen messen, Vorschau für Luis, gewählte Probe ausarbeiten und unabhängig prüfen, Vorlage für den Auftraggeber (Tor G2).
argument-hint: "[slugs, Standard: klar,blatt,bild]"
allowed-tools: Agent, Read, Write, Edit, Glob, Grep, Bash(node tools/shots.mjs*), Bash(node design/vergleich/aufnahmen.mjs*), Bash(python tools/bild_holen.py*), Bash(git *), AskUserQuestion, Skill, Artifact
---

# /design-runde

## Ausführungsvertrag

- Die Hauptsitzung **gestaltet nicht selbst**: kein HTML/CSS für Proben, keine Geschmacksurteile. Sie startet
  Agents, misst mit `aufnahmen.mjs` und baut Vorschau und Vorlage.
- **Luis sieht Schnellproben früh und ungefiltert** (interne Vorschau, als solche gekennzeichnet). **Der
  Auftraggeber** sieht nur, was Luis gewählt hat und was die unabhängige Prüfung bestanden hat.
- Jede Prüfung kommt aus einem **frischen** `design-kritiker`, der weder die Begründung des Gestalters noch frühere
  Kritiken bekommt. Er liefert Messwerte und Befunde, kein Urteil.
- **Durchgelassen wird**, was alle harten Kriterien des Briefs erfüllt und kein offenes P0 oder P1 hat. Das
  entscheidet die Hauptsitzung; eine Punktsumme ist kein Tor.
- Liefert ein Agent nichts Brauchbares (keine Dateien, Prüffehler): einmal mit konkretem Fehler neu beauftragen, dann
  als „nicht geliefert“ melden. Nicht selbst einspringen.

## Schritte

1. **Brief prüfen.** Liegt `design/brief.md` in der aktuellen Fassung vor? Bestätigt ist er, wenn es für diese
   Fassung eine Abnahme gibt (`docs/abnahme/*-G1-runde<n>.md`). Eine Arbeitsfassung reicht für Schnellproben, nicht
   für die Vorlage beim Auftraggeber.
2. **Vorbilder** aktuell? `design/referenzen/news-marken.md` mit Bildern und der Zeile „Spanne der Marken“. Sonst
   `referenz-scout` beauftragen (Startseiten bei 390 und 1280, vermessen).
3. **Material** vorhanden? `design/inhalte/inhalte.json` und die Bilder (`python tools/bild_holen.py`).
4. **Drei `art-director` parallel** (eine Nachricht), je mit `slug`, Variante aus dem Brief und Umfang
   „Schnellprobe“. Standard: `klar`, `blatt`, `bild`.
5. **Messen:** `node design/vergleich/aufnahmen.mjs <slugs>`. Verstößt eine Probe gegen ein hartes Kriterium, geht
   sie einmal mit dem Messwert zurück.
6. **Vorschau für Luis** (`design/vergleich/index.html` als privates Artifact, Vermerk „interne Vorschau, noch ohne
   Prüfung“): je Probe zwei Handy-Bildschirme und der erste Desktop-Bildschirm, Link zur klickbaren Probe und die
   Kennzahlen; daneben ein Vorbild und Runde 2 bei gleicher Breite. **Luis wählt** eine Probe oder eine Mischung
   (AskUserQuestion: was gefällt, was stört, „zu laut“ und „zu langweilig“ als Gegenpole, „würdest du es dem
   Auftraggeber zeigen?“). Mit der Wahl ist der Brief bestätigt: `docs/abnahme/<datum>-G1-runde<n>.md`.
7. **Ausarbeiten:** derselbe `art-director` mit Umfang „Skizze“ (Artikelkopf dazu) und den Anmerkungen von Luis.
8. **Prüfen:** ein frischer `design-kritiker` → `design/kritik/<slug>-r1.md`. Bei P0 oder P1: eine Überarbeitung,
   dann eine zweite frische Prüfung (`-r2.md`). Höchstens eine Überarbeitung.
9. **Vorlage für den Auftraggeber:** dieselbe Seite ohne den Vermerk „intern“ und ohne Punktzahlen, als Artifact.
   Luis bekommt den Link und teilt ihn. Was nicht bestanden hat, geht mit Grund nur an Luis.
10. **Commits** je Schritt (nur `design/` und `docs/abnahme/`), Push.
11. Auf **Tor G2** warten; Urteil nach `docs/abnahme/<datum>-G2-runde<n>.md`.
