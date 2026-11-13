"""Lizenz-Datensatz je Bild (docs/spezifikation/bilder-und-lizenzen.md, Abschnitt 3; Lücken L1–L6, L11, L12, L16, L19).

Kein Netz: Bildquellen und Bild-KI über Fakes, WordPress über einen Fake-Client.
"""

import base64
import io
import sqlite3

import pytest
from PIL import Image

from stand_hilfe import stand_von
from news_radar import images, lizenz, publisher
from news_radar.config import load_settings
from news_radar.images import branded_card, save_pair
from news_radar.store import Store
from news_radar.web import create_app
from news_radar.workflow import repo, schema


# ---- Migration und Regeln --------------------------------------------------------------------------

def test_migration_9_ergaenzt_assets_und_behaelt_altbestand(tmp_path):
    pfad = tmp_path / "radar.sqlite"
    with Store(pfad) as store:
        store.db.execute("INSERT INTO assets (datei, herkunft, lizenz, umfang, erstellt) VALUES "
                         "('alt.jpg', 'commons', 'CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)', "
                         "'Online-Veröffentlichung auf tamil.de', '2026-11-01T10:00:00+00:00')")
        store.db.execute("PRAGMA user_version = 7")
        store.db.commit()
    with Store(pfad) as store:
        assert store.db.execute("PRAGMA user_version").fetchone()[0] == schema.LATEST == 9
        spalten = {r[1] for r in store.db.execute("PRAGMA table_info(assets)")}
        assert {"urheber", "lizenz_kuerzel", "lizenz_url", "bild_url", "bearbeitung", "beleg", "geprueft_von",
                "geprueft_am", "ki_modell", "prompt_hash", "alt", "fokus"} <= spalten
        alt = dict(store.db.execute("SELECT * FROM assets WHERE datei = 'alt.jpg'").fetchone())
        assert alt["lizenz"].startswith("CC BY 4.0") and alt["lizenz_kuerzel"] is None
        assert lizenz.umfang_menge(alt["umfang"]) == set()  # Freitext zählt nicht als Umfang


def test_kuerzel_umfang_und_nachweis_nach_positivliste():
    assert lizenz.gueltig("cc-by-sa-4.0") and lizenz.gueltig("cc-by-2.5") and lizenz.gueltig("pdm-1.0")
    assert not lizenz.gueltig("cc-by-nc-4.0") and not lizenz.gueltig("cc-by-9.9") and not lizenz.gueltig("frei")
    assert lizenz.umfang_fuer("presse-redaktionell") == "website"
    assert lizenz.umfang_fuer("cc-by-sa-4.0") == "website,social,print"
    assert lizenz.umfang_fuer("pexels", {"print", "social", "website"}) == "website,social"
    assert lizenz.umfang_fuer("ki-symbolbild") == "website,social"
    assert lizenz.umfang_text({"print", "website"}) == "website,print"  # feste Reihenfolge für die Social-Spur
    assert lizenz.lizenz_url("cc-by-sa-4.0") == "https://creativecommons.org/licenses/by-sa/4.0/"
    assert lizenz.kuerzel_aus_url("https://creativecommons.org/licenses/by-sa/3.0/de/") == "cc-by-sa-3.0"
    assert lizenz.kuerzel_aus_url("https://creativecommons.org/licenses/by-nc/4.0/") == ""
    assert lizenz.nachweis_vorschlag("cc-by-sa-4.0", urheber="Max Muster", bearbeitung="zugeschnitten") == \
        "Foto: Max Muster / Wikimedia Commons, CC BY-SA 4.0, zugeschnitten"
    assert lizenz.nachweis_vorschlag("tamil-grafik") == "Grafik: Tamil.de"
    assert lizenz.alt_fehler("", "T") and lizenz.alt_fehler("abc", "T") and lizenz.alt_fehler("Titel A", "titel a")
    assert lizenz.alt_fehler("Gopuram vor bewölktem Himmel", "Tempelfest") == ""


