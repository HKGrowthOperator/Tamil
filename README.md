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

### Redaktion v2: Rollen, Belege, Kostenmessung (Blueprint 19.10.)

Mit `RADAR_WORKFLOW=v2` arbeitet der Radar als kleine Redaktion. Ein deterministischer Orchestrator verteilt die Arbeit,
Sprachmodelle kommen nur in einzelnen Rollen zum Einsatz, und jeder Modellaufruf wird gemessen und gegen ein Budget
gebucht.

```
Timer (3 Min.)  run     Quellen → Vorfilter → Signal (Haiku, nur Grauzone) → Story-Clustering → Story + Job
Dienst          worker  Recherche (Belege + Claims, Sonnet) → Gate (Regeln) → Text (Sonnet) → Faktencheck (Sonnet)
                        → Lektorat (Regeln + Haiku) → SEO (Regeln + Haiku) → Bild mit Lizenz → Entwurf „neu“
Kino                    Kinoprogramm → Textvorlage → Entwurf (ohne Modell)
Mensch          App     freigeben (mit Person und Fassungs-Hash protokolliert) → WordPress
```

- **Belege statt Bauchgefühl:** Jede Story sammelt Dokumente (Volltext der Primärquelle, weitere Meldungen zum selben
  Ereignis, Google-News-Titel nur als Hinweis). Die Recherche zieht Aussagen (Claims) mit Dokument-Kennung und
  Fundstelle. Das **Gate** prüft nach Regeln: Kernaussagen (was, wer, wann, wo; bei Terminen Datum und Ort) müssen in
  einer Primärquelle oder in zwei unabhängigen Quellen stehen, und die Fundstelle muss wörtlich im Dokument stehen.
  Sonst landet die Story unter **„Recherche nötig“**, und die Redaktion kann eine Quelle ergänzen.
- **Text nur aus bestätigten Claims**, Länge nach Stofflage (Kurzmeldung, Nachricht, lange Nachricht, Termin, Kino,
  Dossier), Belege je Absatz, Links nur auf Quellen der Story. Der **Faktencheck** prüft danach jeden Satz; bei einer
  ungedeckten Kernaussage gibt es genau eine Überarbeitung.
- **Story-Clustering:** Eine zweite Meldung zum selben Ereignis reichert die Story an, statt einen zweiten Entwurf
  anzulegen. Hängt die Story unter „Recherche nötig“, startet die neue Quelle die Recherche neu.
- **Kosten und Budget:** Preise je Modell (Stand 08.11.2026, inklusive Cache und Fallback-Versuche) in
  `workflow/costs.py`. Vor jedem Aufruf wird der ungünstigste Fall reserviert. Bei 80 % kommt eine Warnung, bei 100 %
  ein harter Stopp für neue bezahlte Schritte. Freigeben und Veröffentlichen laufen weiter.
- **Bilder mit Lizenz:** Archiv → Pressebild (nur mit `bild_nutzen = true` im Register) → Stock → Pool → KI (höchstens
  eins je Story) → Bildkarte. Jedes Bild bekommt einen Datensatz mit Rechteinhaber, Lizenz, Umfang und Ablauf.
- **Ohne API-Schlüssel** laufen Scan und Kino. Recherche und Text übernimmt dann die Cloud-Sitzung:
  `agent export --v2` / `agent import --v2`, mit denselben Gates.

```bash
python -m news_radar quellen pruefen   # Register live prüfen (robots, Ausbeute, Paywall) → data/quellen-pruefung.csv
python -m news_radar run               # RADAR_WORKFLOW=v2: Storys und Jobs anlegen (--mit-jobs: gleich abarbeiten)
python -m news_radar worker            # Jobs abarbeiten (Dienst; --einmal leert die Schlange)
python -m news_radar kosten            # Kosten je Rolle/Modell/Tag, Budgetstand; --csv für die Abrechnung
python -m news_radar bericht --woche   # Annahmequote, „Recherche nötig“, Kosten je Entwurf, Fehler
python -m news_radar dossier --entwurf 12   # Entwurf als Dossier recherchieren (Opus)
python -m news_radar nutzer anlegen priya --rolle redaktion
python -m news_radar abnahme           # 51 Szenarien mit FakeClaude, Kriterien K1–K9 → data/abnahme-bericht.md
python -m news_radar bewertung vergleich --anzahl 10   # Sonnet gegen Opus blind (braucht Schlüssel)
python -m news_radar sicherung erstellen|pruefen|wiederherstellen --datum 2026-11-08
```

Die Prompts der Rollen liegen als Markdown neben `redaktion.md`: `signal.md`, `cluster.md`, `recherche.md`, `text.md`,
`faktencheck.md`, `lektorat.md`, `seo.md`. Die Modelle je Rolle stehen in `.env` (`RADAR_MODELL_<ROLLE>`).

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
- Redaktion v2: im Entwurf Quellen mit Rechten, Faktenmatrix als Ampel, Faktencheck je Satz, Fassungen mit
  Änderungen, Kosten der Story, Bildlizenz, „Als Dossier recherchieren“; Seiten **Recherche nötig**, **Kosten**
  (mit CSV), **Quellen** (Register, robots, Ausfallquote), **Warteschlange** (abgebrochene Jobs neu starten),
  **Benutzer** (Rollen redaktion/admin); Budget-Banner bei 80 % und beim Stopp

### WordPress vorbereiten

Ausführlich in [`wordpress/README.md`](wordpress/README.md). Kurz:

