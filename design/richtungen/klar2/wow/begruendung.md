# Wow-Vorschauen mit Tamil Dots 04A

> **Stand 21.11.2026. Nur Vorschau.** Nichts davon ist freigegeben oder im Theme. `wordpress/` ist unberührt.
> Grundlage: `design/referenzen/wow-2026-11/README.md`, Idee 1 und Idee 2.

| Vorschau | Datei | Was sie zeigt |
|---|---|---|
| 1 „Punkt für Punkt zum Bild“ | `punkt-zum-bild/index.html` | Startseite, deren Aufmacherfoto aus den 238 Punkten entsteht |
| 2 „2026 in 238 Punkten“ | `jahr-in-punkten/index.html` | Sonderseite, auf der die Punkte die Meldungen des Jahres sind |

Öffnen: vom Repo-Root einen Dateiserver starten (`python3 -m http.server`) und die Dateien aufrufen, oder die
HTML-Dateien direkt im Browser öffnen. Neu erzeugen: `python3 design/richtungen/klar2/wow/bauen.py`.

## Idee

Das Signet ist heute Dekor: Es liegt hinter Flächen und in der Bildecke. In beiden Vorschauen **tut es etwas**.

- In Vorschau 1 ist es das Fenster zum Foto. Wer scrollt, fährt durch die Punkte in das Bild hinein.
- In Vorschau 2 ist es die Inhaltskarte. Jeder rote Punkt ist eine Meldung, die sich öffnen lässt.

Beides kann nur tamil.de zeigen, weil die Form aus den eigenen Punktdaten kommt
(`design/signature/daten/punkte.json`, 238 Punkte des Masters). Die Nachrichtenfläche darunter bleibt klar2.

## Was gebaut ist

### Vorschau 1: Punkt für Punkt zum Bild

- **Seite:** Kopf mit Logo, Rubrikband, Aufmacher über die volle Breite, vier Karten „Weitere Geschichten“, drei
  Karten „Weitere Meldungen“, Fuß mit Bildnachweisen. Das Aussehen kommt aus einer Kopie des Theme-CSS 3.8.0
  (`assets/css/theme.css`), dazu rund 50 Zeilen eigenes CSS.
- **Anfang:** Über dem Foto liegt eine Decke in Titan. Sie hat 238 Löcher, genau die Punkte des Masters, in
  unveränderter Form und Lage. Durch die Löcher sieht man das echte Farbfoto. Nichts bewegt sich.
- **Titel von Anfang an (Nacharbeit 21.11.):** Dachzeile und Titel stehen schon am Anfang unten auf der Decke, weiß
  auf Titan (13,4 : 1), in Variante B schwarz auf Weiß. Lage und Größe sind dieselben wie später im Bild, beim
  Aufdecken springt nichts. Die Form steht in der Zone darüber. Gemessen berührt sie den Titel nie: Abstand am Anfang
  110 px bei 390, 61 px bei 820, 65 px bei 1280, und an 79 Stellen des Scrollwegs liegt kein Loch im Titelfeld.
  Im ersten Bildschirm ist der ganze Titel zu sehen (1280 × 800 und 390 × 844).
- **Scrollen:** Das Bild bleibt unter dem Rubrikband stehen (`position: sticky`), solange der Leser 70 % einer
  Bildschirmhöhe scrollt (mindestens 420 px). Auf diesem Weg wachsen die Punkte vom großen Fuß links zum feinen
  Auslauf rechts. Gleichzeitig fährt der Blick 3,2-fach in die Form hinein. So bleiben die Punkte lange einzelne
  Fenster, statt früh zu einem Fleck zu verlaufen.
- **Ende:** Erst steht das Foto über dem Titelfeld, dann löst sich das Titelfeld auf. Derselbe Titel liegt jetzt auf
  dem Verlauf des Themes, dazu kommt der kleine Punktbogen in der Ecke. Zurückscrollen spielt alles rückwärts.
- **Variante B, Einschränkung:** Dort wechselt die Schrift von Schwarz zu Weiß. Während der kurzen Auflösung (5 % des
  Scrollwegs) ist der Kontrast nicht für jede Zwischenstellung gesichert. In Variante A bleibt die Schrift weiß.
