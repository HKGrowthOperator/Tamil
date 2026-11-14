"""Plugin tamil-site: Eigenanzeigen (ungebuchte Werbeplätze, Festlegung F3) lesen sich wie ein ruhiger Anreißer.

Kein Icon, keine Dachzeile, kein Gedankenstrich, keine „·“-Ketten (Hallmark Gate 19 und Floor 10, Kritik
theme-tageskalender-r1 P1-3 und P1-5); Platz, Kennzeichnung „Anzeige“ und Ziel bleiben.
"""

import json

import pytest

VORLAGEN = ["production", "event", "werben", "whatsapp", "whatsapp-klein"]


def _html(wp_cli, vorlage: str) -> str:
    return wp_cli(f"echo tamil_site_eigenanzeige_html( '{vorlage}' );")


@pytest.mark.parametrize("vorlage", VORLAGEN)
def test_eigenanzeige_ohne_icon_dachzeile_und_striche(wp_cli, vorlage):
    html = _html(wp_cli, vorlage)
    assert html.startswith('<a class="flaeche anzeige-wrap"') and f'class="anzeige a-{vorlage}"' in html
    assert "<svg" not in html and "eyebrow" not in html and 'class="marke"' not in html
    assert "–" not in html and "—" not in html and "·" not in html  # –, —, ·
    assert '<span class="claim">' in html and '<span class="cta">' in html


def test_unbekannte_vorlage_bleibt_leer(wp_cli):
    assert _html(wp_cli, "gibt-es-nicht") == ""


def test_whatsapp_oeffnet_neues_fenster_andere_nicht(wp_cli):
    assert 'target="_blank" rel="noopener"' in _html(wp_cli, "whatsapp")
    assert "target=" not in _html(wp_cli, "werben")


def test_ungebuchter_platz_zeigt_eigenanzeige_mit_label(wp_cli):
    """F3: ein ungebuchter Platz bleibt nicht leer; das Label „Anzeige“ steht dabei."""
    raus = json.loads(wp_cli("echo wp_json_encode( array( tamil_site_anzeige( 'footer', false ), tamil_site_settings()['eigen']['footer'] ) );"))
    html, vorlage = raus
    if not vorlage:
        pytest.skip("Footer-Platz hat lokal keine Eigenanzeige eingestellt")
    if "data-wb-buchung" in html or 'class="flaeche anzeige-wrap"' not in html:
        pytest.skip("Footer-Platz ist lokal gebucht oder mit fremdem Code belegt")
    assert 'class="ad ad-footer ad-anzeige"' in html and '<span class="ad-label">Anzeige</span>' in html
