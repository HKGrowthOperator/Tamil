---
name: tamil-migration
description: Den echten Altbestand von tamil.de (Beiträge mit Originaldatum und Slug, Bilder, Seiten, 301-Weiterleitungen) in die neue WordPress-Website übertragen – idempotent, mit Prüfliste, die alte Seite nur lesend. Vorgeladen im migrator; gilt für /website-live.
user-invocable: false
---

# Migration Altbestand → neue Website

Die alte tamil.de wird **nur gelesen**. Ziel ist die neue Website (Coolify-App „tamil-web“), Zugriff über das
Anwendungspasswort „migration“ des Admins (`MIGRATION_APP_PASSWORD`, nie ausgeben).

## Bausteine im Repo

| Was | Wo |
|---|---|
| Export der alten Seite (REST, nur lesen): Beiträge, Seiten, Medien, Menüs, Inventar, 301-Tabelle | `tools/export_site.py` |
| bereinigter Bestand (63 Beiträge, 6 Seiten, Bilder) | `prototyp/content/posts.json`, `prototyp/static/img/` |
| Import in WordPress über REST (`tamil-radar/v1/beitrag`) | `wordpress/dev/import_prototype.py` |
| 301-Weiterleitungen (CSV) | Plugin `tamil-site` (Weiterleitungen), Ziele `/category/<slug>/` |

## Anforderungen

- **Originaldatum** (`datum_original`) und **Original-Slug** je Beitrag; Kategorien wie auf der alten Seite
  (abgebildet auf die neuen Rubriken).
- Beitragsbild und Bilder im Text als Medien in der neuen Seite, mit Alt-Text, wo vorhanden.
- Seiten (Kontakt, Impressum, Datenschutz, Werben …) mit echtem Text; Beispielwerte (Telefon, E-Mail, WhatsApp-Nummer)
  **nicht** übernehmen, sondern leer lassen und melden.
- 301 von jeder alten URL auf die neue (gleicher Slug → gleiche URL ist der Normalfall).
- **Idempotent:** zweiter Lauf legt nichts doppelt an (Abgleich über Slug bzw. `radar_uid`).
- Keine Demo-Inhalte (keine erfundenen Events, keine Platzhalter-Beiträge).

## Prüfliste (Ergebnis an Luis)

| Prüfung | Soll |
|---|---|
| Anzahl Beiträge | = Bestand (63 im bereinigten Snapshot; vollständiger Export: Zahl aus `export_site.py`) |
| Stichprobe 10 Beiträge | Datum, Slug, Kategorie, Bild, Text wie alt |
| Seiten | alle vorhanden, keine Beispielwerte |
| Weiterleitungen | 10 alte URLs → 301 auf das richtige Ziel |
| Medien | keine leeren Bilder (`node tools/shots.mjs` auf Start, Rubrik, 3 Artikel) |
| Doppelt | zweiter Lauf: 0 neu angelegt |

## Stolperfallen

- Anwendungspasswörter funktionieren nur über HTTPS.
- Große Bilder: das Theme braucht ≥ 1200 px Breite für Aufmacher; kleinere Originale nicht hochskalieren, sondern
  melden.
- Der bereinigte Snapshot (63) ist eine Auswahl; ob der volle Bestand (533 Beiträge laut Export) übernommen wird,
  entscheidet Luis – vor dem Lauf fragen, Standard: voller Bestand („alles übernehmen“, 09.11.).
