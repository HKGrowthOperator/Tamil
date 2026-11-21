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


def _termin(stunde: int) -> datetime:
    """Vorstellungen morgen zu verschiedenen Uhrzeiten: derselbe Tag liegt immer in genau einer Kinowoche, und morgen
    immer in dieser oder der nächsten (die Aggregation rechnet mit der echten Uhr)."""
    morgen = datetime.now(kp.TZ).replace(minute=0, second=0, microsecond=0) + timedelta(days=1)
    return morgen.replace(hour=stunde)


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
    stuendlich = Programm([kp.Show("Jailer 2", "CineStar Mainz", "Mainz", "DE", start=_termin(19))])
    selten = Programm([kp.Show("Jailer 2", "Atelier", "Düsseldorf", "DE", start=_termin(21))])
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
        stuendlich.shows.append(kp.Show("Jailer 2", "CineStar Bremen", "Bremen", "DE", start=_termin(20)))
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


def test_teilausfall_liefert_neue_spielorte_zieht_aber_nichts_ab(settings, monkeypatch):
    """Ein Haus der Quelle fiel aus (kp.Teilausfall): neue Spielorte kommen dazu, bisherige der Quelle bleiben."""
    programm = Programm([kp.Show("Jailer 2", "CineStar Bremen", "Bremen", "DE", start=_termin(19))])
    monkeypatch.setitem(kp.PROVIDERS, "cinestar", programm)
    settings.sources = [Source(name="CineStar", type="kino", provider="cinestar")]
    with Store(settings.db_path) as store:
        [item] = sources.fetch_all(settings, store)
        store.insert_draft(_row(item.uid, item.title, typ="kino_termine", fakten=item.facts,
                                fingerprint=item.fingerprint, hinweise=[]))
        programm.fehler = kp.Teilausfall([kp.Show("Jailer 2", "CineStar Mainz", "Mainz", "DE", start=_termin(20))],
                                         "CineStar Bremen")
        [neu] = _scan(settings, store)
        assert neu.quellen_gelaufen == frozenset()  # Quelle gilt nicht als gelaufen
        assert _kinos(store, item.uid) == ["CineStar Bremen", "CineStar Mainz"]
        status = {s["name"]: s for s in store.source_status_all()}
        assert "Teilausfall" in (status["CineStar"]["error_msg"] or "")


def test_kino_traegt_seine_quelle():
    [item] = kp.aggregate_shows([kp.Show("Jailer 2", "Atelier", "Düsseldorf", "DE", start=_termin(19))],
                                quelle="Filmkunstkinos")
    assert item.facts["kinos"][0]["quelle"] == "Filmkunstkinos"


def test_bleibende_spielorte_ohne_kuenftigen_termin_oder_aktive_quelle_fallen_weg():
    jetzt = datetime.now(kp.TZ)
    gestern, morgen = (jetzt - timedelta(days=1)).isoformat(timespec="minutes"), _termin(19).isoformat(timespec="minutes")
    woche = kp.kino_week(jetzt.date())
    alt = {"woche": f"{woche[0]}-W{woche[1]:02d}", "kinos": [
        {"kino": "Vorbei", "stadt": "A", "quelle": "Selten", "termine": [gestern]},
        {"kino": "Teils", "stadt": "B", "quelle": "Selten", "termine": [gestern, morgen]},
        {"kino": "Laeuft", "stadt": "C", "quelle": "Selten", "termine": [], "von": (jetzt - timedelta(days=3)).date().isoformat()},
        {"kino": "Bald", "stadt": "D", "quelle": "Selten", "termine": [], "von": (jetzt + timedelta(days=2)).date().isoformat()},
        {"kino": "Abgeschaltet", "stadt": "E", "quelle": "Aus", "termine": [morgen]},
    ]}
    neu = sources.NewsItem("t", "https://x.example/k", "", "Kinoprogramm", datetime.now(kp.TZ), kind="kino",
                           facts={"kinos": [{"kino": "Neu", "stadt": "F", "quelle": "Oft", "termine": [morgen]}]},
                           quellen_gelaufen=frozenset({"Oft"}), quellen_aktiv=frozenset({"Oft", "Selten"}))
    fakten, _ = kp.vereinige_fakten(alt, neu)
    kinos = {k["kino"]: k for k in fakten["kinos"]}
    assert sorted(kinos) == ["Bald", "Laeuft", "Neu", "Teils"]  # „Laeuft“: Kinowoche des Entwurfs läuft noch
    assert kinos["Teils"]["termine"] == [morgen]  # vergangene Vorstellung gestrichen


def test_laufzeit_ab_faellt_nach_der_kinowoche_weg():
    jetzt = datetime.now(kp.TZ)
    alt = {"woche": "2026-W01", "kinos": [{"kino": "Laeuft", "stadt": "C", "quelle": "Selten", "termine": [],
                                           "von": (jetzt - timedelta(days=3)).date().isoformat()}]}
    neu = sources.NewsItem("t", "https://x.example/k", "", "Kinoprogramm", jetzt, kind="kino",
                           facts={"kinos": [{"kino": "Neu", "stadt": "F", "quelle": "Oft", "termine": []}]},
                           quellen_gelaufen=frozenset({"Oft"}), quellen_aktiv=frozenset({"Oft", "Selten"}))
    fakten, _ = kp.vereinige_fakten(alt, neu)
    assert [k["kino"] for k in fakten["kinos"]] == ["Neu"]
