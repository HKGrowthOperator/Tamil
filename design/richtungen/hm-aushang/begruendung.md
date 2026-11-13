# Linie C „Aushang“ (hm-aushang)

tamil.de als das Schwarze Brett der tamilischen Gemeinden in Deutschland, Österreich und der Schweiz: Jede datierte
Sache hängt als Aushang mit ihrem Datum als Kopf aus, schwarz auf Weiß, mit Haarlinien; nur der nächste Termin ist rot.

## Picks

**Hallmark · v2.0.0**

- **Shape** · Aushang (eigene Form: geordnete Reihen datierter Aushänge, der Aufmacher neben seinem Bild), aus Draw c53a1a; getauscht: der Draw gab Split Studio, das Material ist aber eine Tafel datierter Meldungen · genre editorial · job: visit (was hängt aus, was kommt als Nächstes, wo)
- **Theme** · Ink by request (weißes Papier, Schwarz ohne Farbton, Epilogue 700 über 400, Haarlinien) · Dials: Radius 6 statt 12, keine Pillen, kein IBM Plex Mono (impeccable-Ausschlussliste), Papier kühl statt 100°-Ton
- **Signal** · auf Logo-Rot umgestimmt (oklch 50.8% 0.177 25.6 = #B5282A). Grund: Petrol neben dem roten Logo wären zwei bunte Farben auf Weiß (Runde 1: „zu viele Farben“); ein Aushang ist Schwarz mit einer roten Auszeichnung wie der rote Tag im Kalender. Rot ist nie Fläche und nie Tönung (rosa Kästen sind Runde 3), nur Schrift: Datum und Wort des nächsten Termins, aktuelle Seite in der Navigation, „Läuft“ im Kino, Unterstreichung beim Überfahren, die Heute-Linie im Festkalender
- **Chrome** · nav: Aushangzeile („Als Nächstes: …“) über einer Leiste mit Logo, sieben Rubriken und „Termin einreichen“, unter 75rem Menü als Ausklapper; die Zeile zieht sich nicht zurück, die Seite bleibt still · footer: Kolophon (Logo, ein Satz, Links)
- **Hero** · Stage: Titel, ein Satz, zwei Knöpfe auf 5 Spalten, Tempelbild 4:3 auf 7 Spalten mit Bildnachweis; Unterseiten mit Banner-Kopf
- **Signature** · das Datum als Kopf jedes Aushangs: Tagesziffer in Epilogue 700 (44 px Desktop, 32 px Handy), Monat und Wochentag daneben, „Übermorgen / In 8 Tagen“ am Rand, „Per WhatsApp schicken“ unter jedem Termin; der nächste in Rot
- **Sections (Start)** · Aufmacher · Was als Nächstes aushängt (Reihen) · Nachrichten (Bild 7, Reihen 5) · Kino diese Woche (Band, Filmtitel groß, Städte) · Community (Reihen 7, Bild 5) · Anzeige (Eigenanzeige Billboard, gekennzeichnet) · Küche, Kultur und Sport (Bild mit Reihen, Reihen) · Verzeichnis (Band) · Fuß
- **Type** · Epilogue (OFL, selbst gehostet, Lizenz in `schriften/`), Gewichte 400/600/700; Fließtext 18 px Handy, 19 px im Artikel bei 65 Zeichen; Titel nie in Versalien, keine Dachzeilen, keine Labels in Versalien, keine „·“-Metazeilen
- **Material** · real: 20 Rückblick-Beiträge mit Commons-Bildern und Nachweis, 62 Chronik-Einträge, Kino-Woche 9.11., Termine Düsseldorf 15.11. (Beitrag 30), Basel 21.11. (inhalte.json), Kloten 15.11. und Bern 13.12. (wartende Radar-Entwürfe 5 und 4), Werbeplätze aus `ads.php`, Formularfelder aus §12/§14, Logo · absent (sichtbare Platzhalter): Kontaktdaten der Einrichtungen, Preise („Preis folgt“), Einwilligungstext und Verkaufsbedingungen (KBS), E-Mail und Telefon der Redaktion, Impressum
- **Sweep** · Floor 0 FAIL über http · Reflex 0 offen (6 waived: 22, 44c, 49b, 71, 77, 79) · dismissed 58 (Startseite listet Schlagzeilen, Aufmacher-Titel hat 8 Wörter) · Seiten mit vollem Redaktionstext (`wortlaut.css`: Artikel, Festkalender, Kino, Community Seite 2) tragen `copy: verbatim` · finish-review: nicht gelaufen (kein frischer Prüfer in diesem Lauf)

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
