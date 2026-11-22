# Prüfung mix-ordnung, Runde 2
Harte Kriterien: 16 von 16 erfüllt · P0: 0 · P1: 1 · P2: 2

Maßstab: Brief 10.4 (16 Kriterien, Fassung `klar2`, deren Ordnung die Probe übernimmt), Verbotsliste
`tamil-marke`, Auftrag Luis vom 11./12.11. („überall Bilder“, weniger klassisch). Gemessen am 12.11.2026 mit
`node design/vergleich/aufnahmen.mjs mix-ordnung` (Kennzahlen `design/vergleich/kennzahlen/mix-ordnung.json`,
Bilder `design/vergleich/img/mix-ordnung-*.jpg`) und `tools/shots.mjs` für alle sechs Seiten bei 390, 820 und 1280
(18 Aufnahmen). Zeilenzahlen, Nachweise und Verlaufshöhen kommen aus einer eigenen Messung mit Playwright
(Höhe des Elements geteilt durch die Zeilenhöhe; Abstand von Bild zum nächsten `.nachweis` oder `figcaption`).
`begruendung.md` und die Kritik aus Runde 1 habe ich nicht gelesen. Die fünf offenen Punkte stammen aus dem Auftrag.

## Erster Eindruck (3 Sätze)
Die Startseite ist klar bildstärker als `klar2`: Am Desktop steht rechts neben dem Aufmacher ein zweites großes Bild
statt einer Textliste, am Handy folgt auf den Aufmacher sofort ein Vollbild. Rot, Schriftgrößen, Kanten und Kopf
bleiben so ruhig wie bei einer großen Nachrichtenmarke. Laut ist nichts geworden. Was noch stört, ist der Verlauf im
Bild: Am Handy liegt er auf zwei Dritteln bis drei Vierteln der Bildhöhe und zeigt auf ruhigem Grund eine sichtbare
Oberkante. Dazu kommen graue Nachweiszeilen, die nun unter jedem Anreißer stehen.

## Stand der fünf Befunde aus Runde 1

| # | Befund Runde 1 | Messung Runde 2 | Stand |
|---|---|---|---|
| 1 | Verlauf wirkt als dunkle Platte über den Fotos | Desktop: Verlauf auf 32–44 % der großen Bilder, Oberkante fällt kaum auf. Handy: auf 65–74 % der Bildhöhe (Startseite Aufmacher 186/260 px, Kanguva 150/201, Sardar 155/239, Küche groß 155/239); `rubrik.html` 390: 173/260 px mit sichtbarer Kante (Helligkeit im Himmel 163 → 103 auf 27 px); `index.html` 820, Küche „Bremen“: Verlaufskasten 158 px in einem 140 px hohen Bild | **nicht geschlossen** (Befund P1-1) |
| 2 | Commons-Bild ohne Namensnennung auf `rubrik.html` | alle 15 Fotos auf `rubrik.html` haben einen sichtbaren Nachweis (7 einzeln, die sieben Rubrikkacheln mit Sammelzeile „Bilder: Archiv tamil.de; Sport: Foto: Vincenzo.togni / Wikimedia Commons, CC BY-SA 4.0“). Stichprobe gegen `design/inhalte/rueckblick/rueckblick.json`: rb-30, 43, 51, 60, 67, 71, 85, 87 stimmen mit Urheber und Lizenz überein | geschlossen |
| 3 | Altbestand-Bilder ohne jede Herkunftsangabe | jedes `p*.jpg` auf allen sechs Seiten trägt „Bild: Archiv tamil.de“ (oder die Sammelzeile der Rubrikkacheln). Messung über alle Seiten und Breiten: 0 Bilder ohne Nachweis, 0 versteckte Nachweise | geschlossen (Hinweis P3-2) |
| 4 | Rubrik-Aufmacher am Handy mehr als drei Zeilen | `rubrik.html` 390: 26 px, 3 Zeilen („Steinmeier beim Tempelfest …“); 820 und 1280: 34 px, 3 Zeilen | geschlossen |
| 5 | Listen-Schlagzeilen am Handy mehr als vier Zeilen | 390, alle sechs Seiten: höchstens 4 Zeilen (Startseite 17 px; `termine.html` 19 px: INAIVU, Straßenfeste, Leuk je 4; `suche.html` INAIVU 4; `rubrik.html` Leuk, Mango je 4; `artikel.html` Straßenfeste 4) | geschlossen |

