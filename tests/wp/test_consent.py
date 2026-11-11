"""Plugin tamil-site: Cookie-Zustimmung (eigene Lösung, kein fremdes Skript, Funktionsschalter „zustimmung“)."""

import re
from urllib.parse import urljoin, urlparse

AN = {"X-Tamil-Funktionen": "zustimmung"}


def _ladeadressen(seite: str, basis: str) -> list[str]:
    """Adressen, die der Browser beim Aufbau lädt (Skripte, Stile, Bilder, Rahmen, Schriften)."""
    adressen = re.findall(r'<(?:script|img|iframe|source|video|audio|embed)\b[^>]*\ssrc=["\']([^"\']+)', seite)
    for tag in re.findall(r"<link\b[^>]*>", seite):
        if re.search(r'rel=["\'](?:stylesheet|preload|modulepreload|icon|apple-touch-icon)["\']', tag):
            m = re.search(r'href=["\']([^"\']+)', tag)
            if m:
                adressen.append(m.group(1))
    for srcset in re.findall(r'srcset=["\']([^"\']+)', seite):
        adressen += [teil.strip().split(" ")[0] for teil in srcset.split(",") if teil.strip()]
    adressen += re.findall(r"url\(['\"]?([^'\")]+)", seite)
    return [urljoin(basis, a) for a in adressen if not a.startswith("data:")]


def test_schalter_aus_keine_ausgabe(wp, wp_cli):
    alt = wp_cli("echo wp_json_encode( get_option( 'tamil_site_funktionen', null ) );").strip()
    try:
        wp_cli("$f = (array) get_option( 'tamil_site_funktionen', array() ); $f['zustimmung'] = false; update_option( 'tamil_site_funktionen', $f );")
        seite = wp.get("/").text
        assert "tz-hinweis" not in seite and "consent.js" not in seite and "Cookie-Einstellungen" not in seite
    finally:
        if alt == "null":
            wp_cli("delete_option( 'tamil_site_funktionen' );")
        else:
            wp_cli(f"update_option( 'tamil_site_funktionen', json_decode( '{alt}', true ) );")


def test_kopfzeile_wirkt_nur_lokal(wp_cli):
    code = ("$_SERVER['HTTP_X_TAMIL_FUNKTIONEN'] = 'zustimmung,gibtsnicht';"
            "echo wp_json_encode( array( tamil_site_funktionen_test( 'production' ), tamil_site_funktionen_test( 'staging' ),"
            " tamil_site_funktionen_test( 'local' ), tamil_site_funktionen_test( 'development' ) ) );")
    assert wp_cli(code).strip() == '[[],[],["zustimmung"],["zustimmung"]]'


def test_schalter_an_hinweis_dialog_und_link(wp):
    seite = wp.get("/", headers=AN).text
    assert 'class="tz-hinweis"' in seite and "Alle akzeptieren" in seite and "Nur notwendige" in seite
    assert "Einstellungen" in seite and "<dialog" in seite and 'data-tz-oeffnen' in seite
    assert re.search(r"<a[^>]*data-tz-oeffnen[^>]*>Cookie-Einstellungen</a>", seite)
    assert 'name="tz-externe_medien"' in seite and 'name="tz-statistik"' in seite
    assert re.search(r'src="[^"]*tamil-site/assets/consent\.js\?ver=', seite)
    assert re.search(r"href=[\"'][^\"']*tamil-site/assets/consent\.css\?ver=", seite)
    assert "Vorläufige Fassung" in seite


def test_keine_fremden_adressen_ohne_zustimmung(wp):
    host = urlparse(wp.url).netloc
    for pfad in ("/", "/kontakt/", "/?s=kino"):
        seite = wp.get(pfad, headers=AN).text
        fremd = [a for a in _ladeadressen(seite, wp.url + pfad) if urlparse(a).netloc not in ("", host)]
        assert fremd == [], (pfad, fremd)


def test_texte_pflegbar(wp, wp_cli):
    alt = wp_cli("echo wp_json_encode( get_option( 'tamil_site_zustimmung', null ) );").strip()
    try:
        wp_cli("update_option( 'tamil_site_zustimmung', tamil_site_sanitize_zustimmung( array( 'titel' => 'Eigener Titel <b>x</b>', "
               "'text' => 'Eigener Text.', 'fassung' => '2027-01' ) ) );")
        seite = wp.get("/", headers=AN).text
        assert "Eigener Titel x" in seite and "Eigener Text." in seite and 'data-fassung="2027-01"' in seite
        assert "<b>x</b>" not in seite
    finally:
        if alt == "null":
            wp_cli("delete_option( 'tamil_site_zustimmung' );")
        else:
            wp_cli(f"update_option( 'tamil_site_zustimmung', json_decode( '{alt}', true ) );")
