# Startseiten-Proben: was gebaut ist

Stand 22.11.2026, Theme 3.16.0. Auftrag: Masterplan von Luis vom 21.11.2026, Teil B (TML-W06). Bauvorgabe:
`entwurf.md` in diesem Ordner. Das sind drei Proben zum Vergleichen, keine Entscheidung; Luis wählt.

## Aufruf

- Schalter: Customizer „Tamil.de → Startseite → Startseiten-Proben“ (Standard aus), oder
  `wp eval "set_theme_mod( 'tamil_startseiten_proben', '1' );"`. Aus: `wp eval "remove_theme_mod( 'tamil_startseiten_proben' );"`.
- Adressen: `/?probe=cover`, `/?probe=news`, `/?probe=community`. Schalter aus oder anderer Wert: die normale
  Startseite, gleiche Ausgabe wie vor dem Einbau (verglichen mit der Vorlage aus 3.15.0).
- Probenseiten: `noindex`, Canonical auf die Startseite, `Cache-Control: no-store`, nirgends verlinkt. Oben steht eine
  schmale Zeile „Probe: Cover First, News First, Community First, normale Startseite“ (am Handy kurz: Cover, News,
  Community, normal). Auf der normalen Startseite gibt es sie nicht.

## Gemeinsam

- Vorrat für den ersten Abschnitt sind die acht Beiträge, die `tamil_start_auswahl()` dafür schon reserviert
  (Aufmacher, vier Nebenstücke, drei Meldungen), nach Datum absteigend. Kein eigener Zwischenspeicher, keine Dubletten
  mit dem Rest der Seite.
- Jeder Beitrag ist eine Bildkarte aus `tamil_anr_imbild()`, `tamil_grafik_kino()` oder `tamil_grafik_termin()`: Titel
  im Bild, Punktbogen unten rechts, Schild „Symbolbild“ wo nötig. Der Text neben oder unter der Karte (`.kontext`: Ort,
  Termin, Quelle, ein Satz oder der Vorspann) steht im selben Link und zeigt nur gepflegte Felder.
- Farben, Radien, Schrift, Verläufe: nur Vorhandenes. Neu sind zwei Formatklassen (`.r1610`, `.r32`).
- Werbeplätze nach F3 unverändert: Leaderboard nach den Rubrikkacheln, Billboard nach „Küche“, Fuß, Handy-Leiste.
  Keine Verschiebung nötig.
- Der Wow-Aufmacher bleibt in Cover First und News First aus.

## Cover First (`/?probe=cover`)

- Cover = Aufmacher der Startseite; hat er nur ein Symbolbild aus dem Pool, rückt der erste Beitrag mit eigenem Foto
  aus dem Vorrat nach vorn. Format: Handy 4:3 randlos, Tablet 16:10, Desktop 16:10 (Original mindestens 1,6 : 1) oder
  3:2 (sonst, und immer bei Titeln über 90 Zeichen). Titel `clamp(28px, 22px + 1.52vw, 44px)`, Stufen × 0,9 und × 0,8.
- Kontextfeld unter dem Cover: „Titelgeschichte“ (ab 600 px), Ort, Termin (nur bei Terminen), Quelle, am Desktop das
  Erscheinungsdatum; daneben der Vorspann (Handy: zwei Zeilen).
- Drei Beistücke: B1 4:3, B2 16:9, B3 8:3. B1 und B2 zuerst mit Foto, dann mit eigenem Bild; B3 bevorzugt ein breites
  Bild oder Symbolbild. Gleiche Rubrik und gleiches erstes Titelwort stehen nicht nebeneinander. Am Tablet stehen die
  drei in einer Reihe, gleich hoch, 2 : 1,5 : 1,5.
- Die übrigen vier als Reihe „Weitere Meldungen“ (Handy wischbar wie die Rubrikblöcke), dann die Rubrikkacheln.

## News First (`/?probe=news`)

- `<ol class="zeitfolge">` mit den fünf neuesten Beiträgen des Vorrats: Zeit und Rubrik neben dem Bild, Bildkarte nur
  mit Titel, daneben Ort, ein Satz, Quelle. Erste Zeile größer (16:9, 22 px), die übrigen am Handy 8:3, ab 600 px 16:9.
- Blocktitel „Heute wichtig“ nur, wenn ein Beitrag der Zeitfolge von heute ist, sonst „Zuletzt erschienen“. Zeit:
  „Heute, 19:43 Uhr“, „Gestern, 19:43 Uhr“, älter nur das Datum.
- Rechts (Handy: darunter) das Cover kleiner (Desktop 4:3, sonst 16:9) mit Ort, Quelle und Vorspann, dann die zwei
  ältesten Beiträge (16:9 und 8:3; am Tablet nebeneinander).

