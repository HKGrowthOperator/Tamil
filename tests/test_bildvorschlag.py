"""Bild mit Nachweis: ein Agent schlägt für einen wartenden Entwurf ein echtes Bild vor (Wikimedia Commons oder Material
einer gelisteten Bildquelle); der Radar prüft Herkunft und Rechte selbst, holt das Bild, legt den Lizenz-Datensatz an.

Kein Netz: Abrufe über einen Fake mit derselben Form wie net.safe_get (Fetched), DNS kommt aus conftest.
"""

import io
import json

import pytest
from PIL import Image

from news_radar import bildvorschlag, net, schalter
from news_radar.config import Bildquelle, load_settings
from news_radar.store import Store
from news_radar.workflow import repo

DOK = "https://www.murugantemple.ch/aktuell/thaipusam-2026"
TEMPEL = Bildquelle(host="murugantemple.ch", betreiber="Sri Sivasubramaniar Tempel Zürich", art="tempel",
                    nachweis="Foto: Sri Sivasubramaniar Tempel Zürich")
GESPERRT_IM_REGISTER = Bildquelle(host="fbcdn.net", betreiber="Facebook", art="verein", nachweis="Foto: Facebook")
OG = "https://www.murugantemple.ch/media/thaipusam-og.jpg"
IMG = "https://www.murugantemple.ch/media/prozession-gross.jpg"
COMMONS_SEITE = "https://commons.wikimedia.org/wiki/File:Thaipusam_Zurich_2019.jpg"
COMMONS_THUMB = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Thaipusam_Zurich_2019.jpg/1600px-x.jpg"


def jpeg(w=1600, h=1000, fmt="JPEG") -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (w, h), (180, 90, 40)).save(buf, fmt)
    return buf.getvalue()


def seite(og=OG, body="") -> str:
    kopf = f'<meta property="og:image" content="{og}">' if og else ""
    return (f"<html><head><title>Thaipusam</title>{kopf}</head><body><article><p>Prozession in Zürich.</p>"
            f'<figure><img src="/media/prozession-gross.jpg" alt="Prozession"><figcaption>Prozession 2026</figcaption>'
            f"</figure>{body}</article></body></html>")


def cc_url(lizenz: str) -> str:
    """Lizenz-Adresse, wie Commons sie zum Kurznamen liefert (by, by-sa; sonst leer)."""
    import re as _re
    v = (_re.search(r"\d\.\d", lizenz) or [None])[0] or "4.0"
    art = "by-sa" if "sa" in lizenz.lower() else "by" if "by" in lizenz.lower() else ""
    return f"https://creativecommons.org/licenses/{art}/{v}/" if art else ""


def commons_api(lizenz="CC BY-SA 4.0", artist='<a href="//commons.wikimedia.org/wiki/User:X">Anna K.</a>',
                mime="image/jpeg", breite=4000, lizenz_url=None, titel="File:Thaipusam Zurich 2019.jpg",
                weitere=False, normalized=True):
    lizenz_url = cc_url(lizenz) if lizenz_url is None else lizenz_url
    ext = {"LicenseShortName": {"value": lizenz}, "License": {"value": lizenz.lower().replace(" ", "-")},
           "LicenseUrl": {"value": lizenz_url}, "AttributionRequired": {"value": "true"}}
    if artist is not None:
        ext["Artist"] = {"value": artist}
    info = {"url": "https://upload.wikimedia.org/wikipedia/commons/a/ab/Thaipusam_Zurich_2019.jpg",
            "thumburl": COMMONS_THUMB, "width": breite, "height": 2500, "mime": mime, "extmetadata": ext}
    pages = {"123": {"title": titel, "imageinfo": [info]}}
    if weitere:
        pages["124"] = {"title": "File:Anderes.jpg", "imageinfo": [info]}
    query = {"pages": pages}
    if normalized:
        query["normalized"] = [{"from": "File:Thaipusam_Zurich_2019.jpg", "to": "File:Thaipusam Zurich 2019.jpg"}]
    return json.dumps({"query": query})


