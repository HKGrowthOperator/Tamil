# Unabhängige Prüfung: Theme „Tageskalender“ v2.0.0 (tamil.de)

Stand: Commit 323c544, Branch claude/mache-weiter-i23fs9, lokal http://127.0.0.1:8086, geprüft am 15.11.2026.
Grundlage: `design/brief-v3.md`, `tamil-kritik`, `tamil-marke` mit `references/abgelehnt.md`, Hallmark-Floor
(`SKILL.md` § The Floor, `references/fonts.md`). Begründungen und frühere Kritiken habe ich nicht gelesen.

Kopfzeile: Harte Kriterien (Brief v3, Abschnitt „Was fest bleibt“, plus Hallmark-Floor): 2 verletzt (Tippflächen, echte Inhalte) und 2 Floor-Punkte verletzt (10, 13) · P0: 0 · P1: 7 · P2: 5 · P3: 3

## Erster Eindruck

Das Theme hat eine echte, durchgehaltene Idee: Das Datum ordnet alles, von der Tagesziffer auf der Startseite über die
Artikelspalte bis zu den Monats- und Tagesköpfen der Listen. Dazu kommt ein ruhiger Satz aus zwei Familien, ohne
Dachzeilen, Versal-Labels oder Kartenraster. Mit den aktuellen Testdaten kippt genau diese Idee aber gegen die Seite:
Unter „15 November 2026“ steht ein Aufmacher vom 18. Oktober, daneben zwei leere Kästen, und Archivbilder ohne Bezug
füllen die Listen. Der Kunde sähe eine Kalenderseite, die nichts Aktuelles zeigt.

## Messwerte

Selbst gemessen mit Playwright (Messskript im Arbeitsordner der Sitzung B) auf acht Seitentypen bei 390 und
1280 px. Überlauf und Konsole stammen aus `theme-shots/bericht.json` (390/820/1280).

| Kriterium | 390 | 1280 | Ergebnis |
|---|---|---|---|
| Seitliches Scrollen (8 Seiten × 3 Breiten) | 0 px | 0 px (auch 820) | erfüllt |
| Konsole | nur der gewollte HTTP-Status 404 auf der 404-Seite | dto. | erfüllt |
| Fließtext Artikel | 18 px / 28,8 px Zeilenhöhe, ca. 40 Zeichen pro Zeile | 19 px, Spalte ca. 540 px, ca. 60 Zeichen | erfüllt (v3 fordert ≥ 17, Marke ≥ 18) |
| Vorspann / Anreißertext | 18 px | 20,5 px / 18 px | erfüllt |
| Meta „wo“ / Bildnachweise | 16 px / 14 px | 16 / 14 px | Hinweis (kein Fließtext) |
| Kontrast (alle Textknoten gegen den nächsten deckenden Grund) | kein Wert < 4,5:1 | kein Wert < 4,5:1 | erfüllt; Platzhalter in Eingabefeldern nicht gemessen |
| Tippflächen < 44 px | „Quelle“ 198×35 und 50×33, Artikel-Quellenlink 235×20, Kontakt „WeTransfer“ 98×22, Artikel-Navigation „Kino“ 39×46 | – | **verletzt** (P2, Befund 9) |
| Schlagzeilen | Aufmacher und H1 30 px, Tagesziffer 48 px (Gewicht 800) | Aufmacher und H1 39,7 px, Tagesziffer 73,6 px | Hinweis: größte Schrift ist die Ziffer, schwarz, nicht rot |
| Schriftfamilien | Rethink Sans (Titel), Golos Text (Text), Catamaran Tamil nur für Tamil | dto. | erfüllt: beide in Hallmark `fonts.md` (Z. 30, 40), nicht auf impeccable- oder Projekt-Verbotslisten |
| Versalien/Sperrung/Kapitälchen (Floor 9) | 0 Treffer | 0 Treffer | erfüllt |
| „·“-, „•“-, „\|“-Metazeilen (Floor 10) | 1 im Template (Artikel-Quelle), 1 im Inhalt (Kontakt) | dto. | **verletzt** (Befunde 4, 14) |
| Wörter im ersten Bildschirm Start (Floor 13, „about 80“) | – | ca. 110 (von Hand gezählt) | **verletzt** (P2, Befund 12) |
| Aufmacher: Titel, Satz, Aktion bei 1280×800 sichtbar (Floor 12) | – | ja (Aktion bei y ≈ 472) | erfüllt |
| `overflow-x: clip` auf html, body (Floor 4) | theme.css:65 | | erfüllt |
| Hallmark-Stempel erste Zeile (Floor 15) | theme.css:1 | | erfüllt |
| Logo unverändert | md5 identisch mit `design/inhalte/logo.png` und `prototyp/static/img/logo.png` | | erfüllt |
| Tamil nur im Inhalt, `lang="ta"` | `tamil_ohne_lang` 0; Tamil nur in Plakatbildern | | erfüllt |
| Kartenraster, Verlaufskacheln, „Diese Woche“-Band, Dachzeilen | keine gefunden | keine | erfüllt |
| sloplint | statisch `theme.css`: 0 FAIL, 3 WARN, 1 Verzicht abgelehnt; `--url /`: sauber; **Render-Stufe lief nicht** (kein puppeteer-core) | | Befund 13 |

