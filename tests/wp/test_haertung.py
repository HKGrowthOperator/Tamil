"""Härtungen im Plugin tamil-site (Prüfliste vom 13.11.): Drossel je Anschluss in F2 und F3 wie in F1, Schalter erst
ab passender Datenversion, Umschreibregeln nach dem Registrieren der Beitragstypen.

Gegen ein lokales WordPress (wordpress/dev/setup.sh + serve.sh). Adressen aus den Dokumentationsnetzen (2001:db8::/32,
198.51.100.0/24, 203.0.113.0/24), alle Angaben erfunden (example.test).
"""

import json
import re
import secrets
import shlex
import subprocess
from html.parser import HTMLParser

import pytest
import requests
from wp_umgebung import URL, WP_CLI


def _json(wp_cli, code: str):
    return json.loads(wp_cli(code))


def _netz() -> str:
    """Zufälliges /64 aus 2001:db8::/32, damit Läufe einander nicht drosseln."""
    return f"2001:db8:{secrets.randbelow(0xffff):x}:{secrets.randbelow(0xffff):x}"


# --- 1. Drossel: F2 und F3 rechnen die Adresse wie F1 (IPv6 je /64, TAMIL_PROXY_ANZAHL) -----------------------------

_VZ_SENDEN = """
$_SERVER['REQUEST_METHOD'] = 'POST';
$start = (int) $GLOBALS['wpdb']->get_var( 'SELECT COALESCE( MAX(id), 0 ) FROM ' . tamil_site_vz_tabelle() );
$aus   = array();
foreach ( json_decode( '{{ADRESSEN}}', true ) as $i => $adresse ) {
	$_SERVER['REMOTE_ADDR'] = $adresse;
	$_POST = array(
		'vz_typ' => 'neu', 'vz_eintrag' => '0', 'vz_nonce' => wp_create_nonce( 'tamil_vz_neu' ),
		'vz_zeit' => tamil_site_vz_zeitstempel( time() - 10 ), 'vz_fassung' => tamil_site_vz_einwilligung()['fassung'],
		'vz_webseite' => '', 'vz_einsender_name' => 'Erika Beispiel', 'vz_einsender_email' => 'erika@example.test',
		'vz_berechtigung' => 'inhaber', 'vz_einwilligung' => '1',
		'vz' => array( 'name' => 'Drosselverein {{LAUF}} ' . $i, 'art' => 'verein', 'plz' => '45127', 'stadt' => 'Essen',
			'land' => 'DE', 'bundesland_kanton' => 'Nordrhein-Westfalen', 'telefon' => '+49 201 1234567',
			'email' => 'drossel-' . $i . '@example.test' ),
		'vz_oeffentlich' => array( 'telefon' => '1', 'email' => '1' ),
	);
	$r     = tamil_site_vz_formular_annehmen( 'neu' );
	$aus[] = is_string( $r ) ? 'angenommen' : ( '' !== $r['meldung'] ? $r['meldung'] : wp_json_encode( $r['fehler'] ) );
}
$GLOBALS['wpdb']->query( $GLOBALS['wpdb']->prepare( 'DELETE FROM %i WHERE id > %d', tamil_site_vz_tabelle(), $start ) );
echo wp_json_encode( $aus );
"""


def test_verzeichnis_drossel_je_ipv6_64(wp_cli):
    """Wechselnde Adressen aus einem /64 (ein Anschluss) dürfen die Drossel von fünf je Stunde nicht umgehen."""
    netz, anderes = _netz(), _netz()
    adressen = [f"{netz}::{i}" for i in range(1, 7)] + [f"{anderes}::1"]
    aus = _json(wp_cli, _VZ_SENDEN.replace("{{ADRESSEN}}", json.dumps(adressen)).replace("{{LAUF}}", secrets.token_hex(3)))
    assert aus[:5] == ["angenommen"] * 5, aus
    assert "zu viele Einsendungen" in aus[5], aus
    assert aus[6] == "angenommen", "anderer Anschluss bleibt frei"


