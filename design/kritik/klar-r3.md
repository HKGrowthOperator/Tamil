# Prüfung klar, Runde 3
Harte Kriterien: 12 von 12 erfüllt · P0: 0 · P1: 0 · P2: 5

Geprüft am 10.11.2026: `index.html` und `artikel.html` bei 390 und 1280, bei 820 nur der Überlauf. Kennzahlen aus
`design/vergleich/kennzahlen/klar.json`, Technik aus `shots.mjs` (`bericht.json`), dazu eigene Messung mit Playwright
(Zeilen, Kanten, Bildbreiten, Zeichen je Zeile, Kontrast, Tippflächen, Fokus).

## Erster Eindruck (3 Sätze)

Am Handy steht nach fünf Sekunden fest, was wichtig ist: Bild, rote Dachzeile, eine dreizeilige Schlagzeile in 28 px,
darunter eine Liste mit kleinen Bildern links. Das ist ein BBC-Aufbau ohne Zutaten: kühles Weiß, nur Haarlinien, Rot
nur in 13-px-Dachzeilen, eine Schriftfamilie. Am Desktop steht viel auf einem Blick (9 Schlagzeilen); die
Schwächen liegen in den Einzelheiten unterhalb davon: ungleich lange Vorspänne, eine rechte Spalte, die früh endet,
ein gleichförmiger Küchenblock und ein Termin, bei dem das Datum am kleinsten gesetzt ist.

## Harte Kriterien

| # | Kriterium | Messwert Handy (390 × 844) | Messwert Desktop (1280 × 800) | Ergebnis |
|---|---|---|---|---|
| 1 | Viele Geschichten | 2 ganz sichtbar (Aufmacher + „Sri Lanka schafft Visum“); jede Schlagzeile `h2`/`h3` in einem Link | 9 ganz sichtbar | erfüllt |
| 2 | Kopf | `kopfleiste_hoehe` 112 px (≤ 120), Logo und Rubriken im `<header>`; Aufmacher-Schlagzeile ab 369 px (≤ 480) | Kopf 90 px | erfüllt |
| 3 | Drei Stufen, Verhältnis, Familien | 28 / 19 / 17 px → 1,47-fach; 1 Familie (Libre Franklin) | 34 / 22 / 18 px → 1,55-fach; 1 Familie | erfüllt |
| 4 | Größte Schrift, Zeilen, Versalien | 28 px; Aufmacher 3 Zeilen, sonst höchstens 4 (drei Nebenstücke mit 4); 0 Versalien über 14 px | 34 px; Aufmacher 3 Zeilen, sonst höchstens 3; 0 Versalien | erfüllt |
| 5 | Rot | 0,2 % Fläche; größte rote Schrift 13 px; kein zweiter Buntton | 0,18 %; 13 px; kein zweiter Buntton | erfüllt |
| 6 | Keine Effekte | Radius 0, Schatten 0, gedreht 0, Schriftbreite normal | ebenso | erfüllt |
| 7 | Anreißer ohne Kasten, Icon, Knopf | keine; Rubrikzeile reine Textlinks; Fläche nur am Dienstblock (laut Brief erlaubt) | ebenso | erfüllt |
| 8 | Ein Format Dachzeile/Datum, ≤ 2 Bildformate | Meta überall 13 px, Rubrik Rot 600, Datum Leise 400, Trennstrich 1 px; Datum „17. Juli 2024“; ein Bildformat (16:9, 1,778) | ebenso | erfüllt |
| 9 | Kein Bild über natürlicher Breite (2×) | Aufmacher 390 px (Datei 1382, Grenze 691); Nebenstücke 112, Küche 171 (Grenze 600) | Aufmacher 402, Nebenstücke 208, Küche 276; Artikelbild 680 (Grenze 691) | erfüllt |
| 10 | Kein Überlauf, keine Konsolenfehler | 0 px, 0 Fehler (auch 820: 0 px) | 0 px, 0 Fehler | erfüllt |
| 11 | Dienstblock spätestens 3. Bildschirm | beginnt bei 2242 px (3. Bildschirm reicht bis 2532) | – | erfüllt |
| 12 | Paarvergleich, Messwerte in der Spanne | größte Schlagzeile 28 (18–32), 2 Schlagzeilen (1–3), Aufmacher ab 369 (332–588), Radius 0, Schatten 0, Farbe 0,2 % (< 8), Gewicht 650 (350–800), 1 Bildformat | 34 px (18–36); 9 Schlagzeilen und Kopf 145 px liegen außerhalb, sind aber laut Auftrag gewollt (keine Anzeigen) | erfüllt |

