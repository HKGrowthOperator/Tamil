# Bauvorgabe: drei Startseiten-Proben für tamil.de

Stand 21.11.2026. Grundlage: Theme `wordpress/themes/tamil` (klar2, 3.13.x), `DESIGN.md`, `design/brief.md` §10,
`abgelehnt.md`, Festlegung F3, Testseite `tamil-web.167.233.76.202.sslip.io` (Aufnahmen 390/820/1280 in
`proben/ist/`), Beitragsdaten über die REST-Schnittstelle der Testseite (100 Beiträge, gezählt am 21.11.).

Umfang je Probe: Kopf (unverändert), erster Abschnitt (`.innen.oben`) und der neue Abschnitt „Tamil in meiner
Stadt“. Alles darunter bleibt die heutige Seite. Schalter: `?probe=cover|news|community`, ohne Parameter die heutige
Startseite.

---

## 1. Bestandsaufnahme (heutiger erster Bildschirm)

1. Handy 390: nach 160 px Kopf folgt der Aufmacher 4:3, darunter vier Karten 16:9 in voller Breite untereinander.
   Fünf Karten hintereinander haben denselben Aufbau: Verlauf, Dachzeile, weißer Titel 650 unten links, Punktbogen.
2. Desktop 1280: Aufmacher 780 × 585, rechts drei gleiche Karten 388 × 218, darunter vier gleiche Karten 290 × 218
   mit drei Zeilen Vorspann. Sieben der acht Karten unterscheiden sich in der Fläche um höchstens den Faktor 1,3.
3. Es gibt zwei Stufen (Aufmacher, alles andere). Eine zweite wichtige Geschichte ist nicht zu erkennen.
4. Danach folgen acht Rubrikkacheln, wieder Bild mit Schrift im Verlauf. Bis zur ersten Anzeige sind es 16 Bildflächen
   mit Schrift im Bild.
5. Die Reihenfolge sagt nichts: Daten im ersten Abschnitt 13.11., 8.11., 7.11., 25.10., 24.10., 23.10., 22.10.,
   15.10. Aktualität ist nicht ablesbar, der neueste Beitrag ist acht Tage alt.
6. Kontext fehlt: außer „Rubrik | Datum“ und dem Vorspann steht nirgends Ort oder Quelle, obwohl beides bei 72 von
   100 Beiträgen gepflegt ist (`ort`, `quelle_name`).
7. Vier der acht Karten tragen das Schild „Symbolbild“, eine zeigt ein Kino-Logo. Die Bildregie kann sich nicht auf
   jedes Foto verlassen, große Flächen müssen an Beiträge mit eigenem Foto gehen.
8. Zwei Deepavali-Beiträge stehen mit fast gleichem Titel direkt nebeneinander.
9. Ortsbezug (das Eigene von tamil.de) taucht erst in „Diese Woche“ auf, am Desktop ab etwa 1050 px, am Handy nach
   rund vier Bildschirmen.
10. Nebenbefund: `shots.mjs` meldet bei 820 und 1280 zwei fehlgeschlagene Bildanfragen (`…-300x169.webp/.jpg`).
    Nicht Teil dieser Vorgabe, bitte beim Bau mitprüfen.

---

## 2. Die drei Proben

Gemeinsame Daten: `tamil_start_auswahl()` bleibt die Quelle. Der Vorrat für den ersten Abschnitt sind die acht dort
schon reservierten Beiträge: `lead` und `P` = `neben` (4) + `meldungen` (3), nach Datum absteigend sortiert
(`get_post_timestamp()`). So bleibt alles darunter frei von Dubletten, ohne die Auswahl umzubauen.

### 2.1 Cover First (`?probe=cover`)

**Idee.** Eine Titelgeschichte als Cover mit eigenem Kontextfeld, daneben eine Spalte mit drei Beistücken in drei
Formaten, absteigend. Beste Wahl für Leser, die einmal am Tag kommen und wissen wollen, was die eine Geschichte ist;
wirkt am stärksten wie ein Magazin.

**Aufbau 390** (Kopf 160 px, Bildschirm 844)

```
0    ┌──────────────────────────────┐
     │ Kopfzeile, Logo, Rubrikband  │ 160
160  ├──────────────────────────────┤
     │ COVER 4:3, randlos 390×293   │
     │ Dachzeile                    │
     │ Titel 28 px, max. 4 Zeilen ◔ │
453  ├──────────────────────────────┤
     │ Ort | Quelle (14 px)         │ 24
     │ Vorspann 18 px, 2 Zeilen     │ 52
549  │ ┌──────────────────────────┐ │
     │ │ B1 4:3  358×268, 22 px ◔ │ │
817  │ └──────────────────────────┘ │  ← Titel B1 ganz sichtbar (844)
     │ Satz zu B1 (18 px, 2 Zeilen) │
     │ ┌ B2 16:9 358×201, 19 px ◔ ┐ │
     │ ┌ B3 8:3  358×134, 19 px ◔ ┐ │
     │ „Weitere Meldungen“: übrige 4 als .karten--reihe (wie heute)
     │ Rubrikkacheln → Leaderboard → Tamil in meiner Stadt → Diese Woche …
```

**Aufbau 1440** (Inhalt 1280, Raster wie heute `minmax(0,1fr) 388px`, Abstand 32)

```
┌───────────────────────────────────────────────┬──────────────────────┐
│ COVER 860 × 573 (3:2) oder 860 × 538 (16:10)  │ B1 4:3  388×291 24px │
│                                               │ ◔                    │
│                                               ├──────────────────────┤
│ Dachzeile                                     │ B2 16:9 388×218 20px │
│ Titel 44 px, max. 3 Zeilen                  ◔ ├──────────────────────┤
├──────────────────────┬────────────────────────┤ B3 8:3  388×146 18px │
│ Titelgeschichte      │ Vorspann 19 px,        └──────────────────────┘
│ Ort, Quelle, Datum   │ max. 60 Zeichen/Zeile  (Spalte 687 hoch, Abstände 16)
└──────────────────────┴────────────────────────
  Kontext: 2 Spalten 280 | 548, etwa 120 hoch
─ darunter: übrige 4 als Reihe .neben.karten (wie heute) → Rubrikkacheln → Leaderboard
```

