"""Kino-Programme (CineStar, kinoheld, Cineplexx AT) → tamilische Vorstellungen → ein Item je Film und Kinowoche.

Die APIs sind inoffiziell; jede Anbindung ist hinter `Show` gekapselt, damit Formatänderungen lokal bleiben.
Echte Antworten liegen als Fixtures in tests/fixtures/.
"""

from __future__ import annotations

import hashlib
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import requests

from .config import Settings, Source
from .sources import NewsItem, USER_AGENT
from .wordpress import slugify

log = logging.getLogger(__name__)

TZ = ZoneInfo("Europe/Berlin")
TAMIL_RE = re.compile(r"\btamil\b", re.I)
_VERSION_RE = re.compile(
    r"[\(\[\-–]?\s*(tamil(?:isch)?\s*(?:om(?:e)?u|ov|original)?|om(?:e)?u|ov|omdu|sondervorstellung)\s*[\)\]]?", re.I
)


@dataclass
class Show:
    film: str
    kino: str
    stadt: str
    land: str
    start: datetime | None = None  # konkrete Vorstellung
    von: date | None = None  # Laufzeit (wenn keine Uhrzeiten bekannt)
    bis: date | None = None
    url: str = ""
    provider: str = ""


def is_tamil(*texts: str) -> bool:
    return any(TAMIL_RE.search(t or "") for t in texts)


def clean_film_title(title: str) -> str:
    """„Jailer 2 (Tamil OmeU)“, „(tamil) Jailer 2“, „*Jailer 2“ → „Jailer 2“."""
    t = _VERSION_RE.sub(" ", title or "")
    t = re.sub(r"^\W+|\W+$", "", t)
    return re.sub(r"\s+", " ", t).strip()


def film_key(title: str) -> str:
    return slugify(clean_film_title(title), 60)


def kino_week(d: date) -> tuple[int, int]:
    """Kinowoche läuft Donnerstag bis Mittwoch → auf die ISO-Woche des Donnerstags abbilden."""
    return (d - timedelta(days=3)).isocalendar()[:2]


