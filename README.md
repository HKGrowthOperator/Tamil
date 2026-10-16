# Tamil.de – Relaunch & KI-Agent

Projekt HKG-2026-TML-V-001 (HK Growth Operator × KBS Management GmbH). Plan, Audit, Quellen und ROI:
[„Tamil.de Relaunch, Automation & ROI“](https://claude.ai/code/artifact/08e13154-b4ac-4123-9ff3-0087cf3a3612).

## News-Radar (Teil B)

Findet Nachrichten mit Bezug zur tamilischen Community im DACH-Raum, schreibt daraus einen eigenen
Beitrag im Tamil.de-Stil mit Bild, Kategorie, Schlagworten und SEO-Feldern und legt ihn in eine
Warteschlange. In der **Freigabe-App** wird geprüft, bearbeitet und mit einem Klick veröffentlicht.

```
Quellen (Google News je Stadt, Schweizer Tamil-Portale, Eventfrog, Haus der Religionen, CineStar/kinoheld/Cineplexx, …)
  → Vorfilter (Alter, Ausschluss, Stichworte, DACH-Ort, Dubletten)
  → Claude: Relevanz 1–10 + Text auf Deutsch (auch aus tamilischen/englischen Quellen)
  → Bild (Unsplash/Pexels oder Tamil.de-Bildkarte)
  → Warteschlange (SQLite)  →  Freigabe-App  →  „Direkt posten“ → WordPress (REST, Anwendungspasswort)
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
python -m news_radar publish         # alles Freigegebene nach WordPress
python -m news_radar digest          # Tageszusammenfassung senden
python -m news_radar export          # Protokoll als JSONL
```

Ohne WordPress-Zugangsdaten warten Entwürfe in der App; „Freigeben“ merkt sie vor, sobald WordPress
angebunden ist, veröffentlicht `publish` bzw. der Timer-Lauf sie.

### Freigabe-App

- Login (Cookie, 30 Tage), auf dem Handy als App installierbar („Zum Startbildschirm“)
- Feed mit Reitern Neu / Bearbeitet / Zurückgestellt / Freigegeben / Veröffentlicht / Abgelehnt / Fehler
- Je Entwurf: **Freigeben · Ablehnen · Bearbeiten · Zurückstellen**, bei angebundenem WordPress
  **Direkt posten** (sofort live) und **In WordPress bearbeiten** (als WP-Entwurf, Gutenberg öffnet)
- Bearbeiten: alle Felder, Live-Vorschau, „Neu schreiben lassen“ mit Anweisung, anderes Stockfoto /
  eigenes Bild / Bildkarte, Zurücksetzen auf das Claude-Original
- Dashboard (offene/erledigte Vorgänge, je Kategorie/Quelle, Läufe, Fehler, Quellen-Status), Protokoll mit JSONL-Export

### WordPress vorbereiten

1. Benutzer „ki-agent“ mit Rolle **Autor** anlegen (darf eigene Beiträge veröffentlichen und Bilder hochladen).
2. Profil → Anwendungspasswörter → Passwort erzeugen → `WP_APP_PASSWORD` in `.env`.
3. Kategorien mit den Slugs aus `sources.toml` anlegen (`news`, `community`, `entertainment`, `kino`,
   `events`, `kueche`, `sport`, `kultur`). Fehlt eine, landet der Beitrag in `news`.
4. Optional `WP_SEO_META=rankmath|yoast`, wenn das SEO-Plugin seine Felder per REST annimmt.

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

`tools/export_site.py` exportiert alle öffentlichen Inhalte der alten tamil.de über die REST-API
(ohne Login): Beiträge, Seiten, Medien, Kategorien, Tags → `export/`, dazu `inventory.csv`
(Inhaltsinventar mit Empfehlung übernehmen/prüfen/löschen) und `redirects.csv` (301-Tabelle für den
Kategorien-Umzug).

```bash
python tools/export_site.py --site https://www.tamil.de --out export/        # mit Medien (~10 Min.)
python tools/export_site.py --no-media                                        # nur Texte und Inventar
```