Tablet 820: Cover 16:10 in voller Inhaltsbreite, Kontext darunter einspaltig, B1 bis B3 in einer Reihe gleicher Höhe
mit Breiten 2fr / 1,5fr / 1,5fr (gleich hoch, verschieden breit).

**Coverformat (Bildregie).** Handy immer 4:3. Ab 600 px: Seitenverhältnis des Originals ≥ 1,6 → 16:10 (`r1610`),
sonst 3:2 (`r32`); Titel über 90 Zeichen → immer 3:2 (mehr Höhe für den Titel). Verhältnis aus
`wp_get_attachment_metadata()`. Der Rahmen ist wie überall Mindestmaß und wächst mit dem Titel.

**Wer wohin.**
- Cover = `lead` aus `tamil_start_auswahl()` (Customizer `aufmacher_id`, sonst markiert, sonst neuestes Foto).
  Zusätzlich für die Probe: hat `lead` nur ein Symbolbild (`tamil_bildwahl( $id )['art'] === 'pool'`), rückt der
  erste Beitrag aus `P` mit eigenem Foto (`tamil_leitbild( $P )`) aufs Cover.
- B1 = erster aus `P` mit eigenem Foto (`tamil_ist_foto()`), B2 = nächster, B3 = bevorzugt ein Beitrag mit breitem
  Bild (`tamil_bildwahl()['breit']`) oder Symbolbild, weil 8:3 das am besten verträgt. Zwei Beiträge mit gleicher
  Rubrik und gleichem ersten Titelwort („Deepavali 2026“) nicht nebeneinander: der zweite rückt in die Reihe darunter.
- Übrige vier aus `P`: bestehende Reihe (`.neben.karten`, am Handy `.karten--reihe`), Blocktitel „Weitere Meldungen“.

**Typografie.**
- Covertitel: `clamp(28px, 22px + 1.52vw, 44px)`, 650, Zeilenhöhe 1,1, Laufweite −0,015em, `max-width: 18em`,
  Handy höchstens 4, Desktop höchstens 3 Zeilen. Stufen wie heute über `titel_stufen` (`titel--mittel` × 0,9,
  `titel--klein` × 0,8), nie kürzen, nie trennen.
- B1 22 / 24 px, B2 19 / 20 px, B3 19 / 18 px, alle 650, Zeilenhöhe 1,18 bis 1,2, `text-wrap: balance`.
- Kontext: Angaben 14 px / 600 (Bezeichnung) und 400 (Wert), Vorspann 18 px / 1,45 am Handy, 19 px / 1,5 am Desktop,
  höchstens 60 Zeichen je Zeile. Blocktitel „Titelgeschichte“ 19 / 20 px, 700, mit der 2-px-Linie in Titan.

**Text neben der Karte und seine Quelle.**

| Element | Feld | Wenn leer |
|---|---|---|
| Rubrik, Datum | `tamil_meta()` (im Bild, wie heute) | nie leer |
| Ort | Meta `ort` (Plugin tamil-site, roh wie eingegeben), bei Terminen `tamil_ort_kurz( event_ort )` | Zeile entfällt |
| Termin | `tamil_termin_text( event_datum, event_ende )`, nur wenn `tamil_site_event()` etwas liefert | entfällt |
| Quelle | Meta `quelle_name` als Text „Quelle: …“, kein Link nach außen | entfällt (28 von 100 ohne) |
| Vorspann | `tamil_ganze_saetze( tamil_saetze_bis( tamil_standfirst( $id ), 260 ) )`; am Handy 2 Zeilen | nie leer (Auszug, sonst Textanfang) |
| „Warum das wichtig ist“ | **gibt es als Feld nicht.** Meta `standfirst` ist bei allen 100 Beiträgen leer, der Vorspann kommt aus dem Auszug | Die Überschrift „Warum das wichtig ist“ wird **nicht** gezeigt; der Auszug steht ohne dieses Etikett. Erst mit eigenem Feld (Frage 1) |
| Satz zu B1 | `tamil_saetze( tamil_standfirst( $id ), 1 )` | entfällt |

Der Kontext steht im selben Link wie das Cover (Option `zusatz` von `tamil_anr_imbild()` nimmt das HTML auf, danach
folgt der Vorspann). Kein zweiter Link auf denselben Beitrag.

**Bewegung.** Nur die vorhandene Rückmeldung: Zoom 1,03 in 0,35 s und unterstrichener Titel beim Überfahren. Der
erste Bildschirm bewegt sich nie von selbst. Reduzierte Bewegung: kein Übergang. Wow-Aufmacher bleibt aus.

**Risiken.**
- Bei 1280 × 800 sind drei Titel ganz sichtbar (Cover, B1, B2), B3 endet bei 890 px. Brief §10.4 Nr. 1 verlangt
  vier. Das liegt in der Natur des Covers (Frage 5).
- Ein viertes Seitenverhältnis kommt dazu (16:10 oder 3:2 neben 4:3, 16:9, 8:3); Brief §10.1 nennt drei.
- Die Bilddateien sind 900 bis 1024 px breit und rund 1,9:1. Bei 860 px Coverbreite und doppelter Pixeldichte wird es
  weich, 3:2 schneidet die Seiten ab. Gesichter am Rand prüfen (`object-position` je Bild ist nicht pflegbar).
- Nähe zu Runde 4 („ein Cover mit nur einer Geschichte“): nur zulässig, weil am Handy B1 und am Desktop B1 und B2
  im ersten Bildschirm stehen. Wer B1 nach unten schiebt, baut die abgelehnte Fassung.
