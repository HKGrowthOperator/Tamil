# Prüfung mix-feed, Runde 2
Harte Kriterien: 14 von 16 erfüllt · P0: 0 · P1: 3 · P2: 4 · P3: 3

Maßstab: Brief 10.4 (16 Kriterien) und 10.1, Verbotsliste `tamil-marke`, Abnahme Luis 12.11.2026 („Feed-Wucht mit
klar2-Schrift“). Kennzahlen: `node design/vergleich/aufnahmen.mjs mix-feed` (`design/vergleich/kennzahlen/mix-feed.json`,
Stand 12.11.2026 15:51). Technik: `tools/shots.mjs` für index, artikel, rubrik, termine × 390/820/1280 (12 Aufnahmen,
0 Fehler). Dazu eigene Messungen im Browser (Bildformate, Kanten, Zeilenlänge je Zeichen, Lage der Blöcke, 320 px).
Rohdaten und Vergleichstafeln: `/tmp/claude-0/-home-user/328bcd38-019d-5546-955b-7fea86a20fa1/scratchpad/kritik-feed-r2/`
(`mess.json`, `bericht.json`, `m-handy.jpg`, `m-desk.jpg`, `m-zoom.jpg`, `m-handy23.jpg`, `m-seiten.jpg`).
`begruendung.md` nicht gelesen.

## Stand der sechs P1 aus Runde 1

| # | Befund Runde 1 | Messung Runde 2 | Stand |
|---|---|---|---|
| 1 | Aufmacher-Schlagzeile am Handy ab 534 px | ab 416 px (Bild jetzt 1:1, 390 × 390 ab 149 px) | geschlossen |
| 2 | 5 / 9 Bildformate | index Handy 1:1 · 3:2 · 4:5; Desktop 1:1 · 3:2 · 4:5; rubrik 3, artikel 2, termine 1 (Logo nicht gezählt) | geschlossen |
| 3 | Artikelzeilen Median 83 Zeichen | artikel 1280: Mittel 68, Median 68, 7 von 18 Zeilen 71–75; artikel-80: Mittel 66,8, max. 72; 820 gleich | geschlossen (Rest P3-1) |
| 4 | „Im Kino“ als Reihe gleicher Kacheln mit leeren Flächen | „Sardar 2“ groß (592 × 395, Titel im Bild), daneben „Läuft diese Woche“ als Textliste mit Kinozahl, darunter zwei 3:2-Stücke; keine leere Kachel | geschlossen |
| 5 | Erster Bildschirm wie `mix-ordnung` | Desktop klar anders (Bildwand gegen Aufmacher + Liste); Handy anders in der Behandlung (randlos, Titel im Bild, 1:1) bei gleichen Fotos in gleicher Reihenfolge | geschlossen (Handy knapp); die Lösung am Desktop erzeugt P1-3 |
| 6 | Rubrikband-Text bei x = 16, Logo bei 32 | Bandtext 16 / 24 / 32 px = Logo 16 / 24 / 32 px bei 390 / 820 / 1280, auf allen vier Seiten | geschlossen |

Aus Runde 1 ebenfalls behoben: Anreißertext jetzt 18 px (nur Nachweise 12 px und Kinoorte 15 px darunter),
Nachweise einzeilig und gekürzt, „Symbolbild“ sichtbar (INAIVU), Meldungsbilder Desktop 128 px, Überlauf bei 320 px 0.

## Erster Eindruck (3 Sätze)

Am Handy ist der erste Bildschirm jetzt fast nur Foto: Tempel randlos 1:1, darunter Koovagam 3:2, beide mit weißer
Schlagzeile auf Tinte; das ist sichtbar „Feed“ und weiterhin nicht laut (eine Familie, 30 px, kein Rot). Am Desktop
ist aus „Aufmacher + Meldungsspalte“ eine Wand aus fünf Quadraten geworden, alle in derselben Behandlung (Foto,
dunkler Verlauf, weißer Titel), und der Aufmacher ist dabei auf 596 px geschrumpft. Der Preis der größeren Bilder
steht weiter unten: „Diese Woche“ ist am Handy um 800 px nach unten gerutscht und liegt jetzt außerhalb der Grenze.

## Harte Kriterien (Brief 10.4)

