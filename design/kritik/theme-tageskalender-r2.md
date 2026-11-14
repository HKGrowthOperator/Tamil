# Prüfung Theme „Tageskalender“, Runde 2

Harte Kriterien: 10 von 14 erfüllt · P0: 0 · P1: 6 · P2: 12 · P3: 2

Geprüft: lokales WordPress `http://127.0.0.1:8086/` (Worktree `agent-a7dde36286d3ea89b`, Branch `theme/tageskalender`) gegen die
Probe `http://127.0.0.1:8111/richtungen/hm-tageskalender/`. Maßstab: `design/brief-v3.md`, `design/linien-auftrag.md`,
`abgelehnt.md`, Hallmark-Floor. Eigene Aufnahmen: `shots.mjs` auf 10 Adressen × 390/820/1280 (30 Aufnahmen, 0 Fehler),
sloplint `--render` auf 6 Adressen plus Probe, DOM-Messung mit Puppeteer (390 × 844, 1280 × 800). Gefüllte Tafeln nur aus
den Aufnahmen `wp-theme-shots/r2-gefuellt/` (Stand 22:26). Hinweis: Diese Aufnahmen sind teils älter als der Code; dort
steht im Bildnachweis noch „·“, im laufenden Stand ein Komma.

## Erster Eindruck (3 Sätze)

Das Theme setzt die Probe sehr treu um (gleiche Schriften, gleiche Größen 30/39,7 px, gleicher Datumskopf, Feste- und
Kino-Tafel), und die Werbung ist jetzt ruhig und steht nicht mehr über dem Aufmacher. Was ein Leser heute sieht, kommt
aber von den Daten: am Handy zuerst eine leere Festtafel, daneben eine Kino-Tafel, die eine Oktober-Kinowoche mit
„Stand: 14. November“ als aktuell ausgibt, und beim Klick auf Kino eine nachtblaue Titelkarte mit goldenem „KINO“.
Ordentlich und ruhig, aber mit einer Story im ersten Bildschirm und dem Leerzustand oben wirkt die Startseite dünner
als Spiegel oder Guardian bei gleicher Breite.

## Stand der neun P1 aus Runde 1

| # | Befund | behoben | Messwert |
|---|---|---|---|
| 1 | Werbung über dem Aufmacher | **ja** | Startseite 390: Schlagzeile y 390, Kino-Tafel 992–1228, erste Anzeige y 1276 (Falz 844). 1280: Blatt endet y 867, erste Anzeige y 891 (Falz 800). Kein Werbeplatz im ersten Bildschirm der Startseite. |
| 2 | Sticky-Leiste `.ad-mobile` | **ja** | Startseite 390: verborgen bei Scroll 0 und 700, sichtbar ab 1600 (Blatt endet 1252); Artikel erst ab ca. 4000; Kontakt ab 700 (kein Aufmacher). Leiste 54 px, Grund #f1f5f9, „Anzeige“ 14 px #4b545b (≈ 7:1), Link 248 × 44, ×-Knopf 44 × 44 innerhalb der Leiste. |
| 3 | Eigenanzeigen im Baukasten-Muster | **ja** | Alle Plätze jetzt Text zwischen zwei Linien: Label „Anzeige“ 14 px, Titel, ein Satz, ein unterstrichener Link. Kein Kasten, kein Knopf, keine Logo-Platte, keine Rundung. Rest: Dichte (P2-7). |
| 4 | abgeschnittene Textgrafiken als Leitbild (Kino, Termine) | **nein** (Anschnitt weitgehend weg, Textgrafik bleibt) | Kino-Rubrik: Kopfbild ist weiter der „Porattam“-Flyer (r9, 960 × 675, tamilischer Schriftzug, Termin 25.10. abgelaufen) in 358 × 239 (390) bzw. 477 × 318 (1280), per cover ca. 13/17 px in der Höhe beschnitten, Datumszeile am unteren Rand angeschnitten (1280). Termine: Kopfbild ist das runde PMS-Vereinslogo (r33, tamilischer Schriftzug), jetzt vollständig sichtbar. → P1-A |
| 5 | Gedankenstriche/„·“ in Theme- und Plugin-Texten | **teilweise** | Theme: sichtbarer Text auf 12 Seiten ohne Treffer außer importierten Titeln; Bildnachweis-Trenner jetzt Komma (`inc/bausteine.php:119`). Plugin-Frontend weiter: `tamil-site/includes/verzeichnis-ansicht.php:233` (`implode( ' · ', … )`), `werbung-ansichten.php:135, 144, 162, 223` (` – ` in Platz-, Preis- und Zeitraumtext), `meta.php:40` („DE · AT · CH“). Lokal unsichtbar, weil `/verzeichnis/` und `/werben/` 404 liefern. Admin-Texte nicht gezählt. → P1-B |
| 6 | Beispielkontakte auf Kontakt | **ja** | Kontakt 390/1280: keine Telefon- und keine WhatsApp-Nummer. Einzige Adresse `info@tamil.de`, im importierten Alttext „Mitmachen: Leser-Reporter“ (steht in `site.json` unter den Beispielwerten, vor Livegang bestätigen, P2-11). |
| 7 | Tippflächen unter 44 px (Kontakt-FAQ, Community-Link) | **ja** | `shots.mjs`: 0 Tippflächen < 44 px auf 10 Adressen bei 390 und 820, auch Kontakt und Community. Eigene Messung Kontakt 390: Fragen ≥ 44 px. Rest nur Links im Fließtext (P2-10). |
| 8 | sloplint FAIL 34 (Menüpaneel) | **ja** | FAIL 34 auf 0 von 6 Adressen. Dafür FAIL 58 auf allen 6 Adressen (siehe P1-F). |
| 9 | Festtafel mit echten Daten | **weitgehend** | Gefüllt 390: 2 Einträge, Titel je 2 Zeilen, keine Telefonnummern, Eintrag je 4 Zeilen wie in der Probe. 1280: 3 Zeilen, Titel 3 mit „…“ gekürzt, „Ort folgt“ als Platzhalter. Offen: Ortsdoppelung („…Workshops und Stände in Basel / PMS Basel / Basel“, „…im Kino Claudia Kloten / Kloten“) → P2-2. |

