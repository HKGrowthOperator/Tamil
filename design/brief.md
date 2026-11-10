# Design-Brief: tamil.de, Runde 2 – wie eine große Nachrichtenmarke

- **Status:** Fassung 2.1 vom 10.11.2026. Fassung 2 wurde am 10.11.2026 mit der Wahl der Probe `klar` durch Luis
  bestätigt (`docs/abnahme/2026-11-10-G1-runde2.md`). Nach seinem Urteil zu `klar` („gut, aber zu classic“, mehr Wow,
  überall ein Bild, der Kopf zu schlicht) kommt **Abschnitt 10** dazu. Er gilt für die Fassung `klar2` und geht dort
  den Abschnitten 3 bis 7 vor. Fassung 1 (eine Geschichte als Cover, „Rot trägt“, vier Richtungen) ist abgelöst und
  steht in der Git-Historie (`6195fe5`).
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
  sichtbar in Größe oder Gewicht. Versalien nur in Dachzeilen bis 14 px. Keine Worttrennung in Schlagzeilen. Die Schlagzeile des Aufmachers hat höchstens drei Zeilen, jede andere
  höchstens vier, auch der längste Titel der Inhaltsliste (81 Zeichen); drei sind das Ziel.
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
   Das ist bewusst strenger als bei den Marken, weil die Probe keine Anzeigen zeigt.
2. **Kopf:** Logo und Rubrikzeile stehen im `<header>`, am Handy zusammen höchstens 120 px hoch; die Schlagzeile des
   Aufmachers beginnt spätestens bei 480 px.
3. **Drei Stufen** von Anreißern auf der ganzen Seite, der Aufmacher mindestens 1,25-mal so groß wie ein
   Nebenstück; höchstens zwei Schriftfamilien.
4. **Größte Schrift** im ersten Bildschirm höchstens 32 px am Handy und 38 px am Desktop; die Schlagzeile des
   Aufmachers hat höchstens drei Zeilen, jede andere höchstens vier; keine Versalien über 14 px.
5. **Rot** höchstens 3 % der Fläche (Bilder ausgeblendet); keine rote Schrift über 20 px; kein zweiter Buntton in
   den eigenen Elementen der Seite.
6. **Keine Effekte:** Radius höchstens 2 px, kein weicher Schatten, nichts gedreht, normale Schriftbreite.
7. **Anreißer ohne Kasten**, ohne Icon, ohne Knopf. Kasten heißt: Hintergrundfläche oder Rahmen um einen einzelnen
   Anreißer; Linien zwischen Anreißern sind erlaubt. Auch die Rubrikzeile hat keine Pillen oder Knöpfe.
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

## 10. Fassung 2.1: mehr Wow (gilt für `klar2`)

**Urteil von Luis zu `klar` (10.11.2026):** „Vom Design gefällt es mir, aber es ist noch ein wenig zu classic.“ Er
will mehr Wow, überall ein Bild und einen Kopf, der mehr kann. Auf Nachfrage hat er alles gewählt: großes
Aufmacherbild, bildstarke Blöcke, ein dunkler Kino-Bereich, sanfte Bewegung; im Kopf ein kräftiger Balken, mehr
Inhalt, größer und klarer, Rubriken mit Bild (`docs/abnahme/2026-11-10-G2-runde2.md`).

`klar2` ist `klar` mit mehr Bild und mehr Bühne: dieselbe Schrift (Libre Franklin), dieselben Farbwerte, dieselbe
Ordnung der Nachrichten. Es ist keine neue Richtung. Das Risiko ist bekannt: Acht Verstärkungen auf einmal können
in „zu laut“ kippen, daran ist Runde 4 gescheitert. Deshalb hat jede Verstärkung eine messbare Grenze. Das Wow
kommt aus Fotos, Fläche und Kontrast von Hell und Dunkel, nicht aus Schriftgröße, Rot oder Effekten.

Wo dieser Abschnitt nichts sagt, gelten die Abschnitte 1 bis 9 weiter. Inhalte: `design/inhalte/inhalte-klar2.json`
(statt `inhalte.json`).

