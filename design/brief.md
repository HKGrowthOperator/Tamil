# Design-Brief: tamil.de, Richtungsskizzen Runde 1

- **Status:** bestätigt von Luis am 09.11.2026 (Tor G1, `docs/abnahme/2026-11-09-G1.md`), alle vier Richtungen.
- **Vorläufig:** Die Auswahl des Auftraggebers von der Referenztafel steht aus. Bis dahin gelten die Empfehlungen
  des Scouts aus `design/referenzen/README.md`. Die Auswahl fließt spätestens bei Tor G2 ein.
- **Grundlage:** `PRODUCT.md`, Skill `tamil-marke` mit `references/abgelehnt.md`, Antworten von Luis vom 09.11.2026.
- **Gilt für:** alle vier Richtungen dieser Runde und für den Kritiker als Maßstab.

## 1. Zusammenfassung

tamil.de ist das deutschsprachige Magazin der tamilischen Diaspora in Deutschland, Österreich und der Schweiz. Die
Seite soll sich für die junge, hier aufgewachsene Generation eigenständig und hochwertig anfühlen, ohne Eltern und
Großeltern beim Lesen zu verlieren. Drei Entwürfe sind abgelehnt worden, zuletzt als „komplett generisch“; diese
Runde sucht deshalb zuerst eine Idee, die nur zu tamil.de passt, und baut noch keine ganzen Seiten.

## 2. Wichtigste Handlung

Wer die Startseite am Handy öffnet, sieht in den ersten fünf Sekunden **die eine große Geschichte des Tages** und
tippt sie an. Sie füllt den ersten Bildschirm wie ein Magazin-Cover. Alles andere (Kino, Events, weitere Meldungen)
beginnt erst darunter.

## 3. Gestaltungsrichtung

