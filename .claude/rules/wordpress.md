---
paths:
  - "wordpress/**"
---

# Regeln: WordPress (Theme und Plugins)

- **WPCS:** escapen bei der Ausgabe (`esc_html`, `esc_attr`, `esc_url`, `wp_kses_post`), bereinigen bei der Eingabe,
  Nonces und Rechteprüfung in Admin- und REST-Routen. `bash wordpress/dev/lint.sh` muss sauber sein.
- **Plugins** (`tamil-radar`, `tamil-site`) nur mit Test in `tests/wp/` ändern; der Radar hängt an der
  REST-Schnittstelle von `tamil-radar`.
- **Theme-Umbauten** am Aussehen nur nach Tor G3 und über `/design-umsetzung` (siehe `.claude/rules/design.md`).
- **Schriften selbst gehostet** in `themes/tamil/assets/fonts/` mit Lizenzdatei, eingebunden über `theme.json`
  (`fontFace`). Keine externen Font-CDNs.
- **Lokal prüfen:** `bash wordpress/dev/setup.sh`, `bash wordpress/dev/serve.sh &`, Import über
  `wordpress/dev/import_prototype.py`, Screenshots mit `wordpress/dev/shots.py` oder `node tools/shots.mjs`.
- **Container:** `wordpress/Dockerfile` und `wordpress/docker/start.sh` sind idempotent; Code kommt bei jedem Start frisch
  aus dem Image, persistent sind nur `uploads/` und `database/`. Geheimnisse nur über Variablen.
- **Die echte tamil.de** wird nie beschrieben. Migration liest dort nur (`tools/export_site.py`).
