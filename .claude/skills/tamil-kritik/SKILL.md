---
name: tamil-kritik
description: Prüfbogen für die unabhängige Prüfung einer Gestaltungsprobe für tamil.de – harte Kriterien aus dem Brief messen, Paarvergleich gegen echte Nachrichtenmarken und gegen die abgelehnten Runden, Verbotsliste, Lesbarkeit, Technik. Vorgeladen im design-kritiker.
user-invocable: false
---

# Unabhängige Prüfung

Du prüfst eine Probe, die jemand anderes gebaut hat. Du bekommst nur die Seiten und `design/brief.md`, nicht die
Begründung des Gestalters und keine früheren Kritiken. Lies `begruendung.md` nicht.

Du lieferst **Messwerte und Befunde, kein Gesamturteil.** Ob eine Probe gezeigt wird, entscheidet die Hauptsitzung
anhand deiner Befunde.

Ziel der Gestaltung ist die Ruhe, Ordnung und Wertigkeit einer großen Nachrichtenmarke. Eine Nachrichtenseite soll
wie eine aussehen; Vertrautheit ist kein Mangel. Mangel ist, was laut, verspielt, billig oder alt wirkt.

## Vorgehen

1. **Messen.** `node design/vergleich/aufnahmen.mjs <slug>` nimmt den sichtbaren ersten Bildschirm auf (Handy
   390 × 844, zweiter Handy-Bildschirm, Desktop 1280 × 800, nach `design/vergleich/img/`) und schreibt die Kennzahlen
   nach `design/vergleich/kennzahlen/<slug>.json`. Für die ganze Seite und die Technik:
   `node tools/shots.mjs design/richtungen/<slug>/index.html --out <dein Scratch-Ordner> --kacheln`.
2. **Ansehen.** Jeden ersten Bildschirm wie ein Leser: fünf Sekunden, dann genau.
3. **Paarvergleich.** Lege den ersten Bildschirm der Probe bei gleicher Breite neben
   - zwei Vorbilder aus `design/referenzen/news-marken.md` (Bilder `design/referenzen/img/news-*-handy-1.jpg` und
     `-desktop-1.jpg`),
   - Runde 2 (`.claude/skills/tamil-marke/references/abgelehnt/r2-community-magazin-390.jpg` und `-1280.jpg`),
   - eine Skizze aus Runde 4 (`…/abgelehnt/r4-raster-390.jpg` und `-1280.jpg`).

   Bei `klar2` liegt als erstes Paar `klar` daneben (`design/vergleich/img/klar-start-*.jpg`); die Bilder des
   Bereichs „Diese Woche“ und der „Küche“ (`design/vergleich/img/klar2-woche-*.jpg`, `-kueche-desktop.jpg`) siehst
   du dir ebenfalls an, denn dort liegen die neuen Mittel.

   Frage je Paar: Welche Seite wirkt wertiger, und woran genau sieht man es (Abstände, Linien, Hierarchie, Satz,
   Bildausschnitt, Farbe)? Benenne beobachtbare Unterschiede, keine Adjektive.
4. **Bogen ausfüllen**, Ergebnis nach `design/kritik/<slug>-r<n>.md`.

## Bogen

**A. Harte Kriterien:** für `klar`, `blatt` und `bild` der Brief, Abschnitt 7 (zwölf Kriterien); für `klar2` der
Brief, Abschnitt 10.4 (sechzehn Kriterien, mit den Kennzahlen in Klammern). Der Auftrag nennt dir die Fassung. Jedes
Kriterium einzeln mit Messwert für Handy und Desktop und „erfüllt“ oder „verletzt“. Jede Verletzung ist **P1**. Passt eine Kennzahl nicht zum Bild, miss von Hand nach und
kennzeichne den Wert so. Die Höhe des Kopfs ist `kopfleiste_hoehe`, nicht `erste_schlagzeile_ab`.

Führe **jede Ursache nur einmal** als Befund, im strengsten passenden Abschnitt. Wer dieselbe rote Riesenschrift in
A, B und C zählt, macht die Zahl der Befunde wertlos.

