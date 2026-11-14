"""tools/coolify.py: Geheimnisse erscheinen nie in Ausgaben."""

import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("coolify", Path(__file__).resolve().parents[1] / "tools" / "coolify.py")
coolify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(coolify)


def test_schwaerzen_versteckt_werte_rekursiv():
    roh = {"key": "WEB_PASSWORD", "value": "geheim1", "real_value": "geheim1", "is_buildtime": False,
           "nested": [{"token": "abc", "name": "x"}], "fqdn": "https://tamil.example"}
    s = coolify.schwaerzen(roh)
    assert "geheim1" not in str(s) and "abc" not in str(s)
    assert s["fqdn"] == "https://tamil.example" and s["is_buildtime"] is False and s["nested"][0]["name"] == "x"


def test_wert_aufloesen(tmp_path):
    a, b = coolify.wert_aufloesen("@zufall"), coolify.wert_aufloesen("@zufall")
    assert a != b and len(a) >= 40
    f = tmp_path / "pw"
    f.write_text("aus-datei\n")
    assert coolify.wert_aufloesen(f"@datei:{f}") == "aus-datei"
    assert coolify.wert_aufloesen("v2") == "v2"


def test_env_setzen_schickt_runtime_und_zeigt_keine_werte(monkeypatch, capsys, tmp_path):
    gesendet = {}
    monkeypatch.setattr(coolify, "anfrage", lambda m, p, d=None, timeout=60: gesendet.update(m=m, p=p, d=d))
    f = tmp_path / "pw"
    f.write_text("sehr-geheim")
    coolify.main(["env-setzen", "abc", "RADAR_WORKFLOW=v2", f"WP_APP_PASSWORD=@datei:{f}", "WEB_SECRET=@zufall"])
    out = capsys.readouterr().out
    assert gesendet["m"] == "PATCH" and gesendet["p"] == "/applications/abc/envs/bulk"
    daten = gesendet["d"]["data"]
    assert [d["key"] for d in daten] == ["RADAR_WORKFLOW", "WP_APP_PASSWORD", "WEB_SECRET"]
    assert all(d["is_buildtime"] is False and d["is_runtime"] and d["is_literal"] is False for d in daten)
    assert daten[1]["value"] == "sehr-geheim"
    assert "sehr-geheim" not in out and daten[2]["value"] not in out and "WEB_SECRET" in out


def test_ohne_token_bricht_ab(monkeypatch):
    monkeypatch.delenv("COOLIFY_TOKEN", raising=False)
    with pytest.raises(SystemExit) as e:
        coolify.anfrage("GET", "/applications")
    assert "COOLIFY_TOKEN fehlt" in str(e.value)