def test_verzeichnis_nimmt_adressfunktion_von_f1(wp_cli):
    """Gleiche Adresse ergibt denselben Drossel-Schlüssel wie in F1 (eine Funktion, ein Netzbegriff)."""
    r = _json(wp_cli, "$_SERVER['REMOTE_ADDR'] = '2001:db8:aa:bb::1'; $a = tamil_site_vz_ip_hash( tamil_site_vz_client_ip() );"
                      " $_SERVER['REMOTE_ADDR'] = '2001:db8:aa:bb:ffff::2'; $b = tamil_site_vz_ip_hash( tamil_site_vz_client_ip() );"
                      " echo wp_json_encode( array( $a === $b, $a === tamil_site_einsendung_ip_hash( '2001:db8:aa:bb::7' ) ) );")
    assert r == [True, True]


_WB_DROSSEL = """
if ( ! defined( 'TAMIL_PROXY_ANZAHL' ) ) { define( 'TAMIL_PROXY_ANZAHL', {{PROXYS}} ); }
$fall = function ( $remote, $kette ) {
	$_SERVER['REMOTE_ADDR'] = $remote;
	$_SERVER['HTTP_X_FORWARDED_FOR'] = $kette;
};
$schluessel = array();
// Erster Besucher bucht so oft, wie die Drossel erlaubt.
call_user_func_array( $fall, json_decode( '{{VOLL}}', true ) );
$schluessel[] = tamil_site_werbung_drossel_schluessel();
set_transient( end( $schluessel ), TAMIL_SITE_WERBUNG_DROSSEL, HOUR_IN_SECONDS );
$aus = array();
foreach ( json_decode( '{{PRUEFEN}}', true ) as $p ) {
	call_user_func_array( $fall, $p );
	$schluessel[] = tamil_site_werbung_drossel_schluessel();
	$_POST = array();
	tamil_site_werbung_zustand( array( 'fehler' => array() ) );
	tamil_site_werbung_post_buchen();
	$aus[] = false !== strpos( implode( ' ', tamil_site_werbung_zustand()['fehler'] ), 'Zu viele Buchungen' );
}
foreach ( $schluessel as $s ) { delete_transient( $s ); }
echo wp_json_encode( array( defined( 'TAMIL_PROXY_ANZAHL' ) ? (int) TAMIL_PROXY_ANZAHL : null, $aus ) );
"""


def _wb_drossel(wp_cli, proxys: int, voll: list, pruefen: list):
    code = (_WB_DROSSEL.replace("{{PROXYS}}", str(proxys)).replace("{{VOLL}}", json.dumps(voll))
            .replace("{{PRUEFEN}}", json.dumps(pruefen)))
    konstante, aus = _json(wp_cli, code)
    if konstante != proxys:
        pytest.skip(f"TAMIL_PROXY_ANZAHL ist in wp-config.php fest auf {konstante}")
    return aus


def test_werbung_drossel_je_ipv6_64(wp_cli):
    netz, anderes = _netz(), _netz()
    aus = _wb_drossel(wp_cli, 0, [f"{netz}::1", ""], [[f"{netz}::2", ""], [f"{netz}:1:2:3:4", ""], [f"{anderes}::1", ""]])
    assert aus == [True, True, False], "gleiches /64 gedrosselt, anderes frei"


def test_werbung_drossel_beachtet_proxy_anzahl(wp_cli):
    """Hinter einem zusätzlichen öffentlichen Proxy (TAMIL_PROXY_ANZAHL=1) zählt der Besucher, nicht der Proxy."""
    proxy = "203.0.113.9"
    besucher = f"198.51.100.{secrets.randbelow(200) + 1}"
    anderer = f"198.51.100.{(int(besucher.rsplit('.', 1)[1]) % 200) + 2}"
    aus = _wb_drossel(wp_cli, 1, [proxy, besucher], [[proxy, besucher], [proxy, anderer]])
    assert aus == [True, False], "anderer Besucher hinter demselben Proxy darf nicht gedrosselt sein"


