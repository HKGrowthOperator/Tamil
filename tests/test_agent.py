"""Agent-Modus: Aufgabenmappe exportieren, fertige Beiträge importieren."""

import json

import pytest

from news_radar import agent
from news_radar.config import load_settings
from news_radar.store import Store
from news_radar.writer import ROH_HINWEIS


@pytest.fixture
def settings(monkeypatch, tmp_path):
    for var in ("WP_USER", "WP_APP_PASSWORD", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "GEMINI_API_KEY", "BILD_POOL_DIR"):
        monkeypatch.setenv(var, "")
    s = load_settings()
    s.data_dir = tmp_path
    return s


def _row(uid: str, titel: str, **extra) -> dict:
    row = {
        "uid": uid, "typ": "artikel", "quelle_name": "WA Hamm", "quelle_url": f"https://wa.de/{uid}",
        "quelle_datum": "2026-10-18T09:00", "quelle_sprache": "de", "relevanz": 8, "begruendung": "DACH",
        "dach_bezug": True, "ort": "Hamm", "kategorie": "community", "titel": titel, "teaser": "Teaser",
        "inhalt_html": "<p>Roh</p>", "schlagworte": ["Hamm"], "seo_titel": titel, "meta_beschreibung": "m",
        "bild_datei": "", "bild_credit": "", "bild_alt": titel, "bild_suchbegriff": "temple", "bild_origin": "karte",
        "hinweise": [ROH_HINWEIS], "fakten": {"event_ort": "Hamm"},
    }
    row.update(extra)
    return row


def _fertig(draft_id: int, titel: str, **extra) -> dict:
    d = {
        "id": draft_id, "relevanz": 9, "begruendung": "Tempelfest in Hamm", "kategorie": "community", "typ": "artikel",
        "dach_bezug": True, "ort": "Hamm", "titel": titel, "teaser": "Ein Fest für die Community in Hamm.",
        "inhalt_html": ("<p>Der Tempel in Hamm-Uentrop lädt am Wochenende zum Fest ein, hunderte Gäste werden erwartet.</p>"
                        "<p>Der Verein bittet um Anmeldung, Parkplätze sind knapp.</p><p class=\"quelle\">Quelle: WA Hamm</p>"),
        "schlagworte": ["Hamm", "Tempel"], "seo_titel": titel[:60] or "Fest", "meta_beschreibung": "Tempelfest in Hamm mit Programm und Anmeldung",
        "bild_suchbegriff": "hindu temple festival", "bild_alt": "Tempel in Hamm", "bild_thema": "tempelfest",
        "bild_prompt": "Colorful temple exterior in a German town, marigold garlands, overcast light",
        "event_datum": "", "event_ort": "", "ticket_url": "",
    }
    d.update(extra)
    return d


def test_export_tasks_shape(settings, tmp_path):
    with Store(settings.db_path) as store:
        a = store.insert_draft(_row("u1", "Tempelfest Hamm"))
        b = store.insert_draft(_row("u2", "Google-Treffer", quelle_url="https://news.google.com/rss/x", relevanz=6))
        c = store.insert_draft(_row("u3", "Schon geschrieben", hinweise=[]))
        datei = tmp_path / "aufgaben.json"
        data = agent.export_tasks(store, settings, datei, fetch_text=lambda url: f"Text von {url}")
    assert [e["id"] for e in data["entwuerfe"]] == [a, b]  # c ist keine Rohfassung; Relevanz zuerst
    assert data["entwuerfe"][0]["quelltext"] == "Text von https://wa.de/u1"
    assert data["entwuerfe"][1]["quelltext"] == ""  # Google-News-Links sind Weiterleitungen
    assert data["entwuerfe"][0]["fakten"] == {"event_ort": "Hamm"} and data["entwuerfe"][0]["hinweise"] == [ROH_HINWEIS]
    assert "# Redaktionsprofil" in data["stil"] and "{motiv}" in data["bildregeln"]
    assert "tempelfest" in data["bildthemen"] and "bild_prompt" in data["felder"]
    assert {"slug": "community", "label": "Community"} in data["kategorien"]
    assert json.loads(datei.read_text(encoding="utf-8"))["anleitung"].startswith("Schreibe aus jedem Entwurf")
    with Store(settings.db_path) as store:
        alle = agent.export_tasks(store, settings, datei, nur_roh=False, limit=2, mit_text=False)
    assert len(alle["entwuerfe"]) == 2 and alle["entwuerfe"][0]["quelltext"] == ""


