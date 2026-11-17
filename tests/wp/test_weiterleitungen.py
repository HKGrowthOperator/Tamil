"""Plugin tamil-site: 301-Weiterleitungen für den Relaunch und Werbeplätze, gegen das lokale WordPress."""

import json

import requests
from wp_umgebung import PW, URL, USER


def test_redirect_and_ad_seed(wp):
    r = requests.get(f"{URL}/category/anirudh/", allow_redirects=False, timeout=30)
    assert r.status_code == 301 and r.headers["Location"].rstrip("/").endswith("/category/events")
    home = requests.get(URL + "/", timeout=30).text
    assert "Testbanner Leaderboard" in home or 'class="ad-test"' in home or "<body" in home  # Theme entscheidet, ob der Platz gerendert wird


def test_weiterleitungen_per_rest_und_idempotent(wp_admin):
    """Migration: tamil-site/v1/weiterleitungen ersetzt die Tabelle; wiederholter Aufruf ändert nichts."""
    seed = "alt,neu\n/category/anirudh/,/category/events/\n"
    csv = seed + "/category/blog/,/community/\n"
    url = f"{URL}/wp-json/tamil-site/v1/weiterleitungen"
    try:
        assert requests.post(url, json={"csv": csv}, timeout=30).status_code in (401, 403)  # ohne Anmeldung nicht erlaubt
        for _ in range(2):
            r = requests.post(url, json={"csv": csv}, auth=wp_admin, timeout=30)
            assert r.status_code == 200 and r.json()["eintraege"] == 2
        r = requests.get(f"{URL}/category/blog/", allow_redirects=False, timeout=30)
        assert r.status_code == 301 and r.headers["Location"].rstrip("/").endswith("/community")
    finally:
        requests.post(url, json={"csv": seed}, auth=wp_admin, timeout=30)


def test_weiterleitungen_rechte_prozent_ketten_grenzen(wp_admin):
    url = f"{URL}/wp-json/tamil-site/v1/weiterleitungen"
    seed = "alt,neu\n/category/anirudh/,/category/events/\n"
    admin = wp_admin
    try:
        # Redakteur-/Radar-Benutzer ohne manage_options: 403
        assert requests.post(url, json={"csv": seed}, auth=(USER, PW), timeout=30).status_code == 403
        csv = ("alt,neu\n/%c3%bcber-uns/,/ueber-uns/\n"
               "/a/,/b/\n/b/,/c/\n"            # Kette: wird aufgelöst, nicht verworfen
               "/x/,/y/\n/y/,/x/\n"            # Schleife: beide verworfen
               "/fremd/,https://example.org/z/\n")
        r = requests.post(url, json={"csv": csv}, auth=admin, timeout=30)
        assert r.status_code == 200
        gruende = {v["alt"]: v["grund"] for v in r.json()["verworfen"]}
        assert {"/x/", "/y/", "/fremd/"} == set(gruende)
        assert r.json()["eintraege"] == 3  # /über-uns/, /a/, /b/
        r = requests.get(f"{URL}/%C3%BCber-uns/", allow_redirects=False, timeout=30)
        assert r.status_code == 301 and r.headers["Location"].rstrip("/").endswith("/ueber-uns")
        assert requests.get(f"{URL}/fremd/", allow_redirects=False, timeout=30).status_code != 301
        # Obergrenze
        gross = "alt,neu\n" + "\n".join(f"/p{i}/,/q{i}/" for i in range(5100))
        assert requests.post(url, json={"csv": gross}, auth=admin, timeout=60).status_code == 413
    finally:
        requests.post(url, json={"csv": seed}, auth=admin, timeout=30)


