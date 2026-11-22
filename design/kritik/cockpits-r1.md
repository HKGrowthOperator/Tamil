# Prüfung Cockpits, Runde 1 (hm-eigen, hm-almanac, hm-aushang, hm-terrazzo)

Stand 13.11.2026, unabhängige Prüfung ohne `begruendung.md` und ohne frühere Kritiken. Auf Anweisung der Hauptsitzung
vorzeitig abgeschlossen. **Prüftiefe ist ungleich:**

- **hm-eigen:** vollständig geprüft. Alle sieben Screens als Gliederung aus dem HTML gelesen, Übersicht bei 390 und
  1280 angesehen, Werkzeuge gelaufen.
- **hm-almanac, hm-aushang, hm-terrazzo:** Es liefen nur die Werkzeuge (shots, sloplint), dazu die Schriften und ein
  Textabgleich der Pflichtinhalte und Sperren im HTML. **Ich habe bei diesen drei keine Aufnahme selbst angesehen**,
  also gibt es keine Aussage zu Lesbarkeit, Dichte, Tabellen am Handy und zur Frage „eigenes Werkzeug oder
  Template“. Die Zahl der Befunde ist dort unvollständig und mit hm-eigen nicht vergleichbar.

Harte Kriterien, je Cockpit dieselben sieben. Grundlage sind Brief v3 (Lesbarkeit) und der Linien-Auftrag
(Pflichtinhalte): (1) kein seitliches Scrollen bei 390/820/1280 · (2) keine Konsolenfehler, keine leeren Bilder ·
(3) sloplint `--scope app` ohne FAIL · (4) Tippflächen ≥ 44 px · (5) keine Schrift von der Verbotsliste ·
(6) alle Pflichtinhalte vorhanden · (7) Freigabe bei „Lizenz fehlt“ gesperrt.

| Cockpit | Harte Kriterien | P0 | P1 | P2 | P3 | Prüftiefe |
|---|---|---|---|---|---|---|
| hm-eigen | 7 von 7 | 0 | 2 | 6 | 3 | vollständig |
| hm-almanac | 6 von 7 (5 verletzt) | 0 | 1 | 0 | 1 | nur Werkzeuge und Textabgleich |
| hm-aushang | 6 von 7 (4 verletzt) | 0 | 0 | 1 | 1 | nur Werkzeuge und Textabgleich |
| hm-terrazzo | 6 von 7 (4 knapp verletzt), 6 nicht abschließend | 0 | 0 | 2 | 1 | nur Werkzeuge und Textabgleich |

Messwerkzeuge: `node tools/shots.mjs` mit `--kacheln` auf `http://127.0.0.1:8954/cockpit/<slug>/*.html` (Bilder und
`bericht.json` im Scratch-Ordner `kritik-cockpit/<slug>/`). Sloplint lief mit `--scope app` und je einem `--url` pro
Seite. Ein erster Lauf mit allen Adressen hinter einem einzigen `--url` endete in HTTP 404 und zählt nicht.
Nebenwirkung: Sloplint schreibt seine Aufnahmen nach `design/cockpit/<slug>/.hallmark/shots/` und hat die dort
liegenden Bilder ersetzt. Den Ordner `hm-terrazzo/.hallmark/`, den erst dieser Lauf angelegt hat, habe ich wieder
entfernt.

---

## hm-eigen („Tagesblatt“)

### Messwerte