**B. Wertigkeit im Paarvergleich:** je Paar zwei bis drei beobachtbare Unterschiede. Dazu die vier Punkte, an denen
Runde 4 gescheitert ist, und ihr Gegenteil:

| Punkt | Woran es sich zeigt | Stufe |
|---|---|---|
| zu viel Rot, zu laut | Rotanteil, größte Schrift, Versalien und Effekte laut Kennzahlen; dazu der Eindruck im Bild | P1 |
| Baukasten | Kästen (Fläche oder Rahmen um einzelne Anreißer), Pillen, dekorative Icons, gleichförmige Kartenraster, Knöpfe „Weiterlesen“, weiche Schatten, große Rundungen; Linien zwischen Anreißern sind kein Kasten | P1 |
| Schrift | verzerrte, extraschmale oder extrabreite Schnitte; unruhiger Satz (Zeilenfall, Löcher, zu enge oder zu weite Zeilen); mehr als zwei Familien | P1 |
| nicht hochwertig | ungleiche Abstände, verrutschte Kanten, uneinheitliche Bildformate, schlecht gewählte Bildausschnitte, Dachzeilen und Daten in wechselnder Form | P1 im ersten Bildschirm, sonst P2 |
| alt oder langweilig | wie Runde 2: Creme oder Sand als Grund, braungraue Tinte, runde Bilder, bunte Rubrikpunkte oder ein Mosaik, jeweils für sich; eine Serife im Fließtext nur zusammen mit warmem Grund | P1 |

**C. Verbotsliste:** jede Übereinstimmung mit `tamil-marke` ist P1. Ausdrücklich erlaubt sind eine Serife in den
Schlagzeilen auf kühlem Weiß (Variante `blatt`), ein vertrauter Nachrichtenaufbau und Meldungslisten. Für `klar2`
zusätzlich erlaubt, jeweils nur in den Grenzen von Brief 10.1: zwei dunkle Flächen in Tinte, heller Titel im Bild
auf einem Verlauf nach Tinte, Zoom beim Überfahren, ein stehendes Rubrikband, die größere Schlagzeile des
Aufmachers. Was über diese Grenzen hinausgeht, ist P1 wie bisher.

**D. Leser:** Kann ein 65-Jähriger es am Handy lesen (Schriftgrößen, Kontrast, Tippflächen, klare Wege)? Findet eine
19-Jährige in fünf Sekunden, was wichtig ist? Stimmen die Inhalte mit der Inhaltsliste überein
(`design/inhalte/inhalte.json`, für `klar2` `inhalte-klar2.json`): nichts erfunden, nichts weggelassen, Reihenfolge
eingehalten? Schrift im Bild: an jeder Stelle lesbar, auch über hellen Bildteilen? Ist beim Zoomen auf 200 % und mit
der Tastatur alles erreichbar, auch der seitlich laufende Streifen?

**E. Technik** aus `bericht.json` von `shots.mjs`: Fehler = P0; Tippflächen unter 44 px = P2.

**F. Bedienbarkeit, nur zur Information:** Nielsen 1–10, je 0–4, mit einem Satz. Die Summe ist kein Tor und steht
nicht in der Kopfzeile.

## Ausgabe `design/kritik/<slug>-r<n>.md`

```markdown
# Prüfung <slug>, Runde <n>
Harte Kriterien: <x> von <12 oder 16> erfüllt · P0: <n> · P1: <n> · P2: <n>
## Erster Eindruck (3 Sätze)
## Harte Kriterien (Tabelle: Kriterium, Messwert Handy, Messwert Desktop, erfüllt oder verletzt)
## Paarvergleich (je Paar die beobachtbaren Unterschiede)
## Befunde (P0 bis P3, je mit Ort: Breite und Element, und Behebungsvorschlag)
## Was trägt (höchstens 3 Punkte)
## Bedienbarkeit (Tabelle, nur zur Information)
```

Sei genau und streng. Vier Entwürfe wurden abgelehnt: zwei als alt oder generisch, zwei als laut oder Baukasten. Gib
kein Gesamturteil und keine Empfehlung ab, ob gezeigt wird.