- Verschieden große Stücke dürfen kein Mosaik werden (Runde 2): ein Cover, eine Spalte, sonst nichts verschachteln.
- Steht acht Tage dieselbe Geschichte auf dem Cover, altert die Seite sichtbar. Cover First braucht Pflege
  (`aufmacher_id`).

### 2.2 News First (`?probe=news`)

**Idee.** Oben eine Zeitfolge: Meldungen nach Erscheinen geordnet, links die Zeit, in der Mitte die Bildkarte, rechts
Ort, Quelle und ein Satz. Das Cover steht kleiner daneben. Beste Wahl für Leser, die oft kommen und nur wissen wollen,
was neu ist; setzt voraus, dass wirklich täglich etwas erscheint.

**Aufbau 390**

```
160  ├──────────────────────────────┤
     │ Heute wichtig  (Blocktitel)  │ 48     ← Wortlaut nach Regel unten
208  │ Heute, 19:43 Uhr | Events    │ 22     ← Zeit steht außerhalb des Bilds
     │ ┌ Z1 16:9 358×201, 22 px ◔ ┐ │
431  │ Ort. Ein Satz. (18 px, 2 Z.) │ 52
503  │ 12. November 2026 | Kino     │
     │ ┌ Z2 8:3 358×134, 19 px ◔  ┐ │
659  │ Ort. Ein Satz.               │        ← Z1 und Z2 ganz sichtbar, Z3 angeschnitten
     │ Z3, Z4, Z5 wie Z2            │
     │ COVER klein 16:9, randlos 390×219, Titel 24 px + Vorspann
     │ ┌ N1 16:9 ┐ ┌ N2 8:3 ┐       │
     │ Rubrikkacheln → Leaderboard → Tamil in meiner Stadt → Diese Woche …
```

**Aufbau 1440** (Raster `minmax(0,7fr) minmax(0,5fr)`, Abstand 32: links 728, rechts 520)

```
┌─ Heute wichtig ───────────────────────────────────┐ ┌──────────────────────────┐
│ Heute     ┌ Z1 16:9 380×214 ┐ Ort                 │ │ COVER klein 4:3 520×390  │
│ 19:43 Uhr │ Titel 22 px   ◔ │ Ein Satz, 16 px,    │ │ Titel 28 px, max. 4 Z. ◔ │
│ Events    └─────────────────┘ Quelle              │ ├──────────────────────────┤
├───────────────────────────────────────────────────┤ │ Ort, Quelle, Vorspann    │
│ 12. Nov.  ┌ Z2 16:9 280×158 ┐ Ort. Ein Satz.      │ ├──────────────────────────┤
│ 2026      │ Titel 18 px   ◔ │ Quelle              │ │ N1 16:9 520×292, 20 px ◔ │
├───────────────────────────────────────────────────┤ ├──────────────────────────┤
│ Z3, Z4, Z5 wie Z2 (je 158 + 20)                   │ │ N2 8:3 520×195, 18 px  ◔ │
└───────────────────────────────────────────────────┘ └──────────────────────────┘
  Spalten links: Zeit 76 | Karte 280 (Z1: 380) | Kontext Rest; Zeilen durch 1 px --linie getrennt
  links etwa 970 hoch, rechts etwa 1040
```

Tablet 820: einspaltig, Zeile = Zeit 72 | Karte 300 | Kontext; Cover danach in voller Breite 16:9.

**Wer wohin.**
- Zeitfolge Z1 bis Z5 = die fünf neuesten aus `P` (schon nach Datum sortiert). Markup `<ol class="zeitfolge">`,
  echte Reihenfolge, keine gezeigten Nummern.
- Cover klein = `lead`. N1, N2 = die zwei ältesten aus `P`.
- Ehrlich: `P` sind die neuesten Beiträge **mit zeigbarem Bild und ohne die Kino- und Terminbeiträge aus „Diese
  Woche“**, nicht streng die neuesten überhaupt. Für die Probe reicht das; für den Echtbetrieb müsste die Auswahl
  streng nach Datum laufen (eigene Abfrage `tamil_ids( array( 'posts_per_page' => 5 ) )` vor den Rubrikblöcken).

**Blocktitel und Zeit (keine erfundene Aktualität).**
- „Heute wichtig“ nur, wenn mindestens ein Beitrag der Zeitfolge von heute ist (`wp_date( 'Y-m-d' )`). Sonst
  „Zuletzt erschienen“. Heute (21.11.) wäre es „Zuletzt erschienen“: neuester Beitrag vom 13.11.
- Zeit: heute → „Heute, 19:43 Uhr“; gestern → „Gestern, 19:43 Uhr“; älter → „12. November 2026“ ohne Uhrzeit
  (importierte und von Hand datierte Beiträge tragen 12:00 Uhr, das wäre eine Scheingenauigkeit). `<time datetime>`
  immer vollständig.

**Typografie.**
- Zeit: 15 px / 600, `font-variant-numeric: tabular-nums`, Schwarz; Rubrik dahinter im Format der Dachzeile (13 px,
  Impact, Strich). Am Desktop steht die Zeit zweizeilig in der 76-px-Spalte.
- Titel Z1 22 px, Z2 bis Z5 19 px am Handy und 18 px am Desktop, 650. Im Bild steht nur der Titel
  (`'dach' => ''`), dadurch bleibt mehr Foto frei.
- Kontextsatz: 18 px / 1,45 am Handy (2 Zeilen), 16 px / 1,45 am Desktop (3 Zeilen), höchstens 48 Zeichen je Zeile.
  Ort 14 px / 600, Quelle 14 px in `--leise`.
- Cover klein: `clamp(24px, 21px + 0.5vw, 28px)`, 650, mit `titel_stufen`. Größte Schrift der Seite bleibt damit der
  Covertitel.

**Text neben der Karte.** Zeit und Rubrik (`get_post_timestamp()`, `tamil_hauptkategorie()`), Ort (`ort`), ein Satz
(`tamil_saetze( tamil_standfirst( $id ), 1 )`, über 150 Zeichen an der Wortgrenze gekürzt wie bei `'vorspann' =>
'kurz'`), Quelle (`quelle_name`). Leere Felder entfallen ohne Platzhalter. Alles im selben Link wie die Karte
(`zusatz`).

