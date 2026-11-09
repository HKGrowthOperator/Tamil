"""Signal: welche Meldungen sind die Arbeit wert? Heuristik zuerst, Haiku nur für die Grauzone (gebündelt).

Die Heuristik ist der bisherige Vorfilter (filtering.select). Meldungen, die knapp an der Stichwort-Schwelle scheitern
(Grauzone), bekommen eine zweite Chance: bis zu 10 je Aufruf gehen an Haiku. Erst danach entsteht eine Story – teure
Schritte laufen nie für irrelevante Meldungen.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from .. import filtering, prompts
from ..config import Settings
from ..sources import NewsItem
from ..workflow.costs import BudgetErschoepft
from ..workflow.models import SignalErgebnis
from ..workflow.providers import json_block
from . import Kontext

log = logging.getLogger(__name__)

GRAUZONE = 2  # so viele Punkte unter der Schwelle gilt eine Meldung als Grenzfall
BUENDEL = 10


def heuristik(item: NewsItem, settings: Settings) -> int:
    """Relevanz 1–10 ohne Modell für Meldungen, die der Vorfilter durchgelassen hat."""
    if item.kind in ("event", "kino") and item.dach_score > 0:
        return 8
    if item.dach_score >= 2:
        return 8
    if item.dach_score > 0:
        return 7
    if item.score >= settings.min_score + 2:
        return 6
    return 5


def grauzone(items: list[NewsItem], settings: Settings, seen: set[str], ausgewaehlt: set[str],
             now: datetime | None = None) -> list[NewsItem]:
    """Nachrichten, die knapp an der Stichwort-Schwelle gescheitert sind (frisch, nicht gesehen, nicht gesperrt)."""
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=settings.max_age_hours)
    out = []
    for item in items:
        if item.uid in seen or item.uid in ausgewaehlt or item.kind != "news" or item.published < cutoff:
            continue
        text = f"{item.title} {item.summary}".lower()
        if any(filtering._contains(text, t) for t in settings.blocklist):
            continue
        quelle = filtering.quelle_fuer(item, settings)
        if quelle and quelle.bezug_noetig and not filtering.hat_bezug(item, settings):
            continue  # ohne tamilischen Bezug auch keine zweite Chance über Haiku
        score = filtering.score_item(item, settings.keywords)
        dach, ort = filtering.dach_score(item, settings.regions)
        schwelle = settings.min_score_dach if dach > 0 else settings.min_score
        if score > 0 and schwelle - GRAUZONE <= score < schwelle:  # ohne jedes Stichwort keine Grauzone
            item.score, item.dach_score, item.ort = score, dach, ort
            out.append(item)
    out.sort(key=lambda i: (i.dach_score, i.score), reverse=True)
    return out[:BUENDEL * 2]


def pruefen(ctx: Kontext, kandidaten: list[NewsItem]) -> tuple[list[NewsItem], set[str]]:
    """Grauzone an Haiku. Rückgabe: (angenommene Meldungen mit item.signal, UIDs, die tatsächlich beurteilt wurden).

    Ohne Modell, ohne Budget oder bei einem API-Fehler bleiben die Meldungen unbeurteilt (nicht „gesehen“) und kommen
    beim nächsten Scan wieder dran – ein Ausfall von Haiku stoppt den Scan nie.
    """
    angenommen: list[NewsItem] = []
    beurteilt: set[str] = set()
    if not kandidaten or ctx.claude is None:
        return angenommen, beurteilt
    system = prompts.load_prompt("signal")
    for start in range(0, len(kandidaten), BUENDEL):
        buendel = kandidaten[start:start + BUENDEL]
        meldungen = [{"nr": n, "titel": i.title, "zusammenfassung": i.summary[:400], "quelle": i.source,
                      "ort": i.ort} for n, i in enumerate(buendel, 1)]
        try:
            antwort = ctx.claude.call("signal", system, json_block("meldungen", meldungen), SignalErgebnis)
        except BudgetErschoepft:
            log.info("Signal: Budget erreicht, Grauzone bleibt liegen")
            break
        except Exception as exc:  # noqa: BLE001 – Ausfall des Modells: Grauzone bleibt liegen, Scan läuft weiter
            log.warning("Signal fehlgeschlagen (%s) – Grauzone bleibt liegen", exc)
            break
        if not antwort.ok:
            continue
        for b in antwort.daten.bewertungen:
            if not 1 <= b.nr <= len(buendel):
                continue
            item = buendel[b.nr - 1]
            beurteilt.add(item.uid)
            if b.relevanz >= ctx.settings.min_relevance:
                item.signal = {"relevanz": b.relevanz, "grund": b.grund, "risiko": b.risiko, "land": b.land}
                item.category_hint = filtering.guess_category(item, ctx.settings)
                angenommen.append(item)
    return angenommen, beurteilt
