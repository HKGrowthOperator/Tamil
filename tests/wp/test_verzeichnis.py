"""Verzeichnis (Festlegung F2): öffentliche Liste und Profile, Formulare in tamil-site, REST für den Radar in
tamil-radar, Abnahmefälle aus T4.

Gegen ein lokales WordPress (wordpress/dev/setup.sh + serve.sh). Der Schalter „verzeichnis“ wird für einzelne Aufrufe
über die Test-Kopfzeile eingeschaltet (nur in der Umgebung local wirksam). Alle Angaben sind erfunden (example.test).
"""

import html as html_mod
import json
import re
import secrets

import pytest
import requests

AN = {"X-Tamil-Funktionen": "verzeichnis"}
NS = "/wp-json/tamil-radar/v1/verzeichnis"
EINSENDER = {"vz_einsender_name": "Erika Beispiel", "vz_einsender_email": "erika@example.test", "vz_berechtigung": "inhaber"}


def _json(wp_cli, code: str):
    return json.loads(wp_cli(code))


@pytest.fixture
def seite(wp, wp_cli):
    """Veröffentlichte Seite mit [tamil_verzeichnis]; danach Seite, neue Einträge und neue Einsendungen entfernen."""
    start = _json(wp_cli, "global $wpdb; echo wp_json_encode( array( (int) $wpdb->get_var( 'SELECT MAX(id) FROM ' . tamil_site_vz_tabelle() ),"
                          " (int) $wpdb->get_var( \"SELECT MAX(ID) FROM {$wpdb->posts}\" ) ) );")
    wp_cli("global $wpdb; $wpdb->query( $wpdb->prepare( 'UPDATE ' . tamil_site_vz_tabelle() . ' SET ip_hash = NULL WHERE ip_hash = %s', tamil_site_vz_ip_hash( '127.0.0.1' ) ) );")
    daten = _json(wp_cli, "$id = wp_insert_post( array( 'post_type' => 'page', 'post_status' => 'publish', 'post_title' => 'Verzeichnis Test',"
                          " 'post_name' => 'verzeichnis-test-' . wp_rand(), 'post_content' => '[tamil_verzeichnis]' ) );"
                          " echo wp_json_encode( array( 'id' => $id, 'url' => get_permalink( $id ) ) );")
    yield daten["url"]
    wp_cli(f"wp_delete_post( {daten['id']}, true ); global $wpdb;"
           f"foreach ( get_posts( array( 'post_type' => TAMIL_SITE_VZ_TYP, 'post_status' => 'any', 'numberposts' => -1, 'fields' => 'ids' ) ) as $p ) {{ if ( $p > {start[1]} ) {{ wp_delete_post( $p, true ); }} }}"
           f"$wpdb->query( 'DELETE FROM ' . tamil_site_vz_tabelle() . ' WHERE id > {start[0]}' );")


def _form_wert(html: str, name: str) -> str:
    m = re.search(rf'name="{re.escape(name)}" value="([^"]*)"', html)
    assert m, name
    return m.group(1)


def absenden(wp_cli, url: str, felder: dict, *, typ="neu", eintrag=0, oeffentlich=("adresse", "telefon", "email", "website", "oeffnungszeiten"),
             einsender=None, einwilligung=True, falle="", zeit=None, nonce=None, fassung=None, extra=None) -> requests.Response:
    ziel = f"{url}?vz_formular={typ}" + (f"&vz_eintrag={eintrag}" if eintrag else "")
    seite_html = requests.get(ziel, headers=AN, timeout=30).text
    daten = {
        "vz_typ": typ, "vz_eintrag": str(eintrag),
        "vz_nonce": _form_wert(seite_html, "vz_nonce") if nonce is None else nonce,
        "vz_zeit": wp_cli("echo tamil_site_vz_zeitstempel( time() - 10 );") if zeit is None else zeit,
        "vz_fassung": _form_wert(seite_html, "vz_fassung") if fassung is None else fassung,
        "vz_webseite": falle,
        **(EINSENDER if einsender is None else einsender),
        **{f"vz[{k}]": v for k, v in felder.items()},
        **{f"vz_oeffentlich[{k}]": "1" for k in oeffentlich},
        **(extra or {}),
    }
    if einwilligung:
        daten["vz_einwilligung"] = "1"
    return requests.post(ziel, data=daten, headers=AN, allow_redirects=False, timeout=30)


