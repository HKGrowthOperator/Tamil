# Prüfung hm-tageskalender, Runde 1
Harte Kriterien: 15 von 16 erfüllt · P0: 0 · P1: 3 · P2: 5

Geprüft am 14.11.2026 über `http://127.0.0.1:8111/richtungen/hm-tageskalender/`. Maßstab: `design/brief-v3.md`,
`design/linien-auftrag.md`, `abgelehnt.md`, Hallmark-Floor; Auftrag Luis: „eine Mischung aus A und B“
(A = `hm-eigen`, B = `hm-almanac`). Die Prüfung wurde auf Anweisung der Hauptsitzung vorzeitig abgeschlossen; was
nicht zu Ende geprüft ist, steht ausdrücklich als „nicht geprüft“ da.

Messläufe:
- `tools/shots.mjs` über 13 Seiten bei 390/820/1280 (39 Aufnahmen, `--kacheln`).
- `design/vergleich/aufnahmen.mjs` über file:// lief nicht durch: nach 300 s abgebrochen, keine Ausgabe.
  Vermutete Ursache: `decode()` faul geladener Bilder kehrt nicht zurück. Deshalb lief eine Kopie im Scratch-Ordner
  über http und mit 3 s Zeitlimit je Bild, für Probe, A und B. Die Dateien in `design/vergleich/` sind unverändert.
- `sloplint --genre editorial` über 12 Dateien mit 12 Adressen.

## Erster Eindruck (3 Sätze)
Ruhig, hell, aufgeräumt; das große Tempelfoto und die Tagesziffer „13“ tragen den ersten Bildschirm, Rot erscheint
nur im Logo und bei „als Nächstes“. Nichts wirkt laut, nichts nach Baukasten, und anders als Runde 2 wirkt nichts alt.
Auf den ersten Blick ist es aber die Startseite von A mit dem Kopf von B: Der Kalender, also das, was B ausmacht,
beginnt erst unter dem ersten Bildschirm.

## Harte Kriterien
Brief v3 nennt keine nummerierte Liste mehr. Geprüft wurden die festen Punkte aus Brief v3 („Was fest bleibt“), die
Regeln aus dem Linienauftrag und die messbaren Punkte des Hallmark-Floors.

| # | Kriterium | Handy 390 | Desktop 1280 | Ergebnis |
|---|---|---|---|---|
| 1 | Logo unverändert | `bilder/logo.png` 21 817 Byte wie `design/inhalte/logo.png` | wie Handy | erfüllt |
| 2 | Nur Deutsch, keine tamilische Schrift als Schmuck | `tamil_ohne_lang` 0 auf 13 Seiten | 0 | erfüllt |
| 3 | Nur echte Inhalte aus `design/inhalte/` (Kino, Termine) | „OM“ 12 Kinos, „Jailer 2“ Kino Claudia Kloten und THADAM 13.12. Bern stehen nicht in `design/inhalte/` | wie Handy | **verletzt** (P1-1) |
| 4 | Bildnachweis an jedem Bild | 140 von 140 Bildern auf allen Seiten mit Nachweis am Bild, dazu Liste im Fuß | wie Handy | erfüllt |
| 5 | Fließtext am Handy ≥ 18 px | `--text-body` 1.125rem = 18 px | – | erfüllt |
| 6 | Kontrast WCAG 2.2 AA | aus den Tokens gerechnet: muted 7,8:1, Akzent 6,0:1 auf paper, 5,5:1 auf paper-2; keine helle Schrift auf Bild (Kennzahl 0) | wie Handy | erfüllt |
| 7 | Tippflächen ≥ 44 px | 0 Hinweise (390 und 820, 13 Seiten) | – | erfüllt |
| 8 | Kein seitliches Scrollen | 0 px | 0 px (auch bei 820) | erfüllt |
| 9 | `prefers-reduced-motion`, keine automatische Bewegung | 0 Übergänge, 0 Animationen | 0 | erfüllt |
| 10 | Schriften selbst gehostet, OFL im Ordner | Golos Text und Rethink Sans in `schriften/` mit OFL; shots: 0 nicht geladene Schriften | wie Handy | erfüllt (Widerspruch zu sloplint siehe P2-5) |
| 11 | Keine Gedankenstriche (Gate 19) | 3 Stellen (artikel-48, -71, -83), alle in wörtlichen Zitaten oder Veranstaltungstiteln | wie Handy | erfüllt |
| 12 | Keine Dachzeilen, keine Versal-Labels, keine „·“-Metazeilen | kein `uppercase` und kein `small-caps` im CSS; kein „·“ im Seitentext | wie Handy | erfüllt |
| 13 | Kein gleich großes Kartenraster, keine Verlauf-Kacheln, keine Seitenstreifen | Listen mit Linien; Radius 3 px, Schatten 0 | wie Handy | erfüllt |
| 14 | Seitenliste vollständig (11 Seiten) | alle 11 vorhanden, dazu Danke-Zustände, Rückblick, Rubriken, 12 Verzeichnis-Profile | wie Handy | erfüllt |
| 15 | sloplint ohne FAIL | 0 FAIL, 12 WARN, 150 WAIVED, 5 ANSWERED, 36 NOTE | wie Handy | erfüllt |
| 16 | Floor 12: Schlagzeile, ein Satz und Aktion bei 1280 × 800 sichtbar | – | „Per WhatsApp schicken“ bei y ≈ 548 | erfüllt |