## Harte Kriterien

| # | Kriterium | Handy 390 | Desktop 1280 | Stand |
|---|---|---|---|---|
| 1 | Viele Geschichten | 2 ganz sichtbar (Aufmacher + Koovagam) | 4 | erfüllt |
| 2 | Kopf ≤ 152 px, Aufmacher ab ≤ 480 px | 150 px; ab 295 px | 122 px; ab 414 px | erfüllt |
| 3 | Drei Stufen, Aufmacher ≥ 1,25 × Nebenstück, ≤ 2 Familien | 30 : 21 px (1,43); 1 Familie (Libre Franklin) | 40 : 20 px (2,0); 1 Familie | erfüllt |
| 4 | Größte Schrift, zweitgrößte, Zeilen, Versalien | 30 px (Aufmacher), zweitgrößte 22 px; Aufmacher 3 Zeilen, andere ≤ 4; Versalien > 14 px: 0 | 40 px (Aufmacher), zweitgrößte 26 px; Aufmacher 2 Zeilen, andere ≤ 3; 0 | erfüllt |
| 5 | Rot ≤ 3 %, keine rote Schrift > 20 px, kein zweiter Buntton | 0,05 %; größte rote 13 px; bunt = rot | 0,04 %; 13 px; bunt = rot | erfüllt |
| 6 | Genau zwei dunkle Flächen, erster Bildschirm ≤ 12 % dunkel | `nav.band` + `#diese-woche`; 6,4 % | dieselben zwei; 5,8 % | erfüllt |
| 7 | Keine Effekte, Verlauf nur unter Schrift im Bild | Radius 0, Schatten 0, gedreht 0, Breite normal; Verlauf nur in `.imbild` | gleich | erfüllt (zur Form des Verlaufs: P1-1) |
| 8 | Kein Baukasten | keine Kästen, Pillen, Icons, Knöpfe an Anreißern; 3 gestaltete Kacheln auf „Fläche auf Dunkel“ | gleich | erfüllt |
| 9 | Überall ein Bild | `anreisser_ohne_bild` leer; Grafik 3 (Scene, Ramayana, Diwali in Basel) | gleich | erfüllt |
| 10 | Ein Format für Dachzeile und Datum, ≤ 3 Bildformate | „Rubrik \| Datum“ überall; 3:2, 16:9, 2,35:1 | gleich | erfüllt |
| 11 | Bildgröße | über Dateibreite: keins; über halber Breite: keins | über Dateibreite: keins; über halber Breite: rb-30 (Aufmacher), rb-84 (große Kachel „Diese Woche“), rb-48 (große Kachel „Küche“), alle drei zulässig | erfüllt |
| 12 | Helle Schrift ≥ 4,5 : 1 an der hellsten Stelle | 50 Stellen, kleinster Wert 5,45 | 59 Stellen, kleinster Wert 5,47 | erfüllt |
| 13 | Bewegung | Maßstab 1,03; längster Übergang 0,35 s; 0 Animationen; reduziert 0 Übergänge; fest nur `nav.band`, 46 px | gleich | erfüllt |
| 14 | Kein Überlauf, keine Konsolenfehler | 0 px, 0 Fehler (alle 6 Seiten, auch 820) | 0 px, 0 Fehler | erfüllt |
| 15 | „Diese Woche“ spätestens im dritten Bildschirm | Oberkante 1855 px (≤ 2532) | – | erfüllt |
| 16 | Paarvergleich | durchgeführt (unten) | durchgeführt | erfüllt |

## Paarvergleich

**mix-ordnung gegen `klar2`** (gleiche Ordnung, Vorstufe)
- Desktop: Rechts neben dem Aufmacher steht bei `klar2` eine Textliste „Weitere Meldungen“ mit Daumenbildern. Hier
  steht dort ein Nebenstück mit einem rund 605 × 340 px großen Bild (Koovagam), darunter zwei Meldungen mit Bild. Der
  erste Bildschirm besteht damit zu etwa zwei Dritteln aus Foto statt zur Hälfte. Er ist sichtbar bildstärker.