def _vorgang(antwort: requests.Response) -> str:
    meldung = re.search(r'<div class="vz-meldung".*?</div>', antwort.text, re.DOTALL)
    assert antwort.status_code == 303, meldung.group(0) if meldung else antwort.text[:1500]
    m = re.search(r"vz_eingang=(V\d{6}-[A-Z0-9]{5})", antwort.headers["Location"])
    assert m, antwort.headers["Location"]
    return m.group(1)


def _anzahl(wp_cli) -> int:
    return int(wp_cli("global $wpdb; echo (int) $wpdb->get_var( 'SELECT COUNT(*) FROM ' . tamil_site_vz_tabelle() );"))


def _rest(wp, methode: str, pfad: str, auth=None, **kw) -> requests.Response:
    kw.setdefault("headers", AN)
    return requests.request(methode, wp.url + NS + pfad, auth=auth if auth is not None else wp.auth, timeout=30, **kw)


def _einsendung(wp, vorgang: str) -> dict:
    r = _rest(wp, "GET", f"/einsendung/{vorgang}")
    assert r.status_code == 200, r.text
    return r.json()


def _verein(suffix: str, **mehr) -> dict:
    return {"name": f"Tamilischer Kulturverein Essen {suffix}", "art": "verein", "plz": "45127", "stadt": "Essen", "land": "DE",
            "bundesland_kanton": "Nordrhein-Westfalen", "telefon": "+49 201 1234567", "email": f"verein-{suffix}@example.test", **mehr}


def _anlegen(wp, vorgang: str, felder: dict) -> requests.Response:
    return _rest(wp, "POST", "/eintrag", json={"einsendung": vorgang, "felder": felder})


# --- Upgrade, Schalter, Rechte ------------------------------------------------------------------------------------

def test_upgrade_tabellen_rechte_kategorien(wp_cli):
    r = _json(wp_cli, "global $wpdb; $t = get_term_by( 'slug', 'tempel-kirche', TAMIL_SITE_VZ_KATEGORIE ); echo wp_json_encode( array( tamil_site_datenversion(),"
                      " $wpdb->get_var( $wpdb->prepare( 'SHOW TABLES LIKE %s', tamil_site_vz_tabelle() ) ),"
                      " get_role( 'radar' )->has_cap( 'tamil_verzeichnis_pflegen' ), get_role( 'administrator' )->has_cap( 'tamil_verzeichnis_pflegen' ),"
                      " get_role( 'radar' )->has_cap( 'edit_tamil_vz_eintraege' ), get_role( 'editor' )->has_cap( 'edit_tamil_vz_eintraege' ),"
                      " $t ? get_term_meta( $t->term_id, 'tamil_vz_art', true ) : null,"
                      " count( get_terms( array( 'taxonomy' => TAMIL_SITE_VZ_KATEGORIE, 'hide_empty' => false ) ) ),"
                      " (bool) wp_next_scheduled( 'tamil_site_vz_aufraeumen' ) ) );")
    assert r[0] >= 4 and r[1].endswith("tamil_vz_einsendungen")
    assert r[2] is True and r[3] is False and r[4] is False and r[5] is True  # nur die Radar-Rolle hat das REST-Recht
    assert r[6] == "tempel" and r[7] >= 20 and r[8] is True
    assert wp_cli("delete_option( 'tamil_site_datenversion' ); var_export( tamil_site_upgrade_ausfuehren() && tamil_site_upgrade_ausfuehren() );") == "true"
    assert int(wp_cli("echo count( get_terms( array( 'taxonomy' => TAMIL_SITE_VZ_KATEGORIE, 'hide_empty' => false ) ) );")) == r[7]


