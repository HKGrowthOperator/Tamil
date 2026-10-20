"""Konfiguration aus Umgebungsvariablen (.env) und sources.toml."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_dotenv(path: Path = ROOT / ".env") -> None:
    """Minimaler .env-Loader; bereits gesetzte Variablen haben Vorrang."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.split(" #", 1)[0].strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


@dataclass
class Source:
    name: str
    type: str
    url: str = ""
    query: str = ""
    language: str = "de"
    provider: str = ""  # kino: cinestar | kinoheld | cineplexx
    endpoint: str = "posts"  # wp_json: posts | mec-events | …
    params: dict = field(default_factory=dict)
    selectors: dict = field(default_factory=dict)  # html: item, title, link, date, summary
    kind: str = "news"  # news | event | kino – Vorgabe für alle Treffer der Quelle
    country: str = ""  # DE | CH | AT, wenn die Quelle eindeutig ein Land abdeckt
    min_score: int | None = None  # Überschreibt die Stichwort-Schwelle (0 = vertrauenswürdige Quelle)
    max_items: int = 3  # höchstens so viele Treffer je Lauf
    interval_minutes: int = 0  # 0 = bei jedem Lauf abfragen


@dataclass
class Regions:
    staedte: dict[str, str] = field(default_factory=dict)  # Stadt -> Land (DE/CH/AT)
    laender: dict[str, str] = field(default_factory=dict)  # Begriff -> Land
    aliases: dict[str, list[str]] = field(default_factory=dict)  # Stadt -> andere Schreibweisen
    exakt: set[str] = field(default_factory=set)  # nur mit Großbuchstabe matchen (Essen, Hamm, Bern)


@dataclass
class Category:
    slug: str
    label: str
    hints: list[str]


@dataclass
class Settings:
    sources: list[Source]
    keywords: dict[str, int]
    blocklist: list[str]
    categories: list[Category]
    regions: Regions = field(default_factory=Regions)
    anthropic_model: str = "claude-opus-5-5"
    newsapi_key: str = ""
    gnews_token: str = ""
    unsplash_key: str = ""
    pexels_key: str = ""
    gemini_key: str = ""  # Bild-KI (Gemini Nano Banana); leer = Pool/Stock/Karte
    bild_modell: str = "gemini-nano-banana-2.1"
    bild_groesse: str = "1K"  # 1K | 2K | 4K (Großschreibung Pflicht)
    bild_modus: str = "ki"  # ki | pool | stock | karte – wo die Bildkette beginnt
    bild_retry_pause: float = 2.0
    wp_url: str = ""
    wp_user: str = ""
    wp_app_password: str = ""
    wp_post_status: str = "pending"
    wp_seo_meta: str = "none"  # rankmath | yoast | none
    notify_webhook: str = ""
    web_url: str = "http://127.0.0.1:8787"
    web_user: str = ""
    web_password: str = ""
    web_secret: str = ""
    max_articles: int = 5
    max_drafts_per_day: int = 40
    max_age_hours: int = 36
    min_score: int = 4
    min_score_dach: int = 2
    min_relevance: int = 6
    deadline_seconds: int = 270
    fetch_seconds: int = 60
    data_dir: Path = field(default_factory=lambda: ROOT / "data")

    @property
    def wordpress_enabled(self) -> bool:
        return bool(self.wp_url and self.wp_user and self.wp_app_password)

    @property
    def db_path(self) -> Path:
        return self.data_dir / "radar.sqlite"

    @property
    def bilder_dir(self) -> Path:
        return self.data_dir / "bilder"

    @property
    def bildpool_dir(self) -> Path:
        raw = os.environ.get("BILD_POOL_DIR", "").strip()
        return Path(raw) if raw else self.data_dir / "bildpool"

    def category_slugs(self) -> list[str]:
        return [c.slug for c in self.categories]


def _int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    return int(raw) if raw else default


def load_settings(sources_file: Path = ROOT / "sources.toml") -> Settings:
    load_dotenv()
    raw = tomllib.loads(sources_file.read_text(encoding="utf-8"))
    sources = [Source(**s) for s in raw.get("source", [])]
    reg = raw.get("regions", {})
    regions = Regions(
        staedte={stadt: land.upper() for land, cities in reg.get("staedte", {}).items() for stadt in cities},
        laender={term: land.upper() for land, terms in reg.get("laender", {}).items() for term in terms},
        aliases={k: list(v) for k, v in reg.get("aliases", {}).items()},
        exakt=set(reg.get("exakt", [])),
    )
    categories = [
        Category(slug=slug, label=c["label"], hints=[h.lower() for h in c.get("hints", [])])
        for slug, c in raw.get("categories", {}).items()
    ]
    env = os.environ.get
    return Settings(
        sources=sources,
        keywords={k.lower(): int(v) for k, v in raw.get("keywords", {}).items()},
        blocklist=[t.lower() for t in raw.get("blocklist", {}).get("terms", [])],
        categories=categories,
        regions=regions,
        anthropic_model=env("RADAR_MODEL", "claude-opus-5-5"),
        newsapi_key=env("NEWSAPI_KEY", ""),
        gnews_token=env("GNEWS_TOKEN", ""),
        unsplash_key=env("UNSPLASH_ACCESS_KEY", ""),
        pexels_key=env("PEXELS_API_KEY", ""),
        gemini_key=env("GEMINI_API_KEY", ""),
        bild_modell=env("BILD_MODELL", "") or "gemini-nano-banana-2.1",
        bild_groesse=(env("BILD_GROESSE", "") or "1K").upper(),
        bild_modus=(env("BILD_MODUS", "") or "ki").lower(),
        wp_url=env("WP_URL", "").rstrip("/"),
        wp_user=env("WP_USER", ""),
        wp_app_password=env("WP_APP_PASSWORD", ""),
        wp_post_status=env("WP_POST_STATUS", "publish") or "publish",
        wp_seo_meta=(env("WP_SEO_META", "none") or "none").lower(),
        notify_webhook=env("NOTIFY_WEBHOOK_URL", ""),
        web_url=(env("RADAR_WEB_URL", "") or "http://127.0.0.1:8787").rstrip("/"),
        web_user=env("WEB_USER", ""),
        web_password=env("WEB_PASSWORD", ""),
        web_secret=env("WEB_SECRET", ""),
        max_articles=_int("RADAR_MAX_ARTICLES", 5),
        max_drafts_per_day=_int("RADAR_MAX_DRAFTS_PER_DAY", 40),
        max_age_hours=_int("RADAR_MAX_AGE_HOURS", 36),
        min_score=_int("RADAR_MIN_SCORE", 4),
        min_score_dach=_int("RADAR_MIN_SCORE_DACH", 2),
        min_relevance=_int("RADAR_MIN_RELEVANCE", 6),
        deadline_seconds=_int("RADAR_DEADLINE_SECONDS", 270),
        fetch_seconds=_int("RADAR_FETCH_SECONDS", 60),
    )
