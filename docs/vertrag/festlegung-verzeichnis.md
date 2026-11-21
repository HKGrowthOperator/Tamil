# Festlegung F2: Verzeichnis (Firmen, Dienstleister, Vereine, Tempel)

Vertrag: B1 (durchsuchbares öffentliches Verzeichnis mit Kategorien, Profilen, Kontaktdaten, Standortfiltern und
Premium-Markierung; Agent für Dubletten, fehlende Felder, Klassifikation und Vorschläge zur Freigabe), §8. Stand:
**Ja von Luis am 13.11.2026 mit den Vorschlägen dieser Festlegung** (`docs/abnahme/2026-11-13-auftrag-luis.md`); gebaut wird auf dem Testsystem, im Echtbetrieb bleibt die Funktion per Schalter aus, bis Auftragsverarbeitung und Rechtstexte vorliegen.

## Was gebaut wird

**Öffentlich auf der Website: `/verzeichnis/`**

- **Vier Arten:** Business, Dienstleister, Verein, Tempel. Jede Art hat Kategorien; die Liste liefert KBS (Vorschlag
  unten) und pflegt sie in WordPress.
- **Suche und Filter:** Freitext, Art, Kategorie, Land (DE/AT/CH), Bundesland oder Kanton, Stadt. Die Filter stehen
  in der Adresse, ein gefiltertes Ergebnis lässt sich also teilen.
- **Profil je Eintrag:** Name, Art, Kategorie, kurze Beschreibung (bis 600 Zeichen), Adresse, PLZ, Stadt, Land,
  Telefon, E-Mail, Website, Öffnungszeiten, ein Bild. Für Suchmaschinen als Geschäft, Organisation oder Gebetsstätte
  ausgezeichnet.
- **Premium:** eine Markierung, die nur ein Administrator setzt. Premium-Einträge stehen in den Listen oben und
  tragen sichtbar das Wort „Premium“.
- An jedem Profil: „Änderung melden“. Auf der Übersicht: „Eintrag vorschlagen“.

**Weg eines Eintrags**

1. Jemand schlägt einen Eintrag vor oder meldet eine Änderung (Formular; Name und E-Mail des Einsenders, Angabe „ich
   bin Inhaber oder berechtigt“ oder „ich weise nur darauf hin“, Einwilligung).
2. Der Agent prüft: Pflichtfelder (Name, Art, PLZ, Stadt, Land und mindestens ein Kontaktweg), Form von PLZ,
   Telefon und Adresse der Website, mögliche Dubletten (ähnlicher Name und dazu gleiche PLZ, Telefonnummer oder
   Website) und schlägt eine Kategorie vor.
3. Die Redaktion sieht bei einem neuen Eintrag den Vorschlag mit den Hinweisen, bei einer Änderung **alt neben neu,
   Feld für Feld annehmbar**. Sie ändert, gibt frei oder lehnt ab.
4. Erst die Freigabe schreibt in das öffentliche Verzeichnis.

## Was automatisch läuft und was nicht

| Automatisch | Nur durch einen Menschen |
|---|---|
| Prüfung der Felder, Suche nach Dubletten, Vorschlag der Kategorie, Zusammenfassung des Unterschieds | jede Veröffentlichung, jede Änderung, Premium, Löschen |

**Nichts Erfundenes:** Der Agent darf nur Werte verwenden, die wörtlich in der Einsendung stehen. Er ergänzt nichts
aus dem Netz, rät keine Öffnungszeiten und füllt keine Lücken. Fehlt etwas, steht dort „fehlt“. Ohne Modell (solange
der Schlüssel fehlt) läuft die Prüfung nach festen Regeln; nur der Kategorie-Vorschlag entfällt dann.

## Daten

Öffentlich wird nur, was im Formular als öffentlich gekennzeichnet ist. Name und E-Mail des Einsenders bleiben
intern und werden mit der Einsendung nach 90 Tagen gelöscht. Wer einen Eintrag entfernen lassen will, nutzt
„Änderung melden“ mit der Auswahl „Eintrag entfernen“; die Redaktion entscheidet.

## Was nicht dazugehört

Umkreissuche und Karte; Bewertungen und Kommentare; ein Konto, mit dem Inhaber ihren Eintrag selbst pflegen;
Online-Verkauf von Premium (die Markierung setzt die Verwaltung von Hand); das Zusammensuchen von Einträgen durch uns
oder durch den Agenten.

## So wird abgenommen (Test T4)

- Eintrag vorschlagen → erscheint im Cockpit mit Hinweisen → freigeben → öffentlich über Art, Stadt und Suche zu
  finden.
- Telefonnummer per „Änderung melden“ ändern → Cockpit zeigt alt und neu → freigeben → Profil zeigt die neue Nummer.
  Ablehnen ändert nichts.
- Denselben Verein noch einmal vorschlagen → Hinweis „mögliche Dublette“ mit Verweis auf den vorhandenen Eintrag.
- Premium lässt sich weder über das Formular noch über die Schnittstelle des Radars setzen.
- Ein Vorschlag ohne Stadt wird nicht automatisch ergänzt, sondern als unvollständig markiert.

## Zuarbeit von KBS

Die Kategorien je Art; ein Startbestand als Tabelle (Name, Art, Kategorie, Adresse, PLZ, Stadt, Land, Kontakt) oder
die Entscheidung, leer zu starten. Ein Startbestand läuft durch dieselbe Prüfung.

## Vorschlag für die Kategorien (KBS bestätigt oder ersetzt)

| Art | Kategorien |
|---|---|
| Business | Restaurant und Imbiss · Lebensmittel · Textil und Schmuck · Reise · Sonstiges |
| Dienstleister | Recht und Steuern · Gesundheit · Übersetzung · Foto und Video · Catering und Feiern · Handwerk · Fahrschule · Sonstiges |
| Verein | Kultur · Sport · Tamilschule · Hilfe und Soziales |
| Tempel | Hindu-Tempel · Kirche · weitere Gebetsstätte |

## Offen für Luis (mit Vorschlag)

1. Vier Arten wie im Vertrag; sollen unter „Tempel“ auch Kirchen und andere Gebetsstätten stehen? Vorschlag: ja,
   als eigene Kategorien.
2. Darf jeder einen Eintrag vorschlagen oder nur Inhaber? Vorschlag: jeder; die Redaktion sieht, wer es war.
3. Wirkung von Premium: oben in der Liste und Kennzeichen „Premium“. Reicht das?
4. Startet das Verzeichnis leer oder mit einer Liste von KBS?
