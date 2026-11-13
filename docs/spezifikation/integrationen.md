# Integrationen

Teil der Software-Spezifikation für tamil.de. Stand: 13.11.2026. Beschreibt jede Schnittstelle nach außen: Zweck,
offizieller Weg, Rechte, Grenzen, Fehlerverhalten, Testmodus, Variablen (nur Namen), Stand im Code und was KBS liefern
muss. Bildquellen und Lizenzen im Einzelnen: `bilder-und-lizenzen.md`.

## 1. Regeln für alle Schnittstellen

| Regel | Herkunft |
|---|---|
| Nur offizielle, tatsächlich verfügbare Zugänge; kein Auslesen von Seiten, keine inoffiziellen Dienste | Vertrag §3 Abs. 3; `.claude/rules/vertrag.md` |
| Kostenpflichtige Schnittstellen nur mit Freigabe von KBS (Modelle, Bilderzeugung, Zahlungsgebühren) | §3 Abs. 2 |
| Jeder Aufruf geht über einen austauschbaren Transport; Tests benutzen nur Fakes, nie das Netz | `.claude/rules/radar.md`, `.claude/rules/vertrag.md` |
| Unmittelbar vor jedem Aufruf nach außen wird der Stopp-Schalter des Kanals geprüft (`alles`, `redaktion`, `website`, `eingang`, `verzeichnis`, `instagram`, `facebook`, `whatsapp`; `news_radar/schalter.py`) | §8 Abs. 1 |
| Jede automatische Ausführung schreibt eine Protokollzeile: wer oder welcher Agent, was, Kanal, Fassung der Regel; keine Personendaten | §8 Abs. 1 |
| Geheimnisse nur als Variablen der Apps in Coolify oder in einer lokalen `.env`, nie im Repo, im Chat, in Ausgaben oder Docs | `CLAUDE.md` |
| Unklarer Ausgang (Verbindung bricht nach dem Senden ab) wird abgeglichen, nicht blind wiederholt; bleibt er unklar, entscheidet ein Mensch | F4, Arbeitsregel R-07 |
| Kein Mailversand über irgendeine Schnittstelle | §8 Abs. 2 |
| Der Radar holt bei WordPress ab, nie umgekehrt; WordPress hält Öffentliches, Kunden und Geld | Entscheidung 11.11. |

## 2. Übersicht

| Schnittstelle | Zweck | Läuft in | Stand | Live braucht |
|---|---|---|---|---|
| WordPress REST (Plugin `tamil-radar`) | Beiträge, Bilder, Meta vom Radar zur Website | Radar → Website | gebaut, live auf der Vorschau-Adresse | – |
| Anthropic Messages API | Agenten-Redaktion (Rollen) | Radar | gebaut, ohne Schlüssel (Agent-Modus statt API) | Schlüssel, Kostenfreigabe (Tor B1) |
| Google Gemini (Interactions API) | KI-Symbolbilder | Radar | gebaut, aus | Ja von Luis, Kostenfreigabe, Schlüssel |
| Wikimedia Commons API | Lizenz-Metadaten freier Bilder | Radar | gebaut (Agent-Weg) | – |
| Pexels API | Stockfotos | Radar | gebaut, ohne Schlüssel | Schlüssel |
| Unsplash API | – (nur von Hand, siehe Bilder) | – | gebaut, wird abgelöst | – |
| Instagram Graph API (Content Publishing) | Beiträge auf Instagram | Radar | offen (Baustein 5) | Konten und App von KBS |
| Facebook Pages API | derselbe Beitrag auf der Facebook-Seite | Radar | offen (Baustein 5) | wie Instagram |
| WhatsApp | Kanal-Entwurf zum Kopieren | Cockpit | offen (Baustein 5) | Link zum Kanal |
| Stripe (Checkout, Webhooks, Erstattung) | Werbebuchung mit Zahlung | Website | offen (Baustein 4) | Stripe-Konto von KBS |
| Coolify API | Deploy, Variablen, Stand | Werkzeug `tools/coolify.py` | gebaut | engeres Token (Tor B2) |

## 3. WordPress REST (Plugin `tamil-radar`)

| Punkt | Festlegung |
|---|---|
| Zweck | Freigegebene Entwürfe als Beitrag mit Beitragsbild, Nachweis, Meta (Quelle, Termin, Kino) und SEO anlegen; Kinolisten aktualisieren; Stilbeispiele lesen |
| Offizieller Weg | REST-Namensraum `tamil-radar/v1` des eigenen Plugins: `GET /status`, `POST /beitrag`, `GET /beitrag/{uid}`, `PUT /beitrag/{uid}`, `GET /stil?n=` (`wordpress/plugins/tamil-radar/includes/rest.php`). Rückfall ohne Plugin: Kern-REST `/wp/v2/posts`, `/wp/v2/media` (ohne Nachtrag-Datum) |
| Auth | Anwendungspasswort von WordPress über Basic Auth, nur über HTTPS (developer.wordpress.org, „Authentication“, Abruf 13.11.2026); Benutzer `ki-agent` mit Rolle „Radar“ |
| Rechte | Lesen: `edit_posts`. Schreiben: `edit_posts` und `upload_files`. Veröffentlichen: `publish_posts`. Rolle „Radar“: `read`, `edit_posts`, `publish_posts`, `edit_published_posts`, `delete_posts`, `upload_files` (`includes/role.php`) |
| Grenzen | Bild als Base64 bis 15 MB, nur JPEG, PNG, WebP (`includes/media.php`); Dubletten über `radar_uid` → 409 |
| Fehler und Verhalten | 409: als vorhanden übernehmen (Kinoliste: aktualisieren). Andere Fehler: Entwurf „Fehler“, Meldung im Cockpit, „Erneut“ durch einen Menschen; ein Fehler stoppt den Lauf nicht. Stopp-Schalter `website`: nichts wird gesendet, Freigegebenes wartet, eine Protokollzeile je Entwurf und Stopp (`news_radar/publisher.py`) |
| Testmodus | Fake-Client in `tests/test_publisher.py`; echtes WordPress lokal (`wordpress/dev/`, SQLite) für `tests/wp/` |
| Variablen | Radar: `WP_URL`, `WP_USER`, `WP_APP_PASSWORD`, `WP_POST_STATUS`, `WP_SEO_META`. Website: `RADAR_APP_PASSWORD`, `RADAR_COCKPIT_URL`, `WP_ENVIRONMENT_TYPE` |
| Stand | gebaut und verbunden (Vorschau-Adresse, `WP_POST_STATUS=publish`) |
| Geplant | Meta `bild_lizenz`, `bild_lizenz_url`, `bild_quelle_url` (Bilder); Upload der Social-Datei als eigenes Medium mit öffentlicher JPEG-Adresse (Baustein 5); Abfrage neu veröffentlichter Beiträge und Termine für Social, auch von Hand angelegter (F4: „Erkennen“), z. B. über `/wp/v2/posts?after=` oder einen eigenen Endpunkt; Abholen von Verzeichniseinträgen (Baustein 3); Einsendungen siehe unten |
| KBS liefert | nichts; beim Livegang (Tor B3) nur die Domain |

