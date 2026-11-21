# Design – Tamil.de: „klar2“ mit Bewegung D

> **Stand 16.11.2026:** Richtung `klar2` und Bewegung D gewählt von Luis (`docs/abnahme/2026-11-16-G2-klar2.md`,
> `docs/entscheidungen.md`). Eine Probeseite und Tor G3 entfallen; das Theme `wordpress/themes/tamil` (Version 3.0)
> wird direkt umgebaut und auf dem Testsystem mit echten Beiträgen abgenommen. Quellen: `design/richtungen/klar2/`
> (Startseite, Artikel, CSS), `design/richtungen/klar2/bewegung/` (Variante D), Regeln in `design/brief.md` §10.
> Tokens: `design/tokens.css`.
>
> **Stand 19.11.2026 (Theme 3.4.0):** Markenfarben von Luis (`docs/abnahme/2026-11-19-signature.md`, Branding Master
> Handoff v1.1): Weiß, Titan Red dominant, Impact Red als Akzent, Schwarz für Schrift, Gewichtung „Red Dominance /
> Power“. Sie ersetzen die Farbwerte von klar2 und die Regel „Rot nur als Akzent“. Das Logo bleibt unverändert.
>
> **Stand 19.11.2026 (Theme 3.5.0):** Das Signet „Tamil Dots 04A“ steht als Hintergrund im Theme (Abschnitt „Signet“).
> Freigegeben ist die Form (Luis, 19.11.) und die Platzierungen im Theme 3.5.0 (Luis, 19.11.,
> `docs/abnahme/2026-11-19-signature.md`).
>
> **Stand 20.11.2026 (Theme 3.6.0):** Entscheidungen von Luis (`docs/abnahme/2026-11-20-logo-startseite.md`,
> `docs/entscheidungen.md`): **neues Logo** genau so übernommen (Abschnitt „Logo“; hebt für dieses Logo „das Logo bleibt
> unverändert“ aus dem Branding-Handoff auf), **Startseite „Text auf Bild“** (jeder Beitrag als Bildkarte mit Titel im
> Foto) und der **Punktbogen an jedem Beitrag** (Abschnitt „Signet“). Freigegeben von Luis am 20.11.
>
> **Stand 20.11.2026 (Theme 3.7.0):** **Jede Meldung als Karte** (Luis, 20.11.: „auf jeder meldung tamil dots und
> schrift auf der karte“): Jeder Beitrags-Anreißer der Website ist eine Bildkarte mit Titel im Foto und Punktbogen –
> nicht nur auf der Startseite (Abschnitt „Bausteine“, „Seiten“). Freigabe ausstehend.

> **Stand 21.11.2026 (Theme 3.9.0):** Auftrag von Luis „tamil logo beim runterscrollen in der leitse … bilder nicht
> alle eckig also die karten auf einer höhe“, in der Nacht ohne Rückfrage umgesetzt (`docs/entscheidungen.md`, 21.11.):
> **Logo im stehenden Band** (Abschnitt „Bausteine“), **abgerundete Ecken** und **Karten einer Reihe gleich hoch**
> (Abschnitt „Ecken und Reihen“).

> **Stand 21.11.2026 (Theme 3.10.0):** **Wow-Aufmacher „Punkt für Punkt zum Bild“** auf der Startseite (Abschnitt
> „Wow-Aufmacher“), Logo-Fläche im Band mit 3 px Impact unten, Terminkarten mit gleich hohen Bildflächen.

> **Stand 21.11.2026 (Theme 3.11.0):** Korrekturen aus der unabhängigen Kritik: Wow-Aufmacher zeigt sofort das Foto,
> kurzer Titel, halber Weg, eingebettet in die Seite; Rubrikblöcke im Wechsel aus Reihe und Bühne; runde Ecken auch an
> Bedienelementen.

**Idee:** eine ruhige Nachrichtenseite mit mehr Bild und mehr Bühne. Vorbild BBC News für Kopf und Ordnung,
tagesschau für den Titel im Bild, Spiegel für die Bildblöcke. Das Wow kommt aus Fotos, Fläche und dem Wechsel von
Weiß und Titan Red, nicht aus Schriftgröße oder Effekten.

## Farben

Markenfarben von Luis (19.11.2026). Richtwert der Gewichtung: **50 % Weiß, 35 % Titan Red, 10 % Impact Red, 5 %
Schwarz**. Die vier Markenwerte stehen als Hex im CSS, damit sie exakt so erscheinen (oklch nur im Kommentar). Keine
weiteren Markenfarben (kein Orange, Pink, Gold, Violett); Grauwerte und die Fehlerfarbe sind neutral bzw. semantisch
benannt. Quelle: `theme.css` (Abschnitt Tokens), `design/tokens.css`; `theme.json` trägt dieselben Hex-Werte.