| # | Kriterium | Handy (390 × 844) | Desktop (1280 × 800) | Ergebnis |
|---|---|---|---|---|
| 1 | Viele Geschichten, h2/h3 mit Link | 2 ganz sichtbar (Aufmacher, Koovagam) | 5 | erfüllt |
| 2 | Kopf ≤ 152 px; Aufmacher-Schlagzeile ab ≤ 480 px | Kopf 149; Schlagzeile ab 416 | Kopf 165; Aufmacher-Schlagzeile ab 617 (von Hand), ganz sichtbar | erfüllt |
| 3 | Drei Stufen, Aufmacher ≥ 1,25 × Nebenstück; ≤ 2 Familien | 30 / 22 / 19 px (1,36 ×); nur Libre Franklin | 40 / 24 / 19 px (1,67 ×) | erfüllt |
| 4 | Größte = Aufmacher ≤ 34/44; zweitgrößte ≤ 24/28; Aufmacher ≤ 3 Zeilen, andere ≤ 4; Versalien > 14 px: 0 | 30; 24 („Diese Woche“); 3 Zeilen (101 px); max. 4; 0 | 40; 26; 3 Zeilen (132 px); max. 4; 0 | erfüllt |
| 5 | Rot ≤ 3 %, rote Schrift ≤ 20 px, kein zweiter Buntton | 0 %; 0 px laut Kennzahl (rote Dachzeilen 13 px) | 0 %; dito | erfüllt |
| 6 | Genau zwei dunkle Flächen; ≤ 12 % dunkel im ersten Bildschirm | nav.band + section#diese-woche; 5,3 % | dieselben; 5,4 % | erfüllt |
| 7 | Keine Effekte; Verlauf nur unter Schrift | Radius 0, Schatten 0, gedreht 0, Breite normal | dito | erfüllt (Stärke des Verlaufs: P2-2) |
| 8 | Kein Baukasten (Kasten, Icon, Knopf, Pillen) | keine | keine | erfüllt (Raster: P1-3) |
| 9 | Kein Anreißer ohne Bild; Grafik ≤ 3 | Kennzahl 16 Anreißer, 0 ohne Bild, 0 Grafik; von Hand: Termin „Düsseldorf Tamil Sangam“ (h4 mit Link) ohne Foto | dito | erfüllt in der Zählung (Lücke P2-3) |
| 10 | Ein Format Dachzeile/Datum; ≤ 3 Bildformate | „Rubrik \| Datum“ überall; 3 (1,00 · 1,50 · 0,80) | 3 (1,00 · 1,50 · 0,80) | erfüllt |
| 11 | Bildgröße | über Dateibreite: keins | **rb-71 (Community-Leitbild) 803 px gezeigt, Datei 1280 px**; Community ist keine Ausnahme | **verletzt** (P1-2) |
| 12 | Helle Schrift ≥ 4,5 : 1 | 71 Stellen, kleinster 4,66 | 80 Stellen, 4,82 | erfüllt |
| 13 | Bewegung | Maßstab 1,03; 0,35 s; 0 Animationen; reduziert 0; fest nur nav.band 48 px | dito | erfüllt |
| 14 | Kein Überlauf, keine Konsolenfehler | 0 px (auch 320 px: 0), 0 Fehler | 0 px, 0 Fehler | erfüllt |
| 15 | „Diese Woche“ am Handy ab ≤ 2532 px | **2618 px** (Kennzahl und eigene Messung gleich; Runde 1: 1818) | – | **verletzt** (P1-1) |
| 16 | Paarvergleich | keine weiteren Werte außerhalb der Grenzen | | erfüllt |

## Paarvergleich

**Gegen `mix-ordnung` (Schwester), Handy** (`m-handy.jpg`)
- Beide zeigen Tempel und Koovagam in derselben Reihenfolge (Inhaltsliste). mix-feed: Tempel 1:1 randlos (390 px
  hoch), Koovagam 3:2 randlos, beide Titel weiß im Bild; mix-ordnung: Tempel im Querformat, Koovagam mit Rand, Titel
  schwarz unter dem Bild auf Weiß.
- Anteil Foto im ersten Bildschirm: mix-feed rund 85 %, mix-ordnung rund 60 % mit sichtbarem Weiß. Im Fünf-Sekunden-
  Blick unterscheidbar: dunkle Bildwand gegen helle Seite mit Bildern.

**Gegen `mix-ordnung`, Desktop** (`m-desk.jpg`)
- mix-feed: Aufmacher 596 × 596 links, rechts vier Quadrate 286 × 286 im 2 × 2, alle fünf Titel im Bild; kein
  Vorspann im ersten Bildschirm. mix-ordnung: Aufmacher rund 615 px breit im Querformat, Vorspann darunter, rechts
  ein Bild und zwei Meldungen mit kleinem Bild. Klar zwei Richtungen.
