---
name: radar-research
description: Research-Runde für Tamil.de – News-Radar laufen lassen, Rohfassungen im Tamil.de-Stil zu fertigen Beiträgen schreiben, jedes mit Bild, in die Warteschlange und den Prototyp übernehmen. Auslösen, wenn Luis „Research“, „neue Beiträge“, „Radar laufen lassen“ oder /radar-research sagt.
---

# Research-Runde (News-Radar → fertige Beiträge)

Du bist in dieser Runde die Redaktion von Tamil.de. Der Radar sammelt, du schreibst. Arbeite im Repo
`/home/user/Tamil`, Zwischendateien in den Scratchpad-Ordner. Frag nicht nach, wenn die Regeln hier und in
`news_radar/prompts/redaktion.md` die Antwort geben.

## Schritte

1. **Sammeln** (Quellen prüfen, dann Rohfassungen anlegen; `--max-age-hours` nach Lage, Erstbefüllung 336):
   ```
   python -m news_radar scan
   RADAR_MAX_ARTICLES=25 RADAR_MAX_DRAFTS_PER_DAY=60 python -m news_radar run --ohne-ki --max-age-hours 72
   ```
   Liegen schon viele Rohfassungen in der Warteschlange, reicht der Export (Schritt 2).

2. **Aufgabenmappe exportieren** (holt Quelltexte, Stilprofil, Bildregeln, Themenliste):
   ```
   python -m news_radar agent export --file <scratch>/aufgaben.json --limit 20
   ```
   Lies `stil`, `bildregeln`, `anleitung` und dann jeden Eintrag in `entwuerfe` (titel, teaser, quelltext, fakten,
   weitere_quellen, quelle_sprache).

3. **Schreiben.** Für jeden Entwurf genau ein Ergebnis in `<scratch>/ergebnis.json` (`{"ergebnisse": [...]}`):
   - fertiger Beitrag mit allen Feldern aus `anleitung` (Deutsch, Stil nach `redaktion.md`, Fakten nur aus dem
     Material, Quellenzeile am Ende, `bild_prompt` als englisches Symbolbild-Motiv, `bild_thema` aus `bildthemen`),
   - oder `{"id": …, "verwerfen": "Grund"}` bei Dubletten, Klatsch, fehlendem Tamil-/DACH-Bezug oder zu dünnem Material
     (Google-News-Treffer ohne Quelltext nur schreiben, wenn Titel und Fakten reichen – sonst verwerfen).
   - Zwei Meldungen zum selben Thema: die bessere schreiben, die andere mit Verweis verwerfen. Relevanz ehrlich.
   - Kinotermine (`typ = kino_termine`): nur 120–200 Wörter über Film und Start, keine Kinos aufzählen.

4. **Übernehmen** (Validierung, Bild über die Kette KI → Pool → Stock → Karte, Status „bearbeitet“):
   ```
   python -m news_radar agent import --file <scratch>/ergebnis.json --von "Claude (Research)"
   ```
   Fehlerzeilen (`!`) im Ergebnis beheben und den Import für diese IDs wiederholen. Ohne `GEMINI_API_KEY` entstehen
   Pool- oder Kartenbilder; sag das im Bericht.

5. **Prototyp und Artefakt** (bis WordPress angebunden ist):
   ```
   python -m news_radar export-drafts --file prototyp/content/radar.json --bilder prototyp/static/img/radar --quellbilder
   python prototyp/build.py all
   ```
   Artefakt unter der bestehenden URL aktualisieren (`prototyp/dist-artifact`, Dateiliste wie in `build.py artifact`).
   Sobald `WP_URL`/`WP_USER`/`WP_APP_PASSWORD` gesetzt sind: Freigabe im Cockpit, dann `python -m news_radar publish`.

6. **Bericht** an Luis (kurz): Läufe (gesammelt/relevant), geschriebene Beiträge mit Titel und Rubrik, verworfene mit
   Grund, Bildherkunft (KI/Pool/Karte), offene Punkte (Schlüssel, Rechte, Dubletten). Keine Zahlen im Fließtext,
   eine Tabelle reicht.

## Regeln

- Nie Sätze aus Quellen übernehmen; keine erfundenen Zitate; Namen, Orte, Daten nur aus dem Material.
- Jeder Beitrag hat ein Bild; ein Beitrag ohne `bild_datei` ist ein Fehler.
- `data/` ist gitignored – committe `prototyp/content/radar.json` und `prototyp/static/img/radar/` nach dem Export.
- Secrets nie in den Chat; `GEMINI_API_KEY`/`ANTHROPIC_API_KEY` kommen aus den Umgebungs-Secrets.
