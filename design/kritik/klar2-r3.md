# Prüfung klar2, Runde 3 (gezielte Nachprüfung)
Harte Kriterien: 15 von 16 erfüllt (Kriterium 16 in dieser Runde laut Auftrag nicht geprüft, keine Verletzung) · P0: 0 · P1: 0 · P2: 3

Stand der Messung: 10.11.2026, `aufnahmen.mjs klar2` und `tools/shots.mjs … --kacheln` (6 Aufnahmen, 0 Fehler), dazu eigene
Playwright-Skripte im Scratch-Ordner (`b.js` Artikel, `c.js` Startseite, `d.js` Bildformate, Alt-Texte, Kontrast 820).

## Teil A: Harte Kriterien (Brief 10.4)

| # | Kriterium | Handy (390) | Desktop (1280) | Ergebnis |
|---|---|---|---|---|
| 1 | Viele Geschichten | 2 Schlagzeilen ganz sichtbar | 6 | erfüllt |
| 2 | Kopf ≤ 152 px, Aufmacher ab ≤ 480 px | Kopf 147 px, Schlagzeile ab 323 px | Kopf 167 px (keine Grenze), ab 264 px | erfüllt |
| 3 | Drei Stufen, Aufmacher ≥ 1,25 × Nebenstück, ≤ 2 Familien | 30 : 19 px = 1,58; 1 Familie (Libre Franklin) | 40 : 20 px = 2,0; 1 Familie | erfüllt |
| 4 | Größte Schrift ≤ 34/44, zweitgrößte ≤ 24/28, Zeilen, Versalien | 30 px (Aufmacher), zweitgrößte 22 px; max. 4 Zeilen (Aufmacher 3 im Bild); Versalien 0 | 40 px (Aufmacher), zweitgrößte 26 px; Versalien 0 | erfüllt |
| 5 | Rot ≤ 3 %, keine rote Schrift > 20 px | 0,13 %, größte rote 13 px | 0,09 %, größte rote 13 px | erfüllt |
| 6 | Genau zwei dunkle Flächen, ≤ 12 % im ersten Bildschirm | nav.band + #diese-woche; 6,4 % | dieselben zwei; 5,8 % | erfüllt |
| 7 | Keine Effekte | Radius 0, Schatten 0, gedreht 0, Breite normal | ebenso | erfüllt |
| 8 | Kein Baukasten | keine Pillen, Knöpfe, Icons an Anreißern (Sichtprüfung) | ebenso | erfüllt |
| 9 | Überall ein Bild, Grafik ≤ 3 | ohne Bild 0, Grafik 3 (Scene, Ramayana, Diwali) | ebenso | erfüllt |
| 10 | Ein Format für Dachzeile/Datum; ≤ 3 Bildformate (von Hand gezählt, Logo ausgenommen) | 390: 1,33 · 1,78 · 2,67 = **3** | 820: 1,33 · 1,78 · 2,67 = **3**; 1280: 1,33 · 1,78 · 2,67 = **3**; Dachzeile überall „Rubrik \| Datum“ | erfüllt |
| 11 | Bildgröße | über Dateibreite: keins | über halber Dateibreite nur p9631 (Aufmacher) und p9600 (große Küche-Kachel), beide erlaubt | erfüllt |
| 12 | Helle Schrift ≥ 4,5 : 1 | kleinster 5,98 | kleinster 5,90 (820 von Hand: 6,16) | erfüllt |
| 13 | Bewegung | Maßstab 1,03, längster Übergang 0,35 s, Animationen 0, reduziert 0; fest nur nav.band 46 px | ebenso, Band 48 px | erfüllt |
| 14 | Kein Überlauf, keine Konsolenfehler | 0 px, 0 Fehler (Start und Artikel) | 0 px bei 820 und 1280, 0 Fehler | erfüllt |
| 15 | „Diese Woche“ ≤ 2532 px | Oberkante 2025 px | – | erfüllt |
| 16 | Paarvergleich | in dieser Runde nicht durchgeführt (Auftrag) | – | nicht geprüft |

