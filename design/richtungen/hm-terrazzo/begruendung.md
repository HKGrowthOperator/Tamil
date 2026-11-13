# hm-terrazzo „Terrazzo“ (Linie D, Website) – Begründung

Stand 13.11.2026. Gestaltet nach `design/brief-v3.md` und `design/linien-auftrag.md` mit Hallmark, Theme **Terrazzo
(by request)**. Das Cockpit dieser Linie baut ein anderer Gestalter mit denselben Tokens (`tokens.css`).

## Idee

Der Terrazzoboden vieler tamilischer Häuser in Chennai und Jaffna wird in Feldern gegossen, die Messing- oder
Glasstreifen voneinander trennen. tamil.de übernimmt nur diese Ordnung: Die Seite ist in **Felder ungleicher Breite**
gelegt, getrennt durch 2 px breite Tintenstreifen (die „Fuge“); die Farbe kommt allein aus den Fotos. Kein Muster,
keine Ornamente, keine tamilische Schrift, keine Folklore.

## Hallmark-Picks

**Hallmark · v2.0.0**

- **Shape** · Index-First (Tausch gegen die Ziehung „Letter“ aus Draw 92e264: eine Nachrichtenseite ist ihre Liste) · genre editorial · job: lesen, finden, teilen (Anatomie „listen: a publication“)
- **Theme** · Terrazzo, auf Wunsch; Farbweg „Zement“: kühles Off-white `oklch(96.6% 0.004 250)` statt des warmen Off-white (Runde 2 „Creme“ und Gate 65), Tinte `oklch(19% 0.012 260)`
- **Signal** · das Logo-Rot `oklch(50.8% 0.177 25.6)` (= #B5282A) statt Rost. Rost `oklch(53% 0.15 38)` liegt dem Logo-Rot in Helligkeit und Ton so nah, dass beide nebeneinander wie ein Fehldruck wirken; also trägt das Logo-Rot die wenigen Signale: Fokusring, Unterstreichung beim Überfahren, aktiver Navigationspunkt, Zeile „Heute“, Premium-Marke, Pflichtstern. Nie Fläche.
- **Schrift (bis r1, ersetzt)** · Syne 600 für Köpfe (bewusst nicht 700/800: Syne wird mit dem Gewicht breiter, die Grenze „extrabreit“ aus Runde 4 bleibt gewahrt), Onest 400/500 für Text und Titel der Beiträge (18 px Fließtext), JetBrains Mono 500 nur für Zahlen, die man abliest: Datum im Kalender, Werbemaße in Pixeln, Schrittnummern. Alle OFL, selbst gehostet in `schriften/` mit Lizenzdateien.
- **Chrome** · nav: Masthead, Logo über einem 2 px Tintenstreifen, eine Zeile Rubriken links und Dienste (Termine, Kino, Verzeichnis) rechts hinter einer Haarlinie; am Handy zwei Zeilen, nichts versteckt · footer: Kolophon (Logo, eine Linkzeile, Bildnachweise der Seite, Platzhalter Impressum)
- **Hero** · Stage gespiegelt: Foto auf 7 Spalten, Aufmacher auf 5 Spalten hinter einer Fuge; Unterseiten mit Banner-Kopf (h1 und ein Satz)
- **Signatur** · die Fuge: Tintenstreifen, die Felder ungleicher Breite (7/5, 5/7, 5/4/3) trennen, statt Karten im Raster
- **Karten** · Prüfung ehrlich: Die weißen Karten mit harter Kante kippen bei Beitragslisten sofort in das abgelehnte Kartenraster (Runde 3 und 5–7). Deshalb gibt es **keine Beitragskarten**. Die eine weiße Karte mit harter Kante (12 px Versatz) bleibt dem vorbehalten, was der Leser ausfüllt: Termin einreichen, Buchung, Kontakt, Bestätigung („Form as a request card“ aus dem Theme).
- **Range des Themes** · Spezifikationstabelle für Termine, Kino, Verzeichnis und Werbeplätze; die eine Zahl auf dem Tintenband (11 Kinos); Schritte an Fugen als echtes `<ol>`; Auswahl als randscharfe, aneinanderstoßende Zellen
- **Sections (Start)** · Aufmacher · Die nächsten Feste (Tabelle) · Nachrichten (Feld 7/5) · Kino auf dem Tintenband · Tempel, Vereine und Schulen (Feld 5/7) · Anzeige im Papier-Well · Küche | Kultur und Sport (Feld 7/5) · Fuß
- **Material** · echt: 20 Rückblick-Beiträge mit Commons-Bildern und Nachweis, 62 datierte Einträge aus `docs/redaktion/rueckblick-2026.md`, Kino und Basel-Termin aus `inhalte.json`, THADAM Bern (Radar-Entwurf 4), Werbeplätze aus `ads.php`, WhatsApp-Kanal aus den Standards des Plugins · Bilder: nur `design/inhalte/rueckblick/bilder/` · fehlt (sichtbare Platzhalter): Preise, Kontaktdaten der Redaktion, Impressum, Einwilligungstext, Verkaufsbedingungen, Vorgangsnummer, Kontaktdaten der Verzeichnis-Einträge
- **Sweep (r1)** · siehe „Überarbeitung nach Kritik r1“ unten; dort stehen die geltenden Picks und Ergebnisse

## Seiten

| Datei | Inhalt |
|---|---|
| `index.html` | Startseite |
| `rubrik.html`, `rubrik-2.html` | Rubrik Community mit Bildern und Seitennavigation (4 + 2 Beiträge; mehr Community-Beiträge gibt es im Material nicht) |
| `artikel.html` | Deepavali (Beitrag 30) mit Bildnachweis, Anzeige nach dem zweiten Absatz, Festkalender am Rand, Teilen per WhatsApp, Weiterlesen |
| `artikel-<id>.html` | die 19 übrigen Rückblick-Beiträge (damit jeder Link ein Ziel hat) |
| `termine.html` | Als Nächstes (15.11., 21.11., 13.12.), darunter das Jahr 2026 nach Monaten mit Sprungzellen und Zeile „Heute“ |
| `kino.html` | Kino nach Stadt (Stand 9.11.), die zwei Filme auf dem Tintenband, Kinojahr 2026 |
| `verzeichnis.html` | Suche, Filter Art (mit Anzahl) und Ort (Land, Bundesland/Kanton, Stadt), 12 Einträge als Tabelle, Premium oben, leerer Zustand „Dienstleister“ |
| `verzeichnis-eintrag.html` | Profil Sri Ganesha Hindu Temple mit Premium-Marke (als Darstellungsbeispiel gekennzeichnet) |
| `verzeichnis-<slug>.html` | die 11 übrigen Profile |
| `einreichen.html` | Formular „Termin einreichen“ mit allen Feldern aus §12, Bildrecht, verstecktem Feld, Einwilligung |
| `einreichen-bestaetigung.html` | Zustand nach dem Absenden (Vorgangsnummer als Platzhalter, keine E-Mail) |
| `werben.html` | sechs Plätze mit Maßen, „Preis folgt“, die Formate maßstabsgetreu als Diagramm, Ablauf in fünf Schritten |
| `buchen.html` | Buchung in fünf Schritten: Platz und Laufzeit, Startdatum mit Kalender (gesperrt, belegt als Beispiel, gewählter Zeitraum), Angaben, Werbemittel-Upload je Maß, Zusammenfassung und Weiter zu Stripe |
| `kontakt.html` | Kontaktwege (Platzhalter) und Formular „Nachricht“ |

Verzeichnis: nur Einrichtungen aus den Beiträgen (Name, Stadt, Art; Bundesland/Kanton aus der Stadt), keine
erfundenen Kontaktdaten. Formulare senden nichts (`data-endpoint=""`; die Seite sagt „Nichts gesendet“).

## Prüfung

- `sloplint --genre editorial` statisch über alle zwölf Hauptseiten und `terrazzo.css`: **0 FAIL, 0 WARN**, F7 beantwortet.
- `sloplint` mit Render-Tier über `http://127.0.0.1:8944/…` (alle zwölf Seiten): **0 FAIL, 0 REFLEX, 0 WARN**;
  Hinweise (NOTE 58) zu Wortzahlen: Nachrichten- und Kalenderseiten sind von Natur aus dicht, Texte unverändert
  (`copy: verbatim`).
- `node tools/shots.mjs` bei 390/820/1280 für 14 Seiten (42 Aufnahmen, `shots/`): **0 Fehler**, kein seitliches
  Scrollen, keine Konsolenfehler, alle Schriften geladen. Kleine Tippflächen nur noch die unsichtbaren Radio-
  und Kontrollkästchen (1 × 1 px), deren Beschriftung die 44 px große Fläche ist.
- Fließtext 18 px; Tinte auf Papier 16,7:1, gedämpftes Grau 6,7:1, Logo-Rot auf Papier 5,8:1 (gerechnet aus den Token-Werten).

## Schwächen (je ein Satz)

- Syne bleibt eine eigenwillige Kopfschrift; ob ihre breiten Formen (besonders die Ziffern „2026“, „11“) für ältere Leser und für Luis „hochwertig“ statt „Effekt“ lesen, muss die Prüfung zeigen.
- Die Fuge ist nah an einer klassischen Zeitungsspaltenlinie; die Linie ist ruhig, aber ihre Eigenheit hängt an Feinheiten (ungleiche Felder, 2 px Tinte), die auf dem Handy zu waagrechten Strichen zusammenfallen.
- Das Tintenband mit „11 Kinos“ erscheint auf Start- und Kinoseite; die große Zahl ist dieselbe Tatsache zweimal.
- Die Rubrikseite hat mit sechs Beiträgen zwei dünne Seiten (4 und 2); die Seitennavigation ist echt, wirkt mit so wenig Material aber konstruiert.
- „Weiterlesen“ zeigt drei Bilder in ungleich breiten Feldern mit ungleich hohen Bildern; das ist gewollt (keine gleichen Kacheln), kann aber unruhig wirken.
- Premium, belegte Buchungstage und die Vorgangsnummer sind Darstellungsbeispiele bzw. Platzhalter und als solche gekennzeichnet; ein echter Premium-Eintrag fehlt.
- Die Render-Aufnahmen von sloplint landen im gemeinsamen Ordner `/home/user/Tamil/.hallmark/shots/`; meine habe ich danach dort wieder entfernt, die Belege liegen in `shots/` dieses Ordners.

## Neu bauen

`python3 design/richtungen/hm-terrazzo/bauen.py` vom Repo-Root (liest `design/inhalte/` und
`docs/redaktion/rueckblick-2026.md`, schreibt alle HTML-Seiten, kopiert Bilder und Logo nach `bilder/`).
Stylesheet: `terrazzo.css` (Stempel, Ausnahmen) über `tokens.css` und `base.css` (Hallmark-Scaffold, Farben angepasst).

## Überarbeitung nach Kritik r1 (`design/kritik/hm-terrazzo-r1.md`)

Geltende Picks nach der Überarbeitung (ersetzen oben, wo sie abweichen):

- **Schrift** · Köpfe in **Wix Madefor Display 600** (OFL, selbst gehostet, `schriften/wix-madefor-display-OFL.txt`), Text in Onest 400/500. Grund: Die Leser sind Eltern und Großeltern ebenso wie Gen Z, am Handy. Wix Madefor wurde für das Lesen am Bildschirm gezeichnet: normale Breite, offene Formen, eindeutige Ziffern (1, 7) für Daten. Sie steht weder auf der impeccable-Liste (Syne steht dort) noch auf der Liste der verbrannten Schriften. Drei Gewichte auf der Seite: 400, 500, 600.
- **Keine dritte Familie** · JetBrains Mono ist entfernt; Daten und Maße in Onest mit `tabular-nums`. Ein Datumsformat für Listen („So, 15. Nov.“), eines für Beiträge („8. November 2026“).
- **Signatur: der Feldplan** · Jede Inhaltsart hat auf der Startseite ihr eigenes Feld und ihre eigene Form, getrennt durch 2-px-Fugen: Aufmacher mit großem Bild (8 Spalten) neben dem Feld „Nachrichten“ nur mit Text (4 Spalten); „Die nächsten Feste“ als Datumsliste neben „Kino diese Woche“ als Film mit Städten (7/5); Community als Hochformat mit Liste (5/7); Küche mit zwei kleinen Bildern und Liste neben „Kultur und Sport“ ohne Bild (7/5).
- **Eigener Kopf je Seitentyp** · Termine: der nächste Termin groß als Datum neben dem Titel; Kino: der Satz mit beiden Filmen und die Städteliste; Verzeichnis: die Suche im Kopf; Werben: die Formate maßstabsgetreu als Bild des Kopfes; Rubrik: Zahl der Beiträge; Artikel und Formulare wie bisher.
- **Sweep** · statisch 0 FAIL, 0 WARN, F7 beantwortet; Render über `http://127.0.0.1:8944` (12 Seiten) 0 FAIL, 0 REFLEX, 0 WARN; Ausnahmen im Stempel: 44c, 49b, 59, 77, 78, 79 (64 entfällt mit Mono); `tools/shots.mjs` 14 Seiten × 390/820/1280: 0 Fehler.

| P1 aus r1 | Was geändert ist |
|---|---|
| 1 Seitenstreifen am aktiven Buchungsschritt | Schnitt 600 und 2-px-Tintenlinie unten, kein farbiger Rand |
| 2 Syne auf der Ausschlussliste | Wix Madefor Display (siehe oben) |
| 3 Dritte Familie | JetBrains Mono entfernt, Onest mit Tabellenziffern |
| 4 index 390 mit einer Geschichte | Navigation einzeilig (waagrecht scrollbar, Termine, Kino und Verzeichnis zuerst), Aufmacherbild 16:9, Vorspann am Handy auf zwei Zeilen gekürzt; im ersten Bildschirm (390 × 844) stehen der Aufmacher, der Kopf „Nachrichten“ und drei weitere Schlagzeilen |
| 5 Dunkles Kino-Band, Ziffer „11“ | Band und Ziffer gestrichen; Kino als linierte Liste auf hellem Grund, „11 Kinos“ in Textgröße; Kinoseite nur noch nach Stadt, Land einmal im Kopf |
| 6 Rosa Flächen | `--color-accent-soft` gestrichen; Premium als Wort in Rot und 2-px-Tintenlinie um die Zeile; Tabellenzeilen ohne Hover-Fläche |
| 7 Knopf „Beitrag lesen“ | gestrichen; Schlagzeile und Bild verlinken, WhatsApp als schlichter Link |
| 8 Ein Baustein für alles | Feldplan und eigene Köpfe (siehe oben) |

Zusätzlich aus P2/P3: kein harter Versatzschatten mehr an Formularkarten (nur 2-px-Rand); Hinweistexte 17 px; Monate
als Textlinks in einer Zeile; Metazeilen als „Datum in Ort“ statt Kommaliste; Kinojahr-Bild bleibt beim Kinojahr.

**Ehrlich zur Idee:** Das Terrazzo trägt nur als **Ordnung**, nicht als Oberfläche. Sichtbar sind Felder ungleicher
Größe, getrennt durch Tintenfugen, mit je eigener Form für jede Inhaltsart. Eine Körnung, ein Material oder ein
Bildausschnitt, der an Terrazzo erinnert, kommt bewusst nicht vor (Muster und Effekte sind ausgeschlossen). Damit
steht die Linie einer guten Zeitungsseite mit Spaltenlinien näher als einem Boden. Der Name ist eher Arbeitstitel
als sichtbares Merkmal. Wer ein Bild des Bodens erwartet, wird es nicht finden.

Offen: Wix Madefor ist ruhig, aber eher neutral; ob die Seite damit „gemacht“ statt „generiert“ wirkt, muss die
nächste Prüfung zeigen. Die Rubrik bleibt mit sechs Beiträgen dünn (4 + 2). Premium und belegte Buchungstage sind
weiter Darstellungsbeispiele.

## Überarbeitung nach r2 (`design/kritik/hm-terrazzo-r2.md`)

| P1 aus r2 | Was geändert ist |
|---|---|
| 1 Zeilenlänge 81 bis 89 Zeichen | Maß in rem statt ch: Fließtext, Anreißer und Kopfsätze `max-width: 34rem` (etwa 70 Zeichen bei 18 px Onest), Vorspann `36rem` |
| 2 Tempelspitze abgeschnitten | Bildfokus je Bild im Bauskript (`FOKUS`, für Beitrag 30 und 49 `50% 8%`) statt Mittenausschnitt |
| 3 Idee nur Spaltenlinie | neue Signatur **Kalenderboden** (siehe unten); seitenweite Ausnahmen von 6 auf 4 abgebaut (59 und 77 entfallen) |
| 4 Startseite 390 | Vorspann am Handy auf den ersten vollständigen Satz gekürzt („Am 8. November war Deepavali.“, Kürzung am Satzende wie in `inhalte.json` erlaubt, ohne „…“), Orte am Handy aus der Metazeile, Feldkopf „Nachrichten“ am Handy nur für Screenreader; im ersten Bildschirm (390 × 844) stehen der Aufmacher und zwei vollständige Schlagzeilen |

**Kalenderboden.** Der laufende Monat liegt als Feld aus quadratischen Fliesen, getrennt durch 2-px-Tintenfugen;
Festtage sind in Tinte ausgelegt und verlinkt (8. Deepavali, 15. Düsseldorf, 21. Basel), heute trägt eine rote
Linie, leere Fliesen vor und nach dem Monat sind Papiergrau. Auf der Startseite steht er im ersten Bildschirm als
zweiter Stein neben dem Aufmacher (ein hoher Stein links, rechts der Kalender mit den Festen des Monats), auf der
Festkalender-Seite als November und Dezember im Kopf. Hier trägt die Terrazzo-Idee zum ersten Mal sichtbar: Fliesen
und Fugen sind die Form des Inhalts selbst (Tage, Feste), nicht Schmuck. Am Handy folgt der Kalender nach den
Nachrichten, damit der erste Bildschirm zwei Geschichten zeigt (Umordnung per CSS, Reihenfolge im Quelltext bleibt).

Dazu aus P2/P3: keine Doppelung (Maneez nur unter Nachrichten), Listen nach Datum (neueste zuerst), Ortsregel
„Stadt allein, Land nur außerhalb Deutschlands“, Billboard-Eigenwerbung von der Startseite genommen, die Eigenanzeige
im Artikel heißt jetzt „Eigenanzeige von tamil.de“; Nachrichten und Kino teilen sich das zweite Feld.

**Sweep r2:** sloplint statisch 0 FAIL, 0 WARN (F7 beantwortet); Render über `http://127.0.0.1:8944` (12 Seiten) 0 FAIL,
0 REFLEX, 0 WARN; verbleibende Ausnahmen im Stempel: 44c, 49b, 78, 79. `tools/shots.mjs` 14 Seiten × 390/820/1280: 0 Fehler.

**Offen:** Der Kalenderboden ist ein echtes Kalenderraster aus gleichen Feldern; das ist inhaltlich begründet, kann aber
für ein ungeübtes Auge wie ein Kartenraster wirken. Wix Madefor bleibt eine Katalog-Schrift (Hallmark „Dusk“); ihre
Wahl ist aus dem Leser begründet, nicht neu gefunden. Die Zeilenlänge habe ich gerechnet, nicht nachgemessen.

## Überarbeitung nach r3 (`design/kritik/hm-terrazzo-r3.md`)

| Befund | Was geändert ist |
|---|---|
| P1-1 Kalenderboden am Handy zu tief, wie ein Datumswähler, 42 Zellen für 3 Daten | Am Handy zeigt das Kalenderfeld nur den **Mini-Boden**: die kommenden Feste als je eine Fliese (Tag und Monat in Tinte, rote Fuge oben) mit Titel, Wochentag und Ort; die Monatsfliesen bleiben dem Desktop. Er steht jetzt direkt nach den Nachrichten und vor dem Kino (im zweiten Bildschirm statt im dritten). Festfliesen tragen oben eine rote Fuge; im Buchungskalender ist die Auswahl nur noch ein Tintenrahmen, keine Tintenfläche. |
| P1-2 termine.html ohne Termin im ersten Bildschirm | „Als Nächstes“ steht direkt unter dem Kopf (390: ab etwa y 380); die Monatsfliesen November und Dezember folgen darunter. |
| P2 Kalenderzellen springen nicht | Kommende Festtage führen zu `termine.html#t-<Datum>`, die Zeilen tragen diese Anker; vergangene zum Beitrag. |
| P2 „Städte“ im Kino ohne Funktion | jede Stadt springt zu ihrer Zeile (`#stadt-…`). |
| P2 Köpfe vertikal zentriert | Köpfe oben bündig (`align-items: start`, `justify-content: flex-start`). |

Nicht gelöst: Am Desktop (1280 × 800) steht neben dem Aufmacher weiterhin nur der Kalenderboden, keine zweite
Geschichte; die Nachrichten beginnen unter dem Falz.

**Sweep r3:** sloplint statisch 0 FAIL, 0 WARN; Render über `http://127.0.0.1:8944` (12 Seiten) 0 FAIL, 0 REFLEX, 0 WARN
(Ausnahmen im Stempel: 44c, 49b, 78, 79); `tools/shots.mjs` 14 Seiten × 390/820/1280: 0 Fehler, keine Hinweise.
