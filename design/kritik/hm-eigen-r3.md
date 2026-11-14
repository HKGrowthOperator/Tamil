# Prüfung hm-eigen („Tagesblatt“, Linie A), Runde 3
Harte Kriterien: 16 von 16 erfüllt · P0: 0 · P1: 1 · P2: 7 · P3: 5

Grundlage: `design/brief-v3.md`, `design/linien-auftrag.md`, `abgelehnt.md` (Runden 1 bis 7), Hallmark-Floor.
Geprüft über http://127.0.0.1:8951/richtungen/hm-eigen/ am 13.11.2026 (Server danach beendet).
Werkzeuge: `tools/shots.mjs` (13 Seiten × 390/820/1280 = 39 Aufnahmen, Kacheln), `sloplint --genre editorial` mit
11 `--url`, eine eigene Playwright-Messung (berechnete Stile über http, Schriften geladen).

**Abdeckung, ehrlich:** Angesehen habe ich in dieser Runde Startseite und Artikel bei 390 und 1280 (erster Bildschirm
und Folgekacheln). Termine, Kino, Rubrik, Verzeichnis, Eintrag, Einreichen, Werben, Buchen und Kontakt sind über HTML,
CSS, Messwerte und `bericht.json` geprüft, ihre Aufnahmen aber nicht einzeln angesehen (Abbruch auf Anweisung der
Hauptsitzung). Kein neuer Paarvergleich mit Referenzbildern; Kontrast nicht neu gemessen, Farb-Tokens unverändert
gegenüber r2.

## Erster Eindruck
Der erste Bildschirm ist weiter gemacht und nicht generiert: große Tagesziffer, Aufmacher, darunter „Die nächsten
Feste“ mit roten Ziffern für Sonntage und Festtage. Neu trägt die Idee auch die zweite Hälfte der Startseite
(„Zuletzt bei tamil.de“ nach Monaten mit Tagesziffer statt Rubrik-Reihe) und die Rubrikseite; damit ist der Hauptbefund
aus r2 behoben. Wo es noch kippt: das Datum steht bei 1280 doppelt im ersten Bildschirm, die Bedeutung von Rot ist
zwischen den Seiten nicht gleich, und der Beitragsstrom wiederholt neunmal dieselbe Zeile mit Symbolfotos.

## Harte Kriterien

| # | Kriterium (Brief v3 / Linienauftrag) | Handy 390 | Desktop 1280 | Ergebnis |
|---|---|---|---|---|
| 1 | Logo unverändert | md5 `bilder/logo.png` = `inhalte/logo.png` (a880966e…) | dito | erfüllt |
| 2 | Nur Deutsch, kein Tamil als Schmuck | 0 Tamil-Zeichen in allen HTML-Dateien | 0 | erfüllt |
| 3 | Echte Inhalte, Platzhalter sichtbar | Platzhalter gestrichelt (`.fill`); „KBS“ von `buchen.html` entfernt; 35 Min. Reservierung und 90 Tage Löschfrist stehen so in `festlegung-werbung.md` und `datenmodell.md` | dito | erfüllt |
| 4 | Bildnachweis an jedem Bild | jedes `main figure img` hat `figcaption`; Daumen 13 px „Foto: Name, Lizenz“ | dito | erfüllt |
| 5 | Fließtext Handy ≥ 18 px | Absätze in `main` 18 px (Hilfe- und Auswahltexte 16 px) | 18 bis 20,5 px | erfüllt |
| 6 | Kontrast WCAG 2.2 AA | Tokens unverändert gegenüber r2 (dort Minimum 6,03:1, Rot auf Papier) | dito | erfüllt (nicht neu gemessen) |
| 7 | Tippflächen ≥ 44 px | `bericht.json`: 0 Funde | – | erfüllt |
| 8 | Kein seitliches Scrollen 390/820/1280 | 0 px | 0 px (820: 0 px) | erfüllt |
| 9 | `prefers-reduced-motion` | Regel in `hm-eigen.css` und `base.css`; nur Hover-Übergänge | dito | erfüllt |
| 10 | Schriften selbst gehostet, OFL, höchstens zwei Familien | Rethink Sans + Golos Text geladen (`document.fonts`), woff2 + OFL-Dateien | dito | erfüllt |
| 11 | Keine Dachzeilen | Ort jetzt im Datumsblock (`.tag-ort` unter „Sonntag, Deepavali“), nicht mehr als Zeile über dem `h1` | dito | erfüllt |
| 12 | Keine Versal-Labels, keine Sperrung | 0 Elemente auf 11 Seiten | 0 | erfüllt |
| 13 | Keine „·“-Metazeilen | 0 | 0 | erfüllt |
| 14 | Keine Gedankenstriche | 0 auf 11 Pflichtseiten | 0 | erfüllt |
| 15 | Keine gleich großen Kartenraster, Verlauf-Kacheln, Seitenstreifen, „Diese Woche“-Bänder | Listen mit Linien, Radius 2 px, keine Schatten | dito | erfüllt |
| 16 | Seitenliste vollständig | 11 Seiten plus `einreichen-danke`, `buchen-danke`, `kontakt-danke`, `rubrik-2` | dito | erfüllt |

