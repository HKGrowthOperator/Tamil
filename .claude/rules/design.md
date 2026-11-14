---
paths:
  - "design/**"
  - "wordpress/themes/**"
  - "news_radar/web/static/**"
  - "news_radar/web/templates/**"
  - "prototyp/**"
  - "PRODUCT.md"
  - "DESIGN.md"
---

# Regeln: Gestaltung

- **Seit 13.11.2026 gilt `design/brief-v3.md` mit Hallmark** (`/home/user/hkgrowthoperator/hallmark/skills/hallmark/`,
  Repo `HKGrowthOperator/hallmark`): Floor, Reflex-Gates, Stempel oben im CSS, `sloplint --genre editorial --render`
  ohne FAIL, Prüfung aus frischem Kontext. Der Floor geht den alten Punkten unten vor (keine Dachzeilen, keine
  Versal-Labels, keine „·“-Metazeilen, keine Kartenraster). Erste Probe: `design/richtungen/hm-eigen/`.
- **Ablauf statt Alleingang:** Gestaltet wird über `/design-runde` (Schnellproben → Vorschau für Luis → Prüfung) →
  Tor G2 → `/design-ausbau` → Tor G3 → `/design-umsetzung`. Die Hauptsitzung gestaltet nicht selbst nebenbei
  (Ausnahme 13.11.: auf Anordnung von Luis, siehe `docs/entscheidungen.md`).
- **Markenwissen zuerst:** Skill `tamil-marke` (Zielgruppe, Pflichten, Verbotsliste in
  `references/abgelehnt.md`). Sieben Runden sind abgelehnt; nichts davon wiederholen.
- **Ziel:** eine Seite, die gemacht und nicht generiert aussieht und nur tamil.de gehören kann (`design/brief-v3.md`);
  `design/brief.md` (Nachrichtenmarke) gilt nur noch für Logo, Sprache, Lesbarkeit und echte Inhalte.
- **Jede Probe hat `begruendung.md`** mit dem Hallmark-Picks-Block (Idee, Achsen, Schriften, Farben, Signatur), den
  Ergebnissen von `sloplint` und `tools/shots.mjs` und der Abgrenzung gegen die Runden 1–7 (`abgelehnt.md`).
- **Prüfung ist unabhängig und misst:** Der `design-kritiker` sieht nur Ergebnis und Brief und liefert Messwerte und
  Befunde. Durchgelassen wird, was alle harten Kriterien des Briefs erfüllt und kein offenes P0 oder P1 hat; das
  entscheidet die Hauptsitzung. Luis sieht Schnellproben vorher, der Auftraggeber nur Gewähltes und Bestandenes.
- **Pflichten:** WCAG 2.2 AA, Fließtext ≥ 18 px am Handy, Tippflächen ≥ 44 px, `lang="ta"` für Tamil,
  `prefers-reduced-motion`, kein seitliches Scrollen bei 390/820/1280.
- **Echte Inhalte**, keine erfundenen Titel, Daten, Bildnachweise oder Kontakte.
- **`prototyp/` ist Archiv:** dort nichts Neues bauen; neue Arbeit gehört nach `design/`.
- **Cockpit** folgt dem Produkt-Register: gleiche Tokens, ruhiger, Klarheit vor Ausdruck.
