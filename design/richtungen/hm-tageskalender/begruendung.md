# Probeseite „Tageskalender“ (hm-tageskalender): Begründung

Stand 14.11.2026, Runde 2 (nach `design/kritik/hm-tageskalender-r1.md`; Änderungen im Abschnitt „Runde 2“ am Ende, ältere Aussagen oben sind dort berichtigt). Auftrag von Luis (14.11.): „eine Mischung aus A und B“. Gestaltet nach `design/brief-v3.md` und
`design/linien-auftrag.md` mit Hallmark v2.0.0 (eigene Richtung). Alle Seiten erzeugt `bauen.py` aus echtem Material
(Aufruf vom Repo-Root: `python3 design/richtungen/hm-tageskalender/bauen.py`); von Hand geschrieben ist nur
`hm-tageskalender.css` (Ausgangspunkt war die CSS von Linie A, die Mischung steht im Block „Tageskalender“ am Ende).

## Idee

tamil.de beginnt jeden Tag wie eine Zeitung mit seinem Datum und dem Aufmacher im Foto (Linie A) und ordnet darunter,
was kommt, als gedrucktes Kalenderblatt in Tabellen (Linie B); Rot zeigt nur, was als Nächstes kommt.

## Was aus A und was aus B kam

| Aus A „Tagesblatt“ | Aus B „Kalenderblatt“ |
|---|---|
| Tagesziffer, Monat und Wochentag als Hauptfigur oben links | Die nächsten Feste als Tabelle Tag, Was, Wer, Wo |
| Aufmacher mit großem Foto und Nachweis am Bild | Der nächste Termin zwischen zwei festen Linien in Rot mit „als Nächstes“, vergangene Zeilen grau |
| „Per WhatsApp schicken“, „Zuletzt bei tamil.de“ nach Monaten mit Tagesziffer | Kino als Tabelle: Film, Städte, Zahl der Kinos, Stand |
| Schrift (Rethink Sans, Golos Text) und Farben (Jasminweiß, grüne Tinte, Logo-Rot) | Das helle Blatt mit fester Linie oben als Träger jeder Tabelle |
| Artikelkopf mit Datumsblock, Fuß mit Bildnachweisen, Formulare, Werben, Buchen | Navigation Termine, Kino, Community, Verzeichnis; schmale Leiste „Rückblick 2026 in zwanzig Berichten“ über dem Kopf |
| | Foto neben dem Seitenkopf auf Festkalender, Kino und Verzeichnis (B, Schliff nach r2) |

## Entscheidungen, wo A und B kollidieren (je ein Satz)

- **Rot:** Rot heißt nur noch „als Nächstes“ (B), weil A's Regel „Sonntag oder Festtag“ in einer Tabelle voller
  Sonntage jede zweite Zeile rot gefärbt hätte; auch Datumsblock und Buchungskalender sind deshalb ohne Rot.
- **Datum in der Tabelle:** Die Tag-Spalte zeigt A's große Tagesziffer mit „So, Nov.“ darunter statt B's „So 15.11.“,
  damit die Tabelle dieselbe Hand trägt wie der Datumsblock oben.
- **Ort der Feste auf der Startseite:** Die Tabelle steht unter dem Aufmacher statt in A's linker Spalte, weil vier
  Spalten in einem Drittel der Breite nicht lesbar sind; dafür rückt der Aufmacher-Titel unter das Datum.
- **Kino auf der Startseite:** kompakte Form „Film und Städte | Kinos“ mit Stand im Kopf, weil vier Spalten neben den
  Festen zu schmal werden; die volle Tabelle mit Stand je Film steht auf `kino.html`.
- **Bilder:** A's Bilder in jeder Zeile des Stroms bleiben, am Handy als kleines Quadrat rechts mit Nachweis unter dem
  Titel, weil Luis „überall Bilder“ will und B zu wenig Bild hatte.
- **Rückblick-Leiste:** Sie führt auf eine eigene Seite `rueckblick.html` (alle zwanzig Berichte), weil A's Startseite
  nur Juli bis Oktober zeigt.
- **Kopf:** B's vier Ziele plus A's Menü („Mehr“) für die übrigen Rubriken und Mitmachen; A's Tagesdatum im Kopf nur
  auf Unterseiten und erst ab 1100 px.

## Hallmark-Picks

**Hallmark · v2.0.0**

- **Idea** · tamil.de beginnt jeden Tag mit seinem Datum, dem Aufmacher im Foto und den nächsten Festen als gedruckte
  Tabelle; Rot zeigt nur, was als Nächstes kommt.
