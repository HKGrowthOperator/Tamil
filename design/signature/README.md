# Tamil Dots 04A – Signature-Element

> **Status (19.11.2026):** Master-Form **freigegeben 19.11.** von Luis (`docs/abnahme/2026-11-19-signature.md`);
> der Abgleich mit Feld A der Originalreferenz ist nicht erfolgt. Platzierungen als Website-Hintergrund **im Theme
> 3.5.0, Freigabe vor Testsystem ausstehend** (`wordpress/themes/tamil/assets/img/signatur/`, DESIGN.md „Signet“).
> Alles andere hier (Small, Mini, Farbvorschläge, Hintergründe, Animation, Variante C) bleibt Entwurf.

Tamil Dots ist **nicht das Logo**. Es ist das Signature-Element des Content- und Interface-Designsystems: der
Punktbogen in News-Karten, Website-Modulen und auf Instagram, Facebook und WhatsApp. Die Wortmarke tamil.de bleibt
unverändert und steht immer getrennt vom Signet.

## Grundlage

- Verbindlich wäre laut Luis die Datei „vier_rote_punktmarken_für_tamil.de.png“, Feld A. **Sie liegt uns nicht vor.**
- Vorhanden ist nur `vorlage/tamil-dots-04a-vorlage.jpg` (01 Master, 02 Small, 03 Spatial). Danach ist alles hier gebaut.
- Sobald Feld A vorliegt: Datei nach `vorlage/` legen, `werkzeug/vektorisieren.py` auf das neue Feld richten, neu
  erzeugen, Vergleich wiederholen.

## Wie die Form entsteht

1. `werkzeug/vektorisieren.py` misst jeden Punkt der Vorlage als Ellipse aus. Gemessen werden Lage, beide Halbachsen,
   Drehung und Farbton. Verschmolzene Nachbarn werden getrennt, feine Punkte im Auslauf in einem zweiten Durchgang
   erfasst. Ergebnis: `daten/punkte.json`, 238 Punkte Master, 60 Punkte Small, Einheit Bildpunkte der Vorlage.
2. `tamil_dots.py` (nur Python-Standardbibliothek) baut daraus alle Dateien als saubere Vektoren. Jeder Punkt ist ein
   eigenes `<ellipse>`, also einzeln editierbar. Es gibt keine eingebetteten Bilder und keine Metadaten.
3. Erprobt und verworfen: ein rein rechnerischer Nachbau (Punktraster auf einer Kugel in Perspektive). Er traf
   Silhouette, Auslauf und Punktgrößen nur grob (Pixel-Überdeckung mit der Vorlage etwa 30 %). Der Nachbau aus den
   Messwerten erreicht **87 % (Master) und 85 % (Small)**. Der Rest sind die weichen JPG-Kanten der Vorlage.

```bash
python3 design/signature/werkzeug/vektorisieren.py   # Vorlage -> daten/punkte.json   (braucht numpy, Pillow)
python3 design/signature/tamil_dots.py                # alle SVG/HTML neu              (nur Standardbibliothek)
python3 design/signature/tamil_dots.py --liste        # Übersicht: Datei, Punkte, Größe
python3 design/signature/werkzeug/vergleich.py        # vergleich.jpg + vergleich-overlay.jpg (Pillow, Playwright)
```

## Dateien

