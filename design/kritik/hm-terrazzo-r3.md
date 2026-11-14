# Prüfung hm-terrazzo, Runde 3
Harte Kriterien: 19 von 19 erfüllt · P0: 0 · P1: 2 · P2: 4 · P3: 4

Grundlage: `design/brief-v3.md`, `design/linien-auftrag.md`, `tamil-marke` (Pflichten, `references/abgelehnt.md`),
Kritik r2 (19 abgeleitete Kriterien wie dort). Gemessen über `http://127.0.0.1:8957/richtungen/hm-terrazzo/`.
`begruendung.md` nicht gelesen. Im Bild geprüft: index, termine, artikel, kino (390 und 1280); rubrik nur gemessen.
Cockpit nicht Teil dieser Prüfung.

## Messwerte

| Messung | Ergebnis |
|---|---|
| `tools/shots.mjs`, index/termine/artikel/kino/rubrik × 390/820/1280 | 15 Aufnahmen, 0 Fehler, 0 Überlauf, 0 Konsole, 0 leere Bilder, alle Schriften geladen, 0 Tippflächen-Hinweise, `tamil_ohne_lang` 0 |
| `sloplint --genre editorial`, 4 Seiten + CSS, 4 URLs (je eigenes `--url`) | 0 FAIL · 4 WARN · 132 WAIVED · 1 ANSWERED · 6 DISMISSED · 20 NOTE. Die 4 WARN betreffen nur das Rendern der Dateien ohne Server (Schrift fehlt); die URL-Läufe ohne WARN. Verzichtete Gates: 4 (44c, 79, 78, 49b), r2: 6 |
| Zeichen je Zeile (Range-Messung je Zeichen, letzte Absatzzeile ausgenommen) | `artikel.html` 390 ⌀ 38 / max 44 · 820 ⌀ 60 / max 65 · 1280 ⌀ 60 / max 65 · `artikel-87` 1280 ⌀ 59 / max 65 · `artikel-43` 1280 ⌀ 60 / max 66 · `rubrik` `.reihe__text` 820 max 59, 1280 max 60 · Startseite `.lead` 1280 max 54, 820 max 63 · `termine` `.kopfblock__satz` 1280 max 63. Satzbreite Artikel jetzt 544 px (`max-width: 34rem`), r2 725–772 px |
| Aufmacherbild `rb-30.jpg` | Original 1280 × 960, gezeigt 358 × 201 (390), 632 × 356 (1280), `object-fit: cover; object-position: 50% 8%`; Krone des Gopuram im Bild bei 390, 1280 und im Artikel |
| Startseite 390 × 844 (y in px) | Kopf 123 · h1 409–500 · Datum ≈527 · „Per WhatsApp schicken“ ≈562 · Vorspann ein Satz ≈612 · 2. Schlagzeile „Zürich: Kündigung …“ 707–756, Datum ≈775 · 3. Schlagzeile ab 814 (angeschnitten). 0 `line-clamp`, 0 `text-overflow`, 0 „…“ im Seitentext |
| Startseite 1280 × 800 | Kopf 141 · Bild 165–521 · h1 573–672 · Metazeile 698, Teilen 733, Vorspann Zeile 1 bei 787 · rechts Kalenderboden 218–554 und zwei Termine 570–735 · „Nachrichten“ erst bei 1067 |
| Kalenderboden (`.kb`, Startseite) | Tabelle 7 × 6 = 42 Zellen, davon 12 Leerzellen (`paper-2`), 27 Tage ohne Eintrag, 3 Festtage in Tinte (8. vorbei in `ink-2`, 15., 21.), heute (13.) rote Ziffer und roter Balken unten. Zelle 62 × 44 px (1280), 51 × 44 px (390), 2-px-Tintenfugen. Lage: 1280 im ersten Bildschirm; **390 bei y 1949 (dritter Bildschirm), 820 bei y 2151** |
| Termine | „Als Nächstes“ (erste lesbare Terminliste) bei y 1300 (390) und 776 (1280 × 800, Zeilen ab ≈860); davor zwei Monatsraster (42 + 35 Zellen, 4 Festtage) |
| Schriftfamilien | 2 (Onest, Wix Madefor Display), alle geprüften Seiten |
| Größte Schrift | Startseite h1 28 px (390), 38,9 px (820), 46 px (1280) |
| Kontrast (oklch umgerechnet) | neue Kalenderfarben: `muted` auf `plate` ≈ 7:1, Papier auf `ink-2` ≈ 12:1, `accent` auf `plate` ≈ 5,7:1; keine Stelle < 4,5:1 gefunden |
| Gedankenstriche, „·“ im Seitentext | 0 / 0 (index, termine, artikel, kino) |

