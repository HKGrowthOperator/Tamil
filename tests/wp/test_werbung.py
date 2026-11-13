"""Plugin tamil-site, Werbebuchung (Festlegung F3, Datenmodell §14, Integrationen §11).

Läuft gegen ein lokales WordPress (wordpress/dev/setup.sh + serve.sh). Stripe ist immer der Fake aus stripe_fake.php
(als mu-plugin mit Zufalls-Geheimnis für die Dauer eines Tests), nie das Netz. Gezielt gegen Fehler: falsch signierter,
veralteter und doppelter Webhook, bezahlt ohne Prüfung, geprüft ohne Zahlung, Ablauf, Doppelbuchung (auch gleichzeitig).
"""

import hashlib
import hmac
import json
import os
import re
import secrets
import shlex
import struct
import subprocess
import threading
import time
import zlib
from pathlib import Path

import pytest
import requests
from wp_umgebung import URL, WP_CLI

HIER = Path(__file__).resolve().parent
SEITE = "werben-test"


def _php(code: str):
    """PHP im lokalen WordPress ausführen, Ausgabe als JSON lesen."""
    aus = subprocess.run([*shlex.split(WP_CLI), "eval", code], capture_output=True, text=True, check=True).stdout
    return json.loads(aus) if aus.strip() else None


def _wp_dir() -> Path:
    m = re.search(r"--path=(\S+)", WP_CLI)
    if not m:
        pytest.skip("WP_TEST_WP_CLI ohne --path=")
    return Path(m.group(1))


def png(w: int, h: int, rauschen: bool = False) -> bytes:
    zeile = (lambda: os.urandom(w * 3)) if rauschen else (lambda: b"\xc0\x20\x20" * w)
    roh = b"".join(b"\x00" + zeile() for _ in range(h))

    def chunk(t: bytes, d: bytes) -> bytes:
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(roh, 1 if rauschen else 9)) + chunk(b"IEND", b""))


def gif(w: int, h: int) -> bytes:
    return b"GIF89a" + struct.pack("<HH", w, h) + b"\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00;"


def signiert(body: bytes, geheimnis: str, t: int | None = None) -> str:
    t = int(time.time()) if t is None else t
    sig = hmac.new(geheimnis.encode(), f"{t}.".encode() + body, hashlib.sha256).hexdigest()
    return f"t={t},v1={sig}"


class Werbung:
    def __init__(self, geheimnis: str, seite: str):
        self.geheimnis = geheimnis
        self.seite = seite

    # --- Daten ---------------------------------------------------------------------------------------------------
    def buchung(self, ident) -> dict:
        feld = "id" if isinstance(ident, int) else "nummer"
        return _php(f"""global $wpdb; echo wp_json_encode( $wpdb->get_row( $wpdb->prepare( 'SELECT * FROM %i WHERE {feld} = %s',
            tamil_site_werbung_tabelle( 'buchungen' ), '{ident}' ), ARRAY_A ) );""")

    def tage(self, platz: str) -> list[str]:
        return _php(f"""global $wpdb; echo wp_json_encode( $wpdb->get_col( $wpdb->prepare( 'SELECT tag FROM %i WHERE platz = %s ORDER BY tag',
            tamil_site_werbung_tabelle( 'tage' ), '{platz}' ) ) );""")

    def protokoll(self, bid: int) -> list[str]:
        return [z["was"] for z in _php(f"echo wp_json_encode( tamil_site_werbung_protokoll_lesen( {bid} ) );")]

    def anlegen(self, platz="leaderboard", ab=0, tage=1, zahlung="bezahlt", pruefung="freigegeben") -> int:
        """Buchung direkt anlegen (ohne Formular), Start heute + ab Tage."""
        return _php(f"""global $wpdb;
            $start = tamil_site_werbung_plus_tage( tamil_site_werbung_heute(), {ab} );
            $wpdb->insert( tamil_site_werbung_tabelle( 'buchungen' ), array( 'nummer' => tamil_site_werbung_nummer(), 'platz' => '{platz}',
              'laufzeit' => {tage}, 'start' => $start, 'ende' => tamil_site_werbung_plus_tage( $start, {tage} - 1 ),
              'reserviert_bis' => gmdate( 'Y-m-d H:i:s', time() + 600 ), 'firma' => 'Testfirma Direkt', 'rechnungsadresse' => 'Teststraße 1',
              'email' => 'test@example.test', 'werbemittel_desktop' => 'tamil-werbung/test/d.png', 'werbemittel_mobil' => 'tamil-werbung/test/m.png',
              'ziel_url' => 'https://example.org/ziel', 'betrag' => 5000, 'zahlung' => '{zahlung}', 'pruefung' => '{pruefung}',
              'stripe_zahlung' => 'pi_test_direkt', 'ablehnungsgrund' => '', 'warnung' => '', 'kunden_hash' => '', 'erstellt_at' => gmdate( 'Y-m-d H:i:s' ) ) );
            $id = (int) $wpdb->insert_id;
            echo wp_json_encode( tamil_site_werbung_tage_belegen( tamil_site_werbung_buchung( $id ) ) ? $id : 0 );""")

    def aufrufe(self) -> list[dict]:
        return _php("echo wp_json_encode( get_option( 'tamil_test_stripe_aufrufe', array() ) );") or []

    def stripe_bezahlt(self, session_id: str) -> None:
        _php(f"""$s = get_option( 'tamil_test_stripe_sessions', array() ); $s['{session_id}']['payment_status'] = 'paid';
            $s['{session_id}']['status'] = 'complete'; update_option( 'tamil_test_stripe_sessions', $s, false );""")

    # --- HTTP ----------------------------------------------------------------------------------------------------
    def webhook(self, ereignis: dict, kopf: str | None = None) -> requests.Response:
        body = json.dumps(ereignis).encode()
        return requests.post(f"{URL}/wp-json/tamil-site/v1/werbung/stripe", data=body, timeout=30,
                             headers={"Content-Type": "application/json",
                                      "Stripe-Signature": signiert(body, self.geheimnis) if kopf is None else kopf})

    def bezahlt_meldung(self, b: dict, evt: str | None = None, **ueber) -> dict:
        obj = {"id": b["stripe_session"], "object": "checkout.session", "client_reference_id": b["nummer"],
               "payment_status": "paid", "status": "complete", "amount_total": int(b["betrag"]), "currency": "eur",
               "payment_intent": "pi_test_" + b["nummer"]}
        obj.update(ueber)
        return {"id": evt or "evt_test_" + secrets.token_hex(8), "type": "checkout.session.completed",
                "data": {"object": obj}}

    def formular(self, s: requests.Session, platz: str, laufzeit: int, start: str) -> tuple[str, str]:
        """Schritt 3/4 aufrufen: (Adresse, Nonce)."""
        url = f"{self.seite}?wb=buchen&platz={platz}&laufzeit={laufzeit}&start={start}"
        html = s.get(url, timeout=30).text
        m = re.search(r'name="_wpnonce" value="([^"]+)"[^>]*>\s*<input type="hidden" name="tamil_wb_aktion" value="buchen"', html)
        assert m, "Formular mit Nonce fehlt"
        return url, m.group(1)

    def buchen(self, s: requests.Session, platz="sidebar", laufzeit=7, start=None, bilder=None, **felder):
        start = start or self.fruehester()
        url, nonce = self.formular(s, platz, laufzeit, start)
        daten = {"tamil_wb_aktion": "buchen", "_wpnonce": nonce, "platz": platz, "laufzeit": str(laufzeit),
                 "start": start, "firma": "Testfirma GmbH", "ansprechperson": "Erika Test",
                 "rechnungsadresse": "Teststraße 1\n12345 Teststadt", "email": "kunde@example.test",
                 "telefon": "", "ust_id": "", "ziel_url": "https://example.org/angebot"}
        daten.update(felder)
        if bilder is None:
            bilder = {"werbemittel_desktop": ("b.png", png(300, 600), "image/png")}
        return s.post(url, data=daten, files=bilder, allow_redirects=False, timeout=60)

    def fruehester(self, plus: int = 0) -> str:
        return _php(f"echo wp_json_encode( tamil_site_werbung_plus_tage( tamil_site_werbung_fruehester_start(), {plus} ) );")


