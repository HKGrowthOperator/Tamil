# Kritik zine, Runde 1
Punkte: 27/40 · Slop-Test: bestanden (knapp) · Template-Geruch: 3/4 · **Urteil: überarbeiten**

Grundlage: eigene Aufnahmen (`node tools/shots.mjs … --kacheln`, 390/820/1280, beide Seiten), `bericht.json`
(0 Fehler, kein Überlauf, keine Konsolenfehler, keine zu kleinen Tippflächen, kein Tamil ohne `lang`), Detektor
`npx impeccable detect --fast`, Quelltext `index.html`, `artikel.html`, `zine.css`. `begruendung.md` erst nach der
Bewertung gelesen (Abgleich unten).

## Erster Eindruck (3 Sätze)

Am Desktop ist das ein echtes Cover: „KW 46“ groß in Rot, ein schief eingeklebtes, rot gedrucktes Foto und „KANGUVA“
in voller Breite, das ins Bild schneidet. So etwas hat keiner der drei abgelehnten Entwürfe gehabt. Am Handy bleibt
davon ein lautes Plakat mit Rasterfoto, aber kein *Heft*: Die Ausgabe der Woche schrumpft dort auf eine kleine Zeile
oben rechts, und „Haltung“ im Sinn von Burnt Roti (eine redaktionelle Stimme auf dem Cover) zeigt keine der drei
Breiten.

## Heuristiken

| # | Heuristik | Punkte | Begründung |
|---|---|---|---|
| 1 | Systemstatus | 3 | `aria-current` und rote Unterstreichung zeigen die Rubrik, die Heftzeile nennt die Woche. Fokusrahmen klar. |
| 2 | Sprache der Nutzer | 3 | Deutsch, klare Wörter („Weiterlesen“, „11 Spielorte“, „Per WhatsApp teilen“). „Heft KW 46“ ist für Ältere eher Amtsdeutsch als Magazin. |
| 3 | Kontrolle und Freiheit | 3 | Sprunglink, Logo zur Startseite, Daumenleiste immer erreichbar, Inhaltsverzeichnis am Ende. |
| 4 | Konsistenz | 3 | Stempel-System (Rubrik, Datum) trägt durch beide Seiten. Abweichungen: Kino und Events führen beide auf `#woche`, „Entertainment“ im Artikel ebenso. |
| 5 | Fehlervermeidung | 3 | Ganze Cover- und Aushangfläche ist Ziel. „+ 6 weitere Städte“ sieht aus wie ein eigener Knopf, ist aber keiner. |
| 6 | Wiedererkennen | 3 | Rubriken sichtbar beschriftet, keine Icons ohne Text; am Handy nur vier Rubriken unten, der Rest erst am Seitenende. |
| 7 | Flexibilität | 2 | Ein Weg pro Ziel; keine Suche, kein Weg zu früheren „Heften“, obwohl die Idee Ausgaben verspricht. |
| 8 | Ästhetik und Reduktion | 3 | Zwei Tinten, starke Typografie, ruhiger Artikel. Aber sieben gedrehte Elemente plus Raster plus Stempel: der Zine-Baukasten wird vollständig ausgepackt. |
| 9 | Fehlerhilfe | 2 | In der Skizze nicht gezeigt (z. B. fehlendes Bild, abgelaufener Termin, Film nicht mehr im Kino). |
| 10 | Hilfe | 2 | Untertitel „Kino und Feste in Deutschland und der Schweiz“ hilft; sonst keine Orientierung, was ein „Heft“ hier ist. |
| | **Summe** | **27/40** | Knapp unter der Schwelle. |

## KI-Slop-Test: bestanden (knapp)

- Keine Verlaufsschrift, kein Glas, keine Hero-Metrik, kein Modal, keine Seitenstreifen-Karten. Die Kanten-Linie
  links neben dem Cover-Vorspann (Desktop) ist eine Spaltenlinie in Tinte, kein farbiger Akzentstreifen.
- Kein gleichförmiges Kartenraster: Die drei Aushänge unterscheiden sich in Größe, Drehung, Datumstempel und vor
  allem in der Zahl der Abreißzettel, die aus dem Inhalt kommt (11 Orte, 1 Ort, 2 Orte). Das ist eine echte
  Inhaltsentscheidung, keine Deko.