| Messung | Wert |
|---|---|
| shots.mjs | 21 Aufnahmen (7 Screens × 390/820/1280), 0 Fehler, Überlauf 0, keine leeren Bilder, keine Konsolenfehler |
| Tippflächen < 44 px | nur der Sprunglink „Zum Inhalt“ (1 × 1, versteckt bis zum Fokus; Absicht, kein Befund) |
| sloplint `--scope app`, über URL | 0 FAIL, 0 REFLEX; 12 WAIVED (49b, Titel in Tabellen umbrechen, im Stempel begründet) |
| sloplint, über Datei | 7 WARN „Schrift nicht geladen“. Das liegt nur an `file://`, über die URL sauber. |
| Schriften | Rethink Sans (Köpfe), Golos Text (Text). Zwei Familien, keine auf der Verbotsliste oder der impeccable-Ausschlussliste. |
| Grundschrift | Bedienung 16 px am Desktop, 18 px unter 40rem; Prosa 18 px (`--text-prosa: 1.125rem`) |
| Seitenlänge 390 | Übersicht 5406 px, Entwurf 4530 px, Lizenz fehlt 5904 px |
| Farbe | kühles Papier oklch(97.6% 0.007 120), Tinte grünlich-dunkel, Logo-Rot nur für „angehalten“, die Gefahrknöpfe und die aktuelle Navigation |

### Pflichtinhalte

| Inhalt | Befund |
|---|---|
| Stopp-Schalter | vorhanden: Tabelle aller acht Kanäle mit Stand, wer und seit wann; „Alles anhalten“ mit Grund als Pflichtfeld; Hinweis „Wieder einschalten darf nur admin“. Banner „Angehalten: Instagram und Facebook“ mit Grund oben auf jeder Seite. |
| Budget | vorhanden: Tag und Monat mit Grenze, Balken, Hinweis auf 80 und 100 Prozent |
| Entwurf mit Claims und Belegen je Absatz | vorhanden: unter jedem Absatz C1 bis C7 mit Status (bestätigt, offen, Hintergrund) und Quelle Q1 bis Q3; Quellenliste mit Art und Rechten; Faktencheck-Summe |
| Lizenz-Datensatz | vorhanden: Herkunft, Rechteinhaber, Lizenz mit Link, Umfang, „Soziale Netze: nein, dort die Bildkarte“, KI, Quelle; Hinweis auf dasselbe Bild in Story 49 |
| „Lizenz fehlt“ mit Formular | vorhanden: Warnung oben mit Sprung zum Formular; Formular mit allen Feldern aus §8 und `social` ja/nein; „Freigeben“ ist `disabled` und mit `aria-describedby` begründet |
| Eingang mit Agentenprüfung | vorhanden: Filter je Art, Tabelle mit Hinweisen, Vorgang mit Angaben des Einsenders, Entwurf mit Vermerk „ungeprüft“, Prüfung (Pflichtfelder, Datum, Ort, Dublette mit Link), Übernehmen, Erledigt, Ablehnen, Spam, Antwort per `mailto:`; leerer Zustand „Kooperation“ |
| Social | vorhanden: Karenz mit Restzeit und „Stoppen“, „Von Hand entscheiden“ mit Regel als Grund, WhatsApp-Entwurf mit „Text kopieren“, „Bild herunterladen“ und „Als gepostet markieren“, Historie je Kanal mit Fassung des Regelwerks |
| Verzeichnis alt gegen neu, Dublette | vorhanden: Hinweis „mögliche Dublette von V-0031“ mit Begründung, Vergleichstabelle bisher/Einsendung mit Wahl je Feld; „Als Änderung“ oder „Als neuen Eintrag freigeben“ |
| Buchungen mit Prüfung des Werbemittels | vorhanden: Liste mit Stand, Einblendungen und Klicks; technische Prüfung je Datei (Maße, Zieladresse, Zahlung); Entscheidung mit Grund |

### Befunde

**P0:** keine.

**P1**

1. **Buchungen, alle Breiten, Entscheidung W-2026-0007, Knopf „Ablehnen“.** Ein Klick löst laut Seite die
   automatische volle Erstattung aus („Bei Ablehnung wird voll erstattet und die Tage werden frei“). Es gibt keine
   Bestätigung, und das Feld „Grund bei Ablehnung“ ist kein Pflichtfeld, sondern schon vorbefüllt. Eine Geldbewegung,
   die sich nicht zurücknehmen lässt, ist so mit einem Fehlklick ausgelöst; nach Hallmark (App-Screens) braucht eine
   zerstörende Aktion Bestätigung oder Rücknahme. **Vorschlag:** Grund als Pflichtfeld ohne Vorbefüllung, dazu ein
   zweiter Schritt „Ablehnen und 0,00 € erstatten“ mit Betrag und Firma. „Ablehnen“ räumlich vom Freigabeknopf
   trennen.