## Paarvergleich

**klar neben BBC (Handy und Desktop)**
- Aufbau fast deckungsgleich: Bild über volle Breite, Schlagzeile, Vorspann, dann Liste mit Bild links. BBC setzt
  Zeit und Rubrik grau **unter** die Schlagzeile, klar setzt die Dachzeile rot **darüber**. Dadurch stehen im ersten
  Handy-Bildschirm drei rote Wörter; bei 0,2 % Rotanteil ruhig, aber sichtbar mehr Markenfarbe als BBC (0,0 %).
- Die Listenbilder sind bei klar 112 × 63 px (29 % der Breite), bei BBC etwa 132 px (34 %). Bei BBC erkennt man den
  Bildinhalt (Gerichtszeichnung), bei klar ist der Reisepass ein kleines Grau-Blau. Dafür hat klar 234 px Textspalte;
  drei von vier Schlagzeilen brauchen trotzdem vier Zeilen, wie auch bei BBC.
- BBC trennt den Aufmacher mit einer dunkleren, kräftigen Linie von der Liste; klar nutzt überall dieselbe Haarlinie,
  die dunkle Linie erst über „Weitere Meldungen“. Am Desktop hat klar mehr Inhalt im ersten Bildschirm (9 statt etwa
  2 Schlagzeilen, keine Anzeige, kein Abo-Band); die BBC wirkt durch das klare Blocklogo und die Serifenschlagzeile
  markanter. Das klar-Logo ist ein kleines Rasterbild (bekannt, P3).

**klar neben tagesschau (Handy)**
- tagesschau nutzt Pillen in der Rubrikzeile, ein blaues Kästchen „INTERVIEW“ in Versalien, Blau als Schlagzeilenfarbe
  und ein festes App-Band unten. klar hat nichts davon: Rubriken als Text, Schlagzeile in Tinte, keine feste Leiste.
- tagesschau zeigt im ersten Bildschirm eine Schlagzeile, klar zwei. Die Vorspanngröße ist ähnlich (tagesschau größer,
  etwa 18 px, klar 17 px).

**klar neben Runde 2 (390 und 1280)**
- Runde 2: warmer Cremegrund, braungraue Tinte, Pillen-Rubriken, Anzeige über dem Aufmacher, abgerundetes Bild, bunte
  Rubrikpunkte; am Handy steht im ersten Bildschirm **keine** Schlagzeile. klar: kühles Weiß (oklch 0.985/250),
  fast schwarze kühle Tinte, Textrubriken, Bild ohne Radius, Rubriken nur als Wort, Aufmacher-Schlagzeile bei 369 px.
- Am Desktop hat Runde 2 eine laute 60-px-Schlagzeile unter einem großen Bild und eine Liste mit Bildern rechts;
  klar setzt das Bild halb neben die Schlagzeile (34 px) und die bildlose Meldungsliste rechts. klar ist dichter und
  geordneter; beobachtbar an den gleichen Linksachsen (Dachzeile und Schlagzeile der Nebenstücke beide bei 272 px) und
  dem einen Bildformat.

**klar neben Runde 4 „Raster“ (390 und 1280)**
- Runde 4: rotes Titelwort in etwa 100 px, schmal verzerrte Grotesk, Versalien, rote Linienraster, Daumenleiste unten.
  klar: größte Schrift 28 px, normale Breite, keine Versalien, Linien grau 1 px, keine feste Leiste.
- Runde 4 zeigt eine Geschichte; klar zwei (Handy) und neun (Desktop).

## Befunde

### P0
keine. `bericht.json`: 0 Konsolenfehler, 0 leere Bilder, alle Schriften geladen, 0 Überlauf bei 390/820/1280.

### P1
keine.

### P2

1. **Desktop 1280, Nebenstücke: Vorspänne ungleich lang.** Gemessen 2 / 1 / 3 / 3 Zeilen (119 / 45 / 177 / 145
   Zeichen); Parai hat nur „Parai bedeutet „Sprechen oder Kommunizieren“.“ Die Anreißer sind dadurch 153 / 153 / 190 /
   190 px hoch, im ersten Bildschirm sitzt ein Einzeiler neben einem Zweizeiler. Das Kürzen am Satzende ist erlaubt,
   aber der Stummel wirkt wie ein abgeschnittener Text. **Behebung:** alle vier Vorspänne auf zwei Zeilen begrenzen
   (für Parai den zweiten Satz dazunehmen, „…zurückreicht.“, und die längeren auf einen Satz von etwa 2 Zeilen
   bringen), oder eine feste Zeilenzahl mit `line-clamp: 2` setzen, die an einem Satzende endet.
