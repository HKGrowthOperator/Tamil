# Tamil.de – HTML-Prototypen der fünf Vorlagen (Designkonzept v2 „Radar“)

Vertrag HKG-2026-TML-V-001, Teil A: **A.1.1 Designkonzept**, **A.1.2 Korrekturschleifen**, **A.1.3 Responsive**,
**A.1.4 Vorlagen** (Startseite, Kategorie, Artikel, Events, Kontakt). Die Prototypen sind statisches HTML im eigenen
Tamil.de-Design, gebaut aus den echten Inhalten der alten Seite und aus echten Radar-Daten. Sie sind die Vorlage für
die Theme-Anpassung (Child-Theme eines Premium-Magazin-Themes) und die Grundlage für die zwei Korrekturschleifen mit
dem Auftraggeber.

Zum Durchklicken (Handy und Desktop): **privater Artifact-Link im Pull Request / Claude-Dokument.**

## Regenerieren

```bash
python tools/export_site.py --no-media                      # einmalig: Export der alten Seite nach export/
python prototyp/build.py snapshot                           # Beiträge bereinigen, auswählen, Bilder laden (→ content/posts.json, static/img/)
python prototyp/build.py build                              # dist/  (80 Seiten)
python prototyp/build.py shots                              # shots/ (390 / 820 / 1280 px, Playwright)
python prototyp/build.py artifact                           # dist-artifact/ (Startseite ohne Dokumentgerüst, für claude.ai-Artifact)
python -m pytest tests/test_prototyp.py -q
```

`build` und `shots` brauchen kein Netz; `snapshot` lädt die verwendeten Bilder einmalig von tamil.de.
`content/posts.json` und `static/img/` sind eingecheckt, damit der Build ohne Export reproduzierbar ist.

## Seiten (dist/)

| Vorlage | Dateien | Besonderheiten |
| --- | --- | --- |
| Startseite | `index.html` | Hero (3 neueste mit großem Bild), Top-Themen (Redaktion), Neueste 6, Rubrik-Zeilen je Kategorie, **Kinotermine-Widget** aus Radar-Daten, Event-Teaser, Rezept der Woche, Leerzustand Sport, Newsletter |
| Kategorie | `kategorie-<slug>.html` (8) | Kino als Schaufenster mit Filter-Chips und Kinotermine-Karte, Sport als Leerzustand, Kultur und Küche per Stichwort aus Nachrichten ergänzt |
| Artikel | `artikel-<slug>.html` (71), `kino-jailer-2-kinotermine.html` | Standfirst, Byline, Teilen-Leiste (WhatsApp zuerst), In-Article-Werbeplatz nach dem 2. Absatz, YouTube erst nach Klick; Varianten **Rezept** (Zutaten/Schritte) und **Kinotermine** (Spielorte aus `news_radar.render.render_kino_liste`) |
| Events | `events.html`, `event-<slug>.html` (6) | Liste nach Monat + Monatsraster, Filter DE/AT/CH und Kategorie, Detailseite mit Fakten, Tickets, Teilen, Karten-Platzhalter, Quelle |
| Kontakt | `kontakt.html` | Kontaktkarte, Formular, **Werben** mit den 5 Werbeplätzen, **Event einreichen**, **Mitmachen: Leser-Reporter** (Text der alten Seite), FAQ |
| Sonderseiten | `production.html`, `tv.html`, `ueber-uns.html`, `impressum.html`, `datenschutz.html`, `service-fsk.html` | Aus der alten Seite übernommen (siehe unten); `seite.html` ist die Vorlage für Textseiten |
| Design-System | `design-system.html` | Farben mit Kontrast, Schrift, Abstände, Buttons, Badges, Karten, Formulare, Werbeplätze in Originalgröße, Icons |

Drei Breakpoints: ≤ 600 px (Drawer, 1 Spalte, Mobile-Sticky-Werbeplatz), 601–1023 px (Scroll-Navigation, 2 Spalten),
≥ 1024 px (volle Navigation, 3 Spalten, Sidebar 300 px sticky). Schriften (Fraunces mit Kursiv und den Achsen SOFT/WONK,
Schibsted Grotesk, Noto Serif Tamil) liegen lokal in `static/fonts/`, keine externen Aufrufe beim Laden.

