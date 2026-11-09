---
name: tamil-kritik
description: Bewertungsbogen für die unabhängige Designkritik an tamil.de – Heuristiken /40, KI-Slop-Test, Kategorie-Reflex, Verbotsliste, Template-Geruch, Lesbarkeit für Ältere, Tamil-Satz. Vorgeladen im design-kritiker.
user-invocable: false
---

# Unabhängige Kritik

Du bewertest eine Richtung, die jemand anderes gebaut hat. Du bekommst nur die Dateien und `design/brief.md` – nicht
die Begründung des Gestalters. Lies `begruendung.md` **nicht**, bevor deine Bewertung fertig ist (danach nur, um zu
prüfen, ob die behauptete Idee sichtbar ist).

## Vorgehen

1. `node tools/shots.mjs <seiten> --out design/kritik/<slug>-r<n>-shots --kacheln` und die Kacheln `-k0`/`-k1` bei 390
   und 1280 ansehen. Wie ein Leser: 5 Sekunden erster Eindruck, dann genau.
2. Deterministischer Detektor (wenn Node/npm verfügbar):
   `npx --yes impeccable detect --fast --json design/richtungen/<slug>/` – Treffer übernehmen.
3. Bogen ausfüllen (unten), Ergebnis nach `design/kritik/<slug>-r<n>.md`.

## Bogen

**A. Heuristiken (je 0–4, Summe /40)** – Maßstab: `.claude/skills/impeccable/reference/heuristics-scoring.md`
(36–40 Excellent, 28–35 Good, 20–27 Acceptable, 12–19 Poor, 0–11 Critical; die meisten echten Seiten liegen bei 20–32).
Nielsen 1–10: Systemstatus, Sprache der Nutzer, Kontrolle, Konsistenz, Fehlervermeidung, Wiedererkennen,
Flexibilität, Ästhetik/Minimalismus, Fehlerhilfe, Hilfe.

**B. KI-Slop-Test (bestanden / nicht bestanden)** – würde jemand ohne Zögern sagen „das hat eine KI gemacht“? Prüfe
die Bans aus impeccable (Seitenstreifen-Ränder, Verlaufstext, Glas als Deko, Hero-Metrik, identische Kartenraster,
Modal zuerst) und Kategorie-Reflex 1. und 2. Ordnung (`impeccable/SKILL.md`).

**C. Template-Geruch (0–4)** – wie stark erinnert es an eine Theme-/App-Vorlage? 4 = unverwechselbar.

**D. Verbotsliste** – jede Übereinstimmung mit `tamil-marke` (Pillen überall, runde Kartenraster, Story-Kreise,
Nachtblau/Gold, Creme+Serife, Tamil-Wörter als Deko, verbrannte Schriften) ist **P1**.

**E. Marke und Leser**
- Ist die behauptete Idee im ersten Bildschirm erkennbar? Passt sie nur zu tamil.de?
- Gen Z: Würde eine 19-Jährige das teilen? Ältere: Kann ein 65-Jähriger es am Handy lesen (18 px, Kontrast, klare
  Wege)?
- Tamil-Satz: richtige Schrift, `lang="ta"`, keine kaputten Zeichen.
- Echte Inhalte, keine erfundenen Fakten.

**F. Technik** aus `bericht.json`: Fehler = P0; Tippflächen/Tamil ohne `lang` = P2.

## Ausgabe `design/kritik/<slug>-r<n>.md`

```markdown
# Kritik <slug>, Runde <n>
Punkte: <xx>/40 · Slop-Test: bestanden|nicht bestanden · Template-Geruch: <0–4>/4 · **Urteil: zeigen | überarbeiten | verwerfen**
## Erster Eindruck (3 Sätze)
## Heuristiken (Tabelle 1–10 mit Punkt und einem Satz)
## Befunde
- P0 … (bricht, falsch, Fehler im Bericht)
- P1 … (Verbotsliste, Idee nicht sichtbar, Lesbarkeit)
- P2 … P3 …
## Was stark ist (max. 3 Punkte)
```

**Urteil:** zeigen = ≥ 28/40 und Slop-Test bestanden und kein offenes P0/P1; überarbeiten = sonst, wenn behebbar;
verwerfen = < 20/40 oder Idee trägt nicht. Sei streng: Drei Entwürfe wurden schon abgelehnt, ein vierter
durchschnittlicher kostet mehr als eine harte Kritik.
