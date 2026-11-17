<?php
/**
 * Rubrik-Pool: je Rubrik bis zu vier echte Fotos von Wikimedia Commons (CC0, CC BY, CC BY-SA) als Symbolbilder für
 * Beiträge ohne eigenes Foto (inc/bildkette.php, Stufe d). Urheber, Lizenz und Lizenz-Adresse stammen aus Commons
 * (API oder Dateiseite; Beleg je Bild in design/inhalte/bildpool/bildpool.json). Zu jedem Bild gibt es eine kleine
 * Fassung „<datei>-320.webp“ für kleine Rahmen.
 * Erzeugt von design/inhalte/bildpool/holen.py aus kandidaten.json – nicht von Hand ändern; Nachweise auch in
 * assets/img/rubrik/NACHWEIS.md.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Alle Pool-Bilder je Rubrik.
 *
 * @return array<string,array<int,array{datei:string,w:int,h:int,alt:string,urheber:string,lizenz:string,lizenz_url:string,seite:string,fokus:string}>>
 */
function tamil_bildpool(): array {
	// phpcs:disable WordPress.Arrays.ArrayDeclarationSpacing.AssociativeArrayFound -- Tabelle, eine Zeile je Bild
	return array(
		'news'      => array(
			array( 'datei' => 'news-1.webp', 'w' => 960, 'h' => 566, 'alt' => 'Das Reichstagsgebäude in Berlin, Sitz des Bundestags', 'urheber' => 'Jörg Braukmann', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Reichstagsgeb%C3%A4ude_von_Westen.jpg', 'fokus' => '50% 55%' ),
			array( 'datei' => 'news-2.webp', 'w' => 960, 'h' => 720, 'alt' => 'Das Rathaus von Emsdetten im Münsterland', 'urheber' => 'Ewe vonDetten', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Am_Markt_01_-_Rathaus.jpg', 'fokus' => '50% 50%' ),
			array( 'datei' => 'news-3.webp', 'w' => 960, 'h' => 720, 'alt' => 'Terminal und Vorfeld des Flughafens Bandaranaike bei Colombo in Sri Lanka', 'urheber' => 'ANKAN', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Bandaranaike_International_Airport_(2).jpg', 'fokus' => '50% 50%' ),
		),
		'events'    => array(
			array( 'datei' => 'events-1.webp', 'w' => 960, 'h' => 720, 'alt' => 'Geschmückter Festwagen bei einem Tempelfest in Tamil Nadu, davor eine Menschenmenge von hinten', 'urheber' => 'D Neethidoss', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Kovagam_koothandavar_temple.jpg', 'fokus' => '50% 45%' ),
			array( 'datei' => 'events-2.webp', 'w' => 960, 'h' => 720, 'alt' => 'Tempelfest in Hamm: geschmückter Festwagen und Tempeltürme, davor Besucher unter bunten Schirmen', 'urheber' => 'Rainer Halama', 'lizenz' => 'CC BY-SA 2.5', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/2.5/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Hamm_Tempelfest_2118.jpg', 'fokus' => '50% 50%' ),
			array( 'datei' => 'events-3.webp', 'w' => 960, 'h' => 720, 'alt' => 'Ein geschmückter Tempelwagen mit bunten Stoffbahnen und Säulen vor grauem Himmel', 'urheber' => 'SathiyaSundar', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Theer_the_Temple_Car.jpg', 'fokus' => '50% 50%' ),
			array( 'datei' => 'events-4.webp', 'w' => 960, 'h' => 720, 'alt' => 'Bühne eines Open-Air-Festivals, davor viele Zuschauer von hinten', 'urheber' => 'Artep ^_^ from München, Germany', 'lizenz' => 'CC BY 2.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by/2.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Rock_am_See,_B%C3%BChne_2006.jpg', 'fokus' => '50% 50%' ),
			array( 'datei' => 'events-5.webp', 'w' => 960, 'h' => 720, 'alt' => 'Tempelfest in Hamm: Festwagen neben den Tempeltürmen, Besucher mit Regenschirmen', 'urheber' => 'Rainer Halama', 'lizenz' => 'CC BY-SA 2.5', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/2.5/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Hamm_Tempelfest_2185.jpg', 'fokus' => '50% 45%' ),
			array( 'datei' => 'events-6.webp', 'w' => 960, 'h' => 720, 'alt' => 'Geschmückter Festwagen des Sri-Muthumariamman-Tempels beim Wagenfest', 'urheber' => 'ChanakaW', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Sri_Muthumariamman_Temple(Hindu_temple)_Teru_Festival_Chariot.jpg', 'fokus' => '50% 50%' ),
			array( 'datei' => 'events-7.webp', 'w' => 960, 'h' => 548, 'alt' => 'Umzug beim Karneval der Kulturen in Berlin mit Tänzerinnen und Tänzern in bunten Kostümen', 'urheber' => 'Lear 21', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:KDK_in_B_2025_03.jpg', 'fokus' => '50% 50%' ),
			array( 'datei' => 'events-8.webp', 'w' => 960, 'h' => 720, 'alt' => 'Der goldene Festwagen beim Thaipusam-Fest unter dem Abendhimmel', 'urheber' => 'Seelit2004', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Thaipusam_Festival_The_Golden_Chariot.jpg', 'fokus' => '50% 50%' ),
		),
		'community' => array(
			array( 'datei' => 'community-1.webp', 'w' => 960, 'h' => 720, 'alt' => 'Der Sri-Ganesha-Hindutempel an der Hasenheide in Berlin mit Turm und Festzelt', 'urheber' => '18quirl08', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Sri_Ganesha_Hindutempel_1_Berlin_2026.jpg', 'fokus' => '50% 42%' ),
			array( 'datei' => 'community-2.webp', 'w' => 960, 'h' => 720, 'alt' => 'Der bunt bemalte Tempelturm des Sri-Kamadchi-Ampal-Tempels in Hamm-Uentrop', 'urheber' => 'Rainer Halama', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Hamm-Tempel-Farbgestaltung2014-11-02-13-07.jpg', 'fokus' => '50% 50%' ),
		),
		'kueche'    => array(
			array( 'datei' => 'kueche-1.webp', 'w' => 960, 'h' => 720, 'alt' => 'Vegetarisches Essen nach Art Tamil Nadus auf einem Bananenblatt', 'urheber' => 'KARTY JazZ', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Veg_Full_Meals_in_Tamil_Nadu.JPG', 'fokus' => '50% 50%' ),
			array( 'datei' => 'kueche-2.webp', 'w' => 960, 'h' => 686, 'alt' => 'Kottu Roti, ein Gericht aus Sri Lanka, auf einem Teller', 'urheber' => 'Janice99999999999', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Kottu.jpg', 'fokus' => '50% 50%' ),
			array( 'datei' => 'kueche-3.webp', 'w' => 960, 'h' => 720, 'alt' => 'Ein Teller Chicken Kottu, gehacktes Fladenbrot mit Huhn und Gemüse', 'urheber' => 'Dan arndt', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Chicken_Kottu.jpg', 'fokus' => '50% 50%' ),
		),
		'kino'      => array(
			array( 'datei' => 'kino-1.webp', 'w' => 960, 'h' => 640, 'alt' => 'Der Kinosaal der Lichtburg in Essen mit rotem Vorhang, Rängen und Wandleuchten', 'urheber' => 'Tuxyso', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Lichtburg-Essen-Kinosaal-2025.jpg', 'fokus' => '50% 50%' ),
			array( 'datei' => 'kino-2.webp', 'w' => 960, 'h' => 720, 'alt' => 'Alter Filmprojektor in den Eden-Lichtspielen in Lübeck', 'urheber' => 'Elisabeth S. Meyer-Lassahn', 'lizenz' => 'CC BY-SA 3.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/3.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:ESML_Eden-Lichtspiele_L%C3%BCbeck_Projektor.jpg', 'fokus' => '50% 50%' ),
			array( 'datei' => 'kino-3.webp', 'w' => 960, 'h' => 540, 'alt' => 'Kinosaal des Savoy Filmtheaters, Sitzreihen vor dem Vorhang in blauem und rotem Licht', 'urheber' => 'Taskmanager117', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Kinosaal_Savoy_Filmtheater.jpg', 'fokus' => '50% 50%' ),
			array( 'datei' => 'kino-4.webp', 'w' => 960, 'h' => 640, 'alt' => 'Das Kino in Zell am See von außen mit dem Schriftzug „Kino“ über dem Eingang', 'urheber' => 'Linie29', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Lichtspiele_Zell_am_See.JPG', 'fokus' => '50% 50%' ),
			array( 'datei' => 'kino-5.webp', 'w' => 960, 'h' => 636, 'alt' => 'Kinosaal des Kamp-Theaters in Bad Doberan mit roten Sitzreihen vor der Leinwand', 'urheber' => 'an-d', 'lizenz' => 'CC BY-SA 3.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/3.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Doberan_Kamp-Theater_Kinosaal_1.jpg', 'fokus' => '50% 55%' ),
			array( 'datei' => 'kino-6.webp', 'w' => 960, 'h' => 611, 'alt' => 'Leinwand und Sitzreihen im Zeughauskino in Berlin', 'urheber' => 'Pedro s.l.i. ger', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Zeughauskino_Leinwand_(2).jpg', 'fokus' => '50% 50%' ),
			array( 'datei' => 'kino-7.webp', 'w' => 960, 'h' => 639, 'alt' => 'Innenansicht des Schlachthofkinos mit Leinwand und gelben Sitzreihen', 'urheber' => 'Schlachthof Soest', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Innenansicht_Kinosaal_%22SchlachthofKino%22.jpg', 'fokus' => '50% 55%' ),
			array( 'datei' => 'kino-8.webp', 'w' => 960, 'h' => 638, 'alt' => 'Kinosaal der Rialto-Lichtspiele mit Sitzreihen in warmem Licht', 'urheber' => 'Rialto Lichtspiele', 'lizenz' => 'CC BY-SA 3.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/3.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:RIALTO_Lichtspiele_Kinosaal_-_Leinwand_im_R%C3%BCcken.jpg', 'fokus' => '50% 50%' ),
		),
		'sport'     => array(
			array( 'datei' => 'sport-1.webp', 'w' => 960, 'h' => 720, 'alt' => 'Rasen und Tribüne eines Fußballstadions in der Schweiz', 'urheber' => 'Vincenzo.togni', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:The_Stade_Municipal_of_Yverdon_in_2022.jpg', 'fokus' => '50% 60%' ),
		),
		'kultur'    => array(
			array( 'datei' => 'kultur-1.webp', 'w' => 960, 'h' => 540, 'alt' => 'Messingleuchter, Blumen und Bananen auf einem Tisch im Arulmigu-Sivan-Tempel in Glattbrugg', 'urheber' => 'Roland zh', 'lizenz' => 'CC BY-SA 3.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/3.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Arulmigu_Sivan_Temple,_Glattbrugg_-_Innenansicht_20210320_133243.jpg', 'fokus' => '50% 60%' ),
		),
		'allgemein' => array(
			array( 'datei' => 'allgemein-1.webp', 'w' => 960, 'h' => 692, 'alt' => 'Die Hauptwache in Frankfurt am Main mit Cafétischen davor', 'urheber' => 'DXR', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Hauptwache,_Frankfurt,_South_view_20190915_1.jpg', 'fokus' => '50% 55%' ),
			array( 'datei' => 'allgemein-2.webp', 'w' => 960, 'h' => 425, 'alt' => 'Die Altstadt von Aarau mit der Stadtkirche', 'urheber' => 'Lutz Fischer', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Aarau_Altstadt_Kirche_8941.jpg', 'fokus' => '50% 50%' ),
			array( 'datei' => 'allgemein-3.webp', 'w' => 960, 'h' => 640, 'alt' => 'Blick auf das Städtchen Leuk im Wallis unter Wolken', 'urheber' => 'Björrn Sothmann', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Leuk_20_12_2014_01.jpg', 'fokus' => '50% 50%' ),
		),
	);
	// phpcs:enable
}

/**
 * Die Pool-Bilder, die für eine Rubrik in Frage kommen. Ohne eigenen Pool: Kino und Entertainment nehmen den Pool
 * „kino“ bzw. „events“, nie den allgemeinen (Stadtansichten, Kirchen, Rathäuser passen nicht zu Filmen und Bühnen);
 * alle übrigen den allgemeinen Pool.
 *
 * @return array<int,array{datei:string,w:int,h:int,alt:string,urheber:string,lizenz:string,lizenz_url:string,seite:string,fokus:string}>
 */
function tamil_pool_liste( string $slug ): array {
	$pool   = tamil_bildpool();
	$ersatz = array(
		'kino'          => array( 'kino', 'entertainment', 'events' ),
		'entertainment' => array( 'entertainment', 'events', 'kino' ),
	);
	foreach ( $ersatz[ $slug ] ?? array( $slug ) as $versuch ) {
		if ( ! empty( $pool[ $versuch ] ) ) {
			return $pool[ $versuch ];
		}
	}
	return $pool['allgemein'];
}

/**
 * Ein Bild aus dem Pool einer Rubrik, fest nach Nummer gewählt. Auf einer Seite vergibt tamil_pool_seite() die Bilder
 * reihum, damit keines doppelt erscheint.
 *
 * @return array{datei:string,w:int,h:int,alt:string,urheber:string,lizenz:string,lizenz_url:string,seite:string,fokus:string}
 */
function tamil_pool_bild( string $slug, int $n = 0 ): array {
	$liste = tamil_pool_liste( $slug );
	return $liste[ abs( $n ) % count( $liste ) ];
}
