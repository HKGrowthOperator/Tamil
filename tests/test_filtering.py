import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from news_radar import filtering, sources
from news_radar.agents import relevance
from news_radar.config import Source, load_settings
from news_radar.sources import NewsItem

NOW = datetime(2026, 10, 16, 12, tzinfo=timezone.utc)


@pytest.fixture
def settings(monkeypatch):
    monkeypatch.setenv("WP_USER", "")
    return load_settings()


def item(title, summary="", source="Test", hours_old=1, **kw):
    return NewsItem(title=title, url=f"https://e.com/{abs(hash(title))}", summary=summary, source=source,
                    published=NOW - timedelta(hours=hours_old), **kw)


def test_dach_score_title_city_wins(settings):
    assert filtering.dach_score(item("Tamilen in Paderborn feiern", "auch in Köln"), settings.regions) == (4, "Paderborn")
    assert filtering.dach_score(item("Pongal-Fest", "Tempel in Hamm, Deutschland"), settings.regions) == (2, "Hamm")
    assert filtering.dach_score(item("Tamil film", "shown in Zurich"), settings.regions)[1] == "Zürich"
    assert filtering.dach_score(item("Neues aus Chennai", "Indien"), settings.regions) == (0, "")


def test_exact_terms_case_sensitive(settings):
    assert filtering.dach_score(item("Wir essen tamilisch", "bern ist kein ort"), settings.regions) == (0, "")
    assert filtering.dach_score(item("Tempelfest in Essen", ""), settings.regions) == (3, "Essen")


def test_tamil_terms_substring(settings):
    assert filtering.score_item(item("தமிழர்கள் சுவிஸ்"), {"தமிழ்": 3, "சுவிஸ்": 3}) == 12
    assert filtering.dach_score(item("சுவிஸ் தமிழர் தகவல்"), settings.regions) == (1, "Schweiz")


def test_select_two_tier_threshold(settings):
    with_dach = item("Tamilischer Abend in Luzern", "Kultur")  # tamilisch 8 + Luzern
    without = item("Tamilischer Abend", "Kultur irgendwo")  # tamilisch 8 → reicht auch ohne DACH (min_score 4)
    weak_dach = item("Konzert in Luzern", "tamil Musik")  # konzert 2 + tamil 3 = 5? -> tamil im Text 3, konzert Titel 2 = 5
    weak_nodach = item("Konzert", "tamil Musik")  # 2+3 = 5 ≥ 4 → passt
    very_weak_dach = item("Fest in Luzern", "mit Musik")  # 0 Punkte, DACH → reicht nicht (min_score_dach 2)
    picked = filtering.select([with_dach, without, weak_dach, weak_nodach, very_weak_dach], settings, set(), [], now=NOW)
    titles = [p.title for p in picked]
    assert very_weak_dach.title not in titles and with_dach.title in titles
    assert titles[0] == with_dach.title  # DACH zuerst
    assert picked[0].dach_score == 3 and picked[0].ort == "Luzern"


def test_select_bypasses_keywords_for_kino_and_event_kind(settings):
    kino = item("„Jailer 2“ läuft in 3 Kinos", "CineStar Mainz", source="CineStar", kind="kino", hours_old=0)
    event = item("Vaango Pazhagalam", "Basel", source="Swiss Tamil Info · Events", kind="event", hours_old=100)
    picked = filtering.select([kino, event], settings, set(), [], now=NOW)
    assert {p.title for p in picked} == {kino.title, event.title}
    assert next(p for p in picked if p.kind == "kino").category_hint == "kino"
    assert next(p for p in picked if p.kind == "event").ort == "Basel"  # Stadt aus dem Text schlägt die Länder-Vorgabe
    only_country = item("Tamil Dream Night", "irgendwo", source="Swiss Tamil Info · Events", kind="event")
    assert filtering.select([only_country], settings, set(), [], now=NOW)[0].ort == "Schweiz"


