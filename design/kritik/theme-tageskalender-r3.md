# Prüfung theme-tageskalender, Runde 3
Harte Kriterien: 13 von 16 erfüllt · P0: 0 · P1: 6 · P2: 8

Geprüft: lokales WordPress `http://127.0.0.1:8086/` (Theme `tamil`, Worktree `agent-a7dde36286d3ea89b`, Branch
`theme/tageskalender`), Datenstand 15.11.2026 mit abgelaufenen Terminen und Kinowochen (Leerzustände), dazu die
vorhandenen Aufnahmen mit gefüllten Tafeln (`scratchpad/wp-theme-shots/r3-gefuellt/`, nicht neu erzeugt). Eigene
Aufnahmen: 9 Seiten × 390/820/1280 (`scratchpad/kritik-theme-r3/`). sloplint `--render` auf Startseite, Kino-Rubrik und
Kino-Beitrag. Vergleich: NZZ und Spiegel Desktop, abgelehnte Runde 2 (1280). Begründung und frühere Kritiken nicht gelesen.

## Erster Eindruck (3 Sätze)

Wo ein echtes Foto da ist (Startseite, Community), wirkt die Seite ruhig und gemacht: Tagesziffer, Schlagzeile, Foto
mit Nachweis, gedruckte Tafel; das ist eigenständiger als jede frühere Runde. Seit Flyer und Titelkarten entfernt
wurden, sind aber Kino, Termine und alle Termin- und Kino-Beiträge im ersten Bildschirm reine Textseiten, und im
Leerzustand bestehen sie aus Titel, einem Satz, einem weißen Kasten mit „kennen wir keine“ und einer Eigenanzeige.
Ausgerechnet im Kino-Beitrag steht jetzt das schwarz-gelbe kinoheld-Logo bildschirmbreit als Aufmacherbild, und auf
jeder Seite laufen drei bis vier als „Anzeige“ gekennzeichnete Hausanzeigen samt fester Leiste am Handy.

## Harte Kriterien

Maßstab: `brief-v3.md`, `linien-auftrag.md` (Regeln), Pflichten aus `tamil-marke`, Hallmark-Floor, Luis' Urteile.

| # | Kriterium | Messwert Handy (390) | Messwert Desktop (1280) | Ergebnis |
|---|---|---|---|---|
| 1 | Kein seitliches Scrollen (390/820/1280) | 0 px auf 9 Seiten | 0 px auf 9 Seiten (820 ebenso) | erfüllt |
| 2 | Konsole, Anfragen, Bilder fehlerfrei | 0 Fehler | 0 Fehler (27 Aufnahmen) | erfüllt |
| 3 | Schriften selbst gehostet und geladen | Rethink Sans, Golos Text als woff2 im Theme; `schriften` 0 | dasselbe | erfüllt |
| 4 | Tippflächen ≥ 44 px | `tippflaechen` 0 (390, 820) | entfällt | erfüllt |
| 5 | Fließtext Handy ≥ 18 px | `--text-body` 1,125 rem = 18 px | 18 px | erfüllt |
| 6 | Kontrast AA | Grau #4B545B auf #F1F5F9 ≈ 7,2:1, Rot #B5282A ≈ 6,2:1 (berechnet) | dasselbe | erfüllt |
| 7 | Logo unverändert | `logo.png` | `logo.png` | erfüllt |
| 8 | Nur Deutsch, Tamil nur im Inhalt mit `lang` | `tamil_ohne_lang` 0 | 0 | erfüllt |
| 9 | Bildnachweis an jedem Bild (am Bild oder im Fuß) | Aufmacher „Foto: SwissTamilMedia, Events“; Daumen über Fuß gesammelt | dasselbe | erfüllt (Wahrheit des Nachweises siehe P1-1) |
| 10 | Keine Gedankenstriche und „·“ im Bedientext (Gate 19, R2-B) | Theme 0; Plugin-Ansichten 1 Rest (Platzhalter in Tabelle, P2-1) | dasselbe | erfüllt mit Rest |
| 11 | Keine Dachzeilen, keine Versal-Labels | Rubrik steht als Text unter der Tagesziffer, keine Versalien | dasselbe | erfüllt |
| 12 | Keine „·“-Metazeilen | „Redaktion Tamil.de, 2 Minuten Lesezeit“ | dasselbe | erfüllt |
| 13 | Keine gleich großen Kartenraster, Verlauf-Kacheln, Seitenstreifen | keine | keine | erfüllt |
| 14 | Werbung gekennzeichnet, untergeordnet, nicht über dem Aufmacher, keine Baukasten-Hausanzeigen (Luis) | 3–4 Eigenanzeigen je Seite, feste Leiste „Anzeige, Tamil.de auf WhatsApp, Abonnieren ×“ unten auf jeder Seite | 3–4 Eigenanzeigen je Seite, „Dein Fest im Kalender.“ als Seitenanzeige | **verletzt** (P1-3) |
| 15 | Überall Bilder (Luis) | erster Bildschirm ohne Bild: Kino, Termine, Event-Beitrag, Kino-Beitrag (gefüllt) | Kino, Termine, Event-Beitrag ohne Bild; Startseite (leer) 1 Bild | **verletzt** (P1-2) |
| 16 | Hallmark-Floor: 0 FAIL, keine zurückgewiesene Ausnahme | sloplint: 0 FAIL, 9 REFLEX, 7 WARN, **2 REJECTED** (58, 59) | dasselbe Werkzeuglauf (1440) | **verletzt** (P1-6) |