def _vollstaendig(**mehr) -> dict:
    basis = {"datei": "a.jpg", "sha256": "ab", "herkunft": "commons", "rechteinhaber": "Max Muster",
             "urheber": "Max Muster", "lizenz_kuerzel": "cc-by-4.0", "lizenz_url": lizenz.lizenz_url("cc-by-4.0"),
             "umfang": "website,social", "attribution": "Foto: Max Muster / Wikimedia Commons, CC BY 4.0",
             "quelle_url": "https://commons.wikimedia.org/wiki/File:A.jpg", "bild_url": "https://upload.wikimedia.org/a.jpg",
             "bearbeitung": "zugeschnitten", "beleg": "commons-api", "geprueft_von": "agent:redakteur",
             "geprueft_am": "2026-11-13T19:02:00+00:00", "ki": 0}
    return {**basis, **mehr}


def test_fehlend_prueft_pflichtfelder_kuerzel_umfang_und_ablauf():
    assert lizenz.fehlend(_vollstaendig()) == []
    assert lizenz.fehlend(None) == ["datensatz"]
    assert lizenz.fehlend(_vollstaendig(urheber="")) == ["urheber"]
    assert lizenz.fehlend(_vollstaendig(urheber="unbekannt")) == ["urheber"]
    assert lizenz.fehlend(_vollstaendig(lizenz_kuerzel="cc-by-nc-4.0")) == ["lizenz_kuerzel"]
    assert lizenz.fehlend(_vollstaendig(lizenz_kuerzel="presse-redaktionell")) == ["umfang"]  # Social nicht erlaubt
    assert lizenz.fehlend(_vollstaendig(umfang="Online-Veröffentlichung auf tamil.de")) == ["umfang"]
    assert lizenz.fehlend(_vollstaendig(ablauf="2020-01-01")) == ["ablauf"]
    assert lizenz.fehlend(_vollstaendig(bild_url="")) == ["bild_url"]
    assert lizenz.fehlend(_vollstaendig(bild_url="", geprueft_von="luis")) == []  # von Hand geprüft: Seite reicht
    ki = _vollstaendig(herkunft="pool", lizenz_kuerzel="ki-symbolbild", urheber="", lizenz_url="", quelle_url="",
                       bild_url="", ki=1, ki_modell="", prompt_hash="")
    assert lizenz.fehlend(ki) == ["ki_modell", "prompt_hash"]  # Pool-Bild ohne Modell: nichts erfinden


# ---- Cockpit ---------------------------------------------------------------------------------------

class FakeWP:
    def __init__(self):
        self.posts, self.medien = [], []

    def upload_media(self, image, alt):
        self.medien.append(alt)
        return 9

    def create_post(self, **kw):
        self.posts.append(kw)
        return {"id": 500 + len(self.posts), "link": f"https://www.tamil.de/{kw['slug']}/"}

    def edit_link(self, post):
        return f"https://www.tamil.de/wp-admin/post.php?post={post['id']}&action=edit"


@pytest.fixture
def app(tmp_path, monkeypatch):
    for var in ("WP_URL", "WP_USER", "WP_APP_PASSWORD", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "GEMINI_API_KEY",
                "BILD_POOL_DIR", "BILD_KI_FREIGABE"):
        monkeypatch.setenv(var, "")
    settings = load_settings()
    settings.data_dir = tmp_path
    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim", "s3cret"
    app = create_app(settings, testing=True)
    with Store(settings.db_path) as store:
        for i, titel in enumerate(("Tempelfest in Hamm", "Pongal in Hamburg"), 1):
            name, _ = save_pair(branded_card(titel, "Community", f"u{i}"), settings.bilder_dir, f"u{i}-x")
            store.insert_draft(dict(uid=f"u{i}", typ="artikel", titel=titel, teaser="T", inhalt_html="<p>Text</p>",
                                    kategorie="community", relevanz=8, dach_bezug=True, ort="Hamm", schlagworte=["x"],
                                    bild_datei=name, bild_origin="upload", bild_alt="",
                                    quelle_url="https://q.de/1", quelle_name="Q"))
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def login(client):
    client.get("/login")
    with client.session_transaction() as s:
        token = s["csrf"]
    assert client.post("/login", data={"user": "luis", "password": "geheim", "_csrf": token}).status_code == 302
    return token


