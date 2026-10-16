"""Claude schreibt aus einer Meldung einen eigenständigen Tamil.de-Beitrag (Entwurf)."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import anthropic
from pydantic import BaseModel, Field

from .config import Settings
from .sources import NewsItem

log = logging.getLogger(__name__)

STYLE_FILE = Path(__file__).with_name("style_examples.json")

STYLE_GUIDE = """\
Du bist Redakteur:in von Tamil.de, dem deutschsprachigen Portal für die tamilische Community \
in Deutschland, Österreich und der Schweiz (Nachrichten, Community, Entertainment, Kino, Events, \
Küche, Sport, Kultur).

Stil von Tamil.de:
- Deutsch, warm, nahbar und informativ. Leser:innen werden mit "ihr" angesprochen, nie mit "Sie".
- Immer der Blick der Diaspora: Was bedeutet die Meldung für Tamil:innen in Deutschland/DACH? \
Gibt es Kinostarts, Termine, Tickets oder Bezüge nach Deutschland, gehören sie nach vorne.
- Einstieg mit dem Kern der Nachricht in 1-2 Sätzen, danach Hintergrund, am Ende ein \
praktischer Hinweis oder eine Einordnung.
- Tamilische Eigennamen, Filmtitel und Begriffe korrekt schreiben; Filmtitel in „deutschen \
Anführungszeichen“.
- Keine Übertreibungen, keine Clickbait-Formulierungen, keine Emojis, keine erfundenen Zitate.

Harte Regeln:
- Schreibe einen EIGENEN Text. Übernimm keine Sätze aus der Quelle, nur Fakten.
- Verwende nur Fakten aus dem Quellmaterial. Was unklar ist, lässt du weg.
- Länge des Haupttextes: 250-450 Wörter, 3-6 Absätze als <p>, optional eine <h2>-Zwischenüberschrift.
- Der letzte Absatz nennt die Quelle: <p class="quelle">Quelle: NAME</p>.
- Bewerte ehrlich, wie relevant die Meldung für die tamilische Community im DACH-Raum ist (1-10). \
Allgemeine Weltnachrichten ohne tamilischen Bezug bekommen höchstens 3.
"""


class Draft(BaseModel):
    relevanz: int = Field(description="1-10: Relevanz für die tamilische Community im DACH-Raum")
    begruendung: str = Field(description="Ein Satz, warum relevant oder nicht")
    kategorie: str
    titel: str = Field(description="Deutsche Überschrift, max. 90 Zeichen")
    teaser: str = Field(description="Anreißer, 1-2 Sätze, max. 220 Zeichen")
    inhalt_html: str = Field(description="Haupttext als HTML (<p>, <h2>, <strong>)")
    schlagworte: list[str] = Field(description="3-6 Schlagworte auf Deutsch")
    seo_titel: str = Field(description="max. 60 Zeichen")
    meta_beschreibung: str = Field(description="max. 155 Zeichen")
    bild_suchbegriff: str = Field(description="2-4 englische Begriffe für ein passendes Stockfoto, ohne Personennamen")
    bild_alt: str = Field(description="Deutscher Alt-Text für das Beitragsbild")


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
    # Stabiler System-Prompt -> Prompt-Caching spart Kosten bei jedem 5-Minuten-Lauf
    return [{"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}]


def build_user_message(item: NewsItem, article_text: str) -> str:
    return (
        "Schreibe aus dieser Meldung einen Tamil.de-Beitrag.\n\n"
        f"Quelle: {item.source}\nURL: {item.url}\nVeröffentlicht: {item.published:%d.%m.%Y %H:%M} UTC\n"
        f"Vorgeschlagene Kategorie: {item.category_hint}\n\n"
        f"Titel der Quelle: {item.title}\n"
        f"Zusammenfassung der Quelle: {item.summary}\n\n"
        f"Artikeltext der Quelle (nur als Faktenbasis):\n{article_text or '(nicht verfügbar)'}"
    )


class Writer:
    def __init__(self, settings: Settings, client: anthropic.Anthropic | None = None):
        self.settings = settings
        self.client = client or anthropic.Anthropic(max_retries=2, timeout=120)
        self.system = build_system(settings)
        self.schema = _schema(settings.category_slugs())

    def write(self, item: NewsItem, article_text: str) -> Draft | None:
        response = self.client.beta.messages.create(
            model=self.settings.anthropic_model,
            max_tokens=16000,
            system=self.system,
            messages=[{"role": "user", "content": build_user_message(item, article_text)}],
            output_config={"effort": "medium", "format": {"type": "json_schema", "schema": self.schema}},
            # Bei einer Ablehnung übernimmt serverseitig ein Ersatzmodell
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        if response.stop_reason == "refusal":
            log.warning("Abgelehnt: %s (%s)", item.title, getattr(response.stop_details, "category", None))
            return None
        if response.stop_reason == "max_tokens":
            log.warning("Abgeschnitten: %s", item.title)
            return None
        text = "".join(b.text for b in response.content if b.type == "text")
        return Draft.model_validate_json(text)
