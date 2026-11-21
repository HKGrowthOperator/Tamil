"""Werbeplätze auf Beiträgen wie in Festlegung F3 (docs/vertrag/festlegung-werbung.md): „Im Artikel“ nach dem zweiten
Absatz ohne Mindestlänge, „Fuß“ über dem Fuß jeder Seite – auch bei kurzen Artikeln. Die Seite „Werben“ nennt die
Plätze mit dem Wortlaut der Festlegung. (Der Vorschlag N-06, kurze Artikel mit weniger Flächen, ist nicht umgesetzt.)

Gegen ein lokales WordPress (wordpress/dev/setup.sh + serve.sh).
"""

import json
import re

import pytest
import requests
from wp_umgebung import URL


@pytest.fixture
def beitraege(wp_cli, seite_production):
    """Beiträge mit 1, 2 und 6 Absätzen, danach entfernt."""
    ids = {}
    for slug, zahl in (("f3-ein-absatz", 1), ("f3-zwei-absaetze", 2), ("f3-sechs-absaetze", 6)):
        text = "".join(f"<p>Absatz {i} " + "Wort " * 30 + "</p>" for i in range(1, zahl + 1))
        ids[slug] = int(wp_cli("echo (int) wp_insert_post( array( 'post_status' => 'publish', 'post_title' => 'F3-Probe',"
                               f" 'post_name' => '{slug}', 'post_content' => '{text}' ) );").strip())
    yield ids
    for pid in ids.values():
        wp_cli(f"wp_delete_post( {pid}, true );")


def _html(slug: str) -> str:
    return requests.get(f"{URL}/{slug}/", timeout=30).text


def _nach_dem_zweiten_absatz(html: str) -> bool:
    vor = html[: html.index('class="ad ad-inarticle')]
    return "Absatz 2 " in vor and "Absatz 3 " not in vor


@pytest.mark.parametrize("slug", ["f3-zwei-absaetze", "f3-sechs-absaetze"])
def test_im_artikel_nach_dem_zweiten_absatz_ohne_mindestlaenge(wp, beitraege, slug):
    html = _html(slug)
    assert html.count('class="ad ad-inarticle') == 1, slug
    assert _nach_dem_zweiten_absatz(html), slug


def test_ohne_zweiten_absatz_kein_platz_im_text(wp, beitraege):
    assert 'class="ad ad-inarticle' not in _html("f3-ein-absatz")


@pytest.mark.parametrize("slug", ["f3-ein-absatz", "f3-zwei-absaetze", "f3-sechs-absaetze"])
def test_fuss_auf_jeder_seite_auch_bei_kurzen_artikeln(wp, beitraege, slug):
    assert re.search(r'<aside class="ad ad-footer', _html(slug)), slug


def test_werben_nennt_die_plaetze_wie_die_festlegung(wp_cli):
    wo = {k: v["wo"] for k, v in json.loads(wp_cli("echo wp_json_encode( tamil_site_werbung_formate() );")).items()}
    assert wo["inarticle"] == "im Artikel nach dem zweiten Absatz"
    assert wo["footer"] == "über dem Fuß jeder Seite"
