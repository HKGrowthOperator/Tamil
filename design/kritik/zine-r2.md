# Kritik zine, Runde 2
Punkte: 28/40 · Slop-Test: bestanden (knapp) · Template-Geruch: 3/4 · **Urteil: zeigen**

Grundlage: eigene Aufnahmen 390/820/1280 mit `tools/shots.mjs --kacheln` (Scratch-Ordner, 0 Fehler, kein seitliches
Scrollen, keine Konsolenfehler, alle Schriften geladen), Quelltext `index.html`, `artikel.html`, `zine.css`,
Detektor `impeccable detect --fast`, Abgleich mit `prototyp/content/posts.json` (9711, 9655) und Brief Abschnitt 8.
`begruendung.md` erst nach der Bewertung gelesen.

## Erster Eindruck (3 Sätze)
Am Handy steht in fünf Sekunden ein Heftkopf („HEFT KW 45“ groß in Rot neben dem Logo), ein schief eingeklebtes, in
Logo-Rot gedrucktes Kanguva-Foto und darüber gedruckt ein riesiges „KANGUVA“: das ist ein Cover, kein Nachrichtenportal,
und es sieht keinem der drei abgelehnten Entwürfe ähnlich. Der Abschnitt „Diese Woche“ auf rotem Grund mit Aushängen
und gestrichelten Ortsstreifen ist klar anders gebaut als das Cover, wirkt aber deutlich braver als der Kopf. Der
Artikel ist ruhig, groß gesetzt und gut lesbar; die Lautstärke klingt nur noch in Stempel und Überschrift nach.

## Heuristiken
| # | Heuristik | Punkte | Begründung |
|---|---|---|---|
| 1 | Systemstatus | 3 | `aria-current` in Rubrikzeile und Daumenleiste, Hover-Zustände, „Aus Heft KW 35“ sagt im Artikel, wo man ist. |
| 2 | Sprache der Nutzer | 3 | Durchgehend Deutsch, „Spielorte“, „Per WhatsApp weiterschicken“, „Zum Weiterschicken an die Familie“ treffen die Leser; „Heft KW 45“ ist etwas Amtsdeutsch. |
| 3 | Kontrolle und Freiheit | 3 | Sprunglink, Logo zurück zur Startseite, Daumenleiste unten mit „Inhalt“ als Ausweg zu allen Rubriken. |
| 4 | Konsistenz | 3 | Stempel, Linien und Schriftstimmen ziehen sich durch beide Seiten; Brüche: Seitentitel „Heft KW 46“ gegen sichtbar „KW 45“, Inhaltsliste bei 820 kollidiert. |
| 5 | Fehlervermeidung | 3 | Ganze Cover- und Aushangfläche ist Tippziel, Weiterschicken-Streifen 48 px; Rubrikstempel im Artikel nur 39 px hoch. |
| 6 | Wiedererkennen statt Erinnern | 3 | Rubriken als Wörter, oben (ab 1100 px) und unten (Handy, Tablet), Inhaltsverzeichnis als letzte Heftseite. |
| 7 | Flexibilität | 3 | Zwei Navigationswege, Teilen ohne Umweg, Abkürzung „Inhalt“; Suche fehlt (für die Skizze kein Befund). |
| 8 | Ästhetik und Minimalismus | 3 | Das Cover ist konzentriert und eigenständig; „Diese Woche“ bleibt ein Kartenstapel auf Rot mit leicht zufällig wirkenden Versätzen. |
| 9 | Fehler erkennen und beheben | 2 | Kein Fall auf diesen Seiten; die 2024-Heftzeile neben einem Diwali-Termin 2026 ist eine eingebaute Verwirrung. |
| 10 | Hilfe | 2 | Kontexthinweise vorhanden („und 6 weitere Städte“, Unterzeile des Bretts), sonst nichts nötig und nichts da. |
| | **Summe** | **28/40** | Good, knapp an der Schwelle. |

## KI-Slop-Test: bestanden (knapp)
- Keine Bans aus impeccable: keine Seitenstreifen-Ränder als Deko, kein Verlaufstext, kein Glas, keine Hero-Metrik,
  kein Modal, keine identischen Kartenraster (drei Aushänge mit verschiedenem Aufbau: Ortsraster, Absender plus
  Datumstempel, Zwei-Orte-Raster).