def _store(app):
    return Store(app.extensions["settings"].db_path)


def _png(farbe=(10, 10, 200)) -> io.BytesIO:
    buf = io.BytesIO()
    Image.new("RGB", (1600, 900), farbe).save(buf, "PNG")
    buf.seek(0)
    return buf


def test_freigabe_und_sammelfreigabe_ohne_datensatz_gesperrt(client, app):
    token = login(client)
    seite = client.get("/entwurf/1").get_data(as_text=True)
    assert "Lizenz fehlt: Datensatz, Alt-Text" in seite and "Lizenz eintragen" in seite
    resp = client.post("/entwurf/1/status", data={"_csrf": token, "aktion": "freigeben", "stand": stand_von(client, 1)},
                       follow_redirects=True)
    assert "Lizenz fehlt: Datensatz" in resp.get_data(as_text=True)
    resp = client.post("/entwurf/sammelfreigabe", data={"_csrf": token, "ids": ["1", "2"], "stand_1": "0", "stand_2": "0"},
                       follow_redirects=True)
    assert "Nicht freigegeben (2)" in resp.get_data(as_text=True) and "Lizenz fehlt" in resp.get_data(as_text=True)
    resp = client.post("/entwurf/1/veroeffentlichen", data={"_csrf": token, "stand": "0"}, follow_redirects=True)
    assert "Lizenz fehlt" in resp.get_data(as_text=True)
    with _store(app) as store:
        assert {store.get_draft(i)["status"] for i in (1, 2)} == {"neu"}


def test_bildkarte_im_cockpit_legt_vollstaendigen_datensatz_an_und_gibt_frei(client, app):
    token = login(client)
    client.post("/entwurf/1/bild", data={"_csrf": token, "aktion": "karte"})
    with _store(app) as store:
        d = store.get_draft(1)
        asset = repo.asset_fuer_entwurf(store, 1, d["bild_datei"])
    assert asset["lizenz_kuerzel"] == "tamil-grafik" and asset["umfang"] == "website,social,print"
    assert asset["draft_id"] == 1 and asset["sha256"] and lizenz.fehlend(asset) == []
    assert d["bild_alt"] == "Grafik mit der Überschrift: Tempelfest in Hamm"
    resp = client.post("/entwurf/1/status", data={"_csrf": token, "aktion": "freigeben", "stand": stand_von(client, 1)})
    assert resp.status_code == 302
    with _store(app) as store:
        assert store.get_draft(1)["status"] == "freigegeben"


