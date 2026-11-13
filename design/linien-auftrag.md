# Auftrag für die Design-Linien (Nacht 13./14.11.2026)

Luis will „mehrere Linien fertig“ und wählt danach selbst. Jede Linie ist eine vollständige Gestaltung von Website und
Redaktions-Cockpit mit Hallmark. Diese Datei gilt für jeden Gestalter einer Linie; die Besonderheiten der Linie stehen
im jeweiligen Auftrag.

## Pflichtlektüre

1. `design/brief-v3.md` (gilt vor `design/brief.md`) und `.claude/skills/tamil-marke/references/abgelehnt.md`
   (Runden 1–7: nichts davon wiederholen).
2. Hallmark: `/home/user/hkgrowthoperator/hallmark/skills/hallmark/SKILL.md` und die dort genannten Referenzen
   (Floor, Reflex-Gates, Stempel oben im CSS, Picks-Block, Theme-Datei unter `references/themes/<theme>.md`).
3. Inhalte: `design/inhalte/rueckblick/rueckblick.json` (20 Beiträge mit Bildern und Nachweisen, Bilder unter
   `design/inhalte/rueckblick/bilder/`), `design/inhalte/inhalte.json` (Kino, Termine), `design/inhalte/logo.png`,
   `docs/redaktion/rueckblick-2026.md` (62 datierte Einträge), `design/richtungen/hm-eigen/bauen.py` (Beispiel, wie
   man daraus Seiten erzeugt).
4. Fachliches für die neuen Seiten: `docs/spezifikation/datenmodell.md` §12 (Einsendung), §13 (Verzeichnis), §14
   (Werbeplatz, Angebot, Buchung), §15 (Social), §8 (Bild-Lizenz); `docs/vertrag/festlegung-*.md`;
   `wordpress/plugins/tamil-site/includes/ads.php` (die sechs Werbeplätze und ihre Maße).

## Seiten (Website), je Handy 390 und Desktop 1280

| Datei | Inhalt |
|---|---|
| `index.html` | Startseite |
| `rubrik.html` | Rubrik „Community“ (Liste mit Bildern, Seitennavigation) |
| `artikel.html` | Artikel (Deepavali, Beitrag 30) mit Bildnachweis, Teilen per WhatsApp, Weiterlesen |
| `termine.html` | Festkalender: kommende Termine zuerst, Jahr 2026 darunter |
| `kino.html` | Kino diese Woche nach Stadt |
| `verzeichnis.html` | Verzeichnis: Suche, Filter Art (Business, Dienstleister, Verein, Tempel) und Ort (Land, Bundesland/Kanton, Stadt), Liste |
| `verzeichnis-eintrag.html` | Profil eines Eintrags (Premium-Markierung sichtbar gekennzeichnet) |
| `einreichen.html` | Formular „Termin einreichen“ (Felder aus §12), Einwilligung, Bestätigungsseite als Zustand |
| `werben.html` | Werbeplätze und Preise (Preise als Platzhalter „Preis folgt“), Ablauf der Buchung |
| `buchen.html` | Buchung Schritt für Schritt (Platz, Zeitraum mit Verfügbarkeit, Werbemittel-Upload, Zusammenfassung, Zahlung) |
| `kontakt.html` | Kontakt (Platzhalter klar gekennzeichnet) mit Formular „Nachricht“ |

## Cockpit (App-Screens, Produkt-Register: ruhiger, gleiche Tokens), Ordner `design/cockpit/<slug>/`

| Datei | Inhalt |
|---|---|
| `uebersicht.html` | Stand: wartende Entwürfe, Eingang, Social, Budget, Stopp-Schalter |
| `entwurf.html` | Entwurf mit Text, Claims und Belegen je Absatz, Bild mit Lizenz-Datensatz (und Zustand „Lizenz fehlt“ mit Formular), Freigabe |
| `eingang.html` | Einsendungen (Termin, Beitrag, Kooperation, Werbung, Kontakt) mit Agenten-Prüfung und Übernahme |
| `social.html` | Social-Historie je Kanal, Karenz-Countdown, „von Hand entscheiden“, WhatsApp-Entwurf zum Kopieren |
| `verzeichnis.html` | Verzeichnis-Einsendung: alt gegen neu, Dublettenhinweis, Freigabe |
| `buchungen.html` | Werbebuchungen: Liste, Prüfung des Werbemittels, Status, Einblendungen und Klicks |

Cockpit-Daten dürfen Beispieldaten sein, müssen aber als solche erkennbar plausibel sein (keine echten Personen,
keine echten Telefonnummern, E-Mail nur `@example.org`). Die Website zeigt nur echte Inhalte; wo es keine gibt
(Verzeichnis-Kontakte, Preise, Impressum), steht ein sichtbarer Platzhalter. Für das Verzeichnis nur Einrichtungen,
die in den Rückblick-Beiträgen vorkommen (Name, Stadt, Art), ohne erfundene Kontaktdaten.

## Regeln

- Nur Deutsch, keine tamilische Schrift als Schmuck, Logo unverändert (`bilder/logo.png`), Bildnachweis an jedem Bild.
- Fließtext am Handy mindestens 18 px, Kontrast WCAG 2.2 AA, Tippflächen 44 px, kein seitliches Scrollen bei
  390/820/1280, `prefers-reduced-motion`. Schriften selbst gehostet (OFL, Lizenz im Ordner).
- Keine Gedankenstriche im Text (Hallmark Gate 19), keine Dachzeilen, keine Versal-Labels, keine „·“-Metazeilen,
  keine gleich großen Kartenraster, keine Verlauf-Bildkacheln, keine Seitenstreifen als Akzent.
- Nur im eigenen Ordner schreiben (`design/richtungen/<slug>/` und `design/cockpit/<slug>/`). Kein Git.

## Prüfen, bevor du fertig meldest

- Lokaler Server: `cd /home/user/Tamil/design && python3 -m http.server <port> --bind 127.0.0.1 &` (Port aus deinem
  Auftrag). Schriften laden über `file://` nicht; geprüft wird über `http://127.0.0.1:<port>/…`.
- Hallmark: `HALLMARK_PUPPETEER=/tmp/claude-0/-home-user/328bcd38-019d-5546-955b-7fea86a20fa1/scratchpad/pptr/node_modules/puppeteer-core
  CHROME_PATH=/tmp/claude-0/-home-user/328bcd38-019d-5546-955b-7fea86a20fa1/scratchpad/chrome-ns.sh node
  /home/user/hkgrowthoperator/hallmark/skills/hallmark/scripts/sloplint.mjs <dateien> --genre editorial --url <adressen>`
  (Cockpit mit `--scope app`). Ziel: 0 FAIL; REFLEX und WARN begründet beheben oder im Stempel ausnehmen.
- `node /home/user/Tamil/tools/shots.mjs <datei> --out <ordner>`: 0 Fehler bei 390/820/1280.
- `begruendung.md` mit Picks-Block, Seitenliste, Prüfergebnissen und den eigenen Schwächen in einem Satz je Punkt.

## Bericht

Höchstens 15 Zeilen: Idee der Linie in einem Satz, Seitenliste, Prüfergebnisse, offene Schwächen.