Technik (`bericht.json`): 39 Aufnahmen, 0 Fehler, 0 Konsolenfehler, 0 leere Bilder, 0 ungeladene Schriften.
Hallmark `sloplint` (11 URLs): **0 FAIL, 0 WARN** auf den URLs; die 11 WARN des Gesamtlaufs betreffen nur die
Datei-Renderings über `file://` (Ersatzschrift, bekannt). 138 WAIVED (49b, 59, 77, 78, 79, im Stempel begründet;
sloplint merkt an: fünf Reflex-Ausnahmen sind ein Hausstil und gehören in eine `design.md`), 33 NOTE zu Gate 58
(Startseite 494 sichtbare Wörter, Termine 709, bei 1440 bis 491 Wörter auf einem Bildschirm).

## Status der P1 aus r2

| r2-P1 | Status | Beleg |
|---|---|---|
| 1 Dachzeile im Artikel | **behoben** | `p.ort` entfällt; Orte als `.tag-ort` im Datumsblock (390 und 1280) |
| 2 Bildnachweis nicht an jedem Bild | **behoben** | `figcaption` an jedem Daumen (`.tage.strom .daumen`), z. B. „Foto: Rainer Halama, CC BY-SA 4.0“ |
| 3 Titel stößt ans Bild (390) | **behoben** | Abstand Aufmacher-`h1` → Bild 16 px gemessen |
| 4 Unruhiger Satz im Nachrichtenblock (390) | **behoben** | Startseite ohne Vorspann im Strom; in `rubrik.html` läuft `.teaser` am Handy über die volle Breite (`grid-column: 1 / -1`) |
| 5 Rubrik-Reihe ab Bildschirm 2 | **behoben** | Startseite: „Zuletzt bei tamil.de“ nach Monaten mit Tagesziffer; `rubrik.html` ebenso; keine `.kopfzeile` + „Alles aus …“ mehr |

r2-P2 im Überblick: Ziffernspalte zeigt Anzahl (behoben, „In 11 Kinos: …“), „KBS“ auf Leserseite (behoben), Kopf wie
Runde 2 (geändert: Datum im Kopf, drei Dienste, Rubriken im Menü), Verzeichnis Liste zuerst (laut CSS behoben, Filter in
`details`; Aufnahme nicht angesehen), Loch linke Spalte 1280 (jetzt gespiegelt, siehe P2-3), Kino „Nach Stadt“
(teilweise, siehe P3-2).

## Paarvergleich
Nicht neu aufgenommen (siehe Abdeckung). Beobachtete Änderung gegenüber dem r2-Vergleich mit Runde 2 (1280): Der Kopf
ist nicht mehr deckungsgleich (statt fünf grauer Rubriken jetzt Datum, „Termine, Kino, Verzeichnis“ fett und
„Rubriken +“). Gegenüber Runde 4 unverändert: kein rotes Riesenwort, Rot nur auf Ziffern und „Sonntag, Deepavali“,
größte Schrift die Tagesziffer in Tinte (48 / 73,6 px), Schlagzeile 30 / 39,7 px.

## Gemacht oder generiert, konkret
Gemacht: Tagesblatt-Kopf; „Die nächsten Feste“; Artikelkopf „8 / November 2026 / Sonntag, Deepavali / Berlin,
Düsseldorf, München“; Strom nach Monaten mit Tagesziffer auf Startseite, Rubrik, Weiterlesen und „Bei tamil.de
erwähnt“. Die Datumsspalte hält jetzt die ganze Leserseite zusammen.
Vertraut bis generisch: die Stromzeile selbst (Ziffer, Titel, Rubrik und Ort, Daumen rechts) ist das Muster eines
Archivs; Fuß in vier Spalten; Formulare mit Standardfeldern; Werben als Liste mit Formatrahmen. Nichts davon ist laut
oder Baukasten, aber dort liegt das Austauschbare.

