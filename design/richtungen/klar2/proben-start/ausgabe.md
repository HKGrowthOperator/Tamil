# Vierte Probe „Ausgabe“ (`/?probe=ausgabe`)

Stand 22.11.2026. Grundlage: Empfehlung der unabhängigen Kritik vom 22.11. zu den drei Proben aus Theme 3.16.1
(Cover als Gerüst, Stadtbereich als kompakter Streifen direkt darunter, ein wirklich großer Titel, sichtbare tamilische
Schrift, Kommendes vor Vergangenem, weniger Gleichförmigkeit). Auftrag von Luis, Block 1. Keine Entscheidung: Luis wählt.
Die normale Startseite und die drei Proben bleiben, wie sie sind.

## Aufbau 390 (Kopf 160 px, Umschalter 44 px, Bildschirm 844)

```
204  COVER randlos, mindestens 407 px, sonst Bildschirmhöhe minus 280 px, höchstens 4:5 (487 px)
     Dachzeile, Titel 32 px (ab 61 Zeichen 29 px, ab 91 Zeichen 26 px), Punktbogen unten rechts
691  Rubrik der Titelgeschichte auf Tamil und Deutsch, Ort, Termin, Quelle (14 px), Vorspann 18 px in ganzen Sätzen
     STREIFEN auf Titan, randlos: „Tamil in meiner Stadt“, Stadtwahl 48 px,
       eine wischbare Reihe (Karte 72 % breit): erst Kino ab heute, dann Termine ab heute; Balken und Pfeile darunter
     GROSSES BEISTÜCK 4:3, Titel 24 px, Vorspann in ganzen Sätzen; zwei kleinere 16:9 untereinander, Titel 19 px
     „Weitere Meldungen“: eine große Karte 4:3, drei kleine als wischbare Reihe
     Rubrikkacheln, zweisprachig. Danach Werbeplatz 01 wie heute.
```

## Aufbau 1440 (Inhalt 1200 px)

```
     COVER 1200 breit, Höhe = Bildschirmhöhe minus 250 px, mindestens 480, höchstens 640 px; Titel 60 / 52 / 44 px
     darunter drei Spalten: Rubrik auf Tamil | „Titelgeschichte“ mit Ort, Termin, Quelle, Erschienen | Vorspann 20 px
     STREIFEN auf Titan über die volle Breite: links Titel, Stadtwahl und Links (250 px), rechts drei Karten je Blick
       (Bild 3:2, alle Karten gleich hoch), unten rechts das Signet auf der Fläche wie in „Diese Woche“
     BEISTÜCKE: groß 2/3 (16:9, Titel 30 px, Vorspann) | zwei kleinere 1/3 gestapelt, so hoch wie das große
     WEITERE MELDUNGEN gespiegelt: drei flache Karten 1/3 gestapelt | eine große 2/3 (4:3, Titel 28 px)
     Rubrikkacheln in einer Zeile, zweisprachig
```

## Auswahl

- Vorrat wie Cover First: `tamil_probe_cover_auswahl()` (Titelgeschichte aus `lead`; trägt sie nur ein Symbolbild aus
  dem Pool, rückt ein Beitrag mit eigenem Foto aufs Cover). Beistück 1 groß, Beistücke 2 und 3 klein. Aus den vier
  übrigen wird der erste mit eigenem Foto die große Karte, die anderen drei stehen flach daneben. Kein Beitrag doppelt.
- Streifen: `tamil_stadt_daten()`. Nur Kommendes: Filme mit Vorstellung ab heute (höchstens 3 sichtbar), Termine ab
  heute (höchstens 6). Keine Geschichten, sie sind Rückblick. Wählbar sind nur Städte mit Vorstellung oder Termin.
  Hat die Stadt in einem Fach nichts, steht dort der Bestand aus allen Städten mit einer Zeile darüber; gibt es
  nirgends etwas, ein leiser Satz mit Link.
- „Diese Woche“ entfällt in dieser Probe, der Streifen ersetzt es. Es gibt damit nur eine Kinozählung: Kinos mit
  Vorstellung ab heute, bei Abweichung von der Kinoliste „ab heute noch N von M Kinos“.
- Werbeplätze nach F3 unverändert: Leaderboard nach den Rubrikkacheln, Billboard nach „Küche“, Fuß.

## Typografie

| Stelle | 390 | 820 | 1440 |
|---|---|---|---|
| Covertitel (bis 60 / bis 90 / über 90 Zeichen) | 32 / 29 / 26 px | 43 / 38 / 32 px | 60 / 52 / 44 px |
| Vorspann der Titelgeschichte | 18 px | 19 px | 20 px |
| Großes Beistück, große Karte | 24 px | 26 px | 30 und 28 px |
| Kleine Karten | 19 px | 18 px | 19 px, flache 18 px |
| Karten im Streifen | 18 px | 18 px | 19 px |
| Tamilischer Rubrikname am Cover | 24 px | 28 px | 34 px |

Ein Titel mit einem Wort ab 16 Zeichen steht am Handy eine Stufe kleiner, damit kein Wort bricht.

## Tamilische Schrift

Echter Bestand: die acht tamilischen Rubriknamen in `inc/rubriken.php` (überschreibbar je Kategorie über das Feld
„tamil“). Sie stehen an zwei Stellen, jeweils als Name der Rubrik und mit `lang="ta"` in Catamaran: einmal groß in
Titan neben dem Kontextfeld der Titelgeschichte, und in jeder Rubrikkachel über dem deutschen Namen. Nicht vor
Überschriften, nicht in Karten. Tamilische Titel oder Vorspänne gibt es im Bestand nicht; übersetzt wird nichts.

## Wiederverwendet

`tamil_anr_imbild()`, `tamil_kontext()`, `tamil_grafik_kino()`, `tamil_grafik_termin()`, `tamil_kacheln()` (neuer
Schalter für den tamilischen Namen), `tamil_stadt_daten()`, `stadt-start.js` und `stadt.js` über dieselben
data-Attribute. Neu: `template-parts/home/probe-ausgabe.php`, `stadt-streifen.php`, `assets/js/streifen.js` (Pfeile
und Balken der Reihe), ein CSS-Block am Ende des Proben-Abschnitts.

## Bewegung

Nur als Antwort: der Balken folgt dem Wischen, die Reihe gleitet beim Tippen auf einen Pfeil, der Inhalt blendet beim
Stadtwechsel kurz um (160 ms). Alles nur unter `prefers-reduced-motion: no-preference`. Der Wow-Aufmacher bleibt aus.

## Gemessen (lokal, 22.11.2026, Titel der Titelgeschichte 82 Zeichen, also Stufe „mittel“)

| Breite × Höhe | Titelbild | Covertitel | Titel endet bei | sichtbar bis |
|---|---|---|---|---|
| 390 × 844 | 390 × 488 px | 28,8 px, 4 Zeilen | 644 px | 769 px (fester Werbebalken) |
| 820 × 1180 | 772 × 483 px | 39,1 px, 3 Zeilen | 685 px | 1180 px |
| 1280 × 800 | 1200 × 550 px | 48,5 px, 3 Zeilen | 764 px | 800 px |
| 1440 × 900 | 1200 × 640 px | 52,2 px, 3 Zeilen | 854 px | 900 px |

Ein Titel bis 60 Zeichen stünde in 32 px (390) und 60 px (1440). Kein seitliches Scrollen bei 390, 820, 1280, 1440.
