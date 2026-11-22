# Kritik raster, Runde 2
Punkte: 28/40 · Slop-Test: bestanden · Template-Geruch: 3/4 · **Urteil: zeigen**

Grundlage: eigene Aufnahmen (`node tools/shots.mjs … --kacheln`, 390/820/1280, Scratch-Ordner), `bericht.json`
0 Fehler (kein Überlauf, keine Konsolenfehler, alle Bilder und Schriften geladen, keine zu kleinen Tippflächen,
kein Tamil ohne `lang`). Detektor `npx impeccable detect`: 19 Treffer, alle Kategorie *quality*, keiner *slop*
(Einordnung unter P3). Inhalte geprüft gegen `prototyp/content/posts.json` (9711, 9655) und Brief Abschnitt 8.
`begruendung.md` erst nach der Bewertung gelesen.

## Erster Eindruck (3 Sätze)
Am Desktop ein echtes Plakat: KANGUVA in schmalen roten Versalien über die volle Breite, darunter ein rotes
Haarlinienraster, dessen senkrechte Linien vom Cover bis in „Diese Woche“ durchlaufen; das wirkt gebaut, nicht
zusammengesteckt. Am Handy ist die eine Geschichte sofort da (Zeitzeile, Wort, Überschrift vollständig, Bild), die
Seite bleibt hell, rot und ohne jedes App-Muster. Schwächer ist alles, was nach dem Cover kommt: Der Fahrplan ist
gut lesbar, aber trocken, und leere Rasterfelder sehen bei 820 unfertig aus.

## Heuristiken

| # | Heuristik | Punkte | Begründung |
|---|---|---|---|
| 1 | Systemstatus | 3 | `aria-current` rot mit Unterkante in Kopf und Daumenleiste; Fokusrahmen 3 px, Cover-Fokus um die ganze Fläche. |
| 2 | Sprache der Nutzer | 3 | Klares Deutsch („11 Kinos“, „+6 weitere Städte“, „ab Do, 14. Nov. 2024“); Etiketten uneinheitlich („Kino · Kinostart“ gegen „Film · im Kino“). |
| 3 | Kontrolle und Freiheit | 3 | Sprunglink, Logo zur Startseite, Daumenleiste plus Rubrikenraster ohne JavaScript. |
| 4 | Konsistenz | 3 | Spaltenraster 3/4/5 trägt Cover, Fahrplan und Artikel-Einzug; Etikettenstil überall gleich; Rubrikbezeichnungen wechseln. |
| 5 | Fehlervermeidung | 3 | Ganze Cover-Fläche ist Ziel, Bilder nie hochskaliert, Wortgröße begrenzt; „+6 weitere Städte“ ist eine Sackgasse. |
| 6 | Wiedererkennen statt Erinnern | 3 | Navigation immer sichtbar (Kopf ab 900 px, sonst Daumenleiste), Zeit und Ort ausgeschrieben statt kodiert. |
| 7 | Flexibilität | 3 | Drei Wege zu den Rubriken, WhatsApp-Teilen als einfacher Link; keine Suche, kein Kalender-/Ortsfilter (Skizze). |
| 8 | Ästhetik und Minimalismus | 3 | Eine Farbe, eine Display-Familie mit harten Breitensprüngen, wenig Elemente; leere Rasterfelder und drei rote Signale über dem Wort kosten. |
| 9 | Fehlerhilfe | 2 | In der Skizze keine Fehler- oder Leerzustände sichtbar (z. B. Woche ohne Termine). |
| 10 | Hilfe und Dokumentation | 2 | Selbsterklärend, aber keine Orientierung, was „Diese Woche“ umfasst außer einer Unterzeile. |
| | **Summe** | **28/40** | Unteres Ende von „Good“; trägt durch Idee und Ausführung des Covers, nicht durch den Rest. |

## Slop-Test: bestanden
Keine Seitenstreifen-Ränder, kein Verlaufstext, kein Glas, keine Hero-Metrik, kein Modal, keine identischen
Karten (das Ortsraster sind Datenfelder, deren Anzahl die Information ist). Kategorie-Reflex 1. Ordnung
(„Diaspora-Magazin = Ornament, Gold, Tamil-Schrift“) vermieden. Kategorie-Reflex 2. Ordnung ist das Risiko:
rotes Haarlinienraster plus schmale Riesenversalien liegt nah am Swiss-/Brutalist-Utility-Genre. Es kippt nicht,
weil das Raster eine inhaltliche Aufgabe hat (Zeit | Was | Orte, wie ein Kinoaushang) und am Desktop die Linien
von Cover und Fahrplan sichtbar dieselben sind. Niemand würde ohne Zögern „KI“ sagen; eher „Kinoaushang“.