| Token | Wert | Rolle |
|---|---|---|
| `--tamil-color-background` (`grund`, `weiss`) | `#FFFFFF` | Seitengrund |
| `--tamil-color-primary` (`titan`) | `#660000` | **dominant:** Rubrikband, „Diese Woche“, Kino „Im Programm“, Termine „Ab heute“, Knöpfe, aktive Filter und Seitenzahl, Linien über Blöcken (`linie-stark`), Fokusrahmen (`fokus`), Fuß (Linie oben, Zeile mit Rechtlichem), Schild „Symbolbild“, Icon und Browserleiste |
| `--tamil-color-accent` (`rot`) | `#B30000` | **Akzent:** Rubrik in der Dachzeile, Top-News, Schild „Neu“, Links im Text, Leselinie, Markierung der aktiven Rubrik, Überfahren im Band und an Knöpfen, Linie unter Titeln auf Titan (`linie-titan`) |
| `--tamil-color-text` (`tinte`) | `#000000` | Fließtext und Überschriften auf Weiß |
| `titan-tief` | `#520000` | Ableitung (Titan mit 20 % Schwarz): Bildkacheln auf Titan |
| `neutral-flaeche` (`flaeche`) | `#F2F2F2` | Bildgrund beim Laden, Hinweise, Meldungen der Formulare |
| `neutral-linie` (`linie`) | `#D9D9D9` | Trennlinien zwischen Zeilen |
| `neutral-leise` (`leise`) | `#555555` | Datum, Orte, Nachweise, Beschriftungen, „Anzeige“ |
| `neutral-hell-leise` (`hell-leise`) | `#CCCCCC` | Nebeninfos auf Titan und im Bild |
| `status-fehler` | = Impact | Formularfehler (Text, Rand) |
| Signet | Titan, Impact, Weiß mit Deckkraft | „Tamil Dots 04A“ als Hintergrund (Abschnitt „Signet“); keine eigenen Farbwerte |

Kontraste (WCAG 2.2 AA): Weiß auf Titan 13,4 : 1, Weiß auf Impact 7,2 : 1, Impact auf Weiß 7,2 : 1, Titan auf Weiß
13,4 : 1, `#555` auf Weiß 7,5 : 1, `#CCC` auf Titan 8,4 : 1. Die aktive Rubrik ist in Impact markiert und trägt 3 px
Weiß darunter, weil Impact gegen Titan nur 1,9 : 1 hat; der Zustand hängt so nicht am Rotton. Der einzige Verlauf liegt
unter Schrift im Bild: durchsichtig nach Schwarz, auf Titan-Flächen nach Titan. Ecken seit 3.9.0 gerundet (10 px an
Karten und Bildern, 6 px an kleinen Kacheln und Bedienelementen, Abschnitt „Ecken und Reihen“); keine Schatten, nichts
gedreht. Rot als Schrift nie über 20 px; im Bild und auf Titan ist die Dachzeile weiß. Anzeigen bleiben neutral
(Schwarz), damit sie sich vom redaktionellen Teil abheben.

## Logo (seit 20.11.2026)

Das neue Logo von Luis, **genau so übernommen**, auch die Schreibweise: „tamil“ in Rot, „.de“ in Dunkelgrau, darunter
„portal • lifestyle • entertainment“ und „& KOMMUNITYPLATTFORM DER COMMUNITY“. Kein Neuzeichnen, kein Vektor-Nachbau,
Farben aus der Vorlage.

- **Quelle:** `design/inhalte/logo-2026-11.webp` (1969 × 799, weißer Grund). `design/inhalte/logo_freistellen.py`
  stellt den Grund je Bildpunkt frei (Lage zwischen Weiß und der Druckfarbe = Deckkraft; voll deckende Punkte behalten
  ihre Farbe) und schneidet ohne Rand zu. Auf Weiß weicht das Ergebnis im Mittel um 1 von 255 von der Quelle ab.
- **Dateien:** `design/inhalte/logo.png` (1920 × 695, Social und Druck), im Theme `assets/img/logo.webp` (199 × 72),
  `logo-2x.webp` (398 × 144, unter 30 KB) per `srcset`, `logo.png` (398 × 144) für Schema und als Rückfall.
- **Kopf:** 56 / 64 / 72 px hoch (Handy / Tablet / Desktop), damit „portal • lifestyle • entertainment“ lesbar bleibt
  (die Zeile ist rund ein Sechstel der Logohöhe); die Zeile „& KOMMUNITYPLATTFORM …“ ist im Kopf nur angedeutet, so
  ist sie in der Vorlage angelegt. **Fuß:** 56 px. `alt="tamil.de"`, Breite und Höhe aus der Datei.
- **Teilenbild** `assets/img/teilen.jpg` (1200 × 630, `design/inhalte/teilen_bauen.mjs`) und `screenshot.jpg` zeigen
  das neue Logo; die Social-Muster (`design/social/`) ebenso.
- **Favicon und App-Icon „t.“** bleiben vorerst (offene Frage an Luis).
- Signet und Logo bleiben getrennt: der Punktbogen steht nie am, im oder hinter dem Logo.

## Schrift

Eine Familie: **Libre Franklin** (variabel 100–900, OFL, selbst gehostet, nur der lateinische Teil wird vorgeladen).
Tamil fällt über `unicode-range` und `:lang(ta)` auf die Tamil-Untermenge von **Catamaran**.