def test_schalter_aus(wp, wp_cli, seite):
    vorgang = _vorgang(absenden(wp_cli, seite, _verein(secrets.token_hex(3))))
    eintrag = _anlegen(wp, vorgang, {k: v for k, v in _verein("aus").items()}).json()["eintrag"]
    alt = wp_cli("echo wp_json_encode( get_option( 'tamil_site_funktionen', null ) );").strip()
    try:
        wp_cli("$f = (array) get_option( 'tamil_site_funktionen', array() ); $f['verzeichnis'] = false; update_option( 'tamil_site_funktionen', $f );")
        html = requests.get(seite, timeout=30).text
        assert "Das Verzeichnis steht derzeit nicht zur Verfügung." in html and "vz-liste" not in html and "verzeichnis.css" not in html
        assert requests.get(eintrag["link"], timeout=30).status_code == 404
        vorher = _anzahl(wp_cli)
        r = requests.post(seite, data={"vz_typ": "neu", "vz[name]": "x", "vz[art]": "verein", "vz_einwilligung": "1"}, allow_redirects=False, timeout=30)
        assert r.status_code == 200 and _anzahl(wp_cli) == vorher
        rest = _rest(wp, "GET", "/einsendungen", headers={})
        assert rest.status_code == 503 and rest.json()["code"] == "tamil_funktion_aus"
    finally:
        if alt == "null":
            wp_cli("delete_option( 'tamil_site_funktionen' );")
        else:
            wp_cli(f"update_option( 'tamil_site_funktionen', json_decode( '{alt}', true ) );")


def test_rechte_nur_radar(wp, wp_admin):
    assert _rest(wp, "GET", "/einsendungen", auth=()).status_code == 401
    for methode, pfad, body in (("GET", "/einsendungen", None), ("GET", "/eintraege", None),
                                ("POST", "/eintrag", {"einsendung": "V261113-AAAAA", "felder": {}})):
        r = _rest(wp, methode, pfad, auth=wp_admin, json=body)
        assert r.status_code == 403, (pfad, r.text)  # auch der Administrator nicht: nur die Radar-Rolle
    assert _rest(wp, "GET", "/einsendungen").status_code == 200
    # Kern-REST zeigt den Beitragstyp nicht
    assert requests.get(wp.url + "/wp-json/wp/v2/tamil_vz_eintrag", auth=wp.auth, timeout=30).status_code == 404


# --- Abnahme T4 ---------------------------------------------------------------------------------------------------

def test_t4_vorschlagen_freigeben_finden(wp, wp_cli, seite):
    s = secrets.token_hex(3)
    felder = _verein(s, beschreibung="Tanz, Musik und Sprachkurse.", oeffnungszeiten="Sa 10–14 Uhr", website="https://verein.example.test")
    vorgang = _vorgang(absenden(wp_cli, seite, felder))
    danke = requests.get(seite + f"?vz_eingang={vorgang}&vz_pruef=falsch", headers=AN, timeout=30).text
    assert vorgang not in danke  # Danke nur mit Prüfsumme

    liste = _rest(wp, "GET", "/einsendungen", params={"nach": 0, "anzahl": 100}).json()
    eins = next(e for e in liste["einsendungen"] if e["vorgangsnummer"] == vorgang)
    assert liste["naechster"] >= eins["id"]
    assert _rest(wp, "GET", "/einsendungen", params={"nach": eins["id"]}).json()["einsendungen"] == [] or all(
        e["id"] > eins["id"] for e in _rest(wp, "GET", "/einsendungen", params={"nach": eins["id"]}).json()["einsendungen"])
    assert eins["typ"] == "neu" and eins["status"] == "neu" and eins["berechtigung"] == "inhaber"
    assert eins["einsender"] == {"name": "Erika Beispiel", "email": "erika@example.test"}
    assert eins["einwilligung"] == {"erteilt": True, "fassung": "2026-11-vorlaeufig"}
    assert eins["felder"]["telefon"] == {"wert": "+49 201 1234567", "oeffentlich": True}
    assert "kategorie" not in eins["felder"]  # schlägt der Agent vor, nicht das Formular
    assert eins["regeln"] == {"fehlt": [], "formfehler": [], "dubletten": []}

    r = _rest(wp, "POST", f"/einsendung/{vorgang}/status", json={"status": "geprueft", "pruefung": {"kategorie_vorschlag": "verein-kultur"}})
    assert r.status_code == 200 and r.json()["status"] == "geprueft" and r.json()["pruefung"]["kategorie_vorschlag"] == "verein-kultur"

    r = _anlegen(wp, vorgang, {**felder, "kategorie": "verein-kultur"})
    assert r.status_code == 201, r.text
    eintrag = r.json()["eintrag"]
    assert eintrag["status"] == "veroeffentlicht" and eintrag["premium"] is False
    assert eintrag["felder"]["kategorie"] == "verein-kultur" and eintrag["felder"]["stadt"] == "Essen"
    assert r.json()["einsendung"]["status"] == "freigegeben" and r.json()["einsendung"]["eintrag_id"] == eintrag["id"]
    # Dieselbe Freigabe noch einmal: kein zweiter Eintrag
    zweit = _anlegen(wp, vorgang, felder)
    assert zweit.status_code == 200 and zweit.json()["bereits"] is True and zweit.json()["eintrag"]["id"] == eintrag["id"]

    name = felder["name"]
    for params in ({"vz_art": "verein"}, {"vz_stadt": "Essen"}, {"vz_suche": name}, {"vz_kategorie": "verein-kultur", "vz_land": "DE"},
                   {"vz_region": "Nordrhein-Westfalen"}):
        html = requests.get(seite, params=params, headers=AN, timeout=30).text
        assert html_mod.escape(name) in html, params
    assert name not in requests.get(seite, params={"vz_art": "tempel"}, headers=AN, timeout=30).text
    assert name not in requests.get(seite, params={"vz_land": "CH"}, headers=AN, timeout=30).text

    profil = requests.get(eintrag["link"], headers=AN, timeout=30)
    assert profil.status_code == 200
    assert "+49 201 1234567" in profil.text and "Sa 10–14 Uhr" in profil.text and "Änderung melden" in profil.text
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', profil.text, re.DOTALL).group(1))
    assert ld["@type"] == "Organization" and ld["address"]["postalCode"] == "45127" and ld["name"] == name


