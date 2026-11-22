# Entscheidungslog

Neueste oben. Format: Datum · Entscheidung · wer · warum. Was hier steht, gilt, bis ein neuerer Eintrag es ändert.
Eine Entscheidung nicht stillschweigend umkehren: neuen Eintrag schreiben.

## 22.11.2026

- **Unterlagen nachgezogen:** Übergabe an Nick bereinigt, Spalte „Stand“ im Leistungsverzeichnis aktualisiert (Ja von
  Luis am 22.11.). Kein Leistungstext geändert. · Luis
- **Probe „Ausgabe“: Fehler aus der zweiten unabhängigen Kritik behoben (Theme 3.17.1).** · Korrekturen, umgesetzt
  vom Theme-Bauer im Auftrag der Hauptsitzung. **Keine Gestaltungsentscheidung**; was die Kritik an Gestaltung und
  Inhalt anmerkt (Kinozahlen, wählbare Städte, tamilische Schrift, Gewichtung, Symbolbilder), bleibt bei Luis.
  - **Stadtwahl leerte die Karten** (alle vier Proben, nur ohne „Bewegung reduzieren“): Die Stadtwahl suchte den
    umschaltbaren Kopf eines Fachs über `[data-art]`; dasselbe Attribut setzt `app.js` für das Einblenden an jede
    Karte. In Fächern ohne solchen Kopf traf die Suche die erste Karte und überschrieb sie mit leerem Text. Der Kopf
    hat jetzt ein eigenes Kennzeichen (`data-fach-kopf`). Die Browser-Tests der Stadtwahl laufen nun auch mit Bewegung.
  - **Vergangener Termin nie als Cover der Ausgabe:** Ist der Aufmacher ein Beitrag, dessen Termin vorbei ist, rückt
    der erste Beitrag mit eigenem Foto ohne vergangenen Termin aufs Cover, sonst der neueste ohne vergangenen Termin;
    der verdrängte Beitrag wird ein Beistück. Gilt nur für diese Probe; `tamil_start_auswahl()` und Cover First
    bleiben unverändert.
  - **Ersatzhinweis im Streifen:** am Handy als ganzer Satz über der Reihe („Für … kein Termin. In der Reihe stehen
    Termine aus anderen Städten.“), ab 600 px wie bisher in der Spalte. Spaltentitel stehen immer auf einer Höhe.
  - **Titelbild am Handy:** `sizes` nennt die wirkliche Bildbreite (Höhe mal Seitenverhältnis, bei 16:9 222vw statt
    100vw), der Browser lädt damit die größte passende Fassung. Mehr als das Original gibt es nicht her: Viele Bilder
    im Bestand sind nur 900 bis 1200 px breit und bleiben am Handy bei Faktor 2 weich (Datenbefund, nicht behoben).
  - **Titelstufen am Handy:** großes Beistück 20 px (vorher 24), kleine 17 px (vorher 19); der Covertitel bleibt.
  - **Bildkanten auf gemeinsamen Linien (Vorgabe von Luis, 22.11.: „Das muss alles auf einer Höhe sein“).** Gilt für
    die normale Startseite und die Ausgabe ab 600 px: Oberkante der Bilder in allen Spalten gleich, Unterkante des
    letzten Bilds jeder Spalte gleich; Text unter einem Bild steht unter dieser Linie. Geändert: Aufmacher neben
    „Weitere Meldungen“ (die Überschrift steht über der Bildlinie, die drei Karten teilen sich die Höhe des
    Aufmacherbilds; **das ändert die normale Startseite bewusst**), „Diese Woche“ (Kinokarte: Bild in der Bildzeile,
    Städte darunter; Kino und Termine in einer Reihe mit gleich breiten Spalten), Beistücke der Ausgabe. Nicht
    angeglichen: der Wow-Aufmacher (eigene Bahn, derzeit aus) und „Diese Woche“ mit mehreren Filmen untereinander.
    Messung: `wordpress/dev/kantenlinie.mjs`, Regel in `DESIGN.md`.
  - **Streifen mit weniger als drei Karten:** Die Karten werden breiter und füllen die Reihe (ab 600 px); eine
    einzelne Karte wird so breit wie bei zweien, nicht bildschirmfüllend.

- **Vierte Startseiten-Probe „Ausgabe“ (Theme 3.17.0, `/?probe=ausgabe`).** · Auftrag von Luis (Block 1) nach der
  Empfehlung der unabhängigen Kritik vom 22.11., gebaut vom Theme-Bauer im Auftrag der Hauptsitzung
  - **Das ist keine Entscheidung, Luis wählt.** Die normale Startseite und die drei Proben bleiben unverändert; die
    Probe gibt es nur mit dem Schalter „Startseiten-Proben“, mit `noindex`, nirgends verlinkt.
  - **Cover:** die Titelgeschichte über die volle Breite. Titel im Bild 32 px am Handy bis 60 px am Desktop, nach
    Länge in Stufen kleiner, nie gekürzt. Die Bildhöhe richtet sich nach dem Bildschirm, damit Bild und ganzer Titel
    im ersten Bildschirm stehen (Handy mindestens 407 px, Desktop 480 bis 640 px).
  - **„Tamil in meiner Stadt“ als Streifen auf Titan** direkt unter dem Cover: Stadtwahl und eine Reihe mit Filmen ab
    heute und Terminen ab heute, wischbar mit Balken und Pfeilen. Nur Kommendes, keine Geschichten; wählbar sind nur
    Städte mit Vorstellung oder Termin. Der Streifen **ersetzt in dieser Probe „Diese Woche“**; damit gibt es dort
    nur noch eine Kinozählung (Kinos mit Vorstellung ab heute, bei Abweichung „ab heute noch N von M Kinos“).
  - **Beistücke mit Gewicht:** ein großes Stück mit zwei kleineren daneben, „Weitere Meldungen“ gespiegelt mit einer
    großen Karte und drei flachen. Jeder Beitrag bleibt eine Bildkarte mit Titel im Bild und Punktbogen.
  - **Tamilische Schrift, nur aus dem Bestand:** die tamilischen Rubriknamen aus `inc/rubriken.php` stehen in den
    Rubrikkacheln über dem deutschen Namen und einmal am Kontextfeld der Titelgeschichte (`lang="ta"`, Catamaran).
    Das weicht in dieser Probe von „Nur Deutsch“ (Luis, 09.11.) ab, weil der Auftrag es so vorgibt; es gilt nur
    hier und ist keine neue Regel. Übersetzt oder erfunden wird nichts; tamilische Titel gibt es im Bestand nicht.
  - Aufbau: `design/richtungen/klar2/proben-start/ausgabe.md`. Code: `inc/proben.php`,
    `template-parts/home/probe-ausgabe.php`, `stadt-streifen.php`, `assets/js/streifen.js`, `inc/anreisser.php`
    (`tamil_kacheln()` mit Schalter für den tamilischen Namen), Tests in `tests/wp/test_startseiten_proben.py`.

- **Startseiten-Proben: Wahrheits- und Datenfehler behoben (Theme 3.16.1).** · Korrekturen aus der unabhängigen
  Kritik vom 22.11., umgesetzt vom Theme-Bauer im Auftrag der Hauptsitzung
  - **Das ist keine Gestaltungsentscheidung.** Die drei Proben bleiben, wie sie sind; welche Richtung gilt, entscheidet
    Luis. Die Dopplung „Stadtbereich zeigt dieselben Karten wie Diese Woche“ ist bewusst nicht angefasst.
  - **Eine erklärte Kinozahl:** „Diese Woche“ nennt alle Kinos der Kinoliste, „Tamil in meiner Stadt“ nur die mit
    Vorstellung ab heute. Weichen die Zahlen ab, steht im Stadtbereich „ab heute noch N von M Kinos“.
  - **Vergangene Termine:** Das Kontextfeld der Titelgeschichte schreibt einen Termin vor heute als „war am …“.
  - **„Zuletzt erschienen“ (News First):** Fehlt die Titelgeschichte in der Liste, obwohl sie nach ihrem Datum
    hineingehört, sagt eine Zeile unter der Überschrift das und führt zu ihr. Die Auswahl bleibt unverändert.
  - **Dünne Stadt:** Hat die gewählte Stadt in einem Fach nichts, zeigt das Fach den Bestand aus allen Städten mit
    einer Zeile darüber („In Bern gerade kein Film. Im Kino anderswo:“). Leersätze stehen nur noch, wenn es nirgends
    etwas gibt; sie sind kurz und nicht mehr fett.
  - **Stadtauswahl:** Gezählt werden die 200 neuesten Beiträge mit Ort (vorher 24). Wählbar ist jede Stadt mit Kino
    ab heute, kommendem Termin oder zwei Beiträgen. Unter „Alle Städte“ stehen nur Geschichten der letzten 60 Tage,
    neueste zuerst (vorher Rubrik Community zuerst, ohne Altersgrenze); das Fach heißt dort „Aus den Städten“ und
    entfällt ohne junge Geschichte.
  - Code: `inc/proben.php`, `inc/anreisser.php` (`zahl_text`), `template-parts/home/stadt.php`, `probe-news.php`,
    `assets/js/stadt-start.js`; Tests in `tests/wp/test_startseiten_proben.py`.

## 21.11.2026

