"""Einsendungen (Festlegung F1): Formulare in tamil-site, Abholen über REST in tamil-radar, Löschfrist.

Gegen ein lokales WordPress (wordpress/dev/setup.sh + serve.sh). Der Funktionsschalter „einreichungen“ wird für
einzelne Aufrufe über die Test-Kopfzeile eingeschaltet (nur in der Umgebung local wirksam). Alle Personendaten in
diesen Tests sind erfunden (example.test).
"""

import base64
import hashlib
import io
import json
import re

import pytest
import requests
from PIL import Image
from PIL.PngImagePlugin import PngInfo

AN = {"X-Tamil-Funktionen": "einreichungen"}
NS = "/wp-json/tamil-radar/v1"
PERSON = {"name": "Erika Beispiel", "email": "erika@example.test", "telefon": "+49 30 1234567"}
EVENT = {
    "titel": "Pongal-Fest Testverein", "beginn": "2027-01-16T18:30", "ende": "2027-01-16T22:00",
    "ort": "Gemeindesaal, Beispielstraße 1", "stadt": "Essen", "land": "DE", "veranstalter": "Testverein e. V.",
    "beschreibung": "Tanz, Musik und Essen.", "eintritt": "10 Euro, Kinder frei",
    "ticket_link": "https://tickets.example.test/pongal",
}


def _json(wp_cli, code: str):
    return json.loads(wp_cli(code))


@pytest.fixture
def seite(wp, wp_cli):
    """Veröffentlichte Seite mit allen fünf Formularen; danach werden Seite und neue Einsendungen entfernt."""
    start = int(wp_cli("global $wpdb; echo (int) $wpdb->get_var( 'SELECT MAX(id) FROM ' . tamil_site_einsendung_tabelle() );") or 0)
    # Drossel für die Adresse der Tests zurücksetzen (nur lokale Testdaten)
    wp_cli("global $wpdb; $wpdb->query( $wpdb->prepare( 'UPDATE ' . tamil_site_einsendung_tabelle() . ' SET ip_hash = NULL WHERE ip_hash = %s', tamil_site_einsendung_ip_hash( '127.0.0.1' ) ) );")
    inhalt = "".join(f'[tamil_einsendung art="{a}"]' for a in ("event", "beitrag", "kooperation", "werbung", "kontakt"))
    daten = _json(wp_cli, "$id = wp_insert_post( array( 'post_type' => 'page', 'post_status' => 'publish', "
                          f"'post_title' => 'Einsenden Test', 'post_name' => 'einsenden-test-' . wp_rand(), 'post_content' => '{inhalt}' ) );"
                          " echo wp_json_encode( array( 'id' => $id, 'url' => get_permalink( $id ) ) );")
    yield daten["url"]
    wp_cli(f"wp_delete_post( {daten['id']}, true );"
           "global $wpdb; $t = tamil_site_einsendung_tabelle();"
           f"foreach ( (array) $wpdb->get_col( $wpdb->prepare( \"SELECT bild_datei FROM {{$t}} WHERE id > %d AND bild_datei != ''\", {start} ) ) as $d ) {{ wp_delete_file( tamil_site_einsendung_bildordner() . $d ); }}"
           f"$wpdb->query( $wpdb->prepare( \"DELETE FROM {{$t}} WHERE id > %d\", {start} ) );")


def _formular(html: str, art: str) -> str:
    m = re.search(rf'<div class="tf tf-{art}" id="tf-{art}">(.*?)</form>', html, re.DOTALL)
    assert m, f"Formular {art} fehlt"
    return m.group(1)


def _wert(block: str, name: str) -> str:
    m = re.search(rf'name="{re.escape(name)}" value="([^"]*)"', block)
    assert m, name
    return m.group(1)


