# Tamil.de – Relaunch & KI-Agent

Projekt HKG-2026-TML-V-001 (HK Growth Operator × KBS Management GmbH).

## News-Radar

Findet Nachrichten mit Bezug zur tamilischen Community, filtert sie und legt sie als
fertigen WordPress-Entwurf mit Text, Bild, Kategorie, Schlagworten und SEO-Feldern an.
Veröffentlicht wird erst nach Freigabe in WordPress (Status „Ausstehender Review“).

```
Quellen (RSS, NewsAPI, GNews)  →  Vorfilter (Alter, Ausschluss, Stichworte, Dubletten)
  →  Claude: Relevanz 1–10 + Text im Tamil.de-Stil  →  Bild (Unsplash/Pexels oder Tamil.de-Karte)
  →  WordPress-Entwurf  →  Benachrichtigung (Slack/Teams/Discord)
```

Takt: alle 3 Minuten, ein Lauf dauert ca. 1–2 Minuten und bricht spätestens nach
4,5 Minuten ab. Damit liegt eine neue Meldung spätestens rund 5 Minuten nach Erscheinen
im Feed als Entwurf vor.

### Start

```bash
pip install -r requirements.txt
cp .env.example .env            # Schlüssel eintragen
python -m news_radar style      # Stil aus veröffentlichten tamil.de-Beiträgen lernen
python -m news_radar scan       # Quellen testen: was würde ausgewählt?
python -m news_radar run        # ein Lauf
python -m news_radar loop --interval 180   # Dauerbetrieb
python -m news_radar export     # Protokoll als JSONL
```

Ohne WordPress-Zugangsdaten läuft alles als Dry-Run: Entwürfe landen mit Bild und
`vorschau.html` in `out/`.

### Server

`sudo ./deploy/install.sh` richtet einen systemd-Timer (alle 3 Minuten) unter
`/opt/tamil-news-radar` ein.

### WordPress vorbereiten

1. Benutzer „KI-Agent“ mit Rolle **Autor** anlegen (darf Entwürfe einreichen, nicht veröffentlichen).
2. Unter Profil → Anwendungspasswörter ein Passwort erzeugen und in `.env` eintragen.
3. Kategorien mit den Slugs aus `sources.toml` anlegen (`news`, `community`, `entertainment`,
   `kino`, `events`, `kueche`, `sport`, `kultur`). Fehlt eine, landet der Beitrag in `news`.

### Anpassen

Quellen, Stichwort-Gewichte, Ausschlussliste und Kategorien stehen in `sources.toml`.
Schwellenwerte und Takt stehen in `.env` (siehe `.env.example`).

### Tests

```bash
python -m pytest -q
```

## Plan, Zeitplan & ROI

Siehe das Dokument [„Tamil.de Relaunch, Automation & ROI“](https://claude.ai/code/artifact/08e13154-b4ac-4123-9ff3-0087cf3a3612).
