---
description: Wartende Storys des Live-Radars im Agent-Modus schreiben oder begründet verwerfen und danach auswerten.
argument-hint: "[limit, Standard 5]"
allowed-tools: Agent, Read, Bash(python tools/radar_bericht.py*)
---

# /research [limit]

## Ausführungsvertrag

- Schreiben macht der `redakteur`; die Hauptsitzung schreibt keine Beiträge selbst.
- Tokens nie ausgeben, nur Datei- oder Variablennamen weitergeben.

## Schritte

1. Stand lesen: `python tools/radar_bericht.py` – gibt es offene Storys? Wenn nein: melden und stoppen.
2. `redakteur` beauftragen mit: Limit (Standard 5), Radar-Adresse, Ort des Agent-Tokens (Umgebungsvariable
   `RADAR_AGENT_TOKEN` oder Datei mit Rechten 600), Scratch-Ordner.
3. Danach erneut `python tools/radar_bericht.py` und mit der Tabelle des Redakteurs abgleichen.
4. Bericht an Luis: Tabelle Story · Ergebnis · Titel/Grund · Hinweise; was er im Cockpit freigeben kann.
