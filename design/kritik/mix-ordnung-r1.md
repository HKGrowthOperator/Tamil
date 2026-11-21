# Prüfung mix-ordnung, Runde 1
Harte Kriterien: 16 von 16 erfüllt (Startseite, Brief 10.4) · P0: 0 · P1: 6 · P2: 4 · P3: 3

Maßstab: Brief 2.1 mit Abschnitt 10.4 (die Probe übernimmt Ordnung, Kopf und Mittel von `klar2`), Verbotsliste,
Auftrag vom 12.11. (überall Bilder, Bildwucht, „im Zweifel leiser“ gilt nicht mehr). `begruendung.md` nicht gelesen.
Gemessen am 12.11.2026 mit `node design/vergleich/aufnahmen.mjs mix-ordnung` (Kennzahlen:
`design/vergleich/kennzahlen/mix-ordnung.json`), mit einer Kopie dieses Skripts für artikel, rubrik, termine, suche
und kontakt (nur im Scratch-Ordner), mit `node tools/shots.mjs … --kacheln` für alle sechs Seiten bei 390, 820 und
1280 (18 Aufnahmen, 0 Fehler) und mit eigenen Playwright-Messungen (Logo, Bildformate, Bildnachweise, Zeilenzahl,
Zeilenlänge, Fokus, Zoom auf 640 und 320 px).

## Erster Eindruck (3 Sätze)

Die Startseite liest sich sofort als Nachrichtenseite: heller kühler Grund, dunkles Rubrikband, ein großes Foto mit
Schlagzeile, darunter und daneben weitere Fotos. Neben dem Live-Design ist der Sprung groß; neben `klar2` ist der
erste Handy-Bildschirm fast derselbe, erst am Desktop und weiter unten wird es deutlich bildstärker. Was die Bildwucht
bremst, ist der fast deckende Tinte-Verlauf: Die Fotos im ersten Bildschirm liegen zur Hälfte unter einer dunklen Fläche
und wirken eher gedämpft als stark.

## Harte Kriterien (Startseite, Brief 10.4)

| # | Kriterium | Handy 390 × 844 | Desktop 1280 × 800 | Ergebnis |
|---|---|---|---|---|
| 1 | Viele Geschichten (`schlagzeilen_ganz_sichtbar`), h2/h3 mit Link | 2 (Aufmacher und „Vaani Vizha“) | 6 | erfüllt |
| 2 | Kopf ≤ 152 px (`kopfleiste_hoehe`); Aufmacher ab ≤ 480 px | 150 px; 270 px | 122 px; 272 px | erfüllt |
| 3 | Drei Stufen, Aufmacher ≥ 1,25 × Nebenstück; ≤ 2 Familien | 30 : 20 px = 1,5; Libre Franklin | 40 : 26 px = 1,54 | erfüllt |
| 4 | Größte ≤ 34/44 px und Aufmacher; zweitgrößte ≤ 24/28 px; Zeilen 3/4; Versalien | 30 / 22 px; 3 / 4 Zeilen; 0 | 40 / 26 px; 2 / 3 Zeilen; 0 | erfüllt (auf Unterseiten verletzt, siehe P1-4, P1-5, P2-2) |
| 5 | Rot ≤ 3 %, rote Schrift ≤ 20 px, kein zweiter Buntton | 0,04 %; 13 px; bunt = rot | 0,05 %; 13 px; bunt = rot | erfüllt |
| 6 | Genau zwei dunkle Flächen; ≤ 12 % dunkel im ersten Bildschirm | `nav.band`, `#diese-woche`; 6,2 % | dieselben; 5,7 % | erfüllt (auf `termine.html` 22,7 % und 24,1 %, siehe P1-6) |
| 7 | Keine Effekte; Verlauf nur unter Schrift im Bild | Radius 0, Schatten 0, gedreht 0, Breite normal; `--verlauf` nur in `.imbild` | dasselbe | erfüllt (Wirkung des Verlaufs siehe P1-1) |
| 8 | Kein Baukasten | keine Pillen, kein Kasten an Anreißern; 3 Kacheln „Fläche auf Dunkel“ | dasselbe | erfüllt |
| 9 | Überall ein Bild (`anreisser_ohne_bild`), Grafik ≤ 3 | 22 Anreißer, 0 ohne Bild, 3 Grafik | dasselbe | erfüllt |
| 10 | Ein Format Dachzeile/Datum; ≤ 3 Bildformate | „Rubrik \| 17. Juli 2024“ überall; 1,50 · 1,78 · 2,35 | dasselbe | erfüllt |
| 11 | Bildgröße | über Dateibreite: keins | über halber Dateibreite nur `rb-30` (Aufmacher, 797 px) und `rb-48` (große Küchen-Kachel, 862 px) | erfüllt |
| 12 | Helle Schrift ≥ 4,5 : 1 an der hellsten Stelle | kleinster Wert 5,9 (48 Zeilen) | 5,58 (66 Zeilen) | erfüllt |
| 13 | Bewegung | Maßstab 1,03; 0,35 s; 0 Animationen; „reduziert“: 0 Übergänge; fest nur `nav.band` 46 px | dasselbe | erfüllt |
| 14 | Kein Überlauf, keine Konsolenfehler | 0 px bei 390 und 820, 0 Fehler (alle 6 Seiten) | 0 px, 0 Fehler | erfüllt |
| 15 | „Diese Woche“ am Handy ≤ 2532 px | Oberkante 1933 px | – | erfüllt |
| 16 | Paarvergleich: kein Messwert außerhalb der Grenzen | alle Werte innerhalb | alle Werte innerhalb | erfüllt |

