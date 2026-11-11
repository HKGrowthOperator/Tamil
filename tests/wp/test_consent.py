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
    assert wp_cli(code).strip() == '[[],[],["zustimmung"],[]]'


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


BANNER = '<a href="https://werbekunde.example/"><img src="https://cdn.werbung.example/banner.jpg" alt="Banner"></a>'


def _banner_setzen(wp_cli, html: str | None) -> str:
    """Setzt Banner-HTML für alle Werbeplätze, gibt den alten Stand (JSON) zurück."""
    alt = wp_cli("echo wp_json_encode( get_option( 'tamil_site_settings', null ) );").strip()
    if html is not None:
        wp_cli("$s = (array) get_option( 'tamil_site_settings', array() ); foreach ( array_keys( tamil_site_werbeplaetze() ) as $p ) {"
               f" $s['anzeigen'][ $p ] = {html!r}; }} update_option( 'tamil_site_settings', $s );")
    return alt


def _banner_zurueck(wp_cli, alt: str) -> None:
    if alt == "null":
        wp_cli("delete_option( 'tamil_site_settings' );")
    else:
        wp_cli(f"update_option( 'tamil_site_settings', json_decode( {alt!r}, true ) );")


def test_werbeplatz_mit_fremdem_inhalt_erst_nach_zustimmung(wp, wp_cli):
    alt = _banner_setzen(wp_cli, BANNER)
    try:
        seite = wp.get("/", headers=AN).text
        assert '<template data-zustimmung="externe_medien">' in seite
        ohne_vorlagen = re.sub(r"<template\b.*?</template>", "", seite, flags=re.DOTALL)
        assert "cdn.werbung.example" not in " ".join(_ladeadressen(ohne_vorlagen, wp.url + "/"))
        assert "cdn.werbung.example" in seite  # inaktiv in der Vorlage, consent.js setzt sie nach Zustimmung ein
        # Schalter aus: wie bisher direkt
        assert "cdn.werbung.example/banner.jpg" in " ".join(_ladeadressen(wp.get("/").text, wp.url + "/"))
    finally:
        _banner_zurueck(wp_cli, alt)


def test_werbeplatz_ohne_fremde_adressen_wie_bisher(wp, wp_cli):
    alt = _banner_setzen(wp_cli, '<a href="/kontakt/"><img src="/wp-content/uploads/eigen.jpg" alt="Eigen"></a>')
    try:
        seite = wp.get("/", headers=AN).text
        assert "data-zustimmung" not in seite and "/wp-content/uploads/eigen.jpg" in seite
        code = ("echo wp_json_encode( array_map( 'tamil_site_fremde_inhalte', array( '<img src=\"https://x.example/a.png\">',"
                " '<script>var a=1;</script>', '<a href=\"https://x.example/\">Link</a>', '<img src=\"/a.png\">',"
                " '<img srcset=\"//x.example/a.png 2x\">', '<div style=\"background:url(https://x.example/b.png)\"></div>',"
                f" '<img src=\"{wp.url}/a.png\">' ) ) );")
        assert wp_cli(code).strip() == "[true,true,false,false,true,true,false]"
    finally:
        _banner_zurueck(wp_cli, alt)
