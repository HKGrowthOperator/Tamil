# Prüfung hm-terrazzo, Runde 2
Harte Kriterien: 18 von 19 erfüllt · P0: 0 · P1: 4 · P2: 3 · P3: 4

Grundlage: `design/brief-v3.md`, `design/linien-auftrag.md`, `tamil-marke` (Pflichten, `references/abgelehnt.md`),
Hallmark-Floor. Die 18 abgeleiteten Kriterien aus r1 gelten weiter; neu ist Nr. 19 (Zeilenlänge ≤ 70 Zeichen,
Pflicht laut `tamil-marke`), die r1 nicht gemessen hat. Gemessen über `http://127.0.0.1:8953/richtungen/hm-terrazzo/`.
Die Prüfung wurde auf Anweisung der Hauptsitzung vorzeitig abgeschlossen: Der Paarvergleich mit den Referenzbildern
wurde in dieser Runde nicht neu durchgeführt, Unterseiten nur per Messung und Code geprüft, nicht jede einzeln im Bild.
Cockpit nicht Teil dieser Prüfung.

## Messwerte

| Messung | Ergebnis |
|---|---|
| `tools/shots.mjs`, 12 Seiten × 390/820/1280 | 36 Aufnahmen, 0 Fehler, 0 Konsolenmeldungen, 0 Überlauf, alle Schriften geladen; gemeldete Tippflächen sind nur die versteckten 1×1-Eingaben (ihre Labels ≥ 44 px) |
| `sloplint --genre editorial`, 12 Dateien + CSS, 12 URLs | 0 FAIL · 12 WARN · 188 WAIVED · 22 DISMISSED · 1 ANSWERED · 42 NOTE. Die 12 WARN betreffen nur das Rendern der Dateien ohne Server (Schrift fehlt); die 12 URL-Läufe haben keine WARN. Sloplint: „6 reflex gates waived (44c, 79, 77, 78, 59, 49b): that is a house style“ |
| Schriftfamilien (berechnet, alle 12 Seiten, 390 und 1280) | 2: Wix Madefor Display (h1, h2, Monats- und Formularköpfe), Onest (alles andere). Kein Mono mehr |
| Größte Schrift | Startseite h1 30 px (390) / 46 px (1280); Termine `.naechster__wann` 32 / 48 px; alle Unterseiten h1 46 px bei 1280 |
| Versalien, Sperrung, Kursiv, Verläufe, Rundungen, Außenschatten | je 0 Elemente auf allen 12 Seiten |
| Kontrast (Canvas-Umrechnung der oklch-Werte, jedes Textelement gegen seinen Grund) | 0 Textstellen unter 4,5:1 |
| Fließtext Handy | 18 px (Artikel, Rubrik), Vorspann 19 px, Hinweistexte 17 px |
| Zeichen je Zeile (Range-Messung, letzte Zeile ausgenommen) | Artikel 390: ⌀ 38–40, max 44 · **820: ⌀ 81–89, max 90 · 1280: ⌀ 81–83, max 86** · Rubrik 1280: max 83 · Startseite-Vorspann 1280: max 74 |
| Kopfhöhe (`header`) | 123 px (390), 141 px (1280); r1: etwa 195 px bei 390 |
| Erster Bildschirm 390 × 844 | h1 bis y 506, „Nachrichten“ bei 754, erste Nachrichtenzeile 815–889 (bei 844 nach der ersten Zeile abgeschnitten) |
| Erster Bildschirm 1280 × 800 | Aufmacher + 4 Nachrichten ganz sichtbar; h1 627–726, Vorspann ab 757 vom Falz geschnitten, Datum und „Per WhatsApp schicken“ bei y≈873 |
| Aufmacherbild | Original 1280 × 960 (4:3), gezeigt 16:9 (728 × 410 bei 1280, 358 × 201 bei 390), Mittenausschnitt |

## Erster Eindruck (3 Sätze)
Aufgeräumt, kühl und ruhig; die lauten und baukastenhaften Reste aus r1 (Riesenziffer, Mono, Versatzschatten, rosa
Fläche, roter Seitenstreifen, Vollton-Knopf) sind weg. Was bleibt, ist eine ordentliche Zeitungsseite: großes Bild
links, Schlagzeilenliste rechts, senkrechte 2-px-Spaltenlinie, darunter Tabelle und Liste im selben Muster. Die
„Feldordnung“ liest sich als gewöhnliche Spaltenlinie, wie sie jede Tageszeitung hat; an tamil.de bindet die Seite
nur das Logo und der Inhalt, keine Form.

## Harte Kriterien

