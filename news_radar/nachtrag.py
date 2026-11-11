"""Nachtrag (Rückblick): eine Story aus einem Vorschlag mit Quellen anlegen – ohne Scan, ohne Modell, ohne Kosten.

  POST /api/agent/vorschlag  (Bearer RADAR_AGENT_TOKEN)   ·   python -m news_radar agent vorschlag --datei v.json

Eingabe: {"vorschlaege": [...]} oder eine Liste. Je Vorschlag: arbeitstitel, datum (JJJJ-MM-TT, Tag des Ereignisses
oder der Meldung), rubrik, ort, bezug, heikel, quellen [{url, titel, herausgeber, datum, sprache, art}], optional
kernfakten und bild_hinweis (nur Hinweise für den Agenten, nie Belege).

Der Radar holt jede Quelle selbst (net.safe_get, Stopp-Schalter vor jedem Abruf) und legt sie als source_documents
an; Text und Titel eines Dokuments stammen nie aus dem Vorschlag, sondern aus der abgerufenen Seite (Titel aus
og:title bzw. <title>, sonst leer) – sonst würde ein erfundener „Titel“ zur Fundstelle im Gate. Danach steht die Story im Agent-Export
(Herkunft „nachtrag“, Status „neu“, kein Job) und läuft durch Import und Gate wie jede andere.
"""

from __future__ import annotations

import json
import re
from datetime import date, timedelta
from difflib import SequenceMatcher
from html import unescape
from typing import Callable

from pydantic import BaseModel, Field, ValidationError, field_validator

from . import net, schalter, sources
from .agents import Kontext
from .agents.research import VOLLTEXT_MIN
from .config import Settings
from .store import Store
from .workflow import repo

RUBRIKEN = ("news", "community", "entertainment", "kino", "events", "kueche", "sport", "kultur")
MAX_QUELLEN = 6
MAX_VORSCHLAEGE = 20  # je Aufruf: jeder Vorschlag holt bis zu 6 Seiten
FRUEHESTES = date(2020, 1, 1)
ZEITRAUM_TAGE = 14  # Titel-Dublette: ähnlicher Titel in diesem Abstand zum Ereignisdatum
AEHNLICH = 0.82
TEXT_MAX = 20000


class Quelle(BaseModel):
    url: str
    titel: str = ""
    herausgeber: str = ""
    datum: str = ""
    sprache: str = "de"
    art: str = ""


class Vorschlag(BaseModel):
    arbeitstitel: str = Field(min_length=3, max_length=300)
    datum: str
    rubrik: str
    ort: str = ""
    bezug: str = ""
    heikel: bool = False
    quellen: list[Quelle] = Field(min_length=1)
    kernfakten: list[str] = Field(default_factory=list)
    bild_hinweis: str = ""

    @field_validator("datum")
    @classmethod
    def _datum(cls, v: str) -> str:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v or ""):
            raise ValueError("datum muss JJJJ-MM-TT sein")
        date.fromisoformat(v)  # wirft bei 2026-02-30
        return v

    @field_validator("rubrik")
    @classmethod
    def _rubrik(cls, v: str) -> str:
        if v not in RUBRIKEN:
            raise ValueError(f"rubrik muss eine von {', '.join(RUBRIKEN)} sein")
        return v

    @field_validator("quellen")
    @classmethod
    def _quellen(cls, v: list[Quelle]) -> list[Quelle]:
        if len(v) > MAX_QUELLEN:
            raise ValueError(f"höchstens {MAX_QUELLEN} Quellen")
        for q in v:
            if not q.url.lower().startswith(("http://", "https://")):
                raise ValueError(f"nur http/https-Adressen ({q.url[:80]})")
        return v


class VorschlagAbgelehnt(ValueError):
    pass


_TITEL_RES = (
    re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)["\']', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', re.I),
    re.compile(r"<title[^>]*>(.*?)</title\s*>", re.I | re.S),
)