| Datei | Was | Punkte | Größe |
|---|---|---|---|
| `master.svg` | **01 Master** („Tamil Dots A“), Form freigegeben 19.11.: flach, transparent, nur #660000 → #B30000 in 7 Stufen | 238 | 18 KB |
| `small-entwurf.svg` | **02 Small**, eigener Entwurf nach Feld „02 Small“: weniger, größere Punkte, Teilbogen. Ersetzt den Master nicht | 60 | 5 KB |
| `mini-entwurf.svg` | Mini für 24–48 px, aus Small abgeleitet (Größen gestaucht, Berührungen ausgedünnt) | 47 | 4 KB |
| `mini-16-entwurf.svg` | Mini für 16–23 px, noch gröber | 23 | 2 KB |
| `spatial.svg` | **03 Spatial**: Scheiben mit Kante und weichem Bodenschatten. Nur für besondere Orte | 238 | 29 KB |
| `animiert.svg` | „Punkte bauen die Form auf“, spielt beim Öffnen einmal ab | 238 | 24 KB |
| `variante-c.svg` | **Variante C**: unterste Punktreihe als Welle. Nur als Bewegung, nie als stehendes Zeichen | 50 | 5 KB |
| `animation.html` | Vorführung von Aufbau und Variante C mit Knopf und Einbau-Beispiel | – | – |
| `vorschlaege/master-*.svg` | **Vorschläge**, nicht Teil des Masters: `rot-auf-weiss` (weiße Platte), `weiss` (für rote Flächen), `hell` (leise Tönung auf Weiß), `impact-auf-titan`, `titan-auf-impact` | 238 | je 18 KB |
| `hintergrund/*.svg` | **Vorschläge** für Website-Hintergründe, dekorativ (`aria-hidden`), transparent | 56–238 | 4–18 KB |
| `hintergrund/vorschau.html`, `vorschau-390.png`, `vorschau-1280.png` | Hintergründe im Zusammenhang (Kopf, Rubrikband, Titan-Fläche, Fuß, 404) | – | – |
| `vergleich.jpg` | Vorlage und Nachbau nebeneinander, gleiche Größe (Master, Small, Spatial) | – | – |
| `vergleich-overlay.jpg` | Vorlage grau, Nachbau blau halbtransparent darüber | – | – |
| `mini-test.png` | Mini bei 16, 24, 32, 48 px, dazu Master bei 32 px (3-fach vergrößert) | – | – |
| `daten/punkte.json` | Messwerte (x, y, Halbachsen, Drehung, Ton 0..1) | – | 11 KB |

Alle SVG haben eine `viewBox`, keine feste Breite oder Höhe und bleiben unter 30 KB.

## Farben

- **Master:** ausschließlich Titan Red `#660000` und Impact Red `#B30000` sowie 5 Zwischenstufen. Der Ton folgt der
  Vorlage: dunkel am großen linken Fuß, hell nach oben rechts. Flach, ohne Verlauf in der Fläche und ohne Schatten.
- **Vorschläge** (`vorschlaege/`, `hintergrund/`) mischen nur Titan, Impact und Weiß. „hell“ ist eine echte helle
  Farbe (Impact mit Weiß gemischt), keine Deckkraft. Dadurch bleibt sie auf jedem Weiß gleich.
- Gewichtung laut Handoff: Titan ~35 % · Impact ~10 % · Weiß ~50 % · Schwarz (Schrift) ~5 %.

## Größen und Schutzraum

| Fassung | Einsatz | kleinste Breite |
|---|---|---|
| Master | Kopfbereiche, Karten, große Flächen | 120 px (Bildschirm), 30 mm (Druck) |
| Small | Kacheln, Teaser, Social-Ecken | 48 px |
| Mini | Icon, Favicon-Nähe, Listen | 24 px (`mini-entwurf.svg`), darunter `mini-16-entwurf.svg` ab 16 px |
| Spatial | Sonderseiten (404, Jahresrückblick, Titelseite eines Specials) | 320 px |

- **Schutzraum** um das freistehende Signet: rundum mindestens 8 % seiner Breite (etwa der größte Punkt). Darin
  stehen kein Text, kein Logo, keine Bildkante.
- **Als Hintergrund** darf das Signet von der Kante der Fläche angeschnitten werden (rechts oder unten). Der große
  linke Fuß oder der Bogen muss erkennbar bleiben.
- Die freie Fläche unter dem Bogen gehört zur Form. Nicht füllen, nichts hineinsetzen.

## Do / Don't

**Do**
- Master auf Weiß oder transparent. Auf roten und dunklen Flächen die Vorschläge `weiss`, `impact-auf-titan`
  oder `titan-auf-impact` nutzen, sobald freigegeben.
