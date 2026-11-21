"""Formate der Werbeplätze aus einer Konfiguration (Prüfung 17.11., P1-8): Die Tabelle auf „Werben“, die Labels in den
Einstellungen, die Prüfung hochgeladener Werbemittel, das Umschalten zwischen Desktop- und Handy-Bild gebuchter Anzeigen
und die Darstellung (CSS) kommen alle aus tamil_site_werbung_formate(). Gemessen wird im Browser bei 390, 820 und
1280 px: Jede Fläche hat das Seitenverhältnis des angegebenen Formats und die angegebene Breite (am Handy über die
Spaltenbreite, höchstens 20 % größer).

Gegen ein lokales WordPress (wordpress/dev/setup.sh + serve.sh); die Messung braucht Playwright (sonst übersprungen).
"""

import json
import re

import pytest
import requests
from wp_umgebung import URL


def _formate(wp_cli) -> dict:
    return json.loads(wp_cli("echo wp_json_encode( tamil_site_werbung_formate() );"))


def test_formate_wie_mit_dem_theme_abgestimmt(wp_cli):
    f = _formate(wp_cli)
    assert list(f) == ["leaderboard", "sidebar", "inarticle", "billboard", "footer", "mobile"]
    erwartet = {
        "leaderboard": ([728, 90], [320, 100], 768),
        "sidebar": ([300, 600], [300, 600], 0),
        "inarticle": ([336, 280], [336, 280], 0),
        "billboard": ([970, 250], [336, 280], 1024),
        "footer": ([728, 90], [320, 100], 768),
        "mobile": ([320, 50], [320, 50], 0),
    }
    for platz, (desktop, mobil, ab) in erwartet.items():
        assert (f[platz]["desktop"], f[platz]["mobil"], f[platz]["ab"]) == (desktop, mobil, ab), platz
    assert "unter der Navigation" not in f["leaderboard"]["wo"]


def test_tabelle_und_labels_aus_der_konfiguration(wp_cli):
    texte = json.loads(wp_cli("$t = array(); foreach ( array_keys( tamil_site_werbung_formate() ) as $p ) {"
                              " $t[ $p ] = array( tamil_site_werbung_masse_text( $p ), tamil_site_werbeplaetze()[ $p ] ); } echo wp_json_encode( $t );")
                       .replace("\\u00a0", " "))  # geschützte Leerzeichen wie normale lesen
    assert "\u00a0" in wp_cli("echo tamil_site_werbung_masse_text( 'inarticle' );")  # 336 × 280 bricht nicht um
    assert texte["leaderboard"][0] == "728 × 90, unter 768 px Breite 320 × 100"
    assert texte["inarticle"][0] == "336 × 280"
    assert texte["billboard"][0] == "970 × 250, unter 1024 px Breite 336 × 280"
    for platz, (masse, label) in texte.items():
        assert masse in label, platz  # Einstellungen nennen dieselben Maße
    css = wp_cli("echo tamil_site_anzeigen_formate_css();")
    assert "aspect-ratio:728/90" in css and "aspect-ratio:320/100" in css and "aspect-ratio:336/280" in css
    assert "@media (min-width:768px)" in css and "@media (min-width:1024px)" in css
    assert "aspect-ratio:300/250" not in css
    assert not re.search(r"\.ad\.ad-leaderboard[^{}]*\{[^}]*aspect-ratio:320/50", css)  # Handy-Leaderboard ist 320 × 100


def test_gebuchte_anzeige_wechselt_das_bild_an_derselben_grenze(wp_cli):
    """<source media> der gebuchten Anzeige folgt der Grenze aus der Konfiguration (unter 768 px das Handy-Bild)."""
    code = wp_cli("echo tamil_site_werbung_picture_quelle( 'leaderboard', 'https://example.test/m.png' );")
    assert 'media="(max-width: 767px)"' in code and 'width="320" height="100"' in code
    assert wp_cli("echo tamil_site_werbung_picture_quelle( 'inarticle', 'https://example.test/m.png' );") == ""


