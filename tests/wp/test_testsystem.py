"""Einrichtung des Testsystems (wordpress/docker/wp-helfer.php testsystem, aufgerufen von start.sh außerhalb des
Echtbetriebs): Seiten production, einreichen, werben, verzeichnis; einmalig Bausteine Einreichungen, Verzeichnis und
Werbebuchung an (Entscheidung Luis 17.11.) und erkennbar erfundene Beispiel-Einträge im Verzeichnis.

Gegen ein lokales WordPress (wordpress/dev/setup.sh + serve.sh); der Helfer läuft zweimal, um die Idempotenz zu zeigen.
Danach wird alles auf den Stand vor dem Test zurückgesetzt. Die Prüfungen von start.sh brauchen kein WordPress.
"""

import base64
import json
import os
import re
import shlex
import subprocess
from pathlib import Path

import pytest
import requests
from wp_umgebung import URL, WP_CLI

ROOT = Path(__file__).resolve().parents[2]
HELFER = ROOT / "wordpress" / "docker" / "wp-helfer.php"
START = (ROOT / "wordpress" / "docker" / "start.sh").read_text(encoding="utf-8")
SEITEN = ("production", "einreichen", "werben", "verzeichnis")


def _helfer(aufgabe: str) -> str:
    env = os.environ | {"WP_ADMIN_USER": os.environ.get("WP_ADMIN_USER", "admin")}
    r = subprocess.run([*shlex.split(WP_CLI), "eval-file", str(HELFER), aufgabe], capture_output=True, text=True, env=env, check=False)
    assert r.returncode == 0, r.stdout + r.stderr
    return r.stdout + r.stderr


def _php(wp_cli, code: str):
    return json.loads(wp_cli(code))


@pytest.fixture
def testsystem(wp_cli):
    """Stand der Seiten, Schalter, Merker und Einträge sichern; nach dem Test genau so zurück."""
    sicher = wp_cli(
        "global $wpdb; $seiten = array(); foreach ( array( 'production', 'einreichen', 'werben', 'verzeichnis' ) as $slug ) {"
        " $p = get_page_by_path( $slug, OBJECT, 'page' ); $seiten[ $slug ] = $p ? array( $p->ID, $p->post_status ) : null; }"
        " echo base64_encode( wp_json_encode( array( 'seiten' => $seiten, 'funktionen' => get_option( 'tamil_site_funktionen', null ),"
        " 'merker' => get_option( 'tamil_c_testsystem', null ), 'max' => (int) $wpdb->get_var( \"SELECT MAX(ID) FROM {$wpdb->posts}\" ),"
        " 'beispiele' => get_posts( array( 'post_type' => TAMIL_SITE_VZ_TYP, 'post_status' => 'any', 'numberposts' => -1, 'fields' => 'ids',"
        " 'meta_key' => '_tamil_vz_beispiel' ) ) ) ) );")
    # Schon vorhandene Beispiel-Einträge (etwa auf einem eingerichteten Testbett) vorübergehend ohne Kennzeichen: Der
    # Helfer legt dann eigene an, und „beispiele-entfernen“ löscht die vorhandenen nicht mit.
    vorhanden = ", ".join(str(int(i)) for i in json.loads(base64.b64decode(sicher))["beispiele"])
    wp_cli("delete_option( 'tamil_c_testsystem' );"
           f" foreach ( array( {vorhanden} ) as $id ) {{ delete_post_meta( (int) $id, '_tamil_vz_beispiel' ); }}")
    yield json.loads(base64.b64decode(sicher))
    alt = json.loads(base64.b64decode(sicher))
    wp_cli(f"$alt = json_decode( base64_decode( '{sicher}' ), true ); global $wpdb;"
           " foreach ( get_posts( array( 'post_type' => array( 'page', TAMIL_SITE_VZ_TYP ), 'post_status' => 'any', 'numberposts' => -1, 'fields' => 'ids' ) ) as $id ) {"
           f" if ( $id > {int(alt['max'])} ) {{ wp_delete_post( $id, true ); }} }}"
           " foreach ( $alt['seiten'] as $slug => $s ) { if ( $s ) { wp_update_post( array( 'ID' => $s[0], 'post_status' => $s[1] ) ); } }"
           " foreach ( array( 'funktionen' => 'tamil_site_funktionen', 'merker' => 'tamil_c_testsystem' ) as $k => $o ) {"
           " if ( null === $alt[ $k ] ) { delete_option( $o ); } else { update_option( $o, $alt[ $k ] ); } }"
           " foreach ( $alt['beispiele'] as $id ) { update_post_meta( (int) $id, '_tamil_vz_beispiel', '1' ); }")