Kennzahlen erster Bildschirm (Probe | A | B):

| Kennzahl | Probe 390 | A 390 | B 390 | Probe 1280 | A 1280 | B 1280 |
|---|---|---|---|---|---|---|
| Kopfhöhe | 143 px | 61 px | 147 px | 122 px | 73 px | 118 px |
| erste Schlagzeile ab | 226 px | 148 px | 606 px | 245 px | 97 px | 606 px |
| größte Schrift | 48 px (Ziffer „13“) | 48 | 32 | 73,6 px (Ziffer) | 73,6 | 40,2 |
| Rot ohne Bilder | 0,0 % | 0,1 % | 0,2 % | 0,0 % | 0,1 % | 0,1 % |
| Anreißer im ersten Bildschirm | 1 | 1 | 2 | 1 | 1 | 2 |
| Schatten / Radius | 0 / 3 px | 0 / 3 | 0 / 2 | 0 / 3 | 0 / 3 | 0 / 2 |

## Paarvergleich

### Probe gegen A und B (Startseite 390 und 1280, nebeneinander)
- **Material ist zu 100 % A.** `tokens.css` und `base.css` sind byteweise gleich wie bei A. Schriften (Rethink Sans
  und Golos Text), Papier (grünliches Weiß oklch 97,6 % 0,007 120), Akzent und Radius stammen ebenfalls aus A. Von
  B (Hanken Grotesk, kühles Blaugrau, Magenta-Rot) ist nichts übrig. Im CSS stehen 499 der 508 Zeilen von A
  unverändert; dazu kommen 186 neue Zeilen.
- **Der erste Bildschirm ist A mit dem Kopf von B.** Bei 390 kommen Tagesziffer, Schlagzeile, Foto, Nachweis,
  Vorspann und WhatsApp-Link aus A, in derselben Reihenfolge und mit denselben Maßen. Neu sind nur die
  Rückblick-Leiste und die Navigationszeile von B darüber; sie heben den Kopf von 61 auf 143 px. Dadurch rutscht
  „Die nächsten Feste“, bei A noch im ersten Bildschirm (y ≈ 740), unter die Kante (y ≈ 848). Bei 1280 steht der Text
  jetzt links und das Foto rechts (668 × 500). A hatte dort die Feste-Liste links neben der Schlagzeile. In der Probe
  beginnen die Tabellen bei y ≈ 727, sichtbar sind nur ihre Köpfe. Der erste Bildschirm zeigt damit **weniger
  Kalender als A und als B**.
