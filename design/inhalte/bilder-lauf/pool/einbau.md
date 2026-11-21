# Einbau der Pool-Erweiterung ins Theme

Für den Theme-Agenten. In diesem Lauf wurde am Theme nichts geändert; alles liegt unter
`design/inhalte/bilder-lauf/`. 32 neue Symbolbilder, je Rubrik vier, alle KI-generiert.

## Vorher klären (nicht Sache des Theme-Agenten allein)

1. **Entscheidungslog.** `docs/entscheidungen.md` und `docs/spezifikation/bilder-und-lizenzen.md` 4.1 sagen seit
   11.11. „keine KI-Bilder“; der Pool besteht laut `inc/bildpool.php` und `NACHWEIS.md` aus „echten Fotos“. Der
   Auftrag von Luis vom 21.11. kehrt das um. Das gehört als neuer Eintrag ins Entscheidungslog, bevor die Bilder live
   gehen, sonst widerspricht der Code der Doku.
2. **Heikle Themen.** Spezifikation 4.2 Punkt 3: Politik, Justiz, Unglück, Tod, Medizin, Gedenken bekommen kein
   KI-Bild. Das Theme kennt diese Einstufung heute nicht; die vier neuen Nachrichten-Bilder (`news-4` bis `news-7`)
   würden also auch bei Asyl- und Gerichtsmeldungen erscheinen. Entweder die `news`-Bilder vorerst weglassen oder
   eine Sperre bauen (z. B. Beitrags-Meta vom Radar, bei „heikel“ nur die drei Commons-Fotos).
3. **Wortlaut des Nachweises.** Vorgabe für diesen Lauf: „Symbolbild: KI-generiert · Tamil.de“. Die Spezifikation
   (4.8 und Tabelle der Bildarten) nennt „Symbolbild: KI-generiert · Tamil.de“. Einen Wortlaut wählen und überall
   gleich setzen.

## 1. Dateien kopieren

Alle `*.webp` aus `design/inhalte/bilder-lauf/pool-theme/` (96 Dateien) nach
`wordpress/themes/tamil/assets/img/rubrik/`. Namen und Größen folgen dem Bestand: `<rubrik>-<n>.webp` (960 × 540),
`<rubrik>-<n>-480.webp`, `<rubrik>-<n>-320.webp`, WebP Qualität 78. Die Nummern schließen an den Bestand an
(`news-4…7`, `events-9…12`, `community-3…6`, `kueche-4…7`, `kino-9…12`, `sport-2…5`, `kultur-2…5`);
`entertainment-1…4` ist neu. `pool-neu.json` daneben enthält dieselben Angaben maschinenlesbar (nicht mitkopieren).

Die 320er-Fassung liest auch `inc/signatur.php` (Zeile um 194); sie ist für jedes Bild vorhanden.

## 2. Liste ergänzen: `inc/bildpool.php`, Funktion `tamil_bildpool()`

Die folgenden Zeilen an die jeweilige Rubrik anhängen; `entertainment` ist ein neuer Schlüssel. Neu ist das Feld
`'ki' => true`; `urheber`, `lizenz`, `lizenz_url`, `seite` bleiben leer (keine erfundenen Angaben). Die
`@return`-Typen in `tamil_bildpool()`, `tamil_pool_liste()`, `tamil_pool_bild()` (alle `inc/bildpool.php`),
`tamil_pool_fuer()` und `tamil_pool_seite()` (`inc/bildkette.php`) um `ki?:bool` erweitern und den Kopfkommentar
beider Dateien („echte Fotos von Wikimedia Commons“) anpassen.

