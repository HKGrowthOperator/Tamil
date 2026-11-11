"""`quellen pruefen`: jede Quelle des Registers live abfragen und bewerten → data/quellen-pruefung.csv.

Gemessen je Quelle: Erreichbarkeit und Dauer, Treffer jetzt und der letzten 14 Tage (live und aus der Datenbank),
daraus entstandene Entwürfe, robots.txt, Paywall-Hinweis auf einer Artikelseite. Die Punktzahl ist eine
Entscheidungshilfe; welche Quellen aktiv sind, steht ausschließlich in sources.toml (enabled).
"""

from __future__ import annotations

import csv
import logging
import re
import time
import urllib.robotparser
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

import requests

from . import net, sources
from .config import Settings, Source
from .store import Store

log = logging.getLogger(__name__)

_PAYWALL_RE = re.compile(
    r"paywall|piano\.io|tinypass|plus-artikel|\bplus\b-inhalt|jetzt (?:weiter)?lesen mit|abo abschlie|"
    r"subscribe to continue|subscriber[- ]only|premium-inhalt|nur für abonnenten",
    re.I,
)
TOKEN_TYPES = {"newsapi": "NEWSAPI_KEY", "gnews": "GNEWS_TOKEN"}


@dataclass
class Pruefung:
    name: str
    typ: str
    kind: str
    land: str
    aktiv_bisher: bool
    erreichbar: bool
    fehler: str
    sekunden: float
    treffer_jetzt: int
    treffer_14_tage: int
    gesehen_14_tage_db: int
    entwuerfe_db: int
    robots: str
    paywall_hinweis: bool
    punkte: float = 0.0
    empfehlung: str = ""
    warnung: str = ""


_JAHR_RE = re.compile(r"(?<!\d)(20\d\d)(?!\d)")


def jahr_warnung(url: str, jahr: int) -> str:
    """Adresse mit einer Jahreszahl vor dem laufenden Jahr (z. B. Filmreihe „…-2026/“): wahrscheinlich umzustellen."""
    alt = sorted({int(j) for j in _JAHR_RE.findall(url or "") if int(j) < jahr})
    return f"Adresse nennt {', '.join(map(str, alt))} – auf {jahr} umstellen?" if alt else ""


def robots_status(url: str, timeout: float = 8) -> str:
    """erlaubt | verboten | unbekannt für die konkrete URL mit unserem User-Agent."""
    parts = urlsplit(url)
    if not parts.scheme or not parts.netloc:
        return "unbekannt"
    try:
        text = net.safe_get_text(f"{parts.scheme}://{parts.netloc}/robots.txt", timeout=timeout, max_bytes=500_000)
    except net.HTTPError as exc:
        return "erlaubt" if 400 <= exc.status < 500 else "unbekannt"  # kein robots.txt = keine Einschränkung
    except (requests.RequestException, ValueError):
        return "unbekannt"
    parser = urllib.robotparser.RobotFileParser()
    parser.parse(text.splitlines())
    return "erlaubt" if parser.can_fetch(net.USER_AGENT, url) else "verboten"


def paywall_hint(url: str) -> bool:
    if not url or "news.google.com" in url:
        return False
    try:
        page = net.safe_get_text(url, timeout=8, max_bytes=3_000_000)
    except (requests.RequestException, ValueError):
        return False
    return bool(_PAYWALL_RE.search(page[:400_000]))


def _db_counts(store: Store | None, source: Source, since: str) -> tuple[int, int]:
    if store is None:
        return 0, 0
    like = f"{source.name}%"
    seen = store.db.execute("SELECT COUNT(*) FROM seen WHERE source LIKE ? AND created_at >= ?", (like, since)).fetchone()[0]
    drafts = store.db.execute(
        "SELECT COUNT(*) FROM drafts WHERE uid IN (SELECT uid FROM seen WHERE source LIKE ?)", (like,)
    ).fetchone()[0]
    return seen, drafts


