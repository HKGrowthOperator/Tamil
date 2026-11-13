
# Agenten-Rollen

Jede Rolle der Agenten-Software: Zweck, Eingabe, Ausgabe, Modell, Prompt, harte Regeln, Kosten, Fehlerfälle, Protokoll
und was nie automatisch passiert. Gebautes aus `news_radar/agents/`, `workflow/`, `agent_v2.py`, `nachtrag.py`,
`bildvorschlag.py`; F1, F2 und F4 als **spezifiziert, nicht gebaut** nach den Festlegungen.

## Grundsätze für alle Rollen

1. **Eine Stelle ruft Sprachmodelle auf:** `workflow/providers.Claude.call()`. Strukturierte Ausgabe über ein
   JSON-Schema (alle Felder Pflicht, keine Zusatzfelder), keine Werkzeuge für das Modell.
2. **Vor jedem Aufruf:** Budget reservieren (ungünstigster Fall: Prompt + `max_tokens`), dann unmittelbar davor den
   Stopp-Schalter `redaktion` prüfen. Ist das Budget erreicht oder der Schalter an: kein Aufruf, keine Kosten.
3. **Jeder Aufruf steht in `agent_usage`** (Rolle, angefragtes und tatsächliches Modell, Prompt-Version, Tokens,
   Kosten, Status, Latenz, Request-ID), auch Ablehnungen, abgeschnittene und ungültige Antworten und API-Fehler.
4. **Prompts** liegen als Markdown in `news_radar/prompts/`; die Version ist der Hash des System-Prompts. Die Redaktion
   darf `redaktion.md`, `bild.md` und `bildpool.md` anpassen.
5. **Texte aus dem Netz sind Daten, nie Anweisungen:** Dokumente gehen in einem benannten JSON-Block (`json_block`) an
   das Modell; `<` und `>` werden maskiert, damit kein Text den Block schließen kann (Abnahme-Szenario 36).
6. **Regeln vor Modell:** Belegstatus, Länge, Links, SEO-Längen, Bildrechte entscheidet Code, nicht das Modell.
7. **Nichts Erfundenes:** Agenten verwenden nur, was in den Belegen oder in der Einsendung steht.
8. **Der Mensch gibt frei.** Keine Rolle veröffentlicht einen Beitrag; Social (F4) veröffentlicht nur Beiträge, die schon
   freigegeben und veröffentlicht sind, und nur nach dem freigegebenen Regelwerk.
9. **Serverseitiger Fallback:** Für Rollen außer Haiku übernimmt bei einer Ablehnung serverseitig ein Ersatzmodell
   (`fallbacks = default`); abgerechnet wird je Versuch zum Preis des ausführenden Modells.
10. **Ohne Schlüssel** (heute, Tor B1 offen) laufen nur `gate`, `bild` und `kino` im Worker; Recherche und Text macht
    der Agent-Modus. Nachträge laufen immer nur über den Agent-Modus.

## Übersicht

