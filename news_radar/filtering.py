"""Vorfilter: Aktualität, Ausschlussliste, Stichwort- und DACH-Relevanz, Dubletten.

Zweistufig: Meldungen mit erkennbarem DACH-Bezug brauchen nur wenige tamilische Stichworte,
Meldungen ohne DACH-Bezug die volle Schwelle. Events und Kinoprogramme umgehen die Stichwortwertung.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher

from .config import Regions, Settings, Source
from .sources import NewsItem

_TAMIL_SCRIPT = re.compile(r"[஀-௿]")


def _contains(text: str, term: str, exact: bool = False, suffix: int = 0) -> bool:
    """Ganzes Wort (optional mit bis zu `suffix` Flexionsbuchstaben: tamilisch → tamilischer/-en);
    tamilische Schrift per Teilstring ohne abschließendes Pulli (தமிழ் trifft தமிழர்கள்);
    `exact` = Groß-/Kleinschreibung beachten (Essen, Hamm, Bern)."""
    if _TAMIL_SCRIPT.search(term):
        return term.rstrip("\u0bcd") in text
    flags = 0 if exact else re.I
    tail = rf"[a-zäöüß]{{0,{suffix}}}" if suffix else ""
    return re.search(rf"(?<![\w]){re.escape(term)}{tail}(?![\w])", text, flags) is not None


def score_item(item: NewsItem, keywords: dict[str, int]) -> int:
    title = item.title.lower()
    body = item.summary.lower()
    score = 0
    for term, weight in keywords.items():
        if _contains(title, term, suffix=2):
            score += weight * 2
        elif _contains(body, term, suffix=2):
            score += weight
    return score


def dach_score(item: NewsItem, regions: Regions) -> tuple[int, str]:
    """(Punkte, Ort): Stadt im Titel 3, im Text 1, Land 1. Ort = erste Stadt im Titel, sonst im Text, sonst Land."""
    title, body = item.title, item.summary
    score, ort, body_ort, land_ort = 0, "", "", ""
    for stadt, land in regions.staedte.items():
        names = [stadt] + regions.aliases.get(stadt, [])
        exact = stadt in regions.exakt
        if any(_contains(title, n, exact) for n in names):
            score += 3
            ort = ort or stadt
        elif any(_contains(body, n, exact) for n in names):
            score += 1
            body_ort = body_ort or stadt
    for term, land in regions.laender.items():
        if _contains(title, term) or _contains(body, term):
            score += 1
            land_ort = land_ort or {"DE": "Deutschland", "CH": "Schweiz", "AT": "Österreich"}.get(land, land)
    return score, ort or body_ort or land_ort


def guess_category(item: NewsItem, settings: Settings) -> str:
    text = f"{item.title} {item.summary}".lower()
    best, best_hits = settings.categories[0].slug if settings.categories else "news", 0
    for cat in settings.categories:
        hits = sum(1 for h in cat.hints if _contains(text, h))
        if hits > best_hits:
            best, best_hits = cat.slug, hits
    if best_hits == 0 and item.kind == "kino":
        return "kino"
    if best_hits == 0 and item.kind == "event":
        return "events"
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
    """Die relevantesten neuen Meldungen, DACH zuerst, dann nach Punkten und Datum."""
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=settings.max_age_hours)
    by_name: dict[str, Source] = {s.name: s for s in settings.sources}
    per_source: dict[str, int] = {}
    picked: list[NewsItem] = []
    titles = list(recent_titles)
    for item in sorted(items, key=lambda i: i.published, reverse=True):
        text = f"{item.title} {item.summary}".lower()
        if item.uid in seen_uids:
            continue
        if item.kind == "news" and item.published < cutoff:
            continue
        if any(_contains(text, term) for term in settings.blocklist):
            continue
        source = by_name.get(item.source) or by_name.get(item.source.split(" · ")[0])
        if source and source.kind != "news" and item.kind == "news":
            item.kind = source.kind
        item.score = score_item(item, settings.keywords)
        item.dach_score, item.ort = dach_score(item, settings.regions)
        if source and source.country and not item.ort:
            item.ort = {"DE": "Deutschland", "CH": "Schweiz", "AT": "Österreich"}.get(source.country, source.country)
            item.dach_score = max(item.dach_score, 1)
        needed = None
        if source and source.min_score is not None:
            needed = source.min_score  # 0 = vertrauenswürdige Quelle, alles durchlassen
        elif item.kind == "news":
            needed = settings.min_score_dach if item.dach_score > 0 else settings.min_score
        if needed and item.score < needed:
            continue
        twin = next((p for p in picked if similar(item.title, p.title)), None)
        if twin is not None:
            twin.related.append(item)
            continue
        if any(similar(item.title, t) for t in titles):
            continue
        key = source.name if source else item.source
        limit = source.max_items if source else settings.max_articles
        if per_source.get(key, 0) >= limit:
            continue
        per_source[key] = per_source.get(key, 0) + 1
        item.category_hint = guess_category(item, settings)
        titles.append(item.title)
        picked.append(item)
    picked.sort(key=lambda i: (i.dach_score > 0, i.score + i.dach_score, i.published), reverse=True)
    return picked
