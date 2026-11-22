# Kritik plakatwand, Runde 1
Punkte: 27/40 · Slop-Test: bestanden (knapp) · Template-Geruch: 3/4 · **Urteil: überarbeiten**

Grundlage: eigene Aufnahmen bei 390/820/1280 (`tools/shots.mjs --kacheln`, 6 Aufnahmen, 0 Fehler, kein Überlauf,
keine Konsolenfehler, keine Tippflächen-Hinweise, kein Tamil ohne `lang`), Quelltext von `index.html`, `artikel.html`,
`plakatwand.css`, Detektor `impeccable detect`. `begruendung.md` erst nach der Bewertung gelesen.

## Erster Eindruck (3 Sätze)

Am Handy funktioniert die Hauptaufgabe: Logo, Filmbild, dann eine rote Wand mit „KANGUVA“ auf voller Breite und der
ganzen Überschrift, „Lesen“ noch im ersten Bildschirm – laut, eindeutig, eine Geschichte. Der Plakatsatz (jede Zeile
auf Wandbreite gezogen) ist ein echtes, eigenes Mittel und trägt auch die Kino-Einträge ohne Foto überzeugend. Am
Desktop aber kippt das Bild zu „rote Fläche mit weißer fetter Grotesk links, Kanguva-Foto rechts“ – genau der Blick,
den der Auftraggeber in Runde 3 als generisch abgelehnt hat, und das „überlebensgroße, angeschnittene Gesicht“ der
Idee ist nirgends zu sehen.

## Heuristiken

| # | Heuristik | Punkte | Begründung |
|---|---|---|---|
| 1 | Systemstatus | 2 | Keine Markierung der aktuellen Rubrik/Seite in Kopf oder Daumenleiste; im Artikel kein Hinweis, wo man ist, außer der Rubrikzeile. |
| 2 | Sprache der Nutzer | 4 | Nur Deutsch, klare Wörter („11 Spielorte in Deutschland“, „Samstag, 21. November 2026“, „Auf WhatsApp teilen“), echte Inhalte unverändert. |
| 3 | Kontrolle und Freiheit | 3 | Ganze Cover-Fläche ist ein Ziel, Sprunglink, Daumenleiste mit 56 px; „Rubriken“ springt nur in den Fuß. |
| 4 | Konsistenz | 3 | Ein Schriftsystem, ein Rot, ruhiger Artikel mit Echo der Wand; der rote Fest-Bogen wiederholt aber die Cover-Geste und schwächt „die eine laute Wand“. |
| 5 | Fehlervermeidung | 3 | Große Tippflächen, kein Doppelsinn; der Plakatsatz hängt an handgemessenen Faktoren je Zeile – ohne Faktor/mit falschem Umbruch kippt die Optik. |
| 6 | Wiedererkennen statt Erinnern | 3 | Rubriken oben (Desktop) bzw. Daumenleiste (Handy) dauerhaft sichtbar; Rubrikmarke „KINO“ im Cover sehr klein gegenüber dem Titel. |
| 7 | Flexibilität | 2 | Keine Suche, kein Weg zu „mehr Kino“ im Cover; WhatsApp-Teilen nur im Artikel. Für eine Skizze vertretbar. |
| 8 | Ästhetik und Minimalismus | 3 | Klar, reduziert, eine Farbe, Abstände wechseln bewusst; am Desktop wirkt das Cover eher wie Rahmen + Einsatzbild als wie Plakatwand. |
| 9 | Fehlerhilfe | 2 | Nicht gezeigt (Skizze). |
| 10 | Hilfe | 2 | Nicht gezeigt (Skizze). |
| | **Summe** | **27/40** | knapp unter der Schwelle 28 |

## KI-Slop-Test: bestanden (knapp)

Keine Seitenstreifen, kein Verlaufstext, kein Glas, keine Hero-Metrik, kein Kartenraster, kein Modal, keine Icons
über Überschriften, keine Pillen, keine Rundungen. Kategorie-Reflex 1. Ordnung („Kino = Bebas/Anton, Neon, Glitzer“)
ist sauber vermieden. Kategorie-Reflex 2. Ordnung ist das Risiko: „riesige, auf Breite gezogene Versalien in
schmaler Grotesk auf Farbfläche“ ist inzwischen selbst ein verbreiteter Editorial-Konzept-Trope (und Bricolage
Grotesque ist eine Trend-Schrift der letzten zwei Jahre). Die sorgfältige Ausführung – je Zeile gezogene Größen,
Schriftplakate statt Platzhalterbildern, Kassenblock – hält es auf der richtigen Seite. Bestanden, aber nur, solange
das Bild nicht der Teil bleibt, der wie aus der Vorlage aussieht (siehe P1-1).

## Template-Geruch: 3/4

Kein Theme-/App-Geruch. Abzug für den Desktop-Aufmacher (Foto als ordentliches Rechteck in roter Fläche, Titel
daneben) und für „Diese Woche“ bei 1280 (zwei gleich gebaute Spalten nebeneinander, nur Farbe und Zeilenzahl
unterscheiden sie).