## Handschrift (v2)

- **Farben:** Nacht-Indigo `#0E1226`, Kumkum-Rot `#C8102E`, Manjal-Gelb `#E8B923`, Blatt-Grün `#1F7A4D`, Papier `#FAFAF8`.
  Die Triade Nacht/Kumkum/Manjal ist bewusst kein Creme-Serif-Standard: Kumkum und Manjal (Kurkuma) sind die Farben
  tamilischer Rituale, das Indigo ist der Nachthimmel hinter dem Radar.
- **Schrift:** Fraunces (variabel, WONK/SOFT für die leicht eigenwilligen Buchstaben, Kursiv für Akzente) für Titel und
  Zahlen, Schibsted Grotesk (eine Zeitungsschrift) für Lauftext und Bedienelemente. Das tamilische Wort ist die
  Überschrift jedes Abschnitts, der deutsche Begriff steht kursiv daneben („சினிமா *Kino*“).
- **Das eine prägende Element:** die **Radar-Bühne** auf der Startseite: eine Punktkarte von Deutschland, Österreich und
  der Schweiz (`radar_map.py` rastert die Länderumrisse aus `content/geo/`), ein rotierender Sweep und pulsierende Blips
  an den Orten, an denen der News-Radar diese Woche etwas gefunden hat, dazu das Protokoll „zuletzt erfasst“ und drei Zahlen.
- **Bewegung, gezielt:** die Aufmacher-Schlagzeile steigt Wort für Wort auf (einmal, beim Laden), der Schlagzeilen-Ticker
  unter der Navigation läuft, der Kino-Radar zählt seine Kinos hoch und lässt die Spielorte als Filmstreifen durchlaufen,
  Artikel haben einen Lesebalken. Alles stoppt bei `prefers-reduced-motion`.
- **Kolam-Marke:** eine kleine Schleifenlinie um fünf Punkte neben der Wortmarke, als Vorschlag bis die Logo-Datei vorliegt.
  Dasselbe Punktraster liegt hinter der Radar-Bühne, im Footer und auf den automatisch erzeugten Tamil.de-Bildkarten.

## Übernahme von tamil.de (Phase 2b)

Die alte Seite (WordPress 6.2.14, Theme „Observer“) wurde am 17.10. nur lesend geprüft; `tools/export_site.py --meta-only`
schreibt den Befund nach `export/site_meta.json` und lädt Logo und Werbebanner nach `export/brand/`. Was übernommen ist:

| Element der alten Seite | Im Prototyp |
| --- | --- |
| Logo `kkbslogo.png` (300 × 121, dunkles Rot auf hellem Grund) | Masthead, Drawer und Footer (`img/logo.png`); Wortmarke und Kolam-Marke bleiben als Vorschlag im Design-System |
| Claim aus dem SEO-Titel | Claim und Meta-Beschreibung |
| Hauptmenü Home · News · Entertainment · EVENTS · Blog · Küche · KINO | Nachrichten · Entertainment · Events · Community (vorher „Blog“) · Küche · Kino · Sport · Kultur · Kontakt; 301-Regeln in `redirects.csv` |
| Top-Menü Über · Impressum · Datenschutz | Topbar und Footer-Legal auf echte Seiten |
| Ticker „Top-Themen“ (Tag `ticker`) | v2-Ticker, Tag `ticker` hat Vorrang vor den neuesten Beiträgen |
| Header-Werbung 728 × 90 → Gravity Club, Sidebar 336 × 280 → Olyyn | Werbeplätze 01 und 02 zeigen die echten Banner mit Link und Kennzeichnung „Werbepartner“ (`werbung_live` in `site.json`) |
| WhatsApp-Kanal, Instagram `@tamil_de` | Topbar und Footer; Facebook/YouTube als „ausstehend“ markiert |
| Startseiten-Slider „POWERED BY TAMIL.DE Production“ (A.R. Rahman, Ilaiyaraaja, Anirudh „Live mit dir!“, Santhosh Narayanan 2025) | Block **Tamil.de Production** auf der Startseite + `production.html` mit Konzerten, Service-Texten der Anirudh-Tour (Saalplan, Eventim, Einlass) und Ticketmaster-Link |
| Küche-Block mit Kottu Roti, Payasam, Biryani, Dosa | Alle Rezepte in Küche (die 120-Wörter-Regel gilt dort nicht) |
| Seite `/tv/` mit zwei HLS-Streams (beide derzeit 404) | `tv.html` mit Player-Platzhalter je Sender, Status „Stream wird angefragt“ |
| Seite `/fsk/` | `service-fsk.html` unter Kino |
| Seite `/reporter/` (Leser-Reporter, bis 100 € Honorar) | Abschnitt „Mitmachen“ auf der Kontaktseite |
| Seiten `/maya/` (M.I.A.-Film) und 2018-Rückblick | Beiträge in Kino bzw. Community mit Bildkarte |
| `ueberuns`, `datenschutzerklaerung` (2016), `impressum` (leer) | `ueber-uns.html`, `datenschutz.html` mit Hinweis „Stand 2016“, `impressum.html` als Platzhalter mit Anschrift aus dem Vertrag |
| Seite `/kino/` (Jailer 2, manuell) | ersetzt durch den Kinotermine-Beitrag des Radars; 301 auf die Kino-Rubrik |

**Nicht übernommen:** Mitgliederbereich (Ultimate Member, 2019; 301 auf die Startseite), englische `privacy-policy`,
leere Altlasten (`fb`, `location`, `gd-*`, `backup*`), Kopierschutz-Plugin, Theme-Schriften Ubuntu/Viga (im Design-System
als „Vorher“ notiert). Tag `TT` (116 Beiträge) wird nicht übernommen, Bedeutung beim Auftraggeber erfragen.

## Was echt ist, was Beispiel

**Echt:** alle Beiträge, Teaser und Bilder stammen aus dem Export der alten tamil.de (533 Beiträge, 1.573 Medien);
die Kinotermine zu „Jailer 2“ (9 Kinos in DE/CH/AT) aus CineStar, kinoheld, Eventfrog, Cineplexx und megaplex.at,
Stand 16.10.2026; die Events aus tamilswiss.ch, Eventfrog und kinoheld; Logo, Menüs, Ticker, Werbebanner (Gravity Club, Olyyn), Social-Links,
die Texte der Seiten Über uns, Datenschutz, FSK, Leser-Reporter und TV sowie die Production-Plakate von der alten
tamil.de; die Anschrift laut Vertrag.

**Als Beispiel markiert** (gestrichelter Gold-Rahmen „Beispiel“): Telefon, E-Mail, WhatsApp-Nummer, Rezept-Fakten
(Zeit, Portionen), Autorenbox, FAQ-Texte, Platzhalterkarten in Sport, Mediadaten-PDF. Datumsangaben sind um 708 Tage
in die Gegenwart verschoben (neuester echter Beitrag: 06.11.2024), jede Seite sagt das in der Fußzeile.

## Lückenliste für den Auftraggeber

Was der Export nicht hergibt und vor dem Relaunch geklärt werden muss:

1. **Autoren** – alle 533 Beiträge laufen auf Benutzer 1, keine Profile. Prototyp: „Redaktion Tamil.de“. Benötigt: Namen, Kurzprofil, Foto je Autor:in.
2. **Bildrechte und Alt-Texte** – `alt_text` ist bei allen Medien leer, Bildnachweise fehlen. Prototyp: Alt-Text = Titel, Credit „Foto: Tamil.de“. Benötigt: Nachweise oder Freigabe für die Übernahme.
3. **Rezepte** – fünf Rezepte aus dem Altbestand (Kottu Roti, Payasam, Biryani, Dosa, Kothu Rotti), aber ohne Zutatenlisten, Zeit und Portionen. Benötigt: strukturierte Rezepte oder Freigabe, dass die Redaktion sie nachträgt.
4. **Sport und Kultur** – keine Beiträge im Altbestand. Prototyp: Sport leer, Kultur per Stichwort aus Nachrichten. Entscheidung: Sport zum Start zeigen oder ausblenden?
5. **Kino-Altbestand** – rund 80 Drei-Wort-Beiträge mit YouTube-Video (unter 120 Wörter) werden nicht übernommen; 10 Kritiken stammen aus 2018–2020.
6. **Events** – im Altbestand 6 Beiträge (Anirudh 2024). Aktuelle Events kommen aus Schweizer Quellen; für DE/AT fehlen Veranstalter-Quellen (Eventim, Vereine, Tempel).
7. **Schlagworte** – unbrauchbar („Tamil“ 221×, „TT“ 116×, „ticker“ 26×). Beim Import wird ein neues Tag-Set angelegt.
8. **Kontaktdaten, Impressum, Datenschutz** – Telefon/E-Mail im Angebot sind Platzhalter; Impressum-Seite der alten tamil.de ist leer, Datenschutzerklärung von 2016. Benötigt: vollständiger Impressumstext (Vertretung, Register, USt-ID, § 18 MStV), aktuelle Datenschutzerklärung.
9. **Logo und Mediadaten** – Logo nur als 300 × 121-PNG von der alten Seite. Benötigt: Vektor oder große Datei, Variante für dunklen Grund; Mediadaten/Preise für die Werbeplätze (Button „folgt“).
10. **Social-Media-Kanäle** – WhatsApp-Kanal und Instagram von der alten Seite übernommen; Facebook und YouTube unbekannt (im Prototyp „ausstehend“).
11. **Versalien-Titel und Kritik-Format** – Titel in Großbuchstaben und Teaser „Pluspunkte: + …“ werden beim Import normalisiert; Redaktion prüft Stichproben.
12. **Tote Bilder und Einbettungen** – 75 Beiträge mit `http://`-Bildern externer Seiten (entfernt), 83 iframes (YouTube erst nach Klick, Rest entfernt).
13. **Werbeverträge** – Gravity Club (Leaderboard) und Olyyn (Sidebar) laufen auf der alten Seite. Benötigt: Laufzeit, Format, Preis, ob sie in den Relaunch übergehen.
14. **TV-Streams** – beide HLS-Adressen (Santhora TV, Tamil Business TV) antworten mit 404. Benötigt: aktuelle Stream-Adressen oder Entscheidung, die TV-Seite abzuschalten.
15. **Partner-Logos** – das Plugin `best-logo-slider` ist aktiv, Logos wurden nicht gefunden. Benötigt: Liste der Partner oder Streichung.
16. **Mitgliederbereich** – Ultimate Member wird nicht übernommen. Benötigt: Freigabe, die Nutzerdaten der alten Seite zu löschen (DSGVO), und ob Mitglieder informiert werden sollen.
17. **Tag „TT“** – 116 Beiträge, Bedeutung unklar. Benötigt: Erklärung oder Freigabe zum Verwerfen.

## Zuordnung zum Code

`build.py` nutzt aus dem News-Radar `news_radar.render` (HTML-Bereinigung, Kinoliste) und `news_radar.wordpress.slugify`;
`cards()` erzeugt die Tamil.de-Bildkarten für Events ohne Foto mit `news_radar.images.branded_card`. `radar_map.py` baut
die DACH-Punktkarte. Die Werbeplätze, Kategorien, Top-Themen, Kontaktdaten, Städte-Koordinaten und Radar-Meldungen stehen
in `content/site.json`, die Events und Kinotermine in `content/events.json`.

Die Freigabe-App des News-Radars (`news_radar/web/`) trägt dieselbe Handschrift als dunkles Cockpit: Seitenleiste mit
Live-Status und Countdown bis zum nächsten Lauf, Board-Feed mit Tastaturkürzeln (J/K, F, A, Enter), Quellen-Radar im
Dashboard, Editor mit Papier-Vorschau.
