# klar – Begründung (Skizze)

1. **Vorbild:** BBC News und tagesschau. Übernommen: ein Bildformat 16:9 für alle Bilder (BBC), Aufmacher-Schlagzeile 28 px Handy / 34 px Desktop (tagesschau 32/34, BBC 24/28), Desktop wie BBC: Aufmacher mit Bild neben dem Text, rechts eine Spalte mit Meldungen; Nebenstücke wie tagesschau-Bildschirm 2 (Bild links, Text rechts); Trennung nur durch 1-px-Linien, Radius 0.
2. **Schrift:** Libre Franklin (variabel, normale Breite, OFL, `schriften/`), Schlagzeilen 600–650, Text 400. Tamil im Inhalt: Ersatzschrift über `:lang(ta)`.
3. **Farbe:** die festen Werte des Briefs; Rot nur im Logo und in der Rubrik der Dachzeile (13 px). Fläche nur für „Diese Woche“.
4. **Ordnung:** Aufmacher 28/34 px · Nebenstück mit Bild 19/22 px · Meldung ohne Bild 17/18 px. Dachzeile immer „Rubrik | 17. Juli 2024“, 13 px, über der Schlagzeile.
5. **Erkennungszeichen:** „Diese Woche“ als nüchterne Liste: Film, Zahl der Kinos, Städte; Termin mit Datum, Ort, Veranstalter.
6. **Abgrenzung:** gegen Runde 2 kühler Grund statt Creme, Grotesk statt Serifen-Fließtext, Radius 0 statt runder Bilder (R2 etwa 12 px); gegen Runde 4 größte Schrift 34 px statt 98–335 px, Rotanteil unter 1 % statt 6–54 %, keine Versalien in Schlagzeilen.
7. **Artikel:** eine Spalte (Bild 680 px, Text höchstens 29 em ≈ 66 Zeichen), Dachzeile wie auf der Startseite, `h1` 28/36 px, Vorspann 19/20 px (Gewicht 500), Fließtext 18/19 px bei Zeilenhöhe 1,6.
8. **Artikel:** Lesezeit und „Per WhatsApp teilen“ als schlichte Leiste unter einer 1-px-Linie (Link unterstrichen, rot nur beim Überfahren); darunter nur Bild und Text.

## Überarbeitung (Prüfung r1)

- Nebenstücke am Handy: Bild 132 × 74 px, Dachzeile an der Bildunterkante, Schlagzeile darunter über die volle Breite. Daneben gesetzt liefen die Titel bei 120–132 px auf 4–5 Zeilen; der Brief erlaubt höchstens 3.
- „Diese Woche“: Etiketten „Im Kino“ und „Termine“ in der Form der Dachzeile (13 px, Rot), Datum des Termins als Meta-Zeile (13 px, leise); am Desktop drei gleich breite Spalten mit derselben Linie und Oberkante. Vorspann der Nebenstücke am Desktop höchstens 31 em (≤ 66 Zeichen).
- Klein: Rubrik „Nachrichten“ im Artikel als aktiv markiert (`aria-current`, Rot, 600); in „Küche“ nur noch das Datum statt Rubrik und Datum.