def test_t4_telefon_aendern_alt_neu_und_ablehnen(wp, wp_cli, seite):
    s = secrets.token_hex(3)
    eintrag = _anlegen(wp, _vorgang(absenden(wp_cli, seite, _verein(s))), _verein(s)).json()["eintrag"]
    neu = absenden(wp_cli, seite, {**eintrag["felder"], "telefon": "+49 201 7654321"}, typ="aenderung", eintrag=eintrag["id"])
    vorgang = _vorgang(neu)
    eins = _einsendung(wp, vorgang)
    assert eins["typ"] == "aenderung" and eins["eintrag_id"] == eintrag["id"]
    assert list(eins["felder"]) == ["telefon"]  # nur, was sich geändert hat
    alt = _rest(wp, "GET", f"/eintrag/{eintrag['id']}").json()
    assert alt["felder"]["telefon"] == "+49 201 1234567"  # alt neben neu im Cockpit

    veraltet = _rest(wp, "POST", f"/eintrag/{eintrag['id']}", json={"einsendung": vorgang, "stand": "0" * 16, "felder": {"telefon": "+49 201 7654321"}})
    assert veraltet.status_code == 409 and veraltet.json()["code"] == "tamil_vz_stand"
    r = _rest(wp, "POST", f"/eintrag/{eintrag['id']}", json={"einsendung": vorgang, "stand": alt["stand"], "felder": {"telefon": "+49 201 7654321"}})
    assert r.status_code == 200, r.text
    assert r.json()["eintrag"]["felder"]["telefon"] == "+49 201 7654321" and r.json()["eintrag"]["felder"]["email"] == alt["felder"]["email"]
    assert "+49 201 7654321" in requests.get(eintrag["link"], headers=AN, timeout=30).text

    # Ablehnen ändert nichts
    vorgang2 = _vorgang(absenden(wp_cli, seite, {**eintrag["felder"], "telefon": "+49 201 1111111"}, typ="aenderung", eintrag=eintrag["id"]))
    stand = _rest(wp, "GET", f"/eintrag/{eintrag['id']}").json()["stand"]
    assert _rest(wp, "POST", f"/einsendung/{vorgang2}/status", json={"status": "abgelehnt"}).json()["status"] == "abgelehnt"
    nach = _rest(wp, "GET", f"/eintrag/{eintrag['id']}").json()
    assert nach["stand"] == stand and nach["felder"]["telefon"] == "+49 201 7654321"
    spaet = _rest(wp, "POST", f"/eintrag/{eintrag['id']}", json={"einsendung": vorgang2, "stand": stand, "felder": {"telefon": "+49 201 1111111"}})
    assert spaet.status_code == 409 and spaet.json()["code"] == "tamil_vz_abgelehnt"
    assert _rest(wp, "POST", f"/einsendung/{vorgang2}/status", json={"status": "geprueft"}).status_code == 409


