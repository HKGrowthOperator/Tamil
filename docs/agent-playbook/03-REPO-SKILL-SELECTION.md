# Tamil.de: Auswahl und Einsatz der GitHub-Skills
Stand: 11.11.2026. Gegen die erreichbaren HK-Forks geprüft. Zweck: reproduzierbare Auswahl für Website, Cockpit und Engineering. Das ist eine Quellenprüfung, keine Bestätigung einer Installation in Luis' Claude-, Codex- oder Hermes-Umgebung.

## Wichtigste Ergebnisse

1. Der gemeinte Designer lässt sich konkret zuordnen: `HKGrowthOperator/skill` verweist auf `emilkowal.ski/skill` und enthält `skills/emil-design-eng/SKILL.md`, das sich ausdrücklich auf **Emil Kowalski** bezieht. „Iman Kowalski“ nicht als separates Tool installieren.
2. Der aktuelle `taste-skill` enthält **ein** Skill mit Installationsnamen `design-taste-frontend`. Der echte Pfad ist `skills/taste-skill/SKILL.md`. Ältere Anleitungen mit anderen Pfaden oder mehreren Skills im selben Repository sind historisch.
3. Impeccable ist im geprüften Skill als **3.0.7** beschrieben. Seine Kontext- und Unterbefehlsregeln müssen vor einer tatsächlichen Anwendung gelesen werden. Ein pauschales „Impeccable an“ ersetzt das nicht.
4. Die geeignete Kombination lautet: Agent-Playbook als Hausregel, Impeccable für UX/UI-Prüfung, Taste für eine begrenzte gestalterische Richtung, Emil für Interaktionsdetails, Superpowers für gezieltes Engineering, ein Browser-QA-Werkzeug. Kein zweiter Orchestrator ist erforderlich.
5. „Amazon Agent Bridge“ konnte anhand des Wortlauts nicht eindeutig einem Repository zugeordnet werden. Die Suchen nach `user:HKGrowthOperator agent bridge` und `"Amazon Agent Bridge"` lieferten keine Treffer. `awesome-claude-code` existiert im HK-Konto, ist aber damit nicht als das gemeinte Projekt bestätigt.

## Verifizierte Auswahl

### Vorrang des bereits vorhandenen Tamil-Systems

Zusätzlich am Commit `181c8337bd47e9ebf284f584501d64e5136d9726` des Branches `claude/radar-multiagent` geprüft: Der Tree enthält **11 Agent-Dateien** und **12 SKILL.md-Dateien** (Impeccable plus 11 Projektskills). Diese zählen Repositorydateien, keine laufenden Agenten oder erkannten Skills in einer Sitzung. Impeccable ist bereits mit Referenzen, Skripten, LICENSE, NOTICE und HERKUNFT.md im Tamil-Repository abgelegt. HERKUNFT.md nennt Version 3.0.7 und Quellstand e587004.

Die neuen Regeln werden deshalb **ergänzt**, nicht als Ersatzarchitektur installiert. Die vorhandenen Rollen `art-director`, `theme-bauer`, `plugin-bauer`, `radar-entwickler`, `cockpit-bauer`, `migrator`, `redakteur`, `referenz-scout`, `design-kritiker`, `code-pruefer`, `qa-pruefer` bleiben Ausgangspunkt. Die zugehörigen Dateien sind im Tree bestätigt; in diesem Teil-Audit wurden nicht alle Rollenbeschreibungen vollständig gelesen.

Inhaltlich gelesen wurden `DESIGN.md`, `.claude/rules/design.md`, `.claude/skills/tamil-marke/SKILL.md`, `.claude/skills/tamil-richtung/SKILL.md` und `.claude/skills/impeccable/HERKUNFT.md`. Daraus folgt:

- `DESIGN.md` beschreibt ausdrücklich die **abgelehnte Runde 2** und darf keine neue Art Direction bestimmen. Maßstab ist `design/brief.md` mit der aktuellen `klar2`-Ergänzung. Keine Creme-/Sand-/Serifen-Richtung wieder aufnehmen.
- Das Ziel ist die vertraute Hierarchie einer großen, ruhigen Nachrichtenmarke. Rot bleibt Akzent, Deutsch bleibt Oberflächensprache. Generische Taste-Aufforderungen zu Eigenwilligkeit oder Impeccable-Brand-Aufforderungen zu Lautstärke werden von den Tamil-Regeln begrenzt.
- Das bestehende Designverfahren bleibt `/design-runde` → G2 → `/design-ausbau` → G3 → `/design-umsetzung`. Ein neuer Prompt erklärt keine Gates eigenmächtig für bestanden. Die aktuelle G2/G3-Freigabe muss der Projektlead im maßgeblichen Status prüfen.
- Mobile Fließschrift mindestens 18 px, Tippflächen mindestens 44 × 44 px, Textkontrast mindestens 4,5:1, kein seitlicher Überlauf bei 390/820/1280 px. Neue Gestaltung gehört nach `design/`; `prototyp/` ist Archiv.
- Für `klar2` gilt die festgelegte Inhaltsfassung, nicht neu erfundener Inhalt. Die bestehende Designregel weist Section 10 des Briefs Vorrang zu, unter anderem bei Bildern und dem begrenzten visuellen Ausbau.

Taste, Emil und Transitions sind ergänzende Kandidaten für eine konkrete Aufgabe. Ihre Existenz als HK-Fork rechtfertigt weder eine Neuinstallation des bereits vendorten Impeccable noch das Überschreiben projektgebundener Skills.

Alle Repositories: `https://github.com/HKGrowthOperator/<Name>`. Die folgende Entscheidung ist eine Empfehlung für Tamil.de, keine Behauptung über bereits installierte Skills.

| Repository | Tatsächlich geprüfte Skill-/Regeldatei | Zweck im Tamil-Produkt | Entscheidung | Grenze |
|---|---|---|---|---|
| HKGrowthOperator-Agent-Playbook | ARBEITSREGELN.md, v1.0.0 | Scope, Branch, Nachweise, Zustände, Übergabe, Parallelität | Verbindlicher Projektstandard | Keine automatische Ausführungsfreigabe aus der Datei ableiten |
| impeccable | .claude/skills/impeccable/SKILL.md, v3.0.7 | Magazin-Lesbarkeit, Navigation, Formulare, Werbebuchung, Cockpit, Accessibility, Fehlerzustände | Primärer UX/UI-Review | Kontextloader, passendes Register und Befehlsreferenz laden; nicht alle Unterbefehle gleichzeitig |
| taste-skill | skills/taste-skill/SKILL.md; name: design-taste-frontend | Eigenständige Editorial-Richtung und gezielter visueller Ausbau; Cockpit mit eigenem App-Screen-Pfad | Art Direction bei einem abgegrenzten Designauftrag | Bestehende Farben/Typografie mit `--keep palette,type` erhalten; keine Vollneugestaltung bei jeder Änderung |
| skill | skills/emil-design-eng/SKILL.md; name: emil-design-eng | Buttons, Popovers, Touch, Motion, wahrgenommene Geschwindigkeit | Ergänzende Design-Engineering-Referenz | Keine eigenständige Produktstrategie; fehlende explizite Repository-Lizenz vor Weiterverteilung klären |
| transitions.dev | skills/transitions-dev/SKILL.md; name: transitions-dev | Ein begründeter Dropdown-, Panel- oder Statusübergang | Optional pro Interaktion | Kein Motion-Framework einführen; Reduced Motion erhalten; keine explizite Lizenzdatei im geprüften Tree |
| superpowers | skills/verification-before-completion/SKILL.md und skills/dispatching-parallel-agents/SKILL.md | Reproduzierbare Aufgaben, unabhängige Teilbereiche, Nachweise vor Abschluss | Gezielt für Engineering | Kein zweiter dauerhafter Koordinator neben dem Projektlead; weitere Unter-Skills vor Verwendung lesen |
| gstack | SKILL.md, name: gstack, Browser-Fokus; README | Browser-QA, responsive Screens, Formulare, Zustände, Console, Code-/Designreview nach gesondertem Lesen | Optional, wenn eingerichtet | Setup und Browserzugriff erst verifizieren; kein automatisches Shipping/Deploy aus einem QA-Auftrag |
| unlazy | SKILL.md; README nennt Source-Ziel 2.1.0, nicht als getaggter Release ausgewiesen | Abnahmeübersicht bei großen mehrteiligen Aufträgen | Optional bei Umfang mit realem Nutzen | Checker führt CHECK-Zeilen als Code aus; keine unbekannten Befehle oder Hooks blind starten |

## Reproduzierbare Stände

Die SHA ist jeweils über `GET /repos/HKGrowthOperator/<repo>/commits/main` ermittelt. Repository-Zustand vom 11.11.2026; eine spätere Installation muss bewusst denselben Commit verwenden oder die Abweichung dokumentieren.