### Einsendungen (F1)

Der Radar holt Einsendungen der Formulare ab (`wordpress/plugins/tamil-radar/includes/einsendungen.php`, Daten und
Prüfungen in `tamil-site/includes/einsendungen*.php`). WordPress ruft den Radar nie auf und verschickt keine E-Mail.

| Punkt | Festlegung |
|---|---|
| Routen | `GET /einsendungen?nach=<id>&anzahl=<1–100, Standard 50>` · `GET /einsendung/{vorgang}` · `POST /einsendung/{vorgang}/status` mit `{"status": …}` · `GET /einsendung/{vorgang}/bild` (alle unter `tamil-radar/v1`) |
| Auth und Recht | Anwendungspasswort wie oben; Recht `tamil_einsendungen_abholen`, nur Rolle „Radar“ (vergeben über die Upgrade-Routine von `tamil-site`, Datenversion 2). Ohne Anmeldung 401, ohne Recht 403 (auch für Administratoren) |
| Voraussetzung | Plugin `tamil-site` aktiv mit Datenversion ≥ 2, sonst 503 `tamil_site_fehlt` (der Radar wertet das als „nichts abzuholen“). Der Funktionsschalter „Einreichungen“ steuert nur das Annehmen auf der Website; Abholen, Status und Bild bleiben erreichbar, damit vorhandene Einsendungen auch nach dem Ausschalten abgeschlossen werden |
| Cursor | Liste aufsteigend nach `id`, nur `id > nach`. Antwort `{"einsendungen": [...], "weiter": <id>, "mehr": bool}`; der Radar merkt sich `weiter` und fragt erneut, solange `mehr` wahr ist. Lesen ändert nichts (beliebig wiederholbar) |
| Einwilligung | `einwilligung_fassung` ist die Fassung, der zugestimmt wurde. Den Text je Fassung archiviert die Website (Option `tamil_site_einsendungen_fassungen`, sichtbar unter Werkzeuge → Einsendungen); ein geänderter Text wird nur mit neuer Fassung gespeichert, eine Fassung steht immer für genau einen Text |
| Einsendung | `id`, `vorgangsnummer` (Form `T261113-K7M3Q`), `art` (`event`, `beitrag`, `kooperation`, `werbung`, `kontakt`), `status`, `eingang_at`, `abgeholt_at`, `abgeschlossen_at` (ISO 8601, UTC), `name`, `email`, `telefon`, `einwilligung`, `einwilligung_fassung`, `felder` (je Art: Event `titel`, `beginn`, `ende` (ISO 8601 mit Versatz), `ort`, `stadt`, `land` (DE/AT/CH), `veranstalter`, `beschreibung`, `eintritt`, `ticket_link`; Beitrag `thema`, `text`, `link`; Kooperation `organisation`, `anliegen`; Werbung `firma`, `platz_zeitraum`, `nachricht`; Kontakt `nachricht`; leere Felder als `""`), `bild` (`null` oder `typ`, `groesse`, `sha256`, `recht_bestaetigt`). Kein IP-Hash, kein Dateiname |
| Status setzen | Erlaubt: `abgeholt` (aus `eingegangen`), `uebernommen`, `erledigt`, `abgelehnt`, `spam` (aus `eingegangen` oder `abgeholt`). Ein Abschluss setzt `abgeschlossen_at` (Beginn der Löschfrist) und ist endgültig: derselbe Status noch einmal → 200 ohne Wirkung; ein anderer Abschluss → 409 `tamil_einsendung_abgeschlossen` mit `data.aktuell`; `abgeholt` nach einem Abschluss → 200 ohne Wirkung. Unbekannter Status 400, unbekannte Vorgangsnummer 404, Datenbankfehler (auch beim Lesen, in allen vier Routen) 500 `tamil_einsendung_db` (nichts geändert; erneut versuchen). Prüfung und Schreiben sind eine bedingte Anweisung (kein Rennen). `vorbereitet` führt nur der Radar |
| Bild | `{"vorgangsnummer", "typ" (image/jpeg oder image/png), "groesse", "sha256", "daten_base64"}`; 404 ohne Bild. Das Bild ist neu gespeichert ohne Metadaten. Bei „übernehmen“ lädt der Radar es mit dem Beitrag hoch (`POST /beitrag`, Base64); auf der Website bleibt es bis zur Löschfrist nicht öffentlich |
| Protokoll (Website) | Eingang (`website`), jeder Statuswechsel und jeder Bildabruf (Benutzername), Löschungen (`cron`); nur Vorgangsnummer, Aktion, kurze Notiz, keine Namen oder Kontaktdaten. Frist 12 Monate |
| Löschfrist | WP-Cron stündlich, unabhängig vom Schalter: 90 Tage nach Abschluss (`uebernommen`, `erledigt`, `abgelehnt`), Spam nach 7 Tagen, nie abgeschlossene (`eingegangen`, `abgeholt`) 90 Tage nach Eingang (Höchstfrist, Protokollzeile „Hoechstfrist“), IP-Hash nach 24 Stunden. Die Höchstfrist gilt auch, wenn der Eingang im Radar (Stopp-Schalter `eingang`) so lange angehalten ist: Was länger als 90 Tage nicht abgeholt wurde, wird ungesehen gelöscht. Der Radar löscht seine Kopie mit denselben Fristen |
| Ablauf im Radar (zu bauen) | Stopp-Schalter `eingang` prüfen → `GET /einsendungen?nach=` → je Einsendung speichern → `POST …/status` `abgeholt` → Agent bereitet vor → Redaktion entscheidet → `POST …/status` mit dem Abschluss. Bei unklarem Ausgang (Abbruch nach dem Senden) erneut `GET /einsendung/{vorgang}` und abgleichen |
| Testmodus | `tests/wp/test_einsendungen.py` gegen das lokale WordPress; Schalter je Aufruf über die Kopfzeile `X-Tamil-Funktionen: einreichungen` (nur Umgebung `local`) |
| Variablen | Website: `TAMIL_PROXY_ANZAHL` (zusätzliche Proxys **vor** Traefik, z. B. Cloudflare; Standard 0, hinter Traefik allein 0 lassen. Apache (`mod_remoteip`, Basis-Image und `wordpress/Dockerfile`) setzt hinter Traefik schon die Adresse des Besuchers als `REMOTE_ADDR`; jeder Wert über 0 nimmt einen Eintrag aus dem restlichen `X-Forwarded-For` und macht die Adresse fälschbar, wenn davor kein weiterer Proxy steht). `wordpress/docker/start.sh` schreibt sie als Konstante in `wp-config.php`. Die Drossel nimmt `REMOTE_ADDR`; IPv6 zählt je /64 |
| Stand | Website gebaut und lokal geprüft; Radar-Seite offen |

