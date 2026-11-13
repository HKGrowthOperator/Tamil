# Prüfung hm-terrazzo, Runde 1
Harte Kriterien: 17 von 18 erfüllt · P0: 0 · P1: 8 · P2: 5 · P3: 4

Grundlage: `design/brief-v3.md`, `design/linien-auftrag.md`, `tamil-marke/references/abgelehnt.md`. Weil Brief v3 keine
nummerierten Kriterien mehr hat, sind die 18 harten Kriterien unten aus Brief v3 („Was fest bleibt“) und den Regeln
des Linien-Auftrags abgeleitet. Gemessen über `http://127.0.0.1:8953/richtungen/hm-terrazzo/` mit `tools/shots.mjs`
(11 Seiten × 390/820/1280, 33 Aufnahmen) und einem eigenen Playwright-Skript (Schriftfamilien, Größen, Versalien,
Sperrung, Verläufe, Schatten, Bildnachweise, Labelgrößen). Cockpit nicht Teil dieser Prüfung.

## Erster Eindruck (3 Sätze)
Ruhig, kühl, ordentlich, ohne Lärm: kein Rot als Fläche, keine Versalien, keine Pillen, keine Verläufe, echte und
ehrlich gekennzeichnete Inhalte. Gemacht für tamil.de wirkt sie trotzdem nicht: Schriften (Syne, Onest, JetBrains Mono),
2-px-Tintenlinien, Radius 0 und der harte Versatzschatten von 12 px stammen fast unverändert aus dem Hallmark-Theme
„Terrazzo“. Das ist die Stimme einer Materialbibliothek („codes and millimetres“, Schatten dort 14 px, Rost statt
Logorot). Vom Terrazzo selbst ist auf keiner Seite etwas zu sehen, und alle Seiten sind aus denselben drei Bausteinen
gebaut (Bild links, 2-px-Fuge, Text rechts; Kopf mit h1 links und einer Zeile rechts; linierte Tabelle).

## Harte Kriterien

| # | Kriterium (Quelle) | Handy 390 | Desktop 1280 | Ergebnis |
|---|---|---|---|---|
| 1 | Logo unverändert (v3) | `logo.png`, Bild | dto. | erfüllt |
| 2 | Nur Deutsch, keine tamilische Schrift als Schmuck (v3) | `tamil_ohne_lang` 0, keine Tamil-Zeichen | dto. | erfüllt |
| 3 | Echte Inhalte, Platzhalter sichtbar (v3) | Kino genau nach `inhalte.json` (11/2 Kinos, „6 weitere Städte“); alle 12 Verzeichniseinträge in `rueckblick.json`; „Preis folgt“, „Texte folgen von KBS Digitalmedia“, Premium „nur zur Darstellung“; WhatsApp-Kanal echt (`inhalte.md`) | dto. | erfüllt |
| 4 | Bildnachweis an jedem Bild (v3, Auftrag) | 0 Bilder ohne Nachweis in `main` (alle 11 Seiten) | 0 | erfüllt |
| 5 | Fließtext Handy ≥ 18 px (Auftrag) | 19 px (`main p`) | 20,6 px | erfüllt (Hinweistexte 16 px, siehe P2) |
| 6 | Kontrast AA (v3) | von Hand aus den Tokens (oklch, Näherung Y≈L³): Grau `--color-muted` auf Papier 6,7:1, auf `paper-2` 6,1:1; Rot `--color-accent` 5,2:1; Grau auf Tinte 10,6:1 | dto. | erfüllt (Messskript scheiterte an oklch-Werten, deshalb von Hand) |
| 7 | Tippflächen 44 px (v3) | `shots.mjs` meldet nur die versteckten 1×1-Eingaben; ihre Labels 48 px hoch, 53 bis 294 px breit | – | erfüllt |
| 8 | Kein seitliches Scrollen 390/820/1280 (v3) | 0 px | 0 px (820: 0 px) | erfüllt |
| 9 | `prefers-reduced-motion` (Auftrag) | `base.css` Z. 25, `terrazzo.css` Z. 407 | dto. | erfüllt |
| 10 | Schriften selbst gehostet, OFL im Ordner (Auftrag) | `schriften/*.woff2`, `syne-OFL.txt`, `onest-OFL.txt`, `jetbrains-mono-OFL.txt`; `schriften` leer im Bericht | dto. | erfüllt |
| 11 | Keine Gedankenstriche (Auftrag) | eigener Text 0; `buchen.html` „23.11.–06.12.2026“ ist ein Bis-Strich | dto. | erfüllt |
| 12 | Keine Dachzeilen (Auftrag) | keine | keine | erfüllt |
| 13 | Keine Versal-Labels (Auftrag) | 0 Elemente mit `uppercase`, 0 mit Sperrung ≥ 1 px | 0 | erfüllt |
| 14 | Keine „·“-Metazeilen (Auftrag) | 0 | 0 | erfüllt (Komma-Metazeilen, siehe P3) |
| 15 | Keine gleich großen Kartenraster (Auftrag) | keine | keine | erfüllt |
| 16 | Keine Verlauf-Bildkacheln (Auftrag) | 0 `gradient` | 0 | erfüllt |
| 17 | Keine Seitenstreifen als Akzent (Auftrag) | `buchen.html`, `.schrittfolge a[aria-current] { box-shadow: inset 3px 0 0 var(--color-accent) }`: roter 3-px-Streifen links am aktiven Schritt | dto. | **verletzt** |
| 18 | Seitenliste vollständig (Auftrag) | alle 11 Seiten plus `einreichen-bestaetigung.html` | dto. | erfüllt |

