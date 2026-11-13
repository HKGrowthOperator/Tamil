# Festlegung F4: Instagram, Facebook und WhatsApp-Entwurf

Vertrag: B2 (automatisches Instagram- und Facebook-Publishing), B3 (WhatsApp-Channel-Entwurf, E-Mail von Hand), §3
Abs. 3, §8 Abs. 1. Stand: **Ja von Luis am 13.11.2026 mit den Vorschlägen dieser Festlegung** (`docs/abnahme/2026-11-13-auftrag-luis.md`); gebaut wird auf dem Testsystem, im Echtbetrieb bleibt die Funktion per Schalter aus, bis Auftragsverarbeitung und Rechtstexte vorliegen. Live erst mit den Konten von KBS und der einmaligen
Freigabe des Regelwerks durch KBS. Gebaut wird zuerst im Trockenmodus (alles außer dem letzten Aufruf an Meta), bis die Konten
da sind.

## Was gebaut wird

1. **Erkennen:** Der Radar fragt die Website alle paar Minuten nach neu veröffentlichten Beiträgen und Terminen, auch
   nach solchen, die jemand von Hand in WordPress angelegt hat. Der übernommene Altbestand löst nie etwas aus.
2. **Prüfen gegen das Regelwerk** (unten). Erfüllt ein Beitrag alle Regeln, geht er automatisch weiter. Sonst steht
   er im Cockpit unter „von Hand entscheiden“ mit dem Grund.
3. **Vorbereiten:** Text aus Titel und Vorspann, feste Hashtags je Rubrik, Verweis auf tamil.de. Bild im Hochformat
   1080 × 1350 aus dem Beitragsbild; ohne Bildrecht für Social die Bildkarte „Grafik: Tamil.de“.
4. **Karenz von zehn Minuten:** In dieser Zeit lässt sich der Beitrag im Cockpit ändern oder stoppen.
5. **Veröffentlichen** auf Instagram und danach derselbe Inhalt auf der Facebook-Seite, über die offiziellen
   Schnittstellen von Meta. Keine zweite Freigabe bei regelkonformen Beiträgen.
6. **Historie im Cockpit:** je Beitrag und Kanal Stand, Zeit, Link zum Beitrag bei Instagram und Facebook, die
   Fassung des Regelwerks. Dazu Fehler, Dubletten, Pausen und alles, was nicht freigabefähig war.
7. **WhatsApp:** Für denselben Beitrag liegt im Cockpit ein Entwurf (Text, Link, Bild) mit „Kopieren“, „Bild
   herunterladen“ und „als gepostet markieren“. Veröffentlicht wird von Hand im Kanal, weil Meta für Kanäle keine
   Schnittstelle zum Veröffentlichen anbietet.

## Das Regelwerk (Vorschlag; KBS gibt es einmal frei, jede Änderung bekommt eine neue Fassung)

| Regel | Vorschlag |
|---|---|
| Rubriken | alle acht; „Nachrichten“ nur, wenn der Beitrag nicht als heikel markiert ist |
| Heikle Themen (Politik, Justiz, Unglück, Tod, Medizin) | nie automatisch, immer von Hand |
| Alter | Beitrag höchstens 48 Stunden alt; Termine nur, wenn sie in der Zukunft liegen |
| Bild | nur mit Recht zur Nutzung in sozialen Netzen; sonst Bildkarte |
| Menge | höchstens sechs Beiträge am Tag, mindestens 60 Minuten Abstand |
| Ruhezeit | zwischen 22 und 7 Uhr wird nichts veröffentlicht; Wartendes geht um 7 Uhr hinaus |
| Dubletten | jeder Beitrag höchstens einmal je Kanal; Korrekturen am Artikel lösen nichts erneut aus |
| Kennzeichnung | Bilder aus der KI tragen den Hinweis wie auf der Website |

## Was automatisch läuft und was nicht

| Automatisch | Nur durch einen Menschen |
|---|---|
| Erkennen, Regelprüfung, Text und Bild vorbereiten, nach der Karenz veröffentlichen, WhatsApp-Entwurf bereitstellen | alles, was eine Regel verletzt oder unklar ist; Änderungen am Regelwerk; das Posten im WhatsApp-Kanal; jede Antwort auf Kommentare und Nachrichten |

**Bei Fehlern wird nicht blind wiederholt.** Bricht die Verbindung beim Veröffentlichen ab, gleicht das System mit
den letzten Beiträgen des Kontos ab; bleibt es unklar, entscheidet ein Mensch. Läuft der Zugang zu Meta ab oder sperrt
Meta das Konto, pausiert der Kanal und das Cockpit zeigt den Grund. Der Stopp-Schalter je Kanal wirkt sofort, auch
während der Karenz.

## Was nicht dazugehört

Storys, Reels, Karussells und Video; Kommentare und Nachrichten beantworten; Auswertung der Reichweite; bezahlte
Reichweite; weitere Netzwerke (TikTok, X, YouTube); automatisches Posten in WhatsApp über inoffizielle Dienste (§3
Abs. 3). Ein Link im Instagram-Text ist bei Instagram nicht anklickbar; der Text verweist auf tamil.de.

## So wird abgenommen (Tests T1 bis T3)

- Einen Artikel freigeben: Nach der Karenz steht er auf Instagram und Facebook; die Historie zeigt beide Links und
  die Kennung von Meta.
- Einen Termin aus einer Einsendung veröffentlichen: beide Beiträge erscheinen; ein Termin in der Vergangenheit wird
  übersprungen.
- Einen heiklen Beitrag veröffentlichen: nichts geht automatisch hinaus, er steht unter „von Hand entscheiden“.
- Kanal „Instagram“ stoppen und einen Beitrag freigeben: nichts geht hinaus, das Protokoll nennt den Grund.
- WhatsApp-Entwurf kopieren, im Kanal posten, „als gepostet“ markieren: steht mit Person und Zeit im Protokoll.
- Der übernommene Altbestand hat nichts ausgelöst.

Solange die Konten fehlen, laufen diese Tests im Trockenmodus und mit einer nachgestellten Schnittstelle; der Vertrag
verlangt je Kanal einen tatsächlichen oder von der Schnittstelle bestätigten Test.

## Zuarbeit von KBS

Instagram-Professional-Konto, damit verknüpfte Facebook-Seite und Business-Portfolio bei Meta; die App bei Meta liegt
bei KBS; falls Meta es verlangt, Unternehmensverifizierung und App-Prüfung (Wochen). Einmalige Freigabe des
Regelwerks. Hashtags je Rubrik. Der Link zum WhatsApp-Kanal.

## Offen für Luis (mit Vorschlag)

1. Regelwerk wie in der Tabelle? Besonders: sechs am Tag, Ruhezeit 22 bis 7 Uhr, 48 Stunden.
2. Bild: das Foto im Hochformat mit kleiner Logo-Leiste, oder eine gestaltete Karte mit Schlagzeile im Bild?
   Vorschlag: zum Start das Foto mit Logo-Leiste; die Karte folgt mit dem neuen Design.
3. Zehn Minuten Karenz vor dem Veröffentlichen?
4. Wer darf das Regelwerk ändern? Vorschlag: nur `admin`, jede Änderung mit neuer Fassung und im Protokoll.
5. Auf Facebook als Foto mit Text und Link (wie Instagram) oder als Link mit Vorschau? Vorschlag: Foto mit Text.