**Bewegung.** Beim Überfahren einer Zeile: Zoom wie heute, dazu wird die Trennlinie über der Zeile Titan
(`border-color`, 0,2 s). Reduzierte Bewegung: Farbwechsel ohne Übergang.

**Risiken.**
- Größtes Risiko ist der Inhalt, nicht die Form: im November neun Beiträge, davon sieben an drei Tagen. An den
  meisten Tagen zeigt die Probe „Zuletzt erschienen“ mit Daten von vor einer Woche und stellt genau das aus, was fehlt.
- Fünf gleich gebaute Zeilen sind wieder eine Wiederholung. Sie ist hier Absicht (Reihenfolge ist die Aussage), aber
  Luis' Einwand „ähnliche Bildkarten“ trifft die Probe am ehesten.
- Bei 280 px Kartenbreite passen etwa 22 Zeichen je Zeile; Titel über 80 Zeichen brauchen vier Zeilen, der Rahmen
  wächst und die Zeilen werden ungleich hoch. Zulässig (kein Abschneiden), aber unruhiger.
- Am Handy steht das Cover erst nach rund 1250 px. Das eigene Foto der Titelgeschichte verliert seine Wirkung.
- Symbolbilder fallen in kleinen Karten weniger auf, das Schild „Symbolbild“ steht aber dichter (bis zu vier von
  fünf Zeilen).

### 2.3 Community First (`?probe=community`)

**Idee.** Die Seite beginnt mit „Tamil in meiner Stadt“: Stadt wählen, darunter Kino, Termine und Geschichten von
dort. Danach folgt der heutige erste Abschnitt unverändert (Aufmacher, Meldungen, Nebenstücke). Beste Wahl für die
Stammleser aus der Community, die wegen Kino und Terminen kommen; die einzige Probe, die es so nur bei tamil.de gibt.

**Aufbau 390**

```
160  ├──────────────────────────────┤
     │ Tamil in meiner Stadt (24px) │ 40
     │ Stadt [ Alle Städte      ▾ ] │ 48 + Hinweis 20
280  │ Im Kino                      │
     │ ┌ Film 16:9 358×201, 22px ◔┐ │
     │ Kino, Zeit. Tickets und Zeiten│ 48
545  │ Termine                      │
     │ ┌ T1 8:3 358×134, 19 px ◔  ┐ │
     │ Datum, Ort, Eintritt         │  ← Film und T1 ganz sichtbar
     │ ┌ T2 8:3 ┐                   │
     │ Aus der Stadt                │
     │ ┌ G1 16:9 ┐ ┌ G2 8:3 ┐ ┌ G3 8:3 ┐ (Bauart Bühne wie „Küche“)
     │ Kino nach Stadt | Alle Termine
     │ ── heutiger erster Abschnitt: Aufmacher 4:3, Meldungen, Nebenstücke, Rubrikkacheln
     │ Leaderboard → Diese Woche …
```

**Aufbau 1440**

```
┌ Tamil in meiner Stadt (28 px) ──────────────── Stadt [ Alle Städte ▾ ] ┐  70
├─────────────────────────┬──────────────────┬──────────────────┤
│ Im Kino                 │ Termine          │                  │
│ Film 8:3 516×206 ◔      │ T1 366×206 ◔     │ T2 366×206 ◔     │  eine Reihe, gleich hoch,
│ Kino, Zeit, Tickets     │ Datum, Ort       │ Datum, Ort       │  5fr / 3,5fr / 3,5fr
├─────────────────────────┴──────────────────┴──────────────────┤
│ Aus der Stadt: Bühne (bestehend): G1 16:9 groß 860×484 | G2, G3 je 8:3 388 gestapelt │
└────────────────────────────────────────────────────────────────┘
  Kino nach Stadt | Alle Termine
─ danach .innen.oben wie heute (Aufmacher 4:3 + Meldungen 388 + Nebenstücke) → Rubrikkacheln → Leaderboard
```

Abschnitt auf Weiß mit der 2-px-Linie in Titan, **keine** zweite Titan-Fläche über dem Aufmacher. Bei 1280 × 800
ganz sichtbar: Film, T1, T2 und die erste kleine Kachel der Bühne (vier Titel).

**Wer wohin.** Aufbau und Daten des Abschnitts: Kapitel 3. Darunter `lead`, `meldungen`, `neben`, `kacheln` genau wie
in `front-page.php`. Die Beiträge des Abschnitts kommen nicht aus `P` und nicht aus `lead`.

**Typografie.** Abschnittstitel 24 / 28 px, 700. Fachtitel („Im Kino“, „Termine“, „Aus der Stadt“) 17 px / 700 in
Schwarz, keine Versalien. Karten wie in Kapitel 3. Der Aufmacher darunter behält die heutigen Größen (26 / 38 px).

**Text neben der Karte.** Kapitel 3 (Spielort und Zeit aus `kino_fakten`, Datum, Ort und Eintritt aus den
Termin-Metadaten, bei Geschichten Ort und ein Satz).

**Bewegung.** Nach einer Stadtwahl blendet der Inhalt des Abschnitts in 160 ms um (`opacity`, Antwort auf die
Handlung). Reduzierte Bewegung: sofortiger Wechsel. Kein Springen: die Kartenreihe hält ihre Höhe.

**Risiken.**
- Die Datenlage trägt den ersten Bildschirm heute nicht (Kapitel 3.1). Ab morgen gibt es keine Vorstellung und
  genau einen Termin; der Abschnitt bestünde oben aus einer Terminkarte und einer Leerzeile.
- Kino und Termine stehen noch einmal in „Diese Woche“ (derselbe Film, dieselben Termine). Solange beide Bereiche
  bleiben, ist das eine Dopplung (Frage 2).