- Kategorie-Reflex 1. Ordnung (Nachrichtenportal-Raster) vermieden. **2. Ordnung ist das Risiko:** „Zine“ → Halbtonraster,
  Duoton, Gummistempel mit Doppelrahmen, gestrichelte Abrisslinien, schiefes Foto ist der Standardbaukasten, den man
  bei „Zine“ erraten würde. Gerettet wird es durch die Komposition (Coverwort als Überdruck über dem Rotdruck, Heftkopf
  aus Kalenderwoche, Breitenachse der Anybody von 50 % am Handy bis 120 % am Desktop) und durch Zurückhaltung (nur
  Foto und ein Stempel gedreht). Ein weiterer Stempel mehr, und es kippt.
- Detektor (`impeccable detect --fast`): `cream-palette` auf beiden Seiten (rgb 251 246 245), `tight-leading` 1,18 im
  Artikel, `cramped-padding` am Brett. Eigene Prüfung: Der Grund ist `oklch(97.6% 0.006 25)`, ein fast neutrales,
  leicht rötliches Weiß, kein Sand; mit Grotesk-Text und fast schwarzer Tinte ist das nicht die abgelehnte
  Creme-Serife-Braungrau-Kombination (Fehlalarm, P3). Die enge Zeilenhöhe betrifft Auszeichnungszeilen (Heftzeile,
  Überschriften), nicht den Fließtext (1,55). „cramped-padding“ am Brett ist ein Fehlalarm (Rand `--rand` ist da).

## Template-Geruch: 3/4
Kein Theme, das man kennt. Abzug, weil „Diese Woche“ am Handy als Stapel weißer Kästen auf Rot einem Karten-Layout
nahekommt, und weil die Stempel-Sprache (vier Doppelrahmen-Kästen auf zwei Seiten) Richtung Etikett geht.

## Verbotsliste
Keine Übereinstimmung. Kein Nachtblau, Gold, Neon, Ornament; keine tamilische Schrift (auch nicht als Deko); kein
Laufband; keine Pillen, Rundungen, Story-Kreise, Knopfreihen, rosa Kästen, kein 01/02/03; Schriften Anybody und
Atkinson Hyperlegible Next stehen weder auf der impeccable-Liste noch unter den verbrannten Schriften. Grenzfall
„rote Platte über dem Bild“: Hier ist das Foto selbst rot gedruckt und die Überschrift steht auf Papier; das ist ein
anderes Mittel, wird aber vom Auftraggeber womöglich als „schon wieder rot über dem Bild“ gelesen (siehe P2-2).

## Marke und Leser
- **Idee im ersten Bildschirm:** Ja. Bei 390 × 844 stehen Heftkopf, Coverzeile, Foto, „KANGUVA“, die vollständige
  Überschrift (endet bei etwa 580 px), Vorspann und „Weiterlesen“ über der Daumenleiste; „Diese Woche“ beginnt
  darunter. Bei 1280 stehen Coverwort und Überschrift gemeinsam im ersten Bildschirm.
- **Nur zu tamil.de?** Teilweise. Das „Heft der Woche“ könnte jedes Wochenmagazin tragen. Tamil-eigen wird es erst
  im Brett: Verein als Absender, Kinos als Ortsstreifen, „Zum Weiterschicken an die Familie“. Das ist sichtbar, aber
  leiser als das Cover.
- **Gen Z:** Das Cover würde eine 19-Jährige als Screenshot teilen (Rotdruck plus Riesenwort sieht nach Heft aus,
  nicht nach Portal). Das Brett eher nicht.
- **Ältere:** Fließtext 19 px (Desktop 20 px), Zeilen um 64 Zeichen, Text auf Rot 5,9:1, Atkinson Hyperlegible,
  Rubriken als ganze Wörter unten am Daumen, Ortsnamen waagerecht. Ein 65-Jähriger kommt zurecht.
- **Tamil-Satz:** Keine Tamil-Zeichen auf den Seiten; `:lang(ta)` und Noto Sans Tamil als Ersatz im Stapel sind
  vorbereitet. Bericht: `tamil_ohne_lang` 0.
