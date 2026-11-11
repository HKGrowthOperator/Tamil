"""wordpress/dev/env_local.sh: Werte in $WP_DIR/.env.local überstehen das dokumentierte Laden
`set -a; . .env.local; set +a` – auch mit Leerzeichen (WP_TEST_WP_CLI). Läuft ohne WordPress."""

import subprocess
from pathlib import Path

HILFE = Path(__file__).resolve().parents[2] / "wordpress" / "dev" / "env_local.sh"


def _bash(skript: str) -> str:
    return subprocess.run(["bash", "-c", skript], capture_output=True, text=True, check=True).stdout


def test_werte_mit_leerzeichen_ueberstehen_das_laden(tmp_path):
    datei = tmp_path / ".env.local"
    wert = f"php {tmp_path}/wp-cli.phar --path={tmp_path} --allow-root"
    ausgabe = _bash(
        f'ENV_LOCAL="{datei}"; . "{HILFE}"; touch "$ENV_LOCAL"\n'
        'setenv WP_TEST_WP_CLI "alt wert"\n'
        f'setenv WP_TEST_WP_CLI "{wert}"\n'
        'setenv WP_TEST_URL "http://127.0.0.1:8085"\n'
        "setenv WP_X 'a$b \"c\" d|e'\n"
        'printf "%s\\n" "$(getenv WP_TEST_WP_CLI)"\n'
        f'( set -a; . "{datei}"; set +a; printf "%s\\n%s\\n%s\\n" "$WP_TEST_WP_CLI" "$WP_TEST_URL" "$WP_X" )\n'
    )
    assert ausgabe.splitlines() == [wert, wert, "http://127.0.0.1:8085", 'a$b "c" d|e']
    assert datei.read_text().count("WP_TEST_WP_CLI=") == 1


def test_setup_nutzt_die_hilfe():
    setup = (HILFE.parent / "setup.sh").read_text()
    assert 'env_local.sh"' in setup and "setenv() {" not in setup