def _parse_cinestar_dt(value: str) -> datetime | None:
    # "2026-10-18 20:00 CEST"
    try:
        return datetime.strptime(value[:16], "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
    except (TypeError, ValueError):
        return None


# ---- Anbieter ---------------------------------------------------------------

def fetch_cinestar(source: Source, settings: Settings, http=requests) -> list[Show]:
    base = source.url or "https://www.cinestar.de"
    headers = {"User-Agent": USER_AGENT}
    cinemas = http.get(f"{base}/api/cinema/", headers=headers, timeout=10).json()
    wanted = set(source.params.get("cinemas") or [])
    if wanted:
        cinemas = [c for c in cinemas if c["id"] in wanted]
    shows: list[Show] = []

    def one(cinema: dict) -> list[Show]:
        try:
            data = http.get(f"{base}/api/cinema/{cinema['id']}/show/", headers=headers, timeout=6).json()
        except Exception as exc:  # noqa: BLE001 - ein Kino fällt aus, die anderen laufen weiter
            log.debug("CineStar %s: %s", cinema.get("name"), exc)
            return []
        out = []
        for s in data:
            if not is_tamil(s.get("title"), s.get("subtitle"), " ".join(s.get("attributes") or [])):
                continue
            film = clean_film_title(s.get("title") or "")
            url = f"{base}{s['detailLink']}" if s.get("detailLink") else f"{base}/{cinema.get('slug', '')}"
            times = [_parse_cinestar_dt(st.get("datetime", "")) for st in s.get("showtimes") or []]
            times = [t for t in times if t]
            if times:
                out += [Show(film, cinema["name"], cinema["city"], "DE", start=t, url=url, provider="cinestar") for t in times]
            else:
                von, bis = _parse_cinestar_dt(s.get("startDate", "")), _parse_cinestar_dt(s.get("endDate", ""))
                out.append(Show(film, cinema["name"], cinema["city"], "DE", von=von.date() if von else None,
                                bis=bis.date() if bis else None, url=url, provider="cinestar"))
        return out

    with ThreadPoolExecutor(max_workers=6) as pool:
        for batch in pool.map(one, cinemas):
            shows += batch
    return shows


KINOHELD_QUERY = """{ search(query: "tamil", limit: 100) { __typename ... on Show { id name beginning
  cinema { id name city { name } } movie { id title } } } }"""


def fetch_kinoheld(source: Source, settings: Settings, http=requests) -> list[Show]:
    url = source.url or "https://next-live.kinoheld.de/graphql"
    resp = http.post(url, json={"query": KINOHELD_QUERY}, headers={"User-Agent": USER_AGENT}, timeout=15)
    resp.raise_for_status()
    shows = []
    for r in resp.json().get("data", {}).get("search", []) or []:
        if r.get("__typename") != "Show" or not is_tamil(r.get("name")):
            continue
        try:
            start = datetime.fromisoformat(r["beginning"])
        except (KeyError, ValueError):
            continue
        cinema = r.get("cinema") or {}
        shows.append(Show(clean_film_title(r["name"]), cinema.get("name", "?"), (cinema.get("city") or {}).get("name", ""),
                          "DE", start=start, url="https://www.kinoheld.de/", provider="kinoheld"))
    return shows


def _cineplexx_city(c: dict) -> str:
    for key in ("city", "address2"):
        val = c.get(key) or ""
        if m := re.search(r"\d{4}\s+(.+)$", val):
            return m.group(1).strip()
        if val and not re.search(r"\d", val):
            return val.strip()
    return ""


def fetch_cineplexx(source: Source, settings: Settings, http=requests) -> list[Show]:
    base = source.url or "https://app.cineplexx.at"
    headers = {"User-Agent": USER_AGENT}
    movies = http.get(f"{base}/api/v2/movies", headers=headers, timeout=15).json()
    cinemas = {c["id"]: c for c in http.get(f"{base}/api/v1/cinemas", headers=headers, timeout=15).json()}
    shows = []
    for m in movies:
        if (m.get("originLangCMS") or "").lower() != "tamil" and not is_tamil(m.get("title"), m.get("titleCalculated")):
            continue
        film = clean_film_title(m.get("titleCalculated") or m.get("title") or "")
        von = None
        if m.get("startDate"):
            try:
                von = date.fromisoformat(m["startDate"][:10])
            except ValueError:
                von = None
        url = f"https://www.cineplexx.at/film/{m['shortURL']}" if m.get("shortURL") else "https://www.cineplexx.at/"
        for cid in m.get("cinemaIds") or []:
            c = cinemas.get(cid, {})
            shows.append(Show(film, c.get("name", f"Cineplexx {cid}"), _cineplexx_city(c), "AT", von=von, url=url, provider="cineplexx"))
    return shows


PROVIDERS = {"cinestar": fetch_cinestar, "kinoheld": fetch_kinoheld, "cineplexx": fetch_cineplexx}


# ---- Aggregation --------------------------------------------------------------

def _weeks_of(show: Show, weeks: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if show.start:
        w = kino_week(show.start.date())
        return [w] if w in weeks else []
    if show.von or show.bis:
        von, bis = show.von or show.bis, show.bis or show.von
        return [w for w in weeks if _week_overlaps(w, von, bis)]
    return []


def _week_overlaps(week: tuple[int, int], von: date, bis: date) -> bool:
    thursday = date.fromisocalendar(week[0], week[1], 4)  # Donnerstag der Kinowoche
    return von <= thursday + timedelta(days=6) and bis >= thursday


def _fingerprint(kinos: list[dict]) -> str:
    parts = sorted(f"{k['kino']}/{k['stadt']}/" + ",".join(t[:10] for t in k.get("termine") or []) for k in kinos)
    return hashlib.sha1("|".join(parts).encode()).hexdigest()


def aggregate_shows(shows: list[Show], now: datetime | None = None) -> list[NewsItem]:
    """Ein NewsItem je Film und Kinowoche (diese und nächste Woche)."""
    now = now or datetime.now(timezone.utc)
    this_week = kino_week(now.astimezone(TZ).date())
    next_week = kino_week(date.fromisocalendar(this_week[0], this_week[1], 4) + timedelta(days=7))
    weeks = [this_week, next_week]
    groups: dict[tuple[str, tuple[int, int]], dict] = {}
    for s in shows:
        key = film_key(s.film)
        if not key:
            continue
        for week in _weeks_of(s, weeks):
            g = groups.setdefault((key, week), {"film": clean_film_title(s.film), "kinos": {}})
            k = g["kinos"].setdefault((s.kino, s.stadt), {"kino": s.kino, "stadt": s.stadt, "land": s.land, "termine": [], "url": s.url})
            if s.start:
                k["termine"].append(s.start.isoformat(timespec="minutes"))
            elif s.von:
                k["von"] = s.von.isoformat()
    items = []
    for (key, (year, week)), g in groups.items():
        kinos = sorted(g["kinos"].values(), key=lambda k: (k["stadt"], k["kino"]))
        for k in kinos:
            k["termine"] = sorted(set(k["termine"]))
        cities = sorted({k["stadt"] for k in kinos if k["stadt"]})
        n = len(kinos)
        title = f"„{g['film']}“ (Tamil) läuft in {n} {'Kino' if n == 1 else 'Kinos'}: " + ", ".join(cities[:6]) + (" …" if len(cities) > 6 else "")
        facts = {"film": g["film"], "woche": f"{year}-W{week:02d}", "kinos": kinos}
        summary = "; ".join(f"{k['kino']} ({k['stadt']})" for k in kinos)
        items.append(NewsItem(
            title=title, url=kinos[0].get("url") or "https://www.tamil.de/kino/", summary=summary[:1200],
            source="Kinoprogramm", published=now, language="de", kind="kino", category_hint="kino",
            facts=facts, fingerprint=_fingerprint(kinos), uid_override="kino:" + hashlib.sha1(f"{key}:{year}W{week}".encode()).hexdigest(),
        ))
    return items


def merge_kino_items(items: list[NewsItem]) -> list[NewsItem]:
    """Derselbe Film in derselben Woche aus mehreren Anbietern → ein Item mit allen Spielorten."""
    merged: dict[str, NewsItem] = {}
    others: list[NewsItem] = []
    for it in items:
        if it.kind != "kino":
            others.append(it)
            continue
        if it.uid not in merged:
            merged[it.uid] = it
            continue
        base = merged[it.uid]
        known = {(k["kino"], k["stadt"]) for k in base.facts["kinos"]}
        base.facts["kinos"] += [k for k in it.facts["kinos"] if (k["kino"], k["stadt"]) not in known]
        base.facts["kinos"].sort(key=lambda k: (k["stadt"], k["kino"]))
        base.fingerprint = _fingerprint(base.facts["kinos"])
        cities = sorted({k["stadt"] for k in base.facts["kinos"] if k["stadt"]})
        n = len(base.facts["kinos"])
        base.title = f"„{base.facts['film']}“ (Tamil) läuft in {n} {'Kino' if n == 1 else 'Kinos'}: " + ", ".join(cities[:6]) + (" …" if len(cities) > 6 else "")
        base.summary = "; ".join(f"{k['kino']} ({k['stadt']})" for k in base.facts["kinos"])[:1200]
    return others + list(merged.values())


def fetch_kino(source: Source, settings: Settings) -> list[NewsItem]:
    provider = PROVIDERS.get(source.provider)
    if provider is None:
        raise ValueError(f"Unbekannter Kino-Anbieter: {source.provider}")
    return aggregate_shows(provider(source, settings))
