# Kritik raster, Runde 1
Punkte: 27/40 · Slop-Test: bestanden (knapp) · Template-Geruch: 2/4 · **Urteil: überarbeiten**

Grundlage: eigene Aufnahmen bei 390/820/1280 (`tools/shots.mjs --kacheln`, 6 Aufnahmen, 0 Fehler, kein Überlauf,
keine Konsolenfehler, keine Tippflächen-Hinweise, kein Tamil ohne `lang`), Quelltext von `index.html`, `artikel.html`,
`raster.css`, Detektor `impeccable detect` (18 Treffer, alle „quality“, keine „slop“), Brief `design/brief.md`.
`begruendung.md` erst nach der Bewertung gelesen.

## Erster Eindruck (3 Sätze)
Am Handy knallt „KANGUVA“ in roten Steckbuchstaben über die volle Breite, darunter Satz, Bild und Vorspann als eine
tippbare Einheit: die eine Geschichte steht vollständig im ersten Bildschirm, laut und klar. Danach wird es kühl: jedes
Datum, jede Rubrik, jede Stadt sitzt in einem eigenen Haarlinienkasten, und „Diese Woche“ liest sich eher wie eine
Tabelle als wie ein Aushang, den man weiterleiten will. Der Artikel ist vorbildlich ruhig und gut lesbar, aber nichts
im ersten Bildschirm sagt „das ist tamil.de“ und nicht irgendein rotes Swiss-Grid-Magazin.

## Heuristiken
| # | Heuristik | Punkte | Begründung |
|---|---|---|---|
| 1 | Systemstatus | 2 | Rubrik, Datum, Lesezeit sichtbar; die aktuelle Rubrik (`aria-current` in Kopf und Daumenleiste des Artikels) ist optisch nicht markiert. |
| 2 | Sprache der Nutzer | 3 | Klares Deutsch („Diese Woche“, „Spielorte“, „Artikel lesen“); „Samstag, 2026“ ist eine schiefe Zeitangabe. |
| 3 | Kontrolle und Freiheit | 3 | Logo zur Startseite, Sprunglink, Daumenleiste, Rubrikenraster ohne JavaScript erreichbar. |
| 4 | Konsistenz | 4 | Eine Linienstärke, eine Farbe, eine Display-Familie mit klaren Breitenstufen: das System hält auf beiden Seiten und allen Breiten. |
| 5 | Fehlervermeidung | 3 | Ganze Cover-Fläche als Ziel, Tippflächen 56 px in der Leiste, 44 px im Kopf. |
| 6 | Wiedererkennen statt Erinnern | 3 | Navigation immer sichtbar (Kopf ab 900 px, darunter Daumenleiste); Etiketten an allen Einträgen. |
| 7 | Flexibilität | 2 | Drei Navigationswege, aber keine Abkürzung für Wiederkehrer (Suche, „mein Ort“), für eine Skizze erwartbar. |
| 8 | Ästhetik und Minimalismus | 3 | Starke Hierarchie im Cover; dagegen Kästen um jedes Metadatum und doppelte Rubriken-Navigation am Desktop. |
| 9 | Fehlerhilfe | 2 | Kein Fall gezeigt; neutral bewertet. |
| 10 | Hilfe und Orientierung | 2 | Lesezeit und Zahl der Spielorte helfen; sonst nichts. |
| | **Summe** | **27/40** | knapp unter der Schwelle 28 |

## Slop-Test, Template-Geruch, Verbotsliste
- **Bans aus impeccable:** keine Seitenstreifen, kein Verlaufstext, kein Glas, keine Hero-Metrik, keine identischen
  Kartenraster, kein Modal. Detektor: 0 Slop-Treffer.
- **Kategorie-Reflex 1. Ordnung** (Diaspora-Magazin → Ornament, Gold, Bollywood-Glitzer): vermieden.
- **Kategorie-Reflex 2. Ordnung** (Magazin, das nicht altbacken sein soll → rotes Swiss-/Brutalist-Raster mit
  Haarlinien, Versalien-Etiketten mit Sperrung und einem Riesenwort): **getroffen, aber vom Brief verordnet**
  („strenges Linienraster, große lateinische Typografie“). Deshalb „bestanden (knapp)“: Was die Skizze vor dem Urteil
  „KI-Vorlage“ rettet, sind das Steckbuchstaben-Wort, das exakt die Feldbreite füllt, und das Ortsraster. Was sie
  dorthin zieht, ist die Gleichbehandlung: jedes Metadatum im eigenen Haarlinienfeld (Cover-Meta, Artikel-Meta,
  Daumenleiste, Rubrikenraster). Diese Lane steht in `impeccable/reference/brand.md` als nächster Kandidat für die
  Reflex-Liste („Brutalist-utility … may join“).
