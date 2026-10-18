=== Tamil.de Website ===
Contributors: hkgrowthoperator
Tags: events, kino, werbung, weiterleitungen
Requires at least: 6.6
Tested up to: 7.1
Requires PHP: 8.1
Stable tag: 1.0.0
License: MIT

Website-Funktionen für Tamil.de – unabhängig vom Theme und vom News-Radar.

== Description ==

* Beitrags-Felder mit Eingabemaske „Vorspann und Termin“: Vorspann, Ort, Veranstaltung (Beginn, Ende, Ort, Land,
  Veranstalter, Preis, Ticket-Link). Die Kinoliste `kino_fakten` (JSON) schreibt der News-Radar; die Maske zeigt sie an.
  Alle Felder sind im REST-Schema sichtbar.
* Werbeplätze `tamil_site_anzeige( 'leaderboard' )` bzw. `[tamil_anzeige platz="…"]`: Advanced-Ads-Platzierung, sonst
  Banner-HTML, sonst eine Eigenanzeige von Tamil.de (Production, Newsletter, Werben, WhatsApp-Kanal).
* 301-Weiterleitungen aus einer CSV (Spalten „alt“, „neu“) für den Relaunch.
* Abfragen fürs Theme: `tamil_site_upcoming_events()`, `tamil_site_kino_posts()`, `tamil_site_event()`,
  `tamil_site_kino_fakten()`.

Das Theme „Tamil.de“ nutzt diese Funktionen, wenn das Plugin aktiv ist, und läuft ohne sie weiter (ohne Werbeplätze
und Terminlisten). Der News-Radar ist ein eigenes Plugin („Tamil.de News-Radar“) und keine Voraussetzung.

== Installation ==

1. Plugin hochladen und aktivieren.
2. Einstellungen → Tamil.de Website: Werbeplätze und die Weiterleitungs-CSV hinterlegen.

== Changelog ==

= 1.0.0 =
* Erste Fassung.