### 10.1 Was neu erlaubt ist, jeweils mit Grenze

- **Dunkle Flächen, genau zwei:** das Rubrikband im Kopf und der Bereich „Diese Woche“. Dunkel ist die Tinte
  `oklch(0.21 0.012 255)`, kein Nachtblau, kein Schwarz, kein Gold daneben. Der Grund der Seite bleibt hell: Im
  ersten Bildschirm sind höchstens 12 % der Fläche dunkel (Bilder ausgeblendet).

  | Rolle auf Dunkel | Wert | Verwendung |
  |---|---|---|
  | Schrift hell | `oklch(0.985 0.002 250)` (der Grund) | Titel, aktive Rubrik |
  | Schrift leise hell | `oklch(0.82 0.006 250)` | Rubriken, Datum, Orte, Nebeninfos |
  | Linie auf Dunkel | `oklch(0.36 0.010 255)` | feine Trennlinien, 1 Pixel |
  | Fläche auf Dunkel | `oklch(0.26 0.012 255)` | nur für die gestalteten Kacheln ohne Foto |

  Rot hat auf Dunkel zu wenig Kontrast für Schrift (rund 2,6 : 1). Dachzeilen auf dunklem Grund und im Bild sind
  deshalb hell. Rot darf dort nur als Linie stehen, und nie als einziges Zeichen für einen Zustand.
- **Titel im Bild:** beim Aufmacher, bei den Rubrikkacheln und bei den Bildkacheln in „Diese Woche“ und „Küche“.
  Unter der Schrift liegt ein Verlauf von durchsichtig nach Tinte; das ist der einzige erlaubte Verlauf. Gemessen
  wird der Kontrast an der hellsten Stelle unter jeder Zeile: mindestens 4,5 : 1. Nebenstücke und Meldungen
  behalten ihren Text neben oder unter dem Bild.
- **Größere Schlagzeile nur beim Aufmacher:** 28 bis 34 px am Handy, 36 bis 44 px am Desktop, höchstens drei
  Zeilen. Titel in den großen Kacheln (Kino, Küche) höchstens 24 px am Handy und 28 px am Desktop. Alle anderen
  Stufen bleiben wie in Abschnitt 3.
- **Großes Aufmacherbild:** am Handy randlos über die volle Breite; am Desktop mindestens 760 px breit (rund 60 %
  der Inhaltsbreite), daneben oder darunter weitere Schlagzeilen, damit der erste Bildschirm viele Geschichten
  zeigt. Dachzeile und Schlagzeile stehen unten im Bild; ein Vorspann darf darunter stehen.
- **Bewegung, nur als Antwort:** Bilder zoomen beim Überfahren leicht (Maßstab höchstens 1,04, Übergang höchstens
  0,4 s, sanft auslaufend), Links ändern die Farbe. Das Rubrikband bleibt beim Scrollen stehen (`position: sticky`,
  höchstens 56 px hoch); Kopfzeile und Logo scrollen weg, der Kopf wird so von selbst flacher. Nichts bewegt sich
  von selbst: keine `animation`, kein Laufband, kein Einblenden beim Scrollen, kein JavaScript. Mit
  `prefers-reduced-motion: reduce` gibt es keinen Übergang.
- **Bildformate:** höchstens drei Seitenverhältnisse auf der Seite (bisher zwei), zum Beispiel eines für die
  Anreißer, eines für Aufmacher und große Kacheln, eines für die Rubrikkacheln.
- **Bildgröße:** Kein Bild wird über seine Dateibreite hinaus gezeigt. Bei doppelter Pixeldichte gilt weiter die
  halbe Dateibreite; ausgenommen sind das Aufmacherbild und die eine große Kachel in „Diese Woche“ und in „Küche“.
  Die echte Seite liefert später größere Dateien aus.

### 10.2 Aufbau von oben nach unten