def fake(seiten: dict, abrufe: list | None = None, umleitung: dict | None = None):
    """Wie net.safe_get, ohne Netz: str → HTML/JSON, bytes → Bild; unbekannte Adresse → 404."""
    def abruf(url, *, frist=None, bild=False):
        if abrufe is not None:
            abrufe.append(url)
        if url.startswith("https://commons.wikimedia.org/w/api.php"):
            url = "API"
        if url not in seiten:
            raise net.HTTPError(404, url)
        inhalt = seiten[url]
        if isinstance(inhalt, Exception):
            raise inhalt
        if isinstance(inhalt, bytes):
            return net.Fetched(url=url, status=200, content=inhalt, content_type="image/jpeg")
        ctype = "application/json" if url == "API" else "text/html; charset=utf-8"
        return net.Fetched(url=(umleitung or {}).get(url, url), status=200, content=inhalt.encode(), content_type=ctype)
    return abruf


@pytest.fixture
def settings(tmp_path, monkeypatch):
    for var in ("WP_URL", "WP_USER", "WP_APP_PASSWORD", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "GEMINI_API_KEY",
                "BILD_POOL_DIR", "NOTIFY_WEBHOOK_URL", "RADAR_AGENT_TOKEN"):
        monkeypatch.setenv(var, "")
    s = load_settings()
    s.data_dir = tmp_path
    s.bildquellen = [TEMPEL, GESPERRT_IM_REGISTER]
    return s


def story_mit_entwurf(store, url=DOK, status=None) -> tuple[int, int]:
    sid = repo.story_anlegen(store, typ="news", titel="Thaipusam in Zürich")
    repo.dokument_hinzufuegen(store, sid, url=url, publisher="murugantemple.ch", text="Prozession")
    did = store.insert_draft({"uid": f"bild-{sid}", "titel": "Thaipusam in Zürich", "story_id": sid,
                              "kategorie": "community", "bild_datei": "alt.jpg", "bild_credit": "Grafik: Tamil.de",
                              "bild_origin": "karte"})
    if status:
        store.set_status(did, status)
    return sid, did


def vorschlagen(store, settings, eintraege, seiten, abrufe=None, **kw):
    return bildvorschlag.annehmen(store, settings, {"bilder": eintraege}, von="test", abruf=fake(seiten, abrufe), **kw)


def eins(store, settings, eintrag, seiten, abrufe=None):
    return vorschlagen(store, settings, [eintrag], seiten, abrufe)["ergebnisse"][0]


# ---- Commons ------------------------------------------------------------------------------------------

def test_commons_cc_by_sa_gesetzt_mit_nachweis_lizenz_und_protokoll(settings):
    with Store(settings.db_path) as store:
        sid, did = story_mit_entwurf(store)
        settings.bilder_dir.mkdir(parents=True, exist_ok=True)
        (settings.bilder_dir / "alt.jpg").write_bytes(b"x")
        e = eins(store, settings, {"story_id": sid, "weg": "commons", "seite_url": COMMONS_SEITE,
                                   "alt": "Prozession beim Thaipusam in Zürich"},
                 {"API": commons_api(), COMMONS_THUMB: jpeg()})
        assert e["ergebnis"] == "gesetzt", e
        assert e["entwurf_id"] == did and e["nachweis"] == "Foto: Anna K. / Wikimedia Commons, CC BY-SA 4.0"
        d = store.get_draft(did)
        assert d["bild_credit"] == e["nachweis"] and d["bild_origin"] == "commons"
        assert d["bild_alt"] == "Prozession beim Thaipusam in Zürich"
        assert (settings.bilder_dir / d["bild_datei"]).is_file() and not (settings.bilder_dir / "alt.jpg").exists()
        with Image.open(settings.bilder_dir / d["bild_datei"]) as img:
            assert img.size == (1200, 675)
        a = repo.asset_fuer_datei(store, d["bild_datei"])
        assert a["herkunft"] == "commons" and a["rechteinhaber"] == "Anna K." and a["quelle_url"] == COMMONS_SEITE
        assert "CC BY-SA 4.0" in a["lizenz"] and "creativecommons.org" in a["lizenz"]
        assert a["attribution"] == e["nachweis"] and "Zuschnitt" in a["umfang"] and a["draft_id"] == did
        zeile = repo.aktionen(store, did)[-1]
        assert zeile["aktion"] == "bild" and zeile["wer"] == "test" and zeile["kanal"] == "redaktion"
        assert zeile["ausloeser"] == "agent"
        assert any(ev.get("id") == did for ev in store.iter_log(event="bild"))


