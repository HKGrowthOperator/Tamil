# Eichlauf des Prüfbogens an drei Bildpaaren

Grundlage ist `design/brief.md` (Arbeitsfassung 2), Abschnitt 3 und 7. Geprüft wurden fertige Bildschirmfotos, nicht die Seiten selbst.
Alle Werte sind **aus dem Bild geschätzt** (Pixel des Fotos auf CSS-Pixel umgerechnet: X-Handy, X-Desktop und Y-Handy liegen in doppelter Dichte vor, der Rest in einfacher).
Ausnahmen sind ausdrücklich gekennzeichnet: **K** = Kennzahl aus `design/vergleich/kennzahlen/raster.json`, **R** = Messwert aus `design/referenzen/news-marken.md`.
Die Farbanteile sind am Foto außerhalb der Bildflächen geschätzt (HSV: Sättigung > 0,35, Hellwert > 0,2).
Was am Bild nicht prüfbar ist, steht als „nicht ablesbar“ in der Tabelle und wird nicht gewertet.

Die Reihenfolge der Kandidaten ist zufällig. Es gibt kein Gesamturteil und keine Rangfolge.

---

## Kandidat X (`r4-raster-390.jpg`, `r4-raster-1280.jpg`)

### A. Harte Kriterien

| # | Kriterium | Handy 390 | Desktop 1280 | Ergebnis |
|---|---|---|---|---|
| 1 | Viele Geschichten | **K** 1 ganz sichtbar („KANGUVA“ mit Unterzeile; „In deutschen Kinos“ ist keine Schlagzeile mit eigenem Beitrag) | **K** 1 (nötig sind 4) | verletzt |
| 2 | Kopf ≤ 120 px, Aufmacher ab ≤ 480 px | **K** 275 px bis zur Schlagzeile. Von Hand: Logo 0–72 px, aber **keine Rubrikzeile im Kopf**; die Rubriken stehen in einer festen Leiste am unteren Rand (ab 787 px). Der Titel beginnt bei etwa 190 px. | Rubriken im Kopf, 69 px hoch | verletzt (keine Rubrikzeile im Kopf) |
| 3 | Drei Stufen, Aufmacher ≥ 1,25 × Nebenstück, ≤ 2 Familien | nur eine Geschichte, also keine Stufen. **K** 2 Familien (Archivo, Atkinson Hyperlegible Next) | ebenso | verletzt |
| 4 | Größte Schrift ≤ 32/38 px, ≤ 3 Zeilen, keine Versalien > 14 px | **K** 98 px, **K** 4 Versalienstellen > 14 px (KANGUVA, Fußleiste) | **K** 335 px, **K** 15 Versalienstellen | verletzt |
| 5 | Rot ≤ 3 %, keine rote Schrift > 20 px, kein zweiter Buntton | **K** Rot 6 %, rote Schrift 98 px | **K** Rot 18 %, rote Schrift 335 px | verletzt |
| 6 | Radius ≤ 2 px, kein Schatten, nichts gedreht, normale Breite | **K** Radius 0, Schatten 0, gedreht 0, **verstellte Schriftbreite an 51 Stellen** | **K** 0 / 0 / 0, **47 Stellen** | verletzt (Schriftbreite) |
| 7 | Anreißer ohne Kasten, Icon oder Knopf | Anreißer ohne Knopf und Icon. Die rot gerahmten Zellen (Datum oder Dachzeile) sind Linien, kein gefüllter Kasten. | ebenso | erfüllt (Grenzfall, siehe Bogenhinweise) |
| 8 | Ein Format für Dachzeile und Datum, ≤ 2 Bildformate | Datum steht dreimal, jedes Mal anders: „14.11.“ (rot, groß), „AB DO, 14. NOV. 2024“ und am Desktop unten „9. NOVEMBER 2024 · 3 MIN. LESEZEIT“. 1 Bildformat. | ebenso | verletzt (Datum) |
| 9 | Kein Bild über natürlicher Breite (2×) | **K** keins | **K** p9711.jpg 533 px gezeigt bei 1024 px Datei (Grenze 512) | verletzt |
| 10 | Kein Überlauf, keine Konsolenfehler | **K** Überlauf 0, Seitenfehler leer | **K** 0, leer | erfüllt (820 px nicht gemessen) |
| 11 | Dienstblock spätestens im 3. Handy-Bildschirm | nicht ablesbar | – | nicht ablesbar |
| 12 | Messwerte innerhalb der Spanne der Marken | größte Schrift 98 statt 18–32 px, Rot 6 % bei Marken 0–7,5 % | größte Schrift 335 statt 18–36 px, Farbanteil 18 % (über allen Marken außer Guardian), Schlagzeilen 1 | verletzt |

