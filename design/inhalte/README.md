# Gemeinsames Material für die Proben (Runde 2)

- `inhalte.json`: die festen, echten Inhalte für alle Proben. Aufmacher, vier Nebenstücke mit Bild, sechs Meldungen
  ohne Bild, Rubrikblock „Küche“ und der Dienstblock „Diese Woche“. Ausgewählt nach Bildqualität, nicht nach Datum:
  Karten, Werbegrafiken und Collagen aus dem Bestand erscheinen nur als Meldung ohne Bild.
- `inhalte-klar2.json`: die Inhalte für die Fassung `klar2` (Brief, Abschnitt 10). Jeder Anreißer hat ein Bild:
  Die Meldungen mit Karte und Werbegrafik sind gegen Beiträge mit Foto getauscht; dazu kommen die Kopfzeile, sieben
  Rubrikkacheln (je ein Foto aus einem echten Beitrag der Rubrik, das sonst nicht auf der Seite steht) und der
  Bereich „Diese Woche“ mit zwei Kino-Beiträgen. Die Einträge aus dem News-Radar haben kein Foto und bekommen eine
  gestaltete Kachel.
- `bilder/`: Originale der alten tamil.de, nur lesend geholt und verkleinert (`python tools/bild_holen.py`);
  `bilder.json` hält Maße, Originalmaße und Quelle fest. Der Bestand endet im November 2024.
- `logo.png`: das Logo unverändert (300 × 121 Pixel). Eine Vektordatei liegt nicht vor.

Neu erzeugen: `python tools/bild_holen.py --out design/inhalte/bilder --breite 1600 9631` und
`--breite 1200 9655 9642 9662 9711 9600 9597 9594 9591`. Für `klar2` dazu:
`--breite 1600 9670 9635 9572 9556 9674 9583 9650 9697 9711 9600 8468 9344 9198 9146 9149 6708 8527`.