- **Kategorie-Reflex 1. Ordnung (Diaspora-Magazin → Gold, Ornament, Dunkel):** vermieden.
- **Kategorie-Reflex 2. Ordnung (Zine, das nicht App-Vorlage sein soll → Halbton-Raster, schief geklebt, Gummistempel,
  gestrichelte Abreißkante):** getroffen. Jedes dieser Mittel ist das erste, was ein Modell bei „Zine“ greift. Der
  Test ist nur deshalb bestanden, weil die Ausführung diszipliniert ist (zwei Farben, keine Klebeband-Texturen, keine
  Handschrift, keine Papierrisse) und die Abreißzettel an echten Inhalt gebunden sind. Siehe P2-1.

## Verbotsliste (`tamil-marke`)

Keine Übereinstimmung:
- Grund hell (rosé getöntes Weiß), kein Nachtblau, kein Gold/Gelb, keine Ornamente, kein Neon, kein Laufband.
- Keine tamilischen Wörter als Gestaltungsmittel; Noto Sans Tamil nur als Ersatzschrift über `:lang(ta)`. Nur Deutsch.
- Keine Pillen, keine runden Karten, keine Story-Kreise, keine abgerundeten Knopfreihen, keine rosa Kästen, kein
  01/02/03, keine Icons über Überschriften.
- Schriften Anybody + Atkinson Hyperlegible Next: weder auf der impeccable-Ausschlussliste noch unter den verbrannten
  Schriften.
- Detektor meldet `cream-palette` (rgb 251 246 245). Geprüft: Das ist ein kühles Weiß mit Rotstich (Chroma 0,006,
  Farbton 25), mit fast schwarzer Tinte und ohne Serife. Die verbotene Kombination Creme + Serife + Braungrau liegt
  nicht vor. Kein Befund, aber Ton nicht wärmer schieben (P3-1).
- Nah dran, aber nicht gleich: „rote Platte über dem Bild“. Siehe P2-3.

## Befunde

### P0
- Keine. `bericht.json` sauber bei allen sechs Aufnahmen.

### P1
- **P1-1 · Die Heft-Idee ist am Handy nicht sichtbar, und „Haltung“ fehlt auf allen Breiten.**
  Ort: `index.html`, 390 (und 820), erster Bildschirm, `.cover`. Der Kern laut Brief ist „jede Woche ein neues Cover
  mit Haltung, gebaut wie ein selbst gemachtes Heft“. Bei 390 ist `.heft` (großes „KW 46“) per `display: none`
  ausgeblendet; übrig bleibt `.heftzeile` oben rechts in 16–20 px gestauchter Schrift. Wer das Handy öffnet, sieht ein
  Kino-Plakat mit Rasterfoto, nicht die Ausgabe einer Woche. Am Desktop trägt „KW 46“ die Idee, am Handy, wo die
  Leser sind, nicht. Zweitens: Burnt Roti ist als Vorbild gewählt wegen der Haltung seiner Cover (eine Aussage, ein
  Ton, eine Zeile, die man weiterschickt). Hier ist das Cover die unveränderte Beitragsüberschrift in groß; es gibt
  keinen Ort, an dem eine Redaktion eine Woche *kommentiert*.
  Behebung: (a) Heftnummer am Handy ins Cover holen, nicht in den Kopf: z. B. „KW 46“ als zweiter Stempel auf der
  Bildecke oder eine Heftkopfzeile direkt über dem Foto („tamil.de · Heft 46 · 9.–15. Nov.“) in Coverschriftgröße,
  sodass Marke + Ausgabe + Coverwort eine Einheit bilden. (b) Eine Coverzeile als eigenes Feld vorsehen (eine kurze
  redaktionelle Zeile neben dem Titel, wie bei echten Heften), in der Skizze als Platzhalter klar gekennzeichnet,
  damit nichts erfunden wird; oder in der Begründung zeigen, woher die Haltung wöchentlich kommen soll. Ohne das ist
  „Haltung“ eine Behauptung.