| Rolle | Größe Handy / Desktop | Gewicht |
|---|---|---|
| Aufmacher (Titel im Bild) | 30 / 34 (Tablet) / 40 px | 650 |
| Artikeltitel | 28 / 38 px | 650 |
| Seitenkopf | 28 / 34 px | 700 |
| Titel große Kachel | 22 / 26 px | 650 |
| Titel Bildkarte | 19–21 / 17–20 px, ausgeglichen, höchstens 4 Zeilen | 650 |
| Nebenstück, Blocktitel | 19 / 20 px | 650 / 700 |
| Meldung, Listenzeile | 17 / 19 px | 600 |
| Fließtext im Artikel | 18 / 19 px, Zeilenhöhe 1,6 | 400 |
| Text sonst | 17 px | 400 |
| Dachzeile „Rubrik \| Datum“, Nachweise | 13 px | 600 / 400 |

Keine Versalien, keine Kursive. Der Artikel steht in einer Spalte von höchstens 560 px (am Tablet 600 px mit
gemeinsamer Kante für Kopf, Bild und Text), höchstens 70 Zeichen je Zeile.

## Bausteine

- **Kopf:** Kopfzeile (Datum, Top-News: Schild „Neu“ in Impact, die Überschriften der neuesten Beiträge in Impact, ab 1024 px zwei mit
  feiner Linie, darunter einer, einzeilig mit Auslassung, am Handy ohne Datum; Suche), Logo 56/64/72 px auf
  weißem Grund (Abschnitt „Logo“), Rubrikband in Titan mit weißer Schrift (`nav`, 46/48 px, steht beim Scrollen), aktive Rubrik in
  Impact mit Gewicht 600 und 3 px Weiß darunter, beim Überfahren Impact, Fokusring weiß, am Handy seitlich mit
  Einrasten; „Mehr“ am Ende mit Suche, Diensten und Social. Seit 3.9.0: Ist der Kopf aus dem Bild, zeigt das stehende
  Band links das ganze Logo klein (30/34 px hoch) auf einer weißen Fläche bündig am Rand in voller Bandhöhe (104/120 px
  breit), als Link zur Startseite; die Rubriken rücken zur Seite (transform, kein Springen), Einblenden 0,2 s nur ohne
  reduzierte Bewegung; oben auf der Seite ist es weg und nicht fokussierbar.
- **Anreißer:** ein Link um Bild und Text; Dachzeile „Rubrik | Datum“; Bild füllt seinen Rahmen. Formate: 4:3
  (Aufmacher, große Kachel in „Diese Woche“, Viererreihen am Desktop), 16:9 (Bildkarten, Rubrikkacheln, Küche groß),
  8:3 (kleine Kacheln). Beim Überfahren Zoom 1,03 in 0,35 s, Titel unterstrichen.
- **Bilderpflicht** (Luis, 17.11.): Jeder Anreißer, jede Listenzeile, Kachel, jedes Suchergebnis, „Weiterlesen“ und
  jeder Kino- und Termineintrag zeigt ein echtes Bild; nichts nur als Text. Ausgenommen sind Rubrikband, Top-News im
  Kopf, Fußlisten, Formulare und reine Textseiten. Bildkette an einer Stelle (`inc/bildkette.php`): eigenes Foto (Titelkarten nie;
  Bänder über 2,5:1 werden beschnitten, Nachweis „zugeschnitten“) → erstes Bild aus dem Text ab 600 px → bei Kino und
  Terminen das Foto eines anderen Beitrags zum selben Film bzw. zur selben Veranstaltung (ohne Schild) → Symbolbild
  aus dem Rubrik-Pool (Commons-Fotos und seit 3.13.0 KI-Symbolbilder, je Rubrik abwechselnd; je Seite reihum
  vergeben, damit kein Ersatzbild auf einer Seite doppelt erscheint; Kino und Events mit eigenen Pools, nie Kirchen
  oder Rathäuser für Kino und Entertainment; Nachrichten nie mit KI-Bild; Schild „Symbolbild“ oben rechts ab 150 px
  Rahmenbreite, darunter ein „S“; „Symbolbild,“ vor dem Commons-Nachweis, KI-Bilder genau „Symbolbild: KI-generiert ·
  Tamil.de“, auch im Fuß). Die KI-Bilder haben das Motiv oben links der Mitte und unten eine ruhige, dunkle Fläche:
  der Punktbogen ist auf allen weiß (Ecke gemessen 0,001 bis 0,135, Grenze 0,3). Nachweise entstehen an
  einer Stelle (`tamil_nachweis_bauen()`): Urheber verlinkt auf die Dateiseite, Lizenz auf den Lizenztext,
  „zugeschnitten“ bei freien Lizenzen und Bändern. Prüfung: `node wordpress/dev/bilder_pflicht.mjs`.
- **Bild mit Titel im Bild:** Aufmacher, große Kacheln und seit 3.6.0 **jede Bildkarte der Startseite** („Text auf
  Bild“, unten); das Format ist nur Mindesthöhe, längere Titel machen die Kachel höher statt abzuschneiden (Bildkarten:
  höchstens vier Zeilen); Fokus als Rahmen nach innen. Rechts unten hält der Text den Platz für den Punktbogen frei.