def test_t4_dublette_mit_verweis(wp, wp_cli, seite):
    s = secrets.token_hex(3)
    eintrag = _anlegen(wp, _vorgang(absenden(wp_cli, seite, _verein(s))), _verein(s)).json()["eintrag"]
    nochmal = _vorgang(absenden(wp_cli, seite, {**_verein(s), "name": f"Tamilischer Kulturverein Essen {s} e. V.", "telefon": "", "email": "x@example.test"}))
    dubletten = _einsendung(wp, nochmal)["regeln"]["dubletten"]
    assert {"eintrag_id": eintrag["id"], "grund": "name+plz"} in dubletten
    anders = _vorgang(absenden(wp_cli, seite, {**_verein(s), "name": "Sportverein Ganz Anders", "plz": "45128"}))
    assert all(d["eintrag_id"] != eintrag["id"] for d in _einsendung(wp, anders)["regeln"]["dubletten"])


def test_t4_premium_weder_formular_noch_schnittstelle(wp, wp_cli, wp_admin, seite):
    s = secrets.token_hex(3)
    vorgang = _vorgang(absenden(wp_cli, seite, _verein(s), extra={"vz[premium]": "1", "vz_premium": "1"}))
    assert "premium" not in _einsendung(wp, vorgang)["felder"]
    verboten = _anlegen(wp, vorgang, {**_verein(s), "premium": True})
    assert verboten.status_code == 403 and verboten.json()["code"] == "tamil_vz_premium_verboten"
    unbekannt = _anlegen(wp, vorgang, {**_verein(s), "bewertung": 5})
    assert unbekannt.status_code == 400 and unbekannt.json()["data"]["felder"] == ["bewertung"]
    eintrag = _anlegen(wp, vorgang, _verein(s)).json()["eintrag"]
    assert eintrag["premium"] is False
    # Kern-REST: Meta ist geschützt, der Typ nicht über /wp/v2 erreichbar
    assert requests.post(wp.url + f"/wp-json/wp/v2/posts/{eintrag['id']}", json={"meta": {"_tamil_vz_premium": "1"}},
                         auth=wp.auth, timeout=30).status_code in (400, 403, 404)
    # Ein Administrator setzt Premium: oben in der Liste, sichtbar gekennzeichnet
    s2 = secrets.token_hex(3)
    anderer = _anlegen(wp, _vorgang(absenden(wp_cli, seite, {**_verein(s2), "name": f"AAA Verein {s2}", "plz": "45130"})),
                       {**_verein(s2), "name": f"AAA Verein {s2}", "plz": "45130"}).json()["eintrag"]
    wp_cli(f"update_post_meta( {eintrag['id']}, '_tamil_vz_premium', '1' );")
    html = requests.get(seite, params={"vz_stadt": "Essen"}, headers=AN, timeout=30).text
    assert html.index(f"Kulturverein Essen {s}") < html.index(f"AAA Verein {s2}")
    li = re.search(rf'<li class="vz-eintrag vz-premium">\s*<a[^>]*>Tamilischer Kulturverein Essen {s}</a>\s*<span class="vz-premium-marke">Premium</span>', html)
    assert li, "Premium-Eintrag ohne Kennzeichen"
    assert _rest(wp, "GET", f"/eintrag/{eintrag['id']}").json()["premium"] is True
    assert _rest(wp, "GET", f"/eintrag/{anderer['id']}").json()["premium"] is False


def test_t4_unvollstaendig_wird_markiert_nicht_ergaenzt(wp, wp_cli, seite):
    s = secrets.token_hex(3)
    ohne_stadt = {k: v for k, v in _verein(s).items() if k != "stadt"}
    vorgang = _vorgang(absenden(wp_cli, seite, ohne_stadt))
    eins = _einsendung(wp, vorgang)
    assert "stadt" not in eins["felder"] and eins["regeln"]["fehlt"] == ["stadt"]
    r = _anlegen(wp, vorgang, ohne_stadt)
    assert r.status_code == 400 and r.json()["code"] == "tamil_vz_unvollstaendig" and r.json()["data"]["fehlt"] == ["stadt"]
    ohne_kontakt = {k: v for k, v in _verein(s).items() if k not in ("telefon", "email")}
    assert _anlegen(wp, vorgang, ohne_kontakt).json()["data"]["fehlt"] == ["kontakt"]
    assert _einsendung(wp, vorgang)["status"] == "neu"  # abgewiesene Freigabe verbraucht die Einsendung nicht


