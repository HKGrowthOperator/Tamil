# Design – Tamil.de: „klar2“ mit Bewegung D

> **Stand 16.11.2026:** Richtung `klar2` und Bewegung D gewählt von Luis (`docs/abnahme/2026-11-16-G2-klar2.md`,
> `docs/entscheidungen.md`). Eine Probeseite und Tor G3 entfallen; das Theme `wordpress/themes/tamil` (Version 3.0)
> wird direkt umgebaut und auf dem Testsystem mit echten Beiträgen abgenommen. Quellen: `design/richtungen/klar2/`
> (Startseite, Artikel, CSS), `design/richtungen/klar2/bewegung/` (Variante D), Regeln in `design/brief.md` §10.
> Tokens: `design/tokens.css`.

**Idee:** eine ruhige Nachrichtenseite mit mehr Bild und mehr Bühne. Vorbild BBC News für Kopf und Ordnung,
tagesschau für den Titel im Bild, Spiegel für die Bildblöcke. Das Wow kommt aus Fotos, Fläche und dem Wechsel von
Hell und Dunkel, nicht aus Schriftgröße, Rot oder Effekten.

## Farben

oklch im CSS (`theme.css`, `design/tokens.css`), Hex nur als Rückfall in `theme.json`.

| Token | oklch | Hex | Rolle |
|---|---|---|---|
| `grund` | 0.985 0.002 250 | `#F9FAFB` | Seitengrund; Schrift auf Dunkel („hell“) |
| `flaeche` | 0.962 0.003 250 | `#F1F3F4` | Bildgrund beim Laden, Hinweise, Meldungen der Formulare |
| `tinte` | 0.21 0.012 255 | `#15191E` | Text, Linien über Blöcken, „Diese Woche“ |
| `leise` | 0.45 0.012 255 | `#51565C` | Datum, Orte, Nachweise, Beschriftungen |
| `linie` | 0.88 0.004 250 | `#D5D8DA` | Trennlinien zwischen Zeilen |
| `rot` | 0.508 0.177 25.6 | `#B5282A` | Fläche des Rubrikbands (seit 17.11.); sonst nur Akzent: Rubrik in der Dachzeile, Fehler |
| `rot-hell` | 0.55 0.175 25.6 | `#C33937` | Rubrikband beim Überfahren und bei offenem „Mehr“ (weiß darauf 5,1 : 1) |
| `rot-linie` | 0.62 0.15 25.6 | `#D15C55` | feine Trennlinie im Rubrikband |
| `rot-dunkel` | 0.42 0.15 25.6 | `#8D1A1D` | Spur unter der hellen Leselinie (Bewegung D) |
| `hell-leise` | 0.82 0.006 250 | `#C1C4C8` | Nebeninfos auf Dunkel |
| `linie-dunkel` | 0.36 0.010 255 | `#3A3D42` | Linien auf Dunkel |
| `flaeche-dunkel` | 0.26 0.012 255 | `#20242A` | gestaltete Kacheln ohne Foto (Kino, Termine) |

Das Rubrikband ist rot mit weißer Schrift (Luis, 17.11.2026; weiß auf Rot 6,1 : 1). Damit bleibt genau eine
dunkle Fläche je Seite: „Diese Woche“ (auf Kino und Termine „Im Programm“ bzw. „Ab heute“). Der einzige Verlauf
liegt unter Schrift im Bild (durchsichtig nach Tinte). Radius 0, keine Schatten, nichts gedreht. Rot als Fläche nur im
Band, als Schrift nie über 20 px; auf Dunkel ist die Dachzeile hell.

## Schrift

Eine Familie: **Libre Franklin** (variabel 100–900, OFL, selbst gehostet, nur der lateinische Teil wird vorgeladen).
Tamil fällt über `unicode-range` und `:lang(ta)` auf die Tamil-Untermenge von **Catamaran**.

| Rolle | Größe Handy / Desktop | Gewicht |
|---|---|---|
| Aufmacher (Titel im Bild) | 30 / 34 (Tablet) / 40 px | 650 |
| Artikeltitel | 28 / 38 px | 650 |
| Seitenkopf | 28 / 34 px | 700 |
| Titel große Kachel | 22 / 26 px | 650 |
| Nebenstück, Blocktitel | 19 / 20 px | 650 / 700 |
| Meldung, Listenzeile | 17 / 19 px | 600 |
| Fließtext im Artikel | 18 / 19 px, Zeilenhöhe 1,6 | 400 |
| Text sonst | 17 px | 400 |
| Dachzeile „Rubrik \| Datum“, Nachweise | 13 px | 600 / 400 |

Keine Versalien, keine Kursive. Der Artikel steht in einer Spalte von höchstens 560 px (am Tablet 600 px mit
gemeinsamer Kante für Kopf, Bild und Text), höchstens 70 Zeichen je Zeile.

## Bausteine

- **Kopf:** Kopfzeile (Datum, ab 800 px „Diese Woche“ mit nächstem Termin und Film, Suche), Logo 44/52/58 px auf
  hellem Grund, rotes Rubrikband mit weißer Schrift (`nav`, 46/48 px, steht beim Scrollen), aktive Rubrik mit
  Gewicht 600 und 3 px Weiß darunter, beim Überfahren etwas hellerer Grund, Fokusring weiß, am Handy seitlich mit
  Einrasten; „Mehr“ am Ende mit Suche, Diensten und Social.
