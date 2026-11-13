# Cockpit hm-eigen „Tagesblatt“: Begründung

Stand 13.11.2026. Redaktions-Cockpit der Linie A nach `design/linien-auftrag.md`, gestaltet mit Hallmark im
Produkt-Register (`theme.mjs scaffold --custom --scope app`, Flow „App screens“). Grundlage sind die Tokens und Schriften
der Website-Linie `design/richtungen/hm-eigen/`; Funktion aus `news_radar/web/templates/` und
`docs/spezifikation/datenmodell.md` (§6, §8, §12 bis §16), Social nach `docs/regeln-social.md`.

## Idee

Dieselbe Marke wie das Tagesblatt, aber als Werkzeug: Jede Aufgabe steht an ihrem Tag. Die Tagesziffer erscheint klein im
Kopf (heute, 13) und als Spalte vor jeder Arbeitsliste; sonst ruhige Linien, eine Seitenleiste, Tabellen vor Kästen.

## Hallmark-Picks

| Achse | Wahl |
|---|---|
| Screen | Übersicht als Tagesliste mit Kennzahlenzeile und Betriebsspalte (Stopp-Schalter, Budget, Radar); Entwurf mit Belegen je Absatz und Freigabe rechts; Eingang, Verzeichnis, Buchungen als Liste mit geöffnetem Vorgang darunter; Social nach Karenz, „von Hand“, WhatsApp, Historie |
| Schale | Kopfleiste (Logo, Tagesziffer, Radar-Stand, Abmelden); Seitenleiste mit zwölf Zielen in „Arbeit“ und „Betrieb“, unter 60rem ein Menü in der Kopfleiste; Banner für angehaltene Kanäle auf jeder Seite |
| Papier | Jasminweiß `oklch(97.6% 0.007 120)`, Seitenleiste und Felder `paper-2`, Banner `paper-3` |
| Tinte | Blattgrün-Schwarz `oklch(21% 0.022 155)` |
| Rot | Logo-Rot `oklch(50.5% 0.175 25)` nur für den einen Primärknopf je Vorgang, die Markierung der aktuellen Auswahl und den Fokus; „angehalten“, „offen“, „fehlt“ in `--color-halt` als Wort, nie als Fläche |
| Zweite Farbe | Bananenblatt-Ton als `--color-ok` nur für „läuft“, „bestätigt“, „in Ordnung“ |
| Schrift | Golos Text für alles (400, 600); Rethink Sans 700 nur für Köpfe, Kennzahlen und die Tagesziffer. Feste Stufen im Verhältnis 1,2, keine fließenden Größen |
| Signatur | die Tagesliste: links die Ziffer des Tages (Termin, Ereignis oder Eingang), rechts Titel, eine Zeile Stand, eine Aktion |
| Zustände | voll; leer (Eingang „Kooperation“, Buchung ohne Zahlen); Fehler (Lizenz fehlt, Erstattung fehlgeschlagen, Dublette, abweichendes Werbemittel, Quelle mit Fehler); Karenz; angehalten. Kein Ladezustand: das Cockpit rendert auf dem Server |
| Verhalten | nur `app.js` für „Text kopieren“ (WhatsApp); ohne Skript bleibt der Text sichtbar und markierbar |

## Screens (je 390 und 1280, geprüft auch bei 820)