2. **Buchungen, alle Breiten, Knopf „Werbemittel freigeben“.** Der Knopf ist aktiv, obwohl die technische Prüfung
   direkt daneben „abweichend“ meldet (Handy 320 × 100 statt 300 × 250). Damit geht ein Werbemittel im falschen Format
   mit einem Klick live. Das widerspricht der Prüfung „Maße des Platzes“ aus §14 und ist anders gelöst als bei „Lizenz
   fehlt“, wo gesperrt wird. **Vorschlag:** bei „abweichend“ sperren wie bei der Lizenz, mit Begründung über
   `aria-describedby`, oder freigeben nur mit ausdrücklicher Übersteuerung (Häkchen „Format trotzdem annehmen“ und
   Grund ins Protokoll).

**P2**

3. **Entwurf, alle Breiten, Freigabe-Spalte.** „Freigeben“ ist aktiv und veröffentlicht sofort, obwohl drei Zeilen
   darüber „Offen: Berlin ohne Datum, nicht belegt (C3)“ steht. Laut Spezifikation ist das erlaubt, versehentlich
   freigeben lässt es sich trotzdem leicht, denn „Freigeben“, „Zurückstellen“ und „Ablehnen“ stehen ohne Abstand
   untereinander. **Vorschlag:** Solange ein Kern-Claim „offen“ oder „Widerspruch“ ist, vor „Freigeben“ ein Häkchen
   „Offene Punkte gelesen“ verlangen; „Ablehnen“ mit Abstand oder hinter einer Aufklappe.
4. **Lizenz fehlt, alle Breiten, Formular „Lizenz eintragen“.** Der Knopf „Bei Commons erneut abrufen“ liegt im
   selben Formular wie die Pflichtfelder (Rechteinhaber, Lizenz, Bildnachweis) und hat kein `formnovalidate`, anders
   als „Bildkarte nehmen“. Der Browser blockiert den Abruf, solange die Felder leer sind, also genau dann, wenn man ihn
   braucht. **Vorschlag:** `formnovalidate` ergänzen oder den Abruf als eigenes Formular über das Eingabeformular
   setzen.
5. **Social, alle Breiten, WhatsApp-Entwurf.** Für denselben Beitrag (Vaani Vizha) nimmt die Karenz-Fassung die
   Bildkarte, „weil das Recht für soziale Netze nicht eingetragen ist“. Der WhatsApp-Entwurf bietet aber das Foto
   `rb-33.jpg` zum Herunterladen an. Das widerspricht Regel R4 und lädt dazu ein, das Foto ohne Recht zu posten.
   **Vorschlag:** Auch im WhatsApp-Entwurf gilt die Bildkarte, solange `social` nicht „ja“ ist; das Foto nur mit
   eingetragenem Recht anbieten.
6. **Social, alle Breiten, „Von Hand entscheiden“, Zeile R2 (Politik).** „Trotzdem vorbereiten“ schickt ein heikles
   Thema mit einem Klick zurück in den Automatik-Weg, ohne Grund und ohne Hinweis auf eine zweite Person (§6 nennt den
   Hinweis „vor der Freigabe eine zweite Person lesen lassen“). **Vorschlag:** Grund als Pflichtfeld (ins Protokoll),
   Hinweis auf die zweite Person, Knopftext „Für Instagram und Facebook vorbereiten“ statt „Trotzdem“.
7. **Eingang, alle Breiten, Vorgang E-0412.** „Ablehnen“ und „Spam“ sind beide als Gefahr gekennzeichnet, stehen direkt
   nebeneinander unter „Übernehmen“ und wirken ohne Bestätigung. Laut Status-Maschine gibt es keinen Weg zurück, und
   bei Spam wird nach 7 Tagen gelöscht. **Vorschlag:** „Spam“ hinter „Weitere Aktionen“ legen oder eine
   Rücknahme-Meldung für einige Sekunden anbieten („Rückgängig“).