## Paarvergleich (erster Bildschirm, gleiche Breite)

**Terrazzo gegen BBC und Guardian (1280):**
- Dichte: Die Vorbilder zeigen im ersten Bildschirm fünf bis sechs Geschichten mit Bild. Terrazzo zeigt einen Aufmacher und
  drei Terminzeilen, dazwischen rund 130 px leere Fläche (Aufmacher endet bei y≈683, „Die nächsten Feste“ beginnt bei y≈815).
- Hierarchie: Der Guardian staffelt mit Serifenkopf, farbiger Rubrikmarke und drei Bildgrößen. Terrazzo hat genau zwei
  Stufen (Syne-Kopf, Onest-Text). Die Ordnung ist sauberer als bei der BBC (keine Werbung über dem Aufmacher), aber
  so spärlich, dass die Seite eher wie eine Agentur- oder Portfolioseite wirkt als wie eine Nachrichtenmarke.
- Bild: Das Tempelfoto hat bei 632 × 474 px einen guten, ruhigen Ausschnitt. Das Querformat des Guardian-Aufmachers
  wirkt durch die größere Bildfläche wertiger.

**Terrazzo gegen Runde 2 (1280):**
- Grund und Tinte: kühles Off-white `oklch(96,6 % 0,004 250)` statt Sand, Tinte fast schwarz statt Braungrau, keine
  Rubrikpunkte, kein Mosaik, keine runden Bilder. Kein Rückfall in Runde 2.
- Runde 2 zeigt sechs Anreißer, Terrazzo einen. Terrazzo wirkt geordneter, aber leerer.
- Statt Pillen ordnen hier Linien (1 px zwischen Zeilen, 2 px über Tabellen). Das ist der stärkste Unterschied zu
  Runde 2 und 3.

**Terrazzo gegen Runde 4 „Raster“ (1280):**
- Keine Riesenschrift im ersten Bildschirm: Aufmacher etwa 46 px gegen „KANGUVA“ mit rund 150 px, kein Rot als Fläche,
  kein Liniengitter in Rot.
