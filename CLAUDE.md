# CLAUDE.md – Tamil.de

Relaunch von tamil.de (deutschsprachiges Magazin der tamilischen Diaspora in DE/AT/CH) plus News-Radar mit
Agenten-Redaktion. Auftraggeber über Luis (HK Growth Operator). Sprache in Code-Kommentaren, Oberflächen und Doku:
Deutsch. **Maßstab für „fertig“ ist der Vertrag (Anlage 1):** `docs/vertrag/leistungen.md`.

## Systeme

| System | Code | Läuft auf | Adresse |
|---|---|---|---|
| Website (WordPress: Theme `tamil`, Plugins `tamil-site`, `tamil-radar`) | `wordpress/` | Coolify-App „tamil-web“ | tamil-web.167.233.76.202.sslip.io (vorerst) |
| News-Radar (Scan, Storys, Redaktion v2 mit Belegen, Budget) | `news_radar/`, `sources.toml` | Coolify-App „tamil.de“ | tamil.hk-growthoperator.de |
| Redaktions-Cockpit (Freigabe → WordPress) | `news_radar/web/` | im Radar-Container | dieselbe |
| Design (Marke, Brief, Referenzen, Richtungen) | `design/`, `PRODUCT.md`, `DESIGN.md` | Artifacts für Abnahmen | – |
| Betrieb | `Dockerfile`, `wordpress/Dockerfile`, `wordpress/docker/`, `tools/`, `deploy/` (systemd, nur Alternative) | Coolify v4 | siehe `docs/betrieb.md` |

Datenfluss: Quellen → Scan → Story + Jobs → Agenten (oder Agent-Modus `/api/agent/*`) → Entwurf mit Claims/Belegen →
Freigabe im Cockpit → `publisher.py` → Plugin `tamil-radar` (REST) → Beitrag auf der Website.

## Wo was liegt

- `docs/` – `architektur.md`, `betrieb.md` (Apps, Variablennamen, Volumes, Deploy), `ablaeufe.md` (Abläufe und Tore),
  `entscheidungen.md` (Entscheidungslog), `abnahme/` (jede Abnahme des Auftraggebers), `vertrag/`
  (Leistungsverzeichnis, Festlegung je Baustein, Zuarbeit von KBS).
- `design/` – `brief.md`, `referenzen/`, `richtungen/<slug>/`, `kritik/`, später `tokens.css`.
- `prototyp/` – **Archiv.** Nur `prototyp/content/*.json` ist noch Datenquelle (Importer, Tests). Nichts Neues hier bauen.
- `tools/` – `export_site.py` (alte tamil.de nur lesen), `shots.mjs` (Screenshots + Prüfung), `coolify.py` (Deploy).
- `tests/` – pytest; `tests/wp/` braucht ein lokales WordPress (`wordpress/dev/`), sonst übersprungen.
- `.claude/` – `rules/` (Bereichsregeln), `skills/`, `agents/`, `commands/` (siehe unten).

## Befehle

```bash
pip install -r requirements.txt
python -m pytest -q                         # alle Tests (FakeClaude, kein Netz)
python -m news_radar abnahme                # alle Szenarien müssen bestehen
python -m news_radar web                    # Cockpit lokal auf :8787
bash wordpress/dev/setup.sh && bash wordpress/dev/serve.sh &   # lokales WordPress (SQLite) auf :8085
bash wordpress/dev/lint.sh                  # PHP-Lint, theme.json, PHPCS/WPCS
node tools/shots.mjs <url|datei> --out <ordner>   # 390/820/1280, seitliches Scrollen, Konsole, Schrift
python tools/coolify.py status              # Stand beider Apps (Token aus $COOLIFY_TOKEN)
```

## Regeln (immer)

- **Git:** Arbeit auf `claude/radar-multiagent`, PR #2 gegen `main`. Gemergt wird nur per PR und nach dem
  jeweiligen Tor. Nie direkt auf `main`, nie force, nie `--no-verify`.
- **Commits:** `type(scope): Nachricht`, eine Sache je Commit. Abschluss mit den Zeilen `Co-Authored-By` und
  `Claude-Session` aus der Sitzung. Keine Modellnamen in Commits oder PR-Texten.
- **Geheimnisse:** nur in Coolify-Variablen oder in einer lokalen `.env` (nie eingecheckt). Nie im Chat, nie in
  Ausgaben, nie in Docs; in Docs stehen nur Variablen*namen*. Die Vertrags-IBAN wird nie veröffentlicht.