@pytest.fixture
def wb(wp, wp_cli):
    """Werbung an, Fake-Stripe als mu-plugin, Testpreise, eigene Seite; danach alles zurück."""
    mu = _wp_dir() / "wp-content" / "mu-plugins"
    mu.mkdir(exist_ok=True)
    geheimnis = "whsec_test_" + secrets.token_hex(16)
    datei = mu / "tamil-test-stripe-fake.php"
    datei.write_text((HIER / "stripe_fake.php").read_text(encoding="utf-8").replace("__GEHEIMNIS__", geheimnis), encoding="utf-8")
    alt = _php("""echo wp_json_encode( array( get_option( 'tamil_site_funktionen', array() ), get_option( 'tamil_site_werbung_angebote', null ) ) );""")
    seite_id = _php(f"""tamil_site_upgrade_ausfuehren();
        $f = (array) get_option( 'tamil_site_funktionen', array() ); $f['werbung'] = true; update_option( 'tamil_site_funktionen', $f );
        update_option( 'tamil_site_werbung_angebote', array( 'laufzeiten' => array( 1, 7 ), 'vorlauf' => 2, 'bedingungen_fassung' => 'Test 1',
          'plaetze' => array( 'sidebar' => array( 'aktiv' => true, 'preise' => array( 1 => 5000, 7 => 20000 ) ),
                              'leaderboard' => array( 'aktiv' => true, 'preise' => array( 7 => 30000 ) ) ) ), false );
        delete_option( 'tamil_test_stripe_aufrufe' ); delete_option( 'tamil_test_stripe_sessions' ); delete_option( 'tamil_test_stripe_erstattung' );
        $alt = get_page_by_path( '{SEITE}', OBJECT, 'page' ); if ( $alt ) {{ wp_delete_post( $alt->ID, true ); }}
        echo wp_json_encode( wp_insert_post( array( 'post_type' => 'page', 'post_status' => 'publish', 'post_title' => 'Werben (Test)',
          'post_name' => '{SEITE}', 'post_content' => '[tamil_werbung]' ) ) );""")
    yield Werbung(geheimnis, f"{URL}/{SEITE}/")
    _php(f"""global $wpdb;
        $ids = $wpdb->get_col( $wpdb->prepare( "SELECT id FROM %i WHERE firma LIKE 'Testfirma%%'", tamil_site_werbung_tabelle( 'buchungen' ) ) );
        foreach ( $ids as $id ) {{
          $b = tamil_site_werbung_buchung( (int) $id );
          if ( ! str_starts_with( $b['werbemittel_desktop'], 'tamil-werbung/test/' ) ) {{ tamil_site_werbung_datei_loeschen( $b['werbemittel_desktop'] ); tamil_site_werbung_datei_loeschen( $b['werbemittel_mobil'] ); }}
          foreach ( array( 'tage', 'statistik', 'protokoll' ) as $t ) {{ $wpdb->delete( tamil_site_werbung_tabelle( $t ), array( 'buchung_id' => (int) $id ) ); }}
          $wpdb->delete( tamil_site_werbung_tabelle( 'buchungen' ), array( 'id' => (int) $id ) );
        }}
        $wpdb->query( $wpdb->prepare( "DELETE FROM %i WHERE ereignis_id LIKE 'evt_test_%%'", tamil_site_werbung_tabelle( 'ereignisse' ) ) );
        wp_delete_post( {int(seite_id)}, true );
        delete_option( 'tamil_test_stripe_aufrufe' ); delete_option( 'tamil_test_stripe_sessions' ); delete_option( 'tamil_test_stripe_erstattung' );
        echo '';""")
    _php(f"""update_option( 'tamil_site_funktionen', json_decode( '{json.dumps(alt[0] or {})}', true ) ?: array() );
        $a = json_decode( '{json.dumps(alt[1])}', true ); if ( null === $a ) {{ delete_option( 'tamil_site_werbung_angebote' ); }} else {{ update_option( 'tamil_site_werbung_angebote', $a, false ); }}""")
    datei.unlink()


