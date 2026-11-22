# Prüfung hm-almanac („Kalenderblatt“), Runde 1
Harte Kriterien: 13 von 15 erfüllt · P0: 0 · P1: 5 · P2: 8 · P3: 7

Grundlage: `design/brief-v3.md`, `design/linien-auftrag.md`, `tamil-marke/references/abgelehnt.md`. Nicht gelesen:
`begruendung.md`, `.hallmark/`, frühere Kritiken. Aufnahmen: `tools/shots.mjs` mit 390/820/1280 von index, artikel,
termine, kino, verzeichnis, einreichen, werben, buchen über http://127.0.0.1:8952 (24 Aufnahmen, 0 Fehler). Dazu
Messungen im Browser (berechnete Schriftgrößen, Kontrast über Canvas, Bilder im ersten Bildschirm, seitliche Scroller)
und ein Paarvergleich bei 390 px mit NZZ, Spiegel, R2 und R4-Raster.

## Erster Eindruck
Hier steckt eine echte Idee, die zu tamil.de gehört: Die Startseite beginnt mit einem Kalenderblatt (Tag, Was, Wer,
Wo, „als Nächstes“ in Rot, vergangene Einträge grau, „Stand: Freitag, 13. November“). Diese Idee trägt über Termine,
Kino, Verzeichnis, Werben, Buchen und den Artikel. Die Hülle um das Blatt ist dagegen aus dem Vorlagenbaukasten:
Landingpage-Claim mit zwei Knöpfen, „Beitrag lesen“-Knöpfe, ein roter Vollflächen-Knopf in jedem Seitenkopf, ein
dunkler Kino-Block wie in Runde 5–7 und IBM Plex Mono für alle Ziffern, eine Schrift von der Ausschlussliste.

## Harte Kriterien

| # | Kriterium (Brief v3, Linien-Auftrag) | Handy 390 | Desktop 1280 | Ergebnis |
|---|---|---|---|---|
| 1 | Logo unverändert | `bilder/logo.png`, Original | dto. | erfüllt |
| 2 | Nur Deutsch, keine tamilische Schrift als Schmuck | `tamil_ohne_lang` 0, keine Tamil-Glyphen gesehen | dto. | erfüllt |
| 3 | Echte Inhalte | Stichprobe von 13 Angaben (Kloten, Aula Lysbüchel, THADAM 13.12., „Tickets günstiger“, Stripe, AiYA, Ceylon Palace, Glattbrugg, Kudumbam, Tamilalayam, OM 12 Spielorte, Gütersloh, Steinmeier): alle in `design/inhalte/`, `docs/redaktion/rueckblick-2026.md` bzw. `docs/vertrag/festlegung-werbung.md` gefunden; die Wochentage (8./15.11. So, 21.11. Sa, 13.12. So, 13.11. Fr) stimmen; Preise sichtbar als Platzhalter „folgt“ | dto. | erfüllt |
| 4 | Bildnachweis sichtbar | Artikel: direkt am Bild; Start, Termine, Kino: nur im Fuß („Bildnachweise“, `index.html` Z. 179) | dto. | erfüllt nach Brief v3 (siehe P2-5) |
| 5 | Fließtext am Handy ≥ 18 px | Absätze in `main` im Median 18 px (Artikel, Start, Termine, Kino) | Artikel 19 px | erfüllt |
| 6 | Kontrast WCAG AA | kleinster Wert 5,85:1 (Hell auf Rot `#B5282A`), Grau 6,26:1 auf Grund, 10,45:1 im dunklen Block | dto. | erfüllt |
| 7 | Tippflächen ≥ 44 px | Inline-Links 20–23 px hoch (Termine 6×, Kino 2×, Bildnachweis 20 px), Checkbox 24×24, Dateifeld 224×34 | n. a. | verletzt (nach Bogen E als P2 geführt) |
| 8 | Kein seitliches Scrollen 390/820/1280 | 0 px auf allen 8 Seiten | 0 px | erfüllt |
| 9 | `prefers-reduced-motion` | Regel in `almanac.css` und `base.css` | dto. | erfüllt |
| 10 | Schriften selbst gehostet, OFL im Ordner | `schriften/*.woff2`, `OFL.txt`, keine ungeladene Schrift | dto. | erfüllt |
| 11 | Keine Gedankenstriche | keiner auf den 8 Seiten; 1 Fund im Fließtext von `artikel-71.html` (P3) | dto. | erfüllt |
| 12 | Keine Dachzeilen, Versal-Labels, „·“-Metazeilen | 0 Elemente mit `text-transform: uppercase`, keine Dachzeile | dto. | erfüllt |
| 13 | Keine gleich großen Kartenraster, Verlauf-Bildkacheln, Seitenstreifen | keine | keine | erfüllt |
| 14 | Seitenliste vollständig | alle 11 Dateien vorhanden (+ `einreichen-danke.html`, 19 Artikel) | dto. | erfüllt |
| 15 | Kino „diese Woche nach Stadt“ | nach Film geordnet; „OM“ nur „in Deutschland“, „Scene“ „und 6 weitere Städte“ | dto. | **verletzt** (P1-4) |

