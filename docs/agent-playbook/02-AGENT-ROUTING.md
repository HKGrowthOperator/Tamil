# Agent-Routing und Aufgabenbesitz

## Bestehende Rollen nutzen

Die folgenden Rollen sind auf dem geprüften Ausbau-Branch bereits in `.claude/agents/` vorhanden.
Vor Ausführung die jeweilige Datei lesen; diese Tabelle ersetzt ihre Grenzen und Tools nicht.

| Agent | Auftrag | Primäre Schreibbereiche | Übergabe |
|---|---|---|---|
| referenz-scout | Gezielte Quellen-/Skill-/Referenzsuche | Zugewiesene Referenzdokumentation | Quelle, Stand, Nutzen, Rechte, Entscheidung |
| art-director | Gewählte visuelle Richtung ausarbeiten | Zugewiesene design/richtungen/-Probe | Vorschau und Brief-Abgleich |
| design-kritiker | Ergebnis unabhängig messen | design/kritik/ | P0/P1/P2, Ort und Messwert; keine Designerbegründung lesen |
| theme-bauer | Bestätigte Gestaltung in WordPress | wordpress/themes/tamil/ | Theme-Diff und Seitentypen |
| cockpit-bauer | Interne Arbeitsoberfläche | news_radar/web/ | Zustände, Rollen, Bedienabläufe |
| plugin-bauer | Einreichungen, Verzeichnis, Werbung, WP-REST | wordpress/plugins/ und zugewiesene WP-Tests | Datenmodell, Rechte, API, Migration, Tests |
| radar-entwickler | Jobs, Agentlogik, Adapter, Verarbeitung | news_radar/ und zugewiesene Tests | Zustände, Failure-/Retry-Verhalten, Kosten |
| code-pruefer | Unabhängige fachliche Codeprüfung | Befundbericht | Diffbezogene Fehler mit Reproduktion |
| qa-pruefer | Browser und reale Nutzerwege | Zugewiesene QA-Nachweise | URL, Viewport, Ablauf, Befund |
| redakteur | Belegte redaktionelle Arbeit | Zugewiesener redaktioneller Ablauf | Fakten, Quellen, Rechte; keine Produktmigration |
| migrator | Bestehende Inhalte übernehmen/prüfen | Zugewiesene Importwerkzeuge | Mengen, IDs, Redirects, Wiederholbarkeit |

## Koordinator

Ein Koordinator hält Scope, Dateibesitz, Integration, Freigaben und Abschluss zusammen.
Er startet keine neue Agentenstruktur neben der vorhandenen. Standard: höchstens zwei parallele
Implementierungsbereiche insgesamt. Reviewer folgen auf ein integriertes Ergebnis; keine rekursiven Kaskaden.

Der lokale Runner bestimmt die tatsächlichen Modelle und Tools. Die in Claude-Agentdateien enthaltenen
Modell-/Toolfelder sind keine Aussage über Codex-, Hermes- oder Grok-Verfügbarkeit.
Kein festes Qualitätsversprechen nach Modellname. Bei einem anderen Runner die Rollen als separate,
begrenzte Arbeitsaufträge ausführen und dieselben Schreibgrenzen einhalten.

## Sinnvolle Paare

| Baustein | Bereich A | Bereich B | Vorher festlegen |
|---|---|---|---|
| Einreichungen F1 | plugin-bauer: Formular, Speicherung, Abruf | radar-entwickler: Eingang, Prüfung, Freigabe | Felder, Status, Poll-/Ack-Verhalten, Rollen |
| Verzeichnis F2 | plugin-bauer: Profile, Suche, Änderungen | radar-entwickler: Dubletten-/Fehlfeldvorschläge | Kanonische ID, Revision, Freigabeverfahren |
| Werbung F3 | plugin-bauer: Bestand, Buchung, Zahlung, Ausspielung | radar-entwickler: nur vereinbarte Cockpit-Sicht/Prüfaufgaben | WordPress bleibt finanziell maßgeblich; kein zweites Buchungsledger |
| Social F4 | radar-entwickler: Regeln, Queue, Meta-Adapter | plugin-bauer: veröffentlichte Inhalte sicher bereitstellen | Kanal-ID, Inhaltsrevision, Rechte, Idempotenz |
| Design nach G3 | theme-bauer | cockpit-bauer | Freigegebene Tokens, Komponenten, Formzustände |
| Migration | migrator | QA nach sinnvoller Teilabgabe | Quellen-ID, Originaldatum, Mengen/Redirects |

Nicht parallel an derselben Schema-/API-/Shared-Datei arbeiten. Der Koordinator weist gemeinsame Dateien
genau einem Besitzer zu; andere liefern Änderungswünsche. Erst Schnittstellen klären, dann Agenten starten.

## Auftragsvorlage je Agent

- Ergebnis: ein vollständiger Nutzerablauf oder konkret messbares Teilresultat.
- Start: Repo, Branch, SHA, relevante Festlegung, bisherige Implementierung.
- Schreibbesitz: genaue Pfade; gemeinsame Dateien mit benanntem Eigentümer.
- Schnittstelle: Route/Version oder bestehende Funktion, Felder, Rechte, Fehler, Idempotenz.
- Nachweise: passende Tests, Browser-/Providergrenze, Akzeptanzfälle.
- Grenzen: Echtbetrieb/Testmodus, keine Secrets, keine unzulässigen Außenwirkungen.
- Abgabe: Diff/Commit, Ergebnis, tatsächliche Prüfungen, offene Punkte, nächste Integration.

## Entwicklungs- und Laufzeitagenten trennen

Der vorhandene Radar implementiert Produktionsjobs; Entwicklungsagenten implementieren diese Software.
Ein Codex-/Claude-/Hermes-/Grok-Adapter darf nur die vorhandene begrenzte Agent-API nutzen,
nachdem Authentisierung und Funktionsumfang belegt wurden. Keine gemeinsamen Admin-Tokens.
Worker-Identität, erlaubte Jobtypen, claim/lease, Revision, Budget und Stopp am Übergang prüfen.

Empfohlenes Modellrouting nach Aufgabenqualität und Kosten: Extraktion/Klassifikation klein beginnen;
Schreiben/Faktenabgleich bei belegtem Bedarf leistungsfähiger; Freigabeentscheidungen nicht durch
Modellkonsens ersetzen. Nur tatsächlich konfigurierte Provider verwenden. Mocks, menschliche Recherche,
Agent-Modus und bezahlter Modelllauf im Protokoll auseinanderhalten.