- **Technik:** ein `<canvas>` über dem normalen `<img>`. Je Bild eine Titan-Fläche und ein einziger Pfad aus 238
  Ellipsen, mit `destination-out` ausgestanzt. Kein WebGL, kein Framework, kein fremdes Skript. Skript und
  Punktdaten stehen in der Seite: zusammen 16,1 KB roh, 6,6 KB gepackt.
- **Ohne Skript, mit „weniger Bewegung“ oder in Variante C:** sofort das fertige Foto mit Titel, kein Festhalten,
  kein Scrollweg. Die Decke wird nur eingeschaltet, wenn das Skript im Kopf die Klasse `wow-an` setzt.
- **Umschaltleiste oben (nur Vorschau):** A „Punkte auf Titan“, B „Punkte auf Weiß“, C „aus (wie heute)“. Auch
  über `?v=a`, `?v=b`, `?v=c`.

Entscheidungen, die ich getroffen habe:

1. **Aufmacher ist die Deepavali-Meldung, nicht die Geschichtenstunde in Aarau.** Auf der Testseite steht Aarau
   oben (Foto einer grauen Bibliothek). Für den Beweis braucht es ein Foto mit Farbe und einem klaren Motiv. Die
   Deepavali-Meldung hat ein eigenes Foto des Berliner Tempels, kein Symbolbild. Titel, Datum, Vorspann und Nachweis
   sind unverändert übernommen. Aarau steht als erste Karte darunter.
2. **Variante A (Titan) ist die Empfehlung.** Titan ist die dominante Markenfarbe, die Decke schließt bündig an das
   Rubrikband an, und das Foto leuchtet in den Punkten. Variante B (Weiß) ist feiner, wirkt im ersten Bildschirm aber
   wie eine leere Fläche mit einem Muster.
3. **Die Form steht mittig in der Zone über dem Titel** mit Luft zum Rand (höchstens 74 % der Bildbreite, am Handy
   86 %). Die freie Fläche unter
   dem Bogen bleibt frei.
4. **Der Vorspann bleibt mit stehen.** Sonst stünde am Handy während des Wachsens eine leere weiße Fläche unter
   dem Bild.
5. **Aufmacher über die volle Breite** statt 780 px neben der Spalte „Weitere Meldungen“. Die Form braucht Fläche.
   Im Theme wäre das eine eigene Aufmacher-Fassung.

### Vorschau 2: 2026 in 238 Punkten

- **Seite:** Seitentitel, ein Satz Erklärung, die Kuppel groß auf Weiß, Filter nach Rubrik, darunter alle Meldungen
  als Liste nach Monaten.
- **Ehrliche Zahl:** Auf dem Testsystem stehen **72 Meldungen mit Datum 2026** (von 604 Beiträgen insgesamt, der
  Rest ist Altbestand 2021 bis 2024). Darum sind **72 von 238 Punkten** belegt. Die übrigen 166 Punkte sind blass,
  ohne Link, und die Seite sagt das im Text.
- **Zuordnung:** Die Meldungen laufen zeitlich am Bogen entlang, Januar am Fuß links, November im Auslauf rechts
  (dieselbe Reihenfolge wie beim Aufbau in `design/signature/tamil_dots.py`). In jedem der 72 Abschnitte bekommt die
  Meldung den größten Punkt, damit er sich treffen lässt. **Die Punktgröße sagt nichts über die Bedeutung.**
- **Zeigen oder Fokus:** Der Punkt wird größer, Impact mit schwarzem Rand, ein schwarzes Schild zeigt Titel, Rubrik
  und Datum. Klick öffnet die Meldung auf der Testseite. Jeder Punkt hat einen unsichtbaren Griff, der etwas größer ist als der Punkt selbst.
- **Filter:** Die Punkte der Rubrik stehen in Impact, alle anderen blass. Die Liste zeigt dieselbe Auswahl, eine
  Statuszeile nennt die Zahl (`role="status"`).
