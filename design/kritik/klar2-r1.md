# Prüfung klar2, Runde 1
Harte Kriterien: 15 von 16 erfüllt · P0: 0 · P1: 1 · P2: 9

Gemessen am 10.11.2026 mit `node design/vergleich/aufnahmen.mjs klar2` (Kennzahlen `design/vergleich/kennzahlen/klar2.json`)
und `node tools/shots.mjs … --kacheln` (390/820/1280, Bericht im Scratch-Ordner). Werte mit „(von Hand)“ stammen aus
einem eigenen Messskript (Rahmenmaße der Bilder, Sprungziele, Fokus, Kontrast bei 820 nach dem Verfahren von
`kontrast.py`).

## Erster Eindruck (3 Sätze)

Am Handy steht oben ein randloses Foto mit weißer Schlagzeile im Bild, darunter ein Streifen Bildkacheln und dann die
vertraute Liste aus `klar` mit roten Dachzeilen und feinen Linien. Am Desktop füllt das Aufmacherbild (780 × 585 px)
fast zwei Drittel des Schirms, rechts laufen sechs Meldungen mit kleinen Bildern, das dunkle Rubrikband trennt den
Kopf klar ab. Es wirkt wie eine bildstarke Nachrichtenseite, nicht wie ein Plakat; schwächer sind die Übergangsbreite
820 px und die Tastaturführung um das stehende Band.

## Harte Kriterien (Brief 10.4)

| # | Kriterium | Handy (390 × 844) | Desktop (1280 × 800) | Ergebnis |
|---|---|---|---|---|
| 1 | Viele Geschichten | 2 ganz sichtbar (Aufmacher, „Sri Lanka schafft Visum…“); alle als h2/h3 mit Link | 6 ganz sichtbar | erfüllt |
| 2 | Kopf ≤ 152 px; Aufmacher-Schlagzeile ≤ 480 px | `kopfleiste_hoehe` 147 (Kopfzeile 44 + Logo 56 + Band 46); `erste_schlagzeile_ab` 323 | 167; 264 (erste Meldung rechts), Aufmacher-Titel ab 662 | erfüllt |
| 3 | Drei Stufen, Aufmacher ≥ 1,25 × Nebenstück, ≤ 2 Familien | 30 / 19 px = 1,58; Nebenstück 19 px/650, Meldung 17 px/600 (von Hand); 1 Familie (Libre Franklin) | 40 / 20 px = 2,0; Meldung 17 px/600 | erfüllt |
| 4 | Größte Schrift ≤ 34/44 und = Aufmacher; zweitgrößte ≤ 24/28; Zeilen; Versalien | 30 px Aufmacher; zweitgrößte 22 px; Aufmacher 3 Zeilen, längste andere 4 (Parai, Konzert, Maya, Mango); Versalien > 14 px: 0 | 40 px Aufmacher; zweitgrößte 26 px (Kanguva, Kottu Roti); Aufmacher 2 Zeilen, längste andere 4 (Maya, Mango); 0 | erfüllt |
| 5 | Rot ≤ 3 %, keine rote Schrift > 20 px, kein zweiter Buntton | 0,13 %; größte rote 13 px | 0,09 %; 13 px | erfüllt |
| 6 | Genau zwei dunkle Flächen, ≤ 12 % dunkel im 1. Schirm | `nav.band` + `section#diese-woche`; 6,4 % | dieselben zwei; 5,8 % | erfüllt |
| 7 | Keine Effekte, Verlauf nur unter Schrift im Bild | Radius 0, Schatten 0, gedreht 0, Breite normal; Verläufe nur `.imbild` und `.kachel__name` (CSS gelesen) | dasselbe | erfüllt |
| 8 | Kein Baukasten | keine Kästen um Anreißer, keine Pillen, kein Knopf; Fläche nur an den drei `.grafik` | dasselbe | erfüllt |
| 9 | Überall ein Bild | `anreisser_ohne_bild` leer; `anreisser_mit_grafik` 3 (Scene, Ramayana, Diwali) | dasselbe | erfüllt |
| 10 | Ein Format für Dachzeile und Datum; ≤ 3 Bildformate | Dachzeile „Rubrik \| T. Monat JJJJ“ überall gleich; Bildformate (von Hand) 4:3, 16:9, 2,1:1 = 3 | **4 Formate (von Hand): 4:3 (Aufmacher, Kanguva, Kottu Roti), 16:9 (Kacheln, Nebenstücke, Meldungen), 1,59:1 (Rathamaarey-Kachel, 384 × 241), 2,11:1 (Payasam, Biryani, Dosa, 384 × 182)**; bei 820: 4:3, 16:9, 1,28:1 (Rathamaarey 378 × 296) | **verletzt** |
| 11 | Bildgröße | `bilder_ueber_dateibreite` leer; `bilder_ueber_natuerlicher_breite` leer | leer; über halber Dateibreite nur p9631 (Aufmacher, 780/1382) und p9600 (große Küche-Kachel, 792/1558), beide erlaubt | erfüllt |
| 12 | Helle Schrift ≥ 4,5 : 1 | 43 Stellen, kleinster 5,56 („13. Oktober 2024“ auf p9697); `unter_4_5` leer | 52 Stellen, kleinster 5,46 („16. Juli 2024“, Küche); leer. Bei 820 (von Hand): kleinster 4,94 („13. Oktober 2024“ über dem weißen Hemd in p9697) | erfüllt |
| 13 | Bewegung | Maßstab 1,03; längster Übergang 0,35 s; Animationen 0; bei „reduziert“ 0 Übergänge; fest nur `nav.band` sticky, 46 px | 1,03; 0,35 s; 0; 0; `nav.band` 48 px | erfüllt |
| 14 | Kein Überlauf, keine Konsolenfehler | 0 px; 0 Fehler (index und artikel) | 0 px bei 820 und 1280; 0 Fehler | erfüllt |
| 15 | „Diese Woche“ ≤ 2532 px am Handy | Oberkante 2025 px | (Desktop 1550 px) | erfüllt |
| 16 | Paarvergleich, kein Messwert außerhalb der Grenzen | alle Kennzahlen in den Grenzen von 10.4 außer Nr. 10 (dort gezählt). Hinweis: `erste_schlagzeile_ab` 323 px liegt 9 px unter der Spanne der Marken (332 bis 588); 10.4 verlangt nur ≤ 480, deshalb kein Befund | Aufmacher 40 px über Spiegel (36 px), von 10.1 gedeckt | erfüllt |

