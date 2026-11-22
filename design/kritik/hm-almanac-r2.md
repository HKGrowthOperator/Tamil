# Prüfung hm-almanac („Kalenderblatt“), Runde 2
Harte Kriterien: 14 von 15 erfüllt · P0: 0 · P1: 0 · P2: 5 · P3: 9

Grundlage: `design/brief-v3.md`, `design/linien-auftrag.md`, `tamil-marke/references/abgelehnt.md`, Hallmark
`SKILL.md` und `references/gates.md`, `design/kritik/hm-almanac-r1.md`. Nicht gelesen: `begruendung.md`.
Aufnahmen: `tools/shots.mjs` über http://127.0.0.1:8952 für 15 Seiten (index, rubrik, rubrik-2, artikel, termine,
kino, verzeichnis, verzeichnis-eintrag, einreichen, einreichen-danke, werben, buchen, kontakt, artikel-71,
artikel-37) bei 390, 820 und 1280: 45 Aufnahmen, 0 Fehler. Angesehen habe ich die ersten Bildschirme von index (390
und 1280), kino (390) und termine (1280). Dazu Messungen im Browser (Schriftgrößen, Bilder im ersten Bildschirm,
leere Zellen, Knöpfe) und Kontraste aus den Tokens. Ein frischer Paarvergleich mit Referenzbildern fand nicht statt
(siehe unten). Weil die Zeit begrenzt war, habe ich verzeichnis, werben, buchen, einreichen und kontakt nur
gemessen und nicht angesehen.

## Erster Eindruck
Die Hülle aus Runde 1 ist weg: kein Werbesatz mit Knopfpaar, kein dunkler Kino-Block, keine Mono-Ziffern, kein roter
Flächenknopf. Übrig ist das Kalenderblatt als Kopf jeder Seite, und das gehört erkennbar tamil.de: Tag, Fest, Verein,
Ort, „als Nächstes“, ein Stand-Datum. Das Risiko hat sich verschoben: Am Handy öffnen fünf der sechs Hauptseiten mit
Überschrift und Tabelle ohne ein einziges Bild. Die Seite wirkt dadurch gemacht und ordentlich, aber trocken, eher
wie ein Nachschlagewerk als wie ein Magazin.

## Harte Kriterien

| # | Kriterium (Brief v3, Linien-Auftrag) | Handy 390 | Desktop 1280 | Ergebnis |
|---|---|---|---|---|
| 1 | Logo unverändert | `bilder/logo.png` md5-gleich mit `design/inhalte/logo.png` | dto. | erfüllt |
| 2 | Nur Deutsch, keine tamilische Schrift als Schmuck | `tamil_ohne_lang` 0 auf 15 Seiten | dto. | erfüllt |
| 3 | Echte Inhalte | Stichprobe Kino, Termine, Festjahr, Kinojahr gegen `docs/redaktion/rueckblick-2026.md` und `rueckblick.json`: belegt; ein Ort fehlt (P3-2) | dto. | erfüllt |
| 4 | Bildnachweis sichtbar, am Bild | jetzt in jeder `figcaption` (index, termine, kino, rubrik, artikel) | dto. | erfüllt |
| 5 | Fließtext am Handy ≥ 18 px | Median der Absätze und Zellen 18 px auf allen 10 gemessenen Seiten | 18–20,5 px | erfüllt |
| 6 | Kontrast WCAG AA | aus den Tokens: Grau auf Grund 6,24:1, Grau auf Bogen 6,91:1, Rot (`accent-2`) auf Bogen 8,94:1, Logo-Rot auf Grund 5,58:1 | dto. | erfüllt |
| 7 | Tippflächen ≥ 44 px | Rest: `artikel.html` „Diwali in Basel, Aula Lysbüchel“ 278×23, `artikel-71.html` „Community“ 77×20, Dateifeld 224×34 (einreichen, kontakt), Checkboxen 24×24 | n. a. | verletzt (nach Bogen E P2-4) |
| 8 | Kein seitliches Scrollen 390/820/1280 | 0 px auf 15 Seiten | 0 px | erfüllt |
| 9 | `prefers-reduced-motion` | Regeln in `base.css` und `almanac.css` | dto. | erfüllt |
| 10 | Schriften selbst gehostet, OFL im Ordner | `schriften/hanken-grotesk-…woff2`, `OFL.txt`, `schriften` leer im Bericht | dto. | erfüllt |
| 11 | Keine Gedankenstriche | 3 Funde, alle in wörtlichen Eigennamen oder Zitaten (`artikel-48`, `-71`, `-83`) | dto. | erfüllt |
| 12 | Keine Dachzeilen, Versal-Labels, „·“-Metazeilen | 0 × `uppercase` oder Sperrung in den CSS-Dateien, keine Dachzeile gesehen | dto. | erfüllt |
| 13 | Keine gleich großen Kartenraster, Verlauf-Bildkacheln, Seitenstreifen | keine; `band--ink` wird in keiner Seite mehr benutzt | keine | erfüllt |
| 14 | Seitenliste vollständig | 11 Dateien plus `einreichen-danke.html`, `rubrik-2.html`, 19 Artikel | dto. | erfüllt |
| 15 | Kino „diese Woche nach Stadt“ | Stadtindex nach Ländern und Alphabet, Film zweitrangig; Lücken offen benannt (P2-2) | dto. | erfüllt |

