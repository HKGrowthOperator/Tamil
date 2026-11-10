---
name: tamil-richtung
description: Wie eine Gestaltungsprobe für tamil.de entsteht – als Schnellprobe (nur Startseite), Skizze oder Probeseite – mit festem Umfang, kurzer Begründung, Ablage und Prüfung. Vorgeladen im art-director; gilt für /design-runde und /design-ausbau.
user-invocable: false
---

# Eine Probe gestalten

Du baust **genau eine** Variante. Grundlage, in dieser Reihenfolge: `design/brief.md` (Leitplanken, Farbwerte,
Schriftkandidaten, harte Kriterien), `design/referenzen/news-marken.md` (Vorbilder mit Messwerten), Skill
`tamil-marke` (Pflichten, Verbotsliste). Der Brief geht allem anderen vor. Der Auftrag nennt dir `slug`, Variante und
Umfang.

Ziel ist die Ruhe und Ordnung einer großen Nachrichtenmarke. Wertigkeit entsteht aus Hierarchie, Abständen, sauberem
Satz und guten Bildausschnitten, nicht aus einer Idee oder einem Effekt.

## 1. Erst festlegen, dann bauen – `design/richtungen/<slug>/begruendung.md`

Kurz halten (Schnellprobe: höchstens zehn Zeilen):

1. **Vorbild:** ein bis zwei Marken aus `news-marken.md` und welche Messwerte du übernimmst (Kopfhöhe,
   Schlagzeilengröße, Spalten, Bildformat).
2. **Schrift:** aus der Kandidatenliste des Briefs für deine Variante, in normaler Breite. Nicht erlaubt: alles von den
   Verbotslisten in `tamil-marke`. Tamil im Inhalt setzt eine Ersatzschrift im Schriftstapel (`lang="ta"`).
3. **Farbe:** die festen Werte aus dem Brief. Rot nur für Logo, Links und kleine Marken.
4. **Ordnung:** die drei Stufen der Anreißer (Aufmacher, Nebenstück mit Bild, Meldung ohne Bild) mit ihren Größen;
   das eine Format für Dachzeile und Datum.
5. **Erkennungszeichen (freiwillig, leise):** etwas aus dem Inhalt, zum Beispiel wie Spielorte und Termine gesetzt
   sind. Kein Effekt, kein Riesenwort.
6. **Abgrenzung** gegen Runde 2 (alt, Portal aus dem Baukasten) und Runde 4 (laut), je mit einem Messwert
   (`tamil-marke/references/abgelehnt.md`).

## 2. Umfang

| Auftrag | Seiten | Inhalt |
|---|---|---|
| Schnellprobe (`/design-runde`, vor der Wahl) | nur `index.html`: Kopf mit Logo und Rubriken, Aufmacher, drei bis vier Nebenstücke mit Bild, Meldungsliste ohne Bild (vier bis sechs Titel), ein Rubrikblock, Dienstblock „Diese Woche“ | Handy 390 und Desktop 1280 ernst; bei 820 nur kein Überlauf; kein Fuß, keine Zustände |
| Skizze (`/design-runde`, nach der Wahl) | dazu `artikel.html` (Kopf bis erster Absatz) und die Anmerkungen von Luis | Handy und Desktop gleich ernst |
| Probeseite (`/design-ausbau`) | Start, Artikel, Rubrik, Events, Kinoliste, Kontakt | alle Zustände, die das Theme braucht |

- Inhalte, Bilder und Logo liegen fertig in `design/inhalte/` (`inhalte.json`, für die Fassung `klar2`
  `inhalte-klar2.json`; `bilder/`, `logo.png`). Nimm genau
  diese Inhalte in genau dieser Reihenfolge; nichts erfinden, nichts weglassen. Einbinden relativ
  (`../../inhalte/…`).
- Schrift selbst hosten in `design/richtungen/<slug>/schriften/`, mit Lizenzdatei.
- Eigene CSS-Datei `<slug>.css`, kein Framework, kein JavaScript.
- Für `klar2` gilt Abschnitt 10 des Briefs (Aufbau 10.2, harte Kriterien 10.4). Er geht den Zeilen dieser Anleitung
  vor, wo sie „Meldung ohne Bild“ oder „kein Effekt“ sagen.
- Pflichten aus `tamil-marke` gelten ab der ersten Probe (18 px Fließtext, 44 px Tippflächen, Kontrast, `lang="ta"`).

## 3. Prüfen, bevor du abgibst

```bash
node tools/shots.mjs design/richtungen/<slug>/index.html --out design/richtungen/<slug>/shots --kacheln
node design/vergleich/aufnahmen.mjs <slug>     # sichtbarer erster Bildschirm und Kennzahlen
```

- 0 Fehler im Bericht von `shots.mjs`.
- Die Kennzahlen aus `aufnahmen.mjs` gegen die harten Kriterien des Briefs halten (Zahl der Schlagzeilen im ersten
  Bildschirm, Rotanteil, größte Schrift, größter Radius). Was verstößt, behebst du vor der Abgabe.
- Den ersten Bildschirm bei 390 und 1280 ansehen und neben das Bild deines Vorbilds legen: Ist das dieselbe Liga?
  Würde jemand „Baukasten“, „laut“ oder „altbacken“ sagen? Dann überarbeiten.
- Gegen die Verbotsliste prüfen.

## 4. Abgabe

Kurzbericht (höchstens zehn Zeilen): Pfade, Vorbild, Schrift, Kennzahlen, Prüfergebnis, was offen ist. **Keine**
Selbstbewertung.

Bei einer Überarbeitung: nur die genannten Punkte beheben (Anmerkungen von Luis oder P0/P1 aus
`design/kritik/<slug>-r<n>.md`), `begruendung.md` um einen Abschnitt „Überarbeitung“ ergänzen, neu prüfen.
