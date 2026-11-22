# Plan: tamil.de mit Hallmark, Theme Almanac (hm-almanac)

Stand 13.11.2026, 20:30 Berlin. Abgabe 22:10. Arbeitsordner `/home/user/Tamil/design/richtungen/hm-almanac/` (existiert noch nicht). Kein Git, nichts außerhalb des Ordners ändern. Wegen Plan-Modus ist bisher nur gelesen worden (einzige Ausnahme: ein Kontaktbogen der Bilder in `scratchpad/hm-plan/kontakt.jpg`, temporär).

## 0. Befunde aus der Vorbereitung (gelesen, belegt)

- **Pre-flight:** `/home/user/Tamil/DESIGN.md` existiert, ist aber ausdrücklich „abgelehnt, gilt nicht für neue Gestaltung“ → kein gesperrtes System. Kein Framework, statisches HTML. Logo `logo.png` 300×121, transparent, Rot `rgb(181,40,42)` = `oklch(50.8% 0.177 25.6)`, Grau `rgb(60,60,60)`.
- **Draw** (lesend gelaufen, reproduzierbar mit `--seed 26f3b5`): `--material words --job read` (read → listen) `--theme almanac`, Log leer:
  shape **Manifesto** · hero **Ledge** · nav **banner over a retracting bar** · footer **index columns** · weglassen: **Statement, Steps** · Hero führt mit **Datum und Ort** · Abschnitte: Live-Foto, „record as Index“, „earlier work as covers in a Rail“ · Schluss: „more of the catalogue“.
- **Tausch (im Picks-Block benennen):** Shape Manifesto → eigener Name **„Kalenderblatt“** (Manifesto = Versal-Plakatschrift, schräg, „verkauft Zustimmung“: genau Runde 4 „laut, Schräglagen, Riesenschrift“; Job ist lesen/finden). Rail aus Bildkacheln → **Kino auf dem Tintenband** (eine Reihe gleich großer Bildkacheln ist das abgelehnte Kartenraster; der Altbestand 2024 besteht aus Screenshots/Werbegrafiken). Alles andere aus dem Draw bleibt.
- **Logo-Rot vs. Magenta (bewusst gelöst):** Almanacs Akzent wird auf den Farbton des Logos umgestimmt, Rolle und Haltung bleiben (Restrained, < 5 %, eine Zeile, der Füllknopf, Link-Unterstreichungen). Begründung: 350° neben 25.6° liegen 35° auseinander und lesen sich nebeneinander wie ein Druckfehler; auf tamil.de ist das Rot des Kopfs die eine Signalfarbe. Tokens (als `:root`-Block oben in `almanac.css`):
  `--color-accent: oklch(50.8% 0.177 25.6)` (= Logo) · `--color-accent-2: oklch(42% 0.160 25.6)` (Hover, roter Text auf Schiefer) · `--color-focus: oklch(48% 0.19 25.6)` · `--color-accent-ink` bleibt `oklch(97% 0.006 245)`. Roter Text nur auf `--color-sheet` (≈ 5,3:1), auf `--color-paper` nur `accent-2`.
