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
