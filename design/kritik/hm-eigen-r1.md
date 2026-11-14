# Prüfung hm-eigen, Runde 1
Pflichten (Brief v3, „Was fest bleibt“): 7 von 8 erfüllt · P0: 0 · P1: 7 · P2: 11 · P3: 3

Grundlage: nur `design/brief-v3.md` und `tamil-marke/references/abgelehnt.md`. Keine `begruendung.md` gelesen.
Messung: `tools/shots.mjs` (390/820/1280, alle vier Seiten, 0 Fehler) und ein eigenes Playwright-Messskript (Kontrast,
Schriftgrößen, Tippflächen, Inhalt des ersten Bildschirms). `design/vergleich/aufnahmen.mjs hm-eigen` hing über `file://`
(es wartet per `decode()` auf die Bilder mit `loading="lazy"`) und wurde abgebrochen. Es gibt deshalb keine
`kennzahlen/hm-eigen.json`. Das ist ein Fehler des Werkzeugs und kein Befund an der Probe.

## Urteil in einem Satz
Die Muster der Runden 5–7 sind sauber vermieden, das Gesamtbild wirkt aber nicht „gemacht“. Die zwei auffälligsten
Gesten sind fast wörtlich Runde 4: eine riesige, oft rote Datumsziffer („14.11.“ und „KW 45“ in R4) und ein riesiges
Filmwort auf einer Vollfarbfläche („KANGUVA“ in R4, hier „Scene“ auf Grün). Darum herum liegt ein Hero nach
Landingpage-Art mit rotem Knopf.

## Erster Eindruck
Ruhig, hell und gut lesbar. Es gibt keine Dachzeilen, keine Versal-Labels, keine „·“-Metazeilen und kein Kartenraster.
Die Tageszeilen mit Ziffer, Titel und Ort sind der stärkste und eigenständigste Teil. Nach fünf Sekunden bleiben aber vor
allem drei Dinge hängen: eine 216 px große Zahl, ein roter „Beitrag lesen“-Knopf und, beim Weiterscrollen, ein grünes
Band mit dem Wort „Scene“ in 192 px. Im ersten Bildschirm steht genau eine Geschichte, am Handy ohne Foto.

## Pflichten (Brief v3 und Marke)
| Pflicht | Handy 390 | Desktop 1280 | Ergebnis |
|---|---|---|---|
| Fließtext ≥ 18 px am Handy | Vorspann, `.satz`, `.wo` und Artikeltext 18 px; Artikel Desktop 19 px | – | erfüllt |
| Kontrast WCAG AA | Mindestwert 6,03:1 (Rot `#b3282c` auf Papier, Knopftext); Grün-Feld 6,77:1; `muted` 7,2–7,9:1 | gleich | erfüllt |
| Tippflächen ≥ 44 px | `.dienste a` „Kino“ 39×44 auf allen Seiten (390/820); „Zum Festkalender“ 173×24; „Quelle“ 44×17; `.fuss li a` min-height 40 px (CSS) | – | **verletzt** |
| Kein seitliches Scrollen 390/820/1280 | `ueberlauf` 0 auf allen 12 Aufnahmen | 0 | erfüllt |
| Keine Konsolenfehler, Bilder, Schriften | 0 / 0 / 0 | 0 | erfüllt |
| Jedes Bild mit Nachweis | 4 Fotos (rb-30, rb-71, rb-37, rb-84): Nachweis am Bild mit Quellen-Link und im Fuß | gleich | erfüllt |
| Keine erfundenen Inhalte | Kino entspricht `inhalte-klar2.json` (Scene: 11 Kinos, 5 Orte + 6; Ramayana: Gütersloh, Ravensburg; Stand 9.11.); Termine stammen aus `docs/redaktion/rueckblick-2026.md` und Radar-Entwürfen; 96 Datumszeilen mit Wochentag und Rot-Logik nachgerechnet, alle richtig | – | erfüllt (siehe P1-6 zur Einordnung „Festkalender“) |
| Logo unverändert, nur Deutsch | `bilder/logo.png` 300×121 (Datei nicht byteweise verglichen), kein Tamil als Schmuck | – | erfüllt |