## Stand der r2-P1

| r2 | Befund | Stand r3 |
|---|---|---|
| P1-1 | Zeilenlänge Artikel > 70 Zeichen bei 820/1280 | **behoben**: max 65–66 Zeichen auf drei Artikeln, ⌀ 59–60; Rubrik max 60 |
| P1-2 | Aufmacherbild schneidet die Turmspitze ab | **behoben**: `object-position: 50% 8%`, Krone und oberste Figurenreihe sichtbar (Startseite 390/1280, Artikel 390/1280) |
| P1-3 | keine eigene Form, gewöhnliche Zeitungsseite | **teilweise**: Der Kalenderboden ist kein Kartenraster im verbotenen Sinn (die Zellen sind Tage, keine Anreißer, Inhalt kommt aus den Festen) und steht am Desktop im ersten Bildschirm. Er trägt aber nur dort; am Handy fehlt er auf den ersten zwei Bildschirmen, und er spricht die Sprache des Buchungs-Datumswählers. Rest als neuer P1-1 |
| P1-4 | Startseite 390: zweite Schlagzeile nicht ganz sichtbar, Vorspann mit „…“ | **behoben**: zwei vollständige Schlagzeilen (Aufmacher, „Zürich …“ bis y 756, Datum 775), Vorspann ein eigener kurzer Satz, keine Kappung |

Aus r2 P2 außerdem behoben: Doppelung „Zürich: Kündigung …“ (1 Vorkommen), Listen nach Datum (Nachrichten 02.09.,
17.08., 28.05., 25.05.; Tempel 07.09., 26.07., 27.06.), Falz 1280 (Datum und Teilen jetzt über dem Vorspann, im ersten
Bildschirm).

## Erster Eindruck (3 Sätze)
Am Desktop hat die Startseite jetzt ein Bild, das man wiedererkennt: großes Foto links, rechts ein Monat als
schwarz gefugte Tafel mit drei gefüllten Festtagen. Am Handy ist davon nichts zu sehen; dort bleibt es bei Logo,
Foto, Schlagzeile und linierter Liste, sauber, aber die gleiche Seite wie in r2. Die Tafel selbst liest sich eher
als Datumswähler eines Buchungsformulars denn als Terrazzo- oder Fliesenboden.

## Harte Kriterien

