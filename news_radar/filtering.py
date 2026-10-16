"""Vorfilter: Aktualität, Ausschlussliste, Stichwort-Relevanz, Dubletten."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher

from .config import Settings
from .sources import NewsItem


def _contains(text: str, term: str) -> bool:
    return re.search(rf"(?<![\w]){re.escape(term)}(?![\w])", text) is not None


def score_item(item: NewsItem, keywords: dict[str, int]) -> int:
    title = item.title.lower()
    body = item.summary.lower()
    score = 0
    for term, weight in keywords.items():
        if _contains(title, term):
            score += weight * 2
        elif _contains(body, term):
            score += weight
    return score


def guess_category(item: NewsItem, settings: Settings) -> str:
    text = f"{item.title} {item.summary}".lower()
    best, best_hits = settings.categories[0].slug if settings.categories else "news", 0
    for cat in settings.categories:
        hits = sum(1 for h in cat.hints if _contains(text, h))
        if hits > best_hits:
            best, best_hits = cat.slug, hits
    return best


def similar(a: str, b: str, threshold: float = 0.82) -> bool:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold


def select(
    items: list[NewsItem],
    settings: Settings,
    seen_uids: set[str],
    recent_titles: list[str],
    now: datetime | None = None,
) -> list[NewsItem]:
    """Gibt die relevantesten neuen Meldungen zurück, absteigend nach Score."""
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=settings.max_age_hours)
    picked: list[NewsItem] = []
    titles = list(recent_titles)
    for item in items:
        text = f"{item.title} {item.summary}".lower()
        if item.published < cutoff or item.uid in seen_uids:
            continue
        if any(_contains(text, term) for term in settings.blocklist):
            continue
        item.score = score_item(item, settings.keywords)
        if item.score < settings.min_score:
            continue
        if any(similar(item.title, t) for t in titles):
            continue
        item.category_hint = guess_category(item, settings)
        titles.append(item.title)
        picked.append(item)
    picked.sort(key=lambda i: (i.score, i.published), reverse=True)
    return picked
