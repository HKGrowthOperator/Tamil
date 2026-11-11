"""Story-Clustering: gehört eine Meldung zu einer Story, die wir schon haben?

Reihenfolge (billig vor teuer): gleiche URL/UID → Kino-Schlüssel (Film + Kinowoche) → Event-Schlüssel (Datum + Stadt +
Titelwörter) → Titelähnlichkeit über die Storys der letzten 7 Tage. Eindeutig ähnlich (≥ 0,82) = gleiche Story,
Grenzfälle (0,55–0,82) entscheidet Haiku gebündelt. Eine Meldung zu einer bestehenden Story reichert diese an
(neues Dokument) statt einen zweiten Beitrag anzulegen.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from .. import prompts, schalter
from ..sources import NewsItem
from ..workflow import repo
from ..workflow.costs import BudgetErschoepft
from ..workflow.models import ClusterErgebnis
from ..workflow.providers import json_block
from . import Kontext

log = logging.getLogger(__name__)

SICHER, GRENZE = 0.82, 0.55
_STOP = {"der", "die", "das", "und", "in", "im", "am", "an", "auf", "mit", "für", "von", "zum", "zur", "the", "a", "of",
         "and", "ein", "eine", "einen", "läuft", "tamil", "tamilische", "tamilischen", "tamilischer", "neue", "neuen"}


@dataclass
class Zuordnung:
    item: NewsItem
    story_id: int | None
    grund: str
    bezug: int | None = None  # gleiche Story wie die neue Meldung an dieser Stelle desselben Scans


def woerter(text: str) -> set[str]:
    return {w for w in re.findall(r"[\wäöüß]{3,}", text.lower()) if w not in _STOP}


def aehnlichkeit(a: str, b: str) -> float:
    seq = SequenceMatcher(None, a.lower(), b.lower()).ratio()
    wa, wb = woerter(a), woerter(b)
    jaccard = len(wa & wb) / len(wa | wb) if wa and wb else 0.0
    return max(seq, jaccard)


def schluessel(item: NewsItem) -> str:
    if item.kind == "kino":
        return item.uid  # kino:<Film+Woche>
    if item.kind == "event":
        datum = str((item.facts or {}).get("event_datum") or "")[:10]
        if datum:
            top = "-".join(sorted(woerter(item.title))[:3])
            return f"event:{datum}:{(item.ort or '').lower()}:{top}"
    return ""


def zuordnen(ctx: Kontext, items: list[NewsItem], tage: int = 7) -> list[Zuordnung]:
    store = ctx.store
    bestehend = repo.stories_seit(store, tage)
    ergebnis: list[Zuordnung] = []
    grenzfaelle: list[tuple[int, NewsItem, dict]] = []
    for item in items:
        sid = repo.story_zu(store, url=item.url, uid=item.uid)
        if sid:
            ergebnis.append(Zuordnung(item, sid, "gleiche Meldung"))
            continue
        key = schluessel(item)
        if key:
            sid = repo.story_zu(store, schluessel=key)
            if sid:
                ergebnis.append(Zuordnung(item, sid, "gleicher Kino-/Termin-Schlüssel"))
                continue
        if item.kind == "kino":
            ergebnis.append(Zuordnung(item, None, "neue Kinowoche"))
            continue
        # Meldungen desselben Scans, die der Vorfilter nicht zusammengelegt hat (z. B. „… (verschoben)“)
        frueher = next((i for i, z in enumerate(ergebnis) if z.story_id is None and z.bezug is None
                        and z.item.kind == item.kind and ((key and schluessel(z.item) == key)
                                                          or aehnlichkeit(item.title, z.item.title) >= SICHER)), None)
        if frueher is not None:
            ergebnis.append(Zuordnung(item, None, "gleiche Story wie eine Meldung desselben Scans", bezug=frueher))
            continue
        best, wert = None, 0.0
        for s in bestehend:
            if s["typ"] in ("kino", "dossier") or s["status"] == "verworfen" or s.get("herkunft") == "nachtrag":
                continue
            w = aehnlichkeit(item.title, s.get("titel") or "")
            if w > wert:
                best, wert = s, w
        if best is not None and wert >= SICHER:
            ergebnis.append(Zuordnung(item, best["id"], f"Titel ähnlich ({wert:.2f})"))
        elif best is not None and wert >= GRENZE:
            grenzfaelle.append((len(ergebnis), item, best))
            ergebnis.append(Zuordnung(item, None, f"Grenzfall ({wert:.2f})"))
        else:
            ergebnis.append(Zuordnung(item, None, "neue Story"))
    if grenzfaelle and ctx.claude is not None:
        _grenzfaelle_entscheiden(ctx, grenzfaelle, ergebnis)
    return ergebnis


def _grenzfaelle_entscheiden(ctx: Kontext, faelle: list[tuple[int, NewsItem, dict]], ergebnis: list[Zuordnung]) -> None:
    paare = [{"nr": n, "neu": f"{item.title} – {item.summary[:200]}", "bestehend": story.get("titel") or ""}
             for n, (_, item, story) in enumerate(faelle, 1)]
    try:
        antwort = ctx.claude.call("cluster", prompts.load_prompt("cluster"), json_block("paare", paare), ClusterErgebnis)
    except BudgetErschoepft:
        return  # im Zweifel neue Story
    except schalter.Gestoppt:
        raise  # angehalten: der Scan bricht ab, statt doppelte Storys anzulegen
    except Exception as exc:  # noqa: BLE001 – Ausfall des Modells: im Zweifel neue Story, Scan läuft weiter
        log.warning("Cluster-Prüfung fehlgeschlagen (%s) – Grenzfälle werden neue Storys", exc)
        return
    if not antwort.ok:
        return
    for e in antwort.daten.entscheidungen:
        if 1 <= e.nr <= len(faelle) and e.gleiche_story:
            idx, item, story = faelle[e.nr - 1]
            ergebnis[idx] = Zuordnung(item, story["id"], f"gleiche Story laut Cluster-Prüfung: {e.grund}")