- **Look** · Papier Jasminweiß `oklch(97.6% 0.007 120)` und Tinte `oklch(21% 0.022 155)` aus A; Blatt
  `oklch(99.3% 0.004 120)` mit fester Linie `oklch(32% 0.02 155)` nach B; Akzent Logo-Rot `oklch(50.5% 0.175 25)`;
  Rethink Sans 600 für Köpfe, 800 nur für Ziffern; Golos Text für Lesetext (OFL, selbst gehostet, Lizenzen in
  `schriften/`).
- **Job** · read (lesen, finden, teilen).
- **Chrome** · nav: Leiste „Rückblick 2026“ über dem Kopf, Logo, Termine, Kino, Community, Verzeichnis, Menü „Mehr“
  (am Handy zweite Zeile unter dem Logo) · footer: Feld paper-2 mit Logo, Rubriken, Diensten, Bildnachweisen.
- **Hero** · Startseite: Tagesziffer, Aufmacher-Schlagzeile, Vorspann und WhatsApp links (5 Spalten), Foto 4:3 rechts
  (7 Spalten); am Handy Datum, Schlagzeile, Foto, Vorspann.
- **Signature** · die Feste-Tabelle mit großer Tagesziffer je Zeile, der nächste Termin zwischen zwei festen Linien in
  Rot mit „als Nächstes“.
- **Sections** · Start: Tagesblatt · Kalender (Feste 8 Spalten, Kino 4 Spalten) · Zuletzt bei tamil.de · Fuß.
  Termine: Kopf mit Foto · Ab heute (Tabelle, Teilen je Zeile) · Das Jahr 2026 (Monate als Tabellen, eingeklappt).
  Kino: Kopf mit Foto · Im Programm · Nach Stadt (nach Land) · Aus dem Kinojahr. Rubrik: neuester Beitrag als
  Aufmacher mit großem Foto · Strom mit Bild je Zeile · Seitennavigation.
- **Material** · real: 20 Rückblick-Beiträge mit Bildern und Nachweisen (`rueckblick.json`), Chronik aus
  `docs/redaktion/rueckblick-2026.md`, Kino „Scene“ und „Ramayana“ aus `inhalte.json` (Stand 9.11.), Diwali in Basel aus
  `inhalte.json`, Düsseldorf 15.11. aus Beitrag 30 (seit Runde 2 nichts mehr aus wartenden Radar-Entwürfen) · pictures: Commons-Fotos der Beiträge, Symbol- und Archivbilder als
  solche gekennzeichnet · absent: Kinonamen und Uhrzeiten, sechs Städte von „Scene“, weitere kommende Termine,
  Preise, Kontaktdaten, Impressum.
- **Sweep** · `sloplint --genre editorial` über die elf Pflichtseiten (Dateien und `--url`): 0 FAIL, 0 REFLEX offen;
  waived 49b, 78, 77, 79, 59; answered F25, F15 · `shots.mjs`: 48 Aufnahmen, 0 Fehler · keine Prüfung aus frischem
  Kontext in diesem Auftrag (Agents starten keine Agents).

## Seiten

| Datei | Inhalt |
|---|---|
| `index.html` | Tagesblatt mit Aufmacher, Tabellen „Die nächsten Feste“ und „Im Kino“, Strom „Zuletzt bei tamil.de“ |
| `rubrik.html`, `rubrik-2.html` | Community: neuester Beitrag als Aufmacher, dann Strom nach Monaten mit Bild je Zeile, Seitennavigation; dazu `rubrik-nachrichten/-kultur/-kueche/-sport.html` als Ziele des Menüs |
| `artikel.html` | Deepavali (Beitrag 30) mit Datumsblock, Bildnachweis, WhatsApp, Tabelle „Im Beitrag genannt“, Weiterlesen; dazu 19 weitere `artikel-<id>.html` |
| `termine.html` | Festkalender: „Ab heute“ als Tabelle mit „als Nächstes“ und Teilen je Zeile, darunter das Jahr 2026 nach Monaten |
| `kino.html` | Im Programm (Film, Städte, Kinos, Stand, Teilen), Nach Stadt (Deutschland, Schweiz), Kinojahr |
| `verzeichnis.html`, `verzeichnis-eintrag.html` | Suche, Filter Art und Ort, Liste; Profil Sri Ganesha Hindu Temple mit Premium als Beispiel gekennzeichnet; dazu 11 weitere Profile |
| `einreichen.html`, `einreichen-danke.html` | Termin einreichen (§12) mit Einwilligung, Bestätigung als Zustand |
| `werben.html`, `buchen.html`, `buchen-danke.html` | Plätze mit Maßen, Preise „folgt“, Buchung in fünf Schritten, Kundenübersicht |
| `kontakt.html`, `kontakt-danke.html` | Formular „Nachricht“, Redaktionsdaten als Platzhalter |
| `rueckblick.html` | Ziel der Leiste: alle zwanzig Berichte nach Monaten |

