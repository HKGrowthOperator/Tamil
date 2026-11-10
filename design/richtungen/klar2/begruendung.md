# klar2 – Begründung (Skizze, Brief 2.1 Abschnitt 10)

`klar` mit mehr Bild und mehr Bühne, keine neue Richtung. Schrift (Libre Franklin, normale Breite, eine Familie),
die sechs Farbwerte, das Dachzeilenformat „Rubrik | Datum“, Linien statt Kästen, Fokusrahmen und der Block
`prefers-reduced-motion` sind unverändert übernommen.

1. **Vorbild:** BBC News für Kopf und Ordnung (Logo auf hell, dunkles Rubrikband ~48 px, Aufmacher mit
   Anreißerspalte daneben, Meldungen mit kleinem Bild rechts); tagesschau für den Titel im Bild auf dunklem Verlauf;
   Spiegel für die Bildblöcke (große Kachel plus kleinere daneben).
2. **Gegenüber `klar` verstärkt, je mit Grenze (gemessen mit `aufnahmen.mjs`):**
   - Kopf in drei Teilen: Kopfzeile (Datum, „Diese Woche“-Hinweise ab 600 px, Suche mit Lupe), Logo 44/58 px hoch,
     dunkles Rubrikband als eigenes `<nav>`, das stehen bleibt. Kopf am Handy 147 px (Grenze 152); fest steht nur
     das Band, 46/48 px (Grenze 56).
   - Aufmacher: Foto 4:3, am Handy randlos, am Desktop 780 px breit; Dachzeile und Titel im Bild auf dem einzigen
     Verlauf (durchsichtig nach Tinte). Titel 30/40 px (Grenze 34/44), höchstens drei Zeilen.
   - Rubrikkacheln: sieben Bildkacheln 16:9 als Navigation ohne `h2`/`h3`, am Handy ein Streifen im eigenen
     Behälter, rechts angeschnitten; am Desktop eine Reihe unter Aufmacher und Meldungen.
   - Überall ein Bild: Nebenstücke (am Desktop vier nebeneinander, Bild über dem Titel), Meldungen mit Bild 96/120 px.
     `anreisser_ohne_bild` leer, `anreisser_mit_grafik` genau 3 (die Radar-Einträge).
   - „Diese Woche“ dunkel über die volle Breite: Kanguva groß (4:3), Rathamaarey klein (16:9, die eingebrannte
     Bildzeile liegt außerhalb des Rahmens), „Im Kino“ und „Termine“ als Kacheln in „Fläche auf Dunkel“ mit
     `data-grafik`; Zahl der Kinos und Termindatum 18 px, nach dem Titel die größte Angabe.
   - „Küche“ hell: Kottu Roti groß (4:3, zwei Drittel), drei kleinere Kacheln gestapelt daneben.
   - Bewegung: nur Bildzoom 1,03 beim Überfahren, 0,35 s, mit „Bewegung reduzieren“ 0 Übergänge.
3. **Bildformate:** 16:9 (Anreißer, Rubrikkacheln, kleine Kino-Kachel), 4:3 (Aufmacher, große Kacheln), rund 2:1
   (kleine Küchenkacheln). Kein Bild über der Dateibreite; über der halben Breite nur Aufmacher und Kottu Roti.
4. **Abgrenzung Runde 2** (alt, Baukasten): kühler heller Grund statt Creme, Grotesk statt Serifen-Fließtext, keine
   Kartenraster mit Rahmen; Messwert: Radius 0 px, Schatten 0.
5. **Abgrenzung Runde 4** (laut): größte Schrift 30/40 px statt 98–335 px, zweitgrößte 22/26 px (Grenze 24/28), Rot 0,1 % der
   Fläche (Runde 4: 6–54 %), keine rote Schrift über 13 px, dunkel im ersten Bildschirm 6,4/5,8 % (Grenze 12),
   genau zwei dunkle Flächen, keine Versalien, nichts gedreht, keine Animation.

## Überarbeitung (Prüfung r1)

- **P1 Bildformate:** Die Rasterzeile bestimmt keine Bildhöhe mehr. Jede Kachel hat ein festes Format aus 4:3, 16:9
  und 8:3. 8:3 gilt für Rathamaarey und die kleinen Küche-Kacheln: Bei 8:3 schneidet das Bild unten 12 % ab, so
  bleibt die eingebrannte Bildzeile unsichtbar, und alle vier Männer sind zu sehen.
  - Gemessen sind es je Breite genau drei Formate (390, 820 und 1280: 1,33 / 1,78 / 2,67).
  - Die Küche am Desktop hat Spalten im Verhältnis 803 : 373. Kottu Roti steht in 16:9 (803 × 452), die drei
    kleinen Kacheln in 8:3 (373 × 140), beide Seiten enden auf derselben Linie.
  - In „Diese Woche“ gleichen die Kino-Kacheln ohne Foto die Höhe aus.
- **Rathamaarey:** Titel unter dem Bild statt im Bild, damit die Gesichter frei bleiben.
- **Sprungziele:** `scroll-padding-top: 56px`.
- **Fokus:** Bei Aufmacher, Bildkacheln und Rubrikkacheln wird der Rahmen nach innen gezeichnet: dunkler Rand mit
  heller Linie. Der Streifen hat 5 px Innenabstand oben und unten und `scroll-padding-inline`.
- **Bei 600–1023 px:**
  - Aufmachertitel 34 px.
  - Meldungen zweispaltig.
  - „Termine“ über die volle Breite.
- **Desktop:** Die Reihe der Rubrikkacheln ist zwischen zwei feinen Linien mit 40 px Abstand vom Block der
  Nebenstücke abgesetzt.
- **Offen:** P2 Nr. 7 (Rangfolge Nebenstücke und Meldungen am Desktop).