@pytest.mark.parametrize("lizenz,artist,mime,grund", [
    ("CC BY-NC-SA 4.0", "Anna", "image/jpeg", "Lizenz"),
    ("CC BY-ND 2.0", "Anna", "image/jpeg", "Lizenz"),
    ("GFDL", "Anna", "image/jpeg", "Lizenz"),
    ("", "Anna", "image/jpeg", "Lizenz"),
    ("CC BY 4.0", None, "image/jpeg", "Namensnennung"),
    ("CC BY-SA 3.0", "<span></span>", "image/jpeg", "Namensnennung"),
    ("CC BY 4.0", "Anna", "image/svg+xml", "Dateityp"),
])
def test_commons_abgelehnt(settings, lizenz, artist, mime, grund):
    with Store(settings.db_path) as store:
        sid, did = story_mit_entwurf(store)
        abrufe = []
        e = eins(store, settings, {"story_id": sid, "weg": "commons", "seite_url": COMMONS_SEITE},
                 {"API": commons_api(lizenz, artist, mime), COMMONS_THUMB: jpeg()}, abrufe)
        assert e["ergebnis"] == "abgelehnt" and grund in e["grund"], e
        assert COMMONS_THUMB not in abrufe and store.get_draft(did)["bild_origin"] == "karte"


@pytest.mark.parametrize("lizenz,url", [
    ("CC BY NC", None), ("CC BY 4.0 ND", None), ("CC BY-SA 4.0 nc", None), ("PD-fairuse", ""),
    ("pd-us-unpublished", ""), ("CC BY 4.0", "https://creativecommons.org/licenses/by-nc/4.0/"),
    ("CC BY-SA 4.0", "https://creativecommons.org/licenses/by/4.0/"), ("CC BY 4.0", ""),
    ("CC BY 4.0", "https://example.org/licenses/by/4.0/"), ("Public domain", "https://example.org/pd"),
])
def test_commons_lizenz_nur_ueber_positivliste_und_adresse(settings, lizenz, url):
    with Store(settings.db_path) as store:
        sid, _ = story_mit_entwurf(store)
        e = eins(store, settings, {"story_id": sid, "weg": "commons", "seite_url": COMMONS_SEITE},
                 {"API": commons_api(lizenz, "Anna", lizenz_url=url), COMMONS_THUMB: jpeg()})
        assert e["ergebnis"] == "abgelehnt" and "Lizenz" in e["grund"], e


@pytest.mark.parametrize("lizenz,url", [
    ("CC BY 2.0 de", "https://creativecommons.org/licenses/by/2.0/de/"), ("CC0", "https://creativecommons.org/publicdomain/zero/1.0/"),
    ("PD-old-70", ""), ("Public domain", ""), ("CC BY-SA 3.0", "http://creativecommons.org/licenses/by-sa/3.0"),
])
def test_commons_lizenz_erlaubt(settings, lizenz, url):
    with Store(settings.db_path) as store:
        sid, _ = story_mit_entwurf(store)
        e = eins(store, settings, {"story_id": sid, "weg": "commons", "seite_url": COMMONS_SEITE},
                 {"API": commons_api(lizenz, "Anna", lizenz_url=url), COMMONS_THUMB: jpeg()})
        assert e["ergebnis"] == "gesetzt", e