| Repository | Geprüfter Commit | Lizenzbefund |
|---|---|---|
| HKGrowthOperator-Agent-Playbook | 52483b65417ae33282db19c126232744b8f67b24 | Hausinterne Regeln; kein LICENSE-Pfad im geprüften Tree |
| impeccable | e587004ee42883dad40d14cd0f5e1b21ae1933df | Apache 2.0, LICENSE gelesen; NOTICE bei Distribution beachten |
| taste-skill | 12af471f627f866411b4bd785b19646d3672784c | MIT, LICENSE gelesen |
| skill | ecf66bbd1fb33c25332b6b0e454d08049978284c | Kein LICENSE-Pfad im vollständigen geprüften Tree; README verlinkt Emil-Seite |
| superpowers | fe78c2abf375d56d0aa64f892568347de102bc84 | MIT, LICENSE gelesen |
| gstack | a5833c413f98b13f105beac96262e8098b628461 | MIT, LICENSE gelesen |
| unlazy | 16671491f6679ad9378f52604d3bc2415b4120c7 | MIT, LICENSE gelesen |
| transitions.dev | 04825e98af89d2bc72c24d19addf9d9a37ea05fe | Kein LICENSE-/NOTICE-Pfad im vollständigen geprüften Tree |

## Konkretes Routing

### Öffentliche Magazinseiten
Der Designlead beginnt mit dem bestehenden Produkt- und Designkontext und dem realen Seiteninhalt. Impeccable prüft Hierarchie, Rubriken, Lesbarkeit, Inhaltsdichte und mobile Bedienbarkeit. Taste wird nur verwendet, wenn eine eigenständige visuelle Richtung oder größere Überarbeitung beauftragt ist. Redaktioneller Inhalt wird nicht in ein beliebiges Landingpage-Muster mit künstlichen Kennzahlen, Testimonials und Pricing-Karten gepresst.

Die neun vertraglichen Themenbereiche und echte Artikel, Events, Quellen und Werbeflächen bestimmen die Informationsarchitektur. Der Platzbedarf von Anzeigen wird im Layout reserviert. Medien werden mit Herkunft und Nutzungsrecht geführt. Eine bestehende inhaltlich gute Seite wird verbessert, ohne ihren Inhalt für eine zufällig gezogene Komposition zu verbiegen.

### Cockpit und Werbekundenbereich
Hier gilt App-Screen-Logik: Arbeitszustände, Tabellen, Filter, verständliche Formulare, Fehlerursachen und nächste Aktionen haben Vorrang. Taste verlangt für solche Screens `references/app-screens.md` und `inspect.mjs --app`; die Landingpage-Regeln gelten ausdrücklich nicht identisch. Diese Referenz wurde in diesem Audit nicht vollständig angewendet und muss beim realen Designlauf vor Beginn gelesen werden.

Impeccable unterscheidet `brand` und `product`; das interne Arbeits-Cockpit ist `product`. Die öffentliche Startseite wird anhand ihrer tatsächlichen Magazinaufgabe beurteilt, nicht blind als Produktdashboard behandelt. Styles dürfen zusammenpassen, die Bedienlogik muss nicht dieselbe sein.

### Interaktionspolitur
Emil eignet sich nach der funktionalen Umsetzung: klare aktive Buttons, Popover-Ursprung am Auslöser, kurze unterbrechbare Übergänge, keine `transition: all`, Touch-Hover nur auf passenden Geräten und Reduced Motion. Häufige Tastaturaktionen bleiben unmittelbar. Eine UI-Review wird als Tabelle mit Vorher, Nachher und Grund dokumentiert.

Transitions.dev ist eine alternative konkrete Snippet-Quelle. Nie zwei konkurrierende Motion-Systeme für dasselbe Element. Impeccable verbietet dekorativen Bounce, während einzelne Transitions-Snippets Springs verwenden: im Tamil-Projekt bestimmt die dokumentierte Designentscheidung den Effekt, nicht die Summe aller Skillpräferenzen. Bei einem Konflikt lieber einen kleinen, zugänglichen Übergang aus dem gewählten Standard verwenden.

### Engineering und QA
Der Implementierungslead legt klar benannte Akzeptanzkriterien und Dateiverantwortung fest. Superpowers' Verifikation ergänzt das Haus-Playbook. Prüfungen müssen zum Fehler passen, etwa zu doppelten Buchungen, unsicheren Zustandswechseln oder Wiederanläufen, nicht nur zu sichtbaren Erfolgszuständen.

