# Prüfung Theme „Tageskalender“ (tamil 2.0.0) gegen Probe hm-tageskalender, Runde 1
Harte Kriterien: 12 von 19 erfüllt · P0: 0 · P1: 9 · P2: 9

Geprüft am 14.11.2026: lokales WordPress `http://127.0.0.1:8086/` gegen die Probe `http://127.0.0.1:8111/richtungen/hm-tageskalender/`.
Seiten: Start `/`, Artikel `/protest-in-bern-gegen-den-abriss-der-thileepan-statue-in-jaffna/`. Ein Deepavali-Beitrag fehlt im
lokalen WordPress, deshalb dient dieser Artikel als Gegenstück zu `artikel.html`. Dazu `/category/community/`, `/events/`,
`/category/kino/` und `/kontakt/`, jeweils bei 390 und 1280 (shots.mjs zusätzlich bei 820). Die gefüllten Tafeln wurden nur aus
den vorhandenen Aufnahmen `wp-theme-shots/b3-start`, `b4-artikel` und `b6-termine` beurteilt. Messskript (Puppeteer),
`tools/shots.mjs` und `sloplint --genre editorial --url` für alle sechs Seiten; sloplint lief zum Vergleich auch auf Probe-Start
und Probe-Termine. Aufnahmen und Vergleichstafeln liegen unter
`/tmp/claude-0/-home-user/16175975-e412-59cc-bdc3-6fbcba0681fa/scratchpad/kritik-theme-r1/` (Unterordner `m/`).

Folgende Abweichungen hat der Theme-Bauer als bewusst angegeben. Sie sind hier nicht als Fehler gewertet, wohl aber in ihrer Wirkung:
Werbeplätze mit „Anzeige“, Werbeplatz 03 im Artikel (300 × 250), Leiste mit „Termin einreichen“/„Werben“, Suche unter „Mehr“
und keine Seitenspalte.

## Erster Eindruck (3 Sätze)

Satz, Linien, Farben und die Tageskalender-Idee (große Tageszahl, Tafel mit Stand, Tag-Spalte in jeder Liste) sind aus der
Probe genau übertragen. Schlechter wird das Theme fast nur an zwei Stellen. Die erste ist die Werbung: ein Banner über dem
Aufmacher an derselben Stelle und mit derselben Hausanzeige „tamil.de | Live mit dir!“ wie in Runde 2, dazu eine Sticky-Leiste
mit überstehendem ×-Knopf und graue Hausanzeigen-Kästen mit Icon über der Überschrift. Die zweite sind echte Daten, die die
Probe nie zeigen musste: beschnittene Textgrafiken als Leitbild, Tafel-Einträge mit Telefonnummer und Vierzeilern. Am Handy
sieht der Leser auf jeder Seite zuerst eine Anzeige und am unteren Rand eine zweite.

## Harte Kriterien

Grundlage: `brief-v3.md` (was fest bleibt), `linien-auftrag.md` (Regeln), Pflichten aus `tamil-marke` und der Hallmark-Floor.