Bildformate im Einzelnen: 1,33 = Aufmacher, große Kino-Kachel, bei 390 auch große Küche-Kachel, bei 820 auch die drei
kleinen Küche-Kacheln; 1,78 = Rubrikkacheln, Nebenstücke, Meldungen, bei 820/1280 große Küche-Kachel; 2,67 = kleine
Kino-Kachel und bei 390/1280 die kleinen Küche-Kacheln. Die Zuordnung wechselt je Breite (siehe P3), die Zahl bleibt drei.

## Teil B: Artikelseite

### B1 Zeichen je Zeile (eigene Zählung über Zeichen-Rechtecke, Leerzeichen eingeschlossen, letzte Zeile je Absatz ausgenommen)

| Breite | Fließtext: Zeilen gezählt · längste · Median · Mittel | Vorspann: Zeilen · längste · Median | Grenze 70 |
|---|---|---|---|
| 390 | 28 · **43** · 39 · 38 | 4 · 37 · 35 | eingehalten |
| 820 | 19 · **65** · 57 · 55 | 3 · 56 · 55 | eingehalten |
| 1280 | 18 · **65** · 59 · 59 | 3 · 56 · 55 | eingehalten |

Titel bei 820 einzeilig mit 49 Zeichen über 712 px; auch er bleibt unter 70.

### B2 Schrift, Zeilenhöhe, Kontrast

- Fließtext: 18 px / 28,8 px (1,6) bei 390 und 820; 19 px / 30,4 px bei 1280. Pflicht 18 px am Handy erfüllt.
- Vorspann 19 px (390, 820) und 20 px (1280), Zeilenhöhe 1,45. Titel 28 px (390, 820), 38 px (1280).
- Kontraste (OKLCH umgerechnet): Tinte auf Grund rund 17 : 1; Dachzeile/Datum/Lesezeit `oklch(0.45 …)` auf Grund 7,1 : 1;
  Rot #B5282A (Rubrik) auf Grund 6,1 : 1. Alle über 4,5.
- Kleine Angaben: Meta 13 px, Leiste 14 px; lesbar, aber an der Untergrenze für ältere Leser (keine Pflichtverletzung).

### B3 Aufbau im Bild

- Reihenfolge bei allen Breiten: Kopfzeile, Logo, Rubrikband (aktiv „Nachrichten“, weiß, 600, rote 3-px-Linie), Dachzeile
  „Nachrichten | 17. Juli 2024“, Titel, Vorspann, Linie, Leiste „2 Min. Lesezeit“ links und „Per WhatsApp teilen“ rechts,
  großes Bild, drei Absätze.
- 390: Alles auf einer Kante (16 px), Bild randlos 390 × 293. Ruhig und klar.
- 820: Artikel auf Kante 54 px, Logo und Band auf 24 px. Rechts drei verschiedene Kanten: Titel/Leiste/Bild enden bei
  766 px, Vorspann bei 605 px, Fließtext bei 576 px (siehe P2-2).
- 1280: Textspalte 560 px, zentriert (360–920), Bild 1040 px (120–1160), ebenfalls zentriert; Logo und Band auf 40 px.
  Verhältnis Bild zu Spalte 1,86 : 1, symmetrisch um dieselbe Mitte; wirkt geordnet, wie bei Zeit oder Spiegel. Kopf
  und Fließtext teilen links und rechts die Kante 360/920.
- Die Seite endet nach dem dritten Absatz ohne Fußzeile oder Rückweg (siehe P3).

### B4 Tastatur

Reihenfolge 390: Suche → Logo → 9 Rubriken (Nachrichten zuerst) → „Per WhatsApp teilen“. Bei 820 und 1280 vorweg die zwei
Hinweise „Diese Woche“. Jeder Fokus sichtbar: auf hellem Grund 2 px Tinte mit 3 px Abstand, im Band 2 px hell nach innen
(-4 px), dadurch an keiner Seite abgeschnitten. Kein fokussiertes Element liegt unter dem stehenden Band (gemessen:
Überdeckung 0 bei allen Einträgen). Tippflächen ≥ 44 px bei 390 und 820 (Band 46, Logo 56, WhatsApp 44); bei 1280 sind
die Kopfzeilen-Links 38 px hoch (Desktop, keine Pflicht).

