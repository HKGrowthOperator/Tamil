# Übergabe Backend an Nick: tamil.de

Stand: 17.11.2026, nach Abschluss der Frontend-Runde (Theme 3.3.1 auf dem Testsystem). Kommen weitere Punkte von Luis,
wird diese Datei ergänzt.

**Website heute:** Testsystem `https://tamil-web.167.233.76.202.sslip.io`, gebaut aus `claude/radar-multiagent`.
- Design klar2 mit rotem Rubrikband und Bewegung D.
- Bilderpflicht mit Bildkette (`inc/bildkette.php`, `inc/filmbilder.php`) und Rubrik-Pool.
- Eigenanzeigen als Bildbanner.
- Module auf dem Testsystem an: Einreichungen, Verzeichnis, Werbung.
- Regeln in `DESIGN.md` und `docs/entscheidungen.md` (16. und 17.11.).
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

---

## 1. Automatisches Posten nach Instagram, im Stil von Bild.de

**Wunsch von Luis (17.11., sinngemäß):** Jeder Beitrag der Website geht automatisch als Post nach Instagram, so wie
Bild.de seine Instagram-Posts aus der Website baut.
- Ein großes Bild.
- Oben links „tamil.de“ in weißer Schrift.
- Darunter kurz die Überschrift.
- Je nach Länge des Beitrags ein Einzelbild oder ein Karussell (Slider) mit mehreren Folien.

**Design:** Die Vorlagen kommen aus dem Frontend, im Look klar2:
- Formate: Feed 1080×1350, Karussell-Folien, Story 1080×1920.
- Liegen dann in `design/social/`.
- Die Bilderzeugung baut sie nach. Abweichungen nur mit Luis.

**Umsetzung:**
- Code-Stellen:
  - Bilderzeugung: `news_radar/social/bild.py` (1080×1350, noch im alten Sand-Look; der Docstring sagt „das neue
    Design folgt später“).
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
- **Umsetzung:** Der Radar baut je Beitrag ein fertiges Paket. Es besteht aus dem Bild im selben Bild.de-Stil und dem
  Text mit Link zum Kopieren. Das Paket erscheint im Cockpit mit Knopf „Kopieren“ bzw. „Bild sichern“. Gepostet wird
  von Hand.
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

## 5. Bildkarte, Social-Bilder und Titelkarten im klar2-Look

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
- **Bildkarte** (`news_radar/images.py`, `branded_card`, 1200×675) und **Social-Bilder**
  (`news_radar/social/bild.py`) auf klar2 umstellen. Grundlage sind die Tokens in `design/tokens.css` und `DESIGN.md`:
  - Libre Franklin
  - oklch-Farben
  - Rot nur als Akzent
  - Radius 0
  - Verlauf unten für Text im Bild

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
  `…-lichterf/`, `…-im-k/`. Nach dem Livegang bleiben sie dauerhaft.
- **Bitte:** an Wortgrenzen kürzen (z. B. höchstens 60 bis 70 Zeichen bis zum letzten ganzen Wort). Bestehende Slugs nur
  mit 301-Weiterleitung ändern.

## 6b. Bildnachweise aus dem Radar

Für vollständige CC-Nachweise braucht die Website je Bild, als Meta am Anhang bzw. Beitrag:
- Urheber
- Lizenzname und Link zur Lizenz
- Link zur Dateiseite (bei Commons die File-Seite)
- **Originalbreite und -höhe:** Daran erkennt das Theme „zugeschnitten“.

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

## 7. Cockpit im klar2-Look

**Ursprünglich geplant:** Website und Cockpit bekommen dasselbe Design (Entscheidung vom 16.11.). Seit 17.11. liegt das
Cockpit bei Nick.

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
