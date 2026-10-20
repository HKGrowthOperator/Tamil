# Tamil.de – WordPress-Pakete

Drei Pakete, sauber getrennt nach den zwei Lieferungen:

| Paket | Ordner | Teil | Aufgabe |
|---|---|---|---|
| Theme **Tamil.de** | `themes/tamil` | A – Website | Gestaltung und Vorlagen: Startseite, Rubriken, Artikel, Termine, Kontakt, Production, TV, Suche, 404 |
| Plugin **Tamil.de Website** | `plugins/tamil-site` | A – Website | Werbeplätze mit Eigenanzeigen, 301-Weiterleitungen, Termin-Felder mit Eingabemaske, Abfragen fürs Theme |
| Plugin **Tamil.de News-Radar** | `plugins/tamil-radar` | B – News-Radar | Anbindung des externen Radars: REST `tamil-radar/v1`, Rolle „Radar“, Cockpit im Backend, Dashboard-Widget |

Website und Theme laufen ohne den Radar. Der Radar bleibt ein eigenes Werkzeug (Freigabe-App, eigener Server) und
schreibt nur über die REST-Schnittstelle in WordPress. Wird `tamil-radar` deaktiviert, bleiben alle Beiträge, Bilder
und Felder erhalten.

## Installation auf tamil.de

1. **Pakete bauen:** `bash wordpress/dev/package.sh` → `wordpress/dist/tamil.zip`, `tamil-site.zip`,
   `tamil-radar.zip` (+ `SHA256SUMS`).
2. **Hochladen:** Design → Themes → Hochladen (`tamil.zip`); Plugins → Installieren → Hochladen (`tamil-site.zip`,
   dann `tamil-radar.zip`). Beide Plugins aktivieren, danach das Theme.
3. **Kategorien** (Slug genau so): `news`, `entertainment`, `events`, `community`, `kueche`, `kino`, `sport`,
   `kultur`. Das tamilische Wort je Rubrik lässt sich unter Beiträge → Kategorien ändern (Feld „Tamilisches Wort“).
4. **Seiten** (Slug = Vorlage, wird automatisch gewählt): `events` (Veranstaltungskalender), `kontakt`,
   `production`, `tv`, außerdem `impressum`, `datenschutz`, `ueber-uns`.
5. **Permalinks:** Einstellungen → Permalinks → „Beitragsname“ (`/%postname%/`). Rubriken liegen unter
   `/category/<slug>/`.
6. **Customizer → Tamil.de:** Kontakt (Telefon, E-Mail, WhatsApp, Anschrift), Social-Profile (der WhatsApp-Kanal
   erscheint in Seitenspalte und Footer), Startseite (Aufmacher- und Rezept-ID, sonst automatisch), Production,
   TV-Sender, Formulare (Shortcode eines Formular-Plugins für Kontakt und „Event einreichen“).
   Kontaktdaten sind leer, bis sie eingetragen sind – es erscheinen keine Beispielnummern.
7. **Menüs (optional):** „Hauptnavigation“, „Footer: Service“, „Footer: Rechtliches“. Ohne Menü baut das Theme die
   Navigation aus den Rubriken.
8. **Einstellungen → Tamil.de Website:**
   - Werbeplätze 01–05 (+ Startseite): Advanced-Ads-Platzierung (Slug) **oder** Banner-HTML **oder** Eigenanzeige.
     Ohne Buchung zeigt jeder Platz eine Eigenanzeige (Production, Event melden, Werben, WhatsApp-Kanal).
   - Weiterleitungen: `export/redirects.csv` aus `tools/export_site.py` einfügen (Spalten `alt`, `neu`).
9. **Radar anbinden** (nur mit Teil B):
   - Benutzer `ki-agent` mit Rolle **Radar** anlegen → Profil → Anwendungspasswort erzeugen.
   - In der `.env` des Radars: `WP_URL=https://www.tamil.de`, `WP_USER=ki-agent`, `WP_APP_PASSWORD=…`,
     `WP_POST_STATUS=draft` (Redaktion veröffentlicht) oder `publish`.
   - News-Radar → Einstellungen: Adresse des Cockpits (`https://radar.tamil.de`). Das Cockpit erscheint im Menü
     „News-Radar“ (eingebettet nur unter HTTPS, sonst über „In neuem Tab öffnen“).
   - Prüfen: `python -m news_radar publish --pruefen` (zeigt Plugin, Rechte und Kategorien, veröffentlicht nichts).
