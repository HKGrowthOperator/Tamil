# Prüfung hm-aushang, Runde 3
Harte Kriterien: 14 von 15 erfüllt · P0: 0 · P1: 1 · P2: 6 · P3: 7

Grundlage: `design/brief-v3.md`, `design/linien-auftrag.md`, `abgelehnt.md` (Runden 1–7), Pflichten aus `tamil-marke`,
Kritik Runde 2 (`hm-aushang-r2.md`). Gemessen am 13.11.2026 über http://127.0.0.1:8956/richtungen/hm-aushang/ mit
`tools/shots.mjs --kacheln` (index, termine, kino, artikel, rubrik; je 390/820/1280), `sloplint --genre editorial`
mit je einem `--url` pro Seite (fünf Seiten) und einem eigenen Messskript (berechnete Schriftgrößen, Lagen und
Rasterspalten der Zettel). Angesehen: erster Bildschirm von index, termine, kino bei 390 und 1280, artikel bei 390,
dazu index 390 und 1280 zweiter Bildschirm und rubrik 390 „Feste der Gemeinden“. `begruendung.md` nicht gelesen.
Nicht neu geprüft: verzeichnis, verzeichnis-eintrag, einreichen, werben, buchen, kontakt (Stand aus r2 übernommen,
wo vermerkt). Die Quelle „Eventfrog“ für die Uhrzeit von „Jailer 2“ gilt laut Auftrag als belegt.

## Erster Eindruck
Die Startseite ist ruhiger und geschlossener als in Runde 2: Aufmacher links, „Am Brett“ rechts, die Termine stehen
jetzt als Zeilen zwischen Haarlinien, die Mitnahmen sind Textlinks unter einer gestrichelten Linie, und die
Aufmacher-Schlagzeile ist wieder die größte Schrift. Auf `termine` und `rubrik` bei 390 kippt derselbe Zettel aber
in ein zweispaltiges Raster mit einer 134 px schmalen Textspalte; Titel, Ort und Mitnahmen brechen dort Wort für
Wort um, auf `termine` schon im ersten Bildschirm. Unter der Falz der Startseite bleiben bei 1280 die großen Lücken
neben den Meldungslisten.

## Messwerte

| Wert | Handy 390 | Desktop 1280 |
|---|---|---|
| Aufmacher-Schlagzeile H1 (index) | 32 px / 700, 3 Zeilen | 49,9 px / 700, 3 Zeilen |
| H1 Unterseiten (termine, kino, rubrik / artikel) | 32 px / 30 px | 49,9 px / 39,2 px |
| Abschnittstitel H2 („Nachrichten“, „Am Brett“ auf termine) | 24 px | 30,4 px |
| „Am Brett“ auf index (`.brett-titel`) | 22 px | 27,8 px |
| Titel Zweitgeschichte, Filmtitel, Spaltentitel (H3) | 22 px | 27,8 px |
| Zettel- und Meldungstitel (H3) | 19 px | 21,8 px |
| Fließtext / kleinste Schrift | 19 px / 15 px (artikel 14 px) | 20,6 px / 15 px |
| Schriftfamilien | 1 (Epilogue, selbst gehostet) | 1 |
| Zettel-Raster index, artikel | eine Spalte, 358 px | eine Spalte, 467 px (Randspalte) |
| Zettel-Raster termine, rubrik | **zwei Spalten, 208 px + 134 px** | zwei Spalten, 208 px + 720 px |
| „Hängt noch“ (alle Zettel, alle Seiten) | immer unter dem Datum, x wie Datum | dto. (index x 749, termine x 64) |
| Zweite Geschichte im ersten Bildschirm (index) | Zettel-Datum y 723, Titel y 782 (Falz 844) | drei Zettel, dritter Titel y 720 (Falz 800) |
| Seitenlänge index / termine | 7249 px / 10863 px | 5195 px / 7951 px |
| Überlauf seitlich | 0 px (5 Seiten) | 0 px (auch 820) |
| Konsolenfehler / leere Bilder / Schriftfehler | 0 / 0 / 0 | 0 / 0 / 0 |
| Tippflächen < 44 px (`bericht.json`) | 0 bei 390 | bei 820: 4 Bildnachweis-Links mit 40 px (index 2, artikel 1, rubrik 1) |
| sloplint (5 Seiten, 5 URLs) | 0 FAIL, 7 WARN (1× F15 Spaltenabstände 64/24/40 px, 1× F21 h1→h3 in artikel, 5× Schrift-Fallback im eigenen Render), 91 WAIVED, 5 DISMISSED, 15 NOTE | |