## Frage 1: Gemacht oder generiert?
**Vermieden** (Lob, das verdient ist): Dachzeilen, Versal-Labels mit Sperrung, „·“-Metazeilen, gleich große
Kartenraster, Bildkacheln mit Verlauf und Titel im Bild, rote Platte, Nachtblau/Gold, Sand und Serife, runde Bilder,
Pillen, Icons. Grund ist ein kühles Weiß, die Radien liegen bei 2 px, Schatten gibt es nicht.

**Daran würde ein Betrachter eine Vorlage erkennen:**
1. Hero nach Landingpage-Art: große Zahl links, große Überschrift rechts, darunter **roter Primärknopf + Textlink**
   („Beitrag lesen“ / „Per WhatsApp schicken“). Keine Nachrichtenmarke setzt unter ihren Aufmacher einen Knopf.
2. Der Abschnittskopf ist überall gleich: H2 in 48 px und Gewicht 800, ein Satz Unterzeile, rechts „Ganzer … →“
   (`.kopfzeile`). Das ist der Abschnittskopf einer SaaS-Seite.
3. Ein dunkles Vollfarbband mit **einem Riesenwort** („Scene“ in 192 px, Gewicht 800, −0,05em): das Statement-Band einer
   Vorlage und zugleich die Geste aus R4.
4. Eine einzige Zeilenform (`.tage`) wird siebenmal wiederholt: Feste, Tempel, Nachrichten, Küche, Weiterlesen,
   Kinojahr, Festkalender.
5. Abschnittsabstände von 120 px und leere Spalten im Hero. Das ist der Rhythmus einer Landingpage, keine Dichte einer
   Nachrichtenseite.

**Paarvergleich bei gleicher Breite:**
- *Guardian 1280:* Dort stehen schon im ersten Bildschirm mehrere Geschichten, gegliedert durch Spaltenlinien. Die
  Schlagzeile (~30 px) ist selbst der Link, die Dachzeile in Rot ist klein. hm-eigen zeigt eine Geschichte, die
  Schlagzeile hat 53 px in 800, ein Drittel der Breite füllt eine Zahl, darunter bleiben ~500 px leer, und zum Beitrag
  führt ein Knopf.
- *R4 Raster/Zine 1280:* gleicher Aufbau. Ein großes rotes Datum („14.11.“, „KW 45“) entspricht hier der roten
  „15“ in 216 px (Termine) und der roten „8“ in 136 px (Artikel). Das Riesenwort „KANGUVA“ entspricht hier „Scene“.
  hm-eigen ist ruhiger: kein Stempel, kein Halbton, keine Schräglage, keine schmale Schrift, keine Versalien. Die
  Gesten bleiben trotzdem dieselben.
- *R2 1280:* kein Rückfall. Kein Creme, keine Serife, keine runden Bilder, keine bunten Punkte.

## Frage 2: Trägt die Idee (Datum als Hauptfigur, Rot nur für Sonntage und Festtage)?
- **Trägt:** auf der Startseite im Tagesblatt und in den Tageszeilen, im Artikelkopf („8, Sonntag, Deepavali“ in Rot)
  und in der Legende auf der Terminseite. Die Rot-Logik ist in allen 96 Zeilen fehlerfrei umgesetzt.
- **Bricht:**
  (a) Kino: Im ersten Bildschirm steht kein einziges Datum, nur Wort und Fläche (P1-2).
  (b) Termine: Der „Festkalender“ beginnt im Januar, die kommenden Feste liegen ganz unten. Er ist zudem voller
  Nicht-Feste: Studie, App „Tamils Point“, Konsulartage, Fußballmeister, Restaurants (P1-6).
  (c) Der rote Knopf widerspricht „Rot nur für Sonntage“: Am Freitag, dem 13., sind Knopf und Logo das einzige Rot
  im ersten Bildschirm (P1-5).
  (d) Die Nachrichten tragen am 13. November die Daten 17. August, 28. Mai und 25. Mai in 48 px. Weil das Datum die
  Hauptfigur ist, sieht die Seite dadurch veraltet aus (P2-5).

## Befunde

### P0
Keine. Technik ohne Fehler.

