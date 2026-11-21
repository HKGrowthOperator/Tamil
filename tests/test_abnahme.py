"""Abnahme: alle Szenarien mit FakeClaude müssen bestehen, alle Kriterien K1–K9 erfüllt sein."""

import pytest

from news_radar import abnahme
from news_radar.abnahme.szenarien import SZENARIEN
from news_radar.config import load_settings


@pytest.fixture(scope="module")
def ergebnisse(tmp_path_factory):
    basis = load_settings()
    return abnahme.alle(basis=basis, ordner=tmp_path_factory.mktemp("abnahme"))


def test_es_gibt_mindestens_50_szenarien():
    assert len(SZENARIEN) >= 50 and len({s.nr for s in SZENARIEN}) == len(SZENARIEN)


@pytest.mark.parametrize("nr", [s.nr for s in SZENARIEN])
def test_szenario(ergebnisse, nr):
    e = next(e for e in ergebnisse if e.szenario.nr == nr)
    assert e.ok, f"{e.szenario.name}: {e.abweichungen or [k for k, v in e.kriterien.items() if not v]}\n{e.fehler}"


def test_bericht_nennt_alle_kriterien(ergebnisse):
    text = abnahme.bericht(ergebnisse)
    assert f"**{len(ergebnisse)} von {len(ergebnisse)} Szenarien bestanden.**" in text
    for k in ("K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8", "K9"):
        assert k in text
