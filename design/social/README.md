# Social-Karten tamil.de – Spezifikation

> **Vorschlag, nicht freigegeben.** Das Signet „Tamil Dots 04A“ ist ein Entwurf (Abgleich mit der Originalreferenz
> Feld A steht aus, `design/signature/README.md`). Keine Einbindung in die Social-Automatik, bevor Luis zustimmt.
> Alle Bilder in `muster/` sind als **MUSTER** gekennzeichnet. Sie zeigen einen echten Beitrag des Testsystems mit
> echtem Foto und Nachweis, sind aber keine Veröffentlichung.

Ein Kartensystem für Instagram, Facebook und WhatsApp im Stil der Bild.de-Posts (Wunsch von Luis, 17.11.):
- ein großes Foto,
- oben links das Logo tamil.de,
- darunter die Überschrift auf Titan Red,
- das Signet Tamil Dots als Markenelement in der Fläche.

## Dateien

| Pfad | Inhalt |
|---|---|
| `vorlagen/karte.html` | eine Vorlage für alle Formate: `?format=feed\|karussell\|story\|facebook\|whatsapp`, `&folie=1..n`, `&muster=1` (Kennzeichnung), `&hilfe=1` (sichere Zonen) |
| `vorlagen/karten.css` | Maße, Schrift, Farben |
| `vorlagen/daten-muster.js` | Mustereintrag (`window.KARTE`), echter Beitrag 2716 vom Testsystem |
| `vorlagen/muster-rendern.mjs` | rendert alle Muster nach `muster/` (Playwright, Chromium) |
| `bilder/deepavali-2026-ganesha-tempel-berlin.jpg` | Beitragsbild 1200 × 675 vom Testsystem (REST `/wp/v2/media/2717`) |
| `schriften/` | Libre Franklin (variabel, latin + latin-ext), OFL |
| `muster/*.jpg` | gerenderte Muster; `*-zonen.jpg` mit eingezeichneten sicheren Zonen |

Logo: `design/inhalte/logo.png`, das neue Logo von Luis (20.11.2026), aus `design/inhalte/logo-2026-11.webp`
freigestellt (`design/inhalte/logo_freistellen.py`, durchsichtiger Grund, Farben unverändert). Signet: `design/signature/vorschlaege/master-impact-auf-titan.svg`
(auf Titan), `…/master-hell.svg` (weiße Folien), `design/signature/master.svg` (Schlussfolie).

```bash
node design/social/vorlagen/muster-rendern.mjs           # alle Formate -> muster/*.jpg
node design/social/vorlagen/muster-rendern.mjs --hilfe   # Feed, Story, Facebook mit Zonen
```

**Automatik (später, Nick):** Seite `karte.html?format=…` in Zielgröße öffnen (`deviceScaleFactor: 1`). Vorher
`window.KARTE` per `page.addInitScript` setzen und `muster` weglassen. Auf `document.fonts.ready` und die Bilder
warten, dann das Element `.karte` fotografieren. Alternativ dieselben Maße in `news_radar/social/bild.py` (Pillow)
nachbauen. Abweichungen nur mit Luis.

## Daten je Karte (`window.KARTE`)

| Feld | Pflicht | Quelle |
|---|---|---|
| `rubrik` | ja | Kategorie des Beitrags (z. B. „Events“) |
| `titel` | ja | Beitragstitel, unverändert |
| `kurztitel` | nein | für Story und Facebook, höchstens 60 Zeichen; sonst `titel` |
| `bild`, `bild_alt` | ja | Beitragsbild, mindestens 1200 px breit; Alternativtext |
| `nachweis` | ja | Bildnachweis wie auf der Website (Meta `bild_credit`), z. B. „Foto: 18quirl08 / Wikimedia Commons, CC BY-SA 4.0“ |
| `fokus` | nein | Bildausschnitt als `object-position`, Vorgabe „50% 45%“; bei Personen auf Gesichter setzen |
| `link_text` | ja | „tamil.de“ |
| `folien[]` | nur Karussell | Kernaussagen aus dem Text: `{titel, text[]}` oder `{titel, liste[[Ort, Zeile]]}`. Nur belegte Aussagen aus dem Beitrag, nichts erfinden |

