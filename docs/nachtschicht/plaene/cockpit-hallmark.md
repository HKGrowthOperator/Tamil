# Plan: Redaktions-Cockpit tamil.de mit Hallmark (Almanac, App-Screens)

Stand 13.11.2026, 20:25 Berlin. Abgabe 22:10. Plan-Modus aktiv: bisher nur gelesen, nichts geschrieben.
Nach Freigabe wird genau dieser Ablauf ausgeführt, nur in `/home/user/Tamil/design/cockpit/hm-almanac/`.

## Gelesen (Pre-flight, Schritt 0)

- Hallmark `SKILL.md` (Floor 1 bis 16, Flow 0 bis 7), `references/flow.md` § App screens, Theme `almanac.md`.
- `design/brief-v3.md`: Hallmark-Floor geht vor; keine Dachzeilen, keine Versal-Labels, keine „·“-Metazeilen;
  Logo `design/inhalte/logo.png` unverändert; nur Deutsch; AA, 44 px, 390 zuerst, kein seitliches Scrollen.
- Cockpit-Templates (alle 16) und `app.css` als Funktionsquelle; Aussehen wird nicht übernommen.
- `docs/vertrag/festlegung-social.md` (F4, Vorschlag, Trockenmodus, Karenz 10 min, Regelwerk-Tabelle, WhatsApp von Hand).
- Live-Bericht `bericht-jetzt.json` (Stand 12.11.2026 17:57 UTC). Echte Werte, die verwendet werden:
  - Entwürfe 68 (neu 65, veröffentlicht 3); Storys 110 (fertig 68, recherche_erforderlich 19, verworfen 17, neu 6);
    Herkunft nachtrag 73 / radar 37; sensibel 20.
  - Warteschlange offen 6, läuft 0, wartet_budget 0, tot 0, fertig 31.
  - Budget: heute 0,00 von 2,00 USD, Monat 0,00 von 2,00 USD, kein Stopp; Kosten 7 Tage 0,00 USD
    (Agent-Modus, 104 Aufrufe agent, 3 kino). Gestoppt: keine Kanäle.
  - Läufe #1612 bis #1619 (gesammelt 72 bis 158, relevant 3, Notiz „termin_veraltet 3, ohne_bezug 10, ausland 11, tageslimit 3“).
  - Prüffall Entwurf #36 / Story 67 „Ranjan Neelakandan …“: 19 Claims (17 bestätigt, C5 und C18 Widerspruch),
    Q1 Yverdon Sport FC, Q2 Le Dauphiné, Q3 en.wikipedia.org, Bild „Foto: Vincenzo.togni / Wikimedia Commons, CC BY-SA 4.0“,
    vier Hinweise (zwei Widersprüche aus dem Text gelassen, Länge 304 statt 450 bis 750, Agent-Modus redakteur-r6-3),
    Fassungen c3918e9d (text) und fb2bf86a (entwurf), Kosten 0,000 USD, 1 Aufruf.
  - Weitere echte Titel/Hinweise: #68 Deepavali 2026, #29 Wien Arangetrams, #57 Vibuja Manichelvan, #67 Luzern/Basel,
    #54 „OM“ im Kino (Bildkarte, Kino-Vorlage), Recherche-Storys 20, 22, 28 (sensibel, Einzelquelle), 103, 109, 110.
- Keine Social-Daten im Bericht (F4 nur Vorschlag). Daraus folgt: Social-Screen im **Trockenmodus**, Kandidaten sind die
  drei tatsächlich veröffentlichten Entwürfe, keine Meta-Kennungen, keine Links, keine Reichweite.
- Kein Tokens/Passwort aus dem Bericht wird übernommen (lokale Passwortdatei wird nicht geöffnet).

## Schritt 1 (ohne Rückfrage, Schluss gezogen)

Material: echte Entwürfe, Claims, Läufe, Budget aus dem Bericht; Bild nur als Nachweiszeile plus Platz (kein
Stockfoto, App-Scope ohne Stand-in-Fotos). Publikum: Redaktion (2 bis 4 Personen, Rollen admin/redaktion/leser), am
Laptop und am Handy. Job: prüfen und freigeben. Ton: utilitarian/editorial. Genre: editorial (vom Theme gesetzt).