Schriftgrößen (gemessen): H1 32 px am Handy und 40,2 px am Desktop auf allen Seiten, größte Schrift jeweils die H1.
Damit hält die Seite die Obergrenze aus `tamil-marke` (32/38, Aufmacher 34/44).

Hallmark (`sloplint --genre editorial`, statisch über 22 Dateien und mit Render über 11 Adressen):
**0 FAIL, 0 WARN, 141 WAIVED, 2 ANSWERED, 30 DISMISSED, 20 NOTE.** Hinweis: Der Render-Lauf schreibt seine
Aufnahmen nach `richtungen/hm-almanac/.hallmark/shots/`. Das hat dort die Bilder des Gestalters überschrieben.

## Stand der P1 aus Runde 1

| r1 | Befund | Stand r2 | Beleg |
|---|---|---|---|
| P1-1 | IBM Plex Mono für alle Ziffern | **behoben** | `--font-outlier` und `.num` jetzt Hanken Grotesk mit `tabular-nums lining-nums`; keine Mono-Datei in `schriften/` |
| P1-2 | Landingpage-Hülle (Werbesatz, Knopfpaar, „Beitrag lesen“) | **behoben** | H1 „Die nächsten Feste der Community“ aus dem Inhalt; 0 Knöpfe in `main` auf index, termine, kino, rubrik-Kopf; Teilen als Link. Rest: `rubrik.html` „Ältere Beiträge“ als Knopf neben der Seitenzahl 2 (P3-8) |
| P1-3 | Dunkler Kino-Block auf der Startseite | **behoben** | Kino steht auf dem hellen Bogen (`.kino-blatt`), `band--ink` ist nirgends mehr in Gebrauch |
| P1-4 | Kino nicht nach Stadt | **behoben, mit Rest** | `kino.html` beginnt mit „Spielorte ab 9. November“, Städte nach Land und Alphabet. „OM“ (12 Spielorte) steht in keiner Stadtzeile, siehe P2-2 |
| P1-5 | Ungleicher Abstand Kopf → erster Block, H1 unter dem Blatt | **behoben** | Token `--space-head-after` (40 px) in allen Kopfzeilen; die H1 der Startseite steht über dem Blatt (y 158, Blatt ab y 286 bei 1280) |

**Verdecken die Ausnahmen im Stempel Befunde?** Ich habe jede Ausnahme gegen das Bild und die Messung gelesen.
Keine verdeckt einen Floor-Verstoß oder ein P1:
- *waive 78* (Abschnittsköpfe unter 40 px) folgt aus der Obergrenze der Marke (44 px). Das ist berechtigt.
- *waive 49b* (umbrechende Links) betrifft die Titel der Berichte. Das ist berechtigt.
- *waive 59* (40 px Kopf → Blatt) ist genau die Behebung von r1 P1-5. Das ist berechtigt.
- *waive 44c* auf der Startseite verdeckt eine kleine Unruhe: Die rechte Spalte endet bei 1280 auf y≈705, der Bogen
  auf y≈790. Danach folgen rund 177 px Leere bis zum Kino-Bogen (P3-6). Das ist kein P1.

