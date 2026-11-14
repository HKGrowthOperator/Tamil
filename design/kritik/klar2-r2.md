# Prüfung klar2, Runde 2
Harte Kriterien: 16 von 16 erfüllt · P0: 0 · P1: 1 · P2: 6

Gemessen am 10.11.2026 mit `node design/vergleich/aufnahmen.mjs klar2` (Kennzahlen `design/vergleich/kennzahlen/klar2.json`),
`node tools/shots.mjs … --kacheln` (390/820/1280, beide Seiten) und einem eigenen Playwright-Skript (Bildformate je
Breite, Zeilenzahl, Fokus per Tab, Sprungmarken, Zoom 640 × 400 bei `deviceScaleFactor: 2`, Zeichen je Zeile im
Artikel, Abgleich mit `inhalte-klar2.json`). Werte aus dem eigenen Skript sind mit „(Hand)“ gekennzeichnet.

## Erster Eindruck

Am Handy und am Desktop liest sich die Seite als Nachrichtenseite: ein großes Foto mit weißer Schlagzeile unten, ein
dunkles Rubrikband, darunter Linien und kleine Bilder in fester Ordnung. Neu und am stärksten wirkt „Diese Woche“:
Das Kanguva-Standbild auf Tinte ist der Moment, in dem die Seite mehr als `klar` kann, ohne laut zu werden. Rot steht
nur in den 13-px-Dachzeilen und in der Linie unter der aktiven Rubrik; es gibt keine Versalien, keine Rundungen und
keine Schatten.

## Harte Kriterien (Brief 10.4)

| # | Kriterium | Handy 390 | Desktop 1280 | Ergebnis |
|---|---|---|---|---|
| 1 | Viele Geschichten (`schlagzeilen_ganz_sichtbar`) | 2 (Aufmacher + „Sri Lanka schafft Visum…“) | 6 (Aufmacher + 5 Meldungen) | erfüllt |
| 2 | Kopf (`kopfleiste_hoehe` / `erste_schlagzeile_ab`) | 147 px / 323 px | 167 px / 264 px | erfüllt |
| 3 | Drei Stufen, Faktor ≥ 1,25, ≤ 2 Familien (Hand) | 30 / 19 / 17 px, Faktor 1,58; Libre Franklin | 40 / 20 / 17 px, Faktor 2,0; Libre Franklin | erfüllt |
| 4 | Größte Schrift, zweitgrößte, Zeilen, Versalien | 30 px Aufmacher; 2. 22 px; Aufmacher 3 Zeilen, sonst ≤ 4; 0 Versalien > 14 px | 40 px; 2. 26 px (Kanguva-Kachel); 2 Zeilen, sonst ≤ 4; 0 | erfüllt |
| 5 | Rot ≤ 3 %, rote Schrift ≤ 20 px, kein 2. Buntton | 0,13 %; 13 px; bunt = rot | 0,09 %; 13 px; bunt = rot | erfüllt |
| 6 | Dunkel: genau zwei Flächen, ≤ 12 % im 1. Schirm | `nav.band` + `#diese-woche`; 6,4 % | dieselben zwei; 5,8 % | erfüllt |
| 7 | Keine Effekte, Verlauf nur unter Schrift (Hand) | Radius 0, Schatten 0, gedreht 0, Breite 0; Verläufe nur an `.imbild` (5) und `.kachel__name` (7), alle mit Text | wie Handy | erfüllt |
| 8 | Kein Baukasten | keine Pillen, Icons oder Knöpfe an Anreißern; Fläche nur an den 3 Radar-Kacheln | wie Handy | erfüllt |
| 9 | Überall ein Bild | `anreisser_ohne_bild` leer; Grafik 3 (Scene, Ramayana, Diwali) | wie Handy | erfüllt |
| 10 | Ein Format Dachzeile/Datum; ≤ 3 Bildformate je Breite (Hand) | „Rubrik │ Datum mit Jahr“ überall; 390: 4:3, 16:9, 8:3 | 820: 4:3, 16:9, 8:3 · 1280: 4:3, 16:9, 8:3 | erfüllt |
| 11 | Bildgröße | beide Listen leer | über halber Breite nur p9631 (Aufmacher) und p9600 (große Küche-Kachel); über Dateibreite leer | erfüllt |
| 12 | Helle Schrift ≥ 4,5 : 1 | 43 Stellen, min. 5,98; 820 px per Auge lesbar | 52 Stellen, min. 5,90 | erfüllt |
| 13 | Bewegung | Maßstab 1,03; 0,35 s; 0 Animationen; reduziert 0; fest nur Band 46 px | 1,03; 0,35 s; 0; 0; Band 48 px | erfüllt |
| 14 | Kein Überlauf, keine Konsolenfehler | 0 px (390 und 820), Konsole leer | 0 px, Konsole leer; Artikel ebenso | erfüllt |
| 15 | „Diese Woche“ am Handy ≤ 2532 px | Oberkante 2025 px | – | erfüllt |
| 16 | Paarvergleich (klar, BBC, Spiegel, R2, R4) | durchgeführt, kein Wert außerhalb der Grenzen | durchgeführt | erfüllt |

