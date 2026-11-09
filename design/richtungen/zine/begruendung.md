# Richtung `zine`: Heft der Woche

Skizze, Runde 1. Dateien: `index.html` (Cover + „Diese Woche“), `artikel.html` (Kopf bis erster Absatz),
`zine.css`, Schriften selbst gehostet in `fonts/` mit Lizenzdateien.

## 1. Vorbild

- **Burnt Roti** (https://burntroti.com, `design/referenzen/img/burntroti.png`). Übernommen: das Cover als
  Einstieg mit Haltung, das jede Woche neu gebaut wird; das Heft ist das Format, nicht der Blog darunter. Nicht
  übernommen: die Tropfschrift, der schwarze Feuer-Hintergrund und der gewöhnliche Blog-Teil darunter (genau die
  Schwäche, die der Scout benennt).
- **WEIRDO zine** (https://southasianbritain.org/organizations/weirdo-zine/, `weirdo.png`), bewertet über sein
  Cover. Übernommen: ein Foto, das nur in einer Farbe gedruckt ist, und eine einzige Akzentfarbe als Haltung. Bei
  uns wird das Foto in Logo-Rot gedruckt, die Schrift in fast schwarzer Tinte auf Papier.

## 2. Idee in einem Satz

tamil.de ist das Heft, das in der Diaspora sonst am Vereinsabend kopiert, gefaltet und am Tempeleingang ausgelegt
wird: jede Woche ein Cover im Zweifarbdruck mit der Kalenderwoche als Heftnummer, und darunter das Schwarze Brett
aus dem Asia-Laden, an dem Kino und Feste als Aushänge mit Abreißzetteln hängen.

## 3. Drei Stimmwörter (als Gegenstände)

**Copyshop-Kopie** (zwei Tinten, etwas schief aufgeklebt) · **Abreißzettel** (Aushang mit Streifen zum Mitnehmen)
· **Gummistempel** (Rubrik, Datum, ein Abdruck, nicht zehn).

## 4. Schrift

Verfahren nach `impeccable/reference/brand.md`.

- **Reflex-Schriften und warum nicht:** *Bebas Neue* (jedes Plakat-Template seit 2012, keine Breitenachse, nur
  Versalien), *Space Mono* bzw. Schreibmaschine (steht auf der Ausschlussliste; Mono wäre hier Kostüm),
  *Permanent Marker* (Handschrift-Imitat, wirkt nach Bastelvorlage und ist für Ältere schlecht lesbar). Dazu tabu:
  Inter, DM Sans, Space Grotesk, Fraunces, Playfair sowie Catamaran, Literata, Anek, Schibsted Grotesk, Noto Serif
  Tamil.
- **Auszeichnung: Anybody** (Etcetera Type Co., Google Fonts, SIL OFL). Eine Grotesk mit Breitenachse von 50 bis
  150 und Gewichtsachse 100 bis 900. Das ist die Zine-Technik ohne Kitsch: Beim Kleben eines Covers wird Schrift
  gestaucht und gestreckt, bis sie die Fläche füllt. Anybody tut das sauber. Das Coverwort steht am Handy
  schmal und hoch (Breite 50), am Desktop breit (Breite 100 bis 130); die Rubrik-Stempel und Abreißzettel nutzen
  schmale halbfette Schnitte. Eine Familie, viele Stimmen.
- **Text: Atkinson Hyperlegible Next** (Braille Institute, Google Fonts, SIL OFL). Gezeichnet für Menschen mit
  Sehschwäche, eindeutige Formen bei I/l/1 und 0/O. Das ist die ehrliche Antwort auf „Eltern und Großeltern lesen
  mit“: keine Serife (altbacken), aber auch keine anonyme Grotesk, sondern eine Schrift mit Haltung zur
  Lesbarkeit. Fließtext 19 px am Handy, 20 px am Desktop, Zeilen höchstens 64 Zeichen.
- **Tamil im Inhalt:** Ersatzschrift **Noto Sans Tamil** (SIL OFL, nur Tamil-Teilmenge, selbst gehostet) im
  Stapel und über `:lang(ta)`. Tamilische Schrift kommt als Gestaltungsmittel nirgends vor.
- Lizenzen: `fonts/OFL-anybody.txt`, `fonts/OFL-atkinsonhyperlegiblenext.txt`, `fonts/OFL-notosanstamil.txt`.

## 5. Farbstrategie: Committed, als Zweifarbdruck

Gedacht wie eine Riso-Kopie: zwei Tinten auf einem Papier. Rot trägt die Fläche über die Fotos und das Schwarze
Brett, nicht über Platten hinter Text.

| Token | Wert | Rolle |
|---|---|---|
| `--papier` | `oklch(97.6% 0.006 25)` | Grund, kühles Weiß mit einem Hauch Rot, kein Creme |
| `--tinte` | `oklch(21% 0.018 25)` | Schrift, Linien |
| `--rot` | `oklch(50.8% 0.177 25.6)` | Logo-Rot #B5282A: Fotodruck, Stempel, Schwarzes Brett |
| `--rot-tief` | `oklch(43% 0.16 25.6)` | rote Schrift auf Papier in kleinen Größen |
| `--grau` | `oklch(42% 0.012 25)` | Nebeninfos, nur ab 16 px |

- Fotos auf dem Cover werden einfarbig in Rot gedruckt (Graustufen, im Modus „screen“ über Rot gelegt, dazu ein
  sehr feines Raster). Dunkles wird Rot, Helles wird Papier. Das Bild ist rot, aber es ist ein Bild, keine Platte.
- „Diese Woche“ steht auf rotem Karton (das Schwarze Brett); die Aushänge darauf sind Papier mit schwarzer Tinte.
  Text auf Rot ist nur die große Abschnittsüberschrift in Papierweiß (Kontrast etwa 5,9:1).
- Kein reines Schwarz oder Weiß, kein Gold, kein Gelb, kein Nachtblau.
- Im Artikel bleibt das Foto in Farbe: Nachrichten sind belegt und ruhig; der Zweifarbdruck gehört dem Cover.

## 6. Signatur-Element

**Das Wochen-Cover im Zweifarbdruck:** ein Coverwort in riesiger gestauchter Anybody, ein in Rot gedrucktes Foto,
leicht schief eingeklebt und das Coverwort anschneidend, ein roter Gummistempel mit der Rubrik und die
Heftzeile „Heft KW 46“ (die echte Kalenderwoche vom 9. bis 15. November 2026, keine erfundene Ausgabennummer).
Darunter, als zweites Erkennungszeichen: **Aushänge mit Abreißzetteln**, bei denen jeder Spielort ein Streifen
ist. 11 Kinos ergeben eine lange gestrichelte Reihe, 2 Kinos eine kurze.

## 7. Abgrenzung zu den abgelehnten Runden

1. **Runde 1 (Nachtblau, Gold, Laufband):** heller Papiergrund, nur zwei Tinten (Rot und fast Schwarz), keine
   tamilischen Wörter, kein Laufband, keine Bewegung außer einem leisen Zurechtrücken beim Zeigen mit der Maus.
2. **Runde 2 (Creme, Serife, Braungrau, Mosaik):** kühles Papierweiß statt Sand, Grotesk statt Serife im Text,
   fast schwarze Tinte statt Braungrau, statt Mosaik ein einziges Cover und dann ein Aushangbrett mit eigenem
   Rhythmus.
3. **Runde 3 (App-Vorlage, rote Platte, Pillen, runde Karten):** keine Rundungen, keine Pillen, keine
   Story-Kreise, keine Knopfreihen. Die Überschrift steht auf Papier, nicht auf einer roten Platte; Rot ist
   Druckfarbe des Fotos. Die Aushänge sind verschieden groß, verschieden schief und tragen Abreißzettel, kein
   gleichförmiges Kartenraster.

## 8. Zustände aus dem Brief

- **Kleines Bild:** Das Cover trägt über das Coverwort und die Heftzeile. Das Foto wird nie größer als seine
  Pixelbreite gezeigt (`max-width` auf die natürliche Breite, am Desktop belegt es rund 680 von 1024 px). Bei
  Bildern unter 700 px rückt es kleiner ein und das Coverwort bekommt mehr Fläche; das Zweifarbraster kaschiert
  leichte Unschärfe besser als ein Farbfoto.
- **Eintrag ohne Foto:** Die Aushänge sind gebaut, um ohne Foto zu bestehen: Titel, Art (Im Kino, Fest), Ort als
  Abreißzettel, Datum als roter Stempel, wenn es eines gibt. Kein Platzhalterbild.
- **Lange und kurze Überschrift:** Das Coverwort ist der Teil vor Gedankenstrich oder Doppelpunkt („Kanguva“), der
  Rest steht als Coverzeile darunter. Ein kurzer Titel wie „Dosa“ ist komplett Coverwort. Ein Titel mit 78 Zeichen
  ohne Trenner bekommt die Coverzeilen-Größe als Ganzes (Klasse `cover--lang`), damit er am Handy im ersten
  Bildschirm bleibt. Auf dem Brett zeigen „Scene“ (5 Zeichen) und „Ramayana: Rise of a Legend“ den Unterschied.
- **Viele und wenige Spielorte:** Abreißzettel brechen um. „Scene“: fünf benannte Städte und ein roter Zettel
  „+ 6 weitere Städte“ (die anderen sechs sind im Entwurf nicht benannt, also werden sie nicht erfunden).
  „Ramayana“: zwei Zettel.
- **Fokus:** 3 px Tintenrahmen mit Abstand auf Papier, Papierrahmen auf Rot. **Bewegung:** nur das Zurechtrücken
  des Covers beim Zeigen; bei `prefers-reduced-motion` ausgeschaltet.

## 9. Bedienung

- Das ganze Cover ist ein Link zum Artikel.
- Am Handy liegt die Rubrikleiste unten in Daumenreichweite (Kino, Events, Nachrichten, Inhalt), eckig, durch
  Linien getrennt, jede Fläche mindestens 48 px hoch. „Inhalt“ springt zum Inhaltsverzeichnis am Seitenende, das
  wie die letzte Heftseite alle Rubriken groß aufführt. Am Desktop steht die Rubrikzeile oben.
- Teilen im Artikel: ein normaler Link zu WhatsApp (`wa.me`), kein Skript.
- Kein JavaScript.
