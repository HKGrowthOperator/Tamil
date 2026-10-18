"""Claude schreibt aus einer Meldung einen eigenständigen Tamil.de-Beitrag (Entwurf) – und schreibt ihn auf Wunsch um."""

from __future__ import annotations

import html
import json
import logging
import re
from datetime import date
from pathlib import Path
from typing import Literal

import anthropic
from pydantic import BaseModel, Field

from .config import Settings
from .sources import NewsItem, clean_text

log = logging.getLogger(__name__)

STYLE_FILE = Path(__file__).with_name("style_examples.json")

STYLE_GUIDE = """\
Du bist Redakteur:in von Tamil.de, dem deutschsprachigen Portal für die tamilische Community \
in Deutschland, Österreich und der Schweiz (Nachrichten, Community, Entertainment, Kino, Events, \
Küche, Sport, Kultur).

Stil von Tamil.de:
- Deutsch, warm, nahbar und informativ. Leser:innen werden mit "ihr" angesprochen, nie mit "Sie".
- Immer der Blick der Diaspora: Was bedeutet die Meldung für Tamil:innen in Deutschland, Österreich \
und der Schweiz? Kinostarts, Termine, Tickets oder Orte im DACH-Raum gehören nach vorne.
- Einstieg mit dem Kern der Nachricht in 1-2 Sätzen, danach Hintergrund, am Ende ein \
praktischer Hinweis oder eine Einordnung.
- Tamilische Eigennamen, Filmtitel und Begriffe korrekt schreiben; Filmtitel in „deutschen \
Anführungszeichen“. Orte so transkribieren, wie deutsche Medien es tun (Jaffna, Kilinochchi, Chennai).
- Keine Übertreibungen, keine Clickbait-Formulierungen, keine Emojis, keine erfundenen Zitate.

Quellen können auf Deutsch, Englisch oder Tamil sein. Du schreibst IMMER auf Deutsch.

Harte Regeln:
- Schreibe einen EIGENEN Text. Übernimm keine Sätze aus der Quelle, nur Fakten.
- Verwende nur Fakten aus dem Quellmaterial. Was unklar ist, lässt du weg. Datum, Ort und \
Ticket-Link eines Events nur angeben, wenn sie in der Quelle stehen.
- Länge des Haupttextes: 250-450 Wörter, 3-6 Absätze als <p>, optional eine <h2>-Zwischenüberschrift. \
Bei typ=kino_termine nur 120-200 Wörter über den Film und den Kinostart – die Liste der Kinos und \
Termine wird automatisch unter den Text gesetzt, also KEINE Kinos im Text aufzählen.
- Der letzte Absatz nennt die Quelle: <p class="quelle">Quelle: NAME</p>.
- typ: "event" nur für eine konkrete Veranstaltung mit Datum; "kino_termine" nur, wenn das \
Quellmaterial ein Kinoprogramm ist; sonst "artikel".
- dach_bezug=true nur, wenn ein Ort, eine Organisation oder eine Person in Deutschland, Österreich \
oder der Schweiz ausdrücklich vorkommt; ort = dieser Ort (Stadt, sonst Land), sonst leer.
- Bewerte ehrlich, wie relevant die Meldung für die tamilische Community im DACH-Raum ist (1-10). \
Allgemeine Weltnachrichten ohne tamilischen Bezug bekommen höchstens 3; Relevanz ab 6 nur bei \
erkennbarem Nutzen für die Community (Termin vor Ort, Betroffenheit, Kultur, Sport, Kino, Küche).
"""

REWRITE_RULES = """\
Du bekommst einen bestehenden Entwurf und eine Anweisung der Redaktion. Schreibe den Entwurf \
entsprechend um und liefere das vollständige Ergebnis in derselben Struktur. Behalte alle Fakten, \
relevanz, begruendung, typ und kategorie bei, sofern die Anweisung nichts anderes verlangt.
"""