def test_select_keeps_related_sources_and_respects_max_items(settings):
    a = item("Anirudh live in Köln: Tickets ab Freitag", "tamil", source="Google News DACH · WAZ")
    b = item("Anirudh live in Köln - Tickets ab Freitag!", "tamil", source="Google News DACH · Express")
    picked = filtering.select([a, b], settings, set(), [], now=NOW)
    assert len(picked) == 1 and picked[0].related[0].source.endswith("Express")

    settings.sources = [Source(name="Tamil-Portal", type="rss", url="https://x", min_score=0, max_items=2, kind="news")]
    items = [item(t, "ohne Stichwort", source="Tamil-Portal") for t in ("Pongal", "Deepavali", "Thaipusam", "Navaratri", "Theruvizha")]
    assert len(filtering.select(items, settings, set(), [], now=NOW)) == 2


def test_event_source_with_min_score_drops_unrelated_hits(settings):
    settings.sources = [Source(name="Eventfrog", type="html", url="https://x", kind="event", min_score=1)]
    good = item("Jailer 2 Tamil Kino Kloten", "", source="Eventfrog", kind="event")
    bad = item("Family Halloween", "Kinderfest", source="Eventfrog", kind="event")
    assert [p.title for p in filtering.select([good, bad], settings, set(), [], now=NOW)] == [good.title]


def test_select_filters_old_blocked_seen_and_blocklist(settings):
    old = item("Tamilen in Berlin", hours_old=200)
    blocked = item("Tamil casino bonus Berlin", "tamil")
    seen = item("Tamilen in Hamburg")
    picked = filtering.select([old, blocked, seen], settings, {seen.uid}, [], now=NOW)
    assert picked == []


def test_event_abroad_from_dach_source_is_dropped(settings):
    """Pilot 09.11.: Swiss Tamil Info berichtete über das Tamil Fest in Markham (Kanada) – das ist kein DACH-Termin."""
    markham = item("“தமிழ் தெருவிழா 2026” அறிமுக விழா!",
                   "கனடியத் தமிழர் பேரவையினால் (Canadian Tamil Congress) … City of Markham இல் நடைபெறவுள்ள Tamil Fest 2026",
                   source="Swiss Tamil Info · Events", kind="event")
    zuerich = item("Tamil Fest Zürich", "wie in London, jetzt auch in Zürich", source="Swiss Tamil Info · Events",
                   kind="event")
    schweiz = item("Tamil Dream Night", "irgendwo", source="Swiss Tamil Info · Events", kind="event")
    picked = filtering.select([markham, zuerich, schweiz], settings, set(), [], now=NOW)
    titel = {p.title for p in picked}
    assert markham.title not in titel and {zuerich.title, schweiz.title} <= titel


def test_tamil_month_names_are_dates():
    from news_radar import dates

    now = datetime(2026, 11, 9, tzinfo=dates.TZ)
    assert dates.parse_de_date("ஜூலை 13, 2026 அன்று", now).isoformat() == "2026-07-13"
    assert dates.parse_de_date("21 நவம்பர் 2026", now).isoformat() == "2026-11-21"
    assert [d.isoformat() for d in dates.alle_daten("ஓகஸ்ட் 22, 2026 முதல் செப்டம்பர் 3, 2026 வரை", now)] == \
        ["2026-08-22", "2026-09-03"]


# ---- Fund 09.11.: alte Berichte aus Termin-Rubriken und allgemeine Schweizer Meldungen -------------------------------

FIX = Path(__file__).parent / "fixtures"
FUND = datetime(2026, 11, 9, 20, tzinfo=timezone.utc)  # Zeitpunkt des Live-Berichts


def _quelle(settings, name):
    return next(s for s in settings.sources if s.name == name)


def _feed(settings, datei, quelle, now=FUND):
    return sources._feed_items((FIX / datei).read_bytes(), _quelle(settings, quelle), now=now)


