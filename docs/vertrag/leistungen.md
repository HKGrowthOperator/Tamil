# Leistungsverzeichnis tamil.de

Grundlage: Gesamtvertrag (Vertragsstand 11.11.2026), **Anlage 1, Teil A und B**. Dieses Verzeichnis ist der Maßstab
für „fertig“. Hier steht nur der Leistungsumfang für tamil.de. Preise, Zahlungsplan und die Vertragsdatei liegen nicht
im Repo. Merzlicht (Anlage 2) und AJ Gamestation (Anlage 3) sind eigene Projekte.

Für Luis liegen Überblick, Festlegungen und die Liste für KBS als Dokument vor (privat, zum Kommentieren und
Bestätigen): https://claude.ai/artifact/3ebPy94NJHUjafi54sFtYP. Maßgeblich für den Bau ist die Fassung im Repo; ein Ja
oder eine Änderung aus dem Dokument wird hier und in `docs/abnahme/` nachgetragen.

Stand: `fertig` · `teilweise` · `offen` · `wartet` (auf Zuarbeit oder ein Tor). Bei jedem Baustein nachtragen.
Bausteine und Reihenfolge: siehe unten. Einzelheiten je Baustein: `festlegung-<baustein>.md`.

Spalte „Stand“ zuletzt nachgezogen am 22.11.2026 (Ja von Luis), nur diese Spalte. Dort heißt `gebaut`: der Code liegt
im Repo. `automatisch geprüft`: Test oder Szenario bestanden, mit nachgestellten Schnittstellen. `im Echtbetrieb aus`:
per Schalter aus, mit dem Grund. `von Hand abgenommen` steht nur, wo ein Handtest protokolliert ist; bis 22.11. ist
das bei keinem Punkt der Fall. Die automatischen Ergebnisse stammen aus dem Lauf vom 14./15.11. und sind seither nicht
neu gelaufen.

## Teil A – Website, Redaktion, Werbebuchung

