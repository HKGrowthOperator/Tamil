# Produkt und Scope: Tamil.de

## Produktdefinition

Tamil.de ist ein deutschsprachiges Nachrichten-, Magazin-, Event- und Community-Portal für die tamilische
Diaspora in Deutschland, Österreich und der Schweiz. Es verbindet verlässliche redaktionelle Inhalte,
nützliche Termine und auffindbare Community-Angebote mit dem Verkauf eigener digitaler Werbeflächen.

Ziel ist ein vollständig nutzbarer Ablauf für Leser, Einreicher, Werbekunden und KBS-Redaktion.
Eine sichtbare Seite mit Platzhalterfunktion erfüllt diesen Ablauf nicht. Bestehendes WordPress und Radar
werden vervollständigt; ein neues SaaS-Frontend oder eine pauschale Datenbankmigration sind nicht beauftragt.

## Maßstab

Anlage 1 Teile A/B des Gesamtvertrags, Stand 11.11.2026, operativ abgebildet in
`docs/vertrag/leistungen.md`. Die vollständige Vertragsdatei und finanzielle Angaben bleiben außerhalb des
Repositories. Merzlicht und AJ Gamestation haben eigene Umfänge und keine gemeinsamen Buchungs- oder Mailregeln.

| Nutzer | Vollständiger Kernablauf | Sichtbares Erfolgskriterium |
|---|---|---|
| Leser | Aufmacher/Rubrik → Artikel → Quelle/Autor → passende Termine | Lesbar am Handy, richtige Daten, echte Links, kein Zugang zu Interna |
| Event-Einreicher | Formular → Eingangsbestätigung im Web → Prüfung → Veröffentlichung | Event erscheint erst nach Freigabe mit korrektem Ort/Zeit/Veranstalter |
| Community-Anbieter | Eintrag vorschlagen/ändern → Dublettenprüfung → Freigabe | Öffentliches Profil mit Kategorien, Standort und nachvollziehbaren Änderungen |
| Werbekunde | Platz/Laufzeit → Verfügbarkeit → Upload → Zahlung → Prüfung → Kampagne | Aktivierung nur bezahlt, freigegeben und im Zeitfenster; Status im Web |
| Redaktion | Eingang → Prüfung/Bearbeitung → Freigabe → Veröffentlichung → Historie | Quellen/Bildrechte nachvollziehbar, Fehler und Stopp funktionieren |
| KBS-Admin | Rollen/Regeln → Werbung/Verzeichnis verwalten → Lauf prüfen | Berechtigte Änderung, Protokoll, sichere Pause und Wiederaufnahme |

## Inhalte und Oberfläche

Neun Themenbereiche: Nachrichten, Community, Entertainment, Kino, Events, Küche, Sport, Kultur und Kontakt.
Kontakt ist eine Serviceseite; ihre vertragliche Erreichbarkeit nicht als neunte Artikelrubrik missverstehen.
Startseite, Artikel, Rubriken, Suche, Archiv, Events mit Kalender, Kontakt und bearbeitbarer Medienbestand gehören zusammen.

Originaldaten des Altbestands erhalten. Rückblick-Beiträge trennen Ereignisdatum und neue Veröffentlichung;
kein scheinbar aktueller Altartikel. Das bestehende Rückblick- und Quellenverfahren erhalten.
Autor und Quelle nicht gleichsetzen; Bilder brauchen Rechte auch für den jeweils vorgesehenen Social-Kanal.

## Systembesitz

| Bereich | Eigentümer der Daten/Funktion |
|---|---|
| Öffentliches CMS, Medien, Eventdaten, Einreichungen, Verzeichnis, Werbeangebote, Buchungen, Zahlung | WordPress und eigene Plugins |
| Quellen, Storys, Belege/Claims, Entwürfe, Jobs, Usage/Budget, Stopp, Protokoll, Social-Status | Python-Radar/Cockpit |
| Zahlungsausführung/Kartendaten | Freigegebenes KBS-Zahlungsanbieter-Konto |
| Gestaltungskonzept und Nachweise | Bestehende design/-Struktur und Abnahmeprotokolle |
| Auftragsumfang, Änderungen, Abnahmestatus | Bestehendes Vertragsregister und Entscheidungslog |

Website und Cockpit bleiben getrennt abnehmbar. Der Radar holt freigegebene Daten über begrenzte Schnittstellen ab.
Kein Direktzugriff beliebiger Agentmodelle auf WordPress-Datenbank oder Zahlungsgeheimnisse.

## Automatik und Grenzen

- E-Mail bleibt manuell; auch automatisch versandte Formular- oder Buchungsbestätigungen sind nicht vorgesehen.
  WordPress, Plugins und Providerkonten zusammen prüfen; ein statischer Python-Test beweist das nicht allein.
- Instagram und Facebook folgen einem einmalig genehmigten, versionierten Regelwerk; regelkonforme Inhalte
  brauchen keine zweite Einzelfreigabe. Ausnahmen, Sicherheitsfälle und unklarer Ausgang gehen zur Prüfung.
- WhatsApp Channel erhält vorbereiteten Text, Link und Bild. Automatisches Publishing erst bei belegter
  offizieller, für KBS freigeschalteter Fähigkeit. Business-Messaging nicht mit Channel-Publishing verwechseln.
- Keine laufende Werbekundenakquise, Kampagnenproduktion, externen Ad-Netzwerke, unbegrenzte Migration,
  24/7-Bereitschaft oder zusätzlichen Hauptmodule aus diesem Auftrag ableiten.
- Zwei gebündelte Korrekturrunden je Modul; vier Wochen technische Feinjustierung nach Agent-Inbetriebnahme
  plus drei Monate Betreuung nach Go-live. Startdaten konkret protokollieren, nicht aus dem Git-Datum ableiten.

## Produktmessung als Empfehlung

Ohne erfundene Zielwerte: erfolgreiche Artikelaufrufe und Suchwege, Einreichung bis Freigabe, Buchung bis
bezahlte/aktive Kampagne, fehlgeschlagene Checkouts, blockierte Doppelbuchungen, Social-Erfolge je Kanal,
ungeklärte externe Ergebnisse, Zeit bis Fehlerbearbeitung und Modellkosten je nutzbarem Ergebnis.
Messung datensparsam und mit tatsächlich genehmigter Konfiguration; keine neue Trackingplattform voraussetzen.
