# Tamil.de — Branding Master Handoff für Plot (v1.1, 19.11.2026)

> Vom Auftraggeber (Luis) übergebene Fassung, inhaltlich unverändert übernommen. Ausführender Agent („Plot“) ist die
> Website-Sitzung. Sie ist verbindlich für Branding-Entscheidungen. Neuere Übergaben ersetzen sie Schritt für Schritt.

**Projekt:** Tamil.de — Marken-Relaunch / Designsystem

**Status:**
- Schritte 1 und 2 sind in der kreativen Richtung entschieden.
- Technische Integration und Detailfreigabe stehen noch aus.

**Zweck:** Diese Datei ist die verbindliche Übergabe der bisher gemeinsam getroffenen Branding-Entscheidungen.
- Plot soll nicht eigenständig eine neue Marke, ein Logo oder ein Website-Theme entwerfen.
- Die offenen Branding-Schritte werden nacheinander mit dem Auftraggeber entschieden und jeweils in einer neuen
  Markdown-Übergabe dokumentiert.

## 0. Die wichtigste Abgrenzung

**Tamil Dots 04A ist NICHT das Logo.** Es ist das wiederkehrende grafische Signature-Element des Content- und
Interface-Designsystems. Eingesetzt wird es als charakteristischer Punktbogen, zum Beispiel in:
- News-Karten und Beitragsgrafiken
- Website-Modulen
- Instagram-, Facebook- und WhatsApp-Inhalten

**Das bestehende Tamil.de-Logo bleibt unabhängig davon bestehen:**
- keine Logo-Neugestaltung
- kein Logo-Austausch
- keine Verschmelzung von Dots und Wortmarke ohne gesonderte Freigabe

**Ausrichtung der Marke:**
- Tamil.de soll sich als moderne, futuristische tamilische Community-Marke für Menschen im DACH-Raum entwickeln, nicht
  bloß als klassisches Nachrichtenmagazin.
- News bleiben dennoch ein wesentlicher Content-Typ.
- Die grafische Wiedererkennbarkeit muss gerade bei wiederkehrenden News-Posts funktionieren.

## 1. Entschiedene Farbwelt (Schritt 1, abgeschlossen)

| Rolle | Bezeichnung | HEX | Status |
|---|---|---|---|
| Dominante Markenfarbe | Titan Red | `#660000` | Festgelegt |
| Roter Akzent | Impact Red | `#B30000` | Festgelegt |
| Hintergrund | Reinweiß | `#FFFFFF` | Verbindlich, insbesondere für Website-Grundflächen |
| Typografie / Kontrast | Schwarz | `#000000` | Festgelegte Grundfarbe |

**Farbrichtung:** C, Red Dominance / Power.

**Gewichtung:**
- Orientierende Werte: 50 % Weiß, 35 % Titan Red, 10 % Impact Red, 5 % Schwarz.
- Das sind gestalterische Richtwerte, keine starre Flächenberechnung für jede einzelne Karte.
- Weiß bleibt der verpflichtende Website-Hintergrund.
- Keine neuen Hauptfarben, keine Orange-, Pink-, Gold- oder Violett-Akzente ohne ausdrückliche Entscheidung.

```css
:root {
  --tamil-color-background: #FFFFFF;
  --tamil-color-primary: #660000;
  --tamil-color-accent: #B30000;
  --tamil-color-text: #000000;
}
```

**Technische Prüfung vor Produktivsetzung:**
- Kontrast und Lesbarkeit für kleine Texte, Hover- und Focus-Zustände sowie mobile Ansichten testen.
- Für funktionale Zustände ggf. weitere neutrale oder semantische Tokens vorschlagen, nicht ungefragt als neue
  Markenfarben festlegen.

## 2. Signature-Element (Schritt 2, Richtung festgelegt)

- **Name:** Tamil Dots 04A.
- **Status:** Aus mehreren Richtungen ausgewählt und als visuelles System bestätigt.
- **Gestalt:**
  - ein markanter, geschwungener, kuppel- bzw. bogenförmiger Verlauf aus einzelnen elliptischen Punkten;
  - links größer und dichter, nach rechts feiner auslaufend;
  - eine charakteristische freie Fläche unter dem Bogen;
  - in Titan Red und Impact Red, auf weißem bzw. transparentem Grund.