## Befunde

### P0
keine.

### P1
1. **Datum doppelt und in zwei Formen im ersten Bildschirm.** `index.html`, 1280 (bis 1040 px Breite sichtbar),
   `.kopf-datum` „Freitag, 13. November 2026“ und 60 px darunter `.blatt-tag` „13 / November 2026 / Freitag“. Das
   Erkennungszeichen wird von einer gewöhnlichen Datumszeile im Kopf gedoppelt; nach Bogen B „Daten in wechselnder
   Form im ersten Bildschirm“. Abhilfe: `.kopf-datum` auf der Startseite weglassen (dort trägt das Tagesblatt das
   Datum); auf den übrigen Seiten behalten oder ebenfalls streichen.

### P2
1. **Rot bedeutet nicht überall dasselbe.** Gleicher Beitrag, andere Farbe: „Steinmeier beim Tempelfest in Hamm“
   (So, 26. Juli) ist auf `termine.html` rot, auf `index.html`, `rubrik.html` und `artikel.html` (Weiterlesen) schwarz;
   „Sri Ganesha Hindu Temple geweiht“ (So, 7. Juni) rot auf `termine.html`, schwarz auf `verzeichnis-eintrag.html`;
   „Film Akka in Biel“ (So, 15. Feb.) rot auf `kino.html`. Ursache: `strom_zeile` färbt nur Festtage, `zeile` färbt
   Sonntage und Festtage. Die Legende auf `termine.html` sagt „Rot steht für einen Termin an einem Sonntag oder an einem
   Festtag“. Abhilfe: eine Regel für alle Listen (entweder überall Sonntag und Festtag, oder Rot nur bei Terminen und
   nie bei Beiträgen, dann auch nicht in „Zurückliegend“ und „Aus dem Kinojahr“).
2. **Strom gleichförmig, viel Leerraum je Zeile.** `index.html` „Zuletzt bei tamil.de“, 390: neun Zeilen in genau
   gleicher Form (Ziffer, Titel, Rubrik und Ort, Daumen 192 × 128, Nachweis), Seite 6058 px hoch; 1280: Titel endet
   bei x ≈ 1000, Daumen bei x = 1037, Zeile ≈ 180 px hoch für einen einzeiligen Titel, Mitte leer. Abhilfe: Daumen am
   Handy nur beim jeweils ersten Beitrag eines Monats oder kleiner neben den Titel; bei 1280 Vorspann in die leere
   Mitte (wie `rubrik.html` mit `mit-teaser`) oder zwei Spalten je Monat.
3. **Loch rechts unter dem Aufmacherbild.** `index.html`, 1280: Bildnachweis endet bei y ≈ 795, linke Spalte („Alle
   Spielorte“) bei y ≈ 910; rechts ≈ 115 px leer bis zum nächsten Abschnitt (r2-P2-1 gespiegelt). Abhilfe: Bildhöhe
   an die Spalte binden oder „Im Kino“ unter das Bild in die rechte Spalte.
4. **Verrutschte Kante im Artikel.** `artikel.html`, 1280: `h1` und Vorspann beginnen bei x = 370, der Fließtext bei
   x = 362 (8 px gemessen), weil Kopf (3/9) und Text (3/6/3) verschiedene Raster haben. Abhilfe: beide auf dasselbe
   Raster (z. B. Kopf ebenfalls 3/6/3 oder gleiche `grid-template-columns`).
5. **Dasselbe Foto mehrfach auf einer Seite.** `rb-30.jpg` und `rb-49.jpg` sind dieselbe Datei (md5 2cd3fa30…).
   `verzeichnis-eintrag.html`: einmal groß, zweimal als Daumen (dreimal dasselbe Foto); `artikel.html`: Aufmacherbild
   und Daumen „Berlin: Sri Ganesha Hindu Temple geweiht“ in Weiterlesen. Abhilfe: bei gleichem Bild den Daumen
   weglassen (Zeile ohne Bild) oder ein zweites belegtes Motiv wählen.