| # | Kriterium (Quelle) | Handy 390 | Desktop 1280 | Ergebnis |
|---|---|---|---|---|
| 1 | Logo unverändert (v3) | `bilder/logo.png` | dto. | erfüllt |
| 2 | Nur Deutsch, keine Tamil-Schrift als Schmuck (v3) | `tamil_ohne_lang` 0 | dto. | erfüllt |
| 3 | Echte Inhalte, Platzhalter sichtbar (v3) | Titel, Daten, Kino nach Inhaltsliste; Impressum „Texte folgen von KBS Digitalmedia“ als gestrichelte Lücke | dto. | erfüllt (Doppelung siehe P2-1) |
| 4 | Bildnachweis an jedem Bild (v3) | Nachweis unter jedem Bild der Startseite und im Fuß | dto. | erfüllt |
| 5 | Fließtext Handy ≥ 18 px (Auftrag) | 18 px, Vorspann 19 px | 18 px | erfüllt |
| 6 | Kontrast AA (v3) | 0 Stellen < 4,5:1 | 0 | erfüllt |
| 7 | Tippflächen 44 px (v3) | nur versteckte Eingaben gemeldet; Links im Fließtext ausgenommen | – | erfüllt |
| 8 | Kein seitliches Scrollen (v3) | 0 px | 0 px (820: 0) | erfüllt |
| 9 | `prefers-reduced-motion` (Auftrag) | `base.css`, `terrazzo.css` Ende | dto. | erfüllt |
| 10 | Schriften selbst gehostet, OFL im Ordner | `schriften/*.woff2`, zwei OFL-Dateien | dto. | erfüllt |
| 11 | Keine Gedankenstriche (Auftrag) | 0 im eigenen Text | 0 | erfüllt (`buchen.html` Bis-Strich, sloplint NOTE 19) |
| 12 | Keine Dachzeilen | 0 | 0 | erfüllt |
| 13 | Keine Versal-Labels | 0 | 0 | erfüllt |
| 14 | Keine „·“-Metazeilen | 0 | 0 | erfüllt |
| 15 | Keine gleich großen Kartenraster | keine | keine | erfüllt |
| 16 | Keine Verlauf-Bildkacheln | 0 Verläufe | 0 | erfüllt |
| 17 | Keine Seitenstreifen als Akzent | aktiver Buchungsschritt jetzt 2-px-Linie unten | dto. | erfüllt |
| 18 | Seitenliste vollständig | 11 Seiten + Bestätigung | dto. | erfüllt |
| 19 | Zeilenlänge ≤ 70 Zeichen (`tamil-marke`, Pflichten) | Artikel max 44 | **Artikel ⌀ 81–83, max 86 (820: max 90); Rubrik max 83** | **verletzt** |

## Paarvergleich
In dieser Runde nicht neu gegen die Referenzbilder gelegt (Abbruch auf Anweisung). Gegen den eigenen Stand aus r1:
- Dichte 1280: r1 ein Aufmacher und drei Terminzeilen; jetzt Aufmacher und vier Nachrichten im ersten Bildschirm,
  die Leerfläche von etwa 130 px ist weg.
- Kopf 390: r1 etwa 195 px mit zweizeiliger Navigation; jetzt 123 px, eine Zeile, angeschnittenes „Nachrichte…“ zeigt
  das Weiterwischen.
- Satz: zwei Familien statt drei; Wix Madefor Display ist ruhiger und schmaler als Syne, die breiten Ziffern sind weg.

## Befunde

### P0
Keine.

### P1
1. **Zeilenlänge im Fließtext über 70 Zeichen** (A19), `artikel.html` und alle `artikel-*.html` bei 820 und 1280,
   `.artikel__text > p { max-width: 65ch }` ergibt 725 bis 772 px und ⌀ 81 bis 89 Zeichen (Onest hat eine breite „0“,
   65ch sind hier gut 80 Zeichen); `rubrik.html` 1280 `.reihe__text` (60ch) bis 83 Zeichen. *Abhilfe:* Maß in rem
   statt ch, etwa `max-width: 34rem` (≈ 610 px, ≈ 70 Zeichen bei 18 px Onest) für Artikel und Rubrik-Anreißer; den
   Vorspann der Startseite (74 Zeichen) auf `36rem`.
2. **Aufmacherbild schneidet die Tempelspitze ab** (B, Bildausschnitt im ersten Bildschirm), `index.html` 390 und 1280,
   `artikel.html` 390 und 1280, `.bild--16-9` auf `rb-30.jpg`: Das Original (4:3) zeigt den Gopuram mit Krone
   (y≈70–110); der 16:9-Mittenausschnitt beginnt bei y≈120, die oberste Reihe und die Krone fehlen. Es ist das erste,
   was jeder Leser sieht. *Abhilfe:* je Bild einen Bildpunkt setzen (`object-position: 50% 8%` für dieses Foto) oder
   am Desktop 3:2 mit Anschnitt unten; generell Fokus je Bild im Bauskript statt Mittenausschnitt.
