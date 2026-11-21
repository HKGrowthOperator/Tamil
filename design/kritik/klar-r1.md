# Prüfung klar, Runde 1
Harte Kriterien: 12 von 12 erfüllt · P0: 0 · P1: 0 · P2: 3

Grundlage: `node design/vergleich/aufnahmen.mjs klar` (Kennzahlen `design/vergleich/kennzahlen/klar.json`, Stand
2026-11-10T09:41), `tools/shots.mjs --kacheln` für Startseite und Artikel bei 390/820/1280 (0 Fehler) und eigene
Nachmessung mit Playwright am Artikel und an der Startseite (Schriftgrößen, Zeichen je Zeile, Kontrast, Bildbreiten,
Fokus per Tab).

## Erster Eindruck (3 Sätze)

Am Handy liest es sich in fünf Sekunden wie eine Nachrichtenseite: Rubrikzeile, Bild über die volle Breite, klare
Schlagzeile, darunter zwei Nebenstücke mit kleinem Bild und Linie, Rot nur in den Dachzeilen. Am Desktop steht der
Aufbau einer Tagesschau- oder BBC-Startseite: Aufmacher mit Bild auf halber Breite, Nebenstücke darunter, rechts eine
schmale Spalte „Weitere Meldungen“; neun Schlagzeilen sind ohne Scrollen ganz sichtbar. Schwächen gibt es nur in den
Einzelheiten: sehr kleine Bilder der Nebenstücke am Handy und ein Dienstblock, der seine eigenen Etiketten
mitbringt.

## Harte Kriterien

| # | Kriterium | Messwert Handy (390 × 844) | Messwert Desktop (1280 × 800) | Ergebnis |
|---|---|---|---|---|
| 1 | Viele Geschichten | 3 Schlagzeilen ganz sichtbar (Aufmacher, „Sri Lanka schafft Visum …“, „Parai …“); alle `h2`/`h3` in einem Link | 9 ganz sichtbar (Aufmacher, 2 Nebenstücke, 6 Meldungen) | erfüllt |
| 2 | Kopf | `<header>` mit Logo und `nav`; `kopfleiste_hoehe` 112 px (≤ 120); Aufmacher-Schlagzeile ab 369 px (≤ 480) | Kopf 90 px, Schlagzeile ab 145 px | erfüllt |
| 3 | Drei Stufen, Verhältnis, Familien | 28 / 19 / 17 px (Gewicht 650 / 650 / 600); 28 : 19 = 1,47; eine Familie (Libre Franklin) | 34 / 22 / 18 px; 34 : 22 = 1,55; eine Familie | erfüllt |
| 4 | Größte Schrift, Zeilen, Versalien | 28 px; Aufmacher 3 Zeilen, längster Titel (81 Zeichen, Meldung) 2 Zeilen, Nebenstücke höchstens 3; Versalien über 14 px: 0 | 34 px; Aufmacher 3 Zeilen, andere höchstens 3; Versalien über 14 px: 0 | erfüllt |
| 5 | Rot | 0,2 % Fläche; größte rote Schrift 13 px (Dachzeile); kein zweiter Buntton | 0,2 %; 13 px; kein zweiter Buntton | erfüllt |
| 6 | Keine Effekte | Radius 0, Schatten 0, gedreht 0, Schriftbreite unverändert | dieselben Werte | erfüllt |
| 7 | Anreißer ohne Kasten | nur Linien (1 px, Linie) zwischen Anreißern; keine Icons, keine Knöpfe; Rubrikzeile als Textzeile ohne Pillen | wie Handy | erfüllt |
| 8 | Ein Format für Dachzeile/Datum, höchstens zwei Bildformate | „Rubrik │ 17. Juli 2024“, 13 px, überall gleich; alle Bilder 16 : 9 (ein Format) | wie Handy | erfüllt (zum Dienstblock siehe P2-2) |
| 9 | Kein Bild über natürlicher Breite bei 2× | größtes Verhältnis: Aufmacher 390 px gezeigt / 1382 px Datei; Logo 119 / 300 | Aufmacher 402 / 1382; Nebenstücke 208 / 1200; Küche 276 / 1200; Logo 150 / 300 (genau die Grenze); Artikelbild 680 / 1382 | erfüllt |
| 10 | Kein Überlauf, keine Konsolenfehler | 0 px; Konsole leer (auch 820: 0 px) | 0 px; Konsole leer | erfüllt |
| 11 | Dienstblock spätestens im 3. Bildschirm | beginnt bei 2172 px (Grenze 2532 px), also im 3. Bildschirm | – | erfüllt |
| 12 | Paarvergleich, Spanne der Marken | größte Schlagzeile 28 px (Spanne 18–32), Gewicht 650 (350–800), 3 Schlagzeilen (1–3), Rot 0,2 %, Radius 0 | größte Schlagzeile 34 px (18–36), Rot 0,2 %, Radius 0 | erfüllt, mit Anmerkung |