def _mit_bezug(fall: int, **kw) -> NewsItem:
    """Echte Termine mit tamilischem Bezug (Fälle 3, 4, 5) als Meldung ihrer Quelle, ohne echtes Datum."""
    daten = json.loads((FIX / "radar_termine_mit_bezug.json").read_text(encoding="utf-8"))
    f = next(f for f in daten["faelle"] if f["fall"] == fall)
    return NewsItem(title=f["titel"], url=f["url"], summary=f["text"], source=f["quelle"], published=kw.pop("now", FUND),
                    language=f["language"], kind="event", facts=f["facts"], **kw)


def _nr(item) -> str:
    return item.url.rstrip("/").rsplit("/", 1)[-1]


def test_fund_alte_berichte_und_meldungen_ohne_bezug_fallen_raus(settings):
    events = _feed(settings, "swisstamilinfo_events.xml", "Swiss Tamil Info · Events")
    schweiz = _feed(settings, "swisstamilinfo_schweiz.xml", "Swiss Tamil Info · Schweiz")
    zaehler = Counter()
    picked = filtering.select(events + schweiz, settings, set(), [], now=FUND, zaehler=zaehler)
    raus = {_nr(i) for i in events + schweiz} - {"27129"}  # Fälle 8, 13, 14, 15 (Termine) und 9, 10, 12 (Schweiz)
    assert raus == {"22670", "22741", "22541", "22051", "28493", "28496", "28520"}
    assert not raus & {_nr(p) for p in picked}
    assert zaehler["ohne_bezug"] == 3  # Unfall, Polizei, Wahl


def test_fund_navaratri_faellt_nach_30_tagen_raus(settings):
    """Fall 11 erschien am 11.10.2026 und nennt kein Datum in der Zukunft. Am Tag des Fundes (09.11.) war er erst
    29 Tage alt, also noch unter RADAR_EVENT_MAX_ALTER_TAGE = 30; ab dem 31. Tag fällt er heraus."""
    assert settings.event_max_alter_tage == 30
    am_fundtag = _feed(settings, "swisstamilinfo_events.xml", "Swiss Tamil Info · Events")
    assert "27129" in {_nr(p) for p in filtering.select(am_fundtag, settings, set(), [], now=FUND)}
    spaeter = FUND + timedelta(days=2)
    items = _feed(settings, "swisstamilinfo_events.xml", "Swiss Tamil Info · Events", now=spaeter)
    zaehler = Counter()
    assert "27129" not in {_nr(p) for p in filtering.select(items, settings, set(), [], now=spaeter, zaehler=zaehler)}
    assert zaehler["termin_veraltet"] >= 1


def test_termine_mit_bezug_bleiben_drin(settings):
    basel = _mit_bezug(3)  # Eventfrog CH, Termin 21.11.2026, kein echtes Datum
    assert [p.title for p in filtering.select([basel], settings, set(), [], now=FUND)] == [basel.title]
    # strukturierter Termin in der Zukunft schlägt ein altes Veröffentlichungsdatum
    alt_mit_termin = _mit_bezug(3, source_published=FUND - timedelta(days=120))
    assert filtering.select([alt_mit_termin], settings, set(), [], now=FUND)
    # Termin ohne bekanntes echtes Datum: keine Altersprüfung
    for fall in (4, 5):
        assert filtering.select([_mit_bezug(fall)], settings, set(), [], now=FUND), fall


def test_alter_termin_bleibt_mit_datum_im_text_in_der_zukunft(settings):
    """Fall 5 kündigt die Tamil Dream Night am „ஒக்டோபர் 11“ an: 40 Tage vorher veröffentlicht, bleibt sie bis zum
    Termin drin; danach (Bericht alt, Datum vorbei) fällt sie heraus."""
    vorher = datetime(2026, 10, 5, 12, tzinfo=timezone.utc)
    ankuendigung = _mit_bezug(5, now=vorher, source_published=vorher - timedelta(days=40))
    assert filtering.select([ankuendigung], settings, set(), [], now=vorher)
    vorbei = _mit_bezug(5, source_published=vorher - timedelta(days=40))
    zaehler = Counter()
    assert filtering.select([vorbei], settings, set(), [], now=FUND, zaehler=zaehler) == []
    assert zaehler == Counter(termin_veraltet=1)