def _stand(wp_cli) -> dict:
    return _php(wp_cli,
                "$seiten = array(); foreach ( array( 'production', 'einreichen', 'werben', 'verzeichnis' ) as $slug ) {"
                " $p = get_page_by_path( $slug, OBJECT, 'page' ); $seiten[ $slug ] = $p ? array( 'id' => $p->ID, 'status' => $p->post_status,"
                " 'inhalt' => $p->post_content, 'titel' => $p->post_title, 'vorlage' => get_page_template_slug( $p ) ) : null; }"
                " $b = get_posts( array( 'post_type' => TAMIL_SITE_VZ_TYP, 'post_status' => 'any', 'numberposts' => -1, 'meta_key' => '_tamil_vz_beispiel' ) );"
                " echo wp_json_encode( array( 'seiten' => $seiten, 'funktionen' => array_map( 'tamil_site_funktion_an', array( 'einreichungen' => 'einreichungen',"
                " 'verzeichnis' => 'verzeichnis', 'werbung' => 'werbung', 'zustimmung' => 'zustimmung' ) ),"
                " 'beispiele' => array_map( static function ( $p ) { return array( 'id' => $p->ID, 'titel' => $p->post_title, 'inhalt' => $p->post_content,"
                " 'status' => $p->post_status, 'werte' => tamil_site_vz_eintrag_werte( $p->ID ) ); }, $b ) ) );")


def test_testsystem_einrichten_zweimal_gleich(wp, wp_cli, testsystem):
    zustimmung_vorher = _php(wp_cli, "echo wp_json_encode( tamil_site_funktion_an( 'zustimmung' ) );")
    vorher = _stand(wp_cli)["seiten"]
    erste = _helfer("testsystem")
    stand = _stand(wp_cli)
    zweite = _helfer("testsystem")
    assert _stand(wp_cli) == stand, "zweiter Lauf ändert nichts"
    assert "angelegt" not in zweite and "eingeschaltet" not in zweite and "veröffentlicht" not in zweite, zweite
    assert "Bausteine eingeschaltet" in erste

    seiten = stand["seiten"]
    for slug in SEITEN:
        assert seiten[slug] and seiten[slug]["status"] == "publish", slug
    # Eine schon veröffentlichte Seite (etwa „Production“ aus einer Übernahme) behält Titel, Inhalt und Vorlage; geprüft
    # wird der Inhalt nur bei Seiten, die der Helfer selbst angelegt oder veröffentlicht hat.
    gepflegt = {slug for slug in SEITEN if vorher[slug] and vorher[slug]["status"] == "publish"}
    for slug in gepflegt:
        assert seiten[slug] == vorher[slug], f"{slug}: bestehende Seite verändert"
    if "production" not in gepflegt:
        assert seiten["production"]["titel"] == "Live mit dir!"
        if "page-production.php" in wp_cli("echo wp_json_encode( array_keys( wp_get_theme()->get_page_templates() ) );"):
            assert seiten["production"]["vorlage"] == "page-production.php"
        # Archivbeiträge der Konzertreihe (Testsystem) oder, ohne sie, der Satz aus dem Altbestand
        assert "Die Konzerte im Archiv" in seiten["production"]["inhalt"] or "auf deutschen Bühnen" in seiten["production"]["inhalt"]
    if "einreichen" not in gepflegt:
        assert '[tamil_einsendung art="event"]' in seiten["einreichen"]["inhalt"]
        for art in ("beitrag", "kooperation", "werbung"):
            assert f'href="#tf-{art}"' in seiten["einreichen"]["inhalt"], art
    for slug, kennung in (("werben", "[tamil_werbung]"), ("verzeichnis", "[tamil_verzeichnis]")):
        if slug not in gepflegt:
            assert kennung in seiten[slug]["inhalt"], slug

    assert stand["funktionen"] == {"einreichungen": True, "verzeichnis": True, "werbung": True, "zustimmung": zustimmung_vorher}

    beispiele = stand["beispiele"]
    assert len(beispiele) == 4
    assert {b["werte"]["art"] for b in beispiele} == {"tempel", "verein", "business", "dienstleister"}
    for b in beispiele:
        assert b["titel"].startswith("Beispiel: ") and "Beispiel" in b["inhalt"] and b["status"] == "publish"
        assert b["werte"]["stadt"] == "Musterstadt" and b["werte"]["website"] == "https://example.org/"
        assert not b["werte"]["telefon"] and not b["werte"]["email"], "keine echt wirkenden Kontaktdaten"

    # Die Seiten antworten, die Formulare und das Verzeichnis sind da, Werben sagt den Stand der Zahlung
    if "einreichen" not in gepflegt:
        assert "tf-formular" in requests.get(f"{URL}/einreichen/", timeout=30).text
    if "verzeichnis" not in gepflegt:
        assert "Beispiel: Tempelverein Musterstadt" in requests.get(f"{URL}/verzeichnis/", timeout=30).text
    if "werben" not in gepflegt:
        assert "auf Anfrage" in requests.get(f"{URL}/werben/", timeout=30).text
    assert requests.get(f"{URL}/production/", timeout=30).status_code == 200


