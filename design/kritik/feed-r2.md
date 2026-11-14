# Kritik feed, Runde 2
Punkte: 28/40 · Slop-Test: bestanden · Template-Geruch: 3/4 · **Urteil: zeigen** (knapp, mit den P2-Punkten unten als Auflage vor einem Ausbau)

Geprüft: `index.html` und `artikel.html` bei 390 × 844, 820 × 1180, 1280 × 900 (shots.mjs) sowie eigene Zustände bei
1280 × 800, 1280 × 720, 1366 × 768, 1440 × 900 (gescrollt, „Mehr“ offen, Tastaturfokus, Esc, Klick außerhalb).
`bericht.json`: 0 Fehler, kein Überlauf, keine Konsolenfehler, alle Schriften geladen, keine zu kleinen Tippflächen,
kein Tamil ohne `lang`. Detektor `npx impeccable detect`: keine Treffer.

## Erster Eindruck (3 Sätze)

Am Handy steht in fünf Sekunden genau eine Geschichte da: ein riesiges rotes „Kanguva“ in einer sehr schmalen, schweren
Grotesk, darunter der Rest der Überschrift, dann das Bild, und unten eine graue Schriftleiste ohne Icons. Das ist
eigenständiger als alles, was die drei abgelehnten Runden hatten: zwei Farben aus dem Logo, keine Pillen, keine
Karten, keine Rundungen, und das gekippte „.de“ aus dem Logo taucht als Zeichen wieder auf. Schwächen liegen nicht in
der Haltung, sondern in den Rändern: am verbreiteten Laptop fehlt die Navigation im ersten Bildschirm, und das
Länderzeichen sagt auf dem Cover nur, was die Überschrift schon sagt.

## Heuristiken

| # | Heuristik | Punkte | Begründung |
|---|---|---|---|
| 1 | Systemstatus | 3 | Aktuelle Rubrik im Artikel unterstrichen, „Mehr“ zeigt offen/zu über Pfeil und Rot; auf der Startseite fehlt jede Ortsangabe in der Leiste (kein „Start“). |
| 2 | Sprache der Nutzer | 3 | Durchgehend klares Deutsch, Orte und Daten ausgeschrieben; die Legende „Das Zeichen aus unserem Logo sagt, in welchem Land“ ist Erklärsprache in eigener Sache. |
| 3 | Kontrolle | 3 | Ganzes Cover ein Link, „Mehr“ schließt per erneutem Tippen; Esc und Klick außerhalb schließen nicht, und bei 1366 × 768 springt die Seite beim Öffnen um 418 px. |
| 4 | Konsistenz | 3 | Länderzeichen, Schriftrollen und Farbrollen sind auf beiden Seiten gleich; die Leiste wechselt zwischen Startseite (Kino, Events, Community, Nachrichten) und Artikel (Start, Nachrichten, Teilen) den Inhalt. |
| 5 | Fehlervermeidung | 3 | Große Ziele (Leiste 60 px hoch, Links ≥ 44 px), keine Fehlgriffe zwischen eng liegenden Zielen; „Teilen“ steht im Artikel zweimal. |
| 6 | Wiedererkennen | 3 | Rubrik über jeder Überschrift, Leiste am Handy immer sichtbar; Rubriken hinter „Mehr“ muss man kennen. |
| 7 | Flexibilität | 2 | Keine Suche, keine Abkürzungen, Desktop-Leiste nicht fest; für eine Skizze erwartbar, aber nichts darüber hinaus. |
| 8 | Ästhetik und Minimalismus | 3 | Starke, reduzierte Typografie, nur zwei Logofarben und Papier; Abzug für die doppelte Länderzeile auf dem Cover und die leere linke rote Hälfte in „Diese Woche“ am Desktop. |
| 9 | Fehlerhilfe | 2 | Keine Fehlerzustände in der Skizze; nichts zu bewerten, nichts gezeigt. |
| 10 | Hilfe | 3 | Das Zeichensystem wird einmal erklärt, Orte und Länder stehen ausgeschrieben, niemand muss raten. |
| | **Summe** | **28/40** | Untere Kante von „Good“. |

## Befunde

### P0
Keine. `bericht.json` ohne Fehler bei allen drei Breiten.

