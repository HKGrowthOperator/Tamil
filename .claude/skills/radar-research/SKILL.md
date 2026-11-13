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
- Kontrolle: `python tools/radar_bericht.py` (Lese-Token `RADAR_LESE_TOKEN`, sonst `RADAR_AGENT_TOKEN` – `/api/bericht` nimmt beide).

## Schritte

1. Mappe holen; `anleitung`, `stil` und je Story `dokumente` (mit `id`), `laenge`, `typ` und `stilbeispiele`
   (zwei Beiträge der alten tamil.de derselben Art: nur Ton und Aufbau, nie Inhalt) lesen.
2. Je Story genau ein Ergebnis in `{"ergebnisse": [...]}`:
   - **Beitrag:** `claims` (Aussage, `evidence_source_ids`, wörtliche Fundstelle aus dem Dokument), optional
     `widersprueche`, `beitrag` mit allen Feldern aus der Anleitung; `belege`: zu jedem `<p>` (ab 1) die Claim-IDs.
     Letzter Absatz ist die Quellenzeile `<p class="quelle">Quelle: …</p>`.
   - **Zweite KI (Pflicht):** vor dem Import prüft ein **eigener Agent aus frischem Kontext** (eine andere Instanz,
     kennt deine Begründung nicht, nur `dokumente` und den Beitrag; Maßstab: `news_radar/prompts/pruefer.md`, Aufgabe
     `entwurf`) jeden Satz und liefert den Block `pruefung`. Beispiel:

     ```json
     "pruefung": {"pruefer": "claude-code/pruefer-1", "autor": "claude-code/redakteur-1",
      "zeitpunkt": "2026-11-13T21:40:00+00:00", "urteil": "importieren",
      "befunde": [{"schwere": "P3", "beschreibung": "Teaser etwas lang", "satz": "", "behoben": false}],
      "saetze": [{"nr": 1, "satz": "Der Verein erhielt am Freitag den Integrationspreis.", "urteil": "gedeckt",
                  "claim_ids": ["C1"], "fundstelle": "hat am Freitag den Integrationspreis", "kern": true}]}
     ```

     Pflicht für jeden Beitrag (Verwerfen braucht keine): eine andere Instanz als der Autor (`pruefer` ≠ `?von=` und ≠ `autor`), `zeitpunkt` ISO 8601 mit Zeitzone, nicht in der Zukunft, höchstens drei Tage alt, `urteil` `importieren` oder `nicht_importieren`, `befunde` mit `schwere` P1/P2/P3 und `behoben`, `saetze` nicht leer (`urteil` gedeckt/ungedeckt/widerspruch/kein_fakt, `kern`). Abgewiesen – nichts geändert – ohne Block, bei gleicher Instanz, ungültigem Zeitpunkt, `nicht_importieren`, offenen P1/P2 oder leeren `saetze`. Danach streicht der Radar ungedeckte Nebensätze; eine ungedeckte Kernaussage schickt die Story in die Nachrecherche. Der Block wird als Fassung `pruefung` gespeichert, der Entwurf trägt „Geprüft von zweiter KI (Prüfer, Zeitpunkt)“ und die Befunde als Hinweise.
   - **Zu dünn:** selbst weitersuchen (Seite des Veranstalters, Verein, registrierte Medien – nie soziale Netzwerke, keine
     Paywall) und `{"story_id": …, "neue_quellen": ["https://…"]}` liefern; der Radar liest sie selbst und hängt sie an,
     die Story kommt im nächsten Export mit den neuen Dokumenten. Ein Eintrag nur mit `fehlend` wird abgelehnt: nichts
     bleibt offen.
   - **Verwerfen:** `{"story_id": …, "verwerfen": "Grund"}` bei vergangenem Termin, fehlendem DACH-Bezug, Dublette,
     Klatsch – oder wenn die Belege auch nach der Suche nicht tragen.
3. Importieren; Antwort lesen (`entwuerfe`, `nachrecherche`, `quellen`, `verworfen`, `fehler`). Fehler beheben, nur
   diese Storys erneut.
4. `python tools/radar_bericht.py` → Entwürfe mit Hinweisen prüfen (Länge, Quellenzeile, Copydesk).
5. Bericht an Luis: Tabelle Story · Ergebnis · Titel/Grund · Hinweise.

## In Nachrecherche (eigene Liste im Export)

„Recherche nötig“ gibt es nicht mehr als Endzustand (Auftrag Luis, 13.11.2026). Scheitert das Gate, sucht der Radar
selbst (höchstens zwei Runden); ohne Modellschlüssel stehen solche Storys danach in der Mappe unter `nachrecherche`
(nicht unter `storys`) mit `runde`, `letzte_runde`, `fehlend` (Fehlstellen), `suchanfragen`, `gruende` und dem
`ergebnis` der letzten Runde. Je Story: mit den Suchanfragen nach Belegen für die Fehlstellen suchen und `neue_quellen`
liefern – oder, wenn die bestätigten Aussagen tragen, einen Beitrag nur aus ihnen (notfalls Kurzmeldung 80–150 Wörter,
nur bestätigte Claims, jeder Absatz belegt) – oder verwerfen mit Grund. Bei `letzte_runde: true` entscheidet der Import
endgültig: Kurzmeldung aus bestätigten Claims oder verworfen. In der Übersicht (`nur=uebersicht`) tragen diese Storys
`"nachrecherche": true`.

## Story ergänzen

Fehlen einer Story in Nachrecherche (Herkunft `nachtrag` oder `radar`) Kernfakten und hast du Quellen, keine neue Story
vorschlagen:
denselben Vorschlag mit `"story_id": <Nummer>` und den neuen Quellen an `POST /api/agent/vorschlag` schicken (oder
`agent vorschlag --datei`). Der Radar holt nur Adressen, die noch nicht Beleg der Story sind, hängt sie an (Q<n+1> …),
gibt die Story wieder frei (Status „neu“) und führt die Hinweise zusammen (leeres `bezug`/`bild_hinweis` behält den
alten Wert; `kernfakten` aus neu und alt ohne Doppel, neue zuerst, höchstens 12). Antwort
`ergaenzt`; `vorhanden` heißt: keine neue Quelle; `abgelehnt` nennt den Grund („Story nicht ergänzbar“: unbekannt,
nicht in Nachrecherche, Kino oder schon ein Entwurf; oder „Job läuft“; Einzelheiten im Ereignislog). Eine Story vom Scan
bekommt danach wieder einen Recherche-Job. Danach die Story im nächsten Export neu schreiben – alle Dokumente sind
dabei.

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
'{"bilder": [{"story_id": 42, "weg": "quelle", "seite_url": "https://…", "alt": "…"}]}' "$RADAR/api/agent/bild?von=claude-research"` (`von`: a–z, 0–9, Bindestrich)
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