### Verzeichnis (F2)

Der Radar holt Einsendungen ab, liest Einträge für den Vergleich alt/neu und schreibt nach der Freigabe im Cockpit
genau die freigegebenen Werte. WordPress ruft den Radar nie auf und verschickt keine E-Mail.
Code: `wordpress/plugins/tamil-radar/includes/verzeichnis.php` (Routen), Logik und Prüfungen in
`wordpress/plugins/tamil-site/includes/verzeichnis.php`.

| Punkt | Festlegung |
|---|---|
| Recht | `tamil_verzeichnis_pflegen`, nur Rolle „Radar“ (Upgrade-Routine, Datenversion 4). Administratoren haben es nicht; der Beitragstyp ist nicht über `/wp/v2` erreichbar |
| Schalter | `verzeichnis` (Standard aus). Aus oder Plugin `tamil-site` fehlt: `503` mit `tamil_funktion_aus` bzw. `tamil_site_fehlt` |
| `GET /verzeichnis/einsendungen?nach=<id>&anzahl=<1..100>` | Einsendungen mit `id > nach`, aufsteigend; Antwort `{einsendungen: [...], naechster: <id>}`. `naechster` ist der nächste Cursor |
| `GET /verzeichnis/einsendung/{vorgang}` | eine Einsendung: `typ` (`neu`, `aenderung`, `entfernen`), `eintrag_id`, `status`, `einsender {name, email}`, `berechtigung`, `felder {feld: {wert, oeffentlich}}` (bei Änderungen nur geänderte Felder), `anmerkung`, `einwilligung {erteilt, fassung}`, `regeln {fehlt[], formfehler[], dubletten[{eintrag_id, grund}]}` (feste Regeln, ohne Modell), `pruefung` (Ablage des Agenten), `entscheidung` |
| `POST /verzeichnis/einsendung/{vorgang}/status` | `{"status": "geprueft" \| "abgelehnt", "pruefung": {…}}`; `freigegeben` setzt nur die Freigabe. Abgeschlossene Einsendungen: `409 tamil_vz_status_konflikt` |
| `GET /verzeichnis/eintraege?nach=&anzahl=` | alle Einträge (veröffentlicht und entfernt) mit Cursor, für die Dublettenprüfung |
| `GET /verzeichnis/eintrag/{id}` | `{id, felder, premium, status (veroeffentlicht \| entfernt), stand, link, geaendert}`; `stand` ist die Prüfsumme über Felder und Status |
| `POST /verzeichnis/eintrag` | `{"einsendung": "V…", "felder": {…}}` → `201`; Einsendung vom Typ `neu`. Wiederholt: `200` mit `bereits: true`, kein zweiter Eintrag |
| `POST /verzeichnis/eintrag/{id}` | `{"einsendung", "stand", "felder"}`; Einsendung vom Typ `aenderung` zu diesem Eintrag; schreibt nur die übergebenen Felder |
| Werte nur aus der Einsendung | Geschrieben werden nur Felder, die in der Einsendung stehen, und `kategorie` (sonst `400 tamil_vz_nicht_eingesandt`, `data.felder`). Weicht ein Wert vom eingesandten ab, steht der Feldname in `entscheidung.abweichend` und im Protokoll („abweichend: <Feld>“), nie der Wert. Hat der Einsender ein Feld nicht zur Veröffentlichung freigegeben, wird jeder nicht leere Wert dafür abgewiesen; „Änderung melden“ mit entferntem Haken bei einem gezeigten Wert ist eine Änderung auf leer |
| Wiederanlauf | Bricht eine Freigabe nach dem Beanspruchen ab (`freigegeben`, `entscheidung` leer), antwortet dieselbe Freigabe 120 Sekunden lang `409 tamil_vz_in_arbeit` und läuft danach mit denselben Werten erneut (ohne `stand`-Prüfung); ein schon angelegter Eintrag wird über die Vorgangsnummer gefunden, nicht doppelt angelegt |
| `POST /verzeichnis/eintrag/{id}/entfernen` | `{"einsendung", "stand"}`; Einsendung vom Typ `entfernen`; Eintrag wird Entwurf (nicht gelöscht) |
| Felder | `name`, `art` (`business`, `dienstleister`, `verein`, `tempel`), `kategorie` (Slug, passend zur Art), `beschreibung` (≤ 600), `adresse`, `plz` (DE 5, AT/CH 4 Ziffern), `stadt`, `land` (`DE`, `AT`, `CH`), `bundesland_kanton` (Liste je Land), `telefon`, `email`, `website` (http/https), `oeffnungszeiten` |
| Fehler | `400 tamil_vz_unbekannte_felder` (`data.felder`), `400 tamil_vz_ungueltig` (`data.fehler`), `400 tamil_vz_unvollstaendig` (`data.fehlt`, Pflicht: Name, Art, PLZ, Stadt, Land, ein Kontaktweg), `403 tamil_vz_premium_verboten`, `404 tamil_vz_einsendung_fehlt` / `tamil_vz_eintrag_fehlt`, `409 tamil_vz_falsche_einsendung` (Typ oder Eintrag passt nicht), `409 tamil_vz_abgelehnt`, `409 tamil_vz_stand` (seit dem Lesen geändert; `data.stand`), `400 tamil_vz_nicht_eingesandt` (`data.felder`), `409 tamil_vz_nicht_oeffentlich` (`data.feld`: der Einsender hat das Feld nicht zur Veröffentlichung freigegeben), `409 tamil_vz_in_arbeit` / `tamil_vz_gesperrt` (gleichzeitige Freigabe) |
| Nebenläufigkeit | Jede Einsendung wird genau einmal freigegeben (bedingtes UPDATE auf den Status); Änderungen am selben Eintrag laufen unter einer Sperre (auch die Eingabemaske in wp-admin) und nur gegen den gelesenen `stand`; Art und Kategorie werden auch bei Teiländerungen gegeneinander geprüft |
| Premium | nur ein Administrator in wp-admin; weder Formular noch diese Routen setzen es |
| Protokoll | Tabelle `tamil_vz_protokoll`: Zeit, wer (Benutzername, `website`, `cron`), Aktion, Vorgangsnummer, Eintrag, Feldnamen; keine Inhalte oder Personendaten; Frist 12 Monate |
| Testmodus | `tests/wp/test_verzeichnis.py` gegen das lokale WordPress |
| Stand | gebaut auf der Website; die Gegenseite im Radar (Abholen, Prüfung durch den Agenten, Cockpit alt/neu) fehlt noch |

