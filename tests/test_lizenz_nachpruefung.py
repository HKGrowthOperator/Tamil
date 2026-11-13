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