# --- 2. Funktionsschalter erst ab der Datenversion des Bausteins ----------------------------------------------------

@pytest.fixture
def datenversion_drei(wp_cli):
    """Lage nach einem gescheiterten Upgrade: Datenversion 3 (Verzeichnis-Tabellen fehlen noch), Wartezeit läuft, damit
    Seitenaufrufe das Upgrade nicht sofort nachholen. Danach alle Optionen tamil_site_* wie vorher (das Formular speichert
    die ganze Gruppe: Werbeplätze, Weiterleitungen, SEO) und Upgrade auf den vollen Stand."""
    muster = "$wpdb->esc_like( 'tamil_site_' ) . '%'"
    sicher = wp_cli("global $wpdb; echo base64_encode( wp_json_encode( $wpdb->get_results( $wpdb->prepare("
                    f" 'SELECT option_name, option_value, autoload FROM %i WHERE option_name LIKE %s', $wpdb->options, {muster} ), ARRAY_A ) ) );")
    wp_cli("update_option( 'tamil_site_datenversion', 3 ); update_option( 'tamil_site_upgrade_fehler', time() );"
           " update_option( 'tamil_site_funktionen', array() );")
    yield
    wp_cli(f"global $wpdb; $alt = json_decode( base64_decode( '{sicher}' ), true );"
           f" $wpdb->query( $wpdb->prepare( 'DELETE FROM %i WHERE option_name LIKE %s', $wpdb->options, {muster} ) );"
           " foreach ( $alt as $zeile ) { $wpdb->replace( $wpdb->options, $zeile ); } wp_cache_flush();"
           " update_option( 'tamil_site_datenversion', 3 ); tamil_site_upgrade_ausfuehren();")
    assert wp_cli("echo tamil_site_datenversion();") == wp_cli("echo TAMIL_SITE_DATENVERSION;")


class _Formular(HTMLParser):
    """Felder eines Formulars so, wie der Browser sie absendet (nicht angehakte Kästchen und gesperrte Felder fehlen)."""

    def __init__(self, action: str):
        super().__init__(convert_charrefs=True)
        self.action, self.drin, self.felder, self._text, self._select = action, False, [], None, None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form":
            self.drin = a.get("action") == self.action
        if not self.drin or "disabled" in a:
            return
        name, typ = a.get("name"), a.get("type", "text")
        if tag == "input" and name and typ != "submit" and (typ not in ("checkbox", "radio") or "checked" in a):
            self.felder.append((name, a.get("value") or ("on" if typ == "checkbox" else "")))
        elif tag == "textarea" and name:
            self._text = [name, ""]
        elif tag == "select" and name:
            self._select = [name, None]
        elif tag == "option" and self._select is not None and ("selected" in a or self._select[1] is None):
            self._select[1] = a.get("value", "")

    def handle_data(self, data):
        if self._text is not None:
            self._text[1] += data

    def handle_endtag(self, tag):
        if tag == "form":
            self.drin = False
        elif tag == "textarea" and self._text is not None:
            self.felder.append((self._text[0], self._text[1]))
            self._text = None
        elif tag == "select" and self._select is not None:
            self.felder.append((self._select[0], self._select[1] or ""))
            self._select = None


def _formularfelder(html: str, action: str) -> list:
    p = _Formular(action)
    p.feed(html)
    return p.felder


def test_schalter_vor_datenversion_bleibt_aus(wp_cli, datenversion_drei):
    r = _json(wp_cli, "update_option( 'tamil_site_funktionen', array( 'verzeichnis' => true, 'werbung' => true, 'einreichungen' => true ) );"
                      " echo wp_json_encode( array( tamil_site_funktion_an( 'verzeichnis' ), tamil_site_funktion_an( 'werbung' ),"
                      " tamil_site_funktion_an( 'einreichungen' ) ) );")
    assert r == [False, True, True], "Verzeichnis braucht Datenversion 4"