- Kopf: Logo, Datum und die Hinweise „Diese Woche“ stehen in einer Zeile, das Band liegt darunter: 122 px statt
  rund 150 px bei `klar2`. Die Seite beginnt dadurch früher mit Bild.
- Handy: Bei `klar2` folgt auf den Aufmacher ein Vorspann aus vier Zeilen und dann der Streifen mit den
  Rubrikkacheln. Hier folgen ein Satz und sofort ein Vollbild in 16:9. Was `klar2` ruhiger macht: Unter jedem
  Anreißer steht keine graue Nachweiszeile. Hier kommt mit dem Nachweis eine vierte Textebene dazu (P2-1).

**gegen BBC News (Vorbild)**
- BBC setzt Bild oben, Schlagzeile darunter, Meldungen mit Daumenbild links, getrennt durch Haarlinien. Die Liste
  hier ist gleich gebaut: Linie, Daumen rechts mit 96 px, Dachzeile „Rubrik | Datum“. Das wirkt vertraut, nicht
  generisch.
- Unterschied: BBC zeigt auf der Startseite bei keinem Anreißer einen Bildnachweis. Hier stehen am Desktop im
  ersten Bildschirm drei Nachweise, zwei davon zweizeilig in der Textspalte.

**gegen Spiegel (Vorbild)**
- Spiegel zeigt ein großes Bild über die Spaltenbreite, die Dachzeile rot, die Schlagzeile schwarz. Hier liegt die
  Schlagzeile im Bild (erlaubt), die Dachzeile im Bild ist hell. Die Hierarchie aus großer Schlagzeile, kleiner
  Dachzeile und Bild ist gleich klar.
- Spiegel trennt Bild und Text scharf, ohne Abdunkeln. Hier liegt die Schlagzeile auf einem Verlauf. Am Desktop fällt
  das kaum auf (39 % der Bildhöhe), am Handy deckt der Verlauf drei Viertel des Bildes (P1-1).

**gegen Runde 2 (abgelehnt: „altbacken“)**
- Runde 2: cremefarbener Grund, Anzeige über dem Aufmacher, runde Knöpfe als Rubriken, farbige Punkte. Hier: kühles
  Weiß, keine Anzeige im ersten Bildschirm, rechteckige Bilder mit Radius 0, Rubriken als Text im Band. Kein Rückfall.

**gegen Runde 4, Raster (abgelehnt: „zu laut, Baukasten“)**
- Runde 4: rotes Titelwort „KANGUVA“ über die volle Breite, schmale Auszeichnungsschrift, Navigation in Versalien in
  Rahmenzellen. Hier: Rot bei 0,04 % der Fläche, größte Schrift 40 px in Weiß im Bild, Libre Franklin in normaler
  Breite, Navigation in normaler Schreibung ohne Rahmen. Kein Rückfall.

Antworten auf die zwei Fragen aus Brief 10.4: Neben `klar2` wirkt die Probe sichtbar bildstärker und weniger
„classic“. Am Desktop kommt das von der zweiten großen Bildfläche rechts oben, am Handy vom Vollbild direkt nach dem
Aufmacher. Laut, verspielt oder Baukasten ist nichts geworden. Am nächsten an „billig“ liegt der Verlauf am Handy
(P1-1).

## Befunde

### P0
keine. `shots.mjs`: 18 Aufnahmen, 0 Fehler, 0 Konsolenmeldungen, 0 leere Bilder, 0 fehlende Schriften, 0 zu kleine
Tippflächen, 0 Tamil ohne `lang`.

### P1

