# Kritik feed, Runde 1
Punkte: 26/40 · Slop-Test: bestanden · Template-Geruch: 3/4 · **Urteil: überarbeiten**

Grundlage: eigene Aufnahmen mit `tools/shots.mjs --kacheln` bei 390/820/1280 (beide Seiten), dazu eigene Zustandsaufnahmen
(„Mehr“ offen bei 390 und 1280, gescrollt in „Diese Woche“ und im Artikel bei 1280, Tastaturfokus).
`bericht.json`: 0 Fehler, kein Überlauf, keine Konsolenfehler, alle Schriften geladen, keine zu kleinen Tippflächen,
kein Tamil ohne `lang`. Detektor `npx impeccable detect`: keine Treffer. Inhalte gegen `prototyp/content/posts.json`
geprüft: Titel, Vorspann, Daten (`datum_original`) und Länderliste stimmen; „visumfrei ab 1. Oktober 2024“ stammt aus
der Zwischenüberschrift des Beitrags. Nichts erfunden.

## Erster Eindruck (3 Sätze)
Bei 390 steht „Kanguva“ riesig in Logo-Rot oben, die ganze Überschrift ist ohne Scrollen lesbar, darunter das Filmbild
und eine rote Fläche: Die eine Geschichte ist sofort da, und es sieht nach keiner App-Vorlage aus. Das gekippte
„.de“ aus dem Logo ist ein eigenes, nur zu tamil.de passendes Zeichen, und „Diese Woche“ als bildloser Kinoaushang
löst das Problem „Termine ohne Foto“ überzeugend. Was die Skizze vom Zeigen trennt, ist handwerklich: die feste
Leiste liegt am Desktop wie ein Fremdkörper über Bild und Text, das Länderzeichen erklärt sich nicht selbst, und Rot
mit schwerer schmaler Schrift auf Weiß streift den Boulevard-Ton, den der Auftraggeber gerade nicht will.

## Heuristiken

| # | Heuristik | Punkte | Begründung |
|---|---|---|---|
| 1 | Systemstatus | 3 | `aria-current` im Artikel sichtbar unterstrichen, „Mehr“ wird beim Öffnen rot; auf der Startseite keine aktuelle Rubrik markiert. |
| 2 | Sprache der Nutzer | 3 | Nur Deutsch, klare Wörter („Im Kino“, „Alle 11 Spielorte“); „.de/.at/.ch“ liest ein Älterer aber als Webadresse, nicht als „gilt hier“. |
| 3 | Kontrolle | 3 | Ganzes Cover ein Ziel, „Mehr“ ohne Skript auf- und zuklappbar; schließt nicht per Escape oder Tipp daneben. |
| 4 | Konsistenz | 3 | Zeichen, Rubrikzeile und Leiste durchgängig; die Leiste ist aber auf Start (halbe Breite) und Artikel (Stummel) am Desktop zwei verschiedene Dinge. |
| 5 | Fehlervermeidung | 2 | `.de .at .ch` oben rechts sieht wie ein Länder-Umschalter aus, ist aber kein Link; Kopfwort-Regel kann bei langen ersten Wörtern überlaufen. |
| 6 | Wiedererkennen | 3 | Rubriken als Wörter in Daumenreichweite, kein Icon-Raten; Rubrik und Datum immer an gleicher Stelle. |
| 7 | Flexibilität | 2 | Keine Suche, keine Abkürzung zu Kino nach Stadt; für eine Skizze erwartbar. |
| 8 | Ästhetik/Minimalismus | 3 | Zwei Farben, zwei Schriften, harte Kanten, wechselnde Abstände; Abzug für die durchlaufende rote Fläche am Handy und den Desktop-Stummel. |
| 9 | Fehlerhilfe | 2 | Nicht vorhanden (Skizze). |
| 10 | Hilfe | 2 | Das Zeichensystem soll sich über `.de .at .ch` im Kopf erklären, tut es aber nicht. |
| | **Summe** | **26/40** | |

## Slop-Test und Kategorie-Reflex
- Keine Seitenstreifen, kein Verlaufstext, kein Glas, keine Hero-Zahl, kein Kartenraster, kein Modal: **bestanden**.
- 1. Ordnung (Diaspora-Magazin → Gold, Ornament, Bollywood): vermieden.
- 2. Ordnung (Gen-Z-Magazin, das nicht Creme und nicht App sein darf → riesige schmale Plakatschrift und eine
  Volltonfläche): **teilweise getroffen**. Das ist eine erratbare Antwort; gerettet wird sie durch das Länderzeichen,
  das nur hier Sinn ergibt. Siehe P2 zum Boulevard-Ton.

