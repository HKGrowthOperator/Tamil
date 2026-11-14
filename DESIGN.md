# Design – Tamil.de: „Tageskalender“

> **Stand 14.11.2026:** Richtung gewählt von Luis („eine Mischung aus A und B“, `docs/abnahme/2026-11-14-design-luis.md`).
> Tor G3 steht noch aus; diese Datei gilt bis dahin nur auf dem Theme-Branch. Quelle ist die Probe
> `design/richtungen/hm-tageskalender/` (Runde 3), Tokens in `design/tokens.css`, Kritik in
> `design/kritik/hm-tageskalender-r*.md`. Maßstab: `design/brief-v3.md` mit Hallmark.

**Idee:** tamil.de beginnt jeden Tag wie eine Zeitung mit seinem Datum und dem Aufmacher im Foto (Linie A) und ordnet
darunter, was kommt, als gedrucktes Kalenderblatt in Tabellen (Linie B). Rot zeigt nur, was als Nächstes kommt.

## Farben

Hex in `theme.json` (Palette), oklch in `design/tokens.css`, im Theme als `--color-*` aus `--wp--preset--color--*`.

| Token (theme.json) | Hex | Rolle |
|---|---|---|
| `papier` | `#F1F5F9` | Seitengrund (kühles Papier aus B) |
| `papier-2` | `#E5EAEF` | Fuß, Leiste über dem Kopf, Mulden, Hover |
| `papier-3` | `#D8DFE5` | Bildgrund beim Laden |
| `blatt` | `#FBFDFF` | helles Tabellenblatt mit fester Linie oben |
| `tinte` | `#0C151C` | Text, Köpfe, 2-px-Linie über Listen (über 14:1 auf Papier) |
| `tinte-2` | `#222A31` | Vorspann, Nebentext |
| `grau` | `#4B545B` | Stand, Nachweise, Tabellenköpfe, Wochentag |
| `linie` | `#C5CBD0` | Zeilenlinien |
| `linie-fest` | `#2B343B` | feste Kante des Blatts, Linien um „als Nächstes“ |
| `rot` | `#B5282A` | Logo-Rot. **Nur** Tagesziffer und Titel des nächsten Termins und das Wort „als Nächstes“ (6:1 auf Papier) |

Keine Flächen in Rot, keine Verläufe, keine Schatten, keine dunklen Bänder. Sonntage und Festtage sind nicht rot.

## Schrift

| Rolle | Schrift | Schnitt | Größe |
|---|---|---|---|
| Köpfe, Tabellentitel | **Rethink Sans** | 600 | Schlagzeile `clamp(1.875rem, 1.6vw + 1.2rem, 2.75rem)` (rund 40 px bei 1280), Abschnitt 22–28 px, Listentitel 20–26 px |
| Ziffern (Tag) | Rethink Sans | 800 | Tagesziffer `clamp(3rem, 4.5vw + 1rem, 5.5rem)`, je Zeile 34–40 px, in Tabellen 30 px |
| Lesetext, Tabellenzellen | **Golos Text** | 400, 600 | 18 px überall (auch am Handy), Artikeltext 19 px, Vorspann 18–22 px, Stand/Nachweise 14 px |
| Tamil im Inhalt | Catamaran (nur Tamil-Untermenge) | – | greift nur für `lang="ta"` und Tamil-Zeichen |

OFL, selbst gehostet in `wordpress/themes/tamil/assets/fonts/` (Lizenzen daneben). Keine Versalien, keine Sperrung,
keine Kursive, keine „·“-Metazeilen, keine Dachzeilen über Titeln.

## Bausteine

- **Leiste über dem Kopf** (ab 761 px): schmal, `papier-2`, Unterzeile der Marke links, Termin einreichen und Werben
  rechts. Am Handy ausgeblendet; die Ziele stehen im Menü.
- **Kopf:** Logo, vier Ziele (Termine, Kino, Community, Verzeichnis) in Golos 600 mit Unterstrich für die aktuelle
  Seite, Menü „Mehr +“ als Aufklapper (übrige Rubriken, Dienste, Suche). Bis 760 px eine Zeile: Logo, Termine, Kino,
  Mehr; bis 520 px stehen Community und Verzeichnis nur im Menü.
