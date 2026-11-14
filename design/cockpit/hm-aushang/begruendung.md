# Cockpit hm-aushang „Aushang“: Begründung

Stand 13.11.2026. Redaktions-Cockpit der Linie C nach `design/linien-auftrag.md`, mit Hallmark im Produkt-Register
(`theme.mjs scaffold ink --scope app`, Flow „App screens“). Farben, Schrift und Idee kommen aus
`design/richtungen/hm-aushang/`. Die Funktionen stammen aus `news_radar/web/templates/`, `docs/spezifikation/datenmodell.md`
(§6, §8, §12 bis §16) und `docs/regeln-social.md`.

## Idee

Auf der Website ist tamil.de das Schwarze Brett: Jede datierte Sache hängt mit ihrem Datum als Kopf aus, und nur die
nächste ist rot. Im Cockpit wird daraus die Frage, die eine Redaktion zuerst stellt: **Was geht als Nächstes von selbst
hinaus, und kann ich es noch anhalten?** Diese Antwort steht auf jeder Seite in der Aushangzeile unter der Kopfleiste,
mit Uhrzeit in Logo-Rot, „Ansehen“ und „Stoppen“. Jede Arbeitsliste führt mit ihrer Frist (Uhrzeit, Ereignistag,
Starttag). Sonst gibt es Haarlinien, Tabellen und schwarze Schrift auf kühlem Weiß.

## Picks

**Hallmark · v2.0.0 · scope: app**

- **Screen** · Arbeitslisten als „Brett“ (Zeilen mit der Frist als Kopf, Titel, eine Zeile Stand, eine Aktion), der geöffnete Vorgang darunter mit Entscheidung rechts · states: voll, leer (Kooperation), Fehler (Lizenz fehlt, Dublette, abweichendes Werbemittel, Erstattung fehlgeschlagen, Datum in der Vergangenheit), Karenz, Trockenmodus, angehalten; kein Ladezustand, weil der Server rendert
- **Theme** · Ink (by request), Palette der Linie unverändert (Papier `oklch(99.4% 0.002 250)`, Tinte `oklch(16% 0 0)`, Logo-Rot `oklch(50.8% 0.177 25.6)`); Radius 6, keine Pillen, kein IBM Plex Mono
- **Shell** · Kopfleiste: Logo, „Redaktion“, sechs Arbeitsziele als Reiter mit Zahl, „Betrieb“ (Stopp-Schalter, Kosten, Quellen, Protokoll, Zeitplan, Benutzer) als Aufklapper, Abmelden; unter 60rem ein Menü. Keine Seitenleiste: sechs Ziele brauchen keine
- **Signal** · Logo-Rot nur als Schrift: die nächste Frist, die aktuelle Seite (Unterstrich im Reiter), „angehalten“, „Lizenz fehlt“, „Datum nicht belegt“, Warnungen, der Stoppen-Knopf als Umriss. Nie als Fläche. Der Primärknopf ist schwarz
- **Signature** · die Aushangzeile („Als Nächstes geht hinaus: 14:20 …“) und die Frist als Kopf jeder Arbeitszeile in Epilogue 700, die nächste in Rot
- **Type** · Epilogue (OFL, selbst gehostet, Lizenz in `schriften/`), 400/600/700; feste Skala im Verhältnis 1,2 ab 17 px, unter 60rem 18 px; Entwurfstext 18 px bei höchstens 65 Zeichen; keine fließenden Größen, keine Versalien, keine Dachzeilen
- **Density** · Bedienelemente 40 px am Desktop, 44 px unter 60rem; Tabellen vor Kästen; ein Behälter für Meldungen (`paper-2` mit Haarlinie, Fehler mit roter Linie auf Weiß)
- **Behavior** · nur `app.js` für „Text kopieren“ (WhatsApp); ohne Skript bleibt der Text sichtbar und markierbar. Filter stehen in der Adresse (`?art=`, `?stand=`). Abschnitte ohne Bewegung, Übergänge nur 120 ms auf Farbe

## Screens (je 390 und 1280, geprüft auch bei 820)

