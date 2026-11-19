# Design – Tamil.de: „klar2“ mit Bewegung D

> **Stand 16.11.2026:** Richtung `klar2` und Bewegung D gewählt von Luis (`docs/abnahme/2026-11-16-G2-klar2.md`,
> `docs/entscheidungen.md`). Eine Probeseite und Tor G3 entfallen; das Theme `wordpress/themes/tamil` (Version 3.0)
> wird direkt umgebaut und auf dem Testsystem mit echten Beiträgen abgenommen. Quellen: `design/richtungen/klar2/`
> (Startseite, Artikel, CSS), `design/richtungen/klar2/bewegung/` (Variante D), Regeln in `design/brief.md` §10.
> Tokens: `design/tokens.css`.
>
> **Stand 19.11.2026 (Theme 3.4.0):** Markenfarben von Luis (`docs/abnahme/2026-11-19-signature.md`, Branding Master
> Handoff v1.1): Weiß, Titan Red dominant, Impact Red als Akzent, Schwarz für Schrift, Gewichtung „Red Dominance /
> Power“. Sie ersetzen die Farbwerte von klar2 und die Regel „Rot nur als Akzent“. Das Signet „Tamil Dots 04A“ folgt
> nach Vektordatei und Anleitung von Luis; das Logo bleibt unverändert.

**Idee:** eine ruhige Nachrichtenseite mit mehr Bild und mehr Bühne. Vorbild BBC News für Kopf und Ordnung,
tagesschau für den Titel im Bild, Spiegel für die Bildblöcke. Das Wow kommt aus Fotos, Fläche und dem Wechsel von
Weiß und Titan Red, nicht aus Schriftgröße oder Effekten.

## Farben

Markenfarben von Luis (19.11.2026). Richtwert der Gewichtung: **50 % Weiß, 35 % Titan Red, 10 % Impact Red, 5 %
Schwarz**. Die vier Markenwerte stehen als Hex im CSS, damit sie exakt so erscheinen (oklch nur im Kommentar). Keine
weiteren Markenfarben (kein Orange, Pink, Gold, Violett); Grauwerte und die Fehlerfarbe sind neutral bzw. semantisch
benannt. Quelle: `theme.css` (Abschnitt Tokens), `design/tokens.css`; `theme.json` trägt dieselben Hex-Werte.

| Token | Wert | Rolle |
|---|---|---|
| `--tamil-color-background` (`grund`, `weiss`) | `#FFFFFF` | Seitengrund |
| `--tamil-color-primary` (`titan`) | `#660000` | **dominant:** Rubrikband, „Diese Woche“, Kino „Im Programm“, Termine „Ab heute“, Knöpfe, aktive Filter und Seitenzahl, Linien über Blöcken (`linie-stark`), Fokusrahmen (`fokus`), Fuß (Linie oben, Zeile mit Rechtlichem), Schild „Symbolbild“, Icon und Browserleiste |
| `--tamil-color-accent` (`rot`) | `#B30000` | **Akzent:** Rubrik in der Dachzeile, Top-News, Schild „Neu“, Links im Text, Leselinie, Markierung der aktiven Rubrik, Überfahren im Band und an Knöpfen, Linie unter Titeln auf Titan (`linie-titan`) |
| `--tamil-color-text` (`tinte`) | `#000000` | Fließtext und Überschriften auf Weiß |
| `titan-tief` | `#520000` | Ableitung (Titan mit 20 % Schwarz): Bildkacheln auf Titan |
| `neutral-flaeche` (`flaeche`) | `#F2F2F2` | Bildgrund beim Laden, Hinweise, Meldungen der Formulare |
| `neutral-linie` (`linie`) | `#D9D9D9` | Trennlinien zwischen Zeilen |
| `neutral-leise` (`leise`) | `#555555` | Datum, Orte, Nachweise, Beschriftungen, „Anzeige“ |
| `neutral-hell-leise` (`hell-leise`) | `#CCCCCC` | Nebeninfos auf Titan und im Bild |
| `status-fehler` | = Impact | Formularfehler (Text, Rand) |
| `--signatur-*` | – | Platz für das Signet „Tamil Dots 04A“, kommt nach Freigabe |

Kontraste (WCAG 2.2 AA): Weiß auf Titan 13,4 : 1, Weiß auf Impact 7,2 : 1, Impact auf Weiß 7,2 : 1, Titan auf Weiß
13,4 : 1, `#555` auf Weiß 7,5 : 1, `#CCC` auf Titan 8,4 : 1. Die aktive Rubrik ist in Impact markiert und trägt 3 px
Weiß darunter, weil Impact gegen Titan nur 1,9 : 1 hat; der Zustand hängt so nicht am Rotton. Der einzige Verlauf liegt
unter Schrift im Bild: durchsichtig nach Schwarz, auf Titan-Flächen nach Titan. Radius 0, keine Schatten, nichts
gedreht. Rot als Schrift nie über 20 px; im Bild und auf Titan ist die Dachzeile weiß. Anzeigen bleiben neutral
(Schwarz), damit sie sich vom redaktionellen Teil abheben.

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

