# Bilder und Lizenzen

Teil der Software-Spezifikation für tamil.de. Stand: 13.11.2026. Gilt für den News-Radar (Bildkette, Cockpit), die
Website (WordPress, Plugin `tamil-radar`, Theme `tamil`) und Social (Baustein 5, Festlegung F4).

Grundlage: Vertrag A1.5 (Quellen- und Bildangaben), B2.1 (Bild- und Formatvorgaben für Social), B2.2 (Instagram nur
nach genehmigten Regeln), §3 Abs. 2 (kostenpflichtige Schnittstellen nur mit Freigabe), §3 Abs. 3 (nur offizielle
Zugänge), §8 Abs. 1 (automatisch nur nach freigegebenen Regeln, Protokoll), §8 Abs. 3 (Verantwortung für Inhalte bei
KBS); Festlegung F4 (Regel „Bild nur mit Recht für Social, sonst Bildkarte“); Entscheidungen vom 20.10., 09.11.,
10.11., 11.11. und 12.11.2026 (`docs/entscheidungen.md`).

Vorgabe von Luis: „Definiere einmal die Bildgenerierung und woher du dir die Bilder ziehst. Wir brauchen auch immer
Lizenzen, am besten da drauf. Wenn wir keine haben, müssen wir die anderen eingeben, das ist auch kein Problem.“

## 1. Grundsätze

| Nr. | Grundsatz |
|---|---|
| G1 | **Kein Bild ohne Lizenz-Datensatz.** Das gilt für jedes Bild, das auf die Website oder in einen Social-Beitrag geht, auch für eigene Fotos und die Bildkarte. |
| G2 | **Die Lizenz stellt der Radar selbst fest**, nicht der Vorschlag: Lizenz und Urheber kommen aus der Commons-API, aus dem Bildquellen-Register oder aus der Stock-Schnittstelle. Was ein Agent nur behauptet, zählt nicht. Einzige Ausnahme ist die manuelle Eingabe durch die Redaktion mit Beleg (Abschnitt 3.4). |
| G3 | **Gate:** Ohne vollständigen Lizenz-Datensatz mit Umfang „Website“ keine Freigabe. Ohne Umfang „Social“ geht das Bild nicht nach Instagram, Facebook oder in den WhatsApp-Entwurf; dort steht dann die Bildkarte. |
| G4 | **Nachweis sichtbar am Bild:** Bildunterschrift auf der Website, Nachweis im Text des Social-Beitrags. |
| G5 | **Kein Bild täuscht ein Ereignis vor.** KI-Bilder sind nur Symbolbilder, immer gekennzeichnet, nie mit erkennbaren realen Personen. |
| G6 | **Im Zweifel die Bildkarte „Grafik: Tamil.de“.** Sie ist immer verfügbar und rechtlich sauber. Luis will „überall Bilder“ (11.11., 12.11.), aber keine fremden Fotos ohne Recht. |

## 2. Bildquellen in fester Reihenfolge

Die Bildkette probiert die Stufen der Reihe nach; das erste Bild mit vollständiger Lizenz gewinnt. Die Redaktion kann
im Cockpit jede Stufe gezielt wählen oder ein eigenes Bild hochladen (mit Lizenz, Abschnitt 3.4).

| Stufe | Quelle | Zulässig, wenn | Lizenz-Kürzel | Umfang Standard | Stand im Code |
|---|---|---|---|---|---|
| 1 | Eigenes Archiv mit Rechten | Eintrag in `data/archiv/archiv.json` mit Rechteinhaber, Lizenz, Umfang; Thema oder Rubrik passt; Ablauf nicht überschritten | `eigen` oder `nutzungsrecht` | laut Eintrag | gebaut (`news_radar/agents/media.py` `_archiv`) |
| 2 | Register-Quellen (Tempel, Vereine, Veranstalter, Festivals, Kinos, Betriebe, Personen, Sport) | Host steht in `[[bildquellen]]` (`sources.toml`) **und** die Seite ist ein Beleg genau dieser Story; Bild liegt beim eingetragenen Host | `presse-redaktionell` (ohne schriftliche Erlaubnis) oder `nutzungsrecht` (mit Erlaubnis) | nur Website, außer die Erlaubnis nennt Social | gebaut als Agent-Weg (`news_radar/bildvorschlag.py` `_quelle`); in der automatischen Kette fehlt es (siehe 6.2) |
| 3 | Wikimedia Commons | Lizenz mit Lizenz-Adresse bei creativecommons.org: CC BY, CC BY-SA, CC0 oder Public Domain Mark; Urheber bekannt | `cc-by-<v>`, `cc-by-sa-<v>`, `cc0-1.0`, `pdm-1.0` | Website und Social (Regeln 2.3) | gebaut als Agent-Weg (`bildvorschlag.py` `_commons`); in der automatischen Kette fehlt es |
| 4 | Stock mit eindeutiger Lizenz | Pexels automatisch über die Schnittstelle; Unsplash nur von Hand (2.4); keine erkennbaren Personen in Nachrichten-Zusammenhang, keine Marken | `pexels`, `unsplash` | Website und Social | teilweise (`news_radar/images.py` `from_unsplash`, `from_pexels`) |
| 5 | KI-Symbolbild (Gemini), zuerst aus dem Bildpool | **erst nach neuem Ja von Luis** (Entscheidungen 09.11. und 11.11.: „keine KI-Bilder“); Bedingungen in 4.2 | `ki-symbolbild` | Website und Social, immer gekennzeichnet | gebaut, aber nicht abgesichert (`news_radar/bilder.py`, `media.py` `_ki`) |
| 6 | Bildkarte „Grafik: Tamil.de“ | immer | `tamil-grafik` | Website und Social | gebaut (`images.py` `branded_card`) |

Die Reihenfolge im Code (`news_radar/config.py`, `BILD_REIHENFOLGE`) lautet heute `archiv, quelle, stock, pool, ki,
karte` und kennt Commons nicht. Soll-Reihenfolge: `archiv, register, commons, stock, ki, karte` (Pool als Teil von
`ki`).

### 2.1 Eigenes Archiv

- Nur Bilder, deren Rechte KBS oder Tamil.de nachweislich hat (eigene Fotos, beauftragte Fotografen, schriftliche
  Erlaubnis). Zuarbeit KBS Nr. 14 (`docs/vertrag/zuarbeit-kbs.md`).
- Pflichtangaben je Bild wie im Lizenz-Datensatz (Abschnitt 3); fehlt eine, wird das Bild übersprungen (heute schon so).
- Der übernommene Altbestand der alten Seite (1445 Medien) ist **kein** Archiv mit Rechten: Für diese Bilder ist die
  Rechtelage unbekannt. Sie bleiben an ihren alten Beiträgen und werden nicht automatisch wiederverwendet.

### 2.2 Register-Quellen

- Register `[[bildquellen]]` in `sources.toml` (heute 28 Einträge): Host, Betreiber, Art, wörtlicher Nachweis,
  optional `bild_hosts`. Soziale Netzwerke und Bildagenturen sind fest gesperrt (`config.py`, `BILD_GESPERRT`,
  `BILD_GESPERRT_MARKEN`); geteilte Hoster (wp.com, cloudfront.net …) sind als `bild_hosts` verboten.