@pytest.mark.parametrize("artist,ergebnis,erwartet", [
    ("&lt;script&gt;alert(1)&lt;/script&gt;Anna K.", "gesetzt", "Foto: Anna K. / Wikimedia Commons, CC BY-SA 4.0"),
    ("<b>Anna</b> &amp; Ravi", "gesetzt", "Foto: Anna & Ravi / Wikimedia Commons, CC BY-SA 4.0"),
    ("Anna\u202eK.", "abgelehnt", "Urheber"),
    ("Anna\x07K.", "abgelehnt", "Urheber"),
    ("A" * 81, "abgelehnt", "Urheber"),
])
def test_commons_urhebername(settings, artist, ergebnis, erwartet):
    with Store(settings.db_path) as store:
        sid, _ = story_mit_entwurf(store)
        e = eins(store, settings, {"story_id": sid, "weg": "commons", "seite_url": COMMONS_SEITE},
                 {"API": commons_api(artist=artist), COMMONS_THUMB: jpeg()})
        assert e["ergebnis"] == ergebnis, e
        assert erwartet in (e.get("nachweis") or e["grund"])
        assert "script" not in (e.get("nachweis") or "") and "alert" not in (e.get("nachweis") or "")


def test_commons_gemeinfrei_ohne_artist(settings):
    with Store(settings.db_path) as store:
        sid, _ = story_mit_entwurf(store)
        e = eins(store, settings, {"story_id": sid, "weg": "commons", "seite_url": COMMONS_SEITE},
                 {"API": commons_api("Public domain", None, lizenz_url=""), COMMONS_THUMB: jpeg()})
        assert e["ergebnis"] == "gesetzt" and e["nachweis"] == "Foto: Wikimedia Commons, gemeinfrei"


def test_commons_zu_schmal_abgelehnt(settings):
    with Store(settings.db_path) as store:
        sid, _ = story_mit_entwurf(store)
        e = eins(store, settings, {"story_id": sid, "weg": "commons", "seite_url": COMMONS_SEITE},
                 {"API": commons_api(breite=640), COMMONS_THUMB: jpeg()})
        assert e["ergebnis"] == "abgelehnt" and "800" in e["grund"]


@pytest.mark.parametrize("url", [
    "https://commons.wikimedia.org/wiki/Category:Thaipusam",
    "https://en.wikipedia.org/wiki/File:Thaipusam.jpg",
    "https://commons.wikimedia.org.evil.example/wiki/File:X.jpg",
])
def test_commons_keine_dateiseite_abgelehnt(settings, url):
    with Store(settings.db_path) as store:
        sid, _ = story_mit_entwurf(store)
        abrufe = []
        e = eins(store, settings, {"story_id": sid, "weg": "commons", "seite_url": url}, {}, abrufe)
        assert e["ergebnis"] == "abgelehnt" and "Dateiseite" in e["grund"] and abrufe == []


@pytest.mark.parametrize("url", [COMMONS_SEITE.replace(".jpg", ".jpg%7CFile:Anderes.jpg"),
                                 COMMONS_SEITE.replace(".jpg", ".jpg|File:Anderes.jpg"), COMMONS_SEITE + "%23x",
                                 COMMONS_SEITE.replace("Zurich", "Zu%00rich"), COMMONS_SEITE.replace("Zurich", "Zu[r]ich")])
def test_commons_titel_mit_sonderzeichen_abgelehnt(settings, url):
    with Store(settings.db_path) as store:
        sid, _ = story_mit_entwurf(store)
        abrufe = []
        e = eins(store, settings, {"story_id": sid, "weg": "commons", "seite_url": url}, {}, abrufe)
        assert e["ergebnis"] == "abgelehnt" and "Dateiseite" in e["grund"] and abrufe == [], e


@pytest.mark.parametrize("api", [commons_api(weitere=True), commons_api(titel="File:Anderes.jpg"),
                                 json.dumps({"query": {"pages": {}}})])
def test_commons_genau_die_verlinkte_datei(settings, api):
    with Store(settings.db_path) as store:
        sid, _ = story_mit_entwurf(store)
        e = eins(store, settings, {"story_id": sid, "weg": "commons", "seite_url": COMMONS_SEITE},
                 {"API": api, COMMONS_THUMB: jpeg()})
        assert e["ergebnis"] == "abgelehnt", e


# ---- Quelle aus dem Register --------------------------------------------------------------------------