**Datumsbereich „15. November bis 19. Oktober“:** liegt an den Daten, die Anzeige fängt es aber nicht ab. In der Datenbank hat
nur ein Termin ein Ende: ID 228 „Jailer 2 (Tamil) im Kino Claudia Kloten“, `event_datum` 2026-10-16, `event_ende`
2026-10-19 (stimmig). In den gefüllten Aufnahmen steht er am 15. November: Verschoben wurde nur der Beginn (+30 Tage),
nicht das Ende. `tamil_termin_text()` (`inc/template-tags.php:160–171`) gibt jedes abweichende Ende ohne Vergleich aus,
`inc/schema.php:42–45` würde `endDate` vor `startDate` schreiben. → P2-3.

## Harte Kriterien

| Kriterium | Handy 390 | Desktop 1280 | Stand |
|---|---|---|---|
| 1 Kein seitliches Scrollen | 0 px (10 Adressen, auch 820) | 0 px | erfüllt |
| 2 Technik (Konsole, Bilder, Schriften) | 0 / 0 / 0 | 0 / 0 / 0 | erfüllt |
| 3 Fließtext Handy ≥ 18 px | 18 px (Meta 14/16 px) | 18–20,5 px | erfüllt |
| 4 Tippflächen ≥ 44 px (`shots.mjs`) | 0 Treffer | – | erfüllt |
| 5 Kontrast AA (Stichprobe) | Anzeige-Label 7:1, Fließtext Tinte #0c151c auf Hell | gleich | erfüllt (Stichprobe) |
| 6 Nur Deutsch, keine tamilische Schrift als Schmuck | im Satz keine | im Satz keine | erfüllt (Bilder siehe P1-A) |
| 7 Logo unverändert | `logo.png` 96 × 39 | 124 × 50 | erfüllt |
| 8 Echte Inhalte, keine falschen Angaben | Kino-Tafel: Oktober-Woche mit „Stand: 14. November“ | ebenso, im ersten Bildschirm | **verletzt** (P1-C) |
| 9 Bildnachweis an jedem Bild | ja | ja | erfüllt |
| 10 Keine Gedankenstriche, keine „·“ | Kino-Artikel, Plugin-Frontend | ebenso | **verletzt** (P1-B, P1-E) |
| 11 Keine Dachzeilen, keine Versal-Labels | Versal „KINO“ in Titelkarte | ebenso | **verletzt** (P1-D) |
| 12 Keine gleich großen Kartenraster, Verlaufskacheln, Seitenstreifen | keine | keine | erfüllt |
| 13 Werbung gekennzeichnet, untergeordnet, nicht über dem Aufmacher | erste Anzeige y 1276 | y 891 | erfüllt |
| 14 sloplint 0 FAIL | FAIL 58 auf 6 von 6 | – | **verletzt** (P1-F) |

