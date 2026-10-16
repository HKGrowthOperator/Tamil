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
    anthropic_model: str = "claude-opus-5-5"
    newsapi_key: str = ""
    gnews_token: str = ""
    unsplash_key: str = ""
    pexels_key: str = ""
    wp_url: str = ""
    wp_user: str = ""
    wp_app_password: str = ""
    wp_post_status: str = "pending"
    notify_webhook: str = ""
    max_articles: int = 5
    max_age_hours: int = 36
    min_score: int = 4
    min_relevance: int = 6
    deadline_seconds: int = 270
    data_dir: Path = field(default_factory=lambda: ROOT / "data")
    out_dir: Path = field(default_factory=lambda: ROOT / "out")

    @property
    def wordpress_enabled(self) -> bool:
        return bool(self.wp_url and self.wp_user and self.wp_app_password)

    def category_slugs(self) -> list[str]:
        return [c.slug for c in self.categories]


def _int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    return int(raw) if raw else default


def load_settings(sources_file: Path = ROOT / "sources.toml") -> Settings:
    load_dotenv()
    raw = tomllib.loads(sources_file.read_text(encoding="utf-8"))
    sources = [Source(**s) for s in raw.get("source", [])]
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
        anthropic_model=env("RADAR_MODEL", "claude-opus-5-5"),
        newsapi_key=env("NEWSAPI_KEY", ""),
        gnews_token=env("GNEWS_TOKEN", ""),
        unsplash_key=env("UNSPLASH_ACCESS_KEY", ""),
        pexels_key=env("PEXELS_API_KEY", ""),
        wp_url=env("WP_URL", "").rstrip("/"),
        wp_user=env("WP_USER", ""),
        wp_app_password=env("WP_APP_PASSWORD", ""),
        wp_post_status=env("WP_POST_STATUS", "pending") or "pending",
        notify_webhook=env("NOTIFY_WEBHOOK_URL", ""),
        max_articles=_int("RADAR_MAX_ARTICLES", 5),
        max_age_hours=_int("RADAR_MAX_AGE_HOURS", 36),
        min_score=_int("RADAR_MIN_SCORE", 4),
        min_relevance=_int("RADAR_MIN_RELEVANCE", 6),
        deadline_seconds=_int("RADAR_DEADLINE_SECONDS", 270),
    )