def test_quelle_og_image_mit_nachweis_aus_dem_register(settings):
    with Store(settings.db_path) as store:
        sid, did = story_mit_entwurf(store)
        e = eins(store, settings, {"story_id": sid, "weg": "quelle", "seite_url": DOK}, {DOK: seite(), OG: jpeg()})
        assert e["ergebnis"] == "gesetzt", e
        assert e["nachweis"] == "Foto: Sri Sivasubramaniar Tempel Zürich"
        d = store.get_draft(did)
        assert d["bild_credit"] == e["nachweis"] and d["bild_origin"] == "quelle" and d["bild_alt"] in (None, "")
        a = repo.asset_fuer_datei(store, d["bild_datei"])
        assert a["herkunft"] == "quelle" and a["rechteinhaber"] == TEMPEL.betreiber and a["quelle_url"] == OG
        assert "tempel" in a["lizenz"] and "keine ausdrückliche Lizenz" in a["lizenz"]


def test_quelle_nachweis_nie_aus_dem_vorschlag(settings):
    with Store(settings.db_path) as store:
        sid, _ = story_mit_entwurf(store)
        e = eins(store, settings, {"story_id": sid, "weg": "quelle", "seite_url": DOK, "nachweis": "Foto: Erfunden"},
                 {DOK: seite(), OG: jpeg()})
        assert e["ergebnis"] == "gesetzt" and e["nachweis"] == TEMPEL.nachweis


def test_quelle_bild_url_aus_dem_html(settings):
    with Store(settings.db_path) as store:
        sid, did = story_mit_entwurf(store)
        e = eins(store, settings, {"story_id": sid, "weg": "quelle", "seite_url": DOK, "bild_url": IMG},
                 {DOK: seite(), IMG: jpeg(2000, 1300)})
        assert e["ergebnis"] == "gesetzt", e
        assert repo.asset_fuer_datei(store, store.get_draft(did)["bild_datei"])["quelle_url"] == IMG


@pytest.mark.parametrize("eintrag,seiten,grund", [
    ({"seite_url": "https://www.srf.ch/news/thaipusam"}, {}, "Register"),
    ({"seite_url": "https://www.murugantemple.ch/andere-seite"}, {}, "Dokument"),
    ({"seite_url": DOK, "bild_url": "https://www.murugantemple.ch/media/fremd.jpg"}, {DOK: seite()}, "nicht auf der Seite"),
    ({"seite_url": DOK, "bild_url": IMG}, {DOK: seite(body='<p>Foto: Keystone / SDA</p>'), IMG: jpeg()}, "Agenturbild"),
    ({"seite_url": DOK}, {DOK: seite(og="https://www.murugantemple.ch/media/dpa-12345.jpg")}, "Agenturbild"),
    ({"seite_url": DOK}, {DOK: seite(), OG: jpeg(700, 500)}, "zu klein"),
    ({"seite_url": DOK}, {DOK: seite(), OG: jpeg(2400, 300)}, "zu klein"),
    ({"seite_url": DOK}, {DOK: seite(), OG: jpeg(3000, 1000)}, "Seitenverhältnis"),
    ({"seite_url": DOK}, {DOK: seite(og="https://scontent.xx.fbcdn.net/v/t1/bild.jpg")}, "gesperrt"),
    ({"seite_url": DOK}, {DOK: seite(og="")}, "kein Bild"),
    ({"seite_url": DOK}, {DOK: seite(og="https://cdn.example.org/fremd.jpg"),
                          "https://cdn.example.org/fremd.jpg": jpeg()}, "Host"),
    ({"seite_url": DOK}, {DOK: seite(og="https://bilder.keystone.ch/fremd.jpg")}, "gesperrt"),
    ({"seite_url": DOK}, {DOK: seite(og="https://www.apnews.com/a.jpg")}, "gesperrt"),
    ({"seite_url": DOK}, {DOK: seite(og="https://cdn.ap.org/a.jpg")}, "gesperrt"),
    ({"seite_url": DOK}, {DOK: seite(og="https://epa.eu/a.jpg")}, "gesperrt"),
])
def test_quelle_abgelehnt(settings, eintrag, seiten, grund):
    with Store(settings.db_path) as store:
        sid, did = story_mit_entwurf(store)
        e = eins(store, settings, {"story_id": sid, "weg": "quelle", **eintrag}, seiten)
        assert e["ergebnis"] == "abgelehnt" and grund in e["grund"], e
        assert store.get_draft(did)["bild_origin"] == "karte"


