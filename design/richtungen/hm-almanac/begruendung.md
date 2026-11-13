# hm-almanac – Begründung

Linie B „Kalenderblatt“ nach `design/brief-v3.md` und `design/linien-auftrag.md`, gebaut mit Hallmark v2.0.0, Theme
Almanac (gedealt 2/3), Akzent auf das Logo-Rot umgestimmt. Idee in einem Satz: tamil.de als gedrucktes Jahrbuch der
Community, in dem Termine, Spielorte, Einträge und Preise als Bogen mit festen Linien und Tabellenziffern stehen.
Statisches HTML/CSS, Schriften selbst gehostet (`schriften/`, OFL), Bilder als Kopien in `bilder/`. Datenseiten
erzeugt `bauen.py` (Aufruf vom Repo-Root: `python3 design/richtungen/hm-almanac/bauen.py`).

## Seitenliste

| Datei | Inhalt |
|---|---|
| `index.html` | Startseite: Überschrift über dem Bogen der nächsten Termine, daneben der Deepavali-Bericht mit Foto; Kino als heller Bogen; Hamm; Jahr 2026 in Berichten (alle 20 Zeilen verlinkt) |
| `rubrik.html`, `rubrik-2.html` | Rubrik Community: neuester Bericht als Split, dann datierte Zeilen mit Bild am Zeilenende, Seitennavigation 1 von 2 |
| `artikel.html` | Deepavali (Beitrag 30) mit Bildnachweis, Randbogen der genannten Termine, WhatsApp, Weiterlesen |
| `artikel-<id>.html` | die übrigen 19 Rückblick-Beiträge aus `rueckblick.json`, gleiche Form; Randbogen „Im Rückblick 2026“ mit dem Bericht davor und danach |
| `termine.html` | Festkalender: kommende Termine zuerst, darunter das Festjahr 2026 als ein Diagramm (Einträge mit Bericht verlinkt) |
| `kino.html` | Spielorte nach Stadt (Deutschland, Schweiz), darunter nach Film, Kinojahr 2026 als heller Bogen, Koovagam |
| `verzeichnis.html` | Suche, Filter Art (Business, Dienstleister, Verein, Tempel) und Ort (Land, Bundesland/Kanton, Stadt), Liste als Bogen; 12 Einrichtungen aus den Berichten, je mit Datum des Berichts; Filter wirken sofort und stehen in der Adresse |
| `verzeichnis-eintrag.html` | Profil Ceylon Palace, Bremen; Markierung „Premium“ sichtbar und als Muster gekennzeichnet; jede fehlende Angabe steht als „fehlt“ |
| `einreichen.html`, `einreichen-danke.html` | Termin einreichen mit allen Feldern aus §12, Einwilligung, Falle für Programme; Bestätigung mit Vorgangsnummer (Platzhalter) als eigener Zustand |
| `werben.html` | sechs Werbeplätze mit Maßen aus `ads.php`, Preis „folgt“, frühester Start, Ablauf der Buchung |
| `buchen.html` | Buchung in fünf Schritten: Platz und Laufzeit, Startdatum im Monatsbogen (Vorlauf gesperrt), Angaben, Werbemittel, Prüfen und Zahlung (Knopf gesperrt, Preise folgen) |
| `kontakt.html` | Formular „Nachricht“, Kontaktwege als Platzhalter gekennzeichnet |

## Hallmark-Picks

**Hallmark · v2.0.0**