- Die Titelgeschichte beginnt am Handy nach rund zwei Bildschirmen. Für neue Besucher sieht der Einstieg aus wie ein
  Veranstaltungskalender, nicht wie ein Magazin.
- Ein Auswahlfeld als erstes Element verlangt eine Handlung, bevor etwas Persönliches erscheint. Deshalb ist der
  Zustand „Alle Städte“ vollständig und die Wahl freiwillig.
- Der erste Abschnitt wird lang; der Leaderboard (nach den Rubrikkacheln, F3) rückt am Handy um etwa 1000 px nach
  unten. Der Ort bleibt, die Sichtbarkeit sinkt. `app.js` blendet die feste Handy-Anzeige erst nach
  `main .aufmacher` ein; in dieser Probe also später.

---

## 3. Abschnitt „Tamil in meiner Stadt“ (in allen drei Proben gleich gebaut)

Position: Cover First und News First direkt nach dem Leaderboard, vor „Diese Woche“. Community First ganz oben in
`main`, vor `.innen.oben`. `id="meine-stadt"`, `<section class="stadt innen" aria-labelledby="t-stadt"
data-stadt-bereich>`.

### 3.1 Was an Daten wirklich da ist (Testseite, 21.11.2026)

| Quelle | Bestand | Folge |
|---|---|---|
| Kino: Meta `kino_fakten` (`kinos[]` mit `kino`, `stadt`, `land`, `termine[]` oder `von`/`bis`, `url`) | 3 Beiträge mit Liste. Mit Spieltagen ab heute nur „OM“: 13 Kinos in 12 Städten (Bremen, Chemnitz, Dortmund, Düsseldorf, Erlangen, Jena, Karlsruhe, Magdeburg, Mainz, Oberhausen, Rostock, Siegen), alle Vorstellungen am 21.11. Nur Deutschland | Stadt und Land sauber getrennt, gut filterbar. Aber: ab 22.11. ist das Fach leer |
| Termine: `event_datum`, `event_ende`, `event_ort`, `event_veranstalter`, `event_preis`, `event_land` | 4 Beiträge mit Termin überhaupt. Ab heute: Basel (21.11.), Aarau (21.11.), Bern (13.12.). `event_land` ist bei allen leer | Stadt nur über `tamil_ort_kurz( event_ort )` (letzter Teil nach dem Komma, ohne Postleitzahl). Land nicht filterbar |
| Beiträge mit Ort: Meta `ort` (Freitext, „Ort der Meldung“) | 72 von 100 gefüllt, 58 Schreibweisen, oft mehrere Orte („Viersen, Arnsberg, Hannover, Stuttgart und Landau, Deutschland“), achtmal nur „Deutschland“. Zerlegt: 53 Orte. Bern 7, Berlin 6, Zürich 5, Wien 5, Basel 3, Düsseldorf 3, Wuppertal 3, Stuttgart 3; je 2: Aarau, Kloten, München, Köln, Hamburg, Glattbrugg; 39 Orte nur einmal | Brauchbar für etwa 14 Städte. Viele Beiträge sind von 2024, das Jahr muss sichtbar sein |
| Verzeichnis (`tamil_vz_eintrag`, `_tamil_vz_stadt`) | nur ein Testeintrag („Musterstadt“) | **nicht verwenden** |
| Eigenes Stadt-Feld, Taxonomie, Koordinaten | gibt es nicht | keine Standortabfrage, keine Umkreissuche |

Ehrliches Fazit: Nur Düsseldorf, Bremen und Oberhausen haben heute Kino **und** Beiträge; Bern, Basel und Aarau
Termin **und** Beiträge. Für fast jede Stadt ist höchstens eines von drei Fächern gefüllt. Der Abschnitt muss mit
einem gefüllten Fach gut aussehen, sonst ist er nicht baubar.

### 3.2 Stadtliste

Neue Funktion `tamil_stadt_daten()` (Theme, `inc/proben.php`), Ergebnis im Transient wie die Startseite:
- Kino-Städte: aus `tamil_kino_filme( 6 )`, je Kino nur, wenn `termine`/`bis` ≥ heute.
- Termin-Städte: `tamil_site_upcoming_events( 12 )`, Stadt aus `tamil_termin_angaben()['stadt']`, „Ort folgt“ fällt
  weg.
- Beitrags-Städte: neue Hilfsfunktion `tamil_stadt_namen( string $ort ): string[]`: trennt an `,`, `;`, `/`, „ und “;
  verwirft Länder (Deutschland, Schweiz, Österreich, Sri Lanka), alles mit „Kanton“, Klammern und Wörter wie
  „Tamilalayams“; Schlüssel `sanitize_title()`. Quelle: die 24 neuesten Beiträge mit `ort`, ohne `lead`, `P` und
  die Beiträge aus `woche`.
- In die Auswahl kommt eine Stadt mit mindestens einer kommenden Vorstellung, einem kommenden Termin oder zwei
  Beiträgen. Sortiert alphabetisch (`SORT_LOCALE_STRING`), ohne Ländergruppen (Land ist nur beim Kino bekannt).
  Heute etwa 25 Einträge.

### 3.3 Stadtwahl (Bedienelement)

- Ein echtes Auswahlfeld, keine Knopfreihe: `<label for="stadt-wahl">Stadt</label><select id="stadt-wahl">` mit
  „Alle Städte“ als erstem Eintrag. 25 Städte als Knöpfe wären eine Pillenreihe (Runde 3) oder eine wischbare Leiste.
  Feld 48 px hoch, 17 px, Radius 6 px, Rand 1 px `--leise`, Fokusrahmen wie alle Felder. Tastatur und Vorlesen wie
  jedes `select`, kein eigenes Listenfeld.
