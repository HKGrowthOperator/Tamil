# Bildregeln Tamil.de

Jeder Beitrag auf Tamil.de hat ein Beitragsbild – ohne Ausnahme. Die Reihenfolge im Radar: KI-Symbolbild nach diesen
Regeln → Bild aus dem Bildpool des Themas → freies Stockfoto (nur mit Schlüssel) → Tamil.de-Bildkarte. Diese Datei wird
beim Generieren automatisch als Vorlage gelesen; die Redaktion darf sie anpassen.

## Hausstil

- Editoriale Fotografie: natürliches Licht, echte Räume, Alltag der tamilischen Diaspora in Deutschland, Österreich und
  der Schweiz – Tempel, Vereinsheime, Kinos, Konzerthallen, Küchen, Straßen, Schulhöfe. Keine Stockfoto-Posen.
- Farbwelt: warmes Kumkum-Rot, Manjal-Gelb und tiefes Nachtblau dürfen vorkommen (Blumen, Stoffe, Lichter), aber nicht
  als Filter. Kein HDR, keine Neonfarben, kein Weichzeichner.
- Perspektive: Augenhöhe oder leicht erhöht, 35–50-mm-Look, Hauptmotiv im ersten Drittel, ruhiger Hintergrund, Platz für
  einen Titel-Overlay links oder unten.
- Format 16:9, Querformat, mindestens 1K. Keine Ränder, keine Collagen, keine Rahmen.
- Rubriken: **Kino/Entertainment** = Saal, Leinwandlicht, Plakatwände ohne Text, Bühne, Instrumente; **Community/Kultur**
  = Tempel, Fest, Kolam, Saris, Hände, Lampen; **Nachrichten** = Orte, Gebäude, Landschaft (Küste Jaffnas, Chennai,
  Berliner Behörde) ohne Personen im Fokus; **Küche** = Gericht auf Tisch, Dampf, Gewürze; **Sport** = Spielfeld,
  Trikot ohne Logo; **Events** = Halle, Publikum von hinten, Lichtstimmung.

## Harte Regeln (Symbolbild)

1. **Symbolbild, kein Dokument.** Das Bild stellt die Stimmung oder den Ort dar, nie ein konkretes Ereignis so, als wäre
   es dort fotografiert worden. Keine Nachstellung von Unfällen, Protesten mit erkennbaren Parolen, Gerichtsszenen.
2. **Keine realen Personen.** Keine Schauspieler, Politiker, Sportler, Künstler mit Wiedererkennungswert – auch nicht
   „im Stil von“. Menschen nur anonym: von hinten, im Anschnitt, in der Menge, in Unschärfe.
3. **Kein Text, keine Logos, keine Flaggen, keine Marken, keine Schriftzüge** auf Plakaten, Trikots, Schildern.
4. **Keine religiösen Darstellungen von Gottheiten** als Hauptmotiv (Respekt); Tempelarchitektur, Lampen, Blumen und
   Rituale von außen sind in Ordnung.
5. Keine Gewalt, keine Waffen, keine Verletzten, keine Kinder im Fokus.
6. Jedes KI-Bild wird als Symbolbild gekennzeichnet: Bildnachweis „Symbolbild: KI-generiert · Tamil.de“.

## Vorlage für den Prompt

Der Writer liefert je Beitrag ein `bild_prompt` (Englisch, 30–60 Wörter, nur das Motiv) und ein `bild_thema` (Slug aus
`bildpool.md`). Der Radar setzt daraus den endgültigen Prompt zusammen:

```
Editorial photograph for a German-language news site of the Tamil diaspora.
Scene: {motiv}
Style: natural light, candid documentary feel, 35mm lens look, eye level, calm background, subject in the left third,
warm but realistic colors (kumkum red, marigold yellow, deep indigo accents), no filters.
Strict rules: no text, no letters, no logos, no flags, no watermarks, no real or recognizable people, people only
anonymous (from behind, cropped, in the crowd or out of focus), no deities as main subject, no violence, no children
in focus. Landscape 16:9.
```

`{motiv}` wird durch `bild_prompt` ersetzt. Fehlt `bild_prompt`, nimmt der Radar den Motiv-Prompt des Themas aus
`bildpool.md`.
