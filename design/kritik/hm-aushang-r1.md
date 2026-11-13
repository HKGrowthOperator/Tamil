# Prüfung hm-aushang, Runde 1
Harte Kriterien: 11 von 15 erfüllt (1 nicht geprüft) · P0: 0 · P1: 7 · P2: 8

Grundlage: `design/brief-v3.md`, `design/linien-auftrag.md`, `abgelehnt.md` (Runden 1–7), Pflichten aus `tamil-marke`.
Gemessen am 13.11.2026 über http://127.0.0.1:8954/richtungen/hm-aushang/ mit `tools/shots.mjs` bei 390/820/1280
(index, artikel, termine, kino, verzeichnis, einreichen, werben, buchen). `begruendung.md` und frühere Kritiken nicht gelesen.

## Erster Eindruck
Kühles Weiß, reines Schwarz, eine Grotesk (Epilogue), Rot nur an den nächsten Terminen: sauber, aufgeräumt, nichts
Lautes und nichts aus Runde 2. Der erste Bildschirm der Startseite ist aber ein Landingpage-Aufmacher (Titel links,
Knopfpaar, Foto rechts, 125 und 240 px Leerraum) mit genau einer Geschichte; das Eigene („Aushang“) beginnt erst
darunter. Die tragende Idee, die große Tagesziffer vor jeder Zeile, ist die Standardregel des Hallmark-Themes „Ink“
und deckt sich mit der Signatur von `hm-eigen`.

## Harte Kriterien

| # | Kriterium (brief-v3, linien-auftrag) | Handy 390 | Desktop 1280 | Ergebnis |
|---|---|---|---|---|
| 1 | Logo unverändert | Bilddatei, 48 px hoch | dto. | erfüllt |
| 2 | Nur Deutsch, keine tamilische Schrift als Schmuck | `tamil_ohne_lang` 0, keine Zierschrift | dto. | erfüllt |
| 3 | Echte Inhalte, nichts erfunden | „Jailer 2 zum Spezialpreis, 15. November, Kloten“ ohne Quelle | dto. | **verletzt** (P1-6) |
| 4 | Bildnachweis an jedem Bild | index, artikel: am Bild | dto. | erfüllt |
| 5 | Fließtext Handy ≥ 18 px (brief-v3: 17) | `--text-md` 1.125rem = 18 px, Zeilenhöhe 1.6 | 18 px | erfüllt |
| 6 | Kontrast AA | aus Tokens gerechnet: ink-2 ca. 13:1, muted (L 44 %) ca. 7:1, Rot (L 50,8 %) ca. 6:1 auf paper | dto. | erfüllt (gerechnet, nicht je Element) |
| 7 | Tippflächen 44 px | Logo 99×40, Monatssprünge 31–41 breit, Fuß „Kino“ 38×44, Checkbox 24×24, Dateifeld 226×35 | – | **verletzt** (nach Bogen E als P2 geführt) |
| 8 | Kein seitliches Scrollen | 0 px, alle 8 Seiten | 0 px (auch 820) | erfüllt |
| 9 | `prefers-reduced-motion` | nicht geprüft | – | offen |
| 10 | Keine Dachzeilen, Versal-Labels, „·“-Metazeilen | keine gesehen | keine gesehen | erfüllt |
| 11 | Keine gleich großen Kartenraster, Verlaufkacheln, Seitenstreifen | keine | keine | erfüllt |
| 12 | Nichts aus Runden 1–7 wiederholt | ein Cover mit einer Geschichte; „diese Woche“-Band | dto. | **verletzt** (P1-1, P1-3) |
| 13 | Schriften selbst gehostet, OFL im Ordner | `schriften/epilogue-*.woff2`, `Epilogue-OFL.txt` | dto. | erfüllt |
| 14 | Seitenliste vollständig | alle 11 Seiten plus Danke-Zustand vorhanden | dto. | erfüllt |
| 15 | Keine Konsolenfehler, keine leeren Bilder | 0 / 0 | 0 / 0 | erfüllt |

## Paarvergleich

**Runde 2 (r2-community-magazin-1280) gegen index-1280:**
- R2 zeigt im ersten Bildschirm einen Aufmacher und fünf weitere Geschichten mit Bild; Aushang zeigt eine Geschichte
  und zwei Knöpfe, der Rest liegt ab y = 1015. R2 ist dichter und wirkt eher nach Nachrichtenseite.
