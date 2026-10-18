=== Tamil.de News-Radar ===
Contributors: hkgrowthoperator
Tags: redaktion, rest-api, events, kino, weiterleitungen
Requires at least: 6.6
Tested up to: 7.1
Requires PHP: 8.1
Stable tag: 1.0.0
License: MIT

Anbindung des News-Radars (externes Werkzeug) an WordPress.

== Description ==

Der News-Radar sammelt Meldungen, schreibt Entwürfe und legt sie nach Freigabe in WordPress an. Dieses Plugin liefert
die Gegenstelle:

* REST-Namespace `tamil-radar/v1`: `GET status`, `POST beitrag` (Beitrag + Base64-Bild + Kategorie + Schlagworte +
  Meta + SEO in einem Aufruf, Dublette per `radar_uid` → 409), `GET/PUT beitrag/{uid}`, `GET stil`.
* Beitrags-Meta: Quelle, Bildnachweis, Ort, Event (Datum, Ende, Ort, Land, Tickets), Kinoliste (`kino_fakten`),
  Rezept – alles im REST-Schema sichtbar.
* Rolle „Radar“ (eigene Beiträge anlegen, veröffentlichen, aktualisieren, Bilder hochladen).
* Menü „News-Radar“ mit dem Cockpit (iframe + Tab-Link), Dashboard-Widget, Spalte „Radar“ in der Beitragsliste.
* 301-Weiterleitungen aus einer CSV (Relaunch: alte Kategorien und Seiten).
* Werbeplätze: `tamil_radar_anzeige('leaderboard')` bzw. `[tamil_anzeige platz="…"]` – Advanced Ads, sonst
  Banner-HTML aus den Einstellungen.
* Abfragen fürs Theme: `tamil_radar_upcoming_events()`, `tamil_radar_kino_posts()`, `tamil_radar_event()`,
  `tamil_radar_kino_fakten()`, `tamil_radar_bildnachweis()`.

== Installation ==

1. Plugin hochladen und aktivieren.
2. Benutzer `ki-agent` mit Rolle „Radar“ anlegen, Anwendungspasswort erzeugen → `WP_URL`, `WP_USER`,
   `WP_APP_PASSWORD` im Radar eintragen.
3. Kategorien `news`, `community`, `entertainment`, `kino`, `events`, `kueche`, `sport`, `kultur` anlegen.
4. Unter News-Radar → Einstellungen die Cockpit-Adresse, Werbeplätze und die Weiterleitungs-CSV hinterlegen.

== Changelog ==

= 1.0.0 =
* Erste Fassung.