## Paarvergleich

**klar2 neben klar (390 / 1280).**
- Handy: Bei `klar` steht die Schlagzeile schwarz unter dem Foto (Bild ≈ 190 px hoch). Bei `klar2` liegt sie weiß unten
  im 293 px hohen, randlosen Foto, und zwischen Kopf und Bild liegt das 46 px hohe Tintenband. Der erste Schirm ist zu
  rund 40 % Foto statt zu rund 22 %.
- Desktop: Bei `klar` ist das Aufmacherbild etwa 420 px breit und steht links neben der Schlagzeile; sichtbar sind rund
  zehn Schlagzeilen. Bei `klar2` ist es 780 × 585 px mit dem Titel im Bild; sichtbar sind sechs. Die Seite gewinnt Bild
  und verliert im ersten Schirm etwa vier Geschichten. Der Vorspann fällt bei 800 px Höhe unter den Rand und ist nur
  angeschnitten zu sehen.

**klar2 neben BBC.**
- BBC setzt die Schlagzeile (24 px Serife, 500) unter das Bild und nutzt Linien zwischen Anreißern. `klar2` legt den
  Aufmacher ins Bild, behält bei allen übrigen Anreißern aber dieselbe BBC-Ordnung: Linie, kleines Bild, Titel, Dachzeile.
- BBC hat keine dunkle Fläche im Kopf. Das Band bei `klar2` (6,4 %) ist die auffälligste Abweichung, wirkt aber neutral,
  weil seine Schrift leise hell ist und nicht rot.

**klar2 neben Spiegel.**
- Der Spiegel trägt eine orange Kopfleiste (6,2 % Fläche) und Slab-Schlagzeilen in 800. `klar2` hat eine fast gleich
  große Fläche im Kopf (6,4 %), aber in unbunter Tinte, und Schlagzeilen in Libre Franklin 600–650. Das gibt dieselbe
  Kopfmasse mit weniger Lautstärke.
- Wie beim Spiegel ist das Aufmacherbild randlos und groß. Beim Spiegel steht die Schlagzeile darunter, bei `klar2` liegt
  sie im Bild.

**klar2 neben Runde 2.**
- Runde 2 hat einen Grund in Creme oder Sand, abgerundete Pillen („Nachrichten“, „Kino“) und eine runde Anzeigenkapsel.
  `klar2` hat einen kühlen Weißgrund, Radius 0 und Rubriken als Text im Band.
- Runde 2 zeigt im ersten Schirm (390) keine Schlagzeile. `klar2` zeigt zwei.

**klar2 neben Runde 4.**
- Runde 4 hat das rote Versal-Titelwort „KANGUVA“ in schmaler Schrift über die ganze Breite und Kastenlinien um jede
  Rubrik. Bei `klar2` ist dasselbe Thema ein Foto mit 26 px weißem Titel in normaler Breite, und Rot ist auf 13 px
  begrenzt.
- Runde 4 rahmt jede Rubrik im Kopf als Kästchen. `klar2` setzt die Rubriken als ungerahmten Text auf Tinte; als
  Zustandszeichen trägt nur die aktive Rubrik eine 3-px-Linie.

**Die zwei Fragen aus 10.4.**
1. *Sichtbar bildstärker und weniger „classic“ als klar?* Ja, beobachtbar. Der Fotoanteil im ersten Handy-Schirm ist
   etwa doppelt so groß. Der Titel steht im Bild, der Kopf hat eine Tintenfläche, und am Handy liegen sieben
   Bildkacheln im ersten Schirm. Weiter unten liegt ein ganzer Block auf Tinte mit großem Filmstandbild, und die Küche
   ist ein Bildmosaik aus einer großen und drei flachen Kacheln. Es fehlen keine Bilder mehr.