def test_ausland_sri_lanka_ohne_falsche_treffer(settings):
    quelle = "Swiss Tamil Info · Events"
    zuerich = item("Tamilen aus Sri Lanka feiern in Zürich", "Fest der Gemeinde", source=quelle, kind="event")
    news = item("Tamilen aus Sri Lanka feiern in Zürich", "Fest der Gemeinde", source="Google News CH · Tamilen")
    # யாழினி (Vorname) und யாழிசை (Musik) sind kein Jaffna: die Kurzform steht nur mit Punkt in der Liste
    yazhini = item("செல்வி யாழினியின் பரதநாட்டிய அரங்கேற்றம்", "யாழிசை நிகழ்வு", source=quelle, kind="event")
    kilinochchi = item("Tempeleröffnung in Kilinochchi", "Feier der Gemeinde", source=quelle, kind="event")
    picked = {p.title for p in filtering.select([zuerich, yazhini, kilinochchi], settings, set(), [], now=NOW)}
    assert picked == {zuerich.title, yazhini.title}
    assert filtering.select([news], settings, set(), [], now=NOW)[0].ort == "Zürich"
    # „சுவிட்சர்லாந்தில்“ ist ein DACH-Bezug: Fall 5 nennt indische Sänger, bleibt aber ein Schweizer Termin
    assert filtering.dach_score(_mit_bezug(5), settings.regions)[0] > 0


def test_laendernamen_heben_den_dach_bezug_nicht_auf(settings):
    """Review: „இலங்கை“ (Sri Lanka) steht in fast jedem Bericht der Diaspora. Nur Ortsnamen außerhalb von DACH machen
    einen Termin zum Auslandstermin, Ländernamen nicht."""
    gestern = FUND - timedelta(days=1)
    luzern = NewsItem(title="லுசேர்ன் நகரில் மாவீரர் நாள் 27.11.2026", url="https://swisstamilinfo.ch/40001/",
                      summary="இலங்கையில் உயிர்நீத்த மாவீரர்களை நினைவுகூரும் நிகழ்வு", source="Swiss Tamil Info · Events",
                      published=FUND, language="ta", kind="event", source_published=gestern)
    visa = NewsItem(title="இலங்கைத் தமிழர்களுக்கு புதிய விசா விதிகள்", url="https://swisstamilinfo.ch/40002/",
                    summary="தமிழ் அகதிகள் புதிய விதிகளை எதிர்கொள்கின்றனர்", source="Swiss Tamil Info · Schweiz",
                    published=gestern, language="ta", source_published=gestern)
    picked = {p.url: p for p in filtering.select([luzern, visa], settings, set(), [], now=FUND)}
    assert picked[luzern.url].ort == "Schweiz"
    assert picked[visa.url].ort == "Schweiz" and picked[visa.url].dach_score >= 1


def test_termin_mit_auslandsort_zaehlt_im_zaehler(settings):
    events = _feed(settings, "swisstamilinfo_events.xml", "Swiss Tamil Info · Events")
    ohne_alter = [e for e in events if e.source_published is None]  # Fälle 13, 14, 15: nur über den Ort
    zaehler = Counter()
    assert filtering.select(ohne_alter, settings, set(), [], now=FUND, zaehler=zaehler) == []
    assert zaehler == Counter(ausland=3)


