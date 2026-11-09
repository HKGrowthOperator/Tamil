# News-Marken: vermessene Startseiten

Stand 09.11.2026. Sechs Startseiten, je bei 390 × 844 (Faktor 2, Bildschirm 1 und 2) und 1280 × 800 (Bildschirm 1),
Chromium über Playwright, deutsche Spracheinstellung. Die Seiten wurden vom Skript und von Hand geprüft; Werte, die von
Hand korrigiert wurden, sind mit „(Hand)“ markiert. Bilder: `design/referenzen/img/news-<kurzname>-handy-1.jpg`,
`-handy-2.jpg`, `-desktop-1.jpg`.

## Was nicht ging, und Ersatz

- **zeit.de**: antwortet aus dieser Umgebung mit der Fehlerseite „Da ist etwas schiefgelaufen“ (zwei Versuche). Ersatz
  derselben Familie: **sueddeutsche.de**. Es gibt keine Zeit-Messwerte. Zeit gilt hier nur als „elegant“ nach Vorwissen
  des Projektleiters, nicht als gemessen.
- **Zustimmungsdialoge**: Spiegel, NZZ und SZ wurden per Klick auf „Einwilligen und weiter“, „Alle Anbieter
  akzeptieren“ bzw. „Ich bin einverstanden“ geschlossen. Beim **Guardian** (US-Variante „Your privacy“) ließ sich der
  Dialog nicht anklicken; er wurde per CSS ausgeblendet. Beim **NZZ-Desktop** wurde der Dialog nach dem Klick per Skript
  entfernt, beim **Spiegel-Desktop** das Abo-Fenster (Layer). Die Seitenbilder zeigen sonst den echten Zustand.
- **Störer im Bild**, die Zahlen verzerren: tagesschau-Handy hat unten eine blaue App-Leiste (#002db4, etwa 4 % der
  Fläche); BBC-Desktop eine Abo-Leiste unten und eine Anzeige oben; Spiegel- und SZ-Desktop zeigen im ersten
  Bildschirm eine große Anzeige (Telekom, rosa/schwarz) und Seitenwerbung; Spiegel-Handy-2 und SZ-Handy-2 zeigen eine
  Anzeige. Die Anzeigen sind in den Farbanteilen enthalten.

## Übersichtstabelle