10. **SEO:** Rank Math oder Yoast installieren; der Radar schreibt Titel, Beschreibung und Fokus-Schlagwort in das
    vorhandene Plugin.

## Was der Radar in WordPress anlegt

Ein Aufruf `POST /wp-json/tamil-radar/v1/beitrag` legt den kompletten Beitrag an: Text, Vorspann, Rubrik,
Schlagworte, Beitragsbild (mit Alt-Text und Bildnachweis als Bildunterschrift), Meta und SEO. Dubletten erkennt das
Plugin an `radar_uid` (Antwort 409 mit der vorhandenen ID). Kinolisten werden per `PUT beitrag/{uid}` fortgeschrieben.

| Feld | Bedeutung | Pflege |
|---|---|---|
| `standfirst`, `ort` | Vorspann, Ort der Meldung | Eingabemaske „Vorspann und Termin“ / Radar |
| `event_datum`, `event_ende`, `event_ort`, `event_land`, `event_veranstalter`, `event_preis`, `ticket_url`, `ticket_label` | Termin – erscheint im Kalender, auf der Startseite und als Faktenkasten im Beitrag | Eingabemaske / Radar |
| `kino_fakten` | Kinoliste (Film, Kinowoche, Spielorte) – Kino-Schaufenster auf der Startseite | Radar |
| `radar_uid`, `radar_relevanz`, `quelle_*` | Herkunft aus dem Radar, Quellenzeile | Radar |
| `bild_credit`, `bild_origin` | Bildnachweis; `ki` = KI-Symbolbild, das Theme ergänzt „Symbolbild: KI-generiert“ | Radar |

Jeder Beitrag zeigt ein Bild: Ohne Beitragsbild setzt das Theme die Bildkarte der Rubrik ein.

## Lokales Testbett (ohne Docker, ohne MySQL)

```bash
export WP_DIR=/pfad/zum/scratch/tamil-wp           # außerhalb des Repos
bash wordpress/dev/setup.sh                         # WordPress + SQLite + wp-cli, Plugins/Theme als Symlink
bash wordpress/dev/serve.sh &                       # http://127.0.0.1:8085
set -a; . "$WP_DIR/.env.local"; set +a              # Zugänge (nie ins Repo)
python wordpress/dev/import_prototype.py --wp-cli "php $WP_DIR/wp-cli.phar --path=$WP_DIR --allow-root"
python wordpress/dev/shots.py --out "$WP_DIR/shots" # Screenshots 390/820/1280 + Backend, prüft horizontales Scrollen
python -m pytest tests/test_wp_plugin.py -v         # Integrationstests gegen das laufende WordPress
bash wordpress/dev/lint.sh                          # php -l + WordPress-Coding-Standards (PHPCS)
bash wordpress/dev/package.sh                       # ZIPs nach wordpress/dist/
```

Zurücksetzen: `rm "$WP_DIR"/wp-content/database/tamil.sqlite && bash wordpress/dev/setup.sh`.

## Gestaltung

Der Look „modernes Community-Magazin“ ist in [`DESIGN.md`](../DESIGN.md) beschrieben (Farben, Schriften, Bausteine),
die Haltung dahinter in [`PRODUCT.md`](../PRODUCT.md).

- **Farben und Schriften** stehen in `themes/tamil/theme.json` (Palette `papier`, `sand`, `tinte`, `rot` …; Schriften
  Catamaran für Titel, Literata für Text). `assets/css/theme.css` liest sie als Variablen – eine geänderte Palette
  wirkt überall, auch im Editor.
- **Layout** liegt in den Vorlagen (`front-page.php`, `template-parts/home/*`, `single.php` …) und in `theme.css`.
  Die Daten (Auswahl der Startseite, Termine, Kinoliste, Werbeplätze) kommen aus Funktionen, die bleiben.
- **Bildgrößen:** Aufmacher 16:10, Karten 4:3, Zeilen quadratisch. Nach dem Wechsel auf dieses Theme die
  Vorschaubilder einmal neu erzeugen (Plugin „Regenerate Thumbnails“ oder `wp media regenerate`).

## Secrets

Nichts davon gehört ins Repo: `WP_APP_PASSWORD` (Radar), Admin-Zugänge, `.env.local` des Testbetts, API-Schlüssel des
Radars (`ANTHROPIC_API_KEY`, `GEMINI_API_KEY`). Anwendungspasswörter lassen sich im Profil jederzeit widerrufen.
