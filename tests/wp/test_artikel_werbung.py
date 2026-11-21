"""Werbeflächen auf Beiträgen nach Länge (Prüfung 21.11., N-06): Die Anzeige im Text steht erst ab fünf Absätzen;
kurze Beiträge zeigen keine Anzeige im Text und keinen Fuß-Platz, also in jeder Breite höchstens zwei Flächen
(am Handy Leaderboard und Handy-Leiste, ab 768 px nur das Leaderboard, ab 1024 px Half Page und Leaderboard).
Ein von der Redaktion per [tamil_anzeige] gesetzter Platz bleibt stehen.

Gegen ein lokales WordPress (wordpress/dev/setup.sh + serve.sh).
"""

import json
import re

import pytest
import requests
from wp_umgebung import URL


def _absaetze(wp_cli, html: str) -> int:
    return int(wp_cli(f"echo tamil_site_artikel_absaetze( {html!r} );").strip())


def test_absaetze_zaehlen_nur_text(wp_cli):
    assert _absaetze(wp_cli, "<p>Eins</p><p> </p><p>&nbsp;</p><p>Zwei <a href=\"#\">Link</a></p>") == 2
    assert _absaetze(wp_cli, "<p>Text</p><p class=\"quelle\">Quelle: X</p>") == 1
    # ohne <p>: wie wpautop (Zeilenumbrüche in PHP gebaut, repr() gäbe ein wörtliches \n)
    code = "echo tamil_site_artikel_absaetze( implode( \"\\n\\n\", array( 'Erster Absatz.', 'Zweiter.', 'Dritter.' ) ) );"
    assert int(wp_cli(code).strip()) == 3


def test_regel_nach_laenge(wp_cli):
    for zahl in (0, 1, 4):
        plaetze = wp_cli(f"echo implode( ',', tamil_site_artikel_plaetze( {zahl} ) );").strip().split(",")
        assert "inarticle" not in plaetze and "footer" not in plaetze, zahl
        assert {"leaderboard", "sidebar", "mobile"} <= set(plaetze), zahl
    for zahl in (5, 12):
        plaetze = wp_cli(f"echo implode( ',', tamil_site_artikel_plaetze( {zahl} ) );").strip().split(",")
        assert {"inarticle", "footer", "leaderboard", "sidebar", "mobile"} <= set(plaetze), zahl


@pytest.fixture
def beitraege(wp_cli, seite_production):
    """Beiträge mit 4, 5 und 2 Absätzen (der letzte mit [tamil_anzeige] der Redaktion), danach entfernt."""
    ids = {}
    for slug, zahl, zusatz in (("werbung-kurz", 4, ""), ("werbung-lang", 5, ""), ("werbung-redaktion", 2, "[tamil_anzeige]")):
        text = "".join(f"<p>Absatz {i} " + "Wort " * 30 + "</p>" for i in range(1, zahl + 1)) + zusatz
        ids[slug] = int(wp_cli("echo (int) wp_insert_post( array( 'post_status' => 'publish', 'post_title' => 'Werbeprobe',"
                               f" 'post_name' => '{slug}', 'post_content' => '{text}' ) );").strip())
    yield ids
    for pid in ids.values():
        wp_cli(f"wp_delete_post( {pid}, true );")


def _plaetze(slug: str) -> list[str]:
    html = requests.get(f"{URL}/{slug}/", timeout=30).text
    return re.findall(r'<aside class="ad ad-([a-z]+)', html)


def test_kurzer_beitrag_hoechstens_zwei_flaechen(wp, beitraege):
    plaetze = _plaetze("werbung-kurz")
    assert "inarticle" not in plaetze and "footer" not in plaetze, plaetze
    # sichtbar je Breite: Handy (unter 768) ohne Half Page, ab 768 ohne Handy-Leiste, ab 1024 ohne Handy-Leiste
    for sichtbar in (set(plaetze) - {"sidebar"}, set(plaetze) - {"sidebar", "mobile"}, set(plaetze) - {"mobile"}):
        assert len(sichtbar) <= 2, (sichtbar, plaetze)


def test_langer_beitrag_mit_anzeige_im_text(wp, beitraege):
    html = requests.get(f"{URL}/werbung-lang/", timeout=30).text
    assert 'class="ad ad-inarticle' in html
    # nach dem zweiten Absatz
    vor = html[: html.index('class="ad ad-inarticle')]
    assert "Absatz 2 " in vor and "Absatz 3 " not in vor


def test_platz_der_redaktion_bleibt(wp, beitraege):
    assert "inarticle" in _plaetze("werbung-redaktion")


def test_werben_nennt_die_regel(wp_cli):
    """Die Seite „Werben“ verspricht nichts, was die Regel nicht hält (N-06)."""
    wo = {k: v["wo"] for k, v in json.loads(wp_cli("echo wp_json_encode( tamil_site_werbung_formate() );")).items()}
    assert "ab fünf Absätzen" in wo["inarticle"]
    assert "außer kurzen Artikeln" in wo["footer"]