Weitere Messwerte: Logo 46 px (Handy, Soll 44–52) und 58 px (Desktop, Soll 56–60). Rubrikband 46 px, jede Rubrik
46 px hoch tippbar. Fließtext im Artikel 18 px bei Zeilenhöhe 28,8 px, Vorspann 19 px; 37 Zeichen je Zeile am Handy,
61 am Desktop (Soll ≤ 70). Keine Tippfläche unter 44 px auf allen sechs Seiten bei 390 und 820 (`bericht.json`).
Zoom 200 % (640 px) und 400 % (320 px): 0 px Überlauf auf allen Seiten. Fokus: `a:focus-visible` 2 px Tinte, im
Band und auf Bildkacheln 2 px hell nach innen versetzt; Tab erreicht alle Rubriken, das Band rollt mit.

## Paarvergleich

**Live-Design Runde 2 (`r2-heute-handy.jpg`, `-desktop.jpg`) gegen Probe**
- Handy: Live hat Sandgrund, Rubriken als Pillen, eine Anzeige mit rotem Pillenknopf vor dem Aufmacher, einen
  Aufmacher als cremefarbenen Kasten mit Ornament und ohne Foto, Vorspann in Serife und eine feste WhatsApp-Leiste
  unten. Die Probe hat kühles Weiß, das erste Foto beginnt bei 150 px, keine Pille, keine feste Leiste, 2 ganze
  Schlagzeilen und 2 Fotos im ersten Bildschirm (Live: 0 Fotos).
- Desktop: Live zeigt Anzeige über dem Aufmacher, Aufmacher ohne Foto, runde Vorschaubilder und farbige Punkte vor
  den Dachzeilen. Die Probe füllt rund drei Viertel des ersten Bildschirms mit drei rechteckigen Fotos und zeigt 6
  ganze Schlagzeilen. Beobachtbar weniger klassisch und deutlich bildstärker.

