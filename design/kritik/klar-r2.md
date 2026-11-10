# Prüfung klar, Runde 2
Harte Kriterien: 12 von 12 erfüllt · P0: 0 · P1: 1 · P2: 4

Grundlage: `node design/vergleich/aufnahmen.mjs klar` (Kennzahlen `design/vergleich/kennzahlen/klar.json`, Stand
2026-11-10T09:49), `tools/shots.mjs` bei 390/820/1280 für `index.html` und `artikel.html` (0 Fehler), eigene Messung mit
Playwright (Zeilen, Bildbreiten, Zeichen je Zeile, Kontrast über Canvas aus den oklch-Werten, Fokus per Tab).

## Erster Eindruck (3 Sätze)
Am Handy und am Desktop sieht man sofort eine Nachrichtenseite: ein Aufmacher mit Bild, darunter oder daneben weitere
Geschichten, rote Dachzeilen klein, sonst kühles Weiß, dunkle Tinte und feine Linien. Nichts ist laut, nichts sieht
nach Baukasten aus; die Seite ist eher zurückhaltend als karg. Einzige Stelle, die im ersten Handy-Bildschirm stört:
Bei den Nebenstücken steht die Dachzeile allein unten rechts neben dem kleinen Bild, darüber bleibt ein leeres Feld.

## Harte Kriterien

| # | Kriterium | Handy 390 × 844 | Desktop 1280 × 800 | Ergebnis |
|---|---|---|---|---|
| 1 | Viele Geschichten | 2 Schlagzeilen ganz sichtbar (Aufmacher 369–464 px, „Sri Lanka schafft Visum …“ ab 725 px); alle `h2`/`h3` in Links | 9 ganz sichtbar | erfüllt |
| 2 | Kopf | `<header>` mit Logo und Rubrikzeile, 112 px; Aufmacher ab 369 px (≤ 480) | Kopf 90 px, eine Zeile | erfüllt |
| 3 | Drei Stufen, ≥ 1,25×, ≤ 2 Familien | 28 / 19 / 17 px (Verhältnis 1,47); Gewicht 650 / 650 / 600; nur Libre Franklin | 34 / 22 / 18 px (1,55) | erfüllt (Abstand Nebenstück–Meldung knapp, siehe P2-2) |
| 4 | Größte Schrift, Zeilen, Versalien | 28 px; Aufmacher 3 Zeilen, sonst höchstens 3 (Parai, Kanguva); 0 Versalien > 14 px | 34 px; Aufmacher 3 Zeilen, Meldungen höchstens 3; 0 Versalien | erfüllt |
| 5 | Rot | 0,16 % der Fläche; größte rote Schrift 13 px; kein zweiter Buntton | 0,18 %; 13 px | erfüllt |
| 6 | Keine Effekte | Radius 0, Schatten 0, gedreht 0, Breite nicht verstellt | ebenso | erfüllt |
| 7 | Anreißer ohne Kasten, Icon, Knopf | keine; Trennung nur mit 1-px-Linien; Rubriken als Textzeile ohne Pillen; Fläche nur beim Dienstblock (laut Brief erlaubt) | ebenso | erfüllt |
| 8 | Ein Format Dachzeile/Datum, ≤ 2 Bildformate | „Rubrik │ 17. Juli 2024“, 13 px, Rubrik 600 rot; alle Bilder 16:9 (Logo ausgenommen) | ebenso | erfüllt (Termin mit Wochentag aus den Inhalten, siehe P3) |
| 9 | Kein Bild über natürlicher Breite (2×) | größtes Verhältnis: Aufmacher 390 px bei 1382 px (Grenze 691), Logo 119 bei 300 | Aufmacher 402 / 1382, Logo 150 / 300 (genau an der Grenze), Artikelbild 680 / 1382 | erfüllt |
| 10 | Überlauf, Konsole | 0 px, 0 Fehler (auch 820: 0 px) | 0 px, 0 Fehler | erfüllt |
| 11 | Dienstblock spätestens im 3. Bildschirm | beginnt bei 2392 px (3. Bildschirm endet bei 2532) | – | erfüllt (knapp) |
| 12 | Spanne der Marken | größte Schlagzeile 28 (18–32), Aufmacher ab 369 (332–588), 2 Schlagzeilen (1–3), Radius 0, Schatten 0, Farbanteil 0,2 % | 34 px (18–36); 9 Schlagzeilen und Beginn bei 145 px laut Auftrag gewollt | erfüllt |

