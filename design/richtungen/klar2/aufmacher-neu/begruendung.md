# Neuer Aufmacher: vier Ideen, drei Sonderfarben

Stand 21.11.2026. Gesprächsgrundlage für Luis, keine Entscheidung und kein Theme-Umbau. Anlass: Der Wow-Aufmacher
„Punkt für Punkt zum Bild“ (238 Punkte groß in Titan über dem Foto) ist seit Theme 3.13.1 abgeschaltet. Gesucht ist
ein Ersatz, der besonderer ist, die Tamil Dots als Wiedererkennung behält und das Foto nicht verdeckt.

- `index.html`: die Seite (CSS und JS inline, Bilder und Schrift als Dateien daneben).
- `artifact.html`: dieselbe Seite ohne doctype/html/head/body, alles als data-URI (888 KB), gebaut mit `python3 bauen.py`.
- Schrift: Libre Franklin aus dem Theme (`schriften/`, OFL liegt bei). Punktbogen: `ecke.svg` aus
  `wordpress/themes/tamil/assets/img/signatur/`, CSS der Ecke aus `theme.css` übernommen (13 % des Rahmens, 20 bis
  56 px, weiß, dunkler Schein nur dort, wo kein Verlauf liegt).
- Inhalte: Titel, Daten, Rubriken, Bilder, Alt-Texte und Bildnachweise aus der REST-Schnittstelle des Testsystems
  (`/wp-json/wp/v2/posts`, gelesen am 21.11.2026). Nichts erfunden. Die fünf Fotos sind Beitragsbilder des Testsystems
  (dort als Wikimedia-Commons-Fotos mit Nachweis hinterlegt, teils als Symbolbild), auf 1200 px, WebP, Qualität 70.

## Was in allen vier Ideen gleich ist

- Kleiner Punktbogen unten rechts im Bild, wie auf jeder Bildkarte. Kein Punktmuster über dem Foto, keine rote oder
  titanfarbene Fläche über dem Bild.
- Schlagzeile 30 px am Handy, 40 px am Desktop (Idee C 36 px), Gewicht 650, keine Versalien. Das bleibt in den Grenzen
  von Brief §10.
- Bewegung nur unter `prefers-reduced-motion: no-preference`. Ohne Skript, ohne Unterstützung für
  `animation-timeline` und mit „Bewegung reduzieren“ steht sofort der fertige Zustand.

## Idee A: Farbe bricht auf

- **Idee:** Das Foto steht sofort da, in Grau. Der Punktbogen in der Ecke erscheint zuerst, von dort läuft die Farbe
  in rund 1,5 s einmal über das Bild (zweites Bild mit radialer Maske aus der Ecke unten rechts).
- **Unterschied zu den abgelehnten Runden und zum abgeschalteten Wow:** Nichts liegt über dem Foto (keine Decke, keine
  Punkte, kein Rot). Der Titel ist vom ersten Moment an lesbar. Keine Riesenschrift, keine Vollfarbfläche (Runde 4),
  kein App-Muster (Runde 3).
- **Offene Fragen an Luis:** Darf sich der erste Bildschirm einmal beim Laden von selbst bewegen? Bisher gilt „nichts
  bewegt sich von selbst“. Soll das bei jedem Besuch spielen oder nur einmal je Sitzung? Was passiert bei farbarmen
  Fotos (dann normaler Aufmacher)?

## Idee B: Drei Bahnen

- **Idee:** Das Foto besteht aus drei senkrechten Bahnen, die beim Scrollen verschieden hoch aufsteigen und sich zu
  einem Bild schließen. Titel schwarz auf Weiß unter dem Bild, Dachzeile in Impact.
- **Unterschied:** Kein Verlauf und kein Text im Bild; das Bild selbst ist die Bewegung. Kein Kartenraster, keine
  Schräglage, kein Stempel (Runde 4), keine runden Formen (Runde 2 und 3).
- **Offene Fragen an Luis:** Der Aufmacher steht ganz oben, dort gibt es keinen Scrollweg. Soll die Bewegung dann beim
  Laden spielen (wie A), oder gehört die Idee eher an die großen Kacheln weiter unten? Ist ein Titel unter statt im
  Bild für den Aufmacher gewollt?

## Idee C: Bühne mit drei Geschichten

- **Idee:** Ein Bildplatz, daneben (am Handy darunter) drei Zeilen. Antippen zieht das Bild der gewählten Geschichte
  wie einen Vorhang von unten über die Bühne (800 ms, Kurve „vorhang“ aus Bewegung D), der Titel im Bild wechselt mit.
- **Unterschied:** Kein Karussell, das von selbst läuft, keine Punkte-Navigation, keine Pillen (Runde 3). Bewegung nur
  als Antwort auf eine Handlung. Der erste Bildschirm zeigt drei Geschichten statt einer (Runde 4: „Cover mit nur
  einer Geschichte“).
