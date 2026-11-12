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
          "event", "events", "programm", "sangam", "verein", "association"}
_GLEICH = {"diwali": "deepavali", "deepawali": "deepavali", "dipavali": "deepavali", "deepavaly": "deepavali",
           "dipawali": "deepavali", "தீபாவளி": "deepavali"}
_LAENDER = {"deutschland", "germany", "de", "österreich", "oesterreich", "austria", "at", "schweiz", "switzerland",
            "suisse", "svizzera", "ch"}
_STADT_GLEICH = {"munich": "münchen", "muenchen": "münchen", "cologne": "köln", "koeln": "köln", "zurich": "zürich",
                 "zuerich": "zürich", "geneva": "genf", "vienna": "wien", "nuremberg": "nürnberg",
                 "duesseldorf": "düsseldorf", "dusseldorf": "düsseldorf"}


# Kurze Wörter, die in Titeln ganz in Großbuchstaben Inhalt sind, keine Kürzel („TAMIL NEW YEAR“)
_KURZWORT = {"new", "day", "eid", "sri", "art", "cup", "run", "fun", "tag"}


def _kuerzel(titel: str) -> set[str]:
    """Vereinskürzel im Titel (MTS, FTS, BTS): 2–5 Großbuchstaben, keine bekannten Wörter. Steht der ganze Titel in
    Großbuchstaben („TAMIL NEW YEAR“, „ONAM 2026“), sind Wörter mit Selbstlaut ab vier Buchstaben Inhalt (ONAM, THAI,
    YEAR); kürzere bleiben Kürzel (TYO, ATS), außer bekannten Wörtern wie NEW."""
    gross = not re.search(r"[a-zäöüß]", titel)
    return {w.lower() for w in re.findall(r"\b[A-ZÄÖÜ]{2,5}\b", titel)
            if not (gross and re.search(r"[AEIOUÄÖÜY]", w) and (len(w) >= 4 or w.lower() in _KURZWORT))
            and w.lower() not in _FUELL and w.lower() not in _STOP and w.lower() not in _GLEICH}


# „<Ort> Tamil <Vereinswort>“ (München Tamil Sangam, German Tamil Sangam): Portale wie „Swiss Tamil Info“ sind keine
# Vereine und geben keinen Hinweis
_VEREIN_RE = re.compile(r"\b([A-ZÄÖÜ])[^\W\d_]*\s+(?:Tamil|TAMIL)\s+([^\W\d_]+)")
_VEREINSWORT = {"sangam", "sangham", "sangamam", "verein", "kulturverein", "association", "mandram", "manram",
                "society", "union", "club", "mandapam"}


def _vereine(titel: str, quellen: tuple[str, ...] = ()) -> set[str]:
    """Hinweise auf den Verein: Kürzel im Titel und die Anfangsbuchstaben von „<Ort> Tamil <Vereinswort>“ in Titel und
    Quellennamen („München Tamil Sangam · Termine“ → mts)."""
    hinweise = _kuerzel(titel)
    for text in (titel, *quellen):
        hinweise |= {f"{a}t{b[0]}".lower() for a, b in _VEREIN_RE.findall(text or "") if b.lower() in _VEREINSWORT}
    return hinweise


def titel_kern(titel: str) -> set[str]:
    """Kennwörter eines Termintitels: klein, ohne Jahreszahlen, Satzzeichen, Füllwörter und Vereinskürzel (MTS, FTS);
    Diwali/Deepavali/Deepawali gelten als ein Wort."""
    kuerzel = _kuerzel(titel)
    roh = re.findall(r"[^\W\d_]+", titel.lower())
    return {_GLEICH.get(w, w) for w in roh
            if len(w) >= 3 and w not in kuerzel and w not in _FUELL and w not in _STOP}


def _stadt(ort: str) -> str:
    ort = re.sub(r"\s+", " ", (ort or "").strip().lower())
    return "" if ort in _LAENDER else _STADT_GLEICH.get(ort, ort)


# Straße: Hausnummer, „straße“/„str.“ oder eines dieser Wörter für sich („Am Ring“, „Wiener Platz“). Orte, die nur
# so enden (Pöring, Neuring), bleiben Orte.
_STRASSE = re.compile(r"\d|straße|strasse|\bstr\.|(?:^|\s)(platz|weg|allee|gasse|ring|damm|ufer|chaussee)\b", re.I)


def _ortsteile(voll: str) -> list[str]:
    """Bestandteile eines vollen Orts ohne Straßenangaben und Postleitzahl: „Bürgerhaus Neukeferloh, Leonhard-Stadler-
    Straße 12, Neukeferloh“ → [„bürgerhaus neukeferloh“, „neukeferloh“]."""
    teile = [re.sub(r"^\d{4,5}\s+", "", t.strip().lower()) for t in (voll or "").split(",")]
    return [t for t in teile if t and not _STRASSE.search(t)]


def _stadt_in(stadt: str, voll: str) -> bool:
    muster = re.compile(rf"\b{re.escape(stadt)}\b")
    return any(muster.search(t) for t in _ortsteile(voll))


def ort_vertraeglich(ort_a: str, voll_a: str, ort_b: str, voll_b: str) -> bool:
    """Gleiche Stadt, eine Seite ohne Stadt (leer oder nur Land) oder die Stadt der einen Seite steht als ganzes Wort
    in einem Ortsbestandteil der anderen (Gemeinde Grasbrunn ↔ „Bürgerhaus Neukeferloh“), nie in einem Straßennamen."""
    a, b = _stadt(ort_a), _stadt(ort_b)
    if not a or not b or a == b:
        return True
    return _stadt_in(a, voll_b) or _stadt_in(b, voll_a)