- **Drei Startseiten-Proben zum Vergleichen (Theme 3.16.0; Masterplan von Luis vom 21.11., Teil B, Ticket TML-W06).**
  · Luis, umgesetzt vom Theme-Bauer im Auftrag der Hauptsitzung
  - **Das ist keine Entscheidung über die Startseite.** Gebaut sind drei Proben für den ersten Bildschirm, damit Luis
    vergleichen und wählen kann: „Cover First“ (`/?probe=cover`), „News First“ (`/?probe=news`), „Community First“
    (`/?probe=community`). Bauvorgabe und Begründung: `design/richtungen/klar2/proben-start/`.
  - **Nur mit Schalter:** Customizer „Tamil.de → Startseite → Startseiten-Proben“ (`tamil_startseiten_proben`,
    Standard aus). Ist er aus oder der Wert unbekannt, steht exakt die normale Startseite da (geprüft: gleiche
    Ausgabe wie vor dem Einbau). Probenseiten tragen `noindex`, werden nicht zwischengespeichert, sind nirgends
    verlinkt und zeigen oben einen kleinen Umschalter zwischen den Proben und der normalen Startseite.
  - **Gleiche Beiträge, kein eigener Zwischenspeicher:** Die Proben ordnen die acht Beiträge neu, die
    `tamil_start_auswahl()` für den ersten Abschnitt schon reserviert (Aufmacher, Nebenstücke, Meldungen). Alles
    darunter bleibt die bestehende Seite; die Werbeplätze nach F3 stehen an ihrem Ort (Leaderboard nach den
    Rubrikkacheln, Billboard nach „Küche“, Fuß, Handy-Leiste).
  - **Neu in allen Proben: „Tamil in meiner Stadt“** (Kino, Termine, Geschichten mit Ort, Stadtwahl). Die Wahl bleibt
    nur im `localStorage` des Browsers; kein Cookie, keine Anfrage an den Server, keine Standortabfrage. Ohne Skript
    steht der Zustand „Alle Städte“. Städte kommen aus `kino_fakten`, den Termin-Feldern und dem Freitext „Ort der
    Meldung“; ein eigenes Stadt-Feld gibt es nicht.
  - **Nichts erfunden:** kein Etikett „Warum das wichtig ist“ (das Feld gibt es nicht), „Heute wichtig“ nur mit einem
    Beitrag von heute, sonst „Zuletzt erschienen“; Uhrzeit nur bei Beiträgen von heute oder gestern.
  - **Offen bei Luis** (Fragen 1 bis 5 der Bauvorgabe): eigenes Feld für den Kontextsatz, Dopplung mit „Diese
    Woche“, tägliche Beiträge, Stadt und Land als eigene Felder, Abweichungen vom Brief §10 bei Cover First.
  - Code: `inc/proben.php`, `template-parts/home/probe-*.php`, `template-parts/home/stadt.php`,
    `assets/js/stadt-start.js`, `assets/js/stadt.js`, Abschnitt „Startseiten-Proben“ in `assets/css/theme.css`;
    Test `tests/wp/test_startseiten_proben.py`.
- **Grundlage reparieren (Theme 3.15.0; Masterplan von Luis vom 21.11., Teil A, Tickets TML-W02, TML-W03, TML-W05).**
  · Luis, umgesetzt vom Theme-Bauer im Auftrag der Hauptsitzung
  - **Cover mit Ablauf (TML-W02):** Ein abgelaufenes Cover bleibt nie stehen. Ein im Customizer gesetzter Aufmacher
    gilt bis zum Ende des Tages „Aufmacher gilt bis“ (neues Datumsfeld, Zeitzone der Website). Ohne Datum gilt er
    höchstens sieben Tage ab dem Eintragen der Beitrags-ID (Zeitpunkt in der Option `tamil_aufmacher_seit`,
    geschrieben bei jeder Änderung der ID). **Altbestand** ohne Zeitpunkt (Cover vor 3.15.0 gesetzt): Es zählt die
    Veröffentlichung des Beitrags plus sieben Tage, nicht das Änderungsdatum, damit eine Tippfehlerkorrektur kein
    altes Cover verlängert. Folge beim Ausrollen: Ein heute gesetzter Aufmacher, dessen Beitrag älter als sieben Tage
    ist, fällt sofort weg; wer ihn halten will, trägt das Datum ein. Ein markierter Beitrag („oben halten“) ist nur
    sieben Tage nach Veröffentlichung Cover. Danach greift die bisherige Kette (neuestes Foto). Der Customizer sagt
    am Feld, bis wann das Cover gilt oder seit wann es abgelaufen ist. Der Zwischenspeicher der Startseite trägt
    das Tagesdatum im Schlüssel und zusätzlich die Frist des Covers. Code: `inc/queries.php`
    (`tamil_cover_manuell()`), `inc/customizer.php`; Test `tests/wp/test_cover_ablauf.py`.
  - **„Diese Woche“ nur mit kommenden Vorstellungen (TML-W03):** Die Bildkacheln zeigen nur noch Beiträge, deren
    Film laut Kinoliste (`kino_fakten`, `tamil_kino_filme()`) mindestens einen Spieltag ab heute hat: Beiträge der
    Rubrik Kino mit genau demselben Filmschlüssel (Film aus der Kinoliste oder Titel in Anführungszeichen), dann die
    Kinolisten selbst. Die Regel „Kino-Beiträge der letzten 30 Tage“ (17.11.) entfällt; ein neuer Beitrag über einen
    Film ohne kommende Vorstellung steht dort nicht mehr. Gibt es keine, bleiben die Plätze leer und das Raster
    rückt zusammen. Die Datenquelle (Plugin, Radar) ist unverändert. Test `tests/wp/test_woche_spieltage.py`.
  - **Ein Radius (TML-W05):** `design/tokens.css` führt jetzt wie das Theme `--radius: 10px` und
    `--radius-klein: 6px` (dort stand noch 0 aus der Zeit vor 3.9.0). `tests/test_tokens_radius.py` vergleicht beide
    Dateien.

- **Rubriken im Band mit Tamil-Dots-Bewegung (Theme 3.14.0).** Luis am 21.11.: bei den Rubriken im Kopf „mehr
  Animation“; beim Darübergehen „gehen da Tamil Dots rein“ und die Fläche wird „von Rot auf Weiß“. Umgesetzt in
  `assets/css/theme.css` (Abschnitt Band): Punkte wachsen im Raster bis zur weißen Fläche, Schrift auf Titan; auch
  im Tastaturfokus, ohne Bewegung bei „Bewegung reduzieren“. · Luis
- **Wow-Aufmacher abgeschaltet (Theme 3.13.1).** Luis am 21.11.: Die Tamil Dots liegen im Aufmacher „über die ganze
  Seite“ und sehen „ganz rot“ aus; sie sollen „klein, minimiert rechts unten in der Ecke nur, wie bei den anderen
  Beiträgen“ sitzen, weil die Decke „den ganzen Aufmacher kaputt“ macht. Der Schalter im Customizer steht jetzt
  standardmäßig auf aus; der Aufmacher ist die normale Bildkarte mit Punktbogen unten rechts. Der Code bleibt
  liegen, bis der neue Aufmacher mit Luis entschieden ist. · Luis

- **KI-Symbolbilder als Ersatzbilder im Rubrik-Pool erlaubt (Theme 3.13.0).** Auftrag von Luis am 21.11.: „suche
  außerdem täglich beiträge und wenn keine bilder vorhanden oder sonst was gebe mir bitte ein generiertes bild das
  aussieht wie echt hyperrealistisch nicht nach ki“ und „gehe mit higgsfield und skills noch mal über die bestehende
  seite komplett rüber“. Das kehrt den Eintrag vom 11.11. („keine KI-Bilder“) für genau diesen Fall um: nur
  Symbolbilder ohne erkennbare Personen, Marken, Schrift oder nachgestellte Ereignisse, immer mit Schild „Symbolbild“
  und dem Nachweis genau „Symbolbild: KI-generiert · Tamil.de“ (Spezifikation 4.8; nachgezogen in
  `docs/spezifikation/bilder-und-lizenzen.md` 4.1). Alles andere aus dem 11.11. bleibt. · Luis, umgesetzt vom
  Theme-Bauer im Auftrag der Hauptsitzung
  - **Heikle Themen ohne KI-Bild (Spezifikation 4.2 bleibt):** Das Theme kennt die Einstufung nicht. Darum kommen die
    vier Nachrichten-Bilder `news-4` bis `news-7` nicht in den Pool (Dateien nur unter `design/inhalte/bilder-lauf/`),
    und für Beiträge der Rubrik Nachrichten wählt die Bildkette nie ein Poolbild mit `'ki' => true`, auch nicht über
    den allgemeinen Ausweich-Pool und auch nicht, wenn die Hauptrubrik eine andere ist (Test
    `tests/wp/test_bildpool_ki.py`).
  - **Vorbehalte:** `community-4` (Ganesha-Relief am Tempeleingang) bleibt draußen; `events-10` und `events-12` sind
    drin. Im Pool stehen 27 KI-Bilder (Entertainment 4, Events 4, Community 3, Küche 4, Kino 4, Sport 4, Kultur 4),
    je Rubrik abwechselnd mit den Commons-Fotos. Quelle, Prompt und Modell je Bild: `design/inhalte/bilder-lauf/pool/`;
    erzeugt wird die Liste mit `design/inhalte/bildpool/holen.py --text`. Rückweg: in `holen.py` die Einträge über
    `KI_AUS` ausschließen oder `KI_JSON` leeren und neu schreiben.

