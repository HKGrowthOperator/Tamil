---
name: radar-research
description: Research-Runde für tamil.de – wartende Storys des Live-Radars im Agent-Modus schreiben (Claims mit Fundstelle, Beitrag im Tamil.de-Stil mit Belegen je Absatz) oder begründet verwerfen, dann importieren und prüfen. Auslösen bei „Research“, „neue Beiträge“, „Storys schreiben“, „Radar abarbeiten“ oder über /research.
argument-hint: "[limit]"
---

# Research-Runde (Agent-Modus gegen den Live-Radar)

Du bist die Redaktion von tamil.de. Der Live-Radar (https://tamil.hk-growthoperator.de) hat Storys mit gesammelten
Dokumenten; du ziehst Claims, schreibst und importierst. Dieselben Gates wie beim Modell-Worker gelten: Kernaussagen
nur aus bestätigten Claims, Belege je `<p>`, Links nur auf Quellen der Story.

## Zugang

- Token: Umgebungsvariable `RADAR_AGENT_TOKEN` oder eine Datei mit Rechten 600 (Pfad vom Auftraggeber der Runde). Nie
  ausgeben, nie in Dateien im Repo.
- Mappe: `curl -fsS -H "Authorization: Bearer $RADAR_AGENT_TOKEN" "$RADAR/api/agent/export?limit=5" > <scratch>/mappe.json`
- Import: `curl -fsS -X POST -H "Authorization: Bearer $RADAR_AGENT_TOKEN" -H "Content-Type: application/json" --data @<scratch>/ergebnis.json "$RADAR/api/agent/import?von=Claude%20(Research)"`
- Kontrolle: `python tools/radar_bericht.py` (Lese-Token).

## Schritte

1. Mappe holen; `anleitung`, `stil` und je Story `dokumente` (mit `id`), `laenge`, `typ` lesen.
2. Je Story genau ein Ergebnis in `{"ergebnisse": [...]}`:
   - **Beitrag:** `claims` (Aussage, `evidence_source_ids`, wörtliche Fundstelle aus dem Dokument), optional
     `widersprueche`, `beitrag` mit allen Feldern aus der Anleitung; `belege`: zu jedem `<p>` (ab 1) die Claim-IDs.
     Letzter Absatz ist die Quellenzeile `<p class="quelle">Quelle: …</p>`.
   - **Zu dünn:** nur `claims` plus `fehlend` (was fehlt) – der Radar setzt „Recherche nötig“.
   - **Verwerfen:** `{"story_id": …, "verwerfen": "Grund"}` bei vergangenem Termin, fehlendem DACH-Bezug, Dublette,
     Klatsch.
3. Importieren; Antwort lesen (`angelegt`, `recherche`, `verworfen`, `fehler`). Fehler beheben, nur diese Storys erneut.
4. `python tools/radar_bericht.py` → Entwürfe mit Hinweisen prüfen (Länge, Quellenzeile, Copydesk).
5. Bericht an Luis: Tabelle Story · Ergebnis · Titel/Grund · Hinweise.

## Stolperfallen

- Fundstellen müssen **wörtlich** im Dokument stehen, sonst verwirft das Gate den Claim.
- Termine: das späteste Datum im Text zählt; liegt es in der Vergangenheit → verwerfen.
- Länge nach `laenge` (Event 150–250 Wörter); zu kurz erzeugt Hinweise im Cockpit.
- Stil: `news_radar/prompts/redaktion.md` (Deutsch, „ihr“-Ansprache, keine übernommenen Sätze, keine erfundenen
  Zitate).
- Lokaler Rückfallweg ohne Live-Radar: `python -m news_radar agent export --v2 --file …` / `agent import --v2 …`.