| # | Kriterium | Handy 390 | Desktop 1280 | Ergebnis |
|---|---|---|---|---|
| 1 | Logo unverändert | Bilddatei Logo | dto. | erfüllt |
| 2 | Nur Deutsch, keine tamilische Schrift als Schmuck | keine | keine | erfüllt |
| 3 | Echte Inhalte, Platzhalter als solche erkennbar | Kontakt: WhatsApp „+49 170 123 4567“ und E-Mail „info@tamil.de“ ohne „(Beispiel)“, nur das Telefon ist markiert | dto. | **verletzt** → P1-6 |
| 4 | Bildnachweis an jedem Bild | Start 14 von 14 Fotos, Artikel 5/5, Termine 2/2, Kino 2/2 (Logos ausgenommen) | dto. | erfüllt (Inhalt der Nachweise: P2-1) |
| 5 | Fließtext am Handy ≥ 18 px | 18 px / 27–30,6 px Zeilenabstand auf allen Seiten | 18–20,5 px | erfüllt |
| 6 | Zeilenlänge Fließtext ≤ 70 Zeichen | Artikel ~36–38 | Artikel ~53–60; Listen-Anreißer ~74–76 (geschätzt) | erfüllt für Fließtext (Anreißer: P2-6) |
| 7 | Kontrast WCAG AA | 0 Textstellen unter der Grenze (6 Seiten) | 0 | erfüllt |
| 8 | Tippflächen ≥ 44 px | Kontakt: drei FAQ-Zeilen 358 × 31 px; Community: Link „Wasser für Poovathan…“ 181 × 24 px (von Hand gemessen, shots.mjs meldet nichts) | – | **verletzt** → P1-7 |
| 9 | Kein seitliches Scrollen 390/820/1280 | 0 px | 0 px (820: 0 px) | erfüllt |
| 10 | `prefers-reduced-motion` | in `theme.css` und `app.js` vorhanden | dto. | erfüllt (Vorhandensein geprüft, Verhalten nicht einzeln) |
| 11 | Schriften selbst gehostet, keine Konsolenfehler | Golos Text und Rethink Sans aus dem Theme-Ordner; shots.mjs auf den 6 Seiten 0 Fehler | dto. | erfüllt |
| 12 | Keine Gedankenstriche (Gate 19) | Start 4, Artikel 4, Termine 4, Kino 4 | Start 8, Artikel 5 (Probe überall 0) | **verletzt** → P1-5 |
| 13 | Keine „·“-Ketten (Floor 10) | Start 6, Artikel 3 | Start 9, Artikel 6 (Probe 0) | **verletzt** → P1-5 |
| 14 | Keine Dachzeilen | nur in Hausanzeigen („Veranstaltungskalender“, „Werben auf Tamil.de“ über dem Titel) | dto. | **verletzt** → P1-3 |
| 15 | Keine Versal-Labels | 0 Elemente mit `uppercase`/Sperrung | 0 | erfüllt |
| 16 | Keine gleich großen Kartenraster, keine Bildkacheln mit Verlauf, keine Seitenstreifen | keine; 0 Rundungen ≥ 6 px, 0 Schatten | dto. | erfüllt |
| 17 | Floor 12: Titel des Aufmachers bei 1280 × 800 sichtbar | – | Start: Titel bei 377 px (Probe 245); Artikel bei 294 px | erfüllt |
| 18 | sloplint 0 FAIL | FAIL 34 auf allen 6 Seiten (nur im Theme) | FAIL 58 (Wörter je Bildschirm bei 1440) auf allen Seiten, ebenso in der Probe (Start 173, Termine 524 Wörter), daher hier nicht als Rückschritt gezählt | **verletzt** → P1-8 |
| 19 | Werbung als „Anzeige“ gekennzeichnet und dem Inhalt untergeordnet | Banner bei y 77–153 vor allem Inhalt; Sticky-Leiste ohne „Anzeige“ | Leaderboard bei y 138–254 vor dem Aufmacher | **verletzt** → P1-1, P1-2 |

## Treue zur Probe (je Seite: was anders ist, ob es schlechter ist)

