# Tamil.de – aktueller Produkt- und Codebefund

Stand: 11.11.2026. Nur lesender Audit über den verbundenen GitHub-Zugang. Keine Änderung, Installation, Veröffentlichung oder Ausführung gegen Kundensysteme. Maßstab: Anlage 1 des Gesamtvertrags vom 11.11.2026 und die tatsächlich vorhandene Umsetzung. Aussagen aus Projektprotokollen sind als solche gekennzeichnet; sie ersetzen keine von uns durchgeführte Laufzeitabnahme.

## 1. Entscheidender Befund

Das Hauptrepo ist **HKGrowthOperator/Tamil**. Das Produkt hat schon eine erhebliche technische Grundlage und ein ausführliches Agentensystem. Die jüngste Arbeit liegt **nicht auf main**, sondern auf **claude/radar-multiagent**. Genau dort weiterarbeiten und die bestehenden Regeln ergänzen. Kein zweites Cockpit, keine neue Agentenlandschaft und kein weiterer Website-Prototyp im Archiv anfangen.

Die vertraglich entscheidenden Lücken sind **Einreichungen, Community-Verzeichnis, Werbe-Self-Service mit Zahlung und Instagram/Facebook/WhatsApp-Vorbereitung**. Die vorhandene KI-Redaktion ist weiter als diese Umsatz- und Community-Funktionen. Mehr Orchestrierungssoftware allein schließt diese Lücken nicht.

## 2. GitHub-Stand, Branches und Release

| Branch | Am 11.11. gelesener Commit | Befund |
|---|---|---|
| main | `2b09d51763f7f72d74db173b11f8a08fe3980e86` | Merge von PR #1 am 09.11.2026. Enthält Website-Theme, tamil-site/tamil-radar und Radar v1. |
| claude/news-radar | `91b11bada7c4ada1eeb54802afabc068a074587f` | Stand vom 20.10.; identischer Dateibaum wie main. main liegt nur um den Merge-Commit voraus. Frühere Festlegung „news-radar ist Baseline statt main“ ist inzwischen historisch. |
| claude/radar-multiagent | `181c8337bd47e9ebf284f584501d64e5136d9726` | 196 Commits vor dem gemeinsamen Vorfahren; gegenüber main `diverged`, 196 voraus, 1 zurück. Darin liegen der aktuelle Betriebsstand, Vertragsledger, Agenten, Designarbeit und Cockpit-Grundlage. |