## Template-Geruch: 3/4
Kein Theme- oder App-Muster erkennbar. Abzug, weil „rote Linien + Condensed-Versalien“ als Stil bekannt ist und
der Fahrplan für sich allein auch eine generische Tabelle sein könnte.

## Verbotsliste: keine Übereinstimmung
Kein Nachtblau, Gold, Neon, Ornament; kein Laufband; keine Tamil-Wörter (keine tamilische Schrift auf den Seiten,
Ersatzstapel per `:lang(ta)` vorbereitet); Grund `oklch(0.985 0.004 25)` ist Weiß mit Rothauch, kein Creme;
Fließtext Atkinson Hyperlegible Next (Grotesk), keine Serife; keine Pillen (Etiketten sind reiner Text), keine
Rundungen, keine Story-Kreise, keine Knopfreihen, keine rote Platte über dem Bild, keine 01/02/03 (die großen
Zahlen „11“ und „2“ sind belegte Kinozahlen). Schriften Archivo und Atkinson Hyperlegible Next stehen weder auf der
impeccable-Ausschlussliste noch unter den verbrannten Schriften.

## Marke und Leser
- **Idee im ersten Bildschirm:** ja. Bei 390 beginnt das Cover mit einer Aushangzeile (14.11. | Kino · Kinostart,
  In deutschen Kinos, auch in 3D), dann KANGUVA über die volle Breite, dann der Satz vollständig lesbar, dann das
  Bild. Bei 1280 stehen die senkrechten Linien bei denselben x-Positionen in Cover und Fahrplan; der „Aushang“
  aus der Begründung ist sichtbar. Die behaupteten „Hallenbodenlinien der Aula“ sind eine Erzählung, keine
  sichtbare Eigenschaft; das schadet nicht.
- **Nur zu tamil.de?** Teilweise. Das Ortsraster (11 Felder gegen 2 gegen 1 Aula in Basel) macht die verstreute
  Diaspora in Mittelstädten sichtbar; das ist eigenständig. Das Cover selbst würde auch einem Festival- oder
  Kinoportal stehen.
- **19-Jährige:** Das KANGUVA-Cover ist screenshot- und teilbar. „Diese Woche“ ist für sie eher Fahrplan als
  Kultur; der Wechsel der Tonlagen (Nachrichten ruhig, Kino lebendig) ist kaum spürbar.
- **65-Jähriger:** gut bedient. Fließtext 19/20 px, Atkinson Hyperlegible, Tinte ~16:1, Rot ~6:1, Datum und Ort
  groß und ausgeschrieben. Einzige Schwäche: die Daumenleiste (siehe P2).
- **Tamil-Satz:** keine Tamil-Inhalte auf den Seiten; Stapel und `lang`-Regel vorhanden.
- **Echte Inhalte:** Titel, Vorspann, Datum, Bild, Länderliste wörtlich aus 9711/9655. „Mit Suriya und Bobby
  Deol“, „In deutschen Kinos“, „auch in 3D“ stehen im Beitragstext von 9711 (belegt). Wochentage stimmen
  (14.11.2024 Donnerstag, 21.11.2026 Samstag). „+6 weitere Städte“ statt erfundener Namen ist korrekt. Nichts erfunden.

## Befunde

**P0:** keine. `bericht.json` ohne Fehler bei allen sechs Aufnahmen.

**P1:** keine. Verbotsliste sauber, Idee sichtbar, Überschrift am Handy im ersten Bildschirm vollständig,
Artikel ruhig, nur Deutsch.

**P2**
- **Aushangzeile ohne Regel für Nicht-Termin-Cover** (index.html, alle Breiten, `.cover__zeile`): Das Cover
  stützt die Idee jetzt auf Zeit | Was | Ort. Für einen Nachrichten-Aufmacher wie „Sri Lanka schafft Visum für
  Deutsche ab“ gibt es weder Termin noch Ort; außerdem macht die riesige „14.11.“ eine zwei Jahre alte Geschichte
  (2024) optisch zu einer kommenden. Behebung: im Ausbau eine zweite Cover-Seite mit Nachrichten-Aufmacher zeigen;
  Zeitspalte dann mit Veröffentlichungsdatum oder Rubrikwort füllen, groß-rot nur für künftige Termine.
