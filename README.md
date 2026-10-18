# Tamil.de – Relaunch & KI-Agent

Projekt HKG-2026-TML-V-001 (HK Growth Operator × KBS Management GmbH). Plan, Audit, Quellen und ROI:
[„Tamil.de Relaunch, Automation & ROI“](https://claude.ai/code/artifact/08e13154-b4ac-4123-9ff3-0087cf3a3612).

## News-Radar (Teil B)

Findet Nachrichten mit Bezug zur tamilischen Community im DACH-Raum, schreibt daraus einen eigenen
Beitrag im Tamil.de-Stil mit Bild, Kategorie, Schlagworten und SEO-Feldern und legt ihn in eine
Warteschlange. In der **Freigabe-App** wird geprüft, bearbeitet und mit einem Klick veröffentlicht.
Der Radar ist ein eigenständiges Werkzeug (eigener Server, eigene App); mit WordPress spricht er nur über das
Plugin `tamil-radar` (siehe [`wordpress/README.md`](wordpress/README.md)).

```
Quellen (Google News je Stadt, Schweizer Tamil-Portale, Eventfrog, Haus der Religionen, CineStar/kinoheld/Cineplexx, …)
  → Vorfilter (Alter, Ausschluss, Stichworte, DACH-Ort, Dubletten)
  → Claude: Relevanz 1–10 + Text auf Deutsch im Stil von prompts/redaktion.md (auch aus tamilischen/englischen Quellen)
  → Bild – immer: KI-Symbolbild (Gemini, prompts/bild.md) → Bildpool je Thema → Stockfoto → Tamil.de-Bildkarte
  → Warteschlange (SQLite)  →  Freigabe-App  →  „Direkt posten“ → WordPress (Plugin tamil-radar, ein REST-Aufruf)
```

Takt: alle 3 Minuten; ein Lauf bricht spätestens nach 4,5 Minuten ab. Eine Meldung liegt also rund
5 Minuten nach Erscheinen im Feed als Entwurf vor. Kinoprogramme werden je Film und Kinowoche zu
**einem** Beitrag „‹Film› (Tamil) läuft in n Kinos“ gebündelt und aktualisiert, solange er offen ist.

### Start

```bash
pip install -r requirements.txt
cp .env.example .env                 # Schlüssel eintragen (ANTHROPIC_API_KEY, WEB_*; WordPress optional)
python -m news_radar style           # Stil aus veröffentlichten tamil.de-Beiträgen lernen
python -m news_radar scan            # Quellen testen: was würde ausgewählt?
python -m news_radar run --max-age-hours 336   # Erstbefüllung (14 Tage), danach:
python -m news_radar run             # ein Lauf (Timer)
python -m news_radar web             # Freigabe-App lokal: http://127.0.0.1:8787
python -m news_radar publish         # alles Freigegebene nach WordPress (--pruefen: nur Verbindung testen)
python -m news_radar bildpool status # Reserve-Bilder je Thema; bildpool fuellen --anzahl 3 (braucht GEMINI_API_KEY)
python -m news_radar digest          # Tageszusammenfassung senden
python -m news_radar export          # Protokoll als JSONL
```

Ohne WordPress-Zugangsdaten warten Entwürfe in der App; „Freigeben“ merkt sie vor, sobald WordPress
angebunden ist, veröffentlicht `publish` bzw. der Timer-Lauf sie.

### „Research“ aus der Cloud-Sitzung

Solange kein `ANTHROPIC_API_KEY` auf dem Server liegt, schreibt Claude die Beiträge direkt in der Sitzung:
`/radar-research` oder einfach „Research“ startet die Runde (Skill `.claude/skills/radar-research`).

```bash
python -m news_radar scan
python -m news_radar run --ohne-ki --max-age-hours 72     # Rohfassungen mit Quelle und Bild
python -m news_radar agent export --file aufgabe.json     # Aufgabenmappe: Rohfassungen, Quelltexte, Stilprofil, Bildregeln
#   … Claude schreibt die Beiträge im Tamil.de-Stil (oder verwirft mit Grund) …
python -m news_radar agent import --file ergebnis.json --von "Claude (Research)"   # prüft Felder, setzt Bild, Status „bearbeitet“
```

Stil und Bilder sind Textdateien, keine Programmlogik: `news_radar/prompts/redaktion.md` (Tonfall, Haltung, Aufbau je
Beitragstyp, Tabus – abgeleitet aus 160 Beiträgen der alten tamil.de), `bild.md` (Hausstil und harte Regeln für
Symbolbilder: keine realen Personen, kein Text, keine Logos) und `bildpool.md` (rund 30 Themen mit Motiv je Rubrik).
KI-Bilder tragen den Nachweis „Symbolbild: KI-generiert · Tamil.de“.

### Freigabe-App

- Login (Cookie, 30 Tage), auf dem Handy als App installierbar („Zum Startbildschirm“)
- Feed mit Reitern Neu / Bearbeitet / Zurückgestellt / Freigegeben / Veröffentlicht / Abgelehnt / Fehler
- Je Entwurf: **Freigeben · Ablehnen · Bearbeiten · Zurückstellen**, bei angebundenem WordPress
  **Direkt posten** (sofort live) und **In WordPress bearbeiten** (als WP-Entwurf, Gutenberg öffnet)
- Bearbeiten: alle Felder, Live-Vorschau, „Neu schreiben lassen“ mit Anweisung, Zurücksetzen auf das Claude-Original
- Bild: **Neu generieren** (Motiv für die Bild-KI editierbar, Thema wählbar), **Aus dem Pool**, anderes Stockfoto,
  eigenes Bild, Bildkarte; KI-Bilder sind im Feed und im Editor als „KI-Symbolbild“ markiert
- Im WordPress-Backend unter „News-Radar“ eingebettet (nur unter HTTPS; `frame-ancestors` erlaubt nur `WP_URL`)
- Dashboard (offene/erledigte Vorgänge, je Kategorie/Quelle, Läufe, Fehler, Quellen-Status), Protokoll mit JSONL-Export

### WordPress vorbereiten

Ausführlich in [`wordpress/README.md`](wordpress/README.md). Kurz:

1. Plugin `tamil-radar` installieren (`bash wordpress/dev/package.sh` → `wordpress/dist/tamil-radar.zip`).
2. Benutzer „ki-agent“ mit Rolle **Radar** anlegen, Profil → Anwendungspasswörter → `WP_APP_PASSWORD` in `.env`.
3. Kategorien mit den Slugs aus `sources.toml` (`news`, `community`, `entertainment`, `kino`, `events`, `kueche`,
   `sport`, `kultur`). Fehlt eine, landet der Beitrag in `news`.
4. `python -m news_radar publish --pruefen` zeigt, ob das Plugin antwortet. Ohne Plugin nutzt der Radar die Core-REST
   (dann ohne Termin- und Kinofelder; SEO nur mit `WP_SEO_META=rankmath|yoast`).

### Server (HK-Server, systemd)

```bash
sudo ./deploy/install.sh     # /opt/tamil-news-radar: venv, Timer (3 Min.), Web-Service (gunicorn :8787), Digest-Timer (8 Uhr), Backup-Cron
```

Zugriff von außen über Cloudflare Tunnel: `deploy/cloudflared-ingress.yml`. Die App lauscht nur auf 127.0.0.1.

### Anpassen

Quellen, Regionen (DACH-Städte, Aliase, Tamil-Schreibweisen), Stichwort-Gewichte, Ausschlussliste und
Kategorien stehen in `sources.toml`; Schwellen und Takt in `.env` (siehe `.env.example`).

### Tests

```bash
python -m pytest -q
```

## Website-Relaunch (Teil A)

WordPress-Pakete in [`wordpress/`](wordpress/README.md): Theme **Tamil.de** (Startseite, Rubriken, Artikel, Termine,
Kontakt, Production, TV – Optik aus dem Designkonzept v3, ohne Radar-Elemente; Farben und Schriften in `theme.json`
für den Design-Relaunch austauschbar) und Plugin **Tamil.de Website** (Werbeplätze mit Eigenanzeigen,
301-Weiterleitungen, Termin-Felder). Lokales Testbett mit PHP + SQLite, Importer, Screenshots und PHPCS:
`wordpress/dev/`. Der klickbare Prototyp liegt in [`prototyp/`](prototyp/README.md).

`tools/export_site.py` exportiert alle öffentlichen Inhalte der alten tamil.de über die REST-API
(ohne Login): Beiträge, Seiten, Medien, Kategorien, Tags → `export/`, dazu `inventory.csv`
(Inhaltsinventar mit Empfehlung übernehmen/prüfen/löschen) und `redirects.csv` (301-Tabelle für den
Kategorien-Umzug).

```bash
python tools/export_site.py --site https://www.tamil.de --out export/        # mit Medien (~10 Min.)
python tools/export_site.py --no-media                                        # nur Texte und Inventar
```