def absenden(wp, wp_cli, url: str, art: str, felder: dict, *, einwilligung=True, falle="", zeit=None, nonce=None,
             fassung=None, bild=None, bild_recht=True, kopf=AN) -> requests.Response:
    block = _formular(requests.get(url, headers=kopf, timeout=30).text, art)
    daten = {
        "tf_art": art,
        "tf_nonce": _wert(block, "tf_nonce") if nonce is None else nonce,
        "tf_zeit": wp_cli("echo tamil_site_einsendung_zeitstempel( time() - 10 );") if zeit is None else zeit,
        "tf_fassung": _wert(block, "tf_fassung") if fassung is None else fassung,
        "tf_webseite": falle,
        **{f"tf[{k}]": v for k, v in {**PERSON, **felder}.items()},
    }
    if einwilligung:
        daten["tf_einwilligung"] = "1"
    if bild_recht:
        daten["tf_bild_recht"] = "1"
    dateien = {"tf_bild": bild} if bild else None
    return requests.post(url, data=daten, files=dateien, headers=kopf, allow_redirects=False, timeout=30)


def _vorgang(antwort: requests.Response) -> str:
    assert antwort.status_code == 303, antwort.text[:2000]
    m = re.search(r"eingang=(T\d{6}-[A-Z0-9]{5})", antwort.headers["Location"])
    assert m, antwort.headers["Location"]
    return m.group(1)


def _anzahl(wp_cli) -> int:
    return int(wp_cli("global $wpdb; echo (int) $wpdb->get_var( 'SELECT COUNT(*) FROM ' . tamil_site_einsendung_tabelle() );"))


def _rest(wp, methode: str, pfad: str, auth=None, **kw) -> requests.Response:
    kw.setdefault("headers", AN)
    return requests.request(methode, wp.url + NS + pfad, auth=auth if auth is not None else wp.auth, timeout=30, **kw)


# --- Schalter, Upgrade, Markup ------------------------------------------------------------------------------------

def test_upgrade_tabelle_recht_und_cron(wp_cli):
    r = _json(wp_cli, "global $wpdb; echo wp_json_encode( array( tamil_site_datenversion(), "
                      "$wpdb->get_var( $wpdb->prepare( 'SHOW TABLES LIKE %s', tamil_site_einsendung_tabelle() ) ), "
                      "get_role( 'radar' )->has_cap( 'tamil_einsendungen_abholen' ), get_role( 'administrator' )->has_cap( 'tamil_einsendungen_abholen' ), "
                      "(bool) wp_next_scheduled( 'tamil_site_einsendungen_aufraeumen' ), "
                      "file_get_contents( tamil_site_einsendung_bildordner() . '.htaccess' ) ) );")
    assert r[0] >= 2 and r[1].endswith("tamil_einsendungen")
    assert r[2] is True and r[3] is False  # nur der Radar-Benutzer
    assert r[4] is True and "Require all denied" in r[5]
    # Schritt ist idempotent (Version zurücksetzen, zweimal laufen lassen)
    assert wp_cli("delete_option( 'tamil_site_datenversion' ); var_export( tamil_site_upgrade_ausfuehren() && tamil_site_upgrade_ausfuehren() );") == "true"


def test_schalter_aus_neutraler_hinweis_nichts_angenommen(wp, wp_cli, seite):
    alt = wp_cli("echo wp_json_encode( get_option( 'tamil_site_funktionen', null ) );").strip()
    try:
        wp_cli("$f = (array) get_option( 'tamil_site_funktionen', array() ); $f['einreichungen'] = false; update_option( 'tamil_site_funktionen', $f );")
        html = requests.get(seite, timeout=30).text
        assert html.count("Dieses Formular steht derzeit nicht zur Verfügung.") == 5
        assert "tf_nonce" not in html and "einsendungen.css" not in html
        vorher = _anzahl(wp_cli)
        r = requests.post(seite, data={"tf_art": "kontakt", "tf[nachricht]": "x", "tf[name]": "a", "tf[email]": "a@example.test",
                                       "tf_einwilligung": "1"}, allow_redirects=False, timeout=30)
        assert r.status_code == 200 and _anzahl(wp_cli) == vorher
        rest = _rest(wp, "GET", "/einsendungen", headers={})
        assert rest.status_code == 503 and rest.json()["code"] == "tamil_funktion_aus"
    finally:
        if alt == "null":
            wp_cli("delete_option( 'tamil_site_funktionen' );")
        else:
            wp_cli(f"update_option( 'tamil_site_funktionen', json_decode( '{alt}', true ) );")