Vier Punkte sind Buchhaltungsfehler (P3-4):
- `job: listen` steht auf fünf Seiten. Das ist der Job für Podcast und Musik, nicht für ein Magazin („lesen,
  finden, teilen“). Damit lief die Prüfung der Anatomie (Gate 85, `anatomy.md`) gegen die falsche Kategorie.
- `dismissed 52` in `werben.css` nennt eine stillgelegte Gate-Nummer (`gates.md` § 1: „retired numbers stay
  retired“).
- `almanac.css` hat den Stempel, aber keine Zeile mit der Selbstkritik (Floor 15).
- sloplint meldet selbst, dass vier Reflex-Gates auf jeder Seite ausgenommen sind (44c, 59, 78, 49b). Das ist ein
  Hausstil, der in eine `design.md` gehört.

## Paarvergleich (390 px, erster Bildschirm)

Diese Runde gab es keinen frischen Vergleich mit den Referenzbildern. Die Maße der Vorbilder stammen aus r1, der Blick
auf die Probe ist neu.
- **NZZ (Handy):** Bei der NZZ folgt direkt unter der Navigation ein Foto von 356 px Höhe. Bei hm-almanac steht dort
  eine H1 von 32 px, eine Unterzeile und ab y 358 der Bogen mit fünf Terminzeilen. Das erste Foto beginnt bei
  y≈1110, also auf dem zweiten Bildschirm. Ordnung und Satz der Probe sind gleichwertig: Linien in zwei Stärken,
  rechte Winkel, eine Schrift, gleiche Zeilenabstände. Was fehlt, ist das Bild.
- **Spiegel (Handy):** Der Spiegel zeigt im ersten Bildschirm drei Geschichten. Die Probe zeigt fünf Termine und keine
  Geschichte. Für die Aufgabe „finden“ ist das stärker, für „lesen“ schwächer.
- **Runde 2 (Community-Magazin):** R2 hat Creme-Grund, Pillen, ein abgerundetes Bild und eine Anzeige oben. Die Probe
  hat einen kühlen Grund (oklch 95,5 % / Hue 245), keine Rundung, keine Pillen und keine Anzeige. Der Abstand ist
  klar.
- **Runde 4 (Raster):** R4 hat ein rotes Riesenwort, Extraschmal-Schrift und Plakatzahlen. In der Probe ist nichts
  davon geblieben. Die Kino-Zahlen stehen in Lesegröße in der Tabellenspalte, Rot nur in „als Nächstes“, in Links
  und in der Heute-Marke der Zeitleiste.
- **Die vier Punkte aus Runde 4:**
  - zu laut: nein (größte Schrift 40 px, kein Rot als Fläche);
  - Baukasten: nein (keine Kästen um Anreißer, keine Pillen, kein Kartenraster);
  - Schrift: eine Familie, ruhiger Satz;
  - wertig: ja, mit den Abstandsresten aus P3-6.
- **Gegenrisiko „zu classic / trocken“:** Diesen Punkt hat Luis bei `klar` gerügt. Er trifft hier am Handy zu, siehe
  P2-1.

## Befunde

### P0
Keine. `bericht.json`: 0 Fehler, 0 Konsolenfehler, 0 leere Bilder, 0 px Überlauf (15 Seiten × 3 Breiten).

### P1
Keine offenen. Alle fünf P1 aus r1 sind behoben (Tabelle oben).

### P2
1. **Kein Bild im ersten Handy-Bildschirm der Hauptseiten** (offener Rest von r1 P2-2). Gemessen bei 390 × 844:
   0 Bilder auf index, termine, kino, verzeichnis und werben. Bei 1280 × 800 hat nur index ein Bild. Am Handy, dem
   Hauptgerät laut Brief v3, sieht man fünf Mal hintereinander Überschrift plus Tabelle. Hallmark verlangt: „a page
   with pictures leads with them“. Das Material hat 20 Fotos mit Nachweis.
   *Abhilfe:* Auf der Startseite bei 390 den ersten Bericht mit Foto zwischen Kopf und Bogen setzen oder ein
   schmales Bild (16:9) an die Zeile „als Nächstes“ hängen. Auf termine und kino ein Bild aus dem zugehörigen
   Bericht unmittelbar nach dem ersten Bogen.
