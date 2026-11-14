# Festlegung F3: Werbebuchung mit Online-Zahlung

Vertrag: A2 (Angebots- und Preisdarstellung, Self-Service-Buchung, Verfügbarkeit, Freigabeprüfung, Online-Zahlung,
automatischer Start und Ablauf, Kundenübersicht, Admin mit Statistik), A3, §8. Stand: **Ja von Luis am 13.11.2026 mit den Vorschlägen dieser Festlegung** (`docs/abnahme/2026-11-13-auftrag-luis.md`); gebaut wird auf dem Testsystem, im Echtbetrieb bleibt die Funktion per Schalter aus, bis Auftragsverarbeitung und Rechtstexte vorliegen. Preise und Regeln liefert KBS; bis dahin Platzhalterwerte, deutlich gekennzeichnet. Zahlungsanbieter: Stripe (Luis, 11.11.), gebaut wird
zuerst im Testmodus.

## Was gebaut wird

**Die sechs vorhandenen Werbeplätze** werden buchbar:

| Platz | Wo | Format Desktop / Handy |
|---|---|---|
| Leaderboard | unter der Navigation, alle Seiten | 728 × 90 / 320 × 50 |
| Half Page | Seitenspalte | 300 × 600 |
| Im Artikel | nach dem zweiten Absatz | 728 × 90 / 300 × 250 |
| Billboard | Startseite, zwischen den Rubriken | 970 × 250 / 300 × 250 |
| Fuß | über dem Fuß der Seite | 728 × 90 / 320 × 100 |
| Mobil | am Handy fest am unteren Rand | 320 × 50 |

**Öffentlich: die Seite „Werben“** mit Plätzen, Maßen, Position, Preisen je Laufzeit und dem nächsten freien Termin.

**Buchung in fünf Schritten**
1. Platz und Laufzeit wählen.
2. Startdatum wählen; belegte Tage sind gesperrt.
3. Kundendaten: Firma, Ansprechperson, Rechnungsadresse, E-Mail, Telefon, USt-ID (freiwillig).
4. Werbemittel hochladen (Bild in den Maßen des Platzes, für Desktop und Handy) und die Zieladresse angeben.
5. Zusammenfassung, Bedingungen annehmen, bei Stripe bezahlen.

**Danach**
- Die gewählten Tage sind während der Zahlung 35 Minuten reserviert; ohne Zahlung werden sie wieder frei.
- Die Zahlung gilt erst als bestätigt, wenn Stripe sie meldet (signierte Meldung, zusätzlich Abgleich bei der Rückkehr
  auf die Website).
- KBS prüft das Werbemittel in der Verwaltung und gibt frei oder lehnt mit Grund ab.
- **Aktiv ist eine Buchung nur, wenn sie bezahlt und geprüft und nicht pausiert ist und heute im gebuchten Zeitraum
  liegt.** Start, Wechsel und Ende folgen allein aus dem Datum. Nach dem Ende steht wieder die Eigenanzeige.
- Bei Ablehnung wird der volle Betrag über Stripe erstattet und die Tage werden frei.

**Kundenübersicht** auf der Website, ohne Konto und ohne E-Mail von uns: Nach der Zahlung zeigt die Website einen
geheimen Link zur Buchung (Stand der Prüfung, Zeitraum, Zahlung, Beleg von Stripe, Einblendungen und Klicks). Wer den
Link verliert, findet die Buchung mit Buchungsnummer und E-Mail-Adresse wieder.

**Verwaltung für KBS** (in WordPress, Menü „Werbung“)
- Angebote: je Platz aktiv oder nicht, Laufzeiten, Preis je Laufzeit, Anzeigen gleichzeitig, Vorlauf.
- Buchungsliste mit Stand (reserviert, bezahlt, in Prüfung, geplant, läuft, pausiert, beendet, abgelehnt, erstattet).
- Prüfen, Pausieren und Fortsetzen, Beenden, Erstatten.
- Statistik je Buchung und Tag: Einblendungen (mindestens die halbe Fläche eine Sekunde sichtbar) und Klicks; Export.