Für Browser-QA reicht **ein** tatsächlich funktionierender Werkzeugpfad: gstack, wenn eingerichtet, sonst der bereits verfügbare Browser/Playwright. Keine gstack-Installation nur für die Behauptung, ein Tool mehr verwendet zu haben. Ein Browser-QA-Bericht nennt URL, Commit-/Buildbezug, Viewports, Abläufe, Belege und offene Blocker.

Unlazy lohnt sich bei einer größeren Umsetzung über mehrere Module. Für ein kleines Formular genügt eine verständliche Abnahmeliste. Wenn der Checker eingesetzt wird, werden geerbte CHECK-Zeilen vor Ausführung gelesen; `--status` ist kein erneuter Testlauf. Ein optionaler Stop-Hook wird nicht still installiert.

## Technische Voraussetzungen und Installationsnachweis

| Werkzeug | Laut geprüfter Quelle nötig | Nachweis vor der tatsächlichen Nutzung |
|---|---|---|
| Taste | Node 22+, Chrome/Edge/Chromium; Netz für Bildsuche | Installationspfad, geladene SKILL.md, gepinnter Commit, erfolgreich laufendes eigenes Script |
| Impeccable | Harness-geeigneter Bundle-/Skillpfad, Kontextloader | Geladener Kontext, verwendeter Unterbefehl und Referenz; keine Readme-only-Nutzungsbehauptung |
| Emil | Markdown-Skill; keine gesonderte Laufzeit im geprüften Skill gefordert | Tatsächlicher Skillpfad und geladene Fassung; Rechte vor Vendoring klären |
| Transitions | Portables CSS, bei einzelnen Effekten kleine JS-Steuerung | Relevante Referenzdatei lesen, bestehende Tokens respektieren, Reduced-Motion-Test |
| gstack | README: Claude Code, Git, Bun 1.0+; weitere Harnesses mit jeweils eigenem Setup | Installierter Host, Setup-Ausgang, Browserstatus, erfolgreicher echter QA-Lauf |
| Unlazy | Node 16+, keine externen Runtime-Pakete laut README | Vertrauenswürdiger Checker, gelesene CHECKs, Ledger-Version und tatsächlich ausgeführte Verifikation |
| Superpowers | Harness-spezifische Installation | Verfügbare Unter-Skills statt pauschaler Repo-Präsenz melden |

Keine dieser Voraussetzungen wurde hier als installiert oder laufzeitgeprüft bestätigt. Geprüft wurden Repositoryquellen. Es wurden keine Installationsskripte, Hooks, Browser-Tunnel, Telemetrie- oder Autoupdate-Konfigurationen ausgeführt.

## Empfohlene feste Regel

Vor einer Aufgabe genau einen führenden Workflow bestimmen. Das Agent-Playbook regelt die Arbeitsweise; der Produktumfang kommt aus dem aktuellen Vertrags- und Produktstand. Ein Designskill gibt Gestaltungshilfe, kein neues Feature und keine Berechtigung. Ein QA-Skill beweist nur die tatsächlich ausgeführten Prüfungen.

Je eingesetztem Skill die aufgabenbezogene Auswahl in diesem Dokument ergänzen (keine zweite konkurrierende Auswahldatei):
- Repository-URL und Commit;
- tatsächlicher SKILL.md-Pfad und benötigte Referenzen;
- Zweck in dieser Aufgabe;
- Status `Quelle geprüft / installiert / geladen / ausgeführt / Ergebnis geprüft`;
- Lizenz und übernommene Dateien;
- abweichende Projektentscheidung mit Grund.

Nicht alle Skills gleichzeitig in jeden Agent-Kontext laden. Für eine PHP-Sicherheitskorrektur ist kein vollständiger Designkatalog erforderlich; für einen typografischen Fix muss kein Multiagent-Orchestrator gestartet werden. Die Dateien werden aufgabenspezifisch geladen.

## Agent-Zusammenarbeit

Gemäß Haus-Playbook standardmäßig höchstens zwei parallele Implementierungsbereiche insgesamt. Ein Koordinator verantwortet Integration. Designer und Backendentwickler können parallel arbeiten, wenn gemeinsame Schnittstellen vorher stehen und kein gemeinsamer Dateischreiber entsteht. Architekturentscheidungen, Datenmigrationen und geteilte Zustandsmaschinen bleiben koordiniert.

