# Richtung „Plakatwand“: Begründung (Skizze, Runde 1)

## 1. Vorbild

- **DT Next: „Chennai's forgotten art: How flex printing erased hand-painted banners“**
  (https://www.dtnext.in/lifestyle/chennais-forgotten-art-how-flex-printing-erased-hand-painted-banners,
  `design/referenzen/img/dtnext-flex.png`). Übernommen wird nicht der Malstil, sondern die **Arbeitsweise der
  Bannermaler**: Ein Filmtitel wird nicht „gesetzt“, er wird auf die Fläche gemalt, und jede Zeile wird so breit
  gezogen, bis sie die Wand füllt. Die Zeilen bekommen dadurch verschiedene Größen; der Titel ist ein Block, kein
  Absatz. Dazu der Maßstab: Gesichter größer als der Betrachter, vom Rand der Wand angeschnitten.
- **The News Minute: „Why posters and cut-outs in Tamil cinema are much more than advertisements“**
  (https://www.thenewsminute.com/tamil-nadu/why-posters-and-cut-outs-tamil-cinema-are-much-more-advertisements-132081,
  `tnm-posters.png`). Übernommen: **„Ein Plakat verdichtet den Film zu einem einzigen Bild.“** Auf der Startseite
  steht deshalb genau eine Geschichte mit genau einem Bildausschnitt, nichts daneben. Und der Aufbau eines
  Filmplakats in zwei Stimmen: riesiger Titel, darunter die kleinere Zeile mit dem Versprechen.

Bewusst **nicht** übernommen: Pinseltextur, Leinwand, 3D-Titel, Neonfarben, Patina. Das wäre der Filter über
Fotos, vor dem die Referenzliste warnt, und es wäre Nostalgie.

## 2. Idee in einem Satz

Die Startseite plakatiert jede Woche eine Geschichte so, wie die Bannermaler in Chennai einen Film plakatiert haben
(ein Gesicht überlebensgroß und angeschnitten, der Titel Zeile für Zeile auf Wandbreite gezogen, Rot als Wand), nur
auf hellem Grund, am Handy und auf Deutsch.

## 3. Drei Stimmwörter (als Gegenstände)

**Kleisterbogen** (ein Bogen nach dem anderen an die Wand, Kante an Kante, ohne Rahmen), **Malerlineal** (jede
Zeile wird auf die volle Breite eingeteilt, nichts flattert), **Kinokasse** (wann, wo, wie viele Säle: klar, groß,
für die Mutter genauso lesbar wie für die Tochter).

## 4. Schrift

Verfahren nach impeccable `reference/brand.md`, Abschnitt Font selection.

- **Reflex für „Kinoplakat“:** Bebas Neue, Anton, Oswald. Alle drei verworfen: Sie sind die Standardantwort auf
  „Poster“ und tragen keine Handschrift, nur Enge. (Dazu verbrannt bzw. ausgeschlossen: Anek, Catamaran, Literata,
  Schibsted Grotesk, Fraunces, Space Grotesk, Inter, DM Sans.)
- Geprüft und gerendert: Big Shoulders Display (zu sehr Chicagoer Amtsschild), Sofia Sans Extra Condensed (zu
  glatt), Archivo 62 % (zu technisch), Antonio und Smooch Sans (zu dünn im Ausdruck).
- **Gewählt für Plakatzeilen: Bricolage Grotesque**, Breite 75 %, Gewicht 800, optische Größe 96 (Google Fonts,
  OFL, selbst gehostet in `schriften/`). Ihre Tintenfallen und leicht unruhigen Rundungen wirken bei Plakatgröße
  wie mit dem Pinsel gezogene Kanten, ohne Pinseleffekt. Die Breitenachse ist genau das Werkzeug des Bannermalers:
  enger ziehen, bis die Zeile passt.
- **Gewählt für Text: Atkinson Hyperlegible Next** (Google Fonts, OFL, selbst gehostet). Vom Braille Institute für
  Menschen mit eingeschränktem Sehen gebaut: unverwechselbare Formen für I, l, 1, 0, O. Das ist der Beitrag für Eltern
  und Großeltern, und die Schrift ist kein Reflex-Grotesk.
- **Tamil:** Die Auszeichnungsschrift muss Tamil laut Brief nicht abdecken. Für Tamil im Inhalt steht **Noto Sans
  Tamil** (OFL, selbst gehostet, nur Tamil-Bereich per `unicode-range`) im Textstapel und greift über `:lang(ta)`.
  Die Skizze enthält kein Tamil, weil die festen Inhalte keines haben; die Schrift lädt nur bei Bedarf.
- Lizenzen: `schriften/OFL-*.txt`.

## 5. Farbstrategie

**Committed**, Rot aus dem Logo trägt die Seite. Referenz: die rote Wand, auf die geklebt wird.

| Token | OKLCH | Rolle |
|---|---|---|
| `--rot` | `oklch(0.508 0.177 25.6)` | Logo #B5282A umgerechnet; Wand des Aufmachers, Plakatzeilen auf Papier, Fest-Bogen |
| `--rot-tief` | `oklch(0.42 0.15 25.6)` | Zustand bei Zeigen/Tippen, kleiner roter Text |
| `--papier` | `oklch(0.977 0.005 25)` | Grund; fast weiß, kaum zum Rot getönt, ausdrücklich kein Creme |
| `--tinte` | `oklch(0.21 0.022 25)` | Text; fast schwarz, kein Braungrau |
| `--grau` | `oklch(0.46 0.02 25)` | Nebenangaben |