def test_bezug_noetig_nur_fuer_die_markierte_quelle(settings):
    quelle = "Swiss Tamil Info · Schweiz"
    assert _quelle(settings, quelle).bezug_noetig
    tempel = item("சூரிச் அம்மன் கோவில் தேர்த்திருவிழா", "பக்தர்கள் கலந்து கொண்டனர்", source=quelle)
    tempel.published = FUND - timedelta(hours=1)
    unfall = _feed(settings, "swisstamilinfo_schweiz.xml", quelle)[0]
    zaehler = Counter()
    assert [p.title for p in filtering.select([tempel, unfall], settings, set(), [], now=FUND, zaehler=zaehler)] == \
        [tempel.title]
    assert zaehler == Counter(ohne_bezug=1)
    # dieselbe Meldung aus einer Quelle ohne die Option läuft wie bisher durch
    anders = NewsItem(title=unfall.title, url="https://e.com/unfall", summary=unfall.summary,
                      source="SwissTamilMedia · Community", published=unfall.published, language="ta")
    assert filtering.select([anders], settings, set(), [], now=FUND)
    # Ortsnamen zählen nicht als Bezug, auch nicht über die Grauzone
    kino = item("Neues Lichtspielhaus in Zürich", "Das Kino öffnet am Freitag", source=quelle)  # 1 Punkt: Grauzone
    kino.published = FUND - timedelta(hours=1)
    assert filtering.select([kino], settings, set(), [], now=FUND) == []
    assert relevance.grauzone([kino], settings, set(), set(), FUND) == []


# ---- Live-Fund 12.11.2026: Meldungen ohne DACH-Bezug wurden Storys (89, 91, 92) ----

FUND_1211 = json.loads((Path(__file__).parent / "fixtures" / "radar_ohne_dach_2026-11-12.json").read_text("utf-8"))


def _fund_items(gruppe):
    return [item(f["title"], f["summary"], source=f["source"]) for f in FUND_1211[gruppe]]


def test_fund_1211_ausland_und_fremdes_kino_ohne_dach_fallen_heraus(settings):
    """Tamil Nadu (Wirtschaft), Sri Lanka (Politik) und Telugu-Kino ohne DACH-Ort sind keine Story; Kollywood und die
    Gegenproben mit DACH-Bezug bleiben."""
    raus, kollywood, durch = _fund_items("raus"), _fund_items("kollywood"), _fund_items("durch")
    zaehler = Counter()
    picked = filtering.select(raus + kollywood + durch, settings, set(), [], now=NOW, zaehler=zaehler)
    titel = {p.title for p in picked}
    assert titel.isdisjoint(i.title for i in raus)
    assert {i.title for i in durch} <= titel
    # Kollywood ohne DACH bleibt (Rubrik Entertainment), auch wenn „Tamil Nadu“ im Text steht; je Quelle max_items (2)
    assert len(titel & {i.title for i in kollywood}) == 2
    assert zaehler["ausland"] == 2 and zaehler["fremdes_kino"] == 1



def test_quelle_mit_punkt_im_namen_und_verlag_wird_gefunden(settings):
    """Review 12.11.: „Google News EN · Kollywood · Verlag“ wurde als „Google News EN“ gesucht und nicht gefunden –
    max_items (2) griff nicht. Zuordnung über den längsten bekannten Namen, kein Treffer über ein bloßes Präfix."""
    titel = ["Rajinikanth begins shooting in Mysuru", "Anirudh tops the charts again", "Kollywood box office weekend"]
    kollywood = [item(t, "Tamil cinema", source=f"Google News EN · Kollywood · Verlag {n}") for n, t in enumerate(titel)]
    assert filtering.quelle_fuer(kollywood[0], settings).name == "Google News EN · Kollywood"
    assert filtering.quelle_fuer(item("x", source="Google News EN"), settings) is None
    assert filtering.quelle_fuer(item("x", source="Google News DACH · NZZ"), settings).name == "Google News DACH"
    assert filtering.quelle_fuer(item("x", source="Google News ENX · Kollywood"), settings) is None
    picked = filtering.select(kollywood, settings, set(), [], now=NOW)
    assert len(picked) == 2


# ---- Prüfung 12.11.2026: Nachbesserung der Ausland-Regel (P1–P3) ----

def _einzeln(items, settings):
    """Jede Meldung für sich durch select (max_items je Quelle und Dubletten spielen hier keine Rolle)."""
    zaehler = Counter()
    picked = [p for i in items for p in filtering.select([i], settings, set(), [], now=NOW, zaehler=zaehler)]
    return picked, zaehler