| Nr. | Der Vertrag verlangt | Baustein | Stand 22.11.2026 |
|---|---|---|---|
| A1.1 | Individueller responsiver Neuaufbau als Magazin-, Event-, Nachrichten- und Community-Portal für Desktop und Handy | 6 | teilweise: gebaut im Aussehen `klar2` (Wahl von Luis am 16.11., `docs/abnahme/2026-11-16-G2-klar2.md`), Theme 3.16.1 auf dem Testsystem (`docs/entscheidungen.md`, 22.11.); Startseite: drei Proben gebaut, die Wahl von Luis ist offen; nicht von Hand abgenommen (Tor G4); die Live-Domain ist nicht umgestellt (Tor B3) |
| A1.2 | CMS mit Startseite, Artikeln, Rubriken, Suche, Beitragsarchiv | – | gebaut, seit 16.11. im Aussehen `klar2` (Theme 3.16.1 auf dem Testsystem, `docs/entscheidungen.md`); nicht von Hand abgenommen |
| A1.3 | Event-Einreichung | 2 | gebaut: Formular „Event einreichen“ (Plugin `tamil-site`); automatisch geprüft (`tests/wp/test_einsendungen.py` 55/55, Szenario 80, `docs/abnahme/2026-11-15-B5.md`); auf dem Testsystem eingeschaltet (Luis 17.11., `docs/betrieb.md`); im Echtbetrieb aus (wartet auf Auftragsverarbeitung und Einwilligungstext von KBS); Handtest T7 Teil C nicht gelaufen |
| A1.4 | Veranstaltungskalender | 2 | teilweise: Listen- und Monatsansicht für kommende Termine; Ende, Veranstalter, Preis und Land überträgt der Radar nur bei Terminen aus einer Einsendung (`news_radar/publisher.py`, `TERMIN_FAKTEN`), bei Terminen aus dem Scan nicht (`docs/uebergabe/backend-nick.md`, 6 und 6e); nicht von Hand abgenommen |
| A1.5 | Autor- und Quellenangaben | 6 | teilweise: Quelle und Bildnachweis vorhanden, Nachweis mit Links auf Dateiseite und Lizenz (Theme `inc/bildkette.php`); als Autor steht nach außen die Redaktion (Entscheidung 12.11., `tamil-site/includes/autoren.php`); nicht von Hand abgenommen |
| A1.6 | Kontakt | 2 | gebaut: Formular „Kontakt“ als Teil der Einreichungen (Plugin `tamil-site`, `tests/wp/test_einsendungen.py` 55/55, `docs/abnahme/2026-11-15-B5.md`); auf dem Testsystem eingeschaltet (`docs/betrieb.md`); im Echtbetrieb aus (wartet auf Auftragsverarbeitung und Einwilligungstext); ob die Seite Kontakt das Formular zeigt: nicht nachgeprüft am 22.11. |
| A1.7 | Für KBS bearbeitbare Inhalte, pflegbarer Inhalts- und Medienbestand | – | fertig (WordPress, Einstellungen, Menüs, Mediathek) (nicht nachgeprüft am 22.11.) |
| A1.8 | Neun Themenbereiche (Nachrichten, Community, Entertainment, Kino, Events, Küche, Sport, Kultur, Kontakt), konsistente Navigation | 6 | teilweise: acht Rubriken und die Seite Kontakt; Kontakt fehlt in der Rubrikleiste (nicht nachgeprüft am 22.11.) |
| A1.9 | Technische Übernahme vorhandener Inhalte | 0 | fertig: 532 Beiträge, 7 Seiten, 1445 Medien (`docs/abnahme/2026-11-11-uebernahme.md`) |
| A1.10 | Basis-SEO | 1 | gebaut, automatisch geprüft (`tests/wp/test_seo.py` 23/23, `docs/abnahme/2026-11-15-B5.md`): Titel, Beschreibung, Vorschau für soziale Netze, Artikel- und Termin-Schema, Brotkrumen; das Testsystem ist bis zum Livegang für Suchmaschinen gesperrt (`docs/betrieb.md`); nicht von Hand abgenommen |
| A1.11 | Weiterleitungen | 0 | fertig: 25 Einträge, alle geprüft |
| A1.12 | Sitemap | – | gebaut (WordPress-Kern, `wp-sitemap.xml`); auf dem Testsystem bis zum Livegang abgeschaltet, weil es für Suchmaschinen gesperrt ist (`docs/betrieb.md`, Tor B3) |
| A1.13 | Performance- und Mobiloptimierung | 1, 6 | teilweise: Bildgrößen, lokale Schriften, Cache-Kopfzeilen gebaut; am Handy gemessen auf dem Testsystem (Lighthouse mobil, Theme 3.9.0, je ein Lauf, zehn Seitentypen: Leistung 96 bis 100, Zielwert 80; `docs/abnahme/2026-11-21-nacht.md`); mit Theme 3.16.1 und auf der Live-Domain nicht gemessen |
| A1.14 | Einbindung rechtlich freigegebener Pflichtinformationen | 1 | wartet: Impressum und Datenschutz brauchen Texte von KBS (das Impressum der alten Seite ist leer); weiter offen laut `docs/vertrag/zuarbeit-kbs.md`, Nr. 2 |
| A1.15 | Cookie-Consent-Technik | 1 | gebaut, automatisch geprüft (`tests/wp/test_consent.py` 8/8, `docs/abnahme/2026-11-15-B5.md`): eigene Lösung ohne fremden Dienst; das Ja zu F0 liegt vor (13.11., `docs/abnahme/2026-11-13-ja-zu-allem.md`); im Echtbetrieb aus (wartet auf den Text von KBS); ob auf dem Testsystem eingeschaltet: nicht nachgeprüft am 22.11. |
| A2.1 | Öffentliche Angebots- und Preisdarstellung; KBS pflegt Formate, Preise und Laufzeiten im Admin | 4 | gebaut (Plugin `tamil-site`, Seite „Werben“, Pflege im Admin; Ja zu F3 am 13.11.); auf dem Testsystem eingeschaltet, ohne Stripe-Schlüssel mit Preisen „auf Anfrage“ (`docs/betrieb.md`); wartet auf Formate, Preise und Laufzeiten von KBS; nicht von Hand abgenommen |
| A2.2 | Self-Service-Buchung: Werbefläche, Laufzeit, verfügbare Belegung wählen; Kundendaten; Werbemittel hochladen | 4 | gebaut, automatisch geprüft (`tests/wp/test_werbung.py` 34/34, Stripe nachgestellt, `docs/abnahme/2026-11-15-B5.md`); auf dem Testsystem eingeschaltet, dort ohne Online-Zahlung (`docs/betrieb.md`); im Echtbetrieb aus (wartet auf Stripe-Konto von KBS und Auftragsverarbeitung); Handtest T5 nicht gelaufen |
| A2.3 | Automatische Reservierungs- und Verfügbarkeitsprüfung gegen Doppelbuchung; Freigabeprüfung für unzulässige oder auffällige Werbemittel | 4 | gebaut, automatisch geprüft (`test_werbung.py`: gleichzeitige Buchungen, genau eine gewinnt; bezahlt ohne Prüfung erscheint nicht; `docs/abnahme/2026-11-15-B5.md`); im Echtbetrieb aus (wartet auf Stripe-Konto von KBS); nicht von Hand abgenommen |
| A2.4 | Online-Zahlung über ein von KBS freigegebenes Konto, gesicherter Statusabgleich, Aktivierung nur nach bestätigter Zahlung | 4 | gebaut, automatisch geprüft gegen eine nachgestellte Schnittstelle (`test_werbung.py`: Zahlung, Webhook mit Signatur, Abbruch; `docs/abnahme/2026-11-15-B5.md`); die im Vertragstest T5 genannte Datei `tests/wp/test_buchung.py` fehlt weiter; im Echtbetrieb aus (wartet auf das Stripe-Konto von KBS, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`); Handtest T5 nicht gelaufen |
| A2.5 | Automatischer Start, Wechsel und Ablauf nach gebuchter Laufzeit; Buchungs- und Zahlungsübersicht für Kunden auf der Website | 4 | gebaut, automatisch geprüft (`test_werbung.py`: Aktiv-Funktion mit gestelltem Datum, Ablauf nach einem Tag, danach Eigenanzeige; `docs/abnahme/2026-11-15-B5.md`); Kundenübersicht: nicht nachgeprüft am 22.11.; im Echtbetrieb aus (wartet auf Stripe-Konto von KBS); Handtest T6 nicht gelaufen |
| A2.6 | Admin mit Buchungsliste, Kampagnenstatus, Laufzeiten, Prüfung, Pausieren/Beenden, einfacher Statistik | 4 | gebaut (Plugin `tamil-site`: Buchungsliste, Prüfung, Pausieren, Fortsetzen, Beenden, Zählung; `test_werbung.py` 34/34, `docs/abnahme/2026-11-15-B5.md`); im Echtbetrieb aus (wartet auf Stripe-Konto von KBS); nicht von Hand abgenommen |

## Teil B – Agent, Verzeichnis, Social, Betreuung

| Nr. | Der Vertrag verlangt | Baustein | Stand 22.11.2026 |
|---|---|---|---|
| B1.1 | Zentrales webbasiertes Agenten-Cockpit mit Rollen, Aufgaben- und Freigabestatus, Bearbeitung, zeitgesteuerten Ausführungen, Fehleransicht, Stopp-Funktion und Protokoll | 1 | gebaut, automatisch geprüft (`tests/test_schalter.py` 21/21, `tests/test_rechte.py` 9/9, Szenarien 52 bis 54, `docs/abnahme/2026-11-15-B5.md`): Stopp-Schalter (alles und je Kanal), Rollen `admin`, `redaktion`, `leser`, Protokoll mit Filter und Export, Zeitplan-Ansicht, Fehleransicht; das Ja zu F0 mit der Rollen-Zuordnung liegt vor (13.11., `docs/abnahme/2026-11-13-ja-zu-allem.md`); Handtest T7 Teil A und B nicht gelaufen |
| B1.2 | Automatische Erfassung und Vorbereitung eingehender Beiträge, Event-Einreichungen, Kooperations- und Werbeanfragen; Vorschläge nachvollziehbar und editierbar | 2 | gebaut, automatisch geprüft (`tests/test_eingang.py` 21/21, Szenarien 80 bis 87, `docs/abnahme/2026-11-15-B5.md`; Ja zu F1 am 13.11.); im Echtbetrieb aus (Schalter `RADAR_EINGANG`, wartet auf Auftragsverarbeitung und Rechtstexte, `docs/betrieb.md`); nicht von Hand abgenommen |
| B1.3 | Durchsuchbares öffentliches Verzeichnis (Business, Dienstleister, Vereine, Tempel) mit Kategorien, Profilen, Kontaktdaten, Standortfiltern, Premium-Markierung durch die Verwaltung | 3 | gebaut, automatisch geprüft (`tests/wp/test_verzeichnis.py` 21/21, `docs/abnahme/2026-11-15-B5.md`; Ja zu F2 am 13.11.); auf dem Testsystem eingeschaltet mit vier gekennzeichneten Beispiel-Einträgen (`docs/betrieb.md`); im Echtbetrieb aus (wartet auf Auftragsverarbeitung und Einwilligungstext); Handtest T4 nicht gelaufen |
| B1.4 | Agent für Verzeichniseinträge: Dubletten- und Fehlfeldprüfung, Klassifikation, Vorschläge zur Freigabe; nichts Ungeprüftes oder Erfundenes | 3 | gebaut, automatisch geprüft (`tests/test_verzeichnis_agent.py` 34/34, Szenarien 88 und 89, `docs/abnahme/2026-11-15-B5.md`); im Echtbetrieb aus (Schalter `RADAR_VERZEICHNIS`, wartet auf Auftragsverarbeitung und Rechtstexte, `docs/betrieb.md`); Handtest T4 nicht gelaufen |
| B2.1 | Veröffentlichte Artikel und Events erzeugen automatisch Text, Bild- und Formatvorgaben, Verweise und einen Social-Beitrag | 5 | gebaut, automatisch geprüft im Trockenmodus (`tests/test_social.py` 78/78, Szenario 77, `docs/abnahme/2026-11-15-B5.md`; Ja zu F4 am 13.11.); das Social-Bild hat noch das alte Aussehen, das freigegebene Kartensystem ist nicht angebunden (`news_radar/social/bild.py`, `docs/uebergabe/backend-nick.md` 6d); im Echtbetrieb aus (Schalter `RADAR_SOCIAL`); nicht von Hand abgenommen |
| B2.2 | Veröffentlichung auf einem berechtigten Instagram-Professional-Konto nach einmalig genehmigten Regeln | 5 | gebaut, automatisch geprüft gegen eine nachgestellte Schnittstelle (Szenarien 70 und 78, `docs/abnahme/2026-11-15-B5.md`); im Echtbetrieb aus (wartet auf die Meta-Konten von KBS mit `META_ZUGANG`, `META_IG_USER_ID`, `META_PAGE_ID`, die einmalige Freigabe des Regelwerks durch KBS, Auftragsverarbeitung und Rechtstexte); Handtest T1 nicht gelaufen |
| B2.3 | Derselbe Inhalt automatisch auf der verbundenen Facebook-Seite, ohne zweite Einzelfreigabe | 5 | gebaut, automatisch geprüft gegen eine nachgestellte Schnittstelle (Szenario 70: zuerst Instagram, dann Facebook; `docs/abnahme/2026-11-15-B5.md`); im Echtbetrieb aus (wartet wie B2.2); Handtests T1 und T2 nicht gelaufen |
| B2.4 | Fehler, Dubletten, Pausen, Historie und nicht freigabefähige Beiträge im Cockpit sichtbar | 5 | gebaut, automatisch geprüft (Cockpit-Seite „Social“; Szenarien 72, 73, 76, `docs/abnahme/2026-11-15-B5.md`); im Echtbetrieb aus (Schalter `RADAR_SOCIAL`); nicht von Hand abgenommen |
| B3.1 | WhatsApp-Channel-Inhalte (Text, Link, Bild) automatisch vorbereitet und bereitgestellt; Veröffentlichung von Hand, solange es keine offizielle Schnittstelle gibt | 5 | gebaut, automatisch geprüft (`tests/test_social.py` 78/78, Szenario 74, `docs/abnahme/2026-11-15-B5.md`); im Echtbetrieb aus (wartet auf das Einschalten von Social und den Kanal von KBS, `WHATSAPP_KANAL_URL`); Handtest T3 nicht gelaufen |
| B3.2 | E-Mail bleibt vollständig manuell | – | erfüllt: im Code wird keine E-Mail verschickt; ein Test sichert das ab (Baustein 1) |
| B4 | Vier Wochen Feinjustierung nach Inbetriebnahme des Agenten, drei Monate Betreuung nach dem Livegang | 7 | beginnt nach dem Livegang |
| B5 | Sieben wesentliche Abnahmetests | 7 | teilweise (Protokoll vom 15.11.2026, bis 22.11. kein neueres B5-Protokoll in `docs/abnahme/`): automatisch 6 von 7 bestanden, T5 ohne die genannte Testdatei (`tests/wp/test_buchung.py` fehlt weiter); Handtests 0 von 7 gelaufen (`docs/abnahme/2026-11-15-B5.md`) |

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

| Nr. | Test laut Vertrag | Baustein | Automatisch | Von Hand auf dem Testsystem | Stand 15.11.2026 |
|---|---|---|---|---|---|
| T1 | Artikel zu Instagram und Facebook (tatsächlich oder durch die Schnittstelle bestätigt) | 5 | `tests/test_social.py`, Abnahme-Szenarien | Beitrag freigeben; Kennung und Link beider Kanäle stehen in der Historie | automatisch bestanden (nachgestellte Schnittstelle); Handtest wartet auf Meta-Konten und Regelwerk-Freigabe |
| T2 | Veranstaltung zu Instagram und Facebook | 5 | Szenarien „Termin in der Zukunft“, „Termin vorbei“ | Termin aus einer Einsendung veröffentlichen, beide Beiträge prüfen | automatisch bestanden; Handtest wartet auf Meta-Konten und Auftragsverarbeitung |
| T3 | WhatsApp-Beitragsentwurf | 5 | `tests/test_social.py` | Text kopieren, im Kanal posten, „gepostet“ markieren | automatisch bestanden; Handtest wartet auf Einschalten von Social und den Kanal von KBS |
| T4 | Verzeichnis-Neueintrag und Änderungsfreigabe | 3 | `tests/wp/test_verzeichnis.py`, `tests/test_verzeichnis_agent.py` | Eintrag vorschlagen, freigeben, öffentlich finden; Telefonnummer ändern lassen, Unterschied prüfen, freigeben | automatisch bestanden; Handtest wartet auf Auftragsverarbeitung |
| T5 | Werbebuchung mit erfolgreichem und fehlgeschlagenem Checkout | 4 | `tests/wp/test_buchung.py` | Testkarte mit Erfolg und mit Ablehnung; die Kundenübersicht zeigt den Stand | offen: `tests/wp/test_buchung.py` fehlt, Ersatz `test_werbung.py` bestanden; Handtest wartet auf Stripe-Konto |
| T6 | Geprüfte Kampagnenaktivierung und Laufzeitende | 4 | Aktiv-Funktion mit gestellter Uhr | Buchung mit einem Tag Laufzeit: freigeben, Banner sehen, am Folgetag wieder Eigenanzeige | automatisch bestanden; Handtest wartet auf Stripe-Konto |
| T7 | Agenten-Stopp und Fehlerbehandlung; redaktionelle Verwaltung | 1, 2 | `tests/test_schalter.py`, `tests/test_rechte.py`, `tests/test_eingang.py` | Kanal stoppen, Beitrag freigeben: nichts geht hinaus, das Protokoll nennt den Grund; Fehler auslösen, „Erneut“; Termin einreichen bis zum Kalender | automatisch bestanden; Handtest offen (Stopp und „Erneut“ sofort möglich, Termin wartet auf Auftragsverarbeitung) |

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
