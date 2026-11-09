# Richtung „raster“: Raster + große Schrift

Skizze, Runde 1. Seiten: `index.html` (Cover + „Diese Woche“), `artikel.html` (Kopf bis erster Absatz),
Stil: `raster.css`, Schriften: `fonts/` (mit Lizenzdateien).

## 1. Vorbild

- **Highsnobiety** (https://www.highsnobiety.com, `design/referenzen/img/highsnobiety.png`): die schmale, fette
  Grotesk in Versalien für Marke und Navigation, ein einziges großes Element im Kopf, weißer Grund ohne Farbflächen.
  Übernommen: die Strenge der Hierarchie und die Navigation als Zeile aus Versalien.
- **Hypebeast** (https://hypebeast.com, `design/referenzen/img/hypebeast.png`): dünne Trennlinien statt Karten,
  Überschriften groß und dunkel, Spalten durch Haarlinien getrennt. Übernommen: **Linien als Raster**, keine Schatten,
  keine Rundungen.
- Nicht übernommen (Warnungen aus der Referenzliste): Werbung im Kopf, Reaktionszahlen, Produktlastigkeit, die
  Abhängigkeit von starken Modefotos. Bei uns trägt die Schrift, nicht das Foto.

## 2. Idee in einem Satz

tamil.de ist der **Aushang der Diaspora**: ein rotes Linienraster wie die Spielfeldlinien in der Schulaula, in der
die Gemeinde feiert, und jede Geschichte, jede Stadt, jeder Kinosaal bekommt darin ein eigenes Feld, vom
Kinostart in elf Städten bis zum Diwali in einer Basler Aula.

Warum nur tamil.de: Tamilisches Leben in DACH findet nicht in einer Hauptstadt statt, sondern verstreut, in
Mittelstadtkinos, Vereinsaulen und Tempeln von Gütersloh bis Ravensburg. Das Raster macht diese Verstreuung lesbar.
Die Anzahl der Felder **ist** die Information (11 Kinos sehen anders aus als 2).

## 3. Drei Stimmwörter (als Gegenstände)

1. **Fahrplanaushang** am Bahnsteig: Zeilen, Spalten, große Zeit links, alles auf einen Blick, auch für Oma.
2. **Steckbuchstabentafel** vor dem Kino: große, schmale Versalien in Reih und Glied, ein Wort füllt die Tafel.
3. **Hallenbodenlinie** in der Turnhalle oder Aula: rote Linien auf hellem Boden, die den Raum ordnen, ohne ihn
   zu füllen.

## 4. Schrift

Verfahren nach `impeccable/reference/brand.md`.

**Reflex-Schriften, verworfen:**
- *Bebas Neue / Anton*: die erste Antwort auf „schmale Plakatversalien“; tausendfach auf Eventflyern, nur Versalien
  bzw. nur ein Schnitt, keine Textschnitte. Wirkt sofort wie Vorlage.
- *Oswald*: die Google-Fonts-Standardantwort auf „Highsnobiety-Grotesk“; enge Laufweite, aber flache Schnitte
  und schwache Kleinbuchstaben.
- *Inter / Space Grotesk*: Ausschlussliste; außerdem der Klang jeder SaaS-Seite.
(Verbrannte Schriften dieses Projekts kommen nicht in Frage: Catamaran, Literata, Anek, Schibsted Grotesk,
Noto Serif Tamil, Fraunces.)

**Gewählt:**
- **Archivo** (Omnibus-Type, OFL), variabel mit Breitenachse `wdth 62–125` und Gewicht `100–900`. Gebaut für
  Schlagzeilen in Druck und Netz, also Zeitungs- und Aushang-Grotesk, nicht Mode-Grotesk. Eine Familie liefert die
  ganze Lautstärke: das Cover-Wort in `wdth 62 / wght 850` (Steckbuchstabentafel), Überschriften in `wdth 75–80 / 700`,
  Etiketten und Navigation in `wdth 85 / 600` Versalien. Das Raster bekommt seinen Ton aus **einer** Familie mit
  harten Breitensprüngen statt aus einem Schriftpaar.
- **Atkinson Hyperlegible Next** (Braille Institute, OFL) für Vorspann und Fließtext. Entworfen für Menschen mit
  Sehschwäche: eindeutige Formen bei I/l/1, 0/O, offene Punzen. Das ist die Antwort auf „Eltern und Großeltern
  lesen mit“, ohne dass die Seite alt aussieht; sie ist eine Grotesk, keine Serife auf Creme.
- **Tamil:** kommt in den beiden Skizzenseiten nicht vor. Für Inhalte mit `lang="ta"` steht im Stapel eine
  Ersatzschrift (`Noto Sans Tamil`, `Tamil Sangam MN`, `Latha`, `Nirmala UI`), gesetzt über `:lang(ta)` mit größerer
  Zeilenhöhe. Auszeichnungsschriften decken Tamil laut Brief nicht ab; tamilische Schrift ist kein Gestaltungsmittel.
- Beide Schriften liegen selbst gehostet in `fonts/` (Teilmenge Latein, woff2; deckt Umlaute, ß und deutsche Anführungszeichen), Lizenzen
  `fonts/OFL-Archivo.txt` und `fonts/OFL-AtkinsonHyperlegibleNext.txt`.

## 5. Farbstrategie: Committed, aber in Linie und Schrift, nicht in Platten

- **Träger:** Logo-Rot #B5282A = `oklch(0.508 0.177 25.6)`. Es ist die **einzige** bunte Farbe der Seite.
- **Grund:** `oklch(0.985 0.004 25)`, ein Weiß mit einem Hauch Rot, kein Creme, kein Sand.
- **Tinte:** `oklch(0.2 0.012 25)`, zum Rot getöntes Fast-Schwarz. Zweitton für Metadaten `oklch(0.42 0.015 25)`
  (Kontrast > 7:1 auf dem Grund).
- **Wo das Rot sitzt:** (1) alle Rasterlinien, (2) das Cover-Wort in Riesengröße, (3) die großen Zeitangaben im
  Fahrplan „Diese Woche“, (4) das Logo. Nie als Fläche hinter Text, nie als Platte über einem Bild, kein Band.
- **Wie viel Fläche, und warum so:** Ein strenges Raster verträgt keine roten Flächen, ohne seine Linien zu
  verlieren; eine rote Platte wäre außerdem genau der abgelehnte Aufmacher aus Runde 3. Das Rot bekommt deshalb seine
  Masse über **Schriftgröße**: Das Cover-Wort füllt am Handy die ganze Breite und deckt mit Logo und Linien grob ein
  Viertel bis ein Drittel des ersten Bildschirms ab; am Desktop ist es die breiteste Form der Seite. Das liegt im
  unteren Bereich von „Committed“ und ist bewusst so: laut im Kopf. Im Artikel bleibt nur das Linienrot (ruhig im
  Text).
- Kontrast: Rot auf Grund ≈ 6,2:1 (AA auch für kleine Schrift), Tinte auf Grund ≈ 16:1.

## 6. Signatur-Element

**Das rote Raster mit dem Steckbuchstaben-Wort.** Der erste Bildschirm ist ein Aushang aus roten Haarlinien; im
obersten Feld steht das Stichwort der großen Geschichte („KANGUVA“) so groß, dass es die volle Rasterbreite füllt.
Darunter setzt sich dasselbe Raster als **Ortsraster** fort: Jeder Kino- oder Eventeintrag hat ein Feld pro Stadt.
„Scene“ füllt eine Zeile mit Städten, „Ramayana“ zwei Felder, Diwali ein einziges Feld „Basel, Aula Lysbüchel“.

## 7. Abgrenzung zu den abgelehnten Runden

1. **Gegen Runde 1 (Nachtblau, Gold, Laufband):** heller Grund, genau eine bunte Farbe, keine Ornamente, kein
   Laufband, keine tamilischen Wörter. Die einzige Bewegung ist die des Lesers.
2. **Gegen Runde 2 (Creme, Serife, Mosaik):** kein Creme, kein Braungrau, keine Serife im Text, keine runden Bilder.
   Statt Mosaik mit Seitenleiste ein einziger Aufmacher und darunter ein Fahrplan; die Ordnung kommt aus Linien,
   nicht aus Kästen.
3. **Gegen Runde 3 (App-Vorlage):** keine Pillen, keine Rundungen (überall `border-radius: 0`), keine Story-Kreise,
   keine Knopfreihen, keine rote Platte über dem Bild, keine 01/02/03. Etiketten sind Text in einem Rasterfeld, kein
   Hintergrundkasten. Das Rot ist Linie und Schrift.

## 8. Zustände (Brief, Abschnitt 6)

- **Aufmacher mit kleinem Bild:** Das Bild sitzt in einem Rasterfeld mit `max-width` = Originalbreite
  (`p9711.jpg`: 1024 px) und wird nie hochskaliert. Das Cover trägt über das Stichwort und die Überschrift; ist das
  Bild schmaler als sein Feld, bleibt das Feld stehen und das Bild sitzt links oben darin, die Linien schließen es ein.
  Auch ein schwaches Foto liegt so in einem gebauten Rahmen statt in einer leeren Fläche.
- **Eintrag ohne Foto:** Kino und Events haben **nie** ein Bild. Ihre Form ist der Fahrplan: große rote Zeitangabe,
  Titel, Ortsraster. Ohne Bild sieht nichts leer aus, weil nichts für ein Bild gebaut ist.
- **Lange und kurze Überschrift:** Das Cover zerlegt den Titel am Gedankenstrich in **Stichwort** (Steckbuchstaben,
  rot, füllt die Breite) und **Satz** (Tinte, Archivo `wdth 75`). „Kanguva – Ein tamilisches Kino-Highlight …“ wird zu
  KANGUVA + Satz. Ohne Gedankenstrich gilt: bis etwa 12 Zeichen („Dosa“) steht der ganze Titel als Stichwort;
  längere Titel (bis 78 Zeichen) stehen ganz als Satz in der nächstkleineren Stufe `wdth 62 / 800` in Rot, mit
  `text-wrap: balance`. Das Theme entscheidet das über die Zeichenzahl, nicht die Redaktion.
- **Viele und wenige Spielorte:** Das Ortsraster füllt sich mit `auto-fill`. Bei 11 Kinos zeigt die Skizze die fünf
  im Entwurf genannten Städte und ein sechstes Feld „und 6 weitere Städte“ (die übrigen Namen nennt der freigegebene
  Entwurf nicht, deshalb erfinde ich sie nicht); 2 Kinos sind zwei Felder. Die Zahl steht zusätzlich als Text.
- **Fokus:** 3 px Tintenrahmen mit Abstand auf jedem Link; die Cover-Fläche bekommt beim Fokus einen Rahmen um das
  ganze Feld. **Bewegung:** keine Animation; Übergänge (nur Farbe der Unterstreichung) entfallen bei
  `prefers-reduced-motion: reduce`.

## 9. Bedienung

- Das ganze Cover-Feld ist ein Link auf den Artikel (Überschriften-Link mit über das Feld gezogener Fläche).
- Navigation: am Desktop eine Zeile Rasterfelder im Kopf; bis 899 px eine feste Leiste unten mit vier Feldern
  (Nachrichten, Kino, Events, Rubriken), jedes ≥ 56 px hoch, in Daumenreichweite. „Rubriken“ springt zum Rubrikenraster
  am Seitenende (ohne JavaScript).
- Teilen über WhatsApp im Artikel als einfacher Link (`https://wa.me/?text=…`), kein Skript.
- Kein JavaScript auf beiden Seiten.