Hinweis zur Messung: Ein erster sloplint-Lauf mit kommagetrennten Adressen meldete 1 FAIL („HTTP 404“), weil das
Skript nur eine Adresse je `--url` annimmt; das ist ein Bedienfehler der Prüfung, kein Befund. Der zweite Lauf mit
fünf `--url` ist maßgeblich.

## Harte Kriterien

| # | Kriterium (brief-v3, linien-auftrag) | Handy 390 | Desktop 1280 | Ergebnis |
|---|---|---|---|---|
| 1 | Logo unverändert | `bilder/logo.png`, 44 px hoch | dto., 48 px | erfüllt |
| 2 | Nur Deutsch, keine tamilische Schrift als Schmuck | `tamil_ohne_lang` 0 | dto. | erfüllt |
| 3 | Echte Inhalte, nichts erfunden | Jailer 2 „17 Uhr“ mit sichtbarer Quelle Eventfrog (laut Auftrag belegt); Festkalender ohne Nachrichten | dto. | erfüllt |
| 4 | Bildnachweis an jedem Bild | am Bild, verlinkt | dto. | erfüllt |
| 5 | Fließtext Handy ≥ 18 px | 19 px | 20,6 px | erfüllt |
| 6 | Kontrast AA | Tokens wie r2: ink 16 %, ink-2 28 %, muted 44 % L auf paper 99,4 %; Rot 50,8 % L (≥ 6:1) | dto. | erfüllt (gerechnet) |
| 7 | Tippflächen 44 px | 0 Treffer bei 390 auf 5 Seiten | bei 820 Bildnachweis-Links 40 px | **verletzt** (wie r2 nach Bogen E als P2-1) |
| 8 | Kein seitliches Scrollen | 0 px | 0 px | erfüllt |
| 9 | `prefers-reduced-motion` | Block in `base.css` | dto. | erfüllt (im Code) |
| 10 | Keine Dachzeilen, Versal-Labels, „·“-Metazeilen, keine Gedankenstriche | keine; kein „·“, „–“ oder „—“ im Text der fünf Seiten; Metazeilen mit Komma („Berlin, 17. August 2026“) | dto. | erfüllt |
| 11 | Keine gleich großen Kartenraster, Verlaufkacheln, Seitenstreifen | Zettel ohne Rahmen und Rundung, Zeilen zwischen Haarlinien | termine eine Spalte, `max-width: 60rem` | erfüllt |
| 12 | Nichts aus Runden 1–7 wiederholt | kein Band, keine Fläche in Rot, keine Pillen, keine Knopfreihe | dto. | erfüllt |
| 13 | Schriften selbst gehostet, OFL im Ordner | `schriften/epilogue-latin(-ext)-wght-normal.woff2`, `Epilogue-OFL.txt` | dto. | erfüllt |
| 14 | Seitenliste vollständig | 11 Seiten, Danke-Zustand, 19 Artikel, 12 Profile | dto. | erfüllt |
| 15 | Keine Konsolenfehler, keine leeren Bilder | 0 / 0 | 0 / 0 | erfüllt |

## Stand der P1 aus Runde 2