**Anmerkung zu 12 (Auslegung, nicht gezählt):** Zwei Desktop-Werte liegen außerhalb der Spanne der Marken, beide in
die Richtung, die der Brief ausdrücklich verlangt: 9 statt höchstens 4 Schlagzeilen im ersten Bildschirm und 145 px
statt mindestens 451 px bis zur ersten Schlagzeile. Die Spanne ist bei den Marken durch Anzeigen und große Köpfe
gedrückt (Brief, Abschnitt 7), Kriterium 1 fordert „mindestens vier“ und die Variante `klar` „die höchste Dichte“.
Ich werte das nicht als P1; die Hauptsitzung sollte es wissen.

## Paarvergleich

**klar neben BBC (Handy 390 und Desktop 1280)**
- Aufbau fast deckungsgleich: Bild über die volle Breite, Schlagzeile, Vorspann, dann Nebenstücke mit Bild links und
  Text rechts, getrennt durch 1-px-Linien. BBC setzt Rubrik und Zeit **unter** die Schlagzeile, klar **darüber** in Rot;
  beides ist ruhig.
- Bilder der Nebenstücke: BBC zeigt sie etwa 132 px breit (gut ein Drittel der Breite), klar nur 90 × 51 px. Bei BBC
  erkennt man die Gerichtszeichnung, bei klar sind Konzert- und Kanguva-Motiv nur noch Farbflecken. Hier wirkt BBC
  wertiger.
- Schrift: BBC Serife in den Schlagzeilen, klar eine Grotesk 650 mit leicht engem Laufweite (−0,012 em) und
  ausgeglichenem Zeilenfall (`text-wrap: balance`); Satz ohne Löcher, Zeilenabstände gleichmäßig. Gleichwertig.
- Desktop: BBC drängt den Inhalt durch Anzeige und Abo-Leiste unter die Falz; klar zeigt neun Schlagzeilen in drei
  klar getrennten Zonen mit gleicher Oberkante (Bild, Dachzeile des Aufmachers und schwarze Linie über „Weitere
  Meldungen“ stehen auf einer Linie). Hier ist klar aufgeräumter.

**klar neben Tagesschau**
- Tagesschau arbeitet mit blauen Kästchen-Etiketten („INTERVIEW“) und blauer Schlagzeile; klar hat keine Etiketten,
  Rot nur in 13-px-Dachzeilen, Schlagzeilen in Tinte. klar ist hier zurückhaltender.
- Tagesschau-Desktop: ein Bild über die volle Breite, nur eine Geschichte sichtbar; klar zeigt den Aufmacher auf halber
  Breite und daneben Text, also deutlich mehr Geschichten bei gleicher Ruhe.
- Tagesschau setzt die Schlagzeile mit 350 Gewicht sehr leicht; klar mit 650 kräftiger, ohne laut zu werden.

**klar neben Runde 2 (Community-Magazin)**
- Grund: Runde 2 creme/sand mit braungrauer Tinte; klar kühles Weiß (249/250/251) mit blaugrauer Tinte. Kein warmer
  Ton.
- Runde 2 hat Pillen in der Rubrikzeile, einen abgerundeten Anzeigenkasten, ein Bild mit großem Radius und bunte
  Rubrikpunkte; klar hat Radius 0, keine Punkte, eine Textzeile als Rubrikleiste.
- Erster Handy-Bildschirm: Runde 2 zeigt keine einzige Schlagzeile, klar drei.