2. **Desktop 1280, rechte Spalte endet früh.** Die Meldungsliste endet bei etwa 775 px, die Nebenstücke links bei
   etwa 1075 px; darunter bleiben rund 300 px leere Spalte, bevor der Küchenblock beginnt. Sichtbar beim ersten
   Scrollen. **Behebung:** den Dienstblock „Diese Woche“ (Kino und Termin) am Desktop in die rechte Spalte unter die
   Meldungen setzen; das füllt die Lücke mit dem Eigenen von tamil.de und zieht es nach oben.
3. **Handy 390 und Desktop, Dienstblock „Diese Woche“, Termin: Datum am kleinsten.** „Samstag, 21. November 2026“
   steht in 13 px Leise, der Ort darunter in 16 px Leise, der Text in 16 px Tinte. Bei den Kino-Einträgen steht die
   Kernangabe („11 Kinos in Deutschland“) in 16 px halbfett. Beide Spalten folgen damit verschiedenen Mustern, und die
   wichtigste Angabe eines Termins ist die unauffälligste. **Behebung:** Termin parallel zum Kino setzen: Titel 18 px,
   Datum 16 px halbfett (wie die Kinozahl), Ort · Veranstalter 16 px Leise, Text 16 px.
4. **Handy 390, Nebenstücke: drei von vier Schlagzeilen bei vier Zeilen.** Parai, Konzert und Kanguva brauchen in der
   234 px breiten Textspalte vier Zeilen (Ziel laut Brief drei). Bei Kanguva steht dadurch „14. November“ allein in
   einer kurzen Zeile. Das liegt in der erlaubten Grenze und ist bei BBC ähnlich, macht den zweiten Bildschirm aber
   zu einer Folge von Viererblöcken (148 px hoch). Gemessen: `text-wrap: pretty` oder `wrap` ändert die Zeilenzahl
   nicht. **Behebung:** Bild auf 104 px und Spaltenlücke auf 10 px verringern und nachmessen, ob drei Zeilen reichen; sonst
   die vier Zeilen hinnehmen und nur den Zeilenfall bei Kanguva prüfen (das Zusammenhalten von `Kino-Highlight` und
   `14.&nbsp;November` erzeugt die kurze Zeile).
5. **Rubrikblock „Küche“, Handy 2 × 2 und Desktop 4 × 1: vier gleichförmige Kacheln.** Gleiche Bildgröße, gleiches
   Datum („16. Juli 2024“ viermal), Titel aus einem Wort, kein Vorspann. Ohne Kasten und ohne Schatten bleibt es
   erlaubt, aber es ist das einzige Raster ohne jede Abstufung auf der Seite und kommt dem verbotenen Muster
   „identische Kartenraster“ am nächsten. **Behebung:** den ersten Beitrag größer (Bild halbe Breite, Vorspann von
   einem Satz), die drei anderen als Liste mit kleinem Bild wie die Nebenstücke; am Handy die drei als Zeilen mit Bild
   links.

### P3

- **Handy 390, Nebenstücke ohne Vorspann** (`display: none`). Laut Auftrag zulässig; BBC verfährt ebenso. Für
  Ältere fehlt damit am Handy jeder Kontext außer der Schlagzeile; prüfen, ob wenigstens das Kino-Stück einen
  Satz bekommt.
- **Handy 390, Nebenstück und Meldung liegen nah beieinander:** 19 px / 650 gegen 17 px / 600. Der Unterschied ist
  sichtbar, aber knapp; das Bild trägt die Unterscheidung. Meldung auf 400–500 Gewicht senken würde die Stufe klarer
  machen.
- **820, Aufmacher-Vorspann 79 bis 82 Zeichen je Zeile** (17 px auf 680 px). Außerhalb des Prüfumfangs, für den
  Ausbau `max-width: 34em` setzen.
- **Logo:** kleines Rasterbild, Unterzeile in Kopfgröße unlesbar (bekannt, Brief Abschnitt 9).
- **Inhalt:** Titel „Das ursprüngliche Musik“ ist ein Grammatikfehler aus dem Bestand; unverändert übernommen, also
  richtig nach Brief, aber für die Redaktion zu melden.