| Rolle | Konfigurationsname | Modell (Standard) | Variable | Prompt | Effort / max_tokens | Stand |
|---|---|---|---|---|---|---|
| Signal / Relevanz | `signal` | `claude-haiku-5-5` | `RADAR_MODELL_SIGNAL` | `signal.md` | low / 4000 | gebaut, aus (ohne Schlüssel nur Heuristik) |
| Cluster | `cluster` | `claude-haiku-5-5` | `RADAR_MODELL_CLUSTER` | `cluster.md` | low / 2000 | Regeln live; Modell aus |
| Recherche | `recherche` | `claude-sonnet-5-5` | `RADAR_MODELL_RECHERCHE` | `recherche.md` | medium / 12000 | gebaut, aus |
| Gate | – (Regeln) | kein Modell | – | – | – | live |
| Nachrecherche | `nachrecherche` | kein Modell (Provider `suche`, 0 $) | – | – | – | gebaut, läuft auch ohne Schlüssel |
| Prüfer (zweite KI) | `pruefer` | `claude-opus-5-5` (stärkstes der Konfiguration) | `RADAR_MODELL_PRUEFER` | `pruefer.md` | high / 16000 | gebaut, aus (ohne Schlüssel: Satzprüfung der Research-Sitzung) |
| Text | `text` | `claude-sonnet-5-5` | `RADAR_MODELL_TEXT` (Alias `RADAR_MODEL`) | `redaktion.md` + `text.md` + Stilbeispiele | medium / 16000 | gebaut, aus |
| Faktencheck | `faktencheck` | `claude-sonnet-5-5` | `RADAR_MODELL_FAKTENCHECK` | `faktencheck.md` | medium / 12000 | gebaut, aus |
| Lektorat | `lektorat` | `claude-haiku-5-5` | `RADAR_MODELL_LEKTORAT` | `redaktion.md` + `lektorat.md` | low / 4000 | Regeln live; Modell aus |
| SEO | `seo` | `claude-haiku-5-5` | `RADAR_MODELL_SEO` | `seo.md` | low / 3000 | Regeln live; Modell aus |
| Medien / Bild | `bild` | `gemini-nano-banana-2.1` | `BILD_MODELL`, `BILD_GROESSE`, `RADAR_KI_BILDER_JE_ARTIKEL` | `bild.md`, `bildpool.md` | – | Kette live (Karte, Archiv, Quelle); KI und Stock aus |
| Dossier | `dossier` | `claude-opus-5-5` | `RADAR_MODELL_DOSSIER` | `redaktion.md` + `text.md` | high / 32000 | gebaut, aus |
| Kino-Vorlage | `kino` | kein Modell (`vorlage`) | – | – | – | live |
| Agent-Modus | `agent` | Claude-Code-Sitzung (`claude-code`, 0 $ in `agent_usage`) | `RADAR_AGENT_TOKEN` | Export-Anleitung `ANLEITUNG_V2`, `redaktion.md`, `.claude/skills/radar-research` | – | live |
| Nachtrag | – | kein Modell | `RADAR_AGENT_TOKEN`, `RADAR_NACHTRAG_TAG` | – | – | live |
| Bild mit Nachweis | – | kein Modell | `RADAR_AGENT_TOKEN` | – | – | live |
| Eingang (F1) | `eingang` (Vorschlag) | zu prüfen (Vorschlag Haiku) | `RADAR_MODELL_EINGANG` (Vorschlag) | `eingang.md` (neu) | – | spezifiziert |
| Verzeichnis (F2) | `verzeichnis` (Vorschlag) | Haiku nur für den Kategorie-Vorschlag (Vorschlag) | `RADAR_MODELL_VERZEICHNIS` (Vorschlag) | `verzeichnis.md` (neu) | – | spezifiziert |
| Social (F4) | `social` (Vorschlag) | kein Modell (Text aus Titel und Vorspann) | – | – | – | spezifiziert, in Bau |

Budget gilt für alle bezahlten Rollen gemeinsam: `RADAR_BUDGET_TAG_USD`, `RADAR_BUDGET_MONAT_USD`, Warnung bei
`RADAR_BUDGET_WARNUNG`; Pilot-Grenze `RADAR_ENTWUERFE_TAG` neue bezahlte Storys je Tag (Kino zählt nicht). Bei
Erreichen: neue bezahlte Jobs warten (`wartet_budget`), Freigabe und Übertragung laufen weiter.

---

## Signal / Relevanz (`agents/relevance.py`)

- **Zweck:** Meldungen aussortieren, bevor Geld und Zeit in sie fließen.
- **Eingabe:** Meldungen eines Scans; zuerst die Heuristik (`filtering.select`: Stichwort-Punkte, DACH-Bezug,
  Ausland-Regel, Alter, Sperrlisten, Termin-Alter). Nur die **Grauzone** (bis 2 Punkte unter der Schwelle) geht an
  das Modell, gebündelt zu höchstens 10 je Aufruf; nur solange heute weniger bezahlte Storys als
  `RADAR_ENTWUERFE_TAG` angelegt sind.
- **Ausgabe:** je Meldung `nr`, `relevanz` (1–10), `land` (DE/AT/CH/leer), `grund` (ein Satz), `risiko` (`keins`,
  `sensibel`, `fragwuerdig`). Angenommen ab `RADAR_MIN_RELEVANCE` (6). `risiko = sensibel` setzt `stories.sensibel`.
- **Harte Regeln:** Ausschlussliste, Gedenktermin-Sperre und Ausland-Regel entscheidet die Heuristik, nie das Modell.
- **Kosten:** ein gebündelter Haiku-Aufruf je Grauzone-Bündel.
- **Fehlerfälle:** Modell fällt aus → Grauzone bleibt liegen, Scan läuft weiter; nur vom Modell wirklich beurteilte
  und abgelehnte Meldungen gelten als gesehen (`seen.status = irrelevant`).
- **Protokoll:** `agent_usage` (Rolle `signal`), Laufnotiz (`grauzone`, `grauzone_angenommen`).
- **Nie automatisch:** keine Story ohne Vorfilter oder Signal-Annahme.

## Cluster (`agents/cluster.py`)

- **Zweck:** erkennen, ob eine Meldung zu einer bestehenden Story gehört.
- **Eingabe:** ausgewählte Meldungen, Storys der letzten 7 Tage.
- **Reihenfolge (billig vor teuer):** gleiche URL/UID → Kino-Schlüssel (Film + Kinowoche) → Event-Schlüssel (Datum +
  Stadt + Titelwörter) → gleicher Termin (Datum, Titelkern, verträglicher Ort) → Titelähnlichkeit: ≥ 0,82 gleiche
  Story; 0,55–0,82 Grenzfall ans Modell.