Kontraste (gerechnet): Papier auf Rot 5,9 : 1, Rot auf Papier 5,9 : 1, Tinte auf Papier 16,6 : 1, Grau auf Papier
6,7 : 1. Tinte auf Rot (2,8 : 1) kommt nicht vor. Keine weitere Farbe: kein Gold, kein Gelb, kein Blau, kein Neon.
Am Handy ist der erste Bildschirm zu gut der Hälfte rot; der Rest der Seite ist Papier mit roter Schrift.

## 6. Signatur-Element: der Plakatsatz

Jede Plakatzeile wird **auf die volle Breite ihrer Wand gezogen**. „KANGUVA“ füllt am Handy 358 px, am Desktop
1184 px; die Zeilen darunter sind kleiner, weil sie länger sind, und füllen trotzdem die Breite. So entsteht ein
Block mit wechselnden Größen, wie ein gemalter Bannertitel, ohne Effekt und ohne Bildfilter. Das Bild darunter ist
angeschnitten (Wandkante, Bildschirmrand), nie hochskaliert.

Technik: Für jede Zeile steht ein Breitenfaktor `--r` (Zeilenbreite in em) im HTML; die Schriftgröße ist
`100cqi / --r` (Container-Einheiten). Kein JavaScript. Im Theme rechnet PHP den Faktor aus einer Breitentabelle der
Schrift (Glyphenbreiten als JSON), die Redaktion kann Umbrüche im Cockpit setzen; ohne Faktor fällt die Zeile auf
eine feste, fließende Größe zurück.

Der Plakatsatz kommt nur auf der Startseite und in den Rubrikköpfen vor. Im Artikel steht die Überschrift in
derselben Schrift, aber normal umbrochen und ruhig.

## 7. Abgrenzung zu den abgelehnten Runden

1. **Nicht Runde 1 (Nachtblau):** heller Grund, nur Rot, Tinte und Papier. Keine Tamil-Wörter, kein Laufband, keine
   Radar-Technik, keine Werbung im ersten Bildschirm.
2. **Nicht Runde 2 (Community-Magazin):** keine Serife im Text, kein Creme, kein Braungrau, kein Mosaik aus
   gleichrangigen Meldungen. Die Startseite hat eine Geschichte und eine Haltung (Plakat), keine Nachrichtenliste.
3. **Nicht Runde 3 (App-Vorlage):** keine Pillen, keine Rundungen, keine Story-Kreise, keine Knopfreihen, keine
   rosa Kästen, keine 01/02/03. Und keine „rote Platte über dem Bild“: Dort lag eine abgerundete rote Karte auf dem
   Foto. Hier ist Rot die Wand selbst, randlos über die ganze Breite; das Foto ist auf die Wand geklebt, die Schrift
   steht auf der Wand und läuft über die Bildkante, ohne Kasten.

## Zustände aus dem Brief (Abschnitt 6)

- **Aufmacher mit kleinem Bild (692 bis 900 px):** Das Bild ist ein Bogen auf der Wand, nicht die Wand. Es wird nur
  verkleinert oder angeschnitten (`object-fit: cover`, Höchstmaß = Originalgröße); die Wirkung tragen Rot und
  Plakatsatz. Am Desktop zeigt der Bildbogen höchstens 1024 × 538 px; ein 692 px breites Bild wird schmaler
  angeschnitten, die Wand bleibt gleich.
- **Eintrag ohne Foto:** Kino und Events sind **Schriftplakate**. Der Filmtitel im Plakatsatz ist das Bild; darunter
  ein Kassenblock mit Spielorten bzw. Datum, Ort und Veranstalter. Kein Platzhalterbild.
- **Lange und kurze Überschrift:** Kurz („Scene“, „Dosa“) wird eine einzige, sehr große Zeile; lang (bis 78 Zeichen)
  wird auf 4 bis 6 Zeilen verteilt. Regel: Titelwort vor Doppelpunkt oder Gedankenstrich bekommt eine eigene Zeile,
  der Rest wird in Zeilen von etwa 12 bis 18 Zeichen geteilt. Am Handy bleibt die Überschrift so im ersten Bildschirm;
  wird sie zu hoch, wird der Bildbogen niedriger, nie die Schrift kleiner als 40 px.
- **Viele und wenige Spielorte:** gezeigt mit „Scene“ (11) und „Ramayana“ (2). Der Kassenblock wächst, der
  Plakatsatz bleibt; am Desktop ist der Bogen mit vielen Orten der große.
- **Fokus und Bewegung:** Jeder Link hat einen sichtbaren Fokusrahmen (Tinte auf Papier, Papier auf Rot). Es gibt
  keine automatische Bewegung; die einzige Überblendung beim Zeigen ist unter `prefers-reduced-motion` abgeschaltet.

## Was die Skizze offen lässt

- Die Kino-Einträge haben im Radar-Entwurf kein Startdatum; die Skizze zeigt deshalb nur die Spielorte. Im Theme
  bekommt der Kassenblock eine Zeile „Wann“, sobald das Datum belegt ist.
- Von den 11 Spielorten von „Scene“ sind im Brief nur fünf genannt; die anderen sechs sind nicht erfunden, sondern
  als „und 6 weitere Städte“ stehen gelassen.
- Bildnachweise sind im Bestand nicht belegt und werden daher nicht gezeigt.