class Draft(BaseModel):
    relevanz: int = Field(description="1-10: Relevanz für die tamilische Community im DACH-Raum")
    begruendung: str = Field(description="Ein Satz, warum relevant oder nicht")
    kategorie: str
    typ: Literal["artikel", "event", "kino_termine"]
    dach_bezug: bool = Field(description="true nur bei ausdrücklichem Bezug zu DE/AT/CH")
    ort: str = Field(description="Stadt oder Land im DACH-Raum, sonst leer")
    titel: str = Field(description="Deutsche Überschrift, max. 90 Zeichen")
    teaser: str = Field(description="Anreißer, 1-2 Sätze, max. 220 Zeichen")
    inhalt_html: str = Field(description="Haupttext als HTML (<p>, <h2>, <strong>)")
    schlagworte: list[str] = Field(description="3-6 Schlagworte auf Deutsch")
    seo_titel: str = Field(description="max. 60 Zeichen")
    meta_beschreibung: str = Field(description="max. 155 Zeichen")
    bild_suchbegriff: str = Field(description="2-4 englische Begriffe für ein passendes Stockfoto, ohne Personennamen")
    bild_alt: str = Field(description="Deutscher Alt-Text für das Beitragsbild")
    event_datum: str = Field(description="Nur typ=event: YYYY-MM-DD, sonst leer")
    event_ort: str = Field(description="Nur typ=event: Veranstaltungsort, sonst leer")
    ticket_url: str = Field(description="Nur wenn in der Quelle genannt, sonst leer")


def _schema(categories: list[str]) -> dict:
    schema = Draft.model_json_schema()
    schema["properties"]["kategorie"] = {"type": "string", "enum": categories}
    for prop in schema["properties"].values():
        prop.pop("title", None)
    schema.pop("title", None)
    schema["additionalProperties"] = False
    schema["required"] = list(schema["properties"])
    return schema


def load_style_examples(path: Path = STYLE_FILE, limit: int = 4) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))[:limit]