### P1
1. **Küche-Block am Desktop zerfällt.** Bei 1280 und allen Breiten über 860 px hat `#küche .paar .tage li` das Raster
   `5.5rem 1fr 14rem auto` in einer 5fr-Spalte (~478 px). Für den Titel bleiben ~110 px, es steht **ein Wort je Zeile**
   (zum Beispiel „Bremen: / Vater / und / Sohn / …“, 12 Zeilen). Dasselbe in milderer Form bei `#community`
   (Titel über 4–5 Zeilen). *Abhilfe:* `.paar .tage li, aside .tage li { grid-template-columns: 4.5rem minmax(0,1fr) }`,
   `.wo`/`.teilen` in Spalte 2 (wie in der 760-px-Regel), oder die Liste in voller Breite und das Bild darüber.
2. **Kino-Feld wiederholt R4.** `.feld` ist eine dunkelgrüne Vollfarbfläche (Verbotsliste: „andere Vollfarbflächen“),
   darin `.plakat .film` „Scene“ in 192 px (Desktop) und 80 px (Handy), Gewicht 800, −0,05em: das Riesenwort wie
   „KANGUVA“. Der Titel „Tamilisches Kino diese Woche“ ist das „Diese Woche“-Band, das Brief v3 ausdrücklich nennt.
   Betroffen sind die Startseite (Abschnitt 3) und `kino.html` im ersten Bildschirm. Ein Bild gibt es dort nicht. Am Handy
   stößt die H2 ohne Abstand an „Scene“. *Abhilfe:* Fläche auf `paper`/`paper-2` mit Linie; Filmtitel in Titelgröße
   (≤ 32 px) mit Standbild oder Plakat, falls ein Nachweis vorliegt; Spielorte als Tageszeilen. Heißt das Band „Kino“
   und nicht „diese Woche“, trägt das Datum auch hier.
3. **Rote Ziffer in Displaygröße.** `.tag.rot .ziffer`: 216 px am Desktop und 104 px am Handy auf `termine.html`
   („15“), 136 px und 80 px in `artikel.html` („8“). An jedem Sonntag und Festtag wird damit auch der Kopf der
   Startseite zu einer 216-px-Ziffer in Rot. Das entspricht „riesige rote Titelwörter / zu viel Rot“ (R4).
   *Abhilfe:* Ziffer höchstens ~96 px am Desktop und ~56 px am Handy; in Displaygröße die Ziffer in Tinte und das Rot
   als kleine Marke (Wochentag „So“ oder Haarlinie). Die volle rote Ziffer nur in den Zeilen (48 px).
4. **Erster Bildschirm mit nur einer Geschichte.** Am Handy (390×844) ist nur die Aufmacher-H1 sichtbar, das Foto beginnt
   bei y=812, ein Foto ist also nicht zu sehen. Am Desktop (1280×800) steht eine Geschichte, die nächste Zeile kommt bei
   y≈1050; links unter „Zum Festkalender“ bleiben ~500 px leer. Das war ein Ablehnungsgrund in R4, und die Marke
   verlangt einen Aufmacher und weitere Geschichten. *Abhilfe:* Datumsblock verdichten (Ziffer und Monat in einer
   Zeile, siehe P1-3) und „Die nächsten Feste“ (3 Zeilen) in die linke Spalte des Tagesblatts setzen; am Handy das Bild
   vor den Vorspann.
5. **Knopf „Beitrag lesen“ und Kopf nach Landingpage-Art.** Gemeint sind `.aufmacher .aktionen .knopf`, ein roter
   Vollknopf, und `.kopfzeile` (H2 48 px, Unterzeile, „mehr“ rechts). Die Aufmacher-H1 und das Bild sind **nicht
   verlinkt**. Im Bogen fällt ein Weiterlesen-Knopf unter „Baukasten“; der Knopf bricht außerdem die Rot-Regel der Idee.
   *Abhilfe:* H1 und Bild als Link (`.titel-link`), keinen Knopf, WhatsApp als Textlink; Abschnittsköpfe auf 24–28 px
   ohne Unterzeile; den roten Knopf ganz streichen. Im `.teilen-block` des Artikels höchstens ein Knopf in Tinte.
