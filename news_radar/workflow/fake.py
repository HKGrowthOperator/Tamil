"""FakeClaude: ein Ersatz für anthropic.Anthropic ohne Netz – für Tests und die Abnahme (`abnahme`).

Die Rolle steht in der Beschreibung des JSON-Schemas („rolle:recherche …“). Jede Rolle hat eine deterministische
Standardantwort, die aus den JSON-Blöcken im Prompt (<dokumente>, <claims>, <entwurf> …) gebaut wird; Szenarien
überschreiben einzelne Rollen (eigene Antwort, Ablehnung, abgeschnittene Antwort, API-Fehler).
Die Antworten tragen ein usage-Objekt wie die echte API, damit Kostenmessung und Budget mitgetestet werden.
"""

from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from types import SimpleNamespace
from typing import Any, Callable

Responder = Callable[[str, str, dict], dict]

_BLOCK_RE = r"<{name}>\n(.*?)\n</{name}>"
_SATZ_RE = re.compile(r"(?<=[^0-9][.!?])\s+(?=[A-ZÄÖÜ„\"])")  # nicht nach „21.“ (Datum) trennen
_DATUM_RE = re.compile(r"\b\d{1,2}\.\s*(?:\d{1,2}\.|Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|"
                       r"November|Dezember)|\b20\d\d-\d\d-\d\d\b|\b(?:Montag|Dienstag|Mittwoch|Donnerstag|Freitag|"
                       r"Samstag|Sonntag)\b", re.I)
_PREIS_RE = re.compile(r"\b\d+(?:[.,]\d+)?\s*(?:Euro|EUR|CHF|Franken|€)", re.I)
_STAEDTE = ("Berlin", "Hamburg", "Köln", "Düsseldorf", "Dortmund", "Essen", "Frankfurt", "Stuttgart", "München",
            "Hannover", "Bielefeld", "Paderborn", "Hamm", "Bremen", "Mainz", "Zürich", "Bern", "Basel", "Luzern",
            "St. Gallen", "Wien", "Graz", "Linz")


