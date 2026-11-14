# Entscheidungslog

Neueste oben. Format: Datum · Entscheidung · wer · warum. Was hier steht, gilt, bis ein neuerer Eintrag es ändert.
Eine Entscheidung nicht stillschweigend umkehren: neuen Eintrag schreiben.

## 13.11.2026

- **Bezahlte Werbebuchungen überdauern die Deinstallation** (steuerliche Aufbewahrung): Buchungen und Protokoll
  bleiben, nie bezahlte Buchungen werden entfernt; ganz gelöscht wird nur mit der Option
  `tamil_site_werbung_deinstallation_loeschen`. Datenversion 4 mit den Schritten F1 = 2, F3 = 3, F2 = 4. ·
  Hauptsitzung bei der Zusammenführung der Bausteine
- **Einsendungen ohne Abschluss werden nach 90 Tagen gelöscht** (F1 nannte nur Fristen für Abgeschlossenes); Abholen
  und Status bleiben auch bei ausgeschaltetem Schalter erreichbar, damit nichts liegen bleibt. Die Frist gilt auch bei
  angehaltenem Eingang (Stopp `eingang`): Was länger als 90 Tage nicht abgeholt wurde, wird ungesehen gelöscht. ·
  Hauptsitzung nach Code-Prüfung
- **Recherche bleibt nie offen:** Nachrecherche durch den Radar, zweite KI prüft, Ende immer als Entwurf oder
  verworfen mit Grund; keine Links von Hand. Termin-Seiten liefern ihre strukturierten Angaben (Datum, Uhrzeit,
  Adresse) mit. · Luis („Es muss alles mit der Recherche klappen … auch keine Links einfügen“)
- **Ja zu allem (21:50):** F0–F4 mit allen Vorschlägen, Regelwerk Social Fassung 1; Gedenk-Sperre für alle
  Terminquellen (dann Tempel Backnang an, mit Festauswahl `params.nur_titel`); Veranstalter STCC gesperrt
  (`[blocklist] veranstalter`); dein-dein.de an. Design: keine Auswahl, mehrere fertige Linien (A Tagesblatt, B
  Kalenderblatt, C Aushang, D Terrazzo), Luis wählt. Nicht automatisch: Freigabe der Rückblick-Entwürfe, Echtbetrieb
  neuer Funktionen, Tore B1–B3. · Luis (`docs/abnahme/2026-11-13-ja-zu-allem.md`)
- **Design aller bisherigen Runden abgelehnt, Neugestaltung mit Hallmark:** `mix-ordnung`, `mix-feed` und alles davor
  gelten als „komplett generisch“. Neuer Brief `design/brief-v3.md`; gestaltet wird mit dem Hallmark-Skill (Floor,
  Reflex-Gates, `sloplint --render`, Prüfung aus frischem Kontext). Der Hallmark-Floor geht den alten Regeln aus
  `tamil-marke`/`tamil-richtung` vor (keine Dachzeilen, keine Versal-Labels, keine „·“-Metazeilen). Website **und**
  Cockpit werden neu gestaltet. · Luis · „generischer AI-Slop“, der Auftrag hat Gewicht.
- **Neugestaltung auf Anordnung von Luis, ohne Umweg über `/design-runde`:** Die Hauptsitzung baut die erste Probe
  selbst (die Sitzung stand im Planmodus, Hintergrund-Agenten durften nicht schreiben); die Prüfung kommt trotzdem
  aus frischem Kontext (`design/kritik/hm-eigen-r1.md`). Abnahme durch den Auftraggeber bleibt Tor G4. · Luis
  („alles selber entscheiden“), Hauptsitzung
- **Erste Probe „Tagesblatt“ (`design/richtungen/hm-eigen/`):** Das Datum ist die Hauptfigur wie im tamilischen
  Küchenkalender; Rot (Logo-Rot) nur für Sonntage, Festtage, Logo, einen Primärknopf und den Fokus; Bananenblatt-Grün
  nur für den Kino-Bereich; Rethink Sans und Golos Text (OFL, selbst gehostet). · Hauptsitzung
