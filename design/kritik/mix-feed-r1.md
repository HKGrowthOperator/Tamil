# Prüfung mix-feed, Runde 1
Harte Kriterien: 14 von 16 erfüllt · P0: 0 · P1: 6 · P2: 9 · P3: 4

Maßstab: Brief 10.4 (16 Kriterien) mit den Kennzahlen aus `node design/vergleich/aufnahmen.mjs mix-feed`
(`design/vergleich/kennzahlen/mix-feed.json`, Stand 12.11.2026 15:29), Technik aus `tools/shots.mjs` (8 Seiten × 390/820/1280,
24 Aufnahmen, 0 Fehler), dazu eigene Messungen im Browser (Tippflächen, Zeilenlänge, Bildformate, Nachweise, Tastatur,
320 px). Geprüft: index, artikel, rubrik, termine, suche, kontakt, Stichproben artikel-37 und artikel-80.
Rohdaten und Aufnahmen: `/tmp/claude-0/-home-user/328bcd38-019d-5546-955b-7fea86a20fa1/scratchpad/kritik-feed/`
(`mess.json`, `shots/bericht.json`, Vergleichstafeln `m-*.jpg`). `begruendung.md` nicht gelesen.

## Erster Eindruck (3 Sätze)

Am Handy füllt ein hochformatiges Tempelfoto (390 × 508 px) gut 60 % des ersten Bildschirms, die Schlagzeile steht
weiß im Bild, darunter eine Meldung mit kleinem Bild: ruhig, sauber, klar bildstärker als das Live-Design und nicht
laut. Kopf, Schrift, Rubrikband und Aufmacher sind aber fast deckungsgleich mit `klar2` und `mix-ordnung`; das
Eigene von „Feed“ (Hochformate, Wischstreifen, Titel im Bild) zeigt sich erst ab dem zweiten Bildschirm.
Die Mängel liegen in der Ordnung, nicht in der Lautstärke: zu viele Bildformate, zu lange Zeilen im Artikel am
Desktop, eine verrutschte Kante im Kopf, eine Reihe gleicher Kacheln in „Diese Woche“.

## Harte Kriterien (Brief 10.4)

| # | Kriterium | Handy (390 × 844) | Desktop (1280 × 800) | Ergebnis |
|---|---|---|---|---|
| 1 | Viele Geschichten, h2/h3 mit Link | 2 ganz sichtbar (Aufmacher + „Bundestagsdrucksache“) | 4 | erfüllt |
| 2 | Kopf ≤ 152 px; Aufmacher-Schlagzeile ab ≤ 480 px | Kopf 149 px; **Schlagzeile ab 534 px** | Kopf 167 px; ab 346 px | **verletzt** (Handy) |
| 3 | Drei Stufen, Aufmacher ≥ 1,25 × Nebenstück; ≤ 2 Familien | 30 / 22 / 19–20 px (1,36 ×); nur Libre Franklin | 40 / 22–24 / 19 px (1,67 ×) | erfüllt |
| 4 | Größte Schrift ≤ 34/44 und = Aufmacher; zweitgrößte ≤ 24/28; Aufmacher ≤ 3 Zeilen, andere ≤ 4; keine Versalien > 14 px | 30 px Aufmacher; zweitgrößte 24 px („Diese Woche“); 3 Zeilen; max. 4; Versalien 13 px | 40 px; zweitgrößte 26 px; 2 Zeilen; max. 4; 0 | erfüllt |
| 5 | Rot ≤ 3 %, keine rote Schrift > 20 px, kein zweiter Buntton | 0,08 %; größte rote 13 px; bunt = rot | 0,06 %; 13 px | erfüllt |
| 6 | Genau zwei dunkle Flächen; ≤ 12 % dunkel im ersten Bildschirm | nav.band + section#diese-woche; 6,2 % | dieselben; 5,8 % | erfüllt (siehe P2-7 zum Eindruck am Handy) |
| 7 | Keine Effekte, Verlauf nur unter Schrift im Bild | Radius 0, Schatten 0, gedreht 0, Breite normal | dito | erfüllt |
| 8 | Kein Baukasten (Kasten, Icon, Knopf, Pillen) | keine; gestaltete Kacheln auf „Fläche auf Dunkel“ | keine | erfüllt (Kartenreihe siehe P1-4) |
| 9 | Kein Anreißer ohne Bild; Grafik-Kacheln ≤ 3 | Kennzahl: 18 Anreißer, 0 ohne Bild, 0 Grafik; **von Hand:** 2 Grafik-Kacheln („Scene“, „Ramayana“, als `h4` nicht gezählt) + 2 Termine ohne Bild (`h4`) | dito | erfüllt in der Zählung des Briefs (2 ≤ 3), Lücke siehe P2-6 |
| 10 | Ein Format für Dachzeile/Datum; ≤ 3 Bildformate | Dachzeile einheitlich „Rubrik \| Datum“; **5 Bildformate** (0,77 · 0,80 · 0,67 · 1,33 · 1,50) | **9 Bildformate** (1,50 · 1,33 · 1,60 · 0,67 · 0,99 · 1,03 · 0,73 · 0,55 · 0,80) | **verletzt** |
| 11 | Bildgröße | über Dateibreite: keins; über halber Dateibreite: keins | nur Aufmacher rb-30 (803 von 1280 px), erlaubt | erfüllt |
| 12 | Helle Schrift ≥ 4,5 : 1 an der hellsten Stelle | 52 Stellen, kleinster Wert 5,11 | 83 Stellen, 5,36 | erfüllt |
| 13 | Bewegung | Maßstab 1,03; längster Übergang 0,35 s; 0 Animationen; reduziert: 0 Übergänge; fest nur nav.band 48 px (sticky) | dito; Zoom beim Überfahren nachgemessen: matrix(1.03) | erfüllt |
| 14 | Kein Überlauf 390/820/1280, keine Konsolenfehler | 0 px, 0 Fehler (alle 8 Seiten) | 0 px, 0 Fehler | erfüllt |
| 15 | „Diese Woche“ spätestens im dritten Handy-Bildschirm | Oberkante 1818 px (≤ 2532) | – | erfüllt |
| 16 | Paarvergleich | keine weiteren Werte außerhalb der Grenzen; Abweichungen unter 2 und 10 gezählt | | erfüllt |