def test_upload_ohne_standardnachweis_dann_lizenz_eintragen(client, app):
    token = login(client)
    client.post("/entwurf/1/bild", data={"_csrf": token, "aktion": "upload", "datei": (_png(), "foto.png")},
                content_type="multipart/form-data")
    with _store(app) as store:
        d = store.get_draft(1)
        asset = repo.asset_fuer_entwurf(store, 1, d["bild_datei"])
    assert d["bild_credit"] in ("", None) and "Tamil.de" not in (d["bild_credit"] or "")  # kein falscher Nachweis
    assert asset["herkunft"] == "upload" and not asset["lizenz_kuerzel"]
    assert "Lizenz fehlt" in client.get("/entwurf/1").get_data(as_text=True)

    # Prüfung nach 3.4: Fehler werden gemeldet, nichts gespeichert
    falsch = {"_csrf": token, "herkunft": "presse", "lizenz": "presse-redaktionell", "rechteinhaber": "",
              "umfang": ["website", "social"], "quelle_url": "javascript:alert(1)", "ablauf": "2020-01-01", "alt": "x"}
    text = client.post("/entwurf/1/lizenz", data=falsch, follow_redirects=True).get_data(as_text=True)
    for teil in ("Rechteinhaber fehlt", "Umfang höchstens: Website", "Quelle: nur eine http", "Ablauf muss",
                 "Alt-Text muss"):
        assert teil in text, teil
    with _store(app) as store:
        assert store.db.execute("SELECT COUNT(*) FROM assets WHERE draft_id = 1").fetchone()[0] == 1

    ok = {"_csrf": token, "herkunft": "dritte", "lizenz": "nutzungsrecht", "urheber": "Foto Kumar",
          "rechteinhaber": "Foto Kumar", "umfang": ["website", "social"], "quelle_url": "https://tempel-hamm.de/fest",
          "alt": "Gopuram des Tempels mit Blumengirlanden"}
    text = client.post("/entwurf/1/lizenz", data=ok, follow_redirects=True).get_data(as_text=True)
    assert "Beleg fehlt" in text  # Nutzungsrecht braucht einen Beleg
    beleg = io.BytesIO(b"%PDF-1.4 Erlaubnis")
    resp = client.post("/entwurf/1/lizenz", data={**ok, "beleg": "Mail vom 12.11.2026", "beleg_datei": (beleg, "mail.pdf")},
                       content_type="multipart/form-data")
    assert resp.status_code == 302
    settings = app.extensions["settings"]
    with _store(app) as store:
        d = store.get_draft(1)
        asset = repo.asset_fuer_entwurf(store, 1, d["bild_datei"])
        protokoll = [dict(r) for r in store.db.execute("SELECT * FROM editorial_actions WHERE aktion = 'lizenz'")]
    assert asset["lizenz_kuerzel"] == "nutzungsrecht" and asset["umfang"] == "website,social"
    assert asset["geprueft_von"] == "luis" and "belege/" in asset["beleg"] and lizenz.fehlend(asset) == []
    assert d["bild_credit"] == "Foto: Foto Kumar" and d["bild_alt"] == "Gopuram des Tempels mit Blumengirlanden"
    belege = list((settings.data_dir / "belege").iterdir())
    assert len(belege) == 1 and belege[0].suffix == ".pdf" and belege[0].read_bytes().startswith(b"%PDF")
    assert len(protokoll) == 1 and "nutzungsrecht" in protokoll[0]["notiz"] and "Kumar" not in protokoll[0]["notiz"]
    assert client.get("/bild/" + belege[0].name).status_code == 404  # Belege sind nicht öffentlich
    resp = client.post("/entwurf/1/status", data={"_csrf": token, "aktion": "freigeben", "stand": stand_von(client, 1)})
    with _store(app) as store:
        assert store.get_draft(1)["status"] == "freigegeben"


def test_formular_kein_ki_kuerzel_und_cc_mit_urheber():
    felder, fehler = lizenz.formular_pruefen({"herkunft": "eigen", "lizenz": "ki-symbolbild", "rechteinhaber": "X",
                                              "umfang": "website", "alt": "Ein Bild mit Motiv"}, None, titel="T")
    assert "Lizenz passt nicht" in fehler[0]
    felder, fehler = lizenz.formular_pruefen({"herkunft": "commons", "lizenz": "cc-by-sa", "version": "4.0",
                                              "rechteinhaber": "Max", "urheber": "", "umfang": "website",
                                              "quelle_url": "https://commons.wikimedia.org/wiki/File:A.jpg",
                                              "alt": "Ein Bild mit Motiv"}, None, titel="T")
    assert any("Urheber fehlt" in f for f in fehler)
    felder, fehler = lizenz.formular_pruefen({"herkunft": "commons", "lizenz": "cc-by-sa", "version": "4.0",
                                              "rechteinhaber": "Max Muster", "urheber": "Max Muster",
                                              "umfang": "website", "quelle_url": "https://commons.wikimedia.org/wiki/File:A.jpg",
                                              "alt": "Ein Bild mit Motiv"}, None, titel="T")
    assert fehler == [] and felder["lizenz_kuerzel"] == "cc-by-sa-4.0"
    assert felder["lizenz_url"] == "https://creativecommons.org/licenses/by-sa/4.0/"
    assert felder["attribution"] == "Foto: Max Muster / Wikimedia Commons, CC BY-SA 4.0, zugeschnitten"
    _, fehler = lizenz.formular_pruefen({"herkunft": "eigen", "lizenz": "eigen", "rechteinhaber": "Tamil.de",
                                         "umfang": "website", "alt": "Ein Bild mit Motiv"},
                                        ("x.exe", b"MZ\x90\x00"), titel="T")
    assert fehler == ["Beleg: nur PDF, PNG oder JPEG"]