## Leser und Inhalte

- **65-Jähriger am Handy:** Fließtext im Artikel 18 px, Zeilenabstand 1,6, im Mittel 38 Zeichen je Zeile (höchstens
  44); Desktop 19 px, Mittel 54, höchstens 66 Zeichen (≤ 70). Vorspann im Artikel 19 px / 500. Kontrast: Tinte auf
  Grund 16,9:1, Leise auf Grund 7,1:1, Leise auf Fläche 6,7:1, Rot auf Grund 6,1:1, Rot auf Fläche 5,7:1 (alle
  ≥ 4,5). Dachzeile und Datum 13 px (Untergrenze der Spanne 12–14, gut lesbar durch 7:1). Tippflächen: keine unter
  44 px (Rubriken 44 px hoch, ganze Anreißer als Ziel, „Per WhatsApp teilen“ 138 × 44). Fokus: 2 px Umriss in Tinte
  auf jedem Link, mit Abstand 3 px, sichtbar (am Handy scrollt die Rubrikzeile beim Tabben mit).
- **19-Jährige in fünf Sekunden:** Aufmacher mit Bild und klarer Schlagzeile, darunter sofort die nächste Geschichte;
  Rubrik steht über jeder Schlagzeile. Kino und Termine liegen am Handy im dritten Bildschirm.
- **Inhalte gegen `inhalte.json`:** Rubriken vollständig in Reihenfolge; Aufmacher, vier Nebenstücke, sechs
  Meldungen, vier Küchenbeiträge, zwei Filme, ein Termin, alle in der vorgegebenen Reihenfolge, Titel und Daten
  unverändert. Vorspänne jeweils am Satzende gekürzt. Kino: Titel, Zahl der Kinos, Land, fünf Orte und „6 weitere
  Städte“, nichts ergänzt. Termin: Datum, Ort, Veranstalter, Text unverändert. Küche ohne Dachzeile (erlaubt).
  Artikel: Dachzeile, Schlagzeile, Vorspann, Datum, Lesezeit 2 Min., Bild, genau die drei Absätze unverändert, keine
  Autorenzeile, kein Bildnachweis, WhatsApp-Link ohne Skript. Nichts erfunden, nichts weggelassen.

## Was trägt

1. Zahlen und Bild stimmen überein: 28/34 px größte Schrift, 0,2 % Rot, Radius 0, eine Familie, ein Bildformat; der
   erste Bildschirm sieht aus wie eine Nachrichtenseite und nicht wie ein Baukasten.
2. Gleiche Kanten: Dachzeile und Schlagzeile der Nebenstücke stehen auf einer Linksachse (Handy 140 px, Desktop
   272 px), die Meta-Zeile hat überall dasselbe Format.
3. Der Artikel ist ruhig und gut lesbar (18/19 px, 1,6, ≤ 66 Zeichen), mit schlichtem Teilen-Link.

## Bedienbarkeit (nur zur Information)

| Heuristik (Nielsen) | 0–4 | Satz |
|---|---|---|
| 1 Sichtbarkeit des Systemzustands | 3 | Aktive Rubrik im Artikel rot und halbfett; auf der Startseite keine aktive Rubrik (passend). |
| 2 Übereinstimmung mit der Welt | 4 | Vertraute Begriffe, Daten mit Jahr, „Im Kino“, „Termine“. |
| 3 Kontrolle und Freiheit | 3 | Logo führt zurück; seitlich laufende Rubrikzeile ohne sichtbaren Hinweis außer dem angeschnittenen Wort. |
| 4 Konsistenz | 3 | Meta-Format einheitlich; Termin weicht im Muster vom Kino ab (P2-3). |
| 5 Fehlervermeidung | 3 | Ganze Anreißer als Ziel, ausreichend große Flächen. |
| 6 Erkennen statt Erinnern | 4 | Rubrik an jeder Geschichte. |
| 7 Flexibilität | 2 | Keine Suche, kein Menü für mehr (Skizze, nicht verlangt). |
| 8 Ästhetik und Minimalismus | 3 | Ruhig; Küchenraster und Vorspannlängen am Desktop unausgeglichen. |
| 9 Fehlermeldungen | – | nicht Teil der Skizze. |
| 10 Hilfe | – | nicht Teil der Skizze. |