- **Template-Geruch 2/4:** keine Theme-Vorlage im WordPress-Sinn, aber nah an den vielen „Swiss Grid“-Vorlagen aus
  Framer/Webflow. Unverwechselbar wird es erst im Ortsraster, und das liegt unter dem ersten Bildschirm.
- **Verbotsliste (`tamil-marke`):** keine Übereinstimmung. Keine Pillen (Etiketten sind Text in Feldern), keine
  Rundungen, keine Story-Kreise, keine rote Platte über dem Bild, kein Laufband, kein Nachtblau/Gold, kein Creme mit
  Serife, keine Tamil-Wörter, nur Deutsch. Schriften Archivo und Atkinson Hyperlegible Next: weder auf der
  impeccable-Ausschlussliste noch verbrannt; selbst gehostet mit Lizenzdateien.

## Befunde

### P0
- keine. `bericht.json`: 0 Fehler, Überlauf 0 bei allen Breiten, keine Konsolenfehler, alle Bilder und Schriften geladen.

### P1
- **P1 · Idee im ersten Bildschirm nicht als tamil.de-eigen erkennbar** (index, 390 und 1280, Cover). Behauptet ist
  der „Aushang der Diaspora“: Städte, Säle, Termine als Felder. Im ersten Bildschirm sieht man davon nur ein rotes
  Linienraster mit Riesenwort; der Cover-Metastreifen („KINO | 6. NOVEMBER 2024 | 2 MIN. LESEZEIT“) ist ein üblicher
  Datenstreifen, kein Aushang. Das Eigene (Ortsraster, Fahrplan) beginnt erst nach dem Scrollen; ohne Begründung
  liest der erste Bildschirm als beliebiges rotes Raster-Magazin. Das ist genau der Vorwurf „generisch“ aus Runde 3.
  **Behebung:** Das Cover selbst in der Sprache des Fahrplans bauen: die belegte Angabe „ab 14.11.“ als große rote
  Zeitangabe im ersten Feld (wie „21.11.“ bei Diwali), „in deutschen Kinos“ als Ortsfeld, dann Wort, Satz, Bild. Dann
  sind Cover und „Diese Woche“ ein System, und der Aushang ist im ersten Blick da. Den Metastreifen mit Lesezeit
  dafür aus dem Raster nehmen (leise Zeile unter dem Vorspann).

### P2
- **P2 · Fahrplan ohne Zeit** (index, alle Breiten, „Diese Woche“, linke Spalte). Die größte rote Fläche des Abschnitts
  ist zweimal derselbe Ersatztext „IM KINO“; der Brief verlangt Termine „nach Datum und Ort lesbar“, der Fahrplan
  behauptet „große Zeit links“. **Behebung:** Für Kino-Einträge ohne Termin die Spalte anders belegen (z. B. die Zahl
  der Spielorte „11“ / „2“ als große rote Ziffer mit „Kinos“ darunter; die Zahl ist belegt) oder die beiden Filme unter
  einem gemeinsamen Zeitfeld „Läuft jetzt“ zusammenfassen statt es zu wiederholen.
- **P2 · „11 sehen anders aus als 2“ trägt nicht** (index, 1280 und 820, Ortsraster). „Scene“ zeigt 6 Felder,
  „Ramayana“ 2 Felder, die aber durch `flex-grow` und Zeilenhöhe fast dieselbe Fläche belegen (bei 1280 je rund
  265 × 155 px statt 177 × 77 px). Die Menge ist so kaum ablesbar. **Behebung:** feste Feldbreite (kein Wachsen), den
  Rest der Zeile leer und hell lassen; „und 6 weitere“ als sechs leere Felder oder als ein Feld mit großer „+6“.
- **P2 · Kleines-Bild-Zustand widerspricht dem Code** (index, ab 1024 und darunter, `.cover__bild img`). Die
  Begründung sagt „nie hochskaliert“, aber `width: 100%` mit festem `max-width: 1024px` vergrößert ein 692-px-Bild in
  jedem breiteren Feld (bei 1280 auf etwa 747 px, bei 1000 px Breite auf 1000 px). **Behebung:** `max-width` aus der
  natürlichen Breite setzen (Attribut `width` + `max-width: min(100%, attr)` bzw. im Theme als Inline-Stil), bei
  Desktop `object-fit: cover` nur, wenn das Original größer ist als das Feld.