- Titel: `<h2 id="t-stadt">Tamil in <span data-stadt-name>meiner Stadt</span></h2>`. Nach der Wahl „Tamil in Bern“.
- Darunter 14 px in `--leise`: „Die Auswahl bleibt nur in diesem Browser gespeichert.“
- Speicherung: `localStorage`, Schlüssel `tamil_stadt`, Wert `{ "slug": "bern", "name": "Bern" }`. Kein Cookie,
  nichts geht an den Server, keine Standortabfrage, kein Zustimmungsdialog nötig. „Alle Städte“ löscht den Eintrag.
  `try/catch` um jeden Zugriff (privater Modus).
- Kein Springen beim Laden: ein kleines Skript direkt hinter dem Abschnitt (inline, vor dem ersten Malen) liest den
  Schlüssel und setzt die `hidden`-Attribute. Alle Karten aller Städte stehen im HTML, gefiltert wird über
  `data-stadt` wie auf `/events/` (`app.js`, Abschnitt `[data-filter]`: gleiche Logik, hier mit `select` statt
  `.chip`). Versteckte Karten laden ihre Bilder nicht (`loading="lazy"`).
- Statuszeile `<p class="nur-vorlesen" aria-live="polite">`: „Bern: 1 Termin, 3 Geschichten, keine Vorstellung.“
- Ist die gespeicherte Stadt nicht mehr in der Liste: Zustand „Alle Städte“ und sichtbar der Satz „Für {Stadt}
  haben wir gerade nichts Neues. Hier steht, was in allen Städten läuft.“

### 3.4 Was darunter erscheint

| Fach | Karte | Text unter der Karte | Quelle | Höchstens |
|---|---|---|---|---|
| Im Kino | `tamil_grafik_kino( $f )`, eine Karte je Film, `data-stadt` mit allen Stadt-Schlüsseln des Films | „Alle Städte“: `tamil_staedte_kurz()`. Mit Stadt: je Kino dieser Stadt eine Zeile „Kino, Termin“ und der Link „Tickets und Zeiten“ (`kinos[].url`, außerhalb des Kartenlinks, 44 px) | `kino_fakten`; Terminwortlaut wie in `tamil_kino_orte_tafel()` (die Formatierung dort in eine Funktion `tamil_kino_termin_text( array $k )` auslagern und an beiden Stellen nutzen) | 2 Filme |
| Termine | `tamil_grafik_termin( $id, 'h3', false )`, `data-stadt` | Datum im Bild (Dachzeile), darunter Ort, Veranstalter, Eintritt (`tamil_termin_angaben()`) | Termin-Metadaten | 2 sichtbar, bis 12 im HTML |
| Aus der Stadt | `tamil_anr_imbild()` in der Bauart Bühne (`kueche__raster rubrikblock__buehne kueche__raster--N` aus `template-parts/home/rubrik.php`): erste groß 16:9, zwei klein 8:3 | Ort (`ort`), unter der großen Karte ein Satz. Datum mit Jahr in der Dachzeile | Beiträge mit `ort` (3.2), Rubrik „Community“ zuerst, dann nach Datum | 3 sichtbar, 24 im HTML |

- „Alle Städte“ (Standard, auch ohne Skript): nächste Vorstellungen, nächste Termine, die drei neuesten Geschichten
  mit Ort.
- Die Karten `.grafik--karte` sind für Titan gebaut. Auf Weiß brauchen `grafik__orte` und `grafik__text` Schwarz
  bzw. `--leise` und den schwarzen Verlauf (`--verlauf-karte` statt `--verlauf-karte-titan`): Variante
  `.stadt .grafik--karte`.
- Reihe gleich hoch: ein Fach ohne Inhalt belegt keine Kartenfläche. Seine Leerzeile steht unter der Reihe, die
  gefüllten Fächer teilen sich die Breite (`termine-1` bis `termine-3` gibt es schon als Muster).

### 3.5 Leerzustände (Wortlaut)

Als Textzeile (`.stadt__leer`, 18 px am Handy, Link 44 px hoch), **nicht** als Bildkachel: drei leere Symbolbilder
nebeneinander wären schlechter als ein Satz.

| Fall | Wortlaut | Link |
|---|---|---|
| Stadt ohne Vorstellung | „In {Stadt} läuft gerade kein tamilischer Film, von dem wir wissen. Alle Spielorte stehen unter Kino nach Stadt.“ | `tamil_rubrik( 'kino' )['url']` |
| Stadt ohne Termin | „Für {Stadt} steht kein Termin im Kalender. Kennt ihr einen? Schickt ihn der Redaktion, kostenlos für Vereine, Tempel und Schulen.“ | `tamil_einreichen_url()` |
| Stadt ohne Geschichte | „Aus {Stadt} haben wir noch keine Geschichte. Die neuesten stehen in der Rubrik Community.“ | `tamil_rubrik( 'community' )['url']` |
| Alle Städte, kein Film | Wortlaut aus `woche.php`: „Für diese Woche kennen wir keine tamilische Vorstellung. Kinostarts, Kritiken und frühere Spielorte stehen in der Rubrik Kino.“ | Rubrik Kino |
| Alle Städte, kein Termin | Wortlaut aus `woche.php`: „Gerade steht kein kommender Termin im Kalender. Kennt ihr einen? Schickt ihn der Redaktion, kostenlos für Vereine, Tempel und Schulen.“ | Einreichen |
| Gespeicherte Stadt nicht mehr da | siehe 3.3 | keiner |
| Gar keine Daten (kein Film, kein Termin, kein Beitrag mit Ort) | Abschnitt wird nicht ausgegeben | |

### 3.6 Ohne JavaScript

Das Auswahlfeld samt Hinweis trägt `hidden` und erscheint erst mit Skript (wie `.filter` auf `/events/`). Zu sehen
ist der vollständige Zustand „Alle Städte“ mit dem Titel „Tamil in meiner Stadt“. Als Ersatz stehen am Ende des
Abschnitts immer zwei Links (`.textlink`, wie `woche__weiter`): „Kino nach Stadt“ und „Alle Termine“. Beide Seiten
gibt es und sie sind nach Stadt geordnet bzw. filterbar.

---

## 4. Gemeinsame Regeln, Wiederverwendung, neue Teile