## Community First (`/?probe=community`)

- „Tamil in meiner Stadt“ steht ganz oben; danach folgt der erste Abschnitt der Startseite aus `front-page.php`
  unverändert (gleiche Beiträge in gleicher Reihenfolge, per Test geprüft).

## „Tamil in meiner Stadt“ (alle drei; bei Cover und News nach dem Leaderboard, vor „Diese Woche“)

- Daten (`tamil_stadt_daten()`): Kino aus `tamil_kino_filme( 6 )`, je Kino nur mit Vorstellung ab heute; Termine aus
  `tamil_site_upcoming_events( 12 )`; Geschichten: die 24 neuesten Beiträge mit „Ort der Meldung“, ohne die Beiträge
  des ersten Abschnitts, von „Diese Woche“ und ohne die Filme und Termine des Abschnitts selbst, Community zuerst.
  Städte aus Freitext zerlegt (`tamil_stadt_namen()`), ohne Länder, Kantone, Klammern, Postleitzahlen, Einrichtungen.
  Eine Stadt kommt in die Auswahl mit einer Vorstellung, einem Termin oder zwei Geschichten. Kein Verzeichnis.
- Bedienung: echtes `<select>` mit „Alle Städte“, Titel wird „Tamil in {Stadt}“, Statuszeile für Vorleseprogramme
  (`aria-live`). Gespeichert wird nur im `localStorage` (`tamil_stadt`); `try/catch` um jeden Zugriff. Ein kleines
  Skript direkt hinter dem Abschnitt wendet die gespeicherte Stadt vor dem ersten Malen an (`stadt-start.js`,
  eingebettet); `stadt.js` (defer, nur auf Probenseiten) bedient das Feld.
- Ohne Skript: Zustand „Alle Städte“, kein Auswahlfeld, Links „Kino nach Stadt“ und „Alle Termine“.
- Sichtbar: höchstens zwei Filme, zwei Termine, drei Geschichten (Bühne wie die Küche: die erste groß 16:9, die
  übrigen 8:3). Mit Stadt steht unter dem Film je Kino die Zeile „Kino, Termin“ mit „Tickets und Zeiten“.
- Leerzustände als Satz mit Link, Wortlaut nach Kapitel 3.5 der Vorgabe; gibt es gar nichts, entfällt der Abschnitt.

## Abweichungen von der Vorgabe

- **Kein eigener Zwischenspeicher** für `tamil_stadt_daten()` (Vorgabe: Transient). Die Daten werden je Aufruf einer
  Probenseite gerechnet (drei Abfragen), damit zwischen Probe und normaler Seite nichts verwechselt werden kann.
- **Inhaltsbreite 1200 statt 1280 px.** Das Theme setzt `.innen` am Desktop auf 1200 px. Das Cover ist deshalb
  780 px breit (Vorgabe 860), die Zeitfolge 700 px, die Spalte rechts in News First 487 px (Vorgabe 520).
- **Umschalter über dem Inhalt** (44 px hoch) schiebt den ersten Bildschirm nach unten. Er gehört zur Probe, nicht
  zum Entwurf; die Messwerte unten enthalten ihn.
- **Zeitspalte der Zeitfolge 100 bzw. 104 px** statt 72 bzw. 76 px: „18. Oktober 2026“ bricht sonst in drei Zeilen.
- **Fachtitel als `<h3>`, Karten darunter `<h4>`** (Vorgabe: Karten `h3`), damit die Gliederung stimmt.
- **Leerzustand als Satz plus Link:** Der Wortlaut ist der aus Kapitel 3.5; der zweite Satz ist jeweils der Link.
- **Eine einzige Karte in der Reihe Kino/Termine (ab 600 px):** Die Karte bekommt die halbe Breite (höchstens 516 px)
  und die Sätze zu den leeren Fächern stehen daneben statt darunter; sonst bliebe rechts ein Loch.
- **Zwei Geschichten in „Aus der Stadt“** stehen gleich groß nebeneinander (beide 16:9 mit Satz), statt groß neben
  einer hochgezogenen kleinen.
- **Geschichten ohne erkennbare Stadt** (Ort nur „Deutschland“, „Kanton Solothurn“) erscheinen unter „Alle Städte“
  mit ihrem Ort, wie eingegeben, aber in keiner Stadt.
- **Stadtwechsel:** Der Inhalt blendet 160 ms um; die Reihe hält ihre Höhe dabei nicht fest (nach dem Wechsel kann
  der Abschnitt kürzer oder länger sein).
- **Cover-Tablet immer 16:10** (wie in der Vorgabe skizziert); die Regel 16:10 oder 3:2 greift ab 1024 px.
- **Datum im Kontextfeld des Covers nur am Desktop** (es steht schon in der Dachzeile im Bild); „Titelgeschichte“
  erst ab 600 px (am Handy zählt die Höhe).