def test_fund_1211_diaspora_ohne_dach_ort_bleibt(settings):
    """P1: Adjektive und Varianten (German, Austrian, Schweizer), tamilische Schreibweisen (ஜேர்மனி) und deutschsprachige
    Treffer aus Google News DACH sind für die Ausland-Regel ein DACH-Hinweis – ohne [regions] laender zu ändern."""
    diaspora = _fund_items("diaspora")
    picked, zaehler = _einzeln(diaspora, settings)
    assert [p.title for p in picked] == [i.title for i in diaspora]
    assert zaehler["ausland"] == 0
    assert all(p.dach_score == 0 for p in picked)  # Ranking unverändert: nur die Ausland-Regel kennt die Hinweise


def test_fund_1211_ausland_bleibt_draussen_trotz_hinweisen(settings):
    """Gegenprobe zu P1: Die bisherigen Ausland-Fälle (englisch, ohne DACH-Hinweis) fallen weiter heraus."""
    picked, zaehler = _einzeln(_fund_items("raus"), settings)
    assert picked == [] and zaehler["ausland"] == 2 and zaehler["fremdes_kino"] == 1


def test_fund_1211_kollywood_quelle_und_stars_gelten_als_kino(settings):
    """P3a (Entscheidung 12.11.): Kollywood-Quelle oder Kollywood-/Star-Begriff reicht für die Kino-Ausnahme, auch wenn
    guess_category „news“ ergibt."""
    kollywood = _fund_items("kollywood_ohne_hinweis")
    assert all(filtering.guess_category(i, settings) == "news" for i in kollywood)
    picked, zaehler = _einzeln(kollywood, settings)
    assert [p.title for p in picked] == [i.title for i in kollywood]
    assert zaehler["ausland"] == 0
    # Star ohne Kollywood-Quelle: ebenfalls Kino; ohne Star und ohne Kollywood-Quelle bleibt es Ausland
    star = item("Ilaiyaraaja honoured by India", "Ilaiyaraaja honoured by India  DT Next", source="Tamil Guardian")
    assert filtering.ohne_dach_grund(star, settings, filtering.quelle_fuer(star, settings)) == ""
    politik = item("Chief Minister honoured by India", "Tamil Nadu Chief Minister honoured", source="Tamil Guardian")
    assert filtering.ohne_dach_grund(politik, settings, filtering.quelle_fuer(politik, settings)) == "ausland"


def test_fund_1211_verlagsname_ist_kein_bezug(settings):
    """P3b: „The Hindu“ im Google-News-Anriss ist der Verlag, kein tamilischer Bezug („hindu“ in [bezug] terms)."""
    picked, zaehler = _einzeln(_fund_items("fremdes_kino_verlag"), settings)
    assert picked == [] and zaehler["fremdes_kino"] == 1


def test_fund_1211_grauzone_wendet_ausland_regel_an(settings):
    """P2: Was select als Ausland verwirft, geht auch bei Score 2–3 nicht über die Grauzone an Haiku."""
    grau = _fund_items("grauzone_raus")
    assert all(2 <= filtering.score_item(i, settings.keywords) <= 3 for i in grau)
    picked, zaehler = _einzeln(grau, settings)
    assert picked == [] and zaehler["ausland"] == 2
    assert relevance.grauzone(_fund_items("grauzone_raus"), settings, set(), set(), NOW) == []


def test_fund_1211_genf_ist_dach_hinweis(settings):
    """Zweite Prüfung 12.11.: Genf steht nicht in [regions.staedte] (Ranking), ist für die Ausland-Regel aber DACH –
    UNHRC-Sitzungen zu Sri Lanka mit Kundgebungen der Diaspora."""
    genf = [item("Tamils rally in Geneva as UNHRC debates Sri Lanka",
                 "Hundreds of Tamils gathered at the Broken Chair in Geneva", source="Tamil Guardian"),
            item("Volker Turk urges Sri Lanka to act on accountability",
                 "The UN rights chief told the Human Rights Council in Geneva that Sri Lanka must act",
                 source="Tamil Guardian")]
    picked, zaehler = _einzeln(genf, settings)
    assert [p.title for p in picked] == [i.title for i in genf] and zaehler["ausland"] == 0


