# hm-almanac – Begründung

Probe nach `design/brief-v3.md`, gebaut mit Hallmark v2.0.0, Theme Almanac (gedealt 2/3). Seiten: `index.html`,
`artikel.html`, `termine.html`, `kino.html`. Statisches HTML/CSS, Schriften selbst gehostet (`schriften/`, OFL),
Bilder als Kopien in `bilder/`.

## Hallmark-Picks

**Hallmark · v2.0.0**

- **Shape** · Kalenderblatt (eigener Name), aus Draw `26f3b5` · genre editorial · job: listen (lesen): Lesen im Aufmacher, die Daten im Hero direkt daneben. Gezogen war Manifesto; getauscht, weil Manifesto mit großer, schräger Versalschrift Zustimmung verkauft, also genau das, was in Runde 4 als „laut, Baukasten“ abgelehnt wurde. Der Job ist lesen und finden.
- **Theme** · Almanac, dealt 2/3 (Seed `tamil-deutschsprachiges-online-magazin-der-ff32·6bcf19c0·2026-11-13·r0`): Schieferpapier, heller gedruckter Bogen, Hanken Grotesk über Newsreader, Ziffern in IBM Plex Mono, zwei Linienstärken, eckig. **Akzent auf das Logo-Rot umgestimmt** (`oklch(50.8% 0.177 25.6)`, gemessen aus `logo.png`); Almanacs Magenta (Farbton 350) läge nur 35° daneben und würde sich wie ein Druckfehler lesen. Rolle und Haltung bleiben: restrained, unter 5 %, eine Zeile, der gefüllte Knopf, die Unterstreichungen.
- **Chrome** · nav: Tintenband „Rückblick 2026 in zwanzig Berichten“ über einer Leiste, die beim Abwärtslesen einfährt (Logo unverändert, Termine, Kino, Rückblick) · footer: Indexspalten (Logo, Dienste, Rubriken, Bildnachweise, Rechtliches).
- **Hero** · Startseite Ledge: der Bogen oben über 12 Spalten, Kopf „Deepavali ist vorbei. Gefeiert wird weiter.“ auf der Grundlinie, Satz und Aktionen rechts daneben · Termine Index · Kino und Artikel Banner.
- **Signature** · das Kalenderblatt: die nächsten Feste als gedruckter Bogen, Datum in Mono, die nächste Zeile (So 15.11., Düsseldorf Tamil Sangam) in Logo-Rot. Auf `termine.html` zusätzlich das Festjahr 2026 als ein großes Diagramm mit elf Festen und dem heutigen Tag als roter Linie.
- **Sections** · Startseite: Ledge-Hero (Bogen) · Split 6/6 Aufmacher Deepavali · Tintenband Kino · Split 6/6 Hamm-Uentrop, Foto rechts · Jahr-Index mit Reitern · Footer. Termine: Bogen November/Dezember · Festjahr-Diagramm · Split Glattbrugg · Footer. Kino: Filmliste mit großen Mono-Ziffern · Tintenband Kinojahr 2026 · Split Koovagam · Footer. Artikel: Kopf mit Bild über zehn Spalten · Text mit Randbogen „Im Beitrag genannt“ · drei Anschlusslinks · Footer. Weggelassen laut Draw: Statement, Steps. Getauscht: die Bild-Rail (Bildkachelreihe = abgelehntes Kartenraster) gegen das Kino-Tintenband.
- **Material** · real: 20 Rückblick-Beiträge 2026 (`rueckblick.json`), Termine Deepavali München 8.11., Düsseldorf Tamil Sangam 15.11., Diwali in Basel 21.11., THADAM Bern 13.12., Kino „Scene“ (11 Kinos), „Ramayana: Rise of a Legend“ (Gütersloh, Ravensburg), „OM“ (12 Spielorte), „Jailer 2“ (Kino Claudia, Kloten, 15.11.), Kinojahr und Festjahr aus `rueckblick-2026.md`, das Logo · pictures: die Commons-Bilder der Beiträge rb-30, rb-71, rb-76, rb-43, Behandlung muted, Nachweis im Fuß und im Artikel unter dem Bild · absent: Uhrzeiten, Preise, Kinonamen zu „Scene“ und „OM“, Datum Thai Pongal 2027, Impressum und Datenschutz.
- **Sweep** · Floor 0 FAIL · Reflex 0 offen (1 Verzicht: 49b, Berichtstitel als Links brechen am Handy um) · 1 Finish beantwortet (F17, Etiketten der Zeitleiste) · 5 WARN begründet zurückgewiesen (58 Seitenwörter inkl. versteckter Reiter, 58 Fenster 85 und 91 Wörter, 77 auf Termine und Artikel) · hero-review: fix, 5 Befunde, 1 erledigt, 2 teilweise, 2 bewusst belassen · finish-review: Subagent in frischem Kontext (`claude -p`, Sonnet), fix, 8 Befunde, 3 erledigt, 5 teilweise · `tools/shots.mjs`: 12 Aufnahmen, 0 Fehler (kein seitliches Scrollen, keine Konsolenfehler).

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

## Abgrenzung

- **Gegen Runde 2** (Sand, Braungrau, Serife, runde Bilder): kühles Schieferpapier statt Creme, blauschwarze Tinte statt Braungrau, eckige Bilder, Grotesk-Köpfe. Gemeinsam bleibt nur die Serife im Fließtext (Newsreader). Das ist das größte Risiko dieser Probe; ein Tausch wäre eine Zeile (`--font-body`).
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

## Offene Punkte

- Newsreader-Fließtext (s. o.) braucht ein Ja oder Nein von Luis.
- Inhalte sind großenteils unfreigegebene Entwürfe; „OM“, „Jailer 2“ und THADAM stammen aus wartenden Radar-Entwürfen vom 12.11.
- Der Altbestand 2024 ist bewusst nicht genutzt (er würde eine Seite von 2026 alt aussehen lassen, die Bilder sind Screenshots und Werbegrafiken).
- Impressum und Datenschutz stehen als sichtbare Platzhalter da.
- Die WhatsApp-Links tragen nur den Text; die Live-URL hängt WordPress an.
- Das Bild rb-30 ist dasselbe Foto wie bei Story 49.
- Nur der Deepavali-Beitrag hat eine Artikelseite; die übrigen Zeilen im Jahr-Index sind noch keine Links.
- Kleine Tippflächen bleiben bei Textlinks in Zeilen und bei den Bildnachweisen (Hinweise von `shots.mjs`, keine Fehler).
- Ablauf: Die Hero-Prüfung lief, während die übrigen Abschnitte schon standen (Zeitdruck). Der erste Reviewer-Versuch scheiterte am Modell-Limit, der zweite lief mit Sonnet.