- **Bildkarte „Text auf Bild“** (Luis 20.11.2026; seit 3.7.0 **jeder Beitrags-Anreißer der Website**, nicht nur die
  Startseite): Foto 16:9 (am Desktop in Viererreihen 4:3), darauf auf
  dem Verlauf nach Schwarz die Dachzeile „Rubrik | Datum“ und der Titel, weiß, ausgeglichen umbrochen
  (`text-wrap: balance`). Der Verlauf erreicht 66 % Schwarz (auf Titan 86 % Titan), bevor die Schrift beginnt (N-12, 21.11.: auf reinem Weiß 7,2 : 1, schlechtester Titel der Startseite 7,6 : 1); gemessen
  hält jede Textzeile im 5-%-Quantil mindestens 5,9 : 1 (Ziel 4,5 : 1). Das Foto sitzt höher im Rahmen (Position
  50 % 28 %), damit Gesichter über dem Verlauf bleiben; Pool-Bilder behalten ihren Fokus. Vorspann unter dem Bild
  (drei Zeilen): in Listen und „Weiterlesen“ immer, auf der Startseite nur am Desktop.
- **Kartenraster** (`tamil_zeilen()`, seit 3.7.0 jede Liste von Beiträgen: Rubrik, Suche, Archive, 404, Production,
  Termine, „Aus dem Kinojahr“): Handy eine Spalte, Tablet zwei, Desktop drei; Vorspann und Angaben (Ort, Eintritt)
  unter dem Bild; Suchwort fett in Titel und Vorspann. Die erste Karte im ersten Bildschirm lädt sofort, alle anderen
  mit geringem Vorrang; Karten ab der dritten mit `content-visibility: auto`, wischbare Reihen laden kurz vor dem Bild.
- **Keine Karten** (gewollt, so gezählt): Top-News im Kopf, Rubrikband, Fußlisten, Rubrikkacheln (Navigation),
  Kinotabelle „Nach Stadt“ (ihre Zeilen verlinken auf Kinos, nicht auf Beiträge), Verzeichnis, Anzeigen, Formulare,
  reine Textseiten, der Artikel selbst (Titel über dem Bild). Prüfung: `bilder_pflicht.mjs`, Wert „Titel im Bild“
  (Soll 100 %, Ausnahmen mit Namen).
- **Rubrikkacheln:** Navigation mit Bild (Foto des neuesten Beitrags der Rubrik, sonst das erste Bild ihres Pools),
  Name im Bild.
- **Bildkacheln auf Titan** (`data-grafik`, Grund `titan-tief`): Kino mit Bild 4:3 links (Film, Zahl der Kinos, Städte) und Termine mit
  Bild 16:9 oben (Titel, Datum mit Uhrzeit und Ende als größte Angabe, Ort, Veranstalter, Eintritt, Vorspann); leer
  zeigen sie ein Symbolbild und sagen, wo es weitergeht.
- **Blocktitel:** 19 px, schwarz, 2 px Linie in Titan darüber; Listen mit Linien statt Kästen; Tabellen ebenso
  (Kopflinien in Titan, Zeilenlinien neutral).
- **Knöpfe** nur für Formulare und Bedienung: Titan mit weißer Schrift, beim Überfahren Impact, eckig, 48 px hoch. Sonst unterstrichene Textlinks, 44 px tippbar.
- **Anzeigen:** Label „Anzeige“, je Platz ein benannter Bereich des Plugins; Formate aus
  `tamil_site_werbung_formate()`, dieselbe Fläche für Eigenanzeige (Bildbanner), gebuchte Anzeige und Banner-Code.
  Handy-Leiste 320 × 50 fest unten, erst wenn der erste Abschnitt aus dem Bild ist (spätestens nach einem
  Bildschirm), schließbar, nur unter 768 px Breite und ab 500 px Fensterhöhe.
- **Fuß:** weißer Grund mit 3 px Linie in Titan oben, die Zeile mit Rechtlichem als Band in Titan über die volle Breite; Logo und Unterzeile, Rubriken, Dienste, Social (nur mit Adresse),
  Bildnachweise der Seite, Rechtliches mit Platz für „Cookie-Einstellungen“.

## Seiten

- **Startseite („Text auf Bild“ seit 3.6.0):** jeder Beitrag als Bildkarte mit Titel im Foto. Aufmacher 4:3, am
  Desktop daneben „Weitere Meldungen“ als Stapel von drei Karten 16:9 (so hoch wie der Aufmacher; Handy und Tablet:
  wischbare Reihe, die nächste Karte schaut an), vier Nebenstücke als Karten (Handy untereinander, Tablet 2 × 2,
  Desktop zu viert in 4:3 mit Vorspann), Rubrikkacheln (Navigation, unverändert), Werbeplatz 01, „Diese Woche“ (Kino
  groß 4:3 und klein 8:3, „Im Kino“ mit Zahl der Kinos in der Dachzeile und den Städten darunter, „Termine“ mit dem
  Datum des Termins in der Dachzeile und Ort und Eintritt darunter, alle mit Titel im Bild), „Küche“ (groß 16:9, klein
  8:3 mit Titel im Bild, am Tablet die kleinen 16:9 nebeneinander), Billboard, Rubrikblöcke mit je vier Karten (Handy
  wischbar, Tablet 2 × 2, Desktop zu viert). „Diese Woche“ zeigt nur Aktuelles: Filme mit Spieltagen
  ab heute, Kino-Beiträge der letzten 30 Tage, Termine der nächsten 14 Tage (sonst die nächsten drei); was dort
  steht, kommt oben nicht noch einmal. Ein einzelner Termin über die ganze Breite steht als Band: Bild in
  Dateigröße (höchstens 380 px), Orte und Vorspann mittig daneben (3.12.0, K-13).
