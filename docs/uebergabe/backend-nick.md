# Übergabe Backend an Nick: tamil.de

Stand: 22.11.2026 (Theme 3.16.1). Am 22.11. bereinigt (Ja von Luis): Abschnitte 1, 5 und 7 an die Abschnitte 0, 0a
und 6d angeglichen, neuer Abschnitt 6e, offene Fragen ergänzt. Kommen weitere Punkte von Luis, wird diese Datei
ergänzt.

**Was gilt bei Widerspruch:** der neuere Abschnitt. Für Logo, Farben, Signet, Radius und Social-Bilder sind das 0a
(20.11.), 0 (19.11.) und 6d (21.11.). Wo ältere Abschnitte noch „klar2-Look“ sagen, ist damit nur noch Schrift und
Aufbau gemeint, nicht Farbe, Logo oder Radius.

**Website heute:** Testsystem `https://tamil-web.167.233.76.202.sslip.io`, gebaut aus `claude/radar-multiagent`.
- Design klar2 mit rotem Rubrikband und Bewegung D; seit 19. bis 21.11. mit Markenfarben Titan und Impact Red, neuem
  Logo, Signet Tamil Dots und Radius 10 px / 6 px (Abschnitte 0, 0a, 6d).
- Startseite: drei Proben zum Vergleichen hinter einem Schalter, dazu „Tamil in meiner Stadt“ (Abschnitt 6e). Welche
  Probe gilt, entscheidet Luis.
- Bilderpflicht mit Bildkette (`inc/bildkette.php`, `inc/filmbilder.php`) und Rubrik-Pool.
- Eigenanzeigen als Bildbanner.
- Module auf dem Testsystem an: Einreichungen, Verzeichnis, Werbung.
- Regeln in `DESIGN.md` und `docs/entscheidungen.md` (16. bis 22.11.).
- Die Live-Domain tamil.de ist nicht umgestellt (Tor B3 offen).
- Auf `main` kommen von der Website-Seite nur Website-Dateien.

**Für wen:** Nick und seine Claude-Sitzung. Die Datei ist so geschrieben, dass sie sich direkt als Auftrag verwenden
lässt. Erst `CLAUDE.md`, `docs/architektur.md`, `docs/betrieb.md` und `docs/entscheidungen.md` im Repo
`HKGrowthOperator/Tamil` lesen.

**Aufteilung seit 17.11. (Luis):**
- **Luis und dessen Sitzung:** Website, Design und Fulfillment. Das umfasst das Theme `wordpress/themes/tamil`, das
  Plugin `tamil-site` (Frontend-Teile) und das Testsystem der Website.
- **Nick:** das Backend. Das umfasst den News-Radar (`news_radar/`, `sources.toml`), das Redaktions-Cockpit
  (`news_radar/web/`), Agenten, Publisher, Bilderzeugung, Social-Automatik und das Plugin `tamil-radar` (REST zum
  WordPress).

## 0a. Neu seit 20.11.: neues Logo (verbindlich)

**Luis, 20.11.:** Das neue Logo wird **genau so** übernommen, auch die Schreibweise der Zeilen „portal • lifestyle •
entertainment“ und „& KOMMUNITYPLATTFORM DER COMMUNITY“. Kein Neuzeichnen, kein Vektor-Nachbau. Das hebt „Das Logo
bleibt unverändert“ unten für dieses Logo auf (`docs/entscheidungen.md`, 20.11.).

- **Dateien:** `design/inhalte/logo.png` (1920 × 695, freigestellt, durchsichtiger Grund, ohne Rand) für Bildkarte und
  Social-Bilder; Quelle `design/inhalte/logo-2026-11.webp`, Freistellung `design/inhalte/logo_freistellen.py`. Im Theme
  `assets/img/logo.webp`, `logo-2x.webp` und `logo.png` (398 × 144).
- **Bitte umstellen:** Cockpit (Kopf, Vorschau), die Bildkarte des Radars und die Social-Bilder nutzen ab jetzt dieses
  Logo, nicht mehr das alte `logo.png` (300 × 121). Die Social-Vorlage `design/social/vorlagen/karte.html` und alle
  Muster in `design/social/muster/` zeigen es schon. Auf Foto oder Titan steht es weiter auf weißer Platte (eine weiße
  Fassung gibt es nicht).