## Paarvergleich

**gegen `klar` (gleiche Breite).**
- Handy: Bei `klar` steht das Bild 390 × 220 ohne Schrift, die Schlagzeile schwarz darunter ab rund 370 px; bei `klar2`
  ist das Bild 390 × 293 (4:3) und die Schlagzeile steht weiß im unteren Drittel des Fotos ab 323 px. Neu sind die
  Kopfzeile mit Datum und Suche (44 px) und das dunkle Band (46 px) statt einer hellen Rubrikzeile mit Linien.
- Handy: Beide zeigen zwei vollständige Schlagzeilen; bei `klar` ist die dritte (Parai) angeschnitten sichtbar, bei
  `klar2` steht an ihrer Stelle der Streifen der Rubrikkacheln (drei Kacheln, die dritte an der Kante angeschnitten).
- Desktop: `klar` zeigt das Aufmacherbild rund 400 px breit neben der Schlagzeile, links drei Nebenstücke und rechts
  sechs Meldungen, zusammen rund zehn Schlagzeilen; `klar2` zeigt ein Bild 780 × 585 mit Titel im Bild und rechts
  fünf ganze Meldungen. Die Bildfläche im ersten Schirm ist etwa fünfmal so groß, die Zahl der Geschichten sinkt von
  rund zehn auf sechs.

**gegen BBC.**
- Handy: BBC setzt den Titel (24 px Serif, 500) unter ein 16:9-Bild, `klar2` setzt 30 px Grotesk 650 in ein 4:3-Bild.
  Beide trennen nur mit Linien, beide haben ein kleines Bild links am zweiten Anreißer (BBC 132 px, `klar2` 112 px).
- Desktop: BBC stellt Aufmachertext links neben ein Doppelbild und hat Weißraum über dem Inhalt (Anzeige); `klar2`
  hat dieselbe Ordnung „großes Bild, schmale Liste daneben“, aber die Liste rechts, mit Bildern 120 px.

**gegen Spiegel.**
- Handy: Spiegel hat ein randloses Bild ähnlicher Höhe (rund 290 px) und den Titel (28 px, 800, Condensed-Slab)
  darunter; `klar2` hat dasselbe Bildmaß, aber den Titel im Bild und eine normale Breite. Der Farbanteil ist
  vergleichbar: Spiegel 6,2 % Orange im Kopf, `klar2` 6,4 % Tinte (Band).
