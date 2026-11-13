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
- **Schrift** · Syne 600 für Köpfe (bewusst nicht 700/800: Syne wird mit dem Gewicht breiter, die Grenze „extrabreit“ aus Runde 4 bleibt gewahrt), Onest 400/500 für Text und Titel der Beiträge (18 px Fließtext), JetBrains Mono 500 nur für Zahlen, die man abliest: Datum im Kalender, Werbemaße in Pixeln, Schrittnummern. Alle OFL, selbst gehostet in `schriften/` mit Lizenzdateien.
- **Chrome** · nav: Masthead, Logo über einem 2 px Tintenstreifen, eine Zeile Rubriken links und Dienste (Termine, Kino, Verzeichnis) rechts hinter einer Haarlinie; am Handy zwei Zeilen, nichts versteckt · footer: Kolophon (Logo, eine Linkzeile, Bildnachweise der Seite, Platzhalter Impressum)
- **Hero** · Stage gespiegelt: Foto auf 7 Spalten, Aufmacher auf 5 Spalten hinter einer Fuge; Unterseiten mit Banner-Kopf (h1 und ein Satz)
- **Signatur** · die Fuge: Tintenstreifen, die Felder ungleicher Breite (7/5, 5/7, 5/4/3) trennen, statt Karten im Raster
- **Karten** · Prüfung ehrlich: Die weißen Karten mit harter Kante kippen bei Beitragslisten sofort in das abgelehnte Kartenraster (Runde 3 und 5–7). Deshalb gibt es **keine Beitragskarten**. Die eine weiße Karte mit harter Kante (12 px Versatz) bleibt dem vorbehalten, was der Leser ausfüllt: Termin einreichen, Buchung, Kontakt, Bestätigung („Form as a request card“ aus dem Theme).
- **Range des Themes** · Spezifikationstabelle für Termine, Kino, Verzeichnis und Werbeplätze; die eine Zahl auf dem Tintenband (11 Kinos); Schritte an Fugen als echtes `<ol>`; Auswahl als randscharfe, aneinanderstoßende Zellen
- **Sections (Start)** · Aufmacher · Die nächsten Feste (Tabelle) · Nachrichten (Feld 7/5) · Kino auf dem Tintenband · Tempel, Vereine und Schulen (Feld 5/7) · Anzeige im Papier-Well · Küche | Kultur und Sport (Feld 7/5) · Fuß
- **Material** · echt: 20 Rückblick-Beiträge mit Commons-Bildern und Nachweis, 62 datierte Einträge aus `docs/redaktion/rueckblick-2026.md`, Kino und Basel-Termin aus `inhalte.json`, THADAM Bern (Radar-Entwurf 4), Werbeplätze aus `ads.php`, WhatsApp-Kanal aus den Standards des Plugins · Bilder: nur `design/inhalte/rueckblick/bilder/` · fehlt (sichtbare Platzhalter): Preise, Kontaktdaten der Redaktion, Impressum, Einwilligungstext, Verkaufsbedingungen, Vorgangsnummer, Kontaktdaten der Verzeichnis-Einträge
- **Sweep** · Floor 0 FAIL · Reflex 0 offen (8 begründet im Stempel ausgenommen: 44c, 49b, 59, 64, 77, 78, 79; 77 als WARN auf Unterseiten verworfen) · F7 beantwortet · Prüfung aus frischem Kontext: steht aus (Hauptsitzung)

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
- Fließtext 18 px; Tinte auf Papier etwa 16:1, gedämpftes Grau etwa 7:1, Logo-Rot auf Papier etwa 6:1.

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