def bewerten(p: Pruefung, source: Source) -> float:
    """Punkte: liefert überhaupt etwas, wie viel Aktuelles, wie viel davon wurde Entwurf, DACH-Bezug, Rechte."""
    if not p.erreichbar:
        return -10.0
    punkte = 2.0
    punkte += min(p.treffer_14_tage, 30) / 6  # bis 5
    punkte += min(p.entwuerfe_db, 6)  # bis 6: was die Redaktion bisher wirklich gebraucht hat
    if source.country or source.type == "gnews_region" or source.kind in ("event", "kino"):
        punkte += 2  # DACH-Bezug oder Termine/Kino vor Ort
    if p.treffer_jetzt == 0:
        punkte -= 2
    if p.robots == "verboten":
        punkte -= 8
    if p.paywall_hinweis:
        punkte -= 3
    return round(punkte, 1)


def pruefe_quelle(source: Source, settings: Settings, store: Store | None, now: datetime) -> Pruefung:
    since = (now - timedelta(days=14)).isoformat()
    land = source.country or ("DACH" if source.type == "gnews_region" else "")
    p = Pruefung(name=source.name, typ=source.type, kind=source.kind, land=land, aktiv_bisher=source.enabled,
                 erreichbar=False, fehler="", sekunden=0.0, treffer_jetzt=0, treffer_14_tage=0,
                 gesehen_14_tage_db=0, entwuerfe_db=0, robots="unbekannt", paywall_hinweis=False)
    p.gesehen_14_tage_db, p.entwuerfe_db = _db_counts(store, source, since)
    p.warnung = jahr_warnung(source.url, now.year)
    if p.warnung:
        log.warning("%s: %s", source.name, p.warnung)
    env_key = TOKEN_TYPES.get(source.type)
    if env_key and not getattr(settings, {"newsapi": "newsapi_key", "gnews": "gnews_token"}[source.type]):
        p.fehler = f"kein Schlüssel ({env_key})"
        return p
    t0 = time.monotonic()
    try:
        items = sources.fetch_source(source, settings)
        p.erreichbar = True
    except Exception as exc:  # noqa: BLE001 – die Prüfung soll jede Quelle bewerten, auch kaputte
        p.fehler = str(exc)[:160]
        items = []
    p.sekunden = round(time.monotonic() - t0, 1)
    cutoff = now - timedelta(days=14)
    p.treffer_jetzt = len(items)
    p.treffer_14_tage = sum(1 for i in items if i.kind != "news" or i.published >= cutoff)
    probe = source.url or (items[0].url if items else "")
    if source.type in ("rss", "html", "wp_json") and probe:
        p.robots = robots_status(probe)
    elif source.type == "gnews_region" and items:
        p.robots = robots_status(items[0].url)
    if source.kind == "news" and items:
        p.paywall_hinweis = paywall_hint(next((i.url for i in items if "news.google.com" not in i.url), ""))
    return p


def pruefen(settings: Settings, store: Store | None, file: Path, aktiv: int = 20) -> list[Pruefung]:
    now = datetime.now(timezone.utc)
    ergebnisse = []
    for source in settings.alle_quellen:
        p = pruefe_quelle(source, settings, store, now)
        p.punkte = bewerten(p, source)
        ergebnisse.append(p)
        log.info("%-34s %s %5.1f Punkte · %d jetzt · %d in 14 Tagen · %d Entwürfe · robots %s%s",
                 source.name, "ok " if p.erreichbar else "ERR", p.punkte, p.treffer_jetzt, p.treffer_14_tage,
                 p.entwuerfe_db, p.robots, " · Paywall?" if p.paywall_hinweis else "")
    ranking = sorted(ergebnisse, key=lambda p: p.punkte, reverse=True)
    for rang, p in enumerate(ranking, 1):
        p.empfehlung = "aktiv" if rang <= aktiv and p.punkte > 0 else "aus"
    file.parent.mkdir(parents=True, exist_ok=True)
    with file.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(asdict(ranking[0]).keys()) if ranking else ["name"])
        writer.writeheader()
        for p in ranking:
            writer.writerow(asdict(p))
    return ranking