**Verbindliche gestalterische Prinzipien:**
1. Die Silhouette und das charakteristische Verhältnis großer zu kleiner Punkte beibehalten.
2. Dots sind ein Designmotiv, keine neue Wortmarke und kein Ersatz für das bestehende Logo.
3. Ein konsistentes Kartensystem für Nachrichten und Community-Inhalte entwickeln. Dieselbe grafische DNA gilt über
   Instagram, Facebook, WhatsApp und Frontend hinweg, angepasst an Format und Inhalt.
4. Die Dots dürfen Bilder rahmen, hinterlegen oder die Bildkomposition gliedern. Überschriften oder Gesichter dürfen sie
   nie unlesbar überlagern.
5. Die Bildsprache soll jung, redaktionell, kraftvoll und modern sein, nicht wie eine beliebige Tech-Website.
6. Keine Pfeile oder zusätzlichen geometrischen Signature-Symbole erfinden.
7. Motion ist später möglich, muss aber auch als statisches Motiv funktionieren.

### Referenz und SVG-Neuerstellung durch Claude (verbindliche Korrektur)

**Abgelehnt:** Die zuvor von ChatGPT erstellten Dateien `Tamil_Dots_04A_Vector.svg` und `Tamil_Dots_04A_Preview.png`.
Nicht verwenden, nicht übernehmen und nicht als Master referenzieren. Sie entsprechen der ausgewählten Bildform nicht
ausreichend.

**Referenz:**
- Claude erstellt das SVG selbst von Grund auf.
- Grundlage ist die freigegebene Original-Bildreferenz `vier_rote_punktmarken_für_tamil.de.png`, ausschließlich Feld A
  oben links.
- Ist die Referenz in Claudes Arbeitsumgebung nicht vorhanden, wird sie zuerst beim Auftraggeber angefordert. Keine
  Rekonstruktion allein aus der Beschreibung als angeblich originalgetreu ausgeben.

**Anforderungen:**
1. Ausschließlich die Form 04A rekonstruieren: breiter, geschwungener Bogen aus einzeln angeordneten elliptischen
   Punkten; markante freie Unterseite; die Punkte laufen nach rechts kleiner aus.
2. Das SVG als echte editierbare Vektorgeometrie erstellen, ohne eingebettete PNG/JPG-Bilder, mit transparentem
   Hintergrund.
3. Die Farbpalette auf #660000 und #B30000 begrenzen. Der weiße Hintergrund gehört zur Anwendung, nicht zwingend in die
   SVG-Datei.
4. Referenz und SVG bei gleicher Größe nebeneinander und halbtransparent übereinander vergleichen: Gesamtsilhouette,
   Bogenhöhe, Auslauf, Punktgröße, Abstände, Ausrichtung und Negativraum.
5. Bei Bedarf mehrfach nacharbeiten. Auch ein visuell ähnliches SVG ist nicht automatisch final freigegeben.
6. Zusätzlich eine optisch reduzierte Kleinformat-Version vorbereiten, aber als separaten Entwurf, nicht als Ersatz für
   das Master-SVG.
7. Vor Einbau in Frontend, Backend oder Social-Templates Vergleichsvorschau und SVG zur expliziten Freigabe vorlegen.
8. Das bestehende Logo bleibt unverändert. Die Dots sind ein Content- und Frontend-Designmotiv und kein Logo.

**Status:** SVG-Neuerstellung durch Claude beauftragt bzw. vorgesehen, noch nicht erstellt oder freigegeben. Die
grafische Richtung 04A ist bestätigt.

### Beispiel für die Verwendung

Ein News-Post besteht grundsätzlich aus:
- dem unveränderten Publisher-Logo bzw. Absender;
- einer einheitlichen Rubrikkennzeichnung;
- einer gut lesbaren Headline;
- einem passenden redaktionellen Foto bzw. Medieninhalt;
- Tamil Dots 04A als erkennbarer, wiederkehrender grafischer Rahmen- oder Hintergrundkomponente.