**`klar2` (`klar2-start-*.jpg`) gegen Probe**
- Handy: Kopf, Band und Aufmacher mit Titel im Bild sind praktisch gleich gebaut. Unterschied: Unter dem Aufmacher
  stehen bei `klar2` die Rubrikkacheln und eine Meldung mit kleinem Bild (3 Schlagzeilen sichtbar), bei der Probe ein
  randbreites Nebenstückfoto (358 × 238 px) mit Text darunter (2 Schlagzeilen). Das Aufmacherbild der Probe ist mit
  rund 260 px niedriger als bei `klar2` und zeigt ein Gebäude unter grauem Himmel statt eines Gesichts. Im ersten
  Handy-Bildschirm ist die Probe nur wenig bildstärker als `klar2`; ab dem zweiten Bildschirm (Nebenstücke als
  volle Fotos, Woche, Küche) deutlich.
- Desktop: `klar2` hat rechts eine Textliste „Weitere Meldungen“ mit fünf kleinen Bildern; die Probe setzt dort zwei
  Bildkacheln (387 × 258 px) mit Titel im Bild und darunter eine Dreierreihe mit Bild. Die Fotofläche ist sichtbar
  größer, aber alle drei großen Fotos liegen unter dem Verlauf (siehe P1-1); 44,7 % der Bildpunkte des ersten
  Bildschirms sind dunkler als Luma 60 (Handy 30,1 %).

**Vorbilder Spiegel und BBC (`news-spiegel-handy-1.jpg`, `news-bbc-handy-1.jpg`) gegen Probe**
- Beide Vorbilder zeigen das Aufmacherfoto unverdunkelt und setzen die Schlagzeile darunter auf Weiß; die Probe
  setzt sie ins Foto auf einen fast deckenden Verlauf.
- Beide Vorbilder führen mit Menschen und Gesichtern; der erste Bildschirm der Probe zeigt Tempelturm, Steinrelief und
  Reichstag, keinen Menschen.
- Dichte und Ordnung sind vergleichbar: dieselbe Zahl ganzer Schlagzeilen am Handy wie Spiegel, Linien statt Kästen
  wie BBC, Dachzeile mit Datum in einem Format.

**Runde 4 Feed (`r4-feed-handy.jpg`) gegen Probe**
- Feed: rotes Titelwort über die volle Breite in extraschmaler Schrift, nur eine Geschichte, feste Daumenleiste.
  Probe: größte Schrift 30 px, normale Breite, Rot 0,04 %, 2 ganze Schlagzeilen, keine feste Leiste unten. Nichts davon
  wird wiederholt.

Antwort auf die Frage des Auftrags, an diesen Beobachtungen: Neben dem Live-Design wirkt die Probe deutlich weniger
klassisch und bildstärker. Neben `klar2` gilt das am Desktop und ab dem zweiten Handy-Bildschirm, im ersten
Handy-Bildschirm kaum. Laut oder billig ist nichts (Rot, Schrift, Radius, Pillen alle im Rahmen); das Risiko liegt auf
der anderen Seite: schwer und dunkel durch den Verlauf.

## Befunde

### P0
Keine. `bericht.json`: 18 Aufnahmen, 0 Überlauf, 0 Konsolenfehler, 0 leere Bilder, 0 fehlende Schriften.

### P1