## 4. Anthropic (Agenten-Redaktion)

| Punkt | Festlegung |
|---|---|
| Zweck | Rollen der Redaktion v2: Signal, Cluster, Recherche, Faktencheck, Text, Lektorat, SEO, Dossier |
| Offizieller Weg | Messages API über das offizielle Python-SDK `anthropic`; nur `providers.Claude.call()` ruft an (`news_radar/workflow/providers.py`) |
| Auth | API-Schlüssel (`ANTHROPIC_API_KEY`, alternativ `RADAR_ANTHROPIC_API_KEY`) |
| Modelle je Rolle | Haiku 5.5 (`claude-haiku-5-5`): Signal, Cluster, Lektorat, SEO · Sonnet 5.5 (`claude-sonnet-5-5`): Recherche, Faktencheck, Text · Opus 5.5 (`claude-opus-5-5`): Dossier, Prüfer (zweite KI, `RADAR_MODELL_PRUEFER`) (`config.py` `ROLLEN_MODELLE`; je Rolle änderbar über `RADAR_MODELL_<ROLLE>`, `RADAR_MODEL` für Text) |
| Preise (je 1 Mio. Tokens, Eingabe / Ausgabe / Cache-Lesen) | Haiku 5.5: 0,10 $ / 0,50 $ / 0,01 $ (über 100 000 Tokens im Prompt 0,50 $ / 2,50 $) · Sonnet 5.5: 2 $ / 10 $ / 0,10 $ · Opus 5.5: 4 $ / 20 $ / 0,20 $ (Modellübersicht von Anthropic, Stand 03.11.2026). `workflow/costs.py` rechnet bei Sonnet 5.5 Cache-Lesen mit 0,20 $; das überschätzt leicht und ist zu korrigieren |
| Budget | Reservierung des ungünstigsten Falls vor jedem Aufruf; Tag `RADAR_BUDGET_TAG_USD`, Monat `RADAR_BUDGET_MONAT_USD`, Warnung `RADAR_BUDGET_WARNUNG`, neue bezahlte Storys je Tag `RADAR_ENTWUERFE_TAG`; Pilot 2 $ je Tag (Entscheidung 09.11.). Jeder Aufruf steht in `agent_usage` |
| Grenzen | Ratenlimits des Anthropic-Kontos; das SDK wiederholt 429 und 5xx einmal (`max_retries=1`), Zeitlimit 600 s |
| Fehler und Verhalten | 429/5xx nach dem zweiten Versuch: Job scheitert, bleibt im Cockpit sichtbar, wird später neu angestoßen. `stop_reason: refusal`: Status „abgelehnt“; bei Sonnet 5.5 und Opus 5.5 übernimmt der serverseitige Rückfall (`server-side-fallback-2026-07-01`, `fallbacks: "default"`), bei Haiku gibt es keinen. `max_tokens`: Status „abgeschnitten“. Budget erschöpft: neue bezahlte Jobs warten |
| Hinweise zum Modell | Bei Opus 5.5 lässt sich Denken nicht abschalten; die Stufe `effort` ist dort standardmäßig `medium` und soll ausdrücklich gesetzt werden |
| Testmodus | `FakeClaude` (`news_radar/workflow/fake.py`); kein Test ruft `api.anthropic.com` |
| Stand | gebaut; Schlüssel fehlt (Tor B1). Bis dahin schreibt eine Claude-Sitzung im Agent-Modus (`/api/agent/export`, `/api/agent/import`, `RADAR_AGENT_TOKEN`) ohne API-Kosten (Entscheidung 12.11.: Schreib-Automatik später) |
| KBS liefert | Freigabe der Modellkosten (Zuarbeit Nr. 12); den Schlüssel trägt Luis in Coolify ein |

### Agent-Import: Block `pruefung` (Entscheidung Luis, 13.11.2026)

Im Agent-Modus prüft die Research-Sitzung jeden Beitrag durch eine zweite KI aus frischem Kontext und liefert dazu in
`POST /api/agent/import` je Beitrag den Block `pruefung`:

```json
{"pruefer": "claude-code/pruefer-1", "autor": "claude-code/redakteur-1",
 "zeitpunkt": "2026-11-13T21:40:00+00:00", "urteil": "importieren",
 "sha256": "<sha256 hex des geprüften inhalt_html>",
 "befunde": [{"schwere": "P3", "beschreibung": "Teaser etwas lang", "satz": "", "behoben": false}],
 "saetze": [{"nr": 1, "satz": "Der Verein erhielt am Freitag den Integrationspreis.", "urteil": "gedeckt",
             "claim_ids": ["C1"], "fundstelle": "hat am Freitag den Integrationspreis", "kern": true}]}
```

Pflicht für jeden Beitrag (Verwerfen braucht keine): eine andere Instanz als der Autor (`pruefer` ≠ `?von=` und ≠ `autor`), `zeitpunkt` ISO 8601 mit Zeitzone, nicht in der Zukunft, höchstens drei Tage alt, `urteil` `importieren` oder `nicht_importieren`, `befunde` mit `schwere` P1/P2/P3 und `behoben`, `sha256` (hex) genau des eingereichten `inhalt_html`, `saetze` genau die Sätze von Titel, Teaser und Haupttext ohne Quellenzeile – deterministisch geteilt wie `agents/pruefer.saetze_des_entwurfs`, keiner fehlt, keiner zusätzlich (Abkürzungen wie „z. B.“, „Dr.“, „St.“ trennen keinen Satz) (`urteil` gedeckt/ungedeckt/widerspruch/kein_fakt, `kern`). Abgewiesen – nichts geändert – ohne Block, bei gleicher Instanz, ungültigem Zeitpunkt, falschem `sha256`, fehlenden oder fremden Sätzen, `nicht_importieren`, offenen P1/P2 oder leeren `saetze`. Danach streicht der Radar ungedeckte Nebensätze; eine ungedeckte Kernaussage schickt die Story in die Nachrecherche. Der Block wird als Fassung `pruefung` gespeichert, der Entwurf trägt „Geprüft von zweiter KI (Prüfer, Zeitpunkt)“ und die Befunde als Hinweise. `gedeckt` zählt nur mit `claim_ids` bestätigter Claims, und jede Zahl, jedes Datum und jedes großgeschriebene Wort außer am Satzanfang muss in Aussage oder Fundstelle dieser Claims stehen – sonst `ungedeckt`. `kein_fakt` gilt im Agent-Import nie (wie `ungedeckt`). Die Quellenzeile `<p class="quelle">` baut der Radar aus den Dokumenten der Story neu; eingereichter Text darin fällt weg.