Das zuletzt gezeigte Beispiel hat der Auftraggeber ausdrücklich als Richtung bestätigt: dieselbe Headline, dasselbe
Foto und derselbe Dots-Bogen für Instagram, WhatsApp und Facebook. Es ist ein visuelles Prinzip, noch kein
pixelgenau freigegebenes Template oder finaler Exportstandard.

## 3. Umsetzung über alle Kanäle

| Oberfläche | Gewünschtes Verhalten | Noch zu entscheiden |
|---|---|---|
| Website-Frontend | Dots als konsistentes Gestaltungselement in passenden News- und Community-Modulen; weißer Grund | genaue Module, Abstände, Responsive-Verhalten |
| Redaktions-Backend | Wiederverwendbare, zentral gepflegte Karten-Templates statt Einzelgestaltung pro Post | bestehende Architektur, Datenmodell, Exportprozess |
| Instagram | Wiedererkennbarer Feed-, Story- und Reel-Look mit denselben Farb- und Dot-Regeln | Formate, Typografie, Platzierungsraster |
| Facebook | Gleiche Designsprache, formatgerechter Zuschnitt | Formatregeln |
| WhatsApp | Lesbare, kompakte Variante derselben Karte | Bildgröße, Textlänge, Versandprozess |

Keine eigenständige Neugestaltung je Kanal. Ziel ist ein Designsystem mit mehreren responsiven bzw. formatbezogenen
Ausgaben.

## 4. Technische Arbeitsanweisung für Plot

### Jetzt erlaubt

1. Diese Markdown-Datei als Designentscheidung dokumentieren.
2. Die Original-Bildreferenz für 04A prüfen, die SVG-Neuerstellung durch Claude vorbereiten und eine Vergleichsvorschau
   zur Freigabe erstellen.
3. Vorhandene Frontend-, Backend- und Social-Template-Komponenten inventarisieren.
4. Ein Umsetzungskonzept für wiederverwendbare Design-Tokens und eine zentrale TamilDots04A-Komponente erstellen.
5. Technische Risiken benennen: SVG-Komplexität, kleine Größen, Accessibility, Bildzuschnitt, Exportqualität,
   Wartbarkeit.
6. Fragen sammeln, die eine Designfreigabe erfordern.

### Noch nicht erlaubt

- das bestehende Logo ersetzen oder verändern;
- neue Website-Themes oder eigenständige Markenwelten entwickeln;
- eine andere Signature-Form wählen;
- unabgestimmt neue Markenfarben einführen;
- bestehende produktive Layouts oder Redaktionsprozesse ohne ausdrückliche Freigabe überschreiben;
- ein generiertes Beispielbild als tatsächlichen Nachrichteninhalt veröffentlichen;
- SVG-Abweichungen als pixelgenaues Original ausgeben.

### Empfohlene technische Architektur (Vorschlag, noch nicht freigegeben)

- Zentrale Tokens für Farben, später auch für Typografie und Abstände.
- Nach Freigabe des von Claude rekonstruierten SVG: eine wiederverwendbare Komponente mit konfigurierbarer Größe,
  Position und optionaler Animation.
- Ein gemeinsames Karten-Datenmodell (category, headline, image, credit, timestamp usw. nach tatsächlichem Bedarf).
- Formatadapter bzw. Export-Templates für Instagram, Facebook, WhatsApp und Website.
- Visuelle Regressionstests für Layout und Responsive-Ausgaben.
- Versionierung der Assets und Freigabestatus pro Designsystem-Version.

## 5. Branding-Roadmap und Fortschritt