[PR #1](https://github.com/HKGrowthOperator/Tamil/pull/1) ist zusammengeführt. [PR #2](https://github.com/HKGrowthOperator/Tamil/pull/2) ist offen gegen main; Update im gelesenen Snapshot 11.11.2026, 19:04 UTC. Das Zurückliegen um einen Commit erklärt sich durch den main-Merge; es ist kein Beweis für einen verlorenen Feature-Commit. Keine unkontrollierte Branchbereinigung.

**Prüfstatus:** Die Actions-API meldete `total_count: 0`, der kombinierte Commitstatus für den v2-Head `pending` bei `statuses: []`. Das ist keine bestandene CI. Die PR-Beschreibung nennt einen früheren Lauf mit 439 bestandenen und 10 übersprungenen Tests, beschreibt aber noch „Grundlage offen“ und „F3/F4 folgen“, obwohl die aktuellen Dateien Grundlage-Code und F3/F4 bereits enthalten. Die PR-Beschreibung ist daher nicht vollständig aktuell. Vor dem nächsten Release um den tatsächlichen Stand des dann integrierten Heads neu schreiben.

**Regel:** Commit, Prüfstand und Deployment-Stand getrennt führen. Aus `git push` folgt kein Deploy, aus einem bestehenden Deployment folgt kein Nachweis, dass dessen Commit dem aktuellen Head entspricht.

## 3. Tatsächliche Systemzuordnung

Quelle: `CLAUDE.md`, `docs/betrieb.md` und `docs/entscheidungen.md` auf dem v2-Commit.

| System | Code | Dokumentierte Adresse | Aussagegrenze |
|---|---|---|---|
| Bisheriges Magazin | Bestehende öffentliche WordPress-Seite | https://www.tamil.de | Nur lesend behandeln; Migration darf diese Quelle nicht beschreiben. |
| Relaunch/Testsystem | `wordpress/`, Coolify-App `tamil-web` | https://tamil-web.167.233.76.202.sslip.io | Dokumentierter Vorschau-Host; laut Repo noch bisheriges Theme, neues Design folgt. |
| Radar und internes Cockpit | `news_radar/`, `news_radar/web/`, Coolify-App `tamil.de` | https://tamil.hk-growthoperator.de | Internes Redaktionssystem mit Login und getrennten Bearer-Zugängen. |
| Designentwürfe | `design/richtungen/`, `design/brief.md`, `design/kritik/` | Separate Abnahme-Artefakte | Keine produktive Website. `klar2` von Luis intern bestätigt, Auftraggeberurteil G2 ausstehend laut Repo. |
| `produkt.tamil.de`, `imatutamil.de` | Keine Zuordnung in den gelesenen System-/Betriebsdokumenten | Vom Nutzer genannte Bezeichnungen | Nicht ohne DNS-/Deployment-Nachweis einem Repo oder System zuordnen. |

Beide Coolify-Apps sind laut Betriebsdokument aus `claude/radar-multiagent` gebaut; nach Merge von PR #2 soll die Quelle main werden. Aktueller Deploy-Commit und Gesundheit wurden in diesem Codeaudit nicht über Coolify verifiziert. Die dokumentierte Umgebung nutzt WordPress mit SQLite sowie eine eigene SQLite-Datenbank für den Radar. Keine automatische Migration zu Supabase, AWS oder einem neuen Framework begründet.

## 4. Was bereits vorhanden ist

| Bereich | Evidenz im Code/Repo | Reife und Grenze |
|---|---|---|
| WordPress-Magazin | `wordpress/themes/tamil/` mit Startseite, Kategorie, Artikel, Suche, Events, Kontakt; `wordpress/plugins/tamil-site/` | Konkrete Umsetzung, kein leeres Konzept. Kontaktseite ist noch kein Einsendeformular. |
| Contentübernahme | `tools/migration.py`, `docs/abnahme/2026-11-11-uebernahme.md` | Protokoll berichtet 532 Beiträge, 7 Seiten, 1445 Medien, 25 Weiterleitungen; 10er-Stichprobe, 25 Redirects, idempotenter Zweitlauf, 21 Sichtaufnahmen. Nicht durch diesen Audit erneut ausgeführt. |
| SEO, Cache, Zustimmung, Upgrades | `tamil-site/includes/{seo,indexierung,leistung,consent,upgrade,funktionen}.php`, `tests/wp/` | Code vorhanden. Cookie-Schalter standardmäßig aus; Rechtstexte/KBS fehlen. Vorschau ist noindex bis `WP_ENVIRONMENT_TYPE=production`. |
| Werbeausspielung | `tamil-site/includes/ads.php` | Sechs Flächen, Eigenanzeigen, konfigurierbares Banner-HTML/Advanced-Ads-Anbindung. Kein Beweis für Buchungs- oder Zahlungssystem. |
| Quellen-Radar | `sources.py`, `filtering.py`, `kino_providers.py`, `net.py`, `sources.toml` | DACH-/Community-Filter, Quellenabruf und Kino-Pfade; v2 hat zusätzliche Quellen-/Netzschutzregeln. |
| Redaktion v2 | `news_radar/agents/`, `workflow/`, `prompts/` | Signal, Cluster, Recherche, Gate, Text, Faktencheck, Lektorat, SEO, Medien; Claims, Quellen, Versionen und Kosten. |
| Jobs und Kosten | `workflow/jobs.py`, `costs.py`, `providers.py`, `repo.py` | Idempotenzschlüssel, atomarer Job-Claim, Besitzprüfung, Backoff, Dead-Letter, Budgetwartezeit. Nicht durch Mengenangabe „Agenten“ ersetzen. |
| Menschliche Freigabe und WP-Publishing | `web/redaktion.py`, `publisher.py`, `wordpress.py`, `tamil-radar/includes/rest.php` | Freigegebenes wird nach WordPress übertragen; kein Social-Publishing. Plugin-Pfad und Core-REST-Fallback haben unterschiedliche Fähigkeiten. |
| Owner-Cockpit | `web/rechte.py`, `web/betrieb.py`, `schalter.py`, entsprechende Templates | Rollen admin/redaktion/leser, serverseitige Rechte, Stop je Kanal/gesamt, Protokoll/Export und Zeitplan; Rollenverteilung in F0 noch Vorschlag. |
| Externe Agentenanbindung | `web/api.py`, `agent_v2.py` | Getrennte Tokens: Bericht lesen, Aufgaben exportieren/importieren, Nachtrag vorschlagen. Bestehende Integrationsgrenze für weitere berechtigte Clients. Kein Zugriff ohne Capability-/Token-Prüfung. |
| E-Mail-Abgrenzung | `notify.py`, `tests/test_kein_mailversand.py` | Notify nutzt Webhooks, keine E-Mail. Das gilt auch für die gelesene main-Fassung. v2 hat zusätzlich einen statischen Mail-Musterscanner. Dieser beweist keine vollständige Kontrolle fremder WordPress-Core-/Providerkonten. |

## 5. Vertragslücken und konkrete Umsetzungspakete

Der aktuelle Scope ist schon unter `docs/vertrag/leistungen.md` erfasst. Diese Datei fortführen und pro Punkt Implementierung, Test, echte Anbindung und Abnahme ergänzen; keinen konkurrierenden zweiten Scope als Wahrheit daneben legen.

| Paket | Jetzt nachweisbar | Fehlt / nächster Ergebnisumfang | Geeignete Verantwortliche |
|---|---|---|---|
| F0 Grundlage | Technik für SEO, Cache, Rechte, Stop, Protokoll, Zeitplan und Consent vorhanden | Rollenentscheidung und Consent-/Rechtstexte; Aufbewahrung konkret umsetzen; mobile Performancemessung ausstehend | plugin-bauer + radar-entwickler, getrennte Pfade |
| F1 Einreichungen | Seiten/Entwürfe und redaktioneller Kern vorhanden | Eigene Formulare, private Uploads, Spamabwehr, WordPress-Eingang, Abholen durch Radar, Bearbeitungs-/Freigabeablauf, Eventfelder Ende/Preis/Veranstalter | plugin-bauer für WP, radar-entwickler für Eingang im Cockpit |
| F2 Verzeichnis | Spezifikation vorhanden | Public Profile/Search/Filter, Eintrags- und Änderungsvorschläge, private Einsenderdaten, Feld-/Dublettenprüfung, Klassifikation, Feldvergleich und manuelle Freigabe, Premium nur Verwaltung | plugin-bauer + radar-entwickler |
| F3 Werbebuchung | Sechs Werbeplätze, Spezifikation und Stripe-Entscheidung vorhanden | Angebotspreise, atomare Kapazität/Reservierung, Uploadprüfung, Checkout/Webhooks, Zahlungsabgleich, Kampagnenzustände/Laufzeit, Kundenübersicht, Pause/Ende/Statistik | plugin-bauer (Transaktionen/WP); radar-entwickler nur notwendige Cockpit-Integration |
| F4 Social | WordPress-Artikel als Quellobjekte, Schalter und Agentencockpit vorhanden | Social-Outbox, versionierte KBS-Regeln, Meta-Adapter, Instagram + Facebook mit separaten Status, Abgleich unklarer Ausgänge, WhatsApp-Paket/Kopieren/Markierung | radar-entwickler; code-pruefer und qa-pruefer für Provider-/Bedienprüfung |
| Design | `klar2` und aktuelle harte Kriterien vorhanden | Auftraggeberentscheidung G2, vollständige Probeseite G3, Theme-/Cockpitübertragung, QA | art-director → unabhängiger design-kritiker → theme-bauer und cockpit-bauer |
| Abnahme/Betrieb | Migrationsprotokoll und Werkzeuge vorhanden | T1–T7 tatsächlich schließen, aktuelle integrierte Prüfung, dokumentierter Deploy, Wiederherstellung, Übergabe, Live-Domain | Koordinator + qa-pruefer + jeweilige Spezialisten |

F1–F4 sind zum gelesenen Head Spezifikationen, keine fertigen Module. Einzelne zukünftige Testdateien in `leistungen.md` stehen als geplante Pfade; sie sind im gelesenen Dateibaum noch nicht vorhanden. Nicht als laufende Tests ausgeben.

### Zusätzliche technische Präzisierungen für F3/F4

- **Buchungsrettung:** F3 schlägt Wiederfinden einer Buchung mit Buchungsnummer und E-Mail vor. Das sind leicht bekannte Werte. Vor Implementierung mit einem berechtigten, erratungsfesten Zugangsverfahren und sauberer Rechte-/Datensicht spezifizieren. Ein geheim gehaltener Link braucht starke Zufälligkeit, begrenzte Reichweite und Widerruf; keine Buchungsdaten im öffentlichen Cache oder Suchindex.
- **Zahlung:** Browser-Rückkehr und Erfolgstext dürfen keine Zahlung beweisen. Signatur prüfen, Ereignis-ID deduplizieren, Betrag/Währung/Bestellung/Konto abgleichen, Ausgänge bei Timeout reconciliieren. Reservierung und belegte Tage in derselben Transaktion absichern; Race-Test mit zwei zeitgleichen Kunden. Refunds ebenfalls idempotent mit Statusabgleich.
- **Social:** Pro Beitrag, Revision und Kanal ein stabiler Idempotenzschlüssel. Instagram-Erfolg bei Facebook-Ausfall darf keinen zweiten Instagram-Post auslösen. Provider-ID und Regelnversion persistieren. Altbestand wird durch Cutover-/Baseline-Markierung ausgeschlossen. Rechte an Website-Bildern erlauben nicht automatisch Social-Nutzung.
- **Buchungsanzeigen:** Aktiv nur bei verifizierter Zahlung UND Freigabe UND erlaubtem Zeitraum UND nicht pausiert. Zeitgrenzen, Sommer-/Winterzeit und Wartungsneustart testen. Maße/Dateityp/Dateigröße nicht nur im Browser prüfen.
- **Datenverantwortung:** WordPress hält öffentliche Inhalte, Eingaben/Verzeichnis/Angebote/Buchungen; Radar hält Jobs, Vorschläge, Freigabefluss, Regelprüfungen und Ausführungsprotokoll. Keine frei erfundene dritte Datenkopie im ChatGPT-/Claude-Gedächtnis.

## 6. Vorhandene Agenten richtig nutzen

Die Entwicklungsagenten in `.claude/agents/` sind nicht dasselbe wie die Laufzeitrollen unter `news_radar/agents/`. Ersteres baut Software, letzteres verarbeitet redaktionelle Aufgaben. Diese Ebenen in allen Prompts trennen.

| Vorhandener Entwicklungsagent | Zuständigkeit | Darf nicht stillschweigend übernehmen |
|---|---|---|
| referenz-scout | Belegte Referenzen und Material | Produktentscheidung oder Designabnahme |
| art-director | Eine konkrete Richtung/Probeseite | Produktivumbau ohne den bestehenden Designentscheidungsstand |
| design-kritiker | Unabhängige Kritik anhand Brief/Messwerten | Begründung des Gestalters als Evidenz übernehmen |
| theme-bauer | `wordpress/themes/tamil/` | Geschäftslogik/Payment in Templates verstreuen |
| cockpit-bauer | Erscheinung/Bedienung `news_radar/web/` | Parallel mit radar-entwickler dieselben Dateien ändern |
| plugin-bauer | `wordpress/plugins/`, Migrations-/Integrationsvertrag | Neue Optik nebenbei oder ungesicherte Zahlungszustände |
| radar-entwickler | Radar, Jobs, Integration, Cockpitlogik | Gates/Budget/Schutz lockern, um Tests grün zu bekommen |
| qa-pruefer | Browser, Bedienung und konkrete Nachweise | Fake-/Mock-Ergebnis als echte Anbieterabnahme nennen |
| code-pruefer | Relevanter integrierter Diff, Fehler/Rennen/Security | Rekursive Prüferketten starten |
| redakteur | Redaktionelle Inhalte über Agent-Export/Import | Quellcode, Anbieterzugänge oder Freigaben umgehen |
| migrator | Inhaltsexport/-import und Prüfliste | Die alte tamil.de als beschreibbares Ziel nutzen |

**Steuerung:** Ein Koordinator vergibt Ticket, erlaubte Pfade, Schnittstellen, Prüfkriterien und Übergabeformat. Standard höchstens zwei unabhängige Implementierungsbereiche gleichzeitig, entsprechend Agent-Playbook R-03. Ein Designer und ein Pluginentwickler können parallel arbeiten, solange Pfade und Schnittstellen getrennt sind; zwei Schreiber im selben Cockpitpfad brauchen nacheinander geplante Arbeit. Keine Unteragenten aus Unteragenten. Modellangaben im Repo sind bestehende Anbieter-Konfiguration, kein Qualitätsnachweis und keine Verpflichtung für andere Runtimes.

## 7. Dateien und Regeln, die erhalten bleiben

Bereits vorhanden auf dem v2-Branch:

- Einstieg: `CLAUDE.md`, `README.md`, `PRODUCT.md`, `DESIGN.md`.
- Laufende Wahrheit: `docs/entscheidungen.md`, `docs/architektur.md`, `docs/betrieb.md`, `docs/ablaeufe.md`, `docs/vertrag/leistungen.md`, `docs/abnahme/`.
- Bereichsregeln: `.claude/rules/{betrieb,design,radar,vertrag,wordpress}.md`.
- Commands: `/status`, `/design-runde`, `/design-ausbau`, `/design-umsetzung`, `/research`, `/website-live`, `/release`, `/vertrag-bau`, `/abnahme-vertrag`.
- 11 Entwicklungsagenten und 12 Skill-Einstiege: `coolify-betrieb`, `impeccable`, `pruefen`, `radar-auswertung`, `radar-research`, `tamil-cockpit`, `tamil-kritik`, `tamil-marke`, `tamil-migration`, `tamil-richtung`, `tamil-screens`, `tamil-theme`.
- `prototyp/` ist Archiv; nur die JSON-Inhalte darin dienen noch als Datenquelle. Dort keine neue Anwendung bauen.

Eine neue `AGENTS.md` sollte als dünner Einstieg für andere Agenten diese kanonischen Dateien referenzieren. Bereits vorhandene Regeln nicht durch einen allgemeinen Riesenprompt überschreiben. Fachliche Zusatzregeln in bestehende Bereichsdateien oder klar benannte Ergänzungsdokumente einarbeiten.

## 8. Empfohlene nächste konkrete Reihenfolge

1. Im richtigen v2-Branch den aktuellen Head neu feststellen und laufende Arbeit sichern. Scopeledger und PR #2 synchronisieren; keine Branchhistorie umschreiben.
2. F0 als vorhandene Technik behandeln und offene Rollen-/Datenschutz-/Textentscheidungen sichtbar halten. Bezahlsystem/API-/Domainaktionen nur gegen die richtige KBS-Umgebung.
3. Zwei unabhängige Bereiche: F1 WordPress-Formulare und Radar-Eingang; danach F2 auf derselben Eingangs-/Freigabegrundlage. Gemeinsame Schema-/APIänderungen vorab als Vertrag festlegen.
4. F3 als abgeschlossene Buchungsvertikale von Angebot bis Laufzeitende bauen. Anbieter zunächst Sandbox; echte Kapazitäts- und Zahlungsfehlerfälle gehören zur Abnahme.
5. F4 auf bereits veröffentlichten Website-Inhalten aufsetzen. Instagram und Facebook haben eigene Ausführungszustände; WhatsApp zunächst Entwurf. Keine E-Mail-Automation hinzufügen.
6. Die bereits gewählte Designrichtung weiterführen. Keine neue Referenzrunde anfangen, bevor das aktuelle G2-/G3-Ergebnis berücksichtigt ist.
7. Auf dem integrierten Stand Python-Tests und `news_radar abnahme`, für WordPress Lint/WPCS und echte WP-Tests; übersprungene WP-Tests ausdrücklich ausweisen. Browser bei 390/820/1280, Payment-/Meta-Tests und fachliche T1–T7 getrennt dokumentieren.
8. Erst nach konkreter Betriebs-/Fachabnahme PR/Deploy/Domainstand abschließen. Vier Wochen Agent-Feinjustierung und drei Monate Betreuung mit getrennten Startdaten führen; sie beginnen nicht mit dieser Dokumentation.

## 9. Quellen und Beleggrenzen

Alle Codepfade dieser Auswertung beziehen sich auf `181c8337bd47e9ebf284f584501d64e5136d9726`, außer ausdrücklich genannter main-/news-radar-Vergleich. Dauerhafte URL für eine Datei: `https://github.com/HKGrowthOperator/Tamil/blob/181c8337bd47e9ebf284f584501d64e5136d9726/<pfad>`.

Gelesen: `CLAUDE.md`, `README.md`, Vertragsledger und F0–F4, `docs/{architektur,betrieb,ablaeufe,entscheidungen}.md`, Übernahmeprotokoll, `news_radar/{agent_v2,publisher,notify}.py`, `web/{api,rechte,__init__}.py`, `workflow/{jobs,orchestrator}.py`, `tamil-site/includes/{ads,funktionen}.php`, `tamil-radar/includes/rest.php`, `tests/test_kein_mailversand.py`; rekursive Dateibäume beider Hauptstände; GitHub-Compare, PR- und Commit-/Actionsmetadaten.

Nicht behauptet: vollständiger Securityaudit jeder Codezeile; bestandene lokale Tests dieses Audits; live bestätigte Migration, Deploy-/Meta-/Stripeverbindung; DNS-/Deploymentzuordnung von produkt.tamil.de oder imatutamil.de. Ältere PR-Testzahlen und Migrationszahlen sind Berichte aus dem Repo, keine neuen Testergebnisse.
