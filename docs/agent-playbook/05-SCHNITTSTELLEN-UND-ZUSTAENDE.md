# Technische Verträge für die offenen Produktmodule

Empfohlene Ergänzung zum vorhandenen Bauplan. Keine Behauptung, dass die folgenden Mechanismen schon
implementiert sind. Vor dem Bau mit den tatsächlichen Festlegungen und vorhandenen Schnittstellen abgleichen.
Kein neuer Service oder Message-Broker allein wegen dieses Dokuments erforderlich.

## Gemeinsame Regeln

- Jede Nachricht trägt stabile Objekt-ID, Typ, Quellrevision, Regelversion, Erzeugungszeit mit Zeitzone,
  Korrelations-ID und Idempotenzschlüssel. Geheimnisse nicht in Logs oder URLs ablegen.
- Bestehende Tabellen, IDs und Statusnamen zuerst prüfen; hier gezeigte Begriffe sind semantische Verträge.
- WordPress bleibt Source of Truth für Buchung, Zahlung, Einreichung und öffentliche Profile.
- Radar fragt Änderungen seitenweise mit belastbarem Cursor ab. Teilantwort bedeutet nicht Löschung.
  Erneute Zustellung darf keinen zweiten Eingang oder Social-Post erzeugen.
- Autorisierung und erwartete Revision unmittelbar mit der Mutation prüfen. Ein vorheriger GET reicht nicht.
- Zeitzone fachlich Europe/Berlin; intern eindeutige UTC-Zeitpunkte, Datumsspannen und DST-Grenzen testen.
- Stopp verhindert neue externe Aktionen. Bereits laufende, unklar beendete Aktionen erst abgleichen.

## Einreichungen und Verzeichnis

Formular speichert validierte Einreichung und liefert Webbestätigung mit unerratbarer Referenz.
Honeypot/Ratelimit, Längen-/Typgrenzen, Uploadprüfung, erlaubte Dateitypen und sichere Auslieferung.
Öffentliche Einreichung darf keine Admin-/Premium-/Freigabefelder setzen.

Vorgeschlagene Kette: eingegangen → in Prüfung → Nacharbeit/abgelehnt oder freigegeben → veröffentlicht.
KI prüft fehlende Felder/Dubletten und schlägt Klassifikation vor; Freigabe bleibt nachvollziehbar.
Verzeichnisänderung als Revision behandeln, nicht ungeprüft das öffentliche Profil überschreiben.
Premium-Markierung ist eine Adminfunktion, kein zusätzlich beauftragtes Premium-Abo.

## Buchung und Belegung

Preis, Währung, Platz, Laufzeit und Regelversion serverseitig festhalten. Keine Preise aus Browserfeldern übernehmen.
Für gleiche Werbefläche und denselben Zeitraum müssen Reservierung und Kapazitätsprüfung atomar sein.
Bei mehreren Slots Kapazität in derselben Transaktion schützen; bei letzter freier Kapazität genau ein Gewinner.

Semantische Zustände: reserviert → Zahlung offen → bezahlt/in Prüfung → geplant → aktiv → beendet.
Weitere Zustände: abgelaufen, abgelehnt, pausiert, Erstattung offen/erstattet/fehlgeschlagen.
Die Kampagne ist aktiv genau dann, wenn bezahlt, freigegeben, nicht pausiert und innerhalb des Zeitfensters.

Die F3-Festlegung schlägt 35 Minuten Reservierung vor; das ist bis zur Bestätigung ein Vorschlag.
Verspätete Zahlung nach Reservierungsablauf muss mit eventuell neu vergebener Kapazität abgeglichen werden;
keine doppelte Belegung und kein blindes Aktivieren. Fehlfall im Admin sichtbar lösen.

## Stripe

Offizielle Primärquelle: https://docs.stripe.com/webhooks, geprüft 11.11.2026.
Signatur gegen unveränderten Request-Body prüfen; eingehende Event-IDs idempotent verarbeiten und
unterschiedliche Zustellreihenfolgen berücksichtigen. Ein Browser-Redirect beweist keine Zahlung.
Betrag, Währung, Konto, Test/Live-Modus und Buchungszuordnung abgleichen.

Nach Timeout mit demselben Idempotenzbezug beim Anbieter abgleichen, bevor Checkout/Erstattung neu
erzeugt wird. Nicht `erstattet` anzeigen, solange nur ein Auftrag erstellt oder dessen Ausgang unbekannt ist.
Erstattung und Freigabe mit rollen- und versionsgeschützter Mutation. Geldentscheidungen deterministisch;
kein LLM entscheidet Beträge oder erklärt eine Zahlung allein für erfolgreich.

F3 enthält derzeit Wiederfinden per Buchungsnummer plus E-Mail. Vor Implementierung präzisieren:
Eine E-Mail-Adresse ist kein Geheimnis. Kein Zugriff auf Rechnungs-/Kontaktdaten nur mit diesen zwei
leicht beschaffbaren Angaben. Beispielsweise starke Wiederherstellungsreferenz oder manuell geprüfte
Wiederherstellung ohne automatisierte Mail; Wahl in F3 festhalten. Token nur gehasht speichern,
nicht loggen, von Indexierung und Referrer-Weitergabe schützen.

## Social

Kanonischer Schlüssel aus WordPress-ID, veröffentlichter Inhaltsrevision, Kanal und Kampagnenzweck.
Artikel-/Eventveröffentlichung erkennen; Altimport und Nachträge nicht versehentlich als neue Social-Welle behandeln.
Vor Senden Kanalstopp, Rollen/Regelversion, Rechte und aktuelle Freigabe erneut prüfen.

IG und FB haben getrennte Zustände: vorbereitet → eingeplant → sendet → bestätigt,
oder fehlgeschlagen/unklar/gestoppt/manuell prüfen.
Wenn Instagram bestätigt und Facebook scheitert, nur Facebook nach Abgleich erneut versuchen.
Ein HTTP-Timeout darf weder automatisches Doppelposting noch fälschlichen Erfolg auslösen.

API-Version, Kontoberechtigung, Appstatus und Formatgrenzen gegen aktuelle offizielle Meta-Dokumentation prüfen.
Diese Analyse bestätigt keine Meta-Anbindung; der offizielle Content-Publishing-Abruf war hier durch 429 begrenzt.
WhatsApp-Channel-Entwurf bleibt ein anderer Ausgabepfad als WhatsApp-Business-Nachrichten.

F4 erwähnt KI-Bild-Kennzeichnung, während die jüngere Bildentscheidung keine KI-Bilder zulässt.
Die jüngere Entscheidung anwenden und die Festlegung vor Nutzung bereinigen; keine Bildgenerierung aus
einer historischen Tabellenzeile ableiten.

## Laufzeitagents

Vorhandene Jobs, Claims/Leases, Budgetreservierung und Agent-API erhalten.
Worker A darf nach Lease-Verlust keine Ausgabe von B überschreiben. Kostenfreigabe und Jobclaim zusammen
wirksam absichern; Budget nicht nur im UI prüfen. Modellantworten als untrusted Inhalt validieren.
Quelltexte dürfen weder Tools neu autorisieren noch Systemregeln oder Publishingfreigaben überschreiben.

Provideradapter liefern strukturierte Ergebnisse und belastbare Fehler, keine freie Shell-Ausführung.
Externes Agentmodell nur nach verifiziertem API-Vertrag anbinden; MCP ist ein Zugangsweg, kein
Nachweis von Mandantentrennung oder Schreibberechtigung.