## Stand der sechs P1 aus Runde 2

| | Befund R2 | Behoben? | Messwert |
|---|---|---|---|
| A | Kopfbilder Kino/Termine ohne Flyer, Logos, Schriftgrafiken | **ja im Kopf, aber durch Weglassen** | Kino-Rubrik und Termine: 0 Bilder im Kopf bei 390 und 1280. Die Fotoprüfung `tamil_ist_foto()` (`inc/bausteine.php` Z. 50–60) prüft nur „Nachweis beginnt mit Foto:“ und „Alt ≠ Titel“; das kinoheld-Logo (r29.jpg, Nachweis „Foto: Kinoprogramm“, Alt „Kinosaal mit leuchtender Leinwand und Publikum“) besteht diese Prüfung. Folgen: P1-1, P1-2. |
| B | „·“/„–“ in `meta.php`, `verzeichnis-ansicht.php`, `werbung-ansichten.php` | **weitgehend** | `tamil-radar/includes/meta.php`, `tamil-site/includes/meta.php`, `verzeichnis-ansicht.php`: 0 Treffer. `werbung-ansichten.php` Z. 66: `: '–'` als „nächster freier Termin“, wenn nichts buchbar ist (P2-1). Lokal nicht gerendert (keine Seiten Werben/Verzeichnis im lokalen WP). Theme ersetzt „ · “ in Bildnachweisen durch Komma (`bausteine.php` Z. 137). |
| C | Kino-Tafel zeigt keine abgelaufene Woche als aktuell | **ja** | `tamil_kino_filme()` lässt Listen mit `bis < heute` weg; Startseite und Kino-Rubrik zeigen Leerzustand; Kino-Beitrag zeigt „Stand: Kinowoche 15. bis 21. Oktober, Spielzeit vorbei“ (gefüllt, 390). Neu entstanden ist ein Widerspruch zur Feste-Tafel (P1-4). |
| D | Keine nachtblauen Titelkarten mit Gold-„KINO“ | **ja für Titelkarten, Wiedergänger über ein Logo** | `tamil_ist_titelkarte()` blendet Nachweis „Grafik: Tamil.de“ aus; Startseite 5× `ohne-bild`. Dasselbe Bildmuster (dunkle Fläche, gelbe Schrift als Bild) steht jetzt als kinoheld-Logo im Kino-Beitrag, 1178 × 362 px bei 1280 (P1-1). |
| E | Spielortliste im Kino-Artikel ohne „–“, „·“, „Tickets & Infos“ | **im Code ja, im Bild nicht bestätigt** | „Tickets & Infos“: 0 Treffer in Theme und den drei Plugin-Ansichten. Die Liste selbst habe ich im Render nicht isoliert (Selektor nicht gefunden, Kacheln k2/k3 nicht angesehen). Das gleiche Muster lebt im Event-Beitrag als „Anmeldung & Infos“ weiter (P2-3). |
| F | Wortdichte je Bildschirm (Gate 58) | **nein, formal offen** | Die Ausnahme im CSS-Stempel weist sloplint zurück: „waiver on 58 REJECTED (Floor is never waivable)“. Leerer Datenstand: NOTE 58, 111 Wörter (Startseite, 1440, ab y = 350); gefüllt laut eigenem Stempel 173 Wörter, FAIL. Urteil siehe P1-6. |