def test_ki_und_pool_ohne_freigabe_aus(client, app):
    token = login(client)
    settings = app.extensions["settings"]
    settings.gemini_key = "test-key"
    aufrufe = []
    app.extensions["bild_transport"] = lambda headers, body: aufrufe.append(body) or (500, {})
    assert settings.bild_ki_freigabe is False  # Standard aus (Entscheidung „keine KI-Bilder“)
    for aktion in ("ki", "pool"):
        text = client.post("/entwurf/1/bild", data={"_csrf": token, "aktion": aktion, "bild_thema": "kino-saal",
                                                     "bild_prompt": "Empty hall"}, follow_redirects=True).get_data(as_text=True)
        assert "KI-Bilder und der Bildpool sind aus" in text
    assert aufrufe == []
    assert "Neu generieren" not in client.get("/entwurf/1").get_data(as_text=True)


def _ki_antwort():
    buf = io.BytesIO()
    Image.new("RGB", (1024, 576), (120, 60, 200)).save(buf, "PNG")
    return 200, {"status": "completed", "outputs": [{"type": "image", "data": base64.b64encode(buf.getvalue()).decode()}]}


def test_neu_generieren_reserviert_budget_und_schreibt_agent_usage(client, app):
    token = login(client)
    settings = app.extensions["settings"]
    settings.gemini_key, settings.bild_retry_pause, settings.bild_ki_freigabe = "test-key", 0, True
    aufrufe = []
    app.extensions["bild_transport"] = lambda headers, body: (aufrufe.append(body), _ki_antwort())[1]
    settings.budget_tag_usd = 0.0
    text = client.post("/entwurf/1/bild", data={"_csrf": token, "aktion": "ki", "bild_thema": "kino-saal",
                                                 "bild_prompt": "Empty cinema hall"}, follow_redirects=True).get_data(as_text=True)
    assert "Budget erreicht" in text and aufrufe == []
    settings.budget_tag_usd = 5.0
    client.post("/entwurf/1/bild", data={"_csrf": token, "aktion": "ki", "bild_thema": "kino-saal",
                                         "bild_prompt": "Empty cinema hall"})
    with _store(app) as store:
        usage = [dict(r) for r in store.db.execute("SELECT * FROM agent_usage WHERE rolle = 'bild'")]
        offen = store.db.execute("SELECT COUNT(*) FROM budget_reservierungen").fetchone()[0]
        d = store.get_draft(1)
        asset = repo.asset_fuer_entwurf(store, 1, d["bild_datei"])
    assert len(aufrufe) == 1 and len(usage) == 1 and usage[0]["provider"] == "gemini" and usage[0]["kosten_usd"] > 0
    assert offen == 0  # Reservierung wieder freigegeben
    assert asset["lizenz_kuerzel"] == "ki-symbolbild" and asset["ki"] == 1 and asset["ki_modell"] == settings.bild_modell
    assert asset["prompt_hash"] and asset["umfang"] == "website,social"


# ---- Publisher -------------------------------------------------------------------------------------

def _entwurf_mit_karte(store, settings, *, alt="Grafik mit der Überschrift: Tempelfest"):
    img = branded_card("Tempelfest", "Community", "p1")
    name, _ = save_pair(img, settings.bilder_dir, "p1-x")
    did = store.insert_draft(dict(uid="p1", typ="artikel", titel="Tempelfest", teaser="T", inhalt_html="<p>Text</p>",
                                  kategorie="community", relevanz=8, bild_datei=name, bild_origin="karte",
                                  bild_credit=img.credit, bild_alt=alt, quelle_url="https://q.de/1", quelle_name="Q"))
    return did, name, img


