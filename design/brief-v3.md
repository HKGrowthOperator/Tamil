# Design-Brief v3 – tamil.de (13.11.2026)

Gilt ab 13.11.2026 für alle neuen Gestaltungen (Website und Redaktions-Cockpit). Ersetzt die messbaren
„Nachrichtenmarken“-Kriterien aus `design/brief.md` (Fassung 2/2.1). Bleibt gültig: Logo, Sprache, Lesbarkeit,
echte Inhalte, Bildnachweise.

## Warum neu

Urteil von Luis am 13.11. über `mix-ordnung` und `mix-feed` (und alles davor): „komplett generisch“, „generischer
AI-Slop“, „katastrophal“. Der Kunde zahlt 28.000 € netto; die Seite muss gemacht aussehen, nicht generiert.

Was bisher den generischen Eindruck erzeugt hat (nicht wiederholen):

- Nachrichtenportal-Muster: Dachzeilen über jeder Überschrift, Labels in Versalien mit Sperrung, Metazeilen mit „·“,
  Rubrik-Reihen, gleich große Kartenraster, Bildkacheln mit dunklem Verlauf und Titel im Bild, „Diese Woche“-Bänder.
- Runde 1: Nachtblau mit Gold. Runde 2: Sand, Braungrau, Serifen-Fließtext, runde Bilder, bunte Rubrikpunkte
  („altbacken“). Runde 3: Pillen, Story-Kreise, rote Platte („Trash, generisch“). Runde 4: riesige rote Schrift,
  Stempel, Schräglagen, Vollfarbflächen („laut, Baukasten“). Runden 5–7 (`klar`, `klar2`, `mix-*`): saubere, aber
  austauschbare Nachrichtenseite.

## Arbeitsweise

Gestaltet wird mit **Hallmark** (`/home/user/hkgrowthoperator/hallmark/skills/hallmark/SKILL.md`), dem Design-Skill,
den Luis dafür bereitgestellt hat: Floor (nicht verhandelbar), Reflex-Gates, `sloplint --render`, Prüfung aus frischem
Kontext. Der Hallmark-Floor geht allen alten Regeln aus `tamil-marke`/`tamil-richtung` vor, wo sie sich widersprechen
(z. B. keine Dachzeilen und keine Versal-Labels mehr, auch nicht für Rubriken).

## Was fest bleibt

- **Logo** unverändert: `design/inhalte/logo.png` (rot). Kein nachgebautes Logo.
- **Nur Deutsch.** Keine tamilische Schrift als Schmuck (Entscheidung Luis, 09.11.). Tamilische Namen im Inhalt sind
  normaler Text.
- **Echte Inhalte** aus `design/inhalte/` (Rückblick-Beiträge mit Bildern und Nachweisen, Altbestand, Kino, Termine).
  Keine erfundenen Zahlen, Zitate, Logos, Termine, Kontakte. Fehlt etwas: Platzhalter sichtbar als solcher.
- **Bilder nur mit Nachweis** (Commons-Credits stehen in `rueckblick.json`); Bildnachweis sichtbar am Bild oder im Fuß.
- **Lesbarkeit:** Fließtext am Handy mindestens 17 px, Kontrast WCAG 2.2 AA, Tippflächen 44 px, Handy zuerst (390),
  Desktop 1280, kein seitliches Scrollen.

## Wer liest und was die Seite tun muss

Tamilische Familien in Deutschland, Österreich und der Schweiz; junge Leute (18–35) am Handy, ihre Eltern ebenfalls.
Jobs der Seite: **lesen** (Community-Nachrichten, Rückblick), **finden** (Kino: welcher Film läuft wo; Termine:
Tempelfeste, Deepavali, Pongal, Vereinsfeste), **teilen** (per WhatsApp an Familie und Freunde).

## Ergebnis je Variante

`design/richtungen/<slug>/`: Startseite, Artikel, Termine, Kino (Rubrik) – Handy und Desktop; `begruendung.md` mit dem
Hallmark-Picks-Block und den Sweep-Ergebnissen; Prüfbilder mit `node tools/shots.mjs` (390/820/1280). Das Cockpit
bekommt eigene App-Screens unter `design/cockpit/<slug>/`.