- Nur eigenes Material der Quelle, nur wenn die Seite ein Beleg der Story ist, nur für Berichte über diese
  Einrichtung oder dieses Ereignis. Agenturbilder werden am Umfeld erkannt und abgelehnt (`bildvorschlag.py`, `AGENTUR`).
- **Ohne schriftliche Erlaubnis** (heute bei allen Einträgen): Lizenz `presse-redaktionell`, Umfang **nur Website**.
  Restrisiko: Es gibt keine ausdrückliche Lizenz; die Entscheidung dafür hat Luis am 11.11. getroffen, die inhaltliche
  Verantwortung liegt bei KBS (§8 Abs. 3). Für Quellen, die oft genutzt werden, holt KBS eine schriftliche Erlaubnis
  ein; sie wird im Register als `erlaubnis` (Datum, Umfang, Ablage des Belegs) eingetragen und hebt den Umfang an.
- **Kinoplakate und Filmbilder** gehören dem Verleih bzw. der Produktion, nicht dem Kino oder Festival. Website: nur
  im Bericht über genau diesen Film, als Werbematerial mit Nachweis (Entscheidung 11.11.). Social und jede andere
  Nutzung: nur mit Freigabe des Verleihs. Plakate werden nie beschnitten (5.4).

### 2.3 Wikimedia Commons

- Erlaubt: CC BY und CC BY-SA (jede Version, mit Länderfassung), CC0 1.0 und Public Domain Mark 1.0, jeweils **nur mit
  Lizenz-Adresse** bei creativecommons.org. Abgelehnt: alles mit NC oder ND, „Fair use“, als NonFree markierte Dateien,
  Gemeinfreiheit ohne Lizenz-Adresse (PD-old, PD-US …, weil die Geltung in DACH offen ist), unbekannter Urheber bei
  CC BY/BY-SA. So umgesetzt in `bildvorschlag.py` (`commons_lizenz`, `_commons`).
- Lizenz, Urheber, Dateityp und Größe liest der Radar selbst aus der Commons-API (`extmetadata`), nie aus dem Vorschlag.
- Namensnennung (CC BY/BY-SA): Urheber, Lizenzname mit Link auf die Lizenz, Link auf die Dateiseite, Hinweis auf
  Änderungen („zugeschnitten“). CC 4.0 verlangt den Hinweis auf Änderungen ausdrücklich.
- **CC BY-SA:** Eine Bearbeitung steht wieder unter CC BY-SA. Deshalb auf Social **nur Zuschnitt, keine Logo-Leiste,
  kein Text im Bild** (sonst stünde das Logo unter einer freien Lizenz).
- Hinweise von Commons (`Restrictions`, z. B. Persönlichkeitsrechte, Marken) übernimmt der Radar in den Umfang; mit
  solchem Hinweis kein Social.

### 2.4 Stock mit eindeutiger Lizenz

Geprüft auf den offiziellen Lizenzseiten am 13.11.2026:

| Plattform | Kommerziell | Social | Nennung | Verboten | Quelle |
|---|---|---|---|---|---|
| Unsplash | erlaubt („Commercial and non-commercial purposes“) | nicht eigens genannt; die Lizenz erlaubt Kopieren, Bearbeiten, Verbreiten und Nutzen, also auch Social | nicht Pflicht („attribution is appreciated“) | Verkauf ohne wesentliche Bearbeitung; Sammeln von Bildern, um einen ähnlichen oder konkurrierenden Dienst nachzubauen. Zu Personen, Marken und Freigaben sagt die Lizenz nichts | unsplash.com/license, Abruf 13.11.2026 |
| Pexels | erlaubt (Werbung, Produkte genannt) | ausdrücklich erlaubt | nicht Pflicht („Attribution is not required“) | erkennbare Personen nicht in schlechtem Licht; keine unveränderten Kopien verkaufen; keine Empfehlung durch Personen oder Marken im Bild andeuten; nicht auf anderen Stock-Plattformen weiterverbreiten; nicht als Marke oder Firmenname | pexels.com/license, Abruf 13.11.2026 |

Zusätzlich gelten die Regeln der Schnittstellen (Abruf 13.11.2026):

- **Unsplash-API:** Bilder müssen über die von der API gelieferten Adressen eingebunden werden („hotlinked“), der
  Download-Endpunkt ist auszulösen, Fotograf und Unsplash sind mit Link (mit `utm_source`/`utm_medium`) zu nennen
  (help.unsplash.com, „Unsplash API Guidelines“). Tamil.de speichert Bilder in der WordPress-Mediathek und lädt sie für
  Instagram neu hoch; das passt nicht zur Hotlink-Pflicht. **Festlegung: Unsplash nicht automatisch über die API**,
  sondern nur von Hand (Redaktion lädt auf unsplash.com herunter und trägt die Lizenz im Cockpit ein).
- **Pexels-API:** sichtbarer Link zu Pexels und Nennung des Fotografen „when possible“; Grenze 200 Anfragen je Stunde
  und 20 000 je Monat (pexels.com/api/documentation). **Festlegung: Pexels ist der automatische Stock-Weg**, mit
  Nennung „Foto: Name / Pexels“ und Link auf die Fotoseite.
- Für beide: Stockfotos sind Symbolbilder. In Nachrichten keine erkennbaren Personen (keine Modellfreigabe bekannt,
  Persönlichkeitsrecht), keine Marken und Logos, keine Fotos, die wie Ereignisfotos wirken. In Nachrichten trägt der
  Nachweis den Zusatz „Symbolbild“.

### 2.5 KI-Symbolbild

Siehe Abschnitt 4. Der Bildpool besteht aus KI-Bildern und gehört deshalb zu dieser Stufe; er gilt nur, wenn KI-Bilder
freigegeben sind.

### 2.6 Bildkarte

Eigene Grafik aus Rubrikfarbe, Titel, Kolam und Wortmarke (`images.py` `branded_card`, Schrift Catamaran unter der
SIL Open Font License). Lizenz `tamil-grafik`, Umfang Website, Social, Print. Nachweis „Grafik: Tamil.de“. Das Aussehen
folgt der abgenommenen Kachel aus dem neuen Design (Entscheidung 10.11.).

### 2.7 Verboten