- Die rechte Hälfte von mix-feed hat keine Hierarchie mehr: vier gleiche Flächen, gleiche Schrift (19 px), gleiche
  Dachzeile, gleicher Verlauf (P1-3).

**Gegen `klar2`, Handy:** klar2 Aufmacher im Querformat mit Titel im Bild, dann Vorspann, Rubrikkacheln, Liste;
mix-feed ersetzt Vorspann und Kacheln durch das zweite große Bild. Sichtbar bildstärker und weniger „classic“.

**Gegen BBC, Handy:** BBC zwei Fotos nebeneinander (rund 215 px hoch), Serifenschlagzeile schwarz auf Weiß, Vorspann,
dann Liste mit Bildern links. mix-feed hat mehr Bildfläche bei gleicher Zahl ganz sichtbarer Schlagzeilen (2), aber
keinen Vorspann vor dem zweiten Bildschirm; die Nachrichtenliste (zweiter bis dritter Bildschirm, `m-handy23.jpg`) ist
in Aufbau und Ruhe nahe an der BBC.

**Gegen Runde 4 (`r4-raster`, Handy):** R4 „KANGUVA“ rot, schmal, in Versalien über die volle Breite, rote Linien,
Versalien-Navigation. mix-feed: größte Schrift 30 px, Rot 0 %, normale Breite, Versalien nur in „IM KINO“ (≤ 14 px).
Nicht laut. Gegen Runde 2: kühles Weiß, Radius 0, Fotos statt Grafikkarten; nichts davon wiederholt.

## Befunde

### P0
Keine. `bericht.json`: 0 Fehler, 0 Überlauf bei 390/820/1280 (eigene Messung auch 320 px: 0).

### P1

1. **„Diese Woche“ am Handy zu tief (hartes Kriterium 15), durch die Überarbeitung entstanden.** index 390:
   Oberkante 2618 px, Grenze 2532 (Runde 1: 1818). Ursache: oberhalb stehen jetzt Aufmacher 1:1 (390 px), Koovagam
   3:2 (260), INAIVU 4:5 randlos (488), Streifen 4:5 (349), vier Meldungen (rund 680). Behebung: mindestens 150 px
   sparen, z. B. INAIVU auf 3:2 (spart 228 px) oder „Diese Woche“ vor die Meldungsliste stellen; danach nachmessen.
2. **Community-Leitbild über der halben Dateibreite (hartes Kriterium 11), durch die Überarbeitung entstanden.** index
   1280: `bilder/rb-71.jpg` (Datei 1280 × 1707) in `section.community` mit 803 px gezeigt; bei doppelter Dichte
   braucht es 1606 px. Ausgenommen sind nur Aufmacher und die große Kachel in „Diese Woche“ und „Küche“; in Runde 1
   war das 803-px-Bild noch der Aufmacher. Behebung: Leitbild höchstens 640 px breit setzen oder eine Datei ab
   1606 px Breite einsetzen, sofern die Quelle sie hergibt.
3. **Desktop-Einstieg: Aufmacher zu klein und daneben ein gleichförmiges Raster (Brief 10.1, Verbotsliste
   „identische Kartenraster“), durch die Überarbeitung entstanden.** index 1280, erster Bildschirm: Aufmacher
   596 × 596 px; Brief 10.1 verlangt am Desktop mindestens 760 px Breite (Runde 1: 803). Rechts vier Quadrate
   286 × 286 px im 2 × 2, gleiche Größe, gleiches Format, gleiche Schrift 19 px, gleicher Verlauf und je ein Nachweis
   darunter; damit tragen fünf von fünf Anreißern dieselbe Behandlung, und die Seite liest sich wie eine Bildergalerie
   statt wie eine Nachrichtenseite mit Stufen. Behebung: Aufmacher auf 8 von 12 Spalten (rund 800 px, 3:2 oder 1:1);
   rechts eine Spalte mit zwei unterschiedlichen Stücken (oben 4:5 mit Titel im Bild, darunter 3:2 mit Titel unter
   dem Bild) oder ein hohes 4:5 über zwei Zeilen neben zwei kleinen; die übrigen zwei Geschichten als Zeilen mit Bild.

### P2