- **Vertrag ohne weitere Festlegungsrunde bauen:** „Alle Sachen, die im Vertrag drinstehen“ gilt als Ja zu F4
  (Instagram, Facebook, WhatsApp-Entwurf; Trockenmodus bis Konten von KBS und Freigabe des Regelwerks) und als Ja
  zum Bau von F0–F3 auf dem Testsystem mit den Vorschlägen der Festlegungen; im Echtbetrieb bleiben neue Funktionen
  per Schalter aus, bis Auftragsverarbeitung und Rechtstexte vorliegen. · Luis
- **Lizenzpflicht für jedes Bild:** vollständiger Lizenz-Datensatz oder keine Freigabe; fehlt er, trägt die Redaktion
  ihn im Cockpit ein. Reihenfolge der Quellen und Felder in `docs/spezifikation/bilder-und-lizenzen.md`. · Luis
- **Software-Spezifikation** `docs/spezifikation/` ist ab jetzt die Grundlage für alle Bausteine (Felder,
  Statusmaschinen, Agenten, Automationen, Integrationen). · Luis („die ganze Software definieren“)

## 12.11.2026

- **Gedenk-Sperre um Namen von LTTE-Gedenkanlässen erweitert, Terminquelle Vizha an:** `[blocklist] termine` nennt
  zusätzlich Thamilselvan, Brigadier (பிரிகேடியர்), Thileepan, Annai Poopathi/Poopathy, Prabhakaran (jeweils auch in
  Tamil-Schrift); Kittu/Kiddu/கிட்டு stehen in `termine_wort` und treffen nur als ganzes Wort (nicht „Kittur“, nicht
  das Verb „கிட்டும்“). Gesperrt wird nur die automatische Story; eine Redaktion kann solche Termine weiter von Hand
  bearbeiten. · Hauptsitzung · Die Vizha-Probe zeigte drei Gedenkturniere ohne Sperrbegriff (Thamilselvan Memorial
  Cup Dormagen, Colonel Kiddu Cup Rafz, Kiddu Cup Junior Seon); nach der Erweiterung blieben 28 Termine ohne
  Gedenkbezug, daher läuft „Vizha · Termine DACH“.
- **Ausland-Regel: Genf und Romandie zählen als DACH-Hinweis, Ajith nur als „Ajith Kumar“:** Genf/Geneva/Genève/ஜெனீவா
  (UN-Menschenrechtsrat, Kundgebungen) und Orte der Romandie (Lausanne, Fribourg, Neuchâtel, Sion als ganzes Wort …)
  halten eine Meldung drin; in der Kollywood-Ausnahme zählen Starnamen nur als ganze Wörter. Bekannte Restfälle, die
  durchkommen und im Cockpit abgelehnt werden: „ajith“ über die Kino-Hinweise der Kategorien, „Geneva Conventions“,
  „Credit Suisse“, Sion in Mumbai, TVK-Politik über „Vijay“; die Schreibweise ஜெனிவா fehlt noch. · Hauptsitzung nach
  drei Prüfrunden · Gegenüber dem Stand vor der Regel ist keiner davon ein Rückschritt.
- **Terminquelle Tempel Backnang vorerst aus:** Die Gedenktermin-Sperre (`[blocklist] termine`) wirkt heute nur bei
  `tribe_events`-Quellen; ob sie für alle Terminquellen gilt, entscheidet Luis (ändert Abnahme-Szenarien 15, 22–26).
  München Tamil Sangam (`tribe_events`) läuft. · Hauptsitzung nach unabhängiger Prüfung
- **Deutschsprachiger Text gilt für die Ausland-Regel als DACH-Presse:** Deutschsprachige Auslandsnachrichten (z. B.
  tagesschau zu Tamil Nadu) bleiben deshalb vorerst drin, wie vor der Regel. · Hauptsitzung · Ohne Anthropic-Schlüssel
  gibt es keine Grauzonen-Entscheidung; die Redaktion lehnt im Cockpit ab. Wieder ansehen mit Tor B1.
- **Der Verlagsname am Ende von Titel/Anriss ist kein Inhalt:** Er zählt für die Ausland-Regel weder als Bezug noch als
  DACH-Hinweis; in `score_item` und `hat_bezug` zählt er vorerst weiter. · Hauptsitzung