- **Inhalte:** Titel, Vorspann, Erscheinungsdatum (6.11.2024 → KW 45; 26.8.2024 → KW 35), Lesezeit 2, Länderliste,
  Bilder und Bildmaße stimmen mit 9711 und 9655 überein; Kino- und Diwali-Angaben stimmen mit Brief Abschnitt 8;
  21.11.2026 ist ein Samstag. Der WhatsApp-Kanal-Link steht in `site.json` unter den Kanälen (nicht unter den
  Beispielwerten). „Mit Spannung erwartet“ steht wörtlich im Vorspann. Ausnahmen siehe P2-3 und P2-4.

## Technik (`bericht.json`)
0 Fehler, Überlauf 0 bei allen sechs Aufnahmen, keine Konsolenfehler, alle Bilder und Schriften geladen. Hinweis:
eine Tippfläche unter 44 px (Rubrikstempel „Nachrichten“ im Artikel, 149 × 39, bei 390 und 820).

## Befunde

- **P0:** keine.
- **P1:** keine.

- **P2-1 „Diese Woche“ trägt die Idee nicht so stark wie das Cover** (index, 390 und 820, `.brett`/`.aushang`).
  Am Handy sind es drei weiße Kästen untereinander auf Rot; die Versätze (`.aushang:nth-child(2)` 20 px links
  eingerückt, `nth-child(3)` 28 px rechts) lesen sich wie ein Layoutfehler, nicht wie angeheftete Zettel, seit die
  Drehung entfernt wurde. Behebung: entweder entschieden „angeheftet“ (ein sichtbarer Befestigungspunkt oder eine
  oben schwerere Kante je Aushang, verschiedene Breiten statt Einrückungen) oder bündig setzen und den Rhythmus allein
  über Größe und Ortsstreifen tragen. Kein Zufallsversatz von 20 px.
- **P2-2 Rotdruck als Dauerlösung** (index, alle Breiten, `.druck img` mit `filter … brightness(2.35)` und
  `mix-blend-mode: screen`). Das Kanguva-Foto trägt, aber jedes Kino-/Kultur-Cover verliert seine eigenen Farben,
  und der Auftraggeber hat Runde 3 wegen „rot über dem Bild“ verworfen. Behebung vor dem Ausbau: auf der Probeseite
  ein zweites, helles Cover (Küche oder Community) im Rotdruck zeigen und die Graustufen-Variante `.cover--nachricht`
  sichtbar machen, damit der Auftraggeber die Spannweite sieht, nicht nur das eine dunkle Filmstill.
- **P2-3 Heftdatum widerspricht „Diese Woche“** (index, 390 Kopf rechts; 820/1280 `.heft`). Der Heftkopf sagt groß
  „KW 45 · 4. bis 10. Nov. 2024“, direkt darunter steht als „Diese Woche“ Diwali am 21. Nov. 2026. Am Handy ist die
  Jahreszahl 2024 das Zweitgrößte auf dem Schirm und lässt die Seite veraltet wirken. Behebung: Die Heftkennung des
  Covers nur als KW ohne Jahr groß zeigen und das Datum klein; oder das Brett „Diese Woche“ an die laufende Woche
  koppeln und das so beschriften. Die Regel „Cover trägt die Woche seines Beitrags“ vor dem Ausbau mit dem
  Auftraggeber klären.
- **P2-4 „Aushang von Basel Tamil Sangam“ schreibt dem Verein die Urheberschaft zu** (index, Diwali-Aushang,
  `.aushang-art` + `.absender`). Laut Brief ist das ein Radar-Entwurf der Redaktion, kein Aushang des Vereins.
  Behebung: „Basel Tamil Sangam feiert“ (wörtlich aus dem Brief) oder „Veranstalter“ statt „Aushang von“.
- **P2-5 Inhaltsverzeichnis kollidiert bei 820** (index, 820, `.inhalt li a`, `minmax(9.5rem, 1fr)`):
  „ENTERTAINMENT“ läuft in „EVENTS“ hinein und liest sich als „ENTERTAINMENTEVENTS“. Behebung: Mindestbreite der
  Spalten auf etwa 12rem anheben oder Schriftgröße per `cqi` an die Spaltenbreite koppeln; `overflow-wrap` reicht
  bei Versalien nicht.
