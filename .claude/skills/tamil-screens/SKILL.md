---
name: tamil-screens
description: Screenshots und Sichtprüfung für tamil.de bei 390, 820 und 1280 px – seitliches Scrollen, Konsolenfehler, leere Bilder, fehlende Schriften, kleine Tippflächen, Tamil ohne lang. Auslösen, wenn eine Seite, Skizze, das Theme oder das Cockpit angesehen, geprüft oder für eine Abnahme fotografiert werden soll.
allowed-tools: Bash(node tools/shots.mjs*)
---

# Screenshots und Sichtprüfung

```bash
# lokale Dateien (vom Repo-Root aus; ein eingebauter Server liefert sie aus, relative Bildpfade funktionieren)
node tools/shots.mjs design/richtungen/<slug>/index.html design/richtungen/<slug>/artikel.html \
     --out design/richtungen/<slug>/shots --kacheln
# URLs (Live-Seite, lokales WordPress auf :8085, Cockpit auf :8787)
node tools/shots.mjs https://tamil-web.167.233.76.202.sslip.io/ --out <scratch>/live
# Cockpit mit Anmeldung (Zugang aus SHOTS_USER / SHOTS_PASSWORD, nie ausgeben)
node tools/shots.mjs http://127.0.0.1:8787/ http://127.0.0.1:8787/entwurf/1 --login http://127.0.0.1:8787/login --out <scratch>/cockpit
```

Ergebnis: `<out>/<name>-<breite>.png` (ganze Seite), mit `--kacheln` zusätzlich `-k0.png …` (Ausschnitte zum
Ansehen), `<out>/bericht.json`. Rückgabewert 1 bei Fehlern.

## Ansehen

- Erst die Kacheln `-k0` (erster Bildschirm) bei 390 und 1280 lesen; das ist, was Leser und Auftraggeber zuerst sehen.
- Ganze Seiten nur zum Überblick; sie sind zu lang für Details.
- Fixierte Elemente (Leisten unten) erscheinen in Vollseiten mitten im Bild – das ist ein Aufnahme-Effekt.

## Bewerten

| Feld in `bericht.json` | Bedeutung | Stufe |
|---|---|---|
| `ueberlauf` | Pixel, um die die Seite seitlich scrollt | Fehler |
| `konsole` | Konsolenfehler, Seitenfehler, fehlgeschlagene Anfragen, HTTP ≥ 400 | Fehler |
| `bilder` | Bilder ohne Inhalt | Fehler |
| `schriften` | `@font-face`, die nicht geladen wurde | Hinweis (oft ein Pfadfehler) |
| `tippflaechen` | Links/Knöpfe < 44 px bei ≤ 820 px | Hinweis (Pflicht laut Marke: beheben) |
| `tamil_ohne_lang` | Textstellen mit Tamil-Zeichen ohne `lang="ta"` | Hinweis (beheben) |

## Stolperfallen

- Bilder mit `loading="lazy"` lädt das Werkzeug durch Scrollen; trotzdem leere Bilder heißen meist falscher Pfad.
- Externe Schriften/Skripte über das Netz können in der Sandbox scheitern → als Konsolenfehler sichtbar; lieber
  selbst hosten.