- **Material** (nur das): `rueckblick.json` (20 Beiträge, Bilder rb-*.jpg, Nachweise), `inhalte.json` (Kino: „Scene“ 11 Kinos: Berlin, Bremen, Chemnitz, Dortmund, Düsseldorf + 6 weitere Städte; „Ramayana: Rise of a Legend“ 2 Kinos: Gütersloh, Ravensburg; Termin: Diwali in Basel, Basel Tamil Sangam, Sa 21.11.2026, Aula Lysbüchel, „Mitglieder erhalten Tickets günstiger.“), `rueckblick-2026.md` (Titel + Daten, u. a. Entwurf 54 „„OM“ im Kino: 12 Spielorte in Deutschland“, Entwurf 5 „„Jailer 2“ am 15. November zum Spezialpreis im Kino Claudia in Kloten“, Entwurf 4 „THADAM 2026 … am 13. Dezember in Bern“). Deepavali-Text nennt Düsseldorf Tamil Sangam So 15.11. und Sivaalayam München 8.11. Wochentage geprüft (15.11. So, 21.11. Sa, 13.12. So). Nicht verwenden: `prototyp/` (nicht freigegeben im Auftrag), Story-31-Angaben zu Suriya (Recherche nötig), Pongal-2027-Datum (nicht im Material → weglassen).
- **Werkzeuge:** Kein puppeteer-core vorhanden → in `scratchpad/hm-pptr` `npm i puppeteer-core@24`, dann `HALLMARK_PUPPETEER=<dir> CHROME_PATH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome`. `shots.mjs` nutzt Playwright (vorhanden). Kein Agent-Werkzeug in dieser Sitzung → frischer Kontext für Reviews über `claude -p` (CLI 2.1.323 vorhanden); scheitert das, in-thread und so protokollieren.
- **sloplint-Fakten:** Gate 58 FAIL ab > 95 Wörtern je 900-px-Fenster (WARN 81–95; Wörter mit Umlaut zählen oft nicht, Ziffern nie). `copy: verbatim` im Stempel macht 19/58/69 zu NOTE → nur in `artikel.css` (Artikeltext ist wörtliches Material). Stempeltext = erste 40 Zeilen jeder verlinkten CSS; Hero-Haltung = erster Treffer → jede Seite bekommt eigene Seiten-CSS mit eigenem Stempel, die `almanac.css` importiert. Render-Shots landen in `hm-almanac/.hallmark/shots/`.
- **Projektregeln beachten:** Fließtext Handy 18 px (Regel `design.md` sagt 18, Brief 17 → 18 erfüllt beides), Tippflächen 44 px, keine Dachzeilen/Versalien/„·“-Zeilen/Kartenraster/Verlaufskacheln. Risiko offen benennen: Newsreader-Serife im Fließtext steht in der Liste von Runde 2; hier auf kühlem Schiefer mit Grotesk-Köpfen und Mono-Ziffern, Tausch wäre eine Token-Zeile (`--font-body`).

## 1. Einrichten (≈ 8 min)

```
D=/home/user/Tamil/design/richtungen/hm-almanac; H=/home/user/hkgrowthoperator/hallmark/skills/hallmark; S=/tmp/claude-0/-home-user/328bcd38-019d-5546-955b-7fea86a20fa1/scratchpad
mkdir -p $D/.hallmark $D/bilder $D/schriften && cd $D
node $H/scripts/theme.mjs draw --material words --job read --theme almanac --log .hallmark/log.json --seed 26f3b5
node $H/scripts/theme.mjs scaffold almanac --dealt "2/3, seed tamil-deutschsprachiges-online-magazin-der-ff32·6bcf19c0·2026-11-13·r0" --dir .
cp /home/user/Tamil/design/inhalte/logo.png bilder/; cp /home/user/Tamil/design/inhalte/rueckblick/bilder/{rb-30,rb-71,rb-76,rb-43}.jpg bilder/
cp /home/user/Tamil/design/richtungen/bild/schriften/{hanken-grotesk-latin-wght-normal.woff2,OFL.txt} schriften/
# Newsreader (opsz+wght, normal+italic) und IBM Plex Mono 400/500 latin, Version per `npm view` fest pinnen, von cdn.jsdelivr.net/npm/@fontsource(-variable)/…/files/
mkdir -p $S/hm-pptr && cd $S/hm-pptr && npm init -y >/dev/null && npm i puppeteer-core@24 --no-audit --no-fund
```
`.hallmark/preflight.json` schreiben (Befund oben). Bilder in `bilder/` mit width/height aus PIL.

## 2. Picks-Block (wird in `begruendung.md` übernommen, Sweep-Zeile am Ende gefüllt)

