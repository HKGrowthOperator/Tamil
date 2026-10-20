"""Beitragsbild: lizenzfreies Stockfoto (Unsplash/Pexels) oder Tamil.de-Bildkarte.

Bilder der Nachrichtenquelle werden bewusst NICHT übernommen (Urheberrecht).
"""

from __future__ import annotations

import io
import logging
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

from .config import Settings

log = logging.getLogger(__name__)

# Farben aus DESIGN.md („modernes Community-Magazin“): Sand, Tinte, Rot aus dem Logo, Rubrikpunkte
ROT = (181, 40, 42)
SAND = (248, 239, 228)
SAND_2 = (242, 230, 217)
TINTE = (51, 41, 36)
TINTE_2 = (101, 88, 81)
RUBRIK_FARBEN = {
    "news": ROT, "kino": (138, 87, 174), "events": (218, 138, 17), "community": (61, 142, 83),
    "kueche": (201, 103, 54), "kultur": (52, 106, 172), "sport": (13, 146, 152), "entertainment": (198, 80, 133),
}

SIZE = (1200, 675)
_FONT_DIR = Path(__file__).with_name("fonts")
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


def _font(size: int, schnitt: str = "ExtraBold") -> ImageFont.ImageFont:
    for path in [str(_FONT_DIR / f"Catamaran-{schnitt}.ttf"), *_FONT_CANDIDATES]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    for width in range(40, 10, -2):
        lines = textwrap.wrap(text, width=width)
        if all(draw.textlength(line, font=font) <= max_width for line in lines):
            return lines
    return textwrap.wrap(text, width=12)


def _kolam(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float, farbe: tuple[int, int, int], breite: int) -> None:
    """Kolam wie im Theme (assets/icons.svg): vier Blätter aus einer Linie, acht Punkte."""
    def p(x: float, y: float) -> tuple[float, float]:
        return cx + (x - 50) / 50 * r, cy + (y - 50) / 50 * r

    def bezier(a, b, c, d, n=24):
        return [
            (
                (1 - t) ** 3 * a[0] + 3 * (1 - t) ** 2 * t * b[0] + 3 * (1 - t) * t * t * c[0] + t**3 * d[0],
                (1 - t) ** 3 * a[1] + 3 * (1 - t) ** 2 * t * b[1] + 3 * (1 - t) * t * t * c[1] + t**3 * d[1],
            )
            for t in (i / n for i in range(n + 1))
        ]

    kurven = [
        ((50, 50), (38, 38), (38, 20), (50, 10)), ((50, 10), (62, 20), (62, 38), (50, 50)),
        ((50, 50), (62, 38), (80, 38), (90, 50)), ((90, 50), (80, 62), (62, 62), (50, 50)),
        ((50, 50), (62, 62), (62, 80), (50, 90)), ((50, 90), (38, 80), (38, 62), (50, 50)),
        ((50, 50), (38, 62), (20, 62), (10, 50)), ((10, 50), (20, 38), (38, 38), (50, 50)),
    ]
    for k in kurven:
        draw.line(bezier(*[p(*q) for q in k]), fill=farbe, width=breite, joint="curve")
    for x, y in ((50, 30), (70, 50), (50, 70), (30, 50), (24, 24), (76, 24), (24, 76), (76, 76)):
        px, py = p(x, y)
        d = r * 0.07
        draw.ellipse([px - d, py - d, px + d, py + d], fill=farbe)


def branded_card(title: str, category_label: str, slug: str, rubrik: str = "") -> FeaturedImage:
    """Tamil.de-Bildkarte für Beiträge ohne Foto: Sand, Rubrikpunkt, Titel, Kolam in der Rubrikfarbe, Wortmarke."""
    schluessel = rubrik or {"nachrichten": "news", "küche": "kueche"}.get(category_label.lower(), category_label.lower())
    farbe = RUBRIK_FARBEN.get(schluessel, ROT)
    img = Image.new("RGB", SIZE, SAND)
    draw = ImageDraw.Draw(img)
    hell = tuple(int(c + (s - c) * 0.72) for c, s in zip(farbe, SAND))
    _kolam(draw, SIZE[0] - 120, SIZE[1] - 80, 290, hell, 14)

    draw.ellipse([72, 92, 72 + 22, 92 + 22], fill=farbe)
    draw.text((108, 80), category_label, font=_font(36, "Bold"), fill=TINTE)

    font = _font(66)
    lines = _wrap(draw, title, font, SIZE[0] - 340)[:4]
    y = 168
    for line in lines:
        draw.text((72, y), line, font=font, fill=TINTE)
        y += 76

    logo = _font(42)
    draw.text((72, SIZE[1] - 104), "tamil", font=logo, fill=TINTE)
    draw.text((72 + draw.textlength("tamil", font=logo), SIZE[1] - 104), ".de", font=logo, fill=ROT)

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


def _encode(img: Image.Image, quality: int = 86) -> bytes:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    return buf.getvalue()


def from_upload(data: bytes, slug: str, credit: str = "Foto: Tamil.de") -> FeaturedImage:
    """Eigenes Bild der Redaktion: auf 1200×675 zuschneiden, neu kodieren (EXIF weg)."""
    img = ImageOps.exif_transpose(Image.open(io.BytesIO(data)))
    fitted = ImageOps.fit(img, SIZE, Image.Resampling.LANCZOS)
    return FeaturedImage(_encode(fitted), f"{slug}.jpg", "image/jpeg", credit, "upload")


def save_pair(image: FeaturedImage, folder: Path, stem: str) -> tuple[str, str]:
    """Speichert Bild + Vorschaubild (400 px breit) unter data/bilder; gibt beide Dateinamen zurück.

    Der Name wird auf die Zeichen beschränkt, die das Cockpit unter /bild/ ausliefert
    (Kino-UIDs beginnen z. B. mit „kino:“)."""
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-.") or "bild"
    folder.mkdir(parents=True, exist_ok=True)
    name, thumb = f"{stem}.jpg", f"{stem}-thumb.jpg"
    (folder / name).write_bytes(image.data)
    img = Image.open(io.BytesIO(image.data))
    img.thumbnail((400, 400))
    (folder / thumb).write_bytes(_encode(img, quality=80))
    return name, thumb


def load_image(path: Path, credit: str = "", origin: str = "datei") -> FeaturedImage:
    return FeaturedImage(path.read_bytes(), path.name, "image/jpeg", credit, origin)