- **Kollywood und Stars gelten für die Ausland-Regel als Kino/Entertainment:** Nachrichten ohne DACH-Bezug aus der
  Kollywood-Quelle (`kollywood = true`) oder mit einem Begriff aus `[bezug] kollywood` (Kollywood, Rajinikanth, Vijay,
  Ilaiyaraaja …) fallen nicht als „ausland“ heraus, auch wenn die Stichwörter der Kategorien „news“ ergeben. ·
  Hauptsitzung nach unabhängiger Prüfung · „Rajinikanth meets Tamil Nadu Chief Minister“ und „Ilaiyaraaja honoured by
  India“ fielen sonst heraus.
- **Design: Mischung aus `klar2` und den Gen-Z-/Feed-Entwürfen, überall Bilder.** Das Live-Design (Runde 2) ist für
  Luis „hässlich und klassisch“; frühere Entwürfe fand er besser. Zwei Probeseiten (`mix-ordnung`, `mix-feed`), dann
  entscheidet Luis (G3). Jeder Anreißer mit Bild (nur mit Nachweis). Die Haltung „im Zweifel leiser“ aus Runde 2 gilt
  für diese Runde nicht mehr; die Verbotsliste (`abgelehnt.md`) gilt weiter. · Luis · `docs/abnahme/2026-11-12-design-luis.md`
- **Schreib-Automatik später:** Kein Anthropic-Schlüssel und keine tägliche Routine vorerst; der Radar scannt weiter, das
  Schreiben bleibt manuell über den Agent-Modus. · Luis

## 11.11.2026

- **Bild mit Nachweis (`POST /api/agent/bild`):** Ein Agent darf für einen wartenden Entwurf ein Bild vorschlagen, der
  Radar prüft Herkunft und Rechte selbst und setzt Nachweis und Lizenz aus Commons bzw. dem Register, nie aus dem
  Vorschlag. Erlaubt: Wikimedia Commons nur mit Lizenz-Adresse bei creativecommons.org (CC BY, CC BY-SA; nichts mit NC
  oder ND) und eigenes Material von Hosts aus dem Register `[[bildquellen]]` (Tempel, Vereine, Veranstalter, Kinos;
  Plakate gehören dem Verleih), nur wenn die Seite ein Beleg der Story ist. Abgelehnt: Agenturbilder, Logos, Banner,
  Bilder auf fremden CDNs, soziale Netzwerke, KI-Bilder. · Hauptsitzung nach vier unabhängigen Code-Prüfungen · Luis
  will „überall Bilder“, aber keine fremden Fotos ohne Recht.
- **Freigabe gilt nur für den gesehenen Stand:** Jeder Entwurf trägt einen Zähler `stand` (Migration 6, Trigger bei
  jeder inhaltlichen Änderung). Freigabe, Sammelfreigabe und Veröffentlichen nehmen den Stand mit, den die Redaktion
  gesehen hat; hat sich der Entwurf inzwischen geändert (z. B. ein Bild kam dazu), wird die Freigabe abgelehnt
  („veraltet“). Belege und Claims zählen den Stand bewusst nicht, weil sie den Text nicht ändern. · Hauptsitzung
- **Rückblick 2026:** Die Website bekommt die wichtigsten Ereignisse des Jahres 2026 aus der tamilischen Community in
  Deutschland, Österreich und der Schweiz als neu geschriebene Beiträge; der Altbestand bleibt unverändert stehen.
  Neueste zuerst. · Luis („komplett auffrischen, nur mit Daten aus 2026, die aktuellen nach oben, nichts löschen“)
- **Nachtrag statt Rückdatierung ohne Hinweis:** Jeder Rückblick-Beitrag trägt das Datum des Ereignisses und am Ende
  den Vermerk, dass er im November 2026 für den Rückblick geschrieben wurde. Im Cockpit steht „Nachtrag · Datum“. ·
  Hauptsitzung · Ein Beitrag darf nicht so aussehen, als sei er damals erschienen.