- Als Hintergrund rahmen, hinterlegen, gliedern. Mit Abstand zu Text und Gesichtern.
- Animation nur als Antwort auf Scrollen oder Zeigen. Einmal abspielen, dann ruhen.

**Don't**
- Signet nicht in, an oder hinter die Wortmarke setzen. Logo und Signet nicht verschmelzen.
- Nicht außerhalb der Palette umfärben (kein Gold, Blau, Schwarz, keine Verläufe in anderen Farben).
- Nicht spiegeln, drehen, stauchen oder verzerren. Der große Fuß steht links, der Auslauf läuft rechts aus.
- Keine Pfeile, Symbole oder Texte in den Bogen setzen.
- Keine Schatten, Glanz oder 3D außer in `spatial.svg`. Spatial nur an besonderen Orten, nie im Fließtext oder in
  News-Karten.
- Nie unter Überschriften, Fließtext oder Gesichter legen, wenn sie dadurch schlechter lesbar werden. Im Rubrikband
  mit weißen Punkten nur, wo rechts Platz frei bleibt (siehe Vorschau ab 1024 px).
- Variante C nicht als stehendes Zeichen verwenden.

## Animation „Punkte bauen die Form auf“

- Jeder Punkt trägt `style="--i:n"`. n ist die Reihenfolge vom großen linken Fuß (vorn) zum feinen Auslauf (hinten
  rechts). Die Wurzel trägt `--n` (Anzahl) und `--dauer` (Vorgabe 1500 ms).
- Die Klasse `an` an der Wurzel startet den Aufbau. Jeder Punkt wächst mit `cubic-bezier(.16,1,.3,1)`
  (ease-out-expo) von `scale: 0` auf 1 und blendet dabei ein. Nur `scale` und `opacity` werden bewegt.
- Gedrehte Punkte stecken in einer Gruppe mit der Drehung. So wirkt `scale` um die Punktmitte, und die Datei sieht
  auch ohne CSS richtig aus.
- `@media (prefers-reduced-motion: no-preference)` umschließt die Animation. Bei „Bewegung reduzieren“ steht die
  fertige Form sofort da.
- Variante C (`variante-c.svg`): eine Welle läuft zweimal durch die unterste Punktreihe, dann Ruhe.

## Einbau auf der Website (erst nach Freigabe)

- **Statisch als Hintergrund:** CSS `background: url(…/hintergrund/flaeche-impact-auf-titan.svg) right bottom / auto
  110% no-repeat`. Die Dateien in `hintergrund/` sind dekorativ (`aria-hidden="true"`). Die Flächenfarbe kommt aus
  dem CSS.
- **Animiert:** das SVG inline einsetzen (sonst greift das CSS nicht auf die Punkte durch). Beim Hineinscrollen
  einmal `an` setzen (IntersectionObserver, siehe `animation.html`). Keine automatisch startende Animation beim Laden
  der Seite.
- **Barrierefreiheit:**
  - Dekorativ (Normalfall): `aria-hidden="true" focusable="false"`, `<title>` und `role` entfernen. Als CSS-Hintergrund
    oder `<img alt="">` ist das automatisch so.
  - Mit Bedeutung, etwa als eigenständige Markengrafik auf einer Über-uns-Seite: `master.svg` wie geliefert mit
    `role="img"` und `<title>`.
- Benennung: `master.svg` = mit Titel für Hilfsmittel. `hintergrund/*.svg` und `--dekorativ` beim Generator = ohne.

## Offene Punkte

- Abgleich mit Feld A („vier_rote_punktmarken_für_tamil.de.png“) nicht erfolgt; die Master-Form ist trotzdem
  freigegeben (19.11.).
- Platzierungen im Theme 3.5.0: Freigabe vor Testsystem ausstehend.
- Freigabe der übrigen Farbvorschläge, der Hintergründe und der Animation durch Luis.
- Spatial ist eine flache Annäherung (versetzte Kante plus Radialschatten). Für Druck oder große Sonderflächen besser
  einmal sauber in 3D rendern lassen.
