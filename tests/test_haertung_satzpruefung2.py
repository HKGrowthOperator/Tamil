"""Nachbesserung der Satzprüfung nach der Code-Prüfung (P2-1, P2-4, P3).

P2-1 Ein Claim ohne Überlappung mit dem Satz zählt nicht mit – er lehnt den Satz aber auch nicht ab; die Fakten werden
     nur gegen die überlappenden Claims geprüft.
P2-4 Präpositionen und Partikeln am Satzanfang („Laut“, „Beim“, „Etwa“) sind kein Pflichtfakt; Genitiv-s („Kölns“).
P3   Uhrzeit „19.00“ trägt „19“, ein Datum „14.11.2026“ trägt „14“, „Dreizehn“ ist „13“, „achten“ ist kein Zahlwort.
"""

import pytest

from news_radar.agents import pruefer
from news_radar.workflow.models import Claim, SatzUrteil


def _claim(cid, aussage, fundstelle=""):
    return Claim(id=cid, aussage=aussage, art="wo", kern=True, quellen=["Q1"], fundstelle=fundstelle or aussage,
                 sicherheit=0.9, support="bestaetigt")


def _urteil(satz, ids, claims):
    return pruefer.belegt([SatzUrteil(nr=1, satz=satz, urteil="gedeckt", claim_ids=ids, fundstelle="", kern=True)],
                          claims)[0].urteil


KOELN = [_claim("C1", "Der tamilische Kulturverein Köln hat am Freitag den Integrationspreis der Stadt Köln erhalten."),
         _claim("C3", "Der Verein betreibt seit 1998 eine Samstagsschule mit rund 200 Kindern.")]


def test_p2_1_fremder_zusatzclaim_lehnt_belegten_satz_nicht_ab():
    assert _urteil("Tamilischer Verein in Köln gewinnt Integrationspreis", ["C1", "C3"], KOELN) == "gedeckt"


def test_p2_1_fremder_claim_allein_traegt_nicht():
    claims = [_claim("C9", "Die Auszeichnung ist mit 250 Euro dotiert.")]
    assert _urteil("Die Samstagsschule hat 250 Kindern Platz geboten.", ["C9"], claims) == "ungedeckt"


def test_p2_1_fakt_nur_aus_fremdem_claim_traegt_nicht():
    claims = [_claim("C5", "Die Feier beginnt um 10 Uhr mit einer Prozession, der Eintritt ist frei."),
              _claim("C2", "Die tamilische Gemeinde in Hamm feiert am Samstag, 14. November, ihr Lichterfest.")]
    assert _urteil("Die Feier beginnt um 14 Uhr mit einer Prozession, der Eintritt ist frei.", ["C5", "C2"],
                   claims) == "ungedeckt"


@pytest.mark.parametrize("satz, aussage", [
    ("Laut Veranstalter beginnt die Feier um 10 Uhr.", "Der Veranstalter teilt mit: Die Feier beginnt um 10 Uhr."),
    ("Beim Fest gibt es eine Prozession um 10 Uhr.", "Zum Fest gehört eine Prozession um 10 Uhr."),
    ("Etwa 300 Gäste kamen zur Feier.", "Zur Feier kamen 300 Gäste."),
    ("Kölns Kulturverein erhielt den Integrationspreis.", "Der Kulturverein in Köln erhielt den Integrationspreis."),
])
def test_p2_4_satzanfang_ohne_pflichtfakt(satz, aussage):
    assert _urteil(satz, ["C1"], [_claim("C1", aussage)]) == "gedeckt"


def test_p2_4_name_am_satzanfang_bleibt_pflicht():
    claims = [_claim("C1", "Die Feier beginnt um 10 Uhr mit einer Prozession.")]
    assert _urteil("Kumar eröffnet die Feier um 10 Uhr mit einer Prozession.", ["C1"], claims) == "ungedeckt"


@pytest.mark.parametrize("satz, aussage, fundstelle", [
    ("Die Feier beginnt um 19 Uhr mit einer Prozession.", "Die Feier beginnt um 19.00 Uhr mit einer Prozession.", ""),
    ("Die Feier mit Prozession beginnt am 14. November.", "Die Feier mit Prozession im November.", "Beginn 14.11.2026"),
    ("Dreizehn Gruppen tanzen bei der Feier.", "Bei der Feier tanzen 13 Gruppen.", ""),
])
def test_p3_zahlen_in_anderer_schreibung(satz, aussage, fundstelle):
    assert _urteil(satz, ["C1"], [_claim("C1", aussage, fundstelle)]) == "gedeckt"


def test_p3_achten_ist_kein_zahlwort():
    assert "achten" not in pruefer.fakten_beleg("Die Helfer achten auf die Gäste.")


# ---- Gegenprüfung: Dezimalzahlen, Zahlwörter gegen Datum, kurzes Genitiv-s, Monatsname gegen Datum ------------------

@pytest.mark.parametrize("satz, aussage", [
    ("Der Eintritt zur Feier kostet 12 Franken.", "Der Eintritt zur Feier kostet 12.50 Franken."),
    ("Der Eintritt zur Feier kostet 50 Franken.", "Der Eintritt zur Feier kostet 12.50 Franken."),
    ("Zur Feier kamen zehn Familien aus der Gemeinde.", "Zur Feier der Gemeinde am 10.11. kamen Familien."),
    ("Hans Kumar leitet die Feier der Gemeinde.", "Shanthi Kumar leitet die Feier der Gemeinde."),
    ("Die Feier der Gemeinde beginnt am 16. November.", "Die Feier der Gemeinde beginnt am 15.11.2026."),
])
def test_gegenpruefung_bleibt_ungedeckt(satz, aussage):
    assert _urteil(satz, ["C1"], [_claim("C1", aussage)]) == "ungedeckt"


@pytest.mark.parametrize("satz, aussage", [
    ("Die Feier der Gemeinde beginnt um 19 Uhr.", "Die Feier der Gemeinde beginnt um 19.00 Uhr."),
    ("Die Feier der Gemeinde beginnt am 15. November.", "Die Feier der Gemeinde beginnt am 15.11.2026."),
    ("Kölns Kulturverein erhielt den Integrationspreis.", "Der Kulturverein in Köln erhielt den Integrationspreis."),
])
def test_gegenpruefung_bleibt_gedeckt(satz, aussage):
    assert _urteil(satz, ["C1"], [_claim("C1", aussage)]) == "gedeckt"
