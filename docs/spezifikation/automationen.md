
# Automationen

Jeder automatische Ablauf mit Auslöser, freigegebener Regel, Stopp-Schalter, Protokollzeile, Karenz, Wiederholung und
dem, was ein Mensch entscheidet. Grundlage §8 Abs. 1: Automatisch läuft nur, was in freigegebenen, dokumentierten
Regeln steht; Sicherheits-, Fehler- und Ausnahmefälle gehen an einen Menschen; Ausführungen und Freigaben werden
protokolliert.

**Wo die Regeln stehen:** Radar-Redaktion: `docs/vertrag/leistungen.md`, `docs/entscheidungen.md`,
`.claude/rules/radar.md`, Code (`filtering.py`, `agents/factcheck.py`); F0–F4: die Festlegungen (Ja von Luis am
13.11.); Social zusätzlich das Regelwerk mit einmaliger Freigabe durch KBS (`docs/regeln-social.md`, Fassung 1,
Freigabe steht aus).

## Zeitplan des Dienstes

Ein Container (`python -m news_radar dienst`, `news_radar/dienst.py`). Zeiten in Europe/Berlin. Jede Aufgabe läuft als
eigener Prozess mit Timeout und nie doppelt; jeder Lauf steht in `dienst_laeufe`. Eine Aufgabe ruht, solange **alle**
ihre Kanäle angehalten sind (oder „alles“); dann steht `angehalten (<kanal>)` in `dienst_laeufe`. Uhrzeit-Aufgaben
werden nach einem Neustart nicht nachgeholt.

| Aufgabe | Befehl | Takt | Timeout | Kanäle | Zweck | Stand |
|---|---|---|---|---|---|---|
| `web` (Langläufer) | gunicorn, 2 Worker × 4 Threads, Port `$PORT` (3000) | dauernd, Neustart mit Backoff bis 60 s | 120 s je Anfrage | – | Cockpit und API | live |
| `worker` (Langläufer) | `worker` | dauernd, `RADAR_PARALLEL_JOBS` (2) Threads, 5 s Pause bei leerer Schlange | Deadline je Job | `redaktion` (je Job) | Jobs abarbeiten; ohne Schlüssel nur `gate`, `bild`, `kino` | live (nur bei `RADAR_WORKFLOW=v2`; Wert zu prüfen) |
| `scan` | `run` | alle 3 Min. | 300 s | `redaktion`, `website` | Quellen scannen, Storys und Jobs; freigegebene Beiträge nach WordPress | live |
| `digest` | `digest` | täglich 08:00 | 300 s | `alles` | Tageszusammenfassung an den Webhook | gebaut (Webhook zu prüfen) |
| `sicherung` | `sicherung erstellen --ziel /app/data/backup` | täglich 03:00 | 1800 s | keine (läuft auch im Stopp) | Datenbank und Bilder sichern, 14 Tage | live |
| `bildpool` | `bildpool fuellen --anzahl 3 --mit-budget` | montags 04:30 | 1800 s | `redaktion` | Reserve-Bilder über die Bild-KI | gebaut, aus (nur mit `GEMINI_API_KEY`) |
| *Einsendungen abholen* | neu | alle paar Minuten (Vorschlag: im Takt des Scans) | – | `eingang` | F1 | spezifiziert |
| *Verzeichnis abholen und prüfen* | neu | wie Einsendungen | – | `verzeichnis` | F2 | spezifiziert |
| *Social erkennen und senden* | neu | alle paar Minuten (Vorschlag: im Takt des Scans) | – | `instagram`, `facebook`, `whatsapp` | F4 | spezifiziert |
| *Löschfristen* | neu | täglich (Vorschlag: mit der Sicherung) | – | keine | F0, F1, F2 | spezifiziert, nicht gebaut |

In WordPress läuft nichts per Zeitplan; Start und Ende einer Werbebuchung folgen aus dem Datum (F3), nicht aus einem
Job.

## Abläufe im Radar (gebaut)

### A1 Scan der Quellen

