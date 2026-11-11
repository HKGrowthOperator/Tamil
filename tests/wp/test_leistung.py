"""Plugin tamil-site: Cache-Kopfzeilen für HTML (Gäste 60 Sekunden, Suche und angemeldete Seiten nie)."""


def _cc(r) -> str:
    return r.headers.get("Cache-Control", "").replace(" ", "").lower()


def test_gast_startseite_60_sekunden(wp):
    r = wp.get("/")
    assert r.status_code == 200 and _cc(r) == "public,max-age=60"
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
    assert wp_cli(code).strip() == '["public, max-age=60","no-store","","no-store"]'