## Verbotsliste
Keine Übereinstimmung: kein Dunkel, kein Gold, keine Tamil-Schrift, kein Laufband, keine Pillen, keine runden Karten,
keine Story-Kreise, keine Icons über Überschriften, keine 01/02/03, keine rote Platte *über* dem Bild (Rot liegt
darunter bzw. daneben). Schriften (Sofia Sans Extra Condensed, Atkinson Hyperlegible Next) stehen weder auf der
impeccable-Ausschlussliste noch auf der Liste der verbrannten Schriften.

## Befunde

### P0
- keine. `bericht.json` ohne Fehler bei allen sechs Aufnahmen.

### P1
- **Artikel, 1280 (und 820–1280), feste Leiste `.seite-artikel .leiste`:** Am Desktop schrumpft die Leiste auf einen
  356 px breiten grau-roten Stummel unten links. Im ersten Bildschirm liegt er mitten auf dem Passfoto, beim Scrollen
  verdeckt er den Zeilenanfang der Textspalte (Spalte beginnt bei x = 288, Stummel reicht bis 356; in der Aufnahme
  ist „Australien“ zur Hälfte verdeckt). Der Artikel soll ruhig sein; so wirkt er im ersten Desktop-Bildschirm
  kaputt. **Behebung:** Ab 900 px die Leiste nicht fest stellen, sondern als Kopfnavigation in die linke Meta-Spalte
  (`.artikel-meta`) oder oben in den Kopf setzen; „Teilen“ steht dort ohnehin schon unter dem Vorspann. Falls fest
  bleiben soll: volle Breite und `padding-bottom` auf `main`, damit nichts darunter liegt.
- **Startseite, 1280, feste Leiste in der linken Hälfte:** Beim Scrollen durch „Diese Woche“ liegt der graue Balken
  über den Termintiteln der linken Spalte (Aufnahme: der Bereich unter „Diwali in Basel“ und die Fußlinie werden
  abgeschnitten). Am Desktop gibt es keinen Daumen; die Begründung „Daumenreichweite“ trägt hier nicht. **Behebung:**
  Leiste ab 900 px nur im ersten Bildschirm in der linken Hälfte unten (`position: absolute` im Cover statt `fixed`)
  oder als feste Kopfleiste oben; am Handy so lassen.

### P2
- **Länderzeichen, alle Breiten, `.zeichen .tld` und Kopf `.laender`:** Die Idee ist sichtbar, aber nicht lesbar.
  „.de“ neben „ab 14. November im Kino“ wiederholt nur die Webadresse; ein 65-Jähriger liest „.de“ als Domain, eine
  19-Jährige als Logo-Echo, keiner als „kommt hier an“. Die eigene Regel „das Land steht immer ausgeschrieben
  daneben“ ist auf dem Cover („ab 14. November im Kino“) und im Artikel („visumfrei ab 1. Oktober 2024“) nicht
  eingehalten. Dazu sieht `.de .at .ch` oben rechts wie ein Umschalter aus und ist keiner. **Behebung:** Land immer
  ausschreiben („in Deutschland ab 14. November“), `.de .at .ch` oben entweder zu echten Filtern machen (Links zu
  Ländern) oder weglassen; das Zeichen nur dort zeigen, wo es eine Unterscheidung trägt (Termine), nicht auf jedem Text.
- **Startseite, 390/820, Übergang Cover → „Diese Woche“:** Roter Vorspann und roter Abschnitt laufen nur durch eine
  halbtransparente Haarlinie getrennt ineinander; das Cover hat kein Ende, und am Handy ist ab dem Bild alles eine
  rote Fläche. **Behebung:** Zwischen Cover und Woche einen klaren Bruch setzen (Papierstreifen oder die Woche auf
  Papier mit roter Schrift, Cover-Vorspann auf Rot), damit die zwei Hälften auch am Handy als Gegensatz lesbar werden.
- **Tonlage, alle Breiten, `.cover-titel` und `.artikel-titel`:** Rot, sehr schwer, sehr schmal, auf Weiß, Wort an
  Wort: Das ist die Formel der Boulevardzeitung. Für einen Kinostart trägt es, für „Sri Lanka schafft Visum für
  Deutsche ab“ (Nachrichten, laut Marke „ruhig und belegt“) liest es sich wie eine Schlagzeile. **Behebung:** Im
  Artikel und für Nachrichten die Überschrift in Grau oder in geringerer Breite/Strichstärke der Sofia (z. B. 600
  statt 800), Rot nur für Rubrik und Zeichen; die volle Lautstärke den Kino-/Kulturthemen und der Startseite lassen.