**P1-1 · Verlauf deckt am Handy zwei Drittel bis drei Viertel des Bildes und zeigt eine Oberkante (Befund 1 aus
Runde 1, nicht geschlossen).** Verbotsliste: Erlaubt ist ein heller Titel auf einem Verlauf „ohne Platte“.
- Ursache, `mix-ordnung.css` Zeilen 38–45: `--verlauf` geht in 36 px von 0 auf 0,62 Deckkraft, `--verlauf-kurz` in
  20 px von 0 auf 0,64. Darunter bleibt die Deckkraft gleich bei 0,62–0,70. Die Rampe ist so kurz, dass sie auf
  ruhigem Grund als Kante sichtbar wird. Dahinter liegt eine fast gleichmäßige Abdunklung über den ganzen
  Textkasten, und der Kasten ist am Handy so hoch wie Dachzeile, drei Zeilen Titel und Innenabstand.
- Ort und Messung:
  - `rubrik.html`, 390, Aufmacher „Steinmeier beim Tempelfest“: Verlauf 173 von 260 px (66 %). Im blauen Himmel
    fällt die Helligkeit von 163 auf 103 auf nur 27 px (Grauwert, Spalte x 10–90). Man sieht eine waagerechte Kante
    über die volle Breite, darunter liegt ein grauer Schleier über zwei Dritteln des Fotos. Das ist die Platte.
  - `index.html`, 390: Aufmacher 186/260 px (72 %), Kanguva 150/201 (74 %), Sardar 155/239 (65 %), Küche groß
    155/239 (65 %), „Bremen“ 136/201 (68 %). Bei Aufmacher und Kanguva sind drei Viertel des Fotos abgedunkelt.
    Das große Bild wirkt dadurch kleiner, als es ist.
  - `index.html`, 820, Küche, kleine Kachel „Bremen: Vater und Sohn …“: Der Verlaufskasten ist 158 px hoch, das Bild
    nur 140 px (Titel 18 px, 4 Zeilen). Das ganze Bild liegt unter 0,64–0,70 Tinte, die Dachzeile stößt an die
    Oberkante. Neben „Dosa“ und „Payasam“ ist diese Kachel sichtbar eine dunkle Fläche.
  - Desktop 1280 ist unkritisch: Aufmacher 39 %, große Kino-Kachel 32 %, große Küche-Kachel 24 %. Bei der großen
    Küche-Kachel ist die Oberkante über den weißen Bechern links noch zu sehen.
- Behebung:
  1. Rampe lang und weich machen: den Verlauf etwa 64 px über der Dachzeile beginnen lassen und mit mehreren Stufen
     anlegen (zum Beispiel 0 → 0,25 bei 35 % → 0,55 bei 70 % → 0,72 bei 100 %). Die volle Deckkraft liegt dann nur
     unter den letzten zwei Zeilen. Den Kontrast danach mit `aufnahmen.mjs` neu messen (`helle_schrift`, mindestens
     4,5 : 1).
  2. Am Handy beim Aufmacher und bei der Rubrik ein höheres Bildformat nehmen (4:3 statt 3:2, im Rahmen der drei
     Formate), damit der Text höchstens die Hälfte des Bildes deckt.
  3. Bei 820 die kleinen Küche-Kacheln mit dem Titel unter das Bild setzen, wie bei „Rathamaarey“. Oder ab 4
     Titelzeilen das 16:9-Format gegen 4:3 tauschen. Eine Kachel, deren Verlauf höher ist als das Bild, darf es
     nicht geben.

### P2

**P2-1 · Nachweiszeilen unter jedem Anreißer, an zwei verschiedenen Stellen (neu durch die Behebung von Befund 2
und 3, im ersten Bildschirm sichtbar).**
- Ort: `index.html` 1280, erster Bildschirm. Beim Nebenstück steht „Foto: D Neethidoss / …“ direkt unter dem Bild.
  Bei den Meldungen „Vaani Vizha“ und „Bundestagsdrucksache“ steht der Nachweis zweizeilig in der Textspalte unter
  der Schlagzeile, 220 px vom Daumenbild entfernt. Am Handy steht er zwischen Bild und Dachzeile. Jede Meldung hat
  damit vier Textebenen (Dachzeile, Titel, zwei Zeilen Nachweis). Die Liste wird unruhiger als bei `klar2`, BBC oder
  Spiegel, die auf der Startseite keine Nachweise an Anreißern zeigen.
