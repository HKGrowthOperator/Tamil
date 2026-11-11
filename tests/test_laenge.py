"""Länge nach Stofflage (Anweisung des Auftraggebers vom 11.11.2026: Beiträge von mehreren Minuten).

Viel Stoff = acht und mehr bestätigte Aussagen aus mindestens zwei Verlagen oder aus einer Primärquelle mit
Volltext. Mittlerer Stoff = vier bis sieben. Wenig Stoff = Kurzmeldung. Gestreckt wird nie.
"""

import pytest

from news_radar import prompts
from news_radar.agents import copydesk, factcheck, schreiben
from news_radar.workflow.models import Claim, SourceDocument


@pytest.mark.parametrize("typ,bestaetigt,verlage,primaer,soll", [
    ("news", 3, 2, False, "kurz"),
    ("news", 4, 1, False, "normal"),
    ("news", 7, 2, False, "normal"),
    ("news", 8, 2, False, "lang"),
    ("news", 8, 1, False, "normal"),      # eine Zeitung reicht nicht für „lang“
    ("news", 9, 1, True, "lang"),         # … eine ergiebige Primärquelle schon
    ("event", 8, 2, False, "event_lang"),
    ("event", 5, 1, False, "event"),
    ("event", 2, 1, False, "kurz"),
    ("kino", 8, 1, True, "kino_lang"),
    ("kino", 4, 1, False, "kino"),
    ("dossier", 1, 1, False, "dossier"),
])
def test_staffel_nach_stofflage(typ, bestaetigt, verlage, primaer, soll):
    assert factcheck.laenge_fuer(typ, bestaetigt, verlage, primaer) == soll


def test_neue_zielwerte():
    L = schreiben.LAENGEN
    assert L["lang"] == (450, 750)
    assert L["event_lang"] == L["kino_lang"] == (350, 550)
    assert L["normal"] == L["event"] == L["kino"] == (250, 400)
    assert L["kurz"] == (80, 150)
    assert L["dossier"] == (600, 1000)


def _doc(key, verlag, art="volltext", primaer=False):
    return SourceDocument(doc_key=key, url=f"https://{verlag}.example/a", publisher=verlag, art=art, primaer=primaer,
                          text="Wort " * 50)


def _claims(n, quelle):
    return [Claim(id=f"C{i}", aussage=f"Aussage {i}", art="was", kern=i == 1, quellen=[quelle],
                  fundstelle="Wort Wort Wort Wort", sicherheit=0.9) for i in range(1, n + 1)]


def test_gate_lang_aus_primaerquelle_und_ohne_volltext_nie_lang():
    story = {"typ": "news", "titel": "Tempel in Hamm"}
    g = factcheck.gate(story, [_doc("Q1", "tempel", primaer=True)], _claims(9, "Q1"), [])
    assert g.laenge == "lang"
    ohne = factcheck.gate(story, [_doc("Q1", "tempel", art="daten", primaer=True)], _claims(9, "Q1"), [])
    assert ohne.laenge == "kurz"
    event = factcheck.gate({"typ": "event", "titel": "Fest"}, [_doc("Q1", "verein", art="daten", primaer=True)],
                           _claims(9, "Q1"), [])
    assert event.laenge == "event"      # ohne Volltext keine lange Event-Fassung


def test_laengentext_nennt_aufbau_und_verbietet_strecken():
    lang = schreiben.laenge_text("lang", "news")
    assert "450–750" in lang and "<h2>" in lang and "nicht strecken" in lang.lower()
    kino = schreiben.laenge_text("kino_lang", "kino")
    assert "350–550" in kino and "Service-Absatz" in kino and "keine Kinos im Text" in kino
    assert "nichts auffüllen" in schreiben.laenge_text("kurz", "news")


def _html(n, h2=False):
    absatz = "<p>" + " ".join(["Wort"] * (n // 5)) + "</p>"
    return ("<h2>Hintergrund</h2>" if h2 else "") + absatz * 5


def test_lektorat_prueft_neue_laengen_und_zwischenueberschriften():
    def hinweise(n, laenge, h2=False):
        return copydesk.pruefen({"inhalt_html": _html(n, h2)}, [], [], laenge, [])
    assert not any(h.startswith("Länge") for h in hinweise(600, "lang", h2=True))
    zu_kurz = [h for h in hinweise(300, "lang", h2=True) if h.startswith("Länge")]
    assert zu_kurz and "nicht strecken" in zu_kurz[0]
    assert any("Zwischenüberschrift" in h for h in hinweise(600, "lang"))
    assert not any("Zwischenüberschrift" in h for h in hinweise(120, "kurz"))
    assert any(h.startswith("Länge") for h in hinweise(300, "kurz"))


def test_prompts_nennen_die_neue_staffel():
    red = prompts.redaktion()
    for wert in ("450–750", "350–550", "250–400", "80–150"):
        assert wert in red
    assert "180–350" not in red and "300–450" not in red
    assert "nicht strecken" in prompts.load_prompt("text").lower()
    assert "Zwischenüberschrift" in prompts.load_prompt("lektorat")
