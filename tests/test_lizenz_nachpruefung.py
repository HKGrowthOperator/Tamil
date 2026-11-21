"""Befunde der unabhängigen Prüfung zur Lizenzpflicht (P3): Alt-Text, Belegdatei, Status „fehler“, Rechte, CSRF,
Belegdatei über 5 MB, Gate auf allen Freigabe- und Sendewegen."""

import io

import pytest

from stand_hilfe import stand_von
from test_lizenz import FakeWP, _png, _store, app, client, login  # noqa: F401 – Fixtures

from news_radar import lizenz
from news_radar.workflow import repo


def test_stock_rueckfall_karte_setzt_karten_alt_und_upload_uebernimmt_ihn_nicht(client, app):
    token = login(client)
    client.post("/entwurf/1/bild", data={"_csrf": token, "aktion": "stock", "suchbegriff": "temple"})  # ohne Schlüssel
    with _store(app) as store:
        d = store.get_draft(1)
    assert d["bild_origin"] == "karte" and d["bild_alt"] == "Grafik mit der Überschrift: Tempelfest in Hamm"
    client.post("/entwurf/1/bild", data={"_csrf": token, "aktion": "upload", "datei": (_png(), "foto.png")},
                content_type="multipart/form-data")
    with _store(app) as store:
        d = store.get_draft(1)
    assert d["bild_origin"] == "upload" and not d["bild_alt"]  # der Karten-Alt-Text beschreibt das Foto nicht
    formular = client.get("/entwurf/1").get_data(as_text=True).split('id="lizenz"', 1)[1]
    assert "Grafik mit der Überschrift" not in formular


GUELTIG = {"herkunft": "dritte", "lizenz": "nutzungsrecht", "urheber": "Foto Kumar", "rechteinhaber": "Foto Kumar",
           "umfang": ["website"], "quelle_url": "https://tempel-hamm.de/fest", "alt": "Gopuram des Tempels mit Girlanden",
           "beleg": "Mail vom 12.11.2026"}


def _upload(client, token):
    client.post("/entwurf/1/bild", data={"_csrf": token, "aktion": "upload", "datei": (_png(), "foto.png")},
                content_type="multipart/form-data")


def test_belegdatei_erst_nach_erfolgreichem_speichern(client, app, monkeypatch):
    from news_radar.store import Store

    token = login(client)
    _upload(client, token)
    belege = app.extensions["settings"].data_dir / "belege"
    # Entwurf hat sich inzwischen geändert: nichts gespeichert, keine Belegdatei
    monkeypatch.setattr(Store, "update_draft", lambda self, *a, **kw: 0)
    text = client.post("/entwurf/1/lizenz", data={"_csrf": token, **GUELTIG,
                                                   "beleg_datei": (io.BytesIO(b"%PDF-1.4 a"), "a.pdf")},
                       content_type="multipart/form-data", follow_redirects=True).get_data(as_text=True)
    assert "inzwischen geändert" in text and not list(belege.glob("*"))
    monkeypatch.undo()

    # Datensatz lässt sich nicht schreiben: die gerade abgelegte Belegdatei wird wieder entfernt
    def kaputt(*a, **kw):
        raise RuntimeError("Datenbank belegt")

    monkeypatch.setattr(lizenz, "anlegen", kaputt)
    with pytest.raises(RuntimeError):
        client.post("/entwurf/1/lizenz", data={"_csrf": token, **GUELTIG,
                                               "beleg_datei": (io.BytesIO(b"%PDF-1.4 b"), "b.pdf")},
                    content_type="multipart/form-data")
    assert not list(belege.glob("*"))