2. *Etwas laut, verspielt oder Baukasten?* Nach den Messwerten nein: Rot 0,1 %, größte Schrift 30/40 px, keine
   Versalien, Radius 0, keine Schatten, Zoom 1,03. Der Grenzfall sind die sieben gleich großen Rubrikkacheln am Handy
   direkt unter dem Aufmacher: Sie wiederholen das Band darüber und sind die einzige gleichförmige Reihe im ersten
   Schirm. Der Brief verlangt sie; laut wirken sie nicht, weil die Namen klein (15 px) und auf Verlauf gesetzt sind.

## Befunde

### P0
keine (`bericht.json`: Überlauf 0, Konsole leer, keine leeren Bilder, alle Schriften geladen, keine Tippflächen < 44 px).

### P1
1. **Zeilenlänge im Artikel über 70 Zeichen** – `artikel.html`, 1280 px, `.artikel__text p`: 720 px breit bei 19 px,
   gezählt (Hand) im Mittel 73 und höchstens 81 Zeichen je Zeile. Das verletzt die Pflicht „Zeilenlänge ≤ 70 Zeichen“
   (Marke, Brief 8 über 10.3). Bei 390 px (43 Zeichen) und 820 px (62) ist es in Ordnung. *Behebung:*
   `.artikel__text { max-width: 34em }` (rund 650 px) oder die Spalte auf 640 px setzen; Kopf und Vorspann auf dieselbe
   Kante.

### P2
1. **Fokus im seitlich laufenden Streifen nicht ganz sichtbar** – 390 px, `.kacheln`: Nach Tab steht „Events“ bei x
   308–446 und „Küche“ bei 272–410, also halb über dem rechten Rand; der Fokusrahmen ist rechts abgeschnitten. Dasselbe
   gilt im Band („Community“ 312–419) und bei 820 px (Kachel „Küche“ 696–856). *Behebung:*
   `scroll-padding-inline: 16px` am Behälter und `scroll-snap-align: start` an den Kacheln. Alternativ beim Fokus
   `scrollIntoView({inline:'nearest'})` per CSS-Einrasten erzwingen, ohne JavaScript über `scroll-snap`.
2. **Stehendes Band verdeckt Fokus bei 200 %** – 640 × 400 bei DPR 2, Tab auf die große Kanguva-Kachel: Oberkante bei
   6 px unter dem 46 px hohen Band. Das ist teilweise verdeckt (WCAG 2.4.11 ist noch erfüllt, aber knapp). Die
   Sprungmarken `#diese-woche` und `#kueche` liegen dagegen frei (Titel bei 84 / 56 px unter dem Band, 46 px; bei 1280
   px 92 / 203 px unter 48 px). *Behebung:* `html { scroll-padding-top: 56px }` statt nur `scroll-margin` an den
   Bereichen.
3. **Zweite Kino-Kachel ohne Titel im Bild** – alle Breiten, `#diese-woche` Rathamaarey (p9697): Der Titel steht unter
   dem 8:3-Bild. Brief 10.2 Punkt 5 verlangt für beide Kino-Beiträge den Titel im Bild. Dazu stoßen bei 1280 px (384 ×
   144) die Köpfe fast an die Oberkante (kein Kopfraum). Die eingebrannte Bildzeile ist bei 390, 820 und 1280 nicht zu
   sehen, und der Alt-Text passt zum Ausschnitt. *Behebung:* Abweichung im Brief festhalten oder ein höheres Format
   wählen (4:3 aus den drei erlaubten), damit oben Luft bleibt und der Titel unten auf dem Verlauf unter den Gesichtern
   Platz hat.
4. **Artikelbild über der halben Dateibreite** – `artikel.html`, 1280 px: p9631 wird mit 1040 × 585 gezeigt, die Datei
   hat 1382 px. Bei doppelter Dichte ist das mehr als 691 px; Brief 10.1 nimmt nur das Aufmacherbild der Startseite
   und die großen Kacheln aus. Die Kennzahl misst nur `index.html`. *Behebung:* das Bild auf die Textspalte (≤ 720 px)
   begrenzen oder die Ausnahme ausdrücklich im Brief nennen.