## Prüfung

Server `http://127.0.0.1:8111/`, Stand 14.11.2026.

- `sloplint --genre editorial` über `index, rubrik, artikel, termine, kino, verzeichnis, verzeichnis-eintrag,
  einreichen, werben, buchen, kontakt` (Dateien plus je `--url`): **0 FAIL, 0 REFLEX, 11 WARN, 144 WAIVED,
  5 ANSWERED, 33 NOTE.** Die 11 WARN sind „fallback font“ aus dem Datei-Durchgang (Schriften laden über `file://`
  nicht); über http laden sie. NOTE 58 zählt viele Wörter auf Tabellenseiten (Termine bis 524 Wörter auf einem
  Bildschirm bei 1440, wenn November offen ist); `copy: verbatim` steht im Stempel.
- `node tools/shots.mjs` für 16 Seiten (die elf Pflichtseiten plus `rubrik-2`, drei Bestätigungen, `rueckblick`) bei
  390, 820 und 1280: **48 Aufnahmen, 0 Fehler**, 0 px seitliches Scrollen, 0 Konsolenfehler, 0 leere Bilder, 0 kleine
  Tippflächen, 0 Tamil ohne `lang`.
- Fließtext 18 px, Tabellenzellen 18 px, Stand und Nachweise 14 px; Tinte auf Papier > 14:1, Rot auf Papier 6,0:1
  (Tokens aus A unverändert).

## Abgrenzung

- Gegen Runde 2 (Sand, Serife, Pillen): kühles Jasminweiß, Grotesk, eckig, keine Pillen.
- Gegen Runde 4 (rote Riesenschrift): größte Schrift ist die Tagesziffer in Tinte (rund 74 px bei 1280), Schlagzeile rund 40 px,
  Rot nur in einer Tabellenzeile.
- Gegen Runden 5 bis 7: keine Dachzeilen, keine Versal-Labels, keine „·“-Metazeilen, keine Kartenraster, keine
  Verlauf-Kacheln, kein „Diese Woche“-Band.

## Eigene Schwächen

- Vier Hallmark-Ausnahmen (49b, 78, 77, 59) gelten auf fast jeder Seite; das ist ein Hausstil, der noch in eine
  `design.md` gehört.
- Die Tabellen wiederholen auf Start, Termine und Artikel dieselben drei Termine; bei echten Daten würde die Startseite
  mehr Zeilen brauchen.
- Das Aufmacherfoto zeigt den Berliner Tempel im Juni, nicht Deepavali, und ist dieselbe Datei wie bei Beitrag 49.
- Das Karthi-Foto im Strom hat einen roten Hintergrund und ist die größte rote Fläche der Probe.
- Am Handy brechen lange Berichtstitel in der schmalen Spalte neben dem Daumenbild auf vier bis fünf Zeilen um.
- Seitenköpfe mit Foto lassen bei 1280 links unter dem Satz eine leere Fläche.
- Formulare, Werben, Buchen und Kontakt haben kein Foto und tragen die Mischung kaum; sie sind A's Fassung.
- Kinonamen und Uhrzeiten fehlen; „Nach Stadt“ endet für sieben von acht Städten beim Film.
- Verzeichnis-Filter und Buchungskalender sind statisch und zeigen nur Zustände.
- Keine Prüfung aus frischem Kontext; die steht noch aus.

## Neu bauen

`python3 design/richtungen/hm-tageskalender/bauen.py` (vom Repo-Root).

## Runde 2 (nach Kritik r1)

Behoben sind die drei P1 und P2-1 bis P2-4; sonst ist nichts Neues dazugekommen. Was oben in Picks, Look, Chrome, Hero und Sections
anders steht, gilt in der Fassung dieses Abschnitts.

**P1-1 Inhalte.** THADAM, „OM“ und „Jailer 2“ sind auf allen Seiten gestrichen (sie stammten aus nicht freigegebenen
Radar-Entwürfen). Damit entfällt auch das Wort „nur“. Der Kino-Stand heißt jetzt „9. November“ (`inhalte.json`), die
Schweiz-Gruppe in „Nach Stadt“ entfällt. Kommend sind damit nur noch zwei belegte Feste (15.11. Düsseldorf,
21.11. Basel); mehr gibt `design/inhalte/` nicht her.