2. **Stadtindex Kino mit großen Lücken** (`kino.html`).
   - „OM“ läuft laut Quelle an 12 Spielorten, steht aber in keiner Stadtzeile.
   - Bei „Scene“ fehlen 6 von 11 Städten.
   - Die Spalte „Kino und Termin“ ist bei 1280 in 7 von 8 Zeilen leer.
   - Bei 390 besteht der erste Bildschirm aus fünf Zeilen „Berlin / „Scene““, „Bremen / „Scene““ usw.

   Die Fußzeile des Bogens benennt die Lücke ehrlich, sieht aber wie ein unfertiger Datenexport aus.
   *Abhilfe:* Die leere Spalte entfallen lassen. Die Orte von „Scene“ in einer Zeile zusammenfassen („Berlin, Bremen,
   Chemnitz, Dortmund, Düsseldorf“). „OM“ als eigene Zeile führen („Deutschland, 12 Spielorte, Orte folgen“), mit
   einem sichtbaren Platzhalter.
3. **Rubriken im Fuß führen ins Leere** (alle Seiten, `foot__col` „Rubriken“). „Nachrichten“, „Kultur“, „Küche“ und
   „Sport“ verlinken alle auf `index.html#jahr`. Vier Rubriken täuschen Ziele vor, die es nicht gibt.
   *Abhilfe:* Nur Rubriken mit eigener Seite verlinken, die anderen als Platzhalter („Rubrikseite folgt“)
   kennzeichnen oder weglassen.
4. **Tippflächen unter 44 px** (Bogen E, Rest von r1 P2-1). Bei 390:
   - `artikel.html` „Mehr zu Tempeln und Festen“, Link „Diwali in Basel, Aula Lysbüchel“: 278×23
   - `artikel-71.html` „Community“: 77×20
   - Dateifeld in `einreichen.html` und `kontakt.html`: 224×34
   - Checkboxen: 24×24 (die Beschriftung ist anklickbar, deshalb nur Hinweis)

   *Abhilfe:* `.weiter__liste a` und den Rubrik-Link wie die Tabellenlinks mit `padding-block` auf 44 px bringen,
   das Dateifeld auf `min-height: 48px`.
5. **15 px als Erklärtext** (Rest von r1 P2-6, nur gemessen, nicht angesehen). `--text-sm` ist jetzt 15 px und trägt
   weiter Notizen, Stand-Angaben, Bildnachweise und auf `buchen.html` Teile der Erklärung. Der Median liegt bei 18 px,
   aber `buchen.html` hat bei 390 und 1280 16 leere Tabellenzellen und den dichtesten Text der Seite (473 Wörter).
   *Abhilfe:* Erklärende Sätze auf `buchen.html` in `--text-md`, 15 px nur für Tabellenköpfe und Nachweise. Dabei
   prüfen, ob die leeren Zellen gewollte Kalenderfelder sind.

### P3
1. `index.html` und `termine.html`: Bei THADAM ist die Zelle „Wer“ leer. An anderen Stellen kennzeichnet die Probe
   Lücken („ohne Ortsangabe“, „ohne Datum“). *Abhilfe:* „Veranstalter nicht genannt“ eintragen.
2. `termine.html` Zeitleiste: „Kalaiththiran, Göttingen, Stuttgart“. Laut Rückblick (Story 65) waren es Göttingen,
   Mönchengladbach und Stuttgart. *Abhilfe:* Den Ort ergänzen oder auf „drei Städte“ kürzen.
3. `termine.html` Unterzeile „Elf Feste aus dem Rückblick, … bis THADAM in Bern“: THADAM steht nicht im Rückblick,
   sondern ist ein wartender Radar-Entwurf. Dasselbe gilt für „OM“ und „Jailer 2“: Sie sind noch nicht freigegeben,
   werden aber als feste Angaben gezeigt. Für eine Probe ist das tragbar, vor dem Livegang muss es geklärt werden.