**klar neben Runde 4 (Raster)**
- Runde 4: rote Riesenschrift „KANGUVA“ (über 100 px), extraschmale Grotesk, Versalien in der Navigation, rote
  Rasterlinien um jede Zelle, feste Leiste unten. klar: größte Schrift 28/34 px, normale Breite, Versalien nur im
  Dienstblock bei 13 px, graue 1-px-Linien nur zwischen Anreißern, keine feste Leiste.
- Runde 4 zeigt eine Geschichte als Cover; klar zeigt drei (Handy) bzw. neun (Desktop).

## Befunde

**P0:** keine. `bericht.json`: Überlauf 0, Konsole leer, keine leeren Bilder, alle Schriften geladen, keine Tippfläche
unter 44 px, kein Tamil ohne `lang`.

**P1:** keine.

**P2-1 – Bilder der Nebenstücke am Handy zu klein (390, `.stueck .bild`).** 90 × 51 px bei 358 px Inhaltsbreite
(25 %). Motive mit Bühne oder Szene (Konzert, Kanguva) sind nicht mehr zu erkennen; das Bild wirkt wie eine
Briefmarke und der Abstand zur Meldung ohne Bild schrumpft. BBC zeigt rund 132 px. *Behebung:* Spalte auf 120–136 px
(etwa ein Drittel), Spaltenabstand 12–14 px lassen; Schlagzeile bleibt bei 19 px dreizeilig.

**P2-2 – Dienstblock „Diese Woche“ mit eigenen Etiketten- und Datumsformen (390 und 1280, `.woche`).** Neben dem
Seitenformat „Rubrik │ Datum“ (13 px, rot/leise) kommen zwei weitere Formen dazu: graue Versalien-Etiketten „IM KINO“,
„TERMINE“ (13 px, Sperrung 0,06 em) und ein fettes Datum in Tinte mit Wochentag („Samstag, 21. November 2026“,
14 px, 600). Am Desktop kommen ungleiche Spalten (2 : 1) und Kino-Einträge ohne Trennlinie neben einem Termin mit
Linie dazu. Außerhalb des ersten Bildschirms, daher P2. *Behebung:* Etiketten im selben Stil wie die Blocktitel oder
wie die Dachzeile setzen; Datum des Termins in der Form der Meta-Zeile (leise, 13–14 px), Wochentag darf bleiben, weil
er aus den Inhalten kommt; Kino- und Terminspalte am Desktop mit derselben Linie gliedern.

**P2-3 – Vorspann der Nebenstücke am Desktop zu lang gesetzt (1280, `.stueck .vorspann`).** 16 px auf 600 px Breite
ergibt bis zu 81 Zeichen je Zeile (gemessen 78, 75, 81, 78); über der Grenze von 70 Zeichen aus den Pflichten. Der
Aufmacher-Vorspann daneben hat nur 40–50 Zeichen. *Behebung:* `max-width` des Nebenstück-Textes auf etwa 34 em
(≈ 540 px) oder Vorspann auf 17 px; alternativ die Meldungsspalte breiter (etwa 360 px).

**P3**
- P3-1 – Am Handy fehlen die Vorspänne der Nebenstücke (`.stueck .vorspann { display: none }` unter 600 px). Erlaubt,
  aber die Nebenstücke unterscheiden sich am Handy von den Meldungen dann nur noch durch Bild und 19 px/650 gegen
  17 px/600. Mit größerem Bild (P2-1) ist der Unterschied ausreichend; sonst einen Satz Vorspann zeigen.
- P3-2 – Rubrikzeile am Handy: abgeschnittenes „Commun…“ ist der einzige Hinweis aufs seitliche Laufen; keine aktive
  Rubrik, auch nicht im Artikel (Rubrik „Nachrichten“ wird im Kopf nicht markiert, der Brief sieht Rot für die aktive
  Rubrik vor).
- P3-3 – Küche: jede der vier Kacheln trägt die Dachzeile „Küche“ direkt unter dem Blocktitel „Küche“. Vom Brief
  verlangt (jeder Anreißer hat eine Dachzeile), wirkt aber wiederholt; in der Ausbaustufe nur das Datum zeigen, falls
  der Brief das zulässt.
- P3-4 – Logo: Unterzeile in Kopfgröße (119 px bzw. 150 px breit) unlesbar; bekannt (Brief, Abschnitt 9).