Schriften: Rethink Sans (Überschriften) + Golos Text, selbst gehostet, zwei Familien, nicht auf der Verbotsliste.

## Paarvergleich (erster Bildschirm, gleiche Breite)

**Theme gegen Probe (390, 1280):** Satz, Größen und Farben sind gleich gemessen (h1 30/39,68 px, Abschnittstitel 22/25,6 px,
Golos 18 px). Unterschiede: Die Probe zeigt im ersten Handy-Bildschirm zwei echte Feste mit Ort, das Theme den Leersatz
„Gerade steht kein kommendes Fest im Kalender“ (y 144–366). Die Probe führt mit einem Tempel-Foto (Commons), das Theme
mit dem Protestfoto aus Bern. In der Probe kommt keine Titelkarte vor (0 Treffer „Grafik: Tamil.de“), im Theme drei.

**Theme gegen Spiegel (390/1280):** Spiegel zeigt vor dem ersten Bild drei Schlagzeilen und eine Navigationszeile, das Theme
eine einzige Geschichte plus Datumskopf. Spiegel setzt das Aufmacherbild randlos 16:10, das Theme 3:2 mit 16 px Rand und
14-px-Meta darunter. Spiegel hat am Desktop eine große Anzeige über dem Aufmacher; das Theme keine, das ist ruhiger.

**Theme gegen Guardian (390/1280):** Der Guardian trägt den Kopf mit einer Tintenfläche und stellt am Desktop sechs Bilder
in den ersten Bildschirm, das Theme ein Bild. Die Hierarchie ist beim Guardian dreistufig (Serife groß, Meta, Bild),
beim Theme zweistufig, die Tafeln sind reine Textlisten.

**Theme gegen Runde 2 (abgelehnt, „altbacken“):** R2 hat Sandgrund, Pillen-Knöpfe „Nachrichten“/„Kino“ und große
abgerundete Bilder; das Theme hat einen kühlen hellgrauen Grund, eckige Bilder, keine Pillen und keine Rubrikpunkte.
Kein Rückfall.

**Theme gegen Runde 4 Raster (abgelehnt, „laut“):** R4 setzt „KANGUVA“ rot über die volle Breite und Versal-Rubriken im
Raster; das Theme hat als größte Schrift 39,7 px und Rot nur in Logo, Tagesziffer der Feste und „als Nächstes“. Kein
Rückfall. Die einzige Stelle, die in Richtung R1 kippt, ist die nachtblaue Titelkarte (P1-D).

## Befunde

### P0
keine.

### P1

- **P1-A Textgrafik als Leitbild (Vorrunde 4, offen).** Ort: `/category/kino/` 390 und 1280, Kopfbild „Porattam“-Flyer
  mit tamilischem Schriftzug und abgelaufenem Datum, leicht beschnitten; `/events/` 390 und 1280, Kopfbild ist das
  PMS-Vereinslogo. Behebung: Kopfbilder der Rubriken nur aus Fotos mit Nachweis „Foto:“ wählen; Plakate, Flyer und Logos
  ausschließen (Bild-Meta oder ein Kurationsfeld je Rubrik); findet sich keines, Kopf ohne Bild.
- **P1-B Gedankenstriche und „·“ im Plugin-Frontend (Vorrunde 5, Rest).** Ort: `tamil-site/includes/verzeichnis-ansicht.php:233`,
  `werbung-ansichten.php:135, 144, 162, 223`, `meta.php:40`. Behebung: Komma oder eigene Zeilen statt „ · “; „bis“ statt
  „ – “ in Zeiträumen; Platzname und Maße in zwei Spalten.
