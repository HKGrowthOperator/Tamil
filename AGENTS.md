# Tamil.de – gemeinsamer Einstieg für Coding-Agenten

Stand 11.11.2026. Dieser Einstieg ergänzt `CLAUDE.md`; er installiert keine Werkzeuge und startet keine Agents.
Er gilt für Codex, Claude Code und andere Runner, soweit diese die Datei tatsächlich laden.

## Zuerst lesen

1. `CLAUDE.md`: Systemgrenzen, Branch, Commands, bestehende Agents und Freigaben.
2. `docs/vertrag/leistungen.md` und die betroffene `festlegung-*.md`: einziger Fortschritts- und Scope-Maßstab.
3. `docs/entscheidungen.md` und relevante `docs/abnahme/`: bestätigte Entscheidungen erhalten.
4. `docs/agent-playbook/README.md`: Routing, Schnittstellen, Skill-Auswahl, QA und ausführbarer Arbeitsauftrag.
5. Die auf den betroffenen Pfad anwendbaren `.claude/rules/*.md` explizit lesen, wenn der Runner sie nicht automatisch lädt.

Hausstandard: HKGrowthOperator/HKGrowthOperator-Agent-Playbook, Version 1.0.0,
Commit `52483b65417ae33282db19c126232744b8f67b24`, `ARBEITSREGELN.md`.
Vor Anwendung den Text tatsächlich lesen; die Regeln sind kein Ersatz für Produktcode oder Berechtigungen.

## Arbeitsweise

- Hauptprodukt ist `HKGrowthOperator/Tamil`. Integrationsbranch ist laut bestehendem Projektstand
  `claude/radar-multiagent`, PR #2 gegen `main`. Zum Start Remote-SHA und laufende Arbeit prüfen.
  Aufgabenbranches davon ableiten und per PR zurückführen; nie direkt auf `main`, nie Force-Push.
- Bereits vorhandene elf Agents und zwölf Skills weiterverwenden. Ein Koordinator, standardmäßig höchstens
  zwei parallele Implementierungsbereiche, disjunkte Schreibpfade, gemeinsame Schnittstelle vor dem Start.
  Agents starten keine weiteren Agents. Prüfung nach Integration aus frischem Kontext.
- Claude verwendet die vorhandenen Commands. Andere Runner übernehmen dieselben Rollen als klar begrenzte
  Aufträge; keine Claude-Tools, Slash-Commands oder Zugänge als vorhanden behaupten.
- Fortschritt nur im Leistungsverzeichnis pflegen; diese Dokumente sind Regeln und Audit-Snapshots.
  `implementiert`, `lokal geprüft`, `Anbieter geprüft`, `abgenommen` unterscheiden.
- Normale bereits autorisierte Arbeit fortsetzen. Nur tatsächlich fehlende Entscheidungen am betroffenen Schritt
  beachten. Ein neues Regelpapier ist kein Anlass für zusätzliche pauschale Freigabeschleifen.

## Unverhandelbare Produktgrenzen

- WordPress: öffentliche Inhalte, Einreichungen, Verzeichnis, Kunden, Werbung und Zahlung.
  Python-Radar: Recherche, Agenten, Vorschläge, Prüfung, Aufgaben, Stopp, Protokoll und Social-Adapter.
  Radar fragt WordPress ab; kein öffentliches Agenten-Cockpit.
- Kein automatischer E-Mail-Versand im Tamil-Produkt, auch keine automatischen Bestätigungen oder Follow-ups.
  Rückmeldungen und Status auf der Website. Provider-Einstellungen und WordPress-Kern separat prüfen.
- Instagram plus Facebook automatisch innerhalb einmalig genehmigter Regeln; Ausnahmefälle zur manuellen Prüfung.
  WhatsApp-Channel: Entwurf, solange keine offiziell zulässige, für KBS verfügbare Publishing-Schnittstelle belegt ist.
- Keine erfundenen Fakten, Kontakte, Bildrechte, Preise, Freigaben oder Fertigmeldungen.
  Altbestand erhalten, Daten nicht künstlich aktualisieren, keine Agenturfotos ohne passende Rechte.
- Neue Integrationen zunächst Test-/Trockenmodus. Kostenpflichtige Dienste und produktive Aktionen nur im
  vorhandenen Auftrag und mit den erforderlichen dokumentierten Geschäftsregeln.
- Sicherheitsprüfungen am wirksamen Zustandsübergang: Rolle, Version, Claim/Lease, Budget, Stopp,
  Zahlungsstatus, Zeitfenster und Idempotenz; keine Sicherheit durch bloß versteckte Buttons.

## Gestaltung

`DESIGN.md` beschreibt ausdrücklich einen abgelehnten Bestand. Für neue Gestaltung:
`design/brief.md`, insbesondere Abschnitt 10 für `klar2`, `PRODUCT.md`, `tamil-marke`
und die dokumentierten G2-/G3-Entscheidungen. Nicht ungefragt neu gestalten und keine Kundenlayouts kopieren.
Designskills helfen bei der Umsetzung; ihre generischen Vorlieben überschreiben den aktuellen Brief nicht.

## Abschluss

Prüfungen nach `CLAUDE.md` und `docs/agent-playbook/06-QA-UND-RELEASE.md` auswählen.
Keine Laufzeittests nur wegen einer Textänderung; für Produktänderungen die relevanten Fehler- und Wiederanlauffälle.
Übergabe mit Commit, Branch, Umgebung, Ergebnis, Nachweisgrenzen und nächstem konkreten Schritt.
