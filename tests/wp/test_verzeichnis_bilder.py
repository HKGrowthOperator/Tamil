"""Verzeichnis mit Bildern (Auftraggeber 17.11.: alles auf der Website hat ein Bild): Liste und Profil zeigen das
Beitragsbild des Eintrags; ohne eigenes Bild ein Symbolbild seiner Art (Firma und Dienstleister, Verein, Tempel),
gekennzeichnet und mit Nachweis im Fuß.

Gegen ein lokales WordPress (wordpress/dev/setup.sh + serve.sh). Der Schalter „verzeichnis“ wird für einzelne Aufrufe
über die Test-Kopfzeile eingeschaltet. Alle Angaben sind erfunden (example.test).
"""

import base64
import html
import io
import json
import re
import secrets

import pytest
import requests
from PIL import Image
from test_verzeichnis import AN, seite  # noqa: F401 (Fixture)

ARTEN = ("business", "dienstleister", "verein", "tempel")


def _jpeg(farbe: tuple[int, int, int]) -> str:
    puffer = io.BytesIO()
    Image.new("RGB", (800, 450), farbe).save(puffer, "JPEG", quality=85)
    return base64.b64encode(puffer.getvalue()).decode()


@pytest.fixture
def eintraege(wp_cli, seite):  # noqa: F811
    """Je Art ein veröffentlichter Eintrag ohne Bild und ein Verein mit Beitragsbild (Alternativtext, Bildunterschrift)."""
    kennung = secrets.token_hex(3)
    ids = {}
    for art in ARTEN:
        ids[art] = int(wp_cli(
            f"echo (int) tamil_site_vz_eintrag_schreiben( 0, array( 'name' => 'Bildprobe {art} {kennung}', 'art' => '{art}',"
            " 'plz' => '44135', 'stadt' => 'Dortmund', 'land' => 'DE', 'email' => 'probe@example.test' ), 'publish' );").strip())
    mit_bild = int(wp_cli(
        f"$id = (int) tamil_site_vz_eintrag_schreiben( 0, array( 'name' => 'Bildprobe mit Foto {kennung}', 'art' => 'verein', 'plz' => '44135',"
        " 'stadt' => 'Dortmund', 'land' => 'DE', 'email' => 'probe@example.test' ), 'publish' );"
        f" $u = wp_upload_bits( 'vz-bildprobe-{kennung}.jpg', null, base64_decode( '{_jpeg((40, 90, 140))}' ) );"
        " require_once ABSPATH . 'wp-admin/includes/image.php';"
        " $a = wp_insert_attachment( array( 'post_mime_type' => 'image/jpeg', 'post_title' => 'Vereinsfoto', 'post_status' => 'inherit',"
        " 'post_excerpt' => 'Foto: Verein Bildprobe' ), $u['file'], $id );"
        " wp_update_attachment_metadata( $a, wp_generate_attachment_metadata( $a, $u['file'] ) );"
        " update_post_meta( $a, '_wp_attachment_image_alt', 'Vereinsfoto der Bildprobe' ); set_post_thumbnail( $id, $a ); echo $id;").strip())
    yield {"ohne": ids, "mit_bild": mit_bild, "kennung": kennung, "seite": seite}
    wp_cli(f"$t = get_post_thumbnail_id( {mit_bild} ); if ( $t ) {{ wp_delete_attachment( $t, true ); }}")


def _li(html: str, name: str) -> str:
    for li in re.findall(r'<li class="vz-eintrag[^"]*">.*?</li>', html, re.S):
        if name in li:
            return li
    raise AssertionError(f"{name} nicht in der Liste")


def _img(teil: str) -> str:
    m = re.search(r"<img[^>]*>", teil)
    assert m, "kein Bild"
    return m.group(0)


def _attr(tag: str, name: str) -> str:
    m = re.search(rf'\s{name}="([^"]*)"', tag)
    return m.group(1) if m else ""


def test_liste_jeder_eintrag_mit_bild(eintraege):
    html = requests.get(eintraege["seite"] + f"?vz_suche=Bildprobe+{eintraege['kennung']}", headers=AN, timeout=30).text
    gesehen = set()
    for art in ARTEN:
        li = _li(html, f"Bildprobe {art} {eintraege['kennung']}")
        assert "vz-mit-bild" in li and 'class="vz-symbolbild">Symbolbild<' in li, art
        img = _img(li)
        assert _attr(img, "alt").startswith("Symbolbild"), img
        assert 'loading="lazy"' in img and _attr(img, "srcset") and _attr(img, "sizes")
        quelle = _attr(img, "src")
        gesehen.add(quelle.rsplit("/", 1)[-1])
        r = requests.get(quelle, timeout=30)
        assert r.status_code == 200 and r.headers["content-type"].startswith("image/") and len(r.content) > 5000, quelle
    assert len(gesehen) == 3, f"je Art ein eigenes Symbolbild (Firma und Dienstleister teilen eins): {gesehen}"
    li = _li(html, f"Bildprobe mit Foto {eintraege['kennung']}")
    img = _img(li)
    assert "vz-bildprobe" in _attr(img, "src") and _attr(img, "alt") == "Vereinsfoto der Bildprobe"
    assert "vz-symbolbild" not in li and 'loading="lazy"' in img and _attr(img, "srcset")
    # Bildlink ist nur Zugabe: nicht im Tab-Weg, für Screenreader verborgen (der Name ist der Link)
    assert re.search(r'<a class="vz-bild" href="[^"]+" tabindex="-1" aria-hidden="true">', li)