- Rückfall weiter unten: Die Ziffer „11“ im Kino-Band ist 88 px groß (390: 64 px), gesetzt in der breiten Syne. Sie
  steht über demselben Wert in der Überschrift („11 Kinos zeigen ‚Scene‘“). Das ist das Signatur-Element in kleinerer
  Form (siehe P1-5).
- Breite der Schrift gemessen (Canvas, 100 px, gleicher Satz): Syne 600 = 2303 px, Onest 600 = 2168 px, Arial 600 =
  2195 px, also etwa 5 % breiter. Das ist nicht extrabreit im Sinn von Runde 4, aber an den Ziffern (breite „1“ mit
  Fuß) und am geometrischen „a“ deutlich sichtbar.

## Befunde

### P0
Keine. `shots.mjs`: 33 Aufnahmen, 0 Fehler, 0 Konsolenmeldungen, 0 leere Bilder, alle Schriften geladen.

### P1
1. **Seitenstreifen als Akzent** (A17), `buchen.html` bei 390 und 1280, `.schrittfolge a[aria-current]`: roter Streifen
   von 3 px links. *Abhilfe:* aktiven Schritt durch Schriftschnitt 600 und Tinte zeigen, oder durch eine 2-px-Linie
   unten im Material der Fuge. Kein farbiger Rand links.
2. **Schrift aus der Ausschlussliste** (C), alle Seiten, `--font-display: "Syne"` (h1, h2, `.kinoband__zahl`,
   `.monat__kopf`, `legend`, Schrittziffern). Syne steht in `impeccable/reference/brand.md` Z. 30 unter „Training-data
   defaults. Ban list“, und `tamil-marke` verbietet Schriften dieser Liste. Dazu ist sie die Vorgabe des Hallmark-Themes,
   also keine Wahl für tamil.de. *Abhilfe:* eigene Wahl einer ruhigen Kopfschrift in normaler Breite, außerhalb der
   Liste und der verbrannten Schriften, und den Grund dafür aus dem Leser ableiten.
3. **Drei Schriftfamilien** (B, Schrift), 8 von 11 Seiten, `.code` mit JetBrains Mono für Daten („So 15.11.“,
   „Sa 10.01.“, „10.09.“), Pixelmaße und Zeitraum. Das Theme sieht Mono für Produktcodes und Millimeter vor; in einem
   Festkalender wirkt die Schreibmaschinenschrift fremd und technisch. *Abhilfe:* Onest mit `tabular-nums` für Daten und
   Maße, Mono entfernen.
4. **Erster Bildschirm 390 mit nur einer Geschichte** (C, „Cover mit nur einer Geschichte“; Marke: Aufmacher und weitere
   Geschichten), `index.html` 390 × 844: Kopf und zweizeilige `.hauptnav` belegen etwa 195 px (zweite Zeile „Termine
   Kino Verzeichnis“ sieht wie umgebrochen aus), Bild 268 px, Kopfzeile, Vorspann. Der Knopf „Beitrag lesen“ und alles
   Weitere liegen unter 844 px, „Die nächsten Feste“ beginnt bei etwa 1075 px. *Abhilfe:* Navigation einzeilig
   (waagrecht scrollbar mit sichtbarem Ende, oder Menü), Aufmacherbild 3:2 statt etwa 4:3, Vorspann am Handy kürzen,
   damit mindestens die erste Terminzeile oder ein zweiter Anreißer im ersten Bildschirm steht.
5. **Dunkles Kino-Band mit Riesenziffer** (C, „Diese Woche“-Bänder und dunkler Kino-Bereich aus Runde 5–7; Riesenschrift
   aus Runde 4), `index.html` `.kinoband` mit `.kinoband__zahl` (88 px bei 1280, 64 px bei 390) und `kino.html`
   `.kinoband__zahl--klein`. Das Band wiederholt den Wochenstand des Kinos auf Tinte, wie es `klar2` hatte. Die Ziffer
   doppelt die Überschrift. *Abhilfe:* Ziffer streichen; Kino auf der Startseite als linierte Liste „Film, Städte, Stand“
   auf hellem Grund, im selben Material wie die Feste.