- **Kopf:** Kopfzeile (Datum, Top-News: Schild „Neu“ in Impact, die Überschriften der neuesten Beiträge in Impact, ab 1024 px zwei mit
  feiner Linie, darunter einer, einzeilig mit Auslassung, am Handy ohne Datum; Suche), Logo 44/52/58 px auf
  weißem Grund, Rubrikband in Titan mit weißer Schrift (`nav`, 46/48 px, steht beim Scrollen), aktive Rubrik in
  Impact mit Gewicht 600 und 3 px Weiß darunter, beim Überfahren Impact, Fokusring weiß, am Handy seitlich mit
  Einrasten; „Mehr“ am Ende mit Suche, Diensten und Social.
- **Anreißer:** ein Link um Bild und Text; Dachzeile „Rubrik | Datum“; Bild füllt seinen Rahmen. Formate: 4:3
  (Aufmacher, große Kachel in „Diese Woche“), 16:9 (Nebenstücke, Meldungen, Rubrikkacheln, Küche groß), 8:3 (kleine
  Kacheln). Beim Überfahren Zoom 1,03 in 0,35 s, Titel unterstrichen.
- **Bilderpflicht** (Luis, 17.11.): Jeder Anreißer, jede Listenzeile, Kachel, jedes Suchergebnis, „Weiterlesen“ und
  jeder Kino- und Termineintrag zeigt ein echtes Bild; nichts nur als Text. Ausgenommen sind Rubrikband, Top-News im
  Kopf, Fußlisten, Formulare und reine Textseiten. Bildkette an einer Stelle (`inc/bildkette.php`): eigenes Foto (Titelkarten nie;
  Bänder über 2,5:1 werden beschnitten, Nachweis „zugeschnitten“) → erstes Bild aus dem Text ab 600 px → bei Kino und
  Terminen das Foto eines anderen Beitrags zum selben Film bzw. zur selben Veranstaltung (ohne Schild) → Symbolbild
  aus dem Rubrik-Pool (Commons; je Seite reihum vergeben, damit kein Ersatzbild auf einer Seite doppelt erscheint;
  Kino und Events mit eigenen Pools, nie Kirchen oder Rathäuser für Kino und Entertainment; Schild „Symbolbild“
  oben rechts ab 150 px Rahmenbreite, darunter ein „S“; „Symbolbild,“ vor dem Nachweis). Nachweise entstehen an
  einer Stelle (`tamil_nachweis_bauen()`): Urheber verlinkt auf die Dateiseite, Lizenz auf den Lizenztext,
  „zugeschnitten“ bei freien Lizenzen und Bändern. Prüfung: `node wordpress/dev/bilder_pflicht.mjs`.
- **Bild mit Titel im Bild:** Aufmacher und große Kacheln; das Format ist nur Mindesthöhe, längere Titel machen die
  Kachel höher statt abzuschneiden; Fokus als Rahmen nach innen.
- **Rubrikkacheln:** Navigation mit Bild (Foto des neuesten Beitrags der Rubrik, sonst das erste Bild ihres Pools),
  Name im Bild.
- **Bildkacheln auf Titan** (`data-grafik`, Grund `titan-tief`): Kino mit Bild 4:3 links (Film, Zahl der Kinos, Städte) und Termine mit
  Bild 16:9 oben (Titel, Datum mit Uhrzeit und Ende als größte Angabe, Ort, Veranstalter, Eintritt, Vorspann); leer
  zeigen sie ein Symbolbild und sagen, wo es weitergeht.
- **Blocktitel:** 19 px, schwarz, 2 px Linie in Titan darüber; Listen mit Linien statt Kästen; Tabellen ebenso
  (Kopflinien in Titan, Zeilenlinien neutral).
- **Knöpfe** nur für Formulare und Bedienung: Titan mit weißer Schrift, beim Überfahren Impact, eckig, 48 px hoch. Sonst unterstrichene Textlinks, 44 px tippbar.
- **Anzeigen:** Label „Anzeige“, je Platz ein benannter Bereich des Plugins; Formate aus
  `tamil_site_werbung_formate()`, dieselbe Fläche für Eigenanzeige (Bildbanner), gebuchte Anzeige und Banner-Code.
  Handy-Leiste 320 × 50 fest unten, erst wenn der erste Abschnitt aus dem Bild ist (spätestens nach einem
  Bildschirm), schließbar, nur unter 768 px Breite und ab 500 px Fensterhöhe.
- **Fuß:** weißer Grund mit 3 px Linie in Titan oben, die Zeile mit Rechtlichem als Band in Titan über die volle Breite; Logo und Unterzeile, Rubriken, Dienste, Social (nur mit Adresse),
  Bildnachweise der Seite, Rechtliches mit Platz für „Cookie-Einstellungen“.

## Seiten

