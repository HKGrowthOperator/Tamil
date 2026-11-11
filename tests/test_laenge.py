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
    ("event", 5, 1, False, "event_mittel"),
    ("event", 2, 1, False, "kurz"),
    ("kino", 8, 1, True, "kino_lang"),
    ("kino", 4, 1, False, "kino_mittel"),
    ("dossier", 1, 1, False, "dossier"),
])
def test_staffel_nach_stofflage(typ, bestaetigt, verlage, primaer, soll):
    assert factcheck.laenge_fuer(typ, bestaetigt, verlage, primaer) == soll


def test_neue_zielwerte():
    L = schreiben.LAENGEN
    assert L["lang"] == (450, 750)
    assert L["event_lang"] == L["kino_lang"] == (350, 550)
    assert L["normal"] == L["event_mittel"] == L["kino_mittel"] == (250, 400)
    assert L["event"] == L["kino"] == (150, 250)       # ohne Volltext: knapp
    assert L["kurz"] == (80, 150)
    assert L["dossier"] == (600, 1000)


def _doc(key, verlag, art="volltext", primaer=False):
    return SourceDocument(doc_key=key, url=f"https://{verlag}.example/a", publisher=verlag, art=art, primaer=primaer,
                          text="Wort " * 50)


def _claims(n, *quellen):
    return [Claim(id=f"C{i}", aussage=f"Aussage {i}", art="was", kern=i == 1, quellen=list(quellen),
                  fundstelle="Wort Wort Wort Wort", sicherheit=0.9) for i in range(1, n + 1)]


def test_gate_lang_aus_primaerquelle_und_ohne_volltext_nie_lang():
    story = {"typ": "news", "titel": "Tempel in Hamm"}
    g = factcheck.gate(story, [_doc("Q1", "tempel", primaer=True)], _claims(9, "Q1"), [])
    assert g.laenge == "lang"
    ohne = factcheck.gate(story, [_doc("Q1", "tempel", art="daten", primaer=True)], _claims(9, "Q1"), [])
    assert ohne.laenge == "kurz"
    event = factcheck.gate({"typ": "event", "titel": "Fest"}, [_doc("Q1", "verein", art="daten", primaer=True)],
                           _claims(9, "Q1"), [])
    assert event.laenge == "event"      # ohne Volltext nur die knappe Event-Fassung (150–250)
    assert any("höchstens 150–250 Wörter" in h for h in event.hinweise)
    assert any("höchstens 80–150 Wörter" in h for h in ohne.hinweise)
    kurz = factcheck.gate({"typ": "kino", "titel": "Film"}, [_doc("Q1", "verleih", art="daten", primaer=True)],
                          _claims(3, "Q1"), [])
    assert kurz.laenge == "kurz"


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
    assert "ohne Volltext" in red
    for wert in ("450–750", "350–550", "250–400", "80–150", "150–250"):
        assert wert in red
    assert "180–350" not in red and "300–450" not in red
    assert "nicht strecken" in prompts.load_prompt("text").lower()
    assert "Zwischenüberschrift" in prompts.load_prompt("lektorat")


@pytest.mark.parametrize("typ", ["event", "kino"])
def test_ohne_volltext_knapp_und_ohne_druck_zum_strecken(typ):
    assert factcheck.laenge_fuer(typ, 9, 2, True, volltext=False) == typ
    assert factcheck.laenge_fuer(typ, 3, 2, True, volltext=False) == "kurz"
    assert factcheck.laenge_fuer("news", 9, 2, True, volltext=False) == "kurz"
    text = schreiben.laenge_text(typ, typ)
    assert text.startswith("150–250") and "<h2>" not in text and "nichts auffüllen" in text


@pytest.mark.parametrize("typ,docs", [
    ("event", [_doc("Q1", "verein", art="daten", primaer=True)]),
    ("kino", [_doc("Q1", "a"), _doc("Q2", "b")]),
    ("news", [_doc("Q1", "tempel", primaer=True)]),
    ("news", [_doc("Q1", "a", art="zusammenfassung")]),
])
def test_staffel_im_export_entspricht_dem_gate(typ, docs):
    staffel = factcheck.staffel(typ, docs)
    for stufe, n in (("unter 4", 3), ("4 bis 7", 5), ("ab 8", 9)):
        claims = _claims(n, *[d.doc_key for d in docs])
        assert staffel[stufe] == factcheck.gate({"typ": typ, "titel": "x"}, docs, claims, []).laenge
    text = factcheck.staffel_text(typ, docs)
    for laenge in set(staffel.values()):
        lo, hi = schreiben.LAENGEN[laenge]
        assert f"{lo}–{hi}" in text


def test_eine_schwelle_fuer_die_zwischenueberschrift():
    ab = schreiben.H2_AB_WOERTER
    assert f"ab etwa {ab} Wörtern" in schreiben.laenge_text("lang", "news")
    assert f"ab {ab} Wörtern" in prompts.redaktion()
    hinweise = copydesk.pruefen({"inhalt_html": _html(ab + 10)}, [], [], "normal", [])
    assert any("Zwischenüberschrift" in h for h in hinweise)
    assert not any("Zwischenüberschrift" in h
                   for h in copydesk.pruefen({"inhalt_html": _html(ab - 10)}, [], [], "normal", []))