- **Artikel:** Dachzeile, Titel, Vorspann, Leiste mit Lesezeit und „Per WhatsApp teilen“, Bild (randlos am Handy) mit
  Nachweis, Text, Termin als Angaben (auch der Infokasten aus dem Import erscheint als Terminkasten, Datum im
  Hausformat, 3.12.0), Quelle, Schlagworte, Teilen als eine Knopfzeile (WhatsApp gefüllt, Facebook, X, Telegram,
  E-Mail, Link kopieren leise; ab 600 px in einer Zeile), Redaktion; Werbeplatz „Im Artikel“ nach dem zweiten Absatz
  (Festlegung F3); Textspalte mittig wie im Entwurf; Werbeplatz 02 ab 1280 px rechts daneben, darunter nach dem Bild;
  „Weiterlesen“ mit vier Bildkarten (Desktop zu viert in 4:3, Tablet 2 × 2, Handy wischbar).
- **Rubrik:** Seitenkopf, Aufmacher mit „Neu in der Rubrik“ daneben (drei Karten 16:9 als Stapel, Handy wischbar),
  „Weitere Beiträge“ als Kartenraster mit Vorspann, Seiten, Kacheln.
- **Kino:** Seitenkopf, Bereich „Im Programm“ in Titan (Filme als Karten mit Titel im Bild), „Nach Stadt“ (Tabelle,
  jede Zeile mit dem Bild des Films), „Aus dem Kinojahr“ (Kartenraster).
- **Termine:** Seitenkopf, Bereich „Ab heute“ in Titan (Termine der nächsten 14 Tage, sonst die nächsten drei; Karten
  mit dem Datum des Termins in der Dachzeile, Ort und Eintritt darunter), „Kommende Termine“ nach Monaten (Kartenraster:
  Datum mit Uhrzeit in der Dachzeile, Ort, Veranstalter, Eintritt unter dem Bild; Filter nach Land und Stadt als Knöpfe
  mit `aria-pressed`, nur mit Skript), „Das Jahr“ (vergangene Termine als Karten, Monate zum Aufklappen).
- **Kontakt:** Formulare des Plugins (Nachricht, Termin, Kooperation, mit Danke-Anzeige), daneben Redaktionsdaten nur
  aus dem Customizer und „Andere Wege“; darunter die Werbeplätze aus dem Plugin mit „Preis: auf Anfrage“. Kein alter
  Seiteninhalt.
- **Tamil TV:** ohne Sender „Tamil TV kommt“ mit Symbolbild; nicht im Band und nicht unter „Mehr“.
- **Verzeichnisprofil** (`single-tamil_vz_eintrag.php`): Dachzeile, Name, Bild mit Nachweis, Profil des Plugins,
  Link zur Karte (OpenStreetMap, nicht eingebettet); ohne Lesezeit und Teilen-Leiste.
- **Impressum, Datenschutz:** außerhalb des Echtbetriebs der Hinweis „Entwurf: Der Text von KBS folgt.“
- **Suche, 404, Seiten, Archive:** Seitenkopf, Blöcke mit Blocktitel, Kartenraster; Seiten in der Artikelspalte,
  Plugin-Inhalte bis 720 px. Bildnachweise im Fuß eingeklappt („Bildnachweise dieser Seite (n)“).

## Signet „Tamil Dots 04A“ (Theme 3.5.0, an jedem Post seit 3.6.0)

Die Form hat Luis am 19.11.2026 freigegeben (`docs/abnahme/2026-11-19-signature.md`, `design/signature/master.svg`,
238 elliptische Punkte); der Abgleich mit Feld A der Originalreferenz ist nicht erfolgt. Die Platzierungen unten sind
im Theme 3.5.0 gebaut und am 19.11. freigegeben; der Bogen an jedem Post (3.6.0) ist zur Freigabe vorgelegt. Das Signet ist das wiedererkennbare Merkmal der
Marke und wird vor allem als Hintergrund eingesetzt.

**Regeln**

- **Nicht das Logo.** Nie am, im, hinter oder verschmolzen mit dem Logo; das Logo bleibt unverändert.
- **Nur in freier Fläche.** Nie hinter Überschriften, Text oder Gesichtern; nicht im Artikeltext, nicht im
  Logobereich. Über Fotos nur als kleiner Bogen in der Bildecke jedes Beitrags („An jedem Post“, unten). Es rahmt, hinterlegt und gliedert und ist von der Kante seines
  Bereichs angeschnitten (rechts, unten, am Fensterrand). Die freie Fläche unter dem Bogen bleibt frei.
