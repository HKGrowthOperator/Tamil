# Festlegung F1: Einreichungen (Formulare und Eingang im Cockpit)

Vertrag: A1 (Event-Einreichung, Kontakt), B1 (automatische Erfassung und Vorbereitung eingehender Beiträge,
Event-Einreichungen, Kooperations- und Werbeanfragen), §8. Stand: **Ja von Luis am 13.11.2026 mit den Vorschlägen dieser Festlegung** (`docs/abnahme/2026-11-13-auftrag-luis.md`); gebaut wird auf dem Testsystem, im Echtbetrieb bleibt die Funktion per Schalter aus, bis Auftragsverarbeitung und Rechtstexte vorliegen.

## Was gebaut wird

**Auf der Website: fünf eigene Formulare** (kein fremdes Plugin, keine Daten an Dritte)

| Formular | Felder (* Pflicht) |
|---|---|
| Event einreichen | Titel*, Datum und Uhrzeit*, Ende, Ort mit Adresse*, Stadt*, Land* (DE/AT/CH), Veranstalter*, Beschreibung*, Eintritt, Ticket-Link, Bild |
| Beitrag oder Thema vorschlagen | Thema*, Hinweis oder Text*, Link, Bild |
| Kooperation | Organisation, Anliegen* |
| Werbeanfrage | Firma, gewünschter Platz und Zeitraum, Nachricht* |
| Kontakt | Nachricht* |

Jedes Formular fragt zusätzlich nach Name*, E-Mail*, Telefon (freiwillig) und der Einwilligung* in die Verarbeitung
(Text und Fassung von KBS, mit Link zur Datenschutzerklärung). Wer ein Bild mitschickt, bestätigt, dass es verwendet
werden darf.

Nach dem Absenden steht auf der Website „Danke, die Redaktion meldet sich“ mit einer Vorgangsnummer. **Es geht keine
E-Mail hinaus** (§8 Abs. 2).

**Im Cockpit: der Eingang**

1. Der Radar holt neue Einsendungen alle paar Minuten bei der Website ab.
2. Der Agent bereitet vor: Pflichtfelder vollständig? Datum plausibel und in der Zukunft? Ort in Deutschland,
   Österreich oder der Schweiz? Gibt es den Termin oder die Einsendung schon? Dazu eine kurze interne
   Zusammenfassung. Bei Events und Beiträgen entsteht ein Entwurf, **ausschließlich aus den eingesandten Angaben**.
3. Die Redaktion sieht die Einsendung, die Hinweise des Agenten und den Entwurf, kann alles ändern und entscheidet:
   *übernehmen*, *erledigt*, *ablehnen* oder *Spam*.
4. „Übernehmen“ legt einen Entwurf mit dem Vermerk „Angaben des Einsenders, ungeprüft“ an. Ab da gilt der normale
   Weg: prüfen, freigeben, veröffentlichen. Ein Termin erscheint danach im Kalender, mit Eintritt, Ende und
   Veranstalter.
5. Kooperations-, Werbe- und Kontaktanfragen bekommen Status und Notiz. Geantwortet wird von Hand aus dem eigenen
   Mailprogramm; das Cockpit bietet dafür nur einen Link, der das Mailprogramm öffnet.

## Was automatisch läuft und was nicht

| Automatisch | Nur durch einen Menschen |
|---|---|
| Abholen, Abwehr von Spam, Prüfung der Felder, Suche nach Dubletten, Zusammenfassung, Entwurf | Übernehmen, Freigeben, Veröffentlichen, Ablehnen, jede Antwort an den Einsender |

Der Agent schreibt nie einen Text an den Einsender und ergänzt nichts, was nicht in der Einsendung steht. Unklares
(Datum in der Vergangenheit, Ort außerhalb, mögliche Dublette) wird markiert und nicht selbst entschieden. Ist der
Schalter „Eingang“ an, bleiben Einsendungen auf der Website liegen und gehen nicht verloren.

## Schutz vor Missbrauch

Ohne fremden Dienst: ein verstecktes Feld, das nur Programme ausfüllen; eine Zeitprüfung (schneller als drei
Sekunden gilt als Programm); höchstens fünf Einsendungen je Stunde von derselben Adresse (die Adresse wird nur als
nicht rückrechenbarer Wert für 24 Stunden gespeichert); höchstens drei Links im Text. Bilder: nur JPEG und PNG bis
5 MB, neu gespeichert ohne versteckte Angaben, bis zur Übernahme nicht öffentlich.

## Daten

Gespeichert werden die eingegebenen Felder, der Zeitpunkt und die Fassung der Einwilligung. Löschung 90 Tage nach
Abschluss (übernommen, erledigt, abgelehnt); Spam nach 7 Tagen. Namen und Kontaktdaten stehen nicht im Protokoll.

## Was nicht dazugehört

Automatische Bestätigungen oder Antworten per E-Mail; ein Konto oder eine Anmeldung für Einsender; ein
Statusabruf für Einsender; Einreichungen über WhatsApp oder Social Media. Die Online-Buchung von Werbung ist
Baustein 4; bis dahin führt „Werben“ zur Werbeanfrage.

## So wird abgenommen

- Termin einreichen → erscheint im Eingang mit Hinweisen → bearbeiten → übernehmen → freigeben → steht im Kalender
  mit Datum, Ort, Eintritt und Veranstalter (Test T7, „redaktionelle Verwaltung“).
- Eine Einsendung ohne Einwilligung oder mit ausgefülltem verstecktem Feld wird nicht angenommen.
- Derselbe Termin zweimal eingereicht: Die zweite Einsendung trägt den Hinweis „mögliche Dublette“.
- Rolle `leser` kann nichts übernehmen oder ablehnen.
- Im gesamten Ablauf wird keine E-Mail verschickt (automatischer Test).

## Zuarbeit von KBS

Einwilligungstext für die Formulare; die E-Mail-Adresse der Redaktion, an die geantwortet wird; Auftragsverarbeitung
vor dem Echtbetrieb.

## Offen für Luis (mit Vorschlag)

1. Fünf Formulare wie oben, oder zusammenlegen? Vorschlag: wie oben; „Kontakt“ bleibt das allgemeine.
2. Soll ein eingereichtes Bild als Beitragsbild verwendet werden dürfen? Vorschlag: ja, wenn der Einsender das Recht
   bestätigt; sonst die Bildkarte „Grafik: Tamil.de“.
3. Telefon freiwillig, E-Mail Pflicht: in Ordnung?
4. Dürfen Vereine wiederkehrende Termine einreichen? Vorschlag: jeder Termin einzeln, Serien später bei Bedarf.
