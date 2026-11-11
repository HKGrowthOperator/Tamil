# Leistungsverzeichnis tamil.de

Grundlage: Gesamtvertrag (Vertragsstand 11.11.2026), **Anlage 1, Teil A und B**. Dieses Verzeichnis ist der Maßstab
für „fertig“. Hier steht nur der Leistungsumfang für tamil.de. Preise, Zahlungsplan und die Vertragsdatei liegen nicht
im Repo. Merzlicht (Anlage 2) und AJ Gamestation (Anlage 3) sind eigene Projekte.

Für Luis liegen Überblick, Festlegungen und die Liste für KBS als Dokument vor (privat, zum Kommentieren und
Bestätigen): https://claude.ai/artifact/3ebPy94NJHUjafi54sFtYP. Maßgeblich für den Bau ist die Fassung im Repo; ein Ja
oder eine Änderung aus dem Dokument wird hier und in `docs/abnahme/` nachgetragen.

Stand: `fertig` · `teilweise` · `offen` · `wartet` (auf Zuarbeit oder ein Tor). Bei jedem Baustein nachtragen.
Bausteine und Reihenfolge: siehe unten. Einzelheiten je Baustein: `festlegung-<baustein>.md`.

## Teil A – Website, Redaktion, Werbebuchung

| Nr. | Der Vertrag verlangt | Baustein | Stand 11.11.2026 |
|---|---|---|---|
| A1.1 | Individueller responsiver Neuaufbau als Magazin-, Event-, Nachrichten- und Community-Portal für Desktop und Handy | 6 | teilweise: WordPress läuft auf der Vorschau-Adresse; das neue Aussehen `klar2` wartet auf Tor G2 |
| A1.2 | CMS mit Startseite, Artikeln, Rubriken, Suche, Beitragsarchiv | – | fertig (im bisherigen Aussehen) |
| A1.3 | Event-Einreichung | 2 | offen: nur Platzhalter, kein eigenes Formular |
| A1.4 | Veranstaltungskalender | 2 | teilweise: Listen- und Monatsansicht für kommende Termine; Preis, Ende und Veranstalter überträgt der Radar noch nicht |
| A1.5 | Autor- und Quellenangaben | 6 | teilweise: Quelle und Bildnachweis vorhanden; Autor ist ein fester Name |
| A1.6 | Kontakt | 2 | offen: Seite vorhanden, kein eigenes Formular |
| A1.7 | Für KBS bearbeitbare Inhalte, pflegbarer Inhalts- und Medienbestand | – | fertig (WordPress, Einstellungen, Menüs, Mediathek) |
| A1.8 | Neun Themenbereiche (Nachrichten, Community, Entertainment, Kino, Events, Küche, Sport, Kultur, Kontakt), konsistente Navigation | 6 | teilweise: acht Rubriken und die Seite Kontakt; Kontakt fehlt in der Rubrikleiste |
| A1.9 | Technische Übernahme vorhandener Inhalte | 0 | fertig: 532 Beiträge, 7 Seiten, 1445 Medien (`docs/abnahme/2026-11-11-uebernahme.md`) |
| A1.10 | Basis-SEO | 1 | fertig: Titel, Beschreibung, Vorschau für soziale Netze, Artikel- und Termin-Schema, Brotkrumen; das Testsystem ist bis zum Livegang für Suchmaschinen gesperrt |
| A1.11 | Weiterleitungen | 0 | fertig: 25 Einträge, alle geprüft |
| A1.12 | Sitemap | – | fertig (WordPress-Kern, `wp-sitemap.xml`) |
| A1.13 | Performance- und Mobiloptimierung | 1, 6 | teilweise: Bildgrößen, lokale Schriften, Cache-Kopfzeilen; die Messung am Handy (Zielwert 80) steht aus und folgt mit dem neuen Aussehen |
| A1.14 | Einbindung rechtlich freigegebener Pflichtinformationen | 1 | wartet: Impressum und Datenschutz brauchen Texte von KBS (das Impressum der alten Seite ist leer) |
| A1.15 | Cookie-Consent-Technik | 1 | gebaut, ausgeschaltet: eigene Lösung ohne fremden Dienst; eingeschaltet wird nach dem Ja zu F0 und mit dem Text von KBS |
| A2.1 | Öffentliche Angebots- und Preisdarstellung; KBS pflegt Formate, Preise und Laufzeiten im Admin | 4 | offen (sechs Werbeplätze mit Eigenanzeigen vorhanden) |
| A2.2 | Self-Service-Buchung: Werbefläche, Laufzeit, verfügbare Belegung wählen; Kundendaten; Werbemittel hochladen | 4 | offen |
| A2.3 | Automatische Reservierungs- und Verfügbarkeitsprüfung gegen Doppelbuchung; Freigabeprüfung für unzulässige oder auffällige Werbemittel | 4 | offen |
| A2.4 | Online-Zahlung über ein von KBS freigegebenes Konto, gesicherter Statusabgleich, Aktivierung nur nach bestätigter Zahlung | 4 | offen; Echtbetrieb wartet auf das Stripe-Konto von KBS |
| A2.5 | Automatischer Start, Wechsel und Ablauf nach gebuchter Laufzeit; Buchungs- und Zahlungsübersicht für Kunden auf der Website | 4 | offen |
| A2.6 | Admin mit Buchungsliste, Kampagnenstatus, Laufzeiten, Prüfung, Pausieren/Beenden, einfacher Statistik | 4 | offen |