| # | Kriterium (Quelle) | Handy 390 | Desktop 1280 | Ergebnis |
|---|---|---|---|---|
| 1 | Logo unverändert (v3) | `bilder/logo.png` | dto. | erfüllt |
| 2 | Nur Deutsch, keine Tamil-Schrift als Schmuck | `tamil_ohne_lang` 0 | 0 | erfüllt |
| 3 | Echte Inhalte, Platzhalter sichtbar | Kino „6 weitere Städte; die Namen … liegen der Redaktion nicht vor“ | dto. | erfüllt |
| 4 | Bildnachweis an jedem Bild | unter jedem Bild | dto. | erfüllt |
| 5 | Fließtext Handy ≥ 18 px (Auftrag) | `--text-body` 1,125 rem = 18 px | 18 px | erfüllt |
| 6 | Kontrast AA | keine Stelle < 4,5:1 gefunden (Kalender ≥ 5,7:1) | dto. | erfüllt |
| 7 | Tippflächen 44 px | 0 Hinweise; Kalenderzellen 51 × 44 | – | erfüllt |
| 8 | Kein seitliches Scrollen | 0 px | 0 px (820: 0) | erfüllt |
| 9 | `prefers-reduced-motion` | `base.css`, `terrazzo.css` | dto. | erfüllt |
| 10 | Schriften selbst gehostet, OFL | alle geladen über `schriften/` | dto. | erfüllt |
| 11 | Keine Gedankenstriche | 0 | 0 | erfüllt |
| 12 | Keine Dachzeilen | 0 | 0 | erfüllt |
| 13 | Keine Versal-Labels | 0 | 0 | erfüllt |
| 14 | Keine „·“-Metazeilen | 0 | 0 | erfüllt |
| 15 | Keine gleich großen Kartenraster | Kalender = Datentabelle, keine Anreißer | dto. | erfüllt (Hinweis P1-1) |
| 16 | Keine Verlauf-Bildkacheln | 0 | 0 | erfüllt |
| 17 | Keine Seitenstreifen als Akzent | Spaltenlinie 2 px Tinte, „heute“ als Balken unten | dto. | erfüllt |
| 18 | Seitenliste vollständig | 11 Seiten + Bestätigung im Ordner | dto. | erfüllt |
| 19 | Zeilenlänge ≤ 70 Zeichen | max 44–46 | max 65–66 (820 ebenso) | erfüllt |

## Paarvergleich

Gegen die Runde-2- und Runde-4-Bilder in dieser Runde nicht neu gelegt; aus den Messwerten: kein Creme- oder Sandgrund,
keine Serife, keine runden Bilder (Runde 2); kein Rot als Fläche, größte Schrift 46 px, keine Versalien (Runde 4).

**NZZ, Desktop 1280 (`news-nzz-desktop-1.jpg`) gegen Startseite 1280:**
- Rechte Spalte: NZZ setzt dort eine zweite Geschichte mit Bild, Schlagzeile, Anreißer und Autorzeile. Die Probe setzt
  eine Tabelle mit 42 schwarz umrandeten Zellen; die dunkelste und schwerste Fläche des ersten Bildschirms ist damit
  ein Raster, nicht eine Geschichte. Nachrichten folgen erst bei y 1067.
- Linien: NZZ trennt die Spalten mit einer 1-px-Haarlinie in Grau; die Probe mit 2 px Tinte und zieht dieselbe Stärke
  durch jede Kalenderfuge. Die Seite wirkt dadurch strenger, aber auch technischer.
- Hierarchie: Bei der NZZ dominiert das Foto bis zum Falz; bei der Probe stehen Foto (632 × 356) und h1 (46 px) im
  ersten Bildschirm, das ist für die Aufgabe „lesen“ dichter als die NZZ.

**Guardian, Handy 390 (`news-guardian-handy-1.jpg`) gegen Startseite 390:**
- Der Guardian zeigt am Handy ebenfalls nur eine Geschichte im ersten Bildschirm, aber die Marke (Kopf, Serife,
  Rubrikfarben) ist unverwechselbar. Die Probe zeigt zwei Geschichten und ist ruhiger, an tamil.de bindet sie am
  Handy aber nur das Logo; die eigene Form (Kalenderboden) fehlt dort.
- Abstände: Die Probe hat gleichmäßige 16-px-Ränder und Haarlinien zwischen den Anreißern; das ist sauberer als die
  Kästen und Pillen des Guardian-Kopfs.

## Befunde

### P0
Keine.

