"""Die Rollen der Redaktion v2. Jede Rolle ist eine kleine Funktion; Sprachmodelle nur, wo sie Mehrwert bringen.

relevance  Signal: Heuristik wie bisher, nur die Grauzone geht gebündelt an Haiku
cluster    Story-Clustering: URL/UID → Kino-/Event-Schlüssel → Titelähnlichkeit, Grenzfälle an Haiku
research   Belege: Volltext der Primärquelle, Cluster-Quellen, Suche nach zweiter Quelle; Claims mit Sonnet
factcheck  Gate (Regeln, kein Modell) vor dem Schreiben; Satz-für-Satz-Prüfung des Entwurfs mit Sonnet
schreiben  Text aus bestätigten Claims, Länge nach Stofflage, Stilbeispiele passend zu Typ und Rubrik
copydesk   Lektorat: deterministische Prüfungen (Länge, Zahlen, Nähe zum Quelltext, Tabus) + Hinweise von Haiku
seo        Regeln (Längen, Slug, Alt-Text), interne Links nur auf bestehende Beiträge, Fokus-Keyword von Haiku
media      Bild mit Lizenz: Archiv → Quelle (nur mit Erlaubnis) → Stock → Pool → KI → Bildkarte
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from ..config import Settings


@dataclass
class Kontext:
    """Alles, was eine Rolle braucht – austauschbar für Tests (FakeClaude, Fake-Netz, Fake-Bild-KI)."""

    settings: Settings
    store: Any
    claude: Any = None  # workflow.providers.Claude
    budget: Any = None  # workflow.costs.Budget
    fetch_text: Callable[[str], str] | None = None  # Artikeltext einer URL (Standard: sources.fetch_article_text)
    suche: Callable[[str], list[dict]] | None = None  # zweite Quelle: [{"titel", "url", "publisher"}]
    bild_transport: Any = None  # bilder.Transport für die Bild-KI
    wp_suche: Callable[[str], list[dict]] | None = None  # interne Links: [{"titel", "url"}]
    uhr: Callable[[], datetime] = field(default=lambda: datetime.now(timezone.utc))

    def text_von(self, url: str) -> str:
        if self.fetch_text is not None:
            return self.fetch_text(url)
        from ..sources import fetch_article_text

        return fetch_article_text(url)
