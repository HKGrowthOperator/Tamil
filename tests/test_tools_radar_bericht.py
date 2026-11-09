"""tools/radar_bericht.py: --json liefert reines JSON auf der Standardausgabe."""

import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "radar_bericht", Path(__file__).resolve().parents[1] / "tools" / "radar_bericht.py")
radar_bericht = importlib.util.module_from_spec(spec)
spec.loader.exec_module(radar_bericht)


def _falsches_holen(url, token=None):
    if url.endswith("/gesund"):
        return {"ok": True, "offen": 0}
    assert token == "lese-geheim"
    return {"tage": 7, "storys": [{"id": 1, "status": "fertig"}], "entwuerfe": [], "budget": {}}


def test_json_ausgabe_ist_direkt_einlesbar(monkeypatch, capsys, tmp_path):
    """Fund 09.11.: Vor dem JSON stand die Zeile „Gesundheit: …“, die Ausgabe ließ sich nicht einlesen."""
    monkeypatch.setattr(radar_bericht, "holen", _falsches_holen)
    datei = tmp_path / "token"
    datei.write_text("lese-geheim\n")
    assert radar_bericht.main(["--url", "https://radar.example", "--token-datei", str(datei), "--json"]) == 0
    aus = capsys.readouterr()
    assert json.loads(aus.out)["storys"][0]["status"] == "fertig"
    assert "Gesundheit" in aus.err
    assert "lese-geheim" not in aus.out + aus.err


def test_uebersicht_zeigt_gesundheit_weiter_oben(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(radar_bericht, "holen", _falsches_holen)
    datei = tmp_path / "token"
    datei.write_text("lese-geheim\n")
    assert radar_bericht.main(["--url", "https://radar.example", "--token-datei", str(datei)]) == 0
    aus = capsys.readouterr()
    assert aus.out.startswith("Gesundheit:") and "Storys (7 Tage): 1" in aus.out