3. **Die Feldordnung trägt keine eigene Form; die Seite ist eine gewöhnliche Zeitungsseite** (B Baukasten; Brief v3
   „gemacht, nicht generiert“; Runden 5–7 „saubere, aber austauschbare Nachrichtenseite“), alle Seiten. Belege:
   (a) Jede Zeile der Startseite ist dieselbe Konstruktion `.feldreihe` mit senkrechter 2-px-Tintenlinie
   (8-4, 7-5, 5-7, 7-5); das ist die Spaltenlinie jeder Tageszeitung, kein „Feldplan“, den man als eigenes Zeichen
   erkennt. (b) Vom Terrazzo-Material ist nichts übrig; der Stempel sagt es selbst („weakest: S, the floor idea shows
   only as an order of fields, not as a surface“). (c) Die Kopfschrift Wix Madefor Display ist die Vorgabe des
   Hallmark-Themes „Dusk“, Onest die des Themes „Terrazzo“: beide aus dem Katalog, keine aus dem Leser abgeleitete Wahl.
   (d) Sechs Reflex-Gates sind seitenweit verzichtet (188 WAIVED), sloplint nennt das „house style“. Gegenüber r1
   besser: die Felder haben jetzt verschiedene Inhalte (Textliste, Tabelle, Kinoliste, kleine Bilder), und die
   Unterseitenköpfe haben Varianten (`--termin`, `--kino`, `--suche`, `--werben`). *Abhilfe:* einen Zug finden, der
   nur hier passt und aus dem Inhalt kommt, und ihn sichtbar im ersten Bildschirm zeigen, zum Beispiel den
   Festkalender als eigenes Feld mit echter Kalenderform (Monat, Tage, die nächsten Feste markiert) oder Kino als
   Matrix Film × Stadt; die Spaltenlinie nur dort, wo zwei Felder wirklich verschiedenes Material trennen; die
   Kopfschrift begründet wählen.
4. **Erster Bildschirm 390 zeigt weiter nur eine lesbare Geschichte** (C „Cover mit nur einer Geschichte“; Marke:
   Aufmacher und weitere Geschichten), `index.html` 390 × 844: Aufmacher bis y≈680, dann rund 75 px Abstand bis zur
   Fuge, Kopf „Nachrichten“ bei 754, die erste Nachricht beginnt bei 815 und ist nach einer Zeile („Bundestagsdrucksache:
   14“) abgeschnitten. Dazu ist der Vorspann per `-webkit-line-clamp: 2` mitten im Satz mit „…“ gekappt („Ein Blick
   auf das Festjahr des neuen…“). *Abhilfe:* Datum und „Per WhatsApp schicken“ in eine Zeile, Orte am Handy aus der
   Metazeile; Abstand vor dem Nachrichtenfeld am Handy auf 24 px; den Feldkopf „Nachrichten“ am Handy kleiner oder in
   die Fuge; statt Kappen mit „…“ einen eigenen kurzen Satz für das Handy. Ziel: mindestens eine zweite Schlagzeile
   ganz sichtbar.

### P2
1. **Dieselbe Geschichte zweimal auf der Startseite**, `index.html` alle Breiten: „Zürich: Kündigung trifft Restaurant
   Maneez und tamilische Läden im Kreis 5“ steht unter „Nachrichten“ und unter „Küche“. *Abhilfe:* in einem der
   Felder durch einen anderen Beitrag ersetzen.
2. **Listen nicht nach Datum geordnet**, `index.html`: „Nachrichten“ 17.08., 28.05., 25.05., 02.09.; „Tempel, Vereine
   und Schulen“ 26.07. … 21.03., dann 07.09. Ohne erkennbare Regel wirkt die Reihenfolge zufällig. *Abhilfe:* neueste
   zuerst, oder die redaktionelle Gewichtung sichtbar machen.
3. **Falz 1280 × 800 schneidet den Aufmacher**, `index.html`: Schlagzeile ganz sichtbar (sie ist der Link), der
   Vorspann bricht nach zwei von drei Zeilen ab, Datum und „Per WhatsApp schicken“ liegen bei y≈873. Teilen ist eine
   der drei Aufgaben der Seite (Brief v3). *Abhilfe:* Vorspann auf einen Satz (sloplint NOTE 58: 28 Wörter),
   Metazeile mit Teilen-Link über den Vorspann oder Bild am Desktop 2:1.

### P3
1. **Sechs Reflex-Gates seitenweit verzichtet** (44c, 79, 77, 78, 59, 49b). Einige sind für eine Nachrichtenseite
   begründet (49b umbrechende Titel, 78 ruhigere Feldköpfe); in der Summe ist es eine Hausordnung. *Abhilfe:* in
   eine `design.md` übernehmen oder abbauen, wie sloplint vorschlägt.