- **Website:** Seit Theme 3.6.0 zusätzlich „Text auf Bild“ auf der Startseite und der Punktbogen unten rechts in jedem
  Beitragsbild (DESIGN.md). Für das Backend ändert sich dadurch nichts; Beitragsbilder sollten wie bisher Fotos ohne
  eingebrannten Text sein, damit Titel und Bogen darauf gut stehen.
- **Unverändert:** Favicon und App-Icon „t.“ (offene Frage an Luis).

## 0. Neu seit 19.11.: Markenfarben, Signet und Social-Kartensystem (verbindlich)

**Branding:** Grundlage ist `docs/branding/2026-11-19-branding-master-v1.1.md`. Die Freigaben stehen in
`docs/abnahme/2026-11-19-signature.md`.

**Farben:**

| Rolle | Farbe | Anteil (Richtwert) |
|---|---|---|
| Grund | Weiß #FFFFFF | 50 % |
| dominant | Titan Red #660000 | 35 % |
| Akzent | Impact Red #B30000 | 10 % |
| Schrift | Schwarz #000000 | 5 % |

Tokens: `--tamil-color-background`, `--tamil-color-primary`, `--tamil-color-accent`, `--tamil-color-text`, umgesetzt in
`wordpress/themes/tamil` 3.4.0 und `design/tokens.css`. Keine weiteren Markenfarben.

**Signet Tamil Dots 04A:**
- Die Form ist freigegeben: `design/signature/master.svg`. Es gibt nur diese zwei Rottöne, jeder Punkt ist eine Ellipse.
- Generator: `design/signature/tamil_dots.py`.
- Weitere Dateien: Small und Mini als Entwurf, Spatial nur für Sonderstellen, Animation `animiert.svg`.
- Regeln stehen in `design/signature/README.md`.
- Es ist **kein Logo**. Das Signet steht nie am, im oder hinter dem Logo (Logo seit 20.11. neu, Abschnitt 0a).

**Social-Kartensystem:** Die Richtung ist freigegeben, pixelgenaue Exportstandards noch nicht.
- Die Spezifikation in `design/social/README.md` ist die Vorgabe für das automatische Posten nach Instagram (Feed,
  Karussell, Story), Facebook (Link-Post, Story) und WhatsApp. Sie enthält Datenfelder, Maße, sichere Zonen,
  Schriftgrößen, Farbgewichtung, Regeln für das Signet, Bildnachweis und Einzelbild oder Karussell nach Länge.
- Vorlage: `design/social/vorlagen/karte.html?format=…`, Muster in `design/social/muster/`.
- **Aufbau:** Das Logo (seit 20.11. das neue, Abschnitt 0a) steht auf weißer Platte oben links, die Überschrift auf Titan. Der Punktbogen liegt
  auf Titan, nie auf Foto, Überschrift oder Gesichtern. Jede Karte trägt den Bildnachweis.
- Das ersetzt die früheren Vorgaben zum Social-Bild in Abschnitt 1 und 5 (klar2-Look, Radius 0, „tamil.de“ in weißer
  Schrift). Beide Abschnitte sind seit 22.11. angepasst.
- **Noch offen:**
  - eine weiße Logofassung (für „tamil.de weiß oben links“, liefert KBS);
  - eine neue Fassung des Regelwerks F4 (heute gehen Storys und Karussells nie automatisch hinaus), mit Freigabe durch
    KBS.

**Bildkarte, Social-Bilder, Cockpit, Vorschau und `tamil-radar/admin.css`** bitte auf diese Farben und dieses Signet
umstellen, nicht auf den älteren klar2-Look.

---

## 1. Automatisches Posten nach Instagram, im Stil von Bild.de

**Wunsch von Luis (17.11., sinngemäß):** Jeder Beitrag der Website geht automatisch als Post nach Instagram, so wie
Bild.de seine Instagram-Posts aus der Website baut.
- Ein großes Bild.
- Oben links die Marke. Am 17.11. hieß das „tamil.de in weißer Schrift“; **seit 19./20.11. gilt:** das neue Logo auf
  weißer Platte oben links (Abschnitt 0 und 0a). Eine weiße Logofassung gibt es noch nicht (offene Frage an KBS).
- Darunter kurz die Überschrift, auf Titan.
- Je nach Länge des Beitrags ein Einzelbild oder ein Karussell (Slider) mit mehreren Folien.