- **Ausgabe:** je Grenzfall `gleiche_story` (ja/nein), `grund`. Gleiche Story → neues Dokument an der Story
  („angereichert“), Story mit Status `recherche_erforderlich` oder `fehler` startet neu (nur ohne offenen Job – eine
  laufende Nachrecherche liest das neue Dokument ohnehin); eine mangels Beleg verworfene Story (Notiz „Zweite KI:
  verworfen …“) wird wieder zugeordnet und startet ebenfalls neu; offene Entwürfe bekommen einen Hinweis und die Quelle
  in `weitere_quellen`.
- **Kosten:** ein gebündelter Haiku-Aufruf je Scan mit Grenzfällen.
- **Fehlerfälle:** Modell fällt aus oder antwortet nicht `ok` → Grenzfälle werden neue Storys (lieber doppelt als
  falsch zusammengelegt).
- **Protokoll:** `agent_usage`, `log` `story_angereichert`.

## Recherche (`agents/research.py`)

- **Zweck:** Belege sammeln und eine Faktenmatrix (Claims) ziehen; kein Artikel.
- **Eingabe:** Story; Python lädt den Volltext der Primärquelle (über `net.safe_get`, ab `VOLLTEXT_MIN` Zeichen →
  `art = volltext`, `primaer = 1`), nimmt die Meldungen des Clusters dazu und sucht bei Nachrichten und Dossiers mit
  weniger als zwei Verlagen bis zu drei Hinweise über Google News (`art = hinweis`, nur Titel; abschaltbar mit
  `RADAR_RECHERCHE_GOOGLE_NEWS=0`).
- **Vorab-Regel:** Ein Termin, der laut Quelle schon vorbei ist, wird vor jedem bezahlten Aufruf verworfen.
- **Ausgabe:** `claims[]` (`id`, `aussage`, `art`, `kern`, `quellen`, `fundstelle`, `sicherheit`),
  `widersprueche[]` (`claim_ids`, `beschreibung`), `fehlende_angaben[]`.
- **Harte Regeln:** Claims ohne gültige Dokument-Kennung oder mit doppelter ID werden verworfen (`validate_refs`) und
  als Hinweis vermerkt.
- **Kosten:** ein Sonnet-Aufruf je Story (Dossier ebenso).
- **Fehlerfälle:** Antwort nicht `ok` → Job-Fehler → Wiederholung 1/5/30 Min. → nach 3 Versuchen `tot`, Story `fehler`.
- **Protokoll:** `agent_usage` (Rolle `recherche`), Dokumente und Claims in der Datenbank.
- **Nie automatisch:** keine Quelle aus einem Vorschlag ungeprüft übernehmen; Text kommt immer vom Abruf.

## Gate (`agents/factcheck.gate`, kein Modell)

- **Zweck:** vor dem Schreiben entscheiden, ob die Belege einen Beitrag tragen.
- **Eingabe:** Story, Dokumente, Claims, Widersprüche.
- **Regeln:** Belegstatus je Claim: `widerspruch` bei gemeldetem Widerspruch; `bestaetigt`, wenn die Aussage in einer
  Primärquelle (Volltext, Veranstalter, strukturierte Daten) oder in zwei verschiedenen Verlagen steht und die
  Fundstelle wirklich im Dokument vorkommt; `einzelquelle`; `unbestaetigt` bei reinen Hinweisen. Jede Kernaussage
  muss bestätigt sein; Termine brauchen bestätigtes Datum (`wann`) und bestätigten Ort (`wo`). Länge nach Stofflage:
  < 4 bestätigte Aussagen kurz, 4–7 mittel, ≥ 8 aus zwei Verlagen oder Primärquelle mit Volltext lang; ohne Volltext
  nie mehr als knapp. Sensibel-Wortliste (Politik, Gericht, Gesundheit, Tod, Kinder) setzt den Hinweis „zweite Person“.
- **Ausgabe:** `ok`, bewertete Claims, `laenge`, `sensibel`, `gruende`, `hinweise`.
- **Fehlerfälle:** nicht ok → Story `recherche_erforderlich` mit Gründen und Job `nachrecherche` (siehe unten); nach
  zwei Runden entscheidet die zweite KI. Im Cockpit „In Nachrecherche“; niemand muss Quellen von Hand einfügen.
- **Nie lockern,** um einen Test grün zu bekommen (`.claude/rules/radar.md`).

## Text (`agents/schreiben.py`)

