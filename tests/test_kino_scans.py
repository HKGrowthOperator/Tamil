"""Kino-Entwürfe über mehrere Scans (Prüfung 11.11.2026, P1): Ein Spielort bleibt im offenen Entwurf, bis seine
eigene Quelle in einem Scan gelaufen ist und den Film nicht mehr meldet. Nicht fällige oder fehlgeschlagene Quellen
ziehen nichts ab – sonst springen die Spielorte zwischen stündlichen (kinoheld) und seltenen (Kino-HTML) Quellen."""

from datetime import datetime, timedelta

import pytest

from news_radar import kino_providers as kp
from news_radar import pipeline, sources
from news_radar.config import Source, load_settings
from news_radar.store import Store

from test_agent import _row


@pytest.fixture
def settings(monkeypatch, tmp_path):
    for var in ("WP_USER", "WP_APP_PASSWORD", "NEWSAPI_KEY", "GNEWS_TOKEN"):
        monkeypatch.setenv(var, "")
    s = load_settings()
    s.data_dir = tmp_path
    return s


def _termin(tage: int) -> datetime:
    """Eine Vorstellung morgen bzw. übermorgen – liegt sicher in dieser oder der nächsten Kinowoche."""
    jetzt = datetime.now(kp.TZ).replace(hour=19, minute=30, second=0, microsecond=0)
    return jetzt + timedelta(days=tage)


class Programm:
    """Fake-Anbieter: was die Quelle in diesem Scan meldet, oder eine Ausnahme (Ausfall)."""

    def __init__(self, shows):
        self.shows, self.fehler = shows, None

    def __call__(self, source, settings):
        if self.fehler:
            raise self.fehler
        return list(self.shows)


def _scan(settings, store):
    items = sources.fetch_all(settings, store)
    pipeline.refresh_kino(items, store, {i.uid for i in items})  # Film ist bekannt (Entwurf liegt)
    return items


def _kinos(store, uid):
    return sorted(k["kino"] for k in store.draft_by_uid(uid)["fakten"]["kinos"])


def test_spielort_bleibt_bis_die_eigene_quelle_ihn_nicht_mehr_meldet(settings, monkeypatch):
    stuendlich = Programm([kp.Show("Jailer 2", "CineStar Mainz", "Mainz", "DE", start=_termin(1))])
    selten = Programm([kp.Show("Jailer 2", "Atelier", "Düsseldorf", "DE", start=_termin(2))])
    monkeypatch.setitem(kp.PROVIDERS, "kinoheld", stuendlich)
    monkeypatch.setitem(kp.PROVIDERS, "html", selten)
    html_quelle = Source(name="Filmkunstkinos", type="kino", url="https://filmkunst.example/", provider="html",
                         interval_minutes=720)
    settings.sources = [Source(name="kinoheld", type="kino", provider="kinoheld"), html_quelle]

    with Store(settings.db_path) as store:
        # Scan 1: beide Quellen laufen → ein Eintrag mit beiden Spielorten, daraus wird der Entwurf
        [item] = sources.fetch_all(settings, store)
        assert sorted(k["kino"] for k in item.facts["kinos"]) == ["Atelier", "CineStar Mainz"]
        store.insert_draft(_row(item.uid, item.title, typ="kino_termine", fakten=item.facts,
                                fingerprint=item.fingerprint, hinweise=[]))

        # Scan 2: die HTML-Quelle ist nicht fällig (720 Min.), kinoheld meldet zusätzlich Bremen
        stuendlich.shows.append(kp.Show("Jailer 2", "CineStar Bremen", "Bremen", "DE", start=_termin(1)))
        _scan(settings, store)
        assert _kinos(store, item.uid) == ["Atelier", "CineStar Bremen", "CineStar Mainz"]
        hinweise = store.draft_by_uid(item.uid)["hinweise"]
        assert len(hinweise) == 1 and "+CineStar Bremen" in hinweise[0] and "−Atelier" not in hinweise[0]

        # Scan 3: unverändert, die HTML-Quelle weiter nicht fällig → kein neuer Hinweis, nichts springt
        _scan(settings, store)
        assert _kinos(store, item.uid) == ["Atelier", "CineStar Bremen", "CineStar Mainz"]
        assert len(store.draft_by_uid(item.uid)["hinweise"]) == 1

        # Scan 4: die HTML-Quelle wäre fällig, fällt aber aus (429) → Atelier bleibt
        html_quelle.interval_minutes = 0
        selten.fehler = sources.RateLimited("429")
        _scan(settings, store)
        assert "Atelier" in _kinos(store, item.uid)
        store.db.execute("UPDATE source_status SET paused_until = NULL")  # Pause nach 429 für den Test aufheben

        # Scan 5: die HTML-Quelle läuft und meldet den Film nicht mehr → Atelier fällt weg
        selten.fehler, selten.shows = None, []
        _scan(settings, store)
        assert _kinos(store, item.uid) == ["CineStar Bremen", "CineStar Mainz"]
        assert "−Atelier" in store.draft_by_uid(item.uid)["hinweise"][-1]


def test_kino_traegt_seine_quelle():
    [item] = kp.aggregate_shows([kp.Show("Jailer 2", "Atelier", "Düsseldorf", "DE", start=_termin(1))],
                                quelle="Filmkunstkinos")
    assert item.facts["kinos"][0]["quelle"] == "Filmkunstkinos"
