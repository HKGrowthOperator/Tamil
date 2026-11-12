"""Nachrichten einsammeln: RSS/Atom, Token-APIs, Google News je Region, WordPress-REST, HTML-Seiten, Kinoprogramme.

Jeder Quellentyp ist eine Funktion `(source, settings) -> list[NewsItem]` im Registry `FETCHERS`.
`fetch_all` fragt alle fälligen Quellen parallel mit Zeitbudget ab und merkt sich je Quelle Erfolg/Fehler.
"""

from __future__ import annotations

import calendar
import hashlib
import html
import json
import logging
import math
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable
from urllib.parse import parse_qsl, quote_plus, urlencode, urljoin, urlsplit, urlunsplit

import feedparser
import requests

from . import net
from .config import Settings, Source

log = logging.getLogger(__name__)

USER_AGENT = net.USER_AGENT
TIMEOUT = 12
_TAG_RE = re.compile(r"<[^>]+>")
_TRACKING = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid", "ref"}
COUNTRY_NAMES = {"DE": "Deutschland", "CH": "Schweiz", "AT": "Österreich"}
COUNTRY_NAMES_EN = {"DE": "Germany", "CH": "Switzerland", "AT": "Austria"}


class RateLimited(Exception):
    """HTTP 429 – Quelle eine Weile in Ruhe lassen."""


class Teilausfall(Exception):
    """Quelle lieferte nur einen Teil (z. B. ein Kino ohne Antwort): Meldungen gelten, die Quelle zählt nicht als
    vollständig gelaufen."""

    def __init__(self, items: list, grund: str):
        super().__init__(grund)
        self.items = items


@dataclass
class NewsItem:
    title: str
    url: str
    summary: str
    source: str
    published: datetime
    image_url: str = ""
    language: str = "de"
    score: int = 0
    category_hint: str = ""
    kind: str = "news"  # news | event | kino
    dach_score: int = 0
    ort: str = ""
    facts: dict | None = None
    fingerprint: str = ""
    uid_override: str = ""
    related: list["NewsItem"] = field(default_factory=list)
    # Echtes Veröffentlichungsdatum laut Quelle (None = unbekannt). Bei Termin-Quellen ist `published` der
    # Abrufzeitpunkt (Sortierung); erst dieses Feld zeigt, dass ein „neuer“ Treffer ein alter Bericht aus dem Archiv ist.
    source_published: datetime | None = None
    # Kino: Namen der Quellen, die in diesem Scan erfolgreich gelaufen sind (None = unbekannt). Nur sie dürfen einen
    # Spielort aus einem offenen Kino-Entwurf abziehen (kino_providers.vereinige_fakten).
    quellen_gelaufen: frozenset[str] | None = None
    quellen_aktiv: frozenset[str] | None = None  # eingeschaltete Quellen; Spielorte abgeschalteter fallen weg

    @property
    def uid(self) -> str:
        if self.uid_override:
            return self.uid_override
        return hashlib.sha1(normalize_url(self.url).encode()).hexdigest()


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(_TAG_RE.sub(" ", value or ""))).strip()


# Kontaktangaben in Termin-Anrissen (Live-Probe 12.11.: „Contacts: • Name: 0176-…“). Telefon: international (+41,
# 0049 …, auch „(0)“) oder national mit 0 und Vorwahl, Gruppen getrennt durch Leerzeichen . / -; erst ab 8 Ziffern
# eine Nummer (keine Daten, Uhrzeiten, Preise, Postleitzahlen). Ein Name direkt davor zählt mit, wenn er mit
# Doppelpunkt vor der Nummer steht („Mala: 0176 …“) oder einem Kontakt-Wort folgt („Kontakt: Mala 0176 …“).
_TELEFON = (r"(?:(?<![\w+@/.])(?:\+|00)\d{1,3}(?:[ ./-]?\(0\))?(?:[ ./-]?\d{1,5}){2,6}"
            r"|(?<![\w+@/.])0\d{2,5}(?:[ ./-]?\d{2,8}){1,4})(?!\w)")
_EMAIL = r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"
_KONTAKT_WORT = r"\b(?:Kontakte?|Contacts?|Tel\.?|Telefon|Phone|Mobil|Handy|WhatsApp|E-?Mail|Email)"
_NAME = r"[A-ZÄÖÜ][\w-]*(?: [A-ZÄÖÜ][\w-]*)?"
_KONTAKT_RE = re.compile(
    rf"{_KONTAKT_WORT}\s*:?\s*{_NAME}\s+(?P<a>{_TELEFON})"
    rf"|(?:{_KONTAKT_WORT}\s*:?\s*)?(?:{_NAME}\s*:\s*)?(?:(?P<b>{_TELEFON})|{_EMAIL})")
_KONTAKT_REST_RE = re.compile(rf"{_KONTAKT_WORT}\s*:\s*(?=[•|,;]|$)")


