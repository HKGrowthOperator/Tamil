"""Lektorat: deterministische Prüfungen (immer) plus Hinweise von Haiku (wenn Budget da ist).

Deterministisch: Wortzahl gegen die Längenregel, Zahlen im Text ohne Beleg, Nähe zum Quelltext (8-Wort-Folgen),
Tabu-Wendungen aus dem Redaktionsprofil, Rubrik, Quellenzeile. Das Modell schreibt nichts um, es gibt nur Hinweise.
"""

from __future__ import annotations

import re

from .. import prompts
from ..workflow.costs import BudgetErschoepft
from ..workflow.models import Claim, LektoratErgebnis, SourceDocument
from ..workflow.providers import json_block
from . import Kontext
from .schreiben import LAENGEN, woerter

NAEHE_MAX = 0.12  # Anteil der 8-Wort-Folgen, die wörtlich in einem Quelltext stehen dürfen
TABUS = (
    ("share on", "Social-Hinweise gehören nicht in den Text"),
    ("klicken sie", "Tamil.de spricht Leser:innen mit „ihr“ an"),
    ("kein veranstalter hat je", "Superlativ des Veranstalters"),
    ("der beste", "Superlativ – als Zitat kennzeichnen oder weglassen"),
    ("sensationell", "Boulevard-Wort"),
    ("unglaublich", "Boulevard-Wort"),
    ("skandal", "Boulevard-Wort, nur mit Beleg"),
    ("gerüchten zufolge", "keine Gerüchte"),
    ("angeblich", "nur mit Quelle und Einordnung"),
    ("#", "keine Hashtags"),
)
_ZAHL_RE = re.compile(r"\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?\b")


def _text(html_text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html_text or "")).strip()


def _ngramme(text: str, n: int = 8) -> set[tuple[str, ...]]:
    w = re.findall(r"[\wäöüß]+", text.lower())
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def naehe(entwurf_text: str, quelle: str) -> float:
    a = _ngramme(entwurf_text)
    if not a:
        return 0.0
    return len(a & _ngramme(quelle)) / len(a)


def pruefen(entwurf: dict, claims: list[Claim], docs: list[SourceDocument], laenge: str,
            kategorien: list[str]) -> list[str]:
    hinweise: list[str] = []
    html_text = entwurf.get("inhalt_html") or ""
    n = woerter(html_text)
    lo, hi = LAENGEN.get(laenge, LAENGEN["normal"])
    if n < lo * 0.85:
        hinweise.append(f"Länge: {n} Wörter, Regel „{laenge}“ sieht {lo}–{hi} vor – nur mit weiteren belegten "
                        "Einzelheiten verlängern, nicht strecken")
    elif n > hi * 1.15:
        hinweise.append(f"Länge: {n} Wörter, Regel „{laenge}“ erlaubt höchstens {hi}")
    if n >= 400 and "<h2" not in html_text:
        hinweise.append(f"Langer Text ({n} Wörter) ohne Zwischenüberschrift – Abschnitte mit <h2> gliedern")
    belegt = " ".join(c.aussage for c in claims) + " " + " ".join(d.text + " " + d.titel for d in docs)
    belegt_zahlen = set(_ZAHL_RE.findall(belegt))
    fliesstext = _text(re.sub(r'<p class="quelle">.*?</p>', " ", html_text, flags=re.S))
    for zahl in sorted(set(_ZAHL_RE.findall(fliesstext + " " + (entwurf.get("titel") or "")))):
        if zahl not in belegt_zahlen and not (len(zahl) == 4 and zahl.startswith("20")):
            hinweise.append(f"Zahl „{zahl}“ steht in keinem Beleg")
    for d in docs:
        if d.art in ("volltext", "zusammenfassung") and d.text:
            anteil = naehe(fliesstext, d.text)
            if anteil > NAEHE_MAX:
                hinweise.append(f"Text zu nah am Quelltext {d.doc_key} ({anteil:.0%} gleiche 8-Wort-Folgen) – umformulieren")
    klein = f"{entwurf.get('titel', '')} {fliesstext}".lower()
    for wort, grund in TABUS:
        if wort in klein:
            hinweise.append(f"„{wort}“: {grund}")
    if entwurf.get("kategorie") not in kategorien:
        hinweise.append(f"Unbekannte Rubrik „{entwurf.get('kategorie')}“")
    if 'class="quelle"' not in html_text:
        hinweise.append("Quellenzeile fehlt")
    return hinweise


def lektorat(ctx: Kontext, story_id: int, entwurf: dict, job_id: int | None = None) -> list[str]:
    if ctx.claude is None:
        return []
    user = json_block("entwurf", {k: entwurf.get(k) for k in ("titel", "teaser", "inhalt_html")})
    try:
        antwort = ctx.claude.call("lektorat", prompts.redaktion() + "\n\n" + prompts.load_prompt("lektorat"), user,
                                  LektoratErgebnis, story_id=story_id, job_id=job_id)
    except BudgetErschoepft:
        return ["Lektorat übersprungen: Budget erreicht"]
    if not antwort.ok:
        return []
    return [f"Lektorat ({h.art}): „{h.stelle[:80]}“ → {h.vorschlag[:160]}" for h in antwort.daten.hinweise[:12]]