- Desktop: Spiegel legt weiße Karten auf grauen Grund; `klar2` hat keine Karten, Bildkacheln stehen randlos auf Weiß
  bzw. Tinte.

**gegen Runde 2.**
- Runde 2: cremefarbener Grund, Rubriken als runde Pillen, Bilder mit großen Radien, Anzeigenkasten mit rundem
  Knopf, bunte Punkte vor Dachzeilen. `klar2`: kühles Weiß, Radius 0, Rubriken als Textband, Dachzeile als roter Text
  mit Trennstrich.

**gegen Runde 4.**
- Runde 4: „KANGUVA“ in rotem Condensed-Versal über die ganze Breite (98 bis 335 px), rote Rahmenlinien um jedes
  Feld, Versalien im Menü. `klar2` zeigt dasselbe Kanguva-Foto als Kachel mit 22/26 px Titel in normaler Breite,
  Rot 0,1 %, keine Versalien über 14 px, keine Rahmen.

### Die zwei Fragen aus Brief 10.4

**Wirkt `klar2` neben `klar` sichtbar bildstärker und weniger „classic“?** Ja, an diesen Unterschieden: Das
Aufmacherbild ist am Desktop rund 780 statt 400 px breit und trägt die Schlagzeile; zwischen Kopf und Inhalt liegt
ein durchgehendes dunkles Band; unter dem Aufmacher folgt eine Reihe Bildkacheln; der Bereich „Diese Woche“ ist eine
volle dunkle Fläche mit zwei großen Filmbildern; jede Meldung hat ein Bild (in `klar` reine Textliste). Der Preis ist
messbar: am Desktop sechs statt rund zehn Schlagzeilen im ersten Schirm.

**Ist etwas laut, verspielt oder Baukasten geworden?** Laut nicht: Rot 0,1 %, größte Schrift 30/40 px, keine
Versalien, keine Effekte, Bewegung 1,03 und 0,35 s. Am nächsten am Baukasten ist der Desktop zwischen 870 und 1150 px:
eine Reihe aus sieben gleichen Kacheln direkt über einer Reihe aus vier gleichen Nebenstücken (P2 Nr. 8). Die drei
gestalteten Kacheln ohne Foto lesen sich als Inhalt (Titel, Zahl der Kinos 18 px fett, Städte), nicht als leere
Kästen; der lange Termin-Streifen am Desktop (1200 × 118) wirkt eher wie ein Hinweisbalken.

## Befunde

### P0
keine (`bericht.json`: 0 Fehler, 0 Überlauf, keine Konsolenmeldungen, keine leeren Bilder, keine fehlenden Schriften).

### P1

1. **Vier Bildformate am Desktop (Kriterium 10).** Ort: 1280 px, `.woche .kachel--klein` (Rathamaarey, 1,59:1) und
   `.kueche .kachel--klein` (2,11:1), daneben 4:3 und 16:9. Ursache: `.kachel .rahmen { height: 100% }` überschreibt
   das gesetzte `aspect-ratio: 16/9`, die Höhe folgt der Rasterzeile; in der Küche ist `aspect-ratio: auto`. Bei 820 px
   entsteht dieselbe Ursache als 1,28:1. Behebung: Rahmen der kleinen Kacheln auf ein festes Format setzen (16:9 für
   Rathamaarey in allen Breiten; Küche klein entweder 16:9 oder das Raster so anlegen, dass 4:3, 16:9 und ein drittes
   Format reichen) und `height: 100%` nur dort lassen, wo das Format feststeht.

### P2

1. **Sprungziele und Fokus unter dem stehenden Band.** Ort: alle Breiten. Sprung zu `#kueche` (Rubrikband „Küche“,
   Kachel „Küche“) bei 390 px: Titel „Küche“ liegt bei −0,5 bis 36 px, das Band bis 46 px, der Titel ist ganz verdeckt.
   Sprung zu `#diese-woche`: Titel 28 bis 69 px, obere 18 px verdeckt (1280: 12 px). Mit Umschalt+Tab landen
   fokussierte Anreißer teilweise unter dem Band (390: 7, 820: 12, 1280: 4 Fälle; nie ganz verdeckt, WCAG 2.4.11 also
   knapp gehalten). Behebung: `html { scroll-padding-top: 56px }` (oder `scroll-margin-top` an den Abschnitten).
