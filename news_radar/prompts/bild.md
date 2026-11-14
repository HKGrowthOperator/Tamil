# Bildregeln Tamil.de

Jeder Beitrag auf Tamil.de hat ein Beitragsbild – ohne Ausnahme. KI-Symbolbilder und der Bildpool gelten nur mit
BILD_KI_FREIGABE (Entscheidung „keine KI-Bilder“, Spezifikation Bilder 4.1); sonst endet die Kette bei der Bildkarte. Diese Datei wird
beim Generieren automatisch als Vorlage gelesen; die Redaktion darf sie anpassen.

## Hausstil

- Editoriale Fotografie: natürliches Licht, echte Räume, Alltag der tamilischen Diaspora in Deutschland, Österreich und
  der Schweiz – Tempel, Vereinsheime, Kinos, Konzerthallen, Küchen, Straßen, Schulhöfe. Keine Stockfoto-Posen.
- Farbwelt: warmes Kumkum-Rot, Manjal-Gelb und tiefes Nachtblau dürfen vorkommen (Blumen, Stoffe, Lichter), aber nicht
  als Filter. Kein HDR, keine Neonfarben, kein Weichzeichner.
- Perspektive: Augenhöhe oder leicht erhöht, 35–50-mm-Look, Hauptmotiv im ersten Drittel, ruhiger Hintergrund, Platz für
  einen Titel-Overlay links oder unten.
- Format 4:3, Querformat. Keine Ränder, keine Collagen, keine Rahmen.
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
Editorial photograph for a German-language community magazine of the Tamil diaspora in Germany, Austria and
Switzerland.
Scene: {motiv}
Style: natural light, candid documentary feel, 35-50mm lens look, eye level, calm uncluttered background, main subject
in the left third, empty area in the lower left for a caption, warm but realistic colours (kumkum red, marigold
yellow, deep indigo only as accents in flowers, fabrics or light), no filter, no HDR, no neon.
Strict rules: this is a symbolic image, not a depiction of a real event. No text, letters, numbers, signs, posters
with writing, logos, brand names, watermarks or flags. No real, famous or recognizable people and nobody "in the
style of" a real person. People only anonymous: from behind, cropped at the shoulders, as small figures in a crowd or
out of focus; no faces in focus. No children in focus. No deities, idols or religious symbols as decoration; temple
architecture only as a place. No political symbols, no tiger imagery, no military, uniforms, weapons, violence,
injuries, protests or courtrooms. No borders, frames or collage.
Format: landscape 4:3.
```

`{motiv}` wird durch `bild_prompt` ersetzt. Fehlt `bild_prompt`, nimmt der Radar den Motiv-Prompt des Themas aus
`bildpool.md`.
