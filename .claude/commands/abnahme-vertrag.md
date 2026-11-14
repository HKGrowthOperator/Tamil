---
description: Die sieben Abnahmetests aus dem Vertrag (B5) automatisch ausführen und das Abnahmeprotokoll mit den Handtests für das Testsystem schreiben.
argument-hint: "[T1 … T7]"
allowed-tools: Agent, Read, Write, Edit, Glob, Grep, Bash(python -m pytest*), Bash(python -m news_radar abnahme*), Bash(node tools/shots.mjs*), Bash(curl -fsS*), Bash(git *), Skill
---

# /abnahme-vertrag [T1 … T7]

## Ausführungsvertrag

- Maßstab ist die Tabelle „Abnahmetests (B5)“ in `docs/vertrag/leistungen.md`. Kein Test gilt als bestanden, der
  nicht gelaufen ist; was auf Zuarbeit wartet (Konten, Schlüssel), steht als „wartet“ im Protokoll.
- Echte Veröffentlichungen, echte Zahlungen und Schalter im Echtbetrieb löst dieser Command nicht aus. Handtests
  beschreibt er Schritt für Schritt; ausgeführt werden sie von Luis oder KBS auf dem Testsystem.
- Das Protokoll enthält keine Geheimnisse und keine Personendaten.

## Schritte

1. Automatische Tests je Zeile ausführen (pytest-Dateien und Abnahme-Szenarien aus der Tabelle); Ergebnis je Test.
2. Für jede neue Seite Screenshots bei 390, 820 und 1280 (`node tools/shots.mjs`).
3. `docs/abnahme/<datum>-B5.md` schreiben: je Test Vertragstext, automatisches Ergebnis, Handtest als nummerierte
   Schritte mit erwartetem Ergebnis, Feld für Urteil und Datum.
4. Stand in `docs/vertrag/leistungen.md` nachtragen; Bericht an Luis: bestanden, offen, wartet.