## Paarvergleich (390 px, erster Bildschirm)

- **NZZ (Handy):** Bei der NZZ folgt direkt unter der Navigation ein 356 px hohes Foto, darunter ein dreizeiliger
  Titel und eine graue Autorenzeile. Im ersten Bildschirm steht kein Knopf. Bei hm-almanac sind 0 Bilder im ersten
  Bildschirm. Statt einer Geschichte steht dort ein Werbesatz („Deepavali ist vorbei. Gefeiert wird weiter.“) mit
  zwei Knöpfen. Die Datenordnung des Kalenderblatts (Tag/Was/Wer/Wo, „als Nächstes“) ist dagegen klarer und eigener
  als alles bei der NZZ.
- **Spiegel (Handy):** Der Spiegel zeigt im ersten Bildschirm eine Schlagzeilenleiste, ein Foto und einen Aufmacher,
  also drei Geschichten. hm-almanac zeigt nur zwei Kalenderzeilen und keine Geschichte aus dem Rückblick. Die
  Kopfzone ist ähnlich gestaffelt (dunkle Leiste, Logo, vier Textreiter). Durch die schwarze Rückblick-Leiste wirkt
  der Kopf bei hm-almanac aber eher wie ein Cookie- oder Aktionsbanner als wie eine Markenleiste.
- **Runde 2 (Community-Magazin):** R2 hat Creme-Grund, Pillen-Navigation („Nachrichten“, „Kino“), eine Anzeige über
  dem Inhalt und ein abgerundetes Bild. hm-almanac hat einen kühlen Grund rgb(236,241,245), Textreiter mit roter
  Unterstreichung, rechte Winkel und keine Anzeige oben. Der Abstand zu R2 ist klar.
- **Runde 4 (Raster):** R4 hat ein rotes „KANGUVA“ in Extraschmal, ein rotes Linienraster und den Datumsstempel
  „14.11.“. hm-almanac ist schwarz auf hell, hat keine schmalen Schnitte und Linien in Tinte. Verwandt ist das
  „Fahrplan“-Mittel aus R4, also Datum und Zahl als großes Zeichen: auf `kino.html` „15.11.“ und „11 Kinos“ in Mono
  mit 48 px (Desktop) bzw. 32 px (Handy), siehe P2-8.
- **Die vier Punkte aus Runde 4:** Rot ist kein Großflächenrot, nur Logo, Links, „als Nächstes“ und je ein
  Knopf (P2-4). Laut ist die Seite nicht, groß aber schon (P2-3). Baukasten: ja, im Knopfvokabular (P1-2). Schrift:
  Hanken Grotesk ruhig, Plex Mono von der Ausschlussliste (P1-1).

## Befunde

### P0
Keine. `bericht.json`: 0 Fehler, 0 Konsolenfehler, 0 leere Bilder, 0 px Überlauf bei 390/820/1280.

