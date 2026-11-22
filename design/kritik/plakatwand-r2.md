# Kritik plakatwand, Runde 2
Punkte: 29/40 · Slop-Test: bestanden · Template-Geruch: 3/4 · **Urteil: verwerfen** (nach Schwelle: ein offenes P1; die Idee trägt, siehe unten)

Grundlage: eigene Aufnahmen mit `tools/shots.mjs --kacheln` (390/820/1280, 0 Fehler, kein Überlauf, keine
Konsolenfehler, keine fehlenden Schriften, keine zu kleinen Tippflächen, kein Tamil ohne `lang`) und sichtbare erste
Bildschirme bei 390 × 844, 390 × 667, 820 × 1180 und 1280 × 800 (Playwright, Scratch-Ordner). Detektor
`impeccable detect`: keine Slop-Treffer, nur Qualitätshinweise (siehe P3). Begründung erst nach der Bewertung gelesen.

## Erster Eindruck (3 Sätze)

Am Handy ist das in fünf Sekunden ein Kinoplakat: Gesicht randlos oben, „KANGUVA“ über die Bildkante gezogen, darunter
vier Zeilen, jede auf volle Breite gesetzt, alles auf roter Wand, und es ist eindeutig eine Geschichte. „Diese Woche“
setzt das als Schriftplakate auf Papier fort („SCENE“ rot, „RAMAYANA:“ schwarz, „SA 21. NOV.“) und sieht nach keiner
Vorlage aus, die ich kenne. Am Desktop zerfällt die Form teilweise: viel leere rote Fläche oben rechts, und der
Mechanismus „Zusatzzeilen oben, Titelwort unten“ zerlegt Satz-Überschriften in falscher Reihenfolge.

## Heuristiken

| # | Heuristik | Punkte | Begründung |
|---|---|---|---|
| 1 | Systemstatus | 3 | `aria-current` in Artikel-Navigation und Daumenleiste, „Lesen →“ zeigt das Ziel; auf der Startseite ist kein Menüpunkt aktiv markiert. |
| 2 | Sprache der Nutzer | 4 | Nur Deutsch, ausgeschriebene Daten, „11 Spielorte in Deutschland“, „Es feiert der Basel Tamil Sangam“: klar für Mutter und Tochter. |
| 3 | Kontrolle | 3 | Ganze Cover-Fläche ist ein Link, Sprunglink, Daumenleiste mit 56 px; vier Ziele plus „Rubriken“ (Sprung in den Fuß) sind knapp, aber ehrlich. |
| 4 | Konsistenz | 3 | Plakatsatz ist auf Cover und Bögen dieselbe Regel; aber die Titelreihenfolge kippt zwischen Handy (Titelwort oben) und ab 760 px (Titelwort unten). |
| 5 | Fehlervermeidung | 3 | Große Tippflächen, kein Fehlklick-Risiko; Lese-Fehler durch umgestellte Satztitel am Desktop (P1). |
| 6 | Wiedererkennen | 3 | Rubriken am Desktop alle sichtbar, am Handy vier Kurzwege plus Fußliste; Rubrik „KINO“ als Plakatzeile gut erkennbar. |
| 7 | Flexibilität | 3 | Bildhöhe rechnet sich gegen die Titelhöhe, niedrige Handys bekommen eigene Werte, Bild nie hochskaliert; bei 1280 × 800 läuft der Titel aber unter die Falz. |
| 8 | Ästhetik/Minimalismus | 3 | Stark und eigen am Handy; am Desktop große tote Rotfläche (bei „Dosa“ rund 600 px leer) und der Bildbogen wirkt klein. |
| 9 | Fehlerhilfe | 2 | In der Skizze nicht berührt; keine Leer- oder Fehlerzustände (kein Befund, nur keine Punkte). |
| 10 | Hilfe/Orientierung | 2 | Kein Hinweis, was „Diese Woche“ umfasst oder bis wann; Termine der Kino-Bögen fehlen (in der Quelle nicht belegt, daher richtig weggelassen). |
| | **Summe** | **29/40** | |

## Befunde

### P0
- keine. `bericht.json`: 9 Aufnahmen, 0 Fehler.