1. Plugin `tamil-radar` installieren (`bash wordpress/dev/package.sh` → `wordpress/dist/tamil-radar.zip`).
2. Benutzer „ki-agent“ mit Rolle **Radar** anlegen, Profil → Anwendungspasswörter → `WP_APP_PASSWORD` in `.env`.
3. Kategorien mit den Slugs aus `sources.toml` (`news`, `community`, `entertainment`, `kino`, `events`, `kueche`,
   `sport`, `kultur`). Fehlt eine, landet der Beitrag in `news`.
4. `python -m news_radar publish --pruefen` zeigt, ob das Plugin antwortet. Ohne Plugin nutzt der Radar die Core-REST
   (dann ohne Termin- und Kinofelder; SEO nur mit `WP_SEO_META=rankmath|yoast`).

### Coolify (Dockerfile, ein Container)

Coolify baut das `Dockerfile` im Repo-Root (Build-Pack „Dockerfile“, Port **3000**). Im Container läuft
`python -m news_radar dienst`: Cockpit (gunicorn) auf `$PORT`, Scan alle 3 Minuten, Worker der Redaktion v2,
Tageszusammenfassung um 8 Uhr und eine tägliche Sicherung nach `/app/data/backup`. Alles läuft als Nutzer `radar`, nicht als root.

- **Persistent Storage:** ein Volume auf `/app/data`. Ohne Volume sind Datenbank und Bilder beim Redeploy weg.
- **Domain:** in Coolify setzen, dieselbe Adresse als `RADAR_WEB_URL` (mit `https://`).
- **Umgebungsvariablen** (Schlüssel und Passwörter nur in Coolify, nie im Repo):

| Variable | Wert | Zweck |
|---|---|---|
| `ANTHROPIC_API_KEY` | Schlüssel | Modelle der Redaktion v2 (ohne: nur Scan, Worker startet nicht) |
| `RADAR_WORKFLOW` | `v2` | Redaktion mit Rollen, Belegen und Budget |
| `WEB_USER` / `WEB_PASSWORD` | Name / mind. 12 Zeichen | Notzugang (admin) – ohne Passwort startet das Cockpit nicht |
| `WEB_SECRET` | zufällig, 32+ Zeichen | signiert die Cookies |
| `RADAR_WEB_URL` | `https://<domain>` | Links, sichere Cookies |
| `RADAR_PROXY_HOPS` | `1` | hinter Coolify/Traefik: echte Client-IP für die Login-Drossel, HTTPS erkennen |
| `RADAR_BUDGET_TAG_USD` / `RADAR_BUDGET_MONAT_USD` | Pilot: `2` / `2` | harter Kostendeckel |
| `RADAR_ENTWUERFE_TAG` | `5` | neue bezahlte Storys je Tag |
| `RADAR_KI_BILDER_JE_ARTIKEL` | Pilot: `0` | keine KI-Bilder (dann auch kein `GEMINI_API_KEY` nötig) |
| `RADAR_LESE_TOKEN` | zufällig, 32+ Zeichen | optional: `GET /api/bericht` (nur lesen) für Auswertungen |

WordPress-Variablen (`WP_*`) leer lassen, solange nur getestet wird: Dann veröffentlicht der Radar nichts.
`/gesund` zeigt Warteschlange und Budget. Einzelbefehle laufen über „Execute command“ im Container, z. B.
`python -m news_radar kosten` oder `python -m news_radar nutzer anlegen priya --rolle redaktion`.

### Server (HK-Server, systemd)

```bash
sudo ./deploy/install.sh     # /opt/tamil-news-radar: venv, Timer (3 Min.), Web-Service (gunicorn :8787), Digest-Timer (8 Uhr), Backup-Cron
sudo /opt/tamil-news-radar/restore.sh 2026-11-08   # Backup-Stand zurückspielen (prüft vorher die Integrität)
```

Code, venv und Skripte unter `/opt/tamil-news-radar` gehören root, das Dienstkonto `newsradar` schreibt nur in `data/`
und `backup/`. `restore.sh` stoppt alle Radar-Timer und -Dienste (bricht ab, wenn einer weiterläuft) und lässt Python als
`newsradar` laufen. Stilbeispiele (`style`) deshalb im Repo aktualisieren und neu installieren.

Mit `RADAR_WORKFLOW=v2` in der `.env` aktiviert `install.sh` zusätzlich den Worker-Dienst und den wöchentlichen
Bildpool-Timer (nur fehlende Bilder, mit Budget). `/gesund` zeigt Warteschlange und Budget; die Tageszusammenfassung
nennt Kosten und Probleme.

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
Kontakt, Production, TV – Look „modernes Community-Magazin“, beschrieben in [`DESIGN.md`](DESIGN.md) und
[`PRODUCT.md`](PRODUCT.md)) und Plugin **Tamil.de Website** (Werbeplätze mit Eigenanzeigen, 301-Weiterleitungen,
Termin-Felder). Lokales Testbett mit PHP + SQLite, Importer, Screenshots und PHPCS: `wordpress/dev/`. Der frühere
klickbare Prototyp in [`prototyp/`](prototyp/README.md) zeigt den abgelösten Entwurf v3 und dient nur noch als Archiv.

`tools/export_site.py` exportiert alle öffentlichen Inhalte der alten tamil.de über die REST-API
(ohne Login): Beiträge, Seiten, Medien, Kategorien, Tags → `export/`, dazu `inventory.csv`
(Inhaltsinventar mit Empfehlung übernehmen/prüfen/löschen) und `redirects.csv` (301-Tabelle für den
Kategorien-Umzug).

```bash
python tools/export_site.py --site https://www.tamil.de --out export/        # mit Medien (~10 Min.)
python tools/export_site.py --no-media                                        # nur Texte und Inventar
```