**P1-1 · Der Verlauf wirkt als dunkle Platte über den Fotos (Verbotsliste „Platte über dem Bild“, Brief 2.1 „ohne
Platte“; Brief 10.1 „Nebenstücke behalten ihren Text neben oder unter dem Bild“).**
Ort: `index.html` 1280 erster Bildschirm (Aufmacher, Nebenstücke „Vaani Vizha“ und „Bundestagsdrucksache“), 390
Aufmacher; `rubrik.html` 390 und 1280 Aufmacher; Küche 1280 kleine Kachel „Bremen“.
Messung: `--verlauf` steigt in 56 px von 0 auf 76 % Deckkraft und endet bei 92 %, `.imbild` hat 64 px Polster oben.
Im Aufmacher am Desktop stehen Dachzeile, zwei Zeilen Titel, drei Zeilen Vorspann und der Bildnachweis im Bild: rund
58 % der Bildhöhe (≈ 307 von 530 px) liegen unter dem Verlauf, davon fast alles bei 76–92 %. Am Handy haben die
Bildzeilen unter dem Titel eine mittlere Helligkeit von 47–66 (Datei im Mittel 93). In den zwei Nebenstück-Kacheln
(Desktop) liegen Titel und ein zweizeiliger Nachweis über dem Relief und über dem Reichstag; der Nachweis bricht mit
„3.0“ allein in der zweiten Zeile um. Die Kachel „Bremen“ (Küche, 322 × 181 px) ist zu etwa drei Vierteln von Text
bedeckt, Nachweis endet mit „4.0“ allein in der Zeile. Die Bildwucht, die der Auftrag will, wird so verdeckt; der
erste Desktop-Bildschirm ist zu 44,7 % dunkel (mit Bildern).
Behebung: Im Bild nur Dachzeile und Schlagzeile; Vorspann und Nachweis unter das Bild. Verlauf erst ab der Oberkante
der Dachzeile, Deckkraft höchstens 0,7 an der Unterkante, und den Kontrast danach neu messen (≥ 4,5 : 1). Nebenstücke
am Desktop wie am Handy mit Text unter dem Bild, oder nur dann im Bild, wenn die Hauptsitzung Brief 10.1 für diese
Runde aufhebt. Kleine Küchen-Kacheln: Titel unter das Bild.

**P1-2 · Commons-Bild ohne Namensnennung (CC BY-SA verlangt sie).**
Ort: `rubrik.html`, alle Breiten, Rubrikkachel „Sport“ (`bilder/rb-67.jpg`, Stade Municipal Yverdon). Auf
`index.html` steht der Nachweis „Vincenzo.togni / Wikimedia Commons, CC BY-SA 4.0“, auf der Rubrikseite fehlt er.
Behebung: Nachweis an jeder Stelle, an der das Bild erscheint (auch bei Kacheln, z. B. als Zeile unter dem Streifen
„Fotos: …“), oder für die Kachel ein Bild aus dem Altbestand mit Nachweis.

**P1-3 · Fremdbilder aus dem Altbestand ohne jeden Nachweis.**
Ort: `index.html` 11 Bilder: Kino-Kachel „Kanguva“ (`p9711`, Szenenbild des Films, die größte Kachel in „Diese
Woche“), „Rathamaarey“ (`p9697`, Pressefoto), Küche „Dosa“ (`p9591`) und „Payasam“ (`p9597`), sieben Rubrikkacheln
(`p8468`, `p9344`, `p9198`, `p9146`, `p9149`, `p6708`, `p8527`); dieselben auf `artikel.html` und `termine.html`
(`p9711`, `p9697`); `rubrik.html` zusätzlich `p9556`; `kontakt.html` das große Gruppenfoto (`p9146`). Ein
Szenenbild gehört dem Verleih (Entscheidung vom 11.11.); der Auftrag vom 12.11. erlaubt Altbestand nur mit Nachweis.
Behebung: Wo die Quelle bekannt ist, nennen („Szenenbild: <Verleih>“); sonst einheitlich „Foto: Archiv tamil.de“ und
die Quelle bei Luis klären. Das Szenenbild „Kanguva“ und das Pressefoto ohne geklärte Herkunft nicht als größte
Kachel verwenden.

**P1-4 · Aufmacher der Rubrikseite mit vier Zeilen (Brief Abschnitt 3 und Kriterium 4: höchstens drei).**
Ort: `rubrik.html` 390, „Steinmeier beim Tempelfest in Hamm-Uentrop: Dank an die tamilische Minderheit“, 30 px,
Bruch am Bindestrich „Hamm-“ / „Uentrop“.
Behebung: Aufmacher auf Rubrikseiten am Handy 28 px und das Textfeld über die volle Bildbreite (358 px); „Hamm-Uentrop“
mit geschütztem Bindestrich zusammenhalten. Mit dem längsten Titel der Rubrik prüfen.