```php
		'news' => array( // anhängen
			array( 'datei' => 'news-4.webp', 'w' => 960, 'h' => 540, 'alt' => 'Bahnsteig an einem grauen Morgen, Reisende von hinten vor einem einfahrenden Zug', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '40% 40%', 'ki' => true ),
			array( 'datei' => 'news-5.webp', 'w' => 960, 'h' => 540, 'alt' => 'Abflughalle eines Flughafens, Reisende mit Koffern von hinten', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '40% 40%', 'ki' => true ),
			array( 'datei' => 'news-6.webp', 'w' => 960, 'h' => 540, 'alt' => 'Leerer Wartebereich in einem Amtsgebäude mit Stuhlreihe und Tageslicht', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
			array( 'datei' => 'news-7.webp', 'w' => 960, 'h' => 540, 'alt' => 'Mikrofone auf einem Podiumstisch vor leeren Stuhlreihen', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
		),
		'entertainment' => array( // anhängen
			array( 'datei' => 'entertainment-1.webp', 'w' => 960, 'h' => 540, 'alt' => 'Konzertpublikum von hinten vor einer Bühne im Gegenlicht', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
			array( 'datei' => 'entertainment-2.webp', 'w' => 960, 'h' => 540, 'alt' => 'Ein Mikrofon auf einer leeren Bühne im warmen Scheinwerferlicht', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '28% 40%', 'ki' => true ),
			array( 'datei' => 'entertainment-3.webp', 'w' => 960, 'h' => 540, 'alt' => 'Hände am Mischpult, dahinter unscharf die beleuchtete Bühne', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
			array( 'datei' => 'entertainment-4.webp', 'w' => 960, 'h' => 540, 'alt' => 'Hände spielen eine Mridangam-Trommel auf der Bühne', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
		),
		'events' => array( // anhängen
			array( 'datei' => 'events-9.webp', 'w' => 960, 'h' => 540, 'alt' => 'Kolam aus weißem Reismehl vor einer Haustür in Deutschland', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '32% 45%', 'ki' => true ),
			array( 'datei' => 'events-10.webp', 'w' => 960, 'h' => 540, 'alt' => 'Brennende Öllampen aus Ton in einer Reihe bei Dämmerung', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
			array( 'datei' => 'events-11.webp', 'w' => 960, 'h' => 540, 'alt' => 'Geschmückter Festsaal mit Stuhlreihen und Messingleuchter vor Beginn', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '40% 40%', 'ki' => true ),
			array( 'datei' => 'events-12.webp', 'w' => 960, 'h' => 540, 'alt' => 'Girlanden aus Tagetes und Jasmin hängen an einem Eingang', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
		),
		'community' => array( // anhängen
			array( 'datei' => 'community-3.webp', 'w' => 960, 'h' => 540, 'alt' => 'Bunter Tempelturm eines Hindu-Tempels vor grauem Himmel in einem Gewerbegebiet', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '30% 45%', 'ki' => true ),
			array( 'datei' => 'community-4.webp', 'w' => 960, 'h' => 540, 'alt' => 'Abgestellte Schuhe vor dem Eingang eines Tempels im Winter', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
			array( 'datei' => 'community-5.webp', 'w' => 960, 'h' => 540, 'alt' => 'Aufgeschlagenes Schulheft mit Bleistift auf einem Holztisch in einem leeren Klassenzimmer, die Tafel unscharf', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
			array( 'datei' => 'community-6.webp', 'w' => 960, 'h' => 540, 'alt' => 'Hände reichen Tee in Stahlbechern an einem Tisch im Vereinsheim', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
		),
		'kueche' => array( // anhängen
			array( 'datei' => 'kueche-4.webp', 'w' => 960, 'h' => 540, 'alt' => 'Ein Dosa wird auf einer heißen Eisenplatte ausgestrichen', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
			array( 'datei' => 'kueche-5.webp', 'w' => 960, 'h' => 540, 'alt' => 'Idli mit Sambar und Kokos-Chutney auf einem Stahlteller', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
			array( 'datei' => 'kueche-6.webp', 'w' => 960, 'h' => 540, 'alt' => 'Runde Gewürzdose aus Edelstahl mit Senfsaat, Chili, Kurkuma und Curryblättern', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
			array( 'datei' => 'kueche-7.webp', 'w' => 960, 'h' => 540, 'alt' => 'Südindischer Filterkaffee im Stahlbecher mit Schälchen', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '28% 40%', 'ki' => true ),
		),
		'kino' => array( // anhängen
			array( 'datei' => 'kino-9.webp', 'w' => 960, 'h' => 540, 'alt' => 'Kinopublikum von hinten im Licht der Leinwand', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '40% 40%', 'ki' => true ),
			array( 'datei' => 'kino-10.webp', 'w' => 960, 'h' => 540, 'alt' => 'Lichtstrahl des Projektors über dunklen Sitzreihen', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
			array( 'datei' => 'kino-11.webp', 'w' => 960, 'h' => 540, 'alt' => 'Popcorn in schlichten Papierbechern auf der Theke eines Kinofoyers', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
			array( 'datei' => 'kino-12.webp', 'w' => 960, 'h' => 540, 'alt' => 'Eingang eines kleinen Kinos am Abend, nasser Gehweg, Besucher von hinten', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '30% 45%', 'ki' => true ),
		),
		'sport' => array( // anhängen
			array( 'datei' => 'sport-2.webp', 'w' => 960, 'h' => 540, 'alt' => 'Kricketschläger, Ball und Beinschützer am Rand eines Vereinsplatzes', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
			array( 'datei' => 'sport-3.webp', 'w' => 960, 'h' => 540, 'alt' => 'Fußball auf einem nassen Amateurplatz mit Tor und Flutlicht im Herbst', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
			array( 'datei' => 'sport-4.webp', 'w' => 960, 'h' => 540, 'alt' => 'Sporthalle mit Handballtor und Ball auf dem Hallenboden', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
			array( 'datei' => 'sport-5.webp', 'w' => 960, 'h' => 540, 'alt' => 'Gefalteter Karateanzug mit schwarzem Gürtel auf dem Mattenboden', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '32% 35%', 'ki' => true ),
		),
		'kultur' => array( // anhängen
			array( 'datei' => 'kultur-2.webp', 'w' => 960, 'h' => 540, 'alt' => 'Füße einer Bharatanatyam-Tänzerin mit Glöckchen auf dem Bühnenboden', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
			array( 'datei' => 'kultur-3.webp', 'w' => 960, 'h' => 540, 'alt' => 'Erhobene Hand einer Tänzerin in der Mudra-Geste Alapadma, Fingerspitzen und Handfläche rot gefärbt', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '32% 35%', 'ki' => true ),
			array( 'datei' => 'kultur-4.webp', 'w' => 960, 'h' => 540, 'alt' => 'Hände schlagen mit zwei Stöcken eine Parai-Rahmentrommel', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
			array( 'datei' => 'kultur-5.webp', 'w' => 960, 'h' => 540, 'alt' => 'Alte Bücher im Regal neben einer Messinglampe, die Schrift auf den Rücken unscharf', 'urheber' => '', 'lizenz' => '', 'lizenz_url' => '', 'seite' => '', 'fokus' => '35% 40%', 'ki' => true ),
		),
```