def ohne_kontakte(text: str) -> str:
    """Telefonnummern, E-Mail-Adressen und die Kontaktnamen direkt davor aus einem Anriss entfernen."""
    def ersetzen(m: re.Match) -> str:
        nummer = m.group("a") or m.group("b")
        if nummer and len(re.sub(r"\D", "", nummer)) < 8:
            return m.group(0)
        return " "

    neu = _KONTAKT_RE.sub(ersetzen, text or "")
    if neu == text:
        return text
    neu = _KONTAKT_REST_RE.sub(" ", neu)  # „Contacts:“ ohne Kontakte
    neu = re.sub(r"(?:\s*•)+\s*$", "", re.sub(r"(?:\s*•\s*){2,}", " • ", neu))
    neu = re.sub(r"\s+([.,;:!?])", r"\1", re.sub(r"\s+", " ", neu))
    return neu.strip(" •·–-,;")


def normalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    query = urlencode(sorted((k, v) for k, v in parse_qsl(parts.query) if k.lower() not in _TRACKING))
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower().removeprefix("www."), parts.path.rstrip("/"), query, ""))


def _parse_iso(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
    except ValueError:
        return datetime.now(timezone.utc)


class Conditional:
    """ETag/Last-Modified je Feed-URL für bedingte Abrufe (304 = unverändert, nichts Neues)."""

    def __init__(self, data: dict[str, tuple[str, str]] | None = None):
        self.data = dict(data or {})
        self.changed: dict[str, tuple[str, str]] = {}

    def get(self, url: str) -> tuple[str, str]:
        return self.data.get(url, ("", ""))

    def put(self, url: str, etag: str, last_modified: str) -> None:
        if (etag or last_modified) and self.data.get(url) != (etag, last_modified):
            self.data[url] = self.changed[url] = (etag, last_modified)


CONDITIONAL = Conditional()


def _get(url: str, conditional: bool = False, **kw) -> net.Fetched:
    """Abruf über net.safe_get (SSRF-Schutz, Größenlimit); 429 → RateLimited, sonst HTTPError bei 4xx/5xx."""
    kw.setdefault("timeout", TIMEOUT)
    etag, modified = CONDITIONAL.get(url) if conditional else ("", "")
    try:
        resp = net.safe_get(url, etag=etag, last_modified=modified, **kw)
    except net.HTTPError as exc:
        if exc.status == 429:
            raise RateLimited(url) from exc
        raise
    if conditional:
        CONDITIONAL.put(url, resp.etag, resp.last_modified)
    return resp


# ---- Registry ----------------------------------------------------------------

Fetcher = Callable[[Source, Settings], list[NewsItem]]
FETCHERS: dict[str, Fetcher] = {}


def fetcher(type_name: str):
    def wrap(fn: Fetcher) -> Fetcher:
        FETCHERS[type_name] = fn
        return fn

    return wrap


# ---- RSS / Atom -----------------------------------------------------------------

def _feed_items(content: bytes, source: Source, now: datetime | None = None) -> list[NewsItem]:
    feed = feedparser.parse(content)
    now = now or datetime.now(timezone.utc)
    items = []
    for entry in feed.entries:
        struct = entry.get("published_parsed") or entry.get("updated_parsed")
        echt = datetime.fromtimestamp(calendar.timegm(struct), tz=timezone.utc) if struct else None
        published = echt or now
        image = ""
        for media in entry.get("media_content", []) + entry.get("media_thumbnail", []):
            if media.get("url"):
                image = media["url"]
                break
        publisher = (entry.get("source") or {}).get("title") if isinstance(entry.get("source"), dict) else ""
        name = f"{source.name} · {publisher}" if publisher else source.name
        items.append(
            NewsItem(
                title=clean_text(entry.get("title", "")),
                url=entry.get("link", ""),
                summary=clean_text(entry.get("summary", ""))[:1200],
                source=name,
                published=published if source.kind == "news" else now,
                image_url=image,
                language=source.language,
                kind=source.kind,
                source_published=echt,
            )
        )
    return items


@fetcher("rss")
def fetch_rss(source: Source, settings: Settings) -> list[NewsItem]:
    resp = _get(source.url, conditional=True)
    if resp.not_modified:
        return []
    return _feed_items(resp.content, source)


# ---- Token-APIs -------------------------------------------------------------------

@fetcher("newsapi")
def fetch_newsapi(source: Source, settings: Settings) -> list[NewsItem]:
    if not settings.newsapi_key:
        log.info("Übersprungen (kein NEWSAPI_KEY): %s", source.name)
        return []
    resp = _get(
        "https://newsapi.org/v2/everything",
        params={"q": source.query, "language": source.language, "sortBy": "publishedAt", "pageSize": 30},
        headers={"X-Api-Key": settings.newsapi_key},
    )
    return [
        NewsItem(
            title=clean_text(a.get("title") or ""),
            url=a.get("url") or "",
            summary=clean_text(a.get("description") or a.get("content") or "")[:1200],
            source=f"{source.name} · {(a.get('source') or {}).get('name', '')}".strip(" ·"),
            published=_parse_iso(a.get("publishedAt")),
            image_url=a.get("urlToImage") or "",
            language=source.language,
            source_published=_parse_iso(a["publishedAt"]) if a.get("publishedAt") else None,
        )
        for a in resp.json().get("articles", [])
    ]


@fetcher("gnews")
def fetch_gnews(source: Source, settings: Settings) -> list[NewsItem]:
    if not settings.gnews_token:
        log.info("Übersprungen (kein GNEWS_TOKEN): %s", source.name)
        return []
    resp = _get(
        "https://gnews.io/api/v4/search",
        params={"q": source.query, "lang": source.language, "max": 25, "sortby": "publishedAt", "apikey": settings.gnews_token},
    )
    return [
        NewsItem(
            title=clean_text(a.get("title") or ""),
            url=a.get("url") or "",
            summary=clean_text(a.get("description") or a.get("content") or "")[:1200],
            source=f"{source.name} · {(a.get('source') or {}).get('name', '')}".strip(" ·"),
            published=_parse_iso(a.get("publishedAt")),
            image_url=a.get("image") or "",
            language=source.language,
            source_published=_parse_iso(a["publishedAt"]) if a.get("publishedAt") else None,
        )
        for a in resp.json().get("articles", [])
    ]


# ---- Google News je Region ------------------------------------------------------------

def gnews_url(query: str, country: str, lang: str = "de") -> str:
    return f"https://news.google.com/rss/search?q={quote_plus(query)}&hl={lang}&gl={country}&ceid={country}:{lang}"


def region_queries(source: Source, settings: Settings) -> list[str]:
    """Eine Google-News-RSS-URL je Land (de + en) und je Stadt; Reihenfolge = Priorität aus [regions]."""
    base = source.query or "(Tamil OR tamilisch OR Tamilen)"
    when = source.params.get("when", "2d")
    urls = [gnews_url(f"{base} {COUNTRY_NAMES[land]} when:{when}", land) for land in ("DE", "CH", "AT")]
    urls += [gnews_url(f"Tamil {COUNTRY_NAMES_EN[land]} when:{when}", land, "en") for land in ("DE", "CH", "AT")]
    urls += [gnews_url(f"{base} {stadt} when:{when}", land) for stadt, land in settings.regions.staedte.items()]
    return urls[: int(source.params.get("max_queries", 32))]


def rotation(n: int, per_run: int, minute_of_day: int, interval_minutes: int = 3) -> list[int]:
    """Indizes des aktuellen Teil-Laufs: alle ~(n/per_run) Läufe kommt jede Abfrage einmal dran."""
    if n <= per_run:
        return list(range(n))
    k = math.ceil(n / per_run)
    offset = (minute_of_day // max(1, interval_minutes)) % k
    return list(range(offset, n, k))


@fetcher("gnews_region")
def fetch_gnews_region(source: Source, settings: Settings) -> list[NewsItem]:
    urls = region_queries(source, settings)
    per_run = int(source.params.get("per_run", 6))
    now = datetime.now(timezone.utc)
    picks = rotation(len(urls), per_run, now.hour * 60 + now.minute)
    items: list[NewsItem] = []
    seen: set[str] = set()
    for n, idx in enumerate(picks):
        if n:
            time.sleep(float(source.params.get("pause", 0.8)))
        for item in _feed_items(_get(urls[idx]).content, source):
            if item.uid not in seen:
                seen.add(item.uid)
                items.append(item)
    return items


# ---- WordPress-REST ----------------------------------------------------------------

@fetcher("wp_json")
def fetch_wp_json(source: Source, settings: Settings) -> list[NewsItem]:
    params = {"per_page": 20, "orderby": "date", "order": "desc", **source.params}
    resp = _get(f"{source.url.rstrip('/')}/wp-json/wp/v2/{source.endpoint}", params=params)
    now = datetime.now(timezone.utc)
    items = []
    for post in resp.json():
        title = clean_text((post.get("title") or {}).get("rendered", ""))
        summary = clean_text((post.get("excerpt") or {}).get("rendered") or (post.get("content") or {}).get("rendered") or "")
        roh = post.get("date_gmt") or post.get("date")
        # Nur Beiträge haben ein Veröffentlichungsdatum; bei Kalendereinträgen (mec-events & Co.) ist es das Anlagedatum
        echt = _parse_iso(roh) if roh and source.endpoint == "posts" else None
        items.append(NewsItem(
            title=title, url=post.get("link", ""), summary=summary[:1200], source=source.name,
            published=_parse_iso(roh) if source.kind == "news" else now,
            language=source.language, kind=source.kind, source_published=echt,
        ))
    return items


def _kalender_zeit(roh) -> datetime | None:
    """„2026-05-31 10:00:00“ oder ISO „2026-05-31T10:00:00“ → naive Ortszeit; sonst None (mit Rohwert im Log)."""
    roh = str(roh or "").strip()
    if not roh:
        return None
    try:
        return datetime.strptime(roh[:16], "%Y-%m-%d %H:%M")
    except ValueError:
        pass
    try:
        return datetime.fromisoformat(roh).replace(tzinfo=None)
    except ValueError:
        log.debug("Kalender: Datum nicht lesbar: %r", roh)
        return None


@fetcher("tribe_events")
def fetch_tribe_events(source: Source, settings: Settings, now: datetime | None = None) -> list[NewsItem]:
    """Kalender des WordPress-Plugins „The Events Calendar“ (/wp-json/tribe/events/v1/events): ein Termin je
    Eintrag, nur ab heute (in der Anfrage und noch einmal beim Lesen), ohne Gedenktermine aus [blocklist] termine."""
    from .dates import TZ
    from .filtering import gedenktermin  # zirkulären Import vermeiden

    now = now or datetime.now(timezone.utc)
    heute = now.astimezone(TZ).date()
    params = {"per_page": 30, **source.params, "start_date": heute.isoformat()}
    resp = _get(f"{source.url.rstrip('/')}/wp-json/tribe/events/v1/events", params=params)
    items = []
    for ev in resp.json().get("events") or []:
        title, url = clean_text(ev.get("title") or ""), ev.get("url") or ""
        start = _kalender_zeit(ev.get("start_date"))
        if start is None:
            continue
        ende = _kalender_zeit(ev.get("end_date")) or start
        # Ende um Mitternacht gehört zum Vortag („bis 23.5. 00:00“ = bis 22.5.)
        letzter_tag = (ende - timedelta(seconds=1)).date() if ende > start else start.date()
        if not title or not url or letzter_tag < heute:  # laufende mehrtägige Termine bleiben
            continue
        venue = ev.get("venue") if isinstance(ev.get("venue"), dict) else {}
        ort = ", ".join(v for v in (venue.get("venue"), venue.get("address"), venue.get("city")) if v)
        wann = start.strftime("%d.%m.%Y") + ("" if ev.get("all_day") else start.strftime(", %H:%M Uhr"))
        if letzter_tag > start.date():
            wann += letzter_tag.strftime(" bis %d.%m.%Y")
        summary = " · ".join(p for p in (wann, ohne_kontakte(clean_text(ev.get("description") or ""))[:900], ort) if p)
        item = NewsItem(
            title=title, url=url, summary=summary[:1200], source=source.name, published=now,
            language=source.language, kind="event", ort=venue.get("city") or "",
            facts={"event_datum": start.date().isoformat(), "event_ort": ort, "event_ende": letzter_tag.isoformat()},
        )
        if gedenktermin(item, settings):  # Gedenken mit LTTE-Bezug ([blocklist] termine): nie automatisch
            log.info("%s: Gedenktermin ausgelassen: %s", source.name, title)
            continue
        items.append(item)
    return items


# ---- Terminseiten mit JSON-LD (schema.org Event, z. B. Vizha) --------------------------------------

_JSONLD_RE = re.compile(r"<script[^>]+type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>", re.S | re.I)
_HREF_RE = re.compile(r"href=[\"']([^\"'#?]+)[\"']", re.I)
_JAHR_RE = re.compile(r"(?<!\d)(20\d\d)(?!\d)")


def _jsonld(text: str) -> list[dict]:
    """Alle JSON-LD-Objekte einer Seite (Listen und @graph aufgelöst); kaputte Blöcke werden übersprungen."""
    out: list[dict] = []
    for block in _JSONLD_RE.findall(text):
        try:
            data = json.loads(block)
        except ValueError:
            continue
        stapel = data if isinstance(data, list) else [data]
        for d in stapel:
            if isinstance(d, dict):
                out.append(d)
                out += [g for g in d.get("@graph") or [] if isinstance(g, dict)]
    return out


def _typen(d: dict) -> list[str]:
    t = d.get("@type") or []
    return [t] if isinstance(t, str) else [x for x in t if isinstance(x, str)]


def termin_links(text: str, basis: str, muster: str) -> list[str]:
    """Links auf Terminseiten einer Listenseite (gleicher Host, Pfad beginnt mit `muster`): die ItemList aus dem
    JSON-LD (bei Vizha nur kommende Termine, nach Datum), sonst alle passenden Links der Seite."""
    host = urlsplit(basis).netloc

    def passend(urls) -> list[str]:
        out = []
        for u in urls:
            voll = urljoin(basis, str(u or ""))
            teile = urlsplit(voll)
            if teile.netloc == host and teile.path.startswith(muster) and len(teile.path) > len(muster) \
                    and voll not in out:
                out.append(voll)
        return out

    for d in _jsonld(text):
        haupt = d.get("mainEntity") if isinstance(d.get("mainEntity"), dict) else d
        if "ItemList" in _typen(haupt):
            elemente = [e for e in haupt.get("itemListElement") or [] if isinstance(e, dict)]
            return passend(e.get("url") or (e.get("item") if isinstance(e.get("item"), str) else "") for e in elemente)
    return passend(_HREF_RE.findall(text))


def _ld_zeit(roh) -> tuple[datetime | None, bool]:
    """ISO-Zeit aus JSON-LD → (Ortszeit Europe/Berlin, ganztägig). Ohne Zeitzone gilt die Angabe als Ortszeit."""
    from .dates import TZ

    roh = str(roh or "").strip()
    if not roh:
        return None, False
    try:
        dt = datetime.fromisoformat(roh.replace("Z", "+00:00"))
    except ValueError:
        log.debug("JSON-LD: Datum nicht lesbar: %r", roh)
        return None, False
    ganztags = len(roh) == 10
    return (dt.replace(tzinfo=TZ) if dt.tzinfo is None else dt.astimezone(TZ)), ganztags


def _ld_text(wert) -> str:
    if isinstance(wert, dict):
        wert = wert.get("name") or ""
    return clean_text(str(wert or ""))


_ABGESAGT = ("EventCancelled", "EventPostponed", "EventMovedOnline")


def jsonld_termin(text: str, url: str, source: Source, settings: Settings, now: datetime | None = None):
    """Ein Termin aus dem JSON-LD (Typ Event) einer Terminseite oder None: kein Event, abgesagt/verschoben/nur online,
    kein Datum, vorbei, Land nicht in `params.laender` (Vorgabe DE/AT/CH) oder Gedenktermin aus [blocklist] termine (nie automatisch zur Story)."""
    from .dates import TZ
    from .filtering import gedenktermin  # zirkulären Import vermeiden

    now = now or datetime.now(timezone.utc)
    heute = now.astimezone(TZ).date()
    laender = {str(x).upper() for x in source.params.get("laender", ["DE", "AT", "CH"])}
    ev = next((d for d in _jsonld(text) if any(t.endswith("Event") or t == "Festival" for t in _typen(d))), None)
    if ev is None:
        return None
    if any(s in str(ev.get("eventStatus") or "") for s in _ABGESAGT):  # abgesagt, verschoben, nur online
        return None
    title = _ld_text(ev.get("name"))
    start, ganztags = _ld_zeit(ev.get("startDate"))
    if not title or start is None:
        return None
    ende = _ld_zeit(ev.get("endDate"))[0] or start
    letzter_tag = (ende - timedelta(seconds=1)).date() if ende > start else start.date()
    if letzter_tag < heute:
        return None
    ort_ld = ev.get("location")
    ort_ld = next((o for o in ort_ld if isinstance(o, dict)), {}) if isinstance(ort_ld, list) else ort_ld
    ort_ld = ort_ld if isinstance(ort_ld, dict) else {}
    adresse = ort_ld.get("address") if isinstance(ort_ld.get("address"), dict) else {}
    land = _ld_text(adresse.get("addressCountry")).upper()
    if land not in laender:
        return None
    stadt = _ld_text(adresse.get("addressLocality"))
    teile: list[str] = []
    for teil in (_ld_text(ort_ld.get("name")), _ld_text(adresse.get("streetAddress")), stadt):
        if teil and not any(teil in t for t in teile):  # „Hamm Temple“ + „Hamm Temple, Germany“ → einmal
            teile = [t for t in teile if t not in teil] + [teil]
    ort = ", ".join(teile + [COUNTRY_NAMES.get(land, land)])
    ohne_zeit = ganztags or (start.hour, start.minute) == (0, 0)  # 00:00 Ortszeit = Uhrzeit offen (Probe 12.11.)
    wann = start.strftime("%d.%m.%Y") + ("" if ohne_zeit else start.strftime(", %H:%M Uhr"))
    if letzter_tag > start.date():
        wann += letzter_tag.strftime(" bis %d.%m.%Y")
    teile_summary = (wann, _ld_text(ev.get("alternateName")), ohne_kontakte(_ld_text(ev.get("description")))[:900], ort)
    item = NewsItem(
        title=title, url=url, summary=" · ".join(p for p in teile_summary if p)[:1200], source=source.name,
        published=now, language=source.language, kind="event", ort=stadt,
        facts={"event_datum": start.date().isoformat(), "event_ort": ort, "event_ende": letzter_tag.isoformat()},
    )
    # Gedenken mit LTTE-Bezug ([blocklist] termine): nie automatisch. Geprüft wird der volle Text vor dem Kürzen,
    # samt Stichwörtern und Namen von Veranstalter und Mitwirkenden.
    voll = [_ld_text(ev.get("alternateName")), _ld_text(ev.get("description"))]
    for feld in ("keywords", "organizer", "performer"):
        werte = ev.get(feld)
        voll += [_ld_text(w) for w in (werte if isinstance(werte, list) else [werte])]
    pruefung = NewsItem(title=title, url=url, summary=" · ".join(v for v in voll if v), source=source.name,
                        published=now, kind="event")
    if gedenktermin(item, settings) or gedenktermin(pruefung, settings):
        log.info("%s: Gedenktermin ausgelassen: %s", source.name, title)
        return None
    return item


@fetcher("jsonld_events")
def fetch_jsonld_events(source: Source, settings: Settings, now: datetime | None = None) -> list[NewsItem]:
    """Terminkalender ohne Feed (z. B. Vizha): Listenseiten (`params.listen`, relativ zu `url`) nennen die Termine,
    jede Terminseite trägt JSON-LD vom Typ Event. Je Lauf höchstens `params.max_abrufe` Terminseiten (im Wechsel
    aus den Listen, nächster Termin zuerst); Links, deren Slug auf ein vergangenes Jahr endet, werden nicht geholt.
    Ergebnis nach Datum sortiert. Fehlen Seiten, gelten die übrigen Termine (Teilausfall)."""
    now = now or datetime.now(timezone.utc)
    p = source.params
    muster = str(p.get("link_muster", "/events/"))
    frist = time.monotonic() + float(p.get("frist_sekunden", 45))
    listen, fehler = [], []
    for pfad in p.get("listen") or [""]:
        adresse = urljoin(source.url.rstrip("/") + "/", str(pfad).lstrip("/"))
        try:
            listen.append(termin_links(_get(adresse, frist=frist).text, adresse, muster))
        except (requests.RequestException, ValueError) as exc:  # HTTP-Fehler, Zeitlimit, gesperrte Adresse
            fehler.append(f"Liste {pfad}: {exc}")
    if not listen:
        raise RuntimeError("; ".join(fehler) or "keine Liste")
    kandidaten: list[str] = []
    for runde in range(max((len(liste) for liste in listen), default=0)):  # im Wechsel aus den Listen
        for liste in listen:
            if runde < len(liste) and liste[runde] not in kandidaten:
                kandidaten.append(liste[runde])
    jahr = now.astimezone(timezone.utc).year
    # Das Jahr des Termins steht als letzte Jahreszahl im Slug („…-countdown-to-2027-2026“, „…-aarau-2026-2“)
    kandidaten = [u for u in kandidaten if not (jahre := _JAHR_RE.findall(urlsplit(u).path)) or int(jahre[-1]) >= jahr]
    max_abrufe = int(p.get("max_abrufe", 40))
    if len(kandidaten) > max_abrufe:
        log.info("%s: %d Terminseiten, abgerufen werden %d", source.name, len(kandidaten), max_abrufe)
    items, seiten_fehler = [], 0
    for url in kandidaten[:max_abrufe]:
        try:
            item = jsonld_termin(_get(url, frist=frist).text, url, source, settings, now=now)
        except net.Zeitlimit:
            fehler.append("Zeitlimit")
            break
        except (requests.RequestException, ValueError) as exc:  # HTTP-Fehler, gesperrte Adresse, zu groß
            seiten_fehler += 1
            log.debug("%s: %s", source.name, exc)
            continue
        if item is not None:
            items.append(item)
    items.sort(key=lambda i: (i.facts["event_datum"], i.title))
    if seiten_fehler:
        fehler.append(f"{seiten_fehler} Terminseiten nicht abrufbar")
    if fehler:
        raise Teilausfall(items, "; ".join(fehler))
    return items


# ---- HTML-Seiten mit Selektoren -----------------------------------------------------

def _select_text(node, selector: str) -> str:
    """„.titel“ → Text, „a::attr(href)“ → Attribut, „::attr(href)“ → Attribut des Knotens selbst."""
    if not selector:
        return ""
    sel, _, mode = selector.partition("::")
    target = node.select_one(sel) if sel else node
    if target is None:
        return ""
    if mode.startswith("attr(") and mode.endswith(")"):
        return (target.get(mode[5:-1]) or "").strip()
    return clean_text(target.get_text(" "))


def _html_json_items(soup, source: Source, now: datetime) -> list[NewsItem]:
    """Seiten, die ihre Daten als JSON in ein Attribut schreiben (z. B. onclick="openEventDetailsModal({...})")."""
    from .dates import parse_de_datetime

    pattern = source.params["json_pattern"]
    fields = source.params.get("json_fields", {})
    items = []
    for node in soup.select(source.selectors.get("item", "[onclick]")):
        raw = node.get(source.params.get("json_attr", "onclick"), "")
        m = re.search(pattern, html.unescape(raw), re.S)
        if not m:
            continue
        try:
            data = json.loads(m.group(1))
        except ValueError:
            continue
        title = str(data.get(fields.get("title", "title"), "")).strip()
        url = urljoin(source.url, str(data.get(fields.get("url", "url"), "")))
        date_txt = str(data.get(fields.get("date", "date"), ""))
        ort = str(data.get(fields.get("ort", "city"), "") or "").strip("- ")
        when = parse_de_datetime(date_txt, now.astimezone())
        summary = ", ".join(str(data.get(k, "")) for k in fields.get("summary", []) if data.get(k))
        if title and url:
            items.append(NewsItem(
                title=title, url=url, summary=summary[:1200] or date_txt, source=source.name, published=now,
                language=source.language, kind=source.kind, ort=ort,
                facts={"event_datum": when.date().isoformat() if when else "", "event_ort": ort},
            ))
    return items


@fetcher("html")
def fetch_html(source: Source, settings: Settings) -> list[NewsItem]:
    from bs4 import BeautifulSoup  # nur hier gebraucht

    from .dates import parse_de_datetime

    soup = BeautifulSoup(_get(source.url).text, "html.parser")
    now = datetime.now(timezone.utc)
    if source.params.get("json_pattern"):
        return _html_json_items(soup, source, now)
    sel = source.selectors
    items = []
    for node in soup.select(sel.get("item", "article")):
        title = _select_text(node, sel.get("title", "h2"))
        link = _select_text(node, sel.get("link", "a::attr(href)")) or (node.get("href") or "")
        if not title or not link:
            continue
        date_txt = _select_text(node, sel.get("date", ""))
        # params.ort: fester Ort für Seiten eines einzigen Hauses (Tempel), die ihn je Termin nicht nennen
        ort = _select_text(node, sel.get("ort", "")) or str(source.params.get("ort", ""))
        when = parse_de_datetime(date_txt, now.astimezone()) if date_txt else None
        summary_parts = [p for p in (date_txt, _select_text(node, sel.get("summary", "")), ort) if p]
        items.append(NewsItem(
            title=title, url=urljoin(source.url, link), summary=" · ".join(summary_parts)[:1200], source=source.name,
            published=now if source.kind != "news" else (when.astimezone(timezone.utc) if when else now),
            language=source.language, kind=source.kind, ort=ort,
            facts={"event_datum": when.date().isoformat() if when else "", "event_ort": ort},
            # bei Termin-Seiten ist das Datum der Termin (steht in facts), kein Veröffentlichungsdatum
            source_published=when.astimezone(timezone.utc) if when and source.kind == "news" else None,
        ))
    return items


# ---- Kinoprogramme ---------------------------------------------------------------------

@fetcher("kino")
def fetch_kino(source: Source, settings: Settings) -> list[NewsItem]:
    from .kino_providers import fetch_kino as _fetch  # zirkulären Import vermeiden

    return _fetch(source, settings)


# ---- Gesamtlauf ---------------------------------------------------------------------------

def fetch_source(source: Source, settings: Settings) -> list[NewsItem]:
    fn = FETCHERS.get(source.type)
    if fn is None:
        raise ValueError(f"Unbekannter Quellentyp: {source.type}")
    return fn(source, settings)


def _due(source: Source, store, now: datetime, paused: set[str]) -> bool:
    if source.name in paused:
        return False
    if source.interval_minutes and store is not None:
        last = store.source_last_run(source.name)
        if last and now - last < timedelta(minutes=source.interval_minutes):
            return False
    return True


def fetch_all(settings: Settings, store=None) -> list[NewsItem]:
    """Alle fälligen Quellen parallel abfragen; Zeitbudget, Pausen und Status je Quelle."""
    from .kino_providers import merge_kino_items

    global CONDITIONAL
    now = datetime.now(timezone.utc)
    paused = store.sources_paused() if store is not None else set()
    due = [s for s in settings.sources if _due(s, store, now, paused)]
    CONDITIONAL = Conditional(store.http_cache_load() if store is not None else None)

    def record(fn, *args, **kw) -> None:
        if store is None:
            return
        try:
            fn(*args, **kw)
        except Exception:  # noqa: BLE001 - z. B. Store schon geschlossen, Lauf lief weiter
            log.debug("Quellen-Status nicht gespeichert", exc_info=True)

    def safe(source: Source) -> tuple[list[NewsItem], bool]:
        """Meldungen der Quelle und ob sie vollständig gelaufen ist."""
        try:
            items = fetch_source(source, settings)
            log.info("%-34s %3d Meldungen", source.name, len(items))
            record(store.source_ok, source.name, len(items))
            return items, True
        except Teilausfall as teil:
            log.warning("Quelle nur teilweise: %s (%s)", source.name, teil)
            record(store.source_partial, source.name, f"Teilausfall: {teil}")
            return teil.items, False
        except RateLimited as exc:
            log.warning("Quelle pausiert 30 Min. (429): %s", source.name)
            record(store.source_failed, source.name, f"429 {exc}", pause_minutes=30)
        except Exception as exc:  # noqa: BLE001 - Quelle ausfallen lassen, Rest weiterlaufen lassen
            log.warning("Quelle fehlgeschlagen: %s (%s)", source.name, exc)
            record(store.source_failed, source.name, str(exc))
        return [], False

    items: list[NewsItem] = []
    gelaufen: set[str] = set()
    if not due:
        return items
    pool = ThreadPoolExecutor(max_workers=8)
    futures = {pool.submit(safe, s): s for s in due}
    try:
        for fut in as_completed(futures, timeout=settings.fetch_seconds):
            ergebnis, vollstaendig = fut.result()
            if vollstaendig:
                gelaufen.add(futures[fut].name)
            items += ergebnis
    except TimeoutError:
        late = [futures[f].name for f in futures if not f.done()]
        log.warning("Sammel-Zeitbudget (%ss) erreicht, ausstehend: %s", settings.fetch_seconds, ", ".join(late))
    finally:
        pool.shutdown(wait=False, cancel_futures=True)
    record(store.http_cache_save, dict(CONDITIONAL.changed))
    items = merge_kino_items([it for it in items if it.title and it.url])
    for it in items:
        if it.kind == "kino":
            it.quellen_gelaufen = frozenset(gelaufen)
            it.quellen_aktiv = frozenset(s.name for s in settings.sources)
    return items


def fetch_article_text(url: str, limit: int = 6000) -> str:
    """Absätze der Originalseite als Faktenbasis (nur zur Recherche, nicht zur Übernahme)."""
    if "news.google.com" in url:
        return ""  # JS-Weiterleitung, kein Artikeltext erreichbar
    try:
        page = net.safe_get_text(url, timeout=8, max_bytes=3_000_000)
    except (requests.RequestException, ValueError):  # Netz, gesperrte Adresse, Größe, Content-Type
        return ""
    return extract_paragraphs(page, limit)


_NOISE_START_RE = re.compile(r"<(script|style|noscript|template|svg|nav|header|footer|aside|form)\b", re.I)
_ARTICLE_START_RE = re.compile(r"<(article)\b", re.I)
_P_START_RE = re.compile(r"<(p)", re.I)  # wie bisher „<p[^>]*>“: auch <pre>, <param> – geschlossen mit </p>
_SCHLUSS_CACHE: dict[tuple[str, bool], re.Pattern] = {}


def _schluss_re(name: str, mit_leerraum: bool) -> re.Pattern:
    """„</name\\s*>“ (bzw. „</name>“) für die Suche direkt im Original (re.I wie bisher, keine umgeformte Kopie)."""
    key = (name, mit_leerraum)
    if key not in _SCHLUSS_CACHE:
        _SCHLUSS_CACHE[key] = re.compile("</" + re.escape(name) + (r"\s*>" if mit_leerraum else ">"), re.I)
    return _SCHLUSS_CACHE[key]


def bloecke(text: str, start_re: re.Pattern, mit_leerraum: bool = True):
    """Blöcke „<name …>Inhalt</name>“ in einem linearen Durchlauf: je (Anfang, Inhalt-Anfang, Inhalt-Ende, Ende).

    Gleiches Ergebnis wie re.finditer mit „<name\\b[^>]*>(.*?)</name\\s*>“ (re.S, re.I) über die Seite, aber ohne
    dessen quadratische Laufzeit bei fehlenden Schluss-Tags. `start_re` liefert den Namen in Gruppe 1. Wie beim Regex
    wird ein Start ohne Schluss übersprungen und weitergesucht (der Rest der Seite bleibt); linear bleibt es über eine
    Merkliste je Name (ab dort gibt es keinen Schluss mehr) und das gemerkte nächste „>“. Gesucht wird nur im
    Original – Positionen aus einer kleingeschriebenen Kopie verrutschen („İ“.lower() hat zwei Zeichen)."""
    pos, n = 0, len(text)
    kein_schluss_ab: dict[str, int] = {}
    auf = -1
    while pos <= n:
        m = start_re.search(text, pos)
        if not m:
            return
        if auf < m.end():
            auf = text.find(">", m.end())
            if auf < 0:
                return  # kein „>“ mehr: kein Start kann mehr passen
        name = m.group(1).lower()
        e = None
        if name not in kein_schluss_ab:  # die Starts kommen in steigender Folge, also auch auf + 1
            e = _schluss_re(m.group(1), mit_leerraum).search(text, auf + 1)
            if e is None:
                kein_schluss_ab[name] = auf + 1
        if e is None:
            pos = m.start() + 1  # wie der Regex: diesen Start überspringen, weitersuchen
            continue
        yield m.start(), auf + 1, e.start(), e.end()
        pos = e.end()


def ohne_rauschen(html_text: str) -> str:
    """Skripte, Styles, Navigation, Kopf, Fuß, Formulare usw. durch ein Leerzeichen ersetzen (linear)."""
    teile, pos = [], 0
    for anfang, _, _, ende in bloecke(html_text, _NOISE_START_RE):
        teile += [html_text[pos:anfang], " "]
        pos = ende
    teile.append(html_text[pos:])
    return "".join(teile)
_CODE_HINT_RE = re.compile(r"[{};]\s*[a-z#.@-]|\bfunction\s*\(|document\.|window\.|@context|@media|\.tdi_", re.I)


def extract_paragraphs(html_text: str, limit: int = 6000) -> str:
    """Lesbare Absätze einer Artikelseite: Skripte, Styles, Navigation und Code-Reste werden entfernt.

    Bevorzugt den <article>-Block; Absätze mit CSS/JS-Mustern (viele Klammern, Semikolons, JSON-LD) fliegen raus,
    damit die Faktenbasis für Writer und Agent nicht mit Theme-Code vollläuft.
    """
    body = ohne_rauschen(html_text)
    artikel = next(bloecke(body, _ARTICLE_START_RE), None)
    if artikel and artikel[2] - artikel[1] > 400:
        body = body[artikel[1]:artikel[2]]
    out: list[str] = []
    for _, a, b, _ in bloecke(body, _P_START_RE, mit_leerraum=False):
        raw = body[a:b]
        p = clean_text(raw)
        if len(p) <= 60 or len(p) > 3000:
            continue
        if len(_CODE_HINT_RE.findall(p)) >= 2 or p.count("{") + p.count("}") >= 4:
            continue
        out.append(p)
    return "\n".join(out)[:limit]


_OG_RES = (
    re.compile(r'<meta[^>]+property=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)["\']', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image(?::secure_url)?["\']', re.I),
    re.compile(r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']', re.I),
)


def fetch_og_image(url: str, timeout: int = 8) -> str:
    """Vorschaubild (og:image) einer Artikelseite – nur für den Prototyp-Export, nie im Betrieb."""
    if not url or "news.google.com" in url:
        return ""
    try:
        head = net.safe_get_text(url, timeout=timeout, max_bytes=3_000_000)[:300_000]
    except (requests.RequestException, ValueError):
        return ""
    for rx in _OG_RES:
        m = rx.search(head)
        if m:
            return html.unescape(urljoin(url, m.group(1).strip()))
    return ""
