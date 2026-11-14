"""SEO: Regeln (Längen, Slug, Alt-Text), interne Links nur auf bestehende Beiträge, Fokus-Keyword von Haiku."""

from __future__ import annotations

import logging

import requests

from .. import net, prompts
from ..wordpress import slugify
from ..workflow.costs import BudgetErschoepft
from ..workflow.models import SeoErgebnis
from ..workflow.providers import json_block
from . import Kontext

log = logging.getLogger(__name__)

TITEL_MAX, META_MIN, META_MAX, ALT_MAX = 60, 120, 155, 125


def kuerzen(text: str, limit: int) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0].rstrip(",;:–-")
    return cut + "…"


def regeln(felder: dict) -> tuple[dict, list[str]]:
    """Erzwingt die Längen; gibt die korrigierten Felder und Hinweise zurück."""
    hinweise = []
    out = dict(felder)
    out["seo_titel"] = kuerzen(out.get("seo_titel") or out.get("titel") or "", TITEL_MAX)
    meta = " ".join((out.get("meta_beschreibung") or out.get("teaser") or "").split())
    if len(meta) > META_MAX:
        meta = kuerzen(meta, META_MAX)
    if len(meta) < META_MIN:
        hinweise.append(f"Meta-Beschreibung nur {len(meta)} Zeichen (Ziel {META_MIN}–{META_MAX})")
    out["meta_beschreibung"] = meta
    out["bild_alt"] = kuerzen(out.get("bild_alt") or out.get("titel") or "", ALT_MAX)
    out["slug"] = slugify(out.get("titel") or "", 70)
    return out, hinweise


def wp_suche_fuer(wp_url: str):
    """Interne Links: Suche über die öffentliche WordPress-REST (nur bestehende, veröffentlichte Beiträge)."""
    def suche(begriff: str) -> list[dict]:
        try:
            data = net.safe_get(f"{wp_url}/wp-json/wp/v2/search", params={"search": begriff, "per_page": 3,
                                                                           "type": "post"}, timeout=8).json()
        except (requests.RequestException, ValueError) as exc:
            log.info("Interne Links nicht gesucht: %s", exc)
            return []
        return [{"titel": d.get("title", ""), "url": d.get("url", "")} for d in data if d.get("url")]

    return suche


def optimieren(ctx: Kontext, story_id: int, felder: dict, job_id: int | None = None) -> tuple[dict, list[str]]:
    hinweise: list[str] = []
    if ctx.claude is not None:
        user = json_block("entwurf", {k: felder.get(k) for k in ("titel", "teaser", "inhalt_html", "kategorie", "ort")})
        try:
            antwort = ctx.claude.call("seo", prompts.load_prompt("seo"), user, SeoErgebnis, story_id=story_id, job_id=job_id)
            if antwort.ok:
                d: SeoErgebnis = antwort.daten
                felder = {**felder, "seo_titel": d.seo_titel, "meta_beschreibung": d.meta_beschreibung,
                          "bild_alt": d.bild_alt, "fokus_keyword": d.fokus_keyword}
        except BudgetErschoepft:
            hinweise.append("SEO-Vorschlag übersprungen: Budget erreicht (Regeln wurden trotzdem angewendet)")
    felder, regel_hinweise = regeln(felder)
    hinweise += regel_hinweise
    suche = ctx.wp_suche or (wp_suche_fuer(ctx.settings.wp_url) if ctx.settings.wp_url else None)
    if suche and felder.get("fokus_keyword"):
        for treffer in suche(felder["fokus_keyword"])[:2]:
            hinweise.append(f"Interner Link möglich: {treffer['titel']} – {treffer['url']}")
    return felder, hinweise
