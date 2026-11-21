# Prüfung hm-aushang, Runde 2
Harte Kriterien: 12 von 15 erfüllt · P0: 0 · P1: 4 · P2: 6 · P3: 4

Grundlage: `design/brief-v3.md`, `design/linien-auftrag.md`, `abgelehnt.md` (Runden 1–7), Hallmark-Floor, Pflichten aus
`tamil-marke`. Gemessen am 13.11.2026 über http://127.0.0.1:8955/richtungen/hm-aushang/ mit `tools/shots.mjs`
(12 Seiten: index, artikel, termine, kino, rubrik, verzeichnis, verzeichnis-eintrag, einreichen, einreichen-danke,
werben, buchen, kontakt; je 390/820/1280), `sloplint --genre editorial` (index, termine, kino mit `--url`) und einem
eigenen Messskript (berechnete Schriftgrößen und Lagen). Inhalte abgeglichen mit `design/inhalte/inhalte.json`,
`design/inhalte/rueckblick/rueckblick.json` und `docs/redaktion/rueckblick-2026.md`. `begruendung.md` nicht gelesen.
Auf Anweisung der Hauptsitzung vorzeitig abgeschlossen: Artikel, Rubrik, Verzeichnis, Formulare und Buchung nur über
`bericht.json` geprüft, nicht im Bild; der Paarvergleich mit den Referenzbildern ist nicht neu gemacht.

## Erster Eindruck
Die Startseite hat jetzt im ersten Bildschirm einen Aufmacher und daneben drei Termine; Knopfpaar, graues Kino-Band
und der Landingpage-Aufbau aus Runde 1 sind weg. Das neue Merkmal, der „Zettel“ mit Abreißstreifen, ist aber im Bild
ein gerahmter Kasten mit 6 px Rundung und einer Leiste aus drei Knöpfen; auf `termine` bei 1280 stehen drei davon
gleich breit nebeneinander. Unterhalb des ersten Bildschirms wiederholt die Startseite dreimal dieselbe Form (Bild
links, Liste rechts) mit großen Lücken.

## Messwerte

| Wert | Handy 390 | Desktop 1280 |
|---|---|---|
| Aufmacher-Schlagzeile (H1) | 30 px / 700 | 39,2 px / 700 |
| „Am Brett“ (H2) | 31,2 px | 31,2 px |
| Abschnittstitel (H2 „Nachrichten“ usw.) | 28 px | 39,2 px |
| Titel Zweitgeschichte, Filmtitel, Food-Fest (H3) | 31,2 px, Zeilenhöhe 40,6 px | 31,2 px |
| Meldungs- und Zetteltitel (H3) | 19 px | 21,8 px |
| Fließtext / kleinste Schrift | 18 px / 15 px | 18 px / 15 px |
| Schriftfamilien | 1 (Epilogue, selbst gehostet) | 1 |
| Zweite Geschichte im ersten Bildschirm | Zettel ab y 711, Titel y 781 (Falz 844) | drei Zettel bis y 797 (Falz 800) |
| Seitenlänge index | 7471 px | 5629 px |
| Abschnittsabstand / Abstand Kopf→Liste | 72 px / 40 px | 144 px / 64 px |
| Überlauf seitlich | 0 px auf 12 Seiten | 0 px (auch 820) |
| Konsolenfehler / leere Bilder / Schriftfehler | 0 / 0 / 0 | 0 / 0 / 0 |
| sloplint (index, termine, kino) | 0 FAIL, 5 WARN (2× F15 Spaltenabstände, 3× Schrift-Fallback im eigenen Render), 39 WAIVED, 3 DISMISSED | |

## Harte Kriterien