- **Shape** · Kalenderblatt (eigener Name), aus Draw `26f3b5` · genre editorial · job: listen (lesen): Lesen im Aufmacher, die Daten im Hero direkt daneben. Gezogen war Manifesto; getauscht, weil Manifesto mit großer, schräger Versalschrift Zustimmung verkauft, also genau das, was in Runde 4 als „laut, Baukasten“ abgelehnt wurde. Der Job ist lesen und finden.
- **Theme** · Almanac, dealt 2/3 (Seed `tamil-deutschsprachiges-online-magazin-der-ff32·6bcf19c0·2026-11-13·r0`): heller kühler Schieferton (seit Runde 8 L 95,5 statt 84), fast weißer Bogen, Hanken Grotesk für Köpfe, Fließtext und Ziffern (Tabellenziffern; Newsreader und IBM Plex Mono sind seit Runde 8 bzw. Kritik r1 entfernt), zwei Linienstärken, eckig. **Akzent auf das Logo-Rot umgestimmt** (`oklch(50.8% 0.177 25.6)`, gemessen aus `logo.png`); Almanacs Magenta (Farbton 350) läge nur 35° daneben und würde sich wie ein Druckfehler lesen. Rolle und Haltung bleiben: restrained, unter 5 %, eine Zeile, der gefüllte Knopf, die Unterstreichungen.
- **Chrome** · nav: Tintenband „Rückblick 2026 in zwanzig Berichten“ über einer Leiste, die beim Abwärtslesen einfährt (Logo unverändert, Termine, Kino, Rückblick) · footer: Indexspalten (Logo, Dienste, Rubriken, Bildnachweise, Rechtliches).
- **Hero** · Startseite Ledge: der Bogen oben über 12 Spalten, Kopf „Deepavali ist vorbei. Gefeiert wird weiter.“ auf der Grundlinie, Satz und Aktionen rechts daneben · Termine Index · Kino und Artikel Banner.
- **Signature** · das Kalenderblatt: die nächsten Feste als gedruckter Bogen, Datum in Tabellenziffern, die nächste Zeile (So 15.11., Düsseldorf Tamil Sangam) zwischen zwei festen Linien, Datum und Titel in Logo-Rot, dazu „als Nächstes“; keine Fläche, kein Seitenstreifen. Derselbe Bogen trägt Verzeichnis, Preisliste und Buchungskalender. Auf `termine.html` zusätzlich das Festjahr 2026 als ein großes Diagramm mit elf Festen und dem heutigen Tag als roter Linie.
- **Sections** (Stand nach Kritik r1) · Startseite: Überschrift über dem Bogen, daneben Deepavali mit Foto · Kino als heller Bogen · Split Hamm-Uentrop, Foto rechts · Jahr-Index mit Reitern · Footer. Termine: Bogen November/Dezember · Festjahr-Diagramm · Split Glattbrugg · Footer. Kino: Städte als Bogen · nach Film · Kinojahr als heller Bogen · Split Koovagam · Footer. Artikel: Kopf mit Bild über zehn Spalten · Text mit Randbogen „Im Beitrag genannt“ · drei Anschlusslinks · Footer. Weggelassen laut Draw: Statement, Steps. Getauscht: die Bild-Rail (Bildkachelreihe = abgelehntes Kartenraster) gegen das Kino-Tintenband.
- **Material** · real: 20 Rückblick-Beiträge 2026 (`rueckblick.json`), Termine Deepavali München 8.11., Düsseldorf Tamil Sangam 15.11., Diwali in Basel 21.11., THADAM Bern 13.12., Kino „Scene“ (11 Kinos), „Ramayana: Rise of a Legend“ (Gütersloh, Ravensburg), „OM“ (12 Spielorte), „Jailer 2“ (Kino Claudia, Kloten, 15.11.), Kinojahr und Festjahr aus `rueckblick-2026.md`, das Logo · pictures: die Commons-Bilder der Beiträge rb-30, rb-71, rb-76, rb-43, Behandlung muted, Nachweis im Fuß und im Artikel unter dem Bild · absent: Uhrzeiten, Preise, Kinonamen zu „Scene“ und „OM“, Datum Thai Pongal 2027, Impressum und Datenschutz.
- **Sweep (Runde 8)** · `sloplint --genre editorial` über http für alle 32 Seiten (Dateien und `--url`): 0 FAIL, 0 REFLEX offen, 0 WARN offen; neu verzichtet (je Seite begründet im Stempel): 44c und 59 (Formular-, Verzeichnis-, Werbe- und Rubrikseiten öffnen mit einem Titelkopf über Bogen oder Formular), 78 (Schrittköpfe, Profilköpfe, Berichtstitel in Listen), 49b (Berichtstitel als Links) · `tools/shots.mjs`: 48 Aufnahmen (16 Seiten × 390/820/1280), 0 Fehler, kein seitliches Scrollen, keine Konsolenfehler · keine neue Prüfung aus frischem Kontext in dieser Runde (Agents starten keine Agents; die unabhängige Kritik veranlasst die Hauptsitzung).
- **Sweep (Runde 7)** · Floor 0 FAIL · Reflex 0 offen (1 Verzicht: 49b, Berichtstitel als Links brechen am Handy um) · 1 Finish beantwortet (F17, Etiketten der Zeitleiste) · 5 WARN begründet zurückgewiesen (58 Seitenwörter inkl. versteckter Reiter, 58 Fenster 85 und 91 Wörter, 77 auf Termine und Artikel) · hero-review: fix, 5 Befunde, 1 erledigt, 2 teilweise, 2 bewusst belassen · finish-review: Subagent in frischem Kontext (`claude -p`, Sonnet), fix, 8 Befunde, 3 erledigt, 5 teilweise · `tools/shots.mjs`: 12 Aufnahmen, 0 Fehler (kein seitliches Scrollen, keine Konsolenfehler).