## Schritt 2 bis 5: Picks-Block (wird so in `begruendung.md` stehen)

- **Screen** · App-Screens, Scope app, vier Seiten mit gemeinsamer Kopfleiste (Top-Bar, weil sieben Ziele + „Mehr“;
  unter 60rem ein Menü-Knopf mit `<details>`), Zustände: lädt, leer, Fehler, voll je Datenbereich.
- **Theme** · Almanac, dealt 2/3, seed tamil-deutschsprachiges-online-magazin-der-ff32·6bcf19c0·2026-11-13·r0 (Schiefer-Papier,
  Tintenblau, Hanken Grotesk für Köpfe und Bedienung, Newsreader für Text, IBM Plex Mono nur für Ziffern, zwei Linienstärken,
  eckig, ein Magenta nur für Primäraktion/Auswahl/Widerspruch-Zeiger).
- **Chrome** · Kopfleiste: Logo (Datei, klein) + „Redaktion“, Ziele Übersicht, Entwürfe (65), Recherche (19), Social,
  Warteschlange, Kosten, Protokoll, Mehr (Quellen, Zeitplan, Schalter, Benutzer); rechts Radar-Zustand als Text, Person, Abmelden.
- **Signatur** · der Prüfbogen: Entwurfstext auf dem „Sheet“ mit Randspalte, in der je Absatz die Claim-Nummern und ihre
  Ampel als Wort/Form stehen (bestätigt = durchgezogene Linie, Einzelquelle = gestrichelt, Widerspruch = Magenta-Balken
  + Wort „Widerspruch“); Ampel nie nur Farbe.
- **Material** · real: siehe oben · Bilder: nur Nachweiszeile und leerer Bildplatz mit Maß (Datei liegt nicht vor) ·
  absent: Social-Historie, Meta-Links, Kosten > 0, Reichweite.
- **Sweep** · nach dem Bau.

## Schritt 6: Bau

1. `mkdir -p design/cockpit/hm-almanac/{.hallmark,shots}`;
   `node <skill>/scripts/theme.mjs scaffold almanac --scope app --dealt "2/3, seed tamil-…-r0" --dir design/cockpit/hm-almanac`
   → `tokens.css`, `base.css`, Stempel-Gerüst. Danach `references/patterns.md`, `craft.md` § 9 (ohne § 4/7/8),
   `interaction-and-states.md`, `microinteractions.md` nur die Teile zu Steuerelementen lesen; `gates.md` § 1 bis § 4.
2. `cockpit.css` (eine Datei für alle vier Screens): Zeile 1 Stempel (`shape: app screen`, theme almanac, dealt, genre
   editorial, signature: der Prüfbogen), Zeile 2 Kritikzeile, ggf. Waivers. Nur Tokens, keine Literalfarben.
   Bedienelemente 36 bis 40 px hoch, Trefferfläche 44 px am Handy (`min-height: 44px` unter 48rem), acht Zustände je
   Steuerelement (default, hover, focus-visible sofort, active, disabled, loading via `aria-busy`, error, success),
   Hilfsklassen `.is-*` für die Zustandstafel. Typo-Skala fest 1.125 bis 1.2, Text 16 px Desktop / 17 px Handy.
   `overflow-x: clip` auf html/body, `prefers-reduced-motion`, kein `transition: all`.
