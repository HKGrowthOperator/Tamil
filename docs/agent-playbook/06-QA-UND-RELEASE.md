# QA, Nachweise und Release

## Angemessene Prüfung

Dokumentänderungen: Verweise, Widersprüche, Pfade, Branchbasis, Geheimnisse und tatsächlichen Diff prüfen.
Kein Produktlauf allein für einen Textfehler.

Produktänderungen: betroffene Tests und aussagekräftige Regression zuerst; integrierten Stand mit den
Projektprüfungen verifizieren. Übersprungene WP-Tests explizit nennen; `pytest grün` ohne laufendes WordPress
ist kein vollständiger Plugin-Nachweis.

Bestehende Befehle aus `CLAUDE.md`:
- `python -m pytest -q`
- `python -m news_radar abnahme`
- für Theme/Plugins zusätzlich `bash wordpress/dev/lint.sh`
- für Oberflächen `node tools/shots.mjs <url|datei> --out <ordner>`
- lokales WordPress nach den vorhandenen `wordpress/dev/`-Anweisungen

Befehle erst nach Prüfung der tatsächlichen Umgebung ausführen. Paketinstallation, Docker oder fremde
CHECK-Skripte nicht ungeprüft aus einem Skillkatalog übernehmen.

## Wesentliche Prüfungen

| Bereich | Kritische Probe | Nachweisgrenze |
|---|---|---|
| Formulare | gültig/ungültig, Upload, Spam, erneut senden, unberechtigt | echte Speicherung und Eingang, keine bloße Erfolgsbox |
| Verzeichnis | neuer Eintrag, Dublette, fehlendes Feld, Änderungsrevision, Premium-Rechte | öffentliche Änderung erst freigegeben |
| Belegung | zwei parallele Buchungen auf letzte Kapazität, Ablauf vs. verspätete Zahlung | tatsächlich eingesetzte Ziel-DB testen; laut Repo derzeit SQLite, keine MySQL-Annahme |
| Zahlung | Erfolg, Ablehnung, manipulierte Signatur, doppeltes/ungeordnetes Event, Timeout | Testmodus und echter Provider getrennt |
| Kampagne | bezahlt ohne Freigabe, freigegeben ohne Zahlung, Pause, Start, Ende | keine Ausspielung außerhalb aller Bedingungen |
| Social | Artikel und Event, IG-Erfolg/FB-Fehler, Tokenablauf, Timeout, Dublette | tatsächliche/API-bestätigte Kanal-IDs für B5 |
| Agenten | Stop vor Senden, Lease-Verlust, Jobneustart, Budgetgrenze, Rechte | Kontrolle am wirksamen Übergang |
| Mailverzicht | eigene Codepfade, WP-Core/Plugins, Providerkonten | Scanner ergänzt Laufzeit-/Konfigurationsprüfung |
| Migration | zweiter Import, Originaldaten, Medien, Redirects | alte Inhalte nicht löschen oder neu datieren |
| Oberfläche | mobile/desktop, Tastatur, Fokus, Fehler/Leer/Ladezustand | echte Seiten und tatsächliche Viewports |

Providerzugänge fehlen: lokale Simulation fertigstellen und kennzeichnen; nach Providerzugang
nur die fehlende Integrationsgrenze nachweisen. Keine mehrfachen Liveaktionen nur für neue Screenshots.

## Vertragliche Abnahme B5

Bestehende T1–T7 in `docs/vertrag/leistungen.md` sind maßgeblich:
Artikel zu IG/FB; Event zu IG/FB; WhatsApp-Entwurf; Verzeichnisneu-/Änderung;
Checkout Erfolg/Fehler; Aktivierung/Laufzeitende; Stopp/Fehler/redaktionelle Verwaltung.
Für jeden Fall Commit, Umgebung, Datum, echte oder simulierte Grenze und Ergebnis dokumentieren.
Ein Mock ist kein API-bestätigter Veröffentlichungstest.

## Releaseablauf

1. Aktuellen Integrations-SHA und Änderungen anderer Schreiber prüfen.
2. Relevante Ergebnisse integrieren; Code-Prüfer auf tatsächlichen Diff und unabhängige QA ansetzen.
3. P0/P1 lösen, übrige Befunde mit Auswirkung festhalten.
4. Das bestehende Vertragsregister und Entscheidungslog aktualisieren; keine neuen konkurrierenden Listen.
5. PR und dokumentierte Tore nutzen; Deployziel und Datenbank getrennt vom Git-Branch verifizieren.
6. Nach freigegebenem Deploy Gesundheit, Kernablauf und Rollbackweg prüfen; Tokens nicht ausgeben.
7. Übergabe an KBS mit Kernabläufen, Zugangsweg, offenen Punkten und Abnahmeprotokoll.

Ein Dokumentations-PR erteilt weder G2/G3/F0–F4 noch Produktionsfreigabe, hebt keine bestehende
Autorisierung auf und schaltet keine Funktion ein. Domainumschaltung und Anbieteraktionen erfolgen erst im
entsprechenden bereits autorisierten Arbeitsauftrag.
