# Prüfung hm-tageskalender, Runde 2
Harte Kriterien: 14 von 14 erfüllt · P0: 0 · P1: 1 · P2: 7

Maßstab: `design/brief-v3.md`, `design/linien-auftrag.md`, `abgelehnt.md`, Hallmark-Floor. Brief v3 hat keine
nummerierte Kriterienliste; die 14 harten Kriterien unten sind die Pflichten aus Brief v3 („Was fest bleibt“) und
aus `linien-auftrag.md` („Regeln“) plus Floor. Gemessen über `http://127.0.0.1:8111/` mit `tools/shots.mjs`
(index, kino, termine, artikel, rubrik je 390/820/1280), einer eigenen DOM-Messung (Puppeteer, 390 × 844 und
1280 × 800, sieben Seiten) und `sloplint` (index, kino, termine). Aufnahmen:
`/tmp/claude-0/-home-user/16175975-e412-59cc-bdc3-6fbcba0681fa/scratchpad/kritik-tk-r2/`.

## Erster Eindruck (3 Sätze)

Die Startseite liest sich bei 1280 wie die Titelseite eines Tages: Ziffer „13“, Schlagzeile, Vorspann, Foto rechts,
darunter die Festtabelle mit Spaltenköpfen und das Kinoprogramm, alles auf kühlem Papier mit hellen Tafeln unter
einer kräftigen Oberkante. Am Handy steht der Kalender jetzt vor dem Aufmacher, die Schlagzeile ist noch im ersten
Bildschirm (y 552), das Foto nur zu 172 von 238 px. Kino und Termine fallen bei 1280 dagegen in einen gewöhnlichen
Seitenkopf (Titel und Links links, Foto rechts, viel Leerfläche), und die eigentliche Tabelle beginnt erst am
unteren Rand.

## Stand der Vorrunden-Punkte

| Nr. | Punkt | Behoben | Messwert |
|---|---|---|---|
| 1 | Kino/Termine nicht aus `design/inhalte/` (THADAM, „OM“, „Jailer 2“) | **ja** | „THADAM“, „Jailer“, „Kino Claudia“, „OM“: 0 Treffer in index, kino, termine. „Im Programm“ = „Scene“ 11 Kinos und „Ramayana: Rise of a Legend“ 2 Kinos, Stand 9. November, „6 weitere Städte“ mit Hinweis „Orte, Namen der Kinos und Uhrzeiten folgen“ = `inhalte.json` `diese_woche.kino`. Termine = 15.11. Deepavali-Feier Düsseldorf Tamil Sangam (aus Beitrag 30) und 21.11. Diwali in Basel, Aula Lysbüchel (= `diese_woche.termine`). „Aus dem Kinojahr 2026“ und „Das Jahr 2026“: Stichprobe 12 von 12 Titeln und Nachweisen in `design/inhalte` oder `docs/redaktion/rueckblick-2026.md` gefunden (Sardar 2, Mayilaa, First Take, Akka, Gatta Kusthi, Parasakthi, Members of the Problematic Family, Grugahalle, INAIVU, Koothandavar, D Neethidoss, Roland zh). |
| 2 | Mischung trägt im ersten Bildschirm | **ja auf der Startseite**, bei 390 knapp (siehe P2-1) | **390 × 844:** Tagesziffer „13“ 48 px/800 (y 101 bis 150), Festtabelle `<table>` mit zwei Zeilen (y 245 bis 477) und „Ganzer Festkalender“ (y 483), Aufmacher-Schlagzeile 30 px (y 552 bis 655), Aufmacherfoto ab y 672 (172 von 238 px sichtbar). Material aus B sichtbar: kühles Papier `oklch(0.968 0.007 245)`, hellere Tafel mit 2 px Oberkante über die volle Breite. **1280 × 800:** Ziffer 73,6 px, Schlagzeile 39,7 px (y 241), Vorspann, Foto 478 × 358 (y 162 bis 520), Festtabelle mit sichtbaren Köpfen „Tag, Was, Wer, Wo“ (y 536 bis 769, Link y 775), Kinotabelle ab y 602, Rückblick-Leiste (y 0 bis 45) und weiße Tafeln mit Oberkante aus B. Kein „A mit eingeklebten Tabellen“: Bei 1280 bilden Tagesziffer, Aufmacher und Festtabelle eine linke Spalte, Foto und Kino die rechte. |
| 3 | Kopf am Handy: Kanten 16 px, Höhe etwa eine Zeile | **ja** | Kopf 0 bis 61 px; Logo x 16 bis 112 (96 × 38); „Termine“ x 150, „Kino“ x 236, „Mehr +“ x 295 bis 374 → rechter Rand 16 px; Tippflächen 44 px hoch (y 8 bis 52). |
| 4a | Keine vergangenen Feste unter „Die nächsten Feste“ | **ja** | index und termine („Ab heute“): nur 15.11. und 21.11. bei Stand 13.11. |
| 4b | Eine linke Kante je Spalte am Handy | **teilweise** | index 390: Kanten 16 / 82 / 96. „November 2026“ neben der Ziffer steht bei x 82, die zweite Tabellenspalte 70 px tiefer bei x 96 (Versatz 14 px, siehe P2-5). termine 390: 16 / 96 / 180; rubrik 390: 16 / 57. kino 390 meldet 16 / 28 / 59 / 256 / 286 / 306; die Kanten 28 und 59 liegen unterhalb des ersten Bildschirms und sind **nicht von Hand geprüft**. |
| 4c | Lange Titel stoßen nicht ans Vorschaubild | **ja** | Abstand Titel zu Bild: 12 px bei 390 (index 9 Einträge, rubrik 4), 24 px bei 1280. |
| 4d | Gestrichelte Platzhalter brechen nicht | **ja** | `.fill` auf index, kino, termine, rubrik, verzeichnis-eintrag, werben, kontakt: je `getClientRects().length = 1`, kein innerer Überlauf (scrollWidth = clientWidth); zweizeilige Platzhalter („Impressum und Datenschutz folgen“, 68 px hoch bei 1280) bleiben ein Rechteck. |

