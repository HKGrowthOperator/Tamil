# Linie A „Tagesblatt“ (hm-eigen) – Begründung

Stand 13.11.2026, Runde 4 (nach `design/kritik/hm-eigen-r1.md`, `-r2.md` und `-r3.md`). Gestaltet nach `design/brief-v3.md` mit Hallmark
(eigene Richtung). Alle Seiten erzeugt der Generator `bauen.py` aus echtem Material; von Hand geschrieben ist nur
`hm-eigen.css`.

## Idee

tamil.de ordnet sich wie der Kalender in der tamilischen Küche: jeder Beitrag an seinem Tag, das Datum vorn. Das
Erkennungszeichen ist die **Tageszeile** (Ziffer, Titel, Ort, Linie statt Kasten). Rot bedeutet nur „Sonntag oder
Festtag“, klein, nie als Fläche und nie als Riesenschrift.

## Hallmark-Picks

| Achse | Wahl |
|---|---|
| Shape | Tagesblatt (eigene Form): Datum, die nächsten Feste und das Kino links, Aufmacher mit Bild rechts; darunter „Zuletzt bei tamil.de“ nach Tagen mit Monatsköpfen |
| Papier | Jasminweiß `oklch(97.6% 0.007 120)`, Tinte `oklch(21% 0.022 155)`, Mulde `paper-2` für Nachrichten und Fuß |
| Rot | Logo-Rot `oklch(50.5% 0.175 25)`: überall eine Regel, Ziffer in jeder Tageszeile an Sonntagen und Festtagen, Wochentag „Sonntag“/Festname im Datumsblock, Sonntage im Buchungskalender, Fokusring. Kein roter Knopf mehr |
| Schrift | Rethink Sans 600 für Köpfe, 800 nur für Ziffern; Golos Text für Lesetext (beide OFL, selbst gehostet, Lizenzen in `schriften/`). Drei Gewichte: 400, 600, 800 |
| Signatur | die Tageszeile; sie trägt Startseite, Rubrik, Weiterlesen, Festkalender, Erwähnungen im Verzeichnis und den Buchungskalender. Die Ziffernspalte zeigt nur Tage |
| Haltung | geteilt (split), Linien statt Kästen, keine Karten, keine Vollfarbflächen |
| Bilder | Fotos aus Commons mit Nachweis am Bild, auch an jedem Daumenbild (Kurznachweis darunter); volle Nachweise mit Link im Fuß |
| Chrome | Kopf: Logo, Tagesdatum (nicht auf der Startseite, dort trägt es das Tagesblatt), drei Dienste (Termine, Kino, Verzeichnis), Rubriken im Menü; Fuß mit Rubriken, Diensten, Bildnachweisen |
| Sweep | siehe Prüfung unten |

## Seiten

| Datei | Inhalt |
|---|---|
| `index.html` | Startseite |
| `rubrik.html`, `rubrik-2.html` | Community nach Tagen mit Monatsköpfen, Bild und Vorspann, Seitennavigation (5 je Seite); dazu `rubrik-nachrichten/-kultur/-kueche/-sport.html`, damit kein Rubrik-Link ins Leere führt |
| `artikel.html` | Deepavali (Beitrag 30); dazu 19 weitere `artikel-<id>.html` |
| `termine.html` | Festkalender: „Ab heute“ zuerst, darunter „Zurückliegend in 2026“ nach Monaten, absteigend, eingeklappt |
| `kino.html` | Im Programm, nach Stadt (Platzhalter für Kinos und Uhrzeiten), Kinojahr 2026 |
| `verzeichnis.html` | Suche, Filter Art und Ort (Land, Bundesland/Kanton, Stadt), Liste mit Premium oben |
| `verzeichnis-eintrag.html` | Profil Sri Ganesha Hindu Temple (Premium sichtbar, als Darstellungsbeispiel gekennzeichnet); dazu 11 weitere `verzeichnis-<slug>.html` |
| `einreichen.html`, `einreichen-danke.html` | Termin einreichen (Felder aus §12, Einwilligung, Bildrecht, verstecktes Feld) und Bestätigung mit Vorgangsnummer |
| `werben.html` | sechs Plätze mit Formaten im gleichen Maßstab gezeichnet, Preistabelle „folgt“, Ablauf der Buchung |
| `buchen.html`, `buchen-danke.html` | Buchung in fünf Schritten (Platz und Laufzeit, Startdatum mit belegten Tagen, Angaben, Werbemittel, Prüfen und Zahlung bei Stripe) und Kundenübersicht „Bezahlt, in Prüfung“ |
| `kontakt.html`, `kontakt-danke.html` | Formular „Nachricht“, Redaktionsdaten als Platzhalter |

## Überarbeitung nach Kritik r1 (P1)

