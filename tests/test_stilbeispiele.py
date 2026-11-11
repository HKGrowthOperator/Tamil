"""Stilbeispiele aus dem Altbestand der alten tamil.de (Fixture: drei echte Beiträge aus dem REST-Export)."""

import json
from pathlib import Path

import pytest

from news_radar import stilbeispiele
from news_radar.agents import schreiben

EXPORT = Path(__file__).parent / "fixtures" / "alt_export"


def test_bereinigen_entfernt_quellenzeile_teilen_und_links():
    posts, _ = stilbeispiele.laden_export(EXPORT)
    vithya = next(p for p in posts if p["id"] == 9118)
    text = stilbeispiele.bereinigen(vithya["content"]["rendered"])
    assert text.startswith("Es braucht Mut")
    assert "Quelle:" not in text and "Share on" not in text and "WhatsApp" not in text and "http" not in text
    assert "\n\n" in text  # Absätze bleiben getrennt


def test_auswahl_ist_wiederholbar_und_prueft_jeden_beitrag():
    posts, kategorien = stilbeispiele.laden_export(EXPORT)
    auswahl = {9118: "portraet", 4711: "kueche"}
    a = stilbeispiele.auswaehlen(posts, kategorien, auswahl)
    assert a == stilbeispiele.auswaehlen(posts, kategorien, auswahl)
    assert [(b["id"], b["art"]) for b in a] == [(9118, "portraet"), (4711, "kueche")]
    assert a[0]["rubrik"] == "News" and a[0]["woerter"] >= 300 and a[1]["rubrik"] == "Entertainment"
    with pytest.raises(ValueError, match="9597: nur"):  # Payasam: 44 Wörter
        stilbeispiele.auswaehlen(posts, kategorien, {9597: "kueche"})
    with pytest.raises(ValueError, match="nicht im Export"):
        stilbeispiele.auswaehlen(posts, kategorien, {1: "nachricht"})
    assert {k["id"] for k in stilbeispiele.kandidaten(posts, kategorien)} == {9118, 4711}


def test_kuerzen_behaelt_einstieg_und_service_am_schluss():
    text = "\n\n".join([f"Absatz {i} " + "x" * 400 for i in range(20)] + ["Tickets: 50 Euro"])
    kurz = stilbeispiele.kuerzen(text, 2000)
    assert len(kurz) <= 2000 and kurz.startswith("Absatz 0") and kurz.endswith("Tickets: 50 Euro") and "[…]" in kurz


def test_gespeicherte_beispiele_decken_alle_arten_ab():
    alle = stilbeispiele.laden()
    assert 16 <= len(alle) <= 20
    assert {b["art"] for b in alle} == set(stilbeispiele.ARTEN)
    assert all(b["woerter"] >= 300 and b["title"] and b["rubrik"] for b in alle)
    assert not any("http" in b["text"] or "@" in b["text"] for b in alle)


@pytest.mark.parametrize("typ,kategorie,art", [
    ("event", "events", "event"), ("kino", "kino", "kino"), ("news", "community", "portraet"),
    ("news", "kueche", "kueche"), ("news", "nachrichten", "nachricht"), ("dossier", "", "nachricht"),
])
def test_passende_beispiele_je_typ(typ, kategorie, art):
    gewaehlt = schreiben.stilbeispiele(typ, kategorie)
    assert len(gewaehlt) == 3 and gewaehlt[0]["art"] == art


def test_system_prompt_nennt_art_und_laenge_der_beispiele(tmp_path, monkeypatch):
    from news_radar.config import load_settings

    settings = load_settings()
    prompt = schreiben.system_prompt(settings, "event", "events")
    erstes = next(b for b in stilbeispiele.laden() if b["art"] == "event")
    assert f"# {erstes['title']} (event, {erstes['woerter']} Wörter)" in prompt


def test_cli_schreibt_auswahl(tmp_path, monkeypatch):
    from news_radar import __main__ as cli

    ziel = tmp_path / "style.json"
    monkeypatch.setattr(cli, "STYLE_FILE", ziel)
    monkeypatch.setattr(stilbeispiele, "AUSWAHL", {9118: "portraet"})
    assert cli.main(["style", "--export", str(EXPORT)]) == 0
    assert [b["id"] for b in json.loads(ziel.read_text(encoding="utf-8"))] == [9118]