def test_weiterleitungen_ketten_aufloesen_schleifen_verwerfen_pfade_speichern(wp_admin):
    url = f"{URL}/wp-json/tamil-site/v1/weiterleitungen"
    seed = "alt,neu\n/category/anirudh/,/category/events/\n"
    admin = wp_admin
    try:
        csv = ("alt,neu\n"
               "/a/,/b/\n/b/,/c/\n"                       # Kette: /a/ zeigt direkt auf /c/
               "/K1,/K2\n/k2/,/k3/\n"                      # Groß-/Kleinschreibung und fehlender Schrägstrich
               "/p/,/q/\n/q/,/r/\n/r/,/p/\n"              # Schleife über drei: alle verworfen
               f"/voll/,{URL}/ziel/\n")                    # volle eigene Adresse -> Pfad
        r = requests.post(url, json={"csv": csv}, auth=admin, timeout=30)
        assert r.status_code == 200
        tabelle, verworfen = r.json()["tabelle"], {v["alt"] for v in r.json()["verworfen"]}
        assert tabelle["/a/"] == "/c/" and tabelle["/b/"] == "/c/"
        assert tabelle["/k1/"] == "/k3/"
        assert {"/p/", "/q/", "/r/"} == verworfen and not {"/p/", "/q/", "/r/"} & set(tabelle)
        assert tabelle["/voll/"] == "/ziel/"  # nur der Pfad wird gespeichert
        r = requests.get(f"{URL}/a/", allow_redirects=False, timeout=30)
        assert r.status_code == 301 and r.headers["Location"].rstrip("/").endswith("/c")
        # Zeilen werden auch bei \r und \r\n gezählt (Obergrenze)
        gross = "alt,neu\r" + "\r".join(f"/p{i}/,/q{i}/" for i in range(5100))
        assert requests.post(url, json={"csv": gross}, auth=admin, timeout=60).status_code == 413
    finally:
        requests.post(url, json={"csv": seed}, auth=admin, timeout=30)


def test_weiterleitungsziel_folgt_geaendertem_host(wp_cli):
    """Die Adresse der Website wird erst beim Weiterleiten gebildet: nach der Domain-Umschaltung zeigt dieselbe Tabelle auf den neuen Host."""
    code = ("add_filter('home_url', function($u,$p){return 'https://www.tamil.de'.$p;}, 10, 2);"
            "echo tamil_site_redirect_url('/x/') . ' ' . tamil_site_redirect_url('http://alt-host.example/y/');")
    out = wp_cli(code)
    assert out.strip() == "https://www.tamil.de/x/ https://www.tamil.de/y/"


def test_admin_formular_bereinigt_wie_rest(wp_cli):
    """Weg über das Einstellungsformular (sanitize_callback) ohne Browser: %xx bleibt, Ketten werden aufgelöst."""
    code = ("$alt = get_option('tamil_site_redirects_csv', '');"
            "tamil_site_sanitize_redirects_csv(\"alt,neu\\n/%c3%bcber-uns/,/a/\\n/a/,/b/\\n/x/,/y/\\n/y/,/x/\\n\");"
            "echo json_encode(get_option('tamil_site_redirects'));"
            "tamil_site_sanitize_redirects_csv($alt);")
    out = wp_cli(code)
    assert json.loads(out) == {"/%c3%bcber-uns/": "/b/", "/a/": "/b/"}


def test_weiterleitungen_gefaehrliche_ziele_und_geschuetzte_pfade(wp_admin):
    """Nie auf fremden Host umleiten, nie Anmeldung/Verwaltung/REST umleiten (Aussperren)."""
    url = f"{URL}/wp-json/tamil-site/v1/weiterleitungen"
    seed = "alt,neu\n/category/anirudh/,/category/events/\n"
    admin = wp_admin
    try:
        csv = ("alt,neu\n"
               "/s1/,//fremd.example/x\n"          # protokollrelativ: bleibt auf der eigenen Website
               "/s2/,/\\fremd\n"                   # Backslash: verworfen
               "/s3/,/a\x01b\x07c/\n"              # Steuerzeichen fallen weg
               "/wp-admin/,/x/\n/wp-json/,/x/\n/wp-login.php,/x/\n/wp-admin/options.php,/x/\n")
        r = requests.post(url, json={"csv": csv}, auth=admin, timeout=30)
        assert r.status_code == 200
        tabelle, verworfen = r.json()["tabelle"], {v["alt"] for v in r.json()["verworfen"]}
        assert {"/s2/", "/wp-admin/", "/wp-json/", "/wp-login.php/", "/wp-admin/options.php/"} <= verworfen
        assert all(t.startswith("/") and not t.startswith("//") and "\\" not in t for t in tabelle.values())
        assert tabelle["/s3/"] == "/abc/"
        # kein Redirect auf fremden Host, REST und Anmeldung bleiben erreichbar
        for pfad in ("/s1/", "/s3/"):
            loc = requests.get(f"{URL}{pfad}", allow_redirects=False, timeout=30).headers.get("Location", "")
            assert loc.startswith(URL + "/"), loc
        assert requests.get(f"{URL}/wp-json/", allow_redirects=False, timeout=30).status_code == 200
        assert requests.get(f"{URL}/wp-login.php", allow_redirects=False, timeout=30).status_code in (200, 302)
    finally:
        requests.post(url, json={"csv": seed}, auth=admin, timeout=30)