## Prüfungen und was daraus geändert wurde

**Hero-Review (Startseite, frischer Kontext):**
- Kein Foto im ersten Bildschirm: bewusst belassen. Der Bogen ist das Bild, so wie Almanac die gedruckte Tabelle als Hero vorsieht. Das Deepavali-Foto folgt direkt darunter.
- Kopflastig, 280 px Leere bei 1920: behoben, der Hero ist jetzt so hoch wie sein Inhalt.
- Signatur zu schwach, zwei 15.11.-Zeilen gleich: teilweise behoben. Die nächste Zeile hat jetzt eine 4 px rote Kante und ein kräftigeres Datum, die Kinozeile heißt „„Jailer 2“ im Kino“.
- Kopf zeitgebunden: bewusst belassen. Die Startseite ist datiert wie ein Almanach-Blatt.
- Am Handy rutscht der Bogen nach unten: teilweise. Der Kopf steht vorn, der Bogen beginnt bei etwa y 425 von 812.

**Finish-Review (alle vier Seiten, frischer Kontext), erstes Wort `fix`:**

Erledigt:
- Hamm-Uentrop: Kopf jetzt in Display-Größe, Foto über sechs Spalten.
- Termine und Kino: die Aktion steht jetzt unter dem Satz, die Linie unter „Diese Woche im Kino“ läuft über die volle Breite.
- Tippflächen: Band, Fußlinks und Teilen-Link haben jetzt 44 px.

Teilweise:
- Startseite: weniger Abstand zwischen Hero und Aufmacher.
- Jahr-Index: die Reiter laufen am Handy in einer scrollbaren Zeile.
- Zeitleiste: das Etikett „Vaani Vizha“ steht jetzt rechtsbündig, frei von der Heute-Linie.
- Kinojahr: leere Orte heißen jetzt „ohne Ortsangabe“.
- Artikel: die rote Kante im Randbogen ist weg, „Weiter im …“ heißt jetzt „Mehr zu Tempeln und Festen“.

Belassen, mit Grund:
- Die Bildbreite über zehn Spalten im Artikel folgt Almanac.
- Die Schriftgrößen der Zeitleiste sind 15 px; der Reviewer hat sie auf verkleinerten Bildern geschätzt.

Eigener Fund beim Nachsehen: das Logo im Fuß war in die Breite gezogen; behoben.

## Überarbeitung Runde 8 (Auftrag 13./14.11.)

1. **Seitenstreifen am nächsten Termin entfernt.** Statt roter Kante und rosa Fläche steht die Zeile zwischen zwei festen
   Tintenlinien (2 px), Datum und Titel in Logo-Rot, darunter „als Nächstes“. Auch die senkrechte Achse der Zeitleiste
   am Handy ist weg; die Feste stehen dort als Liste mit Haarlinien.
