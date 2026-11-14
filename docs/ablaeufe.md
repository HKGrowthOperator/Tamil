# Abläufe, Rollen und Tore

Wer was macht. Die Hauptsitzung steuert über Commands (`.claude/commands/`), die Arbeit machen Agents
(`.claude/agents/`) mit vorgeladenen Skills (`.claude/skills/`). Agents starten keine Agents.

## Rollen

| Agent | Modell | Aufgabe | Ergebnis |
|---|---|---|---|
| `referenz-scout` | sonnet | echte Vorbilder je Gestaltungsrichtung sammeln, mit Screenshot | `design/referenzen/README.md` |
| `art-director` | opus | genau eine Richtung gestalten (Skizze oder Probeseite), eine Überarbeitung nach Kritik | `design/richtungen/<slug>/` |
| `design-kritiker` | opus | unabhängig bewerten (nur Ergebnis + Brief, nie die Begründung) | `design/kritik/<slug>-r<n>.md` |
| `qa-pruefer` | sonnet | Technik: Überlauf, Kontrast, Tippflächen, Fokus, Konsole, Bildgrößen | Bericht |
| `theme-bauer` | opus | abgenommenes Design ins WordPress-Theme (eigener Worktree) | Commits in `wordpress/themes/tamil` |
| `cockpit-bauer` | opus | gleiches Design im Cockpit, Produkt-Register (eigener Worktree) | Commits in `news_radar/web` |
| `radar-entwickler` | opus | Python-Änderungen am Radar, Test zuerst (eigener Worktree) | Commits in `news_radar/` |
| `plugin-bauer` | opus | Funktionen in den WordPress-Plugins nach bestätigter Festlegung, Test zuerst (eigener Worktree); fasst das Aussehen nicht an | Commits in `wordpress/plugins/` |
| `code-pruefer` | opus | Diff vor jedem Push prüfen: Sicherheit, Fehlerpfade, Tests | Befunde mit Datei:Zeile |
| `redakteur` | opus | wartende Storys im Agent-Modus schreiben oder begründet verwerfen | Import in den Live-Radar |
| `migrator` | sonnet | Altbestand von tamil.de in die neue Website, mit Prüfliste | Bericht + Prüfliste |

## Abläufe

### `/status` (nur lesen)
Gesundheit Radar und Website, Warteschlange, Budget, Entwürfe (`radar-auswertung`), PR-Stand, offene Tore.

### `/design-runde` → Tor G2
1. Brief prüfen (`design/brief.md`; bestätigt mit `docs/abnahme/*-G1-runde<n>.md`), Vorbilder
   (`design/referenzen/news-marken.md`, vermessene Nachrichtenmarken) und Material (`design/inhalte/`).
2. **3× `art-director` parallel**, je eine Schnellprobe: `klar`, `blatt`, `bild`. Umfang: nur die Startseite, Handy
   und Desktop, feste echte Inhalte.
3. Die Hauptsitzung misst jede Probe gegen die harten Kriterien des Briefs (`design/vergleich/aufnahmen.mjs`).
4. **Vorschau für Luis**, intern und ungefiltert: je Probe zwei Handy-Bildschirme, Desktop, Kennzahlen, daneben ein
   Vorbild und Runde 2. Luis wählt eine Probe oder eine Mischung; damit ist der Brief bestätigt.
5. Derselbe `art-director` arbeitet die gewählte Probe aus (Artikelkopf, Anmerkungen von Luis).
6. **`design-kritiker`**, frisch: Messwerte und Befunde, kein Urteil. Bei P0/P1 eine Überarbeitung, dann eine zweite
   frische Prüfung.
7. Durchgelassen wird, was alle harten Kriterien erfüllt und kein offenes P0 oder P1 hat. Eine Punktsumme ist kein
   Tor. Was nicht besteht, geht mit Grund nur an Luis.
8. Vorlage für den Auftraggeber als Artifact. Luis zeigt sie; Urteil nach `docs/abnahme/<datum>-G2-runde<n>.md`.

### `/design-ausbau <slug>` → Tor G3
`art-director` baut Start, Artikel, Rubrik, Events, Kinoliste, Kontakt; danach `design-kritiker` und `qa-pruefer`,
höchstens zwei Runden; Artifact.

