# Richtung `feed`: Begründung (Skizze, Runde 1)

## 1. Vorbild

- **i-D** (https://i-d.co, `design/referenzen/img/idmag.png`). Übernommen: der Einstieg aus **zwei Hälften im
  Gegensatz** (Bild gegen Fläche, Bild gegen Schrift), das **Logo als Form**, die **Leiste unten**, die über dem
  Bild liegt und mit dem Daumen erreichbar ist. Nicht übernommen: die Vollbild-Fotografie (unsere Bilder sind
  692 bis 1024 Pixel breit), die schwebende abgerundete Leiste und die Monospace-Kleinschrift.
- **The Pudding** (https://pudding.cool, `design/referenzen/img/thepudding.png`), ergänzend. Übernommen: dass eine
  ganze Fläche in Vollfarbe steht und der Inhalt darauf ohne Rahmen auskommt; schwere, enge Überschriften. Nicht
  übernommen: Aufkleber, Stempel-Logos, umrandete Nummern-Etiketten (zu nah an Pillen).

## 2. Idee in einem Satz

Das Logo erzählt schon die Diaspora, das aufrechte rote **„tamil“** und das schief angesetzte graue **„.de“**:
Diese Richtung macht das gekippte **„.de“** zum **Länderzeichen** jeder Geschichte (.de, .at, .ch), das zeigt, wo
das, was von dort kommt, hier ankommt, und baut die Seite aus den zwei Hälften des Logos, Rot und Grau.

## 3. Drei Stimmwörter (als Gegenstände)

**Einreisestempel** (das schräg gesetzte Länderzeichen), **Kinokassen-Aushang** (riesiger Filmtitel, darunter
nüchtern Ort und Tag), **S-Bahn-Anzeige** (die graue Leiste unten, kurze Wörter, sofort lesbar).

## 4. Schrift

Reflex-Schriften, verworfen:
1. **Inter / DM Sans:** Ausschlussliste; jede App-Vorlage sieht so aus, genau das wurde in Runde 3 abgelehnt.
2. **Space Grotesk:** Ausschlussliste; „jung und digital“ als Kostüm.
3. **Bricolage Grotesque:** nicht verboten, aber der aktuelle Reflex für „Gen Z mit Charakter“; würde in jede
   zweite Skizze passen. Ebenso verworfen: Anton/Archivo Black (Plakat-Klischee) und Anek (verbrannt, Runde 3).

Gewählt, eine Familie für die Stimme und eine für das Lesen, beide selbst gehostet unter `fonts/` mit
OFL-Lizenzdatei:

- **Sofia Sans Extra Condensed** (Lettersoup, Google Fonts, OFL), variabel 1 bis 1000, für Überschriften, Titel,
  Länderzeichen und Leiste. Sehr schmal, sehr schwer, gerade Schäfte wie das „tamil“ im Logo. Die Schmalheit ist
  hier Funktion: Titel von „Dosa“ bis 78 Zeichen stehen am Handy groß, ohne zu brechen, und ein einzelnes Wort
  („Kanguva“) kann die ganze Breite füllen wie ein Kinoaushang. Das eigenwillige „g“ gibt ihr Gesicht.
- **Atkinson Hyperlegible Next** (Braille Institute, Google Fonts, OFL), für Fließtext, Vorspann, Orte und Daten.
  Gebaut für Menschen, die schlecht sehen; unterscheidbare Formen (I l 1, O 0). Das ist die Antwort auf „Eltern und
  Großeltern beim Lesen nicht verlieren“, ohne dass die Seite alt aussieht.
- **Latein:** beide Familien, Teilmenge `latin` (enthält ä ö ü ß und „ “).
- **Tamil:** Laut Brief keine Tamil-Auszeichnung. Für Tamil im Inhalt steht im Schriftstapel nach den beiden
  Familien `"Noto Sans Tamil", "Tamil Sangam MN", "Latha", "Nirmala UI"`, auszuzeichnen mit `lang="ta"`.
  In der Skizze kommt kein Tamil vor, deshalb wird keine Tamil-Datei geladen. Für das Theme: Noto Sans Tamil
  (OFL) selbst hosten, mit `unicode-range` U+0B80–0BFF, damit sie nur lädt, wenn Tamil auf der Seite steht.

## 5. Farbstrategie: Committed, aus den zwei Farben des Logos

Nur die zwei Logofarben und Papier. Das Rot trägt die Startseite als Fläche (Bildhälfte des Covers, ganzer
Abschnitt „Diese Woche“) und als Schriftmasse (Cover-Überschrift). Das Grau des Logos ist die Stimme von „.de“:
Länderzeichen, Fließtext, Leiste.

| Token | OKLCH | Rolle | Kontrast auf Papier |
|---|---|---|---|
| `--rot` | `oklch(0.508 0.177 25.6)` (= #B5282A aus dem Logo) | Fläche, Überschriften | 6,3 : 1 |
| `--rot-tief` | `oklch(0.42 0.15 25)` | gedrückt, Fokus auf Papier | 8,7 : 1 |
| `--grau` | `oklch(0.36 0.006 25)` (Logo-Grau #3C3C3C, leicht zum Rot getönt) | Länderzeichen, Text, Leiste | 10,4 : 1 |
| `--grau-hell` | `oklch(0.47 0.012 25)` | Daten, Nebenangaben | 6,6 : 1 |
| `--papier` | `oklch(0.985 0.005 25)` | Grund; Schrift auf Rot (6,3 : 1) und auf Grau (10,4 : 1) | |

Szene (Brief): S-Bahn bei Tageslicht, Handy in einer Hand, abends mit der Mutter auf demselben Gerät. Daraus folgt
heller Grund, große Schrift, Bedienung unten. Kein Dunkel, kein Gold, kein Creme.

## 6. Signatur-Element: das Länderzeichen

Das schräge graue **„.de“** aus dem Logo (Winkel wie im Logo, rund −10°), in der schweren schmalen Schrift, gefolgt
von einer aufrechten, nüchternen Zeile: **wo und wann es hier ankommt.**

- Cover: `.de` · ab 14. November im Kino
- Kino: `.de` · in 11 Kinos in Deutschland / in 2 Kinos in Deutschland
- Event: `.ch` · Basel, Schweiz · Samstag, 21. November 2026
- Artikel: `.de` · visumfrei ab 1. Oktober 2024

Es ist kein Etikett und keine Pille: kein Kasten, keine Rundung, keine Farbe außer Grau (auf Papier) oder Papier
(auf Rot). Die Länderkennung selbst ist Zeichen, nicht Information; das Land steht immer ausgeschrieben im Text
daneben, damit niemand „.ch“ deuten muss. Erklärt wird das System einmal als Legende im Kopf von „Diese Woche“
(Runde 2; vorher stand `.de .at .ch` oben neben dem Logo).

Dazu die **zwei Hälften**: am Desktop links Papier mit roter Schrift (das „tamil“), rechts Rot mit Bild (die
Fläche); die Naht bei 50 % läuft von Cover in „Diese Woche“ weiter (Titel links, Ort und Tag rechts). Am Handy
liegen die Hälften übereinander: erst Papier mit Überschrift, dann Bild und Rot, das in „Diese Woche“ weiterfließt.

## 7. Abgrenzung zu den abgelehnten Runden

1. **Gegen Runde 1 (Nachtblau):** heller Grund, nur zwei Farben aus dem Logo, kein Gold, kein Laufband, keine
   tamilischen Wörter, keine Radar-Technik auf der Leserseite.
2. **Gegen Runde 2 (Creme, Serife, altbacken):** kein Creme/Sand, keine Serife, kein Mosaik und keine
   Nachrichtenliste neben dem Aufmacher; eine einzige Geschichte füllt den ersten Bildschirm, und Schrift ist hier
   Plakat, nicht Zeitung.
3. **Gegen Runde 3 (App-Vorlage):** keine Story-Kreise, keine Pillen, keine runden Karten, keine Reels-Kacheln,
   keine 01/02/03. Keine rote Platte über dem Bild: Bild und Rot liegen **nebeneinander** als zwei Hälften, die
   Überschrift steht auf Papier. Die Leiste unten ist eine gerade, graue Schriftleiste ohne Icons und ohne
   Rundungen, eher Fahrgastanzeige als Tab-Bar. Alle Ecken sind eckig.

## 8. Zustände (Brief, Abschnitt 6)

- **Kleines Bild:** Das Bild wird nie größer als seine Pixel gezeigt (Höhe höchstens 538 px bei Kanguva, Breite
  höchstens die halbe Seite). Den Rest des ersten Bildschirms tragen Schrift und Rot: am Desktop füllt die rote
  Hälfte unter dem Bild den Vorspann, am Handy steht die Überschrift ganz ohne Bild oben. Ein 692-px-Bild würde
  denselben Platz mit mehr Rot lassen, nicht mit gestrecktem Bild.
- **Eintrag ohne Foto:** „Diese Woche“ ist ein Aushang ohne Bilder. Der Titel ist das Bild; Länderzeichen, Ort und
  Tag stehen rechts daneben. Kein Platzhalter, kein Nachweis.
- **Lange und kurze Überschrift:** Das erste Wort eines Titels (das Kopfwort, hier „Kanguva“) kann als ein einziges
  riesiges Wort stehen, der Rest folgt kleiner; der Titeltext bleibt vollständig und unverändert (der
  Gedankenstrich ist nur optisch ausgeblendet). „Dosa“ wäre nur Kopfwort. Ein Titel ohne starkes erstes Wort wird
  ganz in der zweiten Größe gesetzt; die schmale Schrift trägt 78 Zeichen am Handy in vier bis fünf Zeilen.
- **Viele und wenige Spielorte:** „Scene“ (11) und „Ramayana“ (2) stehen untereinander im selben Aufbau; die Zahl
  steht im Text, die ersten fünf Städte werden genannt, der Rest als „und 6 weitere Städte“ mit Link.
- **Fokus:** dicke Umrandung in Grau (auf Papier) oder Papier (auf Rot und Grau) auf jedem Link und Knopf.
  **Bewegung:** keine. Die einzige Veränderung (Rubrikenliste aus der Leiste) erscheint ohne Animation.

## 9. Bedienung

- Das ganze Cover ist ein Link. Die Leiste unten (Kino, Events, Community, Nachrichten, Mehr) ist fest in
  Daumenreichweite; „Mehr“ öffnet alle neun Rubriken nach oben, ohne JavaScript (`<details>`).
- Im Artikel trägt die Leiste rechts **„Teilen“** als WhatsApp-Link (`wa.me`, kein Skript); unter dem Vorspann
  steht derselbe Link noch einmal.

## Runde 2 (Überarbeitung nach `design/kritik/feed-r1.md`)

Geändert wurde nur, was die Kritik nennt; Idee, Schriften und Farben bleiben.

- **P1 Leiste am Desktop (Startseite):** Ab 900 px ist die Leiste nicht mehr fest. Sie schließt die linke Hälfte
  des ersten Bildschirms unten ab (`position: absolute` im Block `.erster`) und scrollt mit; über „Diese Woche“
  liegt nichts mehr. Am Desktop gibt es keinen Daumen, die Rubriken stehen dort, wo der erste Blick endet.
- **P1 Leiste am Desktop (Artikel):** Ab 900 px wird die Leiste zur Wortliste in der linken Meta-Spalte unter
  Rubrik und Datum (Start, Nachrichten, Mehr, Teilen), mitlaufend (`sticky`) in ihrer eigenen Spalte. Sie liegt
  weder auf dem Foto noch auf der Textspalte; „Mehr“ klappt darin nach unten auf, ohne den Text zu verschieben.
  Am Handy bleibt sie in beiden Seiten fest unten in Daumenreichweite.
- **Länderzeichen lesbar:** Das Land steht jetzt überall ausgeschrieben neben dem Zeichen (Cover: „in Deutschland
  ab 14. November“; Artikel: „Einreise aus Deutschland visumfrei ab 1. Oktober 2024“). `.de .at .ch` oben rechts
  ist entfernt (sah wie ein Umschalter aus). Erklärt wird das System dort, wo es unterscheidet: im Kopf von
  „Diese Woche“ als Legende „.de Deutschland · .at Österreich · .ch Schweiz“.
- **Ende des Covers:** Der Kopf von „Diese Woche“ steht auf Papier (rote Überschrift, graue Legende), erst die
  Termine stehen auf Rot. So endet das Cover am Handy sichtbar, und Papier/Rot wechseln sich als Gegensatz ab.
- **Tonlage Nachrichten:** Artikelüberschrift in Grau und Strichstärke 620 statt Rot 800; Rot nur noch für Rubrik
  und Länderzeichen. Die volle Lautstärke bleibt Startseite, Kino und Kultur.
- **„Mehr“:** Raster mit gleicher Zeilenhöhe statt Spalten; auf der Startseite ohne die vier Rubriken, die schon in
  der Leiste stehen.
- **Kopfwort:** Regel festgeschrieben: nur bei einem ersten Wort mit höchstens 8 Zeichen, sonst ganzer Titel in der
  zweiten Größe; als Sicherung `overflow-wrap: anywhere`.
- **Fokus auf dem Cover:** Ring je Teilfläche: Grau auf Papier, Papier mit grauer Innenkante auf Bild und Rot.
- **P3 Artikelbild:** bündig mit der Textspalte (736 px breit, kleiner als die 900 Bildpixel). **P3 Cover Desktop:**
  Textblock sitzt unten an der Leiste statt mittig.
