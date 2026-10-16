"""Nachrichten einsammeln: RSS-Feeds und Token-APIs (NewsAPI, GNews)."""

from __future__ import annotations

import calendar
import hashlib
import html
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import feedparser
import requests

from .config import Settings, Source

log = logging.getLogger(__name__)

USER_AGENT = "TamilDE-NewsRadar/1.0 (+https://www.tamil.de)"
TIMEOUT = 12
_TAG_RE = re.compile(r"<[^>]+>")
_TRACKING = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid", "ref"}


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

    @property
    def uid(self) -> str:
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
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return datetime.now(timezone.utc)


def fetch_rss(source: Source) -> list[NewsItem]:
    resp = requests.get(source.url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
    resp.raise_for_status()
    feed = feedparser.parse(resp.content)
    items = []
    for entry in feed.entries:
        struct = entry.get("published_parsed") or entry.get("updated_parsed")
        published = (
            datetime.fromtimestamp(calendar.timegm(struct), tz=timezone.utc) if struct else datetime.now(timezone.utc)
        )
        image = ""
        for media in entry.get("media_content", []) + entry.get("media_thumbnail", []):
            if media.get("url"):
                image = media["url"]
                break
        items.append(
            NewsItem(
                title=clean_text(entry.get("title", "")),
                url=entry.get("link", ""),
                summary=clean_text(entry.get("summary", ""))[:1200],
                source=source.name,
                published=published,
                image_url=image,
                language=source.language,
            )
        )
    return items


def fetch_newsapi(source: Source, token: str) -> list[NewsItem]:
    resp = requests.get(
        "https://newsapi.org/v2/everything",
        params={"q": source.query, "language": source.language, "sortBy": "publishedAt", "pageSize": 30},
        headers={"X-Api-Key": token, "User-Agent": USER_AGENT},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
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


def fetch_gnews(source: Source, token: str) -> list[NewsItem]:
    resp = requests.get(
        "https://gnews.io/api/v4/search",
        params={"q": source.query, "lang": source.language, "max": 25, "sortby": "publishedAt", "apikey": token},
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
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


def fetch_source(source: Source, settings: Settings) -> list[NewsItem]:
    if source.type == "rss":
        return fetch_rss(source)
    if source.type == "newsapi":
        if not settings.newsapi_key:
            log.info("Übersprungen (kein NEWSAPI_KEY): %s", source.name)
            return []
        return fetch_newsapi(source, settings.newsapi_key)
    if source.type == "gnews":
        if not settings.gnews_token:
            log.info("Übersprungen (kein GNEWS_TOKEN): %s", source.name)
            return []
        return fetch_gnews(source, settings.gnews_token)
    raise ValueError(f"Unbekannter Quellentyp: {source.type}")


def fetch_all(settings: Settings) -> list[NewsItem]:
    """Alle Quellen parallel abfragen; eine fehlerhafte Quelle stoppt den Lauf nicht."""

    def safe(source: Source) -> list[NewsItem]:
        try:
            items = fetch_source(source, settings)
            log.info("%-32s %3d Meldungen", source.name, len(items))
            return items
        except Exception as exc:  # noqa: BLE001 - Quelle ausfallen lassen, Rest weiterlaufen lassen
            log.warning("Quelle fehlgeschlagen: %s (%s)", source.name, exc)
            return []

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = pool.map(safe, settings.sources)
    return [item for batch in results for item in batch if item.title and item.url]


def fetch_article_text(url: str, limit: int = 6000) -> str:
    """Absätze der Originalseite als Faktenbasis (nur zur Recherche, nicht zur Übernahme)."""
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=8)
        resp.raise_for_status()
    except requests.RequestException:
        return ""
    paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", resp.text, flags=re.S | re.I)
    text = "\n".join(p for p in (clean_text(x) for x in paragraphs) if len(p) > 60)
    return text[:limit]