- **Form unverändert:** nicht drehen, spiegeln, stauchen; großer Fuß links, Auslauf rechts. Keine Pfeile oder anderen
  Zeichen dazu. Variante C nur als abgeleitete Bewegung (im Theme nicht eingesetzt), Spatial nur an Sonderstellen.
- **Farben:** nur Titan `#660000`, Impact `#B30000` und Weiß, abgestuft allein über Deckkraft (`fill-opacity`), keine
  neuen Farbwerte. Auf Titan: Impact (leise, 1,9 : 1 gegen Titan); auf Weiß: Impact mit 8–17 % Deckkraft.
- **Immer dekorativ:** `aria-hidden="true"`, inline zusätzlich `focusable="false"`, ohne Titel und Text; Hilfsmittel
  lesen nichts vor. Im Druck ausgeblendet.

**Platzierungen**

| Ort | Fassung | Verhalten |
|---|---|---|
| Rubrikband | `band.svg`: Streifen der Kuppel, Impact auf Titan | ab 1024 px in der freien Fläche zwischen letzter Rubrik und „Mehr“, rechts vor „Mehr“; nur wenn dort mindestens 300 px frei sind (Container-Abfrage), nie unter Schrift |
| Titan-Flächen „Diese Woche“, Termine „Ab heute“ | `flaeche.svg` inline: ganze Kuppel, Impact auf Titan | unten rechts angeschnitten, über der Fläche und unter Kacheln, Titeln und Links; der Bogen steigt in einer Zone unter dem letzten Inhalt auf (Handy 34vw, Tablet 196 px, Desktop 104 px Abstand unten) |
| Kino „Im Programm“ | wie oben, `signatur--hoch` | Desktop höher, in der freien Fläche rechts neben dem großen Bild |
| Seitenköpfe: Rubrik, Kino, Termine, Kontakt, Suche, Archive; Werben, Verzeichnis, Einreichen | `hell.svg`: leise Tönung auf Weiß | rechts vom Fensterrand angeschnitten; unter 1024 px schwimmt sie rechts oben und Titel und Zeile fließen herum, ab 1024 px rechts neben der Kopfzeile (Kopf mindestens 152 px hoch). Seiten mit mittiger Spalte (Werben …) ab 1200 px. Rechtstexte ohne |
| Fuß | `band.svg` | ab 1024 px rechts in der Zeile mit Rechtlichem (Titan), am Fensterrand angeschnitten, nur bei freiem Platz |
| 404, Production („Live mit dir!“) | `raum.svg` (03 Spatial) | ganz, ohne Anschnitt und ohne Bodenschatten (3.12.0, N-13); am Handy unter dem Kopf (höchstens 340 px), ab 1024 px rechts daneben (42 %) |

Nicht eingesetzt: ein kleiner Punktbogen über Blocktiteln (die Linie in Titan gliedert schon; er hätte unruhig gewirkt).

**An jedem Post (seit 3.6.0; Luis 19./20.11.: „klein und dezent, aber auf jeden einzelnen Beitrag“).** Ein kleiner
Punktbogen unten rechts im Bild jedes Beitrags, bündig in der Ecke; die Bildkante schneidet rechts den Auslauf und unten
ein Stück vom Fuß ab.

| | |
|---|---|
| Wo | jedes Beitragsbild in einem Rahmen: Aufmacher, Bildkarten, Kacheln, Listen der Rubriken, Suche, 404, Archive, „Weiterlesen“, Kino- und Termineinträge, Zeilen der Kinotabelle (auch mit Symbolbild), Production; das Bild im Artikel (steht es nur im Text, dieses Bild) |
| Nicht | Rubrikkacheln (Navigation), Leerzustände ohne Beitrag, Seiten (Impressum, Werben …), Verzeichniseinträge, Anzeigen, Logo |
| Form | `ecke.svg`: Small-Geometrie als Mini (47 Punkte, Größen leicht gestaucht, damit sie bei 20–56 px einzeln bleiben), unter 4 KB; als CSS-Hintergrund, einmal geladen |
| Größe | 13 % der Rahmenbreite, 20 bis 56 px (Listenzeile 96 px → 20 px, Karte 340 px → 44 px, Aufmacher → 56 px) |
| Farbe | weiß, Deckkraft 95 % am Fuß bis 72 % am Auslauf, mit leisem dunklem Schein (nur Schwarz mit Deckkraft); auf hellen Bildecken `ecke-rot.svg` in Titan (Fuß) und Impact (Bogen). Die Ecke wird einmal gemessen (relative Helligkeit über 0,3) und am Anhang gemerkt |
| Titel im Bild | weiß auf dem Verlauf, ohne Schein; der Text hält rechts die Breite des Bogens + 10 px frei, so liegt der Bogen nie unter Schrift |
| Schild „Symbolbild“ | bleibt oben rechts (in kleinen Rahmen „S“); der Bogen sitzt unten rechts, beide berühren sich nie |
| Bewegung | statisch; er erscheint mit seinem Bild (Aufdecken, Steigen), mit „Bewegung reduzieren“ steht er einfach da |