**Für alle drei.**
- Kopfzeile, Logo, Rubrikband, Fuß: keine Zeile ändern.
- Farben nur über die vorhandenen Variablen (`--titan`, `--rot`, `--tinte`, `--grund`, `--flaeche`, `--linie`,
  `--leise`, `--hell`, `--hell-leise`). Kein neuer Farbwert. Seitengrund `#FFFFFF`.
- Jeder Beitrag ist eine Bildkarte aus `tamil_anr_imbild()` bzw. `tamil_grafik_kino()` / `tamil_grafik_termin()`:
  Titel im Bild, Punktbogen aus `tamil_bild()`. Keine Titellisten. Kontext steht neben oder unter der Karte, nie
  statt der Karte.
- Radius `--radius` (10 px) an Karten, `--radius-klein` (6 px) am Auswahlfeld. Randlose Bilder am Handy bleiben
  gerade (wie der Aufmacher heute).
- Kein seitliches Wischen in den neuen Teilen. Die bestehende Reihe „Weitere Meldungen“ (Cover First) bleibt, wie
  sie ist.
- Werbung: Leaderboard über `tamil_leaderboard()` nach den Rubrikkacheln, Billboard nach „Küche“, Fuß und feste
  Handy-Anzeige unverändert. Nichts über dem Cover, nichts im Abschnitt „Tamil in meiner Stadt“.
- Verboten bleiben: farbige Seitenstreifen, Verlaufsschrift, Glas, Schatten, Versalien in Dach- und Fachtiteln,
  Gedankenstriche als Stilmittel, Pillenreihen, Story-Kreise, Zähler 01/02/03, Tamil-Schrift als Schmuck, Laufband.
- Proben nicht indexieren: bei gesetztem `probe` `noindex` und Canonical auf die Startseite; Seiten-Cache nach
  Parameter trennen.

**Wiederverwenden (nichts neu erfinden).**

| Zweck | Vorhanden |
|---|---|
| Bildkarte mit Titel im Bild | `tamil_anr_imbild()` mit `klasse`, `rahmen`, `ebene`, `dach`, `zusatz`, `vorspann`, `titel_stufen`, `sizes`, `eager`, `niedrig` (`inc/anreisser.php`) |
| Bild, Schild „Symbolbild“, Punktbogen | `tamil_bild()`, `tamil_bildwahl()`, `tamil_ist_foto()`, `tamil_leitbild()` (`inc/bildkette.php`, `inc/bausteine.php`); CSS `.rahmen`, `.r43`, `.r169`, `.r83`, `.signatur-ecke`, `.symbolbild` |
| Dachzeile, Titel, Vorspann | `tamil_meta()`, `tamil_titel()`, `tamil_standfirst()`, `tamil_saetze()`, `tamil_saetze_bis()`, `tamil_ganze_saetze()`, `tamil_text()` |
| Kino und Termine | `tamil_kino_filme()`, `tamil_kino_film()`, `tamil_grafik_kino()`, `tamil_grafik_termin()`, `tamil_termin_angaben()`, `tamil_ort_kurz()`, `tamil_staedte_kurz()`, `tamil_site_upcoming_events()`, `tamil_site_event()` |
| Raster | `.innen`, `.oben` (Desktop `1fr 388px`), `.neben.karten`, `.karten--reihe`, Bühne `.kueche__raster` |
| Titel, Links, Felder | `.block-titel`, `.block-kopf`, `.textlink`, Feldstil der Formulare, Filterlogik `[data-filter]` in `app.js` |
| Auswahl, Dubletten, Filmbilder | `tamil_start_auswahl()`, `tamil_seite_beitraege()` (neue IDs dort anmelden) |

**Neu (Vorschlag).**

| Datei / Klasse | Inhalt |
|---|---|
| `inc/proben.php` | `tamil_probe(): string` (nur `cover`, `news`, `community`, sonst leer), `tamil_probe_vorrat()` (lead + P sortiert), `tamil_kontext( int $id, array $opt ): string`, `tamil_zeit_text( int $ts ): string`, `tamil_stadt_namen()`, `tamil_stadt_daten()`, `tamil_kino_termin_text()` |
| `template-parts/home/probe-cover.php`, `probe-news.php`, `probe-community.php` | je der erste Abschnitt; `front-page.php` verzweigt nur an dieser Stelle |
| `template-parts/home/stadt.php` | der Abschnitt aus Kapitel 3 |
| `.titelseite` | Raster von Cover First; `.aufmacher--cover` (Coverformat, Titelgröße), `.aufmacher--klein` (News First) |
| `.r1610`, `.r32` | `aspect-ratio: 16 / 10`, `3 / 2` |
| `.beistueck`, `.beistueck--gross`, `--mittel`, `--flach` | die drei Beistücke (Format und Titelgröße) |
| `.kontext`, `.kontext__angaben` (`<dl>`), `.kontext__satz` | Text neben der Karte in allen Proben |
| `.zeitfolge`, `.zeitfolge__eintrag`, `.zeitfolge__zeit`, `.zeitfolge__eintrag--erste` | News First |
| `.stadt`, `.stadt__kopf`, `.stadt__wahl`, `.stadt__reihe`, `.stadt__fach` (`--kino`, `--termine`, `--geschichten`), `.stadt__spielorte`, `.stadt__leer`, `.stadt__weiter` | „Tamil in meiner Stadt“ |
| `app.js`, Abschnitt „Stadtwahl“; kleines Inline-Skript hinter dem Abschnitt | Filtern, Speichern, Statuszeile |

---

## 5. Prüfliste für die Abnahme

Gemessen mit `node tools/shots.mjs` (390, 820, 1280) und zusätzlich bei 1440; Höhen 844 bzw. 800.

Alle drei
- [ ] Kein seitliches Scrollen und keine Konsolenfehler bei 390, 820, 1280, 1440.
- [ ] Kopf pixelgleich zur heutigen Seite (Vergleich der oberen 160 px bei 390, 180 px bei 1280).
- [ ] Jeder Beitragslink im Probenbereich enthält ein Bild mit Titel im Bild und `.signatur-ecke`
      (`node wordpress/dev/bilder_pflicht.mjs`, Soll 100 %).