- **Zweck:** den Beitrag im Tamil.de-Stil aus bestätigten Claims schreiben.
- **Eingabe:** nur Claims mit `support = bestaetigt`, Quellenliste, Längenregel, Stilbeispiele passend zu Typ und
  Rubrik (`stilbeispiele.py`), Redaktionsprofil `redaktion.md`, Kategorien, Bildthemen; in Runde 2 die Anmerkung des
  Faktenchecks und die vorige Fassung.
- **Ausgabe:** alle Felder des Entwurfs (`relevanz`, `begruendung`, `kategorie`, `typ`, `dach_bezug`, `ort`, `titel`
  ≤ 90, `teaser` ≤ 220, `inhalt_html`, `schlagworte` 3–6, `seo_titel`, `meta_beschreibung`, `bild_suchbegriff`,
  `bild_alt`, `bild_thema`, `bild_prompt`, `event_datum`, `event_ort`, `ticket_url`) plus `belege[]` (je Absatz die
  Claim-IDs).
- **Harte Regeln:** Länge nach Gate (Wörter: kurz 80–150, normal 250–400, lang 450–750, Event/Kino 150–250, mittel
  250–400, lang 350–550, Dossier 600–1000). Links im Text nur, wenn ihre Adresse in den Dokumenten der Story steht;
  andere entfernt der Code. Kein Allgemeinwissen, keine Vermutung, kein ausgedachtes Zitat.
- **Kosten:** ein Sonnet-Aufruf je Runde, höchstens zwei Runden.
- **Fehlerfälle:** Antwort nicht `ok` → Job-Fehler mit Wiederholung.
- **Protokoll:** `agent_usage`, Fassung `text` bzw. `ueberarbeitung`.

## Faktencheck (`agents/factcheck.text_pruefen`)

- **Zweck:** den fertigen Text Satz für Satz gegen die Belege prüfen; schreibt nichts um.
- **Ausgabe:** je Satz `urteil` (`gedeckt`, `ungedeckt`, `widerspruch`, `kein_fakt`), `claim_ids`, `fundstelle`,
  `kern`.
- **Regeln:** Widerspruch oder ungedeckter Kernsatz in Runde 1 → genau eine Überarbeitung durch „Text“; in Runde 2 →
  Nachrecherche (nach Kurzmeldung oder Endprüfung: verworfen mit Grund). Ungedeckte Nebensätze streicht am Ende die
  zweite KI (Endprüfung) in jedem Fall.
- **Kosten:** ein Sonnet-Aufruf je Runde.
- **Fehlerfälle:** Antwort nicht `ok` → Job-Fehler mit Wiederholung.
- **Protokoll:** `agent_usage`, Fassung `faktencheck` mit allen Satzurteilen (im Cockpit sichtbar).

## Nachrecherche (`agents/nachrecherche.py`, kein Modell)

- **Zweck:** Auftrag Luis vom 13.11.2026 – keine Story bleibt auf „Recherche nötig“ stehen, keine Links von Hand. Scheitert
  das Gate (oder der Faktencheck in Runde 2, oder ein Agent-Import), sucht der Radar selbst Belege für die Fehlstellen.
- **Eingabe:** Story, Dokumente, Claims; Fehlstellen aus den Gründen des Gates (Datum, Ort, zweite Quelle, Klärung eines
  Widerspruchs, Bericht mit Volltext) und `fehlende_angaben` der Recherche.
- **Suchanfragen:** höchstens vier aus Titel (ohne „- Verlag“), Titel + Ort, Personen + Ort, Titel + Fehlstelle.
- **Wege (in dieser Reihenfolge):** `dokumente` (Adressen, die in den Dokumenten genannt sind, z. B. die Seite des
  Veranstalters), `hinweis` (Hinweis-Dokumente mit direkter Adresse ohne Text), `register` (Meldungen registrierter
  Quellen aus den letzten 30 Tagen in `seen`; Suche der registrierten WordPress-Quellen `wp_json`/`tribe_events`),
  `bildquellen` (Startseite eines Betreibers aus dem Bildquellen-Register, wenn Hostname oder zwei eigene Namenswörter
  zur Story passen), `suche` (Google-News-RSS: Google-Adressen bleiben Hinweise, nie Beleg; direkte Adressen werden
  gelesen).
- **Harte Regeln:** alles über `ctx.text_von`/`ctx.json_abruf` (`net.safe_get`, Stopp-Schalter vor jedem Abruf); nie
  soziale Netzwerke (`SOZIAL`); keine Paywall (Register `paywall = true` oder Paywall-Text auf der Seite); angehängt nur
  mit ≥ `VOLLTEXT_MIN` Zeichen und passend (Ort und ein Titelwort oder zwei Titelwörter) als `volltext`, `primaer`;
  höchstens 8 Seiten gelesen und 4 neue Belege je Runde, höchstens zwei Runden je Story. Ob eine Aussage damit
  bestätigt ist, entscheidet wie immer das Gate (wörtliche Fundstelle).