- **Vorschläge für den Rückblick kommen über `POST /api/agent/vorschlag`**: Thema, Datum und ein bis sechs Quellen.
  Der Radar ruft die Quellen selbst ab; Titel, Herausgeber und Text zählen nur aus der abgerufenen Seite. Für
  Nachträge läuft nie ein bezahlter Modell-Job; eigene Tagesgrenze `RADAR_NACHTRAG_TAG`. · Hauptsitzung nach
  unabhängiger Code-Prüfung
- **Länge nach Stofflage:** wenig Stoff (unter 4 bestätigte Aussagen) Kurzmeldung 80–150 Wörter; mittel (4–7, mit
  Volltext) 250–400; viel (ab 8 aus zwei Verlagen oder aus einer Primärquelle mit Volltext) 450–750, Kino und Termine
  350–550; Dossier 600–1000. Zwischentitel ab 350 Wörtern. Ohne Volltext nie mehr als knapp. · Luis („nicht nur eine
  Minute, sondern mehrere Minuten“) · Länge entsteht nur aus belegtem Stoff, nicht aus Füllsätzen.
- **Stil wie die alte Seite:** 19 Beispiele aus dem Altbestand dienen als Tonvorlage (je Story zwei passende). Viele
  lange Altbeiträge sind aus anderen Medien übernommen; sie sind nur Vorbild für den Ton, neue Beiträge entstehen aus
  den Quellen. · Luis („genau in dem gleichen redaktionellen Stil“)
- **Freigabe bleibt bei Luis:** Rückblick-Beiträge erscheinen erst nach Freigabe im Cockpit; neu ist „Ausgewählte
  freigeben“ (bis 100 auf einmal). · Hauptsitzung · Vertrag §8 Abs. 1
- **Bilder:** Plakate und Szenenbilder vom Verleih, Material von Veranstaltern, Tempeln, Vereinen und von der
  betroffenen Person selbst, Wikimedia Commons mit Lizenz, später eigene Instagram-Bilder; jeweils mit Nachweis. Sonst
  die Bildkarte „Grafik: Tamil.de“. Keine Agenturfotos aus anderen Medien (dpa, Keystone, Getty …), keine KI-Bilder.
  · Luis („mit allen Bildern, alles Mögliche“), Grenze bei Agenturfotos: Hauptsitzung · Fremde Agenturfotos sind
  ohne Lizenz ein Abmahnrisiko für KBS.
- **Instagram als Quelle nur über einen Export oder den offiziellen Zugang von Meta**, nicht durch Auslesen der
  Seite. Der Rückblick startet ohne Instagram. · Luis („ausgenommen von Instagram kannst du es trotzdem machen“) ·
  Vertrag §3 Abs. 3
- **Laufende Automatik für neue Meldungen:** Der Radar bekommt weitere Quellen aus einer Quellen-Inventur. Schreiben
  ohne Zutun braucht den Anthropic-Schlüssel (Tor B1) oder bis dahin eine tägliche Runde im Agent-Modus. · Luis („eine
  Automation, dass immer alles neu rausgesucht wird“)
- **Angaben für Suchmaschinen und Cache-Kopfzeilen haben keinen eigenen Schalter** und sind live; sie enthalten keine
  Geschäftsregel. Auf das Ja zu F0 warten nur die Rollen-Zuordnung, das Einschalten des Cookie-Hinweises und die
  Löschfristen. · Hauptsitzung nach Code-Prüfung
- **Das Testsystem ist für Suchmaschinen gesperrt**, solange `WP_ENVIRONMENT_TYPE` nicht `production` ist (noindex,
  `robots.txt`, keine Sitemap). · Hauptsitzung · Sonst stünden 535 Beiträge doppelt im Netz.
- **Der Vertrag ist der Maßstab.** Für tamil.de gilt Anlage 1, Teil A und B des Gesamtvertrags (Vertragsstand
  11.11.2026). Das Leistungsverzeichnis steht in `docs/vertrag/leistungen.md`; Preise, Zahlungsplan und die
  Vertragsdatei liegen nicht im Repo. Merzlicht und AJ Gamestation sind eigene Projekte. · Luis („genau so müssen wir
  das angehen, alles für tamil.de übernehmen und fertig machen, genauer definieren zusammen“)