## Paarvergleich

**Startseite 1280 (leer) gegen NZZ Desktop**
- NZZ: Aufmacherfoto etwa 60 % der Breite und 330 px hoch, zweite Geschichte ebenfalls mit Foto; tamil.de: ein Foto
  von 300 × 225 px (38 % der Breite) rechts, darunter und daneben zwei weiße Kästen mit je einem Leerzustandssatz. Bei
  NZZ trägt das Bild den ersten Bildschirm, bei tamil.de der Text.
- Satz und Linien halten mit: Tagesziffer, Schlagzeile 44 px, Vorspann, feste Linie über jeder Tafel, Nachweis klein
  unter dem Foto; das ist so geordnet wie bei NZZ, ohne deren Nachrichtenportal-Muster zu kopieren.
- Geschichten im ersten Bildschirm: NZZ 2 mit Anriss, tamil.de 1 (Leerzustand). „Viele Geschichten auf einen Blick“
  ist im Leerzustand nicht eingelöst.

**Startseite 1280 gegen Spiegel Desktop**
- Spiegel zeigt drei Schlagzeilen im Streifen plus Anzeige über dem Inhalt; tamil.de hat keine Anzeige über dem
  Aufmacher (richtig) und eine ruhigere Kopfzone (Leiste 44 px, Kopf 78 px, eine Haarlinie).
- Spiegel arbeitet mit Rot als Fläche im Kopf; tamil.de nur mit rotem Logo und roter „als Nächstes“-Zeile. Hier ist
  tamil.de wertiger.

**Startseite 1280 gegen Runde 2 (abgelehnt, „altbacken“)**
- R2 hat im ersten Bildschirm 5 Bilder (ein großes, vier Daumen), tamil.de im Leerzustand 1. Der neue Entwurf ist
  in genau dem Punkt schwächer, den Luis zuletzt verlangt hat („überall Bilder“).
- R2: Creme, farbige Rubrikpunkte, Pillen-Knopf „Tickets“ in der Hausanzeige oben. tamil.de: kühles Grau, keine Punkte,
  keine Pillen, Hausanzeige als Textzeile mit Linie; der Abstand zu R2 in Farbe und Ornament ist eindeutig.
- Beide haben die Eigenanzeige „Live mit dir!“; R2 über dem Aufmacher, tamil.de darunter. Das Motiv selbst hat
  Luis schon einmal gesehen und abgelehnt.

**Runde 4 (laut, Baukasten):** Bild nicht neu angesehen. Abgrenzung über Messwerte: keine rote Fläche, Schlagzeile
30 px Handy, 44 px Desktop, keine Versalien, keine Schräglage, keine verzerrten Schnitte. Größte Schrift ist die
Tagesziffer (bis 88 px, Tinte, nicht Rot); sie ist das Signaturelement und bleibt im Rahmen, solange sie das richtige
Datum zeigt (P1-5).

## Befunde

### P0
Keine. `bericht.json`: 27 Aufnahmen, 0 Fehler, 0 px Überlauf, 0 Konsolenfehler, 0 leere Bilder.

### P1

**P1-1 kinoheld-Logo als Aufmacherbild des Kino-Beitrags (Wiedergänger von A und D)**
Ort: `/jailer-2-rajinikanths-fortsetzung-laeuft-auch-in-der-neuen-woche-in-deutschen-kinos/`; 1280: Bild unter dem
Vorspann, 1178 × 362 px, schwarze Fläche mit gelber und weißer Schrift „kinoheld“; 390: ab y ≈ 585 im ersten
Bildschirm. Beitragsbild `r29.jpg` (1200 × 369, Seitenverhältnis 3,25:1), Nachweis „Foto: Kinoprogramm“, Alt
„Kinosaal mit leuchtender Leinwand und Publikum“. Der Nachweis ist falsch (kein Foto), der Alt beschreibt ein anderes
Bild (Barrierefreiheit), und das Bild liest sich als ungekennzeichnete Werbung eines Ticketanbieters. Nach der Logik
in `tamil_ist_foto()` taugt es sogar als Leitbild eines Seitenkopfs.
Behebung: Daten korrigieren (`bild_origin = karte` oder Nachweis „Grafik: kinoheld“, Alt „Logo kinoheld“) und durch
ein echtes Foto mit Nachweis ersetzen; im Theme Bilder mit Seitenverhältnis über 2,5:1 nie als Beitragsbild oder
Leitbild zeigen; `tamil_ist_foto()` nicht allein am Nachweistext festmachen.

