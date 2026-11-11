# Prioritäten, Entscheidungen und Technikteam

## Reihenfolge

| Priorität | Konkretes Ergebnis | Federführung |
|---|---|---|
| P0 | Richtigen Ausbau-Branch und Deployment-SHA belegen; aktuelle Übergabe lesen | Tech Lead |
| P0 | F0–F4 und G2/G3 anhand echter Protokolle unterscheiden | Produktverantwortlicher Luis |
| P1 | Einreichung von Website bis Freigabe/Kalender vollständig | WordPress + Radar |
| P1 | Verzeichnis mit Suche, Profil, Vorschlagsprüfung und Änderung | WordPress + Radar |
| P1 | F3 sicher präzisieren und Werbebuchung/Stripe bis Laufzeitende | WordPress/Payment-Engineer |
| P1 | Regelkonforme IG-/FB-Ausgabe und WhatsApp-Entwurf | Radar/Integration |
| P1 | klar2 nach Designabnahme auf die vollständigen Seitentypen übertragen | Product Designer + Frontend |
| P1 | T1–T7, Übergabe, Domainumschaltung und Betreuungsstart belegen | QA + Tech Lead + KBS |

Design kann unabhängig als Probe weitergehen, während freigegebene Backendbausteine entstehen.
Gemeinsame Änderungen an Theme/API/Schema erst koordinieren. Kein weiterer Orchestrator als Voraussetzung.

## Noch konkret zu klären

Diese Liste ist ein Stichtagsbefund und keine neue Genehmigungsliste. Für den jeweils aktuellen Stand
`docs/abnahme/`, Festlegungen und `docs/vertrag/zuarbeit-kbs.md` lesen.

- F0: echte Rollenbelegung, Fristen und Cookie-/Rechtstexte.
- F1/F2: Eingangs-/Änderungsregeln und Sichtbarkeit persönlicher Kontaktdaten.
- F3: Preise, Laufzeiten, freigegebenes Stripe-Konto, Erstattungsregeln und sichere Wiederherstellung des
  Kundenstatus. Buchungsnummer + E-Mail allein sind keine ausreichende Zugriffsprüfung.
- F4: KBS-Regelwerk, echte berechtigte Konten, Appstatus und Social-Bildrechte.
- Design: tatsächliches Kundenurteil G2 und vollständige Probeseite G3; alte Ablehnungen erhalten.
- Betrieb: Mapping für produkt.tamil.de ungeklärt; Websitevorschau wurde an der dokumentierten Coolify-Adresse
  beobachtet. Deployment-SHA über berechtigten Betriebszugang belegen.
- Referenzname Amazon Agent Bridge: exakte Quelle fehlt; hat keine blockierende Bedeutung für den
  vorhandenen technischen Stack.

## Benötigte menschliche Fähigkeiten

Das sind Verantwortungsbereiche, keine Behauptung über bereits besetzte Stellen und keine Empfehlung,
sofort sechs Personen einzustellen. Zu Beginn können passende Rollen kombiniert werden.

| Verantwortung | Gesuchte Fähigkeit | Konkrete Arbeitsprobe |
|---|---|---|
| Tech Lead / Senior Fullstack | WordPress/PHP, Python, Datenmodelle, Integration, Scope | Vorhandenen Baustein vollständig integrieren und begründet prüfen |
| WordPress/Payment | REST-Capabilities, Migrationen, Belegungskonkurrenz im eingesetzten DB-System, Stripe | Letzte freie Werbekapazität gegen zwei gleichzeitige Buchungen absichern |
| Python/Agent-Integration | Jobs, Claims/Leases, Provideradapter, Kosten, Quellen | Worker-Neustart und Timeout ohne Doppelaktion demonstrieren |
| Product Designer / Frontend | Editorial-Web, responsive Typografie, Formulare, A11y | Artikel plus Werbebuchung mobil und Desktop aus dem echten Brief |
| QA / Testautomation | WP-Integration, Browser, deterministische Zeit/Konkurrenz | Fehlerfall reproduzieren, Fix prüfen, Anbietergrenze sauber dokumentieren |
| Betrieb, anteilig | Coolify, Container, Backups/Restore, Secrets, Monitoring | Wiederherstellung im Testsystem und nachvollziehbare Versionszuordnung |

Agenten übernehmen Recherche, Code, gezielte Tests und Dokumentation. Menschen verantworten
Produkt-/Geschäftsentscheidungen, Rechte, Betreiberkonten und fachliche Abnahme. Ein breites Agentteam
ersetzt keine klare technische Integrationsverantwortung.

## Architekturentscheidungen als Empfehlung

Bestehenden Stack halten. Kein Supabase-, AWS-, Next.js- oder Multi-Orchestrator-Wechsel ohne belegten
Produktgrund. Vorhandenes Budget-, Job- und Cockpitsystem ausbauen. Provider und Modelle über begrenzte
Adapter austauschbar halten, keine verstreuten Direktaufrufe.

Für HKOS kann später ein Status-/Linkverweis sinnvoll sein; Kundendaten und Freigaben bleiben im
zuständigen Tamil-Projekt. Ein globales Cockpit ist keine automatische Übertragung von Kundenrechten.
