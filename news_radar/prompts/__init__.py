"""Prompt-Dateien der Redaktion (Markdown, von Menschen editierbar).

- redaktion.md  Stilprofil: so schreibt Tamil.de (Stimme, Haltung, Aufbau, Darstellung, Tabus)
- bild.md       Bildregeln + Prompt-Vorlage für KI-Symbolbilder ({motiv} wird eingesetzt)
- bildpool.md   Themenliste mit Motiv-Prompts für die Bildreserve

Der Writer (Claude) und der Agent-Modus lesen diese Dateien bei jedem Lauf – Änderungen wirken sofort.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent

_TABLE_ROW_RE = re.compile(r"^\|\s*([a-z0-9-]+)\s*\|\s*([a-z-]+)\s*\|\s*(.+?)\s*\|\s*$")
_CODE_BLOCK_RE = re.compile(r"```\n(.*?)```", re.S)

# Stichwort → Thema, wenn der Writer kein bild_thema liefert (Rohfassung); Reihenfolge = Priorität
_STICHWORT_THEMA: tuple[tuple[str, str], ...] = (
    ("pongal", "pongal"), ("deepavali", "tempel-innen"), ("diwali", "tempel-innen"), ("kolam", "kolam"),
    ("thaipusam", "tempelfest"), ("tempel", "tempelfest"), ("kovil", "tempelfest"), ("murugan", "tempelfest"),
    ("bharatanatyam", "bharatanatyam"), ("tanz", "bharatanatyam"), ("parai", "parai-musik"),
    ("hochzeit", "hochzeit"), ("tamilschule", "tamilschule"), ("schule", "tamilschule"), ("sprache", "tamil-sprache"),
    ("buch", "buch-literatur"), ("roman", "buch-literatur"), ("literatur", "buch-literatur"),
    ("rezept", "gericht-tisch"), ("kottu", "strassenkueche"), ("street food", "strassenkueche"),
    ("küche", "rezept-kueche"), ("restaurant", "gericht-tisch"), ("biryani", "gericht-tisch"), ("dosa", "gericht-tisch"),
    ("cricket", "cricket"), ("fußball", "fussball"), ("fussball", "fussball"),
    ("konzert", "konzert-buehne"), ("live in", "konzert-buehne"), ("tour", "konzert-buehne"), ("arena", "konzert-buehne"),
    ("album", "musik-studio"), ("song", "musik-studio"), ("single", "musik-studio"), ("sänger", "musik-studio"),
    ("kino", "kino-saal"), ("film", "kino-saal"), ("trailer", "filmplakat-wand"), ("box office", "kino-abend"),
    ("premiere", "kino-abend"), ("kollywood", "filmplakat-wand"),
    ("abschiebung", "behoerde-deutschland"), ("gericht", "behoerde-deutschland"), ("behörde", "behoerde-deutschland"),
    ("asyl", "bahnhof-ankunft"), ("flucht", "bahnhof-ankunft"),
    ("jaffna", "sri-lanka-kueste"), ("kilinochchi", "sri-lanka-kueste"), ("batticaloa", "sri-lanka-kueste"),
    ("colombo", "sri-lanka-stadt"), ("chennai", "chennai-stadt"), ("tamil nadu", "tamil-nadu-tempel"),
    ("regierung", "politik-sri-lanka"), ("parlament", "politik-sri-lanka"), ("wahl", "politik-sri-lanka"),
    ("präsident", "politik-sri-lanka"), ("sri lanka", "sri-lanka-kueste"),
    ("festival", "event-halle"), ("event", "event-halle"), ("night", "event-halle"), ("gala", "event-halle"),
    ("verein", "gemeindefest"), ("gemeinde", "gemeindefest"), ("fest", "gemeindefest"),
)

_RUBRIK_THEMA = {
    "news": "diaspora-stadt", "community": "gemeindefest", "entertainment": "konzert-buehne", "kino": "kino-saal",
    "events": "event-halle", "kueche": "gericht-tisch", "sport": "cricket", "kultur": "kolam",
}


def load_prompt(name: str, fallback: str = "") -> str:
    """Inhalt einer Prompt-Datei (ohne Erweiterung); fehlt sie, der Fallback."""
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        return fallback
    return path.read_text(encoding="utf-8")


def redaktion(fallback: str = "") -> str:
    return load_prompt("redaktion", fallback)


@lru_cache(maxsize=1)
def bildpool_themen() -> list[dict]:
    """Zeilen der Themen-Tabelle aus bildpool.md: [{thema, rubrik, motiv}, …]."""
    themen = []
    for line in load_prompt("bildpool").splitlines():
        m = _TABLE_ROW_RE.match(line)
        if m and m.group(1) != "thema" and m.group(1).strip("-"):  # Kopf- und Trennzeile überspringen
            themen.append({"thema": m.group(1), "rubrik": m.group(2), "motiv": m.group(3)})
    return themen


def thema_slugs() -> list[str]:
    return [t["thema"] for t in bildpool_themen()]


def motiv_fuer_thema(thema: str) -> str:
    for t in bildpool_themen():
        if t["thema"] == thema:
            return t["motiv"]
    return ""


def thema_fuer(kategorie: str, text: str = "") -> str:
    """Bestes Pool-Thema für einen Beitrag: Stichworte im Text, sonst Standard der Rubrik."""
    bekannt = set(thema_slugs())
    haystack = (text or "").lower()
    for wort, thema in _STICHWORT_THEMA:
        if wort in haystack and thema in bekannt:
            return thema
    standard = _RUBRIK_THEMA.get(kategorie, "diaspora-stadt")
    if standard in bekannt:
        return standard
    return thema_slugs()[0] if bekannt else ""


def bild_vorlage() -> str:
    """Die Prompt-Vorlage (Codeblock) aus bild.md; enthält den Platzhalter {motiv}."""
    m = _CODE_BLOCK_RE.search(load_prompt("bild"))
    if not m:
        return "Editorial photograph, documentary style, landscape 16:9, no text, no logos, no recognizable people.\nScene: {motiv}"
    return m.group(1).strip()


def bild_prompt_bauen(motiv: str, thema: str = "") -> str:
    """Endgültiger Prompt für die Bild-KI: Vorlage aus bild.md + Motiv (oder Motiv des Themas)."""
    motiv = (motiv or "").strip() or motiv_fuer_thema(thema)
    if not motiv:
        motiv = "A calm everyday scene of the Tamil diaspora in a German city, documentary style"
    return bild_vorlage().replace("{motiv}", motiv)
