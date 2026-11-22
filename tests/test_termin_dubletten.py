"""Termin-Dubletten zwischen Terminquellen (Befund 12.11.2026): Der Kalender des München Tamil Sangam (tribe_events,
„Diwali-2026“, Bürgerhaus Neukeferloh) und Vizha (jsonld_events, „MTS Diwali 2026“) liefern denselben Termin. Gleiches
Datum + ähnlicher Titel + verträglicher Ort = eine Story. Verschiedene Städte am selben Tag bleiben getrennt.

Die Vizha-Seite zum MTS-Termin liegt nicht als Fixture vor; sie wird aus der echten Düsseldorfer Seite gebaut (Titel,
Datum und Ort ersetzt, Struktur unverändert)."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from news_radar import sources
from news_radar.agents import cluster
from news_radar.config import Source, load_settings
from news_radar.store import Store
from news_radar.workflow import orchestrator, repo
from news_radar.workflow.fake import FakeAnthropic

FIX = Path(__file__).parent / "fixtures"
STAND = datetime(2026, 11, 12, 12, tzinfo=timezone.utc)
MTS = "München Tamil Sangam · Termine"
VIZHA = "Vizha · Termine DACH"
DUS_URL = "https://vizha.app/events/dusseldorf-tamil-sangam-deepavali-2026"
DUS_ORT = ('"location":{"@type":"Place","name":"Am Schönenkamp 1, 40599 Düsseldorf","address":{"@type":"PostalAddress",'
           '"streetAddress":"Am Schönenkamp 1, 40599 Düsseldorf","addressLocality":"Düsseldorf",'
           '"addressCountry":"DE"}}')


class Antwort:
    status_code = 200
    headers = {"Content-Type": "application/json; charset=UTF-8"}

    def __init__(self, datei):
        self.content = (FIX / datei).read_bytes()

    def iter_content(self, size):
        yield self.content

    def raise_for_status(self):
        pass

    def close(self):
        pass


@pytest.fixture
def settings(tmp_path, monkeypatch):
    for var in ("WP_URL", "WP_USER", "WP_APP_PASSWORD", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "GEMINI_API_KEY",
                "BILD_POOL_DIR", "NOTIFY_WEBHOOK_URL", "NEWSAPI_KEY", "GNEWS_TOKEN"):
        monkeypatch.setenv(var, "")
    s = load_settings()
    s.data_dir = tmp_path
    return s


def _quelle(settings, name):
    return next(q for q in settings.alle_quellen if q.name == name)


def mts_kalender(monkeypatch, settings) -> sources.NewsItem:
    monkeypatch.setattr(sources.requests, "get", lambda url, **kw: Antwort("tribe_events_muenchen_tamil_sangam.json"))
    items = sources.FETCHERS["tribe_events"](_quelle(settings, MTS), settings, now=STAND)
    assert [i.title for i in items] == ["Diwali-2026"]
    return items[0]


def vizha(settings, titel, datum, stadt, ort_name="", land="DE", slug="mts-diwali-2026-munchen-tamil-sangam-2026",
          jetzt=STAND):
    text = (FIX / "vizha_event_duesseldorf_deepavali.html").read_text(encoding="utf-8")
    url = f"https://vizha.app/events/{slug}"
    ort = ('"location":{"@type":"Place","name":"%s","address":{"@type":"PostalAddress","streetAddress":"%s",'
           '"addressLocality":"%s","addressCountry":"%s"}}' % (ort_name, ort_name, stadt, land))
    text = (text.replace("Düsseldorf Tamil Sangam Deepavali 2026", titel).replace(DUS_URL, url)
            .replace("2026-11-15T12:30:00.000Z", f"{datum}T12:30:00.000Z")
            .replace("2026-11-15T21:00:00.000Z", f"{datum}T21:00:00.000Z").replace(DUS_ORT, ort))
    q = _quelle(settings, VIZHA)
    item = sources.jsonld_termin(text, url, Source(name=q.name, type=q.type, url=q.url, kind=q.kind,
                                                   language=q.language, params=q.params), settings, now=jetzt)
    assert item is not None and item.title == titel and item.facts["event_datum"] == datum
    return item


def termin(titel, datum, stadt, url):
    return sources.NewsItem(title=titel, url=url, summary="", source="Test", published=STAND, kind="event", ort=stadt,
                            facts={"event_datum": datum, "event_ende": datum,
                                   "event_ort": f"{stadt}, Deutschland" if stadt else "Deutschland"})


# ---- Abgleich (rein) -----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("stadt,ort_name", [
    ("Neukeferloh", "Bürgerhaus Neukeferloh"),       # gleiche Stadt
    ("", ""),                                        # Vizha ohne Ort: nur das Land
    ("Grasbrunn", "Bürgerhaus Neukeferloh"),         # Gemeinde, der Ortsteil steht im Ort des anderen
])
def test_mts_kalender_und_vizha_sind_derselbe_termin(monkeypatch, settings, stadt, ort_name):
    a = mts_kalender(monkeypatch, settings)
    b = vizha(settings, "MTS Diwali 2026", "2026-11-21", stadt, ort_name)
    assert cluster.gleicher_termin(a, b) and cluster.gleicher_termin(b, a)


@pytest.mark.parametrize("titel", ["Deepavali Feier", "MTS Deepawali Celebration 2026", "Diwali Festival 2026",
                                   "DIWALI-2026"])
def test_schreibweisen_und_fuellwoerter(monkeypatch, settings, titel):
    a = mts_kalender(monkeypatch, settings)
    assert cluster.gleicher_termin(a, termin(titel, "2026-11-21", "Neukeferloh", "https://x.example/1"))


def test_anderes_datum_oder_anderer_anlass_bleibt_getrennt(monkeypatch, settings):
    a = mts_kalender(monkeypatch, settings)
    assert not cluster.gleicher_termin(a, termin("MTS Diwali 2026", "2026-11-22", "Neukeferloh", "https://x.example/1"))
    assert not cluster.gleicher_termin(a, termin("MTS Pongal 2026", "2026-11-21", "Neukeferloh", "https://x.example/2"))
    assert not cluster.gleicher_termin(a, termin("2026", "2026-11-21", "Neukeferloh", "https://x.example/3"))


def test_deepavali_in_verschiedenen_staedten_am_selben_tag_bleibt_getrennt(settings):
    # echte Titel aus vizha_de_events.html, alle auf den 7.11. gelegt (abgerufen am 1.11.)
    vorher = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)
    stuttgart = vizha(settings, "German Tamil Sangam Diwali Festival of Lights 2026", "2026-11-07", "Stuttgart",
                      "Stuttgart", slug="german-tamil-sangam-diwali-festival-of-lights-2026", jetzt=vorher)
    berlin = vizha(settings, "Diwali Thiruvizha 2026 Berlin Tamil Sangam", "2026-11-07", "Berlin", "Berlin",
                   slug="diwali-thiruvizha-2026-berlin-tamil-sangam-2026", jetzt=vorher)
    frankfurt = vizha(settings, "FTS Deepavali Celebration 2026", "2026-11-07", "Frankfurt am Main", "Frankfurt",
                      slug="fts-deepavali-celebration-2026", jetzt=vorher)
    for x, y in ((stuttgart, berlin), (berlin, frankfurt), (stuttgart, frankfurt)):
        assert not cluster.gleicher_termin(x, y)
    # Gegenprobe: dieselben Titel in derselben Stadt wären derselbe Termin
    gleich = termin("Deepavali 2026", "2026-11-07", "Stuttgart", "https://x.example/s")
    assert cluster.gleicher_termin(stuttgart, gleich)


# ---- im Scan: eine Story ---------------------------------------------------------------------------------------------

def _kontext(settings, store):
    return orchestrator.kontext(settings, store, client=FakeAnthropic(), fetch_text=lambda u: "", suche=lambda q: [])


def test_im_selben_scan_eine_story(monkeypatch, settings):
    a = mts_kalender(monkeypatch, settings)
    b = vizha(settings, "MTS Diwali 2026", "2026-11-21", "", "")
    with Store(settings.db_path) as store:
        z = cluster.zuordnen(_kontext(settings, store), [a, b])
    assert z[0].story_id is None and z[0].bezug is None
    assert z[1].bezug == 0


def test_spaeter_gemeldet_landet_in_der_bestehenden_story(monkeypatch, settings):
    a = mts_kalender(monkeypatch, settings)
    b = vizha(settings, "MTS Diwali 2026", "2026-11-21", "Neukeferloh", "Bürgerhaus Neukeferloh")
    with Store(settings.db_path) as store:
        sid = repo.story_anlegen(store, typ="event", titel=a.title, ort=a.ort, schluessel=cluster.schluessel(a))
        andere = repo.story_anlegen(store, typ="event", titel="Deepavali", ort="Berlin",
                                    schluessel="event:2026-11-21:berlin:deepavali")
        z = cluster.zuordnen(_kontext(settings, store), [b])
        assert z[0].story_id == sid and z[0].story_id != andere
        # Gegenprobe: Deepavali in Berlin am selben Tag findet die Berliner Story, nicht die Münchner
        berlin = termin("Berlin Tamil Sangam Deepavali 2026", "2026-11-21", "Berlin", "https://x.example/b")
        assert cluster.zuordnen(_kontext(settings, store), [berlin])[0].story_id == andere


def test_anderer_tag_findet_keine_story(monkeypatch, settings):
    a = mts_kalender(monkeypatch, settings)
    with Store(settings.db_path) as store:
        repo.story_anlegen(store, typ="event", titel=a.title, ort=a.ort, schluessel=cluster.schluessel(a))
        spaeter = termin("MTS Diwali 2026", "2026-11-28", "Neukeferloh", "https://x.example/n")
        assert cluster._termin_story(store, spaeter) is None  # (die Titelähnlichkeit danach bleibt unverändert)


# ---- Befunde der unabhängigen Prüfung von b24ad9c: kein Übermerging -------------------------------------------------
# Jeder Fall wird zweimal geprüft: gegen bestehende Storys (_termin_story) und im selben Scan (bezug).

def _ohne_ort(titel, datum="2026-11-21", url="https://x.example/neu"):
    return termin(titel, datum, "", url)


def _mit_ort(titel, stadt, voll, datum="2026-11-21", url="https://x.example/neu"):
    item = termin(titel, datum, stadt, url)
    item.facts["event_ort"] = voll
    return item


def _aus_quelle(item, quelle):
    item.source = quelle
    return item


def _story(store, item, status="neu"):
    return repo.story_anlegen(store, typ="event", titel=item.title, ort=item.ort, schluessel=cluster.schluessel(item),
                              status=status)


def _bezug_im_scan(settings, store, vorher: list, neu):
    return cluster.zuordnen(_kontext(settings, store), [*vorher, neu])[-1].bezug


NEGATIV = {
    # ohne Ort, nur ein Kernwort: keine Teilmengenregel gegen einen längeren Titel aus einer anderen Stadt
    "leerer Ort gegen andere Stadt": (
        [("Diwali Thiruvizha 2026 Berlin Tamil Sangam", "Berlin", "Berlin, Deutschland")],
        _ohne_ort("Deepavali 2026")),
    # ohne Ort und zwei passende Termine an dem Tag: mehrdeutig → keine Zuordnung
    "zwei Kandidaten": (
        [("Deepavali", "Stuttgart", "Stuttgart, Deutschland"), ("Deepavali", "Berlin", "Berlin, Deutschland")],
        _ohne_ort("Diwali 2026")),
    # Stadt nur im Straßennamen oder als Wortteil („Frankfurter Straße“, „Wiener Platz“)
    "Stadt im Straßennamen": (
        [("Deepavali Feier", "Frankfurt", "Saalbau, Frankfurt, Deutschland")],
        _mit_ort("Deepavali 2026", "Offenbach", "Stadthalle, Frankfurter Straße 5, 63065 Offenbach, Deutschland")),
    "Wiener Platz": (
        [("Deepavali Feier", "Wien", "Wien, Österreich")],
        _mit_ort("Deepavali 2026", "München", "Gasthaus am Platz, Wiener Platz 1, München, Deutschland")),
    # verschiedene Vereinskürzel, eine Seite ohne Ort
    "verschiedene Kürzel": (
        [("BTS Diwali 2026", "Berlin", "Berlin, Deutschland")],
        _ohne_ort("MTS Diwali 2026")),
}


@pytest.mark.parametrize("fall", sorted(NEGATIV))
def test_kein_uebermerging_gegen_bestehende_storys(settings, fall):
    vorher, neu = NEGATIV[fall]
    with Store(settings.db_path) as store:
        for n, (titel, stadt, voll) in enumerate(vorher):
            _story(store, _mit_ort(titel, stadt, voll, url=f"https://x.example/{n}"))
        assert cluster._termin_story(store, neu) is None


@pytest.mark.parametrize("fall", sorted(NEGATIV))
def test_kein_uebermerging_im_selben_scan(settings, fall):
    vorher, neu = NEGATIV[fall]
    alt = [_mit_ort(titel, stadt, voll, url=f"https://x.example/{n}") for n, (titel, stadt, voll) in enumerate(vorher)]
    with Store(settings.db_path) as store:
        assert _bezug_im_scan(settings, store, alt, neu) is None


def test_verworfene_story_zieht_keinen_termin_an(monkeypatch, settings):
    a = mts_kalender(monkeypatch, settings)
    b = vizha(settings, "MTS Diwali 2026", "2026-11-21", "Neukeferloh", "Bürgerhaus Neukeferloh")
    with Store(settings.db_path) as store:
        _story(store, a, status="verworfen")
        assert cluster._termin_story(store, b) is None


def test_kuerzel_nur_auf_einer_seite_stoert_nicht(settings):
    # Seit der Folgearbeit P3 braucht ein Kernwort ohne Ort einen Vereinshinweis: der Kalender trägt ihn als Quelle
    # („München Tamil Sangam“ ↔ MTS), wie im Live-Fall. Ohne diesen Hinweis: test_ein_kernwort_ohne_ort_ohne_…
    a = _aus_quelle(_mit_ort("Diwali-2026", "Neukeferloh", "Bürgerhaus Neukeferloh, Neukeferloh"),
                    "München Tamil Sangam · Termine")
    b = _ohne_ort("MTS Diwali 2026", url="https://x.example/b")
    assert cluster.gleicher_termin(a, b)
    assert not cluster.gleicher_termin(_ohne_ort("FTS Diwali 2026", url="https://x.example/f"), b)
    with Store(settings.db_path) as store:
        assert _bezug_im_scan(settings, store, [a], b) == 0
        sid = _story(store, a)
        repo.dokument_hinzufuegen(store, sid, url=a.url, quelle=a.source)
        assert cluster._termin_story(store, b) == sid


# ---- Folgearbeit P3 (Gegenprüfung von fd1aba5) -----------------------------------------------------------------------
# 1. Ein Kernwort ohne Ort reicht allein nicht: Deepavali ist an einem Tag in vielen Städten. Zusammengelegt wird nur
#    mit einem Vereinshinweis auf beiden Seiten (Kürzel „MTS“ ↔ Quelle „München Tamil Sangam“, oder dasselbe Kürzel).
# 2. Orte mit Endungen wie -ring, -weg, -damm sind keine Straßen (Pöring, Zorneding).
# 3. Titel ganz in Großbuchstaben: „ONAM“, „NEW“, „THAI“ sind keine Vereinskürzel.

def test_ein_kernwort_ohne_ort_ohne_vereinshinweis_bleibt_getrennt(settings):
    berlin = _mit_ort("Deepavali", "Berlin", "Berlin, Deutschland", url="https://x.example/b")
    neu = _ohne_ort("Diwali 2026")
    assert not cluster.gleicher_termin(berlin, neu) and not cluster.gleicher_termin(neu, berlin)
    with Store(settings.db_path) as store:
        assert _bezug_im_scan(settings, store, [berlin], neu) is None
        _story(store, berlin)
        assert cluster._termin_story(store, neu) is None


def test_ein_kernwort_ohne_ort_mit_vereinshinweis_der_quelle(settings):
    kalender = _aus_quelle(_mit_ort("Diwali-2026", "Neukeferloh", "Bürgerhaus Neukeferloh, Neukeferloh"),
                           "München Tamil Sangam · Termine")
    vizha_mts = _ohne_ort("MTS Diwali 2026", url="https://x.example/v")
    vizha_bts = _ohne_ort("BTS Diwali 2026", url="https://x.example/w")
    assert cluster.gleicher_termin(kalender, vizha_mts) and cluster.gleicher_termin(vizha_mts, kalender)
    assert not cluster.gleicher_termin(kalender, vizha_bts)
    with Store(settings.db_path) as store:
        assert _bezug_im_scan(settings, store, [kalender], vizha_mts) == 0
        sid = _story(store, kalender)
        repo.dokument_hinzufuegen(store, sid, url=kalender.url, quelle=kalender.source)
        assert cluster._termin_story(store, vizha_mts) == sid
        assert cluster._termin_story(store, vizha_bts) is None


def test_vereinsname_im_titel_zaehlt_als_hinweis():
    a = _mit_ort("Deepavali Feier des Hamburg Tamil Sangam", "Hamburg", "Hamburg, Deutschland")
    assert cluster.gleicher_termin(a, _ohne_ort("HTS Deepavali 2026", url="https://x.example/h"))
    assert not cluster.gleicher_termin(a, _ohne_ort("MTS Deepavali 2026", url="https://x.example/m"))


@pytest.mark.parametrize("voll_a", ["Pfarrsaal, Pöring, Zorneding", "Gasthof, Pöring-Nord, Zorneding"])
def test_orte_mit_strassenendung_sind_keine_strassen(voll_a):
    # Pöring ist ein Ortsteil von Zorneding: steht der Ortsteil im vollen Ort der anderen Seite, ist es derselbe Termin
    a = _mit_ort("Deepavali 2026", "Zorneding", voll_a)
    b = _mit_ort("Deepavali Feier", "Pöring", "Pfarrheim St. Martin, Pöring")
    assert cluster.ort_vertraeglich(a.ort, a.facts["event_ort"], b.ort, b.facts["event_ort"])
    assert cluster.gleicher_termin(a, b)


def test_strassen_bleiben_strassen():
    # Gegenprobe: Hausnummer oder „-straße“ machen einen Ortsbestandteil weiterhin zur Straße
    assert not cluster.ort_vertraeglich("Offenbach", "Frankfurter Ring 5, Offenbach", "Frankfurt", "Frankfurt")
    assert not cluster.ort_vertraeglich("München", "Wiener Platz 1, München", "Wien", "Wien, Österreich")
    assert cluster._ortsteile("Saal, Am Ring, Neuring") == ["saal", "neuring"]


@pytest.mark.parametrize("gross,klein", [
    ("ONAM 2026", "Onam Feier 2026"),
    ("TAMIL NEW YEAR 2026", "MTS Tamil New Year 2026"),
    ("THAI PONGAL VIZHA", "Thai Pongal Vizha 2026"),
])
def test_titel_in_grossbuchstaben(gross, klein):
    a = _mit_ort(gross, "München", "München, Deutschland")
    b = _mit_ort(klein, "München", "Saal, München", url="https://x.example/k")
    assert cluster.gleicher_termin(a, b) and cluster.gleicher_termin(b, a)


def test_kuerzel_in_grossbuchstaben_titeln_bleiben_kuerzel():
    a = _mit_ort("MTS DIWALI 2026", "München", "München, Deutschland")
    b = _mit_ort("BTS DIWALI 2026", "München", "München, Deutschland", url="https://x.example/b")
    assert cluster._kuerzel(a.title) == {"mts"} and not cluster.gleicher_termin(a, b)


# ---- Befunde der Code-Prüfung (Folgearbeit P3) -------------------------------------------------------------------------

def test_portalname_ist_kein_verein():
    # „Swiss Tamil Info“ ist ein Portal, kein Verein: kein Hinweis „sti“, keine Zusammenlegung über die Quelle
    a = _aus_quelle(_mit_ort("Deepavali 2026", "Zürich", "Zürich, Schweiz"), "Swiss Tamil Info · Events")
    b = _aus_quelle(_ohne_ort("Deepavali Abend Bern", url="https://x.example/s"), "Swiss Tamil Info · Events")
    assert cluster._vereine(a.title, (a.source,)) == set()
    assert not cluster.gleicher_termin(a, b)
    assert cluster._vereine("Deepavali", ("Düsseldorf Tamil Sangam · Termine",)) == {"dts"}


def test_kurze_kuerzel_in_grossbuchstaben_bleiben_kuerzel():
    a = _mit_ort("TYO DEEPAVALI 2026", "München", "München, Deutschland")
    b = _mit_ort("BTS Deepavali 2026", "München", "München, Deutschland", url="https://x.example/b")
    assert cluster._kuerzel(a.title) == {"tyo"} and not cluster.gleicher_termin(a, b)
    assert cluster._kuerzel("TAMIL NEW YEAR 2026") == set()