### P1
1. **Kalenderboden trägt nur am Desktop und liest sich als Datumswähler** (Rest von r2-P1-3; Brief v3 „gemacht, nicht
   generiert“, „Handy zuerst“), `index.html`.
   (a) Am Handy liegt er bei y 1949 (dritter Bildschirm), bei 820 bei y 2151: Wer am Handy liest, also die Mehrheit,
   sieht dieselbe Seite wie in r2 (Foto, Schlagzeile, linierte Liste). (b) Er benutzt denselben Bildcode wie der
   Datumswähler in `buchen.html`: `.kb td.fest` (Tinte, helle Ziffer) entspricht `.kalender .tag--gewaehlt`
   (gewählter Tag), und die Legende auf `termine.html` lautet „Belegt sind die Tage mit Fest“, während „belegt“ in
   `buchen.html` die gesperrten, durchgestrichenen Tage meint. Ein Leser sieht also ein Formularelement, kein
   Zeichen der Marke. (c) Für drei Daten stehen 42 Zellen; 12 davon (29 %) sind graue Füllzellen, 27 leere Tage. Die
   Liste darunter wiederholt zwei der drei Feste. (d) Das „Fliesen“-Bild kommt nicht an: Die Zellen sind Rechtecke
   (62 × 44 bzw. 51 × 44 px) mit Tabellenrahmen.
   *Abhilfe:* am Handy direkt unter den Aufmacher, als eine Woche oder die nächsten 14 Tage in einer Zeile
   (7 bis 14 Zellen, Festtage gefüllt, darunter der nächste Termin), nicht als ganzer Monat; Leerzellen weglassen;
   den Buchungs-Datumswähler optisch anders auszeichnen (gewählt z. B. Rahmen statt Füllung) und in der Legende
   „Festtage“ statt „belegt“ schreiben; Fugen zum Inhalt hin dünner (1 px) und nur außen 2 px, damit die Tafel als
   Fläche und nicht als Tabelle wirkt.
2. **Termine: keine lesbaren Termine im ersten Bildschirm** (Auftrag: „kommende Termine zuerst“; Job „finden“),
   `termine.html` 390 und 1280. Am Handy füllen zwei Monatsraster (77 Zellen, 4 Festtage) den ersten Bildschirm;
   die Liste „Als Nächstes“ mit Name, Ort und „Per WhatsApp schicken“ beginnt bei y 1300. Bei 1280 × 800 liegt ihr
   Kopf bei 776, die Zeilen ab ≈860, also ebenfalls unter dem Falz. Was am 15. ist, erfährt man nur durch Tippen auf
   ein schwarzes Feld oder Scrollen. *Abhilfe:* „Als Nächstes“ vor die Monate; am Desktop die Liste links an die
   Stelle des frei stehenden h1-Blocks, Monate rechts; am Handy nur den laufenden Monat und Dezember darunter oder
   hinter einem Link.

### P2
1. **Startseite 1280: nur der Aufmacher als Geschichte im ersten Bildschirm**, `index.html` 1280 × 800. In r2 standen
   Aufmacher und vier Nachrichten im ersten Bildschirm; jetzt nimmt der Kalenderboden die rechte Spalte, „Nachrichten“
   beginnt bei y 1067. Zwischen Ende des Aufmacherblocks (897) und dieser Überschrift liegen 170 px mit einer Linie.
   Keine Verletzung von „Cover mit nur einer Geschichte“, weil zwei Termine sichtbar sind, aber ein Rückschritt für die
   Aufgabe „lesen“. *Abhilfe:* Kalenderboden schmaler (eine Woche, siehe P1-1) und zwei Nachrichtenzeilen darunter in
   derselben Spalte; Abstand vor „Nachrichten“ auf ≈ 64 px.
2. **Kalenderzellen verlinken auf die eigene Seite**, `termine.html`: 21. Nov. und 13. Dez. zeigen auf `termine.html`
   (neu laden statt springen); auf der Startseite verlinkt die Zelle 21 auf `termine.html`, der Listeneintrag „Diwali
   in Basel …“ daneben ist kein Link, der Eintrag darüber schon. *Abhilfe:* Sprungmarken auf die Zeile in „Als
   Nächstes“ (`#t-2026-11-21`), Listeneinträge einheitlich verlinken.
3. **Kino: „Städte“ ist eine Liste ohne Funktion**, `kino.html` 390 (≈ y 530–740) und 1280 (rechte Spalte des ersten
   Bildschirms). Sieben Städtenamen als reiner Text (`ul.stadtliste`, keine Links), gesetzt wie eine Navigation, und
   direkt darunter dieselben Städte als erste Tabellenspalte. *Abhilfe:* streichen oder zu Sprunglinks auf die
   Tabellenzeilen machen; am Handy den gewonnenen Platz für die Tabelle nutzen.
