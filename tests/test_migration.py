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


@pytest.mark.parametrize("url", ["https://tamil-web.example.sslip.io", "https://nottamil.de", "https://tamil.de.evil.example",
                                 "http://127.0.0.1:8086", "http://localhost:8085", "http://[::1]:8085"])
def test_ziel_pruefen_erlaubt(url):
    assert migration.ziel_pruefen(url) == ""


def test_http_nur_lokal():
    assert "Klartext" in migration.ziel_pruefen("http://neu.example")
    assert "Klartext" in migration.ziel_pruefen("http://10.0.0.5")


def test_nach_umschaltung_nur_mit_beiden_schaltern():
    assert migration.ziel_pruefen("https://www.tamil.de", True, False)
    assert migration.ziel_pruefen("https://alt.tamil.de", True, True)  # Unterdomain nie
    assert migration.ziel_pruefen("https://www.tamil.de", True, True) == ""
    assert migration.ziel_pruefen("https://tamil.de", True, True) == ""


@pytest.mark.parametrize("url", ["https://TAMIL.DE", "https://x@tamil.de", "https://tamil.de.", "https://alt.tamil.de",
                                 "https://www.tamil.de:8443", "http://neu.example"])
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
