"""Migration des Altbestands (tools/migration.py): Logik ohne Netz."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import migration  # noqa: E402

SITE = json.loads((Path(__file__).resolve().parent.parent / "prototyp" / "content" / "site.json").read_text(encoding="utf-8"))


def test_kategorien_abbildung():
    assert migration.map_kategorien(["news"]) == ("news", [], [])
    assert migration.map_kategorien(["blog"]) == ("community", [], [])
    assert migration.map_kategorien(["kritik"]) == ("kino", [], ["Kritik"])
    assert migration.map_kategorien(["anirudh"]) == ("events", [], ["Anirudh"])
    assert migration.map_kategorien(["turniere"]) == ("sport", [], [])
    # spezifische Rubrik vor news, news bleibt als weitere
    assert migration.map_kategorien(["news", "media"]) == ("kino", ["news"], [])
    # nur „test“: nicht übernehmen; Unbekanntes landet in news
    assert migration.map_kategorien(["test"]) == (None, [], [])
    assert migration.map_kategorien(["irgendwas"]) == ("news", [], [])


def test_alle_ziele_sind_neue_rubriken():
    from export_site import CATEGORY_MAP
    for neu, _ in CATEGORY_MAP.values():
        assert neu is None or neu in migration.NEUE_RUBRIKEN


def test_idempotenz_schluessel():
    assert migration.post_uid(9711) == "alt-9711"
    assert migration.post_uid(5, aus_seite=True) == "altseite-5"
    assert migration.idempotenz_pruefen([{"slug": "a"}, {"slug": "b"}, {"slug": "a"}]) == ["a"]


def test_kontaktangaben_werden_nur_gezaehlt_nie_geloescht():
    werte = migration.beispielwerte(SITE)
    assert "info@tamil.de" in werte and len(werte) == 3
    html = "<p>Tel. +49 69 123 456, Mail info@tamil.de</p><p>WhatsApp +491701234567</p>"
    assert migration.kontaktangaben(html, werte) == werte
    assert migration.kontaktangaben("<p>nichts</p>", werte) == []
    assert not hasattr(migration, "strip_beispielwerte")


def test_bildadressen_umschreiben():
    alt = "https://www.tamil.de/wp-content/uploads/2024/11/kanguva-300x200.jpg"
    html = (f'<p><a href="{alt}"><img src="{alt}" srcset="{alt} 300w, x 600w" sizes="(max-width:300px) 100vw" alt="Plakat"></a>'
            '<a href="https://www.tamil.de/anderer-beitrag/">mehr</a> <a href="http://tamil.de">Start</a></p>')
    assert migration.upload_urls(html) == [alt]
    neu = migration.rewrite_html(html, {alt: "https://neu.example/wp-content/uploads/2026/11/kanguva-300x200.jpg"})
    assert "tamil.de/wp-content" not in neu and neu.count("neu.example") == 2
    assert "srcset" not in neu and "sizes" not in neu and 'alt="Plakat"' in neu
    assert 'href="/anderer-beitrag/"' in neu and 'href="/"' in neu


def test_http_variante_und_youtube():
    alt = "https://www.tamil.de/wp-content/uploads/2020/01/a.jpg"
    neu = migration.rewrite_html('<img src="http://www.tamil.de/wp-content/uploads/2020/01/a.jpg">', {alt: "https://n/a.jpg"})
    assert 'src="https://n/a.jpg"' in neu
    yt = '<iframe loading="lazy" width="630" src="https://www.youtube.com/embed/YP4PBOfhaN8?feature=oembed" allowfullscreen></iframe>'
    out = migration.rewrite_html(yt, {})
    assert "<iframe" not in out and "https://www.youtube.com/watch?v=YP4PBOfhaN8" in out


def test_fremde_bilder():
    html = '<img src="http://www.tamil.de/wp-content/uploads/a.jpg"><img src="https://static.giga.de/x.jpg"><img src="/rel.jpg">'
    assert migration.fremde_bilder(html) == ["https://static.giga.de/x.jpg"]


def test_redirect_csv_und_seitenplan():
    cats = [{"slug": "blog", "count": 21}, {"slug": "news", "count": 3}]
    pages = [{"slug": "ueberuns", "link": "https://www.tamil.de/ueberuns/"}, {"slug": "login", "link": "https://www.tamil.de/login/"}]
    csv_text = migration.redirect_csv("https://www.tamil.de", cats, pages, [("https://www.tamil.de/a/", "https://www.tamil.de/b/")])
    zeilen = csv_text.splitlines()
    assert zeilen[0] == "alt,neu"
    assert "/category/blog/,/category/community/" in zeilen
    assert "/ueberuns/,/ueber-uns/" in zeilen
    assert "/a/,/b/" in zeilen
    plan = migration.seiten_plan(pages + [{"slug": "maya"}, {"slug": "kino"}])
    assert [p["slug"] for p in plan["seite"]] == ["ueberuns"] and [p["slug"] for p in plan["loeschen"]] == ["login"]
    assert [p["slug"] for p in plan["beitrag"]] == ["maya"] and [p["slug"] for p in plan["redirect"]] == ["kino"]


def test_text_entities():
    assert migration.text("Kanguva &#8211; <b>Highlight</b>\n  jetzt") == "Kanguva – Highlight jetzt"


def test_medien_slug_stabil_und_eindeutig():
    a = migration.media_slug("https://www.tamil.de/wp-content/uploads/2019/11/image.gif")
    assert a == migration.media_slug("http://tamil.de/wp-content/uploads/2019/11/image.gif")  # Schema/Host egal
    assert a != migration.media_slug("https://www.tamil.de/wp-content/uploads/2020/01/image.gif")  # gleicher Name, anderer Monat
    assert a.startswith("alt-image-")


# ---- Schutz der alten Seite, Ziel-Adresse

import pytest  # noqa: E402


@pytest.mark.parametrize("url", [
    "https://tamil.de", "https://www.tamil.de/", "https://TAMIL.DE", "https://Www.Tamil.De", "https://tamil.de.",
    "https://x@tamil.de", "https://user:pw@neu.example", "https://tamil.de:443", "https://alt.tamil.de", "https://a.b.tamil.de/x",
    "http://www.tamil.de", "ftp://neu.example", "neu.example",
])
def test_ziel_pruefen_lehnt_ab(url):
    assert migration.ziel_pruefen(url)


SSLIP = "https://tamil-web.167.233.76.202.sslip.io"


@pytest.mark.parametrize("url", [SSLIP, SSLIP + "/", "http://127.0.0.1:8086", "http://localhost:8085", "http://[::1]:8085", "HTTPS://TAMIL-WEB.167.233.76.202.SSLIP.IO"])
def test_ziel_pruefen_erlaubt(url):
    assert migration.ziel_pruefen(url) == ""
    assert migration.ziel_normalisieren(url)[0].startswith(("http://", "https://"))


def test_normalisierte_adresse_wird_verwendet():
    assert migration.ziel_normalisieren("HTTPS://TAMIL-WEB.167.233.76.202.SSLIP.IO/")[0] == SSLIP


@pytest.mark.parametrize("url", ["https://%74amil.de", "https://tamil.de%2e", "https://%54AMIL.DE", "https://www.%74amil.de/x",
                                 "https://exämple.de", "https://tamil.de\u2024", "https://a b.de",
                                 "https://10.0.0.5", "https://203.0.113.9", "https://[2001:db8::1]", "https://127.0.0.2", "https://xn--tamil-xyz.de"])
def test_ziel_normalisieren_lehnt_ab(url):
    assert migration.ziel_normalisieren(url) == ("", migration.ziel_normalisieren(url)[1]) and migration.ziel_normalisieren(url)[1]


def test_prozent_im_host_auch_mit_ziel_host_abgelehnt():
    assert migration.ziel_pruefen("https://%74amil.de", ziel_host="tamil.de")
    assert migration.ziel_pruefen("https://neu%2eexample", ziel_host="neu.example")


def test_punycode_nur_mit_ziel_host():
    assert "Positivliste" in migration.ziel_pruefen("https://xn--exmple-cua.de")
    assert migration.ziel_pruefen("https://xn--exmple-cua.de", ziel_host="xn--exmple-cua.de") == ""
    assert migration.ziel_pruefen("https://exämple.de", ziel_host="exämple.de")  # Nicht-ASCII bleibt verboten


def test_positivliste_und_ziel_host():
    assert "Positivliste" in migration.ziel_pruefen("https://neu.example")
    assert migration.ziel_pruefen("https://neu.example", ziel_host="neu.example") == ""
    assert migration.ziel_pruefen("https://neu.example", ziel_host="NEU.example") == ""  # Vergleich nach Normalisierung
    assert "Positivliste" in migration.ziel_pruefen("https://neu.example", ziel_host="andere.example")
    # --ziel-host öffnet nie die alte Seite
    assert "alte" in migration.ziel_pruefen("https://alt.tamil.de", ziel_host="alt.tamil.de")
    assert "alte" in migration.ziel_pruefen("https://tamil.de", ziel_host="tamil.de")


def test_http_nur_lokal():
    assert "Klartext" in migration.ziel_pruefen("http://neu.example", ziel_host="neu.example")
    assert "Klartext" in migration.ziel_pruefen("http://tamil-web.167.233.76.202.sslip.io")


def test_nach_umschaltung_nur_mit_beiden_schaltern():
    assert migration.ziel_pruefen("https://www.tamil.de", True, False)
    assert migration.ziel_pruefen("https://alt.tamil.de", True, True)  # Unterdomain nie
    assert migration.ziel_pruefen("https://www.tamil.de", True, True) == ""
    assert migration.ziel_pruefen("https://tamil.de", True, True) == ""
    assert "alte" in migration.ziel_pruefen("https://alt.tamil.de", True, True, ziel_host="alt.tamil.de")


@pytest.mark.parametrize("url", ["https://TAMIL.DE", "https://x@tamil.de", "https://tamil.de.", "https://alt.tamil.de",
                                 "https://www.tamil.de:8443", "http://neu.example", "https://%74amil.de", "https://tamil.de%2e", "https://neu.example"])
def test_main_bricht_ab(url, monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("MIGRATION_APP_PASSWORD", "geheim-nicht-ausgeben")
    monkeypatch.setenv("MIGRATION_ZIEL_IST_NEU", "1")  # frühere Abschaltung wirkt nicht mehr
    assert migration.main(["--export", str(tmp_path), "--url", url]) == 2
    assert "geheim-nicht-ausgeben" not in capsys.readouterr().out


def test_main_nach_umschaltung_ohne_bestaetigung(monkeypatch, tmp_path):
    monkeypatch.setenv("MIGRATION_APP_PASSWORD", "x")
    assert migration.main(["--export", str(tmp_path), "--url", "https://www.tamil.de", "--nach-umschaltung"]) == 2


# ---- Seiten bereinigen, Auszug, Links

def test_seite_bereinigen():
    roh = ('<p onclick="x()">Text <a href="javascript:alert(1)">böse</a> <a href="https://a.example/" onmouseover="y()">gut</a></p>'
           '<script>alert(1)</script><iframe src="https://evil.example"></iframe><img src="x.jpg" onerror="z()" alt="B">')
    sauber = migration.seite_bereinigen(roh)
    for schlecht in ("script", "iframe", "onclick", "onmouseover", "onerror", "javascript:"):
        assert schlecht not in sauber
    assert 'href="https://a.example/"' in sauber and 'alt="B"' in sauber and "gut" in sauber


def test_teaser_ohne_nackte_videoadresse():
    inhalt = ('<p>Neues Lied von Anirudh ist da und wird viel gehört.</p>'
              '<figure class="wp-block-embed"><div class="wp-block-embed__wrapper">\nhttps://www.youtube.com/watch?v=abc123XYZ\n</div></figure>'
              '<p>Mehr Text folgt.</p>')
    auszug = "<p>Neues Lied von Anirudh ist da https://www.youtube.com/watch?v=abc123XYZ Mehr Text</p>"
    t, ersetzt = migration.bilde_teaser(auszug, inhalt)
    assert "youtube" not in t and t.startswith("Neues Lied") and "Mehr Text folgt." in t and ersetzt
    t2, ersetzt2 = migration.bilde_teaser("", inhalt)  # kein eigener Auszug
    assert "youtube" not in t2 and t2 and not ersetzt2
    assert migration.bilde_teaser("<p>Eigener Auszug.</p>", inhalt) == ("Eigener Auszug.", False)


def test_nicht_uebertragene_upload_links_bleiben_absolut():
    html = '<a href="https://www.tamil.de/wp-content/uploads/2019/11/x.pdf">PDF</a> <a href="https://www.tamil.de/seite/">S</a>'
    neu = migration.rewrite_html(html, {})
    assert 'href="https://www.tamil.de/wp-content/uploads/2019/11/x.pdf"' in neu and 'href="/seite/"' in neu
    assert len(migration.OFFENE_UPLOAD_HREF_RE.findall(neu)) == 1


# ---- Bilder holen

class _Antwort:
    def __init__(self, code, inhalt=b"", header=None):
        self.status_code, self.content, self.headers = code, inhalt, header or {}


class _Sitzung:
    def __init__(self, antworten):
        self.antworten, self.aufrufe, self.max_redirects = list(antworten), [], 0

    def get(self, url, **kw):
        self.aufrufe.append((url, kw))
        return self.antworten.pop(0)


def _medien(tmp_path, antworten):
    m = migration.Medien(tmp_path / "meinmedien", pause=0, warte=0)
    m.session = _Sitzung(antworten)
    return m


U = "https://www.tamil.de/wp-content/uploads/2020/01/a.jpg"


def test_holen_wiederholt_bei_5xx_und_nutzt_medienordner(tmp_path):
    m = _medien(tmp_path, [_Antwort(503), _Antwort(429), _Antwort(200, b"BILD")])
    assert m.holen(U) == b"BILD" and len(m.session.aufrufe) == 3 and U not in m.status
    assert (tmp_path / "meinmedien" / "2020" / "01" / "a.jpg").read_bytes() == b"BILD"  # --medien wirkt
    assert m.holen(U) == b"BILD" and len(m.session.aufrufe) == 3  # aus dem Ordner


def test_holen_gibt_nach_drei_versuchen_auf_und_404_nicht_wiederholt(tmp_path):
    m = _medien(tmp_path, [_Antwort(503)] * 3)
    assert m.holen(U) is None and m.status[U] == 503 and len(m.session.aufrufe) == 3
    m = _medien(tmp_path, [_Antwort(404)])
    assert m.holen(U) is None and m.status[U] == 404 and len(m.session.aufrufe) == 1


def test_holen_nur_alte_hosts_und_https_keine_fremden_weiterleitungen(tmp_path):
    m = _medien(tmp_path, [])
    assert m.holen("https://evil.example/wp-content/uploads/2020/01/b.jpg") is None and not m.session.aufrufe
    m = _medien(tmp_path, [_Antwort(302, header={"Location": "https://evil.example/x.jpg"})])
    assert m.holen(U) is None and "fremden Host" in m.status[U]
    m = _medien(tmp_path, [_Antwort(301, header={"Location": "https://tamil.de/neu.jpg"}), _Antwort(200, b"OK")])
    assert m.holen(U) == b"OK"
    assert all(kw["allow_redirects"] is False for _, kw in m.session.aufrufe)
    m = _medien(tmp_path, [_Antwort(200, b"HTTP")])
    m.holen("http://www.tamil.de/wp-content/uploads/2020/02/c.jpg")
    assert m.session.aufrufe[0][0].startswith("https://")


# ---- Weiterleitungstabelle bleibt bei jedem Lauf vollständig

class FakeWP:
    """Neue Website als Wörterbuch: uid -> Beitrag. `belegt` = Slugs fremder Beiträge (ohne alt-Kennung)."""

    def __init__(self, belegt=None):
        self.beitraege, self.belegt = {}, belegt or {}
        self.url = "http://127.0.0.1:1"

    def req(self, method, path, **kw):
        if path.startswith("tamil-radar/v1/beitrag/"):
            d = self.beitraege.get(path.rsplit("/", 1)[1])
            return (200, d) if d else (404, {})
        if path == "wp/v2/posts":
            slug = kw["params"]["slug"]
            return 200, ([{"id": self.belegt[slug]}] if slug in self.belegt else [])
        raise AssertionError(path)


def _posts():
    return [{"id": i, "slug": f"s{i}", "link": f"https://www.tamil.de/s{i}/", "categories": [1], "date": f"2020-01-0{i}T00:00:00"} for i in (1, 2, 3)]


def _mig(tmp_path, wp):
    (tmp_path / "media.json").write_text("[]")
    return migration.Migration(wp, tmp_path, migration.Medien(tmp_path / "media"), SITE)


def test_tabelle_vollstaendig_nach_wiederanlauf_und_limit(tmp_path):
    wp = FakeWP()
    # Lauf 1 hat s2 unter anderem Slug angelegt (WordPress hängt -2 an); alle drei existieren schon (Wiederanlauf)
    for i, slug in ((1, "s1"), (2, "s2-2"), (3, "s3")):
        wp.beitraege[f"alt-{i}"] = {"id": 100 + i, "slug": slug, "link": f"http://127.0.0.1:1/{slug}/"}
    m = _mig(tmp_path, wp)
    cats = {1: "news"}
    rows = m.abweichungen(_posts(), cats, [])
    assert rows == [("https://www.tamil.de/s2/", "http://127.0.0.1:1/s2-2/")]  # auch bei "vorhanden" und unabhängig von --limit
    csv_text = migration.redirect_csv("https://www.tamil.de", [], [], rows)
    assert "/s2/,/s2-2/" in csv_text
    # derselbe Aufruf noch einmal (zweiter Lauf, anderes Migration-Objekt): gleiche Tabelle
    assert _mig(tmp_path, wp).abweichungen(_posts(), cats, []) == rows


def test_slug_kollision_mit_fremdem_beitrag_ohne_weiterleitung(tmp_path):
    wp = FakeWP(belegt={"s2": 999})  # /s2/ gehört einem Radar-Beitrag
    for i, slug in ((1, "s1"), (2, "s2-2"), (3, "s3")):
        wp.beitraege[f"alt-{i}"] = {"id": 100 + i, "slug": slug, "link": f"http://127.0.0.1:1/{slug}/"}
    m = _mig(tmp_path, wp)
    assert m.abweichungen(_posts(), {1: "news"}, []) == []
    assert m.bericht["slug_kollisionen"][0]["belegt_von"] == [999] and m.bericht["slug_abweichungen"] == []


def test_main_prueft_ziel_vor_dem_passwort(monkeypatch, tmp_path, capsys):
    monkeypatch.delenv("MIGRATION_APP_PASSWORD", raising=False)
    pwdatei = tmp_path / "gibtsnicht.pw"  # würde beim Lesen eine Ausnahme auslösen
    assert migration.main(["--export", str(tmp_path), "--url", "https://alt.tamil.de", "--passwort-datei", str(pwdatei)]) == 2


# ---- schreibende Sitzung folgt keinen Weiterleitungen

def _wp_klasse():
    return migration._lade_wp_klasse()


class _FakeHttp:
    def __init__(self, antwort):
        self.antwort, self.aufrufe = antwort, []

    def request(self, method, url, **kw):
        self.aufrufe.append((method, url, kw))
        return self.antwort


class _R:
    def __init__(self, code, header=None, daten=None):
        self.status_code, self.headers, self._d, self.text = code, header or {}, daten if daten is not None else {}, ""

    def json(self):
        return self._d


@pytest.mark.parametrize("code", [301, 302, 307, 308])
def test_wp_req_folgt_keinen_weiterleitungen(code):
    wp = _wp_klasse()("http://127.0.0.1:1", "u", "geheim")
    wp.http = _FakeHttp(_R(code, {"Location": "https://www.tamil.de/wp-json/x"}))
    with pytest.raises(RuntimeError) as exc:
        wp.req("POST", "tamil-radar/v1/beitrag", json={})
    assert "www.tamil.de" in str(exc.value) and "geheim" not in str(exc.value)
    assert wp.http.aufrufe[0][2]["allow_redirects"] is False


def test_wp_req_normal_weiter():
    wp = _wp_klasse()("http://127.0.0.1:1", "u", "p")
    wp.http = _FakeHttp(_R(200, daten={"ok": 1}))
    assert wp.req("GET", "x") == (200, {"ok": 1})


# ---- kleinere Punkte

def test_medien_sitzung_ohne_retry_adapter(tmp_path):
    m = migration.Medien(tmp_path)
    assert m.session.get_adapter("https://www.tamil.de").max_retries.total == 0


def test_voruebergehende_fehler_und_rueckgabecode_logik():
    assert migration.ist_voruebergehend(503) and migration.ist_voruebergehend(429)
    assert migration.ist_voruebergehend("Netzfehler: timeout") and migration.ist_voruebergehend("Upload 500")
    assert not migration.ist_voruebergehend(404) and not migration.ist_voruebergehend(403)
    assert not migration.ist_voruebergehend("fremder Host")
    assert not migration.ist_voruebergehend("Weiterleitung auf fremden Host")


def test_http_gross_geschrieben_wird_https(tmp_path):
    m = _medien(tmp_path, [_Antwort(200, b"X")])
    m.holen("HTTP://www.tamil.de/wp-content/uploads/2020/03/d.jpg")
    assert m.session.aufrufe[0][0].startswith("https://")
    assert migration.rewrite_html('<img src="HTTP://www.tamil.de/wp-content/uploads/2020/03/d.jpg">',
                                  {"https://www.tamil.de/wp-content/uploads/2020/03/d.jpg": "https://n/d.jpg"}).count("https://n/d.jpg") == 1


def test_kollisionspruefung_ohne_200_schreibt_nichts(tmp_path):
    wp = FakeWP()
    for i, slug in ((1, "s1"), (2, "s2-2"), (3, "s3")):
        wp.beitraege[f"alt-{i}"] = {"id": 100 + i, "slug": slug, "link": f"http://127.0.0.1:1/{slug}/"}
    wp.req_orig = wp.req
    wp.req = lambda method, path, **kw: (500, {}) if path == "wp/v2/posts" else wp.req_orig(method, path, **kw)
    m = _mig(tmp_path, wp)
    assert m.abweichungen(_posts(), {1: "news"}, []) == []
    assert m.bericht["slug_pruefung_fehlgeschlagen"][0]["status"] == 500


def test_seite_bereinigen_behaelt_tabellen_und_zitate():
    h = "<table><caption>C</caption><colgroup><col></colgroup><tbody><tr><td>x</td></tr></tbody><tfoot><tr><td>f</td></tr></tfoot></table><s>a</s><mark>b</mark><abbr title=\"t\">c</abbr><cite>d</cite>"
    sauber = migration.seite_bereinigen(h)
    for tag in ("caption", "colgroup", "tfoot", "<s>", "mark", "abbr", "cite"):
        assert tag in sauber


def test_leere_seite_fuellen_fehler_bricht_ab(tmp_path):
    class W(FakeWP):
        def req(self, method, path, **kw):
            if method == "GET" and path == "wp/v2/pages":
                return 200, [{"id": 7, "content": {"raw": ""}}]
            return 500, {"message": "kaputt"}
    m = _mig(tmp_path, W())
    quelle = {"content": {"rendered": "<p>" + "Wort " * 30 + "</p>"}, "date": "2020-01-01T00:00:00"}
    with pytest.raises(RuntimeError):
        m.seite("kontakt", "Kontakt", quelle, "seite-x")