| r2 | Befund | Stand r3 |
|---|---|---|
| P1-1 | Zettel als Kartenraster mit Knopfleiste | **behoben** für den Kasten: kein Rahmen, keine Rundung, Trennung nur durch Haarlinien (`.zettel { border-bottom: 1px solid rule }`); Mitnahmen als Textlinks hinter „Mitnehmen:“ unter einer gestrichelten Linie (`.abriss`), 44 px hoch; termine 1280 eine Spalte statt drei. **Neu entstanden** ist das zweispaltige Zettel-Raster am Handy, siehe P1-1 unten. |
| P1-2 | Uhrzeit „Jailer 2“ ohne Quelle | **behoben** nach Vorgabe: „Quelle: Eventfrog“ steht am Zettel (index, termine) und in der Kino-Zeile. Die `.ics` ist ehrlicher als in r2 (keine erfundene Dauer, keine Zeitzone ohne VTIMEZONE), siehe P3-1. |
| P1-3 | Hierarchie und Satz der Titel am Handy | **behoben.** H1 index 32 px ist jetzt die größte Schrift (H2 24, H3 22 und 19 px); bei 1280 H1 49,9 > H2 30,4 > H3 27,8. `hyphens: auto` an h1–h3; „Bundestagsdrucksache:“ bricht bei 390 nicht mehr im Wort. Rest: „Am Brett“ 22 px gegen andere H2 24 px (P3-2). |
| P1-4 | „Hängt noch“ in wechselnder Lage | **behoben.** `.zettel-kopf` ist ein Raster; „Hängt noch“ steht auf allen drei Zetteln direkt unter dem Datum (index 1280: y 215/453/692, jeweils x 749). |

Aus r2 P2 zusätzlich: P2-4 (Nachrichten im Festkalender) **behoben**, keine Asyl-, Visa- oder Drucksachen-Meldung
mehr auf termine, Unterzeile jetzt „aus den Beiträgen 2026, noch nicht freigegeben“; P2-6 (`.ics` ohne VTIMEZONE)
**entfallen**; P2-3 (dreimal dieselbe Form unter der Falz) **teilweise**: Community setzt Liste links, Bild rechts.
Weiter offen: P2-1 Tippflächen (820), P2-2 Lücken bei 1280, P2-5 Spaltenabstände.

## Paarvergleich

Nur gegen Runde 2 dieser Linie; die Referenzbilder sind nicht neu nebengelegt (brief-v3 misst nicht mehr gegen
Nachrichtenmarken).

- **index 1280, „Am Brett“ r2 gegen r3:** r2 drei gerahmte Kästen mit 6 px Rundung und 48 px hoher Knopfleiste,
  „Hängt noch“ einmal rechts, einmal darunter. r3: Zeilen zwischen Haarlinien in derselben Linienordnung wie die
  Meldungslisten, Datum, „Hängt noch“, Titel, Ort in fester Folge; drei Termine enden bei y ca. 855 statt 797, der
  dritte Titel bleibt bei y 720 über der Falz. Die rechte Spalte liest sich jetzt als Teil derselben Seite.
- **Titelordnung 390 r2 gegen r3:** r2 Zweitgeschichte 31,2 px über H1 30 px; r3 H1 32 px, Zweitgeschichte 22 px,
  Zettel 19 px. Der Blick landet zuerst auf dem Aufmacher.
- **termine 390 gegen index 390 (gleiche Runde):** Auf index ist der Zettel eine Spalte über 358 px, Titel in zwei
  Zeilen; auf termine derselbe Zettel in 208 + 134 px, Titel „Deepavali-/Feier des/Düsseldorf/Tamil Sangam“ in vier
  Zeilen, „Mitnehmen:“, „WhatsApp“, „Kalender Karte“ in drei Zeilen; 152 px links unter dem Datum bleiben leer.

## Befunde

### P0
keine (0 Konsolenfehler, 0 leere Bilder, 0 px Überlauf auf 5 Seiten bei 390/820/1280).