def test_publish_draft_sendet_nicht_ohne_datensatz_und_protokolliert(tmp_path, monkeypatch):
    monkeypatch.setenv("WP_URL", "")
    settings = load_settings()
    settings.data_dir = tmp_path
    wp = FakeWP()
    with Store(settings.db_path) as store:
        did, name, img = _entwurf_mit_karte(store, settings)
        store.set_status(did, "freigeben")
        ergebnis = publisher.publish_approved(settings, store, wp)
        d = store.get_draft(did)
        zeile = store.db.execute("SELECT * FROM editorial_actions WHERE aktion = 'lizenz_fehlt'").fetchone()
    assert wp.posts == [] and wp.medien == [] and ergebnis[0].status == "fehler"
    assert d["status"] == "fehler" and "Lizenz unvollständig: Datensatz" in d["fehler"]
    assert zeile is not None and zeile["kanal"] == "website" and zeile["ausloeser"] == "dienst"


def test_publish_mit_datensatz_sendet_alt_und_lizenz_meta(tmp_path):
    settings = load_settings()
    settings.data_dir = tmp_path
    with Store(settings.db_path) as store:
        did, name, img = _entwurf_mit_karte(store, settings)
        lizenz.anlegen(store, datei=name, daten=img.data, draft_id=did, felder=lizenz.datensatz(img, titel="Tempelfest"))
        row = store.get_draft(did)
        payload = publisher.plugin_payload({**row, **publisher.lizenz_meta(lizenz.asset_fuer(store, row))}, settings,
                                           "publish")
        assert payload["meta"]["bild_lizenz"] == "tamil-grafik" and "bild_quelle_url" not in payload["meta"]
        assert payload["bild"]["alt"] == "Grafik mit der Überschrift: Tempelfest"
        store.update_draft(did, bild_alt="")
        with pytest.raises(lizenz.LizenzFehlt, match="Alt-Text"):
            publisher.publish_draft(store.get_draft(did), settings, FakeWP(), store, status="publish")
        assert publisher.bild_payload({**store.get_draft(did)}, settings)["alt"] == ""  # kein Rückfall auf den Titel


def test_lizenz_meta_nur_http_adressen():
    meta = publisher.lizenz_meta({"lizenz_kuerzel": "cc-by-4.0", "lizenz_url": "https://creativecommons.org/licenses/by/4.0/",
                                  "quelle_url": "javascript:alert(1)"})
    assert meta == {"bild_lizenz": "cc-by-4.0", "bild_lizenz_url": "https://creativecommons.org/licenses/by/4.0/",
                    "bild_quelle_url": ""}
    assert ("bild_lizenz", "bild_lizenz") in publisher.META_FIELDS
    assert publisher.radar_meta({"uid": "x", "bild_lizenz": "cc-by-4.0", "bild_quelle_url": "https://c/x"}) == \
        {"radar_uid": "x", "bild_lizenz": "cc-by-4.0", "bild_quelle_url": "https://c/x"}


# ---- Bildketten (L1, L6, L11) ----------------------------------------------------------------------

def test_v1_kette_ohne_freigabe_kein_ki_und_kein_pool(tmp_path, monkeypatch):
    from news_radar import bilder

    monkeypatch.setenv("BILD_KI_FREIGABE", "")
    settings = load_settings()
    settings.data_dir = tmp_path
    settings.gemini_key = "test"
    pool = bilder.BildPool(tmp_path / "pool")
    pool.add("kino-saal", branded_card("x", "Kino", "x"), "prompt")
    aufrufe = []
    bild = bilder.beitragsbild(settings, titel="Film", kategorie="kino", kategorie_label="Kino", slug="s",
                               bild_prompt="Empty hall", bild_thema="kino-saal",
                               transport=lambda h, b: aufrufe.append(b) or _ki_antwort(), pool=pool)
    assert bild.origin == "karte" and aufrufe == [] and pool.status()["kino-saal"]["genutzt"] == 0