| | |
|---|---|
| Auslöser | Dienst `scan`, alle 3 Min. |
| Regel | Quellen-Register (`sources.toml`: `enabled`, `interval_minutes`, `max_items`, Schwellen), Vorfilter (`filtering.select`: Alter `RADAR_MAX_AGE_HOURS` 36, Termin-Alter `RADAR_EVENT_MAX_ALTER_TAGE` 30, Ausland-Regel, Sperrlisten, DACH-Bezug), Pilot-Grenze `RADAR_ENTWUERFE_TAG` |
| Stopp | `redaktion` vor dem Abruf und vor jeder Meldung (ganz oder gar nicht); Unverarbeitetes bleibt ungesehen |
| Protokoll | `runs` (Zählwerte, Laufnotiz), `log` (`story_angereichert`, `tageslimit`, `kino_aktualisiert` …), `source_status` |
| Karenz | – |
| Wiederholung | nächster Lauf; Quellen mit Fehlern pausieren (`paused_until`) |
| Mensch | nichts; Quellen ein- und ausschalten nur über das Repo |

### A2 Story und Jobs anlegen

| | |
|---|---|
| Auslöser | Scan: neue Meldung ohne passende Story |
| Regel | Cluster-Reihenfolge; Termine in der Vergangenheit werden nicht angelegt; Priorität 30/20/10 |
| Stopp | `redaktion` |
| Protokoll | `seen.status = story`; Jobs `recherche` (bzw. `kino`) idempotent |
| Wiederholung | – (idempotente Schlüssel) |
| Mensch | „Story verwerfen“, „Quelle ergänzen“ |

### A3 Anreichern und Neustart

| | |
|---|---|
| Auslöser | Scan: Meldung gehört zu einer bestehenden Story |
| Regel | neues Dokument an der Story; Story in `recherche_erforderlich`/`fehler` startet neu; offener Entwurf bekommt Hinweis und Quelle |
| Stopp | `redaktion` |
| Protokoll | `log` `story_angereichert` |
| Mensch | entscheidet über den Entwurf wie sonst |

### A4 Jobs abarbeiten (Redaktion v2)

| | |
|---|---|
| Auslöser | Worker: fällige Jobs nach Priorität |
| Regel | Kette `recherche → gate → schreiben → faktencheck → lektorat → seo → bild`; Kino `kino`; Gate-Regeln; höchstens zwei Text-Runden |
| Stopp | `redaktion` bei der Übernahme eines Jobs und unmittelbar vor jedem Aufruf nach außen (Modell, Abruf, Suche); mitten im Schritt: Job zurück, Versuch zählt nicht |
| Protokoll | `agent_usage` je Aufruf; `article_versions` je Fassung; `log` (`entwurf`, `verworfen`, `recherche_erforderlich`, `angehalten`, `budget`, `fehler`) |
| Karenz | – |
| Wiederholung | nach 1, 5, 30 Min.; nach 3 Versuchen `tot` (Story `fehler`); Budget: `wartet_budget`, nach 15 Min. erneut; abgelaufene Deadline: zurück in die Schlange |
| Mensch | „Erneut“ bei toten Jobs (admin); „Quelle ergänzen“; jeder Entwurf wartet auf Freigabe |

### A5 Budget

| | |
|---|---|
| Auslöser | jeder bezahlte Aufruf |
| Regel | Reservierung des ungünstigsten Falls; Summe aus Kosten und Reservierungen ≤ Tages- und Monatsgrenze; Reservierungen verfallen nach 60 Min. |
| Stopp | eigener harter Stopp, unabhängig von den Schaltern |
| Protokoll | `budget_reservierungen`, `agent_usage`; Warnung bei 80 % an den Webhook |
| Mensch | Grenzen über Coolify-Variablen; Freigabe laufender Kosten durch KBS (§3 Abs. 2, Tor B1) |

### A6 Übertragung freigegebener Beiträge nach WordPress

| | |
|---|---|
| Auslöser | im Lauf `scan` nach dem Scan (`publish_approved`, höchstens 10 je Lauf, älteste Freigabe zuerst) |
| Regel | nur Status `freigegeben`, atomar reserviert (`wird_veroeffentlicht`); `WP_POST_STATUS` (`publish`); Dublette über `radar_uid` (409) → übernommen, bei Kino Kinoliste aktualisiert |
| Stopp | `website` vor dem Lauf und unmittelbar vor dem ersten Aufruf je Beitrag; mitten im Lauf gehen die übrigen zurück auf `freigegeben` |
| Protokoll | `editorial_actions` `veroeffentlicht` (Auslöser `dienst`, Kanal `website`); bei Stopp einmal je Stopp und Entwurf `zurueckgehalten` mit dem Schalter als Grund; `log` `veroeffentlicht`/`fehler` |
| Karenz | keine; freigegeben heißt: beim nächsten Lauf (≤ 3 Min.) |
| Wiederholung | keine automatische: WordPress-Fehler → Status `fehler`; „Erneut“ durch eine Person |
| Mensch | Freigabe (nur mit gesehenem `stand`), „Direkt posten“, „WordPress-Entwurf“ |

