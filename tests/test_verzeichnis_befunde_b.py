"""Verzeichnis: Befunde der Code-Prüfung von Sitzung B (P3).

a) Freigabe und gleichzeitige Ablehnung aus einem zweiten Fenster: die Website hat angelegt, im Radar ist die
   Einsendung inzwischen abgelehnt – das wird protokolliert und gemeldet, nicht still übergangen.
b) Netzabbruch beim Anlegen und kein Abgleich möglich: Ausgang unklar, noch einmal freigeben (nichts doppelt) – nicht
   „nichts geändert“.
d) Ohne Vorschlag des Agenten gilt die vom Einsender gewählte Kategorie, wenn sie zur Art passt.
"""

import pytest
import requests

from news_radar import verzeichnis
from news_radar.workflow import repo

from test_verzeichnis_agent import VEREIN, lauf, settings, store, wp  # noqa: F401


class _Sitzung:
    """Wie die Fake-Website, mit einem Eingriff vor dem Anlegen bzw. einem Netzabbruch."""

    def __init__(self, wp, vorher=None, abbruch=False):
        self.wp, self.vorher, self.abbruch = wp, vorher, abbruch
        self.headers, self.auth = {}, None

    def request(self, method, url, **kw):
        if method == "POST" and url.rstrip("/").endswith("/eintrag"):
            if self.abbruch:
                raise requests.ConnectionError("Verbindung abgebrochen")
            if self.vorher:
                self.vorher()
        if self.abbruch and method == "GET" and "/einsendung" in url:
            raise requests.ConnectionError("Verbindung abgebrochen")
        return self.wp.request(method, url, **kw)


def _client(sitzung):
    from news_radar.wordpress import TamilRadarClient

    return TamilRadarClient("https://www.tamil.test", "ki-agent", "app-pw", session=sitzung)


def test_a_freigabe_gegen_gleichzeitige_ablehnung_wird_gemeldet(store, wp):
    v = wp.einreichen("neu", {**VEREIN})
    lauf(store, wp)

    def zweites_fenster():
        verzeichnis.ablehnen(store, None, v, von="anna")

    with pytest.raises(verzeichnis.Konflikt, match="abgelehnt"):
        verzeichnis.freigeben(store, _client(_Sitzung(wp, vorher=zweites_fenster)), v, von="priya")
    assert repo.aktionen_liste(store, aktion="verzeichnis_freigabe_konflikt")


def test_b_netzabbruch_heisst_ausgang_unklar(store, wp):
    v = wp.einreichen("neu", {**VEREIN})
    lauf(store, wp)
    with pytest.raises(verzeichnis.Konflikt) as fehler:
        verzeichnis.freigeben(store, _client(_Sitzung(wp, abbruch=True)), v, von="priya")
    assert "Ausgang unklar" in str(fehler.value) and "nichts doppelt" in str(fehler.value)
    assert "nichts geändert" not in str(fehler.value)


@pytest.mark.parametrize("kategorie, erwartet", [("verein-kultur", "verein-kultur"), ("business-reise", "")])
def test_d_kategorie_des_einsenders_als_ersatz(store, wp, kategorie, erwartet):
    v = wp.einreichen("neu", {**VEREIN, "kategorie": kategorie})
    lauf(store, wp)  # ohne Modell: kein Vorschlag des Agenten
    assert verzeichnis.vorschlag(verzeichnis.holen(store, v))["kategorie"] == erwartet


def test_a_doppelte_freigabe_ist_kein_konflikt(store, wp):
    # Doppelklick bzw. zweites Fenster gibt ebenfalls frei: kein Fehlalarm, die Antwort kommt zurück
    v = wp.einreichen("neu", {**VEREIN})
    lauf(store, wp)

    def anna_gibt_frei():
        verzeichnis.freigeben(store, _client(_Sitzung(wp)), v, von="anna")

    ergebnis = verzeichnis.freigeben(store, _client(_Sitzung(wp, vorher=anna_gibt_frei)), v, von="priya")
    assert isinstance(ergebnis, dict) and "nicht_uebernommen" in ergebnis
    assert not repo.aktionen_liste(store, aktion="verzeichnis_freigabe_konflikt")
    assert verzeichnis.holen(store, v)["status"] == "freigegeben"
