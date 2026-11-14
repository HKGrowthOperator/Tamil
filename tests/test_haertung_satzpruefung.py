"""Härtung der Satzprüfung im Agent-Import (Prüfliste vom 13.11.2026, Punkt 2).

Die zweite KI urteilt je Satz „gedeckt“ mit claim_ids; der Radar prüft nach (pruefer.belegt). Nachgestellt über den
echten Weg (Agent-Import der Hamm-Story mit einem zusätzlichen Satz und dem Urteil der Prüferin):

a) Zahlen nur als ganze Tokens: „300“ steckt in „3000“, „1“ in „10“ – das trägt den Satz nicht.
b) Zahlwörter („zwölf“) und Verneinungen („nicht“, „kein“) sind Fakten, die im Beleg stehen müssen.
c) Höchstens drei Claims je Satz, und jeder genannte Claim überlappt mit dem Satz (nicht nur in einer Zahl).
d) Das erste Wort zählt mit (ein Name am Satzanfang), Funktionswörter („Die“, „Der“) ausgenommen.
"""

import hashlib

import pytest

from news_radar.agent_v2 import import_daten
from news_radar.agents import pruefer
from news_radar.store import Store
from news_radar.workflow import fake as fake_mod

from test_nachrecherche import _hamm_offen, settings  # noqa: F401


def _import(settings, zusatz, claim_ids):
    """Hamm-Story im Agent-Import; der Zusatzsatz steht am Ende des ersten Absatzes und ist von der zweiten KI
    als „gedeckt“ mit `claim_ids` beurteilt. Ergebnis: inhalt_html des Entwurfs."""
    with Store(settings.db_path) as store:
        ctx, sid, claims, beitrag = _hamm_offen(settings, store)
        beitrag = dict(beitrag)
        html = beitrag["inhalt_html"]
        i = html.index("</p>")
        beitrag["inhalt_html"] = html = html[:i] + " " + zusatz + html[i:]
        block = fake_mod.pruefung_block(beitrag, claims, pruefer="p2")
        block["sha256"] = hashlib.sha256(html.encode()).hexdigest()
        for s in block["saetze"]:
            if s["satz"] == zusatz:
                s.update(urteil="gedeckt", claim_ids=claim_ids, fundstelle="", kern=False)
        assert any(s["satz"] == zusatz for s in block["saetze"])
        stats = import_daten(store, settings, {"ergebnisse": [{"story_id": sid, "claims": claims, "beitrag": beitrag,
                                                               "pruefung": block}]}, von="cloud-sitzung", ctx=ctx)
        d = store.list_drafts()
        assert stats["entwuerfe"] == 1, stats
        return d[0]["inhalt_html"]


# ---- a) Zahlen als ganze Tokens ---------------------------------------------------------------------------------

@pytest.mark.parametrize("zusatz, ids", [
    ("Erwartet werden rund 300 Besucherinnen und Besucher aus ganz Deutschland.", ["C3"]),  # 300 in 3000
    ("Die Feier beginnt um 1 Uhr mit einer Prozession, der Eintritt ist frei.", ["C5"]),  # 1 in 10
    ("Die tamilische Gemeinde in Hamm feiert am Samstag, 4. November, ihr Lichterfest im Sri-Kamadchi-Ampal-Tempel.",
     ["C2"]),  # 4 in 14
])
def test_a_zahl_nur_als_ganzes_token(settings, zusatz, ids):
    assert zusatz not in _import(settings, zusatz, ids)


def test_a_richtige_zahl_bleibt(settings):
    zusatz = "Erwartet werden insgesamt rund 3000 Besucherinnen und Besucher aus ganz Deutschland."
    assert zusatz in _import(settings, zusatz, ["C3"])


# ---- b) Zahlwörter und Verneinungen -----------------------------------------------------------------------------

@pytest.mark.parametrize("zusatz", [
    "Die Feier beginnt um zwölf Uhr mit einer Prozession, der Eintritt ist frei.",
    "Die Feier beginnt um 10 Uhr mit einer Prozession, der Eintritt ist nicht frei.",
    "Die Feier beginnt um 10 Uhr mit einer Prozession, es gibt keinen freien Eintritt.",
])
def test_b_zahlwort_und_verneinung_muessen_belegt_sein(settings, zusatz):
    assert zusatz not in _import(settings, zusatz, ["C5"])


def test_b_zahlwort_mit_ziffer_im_beleg_bleibt(settings):
    zusatz = "Die Feier beginnt um zehn Uhr mit einer Prozession, der Eintritt ist frei."
    assert zusatz in _import(settings, zusatz, ["C5"])


# ---- c) höchstens drei Claims, Mindestüberlappung -----------------------------------------------------------------

def test_c_mehr_als_drei_claims_tragen_keinen_satz(settings):
    # jedes Wort steht irgendwo in den vier Claims, die Aussage („2002 Besucherinnen“) stimmt trotzdem nicht
    zusatz = ("Der Tempelverein in Hamm-Uentrop erwartet am Samstag, 14. November, rund 2002 Besucherinnen aus "
              "ganz Deutschland.")
    assert zusatz not in _import(settings, zusatz, ["C2", "C3", "C4", "C6"])


def test_c_claim_nur_fuer_eine_zahl_genannt_traegt_nicht(settings):
    # C2 wird nur wegen der „14“ (14. November) genannt; mit dem Satz hat er sonst nichts gemein
    zusatz = "Die Feier beginnt um 14 Uhr mit einer Prozession, der Eintritt ist frei."
    assert zusatz not in _import(settings, zusatz, ["C5", "C2"])


def test_c_zwei_passende_claims_tragen(settings):
    zusatz = "Die tamilische Gemeinde in Hamm erwartet am Samstag rund 3000 Besucherinnen und Besucher."
    assert zusatz in _import(settings, zusatz, ["C2", "C3"])


# ---- d) erstes Wort ---------------------------------------------------------------------------------------------

def test_d_name_am_satzanfang_muss_belegt_sein(settings):
    zusatz = "Kumar eröffnet die Feier um 10 Uhr mit einer Prozession."
    assert zusatz not in _import(settings, zusatz, ["C5"])


def test_d_funktionswort_am_satzanfang_zaehlt_nicht():
    assert "Die" not in pruefer.fakten_beleg("Die Feier beginnt um 10 Uhr.")
    assert "Kumar" in pruefer.fakten_beleg("Kumar eröffnet die Feier.")
