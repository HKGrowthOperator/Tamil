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


def test_bereinigen_entfernt_bildnachweise_agenturen_und_autorenzeilen():
    roh = ("<p>SOLINGEN (red) – Rund 75 Kinder lernen sonntags Tamil.</p>"
           "<p>Von Jürgen Webermann</p><p>MALOLO KESSLER</p>"
           "<p>Er sitzt neu im Stadtparlament. (Bild: Urs Bucher) Er läuft Halbmarathons.</p>"
           "<p>© Nierhoff</p><p>Foto: Max Muster</p>"
           "<p>Die Schule feiert. ( Foto: Nanthakumar Kumarasamy )</p>"
           "<p>Pfarrer Savarimuthu lud ein. © Nierhoff Werne – Seit 2013 gibt es Messen in Tamil.</p>"
           "<p>Anna Fries ( KNA )</p><p>Das Fest endet am Dienstag. Anna Fries ( KNA )</p>"
           "<p>Schmerzhafte Rituale</p>"
           "<p>«Ich will Menschenleben retten.» (Berner Zeitung)</p><p>Jürgen Kappel</p><p>Templefest:</p>")
    text = stilbeispiele.bereinigen(roh)
    for rest in ("SOLINGEN", "(red)", "Webermann", "KESSLER", "Bucher", "Nierhoff", "Muster", "Kumarasamy", "Foto",
                 "©", "KNA", "Fries", "Berner Zeitung", "Kappel"):
        assert rest not in text, rest
    assert text.startswith("Rund 75 Kinder lernen sonntags Tamil.")
    assert "Er sitzt neu im Stadtparlament. Er läuft Halbmarathons." in text
    assert "Pfarrer Savarimuthu lud ein. Seit 2013 gibt es Messen in Tamil." in text
    assert "Das Fest endet am Dienstag.\n\n" in text
    assert "Schmerzhafte Rituale" in text                      # Zwischenzeile mitten im Text bleibt
    assert text.endswith("«Ich will Menschenleben retten.»")
    assert stilbeispiele.bereinigen("<p>LützelflühVor 26 Jahren kam sie zur Welt.</p>") == \
        "Vor 26 Jahren kam sie zur Welt."


def test_gespeicherte_beispiele_ohne_fremde_nachweise():
    import re
    muster = re.compile(r"\((?:\s*(?:Foto|Fotos|Bild|Bilder)\s*:)|©|\((?:red|dpa|KNA|ots|epd|AFP|sda)\s*\)|"
                        r"\bQuelle\s*:|\bTel\.|^Von [A-ZÄÖÜ]\w+ [A-ZÄÖÜ]\w+$", re.M)
    for b in stilbeispiele.laden():
        assert not muster.search(b["text"]), (b["id"], muster.search(b["text"]).group(0))


@pytest.mark.parametrize("kaputt", ["fehlt", "kein_json", "falsche_form", "untauglich"])
def test_cli_meldet_kaputte_eingabe_ohne_traceback(tmp_path, monkeypatch, capsys, kaputt):
    from news_radar import __main__ as cli

    ziel = tmp_path / "style.json"
    monkeypatch.setattr(cli, "STYLE_FILE", ziel)
    ordner = tmp_path / "export"
    ordner.mkdir()
    if kaputt == "kein_json":
        (ordner / "posts.json").write_text("{kaputt", encoding="utf-8")
    elif kaputt == "falsche_form":
        (ordner / "posts.json").write_text('[{"id": 1}]', encoding="utf-8")
    elif kaputt == "untauglich":
        (ordner / "posts.json").write_text((EXPORT / "posts.json").read_text(encoding="utf-8"), encoding="utf-8")
        monkeypatch.setattr(stilbeispiele, "AUSWAHL", {9597: "kueche"})
    assert cli.main(["style", "--export", str(ordner)]) == 1
    assert "Stilbeispiele" in capsys.readouterr().err
    assert not ziel.exists()


def test_kaputte_beispieldatei_laesst_export_ohne_beispiele_weiterlaufen(tmp_path):
    datei = tmp_path / "style.json"
    datei.write_text("[{kaputt", encoding="utf-8")
    assert stilbeispiele.laden(datei) == [] and stilbeispiele.passende("event", "", path=datei) == []
    datei.write_text('{"kein": "liste"}', encoding="utf-8")
    assert stilbeispiele.laden(datei) == []
    datei.write_text('[{"title": "ohne Text"}, {"title": "T", "text": "x", "art": "event"}]', encoding="utf-8")
    assert [b["title"] for b in stilbeispiele.laden(datei)] == ["T"]