def _zur_zahlung(wb: Werbung, s: requests.Session, **kw) -> dict:
    """Formular → Zusammenfassung → Bedingungen → Stripe. Gibt die Buchung zurück."""
    r = wb.buchen(s, **kw)
    assert r.status_code == 303, r.text[-2000:]
    ziel = r.headers["Location"]
    nummer = re.search(r"nummer=(W[A-Z0-9]+)", ziel).group(1)
    html = s.get(ziel, timeout=30).text
    assert "Zusammenfassung" in html and nummer in html
    nonce = re.search(r'name="_wpnonce" value="([^"]+)"[^>]*>\s*<input type="hidden" name="tamil_wb_aktion" value="bezahlen"', html).group(1)
    r = s.post(wb.seite, data={"tamil_wb_aktion": "bezahlen", "_wpnonce": nonce, "nummer": nummer, "bedingungen": "1"},
               allow_redirects=False, timeout=30)
    assert r.status_code == 303 and r.headers["Location"].startswith("https://checkout.stripe.com/"), r.text[-1500:]
    return wb.buchung(nummer)


# --- Tabellen, Schalter ----------------------------------------------------------------------------------------------

def test_tabellen_und_eindeutiger_tag_je_platz(wb):
    r = _php("""global $wpdb; $t = tamil_site_werbung_tabelle( 'tage' );
        $a = $wpdb->query( $wpdb->prepare( 'INSERT IGNORE INTO %i (platz, tag, buchung_id) VALUES (%s, %s, %d)', $t, 'footer', '2099-01-01', 999001 ) );
        $b = $wpdb->query( $wpdb->prepare( 'INSERT IGNORE INTO %i (platz, tag, buchung_id) VALUES (%s, %s, %d)', $t, 'footer', '2099-01-01', 999002 ) );
        $wpdb->query( $wpdb->prepare( 'DELETE FROM %i WHERE tag = %s', $t, '2099-01-01' ) );
        echo wp_json_encode( array( (int) $a, (int) $b, (int) get_option( 'tamil_site_datenversion' ) >= 2 ) );""")
    assert r == [1, 0, True]


def test_schalter_aus_nichts_oeffentlich(wb):
    bid = wb.anlegen("leaderboard", 0, 1)
    _php("$f = (array) get_option( 'tamil_site_funktionen' ); $f['werbung'] = false; update_option( 'tamil_site_funktionen', $f );")
    assert 'wb-werbung' not in requests.get(wb.seite, timeout=30).text
    assert f'data-wb-buchung="{bid}"' not in requests.get(URL + "/", timeout=30).text
    assert wb.webhook({"id": "evt_test_aus", "type": "checkout.session.completed", "data": {"object": {}}}).status_code == 503
    assert _php("echo wp_json_encode( is_wp_error( tamil_site_stripe_aufruf( 'GET', 'checkout/sessions/x' ) ) );") is True
    assert wb.aufrufe() == []


def test_preisseite_platzhalter_und_naechster_termin(wb):
    html = requests.get(wb.seite, timeout=30).text
    assert "Preis folgt" in html and "Platzhalter" in html
    assert "200,00 €" in html  # sidebar 7 Tage
    zeile = re.search(r"<tr><th scope=\"row\">Half Page</th>.*?</tr>", html, re.S).group(0)
    assert "wb=buchen" in zeile and re.search(r"\d\d\.\d\d\.\d{4}", zeile)
    zeile = re.search(r"<tr><th scope=\"row\">Billboard</th>.*?</tr>", html, re.S).group(0)
    assert "wb=buchen" not in zeile  # ohne Preis nicht buchbar


# --- Aktiv-Funktion --------------------------------------------------------------------------------------------------

