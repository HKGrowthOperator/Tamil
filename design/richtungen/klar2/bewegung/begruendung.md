# klar2 – Bewegung beim Scrollen (Vorschau mit vier Varianten)

Stand 16.11.2026. Auftrag aus Tor G2 (`docs/abnahme/2026-11-16-G2-klar2.md`): Luis will Scroll-Animationen sehen,
„nicht hyperrealistisch und mega geil“, und wählt dann eine. Das Verbot in `design/brief.md` §10.1 („kein Einblenden
beim Scrollen, kein JavaScript“) ist dafür am 16.11. aufgehoben, **nur für Bewegung beim Scrollen**. Alles andere an
klar2 bleibt: Raster, Farben, Schrift, Inhalte, Bildformate, Hover-Zoom.

Öffnen: `index.html` (Standard D). Teilbare Links: `index.html#a`, `#b`, `#c`, `#d`, `#aus`. Die Leiste unten schaltet
um; jedes Umschalten springt nach oben und stellt alles neu auf. Noch einmal auf die aktive Variante tippen spielt sie
von vorn.

## Dateien

| Datei | Inhalt |
|---|---|
| `index.html` | Kopie von `../index.html`, nur Pfade (`../klar2.css`, `../schriften/…`, `../../../inhalte/…`, `../artikel.html`), Titel, zwei Verweise und die Leiste (`hidden`, das Skript gibt sie frei) |
| `bewegung.css` | Leiste, Zustände je Variante, Scroll-Timelines und Ersatzweg |
| `bewegung.js` | Umschalter, Zuteilung der Einheiten, IntersectionObserver, Zeilenteilung, Ersatz-Scroll-Handler; ohne Bibliothek |
| `pruefen.cjs` | Playwright-Prüfung (Endlage, Zeilen, schneller Sprung, Umschalten, Ersatzweg, reduziert) und Einzelbilder |
| `shots/` | `bericht.json` von `tools/shots.mjs`, `frames/*.jpg` (390 × 844, JPEG 70); die großen PNG sind ignoriert |

**Inhalt:** unverändert. Die Seite ist 4095 / 4067 / 3182 px hoch (390 / 820 / 1280), also 4,9 / 4,5 / 3,5
Bildschirme; das reicht. Alle 24 Bilder aus `inhalte/bilder/` stehen schon auf der Seite. Die einzigen weiteren
echten Einträge (`inhalte.json`: 9688, 9678) haben kein Foto und sind in klar2 als Anreißer nicht zulässig. Es gibt
keinen Tamil-Text auf der Seite.

## Für alle Varianten gleich

- **Erster Bildschirm steht sofort.** Was beim Laden (oder nach dem Umschalten) im Bild ist, wird nicht versteckt und
  bewegt sich nicht von selbst. Die Marke erlaubt keine automatisch startende Animation, die Freigabe gilt nur für das
  Scrollen. Bewegung beginnt mit dem ersten Scrollen.
- **Einmal.** Was einmal erschienen ist, bleibt; beim Zurückscrollen wird nichts wieder versteckt. Nur Kopf,
  Leselinie und Aufmacher-Tiefe hängen am Scrollweg und laufen in beide Richtungen.
- **Auslöser:** Oberkante 10 % über dem unteren Bildrand. Was schneller vorbeigescrollt wurde, als es auslösen
  konnte, erscheint trotzdem (der Beobachtungsrahmen reicht nach oben weit über die Seite hinaus); bei einem Sprung ans
  Ende bleibt nichts versteckt.
- **Staffel:** Was gemeinsam ankommt, läuft in Lesereihenfolge: 60 ms von links nach rechts (höchstens 6 Schritte, die
  sieben Rubrikkacheln also 0 bis 360 ms), jede weitere Reihe 100 ms später (höchstens 300 ms). Die Rubrikkacheln
  kommen als Gruppe, damit auch die rechts angeschnittenen am Handy fertig sind.
- **Endzustand = klar2.** Nach jeder Variante liegt jedes der 266 Elemente in Kopf, Band und Hauptteil auf denselben
  Pixeln wie in `../index.html`, ohne Rest von Versatz, Transparenz, Beschnitt oder Zeilenspannen (gemessen, siehe
  unten).