- **Danach:** Neues gefunden → Recherche und Gate erneut; nichts gefunden oder zwei Runden vorbei → zweite KI
  (`pruefung`). Ohne Modell (Agent-Modus) → Recherche-Job, die Story steht mit Fehlstellen und Suchanfragen im Export
  (Liste `nachrecherche`). Nachträge: nur die Suche, danach Export.
- **Kosten:** keine Modellkosten; je Runde eine Zeile in `agent_usage` (Rolle `nachrecherche`, Provider `suche`, 0 $).
  Die folgenden Modellaufrufe (Recherche, Prüfer) laufen über die Budget-Reservierung wie alle anderen.
- **Protokoll:** `log` `nachrecherche` (Runde, Fehlstellen, Anfragen, neue Belege, Wege, Ablehnungen, Ergebnis),
  `stories.notiz`, Hinweis im Entwurf „Nachrecherche Runde n von 2: …“.

## Prüfer – zweite KI (`agents/pruefer.py`, Rolle `pruefer`)

- **Zweck:** unabhängige Prüfung aus frischem Kontext (kennt nur Dokumente, Claims und Text, nicht die Begründungen
  von Recherche und Schreiber) – Auftrag Luis vom 13.11.2026, auch wenn es mehr kostet.
- **(a) Nach der Nachrecherche** (`pruefung`): `schreiben` (nur aus bestätigten Claims, notfalls Kurzmeldung) oder
  `verwerfen` mit Grund. Der Code entscheidet mit: eine Kurzmeldung braucht mindestens eine bestätigte Kernaussage,
  keinen Widerspruch in einer Kernaussage und bei Terminen bestätigtes Datum und bestätigten Ort
  (`kurzmeldung_regel`) – die zweite KI kann nur strenger sein. Unbestätigte Kernaussagen werden zu Nebenaussagen
  (`kern = false`) und kommen nicht in den Text (Hinweis „Nicht im Text, weil nicht belegt“); Länge `kurz` (Termine
  `event`).
- **(b) Vor „neu im Cockpit“** (`endpruefung`, nach SEO): jeder Satz gegen die Dokumente (`gedeckt`, `ungedeckt`,
  `widerspruch`, `kein_fakt`, `kern`). Ungedeckte Nebensätze – und die, die der Faktencheck nicht gedeckt fand – werden
  gestrichen (Hinweis „Zweite KI hat gestrichen“); eine ungedeckte Kernaussage oder ein Satz, der sich nicht sicher
  streichen lässt, heißt einmal Überarbeitung, danach verworfen. Bleiben weniger als 25 Wörter, kein Entwurf.
- **Ausgabe im Entwurf:** Hinweis „Geprüft von zweiter KI (Modell): n Sätze gegen die Dokumente geprüft, …“; Fassung
  `pruefung` mit allen Satzurteilen.
- **Kosten:** ein Aufruf mit dem stärksten Modell je Story nach der Nachrecherche und je Entwurf (bei Überarbeitung
  zwei); Budget über die Reservierung, `agent_usage` Rolle `pruefer`.
- **Fehlerfälle:** Antwort nicht `ok` → Job-Fehler mit Wiederholung; höchstens drei `pruefung`-Jobs je Story.

## Lektorat (`agents/copydesk.py`)

- **Zweck:** Hinweise für die Redaktion; schreibt den Text nicht um.
- **Regeln (immer, ohne Modell):** Wortzahl gegen die Längenregel; Zahlen ohne Beleg; Nähe zum Quelltext (höchstens 12 %
  gleiche 8-Wort-Folgen); Tabu-Wendungen (z. B. „klicken Sie“, Superlative, Boulevard-Wörter); bekannte Rubrik;
  Quellenzeile; lange Texte ohne Zwischenüberschrift.
- **Modell (wenn Budget da ist):** Hinweise zu Sprache, Stil, Verständlichkeit, Ton, Fakten (höchstens 12).
- **Fehlerfälle:** Budget erreicht → „Lektorat übersprungen“; Antwort nicht `ok` → keine Modell-Hinweise, der Ablauf
  läuft weiter.
- **Protokoll:** `agent_usage`, Fassung `lektorat`, Hinweise am Entwurf.

## SEO (`agents/seo.py`)

- **Zweck:** Angaben für Suchmaschinen.
- **Regeln:** SEO-Titel ≤ 60, Meta-Beschreibung 120–155 (gekürzt bzw. Hinweis), Alt-Text ≤ 125, Slug aus dem Titel;
  interne Links nur auf bestehende Beiträge (Suche in WordPress).
