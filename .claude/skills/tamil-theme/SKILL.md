---
name: tamil-theme
description: Ein abgenommenes Design (Tor G3, design/tokens.css, DESIGN.md) ins WordPress-Theme wordpress/themes/tamil übertragen – theme.json, theme.css, Template-Parts, Schriften – und lokal prüfen. Vorgeladen im theme-bauer; gilt für /design-umsetzung.
user-invocable: false
---

# Design → WordPress-Theme

Quelle der Wahrheit: `design/tokens.css`, `DESIGN.md` und die abgenommene Probeseite
`design/richtungen/<slug>/seiten/`. Nichts daraus 1:1 kopieren; das Theme bleibt WordPress-gerecht (WPCS, Escaping,
Customizer, Gutenberg).

## Wo was liegt

| Was | Datei |
|---|---|
| Farben, Schriften, Größen, Abstände | `wordpress/themes/tamil/theme.json` (Palette, `fontFamilies` mit `fontFace` und `file:./assets/fonts/…`, `fontSizes`, `spacing`) |
| Stile | `assets/css/theme.css` (Abschnitte: Tokens → Basis → Knöpfe → Kopf → Karten → Startseite → Artikel → Kalender → Anzeigen → Fuß → Gutenberg → Breakpoints) |
| Editor-Stile | `assets/css/editor.css` |
| Schriften | `assets/fonts/*.woff2` + Lizenzdatei; Preload in `inc/enqueue.php` |
| Startseite | `front-page.php` + `template-parts/home/*.php` |
| Kopf/Fuß | `header.php`, `template-parts/header/*`, `footer.php` |
| Artikel | `single.php`, `template-parts/article/*` |
| Karten | `template-parts/card.php`, `template-parts/event-card.php` |
| Seiten | `page-events.php`, `page-kontakt.php`, `category.php`, `search.php`, `404.php` |
| JS | `assets/js/app.js` (klein halten, ohne Abhängigkeiten) |

## Ablauf

1. Tokens aus `design/tokens.css` in `theme.json` (Palette, Schriften) und als `:root`-Variablen in `theme.css`
   (die `--wp--preset--*` lesen).
2. Bausteine der Probeseite auf die vorhandenen Template-Parts abbilden; fehlende Teile neu anlegen, Markup
   semantisch, alle Ausgaben escapt.
3. Schriften selbst hosten (woff2 + Lizenz), alte Schriften entfernen, Preload anpassen.
4. Lokal prüfen:
   ```bash
   bash wordpress/dev/setup.sh && bash wordpress/dev/serve.sh &      # einmal; WP_DIR siehe Skript
   set -a; . "$WP_DIR/.env.local"; set +a
   python wordpress/dev/import_prototype.py --wp-cli "php $WP_DIR/wp-cli.phar --path=$WP_DIR --allow-root"
   bash wordpress/dev/lint.sh
   python wordpress/dev/shots.py --out <scratch>/wpshots     # oder node tools/shots.mjs <urls>
   ```
5. Vergleich mit der Probeseite: gleiche Kacheln nebeneinander; jede sichtbare Abweichung begründen oder beheben.
6. Version in `style.css` erhöhen (Minor), Commit `feat(theme): …` je Baustein.

## Stolperfallen

- Customizer-Werte (Kontakt, Social) erscheinen nur, wenn gesetzt – Beispielwerte nie als echt einbauen.
- Werbeplätze kommen aus dem Plugin `tamil-site`; Optik im Theme, Logik im Plugin lassen.
- Plugins nicht für Optik ändern. Wenn doch nötig: Test in `tests/wp/`.
- PHPCS meckert über ungeescapte Ausgaben und fehlende Textdomain `tamil`.