- Aushang ist sichtbar kühler und härter gesetzt: Grund nahezu weiß statt Sand, Tinte schwarz statt Braungrau,
  1-px-Linie in Schwarz unter dem Kopf, keine bunten Rubrikpunkte, Bildecken 6 statt ca. 12 px. Der Rückfall in Runde 2
  ist gebannt.
- R2 trägt Datum, Ort und Rubrik klein über dem Titel; Aushang zieht das Datum als große Ziffer nach links. Das ist der
  einzige Unterschied in der Gliederung einer Meldungszeile.

**Runde 4 Raster (r4-raster-1280) gegen index-1280:**
- Keine rote Riesenschrift, keine Versalien in der Navigation, keine verzerrten Schnitte: Epilogue ist normalbreit,
  der Rückfall in Runde 4 („breite Schrift“) liegt nicht vor.
- Gemeinsam ist das rote Datum als Bildzeichen: R4 setzt „14.11.“ groß und rot oben links, Aushang „15“ in Rot vor
  jeder nächsten Zeile (ca. 36–44 px). Kleiner und ruhiger, aber dieselbe Geste.
- R4 rahmt alles in rote Linien; Aushang nutzt graue Haarlinien zwischen den Zeilen. Wertiger und ruhiger.

**Andere Linie dieser Runde (`hm-eigen`, nur der Stempel oben im CSS gelesen):** Signatur dort „die Tageszeile
(Ziffer, Titel, Ort), Ziffer rot nur bei Terminen an Sonntagen und Festtagen“. Aushang: Ziffer in Epilogue 700 vor
jedem datierten Eintrag, die nächste in Rot, darunter Ort. Für einen Betrachter derselbe Aufbau (siehe P1-4).

Die Nachrichtenmarken-Bilder habe ich aus Sparsamkeit nicht nebengelegt; brief-v3 misst nicht mehr gegen sie.

## Befunde

### P0
keine (0 Konsolenfehler, 0 leere Bilder, 0 px Überlauf auf allen 8 Seiten bei 390/820/1280).

### P1
1. **Erster Bildschirm mit nur einer Geschichte** (index, 390 und 1280; Verbot „Cover mit nur einer Geschichte“,
   Runde 4). 1280×800: Aufmacher-Bereich von y 118 bis ca. 1015, darin 125 px Luft über dem Bild und 240 px unter der
   Bildzeile; „Was als Nächstes aushängt“ beginnt erst bei y 1015. 390×844: Titel, Vorspann, zwei Knöpfe, Bild bis
   y 920, keine zweite Geschichte. *Abhilfe:* Aufmacher-Stage auf Inhaltshöhe begrenzen (Luft oben und unten 32–48 px),
   bei 1280 die ersten drei Aushangzeilen neben oder direkt unter den Aufmacher in den ersten Bildschirm, bei 390 die
   erste Zeile über die Falz.
2. **Landingpage-Bausteine** (Baukasten, Bogen B). Aufmacher mit Knopfpaar „Beitrag lesen“ (schwarz gefüllt) und
   „Per WhatsApp schicken“ (umrandet), also ein „Weiterlesen“-Knopf statt verlinkter Schlagzeile; dazu der CTA-Kasten
   „Termin einreichen“ rechts im Kopf und auf jeder Unterseite dasselbe Split-Banner (H1 links, Vorspann und Knöpfe
   rechts: werben „Platz buchen / Werbung anfragen“, verzeichnis „Eintrag vorschlagen“). Das ist der Aufbau einer
   Produkt-Landingpage. *Abhilfe:* Schlagzeile als Link, WhatsApp als schlichter Textlink wie in den Aushangzeilen,
   „Termin einreichen“ als Textlink in der Navigation, Unterseitenköpfe einspaltig mit Liste direkt darunter.
3. **„Diese Woche“-Band** (index 1280, ca. y 3120–3570; Verbot seit Runden 5–7): Abschnitt „Tamilisches Kino diese
   Woche“ auf vollbreiter grauer Fläche mit drei Spalten und rotem „Läuft“. *Abhilfe:* Kino ohne Flächenwechsel als
   Aushangzeilen in der Hauptspalte, Überschrift ohne „diese Woche“ (z. B. „Im Kino“ mit Stand-Datum).