## Teil B – Agent, Verzeichnis, Social, Betreuung

| Nr. | Der Vertrag verlangt | Baustein | Stand 11.11.2026 |
|---|---|---|---|
| B1.1 | Zentrales webbasiertes Agenten-Cockpit mit Rollen, Aufgaben- und Freigabestatus, Bearbeitung, zeitgesteuerten Ausführungen, Fehleransicht, Stopp-Funktion und Protokoll | 1 | fertig bis auf das Ja zu F0: Stopp-Schalter (alles und je Kanal), Rollen `admin`, `redaktion`, `leser`, Protokoll mit Filter und Export, Zeitplan-Ansicht, Fehleransicht; die Zuordnung der Rollen ist ein Vorschlag |
| B1.2 | Automatische Erfassung und Vorbereitung eingehender Beiträge, Event-Einreichungen, Kooperations- und Werbeanfragen; Vorschläge nachvollziehbar und editierbar | 2 | offen |
| B1.3 | Durchsuchbares öffentliches Verzeichnis (Business, Dienstleister, Vereine, Tempel) mit Kategorien, Profilen, Kontaktdaten, Standortfiltern, Premium-Markierung durch die Verwaltung | 3 | offen |
| B1.4 | Agent für Verzeichniseinträge: Dubletten- und Fehlfeldprüfung, Klassifikation, Vorschläge zur Freigabe; nichts Ungeprüftes oder Erfundenes | 3 | offen |
| B2.1 | Veröffentlichte Artikel und Events erzeugen automatisch Text, Bild- und Formatvorgaben, Verweise und einen Social-Beitrag | 5 | offen |
| B2.2 | Veröffentlichung auf einem berechtigten Instagram-Professional-Konto nach einmalig genehmigten Regeln | 5 | offen; wartet auf die Konten von KBS |
| B2.3 | Derselbe Inhalt automatisch auf der verbundenen Facebook-Seite, ohne zweite Einzelfreigabe | 5 | offen |
| B2.4 | Fehler, Dubletten, Pausen, Historie und nicht freigabefähige Beiträge im Cockpit sichtbar | 5 | offen |
| B3.1 | WhatsApp-Channel-Inhalte (Text, Link, Bild) automatisch vorbereitet und bereitgestellt; Veröffentlichung von Hand, solange es keine offizielle Schnittstelle gibt | 5 | offen |
| B3.2 | E-Mail bleibt vollständig manuell | – | erfüllt: im Code wird keine E-Mail verschickt; ein Test sichert das ab (Baustein 1) |
| B4 | Vier Wochen Feinjustierung nach Inbetriebnahme des Agenten, drei Monate Betreuung nach dem Livegang | 7 | beginnt nach dem Livegang |
| B5 | Sieben wesentliche Abnahmetests | 7 | offen: Tabelle unten |

## Bausteine und Reihenfolge (mit Luis am 11.11.2026 festgelegt)

| Nr. | Baustein | Festlegung | Braucht |
|---|---|---|---|
| 0 | Laufendes abschließen: Übernahme prüfen, Radar verbinden | – | – |
| 1 | Grundlage: Upgrade-Routine, SEO, Cache, Cookie-Zustimmung, Rechtsseiten; Stopp-Schalter, Rollen, Protokoll | `festlegung-grundlage.md` (F0) | die Technik beginnt sofort; Ja zu F0 für Rollen, Kategorien, Fristen |
| 2 | Einreichungen: Formulare → Eingang im Cockpit → Freigabe | `festlegung-einreichungen.md` (F1) | Ja zu F1 |
| 3 | Verzeichnis mit Agentenprüfung | `festlegung-verzeichnis.md` (F2) | Ja zu F2 |
| 4 | Werbebuchung mit Stripe | `festlegung-werbung.md` (F3) | Ja zu F3; Preise und Konto von KBS |
| 5 | Instagram, Facebook, WhatsApp-Entwurf | `festlegung-social.md` (F4), `docs/regeln-social.md` | Ja zu F4, einmalige Freigabe des Regelwerks durch KBS; Konten |
| 6 | Design: Probeseite mit allen Seitentypen, Umsetzung | – | Tore G2 und G3 |
| 7 | Abnahme, Übergabe, Livegang, Betreuung | – | Abnahme durch KBS, Tor B3 |