2. **Ortsangaben in wechselnder Form**, Startseite: „in Aarau, Schweiz“, „in Leuk“ (ebenfalls Schweiz), „in Zürich,
   Schweiz“ neben „in Zürich“, „in Deutschland“. *Abhilfe:* eine Regel (Stadt allein, Land nur außerhalb DE).
3. **h1 46 px auf allen Unterseiten bei 1280**, Termine-Datum `.naechster__wann` 48 px. Brief v3 hat die alten
   Grenzen (38/44 px) ersetzt, deshalb kein P1; zur Einordnung: kleiner als jede Runde-4-Skizze, aber größer als die
   frühere Aufmachergrenze.
4. **Eigenwerbung als „Anzeige“**, `index.html` Billboard „Dein Fest im Kalender.“ verweist auf `einreichen.html`.
   Echte Anzeige ist es nicht. *Abhilfe:* als „Anzeigenplatz, Beispiel“ kennzeichnen oder als Hinweis der Redaktion.

## Stand der r1-P1

| r1 | Befund | Stand r2 |
|---|---|---|
| P1-1 | roter Seitenstreifen am aktiven Buchungsschritt | **behoben**: `.schrittfolge a[aria-current]` jetzt 600 und 2-px-Tintenlinie unten |
| P1-2 | Syne (Ausschlussliste) | **behoben**: Wix Madefor Display, auf keiner Liste; Herkunft siehe P1-3 |
| P1-3 | drei Familien, JetBrains Mono | **behoben**: gemessen 2 Familien auf allen 12 Seiten |
| P1-4 | erster Bildschirm 390 nur eine Geschichte | **teilweise**: Kopf 195 → 123 px, Navigation einzeilig, Bild 16:9; zweite Geschichte weiter nur angeschnitten (P1-4) |
| P1-5 | dunkles Kino-Band mit Riesenziffer | **behoben**: kein `.kinoband` mehr; Kino als linierte Liste auf hellem Grund |
| P1-6 | rosa Hinterlegung (Premium, Hover) | **behoben**: kein `accent-soft`; Premium als Wort und 2-px-Tintenlinien |
| P1-7 | Knopf „Beitrag lesen“ | **behoben**: kein `.btn--primaer` auf der Startseite, die Schlagzeile ist der Link |
| P1-8 | ein Baustein für alles, keine eigene Idee | **teilweise**: Felder inhaltlich verschieden, Unterseitenköpfe variiert; die Idee bleibt eine Spaltenlinie (P1-3) |

Aus r1 P2 außerdem behoben: Versatzschatten (0 Außenschatten), Hinweistexte 16 → 17 px, Dichte am Desktop.

## Was trägt
- Ruhe ohne Rückfall: 0 Versalien, 0 Verläufe, 0 Rundungen, 0 Schatten, Rot nur im Logo, in Fokus, Stern und
  „Premium“; kühler Grund, kein Runde-2-Ton.
- Inhalte ehrlich und vollständig belegt: Nachweis unter jedem Bild und im Fuß, Platzhalter als gestrichelte Lücke.
- Desktop-Startseite mit fünf Geschichten im ersten Bildschirm und klarer Rangfolge Bild, Schlagzeile, Liste.

## Bedienbarkeit (nur zur Information)

| Nielsen | 0–4 | Satz |
|---|---|---|
| 1 Status | 3 | Aktive Rubrik rot unterstrichen, Buchungsschritt markiert. |
| 2 Sprache der Nutzer | 4 | Klare deutsche Sätze. |
| 3 Kontrolle | 3 | Navigation am Handy wischbar, Ende angeschnitten sichtbar. |
| 4 Konsistenz | 4 | Ein Kopf, ein Listenmuster, eine Formularform. |
| 5 Fehlervermeidung | 3 | Pflichtfelder markiert, belegte Tage durchgestrichen. |
| 6 Erkennen statt Erinnern | 3 | Termine mit Wochentag und Ort. |
| 7 Flexibilität | 2 | Keine Suche im Kopf. |
| 8 Ästhetik und Reduktion | 3 | Aufgeräumt; doppelte Geschichte, gekappter Vorspann. |
| 9 Fehlerhilfe | 2 | Fehlerzustände der Formulare nicht gezeigt. |
| 10 Hilfe | 3 | Ablauf beim Einreichen und Buchen erklärt. |

Nicht geprüft: Zoom 200 %, Tastaturweg, Unterseiten im Bild einzeln, Cockpit. Hinweis: Der sloplint-Renderlauf
schreibt seine Aufnahmen nach `design/richtungen/hm-terrazzo/.hallmark/shots/` (gitignored); die Dateien dort stammen
jetzt aus diesem Prüflauf.