# --- Fehlerfälle ------------------------------------------------------------------------------------------------

def test_formular_pflicht_und_spamschutz(wp, wp_cli, seite):
    vorher = _anzahl(wp_cli)
    felder = _verein(secrets.token_hex(3))
    falle = absenden(wp_cli, seite, felder, falle="http://spam.example.test")
    assert falle.status_code == 200 and "nicht angenommen" in falle.text
    schnell = absenden(wp_cli, seite, felder, zeit=wp_cli("echo tamil_site_vz_zeitstempel();"))
    assert schnell.status_code == 200 and "schneller" in schnell.text
    gefaelscht = absenden(wp_cli, seite, felder, zeit="1700000000.aaaaaaaaaaaaaaaaaaaa")
    assert gefaelscht.status_code == 200 and "abgelaufen" in gefaelscht.text
    assert "abgelaufen" in absenden(wp_cli, seite, felder, nonce="falsch").text
    ohne = absenden(wp_cli, seite, felder, einwilligung=False)
    assert "Ohne Einwilligung" in ohne.text
    assert "Text der Einwilligung hat sich geändert" in absenden(wp_cli, seite, felder, fassung="alt").text
    leer = absenden(wp_cli, seite, {"plz": "45127"}, einsender={"vz_einsender_name": "", "vz_einsender_email": "kaputt"})
    for text in ("Namen des Eintrags", "eine der vier Arten", "euren Namen", "gültige E-Mail-Adresse für Rückfragen", "Inhaber oder berechtigt"):
        assert text in leer.text, text
    form = absenden(wp_cli, seite, {**felder, "plz": "123", "website": "javascript:alert(1)", "telefon": "abc", "art": "partei"})
    assert form.status_code == 200
    for text in ("fünf Ziffern", "mit https://", "Telefonnummer aus Ziffern", "eine der vier Arten"):
        assert text in form.text, text
    assert _anzahl(wp_cli) == vorher
    # Drossel: höchstens fünf je Stunde und Anschluss
    wp_cli("global $wpdb; for ( $i = 0; $i < 5; $i++ ) { $wpdb->insert( tamil_site_vz_tabelle(), array( 'vorgangsnummer' => 'VTEST-' . wp_rand(), 'typ' => 'neu',"
           " 'eingang_at' => gmdate( 'Y-m-d H:i:s' ), 'einsender_name' => 'x', 'einsender_email' => 'x@example.test', 'berechtigung' => 'hinweis',"
           " 'felder' => '{}', 'anmerkung' => '', 'pruefung' => '{}', 'entscheidung' => '{}', 'ip_hash' => tamil_site_vz_ip_hash( '127.0.0.1' ) ) ); }")
    gedrosselt = absenden(wp_cli, seite, felder)
    assert gedrosselt.status_code == 200 and "zu viele Einsendungen" in gedrosselt.text
    wp_cli("global $wpdb; $wpdb->query( \"DELETE FROM \" . tamil_site_vz_tabelle() . \" WHERE vorgangsnummer LIKE 'VTEST-%'\" );")


def test_escaping_formular_liste_profil(wp, wp_cli, seite):
    boese = '<script>alert(1)</script>"><img src=x onerror=alert(2)>'
    s = secrets.token_hex(3)
    # Zurückgezeigte Werte nach einem Fehler
    zurueck = absenden(wp_cli, seite, {**_verein(s), "name": "Verein " + boese, "plz": "1"})
    assert "<script>alert(1)" not in zurueck.text and "onerror=alert(2)>" not in zurueck.text
    felder = {**_verein(s), "name": f"Verein {s} " + boese, "beschreibung": "Text " + boese, "oeffnungszeiten": "Mo " + boese}
    vorgang = _vorgang(absenden(wp_cli, seite, felder))
    eintrag = _anlegen(wp, vorgang, felder).json()["eintrag"]
    for html in (requests.get(seite, params={"vz_suche": s}, headers=AN, timeout=30).text, requests.get(eintrag["link"], headers=AN, timeout=30).text):
        assert "<script>alert(1)" not in html and "<img src=x" not in html
    profil = requests.get(eintrag["link"], headers=AN, timeout=30).text
    ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', profil, re.DOTALL).group(1)
    assert "</script" not in ld and "<" not in ld