### P2
- **P2-1 · Zine-Baukasten statt tamil.de-eigener Mittel.** Ort: beide Seiten, alle Breiten; `.druck` (Halbton-Raster,
  Drehung), `.stempel`, `.datumstempel`, `.aushang` (Drehung), `.zettel` (gestrichelt). Nimmt man Logo und Kanguva
  weg, könnte das jedes Indie-Zine-Theme sein. Die Begründung nennt starke, nur hier passende Orte (Tempeleingang,
  Asia-Laden, Vereinsabend), aber davon ist nichts sichtbar; es steht nur im Text. Behebung: mindestens ein Mittel
  aus genau dieser Welt statt eines Allzweck-Zine-Zeichens, z. B. den Aushang nach dem Vorbild echter Aushänge in
  tamilischen Läden/Tempeln gestalten (Kopf, Kontaktstreifen, Stempel des Vereins als Absender: „Basel Tamil Sangam“
  als Absenderstempel statt generischem „Fest“), und die Zahl der gedrehten Elemente halbieren (Cover-Foto und ein
  Stempel reichen; Aushänge gerade oder nur einer schief).
- **P2-2 · Cover-Foto trägt am Handy kaum.** Ort: `index.html`, 390, `.druck img`. Bei 355 px Breite wird Suriya in
  Rot-Halbton zu rotem Rauschen; Gesicht und Fellumhang sind nur mit Mühe zu erkennen, das Bild wirkt dunkler und
  matschiger als am Desktop. Behebung: am Handy enger auf das Gesicht schneiden (`aspect-ratio` 4:5 oder 1:1 mit
  `object-position`), Raster gröber oder ab ≤ 560 px weglassen, Kontrast/Helligkeit für kleine Breiten eigens
  abstimmen.
- **P2-3 · Rote Fläche + fette Schrift an der Unterkante liegt nah an „rote Platte über dem Bild“ (Runde 3).** Ort:
  `index.html`, 390, Cover. Technisch ist es ein rot gedrucktes Foto und die Schrift steht auf Papier, aber auf den
  ersten Blick am Handy liest sich ein rotes Rechteck mit riesiger schwarzer Grotesk an der Unterkante. Der
  Auftraggeber hat genau diesen Eindruck abgelehnt. Behebung: Foto am Handy heller drucken (mehr Papier im Bild,
  weniger Volltonrot), damit es als Druck und nicht als Fläche gelesen wird; Überschneidung von „KANGUVA“ und Bild
  klar als Überdruck zeigen (z. B. Schrift über dem Bild statt bündig an seiner Kante).
- **P2-4 · Heftdatum 2026 neben einem Beitrag von 2024 suggeriert einen aktuellen Kinostart.** Ort: `index.html`,
  alle Breiten, `.heft`/`.heftzeile` zusammen mit „ab 14. November“. Kanguva startete am 14. November 2024; unter
  „Heft KW 46 · 9.–15. November 2026“ liest jeder „startet diese Woche“. Inhalt ist vom Brief vorgegeben, die
  Kombination mit dem Heftdatum ist eine Entscheidung der Richtung. Behebung: in der Skizze das Originaldatum des
  Beitrags am Cover zeigen oder das Heftdatum sichtbar als Muster kennzeichnen; im Theme: ein Altbeitrag darf nie
  Cover einer laufenden KW werden, ohne dass sein Datum sichtbar ist.
- **P2-5 · Rot-Halbton nur für Kino gedacht, gilt aber für jedes Cover.** Ort: `zine.css`, `.druck img`. Bei einem
  Nachrichten-Aufmacher (Unglück, Politik in Sri Lanka, Todesfall in der Community) wirkt ein rot gerastertes Gesicht
  wie ein Fahndungs- oder Propagandaplakat. Das widerspricht „Nachrichten ruhig und seriös“. Behebung: zweite
  Cover-Tonlage festlegen (Nachrichten-Cover mit Foto in Graustufen/Farbe und Rot nur im Stempel) und in der
  Begründung zeigen.
- **P2-6 · Linkname des Covers ist ein ganzer Absatz.** Ort: `index.html`, `.cover-flaeche`. Der Link umfasst
  Alt-Text (zwei Zeilen Bildbeschreibung), Titel, Vorspann und „Weiterlesen“; Screenreader lesen das alles als
  einen Linknamen. Behebung: `aria-labelledby` auf die Überschrift setzen oder das Bild im Link mit `alt=""`
  auszeichnen (die Beschreibung gehört in den Artikel).

### P3
- **P3-1 · Grundton beobachten.** `--papier` ist korrekt ein rotstichiges Weiß; der Detektor liest es schon als
  Creme. Bei der Umsetzung nicht wärmer oder gelblicher werden lassen.