1. **Kopf in drei Teilen.**
   - *Kopfzeile* (schmal, heller Grund, 13 bis 14 px, Leise): links das Datum, in der Mitte oder rechts die zwei
     Hinweise „Diese Woche“ als Links zum Bereich, ganz rechts die Suche (Wort „Suche“, eine kleine Lupe als
     Bedienelement ist erlaubt). Am Handy bleiben Datum und Suche; die Hinweise dürfen entfallen.
   - *Logo* auf hellem Grund, unverändert, größer als bei `klar`: am Handy 44 bis 52 px hoch, am Desktop 56 bis
     60 px (mehr trägt die Datei mit 300 × 121 px nicht).
   - *Rubrikband* (dunkel, ein `<nav>`): die neun Rubriken in „Schrift leise hell“, 15 bis 16 px. Die aktive Rubrik
     hat volle Helligkeit, Gewicht 600 und darunter eine 3 px starke Linie (hell oder Rot). Keine Pillen, keine
     Knöpfe. Am Handy läuft das Band seitlich in sich; jede Rubrik ist 44 px hoch tippbar.

   Am Handy sind die drei Teile zusammen höchstens 152 px hoch.
2. **Aufmacher** mit großem Bild, Dachzeile und Schlagzeile im Bild.
3. **Rubrikkacheln:** sieben kleine Bildkacheln mit dem Rubriknamen im Bild (15 bis 17 px, Gewicht 600). Sie sind
   Navigation, keine Schlagzeilen (kein `h2`, kein `h3`). Am Desktop eine Reihe; am Handy ein Streifen, der in
   seinem eigenen Behälter seitlich läuft und an der rechten Kante sichtbar angeschnitten ist. Die Kacheln stehen
   so, dass die harten Kriterien 1 und 15 erfüllt bleiben (unter dem Aufmacher oder unter dem Nachrichtenblock).
4. **Nachrichten:** vier Nebenstücke mit Bild und sechs Meldungen, jede mit kleinem Bild (am Handy mindestens
   96 px breit, am Desktop mindestens 120 px). Die Ordnung aus `klar` bleibt: Dachzeile „Rubrik | Datum“, Linien
   statt Kästen.
5. **„Diese Woche“** (`id="diese-woche"`, dunkel, über die volle Breite): zwei Kino-Beiträge als Bildkacheln mit
   Titel im Bild, die erste groß. Daneben oder darunter „Im Kino“ mit den zwei Filmen aus dem News-Radar und
   „Termine“ mit Diwali in Basel. Diese drei Einträge haben kein Foto; sie sind gestaltete Kacheln aus Schrift und
   „Fläche auf Dunkel“ und tragen `data-grafik`. Die Zahl der Kinos und das Datum des Termins sind dort die größten
   Angaben nach dem Titel. Kein erfundenes Bild, kein Platzhalterbild, kein Icon.
6. **„Küche“** (`id="kueche"`, heller Grund): vier Bildkacheln mit Titel im Bild, die erste deutlich größer als die
   anderen. Vier gleiche Kacheln in einer Reihe sind ausgeschlossen.
7. **Artikel** (`artikel.html`): derselbe Kopf, das Bild groß (randlos am Handy), sonst ruhig wie bei `klar`.

### 10.3 Was sich nicht ändert

Die sechs Farbwerte aus Abschnitt 3; Libre Franklin in normaler Breite, höchstens zwei Familien; nur Deutsch; Rot
höchstens 3 % der Fläche und keine rote Schrift über 20 px; kein zweiter Buntton; keine Versalien über 14 px;
Radius höchstens 2 px; kein weicher Schatten (auch nicht an Schrift); nichts gedreht; keine Pillen, Icons oder
Knöpfe an Anreißern; ein Format für Dachzeile und Datum; die Pflichten aus Abschnitt 8.

### 10.4 Harte Kriterien für `klar2` (ersetzen Abschnitt 7 für diese Fassung)

Gemessen wird mit `node design/vergleich/aufnahmen.mjs klar2` bei 390 × 844 und 1280 × 800; in Klammern steht die
Kennzahl aus `design/vergleich/kennzahlen/klar2.json`.

