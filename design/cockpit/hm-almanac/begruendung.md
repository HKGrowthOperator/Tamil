# Cockpit hm-almanac – Begründung

Redaktions-Cockpit der Linie B „Kalenderblatt“. Produkt-Register: dieselbe Marke wie die Website
(`design/richtungen/hm-almanac/`, Stand 13.11. 20:55: helles Schieferpapier, fast weißer Bogen, Hanken Grotesk auch im
Text, Ziffern in Hanken Grotesk mit Tabellenziffern (IBM Plex Mono nach Kritik cockpits-r1 entfernt), Akzent im Logo-Rot), ruhiger und dichter. Statisches HTML/CSS, erzeugt mit `bauen.py`;
`app.js` nur für „Text kopieren“ im WhatsApp-Entwurf. Schriften selbst gehostet in `schriften/` (OFL).

## Hallmark-Picks

**Hallmark · v2.0.0**

- **Screen** · App-Screens, Scope app, eine Kopfleiste über sechs Bereichen; Arbeitslisten als Tabellen auf dem Bogen, Warteschlangen als Liste links und Vorgang rechts · states: loading (Statistik „heute“ in Buchungen), empty („Zuletzt abgeschlossen“ im Eingang, „Veröffentlicht“ in Social, „Fehler der letzten 7 Tage“ in der Übersicht), error (Abholen fehlgeschlagen im Eingang, Erstattung fehlgeschlagen in Buchungen, Lizenz fehlt im Entwurf), full.
- **Theme** · Almanac, dealt 2/3 (Seed `tamil-deutschsprachiges-online-magazin-der-ff32·6bcf19c0·2026-11-13·r0`), Akzent auf das Logo-Rot umgestimmt, Papier und Textschrift wie die Linie nach Runde 8. Skala fest 1.2 (16 / 19 / 23 / 28 px), am Handy Text 18 px, Bedienelemente 40 px am Desktop und 44 px unter 60rem.
- **Chrome** · nav: Kopfleiste mit Logo und „Redaktion“, Übersicht, Entwürfe, Eingang, Social, Verzeichnis, Buchungen mit Zählern in Mono, „Mehr“ als Ausklapper (Recherche, Warteschlange, Kosten, Quellen, Protokoll, Zeitplan, Schalter, Benutzer), rechts der Radar-Zustand als Text und Abmelden; unter 60rem ein Knopf „Menü“ · footer: eine Zeile, woher die Zahlen stammen.
- **Signature** · der datierte Bogen: jede Arbeitsliste liegt als heller Bogen mit 2-px-Tintenlinie auf dem Schiefer, Ziffern in Mono, die dringendste Zeile zwischen zwei festen Linien mit dem Wort „zuerst“. Im Entwurf wird er zum Prüfbogen: Text links, am Rand je Absatz die Claims und Quellen, Widersprüche an der Stelle, an der sie fehlen.
- **Material** · real: Entwurf 36 / Story 67 mit 19 Claims, drei Quellen, vier Hinweisen und zwei Fassungen; Läufe #1600 bis #1619, Budget, Warteschlange, Zähler (65 neu, 19 Recherche) aus dem Live-Bericht vom 12.11.2026, 18:57; die drei veröffentlichten Beiträge (Diwali in Basel, „Scene“, „Ramayana“) für Social; Regelwerk Fassung 1 · pictures: das Commons-Foto zu rb-67 mit Nachweis, eine gebaute Vorschau der Bildkarte · Beispieldaten: Einsendungen, Social-Stände, Verzeichnis-Einsendungen, Buchungen, Einblendungen und Klicks (spezifiziert, nicht gebaut; Personen und Kunden anonym, Telefon offensichtlich ungültig, E-Mail nur @example.org) · absent: Preise („Preis folgt“), Hashtags (liefert KBS), Link zum Beitrag, Werbemittel-Dateien (gestrichelte Plätze mit Maß).
- **Sweep** · sloplint `--scope app` über http je Seite: 0 FAIL, 0 REFLEX, 0 WARN (vorher 10 FAIL behoben: Fokusring des Sprunglinks, Überlauf eines Knopfs bei 375, Deaktiviert nur über Deckkraft; dazu 1 REFLEX 72 und 2 WARN F19/25) · `tools/shots.mjs`: 21 Aufnahmen, 0 Fehler, 0 Hinweise (kein seitliches Scrollen, keine Konsolenfehler, alle Schriften geladen, keine kleinen Tippflächen) · Finish-Review aus frischem Kontext: nicht gelaufen.

## Seiten