- **Liste:** dieselben 72 Meldungen als normale Links, mindestens 44 px hoch. Überfahren einer Zeile hebt ihren
  Punkt hervor. Vor der Kuppel steht der Link „Alle 72 Meldungen als Liste lesen“.
- **Bewegung:** keine beim Laden und keine beim Scrollen, nur 0,16 s beim Zeigen. Unter „weniger Bewegung“ gar keine.
- **Nicht gebaut:** das Aufleuchten Monat für Monat beim Scrollen aus der Ideenbeschreibung.

## Messwerte

Gemessen am 21.11.2026 mit Playwright/Chromium ohne Grafikkarte.

| Prüfung | Vorschau 1 | Vorschau 2 |
|---|---|---|
| `tools/shots.mjs` bei 390, 820, 1280: seitliches Scrollen | 0 px | 0 px |
| `tools/shots.mjs`: Konsolenfehler, leere Bilder, fehlende Schriften | 0 | 0 |
| `tools/shots.mjs`: Tippflächen unter 44 px | 0 | 15 Punkte der Kuppel bei 390 und 820 (gewollt, Liste darunter) |
| axe-core 4, WCAG 2.0 bis 2.2 A und AA, 390 und 1280, oben und gescrollt | 0 Verstöße (A, B, C) | 0 Verstöße |
| Seite ohne Bilder und Schriften | 31,8 KB | 96,9 KB |
| Aufmacherfoto | 199 KB (1200 px), 79 KB (768 px) | – |

**Bildrate beim Scrollen**, 390 × 844, dreifache Pixeldichte, CPU vierfach gedrosselt, 150 Bilder mit je 12 px
Scrollweg. Ziel sind 16,7 ms je Bild.

| Fassung | Median | längstes Bild | Bilder über 33,4 ms |
|---|---|---|---|
| Vorschau 1, A (Titan), 9 Läufe vor der Nacharbeit | 16,7 ms | 33,4 ms in sieben Läufen, je einmal 50,0 ms und 333 ms | 0 bis 5 von 149 |
| Vorschau 1, B (Weiß), 3 Läufe | 16,7 ms | 33,3 bis 33,5 ms | 0 bis 2 von 149 |
| Vorschau 1, C (aus), 6 Läufe | 16,7 ms | 16,8 ms | 0 |
| Vorschau 2, 3 Läufe | 16,7 ms | 16,8 ms | 0 |

Nach der Nacharbeit (Titel von Anfang an) drei weitere Läufe je Variante A und B: Median 16,7 ms, längstes Bild
16,8 bis 33,3 ms, kein Bild über 33,4 ms.

Einordnung: Mit der Decke fällt gelegentlich ein Bild aus (33 ms statt 17 ms). Der eine Wert von 333 ms kam in
neun Läufen einmal vor und ließ sich nicht wiederholen. Ob er von der Seite oder vom Prüfrechner kam, ist offen.
Die Messung läuft ohne Grafikkarte. Auf einem echten Handy fehlt noch die Gegenprobe.

Dafür getan: Die Decke zeichnet ruhend scharf (höchstens zweifache Dichte) und in Bewegung mit rund 250 000
Bildpunkten. Mit 500 000 Bildpunkten lag das längste Bild öfter bei 50 ms.

Nicht gemessen: LCP, CLS und INP im echten Theme. Kontrast der Schrift im Bild: nicht neu gemessen, es ist der
unveränderte Verlauf des Themes (laut `DESIGN.md` mindestens 5,9 : 1), axe meldet keinen Verstoß.

## Abgrenzung zur Verbotsliste