- **Was von B kommt:** die Leiste „Rückblick 2026 in zwanzig Berichten“, die vier Ziele im Kopf, die zwei Tabellen
  auf hellem Blatt mit 2-px-Linie oben (Tag/Was/Wer/Wo sowie Film/Kinos) und die rote Zeile „als Nächstes“ zwischen
  zwei festen Linien. Echt verschmolzen ist nur eine Stelle: Die Feste-Tabelle trägt die große Tagesziffer von A
  (30 px, Gewicht 800, Wochentag darunter) in der Tag-Spalte von B.
- **Darunter wieder A:** „Zuletzt bei tamil.de“ mit Monatsköpfen, Datum links und Bild rechts (240 × 160) sowie der
  Fuß sind Zeile für Zeile die Startseite von A. Die Gliederung von B („Das Jahr 2026 in Berichten“ mit Reitern,
  großes Foto zum Tempelfest) fehlt.

### Gegen Nachrichtenmarken, Runde 2 (`r2-community-magazin`) und Runde 4 (`r4-raster`)
**Nicht geprüft.** Die Bilder wurden wegen des vorgezogenen Abschlusses nicht neben die Probe gelegt. Aus den Messwerten
allein: kein Creme- oder Sandgrund (paper hat Chroma 0,007), keine Serife, keine runden Bilder, keine bunten
Rubrikpunkte (Gegenteil von Runde 2); 0,0 % Rot, keine Versalien, keine Schräglage, kein Schatten, Radius 3 px
(Gegenteil von Runde 4).

### Die vier Punkte aus Runde 4
| Punkt | Befund |
|---|---|
| zu viel Rot, zu laut | nein: 0,0 % Rot ohne Bilder; Rot nur im Logo und bei „als Nächstes“ |
| Baukasten | nein: keine Pillen, Icons, Schatten oder „Weiterlesen“-Knöpfe, Listen mit Linien; die zwei Tabellen-Blätter sind Flächen, aber Tabellen und keine Anreißer-Kästen |
| Schrift | zwei Familien, keine verzerrten Schnitte; Zeilenfall ruhig |
| nicht hochwertig | im ersten Bildschirm eine verrutschte Kante (P1-3), darunter Kleinigkeiten (P2) |
| alt oder langweilig | nicht alt; „generisch“ nicht geprüft gegen die Vorbilder (siehe oben) |

## Befunde

### P0
Keine. shots: 39 Aufnahmen, 0 Fehler, 0 Konsolenfehler, 0 leere Bilder, 0 px Überlauf.

### P1
**P1-1 Kino- und Termindaten, die nicht in `design/inhalte/` stehen.**
- Ort: `index.html` 390/1280: Blatt „Die nächsten Feste“, Zeile „13 So, Dez. THADAM 2026, Networking- und
  Gala-Nacht, Bern“; Blatt „Im Kino“, Zeilen „„OM“ 12 Kinos, in Deutschland, Orte folgen“ und „„Jailer 2“ 1 Kino,
  Kloten, Kino Claudia, nur am Sonntag, 15. November“; Kopf des Blatts „Stand: 9. und 12. November“.
- Auch in `kino.html` („OM“, „Jailer 2“) und `termine.html` (THADAM).
- Herkunft: `docs/redaktion/rueckblick-2026.md`, Zeile 86. Dort stehen sie als **wartende** Radar-Entwürfe 54, 4
  und 5, nicht freigegeben. `design/inhalte/inhalte.json` nennt nur „Scene“ und „Ramayana: Rise of a Legend“
  (freigegeben am 09.11.) und den Termin Diwali Basel. „nur am Sonntag“ steht auch im Entwurf nicht; dort heißt es
  „am 15. November zum Spezialpreis“.