- **Leere Rasterfelder wirken unfertig** (index.html, 820: Zeile „Ramayana“ mit leerer zweiter Ortszeile; Diwali
  mit einem einzelnen umrandeten Feld und offenen Linien; 390: drittes leeres Feld bei Ramayana): Die Absicht
  („was nicht belegt ist, bleibt hell“) liest sich als Layoutfehler, weil die Linien an der Leerstelle abbrechen.
  Behebung: Ortsraster bei wenigen Orten mit Zeilenlinie über die ganze Spaltenbreite abschließen und Felder nur
  dort zeichnen, wo ein Ort steht (keine halben Kästen), oder Leerfelder bewusst schraffiert/mit Haarlinie füllen.
- **„+6 weitere Städte“ ist eine Sackgasse** (index.html, alle Breiten, `.ortsraster__mehr`): Wer wissen will,
  ob „Scene“ in seiner Stadt läuft, kommt nicht weiter. Behebung: Feld als Link auf den Beitrag oder als
  `<details>` mit allen Orten, sobald der Radar-Entwurf sie liefert.
- **Daumenleiste zu klein für Ältere** (index.html und artikel.html, 390/820, `.daumen a`): 14 px, Versalien,
  `wdth 75` mit Sperrung; das ist die Hauptnavigation am Handy. Behebung: 16–17 px, `wdth 85`, gemischte
  Schreibung oder geringere Sperrung; Höhe 56 px bleibt.
- **Tonlagen-Wechsel kaum sichtbar** (index.html, „Diese Woche“, alle Breiten): Kino und Events sprechen dieselbe
  Fahrplansprache wie eine Nachricht wäre; der Brief will Kino und Kultur „lebendig und stolz“. Behebung im
  Ausbau: für Kino-Einträge das Steckbuchstaben-Wort in kleiner Stufe (z. B. „SCENE“ rot, `wdth 62`) statt
  `„Scene“` in Satzschrift, Nachrichten bleiben in der ruhigen Stufe.

**P3**
- Drei rote Signale über dem Cover-Wort (index.html, 390 und 820: „14.11.“, „KINO · KINOSTART“, KANGUVA)
  konkurrieren; die Zeitangabe in Tinte oder kleiner würde dem Wort die Bühne lassen.
- „ab Do, 14. / Nov. 2024“ bricht bei 390 in drei Zeilen (`.zeit__klein` in der schmalen Spalte); Kurzform „ab Do 14.11.24“ oder breitere Spalte.
- Rubrik „Kino · Kinostart“ beim Cover, Beitrag 9711 ist in der Kategorie *news* (Chip „kinostart“); im Theme die
  echte Kategorie zeigen.
- „u. a.“ statt „u.a.“ im ersten Absatz von 9655: harmlose Satzkorrektur, aber der Brief verlangt Texte unverändert.
- Cover-Wort mit `overflow: hidden` (index.html, `.cover__wort`): breite Buchstaben (M, W) können laut eigener
  Messung abgeschnitten werden; im Theme Breitentabelle je Buchstabe oder `fit`-Messung.
- Artikel bei 1280: Der Einzug um 25 % soll an der Titellinie des Fahrplans stehen, ohne sichtbare Linie wirkt er
  wie eine leere linke Spalte. Eine einzige senkrechte Haarlinie an dieser Stelle würde die Idee auch im ruhigen
  Artikel einlösen.
- Detektor: 18 × „cramped-padding“ sind Fehlalarme der Linientechnik (Linien aus 1-px-Fugen über rotem Grund;
  jsdom rechnet ohne Layout, in den Aufnahmen ist überall ≥ 16 px Innenabstand). 1 × „tight-leading 1.16“ betrifft
  Überschrift/Etikett, nicht Fließtext (1,55–1,65).

## Was vor einem Ausbau zu beheben wäre
1. Zweiter Cover-Fall mit Nachrichten-Aufmacher (P2 Aushangzeile) und ein langer Titel ohne Stichwort.
2. Leerfelder im Ortsraster sauber abschließen, „+6“ verlinken.
3. Daumenleiste größer, Kino-Einträge lauter.

## Was stark ist
- **Das Cover am Desktop:** KANGUVA als Steckbuchstabentafel über die volle Breite, Bild rechts in seiner
  Originalgröße, Linien, die bis in den Fahrplan weiterlaufen. Das ist eine gebaute Seite, keine Vorlage.
- **Das Ortsraster:** 11 gegen 2 gegen 1 Aula ist sofort ablesbar und erfindet nichts; es macht die Verstreuung der
  Diaspora sichtbar und funktioniert ohne Fotos.
- **Der Artikel:** wirklich ruhig, eine Spalte, Atkinson in 19/20 px, ≤ 70 Zeichen, WhatsApp-Teilen als
  schlichter Link, Bild nie hochskaliert. Laut im Kopf, ruhig im Text ist eingelöst.