- **Modell:** `fokus_keyword`, `seo_titel`, `meta_beschreibung`, `bild_alt`. Fällt es aus, gelten nur die Regeln.
- **Hinweis:** An WordPress geht als Fokus das erste Schlagwort, nicht das Fokus-Keyword der Rolle (zu prüfen).
- **Protokoll:** `agent_usage`, Fassung `seo`.

## Medien / Bild (`agents/media.py`, `bilder.py`, `images.py`)

- **Zweck:** jedes Beitragsbild mit Lizenz-Datensatz; kein Beitrag ohne Bild.
- **Reihenfolge** (`BILD_REIHENFOLGE`): Archiv (eigene lizenzierte Bilder, Ablauf beachtet) → Pressebild der Quelle (nur
  `bild_nutzen = true`) → Stockfoto (Unsplash/Pexels mit Schlüssel) → Bildpool (Reserve-Symbolbilder) → KI-Symbolbild
  (Gemini, höchstens 1 je Story, nur mit Budget) → Tamil.de-Bildkarte (immer möglich).
- **Ausgabe:** Datei, `assets`-Datensatz (Rechteinhaber, Lizenz, Umfang, Nachweis, Ablauf, KI), Felder am Entwurf.
- **Harte Regeln:** KI-Bilder sind Symbolbilder und tragen den Hinweis; keine realen Personen, kein Text im Bild
  (`bild.md`). Ein Bild ohne Datensatz wird nie verwendet. Vor Abrufen nach außen gilt der Stopp-Schalter.
- **Kosten:** Bild-KI nach `costs.BILD_PREISE`, Zeile in `agent_usage` (Provider `gemini`, Rolle `bild`).
- **Fehlerfälle:** jeder Ausfall fällt eine Stufe weiter bis zur Bildkarte; bricht der Schritt nach dem Speichern ab,
  werden Datei und Datensatz wieder entfernt.

## Dossier (Rolle `dossier`)

- **Zweck:** auf Anforderung der Redaktion („Als Dossier recherchieren“, Recht `dossier`) ein langer Beitrag aus allen
  Quellen eines Entwurfs.
- **Ablauf:** neue Story `typ = dossier` mit allen Dokumenten, Priorität 0; dann derselbe Weg wie oben, Text mit Opus,
  Länge 600–1000 Wörter.
- **Nie automatisch:** Ein Dossier entsteht nur durch eine Person.

## Kino-Vorlage (`orchestrator.kino_text`, kein Modell)

- **Zweck:** Kinoprogramm-Beitrag je Film und Kinowoche.
- **Eingabe:** `kino_fakten` (Film, Woche, Kinos mit Stadt, Land, Terminen).
- **Ausgabe:** fester Text (Titel, Anriss, drei Absätze, Quellenzeile), Kinoliste hängt `render.py` an; Hinweis
  „Kino-Vorlage ohne KI: Besetzung und Handlung bei Bedarf ergänzen“.
- **Kosten:** 0 $; Zeile in `agent_usage` mit Provider `vorlage` (Abnahmekriterium K7: kein Modellaufruf für Kino).

## Agent-Modus (Redakteur-Sitzungen) (`agent_v2.py`, `web/api.py`)

- **Zweck:** Recherche und Text durch eine Claude-Code-Sitzung (Agent `redakteur`, Skill `radar-research`), solange
  kein API-Schlüssel gesetzt ist (Entscheidung 12.11.2026) – mit denselben Gates.
- **Zugang:** `Authorization: Bearer $RADAR_AGENT_TOKEN`; ohne gesetztes Token gibt es die Endpunkte nicht (404).
  Jede Route prüft den Schalter `redaktion` (409 bei Stopp).
- **Export** `GET /api/agent/export`: `?limit=N` (höchstens 20), `?ids=3,4,5` (höchstens 20, nur Ziffern),
  `?nur=uebersicht` (bis 200 Storys ohne Dokumente). Inhalt: Story, Dokumente mit Volltext, Regeln für Recherche, Gate,
  Länge (`staffel`), Anleitung.
  Storys in Nachrecherche stehen in der eigenen Liste `nachrecherche` mit `runde`, `letzte_runde`, `fehlend`,
  `suchanfragen`, `gruende` und dem `ergebnis` der letzten Runde; die Übersicht markiert sie mit `nachrecherche: true`.