## Befunde

### P1

1. **Start, alle Breiten: Der Aufmacher wirkt wie die Nachricht von heute, ist aber vier Wochen alt.** Unter der
   Tagesziffer „15 November 2026, Sonntag“ steht ohne eigenes Datum „Protest in Bern gegen den Abriss der
   Thileepan-Statue in Jaffna“. Der Beitrag ist laut REST-API vom 18.10.2026. Bei einer politischen Meldung ist das ein
   Redaktionsrisiko und kein reines Datenproblem: Das Template zeigt das Datum des Aufmachers nie
   (`template-parts/home/blatt.php`, Kopf Z. 3, `article.aufmacher` Z. 23). Behebung: Ist der Aufmacher nicht von
   heute, gehört unter die Schlagzeile ein eigenes Datum in derselben Form wie in den Listen („vom 18. Oktober“).
   Alternativ steht die Tagesziffer nur, wenn der Aufmacher höchstens 48 Stunden alt ist.

2. **Archivbilder ohne Bezug, mit erkennbaren Personen, mehrfach wiederholt** (`inc/bausteine.php:58–60` und `:186`,
   `template-parts/kino-seite.php:25`, `page-events.php:60`):
   - Start 1280/390: Das Porträt eines Schauspielers vor rotem Grund steht zweimal neben „Jailer 2“. Der Leser hält
     den Mann für einen Darsteller des Films.
   - Kino, erster Bildschirm 1280: Dasselbe Porträt ist das Kopfbild der Rubrik.
   - „Komponist Deva ist tot“: Die Todesmeldung trägt ein Foto einer Bharatanatyam-Tänzerin.
   - Start 1280: Dasselbe Tempelwagen-Foto erscheint dreimal direkt hintereinander (Ramayana Pforzheim, Beat Your
     Heart, Vaango Workshops). Auch das Kopfbild von Events ist dieses Foto.

   Das liest sich generiert und ist bei Personenbildern auch rechtlich unschön. Der Zusatz „Archivbild der Rubrik“
   ändert daran wenig. Behebung: Ohne eigenes Foto eine Zeile ohne Bild setzen; Nachrichtenlisten vertragen das.
   Rubrikbilder ohne erkennbare Personen (Kinosaal statt Schauspieler). Nie dasselbe Bild in benachbarten Zeilen
   und nie bei Todesmeldungen.

3. **Leere Module im ersten Bildschirm.** Start 1280: „Die nächsten Feste“ zeigt „Gerade steht kein kommendes Fest im
   Kalender…“, „Im Kino“ zeigt „Für diese Woche kennen wir keine tamilische Vorstellung…“. Dasselbe gilt für den
   zweiten Bildschirm am Start bei 390, für Kino „Im Programm“ und für Events „Ab heute“, jeweils im ersten Bildschirm.
   Quellen: `template-parts/home/blatt.php:39`, `inc/bausteine.php:697`, `page-events.php:84`. Erwartbar bei alten
   Daten, aber ein Kalender-Konzept, das dreimal „nichts da“ sagt, ist dem Kunden nicht zu zeigen. Für Kino gibt es
   einen Ausweg (`bausteine.php:695`), für Feste und Termine nicht. Behebung: Fallback „Zuletzt im Kalender“ mit den
   letzten zwei bis drei Terminen, als vergangen gekennzeichnet, oder das Modul auf eine Zeile einklappen. Vorgeführt
   wird nur mit aktuellen Terminen.

4. **Hallmark-Floor 10, Verbotsliste Runde 5–7: „·“-Metazeile im Artikel.** Unter dem Text steht „Quelle:
   SwissTamilMedia · Community“ (Artikel, 390 und 1280). Ursache: `template-parts/article/quelle.php:15–17` gibt
   `quelle_name` roh aus. Die Listen normalisieren den Punkt bereits (`inc/bausteine.php:215`). Behebung: dieselbe
   Ersetzung auch in `quelle.php`, besser zentral beim Import.

