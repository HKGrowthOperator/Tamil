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


def test_ohne_lese_token_nimmt_es_das_agent_token(monkeypatch, capsys):
    """/api/bericht nimmt auch das Agent-Token: die Routine kommt mit RADAR_AGENT_TOKEN allein aus."""
    gesehen = []

    def holen(url, token=None):
        gesehen.append(token)
        return {"ok": True} if url.endswith("/gesund") else {"tage": 7, "storys": [], "entwuerfe": [], "budget": {}}

    monkeypatch.setattr(radar_bericht, "holen", holen)
    monkeypatch.delenv("RADAR_LESE_TOKEN", raising=False)
    monkeypatch.setenv("RADAR_AGENT_TOKEN", "agent-geheim")
    assert radar_bericht.main(["--url", "https://radar.example", "--json"]) == 0
    aus = capsys.readouterr()
    assert "agent-geheim" in gesehen and "agent-geheim" not in aus.out + aus.err
    monkeypatch.setenv("RADAR_LESE_TOKEN", "lese-geheim")  # beide gesetzt: das Lese-Token geht vor
    gesehen.clear()
    assert radar_bericht.main(["--url", "https://radar.example", "--json"]) == 0
    assert "lese-geheim" in gesehen and "agent-geheim" not in gesehen
    monkeypatch.delenv("RADAR_LESE_TOKEN")
    monkeypatch.delenv("RADAR_AGENT_TOKEN")
    assert radar_bericht.main(["--url", "https://radar.example"]) == 2


def test_token_nur_ueber_https(monkeypatch, capsys):
    """Das Token (egal welches) geht nie unverschlüsselt übers Netz; nur lokal ist http erlaubt."""
    gesehen = []

    def holen(url, token=None):
        gesehen.append(url)
        return {"ok": True} if url.endswith("/gesund") else {"tage": 7, "storys": [], "entwuerfe": [], "budget": {}}

    monkeypatch.setattr(radar_bericht, "holen", holen)
    monkeypatch.setenv("RADAR_AGENT_TOKEN", "agent-geheim")
    for url in ("http://radar.example", "http://tamil.hk-growthoperator.de", "ftp://radar.example",
                "http://localhost.radar.example", "http://127.0.0.1.radar.example"):
        assert radar_bericht.main(["--url", url]) == 2, url
    assert gesehen == [] and "https" in capsys.readouterr().err
    for url in ("http://localhost:8787", "http://127.0.0.1:8787", "https://radar.example"):
        assert radar_bericht.main(["--url", url, "--json"]) == 0, url