def test_bild_zu_viele_pixel_wird_nicht_dekodiert(settings, monkeypatch):
    buf = io.BytesIO()
    Image.new("1", (9000, 5000)).save(buf, "PNG")  # 45 Mio. Pixel, stark komprimierbar (wenige KB)
    assert len(buf.getvalue()) < 1_000_000
    geladen = []
    original = Image.Image.load
    monkeypatch.setattr(Image.Image, "load", lambda self: geladen.append(self.size) or original(self))
    with Store(settings.db_path) as store:
        sid, _ = story_mit_entwurf(store)
        e = eins(store, settings, {"story_id": sid, "weg": "quelle", "seite_url": DOK},
                 {DOK: seite(), OG: buf.getvalue()})
        assert e["ergebnis"] == "abgelehnt" and "zu groß" in e["grund"], e
        assert (9000, 5000) not in geladen
        e = eins(store, settings, {"story_id": sid, "weg": "quelle", "seite_url": DOK},
                 {DOK: seite(), OG: jpeg(fmt="GIF")})
        assert e["ergebnis"] == "abgelehnt" and "Dateityp" in e["grund"], e


def test_quelle_bild_auf_eigenem_cdn_ueber_bild_hosts(settings):
    settings.bildquellen = [Bildquelle(host=TEMPEL.host, betreiber=TEMPEL.betreiber, art="tempel",
                                       nachweis=TEMPEL.nachweis, bild_hosts=["cdn.example.org"])]
    with Store(settings.db_path) as store:
        sid, _ = story_mit_entwurf(store)
        cdn = "https://img.cdn.example.org/fremd.jpg"
        e = eins(store, settings, {"story_id": sid, "weg": "quelle", "seite_url": DOK}, {DOK: seite(og=cdn), cdn: jpeg()})
        assert e["ergebnis"] == "gesetzt", e


def test_quelle_bild_auf_fremdem_host_abgelehnt(settings):
    with Store(settings.db_path) as store:
        sid, _ = story_mit_entwurf(store)
        fremd = "https://cdn.example.org/fremd.jpg"
        html = seite(body=f'<img src="{fremd}" alt="Tempel">')
        e = eins(store, settings, {"story_id": sid, "weg": "quelle", "seite_url": DOK, "bild_url": fremd},
                 {DOK: html, fremd: jpeg()})
        assert e["ergebnis"] == "abgelehnt" and "Host" in e["grund"]


@pytest.mark.parametrize("ziel,ergebnis", [("https://www.ammankovil.ch/aktuell/x", "abgelehnt"),
                                           ("https://news.murugantemple.ch/thaipusam", "gesetzt")])
def test_quelle_umleitung_nur_beim_eingetragenen_host(settings, ziel, ergebnis):
    settings.bildquellen = [TEMPEL, Bildquelle(host="ammankovil.ch", betreiber="Amman", art="tempel",
                                               nachweis="Foto: Amman")]
    with Store(settings.db_path) as store:
        sid, _ = story_mit_entwurf(store)
        og = ziel.rsplit("/", 1)[0] + "/bild.jpg"
        out = bildvorschlag.annehmen(store, settings, {"bilder": [{"story_id": sid, "weg": "quelle", "seite_url": DOK}]},
                                     von="test", abruf=fake({DOK: seite(og=og), og: jpeg()}, umleitung={DOK: ziel}))
        e = out["ergebnisse"][0]
        assert e["ergebnis"] == ergebnis, e
        if ergebnis == "abgelehnt":
            assert "umgeleitet" in e["grund"]


def test_gesperrter_host_auch_im_register(settings):
    with Store(settings.db_path) as store:
        url = "https://scontent.fbcdn.net/seite"
        sid, _ = story_mit_entwurf(store, url=url)
        abrufe = []
        e = eins(store, settings, {"story_id": sid, "weg": "quelle", "seite_url": url}, {}, abrufe)
        assert e["ergebnis"] == "abgelehnt" and "gesperrt" in e["grund"] and abrufe == []


