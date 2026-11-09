---
name: tamil-richtung
description: Wie eine Gestaltungsrichtung für tamil.de als Skizze oder Probeseite entsteht – fester Umfang, Pflichtbegründung, Ablage, Prüfung. Vorgeladen im art-director; gilt für /design-runde und /design-ausbau.
user-invocable: false
---

# Eine Richtung gestalten

Du baust **genau eine** Richtung. Grundlage: `design/brief.md` (Tor G1), `design/referenzen/README.md`, Skill
`tamil-marke` (Pflichten, Verbotsliste), Skill `impeccable` (Gestaltungsgesetze, brand-Register). Der Auftrag nennt
dir den `slug` und die Richtung.

## 1. Erst denken, dann bauen – `design/richtungen/<slug>/begruendung.md`

Pflichtfelder, bevor eine Zeile CSS entsteht:

1. **Vorbild:** 1–2 echte Vorbilder aus `design/referenzen/` (Name + URL) und was genau du übernimmst.
2. **Idee in einem Satz:** was diese Seite hat, das nur zu tamil.de passt (nicht „modern und jung“).
3. **Drei Stimmwörter** als Gegenstände gedacht (z. B. „Siebdruck, Kinokasse, Straßenbanner“).
4. **Schrift:** nach dem impeccable-Verfahren (`reference/brand.md`, Abschnitt Font selection): drei Reflex-Schriften
   nennen und verwerfen; gewählte Familie(n) mit Begründung; Latein **und** Tamil abgedeckt (Google Fonts mit
   Tamil-Unterstützung oder selbst gehostet mit Lizenz). Nicht erlaubt: impeccable-Ausschlussliste und die in
   `tamil-marke` genannten verbrannten Schriften.
5. **Farbstrategie:** Restrained / Committed / Full palette / Drenched – mit Rot aus dem Logo als Träger; Tokens in
   OKLCH; nie reines Schwarz/Weiß.
6. **Signatur-Element:** das eine Ding, an dem man die Seite wiedererkennt.
7. **Abgrenzung:** in drei Punkten, warum das nicht wie die drei abgelehnten Runden aussieht
   (`tamil-marke/references/abgelehnt.md`).

## 2. Umfang

| Auftrag | Seiten | Inhalt |
|---|---|---|
| Skizze (`/design-runde`) | `index.html` (erster Bildschirm + **ein** weiterer Abschnitt, z. B. Kino oder Events) und `artikel.html` (Kopf bis erster Absatz) | Handy und Desktop gleich ernst |
| Probeseite (`/design-ausbau`) | Start, Artikel, Rubrik, Events, Kinoliste, Kontakt | alle Zustände, die das Theme braucht |

- Echte Inhalte aus `tamil-marke/references/inhalte.md`; Bilder relativ aus `../../../prototyp/static/img/` einbinden.
- Eigene CSS-Datei `<slug>.css`, keine gemeinsame Basis mit anderen Richtungen, kein Framework.
- JavaScript nur, wenn die Idee es braucht (z. B. Wischen); Inhalte müssen ohne JS sichtbar sein.
- Pflichten aus `tamil-marke` gelten schon in der Skizze (18 px, 44 px, Kontrast, `lang="ta"`).

## 3. Prüfen, bevor du abgibst

```bash
node tools/shots.mjs design/richtungen/<slug>/index.html design/richtungen/<slug>/artikel.html \
     --out design/richtungen/<slug>/shots --kacheln
```

- 0 Fehler im Bericht; Hinweise zu Tippflächen und Tamil beheben.
- Erste Kacheln (`-k0`) bei 390 und 1280 ansehen und gegen die eigene Idee prüfen: Ist das Signatur-Element im
  ersten Bildschirm sichtbar? Würde jemand sagen „das ist eine App-Vorlage“? Dann überarbeiten.
- Gegen die Verbotsliste prüfen.

## 4. Abgabe

Kurzbericht (max. 10 Zeilen): Pfade, Idee in einem Satz, Vorbild, Schrift, Prüfergebnis. **Keine** Selbstbewertung –
die macht der `design-kritiker`.

Bei einer Überarbeitung nach Kritik: nur die P0/P1-Punkte aus `design/kritik/<slug>-r<n>.md` beheben, `begruendung.md`
um einen Abschnitt „Überarbeitung“ ergänzen, neu prüfen.
