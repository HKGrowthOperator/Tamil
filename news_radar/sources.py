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

from .config import Settings, Source

log = logging.getLogger(__name__)

USER_AGENT = "TamilDE-NewsRadar/2.0 (+https://www.tamil.de)"
TIMEOUT = 12
_TAG_RE = re.compile(r"<[^>]+>")
_TRACKING = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid", "ref"}
COUNTRY_NAMES = {"DE": "Deutschland", "CH": "Schweiz", "AT": "Österreich"}
COUNTRY_NAMES_EN = {"DE": "Germany", "CH": "Switzerland", "AT": "Austria"}


class RateLimited(Exception):
    """HTTP 429 – Quelle eine Weile in Ruhe lassen."""


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

    @property
    def uid(self) -> str:
        if self.uid_override:
            return self.uid_override
        return hashlib.sha1(normalize_url(self.url).encode()).hexdigest()


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(_TAG_RE.sub(" ", value or ""))).strip()


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


def _get(url: str, **kw) -> requests.Response:
    kw.setdefault("timeout", TIMEOUT)
    headers = {"User-Agent": USER_AGENT, **kw.pop("headers", {})}
    resp = requests.get(url, headers=headers, **kw)
    if resp.status_code == 429:
        raise RateLimited(url)
    resp.raise_for_status()
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
        published = datetime.fromtimestamp(calendar.timegm(struct), tz=timezone.utc) if struct else now
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
            )
        )
    return items


@fetcher("rss")
def fetch_rss(source: Source, settings: Settings) -> list[NewsItem]:
    return _feed_items(_get(source.url).content, source)


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
        items.append(NewsItem(
            title=title, url=post.get("link", ""), summary=summary[:1200], source=source.name,
            published=_parse_iso(post.get("date_gmt") or post.get("date")) if source.kind == "news" else now,
            language=source.language, kind=source.kind,
        ))
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
        ort = _select_text(node, sel.get("ort", ""))
        when = parse_de_datetime(date_txt, now.astimezone()) if date_txt else None
        summary_parts = [p for p in (date_txt, _select_text(node, sel.get("summary", "")), ort) if p]
        items.append(NewsItem(
            title=title, url=urljoin(source.url, link), summary=" · ".join(summary_parts)[:1200], source=source.name,
            published=now if source.kind != "news" else (when.astimezone(timezone.utc) if when else now),
            language=source.language, kind=source.kind, ort=ort,
            facts={"event_datum": when.date().isoformat() if when else "", "event_ort": ort},
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
        last = store.source_last_ok(source.name)
        if last and now - last < timedelta(minutes=source.interval_minutes):
            return False
    return True


def fetch_all(settings: Settings, store=None) -> list[NewsItem]:
    """Alle fälligen Quellen parallel abfragen; Zeitbudget, Pausen und Status je Quelle."""
    from .kino_providers import merge_kino_items

    now = datetime.now(timezone.utc)
    paused = store.sources_paused() if store is not None else set()
    due = [s for s in settings.sources if _due(s, store, now, paused)]

    def record(fn, *args, **kw) -> None:
        if store is None:
            return
        try:
            fn(*args, **kw)
        except Exception:  # noqa: BLE001 - z. B. Store schon geschlossen, Lauf lief weiter
            log.debug("Quellen-Status nicht gespeichert", exc_info=True)

    def safe(source: Source) -> list[NewsItem]:
        try:
            items = fetch_source(source, settings)
            log.info("%-34s %3d Meldungen", source.name, len(items))
            record(store.source_ok, source.name, len(items))
            return items
        except RateLimited as exc:
            log.warning("Quelle pausiert 30 Min. (429): %s", source.name)
            record(store.source_failed, source.name, f"429 {exc}", pause_minutes=30)
        except Exception as exc:  # noqa: BLE001 - Quelle ausfallen lassen, Rest weiterlaufen lassen
            log.warning("Quelle fehlgeschlagen: %s (%s)", source.name, exc)
            record(store.source_failed, source.name, str(exc))
        return []

    items: list[NewsItem] = []
    if not due:
        return items
    pool = ThreadPoolExecutor(max_workers=8)
    futures = {pool.submit(safe, s): s for s in due}
    try:
        for fut in as_completed(futures, timeout=settings.fetch_seconds):
            items += fut.result()
    except TimeoutError:
        late = [futures[f].name for f in futures if not f.done()]
        log.warning("Sammel-Zeitbudget (%ss) erreicht, ausstehend: %s", settings.fetch_seconds, ", ".join(late))
    finally:
        pool.shutdown(wait=False, cancel_futures=True)
    items = [it for it in items if it.title and it.url]
    return merge_kino_items(items)


def fetch_article_text(url: str, limit: int = 6000) -> str:
    """Absätze der Originalseite als Faktenbasis (nur zur Recherche, nicht zur Übernahme)."""
    if "news.google.com" in url:
        return ""  # JS-Weiterleitung, kein Artikeltext erreichbar
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=8)
        resp.raise_for_status()
    except requests.RequestException:
        return ""
    paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", resp.text, flags=re.S | re.I)
    text = "\n".join(p for p in (clean_text(x) for x in paragraphs) if len(p) > 60)
    return text[:limit]


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
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException:
        return ""
    head = resp.text[:300_000]
    for rx in _OG_RES:
        m = rx.search(head)
        if m:
            return html.unescape(urljoin(url, m.group(1).strip()))
    return ""
