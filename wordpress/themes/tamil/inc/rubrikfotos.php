<?php
/**
 * Rubrikfotos: feste Ersatzbilder je Rubrik für Beiträge und Seitenköpfe ohne eigenes Foto (Luis: „überall Bilder“).
 * Nur echte Fotos aus dem Rückblick-Bestand (Wikimedia Commons) mit Urheber, Lizenz und Quelle; Herkunft je Datei in
 * assets/img/rubrik/NACHWEIS.md. Erzeugt aus design/inhalte/rueckblick/rueckblick.json.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Rubrikfoto einer Rubrik (Slug), sonst das allgemeine.
 *
 * @return array{datei:string,w:int,h:int,alt:string,nachweis:string,quelle:string}
 */
function tamil_rubrikfoto( string $slug ): array {
	// phpcs:disable WordPress.Arrays.ArrayDeclarationSpacing.AssociativeArrayFound -- Tabelle, eine Zeile je Rubrik
	$fotos = array(
		'events'        => array( 'datei' => 'events.jpg', 'w' => 960, 'h' => 720, 'alt' => 'Der Sri-Ganesha-Hindutempel an der Hasenheide in Berlin mit Turm und Festzelt, aufgenommen im Juni 2026', 'nachweis' => 'Foto: 18quirl08 / Wikimedia Commons, CC BY-SA 4.0', 'quelle' => 'https://commons.wikimedia.org/wiki/File:Sri_Ganesha_Hindutempel_1_Berlin_2026.jpg' ),
		'kino'          => array( 'datei' => 'kino.jpg', 'w' => 960, 'h' => 720, 'alt' => 'Geschmückter Festwagen beim Koothandavar-Fest in Koovagam, Tamil Nadu, davor eine Menschenmenge von hinten (Archivbild 2023)', 'nachweis' => 'Foto: D Neethidoss / Wikimedia Commons, CC BY-SA 4.0', 'quelle' => 'https://commons.wikimedia.org/wiki/File:Kovagam_koothandavar_temple.jpg' ),
		'community'     => array( 'datei' => 'community.jpg', 'w' => 960, 'h' => 1280, 'alt' => 'Der bunt bemalte Tempelturm des Sri-Kamadchi-Ampal-Tempels in Hamm-Uentrop (Archivbild 2014)', 'nachweis' => 'Foto: Rainer Halama / Wikimedia Commons, CC BY-SA 4.0', 'quelle' => 'https://commons.wikimedia.org/wiki/File:Hamm-Tempel-Farbgestaltung2014-11-02-13-07.jpg' ),
		'kultur'        => array( 'datei' => 'kultur.jpg', 'w' => 960, 'h' => 1440, 'alt' => 'Die Bharatanatyam-Tänzerin Amrutha Naresh Rao bei einem Auftritt in Bangalore (Symbolbild)', 'nachweis' => 'Foto: Bobinson / Wikimedia Commons, CC BY-SA 4.0', 'quelle' => 'https://commons.wikimedia.org/wiki/File:Bharatanatyam_dancer_amrutha_naresh_rao_1.jpg' ),
		'entertainment' => array( 'datei' => 'kultur.jpg', 'w' => 960, 'h' => 1440, 'alt' => 'Die Bharatanatyam-Tänzerin Amrutha Naresh Rao bei einem Auftritt in Bangalore (Symbolbild)', 'nachweis' => 'Foto: Bobinson / Wikimedia Commons, CC BY-SA 4.0', 'quelle' => 'https://commons.wikimedia.org/wiki/File:Bharatanatyam_dancer_amrutha_naresh_rao_1.jpg' ),
		'kueche'        => array( 'datei' => 'kueche.jpg', 'w' => 960, 'h' => 982, 'alt' => 'Vegetarisches Essen nach Art Tamil Nadus auf einem Bananenblatt, die einzelnen Gerichte beschriftet (Symbolbild)', 'nachweis' => 'Foto: KARTY JazZ / Wikimedia Commons, CC BY-SA 4.0', 'quelle' => 'https://commons.wikimedia.org/wiki/File:Veg_Full_Meals_in_Tamil_Nadu.JPG' ),
		'news'          => array( 'datei' => 'news.jpg', 'w' => 960, 'h' => 566, 'alt' => 'Das Reichstagsgebäude in Berlin, Sitz des Bundestags (Archivbild)', 'nachweis' => 'Foto: Jörg Braukmann / Wikimedia Commons, CC BY-SA 4.0', 'quelle' => 'https://commons.wikimedia.org/wiki/File:Reichstagsgebäude_von_Westen.jpg' ),
		'sport'         => array( 'datei' => 'sport.jpg', 'w' => 960, 'h' => 720, 'alt' => 'Das Stade Municipal in Yverdon-les-Bains, Heimstadion von Yverdon-Sport (Archivbild 2022)', 'nachweis' => 'Foto: Vincenzo.togni / Wikimedia Commons, CC BY-SA 4.0', 'quelle' => 'https://commons.wikimedia.org/wiki/File:The_Stade_Municipal_of_Yverdon_in_2022.jpg' ),
		'allgemein'     => array( 'datei' => 'allgemein.jpg', 'w' => 960, 'h' => 720, 'alt' => 'Der Sri-Ganesha-Hindutempel an der Hasenheide in Berlin mit Turm und Festzelt, aufgenommen im Juni 2026', 'nachweis' => 'Foto: 18quirl08 / Wikimedia Commons, CC BY-SA 4.0', 'quelle' => 'https://commons.wikimedia.org/wiki/File:Sri_Ganesha_Hindutempel_1_Berlin_2026.jpg' ),
	);
	// phpcs:enable
	return $fotos[ $slug ] ?? $fotos['allgemein'];
}