## Was automatisch läuft und was nicht

| Automatisch | Nur durch einen Menschen |
|---|---|
| Preis berechnen, Verfügbarkeit prüfen und reservieren, technische Prüfung des Werbemittels (Format, Maße, Größe, Zieladresse), Zahlung abgleichen, Start und Ende nach Datum, Zählung, Erstattung nach einer Ablehnung | Freigabe oder Ablehnung des Werbemittels, Pausieren, vorzeitiges Beenden, Preise und Angebote ändern |

Fehler bei Zahlung oder Erstattung stehen als Warnung in der Buchungsliste und gehen an einen Menschen. Jede Buchung
führt ein eigenes Protokoll (wann reserviert, bezahlt, geprüft, gestartet, beendet, von wem).

## Daten

Kartendaten sieht und speichert die Website nie; sie bleiben bei Stripe. Gespeichert werden die Kundendaten der
Buchung, das Werbemittel, Betrag und Stand der Zahlung. Die Zählung arbeitet ohne Cookies und ohne Personendaten.
Buchungsdaten bleiben so lange, wie es das Steuerrecht verlangt (KBS nennt die Frist).

## Was nicht dazugehört

Gestaltung von Werbemitteln; Werbekunden gewinnen; fremde Werbenetzwerke; bewegte Banner, Video und fremde Skripte
(nur JPEG und PNG); Zielgruppen-Auswahl; Rabattcodes; Abos und automatische Verlängerung; Rechnungen mit ausgewiesener
Umsatzsteuer (der Beleg kommt von Stripe, Rechnungen stellt KBS); Kundenkonten mit Anmeldung; eine rechtliche Prüfung
der Verkaufsbedingungen (A3). Eine Buchungsbestätigung per E-Mail von unserem System gibt es nicht (§8 Abs. 2); ob
Stripe einen Zahlungsbeleg mailt, stellt KBS im eigenen Stripe-Konto ein.

## So wird abgenommen (Tests T5 und T6)

- Buchung mit Testkarte: Zahlung erfolgreich, die Kundenübersicht zeigt „bezahlt, in Prüfung“.
- Buchung mit abgelehnter Testkarte: keine Buchung, die Tage sind wieder frei.
- Zwei Kunden wählen gleichzeitig denselben Platz und Tag: Genau eine Buchung kommt zustande.
- Bezahlt, aber nicht geprüft: Das Banner erscheint nicht. Nach der Freigabe erscheint es am Starttag.
- Buchung mit einem Tag Laufzeit: am Folgetag steht wieder die Eigenanzeige; die Statistik zeigt Einblendungen.
- Ablehnung: Der Betrag wird erstattet, die Tage sind frei, die Kundenübersicht nennt den Grund.
- Eine gefälschte oder doppelt gesendete Zahlungsmeldung ändert nichts.

## Zuarbeit von KBS

Preise je Platz und Laufzeit; Laufzeiten; Anzeigen gleichzeitig je Platz; Werberichtlinien (was unzulässig ist);
Verkaufsbedingungen; Stripe-Konto; Angabe, ob Preise mit oder ohne Umsatzsteuer gezeigt werden und wie Rechnungen
entstehen; Aufbewahrungsfrist.

## Offen für Luis (mit Vorschlag)

1. Laufzeiten: 7, 14 und 30 Tage?
2. Je Platz eine Anzeige zur selben Zeit (exklusiv) oder mehrere im Wechsel? Vorschlag: eine; Wechsel später.
3. Jedes Werbemittel vor dem Start von Hand prüfen, Vorlauf zwei Werktage? Vorschlag: ja. Alternative: Anzeigen
   bekannter Kunden starten ohne Prüfung.
4. Bei Ablehnung volle Erstattung; Stornierung durch den Kunden nur über KBS? Vorschlag: ja.
5. Preise mit Umsatzsteuer anzeigen, Rechnung stellt KBS von Hand? Vorschlag: ja, bis KBS es anders will.
6. Soll der feste Platz am unteren Rand des Handys verkauft werden? Er ist auffällig. Vorschlag: ja, als teuerster Platz.