### P1
1. **Schrift von der Ausschlussliste: IBM Plex Mono.** `impeccable/reference/brand.md` Z. 30 („Ban list … IBM Plex
   Mono“). Die Verbotsliste in `tamil-marke` übernimmt diese Liste. Plex Mono setzt jede Ziffer: die Datumsspalte des
   Kalenderblatts („So 08.11.“, alle Seiten), die Zahlen auf `kino.html` („11“, „12“, „15.11.“), die Maße und
   „Start ab 17.11.“ auf `werben.html`/`buchen.html` und die rot gepunkteten Daten in der Spalte „Im Bericht“ auf
   `verzeichnis.html`. Im Bild steht dadurch Hanken neben Mono: „So 08.11.“ springt in Breite und Grauwert und liest
   sich wie eine Terminalzeile. *Abhilfe:* Ziffern aus Hanken Grotesk mit `font-variant-numeric: tabular-nums
   lining-nums` setzen, Spalten über die Breite ausrichten statt über eine Mono.
2. **Landingpage-Hülle statt Nachrichtenkopf (Baukasten).** `index.html`: H1-Werbesatz „Deepavali ist vorbei.
   Gefeiert wird weiter.“, darunter eine Unterzeile und das Knopfpaar „Alle Termine“ (rot gefüllt) und
   „Kinoprogramm“ (Rahmen), also das CTA-Paar einer Produktseite. Unter beiden Geschichten steht dazu der Knopf
   „Beitrag lesen“, obwohl der Titel schon der Link ist (Bogen B: Knöpfe „Weiterlesen“). Termine, Kino und
   Verzeichnis wiederholen dieselbe Schablone: Satz als H1, Unterzeile, roter Knopf, weißes Blatt.
   *Abhilfe:* Das Kalenderblatt selbst wird der Kopf der Startseite, mit einer echten Überschrift aus dem Inhalt
   statt des Werbesatzes. „Beitrag lesen“ entfällt. „Per WhatsApp teilen“ wird ein schlichter Link, wie es
   `abgelehnt.md` (R4, „brauchbar bleibt“) festhält.
3. **Dunkler Kino-Block auf der Startseite wiederholt Runde 5–7.** `index.html`, Abschnitt „Was im Kino läuft“,
   Grund rgb(6,14,21) über die volle Breite (390 und 1280). `abgelehnt.md` nennt „dunkler Kino-Bereich“ und
   „Diese Woche“-Bänder ausdrücklich als Bestandteile der abgelehnten Runden. *Abhilfe:* Kino als eigener Abschnitt
   des Kalenderblatts auf demselben hellen Blatt, getrennt durch eine Linie in Tinte. Keine zweite dunkle Fläche.
4. **Kino nicht „nach Stadt“ (Seitenliste).** `kino.html` ist nach Film geordnet. Bei „OM“ steht nur „in
   Deutschland“, bei „Scene“ „Berlin, Bremen, Chemnitz, Dortmund, Düsseldorf und 6 weitere Städte“. Wer in
   Stuttgart oder Zürich wohnt, findet seine Stadt nicht, und gerade das ist die Aufgabe „finden: welcher Film läuft
   wo“ aus Brief v3. *Abhilfe:* Einen Stadtindex als Hauptliste anlegen (Stadt, darin Kino und Film, alphabetisch),
   die Filmansicht darunter. Fehlen Städte in der Quelle, steht ein sichtbarer Platzhalter („Spielorte für OM folgen“).
5. **Ungleicher Abstand im ersten Bildschirm (nicht hochwertig).** Bei 1280 liegen zwischen Seitenkopf-Knopf und
   erstem Inhaltsblock auf `termine.html` etwa 40 px, auf `kino.html` etwa 160 px (Knopf endet bei y≈455,
   „Spielorte ab 9. November“ beginnt bei y≈617). Die Schablone ist dieselbe, die Abstände sind es nicht. Auf
   `index.html` steht bei 1280 die H1 mit 66,9 px *unter* dem Kalenderblatt. Das größte Element liegt also unten
   und das Auge springt zurück. *Abhilfe:* Den Abstand Kopf → erster Block als Token festlegen
   (`--space-head-after`) und auf allen Seitentypen gleich halten. Auf der Startseite steht die Überschrift über dem
   Blatt.

