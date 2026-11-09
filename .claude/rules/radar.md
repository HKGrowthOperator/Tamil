---
paths:
  - "news_radar/**"
  - "sources.toml"
  - "tests/**"
  - "requirements.txt"
  - "Dockerfile"
---

# Regeln: News-Radar und Cockpit

- **Tests ohne Netz und ohne echte Modelle:** `FakeClaude` (`news_radar/workflow/fake.py`) und Fake-Transporte. Kein
  Test darf `api.anthropic.com` oder eine echte Quelle aufrufen.
- **Neue Funktion = neuer Test zuerst** (`tests/test_<bereich>.py`). Fehler aus dem Live-Betrieb bekommen einen
  Regressionstest mit dem echten Fall als Fixture.
- **Nur `providers.Claude.call()` ruft Anthropic auf.** Jeder Aufruf wird nach `agent_usage` geschrieben; Kosten über
  `workflow/costs.py`, Budget über Reservierung vor dem Aufruf.
- **Gate:** Kernaussagen nur aus bestätigten Claims; Belege je Absatz; Links im Text nur, wenn sie in den
  `source_documents` stehen. Nie lockern, um einen Test grün zu bekommen.
- **Netz nur über `net.safe_get`** (SSRF-Schutz, Redirect-Prüfung, Größenlimit).
- **Cockpit:** HTML aus Entwürfen immer durch `render.sanitize_html` (nh3), externe Links durch `safe_url`. CSP ohne
  Inline-Script und ohne Inline-Event-Handler; Verhalten gehört in `static/app.js`.
- **Prompts** liegen als Markdown in `news_radar/prompts/`; die Version ist der Hash des Inhalts.
- **Schema-Änderungen** nur als neue Migration in `workflow/schema.py` (`MIGRATIONS`), nie bestehende ändern.
- **Fertig:** `python -m pytest -q` und `python -m news_radar abnahme` (51/51).