def test_aktiv_nur_wenn_bezahlt_und_geprueft_und_nicht_pausiert_und_im_zeitraum(wb):
    r = _php("""$h = '2030-06-10';
        $b = array( 'zahlung' => 'bezahlt', 'pruefung' => 'freigegeben', 'pausiert' => 0, 'beendet_at' => null, 'start' => '2030-06-10', 'ende' => '2030-06-16' );
        $f = array(
          'alles'               => tamil_site_werbung_aktiv( $b, $h ),
          'bezahlt_ungeprueft'  => tamil_site_werbung_aktiv( array_merge( $b, array( 'pruefung' => 'offen' ) ), $h ),
          'geprueft_unbezahlt'  => tamil_site_werbung_aktiv( array_merge( $b, array( 'zahlung' => 'offen' ) ), $h ),
          'erstattet'           => tamil_site_werbung_aktiv( array_merge( $b, array( 'zahlung' => 'erstattet' ) ), $h ),
          'abgelehnt'           => tamil_site_werbung_aktiv( array_merge( $b, array( 'pruefung' => 'abgelehnt' ) ), $h ),
          'pausiert'            => tamil_site_werbung_aktiv( array_merge( $b, array( 'pausiert' => 1 ) ), $h ),
          'beendet'             => tamil_site_werbung_aktiv( array_merge( $b, array( 'beendet_at' => '2030-06-11 10:00:00' ) ), $h ),
          'vor_start'           => tamil_site_werbung_aktiv( $b, '2030-06-09' ),
          'letzter_tag'         => tamil_site_werbung_aktiv( $b, '2030-06-16' ),
          'nach_ende'           => tamil_site_werbung_aktiv( $b, '2030-06-17' ),
        );
        echo wp_json_encode( $f );""")
    assert r == {"alles": True, "bezahlt_ungeprueft": False, "geprueft_unbezahlt": False, "erstattet": False,
                 "abgelehnt": False, "pausiert": False, "beendet": False, "vor_start": False, "letzter_tag": True,
                 "nach_ende": False}


def test_bezahlt_ohne_pruefung_erscheint_nicht_nach_freigabe_schon(wb):
    bid = wb.anlegen("leaderboard", 0, 1, zahlung="bezahlt", pruefung="offen")
    assert f'data-wb-buchung="{bid}"' not in requests.get(URL + "/", timeout=30).text
    assert _php(f"echo wp_json_encode( tamil_site_werbung_stand( tamil_site_werbung_buchung( {bid} ) ) );") == "in_pruefung"
    assert _php(f"echo wp_json_encode( tamil_site_werbung_freigeben( {bid} ) );") is True
    html = requests.get(URL + "/", timeout=30).text
    assert f'data-wb-buchung="{bid}"' in html and 'rel="sponsored noopener"' in html
    assert "tamil-werbung/test/m.png" in html  # Bild fürs Handy über <source>


def test_geprueft_ohne_zahlung_erscheint_nicht_und_ist_nicht_freizugeben(wb):
    bid = wb.anlegen("leaderboard", 0, 1, zahlung="offen", pruefung="freigegeben")
    assert f'data-wb-buchung="{bid}"' not in requests.get(URL + "/", timeout=30).text
    bid2 = wb.anlegen("footer", 0, 1, zahlung="offen", pruefung="offen")
    assert _php(f"echo wp_json_encode( tamil_site_werbung_freigeben( {bid2} ) );") is False


def test_ablauf_ein_tag_dann_wieder_eigenanzeige(wb):
    bid = wb.anlegen("leaderboard", 0, 1)
    html = requests.get(URL + "/", timeout=30).text
    assert f'data-wb-buchung="{bid}"' in html
    r = _php(f"""$b = tamil_site_werbung_buchung( {bid} ); $morgen = tamil_site_werbung_plus_tage( tamil_site_werbung_heute(), 1 );
        echo wp_json_encode( array( tamil_site_werbung_aktiv( $b, $morgen ), null === tamil_site_werbung_laufend( 'leaderboard', $morgen ), tamil_site_werbung_stand( $b, $morgen ) ) );""")
    assert r == [False, True, "beendet"]
    # Buchung „von gestern“: heute steht wieder die Eigenanzeige
    _php(f"""global $wpdb; $g = tamil_site_werbung_plus_tage( tamil_site_werbung_heute(), -1 );
        $wpdb->update( tamil_site_werbung_tabelle( 'buchungen' ), array( 'start' => $g, 'ende' => $g ), array( 'id' => {bid} ) );
        $wpdb->update( tamil_site_werbung_tabelle( 'tage' ), array( 'tag' => $g ), array( 'buchung_id' => {bid} ) );""")
    html = requests.get(URL + "/", timeout=30).text
    assert f'data-wb-buchung="{bid}"' not in html and "ad-leaderboard ad-anzeige" in html


def test_pausieren_fortsetzen_beenden(wb):
    bid = wb.anlegen("leaderboard", 0, 7)
    assert _php(f"echo wp_json_encode( array( tamil_site_werbung_pausieren( {bid}, true ), tamil_site_werbung_pausieren( {bid}, true ) ) );") == [True, False]
    assert f'data-wb-buchung="{bid}"' not in requests.get(URL + "/", timeout=30).text
    assert _php(f"echo wp_json_encode( tamil_site_werbung_pausieren( {bid}, false ) );") is True
    assert f'data-wb-buchung="{bid}"' in requests.get(URL + "/", timeout=30).text
    assert _php(f"echo wp_json_encode( tamil_site_werbung_beenden( {bid} ) );") is True
    assert f'data-wb-buchung="{bid}"' not in requests.get(URL + "/", timeout=30).text
    assert len(wb.tage("leaderboard")) == 1  # nur heute bleibt belegt, die folgenden Tage sind frei


# --- Buchungsablauf --------------------------------------------------------------------------------------------------

def test_werbemittel_typ_groesse_und_masse_werden_geprueft(wb):
    s = requests.Session()
    faelle = {
        "falsche Maße": ("b.png", png(300, 250), "image/png"),
        "GIF": ("b.png", gif(300, 600), "image/png"),
        "kein Bild": ("b.png", b"<?php echo 1;", "image/png"),
        "zu groß": ("b.png", png(300, 600, rauschen=True), "image/png"),
    }
    for name, datei in faelle.items():
        r = wb.buchen(s, bilder={"werbemittel_desktop": datei})
        assert r.status_code == 200, name
        assert "wb-fehler" in r.text, name
    assert wb.tage("sidebar") == []
    r = wb.buchen(s, ziel_url="javascript:alert(1)")
    assert r.status_code == 200 and "Zieladresse" in r.text
    # zwei Bilder nötig: Leaderboard ohne Handy-Bild
    r = wb.buchen(s, platz="leaderboard", laufzeit=7, bilder={"werbemittel_desktop": ("d.png", png(728, 90), "image/png")})
    assert r.status_code == 200 and "Handy" in r.text
    assert wb.tage("leaderboard") == []