### P1
Keine offen. Geprüft gegen die Verbotsliste: kein Dunkel, kein Gold, kein Creme mit Serife, keine Tamil-Schrift (die
Seite zeigt nur Deutsch), keine Pillen, keine runden Karten, keine Story-Kreise, keine Knopfreihen, keine rosa Kästen,
keine 01/02/03, keine rote Platte über dem Bild (Rot liegt unter bzw. neben dem Bild). Schriften (Sofia Sans Extra
Condensed, Atkinson Hyperlegible Next) stehen weder auf der impeccable-Ausschlussliste noch unter den verbrannten
Schriften. Inhalte gegen `prototyp/content/posts.json` und Brief Abschnitt 8 geprüft: Titel, Vorspann, Datum
(`datum_original`), Lesezeit (`lesezeit: 2`), „Kinostart“ (`chips`), Länderliste, Spielorte und „Samstag,
21. November 2026“ (Wochentag stimmt) sind echt. Ausnahme siehe P2-2.

### P2
1. **Navigation fehlt im ersten Bildschirm am üblichen Laptop** (index.html, Desktop, `.leiste` in `.erster`). Die
   Leiste hängt unten am Cover-Block, der höher als der Bildschirm wird: bei 1280 × 800 sind 8 px sichtbar, bei
   1366 × 768 und 1280 × 720 liegt sie ganz darunter (Oberkante 772 bzw. 744). Der Brief verlangt „Marke und eine
   knappe Navigation“ im ersten Bildschirm, und `begruendung.md` behauptet, die Leiste schließe den ersten Bildschirm
   ab. Ein Klick auf „Mehr“ springt dort um gut 400 px. *Behebung:* Cover-Höhe auf genau `100svh` begrenzen und die
   Leiste als eigene Rasterzeile hineinnehmen; das Kopfwort zusätzlich über die Höhe deckeln
   (`font-size: min(15vw, 24svh)`) und das obere Polster der linken Hälfte (`7rem`) über die Höhe staffeln.
2. **Länderzeile wiederholt oder formuliert neu** (index.html, alle Breiten, `.cover-text .zeichen`; artikel.html,
   `.artikel-kopf .zeichen`). Auf dem Cover steht „.de in Deutschland ab 14. November“ direkt unter „… ab 14. November
   in Deutschland“: dieselbe Aussage zweimal, im wertvollsten Platz des Handy-Bildschirms (sie schiebt das Bild um
   rund 90 px nach unten). Im Artikel ist „Einreise aus Deutschland visumfrei ab 1. Oktober 2024“ ein neuer Satz, den
   es im Beitrag nicht gibt (dort Zwischentitel „Sri Lanka ab 1. Oktober 2024 visumfrei“, 30 Tage, Pilotprogramm); er
   verkürzt und muss je Artikel von der Redaktion geschrieben werden. *Behebung:* die Zeile nur aus Datenfeldern bauen
   (Land, Ort, Datum, die nicht schon im Titel stehen), auf dem Cover weglassen, wenn sie nichts Neues sagt; im
   Artikel den Zwischentitel unverändert übernehmen oder nur „.de Deutschland“ setzen.
3. **Das Signatur-Element braucht eine Gebrauchsanweisung** (index.html, „Diese Woche“, `.legende`). Der Brief sagt
   „nichts, was man erst erklären muss“; die Legende erklärt das Zeichen, und weil das Land überall ausgeschrieben
   daneben steht, trägt das Zeichen selbst kaum Information. Es ist damit eher Ornament als System. *Behebung:*
   Legende streichen und das Zeichen dort einsetzen, wo es unterscheidet (Termine aus .de/.at/.ch gemischt), dort
   aber selbsterklärend durch die ausgeschriebene Stadt; oder das Zeichen als Gliederung nutzen (Termine nach Land
   gruppiert, „.ch“ als Zwischenkopf).
4. **Cover am Handy ist eher Artikelkopf als Cover** (index.html, 390, erster Bildschirm). Überschrift auf Papier,
   darunter ein Bildstreifen, über dessen unteres Viertel die Leiste liegt; Bild und Schrift sind zwei gestapelte
   Teile, keine Fläche. Die 19-Jährige aus dem Brief sieht eine sehr gute Überschrift, aber kein Bild, das sie
   teilen will. *Behebung:* mit P2-2 die Doppelzeile streichen, damit das Bild höher beginnt; das Bild bis an die
   Leiste ziehen (Höhe `calc(100svh - Kopfhöhe - Leiste)` bis höchstens 538 px) und das Kopfwort mit der Unterkante an
   die Bildkante setzen, ohne Platte und ohne Text auf dem Bild.