def test_formulare_markup_barrierefrei(wp, seite):
    antwort = requests.get(seite, headers=AN, timeout=30)
    assert antwort.headers.get("Cache-Control") == "no-store"
    html = antwort.text
    for art in ("event", "beitrag", "kooperation", "werbung", "kontakt"):
        block = _formular(html, art)
        assert 'class="tf-formular" method="post"' in block
        assert 'name="tf_einwilligung" value="1" required' in block and 'name="tf_webseite"' in block
        assert 'class="tf-falle" aria-hidden="true"' in block and 'tabindex="-1"' in block
        # jedes sichtbare Eingabefeld hat eine Beschriftung
        for feld_id in re.findall(r'<(?:input(?![^>]*type="hidden")|textarea|select)[^>]*\sid="([^"]+)"', block):
            assert f'<label for="{feld_id}"' in block, (art, feld_id)
        assert ('name="tf_bild"' in block) == (art in ("event", "beitrag"))
        assert ('enctype="multipart/form-data"' in block) == (art in ("event", "beitrag"))
    event = _formular(html, "event")
    assert 'type="datetime-local"' in event and '<option value="AT">Österreich</option>' in event
    assert "Titel <span class=\"tf-pflicht\">(Pflicht)</span>" in event
    assert 'accept="image/jpeg,image/png"' in event
    assert "Vorläufige Fassung." in event and 'name="tf_fassung" value="2026-11-vorlaeufig"' in event
    assert re.search(r"tamil-site/assets/einsendungen\.css\?ver=", html)
    ids = re.findall(r'\sid="([^"]+)"', html)
    assert len(ids) == len(set(ids)), "doppelte IDs"


# --- Annahme und Abwehr -------------------------------------------------------------------------------------------

def test_event_angenommen_danke_mit_vorgangsnummer_und_abholbar(wp, wp_cli, seite):
    vorgang = _vorgang(absenden(wp, wp_cli, seite, "event", EVENT))
    zeile = _json(wp_cli, f"echo wp_json_encode( tamil_site_einsendung_ausgabe( tamil_site_einsendung_zeile( '{vorgang}' ) ) );")
    assert zeile["art"] == "event" and zeile["status"] == "eingegangen"
    assert zeile["einwilligung"] is True and zeile["einwilligung_fassung"] == "2026-11-vorlaeufig"
    assert zeile["name"] == PERSON["name"] and zeile["email"] == PERSON["email"]
    assert zeile["felder"]["land"] == "DE" and zeile["felder"]["beginn"].startswith("2027-01-16T18:30:00")
    assert zeile["felder"]["ticket_link"] == EVENT["ticket_link"] and zeile["bild"] is None
    # kein Name, keine Kontaktdaten im Protokoll
    protokoll = wp_cli("global $wpdb; echo wp_json_encode( $wpdb->get_results( $wpdb->prepare( 'SELECT * FROM ' . tamil_site_einsendung_protokoll_tabelle() . ' WHERE vorgangsnummer = %s', "
                       f"'{vorgang}' ) ) );")
    assert '"aktion":"eingang"' in protokoll and PERSON["name"] not in protokoll and PERSON["email"] not in protokoll