- [ ] Nur Farbwerte aus den Tokens (`getComputedStyle` über alle Elemente: keine fremde Farbe); Seitengrund `#FFFFFF`.
- [ ] Größte Schrift ist der Covertitel, höchstens 34 px bei 390 und 44 px ab 1280; zweitgrößte höchstens 24 / 28 px.
- [ ] Sätze am Handy mindestens 18 px; alle Links und das Auswahlfeld mindestens 44 px hoch.
- [ ] Helle Schrift im Bild mindestens 4,5 : 1 an der hellsten Stelle unter jeder Zeile.
- [ ] Karten einer Reihe: Ober- und Unterkante ≤ 1 px Abweichung (`node wordpress/dev/kartenhoehe.mjs`).
- [ ] Radien nur 10 px und 6 px (randlose Handy-Bilder 0).
- [ ] Leaderboard steht direkt nach den Rubrikkacheln; keine Anzeige über dem ersten Beitrag; Billboard, Fuß und
      Handy-Leiste wie auf der heutigen Seite.
- [ ] Mit `prefers-reduced-motion: reduce` kein Übergang; ohne Nutzerhandlung bewegt sich im ersten Bildschirm nichts.
- [ ] Kein Element zeigt ein leeres Etikett („Quelle:“ ohne Wert, „Ort:“ ohne Wert); „Warum das wichtig ist“ kommt
      im HTML nicht vor, solange das Feld fehlt.
- [ ] `?probe=…` trägt `noindex`; ohne Parameter ist die Startseite unverändert (Bildvergleich).

Cover First
- [ ] 390 × 844: Covertitel und Titel von B1 ganz sichtbar ohne Scrollen.
- [ ] 1280 × 800: Cover, B1 und B2 ganz sichtbar (drei Titel; Abweichung vom Brief, Frage 5).
- [ ] Keine zwei Beistücke gleich groß: Flächen B1 > B2 > B3, je mindestens Faktor 1,25; drei verschiedene Formate.
- [ ] Coverfläche mindestens das Vierfache von B1 am Desktop; Covertitel höchstens 3 Zeilen bei 1280, 4 bei 390.
- [ ] Vorspann höchstens 60 Zeichen je Zeile.

News First
- [ ] Zeitfolge streng absteigend nach `datetime`; Uhrzeit nur bei Beiträgen von heute oder gestern.
- [ ] Blocktitel „Heute wichtig“ nur, wenn ein Beitrag das heutige Datum trägt; sonst „Zuletzt erschienen“.
- [ ] 390 × 844: zwei Titel der Zeitfolge ganz sichtbar; 1280 × 800: drei Zeilen und das Cover (vier Titel).
- [ ] Jede Zeile hat Zeit und Satz; Ort und Quelle nur, wenn gepflegt.
- [ ] Coverfläche am Desktop mindestens das 2,5-Fache einer Karte der Zeilen 2 bis 5.

Community First
- [ ] 390 × 844: Abschnittstitel, Auswahlfeld und zwei Kartentitel ganz sichtbar.
- [ ] Aufmacher und alles darunter gleich der heutigen Seite, nur nach unten verschoben.

„Tamil in meiner Stadt“
- [ ] Bedienung nur mit Tastatur: Feld erreichbar, Wahl ändert Inhalt und Titel, Fokus bleibt auf dem Feld.
- [ ] Nach Neuladen steht die gewählte Stadt ohne sichtbaren Wechsel (kein Layout-Sprung, CLS des Abschnitts 0).
- [ ] Es entsteht kein Cookie und keine Anfrage an den Server durch die Wahl; `navigator.geolocation` wird nie
      aufgerufen.
- [ ] Ohne JavaScript: Zustand „Alle Städte“, kein Auswahlfeld, die Links „Kino nach Stadt“ und „Alle Termine“
      sind da.
- [ ] Jede Stadt der Liste zeigt mindestens ein gefülltes Fach; jedes leere Fach zeigt genau den Wortlaut aus 3.5.
- [ ] Keine vergangene Vorstellung, kein vergangener Termin; Beiträge tragen das Datum mit Jahr.
- [ ] Kein Eintrag aus dem Verzeichnis („Musterstadt“), keine Länder als Stadt („Deutschland“).
- [ ] Statuszeile wird nach der Wahl vorgelesen (`aria-live="polite"`).

---

## 6. Offene Fragen an Luis

1. **„Warum das wichtig ist“:** Das Feld gibt es nicht, der Vorspann ist überall der automatische Auszug. Soll die
   Redaktion (oder der Radar) künftig einen eigenen Satz liefern (neues Feld im Plugin)? Bis dahin steht der Auszug
   ohne dieses Etikett.
2. **Dopplung mit „Diese Woche“:** „Tamil in meiner Stadt“ zeigt Kino und Termine, „Diese Woche“ auch. Soll der neue
   Abschnitt „Diese Woche“ ersetzen, wenn eine Probe gewinnt? In den Proben bleiben vorerst beide stehen.
3. **Aktualität:** Im November erschienen neun Beiträge, der neueste vor acht Tagen. News First zeigt dann „Zuletzt
   erschienen“ statt „Heute wichtig“. Ist das gewollt, oder sagt die Redaktion tägliche Beiträge zu?
4. **Orte:** `ort` ist Freitext mit 58 Schreibweisen, `event_land` ist leer. Sollen Redaktion und Radar künftig
   Stadt und Land getrennt pflegen? Ohne das bleibt die Stadtliste eine Zerlegung von Freitext und kennt keine Länder.
5. **Abweichungen vom Brief §10 bei Cover First:** viertes Bildformat (16:10 oder 3:2) und am Desktop drei statt
   vier ganz sichtbare Titel im ersten Bildschirm. Für die Probe in Ordnung?