- Behebung: drei Zeilen streichen und „Stand“ auf „9. November“ zurücksetzen. Oder, falls die Hauptsitzung die
  Entwürfe freigibt, sie wörtlich und sichtbar als „Entwurf, noch nicht freigegeben“ kennzeichnen. „nur“ in jedem
  Fall streichen.

**P1-2 Die Mischung trägt im ersten Bildschirm nicht: A mit eingeklebten Tabellen.**
- Ort: `index.html` erster Bildschirm 390 × 844 und 1280 × 800.
- Messwerte: Kopf 143 px (A 61). Bei 390 beginnt das Feste-Blatt bei y ≈ 848, also unter der Kante; bei 1280 bei
  y ≈ 727, nur Kopfzeilen sichtbar. Ein Anreißer im ersten Bildschirm; Tokens, Grundstil, Schriften und Papier sind
  gleich wie bei A.
- Behebung, mindestens eines davon, besser beides:
  - (a) Den Kalender in den ersten Bildschirm holen. Bei 1280 das Foto auf 5 Spalten verkleinern und das
    Feste-Blatt mit den nächsten drei Zeilen in die Textspalte unter den Vorspann stellen (oder neben die
    Schlagzeile, wie A es mit der Liste tat). Bei 390 die Rückblick-Leiste in „Mehr“ verschieben (spart 44 px) und
    die nächste Festzeile („15 So, Nov. Deepavali-Feier, als Nächstes“) direkt unter die Tagesziffer setzen, vor die
    Schlagzeile oder vor das Foto.
  - (b) Eine Materialentscheidung von B sichtbar übernehmen statt nur seiner Bauteile. Beispiel: die Ordnung von B
    (Tabellenrhythmus, 2-px-Linien, Blatt auf Grund) auch für „Zuletzt bei tamil.de“, oder das kühlere Papier von B
    als Grund. Eine dritte Schrift kommt nicht dazu.

**P1-3 Verrutschte Kante im Kopf am Handy (erster Bildschirm).**
- Ort: alle Seiten, 390, Navigationszeile „Termine Kino Community Verzeichnis“.
- Messwert: Die Trennlinie über der Zeile beginnt bei x = 4 px, der Text von „Termine“ bei x ≈ 12 px. Logo,
  Datum, Schlagzeile und Foto stehen bei x = 16 px.
- Ursache: `.haupt { margin-left: calc(-1 * var(--space-sm)) }` (−12 px) bei ≤ 760 px, zusammen mit
  `padding-inline: var(--space-xs)` (8 px) bei ≤ 400 px.
- Behebung: Bei ≤ 400 px `margin-left: calc(-1 * var(--space-xs))`, damit der Text auf 16 px steht. Die Linie
  gehört an den `.wrap` oder auf die volle Breite, nicht an `.haupt`.

### P2
- **P2-1 Vergangener Termin unter „Die nächsten Feste“.** `index.html` 390/1280: Die erste Zeile ist „8 So, Nov.
  Deepavali, das Lichterfest“, über dem Blatt steht „Stand: Freitag, 13. November“. Behebung: Auf der Startseite die
  vergangene Zeile weglassen oder das Blatt „Feste im November und Dezember“ nennen.
- **P2-2 Drei linke Kanten in einer Spalte am Handy.** `index.html` 390, zweiter Bildschirm: Das Tabellen-Blatt
  beginnt nach Augenschein bei x ≈ 8 px, sein Text bei 24 px, Aufmacher und „Zuletzt bei tamil.de“ bei 16 px.
  Behebung: Blatt bündig auf 16 px, Innenabstand 16 px; oder Blatt randlos über die volle Breite.
- **P2-3 Titel stößt ans Bild.** `index.html` 390, „Zuletzt bei tamil.de“, August, „Bundestagsdrucksache:“: Das
  lange Wort läuft bis etwa 2 px an das Vorschaubild. Behebung: `hyphens: auto` (die Seite hat `lang="de"`) oder
  mindestens 12 px Spaltenabstand.