| Schritt | Thema | Stand |
|---|---|---|
| 1 | Markenfarben und Farbgewichtung | **Abgeschlossen** |
| 2 | Signature-Element / visuelles Content-Erkennungsmerkmal | **Richtung 04A beschlossen; technische Detailfreigabe offen** |
| 3 | Markenpositionierung | **Als Nächstes gemeinsam entscheiden** |
| 4 | Markenpersönlichkeit | Offen |
| 5 | Markensprache / Tonalität | Offen |
| 6 | Content-Rubriken und redaktionelle Formate | Offen |
| 7 | Typografie und Bildsprache | Offen |
| 8 | Plattformübergreifende Templates / Motion | Offen |
| 9 | Brand Guidelines und Implementierungsfreigabe | Offen |

Das bestehende Logo wird nur auf technische Einsetzbarkeit geprüft. Eine Logo-Neugestaltung ist nicht Teil dieser
Roadmap, sofern sie nicht separat beauftragt wird.

## 6. Nächster gemeinsamer Branding-Schritt: Positionierung

Die Positionierung ist noch nicht entschieden. Bisher diskutiert wurden drei Richtungen:

| Richtung | Leitsatz | Fokus |
|---|---|---|
| P1 — The New Generation | „Die Stimme einer neuen tamilischen Generation.“ | Identität, Zukunft, Kultur und Menschen |
| P2 — Tamil Pulse | „Der Puls der tamilischen Community.“ | aktuelle Entwicklungen, News und Gespräche |
| P3 — The Community | „Das digitale Zuhause junger Tamilen.“ | Zugehörigkeit und Verbindung im DACH-Raum |

Im Gespräch wurde P1 empfohlen, gegebenenfalls in Verbindung mit P2. Das ist keine Freigabe. Plot darf daraus noch keine
endgültigen Slogans oder Content-Regeln ableiten.

Als Nächstes entscheidet der Auftraggeber zwischen P1, P2, P3 oder einer definierten Kombination. Danach entsteht für
diesen Schritt eine eigene Markdown-Übergabe, und das Masterdokument wird versioniert.

## 7. Arbeitsmodus für alle weiteren Schritte

- Ein Branding-Thema nach dem anderen entscheiden. Mehrere Optionen nur innerhalb des aktuellen Themas.
- Bestehende Favoriten und festgelegte Entscheidungen immer übernehmen.
- Bei visuellen Entscheidungen echte Vergleichsbilder liefern, aber keine ungefragten Website- oder Logo-Entwürfe.
- Nach jeder Entscheidung eine aktualisierte .md-Datei für Plot bereitstellen.
- Klar zwischen festgelegt, Favorit, Vorschlag und noch offen unterscheiden.
- Keine stillschweigenden Entscheidungen und keine eigenmächtige Implementierung.

## 8. Übergabe-Checkliste für Plot

- [ ] Farb-Tokens übernehmen und dokumentieren.
- [ ] Freigegebene Original-Bildreferenz (Feld A) erhalten und öffnen.
- [ ] Claude erstellt ein neues editierbares SVG; bisherige SVG/PNG ausdrücklich verwerfen.
- [ ] SVG mit der Referenz vergleichen und dem Auftraggeber vorlegen.
- [ ] Explizite Freigabe des neuen SVG vor jeder Integration einholen.
- [ ] Bestehendes Logo unverändert lassen.
- [ ] Ist-Zustand von Frontend, Backend und Social-Templates erfassen.
- [ ] Vorschlag für ein gemeinsames Karten- und Export-System vorlegen.
- [ ] Vor jeglichem produktiven Einbau Freigabe einholen.
- [ ] Auf das Ergebnis des Positionierungs-Workshops warten.

**Korrektur v1.1:** Bisherige SVG/PNG abgelehnt. Claude rekonstruiert 04A neu anhand der Originalreferenz; keine
Integration vor Freigabe.

**Kurzbriefing für Plot:**
- Tamil.de bekommt keine neue Logoidentität, sondern ein einheitliches, wiedererkennbares visuelles Content-System.
- Festgelegt sind Weiß #FFFFFF, Titan Red #660000, Impact Red #B30000, Schwarz #000000, die Farbrichtung Red Dominance
  sowie das Signature-Motiv Tamil Dots 04A als grafischer Punktbogen.
- Die weitere Markenstrategie wird Schritt für Schritt entschieden.
- Nicht eigenmächtig redesignen oder deployen.