## Paarvergleich

**klar neben BBC (Handy, 390):** Das Bild der Nebenstücke ist gleich breit (132 px, BBC ebenfalls etwa 132 px). BBC
setzt die Schlagzeile rechts neben das Bild, beginnend an seiner Oberkante, Zeit und Rubrik darunter; `klar` setzt nur
die Dachzeile neben das Bild an dessen Unterkante und die Schlagzeile darunter über die volle Breite. Dadurch steht
rechts oberhalb jeder Dachzeile ein leeres Feld von etwa 200 × 55 px, und Dachzeile (links bei x = 162) und Schlagzeile
(x = 16) haben keine gemeinsame Kante. Aufmacher: beide Bild über volle Breite, Schlagzeile in drei Zeilen ab etwa
360 px; BBC mit Serife ~30 px, `klar` Grotesk 28 px. Bei BBC sind Nebenstücke größer gesetzt (~22 px) als bei `klar`
(19 px).

**klar neben BBC (Desktop, 1280):** BBCs erster Bildschirm besteht aus zwei Navigationszeilen, einer Anzeige und
„NEWS“; nur eine Schlagzeile ist ganz sichtbar. `klar` zeigt bei einzeiligem Kopf (90 px) neun Schlagzeilen in zwei
Spalten mit Linien zwischen den Anreißern; das entspricht der BBC-Ordnung weiter unten auf der Seite. Der
Aufmacher mit Bild und Text je zur halben Breite wirkt geordnet, das Bild ist 402 px breit, also deutlich kleiner als
BBCs Doppelbild.

**klar neben Tagesschau:** Die Tagesschau hat graue Pillen in der Rubrikzeile, einen blauen Kasten „INTERVIEW“ und eine
blaue Schlagzeile; `klar` hat nichts davon. Bei `klar` stehen die Rubriken als reiner Text, die Dachzeile ist rot,
13 px, die Schlagzeile in Tinte. Die Tagesschau zeigt am Handy nur einen Aufmacher und ein zweites Großbild; bei `klar`
folgen auf den Aufmacher sofort kleine Anreißer, die Seite ist dichter.

**klar neben Runde 2:** Runde 2 hat einen Grund in Creme, Rubriken als Pillen, abgerundete Bildecken, einen cremefarbenen
Anzeigenkasten mit rotem Knopf und am Desktop bunte Punkte vor den Rubriken. `klar` hat einen kühlen weißen Grund, Rubriken
als Text, Bildecken mit 0 px, keine Punkte und 1-px-Linien statt Flächen. Im ersten Handy-Bildschirm zeigt Runde 2 keine
einzige Schlagzeile, `klar` zeigt zwei.

**klar neben Runde 4 (Raster):** Runde 4 hat ein rotes Titelwort von etwa 335 px, schmale Schnitte, Versalien in der
Navigation, rote Rahmenlinien und eine feste Leiste unten. Bei `klar` ist die größte Schrift 34 px in normaler
Breite, es gibt keine Versalien, 0,2 % Rot und keine feste Leiste.

Zu den Punkten aus Runde 4: zu viel Rot, zu laut: nein (0,2 %, 34 px). Baukasten: nein (keine Kästen, Pillen, Icons,
Knöpfe, Schatten oder Rundungen). Schrift: eine Familie in normaler Breite; Satz bis auf P2-3 ruhig. Nicht hochwertig:
ein Befund im ersten Handy-Bildschirm (P1-1), ansonsten gleiche Bildformate und Kanten. Alt oder langweilig: kein
Creme, keine runden Bilder, keine bunten Punkte, kein Mosaik.

## Befunde

### P0
keine.