def test_belegte_tage_sind_nicht_waehlbar_und_vorlauf(wb):
    start = wb.fruehester(3)
    bid = wb.anlegen("sidebar", 0, 1)  # heute: vor dem Vorlauf, ohnehin nicht wählbar
    _php(f"""global $wpdb; $wpdb->update( tamil_site_werbung_tabelle( 'buchungen' ), array( 'start' => '{start}', 'ende' => '{start}' ), array( 'id' => {bid} ) );
        $wpdb->update( tamil_site_werbung_tabelle( 'tage' ), array( 'tag' => '{start}' ), array( 'buchung_id' => {bid} ) );""")
    html = requests.get(f"{wb.seite}?wb=buchen&platz=sidebar&laufzeit=7", timeout=30).text
    starts = re.findall(r'<option value="(\d{4}-\d\d-\d\d)"', html)
    assert starts and starts[0] == wb.fruehester(4)  # jeder 7-Tage-Zeitraum ab Tag 0 bis 3 enthält den belegten Tag
    for s in starts[:10]:
        assert not (s <= start <= _php(f"echo wp_json_encode( tamil_site_werbung_plus_tage( '{s}', 6 ) );")), s
    heute = _php("echo wp_json_encode( tamil_site_werbung_heute() );")
    assert heute not in starts
    html = requests.get(f"{wb.seite}?wb=buchen&platz=sidebar&laufzeit=7&start={heute}", timeout=30).text
    assert 'name="tamil_wb_aktion" value="buchen"' not in html  # kein Formular für diesen Tag
    # auch von Hand abgeschickt: der Vorlauf wird auf dem Server geprüft
    s = requests.Session()
    url, nonce = wb.formular(s, "sidebar", 7, starts[0])
    r = s.post(url, data={"tamil_wb_aktion": "buchen", "_wpnonce": nonce, "platz": "sidebar", "laufzeit": "7", "start": heute,
                          "firma": "Testfirma Vorlauf", "ansprechperson": "V", "rechnungsadresse": "V", "email": "v@example.test",
                          "ziel_url": "https://example.org"},
               files={"werbemittel_desktop": ("b.png", png(300, 600), "image/png")}, allow_redirects=False, timeout=60)
    assert r.status_code == 200 and "nicht wählbar" in r.text and wb.tage("sidebar") == [start]


def test_buchung_zahlung_webhook_freigabe_ende_zu_ende(wb, wp_sitzung):
    s = requests.Session()
    b = _zur_zahlung(wb, s)
    assert b["zahlung"] == "offen" and b["stripe_session"].startswith("cs_test_")
    assert len(wb.tage("sidebar")) == 7
    assert b["bedingungen_fassung"] == "Test 1" and b["bedingungen_at"]
    aufruf = [a for a in wb.aufrufe() if a["pfad"] == "checkout/sessions"][0]
    assert aufruf["body"]["line_items"][0]["price_data"]["unit_amount"] == "20000"
    assert aufruf["body"]["client_reference_id"] == b["nummer"] and aufruf["idempotenz"] == "checkout-" + b["nummer"]
    assert "{CHECKOUT_SESSION_ID}" in aufruf["body"]["success_url"]
    # nur Kennungen gespeichert, kein Kartendatum
    assert not any(k in json.dumps(b) for k in ("4242", "card_number", "cvc"))

    # Meldung von Stripe (signiert) → bezahlt, in Prüfung
    wb.stripe_bezahlt(b["stripe_session"])
    r = wb.webhook(wb.bezahlt_meldung(b))
    assert r.status_code == 200 and r.json()["ergebnis"] == "bezahlt"
    b = wb.buchung(b["nummer"])
    assert b["zahlung"] == "bezahlt" and b["pruefung"] == "offen"

    # Rückkehr von Stripe: Abgleich, dann geheimer Link
    r = s.get(f"{wb.seite}?wb=rueckkehr&nummer={b['nummer']}&session_id={b['stripe_session']}", allow_redirects=False, timeout=30)
    assert r.status_code == 303 and "buchung=" in r.headers["Location"]
    token = re.search(r"buchung=([a-f0-9]{48})", r.headers["Location"]).group(1)
    assert hashlib.sha256(token.encode()).hexdigest() == b["kunden_hash"] and token not in json.dumps(wb.buchung(b["nummer"]))
    html = requests.get(r.headers["Location"], timeout=30)
    assert "bezahlt, in Prüfung" in html.text and "Zahlungsbeleg von Stripe" in html.text
    assert html.headers.get("Referrer-Policy") == "no-referrer" and "noindex" in html.text
    assert f'data-wb-buchung="{b["id"]}"' not in requests.get(URL + "/", timeout=30).text

    # Freigabe in wp-admin (Nonce und Recht), dann am Starttag sichtbar
    seite = wp_sitzung.get(f"{URL}/wp-admin/admin.php?page=tamil-werbung&buchung={b['id']}", timeout=30).text
    assert b["nummer"] in seite and "Testfirma GmbH" in seite
    nonce = re.search(r'name="_wpnonce" value="([^"]+)"[^>]*>.*?name="aktion" value="freigeben"', seite, re.S).group(1)
    r = wp_sitzung.post(f"{URL}/wp-admin/admin-post.php", data={"action": "tamil_wb_verwalten", "_wpnonce": nonce,
                        "buchung": b["id"], "aktion": "freigeben"}, allow_redirects=False, timeout=30)
    assert r.status_code == 302 and "ergebnis=ok" in r.headers["Location"]
    b = wb.buchung(b["nummer"])
    assert b["pruefung"] == "freigegeben"
    assert _php(f"echo wp_json_encode( tamil_site_werbung_stand( tamil_site_werbung_buchung( {b['id']} ) ) );") == "geplant"
    assert _php(f"echo wp_json_encode( tamil_site_werbung_aktiv( tamil_site_werbung_buchung( {b['id']} ), '{b['start']}' ) );") is True
    assert "Werbemittel geprüft und freigegeben" in wb.protokoll(b["id"])


