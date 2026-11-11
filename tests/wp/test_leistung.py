"""Plugin tamil-site: Cache-Kopfzeilen für HTML (Gäste 60 Sekunden, Suche und angemeldete Seiten nie)."""

import requests


def _cc(r) -> str:
    return r.headers.get("Cache-Control", "").replace(" ", "").lower()


def test_gast_startseite_60_sekunden(wp):
    r = wp.get("/")
    # kein gemeinsamer Zwischenspeicher vorgesehen: private ist die sichere Wahl
    assert r.status_code == 200 and _cc(r) == "private,max-age=60"
    assert "cookie" in r.headers.get("Vary", "").lower()
    assert "no-store" not in _cc(wp.get("/category/kino/"))


def test_suche_nie_zwischenspeichern(wp):
    assert "no-store" in _cc(wp.get("/?s=kino"))


def test_angemeldet_unveraendert(wp, wp_sitzung):
    r = wp_sitzung.get(f"{wp.url}/", timeout=30)
    assert r.status_code == 200 and "public" not in _cc(r)


def test_post_rest_und_admin_nicht_oeffentlich(wp):
    assert "public" not in _cc(wp.get("/wp-json/"))
    assert "public" not in _cc(wp.get("/wp-login.php"))


def test_seite_meldet_sich_als_nie_zwischenspeichern(wp, wp_cli):
    # Ein Muster für spätere Formular- und Buchungsseiten: Filter tamil_site_nie_zwischenspeichern
    code = ("echo wp_json_encode( array( tamil_site_cache_regel( false, false, false ), tamil_site_cache_regel( false, false, true ), "
            "tamil_site_cache_regel( true, false, false ), tamil_site_cache_regel( false, true, false ) ) );")
    assert wp_cli(code).strip() == '["private, max-age=60","no-store","","no-store"]'


def test_passwortgeschuetzter_beitrag_nie_zwischenspeichern(wp, wp_cli):
    pid = int(wp_cli("echo wp_insert_post( array( 'post_title' => 'Geschützt', 'post_name' => 'leistung-geschuetzt',"
                     " 'post_status' => 'publish', 'post_password' => 'geheim', 'post_content' => '<p>Nur mit Passwort.</p>' ) );"))
    try:
        assert "no-store" in _cc(wp.get("/leistung-geschuetzt/"))
        # nach Eingabe des Passworts (Cookie wp-postpass_…) ist post_password_required() falsch – trotzdem nie zwischenspeichern
        s = requests.Session()
        s.post(f"{wp.url}/wp-login.php?action=postpass", data={"post_password": "geheim"}, allow_redirects=False, timeout=30)
        r = s.get(f"{wp.url}/leistung-geschuetzt/", timeout=30)
        assert "Nur mit Passwort." in r.text and "no-store" in _cc(r) and "public" not in _cc(r)
    finally:
        wp_cli(f"wp_delete_post( {pid}, true );")