- **Nur `transform`, `opacity`, `clip-path`.** `transform` als Einzeleigenschaften `translate` und `scale`, damit
  der Bildzoom von klar2 beim Überfahren (`transform: scale(1.03)`) erhalten bleibt. `will-change` nur, solange ein
  Stück läuft (Klasse `.laeuft`). Bilder behalten `width`/`height`; nichts verändert das Layout.
- **Stufenweise.** Ohne Skript, vor dem Skript und bei einem Fehler ist alles sichtbar: Versteckt wird nur unter
  `html.bewegt` und nur an Elementen, denen das Skript `data-art` gegeben hat. Bei einem Fehler nimmt das Skript
  `.bewegt` weg und meldet ihn in der Konsole.
- **Reduzierte Bewegung:** Alles steht in `@media (prefers-reduced-motion: no-preference)`, und das Skript setzt bei
  `reduce` weder `.bewegt` noch `data-art`. Ergebnis: klar2 ohne jede Bewegung, auch ohne Leselinie und Kopffaltung.
  Die Leiste bleibt und sagt „Bewegung reduziert (Systemeinstellung).“ Ändert sich die Einstellung bei offener Seite,
  stellt sich die Seite neu auf. Der Block aus `klar2.css` (keine Übergänge bei `reduce`) gilt weiter.
- **Technik:** Auftritte sind zeitgesteuert (feste Dauer, einmal) und laufen daher über IntersectionObserver plus
  Klasse `.da` mit CSS-Übergängen. Was am Scrollweg hängt, läuft über CSS-Scroll-Timelines (`view-timeline` am Kopf und
  am Aufmacherbild, `scroll(root)` für die Leselinie) in `@supports (animation-timeline: scroll())`. Kann der Browser
  das nicht (zurzeit Firefox), rechnet ein einziger passiver Scroll-Handler mit `requestAnimationFrame` dieselben Werte
  als Variablen an drei Elementen.
- **Sprünge auf der Seite** (`#diese-woche`, `#kueche`) scrollen weich, ohne die Adresse zu ändern, damit der geteilte
  Link die Variante behält. Platzhalter-Links `href="#"` tun in der Vorschau nichts (in klar2 springen sie nach oben).

## Die Varianten

Kurven: `--expo` = `cubic-bezier(.16,1,.3,1)` (ease-out-expo), `--sanft` = `cubic-bezier(.33,1,.68,1)`
(ease-out-cubic, nur für Einblenden), `--vorhang` = `cubic-bezier(.3,.1,.1,1)` (kurz an, lang aus).

### A Einblenden

| Was | Bewegung | Dauer, Kurve | Technik |
|---|---|---|---|
| Aufmacher, Rubrikkacheln, Nebenstücke, Meldungen, Blocktitel, alles in „Diese Woche“ und „Küche“ | 16 px nach oben, von 0 auf 1 | Weg 500 ms `--expo`, Deckkraft 400 ms `--sanft`; Staffel wie oben | IO + `.da`, Übergang auf `translate`/`opacity` |

Reduziert: steht still, alles sichtbar.

### B Aufdecken

| Was | Bewegung | Dauer, Kurve | Technik |
|---|---|---|---|
| Bilder (Nebenstücke, Meldungen, Rubrikkacheln, Kacheln) und die drei Kacheln ohne Foto | Freigabe von unten: `clip-path: inset(100% 0 0 0)` → `inset(0)`, Bild dabei 1,06 → 1 | je 650 ms `--expo` | `clip-path` am Rahmen, `scale` am Bild |
| Überschriften (Titel, Blocktitel) | steigen Zeile für Zeile aus einer Kante: jede Zeile von 115 % ihrer Höhe auf 0 | 650 ms `--expo`, Start 140 ms nach dem Bild, je Zeile 80 ms; Blocktitel ohne Bild ab 0 ms | Skript misst die Zeilen nach dem Laden der Schrift und legt sie in Spannen; Beschnitt per `clip-path` je Zeile |
| Dachzeile, Rubrikname im Bild | nur einblenden | 450 ms `--sanft`, ab 100 ms | `opacity` |
| Vorspann, Kino-Zahlen, Orte, Termintext | nur einblenden | 450 ms `--sanft`, ab 320 ms | `opacity` |