- **Inhalte:** Die echte tamil.de wird nur gelesen, nie beschrieben. Keine erfundenen Fakten, Kontakte oder
  Bildnachweise. Platzhalter kennzeichnen (Telefon, E-Mail und WhatsApp-Nummer in `prototyp/content/site.json` sind
  Beispielwerte).
- **Vertrag:** Erst festlegen, dann bauen (`docs/vertrag/festlegung-<baustein>.md`, Ja von Luis in `docs/abnahme/`).
  Kein Mailversand. Automatisch läuft nur, was in einer freigegebenen Regel steht; jede automatische Ausführung prüft
  den Stopp-Schalter und schreibt Protokoll. Neue Funktionen bleiben im Echtbetrieb aus, bis Auftragsverarbeitung und
  Rechtstexte vorliegen. Einzelheiten: `.claude/rules/vertrag.md`.
- **Fertig heißt:** pytest grün · `abnahme` alle Szenarien · bei Theme/Plugin zusätzlich `lint.sh` · bei Oberflächen zusätzlich
  `tools/shots.mjs` bei 390/820/1280 ohne seitliches Scrollen und ohne Konsolenfehler. Skill `pruefen` macht das je
  Bereich.
- **Design:** Kein Umbau von Theme oder Cockpit ohne Tor G3. Gestaltet wird über `/design-runde`, `/design-ausbau`,
  `/design-umsetzung`, nie nebenbei. Verbotsliste: `.claude/skills/tamil-marke/references/abgelehnt.md`.
- **Orchestrierung:** Die Hauptsitzung steuert über die Commands und gestaltet oder baut Großes nicht selbst. Agents
  starten keine Agents. Kritik kommt immer aus einem frischen Kontext, der die Begründung des Gestalters nicht kennt.

## Abläufe (Commands)

| Command | Wofür |
|---|---|
| `/status` | Stand von Radar, Website, Budget, PR und offenen Toren (nur lesen) |
| `/design-runde` | Referenzen → vier Richtungen parallel → unabhängige Kritik → Vergleichsseite (Tor G2) |
| `/design-ausbau <slug>` | gewählte Richtung als Probeseite mit allen Seitentypen (Tor G3) |
| `/design-umsetzung` | DESIGN.md + Tokens, Theme und Cockpit parallel umbauen, QA, Release |
| `/research` | wartende Storys im Agent-Modus gegen den Live-Radar schreiben, dann auswerten |
| `/website-live` | WordPress in Coolify einrichten, echte Inhalte migrieren, Radar verbinden (Tor G4) |
| `/release` | prüfen → Code-Review → Commits → Push → PR → Deploy → Gesundheit |
| `/vertrag-bau <baustein>` | einen Baustein aus dem Vertrag nach bestätigter Festlegung bauen, prüfen, zusammenführen |
| `/abnahme-vertrag` | die sieben Abnahmetests aus dem Vertrag (B5) ausführen, Protokoll schreiben |

Tore beim Auftraggeber (immer über Luis, festgehalten in `docs/abnahme/`): **G1** Brief und Referenzen · **G2**
Richtung · **G3** Probeseite · **G4** Live-Website. Betriebstore bei Luis: **B1** Anthropic-Schlüssel in Coolify ·
**B2** Root-Token widerrufen · **B3** Domain tamil.de umschalten. Festlegungen bei Luis: **F0** Grundlage · **F1**
Einreichungen · **F2** Verzeichnis · **F3** Werbung · **F4** Social (Regelwerk zusätzlich einmalig durch KBS).

## Skills und Agents

- Skills (`.claude/skills/`): `tamil-marke`, `tamil-screens`, `tamil-richtung`, `tamil-kritik`, `impeccable`,
  `tamil-theme`, `tamil-cockpit`, `radar-research`, `radar-auswertung`, `coolify-betrieb`, `tamil-migration`, `pruefen`.
- Agents (`.claude/agents/`): `referenz-scout`, `art-director`, `design-kritiker`, `qa-pruefer`, `theme-bauer`,
  `cockpit-bauer`, `radar-entwickler`, `plugin-bauer`, `code-pruefer`, `redakteur`, `migrator`.
- Wer was macht und wann: `docs/ablaeufe.md`. Was entschieden ist (nicht stillschweigend umkehren):
  `docs/entscheidungen.md`.

## Gemeinsames Agent-Playbook

Für modellübergreifendes Routing, geprüfte Skillquellen, Schnittstellen-/QA-Verträge und den kopierbaren
Umsetzungsauftrag zusätzlich `docs/agent-playbook/README.md` lesen. `AGENTS.md` führt andere Runner zu denselben
Projektregeln. Vertragsregister, Entscheidungslog, bestehende Commands und dokumentierte Tore bleiben maßgeblich.