- **P1-C Kino-Tafel gibt eine abgelaufene Kinowoche als aktuell aus (neu).** Ort: Startseite 1280 im ersten Bildschirm
  (Kino-Tafel y 584–843), 390 ab y 992; `/category/kino/` „Im Programm, Stand: 14. November“ und „Nach Stadt … ab
  18.10.“; Kino-Artikel „Kinoliste, Stand: 14. November“ bei Kinowoche 15.–22. Oktober. Ursache: `stand` ist
  `get_post_modified_time()` (`inc/bausteine.php`, `tamil_kino_filme()`), Vergangenes wird nicht gefiltert, anders als bei
  den Festen. Behebung: Stand aus dem Datenstand der Kinoliste (Radar-Zeitstempel oder Kinowoche) nehmen; Filme
  ausblenden, deren letzte Vorstellung oder Kinowoche vorbei ist; Leerzustand wie bei der Festtafel.
- **P1-D Nachtblaue Titelkarten mit goldenem Versal-Label als Beitragsbild (neu).** Ort: `/kino-jailer-2-kinotermine/`
  1280 Kopfbild 1178 × 662 ab ca. y 470, also im ersten Bildschirm, 390 358 × 201; `/jailer-2-knackt-…/` 390 und 1280;
  Liste „Zuletzt“ auf der Startseite 1280 mit Vorschaubildern, deren Text links angeschnitten ist („ailer 2“ knackt…“).
  Nachweis jeweils „Grafik: Tamil.de“. Das ist Runde 1 (Nachtblau mit Gold) plus Versal-Label und doppelt die
  Schlagzeile als Bild. Behebung: Bilder mit Nachweis „Grafik: Tamil.de“ (oder einem Flag) im Theme nicht ausgeben: Liste
  ohne Vorschaubild, Artikel mit Datumskopf statt Bild; die Karten nicht in den Bestand übernehmen.
- **P1-E Spielortliste im Kino-Artikel mit „–“ und „·“ (neu).** Ort: `/kino-jailer-2-kinotermine/` 390 und 1280, Abschnitt
  „Spielorte und Termine“ („Bremen – CineStar Kristall-Palast: ab 18.10.2026 · Tickets & Infos“) und Titel „… – alle
  Spielorte“. Erzeugt außerhalb des Themes (Beitragsinhalt mit Klasse `kino-liste`, `news_radar/render.py`), aber auf der
  wichtigsten Seitenart sichtbar. Behebung: Die Liste im Kino-Artikel aus den Kino-Fakten mit der Vorlage der Kino-Rubrik
  setzen (dort schon sauber: „Bremen / „Jailer 2“ / CineStar Kristall-Palast, ab 18.10. / Tickets und Zeiten“) und den
  Rohtext unterdrücken, oder `render.py` umstellen; Titelvorlage ohne Gedankenstrich.
- **P1-F sloplint FAIL 58 auf 6 von 6 Adressen (neu gegenüber FAIL 34).** Ort: 1440 px, Liste „Zuletzt“ bzw. Fuß
  (Startseite 185 Wörter ab y 2950, Kontakt 183, Kino-Artikel 161); im Artikel zusätzlich „hero carries 3 text blocks“.
  Die Probe hat denselben FAIL (173 Wörter ab y 3050), der Mangel ist also geerbt. Behebung: Anreißertexte in „Zuletzt“
  ab 1280 auf eine Zeile kürzen oder weglassen, Fußtext straffen; den Artikel-FAIL im Stempel begründet ausnehmen, falls
  die Regel für Artikel nicht gemeint ist.

### P2

1. Leerzustand oben: Startseite 390, die leere Festtafel ist das erste Element nach dem Datum (y 144–366) und schiebt die
   Schlagzeile auf y 390. Behebung: ohne kommende Feste die Tafel auf eine Zeile unter dem Aufmacher verkleinern.
2. Ortsdoppelung in der Festtafel (Rest Vorrunde 9): Spalte „Wo“ ausblenden, wenn der Ort schon im Titel oder bei „Wer“ steht.
3. Datumsbereich ohne Prüfung (`template-tags.php:160–171`, `schema.php:42–45`): Ende vor Beginn ignorieren und
   protokollieren.