2. **Fokusrahmen der Rubrikkacheln abgeschnitten.** Ort: 390 und 820 px, `.kacheln a:focus-visible`. Der Behälter
   `.kacheln ul` hat `overflow-x: auto` ohne Innenabstand oben und unten; der Rahmen (2 px, Abstand 3 px) ist oben
   und unten weggeschnitten, sichtbar bleibt eine dunkle Senkrechte zwischen zwei Kacheln. Nach dem Fokus bleibt die
   erste Kachel links angeschnitten („achrichten“). Behebung: `padding-block: 5px` am `ul`, Rahmen nach innen
   (`outline-offset: -4px`, heller Rahmen) und `scroll-padding-inline: 16px`.
3. **Fokus des Aufmachers am Handy nicht als Ganzes erkennbar.** Ort: 390 px, `.aufmacher .anr`. Das Bild ist mit
   negativem Rand randlos; der dunkle Rahmen umschließt nur den Vorspann und verschwindet über dem dunklen Bildteil.
   Behebung: Fokus am Bildrahmen nach innen zeichnen (heller Rahmen, `outline-offset: -4px`) oder den Link ohne
   negativen Rand umfassen.
4. **Lücke neben „Termine“ bei 820 px.** Ort: 820 px, `.woche__raster` (zwei Spalten). „Termine“ steht links, rechts
   bleibt eine dunkle Leerfläche rund 378 × 215 px. Behebung: `.woche__gruppe--termine { grid-column: 1 / -1 }` ab
   600 px, wie am Desktop.
5. **Löcher in der Meldungsliste bei 820 px.** Ort: 820 px, `.meldung .anr`. Titel meist einzeilig über rund 580 px,
   das Bild 160 × 90 ganz rechts; zwischen Titelende und Bild bleiben bis zu 350 px leer, jede Zeile ist 122 px hoch.
   Behebung: zwischen 600 und 1023 px die Meldungen zweispaltig setzen oder das Bild links neben den Titel stellen.
6. **Bildausschnitt der Rathamaarey-Kachel.** Ort: 390 px, `.woche .kachel--klein`. Der Bereich mit Verlauf und Text
   reicht über rund zwei Drittel der 201 px hohen Kachel; die Dachzeile läuft über Kinn und Bart des zweiten Mannes,
   der Kopf von Rajinikanth ist oben angeschnitten, der linke Mann nur als Rand zu sehen. Bei 820 px zeigt die Kachel
   nur zwei der vier Männer, der Alt-Text nennt vier. Die eingebrannte Bildzeile ist in allen drei Breiten nicht
   sichtbar (gut). Behebung: am Handy 4:3 oder Text unter das Bild; Alt-Text an den gezeigten Ausschnitt anpassen oder
   den Ausschnitt so wählen, dass vier Personen sichtbar bleiben.
7. **Rangfolge am Desktop umgekehrt.** Ort: 1280 px. Die vier Nebenstücke (zweite Stufe, mit Vorspann) beginnen erst
   bei 1253 px unter den Rubrikkacheln; die sechs Meldungen (dritte Stufe) stehen ab 264 px neben dem Aufmacher.
   Behebung: Rubrikkacheln unter die Nebenstücke legen (Brief 10.2 erlaubt „unter dem Nachrichtenblock“), dann stehen
   die Nebenstücke direkt unter dem Aufmacher.
8. **Zwei gleichförmige Reihen übereinander.** Ort: 1280 px, 870 bis 1150 px Höhe. Sieben gleich große Kacheln
   (158 × 89) und darunter vier gleich große Nebenstücke (282 × 159), beide im gleichen Abstand: der Abschnitt liest
   sich wie ein Kachelportal. Behebung: wie Nr. 7 trennen, oder die Rubrikkacheln niedriger und mit Abstand/Linie vom
   Nachrichtenblock absetzen.
9. **Aufmachertitel bei 820 px zu klein für das Bild.** Ort: 820 px, `.aufmacher .titel`. 30 px Schrift (Handygröße)
   auf einem Bild 772 × 579; der Titel füllt zwei Zeilen im unteren Siebtel, das Foto erdrückt ihn. Behebung: ab
   600 px 34 bis 36 px, oder das Bild bis 1023 px auf 16:9 setzen.

### P3

1. Desktop-Kopf: Logozeile 80 px hoch mit leerer Fläche rechts vom Logo; zusammen mit Kopfzeile und Band 167 px. Die
   Fläche könnte die Hinweise „Diese Woche“ aufnehmen und die Kopfzeile ersetzen.
