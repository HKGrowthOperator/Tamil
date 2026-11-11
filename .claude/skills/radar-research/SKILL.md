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
- Arbeit aufteilen (mehrere Sitzungen gleichzeitig): erst `…/api/agent/export?nur=uebersicht` (Liste der offenen
  Storys ohne Dokumente, kein Abruf), dann je Sitzung eigene Storys mit `…/api/agent/export?ids=3,4,5` holen (höchstens
  20, nur offene, in dieser Reihenfolge; Fertiges oder Fremdes fällt still heraus). Lokal: `agent export --v2 --ids 3,4,5`.
- Dokumente mit `art: "daten"` sind strukturierte Angaben einer Seite (JSON-LD), kein sichtbarer Text: Aussagen
  daraus sind belegbar, aber die Länge bleibt knapp (Längenregel); nichts aus ihnen ausschmücken.
- Import: `curl -fsS -X POST -H "Authorization: Bearer $RADAR_AGENT_TOKEN" -H "Content-Type: application/json" --data @<scratch>/ergebnis.json "$RADAR/api/agent/import?von=Claude%20(Research)"`
- Kontrolle: `python tools/radar_bericht.py` (Lese-Token).

## Schritte

1. Mappe holen; `anleitung`, `stil` und je Story `dokumente` (mit `id`), `laenge`, `typ` und `stilbeispiele`
   (zwei Beiträge der alten tamil.de derselben Art: nur Ton und Aufbau, nie Inhalt) lesen.
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

## Nachtrag ergänzen

Fehlen einer Nachtrag-Story (Herkunft `nachtrag`, Status „Recherche nötig“) Kernfakten, keine neue Story vorschlagen:
denselben Vorschlag mit `"story_id": <Nummer>` und den neuen Quellen an `POST /api/agent/vorschlag` schicken (oder
`agent vorschlag --datei`). Der Radar holt nur Adressen, die noch nicht Beleg der Story sind, hängt sie an (Q<n+1> …),
gibt die Story wieder frei (Status „neu“) und ersetzt die Hinweise (`bezug`, `kernfakten`, `bild_hinweis`). Antwort
`ergaenzt`; `vorhanden` heißt: keine neue Quelle; `abgelehnt` nennt den Grund (Story nicht gefunden, keine
Nachtrag-Story, Story ist …, Job läuft). Danach die Story im nächsten Export neu schreiben – alle Dokumente sind dabei.

## Stolperfallen

- Fundstellen müssen **wörtlich** im Dokument stehen, sonst verwirft das Gate den Claim.
- Termine: das späteste Datum im Text zählt; liegt es in der Vergangenheit → verwerfen.
- Länge nach Stofflage (`laenge` in der Mappe, Staffel in `redaktion.md`): viel Stoff (ab acht bestätigten Aussagen
  aus zwei Quellen oder einer ergiebigen Primärquelle) Nachricht/Porträt 450–750, Kino/Event 350–550 Wörter; mittel
  (vier bis sieben) 250–400; wenig = Kurzmeldung 80–150; ohne Volltext Event/Kino höchstens 150–250, sonst
  Kurzmeldung. Die Mappe nennt je Story die Staffel in `laenge` und `laenge_staffel` – genau so stuft der Import ein. Lange Beiträge: Kern im ersten Absatz, `<h2>` je Abschnitt,
  Hintergrund nur aus Claims, bei Termin/Kino ein Service-Absatz. **Nie strecken** – trägt der Stoff die Spanne
  nicht, bleibt der Text kürzer. Abweichungen und lange Texte ohne `<h2>` erzeugen Hinweise im Cockpit.
- Stil: `news_radar/prompts/redaktion.md` (Deutsch, „ihr“-Ansprache, keine übernommenen Sätze, keine erfundenen
  Zitate).
- Lokaler Rückfallweg ohne Live-Radar: `python -m news_radar agent export --v2 --file …` / `agent import --v2 …`.