- **Reihenfolge der Bausteine:** Grundlage, dann Formulare und Verzeichnis, dann Werbebuchung, dann Instagram und
  Facebook. · Luis · Formulare und Verzeichnis brauchen am Anfang nichts von KBS, und die späteren Bausteine bauen
  darauf auf.
- **Zahlungsanbieter: Stripe**, zuerst im Testmodus; KBS legt später ein eigenes Konto an. · Luis
- **Erst festlegen, dann bauen:** Je Baustein eine Festlegung (`docs/vertrag/festlegung-<baustein>.md`, für Luis als
  Reiter im Projekt-Dokument); Luis bestätigt oder ändert, dann wird gebaut. Neue Tore F0 bis F4. · Luis · Der
  Vertrag verlangt für alles Automatische freigegebene, dokumentierte Regeln (§8 Abs. 1).
- **Website und Cockpit bleiben getrennt abnehmbar:** WordPress hält Öffentliches, Kunden und Geld (Formulare,
  Verzeichnis, Werbebuchung, Zahlung); das Cockpit hält Agenten, Prüfung, Freigabe, Zeitplan, Stopp und Protokoll.
  Der Radar holt bei WordPress ab, nie umgekehrt. · Hauptsitzung nach gegengeprüftem Bauplan
- **Keine automatische E-Mail, auch keine Bestätigungen** (§8 Abs. 2). Rückmeldung steht auf der Website; die
  Buchungsübersicht kommt über einen geheimen Link. Ein Test sichert ab, dass im Code kein Mailversand vorkommt. ·
  Hauptsitzung
- **WhatsApp bleibt Handarbeit:** Entwurf zum Kopieren, weil Meta für Kanäle keine Schnittstelle zum Veröffentlichen
  nennt (geprüft in der Doku von Meta am 11.11.). · Hauptsitzung · Vertrag B3, §3 Abs. 3
- **Neue Funktionen sind im Echtbetrieb aus**, bis Auftragsverarbeitung und Rechtstexte vorliegen; auf dem Testsystem
  (Vorschau-Adresse) laufen sie. · Hauptsitzung · §8 Abs. 3
- **„Alle Szenarien“ statt „51/51“:** Die Abnahme des Radars wächst mit den Bausteinen; die Regel nennt keine feste
  Zahl mehr. · Hauptsitzung
- **Website steht mit dem vollen Altbestand** (532 Beiträge, 7 Seiten, 1445 Medien, 25 Weiterleitungen; Stichprobe,
  alle Weiterleitungen und der zweite Lauf ohne Befund). Der Radar ist verbunden und veröffentlicht Freigegebenes
  direkt. · Ablauf `/website-live` · Prüfliste in `docs/abnahme/2026-11-11-uebernahme.md`
- **Coolify-Zugang über Tokens aus dem Chat.** Luis hat zwei Tokens als Bildschirmfoto gegeben und angewiesen, sie zu
  verwenden („behalte den und mache“); der DNS-Eintrag für das sichere Formular wurde nicht gesetzt. Die Werte liegen
  nur in Sitzungsdateien, wurden nie ausgegeben und nur für die beiden Tamil-Apps benutzt. Beide Tokens sind zu
  widerrufen (Tor B2). Das löst den Eintrag vom 10.11. („Zugang bleibt beim DNS-Namen“) für die Einrichtung ab; als
  Zielzustand bleibt er richtig. · Luis

## 10.11.2026

- **Website geht jetzt auf Coolify, mit echten Inhalten und dem bisherigen Theme** (App „tamil-web“ unter der
  Vorschau-Adresse; voller Altbestand, Radar verbunden). Das neue Design `klar2` folgt als Theme nach dem Urteil des
  Auftraggebers und der Probeseite. · Luis („alles auf Coolify pushen, deployen“; auf Rückfrage: Website mit echten
  Inhalten)
- **Die drei schon freigegebenen Entwürfe** (Diwali in Basel, „Scene“, „Ramayana“) **erscheinen beim Verbinden alle
  drei.** · Luis · Diwali in Basel ist mit 73 Wörtern kurz und hat keine Quellenzeile; das war ihm bekannt.