**P1-5 · Schlagzeilen mit fünf Zeilen in Listen mit Vorschaubild (Kriterium 4: höchstens vier).**
Ort: 390 px, `rubrik.html` „30 Jahre Tamilschule Aarau: Von 37 auf 78 Kinder …“ (17 px, 5 Zeilen),
`suche.html` „INAIVU in Zürich: Benefizabend mit Musik und Tanz für Sehbehinderte in Sri Lanka“ (17 px, 5 Zeilen).
Vier weitere Titel stehen bei genau vier Zeilen (Rubrik, Suche, Artikel). Ursache: Textspalte von rund 200 px neben
einem rund 128 px breiten Bild.
Behebung: Vorschaubild am Handy auf 96 px (Untergrenze aus 10.2) verkleinern oder über den Text setzen; danach den
längsten Titel (81 Zeichen) prüfen.

**P1-6 · „Kino und Termine“: erster Bildschirm zu dunkel (Brief 10.1 „Der Grund der Seite bleibt hell“, Kriterium 6,
hier auf die Unterseite angewandt).**
Ort: `termine.html`, dunkler Anteil ohne Bilder 22,7 % (390) und 24,1 % (1280), Grenze 12 %; die dunkle Fläche beginnt
bei 289 px (Handy) und 314 px (Desktop) und füllt mit den Fotos fast den ganzen Rest des ersten Bildschirms.
Behebung: Den hellen Teil (Termine mit Datum und Ort) zuerst setzen und den dunklen Kino-Block darunter, oder den
Kino-Block auf der Unterseite hell setzen. Gilt die 12-%-Grenze nach Ansicht der Hauptsitzung nur für die Startseite,
ist dies ein P2.

### P2

**P2-1 · „Diese Woche“ zeigt, was nicht diese Woche ist.** Ort: `index.html` alle Breiten, `termine.html`. Unter dem
Datum „Donnerstag, 12. November 2026“ und der Überschrift „Diese Woche“ stehen „Kanguva … ab 14. November“ vom
6. November 2024, „Rathamaarey“ vom 13. Oktober 2024 und „Sardar 2 … war für den 10. September geführt“; in der Küche
„Dosa“ und „Payasam“ vom 16. Juli 2024 neben Beiträgen von 2026. Ein Leser hält „Kanguva ab 14. November“ für aktuell.
Behebung: In „Diese Woche“ nur Aktuelles (Scene, Ramayana, Diwali in Basel), möglichst mit einem Veranstalterbild mit
Nachweis; ältere Kino-Beiträge unter „Kino“ ohne den Wochenbezug.

**P2-2 · Rubrikname so groß wie ein Aufmacher.** Ort: `rubrik.html`, „Community“ 34 px (1280) und 28 px (390) über
einem Aufmacher von 40 und 30 px; zweitgrößte Schrift über der Grenze von 28/24 px aus Kriterium 4. Behebung: 28 px
am Desktop, 24 px am Handy.

**P2-3 · Bildwahl ohne Menschen, gleiches Motiv mehrfach.** Ort: erster Bildschirm `index.html` 390 und 1280
(Tempelturm, Steinrelief, Reichstag, kein Mensch); `rubrik.html` 1280 zwei Tempeltürme nebeneinander (Hamm und
Hasenheide); Hasenheide-Turm zusätzlich als Aufmacher der Startseite und im Artikel, Hamm-Turm zusätzlich in „Weitere
Geschichten“. Die Vorbilder holen ihre Wucht aus Gesichtern. Behebung: Für den ersten Bildschirm mindestens ein Foto
mit Menschen (z. B. das helle Festfoto „Koovagam“ als Nebenstück nach oben); auf einer Seite nie zwei gleiche Motive
nebeneinander.

