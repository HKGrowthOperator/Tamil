"""Terminquelle Vizha (vizha.app, Veranstaltungskalender der tamilischen Diaspora), ohne Netz.

Die Fixtures sind Auszüge der echten Seiten vom 12.11.2026 (Titel, JSON-LD, Links auf /events/):
- Länderseiten /de/events und /ch/events: Linklisten (auf der DE-Seite stehen auch Termine in Schweden),
- Terminseiten mit JSON-LD vom Typ Event: Zürich Tamil Sangam Deepavali (CH, 14.11.), Düsseldorf Tamil Sangam
  Deepavali (DE, 15.11.), Stockholm Smash Fest (SE), Tamil Halloween Party Dortmund (DE, 31.10., vorbei) und
  Oslo Maaveerar Cup (NO, Gedenken mit LTTE-Bezug)."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from news_radar import sources
from news_radar.config import Source, load_settings

FIX = Path(__file__).parent / "fixtures"
STAND = datetime(2026, 11, 12, 12, tzinfo=timezone.utc)  # Abruf der Fixtures
VIZHA = "Vizha · Termine DACH"
SEITEN = {
    "https://vizha.app/de/events": "vizha_de_events.html",
    "https://vizha.app/ch/events": "vizha_ch_events.html",
    "https://vizha.app/events/zurich-tamil-sangam-deepavali-celebration-2026": "vizha_event_zurich_deepavali.html",
    "https://vizha.app/events/dusseldorf-tamil-sangam-deepavali-2026": "vizha_event_duesseldorf_deepavali.html",
    "https://vizha.app/events/stockholm-smash-fest-4-sweden-badminton-open-2026": "vizha_event_stockholm_badminton.html",
    "https://vizha.app/events/tamil-halloween-party-is-back-2026": "vizha_event_dortmund_halloween.html",
}


class Antwort:
    def __init__(self, datei: str | None):
        self.status_code = 200 if datei else 404
        self.content = (FIX / datei).read_bytes() if datei else b"not found"
        self.headers = {"Content-Type": "text/html; charset=utf-8"}

    def iter_content(self, size):
        yield self.content

    def raise_for_status(self):
        pass

    def close(self):
        pass


@pytest.fixture
def settings(monkeypatch):
    for var in ("WP_USER", "WP_APP_PASSWORD", "NEWSAPI_KEY", "GNEWS_TOKEN"):
        monkeypatch.setenv(var, "")
    return load_settings()


@pytest.fixture
def aufrufe(monkeypatch):
    liste = []

    def get(url, **kw):
        liste.append(url)
        return Antwort(SEITEN.get(url))  # alle anderen Terminseiten: 404

    monkeypatch.setattr(sources.requests, "get", get)
    return liste


def _quelle(settings, **params) -> Source:
    q = next(q for q in settings.alle_quellen if q.name == VIZHA)
    return Source(name=q.name, type=q.type, url=q.url, kind=q.kind, language=q.language, params={**q.params, **params})


def test_vizha_ist_registriert(settings):
    q = next(q for q in settings.alle_quellen if q.name == VIZHA)
    assert (q.type, q.url, q.kind, q.country) == ("jsonld_events", "https://vizha.app", "event", "")
    assert q.enabled and q.robots == "erlaubt" and q.betreiber and q.notiz and q.interval_minutes == 360
    assert q.params["listen"] == ["/de/events", "/ch/events"]
    assert q.params["laender"] == ["DE", "AT", "CH"] and q.params["max_abrufe"] == 40
    assert "jsonld_events" in sources.FETCHERS


def test_nur_kommende_termine_in_dach_mit_ort_und_ortszeit(settings, aufrufe):
    with pytest.raises(sources.Teilausfall) as teil:  # die übrigen Terminseiten fehlen in den Fixtures (404)
        sources.FETCHERS["jsonld_events"](_quelle(settings), settings, now=STAND)
    items = teil.value.items
    # Stockholm (SE) steht auf beiden Listen, liegt aber nicht in DACH. Reihenfolge: nächster Termin zuerst
    assert [(i.title, i.facts["event_datum"]) for i in items] == [
        ("Zurich Tamil Sangam Deepavali Celebration 2026", "2026-11-14"),
        ("Düsseldorf Tamil Sangam Deepavali 2026", "2026-11-15"),
    ]
    zuerich, duesseldorf = items
    assert all(i.kind == "event" and i.source == VIZHA for i in items)
    assert zuerich.url == "https://vizha.app/events/zurich-tamil-sangam-deepavali-celebration-2026"
    assert zuerich.ort == "Embrach"
    assert zuerich.facts["event_ort"] == "Embrach Gemeinde Saal, Dorfstrasse 9, 8424 Embrach, Schweiz"
    assert zuerich.summary.startswith("14.11.2026, 14:30 Uhr")  # 13:30 UTC = 14:30 Ortszeit
    assert "தீபாவளி கொண்டாட்டம்" in zuerich.summary  # alternateName (Tamil) für Suche und Gedenktermin-Sperre
    assert duesseldorf.facts["event_ort"] == "Am Schönenkamp 1, 40599 Düsseldorf, Deutschland"
    assert duesseldorf.summary.startswith("15.11.2026, 13:30 Uhr")
    assert duesseldorf.facts["event_ende"] == "2026-11-15"
    # Listen zuerst, danach jede kommende Terminseite (ItemList der Liste) genau einmal, im Wechsel DE/CH;
    # vergangene Termine, die nur als Link auf der Seite stehen (Halloween in Dortmund), werden gar nicht geholt
    assert aufrufe[:2] == ["https://vizha.app/de/events", "https://vizha.app/ch/events"]
    assert aufrufe[2:5] == ["https://vizha.app/events/dusseldorf-tamil-sangam-deepavali-2026",
                            "https://vizha.app/events/pechu-potti-2026-zurich-2026",
                            "https://vizha.app/events/stockholm-smash-fest-4-sweden-badminton-open-2026"]
    assert len(aufrufe) == len(set(aufrufe)) == 2 + 16 + 20 - 2
    assert "https://vizha.app/events/tamil-halloween-party-is-back-2026" not in aufrufe
    assert "Terminseiten" in str(teil.value)


def test_hoechstens_max_abrufe_terminseiten_je_lauf(settings, aufrufe):
    with pytest.raises(sources.Teilausfall) as teil:  # Pechu Potti Zürich: nicht in den Fixtures (404)
        sources.FETCHERS["jsonld_events"](_quelle(settings, max_abrufe=3), settings, now=STAND)
    assert len(aufrufe) == 2 + 3
    assert [i.title for i in teil.value.items] == ["Düsseldorf Tamil Sangam Deepavali 2026"]


def test_links_aus_vergangenen_jahren_werden_nicht_abgerufen(settings, aufrufe):
    spaeter = datetime(2027, 3, 1, 12, tzinfo=timezone.utc)
    with pytest.raises(sources.Teilausfall) as teil:
        sources.FETCHERS["jsonld_events"](_quelle(settings), settings, now=spaeter)
    assert teil.value.items == []
    # nur Termine, deren Slug auf 2027 oder später endet, werden noch geholt, z. B. „vanakkam-europa-2027“;
    # „tamil-nite-frankfurt-2026-countdown-to-2027-2026“ (Silvester 2026) nicht mehr
    abgerufen = aufrufe[2:]
    assert len(abgerufen) == 9 and all("2027" in u or "2029" in u for u in abgerufen)


def test_links_ohne_itemlist_aus_der_seite():
    """Ohne ItemList im JSON-LD gelten die Links auf /events/ (dann auch vergangene, z. B. Halloween)."""
    text = (FIX / "vizha_de_events.html").read_text(encoding="utf-8")
    mit = sources.termin_links(text, "https://vizha.app/de/events", "/events/")
    assert len(mit) == 16 and mit[0] == "https://vizha.app/events/dusseldorf-tamil-sangam-deepavali-2026"
    ohne = sources.termin_links(text.replace('"@type":"ItemList"', '"@type":"Thing"'),
                                "https://vizha.app/de/events", "/events/")
    assert len(ohne) == 22 and "https://vizha.app/events/tamil-halloween-party-is-back-2026" in ohne


def test_vergangener_termin_faellt_heraus(settings):
    quelle = _quelle(settings)
    text = (FIX / "vizha_event_dortmund_halloween.html").read_text(encoding="utf-8")
    url = "https://vizha.app/events/tamil-halloween-party-is-back-2026"
    assert sources.jsonld_termin(text, url, quelle, settings, now=STAND) is None  # 31.10. bis 1.11., vorbei
    item = sources.jsonld_termin(text, url, quelle, settings, now=datetime(2026, 10, 31, 20, tzinfo=timezone.utc))
    assert item.facts["event_datum"] == "2026-10-31" and item.facts["event_ende"] == "2026-11-01"
    assert item.summary.startswith("31.10.2026, 23:00 Uhr bis 01.11.2026")


def test_termin_ausserhalb_dach_faellt_heraus(settings):
    text = (FIX / "vizha_event_stockholm_badminton.html").read_text(encoding="utf-8")
    url = "https://vizha.app/events/stockholm-smash-fest-4-sweden-badminton-open-2026"
    assert sources.jsonld_termin(text, url, _quelle(settings), settings, now=STAND) is None
    assert sources.jsonld_termin(text, url, _quelle(settings, laender=["SE"]), settings, now=STAND) is not None


def test_gedenktermin_wird_nie_automatisch_story(settings, aufrufe):
    """Oslo Maaveerar Cup (echte Seite): Gedenken mit LTTE-Bezug ([blocklist] termine) fällt auch dann heraus, wenn
    das Land zugelassen wäre."""
    quelle = _quelle(settings, laender=["NO"])
    text = (FIX / "vizha_event_oslo_maaveerar.html").read_text(encoding="utf-8")
    url = "https://vizha.app/events/oslo-maaveerar-cup-2026"
    vorher = datetime(2026, 10, 20, 12, tzinfo=timezone.utc)
    assert sources.jsonld_termin(text, url, quelle, settings, now=vorher) is None
    # Gegenprobe: dieselbe Seite ohne Sperrbegriffe wäre ein Termin
    ohne = text.replace("Maaveerar", "Winter").replace("மாவீரர்", "குளிர்கால")
    item = sources.jsonld_termin(ohne, url, quelle, settings, now=vorher)
    assert item is not None and item.facts["event_datum"] == "2026-10-31"


def test_mitternacht_gilt_als_termin_ohne_uhrzeit(settings):
    """Live-Probe 12.11.: „Europe-wide Indoor Football Tournament – Bern“ steht mit 00:00 Ortszeit im Kalender – das ist
    ein Platzhalter für „Uhrzeit offen“, kein Beginn um Mitternacht."""
    text = (FIX / "vizha_event_zurich_deepavali.html").read_text(encoding="utf-8")
    text = text.replace("2026-11-14T13:30:00.000Z", "2026-11-14T23:00:00.000Z")  # = 15.11. 00:00 Ortszeit
    url = "https://vizha.app/events/zurich-tamil-sangam-deepavali-celebration-2026"
    item = sources.jsonld_termin(text, url, _quelle(settings), settings, now=STAND)
    assert item.facts["event_datum"] == "2026-11-15" and item.summary.startswith("15.11.2026 · ")


# ---- Gedenkturniere ohne die alten Sperrbegriffe (Vizha-Probe 12.11.2026, Entscheidung Hauptsitzung) ----------

GEDENKTURNIERE = {
    "vizha_event_dormagen_thamilselvan_cup.html": "https://vizha.app/events/br-s-p-thamilselvan-memorial-cup-2026",
    "vizha_event_rafz_kiddu_cup.html": "https://vizha.app/events/colonel-kiddu-cup-2027-adults-2027",
    "vizha_event_seon_kiddu_cup_junior.html": "https://vizha.app/events/colonel-kiddu-cup-junior-2027",
}


@pytest.mark.parametrize("datei", sorted(GEDENKTURNIERE))
def test_gedenkturniere_werden_nie_automatisch_story(settings, datei):
    text = (FIX / datei).read_text(encoding="utf-8")
    assert sources.jsonld_termin(text, GEDENKTURNIERE[datei], _quelle(settings), settings, now=STAND) is None
    # Gegenprobe: ohne die Namen wäre es ein gewöhnliches Turnier in DACH
    ohne = (text.replace("Thamilselvan", "Rhein").replace("Kiddu", "Winter").replace("BR.S.P.", "")
            .replace("பிரிகேடியர் சு.ப. தமிழ்ச்செல்வன் ", ""))
    assert sources.jsonld_termin(ohne, GEDENKTURNIERE[datei], _quelle(settings), settings, now=STAND) is not None


def test_deepavali_und_cricket_ohne_gedenkbezug_bleiben(settings):
    zuerich = (FIX / "vizha_event_zurich_deepavali.html").read_text(encoding="utf-8")
    url = "https://vizha.app/events/zurich-tamil-sangam-deepavali-celebration-2026"
    assert sources.jsonld_termin(zuerich, url, _quelle(settings), settings, now=STAND) is not None
    cricket = (FIX / "vizha_event_manchester_cricket.html").read_text(encoding="utf-8")
    url = "https://vizha.app/events/nta-40th-anniversary-inter-region-indoor-cricket-championshi-2026"
    vorher = datetime(2026, 10, 20, 12, tzinfo=timezone.utc)
    assert sources.jsonld_termin(cricket, url, _quelle(settings, laender=["GB"]), settings, now=vorher) is not None


def test_kittu_nur_als_ganzes_wort(settings):
    """„கிட்டு“/„Kittu“ trifft nur als ganzes Wort: „கிட்டும்“ („wird zuteil“) ist ein gewöhnliches Verb, „Kittur“ ein
    Ort."""
    from news_radar import filtering

    def termin(titel):
        return sources.NewsItem(title=titel, url="https://x.example/1", summary="", source="Test",
                                published=STAND, kind="event")

    assert filtering.gedenktermin(termin("கேணல் கிட்டு வெற்றிக் கிண்ணம் 2027"), settings)
    assert filtering.gedenktermin(termin("Colonel Kittu Cup 2027"), settings)
    assert filtering.gedenktermin(termin("Annai Poopathy Memorial Day"), settings)
    assert filtering.gedenktermin(termin("திலீபன் நினைவு நாள்"), settings)
    assert not filtering.gedenktermin(termin("தீபாவளி 2026 – எல்லோருக்கும் பரிசு கிட்டும்"), settings)
    assert not filtering.gedenktermin(termin("Kittur Rani Chennamma – Tanzabend"), settings)


# ---- Keine Telefonnummern, E-Mail-Adressen und Kontaktnamen im Anriss (Live-Probe 12.11.: Vanakkam Europa 2027) ----

def test_vanakkam_europa_ohne_kontakte(settings):
    """Echter Fall mit erfundenen Namen und Nummern im gleichen Format („• Name: 0176-12345678“)."""
    text = (FIX / "vizha_event_dortmund_vanakkam_europa.html").read_text(encoding="utf-8")
    item = sources.jsonld_termin(text, "https://vizha.app/events/vanakkam-europa-2027", _quelle(settings), settings,
                                 now=STAND)
    for weg in ("0157", "0176", "12345678", "Anbu", "Mala", "Kumar", "Contacts"):
        assert weg not in item.summary, weg
    # der Rest bleibt: Adresse mit PLZ und Hausnummern-Spanne, Website, Uhrzeit, Ort
    assert "Address: Burgweg 16-22, 44145 Dortmund, Germany" in item.summary
    assert "Website: https://www.vanakkameuropa.de" in item.summary and "2:30 PM CET" in item.summary
    assert item.summary.startswith("01.01.2027, 14:30 Uhr")


@pytest.mark.parametrize("roh, rein", [
    ("Infos unter +41 79 123 45 67.", "Infos unter."),
    ("Anmeldung bei +49 (0)176 1234 5678 oder vor Ort", "Anmeldung bei oder vor Ort"),
    ("Tickets 0041 79 123 45 67 · Eintritt frei", "Tickets · Eintritt frei"),
    ("Eintritt frei. Kontakt: Mala 0176 1234567", "Eintritt frei."),
    ("Kontakt: Mala Kumar: 0176/1234567", ""),
    ("Fragen an info@verein.example oder vor Ort", "Fragen an oder vor Ort"),
    ("Eintritt frei. E-Mail: kasse@verein.example", "Eintritt frei."),
    ("Hotline 044.123.45.67, sonst +94 77 123 4567", "Hotline, sonst"),
    ("Tel. +44 20 7946 0958", ""),
])
def test_kontakte_werden_entfernt(roh, rein):
    assert sources.ohne_kontakte(roh) == rein


@pytest.mark.parametrize("text", [
    "Am 15.11.2026 um 18:30 Uhr in 8302 Kloten, Eintritt CHF 25.–",
    "Samstag 05.12.2026, 08:00 Uhr, Burgweg 16-22, 44145 Dortmund",
    "Preisgeld 1.000 €, Startgebühr 100 €, Kategorien U09, U11, U13 (CHF 75/team)",
    "Zeitraum 2026-11-14 bis 2026-11-15, Saal 2, Instagram: @vanakkam_europa",
    "01067 Dresden, Hausnummer 12/14",
])
def test_kontaktfilter_laesst_daten_zeiten_preise_und_plz(text):
    assert sources.ohne_kontakte(text) == text


# ---- Befunde der unabhängigen Prüfung von 3a50746 ------------------------------------------------------------------

ZUERICH_URL = "https://vizha.app/events/zurich-tamil-sangam-deepavali-celebration-2026"


def _zuerich() -> str:
    return (FIX / "vizha_event_zurich_deepavali.html").read_text(encoding="utf-8")


@pytest.mark.parametrize("status", ["EventCancelled", "EventPostponed", "EventMovedOnline"])
def test_abgesagt_verschoben_oder_online_ist_kein_termin(settings, status):
    text = _zuerich().replace("https://schema.org/EventScheduled", f"https://schema.org/{status}")
    assert sources.jsonld_termin(text, ZUERICH_URL, _quelle(settings), settings, now=STAND) is None


def test_neu_angesetzt_bleibt_termin(settings):
    text = _zuerich().replace("https://schema.org/EventScheduled", "https://schema.org/EventRescheduled")
    assert sources.jsonld_termin(text, ZUERICH_URL, _quelle(settings), settings, now=STAND) is not None


@pytest.mark.parametrize("ersetzen", [
    # Sperrbegriff hinter Zeichen 900 der Beschreibung (der Anriss kürzt dort)
    ('"description":"Festival:', '"description":"' + "Kulturprogramm mit Tanz und Musik. " * 30
     + 'Maaveerar Naal. Festival:'),
    ('"alternateName":', '"keywords":"maaveerar","alternateName":'),
    ('"alternateName":', '"keywords":["sports","Maaveerar"],"alternateName":'),
    ('"alternateName":', '"organizer":{"@type":"Organization","name":"Maaveerar Committee"},"alternateName":'),
    ('"alternateName":', '"performer":[{"@type":"Person","name":"Band"},{"@type":"PerformingGroup",'
                         '"name":"Heroes Day Choir"}],"alternateName":'),
])
def test_gedenk_sperre_prueft_den_vollen_text(settings, ersetzen):
    alt, neu = ersetzen
    text = _zuerich()
    assert alt in text
    item = sources.jsonld_termin(text.replace(alt, neu, 1), ZUERICH_URL, _quelle(settings), settings, now=STAND)
    assert item is None


DUESSELDORF_URL = "https://vizha.app/events/dusseldorf-tamil-sangam-deepavali-2026"
PECHU_URL = "https://vizha.app/events/pechu-potti-2026-zurich-2026"


class Sonderantwort(Antwort):
    def __init__(self, status: int, location: str = ""):
        super().__init__(None)
        self.status_code = status
        if location:
            self.headers = {**self.headers, "Location": location}


def _netz(monkeypatch, sonder: dict):
    aufrufe = []

    def get(url, **kw):
        aufrufe.append(url)
        if url in sonder:
            return sonder[url]
        return Antwort(SEITEN.get(url))

    monkeypatch.setattr(sources.requests, "get", get)
    return aufrufe


def test_429_bei_einer_terminseite_bricht_ab_und_behaelt_die_gelesenen(settings, monkeypatch):
    aufrufe = _netz(monkeypatch, {PECHU_URL: Sonderantwort(429)})
    with pytest.raises(sources.Teilausfall) as teil:
        sources.FETCHERS["jsonld_events"](_quelle(settings), settings, now=STAND)
    assert [i.title for i in teil.value.items] == ["Düsseldorf Tamil Sangam Deepavali 2026"]
    assert "429" in str(teil.value)
    assert aufrufe[2:] == [DUESSELDORF_URL, PECHU_URL]  # danach nichts mehr


def test_weiterleitung_auf_fremden_host_wird_uebersprungen(settings, monkeypatch):
    fremd = "https://fremd.example/events/dusseldorf"
    _netz(monkeypatch, {DUESSELDORF_URL: Sonderantwort(301, fremd),
                        fremd: Antwort("vizha_event_duesseldorf_deepavali.html")})
    with pytest.raises(sources.Teilausfall) as teil:  # Pechu Potti: 404
        sources.FETCHERS["jsonld_events"](_quelle(settings, max_abrufe=2), settings, now=STAND)
    assert teil.value.items == []


def test_weiterleitung_auf_http_wird_uebersprungen(settings, monkeypatch):
    unsicher = "http://vizha.app/events/dusseldorf-tamil-sangam-deepavali-2026"
    _netz(monkeypatch, {DUESSELDORF_URL: Sonderantwort(301, unsicher),
                        unsicher: Antwort("vizha_event_duesseldorf_deepavali.html")})
    with pytest.raises(sources.Teilausfall) as teil:
        sources.FETCHERS["jsonld_events"](_quelle(settings, max_abrufe=2), settings, now=STAND)
    assert teil.value.items == []


@pytest.mark.parametrize("budget, frist", [(60, 45), (40, 25), (10, 5)])
def test_eigene_frist_bleibt_unter_dem_sammelbudget(settings, monkeypatch, budget, frist):
    """`fetch_all` verwirft eine Quelle, die nach `fetch_seconds` noch läuft: Die Frist des Kalenders endet mindestens
    15 s vorher (ein hängender Einzelabruf darf bis TIMEOUT = 12 s dauern), höchstens nach 45 s, mindestens 5 s."""
    fristen = []

    def get(url, **kw):
        fristen.append(kw.get("frist"))
        raise sources.net.HTTPError(404, url)

    monkeypatch.setattr(sources, "_get", get)
    monkeypatch.setattr(sources.time, "monotonic", lambda: 1000.0)
    settings.fetch_seconds = budget
    with pytest.raises(RuntimeError):
        sources.FETCHERS["jsonld_events"](_quelle(settings), settings, now=STAND)
    assert fristen and all(f == 1000.0 + frist for f in fristen)


def test_mehrere_events_das_der_seite_gewinnt(settings):
    """Ein weiteres Event-Objekt vor dem eigentlichen (z. B. „ähnliche Termine“) verdrängt den Termin der Seite nicht."""
    fremd = (FIX / "vizha_event_duesseldorf_deepavali.html").read_text(encoding="utf-8")
    block = fremd[fremd.index('<script type="application/ld+json">'):fremd.index("</script>") + len("</script>")]
    text = _zuerich().replace("</title>", "</title>\n" + block, 1)
    item = sources.jsonld_termin(text, ZUERICH_URL, _quelle(settings), settings, now=STAND)
    assert item.title == "Zurich Tamil Sangam Deepavali Celebration 2026"


def test_name_als_liste(settings):
    text = _zuerich().replace('"name":"Zurich Tamil Sangam Deepavali Celebration 2026"',
                              '"name":["Zurich Tamil Sangam Deepavali Celebration 2026","Deepavali Zürich"]', 1)
    item = sources.jsonld_termin(text, ZUERICH_URL, _quelle(settings), settings, now=STAND)
    assert item.title == "Zurich Tamil Sangam Deepavali Celebration 2026"


@pytest.mark.parametrize("land, name", [
    ('"Switzerland"', "Schweiz"), ('"Schweiz"', "Schweiz"), ('"Germany"', "Deutschland"),
    ('"Deutschland"', "Deutschland"), ('"Österreich"', "Österreich"), ('"Austria"', "Österreich"),
    ('{"@type":"Country","name":"Switzerland"}', "Schweiz"),
])
def test_land_als_name(settings, land, name):
    text = _zuerich().replace('"addressCountry":"CH"', f'"addressCountry":{land}')
    item = sources.jsonld_termin(text, ZUERICH_URL, _quelle(settings), settings, now=STAND)
    assert item is not None and item.facts["event_ort"].endswith(", " + name)


def test_land_als_name_ausserhalb_dach(settings):
    text = _zuerich().replace('"addressCountry":"CH"', '"addressCountry":"Sweden"')
    assert sources.jsonld_termin(text, ZUERICH_URL, _quelle(settings), settings, now=STAND) is None


# ---- Gegenprüfung von 69e232d: Laufzeit des Kontaktfilters, Varianten der Gedenk-Namen ------------------------------

@pytest.mark.parametrize("text", [
    "a" * 200_000,  # ohne Leerzeichen
    "a." * 50_000,
    "A" * 200_000,  # Namensmuster („Name: 0176 …“)
    "0176 1234567 " + " •" * 50_000,  # Aufräumen nach einem Treffer
    "1." * 100_000,
    "+1 " * 60_000,
], ids=["a200k", "a-punkt50k", "A200k", "bullets50k", "1-punkt100k", "plus1-60k"])
def test_kontaktfilter_laeuft_linear(text):
    import time

    t0 = time.perf_counter()
    sources.ohne_kontakte(text)
    assert time.perf_counter() - t0 < 0.5


def test_beschreibung_wird_vor_dem_kontaktfilter_gekuerzt(settings, monkeypatch):
    laengen = []
    echt = sources.ohne_kontakte

    def messen(text):
        laengen.append(len(text))
        return echt(text)

    monkeypatch.setattr(sources, "ohne_kontakte", messen)
    text = _zuerich().replace('"description":"Festival:', '"description":"' + "x" * 20_000 + ' Festival:')
    item = sources.jsonld_termin(text, ZUERICH_URL, _quelle(settings), settings, now=STAND)
    assert item is not None and laengen and max(laengen) <= 3000


@pytest.mark.parametrize("titel", [
    "கேணல் கிட்டுவின் நினைவாக உதைபந்தாட்டம்",  # Genitiv
    "கிட்டுவுக்கு வணக்கம்",  # Dativ
    "Tamilselvan Memorial Cup", "Tamil Selvan Cup", "Tamilchelvan Gedenkturnier", "Thamil Selvan Trophy",
])
def test_varianten_der_gedenk_namen(settings, titel):
    from news_radar import filtering

    item = sources.NewsItem(title=titel, url="https://x.example/1", summary="", source="Test", published=STAND,
                            kind="event")
    assert filtering.gedenktermin(item, settings)
