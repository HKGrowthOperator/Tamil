# Prüfung hm-eigen („Tagesblatt“, Linie A), Runde 2
Harte Kriterien: 14 von 16 erfüllt · P0: 0 · P1: 5 · P2: 6 · P3: 6

Grundlage: `design/brief-v3.md`, `design/linien-auftrag.md`, `abgelehnt.md` (Runden 1 bis 7). Geprüft über
http://127.0.0.1:8951/richtungen/hm-eigen/ am 13.11.2026. Aufnahmen mit `tools/shots.mjs` (390/820/1280, 11 Seiten,
33 Aufnahmen), Messungen mit Playwright (berechnete Stile, Kontrast über Canvas aus oklch umgerechnet).

## Erster Eindruck
Der erste Bildschirm ist gemacht und nicht generiert: Die große Tagesziffer „13 / November 2026 / Freitag“, darunter
die nächsten Feste mit roten Ziffern nur für Sonntage und Festtage (mit Legende auf `termine.html`), ist eine Idee, die
aus dem Inhalt kommt und nur tamil.de gehört. Ab dem zweiten Bildschirm kippt die Startseite in eine Rubrik-Reihe
(Kino, Tempel und Vereine, Nachrichten, Küche, Kultur und Sport, je Kopf plus „Alles aus …“ und Daumenliste), und die
Idee ist dort nicht mehr zu sehen. Ruhig, lesbar und frei von Lärm; die Schwächen liegen in Fugen und in der
zweiten Hälfte der Startseite, nicht in Rot oder Effekten.

## Harte Kriterien

| # | Kriterium (Brief v3 / Linienauftrag) | Handy 390 | Desktop 1280 | Ergebnis |
|---|---|---|---|---|
| 1 | Logo unverändert | md5 `bilder/logo.png` = `inhalte/logo.png` | dito | erfüllt |
| 2 | Nur Deutsch, kein Tamil als Schmuck | 0 Tamil-Zeichen auf 11 Seiten | 0 | erfüllt |
| 3 | Echte Inhalte, Platzhalter sichtbar | Stichproben „Scene“, „Ramayana“, THADAM, Basel Tamil Sangam, Verzeichnisnamen in Quellen gefunden; Platzhalter gestrichelt (`.fill`) | dito | erfüllt |
| 4 | Bildnachweis an jedem Bild | Aufmacher, Küche, Rubrik-Aufmacher am Bild; Daumenbilder (`.daumen img`, z. B. rb-71, rb-76, rb-49, rb-80, rb-38, rb-78, rb-30) nur als Sammelliste im Fuß, keinem Bild zuordenbar | dito | **verletzt** |
| 5 | Fließtext Handy ≥ 18 px | alle Absätze in `main` 18 px | 18 bis 20,5 px | erfüllt |
| 6 | Kontrast WCAG 2.2 AA | Minimum 6,03:1 (Rot auf Papier), Tinte ≥ 7,2:1 | dito | erfüllt |
| 7 | Tippflächen ≥ 44 px | `bericht.json`: 0 Funde | – | erfüllt |
| 8 | Kein seitliches Scrollen 390/820/1280 | 0 px | 0 px (820 ebenfalls 0) | erfüllt |
| 9 | `prefers-reduced-motion` | Regel in `hm-eigen.css` und `base.css`; nur Hover-Übergänge 120 bis 220 ms | dito | erfüllt |
| 10 | Schriften selbst gehostet, OFL, höchstens zwei Familien | Rethink Sans + Golos Text, woff2 + OFL-Dateien in `schriften/` | dito | erfüllt |
| 11 | Keine Dachzeilen | `artikel.html`: `p.ort` „Berlin, Düsseldorf, München“ klein und grau direkt über dem `h1` | dito | **verletzt** |
| 12 | Keine Versal-Labels, keine Sperrung | 0 Elemente | 0 | erfüllt |
| 13 | Keine „·“-Metazeilen | 0 | 0 | erfüllt |
| 14 | Keine Gedankenstriche | 0 auf den 11 Pflichtseiten; in `artikel-48/71/83` nur in wörtlichen Titeln und Zitaten | dito | erfüllt (P3-Hinweis) |
| 15 | Keine gleich großen Kartenraster, Verlauf-Bildkacheln, Seitenstreifen, „Diese Woche“-Bänder | keine; Listen mit Linien, Radien 2 bis 3 px, keine Schatten außer Eingabefeldern | dito | erfüllt |
| 16 | Seitenliste vollständig | 11 Seiten plus Danke-Zustände (`einreichen-danke`, `buchen-danke`, `kontakt-danke`), Seitennavigation in `rubrik.html` | dito | erfüllt |