| Verboten | Warum | Abgesichert durch |
|---|---|---|
| Agenturbilder (dpa, Keystone, Getty, Reuters, AFP, AP, Imago, picture alliance, EPA u. a.), auch auf Seiten von Register-Quellen | keine Lizenz, Abmahnrisiko für KBS (Entscheidung 11.11.) | `BILD_GESPERRT`, `AGENTUR` in `bildvorschlag.py` |
| Bilder aus anderen Medien (Zeitungen, Sender, Portale) | Urheberrecht; der Radar übernimmt Pressebilder von Nachrichtenquellen bewusst nicht | Register enthält keine Medien; `images.py` Kopfkommentar |
| Bilder aus sozialen Netzwerken (Instagram, Facebook, TikTok, X, YouTube, Pinterest), auch eingebettet oder über deren CDN | keine Lizenz; Instagram als Quelle nur über Export oder offiziellen Zugang (Entscheidung 11.11.) | `BILD_GESPERRT`, `BILD_GESPERRT_MARKEN` |
| Kinoplakate und Filmbilder ohne Freigabe des Verleihs auf Social und außerhalb eines Berichts über den Film | Rechte beim Verleih | Umfang `presse-redaktionell` = nur Website (fehlt noch, 6.2) |
| Logos, Banner, Wappen als Beitragsbild | Marken- und Namensrechte | Seitenverhältnis-Prüfung (`bildvorschlag.py` `_bild_lesen`, streng) |
| Commons-Dateien mit NC, ND, „Fair use“, NonFree, unbekanntem Urheber | nicht frei für eine werbefinanzierte Seite | `commons_lizenz` |
| Bilder von Bild-CDNs fremder Betreiber und geteilten Hostern | Herkunft nicht prüfbar | `GETEILTE_HOSTER`, Host-Prüfung |
| Fotos von der alten tamil.de für neue Beiträge | Rechte unbekannt (2.1) | Regel; kein Code |
| KI-Bilder als Ereignisfoto, mit erkennbaren realen Personen oder „im Stil von“ Personen | Täuschung, Persönlichkeitsrecht | Prompt-Regeln (4.6), Kennzeichnung (4.8) |
| Unsplash-Bilder über die API ohne Hotlink | API-Richtlinie | Festlegung 2.4; Code fehlt (6.2) |
| Fotos von Personen aus Einsendungen ohne Einwilligung | Datenschutz, Recht am eigenen Bild | Baustein 2 (F1), Einwilligung mit Fassung |

## 3. Lizenz-Datensatz je Bild

### 3.1 Felder

Gespeichert in der Tabelle `assets` (`news_radar/workflow/schema.py`); fehlende Spalten kommen mit einer neuen
Migration dazu (bestehende Migrationen werden nicht geändert).

| Feld | Pflicht | Inhalt | Beispiel | heute in `assets` |
|---|---|---|---|---|
| `datei`, `sha256` | ja | Dateiname der Master-Datei, Prüfsumme | `ab12-e41-9f3c2d1a.jpg` | ja |
| `herkunft` | ja | `archiv`, `register`, `commons`, `stock`, `ki`, `pool`, `karte`, `upload` | `commons` | ja (`quelle` statt `register`) |
| `urheber` | ja bei CC BY/BY-SA, Stock, Archiv | Fotografin oder Fotograf | `Max Muster` | nein (steckt in `rechteinhaber`) |
| `rechteinhaber` | ja | wer die Rechte hält | `Max Muster` / `Verleih (über CineStar)` | ja |
| `lizenz_kuerzel` | ja | aus der Positivliste 3.2 | `cc-by-sa-4.0` | nein (Freitext in `lizenz`) |
| `lizenz_url` | ja bei CC, Stock | Adresse des Lizenztexts | `https://creativecommons.org/licenses/by-sa/4.0/` | nein (in `lizenz` eingebettet) |
| `umfang` | ja | Menge aus `website`, `social`, `print` | `website,social` | Freitext |
| `nachweis` | ja | Bildunterschrift nach Muster 3.5 | `Foto: Max Muster / Wikimedia Commons, CC BY-SA 4.0, zugeschnitten` | ja (`attribution`) |
| `ablauf` | nein | Ende des Nutzungsrechts (JJJJ-MM-TT), leer = unbefristet | `2027-12-31` | ja |
| `quelle_url` | ja außer KI, Karte, eigenes Foto | Seite, auf der das Bild steht (Dateiseite, Beleg der Story) | Commons-Dateiseite | ja |
| `bild_url` | ja außer KI, Karte, Upload | Adresse der abgerufenen Bilddatei | `https://upload.wikimedia.org/…` | nein (nur als Hash im Protokoll) |
| `bearbeitung` | ja | `keine`, `zugeschnitten`, `eingepasst`, `Logo-Leiste`, `KI-Hinweis` | `zugeschnitten` | nein |
| `beleg` | ja | wie die Lizenz geprüft wurde: Commons-API-Abruf mit Zeitpunkt, Register-Fassung (Hash von `sources.toml`), Lizenzseite mit Abrufdatum, abgelegte Erlaubnis (Datei unter `data/belege/`, nicht öffentlich) | `commons-api 2026-11-13T19:02Z` | nein |
| `geprueft_von`, `geprueft_am` | ja | `dienst`, `agent:<name>` oder Benutzername; Zeitpunkt | `agent:redakteur`, `2026-11-13T19:02Z` | nur `erstellt` |
| `ki`, `ki_modell`, `prompt_hash` | ja bei KI | Kennzeichen, Modell-ID, Hash des endgültigen Prompts | `1`, `gemini-nano-banana-2.1` | nur `ki` |
| `alt` | ja | Alt-Text (5.5) | `Gopuram eines Tempels vor bewölktem Himmel` | nein (am Entwurf `bild_alt`) |
| `fokus` | nein | Bildmitte für Zuschnitte in Prozent (x, y) | `50,35` | nein |
| `story_id`, `draft_id`, `erstellt` | ja | Zuordnung | – | ja |

**Vollständig** ist ein Datensatz, wenn alle Pflichtfelder gesetzt sind, das Kürzel in der Positivliste steht, der
Ablauf nicht überschritten ist und bei Lizenzen mit Namensnennung `urheber` gesetzt ist.

### 3.2 Positivliste der Lizenz-Kürzel

| Kürzel | Bedeutung | Höchster Umfang | Namensnennung |
|---|---|---|---|
| `eigen` | eigenes Werk von Tamil.de oder KBS (Foto der Redaktion) | Website, Social, Print | „Foto: Tamil.de / Name“ |
| `nutzungsrecht` | schriftliche Erlaubnis des Rechteinhabers (Mail, Vertrag, Formular); Beleg Pflicht | laut Erlaubnis | wie vereinbart |
| `presse-redaktionell` | Material einer Register-Quelle oder eines Verleihs ohne ausdrückliche Lizenz | nur Website, nur im Bericht über Einrichtung, Ereignis oder Film | wörtlich aus dem Register |
| `cc-by-<version>` | Creative Commons Namensnennung | Website, Social, Print | Pflicht, mit Lizenz-Link und Änderungshinweis |
| `cc-by-sa-<version>` | Creative Commons Namensnennung, Weitergabe unter gleichen Bedingungen | Website, Social (ohne Logo/Text im Bild), Print | Pflicht, wie CC BY |
| `cc0-1.0`, `pdm-1.0` | gemeinfrei mit Lizenz-Adresse | Website, Social, Print | Hausregel: Urheber nennen, wenn bekannt |
| `pexels` | Pexels-Lizenz | Website, Social | Hausregel und API-Pflicht: „Foto: Name / Pexels“ mit Link |
| `unsplash` | Unsplash-Lizenz (nur von Hand) | Website, Social | Hausregel: „Foto: Name / Unsplash“ mit Link |
| `ki-symbolbild` | mit Gemini erzeugt, Nutzungsbedingungen von Google | Website, Social | „Symbolbild: KI-generiert · Tamil.de“ |
| `tamil-grafik` | Bildkarte | Website, Social, Print | „Grafik: Tamil.de“ |

