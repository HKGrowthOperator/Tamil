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
| Import des vollen Exports in WordPress über REST, idempotent, mit Bericht | `tools/migration.py` (Tests `tests/test_migration.py`) |
| Import des Prototyp-Schnappschusses (63 Beiträge, nur lokal) | `wordpress/dev/import_prototype.py` |
| 301-Weiterleitungen (CSV) | Plugin `tamil-site` (Weiterleitungen), Ziele `/category/<slug>/` |

## Live-Lauf

```bash
python tools/migration.py --export <export-ordner> --url https://tamil-web.167.233.76.202.sslip.io \
  --benutzer <admin> --passwort-datei <datei mit Rechten 600> --bericht <bericht.json>
```

`--trocken` schreibt nichts, `--limit N` begrenzt die Beiträge, `--nur weiterleitungen` baut nur die 301-Tabelle.
Rückgabecodes: 0 fertig · 2 Ziel abgelehnt · 3 Bilder fehlen, die ein neuer Lauf nachziehen kann · 4 Vorabprüfung des
Ziels gescheitert. Schutz der alten Seite: Das Ziel wird wie bei `requests` normalisiert und gegen eine Positivliste
geprüft (die Vorschau-Adresse und lokale Adressen; jeder andere Host nur mit `--ziel-host`), `tamil.de` samt
Unterdomains ist immer gesperrt, die Sitzung folgt keinen Weiterleitungen, und vor dem ersten Schreiben muss am Ziel
die neue Website antworten (Namensräume `tamil-radar/v1` und `tamil-site/v1`). Bilder werden nur lesend über https
von `tamil.de` und `www.tamil.de` geholt.

## Anforderungen

- **Originaldatum** (`datum_original`) und **Original-Slug** je Beitrag; Kategorien wie auf der alten Seite
  (abgebildet auf die neuen Rubriken).
- Beitragsbild und Bilder im Text als Medien in der neuen Seite, mit Alt-Text, wo vorhanden.
- Seiten (Kontakt, Impressum, Datenschutz, Werben …) mit echtem Text. Texte der alten Seite bleiben unverändert,
  auch Kontaktangaben darin (`info@tamil.de` ist die echte Adresse der alten Seite). Die Kontaktfelder der neuen
  Website (Customizer) werden **nie** mit den Beispielwerten aus `prototyp/content/site.json` gefüllt; sie bleiben
  leer, bis der Auftraggeber die echten Werte nennt.
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
- Der bereinigte Snapshot (63) ist eine Auswahl. Übernommen wird der volle Bestand (Luis, 09.11.: „alles
  übernehmen“): 533 Beiträge im Export, davon 3 Testbeiträge nicht, dazu 2 Seiten als Beiträge, also 532.
- Bekannt aus dem Probelauf (10.11.): Das Impressum der alten Seite ist leer; zwei Bilder im Text gibt es auf der
  alten Seite nicht mehr; ein Beitrag hat kein Beitragsbild; rund 300 Beitragsbilder sind schmaler als 1200 px.
- YouTube-Videos werden zu Einbettungen umgewandelt; das Theme zeigt sie als Box „Video laden“ (erst nach Klick).