### P3
1. **„Mehr“ schließt nicht mit Esc oder Klick außerhalb** (beide Seiten, `<details>` in `.leiste`); am Handy deckt die
   offene Liste rund 40 % des Bildschirms. *Behebung:* wenige Zeilen Skript für Esc/Außenklick und Fokus zurück auf
   „Mehr“.
2. **Kopfwort-Regel greift falsch** (`.kopfwort`, Begründung). „Erstes Wort ≤ 8 Zeichen“ würde bei „Sri Lanka schafft
   Visum …“ das Wort „Sri“ riesig setzen. *Behebung:* Kopfwort nur, wenn der Titel einen Gedankenstrich hat und davor
   ein Eigenname steht, oder redaktionell im Cockpit setzen.
3. **Leere rote linke Hälfte in „Diese Woche“** (index.html, 1280, `.termin`): unter „Scene“ und „Diwali in Basel“
   steht viel Rot ohne Inhalt, die Naht wirkt hier eher als Lücke. *Behebung:* Titel vertikal an die Unterkante der
   Zeile setzen oder die Spalten auf etwa 5 : 7 verschieben.
4. **Teilen doppelt** (artikel.html, 390): „Auf WhatsApp teilen“ unter dem Vorspann und „Teilen“ in der Leiste im
   selben Bildschirm. *Behebung:* am Handy eins von beiden.
5. **Logo-Unterzeile unlesbar klein** (beide Seiten, `.kopf-logo img` 120 px): „portal • lifestyle • entertainment“
   wird etwa 6 px hoch. Das Logo bleibt unverändert, aber am Handy auf 140 bis 150 px Breite gehen.
6. **Leiste auf der Startseite ohne Ortsmarke** (index.html): Kein Eintrag zeigt, dass man auf der Startseite ist;
   im Artikel ist „Nachrichten“ unterstrichen. *Behebung:* gleiche Logik auf beiden Seiten.

## Was stark ist

- **Schrift als Plakat, Text als Ruhe:** Das bildschirmbreite „Kanguva“ in Sofia Sans Extra Condensed ist laut, der
  Artikel in Atkinson Hyperlegible Next (19 px, 66 Zeichen, graue Überschrift) ist still. Genau „laut im Kopf, ruhig im
  Text“, und für den 65-Jährigen am Handy gut lesbar (Kontraste 6,3 : 1 und mehr).
- **„Diese Woche“ als Aushang statt Kartenraster:** Titel riesig, Ort und Tag nüchtern daneben, keine Bilder nötig,
  11 und 2 Spielorte im selben Aufbau. Das löst die Brief-Zustände „ohne Foto“ und „viele/wenige Spielorte“ sauber.
- **Graue Schriftleiste unten am Handy:** Daumenreichweite ohne Tab-Bar-Vorlage (keine Icons, keine Rundungen), wirkt
  wie eine Fahrgastanzeige und ist klar vom i-D-Vorbild abgeleitet, nicht kopiert.

## Abgleich mit `begruendung.md` (nach der Bewertung gelesen)

Die behauptete Idee ist sichtbar: die zwei Hälften (Papier/Rot, am Desktop als 50/50-Naht von Cover bis „Diese
Woche“), das gekippte Länderzeichen aus dem Logo, die Leiste in Daumenreichweite. Nicht eingelöst ist die Behauptung,
die Desktop-Leiste schließe „den ersten Bildschirm“ ab (P2-1), und das Länderzeichen trägt auf den gezeigten Seiten
weniger Information, als die Begründung ihm zuschreibt (P2-2, P2-3): bei drei von vier Vorkommen steht „.de“, und das
Land steht ohnehin ausgeschrieben daneben.

## Vor einem Ausbau zu beheben

P2-1 (Navigation am Laptop), P2-2 (keine doppelten oder neu formulierten Zeilen), P2-4 (Bild im ersten
Handy-Bildschirm stärker). P2-3 entscheidet, ob das Länderzeichen System oder Schmuck ist; das sollte vor Tor G3
geklärt sein.