8. **Übersicht, 390.** Stopp-Schalter, Budget und Radar-Stand kommen erst nach allen Listen, etwa vier Bildschirme
   tief (Seite 5406 px). Oben steht nur das Banner mit „Schalter ansehen“. Für einen Notschalter ist das am Handy weit.
   **Vorschlag:** unter 60rem Stopp und Budget vor die Listen stellen oder im Kopf einen festen Sprung „Stopp“
   anbieten.

**P3**

9. **Übersicht, Seitenleiste gegen Kennzahlenreihe.** „Social 3“ in der Navigation steht neben „Social, von Hand 2“
   in der Kennzahlenreihe, und „Buchungen 2“ neben „Werbemittel prüfen 1“. Die Zähler meinen Verschiedenes, und das
   steht nirgends. **Vorschlag:** gleiche Zählweise oder den Zähler benennen („3 offen“).
10. **Übersicht, Budget.** „$1.38 von $5.00“ hat englischen Dezimalpunkt in einer deutschen Oberfläche. **Vorschlag:**
    „1,38 $ von 5,00 $“ bzw. „US-Dollar“.
11. **Übersicht, 1280, Gesamtbild.** Seitenleiste, Kennzahlenreihe mit fünf Zahlen und rechte Spalte sind die
    vertrauten Admin-Bausteine. Eigenes trägt vor allem die Tagesliste mit der Ziffer links. Kein Verstoß (Vertrautheit
    ist im Produkt-Register erwünscht), aber die Kennzahlenreihe ist das Template-hafteste Element. **Vorschlag:** die
    Zahlen in die Köpfe der Listen ziehen („Eingang, 5 neu“) statt als eigene Reihe.

### Was trägt

- Die Sperre bei „Lizenz fehlt“ ist vorbildlich gelöst: Warnung oben, Sprung zum Formular, `disabled` mit hörbarem
  Grund, Formular mit allen Feldern aus §8 und den drei Auswegen (eintragen, neu abrufen, Bildkarte).
- Claims stehen direkt unter ihrem Absatz, jeweils mit Status und Quelle. So wird der Faktencheck beim Lesen
  erledigt, ohne zwischen Text und Quellen zu springen.
- Der Stopp braucht einen Grund, das Banner nennt Grund, Person und Zeit. Ein versehentliches Anhalten ist damit kaum
  möglich, und ein Halt ist überall sichtbar.

---

## hm-almanac (nur Werkzeuge und Textabgleich)

| Messung | Wert |
|---|---|
| shots.mjs | 21 Aufnahmen, 0 Fehler, Überlauf 0, keine Tippfläche < 44 px gemeldet |
| sloplint `--scope app`, URL und Datei | clean: 0 FAIL, 0 REFLEX, 0 WARN |
| Schriften | Hanken Grotesk (Text und Köpfe), IBM Plex Mono (Ziffern) |
| Lizenz fehlt | im Screen `entwurf.html`; „Freigeben“ als `type="button" aria-disabled="true"` mit `aria-describedby`; die normale Freigabe liegt in `entwurf-freigabe.html` |
| Pflichtinhalte laut Textabgleich | Budget, Stopp mit Grund als Pflichtfeld, Claims (C1 ff., „Beleg“ 45-mal), Karenz, „von Hand“, WhatsApp mit Kopieren, Dublette, bisher/neu, Werbemittel, Einblendungen, Erstattung: alle Begriffe vorhanden; Anordnung nicht angesehen |

**P1**

1. **Alle Screens, Ziffern.** IBM Plex Mono steht auf der impeccable-Ausschlussliste (`impeccable/reference/brand.md`,
   Reflex-reject list), die `tamil-marke` als Teil der Verbotsliste nennt. **Vorschlag:** Ziffern in Hanken Grotesk
   mit `font-variant-numeric: tabular-nums` setzen. Hallmark erlaubt Mono im App-Register nur, wenn Mono das Material
   ist.