Ablauf je Baustein: Festlegung schreiben → Luis sagt Ja oder ändert → Agents bauen (Test zuerst, eigener Worktree) →
unabhängige Code-Prüfung → auf dem Testsystem zeigen → Abnahmetest ins Protokoll.

## Abnahmetests (B5)

| Nr. | Test laut Vertrag | Baustein | Automatisch | Von Hand auf dem Testsystem |
|---|---|---|---|---|
| T1 | Artikel zu Instagram und Facebook (tatsächlich oder durch die Schnittstelle bestätigt) | 5 | `tests/test_social.py`, Abnahme-Szenarien | Beitrag freigeben; Kennung und Link beider Kanäle stehen in der Historie |
| T2 | Veranstaltung zu Instagram und Facebook | 5 | Szenarien „Termin in der Zukunft“, „Termin vorbei“ | Termin aus einer Einsendung veröffentlichen, beide Beiträge prüfen |
| T3 | WhatsApp-Beitragsentwurf | 5 | `tests/test_social.py` | Text kopieren, im Kanal posten, „gepostet“ markieren |
| T4 | Verzeichnis-Neueintrag und Änderungsfreigabe | 3 | `tests/wp/test_verzeichnis.py`, `tests/test_verzeichnis_agent.py` | Eintrag vorschlagen, freigeben, öffentlich finden; Telefonnummer ändern lassen, Unterschied prüfen, freigeben |
| T5 | Werbebuchung mit erfolgreichem und fehlgeschlagenem Checkout | 4 | `tests/wp/test_buchung.py` | Testkarte mit Erfolg und mit Ablehnung; die Kundenübersicht zeigt den Stand |
| T6 | Geprüfte Kampagnenaktivierung und Laufzeitende | 4 | Aktiv-Funktion mit gestellter Uhr | Buchung mit einem Tag Laufzeit: freigeben, Banner sehen, am Folgetag wieder Eigenanzeige |
| T7 | Agenten-Stopp und Fehlerbehandlung; redaktionelle Verwaltung | 1, 2 | `tests/test_schalter.py`, `tests/test_rechte.py`, `tests/test_eingang.py` | Kanal stoppen, Beitrag freigeben: nichts geht hinaus, das Protokoll nennt den Grund; Fehler auslösen, „Erneut“; Termin einreichen bis zum Kalender |

Protokoll: `docs/abnahme/<datum>-B5.md`, erzeugt mit `/abnahme-vertrag`.

## Regeln aus dem Hauptvertrag, die den Bau bestimmen

- **§3 Abs. 2:** Laufende Plattformgebühren, Lizenzen fremder Software und kostenpflichtige Schnittstellen nur mit
  Freigabe von KBS (Zahlungsgebühren, Modellkosten der Agenten).
- **§3 Abs. 3:** Externe Dienste nur über zulässige, tatsächlich verfügbare offizielle Zugänge.
- **§4:** Übergabe mit funktionierender Website, dokumentierten Kernabläufen, Zugängen und kurzem Abnahmeprotokoll.
- **§8 Abs. 1:** Automatisch läuft nur, was in freigegebenen, dokumentierten Regeln liegt. Sicherheits-, Fehler- und
  Ausnahmefälle gehen in eine manuelle Prüfstufe. Ausführungen und Freigaben werden protokolliert.
- **§8 Abs. 2:** E-Mail bleibt bei tamil.de ein ausschließlich von Hand betreuter Kanal. Keine automatischen
  Antworten, keine KI-Mails, keine automatischen Nachfassmails.
- **§8 Abs. 3:** Vereinbarung zur Auftragsverarbeitung vor dem Echtbetrieb mit Personendaten. Für Inhalte,
  Einwilligungen, Impressum und Datenschutz ist KBS verantwortlich.
- **§9:** KBS prüft auf einem Testsystem (die Vorschau-Adresse) und meldet wesentliche Mängel binnen zehn Werktagen.

## Was nicht dazugehört

Kampagnen gestalten, Werbekunden gewinnen, fremde Werbenetzwerke, Gebühren Dritter, rechtliche Prüfung von
Verkaufsbedingungen, unbegrenzte Content-Übernahme (A3). Rund-um-die-Uhr-Bereitschaft und neue Hauptmodule (B4).
Automatische E-Mails jeder Art. Zwei gebündelte Korrekturrunden je Modul sind enthalten (§3 Abs. 1).