def build_system(settings: Settings) -> list[dict]:
    cats = "\n".join(f"- {c.slug}: {c.label}" for c in settings.categories)
    text = f"{STYLE_GUIDE}\nKategorien (Slug: Name):\n{cats}\n"
    examples = load_style_examples()
    if examples:
        text += "\nSo klingen veröffentlichte Tamil.de-Beiträge (Stilbeispiele, nicht inhaltlich übernehmen):\n"
        for ex in examples:
            text += f"\n<beispiel>\n# {ex['title']}\n{ex['text']}\n</beispiel>\n"
    # Stabiler System-Prompt -> Prompt-Caching spart Kosten bei jedem 3-Minuten-Lauf
    return [{"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}]


LANGUAGE_NAMES = {"de": "Deutsch", "en": "Englisch", "ta": "Tamil"}


def _facts_block(item: NewsItem) -> str:
    facts = item.facts or {}
    if not facts:
        return ""
    return "\nStrukturierte Fakten aus der Quelle (JSON):\n" + json.dumps(facts, ensure_ascii=False, indent=1)


def build_user_message(item: NewsItem, article_text: str) -> str:
    lines = [
        "Schreibe aus dieser Meldung einen Tamil.de-Beitrag.",
        "",
        f"Quelle: {item.source}",
        f"URL: {item.url}",
        f"Sprache der Quelle: {LANGUAGE_NAMES.get(item.language, item.language)}",
        f"Veröffentlicht: {item.published:%d.%m.%Y %H:%M} UTC",
        f"Art der Meldung laut Vorfilter: {item.kind}",
        f"DACH-Ort laut Vorfilter: {item.ort or 'keiner erkannt'}",
        f"Vorgeschlagene Kategorie: {item.category_hint}",
        "",
        f"Titel der Quelle: {item.title}",
        f"Zusammenfassung der Quelle: {item.summary}",
    ]
    if item.related:
        lines.append("Weitere Quellen zur selben Meldung: " + "; ".join(f"{r.source} ({r.url})" for r in item.related))
    lines += ["", f"Artikeltext der Quelle (nur als Faktenbasis):\n{article_text or '(nicht verfügbar)'}"]
    return "\n".join(lines) + _facts_block(item)


def build_rewrite_message(row: dict, anweisung: str) -> str:
    current = {
        k: row.get(k)
        for k in (
            "relevanz", "begruendung", "kategorie", "typ", "dach_bezug", "ort", "titel", "teaser", "inhalt_html",
            "schlagworte", "seo_titel", "meta_beschreibung", "bild_suchbegriff", "bild_alt", "event_datum",
            "event_ort", "ticket_url",
        )
    }
    facts = row.get("fakten") or {}
    text = (
        f"{REWRITE_RULES}\nAnweisung der Redaktion: {anweisung.strip()}\n\n"
        f"Quelle: {row.get('quelle_name', '')} – {row.get('quelle_url', '')}\n\n"
        f"Bestehender Entwurf (JSON):\n{json.dumps(current, ensure_ascii=False, indent=1)}"
    )
    if facts:
        text += "\n\nStrukturierte Fakten (JSON):\n" + json.dumps(facts, ensure_ascii=False, indent=1)
    return text


class Writer:
    def __init__(self, settings: Settings, client: anthropic.Anthropic | None = None):
        self.settings = settings
        self.client = client or anthropic.Anthropic(max_retries=2, timeout=120)
        self.system = build_system(settings)
        self.schema = _schema(settings.category_slugs())

    def _create(self, client: anthropic.Anthropic, user_message: str) -> Draft | None:
        response = client.beta.messages.create(
            model=self.settings.anthropic_model,
            max_tokens=16000,
            system=self.system,
            messages=[{"role": "user", "content": user_message}],
            output_config={"effort": "medium", "format": {"type": "json_schema", "schema": self.schema}},
            # Bei einer Ablehnung übernimmt serverseitig ein Ersatzmodell
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        if response.stop_reason == "refusal":
            log.warning("Abgelehnt (%s)", getattr(response.stop_details, "category", None))
            return None
        if response.stop_reason == "max_tokens":
            log.warning("Antwort abgeschnitten")
            return None
        text = "".join(b.text for b in response.content if b.type == "text")
        return Draft.model_validate_json(text)

    def write(self, item: NewsItem, article_text: str) -> Draft | None:
        return self._create(self.client, build_user_message(item, article_text))

    def rewrite(self, row: dict, anweisung: str, timeout: float = 80.0) -> Draft | None:
        """Umschreiben nach Anweisung – ohne Retries, damit ein Web-Request nie minutenlang hängt."""
        client = self.client.with_options(timeout=timeout, max_retries=0)
        return self._create(client, build_rewrite_message(row, anweisung))


# ---- Rohfassung ohne Sprachmodell ----------------------------------------------------------------

ROH_HINWEIS = (
    "Rohfassung ohne KI: Titel und Zusammenfassung stammen aus der Quelle, der Auszug ist ein Zitat – "
    "vor der Freigabe neu schreiben."
)
# „ - Verlag“ am Ende; der Verlagsname darf Bindestriche enthalten (Weser-Kurier), aber keinen weiteren Trenner
_SUFFIX_RE = re.compile(r"\s+[-–—|]\s+((?:(?!\s[-–—|]\s).){2,60})$")


def split_source_suffix(title: str) -> tuple[str, str]:
    """„Überschrift - Verlag“ (so liefert Google News die Titel) → (Überschrift, Verlag)."""
    m = _SUFFIX_RE.search(title)
    if not m or len(title[: m.start()].strip()) < 20:
        return title.strip(), ""
    return title[: m.start()].strip(), m.group(1).strip()


def _first_sentence(text: str, limit: int = 220) -> str:
    text = clean_text(text)
    m = re.match(r"(.{40,}?[.!?])(\s|$)", text)
    return (m.group(1) if m else text)[:limit].strip()


_WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
_MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
_KALENDER_FLOSKEL_RE = re.compile(r"[\U0001F000-\U0001FAFF\u2600-\u27BF]|\b(Not specified|All Day)\b", re.I)


def event_teaser(summary: str, facts: dict | None) -> str:
    """Veranstaltungskalender liefern oft nur Floskeln („Not specified, All Day“) – Datum und Ort sind der bessere Anreißer."""
    facts = facts or {}
    parts = []
    datum = str(facts.get("event_datum") or "")[:10]
    if datum:
        try:
            d = date.fromisoformat(datum)
            parts.append(f"{_WOCHENTAGE[d.weekday()]}, {d.day}. {_MONATE[d.month - 1]} {d.year}")
        except ValueError:
            pass
    if facts.get("event_ort"):
        parts.append(str(facts["event_ort"]))
    rest = re.sub(r"\s*,\s*(,\s*)+", ", ", _KALENDER_FLOSKEL_RE.sub("", clean_text(summary))).strip(" ,·")
    if parts:
        return " · ".join(parts)
    return rest


def _cut(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + " …"


class RawWriter:
    """Entwürfe ohne Sprachmodell: Titel und Zusammenfassung der Quelle plus ein markiertes Zitat.

    Nur für `run --ohne-ki` (Erstbefüllung, Quellentest, Ausfall des Modells). Jeder Entwurf trägt
    ROH_HINWEIS, die Freigabe-App zeigt ihn als „Rohfassung“; vor der Freigabe wird er neu geschrieben.
    """

    hinweis = ROH_HINWEIS

    def __init__(self, settings: Settings):
        self.settings = settings
        self.slugs = settings.category_slugs()
        self.keywords = sorted(settings.keywords, key=len, reverse=True)

    def write(self, item: NewsItem, article_text: str) -> Draft:
        titel = clean_text(item.title)
        if item.source.lower().startswith("google news"):  # nur dort hängt der Verlag am Titel
            titel, _verlag = split_source_suffix(titel)
        voll = titel
        titel = _cut(titel, 90)
        summary = clean_text(item.summary)
        if item.kind == "event":
            summary = event_teaser(summary, item.facts)
        if summary.lower() == voll.lower() or (summary.lower().startswith(voll.lower()) and len(summary) - len(voll) < 40):
            summary = ""  # viele Feeds wiederholen nur die Überschrift (Google News: Überschrift + Verlag)
        if not summary and article_text:
            summary = _first_sentence(article_text)
        teaser = _cut(summary or titel, 220)

        parts = [f"<p>{html.escape(summary)}</p>"] if summary else []
        excerpt = clean_text(article_text)
        if excerpt:
            parts.append(f"<h2>Auszug aus der Quelle</h2>\n<blockquote>{html.escape(_cut(excerpt, 600))}</blockquote>")
        parts.append(f'<p class="quelle">Quelle: {html.escape(item.source)}</p>')

        if item.dach_score >= 2:
            relevanz = 8
        elif item.dach_score > 0:
            relevanz = 7
        elif item.score >= self.settings.min_score + 2:
            relevanz = 6
        else:
            relevanz = 4
        kategorie = item.category_hint if item.category_hint in self.slugs else ("news" if "news" in self.slugs else self.slugs[0])
        typ = {"kino": "kino_termine", "event": "event"}.get(item.kind, "artikel")

        haystack = f"{titel} {summary}".lower()
        worte: list[str] = []
        for term in self.keywords:
            if term in haystack and term.title() not in worte:
                worte.append(term.title())
            if len(worte) >= 5:
                break
        if item.ort and item.ort not in worte:
            worte.append(item.ort)
        facts = item.facts or {}
        return Draft(
            relevanz=relevanz,
            begruendung=f"Vorfilter: {item.score} Punkte, DACH {item.dach_score}, Ort {item.ort or '–'} (ohne KI bewertet)",
            kategorie=kategorie,
            typ=typ,
            dach_bezug=item.dach_score > 0,
            ort=item.ort,
            titel=titel,
            teaser=teaser,
            inhalt_html="\n".join(parts),
            schlagworte=worte[:6],
            seo_titel=_cut(titel, 60),
            meta_beschreibung=_cut(teaser, 155),
            bild_suchbegriff=f"{kategorie} tamil community",
            bild_alt=titel,
            event_datum=str(facts.get("event_datum", "") or "")[:10],
            event_ort=str(facts.get("event_ort", "") or ""),
            ticket_url=str(facts.get("ticket_url", "") or ""),
        )