| # | Kriterium (brief-v3, linien-auftrag) | Handy 390 | Desktop 1280 | Ergebnis |
|---|---|---|---|---|
| 1 | Logo unverändert | Bilddatei `bilder/logo.png`, 48 px hoch | dto. | erfüllt |
| 2 | Nur Deutsch, keine tamilische Schrift als Schmuck | `tamil_ohne_lang` 0, keine Zierschrift | dto. | erfüllt |
| 3 | Echte Inhalte, nichts erfunden | „Jailer 2“, „Sonntag, 15. November, 17 Uhr“, `.ics` 17:00–20:00: Uhrzeit ohne Quelle | dto. | **verletzt** (P1-2) |
| 4 | Bildnachweis an jedem Bild | am Bild, verlinkt | dto. | erfüllt |
| 5 | Fließtext Handy ≥ 18 px (brief-v3: 17) | 18 px, Zeilenhöhe 1,6 | 18 px | erfüllt |
| 6 | Kontrast AA | Tokens unverändert gegen Runde 1: ink-2 ca. 13:1, muted ca. 7:1, Rot ca. 6:1 auf paper | dto. | erfüllt (gerechnet) |
| 7 | Tippflächen 44 px | Bildnachweis-Links 39 px hoch; rubrik „Ältere Beiträge“ 138×29; einreichen Checkbox 24×24, Dateifeld 226×35; kontakt „tamil.de auf WhatsApp“ 205×18 | – | **verletzt** (nach Bogen E als P2-1) |
| 8 | Kein seitliches Scrollen | 0 px | 0 px | erfüllt |
| 9 | `prefers-reduced-motion` | Block in `base.css`, keine Animationen außer Übergängen an Links | dto. | erfüllt (im Code geprüft) |
| 10 | Keine Dachzeilen, Versal-Labels, „·“-Metazeilen | keine | keine | erfüllt |
| 11 | Keine gleich großen Kartenraster, Verlaufkacheln, Seitenstreifen | Zettel als gerahmte Kästen untereinander | termine: drei gleich breite Zettel nebeneinander (`.zettel-liste--quer`, `repeat(auto-fit, minmax(20rem, 1fr))`) | **verletzt** (P1-1) |
| 12 | Nichts aus Runden 1–7 wiederholt | kein Cover mit einer Geschichte, kein „Diese Woche“-Band, kein Rot als Fläche | dto. | erfüllt (Knopfleiste der Zettel unter 11) |
| 13 | Schriften selbst gehostet, OFL im Ordner | `schriften/epilogue-*.woff2`, `Epilogue-OFL.txt` | dto. | erfüllt |
| 14 | Seitenliste vollständig | 11 Seiten, Danke-Zustand, 19 Artikel, 12 Profile | dto. | erfüllt |
| 15 | Keine Konsolenfehler, keine leeren Bilder | 0 / 0 | 0 / 0 | erfüllt |

## Stand der P1 aus Runde 1

| r1 | Befund | Stand r2 |
|---|---|---|
| P1-1 | Erster Bildschirm mit nur einer Geschichte | **behoben.** 390: erster Zettel ab y 711; 1280: Aufmacher und drei Zettel bis y 797. |
| P1-2 | Landingpage-Bausteine (Knopfpaar, Split-Banner) | **behoben.** Schlagzeile ist der Link, WhatsApp ist Textlink, `.btn` nur noch an Formular-Absendern (buchen, einreichen, kontakt, verzeichnis). |
| P1-3 | „Diese Woche“-Band | **behoben.** „Im Kino“ ohne Flächenwechsel in der Hauptspalte, mit Stand-Datum. |
| P1-4 | Signatur ist Theme-Standard | **verlagert.** Neue Signatur Zettel mit Abreißstreifen; im Bild ein Kartenmuster, siehe P1-1. Die Tagesziffer-Zeile (wie `hm-eigen`) trägt weiter das Jahr auf termine und kino. |
| P1-5 | Datumsblock verrutscht | **behoben.** Ziffer, Monat, Wochentag als ein Block, linksbündig bei x 64 (1280) bzw. x 16 (390). |
| P1-6 | Nicht belegter Termin Jailer 2 | **teilweise.** „Spezialpreis“ gestrichen, Datum und Kino jetzt auf Entwurf 5 in `rueckblick-2026.md` rückführbar; neu hinzugekommen ist die Uhrzeit 17 Uhr (P1-2). |
| P1-7 | Kino-Seite beantwortet „welcher Film läuft wo“ nicht | **weitgehend behoben.** Keine wortgleichen Stadtzeilen mehr; je Film Zahl der Kinos und Städte, Stadtfilter, ehrlicher Hinweis auf fehlende Spielorte. Offen bleibt nur die Uhrzeit (P1-2). |

