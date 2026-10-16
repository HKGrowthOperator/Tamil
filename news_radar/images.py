"""Beitragsbild: lizenzfreies Stockfoto (Unsplash/Pexels) oder Tamil.de-Bildkarte.

Bilder der Nachrichtenquelle werden bewusst NICHT übernommen (Urheberrecht).
"""

from __future__ import annotations

import io
import logging
import textwrap
from dataclasses import dataclass
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

from .config import Settings

log = logging.getLogger(__name__)

# Farben aus dem Tamil.de-Designsystem
ROT = (176, 30, 44)
GOLD = (201, 168, 76)
ANTHRAZIT = (26, 26, 28)
WARMWEISS = (250, 247, 242)

SIZE = (1200, 675)
_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


@dataclass
class FeaturedImage:
    data: bytes
    filename: str
    mime: str
    credit: str
    origin: str  # unsplash | pexels | karte


def _font(size: int) -> ImageFont.ImageFont:
    for path in _FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    for width in range(40, 10, -2):
        lines = textwrap.wrap(text, width=width)
        if all(draw.textlength(line, font=font) <= max_width for line in lines):
            return lines
    return textwrap.wrap(text, width=12)


def branded_card(title: str, category_label: str, slug: str) -> FeaturedImage:
    img = Image.new("RGB", SIZE, ANTHRAZIT)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, SIZE[0], 14], fill=ROT)
    draw.rectangle([72, 120, 72 + 64, 126], fill=GOLD)
    draw.text((72, 142), category_label.upper(), font=_font(30), fill=GOLD)

    font = _font(58)
    lines = _wrap(draw, title, font, SIZE[0] - 144)[:5]
    y = 210
    for line in lines:
        draw.text((72, y), line, font=font, fill=WARMWEISS)
        y += 72

    logo = _font(40)
    draw.text((72, SIZE[1] - 92), "tamil", font=logo, fill=WARMWEISS)
    draw.text((72 + draw.textlength("tamil", font=logo), SIZE[1] - 92), ".de", font=logo, fill=ROT)

    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=88, optimize=True, progressive=True)
    return FeaturedImage(buf.getvalue(), f"{slug}.jpg", "image/jpeg", "Grafik: Tamil.de", "karte")


def _download(url: str) -> bytes:
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.content


def from_unsplash(query: str, key: str, slug: str) -> FeaturedImage | None:
    resp = requests.get(
        "https://api.unsplash.com/search/photos",
        params={"query": query, "orientation": "landscape", "per_page": 1, "content_filter": "high"},
        headers={"Authorization": f"Client-ID {key}", "Accept-Version": "v1"},
        timeout=10,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        return None
    photo = results[0]
    # Unsplash-Richtlinie: Download-Endpoint aufrufen
    requests.get(photo["links"]["download_location"], headers={"Authorization": f"Client-ID {key}"}, timeout=10)
    data = _download(photo["urls"]["regular"])
    credit = f"Foto: {photo['user']['name']} / Unsplash"
    return FeaturedImage(data, f"{slug}.jpg", "image/jpeg", credit, "unsplash")


def from_pexels(query: str, key: str, slug: str) -> FeaturedImage | None:
    resp = requests.get(
        "https://api.pexels.com/v1/search",
        params={"query": query, "orientation": "landscape", "per_page": 1},
        headers={"Authorization": key},
        timeout=10,
    )
    resp.raise_for_status()
    photos = resp.json().get("photos", [])
    if not photos:
        return None
    photo = photos[0]
    data = _download(photo["src"]["large2x"])
    return FeaturedImage(data, f"{slug}.jpg", "image/jpeg", f"Foto: {photo['photographer']} / Pexels", "pexels")


def featured_image(settings: Settings, query: str, title: str, category_label: str, slug: str) -> FeaturedImage:
    for provider, key in ((from_unsplash, settings.unsplash_key), (from_pexels, settings.pexels_key)):
        if not key:
            continue
        try:
            image = provider(query, key, slug)
            if image:
                return image
        except requests.RequestException as exc:
            log.warning("Bildsuche fehlgeschlagen (%s): %s", provider.__name__, exc)
    return branded_card(title, category_label, slug)