## Harte Kriterien

| Kriterium | Messwert Handy (390) | Messwert Desktop (1280) | Ergebnis |
|---|---|---|---|
| 1 Logo unverändert | `bilder/logo.png`, md5 gleich `design/inhalte/logo.png`, 96 × 38 | gleich, 124 × 50 | erfüllt |
| 2 Nur Deutsch, keine tamilische Schrift als Schmuck | `tamil_ohne_lang` 0, keine Tamil-Zeichen gesehen | gleich | erfüllt |
| 3 Echte Inhalte | siehe Vorrunden-Punkt 1 | gleich | erfüllt |
| 4 Bildnachweis an jedem Bild | Bildunterschrift mit Urheber, Lizenz, „Quelle“ an Aufmacher, Kino-, Termine-, Rubrik- und Listenbildern; „Symbolbild.“ gekennzeichnet | gleich | erfüllt |
| 5 Fließtext ≥ 18 px am Handy (Auftrag; Brief v3: 17) | index, kino, termine, rubrik, werben: kleinster Text über 30 Zeichen 18 px | – | erfüllt (Ausnahme auf Nebenseiten siehe P2-6) |
| 6 Kontrast WCAG 2.2 AA | sloplint 0 FAIL im Render; Text `oklch(0.19)` auf `oklch(0.968)`; Grautöne nicht von Hand nachgemessen | gleich | erfüllt (laut sloplint) |
| 7 Tippflächen ≥ 44 px | `tippflaechen` 0 bei 390 und 820 (5 Seiten) | – | erfüllt |
| 8 Kein seitliches Scrollen | `ueberlauf` 0 bei 390 | 0 bei 820 und 1280 (15 Aufnahmen) | erfüllt |
| 9 `prefers-reduced-motion` | Regel in `base.css` und `hm-tageskalender.css`; Übergänge nur Hintergrund, Rahmen, `transform` | gleich | erfüllt |
| 10 Schriften selbst gehostet, OFL im Ordner | Golos Text und Rethink Sans als woff2, zwei OFL-Dateien in `schriften/`; `shots.mjs`: 0 nicht geladene Schriften | gleich | erfüllt |
| 11 Keine Gedankenstriche | 0 auf 7 Seiten | 0 | erfüllt |
| 12 Keine Dachzeilen, Versal-Labels, „·“-Metazeilen | `text-transform: uppercase` 0, Sperrung 0, „·“ 0; Rubrik und Ort stehen unter dem Titel („Kultur, Deutschland“) | gleich | erfüllt |
| 13 Keine gleich großen Kartenraster, Verlauf-Kacheln, Seitenstreifen | keine gesehen; Listen mit Linien, Bild rechts | gleich | erfüllt |
| 14 Hallmark-Floor | sloplint index/kino/termine je 0 FAIL, 1 WARN (siehe P2-7); `overflow-x: clip` auf html und body; 2 Familien; Radius 2 px | gleich | erfüllt |

