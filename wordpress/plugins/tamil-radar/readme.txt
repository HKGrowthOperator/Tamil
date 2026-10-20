=== Tamil.de News-Radar ===
Contributors: hkgrowthoperator
Tags: redaktion, rest-api, news-radar
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
* Beitrags-Meta: Herkunft (`radar_uid`, Quelle, Relevanz), Bildnachweis und -herkunft (`bild_origin` = `ki` für
  KI-Symbolbilder), Ort, Termin und Kinoliste (`kino_fakten`). Die Website-Felder registriert das Plugin
  „Tamil.de Website“ mit Eingabemaske, wenn es aktiv ist; der Radar schreibt sie in jedem Fall.
* Rolle „Radar“ (eigene Beiträge anlegen, veröffentlichen, aktualisieren, Bilder hochladen).
* Menü „News-Radar“ mit dem Cockpit (iframe + Tab-Link), Dashboard-Widget, Spalte „Radar“ in der Beitragsliste.

Der Radar ist ein eigenständiges Werkzeug. Website, Theme, Werbeplätze und Weiterleitungen hängen nicht von diesem
Plugin ab; wird es deaktiviert, bleiben alle Beiträge, Bilder und Meta-Felder erhalten.

== Installation ==

1. Plugin hochladen und aktivieren.
2. Benutzer `ki-agent` mit Rolle „Radar“ anlegen, Anwendungspasswort erzeugen → `WP_URL`, `WP_USER`,
   `WP_APP_PASSWORD` im Radar eintragen.
3. Kategorien `news`, `community`, `entertainment`, `kino`, `events`, `kueche`, `sport`, `kultur` anlegen.
4. Unter News-Radar → Einstellungen die Cockpit-Adresse hinterlegen.

== Changelog ==

= 1.0.0 =
* Erste Fassung.