- **„Mehr“-Liste geöffnet, 390 und 1280, `.alle` mit `columns`:** Die zweite Spalte beginnt höher als die erste
  („Küche“ steht über „Nachrichten“) und hat ungleiche Abstände („Küche“–„Kino“ enger als der Rest). **Behebung:**
  Statt `columns` ein Raster (`display: grid; grid-template-columns: 1fr 1fr`) mit gleicher Zeilenhöhe; Doppelungen
  mit der Leiste (Kino, Events, Community, Nachrichten) weglassen oder die Leiste-Einträge zuerst hervorheben.
- **Kopfwort-Regel, Startseite, 390, `.kopfwort` mit `33vw`:** Bei ca. 129 px Schriftgröße passt „Kanguva“; ein
  längeres erstes Wort („Spekulationen“, „Pan-India-Erfolg“, „Lichterfest“) läuft seitlich aus. Die Begründung sagt
  „kann“, eine Regel fehlt. **Behebung:** Kopfwort nur bei ≤ 8 Zeichen, sonst Titel in der zweiten Größe; oder
  Größe an die Wortlänge koppeln; mindestens `overflow-wrap: anywhere` als Sicherung. Für die Probeseite einen
  78-Zeichen-Titel ohne Gedankenstrich mitbauen.
- **Fokus auf dem Cover, 390, `.cover-link:focus-visible`:** Der graue Ring (Kontrast ca. 1,7 : 1 gegen Rot) ist auf
  Bild und rotem Vorspann kaum zu sehen. **Behebung:** Ring in Papier mit grauem `box-shadow` als zweite Kante,
  oder den Ring nur um `.cover-text` legen.

### P3
- **Artikel, 1280, `.artikel-bild`:** Das Bild steht von x = 124 bis 1024, also weder auf der Meta-Spalte noch auf der
  Textspalte; die rechte Kante fluchtet, die linke wirkt zufällig. Entweder bündig mit der Textspalte (736 px, kein
  Hochskalieren nötig) oder bis an die linke Seitenkante.
- **Startseite, 1280, Cover links:** Zwischen Logo und Rubrikzeile stehen rund 150 px leeres Papier, unter „.de ab
  14. November“ noch einmal so viel; die Überschrift sitzt dadurch etwas verloren. Kopfwort größer oder Block nach
  unten an die Leiste rücken.
- **Datum auf dem Cover:** „6. November 2024“ über einem Kinostart „ab 14. November“ macht die Skizze sichtbar alt;
  inhaltlich korrekt (`datum_original`), für den Vergleich aber ungünstig. Kein Handlungsbedarf außer einem Hinweis
  bei der Vorlage.

## Was stark ist
- **Das Länderzeichen** ist die erste Idee in vier Runden, die wirklich nur zu tamil.de passt: aus dem eigenen Logo
  abgeleitet, ohne Tamil-Schrift, ohne Kasten oder Pille. Es braucht nur eine klarere Bedeutung (siehe P2).
- **„Diese Woche“ als Kinoaushang:** riesiger Filmtitel, daneben nüchtern Land, Ort, Tag; löst „ohne Foto“ und „11
  gegen 2 Spielorte“ ohne Kartenraster und ohne Platzhalterbild. Am Desktop läuft die Naht des Covers sauber weiter.
- **Erster Handy-Bildschirm und Lesbarkeit:** eine Geschichte, Überschrift vollständig sichtbar, Fließtext 19 px in
  Atkinson Hyperlegible Next, Artikel am Handy in der Reihenfolge des Briefs und gut lesbar.

## Nachprüfung gegen `begruendung.md` (nach der Bewertung gelesen)
- „Zwei Hälften im Gegensatz“: am Desktop klar sichtbar (Papier mit roter Schrift links, Bild und Rot rechts). Am
  Handy nur als „oben Papier, unten Rot“ erkennbar; der Gegensatz verschwimmt, weil Rot ohne Bruch in „Diese Woche“
  weiterläuft.
- „Länderzeichen zeigt, wo es hier ankommt“: als Form sichtbar, als Bedeutung nicht. Die behauptete Regel „Land
  steht immer ausgeschrieben daneben“ ist auf Cover und Artikel nicht umgesetzt.
- „Leiste in Daumenreichweite, eher Fahrgastanzeige als Tab-Bar“: am Handy eingelöst; am Desktop nicht durchdacht
  (P1).