## Inhalte (D)

- Startseite: Rubriken (9, Reihenfolge stimmt), Aufmacher, vier Nebenstücke, sechs Meldungen, vier Küchenbeiträge,
  zwei Kinoeinträge und ein Termin stimmen mit `design/inhalte/inhalte.json` in Titel, Dachzeile, Datum und
  Reihenfolge überein. Vorspänne sind an Satzenden gekürzt. Kino: „11 Kinos in Deutschland“, fünf Städte „und
  6 weitere Städte“; „2 Kinos“, Gütersloh, Ravensburg; Termin mit Datum, Ort, Veranstalter und Text unverändert.
  Nichts erfunden, nichts weggelassen.
- Artikel: Dachzeile, Titel, Vorspann (am Satzende gekürzt), Datum, „2 Min. Lesezeit“, Bild, genau die drei Absätze
  unverändert; keine Autorenzeile, kein Bildnachweis (liegt nicht vor, richtig so). WhatsApp-Teilen als schlichter Link
  ohne Skript.
- Leser 65+: Artikel-Fließtext 18 px / 28,8 px Zeilenabstand am Handy (40 Zeichen je Zeile), 19 px / 30,4 px am
  Desktop (46–66 Zeichen je Zeile, ≤ 70); größte Schrift im Artikel 28 px (Handy) / 36 px (Desktop). Kontrast gegen
  den Grund: Text 16,9 : 1, Dachzeile rot 6,1 : 1, Datum und „Lesezeit“ 7,1 : 1. Rubriklinks 44 px hoch, Teilen-Link
  138 × 44 px, Anreißer ganzflächig tippbar. Fokus: 2-px-Rahmen in Tinte mit 3 px Abstand, um den ganzen Anreißer und
  um jeden Rubriklink sichtbar (per Tab aufgenommen, Handy und Desktop).
- 19-Jährige in fünf Sekunden: Aufmacher sofort erkennbar, zwei weitere Geschichten im selben Bildschirm.

## Was trägt (höchstens 3 Punkte)

- Disziplin bei Farbe und Form: Rot 0,2 % nur in 13-px-Dachzeilen, Radius 0, keine Schatten, ein Bildformat, eine
  Schriftfamilie mit drei sauber getrennten Stufen.
- Desktop-Raster: Aufmacher halbbreit, Nebenstücke darunter, Meldungsspalte rechts mit gemeinsamer Oberkante; neun
  ganze Schlagzeilen ohne Gedränge.
- Artikel: ruhiger Kopf, Bild nach der Lesezeit-Leiste, Fließtext in Pflichtgröße mit Zeilenlänge unter 70 Zeichen.

## Bedienbarkeit (nur zur Information)

| Heuristik (Nielsen) | 0–4 | Satz |
|---|---|---|
| 1 Sichtbarkeit des Systemstatus | 3 | Fokus und Unterstreichung beim Überfahren sichtbar; keine aktive Rubrik im Kopf. |
| 2 Übereinstimmung mit der Wirklichkeit | 4 | Vertraute Nachrichtenordnung, deutsche Begriffe, Datum mit Jahr. |
| 3 Kontrolle und Freiheit | 3 | Logo führt zur Startseite; Weiteres (Fuß, Zurück) ist in der Skizze nicht vorgesehen. |
| 4 Konsistenz und Standards | 3 | Meta-Zeile einheitlich; Dienstblock bricht mit eigenen Etiketten (P2-2). |
| 5 Fehlervermeidung | 3 | Ganzflächige Tippziele ohne Konkurrenz durch kleine Links. |
| 6 Wiedererkennen statt Erinnern | 3 | Rubrikzeile immer sichtbar, am Handy aber ohne Hinweis aufs Weiterwischen. |
| 7 Flexibilität und Effizienz | 3 | Neun Schlagzeilen auf einen Blick am Desktop; keine Abkürzungen nötig. |
| 8 Ästhetik und Minimalismus | 4 | Nur Linien und Abstand, nichts Überflüssiges. |
| 9 Fehler erkennen und beheben | – | In der Skizze keine Zustände. |
| 10 Hilfe und Dokumentation | – | Nicht anwendbar. |