5. **Werbetext mit nicht belegter Behauptung** (Plugin `tamil-site/includes/ads.php:85`, sichtbar auf Start, Kino im
   ersten Bildschirm 1280, Suche und 404). Die Anzeige lautet „Die Konzertreihe von Tamil.de mit A.R. Rahman,
   Ilaiyaraaja, Anirudh und Santhosh Narayanan in Deutschland, Österreich und der Schweiz.“ und verlinkt „Tickets“.
   Die Quelle (`prototyp/content/site.json:657`) sagt nur „standen oder stehen mit Tamil.de Production auf deutschen
   Bühnen“. Österreich, Schweiz und die Gegenwartsform sind dazuerfunden. Behebung: den Wortlaut der Quelle übernehmen
   oder einen Platzhalter sichtbar kennzeichnen.

6. **Kontakt: erfundene Leistungszusage an Werbekunden** (`page-kontakt.php:105`): „Formate nach IAB-Standard,
   monatlicher Bericht mit Einblendungen und Klicks.“ `docs/` und `prototyp/content/` enthalten keinen Beleg (Suche
   nach „IAB“: kein Treffer). Die Antwort des Prototyps zu Werbeplätzen ist als „(Beispieltext)“ markiert. Diese
   Zusage hängt am Vertrag (Festlegung F3 Werbung). Behebung: streichen oder als Platzhalter kennzeichnen, bis F3
   festgelegt ist.

7. **Start 1280, erster Bildschirm: zwei gleichartige Kästen mit versetzten Kanten.** „Die nächsten Feste“ beginnt bei
   y ≈ 518 und endet bei ≈ 720. „Im Kino“ beginnt bei ≈ 584 und läuft über 800 hinaus. Beide sind gleich gebaut
   (`.bogen`, Fläche `--color-sheet` mit Linie oben, `theme.css:179`), stehen nebeneinander und sind doch 66 px
   gegeneinander verrutscht. Das wirkt zufällig, und der Bogen wertet das im ersten Bildschirm als nicht hochwertig.
   Behebung: beide Module in eine gemeinsame Rasterzeile unter Aufmacher und Foto setzen (gleiche Oberkante), oder
   „Im Kino“ in der linken Spalte unter „Die nächsten Feste“ stapeln.

### P2

8. **Bildnachweise unter jedem Listenbild zerreißen den Takt der Listen** (`inc/bausteine.php:60–79` und
   `:215–221`; Start, Rubrik, Suche, 404). Bei 1280 sind die Zeilen je nach Länge des Nachweises zwischen ca. 190 und
   345 px hoch. Unter den Schlagzeilen bleibt eine leere Fläche, und der Link „Quelle“ hängt unter einer eigenen
   Linie. Das liest sich wie ein Datenbankausdruck. Der Brief erlaubt den Nachweis „am Bild oder im Fuß“, und der Fuß
   sammelt die Nachweise bereits (`tamil_nachweise`). Behebung: In Listen keinen Nachweis zeigen oder höchstens eine
   einzeilige Kurzform; der volle Nachweis steht im Fuß.

9. **Tippflächen unter 44 px** (390/820): „Quelle“ 198×35 und 50×33 auf Start, Artikel, Kino, Events und 404; der
   Quellenlink im Artikel 235×20; „WeTransfer“ auf Kontakt 98×22; der aktive Navigationspunkt „Kino“ im Artikel 39 px
   breit. Behebung: Mindesthöhe 44 px für Textlinks in Nachweisen und Quellen (Polsterung, `min-height`), Navigation
   mit Mindestbreite.

10. **Feste Leiste unten am Handy** (`theme.css:525–527`, `ads.php:105–111`): „Anzeige | Tamil.de auf WhatsApp |
    Abonnieren | ×“ erscheint nach dem ersten Abschnitt auf jeder Seite und liegt beim Lesen über dem Text. Inhaltlich
    ist es Eigenwerbung, beschriftet ist sie als „Anzeige“. Sie erinnert an die verworfene „feste Daumenleiste“ aus
    Runde 4 und stellt die Werbung nicht unter den Inhalt. Behebung: den WhatsApp-Hinweis nur im Fluss setzen (nach
    dem Artikel, er existiert dort schon), die feste Leiste streichen oder höchstens einmal je Sitzung zeigen;
    Beschriftung „Eigenwerbung“.

11. **390: Listenzeilen mit drei Spalten sind zu eng.** Neben Datumsspalte und Vorschaubild bleiben ca. 180–200 px
    für die Schlagzeile. Sie bricht dadurch über vier bis sechs Zeilen (z. B. „Tamil-Kunstprüfung: Über 1.000 Kinder
    in Deutschland, der Schweiz, Frankreich und Italien“ auf der 404-Seite). Die Datumsangabe zerfällt in
    „So.,“/„Okt.“. Behebung: Bei ≤ 480 px das Datum in die Metazeile oder über die Schlagzeile setzen und das Bild
    darunter oder kleiner, sodass die Schlagzeile die volle Breite bekommt. „Okt.“ unter dem Monatskopf „Oktober“ ist
    ohnehin doppelt.