### P2
1. **Tippflächen unter 44 px** (Bogen E): `termine.html` `.sheet a` (z. B. „Wagenfest“ 274×22, 6×),
   `kino.html` Filmtitel 140×23 und 167×23, `artikel.html` Bildnachweis-Links 257×20 und 90×20,
   `einreichen.html` Checkboxen 24×24, Dateifeld 224×34. Die 1×1-Eingaben sind versteckte Radios mit Label und kein
   Befund. *Abhilfe:* Den Link über die ganze Zeile ziehen (`::after { inset: 0 }`) bzw. `min-block-size: 44px`;
   Checkboxen 24 px mit 44-px-Label.
2. **Kein Bild im ersten Bildschirm** auf index, termine, kino und verzeichnis, bei 390 und 1280 (gemessen: 0 Bilder
   oberhalb von 844 bzw. 800 px). Die Fotos sind das stärkste Material der Rückblick-Beiträge. Am Handy sieht man
   in fünf Sekunden einen Werbesatz und zwei Tabellenzeilen. Das Risiko ist „trocken“ bzw. „zu classic“.
   *Abhilfe:* Auf der Startseite ein Bild am Kalendereintrag „als Nächstes“ oder an der ersten Geschichte.
3. **Schlagzeilengrößen.** H1 66,9 px (index, 1280), 59,2 px (übrige Seiten, 1280), H2 „Steinmeier …“ 59,2 px
   (1280) bzw. 36 px (390), H1 am Handy 36 px. Die Verbotsliste in `tamil-marke` deckelt bei 32/38 px (Aufmacher
   34/44). Brief v3 misst das nicht mehr. *Regelkonflikt:* Gilt die Obergrenze weiter, ist das P1. Das entscheidet
   die Hauptsitzung. *Abhilfe:* Desktop-H1 höchstens 48 px, Handy 32 px.