- **Symbolbilder können sich verschieben:** Der Abschnitt gibt bis zu 24 Geschichten ins HTML (verborgen bis zur
  Stadtwahl). Beiträge ohne eigenes Bild belegen dabei Bilder aus dem Rubrik-Pool; weiter unten auf der Seite kann
  deshalb ein anderes Symbolbild stehen als auf der normalen Startseite.
- **Nebenbefund 10 der Vorgabe** (fehlgeschlagene Bildanfragen `…-300x169`): lokal nicht aufgetreten, `shots.mjs`
  meldet 0 Fehler; auf dem Testsystem nicht geprüft.

## Messwerte (lokal, 22.11.2026, mit Umschalter; Daten des lokalen WordPress, 78 Beiträge)

| Probe | Breite × Höhe | ganz sichtbare Titel im ersten Bildschirm | Maße |
|---|---|---|---|
| Cover First | 390 × 844 | 2 (Cover, B1; B1-Titel endet bei 841 px) | Cover 390 × 293, Titel 4 Zeilen; B1 358 × 269, B2 358 × 201, B3 358 × 153 |
| Cover First | 820 × 1180 | 4 | Cover 772 × 483; Beistücke 296 / 222 / 222 breit, je 220 hoch |
| Cover First | 1280 × 800 und 1440 × 800 | 3 (Cover, B1, B2; B3 endet bei 935 px) | Cover 780 × 488 (16:10), Titel 3 Zeilen; B1 388 × 291, B2 388 × 218, B3 388 × 146 |
| News First | 390 × 844 | 2 (Z1, Z2) | Z1 358 × 201, Z2 358 × 134 |
| News First | 1280 × 800 und 1440 × 800 | 3 (Z1, Z2, Cover; Z3 endet bei 889 px) | Z1 380 × 214, Z2 280 × 158, Cover 487 × 365 |
| Community First | 390 × 844 | 2 (Film, erster Termin), dazu Abschnittstitel und Auswahlfeld | Feld 306 × 48 |
| Community First | 1280 × 800 und 1440 × 800 | 3 (Film, zwei Termine) | Aufmacher beginnt bei 1223 px |

Gegen die Prüfliste der Vorgabe **nicht erreicht**:
- Cover First: Coverfläche am Desktop 3,4-mal B1 (Soll mindestens 4): Folge der Inhaltsbreite 1200 px.
- News First bei 1280 × 800: zwei Zeilen und das Cover ganz sichtbar, nicht drei Zeilen (Soll vier Titel). Die Maße
  der Vorgabe (Z1 214 hoch, Zeilen je 158 + Abstand) ergeben auch ohne Umschalter mehr als 800 px.
- Community First bei 1280 × 800: drei Titel statt vier; die Bühne „Aus der Stadt“ beginnt darunter.
- Kontrast der hellen Schrift im Bild und „nur Farbwerte aus den Tokens“ sind nicht gemessen worden; die Karten nutzen
  die vorhandenen Verläufe und Variablen.

Prüfungen (alle mit den drei Proben als weitere Pfade): `tools/shots.mjs` bei 390, 820, 1280, 1440 je 0 Fehler (kein
seitliches Scrollen, Konsole sauber); `bilder_pflicht.mjs` 0 ohne Bild, Punktbogen 100 %, Titel im Bild 100 %;
`kartenhoehe.mjs` 195 Reihen, 0 uneben; `ueberdeckung.mjs` keine Überdeckung. Stadtwahl im Browser: Fokus bleibt auf
dem Feld, kein Cookie, keine Anfrage, keine Standortabfrage, nach Neuladen steht die Stadt ohne Verschiebung
(CLS 0), ohne JavaScript „Alle Städte“ mit beiden Links.

## Datenlage lokal

Auswahl: Basel, Bremen, Dortmund, Graz, Karlsruhe, Kloten, Wien. Ein Film mit Vorstellung ab heute („Jailer 2“, fünf
Kinos), zwei Termine mit Stadt (Basel, Kloten), zwei Geschichten mit Ort, aber keine davon in einer Stadt der
Auswahl. Jede Stadt zeigt deshalb genau ein gefülltes Fach und zwei Sätze. Der Zustand „Stadt mit Kino, Termin und
Geschichten“ kommt lokal nicht vor und ist nicht im Bild geprüft; „Heute wichtig“ ist nur im Test (mit zwei
Testbeiträgen von heute) gesehen worden, die lokalen Beiträge sind vom Oktober.

## Offene Fragen an Luis

Die Fragen 1 bis 5 aus `entwurf.md` (Kapitel 6) sind unverändert offen.