Zeilen und Barrierefreiheit: Der Text bleibt echter Text in der Überschrift (gleiche Wörter, gleiche Leerzeichen,
`.zusammen` bleibt ganz, keine `aria`-Eingriffe). Sobald eine Überschrift erschienen ist, setzt das Skript ihr
ursprüngliches HTML zurück; dann gilt auch die Unterstreichung beim Überfahren wieder. Geteilte und ungeteilte
Überschriften sind gleich hoch (gemessen). Bei neuer Fensterbreite werden noch nicht gezeigte Überschriften neu
gemessen. Reduziert: nichts wird geteilt, nichts bewegt.

### C Kopf & Bänder

| Was | Bewegung | Dauer, Kurve | Technik |
|---|---|---|---|
| Kopfzeile | verblasst auf den ersten 45 % der Kopfhöhe (45 / 49 / 54 px Scrollweg) | an den Weg gebunden, linear | `view-timeline` am Kopf, `opacity` |
| Logo | wird von 1 auf 0,8 kleiner (Ankerpunkt unten links), bleibt bis zu 40 px zurück und schiebt sich unter das Band; ab 50 % des Wegs blasst es aus, bei 90 % ist es weg | Weg = Kopfhöhe (101 / 109 / 119 px) | `translate`, `scale`, `opacity` |
| Rubrikband | bleibt wie in klar2 als einziges stehen; an seiner Unterkante eine rote Leselinie, 2 px, die mit dem Lesefortschritt der Seite von links wächst | ganze Seite | `scroll(root)`, `scale` X 0 → 1 |
| Aufmacherbild | läuft beim Hinausscrollen bis zu 40 px langsamer als die Seite (Titel im Bild läuft normal mit) | ab Bildoberkante an der Bandunterkante (48 px) bis Bildunterkante dort | `view-timeline` am Bildrahmen, `translate` am Bild; der freie Streifen oben liegt stets unter dem Band |
| „Diese Woche“ | die dunkle Fläche zieht von links auf | 800 ms `--vorhang` | Deckfläche in Seitenfarbe (`::after`), die per `scale` nach rechts wegschrumpft |
| Inhalt von „Diese Woche“ | 16 px nach oben, von 0 auf 1, gestaffelt | 500 ms `--expo`, Start bei 55 % des Vorhangs (440 ms) | IO + `.da` |

Kopf: klar2 erlaubt als festes Element nur das Band (höchstens 56 px, Kriterium 13). Der Kopf bleibt also nicht
stehen und wird kleiner, sondern faltet sich beim Wegscrollen ins Band. Kein Logo im Band: die Datei ist dunkel auf
hell und auf dem Band nicht lesbar, verändert werden darf sie nicht.
Vorhang: zuerst als `clip-path` am Bereich gebaut. Der IntersectionObserver meldet Inhalt unter einem beschnittenen
Vorfahren aber erst, wenn der Beschnitt ganz weg ist (gemessen rund 1,1 s), dann stand die Fläche 300 ms leer. Die
Deckfläche sieht gleich aus und läuft auf dem Compositor.
Reduziert: keine Faltung, keine Leselinie, keine Tiefe, kein Vorhang.

### D Kombination (Empfehlung)

| Teil | aus | Werte |
|---|---|---|
| Kopf faltet sich ins Band, rote Leselinie, Aufmacher-Tiefe 40 px | C | wie C |
| „Diese Woche“: Fläche zieht auf, danach der Inhalt | C | Vorhang 800 ms; Inhalt ab 440 ms |
| Große Bilder (Kanguva, Kottu Roti) decken sich auf, Titel im Bild steigt zeilenweise | B | Bild 750 ms, Maßstab 1,06 → 1 über 1100 ms (setzt sich nach dem Aufdecken noch), Zeilen 700 ms ab 160 ms, je Zeile 90 ms |
| Blocktitel („Weitere Meldungen“, „Diese Woche“, „Küche“) steigen aus ihrer Linie | B | 700 ms ab 0 ms |
| Rubrikkacheln, Nebenstücke, Meldungen, kleine Kacheln, Kino- und Termin-Kacheln steigen gestaffelt | A | 16 px, 560 ms |