def test_danke_nur_mit_echter_pruefsumme(wp, wp_cli, seite):
    antwort = absenden(wp, wp_cli, seite, "kontakt", {"nachricht": "Hallo Redaktion"})
    vorgang = _vorgang(antwort)
    danke = requests.get(antwort.headers["Location"], headers=AN, timeout=30).text
    block = re.search(r'id="tf-kontakt">(.*?)</div>\s*</div>', danke, re.DOTALL).group(1)
    assert "Danke, die Redaktion meldet sich." in block and f'<strong class="tf-vorgang">{vorgang}</strong>' in block
    assert 'role="status"' in block
    falsch = re.sub(r"pruef=[a-z0-9]+", "pruef=0000000000000000", antwort.headers["Location"])
    assert "Danke, die Redaktion meldet sich." not in requests.get(falsch, headers=AN, timeout=30).text


@pytest.mark.parametrize("fall", ["ohne_einwilligung", "falle", "zu_schnell", "falscher_nonce", "alte_fassung",
                                  "zu_viele_links", "pflicht_fehlt", "falsches_land"])
def test_nicht_angenommen(wp, wp_cli, seite, fall):
    felder = dict(EVENT)
    kw = {}
    erwartet = {
        "ohne_einwilligung": "Ohne Einwilligung können wir die Einsendung nicht annehmen.",
        "falle": "Die Einsendung wurde nicht angenommen.",
        "zu_schnell": "schneller, als ein Mensch tippen kann",
        "falscher_nonce": "Das Formular ist abgelaufen.",
        "alte_fassung": "Der Text der Einwilligung hat sich geändert.",
        "zu_viele_links": "Bitte höchstens 3 Links im Text.",
        "pflicht_fehlt": "Titel fehlt.",
        "falsches_land": "Bitte Deutschland, Österreich oder die Schweiz wählen.",
    }[fall]
    if fall == "ohne_einwilligung":
        kw["einwilligung"] = False
    elif fall == "falle":
        kw["falle"] = "https://spam.example.test"
    elif fall == "zu_schnell":
        kw["zeit"] = wp_cli("echo tamil_site_einsendung_zeitstempel();")
    elif fall == "falscher_nonce":
        kw["nonce"] = "0123456789"
    elif fall == "alte_fassung":
        kw["fassung"] = "2025-alt"
    elif fall == "zu_viele_links":
        felder["beschreibung"] = "https://a.example.test https://b.example.test www.c.example.test http://d.example.test"
    elif fall == "pflicht_fehlt":
        felder["titel"] = "   "
    elif fall == "falsches_land":
        felder["land"] = "FR"
    vorher = _anzahl(wp_cli)
    r = absenden(wp, wp_cli, seite, "event", felder, **kw)
    assert r.status_code == 200, r.headers.get("Location")
    block = _formular(r.text, "event")
    assert 'class="tf-meldung" role="alert"' in block and erwartet in block
    assert _anzahl(wp_cli) == vorher
    if fall in ("pflicht_fehlt", "ohne_einwilligung"):
        # Werte bleiben stehen, das Feld ist markiert und verweist auf seine Meldung
        assert 'value="Testverein e. V."' in block
        feld = "titel" if fall == "pflicht_fehlt" else "einwilligung"
        assert re.search(rf'id="tf-event-{feld}"[^>]*aria-describedby="tf-event-{feld}-fehler"[^>]*aria-invalid="true"', block) or \
            re.search(rf'id="tf-event-{feld}"[^>]*aria-invalid="true"[^>]*aria-describedby="tf-event-{feld}-fehler"', block)


def test_drossel_fuenf_je_stunde(wp, wp_cli, seite):
    wp_cli("for ( $i = 0; $i < 5; $i++ ) { tamil_site_einsendung_speichern( array( 'art' => 'kontakt', 'name' => 'Test', 'email' => 't@example.test', "
           "'felder' => array( 'nachricht' => 'x' ), 'einwilligung_fassung' => 'test', 'ip_hash' => tamil_site_einsendung_ip_hash( '127.0.0.1' ) ) ); }")
    vorher = _anzahl(wp_cli)
    r = absenden(wp, wp_cli, seite, "kontakt", {"nachricht": "Noch eine"})
    assert r.status_code == 200 and "zu viele Einsendungen" in _formular(r.text, "kontakt")
    assert _anzahl(wp_cli) == vorher