- **Coolify-Zugang bleibt beim DNS-Namen:** Das sichere Formular nimmt nur echte Hostnamen an, die Adresse
  `coolify.167.233.76.202.sslip.io` lehnt es ab. Luis legt den A-Eintrag `coolify.hk-growthoperator.de` auf den
  Coolify-Server, trägt die Adresse in Coolify ein und erzeugt ein Token ohne Root-Rechte (Tor B2). · Luis · Die
  Alternativen (Token als Umgebungsvariable, App von Hand anlegen) hat er nicht gewählt.
- **Texte der alten Seite bleiben unverändert**, auch Kontaktangaben darin (`info@tamil.de` ist die echte Adresse der
  alten Seite). Leer bleiben nur die Kontaktfelder der neuen Website, bis der Auftraggeber die echten Werte nennt;
  die Beispielwerte aus `prototyp/content/site.json` werden nie eingetragen. · Hauptsitzung nach Code-Review · Das
  Import-Werkzeug hatte die Adresse zuerst aus 11 Beiträgen entfernt.
- **YouTube-Videos laden erst nach Klick** (Box „Video laden“, dann youtube-nocookie.com); das gilt für alle
  übernommenen Beiträge. · Hauptsitzung · Pflicht aus den Markenregeln (Drittanbieter erst nach Klick); der feste
  Player lief am Handy außerdem seitlich über.
- **`klar2` passt, das Aufmacherfoto bleibt groß (4:3).** `klar2` wird die Vorlage für den Auftraggeber; `klar`
  bleibt als Rückfall im Repo. · Luis · nach der internen Vorschau und dem Blick auf alle Bilder im Chat. Am Desktop
  stehen damit sechs statt rund zehn Schlagzeilen im ersten Bildschirm; das ist so gewollt.
- **`klar` bekommt mehr Wow: Fassung `klar2`.** Überall ein Bild (kein Anreißer ohne Bild), großes Aufmacherbild mit
  der Schlagzeile im Bild, Rubrikkacheln mit Bild, große Bildkacheln in „Küche“, ein dunkler Bereich „Diese Woche“,
  ein dreiteiliger Kopf mit dunklem Rubrikband, sanfte Bewegung. · Luis · nach dem Blick auf die Vorlage: „gut vom
  Design, aber noch ein wenig zu classic“; er hat alle acht angebotenen Verstärkungen gewählt.
- **Dafür gelockert, jeweils mit messbarer Grenze** (`design/brief.md`, Abschnitt 10): genau zwei dunkle Flächen in
  der kühlen Tinte (bisher: Dunkel verboten); heller Titel im Bild auf einem Verlauf (bisher: kein Verlauf, kein
  Text im Bild); Zoom beim Überfahren bis 1,04 und ein stehendes Rubrikband (bisher: keine Bewegung); Schlagzeile des
  Aufmachers bis 34 und 44 px (bisher 32 und 38); Kopf am Handy bis 152 px (bisher 120); drei Bildformate (bisher
  zwei); Aufmacherbild und je eine große Kachel bis zur Dateibreite. · Hauptsitzung nach Luis' Auswahl · Unverändert
  bleiben Rot höchstens 3 %, keine rote Schrift über 20 px, normale Schriftbreite, Radius höchstens 2 px, nur
  Deutsch. Runde 4 ist an „zu laut“ gescheitert; deshalb hat jede Lockerung eine Zahl.
- **Einträge aus dem News-Radar ohne Foto bekommen eine gestaltete Kachel**, kein erfundenes Bild. · Hauptsitzung ·
  Der Radar erzeugt für solche Beiträge schon heute eine Grafik („Grafik: Tamil.de“); deren Aussehen folgt später der
  abgenommenen Kachel.
- **Reihenfolge der Vorlage:** Luis sieht `klar2` zuerst in der internen Vorschau; die Vorlage für den Auftraggeber
  wird erst danach und nur ohne offenes P0 oder P1 ersetzt. · Hauptsitzung · Zwei Runden sind ungesehen
  weitergegangen und durchgefallen.
