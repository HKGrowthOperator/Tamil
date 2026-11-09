"""Export der Entwürfe für den Prototyp: JSON-Form, Quellbild vor Bildkarte, Statistik."""

import io
import json

from PIL import Image

from news_radar.export import export_drafts, quellbild
from news_radar.images import branded_card, save_pair
from news_radar.store import Store


def jpeg(width: int, height: int) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), (180, 20, 40)).save(buf, "JPEG")
    return buf.getvalue()


def row(uid, **kw):
    base = dict(uid=uid, titel=f"Titel {uid}", teaser="t", inhalt_html="<p>x</p>", kategorie="kino", relevanz=8, dach_bezug=True,
                ort="Bremen", quelle_name="WA Hamm (via Google News)", quelle_url=f"https://q/{uid}", schlagworte=[], bild_origin="karte",
                bild_credit="Grafik: Tamil.de", bild_alt="alt")
    base.update(kw)
    return base


def test_export_prefers_source_image_and_falls_back_to_card(tmp_path):
    bilder_quelle = tmp_path / "bilder"
    with Store(tmp_path / "r.sqlite") as store:
        name, _ = save_pair(branded_card("Titel", "Kino", "a"), bilder_quelle, "a")
        store.insert_draft(row("a", quelle_datum="2026-10-17T10:00", bild_datei=name))
        store.insert_draft(row("b", quelle_datum="2026-10-18T10:00", bild_datei=name, quelle_bild="https://img/b.jpg"))
        store.insert_draft(row("c", quelle_datum="2026-10-16T10:00", bild_datei=name, quelle_bild="https://img/klein.png"))
        fetched = []

        def fetch(url):
            fetched.append(url)
            return jpeg(200, 100) if "klein" in url else jpeg(1600, 900)  # klein → Bildkarte

        stats = export_drafts(store, tmp_path / "radar.json", tmp_path / "out", quellbilder=True, bilder_quelle=bilder_quelle,
                              fetch_og=lambda url: "https://img/og.jpg" if url.endswith("/a") else "", fetch=fetch)
    assert stats == {"entwuerfe": 3, "quellbilder": 2, "bildkarten": 1, "ohne_bild": 0}
    assert fetched == ["https://img/b.jpg", "https://img/og.jpg", "https://img/klein.png"]
    data = json.loads((tmp_path / "radar.json").read_text(encoding="utf-8"))
    b, a, c = data["entwuerfe"]
    assert b["titel"] == "Titel b" and b["bild"] == {"datei": "r2.jpg", "origin": "quelle", "credit": "Foto: WA Hamm", "alt": "alt", "w": 1200, "h": 675, "balken": False}
    assert a["bild"]["origin"] == "quelle" and c["bild"]["origin"] == "karte" and c["bild"]["datei"] == "r3.jpg"
    assert (tmp_path / "out" / "r2.jpg").exists() and Image.open(tmp_path / "out" / "r2.jpg").size == (1200, 675)
    assert "original_json" not in b and data["quellen"] == [] and data["lauf"] is None


def test_quellbild_rejects_garbage(tmp_path):
    assert quellbild("https://x", tmp_path / "x.jpg", lambda url: b"not an image") is None
    assert quellbild("https://x", tmp_path / "x.jpg", lambda url: None) is None