def test_nicht_oeffentliche_werte_werden_nicht_veroeffentlicht(wp, wp_cli, seite):
    s = secrets.token_hex(3)
    felder = _verein(s)
    vorgang = _vorgang(absenden(wp_cli, seite, felder, oeffentlich=("email",)))
    assert _einsendung(wp, vorgang)["felder"]["telefon"] == {"wert": "+49 201 1234567", "oeffentlich": False}
    r = _anlegen(wp, vorgang, felder)
    assert r.status_code == 409 and r.json()["code"] == "tamil_vz_nicht_oeffentlich" and r.json()["data"]["feld"] == "telefon"
    ok = _anlegen(wp, vorgang, {k: v for k, v in felder.items() if k != "telefon"})
    assert ok.status_code == 201 and ok.json()["eintrag"]["felder"]["telefon"] == ""


def test_entfernen_und_falsche_zuordnung(wp, wp_cli, seite):
    s = secrets.token_hex(3)
    neu_vorgang = _vorgang(absenden(wp_cli, seite, _verein(s)))
    eintrag = _anlegen(wp, neu_vorgang, _verein(s)).json()["eintrag"]
    vorgang = _vorgang(absenden(wp_cli, seite, {}, typ="aenderung", eintrag=eintrag["id"], extra={"vz_wunsch": "entfernen", "vz_anmerkung": "Verein aufgelöst"}))
    eins = _einsendung(wp, vorgang)
    assert eins["typ"] == "entfernen" and eins["felder"] == {} and eins["anmerkung"] == "Verein aufgelöst"
    # Falscher Typ: eine Entfernen-Einsendung legt nichts an und ändert nichts
    assert _anlegen(wp, vorgang, _verein(s)).json()["code"] == "tamil_vz_falsche_einsendung"
    stand = _rest(wp, "GET", f"/eintrag/{eintrag['id']}").json()["stand"]
    assert _rest(wp, "POST", f"/eintrag/{eintrag['id']}", json={"einsendung": vorgang, "stand": stand, "felder": {}}).status_code == 409
    # Ungültige Werte werden abgewiesen
    aend = _vorgang(absenden(wp_cli, seite, {**eintrag["felder"], "plz": "45139"}, typ="aenderung", eintrag=eintrag["id"]))
    falsch = _rest(wp, "POST", f"/eintrag/{eintrag['id']}", json={"einsendung": aend, "stand": stand, "felder": {"plz": "123"}})
    assert falsch.status_code == 400 and "plz" in falsch.json()["data"]["fehler"]
    r = _rest(wp, "POST", f"/eintrag/{eintrag['id']}/entfernen", json={"einsendung": vorgang, "stand": stand})
    assert r.status_code == 200 and r.json()["eintrag"]["status"] == "entfernt"
    assert requests.get(eintrag["link"], headers=AN, timeout=30).status_code == 404
    assert f"Kulturverein Essen {s}" not in requests.get(seite, params={"vz_stadt": "Essen"}, headers=AN, timeout=30).text
    assert _rest(wp, "GET", "/eintrag/999999999").status_code == 404


def test_loeschfrist_und_protokoll_ohne_personendaten(wp, wp_cli, seite):
    s = secrets.token_hex(3)
    vorgang = _vorgang(absenden(wp_cli, seite, _verein(s)))
    _anlegen(wp, vorgang, _verein(s))
    protokoll = wp_cli("global $wpdb; echo wp_json_encode( $wpdb->get_results( $wpdb->prepare( 'SELECT * FROM ' . tamil_site_vz_protokoll_tabelle() . ' WHERE vorgangsnummer = %s', '" + vorgang + "' ) ) );")
    assert "eingang" in protokoll and "angelegt" in protokoll and "ki-agent" in protokoll
    assert "Erika" not in protokoll and "example.test" not in protokoll
    wp_cli(f"global $wpdb; $wpdb->update( tamil_site_vz_tabelle(), array( 'eingang_at' => gmdate( 'Y-m-d H:i:s', time() - 91 * DAY_IN_SECONDS ) ), array( 'vorgangsnummer' => '{vorgang}' ) ); tamil_site_vz_aufraeumen();")
    assert _rest(wp, "GET", f"/einsendung/{vorgang}").status_code == 404