Ohne Foto mit Social-Recht (Regel R4, Lizenzumfang `social`) wird keine Fotokarte gebaut. Dann gilt die Bildkarte.

## Formate

| Format | Größe | Foto | Überschrift | Signet (Quelle, Lage) |
|---|---|---|---|---|
| Instagram Feed (Einzelbild) | 1080 × 1350 | oben, 1080 × 760 | 74 px, 3 Zeilen | Impact auf Titan, links 448, oben 1086, Breite 840, rechts und unten angeschnitten |
| Instagram Karussell Titel | 1080 × 1350 | wie Feed | 74 px | wie Feed; Fußzeile „1/4  Wischen für mehr“ |
| Karussell Inhalt | 1080 × 1350 | keins, Grund Weiß | Folientitel 66 px Titan, Text 42 px Schwarz, Liste 40 px | hell auf Weiß, links 470, oben 1040, Breite 860 |
| Karussell Schluss | 1080 × 1350 | keins, Weiß | „Den ganzen Beitrag lest ihr auf tamil.de“ 66 px, „Link in der Bio“ | Master groß, links 60, oben 640, Breite 960 |
| Instagram/Facebook Story | 1080 × 1920 | Mitte, 1080 × 720 ab y 420 | 78 px | Impact auf Titan oben rechts, links 330, oben −96, Breite 900 (im oberen Randbereich, rein schmückend) |
| Facebook Link-Post | 1200 × 630 | rechts, 720 × 630 | 40 px, Feld links 480 breit | Impact auf Titan, unten links angeschnitten (links −150, oben 452, Breite 560) |
| WhatsApp-Kanal | 1080 × 1080 | oben, 1080 × 590 | 64 px | Impact auf Titan, links 560, oben 880, Breite 680 |

Alle Maße in Bildpunkten der Zielgröße. Rand links und rechts: 56 px (Feed, Karussell, WhatsApp), 64 px (Story),
40 px (Facebook).

## Sichere Zonen

- **Feed und Karussell:** Logo, Überschrift und Nachweis innerhalb x 45–1035. Das Profilraster schneidet auf 3 : 4.
- **Story:** oben 250 px und unten 250 px frei von Inhalt; dort liegen Kopfzeile und Antwortfeld von Instagram. Das
  Signet darf oben in den Randbereich ragen, weil es nur schmückt. Platz für den Link-Sticker: y 1572–1664, links.
- **Facebook:** das ganze Bild ist sichtbar (1,91 : 1). Text bleibt im linken Feld.
- **WhatsApp:** quadratisch, nichts ragt über die Ränder; Logo und Text mindestens 56 px vom Rand.

## Typografie

- Schrift: Libre Franklin (aus `schriften/`), Überschrift Gewicht 760, Zeilenhöhe 1,07, Laufweite −0,012 em,
  `text-wrap: balance`. Keine Versalien in Überschriften.
- Dachzeile (Rubrik): 28 px (Feed), 26 px (WhatsApp), 30 px (Story), 22 px (Facebook), Gewicht 600, 90 % Weiß, davor ein
  Impact-Strich 56 × 8 px.
- Nachweis: 20 px, Gewicht 450, Weiß 92 %, rechts unten im Foto auf dem einzigen Verlauf (Schwarz 0 → 55 %, 120 px).
- Fußzeile: 24 px, „tamil.de“ fett, daneben der Hinweis („Link in der Bio“, „Mehr auf tamil.de“).
- Überschrift: höchstens 3 Zeilen (Feed 74 px, WhatsApp 64 px), Story 78 px bis 3 Zeilen, Facebook 40 px bis 4 Zeilen.
  Bei längeren Titeln eine Stufe kleiner (Feed 66 px, Story 70 px), nie kürzen oder umschreiben. Die Vorlage meldet
  Überlauf beim Rendern als Fehler.

## Farben

- Titan Red `#660000` trägt die Textfelder (dominant, ~35 %), Impact Red `#B30000` ist Akzent (Dachzeilen-Strich,
  Punkte, ~10 %), Weiß für Schrift auf Titan und die Inhaltsfolien (~50 %), Schwarz nur für Fließtext auf Weiß (~5 %).