## Paarvergleich

**Gegen das Live-Design (Runde 2, `r2-heute-*`)**
- Grund: Live warmes Creme mit gerundeten Sandkarten; mix-feed kühles Weiß, Radius 0, keine Karte um Anreißer.
- Aufmacher: Live eine blasse Grafikkarte ohne Foto mit Ornamentlinie, darüber ein Anzeigenkasten; mix-feed ein
  randloses Foto über 390 × 508 px mit weißer Schlagzeile auf Tintenverlauf.
- Navigation: Live Pillenreihe auf Weiß; mix-feed dunkles Band mit 16-px-Rubriken ohne Pillen.
- Ergebnis: deutlich bildstärker und weniger klassisch, an beobachtbaren Punkten (Grundfarbe, Rundungen, Foto statt
  Grafik, Anzeigenkasten weg).

**Gegen `klar2`**
- Kopf identisch: Datumszeile, Logo, dunkles Rubrikband 48 px, Libre Franklin, gleiche Dachzeile „Rubrik | Datum“.
- Unterschied ist das Bildmaß: Aufmacher am Handy 508 px hoch im Hochformat statt rund 260 px im Querformat, am
  Desktop 803 × 535 px; dazu mehr Titel im Bild (Aufmacher, INAIVU, Community 5/5, Küche 4/4, Koovagam).
- Darunter Wischstreifen und Hochformate (4:5, 2:3) statt Rubrikkacheln und Querformaten. Wirkung: `klar2` mit mehr
  Bild, keine neue Ordnung.

**Gegen `mix-ordnung` (Schwester)**
- Erster Bildschirm Handy: gleicher Kopf, gleiches Foto, gleiche Dachzeile, gleiche Schlagzeile an fast gleicher
  Stelle. mix-ordnung zeigt danach Vorspann und ein zweites großes Bild (Koovagam); mix-feed danach eine Meldung mit
  100-px-Bild. Unterhalb des Aufmachers ist also gerade die „Ordnung“-Variante die bildstärkere.
- Erster Bildschirm Desktop: beide großer Aufmacher links, rechte Spalte mit einem Bildanreißer und Meldungen mit
  kleinen Bildern. Unterschied: mix-feed hat rechts oben den Titel im Bild (INAIVU), mix-ordnung darunter.
- Erkennbar anders erst ab Bildschirm 2–3: mix-feed mit Wischstreifen (Kino, Community, Küche), Hochformaten und
  Grafik-Kacheln, mix-ordnung mit untereinander gestapelten Kino-Bildkacheln und Meldungsliste. → P1-5.

**Gegen Vorbilder (BBC Handy, Guardian und BBC Desktop)**
- BBC Handy: zwei Querformate nebeneinander (rund 30 % der Bildschirmhöhe), Serifen-Schlagzeile schwarz auf Weiß,
  Vorspann, feine Linie. mix-feed: ein Bild über rund 60 %, Schlagzeile im Bild, kein Vorspann im ersten Bildschirm.
  Mehr Bildgewicht als die BBC bei gleicher Zahl ganz sichtbarer Schlagzeilen (2).