| Datei | Inhalt |
|---|---|
| `uebersicht.html` | „Was auf dich wartet“ nach Dringlichkeit, Stopp-Schalter je Kanal mit „Alles anhalten“ (Grund Pflicht), Budget, Warteschlange, ein Diagramm der Läufe mit Tabelle, leerer Fehlerbereich |
| `entwurf.html` | Entwurf 36 im Zustand **Lizenz fehlt**: Freigabe gesperrt mit Grund, Lizenz-Formular (Lizenz als Fehlerfeld), Vorschlag aus der Commons-Seite, Prüfbogen, Quellen, alle 19 Claims, Text bearbeiten, Kosten und Fassungen |
| `entwurf-freigabe.html` | derselbe Entwurf mit vollständigem Lizenz-Datensatz, Freigeben und Direkt posten aktiv |
| `eingang.html` | Fehler beim Abholen, Filter in der Adresse, fünf Einsendungen (Termin, Beitrag, Kooperation, Werbung, Kontakt), Vorgang mit Agenten-Prüfung (Pflichtfeld fehlt, Dublette zu Story 30), Einsendung wie eingegangen, Übernehmen, Antworten im Mailprogramm |
| `social.html` | Trockenmodus, Karenz-Countdown mit Text und Stoppen, Regelprüfung R1 bis R9, „von Hand entscheiden“, Historie je Kanal, WhatsApp-Entwurf mit Kopieren, Bild und „als gepostet markieren“, Kanal-Schalter, Regelwerk |
| `verzeichnis.html` | Änderung an Ceylon Palace bisher gegen neu mit Übernahme je Feld, Dublettenhinweis Sri Ganesha Hindu Temple gegen Hindutempel, Freigabe |
| `buchungen.html` | Warnung Erstattung, sechs Buchungen in allen Ständen, Prüfung des Werbemittels mit technischer Prüfung, Einblendungen und Klicks (Beispielwerte) mit Ladezustand, Protokoll |

Jede Seite bei 390 und 1280 (dazu 820) in `shots/`.

## Aus der Funktion übernommen

Leiste, Stopp- und Budget-Banner aus `base.html`; Aktionen und Status-Maschine aus `entwurf.html` und datenmodell §6;
Quellen, Claim-Matrix und Fassungen aus `_belege.html`; Lizenz-Felder aus §8; Eingang §12; Verzeichnis §13;
Buchung und Aktiv-Funktion §14; Social, Karenz und Regelwerk §15 und `docs/regeln-social.md`; Schalter §16.
Weggelassen: die Kacheln und das Radar-Bild des alten Dashboards (Runde 5 bis 7: „generisch“), stattdessen Tabelle und
ein Diagramm.

## Abgrenzung

- Gegen Runde 2: kein Creme, keine Serife im Text, eckige Bilder. Gegen Runde 4: Rot nur für den einen gefüllten Knopf,
  Linkunterstreichung, die dringende Zeile und Widersprüche, nie als Fläche.
- Gegen Runde 5 bis 7 und das alte Dashboard: keine Kennzahl-Kacheln, keine Pillen, keine Versal-Labels, keine
  „·“-Metazeilen, keine Seitenstreifen; Zustände als Wort.

## Schwächen

- Die Zuordnung der Claims zu den Absätzen ist aus den Claim-Texten abgeleitet; live muss sie der Faktencheck liefern.
- „Lizenz fehlt“ ist für Entwurf 36 ein Beispielzustand; live hat das Bild einen Commons-Nachweis.
- Eingang, Social, Verzeichnis und Buchungen zeigen Beispieldaten; die Funktionen sind spezifiziert, nicht gebaut.
- Der Karenz-Countdown steht still (kein Skript); live zählt er herunter.
- Die Bildkarte ist eine Vorschau, nicht die gestaltete Social-Karte (folgt laut F4 mit dem neuen Design).
- Am Handy sind Arbeitslisten lang, weil jede Zeile als Block mit Beschriftung steht.
- Das Datumsfeld zeigt das Format des Browsers (in der Aufnahme englisch).
- Eine Prüfung aus frischem Kontext (Finish-Review) ist nicht gelaufen.
- Links in „Mehr“ zeigen auf die Pfade des heutigen Cockpits; diese Screens sind nicht gestaltet.


## Nach Kritik cockpits-r1

- **P1:** IBM Plex Mono ist entfernt, die Schriftdateien sind gelöscht. Ziffern, Code und Diagrammbeschriftungen stehen
  in Hanken Grotesk mit `tabular-nums lining-nums`, wie auf der Website.
- **P3:** „Freigeben“ bei fehlender Lizenz ist jetzt echt `disabled`. Im Markup steht als Kommentar, dass der Server
  jede Freigabe ohne Lizenz-Datensatz ablehnt (K6); der Knopf zeigt die Regel nur an.