### A7 Kino-Aktualisierung

| | |
|---|---|
| Auslöser | Scan mit neuen Kinoprogrammen |
| Regel | offener Entwurf: Spielorte vereinigen (nur aktive Quellen, künftige Termine), nur solange der Entwurf wartet und auf dem Stand ist, von dem gerechnet wurde; veröffentlichter Beitrag: Kinoliste per `PUT` |
| Stopp | `redaktion` (Scan), `website` (Aktualisierung in WordPress) |
| Protokoll | `log` `kino_aktualisiert`, `kino_update_ignoriert`, `aktualisiert` |
| Mensch | nichts; Kino-Entwürfe brauchen wie alle eine Freigabe |

### A8 Agent-Modus, Nachtrag, Bild mit Nachweis

| | |
|---|---|
| Auslöser | Aufruf einer Claude-Code-Sitzung mit `RADAR_AGENT_TOKEN` (Mensch startet die Sitzung, z. B. `/research`) |
| Regel | Gates wie im Worker; Grenzen 20 Storys je Export, 5 Vorschläge bzw. Bilder je Web-Aufruf, `RADAR_NACHTRAG_TAG` Nachtrag-Entwürfe je Tag |
| Stopp | `redaktion` (409) |
| Protokoll | `agent_usage` (Provider `claude-code`), `log` `agent`, `nachtrag`, `bild`; `editorial_actions` mit Auslöser `agent` |
| Mensch | startet die Sitzung, gibt jeden Entwurf frei |

### A9 Digest und Benachrichtigungen

| | |
|---|---|
| Auslöser | Digest täglich 08:00; Hinweis bei jedem neuen Entwurf; Budgetwarnung |
| Regel | nur an `NOTIFY_WEBHOOK_URL`; ohne Variable nichts; nie E-Mail (§8 Abs. 2) |
| Stopp | Digest ruht bei `alles` |
| Protokoll | `dienst_laeufe` (Digest) |
| Mensch | – |

### A10 Sicherung

| | |
|---|---|
| Auslöser | täglich 03:00 |
| Regel | SQLite-Backup-API (WAL-sicher) und Bilder; 14 Tage aufbewahren (F0 schlägt 30 vor) |
| Stopp | keiner (läuft auch im Stopp) |
| Protokoll | `dienst_laeufe` |
| Mensch | Wiederherstellung nur von Hand (`sicherung wiederherstellen`, prüft Integrität, legt den alten Stand beiseite) |

### A11 Aufräumen

| Was | Wann | Stand |
|---|---|---|
| hängende Jobs (Deadline) | bei jeder Runde des Workers | live |
| abgelaufene Budget-Reservierungen | zählen nach 60 Min. nicht mehr | live |
| abgelaufene Sitzungen | bei jeder Anmeldung | live |
| verwaiste Bilddateien | beim Anlegen eines Entwurfs | live |
| Protokoll (12 Monate), Einsendungen (90 Tage, Spam 7 Tage), Verzeichnis-Einsender (90 Tage), IP-Hash (24 Stunden) | täglich | spezifiziert, nicht gebaut |

## Abläufe in WordPress (gebaut)