6. **Rosa Hinterlegung** (C, „rosa Hinterlegungskästen“, Runde 3), `verzeichnis.html` 390/1280 `.ist-premium
   { background: var(--color-accent-soft) }` (oklch 94,5 % 0,022 25, sichtbar rosa) und `.spec tbody tr:hover` mit
   derselben Fläche in Termine und Werben. *Abhilfe:* Premium durch das Wort „Premium“ in Textform in der Zeile und eine
   2-px-Tintenlinie über dem Eintrag kennzeichnen; Hover nur mit Unterstreichung des Titels.
7. **Knopf „Weiterlesen“ unter dem Aufmacher** (B, Baukasten), `index.html` `.btn.btn--primaer` „Beitrag lesen“, ein
   schwarzer Vollton-Knopf neben dem Link „Per WhatsApp schicken“. *Abhilfe:* die Schlagzeile ist der Link; den Knopf
   streichen, WhatsApp als schlichten Link behalten.
8. **Ein Baustein für alles, keine eigene Idee sichtbar** (B, Baukasten; Brief v3: „gemacht, nicht generiert“). Die
   Startseite stapelt dreimal dasselbe Modul `.feldreihe--7-5` / `--5-7` (Bild über 7 Spalten, senkrechte 2-px-Fuge,
   Text über 5 Spalten): Aufmacher, „Nachrichten aus Berlin, St. Gallen und Colombo“, „Tempel, Vereine und Schulen“.
   Alle zehn Unterseiten öffnen mit demselben `.kopfblock` (h1 links, ein Satz rechts). Das titelgebende Terrazzo kommt
   nirgends vor: keine Körnung, kein Material, kein Bildausschnitt, der es aufnimmt. *Abhilfe:* einen sichtbaren Zug
   finden, der nur tamil.de gehört und aus den Inhalten kommt (zum Beispiel Kalender und Kino als eigene Form statt als
   Tabellen im Portalkleid). Die Abfolge auf der Startseite in Größe und Form staffeln: einmal großes Bild, einmal
   Liste ohne Bild, einmal kleine Bilder in Reihe.

### P2
1. **Harter Versatzschatten** an Formularkarten, `einreichen.html`, `buchen.html`, `kontakt.html` `.karte { box-shadow:
   12px 12px 0 var(--color-paper-3) }`. Ein Neo-Brutalismus-Muster aus der Vorlage, das am Handy wie verrutscht wirkt.
   *Abhilfe:* Karte mit 2-px-Rand ohne Schatten oder ganz ohne Karte auf `paper-2`.
2. **Datumsformen wechseln**, Startseite und Termine: „So 15.11.“ (Mono, ohne Jahr), „17. August 2026, Berlin“
   (Onest, in der Metazeile), „10.09.“ (Kinojahr, Mono, ohne Wochentag). *Abhilfe:* eine Form für Listen
   („So, 15. Nov.“) und eine für Beiträge, durchgehend in Onest.
3. **Kino-Seite doppelt und dünn**, `kino.html`: dieselben Daten zweimal (Tabelle „Nach Stadt“ und dunkles Band), die
   Spalte „Land“ zeigt siebenmal „Deutschland“. Das Karthi-Foto von 2017 steht ohne Bezug zu den laufenden Filmen
   („Scene“, „Ramayana“). *Abhilfe:* je Film eine Zeile mit allen Städten, Land einmal im Kopf; Bild nur mit Bezug zum
   laufenden Programm oder klar dem „Kinojahr“ zugeordnet.
4. **Hinweistexte 16 px** mit mehr als 60 Zeichen, `einreichen.html` (3 Stellen, z. B. „Es geht keine automatisch …“),
   `buchen.html` (2), `werben.html` („Maßstabsgetreu zueinander …“), bei 390. *Abhilfe:* `--text-label` für Hilfetexte
   auf 1,0625 bis 1,125 rem; ältere Leser füllen diese Formulare aus.