### P1
- **Satz-Überschriften werden ab 760 px in falscher Reihenfolge gelesen.** Ort: `zustaende.html`, 820 und 1280,
  Aufmacher „Mango …“. `.satz-zusatz { order: -1 }` stellt die Zusatzzeilen nach oben und das Titelwort nach unten.
  Bei „Kanguva – Ein tamilisches Kino-Highlight …“ funktioniert das (Versprechen oben, Filmtitel unten, wie ein
  Plakat). Bei einem normalen Satztitel liest man „erzielt Rekordpreis bei Auktion im Sri Kurinchikumaran Tempel in
  Gummersbach“ und erst 300 px tiefer „MANGO“: ein Satz ohne Subjekt, der wie ein Fehler aussieht. Die meisten
  Archivtitel sind Sätze („Sri Lanka schafft Visum für Deutsche ab“), der Fall ist also die Regel, nicht die Ausnahme.
  Die eigene Regel der Skizze (eigene Titelzeile nur vor Doppelpunkt oder Gedankenstrich) wird bei „Mango“ schon nicht
  eingehalten. **Behebung:** Umstellung nur, wenn der Titel einen Doppelpunkt oder Gedankenstrich hat (eigene Klasse,
  z. B. `.wand--marke`); sonst Titelwort oben, Zusatzzeilen direkt darunter wie am Handy. Für Satztitel lieber das
  erste Nomen nicht abspalten, sondern den ganzen Satz im Plakatsatz setzen.

### P2
- **Desktop 1280 × 800: der Titel läuft unter die Falz.** Ort: `index.html`, 1280 × 800, „KANGUVA“. Die Wand ist auf
  `100svh − Kopf` angelegt, der Inhalt braucht ~70 px mehr; das wichtigste Wort ist im ersten Bildschirm nur zu zwei
  Dritteln zu sehen (gemessen: Titelunterkante 869 px). Kein gewollter Anschnitt, sondern Überlauf. **Behebung:**
  Titelbreite (`--titel-breite`) auch an die Höhe koppeln, z. B. `min(…cqi, …svh)`, oder Zusatzzeilen bei niedrigen
  Fenstern kleiner setzen.
- **Desktop: große leere Rotfläche, kleiner Bildbogen.** Ort: `index.html` und `zustaende.html`, 820 und 1280,
  oberes rechtes Viertel der Wand; bei „Dosa“ rund 600 px reines Rot zwischen Fuß und Titel. Das Bild (448 × 538)
  steht unten rechts in der Ecke und ist am Desktop nicht „überlebensgroß“. Die Form wirkt dort eher wie Spalte links
  plus Foto rechts als wie eine Wand. **Behebung:** Wandhöhe am Inhalt statt am Fenster ausrichten, wenn Titel kurz
  ist; Bildbogen höher in die Wand ziehen (oben anschneiden statt unten parken); mit Originalbildern (2190 px) erneut
  prüfen.
- **Kleines Handy 390 × 667: Bild wird zum 125-px-Streifen, „KANGUVA“ liegt auf dem Gesicht.** Ort: `index.html`,
  390 × 667. Überschrift ist vollständig im ersten Bildschirm (Pflicht erfüllt), aber vom Gesicht bleiben nur Stirn und
  Augen; die Plakatwirkung ist dort weg. **Behebung:** Rubrikzeile „KINO“ bei niedriger Höhe in den Kopf ziehen
  (spart ~40 px), Zusatzzeilen auf 3 statt 4 Zeilen umbrechen, oder Mindesthöhe des Bildbogens ~180 px.
- **Artikel: roter Wandstreifen hinter dem Nachrichtenbild.** Ort: `artikel.html`, alle Breiten, `.artikel-bild`. Bei
  einer ruhigen Nachricht (Visum) ist eine vollbreite rote Fläche ab Bildmitte das lauteste Element der Seite und
  widerspricht „ruhig im Text“ und der Tonlage „Nachrichten ruhig und belegt“. **Behebung:** Streifen nur für Kino,
  Kultur, Community; bei Nachrichten eine dünne rote Linie oder nichts.

### P3
- **Rubrik „Kino“ für Beitrag 9711:** in `posts.json` steht `kategorien: ["news"]` (Chip `kinostart`). „Kino“ ist eine
  echte Rubrik und inhaltlich richtig, aber eine redaktionelle Umordnung; im Theme muss die Zuordnung aus den Daten
  kommen.
