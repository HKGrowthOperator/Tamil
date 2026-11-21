# Cockpit hm-terrazzo „Terrazzo“ (Linie D): Begründung

Stand 13.11.2026. Redaktions-Cockpit der Linie D nach `design/linien-auftrag.md`, gestaltet mit Hallmark im
Produkt-Register (`theme.mjs scaffold terrazzo --scope app`, Flow „App screens“). Grundlage sind Farbweg und Idee der
Website-Linie `design/richtungen/hm-terrazzo/`; Funktion aus `news_radar/web/templates/`,
`docs/spezifikation/datenmodell.md` (§6, §8, §12 bis §16) und `docs/regeln-social.md`.

Nach Hinweis der Koordination (Kritik der Website-Linie D) ohne Syne und ohne JetBrains Mono: eine Familie, Onest;
Köpfe Onest 600, Ziffern und Kennungen Onest mit `tabular-nums`. Keine rosa Flächen (`--color-accent-soft` ist aus den
Tokens entfernt), keine Seitenstreifen, kein dunkles Band.

## Idee

Dieselbe Fuge wie auf der Website, als Arbeitsordnung: Jeder Vorgang liegt in zwei ungleichen Feldern, getrennt durch
2 px Tinte. Links steht, was vorliegt (Text, Einsendung, Werbemittel, alter Eintrag gegen neuen), rechts, was der Radar
dazu geprüft hat, und darunter die eine weiße Entscheidungskarte mit hartem Versatz. Listen sind Tabellen, nie Karten.

## Hallmark-Picks

| Achse | Wahl |
|---|---|
| Screen | Übersicht: wartende Vorgänge als Tabelle links, Betrieb (Stopp-Schalter, Budget, Radar) rechts; Entwurf: Absatz links, seine Aussagen rechts, Prüfung und Freigabe in der schmalen Spalte; Eingang, Verzeichnis, Buchungen: Liste über die volle Breite, darunter der geöffnete Vorgang in zwei Feldern; Social: Karenz und „von Hand“ links, WhatsApp-Entwurf rechts, Historie darunter |
| Schale | Kopfleiste wie der Masthead der Website: Logo mit „Redaktion“, Radar-Stand, Abmelden; eine Zeile Arbeit (sechs Ziele mit Anzahl) links, Betrieb rechts hinter einer Haarlinie; 2 px Tintenfuge darunter; unter 60rem ein Menü. Banner für angehaltene Kanäle auf jeder Seite |
| Papier | Zement `oklch(96.6% 0.004 250)`, Felder und Banner `paper-2`, ausgewählte Zeile `paper-3`, Eingaben und Karten `plate` |
| Tinte | `oklch(19% 0.012 260)`, Bedienelemente in Tinte |
| Rot | Logo-Rot `oklch(50.8% 0.177 25.6)` nur für aktiven Navigationspunkt, Kennung der ausgewählten Zeile, Pflichtstern, Fokus; Fehlerzustände („Lizenz fehlt“, „angehalten“, „Dublette“) als Wort in `--color-error`, nie als Fläche |
| Schrift | Onest allein (400, 500, 600), feste Stufen 1,2; Fließtext des Entwurfs 18 px, Bedienung 16 px am Desktop, 18 px am Handy |
| Signatur | die Fuge zwischen Vorgang und Prüfung mit der Entscheidungskarte darunter |
| Range | Spezifikationstabelle (Kennung, Titel, Stand); Datensatz als zweispaltige Liste; Auswahl als randscharfe, aneinanderstoßende Zellen (Filter im Eingang, „neu/bisher“ je Feld im Verzeichnis, Social-Recht im Lizenz-Formular); Werbemittel als maßstabsgetreue Rahmen |
| Zustände | voll; leer (`eingang-kooperation.html`); Fehler (Lizenz fehlt, Dublette, Werbemittel weicht ab, Erstattung fehlgeschlagen, Quellen mit Fehler); Karenz; angehalten (Verzeichnis); Trockenmodus; Freigeben gesperrt. Kein Ladezustand: das Cockpit rendert auf dem Server |
| Verhalten | nur `app.js` für „Text kopieren“ beim WhatsApp-Entwurf; ohne Skript bleibt der Text sichtbar und markierbar. Kein Inline-Script, kein Inline-Stil |

## Screens (je 390 und 1280, geprüft auch bei 820)