def test_seite_werben_nennt_die_formate(wp, wp_cli):
    seite = wp_cli("$p = get_page_by_path( 'werben-formate-test', OBJECT, 'page' ); if ( $p ) { wp_delete_post( $p->ID, true ); }"
                   " echo (int) wp_insert_post( array( 'post_type' => 'page', 'post_status' => 'publish', 'post_name' => 'werben-formate-test',"
                   " 'post_title' => 'Werben (Formate)', 'post_content' => '[tamil_werbung]' ) );")
    try:
        html = requests.get(f"{URL}/werben-formate-test/", headers={"X-Tamil-Funktionen": "werbung"}, timeout=30).text
        zeile = re.search(r'<tr><th scope="row">Leaderboard</th>.*?</tr>', html, re.S)
        if not zeile:
            pytest.skip("Seite Werben lokal ohne Tabelle (Schalter aus)")
        assert "728 × 90, unter 768 px Breite 320 × 100" in zeile.group(0).replace("\u00a0", " ").replace("&nbsp;", " ")
        assert "unter dem ersten Abschnitt jeder Seite" in zeile.group(0)
        assert "füllen Banner die Breite der Spalte" in html
    finally:
        wp_cli(f"wp_delete_post( {int(seite)}, true );")


# --- Messung im Browser -------------------------------------------------------------------------------------------

def _playwright():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("Playwright für Python fehlt")
    return sync_playwright


@pytest.fixture
def artikel(wp_cli, seite_production):
    """Ein Artikel mit vier Absätzen (Platz „Im Artikel“), danach entfernt."""
    text = "".join(f"<p>Absatz {i} " + "Wort " * 40 + "</p>" for i in range(1, 6))
    pid = int(wp_cli("echo (int) wp_insert_post( array( 'post_status' => 'publish', 'post_title' => 'Formatprobe',"
                     f" 'post_name' => 'formatprobe-werbung', 'post_content' => '{text}' ) );").strip())
    yield f"{URL}/formatprobe-werbung/"
    wp_cli(f"wp_delete_post( {pid}, true );")


def test_darstellung_hat_die_angegebenen_formate(wp, wp_cli, artikel):
    sync_playwright = _playwright()
    formate = _formate(wp_cli)
    messung = []
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Exception as fehler:  # noqa: BLE001 – ohne Browser keine Messung
            pytest.skip(f"Chromium nicht startbar: {fehler}")
        for breite in (390, 820, 1280):
            seite = browser.new_page(viewport={"width": breite, "height": 900})
            for url in (URL + "/", artikel):
                seite.goto(url, wait_until="networkidle")
                seite.evaluate("document.querySelector('#ad-mobile')?.classList.add('ist-sichtbar')")
                for platz, w, h in seite.evaluate("""() => [...document.querySelectorAll('.ad.ad-bild')].map(a => {
                        const f = a.querySelector('.anzeige-wrap'); const r = f.getBoundingClientRect();
                        return [a.dataset.platz, r.width, r.height]; }).filter(x => x[1] > 0)"""):
                    messung.append((breite, platz, w, h))
            seite.close()
        browser.close()
    assert messung, "keine Werbefläche gemessen"
    for breite, platz, w, h in messung:
        f = formate[platz]
        fw, fh = f["desktop"] if f["ab"] and breite >= f["ab"] else f["mobil"]
        assert abs(w / h - fw / fh) < 0.03, (breite, platz, w, h, fw, fh)
        if breite >= 600:
            assert abs(w - fw) <= 1 or w < fw, (breite, platz, w, fw)  # nie größer als angegeben
        else:
            assert w <= fw * 1.2 + 1 and (w >= fw - 1 or w >= breite - 2 * 16 - 1), (breite, platz, w, fw)
    gemessen = {(b, p) for b, p, _, _ in messung}
    for erwartet in ((390, "leaderboard"), (1280, "leaderboard"), (390, "billboard"), (1280, "billboard"), (390, "inarticle"),
                     (1280, "sidebar"), (390, "mobile"), (390, "footer"), (820, "footer")):
        assert erwartet in gemessen, erwartet


def test_werben_zeigt_je_platz_eine_skizze(wp, wp_cli, seite_production):
    """N-07: Jede Zeile der Tabelle zeigt eine Skizze mit der markierten Fläche des Platzes (dekorativ)."""
    html = requests.get(f"{URL}/werben/", timeout=30).text
    plaetze = list(_formate(wp_cli))
    skizzen = re.findall(r'<svg class="wb-skizze" data-platz="([a-z]+)"[^>]*aria-hidden="true"', html)
    assert skizzen == plaetze
    assert html.count('class="wb-skizze__flaeche"') == len(plaetze)
    assert wp_cli("echo tamil_site_werbung_skizze( 'gibt-es-nicht' );") == ""