- Guardian Desktop: dichte Spalten, Serifen, farbiger Kopfblock, viele Geschichten. mix-feed: vier Schlagzeilen,
  ein Bild über 63 % der Inhaltsbreite, eine Familie. Ruhiger und weniger dicht. Die Bildnachweise unter jedem
  Anreißer machen es aber unruhiger als beide Vorbilder: dort stehen keine Nachweise auf der Startseite (P2-2).

**Gegen Runde 4 (`r4-raster`, `r4-feed`) und Runde 3 (`r3-genz-app`)**
- R4: „KANGUVA“ in roter Schmalschrift über die volle Breite, Rot als Fläche. mix-feed: größte Schrift 30/40 px,
  Rot 0,1 %, normale Breite. Nicht laut.
- R3: Story-Kreise, rote Platte über dem Bild, Pillen. mix-feed: nichts davon; Titel im Bild nur auf Tintenverlauf,
  rechteckig.

## Befunde

### P0
Keine. `shots.mjs`: 0 Konsolenfehler, 0 leere Bilder, 0 Überlauf bei 390/820/1280, 0 Tamil ohne `lang`.

### P1

1. **Aufmacher-Schlagzeile am Handy zu tief (hartes Kriterium 2).** index, 390 × 844: Schlagzeile beginnt bei
   534 px (Grenze 480). Ursache: `.karte--aufmacher .karte__flaeche { height: clamp(420px, calc(100svh - 336px),
   620px) }` ergibt 508 px Bildhöhe unter 149 px Kopf. Behebung: Bildhöhe am Handy auf höchstens rund 450 px begrenzen
   (z. B. `clamp(380px, calc(100svh - 400px), 450px)`); das Hochformat bleibt, der Titel rückt über 480 px.
2. **Zu viele Bildformate (hartes Kriterium 10).** index: Handy 5, Desktop 9 Seitenverhältnisse. Ursachen im CSS:
   4/5, 4/3, 3/2, 2/3, 16/10, 5/2, 3/4 nebeneinander, dazu feste Höhen, die je Breite neue Formate erzeugen
   (`.kueche__reihe .karte__flaeche { height: 380px }`, `.community__gross { flex: 1 1 0 }`, Aufmacher-`clamp`).
   Behebung: auf drei Formate festlegen, z. B. 4:5 (Feed-Kacheln, Aufmacher Handy), 3:2 (Aufmacher Desktop, Stücke,
   Meldungsbilder statt 4:3), 2:3 (Kino); feste Höhen durch `aspect-ratio` ersetzen; Artikelbild 5:2 auf 3:2.
3. **Zeilen im Artikel am Desktop zu lang (Pflicht ≤ 70 Zeichen, Brief 10.2 Nr. 7).** artikel.html, 1280: Fließtext
   20 px in 842 px Spalte, gemessen Median 83, höchstens 88 Zeichen je Zeile; artikel-80: Median 85, höchstens 88;
   Vorspann rund 75; Startseite, Vorspann des Aufmachers 768 px breit, rund 81 Zeichen. Behebung: Textspalte
   auf `max-width: 34em` (bei 20 px rund 680 px, etwa 66 Zeichen); Vorspann unter dem Aufmacher ebenso begrenzen.
4. **Reihe gleicher Kacheln in „Diese Woche“ (Verbotsliste: identische Kartenraster).** index und termine, 1280:
   fünf gleich große 2:3-Kacheln in einer Reihe, zwei davon leere Tintenflächen mit roter Oberlinie und rund 55 %
   leerem Raum über dem Titel. Das liest sich wie eine Filmreihe aus einer Streaming-App, nicht wie ein
   Nachrichtenblock; Brief 10.2 Nr. 6 schließt gleiche Kacheln in einer Reihe für „Küche“ aus. Behebung: ein Kino-Bild
   doppelt breit als Leitstück (Titel im Bild), die zwei Radar-Filme als schmale Liste mit Kinozahl daneben.