def standard_abruf(url: str, frist: float | None = None) -> net.Fetched:
    """Seite holen: SSRF-Schutz, Umleitungen geprüft, Größenlimit (net.safe_get)."""
    return net.safe_get(url, accept=net.TEXT_TYPES, timeout=8, max_bytes=3_000_000)


def seite_lesen(seite: net.Fetched) -> tuple[str, str]:
    """(Text, Titel) der abgerufenen Seite. Der Titel kommt nur aus og:title oder <title>, sonst bleibt er leer."""
    roh = seite.text
    titel = ""
    for rx in _TITEL_RES:
        m = rx.search(roh)
        if m and m.group(1).strip():
            titel = sources.clean_text(unescape(m.group(1)))[:300]
            break
    return sources.extract_paragraphs(roh, TEXT_MAX), titel


def _fehlertext(exc: ValidationError) -> str:
    err = exc.errors()[0]
    feld = ".".join(str(x) for x in err.get("loc", ()))
    return f"{feld}: {err['msg']}".replace("Value error, ", "")


def _norm(titel: str) -> str:
    return " ".join(re.findall(r"\w+", (titel or "").lower()))


def _dublette(store: Store, v: Vorschlag) -> int | None:
    """Story, die diesen Vorschlag schon abdeckt: eine der Adressen ist dort Beleg, oder ein sehr ähnlicher Titel im
    selben Zeitraum. Vom Scan verworfene Radar-Storys zählen nicht (ein Rückblick-Ereignis ist oft „vorbei“ verworfen
    worden); Nachtrag-Storys zählen in jedem Status."""
    for q in v.quellen:
        row = store.db.execute(
            "SELECT s.id FROM source_documents d JOIN stories s ON s.id = d.story_id WHERE d.url_norm = ? "
            "AND NOT (s.herkunft = 'radar' AND s.status = 'verworfen') ORDER BY s.id LIMIT 1",
            (repo.normalize_url(q.url),)).fetchone()
        if row:
            return row[0]
    tag = date.fromisoformat(v.datum)
    von, bis = (tag - timedelta(days=ZEITRAUM_TAGE)).isoformat(), (tag + timedelta(days=ZEITRAUM_TAGE)).isoformat()
    titel = _norm(v.arbeitstitel)
    for row in store.db.execute(
            "SELECT id, titel FROM stories WHERE (herkunft = 'nachtrag' AND ereignis_datum BETWEEN ? AND ?) "
            "OR (herkunft = 'radar' AND status != 'verworfen' AND substr(erstellt, 1, 10) BETWEEN ? AND ?) ORDER BY id",
            (von, bis, von, bis)):
        if SequenceMatcher(None, titel, _norm(row["titel"])).ratio() >= AEHNLICH:
            return row["id"]
    return None


def _pruefen(raw, heute: date) -> Vorschlag:
    if not isinstance(raw, dict):
        raise VorschlagAbgelehnt("Vorschlag muss ein Objekt sein")
    try:
        v = Vorschlag.model_validate(raw)
    except ValidationError as exc:
        raise VorschlagAbgelehnt(_fehlertext(exc)) from None
    tag = date.fromisoformat(v.datum)
    if tag > heute:
        raise VorschlagAbgelehnt(f"datum: {v.datum} liegt in der Zukunft")
    if tag < FRUEHESTES:
        raise VorschlagAbgelehnt(f"datum: {v.datum} liegt vor {FRUEHESTES.isoformat()}")
    for q in v.quellen:  # vor jedem Abruf: interne Adressen lehnen den ganzen Vorschlag ab
        try:
            net.check_url(q.url)
        except net.UnsafeURL as exc:
            grund = "interne Adresse" if "Interne Adresse" in str(exc) else "Adresse gesperrt"
            raise VorschlagAbgelehnt(f"{grund}: {q.url[:80]} ({exc})") from None
    return v