1. **Viele Geschichten:** am Handy die Schlagzeile des Aufmachers und mindestens eine weitere vollständig sichtbar;
   am Desktop mindestens vier (`schlagzeilen_ganz_sichtbar`). Jede Schlagzeile ist ein `h2` oder `h3` mit Link.
2. **Kopf:** am Handy höchstens 152 px bis zur Unterkante des Rubrikbands (`kopfleiste_hoehe`); die Schlagzeile des
   Aufmachers beginnt spätestens bei 480 px (`erste_schlagzeile_ab`).
3. **Drei Stufen** von Anreißern, der Aufmacher mindestens 1,25-mal so groß wie ein Nebenstück; höchstens zwei
   Schriftfamilien.
4. **Größte Schrift:** höchstens 34 px am Handy und 44 px am Desktop, und das ist die Schlagzeile des Aufmachers;
   die zweitgrößte Schrift der Seite höchstens 24 und 28 px (`schriftgroessen_seite`). Aufmacher höchstens drei
   Zeilen, jede andere Schlagzeile höchstens vier. Keine Versalien über 14 px.
5. **Rot** höchstens 3 % der Fläche (Bilder ausgeblendet); keine rote Schrift über 20 px; kein zweiter Buntton.
6. **Dunkel:** genau zwei dunkle Flächen, Rubrikband und „Diese Woche“ (`dunkle_flaechen`); im ersten Bildschirm
   höchstens 12 % dunkel (`farbanteil_ohne_bilder.dunkel`).
7. **Keine Effekte:** Radius höchstens 2 px, kein weicher Schatten, nichts gedreht, normale Schriftbreite; ein
   Verlauf nur unter Schrift im Bild.
8. **Kein Baukasten:** Anreißer ohne Kasten, Icon oder Knopf; keine Pillen. Eine Bildkachel ist kein Kasten; die
   drei gestalteten Kacheln ohne Foto dürfen „Fläche auf Dunkel“ tragen.
9. **Überall ein Bild:** kein Anreißer ohne Bild (`anreisser_ohne_bild` leer); gestaltete Kacheln ohne Foto nur
   für die drei Einträge aus dem News-Radar (`anreisser_mit_grafik` höchstens drei).
10. **Ein Format** für Dachzeile und Datum; höchstens drei Bildformate.
11. **Bildgröße:** kein Bild über seiner Dateibreite (`bilder_ueber_dateibreite` leer); bei doppelter Pixeldichte
    über der halben Dateibreite nur das Aufmacherbild und die große Kachel in „Diese Woche“ und „Küche“
    (`bilder_ueber_natuerlicher_breite`).
12. **Helle Schrift** auf Bild oder dunklem Grund: Kontrast mindestens 4,5 : 1 an der hellsten Stelle
    (`helle_schrift.unter_4_5` leer).
13. **Bewegung:** Maßstab höchstens 1,04 (`groesster_massstab`); längster Übergang höchstens 0,4 s; keine
    Animation; mit „Bewegung reduzieren“ kein Übergang (`bewegung_bei_reduziert`); fest steht nur das Rubrikband,
    höchstens 56 px hoch (`fest_stehend`).
14. **Kein seitlicher Überlauf** bei 390, 820 und 1280; keine Konsolenfehler.
15. **„Diese Woche“** beginnt am Handy spätestens im dritten Bildschirm (Oberkante bei höchstens 2532 px).
16. **Paarvergleich:** `klar2` liegt neben `klar`, neben zwei Vorbildern (BBC und Spiegel) und neben Runde 2 und
    Runde 4. Ein Messwert außerhalb dieser Grenzen ist ein P1.

Zwei Fragen beantwortet die Prüfung zusätzlich in Worten, an beobachtbaren Unterschieden: Wirkt `klar2` neben
`klar` sichtbar bildstärker und weniger „classic“? Und ist irgendetwas daran laut, verspielt oder Baukasten
geworden?

