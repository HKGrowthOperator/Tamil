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
| `code-pruefer` | opus | Diff vor jedem Push prüfen: Sicherheit, Fehlerpfade, Tests | Befunde mit Datei:Zeile |
| `redakteur` | opus | wartende Storys im Agent-Modus schreiben oder begründet verwerfen | Import in den Live-Radar |
| `migrator` | sonnet | Altbestand von tamil.de in die neue Website, mit Prüfliste | Bericht + Prüfliste |

## Abläufe

### `/status` (nur lesen)
Gesundheit Radar und Website, Warteschlange, Budget, Entwürfe (`radar-auswertung`), PR-Stand, offene Tore.

### `/design-runde` → Tor G2
1. Tor G1 prüfen: Gibt es `design/brief.md` mit Bestätigung in `docs/abnahme/`? Sonst Brief mit `impeccable shape`
   (Fragen an Luis) und stoppen.
2. `referenz-scout`, falls `design/referenzen/` fehlt oder veraltet ist.
3. **4× `art-director` parallel**, je eine Richtung: Kollywood-Plakatwand, Diaspora-Zine, Raster + Tamil-Schrift,
   Vertikaler Feed (G1 kann streichen). Umfang: Startseite (erster Bildschirm plus ein Abschnitt) und Artikelkopf,
   Handy und Desktop, echte Inhalte.
4. **4× `design-kritiker`**, jeder frisch. Schwelle: mindestens 28/40 und KI-Slop-Test bestanden.
5. P0/P1 → derselbe `art-director` überarbeitet einmal → neue Kritik.
6. Unter der Schwelle: verworfen, nicht gezeigt (Luis bekommt die Liste mit Begründung).
7. Vergleichsseite als Artifact: bestandene Richtungen nebeneinander, je Vorbild und drei Sätze. Luis zeigt sie dem
   Auftraggeber.

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
| B3 | Domain tamil.de umschalten (Luis mit Auftraggeber) | Livegang |