**Verletzt: 9 von 11 ablesbaren Kriterien** (K1–K6, K8, K9, K12). Erfüllt sind K7 und K10. K11 ist nicht ablesbar.

### B. Wertigkeit

| Punkt | Beobachtung (Ort) | Stufe |
|---|---|---|
| zu viel Rot, zu laut | Desktop: rotes „KANGUVA“ über die volle Breite, etwa 140–725 px hoch und damit 46 % der Bildschirmhöhe. Handy: dasselbe Wort bei 190–260 px, dazu rote Haarlinien um jede Zelle und ein rotes „14.11.“ in etwa 30 px. **K** Rot 6 % (Handy) und 18 % (Desktop). | P1 |
| Baukasten | Das Gerüst ist ein Zellraster aus roten Rahmen (Datum, Dachzeile, Unterzeile in je eigener Zelle). Am Handy steht unten eine feste Knopfreihe aus vier gerahmten Feldern (NACHRICHTEN, KINO, EVENTS, RUBRIKEN). Am Desktop sind die Rubriken einzeln gerahmt. Alles wirkt wie Fahrplan oder Formular, nicht wie Nachrichtenseite. | P1 |
| Schrift | Extraschmale Auszeichnungsschrift für Titel und Unterzeile; **K** verstellte Breite an 51/47 Stellen. Die Unterzeile „Ein tamilisches Kino-Highlight ab 14. November in Deutschland“ ist sehr eng gesetzt, mit engen Wortabständen. Daneben eine zweite, breite Grotesk („auch in 3D“, Vorspann). Die beiden Breiten stoßen hart aneinander. | P1 |
| nicht hochwertig | Erster Bildschirm: drei Datumsformen (siehe K8). Das Desktop-Bild ist rechts angeschnitten (ab 1168/2000 bis zum Rand, ohne Weißraum zur Kante) und hochskaliert (K9). Am Handy schneidet die feste Leiste den Vorspann mitten in der Zeile ab (bei etwa 780 px, „Ab dem 14. November ist der Film“). | P1 |
| alt oder langweilig | Kein Creme, keine Serife, keine braune Tinte, keine runden Bilder. Der Grund ist leicht warm gerötet (etwa rgb 253/249/248), nicht das kühle Weiß des Briefs; das allein ist kein Runde-2-Merkmal. | kein P1 (Grund: P2) |

### C. Verbotsliste (`tamil-marke`)

| Treffer | Ort | Stufe |
|---|---|---|
| Riesiges rotes Titelwort | „KANGUVA“, Handy und Desktop | P1 |
| Schlagzeile in Versalien | ebenda | P1 |
| Extraschmale bzw. verzerrte Schrift | Titel und Unterzeile (**K** verstellte Breite) | P1 |
| Verbrannte Schriften: Archivo, Atkinson Hyperlegible Next (Runde 4) | **K** Schriftfamilien | P1 |
| Cover mit nur einer Geschichte | erster Bildschirm Handy und Desktop | P1 |
| „Signatur-Element“ als Effekt: rotes Linienraster mit Fahrplanzeile | Kopf und Datumsband | P1 |
| Feste Leiste am unteren Rand (Brief 3, „Keine Effekte“; Runde 4 „Daumenleiste“) | Handy ab 787 px | P1 |

**Kandidat X: 20 P1-Befunde** (A: 9, B: 4, C: 7). Viele davon haben dieselbe Ursache (ein rotes Riesenwort in Schmalschrift).

---

## Kandidat Y (`news-bbc-handy-1.jpg`, `news-bbc-desktop-1.jpg`)

Wie vorgegeben zählen fremdes Logo, Sprache und Werbung nicht. Als „Störer“ gelten hier und im Folgenden: der Anzeigenkasten oben am Desktop, die Abo-Leiste unten und die blauen Abo-Knöpfe.

### A. Harte Kriterien