def test_admin_handlung_ohne_nonce_oder_recht_abgewiesen(wb, wp_sitzung):
    bid = wb.anlegen("footer", 0, 1, pruefung="offen")
    r = wp_sitzung.post(f"{URL}/wp-admin/admin-post.php", data={"action": "tamil_wb_verwalten", "buchung": bid,
                        "aktion": "freigeben", "_wpnonce": "falsch"}, allow_redirects=False, timeout=30)
    assert r.status_code in (403, 302) and "ergebnis=ok" not in r.headers.get("Location", "")
    r = requests.post(f"{URL}/wp-admin/admin-post.php", data={"action": "tamil_wb_verwalten", "buchung": bid,
                      "aktion": "freigeben"}, allow_redirects=False, timeout=30)
    assert "ergebnis=ok" not in r.headers.get("Location", "")
    assert wb.buchung(bid)["pruefung"] == "offen"


# --- Webhook ---------------------------------------------------------------------------------------------------------

def test_webhook_falsche_signatur_veraltet_und_doppelt(wb):
    b = _zur_zahlung(wb, requests.Session())
    meldung = wb.bezahlt_meldung(b, evt="evt_test_" + secrets.token_hex(6))
    body = json.dumps(meldung).encode()
    falsch = [
        "",
        signiert(body, "whsec_falsch"),
        signiert(body, wb.geheimnis, int(time.time()) - 400),  # älter als 5 Minuten
        signiert(body, wb.geheimnis, int(time.time()) + 400),
        "t=" + str(int(time.time())) + ",v0=" + hmac.new(wb.geheimnis.encode(), f"{int(time.time())}.".encode() + body, hashlib.sha256).hexdigest(),
        signiert(body + b" ", wb.geheimnis),  # Signatur über anderen Rohtext
    ]
    for kopf in falsch:
        r = requests.post(f"{URL}/wp-json/tamil-site/v1/werbung/stripe", data=body, timeout=30,
                          headers={"Content-Type": "application/json", "Stripe-Signature": kopf})
        assert r.status_code == 400, kopf
    assert wb.buchung(b["nummer"])["zahlung"] == "offen"

    # Betrag passt nicht → nicht bezahlt, Warnung
    r = wb.webhook(wb.bezahlt_meldung(b, amount_total=1))
    assert r.status_code == 200 and wb.buchung(b["nummer"])["zahlung"] == "offen" and wb.buchung(b["nummer"])["warnung"]
    # fremde Session derselben Buchungsnummer → nichts
    r = wb.webhook(wb.bezahlt_meldung(b, id="cs_test_fremd"))
    assert r.json()["ergebnis"] == "unbekannt" and wb.buchung(b["nummer"])["zahlung"] == "offen"

    assert wb.webhook(meldung).json()["ergebnis"] == "bezahlt"
    zweit = wb.webhook(meldung)
    assert zweit.status_code == 200 and zweit.json()["ergebnis"] == "doppelt"
    # dieselbe Zahlung mit neuer Ereignis-ID: idempotent
    assert wb.webhook(wb.bezahlt_meldung(b)).json()["ergebnis"] == "unveraendert"
    assert [p for p in wb.protokoll(b["id"]) if p.startswith("bezahlt")] == ["bezahlt (Meldung checkout.session.completed)"]


def test_signaturpruefung_funktion(wb):
    r = _php("""$g = 'whsec_x'; $t = 1700000000; $body = '{"id":"evt_1"}'; $sig = hash_hmac( 'sha256', $t . '.' . $body, $g );
        echo wp_json_encode( array(
          tamil_site_stripe_signatur_gueltig( $body, "t=$t,v1=$sig", $g, $t + 299 ),
          tamil_site_stripe_signatur_gueltig( $body, "t=$t,v1=falsch,v1=$sig", $g, $t ),
          tamil_site_stripe_signatur_gueltig( $body, "t=$t,v1=$sig", $g, $t + 301 ),
          tamil_site_stripe_signatur_gueltig( $body, "t=$t,v1=$sig", '', $t ),
          tamil_site_stripe_signatur_gueltig( $body, "v1=$sig", $g, $t ) ) );""")
    assert r == [True, True, False, False, False]


# --- Abbruch, Ablauf, Ablehnung --------------------------------------------------------------------------------------

def test_abbruch_auf_der_bezahlseite_gibt_tage_frei(wb):
    s = requests.Session()
    b = _zur_zahlung(wb, s)
    r = s.get(f"{wb.seite}?wb=abbruch&nummer={b['nummer']}", timeout=30)
    assert "Die Zahlung wurde abgebrochen" in r.text
    assert wb.buchung(b["nummer"])["zahlung"] == "fehlgeschlagen" and wb.tage("sidebar") == []
    assert any(a["pfad"].endswith("/expire") for a in wb.aufrufe())
    # verspätete Meldung „abgelaufen“ ändert nichts mehr
    r = wb.webhook({"id": "evt_test_" + secrets.token_hex(6), "type": "checkout.session.expired",
                    "data": {"object": {"id": b["stripe_session"], "client_reference_id": b["nummer"]}}})
    assert r.json()["ergebnis"] == "unveraendert"