def test_ip_nur_als_hash(wp, wp_cli, seite):
    vorgang = _vorgang(absenden(wp, wp_cli, seite, "kooperation", {"organisation": "Verein", "anliegen": "Zusammenarbeit"}))
    roh = _json(wp_cli, f"echo wp_json_encode( tamil_site_einsendung_zeile( '{vorgang}' ) );")
    assert re.fullmatch(r"[0-9a-f]{64}", roh["ip_hash"]) and "127.0.0.1" not in json.dumps(roh)
    assert "ip_hash" not in _rest(wp, "GET", f"/einsendung/{vorgang}").json()


# --- Bilder -------------------------------------------------------------------------------------------------------

def _jpeg_mit_exif() -> bytes:
    exif = Image.Exif()
    exif[0x010E] = "Geheime Beschreibung"  # ImageDescription
    exif[0x0112] = 6  # Orientation: 90° im Uhrzeigersinn drehen
    buf = io.BytesIO()
    Image.new("RGB", (40, 20), (200, 30, 30)).save(buf, "JPEG", exif=exif.tobytes())
    return buf.getvalue()


def test_bild_jpeg_ohne_metadaten_gedreht_und_abholbar(wp, wp_cli, seite):
    vorgang = _vorgang(absenden(wp, wp_cli, seite, "beitrag", {"thema": "Bildtest", "text": "Mit Foto"},
                                bild=("foto.jpg", _jpeg_mit_exif(), "image/jpeg")))
    e = _rest(wp, "GET", f"/einsendung/{vorgang}").json()
    assert e["bild"]["typ"] == "image/jpeg" and e["bild"]["recht_bestaetigt"] is True
    b = _rest(wp, "GET", f"/einsendung/{vorgang}/bild")
    assert b.status_code == 200 and "no-store" in b.headers.get("Cache-Control", "")
    daten = base64.b64decode(b.json()["daten_base64"])
    assert hashlib.sha256(daten).hexdigest() == b.json()["sha256"] == e["bild"]["sha256"]
    assert b"Geheime Beschreibung" not in daten and b"Exif" not in daten
    with Image.open(io.BytesIO(daten)) as img:
        assert img.format == "JPEG" and img.size == (20, 40)
    # nicht öffentlich: zufälliger Dateiname im gesperrten Ordner, nicht in der Mediathek
    datei = wp_cli(f"echo tamil_site_einsendung_zeile( '{vorgang}' )['bild_datei'];")
    assert re.fullmatch(r"[0-9a-f]{32}\.jpg", datei)
    assert wp_cli("echo count( get_posts( array( 'post_type' => 'attachment', 'post_status' => 'any', 's' => 'foto', 'numberposts' => -1 ) ) );") == "0"
    assert '"aktion":"bild_abgerufen"' in wp_cli(f"global $wpdb; echo wp_json_encode( $wpdb->get_results( \"SELECT aktion FROM \" . tamil_site_einsendung_protokoll_tabelle() . \" WHERE vorgangsnummer = '{vorgang}'\" ) );")


def test_bild_png_ohne_textchunks(wp, wp_cli, seite):
    info = PngInfo()
    info.add_text("Comment", "Geheimer Kommentar")
    buf = io.BytesIO()
    Image.new("RGBA", (10, 10), (0, 0, 255, 128)).save(buf, "PNG", pnginfo=info)
    vorgang = _vorgang(absenden(wp, wp_cli, seite, "event", EVENT, bild=("plakat.png", buf.getvalue(), "image/png")))
    daten = base64.b64decode(_rest(wp, "GET", f"/einsendung/{vorgang}/bild").json()["daten_base64"])
    assert daten.startswith(b"\x89PNG") and b"Geheimer Kommentar" not in daten