**P3**

2. **Entwurf, Lizenz fehlt.** Die Sperre arbeitet mit `aria-disabled` statt `disabled`. Das geht, weil der Knopf
   `type="button"` ist und fokussierbar bleibt. Es hängt aber daran, dass später kein Skript den Knopf zum Senden
   bringt. **Vorschlag:** die Sperre im Server prüfen (Stand und Lizenz) und im Code festhalten.

**Nicht geprüft:** Sichtprüfung 390/1280, Fehlbedienung bei Buchung und Eingang. In `buchungen.html` habe ich kein
Feld `grund` für die Ablehnung gefunden; zu bestätigen, ob der Grund dort anders erfasst wird.

---

## hm-aushang (nur Werkzeuge und Textabgleich)

| Messung | Wert |
|---|---|
| shots.mjs | 21 Aufnahmen, 0 Fehler, Überlauf 0 |
| Tippflächen < 44 px (390 und 820) | Kontrollkästchen und Optionsfelder 20 × 20 px: Verzeichnis 14, Lizenz fehlt 4, Buchungen 2 |
| sloplint `--scope app`, URL | 0 FAIL, 0 REFLEX; 1 WARN F7 (dasselbe Rezept auf sechs Eingabe-Selektoren, `cockpit.css:190`); 8 WAIVED (22 Grau ohne Farbton, 49b) |
| Schriften | Epilogue, eine Familie, nicht auf den Listen |
| Lizenz fehlt | „Veröffentlichen“ ist `disabled` mit `aria-describedby="sperre"` |
| Buchung ablehnen | Grund ist Pflichtfeld (`required`) |
| Pflichtinhalte laut Textabgleich | Budget, Stopp mit Grund als Pflichtfeld, Belege („Beleg“ 26-mal), Karenz, „von Hand“, WhatsApp mit Kopieren, Dublette, bisher/neu, Werbemittel, Einblendungen: vorhanden; Claims je Absatz nicht angesehen |

**P2**

1. **Verzeichnis, Lizenz fehlt, Buchungen, 390 und 820.** 20 Kontrollkästchen und Optionsfelder sind 20 × 20 px groß.
   Nicht geprüft habe ich, ob ihr `label` die Trefferfläche auf 44 px bringt. **Vorschlag:** Label als Block mit
   mindestens 44 px Höhe oder `min-block-size: 44px` auf `.wahl label`.

**P3**

2. **Tokens.** `--shadow-card: 0 12px 28px …` ist ein weicher Schatten, ein Merkmal des Baukasten-Looks aus Runde 4.
   Ob und wo er sichtbar ist, habe ich nicht angesehen. **Vorschlag:** prüfen und auf Linie oder Fläche umstellen.

**Nicht geprüft:** Sichtprüfung 390/1280, Fehlbedienung bei Eingang und Social, Lesbarkeit der Tabellen am Handy.

---

## hm-terrazzo (nur Werkzeuge und Textabgleich)

| Messung | Wert |
|---|---|
| shots.mjs | 24 Aufnahmen (8 Screens, zusätzlich `eingang-kooperation.html` als Zustand), 0 Fehler, Überlauf 0 |
| Tippflächen < 44 px | Sprunglink „Zum Inhalt“ 119 × 43 px auf allen Screens; Optionsfelder 1 × 1 (visuell versteckt) im Verzeichnis (10) und bei Lizenz fehlt (2), dazu ein Kontrollkästchen 20 × 20 |
| sloplint `--scope app`, URL | 0 FAIL, 0 REFLEX; 8 WARN nur über `file://` (Schrift); 38 WAIVED (überwiegend 49b) |
| Schriften | Onest, eine Familie, nicht auf den Listen |
| Lizenz fehlt | „Freigeben (Stand 4)“ ist `disabled`, aber ohne `aria-describedby` |
| Pflichtinhalte laut Textabgleich | Budget (nur einmal erwähnt), Stopp mit Grund als Pflichtfeld, Karenz, „von Hand“, WhatsApp mit Kopieren, Dublette, bisher/neu, Werbemittel, Einblendungen: vorhanden; „Beleg“ kommt nicht vor, Claims je Absatz nicht bestätigt |