**Design (Stand 22.11., ersetzt „im Look klar2“):** Es gilt das Social-Kartensystem aus Abschnitt 0.
- Vorgabe: `design/social/README.md` (Maße, sichere Zonen, Schriftgrößen, Signet, Bildnachweis, Einzelbild oder
  Karussell). Zuständig für die Vorgabe: Luis.
- Vorlage `design/social/vorlagen/karte.html?format=…`, Muster in `design/social/muster/`, Schriften in
  `design/social/schriften/`.
- Formate: Feed 1080×1350, Karussell-Folien, Story 1080×1920.
- Die Bilderzeugung baut die Vorlage nach. Abweichungen nur mit Luis. Zuständig: Nick.
- Die Richtung ist freigegeben, pixelgenaue Exportstandards noch nicht (Abschnitt 0).
- Storys und Karussells gehen nach dem heutigen Regelwerk nie automatisch hinaus; dafür braucht es eine neue Fassung
  mit Freigabe durch KBS (Abschnitt 0, offene Fragen).

**Umsetzung:**
- Code-Stellen:
  - Bilderzeugung: `news_radar/social/bild.py` (1080×1350, noch im alten Sand-Look; der Docstring sagt „das neue
    Design folgt später“; am 22.11. im Code so vorgefunden). Umstellung: Abschnitt 6d, TML-W10.
  - Social-Schnittstellen: `news_radar/social/`.
- Ablauf: Auslöser ist die Veröffentlichung eines Beitrags.
  1. Bild bzw. Folien erzeugen. Grundlage sind das Beitragsbild mit Bildnachweis und die Überschrift. Für das
     Karussell zusätzlich die Kernaussagen aus dem Text.
  2. Bildunterschrift mit Link in Bio bzw. Link-Sticker.
  3. Veröffentlichen über die **offizielle Meta Graph API** (Instagram Content Publishing, Karussell-Container).
- **Voraussetzungen**, alle in `docs/vertrag/zuarbeit-kbs.md` und `festlegung-*.md`:
  - Instagram-Professional-Konto von KBS, verknüpfte Facebook-Seite, Business-Portfolio, Meta-App mit KBS als Admin.
  - Die **einmalige Freigabe des Regelwerks durch KBS** (Vertrag B2).
  - Bis dahin Trockenmodus.
- **Pflicht:**
  - Stopp-Schalter vor jeder automatischen Ausführung, Protokoll je Post (`.claude/rules/vertrag.md`).
  - Nur Bilder mit vollständigem Lizenz-Datensatz (`docs/spezifikation/bilder-und-lizenzen.md`).
  - Kein Scraping von Instagram, Facebook, TikTok oder X.
- **Fertig, wenn:**
  - Im Trockenmodus entsteht für einen Beitrag ein Post-Paket (Bilder und Text) und erscheint im Cockpit.
  - Mit Konten von KBS und freigegebener Regel wird ein echter Testpost veröffentlicht und protokolliert.
  - Tests sind grün, `python -m news_radar abnahme` läuft durch.

## 2. WhatsApp-Kanal

- **Wunsch:** auch in WhatsApp alles posten.
- **Lage:** Meta bietet für WhatsApp-Kanäle **keine Schnittstelle zum Veröffentlichen** (Entscheidung vom 13.11.,
  `docs/entscheidungen.md`).
- **Umsetzung:** Der Radar baut je Beitrag ein fertiges Paket. Es besteht aus dem Bild im selben Stil wie für
  Instagram (Kartensystem, Abschnitt 0 und 1) und dem Text mit Link zum Kopieren. Das Paket erscheint im Cockpit mit
  Knopf „Kopieren“ bzw. „Bild sichern“. Gepostet wird von Hand.
- **Fertig, wenn:** Für jeden veröffentlichten Beitrag liegt ein WhatsApp-Paket im Cockpit, und den Link zum Kanal
  nennt KBS.

## 3. Instagram-Inhalte von tamil.de auf die Website

- **Wunsch:** Instagram-Videos und Posts des Kontos tamil.de sollen auf der Website erscheinen.
- **Frontend (Luis):**
  - Ein Block „Auf Instagram“ mit den offiziellen Einbettungen von Instagram.
  - Lädt erst nach Zustimmung im Cookie-Hinweis.
  - Ausgewählt im Cockpit oder als Liste von Post-Links.