## 5. Google Gemini (KI-Symbolbilder)

| Punkt | Festlegung |
|---|---|
| Zweck | KI-Symbolbild als Stufe 5 der Bildkette und Füllen des Bildpools (`bilder-und-lizenzen.md`, Abschnitt 4) |
| Offizieller Weg | Interactions-API `POST https://generativelanguage.googleapis.com/v1beta/interactions` mit `model`, `input`, `store: false`, `response_format` (`type: image`, `mime_type`, `aspect_ratio`, `image_size`); Bild kommt als Base64 (`news_radar/bilder.py`). Google zeigt alle Beispiele für die Bilderzeugung mit dieser API (Abruf 13.11.2026) |
| Auth | Schlüssel in der Kopfzeile `x-goog-api-key` |
| Konto | Google-Projekt mit Abrechnung; für Bildmodelle gibt es keine kostenlose Stufe (Preisseite, Abruf 13.11.2026). In der bezahlten Stufe werden Eingaben nicht zur Produktverbesserung genutzt |
| Modell, Größe | `BILD_MODELL` (Standard `gemini-nano-banana-2.1`), `BILD_GROESSE` (`1K`, `2K`, `4K`; Großschreibung Pflicht); Festlegung 4:3 in 2K = 2400 × 1792 px |
| Kosten | 2K 0,0504 $ je Bild (1K 0,0336 $, 4K 0,113 $; Abruf 13.11.2026) |
| Grenzen | Ratenlimits je nach Stufe des Google-Projekts; im Radar: je Story `RADAR_KI_BILDER_JE_ARTIKEL`, je Tag `RADAR_KI_BILDER_TAG` (neu), Budget wie bei Anthropic |
| Fehler und Verhalten | Netzfehler, 429, 5xx: ein zweiter Versuch nach kurzer Pause; danach kein Bild, die Kette geht weiter zur Bildkarte. Antwort ohne Bildblock oder unlesbares Bild: kein Bild. Nie eine Ausnahme nach oben (`from_gemini` liefert `None`) |
| Testmodus | Transport austauschbar (`bild_transport`), `tests/test_bilder.py`, `tests/test_media.py` |
| Variablen | `GEMINI_API_KEY`, `BILD_MODELL`, `BILD_GROESSE`, `BILD_MODUS`, `BILD_REIHENFOLGE`, `BILD_POOL_DIR`, `RADAR_KI_BILDER_JE_ARTIKEL`; neu: `BILD_KI_FREIGABE`, `RADAR_KI_BILDER_TAG` |
| Stand | gebaut, aus (kein Schlüssel; Entscheidung „keine KI-Bilder“ vom 11.11.) |
| KBS liefert | Freigabe der Kosten; Luis entscheidet über das Einschalten |

## 6. Wikimedia Commons API

| Punkt | Festlegung |
|---|---|
| Zweck | Lizenz, Urheber, Dateityp, Größe und Bildadresse einer Commons-Datei selbst feststellen (Weg „commons“) |
| Offizieller Weg | `GET https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url|size|mime|extmetadata&iiurlwidth=<breite>&titles=File:<name>&format=json`; Bild von `upload.wikimedia.org` oder `thumb.wikimedia.org` (`bildvorschlag.py` `commons_api_url`, `_commons`) |
| Auth | keine; Pflicht ist ein aussagekräftiger User-Agent mit Kontakt (Adresse oder Mail). Fehlt er oder ist er generisch, antwortet Wikimedia mit 403 (User-Agent-Richtlinie der Wikimedia Foundation). Heute: `TamilDE-NewsRadar/2.0 (+https://www.tamil.de)` (`news_radar/net.py`) |
| Grenzen | je Minute: ohne Kennung 10 Anfragen, unangemeldeter Bot mit richtigem User-Agent 200; höchstens 3 gleichzeitige Anfragen; Medien höchstens 2 gleichzeitig; Vorschaubilder nur in Standardbreiten (…, 960, 1280, 1920, 3840 px), andere Breiten werden streng begrenzt; bei Hintergrundarbeit `maxlag` setzen (mediawiki.org, Abruf 13.11.2026) |
| Fehler und Verhalten | 429 oder 503: `Retry-After` beachten, ohne Kopfzeile mindestens 5 s warten bzw. exponentiell zurückweichen; danach Eintrag „nicht bearbeitet“, nicht „abgelehnt“. Lizenz nicht eindeutig: abgelehnt mit Grund. Heute: jeder Netzfehler wird zu „abgelehnt“, `Retry-After` wird nicht beachtet, Breite 1600 ist keine Standardbreite (zu ändern auf 1920) |
| Testmodus | Abruf austauschbar (`abruf`), `tests/test_bildvorschlag.py` |
| Variablen | keine |
| Stand | gebaut als Agent-Weg (`POST /api/agent/bild`, CLI `agent bild`); in der automatischen Bildkette fehlt er |
| KBS liefert | nichts |

## 7. Stock: Pexels und Unsplash

| Punkt | Pexels | Unsplash |
|---|---|---|
| Rolle | automatischer Stock-Weg (Stufe 4) | nur von Hand: die Redaktion lädt auf unsplash.com herunter und trägt die Lizenz ein |
| Offizieller Weg | `GET https://api.pexels.com/v1/search` | API wird nicht mehr automatisch genutzt (Hotlink-Pflicht der API-Richtlinien passt nicht zu Mediathek und Instagram) |
| Auth | Schlüssel in der Kopfzeile `Authorization` | – |
| Grenzen | 200 Anfragen je Stunde, 20 000 je Monat; mehr auf Anfrage (pexels.com/api/documentation, Abruf 13.11.2026) | – |
| Pflichten | sichtbarer Link zu Pexels, Fotograf nennen „when possible“; kein Nachbau von Pexels | – |
| Fehler und Verhalten | 429: Stufe überspringen, kein zweiter Versuch im selben Lauf; ohne Treffer: nächste Stufe | – |
| Testmodus | Fake-Transport (heute direkter `requests`-Aufruf in `news_radar/images.py`; austauschbar machen) | – |
| Variablen | `PEXELS_API_KEY` | `UNSPLASH_ACCESS_KEY` (entfällt) |
| KBS liefert | Konto bei Pexels empfohlen auf KBS, weil die Nutzungsbedingungen den Betreiber binden | – |

## 8. Instagram Graph API (Content Publishing)