| Seite | Was im Theme anders ist | Urteil |
|---|---|---|
| Start 390 | Anzeige (76 px) zwischen Kopf und Tageszahl; Sticky-Leiste unten mit × über dem Aufmacherbild; leere Tafel statt zwei Festen; im Liste-Teil Textgrafiken als Daumenbilder (abgeschnitten). Gefüllt (b3): drei lange Einträge, kein Aufmacher und kein Foto im ersten Bildschirm | schlechter (Werbung, Tafel) |
| Start 1280 | Leiste „Termin einreichen/Werben“; Leaderboard 728 breit, das Label „Anzeige“ steht aber an der linken Containerkante; Aufmacher 132 px tiefer; zweite Hausanzeige (graue Fläche, ~250 hoch) bei y 999; „Verzeichnis“ fehlt im Menü | schlechter (Werbung), sonst treu |
| Artikel 390 | Anzeige oben; Metazeile „Redaktion Tamil.de, 1 Minute Lesezeit“ neu; Sticky-Leiste über dem Bild; Werbeplatz 03 als Hausanzeige mit WhatsApp-Icon über zentriertem Titel; „Quelle“ und „Schlagworte“ neu | Kopf und Satz treu; Werbung schlechter |
| Artikel 1280 | Leaderboard, Half Page (≈ 300 × 626, fast leer, rechts ~11 px über der Bildkante) neben dem Text und 300 × 250 im Text: drei Werbemittel in den ersten zwei Bildschirmen eines Beitrags mit sieben Absätzen | schlechter |
| Community | Aufbau gleich (Bild links, Tageszahl, Titel, Anreißer, Monatsgruppen); Anzeige oben; erster Titel bei 390 vierzeilig (Daten) | gleichwertig bis auf die Anzeige |
| Termine | Seitentitel „Events“ statt „Festkalender“; Leerzustand statt Liste; als Leitbild eine abgeschnittene Textgrafik („eat Your Heart 2026“) statt Foto; Archiv nur mit Terminen | schlechter (Bild, Benennung) |
| Kino | Leitbild ist eine abgeschnittene Textgrafik („ailer 2“ (Tamil) läuft in 9 inos …“) statt Festfoto mit Nachweis; „Nach Stadt“ jetzt mit Kino, Startdatum und „Tickets und Zeiten“ | Bild schlechter, Liste besser |
| Kontakt | Statt Formular „Nachricht“ zwei Knöpfe (E-Mail, WhatsApp), Kontaktblock, FAQ, Werben/Termin/Mitmachen; Beispielkontakte teils ohne Kennzeichnung | inhaltlich reicher, Kennzeichnung schlechter |

**Leerzustand:** ordentlich. Der Kasten bleibt mit „Stand“-Datum stehen, darin ein ruhiger Satz ohne Icon und ohne Illustration,
auf der Startseite mit den Wegen „Ganzer Festkalender“ und „Termin einreichen“. Schwäche: Am Handy beginnt die Startseite dann
mit Anzeige, Tageszahl und „nichts los“, die Signatur wirkt hohl (P2-5). Auf `/events/` fehlt im Kasten der Weg zum Einreichen;
er steht nur darüber.

## Paarvergleich

**Theme gegen Probe (Start 390 und 1280):** (1) Erstes Element nach dem Kopf ist im Theme die Anzeige, in der Probe die
Tageszahl. (2) In der Probe beginnt die Aufmacherzeile bei 390 auf y 529 und das Bild ist angeschnitten sichtbar. Im Theme mit
gefüllter Tafel liegt beides unter 844 px. (3) Abstände, Linienstärken, Schriftgrade und Farben sind identisch gemessen
(Golos Text und Rethink Sans, 48/74 px Tageszahl, 30/40 px Titel, 18 px Text).

**Theme gegen Spiegel (Handy):** (1) Spiegel zeigt im ersten Bildschirm ein großes Foto und genau eine dominante Schlagzeile.
Das Theme zeigt gefüllt kein Foto, das größte Element ist die Tageszahl, danach kommen drei Termine. (2) Bei Spiegel steht keine
Anzeige vor dem Aufmacher; im Theme stehen zwei Werbeelemente im ersten Bildschirm, zusammen rund 17 % der Höhe.
(3) Zugunsten des Themes: kein Rot als Fläche, ruhigere Linien, keine Rubrikreihe.