| Ablauf | Auslöser | Regel | Schalter | Stand |
|---|---|---|---|---|
| Upgrade-Routine | jeder Aufruf: Vergleich `tamil_site_datenversion` | Seiten, Rechte, nummerierte Schritte nachziehen; Sperre gegen gleichzeitige Läufe (300 s) | – | live (Datenversion 1); gebaut bis Datenversion 4 (F1 = 2, F3 = 3, F2 = 4) |
| Container-Start | jeder Deploy (`docker/start.sh`) | Code frisch aus dem Image, Nutzer `ki-agent` mit Anwendungspasswort, Anwendungspasswort „migration“ wird ohne `MIGRATION_APP_PASSWORD` entfernt | – | live |
| Suchmaschinen-Sperre | jeder Aufruf | außerhalb von `production` noindex, `Disallow: /`, keine Sitemap | `WP_ENVIRONMENT_TYPE` | live |
| Angaben für Suchmaschinen | jeder Aufruf | nur ohne Yoast/Rank Math | – | live |
| Cache-Kopfzeilen | jeder Aufruf | Gäste 60 s, nie für Suche, Formulare, Buchung | – | live |
| Cookie-Zustimmung | erster Besuch | drei Kategorien, sechs Monate im Browser | Funktionsschalter `zustimmung` | gebaut, aus |

## Abläufe nach den Festlegungen (spezifiziert, nicht gebaut)

### F1 Einsendungen

| Schritt | Auslöser | Regel | Stopp | Protokoll | Karenz | Wiederholung | Mensch |
|---|---|---|---|---|---|---|---|
| Annehmen auf der Website | Formular | Pflichtfelder, Einwilligung, verstecktes Feld leer, ≥ 3 s, ≤ 5/h je IP-Hash, ≤ 3 Links, Bild JPEG/PNG ≤ 5 MB | Funktionsschalter `einreichungen` | Vorgangsnummer | – | – | – |
| Abholen | alle paar Minuten | nur Neues | `eingang` | Zeile je Abholung (Kennungen, keine Namen) | – | nächster Takt; Einsendungen gehen nicht verloren | – |
| Vorbereiten | nach dem Abholen | Agent „Eingang“ (Regeln, Zusammenfassung, Entwurf nur aus Angaben) | `eingang` | Auslöser `agent`, Kanal `eingang` | – | Job-Regeln (1/5/30 Min., 3 Versuche) – Vorschlag | – |
| Entscheiden | Person | – | – | Auslöser `person` | – | – | übernehmen, erledigt, ablehnen, Spam; Antwort von Hand |
| Löschen | täglich | 90 Tage nach Abschluss, Spam 7 Tage | – | Zähler, keine Inhalte | – | – | – |

### F2 Verzeichnis

| Schritt | Auslöser | Regel | Stopp | Protokoll | Mensch |
|---|---|---|---|---|---|
| Annehmen | Formular „Eintrag vorschlagen“ / „Änderung melden“ | Pflichtangaben, Einwilligung, Missbrauchsschutz wie F1 | Funktionsschalter `verzeichnis` | Vorgangsnummer | – |
| Abholen und prüfen | alle paar Minuten | Agent „Verzeichnis“: Pflichtfelder, Form, Dubletten, Kategorie-Vorschlag, Unterschied | `verzeichnis` | Auslöser `agent`, Kanal `verzeichnis` | – |
| Veröffentlichen | Freigabe | erst die Freigabe schreibt in das öffentliche Verzeichnis; Änderungen feldweise | – | Auslöser `person` | jede Veröffentlichung, Änderung, Premium (nur Administrator in WordPress), Löschen |
| Löschen | täglich | Einsender-Daten nach 90 Tagen | – | – | – |

### F3 Werbebuchung

| Schritt | Auslöser | Regel | Protokoll | Wiederholung | Mensch |
|---|---|---|---|---|---|
| Preis und Verfügbarkeit | Kunde wählt | Angebot von KBS; belegte Tage gesperrt | Buchungsprotokoll | – | – |
| Reservieren | Schritt „Zahlen“ | Tage 35 Min. reserviert; genau eine Buchung je Platz und Tag (atomar) | Buchungsprotokoll | Verfall nach 35 Min. | – |
| Zahlung bestätigen | signierte Stripe-Meldung; zusätzlich Abgleich bei der Rückkehr | nur mit gültiger Signatur; Meldung nur einmal wirksam | Buchungsprotokoll | Abgleich; nie blind wiederholen | – |
| Technische Prüfung Werbemittel | Upload | Format, Maße, Größe, Zieladresse | – | – | – |
| Prüfung Werbemittel | KBS | Werberichtlinien (KBS) | mit Person | – | freigeben oder ablehnen (Grund) |
| Start, Wechsel, Ende | Datum | Aktiv-Funktion (bezahlt ∧ geprüft ∧ nicht pausiert ∧ im Zeitraum) | Buchungsprotokoll | – | pausieren, fortsetzen, beenden |
| Erstattung | Ablehnung | voller Betrag über Stripe, Tage frei | Buchungsprotokoll | Fehler → Warnung in der Liste, Mensch | – |
| Zählung | Anzeige sichtbar (½ Fläche, 1 s) / Klick | ohne Cookies, ohne Personendaten | Statistik je Tag | – | – |