def test_schalter_vor_datenversion_auch_nicht_ueber_testkopf(wp_cli, datenversion_drei):
    """Auch die lokale Test-Kopfzeile schaltet einen Baustein ohne Tabellen nicht ein."""
    r = _json(wp_cli, "$_SERVER['HTTP_X_TAMIL_FUNKTIONEN'] = 'verzeichnis,werbung';"
                      " echo wp_json_encode( array( wp_get_environment_type(), tamil_site_funktion_an( 'verzeichnis' ), tamil_site_funktion_an( 'werbung' ) ) );")
    if r[0] != "local":
        pytest.skip("Test-Kopfzeile wirkt nur in der Umgebung local")
    assert r[1:] == [False, True]


def test_admin_formular_schaltet_baustein_ohne_daten_nicht_ein(wp_cli, wp_sitzung, datenversion_drei):
    html = wp_sitzung.get(f"{URL}/wp-admin/options-general.php?page=tamil-site", timeout=30).text
    feld = re.search(r'<input[^>]*name="tamil_site_funktionen\[verzeichnis\]"[^>]*>', html)
    assert feld and "disabled" in feld.group(0), "Schalter vor Datenversion 4 nicht wählbar"
    assert "Datenversion" in html
    # Absenden wie der Browser (ganzes Formular); das gesperrte Feld zusätzlich von Hand (Manipulation).
    lesen = "echo wp_json_encode( array( tamil_site_settings(), get_option( 'tamil_site_redirects' ) ) );"
    vorher = wp_cli(lesen)
    felder = _formularfelder(html, "options.php") + [("tamil_site_funktionen[verzeichnis]", "1"), ("tamil_site_funktionen[werbung]", "1")]
    assert ("option_page", "tamil_site") in felder
    r = wp_sitzung.post(f"{URL}/wp-admin/options.php", data=felder, allow_redirects=False, timeout=30)
    assert r.status_code == 302
    stand = _json(wp_cli, "echo wp_json_encode( get_option( 'tamil_site_funktionen' ) );")
    assert stand.get("verzeichnis") is False and stand.get("werbung") is True, stand
    def ohne_leere(w):
        if isinstance(w, dict):
            return {k: ohne_leere(v) for k, v in w.items() if ohne_leere(v) not in ("", {}, [])}
        if isinstance(w, list):
            return [ohne_leere(v) for v in w] if w else {}
        return w

    assert ohne_leere(json.loads(wp_cli(lesen))) == ohne_leere(json.loads(vorher)), "übrige Einstellungen bleiben beim Speichern unverändert"


@pytest.fixture
def weiterleitungen_sichern(wp_cli):
    """Weiterleitungen (CSV und Tabelle) vor dem Test merken und danach genau so zurückschreiben."""
    alt = wp_cli("echo base64_encode( wp_json_encode( array( get_option( 'tamil_site_redirects_csv', null ), get_option( 'tamil_site_redirects', null ) ) ) );")
    yield
    wp_cli(f"$a = json_decode( base64_decode( '{alt}' ), true );"
           " foreach ( array( 'tamil_site_redirects_csv', 'tamil_site_redirects' ) as $i => $n ) {"
           " if ( null === $a[ $i ] ) { delete_option( $n ); } else { update_option( $n, $a[ $i ], false ); } }")