**P1-2 Seiten ohne Bild wirken kahl (Luis: „wir brauchen überall Bilder“)**
Ort und Messwert, erster Bildschirm:
- Kino-Rubrik 390 und 1280: 0 Bilder. Inhalt: „Kino“, ein Satz, WhatsApp-Link, Kasten „Im Programm“ mit einem Satz,
  Eigenanzeige „Live mit dir!“. Darunter „Aus dem Kinojahr“ als Textliste, 57 % breit, rechts 500 px leer
  (sloplint REFLEX 77 „thin section“).
- Termine (`/events/`) 390 und 1280: 0 Bilder; „Das Jahr 2026“ 56 % breit, rechts leer.
- Event-Beitrag „Beat Your Heart 2026“ 390 und 1280: 0 Bilder; Kino-Beitrag „Jailer 2 (Tamil) läuft in 9 Kinos“
  (gefüllt, 390): 0 Bilder.
- Startseite leer, 1280 × 800: 1 Bild (NZZ 2, abgelehnte R2 5).
Die Community-Rubrik zeigt, wie es aussehen soll (Foto 668 × 445 px mit Nachweis neben der Schlagzeile). Das Entfernen
von Flyern war richtig, die Lücke wurde aber nicht mit Fotos gefüllt.
Behebung: Bildfolge ohne Leerstelle: eigenes Foto, sonst ein fest hinterlegtes Rubrikfoto mit Nachweis (Kino: Saal oder
Publikum, Termine: ein Fest aus dem Rückblick-Bestand mit Commons-Nachweis), nie Flyer oder Logo. Kino- und
Termine-Kopf mit diesem Foto. In „Aus dem Kinojahr“ und „Das Jahr 2026“ Daumenbilder je Zeile oder die rechte
Spalte bei 1280 mit dem Foto des nächsten Eintrags füllen.

**P1-3 Hausanzeigen auf jeder Seite (Luis hat Baukasten-Hausanzeigen abgelehnt)**
Ort: alle gemessenen Seiten. Startseite: „Live mit dir!“, „Dein Fest im Kalender.“, „Werben auf Tamil.de“,
„Tamil.de auf WhatsApp“, alle als „Anzeige“ gekennzeichnet. 390: feste Leiste unten (etwa 55 px) „Anzeige, Tamil.de auf
WhatsApp, Abonnieren ×“ über dem Inhalt jeder Seite. Kino und Termine: „Live mit dir!“ mit Link „Tickets“ steht im
ersten bis zweiten Bildschirm genau dort, wo das Foto fehlt. Eigenwerbung als „Anzeige“ zu kennzeichnen ist zudem
irreführend; ob die Konzertreihe mit „Tickets“ aktuell ist, ist nicht belegt.
Behebung: Werbeplätze ohne Buchung fallen leer zusammen (Kette in `tamil-site/includes/ads.php` Z. 3 endet heute bei
„Eigenanzeige von Tamil.de“; Standard auf leer setzen). WhatsApp-Kanal als normaler Link im Kopf oder Fuß, „Termin
melden“ steht schon unter der Feste-Tafel. Keine feste Leiste am Handy.

**P1-4 Kino-Tafel widerspricht der Feste-Tafel**
Ort: Startseite 390 und 1280, Kino-Rubrik, Termine (Aufnahmen gefüllt). Die Feste-Tafel führt „als Nächstes“ „Jailer 2
(Tamil) im Kino Claudia Kloten“ am 15. November; daneben bzw. darunter sagt „Im Kino“: „Für diese Woche kennen wir
keine tamilische Vorstellung“. Die Kino-Tafel liest nur Kinolisten, nicht Termine mit Kinovorstellung. Ein Leser sieht
auf einem Bildschirm zwei sich ausschließende Aussagen.
Behebung: Kommende Termine mit Kinovorstellung (Rubrik Kino oder Ort „Kino …“) in die Kino-Tafel aufnehmen, oder der
Leerzustand verweist darauf („Am 15. November: Jailer 2 im Kino Claudia Kloten“ mit Link zum Termin).

