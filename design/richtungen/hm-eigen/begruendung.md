# Linie A „Tagesblatt“ (hm-eigen) – Begründung

Stand 13.11.2026, Runde 2 (nach `design/kritik/hm-eigen-r1.md`). Gestaltet nach `design/brief-v3.md` mit Hallmark
(eigene Richtung). Alle Seiten erzeugt der Generator `bauen.py` aus echtem Material; von Hand geschrieben ist nur
`hm-eigen.css`.

## Idee

tamil.de ordnet sich wie der Kalender in der tamilischen Küche: jeder Beitrag an seinem Tag, das Datum vorn. Das
Erkennungszeichen ist die **Tageszeile** (Ziffer, Titel, Ort, Linie statt Kasten). Rot bedeutet nur „Sonntag oder
Festtag“, klein, nie als Fläche und nie als Riesenschrift.

## Hallmark-Picks

| Achse | Wahl |
|---|---|
| Shape | Tagesblatt (eigene Form): Datum und die nächsten Feste links, Aufmacher mit Bild rechts; darunter Kino, Tempel und Vereine, Nachrichten, Küche, Kultur und Sport |
| Papier | Jasminweiß `oklch(97.6% 0.007 120)`, Tinte `oklch(21% 0.022 155)`, Mulde `paper-2` für Nachrichten und Fuß |
| Rot | Logo-Rot `oklch(50.5% 0.175 25)`: Ziffer in Tageszeilen von Terminen an Sonntagen und Festtagen, Wochentag „Sonntag“/Festname im Datumsblock, Sonntage im Buchungskalender, Fokusring. Kein roter Knopf mehr |
| Schrift | Rethink Sans 600 für Köpfe, 800 nur für Ziffern; Golos Text für Lesetext (beide OFL, selbst gehostet, Lizenzen in `schriften/`). Drei Gewichte: 400, 600, 800 |
| Signatur | die Tageszeile; dieselbe Grammatik trägt Kino (Zahl der Kinos links), Verzeichnis (Stadt links) und den Buchungskalender |
| Haltung | geteilt (split), Linien statt Kästen, keine Karten, keine Vollfarbflächen |
| Bilder | Fotos aus Commons mit Nachweis am Bild; Daumenbilder in Listen mit Nachweis gesammelt im Fuß |
| Sweep | sloplint über http: 0 FAIL, 0 REFLEX offen (5 gewaivt: 49b, 59, 77, 78, 79); shots.mjs 42 Aufnahmen, 0 Fehler, 0 Hinweise |

## Seiten

| Datei | Inhalt |
|---|---|
| `index.html` | Startseite |
| `rubrik.html`, `rubrik-2.html` | Community mit Seitennavigation (5 je Seite); dazu `rubrik-nachrichten/-kultur/-kueche/-sport.html`, damit kein Rubrik-Link ins Leere führt |
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

## Inhalte

Alles echt: 20 Rückblick-Beiträge (Bilder mit Nachweis), Festkalender aus der Spalte „Ereignis“ von
`docs/redaktion/rueckblick-2026.md`, Kino aus `design/inhalte/inhalte.json` (Stand 9.11.). Kommende Termine nur mit
Beleg (15.11. Düsseldorf, 21.11. Basel, 13.12. Bern). Verzeichnis: zwölf Einrichtungen, die in den Beiträgen
vorkommen, mit Beschreibung aus dem Beitragstext; keine Kontaktdaten, keine PLZ. Sichtbare Platzhalter: Impressum,
Kontaktdaten der Redaktion und der Einträge, Preise und freie Termine, Einwilligungstext, Verkaufsbedingungen,
Kinos und Uhrzeiten. Beispielwerte (belegte Tage, Vorgangs- und Buchungsnummer, Premium) sind als solche markiert.

## Prüfung

- `sloplint --genre editorial` über `http://127.0.0.1:8941` für die elf Seiten der Liste: **0 FAIL**, 0 REFLEX offen.
  Gewaivt im Stempel: 49b (lange echte Titel als Links), 59 und 78 (dichter Abstand und ruhige Köpfe, wie von der
  Kritik verlangt), 77 und 79 (kurze Dienstlisten und Seitenköpfe). 11 WARN „fallback font“ stammen aus dem
  `file://`-Durchgang (Schriften laden dort nicht); über http laden sie. Gate 58 ist mit `copy: verbatim` Notiz.
- `node tools/shots.mjs` bei 390/820/1280 für 14 Seiten (alle Seitentypen plus Bestätigungen und Rubrik Seite 2):
  42 Aufnahmen, 0 Fehler, kein seitliches Scrollen, keine Konsolenfehler, keine leeren Bilder, keine kleinen
  Tippflächen.
- Fließtext 18 px (Artikel 19 px am Desktop), Kontrast Tinte auf Papier > 14:1, Rot auf Papier 6,0:1.

## Eigene Schwächen

- Zwei sehr ähnliche Groteskschriften (Rethink Sans, Golos) unterscheiden sich kaum; eine Familie würde reichen.
- Die Tageszeile ist die einzige eigene Idee; Rubrik, Verzeichnis und Formulare sind ordentlich, aber vertraut.
- Am Handy beginnt die zweite Geschichte erst am unteren Rand des ersten Bildschirms.
- „Eintrag vorschlagen“ und „Änderung melden“ führen zum allgemeinen Kontaktformular, nicht zu einem eigenen.
- Verzeichnis-Filter und Buchungskalender sind statisch (kein Skript); sie zeigen Zustände, filtern aber nicht.
- Die Kino-Liste nach Stadt bleibt dünn, solange Kinos und Uhrzeiten fehlen.
- Das Karthi-Foto im Kinojahr hat einen roten Hintergrund und ist damit die größte rote Fläche der Linie.

## Neu bauen

`python3 design/richtungen/hm-eigen/bauen.py` (vom Repo-Root).