### 3.3 Gate (wann geprüft wird, was dann passiert)

| Prüfung | Wann | Ergebnis bei Fehlen |
|---|---|---|
| Datensatz vollständig, Umfang enthält `website` | Freigabe, Sammelfreigabe im Cockpit | Freigabe gesperrt; im Entwurf steht „Lizenz fehlt: <Feld>“ mit dem Knopf „Lizenz eintragen“ |
| dasselbe, erneut | unmittelbar vor dem Senden an WordPress (`publisher.py`) | nicht gesendet, Fehler „Lizenz unvollständig“ im Cockpit, Protokollzeile |
| Umfang enthält `social` | Regelprüfung für Instagram, Facebook, WhatsApp-Entwurf (F4) | automatisch die Bildkarte für Social; der Grund steht in der Historie |
| `ablauf` in 14 Tagen | täglicher Lauf | Liste „Lizenz läuft ab“ im Cockpit |
| `ablauf` erreicht | täglicher Lauf | Vorschlag (braucht ein Ja als Regel, §8 Abs. 1): der Dienst tauscht das Beitragsbild auf der Website gegen die Bildkarte und protokolliert; bis zum Ja nur Hinweis an die Redaktion |
| Bildwechsel nach Freigabe | jede Änderung | Freigabe veraltet (schon gebaut: Zähler `stand`, Entscheidung 11.11.) |

### 3.4 Manuelle Eingabe im Cockpit

Entsteht kein Lizenz-Datensatz automatisch (eigenes Foto, Foto eines Veranstalters per Mail, Unsplash von Hand,
Einsendung, Archivbild ohne Eintrag), trägt die Redaktion ihn ein. Formular „Lizenz eintragen“ am Entwurf (Bereich
„Bild“), Rollen `redaktion` und `admin`:

| Feld im Formular | Eingabe | Prüfung |
|---|---|---|
| Herkunft | Auswahl: eigenes Foto · Foto von Dritten mit Erlaubnis · Archiv · Register-Quelle · Wikimedia Commons · Pexels · Unsplash · Pressematerial (Verleih/Veranstalter) | Pflicht |
| Urheber, Rechteinhaber | Text | Pflicht je nach Lizenz (3.2); kein „unbekannt“ bei Namensnennung |
| Lizenz | Auswahl aus der Positivliste 3.2; Version bei CC | Pflicht; bei CC und Stock wird die Lizenz-Adresse automatisch gesetzt |
| Umfang | Häkchen Website · Social · Print | Pflicht; höchstens der Umfang aus 3.2 |
| Quelle | Adresse der Seite oder „eigenes Foto“ | Pflicht außer bei eigenem Foto |
| Beleg | Datei (PDF, PNG, JPEG, höchstens 5 MB) oder Text, z. B. „Mail von … vom …“ | Pflicht bei `nutzungsrecht`; abgelegt unter `data/belege/`, nicht öffentlich |
| Ablauf | Datum oder leer | Datum in der Zukunft |
| Alt-Text | Text, 5 bis 160 Zeichen | Pflicht, nicht gleich dem Titel |
| Nachweis | wird nach Muster 3.5 vorgeschlagen, änderbar | Pflicht |

Hochladen ohne Lizenz bleibt möglich, um weiterzuarbeiten; die Freigabe bleibt gesperrt, bis der Datensatz vollständig
ist. Ein Standardnachweis „Foto: Tamil.de“ wird **nicht** mehr gesetzt. Jede Eingabe schreibt eine Protokollzeile
(wer, wann, Entwurf, Lizenz-Kürzel; keine Personendaten aus dem Beleg).

### 3.5 Muster für den Nachweis

| Lizenz | Bildunterschrift Website | Links auf der Website | Text im Social-Beitrag |
|---|---|---|---|
| `eigen` | Foto: Tamil.de / Name | – | Foto: Tamil.de |
| `nutzungsrecht` | Foto: Name (oder wie vereinbart) | – | wie vereinbart |
| `presse-redaktionell`, Einrichtung | Foto: Sri Ganesha Hindu Tempel Berlin (wörtlich aus dem Register) | „Bildquelle“ auf die Seite | kein Social ohne Erlaubnis |
| `presse-redaktionell`, Film | Filmplakat: Verleih X (via CineStar) | – | kein Social ohne Freigabe des Verleihs |
| `cc-by-4.0` | Foto: Max Muster / Wikimedia Commons, CC BY 4.0, zugeschnitten | Name → Dateiseite, „CC BY 4.0“ → Lizenz | Foto: Max Muster / Wikimedia Commons, CC BY 4.0 (Nachweis mit Links auf tamil.de) |
| `cc-by-sa-4.0` | Foto: Max Muster / Wikimedia Commons, CC BY-SA 4.0, zugeschnitten | wie CC BY | wie CC BY; Bild ohne Logo-Leiste |
| `cc0-1.0`, `pdm-1.0` | Foto: Max Muster / Wikimedia Commons, gemeinfrei | Dateiseite | Foto: Max Muster / Wikimedia Commons |
| `pexels` | Symbolfoto: Name / Pexels | Name → Fotoseite, „Pexels“ → pexels.com | Symbolfoto: Name / Pexels |
| `unsplash` | Symbolfoto: Name / Unsplash | Name → Profil, „Unsplash“ → unsplash.com | Symbolfoto: Name / Unsplash |
| `ki-symbolbild` | Symbolbild: KI-generiert · Tamil.de | – | KI-Symbolbild · Tamil.de |
| `tamil-grafik` | Grafik: Tamil.de | – | – |

Bei Stockfotos außerhalb von Nachrichten (Küche, Kultur) kann „Symbolfoto“ zu „Foto“ werden. Der Instagram-Text kann
keine Links anklicken lassen; deshalb steht die vollständige Namensnennung mit Links im Artikel auf tamil.de, auf den
der Beitrag verweist.

## 4. Bildgenerierung (KI-Symbolbild)

### 4.1 Stand der Entscheidung

Der Blueprint vom 20.10. sah KI in der Bildkette vor. Seit dem Pilot (09.11.) und der Bildentscheidung vom 11.11.
gilt „keine KI-Bilder“. Diese Spezifikation legt fest, **wie** KI-Bilder entstehen, wenn Luis sie wieder freigibt.
Eingeschaltet wird die Stufe nur mit einem neuen Eintrag im Entscheidungslog **und** einer Freigabe der laufenden
Kosten durch KBS (§3 Abs. 2) **und** dem Schlüssel `GEMINI_API_KEY`. Bis dahin endet die Kette nach Stock bei der
Bildkarte, und der Bildpool wird nicht benutzt.

### 4.2 Wann ein KI-Bild entsteht

Alle Bedingungen müssen erfüllt sein:

1. KI-Bilder sind freigegeben (4.1).
2. Die Stufen 1 bis 4 haben kein Bild mit vollständiger Lizenz geliefert.
3. Das Thema eignet sich: **keine KI-Bilder bei heiklen Themen** (Politik, Justiz, Unglück, Tod, Nachruf, Medizin,
   Gedenken; dieselbe Liste wie im F4-Regelwerk), nicht bei Berichten über eine bestimmte Person. Dort die Bildkarte.
4. Im Bildpool des Themas liegt kein gesichtetes Bild unter der Nutzungsgrenze (4.9); sonst wird das Pool-Bild genommen.
5. Höchstens ein neues KI-Bild je Story (`RADAR_KI_BILDER_JE_ARTIKEL=1`) und höchstens zehn je Tag (neue Grenze,
   Vorschlag `RADAR_KI_BILDER_TAG`).
6. Das Budget reicht; die Kosten werden vor dem Aufruf reserviert (4.4).
7. Der Stopp-Schalter „redaktion“ (oder „alles“) steht nicht auf Halt; er wird unmittelbar vor dem Aufruf geprüft.

Die Redaktion kann im Cockpit „Neu generieren“ wählen; dann gelten 1, 3, 5, 6 und 7 genauso.

### 4.3 Modell, Schnittstelle, Kosten

| Punkt | Festlegung |
|---|---|
| Modell | `gemini-nano-banana-2.1` (Nano Banana 2.1), laut Google das empfohlene Bildmodell; Variable `BILD_MODELL` |
| Schnittstelle | Interactions-API: `POST https://generativelanguage.googleapis.com/v1beta/interactions`, Kopfzeile `x-goog-api-key`, `store: false`, `response_format` Typ `image` (siehe `integrationen.md`) |
| Format | **4:3 in 2K (2400 × 1792 px)**, statt heute 16:9 in 1K (1376 × 768); daraus entstehen alle Zuschnitte (5.1). Großschreibung der Größe ist Pflicht (`2K`) |
| Wasserzeichen | Google versieht alle erzeugten Bilder mit SynthID (unsichtbar) |

Preise laut offizieller Preisseite der Gemini-API (ai.google.dev, weitergeleitet auf aistudio.google.com/docs/pricing),
Abruf 13.11.2026, je erzeugtem Bild:

| Modell | 1K | 2K | 4K | Batch | Kostenlose Stufe |
|---|---|---|---|---|---|
| `gemini-nano-banana-2.1` | 0,0336 $ | 0,0504 $ | 0,113 $ | halber Preis | keine Bilderzeugung |
| `gemini-3.1-flash-lite-image` | 0,0336 $ | – | – | halber Preis | keine |
| `gemini-3.1-flash-image` | 0,067 $ | 0,101 $ | 0,151 $ | – | keine |
| `gemini-3-pro-image` | 0,134 $ | 0,134 $ | 0,24 $ | – | keine |

In der bezahlten Stufe werden die Daten laut derselben Seite nicht zur Verbesserung der Produkte genutzt. Die Tabelle in
`news_radar/workflow/costs.py` (`BILD_PREISE`, geprüft 08.11.2026) stimmt mit diesen Werten überein.

Rechenbeispiel (2K): fünf Entwürfe am Tag (Pilot), jeder mit neuem KI-Bild = 0,25 $ am Tag, rund 7,60 $ im Monat. Den
Bildpool einmal füllen (30 Themen × 3 Bilder) = 4,54 $. In der Praxis weniger, weil Archiv, Register, Commons, Stock und
Pool vorher greifen.

### 4.4 Budgetregel

- Jeder Aufruf reserviert vorher den Preis des Bildes im gemeinsamen Budget (`costs.bild_kosten`, `budget.reservieren`);
  ist Tag oder Monat erschöpft, gibt es kein KI-Bild, die Kette geht zur Bildkarte. Gilt für die Bildkette, das Füllen
  des Pools **und** den Knopf im Cockpit (dort fehlt es heute, 6.2).
- Jeder Aufruf steht in `agent_usage` (Rolle `bild` oder `bildpool`, Anbieter `gemini`, Bilder, Kosten, Status).
- Ein fehlgeschlagener Aufruf wird einmal wiederholt (nur bei Netzfehler, 429 oder 5xx), dann nicht mehr.
- Grenzen: Tagesbudget `RADAR_BUDGET_TAG_USD`, Monatsbudget `RADAR_BUDGET_MONAT_USD` (gemeinsam mit den Modellkosten),
  je Story `RADAR_KI_BILDER_JE_ARTIKEL`, je Tag `RADAR_KI_BILDER_TAG` (neu).

### 4.5 Stil je Rubrik

Hausstil für alle: editoriale Fotografie, natürliches Licht, echte Räume der tamilischen Diaspora in Deutschland,
Österreich und der Schweiz, Augenhöhe, ruhiger Hintergrund, Hauptmotiv im linken Drittel, Platz für Text unten links;
warme, aber natürliche Farben (Kumkum-Rot, Ringelblumen-Gelb, Indigo als Akzente in Blumen, Stoffen, Licht), kein
Filter, kein HDR, keine Neonfarben, keine Ränder oder Collagen.

| Rubrik | Motive | Nicht |
|---|---|---|
| Community | Vereinsheim, Gemeindesaal, Schulraum, Tempel von außen, Lampen, Blumengirlanden, Hände | Gesichter im Fokus, Kinder im Fokus |
| Kultur | Kolam, Pongal-Topf, Instrumente, Bühne mit Silhouette, Bücher | Gottheiten, religiöse Zeichen als Schmuck |
| Kino | leerer Kinosaal, Leinwandlicht, Foyer mit leeren Plakatrahmen | echte Plakate, Schauspieler, Szenen aus Filmen |
| Entertainment | Konzerthalle von hinten, Bühnenlicht, Studio ohne Personen | erkennbare Künstler, Bildschirme mit Text |
| Events | Halle vor dem Einlass, Stuhlreihen, Licht, Publikum von hinten | Brautpaare, Ehrengäste |
| Küche | Gericht auf Bananenblatt, Zutaten, Dampf, Draufsicht | Markenverpackungen |
| Sport | Spielfeld, Ball, Schläger, Bewegungsunschärfe | Vereinslogos, Trikots mit Schrift, erkennbare Spieler |
| Nachrichten (nicht heikel) | Orte, Gebäude, Landschaft, Bahnhof, Straße ohne Schilder | Personen im Fokus, Behördenschilder, Flaggen; heikle Themen bekommen die Bildkarte |

### 4.6 Prompt-Vorlage (verbessert)

Der Writer liefert `bild_prompt` (Englisch, 30 bis 60 Wörter, nur das Motiv) und `bild_thema` (Slug aus
`prompts/bildpool.md`). Der Radar setzt den endgültigen Prompt zusammen; die Version ist der Hash des Inhalts. Fassung
für `news_radar/prompts/bild.md`:

```
Editorial photograph for a German-language community magazine of the Tamil diaspora in Germany, Austria and
Switzerland.
Scene: {motiv}
Style: natural light, candid documentary feel, 35-50mm lens look, eye level, calm uncluttered background, main subject
in the left third, empty area in the lower left for a caption, warm but realistic colours (kumkum red, marigold
yellow, deep indigo only as accents in flowers, fabrics or light), no filter, no HDR, no neon.
Strict rules: this is a symbolic image, not a depiction of a real event. No text, letters, numbers, signs, posters
with writing, logos, brand names, watermarks or flags. No real, famous or recognizable people and nobody "in the
style of" a real person. People only anonymous: from behind, cropped at the shoulders, as small figures in a crowd or
out of focus; no faces in focus. No children in focus. No deities, idols or religious symbols as decoration; temple
architecture only as a place. No political symbols, no tiger imagery, no military, uniforms, weapons, violence,
injuries, protests or courtrooms. No borders, frames or collage.
Format: landscape 4:3.
```

`{motiv}` ist `bild_prompt`; fehlt es, das Motiv des Themas aus `bildpool.md`. Gegenüber der heutigen Fassung neu:
Region DACH, Platz für Text, „Symbolbild“ im Prompt, Zahlen und Schilder, „im Stil von“, Kinder, religiöse Zeichen,
politische Symbole (Tiger, Militär; vgl. Gedenk-Sperre vom 12.11.), Format 4:3.

### 4.7 Ausschlüsse (immer)

Keine Personen mit Gesicht im Fokus, keine erkennbaren oder bekannten Personen, keine Kinder im Fokus, keine Logos,
Marken, Schriftzüge, Flaggen, keine Gottheiten und religiösen Symbole als Deko, keine politischen Symbole, keine
Gewalt, Waffen, Verletzten, Unfälle, Proteste oder Gerichtsszenen, keine Nachstellung eines konkreten Ereignisses.
Ein KI-Bild, das gegen eine Regel verstößt, wird verworfen (Cockpit „Bild ersetzen“), nicht nachbearbeitet.

### 4.8 Kennzeichnung

| Wo | Wie | Stand |
|---|---|---|
| Website, Beitrag | Bildunterschrift „Symbolbild: KI-generiert · Tamil.de“ | gebaut (`bilder.KI_CREDIT`, Theme `tamil_bildnachweis`) |
| Website, Anreißer-Karten | kleines Etikett „KI-Symbolbild“ auf dem Bild | fehlt |
| Instagram, Facebook | Hinweis „KI-Symbolbild“ unten links ins Bild eingebrannt und im Text | fehlt (Baustein 5; F4-Regel „Kennzeichnung“) |
| WhatsApp-Entwurf | wie Instagram | fehlt |
| Datei | IPTC/XMP `DigitalSourceType` = `trainedAlgorithmicMedia`, Credit „Tamil.de (KI-generiert)“; dazu SynthID von Google | fehlt (`images._encode` entfernt alle Metadaten) |
| Datenbank, WordPress | `assets.ki = 1`, `ki_modell`, `prompt_hash`; Meta `bild_origin = ki` bzw. `pool` | teilweise |
| Cockpit | Etikett „KI-Symbolbild“ | gebaut (`entwurf.html`) |

Rechtlicher Rahmen (Einordnung, keine Rechtsberatung; verantwortlich für Inhalte ist KBS, §8 Abs. 3): Pressekodex
Richtlinie 2.2 (Symbolfotos klarstellen) und die Transparenzpflichten nach Art. 50 der KI-Verordnung. Tamil.de
kennzeichnet KI-Bilder immer, unabhängig davon, ob eine Pflicht im Einzelfall greift.

### 4.9 Bildpool

- Reserve aus KI-Symbolbildern je Thema (`data/bildpool/<thema>/`, Index `pool.json`; Themen in `prompts/bildpool.md`).
- Gefüllt wird nur von Hand durch `admin` (`python -m news_radar bildpool fuellen`), drei Bilder je Thema, mit
  Budgetreservierung (gebaut).
- **Neu:** Jedes Pool-Bild wird vor der ersten Nutzung im Cockpit gesichtet (übernehmen oder verwerfen); ungesichtete
  Bilder nimmt die Kette nicht.
- **Neu:** Nutzungsgrenze fünf Einsätze je Bild und nie zweimal am selben Tag; danach wird für das Thema ein neues Bild
  erzeugt (mit Budget) oder die Bildkarte genommen.
- Pool-Bilder sind KI-Bilder: gleiche Kennzeichnung, eigener Lizenz-Datensatz je Einsatz (`herkunft = pool`, `ki = 1`).

Vorgeschlagene Änderungen an `prompts/bildpool.md`:

| Thema | Problem | Vorschlag |
|---|---|---|
| `politik-sri-lanka` | Politik ist heikel, Flaggenmasten und Parlament wirken politisch | streichen; Politik bekommt die Bildkarte |
| `hochzeit` | Brautpaar im Bild | „Decorated Tamil wedding hall before the guests arrive, flowers and brass lamps, no people“ |
| `tamil-sprache` | Kinderhand im Fokus (Regel: keine Kinder im Fokus) | „Adult hand writing Tamil letters in an exercise book, letters not readable“ |
| `tamilschule` | in Ordnung, aber Klassenraum mit Kindern naheliegend | Zusatz „no children“ |
| alle | Format 16:9 | Format 4:3 (4.3) |

## 5. Formate und Zuschnitt

### 5.1 Master

- Nach der Lizenzprüfung wird das Bild als **Master** gespeichert: Originalverhältnis, lange Kante höchstens 2400 px,
  JPEG, sRGB, Qualität 88, Ausrichtung aus EXIF angewendet, alle anderen EXIF-Daten entfernt (Ortsdaten), bei KI-Bildern
  die Kennzeichnung in den Metadaten (4.8).
- Mindestgröße: kurze Kante 1080 px (sonst kein Social-Format ohne Hochrechnen; auf der Website erlaubt ab 800 px Breite,
  wie heute in `bildvorschlag.py`).
- Alle Zuschnitte entstehen aus dem Master, nicht auseinander. Heute wird jedes Bild sofort auf 1200 × 675 beschnitten
  (`images.SIZE`); das reicht weder für das Aufmacherbild noch für Instagram (6.2).
- Fokuspunkt: Standard Mitte; die Redaktion kann ihn im Cockpit setzen (Klick ins Bild).

### 5.2 Website

WordPress erzeugt die Größen aus dem hochgeladenen Master (`wordpress/themes/tamil/inc/setup.php`,
`wordpress/plugins/tamil-site/includes/seo.php`):

| Größe | Maße | Verhältnis | Wofür |
|---|---|---|---|
| `tamil-lead` | 1600 × 1000 | 16:10 | Aufmacher und Artikelkopf |
| `tamil-card` | 960 × 720 | 4:3 | Kacheln |
| `tamil-zeile` | 480 × 480 | 1:1 | Listen |
| `tamil-og` | 1200 × 630 | 1,91:1 | Vorschau in sozialen Netzen und WhatsApp-Link |
| `full` | Master | Original | Rückfall |

- Ausgabe: JPEG als Original; zusätzlich WebP für die Unterformate (WordPress-Filter `image_editor_output_format` im
  Plugin `tamil-site`), Rückfall JPEG. Ladeart wie heute (Aufmacher `eager`, sonst `lazy`).