Aus r1 P2 zusätzlich behoben: THADAM-Termin aus wartendem Entwurf entfernt (P2-7); Kino-Anrede „Ihre Stadt“ einheitlich
mit Sie (P2-6, Hausanzeige nicht nachgeprüft). Weiter offen: Tippflächen (P2-1), Leerraum (P2-2).

## Paarvergleich

Nur gegen den Stand von Runde 1 dieser Linie (Referenzbilder aus Zeitgründen nicht neu nebengelegt; brief-v3 misst
nicht mehr gegen Nachrichtenmarken).

- **index 1280, r1 gegen r2:** r1 hatte 125 px Luft über und 240 px unter dem Aufmacher, zweite Geschichte ab y 1015;
  r2 setzt den Aufmacher (7 Spalten) neben „Am Brett“ (5 Spalten), Oberkanten bei y 117 und 125, drei Termine sichtbar.
  Der erste Bildschirm ist dichter und nützlicher.
- **Zettel gegen Meldungszeile:** In r1 trugen Termine eine Haarlinie und die große Ziffer; in r2 tragen sie einen
  1-px-Rahmen in Tinte, 6 px Rundung, 24 px Innenabstand und eine dreigeteilte Fußleiste mit 48 px Höhe. Die Fläche
  pro Termin wächst von ca. 110 auf 210–250 px, und der Rahmen trennt den Termin vom übrigen Satz der Seite, der nur
  Haarlinien kennt.
- **Abschnitte unter der Falz:** unverändert die Form 7/5 (Bild mit Titel links, Meldungsliste rechts) dreimal
  hintereinander; die rechte Spalte endet bei Nachrichten ca. 390 px und bei Kultur ca. 430 px vor der linken.

## Befunde

### P0
keine (0 Konsolenfehler, 0 leere Bilder, 0 px Überlauf auf 12 Seiten bei 390/820/1280).

### P1
1. **Der Zettel ist ein Kartenraster mit Deko** (termine 1280 erster Bildschirm; index und termine 390 und 1280,
   „Am Brett“). Jeder Termin steht in einem gerahmten Kasten (`.zettel`: 1 px Tinte, `--radius-control` 6 px) mit
   einer Leiste aus drei gleich breiten Feldern „WhatsApp | Kalender | Karte“ (`.abriss`, 48 px, gestrichelte Trenner).
   Auf termine 1280 laufen drei Kästen gleich breit nebeneinander (`.zettel-liste--quer`): das verbotene
   gleich große Kartenraster (Runden 5–7) und die Knopfreihe aus Runde 3. Einziges Zeichen für „Abriss“ ist die
   gestrichelte Linie; ein Leser sieht eine Karte mit Fußleiste. *Abhilfe:* Zettel ohne Rahmen und Rundung als
   Zeilen zwischen Haarlinien wie der übrige Satz; die drei Mitnahmen als Textlinks in einer Zeile unter dem Ort, abgesetzt
   nur durch eine gestrichelte Linie über der Zeile; auf termine eine Spalte, nie drei nebeneinander. Wenn ein Merkmal
   bleiben soll, dann nur am nächsten Termin.
2. **Uhrzeit ohne Quelle** (index „Am Brett“ und „Im Kino“, termine, kino, `kalender/jailer-2-kloten.ics`; alle
   Breiten). „‚Jailer 2‘ im Kino Claudia, Sonntag, 15. November, 17 Uhr“; die `.ics` setzt 17:00 bis 20:00
   Europe/Zurich. Einzige Quelle ist der wartende Entwurf 5 in `docs/redaktion/rueckblick-2026.md` („am 15. November
   … im Kino Claudia in Kloten“), ohne Uhrzeit und ohne Dauer; `inhalte.json` verbietet für diese Kategorie
   ausdrücklich, Uhrzeiten zu ergänzen. Datum und Ort der beiden anderen Zettel sind belegt (Düsseldorf So 15.11.
   aus Beitrag 30, Basel Sa 21.11. Aula Lysbüchel aus `inhalte.json`), ebenso alle 62 Jahreseinträge auf termine
   (Datum, Titel, Wochentag geprüft). *Abhilfe:* „17 Uhr“ streichen, `.ics` ganztägig (`VALUE=DATE`, 20261115–20261116)
   wie die beiden anderen; Zettel als „aus wartendem Entwurf“ kennzeichnen oder bis zur Freigabe weglassen.
