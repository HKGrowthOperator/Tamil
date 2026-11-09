"""Text: der Beitrag aus bestätigten Claims – Länge nach Stofflage, Stilbeispiele passend zu Typ und Rubrik.

Das Modell bekommt nur Claims mit Status „bestaetigt“ und die Quellenliste. Es liefert zu jedem Absatz die Claim-IDs
(`belege`). Links im Text bleiben nur, wenn ihre URL in den Quellen der Story steht; alle anderen entfernt der Code.
"""

from __future__ import annotations

import json
import re

from .. import prompts
from ..config import Settings
from ..writer import SCHEMA_RULES, STYLE_GUIDE, STYLE_FILE
from ..workflow.models import Claim, SourceDocument, TextErgebnis
from ..workflow.providers import json_block
from . import Kontext

# Wörter im Haupttext je Längenregel (redaktion.md: Länge nach Stofflage)
LAENGEN = {"kurz": (80, 150), "normal": (180, 350), "lang": (300, 450), "event": (150, 250), "kino": (120, 200),
           "dossier": (600, 1000)}
_STIL_SIGNALE = {
    "event": ("uhr", "eintritt", "tickets", "veranstalt", "abend", "event"),
    "kino": ("kino", "film", "regie", "trailer", "kinostart"),
    "news": ("regierung", "sri lanka", "politik", "abgeordnete", "visum", "wahl"),
    "community": ("verein", "community", "debüt", "erfolg", "singles"),
}


def stilbeispiele(typ: str, kategorie: str, n: int = 3) -> list[dict]:
    """2–3 Beispiele, die zu Typ und Rubrik passen (statt immer der ersten vier)."""
    if not STYLE_FILE.exists():
        return []
    beispiele = json.loads(STYLE_FILE.read_text(encoding="utf-8"))
    signale = _STIL_SIGNALE.get(typ) or _STIL_SIGNALE.get(kategorie) or _STIL_SIGNALE["news"]
    if kategorie in _STIL_SIGNALE and kategorie != typ:
        signale = signale + _STIL_SIGNALE[kategorie]

    def punkte(ex: dict) -> int:
        text = f"{ex['title']} {ex['text'][:800]}".lower()
        return sum(text.count(s) for s in signale)

    return sorted(beispiele, key=punkte, reverse=True)[:n]


def system_prompt(settings: Settings, typ: str, kategorie: str) -> str:
    profil = prompts.redaktion(fallback=STYLE_GUIDE).strip()
    rolle = prompts.load_prompt("text").strip()
    cats = "\n".join(f"- {c.slug}: {c.label}" for c in settings.categories)
    technik = "\n".join(z for z in SCHEMA_RULES.splitlines() if not z.startswith("- Länge:")
                        and "Kinoliste wird automatisch" not in z)
    text = (f"{profil}\n\n{rolle}\n\n{technik}\n\nKategorien (Slug: Name):\n{cats}\n\n"
            f"Bildthemen (bild_thema): {', '.join(prompts.thema_slugs()) or 'diaspora-stadt'}\n")
    beispiele = stilbeispiele({"artikel": "news"}.get(typ, typ), kategorie)
    if beispiele:
        text += "\nSo klingen veröffentlichte Tamil.de-Beiträge (nur Ton, nicht Inhalt übernehmen):\n"
        for ex in beispiele:
            text += f"\n<beispiel>\n# {ex['title']}\n{ex['text']}\n</beispiel>\n"
    return text


def laenge_text(laenge: str, typ: str) -> str:
    lo, hi = LAENGEN.get(laenge, LAENGEN["normal"])
    zusatz = ""
    if typ == "kino":
        zusatz = " Die Kinoliste wird automatisch angehängt – keine Kinos im Text aufzählen."
    if laenge == "kurz":
        zusatz += " Wenig belegter Stoff: eine kurze Meldung, nichts auffüllen."
    return f"{lo}–{hi} Wörter im Haupttext.{zusatz}"


def quellen_liste(docs: list[SourceDocument]) -> list[dict]:
    seen, out = set(), []
    for d in docs:
        if d.art == "hinweis" or not d.url or d.url.endswith("#daten"):
            continue
        name = d.publisher or d.quelle
        if (name, d.url) in seen:
            continue
        seen.add((name, d.url))
        out.append({"name": name, "url": d.url})
    return out


def schreiben(ctx: Kontext, story: dict, claims: list[Claim], docs: list[SourceDocument], laenge: str,
              anmerkung: str = "", vorige: dict | None = None, job_id: int | None = None) -> TextErgebnis:
    bestaetigt = [c for c in claims if c.support == "bestaetigt"]
    rolle = "dossier" if story["typ"] == "dossier" else "text"
    typ_hint = {"event": "event", "kino": "kino_termine"}.get(story["typ"], "artikel")
    story_info = {"titel": story.get("titel"), "typ": story["typ"], "typ_im_schema": typ_hint, "ort": story.get("ort"),
                  "kategorie": story.get("kategorie"), "relevanz": story.get("relevanz"),
                  "begruendung": story.get("begruendung")}
    teile = [json_block("story", story_info), f"<laenge>{laenge_text(laenge, story['typ'])}</laenge>",
             json_block("claims", [c.model_dump(include={"id", "aussage", "art", "kern"}) for c in bestaetigt]),
             json_block("quellen", quellen_liste(docs))]
    if anmerkung and vorige:
        teile.append(json_block("vorige_fassung", {k: vorige.get(k) for k in ("titel", "teaser", "inhalt_html")}))
        teile.append(f"<anmerkung>\n{anmerkung}\n</anmerkung>")
    teile.append("Schreibe den Beitrag nur aus diesen Claims.")
    antwort = ctx.claude.call(rolle, system_prompt(ctx.settings, typ_hint, story.get("kategorie") or ""),
                              "\n\n".join(teile), TextErgebnis, story_id=story["id"], job_id=job_id)
    if not antwort.ok:
        raise RuntimeError(f"Text ohne Ergebnis: {antwort.status} {antwort.hinweis}")
    ergebnis: TextErgebnis = antwort.daten
    erlaubt = {q["url"] for q in quellen_liste(docs)} | {d.url for d in docs if d.url}
    return ergebnis.model_copy(update={"inhalt_html": links_bereinigen(ergebnis.inhalt_html, erlaubt),
                                       "typ": typ_hint if story["typ"] in ("event", "kino") else ergebnis.typ})


def links_bereinigen(html_text: str, erlaubt: set[str]) -> str:
    """Links, deren Ziel nicht in den Quellen der Story steht, werden zu reinem Text.

    Mit einem HTML-Parser statt Regex: auch <a href=x>, <a href = "x"> und nicht geschlossene <a> werden erkannt.
    Erlaubte Links behalten nur href (keine Event-Handler, kein style).
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_text or "", "html.parser")
    for a in soup.find_all("a"):
        href = (a.get("href") or "").strip()
        if href in erlaubt and href.startswith(("http://", "https://")):
            a.attrs = {"href": href, "target": "_blank", "rel": "noopener"}
        else:
            a.unwrap()
    return str(soup)


def woerter(html_text: str) -> int:
    text = re.sub(r'<p class="quelle">.*?</p>', " ", html_text or "", flags=re.S)
    return len(re.sub(r"<[^>]+>", " ", text).split())