- WordPress vergrößert beim Beschneiden nicht: Ist der Master kleiner als 1600 px breit, fehlt `tamil-lead`.

### 5.3 Social

| Kanal | Datei | Grenzen laut Meta | Festlegung |
|---|---|---|---|
| Instagram (Bildbeitrag) | 1080 × 1350, 4:5, JPEG, sRGB | nur JPEG; höchstens 8 MB; Verhältnis 4:5 bis 1,91:1; Breite 320 bis 1440 px; Text höchstens 2200 Zeichen, 30 Hashtags, 20 Erwähnungen; Alt-Text bis 1000 Zeichen (developers.facebook.com, Abruf 13.11.2026) | Foto mit kleiner Logo-Leiste unten (Vorschlag F4, offen); bei CC BY-SA ohne Leiste; KI-Hinweis eingebrannt |
| Facebook-Seite (Fotobeitrag) | dieselbe Datei | JPEG, PNG u. a.; höchstens 10 MB (Graph-API-Referenz Page Photos) | dieselbe Datei wie Instagram, damit beide gleich aussehen |
| WhatsApp-Kanal (von Hand) | dieselbe Datei zum Herunterladen | keine Schnittstelle | Link im Text erzeugt zusätzlich die Vorschau aus `tamil-og` |

Die Social-Datei wird als eigenes Medium in die WordPress-Mediathek geladen (öffentliche JPEG-Adresse, die Meta beim
Veröffentlichen abruft) und bekommt einen eigenen Lizenz-Datensatz mit `bearbeitung` (z. B. `zugeschnitten, Logo-Leiste`).

### 5.4 Zuschnitt-Regeln

| Regel | Gilt für |
|---|---|
| Zuschnitt um den Fokuspunkt; Gesichter, Hände und Hauptmotiv nie anschneiden | alle Fotos |
| **Plakate, Flyer, Grafiken mit Text werden nie beschnitten**, sondern eingepasst (Fläche in Sand-Farbe drumherum) | Kinoplakate, Veranstaltungsplakate |
| Kein Spiegeln, kein Verzerren, keine Farbfilter | alle |
| CC BY-SA: nur Zuschnitt, nichts dazu | Social |
| Bildkarte wird für jedes Format neu gezeichnet, nicht beschnitten | Bildkarte |
| Wäre das Bild nach dem Zuschnitt schmaler als das Ziel, wird nicht hochgerechnet: Website nimmt `full`, Social nimmt die Bildkarte | alle |

### 5.5 Alt-Text

- Pflicht für jedes Bild; 5 bis 160 Zeichen auf der Website (wie `ALT_MAX` in `bildvorschlag.py`), auf Instagram und
  Facebook derselbe Text (`alt_text`, `alt_text_custom`).
- Beschreibt, was zu sehen ist, nicht die Schlagzeile. Kein „Bild von“. Plakate: „Filmplakat zu <Titel>“. KI-Bilder
  beginnen mit „Symbolbild:“. Bildkarte: „Grafik mit der Überschrift: <Titel>“.
- Kein automatischer Rückgriff auf den Titel (heute `publisher.py` `bild_payload`); fehlt der Alt-Text, bleibt die
  Freigabe gesperrt.

## 6. Abgleich mit dem Code (Stand 13.11.2026)

### 6.1 Gebaut

| Was | Wo |
|---|---|
| Commons-Weg mit fester Positivliste, Lizenz-Adresse Pflicht, NonFree, Urheber Pflicht, Mindestbreite 800 px | `news_radar/bildvorschlag.py` (`commons_lizenz`, `_commons`, `urhebername`) |
| Register-Weg: Host im Register, Seite ist Beleg der Story, Bild beim eingetragenen Host, Agentur-Erkennung, Verleih als Rechteinhaber bei Kino und Festival | `bildvorschlag.py` (`_quelle`, `AGENTUR`), `news_radar/config.py` (`Bildquelle`, `BILD_GESPERRT`), `sources.toml` (`[[bildquellen]]`, 28 Einträge) |
| Lizenz-Datensatz `assets`, beim Agent-Weg in einer Transaktion mit dem Entwurf | `news_radar/workflow/schema.py` (Tabelle `assets`), `bildvorschlag.py` `_setzen`, `agents/media.py` `speichern` |
| Bildkette mit einstellbarer Reihenfolge, Stopp-Schalter vor jedem Aufruf nach außen, Bildkarte als sicherer Rückfall | `agents/media.py` `besorgen`, `config.py` `BILD_REIHENFOLGE` |
| Archiv mit Pflichtangaben und Ablauf | `agents/media.py` `_archiv`, `archiv_vorlage` |
| KI über Gemini mit Budgetreservierung, Grenze je Story, Kostenprotokoll; Bildpool mit Nutzungszähler | `news_radar/bilder.py`, `agents/media.py` `_ki`, `workflow/costs.py` (`BILD_PREISE`) |
| Freigabe nur für den gesehenen Stand (Bildwechsel macht Freigabe ungültig) | Migration 6, Entscheidung 11.11. |
| Cockpit zeigt Lizenz, Rechteinhaber, Ablauf, KI-Etikett, „Bildquelle öffnen“ | `news_radar/web/templates/entwurf.html` (Bereich „Bild“) |
| Nachweis nach WordPress: Bildunterschrift des Anhangs, Meta `bild_credit`, `bild_origin`; KI-Hinweis im Theme; Spalte „KI-Symbolbild“ im Backend | `news_radar/publisher.py` (`bild_payload`, `META_FIELDS`), `wordpress/plugins/tamil-radar/includes/media.php`, `includes/admin.php`, `wordpress/themes/tamil/inc/template-tags.php` (`tamil_bildnachweis`) |

### 6.2 Fehlt