def test_migration_8_auf_9_mit_vorhandenen_social_tabellen(tmp_path, monkeypatch):
    from news_radar.store import Store
    from news_radar.workflow import schema

    pfad = tmp_path / "radar.sqlite"
    monkeypatch.setattr(schema, "MIGRATIONS", {k: v for k, v in schema.MIGRATIONS.items() if k <= 8})
    with Store(pfad) as store:
        assert store.db.execute("PRAGMA user_version").fetchone()[0] == 8
        store.db.execute("INSERT INTO social_beitraege (wp_post_id, quelle_typ, kanal, status, regel_fassung, "
                         "erkannt_at, aktualisiert) VALUES (7, 'beitrag', 'instagram', 'karenz', '1', 'x', 'x')")
        store.db.execute("INSERT INTO assets (datei, herkunft, umfang, erstellt) VALUES ('a.jpg', 'karte', "
                         "'website,social', 'x')")
        store.db.commit()
    monkeypatch.undo()
    with Store(pfad) as store:
        assert store.db.execute("PRAGMA user_version").fetchone()[0] == schema.LATEST >= 9
        assert store.db.execute("SELECT kanal, status FROM social_beitraege").fetchone()[:] == ("instagram", "karenz")
        a = dict(store.db.execute("SELECT * FROM assets").fetchone())
        assert a["umfang"] == "website,social" and "lizenz_kuerzel" in a and a["lizenz_kuerzel"] is None


def test_lizenz_eintragen_nur_mit_recht_und_csrf(client, app):
    with _store(app) as store:
        repo.nutzer_anlegen(store, "lena", "lena-passwort-1", "leser")
    token = login(client)
    assert client.post("/entwurf/1/lizenz", data=GUELTIG).status_code == 400  # ohne CSRF
    leser = app.test_client()
    leser.get("/login")
    with leser.session_transaction() as s:
        t = s["csrf"]
    assert leser.post("/login", data={"user": "lena", "password": "lena-passwort-1", "_csrf": t}).status_code == 302
    assert leser.post("/entwurf/1/lizenz", data={"_csrf": t, **GUELTIG}).status_code == 403
    with _store(app) as store:
        assert store.db.execute("SELECT COUNT(*) FROM editorial_actions WHERE aktion = 'lizenz'").fetchone()[0] == 0
    assert token


def test_beleg_ueber_5_mb_abgelehnt(client, app):
    token = login(client)
    _upload(client, token)
    gross = io.BytesIO(b"%PDF-1.4 " + b"0" * (lizenz.BELEG_MAX + 10))
    text = client.post("/entwurf/1/lizenz", data={"_csrf": token, **GUELTIG, "beleg_datei": (gross, "gross.pdf")},
                       content_type="multipart/form-data", follow_redirects=True).get_data(as_text=True)
    assert "Beleg zu groß" in text
    belege = app.extensions["settings"].data_dir / "belege"
    assert not belege.exists() or not list(belege.glob("*"))
    with _store(app) as store:
        assert not store.db.execute("SELECT 1 FROM assets WHERE lizenz_kuerzel = 'nutzungsrecht'").fetchone()


def test_gate_bei_erneut_und_direkt_posten_mit_wordpress(client, app):
    token = login(client)
    wp = app.extensions["wordpress"] = FakeWP()
    app.extensions["settings"].wp_url, app.extensions["settings"].wp_user = "https://www.tamil.de", "radar"
    app.extensions["settings"].wp_app_password = "x"
    with _store(app) as store:
        store._write("UPDATE drafts SET status = 'fehler', fehler = 'WordPress 500' WHERE id = 1")
    text = client.post("/entwurf/1/status", data={"_csrf": token, "aktion": "erneut", "stand": stand_von(client, 1)},
                       follow_redirects=True).get_data(as_text=True)
    assert "Lizenz fehlt: Datensatz" in text
    for route in ("veroeffentlichen", "wp-entwurf"):
        text = client.post(f"/entwurf/2/{route}", data={"_csrf": token, "stand": stand_von(client, 2)},
                           follow_redirects=True).get_data(as_text=True)
        assert "Lizenz fehlt" in text
    assert wp.posts == [] and wp.medien == []
    with _store(app) as store:
        assert store.get_draft(1)["status"] == "fehler" and store.get_draft(2)["status"] == "neu"