5. **Kaum unterscheidbar von `mix-ordnung` im ersten Bildschirm.** 390 und 1280, index: gleicher Kopf, gleiches
   Aufmacherfoto, gleiche Schlagzeile an gleicher Stelle, rechte Spalte am Desktop gleich gebaut; am Handy zeigt
   `mix-ordnung` unter dem Aufmacher sogar mehr Bild. Runde 4 scheiterte unter anderem daran, dass alle Proben „wie
   Geschwister“ aussahen (`abgelehnt.md`); Luis soll hier zwischen zwei Richtungen wählen. Behebung: den Feed-Gedanken
   in den ersten Bildschirm holen, z. B. am Handy direkt unter dem Aufmacher den nächsten Anreißer als 4:5-Bildkachel
   mit Titel im Bild statt der Meldung mit 100-px-Bild; am Desktop statt „Aufmacher + Meldungsspalte“ eine Bildreihe
   aus Aufmacher und zwei hochformatigen Bildkacheln, Meldungen darunter.
6. **Verrutschte Kante im Kopf am Desktop.** alle Seiten, 1280: Text des Rubrikbands beginnt bei x = 16 px, Logo,
   Datumszeile und Inhalt bei x = 32 px (Aufmacher-Titel bei 64 px). Im ersten Bildschirm ist das die auffälligste
   Kante. Behebung: Band-Inhalt in denselben Innenbehälter wie Logo und Inhalt setzen (32 px Rand), erster Link ohne
   eigenen Innenabstand links. Am Handy stimmen die Kanten (16/16).

### P2

1. **Anreißertext am Handy 17 px.** index (Stücke, Termine), suche (`zeile__teaser` 17 px/25,5), rubrik: rund 860
   Zeichen auf der Startseite in 17 px; Pflicht für Fließtext ist 18 px, gerade für ältere Leser. Behebung: 18 px.
2. **Bildnachweise zerreißen die Anreißer.** index: 21 Nachweise in 12 px, je unter dem Text statt am Bild, oft
   zweizeilig mit Waise („CC BY-SA“ / „4.0“, z. B. Handy „Bundesverwaltungsgericht“, „Sri Lanka erlässt“, Desktop
   Küche „Dan arndt“). Damit hat jede Meldung fünf Zeilen Kleinkram. Die Lizenz steht nur als Text, ohne Verweis auf
   den Lizenztext. Behebung: Nachweis einzeilig direkt unter oder auf der Bildkante, kürzen („Foto: Hadi, CC BY-SA
   4.0“), Lizenz verlinken; auf der Startseite alternativ nur im Artikel und gesammelt im Fuß.
3. **Symbolbilder sichtbar nicht gekennzeichnet.** Desktop erster Bildschirm „INAIVU in Zürich“: Tänzerin bei einem
   Auftritt in Bangalore; Küche „Bremen“ und „Zürich: Kündigung“: Kottu-Teller. „Symbolbild“ steht nur im `alt`.
   Leser halten die Tänzerin für den Abend in Zürich. Behebung: im sichtbaren Nachweis „Symbolbild: …“.
4. **„Bild: Archiv tamil.de“ bei Filmmaterial.** Kino-Reihe: Szenenbild „Kanguva“ (p9711) und Teamfoto
   „Rathamaarey“ (p9697). Das Archiv ist nicht der Urheber; Filmbilder gehören Produktion oder Verleih. Behebung:
   Urheber aus dem Archivbeitrag übernehmen oder das Bild nicht verwenden.
5. **Schlechter Bildausschnitt „Rathamaarey“.** index/termine, Kino-Reihe: Querformat 1600 × 680 auf 2:3 beschnitten
   (`object-position: 60% 40%`); zu sehen ist nur Rajinikanth, links und rechts angeschnittene Schultern; der im Titel
   genannte Prashath Lokeshwaran ist nicht im Bild, `alt` beschreibt „das Team“. Behebung: Querformat behalten oder
   auf die Person des Titels beschneiden.
6. **Bildlose Einträge in „Diese Woche“, und die Messung sieht sie nicht.** Die zwei Radar-Filme sind Kacheln ohne
   Foto, am Handy ist „Scene“ die erste Kachel des Streifens; die zwei Termine haben kein Bild. Alle vier sind `h4`
   und fallen aus `anreisser`, `anreisser_mit_grafik` und `schlagzeilen_seite` heraus. Der Termin „Deepavali-Feier
   des Düsseldorf Tamil Sangam“ verweist auf `artikel.html`, das ein Bild hat. Behebung: Streifen mit einem Foto
   beginnen; Düsseldorf-Termin mit dem Artikelbild; Titel als `h3`, damit die Kennzahlen sie zählen.
7. **Am Handy wirken Bildschirm 2 und 3 dunkel.** index 390: Die INAIVU-Kachel (schwarzer Bühnengrund, randlos,
   rund 420 px) steht direkt vor „Diese Woche“ (1148 px Tinte); von etwa 850 bis 2970 px ist die Seite überwiegend
   dunkel. Das Kriterium misst nur den ersten Bildschirm; der Eindruck „dunkler Grund“ steht auf der Verbotsliste.
   Behebung: INAIVU nach „Diese Woche“ oder in den Community-Block stellen, oder ein helleres Bild wählen.