Technik (`bericht.json`): 33 Aufnahmen, 0 Fehler, 0 Konsolenfehler, 0 leere Bilder, 0 ungeladene Schriften.

## Gemacht oder generiert, konkret

Gemacht:
- Tagesziffer als Seitenkopf (`time` 48 px Handy, 73,6 px Desktop, Rethink Sans 800, Tinte, nicht Rot) und dieselbe
  Ziffernspalte in „Die nächsten Feste“, `termine.html`, im Artikelkopf („8 / November 2026 / Sonntag, Deepavali“)
  und im Buchungskalender (`buchen.html`, „So“, 13, 27 rot). Rot hat eine Bedeutung und wird erklärt.
- Artikel: Datumskopf links, schmale Textspalte, Seitenspalte „Im Kalender“. Ruhig und eigen.
- Verzeichnis: „Premium“ als Wort und getönte Zeile, ehrlich gekennzeichnet, ohne Schmuck.

Generiert (aus dem Werkzeugkasten Nachrichtenportal):
- Startseite ab Bildschirm 2: fünf Blöcke `.kopfzeile` mit `h2` links und `.mehr` „Alles aus …“ rechts, darunter
  `ul.berichte` mit Daumen 104 × 69 (Handy) bzw. 160 × 107 (Desktop) links und Titel rechts. Das ist die
  „Rubrik-Reihe“, die Brief v3 als generisch nennt. Daten stehen dort als 14-px-Metazeile, nicht als Tagesziffer.
- Kopf bei 1280: Logo links, graue Rubriken (Nachrichten, Community, Kultur, Küche, Sport) in 400er Schnitt, Haarlinie
  darunter. Fast deckungsgleich mit dem Kopf von Runde 2.
- Formulare (`einreichen`, `verzeichnis`, `buchen`, `kontakt`): Standardfelder mit 1-px-Rahmen und schwarzem Knopf;
  sauber, aber ohne Bezug zur Idee.

## Trägt die Idee über alle Seitentypen?

| Seite | Idee sichtbar? | Beobachtung |
|---|---|---|
| index | nur erster Bildschirm | danach Rubrik-Reihe |
| artikel | ja | Datumskopf mit Festtag in Rot, „Im Kalender“ |
| termine | ja, Kern | „Ab heute“, Monate darunter, Legende für Rot |
| kino | teilweise | Ziffernspalte zeigt Anzahl Kinos (11, 2), nicht Tage |
| verzeichnis, eintrag | nein | neutral, ordentlich |
| einreichen | nein | Datumsfeld ist ein Standard-Eingabefeld |
| werben | nein | Formatrahmen, sachlich |
| buchen | ja | Kalender mit roten Sonntagen |
| rubrik | nein | Liste mit Daumen und 14-px-Metazeile |

## Paarvergleich

**BBC Handy (390):** BBC setzt das Bild randlos direkt unter die Markenleiste und den Titel mit 16 px Abstand darunter;
bei hm-eigen stößt der Titel ohne Abstand (0 px gemessen) auf das Bild. BBC zeigt im ersten Bildschirm drei
Geschichten, hm-eigen eine Geschichte und drei Termine: weniger Nachrichten, dafür ein eigener Inhaltstyp.

**NZZ Desktop (1280):** NZZ trennt Haupt- und Nebenspalte mit einer senkrechten Haarlinie und füllt beide bis zur
Falz; bei hm-eigen endet die linke Kalenderspalte nach „Ganzer Festkalender“ rund 200 px vor dem Bildende, die Fläche
darunter bleibt leer. NZZ setzt den Titel unter das Bild, hm-eigen Titel, Vorspann und WhatsApp darüber: für Handy und
Teilen günstiger.

**Runde 2 (390/1280):** Grund #F6F8F3 (kühl, leicht grünlich) statt Creme; Bilder eckig statt 12 px gerundet; keine
Rubrikpunkte, keine Anzeige über dem Aufmacher, keine Serife im Fließtext. Gleich geblieben: der Kopf bei 1280
(siehe oben).