4. Stempel-Buchhaltung, siehe oben: `job: listen`, `dismissed 52` (stillgelegte Nummer), die fehlende Zeile mit der
   Selbstkritik in `almanac.css` und vier Hausstil-Ausnahmen ohne `design.md`. *Abhilfe:* `job: read` oder
   `job: find` setzen, die Zeilen bereinigen und die Ausnahmen in eine `design.md` übernehmen.
5. Die Zeitleiste „Das Festjahr 2026“ (termine) habe ich bei 390 nicht angesehen. Bei 1280 stehen die Beschriftungen
   eng, „heute“ liegt dicht an „08.11.“ und „13.12.“. Das sollte bei 390 und mit 200 % Zoom geprüft werden.
6. Leere Flächen bei 1280:
   - index: rund 177 px zwischen dem Ende des Bogens (y≈790) und dem Kino-Bogen, dazu endet die rechte Spalte schon
     bei y≈705;
   - termine: rund 145 px zwischen Bogen und „Das Festjahr 2026“.

   *Abhilfe:* Den Abstand zwischen den Abschnitten auf diesen beiden Seiten auf `--section-gap-s` setzen.
7. Das Bild der Startseite (Sri-Ganesha-Tempel, Juni 2026) zeigt kein Deepavali. Der Rückblick vermerkt „gleiches
   Tempelbild wie Story 49“, und in `rubrik.html` steht dasselbe Foto bei Story 49. *Abhilfe:* Vor dem Livegang ein
   eigenes Bild suchen.
8. `rubrik.html`: Der Knopf „Ältere Beiträge“ steht neben der Seitenzahl „2“ und verdoppelt sie.
   *Abhilfe:* Ein Weg genügt.
9. Nicht erneut geprüft (r1 P3-4 bis P3-6): die Schrittleiste von `buchen.html` bei 390, das Datumsformat der
   Formulare in `de-DE` und eine Vorschau „so erscheint Ihr Termin“ auf `einreichen.html`.

## Was trägt
- **Das Kalenderblatt als Kopf jeder Seite.** Tag, Fest, Wer, Wo, „als Nächstes“ in Rot zwischen zwei kräftigen
  Linien, vergangene Einträge grau, das Stand-Datum. Das ist Inhalt von tamil.de, kein Effekt, und es macht
  „finden“ und „teilen“ (WhatsApp-Link je Zeile) sofort möglich.
- **Die Disziplin nach r1.** Eine Schriftfamilie, Rot nur als Zeichen, keine Knöpfe im Lesefluss, rechte Winkel,
  zwei Linienstärken, Schlagzeilen innerhalb der Obergrenze. Nichts davon erinnert an die Runden 1 bis 7.
- **Die Zeitleiste „Festjahr 2026“** mit der Marke „heute“ und den verlinkten Berichten. Sie ist das einzige Element,
  das wirklich nach Gestaltung aussieht, und ist dabei ein echtes Datenbild.

## Bedienbarkeit (nur zur Information)

| Heuristik | 0–4 | Satz |
|---|---|---|
| 1 Sichtbarkeit des Status | 3 | Stand-Daten und „als Nächstes“ sagen, wie aktuell es ist. |
| 2 Übereinstimmung mit der Welt | 3 | Kino jetzt nach Stadt, Feste nach Datum, Alltagssprache. |
| 3 Kontrolle und Freiheit | 3 | Klare Hauptnavigation; die Rubriken im Fuß führen auf denselben Anker. |
| 4 Konsistenz | 3 | Ein Kopf, ein Bogen, ein Teilen-Link auf allen Seiten; Lücken werden nicht überall gleich gekennzeichnet. |
| 5 Fehlervermeidung | 3 | Pflichtfelder erklärt, vergangene Tage gesperrt (aus r1, nicht erneut geprüft). |
| 6 Wiedererkennen statt Erinnern | 3 | Tag, Was, Wer, Wo wiederholen sich auf allen Seiten. |
| 7 Flexibilität | 2 | Kein Weg zur eigenen Stadt für „OM“; Verzeichnisfilter vorhanden. |
| 8 Ästhetik und Reduktion | 3 | Reduziert und ruhig, am Handy aber ohne Bild. |
| 9 Fehler erkennen | n. g. | Fehlerzustände der Formulare nicht geprüft. |
| 10 Hilfe | 3 | Quellenhinweise unter den Bögen, Ablauf der Buchung erklärt. |