## Paarvergleich

**Probe gegen A (`hm-eigen`) und B (`hm-almanac`), erster Bildschirm.**
- 390: A zeigt Ziffer, Schlagzeile (y 150), Foto (y 263) und die Feste erst ab y 740; B zeigt Seitentitel „Die
  nächsten Feste der Community“, Foto und eine kleine Schlagzeile, die Tabelle erst ab y 750. Die Probe zeigt als
  einzige der drei Ziffer, zwei Festzeilen und die Aufmacher-Schlagzeile zugleich; dafür sinkt die Schlagzeile um
  rund 400 px gegenüber A und das Foto ist angeschnitten.
- 1280: A stellt das Foto 765 px breit rechts, die Feste als Liste ohne Köpfe links; B stellt die Tabelle (fünf
  Zeilen, darunter das vergangene 08.11.) als Hauptsache und das Foto klein daneben. Die Probe übernimmt aus A die
  Ziffer und die Schlagzeile vor dem Foto, aus B Spaltenköpfe, weiße Tafel mit 2 px Oberkante, kühles Papier und
  die Rückblick-Leiste; das Foto ist mit 478 px kleiner als bei A.

**Probe gegen Guardian, Handy (`news-guardian-handy-1.jpg`).**
- Guardian zeigt im ersten Bildschirm Kopf mit Rubrikleiste und drei Geschichten; die Probe einen Aufmacher und zwei
  Termine. Weniger Geschichten, dafür ein eigener Dienst (nächste Feste) an erster Stelle.
- Beide trennen mit Linien statt Kästen; die Probe mit 2 px dunkler Oberkante je Abschnitt und 1 px zwischen
  Zeilen, Guardian mit feinen Linien und farbigen Rubrikmarken. Die Probe hat am Handy keine Rubrikleiste, nur
  „Termine, Kino, Mehr“.

**Probe gegen Runde 2 (`r2-community-magazin-390.jpg`).**
- Runde 2: cremefarbener Grund, Pillen-Navigation mit großen Rundungen, Anzeige über dem Inhalt. Probe: kühles
  Papier (Farbton 245), Radius 2 px, keine Anzeige, keine Pillen. Kein Rückfall.

**Probe gegen Runde 4 (`r4-raster-390.jpg`).**
- Runde 4: rotes Versal-Titelwort „KANGUVA“ über die volle Breite, rote Versal-Dachzeile, feste Leiste unten in
  Versalien. Probe: größte Schrift ist die Tagesziffer (48 px am Handy, schwarz), Rot nur auf Logo, „15“,
  „Deepavali-Feier“ und „als Nächstes“; keine Versalien. Kein Rückfall.

## Befunde

### P0
Keine. `shots.mjs`: 15 Aufnahmen, 0 Fehler (kein Überlauf, keine Konsolenfehler, keine leeren Bilder).

### P1