def test_stock_datensatz_mit_fotoseite_und_umfang(monkeypatch):
    img = images.FeaturedImage(b"x", "s.jpg", "image/jpeg", "Foto: Ana / Pexels", "pexels", urheber="Ana",
                               quelle_url="https://www.pexels.com/photo/1/", bild_url="https://images.pexels.com/1.jpg")
    d = lizenz.datensatz(img)
    assert d["herkunft"] == "stock" and d["lizenz_kuerzel"] == "pexels" and d["umfang"] == "website,social"
    assert d["lizenz_url"] == "https://www.pexels.com/license/" and d["urheber"] == "Ana"
    assert lizenz.fehlend({**d, "datei": "s.jpg", "sha256": "ab", "ki": 0}) == []
    upload = lizenz.datensatz(images.FeaturedImage(b"x", "u.jpg", "image/jpeg", "", "upload"))
    assert upload["herkunft"] == "upload" and "lizenz_kuerzel" not in upload  # nichts erfunden


# ---- Nachführung -----------------------------------------------------------------------------------

def test_nachfuehrung_ergaenzt_nur_vollstaendige_angaben(tmp_path):
    from news_radar.bildvorschlag import adress_hash

    settings = load_settings()
    settings.data_dir = tmp_path
    with Store(settings.db_path) as store:
        def entwurf(uid, origin, quelle_bild=""):
            name, _ = save_pair(branded_card(uid, "Community", uid), settings.bilder_dir, f"{uid}-x")
            did = store.insert_draft(dict(uid=uid, typ="artikel", titel=uid, teaser="T", inhalt_html="<p>T</p>",
                                          kategorie="community", relevanz=8, bild_datei=name, bild_origin=origin,
                                          bild_alt="Gopuram vor Himmel", quelle_bild=quelle_bild))
            return did, name

        def alt_asset(name, did, **f):
            werte = {"datei": name, "herkunft": f.pop("herkunft"), "draft_id": did, "erstellt": "2026-11-12T10:00:00+00:00",
                     "sha256": "", **f}
            spalten = ", ".join(werte)
            return store.db.execute(f"INSERT INTO assets ({spalten}) VALUES ({','.join('?' for _ in werte)})",
                                    list(werte.values())).lastrowid

        c_id, c_name = entwurf("commons", "commons")
        alt_asset(c_name, c_id, herkunft="commons", rechteinhaber="Max Muster",
                  lizenz="CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/)",
                  umfang="Online-Veröffentlichung auf tamil.de; Zuschnitt auf das Seitenformat",
                  attribution="Foto: Max Muster / Wikimedia Commons, CC BY-SA 4.0",
                  quelle_url="https://commons.wikimedia.org/wiki/File:Hindu_Tempel_Hamm.jpg")
        bild = "https://tempel-hamm.de/wp-content/uploads/fest.jpg"
        r_id, r_name = entwurf("register", "quelle", quelle_bild=bild)
        r_asset = alt_asset(r_name, r_id, herkunft="quelle", rechteinhaber="Tempel Hamm", lizenz="Material der Quelle",
                            umfang="Online-Veröffentlichung auf tamil.de", attribution="Foto: Tempel Hamm",
                            quelle_url="https://tempel-hamm.de/fest")
        store.db.execute("INSERT INTO editorial_actions (ts, wer, aktion, draft_id, notiz) VALUES (?,?,?,?,?)",
                         ("2026-11-12T10:00:00+00:00", "agent", "bild", r_id,
                          f"Bild mit Nachweis (quelle): Asset {r_asset}, tempel-hamm.de, #{adress_hash(bild)}"))
        x_id, x_name = entwurf("register-ohne", "quelle", quelle_bild="https://tempel-hamm.de/anderes.jpg")
        x_asset = alt_asset(x_name, x_id, herkunft="quelle", rechteinhaber="Tempel Hamm", lizenz="Material",
                            umfang="x", attribution="Foto: Tempel Hamm", quelle_url="https://tempel-hamm.de/fest")
        store.db.execute("INSERT INTO editorial_actions (ts, wer, aktion, draft_id, notiz) VALUES (?,?,?,?,?)",
                         ("2026-11-12T10:00:00+00:00", "agent", "bild", x_id,
                          f"Bild mit Nachweis (quelle): Asset {x_asset}, tempel-hamm.de, #{adress_hash(bild)}"))
        k_id, k_name = entwurf("karte", "karte")
        u_id, u_name = entwurf("upload", "upload")
        alt_asset(u_name, u_id, herkunft="upload", rechteinhaber="Luis", lizenz="", attribution="Foto: Tamil.de")
        store.db.commit()

        z = lizenz.nachfuehren(store, settings)
        assert z == {"ergaenzt": 2, "karte": 1, "offen": 2, "schon": 0}
        c = repo.asset_fuer_entwurf(store, c_id, c_name)
        assert c["lizenz_kuerzel"] == "cc-by-sa-4.0" and c["urheber"] == "Max Muster" and lizenz.fehlend(c) == []
        assert c["umfang"] == "website,social,print" and c["bild_url"].endswith("Special:FilePath/Hindu_Tempel_Hamm.jpg")
        r = repo.asset_fuer_entwurf(store, r_id, r_name)
        assert r["lizenz_kuerzel"] == "presse-redaktionell" and r["umfang"] == "website" and r["bild_url"] == bild
        x = repo.asset_fuer_entwurf(store, x_id, x_name)
        assert not x["lizenz_kuerzel"] and not x["bild_url"]  # Bildadresse nicht belegt: offen
        k = repo.asset_fuer_entwurf(store, k_id, k_name)
        assert k["lizenz_kuerzel"] == "tamil-grafik" and lizenz.fehlend(k) == []
        u = repo.asset_fuer_entwurf(store, u_id, u_name)
        assert not u["lizenz_kuerzel"]  # eigener Upload ohne Angaben: nichts erfunden
        assert lizenz.nachfuehren(store, settings)["schon"] == 3  # zweiter Lauf ändert nichts mehr


