# Design – Tamil.de

Modernes Community-Magazin. Warmes Weiß, dunkles Braungrau, Rot aus dem Logo als führende Farbe. Gilt für das
WordPress-Theme (`wordpress/themes/tamil`). Das Redaktions-Cockpit (`news_radar/web`) nutzt dieselben Farben und
Schriften in ruhigerer Form (Produkt-Register, siehe unten).

## Overview

- **Stimmung:** hell, warm, aufgeräumt. Nachrichten ruhig und seriös, Kino und Community lebendig.
- **Strategie:** zurückhaltende Grundfläche mit einer entschiedenen Markenfarbe. Rot erscheint in Logo, Links,
  Knöpfen, Rubrikpunkt „Nachrichten“ und in genau einer großen Fläche pro Seite (Mitmach-Band). Safran nur für
  „bald“-Termine und als Punkt auf Rot.
- **Bilder:** groß, abgerundet, ohne Rahmen und ohne Text-Overlays.

## Colors

Hex-Werte stehen in `theme.json` (Palette) und als Variablen in `assets/css/theme.css`.

| Token | Hex | Rolle |
|---|---|---|
| `papier` | `#FDF9F5` | Seitenhintergrund |
| `weiss` | `#FFFDFB` | Flächen auf Papier (Termin-Kacheln, Formulare) |
| `sand` | `#F8EFE4` | ruhige Flächen: Anzeigen, Rezept, Kinoliste, Datumskachel |
| `sand-2` | `#F2E6D9` | Hover auf Sand, Chips |
| `linie` | `#E5DCD5` | Trennlinien, Ränder |
| `tinte` | `#332924` | Text, Überschriften, Footer-Fläche (13.5:1 auf Papier) |
| `tinte-2` | `#655851` | Vorspann, Nebentext (6.5:1) |
| `tinte-3` | `#72665F` | Meta-Zeilen, Datum (5.3:1) |
| `rot` | `#B5282A` | Markenfarbe aus dem Logo; Links, Hauptknopf, Mitmach-Band (Weiß auf Rot 6.3:1) |
| `rot-tief` | `#921A1D` | Hover |
| `rot-hell` | `#FFEAE8` | Hinterlegung, Fokus |
| `safran` | `#F8AC3D` | nur: Datumskachel „bald“, Punkt auf roter Fläche |

**Rubrikpunkte** (9 px, immer mit Wort daneben, nie allein): Nachrichten `rot`, Kino `#8A57AE`,
Events `#DA8A11`, Community `#3D8E53`, Küche `#C96736`, Kultur `#346AAC`, Sport `#0D9298`,
Entertainment `#C65085`.

Nie reines Schwarz oder Weiß. Keine Verläufe, kein Glas, keine dunklen Bühnen.

## Typography

| Rolle | Schrift | Schnitt | Größe |
|---|---|---|---|
| Titel, Navigation, Labels | **Catamaran** (Latein + Tamil aus einer Hand) | 600–800 | Aufmacher `clamp(34px, 4.4vw, 58px)`, Abschnitt `clamp(28px, 3vw, 38px)`, Karte 19–32 px |
| Fließtext, Vorspann | **Literata** (Leseschrift, optische Größen) | 400, kursiv für Zitate | Text 18 px (Handy) bis 20 px (Artikel), Vorspann 20–22 px |

- Laufweite bei Titeln −0.01 bis −0.025 em, Zeilenhöhe 1.02–1.2; Fließtext 1.6–1.7, max. 68 Zeichen.
- Keine Großbuchstaben-Labels, keine verspielte Kursive, keine tamilischen Wörter als Dekor vor Überschriften.
- Tamil-Text (`lang="ta"`) läuft automatisch in Catamaran (Tamil-Subset).

## Elevation

Flach. Tiefe entsteht durch Fläche (Sand auf Papier) und Abstand, nicht durch Schatten. Einziger Schatten: das
geöffnete Menü am Handy.

## Components

- **Kopf:** weiß-transparent, klebt oben; Logo links, Rubriken in der Mitte als Text-Pills, rechts „Werben“, Suche,
  Menü. Am Handy darunter eine wischbare Rubrik-Leiste.
- **Meta-Zeile:** Rubrikpunkt + Rubrik (fett) · Ort · Datum · Lesezeit, Catamaran 14 px.
- **Karte:** Bild (Radius 14–22 px) oben, darunter Meta und Titel; Variante „Zeile“ mit quadratischem Vorschaubild
  rechts. Kein Rahmen, keine Schatten. Hover: Bild zoomt 2.5 %, Titel wird `rot-tief`.
- **Abschnittskopf:** großer Punkt in Rubrikfarbe + Titel, rechts „Alle …“ in Rot.
- **Termin-Kachel:** Datumsblock (Sand, „bald“ = Safran) + Rubrik + Titel + Ort, auf `weiss` mit Linie.
- **Mitmach-Band:** rote Fläche, Radius 28 px, weißer Titel, Kolam-Linie als Motiv, Knöpfe Weiß und Umriss.
- **Knöpfe:** Pill, 46 px hoch. Haupt: `tinte` → Hover `rot`. Marke: `rot`. Auf Rot: `weiss` / Umriss.
- **Anzeige:** Sand-Fläche mit Label „Anzeige“ darüber, Radius 14 px, ordnet sich dem Inhalt unter.
- **Footer:** einzige dunkle Fläche (`tinte`), Wortmarke, vier Spalten.

## Layout

- Inhalt max. 1240 px, Ränder `clamp(16px, 4vw, 40px)`.
- Startseite: Bühne (Aufmacher 1.75 fr + „Neu auf Tamil.de“ 1 fr) → Anzeige → Nachrichten → Kino (mit Kinoliste) →
  Termine → Entertainment → Community + Mitmach-Band → Rezept → Production → Kultur/Sport.
- Abschnitte im Mosaik (eine große Geschichte + drei Zeilen) statt gleichförmiger Kartenraster.
- Abstände: zwischen Abschnitten 72 px, innerhalb 24–32 px.
- Brüche: ≤ 600 px Handy, ≤ 1023 px Tablet (eine Spalte, Rubrik-Leiste), darüber zwei Spalten.

## Cockpit (Produkt-Register)

Gleiche Tokens, hell. Seitenleiste auf `sand`, Arbeitsfläche `papier`, Listen statt Kacheln, Bearbeiten in zwei
Spalten (Text | Vorschau und Bild). Status-Pills in gedämpften Rubrik-/Statusfarben, ein roter Hauptknopf je Ansicht.
