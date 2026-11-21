"""Ein Radius (TML-W05): `design/tokens.css` und das Theme (`assets/css/theme.css`) führen dieselben Werte für
`--radius` und `--radius-klein`. Reiner Dateitest, braucht kein WordPress."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKENS = ROOT / "design" / "tokens.css"
THEME = ROOT / "wordpress" / "themes" / "tamil" / "assets" / "css" / "theme.css"
NAMEN = ("--radius", "--radius-klein")


def _werte(datei: Path) -> dict[str, list[str]]:
    """Alle Festlegungen der Radius-Variablen in einer Datei (jede Stelle, damit auch eine zweite, abweichende auffällt)."""
    text = re.sub(r"/\*.*?\*/", "", datei.read_text(encoding="utf-8"), flags=re.S)
    return {name: re.findall(rf"(?<![\w-]){re.escape(name)}\s*:\s*([^;}}]+)", text) for name in NAMEN}


def test_radien_in_tokens_und_theme_gleich():
    tokens, theme = _werte(TOKENS), _werte(THEME)
    for name in NAMEN:
        assert tokens[name], f"{name} fehlt in design/tokens.css"
        assert theme[name], f"{name} fehlt in theme.css"
        assert {w.strip() for w in tokens[name]} == {w.strip() for w in theme[name]}, f"{name}: Tokens {tokens[name]}, Theme {theme[name]}"


def test_radien_sind_die_abgenommenen_werte():
    werte = _werte(TOKENS)
    assert [w.strip() for w in werte["--radius"]] == ["10px"] and [w.strip() for w in werte["--radius-klein"]] == ["6px"]