def test_ausgeschaltet_bleibt_ausgeschaltet(wp_cli, testsystem):
    """Schaltet jemand einen Baustein im Backend wieder aus, schaltet ihn der nächste Start nicht erneut ein."""
    _helfer("testsystem")
    wp_cli("$f = (array) get_option( 'tamil_site_funktionen' ); $f['werbung'] = false; update_option( 'tamil_site_funktionen', $f );")
    _helfer("testsystem")
    assert _php(wp_cli, "echo wp_json_encode( tamil_site_funktion_an( 'werbung' ) );") is False


def test_beispiele_entfernen(wp_cli, testsystem):
    _helfer("testsystem")
    assert len(_stand(wp_cli)["beispiele"]) == 4
    aus = _helfer("beispiele-entfernen")
    assert "4 Beispiel-Einträge entfernt" in aus and _stand(wp_cli)["beispiele"] == []


def test_vorhandene_seite_bleibt_unveraendert(wp_cli, testsystem):
    """Eine schon gepflegte Seite (anderer Inhalt) wird nicht überschrieben."""
    if testsystem["seiten"]["production"]:
        pytest.skip("Seite production gibt es lokal schon")
    pid = int(wp_cli("echo (int) wp_insert_post( array( 'post_type' => 'page', 'post_status' => 'publish', 'post_name' => 'production',"
                     " 'post_title' => 'Gepflegt', 'post_content' => 'Eigener Text' ) );").strip())
    _helfer("testsystem")
    assert _php(wp_cli, f"echo wp_json_encode( array( get_post( {pid} )->post_title, get_post( {pid} )->post_content ) );") == ["Gepflegt", "Eigener Text"]


# --- ohne WordPress: start.sh und Helfer im Quelltext -----------------------------------------------------------------

def test_start_sh_ruft_testsystem_nur_ausserhalb_des_echtbetriebs():
    block = re.search(r'if \[ "\$WP_ENVIRONMENT_TYPE" != "production" \]; then\n(.*?)\nfi\n', START, re.S)
    assert block and 'wp eval-file "$HELFER" testsystem ||' in block.group(1), "Aufruf nur außerhalb des Echtbetriebs und ohne Abbruch"
    assert START.index("testsystem") > START.index('wp eval-file "$HELFER" zugaenge') and START.index("testsystem") < START.index("exec docker-entrypoint.sh")
    r = subprocess.run(["bash", "-n", str(ROOT / "wordpress" / "docker" / "start.sh")], capture_output=True, text=True, check=False)
    assert r.returncode == 0, r.stderr


def test_helfer_prueft_echtbetrieb_zuerst():
    text = HELFER.read_text(encoding="utf-8")
    rumpf = text[text.index("function tamil_c_testsystem(): void {"):]
    assert rumpf.index("'production' === wp_get_environment_type()") < rumpf.index("tamil_c_seite(")
    assert "example.org" in text and "Musterstadt" in text and "wp_mail" not in text
