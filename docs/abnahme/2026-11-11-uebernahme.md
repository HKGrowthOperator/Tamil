# Übernahme des Altbestands in die neue Website (Vertrag A1, Schritt vor Tor G4)

Datum: 11.11.2026 · Ziel: `https://tamil-web.167.233.76.202.sslip.io` (Vorschau-Adresse, Testsystem) · Werkzeug:
`tools/migration.py` · Die alte tamil.de wurde nur gelesen.

## Ergebnis

| | Anzahl |
|---|---|
| Beiträge auf der neuen Website | 532 (530 Beiträge und 2 alte Seiten, die Beiträge geworden sind) |
| nicht übernommen | 3 Beiträge, die nur in der Rubrik „test“ lagen; 14 Altlast-Seiten (Anmeldung, Sicherungen, leere Seiten) |
| Seiten | 7 (Kontakt, Events, Über uns, Service FSK, TV, Datenschutz, Impressum) |
| Medien | 1445 |
| Weiterleitungen | 25 |
| Dauer | 48 Minuten, ohne Fehler |

## Prüfliste

| Prüfung | Ergebnis |
|---|---|
| Anzahl der Beiträge stimmt mit dem Export überein | ja: 532 |
| Stichprobe von zehn Beiträgen (Datum, Titel, Adresse, Beitragsbild, Text, Seite lädt, keine Bildadressen der alten Seite) | 10 von 10 |
| Alle Weiterleitungen antworten mit 301 und das Ziel lädt | 25 von 25 |
| Zweiter Lauf legt nichts neu an | ja: 532 vorhanden, 0 neu, 0 neue Medien |
| Sichtprüfung (Start, Rubrik Kino, drei Artikel, Events, Kontakt) bei 390, 820 und 1280 | 21 Aufnahmen, 0 Fehler: kein seitliches Scrollen, keine Konsolenfehler, keine leeren Bilder |
| Anwendungspasswort der Übernahme entfernt | ja: Variable gelöscht, Website neu gestartet |

## Bekannte Lücken (kein Fehler der Übernahme)

- **Impressum:** Die Seite der alten Website ist leer. KBS muss den Text liefern.
- **Datenschutz:** Der alte Text ist übernommen und veraltet. KBS muss ihn ersetzen.
- **Kontaktangaben der neuen Seite** (Telefon, E-Mail, WhatsApp) fehlen; die Felder bleiben leer.
- **Zwei Bilder** in einem Beitrag von 2019 („In Sri Lanka kehrt die Angst zurück“) fehlen schon auf der alten Seite.
- **314 Beitragsbilder** sind schmaler als 1200 Pixel und wirken groß gezeigt unscharf.
- **41 Bilder** in 19 Beiträgen liegen auf fremden Servern und bleiben dort.
- **43 eingebettete fremde Inhalte**, die nicht von YouTube stammen, hat der Filter der Website entfernt.
- **Texte der alten Seite** sind unverändert, auch die Adresse `info@tamil.de` in elf Beiträgen.
- **Die Website zeigt noch das bisherige Aussehen.** Das neue Design `klar2` folgt nach den Toren G2 und G3.

## Urteil

Technisch abgeschlossen. Das Urteil des Auftraggebers zur Live-Website (Tor G4) steht aus und folgt nach dem neuen
Design.