@pytest.mark.parametrize("fall,erwartet", [
    ("kein_bild", "Bitte nur Bilder im Format JPEG oder PNG."),
    ("zu_gross", "Das Bild ist größer als 5 MB."),
    ("ohne_recht", "Bitte bestätigt, dass das Bild verwendet werden darf"),
])
def test_bild_abgewiesen(wp, wp_cli, seite, fall, erwartet):
    kw = {"bild": ("foto.jpg", b"<?php echo 1; ?> kein Bild", "image/jpeg")}
    if fall == "zu_gross":
        kw["bild"] = ("gross.jpg", _jpeg_mit_exif() + b"\0" * (5 * 1024 * 1024), "image/jpeg")
    elif fall == "ohne_recht":
        kw = {"bild": ("foto.jpg", _jpeg_mit_exif(), "image/jpeg"), "bild_recht": False}
    vorher = _anzahl(wp_cli)
    r = absenden(wp, wp_cli, seite, "beitrag", {"thema": "Bild", "text": "Test"}, **kw)
    assert r.status_code == 200 and erwartet in _formular(r.text, "beitrag")
    assert _anzahl(wp_cli) == vorher


def test_bild_bei_kontakt_wird_ignoriert(wp, wp_cli, seite):
    vorgang = _vorgang(absenden(wp, wp_cli, seite, "kontakt", {"nachricht": "Ohne Bildfeld"},
                                bild=("foto.jpg", _jpeg_mit_exif(), "image/jpeg")))
    assert _rest(wp, "GET", f"/einsendung/{vorgang}").json()["bild"] is None
    assert _rest(wp, "GET", f"/einsendung/{vorgang}/bild").status_code == 404


# --- REST für den Radar -------------------------------------------------------------------------------------------

def test_rest_rechte(wp, wp_admin, seite):
    assert _rest(wp, "GET", "/einsendungen", auth=()).status_code == 401
    assert requests.get(wp.url + NS + "/einsendungen", headers=AN, timeout=30).status_code == 401
    assert _rest(wp, "GET", "/einsendungen", auth=wp_admin).status_code == 403  # Admin hat das Recht nicht
    assert _rest(wp, "POST", "/einsendung/T000000-AAAAA/status", auth=wp_admin, json={"status": "erledigt"}).status_code == 403
    assert _rest(wp, "GET", "/einsendungen").status_code == 200


def test_rest_cursor(wp, wp_cli, seite):
    start = _rest(wp, "GET", "/einsendungen?anzahl=100").json()
    while start["mehr"]:
        start = _rest(wp, "GET", f"/einsendungen?anzahl=100&nach={start['weiter']}").json()
    cursor = start["weiter"]
    a = _vorgang(absenden(wp, wp_cli, seite, "kontakt", {"nachricht": "Erste"}))
    b = _vorgang(absenden(wp, wp_cli, seite, "werbung", {"firma": "Firma", "platz_zeitraum": "Leaderboard, März", "nachricht": "Zweite"}))
    seite1 = _rest(wp, "GET", f"/einsendungen?nach={cursor}&anzahl=1").json()
    assert [e["vorgangsnummer"] for e in seite1["einsendungen"]] == [a] and seite1["mehr"] is True
    seite2 = _rest(wp, "GET", f"/einsendungen?nach={seite1['weiter']}&anzahl=1").json()
    assert [e["vorgangsnummer"] for e in seite2["einsendungen"]] == [b] and seite2["mehr"] is False
    leer = _rest(wp, "GET", f"/einsendungen?nach={seite2['weiter']}").json()
    assert leer == {"einsendungen": [], "weiter": seite2["weiter"], "mehr": False}
    werbung = seite2["einsendungen"][0]
    assert werbung["art"] == "werbung" and werbung["felder"] == {"firma": "Firma", "platz_zeitraum": "Leaderboard, März", "nachricht": "Zweite"}
    assert set(werbung) == {"id", "vorgangsnummer", "art", "status", "eingang_at", "abgeholt_at", "abgeschlossen_at", "name",
                            "email", "telefon", "einwilligung", "einwilligung_fassung", "felder", "bild"}
    assert _rest(wp, "GET", "/einsendungen?anzahl=101").status_code == 400