- **P2-4 Gestrichelte Platzhalter-Rahmen brechen um.** `index.html` 390, Kino-Blatt: „Orte folgen“ steht in zwei
  gestrichelten Teilrahmen. Ebenso bei 1280 im Fuß: „Impressum und Datenschutz folgen“. Behebung:
  `white-space: nowrap` oder Platzhalter als eigene Zeile. Für „OM“ entfällt das mit P1-1.
- **P2-5 sloplint meldet Ersatzschrift.** 11 WARN „fonts did not load (rethink-sans-latin-wght-normal.woff2)“ in
  der Render-Stufe, während shots 0 nicht geladene Schriften meldet. Nicht abschließend geklärt (nicht geprüft).
  Behebung: neu aufnehmen. Bleibt die Warnung, `src`-Pfad und `unicode-range` der Rethink-Sans-Datei prüfen.

### P3
- Hallmark NOTE 58: 496 bis 1 120 sichtbare Wörter je Seite, Schlagzeile des Aufmachers 8 Wörter, Vorspann
  28 Wörter. Für eine Nachrichtenseite vertretbar, nur zur Information.

### Nicht geprüft
- Paarvergleich mit zwei Nachrichtenmarken, mit Runde 2 und mit Runde 4 (Bilder nicht angesehen).
- Sichtprüfung der Unterseiten `artikel`, `termine`, `kino`, `rubrik`, `verzeichnis`, `verzeichnis-eintrag`,
  `einreichen`, `werben`, `buchen`, `kontakt` und `rueckblick`. Die Aufnahmen liegen vor, die Technik ist sauber
  (0 Fehler, 0 Überlauf, 0 Tippflächen-Hinweise), angesehen wurden sie nicht.
- Zoom auf 200 % und Bedienung mit der Tastatur.
- Kontrast im Browser gemessen: nur aus den Tokens gerechnet.

## Was trägt
1. Die Feste-Tabelle ist die eine echte Verbindung von A und B. Die Tagesziffer von A steht in der
   Tag/Was/Wer/Wo-Ordnung von B, Rot nur für „als Nächstes“ zwischen zwei festen Linien. Ruhig, eigen, und so
   gehört es nur zu tamil.de.
2. Überall Bilder, jedes mit Nachweis: 140 von 140. Das Aufmacherfoto ist bei 1280 groß (668 × 500), die Liste hat
   je Beitrag ein Foto.
3. Die Technik ist sauber: 0 Fehler auf 39 Aufnahmen, 0 FAIL in sloplint, Kontrast der Tokens ab 5,5:1, keine
   Bewegung.

## Bedienbarkeit (nur zur Information)
| Heuristik | 0–4 | Satz |
|---|---|---|
| 1 Systemstatus | 3 | „Stand“ an jedem Blatt, „als Nächstes“ markiert. |
| 2 Sprache der Nutzer | 4 | Deutsch, klare Wörter (Termine, Kino, Verzeichnis). |
| 3 Kontrolle und Freiheit | 3 | „Mehr“-Menü und Fuß führen überall hin. |
| 4 Konsistenz | 3 | Gleicher Kopf und Fuß; linke Kanten am Handy uneinheitlich (P1-3, P2-2). |
| 5 Fehler vermeiden | 3 | Platzhalter sichtbar gekennzeichnet; vergangener Termin unter „nächste“ (P2-1). |
| 6 Wiedererkennen | 4 | Datum, Ort und Veranstalter je Zeile ablesbar. |
| 7 Flexibilität | 2 | Keine Filter auf der Startseite; Kino nach Stadt erst auf der Unterseite. |
| 8 Ästhetik, Minimalismus | 3 | Ruhig; der Kopf am Handy kostet 17 % des Bildschirms. |
| 9 Fehler erkennen | – | Formulare nicht geprüft. |
| 10 Hilfe | 2 | Kein Hinweis, wie man einen Termin einreicht, im ersten Bildschirm. |
