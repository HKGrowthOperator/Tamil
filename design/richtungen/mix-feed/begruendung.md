# mix-feed – Begründung (Probeseite, 12.11.2026)

1. **Auftrag:** Mischung aus der Ordnung von `klar2` und der Bildwucht von Gen-Z/`feed` (Luis, 11./12.11.). Jeder Anreißer hat ein Foto mit Nachweis; Wucht kommt aus Bildfläche und Kachelgrößen, nicht aus Rot oder Schrift.
2. **Vorbild:** Spiegel (bildstark: großes Aufmacherbild, Schlagzeile im Bild, Gewicht 650–700) und BBC (eine Metazeile „Rubrik | Datum“, Linien statt Kästen, Radius 0). Vom App-Feed nur das Verhalten: hohe Bildkarten, Wischstreifen per `scroll-snap`.
3. **Schrift:** Libre Franklin wie `klar2`, normale Breite, eine Familie. Aufmacher 30 px Handy / 40 px Desktop; Bildkarten 22/24 px, kleine Kacheln 18/19 px; Meldungen 18/17 px; Artikel-Fließtext 19/20 px, Spalte ≤ 68 Zeichen.
4. **Farbe:** feste Werte aus Brief 3 und 10.1. Rot nur Dachzeile, aktive Rubrik, Linie über den Radar-Plakaten. Dunkel nur Rubrikband und „Diese Woche“. Verlauf nur unter Schrift im Bild.
5. **Handy:** Aufmacher randlos, füllt den ersten Bildschirm bis auf rund 160 px; darunter schaut die erste Meldung mit Bild hervor. Danach hohe Bildkarte, „Diese Woche“ mit Kino-Plakatstreifen (2:3) und Terminen, Community als große Karte plus Wischstreifen, Küche als Wischstreifen.
6. **Desktop:** dichtes Raster mit ungleichen Kacheln: Aufmacher 8/12 + Bildkarte und drei Meldungen; fünf Plakate in einer Reihe; Community hoch + 2 × 2; Küche als Reihe mit breiter erster Kachel; zum Schluss hohe Karte + drei Nebenstücke.
7. **Erkennungszeichen aus dem Inhalt:** Kino mit Zahl der Kinos und Städten, Termine mit großem Tag; vergangene Termine nach Monaten.
8. **Inhalte:** 20 Rückblick-Beiträge 2026 (Commons, Nachweis unter jedem Bild und in jedem Artikel), Kino/Küche/Archiv aus `inhalte-klar2.json` mit „Bild: Archiv tamil.de“. Zwei Rückblick-Paare teilen dasselbe Foto (30/49, 37/62); sie stehen nie im selben Block. Jeder Rückblick-Beitrag hat eine eigene Artikelseite (`artikel-<id>.html`).
9. **Abgrenzung Runde 2:** kein Creme, keine Serife, Radius 0 statt runder Bilder. **Runde 4:** größte Schrift 40 px statt 98–335 px, keine Versalien über 13 px, keine Rotfläche, keine verzerrte Schrift. **Gen-Z:** keine Pillen, keine Story-Kreise, keine Knopfreihen, keine rote Platte.
10. **Bewegung:** nur Bildzoom 1,03 in 0,35 s beim Überfahren; mit „Bewegung reduzieren“ keine. Kein JavaScript.