**Runde 4, Raster (390/1280):** kein rotes Riesenwort, keine Versal-Navigation, keine Kastenlinien; Rot nur auf zwei bis
drei Tagesziffern je Bildschirm (≈ 30 px Ziffern, 6,03:1). Größte Schrift ist die Tagesziffer in Tinte (48/73,6 px),
Schlagzeile 30/39,7 px, kein verzerrter Schnitt.

**Runden 5 bis 7:** keine Versal-Labels, keine „·“-Zeilen, keine Kacheln mit Verlauf, kein „Diese Woche“-Band. Offen
bleiben die Rubrik-Reihe auf der Startseite und die Ortszeile über dem Artikeltitel.

## Befunde

### P0
keine.

### P1
1. **Dachzeile im Artikel.** `artikel.html`, 390 und 1280, `.artikel-kopf p.ort` („Berlin, Düsseldorf, München“)
   steht klein und grau direkt über dem `h1`. Abhilfe: Orte in den Datumsblock ziehen (unter „Sonntag, Deepavali“ in
   `.tag-rest`) oder unter den Vorspann; dann trägt die Zeile die Tagesblatt-Idee statt eines Portalmusters.
2. **Bildnachweis nicht an jedem Bild.** `index.html`, `rubrik.html`, `artikel.html`, `verzeichnis-eintrag.html`, alle
   Breiten, `.berichte .daumen img`: Nachweis nur als Sammelliste „Bildnachweise“ im Fuß ohne Zuordnung (11 Einträge,
   welcher zu welchem Daumen gehört, bleibt offen). Abhilfe: Kurznachweis je Daumen (z. B. 13 px unter dem Bild oder
   am Ende der Metazeile „Foto: Name, CC BY-SA 4.0“) oder Fußliste mit Beitragstitel je Eintrag.
3. **Erster Bildschirm Handy: Titel stößt ans Bild.** `index.html`, 390, Aufmacher-`h1` → erstes `main img`: Abstand
   0 px, während Datum → Titel ≈ 20 px und Bildunterschrift → Vorspann 16 px. Ungleiche Abstände im ersten
   Bildschirm. Abhilfe: `margin-block-end: var(--space-md)` am Aufmacher-`h1` (16 px), gleiche Fuge wie unter der
   Bildunterschrift.
4. **Unruhiger Satz im Nachrichtenblock.** `index.html`, 390, `.berichte p.teaser` neben dem Daumen: Spalte 242 px bei
   18 px Golos, rund 24 bis 27 Zeichen je Zeile, Vorspann bis 259 px hoch (zehn und mehr Zeilen mit starkem
   Flatterrand). Abhilfe: am Handy Vorspann unter Daumen und Titel über die volle Breite laufen lassen oder dort
   weglassen; Daumen nur neben dem Titel.
5. **Rubrik-Reihe statt Tagesblatt ab Bildschirm 2.** `index.html` (390 ab ≈ 1250 px, 1280 ab ≈ 860 px) und
   `rubrik.html`: fünf Blöcke `.kopfzeile` + `.mehr` „Alles aus …“ + Daumenliste, Datum als 14-px-`p.meta`. Das ist das
   in Brief v3 genannte Muster „Rubrik-Reihen“, und die Idee der Linie endet am ersten Bildschirm. Abhilfe: die zweite
   Hälfte der Startseite nach Tagen ordnen wie „Zurückliegend in 2026“ auf `termine.html` (Tagesziffer links, Titel,
   Ort; Monatsköpfe), Rubrik nur als Wort in der Zeile; in `rubrik.html` dieselbe Ziffernspalte statt Metazeile.

### P2
1. **Loch in der linken Spalte, Desktop.** `index.html`, 1280, unter `Ganzer Festkalender`: ≈ 200 px leere Fläche bis
   zum Bildende. Abhilfe: zwei weitere Termine oder „Zuletzt“ (zwei Tageszeilen) in die Spalte, oder Bildhöhe an die
   Spalte binden.
2. **Ziffernspalte zeigt Anzahl statt Tag.** `index.html` Kino-Block und `kino.html` „Im Programm“, alle Breiten:
   „11 / Kinos“, „2 / Kinos“ im selben Satz wie „15 / So, Nov.“; liest sich in fünf Sekunden als Datum. Abhilfe:
   Anzahl in die Ortszeile („in 11 Kinos: Berlin, …“), Ziffernspalte nur für Tage.