### P1
1. **Nebenstück am Handy: Dachzeile ohne gemeinsame Kante, leeres Feld neben dem Bild** (390, `.stueck`, schon das
   erste Nebenstück im ersten Bildschirm bei 725 px, dazu alle drei weiteren). Das Raster stellt die Dachzeile in
   Spalte 2 an die Unterkante des 132 × 74-px-Bildes (`.stueck .meta { align-self: end }`), die Schlagzeile in die
   Zeile darunter über beide Spalten. Ergebnis: Die Dachzeile liest sich wie eine Bildzeile, beginnt bei x = 162 statt
   an der linken Kante von Schlagzeile und Seite (x = 16), und rechts über ihr bleibt ein leeres Feld von etwa
   200 × 55 px. Auf der übrigen Seite stehen Dachzeile und Schlagzeile immer an derselben linken Kante. Bei BBC steht der
   Text rechts neben dem Bild ab seiner Oberkante.
   *Behebung:* das BBC-Muster übernehmen: Bild links (132 px), rechts daneben ab der Oberkante Dachzeile und Schlagzeile
   (19 px, höchstens vier Zeilen bei rund 200 px Breite, längster Titel prüfen), oder alternativ Dachzeile und
   Schlagzeile gemeinsam unter das Bild, links bündig. Danach die Zeilenzahl der vier Titel neu messen.

### P2
1. **Desktop: rechte Spalte endet 300 px vor der linken** (1280, `.meldungen` neben `.neben`). Die sechs Meldungen
   enden bei etwa 775 px, die Nebenstücke bei etwa 1070 px; dazwischen steht rechts eine leere Fläche von
   320 × 300 px, gleich unter dem ersten Bildschirm. *Behebung:* Nebenstücke am Desktop knapper setzen (Vorspann auf
   höchstens zwei Zeilen) oder unter den Meldungen ein weiteres echtes Element einplanen, sobald Inhalte dafür da sind
   (in der Skizze nichts erfinden); alternativ die Meldungsspalte nur neben dem Aufmacher führen und die Nebenstücke
   darunter über die ganze Breite in zwei Spalten.
2. **Nebenstück und Meldung am Handy kaum unterscheidbar** (390, `.stueck .titel` 19 px/650 gegen `.meldung .titel`
   17 px/600; Küche ebenfalls 19 px). Ohne das Bild trennen die beiden Stufen 2 px und 50 Gewichtseinheiten; im zweiten
   Handy-Bildschirm wirken „Kanguva …“ und „Von Deutschland nach Tamil Nadu …“ fast gleich. Brief verlangt einen
   sichtbaren Unterschied; formal erfüllt, im Bild schwach. *Behebung:* Nebenstück auf 20–21 px oder Meldung auf 400–500
   Gewicht.
3. **Zeilenfall in Schlagzeilen** (390: „Kanguva – Ein tamilisches / Kino-Highlight ab 14. / November in Deutschland“
   trennt Zahl und Monat; „Meet Tamil Singles – Ein neues Dating- / Event …“ bricht am Bindestrich; 1280: „Kino- /
   Highlight“). *Behebung:* geschütztes Leerzeichen in „14.&nbsp;November“, geschützter Bindestrich (U+2011) in
   „Dating‑Event“ und „Kino‑Highlight“; in der Umsetzung als Regel für Datumsangaben und Bindestrichwörter in Titeln.
4. **Dienstblock am Desktop: Titel ohne gemeinsame Oberkante** (1280, `.woche`). „Scene“ und „Ramayana“ beginnen bei
   1573 px, „Diwali in Basel“ bei 1597 px, weil nur der Termin eine Datumszeile darüber hat; die Spaltenmarke „Im Kino“
   steht nur über der ersten der zwei Kinospalten, über der zweiten ist der Platz leer. Am Handy fällt das nicht auf.
   *Behebung:* beim Termin das Datum unter den Titel setzen (wie Zahl und Orte bei den Filmen) oder bei den Filmen eine
   gleich hohe Zeile darüber (etwa „im Kino seit …“, nur wenn die Angabe im Radar vorliegt); „Im Kino“ als Marke über
   beide Kinospalten führen.

### P3
- Nebenstücke am Handy ohne Vorspann (390). Nach Auftrag zulässig, BBC verfährt ebenso; der Leser bekommt aber nur die
  Schlagzeile.
- Termin „Samstag, 21. November 2026“ mit Wochentag und ohne Dachzeile weicht vom Format „Rubrik │ 17. Juli 2024“ ab;
  der Wortlaut ist in `inhalte.json` so vorgegeben, für Termine ist der Wochentag sinnvoll. In DESIGN.md als eigene,
  bewusste Form festhalten.
- Dienstblock am Handy beginnt bei 2392 px, nur 140 px vor dem Ende des dritten Bildschirms; der Termin liegt im
  vierten (2783 px). Wird die Seite länger (Werbeplatz, mehr Nebenstücke), fällt Kriterium 11.