def _eins(ctx: Kontext, store: Store, raw, nr: int, von: str, abruf: Callable) -> dict:
    titel = raw.get("arbeitstitel", "") if isinstance(raw, dict) else ""
    out: dict = {"nr": nr, "arbeitstitel": str(titel)[:120]}
    try:
        v = _pruefen(raw, ctx.uhr().date())
    except VorschlagAbgelehnt as exc:
        return {**out, "ergebnis": "abgelehnt", "grund": str(exc)[:300]}
    vorhanden = _dublette(store, v)
    if vorhanden:
        return {**out, "ergebnis": "vorhanden", "story_id": vorhanden, "grund": f"schon vorhanden: Story {vorhanden}"}
    geholt, uebersprungen = [], []
    for q in v.quellen:
        schalter.pruefen(store, "redaktion")  # unmittelbar vor dem Abruf
        try:
            text, seitentitel = seite_lesen(abruf(q.url))
        except Exception as exc:  # noqa: BLE001 – eine kaputte Seite stoppt den Vorschlag nicht
            uebersprungen.append({"url": q.url, "grund": f"nicht abrufbar ({type(exc).__name__})"[:80]})
            continue
        if len(text or "") < VOLLTEXT_MIN:
            uebersprungen.append({"url": q.url, "grund": "ohne lesbaren Text"})
            continue
        geholt.append((q, text, seitentitel))
    if not geholt:
        return {**out, "ergebnis": "abgelehnt", "grund": "keine Quelle abrufbar", "quellen_uebersprungen": uebersprungen}
    sid = repo.story_anlegen(store, typ="news", titel=v.arbeitstitel, kategorie=v.rubrik, ort=v.ort,
                             sensibel=v.heikel, status="neu", relevanz=7, begruendung="Nachtrag für den Rückblick")
    hinweise = {"bezug": v.bezug, "kernfakten": v.kernfakten[:12], "bild_hinweis": v.bild_hinweis[:300]}
    store._write("UPDATE stories SET herkunft = 'nachtrag', ereignis_datum = ?, vorschlag = ?, notiz = ? WHERE id = ?",
                 (v.datum, json.dumps(hinweise, ensure_ascii=False), f"Nachtrag · Bezug: {v.bezug}"[:900], sid))
    for q, text, seitentitel in geholt:
        repo.dokument_hinzufuegen(store, sid, url=q.url, publisher=q.herausgeber[:120], quelle="Nachtrag",
                                  published_at=q.datum[:25], language=(q.sprache or "de")[:8], rights="zitat",
                                  primaer=True, art="volltext", titel=seitentitel, text=text[:TEXT_MAX])
    repo.aktion(store, wer=von[:60], aktion="nachtrag_angelegt", story_id=sid, kanal="redaktion", ausloeser="agent",
                notiz=f"{len(geholt)} Quellen geholt, {len(uebersprungen)} übersprungen")
    store.event("nachtrag", story=sid, quellen=len(geholt), uebersprungen=len(uebersprungen), von=von[:60])
    return {**out, "ergebnis": "angelegt", "story_id": sid, "quellen_geholt": len(geholt),
            "quellen_uebersprungen": uebersprungen}


def annehmen(store: Store, settings: Settings, raw, *, von: str = "agent", ctx: Kontext | None = None,
             abruf: Callable | None = None) -> dict:
    """Vorschläge annehmen. Hält der Schalter „redaktion“ an, wirft schalter.Gestoppt, bevor etwas abgerufen wird."""
    schalter.pruefen(store, "redaktion")
    items = raw.get("vorschlaege") if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        raise ValueError('Vorschläge: erwartet {"vorschlaege": [...]} oder eine Liste')
    if len(items) > MAX_VORSCHLAEGE:
        raise ValueError(f"höchstens {MAX_VORSCHLAEGE} Vorschläge je Aufruf")
    ctx = ctx or Kontext(settings=settings, store=store)
    abruf = abruf or (lambda url, frist=None: standard_abruf(url, frist=frist))  # zur Laufzeit (austauschbar)
    ergebnisse = [_eins(ctx, store, raw_v, nr, von, abruf) for nr, raw_v in enumerate(items, 1)]
    zaehler = {k: sum(1 for e in ergebnisse if e["ergebnis"] == k) for k in ("angelegt", "vorhanden", "abgelehnt")}
    return {"ergebnisse": ergebnisse, **zaehler}