def test_fund_1211_starnamen_nur_als_ganzes_wort(settings):
    """Zweite Prüfung 12.11.: „vijay“ traf „Vijayan“, „ajith“ srilankische Namen. Für die Kollywood-Ausnahme zählen
    Starnamen nur als ganzes Wort, Ajith nur als „Ajith Kumar“; score_item bleibt unverändert."""
    raus = [item("Kerala CM Pinarayi Vijayan writes to Tamil Nadu on Mullaperiyar dam",
                 "Kerala CM Pinarayi Vijayan writes to Tamil Nadu on Mullaperiyar dam  The Hindu",
                 source="Google News DACH · The Hindu"),
            item("Ajith Nivard Cabraal indicted over bond scam",
                 "Former Central Bank governor of Sri Lanka Ajith Nivard Cabraal indicted", source="Tamil Guardian"),
            item("DIG Ajith Rohana orders crackdown in Jaffna",
                 "Police DIG Ajith Rohana orders crackdown on protests in Jaffna", source="Tamil Guardian")]
    for i in raus:
        assert filtering.ohne_dach_grund(i, settings, filtering.quelle_fuer(i, settings)) == "ausland", i.title
    star = item("Rajinikanth meets Tamil Nadu Chief Minister", "Rajinikanth meets Tamil Nadu Chief Minister",
                source="Tamil Guardian")
    assert filtering.ohne_dach_grund(star, settings, filtering.quelle_fuer(star, settings)) == ""
    ajith = item("Ajith Kumar meets Tamil Nadu Chief Minister", "Ajith Kumar meets Tamil Nadu Chief Minister",
                 source="Tamil Guardian")
    assert filtering.ohne_dach_grund(ajith, settings, filtering.quelle_fuer(ajith, settings)) == ""


def test_fund_1211_tamile_einzahl_ist_deutsch(settings):
    """Zweite Prüfung 12.11.: „Tamile“ (Einzahl) ist ein deutsches Wort; die Meldung bleibt als DACH-Presse drin."""
    tamile = item("Abgewiesener Tamile in Sri Lanka verhaftet",
                  "Abgewiesener Tamile in Sri Lanka verhaftet  20 Minuten", source="Google News DACH · 20 Minuten")
    picked, zaehler = _einzeln([tamile], settings)
    assert [p.title for p in picked] == [tamile.title] and zaehler["ausland"] == 0


def test_fund_1211_romandie_ist_dach_hinweis(settings):
    """Dritte Prüfung 12.11.: Orte der Romandie mit großer tamilischer Community zählen für die Ausland-Regel als DACH
    (nicht im Ranking). „Sion“ nur als ganzes Wort: als Wortanfang träfe es „Sionist“ und „Sionkowski“."""
    bleiben = [item("Tamil association in Lausanne celebrates Pongal", "Tamil families from Sri Lanka gathered",
                    source="Tamil Guardian"),
               item("Tamil temple opens in Sion", "Tamils from Sri Lanka built the temple in Sion",
                    source="Tamil Guardian"),
               item("Tamils of Suisse romande protest Sri Lanka visit", "Tamils from Fribourg and Neuchâtel joined",
                    source="Tamil Guardian")]
    picked, zaehler = _einzeln(bleiben, settings)
    assert [p.title for p in picked] == [i.title for i in bleiben] and zaehler["ausland"] == 0
    for t in ("Sionist groups protest Sri Lanka visit", "Sionkowski urges Sri Lanka to act"):
        raus = item(t, t, source="Tamil Guardian")
        assert filtering.ohne_dach_grund(raus, settings, None) == "ausland", t