Der Benutzer hat in dieser Anfrage Agents ausdrücklich angefordert. Das ist keine allgemeine Dauerfreigabe für spätere externe Veröffentlichungen, Käufe oder Änderungen an anderen Kundenprojekten. Jede Übergabe nennt Ergebnis, Dateibesitz, verwendete Quellen, Prüfumgebung, tatsächlichen Commit und verbleibende Blocker.

## Ungeklärte Quelle „Amazon Agent Bridge“

Bis eine genaue URL oder ein eindeutiger Dateiverweis vorliegt, bleibt der Name als ungeklärte Referenz geführt. Kein AWS-Dienst, AgentCore, AgentBridge oder anderes ähnlich klingendes Projekt wird als Ersatzidentität eingesetzt. `awesome-claude-code` kann als Entdeckungskatalog dienen; jeder daraus ausgewählte Skill braucht wiederum seine eigene Prüfung. Ein Katalog ist kein installierter Laufzeit-Agent.

## Weitere Repository-Kandidaten, nur README-Einordnung

Hier wurde die README zur Zweckerkennung gelesen und der aktuelle Commit festgehalten. Kein vollständiger Code-, Skill-, Lizenz- oder Sicherheitsaudit; keine Installation.

| Repository | Commit | Zweck laut README | Tamil-Entscheidung |
|---|---|---|---|
| promptfoo | a9aacede5c3f84150d999bfbeadbbf39834370ea | CLI/Library für LLM-Evals und Red-Teaming | Sinnvoll für faktische Halluzinationen, Prompt-Injection und Freigaberegeln des Redaktionsagenten; erst konkrete Evals und Anbieter-Datenfluss prüfen |
| crawl4ai | 862f6bccb9c063f49b9d42701baa0eea17a4993f | Web-Crawler/Extraktion zu LLM-tauglichem Markdown | Nur für Quellen, die vorhandene Feed-/Provideradapter nicht zuverlässig abdecken; bestehende Radar-Pipeline zuerst verwenden |
| Agent-Reach | 7a38047acf26a729cbb27851e3cb81639da86b29 | Plattformübergreifender Internet-/Contentzugriff für Agents | Recherche-Kandidat bei konkreter Lücke; keine Umgehung notwendiger Kontozugriffe oder Veröffentlichungsfreigaben daraus ableiten |
| ruflo | 16a55f7a537c4a405e448e59859866eebbdd45a0 | Multiagent-Harness für Claude Code/Codex, Koordination und Memory | Vorerst nur Referenz; vorhandene Tamil-Agents und das Haus-Playbook ausreichen lassen, keinen zweiten Steuerungsapparat einführen |
| claude-code-best-practice | eab161ca5284aa0c88aa44ec4f371e73a356acef | Konzepte/Implementierungsbeispiele zu Agents, Commands, Skills, Hooks, MCP und Plugins | Einzelne Konfigurationsmuster referenzieren; kein pauschaler Import von Hooks oder Settings |
| awesome-claude-code | 614f102accbcd48206d63a21df64adc984026b40 | Sammlung von Claude-Code-Ressourcen | Entdeckungskatalog; aktuelle README kündigt Neuordnung an und enthält eine TODO-Inhaltsübersicht. Nicht als fertigen Agent oder als identifizierte „Amazon Agent Bridge“ behandeln |

README-Werbeaussagen und Skalierungsversprechen wurden nicht als eigene Leistungsnachweise übernommen. Für jeden produktiven Einsatz bleiben Anbieterzugang, Datenverarbeitung, API-Regeln, Versions-/Lizenzprüfung und reale Integration separat zu verifizieren.


## Quellen

Die Inhaltsprüfung erfolgte über GitHub: vollständige Repositorytrees, die oben genannten SKILL.md-Dateien, READMEs sowie vorhandene LICENSE-Dateien. Exakte Commit- und Pfadzuordnung steht zusätzlich in `quellen/skills_evidence.json` und `quellen/skills_evidence_additional.json`. Es wurden keine fremden Skilldateien kopiert oder verändert. Quellen können über die folgenden Muster reproduzierbar geöffnet werden:

- `https://github.com/HKGrowthOperator/<repo>/blob/<commit>/<path>`
- `https://api.github.com/repos/HKGrowthOperator/<repo>/commits/main`

Die inhaltliche Empfehlung ist eine projektspezifische Ableitung aus diesen Quellen. Sie ist keine vollständige Sicherheitsprüfung aller Repositorydateien und kein rechtliches Lizenzgutachten.