- **Backend (Nick), nur falls automatisch:**
  - Die neuesten Posts des eigenen Kontos über die Graph API lesen (Business-Konto von KBS).
  - Als Liste von Links und Metadaten an WordPress geben, z. B. über REST des Plugins `tamil-radar`.
  - Kein Scraping.
- **Offen:** Name des Kontos und Auswahlregel (die neuesten, oder kuratiert). Klären mit Luis.

## 4. AJ Game Station

- **Lage:** Laut Luis gehört das Konto AJ Game Station KBS, „ein riesiger Account“.
- **Frontend:** Bildbanner als Eigenanzeige auf der Website. Die Unterlagen kommen von KBS.
- **Backend, falls gewünscht:** Gegenseitige Hinweise in den Social-Posts, z. B. eine Folie im Karussell oder in der
  Story. Erst nach Absprache mit Luis; nichts automatisch auf fremden Konten posten.

## 5. Bildkarte, Social-Bilder und Titelkarten (Gestaltung nach Abschnitt 0, 0a und 6d)

**Begriff:** „Bildkarte“ meint in dieser Datei die vom Radar erzeugte Grafik ohne Foto (`branded_card`, auf der Website
„Titelkarte“). In `DESIGN.md` heißt „Bildkarte“ dagegen der Anreißer der Website mit Titel im Foto. Das sind zwei
verschiedene Dinge.

**Seit 17.11. gilt auf der Website die Bilder-Pflicht:** Jeder Teaser, jede Kachel und jede Anzeige hat ein echtes
Foto.

**Was das Theme macht:**
- Es zeigt die **Titelkarten nicht mehr**. Das sind Beiträge mit `bild_origin=karte` bzw. Bildnachweis
  „Grafik: Tamil.de“, 17 Beiträge vom 11. und 12.11.
- Ersatz in dieser Reihenfolge:
  1. Bild aus dem Text
  2. Rubrik-Pool, mit „Symbolbild“ und Nachweis

**Bitte im Backend:**
- **Neue Beiträge** bekommen nach Möglichkeit ein echtes Foto als Beitragsbild. Bildreihenfolge laut Blueprint:
  Archiv → Quelle → Stock → Pool. Dazu den vollständigen Lizenz-Datensatz mit Urheber, Lizenz, Link zur Lizenz, Link
  zur Dateiseite und „zugeschnitten“. Die Titelkarte ist nur der letzte Ausweg.
- **Social-Bilder** (`news_radar/social/bild.py`): auf das Social-Kartensystem umstellen (Abschnitt 0, 1 und 6d).
  Zuständig: Nick.
- **Bildkarte** (`news_radar/images.py`, `branded_card`, 1200×675). Ihre Rolle heute, im Code am 22.11. so vorgefunden:
  - Sie ist die letzte Stufe „karte“ der Bildreihenfolge (`BILD_REIHENFOLGE` in `news_radar/config.py`) und wird in
    `news_radar/bilder.py`, `news_radar/agents/media.py` und im Cockpit (`news_radar/web/views.py`) erzeugt.
  - Die Website zeigt sie nirgends als Beitragsbild (`inc/bildkette.php`: `bild_origin=karte` zählt nie als eigenes
    Foto). Sie ist dort nur noch ein Merkmal „kein Foto vorhanden“.
  - Sichtbar bleibt sie im Cockpit und überall, wo das Beitragsbild außerhalb des Themes verwendet wird. Ob dazu die
    Vorschau in sozialen Netzen (`og:image`) gehört: nicht nachgeprüft.
  - Für Social-Posts ohne Foto gibt es eine eigene Karte in `news_radar/social/bild.py` (`karte`), nicht
    `branded_card`.