| Punkt | Festlegung |
|---|---|
| Zweck | Regelkonforme Artikel und Termine nach zehn Minuten Karenz als Bildbeitrag auf dem Instagram-Konto von Tamil.de (Vertrag B2.2, F4) |
| Konto-Voraussetzungen | Instagram-**Professional**-Konto, verknüpft mit der Facebook-Seite; Business-Portfolio bei Meta; App bei Meta im Besitz von KBS. Verlangt die Seite eine Page Publishing Authorization (PPA), muss sie vorher abgeschlossen sein, sonst ist Veröffentlichen nicht möglich (developers.facebook.com, Content Publishing, Abruf 13.11.2026) |
| Weg | „Instagram API with Facebook Login“, weil Facebook ohnehin ein Seiten-Token braucht und ein Token beide Kanäle bedient. Rechte: `instagram_basic`, `instagram_content_publish`, `pages_read_engagement` (dazu `ads_management`, `ads_read`, wenn die Person die Seite über den Business Manager verwaltet). Alternative laut Meta: „Instagram API with Instagram Login“ mit `instagram_business_basic`, `instagram_business_content_publish` |
| Token | Systembenutzer im Business-Portfolio von KBS mit zugewiesener Seite und Instagram-Konto, oder ein langlebiges Seiten-Token (läuft nicht nach Zeit ab, wird aber bei bestimmten Ereignissen ungültig, z. B. Rollen- oder Passwortwechsel). Langlebige Nutzer-Token gelten etwa 60 Tage und taugen nicht für den Dauerbetrieb |
| Zugriffsstufe | Standard Access genügt, wenn nur Personen mit Rolle in der App sie benutzen (eigene Konten von KBS); dafür keine App-Prüfung. Advanced Access bräuchte App Review und Unternehmensverifizierung (Wochen) |
| Ablauf | 1. Social-Bild 1080 × 1350 JPEG als Medium in WordPress, öffentliche Adresse. 2. `POST /{ig-user-id}/media` mit `image_url`, `caption`, `alt_text` → Container-ID. 3. `GET /{container-id}?fields=status_code` bis `FINISHED` (höchstens einmal je Minute, höchstens fünf Minuten). 4. `GET /{ig-user-id}/content_publishing_limit` und Stopp-Schalter `instagram` prüfen. 5. `POST /{ig-user-id}/media_publish` mit `creation_id` → Media-ID. 6. `GET /{media-id}?fields=permalink` → Link für die Historie |
| Grenzen | 100 per API veröffentlichte Beiträge in 24 Stunden je Konto (an anderer Stelle derselben Seite steht 50; Tamil.de plant höchstens sechs am Tag, also unkritisch). Bild: nur JPEG, höchstens 8 MB, Verhältnis 4:5 bis 1,91:1, Breite 320 bis 1440 px. Text: 2200 Zeichen, 30 Hashtags, 20 Erwähnungen; Alt-Text 1000 Zeichen. Aufruf-Kontingent der Plattform: 4800 × Zahl der Einblendungen in 24 Stunden je App und Konto |
| Fehler und Verhalten | Token ungültig (Code 190) oder Konto gesperrt: Kanal pausiert, Grund im Cockpit. Ratenlimit (Codes 4, 17, 32, 613, 80002) oder Tagesgrenze erreicht: warten, beim nächsten zulässigen Zeitpunkt (Ruhezeit 22 bis 7 Uhr beachten) erneut, kein Sofort-Wiederholen. Container `ERROR` oder `EXPIRED`: einmal neuer Container, dann an einen Menschen. Abbruch nach `media_publish`: mit den letzten Beiträgen des Kontos abgleichen (`GET /{ig-user-id}/media?fields=id,caption,timestamp,permalink`), bei Treffer als veröffentlicht übernehmen, sonst „von Hand entscheiden“. Code 368 (als missbräuchlich eingestuft): Kanal pausiert, Mensch |
| Testmodus | Trockenmodus (alles außer dem letzten Aufruf an Meta) und Fake-Transport in den Tests (`tests/test_social.py`, `FakeMeta` in `news_radar/social/fake.py`, Abnahme-Szenarien 70–77). Meta bietet für Veröffentlichungen keine Sandbox; für den echten Abnahmetest T1 empfiehlt sich ein nicht öffentliches Test-Professional-Konto mit Testseite von KBS. Der Vertrag lässt einen „durch die Schnittstelle bestätigten“ Test zu |
| Variablen | `META_GRAPH_VERSION` (Standard `v23.0`; beim Einrichten die aktuelle Version laut Meta), `META_IG_USER_ID`, `META_PAGE_ID`, `META_ZUGANG` (geheim: Token), `RADAR_SOCIAL_LIVE` (live nur zusammen mit allen drei Angaben, sonst Trockenmodus), Funktionsschalter `RADAR_SOCIAL` |
| Stand | gebaut im Trockenmodus (`news_radar/social/`, 13.11.2026); live offen bis Konten und Freigabe des Regelwerks durch KBS; Stopp-Schalter `instagram` fragt der Ablauf vor jedem Aufruf ab |
| KBS liefert | Professional-Konto, verknüpfte Seite, Business-Portfolio, App bei Meta, Rolle für den Systembenutzer, ggf. PPA; einmalige Freigabe des Regelwerks; Hashtags je Rubrik (Zuarbeit Nr. 9, 10) |

## 9. Facebook Pages API

| Punkt | Festlegung |
|---|---|
| Zweck | Derselbe Inhalt wie auf Instagram auf der verbundenen Facebook-Seite, ohne zweite Freigabe (Vertrag B2.3) |
| Weg | `POST /{page-id}/photos` mit `url` (dieselbe JPEG-Adresse), `caption` (Text mit Link auf tamil.de; `message` ist laut Meta veraltet), `alt_text_custom`, `published=true`. Antwort: `id` (Foto) und `post_id`; Link über `GET /{post_id}?fields=permalink_url`. Vorschlag F4 Frage 5: Foto mit Text statt Link-Vorschau |
| Auth und Rechte | Seiten-Token einer Person bzw. eines Systembenutzers, der auf der Seite die Aufgabe `CREATE_CONTENT` ausführen darf; Rechte `pages_manage_posts`, `pages_read_engagement`, `pages_show_list` |
| Grenzen | Datei höchstens 10 MB (JPEG, PNG u. a.). Kontingent für Seiten-Token: 4800 × Zahl der aktiven Nutzer der Seite in 24 Stunden; Fehlercode 80001 |
| Fehler und Verhalten | wie Instagram; zusätzlich: Instagram veröffentlicht, Facebook scheitert → Facebook wird getrennt neu versucht, Instagram nicht wiederholt (Dublettenregel F4: jeder Beitrag höchstens einmal je Kanal) |
| Testmodus | wie Instagram |
| Variablen | `META_PAGE_ID`, Token wie Instagram |
| Stand | gebaut im Trockenmodus wie Instagram; Stopp-Schalter `facebook` vor jedem Aufruf |
| KBS liefert | wie Instagram |