4. „Die nächsten Feste“ enthält eine Kinovorstellung und einen Tanzwettbewerb: Titel „Die nächsten Termine“ oder filtern.
5. Seitentitel „Events“ (englisch) gegen Navigation „Termine“: Seitentitel angleichen.
6. Erklärsatz „Rot steht auf tamil.de für den nächsten Termin.“ (`/events/` 390 und 1280): streichen.
7. Anzeigendichte: Startseite vier „Anzeige“-Flächen (Platz 01, Billboard, Fuß, Mobil), Artikel fünf, alle Eigenwerbung,
   „Live mit dir!“ auf jeder Seite. Ohne gebuchte Werbung höchstens zwei Plätze je Seite füllen.
8. Platz 01 auf Kino und Termine im ersten Desktop-Bildschirm vor der Hauptliste (`/category/kino/` 1280 y 681–809 vor
   „Nach Stadt“, `/events/` 1280 y 595–723). Unter die erste Liste schieben.
9. Anzeige zwischen den Abschnitten am Desktop schmal und mittig gesetzt, nicht an der Rasterkante (Startseite 1280, y 891):
   an die linke Inhaltskante legen.
10. Links im Fließtext unter 44 px: „Tickets & Infos“ 127 × 22 (Kino-Artikel), „Sacnilk (via Google News)“ 202 × 20
    (Quelle), „WeTransfer“ 98 × 22 (Kontakt), jeweils 390. Zeilenhöhe oder Polsterung der Inhaltslinks erhöhen.
11. Kontakt trägt den Alttext 1:1 (Werbeformate mit Pixelmaßen, „IHR exklusives Foto“, „TamilDE Redaktion“), das liest
    sich wie das alte Portal; `info@tamil.de` vor Livegang bestätigen.
12. sloplint REFLEX 49b: Fußlinks „Termin einreichen“, „Tamil.de Production“, „WhatsApp-Kanal“ brechen bei 320 px zweizeilig.

### P3

1. Schriftstapel der Überschriften enthält „Catamaran“ (Runde 2 verbrannt) als Rückfall, vermutlich für Tamil-Zeichen;
   eine nicht verbrannte Tamil-Schrift wählen.
2. Bildnachweis „Foto: SwissTamilMedia, Events“ nennt eine Rubrik statt einer Quelle (Daten).

## Was trägt

1. Datumskopf mit Feste- und Kino-Tafel ist ein eigenes Gerüst und in Schrift, Größen und Farben genau die Probe.
2. Werbung ist jetzt ruhig und regelkonform: Text zwischen Linien, nichts im ersten Bildschirm der Startseite,
   Mobil-Leiste erst nach dem Aufmacher, ×-Knopf 44 × 44.
3. Technik sauber: 30 Aufnahmen ohne Fehler, kein Überlauf, keine Tippfläche unter 44 px laut `shots.mjs`.

## Bedienbarkeit (nur zur Information)

| Heuristik | 0–4 | Satz |
|---|---|---|
| 1 Systemstatus | 2 | „Stand“ steht überall, ist bei Kino aber das Änderungsdatum, nicht der Datenstand. |
| 2 Sprache der Nutzer | 3 | Deutsch und klar; „Events“ gegen „Termine“ bricht das. |
| 3 Kontrolle | 3 | Mobil-Leiste schließbar, 44 × 44. |
| 4 Konsistenz | 2 | Kinoliste im Artikel anders gesetzt als in der Rubrik. |
| 5 Fehlervermeidung | 2 | Ende vor Beginn wird ausgegeben. |
| 6 Wiedererkennen | 3 | Tafeln wiederholen sich auf Start, Rubrik und Termine gleich. |
| 7 Effizienz | 3 | „Kino nach Stadt“ und „Meine Stadt finden“ führen direkt zum Ziel. |
| 8 Ästhetik, Minimalismus | 2 | Ruhig, aber Leerzustand oben und vier bis fünf Eigenanzeigen je Seite. |
| 9 Fehlermeldungen | 3 | Leerzustände sind sprechend formuliert. |
| 10 Hilfe | 2 | Kontakt mit Alttext und Pixelmaßen statt kurzer Hilfe. |

## Nicht geprüft

820 nur über `shots.mjs` (Überlauf, Technik), nicht angesehen. Verzeichnis, Werben, Buchen, Einreichen sind lokal nicht
eingerichtet (404). `prefers-reduced-motion` und Tastaturbedienung nicht gemessen. Kontrast nur als Stichprobe.
