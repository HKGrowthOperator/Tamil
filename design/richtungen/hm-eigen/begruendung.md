# hm-eigen „Tagesblatt“ – Begründung

Stand 13.11.2026. Probe nach `design/brief-v3.md`, gestaltet mit Hallmark (eigene Richtung, `scaffold --custom`).
Seiten: `index.html` (Start), `artikel.html` (Deepavali, 8.11.) und 19 weitere `artikel-<id>.html`, `termine.html`
(Festkalender 2026), `kino.html`. Erzeugt aus echtem Material mit dem Generator `bauen.py` (in diesem Ordner).

## Idee

tamil.de ordnet sich wie der Kalender in der tamilischen Küche: das Datum vorn und groß, Sonntage und Festtage rot,
jeder Beitrag an seinem Tag. Der Abreißkalender hängt in fast jedem tamilischen Haushalt; er ist vertraut, ohne
Folklore zu sein (keine Ornamente, keine tamilische Schrift als Schmuck, nur Deutsch).

## Hallmark-Picks

| Achse | Wahl |
|---|---|
| Shape | Tagesblatt (eigene Form): Tagesziffer links, Aufmacher rechts; darunter Listen nach Tagen |
| Papier | Jasminweiß `oklch(97.6% 0.007 120)`, Tinte Blattgrün-Schwarz `oklch(21% 0.022 155)` |
| Rot | Logo-Rot `oklch(50.5% 0.175 25)`: nur Ziffern an Sonntagen und Festtagen, Logo, ein Primärknopf, Fokus |
| Zweite Farbe | Bananenblatt `oklch(35% 0.075 150)` nur als Fläche des Kino-Bereichs |
| Schrift | Rethink Sans 800 für Ziffern und Überschriften, Golos Text für Lesetext (beide OFL, selbst gehostet) |
| Signatur | die große Tagesziffer; rot, wenn der Tag ein Sonntag oder Festtag ist (Thai Pongal, Tamilisches Neujahr, Deepavali) |
| Haltung | geteilt (split), zwei Druckfarben, Linien statt Kästen, keine Karten |
| Bilder | Fotos aus Commons mit Nachweis am Bild und im Fuß |

Abgrenzung: keine Dachzeilen, keine Versal-Labels, keine „·“-Metazeilen, keine gleich großen Kartenraster, keine
Bildkacheln mit Verlauf und Titel im Bild, keine „Diese Woche“-Bänder (Runden 5–7); kein Nachtblau/Gold (Runde 1),
kein Sand/Braungrau/Serifen-Fließtext (Runde 2), keine Pillen und Story-Kreise (Runde 3), keine rote Fläche, keine
Schräglagen, keine verzerrte Schrift (Runde 4). Schwächste Achse laut Vorab-Kritik: Rot und schwere Grotesk erinnern
an Runde 3/4; deshalb ist Rot nie Fläche, sondern nur Bedeutung (welcher Tag).

## Inhalte

Alles echt: 20 Rückblick-Beiträge aus `design/inhalte/rueckblick/rueckblick.json` (Bilder mit Nachweis), 62
datierte Entwürfe aus `docs/redaktion/rueckblick-2026.md` für den Festkalender, Kino aus `design/inhalte/inhalte.json`
(Stand 9. November 2026). Kommende Termine nur mit Beleg: 15.11. Düsseldorf Tamil Sangam (aus Beitrag 30), 21.11.
Basel Tamil Sangam, 13.12. THADAM Bern (Radar-Entwurf). „Heute“ ist der 13.11.2026. Impressum und Kontakt sind als
Platzhalter gekennzeichnet.

## Prüfung

- `sloplint --genre editorial` (statisch und gerendert über `http://127.0.0.1`): **0 FAIL**. Offen bleiben
  REFLEX 79 (Weißraum unter dem Kopf von Artikel, Termine, Kino bei 1440) und Hinweise zu Wortzahlen (Artikel und
  Kalender sind von Natur aus dicht; Ausnahmen begründet im Stempel von `hm-eigen.css`).
- `node tools/shots.mjs` bei 390/820/1280 für Start, Artikel, Termine, Kino: 0 Fehler, kein seitliches Scrollen,
  keine Konsolenfehler, keine leeren Bilder. Kleine Tippflächen nur bei „Quelle“-Links im Bildnachweis (Textlinks,
  nach WCAG 2.2 ausgenommen).
- Fließtext 18 px, Kontrast der Tinte auf Papier > 14:1, Rot auf Papier 6,0:1, weiße Schrift auf Rot 6,0:1.
- Unabhängige Prüfung aus frischem Kontext: `design/kritik/hm-eigen-r1.md`.

## Neu bauen

`python3 design/richtungen/hm-eigen/bauen.py` (liest `design/inhalte/` und `docs/redaktion/rueckblick-2026.md`,
schreibt die HTML-Seiten und kopiert Bilder, Logo und Schriften).