def test_asset_eines_anderen_entwurfs_zaehlt_nicht(tmp_path):
    with Store(tmp_path / "r.sqlite") as store:
        repo.asset_anlegen(store, datei="a.jpg", herkunft="karte", draft_id=7, lizenz_kuerzel="tamil-grafik")
        assert repo.asset_fuer_entwurf(store, 8, "a.jpg") is None
        assert repo.asset_fuer_entwurf(store, 7, "a.jpg")["lizenz_kuerzel"] == "tamil-grafik"
        with pytest.raises(TypeError):
            repo.asset_anlegen(store, datei="b.jpg", herkunft="karte", erfunden="x")
        with pytest.raises(sqlite3.Error):
            store.db.execute("INSERT INTO assets (herkunft, erstellt) VALUES ('x', 'y')")  # datei NOT NULL


def test_nachfuehrung_beim_dienststart_protokolliert_nur_wenn_etwas_ergaenzt(tmp_path):
    settings = load_settings()
    settings.data_dir = tmp_path
    with Store(settings.db_path) as store:
        name, _ = save_pair(branded_card("Karte", "Community", "k"), settings.bilder_dir, "k-x")
        store.insert_draft(dict(uid="k", typ="artikel", titel="Karte", teaser="T", inhalt_html="<p>T</p>",
                                kategorie="community", relevanz=8, bild_datei=name, bild_origin="karte",
                                bild_alt="Grafik mit der Überschrift: Karte"))
        z = lizenz.nachfuehren_beim_start(store, settings)
        assert z["karte"] == 1
        zeilen = [dict(r) for r in store.db.execute("SELECT * FROM editorial_actions WHERE aktion = 'lizenz_nachfuehrung'")]
        assert len(zeilen) == 1 and zeilen[0]["ausloeser"] == "dienst" and "1 Bildkarten" in zeilen[0]["notiz"]
        lizenz.nachfuehren_beim_start(store, settings)  # nichts mehr zu tun: keine weitere Zeile
        assert store.db.execute("SELECT COUNT(*) FROM editorial_actions WHERE aktion = 'lizenz_nachfuehrung'").fetchone()[0] == 1