- **Theme 3.12.0 / Plugin tamil-site 1.2.0 (Kritik-Bogen 3.11.0, Stufe 2):** · Hauptsitzung im Auftrag von Luis,
  umgesetzt vom Theme-Bauer
  - **Einzelne letzte Karte in normaler Breite (N-04):** Bleibt in einem Raster eine Karte allein in der letzten Zeile,
    steht sie in normaler Spaltenbreite linksbündig, nie über die ganze Zeile (Rubrik, Suche, Events-Archiv, Production
    einheitlich). Warum: aufgezogen wurde ihr Bild weit über die Dateibreite vergrößert und weich (Production 1280:
    1200 statt 384 px). Rückweg: die
    entfernten Regeln QA-04 und K-19 in `theme.css` (siehe Kommentar dort).
  - **Bühnen einheitlich (N-03, N-08):** Küche und Rubrik-Bühnen nutzen dieselben Regeln (`.kueche__raster`), Titel der
    kleinen Karten ganz. Rückweg: Commit 52bb761.
  - **„Kommende Termine“ entfällt, wenn alles unter „Ab heute“ steht (N-05):** die Filter wandern dann nach „Ab heute“.
  - **N-06 nur als Vorschlag an Luis, nicht umgesetzt:** Die Kritik fand auf kurzen Artikeln (eine Minute Lesezeit) vier
    Werbeflächen und schlug vor, die Anzeige im Text erst ab fünf Absätzen und bei kurzen Artikeln höchstens zwei
    Flächen zu zeigen. Das ändert verkaufbare Plätze der von Luis bestätigten Festlegung F3
    (`docs/vertrag/festlegung-werbung.md`: „Im Artikel: nach dem zweiten Absatz“, „Fuß: über dem Fuß jeder Seite“);
    die freie Hand der Nacht deckt Gestaltung, keine Änderung einer Festlegung. Gebaut und wieder zurückgenommen
    (Reverts f67445d, 76afb9a). Stand jetzt wörtlich nach F3: „Im Artikel“ nach dem zweiten Absatz ohne Mindestlänge
    (die Mindestlänge „vier Absätze“ der ersten Theme-Fassung entfällt), Fuß auf jeder Seite; Test
    `tests/wp/test_artikel_werbung.py` prüft das. · Hauptsitzung
  - **Hausanzeigen-Regeln aus 3.9.0 gegen F3 geprüft:** „keine zwei Eigenanzeigen direkt hintereinander“ und „keine
    Eigenanzeige für die eigene Seite“ betreffen nur Eigenanzeigen (bleiben). „Keine Anzeigen auf Impressum und
    Datenschutz“ unterdrückte auch gebuchte Plätze und gilt jetzt nur noch für Eigenanzeigen; gebuchte Plätze stehen
    dort wie auf jeder Seite (F3).
  - **Teilen als Knopfzeile, Infokasten als Terminkasten (N-10, N-11).**
  - **Leichterer Verlauf (N-12):** 66 % Schwarz am Beginn der Schrift (7,2 : 1 auf Weiß, schlechtester Titel 7,6 : 1).
  - **Kuppel ohne Bodenschatten (N-13),** Alt-Text beim Laden unsichtbar (N-16), „Im Kino“ nicht zwischen zwei
    Kinokarten (N-17), Skizze je Werbeplatz auf „Werben“ (N-07).
  - **Ein Termin als Band (K-13):** Bild in Dateigröße, Text mittig daneben (Entscheidung statt schmaler Karte, weil
    die schmale Karte zwei Drittel der Zeile leer ließe).
  - **Nicht umgesetzt:** N-09 (Anschnitt der nächsten Karte am Handy) widerspricht dem Scrollweg des Aufmachers und
    gehört mit N-15 (tote Strecke) und K-07 (Splitter) in eine Überarbeitung von `wow.js` mit neuer Bildratenmessung;
    N-14 (eine linke Kante für Textseiten) braucht eine Entscheidung über die Spaltenbreiten (Artikel 560 px, Seiten
    720 px, Kontakt volle Breite).
- **Theme 3.11.1 (P0 aus dem Live-Stand 3.11.0):** „Weitere Meldungen“ haftet nur noch innerhalb der Aufmacher-Zeile
  (N-01, vorher in 8 von 8 gemessenen Fenstern über der nächsten Zeile, danach 0; Messung `wordpress/dev/ueberdeckung.mjs`);
  Titel im Aufmacher und H1 werden nie gekürzt oder getrennt, lange Titel bekommen kleinere Stufen (N-02). · Hauptsitzung
  im Auftrag von Luis, umgesetzt vom Theme-Bauer

- **Startseite im Wechsel: Reihe und Bühne (Theme 3.11.0, K-06):** Die Rubrikblöcke unter dem Aufmacher wechseln
  zwischen der Reihe aus vier Karten und der Bühne (die erste Karte groß, die übrigen klein gestapelt daneben, gebaut
  wie die Küche). Warum: Die unabhängige Kritik fand fünf gleich gebaute Reihen nacheinander (das „gleichförmige
  Kartenraster“ der Verbotsliste); Luis will „was komplett Spezielles“. Kartenart, Titel im Bild und Punktbogen bleiben,
  die Seite bekommt weitere Höhepunkte. Rückweg: in `front-page.php` beim Rubrik-Block `buehne` auf `false` setzen.

  · Hauptsitzung im Auftrag von Luis, umgesetzt vom Theme-Bauer
- **Wow-Aufmacher überarbeitet (Theme 3.11.0, K-01 bis K-05):** Kuppel größer und am Anfang halb geöffnet (Foto sofort
  erkennbar), Titel 26/38 px und höchstens 84 Zeichen sichtbar, Weg halbiert, Punkte und Titelfeld zugleich, am Desktop
  steht „Weitere Meldungen“ mit, am Tablet hängt der Weg an der Rahmenhöhe. Warum: Kritik-Note 6/10, Anfang fast nur
  Titan, fünf Titelzeilen, Leere neben und unter dem Aufmacher. Rückweg: Werte in `assets/js/wow.js` (T0, Größe) und
  `assets/css/theme.css` (Abschnitt Wow-Aufmacher).

  · Hauptsitzung im Auftrag von Luis, umgesetzt vom Theme-Bauer

- **Wow-Aufmacher „Punkt für Punkt zum Bild“ (Theme 3.10.0):** Der Aufmacher der Startseite bekommt, wenn er ein
  eigenes Foto ab 960 px Breite hat, eine Decke in Titan mit den 238 Punkten des Masters als Fenster aufs Foto; beim
  Scrollen wachsen die Punkte, bis das volle Foto steht (Vorlage `design/richtungen/klar2/wow/punkt-zum-bild/`,
  Variante A). Warum: Luis wollte ausdrücklich einen Wow-Effekt mit den Tamil Dots; das Signet tut hier etwas, statt
  nur Dekor zu sein, und es kann nur tamil.de zeigen. Begrenzt auf eine Stelle, nur mit echtem Foto, der erste
  Bildschirm bewegt sich nicht von selbst, Titel von Anfang an sichtbar. Gemessen: Lighthouse mobil Start (5 Läufe,
  Median) 84 → 83, LCP 4,22 → 4,29 s, CLS 0. **Abschalten:** Customizer → Tamil.de → Startseite → „Wow-Aufmacher“
  oder Filter `add_filter( 'tamil_wow_aufmacher', '__return_false' );`. Ohne Skript und mit „Bewegung reduzieren“
  steht sofort das fertige Foto.

  · Hauptsitzung im Auftrag von Luis (freie Hand bis 8 Uhr), umgesetzt vom Theme-Bauer
- **Logo-Fläche im Band mit 3 px Impact unten** wie unter der aktiven Rubrik. Umkehren: `box-shadow` an
  `.band__logo` entfernen. · Theme-Bauer im Auftrag von Luis

Luis, 00:45 Uhr: Die Nacht wird ohne Rückfragen gearbeitet („entscheide selber … komplett automatisch“). Die folgenden
Gestaltungsentscheidungen zu seinem Auftrag „tamil logo beim runterscrollen in der leitse theme ausarbeiten spezial
mehr rein bilder nicht alle eckig also die karten auf einer höhe alles“ hat der Theme-Bauer getroffen; jede lässt sich
einzeln umkehren.

- **Logo im stehenden Band (Theme 3.9.0):** Sobald der Kopf mit dem großen Logo aus dem Bild ist, zeigt das Rubrikband
  links das ganze Logo klein (30 px hoch, ab 1024 px 34 px) auf einer weißen Fläche bündig am linken Rand in voller
  Bandhöhe. Warum: Das Logo ist dunkelrot und auf Titan unsichtbar; eine weiße Fassung gibt es nicht, Umfärben oder
  Zuschneiden wäre ein Eingriff ins Logo. Die weiße Fläche wiederholt Rot auf Weiß wie im Kopf. Die Rubriken rücken
  per transform zur Seite (kein Springen), Einblenden 0,2 s nur ohne reduzierte Bewegung. Umkehren: `.band__logo`
  in `template-parts/header/kopf.php` entfernen.

  · Theme-Bauer im Auftrag von Luis
- **Abgerundete Ecken (Theme 3.9.0):** Ein Radius für Karten und Bilder, `--radius` 10 px, für kleine Kacheln und die
  Bilder der Kinotabelle `--radius-klein` 6 px. Warum: deutlich weicher, aber noch ruhig und redaktionell; größere
  Radien wirken bei Titel im Bild wie App-Kacheln. Punktbogen und Schild „Symbolbild“ werden von der Rundung
  angeschnitten, nichts steht über. Gerade bleiben Bänder, Kopf, Fuß und Bilder, die am Handy von Rand zu Rand laufen
  (Aufmacher, Artikelbild unter 600 px), weil eine Rundung am Bildschirmrand wie ein Fehler aussieht. Umkehren:
  `--radius` und `--radius-klein` in `assets/css/theme.css` auf 0.

  · Theme-Bauer im Auftrag von Luis
- **Karten auf einer Höhe (Theme 3.9.0):** Der Vorspann unter Karten hält immer drei Zeilen Platz, die Kinokarte in
  „Diese Woche“ ist neben den Terminen so hoch wie diese. Warum: Unterkanten einer Reihe fluchten, ohne Text zu kürzen
  oder Karten zu beschneiden. Messung `wordpress/dev/kartenhoehe.mjs`. Umkehren: die Regel mit `min-height:
  calc(3 * 1.45em)` entfernen.

  · Theme-Bauer im Auftrag von Luis