| Datei | Inhalt |
|---|---|
| `uebersicht.html` | Kennzahlen; wartende Entwürfe (3 Radar, 62 Rückblick) nach Tag; Eingang, Social, Verzeichnis und Buchungen als Tageslisten; Stopp-Schalter aller acht Kanäle mit „Alles anhalten“ (Grund Pflicht); Budget Tag und Monat; Radar-Lauf |
| `entwurf.html` | Entwurf 7 (Deepavali, Story 30): Text mit Claims C1 bis C7 je Absatz und Belegstatus, Quellen Q1 bis Q3, Hinweise vor der Freigabe, Bild mit vollständigem Lizenz-Datensatz, Freigabe mit gesehenem Stand, Bearbeiten und Fassungen als Aufklapper |
| `entwurf-lizenz-fehlt.html` | derselbe Entwurf im Zustand „Lizenz fehlt“: Meldung, Freigeben gesperrt mit Grund, Formular „Lizenz eintragen“ (Herkunft, Rechteinhaber, Lizenz ohne NC/ND, Version, Ablauf, Lizenz-Adresse, Umfang, soziale Netze, Bildnachweis, KI), dazu „erneut abrufen“ und „Bildkarte nehmen“ |
| `eingang.html` | Einsendungen nach Art (Filter in der Adresse), Hinweise des Agenten; geöffnet: Termin mit Angaben, Prüfung, Dublettenhinweis, Entwurf „Angaben des Einsenders, ungeprüft“, übernehmen, erledigt, ablehnen, Spam, Antwort nur per `mailto:`; Leerzustand |
| `social.html` | Regelwerk Fassung 1 im Trockenmodus; Karenz mit Restzeit, Text ändern, Stoppen; „von Hand entscheiden“ mit verletzter Regel (R2, R4); WhatsApp-Entwurf mit Kopieren, Bild herunterladen, „als gepostet markieren“; Historie je Kanal |
| `verzeichnis.html` | Einsendungen; geöffnet: neuer Eintrag mit Dublettenhinweis auf V-0031, Tabelle bisher gegen neu mit Entscheidung je Feld, Premium nur durch den Administrator, Freigabe als Änderung oder neuer Eintrag |
| `buchungen.html` | Buchungen mit Stand, Einblendungen, Klicks und Warnung; geöffnet: Werbemittel in Prüfung mit technischer Prüfung (Handy-Format abweichend), Freigeben oder Ablehnen mit Grund, Preis als Platzhalter |

Daten: Titel, Texte und Hinweise der Entwürfe sind echt (`docs/redaktion/rueckblick-2026.md`,
`design/inhalte/rueckblick/rueckblick.json`); Personen („A. Beispiel“), Firmen („Beispiel Reisen GmbH“), Adressen
(„Beispielstraße 1“), Nummern (`+49 000 …`), Beträge und Zählwerte sind erfunden und so benannt, E-Mail nur
`@example.org`. Der Fuß jeder Seite sagt das. Neu bauen: `python3 design/cockpit/hm-eigen/bauen.py`.

## Prüfung

- `sloplint --genre editorial --scope app` statisch und gerendert über `http://127.0.0.1:8945/cockpit/hm-eigen/…`
  (7 Adressen): **0 FAIL, 0 REFLEX**, 12 WAIVED (49b: Titel von Einsendungen umbrechen in Tabellen auf zwei Zeilen,
  Ausnahme im Stempel), 7 WARN nur aus dem Datei-Aufruf ohne Server (Schrift lädt über `file://` nicht; über
  `http://` geladen, keine Warnung).
- `node tools/shots.mjs` bei 390, 820, 1280 für alle sieben Seiten: **0 Fehler**, kein seitliches Scrollen, keine
  Konsolenfehler, keine leeren Bilder, keine fehlenden Schriften; einzige kleine Tippfläche ist der versteckte Sprunglink
  „Zum Inhalt“. Erste Bildschirme liegen in `shots/` (`-k0.png`), dazu `shots/bericht.json`.
- Fließtext des Entwurfs 18 px, Bedienung 16 px am Desktop und 18 px am Handy; Bedienelemente 40 px am Desktop, 44 px
  unter 60rem; Tinte auf Papier über 14:1, Rot auf Papier 6:1.

## Abgrenzung

Keine Kacheln oder Kartenraster (das alte Dashboard hatte fünf Kacheln und ein Radar-Bild), keine Pillen und Badges
(Runde 3), keine rosa Hinweiskästen (Meldungen stehen auf `paper-2` mit einer Linie), kein Gold-Knopf, keine
Versal-Labels, keine „·“-Metazeilen, keine Gedankenstriche, keine Statuspunkte, Rot nie als Fläche außer dem einen
Primärknopf.

## Schwächen

- Die Tagesziffer in Listen ist bei Vorgängen ohne Datum (Kinowoche) eine Notlösung mit Text statt Ziffer.
- Die Übersicht ist am Handy lang; wer nur den Stopp-Schalter sucht, muss scrollen oder über das Banner gehen.
- Am Handy steht das Lizenz-Formular unter dem ganzen Text; ein Sprunglink in der Meldung hilft, ersetzt aber keine
  eigene Reihenfolge für schmale Bildschirme.
- Werbemittel sind als beschriftete Flächen statt als Bilder gezeigt, weil es kein echtes Werbemittel gibt.
- Unabhängige Prüfung aus frischem Kontext steht aus.