4. **Rot als Fläche** in jedem Seitenkopf: `.btn--primary` (#B5282A, z. B. 254×48 „Kalender per WhatsApp teilen“)
   auf index, termine, kino, verzeichnis und werben. Laut Marke ist Rot nur Akzent. *Abhilfe:* Knopf in Tinte oder
   als Link. Rot bleibt Logo, Links und „als Nächstes“.
5. **Bildnachweis nicht am Bild** auf index (rb-30, rb-71), termine (rb-76) und kino (rb-43). Der Nachweis steht
   nur im Fuß. Brief v3 erlaubt das, der Linien-Auftrag verlangt „Bildnachweis an jedem Bild“. *Abhilfe:* Die
   Nachweiszeile wie im Artikel in jede `figcaption` setzen.
6. **15 px als Lesetext am Handy:** Auf `buchen.html` stehen 1379 Zeichen in 15 px und nur 450 in 18 px. Dazu kommen
   die Hinweise auf `einreichen.html`, Unterzeilen und Bildunterschriften. Für 65-Jährige ist das der Buchungsweg mit
   der kleinsten Schrift. *Abhilfe:* Erklärtexte mindestens 17 px, nur Tabellenköpfe 15 px.
7. **Rangfolge auf der Startseite bei 1280:** Die Knopfreihe beendet den ersten Bildschirm. Die erste Geschichte
   beginnt bei y≈936, also unterhalb davon. Zwischen Claimblock und Geschichte liegen rund 110 px Leere.
   *Abhilfe:* Behebt sich zusammen mit P1-2 und P1-5.
8. **Datum als Plakatzahl (Nähe zu R4):** `kino.html` „15.11.“ und „11“/„12“ in 48 px Mono (1280) bzw. 32 px (390)
   mit eigenem Label „Kinos/Spielorte/Sonntag“. Das ist die Fahrplan- und Stempelgeste aus R4-Raster.
   *Abhilfe:* Die Zahlen in Lesegröße (18–20 px) in die Zeile setzen.

### P3
1. Die schwarze Leiste „Rückblick 2026 in zwanzig Berichten“ oben auf jeder Seite ist eine dritte dunkle Fläche und
   liest sich wie ein Aktionsbanner. *Abhilfe:* Hell, als Link im Kopf.
2. `p.byline` „8. November 2026, Berlin, Düsseldorf, München“ ist die „·“-Metazeile mit Kommas statt Punkten.
   *Abhilfe:* Die Orte in den Satz oder ins Kalenderblatt aufnehmen.
3. `index.html` `div.tabs` („Das Jahr 2026 in Berichten“): 597 px Inhalt in 358 px. Der letzte Reiter ist bei 390
   abgeschnitten, ohne Hinweis auf weitere. *Abhilfe:* Umbrechen oder ein Auswahlfeld.
4. `buchen.html`: Die Schrittleiste bricht bei 390 um („5 Bezahlen“ allein in Zeile 2). Die Schritte sind
   Textlinks mit etwa 20 px Höhe. *Abhilfe:* Senkrechte Liste oder „Schritt 1 von 5“.
5. `einreichen.html`: Die Datumsfelder zeigen „mm/dd/yyyy“. Das kommt von der Browsersprache der Aufnahme; mit
   `de-DE` prüfen.
6. `einreichen.html` trägt die Idee nicht. *Abhilfe:* Eine Vorschau „so erscheint Ihr Termin im Kalenderblatt“ als
   Zustand.
7. `artikel-71.html`: Gedankenstrich im Fließtext („erwachsen kann – ein Band“), sofern es kein wörtliches Zitat ist.

## Was trägt
- **Das Kalenderblatt als Ordnungsprinzip.** Tag, Was, Wer, Wo, „als Nächstes“ als einzige rote Zeile, vergangene
  Einträge grau, Stand-Datum, korrekte Wochentage. Das gehört nur tamil.de und trägt über Termine (dazu die
  Zeitleiste „Festjahr 2026“ mit „heute“-Marke), Werben („Start ab“, „folgt“) und Buchen (Kalender mit
  durchgestrichenen vergangenen Tagen).
- **Die Querverweise.** Im Artikel „Im Beitrag genannt“ mit Datum und Ort, im Verzeichnis die Spalte „Im Bericht“
  mit Datum des Quellbeitrags. Das zeigt, dass alles aus echten Berichten kommt.
- **Der Grund.** Kühles helles Grau rgb(236,241,245), rechte Winkel, keine Pillen, keine Rundungen, keine Versalien,
  Kontrast überall ≥ 5,85:1. Der Abstand zu R1–R3 ist klar.

## Bedienbarkeit (nur zur Information)

| Heuristik | 0–4 | Satz |
|---|---|---|
| 1 Sichtbarkeit des Status | 3 | „Stand“-Daten und „als Nächstes“ sagen, wie aktuell es ist; der Buchungsschritt ist sichtbar. |
| 2 Übereinstimmung mit der Welt | 3 | Kalender, Spielorte, Werbeplätze in Alltagssprache; Kino denkt in Filmen statt in Städten. |
| 3 Kontrolle und Freiheit | 3 | Buchen auf einer Seite, Schritte anspringbar; Reiterleiste am Handy abgeschnitten. |
| 4 Konsistenz | 2 | Gleiche Schablone je Seite, aber ungleiche Abstände und wechselnde Knopf-/Linkformen fürs Teilen. |
| 5 Fehlervermeidung | 3 | Pflichtfelder erklärt („Felder ohne Zusatz sind nötig“), vergangene Tage gesperrt. |
| 6 Wiedererkennen statt Erinnern | 3 | Tabellenköpfe Tag/Was/Wer/Wo wiederholen sich auf allen Seiten. |
| 7 Flexibilität | 2 | Verzeichnisfilter vorhanden; kein Stadtzugang im Kino. |
| 8 Ästhetik und Reduktion | 2 | Das Blatt ist reduziert, die Hülle mit CTA-Paar, roten Knöpfen und dunklem Block nicht. |
| 9 Fehler erkennen | n. g. | Fehlerzustände der Formulare nicht geprüft. |
| 10 Hilfe | 3 | Hinweise je Feld, Ablauf der Buchung auf `werben.html` erklärt. |