- Behebung: Eine Regel für alle Anreißer. Entweder steht der Nachweis immer direkt unter dem Bild, einzeilig, in
  Bildbreite abgeschnitten und vollständig im `title`/Link. Oder, besser für Daumenbilder unter 160 px: Die
  Nachweise sammeln sich am Ende des Blocks in einer Zeile, wie es die Probe bei den Rubrikkacheln schon macht. Am
  Aufmacher und an den großen Kacheln bleibt der Nachweis am Bild.

**P2-2 · Dunkler Anteil auf `termine.html`** (nach Entscheidung der Hauptsitzung P2; die 12-%-Grenze gilt für die
Startseite). Die Seite beginnt am Handy bei 317 px mit „Diese Woche im Kino“ auf Tinte. Ich habe das nicht neu
bewertet.

### P3

**P3-1 · Lizenz ohne Link.** Nur die Bildunterschrift im Artikel verlinkt die Commons-Datei. Alle anderen Nachweise
nennen „CC BY-SA 3.0/4.0“ als Text. CC BY-SA verlangt einen Hinweis auf die Lizenz, wo es zumutbar ist, als Link.
Für das Theme: Urheber auf die Commons-Dateiseite verlinken, Lizenzkürzel auf den Lizenztext. Die Quellen stehen
schon in `rueckblick.json` (`quelle_bild`).

**P3-2 · „Archiv tamil.de“ bei Filmbildern.** `p9711.jpg` (Kanguva-Szenenbild) und `p9697.jpg` (Team von
„Rathamaarey“) sind ihrer Art nach Verleih- oder Pressebilder. „Archiv tamil.de“ sagt, woher das Bild kommt, aber
nicht, wem die Rechte gehören. Für die Probe reicht das (Auftrag: „Altbestand“ zulässig). Auf der echten Seite
sollte der Verleih genannt werden, wo er bekannt ist (zum Beispiel „Bild: Verleih / Archiv tamil.de“).

## Was trägt
1. Bildstärke, ohne laut zu werden: Der erste Desktop-Bildschirm besteht zu zwei Dritteln aus Foto, Rot liegt bei
   0,04 %. Das Wow kommt aus Bildfläche, nicht aus Schrift oder Farbe.
2. Die Ordnung aus `klar2` hält: ein Format für Dachzeile und Datum, Haarlinien statt Kästen, Radius 0, eine Familie,
   alle 16 Messwerte im Rahmen, auf allen sechs Seiten bei drei Breiten ohne Fehler.
3. Nachweise vollständig und nach Stichprobe korrekt: 0 Bilder ohne Herkunft auf allen Seiten. Die Sammelzeile bei
   den Rubrikkacheln zeigt, wie es auch für Daumenbilder ruhig ginge (P2-1).

## Bedienbarkeit (nur zur Information)

| Heuristik | 0–4 | Satz |
|---|---|---|
| 1 Sichtbarkeit des Status | 3 | Aktive Rubrik im Band mit Linie markiert (auf `rubrik.html` sichtbar). |
| 2 Sprache der Leser | 4 | Klare deutsche Dachzeilen, Daten ausgeschrieben. |
| 3 Kontrolle und Freiheit | 3 | Band steht beim Scrollen, Logo führt zur Startseite. |
| 4 Einheitlichkeit | 3 | Anreißer einheitlich; Nachweis an zwei Stellen (P2-1). |
| 5 Fehlervermeidung | 3 | Keine Formularfallen gesehen; Kontakt mit gekennzeichneten Beispielwerten. |
| 6 Erkennen statt Erinnern | 4 | Rubriken immer sichtbar, Dachzeile nennt die Rubrik. |
| 7 Flexibilität | 3 | Kopfhinweise „Diese Woche“ als Abkürzung am Desktop; am Handy entfallen sie. |
| 8 Ästhetik und Reduktion | 3 | Ruhig; Abzug für Nachweiszeilen und den hohen Verlauf am Handy. |
| 9 Fehler erkennen | – | Nicht prüfbar (keine Fehlerzustände in der Probe). |
| 10 Hilfe | 3 | Kontaktseite klar; Suche mit Ergebnisliste. |