4. **Signatur ist Theme-Standard und nicht eigen** (alle Seiten mit Daten). Schrift (Epilogue 700/400), Tinte ohne
   Buntheit und die Regel „a figure … a step larger than the head beside it“ stammen aus dem Hallmark-Theme
   `references/themes/ink.md`; dessen Beschreibung („A notice printed in plain black … the way a well-run community desk
   does“) ist die Idee „Aushang“ selbst. Dieselbe Tagesziffer-Zeile trägt `hm-eigen`, eine rote Datumsziffer trug
   R4 Raster. Gegen brief-v3 („gemacht, nicht generiert; nur tamil.de“) ist das der schwächste Punkt. *Abhilfe:* ein
   zweites, nicht aus dem Theme abgeleitetes Merkmal, das nur tamil.de hat (z. B. Spielort und Uhrzeit als eigener
   Zeilenkopf beim Kino, Festkalender nach Tempeljahr), oder die Datumszeile deutlich anders als `hm-eigen` lösen.
5. **Datumsblock verrutscht** (termine 1280, erster Bildschirm; index, Nachrichten, Community, Küche): Ziffer bei
   x 65, Monat und Wochentag bei x 125 und ca. 35 px tiefer, die beiden Teile stehen treppenförmig in zwei Spalten und
   lesen sich nicht als ein Datum. *Abhilfe:* `.ziffer` und Monat/Wochentag als ein Block in Spalte 1, Monat 4–8 px unter
   der Ziffer, linksbündig auf derselben Kante.
6. **Nicht belegter Termin** (index und termine, Zeile 2): „‚Jailer 2‘ zum Spezialpreis im Kino Claudia“, Sonntag
   15. November, Kloten, „Übermorgen“. Die einzige Quelle im Repo (`prototyp/content/events.json`, Slug
   `jailer-2-kino-claudia-kloten`) nennt 16. bis 19. Oktober und „Preis laut Veranstalter“; „Spezialpreis“ und der
   15. November stehen in keiner der vorgegebenen Inhaltsquellen. *Abhilfe:* Quelle nachweisen oder Zeile entfernen.
7. **Kino-Seite beantwortet „welcher Film läuft wo“ nicht** (kino 390, erster Bildschirm): Jede Stadtzeile (Berlin,
   Bremen, Chemnitz, Dortmund …) wiederholt wortgleich „Scene / Deutschland, in 11 Kinos“ und ein rotes „Läuft“;
   Kinoname, Adresse und Zeitraum fehlen. *Abhilfe:* je Stadt Kino, Film und Spieltage; Anzahl „11 Kinos“ einmal oben;
   „Läuft“ streichen, weil es für alle Zeilen gilt.

### P2
1. **Tippflächen unter 44 px** (390): Logo-Link 99×40 auf allen Seiten; Monatssprünge auf termine „Juli“ 31, „Mai“ 32,
   „Juni“ 38, „April“ 41 px breit; Fußlink „Kino“ 38 px breit; Checkbox einreichen 24×24; Dateifeld 35 px hoch;
   Bildnachweis-Links 39 px hoch. *Abhilfe:* `min-height: 44px` am Logo, `min-width: 44px` und Innenabstand an
   Monatslinks und Fußlinks, Checkbox-Label als Tippfläche ≥ 44 px.
2. **Geringe Dichte und Leerraum** (termine, verzeichnis, werben bei 1280): Terminzeilen ca. 190 px hoch, Titelspalte
   ca. 310 von 1150 px, ca. 570 px leer bis zum Status; im ersten Bildschirm von termine nur gut zwei Termine.
   Unterseitenköpfe mit ca. 100–200 px Luft; auf verzeichnis steht die H1 vertikal mittig, der Vorspann oben, die
   Kanten fluchten nicht. *Abhilfe:* Zeilen auf ca. 110 px, Status direkt hinter den Ort, Köpfe oben bündig.
3. **Ziffer mit zwei Bedeutungen** (index): bei Terminen Ereignisdatum in der Zukunft, bei Nachrichten und Community
   das Veröffentlichungsdatum („28 Mai“, „21 März“). Der Aushang wirkt dadurch veraltet und der Leser kann Termin und
   Beitrag nicht unterscheiden. *Abhilfe:* große Ziffer nur für Termine, Beiträge mit kleinem Datum unter dem Titel.