### P1
1. **Zettel am Handy auf termine und rubrik zweispaltig mit 134 px Textspalte** (termine 390 erster Bildschirm ab
   y 464, „Am Brett“; rubrik 390 „Feste der Gemeinden“ ab y 3969; betroffen sind genau die beiden Seiten mit `.zettel-liste--quer`, in index und den Artikeln steht der Zettel in `.brett` bzw. `.randspalte` und ist einspaltig).
   `.zettel` setzt `grid-template-columns: minmax(0, 13rem) minmax(0, 1fr)`; aufgehoben wird das nur für
   `.brett .zettel` und `.randspalte .zettel`, in den Abfragen `max-width: 60rem` und `40rem` fehlt `.zettel`. Folge
   bei 390: Datum 208 px breit, Text 134 px; Titel vier Zeilen, Ort drei Zeilen („Basel Tamil / Sangam, Aula /
   Lysbüchel, / Basel“), die Mitnahmen auf drei Zeilen, ein Zettel ca. 300 px hoch, links darunter eine leere Fläche.
   Unruhiger Satz und Löcher im ersten Bildschirm einer Hauptseite. *Abhilfe:* `.zettel` in die Liste der
   einspaltigen Raster unter `@media (max-width: 60rem)` aufnehmen (wie `.film-zeile`), also
   `.zettel { grid-template-columns: minmax(0, 1fr); row-gap: var(--space-2xs); }`; danach termine und rubrik bei 390
   und 820 neu aufnehmen.

### P2
1. **Tippflächen** (820): Bildnachweis-Links 40 px hoch (index „Foto: Jörg Braukmann …“ 420×40, „Foto: KARTY JazZ …“
   382×40; artikel „Foto: 18quirl08 …“ 367×40; rubrik „Foto: Ewe vonDetten …“ 412×40). Bei 390 auf den fünf Seiten
   behoben. Formularseiten (einreichen Checkbox, Dateifeld; kontakt WhatsApp-Link) in dieser Runde nicht nachgemessen.
   *Abhilfe:* `min-height: 44px` auch für zweizeilige Nachweise (Zeilenhöhe der Bildunterschrift auf 22 px) oder
   `padding-block: 2px`.
2. **Lücken neben den Meldungslisten bei 1280** (index, Nachrichten). Rechte Spalte endet bei y ca. 1365, die linke
   (Bild, Titel, Vorspann, Ort) bei ca. 1745: ca. 380 px leer rechts. Zwischen Abschnitten weiter 144 px plus
   ca. 40 px bis zur Liste (sloplint: „gaps 88, 96, 226“, als WAIVED 59 im Stempel). *Abhilfe:* rechte Spalte mit
   zwei weiteren Meldungen füllen oder 8/4 setzen; Abschnittsabstand 96 px.
3. **Kino: Stadtfeld ohne Hinweis und schief zum Titel** (kino 390 und 1280). Das Feld „Ihre Stadt“ ist leer, ohne
   Platzhalter, ohne Knopf und ohne Satz, dass die Liste darunter filtert; ein älterer Leser weiß nicht, was er
   eintippen soll und was danach passiert. Bei 1280 steht „Ihre Stadt“ (y 470) über dem Titel „Welcher Film wo“
   (y 540, unten ausgerichtet), dazwischen 180 px leere Fläche unter dem Vorspann. *Abhilfe:* Platzhalter „z. B.
   Berlin“ und Hinweiszeile „Die Liste zeigt dann nur Filme in Ihrer Stadt“; Feld und Titel oben ausrichten.
4. **Überschriftenebene springt** (artikel, sloplint F21): Auf die H1 folgt der Zettel als H3 ohne H2 dazwischen.
   Bildschirmleser verlieren die Gliederung. *Abhilfe:* der Randspalte eine H2 geben („Am Brett“) oder den
   Zetteltitel dort als H2 setzen und mit CSS klein halten.
5. **Drei Spaltenabstände** (sloplint F15, index): 64, 24 und 40 px zwischen Spalten, obwohl `--gap-columns` 32 px
   definiert ist (r2 P2-5 offen). *Abhilfe:* `--gap-columns` in allen Rastern.
6. **91 Ausnahmen im Stempel** (sloplint WAIVED über fünf Seiten, r2: 39 über drei). Darunter 44c (Unterseiten
   beginnen mit einem Kopf, der bei 276–332 px endet), 59 (Abschnittsabstände), 71 (Titel näher am Vorigen als an
   ihrem Inhalt, termine), 77 (dünne Abschnitte „Am Brett“ und „Feste der Gemeinden“ mit 57 % Breite), 78
   (Abschnittstitel 32 px unter 54 px Kopf). Jede einzeln begründbar, zusammen aber ein Zeichen, dass die Prüfregeln
   eher ausgenommen als erfüllt werden; insbesondere 71 und 77 decken sich mit den sichtbaren Lücken aus P2-2.
   *Abhilfe:* 71 und 77 durch Abstände und Breiten beheben statt ausnehmen.