## Verbotsliste (tamil-marke)

- Kein Nachtblau/Gold/Neon, kein Creme+Serife, keine Tamil-Wörter, keine Pillen, keine Story-Kreise, keine runden
  Karten, keine 01/02/03, keine verbrannten Schriften (Bricolage Grotesque, Atkinson Hyperlegible Next, Noto Sans
  Tamil stehen nicht auf der impeccable-Liste und nicht in `abgelehnt.md`).
- **Grenzfall „rote Platte am Aufmacher“** – siehe P1-1. Technisch keine Platte über dem Bild, im ersten Eindruck am
  Desktop aber zu nah an Runde 3.

## Befunde

### P0
- keine. Bericht ohne Fehler, kein seitliches Scrollen bei 390/820/1280, keine Konsolenfehler, alle Bilder geladen,
  kein Bild hochskaliert (Cover max. 1024 × 538, Artikelbild 900 px bei 900 px Original).

### P1
1. **Startseite, 1280 (auch 820), Aufmacher: Desktop-Cover liest sich wie Runde 3, und die halbe Idee fehlt.**
   Rot links mit weißer fetter Grotesk-Überschrift, rechts das Kanguva-Foto als 716 × 460-Rechteck – das ist im
   5-Sekunden-Blick dieselbe Komposition wie der abgelehnte Gen-Z-Aufmacher (gleiches Bild, rote Fläche, weiße fette
   Schrift daneben). Gleichzeitig verspricht die Richtung „ein Gesicht überlebensgroß und vom Rand der Wand
   angeschnitten“; sichtbar ist nur der überlebensgroße *Titel*, das Bild ist ein braves Einsatzbild (am Handy ein
   ~280 px hoher Streifen, Suriyas Gesicht kleiner als „KANGUVA“). Behebung: Den Bildbogen am Desktop deutlich
   beschneiden statt einpassen – enger Ausschnitt auf das Gesicht (`object-position`, Bildbogen hochkant über die
   rechte Wandkante *und* über die Unterkante der Wand hinaus angeschnitten, z. B. 5:7 statt 16:9 in Originalgröße
   ≤ 538 px Höhe), „KANGUVA“ tiefer ins Bild greifen lassen, sodass Schrift und Gesicht *eine* Form bilden. Am Handy
   denselben engen Gesichtsausschnitt zeigen statt der ganzen Szene. Ziel: Kein Betrachter darf beim ersten Blick
   „Platte neben Bild“ sehen, sondern „Bogen auf Wand, angeschnitten“.

### P2
1. **Startseite, 390, „Diese Woche“, Fest-Bogen „SA 21. NOV.“:** zweite rote Vollfläche mit weißer Plakatschrift
   direkt nach dem Cover. Das nimmt dem Aufmacher die Alleinstellung („die eine Wand“) und lässt die Seite am Handy
   rot–papier–rot gestreift wirken. Behebung: Fest-Bogen auf Papier mit rotem Plakatsatz (wie „SCENE“) und nur einer
   roten Kante/einem roten Datumsblock, oder die rote Fläche nur ab 760 px, wo sie quer unter zwei Bögen steht.
2. **Startseite, 1280, „Diese Woche“, Kino-Bögen:** zwei gleich gebaute Spalten (Linie, „IM KINO“, Titel, Kasse) –
   der Brief verlangt „erkennbar anders gebaut, nicht gleichförmig“. Behebung: Bogenbreiten aus dem Plakatsatz
   ableiten (kurzer Titel = schmaler, hoher Bogen; langer Titel = breiter Bogen), z. B. 5/12 und 7/12 statt 1:1, oder
   „Ramayana“ quer unter „Scene“ hängen.
3. **Startseite, alle Breiten, Plakatsatz-Technik:** Jede Zeile braucht einen handgemessenen Faktor `--r` und einen
   redaktionellen Umbruch. Die Begründung beschreibt eine PHP-Breitentabelle als Lösung; in der Skizze ist das nicht
   gezeigt, und ein 78-Zeichen-Titel ist nicht durchgespielt. Unterschiedliche Zeilengrößen können bei ungünstigen
   Umbrüchen zufällig statt gemalt wirken („ab 14. November“ deutlich kleiner als „Kino-Highlight“). Behebung: Für
   Tor G2 einen zweiten Cover-Zustand mit langem Titel (z. B. der 78-Zeichen-Fall aus dem Bestand) und einen mit
   „Dosa“ zeigen; Mindest- und Höchstgröße je Zeile festlegen, damit benachbarte Zeilen nicht mehr als ~1,4× in der
   Größe springen.
4. **Startseite, 390, Aufmacher-Fuß:** Die Rubrik „KINO“ (20 px) und die Meta-Zeile gehen unter dem riesigen Titel
   unter; Brief: „Überschrift, Bild und Rubrik sind eine Einheit“. Behebung: Rubrik als kleine Plakatzeile *über*
   „KANGUVA“ an die Wand (wie „IM KINO“ bei den Bögen), Datum/Lesezeit bleiben unten.