### B5 Inhalt gegen `inhalte-klar2.json`, Schlüssel `artikel`

Dachzeile „Nachrichten“, Titel, Datum „17. Juli 2024“, Lesezeit 2 Min. stimmen. Die drei Absätze sind zeichengleich
(Skriptvergleich: gleich). Der Vorspann endet sauber bei „stattfand.“; das abgeschnittene Bruchstück der Liste („Die
britische Tamilin, die sri-lankisch-tamilischer …“) ist weggelassen, was zum ersten Absatz passt. Keine Autorenzeile, kein
Bildnachweis, nichts erfunden. Alt-Text des Bildes stimmt mit dem Foto (rote Labour-Rosette, Unterstützer).

## Teil C: Startseite

### C1 Seitliche Streifen (390 und 820)

- 390, Rubrikband: 9 Einträge per Tab; jeder ganz im Behälter (kleinster Rand 4 px), Fokusrahmen nach innen, nicht
  abgeschnitten. In Ruhe rechts angeschnitten („Commun…“, 78 von 106 px sichtbar). `scroll-snap-type: x`.
- 390, Rubrikkacheln: 7 Einträge; jeder ganz sichtbar (Rand mindestens 16 px), Rahmen über `::after` nach innen, im Bild
  (Kachel „Kultur“) vollständig. In Ruhe rechts angeschnitten (82 von 138 px). Nach dem Tabben frei verschiebbar
  (scrollLeft 656 → 0 → 656).
- 820, Rubrikkacheln: 7 Einträge, jeder ganz sichtbar (Rand mindestens 24 px), in Ruhe angeschnitten (124 von 160 px), frei
  verschiebbar (396 → 0 → 396). Band bei 820 passt ohne Laufen.
- Nebenbeobachtung: Nach dem Tabben bleibt das Band bei 390 verschoben stehen; die aktive Rubrik „Nachrichten“ ist dann
  nicht mehr zu sehen (P3).

### C2 „Diese Woche“, Kachel „Diwali in Basel“, 1280

Kachel 1200 × 118 px. Linke Gruppe Titel/Datum 60–313 px, rechte Gruppe Ort/Text 361–973 px (Text endet bei 937 px):
Abstand zwischen den Gruppen 48 px, beide oben bündig (2373/2375). Kein Loch zwischen den Gruppen, aber rechts in der
Kachel bleiben 267 bis 303 px (rund 25 % der Breite) leere „Fläche auf Dunkel“ (siehe P2-1).

### C3 Kopfzeile 600 bis 1023 px

| Breite | Hinweise | Höhe Kopfzeile | Kopf bis Unterkante Band |
|---|---|---|---|
| 600, 640, 700, 760, 799 | ausgeblendet | 45 px | 155 px |
| 800, 820, 900, 1000, 1023 | sichtbar, jeder Link einzeilig | 45 px | 155 px |
| 1024 | sichtbar, einzeilig | 39 px | 167 px |

Kein Umbruch, kein Überlauf an keiner der Breiten.

### C4 Zoom beim Überfahren (1280)

Aufmacher, Rubrikkachel, Meldung, Küche-Kachel: vorher `none`, nach 500 ms `scale(1.03)`. Titel und Link-Fläche
unverändert (Rechtecke vor/nach gleich), also kein Sprung; Titel im Bild bleibt hell und lesbar, er wird unterstrichen.
Mit `reducedMotion: 'reduce'` bei 0, 100, 300, 500 ms: `transform: none`, Übergang 0 s.

## Teil D

- Alt-Texte der sechs Meldungsbilder gegen die Dateien: alle sechs treffen (Ufertempel Mahabalipuram, Kamala Harris im
  grauen Blazer mit Perlenkette, Mann mit Bart am Mikrofon vor Orange, Priester mit heiliger Asche im Tempel, junge Frau
  mit langen dunklen Haaren, Wandgemälde mit Soldaten und goldener Statue).
- Die sieben Rubrikkacheln haben `alt=""`; der Rubrikname steht als Text im Link. Zulässig, weil die Kachel Navigation
  ist (P3, Hinweis).
