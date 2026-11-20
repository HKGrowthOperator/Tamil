# Logo, Startseite „Text auf Bild“ und Punktbogen an jedem Beitrag (Luis, 19./20.11.2026)

- **Datum:** 19. und 20.11.2026, über Luis.
- **Gezeigt / gebaut:** Theme 3.6.0 auf `claude/klar2-ausbau` (lokal geprüft, noch nicht auf dem Testsystem).
- **Ergebnis:** Entscheidungen fest (unten); die Umsetzung ist zur Freigabe vorgelegt, **Freigabe ausstehend**.

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

## Offene Fragen an Luis

- Favicon und App-Icon „t.“: so lassen oder aus dem neuen Logo ableiten?
- „Weitere Meldungen“: drei statt bisher sechs (drei Karten 16:9 sind so hoch wie der Aufmacher); die übrigen Beiträge
  stehen weiter unten in den Rubrikblöcken. Passt das?
- Eine weiße Fassung des neuen Logos für Social-Karten (weiß auf Foto) liegt nicht vor.

## Nächster Schritt

Freigabe der Vorlagebilder durch Luis, danach Merge und Deploy aufs Testsystem.