- **P2 · Cover-Wort ist auf „KANGUVA“ geeicht** (`raster.css`, `.cover__wort`: fester Teiler 3.5). Ein längeres Wort
  („RAMAYANA“) wird von `overflow: hidden` abgeschnitten, ein kurzes („DOSA“) füllt das Feld nicht. Die Regel in der
  Begründung ist plausibel, im Code aber nicht angelegt. **Behebung:** Größenstufen nach Zeichenzahl als Klassen
  (das Theme kennt die Länge) oder eine SVG-`textLength`-Lösung; mindestens einen zweiten Fall in der Skizze zeigen.
- **P2 · Aktuelle Rubrik nicht sichtbar** (artikel, 1280 Kopf und 390/820 Daumenleiste). `aria-current="page"` ist
  gesetzt, aber ungestaltet; rot ist in der Leiste stattdessen immer „Rubriken“. **Behebung:** `[aria-current]` rot
  plus 3 px Unterkante; „Rubriken“ in Tinte.
- **P2 · Kasten um jedes Metadatum** (index Cover-Meta, artikel Meta, alle Breiten). Das Raster verliert seine
  Aussage, wenn alles ein Feld ist; es kippt in die Swiss-Grid-Vorlage (siehe Slop-Test). **Behebung:** Felder nur
  dort, wo das Feld Information ist (Orte, Termine, Cover); Metadaten als freie Zeile.
- **P2 · Foto am Handy klein** (index, 390, Cover-Bild ca. 390 × 205 px von 844 px Höhe). Das stärkste Gen-Z-Mittel
  der Seite (Suriya, Fackeln) ist der kleinste Teil des Covers; „lebendig und stolz“ kommt nur aus der Schrift.
  **Behebung:** am Handy Ausschnitt 4:5 oder 1:1 mit `object-fit: cover` (538 px Originalhöhe reicht, kein
  Hochskalieren), Vorspann dafür kürzen oder unter den ersten Bildschirm.

### P3
- **P3 · Daumenleiste eng** (index/artikel, 390, `.daumen a`): „NACHRICHTEN“ hat 4 px Innenabstand und berührt fast
  die Linien. Kleinere Sperrung oder „News“ ist keine echte Rubrik; besser `font-stretch: 75%` für die Leiste.
- **P3 · Diwali-Datum doppelt** (index, alle Breiten): „21.11. / SAMSTAG, 2026“ und daneben „feiert am 21. November
  2026“. Text auf Verein und Anlass kürzen; „Sa 21.11.2026“ statt „Samstag, 2026“.
- **P3 · Doppelte Navigation am Desktop** (index, 1280): Rubriken im Kopf und noch einmal als Raster am Seitenende.
  Am Desktop das untere Raster weglassen oder in den Fuß verlegen.
- **P3 · Artikel-Meta am Handy drei Zeilen hoch** (artikel, 390): Rubrik, Datum, Lesezeit, Teilen belegen rund
  140 px vor der Überschrift. Rubrik und Datum in eine Zeile, Teilen unter den ersten Absatz.
- **P3 · Detektor:** 17 × „cramped-padding“ sind überwiegend Fehlalarme der Fugen-Technik (Linien aus `gap` über
  rotem Grund); 1 × „tight-leading“ (1.16) betrifft Versalien-Etiketten im Artikel, für Anzeigetext vertretbar.

## Was stark ist
- **Lesbarkeit für alle Generationen:** Atkinson Hyperlegible Next in 19–20 px, Tinte 16:1, Zweitton > 7:1,
  Daumenleiste mit 56 px, ganze Cover-Fläche als Ziel, Zeilenlänge im Artikel unter 70 Zeichen. Der Artikel ist
  wirklich ruhig.
- **Das Steckbuchstaben-Wort:** „KANGUVA“ füllt am Handy exakt die Breite, Rot als Masse ohne Platte, der Aufmacher
  steht vollständig im ersten Bildschirm. Das ist eine eigene Lösung für „laut im Kopf“.
- **Das Ortsraster als Keim einer echten Idee:** Städte als Felder zeigen die verstreute Diaspora-Geografie, und
  Einträge ohne Foto sehen nicht leer aus. Hier liegt, was nur zu tamil.de passt; es muss nach oben und lauter werden.

## Abgleich mit `begruendung.md` (nach der Bewertung gelesen)
- „Aushang der Diaspora“: im Ortsraster sichtbar, im ersten Bildschirm nicht (P1).
- „Steckbuchstabentafel“: sichtbar und gelungen. „Fahrplanaushang, große Zeit links“: nur bei einem von drei
  Einträgen (P2). „Hallenbodenlinie“: als rote Haarlinie da, als Turnhallen-/Aula-Bild nicht lesbar.
- Zustände: Ohne-Foto und viele/wenige Spielorte gezeigt; lange/kurze Überschrift nur beschrieben, Code geeicht auf
  ein Wort (P2); kleines Bild beschrieben, Code widerspricht (P2).