**P1-5 Tagesziffer zeigt bei Termin- und Kino-Beiträgen das Veröffentlichungsdatum**
Ort: Event-Beitrag „Beat Your Heart 2026“, 390 und 1280: Kopf „16 Oktober 2026 Freitag“ in bis 88 px, der Termin
ist am 31. Oktober (steht erst im Kasten darunter). Kino-Beiträge: „18 Oktober“ bzw. „16 Oktober“ bei Kinowoche ab
15./19. Oktober. Auf dieser Seite bedeutet die große Ziffer überall sonst „an diesem Tag findet es statt“ (Feste-Tafel,
Termine). Ein 65-jähriger Leser liest das größte Element der Seite als Datum des Fests.
Behebung: Bei Beiträgen mit Termin zeigt die Tagesziffer den Termin (bei Kino die Kinowoche); das
Veröffentlichungsdatum wandert klein in die Autorzeile.

**P1-6 Hallmark-Floor 58: Ausnahme ist ungültig**
Ort: `assets/css/theme.css` Z. 4 (Stempel „waive 58“). sloplint: „waiver on 58 REJECTED (Floor is never waivable)“;
Startseite 1440 im Leerzustand NOTE 58 mit 111 Wörtern ab y = 350, gefüllt laut eigenem Stempel FAIL mit 173 Wörtern.
Beurteilung: Inhaltlich ist die Dichte nicht der Mangel dieser Seite. Eine gefüllte Feste-Tafel mit drei Zeilen neben
einem Aufmacher ist für eine Nachrichtenseite normal (NZZ und Spiegel liegen im ersten Bildschirm darüber), und im
Leerzustand ist die Seite eher zu leer als zu voll. Formal ist das Floor aber nach brief-v3 nicht verhandelbar, und die
Ausnahme im Stempel wirkt nicht; „0 FAIL“ gilt nur, weil die Tafeln gerade leer sind.
Behebung: Floor erfüllen, ohne kahler zu werden: Vorspann des Aufmachers auf der Startseite bei 1280 auf etwa 20
Wörter kürzen, in der Feste-Tafel im ersten Bildschirm die Spalte „Wer“ weglassen und den Titel einzeilig kürzen; dann
gefüllt neu messen. Alternativ entscheidet die Hauptsitzung bewusst gegen Gate 58; dann gehört das in die
Entscheidungen, nicht in einen Stempel, den das Werkzeug verwirft.

### P2

- **P2-1** `tamil-site/includes/werbung-ansichten.php` Z. 66: `'–'` als „nächster freier Termin“, wenn nichts buchbar
  ist (Rest von R2-B). Behebung: „auf Anfrage“ oder Zelle leer mit Satz unter der Tabelle.
- **P2-2** Tagesblock im Kino-Beitrag 390 und 1280: „Kino , Deutschland“ mit sichtbarer Lücke vor dem Komma (HTML hat
  keine; vermutlich Innenabstand des Links für die Tippfläche). Im Event-Beitrag „Events, Kanton Solothurn“ ohne Lücke.
  Behebung: Tippfläche über `padding-block` oder Pseudo-Element vergrößern, nicht über `padding-inline`.