### `/design-umsetzung`
`impeccable document` → neue `DESIGN.md` und `design/tokens.css`; `theme-bauer` und `cockpit-bauer` parallel in
Worktrees; `qa-pruefer` und `design-kritiker` vergleichen mit der Probeseite (Abweichung = P1); Merge; `/release`.

### `/research`
`redakteur` gegen den Live-Radar (`radar-research`), danach `radar-auswertung` → Tabelle an Luis.

### `/website-live` → Tor G4
`coolify-betrieb`: App „tamil-web“ anlegen oder aktualisieren → `migrator`: Altbestand mit Originaldatum, Slug, Bildern,
Seiten und 301-Weiterleitungen → Radar-Variablen `WP_URL`, `WP_USER=ki-agent`, `WP_APP_PASSWORD`,
`WP_POST_STATUS=publish` → Redeploy → Probe: Freigabe im Cockpit erzeugt einen Beitrag → Screenshots gegen die
Live-Adresse.

### `/release`
`pruefen` → `code-pruefer` → Befunde beheben → Commits je Bereich → Push → PR #2 aktualisieren → Coolify-Deploy mit
Warten → `/gesund` und Logs → Bericht.

### `/vertrag-bau <baustein>` → Tore F0 bis F4
Maßstab ist der Vertrag (`docs/vertrag/leistungen.md`). Je Baustein (`grundlage`, `einreichungen`, `verzeichnis`,
`werbung`, `social`): Festlegung schreiben (`docs/vertrag/festlegung-<baustein>.md`, für Luis als Reiter im
Projekt-Dokument) → Luis sagt Ja oder ändert (`docs/abnahme/<datum>-F<n>-<baustein>.md`) → `plugin-bauer` (Website)
und `radar-entwickler` (Radar, Cockpit) bauen parallel in Worktrees → `pruefen`, bei Oberflächen `qa-pruefer` →
`code-pruefer` → zusammenführen → `/release` → auf dem Testsystem zeigen. Regeln: `.claude/rules/vertrag.md`.

### `/abnahme-vertrag` → Abnahme durch KBS
Die sieben Tests aus B5 automatisch ausführen, Protokoll `docs/abnahme/<datum>-B5.md` mit den Handtests für das
Testsystem schreiben. Danach Übergabe nach §4 (Kernabläufe, Zugänge, Protokoll) und Livegang (Tor B3).

## Tore

Abnahmen laufen immer über Luis: Er zeigt dem Auftraggeber den Link und bringt das Urteil zurück. Jede Abnahme wird in
`docs/abnahme/<JJJJ-MM-TT>-<tor>.md` festgehalten (gezeigt, Link, Urteil wörtlich, Änderungswünsche).

| Tor | Was | Danach erlaubt |
|---|---|---|
| G1 | Brief und Referenzen (3–5 „mögen wir“, 2 „mögen wir nicht“ vom Auftraggeber, dazu die Auswahl aus dem Scout) | Richtungsskizzen |
| G2 | eine Richtung aus der Vergleichsseite | Probeseite |
| G3 | Probeseite mit allen Seitentypen | Theme und Cockpit umbauen |
| G4 | Live-Website mit echten Inhalten | Go-live-Vorbereitung, Merge von PR #2 |
| B1 | Anthropic-Schlüssel in Coolify (Luis) | Pilot mit Modellen, Kostenmessung |
| B2 | Coolify-Root-Token widerrufen (Luis) | eigenes, eng gefasstes Token |
| B3 | Domain tamil.de umschalten (Luis mit Auftraggeber) | Livegang; danach beginnen Feinjustierung und Betreuung (Vertrag B4) |
| F0 | Festlegung Grundlage (Rollen, Stopp-Schalter, Cookie-Zustimmung, Fristen) | Rollen und Texte gelten; die Technik beginnt schon vorher |
| F1 | Festlegung Einreichungen | Formulare und Eingang bauen |
| F2 | Festlegung Verzeichnis | Verzeichnis und Verzeichnis-Agent bauen |
| F3 | Festlegung Werbung (Plätze, Preise, Laufzeiten, Ablauf, Erstattung) | Werbebuchung bauen |
| F4 | Festlegung Social und Regelwerk `docs/regeln-social.md` (zusätzlich einmalig durch KBS, §8 Abs. 1) | Instagram, Facebook, WhatsApp-Entwurf bauen und automatisch veröffentlichen |