- **Gestaltung, falls die Bildkarte bleibt:** Schrift Libre Franklin und der Verlauf unten für Text im Bild gelten
  weiter. Ersetzt sind: die Farben (Weiß, Titan #660000, Impact Red #B30000, Schwarz, Abschnitt 0), das Logo (0a) und
  der Radius (nicht mehr 0, sondern 10 px und 6 px, Abschnitt 6d). Zuständig: Nick, Vorgabe von Luis.
- **Offen:** ob die Bildkarte überhaupt weiter erzeugt und umgestaltet werden soll (offene Fragen am Ende).

## 6. Daten für „Diese Woche“ und den Kalender

Das Theme liest (seit 17.11.):
- Kino nur mit Spielzeiten ab heute (`kino_fakten`)
- Termine mit `event_datum` ab heute

Dazu kommen Filter nach Land (DE/AT/CH) und Stadt sowie die Angaben Eintritt, Ende und Veranstalter.

**Bitte im Radar:**
- Diese Felder beim Schreiben eines Kino- oder Termin-Beitrags immer und einheitlich füllen: Datum im ISO-Format,
  Stadt, Land, Ort, Veranstalter, Eintritt, Ende.
- Die genauen Meta-Namen stehen im Theme in `inc/queries.php` und `page-events.php` und in `news_radar/render.py`.
- Fehlt ein Feld, erscheint der Beitrag nicht in „Diese Woche“.

**Befunde der unabhängigen Prüfung vom 17.11.:**
- **Land leer:** Bei allen Terminen ist das Land leer (`data-land=""` im Kalender). Der Länderfilter DE/AT/CH bleibt
  deshalb leer.
- **Fehlende Angaben:** Uhrzeit, Veranstalter und Eintritt fehlen meist.
- **Alter Termin oben:** „Jailer 2 am 15. November“ stand am 17.11. noch oben in „Neu“ und „Diese Woche“. Das Datum der
  Vorstellung bzw. des Termins muss sauber im Meta stehen, damit das Theme Vergangenes aussortiert.

## 6a. Slugs der Radar-Beiträge

- **Befund:** Die Slugs (URLs) neuer Beiträge werden mitten im Wort abgeschnitten, z. B. `…-in-ber/`, `…-grugaha/`,
  `…-lichterf/`, `…-im-k/`. Nach dem Livegang bleiben sie dauerhaft. Die Stelle im Code steht in Abschnitt 6e.
- **Bitte:** an Wortgrenzen kürzen (z. B. höchstens 60 bis 70 Zeichen bis zum letzten ganzen Wort). Bestehende Slugs nur
  mit 301-Weiterleitung ändern.

## 6b. Bildnachweise aus dem Radar

Für vollständige CC-Nachweise braucht die Website je Bild, als Meta am Anhang bzw. Beitrag:
- Urheber
- Lizenzname und Link zur Lizenz
- Link zur Dateiseite (bei Commons die File-Seite)
- **Originalbreite und -höhe:** Daran könnte das Theme „zugeschnitten“ erkennen. Heute liest das Theme kein solches
  Feld und der Radar schreibt keines (Abschnitt 6e).

Der Radar sollte diese Felder beim Import immer mitschreiben. Das Theme zeigt sie verlinkt an (seit 17.11.).

**Namen der Felder**, die das Theme liest (`tamil_nachweis_bauen()`):
- `bild_credit`
- `bild_quelle_url` (Dateiseite)
- `bild_lizenz` (Kürzel)
- `bild_lizenz_url`
- `bild_origin` (`karte` = Titelkarte)
- `bild_symbolbild` (1 = Symbolbild)

**Bitte für den Altbestand nachtragen:** `bild_quelle_url` und `bild_lizenz_url` für die etwa 40 Commons-Beiträge auf
dem Testsystem.
- Ohne diese Felder verlinkt der Nachweis nur die Commons-Suche nach dem Urheber.
- 20 Dateiseiten stehen schon in `design/inhalte/rueckblick/rueckblick.json`. Das Präfix `sNN` im Dateinamen des
  Uploads ist die Story-ID.

**Weitere Einzelpunkte:**
- **OM:** Es gibt nur einen Beitrag, und der hat eine Titelkarte. Ein echtes Film- oder Plakatfoto mit Lizenz würde das
  Symbolbild ersetzen.
- **Seite „TAMIL TV CHANNEL“:** in den Daten auf „Tamil TV“ umbenennen. Das Theme gleicht den Titel bereits an.

## 6c. Datenbefunde aus dem Feinschliff (20.11.)

Ein frischer Prüfdurchgang hat Fehler in den Radar-Inhalten gefunden. Das Theme kann sie nicht sauber beheben,
Einzelheiten stehen in `docs/abnahme/2026-11-20-feinschliff.md`.

- **Falsches Bild bei „Jailer 2“ (P0):**
  - Ein Jailer-2-Beitrag hat das Firmenlogo „KINOPOLIS – Mehr Kino geht nicht“ als Bild, mit dem Nachweis
    „Filmplakat: via Kinopolis“.
  - Über die Bildkette (Schritt „film“) erscheint es auch beim Beitrag über das Kino Claudia in Kloten (Beitrag 2620).
  - Bitte: echtes Plakat mit korrektem Nachweis oder kein Bild. Logos von Kinoketten nie als Beitragsbild übernehmen.
- **Quelle doppelt:** Radar-Beiträge schreiben zwei Links gleichen Namens („Eventfrog CH, Eventfrog CH“) mit
  verschiedenen Zielen. Das Theme hängt jetzt „(2)“ an. Besser ist, die Quelle beim Schreiben eindeutig zu benennen.
- **Meta-Beschreibungen:** Verzeichnis, Werben und Impressum haben noch keine eigene Beschreibung, sondern die
  allgemeine. Das ist Redaktion oder Einstellung.

**Nachtrag 21.11. (Nachtschicht, `docs/abnahme/2026-11-21-nacht.md`):**

- **Kino, Karlsruhe ohne Zahl:** Für „Filmpalast am ZKM“ liefert der Radar nur `von`, keine `termine`. Die
  Stadtliste zeigt deshalb keine Zahl der Vorstellungen.
- **Kinonamen mit Stadt:** Namen wie „CineStar Kristall-Palast - Bremen“ enthalten die Stadt mit Bindestrich-Minus.
  Das Theme normalisiert das nicht, weil es nicht eindeutig ist. Bitte Name und Stadt getrennt liefern.
- **Neu im Theme, zur Kenntnis:**
  - Wow-Aufmacher auf der Startseite (3.10.0). Er greift nur, wenn der Aufmacher-Beitrag ein eigenes Foto ab 960 px
    Breite hat. Titelkarten, Poolbilder und geliehene Filmbilder bekommen den normalen Aufmacher. **Seit 3.13.1 ist
    er standardmäßig aus** (Luis, 21.11.); der Aufmacher ist die normale Bildkarte.
  - Abgerundete Ecken und ein stehendes Rubrikband mit Logo. Für Cockpit-Vorschau und Bildkarte gilt das nicht
    automatisch.
- **Tägliche Bildvorschläge:** Zweimal täglich entsteht eine Liste von Beiträgen ohne geeignetes Bild mit je einem
  Symbolbild-Vorschlag (Nachweis „Symbolbild, KI-generiert (Tamil.de)“). Eingesetzt wird über Radar oder WordPress,
  das entscheidet Luis.

## 6d. Nachtrag 21.11.: Masterplan von Luis (TML-W09, TML-W10)

Nur Hinweise, auf der Website-Seite wurde dafür kein Backend-Code geändert.

- **Social-Bildgenerator an `design/social/` anbinden (TML-W10):** Laut Masterplan nutzt
  `news_radar/social/bild.py` noch das alte Sand-Design. Bitte auf das freigegebene Social-Kartensystem umstellen:
  Vorlage `design/social/vorlagen/karte.html`, Muster in `design/social/muster/`, Schriften in
  `design/social/schriften/`, Regeln in `design/social/README.md` (siehe auch Abschnitt 0 und 0a). Zu Abschnitt 5:
  Der Radius ist seit Theme 3.9.0 nicht mehr 0, sondern 10 px (`--radius`) und 6 px (`--radius-klein`); seit 3.15.0
  steht das auch in `design/tokens.css`.
- **Event- und Kinodaten mit Gültigkeitszeiten (TML-W09):** Die Website zeigt seit Theme 3.15.0 in „Diese Woche“ nur
  noch Filme und Kino-Beiträge mit einem Spieltag ab heute und lässt ein Cover nach Ablauf fallen. Dafür braucht jeder
  Kino- und Termin-Beitrag verlässliche Zeiten: bei Kino je Kino die Spieltage (`termine`) oder `von`/`bis` in
  `kino_fakten`, bei Terminen Beginn und Ende (`event_datum`, Ende). Fehlen sie, kann das Theme nur schätzen (Kinowoche
  plus sechs Tage) oder zeigt den Beitrag dort nicht. Beiträge über einen Film findet das Theme über den Filmtitel:
  derselbe Titel wie im Feld `film` der Kinoliste, im Beitragstitel in Anführungszeichen („…“).

## 6e. Neu seit 22.11.: was die Website vom Backend braucht (Startseiten-Proben, „Tamil in meiner Stadt“)

Die Proben (Theme 3.16.0 und 3.16.1) zeigen Kino, Termine und Geschichten je Stadt. Dabei sind fünf Lücken in den
Daten sichtbar geworden. Zuständig für alle fünf: Nick, soweit nicht anders vermerkt. Hinter jedem Punkt steht, was am
22.11. im Code nachgelesen wurde.

- **(a) Eigene Felder für Stadt und Land an Beiträgen und Terminen.**
  - Im Code bestätigt: Der Radar schickt nur `ort` (ein Freitext) und `event_ort` (`META_FIELDS` in
    `news_radar/publisher.py`). Einen Meta-Schlüssel für die Stadt gibt es nicht.
  - Im Code bestätigt: `event_land` geht nur bei Terminen aus einer Einsendung mit (`TERMIN_FAKTEN`, gesetzt in
    `news_radar/eingang.py`). Bei Terminen aus dem Scan wird es nirgends gesetzt.
  - Im Code bestätigt: Das Theme liest die Städte deshalb aus dem Freitext heraus (`tamil_stadt_namen()` in
    `inc/proben.php`) und aus `kino_fakten`. Nur dort stehen Stadt und Land je Kino getrennt.
  - Laut Prüfung vom 17. und 22.11., nicht nachgeprüft: `ort` hat viele Schreibweisen, `event_land` ist bei den
    Terminen auf dem Testsystem leer.
  - Bitte: je Beitrag und Termin `stadt` und `land` (DE/AT/CH) als eigene Felder schreiben. Namen der Felder mit Luis
    abstimmen (offene Frage).
- **(b) Gültigkeit von Kino-Terminen je Kino.**
  - Im Code bestätigt: Das Theme zählt je Kino nur Spieltage ab heute (`termine`), sonst das Ende (`bis`); ein Kino
    ohne beides gilt als laufend, solange die Liste gilt (`tamil_stadt_kino_laeuft()` in `inc/proben.php`). Weichen die
    Zahlen ab, steht „ab heute noch N von M Kinos“ (`docs/entscheidungen.md`, 22.11.).
  - Laut Prüfung vom 22.11., nicht nachgeprüft: Im Test hatte ein Film 13 Kinos, davon 12 mit einer einzigen
    Vorstellung an einem Tag.
  - Bitte: je Kino verlässlich `termine` oder `von`/`bis` liefern (siehe auch 6c, Karlsruhe, und 6d, TML-W09).
- **(c) Slugs werden mitten im Wort gekürzt.**
  - Im Code bestätigt: `slugify()` in `news_radar/wordpress.py` schneidet mit `text[:max_len]` (Standard 70 Zeichen)
    und entfernt danach nur Bindestriche am Ende.
  - Bitte: vor dem Livegang an der Wortgrenze kürzen. Bestehende Slugs nur mit 301-Weiterleitung ändern (Abschnitt 6a).
- **(d) Feld für einen redaktionellen Satz „Warum das wichtig ist“ (Frage an Luis, noch nicht entschieden).**
  - Im Code bestätigt: Der Radar schreibt `standfirst` nicht (er liest es nur, `news_radar/social/quelle.py`). Das
    Feld ist im Plugin `tamil-radar` angemeldet; das Theme nimmt ersatzweise den Textauszug (`tamil_standfirst()`).
    Ein eigenes Feld für den Kontextsatz gibt es nicht; die Proben zeigen deshalb kein solches Etikett.
  - Laut Prüfung vom 22.11., nicht nachgeprüft: `standfirst` ist bei allen Beiträgen leer.
  - Erst nach dem Ja von Luis bauen. Zuständig für die Entscheidung: Luis.
- **(e) Originalbreite und -höhe der Bilder mitschreiben.**
  - Im Code bestätigt: Der Radar übergibt je Bild nur Datei, Dateiname, Alt-Text und Nachweis (`bild_payload()` in
    `news_radar/publisher.py`), dazu Lizenz-Kürzel und zwei Adressen. Maße des Originals sind nicht dabei, und das
    Theme liest kein solches Feld.
  - Bitte: Breite und Höhe des Originals als Meta mitschreiben (Abschnitt 6b). Feldnamen mit Luis abstimmen; das
    Theme liest sie danach. Zuständig für das Lesen im Theme: Luis' Sitzung.

## 7. Cockpit im klar2-Look

**Ursprünglich geplant:** Website und Cockpit bekommen dasselbe Design (Entscheidung vom 16.11.). Seit 17.11. liegt das
Cockpit bei Nick.

**Seit 19. bis 21.11.:** Farben und Signet nach Abschnitt 0, Logo nach 0a, Radius 10 px und 6 px nach 6d. „klar2“ meint
hier nur noch Schrift und Aufbau.

**Was gehört dazu:**
- `news_radar/web/static/app.css` (noch Oktober-Look: Sand, Catamaran/Literata), die Templates, Schriften, das Manifest
  und `theme-color` in `views.py` und `base.html`
- Die **Artikelvorschau `/vorschau/<id>`** muss wie der Artikel im Theme 3.x aussehen.
- `wordpress/plugins/tamil-radar/assets/admin.css` (noch die alten Farben `#0e1226`/`#c8102e`)

**Hinweis zu Bewegung:** Im Cockpit nur ruhig, kein Einblenden beim Scrollen.

**Hilfen:** `.claude/agents/cockpit-bauer.md`, Skill `tamil-cockpit`, `tests/test_web*.py`, `tools/shots.mjs --login`.

## 8. Zusammenarbeit und Betrieb (wichtig)

- **Beide Coolify-Apps bauen aus demselben Branch `claude/radar-multiagent`:** der Radar mit dem Cockpit und die
  Website `tamil-web`. Jeder Push dorthin baut beide neu.
  - Vor dem Push `git fetch` und die Änderungen der anderen Seite normal mergen.
  - Nie force, nie `--no-verify`.
  - Bereiche nicht überschneiden. Nick ändert nicht `wordpress/themes/tamil` und nicht die Frontend-Teile von
    `tamil-site`; Luis' Sitzung ändert nicht `news_radar/` und nicht `tamil-radar`.
- **Geheimnisse** gehören nur in Coolify-Variablen bzw. eine lokale `.env`, nie in Chat, Docs oder Commits.
- **Fertig heißt:**
  - `python -m pytest -q` grün
  - `python -m news_radar abnahme` mit allen Szenarien
  - bei Oberflächen `tools/shots.mjs` bei 390/820/1280
- **Vertrag:** Neue automatische Funktionen bleiben im Echtbetrieb aus, bis Auftragsverarbeitung und Rechtstexte da
  sind (`.claude/rules/vertrag.md`).

## Offene Fragen an Luis bzw. KBS

- Instagram: Name des tamil.de-Kontos, Business-Konto, Meta-App und Freigabe des Regelwerks.
- WhatsApp: Link zum Kanal.
- AJ Game Station: Unterlagen und was beworben wird.
- Instagram-Inhalte auf der Website: die neuesten oder kuratiert.

Ergänzt am 22.11. (stand in den Abschnitten, fehlte hier):

- **Weiße Logofassung** (Abschnitt 0 und 0a): Gibt es sie, und wer liefert sie? Bis dahin steht das Logo auf weißer
  Platte. An KBS, über Luis.
- **Neue Fassung des Social-Regelwerks** für Karussell und Story (Abschnitt 0 und 1): Heute gehen beide nie automatisch
  hinaus. Braucht eine neue Fassung und die Freigabe durch KBS.
- **Exportstandards der Social-Karten** (Abschnitt 0): pixelgenaue Vorgaben sind noch nicht freigegeben. An Luis.
- **Favicon und App-Icon „t.“** (Abschnitt 0a): bleibt es, oder folgt es dem neuen Logo? An Luis.
- **Bildkarte `branded_card`** (Abschnitt 5): Soll der Radar sie weiter als letzten Ausweg erzeugen und im neuen
  Aussehen bekommen, oder bleibt ein Beitrag ohne Foto ohne Bild, weil die Website ohnehin ein Poolbild zeigt? In
  `DESIGN.md` und `docs/entscheidungen.md` steht dazu keine Entscheidung. An Luis.
- **Stadt und Land als eigene Felder** (Abschnitt 6e a): Ja oder Nein, und unter welchen Namen? An Luis (Frage 4 der
  Bauvorgabe zu den Startseiten-Proben).
- **Feld „Warum das wichtig ist“** (Abschnitt 6e d): eigenes Feld für den Kontextsatz, und wer schreibt ihn? An Luis
  (Frage 1 der Bauvorgabe).
- **Tägliche Bildvorschläge** (Abschnitt 6c): Einsetzen über den Radar oder über WordPress? An Luis.