def test_reservierung_verfaellt_nach_35_minuten(wb):
    b = _zur_zahlung(wb, requests.Session())
    assert len(wb.tage("sidebar")) == 7
    _php(f"""global $wpdb; $wpdb->update( tamil_site_werbung_tabelle( 'buchungen' ), array( 'reserviert_bis' => gmdate( 'Y-m-d H:i:s', time() - 1 ) ), array( 'id' => {b['id']} ) );""")
    html = requests.get(f"{wb.seite}?wb=buchen&platz=sidebar&laufzeit=7", timeout=30).text  # Verfügbarkeit räumt ab
    assert wb.tage("sidebar") == [] and b["start"] in re.findall(r'<option value="(\d{4}-\d\d-\d\d)"', html)
    assert wb.buchung(b["nummer"])["zahlung"] == "fehlgeschlagen"
    # Zahlung kommt trotzdem (verspätete Meldung): Tage werden erneut belegt, wenn frei
    wb.stripe_bezahlt(b["stripe_session"])
    assert wb.webhook(wb.bezahlt_meldung(b)).json()["ergebnis"] == "bezahlt"
    assert len(wb.tage("sidebar")) == 7 and wb.buchung(b["nummer"])["warnung"] == ""


def test_ablehnung_erstattet_voll_und_gibt_tage_frei(wb):
    s = requests.Session()
    b = _zur_zahlung(wb, s)
    wb.stripe_bezahlt(b["stripe_session"])
    wb.webhook(wb.bezahlt_meldung(b))
    assert _php(f"echo wp_json_encode( tamil_site_werbung_ablehnen( {b['id']}, 'Motiv verstößt gegen die Werberichtlinien' ) );") is True
    n = wb.buchung(b["nummer"])
    assert n["zahlung"] == "erstattet" and n["pruefung"] == "abgelehnt" and wb.tage("sidebar") == []
    erst = [a for a in wb.aufrufe() if a["pfad"] == "refunds"]
    assert len(erst) == 1 and erst[0]["body"]["payment_intent"] == "pi_test_" + b["nummer"] and erst[0]["idempotenz"] == "erstattung-" + b["nummer"]
    assert "amount" not in erst[0]["body"]  # volle Erstattung
    token = _php(f"echo wp_json_encode( tamil_site_werbung_neues_token( {b['id']} ) );")
    html = requests.get(f"{wb.seite}?buchung={token}", timeout=30).text
    assert "Motiv verstößt gegen die Werberichtlinien" in html and "erstattet" in html
    # zweite Ablehnung ändert nichts
    assert _php(f"echo wp_json_encode( tamil_site_werbung_ablehnen( {b['id']}, 'nochmal' ) );") is False


def test_gescheiterte_erstattung_wird_warnung_und_kann_wiederholt_werden(wb):
    bid = wb.anlegen("footer", 5, 1, pruefung="offen")
    _php("update_option( 'tamil_test_stripe_erstattung', 'fehler', false );")
    assert _php(f"echo wp_json_encode( tamil_site_werbung_ablehnen( {bid}, 'unzulässig' ) );") is True
    b = wb.buchung(bid)
    assert b["zahlung"] == "bezahlt" and "Erstattung gescheitert" in b["warnung"] and wb.tage("footer") == []
    _php("update_option( 'tamil_test_stripe_erstattung', 'succeeded', false );")
    assert _php(f"echo wp_json_encode( tamil_site_werbung_erstatten( {bid} ) );") is True
    b = wb.buchung(bid)
    assert b["zahlung"] == "erstattet" and b["warnung"] == ""


# --- Doppelbuchung ---------------------------------------------------------------------------------------------------

def test_doppelbuchung_ueberlappender_zeitraum_scheitert(wb):
    start = wb.fruehester(1)
    erste = wb.buchen(requests.Session(), start=start)
    assert erste.status_code == 303
    html = requests.get(f"{wb.seite}?wb=buchen&platz=sidebar&laufzeit=1", timeout=30).text
    angeboten = re.findall(r'<option value="(\d{4}-\d\d-\d\d)"', html)
    assert wb.fruehester(0) in angeboten and wb.fruehester(4) not in angeboten  # belegte Tage nicht wählbar …
    r = _php(f"""echo wp_json_encode( tamil_site_werbung_reservieren( array( 'platz' => 'sidebar', 'laufzeit' => 1, 'start' => tamil_site_werbung_plus_tage( '{start}', 3 ),
        'firma' => 'Testfirma Zwei', 'ansprechperson' => 'X', 'rechnungsadresse' => 'Y', 'email' => 'x@example.test', 'werbemittel_desktop' => 'tamil-werbung/test/d.png',
        'werbemittel_mobil' => '', 'ziel_url' => 'https://example.org' ) )->get_error_code() );""")
    assert r == "belegt"  # … und auch direkt nicht reservierbar
    assert len(wb.tage("sidebar")) == 7