- **Datumsblock:** große Tagesziffer (800), daneben Monat und Jahr (600) und Wochentag (grau); im Artikel und im
  Rubrik-Aufmacher zusätzlich Rubrik und Ort.
- **Bogen (Tabellenblatt):** `blatt` mit 2-px-Kante `linie-fest` oben, Kopf mit Titel links und „Stand: …“ rechts,
  Fuß mit Textlink über einer zweiten festen Linie.
- **Tafel (Tabelle):** Tag (Ziffer 30 px + „So., Nov.“), Was, Wer, Wo, Weitersagen. Der nächste Termin steht zwischen
  zwei festen Linien, Ziffer und Titel rot, darunter „als Nächstes“. Vergangene Zeilen grau. Am Handy zweispaltig:
  Ziffer links (4,25 rem), alles andere rechts auf einer Kante.
- **Strom:** Beiträge nach Monaten, je Zeile Tagesziffer, Titel, „Rubrik, Ort“, Vorspann (nur breit) und Bild mit
  Nachweis rechts; am Handy Bild als kleines Quadrat rechts.
- **Bilder:** immer mit Nachweis (Urheber, Lizenz, Quelle) unter dem Bild, Radius 2 px.
- **Knöpfe:** eckig (2 px), Tinte auf Papier; sonst Textlinks mit 44 px Tippfläche.
- **Anzeigen:** Label „Anzeige“, ruhige Fläche `papier-2`, dem Inhalt untergeordnet (Plätze aus dem Plugin).
- **Fuß:** Fläche `papier-2` mit Logo, Rubriken, Diensten, Rechtlichem und den Bildnachweisen der Seite.

## Seiten

- **Startseite:** links Datum, Aufmacher-Schlagzeile, Vorspann, WhatsApp, darunter „Die nächsten Feste“ (Bogen);
  rechts Foto 4:3 mit Nachweis und „Im Kino“. Am Handy: Datum, Feste, Schlagzeile, Foto, Vorspann, Kino. Danach
  „Zuletzt bei tamil.de“ als Strom nach Monaten.
- **Artikel:** Kopf 3/6/3 (Datumsblock links, Titel, Vorspann, WhatsApp), Foto 16:9 über die volle Breite,
  Text in der Mitte (max. 66 Zeichen), rechts Anzeige; Termin als Bogen; „Weiterlesen“ als Strom.
- **Rubrik:** Seitenkopf, neuester Beitrag als Aufmacher (Foto links, Datum und Titel rechts), dann Strom nach
  Monaten, Seitennavigation.
- **Termine / Kino:** Seitenkopf mit Foto rechts, die Tafel links direkt unter der Einleitung (Kante bei 7 von 12
  Spalten), darunter Monate bzw. Städte als Tafeln.

## Raster und Abstände

- Inhalt max. 1320 px, Rand `clamp(16px, 4vw, 56px)`, Spaltenabstand 32 px (16 px am Handy).
- Abschnitte 64 px (48 px unter 860 px), getrennt durch 1-px-Linien oder die Mulde `papier-2`.
- Brüche: 1100 (Datum im Kopf), 1040, 960 (Artikel einspaltig), 860 (Startseite und Seitenköpfe einspaltig),
  760 (Kopf eine Zeile, Strom Handy), 640 (Tafeln zweispaltig, Blatt randlos), 520, 400.

## Bewegung

Nur auf Zeigen: Unterstrich wird dicker, Bild leicht heller, Knopf 1 px tiefer. `prefers-reduced-motion` schaltet
alles ab. Keine Laufbänder, keine automatischen Animationen.

## Cockpit (Produkt-Register)

Gleiche Tokens und Schriften, ruhiger: Listen und Tabellen auf `blatt`, Linien statt Kästen, ein dunkler Hauptknopf
je Ansicht, Rot nur für Fehler und Fristen.