2. **Fließtext jetzt Grotesk.** Newsreader ist raus (Schriftdateien gelöscht), Hanken Grotesk setzt Köpfe und Text,
   damals noch IBM Plex Mono für die Ziffern (nach Kritik r1 ebenfalls entfernt); damit fällt die letzte Gemeinsamkeit mit Runde 2 (Serifen-Fließtext) weg.
3. **Papier heller.** Grund `oklch(95.5% 0.008 245)` statt 84 %, Bogen `oklch(99% 0.003 245)`, Haarlinie 84 %;
   Kontraste: Tinte auf Grund 17:1, Grau (`muted`) 6,2:1, Rot 5,6:1, Weiß auf Rot 6,2:1. Kursiv ist gestrichen
   (Hanken ohne Kursivschnitt).
4. **Links auf echte Beiträge.** Alle 20 Zeilen im Jahr-Index, die Feste mit Bericht in der Zeitleiste (Aarau, Leuk,
   Glattbrugg, Hamm, Vaani Vizha, Deepavali), „Bride of Aravan“ und „Sardar 2“ im Kinojahr, die Anschlusslinks im
   Artikel und Knöpfe „Beitrag lesen“ bei Hamm, Glattbrugg und Koovagam. Ohne Bericht (Thai Pongal, Kalaiththiran,
   Neujahr, Kevelaer, THADAM, Basel) bleibt es ohne Link.

Dazu: Navigation mit Community und Verzeichnis (am Handy als zweite Zeile unter dem Logo), Fuß mit Spalte
„Mitmachen“, „Diese Woche im Kino“ heißt „Spielorte ab 9. November“ (kein „Diese Woche“ mehr).

## Überarbeitung nach Kritik r1 (`design/kritik/hm-almanac-r1.md`)

**P1**
1. **IBM Plex Mono entfernt.** Die Schriftdateien sind gelöscht. Alle Ziffern stehen in Hanken Grotesk mit
   `font-variant-numeric: tabular-nums lining-nums`.
2. **Baukasten-Hülle entfernt.**
   - Der Werbesatz mit Knopfpaar auf der Startseite ist weg. Kopf ist jetzt „Die nächsten Feste der Community“ über
     dem Kalenderblatt.
   - Alle „Beitrag lesen“-Knöpfe sind entfallen; der Titel ist der Link.
   - Teilen ist überall ein schlichter Link.
   - Die Seitenköpfe von Termine, Kino und Verzeichnis haben keinen Knopf mehr. Der gefüllte Knopf ist Tinte statt
     Rot und steht nur noch bei „Platz buchen“ und an den Formularen.
3. **Kein dunkler Block mehr.** Kino steht auf der Startseite und auf `kino.html` (Kinojahr) als heller Bogen, durch
   eine Linie getrennt. Auch die Leiste „Rückblick 2026“ ist hell (P3-1).
4. **`kino.html` nach Stadt.**
   - Hauptliste: Städte nach Land und Alphabet, je mit Film. Für Kloten sind Kino und Termin genannt.
   - Darunter steht die Ansicht nach Film.
   - Fehlende Kinonamen und die übrigen Orte von „Scene“ und „OM“ nennt eine Zeile unter dem Bogen. Erfunden ist
     nichts.
5. **Ein Abstand für den ersten Bildschirm.**
   - Der Abstand Kopf → erster Block ist das Token `--space-head-after` (40 px) auf allen Seitentypen.
   - Auf der Startseite steht die Überschrift über dem Blatt.
   - Schlagzeilen: höchstens 44 px am Desktop, 32 px am Handy (`--text-display`); Abschnittsköpfe bis 38 px.

**P2 (soweit im Rahmen)**
- Tippflächen: Links in Tabellen, Zeitleiste, Jahr-Index und Bildnachweisen haben 44 px Trefferhöhe, ohne den Satz zu
  verschieben.