def test_agent_import_legt_datensatz_an_und_gate_greift(tmp_path, monkeypatch):
    import json

    from news_radar import agent
    from news_radar.config import load_settings
    from news_radar.store import Store

    for var in ("UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "GEMINI_API_KEY", "BILD_POOL_DIR"):
        monkeypatch.setenv(var, "")
    settings = load_settings()
    settings.data_dir = tmp_path
    with Store(settings.db_path) as store:
        did = store.insert_draft(dict(uid="u1", typ="artikel", titel="Roh", teaser="T", inhalt_html="<p>Roh</p>",
                                      kategorie="community", relevanz=8, bild_datei="", bild_origin="karte"))
        datei = tmp_path / "e.json"
        datei.write_text(json.dumps({"ergebnisse": [{
            "id": did, "relevanz": 9, "begruendung": "x", "kategorie": "community", "typ": "artikel",
            "dach_bezug": True, "ort": "Hamm", "titel": "Tempelfest in Hamm", "teaser": "Ein Fest für die Community in Hamm.",
            "inhalt_html": "<p>Der Tempel in Hamm-Uentrop lädt am Wochenende zum Fest ein, hunderte Gäste werden erwartet.</p><p>Der Verein bittet um Anmeldung, Parkplätze sind knapp.</p>",
            "schlagworte": ["Hamm"], "seo_titel": "Tempelfest in Hamm", "meta_beschreibung": "Tempelfest in Hamm mit Programm und Anmeldung",
            "bild_suchbegriff": "temple", "bild_alt": "Tempel in Hamm", "bild_thema": "tempelfest", "bild_prompt": "",
            "event_datum": "", "event_ort": "", "ticket_url": ""}]}), encoding="utf-8")
        stats = agent.import_results(store, settings, datei, von="agent")
        assert stats["uebernommen"] == 1, stats
        d = store.get_draft(did)
        asset = lizenz.asset_fuer(store, d)
        assert asset["lizenz_kuerzel"] == "tamil-grafik" and asset["geprueft_von"] == "agent:agent"
        assert d["bild_alt"] == "Grafik mit der Überschrift: Tempelfest in Hamm"
        assert lizenz.sperre(store, d, settings) == ""
        store._write("DELETE FROM assets WHERE draft_id = ?", (did,))  # ohne Datensatz: gesperrt
        assert lizenz.sperre(store, store.get_draft(did), settings) == "Lizenz fehlt: Datensatz"


def test_dienst_startet_auch_wenn_die_nachfuehrung_scheitert(tmp_path, monkeypatch, caplog):
    import logging

    from news_radar import dienst
    from news_radar.config import load_settings

    settings = load_settings()
    settings.data_dir = tmp_path

    class Leer:
        langlaeufer, store, stop = [], None, False

        def laufen(self):
            return None

    def kaputt(store, settings):
        raise RuntimeError("Datenbank belegt")

    monkeypatch.setattr(dienst, "rechte_abgeben", lambda data_dir: None)
    monkeypatch.setattr(dienst, "aufbauen", lambda s, port: Leer())
    monkeypatch.setattr(lizenz, "nachfuehren_beim_start", kaputt)
    with caplog.at_level(logging.ERROR):
        assert dienst.main(settings) == 0
    assert "Lizenz-Nachführung fehlgeschlagen" in caplog.text


def test_lizenz_eintragen_im_status_fehler(client, app):
    token = login(client)
    _upload(client, token)
    with _store(app) as store:
        store._write("UPDATE drafts SET status = 'fehler', fehler = 'Lizenz unvollständig: Datensatz' WHERE id = 1")
    assert 'action="/entwurf/1/lizenz"' in client.get("/entwurf/1").get_data(as_text=True)
    client.post("/entwurf/1/lizenz", data={"_csrf": token, **GUELTIG})
    with _store(app) as store:
        d = store.get_draft(1)
        assert d["status"] == "fehler" and lizenz.sperre(store, d, app.extensions["settings"]) == ""
    client.post("/entwurf/1/status", data={"_csrf": token, "aktion": "erneut", "stand": stand_von(client, 1)})
    with _store(app) as store:
        assert store.get_draft(1)["status"] == "freigegeben"
