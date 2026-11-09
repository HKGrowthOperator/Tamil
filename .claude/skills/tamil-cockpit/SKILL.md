---
name: tamil-cockpit
description: Das abgenommene Design ruhig ins Redaktions-Cockpit news_radar/web übertragen (Produkt-Register) – app.css, Jinja-Templates, CSP, Tests, Screenshots mit Anmeldung. Vorgeladen im cockpit-bauer; gilt für /design-umsetzung.
user-invocable: false
---

# Design → Cockpit

Das Cockpit ist ein Werkzeug (impeccable `reference/product.md`): gleiche Tokens und Schriften wie die Website, aber
ruhiger, dichter, Klarheit vor Ausdruck. Eine rote Hauptaktion je Ansicht.

## Wo was liegt

| Was | Datei |
|---|---|
| Stile | `news_radar/web/static/app.css` (eine Datei; Abschnitte: Tokens, Seitenleiste, Inhalt, Feed, Knöpfe, Formulare, Entwurf, Vorschau, Dashboard, Quellen, Protokoll, Login, Redaktion v2, Breakpoints, reduced motion) |
| Verhalten | `news_radar/web/static/app.js` (CSP: kein Inline-Script, keine `on…`-Attribute) |
| Schriften | `news_radar/web/static/fonts/` |
| Seiten | `news_radar/web/templates/*.html` (base, dashboard, feed, entwurf, warteschlange, recherche, quellen, kosten, protokoll, nutzer, login, vorschau, fehler, `_karte`, `_belege`) |
| Vorschau „so sieht es auf tamil.de aus“ | Abschnitt Vorschau in `app.css` – muss nach dem Umbau dem neuen Theme entsprechen |

## Ablauf

1. Tokens aus `design/tokens.css` in den `:root` von `app.css` (keine hart kodierten Farben mehr außerhalb).
2. Schriften austauschen (woff2 in `static/fonts/`, `@font-face` in `app.css`).
3. Ansichten nacheinander anpassen; Inline-`style=` entfernen.
4. Prüfen:
   ```bash
   python -m pytest -q tests/test_web.py tests/test_web_redaktion.py
   WEB_USER=… WEB_PASSWORD=… python -m news_radar web &          # lokal :8787 (Testzugang nur lokal)
   SHOTS_USER=… SHOTS_PASSWORD=… node tools/shots.mjs http://127.0.0.1:8787/ http://127.0.0.1:8787/feed \
        --login http://127.0.0.1:8787/login --out <scratch>/cockpit
   ```
5. Commit `feat(cockpit): …`.

## Stolperfallen

- Die CSP-Tests prüfen den Header; neue externe Quellen (Fonts-CDN) brechen sie – selbst hosten.
- HTML aus Entwürfen läuft durch `render.sanitize_html`; neue Klassen in der Vorschau müssen in der Allowlist
  (`*:class`) erlaubt sein – sind sie.
- Tabellen auf dem Handy in `overflow-x: auto`-Container, nie die Seite verbreitern.