- Logo am Handy 119 px breit, Unterzeile unlesbar (bekannt, Brief Abschnitt 9).

### Leser und Inhalte (D)
- 65-Jähriger am Handy: Vorspann 17 px, Fließtext im Artikel 18 px bei 38 Zeichen je Zeile, Zeilenabstand 1,6;
  Kontrast Tinte 16,9:1, Leise 7,1:1, Rot 6,1:1 auf Grund (auf der Fläche des Dienstblocks 15,9 / 6,7 / 5,7); Dachzeile
  und Datum 13 px sind klein, aber in der Spanne des Briefs. Tippflächen: alle ≥ 44 px (Rubriken 44 px hoch, ganze
  Anreißer als Link, „Per WhatsApp teilen“ 44 px). Fokus: 2-px-Rahmen in Tinte, auf Rubriken und ganzen Anreißern
  sichtbar.
- 19-Jährige in fünf Sekunden: Aufmacher mit großem Bild und drei Zeilen Schlagzeile ist eindeutig, danach eine
  gleichmäßige Liste.
- Inhalte: Rubriken, Aufmacher, vier Nebenstücke, sechs Meldungen, vier Küchenbeiträge, zwei Filme und ein Termin in
  genau der Reihenfolge von `inhalte.json`; Titel unverändert (auch „Das ursprüngliche Musik“ wie im Bestand);
  Vorspänne an Satzenden gekürzt; nichts erfunden. Küche ohne Dachzeile (zulässig). Artikel: Kopf mit Dachzeile,
  Datum, Schlagzeile, Vorspann (bis „stattfand.“), Lesezeit, WhatsApp-Link, Bild, dann genau die drei Absätze
  unverändert; keine Autorenzeile, kein Bildnachweis. Aktive Rubrik „Nachrichten“ im Artikel rot.
- Artikel Desktop: Titel 36 px in 2 Zeilen, Fließtext 19 px, 58 Zeichen je Zeile; Vorspann 44–60 Zeichen je Zeile auf
  der Startseite (≤ 70).

### Technik (E)
`bericht.json`: 6 Aufnahmen, Überlauf 0, Konsole leer, keine leeren Bilder, alle Schriften geladen, keine Tippfläche
unter 44 px, kein Tamil ohne `lang`. `prefers-reduced-motion` ist gesetzt.

## Was trägt
- Die Ordnung am Desktop: Aufmacher mit Bild und Text je zur halben Breite, Nebenstücke mit 16:9-Bild links, rechts
  eine Meldungsliste mit 1-px-Linien; eine einzige Bildform auf der ganzen Seite.
- Die Farbdisziplin: 0,2 % Rot, nur in Dachzeilen und Marken; kühles Weiß; Fläche nur beim Dienstblock.
- Ein einheitliches Format für Dachzeile und Datum („Rubrik │ Datum“, 13 px) über alle Anreißer.

## Bedienbarkeit (nur zur Information)

| Heuristik | Punkte | Satz |
|---|---|---|
| 1 Sichtbarkeit des Zustands | 3 | Aktive Rubrik im Artikel rot; auf der Startseite ist keine Rubrik markiert. |
| 2 Bezug zur Welt | 4 | Deutsche Rubriknamen, Datum ausgeschrieben, „2 Min. Lesezeit“. |
| 3 Kontrolle und Freiheit | 3 | Logo führt zur Startseite; die Rubrikzeile am Handy zeigt das Weiterwischen nur durch das abgeschnittene „Commun“. |
| 4 Einheitlichkeit | 3 | Ein Format für Meta und Bild; Ausnahme Nebenstück am Handy und Termin im Dienstblock. |
| 5 Fehler vermeiden | 4 | Ganze Anreißer als Tippziel, keine kleinen Ziele. |
| 6 Erkennen statt Erinnern | 4 | Rubrik an jedem Anreißer. |
| 7 Flexibilität | 2 | Keine Suche, kein Menü für alle Rubriken am Handy (Skizze). |
| 8 Ästhetik, Reduktion | 4 | Keine Zierelemente. |
| 9 Fehlermeldungen | – | In der Skizze nicht vorhanden. |
| 10 Hilfe | – | In der Skizze nicht vorhanden. |