4. **Knopfreihen als Filter** (verzeichnis Art: Alle/Business/Dienstleister/Verein/Tempel; einreichen Land:
   Deutschland/Österreich/Schweiz): umrandete Knöpfe mit 6 px Rundung in einem grau hinterlegten, gerahmten Kasten;
   nah an der Knopfreihe aus Runde 3. *Abhilfe:* Radios als Liste mit Linien oder ein Auswahlfeld, Filter ohne Kasten.
5. **Legende im Buchungskalender widersprüchlich** (buchen 390, Schritt 2): „grau hinterlegt sind die gebuchten Tage“,
   darüber „Alle späteren Tage sind frei“; 18.–30. November sind grau. *Abhilfe:* „grau: Ihr gewählter Zeitraum“.
6. **Anrede und Kennzeichnung uneinheitlich**: kino „Ihre Stadt“, Hausanzeige auf index „Dein Fest im Kalender“;
   die eigene Aufforderung „Event melden“ ist als „Anzeige“ gekennzeichnet. *Abhilfe:* eine Anrede (Sie), Eigenhinweis
   nicht als Anzeige auszeichnen.
7. **Termin aus wartendem Entwurf** (index, termine): „THADAM 2026 … 13. Dezember, Bern“ steht nur als wartender
   Radar-Entwurf 4 in `docs/redaktion/rueckblick-2026.md`, nicht freigegeben. *Abhilfe:* als Platzhalter kennzeichnen
   oder weglassen, bis freigegeben.
8. **Ungestaltetes Dateifeld** (einreichen 390): Browser-Standard „Choose File / No file chosen“ in einem Rahmen von
   35 px Höhe. *Abhilfe:* eigenes Label „Bild wählen“ als 48-px-Knopf, Dateiname darunter.

### P3
1. Aufmacher-H1 `--text-display` erreicht ca. 50 px bei 1280 (bis 54 px): über der alten Grenze aus `tamil-marke`
   (44 px); in brief-v3 kein Kriterium, zur Kenntnis.
2. `prefers-reduced-motion` nicht geprüft (Budget); Übergänge nur an Links und Knöpfen gesehen.

## Was trägt
- Artikel am Handy: 18 px Fließtext bei Zeilenhöhe 1.6, Vorspann 19 px, WhatsApp vor dem Bild, Bildnachweis direkt
  unter dem Foto; ruhig und gut lesbar.
- werben: maßstäbliche Zeichnungen der sechs Werbeformate mit „Preis folgt“ als gestricheltem Platzhalter und
  Hinweis „Preise liefert KBS“; ehrlich und eigenständig.
- Farbe und Ordnung: kühles Weiß, schwarze Tinte, Rot nur an nächsten Terminen und aktiver Navigation; keine
  Dachzeilen, keine Versal-Labels, keine Kacheln; verzeichnis als lineare Tabelle (Name, Art, Ort).

## Bedienbarkeit (nur zur Information)

| Nielsen | 0–4 | Satz |
|---|---|---|
| 1 Systemstatus | 3 | „Übermorgen“, „In 8 Tagen“ und Stand-Daten zeigen Aktualität. |
| 2 Sprache der Nutzer | 3 | Klar und deutsch; „Läuft“, „Scene“ ohne Zusammenhang. |
| 3 Kontrolle | 3 | Zurück und Menü vorhanden, Buchung schrittweise. |
| 4 Konsistenz | 2 | Ziffer bedeutet mal Termin, mal Veröffentlichung; Du und Sie gemischt. |
| 5 Fehlervermeidung | 3 | Nicht buchbare Tage gesperrt und erklärt. |
| 6 Wiedererkennen | 3 | Navigation stets sichtbar, aktive Rubrik rot. |
| 7 Effizienz | 2 | Wenige Termine je Bildschirm am Desktop. |
| 8 Ästhetik, Minimalismus | 3 | Ruhig, aber viel ungenutzter Raum. |
| 9 Fehler erkennen | 2 | Formularfehler nicht geprüft; Kalenderlegende widersprüchlich. |
| 10 Hilfe | 3 | Feldhinweise im Einreichformular. |