Stopp: Funktionsschalter `werbung` in WordPress; ein Stopp-Schalter im Cockpit ist für die Werbung nicht vorgesehen
(zu prüfen, ob gewünscht).

### F4 Instagram, Facebook, WhatsApp

| Schritt | Auslöser | Regel | Stopp | Protokoll | Karenz | Wiederholung | Mensch |
|---|---|---|---|---|---|---|---|
| Erkennen | alle paar Minuten: Radar fragt WordPress nach neu Veröffentlichtem | kein Altbestand (Kriterium zu prüfen, z. B. Einschaltzeitpunkt), keine Korrekturen | `instagram`, `facebook`, `whatsapp` | Zeile je erkanntem Beitrag | – | nächster Takt | – |
| Regelprüfung | nach dem Erkennen | Regelwerk in freigegebener Fassung | dito | Regelprüfung mit Fassung | – | – | Grenzfälle unter „von Hand entscheiden“ |
| Vorbereiten | regelkonform | Text, Hashtags, Bild 1080 × 1350 oder Bildkarte, KI-Hinweis | dito | – | – | – | Text ändern (Karenz) |
| Karenz | nach dem Vorbereiten | 10 Min. | Schalter wirkt sofort | – | 10 Min. | – | ändern oder stoppen |
| Planen | nach der Karenz | ≤ 6/Tag, ≥ 60 Min. Abstand, Ruhezeit 22–7 Uhr (Wartendes um 7 Uhr) | dito | – | – | – | – |
| Veröffentlichen Instagram, dann Facebook | Zeitpunkt erreicht | offizielle Schnittstelle, unmittelbar vorher Schalter prüfen | `instagram` / `facebook` | Auslöser `agent`, Kanal, Regel-Fassung, Kennung und Link bei Meta | – | **keine blinde Wiederholung**: Abgleich mit dem Konto, sonst Mensch; Zugang abgelaufen → Kanal pausiert | – |
| WhatsApp-Entwurf | wie Vorbereiten | Text, Link, Bild | `whatsapp` | Zeile „gepostet“ mit Person und Zeit | – | – | kopieren, posten, markieren |

Ohne Konten: Trockenmodus bis vor den letzten Aufruf an Meta; der Vertrag verlangt je Kanal einen tatsächlichen oder von
der Schnittstelle bestätigten Test.

## Was nie automatisch passiert

| Nie automatisch | Warum / wo festgelegt |
|---|---|
| Freigabe eines Entwurfs; Veröffentlichen ohne Freigabe | Cockpit-Ablauf, B1.1 |
| E-Mail jeder Art (Antworten, Bestätigungen, Nachfassen) | §8 Abs. 2; `tests/test_kein_mailversand.py` |
| Antwort an Einsender; Übernehmen, Ablehnen von Einsendungen | F1 |
| Veröffentlichen, Ändern, Löschen von Verzeichnis-Einträgen; Premium | F2 |
| Freigabe oder Ablehnung eines Werbemittels; Pausieren, vorzeitiges Beenden; Preise | F3 |
| Social-Beiträge, die eine Regel verletzen oder unklar sind; Änderungen am Regelwerk; Posten im WhatsApp-Kanal; Antworten auf Kommentare | F4, §8 Abs. 1, §3 Abs. 3 |
| Wiedereinschalten des Schalters „alles“ (nur admin) | F0 |
| Neustart toter Jobs („Erneut“, nur admin) | F0 |
| Schreiben von Nachträgen mit einem Modell (nur Agent-Modus) | Entscheidung 11.11.2026 |
| Dossier anstoßen | nur Person (Recht `dossier`) |
| Wiederherstellen einer Sicherung | nur von Hand |
| Quellen ein- oder ausschalten, Bildquellen-Register ändern | nur über das Repo |
