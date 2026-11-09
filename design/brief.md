# Design-Brief: tamil.de, Runde 2 – wie eine große Nachrichtenmarke

- **Status:** Arbeitsfassung 2 vom 09.11.2026. Bestätigt wird sie zusammen mit Luis' Wahl einer Schnellprobe
  (`docs/abnahme/<datum>-G1-runde2.md`). Fassung 1 (eine Geschichte als Cover, „Rot trägt“, vier Richtungen) ist
  abgelöst und steht in der Git-Historie (`6195fe5`).
- **Grundlage:** Urteil von Luis vom 09.11.2026 (`docs/abnahme/2026-11-09-G2.md`), Skill `tamil-marke` mit
  `references/abgelehnt.md`, die vermessenen Vorbilder in `design/referenzen/news-marken.md`.
- **Gilt für:** alle Proben dieser Runde und für die Prüfung. Der Brief geht jeder anderen Anleitung vor.

## 1. Zusammenfassung

tamil.de ist das deutschsprachige Magazin der tamilischen Diaspora in Deutschland, Österreich und der Schweiz. Die
Seite soll aussehen wie eine große, ruhige Nachrichtenmarke: klar, seriös, aufgeräumt, viele Geschichten auf einen
Blick. Vier Entwürfe sind abgelehnt, zuletzt als zu rot, zu laut, wie aus dem Baukasten, mit hässlicher Schrift und
nicht hochwertig. Diese Runde sucht keine Idee. Sie sucht Ordnung und Wertigkeit und zeigt Luis früh drei kleine
Proben.

## 2. Wichtigste Handlung

Wer die Startseite öffnet, erfasst in fünf Sekunden, was wichtig ist: ein klarer Aufmacher, daneben oder darunter
weitere Geschichten. Eine davon wird angetippt.

## 3. Gestaltung, für alle Varianten gleich

- **Szene:** Eine 19-Jährige liest in der S-Bahn am Handy, bei Tageslicht. Abends liest ihr Vater dieselbe Seite am
  Küchentisch. Beide sollen denken: Das ist eine richtige Nachrichtenseite, und sie ist für uns.