def block(text: str, name: str) -> Any:
    m = re.search(_BLOCK_RE.format(name=name), text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except ValueError:
        return None


def _saetze(text: str) -> list[str]:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return [s.strip() for s in _SATZ_RE.split(re.sub(r"\s+", " ", text)) if len(s.strip()) > 25]


# ---- Standardantworten je Rolle ------------------------------------------------------------------

def signal(user: str, system: str, req: dict) -> dict:
    out = []
    for m in block(user, "meldungen") or []:
        text = f"{m.get('titel', '')} {m.get('zusammenfassung', '')}".lower()
        tamil = any(w in text for w in ("tamil", "tamilisch", "sri lanka", "kollywood", "pongal", "jaffna"))
        land = next((land for stadt, land in (("zürich", "CH"), ("bern", "CH"), ("basel", "CH"), ("wien", "AT"))
                     if stadt in text), "DE" if any(w in text for w in ("deutschland", "köln", "hamm", "berlin")) else "")
        out.append({"nr": m["nr"], "relevanz": 7 if tamil and land else (5 if tamil else 2), "land": land,
                    "grund": "tamilischer Bezug" + (" im DACH-Raum" if land else "") if tamil else "kein Bezug",
                    "risiko": "keins"})
    return {"bewertungen": out}


def cluster(user: str, system: str, req: dict) -> dict:
    out = []
    for p in block(user, "paare") or []:
        ratio = SequenceMatcher(None, p.get("neu", "").lower(), p.get("bestehend", "").lower()).ratio()
        out.append({"nr": p["nr"], "gleiche_story": ratio >= 0.6, "grund": f"Titelähnlichkeit {ratio:.2f}"})
    return {"entscheidungen": out}


def recherche(user: str, system: str, req: dict) -> dict:
    docs = [d for d in (block(user, "dokumente") or []) if d.get("art") != "hinweis"]
    claims, n = [], 0
    for doc in docs:
        for satz in _saetze(f"{doc.get('titel', '')}. {doc.get('text', '')}")[:10]:
            if any(SequenceMatcher(None, satz, c["aussage"]).ratio() > 0.8 for c in claims):
                continue
            n += 1
            art = "was"
            if _DATUM_RE.search(satz):
                art = "wann"
            elif _PREIS_RE.search(satz):
                art = "preis"
            elif any(st in satz for st in _STAEDTE):
                art = "wo"
            elif n > 1:
                art = "hintergrund"
            quellen = [d["doc_key"] for d in docs if satz[:60] in f"{d.get('titel', '')}. {d.get('text', '')}"]
            claims.append({"id": f"C{n}", "aussage": satz[:300], "art": art,
                           "kern": art in ("was", "wann", "wo", "preis") and n <= 4,
                           "quellen": quellen or [doc["doc_key"]], "fundstelle": satz[:160], "sicherheit": 0.9,
                           "support": "offen"})
            if n >= 10:
                break
    return {"claims": claims, "widersprueche": [], "fehlende_angaben": []}


def _absaetze(claims: list[dict]) -> tuple[list[str], list[dict]]:
    absaetze, belege = [], []
    for i in range(0, len(claims), 2):
        gruppe = claims[i:i + 2]
        absaetze.append(" ".join(c["aussage"].rstrip(".") + "." for c in gruppe))
        belege.append({"absatz": len(absaetze), "claim_ids": [c["id"] for c in gruppe]})
    return absaetze, belege


def text(user: str, system: str, req: dict) -> dict:
    story = block(user, "story") or {}
    claims = block(user, "claims") or []
    absaetze, belege = _absaetze(claims)
    quelle = (block(user, "quellen") or [{"name": "Quelle"}])[0].get("name", "Quelle")
    titel = (story.get("titel") or "Meldung")[:90]
    html = "\n".join(f"<p>{a}</p>" for a in absaetze) + f'\n<p class="quelle">Quelle: {quelle}</p>'
    teaser = (claims[0]["aussage"] if claims else titel)[:220]
    kategorie = story.get("kategorie") or "news"
    return {
        "relevanz": int(story.get("relevanz") or 7), "begruendung": story.get("begruendung") or "aus den Belegen",
        "kategorie": kategorie, "typ": {"event": "event", "kino": "kino_termine"}.get(story.get("typ"), "artikel"),
        "dach_bezug": bool(story.get("ort")), "ort": story.get("ort") or "", "titel": titel, "teaser": teaser,
        "inhalt_html": html, "schlagworte": ["Tamil", kategorie.title(), story.get("ort") or "Community"][:3],
        "seo_titel": titel[:60], "meta_beschreibung": teaser[:155], "bild_suchbegriff": "tamil community",
        "bild_alt": f"Symbolbild zu: {titel}"[:120], "bild_thema": "", "bild_prompt": "",
        "event_datum": story.get("event_datum", ""), "event_ort": story.get("event_ort", ""), "ticket_url": "",
        "belege": belege,
    }


def faktencheck(user: str, system: str, req: dict) -> dict:
    entwurf = block(user, "entwurf") or {}
    claims = block(user, "claims") or []
    out = []
    for nr, satz in enumerate(_saetze(entwurf.get("inhalt_html", "")), 1):
        if satz.startswith("Quelle:"):
            out.append({"nr": nr, "satz": satz, "urteil": "kein_fakt", "claim_ids": [], "fundstelle": "", "kern": False})
            continue
        treffer = [c for c in claims if SequenceMatcher(None, satz.rstrip("."), c["aussage"].rstrip(".")).ratio() > 0.6
                   or c["aussage"].rstrip(".")[:50] in satz]
        out.append({"nr": nr, "satz": satz, "urteil": "gedeckt" if treffer else "ungedeckt",
                    "claim_ids": [c["id"] for c in treffer], "fundstelle": treffer[0]["fundstelle"] if treffer else "",
                    "kern": any(c.get("kern") for c in treffer)})
    return {"saetze": out}


def lektorat(user: str, system: str, req: dict) -> dict:
    return {"hinweise": []}


def seo(user: str, system: str, req: dict) -> dict:
    entwurf = block(user, "entwurf") or {}
    titel = entwurf.get("titel", "Tamil.de")
    teaser = entwurf.get("teaser", titel)
    meta = (teaser + " Alle Infos auf Tamil.de.")[:155]
    if len(meta) < 120:
        meta = (meta + " Termine, Hintergründe und Reaktionen aus der tamilischen Community.")[:155]
    return {"fokus_keyword": " ".join(titel.split()[:2]), "seo_titel": titel[:60], "meta_beschreibung": meta,
            "bild_alt": f"Symbolbild: {titel}"[:120]}


def eingang(user: str, system: str, req: dict) -> dict:
    """Einsendung (F1): Zusammenfassung und Entwurf nur aus den Feldern im Block <einsendung>."""
    e = block(user, "einsendung") or {}
    f = e.get("felder") or {}
    titel = f.get("titel") or f.get("thema") or ""
    text = f.get("beschreibung") or f.get("text") or f.get("anliegen") or f.get("nachricht") or ""
    erster = (_saetze(text) or [text])[0]
    ort = ", ".join(x for x in (f.get("stadt"), f.get("land")) if x)
    zusammen = f"{e.get('art', 'Einsendung').title()}: {titel or erster[:120]}" + (f" ({ort})" if ort else "")
    entwurf = e.get("art") in ("event", "beitrag")
    return {"zusammenfassung": zusammen, "titel": titel if entwurf else "", "teaser": erster[:220] if entwurf else "",
            "absaetze": [text] if entwurf and text else []}


STANDARD: dict[str, Responder] = {
    "signal": signal, "cluster": cluster, "recherche": recherche, "text": text, "dossier": text,
    "faktencheck": faktencheck, "lektorat": lektorat, "seo": seo, "eingang": eingang,
}


class FakeAnthropic:
    """Antwortet wie client.beta.messages.create; zeichnet jede Anfrage auf (self.requests)."""

    def __init__(
        self,
        antworten: dict[str, Responder | dict | list] | None = None,
        *,
        ablehnen: tuple[str, ...] = (),
        abschneiden: tuple[str, ...] = (),
        fehler: dict[str, Exception] | None = None,
        fallback_modell: dict[str, str] | None = None,
    ):
        self.antworten: dict[str, Any] = {**STANDARD, **(antworten or {})}
        self.ablehnen = set(ablehnen)
        self.abschneiden = set(abschneiden)
        self.fehler = dict(fehler or {})
        self.fallback_modell = dict(fallback_modell or {})
        self.requests: list[dict] = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self.create))
        self.messages = self.beta.messages

    def with_options(self, **_kw) -> "FakeAnthropic":
        return self

    def rollen(self) -> list[str]:
        return [r["rolle"] for r in self.requests]

    def create(self, **kw) -> SimpleNamespace:
        schema = kw.get("output_config", {}).get("format", {}).get("schema", {})
        rolle = str(schema.get("description", "")).split(" ", 1)[0].removeprefix("rolle:") or "text"
        system = kw["system"][0]["text"] if isinstance(kw.get("system"), list) else str(kw.get("system", ""))
        user = kw["messages"][0]["content"]
        self.requests.append({"rolle": rolle, "system": system, "user": user, "kwargs": kw})
        n = len(self.requests)
        if rolle in self.fehler:
            exc = self.fehler[rolle]
            raise exc() if isinstance(exc, type) else exc
        modell = kw["model"]
        prompt_tokens = (len(system) + len(user)) // 4
        cached = len(system) // 4 if n > 1 else 0  # ab dem zweiten Aufruf liegt der System-Prompt im Cache
        usage = {
            "input_tokens": max(1, prompt_tokens - cached),
            "cache_creation_input_tokens": 0 if cached else len(system) // 4,
            "cache_read_input_tokens": cached,
            "cache_creation": {"ephemeral_5m_input_tokens": 0 if cached else len(system) // 4, "ephemeral_1h_input_tokens": 0},
            "output_tokens": 0, "iterations": None,
        }
        if rolle in self.ablehnen:
            return self._antwort(modell, "", "refusal", usage, n)
        antwort = self.antworten.get(rolle) or STANDARD["text"]
        if isinstance(antwort, list):  # mehrere Antworten nacheinander (z. B. erste Fassung, Überarbeitung)
            daten = antwort.pop(0) if len(antwort) > 1 else antwort[0]
            daten = daten(user, system, kw) if callable(daten) else daten
        elif callable(antwort):
            daten = antwort(user, system, kw)
        else:
            daten = antwort
        text = json.dumps(daten, ensure_ascii=False)
        usage["output_tokens"] = len(text) // 4 + 300  # + Thinking
        if rolle in self.abschneiden:
            return self._antwort(modell, text[: len(text) // 2], "max_tokens", usage, n)
        if rolle in self.fallback_modell:  # serverseitiger Fallback: erster Versuch abgelehnt, Ersatzmodell liefert
            ersatz = self.fallback_modell[rolle]
            usage["iterations"] = [
                {"type": "message", "model": modell, "input_tokens": usage["input_tokens"], "output_tokens": 0},
                {"type": "fallback_message", "model": ersatz, "input_tokens": usage["input_tokens"],
                 "output_tokens": usage["output_tokens"]},
            ]
            modell = ersatz
        return self._antwort(modell, text, "end_turn", usage, n)

    @staticmethod
    def _antwort(modell: str, text: str, stop: str, usage: dict, n: int) -> SimpleNamespace:
        content = [SimpleNamespace(type="text", text=text)] if text else []
        return SimpleNamespace(
            id=f"msg_fake_{n}", _request_id=f"req_fake_{n}", model=modell, content=content, stop_reason=stop,
            stop_details=SimpleNamespace(category="cyber") if stop == "refusal" else None, usage=usage,
        )