- **Shape** · Kalenderblatt (eigener Name; gezogenes Manifesto getauscht, s. o.), aus Draw 26f3b5 · genre editorial · job: listen (lesen) – Lesen im Aufmacher, die Daten im Hero daneben
- **Theme** · Almanac, dealt 2/3 (Schieferpapier, Bogen, Hanken Grotesk über Newsreader, Plex-Mono-Ziffern, zwei Linienstärken) · Akzent auf Logo-Rot umgestimmt
- **Chrome** · nav: Band über einer einfahrenden Leiste (Tintenband: „Rückblick 2026: das Jahr der Community in zwanzig Berichten“ → #jahr; Leiste: Logo, Termine, Kino, Rückblick) · footer: Indexspalten (Logo + Satz, Dienste, Rubriken, Bildnachweise, Rechtliches)
- **Hero** · Startseite Ledge (Bogen oben über 12 Spalten, Kopf auf der Grundlinie) · Termine Index · Kino Banner · Artikel Banner
- **Signature** · das Kalenderblatt: die nächsten Feste als gedruckter Bogen, Datum in Mono, die nächste Zeile (So 15.11., Düsseldorf) in Logo-Rot
- **Sections** (Start) · Ledge-Hero (Bogen) · Split 6/6 Aufmacher Deepavali (Foto) · Tintenband Kino · Split 7/5 Hamm-Uentrop (Foto rechts) · Jahr-Index als Switcher nach Quartal · Footer
- **Material** · real: 20 Rückblick-Beiträge, Termine Düsseldorf/Basel/Bern, Kino Scene/Ramayana/OM/Jailer 2, Logo · pictures: Commons-Bilder der Beiträge (rb-30, rb-71, rb-76, rb-43), Behandlung muted · absent: Uhrzeiten, Preise, Kino-Namen zu Scene/OM, Pongal-2027-Datum, Impressum-Inhalte
- **Sweep** · nach dem Bau

Stempel (Startseite, `index.css` Zeile 1–3), analog je Seite mit eigener `hero:`:
```
/* Hallmark · shape: Kalenderblatt · genre: editorial · theme: Almanac (deal 2/3, seed tamil-…·r0) · job: listen · draw: 26f3b5
 * hero: ledge · nav: banner over a retracting bar · footer: index columns · imagery: photographs, Commons pictures of the posts 2, muted · signature: das Kalenderblatt, nächster Termin in Logo-Rot
 * axes: <aus scaffold> · posture: restrained · contrast: pass · fold: pass · v2.0.0 */
/* Hallmark · pre-emit critique: P4 H4 E4 S4 R4 V5 · weakest: <beim Bau ehrlich füllen> */
```
Fingerprint fürs Log: `Bottom-aligned|Asymmetric spans|Hairline|Solid|Tightly cropped to the grid|None`.

## 3. Dateien

`tokens.css`, `base.css` (Scaffold) · `almanac.css` (Stempel, Imports, @font-face, `:root`-Marke + `--text-md: 1.125rem`, Nav, Footer, `.sheet`, `.btn`, `.photo`, `.band--ink`, Tabellen, Responsive) · `index.css`, `termine.css`, `kino.css`, `artikel.css` (je Stempel → `@import url("./almanac.css")` → Seitenregeln) · `site.js` (Leiste einfahren: passiver rAF-Scroll, `transform` only, `:focus-within` zeigt; Switcher-Tabs mit Pfeiltasten; ohne Script alle Panels sichtbar, Tabliste `hidden` bis JS) · Slot-Script des Scaffolds vor `</body>` · `bilder/`, `schriften/`, `begruendung.md`, `shots/`.
Pflicht je Seite: `lang="de"`, `<title>`, Meta-Description, Skip-Link, `:focus-visible` instant, 8 Zustände an Knöpfen, `overflow-x: clip`, `minmax(0,1fr)`, keine Halbgeviertstriche (auch „19. bis 30. Juni“), keine „·“, keine Versalien, keine Dachzeilen (Rubrik steht im Byline-`<dl>` hinter dem Titel), ein gefüllter Knopf je Seite, WhatsApp = `<a href="https://wa.me/?text=…">Per WhatsApp teilen</a>` (Text + Hinweis in der Übergabe, dass WordPress die URL anhängt).

## 4. Seiten (Inhalte festgelegt)

**Bausteine:** `.sheet` = Bogen in `--color-sheet`, 2-px-Tintenlinie oben, Kopfzeile (Titel links, `<time>Stand …</time>` rechts), `thead` mit 2-px-Linie, Zeilen mit Haarlinie, Datum `Wochentag` Newsreader + `15.11.` Plex Mono, eine Zeile `.is-next` rot (Text accent, Grund 8 % accent auf sheet), vergangene Zeilen muted; unter 40rem Zeilen als beschriftete Blöcke. Fotos: `<figure><div class="photo" data-slot="…" data-alt="…"><img …></div><figcaption>Faktum</figcaption></figure>`, eckig, Inset-Outline, Nachweis im Fuß (`[data-credits]`), im Artikel zusätzlich in der Bildunterschrift.

**index.html** (Ledge, 6 Abschnitte inkl. Footer, ≤ 450 Wörter)
1. Hero Ledge: oben Bogen „November und Dezember 2026“ / Stand Freitag, 13. November; Spalten Tag | Was | Wer | Wo; Zeilen: So 08.11. Deepavali, das Lichterfest | Sivaalayam-Tempel | München (vergangen) · **So 15.11. Deepavali-Feier | Düsseldorf Tamil Sangam | Düsseldorf (rot)** · So 15.11. „Jailer 2“, Sondervorstellung | Kino Claudia | Kloten · Sa 21.11. Diwali in Basel | Basel Tamil Sangam | Aula Lysbüchel, Basel · So 13.12. THADAM 2026, Networking- und Gala-Nacht | – leer – | Bern. Unten auf der Grundlinie: h1 „Deepavali ist vorbei. Gefeiert wird weiter.“ (Spalten 1–8), rechts unten Satz „Tempelfeste, Vereinsabende und tamilisches Kino in Deutschland, Österreich und der Schweiz.“ + [Alle Termine] (rot gefüllt) + [Kinoprogramm] (Haarlinie). DOM: Kopf zuerst, Desktop per Grid Bogen oben. Fold 1280×800 rechnen: Band 40 + Leiste 72 + Bogen ≈ 400 + h1 2 Zeilen ≈ 155.
2. Aufmacher Split 6/6: rb-30 4:3 links (lazy), rechts h2 Deepavali-Titel, Teaser, `<time>8. November 2026</time>` + Orte, [Beitrag lesen → artikel.html], Per WhatsApp teilen.
3. Tintenband „Im Kino, Stand 9. November“: Scene (Orte, Ziffer 11 Kinos in Mono groß), OM (12 Spielorte), Ramayana (Gütersloh, Ravensburg, 2 Kinos), Jailer 2 (So 15.11., Kino Claudia, Kloten); Link „Alle Spielorte“ → kino.html. Mono in Sheet-Farbe, Spaltenköpfe paper-2 (Rot auf Tinte besteht 3:1 nicht).
4. Split 5 Text / 7 Foto? → Foto rechts 5 Spalten 4:5 (rb-71 Gopuram), links h2 Steinmeier-Titel, Teaser, `<time>26. Juli 2026</time>`, Hamm, Teilen.
5. Jahr-Index `id="jahr"`: Kopf (Sp. 1–4) „Das Jahr 2026 in Berichten“ + Zeile „Zwanzig Beiträge aus dem Rückblick der Redaktion.“; rechts (5–12) Tabs Okt./Nov. (Standard, 2) · Juli bis Sept. (8) · April bis Juni (7) · Jan. bis März (3); Zeilen Datum Mono | Titel | Ort; nur Deepavali verlinkt. 2-px-Linie über dem Abschnitt, Abstand 176.
6. Footer Indexspalten: Logo + „Das Online-Magazin der tamilischen Community in Deutschland, Österreich und der Schweiz.“ · Dienste (Festkalender, Kino, Rückblick 2026) · Rubriken (Nachrichten, Community, Kultur, Events → termine, Kino → kino, Küche, Sport; ohne Zielseite → #jahr) · Bildnachweise `data-credits` (Nachweis + Link quelle_bild + Lizenzlink) · Rechtliches: zwei Platzhalter `.fill` „Impressum folgt“, „Datenschutz folgt“, „© 2026 tamil.de, KBS Digitalmedia“.

**termine.html** (Hero Index)
1. h1 „Wann und wo gefeiert wird.“, Satz „Tempelfeste, Deepavali, Pongal und Vereinsabende in Deutschland, Österreich und der Schweiz.“, [Kalender per WhatsApp teilen] rot. Darunter als Hauptinhalt der Bogen Nov./Dez. (4 Fest-Zeilen wie oben ohne Kino, Basel mit Satz „Mitglieder erhalten Tickets günstiger.“, `id="basel"`), je Zeile Link „Teilen“ (44 px), Fußnote kursiv „Nach Ankündigungen der Vereine und Tempel, Stand 13. November 2026.“
2. „Das Festjahr 2026“ als ein Diagramm, groß (Almanac Range): Zeitachse über 12 Monatsspalten, 2-px-Achse, Monatskürzel klein, 11 Ereignisse abwechselnd oben/unten (Datum Mono / Name / Ort, max. 8rem): 14.01. Thai Pongal, Bern · 07.02. Kalaiththiran, Göttingen u. a. · 21.03. 30 Jahre Tamilschule, Aarau · 14.04. Tamilisches Neujahr, Glattbrugg · 17.05. Lourdes-Fest, Leuk · 27.06. Wagenfest, Glattbrugg · 26.07. Tempelfest, Hamm · 08.08. Wallfahrt, Kevelaer · 22.10. Vaani Vizha, Tamilalayams · 08.11. Deepavali (→ artikel.html) · 13.12. THADAM, Bern (gestrichelt, kommend); rote Linie „heute, 13.11.“. `<ol aria-label>` semantisch; Spalte per `grid-column: var(--m)`, Position `calc((var(--d) - 1) / 31 * 100%)`, Nov./Dez.-Etiketten rechtsbündig; unter 64rem senkrechte Liste mit Linie links. Zeile darüber: „Elf Feste aus dem Rückblick, vom Thai Pongal in Bern bis THADAM in Bern.“
3. Split Foto rb-76 (7 Sp., 4:3) + Mahotsavam-Titel, Teaser, `<time>`19. bis 30. Juni 2026, Wagenfest 27. Juni, Teilen.
4. Footer.

**kino.html** (Hero Banner)
1. h1 „Welcher tamilische Film wo läuft.“, Satz „Spielorte in Deutschland und der Schweiz, Stand 9. November 2026.“, [Kinoliste per WhatsApp teilen] rot.
2. h2 „Diese Woche im Kino“ + Index der 4 Filme (h3 Titel, Orte, große Mono-Ziffer rechts mit Einheit: 11 Kinos / 12 Spielorte / 2 Kinos / So 15.11.), erste Zeile größer, je „Teilen“; Quellnotiz (Radar 9.11.; OM und Jailer 2 aus Entwürfen).
3. Tintenband „Das Kinojahr 2026“: 8 Zeilen Datum | Film | Ort (Parasakthi 10.01., With Love/Gatta Kusthi 2 06.02., Members of the Problematic Family 16.02. Berlin, First Take 11.04. Bern, Mayilaa 23.04. Köln, Karuppu 14.05. Viernheim/Wien/Berlin, Bride of Aravan 25.07. Stuttgart, Sardar 2 10.09. Deutschland).
4. Split Text links 5 / Foto rechts 7: rb-43 Koovagam + Titel, Teaser, 25. Juli 2026 Stuttgart, Teilen.
5. Footer.

**artikel.html** (Hero Banner, `copy: verbatim`)
1. Kopf Sp. 1–10: h1 Deepavali-Titel (display-s, max 32ch, 2 Zeilen), Teaser als Lead, rechts `<dl>` Datum 8. November 2026 / Orte / Rubrik Events, Textlink „Per WhatsApp teilen“.
2. Bild über 10 Spalten 16:9 (rb-30, fetchpriority high), figcaption: Alt-Satz + „Foto: 18quirl08 / Wikimedia Commons, CC BY-SA 4.0“ verlinkt.
3. Text Sp. 1–7, 65ch, 19 px/18 px Handy, Zeilenhöhe 1,7, vier Absätze wörtlich; Marginalie Sp. 9–12: Bogen „Im Beitrag genannt“ (So 08.11. Deepavali / So 08.11. Sivaalayam-Tempel, München / Sri Ganesha Hindu Temple, Berlin: Lakshmi Pooja, ohne Datum / **So 15.11. Düsseldorf Tamil Sangam (rot)**) + Link „Alle Termine im Festkalender“ + [Per WhatsApp teilen] rot gefüllt.
4. „Weiter im Rückblick“ Rows (3): 07.06. Berlin Tempel geweiht (→ index#jahr), 22.10. Vaani Vizha (→ index#jahr), 21.11. Diwali in Basel (→ termine#basel).
5. Footer.

## 5. Ablauf, Prüfungen, Zeitplan (Berlin)

- 20:40–20:55 Einrichten, `almanac.css` + Nav + Index-Hero. `sloplint index.html --genre editorial --render --stage hero` (mit HALLMARK_PUPPETEER/CHROME_PATH) bis 0 FAIL.
- 20:55–21:00 Hero-Review frisch: `claude -p --add-dir $H/references --add-dir $D --allowedTools Read "Read $H/references/review-hero.md and follow it. Inputs: <4 hero-*-PNGs>, stamp lines 1–2 (zitiert), Picks Material + Signature (zitiert), $H/references/themes/almanac.jpg"` → `.hallmark/hero-review.txt`; Befunde einarbeiten, Stempel `hero-review: …`.
- 21:00–21:35 übrige Abschnitte und drei Seiten.
- 21:35–21:45 `sloplint index.html artikel.html termine.html kino.html --genre editorial --render` bis 0 FAIL, REFLEX beheben oder begründet verzichten; `gates.md` § 5 J-Gates durchgehen.
- 21:45–21:55 Finish-Review frisch (`review-finish.md`, Render-Shots, HTML/CSS-Pfade, Theme-Datei + Bild, Hero-Befunde mit Erledigung, `gates.md` § 4), erstes Wort befolgen, Fixes, Recapture, selbst bewerten.
- 21:55–22:05 `theme.mjs log --entry …` (Felder shape, theme, axes, hero, nav, footer, imagery, photos, entry, fingerprint, sections, signature, waived, prompt), `begruendung.md` (Picks-Block mit Outcome-Zeile, Materialfrage, offene Punkte), `cd /home/user/Tamil && node tools/shots.mjs design/richtungen/hm-almanac/{index,artikel,termine,kino}.html --out design/richtungen/hm-almanac/shots` (0 Überlauf, 0 Konsolenfehler).
- 22:05–22:10 Bericht.
Wenn die Zeit knapp wird: zuerst die Timeline-Spielerei vereinfachen (senkrechte Liste auch am Desktop), nie die Prüfungen streichen.

## 6. Offene Punkte (für den Bericht vorgemerkt)
Newsreader-Fließtext vs. Runde 2; Inhalte großteils unfreigegebene Entwürfe; Kino-Namen/Uhrzeiten fehlen; Altbestand 2024 bewusst nicht genutzt; Impressum/Datenschutz als Platzhalter; WhatsApp-Links ohne Live-URL; Bild rb-30 ist identisch mit rb-49.