| Datei | Inhalt |
|---|---|
| `uebersicht.html` | Kennzahlenzeile; „Was als Nächstes geschieht“ (Karenz 14:20, Kinoliste 16:00, Ruhezeit 22:00, Prüffrist Werbemittel); 3 Radar- und 6 Rückblick-Entwürfe nach Frist mit den echten Hinweisen vor der Freigabe; neu Eingegangenes; Stopp-Schalter aller acht Kanäle mit Grund als Pflicht; Budget Tag und Monat; Radar |
| `entwurf.html` | Entwurf 7 (Story 30, Deepavali): Titel, Vorspann, vier Absätze mit ihren Aussagen C1 bis C7, Beleg und Stand je Absatz, Quellen Q1 bis Q3, Freigabe mit den echten Hinweisen und dem gesehenen Stand, Bild mit vollständigem Lizenz-Datensatz, Bearbeiten und Fassungen als Aufklapper |
| `entwurf-lizenz-fehlt.html` | derselbe Entwurf nach einem Upload ohne Datensatz: Meldung „Lizenz fehlt“, Veröffentlichen gesperrt mit Grund, Formular „Lizenz eintragen“ (Herkunft, Rechteinhaber, Lizenz ohne NC/ND, Version, Lizenz-Adresse, Quelle, Umfang, Ablauf, Recht für soziale Netze, Bildnachweis, KI), „Bildkarte nehmen“, „Bild neu suchen lassen“. Unter 60rem steht die Freigabe vor dem Text |
| `eingang.html` | Filter nach Art in der Adresse; fünf Einsendungen; geöffnet: Termin mit allen Feldern aus §12, Prüfung des Agenten mit Dublettenhinweis, Entwurf mit Vermerk „Angaben des Einsenders, ungeprüft“, Übernehmen, Erledigt, Ablehnen, Spam, Antwort nur per `mailto:`; leerer Zustand „Kooperation“ |
| `social.html` | Trockenmodus nach Regelwerk Fassung 1; Karenz mit Frist, Text ändern, Stoppen, Regelprüfung R1 bis R9, Vorschau 4:5 mit Logo-Leiste und Bildnachweis; „von Hand entscheiden“ mit verletzter Regel; WhatsApp-Entwurf mit Kopieren, Bild herunterladen, „als gepostet markieren“; Historie je Kanal |
| `verzeichnis.html` | Einsendungen; geöffnet: neu eingereichter Eintrag mit Dublettenhinweis, „als Änderung oder neuer Eintrag“, Tabelle bisher gegen neu mit „öffentlich“ und Entscheidung je Feld, Premium nur durch den Administrator |
| `buchungen.html` | drei Buchungen nach Starttag mit Stand; geöffnet: Werbemittel maßstäblich (halbe Größe), Handy-Format abweichend, Angaben, Entscheidung mit Pflichtgrund und Hinweis auf die automatische Erstattung; Warnung „Erstattung fehlgeschlagen“; Einblendungen und Klicks je Tag |

Daten: echt sind Titel, Hinweise, Wortzahlen und Texte der Entwürfe (`docs/redaktion/rueckblick-2026.md`,
`rueckblick.json`) und die Bildnachweise. Beispieldaten sind Personen („A. Beispiel“), Firmen („Beispiel Reisen GmbH“),
Adressen, Nummern (`+49 000 …`, `+41 00 …`), die Uhrzeiten des Tages, Beträge, Zählwerte, Einsendungs- und
Buchungsnummern sowie die Annahme, Entwurf 17 sei um 14:10 Uhr freigegeben worden. E-Mail nur `@example.org`, Preise
„Preis folgt (KBS)“. Der Fuß jeder Seite sagt das. Neu bauen: `python3 design/cockpit/hm-aushang/bauen.py`.

## Prüfungen

- `sloplint --genre editorial --scope app` über 7 Dateien plus `cockpit.css` und die 7 Adressen
  `http://127.0.0.1:8948/cockpit/hm-aushang/…`: **0 FAIL, 0 REFLEX**, 8 WAIVED (22: Tinte ohne Farbton wie auf der Website
  der Linie; 49b: Titel in Listen und der Link „Wikimedia Commons“ bei 320 px auf zwei Zeilen). 8 WARN: 7 × „fallback
  font“ nur aus der Darstellung der Dateien ohne Server (über http lädt Epilogue, die Adressen melden nichts); 1 × F7,
  weil alle Eingabefelder dieselbe Form haben, was gewollt ist.
- `node tools/shots.mjs` bei 390, 820, 1280 für alle sieben Seiten über http: **21 Aufnahmen, 0 Fehler**, kein
  seitliches Scrollen, keine Konsolenfehler, keine leeren Bilder, keine fehlenden Schriften. Hinweise auf kleine
  Tippflächen nennen nur den versteckten Sprunglink und die 20-px-Kreise der Auswahlfelder; deren Beschriftung ist
  jeweils 44 px hoch und die eigentliche Tippfläche. Aufnahmen in `shots/` (`-k0.png` erster Bildschirm), dazu `shots/bericht.json`.
- Kontrast (aus den OKLCH-Werten gerechnet): Tinte auf Papier rund 19:1, `ink-2` rund 14:1, `muted` rund 7,8:1, Logo-Rot auf Papier rund 6:1.

## Abgrenzung

Kein Dashboard aus Kacheln (das alte Cockpit hatte fünf Kacheln), keine Pillen, Badges oder Statuspunkte (Runde 3),
keine rosa Hinweiskästen, kein Rot als Fläche (Runde 4), keine Seitenleiste, keine Versal-Labels, keine Dachzeilen,
keine „·“-Metazeilen, keine Gedankenstriche. Die Linie zeigt sich in der Aushangzeile, der Frist als Kopf und der
roten nächsten Sache, nicht in Schmuck.

## Schwächen (je ein Satz)

- Die Aushangzeile ist am Handy sechs Zeilen hoch und schiebt den Seitenkopf unter den ersten Bildschirm.
- Die Übersicht ist am Handy lang; der Stopp-Schalter liegt weit unten und ist sonst nur über „Betrieb“ im Menü erreichbar.
- Die Frist als Kopf passt schlecht zu Vorgängen ohne echte Frist (Kinoliste „seit gestern“, Ereignistage im Rückblick sind vergangen).
- Die Karenz zeigt einen festen Stand („noch 8 Min.“); eine laufende Uhr bräuchte Skript und bleibt dem Server überlassen.
- Werbemittel sind als beschriftete Rahmen statt als Bilder gezeigt, weil es kein echtes Werbemittel gibt.
- Die Prüfung aus frischem Kontext (Hallmark § 6) steht aus.