**Theme gegen Guardian (Handy):** (1) Der Guardian setzt eine eigene, kräftige Kopfmarke und eine 30-px-Serifenzeile mit Bild
direkt darunter. Das Theme hat denselben Rhythmus aus Titel und Bild erst nach Anzeige, Datum und Tafel. (2) Auch der Guardian
wirbt oben, aber klein und in der eigenen Kopfgestaltung, nicht als gerahmter Fremdkasten.

**Theme gegen Runde 2 (r2-community-magazin-390):** (1) Gleiche Hausanzeige „tamil.de | Live mit dir!“ an derselben Stelle
zwischen Kopf und Aufmacher. Genau das nennt `abgelehnt.md` als Lehre aus Runde 2 („keine Werbung über dem Aufmacher“).
(2) Zugunsten des Themes: kühles Weiß statt Creme, eckig statt Pillen und Rundungen, dünne Linien statt Kästen, kleinere Schrift.

**Theme gegen Runde 4 (r4-raster-390):** (1) Beide öffnen mit großem Datum oben links. In r4 steht „14.11.“ in Rot mit
Versal-Labels und Riesenwort, im Theme „14“ in Schwarz, ein Schnitt, Monat in Normalschrift, also ruhiger und wertiger.
(2) Kein Rot als Fläche, keine Versalien, keine verzerrte Schrift.

## Befunde

### P0
Keine. shots.mjs: 0 Fehler auf den sechs Seiten bei 390/820/1280. Die 404-Meldungen im Bericht stammen von einer zuerst falsch
geratenen Artikeladresse und nicht vom Theme.

### P1

**P1-1 Werbung über dem Aufmacher, im ersten Bildschirm jeder Seite** (alle Seiten; 390: Banner y 77–153; 1280:
Leaderboard y 138–254). Inhalt und Stelle entsprechen Runde 2. Der Aufmacher rutscht bei 1280 um 132 px nach unten (377 statt
245), die Tageszahl ist nicht mehr der Seitenöffner, und die Marken-Pflicht „dem Inhalt untergeordnet“ ist nicht erfüllt. Den
Platz zu behalten ist bewusst gewählt; schädlich ist die Lage. Bei 1280 steht das Label „Anzeige“ außerdem an der Containerkante,
das 728 breite Werbemittel aber mittig: Die beiden haben keine gemeinsame Kante.
*Behebung:* Werbeplatz 01 unter den ersten Abschnitt verlegen (Start: nach Aufmacher, Tafel und Kino; Artikel: nach Bild und
erstem Absatz; Rubrik: nach dem ersten Beitrag), am Handy nach dem Anreißer des Aufmachers. Ungebuchte Plätze nicht als
Hausanzeige füllen. Das Label an die linke Kante des Werbemittels setzen.

**P1-2 Mobile-Sticky-Leiste deckt den ersten Bildschirm ab** (390, alle Seiten; `.ad-mobile`, `theme.css:511`). Eine feste
Leiste von rund 60 px am unteren Rand, darin Eigenwerbung „Tamil.de auf WhatsApp / Abonnieren“, ohne sichtbares „Anzeige“. Der
Schließen-Knopf (44 × 44, `top: -22px`) steht zur Hälfte über der Leiste und liegt auf Aufmacherbild oder Text. Das wirkt wie ein
Cookie-Hinweis aus dem Baukasten; die Probe hat nichts dergleichen.
*Behebung:* Knopf in die Leiste holen (rechts, senkrecht mittig). Die Leiste erst nach dem Aufmacher einblenden oder nur bei
gebuchtem Werbemittel, dann mit „Anzeige“. Die Eigenwerbung für den Kanal gehört als schlichter Link in den Inhalt, nicht in den
Werbeplatz.