| Verbot (`abgelehnt.md`) | Wie die Vorschauen damit umgehen |
|---|---|
| R4 „rot gedrucktes Halbtonfoto“ als Signatur | Die Punkte zeigen das echte Farbfoto, kein gerastertes oder rot eingefärbtes Bild. Der Punktzustand ist nur Anfang und Übergang, der Endzustand ist immer das volle Foto. |
| R2 „keine runden Bilder“, R3 „Rundungen, Kreise“ | Runde Fenster gibt es nur während des Übergangs. Das fertige Bild ist ein Rechteck mit Radius 0. Knöpfe und Schild sind eckig. |
| R1 „dunkle Bühne“ | Vorschau 2 steht auf Weiß. In Vorschau 1 ist die Titan-Decke so groß wie ein Aufmacherbild und verschwindet beim Scrollen. |
| R4 „Rot als Fläche“, „zu viel Rot“ | **Grenzfall in Variante A:** Im ersten Bildschirm steht eine Titan-Fläche in Bildgröße. Seit dem 19.11. ist Titan die dominante Markenfarbe, und Titan-Flächen mit Signet gibt es im Theme schon. Wer das zu viel findet, nimmt Variante B. |
| R4 „Signatur-Elemente als Effekt“, Brief „keine Effekte“ | **Grenzfall, bewusst:** Das ist ein Effekt, und Luis hat ihn bestellt. Er sitzt an genau einer Stelle der Seite, antwortet nur auf Scrollen und lässt sich abschalten. |
| R1 „technische Radar-Spielerei auf der Leserseite“ | Vorschau 2 ist eine eigene Sonderseite, nicht die Startseite. Sie zeigt nur Titel, Datum und Rubrik und hat die Liste als gleichwertigen Weg. |
| R5 bis R7 „Versal-Labels“ | Keine Versalien. Dachzeilen und Verlauf-Bildkarten sind klar2-Bestand und für klar2 erlaubt. |
| Kreise als Schmuck außerhalb des Signets | Alle Punkte sind die Ellipsen des Masters, an ihrer Stelle. Es gibt keine zusätzlichen Kreise. |
| Regel „Die freie Fläche unter dem Bogen bleibt frei“ | Eingehalten. Titel und Schild stehen nie unter dem Bogen: Der Titel steht in einem eigenen Feld unterhalb der Form. |
| Regel „Der erste Bildschirm bewegt sich nie von selbst“ | Eingehalten. Ohne Scrollen ändert sich kein Bildpunkt. |

Die erste Fassung zeigte die Schlagzeile erst nach dem Scrollweg. Das ist behoben: Sie steht von Anfang an auf der
Decke (siehe oben). Der Vorspann beginnt am Handy weiter erst an der Unterkante des ersten Bildschirms.

## Einbau ins WordPress-Theme

### Vorschau 1

| Was | Wo | Aufwand |
|---|---|---|
| Skript (Zeichnen, Scrollweg) als eigener Abschnitt | `assets/js/app.js` oder eigene Datei, nur auf der Startseite geladen | 0,5 Tage |
| Punktdaten als Datei statt in der Seite | `assets/js/` oder `inc/signatur.php`, aus `punkte.json` erzeugt (`assets/img/signatur/bauen.py`) | 0,5 Tage |
| CSS (Bahn, Halter, Decke, Zustände) | `assets/css/theme.css`, Abschnitt Bewegung | 0,5 Tage |
| Aufmacher-Markup: Bahn, Halter, `<canvas>`; Fassung über die volle Breite | `front-page.php`, Aufmacher-Baustein | 1 Tag |
| Schalter im Customizer oder je Beitrag („Aufmacher mit Punktfenster“), Regel „höchstens ein Bild je Seite“ | `inc/`, `functions.php` | 0,5 Tage |
| Abstimmung mit Bewegung D (Kopf schrumpft, Aufmacherbild läuft langsamer, Aufdecken) | `app.js`, `theme.css` | 0,5 bis 1 Tag |
| Prüfung: `shots.mjs`, `bilder_pflicht.mjs`, axe, echtes Handy, Lighthouse | – | 1 Tag |

Zusammen **rund 4 bis 5 Tage**. Nötig ist außerdem ein Ja von Luis und ein Eintrag in `DESIGN.md`
(Abschnitt „Signet“ und „Bewegung“), weil Gestaltung im Theme nur über `/design-umsetzung` geändert wird.

Risiken für Tempo und LCP:

- **LCP:** Das größte Element bleibt das Aufmacherfoto. Es ist ein normales `<img>` mit `fetchpriority="high"`, die
  Decke liegt nur darüber. Chromium zählt verdeckte Bilder nach heutigem Stand trotzdem als LCP-Kandidaten. **Das
  ist nicht gemessen** und muss vor dem Einbau mit Lighthouse am Testsystem belegt werden.
- **Skript im Kopf:** Die Decke braucht ein kleines Skript vor dem ersten Bild, sonst blitzt das Foto kurz auf.
  Das sind wenige Zeilen, sie blockieren aber das Rendern für diese Zeit.
- **Foto lädt spät:** Bei langsamem Netz sind die Punkte erst grau (`neutral-flaeche`), dann kommt das Foto. Das
  sieht nach Fehler aus. Abhilfe: Bild vorladen, kleines Vorschaubild als Hintergrund.
- **Scrollen am Handy:** Gemessen fällt gelegentlich ein Bild aus. Auf alten Android-Geräten kann es mehr sein. Dann
  hilft eine kleinere Decke oder ein Abschalten unter einer Geräteschwelle.
- **Scrollweg:** Die Seite wird um 70 % einer Bildschirmhöhe länger. Die Handy-Anzeige (320 × 50, erscheint nach dem
  ersten Abschnitt) und die Messung der Sichtbarkeit von Anzeigen müssen damit getestet werden.
- **Zusammenspiel mit Bewegung D:** Das langsamer laufende Aufmacherbild und das Aufdecken von unten müssen für
  diesen Aufmacher aus sein, sonst laufen zwei Effekte übereinander.
- **CLS:** keines erwartet, die Höhen stehen im CSS fest. Nicht gemessen.

### Vorschau 2

| Was | Wo | Aufwand |
|---|---|---|
| Seitenvorlage „Jahr in Punkten“, SVG vom Server aus Punktdaten und Beiträgen | `page-jahr.php`, `inc/signatur.php` | 1,5 Tage |
| Auswahl der Beiträge (Jahr, optional Auswahl durch die Redaktion), Zwischenspeicher | `inc/`, Plugin `tamil-site` | 1 Tag |
| CSS und Skript (Filter, Schild) | `theme.css`, `app.js` | 1 Tag |
| Prüfung | – | 0,5 Tage |

Zusammen **rund 4 Tage**. Tempo ist unkritisch: rund 380 SVG-Elemente, 21 KB gepackt, kein Bild, keine Bewegung beim Laden.
Offene Fragen sind redaktionell: Was passiert bei mehr als 238 Meldungen im Jahr (Auswahl der Redaktion oder die
238 meistgelesenen)? Und soll die Punktgröße etwas bedeuten?

## Empfehlung

- **Vorschau 1: ja, in Variante A (Titan), zuerst begrenzt.** Sie ist der stärkste Moment, den die Marke hergibt,
  und kostet wenig Gewicht. Vor dem Einbau braucht es zwei Dinge: eine Messung am echten Handy und eine
  Lighthouse-Messung am Testsystem. Einsatz nur am Aufmacher der Startseite und nur, wenn
  der Beitrag ein eigenes, farbiges Foto hat. Bei Symbolbildern bleibt der normale Aufmacher.
- **Vorschau 2: ja, als Sonderseite für den Jahresrückblick im Dezember**, nicht für die Startseite. Vorher muss
  die Redaktion festlegen, welche Meldungen hineinkommen.

## Dateien

| Datei | Inhalt |
|---|---|
| `bauen.py` | erzeugt beide Seiten aus den Daten (nur Standardbibliothek) |
| `daten/startseite.json` | Aufmacher und sieben Karten: Titel, Datum, Vorspann, Alt-Text, Nachweis, Link (Testseite, 21.11.2026) |
| `daten/meldungen-2026.json` | 72 Meldungen 2026: Titel, Datum, Rubrik, Link (REST-Schnittstelle der Testseite, 21.11.2026) |
| `bilder/` | acht Fotos der Testseite als WebP, verkleinert; Nachweise im Fuß von Vorschau 1 |
| `assets/` | Kopie aus dem Theme 3.8.0: `theme.css`, Schriften (OFL), Logo, Signet-SVG |