- **P3-2 · „+ 6 weitere Städte“ sieht wie ein Knopf aus** (getönte Fläche, Rot), ist aber nur Text; der Tipp führt
  über den Aushang-Link zum Film. Entweder echter Link zur vollständigen Ortsliste oder optisch wie die anderen Zettel.
- **P3-3 · Heftzeile am Handy schwer lesbar für Ältere:** „9. bis 15. Nov. 2026“ 16 px in Breite 62 % und Grau.
  Breite auf ≥ 75 % oder Größe auf 18 px.
- **P3-4 · Gedrehte Textblöcke:** Die Aushänge mit Fließtext sind um 0,4–1° gedreht; auf Bildschirmen mit niedriger
  Pixeldichte wird Text dadurch weicher. Drehung auf Rahmen/Stempel beschränken, Text gerade.
- **P3-5 · Navigation doppelt belegt:** Daumenleiste „Kino“ und „Events“ beide auf `#woche`, im Artikel auch
  „Entertainment“. In der Skizze tragbar, im Theme getrennte Ziele.
- **P3-6 · Desktop 1280:** Die Coverzeile („Ein tamilisches Kino-Highlight …“) beginnt bei etwa 640 px und läuft bei
  800 px Fensterhöhe unter die Kante. Keine Pflicht laut Brief, aber Coverwort-Größe (18,4 cqi) ließe sich etwas
  senken, damit Titel und Coverwort zusammen im ersten Bildschirm stehen.
- **Detektor, übrige Treffer:** `flat-type-hierarchy` ist ein Fehlalarm (Größen in `cqi`, jsdom rechnet ohne Layout);
  `cramped-padding` an `.aushang` unten ist gewollt (Abreißzettel bündig an der Kante), an `.brett` Fehlalarm;
  `tight-leading` im Artikel betrifft die Display-Überschrift mit Zeilenhöhe 1,0, für 38–68 px vertretbar.

## Was stark ist

1. **Abreißzettel als Datenform.** Spielorte werden zu Zetteln, 11 Kinos ergeben eine lange Reihe, 2 eine kurze, ein
   Ort einen Streifen; „+ 6 weitere Städte“ statt erfundener Namen. Das löst die Brief-Fälle „ohne Foto“ und „viele
   und wenige Spielorte“ in einem und ist das Eigenständigste an der Richtung.
2. **Desktop-Cover.** „KW 46“ in Rot, das gekippte Rotdruck-Foto und das angeschnittene „KANGUVA“ ergeben ein
   Plakat, das man teilen würde, und erfüllen „laut im Kopf“ ohne ein einziges verbotenes Mittel.
3. **Lauter Kopf, stiller Text.** Der Artikel nimmt nur den Rubrikstempel und die Anybody-Überschrift mit, sonst
   19/20 px Atkinson Hyperlegible Next, Zeilen ≤ 64 Zeichen, Foto in Farbe, WhatsApp als schlichter Link. Für
   65-Jährige am Handy gut lesbar, und die Schriftwahl ist begründet statt dekorativ.

## Abgleich mit `begruendung.md` (nach der Bewertung gelesen)

- **Sichtbar:** Zweifarbdruck, Gummistempel, Schwarzes Brett mit Abreißzetteln, ruhiger Artikel, Zustände aus dem
  Brief (kleines Bild, ohne Foto, lang/kurz, viele/wenige Orte) sind wie behauptet umgesetzt.
- **Nur teilweise sichtbar:** „jede Woche ein Cover mit der Kalenderwoche als Heftnummer“: am Desktop ja, am Handy
  nicht (P1-1).
- **Nicht sichtbar:** „das Heft, das am Tempeleingang ausgelegt wird“ und „das Schwarze Brett aus dem Asia-Laden“.
  Diese Bilder machen die Idee zu einer tamil.de-Idee, aber auf den Seiten steht davon nichts, was ein allgemeines
  Copyshop-Zine nicht auch hätte (P2-1). Die „Haltung“ aus dem Burnt-Roti-Vorbild wird in der Begründung genannt,
  aber nicht eingelöst (P1-1).

Urteil **überarbeiten**: 27/40 und ein offenes P1. Die Richtung ist behebbar und hat mit den Abreißzetteln und dem
Desktop-Cover zwei echte Stärken; sie verliert ihre Idee genau dort, wo der Auftraggeber zuerst hinsieht, am Handy.