def test_speichern_behaelt_weiterleitungen_ohne_csv(wp_cli, wp_sitzung, weiterleitungen_sichern):
    """B5 Nebenbefund 1: Steht nur die Tabelle (Übernahme ohne CSV), leert das Speichern des Formulars sie nicht. Das
    Formular zeigt die aktive Tabelle als CSV, und fehlt das Feld ganz (manipuliert), bleibt alles, wie es war."""
    tabelle = {"/category/alt-probe/": "/category/events/", "/seite-alt-probe/": "/kontakt/"}
    wp_cli("delete_option( 'tamil_site_redirects_csv' );"
           f" update_option( 'tamil_site_redirects', json_decode( '{json.dumps(tabelle)}', true ), false );")
    lesen = "echo wp_json_encode( get_option( 'tamil_site_redirects' ) );"
    seite = f"{URL}/wp-admin/options-general.php?page=tamil-site"
    html = wp_sitzung.get(seite, timeout=30).text
    felder = _formularfelder(html, "options.php")
    csv = dict(felder).get("tamil_site_redirects_csv", "")
    assert "/category/alt-probe/" in csv and "/seite-alt-probe/" in csv, "Formular zeigt die aktive Tabelle"
    assert wp_sitzung.post(f"{URL}/wp-admin/options.php", data=felder, allow_redirects=False, timeout=30).status_code == 302
    assert _json(wp_cli, lesen) == tabelle, "Speichern des ganzen Formulars behält die Weiterleitungen"
    r = requests.get(f"{URL}/category/alt-probe/", allow_redirects=False, timeout=30)
    assert r.status_code == 301 and r.headers["Location"].rstrip("/").endswith("/category/events")

    ohne = [(n, w) for n, w in _formularfelder(wp_sitzung.get(seite, timeout=30).text, "options.php") if n != "tamil_site_redirects_csv"]
    assert wp_sitzung.post(f"{URL}/wp-admin/options.php", data=ohne, allow_redirects=False, timeout=30).status_code == 302
    assert _json(wp_cli, lesen) == tabelle, "fehlt das Feld, bleiben die Weiterleitungen"


# --- 3. Umschreibregeln erst, wenn alle Beitragstypen registriert sind ----------------------------------------------

def _wp(*args: str) -> str:
    return subprocess.run([*shlex.split(WP_CLI), *args], capture_output=True, text=True, check=True).stdout.strip()


_REGEL_VZ = "$r = get_option( 'rewrite_rules' ); echo wp_json_encode( is_array( $r ) && (bool) preg_grep( '/tamil_vz_eintrag=/', $r ) );"


@pytest.fixture
def vz_eintrag(wp_cli):
    daten = _json(wp_cli, "$id = wp_insert_post( array( 'post_type' => TAMIL_SITE_VZ_TYP, 'post_status' => 'publish',"
                          " 'post_title' => 'Regelprobe ' . wp_rand(), 'post_content' => '' ) );"
                          " echo wp_json_encode( array( 'id' => $id, 'url' => get_permalink( $id ) ) );")
    yield daten
    wp_cli(f"wp_delete_post( {daten['id']}, true );")


def test_aktivieren_und_deaktivieren_erneuern_regeln_nach_registrierung(wp, wp_cli, vz_eintrag):
    if not WP_CLI:
        pytest.skip("WP_TEST_WP_CLI fehlt")
    assert "/verzeichnis/" in vz_eintrag["url"], "Permalinks müssen eingeschaltet sein"
    try:
        _wp("plugin", "deactivate", "tamil-site")
        requests.get(f"{URL}/", timeout=30)  # erster Aufruf ohne Plugin erzeugt die Regeln
        assert _json(wp_cli, _REGEL_VZ) is False, "nach dem Deaktivieren keine Regeln des Verzeichnisses mehr"
    finally:
        _wp("plugin", "activate", "tamil-site")
    requests.get(f"{URL}/", timeout=30)
    assert _json(wp_cli, _REGEL_VZ) is True, "nach dem Aktivieren fehlen die Regeln des Verzeichnisses"
    profil = requests.get(vz_eintrag["url"], headers={"X-Tamil-Funktionen": "verzeichnis"}, timeout=30)
    assert profil.status_code == 200