- Helle Schrift bei 820 von Hand (Text ausgeblendet, hellster Pixel unter jeder Zeile, 58 Zeilen): kleinster Wert 6,16 : 1
  („16. Juli 2024“, 13 px, Küche-Kachel), danach 6,28 und 6,31. Keine Zeile unter 4,5.

## Befunde

### P0
keine (Überlauf 0, Konsolenfehler 0, leere Bilder 0, Schriften geladen).

### P1
keine.

### P2
1. **1280, „Diese Woche“, Kachel „Diwali in Basel“:** rechts rund 270 bis 300 px leere dunkle Fläche (ein Viertel der
   Kachel), die Kachel wirkt wie ein zu breiter Balken mit Inhalt in der linken Hälfte. Behebung: Kachel auf die Breite
   der Kino-Gruppe begrenzen oder eine dritte Spalte nutzen (zum Beispiel Text bis zum rechten Rand laufen lassen,
   `max-width` des Textes aufheben und Titel/Datum-Spalte breiter setzen), oder „Termine“ neben „Im Kino“ stellen.
2. **820, Artikel:** drei rechte Kanten im Kopf und Text (Titel/Leiste/Bild 766 px, Vorspann 605 px, Fließtext 576 px)
   und eine andere linke Kante als Logo und Band (54 gegen 24 px). Brief 10.2.7 verlangt Kopf und Fließtext in einer
   Spalte. Behebung: bei 600 bis 1023 px eine Spaltenbreite für Kopf, Leiste und Text (etwa 560 px wie bei 1280), Bild
   darüber hinaus breit, oder die Spalte auf die Kante des Kopfs (24 px) setzen.
3. **Startseite, Bildformate je Breite:** dieselben Kacheln wechseln das Seitenverhältnis (große Küche-Kachel 1,33 bei
   390, 1,78 bei 820/1280; kleine Küche-Kacheln 2,67 bei 390/1280, 1,33 bei 820). Im Rahmen der drei Formate, aber der
   Bildausschnitt des gleichen Gerichts ändert sich sichtbar. Behebung: jeder Rolle ein festes Format über alle Breiten.

### P3
1. **Artikel, alle Breiten:** Seite endet nach dem dritten Absatz ohne Fußzeile oder Weg zurück zu weiteren Geschichten.
   Behebung: schlichte Fußzeile oder Liste „Weitere Nachrichten“ (für die Probe auch nur die Fußzeile).
2. **390, Rubrikband:** nach dem Tabben bleibt das Band verschoben, die aktive Rubrik ist nicht mehr sichtbar. Behebung:
   keine nötig im Prototyp; im Theme beim Laden die aktive Rubrik ins Bild schieben (`scrollIntoView` nur bei Laden, ohne
   Bewegung).
3. **Rubrikkacheln:** `alt=""` ist zulässig; bei späterer Nutzung als Inhaltsbild beschreibenden Alt-Text ergänzen.
4. **Artikel 390:** Meta 13 px und Leiste 14 px sind klein für ältere Leser; 14/15 px würde reichen, ohne die Ruhe zu stören.

## Was trägt (höchstens 3 Punkte)
- Artikelsatz: 18/19 px bei 1,6 Zeilenhöhe, längste Zeile 43 (Handy) und 65 (Desktop), zentrierte Spalte unter breitem Bild.
- Fokus durchgehend sichtbar und nach innen gezeichnet, auch in den laufenden Streifen; nichts unter dem stehenden Band.
- Bewegung genau in den Grenzen: nur Bild 1,03, Titel ortsfest, bei „reduziert“ keine Veränderung.

## Nicht geprüft
- Kriterium 16, Paarvergleich (laut Auftrag nicht in dieser Runde); daher keine Aussage zu „weniger classic“ gegenüber `klar`.
- Zoom auf 200 % und Bildschirmleser.
- Bilder der Kino-Kacheln und Küche-Kacheln gegen Alt-Texte (nur Meldungen und Rubrikkacheln geprüft).
- Hover-Zoom bei 820 und Touch-Verhalten.
- Bedienbarkeit nach Nielsen (nicht Teil dieser Nachprüfung).