5. **Loch in der Termin-Kachel** – 1280 px, `#diese-woche` „Diwali in Basel“: Die Kachel ist 1200 px breit. Titel und
   Datum stehen links (bis x ≈ 310), Ort und Text beginnen erst bei x 567; dazwischen liegen rund 250 px leere „Fläche
   auf Dunkel“. *Behebung:* die Kachel in die rechte Spalte unter „Im Kino“ setzen oder die zwei Gruppen mit 32 px
   Abstand aneinanderrücken.
6. **Weniger Geschichten im ersten Desktop-Schirm, Vorspann angeschnitten** – 1280 × 800: Sichtbar sind 6 Schlagzeilen
   (`klar` rund 10). Die Zeile „In einem Erdrutschsieg…“ ist an der Unterkante halb abgeschnitten. Bei 820 px nimmt das
   Aufmacherbild (772 × 579) etwa 70 % des Schirms ein, ebenso die Kanguva-Kachel weiter unten. *Behebung:* das
   Aufmacherbild bei 1280 auf 16:9 (780 × 439) und bei 820 auf 16:9 setzen; damit stehen der Vorspann und ein
   Nebenstück im ersten Schirm. Das ist mit den drei Formaten vereinbar.

### P3
- 200 % Zoom: Die Kopfzeile bricht „Diese Woche“ und „„Scene“ läuft in 11 Kinos“ zweizeilig um; der Kopf ist dann
  155 px hoch, das Band 12 % des Viewports. Erreichbar bleibt alles, und es gibt keinen Überlauf. *Behebung:* unter
  700 px CSS-Breite die zwei Hinweise wie am Handy ausblenden.

## Was trägt
- „Diese Woche“ auf Tinte: großes Filmstandbild mit Titel im Bild, daneben die Spielorte als ruhige Schriftkacheln.
  „11 Kinos in Deutschland“ und „Samstag, 21. November 2026“ sind wie verlangt die größten Angaben nach dem Titel.
- Disziplin der Messwerte: Rot 0,1 %, eine Familie, Radius 0, keine Schatten, Zoom 1,03 bei 0,35 s, mit „Bewegung
  reduzieren“ keine Übergänge; Fokusrahmen in Bildkacheln nach innen gezeichnet (dunkel + hell) und auf jedem Grund
  sichtbar.
- Inhalte vollständig: alle 20 Titel, Dachzeilen und Daten in der Reihenfolge von `inhalte-klar2.json`, Kopfzeile mit
  Datum und beiden Hinweisen, sieben Rubrikkacheln (ohne Sport und Kontakt) ohne `h2`/`h3`, nichts erfunden.
  Artikel: 18 px am Handy, 43 Zeichen je Zeile, Bild randlos (4:3), Titel 28/38 px.

## Bedienbarkeit (nur zur Information)

| Heuristik | Punkte | Satz |
|---|---|---|
| 1 Status sichtbar | 3 | Aktive Rubrik mit Linie und 600; Datum oben |
| 2 Bezug zur Welt | 4 | Deutsche Rubriken, Daten mit Jahr, Kinos mit Städten |
| 3 Kontrolle | 3 | Band bleibt stehen; Suche in der Probe nur ein Link |
| 4 Konsistenz | 4 | Ein Dachzeilenformat, drei Bildformate, gleiche Linienordnung |
| 5 Fehler vermeiden | 3 | Tippflächen ≥ 44 px, keine Fallen |
| 6 Erkennen statt erinnern | 3 | Rubriken doppelt (Band und Kacheln): hilfreich, aber redundant |
| 7 Flexibilität | 3 | Sprungmarken aus der Kopfzeile in „Diese Woche“ |
| 8 Ästhetik, Minimalismus | 3 | Ruhig; Termin-Kachel mit Loch, Desktop-Aufmacher sehr groß |
| 9 Fehler erkennen | – | nicht anwendbar |
| 10 Hilfe | – | nicht anwendbar |

## Nicht geprüft
- Kontrast der hellen Schrift bei 820 px nur per Auge (die Kennzahl misst nur 390 und 1280).
- Tastatur und Zoom auf `artikel.html` nur auf Überlauf geprüft (0 px), nicht per Tab.
- Hover-Zoom im Bild nicht aufgenommen, nur über die Kennzahlen (Maßstab, Dauer).
- Alt-Texte nur für Aufmacher, p9697, Kanguva und die Küche gegen den Ausschnitt geprüft, nicht für die
  Rubrikkacheln und die Meldungsbilder.