3. **Kino „Nach Stadt“ ohne Nutzen.** `kino.html`, alle Breiten: sieben Zeilen mit identischem „Kino und Uhrzeiten
   folgen“; der Job „welcher Film läuft wo“ endet bei der Stadt. Abhilfe: solange keine Spielorte vorliegen, eine Zeile
   je Stadt mit Film und einem einzigen Platzhalter darüber, Liste nicht künstlich verlängern.
4. **Verzeichnis am Handy: kein Eintrag im ersten Bildschirm.** `verzeichnis.html`, 390: Suche, fünf Art-Knöpfe, drei
   Auswahlfelder und „Filter anwenden“ vor der Liste; „12 Einträge, Premium zuerst“ erst bei ≈ 1240 px. Abhilfe: Liste
   zuerst, Filter in einem `details` „Filter: Art und Ort“ über der Liste.
5. **Kopf wie Runde 2.** alle Seiten, 1280, `.kopf`: Logo links, graue Rubriken in Runde-2-Reihenfolge, Haarlinie.
   Abhilfe: Kopf an die Idee binden (z. B. Tagesdatum im Kopf, Rubriken ins Menü und in den Fuß, im Kopf nur die drei
   Dienste).
6. **Interne Projektsprache auf Leserseiten.** `buchen.html` „Die Werte unten sind Beispiele, bis KBS Preise und
   Termine liefert“, „Preis je Laufzeit: folgt von KBS“. Abhilfe: „Preis folgt“ wie im Linienauftrag gefordert,
   Lieferant nicht nennen.

### P3
1. Hilfetexte `p.hilfe` und Metazeilen `p.meta` 14 px, Legende `p.legende` auf `termine.html` 16 px; für ältere Leser
   die Legende auf 18 px, Hilfetexte auf 16 px.
2. `verzeichnis.html`: Filter „Dienstleister (0)“ führt ins Leere; ausblenden oder deaktiviert zeigen.
3. Wortlaut „Per WhatsApp teilen“ (`artikel.html`) gegen „Per WhatsApp schicken“ (übrige Seiten); einheitlich.
4. `einreichen.html`/`buchen.html`: Datumsfelder zeigen in der Aufnahme „mm/dd/yyyy“ (Gebietsschema des
   Prüfbrowsers); mit deutschem Hinweistext unter dem Feld absichern.
5. `termine.html`: Zeile „13 / Fr, Nov. / Heute“ ohne Termin; entweder „Heute kein Termin“ oder weglassen.
6. Gedankenstriche in wörtlichen Titeln/Zitaten (`artikel-48`, `-71`, `-83`); als Zitat belassen ist vertretbar,
   Gate 19 bewusst ausnehmen.

## Was trägt
- Die Tageszeile (Ziffer, Wochentag, Titel, Ort) mit Rot als Bedeutung für Sonntage und Festtage: eigen, lesbar,
  erklärt, über Startseite, Artikel, Termine und Buchungskalender gleich gesetzt.
- Ruhe ohne Lärm: zwei Familien, kein Versal, kein „·“, Radien 2 bis 3 px, Rot ≥ 6:1 und nur auf Ziffern.
- Artikelseite: Datumskopf, schmale Textspalte (18 px Handy), „Im Kalender“ als Weiterlesen mit Bezug.

## Bedienbarkeit (nur zur Information)

| Heuristik | 0 bis 4 | Satz |
|---|---|---|
| 1 Systemstatus | 3 | „Heute“-Zeile und Schrittanzeige „Schritt 1 von 5“ zeigen, wo man ist. |
| 2 Sprache der Nutzer | 3 | klar und deutsch; „KBS“ auf `buchen` ist Innensicht. |
| 3 Kontrolle | 3 | „Filter zurücksetzen“, Monate auf- und zuklappbar. |
| 4 Konsistenz | 2 | Ziffernspalte einmal Tag, einmal Anzahl; „teilen“ gegen „schicken“. |
| 5 Fehlervermeidung | 3 | „freiwillig“ markiert, Hilfetexte je Feld. |
| 6 Wiedererkennen | 3 | Dienste dauerhaft im Kopf. |
| 7 Effizienz | 2 | Verzeichnis am Handy erst nach langem Filterblock. |
| 8 Ästhetik, Reduktion | 3 | ruhig; Kino „Nach Stadt“ wiederholt Platzhalter. |
| 9 Fehlerhilfe | 2 | Fehlerzustände der Formulare nicht gesehen. |
| 10 Hilfe | 3 | Legende für Rot, „So geht es weiter“ beim Einreichen. |
