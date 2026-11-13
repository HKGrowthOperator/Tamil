"""WordPress-Container (wordpress/docker/start.sh, wordpress/Dockerfile): Einstellungen für die Einsendungen (F1).

Ohne Docker: Die Prüfung der Variable TAMIL_PROXY_ANZAHL wird aus start.sh herausgelöst und mit bash ausgeführt; die
Apache-Sperre für eingesandte Bilder wird im Dockerfile gesucht.
"""

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
START = (ROOT / "wordpress/docker/start.sh").read_text(encoding="utf-8")
DOCKERFILE = (ROOT / "wordpress/Dockerfile").read_text(encoding="utf-8")


def _proxy_zeilen() -> str:
    zeilen = [z for z in START.splitlines() if z.startswith(("TAMIL_PROXY_ANZAHL=", '[[ "$TAMIL_PROXY_ANZAHL"'))]
    assert len(zeilen) == 2, zeilen
    return "\n".join(zeilen)


@pytest.mark.parametrize("wert,erwartet", [(None, "0"), ("1", "1"), ("2", "2")])
def test_proxy_anzahl_gueltig(wert, erwartet):
    env = {"PATH": "/usr/bin:/bin"} | ({"TAMIL_PROXY_ANZAHL": wert} if wert is not None else {})
    skript = 'fehler() { echo "FEHLER: $*"; exit 3; }\n' + _proxy_zeilen() + '\necho "$TAMIL_PROXY_ANZAHL"'
    r = subprocess.run(["bash", "-c", skript], env=env, capture_output=True, text=True, check=False)
    assert r.returncode == 0 and r.stdout.strip() == erwartet


@pytest.mark.parametrize("wert", ["-1", "10", "1; echo boese", "eins", " 1"])
def test_proxy_anzahl_ungueltig_bricht_ab(wert):
    skript = 'fehler() { echo "FEHLER: $*"; exit 3; }\n' + _proxy_zeilen() + '\necho "$TAMIL_PROXY_ANZAHL"'
    r = subprocess.run(["bash", "-c", skript], env={"PATH": "/usr/bin:/bin", "TAMIL_PROXY_ANZAHL": wert},
                       capture_output=True, text=True, check=False)
    assert r.returncode == 3 and "TAMIL_PROXY_ANZAHL" in r.stdout


def test_proxy_anzahl_landet_in_wp_config():
    assert "define( 'TAMIL_PROXY_ANZAHL', $TAMIL_PROXY_ANZAHL );" in START
    # die Konstante steht vor wp-settings.php (sonst sieht das Plugin sie nicht)
    assert START.index("define( 'TAMIL_PROXY_ANZAHL'") < START.index("require_once ABSPATH . 'wp-settings.php';")
    assert "TAMIL_PROXY_ANZAHL" in (ROOT / "docs/betrieb.md").read_text(encoding="utf-8")


def test_apache_sperrt_eingesandte_bilder():
    block = re.search(r"<Directory /var/www/html/wp-content/uploads/tamil-einsendungen>'; \\\s*echo '\s*Require all denied'",
                      DOCKERFILE)
    assert block, "Apache-Sperre für uploads/tamil-einsendungen fehlt"