1. **Artikel am Desktop: Schlagzeile unter der Falz, durch die Überarbeitung entstanden.** artikel.html 1280 × 800:
   Bild jetzt 3:2 (vorher 5:2), h1 beginnt bei 769 px und ist 92 px hoch, also abgeschnitten; im ersten Bildschirm
   stehen nur Foto und Dachzeile. Behebung: Dachzeile, Schlagzeile und Vorspann über das Bild (wie BBC und Spiegel)
   oder Bildhöhe am Desktop auf rund 420 px begrenzen.
2. **Verlauf wird auf kleinen Kacheln zur grauen Platte.** index 1280, 2 × 2-Kacheln, und index 390, Streifen:
   `--verlauf` erreicht 0,74 Tinte schon 52 px über dem Textblock; bei vierzeiligen Titeln deckt das nach Augenmaß
   rund die Hälfte der 286-px-Kachel. Sichtbar bei „Frankfurt, Duisburg, Dortmund“ (Gebäude unten grau verwaschen) und
   „Vaani Vizha“ (oranger Stein wird braungrau). Die Schrift bleibt lesbar (kleinster Wert 4,82 : 1); der Brief will
   „ohne Platte“. Behebung: Verlauf an die Titelhöhe binden und erst unter der Dachzeile auf 0,74 bringen, oder auf
   kleinen Kacheln Titel unter das Bild.
3. **Termin ohne Bild (offen aus Runde 1).** index und termine, „Diese Woche“: „Düsseldorf Tamil Sangam“ (h4 mit
   Link auf `artikel.html`, das ein Foto hat) steht nur mit Datumsblock. „Diwali in Basel“, „Scene“ und „Ramayana“
   sind die erlaubten Radar-Einträge ohne Foto. Behebung: Artikelbild klein (3:2) an den Düsseldorf-Termin.
4. **Zu lange Zeilen in der Termin-Info bei 820 px.** index 820: `termin__info` 680 px breit, 18 px, erste Zeilen 72
   und 81 Zeichen. Behebung: `max-width: 36em`.

### P3

1. artikel.html 1280 und 820: 7 von 18 Zeilen haben 71–75 Zeichen (Mittel 68). `max-width: 33em` statt 34em hält
   jede Zeile unter 70.
2. Desktop-Kopf 165 px, die Logozeile ist bis auf das Logo leer (offen aus Runde 1). Logo und Datumszeile in eine
   Zeile wie bei `mix-ordnung`.
3. „Läuft diese Woche“: „Scene“ und „Ramayana“ ohne Link; wer die elf Spielorte sucht, kommt nicht weiter. Link auf
   `termine.html#…` oder auf den Radar-Eintrag.

## Was trägt

1. **Fünf der sechs Ordnungsmängel sind sauber behoben:** drei Bildformate auf jeder Seite, Kante von Band und Logo
   deckungsgleich bei allen Breiten, Kino ohne leere Kacheln, Schlagzeile am Handy bei 416 px, Artikelzeilen im
   Mittel 68.
2. **Bildwucht ohne Lautstärke:** am Handy rund 85 % Foto im ersten Bildschirm, trotzdem eine Familie, 30/40 px,
   Rot 0 %, Radius 0, keine Schatten; neben R4 klar auf der ruhigen Seite.
3. **Nachweise jetzt ruhig:** einzeilig unter dem Bild, „Symbolbild“ sichtbar; Anreißertext durchgehend 18 px.

## Bedienbarkeit (nur zur Information)

| Heuristik | 0–4 | Begründung |
|---|---|---|
| 1 Status sichtbar | 3 | Aktive Rubrik hell mit roter Linie im Band. |
| 2 Sprache der Nutzer | 4 | Deutsch, Datum mit Jahr, Kinozahl und Orte. |
| 3 Kontrolle und Freiheit | 3 | Stehendes Rubrikband, Streifen per Tastatur. |
| 4 Einheitlichkeit | 3 | Dachzeile und Nachweis überall gleich; Artikel setzt die Schlagzeile anders als die Startseite. |
| 5 Fehlervermeidung | 2 | Unverändert, nicht neu geprüft. |
| 6 Erkennen statt Erinnern | 3 | Rubriken immer sichtbar; Kinoliste ohne Weg zu den Spielorten. |
| 7 Flexibilität | 4 | Kein Überlauf mehr bei 320 px; reduzierte Bewegung schaltet alles ab. |
| 8 Ästhetik, Reduktion | 3 | Nachweise ruhig; am Desktop fünf gleich behandelte Bildflächen. |
| 9 Fehler erkennen | – | In der Probe nicht prüfbar. |
| 10 Hilfe | 2 | Keine; für eine Nachrichtenseite kaum nötig. |