**P1-1 Kino und Termine bei 1280: Seitenkopf mit Leerfläche, Tafelkante ohne Bezug, Tabelle erst am Rand.**
Ort: `kino.html` und `termine.html`, 1280 × 800. Links stehen Titel (48 px), Einleitung und Links und enden bei
y ≈ 325 (kino) bzw. y ≈ 295 (termine); rechts reicht Foto plus Bildunterschrift bis y ≈ 545 bzw. 525. Links bleibt
eine Leerfläche von rund 650 × 230 px. Die Tafel „Im Programm“ / „Ab heute“ beginnt erst bei y 608 bzw. 590 und
endet rechts bei x 1043: Diese Kante trifft weder den Satzspiegel (x 1229) noch die Bildspalte (x 751 bis 1229).
Im ersten Bildschirm steht je nur eine Zeile („Scene“ bzw. „15 Deepavali-Feier“), obwohl beide Seiten zum Finden da
sind. Das Muster „Titel links, Foto rechts, darunter Tafel“ ist der austauschbare Seitenkopf, gegen den Luis'
Urteil „komplett generisch“ stand; auf der Startseite ist es gelöst, hier nicht. Nach Bogen (nicht hochwertig im
ersten Bildschirm: ungleiche Abstände, verrutschte Kanten) P1.
Behebung: das Raster der Startseite übernehmen, also die Tafel in die linke Spalte (x 51 bis 719) direkt unter
Einleitung und Links setzen und das Foto mit Nachweis rechts daneben stehen lassen, oder die Tafel auf die volle
Breite x 51 bis 1229 ziehen und das Foto auf ≤ 260 px Höhe kürzen. Ziel: mindestens zwei Tabellenzeilen über
y 800, keine Kante bei x 1043.

### P2

**P2-1 Festtabelle am Handy ohne sichtbare Spaltenköpfe.** Ort: index und termine, 390. Die `<th>` „Tag, Was,
Wer, Wo“ sind nur für Screenreader da; sichtbar ist eine Datumsspalte mit Zeilen und Linien, die wie A's Liste
aussieht. B's Kalenderblatt ist am Handy nur über Papier und Tafel erkennbar. Behebung: Köpfe in 14 px über der
Tabelle zeigen, etwa „Tag“ über der Ziffernspalte und „Was, wer, wo“ über der zweiten (x 96).

**P2-2 Daten in wechselnder Form.** Ort: index 1280 „Stand: 9. November“, kino 390 „Stand 9. Nov.“ (ohne
Doppelpunkt, y ≈ 827, erster Bildschirm), kino 1280 Spalte „9. Nov.“, index/termine „Stand: Freitag, 13.
November“; unter den Ziffern „So, Nov.“ und „Sa, Nov.“ (Wochentag ohne Punkt, Monat mit Punkt). Behebung: eine
Form festlegen, z. B. „Stand: 9. November“ überall und unter der Ziffer „So., Nov.“ oder „Sonntag“.

**P2-3 Rubrik am Handy anders gebaut als die Startseite.** Ort: `rubrik.html`, 390. Die Ziffer „8“ steht auf Höhe
der dritten Zeile (Monat, „Sonntag, Deepavali“, Orte), auf der Startseite steht „13“ oben bündig mit dem Monat; und
das Foto steht vor Ziffer und Titel, auf der Startseite der Titel vor dem Foto. Behebung: Ziffer oben ausrichten
und die Reihenfolge Ziffer, Titel, Foto wie auf der Startseite.

**P2-4 Startseite 1280: Tafeln enden ungleich.** Ort: index 1280, unter dem ersten Bildschirm. Festtafel endet bei
y 826, Kinotafel bei y 920; links bleiben 184 px leer bis „Zuletzt bei tamil.de“ (y 1010). Behebung: beide Tafeln
auf gleiche Unterkante strecken (Grid `align-items: stretch`) oder den Abstand unter der kürzeren Tafel schließen.

**P2-5 Zwei innere Kanten im Datumsbereich am Handy.** Ort: index 390, „November 2026 / Freitag“ bei x 82 über der
Tabellenspalte bei x 96. Behebung: Monat und zweite Tabellenspalte auf dieselbe Kante legen (Ziffernspalte 80 px
breit für beide).