**P2-4 · Bildnachweis an wechselnden Stellen.** Ort: Aufmacher im Bild unter dem Titel; Nebenstück am Handy unter
der Schlagzeile; „Koovagam“ (1280) zwischen Bild und Dachzeile; „Sardar 2“ unter der Kachel. Behebung: eine Stelle
für alle (direkt unter dem Bild, 12 px, Leise), auch im dunklen Block.

### P3

**P3-1 · Nebenstück am Desktop 26 px.** Ort: `index.html` 1280, rechte Spalte. Abschnitt 3 sieht 20–24 px vor
(hartes Limit 28 px eingehalten). Behebung: 24 px.

**P3-2 · Rotes Foto im dunklen Block.** Ort: „Sardar 2“, 390 volle Breite, 1280 392 px breit: gesättigter roter
Hintergrund, die lauteste Stelle der Seite. Das Bild ist ein Archivbild von 2017; das steht nur im Alt-Text. Behebung:
Ausschnitt enger auf das Gesicht oder anderes Bild; „Archivbild“ sichtbar in den Nachweis.

**P3-3 · Vorspann des Aufmachers am Handy nur „Am 8. November war Deepavali.“** Ort: `index.html` 390, unter dem
Aufmacherbild. Fünf Wörter ohne neue Information, als einzelne Zeile zwischen zwei Fotos. Behebung: den zweiten Satz
mitnehmen oder den Vorspann am Handy weglassen.

## Was trägt

1. Die Ordnung hält unter mehr Bild: 16 von 16 harten Kriterien auf der Startseite, eine Schriftfamilie, Rot 0,04 %,
   Radius 0, Kopf 150 px, 6 ganze Schlagzeilen im ersten Desktop-Bildschirm.
2. Überall ein Bild ohne Baukasten: 22 Anreißer, keiner ohne Bild, keine Pille, kein Kasten; alle Commons-Bilder der
   Startseite mit Urheber und Lizenz; Platzhalter auf `kontakt.html` sichtbar als „(Beispielwert)“ markiert.
3. Lesbar für Ältere: Fließtext 18 px bei 1,6 Zeilenhöhe, 37 und 61 Zeichen je Zeile, alle Tippflächen ≥ 44 px,
   sichtbarer Fokus, „Bewegung reduzieren“ beachtet, kein Überlauf bei 200 % und 400 % Zoom.

## Bedienbarkeit (nur zur Information)

| Heuristik | 0–4 | Satz |
|---|---|---|
| 1 Sichtbarkeit des Zustands | 3 | Aktive Rubrik hell mit Linie, Suchtreffer mit Zahl; keine Angabe, wo man in langen Listen ist. |
| 2 Bezug zur echten Welt | 3 | Datumsformat und Rubriken vertraut; „Diese Woche“ mit Beiträgen von 2024 widerspricht dem. |
| 3 Kontrolle und Freiheit | 3 | Band bleibt stehen, Logo führt zurück; keine Brotkrumen auf Unterseiten. |
| 4 Einheitlichkeit | 2 | Bildnachweis an vier verschiedenen Stellen, Nebenstücke am Desktop im Bild, am Handy darunter. |
| 5 Fehlervermeidung | 3 | Ganze Anreißer als Tippziel, große Flächen; Suchfeld ohne Hinweis bei leerer Eingabe nicht geprüft. |
| 6 Erkennen statt Erinnern | 3 | Rubriken immer sichtbar, Kopfzeile nennt „Diese Woche“; Rubrikkacheln wiederholen das Band. |
| 7 Flexibilität | 3 | Tastatur und Zoom gehen; kein Sprunglink zum Inhalt gefunden. |
| 8 Ästhetik und Reduktion | 2 | Ruhig in Farbe und Schrift, aber zu viel Text und Verlauf im Bild. |
| 9 Fehler erkennen | 2 | Kein Leer- oder Fehlerzustand der Suche in der Probe. |
| 10 Hilfe | 2 | Kontaktseite mit Wegen zur Redaktion; sonst keine Hilfe nötig. |
