# Gemeinsames Material für die Proben (Runde 2)

- `inhalte.json`: die festen, echten Inhalte für alle Proben. Aufmacher, vier Nebenstücke mit Bild, sechs Meldungen
  ohne Bild, Rubrikblock „Küche“ und der Dienstblock „Diese Woche“. Ausgewählt nach Bildqualität, nicht nach Datum:
  Karten, Werbegrafiken und Collagen aus dem Bestand erscheinen nur als Meldung ohne Bild.
- `bilder/`: Originale der alten tamil.de, nur lesend geholt und verkleinert (`python tools/bild_holen.py`);
  `bilder.json` hält Maße, Originalmaße und Quelle fest. Der Bestand endet im November 2024.
- `logo.png`: das Logo unverändert (300 × 121 Pixel). Eine Vektordatei liegt nicht vor.

Neu erzeugen: `python tools/bild_holen.py --out design/inhalte/bilder --breite 1600 9631` und
`--breite 1200 9655 9642 9662 9711 9600 9597 9594 9591`.