- Bild im ersten Bildschirm: auf der Startseite bei 1280 der Deepavali-Bericht mit Foto neben dem Blatt. Am Handy
  folgt das Foto direkt unter dem Blatt.
- Rot nicht mehr als Fläche (P2-4).
- Bildnachweis an jedem Bild: Startseite, Termine, Kino, Rubrik und Profil, zusätzlich zum Fuß.
- Erklärtexte im Formular und in der Buchung in 18 px.
- Kinozahlen in Lesegröße.
- Reiter des Jahr-Index brechen am Handy um.

**Nicht behoben:**
- P2-2 am Handy: Das Foto steht unter dem Blatt.
- P3-2: Ortszeile unter Berichten.
- P3-4: Schrittleiste der Buchung.
- P3-5: Datumsfeld in der Sprache des Browsers.
- P3-6: Vorschau der Einsendung.
- P3-7: Gedankenstrich im Originaltext von Beitrag 71; der Wortlaut des Beitrags bleibt.

**Prüfung danach:**
- `sloplint --genre editorial` über http und Dateien für alle Seitentypen und alle 20 Artikel: 0 FAIL, 0 offene
  REFLEX, 0 offene WARN.
- Neu verzichtet: 78 auf Start, Termine, Kino und Artikel (Abschnittsköpfe eine Stufe unter dem auf 44 px gedeckelten
  Seitenkopf), 44c auf der Startseite (Blatt als Kopf, Foto daneben), 59 und 49b auf Kino.
- Dismissed: 58 auf Kino (84 Wörter im Kinojahr).
- `tools/shots.mjs`: 48 Aufnahmen (16 Seiten × 390/820/1280), 0 Fehler.

## Schliff nach r2 (`design/kritik/hm-almanac-r2.md`)

- **Bild im ersten Handy-Bildschirm (P2-1).** Alle fünf Hauptseiten zeigen bei 390 ein echtes Foto mit Nachweis direkt
  unter dem Kopf; am Desktop steht es rechts neben dem Kopf.
  - Start: der Deepavali-Bericht steht am Handy vor dem Bogen.
  - Termine: Sivan Kovil Glattbrugg.
  - Kino: Karthi, der Darsteller in „Sardar 2“.
  - Verzeichnis: der Tempel in Hamm.
  - Werben: das Koothandavar-Fest.
- **Kino (P2-2).** Die leere Spalte ist weg. Die Orte von „Scene“ stehen in einer Zeile; „6 weitere Städte“ und
  „OM, 12 Spielorte“ tragen den Platzhalter „Orte folgen“. Die doppelte Ansicht nach Film entfällt, geteilt wird je
  Zeile.
- **Fuß (P2-3).** Verlinkt sind nur Rubriken mit eigener Seite (Community, Events, Kino), dazu der Platzhalter
  „weitere folgen“.
- **Tippflächen (P2-4).** Weiterlesen-Links, Rubrik-Link im Artikelkopf und Dateifeld haben jetzt 44 bzw. 48 px.
- **Schriftgröße (P2-5).** Erklärende Notizen unter den Bögen in 18 px; 15 px bleiben für Tabellenköpfe, Stand und
  Nachweise. Die leeren Zellen in `buchen.html` sind die Kalenderfelder vor dem Monatsersten und nach dem Monatsende.
- **P3.**
  - THADAM: „Veranstalter nicht genannt“.
  - Kalaiththiran: „drei Städte“.
  - Unterzeile des Festjahrs: „aus Rückblick und Radar“.
  - Abstände auf Start und Termine: `--section-gap-s`.
  - Die doppelte Seitenführung in der Rubrik ist entfernt.
- **Buchhaltung (P3-4).**
  - `job` je Seite: read, find, attend, buy.
  - Die Abweisung zu Gate 52 ist gestrichen.
  - `almanac.css` hat die Zeile mit der Selbstkritik.
  - Die Ausnahmen, die überall gelten (44c, 59, 78, 49b), stehen als Hausstil in `design.md`.
