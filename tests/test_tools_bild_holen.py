"""tools/bild_holen.py: Beitragsbild der alten Seite holen und verkleinern, ohne Netz getestet."""

import importlib.util
import io
import json
from pathlib import Path

import pytest
from PIL import Image

spec = importlib.util.spec_from_file_location(
    "bild_holen", Path(__file__).resolve().parents[1] / "tools" / "bild_holen.py")
bild_holen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bild_holen)


def _jpeg(breite, hoehe):
    puffer = io.BytesIO()
    Image.new("RGB", (breite, hoehe), (120, 60, 40)).save(puffer, "JPEG")
    return puffer.getvalue()


def _falsches_netz(bilder):
    def json_holen(url):
        nr = int(url.split("/posts/")[1].split("?")[0])
        return {"id": nr, "_embedded": {"wp:featuredmedia": [{"source_url": f"https://www.tamil.de/wp-content/uploads/b{nr}.jpg"}]}}

    def bytes_holen(url):
        return bilder[url.rsplit("/b", 1)[1].split(".")[0]]

    return json_holen, bytes_holen


def test_grosses_bild_wird_verkleinert_kleines_nie_vergroessert(tmp_path):
    json_holen, bytes_holen = _falsches_netz({"1": _jpeg(2190, 1150), "2": _jpeg(678, 352)})
    ergebnis = bild_holen.holen([1, 2], tmp_path, breite=1600, json_holen=json_holen, bytes_holen=bytes_holen)
    assert ergebnis["1"]["w"] == 1600 and ergebnis["1"]["h"] == 840 and ergebnis["1"]["orig_w"] == 2190
    assert ergebnis["2"]["w"] == 678 and ergebnis["2"]["h"] == 352
    with Image.open(tmp_path / "p1.jpg") as bild:
        assert bild.size == (1600, 840)
    gespeichert = json.loads((tmp_path / "bilder.json").read_text(encoding="utf-8"))
    assert gespeichert["2"]["quelle"].startswith("https://www.tamil.de/")


def test_zweiter_lauf_ergaenzt_bilder_json(tmp_path):
    json_holen, bytes_holen = _falsches_netz({"1": _jpeg(800, 400), "2": _jpeg(900, 450)})
    bild_holen.holen([1], tmp_path, breite=1600, json_holen=json_holen, bytes_holen=bytes_holen)
    bild_holen.holen([2], tmp_path, breite=600, json_holen=json_holen, bytes_holen=bytes_holen)
    gespeichert = json.loads((tmp_path / "bilder.json").read_text(encoding="utf-8"))
    assert set(gespeichert) == {"1", "2"} and gespeichert["2"]["w"] == 600


def test_fremde_adresse_wird_abgelehnt(tmp_path):
    def json_holen(url):
        return {"_embedded": {"wp:featuredmedia": [{"source_url": "https://boese.example/x.jpg"}]}}

    with pytest.raises(ValueError):
        bild_holen.holen([7], tmp_path, breite=800, json_holen=json_holen, bytes_holen=lambda url: b"")


def test_beitrag_ohne_bild_wird_gemeldet(tmp_path):
    ergebnis = bild_holen.holen([9], tmp_path, breite=800, json_holen=lambda url: {"_embedded": {}},
                                bytes_holen=lambda url: b"")
    assert ergebnis == {} and not (tmp_path / "p9.jpg").exists()
