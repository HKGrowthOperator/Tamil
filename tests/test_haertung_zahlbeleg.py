"""Erfundene Zahl in der Claim-Aussage (Code-Prüfung der Nachtschicht 14./15.11., Befund P1).

Die Aussage eines Claims schreibt der Agent selbst; das Gate prüfte nur, ob die Fundstelle wörtlich im Dokument steht.
Eine echte Fundstelle mit einer erfundenen Aussage („5 Millionen Euro Zuschuss“) wurde so „bestätigt“, und die
Satzprüfung ließ den gleichlautenden Satz als „gedeckt“ durch. Jetzt gilt: Jede Zahl der Aussage muss in einem der
gelesenen Dokumente stehen, sonst ist der Claim nicht bestätigt. Zahlen sind sprachunabhängig – die Regel trifft auch
Aussagen auf Deutsch zu englischen oder tamilischen Quellen.
"""

from news_radar.agents import factcheck, pruefer
from news_radar.workflow.models import Claim, SatzUrteil, SourceDocument


def _doc(text, key="Q1", primaer=True, published_at=""):
    return SourceDocument(doc_key=key, url=f"https://beispiel.de/{key}", publisher="Beispiel", quelle="Beispiel",
                          published_at=published_at, retrieved_at="2026-11-14T00:00:00+00:00", language="de",
                          rights="zitat", primaer=primaer, art="volltext", titel="Lichterfest", text=text)


def _claim(aussage, fundstelle, quellen=("Q1",)):
    return Claim(id="C1", aussage=aussage, art="was", kern=True, quellen=list(quellen), fundstelle=fundstelle,
                 sicherheit=0.9)


DOC = _doc("Das Lichterfest im Tempel in Hamm beginnt am Samstag um 19 Uhr. Erwartet werden rund 1.500 Gäste.")


def _support(claim, docs=(DOC,)):
    return factcheck.gate({"typ": "news", "titel": "Lichterfest"}, list(docs), [claim], []).claims[0].support


def test_erfundene_zahl_in_der_aussage_ist_nicht_bestaetigt():
    c = _claim("Das Land NRW zahlt dem Tempel in Hamm 5 Millionen Euro Zuschuss",
               "Das Lichterfest im Tempel in Hamm beginnt")
    assert _support(c) != "bestaetigt"


def test_erfundener_satz_bleibt_ungedeckt():
    c = _claim("Das Land NRW zahlt dem Tempel in Hamm 5 Millionen Euro Zuschuss",
               "Das Lichterfest im Tempel in Hamm beginnt")
    claims = factcheck.gate({"typ": "news", "titel": "Lichterfest"}, [DOC], [c], []).claims
    satz = "Das Land NRW zahlt dem Tempel in Hamm 5 Millionen Euro Zuschuss."
    u = SatzUrteil(nr=1, satz=satz, urteil="gedeckt", claim_ids=["C1"], fundstelle="", kern=True)
    assert pruefer.belegt([u], claims)[0].urteil == "ungedeckt"


def test_zahl_aus_dem_dokument_bleibt_bestaetigt():
    c = _claim("Das Lichterfest im Tempel in Hamm beginnt um 19 Uhr.", "Das Lichterfest im Tempel in Hamm beginnt")
    assert _support(c) == "bestaetigt"


def test_tausenderpunkt_und_komma_zaehlen_gleich():
    c = _claim("Erwartet werden rund 1,500 Gäste.", "Erwartet werden rund 1.500 Gäste")
    assert _support(c) == "bestaetigt"


def test_zahl_aus_einem_zweiten_dokument_der_story_zaehlt():
    zweites = _doc("Der Eintritt kostet 10 Euro.", key="Q2", primaer=False)
    c = _claim("Das Lichterfest in Hamm beginnt um 19 Uhr, der Eintritt kostet 10 Euro.",
               "Das Lichterfest im Tempel in Hamm beginnt", quellen=("Q1", "Q2"))
    assert _support(c, docs=(DOC, zweites)) == "bestaetigt"


def test_jahr_aus_dem_veroeffentlichungsdatum_zaehlt():
    doc = _doc("Das Lichterfest im Tempel in Hamm beginnt am 21.11. um 19 Uhr.", published_at="2026-11-10T08:00+00:00")
    c = _claim("Das Lichterfest im Tempel in Hamm beginnt am 21. November 2026 um 19 Uhr.",
               "Das Lichterfest im Tempel in Hamm beginnt")
    assert _support(c, docs=(doc,)) == "bestaetigt"


def test_aussage_ohne_zahl_unveraendert():
    c = _claim("Im Tempel in Hamm wird das Lichterfest gefeiert.", "Das Lichterfest im Tempel in Hamm beginnt")
    assert _support(c) == "bestaetigt"


def test_uhrzeit_am_pm_traegt_24_stunden_form():
    doc = _doc("The Diwali festival at the temple in Hamm starts at 7 pm.")
    c = _claim("Das Fest im Tempel in Hamm beginnt um 19 Uhr.", "The Diwali festival at the temple in Hamm starts")
    assert _support(c, docs=(doc,)) == "bestaetigt"


def test_monatsname_traegt_monatszahl():
    doc = _doc("The Diwali festival at the temple in Hamm takes place on November 21.")
    c = _claim("Das Fest im Tempel in Hamm findet am 21.11. statt.", "The Diwali festival at the temple in Hamm")
    assert _support(c, docs=(doc,)) == "bestaetigt"


def test_falsche_uhrzeit_bleibt_unbestaetigt():
    doc = _doc("The Diwali festival at the temple in Hamm starts at 7 pm.")
    c = _claim("Das Fest im Tempel in Hamm beginnt um 20 Uhr.", "The Diwali festival at the temple in Hamm starts")
    assert _support(c, docs=(doc,)) != "bestaetigt"