- **Punktbogen bleibt weiß auf dunklen, rot auf hellen Bildecken:** Luis fragte zuerst „warum sind die tamil dots nicht
  in rot ??“ und wollte den Bogen überall in Titan/Impact. Nach Rückfrage bestätigte er die bestehende Regel aus
  3.7.x (Wahl über den Ton der Bildecke, `tamil_signatur_ecke_ton`). Wortlaut: „Die weißen Punkte in den Bildecken
  bleiben, weil diese Ecken meist dunkel sind; rot wäre dort kaum zu sehen, außer auf hellen Bildern. genau so
  umsetzen“. Keine rote Fassung mit weißer Eckfläche.

  · Luis

## 20.11.2026

- **Jede Meldung als Karte (Theme 3.7.0):** Was auf der Startseite gilt, gilt jetzt überall, wo Beiträge angerissen
  werden: jeder Beitrags-Anreißer ist eine Bildkarte mit Dachzeile „Rubrik | Datum“ und Titel im Foto, Punktbogen unten
  rechts, Schild „Symbolbild“ oben rechts – Rubrikseiten („Neu in der Rubrik“, „Weitere Beiträge“), Suche, Archive,
  404, Production, „Weiterlesen“, Termine („Ab heute“, „Kommende Termine“, „Das Jahr“) und Kino („Im Programm“, „Aus
  dem Kinojahr“). Es bleiben: Top-News im Kopf, Navigation, Fußlisten, Rubrikkacheln, Verzeichnis, Anzeigen,
  Formulare, reine Textseiten und die Kinotabelle (Spielorte; ihre Zeilen verlinken auf Kinos, nicht auf Beiträge).
  Wortlaut Luis: „auf jeder meldung tamil dots und schrift auf der karte tamil dots auchh auf der akrte“.

  · Luis (`docs/abnahme/2026-11-20-logo-startseite.md`, Nachtrag 3.7.0)
- **Neues Logo, genau so übernommen:** Das Logo aus `design/inhalte/logo-2026-11.webp` („tamil“ in Rot, „.de“ in
  Dunkelgrau, darunter „portal • lifestyle • entertainment“ und „& KOMMUNITYPLATTFORM DER COMMUNITY“) ersetzt das
  bisherige Logo in Kopf, Fuß, Teilenbild, Theme-Vorschau und Social-Vorlagen – in genau dieser Form und
  Schreibweise, ohne Neuzeichnen oder Vektor-Nachbau, nur vom weißen Grund freigestellt. Das hebt die Regel
  „Logo bleibt unverändert“ aus dem Branding-Handoff v1.1 für dieses Logo auf; alle anderen Logo-Regeln gelten weiter
  (Signet nie am, im oder hinter dem Logo). Favicon und App-Icon „t.“ bleiben, bis Luis anders entscheidet.

  · Luis (`docs/abnahme/2026-11-20-logo-startseite.md`)
- **Startseite „Text auf Bild“:** Alle Beiträge der Startseite stehen als Bildkarten mit Dachzeile „Rubrik | Datum“ und
  Titel im Foto (auf dem Verlauf nach Schwarz) – Nebenstücke, „Weitere Meldungen“, Küche, Rubrikblöcke und „Diese
  Woche“. Die Rubrikkacheln (Navigation) bleiben. Bewegung D und die Bilderpflicht bleiben.

  · Luis (`docs/abnahme/2026-11-20-logo-startseite.md`)
- **Punktbogen an jedem Beitrag:** Das Signet steht klein und dezent an jedem einzelnen Beitrag, als Bogen unten rechts
  im Bild (Anreißer, Listen, Kacheln, Kino, Termine, Suche, Artikelbild). Ausgenommen: Rubrikkacheln (Navigation),
  Leerzustände, Seiten, Verzeichnis, Anzeigen, Logo. Das ergänzt die Regel „nicht über Fotos, nicht in Anreißern“ aus
  dem Theme 3.5.0 um diese eine Ausnahme.

  · Luis (19./20.11., `docs/abnahme/2026-11-20-logo-startseite.md`)

## 19.11.2026

- **Freigaben vom 19.11.:**
  - Die Farben des Themes 3.4.0 kommen aufs Testsystem.
  - Die Form des Signets Tamil Dots 04A (`design/signature/master.svg`) ist freigegeben.
  - Die Richtung der Social-Karten (`design/social/`) stimmt und geht als Vorgabe ans Backend.
  - Als Nächstes kommt das Signet als Hintergrund-Element in die Website. Gezeigt wird es vor dem Einbau aufs
    Testsystem.

  · Luis (`docs/abnahme/2026-11-19-signature.md`)
- **Markenfarben und Signature-System:**
  - **Farben:** Hintergrund Weiß #FFFFFF, Hauptfarbe Titan Red #660000, Akzentfarbe Impact Red #B30000,
    Farbgewichtung „Red Dominance / Power“.
  - **Signet:** „Tamil Dots 04A“, Haupt-Element Tamil Dots A, unabhängig vom Logo.
    - Animation: Punkte bauen die Form auf.
    - Variante C nur als abgeleitetes Bewegungselement, Spatial nur an Sonderstellen.
    - Richtung: einheitliches Kartensystem für News, Social und Website.
  - **Was das ändert:** Die Farbwerte von klar2 (kühles Off-White, Logo-Rot) gelten nicht mehr. Ebenso die Regel „Rot nur
    als Akzent“.
  - **Was bleibt:** Bewegung D, die Bilderpflicht und die Gestaltung von klar2.

  · Luis (`docs/abnahme/2026-11-19-signature.md`)

## 17.11.2026

- **Kopfzeile mit Top-News in Rot:** Zwischen Datum und Suche steht wieder eine Zeile mit Direktlinks, jetzt als
  „Neu“ mit den Überschriften der neuesten Beiträge in Rot (ab 1024 px zwei, darunter einer, einzeilig mit
  Auslassung, am Handy ohne Datum), ohne den Aufmacher der Startseite und ohne den offenen Artikel. Kein Laufband,
  keine Bewegung. Die Zeile ist Navigation und deshalb von der Bilderpflicht ausgenommen. Ersetzt den Wegfall der
  Hinweise „Diese Woche“ vom selben Tag. · Luis
- **Aufteilung:** Luis' Sitzung macht nur noch Website, Design und Fulfillment. Dazu gehören das Theme, die
  Frontend-Teile von `tamil-site` und das Testsystem der Website. Nick macht das Backend: News-Radar, Cockpit, Agenten,
  Publisher, Social-Automatik und `tamil-radar`. Die Übergabe an Nick steht in `docs/uebergabe/backend-nick.md`. · Luis
- **Website-Ergebnisse direkt auf `main`, nur Website-Dateien.**
  - Was auf `main` kommt: `wordpress/themes/tamil`, `wordpress/plugins/tamil-site`, `wordpress/dev`,
    `wordpress/docker`, `wordpress/Dockerfile`, `design/`, `DESIGN.md` und `tests/wp`, als eigener Commit je
    Ergebnis. Ohne Radar und Backend.
  - Das Testsystem baut weiter aus `claude/radar-multiagent`. Dorthin wird jedes Ergebnis zuerst gemergt.
  - Weicht für diese Pfade bewusst von „nie direkt auf main“ ab (`CLAUDE.md`). · Luis
- **Bilderpflicht auf der Website:** Jeder sichtbare Anreißer, jede Listenzeile, Kachel, jedes Suchergebnis,
  „Weiterlesen“ und jeder Kino- und Termineintrag zeigt ein echtes Bild. Ausnahmen: Rubrikband, Fußlisten, Formulare,
  reine Textseiten (Impressum, Datenschutz). Das Theme nimmt das eigene Foto, sonst ein Bild aus dem Text, sonst ein
  gekennzeichnetes Symbolbild aus einem Commons-Pool je Rubrik (`docs/spezifikation/bilder-und-lizenzen.md` 2.7).
  Kehrt die frühere Regel um, Beiträge ohne Foto als reine Textzeile zu zeigen. · Luis
- **„Diese Woche“ nur mit Aktuellem:** Filme mit Spieltagen ab heute, Termine der nächsten 14 Tage (sonst die nächsten
  drei), nie Beiträge älter als 30 Tage ohne kommenden Termin; die Hinweise „Diese Woche“ in der Kopfzeile entfallen.
  · Luis
- **Rubrikband rot mit weißer Schrift** statt dunkel (Tinte). Aktive Rubrik mit 3 px Weiß darunter, Leselinie der
  Bewegung D hell, Fokusring weiß. Damit ist „Diese Woche“ die einzige dunkle Fläche; Rot ist als Fläche nur im Band
  erlaubt. Kehrt §10.1 von `design/brief.md` („Dunkle Flächen, genau zwei“, „Rot nie als Fläche“) für das Band um. ·
  Luis

## 16.11.2026

- **Bewegung D, Theme direkt in klar2, ohne Probeseite und Tor G3, direkt aufs Testsystem.**
  - Luis wählt aus der Vorschau die Variante D: Kopf faltet ins Band, rote Leselinie, Tiefe am Aufmacher, dunkle
    Fläche zieht auf, große Bilder decken auf, Listen steigen.
  - Statt Probeseite und Tor G3 wird das WordPress-Theme sofort umgebaut und über `claude/radar-multiagent` auf
    das Testsystem gebracht. Die Abnahme geschieht dort mit echten Beiträgen.
  - Das Cockpit folgt im zweiten Schritt.

  · Luis (`docs/abnahme/2026-11-16-G2-klar2.md`, Nachtrag)