3. Screens (statisches HTML, kein JS nötig; Filter als echte Links mit `?filter=` für „Zustand in der URL“):
   - **`uebersicht.html`** – Lage. Oben „Was auf dich wartet“: Tabelle der offenen Arbeit (65 neue Entwürfe,
     19 Recherche nötig, 6 Jobs offen, 0 Social von Hand) mit Sprung-Aktion je Zeile. Daneben Gesundheit als
     Tabelle: Radar läuft (alle 3 Minuten, letzter Lauf 12.11. 18:55 Berlin), Worker, Budget heute 0,00/2,00 USD und
     Monat 0,00/2,00 USD als Mono-Ziffern mit 2px-Balken, Stopp-Schalter je Kanal (alles, redaktion, wordpress, social:
     „läuft“ als Wort, Anhalten-Knopf mit Pflichtgrund, Bestätigung). Darunter das eine Diagramm: „gesammelt je Lauf“
     #1600 bis #1619 als eine Magenta-Linie (Almanac-Range „one chart“), dann Tabelle letzte 8 Läufe. Zustände sichtbar:
     ein Bereich „Fehler beim Laden der Quellen“ (Fehlerzustand, mit Erneut), ein Skeleton-Muster in der Zustandstafel.
   - **`entwuerfe.html`** – Liste als Tabelle (Titel + Teaser-Zeile, Rubrik, Ort, Relevanz in Mono, Bild-Herkunft,
     Alter, Aktionen Freigeben/Ansehen). Filterreihe als Tabs mit Zählern: Alle 68, Neu 65, Rückblick (nachtrag),
     Recherche nötig 19, Heikel (sensibel), Freigegeben, Veröffentlicht 3, Abgelehnt. Sammelauswahl mit
     „Ausgewählte freigeben“ (disabled bis Auswahl, loading-Zustand). Zeilen-Zustände: Fehler-Zeile (Publisher-Fehler als
     Muster mit Kennzeichnung „Beispielzustand“), freigegeben, veröffentlicht mit „Beitrag öffnen“. Leerzustand für
     „Abgelehnt: noch keiner“ (echt: 0 im Bericht). Etwa 10 echte Entwürfe aus dem Bericht.
   - **`entwurf.html`** – Prüfansicht für #36. Kopf: Titel, Status „neu“, Rubrik Sport, Rückblick-Nachtrag, Ort,
     Quelle; Aktionsleiste (Freigeben primär magenta, Direkt posten, In WordPress bearbeiten, Zurückstellen,
     Ablehnen mit Bestätigung, Vorschau, Als Dossier). Hauptspalte: der Prüfbogen (Absätze aus `inhalt_html` mit
     Randspalte Claims je Absatz; Zuordnung aus Claim-Texten abgeleitet und so gekennzeichnet). Seitenspalte: Hinweise
     (4, echt), Faktenmatrix 19 Claims kompakt mit Ampel als Wort, Quellen Q1 bis Q3 mit Art/Rechte/Datum, Bild mit
     Nachweis und Lizenz-Feldern zum Nachtragen (Rechteinhaber, Lizenz, Lizenz-URL, Social-Recht ja/nein, Ablauf;
     Feld „Lizenz-URL“ im Fehlerzustand „fehlt“), Kosten dieser Story 0,000 USD, Fassungen c3918e9d/fb2bf86a.
     Bearbeiten-Formular (Überschrift, Teaser, Rubrik, Schlagworte, Text, SEO, Alt-Text) als aufklappbarer Abschnitt
     mit Speichern-Erfolgszustand; Neu-schreiben-Anweisungen.
   - **`social.html`** – Trockenmodus-Banner (Konten fehlen, Regelwerk Vorschlag 11.11., wartet auf KBS).
     Warteschlange Instagram/Facebook: die drei veröffentlichten Entwürfe als Kandidaten mit Regelprüfung je Regel
     (Alter ≤ 48 h, Bildrecht für Social, Menge 6/Tag, Ruhezeit 22 bis 7 Uhr, Heikel), Karenz-Countdown (10:00 Minuten
     als Zustandsmuster, gekennzeichnet, `<time>` + Stoppen/Ändern), „von Hand entscheiden“ mit Grund (Heikel-Beispiel
     aus einer echten sensiblen Story). Regelwerk-Fassung als Almanac-Tabelle. Historie: Leerzustand „Noch nichts
     veröffentlicht, Trockenmodus“. WhatsApp-Entwurf (Text aus Titel/Teaser + tamil.de-Link als Platzhalter, Bild
     herunterladen, Kopieren mit Erfolgszustand „kopiert“, Als gepostet markieren mit Bestätigung) plus Stopp je Kanal.
   - Zusätzlich `zustaende.html` (klein): Zustandstafel aller Steuerelemente in acht Zuständen und der vier
     Datenzustände, damit Hallmarks Pflicht prüfbar ist, ohne die Screens zu überladen.