6. **Symbolbilder nicht als solche erkennbar.** Strom auf `index.html` und `rubrik.html`, alle Breiten: Kottu-Teller zu
   „Kündigung trifft Restaurant Maneez“, Rathaus Emsdetten zum TKS e.V., Reichstag zur Bundestagsdrucksache, Saraswati-
   Relief aus Tamil Nadu zu Vaani Vizha in Deutschland. Der Nachweis nennt nur Fotograf und Lizenz. Abhilfe:
   „Symbolbild“ bzw. „Archivbild“ vor den Nachweis, wie es Nachrichtenseiten tun; wo kein passendes Bild da ist, Zeile
   ohne Bild.
7. **Hierarchie im ersten Bildschirm verdreht.** `index.html`, 1280, linke Spalte: Festtitel in „Die nächsten Feste“
   16 px, darunter Filmtitel „Scene“, „Ramayana: Rise of a Legend“ ≈ 25 px (`.naechste .tage.filme .was`); der
   Nebenblock wiegt schwerer als der Hauptblock. Abhilfe: Filmtitel auf die Größe der Festtitel oder Feste größer.

### P3
1. Bildnachweise der Daumen 13 px (`.tage.strom .daumen figcaption`, `--text-xs`); für ältere Leser 14 px.
2. `kino.html` „Nach Stadt“: weiter sieben Zeilen Stadt und Film unter einem Platzhalter „Kinos und Uhrzeiten folgen“;
   der Job „welcher Film läuft wo“ endet bei der Stadt. Solange keine Spielorte da sind, „Im Programm“ genügt.
3. `werben.html` und `buchen.html`: Billboard „Startseite, zwischen den Rubriken“; die Startseite hat keine
   Rubrikblöcke mehr. Ort neu beschreiben (z. B. „Startseite, zwischen den Monaten“).
4. `termine.html` „Zurückliegend in 2026“: Monatsköpfe zählen „2 Termine“, der Satz darüber sagt „Worüber wir berichtet
   haben“; es sind Beiträge. Einheitlich „Beiträge“ oder echte Termine.
5. Hallmark Gate 58 (NOTE): `termine.html` 709 sichtbare Wörter, 491 auf einem Bildschirm bei 1440 (alle Monate
   aufgeklappt ab November offen); Monate vor dem aktuellen standardmäßig zu lassen.

## Was trägt
- Die Tagesziffer zieht jetzt von der Startseite bis in Rubrik, Artikel, Verzeichnis-Eintrag und Buchungskalender
  durch; die zweite Hälfte der Startseite gehört nicht mehr dem Portal-Baukasten.
- Ruhe ohne Lärm: zwei Familien, kein Versal, kein „·“, kein Gedankenstrich, Radius 2 px, Rot ≥ 6:1 nur auf Ziffern.
- Artikelkopf mit Ort und Festtag im Datumsblock: eigen, lesbar, ohne Dachzeile.

## Bedienbarkeit (nur zur Information)

| Heuristik | 0 bis 4 | Satz |
|---|---|---|
| 1 Systemstatus | 3 | „Heute, kein Termin“, „Schritt 1 von 5“, `aria-current` im Kopf. |
| 2 Sprache der Nutzer | 3 | deutsch und klar; „Termine“ für Beiträge auf `termine.html` irritiert. |
| 3 Kontrolle | 3 | Monate auf- und zuklappbar, Filter zurücksetzen. |
| 4 Konsistenz | 2 | Rot je Seite anders; Datum doppelt im Kopf. |
| 5 Fehlervermeidung | 3 | „freiwillig“ markiert, Hilfetexte 16 px je Feld. |
| 6 Wiedererkennen | 3 | Dienste dauerhaft im Kopf, Rubriken im Menü. |
| 7 Effizienz | 3 | Verzeichnis laut CSS mit Liste zuerst; Startseite am Handy 6058 px lang. |
| 8 Ästhetik, Reduktion | 3 | ruhig; Strom wiederholt dieselbe Zeile, Symbolfotos. |
| 9 Fehlerhilfe | 2 | Fehlerzustände der Formulare nicht gesehen. |
| 10 Hilfe | 3 | Legende für Rot, „So geht es weiter“. |

Hinweis zur Prüfung selbst: `sloplint` schreibt Aufnahmen nach `design/richtungen/hm-eigen/.hallmark/shots/` und hat
dort die Datei-Renderings der elf Seiten überschrieben (21:42 bis 21:43); meine URL-Aufnahmen habe ich nach
`/tmp/claude-0/-home-user/328bcd38-019d-5546-955b-7fea86a20fa1/scratchpad/kritik-A-r3/hallmark-shots/` verschoben.
Gestaltungsdateien sind unverändert.