| # | Kriterium | Handy 390 | Desktop 1280 | Ergebnis |
|---|---|---|---|---|
| 1 | Viele Geschichten | 3 ganz sichtbar (Aufmacher, „Russell Brand sentenced …“, „Watch: Moment judge …“ endet bei etwa 830 px); **R** 2 | **1** ganz sichtbar (Aufmacher). Der rechte Anreißer wird von der Abo-Leiste verdeckt, die Mitte ist Bild. **R** 2 | verletzt am Desktop (Ursache: Anzeige und Abo-Leiste; ohne sie etwa 2) |
| 2 | Kopf ≤ 120 px, Aufmacher ab ≤ 480 px | Logo-Leiste 0–48 px, „NEWS“ bis etwa 115 px, also ≈ 115 px. Die **Rubrikzeile fehlt** (versteckt im Menü). Schlagzeile ab etwa 360 px (**R** 424) | – | erfüllt bei der Höhe; Rubrikzeile fehlt (Brief 3, kein hartes Kriterium) |
| 3 | Drei Stufen, Faktor 1,25, ≤ 2 Familien | Aufmacher etwa 24 px (**R**), Nebenstück etwa 18 px, Faktor 1,33. Eine Meldungsstufe ohne Bild ist im ersten Bildschirm nicht sichtbar. Familien: Serife (Titel, Vorspann) und Grotesk (Zeit, Rubrik) = 2 | Aufmacher etwa 28 px (**R**) | erfüllt, soweit ablesbar (dritte Stufe nicht ablesbar) |
| 4 | Größte Schrift ≤ 32/38 px, ≤ 3 Zeilen, keine Versalien > 14 px | größte Titelschrift etwa 24 px, aber **„Russell Brand sentenced …“ hat 4 Zeilen**. Versalien: nur „NEWS“ (Wortmarke, laut **R** Vektorgrafik) | etwa 28 px, aber der **Aufmacher hat 5 Zeilen** in einer etwa 290 px breiten Spalte | verletzt (Zeilenzahl) |
| 5 | Rot ≤ 3 %, keine rote Schrift > 20 px, kein zweiter Buntton | Rot außerhalb der Bilder etwa 0,3 % (nur „NEWS“); **R** 0,0 % | Rot etwa 0,2 %; **R** 1,2 % (mit Anzeige). Der blaue Abo-Knopf ist ein zweiter Buntton, gehört aber zu den Störern. | erfüllt (Störer ausgenommen) |
| 6 | Radius ≤ 2 px, kein Schatten, nichts gedreht, normale Breite | Bilder eckig, keine Schatten, normale Breite | redaktionell ebenso. Gerundet und mit Schatten sind nur der Anzeigenkasten, die Knöpfe und die Abo-Leiste (Störer). | erfüllt (Störer ausgenommen) |
| 7 | Anreißer ohne Kasten, Icon oder Knopf | Kein Kasten, kein Knopf. Am Videobild steht ein Abspieldreieck in einem weißen Feld unten links (bei etwa 1640/2 px). | kein Kasten | erfüllt (Abspielzeichen als Funktionsmarke gewertet, siehe Bogenhinweise) |
| 8 | Ein Format für Dachzeile und Datum, ≤ 2 Bildformate | Überall „Zeit │ Rubrik“ in derselben Form. Bilder alle etwa 1,78 (**R** 1,78) | ebenso | erfüllt |
| 9 | Bild nicht über natürlicher Breite | nicht ablesbar | nicht ablesbar | nicht ablesbar |
| 10 | Kein Überlauf, keine Konsolenfehler | nicht ablesbar | nicht ablesbar | nicht ablesbar |
| 11 | Dienstblock | entfällt (fremde Seite) | – | nicht ablesbar |
| 12 | Messwerte innerhalb der Spanne der Marken | BBC ist selbst Teil der Eichung, liegt also per Definition in der Spanne | ebenso | erfüllt |

**Verletzt: 2 von 9 ablesbaren Kriterien** (K1 nur am Desktop wegen der Störer; K4 wegen der Zeilenzahl).

### B. Wertigkeit