## 10. WhatsApp

| Punkt | Festlegung |
|---|---|
| Zweck | Für jeden Social-Beitrag ein Entwurf für den WhatsApp-Kanal von Tamil.de (Vertrag B3.1) |
| Offizieller Weg | **Keiner zum Veröffentlichen in Kanälen.** Die Doku von Meta beschreibt für Kanäle nur das Lesen über die Content Library API (Kanal-Updates der letzten 30 Tage); die WhatsApp Cloud API beschreibt Nachrichten an Personen, keine Kanäle (geprüft am 11.11. und 13.11.2026) |
| Umsetzung | Cockpit zeigt Text, Link, Bild (1080 × 1350) mit „Kopieren“, „Bild herunterladen“ und „als gepostet markieren“; gepostet wird von Hand; die Markierung steht mit Person und Zeit im Protokoll |
| Warum nicht die WhatsApp Business Cloud API | Sie schickt Nachrichten an einzelne Personen, die vorher eingewilligt haben (Opt-in mit Namen des Unternehmens, je Nachrichtenart); das wäre ein neuer Verteiler mit Personendaten (Telefonnummern, Einwilligungen, Auftragsverarbeitung), kostenpflichtig, und vertraglich nicht beauftragt (B3.1 nennt den Kanal, Newsletter wurde am 20.10. entfernt) |
| Verboten | inoffizielle Werkzeuge, die WhatsApp Web fernsteuern (§3 Abs. 3; Sperrrisiko für die Nummer) |
| Grenzen, Fehler | keine Schnittstelle, also keine; Stopp-Schalter `whatsapp` blendet den Entwurf aus |
| Testmodus | `tests/test_social.py`, Abnahme-Szenario 74 |
| Variablen | `WHATSAPP_KANAL_URL` (Link zum Kanal, kein Geheimnis; steht im Entwurf, falls gesetzt) |
| Stand | gebaut: Cockpit `/social` mit „Kopieren“, „Bild herunterladen“, „als gepostet markieren“ |
| KBS liefert | Link zum WhatsApp-Kanal; Person, die postet |

## 11. Stripe (Werbebuchung)

| Punkt | Festlegung |
|---|---|
| Zweck | Online-Zahlung der Werbebuchung, gesicherter Statusabgleich, Aktivierung nur nach bestätigter Zahlung, Erstattung bei Ablehnung (Vertrag A2.4, F3) |
| Läuft in | WordPress (geplantes Plugin für Baustein 4), nicht im Radar |
| Offizieller Weg | Stripe Checkout, gehostete Seite: `POST /v1/checkout/sessions` mit `mode=payment`, `line_items`, `client_reference_id` (Buchungsnummer, bis 200 Zeichen), `metadata`, `success_url` mit `{CHECKOUT_SESSION_ID}`, `cancel_url`, `expires_at` 30 Minuten (kleinster erlaubter Wert; Reservierung der Tage 35 Minuten, F3). Erstattung: `POST /v1/refunds` zur Zahlung. Kartendaten sieht die Website nie |
| Auth | geheimer Schlüssel (Test `sk_test_…`, live `sk_live_…`) im Server; Webhook-Geheimnis `whsec_…` je Endpunkt und Modus |
| Webhook | HTTPS-Endpunkt in WordPress; Ereignisse nur, die gebraucht werden: `checkout.session.completed`, `checkout.session.async_payment_succeeded`, `checkout.session.async_payment_failed`, `checkout.session.expired`, Erstattungsereignisse. Prüfung der Kopfzeile `Stripe-Signature` (HMAC-SHA256, nur `v1`) gegen den **unveränderten** Rohtext; Zeittoleranz 5 Minuten, nie 0; Ereignis-ID merken, Dubletten ignorieren; Reihenfolge ist nicht garantiert; sofort 2xx antworten, Arbeit danach; Webhook-Route ohne CSRF-Prüfung, aber nur mit gültiger Signatur (docs.stripe.com/webhooks, Abruf 13.11.2026) |
| Zweiter Abgleich | bei der Rückkehr auf die Website die Checkout-Session abrufen (F3); „bezahlt“ setzt nur eine geprüfte Meldung oder dieser Abruf |
| Grenzen | Stripe wiederholt Webhooks im Livebetrieb bis zu drei Tage mit wachsendem Abstand, in der Sandbox dreimal über einige Stunden; manuelles Nachsenden bis 15 bzw. 30 Tage. Bis zu 16 Ziele je Konto |
| Fehler und Verhalten | ungültige Signatur oder falscher Zeitstempel: 400, nichts ändern, Protokoll. Doppelte Meldung: nichts ändern. Zahlung fehlgeschlagen oder Session abgelaufen: Tage frei. Erstattung scheitert: Warnung in der Buchungsliste, Mensch (F3). Aufrufe an Stripe mit Idempotenzschlüssel, damit eine Wiederholung nichts doppelt anlegt |
| Testmodus | Testschlüssel und Test-Webhook-Geheimnis; Testkarten von Stripe (Erfolg 4242 4242 4242 4242, Ablehnung 4000 0000 0000 0002); `stripe listen --forward-to …` und `stripe trigger …` für Ereignisse; in automatischen Tests ein Fake mit selbst signierten Meldungen (`tests/wp/test_buchung.py`, geplant) |
| Variablen (Vorschlag, App `tamil-web`) | `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`; Modus folgt aus dem Schlüssel; im Echtbetrieb aus, bis Auftragsverarbeitung und Rechtstexte vorliegen |
| Stand | gebaut im Plugin `tamil-site` (`includes/werbung-stripe.php`), geprüft nur gegen den Fake (`tests/wp/test_werbung.py`, `tests/wp/stripe_fake.php`); nicht gegen Stripe selbst (Konto und Testschlüssel fehlen). Schalter „werbung“ Standard aus |
| KBS liefert | Stripe-Konto (Identitätsprüfung dauert Tage), Auszahlungskonto, Einstellung zu Belegmails bei Stripe, Preise, Steuerangabe, Verkaufsbedingungen (Zuarbeit Nr. 7, 8). Gebühren von Stripe sind Gebühren Dritter (§3 Abs. 2) |

## 12. Coolify (Betrieb)