- **Zeilengrößen springen.** Ort: `zustaende.html` 390, „Kurinchikumaran“ (62 px) gegen „Tempel in Gummersbach“
  (44 px). Gewollt (Bannermaler), aber die letzte Zeile wirkt wie ein Nachsatz. Umbruch so wählen, dass die letzte
  Zeile nicht die kleinste ist.
- **Detektor:** `tight-leading` (artikel.html, 1,22) und `cramped-padding` an `.wand-fuss` und `.bogen`: die Linie
  über dem Fuß sitzt mit 8 px dicht am Text; vertretbar, im Ausbau 12 px.
- **Bricolage Grotesque** ist nicht auf der Ausschlussliste, aber seit 2024 eine sehr häufig gegriffene „markante“
  Google-Schrift. Bei 75 % Breite und 800 wirkt sie hier eigen genug; beobachten, dass sie im Ausbau nicht als
  Normalbreite auftaucht, dort kippt sie ins Bekannte.
- Startseite ohne `aria-current` in der Navigation.

### Inhalte (geprüft gegen `posts.json` und Brief Abschnitt 8)
Titel, Daten (`datum_original`), Lesezeiten, Bildmaße, Vorspann und Länderliste von 9655 stimmen. Zustände 9556
(82 Zeichen, 692 × 359, 27.06.2024) und 9591 (4 Zeichen, 900 × 409, 16.07.2024) stimmen. Radar-Einträge entsprechen
dem Brief; „Sa“ für den 21.11.2026 ist richtig. Alt-Text nennt Suriya, der im Beitragstext als Hauptdarsteller steht.
WhatsApp-Kanal ist der echte (laut `inhalte.md`). Nichts erfunden, keine Bildnachweise, keine Platzhalterbilder.

### Verbotsliste und Runde 3
Keine Pillen, keine Rundungen, keine Story-Kreise, keine Knopfreihen, kein rosa Kasten, keine 01/02/03, kein Tamil,
kein Dunkel/Gold, keine verbrannten Schriften. Vergleich mit dem abgelehnten Aufmacher aus Runde 3: dort eine
abgerundete rote Karte neben/auf einem abgerundeten Foto mit Etikett und zwei Knöpfen. Hier ist Rot randlos die Fläche
selbst, das Foto ist ein angeschnittener Bogen, die Schrift steht ohne Kasten und läuft über die Bildkante. Am Handy
bleibt eine Ähnlichkeit zum verbreiteten Muster „Foto oben, Farbfeld mit Titel unten“; der Plakatsatz (Zeile auf
Breite, wechselnde Größen) trennt es davon. Kein Verstoß.

### Abgleich mit `begruendung.md`
Die behauptete Idee (Bannermaler-Plakatsatz, Gesicht angeschnitten, Rot als Wand) ist am Handy sofort sichtbar. Am
Desktop ist „überlebensgroß“ nicht eingelöst; die Begründung räumt das selbst ein (Skizzenbild 1024 px). Die
Umbruchregel aus der Begründung wird bei „Mango“ nicht befolgt (siehe P1).

## Was stark ist
- Der Plakatsatz ist ein echtes Signatur-Element: jede Zeile auf Wandbreite, ohne Effekt, ohne JavaScript, und er
  funktioniert für Fotos und für Einträge ohne Foto gleich (Kino-Bögen als Schriftplakate lösen den Brief-Zustand
  „ohne Foto“ besser als jedes Platzhalterbild).
- Erster Handy-Bildschirm erfüllt den Brief genau: eine Geschichte, Überschrift vollständig sichtbar auch bei 667 px
  Höhe, ganze Fläche tippbar, Bild nie hochskaliert.
- „Kinokasse“ für beide Generationen: „11“ gegen „2“ Spielorte als Plakatziffer, Atkinson Hyperlegible Next mit 18–21
  px Text, Kontraste ≥ 5,9 : 1.

## Vor einem Ausbau zu beheben
1. P1 Titelreihenfolge ab 760 px (Umstellung nur bei Doppelpunkt/Gedankenstrich).
2. Wand am Desktop: Höhe an Inhalt und Fenster koppeln, Bildbogen höher, kein Titel unter der Falz bei 1280 × 800.
3. Kleines Handy: Bildbogen nicht unter ~180 px.
4. Artikel-Rotstreifen nur für laute Rubriken.