- **Probe `klar` wird ausgearbeitet** (nüchtern und kompakt nach BBC und Tagesschau, Schrift Libre Franklin). Brief 2
  ist damit bestätigt. · Luis · gewählt, ohne die Vorschau anzusehen; er sieht die Vorlage, bevor sie zum
  Auftraggeber geht. `blatt` und `bild` bleiben als Alternativen im Repo.
- **Vorlage für den Auftraggeber als eigenes Artifact**, getrennt von der internen Vorschau (dort liegen Bilder
  fremder Nachrichtenseiten zum Vergleich). · Hauptsitzung

## 09.11.2026

- **Neue Richtung: wie eine große Nachrichtenmarke.** Ruhig und seriös, viele Geschichten auf einen Blick, Rot nur
  als Akzent, normale Schrift; Vorbilder Zeit Online, Spiegel, Tagesschau/BBC, Guardian/NZZ. Das löst den Eintrag
  „Redesign für Gen Z: Hypebeast/Highsnobiety, Rot trägt die Seite“ weiter unten ab, ebenso „erster Bildschirm = die
  eine große Geschichte“ und „laut im Kopf“ vom selben Tag. · Luis · nach Ablehnung der vier Richtungsskizzen („zu
  viel Rot, zu laut“, „Baukasten“, „Schrift ist hässlich“, „nicht hochwertig genug“).
- **Prüfung misst statt zu bepunkten.** Die Summe 28/40 ist kein Tor mehr. Durchgelassen wird, was die harten
  Kriterien des Briefs erfüllt und kein offenes P0 oder P1 hat. Luis sieht Schnellproben früh und ungefiltert; der
  Auftraggeber sieht weiter nur Gewähltes und Bestandenes. · Hauptsitzung, von Luis mit „mache es weiter“ getragen ·
  Drei Skizzen hatten mit genau 28/40 bestanden und fielen bei Luis sofort durch.
- **Design-Runde 1, Ergebnis der Kritik:** `zine`, `raster` und `feed` bestehen nach einer Überarbeitung mit je
  28/40 und kommen auf die Vergleichsseite. `plakatwand` erreicht 29/40, hat aber ein offenes P1 und wird nach der
  Regel „nur bestandene“ nicht gezeigt. Stand in `docs/abnahme/2026-11-09-G2.md`. · Ablauf `/design-runde`
- **Radar: keine Ländernamen in der Ausland-Liste.** „Sri Lanka“ oder „Indien“ stehen in fast jedem Bericht der
  Diaspora und würden echte Termine ohne bekannte Stadt verwerfen; in der Liste stehen nur Orte. Altersgrenze für
  Termin-Berichte: 30 Tage (`RADAR_EVENT_MAX_ALTER_TAGE`). · Code-Review, Hauptsitzung
- **Tor G1 bestätigt (vorläufig):** Brief `design/brief.md` mit den Vorbildern des Scouts; die Auswahl des
  Auftraggebers fließt bis G2 ein. Alle vier Richtungen gehen in die Skizzenrunde. · Luis · Die Runde soll nicht auf
  die Rückmeldung warten.
- **Nur Deutsch:** keine tamilische Schrift als Gestaltungsmittel. Die Richtung „Raster + Tamil-Schrift“ wird zu
  „Raster + große Schrift“. · Luis
- **Erster Bildschirm = die eine große Geschichte** (Cover); Kino und Events folgen als zweiter Abschnitt. Laut im
  Kopf, ruhig im Text. · Luis
- **Radar: nur Meldungen mit tamilischem Bezug.** Allgemeine Schweizer Meldungen (Unfall, Polizei, Wahl) erscheinen
  nicht; Quellen, die solche Meldungen liefern, verlangen ein Community-Stichwort. · Luis · Leser finden das auf
  Deutsch überall, und jede Recherche kostet.
- **Coolify-Zugang über DNS-Namen und sicheres Formular:** `coolify.hk-growthoperator.de`, enges Token statt
  Root-Token, Wert nie im Chat (Tor B2). · Luis
- **Projekt-Ordnung (Phase 7):** `CLAUDE.md`, `docs/`, `design/`, Bereichsregeln, 12 Skills, 10 Agents, 7 Commands, vier
  Abnahme-Tore. · Luis · Drei Designrunden sind am Ablauf gescheitert, das Wissen lag nur im Chat.