def test_interne_adresse_abgelehnt_nichts_abgerufen(settings, monkeypatch):
    monkeypatch.setattr(net, "_resolve", lambda host: ["10.0.0.5"] if "murugantemple" in host else ["93.184.216.34"])
    with Store(settings.db_path) as store:
        sid, _ = story_mit_entwurf(store)
        abrufe = []
        e = eins(store, settings, {"story_id": sid, "weg": "quelle", "seite_url": DOK}, {DOK: seite(), OG: jpeg()},
                 abrufe)
        assert e["ergebnis"] == "abgelehnt" and "interne Adresse" in e["grund"] and abrufe == []
        e = eins(store, settings, {"story_id": sid, "weg": "quelle", "seite_url": DOK,
                                   "bild_url": "http://169.254.169.254/latest/meta-data"}, {DOK: seite()}, abrufe)
        assert e["ergebnis"] == "abgelehnt" and "interne Adresse" in e["grund"] and abrufe == []


# ---- Entwurf, Eingabe, Stopp, Zeitlimit ---------------------------------------------------------------

def test_entwurf_schon_freigegeben_oder_keiner(settings):
    with Store(settings.db_path) as store:
        sid, _ = story_mit_entwurf(store, status="freigeben")
        abrufe = []
        e = eins(store, settings, {"story_id": sid, "weg": "quelle", "seite_url": DOK}, {DOK: seite(), OG: jpeg()},
                 abrufe)
        assert e["ergebnis"] == "abgelehnt" and "schon freigegeben" in e["grund"] and abrufe == []
        leer = repo.story_anlegen(store, typ="news", titel="Ohne Entwurf")
        e = eins(store, settings, {"story_id": leer, "weg": "quelle", "seite_url": DOK}, {})
        assert e["ergebnis"] == "abgelehnt" and "kein wartender Entwurf" in e["grund"]


def test_eingabe_fehler(settings):
    with Store(settings.db_path) as store:
        sid, _ = story_mit_entwurf(store)
        for eintrag, grund in (({"story_id": sid, "weg": "stock", "seite_url": DOK}, "weg"),
                               ({"story_id": sid, "weg": "quelle", "seite_url": DOK, "alt": "x" * 161}, "alt"),
                               ({"story_id": sid, "weg": "quelle", "seite_url": "ftp://x.ch/a"}, "seite_url")):
            e = eins(store, settings, eintrag, {})
            assert e["ergebnis"] == "abgelehnt" and grund in e["grund"], e
        with pytest.raises(ValueError, match="höchstens 5"):
            vorschlagen(store, settings, [{}] * 6, {}, max_bilder=5)


def test_stopp_mitten_im_stapel_und_zeitlimit(settings):
    with Store(settings.db_path) as store:
        sid, _ = story_mit_entwurf(store)
        eintrag = {"story_id": sid, "weg": "quelle", "seite_url": DOK}
        out = vorschlagen(store, settings, [eintrag], {DOK: seite(), OG: net.Zeitlimit("zu langsam")})
        assert out["nicht_bearbeitet"] == 1 and "Zeitlimit" in out["ergebnisse"][0]["grund"]
        zeit = iter([0.0, 0.0, 100.0, 100.0, 100.0, 100.0])
        out = vorschlagen(store, settings, [eintrag, eintrag], {DOK: seite(), OG: jpeg()}, frist_gesamt=50.0,
                          uhr=lambda: next(zeit, 100.0))
        assert out["ergebnisse"][-1]["ergebnis"] == "nicht_bearbeitet"
        schalter.setzen(store, "redaktion", True, wer="anna", grund="prüfen")
        abrufe = []
        with pytest.raises(schalter.Gestoppt):
            vorschlagen(store, settings, [eintrag], {DOK: seite(), OG: jpeg()}, abrufe)
        assert abrufe == []


# ---- Route, CLI, Cockpit ------------------------------------------------------------------------------