Warum D: Die Regel ist in einem Satz zu sagen: Kopf und Flächen hängen am Scrollen, große Bilder und Blocktitel
decken sich auf, alles in Listen steigt ruhig nach. A allein ist sauber, aber austauschbar; B auf jedem kleinen Bild
und jeder Meldung ist in langen Listen unruhig (am Handy bewegen sich je Meldung drei Dinge); C allein lässt die Mitte
der Seite still. D setzt das Aufdecken nur dort ein, wo das Bild groß genug ist, dass man es sieht, und die erste
Antwort aufs Scrollen kommt sofort vom Kopf, nicht erst von Inhalten weiter unten. Reduziert: wie alle, nichts bewegt.

## Ergebnisse

`node tools/shots.mjs design/richtungen/klar2/bewegung/index.html --out design/richtungen/klar2/bewegung/shots --kacheln`
(Standard D; das Werkzeug scrollt einmal durch und fotografiert dann):

| Breite | seitlicher Überlauf | Konsolenfehler | leere Bilder | fehlende Schriften | kleine Tippflächen | Tamil ohne `lang` |
|---|---|---|---|---|---|---|
| 390 | 0 | 0 | 0 | 0 | 0 | 0 |
| 820 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1280 | 0 | 0 | 0 | 0 | 0 | 0 |

`node design/richtungen/klar2/bewegung/pruefen.cjs --bilder` (Chromium 153), 30 von 30 bestanden:

- Endlage wie klar2 bei 390, 820 und 1280 für A, B, C, D und Aus (je 266 Elemente, Abweichung ≤ 0,5 px, keine
  Reste von `opacity`, `translate`, `scale`, `clip-path`, keine Zeilenspannen, Deckfläche weg).
- Zeilenteilung: B teilt 20 (390) und 15 (1280) Überschriften, D 5 und 4; Text und Höhe gleich wie ungeteilt.
- Sprung ans Seitenende bei A–D: danach nichts mehr versteckt.
- Umschalten: ohne Hash startet D und schreibt `#d`; Knopf B setzt `#b`, springt nach oben und stellt neu auf; Aus
  entfernt alle Zustände.
- Ersatzweg ohne Scroll-Timelines (in Chromium simuliert): Logo bei 60 px Weg auf 0,88 / Deckkraft 0,76, Leselinie
  wächst, Tiefe 40 px.
- Reduziert (`reducedMotion: 'reduce'`) bei A–D: nichts versteckt, nichts geteilt, Leiste sagt „Bewegung reduziert
  (Systemeinstellung).“
- Keine Konsolenfehler.

Einzelbilder in `shots/frames/` (390 × 844, mitten in der Bewegung, nach Scrollen in 120-px-Schritten pro Bild):

| Variante | Bilder |
|---|---|
| A | `a-1-liste-steigt`, `a-2-liste-ende`, `a-3-woche-steigt`, `a-4-kueche-steigt` |
| B | `b-1-bilder-decken-auf`, `b-2-liste-ende`, `b-3-kanguva-deckt-auf`, `b-4-kueche-deckt-auf` |
| C | `c-1-kopf-faltet`, `c-2-band-steht`, `c-3-flaeche-zieht-auf`, `c-4-flaeche-inhalt` |
| D | `d-1-kopf-faltet`, `d-2-liste-steigt`, `d-3-flaeche-zieht-auf`, `d-4-kanguva-deckt-auf` |
| reduziert | `reduziert-0-oben`, `reduziert-1-woche` |

## Nicht geprüft

- Echte Geräte und andere Browser: Safari und Firefox nicht geöffnet (Firefox nutzt den Ersatzweg, nur simuliert);
  keine Messung der Bildrate auf einem Handy.
- Bildschirmleser mit den geteilten Überschriften nicht ausprobiert; geprüft ist nur, dass Text und Wortgrenzen gleich
  bleiben und nach dem Auftritt das Original-HTML zurückkommt.
- `design/vergleich/aufnahmen.mjs klar2` nicht gegen diese Seite gelaufen. Kriterium 13 aus §10.4 (Maßstab höchstens
  1,04, Übergang höchstens 0,4 s, keine Animation) verletzen A bis D mit Absicht: Maßstab 1,06 beim Aufdecken,
  Übergänge bis 1,1 s, Scroll-Timelines. Nach der Wahl von Luis muss §10.1/§10.4 für die gewählte Bewegung nachgezogen
  werden; der Hover-Zoom (1,03, 0,35 s) bleibt unverändert.