6. **Der Festkalender hilft nicht beim Finden.** `termine.html` beginnt beim Januar. Die kommenden Termine (15.11.,
   21.11., 13.12.) liegen am Handy bei rund 11 000 von 13 594 px. Unter „Feste, Tempel, Vereine und Bühnen“ stehen
   Berichte, die keine Termine sind: Studie (18.3.), App (24.5., rot), Konsulartage, Meistertitel, Restaurants. Rot
   markiert dort den Sonntag eines Berichts. *Abhilfe:* Oben „Ab heute“ mit den kommenden Terminen, darunter
   „Zurückliegend“ absteigend und eingeklappt. In den Kalender nur echte Termine (Feste, Feiern, Aufführungen,
   Kinostarts); Berichte verlinkt in den Rubriken.
7. **Tippflächen (Pflicht aus Brief v3).** `.dienste a` „Kino“ ist auf allen Seiten bei 390 und 820 nur 39×44 groß;
   die Hauptnavigation der Dienste ist damit zu klein. Dazu kommen `.blatt .bis a` (173×24), `figcaption a` „Quelle“
   (44×17) und `.fuss li a` (min-height 40 px). *Abhilfe:* `.dienste a { min-width: 44px; justify-content: center }`,
   „Zum Festkalender“ als `.textlink` in eigener Zeile, `figcaption a { padding-block: 13px }` oder Quelle nur im Fuß,
   `.fuss li a { min-height: 44px }`.

### P2
1. **Tote Anker:** `index.html#kultur` und `#sport` in Kopf, Handy-Menü und Fuß (je dreimal) haben kein Ziel; die
   Rubriken Kultur und Sport fehlen auf der Startseite. *Abhilfe:* Abschnitte mit vorhandenen Beiträgen anlegen (Vaani
   Vizha, Karate, Meistertitel) oder die Links entfernen.
2. **Handy-Menü ohne Hinweis:** Bei `.rubriken-mobil summary { display: flex }` verschwindet das Aufklapp-Zeichen;
   „Rubriken“ liest sich wie gewöhnlicher Text. *Abhilfe:* Zeichen „+“ oder „▾“ ergänzen, oder `display: list-item`.
3. **Datumsblock je Seite verschieden:** Auf der Startseite (390) steht der Monat unten neben der Ziffer, im Artikel
   (390) oben, umbrochen und ~140 px entfernt. Im Artikel am Desktop steht „Sonntag, Deepavali“ abgerutscht bei
   y≈418 (Lücken 80 und 70 px). Ursache: `.tag .ziffer { grid-row: span 2 }` trifft die Spanne in `<time>`, nicht das
   Rasterelement, und `.artikel-kopf .wrap` dehnt mit `stretch`. *Abhilfe:* `.tag time { grid-row: span 2 }`,
   `.tag { align-content: start }`, `.artikel-kopf .wrap { align-items: start }`.
4. **Luftlöcher:** 180 px zwischen Bildzeile und „Die nächsten Feste“ (1280); unter dem Tempelbild ~550 px leer (`.paar`);
   `--section-gap-s` 120 px. Die Startseite ist 6 907 px hoch für ~20 Titel. *Abhilfe:* Abschnittsabstand 48–64 px,
   Bild und Liste gleich hoch oder das Bild über der Liste.
5. **Das Datum zeigt das Alter:** Bei „Nachrichten“ stehen am 13.11. die Ziffern 17 (Aug.), 28 und 25 (Mai) in 48 px.
   *Abhilfe:* Bei Berichten das Datum klein in der Zeile, die große Ziffer nur für Termine; oder nach Aktualität
   kürzen.
6. **Rot ohne Bedeutung:** `.tage li.rot` färbt Sonntage von Berichten (AiYA am 1.3., Tamils Point am 24.5.,
   Emsdetten …). Das Rot wird so zu Rauschen. *Abhilfe:* Rot nur für Festtage und für Termine, die an einem Sonntag
   stattfinden.