def test_profil_symbolbild_mit_nachweis_und_fuss(eintraege):
    liste = requests.get(eintraege["seite"] + f"?vz_suche=Bildprobe+{eintraege['kennung']}", headers=AN, timeout=30).text
    profil = re.search(rf'<a class="vz-name" href="([^"]+)">Bildprobe tempel {eintraege["kennung"]}<', liste).group(1)
    seite = requests.get(profil, headers=AN, timeout=30).text
    figur = re.search(r'<figure class="vz-bild vz-bild--profil">.*?</figure>', seite, re.S)
    assert figur, "Profil ohne Bild"
    assert _attr(_img(figur.group(0)), "alt").startswith("Symbolbild") and "Symbolbild, Foto: Fridolin freudenfett" in figur.group(0)
    assert "Wikimedia Commons" in figur.group(0)
    if "Bildnachweise dieser Seite" in seite:
        fuss = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", seite.split("Bildnachweise dieser Seite", 1)[1])))
        assert "Symbolbild, Foto: Fridolin freudenfett / Wikimedia Commons, CC BY-SA 4.0, zugeschnitten" in fuss
        # Theme 3.3.0 verlinkt nur den Urheber, nicht „Symbolbild, Foto:“
        assert not re.search(r"<a [^>]*>Symbolbild", seite.split("Bildnachweise dieser Seite", 1)[1])


def test_profil_mit_beitragsbild_ein_bild(eintraege, wp_cli):
    """Mit eigenem Bild: genau einmal (zeigt das Theme es schon über dem Text, steht im Profil kein zweites)."""
    seite = requests.get(wp_cli(f"echo get_permalink( {eintraege['mit_bild']} );").strip(), headers=AN, timeout=30).text
    bilder = re.findall(r'<img[^>]+vz-bildprobe-[^>]+>', seite)
    assert len(bilder) == 1, bilder
    assert _attr(bilder[0], "alt") == "Vereinsfoto der Bildprobe"
    assert "Symbolbild" not in seite.split("vz-profil", 1)[1].split("</article>", 1)[0]


def test_ersatzbilder_mit_nachweis_und_dateien(wp_cli):
    bilder = json.loads(wp_cli("echo wp_json_encode( tamil_site_vz_ersatzbilder() );"))
    assert set(bilder) == set(ARTEN)
    for art, b in bilder.items():
        assert b["alt"].startswith("Symbolbild") and "Wikimedia Commons" in b["nachweis"] and "CC" in b["nachweis"], art
    nachweis = (__import__("pathlib").Path(__file__).resolve().parents[2] / "wordpress/plugins/tamil-site/assets/img/verzeichnis/NACHWEIS.md")
    text = nachweis.read_text(encoding="utf-8")
    for b in bilder.values():
        assert b["datei"] in text and b["klein"] in text


def test_leere_auswahl_ausgeblendet_und_aenderungslink_sauber(eintraege, wp_cli):
    """Prüfung 17.11. (P2): „Bundesland oder Kanton“ fehlt, solange kein Eintrag eines hat; der Link „Änderung melden“
    trägt genau vz_formular=aenderung und vz_eintrag (im HTML ist & als &#038; kodiert)."""
    hat_region = wp_cli("echo wp_json_encode( tamil_site_vz_vorhandene_werte( 'bundesland_kanton' ) );").strip() != "[]"
    html = requests.get(eintraege["seite"], headers=AN, timeout=30).text
    assert ('id="vz-filter-region"' in html) == hat_region
    assert 'id="vz-filter-stadt"' in html  # Dortmund gibt es
    profil = requests.get(wp_cli(f"echo get_permalink( {eintraege['ohne']['tempel']} );").strip(), headers=AN, timeout=30).text
    href = re.search(r'<p class="vz-aenderung"><a href="([^"]+)"', profil).group(1).replace("&#038;", "&")
    abfrage = href.split("?", 1)[1].split("#", 1)[0]
    assert abfrage == f"vz_formular=aenderung&vz_eintrag={eintraege['ohne']['tempel']}", href


def test_nachweise_zugeschnitten_mit_quelle_und_lizenz(wp_cli):
    """Symbolbilder und Bannerfotos sind im Bild beschnitten: Nachweis mit „zugeschnitten“, Dateiseite und Lizenz-URL
    gehen mit der Aktion tamil_site_bildnachweis ans Theme."""
    daten = json.loads(wp_cli("echo wp_json_encode( array( tamil_site_vz_ersatzbilder(), tamil_site_eigenanzeige_standardbilder() ) );"))
    for b in list(daten[0].values()) + [v for k, v in daten[1].items() if k != "production"]:
        assert b["nachweis"].endswith(", zugeschnitten") and "(Ausschnitt)" not in b["nachweis"], b["nachweis"]
        assert b["quelle"].startswith("https://commons.wikimedia.org/wiki/File:") and b["lizenz"].startswith("https://creativecommons.org/")
    gemeldet = json.loads(wp_cli("$m = array(); add_action( 'tamil_site_bildnachweis', static function ( $t, $q, $l ) use ( &$m ) { $m[] = array( $t, $q, $l ); }, 10, 3 );"
                                 " tamil_site_nachweis_melden( 'Foto: X / Wikimedia Commons, CC BY-SA 4.0, zugeschnitten', 'https://commons.wikimedia.org/wiki/File:X.jpg',"
                                 " 'https://creativecommons.org/licenses/by-sa/4.0/' ); echo wp_json_encode( $m );"))
    assert gemeldet == [["Foto: X / Wikimedia Commons, CC BY-SA 4.0, zugeschnitten", "https://commons.wikimedia.org/wiki/File:X.jpg",
                         "https://creativecommons.org/licenses/by-sa/4.0/"]]