- **`prototyp/` bleibt Archiv**, Pfade unverändert; `prototyp/content/` bleibt Datenquelle. · Luis · Kein Umbau ohne
  Nutzen.
- **PR #1 wird jetzt gemergt** (Merge-Commit), PR #2 danach gegen `main`; PR #2 wird nach Tor G4 gemergt. · Luis
- **Adressen:** Der Radar bleibt unter `tamil.hk-growthoperator.de`, die Website läuft vorerst unter
  `tamil-web.167.233.76.202.sslip.io`. · Luis · Kein DNS-Aufwand jetzt.
- **Agents mit gemischten Modellen:** Opus für Gestalten, Bauen, Kritik, Code-Prüfung, Redaktion; Sonnet für
  Referenzsuche, Technik-QA, Migration. · Luis · Qualität dort, wo sie zählt, Limit schonen.
- **Kritik-Filter:** Der Auftraggeber sieht nur Richtungen mit mindestens 28/40 und bestandenem Slop-Test. · Luis
- **Abnahmen über Luis**, Referenzen aus Auftraggeber und Scout, Design und Website-Livegang parallel, alle vier
  Richtungen in die Skizzenrunde (Kollywood-Plakatwand, Diaspora-Zine, Raster + Tamil-Schrift, Vertikaler Feed). · Luis
- **Gen-Z-Probeseite abgelehnt** („Trash, komplett generisch“, aber „viel Potenzial, Luft nach oben“). · Auftraggeber
  über Luis · Siehe `.claude/skills/tamil-marke/references/abgelehnt.md`.
- **Redesign für Gen Z:** jung und alt gleich lesbar, Hypebeast/Highsnobiety und Instagram/TikTok als Richtung, Rot trägt
  die Seite, helles Grundbild. · Auftraggeber über Luis · Community-Magazin galt als „altbacken, hingerotzt“.
- **Keine Demo-Inhalte:** Der ganze echte Altbestand von tamil.de wird übernommen (Originaldatum, Slug, Bilder, Seiten,
  301-Weiterleitungen). · Luis
- **„Freigeben“ veröffentlicht sofort** (`WP_POST_STATUS=publish`). · Luis
- **Website als zweite Coolify-App** (WordPress mit SQLite, ein Container). · Luis
- **Agent-Modus übers Netz** (`/api/agent/export|import`, eigenes Token): wartende Storys schreibt eine Claude-Sitzung
  ohne API-Kosten. · Luis · Der Anthropic-Schlüssel fehlt noch.
- **Radar komplett in Coolify** (ein Container: Cockpit, Scan, Worker, Digest, Sicherung), gebaut von
  `claude/radar-multiagent`. · Luis · Statt systemd auf dem HK-Server.
- **Pilot:** 2 $ pro Tag und Monat, 5 Entwürfe pro Tag, keine KI-Bilder, 20 Quellen, Modelle je Rolle wie gesetzt. · Luis
- **Ausland-Filter:** Termine außerhalb von DE/AT/CH werden verworfen (Kanada, UK, Sri Lanka, Indien …). · Ergebnis des
  kostenlosen Pilot-Scans.
- **Root-Token nur für die Einrichtung**, danach widerrufen (Tor B2). · Luis

## 08.11.2026

- **Nachtlauf freigegeben:** Multi-Agenten-Redaktion nach dem Blueprint vom 19.10. ohne Rückfragen bauen. · Luis

## 20.10.2026

- **Blueprint umgesetzt:** Branch `claude/radar-multiagent` mit eigenem PR; Modelle je Rolle (Haiku: Signal, Cluster,
  Lektorat, SEO · Sonnet: Recherche, Faktencheck, Text · Opus: Dossier); keine Embeddings; 20 aktive Quellen;
  Bildreihenfolge Archiv → Quelle → Stock → Pool → KI → Karte. · Luis
- **Newsletter komplett entfernt** (Theme, Plugin, Prototyp, Doku). · Luis
- **Erster Entwurf (Nachtblau, Gold, Ornamente, Tamil-Wörter vor Überschriften) abgelehnt** als „Katastrophe“. ·
  Auftraggeber