- **Design: `klar2` statt „Tageskalender“, auf allen Seiten von Website und Cockpit.** Das kehrt zwei frühere
  Entscheidungen um:
  - das Urteil vom 13.11. („komplett generisch“, gilt für klar2);
  - die Wahl vom 14.11. (Mischung A + B, „Tageskalender“).

  Was daraus folgt:
  - Die Verbote aus „Runden 5–7“ in `abgelehnt.md` sind für die Bestandteile von klar2 aufgehoben. Das betrifft
    Dachzeilen, Bildkacheln mit Verlauf und Titel im Bild, den dunklen „Diese Woche“-Bereich, Rubrikkacheln und
    Metazeilen mit „·“.
  - Für die Gestaltung gelten wieder `design/brief.md` §10 (klar2) und diese Wahl. `design/brief-v3.md` und der
    Hallmark-Floor gelten nicht mehr, wo sie klar2 widersprechen.
  - Neu ist **Bewegung beim Scrollen**: ruhig, nicht hyperrealistisch, nur unter
    `prefers-reduced-motion: no-preference`. Luis wählt die Art aus einer Vorschau. Damit ist §10.1 („kein
    Einblenden beim Scrollen“) aufgehoben.
  - Tageskalender bleibt in der Git-Historie (`claude/mache-weiter-i23fs9`, Theme 2.0.0) und wird nicht weitergebaut.

  Weg: Vorschau Bewegung → `/design-ausbau klar2` für Website und Cockpit → Tor G3 → `/design-umsetzung`. · Luis
  (`docs/abnahme/2026-11-16-G2-klar2.md`)

## 14.11.2026

- **Theme „Tageskalender“: Wortdichte (Hallmark Gate 58) bewusst über der Grenze.** Die Dichte entsteht aus der
  Termintabelle Tag · Was · Wer · Wo, dem Teil aus Linie B, den Luis ausdrücklich wollte; sie liegt im Rahmen großer
  Nachrichtenseiten (Kritik r3). Keine Ausnahme im CSS-Stempel (Hallmark lehnt sie ab), sondern dieser Eintrag. ·
  Hauptsitzung · Wieder ansehen, wenn Luis die Seite mit echten Daten gesehen hat.
- **Eigenanzeigen auf ungebuchten Werbeplätzen bleiben (F3), bis Luis anders entscheidet.** Die Kritik r3 empfiehlt,
  ungebuchte Plätze leer zu lassen; das widerspricht der bestätigten Festlegung F3 („nach dem Ende steht wieder die
  Eigenanzeige“). Frage an Luis im Morgenbericht. · Hauptsitzung

- **Satzprüfung im Agent-Import strenger, aber ohne Überstrenge:** Zahlen nur als ganze Zahl, Zahlwörter und
  Verneinungen sind Fakten, höchstens drei überlappende Claims je Satz (nicht überlappende zählen nicht, statt den Satz
  abzulehnen), ein Name am Satzanfang braucht einen Beleg; Datum und Uhrzeit im Beleg tragen ihre Zahlen nur in ihrer
  Form („19.00 Uhr“ trägt 19, „12.50 Franken“ nicht 12). Szenario 95 hält fest, dass ein fremder Zusatzclaim einen
  belegten Satz nicht kippt. · Hauptsitzung nach Prüfung und zwei Gegenprüfungen
- **Kostendeckel je Story mit Prüfanteil:** Recherche, Schreiben, Faktencheck, Lektorat und SEO laufen bis Deckel minus
  Prüfanteil (Standard 1 $ − 0,30 $ = 0,70 $); Prüfung und Endprüfung bis zum vollen Deckel; ein KI-Bild zählt mit
  (darüber: Bildkarte). Variable `RADAR_KOSTEN_STORY_PRUEFUNG_USD`. · Hauptsitzung · Sonst konnte die Pflichtprüfung am
  Deckel scheitern.

- **Design: Mischung aus A (Tagesblatt) und B (Kalenderblatt), noch nicht fertig.** A gibt das Gerüst (Datum als
  Hauptfigur, Aufmacher mit großem Foto), B die Ordnung (Feste als Tabelle Tag · Was · Wer · Wo, Kino als Tabelle).
  Probe `hm-tageskalender`, danach Theme auf eigenem Branch; aufs Testsystem erst nach dem Ja von Luis. · Luis
  (`docs/abnahme/2026-11-14-design-luis.md`)
- **Stand vom 12.11. in `claude/radar-multiagent` zusammengeführt** (`d0e088c`, ohne Konflikte; 1491 Tests, 86 von 86,
  WordPress 177 von 177). · Luis
- **Nachtschicht 14./15.11. mit drei Ästen** statt zehn Aufgaben: Probe und Theme „Tageskalender“, Verzeichnis
  Radar-Seite (B1.4) mit Härtungen, Abnahmeprotokoll B5 (`docs/nachtschicht/2026-11-14.md`). Ohne Agent-Token keine
  Storys in dieser Nacht. · Hauptsitzung

## 13.11.2026

- **Bezahlte Werbebuchungen überdauern die Deinstallation** (steuerliche Aufbewahrung): Buchungen und Protokoll
  bleiben, nie bezahlte Buchungen werden entfernt; ganz gelöscht wird nur mit der Option
  `tamil_site_werbung_deinstallation_loeschen`. Datenversion 4 mit den Schritten F1 = 2, F3 = 3, F2 = 4. ·
  Hauptsitzung bei der Zusammenführung der Bausteine
- **Einsendungen ohne Abschluss werden nach 90 Tagen gelöscht** (F1 nannte nur Fristen für Abgeschlossenes); Abholen
  und Status bleiben auch bei ausgeschaltetem Schalter erreichbar, damit nichts liegen bleibt. Die Frist gilt auch bei
  angehaltenem Eingang (Stopp `eingang`): Was länger als 90 Tage nicht abgeholt wurde, wird ungesehen gelöscht. ·
  Hauptsitzung nach Code-Prüfung
- **Recherche bleibt nie offen:** Nachrecherche durch den Radar, zweite KI prüft, Ende immer als Entwurf oder
  verworfen mit Grund; keine Links von Hand. Termin-Seiten liefern ihre strukturierten Angaben (Datum, Uhrzeit,
  Adresse) mit. · Luis („Es muss alles mit der Recherche klappen … auch keine Links einfügen“)
- **Ja zu allem (21:50):** F0–F4 mit allen Vorschlägen, Regelwerk Social Fassung 1; Gedenk-Sperre für alle
  Terminquellen (dann Tempel Backnang an, mit Festauswahl `params.nur_titel`); Veranstalter STCC gesperrt
  (`[blocklist] veranstalter`); dein-dein.de an. Design: keine Auswahl, mehrere fertige Linien (A Tagesblatt, B
  Kalenderblatt, C Aushang, D Terrazzo), Luis wählt. Nicht automatisch: Freigabe der Rückblick-Entwürfe, Echtbetrieb
  neuer Funktionen, Tore B1–B3. · Luis (`docs/abnahme/2026-11-13-ja-zu-allem.md`)
- **Design aller bisherigen Runden abgelehnt, Neugestaltung mit Hallmark:** `mix-ordnung`, `mix-feed` und alles davor
  gelten als „komplett generisch“. Neuer Brief `design/brief-v3.md`; gestaltet wird mit dem Hallmark-Skill (Floor,
  Reflex-Gates, `sloplint --render`, Prüfung aus frischem Kontext). Der Hallmark-Floor geht den alten Regeln aus
  `tamil-marke`/`tamil-richtung` vor (keine Dachzeilen, keine Versal-Labels, keine „·“-Metazeilen). Website **und**
  Cockpit werden neu gestaltet. · Luis · „generischer AI-Slop“, der Auftrag hat Gewicht.
- **Neugestaltung auf Anordnung von Luis, ohne Umweg über `/design-runde`:** Die Hauptsitzung baut die erste Probe
  selbst (die Sitzung stand im Planmodus, Hintergrund-Agenten durften nicht schreiben); die Prüfung kommt trotzdem
  aus frischem Kontext (`design/kritik/hm-eigen-r1.md`). Abnahme durch den Auftraggeber bleibt Tor G4. · Luis
  („alles selber entscheiden“), Hauptsitzung
- **Erste Probe „Tagesblatt“ (`design/richtungen/hm-eigen/`):** Das Datum ist die Hauptfigur wie im tamilischen
  Küchenkalender; Rot (Logo-Rot) nur für Sonntage, Festtage, Logo, einen Primärknopf und den Fokus; Bananenblatt-Grün
  nur für den Kino-Bereich; Rethink Sans und Golos Text (OFL, selbst gehostet). · Hauptsitzung
- **Vertrag ohne weitere Festlegungsrunde bauen:** „Alle Sachen, die im Vertrag drinstehen“ gilt als Ja zu F4
  (Instagram, Facebook, WhatsApp-Entwurf; Trockenmodus bis Konten von KBS und Freigabe des Regelwerks) und als Ja
  zum Bau von F0–F3 auf dem Testsystem mit den Vorschlägen der Festlegungen; im Echtbetrieb bleiben neue Funktionen
  per Schalter aus, bis Auftragsverarbeitung und Rechtstexte vorliegen. · Luis
- **Lizenzpflicht für jedes Bild:** vollständiger Lizenz-Datensatz oder keine Freigabe; fehlt er, trägt die Redaktion
  ihn im Cockpit ein. Reihenfolge der Quellen und Felder in `docs/spezifikation/bilder-und-lizenzen.md`. · Luis
- **Software-Spezifikation** `docs/spezifikation/` ist ab jetzt die Grundlage für alle Bausteine (Felder,
  Statusmaschinen, Agenten, Automationen, Integrationen). · Luis („die ganze Software definieren“)

## 12.11.2026