8. **Meldungsbilder am Desktop zu klein.** index 1280, rechte Spalte: 104 px breit (Brief 10.2 Nr. 4: mindestens
   120 px). Behebung: 128 px.
9. **Seitlicher Überlauf bei 320 px (WCAG 1.4.10, entspricht 1280 px bei 400 %).** index: 40 px;
   die Meldungsbilder (`.zeile__bild`, rechter Rand bei 335 und 360 px) ragen hinaus. Bei 640 px (200 %) kein Überlauf, alle anderen Seiten auch bei 320 px
   ohne. Behebung: Spalte des Meldungsbilds unter 360 px schrumpfen lassen (z. B. `minmax(0, 28vw)`).

### P3

1. Nachweis „Sardar 2“ enthält die rohe Adresse „(https://silverscreen.in)“, am Handy dreizeilig. Kürzen auf den
   Namen, Adresse als Link.
2. Küche am Desktop: Breiten 393 / 277 / 278 / 208 px; die letzte Kachel schmaler als die mittleren wirkt zufällig.
   Abgestuft (groß, mittel, mittel, mittel) oder 2 + 2.
3. Desktop-Kopf 167 px hoch, die Logozeile ist bis auf das Logo leer. Logo und Datumszeile in eine Zeile ziehen
   (wie `mix-ordnung`), spart rund 50 px über dem Aufmacher.
4. Inhalte: alle Schlagzeilen außer dem Termin „Deepavali-Feier des Düsseldorf Tamil Sangam“ fand ich wörtlich in
   `inhalte-klar2.json` bzw. im Rückblick; dieser Titel ist eine Neufassung aus dem Aufmacher. Gegen die Quelle
   prüfen. „Kanguva“, „Rathamaarey“ und „Payasam“ führen auf `#` (Archivbeiträge ohne Probeseite; laut Brief zulässig).

## Was trägt

1. **Nicht laut:** eine Familie (Libre Franklin), größte Schrift 30/40 px, Rot 0,1 %, Radius 0, keine Schatten,
   keine Pillen, keine Kreise. Neben R3 und R4 klar auf der ruhigen Seite.
2. **Bild überall, mit Nachweis:** 23 Fotos auf der Startseite, 0 Anreißer ohne Bild in der Zählung, jedes Fremdbild
   mit Nachweis (21/21), helle Schrift im Bild an der schwächsten Stelle 5,11 : 1.
3. **Bedienung sauber:** keine Tippfläche unter 44 px auf allen Seiten bei 390 und 820; Wischstreifen sind fokussierbare
   Regionen mit `aria-label` und sichtbarer Bildlaufleiste, per Tab erreichbar, am Desktop als Raster ohne Wischen;
   sichtbarer doppelter Fokusrahmen auch auf Bildkacheln; „Bewegung reduzieren“ schaltet alle 21 Übergänge ab;
   Kontaktwerte als „Beispielwert“ gekennzeichnet.

## Bedienbarkeit (nur zur Information)

| Heuristik | 0–4 | Begründung |
|---|---|---|
| 1 Status sichtbar | 3 | Aktive Rubrik hell und fett mit Linie; Trefferzahl in der Suche. |
| 2 Sprache der Nutzer | 4 | Deutsch, Datum mit Jahr, Orte und Kinozahlen. |
| 3 Kontrolle und Freiheit | 3 | „Zum Inhalt“, stehendes Rubrikband, Streifen per Tastatur scrollbar. |
| 4 Einheitlichkeit | 3 | Dachzeile überall gleich; Nachweise mal unter Text, mal unter Bild. |
| 5 Fehlervermeidung | 2 | Kontaktformular ohne Pflichtfeld-Hinweise. |
| 6 Erkennen statt Erinnern | 3 | Rubriken immer sichtbar; Streifen am Handy an der Kante angeschnitten. |
| 7 Flexibilität | 3 | Tastatur, Fokus, reduzierte Bewegung; Überlauf bei 320 px. |
| 8 Ästhetik, Reduktion | 2 | Ruhige Typografie, aber 21 Nachweiszeilen und leere Grafik-Kacheln. |
| 9 Fehler erkennen | – | In der Probe nicht prüfbar (Formular sendet nicht, Suche zeigt nur Treffer). |
| 10 Hilfe | 2 | Keine; für eine Nachrichtenseite kaum nötig. |
