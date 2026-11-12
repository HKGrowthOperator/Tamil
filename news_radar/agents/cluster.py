"""Story-Clustering: gehört eine Meldung zu einer Story, die wir schon haben?

Reihenfolge (billig vor teuer): gleiche URL/UID → Kino-Schlüssel (Film + Kinowoche) → Event-Schlüssel (Datum + Stadt +
Titelwörter) → gleicher Termin (gleiches Datum, Kern des Titels gleich, Ort verträglich; Vereinskalender und Vizha) →
Titelähnlichkeit über die Storys der letzten 7 Tage. Eindeutig ähnlich (≥ 0,82) = gleiche Story,
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


# Termin-Abgleich zwischen Quellen: „Diwali-2026“ (Vereinskalender) = „MTS Diwali 2026“ (Vizha)
_FUELL = {"celebration", "celebrations", "feier", "feiern", "festival", "fest", "lights", "lichter", "lichterfest",
          "event", "events", "programm", "e.v", "sangam", "verein", "association"}
_GLEICH = {"diwali": "deepavali", "deepawali": "deepavali", "dipavali": "deepavali", "deepavaly": "deepavali",
           "dipawali": "deepavali", "தீபாவளி": "deepavali"}
_LAENDER = {"deutschland", "germany", "de", "österreich", "oesterreich", "austria", "at", "schweiz", "switzerland",
            "suisse", "svizzera", "ch"}
_STADT_GLEICH = {"munich": "münchen", "muenchen": "münchen", "cologne": "köln", "koeln": "köln", "zurich": "zürich",
                 "zuerich": "zürich", "geneva": "genf", "vienna": "wien", "nuremberg": "nürnberg",
                 "duesseldorf": "düsseldorf", "dusseldorf": "düsseldorf"}


def titel_kern(titel: str) -> set[str]:
    """Kennwörter eines Termintitels: klein, ohne Jahreszahlen, Satzzeichen, Füllwörter und Vereinskürzel (MTS, FTS);
    Diwali/Deepavali/Deepawali gelten als ein Wort."""
    kuerzel = {w.lower() for w in re.findall(r"\b[A-ZÄÖÜ]{2,5}\b", titel) if not w.isdigit()}
    roh = re.findall(r"[^\W\d_]+", titel.lower())
    return {_GLEICH.get(w, w) for w in roh
            if len(w) >= 3 and w not in kuerzel and w not in _FUELL and w not in _STOP}


def _stadt(ort: str) -> str:
    ort = re.sub(r"\s+", " ", (ort or "").strip().lower())
    return "" if ort in _LAENDER else _STADT_GLEICH.get(ort, ort)


def ort_vertraeglich(ort_a: str, voll_a: str, ort_b: str, voll_b: str) -> bool:
    """Gleiche Stadt, eine Seite ohne Stadt (leer oder nur Land) oder die Stadt der einen Seite steht im vollen Ort der
    anderen (Gemeinde Grasbrunn ↔ „Bürgerhaus Neukeferloh“)."""
    a, b = _stadt(ort_a), _stadt(ort_b)
    if not a or not b or a == b:
        return True
    return a in (voll_b or "").lower() or b in (voll_a or "").lower()


def _titel_gleich(a: str, b: str) -> bool:
    ka, kb = titel_kern(a), titel_kern(b)
    if not ka or not kb:
        return False
    return ka <= kb or kb <= ka or len(ka & kb) / len(ka | kb) >= 0.6


def _datum(item: NewsItem) -> str:
    return str((item.facts or {}).get("event_datum") or "")[:10]


def gleicher_termin(a: NewsItem, b: NewsItem) -> bool:
    """Zwei Termin-Meldungen meinen denselben Termin: gleiches Datum, gleicher Titelkern, verträglicher Ort."""
    if a.kind != "event" or b.kind != "event" or not _datum(a) or _datum(a) != _datum(b):
        return False
    return (_titel_gleich(a.title, b.title)
            and ort_vertraeglich(a.ort, (a.facts or {}).get("event_ort", ""),
                                 b.ort, (b.facts or {}).get("event_ort", "")))


def _termin_story(store, item: NewsItem) -> int | None:
    """Bestehende Termin-Story am selben Tag mit gleichem Titelkern und verträglichem Ort (neueste zuerst)."""
    datum = _datum(item)
    if item.kind != "event" or not datum:
        return None
    rows = store.db.execute(
        "SELECT id, titel, ort FROM stories WHERE typ = 'event' AND schluessel LIKE ? AND herkunft != 'nachtrag' "
        "ORDER BY id DESC", (f"event:{datum}:%",)).fetchall()
    for sid, titel, ort in rows:
        voll = (item.facts or {}).get("event_ort", "")
        if _titel_gleich(item.title, titel or "") and ort_vertraeglich(item.ort, voll, ort or "", ort or ""):
            return sid
    return None


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
        sid = _termin_story(store, item)
        if sid:
            ergebnis.append(Zuordnung(item, sid, "gleicher Termin (Datum, Titel, Ort)"))
            continue
        if item.kind == "kino":
            ergebnis.append(Zuordnung(item, None, "neue Kinowoche"))
            continue
        # Meldungen desselben Scans, die der Vorfilter nicht zusammengelegt hat (z. B. „… (verschoben)“)
        frueher = next((i for i, z in enumerate(ergebnis) if z.story_id is None and z.bezug is None
                        and z.item.kind == item.kind and ((key and schluessel(z.item) == key)
                                                          or gleicher_termin(item, z.item)
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