4. **Unterseitenköpfe 1280 senkrecht zentriert, Kanten springen**, `termine.html` (h1 bei y 456, Kalender ab 210,
   ≈ 300 px Leerfläche links oben) und `kino.html` („Städte“ bei 325, h1 bei 210). Die Startseite und der Artikel
   setzen oben bündig. *Abhilfe:* Kopfblöcke oben ausrichten (`align-items: start`), die Fläche für Inhalt nutzen.

### P3
1. **„Nachrichten“ am Handy unsichtbar**, `index.html` 390: `h2.feld__kopf--still` ist 1 px hoch; die zweite Geschichte
   steht ohne sichtbaren Feldkopf, bei 1280 hat sie einen. *Abhilfe:* bei 390 klein sichtbar lassen.
2. **Teilen-Link in zwei Wortlauten**: „Per WhatsApp schicken“ (Startseite, Termine, Kino), „Per WhatsApp teilen“
   (Artikel). *Abhilfe:* eine Form.
3. **„Termin einreichen“ zweimal im ersten Bildschirm**, `termine.html`: Rahmenknopf im Kopf und Tintenknopf unter
   dem h1. *Abhilfe:* auf dieser Seite einen davon weglassen.
4. **Vier Reflex-Gates seitenweit verzichtet** (44c, 79, 78, 49b; r2 sechs), sloplint: „house style“. *Abhilfe:* in
   eine `design.md` übernehmen.

## Was trägt
- Alle vier r2-P1 sind angegangen, drei vollständig: Satzbreite 544 px mit 59–60 Zeichen im Mittel, Bildausschnitt
  mit Turmkrone, zwei ganze Schlagzeilen am Handy ohne Kappung.
- Ruhe ohne Rückfall: 2 Familien, größte Schrift 46 px, Rot nur im Logo, an „heute“ und im Fokus, keine Verläufe,
  Schatten, Versalien, Gedankenstriche oder „·“; 0 Fehler in 15 Aufnahmen.
- Der Kalenderboden kommt aus dem Inhalt (Feste der Community) und ist barrierearm gebaut: Festname in jeder Zelle
  für Screenreader, Zellen 44 px hoch, Kontrast ≥ 5,7:1.

## Bedienbarkeit (nur zur Information)

| Nielsen | 0–4 | Satz |
|---|---|---|
| 1 Status | 3 | Aktive Rubrik rot unterstrichen, „heute“ im Kalender markiert. |
| 2 Sprache der Nutzer | 3 | Klar; „belegt“ für Festtage ist Buchungssprache. |
| 3 Kontrolle | 2 | Kalenderzellen laden die eigene Seite neu statt zu springen. |
| 4 Konsistenz | 2 | Gleicher Bildcode für Festtag und gewählten Buchungstag; zwei Wortlaute für Teilen. |
| 5 Fehlervermeidung | 3 | Pflichtfelder markiert (r2, nicht neu geprüft). |
| 6 Erkennen statt Erinnern | 2 | Festtage im Raster ohne sichtbaren Namen; Name erst in der Liste darunter. |
| 7 Flexibilität | 2 | Keine Suche im Kopf. |
| 8 Ästhetik und Reduktion | 3 | Ruhig; doppelte Stadtliste im Kino, 12 Füllzellen im Kalender. |
| 9 Fehlerhilfe | 2 | Fehlerzustände der Formulare nicht gezeigt (r2, nicht neu geprüft). |
| 10 Hilfe | 3 | Legende unter dem Kalender auf der Terminseite, nicht auf der Startseite. |

Nicht geprüft: Zoom 200 %, Tastaturweg, Formular- und Verzeichnisseiten im Bild, Cockpit. Der sloplint-Renderlauf hat
seine Aufnahmen nach `design/richtungen/hm-terrazzo/.hallmark/shots/` geschrieben (Werkzeugverhalten, gitignored).