- **Farbstrategie: Committed.** Das Logo-Rot (#B5282A, in OKLCH umgerechnet) trägt die Seite, auf hellem Grund.
  Kein dunkler Grund, kein Gold oder Gelb, kein Creme mit Braungrau. Neutrale Töne sind leicht zum Rot getönt.
- **Szene:** Eine 19-Jährige fährt nach der Berufsschule mit der S-Bahn nach Hause, das Handy in einer Hand, bei
  Tageslicht, zwischen WhatsApp und Instagram. Abends zeigt sie ihrer Mutter auf demselben Handy, wann der Film
  läuft. Daraus folgt: heller Grund, große Schrift, klare Tippflächen, nichts, was man erst erklären muss.
- **Lautstärke: laut im Kopf, ruhig im Text.** Startseite und Rubrikköpfe dürfen plakativ sein (große Schrift, viel
  Rot, starke Bilder). Artikelseiten bleiben ruhig und großzügig lesbar.
- **Sprache: nur Deutsch.** Keine tamilische Schrift als Gestaltungsmittel, auch nicht in Rubriken, Überschriften
  oder als großes Schriftbild. Das geht über die Verbotsliste („Tamil-Wörter als Deko“) hinaus und ersetzt für
  diese Arbeit den Satz „Tamil-Schrift, wo sie Inhalt ist“ aus `PRODUCT.md`. Kommt Tamil im Inhalt selbst vor
  (Namen, Zitate im Altbestand), wird es mit `lang="ta"` ausgezeichnet und von einer Ersatzschrift im Schriftstapel
  sauber gesetzt. Auszeichnungsschriften müssen Tamil nicht abdecken.
- **Zwei Tonlagen** (`PRODUCT.md`): Nachrichten ruhig und seriös, Kino und Kultur lebendig. Der Wechsel ist bewusst.

### Die vier Richtungen

Jede Richtung bekommt ihren Kern und ihr Vorbild. Die Idee, die Schriftwahl und das Signatur-Element findet der
Gestalter selbst und begründet sie in `begruendung.md`.

| Slug | Kern | Vorbild (Screenshots in `design/referenzen/img/`) |
|---|---|---|
| `plakatwand` | Die Seite denkt wie eine Kinoplakatwand: ein Bild, ein Moment, überlebensgroß und angeschnitten. Ein Look, kein Filter über Fotos. | DT Next, Reportage über handgemalte Banner (`dtnext-flex.png`); ergänzend The News Minute (`tnm-posters.png`) |
| `zine` | Der Einstieg ist jede Woche ein neues Cover mit Haltung, gebaut wie ein selbst gemachtes Heft. | Burnt Roti (`burntroti.png`); ergänzend WEIRDO zine (`weirdo.png`) |
| `raster` | **Raster + große Schrift:** strenges Linienraster, große lateinische Typografie, Rot als einziger Farbfleck. Ersetzt „Raster + Tamil-Schrift“, weil die Seite nur Deutsch zeigt. | Highsnobiety (`highsnobiety.png`), Hypebeast (`hypebeast.png`) |
| `feed` | Ein vertikaler Fluss fürs Handy: zwei Hälften im Gegensatz, Logo als Form, Navigation in Daumenreichweite. | i-D (`idmag.png`); ergänzend The Pudding (`thepudding.png`) |

Die Vorbilder liefern Haltung und Mittel, keine Vorlage zum Nachbauen. Wo ein Vorbild selbst nah an der Verbotsliste
liegt (Etiketten bei Brut., rote Fläche bei gal-dem), gilt die Verbotsliste.

## 4. Umfang

- **Skizze**, keine fertige Seite. Je Richtung zwei Dateien: `index.html` (erster Bildschirm mit dem Aufmacher plus
  der Abschnitt „Diese Woche“) und `artikel.html` (Kopf bis zum ersten Absatz).
- **Handy und Desktop gleich ernst**: geprüft bei 390, 820 und 1280 Pixeln.
- Statisches HTML mit eigener CSS-Datei, kein Framework, JavaScript nur, wenn die Idee es braucht.
- Keine weiteren Seitentypen, keine Menü-Unterseiten, kein Cockpit. Das kommt nach Tor G2.

## 5. Aufbau

- **Startseite, erster Bildschirm:** Marke und eine knappe Navigation, dann der Aufmacher als Cover. Überschrift,
  Bild und Rubrik sind eine Einheit; nichts daneben konkurriert. Am Handy ist die Überschrift ohne Scrollen
  vollständig lesbar.
- **Darunter „Diese Woche“:** Kino und Events als zweiter Abschnitt mit eigenem Rhythmus, erkennbar anders gebaut
  als das Cover. Termine sind nach Datum und Ort lesbar, nicht als gleichförmiges Kartenraster.
- **Artikel:** Rubrik, Überschrift, Vorspann, Bild, erster Absatz. Ruhig, eine Spalte, höchstens 70 Zeichen je
  Zeile, Fließtext mindestens 18 Pixel am Handy. Die Lautstärke der Startseite klingt im Kopf nach, der Text
  bleibt still.
- Abstände wechseln bewusst; gleiche Polsterung überall ist Monotonie.

## 6. Zustände

Die Skizze zeigt den Normalfall. Diese Fälle müssen in ihr vorkommen oder in `begruendung.md` beantwortet sein:

- **Aufmacher mit kleinem Bild.** Viele Beitragsbilder im Bestand sind nur 692 bis 900 Pixel breit. Das Cover muss
  mit Schrift und Farbe tragen und darf kein Bild über seine Größe strecken.
- **Eintrag ohne Foto.** Die Kino-Termine haben kein Pressefoto. Sie brauchen eine Form, die ohne Bild gut aussieht.
- **Lange und kurze Überschrift.** Von „Dosa“ bis zu 78 Zeichen.
- **Viele und wenige Spielorte.** 11 Kinos und 2 Kinos im selben Abschnitt.
- **Fokus** sichtbar auf jedem Link und Knopf; **`prefers-reduced-motion`** beachtet.

## 7. Bedienung

- Antippen des Covers öffnet den Artikel; die ganze Fläche ist das Ziel.
- Navigation zu den Rubriken ist mit dem Daumen erreichbar; Tippflächen mindestens 44 × 44 Pixel.
- Teilen über WhatsApp ist im Artikel sichtbar (einfacher Link, kein Skript von Dritten).
- Kein Laufband, kein Autoplay, keine automatische Bewegung. Fremdinhalte erst nach Klick.
- Kein seitliches Scrollen der Seite bei 390, 820 und 1280 Pixeln.

## 8. Inhalte

Alle vier Richtungen zeigen **dieselben echten Inhalte**, damit der Vergleich die Gestaltung zeigt und nicht die
Themen. Texte unverändert aus `prototyp/content/posts.json`; Bilder relativ aus `prototyp/static/img/`.

| Platz | Inhalt | Quelle |
|---|---|---|
| Aufmacher (Cover) | „Kanguva – Ein tamilisches Kino-Highlight ab 14. November in Deutschland“ | Beitrag 9711, Bild `p9711.jpg` (1024 × 538) |
| Artikel | „Sri Lanka schafft Visum für Deutsche ab“, Vorspann und erster Absatz | Beitrag 9655, Bild `p9655.jpg` (900 × 458) |
| Diese Woche, Kino | „Scene“ im Kino: 11 Spielorte in Deutschland (Berlin, Bremen, Chemnitz, Dortmund, Düsseldorf und 6 weitere Städte) | Radar-Entwurf, freigegeben |
| Diese Woche, Kino | „Ramayana: Rise of a Legend“ im Kino: 2 Spielorte in Deutschland (Gütersloh, Ravensburg) | Radar-Entwurf, freigegeben |
| Diese Woche, Event | Diwali in Basel: Basel Tamil Sangam feiert am 21. November 2026, Aula Lysbüchel | Radar-Entwurf, freigegeben |

- **Rubriken** (echte Namen): Nachrichten, Entertainment, Events, Community, Küche, Kino, Sport, Kultur, Kontakt.
- **Logo:** `prototyp/static/img/logo.png`, unverändert (Rot und Grau).
- **Datum**, falls gezeigt: das Originaldatum des Beitrags (`datum_original`).
- **Nichts erfinden:** keine weiteren Titel, Zahlen, Uhrzeiten, Preise, Bildnachweise oder Kontakte. Die Kino- und
  Event-Einträge haben keine Fotos; kein Platzhalterbild und kein erfundener Nachweis. Telefon, E-Mail und
  WhatsApp-Nummer in `prototyp/content/site.json` sind Beispielwerte und werden nicht verwendet.
- **Bilder:** In `prototyp/static/img/` liegen verkleinerte Kopien (höchstens 1024 Pixel breit). Auf der echten
  Seite sind die Originale größer; in der Skizze wird trotzdem nichts hochskaliert.
- **Werbung:** Wenn ein Werbeplatz gezeigt wird, trägt er das Wort „Anzeige“ und ordnet sich dem Inhalt unter.

## 9. Hilfreiche Nachschlagedateien

Aus `.claude/skills/impeccable/reference/`: `brand.md` (Register und abgegriffene Stile), `typography.md` und
`typeset.md` (Schriftwahl und Hierarchie), `color-and-contrast.md`, `spatial-design.md` und `layout.md`,
`responsive-design.md`. Barrierefreiheit prüft später `audit.md`; die Pflichten oben gelten trotzdem ab der Skizze.

## 10. Offen

- Die Auswahl des Auftraggebers von der Referenztafel (3 bis 5 Vorbilder, die er mag, 2, die er nicht mag).
- Schriftlizenzen: nur Google Fonts oder selbst gehostete Schriften mit Lizenzdatei im Richtungsordner; nichts von
  der impeccable-Ausschlussliste und keine der verbrannten Schriften aus `abgelehnt.md`.
- Bildsprache für Beiträge ohne Foto (Kino-Termine, Küche): Die Richtung schlägt eine Lösung vor; ob sie sich mit
  dem Bestand halten lässt, zeigt erst die Probeseite.

## Maßstab für die Kritik

Eine Richtung wird dem Auftraggeber nur gezeigt, wenn sie mindestens 28 von 40 Punkten erreicht, den Slop-Test
besteht und kein offenes P0 oder P1 hat. Zusätzlich aus diesem Brief: Die eine Geschichte steht am Handy im ersten
Bildschirm, die Seite zeigt nur Deutsch, der Artikel ist ruhig, und nichts von der Verbotsliste kommt vor.