**P1-3 Hausanzeigen im Baukasten-Muster** (Start 390 zweiter Bildschirm und Start 1280 y 999: „Dein Fest im Kalender“;
Artikel 390/1280 im Text: „Kinostarts und Events direkt aufs Handy“; Artikel 1280 Half Page; Termine: „Werben auf Tamil.de“).
Icon (Blüte, WhatsApp-Zeichen) über der zentrierten Überschrift, eine Dachzeile darüber („Veranstaltungskalender“, „Werben auf
Tamil.de“), grauer Kasten, schwarzer Knopf. Die Half Page ist eine ~626 px hohe graue Fläche mit Inhalt nur in der Mitte, der
Billboard-Platz auf der Startseite eine ~250 px hohe Fläche mit einer Zeile. Das verstößt gegen die Verbotsliste („Icons über
Überschriften“) und gegen Floor 9 (Dachzeile) und ist genau das, was Luis als „Baukasten“ und „AI-Slop“ beanstandet hat.
*Behebung:* Hausanzeigen wie einen Anreißer der Seite setzen: linksbündig, ohne Icon und Dachzeile, Link statt Knopf, Höhe nach
Inhalt. Ungebuchte große Formate (Half Page, Billboard) gar nicht ausgeben.

**P1-4 Beschnittene Textgrafiken als Leitbild im ersten Bildschirm** (Kino 1280 rechte Spalte und Kino 390 unter „Im Programm“:
„ailer 2“ (Tamil) läuft in 9 inos …“; Termine 390/1280: „eat Your Heart 2026“, gefüllt „iler 2 · Kino Claudia Kloten“; in
Listen Start 390/1280 „Jailer 2 knackt …“ und „Komponist Deva …“, dazu ein Kinoheld-Logo als Beitragsbild). `object-fit: cover`
schneidet Grafiken mit Schrift an beiden Seiten ab. Die Probe zeigt an diesen Stellen Fotos mit vollem Nachweis. Ein
abgeschnittener Schriftzug ist im ersten Bildschirm der am billigsten wirkende Einzelpunkt der Seite und widerspricht „überall
Bilder“ im Sinne von Fotos.
*Behebung:* Bilder mit Nachweis „Grafik:“ (oder einem Merkmal „enthält Text“) nie beschneiden (`contain` auf ruhigem Grund) und
für Leitbild-Plätze nur Fotos nehmen: Fallback auf den nächsten Beitrag mit Foto oder auf ein Rubrik-Archivfoto mit Nachweis.

**P1-5 Gedankenstriche und „·“-Ketten in theme- und plugin-eigenen Texten** (Probe: 0). Fundstellen: `themes/tamil/inc/rubriken.php`
(Beschreibungen von Nachrichten, Entertainment, Events, Küche und Kino, z. B. „… Kinoabende – der Veranstaltungskalender …“
auf `/events/`), `plugins/tamil-site/includes/ads.php:88` („A.R. Rahman · Ilaiyaraaja · Anirudh · Santhosh Narayanan – die
Konzertreihe …“, im Leaderboard auf jeder Seite), die WhatsApp-Hausanzeige („… auf WhatsApp – keine Gruppe …“) und die
Werben-Hausanzeige („… Mobile Sticky – Mediadaten …“). Verstößt gegen Gate 19 und Floor 10 (Kriterien 12 und 13).
*Behebung:* die Texte mit Punkt, Doppelpunkt oder Komma neu schreiben und die Namensliste als Satz setzen. Gedankenstriche in
importierten Titeln: P2-7.

**P1-6 Beispielkontakte ohne Kennzeichnung** (Kontakt 390 und 1280, Block „Redaktion und Verlag“). Das Telefon trägt
„(Beispiel)“, WhatsApp „+49 170 123 4567“ und E-Mail „info@tamil.de“ nicht. Laut `CLAUDE.md` sind diese Werte Beispiele. Der
Knopf „E-Mail schreiben“ führt zu dieser Adresse. Ursache sind die Customizer-Daten im lokalen WordPress, nicht die Vorlage
(`customizer.php`: standardmäßig leer); sichtbar ist es trotzdem.
*Behebung:* die Werte vor einer Vorführung leeren oder jeden mit „(Beispiel)“ kennzeichnen; ohne echte E-Mail den Knopf
weglassen.