- **Offene Fragen an Luis:** Wer wählt die drei Geschichten (die drei neuesten oder von der Redaktion gesetzt)? Reicht
  „etwas zum Anfassen“ als Explosion, oder ist das zu still? Am Handy auch Wischen auf dem Bild?

## Idee D: Farbbühne

- **Idee:** Der Aufmacher steht auf einer Fläche in der Sonderfarbe. Das Foto ragt über deren Kante hinaus, der Titel
  steht auf der Farbe. Beim Scrollen wächst die Fläche, das Foto fährt an seinen Platz. Die drei Farbvorschläge lassen
  sich an der Probe umschalten.
- **Unterschied:** Die Fläche ist keine Markenfarbe über dem Bild, sondern eine ruhige vierte Farbe dahinter. Kein Rot
  als Fläche, kein Creme oder Sand (Runde 2), kein Nachtblau mit Gold (Runde 1), keine rosa Hinterlegung (Runde 3).
- **Offene Fragen an Luis:** Soll die Sonderfarbe wirklich bis in den Aufmacher, oder nur in Abschnitte weiter unten?
  `DESIGN.md` sagt bisher „keine weiteren Markenfarben“; das müsste dann geändert werden. Ist das kleinere Foto in
  Ordnung?

## Sonderfarben

Kontrast nach WCAG 2.x (relative Leuchtdichte), gerechnet per Skript aus den Hex-Werten. OKLCH aus denselben Werten.

| Name | Hex | OKLCH | Schwarz | Titan #660000 | Impact #B30000 | Weiß | Leise #555 | Hell-leise #CCC |
|---|---|---|---|---|---|---|---|---|
| Lagune | `#D3EBE7` | `oklch(0.921 0.026 185)` | 16,81 | 10,74 | 5,76 | 1,25 | 5,97 | 1,29 |
| Pfau | `#0C4A50` | `oklch(0.375 0.059 205)` | 2,11 | 1,35 | 1,38 | 9,95 | 1,33 | 6,19 |
| Blatt | `#DDEBCF` | `oklch(0.922 0.040 129)` | 16,86 | 10,77 | 5,78 | 1,25 | 5,99 | 1,29 |

- **Lagune und Blatt** tragen schwarze, titanfarbene und impactrote Schrift (alle über 4,5 : 1). Sie taugen als
  Abschnittsgrund anstelle des neutralen Grau.
- **Pfau** trägt nur Weiß und Hell-leise. Titan und Impact sind darauf weder als Schrift noch als Linie zu sehen
  (unter 1,4 : 1); Pfau und Titan dürfen nie aneinanderstoßen. Pfau wäre eine dritte dunkle Fläche neben Rubrikband
  und „Diese Woche“, also höchstens für einen Abschnitt.
- Alle drei liegen auf der kühlen, grünen Seite, gegenüber von Rot. Gelb, Gold, Creme, Sand, Rosa und Nachtblau sind
  durch die abgelehnten Runden gesperrt und deshalb nicht dabei. Lagune und Blatt sind sich in der Helligkeit sehr
  ähnlich; sie unterscheiden sich nur im Farbton (blaugrün gegen gelbgrün).
- Anwendung auf der Seite: je ein Abschnitt „Kino“ mit drei echten Titeln auf der Farbe, dazu Idee D.

## Text im Bild

Die Schrift im Bild (A, C) steht auf dem Verlauf aus `tokens.css` und beginnt erst unterhalb von 52 px, wo er
mindestens 72 % Schwarz hat. Schlechtester Fall, weißes Foto darunter: Weiß auf rund `#474747`, gerechnet 9,2 : 1.
Das ist gerechnet, nicht am Bildschirmfoto gemessen.

## Prüfung

`node tools/shots.mjs design/richtungen/klar2/aufmacher-neu/index.html design/richtungen/klar2/aufmacher-neu/artifact.html`
bei 390, 820 und 1280: 6 Aufnahmen, 0 Fehler. Je Aufnahme: kein seitliches Scrollen, keine Konsolenfehler, alle Bilder
und Schriften geladen, keine Tippfläche unter 44 px, kein Tamil ohne `lang`.

Zusätzlich je Probe ein Ausschnitt nach dem Scrollen bei 390 und 1280 angesehen (eigenes Playwright-Skript). Dabei
gefunden und behoben: Die Bahnen in B standen still, weil `overflow: hidden` sie zum Scrollbehälter für `view()`
machte; jetzt `overflow: clip`.

Nicht geprüft: echte Geräte, Safari und Firefox (dort fehlt `animation-timeline` teils, dann steht der fertige
Zustand), der Bewegungsablauf selbst als Video, die Artifact-Fassung auf claude.ai, `sloplint` und eine Kritik aus
frischem Kontext.