- **Startseite:** Aufmacher 4:3 (am Desktop daneben „Weitere Meldungen“), vier Nebenstücke, Rubrikkacheln,
  Werbeplatz 01, „Diese Woche“ (Kino groß und klein, „Im Kino“, „Termine“), „Küche“ (groß 16:9, klein 8:3 auf einer
  Kante; unter 1024 px Titel unter dem Bild, am Tablet die große Kachel oben), Billboard, Rubrikblöcke mit je vier Nebenstücken. „Diese Woche“ zeigt nur Aktuelles: Filme mit Spieltagen
  ab heute, Kino-Beiträge der letzten 30 Tage, Termine der nächsten 14 Tage (sonst die nächsten drei); was dort
  steht, kommt oben nicht noch einmal.
- **Artikel:** Dachzeile, Titel, Vorspann, Leiste mit Lesezeit und „Per WhatsApp teilen“, Bild (randlos am Handy) mit
  Nachweis, Text, Termin als Angaben, Quelle, Schlagworte, Teilen, Redaktion; Textspalte mittig wie im Entwurf; Werbeplatz 02 ab 1280 px rechts daneben, darunter nach dem Bild;
  „Weiterlesen“ mit vier Nebenstücken.
- **Rubrik:** Seitenkopf, Aufmacher mit „Neu in der Rubrik“ daneben, Liste mit Bild und Vorspann, Seiten, Kacheln.
- **Kino:** Seitenkopf, Bereich „Im Programm“ in Titan, „Nach Stadt“ (Tabelle, jede Zeile mit dem Bild des Films),
  „Aus dem Kinojahr“ (Liste mit Bild).
- **Termine:** Seitenkopf, Bereich „Ab heute“ in Titan (Termine der nächsten 14 Tage, sonst die nächsten drei),
  „Kommende Termine“ nach Monaten (Zeilen mit Bild, Datum mit Uhrzeit, Ort, Veranstalter, Eintritt; Filter nach Land
  und Stadt als Knöpfe mit `aria-pressed`, nur mit Skript), „Das Jahr“ (vergangene Termine, Monate zum Aufklappen).
- **Kontakt:** Formulare des Plugins (Nachricht, Termin, Kooperation, mit Danke-Anzeige), daneben Redaktionsdaten nur
  aus dem Customizer und „Andere Wege“; darunter die Werbeplätze aus dem Plugin mit „Preis: auf Anfrage“. Kein alter
  Seiteninhalt.
- **Tamil TV:** ohne Sender „Tamil TV kommt“ mit Symbolbild; nicht im Band und nicht unter „Mehr“.
- **Verzeichnisprofil** (`single-tamil_vz_eintrag.php`): Dachzeile, Name, Bild mit Nachweis, Profil des Plugins,
  Link zur Karte (OpenStreetMap, nicht eingebettet); ohne Lesezeit und Teilen-Leiste.
- **Impressum, Datenschutz:** außerhalb des Echtbetriebs der Hinweis „Entwurf: Der Text von KBS folgt.“
- **Suche, 404, Seiten, Archive:** Seitenkopf, Blöcke mit Blocktitel, Listen mit Bild; Seiten in der Artikelspalte,
  Plugin-Inhalte bis 720 px. Bildnachweise im Fuß eingeklappt („Bildnachweise dieser Seite (n)“).

## Bewegung D

Nur unter `prefers-reduced-motion: no-preference`, nur `transform` (als `translate`/`scale`), `opacity` und
`clip-path`; ohne Skript und mit „Bewegung reduzieren“ ist alles sichtbar und still. Der erste Bildschirm bewegt sich
nie von selbst; was einmal erschienen ist, bleibt.

| Teil | Bewegung | Dauer |
|---|---|---|
| Kopf | Kopfzeile verblasst, Logo wird 0,8 und schiebt sich unter das Band (am Scrollweg) | Weg = Kopfhöhe |
| Band | Leselinie 2 px in Impact an der Unterkante des Bands in Titan wächst mit dem Lesefortschritt | ganze Seite |
| Aufmacherbild | bis 40 px langsamer als die Seite | beim Hinausscrollen |
| „Diese Woche“ | Titan-Fläche zieht von links auf, danach steigt der Inhalt | 800 ms, Inhalt ab 55 % |
| Große Kacheln | Bild deckt sich von unten auf, Maßstab 1,06 → 1, Titel zeilenweise | 750 / 1100 / 700 ms |
| Blocktitel | steigen aus ihrer Linie | 700 ms |
| Kacheln, Nebenstücke, Meldungen, Listen | 16 px nach oben, einblenden, gestaffelt 60 ms je Spalte, 100 ms je Reihe | 560 ms |

Am Scrollweg per CSS-Scroll-Timeline (`@supports (animation-timeline: scroll())`), sonst ein passiver Scroll-Handler
mit `requestAnimationFrame`. Auftritte über IntersectionObserver (Auslöser 10 % über der Unterkante). Code:
`assets/js/app.js` (Abschnitt „Bewegung“) und `theme.css` (Abschnitt „Bewegung beim Scrollen“).

## Raster

Inhalt höchstens 1280 px, Rand 16 / 24 / 40 px (ab 600 / 1024 px). Desktop-Startseite: Aufmacher und 388 px
Meldungen mit 32 px Abstand; „Diese Woche“ dreispaltig. Brüche bei 600 und 1024 px.