**P1-7 Tippflächen unter 44 px** (Kontakt 390: FAQ-Zeilen „Wie reiche ich …“, „Was kostet Werbung …“, „Kann ich Artikel …“ je
358 × 31 px; Community 390: Link „Wasser für Poovathan…“ 181 × 24 px; die Lage dieses Links wurde nicht im Bild geprüft).
*Behebung:* `summary` und Listenlinks mit `min-height: 44px` oder Innenabstand versehen.

**P1-8 sloplint FAIL 34 auf allen Seiten** (375 px). Das geschlossene Menü „Mehr“ (`.menue-paneel`, `position: absolute`, nur
79 px breit am rechten Rand) legt das 160 px breite Suchfeld 97 px über den Bildschirmrand hinaus an; verborgen bleibt es nur
durch `overflow-x: clip`. Leser sehen das nicht, geöffnet passt das Feld (x 16–258). Es ist aber ein Floor-Verstoß und die
einzige FAIL-Meldung, die die Probe nicht hat.
*Behebung:* das Panel im geschlossenen Zustand mit `display: none` ausblenden oder ihm `inset-inline: 0` beziehungsweise eine
feste Breite geben.

**P1-9 Festtafel mit echten Daten unruhig im ersten Bildschirm** (Start 390 und 1280, Termine; Aufnahmen b3-start und b6-termine).
In der Spalte „Wer“ steht „SOE · Tel. +41 78 880 90 02“, in „Wo“ „Veranstaltungsort wird vom Veranstalter bekannt gegeben“
(vierzeilig). „Kino Claudia“ kommt im selben Eintrag dreimal vor (Titel, Wer, Wo). Titel laufen in der ~110 px breiten
„Was“-Spalte bei 1280 bis zu sechs Zeilen. Am Handy schieben Anzeige und drei solche Einträge Aufmacher und Foto ganz aus dem
ersten Bildschirm. In der Probe: zwei Einträge mit je zwei bis drei Zeilen.
*Behebung:* In der Tafel nur Titel (höchstens zwei Zeilen, `line-clamp`) und Stadt zeigen. Keine Telefonnummern (die gehören auf
die Terminseite), „Wer“ weglassen, wenn es im Titel oder Ort steht, und den Platzhaltertext zum Ort durch „Ort folgt“ ersetzen.
Am Handy höchstens zwei Einträge, die Spalte „Was“ bei 1280 breiter.

### P2

- **P2-1 Bildnachweise ohne Urheber und Lizenz** (alle Seiten: „Foto: SwissTamilMedia · Events“, „Foto: Tamil.de“). Die Probe
  nennt Urheber, Plattform, Lizenz und einen Link „Quelle“. Das ist ein Datenmangel, für die Vorführung aber sichtbar.
  *Behebung:* Import beziehungsweise Lizenzdatensatz vervollständigen; Quellennamen ohne „·“ ausgeben.
- **P2-2 Gleiche Tageszahl in Serie** (Start 390/1280 „Zuletzt bei tamil.de“: fünfmal „18 So., Okt.“). Die Signatur verliert
  so ihren Sinn. *Behebung:* Einträge desselben Tages zusammenfassen und die Zahl nur beim ersten zeigen.
- **P2-3 Drei Namen für eine Seite:** Menü „Termine“, Seitentitel „Events“ (`/events/`), Links „Ganzer Festkalender“ und
  „Zum Festkalender“. *Behebung:* einen Namen wählen; die Probe nimmt „Festkalender“.
- **P2-4 Kanten der Werbeplätze:** Die Half Page im Artikel bei 1280 ragt rund 11 px über die rechte Bildkante (sloplint 72:
  −31 px bei 1440). Drei Werbemittel in den ersten zwei Bildschirmen eines kurzen Artikels. *Behebung:* in den Container
  einpassen, im Artikel höchstens ein Werbemittel vor dem Ende des Texts.