3. **Hierarchie und Satz der Titel am Handy** (index 390; dazu kino 390). Die Zweitgeschichte „Bundestagsdrucksache …“
   (31,2 px), „Am Brett“ (31,2 px), die Filmtitel (31,2 px) und „Namma Tamil Nadu Food Fest“ (31,2 px) sind größer als
   die Aufmacher-Schlagzeile (30 px) und die Abschnittstitel (28 px). Bei 31,2 px bricht „Bundestagsdrucksach|e:“
   mitten im Wort ohne Trennstrich (`overflow-wrap: break-word`, `hyphens: manual`); der Titel läuft über vier Zeilen
   und 163 px. Bei 1280 sind „Nachrichten“ und die anderen Abschnittstitel genau so groß wie die Aufmacher-H1
   (39,2 px). *Abhilfe:* `hyphens: auto` an h1–h3 (Seite ist `lang="de"`); `.stueck h3`, `.spalte-titel`,
   `.film-titel`, `.brett-titel` unter 40rem auf ca. 22–24 px; Abschnittstitel eine Stufe unter der H1.
4. **„Hängt noch …“ in wechselnder Lage** (index 1280, erster Bildschirm, „Am Brett“). Bei Düsseldorf und Basel steht
   die Angabe rechts neben dem Datum (x ca. 1055), bei Jailer 2 darunter (x 788), weil `.zettel-kopf` mit
   `flex-wrap` und `space-between` bei längerem Datum umbricht. Daten in wechselnder Form im ersten Bildschirm.
   *Abhilfe:* „Hängt noch“ immer unter das Datum (`flex-direction: column`) oder in eine feste Spalte.

### P2
1. **Tippflächen unter 44 px** (390): Bildnachweis-Links 39 px hoch (index 4×, artikel, rubrik, verzeichnis-eintrag);
   rubrik „Ältere Beiträge“ 138×29; einreichen Checkbox 24×24 und Dateifeld 226×35 (r1 P2-1 und P2-8 unverändert);
   kontakt „tamil.de auf WhatsApp“ 205×18. *Abhilfe:* `min-height: 44px` und `display: inline-flex` an Nachweis- und
   Blätterlinks, Checkbox-Label als 44-px-Fläche, eigenes Dateifeld mit 48-px-Label.
2. **Lücken und geringe Dichte bei 1280** (index, termine). index: rechte Spalte endet bei Nachrichten ca. 390 px und
   bei Küche/Kultur ca. 430 px vor der linken; zwischen Abschnitten 144 px plus 64 px unter jedem Titel. termine:
   „Am Brett“ beginnt erst bei y ca. 480, die Zettel bei y 590; die Jahrestitel brechen bei ca. 390 px Breite in drei
   Zeilen, rechts davon ca. 620 px leer (r1 P2-2 offen). *Abhilfe:* Abschnittsabstand 96 px, rechte Spalte mit einer
   dritten und vierten Meldung füllen oder 8/4 setzen; Jahrestitel bis ca. 60 Zeichen Breite, Ort in eine eigene Spalte.
3. **Unter der Falz austauschbar** (index 390 und 1280). Nachrichten, Community, Küche/Kultur sind dreimal dieselbe
   Form (Bild mit großem Titel, daneben Meldungsliste), ohne etwas, das nur tamil.de hat; die Spalten Küche und Kultur
   tragen keine eigene Überschrift, „Sport“ im Abschnittstitel hat keinen eigenen Beitrag. *Abhilfe:* je Abschnitt
   eine eigene Ordnung aus dem Inhalt (Community nach Ort, Küche als Ort mit Adresse), Spalten benennen oder Titel auf
   „Küche und Kultur“ kürzen.
