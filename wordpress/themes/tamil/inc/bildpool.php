<?php
/**
 * Rubrik-Pool: je Rubrik vier echte Fotos von Wikimedia Commons (CC0, CC BY, CC BY-SA) als Symbolbilder für Beiträge
 * ohne eigenes Foto (inc/bildkette.php, Stufe c). Urheber, Lizenz und Lizenz-Adresse stammen aus der Commons-API.
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
		),
		'events'    => array(
			array( 'datei' => 'events-1.webp', 'w' => 960, 'h' => 720, 'alt' => 'Geschmückter Festwagen bei einem Tempelfest in Tamil Nadu, davor eine Menschenmenge von hinten', 'urheber' => 'D Neethidoss', 'lizenz' => 'CC BY-SA 4.0', 'lizenz_url' => 'https://creativecommons.org/licenses/by-sa/4.0/', 'seite' => 'https://commons.wikimedia.org/wiki/File:Kovagam_koothandavar_temple.jpg', 'fokus' => '50% 45%' ),
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
 * Ein Bild aus dem Pool einer Rubrik, fest nach Nummer (Beitrags-ID) gewählt, damit Nachbarn verschieden sind;
 * unbekannte Rubriken nehmen den allgemeinen Pool.
 *
 * @return array{datei:string,w:int,h:int,alt:string,urheber:string,lizenz:string,lizenz_url:string,seite:string,fokus:string}
 */
function tamil_pool_bild( string $slug, int $n = 0 ): array {
	$pool  = tamil_bildpool();
	$liste = $pool[ $slug ] ?? $pool['allgemein'];
	return $liste[ abs( $n ) % count( $liste ) ];
}