| Marke | Familie | Kopfhöhe Handy (px) | größte Schlagzeile Handy / Desktop | Schlagzeilen im 1. Schirm Handy / Desktop | Farbanteil ohne Bilder Handy / Desktop | Radius | Kästen |
|---|---|---|---|---|---|---|---|
| tagesschau | nüchtern | 351 | 32 px, Gew. 350, Thesis / 34 px, 350, Thesis | 1 / 1 | 7,5 % (davon ca. 4 % App-Leiste) / 0,4 % | 0 | nein |
| BBC News | nüchtern | 424 | 24 px, 500, BBC Reith Serif / 28 px, 500 | 2 / 2 | 0,0 % / 1,2 % | 0 | nein (Linien) |
| Guardian | Qualitätsblatt | 588 | 28 px, 500, GH Guardian Headline / 28 px, 500 | 3 / 4 (Hand) | 26,2 % / 28,6 % (Marinenblau #052962 im Kopf) | 0; 100 nur Rundbilder im Meinungsstreifen | teilweise (graue Unterliste, farbige Meinungskarten) |
| NZZ | Qualitätsblatt | 391 | 18 px, 500, NZZ Serif / 18 px, 500 (Aufmacher-Titel unter dem Bildschirm, Seite: 28 px) | 1 / 1 | 0,0 % / 1,0 % | 0 | nein (Linien) |
| Spiegel | bildstark | 561 | 28 px, 800, SpiegelSlabCdUI / 36 px, 800 (nur angeschnitten) | 2 / 3 (Eilleiste) | 6,2 % (orange Kopfleiste) / 12,3 % (mit Anzeige) | 1,5 | Desktop: weiße Fläche auf Grau; Handy nein |
| SZ (Ersatz für Zeit) | elegant (Ersatz) | 332 | 27 px, 800, SZSansDigital / 31 px, 800 (Titel ab 1102 px, unter dem Bildschirm) | 2 / 0 (Anzeige füllt Schirm) | 0,0 % / 4,8 % (Anzeige) | 0 | Handy: weiße Karte auf Grau über dem Bild |

Kopfhöhe = Pixel von oben bis zur Oberkante der Schlagzeile des Aufmachers (nicht des Bildes). Bei BBC, Guardian,
NZZ, Spiegel, SZ steht das Aufmacher-Bild über der Schlagzeile (BBC Bild ab 115 px, NZZ ab 136 px, SZ ab 120 px,
Spiegel ab 251 px) oder neben ihr. Kopfhöhe Desktop: tagesschau 610, BBC 572, Guardian 451, NZZ Aufmacher-Titel unter
dem Schirm (Bild ab 278; rechter Anreißer 546), Spiegel 716, SZ 1102.

### Spanne der Marken

| Messwert | kleinster Wert | größter Wert |
|---|---|---|
| Kopfhöhe Handy (bis Schlagzeile) | 332 px (SZ) | 588 px (Guardian) |
| Kopfhöhe Desktop | 451 px (Guardian) | 1102 px (SZ; mit Anzeige) |
| größte Schlagzeile Handy | 18 px (NZZ) | 32 px (tagesschau) |
| größte Schlagzeile Desktop | 18 px (NZZ, sichtbar) | 36 px (Spiegel) |
| Gewicht der größten Schlagzeile | 350 (tagesschau) | 800 (Spiegel, SZ) |
| Schlagzeilen im 1. Schirm Handy | 1 (tagesschau, NZZ) | 3 (Guardian) |
| Schlagzeilen im 1. Schirm Desktop | 0 (SZ) | 4 (Guardian) |
| Farbanteil ohne Bilder Handy | 0,0 % (BBC, NZZ, SZ) | 26,2 % (Guardian, Marinenblau); ohne Guardian 7,5 % |
| Farbanteil ohne Bilder Desktop | 0,4 % (tagesschau) | 28,6 % (Guardian); ohne Guardian 12,3 % (Spiegel, Anzeige) |
| Farbanteil mit Bildern Handy | 2,4 % (SZ) | 32,8 % (Guardian) |
| Größter Radius an Bildern/Anreißern | 0 | 1,5 px (Spiegel); 100 % nur Guardian-Rundbilder |
| Schatten an Anreißern | 0 | 0 (keine Marke, nach Skript) |
| Bildformate im 1. und 2. Schirm | 1 (BBC, NZZ, Guardian; 16:9, 3:2, 5:4) | 3 (tagesschau 16:9, 1:1, 2,29; SZ 16:9, 3:4, Desktop mehr) |

## Je Marke

### tagesschau (nüchtern) · `https://www.tagesschau.de/`

Bilder: `img/news-tagesschau-handy-1.jpg`, `img/news-tagesschau-handy-2.jpg`, `img/news-tagesschau-desktop-1.jpg`

- Was sie wertig macht: ein Aufmacher mit 16:9-Bild bis an den Rand, darunter Plakette (Dachzeile) und eine einzige
  große Schlagzeile (32 px, Gewicht 350, blau #015999); Rest ist Weißraum, Anreißer ohne Kästen.
- Leichtes Gewicht statt Fett: die Schlagzeile steht in Thesis 350, der Anreißertext in 18 px Thesis, Textfarbe #33322f
  (kein Schwarz). Hierarchie entsteht aus Größe und Abstand, nicht aus Gewicht.
- Farbe nur als Blau (#015999) für Plakette, Schlagzeile, „mehr“-Link; Seite ohne Bilder 0,4 % (Desktop). Anreißer in
  Bildschirm 2: Bild links 1:1, Text rechts; Handy-Kopf 104 px mit Logo, „Sendung verpasst?“ und Menü.
- Dachzeile ja (Plakette wie „INTERVIEW“, „FAQ“ plus graue Zeile), Zeitangabe im ersten Bildschirm nein.
  Seitenhintergrund #ffffff, Desktop-Rand #f1f1f1, Text #33322f.

### BBC News (nüchtern) · `https://www.bbc.com/news`

Bilder: `img/news-bbc-handy-1.jpg`, `img/news-bbc-handy-2.jpg`, `img/news-bbc-desktop-1.jpg`

- Was sie wertig macht: jede Schlagzeile hat dieselbe Meta-Zeile „Zeit | Rubrik“ (z. B. „42 mins ago | US & Canada“),
  grau, mit senkrechtem Strich; das erzeugt Ruhe und Wiedererkennung.
- Anreißer sind nur durch eine dünne graue Linie und Abstand getrennt, ohne Kästen, ohne Schatten, ohne Radius an
  Bildern. Alle Bilder 16:9 (ein einziges Format, 6 von 6 im Bildschirm 1 und 2).
- Farbe fast nur im Wort „NEWS“ (#b80000, Vektorgrafik) und im Logo (Schwarz); Schlagzeilen in Serife (Reith Serif,
  Gewicht 500, 24 px Aufmacher, 18 px sonst), Textfarbe #202224, Grund #ffffff.
- Dachzeile: Rubrik in der Meta-Zeile unter dem Titel; Zeit bei jedem Anreißer.

### Guardian (Qualitätsblatt) · `https://www.theguardian.com/international`

Bilder: `img/news-guardian-handy-1.jpg`, `img/news-guardian-handy-2.jpg`, `img/news-guardian-desktop-1.jpg`
(Datenschutzdialog per CSS ausgeblendet.)

- Was sie wertig macht: Serifenschlagzeilen (GH Guardian Headline, Gewicht 500, 28 px Aufmacher) über sehr großer
  Fläche, Aufmacher mit roter Dachzeile (#c70000, z. B. „Nvidia“) und grauer Zeitangabe „3h ago“.
- Eine einzige Fläche trägt die Marke: Marinenblau #052962 im Kopf (26 % des Bildschirms); Rot nur als Dachzeile in
  Textfarbe, Gelb (#ffe500) nur für einen Knopf. Seite #ffffff, Text #121212.
- Unterlisten stehen auf hellgrauem Kasten mit kurzer grauer Linie über jedem Eintrag; Rundbilder (100 %) nur im
  Meinungsstreifen oben. Das Bildformat der Aufmacher ist 5:4 (1,25), ein Format.
- Handy-Kopf bis Schlagzeile 588 px: Spendenleiste, Meinungsstreifen, Logo, Reiter, Unterreiter, Edition-Hinweis.

### NZZ (Qualitätsblatt) · `https://www.nzz.ch/`

Bilder: `img/news-nzz-handy-1.jpg`, `img/news-nzz-handy-2.jpg`, `img/news-nzz-desktop-1.jpg`
(Desktop: Dialog nach Klick entfernt.)

- Was sie wertig macht: kein Farbanteil im Seitenkörper (0,0 % Handy), Serife (NZZ Serif, Gewicht 500, 18 px) für
  Titel und Sans in Grau für den Lead; nur eine zarte Linie zwischen den Anreißern.
- Bilder 3:2 ohne Radius, bis an die Textspalte (Handy 358 px breit mit 16 px Rand). Ein Format für alle Anreißer.
- Meta-Zeile ohne Rubrik: Autor · „vor 2 Stunden“ · Lesedauer „4 min“ · Merkzeichen. Dachzeile nur selten
  (blaue Versalien „DIE NEUESTEN ENTWICKLUNGEN“, ca. #262ba8). Das Logo ist Schwarz, Kopf 136 px mit Reiter-Leiste.
- Grund #ffffff, Text #121212; die Schlagzeile ist nicht groß, die Wirkung kommt aus Bildgröße und Weißraum.

### Spiegel (bildstark) · `https://www.spiegel.de/`

Bilder: `img/news-spiegel-handy-1.jpg`, `img/news-spiegel-handy-2.jpg`, `img/news-spiegel-desktop-1.jpg`
(Zustimmung per Klick; Desktop-Abofenster ausgeblendet.)

- Was sie wertig macht: Kopfleiste in einem Orange (#e64415) mit weißem Slab-Logo; derselbe Ton erscheint als
  Dachzeile über dem Aufmacher und als Plus-Zeichen. Sonst Schwarz auf Weiß (#000000, Grund #ffffff, Desktop-Fläche
  #f1efed).
- Schlagzeile sehr fett in Condensed-Slab (SpiegelSlabCdUI 800, 28 px Handy, 36 px Desktop), Anreißertext 16 px
  Sans; Aufmacher-Bild füllt die ganze Breite (4:3 Handy, 3:2 Desktop), Radius 1,5 px.
- Oben eine Eilleiste mit drei Schlagzeilen und Zeitangabe („Vor 1 Stunde“). Anreißer in Bildschirm 2: kleines Bild
  rechts (4:3), Titel links, Lesedauer „1 Min“, Merkzeichen. Ohne Bilder 6,2 % Farbe (nur die Kopfleiste).
- Zeitangabe nur in der Eilleiste, sonst Lesedauer; Dachzeile nur beim Aufmacher als eigene Zeile.

### Süddeutsche Zeitung (Ersatz für Zeit, elegant) · `https://www.sueddeutsche.de/`

Bilder: `img/news-sz-handy-1.jpg`, `img/news-sz-handy-2.jpg`, `img/news-sz-desktop-1.jpg`
(Zustimmung per Klick.) Nicht mit Zeit gleichzusetzen.

- Was sie wertig macht: Wortmarke in Antiqua-Schrift auf Weiß (Kopf 80 px dunkles Band darüber, #29293a), Grund
  #ffffff, Textfarbe #29293a (Blauschwarz, kein Schwarz).
- Handy: 16:9-Bild, darüber legt sich eine weiße Karte (Überlapp, Radius 0) mit Schlagzeile 27 px Gewicht 800 und
  Lead 17 px, Autorenzeile mit SZ-Plus-Marke (Türkis #69c1b8 nur als Link-/Linienfarbe).
- Wenig Farbe (0,0 % ohne Bilder auf dem Handy); Hierarchie über Gewicht (800/400) und Abstand. Im Desktop-Bild
  dominiert eine Anzeige, die Schlagzeile des Aufmachers beginnt erst bei 1102 px.
- Dachzeile nein, Zeit nein; Autor/Autorinnen mit Plus-Marke und Merkzeichen.

## Gemeinsamkeiten

- Weißer Grund (#ffffff), Text dunkel aber nicht reinschwarz außer Spiegel/BBC-Meta (#121212, #202224, #29293a, #33322f).
- Schlagzeile des Aufmachers 18 bis 36 px, in einer eigenen Schrift der Marke, nie in einer Systemschrift.
- Ein großes Aufmacher-Bild, Rest durch Linien oder Abstand getrennt; kein Schatten an Anreißern (Skript), Radius 0
  bis 1,5 px (Ausnahme: Guardian-Rundbilder im Meinungsstreifen).
- Farbe sitzt an wenigen festen Orten: eine Markenfarbe für Kopf, Dachzeile oder Links (Blau, Rot, Marine, Orange),
  Seite ohne Bilder höchstens 0 bis 1 % (außer Guardian-Kopf, Spiegel-Kopfleiste).
- Schlagzeile mit gemischter Groß-/Kleinschreibung, keine Versalien in Schlagzeilen (Versalien nur in Plaketten und
  Dachzeilen, tagesschau, NZZ).
- Meta unter oder über dem Titel (Zeit, Rubrik, Autor, Lesedauer) in Grau und kleiner als der Titel.
- Wenige Bildformate (1 bis 3); der Aufmacher ist breiter als die Anreißer.
- Zustimmungsfenster, Abo- und App-Banner, Anzeigen belegen sehr viel vom ersten Bildschirm.

## Unterschiede der Familien

- **nüchtern** (tagesschau, BBC): helle, kleinere Schlagzeilen (tagesschau Gewicht 350), jedes Element mit festem Platz;
  BBC mit Zeit und Rubrik an jedem Anreißer, tagesschau mit Plakette als Dachzeile.
- **Qualitätsblatt** (Guardian, NZZ): Serife in Schlagzeilen, weniger Bild je Schirm. Guardian mit einer
  großen Farbfläche (Marine) im Kopf und roter Dachzeile; NZZ ohne Farbe, Titel nur 18 px.
- **bildstark** (Spiegel): sehr fette Slab-Schlagzeile (800), Bild über die ganze Breite, orange Kopfleiste als Farbfläche.
- **elegant** (SZ, als Ersatz; Zeit nicht messbar): Antiqua-Wortmarke, Sans-Schlagzeile 800/27 px auf weißer Karte,
  Blauschwarz statt Schwarz.

## Messverfahren und Grenzen

- Skript: `/tmp/claude-0/-home-user/328bcd38-019d-5546-955b-7fea86a20fa1/scratchpad/news-marken/` (`messen.mjs`,
  `messen2.mjs`, `messen3.mjs`, `messen4.mjs`, `farbe.py`, Rohdaten in `raw/`).
- Farbanteil: Pixel mit HSV-Sättigung > 0,35 und Helligkeit > 0,2 im Bildschirmfoto; „ohne Bilder“ mit
  `img, picture, video, svg, [style*="background-image"] { visibility: hidden }`. Dunkle Marinen- und Blautöne zählen
  (Guardian). Der rote BBC-Schriftzug „NEWS“ ist eine Vektorgrafik und fällt in „ohne Bilder“ heraus.
- „Schlagzeilen im ersten Bildschirm“ wurde von Hand nachgezählt, weil das Skript Navigation und kleine
  Unterelemente falsch einordnete (tagesschau: 10 px für Inneres der Überschrift; SZ: Seitentitel als Schlagzeile).
  Schlagzeilengrößen, Gewicht und Schrift wurden danach gezielt am Aufmacher gemessen (Hand).
- tagesschau: die drei häufigsten Schlagzeilenstufen waren nicht sauber messbar (Gewicht 350 liegt unter dem Filter);
  Aufmacher 32/34 px (gemessen), Anreißer im Bild etwa 24 px, Dachzeilen 16 px (Skript).
- Häufigste Stufen der Seite (Zahl der Treffer in Klammern, Titel mit Gewicht ≥ 500 und ≥ 16 px, inklusive Links der
  Rubrikleisten): BBC 18 (26), 16 (15), 24/28 (4); Guardian Handy 17 (75), 24 (14), 16 (7), Desktop 17 (63), 20 (58),
  24 (15); NZZ Handy 16 (71), 18 (41), 22 (2), Desktop 18 (83), 16 (17), 28 (13); Spiegel Handy 18 (78), 20 (53),
  16 (41), Desktop 18 (90), 20 (52), 16 (28); SZ Handy 17 (60), 19 (51), 21 (42), Desktop 17 (143), 27 (19), 19 (13).
- Fließ-/Anreißertext: tagesschau 18 px Thesis; BBC 14 px BBC Reith Serif (Skript); Guardian Meta 14 px
  GuardianTextSans, Unterlisten ca. 17 px Serife; NZZ Meta 14 px NZZ Sans, Lead in Sans (Größe nicht sauber gemessen,
  nach Bild ca. 17 bis 18 px); Spiegel 16 px SpiegelSansUI; SZ 17 px SZSansDigital.
- Schatten und Kästen stammen aus dem Skript (Anreißer und Karten im ersten Bildschirm, ohne Kopfleisten) und wurden
  am Bild geprüft; Spiegel-Desktop und SZ-Handy zeigen weiße Flächen auf Grau.
- Bildformate (Breite : Höhe, 2 Stellen, Bildschirm 1 und 2): tagesschau 1,78 / 1,00 / 1,75 (Desktop zusätzlich
  2,29); BBC 1,78; Guardian 1,25; NZZ 1,50; Spiegel 1,33 (Desktop 1,50); SZ 1,78 und 0,75.