- **P2-3** Termin-Kasten im Event-Beitrag, 390 und 1280: Linktext „Anmeldung & Infos“ (dasselbe Muster wie R2-E
  „Tickets & Infos“); Titel wird gekürzt wiederholt („Beat Your Heart 2026 – Tanzwettbewerb (Solo,…“), Datum doppelt
  (Zeile „31 Sa., Okt.“ und „Wann: Sa, 31. Oktober 2026“), bei 390 „SOE“ unten abgeschnitten. Behebung: im Beitrag nur
  Wann, Wo, Wer, Preis als Liste; Link „Zur Anmeldung beim Veranstalter“.
- **P2-4** Ortsangaben in wechselnder Form: Startseite „Ort folgt“, Termine-Jahresliste „Veranstaltungsort wird vom
  Veranstalter bekannt gegeben“; mal nur Stadt („Kloten“), mal volle Adresse mit PLZ („Primarstufe Lysbüchel,
  Lysbüchelplatz 1, 4056 Basel“). Behebung: `tamil_ort_kurz()` auch in der Jahresliste verwenden.
- **P2-5** Termine 390 (gefüllt): Satz „Rot steht auf tamil.de für den nächsten Termin.“ erklärt dem Leser die
  Gestaltung. Behebung: streichen; „als Nächstes“ an der Zeile genügt.
- **P2-6** „Aus dem Kinojahr“ 390 und 1280: viermal hintereinander „18 So., Okt.“ in voller Ziffergröße (gleiches
  Importdatum). Wirkt wie ein Datenfehler. Behebung: Klasse `gleicher-tag` (gibt es in `bausteine.php` Z. 260) auch hier
  anwenden, Ziffer nur beim ersten Eintrag des Tages.
- **P2-7** Leerzustände als weiße Kästen auf grauem Grund („Im Kino“, „Im Programm“, „Ab heute“, „Die nächsten Feste“),
  jeder mit einem einzigen Satz; bei 1280 auf Termine 1178 px breit. Zusammen mit P1-2 lesen sie sich wie ungefüllte
  Formularfelder. Behebung: Leerzustand ohne Fläche als eine Zeile unter der festen Linie, oder durch den nächsten
  bekannten Eintrag mit Bild ersetzen.
- **P2-8** Ausnahme 59 im Stempel zurückgewiesen („reason shares no word with the page“); Abstände zwischen
  Abschnitten 48 und 57 px (REFLEX 59). Behebung: Begründung in Worten der Seite oder Abstand anheben.

### P3

- Termine: Aufklappzeichen „–“ hinter „Oktober 3 Termine“; prüfen, ob es U+2212 (Minus) ist, sonst ersetzen.
- R2-E im gerenderten Kino-Beitrag einmal von Hand ansehen (Kacheln k2/k3 der gefüllten Aufnahme), bevor es als
  erledigt gilt.

## Was trägt

1. Community-Rubrik 1280 und Startseite mit Foto: Tagesziffer, Schlagzeile 44 px, Foto mit Nachweis direkt darunter,
   feste Linie über jeder Tafel. Ruhig, eigenständig, kein Portalmuster.
2. Ehrlicher Kino-Stand: abgelaufene Wochen fallen aus den Tafeln, im Beitrag steht „Spielzeit vorbei“; Leerzustände
   in klarer Sprache mit Weg zur Einsendung.
3. Technik sauber: 0 Fehler in 27 Aufnahmen, Schriften lokal, kein Überlauf, keine Dachzeilen, keine „·“-Zeilen,
   kein Rot als Fläche.

## Bedienbarkeit (nur zur Information)

| Heuristik | 0–4 | Satz |
|---|---|---|
| 1 Systemstatus | 3 | „Stand: 15. November“ und „Spielzeit vorbei“ zeigen den Datenstand. |
| 2 Sprache der Nutzer | 3 | Klare Sätze; „Anmeldung & Infos“ und Erklärsatz zu Rot fallen ab. |
| 3 Kontrolle | 2 | Feste Anzeigenleiste am Handy muss erst weggeklickt werden. |
| 4 Konsistenz | 2 | Große Ziffer heißt mal Termin, mal Veröffentlichung; Ortsangaben wechseln. |
| 5 Fehlervermeidung | 2 | Kino- und Feste-Tafel widersprechen sich. |
| 6 Erkennen statt erinnern | 3 | Navigation mit vier Zielen und Unterstrich für die aktive Seite. |
| 7 Flexibilität | 3 | Festkalender, Kino nach Stadt, WhatsApp-Teilen überall. |
| 8 Ästhetik, Reduktion | 2 | Mit Foto stark, ohne Foto kahl; drei bis vier Hausanzeigen je Seite. |
| 9 Fehler erkennen | 3 | Leerzustände sagen, was fehlt, und wie man es meldet. |
| 10 Hilfe | 2 | Hinweis „Angaben ohne Gewähr“ vorhanden; Kontakt nur über Menü „Mehr“. |
