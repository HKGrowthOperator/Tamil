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
90 % der Wand (Runde 2); die Zeilen darunter sind kleiner, weil sie länger sind, und füllen trotzdem die Breite. So entsteht ein
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

- **Aufmacher mit kleinem Bild (692 bis 900 px):** Das Bild ist ein Bogen auf der Wand, nicht die Wand. Es wird nie
  skaliert, nur in Originalgröße angeschnitten (seit Runde 2 `object-fit: none`); die Wirkung tragen Rot und
  Plakatsatz. Gezeigt in `zustaende.html` mit einem Bild von 692 × 359 px.
- **Eintrag ohne Foto:** Kino und Events sind **Schriftplakate**. Der Filmtitel im Plakatsatz ist das Bild; darunter
  ein Kassenblock mit Spielorten bzw. Datum, Ort und Veranstalter. Kein Platzhalterbild.
- **Lange und kurze Überschrift:** Kurz („Scene“, „Dosa“) wird eine einzige, sehr große Zeile; lang (bis 78 Zeichen)
  wird auf 4 bis 6 Zeilen verteilt. Regel: Titelwort vor Doppelpunkt oder Gedankenstrich bekommt eine eigene Zeile,
  der Rest wird in Zeilen von etwa 12 bis 18 Zeichen geteilt. Am Handy bleibt die Überschrift so im ersten Bildschirm;
  wird sie zu hoch, wird der Bildbogen niedriger, nie die Schrift kleiner als 40 px.
- **Viele und wenige Spielorte:** gezeigt mit „Scene“ (11) und „Ramayana“ (2). Der Kassenblock wächst, der
  Plakatsatz bleibt. Aufbau der Bögen: siehe Runde 2.
- **Fokus und Bewegung:** Jeder Link hat einen sichtbaren Fokusrahmen (Tinte auf Papier, Papier auf Rot). Es gibt
  keine automatische Bewegung; die einzige Überblendung beim Zeigen ist unter `prefers-reduced-motion` abgeschaltet.

## Was die Skizze offen lässt

- Die Kino-Einträge haben im Radar-Entwurf kein Startdatum; die Skizze zeigt deshalb nur die Spielorte. Im Theme
  bekommt der Kassenblock eine Zeile „Wann“, sobald das Datum belegt ist.
- Von den 11 Spielorten von „Scene“ sind im Brief nur fünf genannt; die anderen sechs sind nicht erfunden, sondern
  als „und 6 weitere Städte“ stehen gelassen.
- Bildnachweise sind im Bestand nicht belegt und werden daher nicht gezeigt.

## Runde 2 (Überarbeitung nach `design/kritik/plakatwand-r1.md`)

Die Abschnitte oben gelten weiter. Wo sie dem Folgenden widersprechen, gilt das Folgende.

- **P1, Aufmacher (Abstand zu Runde 3, Gesicht angeschnitten):** Der Bildbogen steht jetzt immer in
  **Originalgröße** (`object-fit: none`) und wird über einen Fokuspunkt je Bild (`--fokus`) eng auf das Gesicht
  beschnitten, statt das ganze Querformat einzupassen. Am Handy läuft er randlos über beide Bildschirmkanten,
  „KANGUVA“ liegt mit der unteren Hälfte auf dem Bild (Brust, Kette), das Gesicht steht darüber. Ab 760 px steht der
  Bogen **hochkant in der rechten unteren Ecke** (448 × 538 px bei 1280) und wird von der rechten und der unteren
  Wandkante angeschnitten. „KANGUVA“ läuft unten quer über 90 % der Wand und über den Körper im Bild. Oben links stehen
  Rubrik, Datum und Zusatzzeilen. Es gibt keine Spalte „Text links, Foto rechts“ mehr, sondern eine Form aus Wand,
  angeschnittenem Bogen und Titelzeile.
- **Grenze des Bildes, ehrlich:** Mit `p9711.jpg` (1024 × 538) ist das Gesicht in Originalgröße etwa 190 px hoch. Am
  Handy (390 px) ist das groß, am Desktop nicht überlebensgroß, sondern nur eng gefasst. Echt überlebensgroß wird es erst
  mit dem Original (2190 × 1150 px laut `posts.json`), das die Live-Seite hat und die Skizze nicht. Auf kleinen Handys
  (390 × 667) wird der Bildbogen ein Streifen von etwa 125 px. Dort greift der Titel nur mit einem Drittel ins Bild,
  damit die Augen sichtbar bleiben.
- **Höchstgröße der Titelzeile:** Die Titelzeile darf das Gesicht nicht verdecken. Darum füllt sie am Desktop 90 % der
  Wand und bei kleinem Bild oder sehr kurzem Wort weniger (`--titel-breite-gross`: „Mango“ 0,5, „Dosa“ 0,45). Im
  Theme wird das aus Bildhöhe und Fokuspunkt berechnet. Benachbarte Zusatzzeilen springen höchstens um etwa 1,4× in
  der Größe; der Umbruch wird danach gewählt (bei „Mango“ 1,41× statt 1,72× in der Alternative).
- **Zustände gezeigt statt beschrieben:** `zustaende.html` zeigt denselben Aufmacher mit zwei echten Beiträgen: einem
  langen Titel (82 Zeichen) mit kleinem Bild (692 × 359, Beitrag 9556) und einem Titel mit 4 Zeichen („Dosa“,
  Beitrag 9591), dessen Bild kein Gesicht hat.
- **Rubrik:** „KINO“ ist jetzt eine eigene Plakatzeile an der Wand über dem Titel (Handy 26 px, Desktop bis 40 px),
  nicht mehr ein kleines Wort im Fuß.
- **Kleine Handys:** Unter 720 px Höhe rücken Kopf, Rubrik und Abstände zusammen. Gemessen: Bei 390 × 667 endet
  „Lesen“ 8 px über der Daumenleiste, bei 360 × 640 ebenso. Aufnahme: `shots/index-erster-bildschirm-390x667.png`.
- **Fest-Bogen:** Am Handy steht er auf Papier mit rotem Datum; die Wand oben ist dort die einzige rote Fläche. Erst ab
  760 px klebt er rot und quer unter den Kino-Bögen.
- **Kino-Bögen:** Die Bogenbreite folgt dem Titel. „Scene“ (kurz) steht in einem schmalen, hohen Bogen (5/12),
  „Ramayana: Rise of a Legend“ (lang) in einem breiten, queren Bogen (7/12): Titel links, Kassenblock rechts unten.
  Die Zahl der Spielorte steht als Plakatziffer vorn („11“ gegen „2“).