**P2-6 16 px bei Texten über 30 Zeichen auf Nebenseiten.** Ort: `verzeichnis-eintrag.html` und `kontakt.html`,
390: kleinster Text mit mehr als 30 Zeichen 16 px (Element nicht bestimmt, wahrscheinlich Hinweis- oder
Formulartext). Unter Brief v3 (17 px) und Auftrag (18 px), falls Fließtext. Behebung: prüfen und auf 18 px setzen.

**P2-7 sloplint meldet Schrift-Ersatz im Render.** Ort: index, kino, termine, je 1 WARN „fallback: rethink-sans-
latin-wght-normal.woff2“. `shots.mjs` meldet alle Schriften geladen, die eigene Messung zeigt Rethink Sans. Wohl ein
Zeitproblem der Aufnahme, aber Hallmark verlangt, keinen Ersatzschnitt abzunehmen. Behebung: Aufnahme wiederholen,
ggf. `font-display` und Vorladen (`<link rel="preload">`) für Rethink Sans.

### P3 (Hinweis)
- sloplint zählt auf termine 60, kino 20, index 14 ausgenommene Stellen; die Gründe stehen im Stempel (49b, 77, 78,
  79). Die Hauptsitzung sollte wissen, dass 49b (verlinkte Titel in Tabellen) die meisten davon abdeckt.
- Das Kinofoto (Koovagam-Fest, Thema eines Films vom Juli) hat keinen Bezug zu den zwei Filmen im Programm; es ist
  richtig als „Archivbild“ gekennzeichnet.

## Was trägt

1. Startseite 1280: Ziffer, Schlagzeile, Vorspann und Festtabelle mit Köpfen in einer Spalte, Foto und
   Kinoprogramm in der zweiten; das ist ein Tagesblatt mit Kalender, das nur tamil.de gehören kann, und es kommt
   ohne Dachzeilen, Versalien und Kartenraster aus.
2. „Zuletzt bei tamil.de“ führt die Datumsspalte des Kalenders („22 / Do, Okt.“) in die Nachrichtenliste weiter;
   Bild rechts mit Nachweis, 24 px Abstand zum Titel.
3. Inhalte sind sauber: keine erfundenen Kino- oder Termin-Angaben mehr, Platzhalter („Diese Orte, die Namen der
   Kinos und die Uhrzeiten folgen“, „Preise folgen“) sind als solche gesetzt und brechen nicht.

## Bedienbarkeit (nur zur Information)

| Heuristik | 0–4 | Satz |
|---|---|---|
| 1 Status sichtbar | 4 | Datum und „Stand“ an jeder Tabelle, aktueller Menüpunkt unterstrichen. |
| 2 Sprache der Leser | 4 | Deutsch, Tagesangaben wie im Kalender. |
| 3 Kontrolle und Freiheit | 3 | „Mehr +“ als Aufklapper; Rückweg nur über Logo und Menü. |
| 4 Konsistenz | 3 | Datumsformen und Ziffer-Ausrichtung wechseln (P2-2, P2-3). |
| 5 Fehlervermeidung | 3 | Formulare nicht im Detail geprüft. |
| 6 Wiedererkennen | 4 | Rot markiert immer den nächsten Termin, im Text erklärt. |
| 7 Effizienz | 3 | Am Handy Feste vor dem Aufmacher; auf Kino und Termine bei 1280 Tabelle erst am Rand (P1-1). |
| 8 Ästhetik und Reduktion | 3 | Ruhig, zwei Familien, Linien statt Kästen; Leerfläche auf den Unterseiten. |
| 9 Fehler erkennen | – | nicht geprüft. |
| 10 Hilfe | 3 | „Meine Stadt finden“, „Termin einreichen“ direkt im Kopf der Seiten. |

**Trägt die Mischung?** Auf der Startseite ja, messbar bei 390 × 844 und 1280 × 800 (Ziffer und Aufmacher aus A,
Festtabelle, Papier, Tafel und Rückblick-Leiste aus B im ersten Bildschirm); auf Kino und Termine bei 1280 noch
nicht, dort steht ein gewöhnlicher Seitenkopf über der Tabelle (P1-1).
