# Feinschliff Theme 3.7.2 (20.11.2026, 18:20–20:00 Uhr)

- **Auftrag (Luis, 20.11., 18:20):** „Arbeite durch bis 20 Uhr, Feinigkeiten, alles korrigieren, einmal neu machen …
  mit Agents.“ Auslegung, im Plan freigegeben: ein frischer Prüfdurchgang über die ganze Website, danach alle Mängel
  korrigiert. Ausdrücklich kein neues Design, der Wow-Umbau wartet auf die Wahl von Luis.
- **Prüfung aus frischem Kontext, nur lesend:**
  - QA-Prüfer auf dem Testsystem 3.7.1: 15 Seitentypen, je 390/820/1280. Werkzeuge: `shots.mjs`, `bilder_pflicht`,
    axe, Lighthouse, Prüflisten aus den Skill-Repos `impeccable` (audit, polish) und `gstack` (qa, design-review).
  - Code-Prüfer: Diff `45b3108..ab57603`.
  - Ergebnis: 19 Befunde aus der QA (1 × P0, 3 × P1, 15 × P2), 8 aus dem Code (3 × P1, 5 × P2).
- **Umsetzung:**
  - Theme 3.7.2 auf `claude/klar2-ausbau` (`16b50ad`), Merge `79afa90` in `claude/radar-multiagent`.
  - Zweite Runde: Theme 3.7.3 (`9ba7de3`).

## Befunde und Stand

| Befund | Stand | Was |
|---|---|---|
| QA-01 (P0) Kinopolis-Logo als Bild der Jailer-2-Beiträge | an Nick | Datenfehler im Quellbeitrag: Bild und Nachweis „Filmplakat: via Kinopolis“ sind falsch. Die Bildkette zieht es über den Schritt „film“ in einen zweiten Beitrag. `docs/uebergabe/backend-nick.md` §6c |
| QA-02 (P1) Titel über Logo-Schrift unlesbar | an Nick | Folge von QA-01. Eine allgemeine Regel „kein Bild mit Schrift oder Logo“ wäre neu und braucht eine Entscheidung |
| QA-03 (P1) Meta-Beschreibungen zusammengeklebt | behoben | Plugin `tamil-site`, mit Test `test_seo.py::test_beschreibung_trennt_bloecke` |
| QA-04 (P1) einzelne Karte allein in einer Zeile (600–1023 px) | behoben | Eine allein stehende letzte Karte läuft über die volle Breite |
| QA-05 Silbentrennung in großen Bildtiteln | behoben | |
| QA-06 „Neu“-Zeile mit vergangenem Termin | behoben (3.7.2 und 3.7.3) | Vergangene Termine sind raus. Gekürzt wird serverseitig am Wortende |
| QA-07 Zukunftsform nach dem Termin | offen | Ein Hinweis „hat bereits stattgefunden“ wäre neue Funktion und neuer Text, Frage an Luis |
| QA-08 Quelle doppelt „Eventfrog CH“ | behoben im Theme, Ursache an Nick | Doppelte Namen bekommen „(2)“. Die Ursache liegt in den Radar-Inhalten |
| QA-09 doppelte Linie unter dem Infokasten | behoben | |
| QA-10 Teilen-Leiste unruhig | behoben | |
| QA-11 Kino-Stadtliste (Doppelte, Umbruch, fehlende Zahl) | offen | Daten und Kino-Logik, braucht eine eigene Runde mit Gegenprobe |
| QA-12 Vorspann endet auf „19.…“ | behoben | Kürzung an der Satzgrenze |
| QA-13 doppelte Meta-Beschreibungen | an Redaktion | Eigene Beschreibungen für Verzeichnis, Werben und Impressum sind Inhalt |
| QA-14 Artikel-Titel ohne „\| Tamil.de“ | behoben (3.7.3) | Plugin `tamil-site`: Zusatz bis 60 Zeichen. Test `test_seo_titel_mit_marke_und_laengenregel` mit Gegenprobe |
| QA-15 zwei H2 vor der H1 | behoben | |
| QA-16 Rubrikband ohne Auslauf links | behoben | |
| QA-17 Fuß bei 390 px | behoben (3.7.2 und 3.7.3) | Die weiße Fläche ist weg. „Folgen“ steht rechts unter „Dienste“ |
| QA-18 Eigenwerbung als „Anzeige“ beschriftet | Frage an Luis (F3) | unverändert |
| QA-19 Tippflächen, Rubrikbilder ohne `srcset` | behoben (3.7.3) | Bildnachweis-Link größer. Kontrollkästchen 24 × 24 px. Rubrikkacheln mit 480er-Fassung (35 statt 141 KiB) |
| CODE-01 (P1) ausgerichtete Bilder im Text | behoben | Mit Testbeitrag geprüft, die Datenbank danach zurückgesetzt |
| CODE-02 (P1) erstes Terminbild lud spät | behoben | `eager` und `fetchpriority=high` |
| CODE-03 (P1) Termine doppelt auf `/events/` | behoben | Ohne Filter keine Doppel. Mit Land- oder Stadtfilter zeigt die Liste wieder alle passenden Termine |
| CODE-04/05 toter Code | behoben | |
| CODE-06 dasselbe Bild zweimal auf einer Seite | offen | Nicht billig lösbar, betrifft die Bildkette über mehrere Abfragen |
| CODE-07 Platzhalterhöhe zu groß | behoben | Karten 290 px, Termine 240 px |
| CODE-08 unlesbare oder riesige Bilder | behoben | Ergebnis wird gemerkt, Originale nur bis 4 MP |

## Prüfungen (lokal, Stand `16b50ad`)

`lint.sh` sauber · `pytest -q tests/wp` 239 bestanden, 2 übersprungen · `pytest -q` 1602 bestanden ·
`news_radar abnahme` 89/89 · `bilder_pflicht` 0 ohne Bild, Signet und Titel im Bild je 100 % · `shots.mjs` auf
7 Seitentypen ohne Fehler · axe 0 Verstöße.

Die Ergebnisse der Live-Prüfung auf dem Testsystem trägt der Abschlussbericht im Chat nach.