12. **Floor 13: Start 1280, erster Bildschirm mit ca. 110 Wörtern** (Floor: „about 80“). Den Überschuss tragen die
    Leertexte der beiden Kästen und die Zeile oben. Behebung ergibt sich aus Befund 3 (Fallback oder Einklappen).

### P3

13. **sloplint** (`theme.css`, Genre editorial): 0 FAIL, 3 WARN. Die Warnungen: Gate 25, `.fuss p` mit 36ch,
    `theme.css:553`; Gate 41, Akzentfläche ohne `--color-accent-ink`; F7, dieselbe Kastenrezeptur auf 9 Selektoren,
    `theme.css:99`. Den Verzicht auf Gate 59 im Stempel lehnt sloplint ab („reason shares no word with the page“). Die
    Render-Stufe lief nicht, weil puppeteer-core fehlt. Behebung: Warnungen beantworten, Verzicht in den Worten der
    Seite begründen, Render-Lauf nachholen.

14. **Kleinigkeiten am Inhalt:**
    - Kontakt: „• Was ist passiert? • Wo ist es passiert? …“ steht als Fließtext mit Punkten im Absatz statt als Liste
      (WP-Inhalt).
    - Fuß: „© 2026 Tamil.de (lokal)“ kommt aus dem Seitentitel der lokalen Installation; vor einer Vorführung
      korrigieren.
    - Artikel „Porattam“: Das Plakat ist als „Foto:“ ausgewiesen statt als „Grafik:“.

15. **Artikel „Porattam“, 1280: Das Plakat zeigt vier private Handynummern der Veranstalter in 1178 px Breite.** Die
    Veranstalter haben die Nummern selbst veröffentlicht, trotzdem sollte die Redaktion entscheiden, ob das Plakat so
    groß als Aufmacherbild stehen soll. Behebung: redaktionelle Freigabe oder ein Ausschnitt.

## Was trägt

- **Die Datums-Idee ist durchgehalten:** Tagesziffer am Start, Datumsspalte im Artikel, Monats- und Tagesköpfe in
  Listen, Suche und 404. Das gehört erkennbar dieser Seite und ist kein Portalbaustein.
- **Der Floor ist sauber eingehalten:** keine Dachzeilen, keine Versal-Labels, keine Kartenraster, keine
  Verlaufskacheln, kein Rot als Fläche. Rot steht nur im Logo. Zwei Familien, Gewicht 600, ruhiger Zeilenfall.
- **Der Artikel ist gut lesbar:** 18/19 px, ca. 40/60 Zeichen pro Zeile, die Metazeile als ganzer Satz („Redaktion
  Tamil.de, veröffentlicht am 18. Oktober 2026, 1 Minute Lesezeit“), die Termin-Tafel nüchtern. Teilen per WhatsApp
  ist als schlichter Link umgesetzt.

## Geprüft und nicht geprüft

Geprüft:
- Start, Artikel (Porattam), Rubrik News und Kino, Events, Kontakt, Suche (?s=diwali, ?s=kino), 404 bei 390 und 1280
  als Messung; Bilder bei 390/820/1280 aus `theme-shots/`.
- Erste Bildschirme von Start (390, 1280), Artikel (390 bis zum dritten Bildschirm, 1280), Kino 1280 und die ersten
  Bildschirme von Kino, Events, Suche und 404 bei 390 genau angesehen.
- Schriftgrößen, Kontrast, Versalien und Sperrung, Trennpunkte, feste Elemente, Tippflächen; Logo per md5;
  Beitragsdaten per REST; Herkunft der Werbe- und Kontakttexte per grep.
- sloplint statisch auf `theme.css` und per `--url` auf der Startseite.

Nicht geprüft:
- sloplint-Render-Stufe (puppeteer-core fehlt).
- 820 nur aus `bericht.json`, nicht angesehen.
- Rubrik News bei 1280 und Kontakt nur gemessen, nicht angesehen.
- Paarvergleich mit den Bildern der Vorbilder und der abgelehnten Runden: aus Zeitgründen nicht nebeneinandergelegt,
  nur gegen die Beschreibungen in `abgelehnt.md` geprüft.
- Kontrast von Platzhaltertext in Eingabefeldern und von Text über Bildern (es gibt keinen).
- Tastaturbedienung und Fokus, Zoom auf 200 %, `prefers-reduced-motion`, Verhalten ohne Skript.
- Cockpit.
- Ob „Komponist Deva ist tot“ inhaltlich stimmt.