1. **Küche/Community am Desktop:** Listen als „Berichte“ (Daumenbild, Titel, Datum und Ort) in zwei Spalten oder als
   Aufmacher mit Liste daneben; kein Raster mehr mit 110 px Titelspalte.
2. **Kino:** keine grüne Fläche, kein Riesenwort. Filme als Zeilen (Zahl der Kinos links, Titel ≤ 28 px, Städte),
   Überschrift „Kino“ mit Stand-Datum statt „diese Woche“.
3. **Rote Ziffer:** Datumsblock höchstens 88 px und immer in Tinte; Rot nur als Wort („Sonntag, Deepavali“). Rote
   Ziffern nur noch in Tageszeilen (≤ 40 px) und nur bei Terminen an Sonntagen und Festtagen, nicht bei Berichten.
4. **Erster Bildschirm:** am Handy Schlagzeile, Foto, Vorspann und der Anfang von „Die nächsten Feste“; am Desktop
   Aufmacher mit Bild und drei kommende Feste.
5. **Knopf und Köpfe:** Aufmacher-Titel und Bild verlinkt, kein roter Knopf; Abschnittsköpfe 22 bis 28 px ohne
   Unterzeile. Der einzige gefüllte Knopf ist Tinte.
6. **Festkalender:** beginnt mit „Ab heute“; nur echte Termine (Feste, Feiern, Aufführungen, Filmstarts), keine
   Studien, Apps, Konsulartage, Meistertitel oder Restaurants.
7. **Tippflächen:** alle Links, Knöpfe und Formularfelder ≥ 44 px (shots.mjs meldet bei 390 und 820 nichts mehr).

Mitgenommen aus P2/P3: Rubrik-Links haben Ziele, Menü mit „+“, einheitlicher Datumsblock, Abschnittsabstand 64 px,
Monatsleiste ersetzt, Teilen-Links 16 px, keine rohe URL im Nachweis, Köpfe 600 statt 800.

## Überarbeitung nach Kritik r2

P1:
1. **Dachzeile im Artikel weg:** Die Orte stehen jetzt im Datumsblock unter Wochentag und Festtag.
2. **Nachweis an jedem Bild:** Jedes Daumenbild trägt seinen Kurznachweis („Foto: Name, Lizenz“) direkt darunter; der
   volle Nachweis mit Link bleibt im Fuß.
3. **Fuge im ersten Bildschirm:** 16 px zwischen Aufmacher-Schlagzeile und Bild am Handy.
4. **Kein Vorspann in schmaler Spalte:** Am Handy läuft der Vorspann über die volle Breite, das Bild steht unter Titel
   und Ort.
5. **Nach Tagen statt Rubrik-Reihe:** Die zweite Hälfte der Startseite ist „Zuletzt bei tamil.de“ (Juli bis Oktober,
   Monatsköpfe, Tageszeile mit Ziffer, Titel, Rubrik als Wort und Ort, Bild rechts). `rubrik.html` und „Weiterlesen“
   nutzen dieselbe Zeile. Keine „Kopfzeile + Alles aus …“-Blöcke mehr.

P2:
- Loch links bei 1280 gefüllt: Das Kino steht in der linken Spalte unter den Festen.
- Ziffernspalte nur für Tage: Kino nennt „In 11 Kinos: Berlin, …“ in der Zeile.
- Kino „Nach Stadt“: ein Platzhalter darüber statt sieben gleiche Zeilen.
- Verzeichnis: Suche und Liste zuerst, Art und Ort in „Filter: Art und Ort“ eingeklappt; Dienstleister (0) deaktiviert.
- Kopf nicht mehr wie Runde 2: Tagesdatum und drei Dienste, Rubriken ins Menü.
- Keine Projektsprache auf Leserseiten („KBS“ ersetzt durch „tamil.de“ oder „Preis folgt“), Platzhalter kürzer.

P3: Legende 18 px, Hilfetexte 16 px, einheitlich „Per WhatsApp schicken“, deutscher Hinweis unter dem Datumsfeld,
„Heute, kein Termin“.

## Überarbeitung nach r3

- **P1, Datum doppelt:** Auf der Startseite steht kein Datum mehr im Kopf; dort trägt allein das Tagesblatt den Tag.
- **Rot hat eine Bedeutung:** Eine Regel für alle Listen (Sonntag oder Festtag), in `bauen.py` über dieselbe Funktion
  `rot()` für Termine und Beiträge; die Legende sagt das so.
- **Strom weniger gleichförmig:** Bei 1280 füllt der Vorspann die Mitte jeder Zeile. Am Handy zeigt nur der erste
  Beitrag eines Monats ein Bild, ohne Vorspann; die Seite ist dadurch deutlich kürzer.