| Nr. | Lücke | Datei | Was zu tun ist |
|---|---|---|---|
| L1 | Der Bilddialog im Cockpit (Upload, Stock, KI, Pool, Karte) legt keinen Lizenz-Datensatz an | `news_radar/web/views.py` `bild()` | jeden Weg über einen gemeinsamen Speicherweg mit Datensatz führen |
| L2 | Upload: Nachweis freiwillig, Standard „Foto: Tamil.de“ (falsche Rechteangabe) | `views.py` `bild()`, `news_radar/images.py` `from_upload` | Standard streichen; Formular 3.4 |
| L3 | Kein Formular „Lizenz eintragen“ | `news_radar/web/templates/entwurf.html`, `views.py` | Formular und Prüfung nach 3.4 |
| L4 | Kein Lizenz-Gate bei Freigabe und Veröffentlichen | `views.py` (Freigabe, Sammelfreigabe), `publisher.py` `publish_draft` | Prüfung nach 3.3 |
| L5 | `assets` ohne `lizenz_kuerzel`, `lizenz_url`, `urheber`, `bild_url`, `bearbeitung`, `beleg`, `geprueft_von/_am`, `ki_modell`, `prompt_hash`, `alt`, `fokus`; `umfang` nur Freitext | `workflow/schema.py`, `workflow/repo.py` `asset_anlegen` | neue Migration V8; Umfang als Menge |
| L6 | Umfang immer „Online-Veröffentlichung auf tamil.de“, auch bei CC BY, Pexels, Karte; Social damit nie erlaubt | `bildvorschlag.py` `UMFANG`, `agents/media.py` `Bild.umfang` | Umfang je Kürzel nach 3.2 setzen |
| L7 | Commons und Register fehlen in der automatischen Kette (nur über den Agent-Weg) | `agents/media.py` `besorgen`, `config.py` `BILD_REIHENFOLGE` | Stufen `register`, `commons` aufnehmen |
| L8 | Zwei Register: `bild_nutzen` an `[[sources]]` (Stufe „quelle“, ohne Host- und Agentur-Prüfung) und `[[bildquellen]]` | `agents/media.py` `_quelle`, `config.py` `Source.bild_nutzen` | auf `[[bildquellen]]` vereinheitlichen; Feld `erlaubnis` (Datum, Umfang, Beleg) ergänzen |
| L9 | Unsplash über die API wird heruntergeladen und neu gespeichert (API verlangt Hotlink), Nachweis ohne Links und UTM | `images.py` `from_unsplash`, `featured_image` | Unsplash aus der automatischen Kette nehmen (2.4) |
| L10 | Pexels-Nachweis ohne Link auf Foto und Pexels; Lizenz „Pexels License“ ohne Adresse; keine Prüfung auf Personen | `images.py` `from_pexels`, `agents/media.py` `_stock` | Fotoseite und Lizenz-Adresse speichern, Nachweis nach 3.5, in Nachrichten nur ohne Personen (Stichwortfilter oder Sichtung) |
| L11 | KI-Stufe hängt nur am fehlenden Schlüssel; Standard `BILD_MODUS=ki`, Pool in der Kette: liegt ein gefüllter Pool vor, entstehen KI-Bilder trotz Entscheidung „keine KI-Bilder“ | `config.py` (`bild_modus`, `BILD_REIHENFOLGE`), `bilder.py` `beitragsbild`, `agents/media.py` | eigener Schalter (Vorschlag `BILD_KI_FREIGABE`, Standard aus) für `pool` und `ki` |
| L12 | Knopf „Neu generieren“ im Cockpit ohne Budgetreservierung und ohne Eintrag in `agent_usage` | `views.py` `bild()` (Aktion `ki`) | wie `agents/media.py` `_ki` |
| L13 | KI-Bild 16:9 in 1K, sofort auf 1200 × 675 | `bilder.py` `gemini_request`, `from_gemini` | 4:3 in 2K, Master nach 5.1 |
| L14 | Master fehlt: alle Wege schneiden sofort auf 1200 × 675; kein Fokuspunkt; `tamil-lead` (1600 px) entsteht so nie | `images.py` (`SIZE`, `from_upload`, `_encode`), `bildvorschlag.py` `_setzen` | Master speichern, Zuschnitte daraus |
| L15 | Kein Social-Format, keine Logo-Leiste, kein eingebrannter KI-Hinweis | fehlt (Baustein 5) | Erzeugung 1080 × 1350 nach 5.3 |
| L16 | Alt-Text: Rückfall auf den Titel, keine Pflicht | `publisher.py` `bild_payload` | Pflicht nach 5.5 |
| L17 | Keine KI-Kennzeichnung in den Metadaten der Datei | `images.py` `_encode`, `bilder.py` | IPTC/XMP `DigitalSourceType` schreiben |
| L18 | Theme kennzeichnet nur `bild_origin = ki`, nicht `pool`, und prüft per Textsuche nach „ki“ (trifft auch „Kino“, „Nikita“); Anreißer ohne Etikett | `wordpress/themes/tamil/inc/template-tags.php` `tamil_bildnachweis` | nach Herkunft `ki` oder `pool` entscheiden; Etikett auf Karten |
| L19 | Lizenz und Links gehen nicht nach WordPress (nur der Nachweistext); Theme kann Urheber und Lizenz nicht verlinken | `publisher.py` `META_FIELDS`, `wordpress/plugins/tamil-radar/includes/meta.php` | Meta `bild_lizenz`, `bild_lizenz_url`, `bild_quelle_url` |
| L20 | Commons-Vorschau in 1600 px; Wikimedia liefert nur Standardbreiten (…, 960, 1280, 1920, 3840) zuverlässig aus; 429 mit `Retry-After` wird nicht beachtet | `bildvorschlag.py` `commons_api_url` (`iiurlwidth`), `_abrufen` | 1920 px; `Retry-After` beachten (`integrationen.md`) |
| L21 | Ablauf wird nur beim Archiv geprüft; keine Liste „läuft ab“, kein Tausch nach Ablauf | fehlt | täglicher Lauf nach 3.3 |
| L22 | Pool-Bilder ohne Sichtung, ohne Nutzungsgrenze | `bilder.py` `BildPool` | Sichtung und Grenze nach 4.9 |
| L23 | Plakate werden wie Fotos beschnitten | `bildvorschlag.py` `_setzen`, `images.py` | Einpassen nach 5.4 |
| L24 | `bildpool.md` und `bild.md` widersprechen den Regeln (Politik-Thema, Brautpaar, Kinderhand, 16:9) | `news_radar/prompts/bildpool.md`, `prompts/bild.md` | Fassung 4.6 und Tabelle 4.9 |

### 6.3 Offen für Luis

1. KI-Symbolbilder wieder zulassen (4.1)? Wenn ja: mit Tagesgrenze zehn und 2K? Freigabe der Kosten durch KBS nötig.
2. Register-Quellen ohne schriftliche Erlaubnis weiter nur für die Website (2.2)? Vorschlag: ja; KBS holt für häufige
   Quellen eine Erlaubnis ein, die auch Social abdeckt.
3. Pexels als automatischer Stock-Weg, Unsplash nur von Hand (2.4)? Vorschlag: ja.
4. Tausch gegen die Bildkarte am Ablauftag der Lizenz automatisch (3.3)? Vorschlag: ja, mit Protokoll.
5. Social-Bild mit Logo-Leiste oder ohne (F4, Frage 2)?

## Quellen (offizielle Seiten, Abruf 13.11.2026)

- Unsplash-Lizenz: https://unsplash.com/license
- Unsplash-API-Richtlinien: https://help.unsplash.com/en/articles/2511245-unsplash-api-guidelines
- Pexels-Lizenz: https://www.pexels.com/license/
- Pexels-API: https://www.pexels.com/api/documentation/
- Gemini-API, Preise: https://ai.google.dev/gemini-api/docs/pricing (leitet weiter auf https://aistudio.google.com/docs/pricing)
- Gemini-API, Bilderzeugung (Modelle, Formate, SynthID): https://ai.google.dev/gemini-api/docs/image-generation (leitet weiter auf https://aistudio.google.com/docs/image-generation)
- Instagram, Bildanforderungen: https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media
- Facebook, Page Photos: https://developers.facebook.com/docs/graph-api/reference/page/photos/
- Wikimedia Commons, Weiterverwendung: https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia
- Wikimedia, Standardgrößen der Vorschaubilder: https://www.mediawiki.org/wiki/Common_thumbnail_sizes