- Kontrast: Weiß auf Titan 13 : 1, Weiß auf Impact 7 : 1. Text liegt nie auf Impact-Punkten, die schlechter lesbar
  machen würden.

## Signet: Regeln für die Platzierung

- Das Signet sitzt im Textfeld oder auf der weißen Folie, **nie auf dem Foto** und nie über Gesichtern.
- Es läuft von unten oder von der Seite in die Karte und wird von der Kante angeschnitten. Der große linke Fuß oder
  der obere Bogen bleibt sichtbar.
- Abstand zur Überschrift: die letzte Zeile endet über dem Bogen. Wird ein Titel länger, rutscht das Signet nicht
  nach oben; dann gilt die kleinere Schriftstufe.
- Das Logo steht immer getrennt vom Signet: oben links auf eigener weißer Platte.

## Logo

- Seit 20.11.2026 das neue Logo (Luis: „genau so übernehmen“): „tamil“ in Rot, „.de“ in Dunkelgrau, darunter
  „portal • lifestyle • entertainment“ und „& KOMMUNITYPLATTFORM DER COMMUNITY“ – Schreibweise wie geliefert.
  Datei: `design/inhalte/logo.png` (1920 × 695, freigestellt, ohne Rand). Kein Neuzeichnen, kein Vektor-Nachbau.
- Eine weiße Fassung liegt nicht vor. Darum steht das Logo auf einer weißen Platte (Innenabstand 16 / 20 / 14 px,
  Logo 216 px breit, Facebook 168 px). Die Muster in `muster/` sind mit dem neuen Logo neu gerendert.
- Luis wünscht „tamil.de in weißer Schrift“. Das geht erst mit einer weißen Logofassung von KBS (offener Punkt).

## Einzelbild oder Karussell

| Beitrag | Instagram | Facebook | WhatsApp |
|---|---|---|---|
| kurz (unter ~2 500 Zeichen oder Meldung) | Einzelbild (Feed) | Link-Post 1200 × 630 | Kanalbild 1080 × 1080 + Text mit Link |
| lang (ab ~2 500 Zeichen, mehrere Abschnitte) | Karussell: Titel + 2–3 Inhaltsfolien + Schluss (4–5 Folien) | Link-Post | Kanalbild |
| Termin oder Kino mit mehreren Orten | Karussell mit Listenfolie (Ort + Zeile) | Link-Post | Kanalbild |

- Je Inhaltsfolie eine Aussage: höchstens 2 kurze Absätze oder 3–4 Listenzeilen.
- Die Story ist optional: dieselbe Überschrift und dasselbe Foto, dazu der Link-Sticker.
- **Achtung Regelwerk:** In der Fassung 1 von `docs/regeln-social.md` gehen Storys und Karussells nie automatisch
  hinaus. Für die Automatik braucht es eine neue Fassung und die Freigabe durch KBS. Bis dahin gelten sie als Entwurf
  im Cockpit.

## Was sich je Format ändert

- **Feed und Karussell-Titel:** Foto oben, Titan-Feld unten. Beim Karussell steht in der Fußzeile die Folienzahl.
- **Inhaltsfolien:** weißer Grund mit Logo ohne Platte, Folienzahl oben rechts, Titan-Titel, schwarzer Text, leises Signet.
- **Schluss:** Master-Signet in Originalfarben groß auf Weiß, Verweis auf den Link.
- **Story:** Titan-Grund; Signet oben im Randbereich; Logo unter der oberen Zone; Foto in der Mitte.
- **Facebook:** quer, Text links, Foto rechts, Logo im Textfeld.
- **WhatsApp:** wie Feed, nur quadratisch und mit kürzerem Foto.

## Muster

`muster/` enthält gerenderte Muster als JPG, alle mit der Aufschrift „MUSTER · Vorschlag, nicht freigegeben“:
- Instagram Feed, Karussell (Folien 1–4), Story, Facebook Link-Post, WhatsApp-Kanal.
- Feed, Story und Facebook zusätzlich mit eingezeichneten Zonen.

Inhalt: Beitrag „Deepavali 2026: Lichterfest in Berlin, Bayern und Düsseldorf“ (Testsystem, Beitrag 2716). Die
Folientexte stammen wörtlich oder sinngleich aus dem Beitrag.
