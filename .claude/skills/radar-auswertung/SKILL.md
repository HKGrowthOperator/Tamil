---
name: radar-auswertung
description: Stand und Auswertung des Live-Radars lesen – Gesundheit, Budget, Warteschlange, Entwürfe mit Hinweisen, Kosten je Rolle und Modell. Auslösen bei „wie steht der Radar“, „Kosten“, „Pilot auswerten“, „was liegt im Cockpit“ oder aus /status und /research.
allowed-tools: Bash(python tools/radar_bericht.py*)
---

# Radar auswerten (nur lesen)

```bash
python tools/radar_bericht.py --token-datei <datei>      # oder RADAR_LESE_TOKEN in der Umgebung
python tools/radar_bericht.py --tage 30 --json > <scratch>/bericht.json   # Rohdaten für Tabellen
```

Liefert `/gesund` und `/api/bericht`: Budget (Tag/Monat, Stopp, Warnung), Warteschlange (offen, läuft, tot,
wartet_budget), Storys je Status, Entwürfe (Status, Typ, Titel, Termin, Hinweise), Kosten je Modell und Rolle.

## Was berichten

- **Kurzstand:** gesund ja/nein, Budget, offene/tote Jobs, neue Entwürfe seit dem letzten Bericht.
- **Pilot (mit Modellen):** Kosten je Artikel und je Rolle gegen die Schätzung 0,12–0,22 $, Gate-Quote („Recherche
  nötig“ / alle), Fehlversuche, Request-IDs für den Abgleich mit der Anthropic-Konsole.
- **Qualität:** je Entwurf die Hinweise (Länge, Quellenzeile, Copydesk) und ob Belege je Absatz vorhanden sind.

## Stolperfallen

- Der Token wird nie ausgegeben; Ausgaben dieses Werkzeugs enthalten ihn nicht.
- „freigegeben“ ohne gesetzte `WP_*`-Variablen heißt: nicht veröffentlicht (siehe `/website-live`).
- Ohne `ANTHROPIC_API_KEY` bleiben Recherche-Jobs „offen“; das ist kein Fehler (Tor B1).