def test_import_results_writes_rejects_and_reports(settings, tmp_path):
    with Store(settings.db_path) as store:
        a = store.insert_draft(_row("u1", "Tempelfest Hamm"))
        b = store.insert_draft(_row("u2", "Dublette"))
        c = store.insert_draft(_row("u3", "Kaputt"))
        store.insert_draft(_row("u4", "Kino", typ="kino_termine"))
        d = store.draft_by_uid("u4")["id"]
        ergebnis = tmp_path / "ergebnis.json"
        ergebnis.write_text(json.dumps({"ergebnisse": [
            _fertig(a, "Chithrapowrnami-Fest in Hamm"),
            {"id": b, "verwerfen": "Gleiches Thema wie Entwurf 1"},
            _fertig(c, "", kategorie="community"),  # leerer Titel → Validierungsfehler
            _fertig(d, "Jailer 2 läuft an", typ="artikel", kategorie="kino"),
            {"id": 999, "verwerfen": "gibt es nicht"},
            _fertig(a, "Nochmal geschrieben", kategorie="gibt-es-nicht"),
        ]}), encoding="utf-8")
        stats = agent.import_results(store, settings, ergebnis, von="Claude (Research)")
        fertig, verworfen, kaputt, kino = (store.get_draft(i) for i in (a, b, c, d))
        log = list(store.iter_log(event="agent"))
    assert stats["uebernommen"] == 2 and stats["verworfen"] == 1 and stats["bilder"] == {"karte": 2}
    assert len(stats["fehler"]) == 3 and any("999" in f for f in stats["fehler"]) and any("gibt-es-nicht" in f for f in stats["fehler"])
    assert fertig["status"] == "bearbeitet" and fertig["titel"] == "Chithrapowrnami-Fest in Hamm"
    assert fertig["hinweise"] == [] and fertig["bild_datei"].endswith("-a1.jpg") and fertig["bild_origin"] == "karte"
    assert fertig["bild_prompt"].startswith("Colorful temple") and fertig["bild_thema"] == "tempelfest"
    assert fertig["bearbeitet_von"] == "Claude (Research)" and fertig["rewrite_count"] == 1
    assert (settings.bilder_dir / fertig["bild_datei"]).exists()
    assert verworfen["status"] == "abgelehnt" and kaputt["status"] == "neu" and kaputt["titel"] == "Kaputt"
    assert kino["typ"] == "kino_termine" and kino["kategorie"] == "kino"  # typ bleibt, Kinoliste hängt daran
    assert [e["aktion"] for e in log] == ["geschrieben", "verworfen", "geschrieben"][::-1] or len(log) == 3


def test_import_refuses_published_drafts(settings, tmp_path):
    with Store(settings.db_path) as store:
        a = store.insert_draft(_row("u1", "Alt"))
        store.set_status(a, "freigeben")
        store.claim_draft(a)
        store.mark_published(a, 5, "https://tamil.de/alt")
        ergebnis = tmp_path / "e.json"
        ergebnis.write_text(json.dumps([_fertig(a, "Neu geschrieben")]), encoding="utf-8")
        stats = agent.import_results(store, settings, ergebnis)
        assert stats["uebernommen"] == 0 and "veroeffentlicht" in stats["fehler"][0]
        assert store.get_draft(a)["titel"] == "Alt"