- **Termin-Abgleich ohne Ort braucht einen Vereinshinweis:** Fehlt auf einer Seite die Stadt und teilen beide Titel nur
  ein Kernwort („Deepavali“), werden sie nur zusammengelegt, wenn derselbe Verein dahintersteht (Kürzel „MTS“ ↔ Quelle
  „München Tamil Sangam · Termine“, oder „Hamburg Tamil Sangam“ im Titel ↔ „HTS“; Portale wie „Swiss Tamil Info“
  sind keine Vereine). Ortsnamen auf -ring, -weg, -damm
  sind keine Straßen mehr; in Titeln ganz in Großbuchstaben zählen nur Wörter ohne Selbstlaut als Kürzel. · Hauptsitzung
  (Folgearbeit P3 aus PR #4) · Deepavali ist am selben Tag in vielen Städten; lieber eine Dublette als zwei Feste in
  einer Story. Bekannte Grenze: ein Fest mit zwei gemeinsamen Kernwörtern („Thai Pongal“) ohne Ort wird weiter
  zusammengelegt.
- **Film-Reihentitel bleibt getrennt (xfail bleibt):** „OM“ und „OM: Chapter 1“ werden nicht automatisch ein Film. ·
  Hauptsitzung · Bestätigt die Prüfung vom 11.11.; „Kantara“ und „Kantara: Chapter 1“ sind verschiedene Filme.
- **Nach außen schreibt immer die Redaktion:** Schema (`NewsArticle.author`), Feed (`dc:creator`) und oEmbed nennen den
  Namen der Autorenzeile („Redaktion Tamil.de“), nie einen Anmeldenamen. Autorenarchive leiten auf die Startseite,
  `/wp/v2/users` nur für Angemeldete. Abschalten über den Filter `tamil_site_autorenarchive`, sobald es Profile gibt
  (Lückenliste Nr. 1). · Hauptsitzung nach SEO-Prüfung · Bisher standen dort „luis“, „News-Radar“ und `ki-agent`.
- **Schlagwörter unter drei Beiträgen: noindex,follow und nicht in der Sitemap;** Benutzer nicht in der Sitemap,
  Rubriken vollständig. Herausgeber als `NewsMediaOrganization` mit Logo; Canonical für Start, Rubrik, Schlagwort. ·
  Hauptsitzung · F0 Punkt 2. Die Sitemap selbst bleibt die von WordPress.
- **Google-News-Sitemap: Vorschlag, nicht gebaut.** F0 sagt „Die Sitemap kommt weiter aus WordPress“. Eine eigene
  News-Sitemap (Beiträge der letzten 48 Stunden, wie bei Merzenich Aktuell) braucht das Ja von Luis. · Hauptsitzung

- **Gedenk-Sperre um Namen von LTTE-Gedenkanlässen erweitert, Terminquelle Vizha an:** `[blocklist] termine` nennt
  zusätzlich Thamilselvan, Brigadier (பிரிகேடியர்), Thileepan, Annai Poopathi/Poopathy, Prabhakaran (jeweils auch in
  Tamil-Schrift); Kittu/Kiddu/கிட்டு stehen in `termine_wort` und treffen nur als ganzes Wort (nicht „Kittur“, nicht
  das Verb „கிட்டும்“). Gesperrt wird nur die automatische Story; eine Redaktion kann solche Termine weiter von Hand
  bearbeiten. · Hauptsitzung · Die Vizha-Probe zeigte drei Gedenkturniere ohne Sperrbegriff (Thamilselvan Memorial
  Cup Dormagen, Colonel Kiddu Cup Rafz, Kiddu Cup Junior Seon); nach der Erweiterung blieben 28 Termine ohne
  Gedenkbezug, daher läuft „Vizha · Termine DACH“.
- **Ausland-Regel: Genf und Romandie zählen als DACH-Hinweis, Ajith nur als „Ajith Kumar“:** Genf/Geneva/Genève/ஜெனீவா
  (UN-Menschenrechtsrat, Kundgebungen) und Orte der Romandie (Lausanne, Fribourg, Neuchâtel, Sion als ganzes Wort …)
  halten eine Meldung drin; in der Kollywood-Ausnahme zählen Starnamen nur als ganze Wörter. Bekannte Restfälle, die
  durchkommen und im Cockpit abgelehnt werden: „ajith“ über die Kino-Hinweise der Kategorien, „Geneva Conventions“,
  „Credit Suisse“, Sion in Mumbai, TVK-Politik über „Vijay“; die Schreibweise ஜெனிவா fehlt noch. · Hauptsitzung nach
  drei Prüfrunden · Gegenüber dem Stand vor der Regel ist keiner davon ein Rückschritt.
- **Terminquelle Tempel Backnang vorerst aus:** Die Gedenktermin-Sperre (`[blocklist] termine`) wirkt heute nur bei
  `tribe_events`-Quellen; ob sie für alle Terminquellen gilt, entscheidet Luis (ändert Abnahme-Szenarien 15, 22–26).
  München Tamil Sangam (`tribe_events`) läuft. · Hauptsitzung nach unabhängiger Prüfung
- **Deutschsprachiger Text gilt für die Ausland-Regel als DACH-Presse:** Deutschsprachige Auslandsnachrichten (z. B.
  tagesschau zu Tamil Nadu) bleiben deshalb vorerst drin, wie vor der Regel. · Hauptsitzung · Ohne Anthropic-Schlüssel
  gibt es keine Grauzonen-Entscheidung; die Redaktion lehnt im Cockpit ab. Wieder ansehen mit Tor B1.
- **Der Verlagsname am Ende von Titel/Anriss ist kein Inhalt:** Er zählt für die Ausland-Regel weder als Bezug noch als
  DACH-Hinweis; in `score_item` und `hat_bezug` zählt er vorerst weiter. · Hauptsitzung
- **Kollywood und Stars gelten für die Ausland-Regel als Kino/Entertainment:** Nachrichten ohne DACH-Bezug aus der
  Kollywood-Quelle (`kollywood = true`) oder mit einem Begriff aus `[bezug] kollywood` (Kollywood, Rajinikanth, Vijay,
  Ilaiyaraaja …) fallen nicht als „ausland“ heraus, auch wenn die Stichwörter der Kategorien „news“ ergeben. ·
  Hauptsitzung nach unabhängiger Prüfung · „Rajinikanth meets Tamil Nadu Chief Minister“ und „Ilaiyaraaja honoured by
  India“ fielen sonst heraus.
- **Design: Mischung aus `klar2` und den Gen-Z-/Feed-Entwürfen, überall Bilder.** Das Live-Design (Runde 2) ist für
  Luis „hässlich und klassisch“; frühere Entwürfe fand er besser. Zwei Probeseiten (`mix-ordnung`, `mix-feed`), dann
  entscheidet Luis (G3). Jeder Anreißer mit Bild (nur mit Nachweis). Die Haltung „im Zweifel leiser“ aus Runde 2 gilt
  für diese Runde nicht mehr; die Verbotsliste (`abgelehnt.md`) gilt weiter. · Luis · `docs/abnahme/2026-11-12-design-luis.md`
- **Schreib-Automatik später:** Kein Anthropic-Schlüssel und keine tägliche Routine vorerst; der Radar scannt weiter, das
  Schreiben bleibt manuell über den Agent-Modus. · Luis

## 11.11.2026

- **Bild mit Nachweis (`POST /api/agent/bild`):** Ein Agent darf für einen wartenden Entwurf ein Bild vorschlagen, der
  Radar prüft Herkunft und Rechte selbst und setzt Nachweis und Lizenz aus Commons bzw. dem Register, nie aus dem
  Vorschlag. Erlaubt: Wikimedia Commons nur mit Lizenz-Adresse bei creativecommons.org (CC BY, CC BY-SA; nichts mit NC
  oder ND) und eigenes Material von Hosts aus dem Register `[[bildquellen]]` (Tempel, Vereine, Veranstalter, Kinos;
  Plakate gehören dem Verleih), nur wenn die Seite ein Beleg der Story ist. Abgelehnt: Agenturbilder, Logos, Banner,
  Bilder auf fremden CDNs, soziale Netzwerke, KI-Bilder. · Hauptsitzung nach vier unabhängigen Code-Prüfungen · Luis
  will „überall Bilder“, aber keine fremden Fotos ohne Recht.
- **Freigabe gilt nur für den gesehenen Stand:** Jeder Entwurf trägt einen Zähler `stand` (Migration 6, Trigger bei
  jeder inhaltlichen Änderung). Freigabe, Sammelfreigabe und Veröffentlichen nehmen den Stand mit, den die Redaktion
  gesehen hat; hat sich der Entwurf inzwischen geändert (z. B. ein Bild kam dazu), wird die Freigabe abgelehnt
  („veraltet“). Belege und Claims zählen den Stand bewusst nicht, weil sie den Text nicht ändern. · Hauptsitzung
- **Rückblick 2026:** Die Website bekommt die wichtigsten Ereignisse des Jahres 2026 aus der tamilischen Community in
  Deutschland, Österreich und der Schweiz als neu geschriebene Beiträge; der Altbestand bleibt unverändert stehen.
  Neueste zuerst. · Luis („komplett auffrischen, nur mit Daten aus 2026, die aktuellen nach oben, nichts löschen“)
- **Nachtrag statt Rückdatierung ohne Hinweis:** Jeder Rückblick-Beitrag trägt das Datum des Ereignisses und am Ende
  den Vermerk, dass er im November 2026 für den Rückblick geschrieben wurde. Im Cockpit steht „Nachtrag · Datum“. ·
  Hauptsitzung · Ein Beitrag darf nicht so aussehen, als sei er damals erschienen.
- **Vorschläge für den Rückblick kommen über `POST /api/agent/vorschlag`**: Thema, Datum und ein bis sechs Quellen.
  Der Radar ruft die Quellen selbst ab; Titel, Herausgeber und Text zählen nur aus der abgerufenen Seite. Für
  Nachträge läuft nie ein bezahlter Modell-Job; eigene Tagesgrenze `RADAR_NACHTRAG_TAG`. · Hauptsitzung nach
  unabhängiger Code-Prüfung
- **Länge nach Stofflage:** wenig Stoff (unter 4 bestätigte Aussagen) Kurzmeldung 80–150 Wörter; mittel (4–7, mit
  Volltext) 250–400; viel (ab 8 aus zwei Verlagen oder aus einer Primärquelle mit Volltext) 450–750, Kino und Termine
  350–550; Dossier 600–1000. Zwischentitel ab 350 Wörtern. Ohne Volltext nie mehr als knapp. · Luis („nicht nur eine
  Minute, sondern mehrere Minuten“) · Länge entsteht nur aus belegtem Stoff, nicht aus Füllsätzen.
- **Stil wie die alte Seite:** 19 Beispiele aus dem Altbestand dienen als Tonvorlage (je Story zwei passende). Viele
  lange Altbeiträge sind aus anderen Medien übernommen; sie sind nur Vorbild für den Ton, neue Beiträge entstehen aus
  den Quellen. · Luis („genau in dem gleichen redaktionellen Stil“)
- **Freigabe bleibt bei Luis:** Rückblick-Beiträge erscheinen erst nach Freigabe im Cockpit; neu ist „Ausgewählte
  freigeben“ (bis 100 auf einmal). · Hauptsitzung · Vertrag §8 Abs. 1
- **Bilder:** Plakate und Szenenbilder vom Verleih, Material von Veranstaltern, Tempeln, Vereinen und von der
  betroffenen Person selbst, Wikimedia Commons mit Lizenz, später eigene Instagram-Bilder; jeweils mit Nachweis. Sonst
  die Bildkarte „Grafik: Tamil.de“. Keine Agenturfotos aus anderen Medien (dpa, Keystone, Getty …), keine KI-Bilder.
  · Luis („mit allen Bildern, alles Mögliche“), Grenze bei Agenturfotos: Hauptsitzung · Fremde Agenturfotos sind
  ohne Lizenz ein Abmahnrisiko für KBS.
- **Instagram als Quelle nur über einen Export oder den offiziellen Zugang von Meta**, nicht durch Auslesen der
  Seite. Der Rückblick startet ohne Instagram. · Luis („ausgenommen von Instagram kannst du es trotzdem machen“) ·
  Vertrag §3 Abs. 3
- **Laufende Automatik für neue Meldungen:** Der Radar bekommt weitere Quellen aus einer Quellen-Inventur. Schreiben
  ohne Zutun braucht den Anthropic-Schlüssel (Tor B1) oder bis dahin eine tägliche Runde im Agent-Modus. · Luis („eine
  Automation, dass immer alles neu rausgesucht wird“)
- **Angaben für Suchmaschinen und Cache-Kopfzeilen haben keinen eigenen Schalter** und sind live; sie enthalten keine
  Geschäftsregel. Auf das Ja zu F0 warten nur die Rollen-Zuordnung, das Einschalten des Cookie-Hinweises und die
  Löschfristen. · Hauptsitzung nach Code-Prüfung
- **Das Testsystem ist für Suchmaschinen gesperrt**, solange `WP_ENVIRONMENT_TYPE` nicht `production` ist (noindex,
  `robots.txt`, keine Sitemap). · Hauptsitzung · Sonst stünden 535 Beiträge doppelt im Netz.
- **Der Vertrag ist der Maßstab.** Für tamil.de gilt Anlage 1, Teil A und B des Gesamtvertrags (Vertragsstand
  11.11.2026). Das Leistungsverzeichnis steht in `docs/vertrag/leistungen.md`; Preise, Zahlungsplan und die
  Vertragsdatei liegen nicht im Repo. Merzlicht und AJ Gamestation sind eigene Projekte. · Luis („genau so müssen wir
  das angehen, alles für tamil.de übernehmen und fertig machen, genauer definieren zusammen“)
- **Reihenfolge der Bausteine:** Grundlage, dann Formulare und Verzeichnis, dann Werbebuchung, dann Instagram und
  Facebook. · Luis · Formulare und Verzeichnis brauchen am Anfang nichts von KBS, und die späteren Bausteine bauen
  darauf auf.
- **Zahlungsanbieter: Stripe**, zuerst im Testmodus; KBS legt später ein eigenes Konto an. · Luis
- **Erst festlegen, dann bauen:** Je Baustein eine Festlegung (`docs/vertrag/festlegung-<baustein>.md`, für Luis als
  Reiter im Projekt-Dokument); Luis bestätigt oder ändert, dann wird gebaut. Neue Tore F0 bis F4. · Luis · Der
  Vertrag verlangt für alles Automatische freigegebene, dokumentierte Regeln (§8 Abs. 1).
- **Website und Cockpit bleiben getrennt abnehmbar:** WordPress hält Öffentliches, Kunden und Geld (Formulare,
  Verzeichnis, Werbebuchung, Zahlung); das Cockpit hält Agenten, Prüfung, Freigabe, Zeitplan, Stopp und Protokoll.
  Der Radar holt bei WordPress ab, nie umgekehrt. · Hauptsitzung nach gegengeprüftem Bauplan
- **Keine automatische E-Mail, auch keine Bestätigungen** (§8 Abs. 2). Rückmeldung steht auf der Website; die
  Buchungsübersicht kommt über einen geheimen Link. Ein Test sichert ab, dass im Code kein Mailversand vorkommt. ·
  Hauptsitzung
- **WhatsApp bleibt Handarbeit:** Entwurf zum Kopieren, weil Meta für Kanäle keine Schnittstelle zum Veröffentlichen
  nennt (geprüft in der Doku von Meta am 11.11.). · Hauptsitzung · Vertrag B3, §3 Abs. 3
- **Neue Funktionen sind im Echtbetrieb aus**, bis Auftragsverarbeitung und Rechtstexte vorliegen; auf dem Testsystem
  (Vorschau-Adresse) laufen sie. · Hauptsitzung · §8 Abs. 3
- **„Alle Szenarien“ statt „51/51“:** Die Abnahme des Radars wächst mit den Bausteinen; die Regel nennt keine feste
  Zahl mehr. · Hauptsitzung
- **Website steht mit dem vollen Altbestand** (532 Beiträge, 7 Seiten, 1445 Medien, 25 Weiterleitungen; Stichprobe,
  alle Weiterleitungen und der zweite Lauf ohne Befund). Der Radar ist verbunden und veröffentlicht Freigegebenes
  direkt. · Ablauf `/website-live` · Prüfliste in `docs/abnahme/2026-11-11-uebernahme.md`
- **Coolify-Zugang über Tokens aus dem Chat.** Luis hat zwei Tokens als Bildschirmfoto gegeben und angewiesen, sie zu
  verwenden („behalte den und mache“); der DNS-Eintrag für das sichere Formular wurde nicht gesetzt. Die Werte liegen
  nur in Sitzungsdateien, wurden nie ausgegeben und nur für die beiden Tamil-Apps benutzt. Beide Tokens sind zu
  widerrufen (Tor B2). Das löst den Eintrag vom 10.11. („Zugang bleibt beim DNS-Namen“) für die Einrichtung ab; als
  Zielzustand bleibt er richtig. · Luis

## 10.11.2026

- **Website geht jetzt auf Coolify, mit echten Inhalten und dem bisherigen Theme** (App „tamil-web“ unter der
  Vorschau-Adresse; voller Altbestand, Radar verbunden). Das neue Design `klar2` folgt als Theme nach dem Urteil des
  Auftraggebers und der Probeseite. · Luis („alles auf Coolify pushen, deployen“; auf Rückfrage: Website mit echten
  Inhalten)
- **Die drei schon freigegebenen Entwürfe** (Diwali in Basel, „Scene“, „Ramayana“) **erscheinen beim Verbinden alle
  drei.** · Luis · Diwali in Basel ist mit 73 Wörtern kurz und hat keine Quellenzeile; das war ihm bekannt.
- **Coolify-Zugang bleibt beim DNS-Namen:** Das sichere Formular nimmt nur echte Hostnamen an, die Adresse
  `coolify.167.233.76.202.sslip.io` lehnt es ab. Luis legt den A-Eintrag `coolify.hk-growthoperator.de` auf den
  Coolify-Server, trägt die Adresse in Coolify ein und erzeugt ein Token ohne Root-Rechte (Tor B2). · Luis · Die
  Alternativen (Token als Umgebungsvariable, App von Hand anlegen) hat er nicht gewählt.
- **Texte der alten Seite bleiben unverändert**, auch Kontaktangaben darin (`info@tamil.de` ist die echte Adresse der
  alten Seite). Leer bleiben nur die Kontaktfelder der neuen Website, bis der Auftraggeber die echten Werte nennt;
  die Beispielwerte aus `prototyp/content/site.json` werden nie eingetragen. · Hauptsitzung nach Code-Review · Das
  Import-Werkzeug hatte die Adresse zuerst aus 11 Beiträgen entfernt.
- **YouTube-Videos laden erst nach Klick** (Box „Video laden“, dann youtube-nocookie.com); das gilt für alle
  übernommenen Beiträge. · Hauptsitzung · Pflicht aus den Markenregeln (Drittanbieter erst nach Klick); der feste
  Player lief am Handy außerdem seitlich über.
- **`klar2` passt, das Aufmacherfoto bleibt groß (4:3).** `klar2` wird die Vorlage für den Auftraggeber; `klar`
  bleibt als Rückfall im Repo. · Luis · nach der internen Vorschau und dem Blick auf alle Bilder im Chat. Am Desktop
  stehen damit sechs statt rund zehn Schlagzeilen im ersten Bildschirm; das ist so gewollt.
- **`klar` bekommt mehr Wow: Fassung `klar2`.** Überall ein Bild (kein Anreißer ohne Bild), großes Aufmacherbild mit
  der Schlagzeile im Bild, Rubrikkacheln mit Bild, große Bildkacheln in „Küche“, ein dunkler Bereich „Diese Woche“,
  ein dreiteiliger Kopf mit dunklem Rubrikband, sanfte Bewegung. · Luis · nach dem Blick auf die Vorlage: „gut vom
  Design, aber noch ein wenig zu classic“; er hat alle acht angebotenen Verstärkungen gewählt.
- **Dafür gelockert, jeweils mit messbarer Grenze** (`design/brief.md`, Abschnitt 10): genau zwei dunkle Flächen in
  der kühlen Tinte (bisher: Dunkel verboten); heller Titel im Bild auf einem Verlauf (bisher: kein Verlauf, kein
  Text im Bild); Zoom beim Überfahren bis 1,04 und ein stehendes Rubrikband (bisher: keine Bewegung); Schlagzeile des
  Aufmachers bis 34 und 44 px (bisher 32 und 38); Kopf am Handy bis 152 px (bisher 120); drei Bildformate (bisher
  zwei); Aufmacherbild und je eine große Kachel bis zur Dateibreite. · Hauptsitzung nach Luis' Auswahl · Unverändert
  bleiben Rot höchstens 3 %, keine rote Schrift über 20 px, normale Schriftbreite, Radius höchstens 2 px, nur
  Deutsch. Runde 4 ist an „zu laut“ gescheitert; deshalb hat jede Lockerung eine Zahl.
- **Einträge aus dem News-Radar ohne Foto bekommen eine gestaltete Kachel**, kein erfundenes Bild. · Hauptsitzung ·
  Der Radar erzeugt für solche Beiträge schon heute eine Grafik („Grafik: Tamil.de“); deren Aussehen folgt später der
  abgenommenen Kachel.
- **Reihenfolge der Vorlage:** Luis sieht `klar2` zuerst in der internen Vorschau; die Vorlage für den Auftraggeber
  wird erst danach und nur ohne offenes P0 oder P1 ersetzt. · Hauptsitzung · Zwei Runden sind ungesehen
  weitergegangen und durchgefallen.
- **Probe `klar` wird ausgearbeitet** (nüchtern und kompakt nach BBC und Tagesschau, Schrift Libre Franklin). Brief 2
  ist damit bestätigt. · Luis · gewählt, ohne die Vorschau anzusehen; er sieht die Vorlage, bevor sie zum
  Auftraggeber geht. `blatt` und `bild` bleiben als Alternativen im Repo.
- **Vorlage für den Auftraggeber als eigenes Artifact**, getrennt von der internen Vorschau (dort liegen Bilder
  fremder Nachrichtenseiten zum Vergleich). · Hauptsitzung

## 09.11.2026

- **Neue Richtung: wie eine große Nachrichtenmarke.** Ruhig und seriös, viele Geschichten auf einen Blick, Rot nur
  als Akzent, normale Schrift; Vorbilder Zeit Online, Spiegel, Tagesschau/BBC, Guardian/NZZ. Das löst den Eintrag
  „Redesign für Gen Z: Hypebeast/Highsnobiety, Rot trägt die Seite“ weiter unten ab, ebenso „erster Bildschirm = die
  eine große Geschichte“ und „laut im Kopf“ vom selben Tag. · Luis · nach Ablehnung der vier Richtungsskizzen („zu
  viel Rot, zu laut“, „Baukasten“, „Schrift ist hässlich“, „nicht hochwertig genug“).
- **Prüfung misst statt zu bepunkten.** Die Summe 28/40 ist kein Tor mehr. Durchgelassen wird, was die harten
  Kriterien des Briefs erfüllt und kein offenes P0 oder P1 hat. Luis sieht Schnellproben früh und ungefiltert; der
  Auftraggeber sieht weiter nur Gewähltes und Bestandenes. · Hauptsitzung, von Luis mit „mache es weiter“ getragen ·
  Drei Skizzen hatten mit genau 28/40 bestanden und fielen bei Luis sofort durch.
- **Design-Runde 1, Ergebnis der Kritik:** `zine`, `raster` und `feed` bestehen nach einer Überarbeitung mit je
  28/40 und kommen auf die Vergleichsseite. `plakatwand` erreicht 29/40, hat aber ein offenes P1 und wird nach der
  Regel „nur bestandene“ nicht gezeigt. Stand in `docs/abnahme/2026-11-09-G2.md`. · Ablauf `/design-runde`
- **Radar: keine Ländernamen in der Ausland-Liste.** „Sri Lanka“ oder „Indien“ stehen in fast jedem Bericht der
  Diaspora und würden echte Termine ohne bekannte Stadt verwerfen; in der Liste stehen nur Orte. Altersgrenze für
  Termin-Berichte: 30 Tage (`RADAR_EVENT_MAX_ALTER_TAGE`). · Code-Review, Hauptsitzung
- **Tor G1 bestätigt (vorläufig):** Brief `design/brief.md` mit den Vorbildern des Scouts; die Auswahl des
  Auftraggebers fließt bis G2 ein. Alle vier Richtungen gehen in die Skizzenrunde. · Luis · Die Runde soll nicht auf
  die Rückmeldung warten.
- **Nur Deutsch:** keine tamilische Schrift als Gestaltungsmittel. Die Richtung „Raster + Tamil-Schrift“ wird zu
  „Raster + große Schrift“. · Luis
- **Erster Bildschirm = die eine große Geschichte** (Cover); Kino und Events folgen als zweiter Abschnitt. Laut im
  Kopf, ruhig im Text. · Luis
- **Radar: nur Meldungen mit tamilischem Bezug.** Allgemeine Schweizer Meldungen (Unfall, Polizei, Wahl) erscheinen
  nicht; Quellen, die solche Meldungen liefern, verlangen ein Community-Stichwort. · Luis · Leser finden das auf
  Deutsch überall, und jede Recherche kostet.
- **Coolify-Zugang über DNS-Namen und sicheres Formular:** `coolify.hk-growthoperator.de`, enges Token statt
  Root-Token, Wert nie im Chat (Tor B2). · Luis
- **Projekt-Ordnung (Phase 7):** `CLAUDE.md`, `docs/`, `design/`, Bereichsregeln, 12 Skills, 10 Agents, 7 Commands, vier
  Abnahme-Tore. · Luis · Drei Designrunden sind am Ablauf gescheitert, das Wissen lag nur im Chat.
- **`prototyp/` bleibt Archiv**, Pfade unverändert; `prototyp/content/` bleibt Datenquelle. · Luis · Kein Umbau ohne
  Nutzen.
- **PR #1 wird jetzt gemergt** (Merge-Commit), PR #2 danach gegen `main`; PR #2 wird nach Tor G4 gemergt. · Luis
- **Adressen:** Der Radar bleibt unter `tamil.hk-growthoperator.de`, die Website läuft vorerst unter
  `tamil-web.167.233.76.202.sslip.io`. · Luis · Kein DNS-Aufwand jetzt.
- **Agents mit gemischten Modellen:** Opus für Gestalten, Bauen, Kritik, Code-Prüfung, Redaktion; Sonnet für
  Referenzsuche, Technik-QA, Migration. · Luis · Qualität dort, wo sie zählt, Limit schonen.
- **Kritik-Filter:** Der Auftraggeber sieht nur Richtungen mit mindestens 28/40 und bestandenem Slop-Test. · Luis
- **Abnahmen über Luis**, Referenzen aus Auftraggeber und Scout, Design und Website-Livegang parallel, alle vier
  Richtungen in die Skizzenrunde (Kollywood-Plakatwand, Diaspora-Zine, Raster + Tamil-Schrift, Vertikaler Feed). · Luis
- **Gen-Z-Probeseite abgelehnt** („Trash, komplett generisch“, aber „viel Potenzial, Luft nach oben“). · Auftraggeber
  über Luis · Siehe `.claude/skills/tamil-marke/references/abgelehnt.md`.
- **Redesign für Gen Z:** jung und alt gleich lesbar, Hypebeast/Highsnobiety und Instagram/TikTok als Richtung, Rot trägt
  die Seite, helles Grundbild. · Auftraggeber über Luis · Community-Magazin galt als „altbacken, hingerotzt“.
- **Keine Demo-Inhalte:** Der ganze echte Altbestand von tamil.de wird übernommen (Originaldatum, Slug, Bilder, Seiten,
  301-Weiterleitungen). · Luis
- **„Freigeben“ veröffentlicht sofort** (`WP_POST_STATUS=publish`). · Luis
- **Website als zweite Coolify-App** (WordPress mit SQLite, ein Container). · Luis
- **Agent-Modus übers Netz** (`/api/agent/export|import`, eigenes Token): wartende Storys schreibt eine Claude-Sitzung
  ohne API-Kosten. · Luis · Der Anthropic-Schlüssel fehlt noch.
- **Radar komplett in Coolify** (ein Container: Cockpit, Scan, Worker, Digest, Sicherung), gebaut von
  `claude/radar-multiagent`. · Luis · Statt systemd auf dem HK-Server.
- **Pilot:** 2 $ pro Tag und Monat, 5 Entwürfe pro Tag, keine KI-Bilder, 20 Quellen, Modelle je Rolle wie gesetzt. · Luis
- **Ausland-Filter:** Termine außerhalb von DE/AT/CH werden verworfen (Kanada, UK, Sri Lanka, Indien …). · Ergebnis des
  kostenlosen Pilot-Scans.
- **Root-Token nur für die Einrichtung**, danach widerrufen (Tor B2). · Luis

## 08.11.2026

- **Nachtlauf freigegeben:** Multi-Agenten-Redaktion nach dem Blueprint vom 19.10. ohne Rückfragen bauen. · Luis

## 20.10.2026

- **Blueprint umgesetzt:** Branch `claude/radar-multiagent` mit eigenem PR; Modelle je Rolle (Haiku: Signal, Cluster,
  Lektorat, SEO · Sonnet: Recherche, Faktencheck, Text · Opus: Dossier); keine Embeddings; 20 aktive Quellen;
  Bildreihenfolge Archiv → Quelle → Stock → Pool → KI → Karte. · Luis
- **Newsletter komplett entfernt** (Theme, Plugin, Prototyp, Doku). · Luis
- **Erster Entwurf (Nachtblau, Gold, Ornamente, Tamil-Wörter vor Überschriften) abgelehnt** als „Katastrophe“. ·
  Auftraggeber