| Punkt | Beobachtung (Ort) | Stufe |
|---|---|---|
| zu viel Rot, zu laut | Rot nur in der Wortmarke „NEWS“. Titel 24–28 px in normalem Gewicht, keine Versalien, keine Effekte. | kein Befund |
| Baukasten | Anreißer nur durch eine 1-px-Linie getrennt (Handy bei etwa 586 und 743 px). Kein Kasten, keine Pille, kein Knopf im redaktionellen Teil. Feste Ordnung: Bild links, Titel rechts, darunter Zeit │ Rubrik. Gerundete Kästen gibt es nur in den Störern. | kein Befund |
| Schrift | Zwei Familien in normaler Breite, ruhiger Zeilenabstand (Aufmacher etwa 1,15). In den schmalen Spalten fallen die Zeilen lang und kurz durcheinander: Desktop-Aufmacher in 5 Zeilen („Republican / congressman to force / … / Hegseth“), Handy-Nebenstück in 4 Zeilen. | P2 (Zeilenfall, schon unter K4 gezählt) |
| nicht hochwertig | Einheitliches Bildformat, gleiche Abstände, gleiche Metazeile an jedem Anreißer. Am Desktop steht der Aufmacher-Titel in einer schmalen Randspalte links neben einem Bild, das doppelt so breit ist; die Hierarchie kippt zum Bild. Am Handy ist das Doppelporträt als Aufmacherbild sauber beschnitten. | kein P1 (Desktop-Hierarchie: P2) |
| alt oder langweilig | Kühles Weiß (Handy #fff), dunkelgraue Tinte, eckige Bilder, keine bunten Punkte, kein Mosaik. **Aber: Serife im Vorspann bzw. Anreißertext** („The effort will likely fail …“). | **P1 nach dem Wortlaut der Zeile** („Serife im Fließtext“); nach der Verbotsliste kein Befund, weil dort nur die Kombination mit Creme und braungrauer Tinte verboten ist |

### C. Verbotsliste

| Treffer | Ort | Stufe |
|---|---|---|
| – | Keine Übereinstimmung. Die Serife im Vorspann bildet nicht die verbotene Kombination (kühles Weiß, graue Tinte). Die feste Abo-Leiste am Desktop zählt zu den Störern. | – |

**Kandidat Y: 3 P1-Befunde nach dem Wortlaut des Bogens** (A: 2, B: 1). Ohne den Serifen-Grenzfall bleiben 2, und von diesen 2 geht K1 allein auf die Störer zurück.

---

## Kandidat Z (`r2-community-magazin-390.jpg`, `r2-community-magazin-1280.jpg`)

Das Desktop-Foto ist 1280 × 900 px groß. Gewertet sind nur die oberen 800 px.

### A. Harte Kriterien

| # | Kriterium | Handy 390 | Desktop 1280 | Ergebnis |
|---|---|---|---|---|
| 1 | Viele Geschichten | **0**: Die Aufmacher-Schlagzeile steht unter dem Bildschirm, das Bild beginnt erst bei 483 px. | 4 ganz sichtbar (rechte Liste: Porattam, Kunstprüfung, Jailer 2, Komponist Deva). Der Aufmacher reicht bis etwa 900 px, ist also bei 800 px abgeschnitten. | verletzt (Handy) |
| 2 | Kopf ≤ 120 px, Aufmacher ab ≤ 480 px | Logo und Rubrikzeile reichen bis etwa 246 px. Die Aufmacher-Schlagzeile beginnt nach 844 px. | Kopf 76 px | verletzt |
| 3 | Drei Stufen, Faktor 1,25, ≤ 2 Familien | nicht ablesbar | Aufmacher etwa 50 px, Nebenstück etwa 19 px. Eine Meldungsstufe ohne Bild ist nicht sichtbar. Familien: Grotesk (Catamaran) und Serife (Literata, in der Anzeige) = 2 | nicht ablesbar (dritte Stufe fehlt im Bild) |
| 4 | Größte Schrift ≤ 32/38 px, ≤ 3 Zeilen, keine Versalien > 14 px | etwa 26 px („tamil.de“ in der Anzeige); Rubrikpillen etwa 22 px | **Aufmacher etwa 50 px** in 3 Zeilen; keine Versalien | verletzt (Desktop) |
| 5 | Rot ≤ 3 %, keine rote Schrift > 20 px, kein zweiter Buntton | Rot außerhalb der Bilder etwa 1,8 % | etwa 0,7 %. **Zweite Bunttöne:** violette, grüne und rosa Rubrikpunkte. Roter, gefüllter Knopf „Tickets“. | verletzt (zweiter Buntton) |
| 6 | Radius ≤ 2 px, kein Schatten, nichts gedreht, normale Breite | Aufmacherbild etwa 16 px gerundet, Rubrikpillen voll gerundet, Anzeigenkasten etwa 30 px | Aufmacherbild etwa 12 px, Kleinbilder etwa 6 px, Anzeigenkasten etwa 12 px, Suchknopf rund | verletzt (Radius) |
| 7 | Anreißer ohne Kasten, Icon oder Knopf | Rubriken als gefüllte Pillen-Knöpfe. Der Anzeigenkasten (Sand) steht vor dem Aufmacher. | farbiger Punkt vor jeder Dachzeile; Anzeigenkasten mit Pillenknopf „Tickets“ und Icon | verletzt (Grenzfall, siehe Bogenhinweise) |
| 8 | Ein Format für Dachzeile und Datum, ≤ 2 Bildformate | nicht ablesbar | Datum überall „18. Oktober 2026“. Ort und Lesezeit fehlen teils, die Form bleibt gleich. Bilder etwa 1,6 und 1:1 = 2 | erfüllt |
| 9 | Bild nicht über natürlicher Breite | nicht ablesbar | nicht ablesbar | nicht ablesbar |
| 10 | Kein Überlauf | nicht ablesbar. Am Handy enden Pillenreihe und Anzeigenkasten hart am rechten Rand; ob das ein eigener Laufbehälter ist, lässt sich nicht erkennen. | nicht ablesbar | nicht ablesbar |
| 11 | Dienstblock | nicht ablesbar | – | nicht ablesbar |
| 12 | Messwerte innerhalb der Spanne der Marken | 0 Schlagzeilen (Marken 1–3); Radius 16 px (Marken 0–1,5) | größte Schrift 50 px (Marken bis 36) | verletzt |

**Verletzt: 7 von 8 ablesbaren Kriterien** (K1, K2, K4, K5, K6, K7, K12). Erfüllt ist K8. Nicht ablesbar sind K3, K9, K10 und K11.

### B. Wertigkeit

| Punkt | Beobachtung (Ort) | Stufe |
|---|---|---|
| zu viel Rot, zu laut | Wenig Rot (Logo, Punkte, Knopf „Tickets“). Laut ist nur die 50-px-Schlagzeile am Desktop (schon unter K4 gezählt). | kein P1 |
| Baukasten | Rubriken als sandfarbene Pillen (Handy 150–225 px). Ein gerundeter Anzeigenkasten mit Pillenknopf und Ticket-Icon (Desktop 276–1004 × 124–214). Abgerundete Bilder. Ein Kreis-Knopf für die Suche. Die Probe ist Runde 2 selbst, steht also im Paarvergleich zwangsläufig bei Runde 2. | P1 |
| Schrift | Grotesk in normaler Breite, ruhig gesetzt. Die Serife steht nur in der Anzeigenzeile. Die Aufmacher-Schlagzeile ist bei 50 px mit engem Zeilenabstand (etwa 1,1) gesetzt und trennt „Thileepan-“ am Zeilenende (Bindestrich im Namen, keine Silbentrennung). | kein P1 (Schriften selbst siehe C) |
| nicht hochwertig | Handy, erster Bildschirm: Erst kommen eine Anzeige, dann ein Bild, dann kein Titel. Pillenreihe und Anzeigenkasten sind am rechten Rand ohne Abschluss abgeschnitten (verrutschte Kante). Desktop: Zwei Kleinbilder („Jailer 2“, „Komponist Deva“) sind Textgrafiken auf Dunkelblau, angeschnitten mitten im Wort, also schlecht gewählte Ausschnitte. Die Rubrikpunkte wechseln die Farbe. | P1 |
| alt oder langweilig | Warmer Grund (etwa rgb 254/249/246), Anzeigenkasten in Sand (248/240/229). Braunschwarze Tinte (dunkelste Kerne etwa rgb 16/9/3). Bunte Rubrikpunkte, abgerundete Bilder, Serife (Literata) in der Anzeigenzeile. | P1 |

### C. Verbotsliste

| Treffer | Ort | Stufe |
|---|---|---|
| Creme/Sand mit braungrauer Tinte (Serifen-Fließtext nur in der Anzeigenzeile sichtbar) | Grund, Anzeigenkasten, Text | P1 |
| Pillen-Labels / abgerundete Knopfreihe | Rubriken am Handy, „Tickets“ | P1 |
| Abgerundete Bilder (Runde 2: „große abgerundete Bilder“) | Aufmacher, Kleinbilder | P1 |
| Bunte Rubrikpunkte (`abgelehnt.md`, Folge 4) | jede Dachzeile am Desktop | P1 |
| Werbung über dem Aufmacher (`abgelehnt.md`, Folge 4) | Handy und Desktop | P1 |
| Verbrannte Schriften Catamaran und Literata (Runde 2) | gesamte Seite | P1 |

**Kandidat Z: 16 P1-Befunde** (A: 7, B: 3, C: 6), mit Doppelungen zwischen A und C (Radius, Pillen).

---

## Zahl der P1 je Kandidat

- Kandidat X: 20 P1 (9 harte Kriterien verletzt)
- Kandidat Y: 3 P1 nach dem Wortlaut, davon 1 Grenzfall (2 harte Kriterien verletzt, eines davon nur durch die Störer)
- Kandidat Z: 16 P1 (7 harte Kriterien verletzt)

## Hinweise zum Bogen (beim Anwenden aufgefallen)

1. **K4 „höchstens drei Zeilen“ trifft das Vorbild.** BBC hat 4 Zeilen (Handy, Nebenstück) und 5 Zeilen (Desktop, Aufmacher in einer schmalen Spalte). Entweder gilt die Grenze nur für den Aufmacher oder für eine Mindest-Spaltenbreite, oder sie wird als P2 gewertet.
2. **K1 „am Desktop mindestens vier“** liegt über der eigenen Eichung: Laut `news-marken.md` haben die Marken am Desktop 0 bis 4 Schlagzeilen, BBC 2. Das Vorbild fällt deshalb schon ohne die Störer durch.
3. **Zeile B „alt oder langweilig“ zählt „Serife im Fließtext“ als einzelnes Merkmal**, die Verbotsliste und der Brief verbieten nur die Kombination mit Creme und braungrauer Tinte. Nach dem Wortlaut wäre BBC hier P1. Die Zeile braucht den Zusatz „in Kombination“ oder eine Mindestzahl von Merkmalen.
4. **K2 und die Kennzahl `kopf_hoehe` messen Verschiedenes.** Das Kriterium meint den Kopf (≤ 120 px), die Kennzahl misst den Abstand bis zur Aufmacher-Schlagzeile (bei X 275 px, obwohl das Logo nur 72 px hoch ist). Außerdem prüft K2 nur die Höhe, nicht ob die Rubrikzeile überhaupt im Kopf steht: X (Rubriken in fester Fußleiste) und BBC (Rubriken im Menü) bestehen die Höhe trotzdem.
5. **K7 „ohne Icon, ohne Kasten“** ist bei Grenzfällen offen: Gilt ein Abspielzeichen am Videobild als Icon? Ist ein Zellraster aus Linien ein Kasten (X)? Sind farbige Punkte vor der Dachzeile Icons (Z)? Zudem fragt K7 nur nach Anreißern; Pillen-Rubriken und Anzeigenkästen fallen durch dieses Raster und werden erst in B und C erfasst.
6. **K5 „kein zweiter Buntton“** sagt nicht, ob Abo- und Anzeigenknöpfe mitzählen. Bei BBC (blau) entscheidet allein diese Auslegung.
7. **K3 ist im ersten Bildschirm oft nicht prüfbar**, weil die dritte Stufe (Meldung ohne Bild) erst weiter unten steht. Das Kriterium sollte sagen, ob es für die ganze Seite oder den ersten Bildschirm gilt.
8. **Doppelzählung:** Dieselbe Ursache erscheint in A, B und C (etwa rotes Riesenwort, Pillen, Radius). Die Zahl der P1 sagt deshalb wenig über die Zahl der unabhängigen Mängel; eine Zählung nach Ursachen würde besser vergleichen.
9. **Zeile B „Baukasten“, Teil „steht näher an Runde 2“,** ist bei Runde 2 selbst zirkulär. Bei X (Plakat statt Portal) greift dieser Teil nicht, obwohl die Rahmenzellen und die Knopfreihe deutlich Baukasten sind.