2. Desktop: Der Vorspann des Aufmachers beginnt unter dem ersten Schirm (Bild endet bei rund 776 px).
3. Datumsformen außerhalb der Dachzeilen weichen ab („Dienstag, 10. November 2026“ in der Kopfzeile, „Samstag,
   21. November 2026“ beim Termin). Beide stammen aus der Inhaltsliste und sind keine Dachzeilen; nur zur Kenntnis.
4. Handy: Nebenstück (19 px/650, Bild links) und Meldung (17 px/600, Bild rechts) unterscheiden sich vor allem durch
   die Bildseite; die Größen liegen nah beieinander. Eine Stufe mehr (20 px) würde die Ordnung klarer machen.

## Inhalte

Titel, Dachzeilen, Daten und Reihenfolge stimmen mit `inhalte-klar2.json` überein (Kopfzeile, neun Rubriken,
sieben Rubrikkacheln ohne Sport und Kontakt, Aufmacher, vier Nebenstücke, sechs Meldungen, zwei Kino-Beiträge,
zwei Filme, ein Termin, vier Küche-Beiträge). Vorspänne sind am Satzende gekürzt. Nichts erfunden, nichts weggelassen.
Gesehene Alt-Texte stimmen: p9631 (Uma Kumaran mit Rosette), p9711 (Krieger mit Fellumhang, Fackeln, Feuer), p9697
(vier Männer, Rajinikanth Zweiter von rechts; zum Ausschnitt siehe P2 Nr. 6), p9600 (Kottu Roti auf blauem Teller),
p9597/p9594/p9591 nach den Kacheln plausibel.

## Was trägt

1. Die Schrift im Bild ist überall lesbar gemessen (kleinster Wert 4,94 bei 820, sonst ≥ 5,46), ohne Platte und ohne
   Rot; Dachzeilen im Bild hell.
2. Die Ordnung aus `klar` (rote Dachzeile „Rubrik | Datum“, feine Linien, kein Kasten) bleibt im ganzen
   Nachrichtenteil erhalten; Rot 0,1 %.
3. „Diese Woche“ zeigt das Eigene von tamil.de: Zahl der Kinos und Termin-Datum sind die größten Angaben nach dem
   Titel, die drei Kacheln ohne Foto wirken als Inhalt.

## Bedienbarkeit (nur zur Information)

| Heuristik | 0–4 | Satz |
|---|---|---|
| 1 Sichtbarkeit des Zustands | 2 | Startseite ohne aktive Rubrik (vertretbar), Artikel markiert „Nachrichten“; Fokus teils abgeschnitten. |
| 2 Bezug zur echten Welt | 4 | Dachzeilen, Daten, „11 Kinos in Deutschland“ sprechen die Sprache der Leser. |
| 3 Kontrolle und Freiheit | 3 | Band steht immer bereit; Sprungziele landen teils unter dem Band. |
| 4 Einheitlichkeit | 3 | Dachzeile einheitlich; Bildformate der kleinen Kacheln uneinheitlich. |
| 5 Fehlervermeidung | 3 | Ganze Anreißer sind Tippziele, Band-Rubriken 46 px hoch. |
| 6 Erkennen statt Erinnern | 3 | Rubrikkacheln mit Bild und Namen; Streifen am Handy angeschnitten, also wischbar erkennbar. |
| 7 Flexibilität | 2 | Kopfzeilen-Hinweise führen zum Bereich, am Handy entfallen sie. |
| 8 Ästhetik und Reduktion | 3 | Ruhig, aber zwei gleichförmige Reihen am Desktop und Löcher bei 820. |
| 9 Fehler erkennen | – | nicht anwendbar (keine Formulare). |
| 10 Hilfe | – | nicht anwendbar. |

## Nicht geprüft

- Zoom auf 200 % (Erreichbarkeit aller Elemente) nicht ausgeführt.
- `artikel.html` nur gemessen (h1 28/38 px, Bild 390 × 293 randlos bzw. 1040 × 585, aktive Rubrik „Nachrichten“,
  0 Fehler), nicht im Bild angesehen.
- Alt-Texte der Nebenstücke und Meldungen nicht gegen die Originaldateien verglichen, nur gegen die Vorschaubilder.
- Kontrast der vier Rubrikkacheln, die am Handy außerhalb des Streifens liegen, bei 390 nicht gemessen (bei 820 und
  1280 alle ≥ 10,7).
- Bewegung beim Überfahren nur aus CSS und Kennzahlen, nicht im Bild beobachtet.