- **Anreißer:** ein Link um Bild und Text; Dachzeile „Rubrik | Datum“; Bild füllt seinen Rahmen. Formate: 4:3
  (Aufmacher, große Kachel in „Diese Woche“), 16:9 (Nebenstücke, Meldungen, Rubrikkacheln, Küche groß), 8:3 (kleine
  Kacheln). Beim Überfahren Zoom 1,03 in 0,35 s, Titel unterstrichen.
- **Bild mit Titel im Bild:** Aufmacher und große Kacheln; Fokus als Rahmen nach innen.
- **Rubrikkacheln:** Navigation mit Bild (Foto des neuesten Beitrags der Rubrik, sonst Rubrikfoto), Name im Bild.
- **Gestaltete Kacheln** (`data-grafik`, Fläche auf Dunkel): Kino (Film, Zahl der Kinos, Städte) und Termine
  (Titel, Datum als größte Angabe, Ort, Vorspann); leer sagen sie, wo es weitergeht.
- **Blocktitel:** 19 px, Linie in Tinte darüber; Listen mit Linien statt Kästen; Tabellen ebenso.
- **Knöpfe** nur für Formulare und Bedienung: Tinte, eckig, 48 px hoch. Sonst unterstrichene Textlinks, 44 px tippbar.
- **Anzeigen:** Label „Anzeige“, feste Formate aus dem Plugin; Eigenanzeige wie ein Anreißer mit Linien.
- **Fuß:** heller Grund mit Linie in Tinte; Logo und Unterzeile, Rubriken, Dienste, Social (nur mit Adresse),
  Bildnachweise der Seite, Rechtliches mit Platz für „Cookie-Einstellungen“.

## Seiten

- **Startseite:** Aufmacher 4:3 (am Desktop daneben „Weitere Meldungen“), vier Nebenstücke, Rubrikkacheln,
  Werbeplatz 01, „Diese Woche“ (Kino groß und klein, „Im Kino“, „Termine“), „Küche“ (groß 16:9, klein 8:3 auf einer
  Kante), Billboard, Rubrikblöcke mit je vier Nebenstücken.
- **Artikel:** Dachzeile, Titel, Vorspann, Leiste mit Lesezeit und „Per WhatsApp teilen“, Bild (randlos am Handy) mit
  Nachweis, Text, Termin als Angaben, Quelle, Schlagworte, Teilen, Redaktion; Werbeplatz 02 rechts ab 1024 px;
  „Weiterlesen“ mit vier Nebenstücken.
- **Rubrik:** Seitenkopf, Aufmacher mit „Neu in der Rubrik“ daneben, Liste mit Bild und Vorspann, Seiten, Kacheln.
- **Kino / Termine:** Seitenkopf, dunkler Bereich „Im Programm“ bzw. „Ab heute“, dann „Nach Stadt“ (Tabelle) bzw.
  „Das Jahr“ (Monate zum Aufklappen).
- **Kontakt, Suche, 404, Seiten, Archive:** Seitenkopf, Blöcke mit Blocktitel, Listen mit Bild; Seiten in der
  Artikelspalte, Plugin-Inhalte bis 720 px.

## Bewegung D

Nur unter `prefers-reduced-motion: no-preference`, nur `transform` (als `translate`/`scale`), `opacity` und
`clip-path`; ohne Skript und mit „Bewegung reduzieren“ ist alles sichtbar und still. Der erste Bildschirm bewegt sich
nie von selbst; was einmal erschienen ist, bleibt.

| Teil | Bewegung | Dauer |
|---|---|---|
| Kopf | Kopfzeile verblasst, Logo wird 0,8 und schiebt sich unter das Band (am Scrollweg) | Weg = Kopfhöhe |
| Band | helle Leselinie 2 px auf dem roten Band wächst mit dem Lesefortschritt | ganze Seite |
| Aufmacherbild | bis 40 px langsamer als die Seite | beim Hinausscrollen |
| „Diese Woche“ | dunkle Fläche zieht von links auf, danach steigt der Inhalt | 800 ms, Inhalt ab 55 % |
| Große Kacheln | Bild deckt sich von unten auf, Maßstab 1,06 → 1, Titel zeilenweise | 750 / 1100 / 700 ms |
| Blocktitel | steigen aus ihrer Linie | 700 ms |
| Kacheln, Nebenstücke, Meldungen, Listen | 16 px nach oben, einblenden, gestaffelt 60 ms je Spalte, 100 ms je Reihe | 560 ms |

Am Scrollweg per CSS-Scroll-Timeline (`@supports (animation-timeline: scroll())`), sonst ein passiver Scroll-Handler
mit `requestAnimationFrame`. Auftritte über IntersectionObserver (Auslöser 10 % über der Unterkante). Code:
`assets/js/app.js` (Abschnitt „Bewegung“) und `theme.css` (Abschnitt „Bewegung beim Scrollen“).

## Raster

Inhalt höchstens 1280 px, Rand 16 / 24 / 40 px (ab 600 / 1024 px). Desktop-Startseite: Aufmacher und 388 px
Meldungen mit 32 px Abstand; „Diese Woche“ dreispaltig. Brüche bei 600, 800 (Hinweise im Kopf) und 1024 px.