Prüfung: `node wordpress/dev/bilder_pflicht.mjs` zählt je Seite und Breite, ob jedes Beitragsbild den Bogen trägt
(sichtbar, bündig unten rechts im Bild, zuoberst, ohne Text im Bild oder das Schild zu überdecken); Soll 100 %.

**Technik.** Bogen an jedem Post: `tamil_bild()` (`inc/bildkette.php`) hängt `tamil_signatur_ecke_html()`
(`<span class="signatur-ecke" aria-hidden="true">`) an jedes Beitragsbild; Option `signet => false` für die Ausnahmen,
`tamil_signatur_ecke_im_text()` für Bilder nur im Text, CSS im Abschnitt „Signet an jedem Post“.
`inc/signatur.php`: `tamil_signatur( $variante, $args )` gibt `<span class="signatur signatur--…"
aria-hidden="true">` aus, inline mit SVG nur für `flaeche` (Animation), sonst leer mit CSS-Hintergrund (zwischengespeichert,
`?ver=` im CSS bei Änderungen erhöhen). Dateien in `assets/img/signatur/` (je unter 30 KB), gebaut mit
`assets/img/signatur/bauen.py` aus `design/signature/daten/punkte.json` über den Generator
`design/signature/tamil_dots.py`. CSS: `theme.css`, Abschnitt „Signet“. Die Kuppel ragt nie aus dem Fenster: Bilder
werden in ihrem Rahmen beschnitten, die Titan-Flächen schneiden mit `overflow: hidden`; was bis an den Fensterrand
reicht, rechnet mit `100vw` und wird bei sichtbarer Bildlaufleiste von `html, body { overflow-x: clip }` abgeschnitten.

**Animation „Punkte bauen die Form auf“** (Bewegung D, nur Titan-Flächen): Beim Hineinscrollen (IntersectionObserver
wie alle Auftritte, nach dem Vorhang von „Diese Woche“) wächst jeder Punkt in der Reihenfolge `--i` vom großen linken
Fuß zum Auslauf von `scale: 0` auf 1 und blendet ein, ease-out-expo, zusammen 1,5 s (`--t-aufbau`), einmal. Nur
`scale` und `opacity`. Ohne Skript, mit „Bewegung reduzieren“ und im ersten Bildschirm steht die fertige Form still.

## Bewegung D

Nur unter `prefers-reduced-motion: no-preference`, nur `transform` (als `translate`/`scale`), `opacity` und
`clip-path`; ohne Skript und mit „Bewegung reduzieren“ ist alles sichtbar und still. Der erste Bildschirm bewegt sich
nie von selbst; was einmal erschienen ist, bleibt.

| Teil | Bewegung | Dauer |
|---|---|---|
| Kopf | Kopfzeile verblasst, Logo wird 0,8 und schiebt sich unter das Band (am Scrollweg) | Weg = Kopfhöhe |
| Band | Leselinie 2 px in Impact an der Unterkante des Bands in Titan wächst mit dem Lesefortschritt | ganze Seite |
| Aufmacherbild | bis 40 px langsamer als die Seite | beim Hinausscrollen |
| „Diese Woche“ | Titan-Fläche zieht von links auf, danach steigt der Inhalt | 800 ms, Inhalt ab 55 % |
| Große Kacheln | Bild deckt sich von unten auf, Maßstab 1,06 → 1, Titel zeilenweise | 750 / 1100 / 700 ms |
| Blocktitel | steigen aus ihrer Linie | 700 ms |
| Kacheln, Bildkarten, Nebenstücke, Meldungen, Listen | 16 px nach oben, einblenden, gestaffelt 60 ms je Spalte, 100 ms je Reihe; wischbare Reihen erscheinen gemeinsam | 560 ms |
| Signet auf Titan-Flächen | Punkte bauen die Form auf (vom Fuß zum Auslauf, `scale` 0 → 1) | 1500 ms |

Am Scrollweg per CSS-Scroll-Timeline (`@supports (animation-timeline: scroll())`), sonst ein passiver Scroll-Handler
mit `requestAnimationFrame`. Auftritte über IntersectionObserver (Auslöser 10 % über der Unterkante). Code:
`assets/js/app.js` (Abschnitt „Bewegung“) und `theme.css` (Abschnitt „Bewegung beim Scrollen“).

## Ecken und Reihen (Theme 3.9.0)

- **Radius:** `--radius` 10 px an Karten und Bildern (Aufmacher, Bildkarten, Kino- und Terminkarten als Ganzes,
  Anzeigenflächen, Artikelbild, Bilder im Text, Verzeichnisbilder); `--radius-klein` 6 px an Rubrikkacheln, den
  Bildern der Kinotabelle und (seit 3.11.0) an Bedienelementen: Felder, Knöpfe, Filter, Seitenzahlen. Ein Rahmen setzt seinen Radius über `--rahmen-r`. Punktbogen und Schild „Symbolbild“
  schließen mit der Rundung ab (angeschnitten, kein Überstand). Gerade bleiben Bänder, Kopf, Fuß und Bilder, die am
  Handy von Rand zu Rand laufen (Aufmacher, Artikelbild unter 600 px). Nur Ecken, keine runden Bildformen.
