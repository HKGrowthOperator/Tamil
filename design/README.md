# design/

Arbeitsordner für das Redesign. Abläufe: `/design-runde`, `/design-ausbau`, `/design-umsetzung` (siehe
`docs/ablaeufe.md`). Marke und Verbotsliste: `PRODUCT.md`, `.claude/skills/tamil-marke/`.

```
design/
  brief.md                  bestätigter Brief (Tor G1), Grundlage für alle Richtungen
  referenzen/               Vorbilder mit Screenshots (referenz-scout)
  richtungen/<slug>/        je Richtung: index.html, artikel.html, <slug>.css, begruendung.md, shots/
  kritik/<slug>-r<n>.md     unabhängige Kritik je Runde (design-kritiker)
  vergleich/                Vergleichsseite für Tor G2
  tokens.css                verbindliche Tokens nach Tor G3 (Quelle für Theme und Cockpit)
```

Regeln:
- Jede Richtung ist eigenständig: eigene CSS-Datei, keine gemeinsame Basis mit anderen Richtungen.
- Nur echte Inhalte aus `prototyp/content/*.json` und dem Radar; Bilder aus `prototyp/static/img/` werden relativ
  eingebunden, nicht kopiert.
- Schriften selbst gehostet (woff2 + Lizenzdatei im Richtungsordner) oder Google Fonts.
- Nichts aus diesem Ordner wird direkt ins Theme kopiert; die Umsetzung läuft über `tokens.css` und `DESIGN.md`.