def test_rest_status_maschine(wp, wp_cli, seite):
    vorgang = _vorgang(absenden(wp, wp_cli, seite, "event", EVENT))
    r = _rest(wp, "POST", f"/einsendung/{vorgang}/status", json={"status": "abgeholt"})
    assert r.status_code == 200 and r.json()["status"] == "abgeholt" and r.json()["abgeholt_at"]
    assert _rest(wp, "POST", f"/einsendung/{vorgang}/status", json={"status": "abgeholt"}).json()["status"] == "abgeholt"
    r = _rest(wp, "POST", f"/einsendung/{vorgang}/status", json={"status": "uebernommen"})
    assert r.status_code == 200 and r.json()["status"] == "uebernommen" and r.json()["abgeschlossen_at"]
    assert _rest(wp, "POST", f"/einsendung/{vorgang}/status", json={"status": "uebernommen"}).status_code == 200  # ohne Wirkung
    assert _rest(wp, "POST", f"/einsendung/{vorgang}/status", json={"status": "abgeholt"}).json()["status"] == "uebernommen"
    konflikt = _rest(wp, "POST", f"/einsendung/{vorgang}/status", json={"status": "erledigt"})
    assert konflikt.status_code == 409 and konflikt.json()["data"]["aktuell"] == "uebernommen"
    assert _rest(wp, "POST", f"/einsendung/{vorgang}/status", json={"status": "vorbereitet"}).status_code == 400
    assert _rest(wp, "POST", "/einsendung/T000000-AAAAA/status", json={"status": "erledigt"}).status_code == 404
    assert _rest(wp, "GET", "/einsendung/T000000-AAAAA").status_code == 404
    # direkt abschließen ohne „abgeholt“ geht auch (vorbereitet führt nur der Radar)
    zweite = _vorgang(absenden(wp, wp_cli, seite, "kontakt", {"nachricht": "Spam?"}))
    assert _rest(wp, "POST", f"/einsendung/{zweite}/status", json={"status": "spam"}).json()["status"] == "spam"
    zeilen = wp_cli(f"global $wpdb; echo wp_json_encode( $wpdb->get_col( \"SELECT CONCAT(wer, ':', notiz) FROM \" . tamil_site_einsendung_protokoll_tabelle() . \" WHERE aktion = 'status' AND vorgangsnummer = '{vorgang}' ORDER BY id\" ) );")
    assert json.loads(zeilen) == [f"{wp.user}:nach=abgeholt", f"{wp.user}:nach=uebernommen"]


# --- Löschfrist und Admin-Liste -----------------------------------------------------------------------------------