**P2**

1. **Entwurf, Lizenz fehlt, alle Breiten.** „Freigeben“ ist gesperrt, aber der Grund hängt nicht am Knopf
   (`aria-describedby` fehlt). Ein Screenreader meldet „Freigeben, nicht verfügbar“ ohne Grund. **Vorschlag:** den
   Hinweistext mit `aria-describedby` verbinden.
2. **Verzeichnis, Lizenz fehlt, 390.** Die Optionsfelder sind 1 × 1 px groß (visuell versteckt); getroffen wird über das
   Label. Nachgemessen habe ich das nicht. **Vorschlag:** Labelhöhe ≥ 44 px sicherstellen und den Fokusring am Label
   zeigen (`:has(:focus-visible)`).

**P3**

3. **Alle Screens, Sprunglink.** 43 px hoch, 1 px unter 44. **Vorschlag:** Innenabstand um 1 px erhöhen.

**Nicht geprüft:** Sichtprüfung 390/1280. Dazu der harte Versatzschatten `12px 12px 0` an den Entscheidungskarten:
Ob er als Effekt oder Baukasten wirkt, habe ich nicht angesehen. Offen bleiben auch die Claims je Absatz und die
Fehlbedienung bei Buchung und Eingang.

---

## Vergleich entlang derselben Kriterien (ohne Gesamturteil)

| Kriterium | hm-eigen | hm-almanac | hm-aushang | hm-terrazzo |
|---|---|---|---|---|
| Prüftiefe | vollständig | Werkzeuge, Textabgleich | Werkzeuge, Textabgleich | Werkzeuge, Textabgleich |
| Screens | 7 | 7 | 7 | 8 (dazu leerer Zustand Kooperation) |
| shots.mjs: Fehler, Überlauf | 0, 0 | 0, 0 | 0, 0 | 0, 0 |
| Tippflächen < 44 px (ohne versteckten Sprunglink) | keine | keine | 20 Felder mit 20 px | Sprunglink 43 px, versteckte Radios |
| sloplint über URL: FAIL / REFLEX / WARN | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 1 (F7) | 0 / 0 / 0 |
| WAIVED | 12 | 0 | 8 | 38 |
| Schriften | Rethink Sans + Golos Text | Hanken Grotesk + **IBM Plex Mono** | Epilogue | Onest |
| Verbotsliste | frei | **Plex Mono (P1)** | frei | frei |
| Pflichtinhalte | alle sieben bestätigt | Begriffe da, nicht angesehen | Begriffe da, nicht angesehen | Begriffe da, Claims je Absatz unbestätigt |
| Freigabe bei Lizenz fehlt gesperrt | ja, `disabled` mit Grund | ja, `aria-disabled` mit Grund | ja, `disabled` mit Grund | ja, `disabled` ohne verbundenen Grund |
| Stopp braucht Grund | ja | ja | ja | ja |
| Ablehnen einer Buchung (Erstattung) abgesichert | **nein** (Grund vorbefüllt, keine Bestätigung) | nicht geprüft (kein Grund-Feld gefunden) | Grund ist Pflicht | nicht geprüft |
| Freigabe trotz abweichendem Werbemittel möglich | **ja** | nicht geprüft | nicht geprüft | nicht geprüft |
| Lesbarkeit, Dichte, Tabellen am Handy | Prosa 18 px; Tabellen gestapelt; Notschalter weit unten (P2) | nicht angesehen | nicht angesehen | nicht angesehen |
| Eigenes Werkzeug oder Template | überwiegend eigen (Tagesliste); Kennzahlenreihe template-haft (P3) | nicht angesehen | nicht angesehen | nicht angesehen |
| P0 / P1 / P2 / P3 | 0 / 2 / 6 / 3 | 0 / 1 / 0 / 1 | 0 / 0 / 1 / 1 | 0 / 0 / 2 / 1 |
