# design.md – Linie B „Kalenderblatt“ (hm-almanac)

Fest gelegtes System dieser Linie. Gilt für alle Seiten in diesem Ordner und für das Theme, falls Luis diese Linie
wählt. Hallmark v2.0.0, Theme Almanac (gedealt 2/3), Akzent auf das Logo-Rot umgestimmt.

## Tokens (Quelle: `tokens.css`, Überschreibungen in `almanac.css`)

| Rolle | Wert |
|---|---|
| Grund | `oklch(95.5% 0.008 245)`, Stufen `92.5%` und `89%` |
| Bogen (das gedruckte Blatt) | `oklch(99% 0.003 245)` mit 2-px-Linie in Tinte oben |
| Tinte, Text, Grau | `oklch(16% 0.020 245)`, `oklch(26% 0.018 245)`, `oklch(46% 0.016 245)` |
| Linien | Haarlinie 1 px `oklch(84% 0.010 240)`, feste Linie 2 px `oklch(32% 0.018 240)` |
| Akzent | Logo-Rot `oklch(50.8% 0.177 25.6)`, dunkel `oklch(42% 0.16 25.6)`; nur Logo, Links, „als Nächstes“, Fokus |
| Schrift | Hanken Grotesk (OFL, selbst gehostet) für alles; Ziffern `tabular-nums lining-nums` |
| Größen | Text 18 px, Lesetext 19 px, klein 15 px (nur Tabellenköpfe, Stand, Nachweise); Schlagzeile höchstens 44 px Desktop, 32 px Handy; Abschnittsköpfe bis 38 px |
| Abstände | 4-px-Raster; `--space-head-after` 40 px zwischen Seitenkopf und erstem Block |
| Formen | eckig, Knöpfe 2 px Radius, keine Schatten, keine Karten |

## Bausteine

- **Bogen:** Kopf (Titel, Stand), Tabelle mit fester Linie unter dem Kopf, Haarlinien zwischen den Zeilen,
  Datum in Tabellenziffern; die eine Zeile, auf die die Seite zeigt, steht zwischen zwei festen Linien in Logo-Rot
  mit dem Wort „als Nächstes“. Keine Fläche, kein Seitenstreifen.
- **Seitenkopf:** Überschrift, ein Satz, ein Link oder höchstens ein gefüllter Knopf in Tinte; daneben (Handy:
  darunter) ein Foto aus einem eigenen Bericht mit Nachweis.
- **Teilen:** immer der schlichte Link „Per WhatsApp teilen“ bzw. „Teilen“.
- **Titel sind die Links**; keine Knöpfe „Beitrag lesen“.
- **Fehlt eine Angabe**, steht ein gestrichelter Platzhalter („folgt“, „fehlt“) oder ein Satz, was die Quelle nicht
  nennt.

## Hausstil-Ausnahmen von Hallmark (gelten auf allen Seiten dieser Linie)

| Gate | Ausnahme | Grund |
|---|---|---|
| 44c | Formular-, Verzeichnis-, Werbe-, Rubrik- und Startseite öffnen mit Titelkopf und Bogen statt mit einer Bühne | Der Bogen ist der Kopf; das Foto steht neben dem Kopf, nicht als Bühne |
| 59 | 40 px zwischen Seitenkopf und erstem Block (`--space-head-after`) | Kopf und Bogen gehören zusammen; die feste Linie trennt |
| 78 | Abschnittsköpfe eine Stufe unter dem Seitenkopf | Schlagzeilen sind auf 44/32 px gedeckelt (Entscheidung der Hauptsitzung nach Kritik r1) |
| 49b | Berichtstitel als Links brechen am Handy um | Ein Berichtstitel ist der Wortlaut des Berichts |

Diese Ausnahmen stehen zusätzlich als `waive`-Zeilen im Stempel der jeweiligen CSS-Datei, damit `sloplint` sie je
Seite nachprüft.

## Verboten (aus `abgelehnt.md` und den Kritiken r1/r2)

Dunkle Flächen, Rot als Fläche, Mono-Schriften, Serifen im Fließtext, Pillen, Karten, Dachzeilen, Versal-Labels,
„·“-Metazeilen, Seitenstreifen, Knopfpaare im Kopf, „Diese Woche“-Bänder.