| Datei | Inhalt |
|---|---|
| `uebersicht.html` | sieben wartende Vorgänge aller Arten; die nächsten fünf Rückblick-Entwürfe mit „Vor der Freigabe“ wörtlich aus dem Bericht; Stopp-Schalter der sieben Kanäle mit Grund, „Alles anhalten“ mit Pflichtgrund; Budget Tag und Monat; Radar-Lauf |
| `entwurf.html` | Entwurf 7 (Deepavali, Story 30): Titel, Vorspann, Bild mit vollständigem Lizenz-Datensatz, vier Absätze mit Aussagen C1 bis C6 und Belegstand, Quellen Q1 bis Q5, Bearbeiten und Fassungen als Aufklapper, Hinweise vor der Freigabe, Faktencheck, Freigabe mit gesehenem Stand |
| `entwurf-lizenz-fehlt.html` | derselbe Entwurf im Zustand „Lizenz fehlt“: Meldung (K6), Formular „Lizenz eintragen“ (Herkunft, Rechteinhaber, Lizenz ohne NC/ND, Ablauf, Quellseite, Umfang, soziale Netze, Bildnachweis, KI), „Erneut abrufen“, „Bildkarte nehmen“; Freigeben gesperrt mit Grund |
| `eingang.html` | Filter nach Art als Zellen, Liste mit Agenten-Hinweisen; geöffnet Termin T-0142: Angaben des Einsenders (ungeprüft), Prüfung (Dublette, Datum, Zusammenfassung), Übernehmen, Erledigt, Ablehnen, Spam, Antwort nur per `mailto:` |
| `eingang-kooperation.html` | Leerzustand des Filters Kooperation |
| `social.html` | Regelwerk Fassung 1 im Trockenmodus; Karenz mit Restzeit, Text ändern, Stoppen; „von Hand entscheiden“ mit verletzter Regel (R2, R4); WhatsApp-Entwurf mit Kopieren, Bildkarte, „als gepostet markieren“; Historie aller Kanäle |
| `verzeichnis.html` | Einsendungen; geöffnet VE-0012: bisher (V-0004) gegen neu mit Wahl je Feld, Dublettenhinweis, Berechtigung, Freigabe als Änderung oder neuer Eintrag; Premium nur durch den Administrator |
| `buchungen.html` | sechs Buchungen mit Stand, Einblendungen, Klicks, Warnung; geöffnet B-0004: Werbemittel maßstabsgetreu, Handy-Format weicht ab, Zahlung, „Preis folgt“, Freigeben oder Ablehnen mit Grund (löst Erstattung aus) |

Daten: Titel, Texte, Bild und Hinweise der Entwürfe sind echt (`design/inhalte/rueckblick/rueckblick.json`,
`docs/redaktion/rueckblick-2026.md`, die drei Radar-Entwürfe 54, 4, 5); die Aussagen C1 bis C6 sind aus dem Text des
Entwurfs abgeleitet, die Quellenliste Q1 bis Q5 ist ein Beispiel. Personen (A./B./C. Beispiel), Firmen, Adressen,
Nummern (`+49 000 …`), Beträge, Zählwerte und Kennungen sind erfunden, E-Mail nur `@example.org`; der Fuß jeder Seite
sagt das. Neu bauen: `python3 design/cockpit/hm-terrazzo/bauen.py` vom Repo-Root.

## Prüfung

- `sloplint --genre editorial --scope app` über `http://127.0.0.1:8947/cockpit/hm-terrazzo/…` (8 Adressen) mit
  `cockpit.css`: **0 FAIL, 0 REFLEX, 0 WARN**, 19 WAIVED (49b: Titel von Vorgängen umbrechen in Tabellen, Ausnahme
  im Stempel). Statisch über alle acht HTML-Dateien und `cockpit.css`: **clean**. Der Datei-Aufruf ohne Server meldet
  nur, dass die Schrift über `file://` nicht lädt; über `http://` keine Warnung.
- `node tools/shots.mjs` bei 390, 820, 1280 für alle acht Seiten (24 Aufnahmen, `shots/`): **0 Fehler**, kein
  seitliches Scrollen, keine Konsolenfehler, keine leeren Bilder, Schrift geladen. Kleine Tippflächen nur der
  versteckte Sprunglink und die unsichtbaren Radio- und Kontrollkästchen, deren Beschriftung die 44 px große Fläche ist.
- Bedienelemente 40 px am Desktop, 44 px unter 60rem; Links in Tabellen und Datensätzen am Handy 44 px hoch.
- Kontrast aus den Token-Werten: Tinte auf Papier 16,7:1, gedämpftes Grau 6,7:1, Logo-Rot auf Papier 5,8:1.

## Abgrenzung

Kein Kachel-Dashboard (das alte hatte fünf Kacheln), keine Karten für Listen, keine Pillen oder Badges (Runde 3),
keine rosa Hinweiskästen (Meldungen stehen auf `paper-2` mit einer Linie oben), keine Statuspunkte, keine Versal-Labels,
keine „·“-Metazeilen, kein dunkles Band, keine Seitenstreifen; die einzige senkrechte Linie ist die Fuge zwischen den
Feldern über die volle Höhe.

## Schwächen (je ein Satz)

- Mit nur einer Familie trägt allein das Gewicht die Hierarchie; ob Köpfe in Onest 600 neben der Website (falls sie bei einer zweiten Schrift bleibt) als dieselbe Marke lesen, entscheidet die Überarbeitung der Linie.
- Die Fuge ist am Handy nur noch eine waagrechte 2 px Linie zwischen gestapelten Feldern; die Ordnung Vorgang gegen Prüfung geht dort in die Reihenfolge über.
- Die Kopfleiste braucht am Handy drei Zeilen (Logo, Radar-Stand, Menü) vor dem Banner; der erste Bildschirm zeigt deshalb erst ab etwa der Hälfte Arbeit.
- Die Tabellen werden am Handy zu Blöcken mit „Feld: Wert“; das ist lesbar, aber länger als nötig, besonders „bisher gegen neu“ im Verzeichnis.
- Die Quellen Q1 bis Q5 im Entwurf sind Beispielnamen ohne Adresse; die echten Belege liegen nur im Radar.
- „Text kopieren“ ist das einzige Skript; die Karenz-Restzeit läuft nicht mit, sie steht als feste Zeit da.
- Das Werbemittel ist als gestrichelter Rahmen gezeichnet, nicht als Bild; ein echtes Werbemittel liegt nicht vor.