- **Farbe (feste Werte, nicht ändern):**

  | Rolle | Wert | Verwendung |
  |---|---|---|
  | Grund | `oklch(0.985 0.002 250)` | Seite; kein Creme, kein Sand |
  | Fläche | `oklch(0.962 0.003 250)` | höchstens für einen abgesetzten Block (Dienstblock) |
  | Tinte | `oklch(0.21 0.012 255)` | Schlagzeilen und Text |
  | Leise | `oklch(0.45 0.012 255)` | Datum, Bildzeilen, Nebeninfos (Kontrast ≥ 4,5:1) |
  | Linie | `oklch(0.88 0.004 250)` | feine Trennlinien, 1 Pixel |
  | Rot | `oklch(0.508 0.177 25.6)` (Logo-Rot #B5282A) | nur Logo, Dachzeilen oder kleine Marken, aktive Rubrik, Links beim Überfahren |

  Kein zweiter Buntton, keine Vollfarbflächen, kein Verlauf. Rot nie als Schlagzeile und nie als Fläche.
- **Schrift:** je Variante aus der Kandidatenliste in Abschnitt 4, normale Breite, höchstens zwei Familien.
  Tamil im Inhalt setzt eine Ersatzschrift im Schriftstapel (`lang="ta"`); auf den Proben kommt kein Tamil vor.

  | Stufe | Handy | Desktop |
  |---|---|---|
  | Schlagzeile Aufmacher | 26–32 px | 30–38 px |
  | Schlagzeile Nebenstück | 19–22 px | 20–24 px |
  | Schlagzeile Meldung | 17–18 px | 17–19 px |
  | Vorspann und Anreißertext | 16–17 px | 16–18 px |
  | Dachzeile, Datum | 12–14 px | 12–14 px |

  Der Aufmacher ist mindestens 1,25-mal so groß wie ein Nebenstück; Nebenstück und Meldung unterscheiden sich
  sichtbar in Größe oder Gewicht. Versalien nur in Dachzeilen bis 14 px. Keine Worttrennung in Schlagzeilen; jede Schlagzeile hat höchstens drei Zeilen, auch der längste Titel der
  Inhaltsliste (81 Zeichen).
- **Ordnung:** drei Stufen von Anreißern (Aufmacher, Nebenstück mit Bild, Meldung ohne Bild). Jeder Anreißer hat
  eine Dachzeile (Rubrik) und ein Datum in einem einzigen Format („17. Juli 2024“). Getrennt wird nur mit feinen
  Linien und Abstand: kein Kasten, kein Schatten, keine Pille, kein Icon, kein Knopf „Weiterlesen“. Der ganze
  Anreißer ist das Tippziel.
- **Bilder:** rechteckig, Radius höchstens 2 px, höchstens zwei Seitenverhältnisse auf der Seite, nie über ihrer
  natürlichen Breite gezeigt (bei doppelter Pixeldichte also höchstens halbe Dateibreite).
- **Kopf:** Logo unverändert, darunter oder daneben die neun Rubriken als schlichte Textzeile, in einem
  `<header>`. Am Handy sind Logo und Rubrikzeile zusammen höchstens 120 px hoch; die Rubrikzeile darf in ihrem
  eigenen Behälter seitlich laufen, die Seite selbst nie.
- **Dienstblock „Diese Woche“:** Kino (Titel, Zahl der Kinos, Städte) und Termine (Datum, Ort, Veranstalter) als
  nüchterne Liste. Das ist das Eigene von tamil.de; es braucht keinen Effekt. Am Handy beginnt der Block spätestens
  im dritten Bildschirm.
- **Keine Effekte:** keine Drehung, kein Stempel, kein Halbton, keine Bewegung, kein Laufband, keine feste Leiste am
  unteren Rand.

## 4. Die drei Varianten

Gleiches Inhaltsgerüst, gleiche Farben. Der Unterschied liegt auf zwei Reglern, damit Luis auch mischen kann.

| Slug | Schlagzeile | Aufmacher | Dichte | Familie der Vorbilder | Schriftkandidaten |
|---|---|---|---|---|---|
| `klar` | Grotesk, halbfett (600–700) | Bild halbe Breite neben dem Text (am Handy Bild über dem Text) | am höchsten: lange Meldungsliste direkt neben oder unter dem Aufmacher | Tagesschau, BBC | Libre Franklin **oder** Source Sans 3 |
| `blatt` | Serife nur in den Schlagzeilen (600–700), alles andere Grotesk | Bild über dem Text | mittel, mehr Luft, klare Spalten mit Linien | Zeit, Guardian, NZZ | Source Serif 4 **oder** Frank Ruhl Libre, dazu Source Sans 3 |
| `bild` | Grotesk, fett (700–800) | Bild über die volle Breite der Inhaltsspalte, Schlagzeile darunter | darunter ein vierspaltiger Block (am Handy einspaltig) | Spiegel | Hanken Grotesk **oder** Radio Canada Big |

- Alle Schriften sind frei lizenziert (OFL) und stehen nicht auf den Verbotslisten. Selbst hosten in
  `design/richtungen/<slug>/schriften/` mit Lizenzdatei.
- **Für `blatt` gilt eine ausdrückliche Ausnahme:** Eine Serife in den Schlagzeilen ist erlaubt. Verboten bleibt die
  Kombination aus Runde 2: Creme oder Sand, braungraue Tinte, Serife im Fließtext.
- **Für `bild`:** Das Aufmacherbild hat 1382 Pixel Breite. Es wird am Desktop höchstens 690 px breit gezeigt.

## 5. Umfang der Schnellprobe

Nur `index.html`, ernsthaft bei 390 und 1280 Pixeln; bei 820 nur kein seitlicher Überlauf. Von oben nach unten:

1. Kopf mit Logo und den neun Rubriken.
2. Aufmacher.
3. Vier Nebenstücke mit Bild.
4. Meldungsliste ohne Bild (sechs Titel).
5. Rubrikblock „Küche“ (vier Beiträge mit Bild).
6. Dienstblock „Diese Woche“ (zwei Kino-Einträge, ein Termin).

Kein Fuß, kein Artikel, keine Zustände, kein Werbeplatz, kein JavaScript. Die Begründung hat höchstens zehn Zeilen.

## 6. Inhalte

Fest für alle Varianten: `design/inhalte/inhalte.json`, Bilder in `design/inhalte/bilder/`, Logo
`design/inhalte/logo.png`. Genau diese Inhalte in genau dieser Reihenfolge; nichts weglassen, nichts erfinden. Der
Vorspann darf an einem Satzende gekürzt werden. Das Datum ist das Originaldatum und wird mit Jahr gezeigt (der
Bestand endet im November 2024). Alt-Texte nur, nachdem das Bild angesehen wurde. Die Rubrik „Kontakt“ und alle
Links führen in der Probe auf `#`.

## 7. Harte Kriterien (werden gemessen)

Gemessen wird der sichtbare erste Bildschirm bei 390 × 844 und 1280 × 800 mit `node design/vergleich/aufnahmen.mjs
<slug>`. Die Zahlen sind an sechs echten Marken geeicht (`design/referenzen/news-marken.md`, „Spanne der Marken“):
größte Schlagzeile 18 bis 32 px am Handy und 18 bis 36 px am Desktop; eine bis drei Schlagzeilen im ersten
Handy-Bildschirm, am Desktop bis zu vier (dort verdrängen Anzeigen oft die Inhalte); Radius 0 bis 1,5 px; keine
Schatten; Farbanteil ohne Bilder meist unter 8 %; die Schlagzeile des Aufmachers beginnt am Handy zwischen 332 und
588 px, weil das Bild davor steht.

1. **Viele Geschichten:** am Handy die Schlagzeile des Aufmachers vollständig und mindestens eine weitere
   Schlagzeile vollständig sichtbar; am Desktop mindestens vier. Jede Schlagzeile ist ein `h2` oder `h3` mit Link.
2. **Kopf** (Logo und Rubrikzeile) am Handy höchstens 120 px; die Schlagzeile des Aufmachers beginnt spätestens bei
   480 px.
3. **Drei Stufen** von Anreißern, der Aufmacher mindestens 1,25-mal so groß wie ein Nebenstück; höchstens zwei
   Schriftfamilien.
4. **Größte Schrift** im ersten Bildschirm höchstens 32 px am Handy und 38 px am Desktop; höchstens drei Zeilen je
   Schlagzeile; keine Versalien über 14 px.
5. **Rot** höchstens 3 % der Fläche (Bilder ausgeblendet); keine rote Schrift über 20 px; kein zweiter Buntton.
6. **Keine Effekte:** Radius höchstens 2 px, kein weicher Schatten, nichts gedreht, normale Schriftbreite.
7. **Anreißer ohne Kasten**, ohne Icon, ohne Knopf.
8. **Ein Format** für Dachzeile und Datum; höchstens zwei Bildformate.
9. **Kein Bild** über seiner natürlichen Breite bei doppelter Pixeldichte.
10. **Kein seitlicher Überlauf** bei 390, 820 und 1280; keine Konsolenfehler.
11. **Dienstblock** beginnt am Handy spätestens im dritten Bildschirm.
12. **Paarvergleich:** Die Probe liegt neben zwei Vorbildern und neben Runde 2. Ein Messwert außerhalb der Spanne
    der Marken ist ein P1.

Zum Vergleich die abgelehnten Skizzen der Runde 4 (`design/vergleich/kennzahlen/`): eine bis zwei Schlagzeilen im
ersten Bildschirm, größte Schrift 98 bis 335 px, Rotanteil 6 bis 54 %.

## 8. Pflichten

WCAG 2.2 AA (Kontrast Text ≥ 4,5:1), Tippflächen mindestens 44 × 44 px, sichtbarer Fokus auf jedem Link,
`prefers-reduced-motion` beachtet, Fließtext im Artikel später mindestens 18 px am Handy, nur Deutsch.

## 9. Offen

- **Logo:** Es liegt nur als kleines Bild vor (300 × 121 px) mit der Unterzeile „portal • lifestyle •
  entertainment“. In Kopfgröße wird die Unterzeile unlesbar. Luis ist nach einer Vektordatei gefragt; bis dahin
  bleibt das Bild unverändert.
- **Zustände, Artikel, weitere Seitentypen** kommen nach der Wahl (Skizze) und im Ausbau (Probeseite).
- **Die Auswahl des Auftraggebers** von der früheren Referenztafel ist mit der neuen Richtung überholt.