Alle Maße sind 960 × 540. `fokus` ist die Bildmitte für `object-position`: Das Hauptmotiv sitzt oben links der
Mitte, unten ist es ruhig und dunkel (Platz für Titel und Markenzeichen).

**`tamil_pool_liste()`** braucht keine Änderung: Für `entertainment` steht die Reihenfolge
`entertainment, events, kino` schon im Code und greift, sobald der Schlüssel gefüllt ist.

**Reihenfolge.** `tamil_pool_seite()` vergibt reihum ab `post_id % Anzahl`. Mit den neuen Einträgen ändert sich die
Zuordnung Beitrag → Bild für alle Beiträge; das ist bei der Sichtprüfung zu erwarten. Sinnvoll ist, die neuen Bilder
zwischen die alten zu mischen statt hinten anzuhängen (Commit 9451b91 hat ähnliche Bilder schon einmal auseinander
sortiert; bei Kino sind die acht alten Säle einander sehr ähnlich).

## 3. Nachweis: `inc/bildkette.php`, Funktion `tamil_pool_nachweis()`

Heute baut die Funktion immer „Foto: Urheber / Wikimedia Commons, Lizenz“ über `tamil_nachweis_bauen()` mit
`zuschnitt` und `symbol`. Für KI-Bilder vorher abzweigen:

```php
function tamil_pool_nachweis( array $pool ): string {
	if ( ! empty( $pool['ki'] ) ) {
		return esc_html__( 'Symbolbild: KI-generiert · Tamil.de', 'tamil' );
	}
	// … bisheriger Aufruf von tamil_nachweis_bauen() …
}
```

Nicht über `tamil_nachweis_bauen()` schicken: Dort würde „Symbolbild,“ ein zweites Mal davorgesetzt und
„zugeschnitten“ angehängt. Die Rückgabe läuft wie bisher an drei Stellen weiter, ohne Änderung:
`tamil_bild()` (Zeile um 492, setzt `$w['nachweis']` und meldet ihn an `tamil_nachweise()` für den Fuß
„Bildnachweise dieser Seite“), `tamil_pool_img()` (Zeile um 526) und `tamil_bild_nachweis_html()` (Zeile um 409,
unter dem Beitragsbild).

Ohne Änderung arbeiten: das Schild `tamil_symbolbild_schild()`, der Alternativtext „Symbolbild: …“ in `tamil_bild()`
und `tamil_pool_img()`, das `srcset` in `tamil_pool_tag()` (320w, 480w, 960w). `inc/schema.php` gibt Pool-Bilder
nicht in die strukturierten Daten (Zeile 94, `'pool' !== art`); dort ist nichts zu tun.

## 4. Nachweisliste: `assets/img/rubrik/NACHWEIS.md`

Einleitung anpassen (nicht mehr nur Commons) und diese Zeilen anhängen:

| Datei | Rubrik | Nachweis | Lizenz | Quelle im Repo |
|---|---|---|---|---|
| `news-4.webp` | Nachrichten | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/news/bahnsteig-morgen.jpg` |
| `news-5.webp` | Nachrichten | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/news/abflughalle.jpg` |
| `news-6.webp` | Nachrichten | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/news/amtsflur.jpg` |
| `news-7.webp` | Nachrichten | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/news/mikrofone-podium.jpg` |
| `entertainment-1.webp` | Entertainment | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/entertainment/konzert-publikum.jpg` |
| `entertainment-2.webp` | Entertainment | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/entertainment/mikrofon-buehne.jpg` |
| `entertainment-3.webp` | Entertainment | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/entertainment/mischpult.jpg` |
| `entertainment-4.webp` | Entertainment | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/entertainment/mridangam-haende.jpg` |
| `events-9.webp` | Events | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/events/kolam-haustuer.jpg` |
| `events-10.webp` | Events | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/events/oellampen-reihe.jpg` |
| `events-11.webp` | Events | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/events/festsaal-vorbereitet.jpg` |
| `events-12.webp` | Events | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/events/blumengirlanden.jpg` |
| `community-3.webp` | Community | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/community/gopuram-grauer-himmel.jpg` |
| `community-4.webp` | Community | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/community/schuhe-tempeleingang.jpg` |
| `community-5.webp` | Community | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/community/klassenzimmer-tamilschule.jpg` |
| `community-6.webp` | Community | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/community/tee-vereinsheim.jpg` |
| `kueche-4.webp` | Küche | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/kueche/dosa-pfanne.jpg` |
| `kueche-5.webp` | Küche | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/kueche/idli-sambar.jpg` |
| `kueche-6.webp` | Küche | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/kueche/gewuerzdose.jpg` |
| `kueche-7.webp` | Küche | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/kueche/filterkaffee.jpg` |
| `kino-9.webp` | Kino | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/kino/publikum-leinwandlicht.jpg` |
| `kino-10.webp` | Kino | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/kino/projektorstrahl.jpg` |
| `kino-11.webp` | Kino | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/kino/popcorn-foyer.jpg` |
| `kino-12.webp` | Kino | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/kino/kinoeingang-abend.jpg` |
| `sport-2.webp` | Sport | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/sport/kricket-ausruestung.jpg` |
| `sport-3.webp` | Sport | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/sport/fussball-vereinsplatz.jpg` |
| `sport-4.webp` | Sport | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/sport/sporthalle-hallenfussball.jpg` |
| `sport-5.webp` | Sport | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/sport/karate-guertel.jpg` |
| `kultur-2.webp` | Kultur | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/kultur/bharatanatyam-fuesse.jpg` |
| `kultur-3.webp` | Kultur | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/kultur/mudra-haende.jpg` |
| `kultur-4.webp` | Kultur | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/kultur/parai-trommel.jpg` |
| `kultur-5.webp` | Kultur | Symbolbild: KI-generiert · Tamil.de | – | `design/inhalte/bilder-lauf/pool/kultur/buecher-messinglampe.jpg` |

Prompt und Modell je Bild stehen in `design/inhalte/bilder-lauf/pool/liste.md`.

## 5. Erzeuger nicht vergessen: `design/inhalte/bildpool/holen.py`

`inc/bildpool.php` und `NACHWEIS.md` werden von `holen.py` aus `kandidaten.json` und `bildpool.json` geschrieben
(„nicht von Hand ändern“). Wer nur die PHP-Datei ergänzt, verliert die Einträge beim nächsten Lauf. Sauber ist:

- `RUBRIKEN` enthält `entertainment` schon.
- In `bauen()` ein dritter Weg neben Commons und Archiv: Einträge mit `"ki": true` aus
  `design/inhalte/bilder-lauf/pool-theme/pool-neu.json` unverändert übernehmen (keine Commons-Abfrage, kein Zuschnitt,
  die drei WebP-Dateien je Bild sind fertig).
- `php_schreiben()` gibt das Feld `ki` mit aus; `nachweis_schreiben()` schreibt für `ki` den festen Nachweis statt
  Urheber und Lizenz. `LIZENZ_OK` gilt für diese Einträge nicht.

## 6. Prüfen

`bash wordpress/dev/lint.sh`, `python -m pytest -q` (u. a. `tests/test_bilder.py`, `tests/test_lizenz.py`),
`node tools/shots.mjs` für Startseite und eine Rubrik bei 390/820/1280. Sichtprüfung: Schild „Symbolbild“ an jeder
Karte mit Pool-Bild, im Fuß genau eine Zeile „Symbolbild: KI-generiert · Tamil.de“, kein leerer Link, kein
„Wikimedia Commons“ ohne Urheber.

## Bilder mit Vorbehalt

Siehe `liste.md`: `community-4` (Ganesha-Relief am Tempeleingang), `events-10` (Dächer im Hintergrund wirken
französisch), `events-12` (Saal wirkt südindisch). Wer streng nach Spezifikation 4.5 und 4.7 geht, lässt diese drei
weg; die Rubriken haben dann immer noch drei neue Bilder.
