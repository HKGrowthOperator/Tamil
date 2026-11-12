# UI, UX und Design-Engineering

## Aktuelle Autorität

`DESIGN.md` auf dem Ausbau-Branch kennzeichnet das Community-Magazin ausdrücklich als abgelehnt.
Das vorhandene warme Theme ist Bestand, keine Vorlage für neue Gestaltung.
Maßstab ist `design/brief.md`, Fassung 2.1, insbesondere Abschnitt 10 für `klar2`,
plus die neueste dokumentierte G2-/G3-Abnahme. Die ältere Nachtblau-/Gold-Radar-Vorschau ist Archiv.

Die Entscheidung vom 10.11. hält `klar2` als internen Vorschlag fest; Kunden-G2/G3 nicht daraus erfinden.
Bestehende Designcommands weiterverwenden. Keine neue Runde mehrerer Stilrichtungen starten, wenn die
aktuelle Aufgabe nur den Ausbau der bereits gewählten Richtung betrifft.

## Skillfolge je Aufgabe

1. `tamil-marke` und betroffenen Brief lesen.
2. `tamil-richtung` für Proben, `tamil-theme` oder `tamil-cockpit` für Umsetzung.
3. Vendortes Impeccable mit Herkunft/Version und nötiger Unterbefehlsreferenz lesen; Kontextregister
   für Magazin/Marke und Cockpit/Produkt trennen.
4. Taste nur bei echter Art-Direction-Aufgabe, Emil Kowalski für einzelne Interaktionsdetails.
   Keine generische Palette oder Schrift gegen den Brief austauschen.
5. `tamil-screens` und `tamil-kritik`; unabhängiger Prüfer bekommt Brief und Ergebnis, keine Begründung
   des Designers und keine alte Kritik als Vorprägung.

## Konkrete Grenzen für klar2

Dies ist eine Checkliste; der vollständige Brief bleibt maßgeblich.

| Bereich | Prüfkriterium |
|---|---|
| Typografie | Libre Franklin; Aufmacher höchstens 34 px mobil / 44 px Desktop; höchstens drei Zeilen |
| Artikel | Lauftext mindestens 18 px mobil; Spalte höchstens etwa 70 Zeichen |
| Kopf | Mobil höchstens 152 px; nur Rubrikband sticky, höchstens 56 px |
| Farbe | Rot höchstens 3 % ohne Bilder; kein zweiter Buntton; genau zwei definierte dunkle Flächen |
| Inhalt | Bildstarke, seriöse Nachrichtenstruktur; echte Daten, keine erfundenen Reichweiten |
| Form | Radius höchstens 2 px, keine Kartenrahmen/Schatten/Pillen an Anreißern |
| Bildtext | Kontrast mindestens 4,5:1 an der hellsten Stelle unter der Schrift |
| Motion | Nur reaktiver Hover, Scale höchstens 1,04, höchstens 0,4 s; Reduced Motion ohne Übergang |
| Dichte | Erstbildschirm-Kriterien nach aktueller protokollierter Ausnahme beurteilen |
| Service | Diese Woche beginnt mobil spätestens im dritten Bildschirm |
| Bedienung | 44 × 44 px Tippziele, sichtbarer Fokus, korrektes Tamil-lang, keine reine Farbcodierung |

Die dokumentierte Entscheidung zum großen 4:3-Aufmacher (10.11.) nennt bewusst geringere Desktop-Dichte.
Widersprüche zwischen Messskript, Brief und bestätigter Ausnahme vor einer Designbewertung im
Entscheidungslog auflösen; die Ausnahme weder still entfernen noch zu einer beliebigen Lockerung erweitern.

## Fehlende Produktoberflächen mitplanen

Nicht nur Startseite schön machen. Probeseite bzw. Ausbau deckt Artikel, Rubrik/Suche, Kalender/Eventdetail,
Einreichung, Verzeichnisliste/-profil/-Änderung, Werbeangebot/Buchung/Zahlungsstatus und Cockpit ab.
Für jedes Formular: Leerzustand, Validierung, Upload läuft/fehlerhaft, Verarbeitung, Erfolg, Dublette,
unberechtigt und vorübergehend nicht verfügbar. Statusmeldung immer im Web, ohne Mailabhängigkeit.

Im Cockpit Listen, Filter, Prioritäten, verständliche Fehler und nächste Aktionen vor dekorative Flächen setzen.
Stopp hat sichtbare Wirkung; Pause, Fehler, wartende Freigabe und bereits veröffentlicht unterscheiden.
Kundenbuchung und redaktionelle Freigabe dürfen keine internen Queue-IDs oder Providergeheimnisse zeigen.

## Designprüfung

Bestehende 390/820/1280-Aufnahmen ausführen; bei produktiven Formularen bei Bedarf 320 und 1440 ergänzen.
Keine allgemeine Behauptung über mobile Qualität aus einem Desktop-Screenshot.
Tastaturweg und Touch-Bedienung, Fokus, Dropdowns, Tabellen, lange Titel, fehlende Bilder, Fehlerzustände
und Reduced Motion prüfen. Fotoausschnitte tatsächlich ansehen, keine unpassenden automatischen Alt-Texte.

Nachweise: Seite, Breite, Element, Befund, Schwere, Änderung, neuer Nachweis.
Ein Pattern aus anderen Kundenrepos ist keine Erlaubnis, deren Marke, Fotos, Copy oder Layout zu kopieren.
