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

## Bild vorschlagen

Entwürfe aus dem Agent-Modus haben zunächst nur die Bildkarte. Für einen **wartenden** Entwurf (noch nicht freigegeben)
darf ein echtes Bild vorgeschlagen werden, auf zwei Wegen:

- **commons:** `seite_url` ist eine Dateiseite `https://commons.wikimedia.org/wiki/File:…`. Erlaubt sind nur
  gemeinfrei/CC0, CC BY und CC BY-SA (nichts mit NC oder ND, kein reines GFDL); JPEG, PNG oder WebP ab 800 Pixel Breite;
  bei CC BY und CC BY-SA muss ein Urheber angegeben sein.
- **quelle:** `seite_url` ist ein Dokument genau dieser Story auf einem Host aus dem Bildquellen-Register
  (`[[bildquellen]]` in `sources.toml`: Tempel, Vereine, Veranstalter, Festivals, Kinos, Betriebe). Ohne `bild_url` nimmt
  der Radar das `og:image`; mit `bild_url` muss die Adresse auf der Seite stehen. Das Bild muss unter dem eingetragenen
  Host liegen (Subdomains und die `bild_hosts` des Eintrags zählen); ein `og:image` auf einem Zeitungs- oder Agentur-CDN
  wird abgelehnt. Nie Agenturfotos (dpa, Keystone,
  Getty …), nie KI-Bilder, nie etwas aus sozialen Netzwerken; Logos, Icons und Banner werden abgelehnt.

Aufruf: `curl -fsS -X POST -H "Authorization: Bearer $RADAR_AGENT_TOKEN" -H "Content-Type: application/json" --data
'{"bilder": [{"story_id": 42, "weg": "quelle", "seite_url": "https://…", "alt": "…"}]}' "$RADAR/api/agent/bild?von=Claude%20(Research)"`
(höchstens fünf je Aufruf, `alt` höchstens 160 Zeichen reiner Text). Den Bildnachweis und die Lizenz setzt **der
Radar** selbst (aus Commons bzw. dem Register), nie aus dem Vorschlag. Antwort je Eintrag: `gesetzt` (mit `nachweis`,
`lizenz`), `abgelehnt` (mit `grund`) oder `nicht_bearbeitet`. Die Freigabe bleibt beim Menschen im Cockpit.

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