- **Import** `POST /api/agent/import`: `{"ergebnisse": [{story_id, claims, widersprueche, beitrag, pruefung} |
  {story_id, verwerfen} | {story_id, neue_quellen}]}` – nur diese drei Ergebnisse; ein Eintrag nur mit Fehlstellen wird
  abgelehnt, nichts geändert. Der Radar prüft selbst: Story aus dem Export und offen; `validate_refs`; **Gate** wie im
  Worker; jeder Absatz braucht Belege aus bestätigten Claims; scheitert das, geht die Story in die Nachrecherche
  (höchstens zwei Runden), danach Kurzmeldung aus bestätigten Claims (Regeln wie beim Prüfer) oder verworfen mit Grund.
  `neue_quellen` (höchstens 5): der Radar liest jede selbst, nie soziale Netzwerke, keine Google-Adressen, keine
  Paywall, nur mit genug Text; die Story bleibt danach im Export. `pruefung` (`von`, `saetze[]`): Satzprüfung einer
  zweiten KI aus frischem Kontext (eigener Agent der Sitzung); ungedeckte Nebensätze werden gestrichen, eine ungedeckte
  Kernaussage schickt die Story in die Nachrecherche; ohne `pruefung` trägt der Entwurf den Hinweis „Ohne zweite
  KI-Prüfung“. Links nur auf Story-Quellen; Lektorat- und SEO-Regeln; Bildkette; Entwurf mit Hinweis „Agent-Modus“.
  Nachtrag-Entwürfe höchstens `RADAR_NACHTRAG_TAG` je Tag.
- **Kosten:** in `agent_usage` als Provider `claude-code`, Rolle `agent`, 0 $ (die Sitzung rechnet über das Abo ab).
- **Protokoll:** `agent_usage`, `log` `agent` (geschrieben/verworfen), `editorial_actions` (Auslöser `agent`).
- **Nie automatisch:** Freigabe, Veröffentlichung; der Agent kann keine Gate-Regel umgehen.

### Nachtrag (`nachtrag.py`, `POST /api/agent/vorschlag`)

- **Zweck:** Rückblick-Storys aus einem Vorschlag mit Quellen (Entscheidung 11.11.2026), ohne Scan, ohne Modell.
- **Eingabe:** höchstens 5 Vorschläge je Web-Aufruf (CLI 100): `arbeitstitel`, `datum`, `rubrik`, `ort`, `bezug`,
  `heikel`, 1–6 `quellen`, optional `kernfakten`, `bild_hinweis` (nur Hinweise, nie Belege), `erzwingen`; optional
  `story_id` zum Ergänzen – seit 13.11.2026 für jede Story in `recherche_erforderlich` ohne Entwurf und ohne laufenden
  Job, egal ob Herkunft `nachtrag` oder `radar` (Storys vom Scan bekommen danach wieder einen Recherche-Job).
- **Regeln:** Der Radar ruft jede Quelle selbst ab (HTML ≤ 3 MB; PDF ≤ 8 MB, ≤ 40 Seiten, eigener Prozess mit
  Zeit- und Speichergrenze); Titel und Text nie aus dem Vorschlag. Kurze Felder (dt/dd, th/td, „Label: Wert“, z. B.
  Filmstart, Regie, Besetzung auf Kinoseiten) kommen wörtlich als „Kurzangaben der Seite“ dazu; JSON-LD von Termin und
  Film nur, wenn es zur Seite gehört (genau eines oder Name passt zu Titel bzw. kanonischer Adresse). `neu_abrufen`
  ersetzt nur das Dokument genau dieser Adresse – bei einer Umleitung nichts („umgeleitet, nicht ersetzt“); der alte
  Stand bleibt als Fassung `quelle_vorher`, die Claims der Story werden gelöscht. Dublettenprüfung und Anlegen in einer
  Schreibtransaktion. Ergebnis je Vorschlag: `angelegt`, `vorhanden`, `vielleicht_vorhanden`, `abgelehnt`,
  `nicht_bearbeitet`, `ergaenzt`.
- **Veröffentlichung:** Beitrag mit dem Ereignisdatum (12:00) und dem Vermerk „Nachtrag der Redaktion …“ am Ende; nur
  über das Plugin `tamil-radar`.

### Bild mit Nachweis (`bildvorschlag.py`, `POST /api/agent/bild`)

- **Zweck:** ein echtes Bild für einen wartenden Entwurf.
- **Eingabe:** höchstens 5 je Aufruf: `story_id`, `weg` (`commons` oder `quelle`), `seite_url`, optional `bild_url`,
  `alt`.
- **Regeln:** Commons nur gemeinfrei/CC0, CC BY, CC BY-SA (Lizenz aus der Commons-API); `quelle` nur auf Hosts des
  Bildquellen-Registers und nur von Seiten, die Beleg der Story sind; Nachweis aus Register oder Commons, nie aus dem
  Vorschlag; gesperrt: soziale Netzwerke, Bildagenturen, Agenturbilder, Logos, Banner, KI-Bilder.
- **Ergebnis:** `gesetzt`, `abgelehnt`, `nicht_bearbeitet`. Freigabe bleibt beim Menschen.

---

## Eingang (F1) – spezifiziert, nicht gebaut