5. **Startseite, Handy, kleine Geräte:** Die Bildhöhe ist auf 844 px Höhe gerechnet (`100svh`, min. 180 px). Bei
   390 × 667 (iPhone SE) reicht der Platz rechnerisch nicht mehr für Bild-Minimum + fünf Titelzeilen + Fuß + Daumenleiste;
   „Lesen“ und vermutlich die letzte Titelzeile rutschen unter die Leiste. Behebung: bei niedriger Höhe
   (`@media (max-height: 700px)`) Bildbogen auf ~120 px oder Titel unter dem Bild ohne Überlappung; nachprüfen.

### P3
1. **Detektor:** `tight-leading` (artikel.html, Zeilenhöhe 1,22) – betrifft Überschrift/Meta, nicht den Fließtext
   (1,62); hinnehmbar. `cramped-padding` an `.bogen` – Bögen haben nur eine obere Linie, Text links bündig ist Absicht;
   kein Handlungsbedarf, außer beim roten Fest-Bogen am Handy prüfen.
2. **Artikel, 390:** roter Streifen hinter dem Bild ist ein schönes Echo, aber am Handy nur 70 px hoch und wirkt wie
   ein Rest. Entweder höher (Bild sitzt halb auf der Wand) oder am Handy weglassen.
3. **Kopf, 820:** zwischen 760 und 899 px keine Rubriken oben, nur Daumenleiste – vertretbar, aber das Tablet-Cover
   ist schon zweispaltig; Navigation oben ab 760 px würde die Breiten angleichen.
4. **Startseite, Cover:** Datum „6. November 2024“ neben „ab 14. November“ und Events von 2026 in „Diese Woche“ ist
   inhaltlich korrekt (Originaldatum), wirkt beim Auftraggeber aber veraltet. Kein Gestaltungsfehler; im
   Vergleichsblatt erwähnen.

## Marke und Leser

- **Idee im ersten Bildschirm:** Am Handy ja (Plakatsatz, Rot als Wand, eine Geschichte). Am Desktop nur zur Hälfte
  (siehe P1-1). Passt sie nur zu tamil.de? Der Bezug zu den Bannermalern ist erst mit der Begründung lesbar; ohne
  Erklärung sieht man „Poster-Editorial“. Mit dem angeschnittenen Gesicht würde der Bezug ohne Text sichtbar.
- **Gen Z:** Das Handy-Cover ist screenshot- und teilbar; „SCENE“ als roter Riesenschriftzug hat Haltung. Ja.
- **Ältere:** Fließtext 19–21 px in Atkinson Hyperlegible Next, Zeilenlänge 62ch, Kontraste ≥ 5,9:1, Tippflächen
  ≥ 44 px, Daten ausgeschrieben. Sehr gut lesbar – die stärkste Leistung dieser Richtung.
- **Tamil-Satz:** kein Tamil im Inhalt; Noto Sans Tamil über `:lang(ta)` und `unicode-range` vorbereitet. In Ordnung.
- **Echte Inhalte:** Titel, Vorspann, Länderliste (inkl. fettem „Deutschland“) entsprechen `posts.json` 9655; Kino-
  und Event-Angaben entsprechen dem Brief; WhatsApp-Kanal ist der echte Kanal laut `inhalte.md`. Nichts erfunden.

## Abgleich mit `begruendung.md` (nach der Bewertung gelesen)

- „Titel Zeile für Zeile auf Wandbreite gezogen“, „Rot als Wand“, „Schriftplakate ohne Foto“, „Kinokasse“: sichtbar
  und gut umgesetzt.
- „Ein Gesicht überlebensgroß und angeschnitten“: **nicht sichtbar** – das Bild ist auf allen Breiten ein eingepasstes
  Querformat. Das bestätigt P1-1.
- Abgrenzung zu Runde 3 („Rot ist die Wand, nicht die Platte“): im Detail richtig, im ersten Eindruck am Desktop
  nicht überzeugend.
- Zustände (langer Titel, kleines Bild) sind in der Begründung beantwortet, aber nicht gezeigt (P2-3).

## Was stark ist

1. **Der Plakatsatz** als Signatur: eigenes, kopierbares Mittel ohne Effekt, das auch Einträge ohne Foto zu Plakaten
   macht („SCENE“, „SA 21. NOV.“) – die beste Antwort auf „Kino-Termine ohne Pressefoto“.
2. **Handy-Cover erfüllt die Hauptaufgabe:** eine Geschichte, Überschrift vollständig und „Lesen“ im ersten
   Bildschirm, ganze Fläche ist das Ziel, Daumenleiste in Reichweite.
3. **Laut im Kopf, ruhig im Text** ist eingelöst: Der Artikel ist still, eine Spalte, 19–21 px, mit einem einzigen
   roten Echo der Wand; Atkinson Hyperlegible Next ist eine durchdachte Wahl für Eltern und Großeltern.
