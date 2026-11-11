"""Gemeinsames für die Integrationstests gegen ein laufendes WordPress (wordpress/dev/setup.sh + serve.sh).

Die Tests laufen nur, wenn die Zugänge gesetzt sind (stehen in $WP_DIR/.env.local, `set -a; . .env.local; set +a`):
- WP_TEST_URL, WP_TEST_USER, WP_TEST_APP_PASSWORD – Radar-Benutzer (Fixture `wp`)
- WP_ADMIN_USER, WP_ADMIN_APP_PASSWORD – Admin für REST und Aufräumen (Fixture `wp_admin`)
- WP_ADMIN_PASSWORD – Admin-Passwort für eine angemeldete Browser-Sitzung (Fixture `wp_sitzung`)
- WP_TEST_WP_CLI – Aufruf von wp-cli, z. B. "php …/wp-cli.phar --path=… --allow-root" (Fixture `wp_cli`)
Ohne sie werden die Tests übersprungen.
"""

import os
import shlex
import subprocess
from dataclasses import dataclass

import pytest
import requests
from wp_umgebung import ADMIN_PW, ADMIN_USER, PW, URL, USER, WP_CLI


@dataclass
class WP:
    url: str
    user: str
    pw: str

    @property
    def auth(self) -> tuple[str, str]:
        return (self.user, self.pw)

    def get(self, pfad: str, **kw) -> requests.Response:
        kw.setdefault("timeout", 30)
        return requests.get(self.url + pfad, **kw)


@pytest.fixture
def wp() -> WP:
    if not (URL and USER and PW):
        pytest.skip("WP_TEST_URL/WP_TEST_USER/WP_TEST_APP_PASSWORD fehlen")
    return WP(URL, USER, PW)


@pytest.fixture
def wp_admin(wp) -> tuple[str, str]:
    if not (ADMIN_USER and ADMIN_PW):
        pytest.skip("WP_ADMIN_USER/WP_ADMIN_APP_PASSWORD fehlen")
    return (ADMIN_USER, ADMIN_PW)


def _cli(code: str) -> str:
    return subprocess.run([*shlex.split(WP_CLI), "eval", code], capture_output=True, text=True, check=True).stdout


@pytest.fixture
def wp_cli(wp):
    """Führt PHP im lokalen WordPress aus (wp eval) und gibt die Ausgabe zurück."""
    if not WP_CLI:
        pytest.skip("WP_TEST_WP_CLI (Aufruf von wp-cli) fehlt")
    return _cli


@pytest.fixture
def wp_sitzung(wp) -> requests.Session:
    """Angemeldete Browser-Sitzung des Admins (Cookies wie im Browser, nicht über Anwendungspasswort)."""
    passwort = os.environ.get("WP_ADMIN_PASSWORD", "")
    if not passwort:
        pytest.skip("WP_ADMIN_PASSWORD fehlt")
    s = requests.Session()
    s.get(f"{URL}/wp-login.php", timeout=30)
    r = s.post(f"{URL}/wp-login.php", data={"log": ADMIN_USER or "admin", "pwd": passwort, "testcookie": "1",
                                            "redirect_to": f"{URL}/wp-admin/"}, allow_redirects=False, timeout=30)
    assert r.status_code == 302 and any(n.startswith("wordpress_logged_in") for n in s.cookies.keys())  # noqa: SIM118, "Anmeldung fehlgeschlagen"
    return s


@pytest.fixture
def funktion(wp_cli):
    """Schaltet Bausteine für die Dauer eines Tests ein (Option tamil_site_funktionen) und stellt danach den alten
    Stand wieder her."""
    alt = _cli("echo wp_json_encode( get_option( 'tamil_site_funktionen', array() ) );")

    def an(*namen: str) -> None:
        werte = ",".join(f"'{n}'=>true" for n in namen)
        _cli(f"update_option( 'tamil_site_funktionen', array_merge( (array) get_option( 'tamil_site_funktionen', array() ), array({werte}) ) );")

    yield an
    _cli(f"update_option( 'tamil_site_funktionen', json_decode( '{alt or '[]'}', true ) ?: array() );")