def test_loeschfrist(wp, wp_cli, seite):
    code = r"""
    global $wpdb;
    $t = tamil_site_einsendung_tabelle();
    $neu = function ( $status, $tage, $mit_bild = false ) use ( $wpdb, $t ) {
        $bild = null;
        if ( $mit_bild ) {
            $name = bin2hex( random_bytes( 16 ) ) . '.png';
            $img  = imagecreatetruecolor( 2, 2 ); imagepng( $img, tamil_site_einsendung_bildordner() . $name );
            $bild = array( 'datei' => $name, 'typ' => 'image/png', 'groesse' => 1, 'sha256' => '' );
        }
        $v = tamil_site_einsendung_speichern( array( 'art' => 'beitrag', 'name' => 'Test', 'email' => 't@example.test', 'felder' => array(),
            'einwilligung_fassung' => 'test', 'bild' => $bild, 'ip_hash' => 'x' ) );
        $wpdb->update( $t, array( 'status' => $status, 'abgeschlossen_at' => gmdate( 'Y-m-d H:i:s', time() - $tage * DAY_IN_SECONDS ),
            'eingang_at' => gmdate( 'Y-m-d H:i:s', time() - ( $tage + 2 ) * DAY_IN_SECONDS ) ), array( 'vorgangsnummer' => $v ) );
        return array( $v, $bild ? tamil_site_einsendung_bildordner() . $bild['datei'] : '' );
    };
    $f = array(
        'alt_uebernommen' => $neu( 'uebernommen', 91, true ),
        'alt_abgelehnt'   => $neu( 'abgelehnt', 95 ),
        'frisch_erledigt' => $neu( 'erledigt', 89 ),
        'alt_spam'        => $neu( 'spam', 8 ),
        'frisch_spam'     => $neu( 'spam', 6 ),
    );
    $offen = $neu( 'eingegangen', 0 );
    $wpdb->update( $t, array( 'abgeschlossen_at' => null ), array( 'vorgangsnummer' => $offen[0] ) );
    $f['offen'] = $offen;
    $bild_vorher = is_file( $f['alt_uebernommen'][1] );
    $zaehler = tamil_site_einsendungen_aufraeumen();
    $da = array();
    foreach ( $f as $k => $x ) { $da[ $k ] = (bool) tamil_site_einsendung_zeile( $x[0] ); }
    echo wp_json_encode( array( 'da' => $da, 'zaehler' => $zaehler, 'bild_vorher' => $bild_vorher, 'bild_nachher' => is_file( $f['alt_uebernommen'][1] ),
        'ip' => $wpdb->get_var( $wpdb->prepare( "SELECT ip_hash FROM {$t} WHERE vorgangsnummer = %s", $f['frisch_erledigt'][0] ) ),
        'protokoll' => $wpdb->get_row( 'SELECT wer, aktion, notiz FROM ' . tamil_site_einsendung_protokoll_tabelle() . ' ORDER BY id DESC LIMIT 1', ARRAY_A ) ) );
    """
    r = _json(wp_cli, code)
    assert r["da"] == {"alt_uebernommen": False, "alt_abgelehnt": False, "frisch_erledigt": True, "alt_spam": False,
                       "frisch_spam": True, "offen": True}
    assert r["bild_vorher"] is True and r["bild_nachher"] is False
    assert r["zaehler"]["geloescht"] >= 2 and r["zaehler"]["spam"] >= 1 and r["zaehler"]["ip_hash"] >= 1
    assert r["ip"] is None  # IP-Hash nach 24 Stunden entfernt
    assert r["protokoll"]["wer"] == "cron" and r["protokoll"]["aktion"] == "loeschfrist"


def test_admin_liste_nur_lesend(wp, wp_cli, wp_sitzung, seite):
    vorgang = _vorgang(absenden(wp, wp_cli, seite, "kontakt", {"nachricht": "Notfall-Ansicht"}))
    liste = wp_sitzung.get(f"{wp.url}/wp-admin/tools.php?page=tamil-einsendungen", timeout=30)
    assert liste.status_code == 200 and vorgang in liste.text
    einzeln = wp_sitzung.get(f"{wp.url}/wp-admin/tools.php?page=tamil-einsendungen&vorgang={vorgang}", timeout=30).text
    assert "Notfall-Ansicht" in einzeln and PERSON["email"] in einzeln
    # einziges Formular auf der Seite: Einwilligungstext; keine Knöpfe für den Status
    wrap = einzeln[einzeln.index('<div class="wrap">'):]
    assert wrap.count("<form") == 1 and 'action="options.php"' in wrap
    assert 'name="status"' not in wrap and "ablehnen" not in wrap.lower()
    # der Radar-Benutzer (ohne manage_options) sieht die Seite nicht
    assert requests.get(f"{wp.url}/wp-admin/tools.php?page=tamil-einsendungen", auth=wp.auth, timeout=30, allow_redirects=False).status_code in (302, 403)

