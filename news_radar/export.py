"""Entwürfe der Warteschlange für den HTML-Prototyp exportieren: JSON plus Beitragsbilder.

Nur für den Prototyp gedacht. `--quellbilder` lädt das Vorschaubild der Quelle (RSS-Bild oder og:image) –
im Betrieb bleibt der Radar bei Bildkarten und Stockfotos, weil die Rechte an Quellbildern nicht geklärt sind.
"""

from __future__ import annotations

import io
import json
import logging
import shutil
from pathlib import Path
from typing import Callable

import requests
from PIL import Image, ImageOps

from . import sources
from .store import Store

log = logging.getLogger(__name__)

MAX_WIDTH = 1200
MIN_WIDTH = 480  # kleiner sind meist Logos oder Icons
Downloader = Callable[[str], bytes | None]


def download(url: str, timeout: int = 12) -> bytes | None:
    try:
        resp = requests.get(url, headers={"User-Agent": sources.USER_AGENT}, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.info("Bild nicht geladen (%s): %s", url[:80], exc)
        return None
    return resp.content if resp.content else None


def quellbild(url: str, dest: Path, fetch: Downloader = download) -> dict | None:
    """Lädt ein Quellbild, dreht es nach EXIF, verkleinert auf MAX_WIDTH und speichert JPEG q76."""
    data = fetch(url)
    if not data:
        return None
    try:
        with Image.open(io.BytesIO(data)) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            if im.width < MIN_WIDTH:
                return None
            if im.width > MAX_WIDTH:
                im = im.resize((MAX_WIDTH, round(im.height * MAX_WIDTH / im.width)), Image.LANCZOS)
            im.save(dest, "JPEG", quality=76, optimize=True, progressive=True)
            return {"w": im.width, "h": im.height, "balken": has_black_bars(im)}
    except (OSError, ValueError) as exc:
        log.info("Bild unbrauchbar (%s): %s", url[:80], exc)
        return None


def has_black_bars(im: Image.Image, anteil: float = 0.12, schwelle: int = 24) -> bool:
    """Hochkant-Plakate und Logos kommen oft mit schwarzen oder weißen Rändern auf Querformat – als Aufmacher ungeeignet."""
    g = im.convert("L")
    w = max(1, int(im.width * anteil))
    links = g.crop((0, 0, w, im.height)).resize((1, 1)).getpixel((0, 0))
    rechts = g.crop((im.width - w, 0, im.width, im.height)).resize((1, 1)).getpixel((0, 0))
    dunkel = links < schwelle and rechts < schwelle
    hell = links > 255 - schwelle and rechts > 255 - schwelle
    return dunkel or hell


def _credit_name(quelle_name: str) -> str:
    return (quelle_name or "Quelle").split(" (via ")[0]


def export_drafts(
    store: Store,
    file: Path,
    bilder: Path | None,
    *,
    quellbilder: bool = False,
    limit: int = 60,
    bilder_quelle: Path | None = None,
    fetch_og: Callable[[str], str] = sources.fetch_og_image,
    fetch: Downloader = download,
) -> dict:
    data = store.export_drafts(limit=limit)
    stats = {"entwuerfe": len(data["entwuerfe"]), "quellbilder": 0, "bildkarten": 0, "ohne_bild": 0}
    if bilder:
        bilder.mkdir(parents=True, exist_ok=True)
    for d in data["entwuerfe"]:
        bild = {"datei": "", "origin": d.get("bild_origin") or "karte", "credit": d.get("bild_credit") or "Grafik: Tamil.de",
                "alt": d.get("bild_alt") or d["titel"], "w": 0, "h": 0}
        if bilder and quellbilder:
            url = d.get("quelle_bild") or fetch_og(d.get("quelle_url") or "")
            if url:
                dest = bilder / f"r{d['id']}.jpg"
                info = quellbild(url, dest, fetch)
                if info:
                    bild.update(datei=dest.name, origin="quelle", credit=f"Foto: {_credit_name(d.get('quelle_name'))}", **info)
                    stats["quellbilder"] += 1
        if not bild["datei"] and bilder and bilder_quelle and d.get("bild_datei"):
            src = bilder_quelle / d["bild_datei"]
            if src.exists():
                dest = bilder / f"r{d['id']}.jpg"
                shutil.copyfile(src, dest)
                with Image.open(dest) as im:
                    bild.update(datei=dest.name, w=im.width, h=im.height)
                stats["bildkarten"] += 1
        if not bild["datei"]:
            stats["ohne_bild"] += 1
        d["bild"] = bild
    if bilder:  # Bilder abgelehnter oder nicht mehr exportierter Entwürfe aufräumen
        keep = {d["bild"]["datei"] for d in data["entwuerfe"] if d["bild"]["datei"]}
        for alt in bilder.glob("r*.jpg"):
            if alt.name not in keep:
                alt.unlink()
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return stats