4. **Festkalender enthält Nachrichten** (termine, „Das Jahr 2026“): neben Festen stehen u. a. „Österreich:
   Asylbehörde BFA legt Länderinformation …“, „Bundesverwaltungsgericht hält … an Asylpraxis fest“, „Sri Lanka erlässt
   … die Visagebühr“; die Zeile „Was die Redaktion 2026 berichtet hat“ stimmt nicht, denn laut Quelle ist davon noch
   nichts veröffentlicht. *Abhilfe:* im Festkalender nur Ereignisse mit Ort; Nachrichten in die Rubrik; Unterzeile
   ehrlich („aus den Beiträgen 2026, noch nicht veröffentlicht“ oder neutral).
5. **Mehrere Spaltenabstände** (sloplint WARN F15, index und termine): 64, 24, 40 und 96 px zwischen Spalten;
   Hallmark verlangt einen Spaltenabstand unterhalb des Aufmachers. *Abhilfe:* `--gap-columns` überall.
6. **`.ics` mit Zeitzone ohne VTIMEZONE** (`kalender/jailer-2-kloten.ics`): `TZID=Europe/Zurich` ohne
   `VTIMEZONE`-Block (RFC 5545, 3.2.19); manche Kalender lehnen die Datei ab oder legen die Zeit falsch. Entfällt mit
   der Abhilfe zu P1-2 (ganztägig). Zeilenenden CRLF korrekt.

### P3
1. „Hängt noch 2 Tage“ ist ein Bild aus dem Aushang; „in 2 Tagen“ wäre für Ältere direkter.
2. Der Karte-Link bei Düsseldorf sucht nur die Stadt (`query=Düsseldorf`), weil kein Ort belegt ist; dann besser
   ohne Karte.
3. Monatssprünge auf termine aufsteigend (Januar … November), die Liste absteigend.
4. sloplint meldet im eigenen Render einen Schrift-Fallback (`epilogue-latin-wght-normal.woff2`); `shots.mjs` meldet
   keine Schriftfehler, die Bilder zeigen Epilogue. Zur Kenntnis: 39 Ausnahmen (WAIVED) über drei Seiten, davon neun
   Ausnahmezeilen im Stempel.

## Was trägt
- Erster Bildschirm der Startseite: Aufmacher mit verlinkter Schlagzeile, Vorspann, WhatsApp als Textlink, Bild mit
  Nachweis; daneben die nächsten Termine mit Datum in Rot nur bei den nächsten. Kein Knopf, kein Band, kein Rot als Fläche.
- Termine-Jahr: 62 Einträge, alle mit belegtem Datum, Titel und Wochentag, Datumsblock sauber gestapelt, „Heute,
  Freitag, 13. November“ als rote Linie im Verlauf.
- Kino als ruhige Tabelle (Film, Zahl der Kinos, Städte) mit ehrlichem Hinweis, wo Spielorte fehlen.

## Bedienbarkeit (nur zur Information)

| Nielsen | 0–4 | Satz |
|---|---|---|
| 1 Systemstatus | 3 | „Heute“, „Hängt noch“, Stand-Daten zeigen Aktualität. |
| 2 Sprache der Nutzer | 3 | Klar und deutsch; „Am Brett“, „Hängt noch“ sind Bilder, keine Alltagssprache. |
| 3 Kontrolle | 3 | Menü, Zurück, Buchung schrittweise. |
| 4 Konsistenz | 2 | „Hängt noch“ springt; Titelgrößen folgen nicht der Wichtigkeit. |
| 5 Fehlervermeidung | 3 | Kalenderdatei je Termin; bei Jailer 2 aber mit unbelegter Zeit. |
| 6 Wiedererkennen | 3 | Navigation stets sichtbar, aktive Rubrik rot. |
| 7 Effizienz | 3 | Kalender, Karte, WhatsApp direkt am Termin. |
| 8 Ästhetik, Minimalismus | 2 | Ruhig, aber Kästen am Brett und große Lücken unter der Falz. |
| 9 Fehler erkennen | 2 | Formulare in dieser Runde nicht im Bild geprüft. |
| 10 Hilfe | 3 | Feldhinweise und Platzhalter klar gekennzeichnet. |