4. Kein Logo-Nachbau: `<img src="../../inhalte/logo.png">` relativ eingebunden (Datei bleibt, wo sie ist).
5. Log: `theme.mjs log --entry '{…, "scope":"app"}' --log design/cockpit/hm-almanac/.hallmark/log.json`;
   `.hallmark/preflight.json` mit den Fundstellen oben.

## Schritt 7: Sweep und Prüfung

1. `node <skill>/scripts/sloplint.mjs design/cockpit/hm-almanac --scope app --genre editorial --render` bis 0 FAIL;
   Reflex beheben oder mit Grund waiven; ein Fix-Durchgang, eine Bestätigung.
2. `gates.md` § 5 (J- und R/J-Gates) durchgehen, WARN bestätigen oder verwerfen.
3. Finish-Review aus frischem Kontext: Subagent (general-purpose) bekommt nur die Screenshots/HTML-Pfade und die
   Anweisung, `references/review-finish.md` selbst zu lesen; ich öffne `review-*.md` nicht. Erstes Wort umsetzen.
4. Prüfbilder: `node tools/shots.mjs design/cockpit/hm-almanac/{uebersicht,entwuerfe,entwurf,social}.html --out
   design/cockpit/hm-almanac/shots` (390/820/1280; kein seitliches Scrollen, keine Konsolenfehler). Schriften kommen
   von Google Fonts; falls der Proxy sie blockt, greifen die Systemfallbacks im Token, und das steht im Bericht.
5. Kontrast stichprobenartig prüfen (muted auf paper/sheet, accent-ink auf accent) – Almanac-Werte liegen laut Theme bei AA.

## Schritt 8: Abgabe

- `begruendung.md`: Picks-Block (aktualisiert, letzte Zeile mit Sweep-Ergebnis), Zuordnungstabelle heutige Funktion →
  Screen (Feed→entwuerfe; Dashboard/Läufe/Quellen-Radar→uebersicht als ein Diagramm + Tabelle; Entwurf/Belege/Bild/
  Neu schreiben→entwurf; Kosten→uebersicht Budget + entwurf Story-Kosten, eigene Kosten-Seite nur verlinkt;
  Schalter→uebersicht + social je Kanal; Recherche→entwuerfe-Filter; Warteschlange/Zeitplan/Protokoll/Quellen/Nutzer/
  Login→Kopfleiste „Mehr“, nicht gezeichnet, als offen gelistet), Material-Liste, offene Punkte.
- Kurzer Bericht auf Deutsch an die Hauptsitzung.

## Zeitplan bis 22:10

| bis | Schritt |
|---|---|
| 20:40 | Scaffold, patterns/craft § 9/states lesen, Stempel |
| 21:25 | vier Screens + Zustandstafel + cockpit.css |
| 21:40 | sloplint --render, Fixes |
| 21:55 | Finish-Review (Subagent) und Fixes |
| 22:05 | shots.mjs, begruendung.md |
| 22:10 | Bericht |

Fällt die Zeit knapp: zuerst `entwurf.html` und `entwuerfe.html` vollständig, dann `uebersicht.html`, `social.html`
zuletzt; die Zustandstafel kann in `entwurf.html` aufgehen.

## Risiken und offene Punkte

- Plan-Modus: Ausführung braucht die Freigabe; bis dahin ist nichts gebaut.
- Social ohne echte Daten: nur Trockenmodus; Countdown und Fehlerzeilen als „Beispielzustand“ gekennzeichnet, nie als Fakt.
- Kosten sind real 0,00 USD (Agent-Modus); werden so gezeigt, nicht geschönt.
- Absatz-Belege: Der Bericht hat keine Absatz→Claim-Zuordnung; sie wird aus den Claim-Texten abgeleitet und als
  abgeleitet markiert (live liefert sie der Faktencheck).
- Logo-Datei ist ein PNG in Rot; auf Schiefer-Papier prüfen, ob es AA-tauglich als Bild wirkt (Logo ist Bild, kein Text).