- **Loch unter dem Aufmacher:** Das Aufmacherbild steht ab 1100 px im Format 3:2 und endet auf Höhe der linken Spalte.
- **Kante im Artikel:** Kopf und Text nutzen dasselbe Raster (3/6/3); Titel und Fließtext beginnen an derselben Kante.
- **Kein Foto doppelt:** Der Generator vergleicht die Bilddateien je Seite; ein schon gezeigtes Foto (rb-30 und rb-49
  sind dieselbe Datei) wird in Listen weggelassen, die Zeile steht dann ohne Bild.
- **Symbolbilder gekennzeichnet:** „Symbolbild.“ oder „Archivbild.“ steht vor dem Nachweis, nach der Angabe der
  Bildredaktion im Alt-Text.
- **Hierarchie links:** Filmtitel in „Im Kino“ so groß wie die Festtitel (16 px).
- P3: Nachweise an Daumen 14 px, Billboard „zwischen den Monaten“, „Zurückliegend“ sagt „Termine, über die wir
  berichtet haben“. „Nach Stadt“ auf `kino.html` bleibt, weil der Linienauftrag „Kino nach Stadt“ verlangt.

## Inhalte

Alles echt: 20 Rückblick-Beiträge (Bilder mit Nachweis), Festkalender aus der Spalte „Ereignis“ von
`docs/redaktion/rueckblick-2026.md`, Kino aus `design/inhalte/inhalte.json` (Stand 9.11.). Kommende Termine nur mit
Beleg (15.11. Düsseldorf, 21.11. Basel, 13.12. Bern). Verzeichnis: zwölf Einrichtungen, die in den Beiträgen
vorkommen, mit Beschreibung aus dem Beitragstext; keine Kontaktdaten, keine PLZ. Sichtbare Platzhalter: Impressum,
Kontaktdaten der Redaktion und der Einträge, Preise und freie Termine, Einwilligungstext, Verkaufsbedingungen,
Kinos und Uhrzeiten. Beispielwerte (belegte Tage, Vorgangs- und Buchungsnummer, Premium) sind als solche markiert.

## Prüfung

Stand nach Kritik r3, Server `http://127.0.0.1:8941` (Haupt-Arbeitsbaum):

- `sloplint --genre editorial` über http für die elf Seiten der Liste: **0 FAIL**, 0 REFLEX offen. Gewaivt im Stempel:
  49b (lange echte Titel als Links), 59 und 78 (dichter Abstand und ruhige Köpfe, wie von der Kritik r1 verlangt),
  77 und 79 (kurze Dienstlisten und Seitenköpfe). 11 WARN „fallback font“ stammen aus dem `file://`-Durchgang
  (Schriften laden dort nicht); über http laden sie. Dazu 2 WARN F25 (Finish): Die Vorspanne im Strom der Startseite sind am Handy absichtlich ausgeblendet (Kritik r3, P2-2). Gate 58 ist mit `copy: verbatim` Notiz.
- `node tools/shots.mjs` bei 390/820/1280 für 14 Seiten (alle Seitentypen, Bestätigungen, Rubrik Seite 2):
  42 Aufnahmen, 0 Fehler, kein seitliches Scrollen, keine Konsolenfehler, keine leeren Bilder, keine kleinen
  Tippflächen.
- Fließtext 18 px (Artikel 19 px am Desktop), Legende 18 px, Hilfetexte 16 px; Kontrast Tinte auf Papier > 14:1,
  Rot auf Papier 6,0:1.

## Eigene Schwächen

- Zwei sehr ähnliche Groteskschriften (Rethink Sans, Golos) unterscheiden sich kaum; eine Familie würde reichen.
- Die Tageszeile ist die einzige eigene Idee; Rubrik, Verzeichnis und Formulare sind ordentlich, aber vertraut.
- Am Handy beginnt die zweite Geschichte erst am unteren Rand des ersten Bildschirms.
- Die Startseite zeigt nach dem Aufmacher nur noch eine lange Liste nach Tagen; Nachrichten heben sich darin nicht ab.
- Formulare, Werben und Verzeichnis-Profil tragen die Idee weiterhin nicht.
- „Eintrag vorschlagen“ und „Änderung melden“ führen zum allgemeinen Kontaktformular, nicht zu einem eigenen.
- Verzeichnis-Filter und Buchungskalender sind statisch (kein Skript); sie zeigen Zustände, filtern aber nicht.
- Die Kino-Liste nach Stadt bleibt dünn, solange Kinos und Uhrzeiten fehlen.
- Das Karthi-Foto im Kinojahr hat einen roten Hintergrund und ist damit die größte rote Fläche der Linie.

## Neu bauen

`python3 design/richtungen/hm-eigen/bauen.py` (vom Repo-Root).
