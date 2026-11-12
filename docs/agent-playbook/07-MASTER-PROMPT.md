# Master-Prompt: Tamil.de vollständig aus dem Bestand umsetzen

Den folgenden Auftrag in die Coding-Sitzung geben. Der Runner muss vorhandene Fähigkeiten tatsächlich
prüfen; Namen von Tools oder Repositories allein stellen sie nicht bereit.

---

Du koordinierst als verantwortlicher Tech Lead die Fertigstellung von Tamil.de für HK Growth und KBS.
Arbeite auf dem vorhandenen Produkt, innerhalb des aktuellen Vertragsumfangs, bis der beauftragte
Baustein als vollständiger Nutzerablauf integriert und nachvollziehbar geprüft ist.

**Start und Quellen**
1. Prüfe HKGrowthOperator/Tamil, Remote-Branches, aktuellen SHA, Arbeitsbaum, Worktrees und aktive Schreiber.
   Der zuletzt geprüfte Ausbau-Branch ist claude/radar-multiagent mit PR #2 nach main. Hole den aktuellen
   Stand; ein alter Audit-SHA ist kein Befehl zum Zurücksetzen.
2. Lies AGENTS.md, CLAUDE.md, docs/agent-playbook/README.md, docs/vertrag/leistungen.md,
   die relevante Festlegung, docs/entscheidungen.md und die passenden Abnahmeprotokolle/Bereichsregeln.
   Haus-Playbook ARBEITSREGELN.md Version 1.0.0, Commit
   52483b65417ae33282db19c126232744b8f67b24 tatsächlich lesen und den verwendeten Stand nennen.
3. Unterscheide Codebestand, lokalen Test, echte Anbieterprüfung und fachliche Abnahme.
   Prüfe nur Änderungen seit der letzten belastbaren Übergabe; keine wiederholte Gesamtinventur.

**Produkt**
WordPress hält Website, Einreichungen, Verzeichnis, Werbekunden, Belegung und Zahlung.
Python-Radar hält Recherche, Jobs, Belege, Agenten, Cockpit, Regeln, Stopp, Historie und Social-Adapter.
Erhalte CMS, Migration, Quellen-/Bildnachweise, Agent-API, Job-/Budgetschutz und freigegebene Inhalte.
prototyp/ ist Archiv. Live tamil.de bleibt lesend, solange der aktuelle Auftrag keine Umschaltung autorisiert.

**Nächster Baustein**
Prüfe F0–F4 gegen die tatsächlichen Protokolle. Wähle den nächsten bereits genehmigten offenen Baustein:
Grundlage → Einreichungen → Verzeichnis → Werbung/Stripe → Social → Abnahme.
Erfinde kein Ja. Bereits autorisierte technische Arbeit fortführen und nur den konkret fehlenden
Entscheidungsschritt benennen. Sind Fachregeln noch offen, bereite konkrete Änderungen an der vorhandenen
Festlegung vor und erledige unabhängige erlaubte Arbeit.

**Agenten**
Nutze die vorhandenen elf Rollen. Ein Koordinator, maximal zwei unabhängige Implementierungsbereiche,
eigene Worktrees bei parallelem Schreiben, kein weiterer Agentstart durch Subagents.
Vor dem Start Pfadbesitz und Schnittstellen mit Feldern, Status, Rechten, Revision und Idempotenz festlegen.
Für WP/Radar: plugin-bauer und radar-entwickler; für bestätigtes Design: theme-bauer und cockpit-bauer.
Danach frischer code-pruefer und passende qa-pruefer-Aufgabe. Liefere ein integriertes Ergebnis.
Wenn der Runner diese Agents nicht direkt unterstützt, verwende dieselben Rollen als explizite Teilaufträge
oder arbeite seriell; behaupte keine installierten Werkzeuge.

**Skills**
Nutze projektbezogene tamil-* Skills und das vorhandene Impeccable-Bundle zuerst.
Prüfe docs/agent-playbook/03-REPO-SKILL-SELECTION.md: tatsächliche SKILL.md, Herkunft, Commit,
benötigte Referenzen, Rechte und Tool-Verfügbarkeit.
Taste nur für beauftragte Art Direction, Emil Kowalski für gezielte Interaktionsqualität,
Superpowers für den passenden Engineering-Schritt, ein verfügbarer Browserweg für QA.
Nicht alle Repos klonen oder alle Skills in jeden Kontext laden. Amazon Agent Bridge ist ungeklärt;
keine erfundene Installation und kein automatisch gleichgesetzter AWS-Dienst.

**Design**
Aktuelles DESIGN.md ist als abgelehnt markiert. Maßstab ist design/brief.md Abschnitt 10 für klar2
mit dokumentierten Ausnahmen und G2/G3. Keine neue Palette, keine neue Runde und keine Theme-Migration
nebenbei. Bestehende /design-*-Commands nutzen. Inhaltsdichte, Leserführung, Anzeigen, Formulare und
Fehlerzustände gemeinsam gestalten. Eigenständige Nachrichtenmarke; keine Kundenlayouts kopieren.

**Geschäftsregeln**
Keine automatischen E-Mails, auch keine Bestätigungen. Webstatus statt Mail.
Instagram und Facebook nach einmalig genehmigter versionierter Regel automatisch; Ausnahmen manuell.
WhatsApp-Channel nur vorbereiten, solange offizielle Publishing-Fähigkeit für KBS nicht belegt ist.
Keine erfundenen Fakten, Bilderrechte, Preise, Daten oder Freigaben; keine KI-Bilder gemäß jüngerer Entscheidung.
Zahlung nur serverseitig bestätigt, Werbemittel freigegeben und Zeitraum gültig → Kampagne aktiv.
Stopp, Rollen, Revision, Budget und Jobbesitz unmittelbar vor der wirksamen Aktion prüfen.
Bei unklarem externem Ausgang abgleichen statt blind wiederholen. Keine Secrets in Chat, Repo oder Logs.

**Prüfung und Übergabe**
Gezielte Regressionen und passende Projektchecks ausführen; WP-Tests nicht still überspringen.
Für Oberflächen echte Browserprüfung bei 390/820/1280, inklusive Fehlerzuständen, Tastatur und Reduced Motion.
Belegungskonkurrenz, doppelte/ungeordnete Webhooks, Lease-Verlust und teilweise fehlgeschlagene Social-Kanäle
testen. Echte Meta-/Stripe-Grenze getrennt von Simulationen dokumentieren.
Aktualisiere das bestehende Leistungsverzeichnis und den Entscheidungslog.
Abgabe: Ergebnis je Nutzerablauf, Repo/Branch/SHA, integrierte Änderungen, tatsächliche Testbefunde,
Anbietergrenze, offene Entscheidungen und nächste konkrete Tätigkeit. Keine Fertigmeldung allein aus Testzahlen.

Beginne jetzt mit dem aktuellen Stand und dem nächsten erlaubten Baustein. Beende den Auftrag nicht nach
einem Plan, wenn Umsetzung bereits autorisiert ist.

---
