---
description: Stand von tamil.de auf einen Blick – Radar (Gesundheit, Budget, Warteschlange, Entwürfe), Website, PR, offene Tore. Nur lesen.
allowed-tools: Bash(python tools/radar_bericht.py*), Bash(python tools/coolify.py status*), Bash(curl -fsS*), Bash(curl -fsSI*), Bash(git *), Read, Glob
---

# /status

Nur lesen, nichts ändern.

1. **Radar:** `python tools/radar_bericht.py` (Lese-Token aus `RADAR_LESE_TOKEN` oder `--token-datei`). Ohne Token:
   nur `curl -fsS https://tamil.hk-growthoperator.de/gesund`.
2. **Website:** `curl -fsSI https://tamil-web.167.233.76.202.sslip.io/` (Status, ob angelegt). Mit `COOLIFY_TOKEN`:
   `python tools/coolify.py status`.
3. **Code:** `git status -sb`, `git log --oneline -5`, PR #2 (Titel, Status, Basis) über die GitHub-Werkzeuge.
4. **Tore:** `docs/abnahme/` (welche liegen vor) gegen die Tabelle in `docs/ablaeufe.md`; offene Betriebstore B1–B3
   aus `docs/betrieb.md` (z. B. `ANTHROPIC_API_KEY` offen).

Ausgabe: eine kurze Tabelle System · Stand · Nächster Schritt, darunter höchstens drei Sätze, was als Nächstes ansteht
und wer es tun muss (Claude oder Luis).
