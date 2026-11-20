# Logo, Startseite „Text auf Bild“ und Punktbogen an jedem Beitrag (Luis, 19./20.11.2026)

- **Datum:** 19. und 20.11.2026, über Luis.
- **Gezeigt / gebaut:** Theme 3.6.0 auf `claude/klar2-ausbau` (lokal geprüft, noch nicht auf dem Testsystem).
- **Ergebnis:** Entscheidungen fest (unten). Umsetzung am 20.11. von Luis **freigegeben** (Antworten unten).

## Entscheidungen von Luis

| Thema | Entscheidung (sinngemäß, wie übermittelt) | Status |
|---|---|---|
| Punktbogen an jedem Post | 19.11.: „Den USP … soll auf jedem einzelnen Post zu sehen sein. Klein und dezent, aber auf jeden einzelnen Post.“ 20.11.: „auf jedem einzelnen Beitrag“ | fest |
| Startseite „Text auf Bild“ | Alle Posts der Startseite werden Bildkarten mit Überschrift im Foto wie der Aufmacher: Dachzeile „Rubrik \| Datum“ und Titel auf dem Verlauf. „Weitere Meldungen“ als Stapel kleiner Bildkarten 16:9; Nebenstücke, Küche, Rubrikblöcke und „Diese Woche“ ebenso. Rubrikkacheln bleiben. Bewegung D und Bilderpflicht bleiben. | fest |
| Neues Logo | Quelle `design/inhalte/logo-2026-11.webp`: „GENAU SO übernehmen, auch die Schreibweise“ („portal • lifestyle • entertainment“, „& KOMMUNITYPLATTFORM DER COMMUNITY“). Kein Neuzeichnen, kein Vektor-Nachbau. | fest |

Das neue Logo hebt für dieses Logo die Regel „Logo bleibt unverändert“ aus dem Branding-Handoff v1.1 auf
(`docs/entscheidungen.md`, 20.11.).

## Umsetzung im Theme 3.6.0 (zur Freigabe)

| Thema | Umsetzung |
|---|---|
| Punktbogen | `ecke.svg` (weiß) und `ecke-rot.svg` (Titan/Impact für helle Bildecken) unten rechts in jedem Beitragsbild, 13 % der Rahmenbreite, 20–56 px, von der Bildkante angeschnitten. Nicht an Rubrikkacheln, Leerzuständen, Seiten, Verzeichnis, Anzeigen, Logo. Bilderpflicht-Prüfung: 100 % der Beitragsbilder tragen ihn, ohne Text oder das Schild „Symbolbild“ zu überdecken. |
| Startseite | Bildkarten mit Titel im Foto; „Weitere Meldungen“ drei Karten 16:9 (Desktop neben dem Aufmacher, Handy/Tablet wischbar), Nebenstücke (Handy untereinander, Tablet 2 × 2, Desktop zu viert in 4:3 mit Vorspann), Rubrikblöcke (Handy wischbar), Küche und „Diese Woche“ mit Titel im Bild. Titel mobil 19–21 px, höchstens vier Zeilen; Kontrast der Schrift im Bild gemessen ≥ 5,9 : 1 (5-%-Quantil). |
| Logo | freigestellt (`design/inhalte/logo_freistellen.py`), Kopf 56 / 64 / 72 px, Fuß 56 px, WebP 1x/2x, `alt="tamil.de"`; Teilenbild, Theme-Vorschau und Social-Muster neu. Favicon und App-Icon „t.“ unverändert. |

**Vorlagebilder** (lokal, Testinhalte): Startseite 1280 und 390, Kopf 1280 und 390, drei Karten nah (2x), Artikel 1280.

## Freigabe (20.11.2026, im Chat)

Gezeigt: die Vorlagebilder oben (Theme 3.6.0, Stand `5b475a4`). Antworten von Luis (Auswahl im Chat):

| Frage | Antwort |
|---|---|
| Theme 3.6.0 freigeben, aufs Testsystem und Website-Dateien auf `main`? | „Freigeben“ |
| „Weitere Meldungen“: drei Bildkarten statt sechs Zeilen? | „Drei ist gut“ |
| Favicon und App-Icon „t.“ lassen oder aus dem neuen Logo ableiten? | „„t.“ lassen“ |

Weiter offen: Eine weiße Fassung des neuen Logos für Social-Karten (weiß auf Foto) liegt nicht vor.

## Nächster Schritt

Merge in `claude/radar-multiagent`, Deploy aufs Testsystem, Prüfung dort, danach Website-Dateien auf `main`.

## Nachtrag 20.11.: Jede Meldung als Karte (Theme 3.7.0)

- **Auftrag (Luis, wörtlich):** „auf jeder meldung tamil dots und schrift auf der karte tamil dots auchh auf der akrte“.
  Gemeint: Was auf der Startseite gilt, gilt überall, wo Beiträge angerissen werden. Live zu sehen war es auf
  `/category/kultur/` („Neu in der Rubrik“ und „Weitere Beiträge“ noch als Zeilen mit Daumenbild).
- **Umsetzung (Theme 3.7.0, `claude/klar2-ausbau`, lokal geprüft):**

| Ort | Vorher | Jetzt |
|---|---|---|
| Rubrik: „Neu in der Rubrik“ | vier Zeilen mit Daumenbild | drei Karten 16:9 als Stapel neben dem Aufmacher (Handy wischbar) |
| Rubrik: „Weitere Beiträge“, Suche, Archive, 404, Production, „Aus dem Kinojahr“ | Zeilen mit Daumenbild | Kartenraster: Desktop 3, Tablet 2, Handy 1 Spalte, Vorspann unter dem Bild |
| Termine: „Ab heute“, „Kommende Termine“, „Das Jahr“ | Bildkacheln mit Titel darunter, Zeilen | Karten, Datum des Termins in der Dachzeile, Ort und Eintritt darunter; Filter nach Land und Stadt bleiben |
| Kino: „Im Programm“ | Bildkacheln quer | Karten mit Titel im Bild |
| Artikel: „Weiterlesen“ | Nebenstücke mit Bild links | vier Karten (Desktop zu viert in 4:3, Tablet 2 × 2, Handy wischbar) |
| bleiben | – | Kinotabelle (Spielorte), Rubrikkacheln, Verzeichnis, Kopf, Fuß, Blättern |

- **Messung:** `bilder_pflicht.mjs` zählt jetzt auch den Titel im Bild: 450 von 450 Beitrags-Anreißern (100 %) bei
  390/820/1280, Punktbogen 480 von 480; Ausnahmen mit Namen (Rubrikkachel, Tabelle, Verzeichnis, Artikel). Kontrast der
  Schrift im Bild ≥ 5,57 : 1 (5-%-Quantil), höchstens vier Titelzeilen.
- **Vorlagebilder:** Rubrik, Suche und Artikelende mit „Weiterlesen“ je 1280 und 390, Kino-Rubrik und Termine.
- **Freigabe:** ausstehend.