def test_route_bild_mit_token_stopp_und_fehlern(settings, monkeypatch):
    from news_radar.web import create_app

    abrufe = []
    monkeypatch.setattr(bildvorschlag, "standard_abruf", fake({DOK: seite(), OG: jpeg()}, abrufe))
    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim", "s3cret"
    client = create_app(settings, testing=True).test_client()
    with Store(settings.db_path) as store:
        sid, did = story_mit_entwurf(store)
    eintrag = {"story_id": sid, "weg": "quelle", "seite_url": DOK}
    assert client.post("/api/agent/bild", json={"bilder": []}).status_code == 404
    settings.agent_token = "agent-token-mit-genug-zeichen"
    kopf = {"Authorization": "Bearer agent-token-mit-genug-zeichen"}
    assert client.post("/api/agent/bild", json={"bilder": []}, headers={"Authorization": "Bearer x"}).status_code == 401
    assert client.post("/api/agent/bild", data="x", headers=kopf, content_type="text/plain").status_code == 400
    zu_viele = client.post("/api/agent/bild", json={"bilder": [eintrag] * 6}, headers=kopf)
    assert zu_viele.status_code == 400 and "höchstens 5" in zu_viele.get_json()["fehler"] and abrufe == []
    with Store(settings.db_path) as store:
        schalter.setzen(store, "redaktion", True, wer="anna", grund="prüfen")
    resp = client.post("/api/agent/bild", json={"bilder": [eintrag]}, headers=kopf)
    assert resp.status_code == 409 and resp.get_json()["kanal"] == "redaktion" and abrufe == []
    with Store(settings.db_path) as store:
        schalter.setzen(store, "redaktion", False, wer="anna")
    resp = client.post("/api/agent/bild?von=bildagent", json={"bilder": [eintrag]}, headers=kopf)
    data = resp.get_json()
    assert resp.status_code == 200 and data["gesetzt"] == 1 and data["ergebnisse"][0]["entwurf_id"] == did
    with Store(settings.db_path) as store:
        assert repo.aktionen(store, did)[-1]["wer"] == "bildagent"


def test_cli_agent_bild(settings, monkeypatch, tmp_path, capsys):
    from news_radar.__main__ import main

    monkeypatch.setattr(bildvorschlag, "standard_abruf", fake({DOK: seite(), OG: jpeg()}))
    monkeypatch.setenv("RADAR_DATA_DIR", str(settings.data_dir))
    monkeypatch.setattr("news_radar.__main__.load_settings", lambda: settings, raising=False)
    with Store(settings.db_path) as store:
        sid, did = story_mit_entwurf(store)
    datei = tmp_path / "bilder.json"
    datei.write_text(json.dumps({"bilder": [{"story_id": sid, "weg": "quelle", "seite_url": DOK}]}), encoding="utf-8")
    assert main(["agent", "bild", "--datei", str(datei)]) == 0
    assert "1 gesetzt" in capsys.readouterr().out
    with Store(settings.db_path) as store:
        assert store.get_draft(did)["bild_origin"] == "quelle"


def test_cockpit_zeigt_nachweis_lizenz_und_link(settings):
    from news_radar.web import create_app

    from test_web_redaktion import login

    with Store(settings.db_path) as store:
        sid, did = story_mit_entwurf(store)
        eins(store, settings, {"story_id": sid, "weg": "commons", "seite_url": COMMONS_SEITE},
             {"API": commons_api(), COMMONS_THUMB: jpeg()})
    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim", "s3cret"
    client = create_app(settings, testing=True).test_client()
    login(client)
    html = client.get(f"/entwurf/{did}").get_data(as_text=True)
    assert "Foto: Anna K. / Wikimedia Commons, CC BY-SA 4.0" in html
    assert "Wikimedia Commons</span>" in html and f'href="{COMMONS_SEITE}"' in html
    assert "Lizenz: CC BY-SA 4.0" in html


def test_register_aus_sources_toml():
    s = load_settings()
    assert len(s.bildquellen) >= 28
    assert all(b.host == b.host.lower() and not b.host.startswith("www.") and b.nachweis for b in s.bildquellen)
    with pytest.raises(ValueError):
        Bildquelle(host="www.example.ch", betreiber="X", art="verein", nachweis="Foto: X")
    with pytest.raises(ValueError):
        Bildquelle(host="example.ch", betreiber="X", art="verein", nachweis=" ")