- **Offen:**
  - Das Foto auf der Startseite zeigt den Tempel vom Juni, kein Deepavali (P3-7).
  - THADAM, „OM“ und „Jailer 2“ sind wartende Radar-Entwürfe (P3-3).
  - Schrittleiste, Datumsformat und Vorschau der Einsendung (P3-9) sind unverändert.

## Abgrenzung

- **Gegen Runde 2** (Sand, Braungrau, Serife, runde Bilder): heller kühler Grund statt Creme (Farbton 245, nicht 60–90), blauschwarze Tinte statt Braungrau, eckige Bilder, Grotesk für Köpfe und Text.
- **Gegen Runde 4** (rote Riesenschrift, Stempel, Schräglagen): Rot nur als eine Zeile und ein Knopf, keine Schräglage, keine Versalien. Das gezogene Manifesto wurde genau deshalb getauscht.
- **Gegen die Nachrichtenportal-Muster:**
  - keine Dachzeilen; die Rubrik steht im Byline-`<dl>`
  - keine Versal-Labels, keine „·“-Metazeilen
  - kein Kartenraster, keine Bildkachel mit Verlauf
  - Kino und Termine als nüchterne, datierte Liste

## Materialfrage (was die Seite am meisten verbessern würde)

Eigene Fotos von tamil.de vom Lichterfest 2026 oder einem Tempelfest, im Querformat. Alle Bilder sind heute Commons-Symbol- oder Archivbilder. Slots mit Größe:
- `aufmacher` 4:3, 640 × 480
- `hamm` 4:5, 640 × 800
- `artikel` 21:9, 1090 × 470
- `glattbrugg` 4:3, 750 × 560
- `koovagam` 4:3, 750 × 560

Danach: die Kinonamen zu „Scene“ und „OM“ und eine Uhrzeit je Termin.

## Offene Punkte und eigene Schwächen

- Formular-, Verzeichnis- und Werbeseiten öffnen mit einem reinen Titelkopf; Hallmark will dort Bild oder Bogen im ersten Bildschirm, verzichtet ist auf dem Protokoll (44c, 59).
- Das Verzeichnis hat nur ein Profil (Ceylon Palace); die anderen elf Namen verweisen auf ihren Bericht, nicht auf ein Profil.
- „Premium“ am Ceylon Palace ist ein gekennzeichnetes Muster, keine Tatsache.
- Preise, Bedingungen, Einwilligungstext, Redaktionsadresse und WhatsApp-Nummer sind Platzhalter („folgt“), die Zahlung ist gesperrt.
- Die Buchung zeigt eine Beispielauswahl (Leaderboard, 23. bis 29.11.); belegte Tage gibt es noch nicht, gesperrt ist nur der Vorlauf.
- Datums- und Dateifelder zeigt der Browser in seiner eigenen Sprache (in der Aufnahme englisch).
- Die Werbeplätze erscheinen auf den Seiten selbst noch nicht; nur die Preisliste nennt sie.
- Keine Finish-Prüfung aus frischem Kontext für die neuen Seiten in dieser Runde.
- Inhalte sind großenteils unfreigegebene Entwürfe; „OM“, „Jailer 2“ und THADAM stammen aus wartenden Radar-Entwürfen vom 12.11.
- Der Altbestand 2024 ist bewusst nicht genutzt (er würde eine Seite von 2026 alt aussehen lassen, die Bilder sind Screenshots und Werbegrafiken).
- Impressum und Datenschutz stehen als sichtbare Platzhalter da.
- Die WhatsApp-Links tragen nur den Text; die Live-URL hängt WordPress an.
- Das Bild rb-30 ist dasselbe Foto wie bei Story 49.
- Kleine Tippflächen bleiben bei Textlinks in Zeilen und bei den Bildnachweisen (Hinweise von `shots.mjs`, keine Fehler).
- Ablauf: Die Hero-Prüfung lief, während die übrigen Abschnitte schon standen (Zeitdruck). Der erste Reviewer-Versuch scheiterte am Modell-Limit, der zweite lief mit Sonnet.
