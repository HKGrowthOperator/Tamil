"""Befunde der unabhängigen Prüfung zur Lizenzpflicht (P3): Alt-Text, Belegdatei, Status „fehler“, Rechte, CSRF,
Belegdatei über 5 MB, Gate auf allen Freigabe- und Sendewegen."""

import io

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