| Punkt | Festlegung |
|---|---|
| Zweck | Stand der beiden Apps lesen, Deploy auslösen, Variablen setzen (nur Namen ausgeben), Volumes lesen |
| Weg | REST `/api/v1` der eigenen Coolify-Instanz: `GET /applications/{uuid}`, `GET /deploy?uuid=…&force=…`, `GET /deployments/{uuid}`, `GET /applications/{uuid}/envs`, `PATCH /applications/{uuid}/envs/bulk`, `GET /applications/{uuid}/storages` (`tools/coolify.py`) |
| Auth | Bearer-Token (`COOLIFY_TOKEN`), Adresse `COOLIFY_URL` |
| Apps | „tamil.de“ (Radar mit Cockpit) und „tamil-web“ (WordPress); Geheimnisse aller Schnittstellen liegen als Laufzeit-Variablen dort (`docs/betrieb.md`) |
| Fehler und Verhalten | Werte werden nie ausgegeben; Antworten werden geschwärzt angezeigt |
| Stand | gebaut. Offen: Tor B2, die beiden bei der Einrichtung benutzten Tokens widerrufen; Zielzustand DNS-Name `coolify.hk-growthoperator.de` und ein Token ohne Root-Rechte |
| KBS liefert | nichts (Betrieb bei Luis) |

## 13. Was ohne Konten des Auftraggebers nicht live gehen kann

| Funktion | Fehlt | Bis dahin |
|---|---|---|
| Instagram und Facebook (B2, Tests T1, T2) | Professional-Konto, Seite, Business-Portfolio, App, Token, ggf. PPA und Unternehmensverifizierung | Trockenmodus, Fake-Schnittstelle |
| WhatsApp-Entwurf (B3, T3) | Link zum Kanal | Entwurf ohne Link zum Kanal |
| Werbebuchung mit Zahlung (A2.4, T5, T6) | Stripe-Konto von KBS, Preise, Bedingungen | Testmodus mit Testkarten |
| Schreiben ohne Zutun | Anthropic-Schlüssel und Kostenfreigabe (Tor B1) | Agent-Modus |
| KI-Symbolbilder | Ja von Luis, Kostenfreigabe, Google-Projekt mit Abrechnung | Bildkarte |
| Automatische Stockfotos | Pexels-Schlüssel | Commons, Register, Bildkarte |
| Livegang der Website | Domain tamil.de (Tor B3), Rechtstexte, Auftragsverarbeitung | Vorschau-Adresse, für Suchmaschinen gesperrt |

## 14. Variablen (nur Namen)

| Name | App | Geheim | Stand |
|---|---|---|---|
| `WP_URL`, `WP_USER`, `WP_POST_STATUS`, `WP_SEO_META` | Radar | nein | gesetzt (bis auf `WP_SEO_META`) |
| `WP_APP_PASSWORD` | Radar | ja | gesetzt |
| `RADAR_APP_PASSWORD` | Website | ja | gesetzt |
| `RADAR_COCKPIT_URL`, `WP_ENVIRONMENT_TYPE` | Website | nein | gesetzt bzw. beim Livegang |
| `ANTHROPIC_API_KEY` (oder `RADAR_ANTHROPIC_API_KEY`) | Radar | ja | offen (Tor B1) |
| `RADAR_MODELL_<ROLLE>`, `RADAR_MODEL` | Radar | nein | Standard aus dem Code |
| `RADAR_BUDGET_TAG_USD`, `RADAR_BUDGET_MONAT_USD`, `RADAR_ENTWUERFE_TAG` | Radar | nein | gesetzt |
| `RADAR_BUDGET_WARNUNG` | Radar | nein | Standard aus dem Code (0,8) |
| `GEMINI_API_KEY` | Radar | ja | offen |
| `BILD_MODELL`, `BILD_GROESSE`, `BILD_MODUS`, `BILD_REIHENFOLGE`, `BILD_POOL_DIR`, `RADAR_KI_BILDER_JE_ARTIKEL` | Radar | nein | Standard aus dem Code |
| `BILD_KI_FREIGABE`, `RADAR_KI_BILDER_TAG` | Radar | nein | neu (Vorschlag) |
| `PEXELS_API_KEY` | Radar | ja | offen |
| `UNSPLASH_ACCESS_KEY` | Radar | ja | entfällt |
| `META_GRAPH_VERSION`, `META_IG_USER_ID`, `META_PAGE_ID` | Radar | nein | im Code (F4), nicht gesetzt |
| `RADAR_SOCIAL` (Funktionsschalter), `RADAR_SOCIAL_LIVE` (live statt trocken; ersetzt den Vorschlag `SOCIAL_MODUS`) | Radar | nein | im Code (F4), nicht gesetzt = aus bzw. trocken |
| `META_ZUGANG` | Radar | ja | im Code (F4), offen (Konten von KBS) |
| `WHATSAPP_KANAL_URL` | Radar | nein | im Code (F4), offen (Link von KBS) |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | Website | ja | im Code verwendet, Werte offen (Stripe-Konto von KBS) |
| `RADAR_AGENT_TOKEN`, `RADAR_LESE_TOKEN` | Radar | ja | gesetzt |
| `COOLIFY_URL`, `COOLIFY_TOKEN` | Werkzeug (lokal) | Token ja | Tor B2 |

## Quellen (offizielle Seiten, Abruf 13.11.2026)

- Instagram Content Publishing: https://developers.facebook.com/docs/instagram-platform/content-publishing/
- Instagram, `POST /{ig-user-id}/media`: https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media
- Facebook Pages API, Beiträge: https://developers.facebook.com/docs/pages-api/posts
- Facebook, Page Photos: https://developers.facebook.com/docs/graph-api/reference/page/photos/
- Meta, Ratenlimits: https://developers.facebook.com/docs/graph-api/overview/rate-limiting/
- Meta, Zugriffsstufen: https://developers.facebook.com/docs/graph-api/overview/access-levels/
- Meta, langlebige Token: https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived/
- WhatsApp, Opt-in: https://developers.facebook.com/docs/whatsapp/overview/getting-opt-in/
- WhatsApp-Kanäle in der Content Library API (nur lesen): https://developers.facebook.com/docs/content-library-and-api/content-library-api/guides/wa-channel
- Stripe Webhooks: https://docs.stripe.com/webhooks
- Stripe Checkout Session anlegen: https://docs.stripe.com/api/checkout/sessions/create
- Gemini-API, Preise und Bilderzeugung: https://ai.google.dev/gemini-api/docs/pricing, https://ai.google.dev/gemini-api/docs/image-generation (weitergeleitet auf aistudio.google.com/docs/…)
- Wikimedia, Ratenlimits: https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits
- Wikimedia, API-Etikette: https://www.mediawiki.org/wiki/API:Etiquette
- Wikimedia Foundation, User-Agent-Richtlinie: https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy
- Pexels API: https://www.pexels.com/api/documentation/
- Unsplash API-Richtlinien: https://help.unsplash.com/en/articles/2511245-unsplash-api-guidelines
- WordPress REST, Authentifizierung: https://developer.wordpress.org/rest-api/using-the-rest-api/authentication/
- Anthropic: Modellübersicht und Preise (Stand 03.11.2026), Python-SDK `anthropic`