5. **Geringe Dichte auf dem Desktop**, `index.html` 1280: erster Bildschirm mit einer Geschichte und drei Terminen, etwa
   130 px leer zwischen Aufmacher und Festen (`.aufmacher { padding-block: 40px 64px }` plus Abstand des Abschnitts).
   *Abhilfe:* rechts neben oder unter dem Aufmacher zwei bis drei Anreißer aus „Nachrichten“ hochziehen.

### P3
1. **Komma-Metazeilen**, überall unter Anreißern: „8. November 2026, Berlin, Düsseldorf, München“. Das ist dasselbe
   Portalmuster wie die verbotene „·“-Zeile, nur mit Komma. *Abhilfe:* Ort in den Satz des Vorspanns, Datum allein.
2. **Premium-Marke als rot umrandetes Kästchen**, `verzeichnis.html` und `verzeichnis-eintrag.html` `.premium`
   (`box-shadow` 1 px Rot). *Abhilfe:* zusammen mit P1-6 als Text lösen.
3. **Monatsleiste als Knopfreihe**, `termine.html` 390: zwölf umrahmte Kästchen in drei Zeilen (Nov und Dez allein in
   der dritten). *Abhilfe:* Monate als Textlinks in einer Zeile oder als Auswahlliste.
4. **Gedankenstriche im Altbestand**, `artikel-71.html` („… erwachsen kann – ein Band …“) und `artikel-83.html`. Das ist
   wörtlich übernommener Inhalt, also kein Gestaltungsfehler; beim Satz einheitlich entscheiden.

## Was trägt
- Inhalte genau und ehrlich: Kino ohne erfundene Spielzeiten („Namen liegen der Redaktion nicht vor“), Platzhalter
  sichtbar („Preis folgt“, „Texte folgen von KBS Digitalmedia“), Bildnachweis an jedem Bild bis hin zu „Archivbild“
  beim Reichstag.
- `werben.html` „Die Formate im Verhältnis“: die sechs Werbeplätze maßstäblich zueinander gezeichnet. Das ist eine
  eigene, nützliche Idee für Anzeigenkunden.
- Ruhe ohne Rückfall in Runde 2 oder 4: kühler Grund, Rot nur im Logo, im Fokus und in Unterstreichungen, Termine als
  linierte Tabelle mit WhatsApp je Zeile.

## Bedienbarkeit (nur zur Information)

| Nielsen | 0–4 | Satz |
|---|---|---|
| 1 Status | 3 | Buchung zeigt Schritt und Zeitraum, „Heute ist Freitag, 13. November 2026“ im Kalender. |
| 2 Sprache der Nutzer | 4 | Klare deutsche Sätze, keine Fachwörter. |
| 3 Kontrolle | 3 | Buchungsschritte als Links, Zurück nicht überall sichtbar. |
| 4 Konsistenz | 4 | Ein Kopf, ein Tabellenmuster, eine Formularform auf allen Seiten. |
| 5 Fehlervermeidung | 3 | Pflichtfelder mit Stern, belegte Tage durchgestrichen. |
| 6 Erkennen statt Erinnern | 3 | Filter mit Zahlen („Tempel 4“), Kino ohne Kinonamen. |
| 7 Flexibilität | 2 | Keine Suche im Kopf, Termine nur über die Monatsleiste. |
| 8 Ästhetik und Reduktion | 3 | Aufgeräumt, aber Daten doppelt (Kino) und große Leerflächen. |
| 9 Fehlerhilfe | 2 | Fehlerzustände der Formulare nicht gezeigt. |
| 10 Hilfe | 3 | „So geht es weiter“ beim Einreichen, „So läuft eine Buchung“. |

Nicht geprüft: Zoom auf 200 % und Tastaturweg (Sprunglink und `:focus-visible` sind vorhanden), Cockpit.