**P1-2 A und B zusammen im ersten Bildschirm.** Was jetzt von B kommt, je ein Satz:
- **Kalender im ersten Bildschirm:** Bei 1280 stehen „Die nächsten Feste“ als Tabelle in der Textspalte unter dem
  Vorspann. Das Foto ist auf fünf Spalten verkleinert, darunter steht die Kino-Tabelle, weil B den Kalender als Kopf
  der Seite will und A den Aufmacher.
- **Am Handy unter der Tagesziffer:** Die Feste-Tabelle folgt direkt auf die Tagesziffer, vor Schlagzeile und Foto,
  weil die Frage „was kommt als Nächstes“ bei B an erster Stelle steht.
- **Kühles Papier aus B:** Grund `oklch(96.8% 0.007 245)`, Blatt `oklch(99.3% 0.003 245)`, blauschwarze Tinte
  `oklch(19% 0.02 245)`, Linien im Farbton 240. Das ist B's Material statt A's grünlichem Weiß. Schriften bleiben die
  zwei von A, keine dritte; `tokens.css` ist angepasst.
- **Randloses Blatt am Handy:** Das Tabellenblatt läuft am Handy über die volle Breite, der Text steht auf derselben
  16-px-Kante wie alles andere, so wie B's Blatt auf dem Grund liegt.

**P1-3 Kopf am Handy.** Bis 760 px ist der Kopf eine Zeile wie bei A: Logo, Termine, Kino, Mehr. Bis 520 px stehen
Community und Verzeichnis nur im Menü. Die Rückblick-Leiste ist am Handy ausgeblendet; ihr Ziel steht im Menü
„Mehr“. Die verrutschte Linie über der zweiten Zeile gibt es nicht mehr. Ab 761 px bleibt B's Leiste über dem Kopf.

**P2.**
- „Die nächsten Feste“ zeigt auf der Startseite nur Kommendes; der 8.11. steht nur noch im Artikel unter „Im Beitrag
  genannt“.
- Am Handy gibt es eine linke Kante: Blatt randlos, Text bei 16 px.
- Lange Titel im Strom trennen jetzt (`hyphens: auto`, erst ab zwölf Zeichen), statt an das Vorschaubild zu stoßen.
- Gestrichelte Platzhalter sind ein Kasten (`inline-block`, gepolstert) und brechen nicht mehr in zwei Teile.

**Messwerte erster Bildschirm (Startseite, gemessen über http).**

| | 390 × 844 | 1280 × 800 |
|---|---|---|
| Kopfhöhe | 61 px (vorher 143) | 122 px mit Leiste (unverändert) |
| erste Festzeile ab y | 245 px (vorher 848) | 614 px (vorher 727, nur der Tabellenkopf war sichtbar) |
| beide Festzeilen enden bei y | 477 px | 769 px |
| Schlagzeile ab y | 555 px | 245 px |
| Foto ab y | 672 px | 162 px |

**Prüfung Runde 2.**
- `sloplint --genre editorial` über index, artikel, rubrik, termine, kino (Dateien plus je `--url`): **0 FAIL,
  0 REFLEX, 5 WARN, 118 WAIVED, 5 ANSWERED, 20 NOTE.**
  - Die 5 WARN sind „fallback font“ im Datei-Durchgang über `file://` (P2-5 der Kritik). Über http laden die
    Schriften; shots meldet 0 nicht geladene Schriften. Nicht weiter verfolgt, weil P2-5 nicht zum Auftrag gehörte.
  - Neu behoben: REFLEX 72 an den Platzhalter-Kästen, durch Innenabstand.
- `tools/shots.mjs` über dieselben fünf Seiten bei 390/820/1280: **15 Aufnahmen, 0 Fehler**, 0 px Überlauf,
  0 Konsolenfehler, 0 kleine Tippflächen.

**Neue oder geänderte Schwächen.**
- Die Feste-Tabelle der Startseite hat nur zwei Zeilen, weil es in `design/inhalte/` nicht mehr kommende Termine gibt.
- Am Handy steht die Aufmacher-Schlagzeile erst bei y 555, das Foto beginnt im unteren Fünftel des ersten Bildschirms.
- Silbentrennung im Strom trennt auch mittellange Wörter („Ta-milalayams“).
- Die anderen Seitentypen (Verzeichnis, Formulare, Werben, Buchen, Kontakt) sind nur technisch geprüft
  (shots.mjs: 18 Aufnahmen, 0 Fehler), nicht angesehen. Papier und Kopf haben sich dort mitgeändert.