- **Zweck:** Einsendungen aus den fünf Formularen prüfen und vorbereiten (B1.2).
- **Eingabe:** abgeholte Einsendung (alle Felder, ohne Kontaktdaten an das Modell – Vorschlag, zu prüfen), bestehende
  Termine und Einsendungen für die Dublettenprüfung.
- **Regeln (ohne Modell):** Pflichtfelder vollständig; Datum plausibel und in der Zukunft; Ort in DE/AT/CH; Dublette
  (gleicher Termin oder gleiche Einsendung).
- **Modell (zu prüfen):** kurze interne Zusammenfassung; bei Event und Beitrag ein Entwurf **ausschließlich aus den
  eingesandten Angaben**, mit Vermerk „Angaben des Einsenders, ungeprüft“.
- **Ausgabe:** Hinweise (`unvollständig`, `Datum in der Vergangenheit`, `Ort außerhalb`, `mögliche Dublette` mit Verweis),
  Zusammenfassung, Entwurf.
- **Harte Regeln:** ergänzt nichts, was nicht in der Einsendung steht; entscheidet Unklares nicht, sondern markiert es;
  schreibt nie an den Einsender.
- **Stopp:** Schalter `eingang` vor dem Abholen und vor jedem Modellaufruf; Einsendungen bleiben dann auf der Website.
- **Kosten:** im gemeinsamen Budget; ohne Schlüssel laufen nur die Regeln.
- **Protokoll:** je Vorbereitung eine Zeile (Auslöser `agent`, Kanal `eingang`, Kennung der Einsendung, keine Namen).
- **Nie automatisch:** übernehmen, freigeben, veröffentlichen, ablehnen, jede Antwort.

## Verzeichnis (F2) – spezifiziert, nicht gebaut

- **Zweck:** Verzeichnis-Einsendungen prüfen und zur Freigabe vorschlagen (B1.4).
- **Regeln (ohne Modell):** Pflichtfelder (Name, Art, PLZ, Stadt, Land, mindestens ein Kontaktweg); Form von PLZ,
  Telefon, Website-Adresse; Dubletten (ähnlicher Name und gleiche PLZ, Telefonnummer oder Website); bei Änderungen der
  Unterschied alt ↔ neu je Feld.
- **Modell:** nur der Kategorie-Vorschlag (aus der Kategorienliste von KBS). Ohne Modell entfällt nur dieser.
- **Harte Regeln:** nur Werte, die wörtlich in der Einsendung stehen; nichts aus dem Netz, keine geratenen
  Öffnungszeiten, keine gefüllten Lücken (Fehlendes heißt „fehlt“); Premium nie.
- **Stopp:** Schalter `verzeichnis`.
- **Protokoll:** Zeile je Prüfung (Auslöser `agent`, Kanal `verzeichnis`).
- **Nie automatisch:** Veröffentlichung, Änderung, Premium, Löschen; kein Zusammensuchen von Einträgen.

## Social (F4) – spezifiziert, in Bau

- **Zweck:** aus veröffentlichten Beiträgen und Terminen Social-Beiträge erzeugen und nach Regelwerk veröffentlichen
  (B2.1–B2.4, B3.1).
- **Eingabe:** neu veröffentlichte Beiträge und Termine (auch von Hand in WordPress angelegte), nie Altbestand;
  Regelwerk in der freigegebenen Fassung; Bildrechte des Beitragsbilds.
- **Ausgabe:** Regelprüfung je Regel; Text aus Titel und Vorspann, feste Hashtags je Rubrik, Verweis auf tamil.de;
  Bild 1080 × 1350 (Foto mit Logo-Leiste, Vorschlag) oder Bildkarte; WhatsApp-Entwurf (Text, Link, Bild).
- **Modell:** keins vorgesehen.
- **Harte Regeln:** heikle Themen nie automatisch; Beitrag höchstens 48 Stunden alt; Termine nur in der Zukunft;
  höchstens 6 am Tag, 60 Min. Abstand, Ruhezeit 22–7 Uhr; je Kanal höchstens einmal; Korrekturen lösen nichts aus;
  KI-Bilder gekennzeichnet; nur offizielle Schnittstellen von Meta.
- **Stopp:** `instagram`, `facebook`, `whatsapp`, wirkt sofort, auch während der Karenz.
- **Fehlerfälle:** Abbruch beim Senden → Abgleich mit den letzten Beiträgen des Kontos, bleibt es unklar →
  Mensch; abgelaufener Zugang oder gesperrtes Konto → Kanal pausiert, Grund im Cockpit; nie blind wiederholen.
- **Protokoll:** je Beitrag und Kanal Stand, Zeit, Link, Kennung bei Meta, Fassung des Regelwerks.
- **Nie automatisch:** alles, was eine Regel verletzt oder unklar ist; Änderungen am Regelwerk; Posten im WhatsApp-Kanal;
  Antworten auf Kommentare und Nachrichten.
