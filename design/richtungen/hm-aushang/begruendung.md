# Linie C „Aushang“ (hm-aushang)

tamil.de als das Schwarze Brett der tamilischen Gemeinden in Deutschland, Österreich und der Schweiz: Jede datierte
Sache hängt als Aushang mit ihrem Datum als Kopf aus, schwarz auf Weiß, mit Haarlinien; nur der nächste Termin ist rot.

## Picks

**Hallmark · v2.0.0**

- **Shape** · Aushang (eigene Form: geordnete Reihen datierter Aushänge, der Aufmacher neben seinem Bild), aus Draw c53a1a; getauscht: der Draw gab Split Studio, das Material ist aber eine Tafel datierter Meldungen · genre editorial · job: visit (was hängt aus, was kommt als Nächstes, wo)
- **Theme** · Ink by request (weißes Papier, Schwarz ohne Farbton, Epilogue 700 über 400, Haarlinien) · Dials: Radius 6 statt 12, keine Pillen, kein IBM Plex Mono (impeccable-Ausschlussliste), Papier kühl statt 100°-Ton
- **Signal** · auf Logo-Rot umgestimmt (oklch 50.8% 0.177 25.6 = #B5282A). Grund: Petrol neben dem roten Logo wären zwei bunte Farben auf Weiß (Runde 1: „zu viele Farben“); ein Aushang ist Schwarz mit einer roten Auszeichnung wie der rote Tag im Kalender. Rot ist nie Fläche und nie Tönung (rosa Kästen sind Runde 3), nur Schrift: Datum und Wort des nächsten Termins, aktuelle Seite in der Navigation, „Läuft“ im Kino, Unterstreichung beim Überfahren, die Heute-Linie im Festkalender
- **Chrome** · (seit r1) nav: Logo und eine Leiste mit sieben Rubriken und „Termin einreichen“ als letztem Textlink, unter 76rem Menü als Ausklapper · footer: Kolophon (Logo, ein Satz, Links)
- **Hero** · (seit r1) kein Stage mehr: Aufmacher auf 7 Spalten (Titel als Link, ein Satz, WhatsApp-Link, Bild 16:9), daneben „Am Brett“ mit den Zetteln; Unterseiten mit einspaltigem Kopf
- **Signature** · (seit r1) der Zettel mit Abreißstreifen: Datum, „Hängt noch 2 Tage“, Titel, Ort, unten hinter einer Perforation drei Streifen zum Mitnehmen (WhatsApp, Kalender als .ics, Karte); der nächste Termin in Rot. Nur für kommende, belegte Termine
- **Sections (Start, seit r1)** · Aufmacher und Am Brett · Nachrichten (Bild 7, Meldungen 5) · Im Kino (Filmzeilen) · Community (Meldungen 7, Bild 5) · Küche, Kultur und Sport · Tempel, Vereine und Läden (Verzeichniszeilen) · Fuß
- **Type** · Epilogue (OFL, selbst gehostet, Lizenz in `schriften/`), Gewichte 400/600/700; Fließtext 18 px Handy, 19 px im Artikel bei 65 Zeichen; Titel nie in Versalien, keine Dachzeilen, keine Labels in Versalien, keine „·“-Metazeilen
- **Material** · real: 20 Rückblick-Beiträge mit Commons-Bildern und Nachweis, 62 Chronik-Einträge, Kino-Woche 9.11., Termine Düsseldorf 15.11. (Beitrag 30), Basel 21.11. (inhalte.json), Kloten 15.11. und Bern 13.12. (wartende Radar-Entwürfe 5 und 4), Werbeplätze aus `ads.php`, Formularfelder aus §12/§14, Logo · absent (sichtbare Platzhalter): Kontaktdaten der Einrichtungen, Preise („Preis folgt“), Einwilligungstext und Verkaufsbedingungen (KBS), E-Mail und Telefon der Redaktion, Impressum
- **Sweep** · (Stand r1, siehe unten) Floor 0 FAIL über http · Reflex 0 offen (6 waived: 22, 44c, 49b, 71, 77, 79) · dismissed 58 (Startseite listet Schlagzeilen, Aufmacher-Titel hat 8 Wörter) · Seiten mit vollem Redaktionstext (`wortlaut.css`: Artikel, Festkalender, Kino, Community Seite 2) tragen `copy: verbatim` · finish-review: nicht gelaufen (kein frischer Prüfer in diesem Lauf)

## Seiten

`index.html`, `rubrik.html` (+ `rubrik-2.html` für die Seitennavigation), `artikel.html` (Beitrag 30; dazu `artikel-<id>.html` für alle 19 übrigen), `termine.html`, `kino.html`, `verzeichnis.html` (13 Einrichtungen aus den Beiträgen, Filter in der Adresse, leerer Zustand für Österreich und Dienstleister), `verzeichnis-eintrag.html` (Sri Ganesha Hindu Temple mit Premium-Markierung als gekennzeichnete Beispielansicht; dazu `verzeichnis-<slug>.html`), `einreichen.html` (Felder §12, Einwilligung, Falle, Bild-Recht) und `einreichen-danke.html` (Zustand nach dem Absenden, Nummer als Platzhalter), `werben.html` (sechs Plätze maßstäblich gezeichnet, „Preis folgt“, frei ab 17.11. nach Vorschlag zwei Werktage Vorlauf), `buchen.html` (fünf Schritte, Kalender November/Dezember, Upload, Zusammenfassung, Stripe), `kontakt.html` (Platzhalter, Nachricht, Impressum folgt). Erzeugt mit `bauen.py`; Skript `aushang.js` filtert nur und sagt bei den Formularen „Nichts wurde gesendet“ (Gate 70).

## Prüfungen

- `sloplint --genre editorial --render` über `http://127.0.0.1:8943/…` für 13 Seiten: 0 FAIL, 0 offene REFLEX. Die 13 WARN „fallback font“ stammen nur aus der `file://`-Darstellung (Schriften laden dort nicht); über http keine. Rest-WARN: F15 (Spaltenabstände 24/40/64/96 zwischen Reihen und Abschnitten), F21 (h1 gefolgt von h3 in Reihen auf drei Seiten).
- `tools/shots.mjs` 390/820/1280, 13 Seiten: 39 Aufnahmen, 0 Fehler, kein seitliches Scrollen, keine Konsolenfehler. Hinweise auf kleine Tippflächen betreffen Bildnachweis-Links und das Logo (40 px hoch).

## Abgrenzung

- Runde 1 (Nachtblau, Gold, viele Farben): weißes Papier, eine einzige Farbe, und die ist das Logo-Rot als Schrift.
- Runde 2 (Creme, Serife, runde Bilder): kühles Weiß, eine Grotesk, Radius 6 px.
- Runde 3 (Pillen, Kreise, rote Platte): keine Pillen, kein Rot als Fläche, Titel nie im Bild.
- Runde 4 (laut): größte Schrift 54 px (Aufmacher, Desktop), 32 px am Handy, normale Breite.
- Runden 5–7 (Portal-Werkzeugkasten): keine Dachzeilen, keine Versal-Labels, keine „·“-Zeilen, kein Kartenraster, keine Verlaufskacheln, kein „Diese Woche“-Band; Ordnung kommt aus Datum und Linie.

## Schwächen (je ein Satz)

- Die Startseite ist lang (rund 6.000 px bei 1440), weil jede Rubrik als eigener Abschnitt mit großem Abstand steht.
- Epilogue wirkt in 700 breit; bei langen Artikeltiteln auf dem Handy werden es vier bis fünf Zeilen.
- Die Chronik-Titel in Festkalender und Community Seite 2 haben keine eigenen Seiten und sind deshalb keine Links.
- Die Rubrik-Zuordnung älterer Chronik-Titel zu „Community“ hat diese Probe vorgenommen, nicht die Redaktion.
- Der Aufmacher und das Verzeichnisprofil nutzen dasselbe Tempelbild (wie Beitrag 30 und 49 im Material).
- Die Finish-Prüfung aus frischem Kontext (Hallmark § 6) steht noch aus.

## Überarbeitung nach Kritik r1

Grundlage: `design/kritik/hm-aushang-r1.md` (7 P1, 8 P2) und die Punkte der Koordination. Geändert nur über `bauen.py`,
`hm-aushang.css` und `aushang.js`.

| Punkt | Was jetzt gilt |
|---|---|
| P1-1 erster Bildschirm | Die Bühne ist weg. Links der Aufmacher (Titel, ein Satz, WhatsApp-Link, Bild darunter), rechts „Am Brett“ mit drei Aushängen. Bei 1280×800 stehen der Aufmacher und alle drei Termine im ersten Bildschirm, bei 390 beginnt der erste Aushang über der Falz. |
| P1-2 Landingpage-Bausteine | Die Schlagzeile ist der Link; Knopfpaar, „Termin einreichen“-Kasten im Kopf und die Aushangzeile über der Leiste sind weg („Termin einreichen“ ist der letzte Navigationslink). Unterseitenköpfe sind einspaltig (Titel, Satz darunter, Textlinks), die Liste folgt direkt. Knöpfe bleiben nur zum Absenden von Formularen. |
| P1-3 „Diese Woche“-Band | Kein graues Band mehr, nirgends. Kino steht auf der Startseite als „Im Kino“ mit Stand-Datum in Linien in der Hauptspalte. |
| P1-4 Signatur | Die Tagesziffer vor jeder Zeile war Ink-Standard und zu nah an Linie A. Neu ist der Zettel mit Abreißstreifen, den es nur für kommende, belegte Termine gibt: oben Datum (nächster rot) und „Hängt noch n Tage“ (ein Aushang hängt bis zum Tag des Termins; danach ist er fort, wie der Kalender-Termin im System), darunter Titel und Ort, unten hinter einer gestrichelten Perforation drei Abschnitte zum Mitnehmen: WhatsApp, Kalender (echte `.ics`-Datei in `kalender/`), Karte (OpenStreetMap-Suche nach dem Ort). Ohne Pinnnadel, Kork oder Papierstruktur. Beiträge tragen keine große Ziffer mehr, nur Ort und Datum klein unter dem Titel (behebt auch P2-3). |
| P1-5 Datumsblock | Ursache war eine Klassenkollision: `.monat` (Monatsabschnitt im Festkalender) gab dem Monatsnamen im Datum 64 px Abstand. Abschnitt heißt jetzt `.monatsblock`; das Datum steht als ein Block (Ziffer, darunter Monat und Wochentag) linksbündig. |
| P1-6 Belege | THADAM (nur wartender Entwurf) entfernt. „Jailer 2“ bleibt nach Bestätigung der Koordination (Radar, Eventfrog, Story 19) genau mit Sonntag, 15. November, 17 Uhr, Kino Claudia, Kloten; „Spezialpreis“ ist gestrichen. |
| P1-7 Kino | Nach Film statt nach Stadt: „Scene“ 11 Kinos in Deutschland, fünf belegte Städte und „6 weitere Städte“, „Ramayana“ 2 Kinos in Gütersloh und Ravensburg, „Jailer 2“ Kino Claudia mit Zeit. Kein „Läuft“. Die Stadtsuche filtert die Filme. Hinweis: Spielorte folgen, sobald sie in den Programmen stehen. |
| P2-1 Tippflächen | Logo-Link 48 px hoch (Handy 44), Monatslinks und Fußlinks mindestens 44×44, Ankreuzfelder mit 44 px Zeile, Dateifeld mit eigenem 44-px-Knopf. |
| P2-2 Dichte | Datumsspalte 7 rem statt 9,5 rem, Unterseitenköpfe oben bündig ohne Zweispalt. |
| P2-4 Knopfreihen | Art im Verzeichnis ist ein Auswahlfeld, der Filter steht ohne Kasten unter einer Linie; Land und Laufzeit sind Radios als Liste mit Linien. |
| P2-5 Legende | „Schwarz: Ihr Starttag. Grau hinterlegt: Ihr gewählter Zeitraum. Durchgestrichen: nicht buchbar.“ |
| P2-6 Anrede, Kennzeichnung | Hausanzeige „Dein Fest“ auf der Startseite entfernt; der WhatsApp-Hinweis im Artikel heißt „In eigener Sache“, nicht „Anzeige“. Anrede durchgehend Sie. |
| P2-7 THADAM | entfernt (siehe P1-6). |
| P2-8 Dateifeld | eigener Knopf über `::file-selector-button`. |

Nebenbei behoben: Vorspann-Ausschnitte brachen bei „Vom 19.“ ab; der erste Satz wird jetzt nur nach einem Kleinbuchstaben
getrennt.

**Prüfung nach der Überarbeitung:** `sloplint --genre editorial --render` über http, 13 Seiten: 0 FAIL, 0 offene REFLEX
(Ausnahmen unverändert 22, 44c, 49b, 71, 77, 79; 58 zurückgewiesen). Übrige WARN: 13 × „fallback font“ nur aus der
`file://`-Darstellung, F15 (Spaltenabstände), F21 (h1 gefolgt von h3). `tools/shots.mjs` 390/820/1280: 39 Aufnahmen,
0 Fehler, kein seitliches Scrollen; index, rubrik und rubrik-2 nach der letzten Textkorrektur noch einmal aufgenommen
(9 Aufnahmen, 0 Fehler).

**Offen:** Die Zettel stehen auf termine und rubrik zu dritt beziehungsweise zu zweit nebeneinander und sind dort fast
gleich groß; das kann wie ein Kartenraster wirken. Die Finish-Prüfung von Hallmark aus frischem Kontext steht weiter aus.