- **Rhythmus (3.11.0):** Die Rubrikblöcke der Startseite wechseln zwischen der Reihe aus vier Karten und der Bühne
  (eine große Kachel, die übrigen klein gestapelt daneben, gebaut wie die Küche); Titel auf kleinen Karten höchstens drei
  Zeilen. Kacheln einer Bühne füllen ihre Rasterzelle, das Bild wächst mit. Seit 3.12.0 (N-03, N-08) sind alle Bühnen
  gleich gebaut (Küche und Rubriken: eine Größe, eine Schrift), Titel der kleinen Karten ganz ohne Kürzung. Eine
  einzelne letzte Karte steht in normaler Breite, nie über die ganze Zeile aufgezogen (N-04).
- **Reihen:** Karten einer Reihe sind gleich hoch und schließen unten bündig: gleiches Bildformat je Reihe, Titel unten
  im Bild, der Vorspann darunter hält immer drei Zeilen Platz; in „Diese Woche“ ist die Kinokarte neben den Terminen so
  hoch wie diese; Terminkarten einer Reihe haben gleich hohe Bildflächen. Prüfung: `node wordpress/dev/kartenhoehe.mjs
  <basis-url>` (je Reihe Ober- und Unterkante und Unterkante der Bildfläche ≤ 1 px; Bühnen je Spalte).

## Wow-Aufmacher „Punkt für Punkt zum Bild“ (Theme 3.10.0, überarbeitet 3.11.0)

- **Wo:** nur der Aufmacher der Startseite, nur mit eigenem Foto (kein Symbol-, Pool- oder Filmbild, keine
  Titelkarte, kein Band), dessen Originalfoto mindestens 960 px breit ist (`inc/wow.php`). Die Fensterbreite spielt
  keine Rolle: die Decke läuft am Handy, Tablet und Desktop. Sonst der normale Aufmacher.
- **Was:** Über dem Foto (`<img>`, `fetchpriority="high"`) liegt ein `<canvas>` in Titan mit den 238 Punkten des
  Masters „Tamil Dots 04A“ als Fenster aufs echte Foto. Die Form steht mittig über dem Titelfeld und berührt den Titel
  nie; Dachzeile und Titel stehen von Anfang an unten auf der Decke (weiß auf Titan 13,4 : 1). Seit 3.11.0 ist die
  Kuppel größer (Handy 98 %, sonst 90 % der Breite) und am Anfang schon halb geöffnet, so dass das Motiv sofort zu
  erkennen ist (Titan im ersten Bildschirm samt Band: 390 × 844 34 %, 1280 × 800 26 %). Beim Scrollen bleibt das Bild
  am Handy und am Desktop unter dem Band stehen (35 % einer Bildschirmhöhe, mindestens 260 px), am Desktop steht
  „Weitere Meldungen“ mit; am Tablet steht nichts fest, der Weg ist 60 % der Rahmenhöhe. Punkte und Titelfeld lösen
  sich über denselben Weg auf, der Titel liegt danach auf dem Verlauf des Fotos, der Punktbogen erscheint.
  Zurückscrollen spielt es rückwärts. Nur Bild, Titel und Vorspann sind Link, nicht die leere Fläche des Wegs.
- **Titel:** nie gekürzt und nie getrennt (seit 3.11.1, N-02; `hyphens: manual`): bis 60 Zeichen 26 px am Handy und
  38 px am Desktop, darüber zwei kleinere Stufen (über 60 und über 90 Zeichen, `titel--mittel`, `titel--klein`).
- **Rahmen:** am Handy hochkant (bis 116 vw, höchstens Bildschirm minus Band; der Vorspann steht über der festen
  Anzeige), von Rand zu Rand; ab 600 px 60 vw, ab 1024 px 420 bis 620 px hoch, mit dem Radius des Aufmachers.
- **Ruhe:** Ohne Skript, ohne Canvas und mit „Bewegung reduzieren“ steht sofort das fertige Foto mit Titel. Bewegung D
  ist für diesen Aufmacher aus. Der erste Bildschirm bewegt sich nie von selbst.
- **Abschalten:** Customizer (Tamil.de → Startseite → „Wow-Aufmacher“, **seit 3.13.1 Standard aus**, Entscheidung von Luis vom 21.11.) oder Filter `tamil_wow_aufmacher`.
- **Technik:** `assets/js/wow.js` (17 KB, 6,9 KB gepackt, Punktdaten darin), nur auf der Startseite, `defer`; ein
  Skript im Kopf setzt `wow-an`. Die Decke zeichnet ruhend höchstens zweifach, in Bewegung mit rund 250 000 Bildpunkten.

## Raster

Inhalt höchstens 1280 px, Rand 16 / 24 / 40 px (ab 600 / 1024 px). Desktop-Startseite: Aufmacher und 388 px
Meldungen mit 32 px Abstand; „Diese Woche“ dreispaltig. Brüche bei 600 und 1024 px.