7. **Kino ohne Kino:** `kino.html` „Nach Stadt“ wiederholt fünfmal „Scene“, ohne Namen der Kinos, ohne Zeiten, ohne
   sichtbaren Platzhalter für Fehlendes (Brief v3: „Platzhalter sichtbar als solcher“). *Abhilfe:* eine Zeile je Film
   mit allen Städten; „Kinos und Uhrzeiten folgen“ als gekennzeichneten Platzhalter.
8. **Monatsleiste als Knopfreihe:** `.monate a` sind 12 umrandete Kästen; am Handy endet die Leiste ohne Hinweis aufs
   Scrollen nach „Jun“. *Abhilfe:* Textlinks ohne Rahmen in zwei Zeilen (6 × 2) oder ein `select`.
9. **Küchenbild:** `rb-37.jpg` (985×943) steht im Format 4:5 auf ~668×835 px. Es ist vergrößert und sehr gesättigt und
   beherrscht den Block. *Abhilfe:* Format 3:2 und kleiner, oder ein anderes Bild mit Nachweis.
10. **Satz durchgehend 800:** Alle H1 und H2 sind in Rethink Sans 800 bei 48–59 px gesetzt (Seitentitel Kino und
    Artikel-H1 59 px, H2 48 px); daneben steht Golos, eine zweite, sehr ähnliche Grotesk. Das wirkt schwer und
    gleichförmig. *Abhilfe:* H2 600 bei 24–28 px; 800 nur für die Ziffern.
11. **Eine Zeilenform für alles:** `.tage` wird siebenmal in gleicher Form wiederholt, ohne Hierarchie zwischen Termin,
    Bericht und Nachricht. *Abhilfe:* Berichte mit Bild oder Vorspann absetzen; die Tageszeile nur für Termine.

### P3
1. Die Teilen-Links in den Zeilen (`.tage .teilen`) haben 14 px, obwohl Teilen eine Kernaufgabe ist. *Abhilfe:* 16 px.
2. Im Bildnachweis der Kinoseite steht eine rohe URL („(https://silverscreen.in)“). *Abhilfe:* „Silverscreen Media“
   ohne URL.
3. Viele leere `.wo` in `termine.html` lassen die rechte Spalte ausfransen. *Abhilfe:* Ort ergänzen, wo er belegt ist,
   sonst die Spalte weglassen.

## Was trägt
1. Die Tageszeilen (Ziffer, Titel, Ort, Linien statt Kästen) mit korrektem Wochentag und folgerichtiger Rot-Logik in
   allen 96 Zeilen. Das ist der eigene Kern; er kommt ohne Dachzeilen, Versal-Labels und Metazeilen aus.
2. Der Artikel: Text in 18/19 px mit Zeilenabstand 1,7, Zeilenlänge ≤ 66ch, ruhig; Bildnachweis an jedem Bild und
   gesammelt im Fuß.
3. Die Technik: AA überall (mindestens 6,03:1), kein Überlauf, keine Konsolenfehler, Schriften selbst gehostet,
   `prefers-reduced-motion` beachtet.

## Bedienbarkeit (nur zur Information)
| Heuristik | 0–4 | Satz |
|---|---|---|
| Sichtbarkeit des Status | 3 | Das Tagesdatum steht vorn; `aria-current` ist bei Termine und Kino gesetzt. |
| Bezug zur Welt | 3 | Kalenderlogik vertraut; der „Festkalender“ ist voller Berichte. |
| Kontrolle und Freiheit | 2 | Zwei der fünf Rubrik-Links führen ins Leere. |
| Konsistenz | 2 | Datumsblock je Seite anders, Rot auch für den Knopf. |
| Fehlervermeidung | 3 | Wenig Interaktion, wenig Fehlerquellen. |
| Erkennen statt Erinnern | 2 | „Rubriken“ am Handy ohne Aufklapp-Zeichen. |
| Flexibilität | 2 | Termine ohne Einstieg „ab heute“, Monatsleiste nur als Sprung. |
| Ästhetik, Minimalismus | 2 | Ruhig, aber Leerflächen und Riesenziffern statt Inhalt. |
| Hilfe bei Fehlern | 2 | Fehlende Kinodaten nicht als Platzhalter gekennzeichnet. |
| Hilfe, Dokumentation | 2 | Legende für Rot vorhanden, sonst nichts nötig. |