def test_gleichzeitige_buchungen_genau_eine_gewinnt(wb):
    for runde in range(3):
        start = wb.fruehester(10 * runde)
        sitzungen = [requests.Session() for _ in range(4)]
        vorbereitet = []
        for s in sitzungen:
            url, nonce = wb.formular(s, "sidebar", 7, start)
            vorbereitet.append((s, url, nonce))
        sperre = threading.Barrier(len(vorbereitet))
        ergebnisse = []

        def los(s, url, nonce):
            daten = {"tamil_wb_aktion": "buchen", "_wpnonce": nonce, "platz": "sidebar", "laufzeit": "7", "start": start,
                     "firma": "Testfirma Rennen", "ansprechperson": "R", "rechnungsadresse": "R", "email": "r@example.test",
                     "ziel_url": "https://example.org"}
            sperre.wait()
            r = s.post(url, data=daten, files={"werbemittel_desktop": ("b.png", png(300, 600), "image/png")},
                       allow_redirects=False, timeout=60)
            ergebnisse.append(r.status_code)

        faeden = [threading.Thread(target=los, args=v) for v in vorbereitet]
        for f in faeden:
            f.start()
        for f in faeden:
            f.join()
        assert sorted(ergebnisse) == [200, 200, 200, 303], (runde, ergebnisse)
    ids = _php("""global $wpdb; echo wp_json_encode( $wpdb->get_col( $wpdb->prepare( "SELECT id FROM %i WHERE firma = 'Testfirma Rennen'", tamil_site_werbung_tabelle( 'buchungen' ) ) ) );""")
    assert len(ids) == 3 and len(wb.tage("sidebar")) == 21


# --- Zählung, Kundenlink ---------------------------------------------------------------------------------------------

def test_einblendungen_und_klicks_je_tag(wb, wp_sitzung):
    bid = wb.anlegen("leaderboard", 0, 1)
    for _ in range(3):
        assert requests.post(f"{URL}/wp-json/tamil-site/v1/werbung/einblendung", data={"buchung": bid}, timeout=30).status_code == 204
    r = requests.get(f"{URL}/wp-json/tamil-site/v1/werbung/klick/{bid}", allow_redirects=False, timeout=30)
    assert r.status_code == 302 and r.headers["Location"] == "https://example.org/ziel"
    assert not r.cookies
    nicht = wb.anlegen("footer", 0, 1, pruefung="offen")  # nicht aktiv: zählt nicht, Ziel noch nicht freigegeben
    requests.post(f"{URL}/wp-json/tamil-site/v1/werbung/einblendung", data={"buchung": nicht}, timeout=30)
    r = requests.get(f"{URL}/wp-json/tamil-site/v1/werbung/klick/{nicht}", allow_redirects=False, timeout=30)
    assert r.headers["Location"].rstrip("/") == URL
    stat = _php(f"echo wp_json_encode( array( tamil_site_werbung_statistik( {bid} ), tamil_site_werbung_statistik( {nicht} ) ) );")
    assert [(z["einblendungen"], z["klicks"]) for z in stat[0]] == [(3, 1)] and stat[1] == []
    seite = wp_sitzung.get(f"{URL}/wp-admin/admin.php?page=tamil-werbung&buchung={bid}", timeout=30).text
    export = re.search(r'href="([^"]*action=tamil_wb_export[^"]*)"', seite).group(1).replace("&#038;", "&").replace("&amp;", "&")
    csv = wp_sitzung.get(export, timeout=30).text
    assert csv.splitlines()[0] == "buchung;tag;einblendungen;klicks" and csv.splitlines()[1].endswith(";3;1")


def test_kundenlink_nur_gehasht_und_wiederfinden(wb):
    s = requests.Session()
    b = _zur_zahlung(wb, s)
    r = s.get(f"{wb.seite}?wb=rueckkehr&nummer={b['nummer']}", allow_redirects=False, timeout=30)
    alt = re.search(r"buchung=([a-f0-9]{48})", r.headers["Location"]).group(1)
    assert "reserviert, Zahlung offen" in requests.get(f"{wb.seite}?buchung={alt}", timeout=30).text
    assert "nicht (mehr) gültig" in requests.get(f"{wb.seite}?buchung={'0' * 48}", timeout=30).text
    # fremder Browser ohne Cookie: Rückkehr zeigt keinen Link
    r = requests.get(f"{wb.seite}?wb=rueckkehr&nummer={b['nummer']}", allow_redirects=False, timeout=30)
    assert r.status_code == 200 and "buchung=" not in r.text.split("wb-wiederfinden")[0]
    # wiederfinden: falsche E-Mail nein, richtige ja (neuer Link, alter ungültig)
    html = requests.get(wb.seite, timeout=30).text
    nonce = re.search(r'name="_wpnonce" value="([^"]+)"[^>]*>\s*<input type="hidden" name="tamil_wb_aktion" value="wiederfinden"', html).group(1)
    r = requests.post(wb.seite, data={"tamil_wb_aktion": "wiederfinden", "_wpnonce": nonce, "nummer": b["nummer"],
                                      "email": "falsch@example.test"}, allow_redirects=False, timeout=30)
    assert r.status_code == 200 and "keine Buchung" in r.text
    r = requests.post(wb.seite, data={"tamil_wb_aktion": "wiederfinden", "_wpnonce": nonce, "nummer": b["nummer"].lower(),
                                      "email": "KUNDE@example.test"}, allow_redirects=False, timeout=30)
    assert r.status_code == 303
    neu = re.search(r"buchung=([a-f0-9]{48})", r.headers["Location"]).group(1)
    assert neu != alt and "nicht (mehr) gültig" in requests.get(f"{wb.seite}?buchung={alt}", timeout=30).text
    assert wb.buchung(b["nummer"])["kunden_hash"] == hashlib.sha256(neu.encode()).hexdigest()
    # Bezahlen nur aus dem Browser, der gebucht hat
    html = s.get(f"{wb.seite}?wb=zusammenfassung&nummer={b['nummer']}", timeout=30).text
    assert "nicht zu diesem Browser" in html  # das Cookie gilt nach dem neuen Link nicht mehr