- **P2-5 Leerzustand der Startseite** (390): Anzeige, Tageszahl und „Gerade steht kein kommendes Fest …“ als ganzer Einstieg.
  *Behebung:* im Leerzustand die Tafel auf eine Zeile mit Link verkürzen und den Aufmacher hochziehen; auf `/events/`
  „Termin einreichen“ auch in den Kasten setzen.
- **P2-6 Anreißer in Listen bei 1280 mit ~74–76 Zeichen je Zeile** (Community, Kontakt ~72). *Behebung:* `max-width` um 62ch.
- **P2-7 Importierte Titel und Anreißer** mit Gedankenstrichen („Kanguva – …“, „Beat Your Heart 2026 – …“), abgebrochenen
  Sätzen („…“) und fehlenden Leerzeichen („Tamil)?Arabisch“, „zu.Meine“), dazu ein Kinoheld-Logo als Beitragsbild.
  *Behebung:* in der Redaktion beziehungsweise Migration bereinigen.
- **P2-8 „Verzeichnis“ fehlt in der Hauptnavigation** (1280; die Probe hat es). Das steht nicht auf der Liste der bewussten
  Abweichungen. *Behebung:* aufnehmen, sobald F2 steht, oder als bewusste Lücke vermerken.
- **P2-9 Kontakt ohne Formular „Nachricht“**, das `linien-auftrag.md` verlangt und die Probe hat. Ersatz sind ein E-Mail- und ein
  WhatsApp-Knopf in zwei Stilen nebeneinander (gefüllt und umrandet). Vermutlich gewollt, solange F1 aus ist. *Behebung:* als
  bewusste Abweichung festhalten.

## Was trägt

- Die Tageskalender-Signatur ist vollständig übertragen: Tageszahl, Tafel mit Stand-Datum, Tag-Spalte in jeder Liste,
  Monatsgruppen. Sie gehört nur tamil.de und ist ruhig gesetzt (Schwarz, ein Schnitt, keine Versalien).
- Handwerk: zwei Familien, 18 px Fließtext, 0 Kontrastfehler, 0 Rundungen, 0 Schatten, kein seitliches Scrollen. Das geöffnete
  Menü „Mehr“ (Suche, Rubriken, Dienste) ist sauber, die 404-Seite bietet „Zuletzt bei tamil.de“ an.
- Kino „Nach Stadt“ mit Kino, Startdatum und „Tickets und Zeiten“ hilft beim Finden mehr als die Probe.

## Bedienbarkeit (nur zur Information)

| Heuristik | 0–4 | Satz |
|---|---|---|
| 1 Sichtbarkeit des Status | 3 | „Stand“-Datum an Tafel und Kino, aktiver Menüpunkt unterstrichen. |
| 2 Sprache der Leser | 3 | Klar und duzend; „Events“ neben „Termine“ und „Festkalender“ stört. |
| 3 Kontrolle und Freiheit | 3 | Sticky-Leiste schließbar, Monatsarchiv auf- und zuklappbar. |
| 4 Konsistenz | 2 | Drei Namen für den Kalender, zwei Knopfstile auf der Kontaktseite. |
| 5 Fehlervermeidung | 3 | Pflichtfelder erklärt (Probe); im Theme keine Formulare. |
| 6 Wiedererkennen statt Erinnern | 3 | Tag-Spalte und Ort in jeder Liste. |
| 7 Flexibilität | 2 | Suche nur hinter „Mehr“, Stadtsprung im Kino vorhanden. |
| 8 Ästhetik und Reduktion | 2 | Werbedichte im ersten Bildschirm und im Artikel. |
| 9 Fehler erkennen | 3 | 404 mit Weiterlesen. |
| 10 Hilfe | 3 | FAQ auf der Kontaktseite. |