### P3
1. `kalender/jailer-2-kloten.ics`: `DTSTART:20261115T170000` als schwebende Ortszeit ohne `DTEND`; nach RFC 5545
   (3.6.1) ein Termin ohne Dauer. Für DE/AT/CH unschädlich; manche Kalender zeigen ihn als Punkt. Wenn Eventfrog eine
   Dauer nennt, `DTEND` ergänzen, sonst so lassen.
2. „Am Brett“ auf index 22 px (1280: 27,8 px), auf termine 24 px (30,4 px): dieselbe Rolle, zwei Größen.
3. index 1280, Nachrichten: „Bundestagsdrucksache: 14 Abschiebungen nach Sri / Lanka …“ trennt „Sri Lanka“ über die
   Zeile (Titelbreite ca. 470 px); `Sri&nbsp;Lanka` setzen.
4. termine 1280: „Festkalender / 2026“ bricht trotz ca. 1100 px freier Breite in zwei Zeilen (enge `max-width`);
   „Das Jahr 2026“ steht tiefer als die Oberkante seiner Unterzeile rechts.
5. termine: Monatssprünge aufsteigend (Januar … November), die Liste absteigend (r2 P3-3 offen).
6. „Hängt noch 2 Tage“ bleibt ein Bild aus dem Aushang; „in 2 Tagen“ wäre für Ältere direkter (r2 P3-1 offen).
7. sloplint meldet im eigenen Render auf allen fünf Seiten einen Schrift-Fallback
   (`epilogue-latin-wght-normal.woff2`); `shots.mjs` meldet 0 Schriftfehler, die Bilder zeigen Epilogue. Zur Kenntnis.

## Was trägt
- Startseite 1280 im ersten Bildschirm: Aufmacher mit verlinkter Schlagzeile neben drei Terminen, die jetzt als
  Zeilen in derselben Linienordnung wie die Meldungen stehen; Rot nur am Datum der nächsten Termine und an der
  aktiven Rubrik.
- Klare Titelordnung über alle geprüften Seiten (32 / 24 / 22 / 19 px am Handy), eine Familie, Fließtext 19 px.
- Kino als Tabelle Film, Zahl der Kinos, Städte, mit Stand-Datum, Quelle am Jailer-Termin und ehrlichem Hinweis auf
  fehlende Spielorte.

## Bedienbarkeit (nur zur Information)

| Nielsen | 0–4 | Satz |
|---|---|---|
| 1 Systemstatus | 3 | „Heute“, „Hängt noch“, Stand-Daten und Quelle zeigen Aktualität. |
| 2 Sprache der Nutzer | 3 | Klar und deutsch; „Am Brett“, „Hängt noch“, „Mitnehmen“ sind Bilder. |
| 3 Kontrolle | 3 | Menü, Zurück, Monatssprünge. |
| 4 Konsistenz | 3 | Zettel einheitlich auf index; am Handy auf termine und rubrik anders gebaut (P1-1). |
| 5 Fehlervermeidung | 3 | Kalenderdateien je Termin, jetzt ohne erfundene Dauer. |
| 6 Wiedererkennen | 3 | Navigation sichtbar, aktive Rubrik rot. |
| 7 Effizienz | 3 | WhatsApp, Kalender, Karte direkt am Termin. |
| 8 Ästhetik, Minimalismus | 3 | Ruhig und linear; Lücken bei 1280 unter der Falz. |
| 9 Fehler erkennen | 2 | Formulare in dieser Runde nicht geprüft; Kino-Feld ohne Rückmeldung, was es tut. |
| 10 Hilfe | 3 | Hinweis zu fehlenden Spielorten, Platzhalter im Fuß gekennzeichnet. |