- **P2-6 Tippfläche Rubrikstempel** (artikel, 390 und 820, `.stempel--rubrik a`, 149 × 39). Behebung: vertikale
  Polsterung auf mindestens 44 px Gesamthöhe.
- **P2-7 Die „Haltung“ des Covers ist in der Skizze zahm** (index, `.cover-ruf` „Mit Spannung erwartet“). Belegt,
  aber es ist eine Floskel aus dem Vorspann; Burnt Roti lebt von einer Zeile mit Meinung. Die Anführungszeichen
  suggerieren zudem ein Zitat ohne Sprecher. Behebung: Anführungszeichen weglassen (Coverzeile, kein Zitat) und dem
  Auftraggeber sagen, dass die Redaktion hier wöchentlich eine eigene Zeile schreiben muss; sonst bleibt das Feld leer
  statt mit Floskeln gefüllt.

- **P3-1** Seitentitel `index.html` lautet „Heft KW 46“, sichtbar ist „KW 45“. Angleichen.
- **P3-2** Gestrichelte Ortsstreifen ragen 2 px über die rechte Aushangkante (index, 820/1280, Diwali-Aushang,
  `.zettel` mit `margin-right: -2px` je `li`). Letzte Spalte ohne negativen Rand.
- **P3-3** Detektor-Treffer `cream-palette`: Fehlalarm in der Sache, aber der Auftraggeber reagiert auf „Creme“.
  Beim Ausbau den Grund eine Spur kühler oder neutraler prüfen (Chroma 0,006 → 0,003), damit er auf keinem Bildschirm
  ins Warme kippt.
- **P3-4** Stempel-Sprache dosieren: „Kino“, „Nachrichten“, „Basel Tamil Sangam“ und der Datumstempel tragen alle
  denselben Doppelrahmen. Beim Ausbau eine Regel: je Fläche höchstens ein Stempel.
- **P3-5** Kino und Events in der Daumenleiste führen beide zu `#woche` (in der Skizze hinnehmbar, im Theme trennen).

## Was stark ist
- Das Coverwort in Anybody mit Breitenachse: am Handy gestaucht und hoch, am Desktop breit über die ganze Seite und
  als Überdruck ins Rotfoto greifend. Das ist ein eigenes Signatur-Element, das nur diese Schriftwahl so kann.
- Der Artikel hält das Versprechen „ruhig im Text“: Atkinson Hyperlegible 19/20 px, Foto in Farbe, ein Stempel, eine
  Linie, Teilen über WhatsApp als schlichter Link, Länderliste zweispaltig. Lesbar für Großeltern, ohne altbacken
  zu wirken.
- Die Ortsstreifen lösen „11 Kinos und 2 Kinos“ und „Eintrag ohne Foto“ sauber und ohne Platzhalterbild.

## Abgleich mit `begruendung.md` (nach der Bewertung gelesen)
- **Sichtbar:** Heft der Woche mit Kalenderwoche, Zweifarbdruck, Coverwort als Überdruck, Gummistempel, Abreißzettel
  je Spielort, Daumenleiste, Weiterschicken als Abreißzettel von heute, ruhiger Artikel. Das trägt.
- **Nicht oder kaum sichtbar:** „Schwarzes Brett aus dem Asia-Laden“ und „Aushänge verschieden schief“. Nach dem
  Entfernen der Drehung (Runde 2) liest niemand ohne Erklärung ein Brett; es sind Kästen auf Rot (P2-1). Das
  Bild „am Vereinsabend kopiert, am Tempeleingang ausgelegt“ ist eine starke, nur tamil.de-eigene Erzählung, auf der
  Seite aber nur im Cover angedeutet.

## Vor einem Ausbau zu beheben
P2-1 (Brett entscheiden), P2-3 (Heftdatum gegen „Diese Woche“), P2-4 (Absender-Formulierung), P2-5 und P2-6
(Technik), dazu für Tor G2 ein zweites Cover zeigen (P2-2).
