# Festlegung F0: Grundlage (Website-Technik und Cockpit)

Vertrag: A1 (Basis-SEO, Performance, Pflichtinformationen, Cookie-Consent), B1 (Cockpit mit Rollen, Stopp-Funktion,
Protokoll), §8. Stand: **Vorschlag vom 11.11.2026, wartet auf das Ja von Luis.** Die reine Technik (Upgrade-Routine,
Register, Tests) beginnt sofort, weil sie keine Geschäftsregel enthält.

## Was gebaut wird

**Website**
1. **Upgrade-Routine:** Bei jedem Start prüft die Website ihre Versionsnummer und richtet Neues nach (Tabellen,
   Seiten, Rechte). Ohne sie kämen neue Bausteine auf der laufenden Website nie an.
2. **Angaben für Suchmaschinen und soziale Netze:** je Seite Titel und Beschreibung, Vorschaubild 1200 × 630,
   Artikel-Schema (`NewsArticle`), Brotkrumen. Suche und Buchungsseiten bleiben aus dem Index. Der Radar liefert
   Beschreibung und Fokus-Schlagwort mit. Die Sitemap kommt weiter aus WordPress.
3. **Tempo:** Dateien des Themes ein Jahr im Browser-Speicher, Bilder 30 Tage, Seiten für nicht angemeldete Besucher
   60 Sekunden. Formular- und Buchungsseiten werden nie zwischengespeichert.
4. **Cookie-Zustimmung:** eigene Lösung ohne fremden Dienst. Drei Kategorien: *notwendig* (immer an), *externe
   Medien* (YouTube, TV-Sender), *Statistik* (vorbereitet, derzeit leer). Hinweis beim ersten Besuch mit „Alle
   akzeptieren“, „Nur notwendige“ und „Einstellungen“; im Fuß ein Link „Cookie-Einstellungen“. Ohne Zustimmung lädt
   nichts von Dritten; ein einzelnes Video lässt sich weiter per Klick laden. Die Wahl wird sechs Monate im Browser
   gespeichert, nichts geht an Dritte.
5. **Rechtsseiten:** „Impressum“ und „Datenschutz“ sind normale Seiten, die KBS in WordPress pflegt. Sie werden
   angelegt und im Fuß verlinkt; veröffentlicht wird der Text, den KBS liefert.
6. **Funktionsschalter:** Jeder neue Baustein lässt sich einzeln ein- und ausschalten. Im Echtbetrieb bleibt er aus,
   bis Auftragsverarbeitung und Rechtstexte vorliegen; auf dem Testsystem ist er an.

**Cockpit**
7. **Stopp-Schalter**, einer für alles und je einer pro Kanal:

   | Schalter | hält an |
   |---|---|
   | alles | jede automatische Ausführung und jeden Aufruf nach außen |
   | Redaktion | Scan der Quellen und die Agenten-Redaktion |
   | Website | das Übertragen freigegebener Beiträge nach WordPress |
   | Eingang | Abholen und Vorbereiten von Einsendungen |
   | Verzeichnis | die Prüfung von Verzeichniseinträgen |
   | Instagram · Facebook · WhatsApp | den jeweiligen Kanal |

   Anhalten heißt: Es beginnt nichts Neues, und unmittelbar vor jedem Aufruf nach außen wird der Schalter noch einmal
   geprüft. Bearbeiten und Freigeben von Hand bleiben möglich; Freigegebenes wartet, bis der Schalter wieder an ist.
   Jeder Stopp braucht einen Grund und steht mit Person und Zeit im Protokoll. Ein Banner zeigt den Stand auf jeder
   Seite. Als Notweg gibt es den Befehl `python -m news_radar stopp an|aus [kanal]`.
8. **Rollen:**

   | Rolle | darf |
   |---|---|
   | `admin` | alles: Benutzer, Schalter, „Erneut“ bei toten Jobs, Regeln ansehen, Export |
   | `redaktion` | bearbeiten, freigeben, Eingang und Verzeichnis prüfen, anhalten (auch „alles“), einen einzelnen Kanal wieder einschalten |
   | `leser` | alles ansehen, nichts ändern |

   Den Schalter „alles“ wieder einschalten darf nur `admin`.
9. **Protokoll:** Jede Freigabe und jede automatische Ausführung steht mit Person oder Agent, Zeit, Gegenstand, Kanal
   und der Fassung der Regel im Protokoll. Ansicht mit Filter, Export als Datei.
10. **Zeitplan-Ansicht:** was wann zuletzt lief und wann es wieder läuft.
11. **Kein Mailversand:** Ein Test schlägt fehl, sobald irgendwo im Code E-Mail verschickt würde.

## Was automatisch läuft und was nicht

Automatisch: Upgrade beim Start, Auslieferung der Angaben für Suchmaschinen, Zeitplan. Von Hand: Schalter,
Benutzer und Rollen, Rechtstexte.

## Was nicht dazugehört

Statistik-Dienste (Google Analytics und ähnliche) sind nicht vorgesehen; die Kategorie ist nur vorbereitet. Ein
Dienst zur Auslieferung über ein fremdes Netz (CDN) ist nicht geplant. Eine rechtliche Prüfung der Texte leisten wir
nicht.

## Fristen (Vorschlag)

| Daten | Aufbewahrung |
|---|---|
| Einsendungen aus Formularen | 90 Tage nach Abschluss, dann gelöscht |
| Protokoll im Cockpit | 12 Monate |
| Sicherungen | 30 Tage |

## So wird abgenommen

- Schalter „Instagram“ an: ein freigegebener Beitrag geht nicht hinaus, das Protokoll nennt den Grund. Schalter
  „alles“ an: weder Scan noch Übertragung laufen; `leser` kann nichts schalten (Test T7).
- Ein Artikel zeigt beim Teilen in WhatsApp oder Facebook Titel, Text und Bild.
- Ohne Zustimmung lädt keine Adresse außerhalb der eigenen Website (im Browser geprüft).
- Messung am Handy (Lighthouse, mobil) auf dem Testsystem für Startseite und Artikel: Zielwert Performance 80 oder
  mehr, kein seitliches Scrollen bei 390, 820 und 1280 Pixeln.

## Zuarbeit von KBS

Impressum, Datenschutzerklärung und der Text für den Cookie-Hinweis; wer im Cockpit welche Rolle bekommt.

## Offen für Luis (mit Vorschlag)

1. Rollen wie oben, oder soll `redaktion` nicht anhalten dürfen? Vorschlag: wie oben, Anhalten ist nie gefährlich.
2. Soll der Cookie-Hinweis immer erscheinen, auch wenn nur Notwendiges gespeichert wird? Vorschlag: ja, weil der
   Vertrag eine Zustimmungstechnik verlangt und externe Medien eine Wahl brauchen.
3. Fristen wie in der Tabelle? Die Frist für Buchungsdaten folgt in F3 (steuerliche Vorgaben).
4. Zielwert 80 für das Tempo am Handy als Abnahmewert?