def _kuerzel_widerspruch(a: str, b: str) -> bool:
    ka, kb = _kuerzel(a), _kuerzel(b)
    return bool(ka and kb and not ka & kb)


def termin_widerspruch(a: NewsItem, b: NewsItem) -> bool:
    """Zwei Termine sind sicher verschieden: andere Vereinskürzel (MTS ≠ BTS) oder derselbe Tag in unverträglichen
    Städten. Bremst auch die allgemeine Titelähnlichkeit („Deepavali“ in Stuttgart ≠ „Deepavali“ in Berlin)."""
    if a.kind != "event" or b.kind != "event":
        return False
    if _kuerzel_widerspruch(a.title, b.title):
        return True
    return bool(_datum(a)) and _datum(a) == _datum(b) and not ort_vertraeglich(
        a.ort, (a.facts or {}).get("event_ort", ""), b.ort, (b.facts or {}).get("event_ort", ""))


def _titel_gleich(a: str, b: str) -> bool:
    ka, kb = titel_kern(a), titel_kern(b)
    if not ka or not kb:
        return False
    if _kuerzel_widerspruch(a, b):
        return False  # MTS ≠ BTS; ein Kürzel nur auf einer Seite stört nicht
    return ka == kb or len(ka & kb) / len(ka | kb) >= 0.6 or ka <= kb or kb <= ka


def _datum(item: NewsItem) -> str:
    return str((item.facts or {}).get("event_datum") or "")[:10]


def _passt(titel_a: str, ort_a: str, voll_a: str, titel_b: str, ort_b: str, voll_b: str,
           quellen_a: tuple[str, ...] = (), quellen_b: tuple[str, ...] = ()) -> bool:
    ohne_ort = not _stadt(ort_a) or not _stadt(ort_b)
    if not (_titel_gleich(titel_a, titel_b) and ort_vertraeglich(ort_a, voll_a, ort_b, voll_b)):
        return False
    if ohne_ort and len(titel_kern(titel_a) & titel_kern(titel_b)) < 2:
        # Ohne Ort trägt ein einzelnes gemeinsames Kernwort („Deepavali“) allein nicht, weder gleich noch als Teilmenge –
        # das Fest ist am selben Tag in vielen Städten. Es braucht denselben Verein auf beiden Seiten
        # (Kürzel MTS ↔ Quelle „München Tamil Sangam · Termine“, oder „Hamburg Tamil Sangam“ im Titel ↔ HTS).
        return bool(_vereine(titel_a, quellen_a) & _vereine(titel_b, quellen_b))
    return True


def gleicher_termin(a: NewsItem, b: NewsItem) -> bool:
    """Zwei Termin-Meldungen meinen denselben Termin: gleiches Datum, gleicher Titelkern, verträglicher Ort."""
    if a.kind != "event" or b.kind != "event" or not _datum(a) or _datum(a) != _datum(b):
        return False
    return _passt(a.title, a.ort, (a.facts or {}).get("event_ort", ""),
                  b.title, b.ort, (b.facts or {}).get("event_ort", ""), (a.source,), (b.source,))


def _termin_story(store, item: NewsItem) -> int | None:
    """Die eine bestehende Termin-Story am selben Tag mit gleichem Titelkern und verträglichem Ort. Mehrere Kandidaten
    = mehrdeutig, dann keine (lieber eine Dublette als zwei Termine in einer Story); verworfene zählen nicht."""
    datum = _datum(item)
    if item.kind != "event" or not datum:
        return None
    praefix = f"event:{datum}:"
    rows = store.db.execute(
        "SELECT s.id, s.titel, s.ort, (SELECT group_concat(d.quelle, char(10)) FROM source_documents d "
        "WHERE d.story_id = s.id) FROM stories s WHERE s.typ = 'event' AND s.status != 'verworfen' "
        "AND substr(s.schluessel, 1, ?) = ?", (len(praefix), praefix)).fetchall()
    voll = (item.facts or {}).get("event_ort", "")
    treffer = [sid for sid, titel, ort, quellen in rows
               if _passt(item.title, item.ort, voll, titel or "", ort or "", ort or "",
                         (item.source,), tuple((quellen or "").split("\n")))]
    return treffer[0] if len(treffer) == 1 else None


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
        offen = [i for i, z in enumerate(ergebnis)
                 if z.story_id is None and z.bezug is None and z.item.kind == item.kind]
        frueher = next((i for i in offen if not termin_widerspruch(item, ergebnis[i].item)
                        and ((key and schluessel(ergebnis[i].item) == key)
                             or aehnlichkeit(item.title, ergebnis[i].item.title) >= SICHER)), None)
        if frueher is None:  # gleicher Termin aus einer anderen Quelle, nur wenn eindeutig
            termine = [i for i in offen if gleicher_termin(item, ergebnis[i].item)]
            frueher = termine[0] if len(termine) == 1 else None
        if frueher is not None:
            ergebnis.append(Zuordnung(item, None, "gleiche Story wie eine Meldung desselben Scans", bezug=frueher))
            continue
        best, wert = None, 0.0
        for s in bestehend:
            if s["typ"] in ("kino", "dossier") or s["status"] == "verworfen" or s.get("herkunft") == "nachtrag":
                continue
            if item.kind == "event" and _kuerzel_widerspruch(item.title, s.get("titel") or ""):
                continue  # MTS-Termin ≠ BTS-Termin, auch bei fast gleichem Titel
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
