# Tamil.de – Agenten, Repositories und Umsetzung

Stand 11.11.2026. Ergänzung der bestehenden Projektstruktur, kein Ersatz für `CLAUDE.md`,
`docs/ablaeufe.md`, die Bereichsregeln oder das Vertragsregister.

## Dokumente

| Datei | Verbindlicher Zweck |
|---|---|
| [01-PRODUKT-UND-SCOPE.md](01-PRODUKT-UND-SCOPE.md) | Produktgrenzen, Nutzerwege und Abnahmekriterien |
| [02-AGENT-ROUTING.md](02-AGENT-ROUTING.md) | Vorhandene Agents, Aufgabenbesitz und Übergabe |
| [03-REPO-SKILL-SELECTION.md](03-REPO-SKILL-SELECTION.md) | Geprüfte Skillquellen, Versionsstände, Auswahl |
| [04-UI-UX-DESIGN.md](04-UI-UX-DESIGN.md) | Aktuelle Designautorität und konkrete Prüfroutine |
| [05-SCHNITTSTELLEN-UND-ZUSTAENDE.md](05-SCHNITTSTELLEN-UND-ZUSTAENDE.md) | Empfohlene technische Verträge für offene Module |
| [06-QA-UND-RELEASE.md](06-QA-UND-RELEASE.md) | Prüfungen, Provider-Nachweise und Release |
| [07-MASTER-PROMPT.md](07-MASTER-PROMPT.md) | Kopierbarer Auftrag für die nächste Coding-Sitzung |
| [08-REPOSITORY-INVENTAR.md](08-REPOSITORY-INVENTAR.md) | Alle 74 sichtbaren Repositories, Rolle und Prüftiefe |
| [09-IST-STAND-AUDIT.md](09-IST-STAND-AUDIT.md) | Stichtagsbefund zum bestehenden Code |
| [10-ENTSCHEIDUNGEN-UND-TECHNIKTEAM.md](10-ENTSCHEIDUNGEN-UND-TECHNIKTEAM.md) | Prioritäten, noch nötige Entscheidungen, Verantwortliche |

## Ein maßgeblicher Ort je Aussage

- Umfang und Fortschritt: `docs/vertrag/leistungen.md`.
- Geschäftsregeln: bestätigte `docs/vertrag/festlegung-*.md` plus `docs/abnahme/`.
- Produktentscheidungen: `docs/entscheidungen.md`.
- Gestaltung: `design/brief.md` plus aktuelle G2/G3-Protokolle; `DESIGN.md` erst nach G3 aktualisieren.
- Betrieb/Umgebungen: `docs/betrieb.md`.
- Agentabläufe: bestehende `docs/ablaeufe.md` und `.claude/`; dieser Ordner ergänzt die Modell- und Runner-übergreifende Übergabe.

Bei Widerspruch aktuelle ausdrückliche Nutzerentscheidung und aktuelle bestätigte Projektentscheidung anwenden.
Historische Angaben als historisch kennzeichnen. Diese Ergänzung bestätigt weder offene Tore noch eine
Provideranbindung. Keine zweite Fortschrittsliste dauerhaft parallel führen.

## Zwei verschiedene Arten von Agents

**Entwicklungs-Agents** lesen und ändern Code in begrenzten Aufträgen. Die elf vorhandenen
`.claude/agents/` sind dafür Rollenbeschreibungen. Sie sind nicht automatisch elf laufende Prozesse.

**Produkt-Agents** laufen im Radar und bearbeiten Recherche, Storys, Claims, Entwürfe und Freigaben.
Sie nutzen Scheduler, Jobzustände, Budgets und die vorhandene Agent-API. Code-Agents erhalten dadurch
keinen pauschalen Produktionszugang. Externe Runner wie Hermes oder Grok brauchen einen belegten
Adapter und eigene eng begrenzte Identität; diese Dokumente richten solche Zugänge nicht ein.

## Auditgrenze

74 Repositories wurden im erreichbaren GitHub-Zugang inventarisiert; Detailprüfung konzentriert auf Tamil,
Agent-Playbook und ausgewählte Skillquellen. Keine Vollprüfung aller Dateien aller Kundenrepos.
Geprüft: Repositoryquellen, aktuelle Dokumente, öffentliches tamil.de und WordPress-Vorschau.
Nicht nachgewiesen: aktueller Produktions-Commit, private Coolify-Konfiguration, vollständige Testsuite in dieser
Analysesitzung, echte Stripe-/Meta-Anbieterabnahme oder fachliche KBS-Endabnahme.
