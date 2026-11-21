"""Formulare mit eigenen deutschen Fehlertexten (Prüfung 17.11., P2): Die Formulare der Einsendungen, des Verzeichnisses
und „Buchung wiederfinden“ prüfen nicht im Browser (novalidate, sonst erscheint z. B. „Please fill out this field.“),
sondern auf der Website: Jedes fehlerhafte Feld trägt aria-invalid und verweist mit aria-describedby auf seinen
deutschen Fehlertext. Das Lockfeld (Honeypot) liegt außerhalb des Bedienbaums (aria-hidden, inert, tabindex -1).

Gegen ein lokales WordPress (wordpress/dev/setup.sh + serve.sh); Schalter über die Test-Kopfzeile. Alle Angaben erfunden.
"""

import re

import pytest
import requests
import test_einsendungen as te
import test_verzeichnis as tv
from test_einsendungen import seite as seite_einsendungen  # noqa: F401 (Fixture)
from test_verzeichnis import seite as seite_verzeichnis  # noqa: F401 (Fixture)

ENGLISCH = ("Please fill", "Please enter", "Please select", "Please match")


def _fehler_verknuepft(html: str) -> list[str]:
    """Für jedes Feld mit aria-invalid: verweist aria-describedby auf ein Element mit deutschem Text? Gibt die Texte zurück."""
    texte = []
    for feld in re.findall(r"<(?:input|select|textarea)\b[^>]*aria-invalid=\"true\"[^>]*>", html):
        ids = re.search(r'aria-describedby="([^"]+)"', feld)
        assert ids, f"aria-invalid ohne aria-describedby: {feld[:160]}"
        gefunden = False
        for kennung in ids.group(1).split():
            m = re.search(rf'id="{re.escape(kennung)}"[^>]*>([^<]+)<', html)
            if m and "fehler" in kennung:
                texte.append(m.group(1).strip())
                gefunden = True
        assert gefunden, f"kein Fehlertext für {feld[:160]}"
    for text in texte:
        assert not any(e in text for e in ENGLISCH), text
    return texte


def test_einsendungen_ohne_browserpruefung_mit_eigenen_fehlern(wp, wp_cli, seite_einsendungen):
    html = requests.get(seite_einsendungen, headers=te.AN, timeout=30).text
    formulare = re.findall(r'<form class="tf-formular"[^>]*>', html)
    assert len(formulare) == 5 and all(" novalidate" in f for f in formulare)
    falle = re.search(r'<p class="tf-falle"[^>]*>', html).group(0)
    assert 'aria-hidden="true"' in falle and " inert" in falle
    assert re.search(r'name="tf_webseite"[^>]*tabindex="-1"', html)
    # leer absenden: deutsche Texte am Feld, nichts angenommen
    vorher = te._anzahl(wp_cli)
    r = te.absenden(wp, wp_cli, seite_einsendungen, "event", {k: "" for k in te.EVENT} | {"name": "", "email": "nicht-gueltig"},
                    einwilligung=False)
    assert r.status_code == 200 and te._anzahl(wp_cli) == vorher
    block = te._formular(r.text, "event")
    texte = _fehler_verknuepft(block)
    assert len(texte) >= 8, texte  # Titel, Beginn, Ort, Stadt, Land, Veranstalter, Beschreibung, Name, E-Mail, Einwilligung
    assert re.search(r'id="tf-event-einwilligung"[^>]*aria-invalid="true"', block)


def test_verzeichnis_ohne_browserpruefung_mit_eigenen_fehlern(wp, wp_cli, seite_verzeichnis):
    html = requests.get(f"{seite_verzeichnis}?vz_formular=neu", headers=tv.AN, timeout=30).text
    form = re.search(r'<form class="vz-form"[^>]*>', html).group(0)
    assert " novalidate" in form
    falle = re.search(r'<p class="vz-falle"[^>]*>', html).group(0)
    assert 'aria-hidden="true"' in falle and " inert" in falle
    r = tv.absenden(wp_cli, seite_verzeichnis, {"name": "", "art": "", "plz": "", "stadt": "", "land": ""},
                    einsender={"vz_einsender_name": "", "vz_einsender_email": "kaputt"}, einwilligung=False)
    assert r.status_code == 200
    texte = _fehler_verknuepft(r.text)
    assert len(texte) >= 5, texte
    for feld in ("vz-einsender-email", "vz-einwilligung-feld"):
        assert re.search(rf'id="{feld}"[^>]*aria-invalid="true"', r.text), feld
    assert 'aria-describedby="vz-berechtigung-fehler"' in r.text


@pytest.fixture
def seite_werben(wp_cli):
    pid = int(wp_cli("echo (int) wp_insert_post( array( 'post_type' => 'page', 'post_status' => 'publish', 'post_title' => 'Werben (Fehler)',"
                     " 'post_name' => 'werben-fehler-test', 'post_content' => '[tamil_werbung]' ) );").strip())
    yield wp_cli(f"echo get_permalink( {pid} );").strip()
    wp_cli(f"wp_delete_post( {pid}, true );")


def test_buchung_wiederfinden_mit_eigenen_fehlern(wp, seite_werben):
    kopf = {"X-Tamil-Funktionen": "werbung"}
    html = requests.get(seite_werben, headers=kopf, timeout=30).text
    form = re.search(r'<form class="wb-formular"[^>]*>(?:(?!</form>).)*name="tamil_wb_aktion" value="wiederfinden"', html, re.S)
    assert form and " novalidate" in form.group(0)[:200]
    nonce = re.search(r'name="_wpnonce" value="([^"]+)"[^>]*>\s*<input type="hidden" name="tamil_wb_aktion" value="wiederfinden"', html).group(1)
    r = requests.post(seite_werben, data={"tamil_wb_aktion": "wiederfinden", "_wpnonce": nonce, "nummer": "", "email": "x"},
                      headers=kopf, timeout=30)
    texte = _fehler_verknuepft(r.text)
    assert "Bitte die Buchungsnummer angeben." in texte and any("E-Mail-Adresse" in t for t in texte)
